#!/usr/bin/env python3
"""One-time lossless DH cache enrichment. The dedicated server database is read-only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import os, sqlite3, shutil, json

stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def say(*parts):
    print(datetime.now(timezone.utc).strftime("%H:%M:%S"), *parts,flush=True)

def ensure_game_closed(client_root: Path):
    needle = str(client_root / "natives")
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal(): continue
        try:
            cmd = (proc/"cmdline").read_bytes().replace(b"\x00",b" ").decode("utf-8","ignore")
        except (OSError, PermissionError): continue
        if needle in cmd and "java" in cmd:
            raise RuntimeError("The selected Minecraft client is running; cache left untouched. PID "+proc.name)

def counts(path):
    db=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
    ans={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in ('FullData','ChunkHash')}
    db.close()
    return ans

def snapshot(source, dest):
    src=sqlite3.connect(f"file:{source}?mode=ro",uri=True,timeout=30)
    dst=sqlite3.connect(str(dest),timeout=30)
    src.backup(dst,pages=10000,sleep=0.1)
    dst.close()
    src.close()
    say("Snapshot done:",dest.name, f"{dest.stat().st_size/1024**3:.2f} GiB")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-db", type=Path, required=True)
    parser.add_argument("--client-db", type=Path, required=True)
    parser.add_argument("--client-config", type=Path, required=True)
    parser.add_argument("--client-root", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    server_db = args.server_db.expanduser().resolve()
    client_db = args.client_db.expanduser().resolve()
    config = args.client_config.expanduser().resolve()
    client_root = args.client_root.expanduser().resolve()
    out = args.work_dir.expanduser().resolve() / ("lod-cache-reuse-" + stamp)
    if args.resume:
        out = args.work_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=args.resume)

    say("Preparing lossless merge. Backup:",out)
    ensure_game_closed(client_root)
    if not server_db.is_file() or not client_db.is_file():
        raise FileNotFoundError("Selected DH SQLite files are missing")
    if not config.is_file():
        raise FileNotFoundError("Selected client DistantHorizons config is missing")
    before=counts(client_db)
    say("Client before:",before)
    if not (out/"server-snapshot.sqlite").exists(): snapshot(server_db,out/"server-snapshot.sqlite")
    if not (out/"merged-client.sqlite").exists(): snapshot(client_db,out/"merged-client.sqlite")
    merged=out/"merged-client.sqlite"
    s=sqlite3.connect(str(merged),timeout=120)
    s.execute("PRAGMA synchronous=NORMAL")
    s.execute("PRAGMA busy_timeout=120000")
    s.execute("ATTACH DATABASE ? AS source",(str(out/"server-snapshot.sqlite"),))
    say("Merging server-only FullData rows while preserving client rows...")
    s.execute("BEGIN IMMEDIATE")
    try:
        s.execute("INSERT OR IGNORE INTO main.FullData SELECT * FROM source.FullData")
        added_full=s.execute("SELECT changes()").fetchone()[0]
        say("FullData added:",added_full)
        s.execute("INSERT OR IGNORE INTO main.ChunkHash SELECT * FROM source.ChunkHash")
        added_hash=s.execute("SELECT changes()").fetchone()[0]
        say("ChunkHash added:",added_hash)
        s.execute("INSERT OR IGNORE INTO main.BeaconBeam SELECT * FROM source.BeaconBeam")
        s.commit()
    except:
        s.rollback()
        raise
    s.execute("DETACH DATABASE source")
    say("Verifying SQLite database integrity...")
    result=s.execute("PRAGMA quick_check").fetchone()[0]
    if result != "ok": raise RuntimeError("Merged database did not pass quick_check: "+str(result))
    s.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    # Make the staged database standalone. Never replace the client DB with a leftover WAL.
    s.execute("PRAGMA journal_mode=DELETE")
    s.close()
    after=counts(merged)
    say("Merged result:",after)
    if after["FullData"] != before["FullData"]+added_full or after["ChunkHash"] != before["ChunkHash"]+added_hash:
        raise RuntimeError("Merged row counts did not match expectations.")
    ensure_game_closed()
    say("Swapping in verified merged DB, preserving original files for rollback...")
    original=out/"original-client-files"
    original.mkdir()
    moved=[]
    for suffix in ("","-wal","-shm"):
        old=Path(str(client_db)+suffix)
        if old.exists():
            dest=original/("DistantHorizons.sqlite"+suffix)
            os.replace(old,dest)
            moved.append((old,dest))
    try:
        os.replace(merged,client_db)
    except:
        for old,backup in reversed(moved):
            os.replace(backup,old)
        raise
    backup_cfg=out/"client-DistantHorizons.toml.before"
    shutil.copy2(config,backup_cfg)
    src=config.read_text()
    old="\t\tdisableUnchangedChunkCheck = true"
    if old in src:
        config.write_text(src.replace(old,"\t\tdisableUnchangedChunkCheck = false",1))
        say("Re-enabled unchanged-chunk detection in original client config.")
    report={
      "created_utc":datetime.now(timezone.utc).isoformat(),
      "original_client_database":str(client_db),
      "source_server_database":str(server_db),
      "before":before,"after":after,
      "added_full_data_sections":added_full,
      "added_chunk_hashes":added_hash,
      "original_client_files_backup":str(original),
      "client_config_backup":str(backup_cfg),
      "server_snapshot":str(out/"server-snapshot.sqlite"),
      "integrity_check":result,
      "note":"Server database remained read-only; the selected client cache was enriched while the client was closed."
    }
    (out/"REPORT.json").write_text(json.dumps(report,indent=2))
    say("SUCCESS: Original client DB enriched; rollback stored in",out)
    say("FINAL:",json.dumps(report))
if __name__=="__main__":
    try:main()
    except Exception as e:
        say("FAILED:",type(e).__name__,str(e),"Original database is preserved unless final swap completed.")
        raise
