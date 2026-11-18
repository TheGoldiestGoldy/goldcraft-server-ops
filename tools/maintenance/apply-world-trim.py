"""Apply or restore the reviewed Overworld region-file trim.

Default mode is a dry run. --apply removes only files already verified in the
separate affected-file backup. --restore copies those files back from backup.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import socket
from datetime import datetime, timezone
from pathlib import Path

import psutil


ROOT = Path(__file__).resolve().parent.parent
WORLD = ROOT / "world"
BACKUP = Path(r"<EXTERNAL_DRIVE>/backup\Minecraft-Fabric-1.21.1-lod-2026-10-22")
PLAN = ROOT / "maintenance" / "world-trim-preview-2026-10-22.csv"
MASK = ROOT / "maintenance" / "world-trim-preview-2026-10-22-mask.json"
BACKUP_MARKER = BACKUP / "TRIM-AFFECTED-FILES-VERIFIED.txt"
PROGRESS = ROOT / "maintenance" / "world-trim-IN-PROGRESS.txt"
DONE = ROOT / "maintenance" / "world-trim-DONE.txt"
UNDO_MANIFEST = ROOT / "maintenance" / "world-trim-undo-manifest.csv"
CHUNKY_TASK = ROOT / "config" / "chunky" / "tasks" / "minecraft" / "overworld.properties"
CHUNKY_DISABLED = CHUNKY_TASK.with_name(CHUNKY_TASK.name + ".disabled")


def require_server_off():
    for process in psutil.process_iter(["name"]):
        try:
            if (process.info["name"] or "").lower() == "java.exe":
                raise RuntimeError("A Java server process is running; stop it cleanly first")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(0.3)
        if connection.connect_ex(("127.0.0.1", 25566)) == 0:
            raise RuntimeError("Minecraft port 25566 is open; stop the server first")


def planned_files():
    with PLAN.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 7431:
        raise RuntimeError(f"Unexpected number of region decisions: {len(rows)}")
    mask = json.loads(MASK.read_text(encoding="utf-8"))
    kept = {tuple(pair) for pair in mask["kept_existing_regions"]}
    if len(kept) != 1883:
        raise RuntimeError("Trim mask has an unexpected number of kept regions")
    files = []
    for row in rows:
        coords = (int(row["region_x"]), int(row["region_z"]))
        should_keep = coords in kept
        if (row["decision"] == "keep") != should_keep:
            raise RuntimeError(f"CSV/mask disagreement at {coords}")
        if should_keep:
            continue
        name = f"r.{coords[0]}.{coords[1]}.mca"
        for kind in ("region", "poi", "entities"):
            relative = Path(kind) / name
            source = WORLD / relative
            backup = BACKUP / relative
            if source.exists() or backup.exists():
                files.append((relative, source, backup))
    if len(files) != 10844:
        raise RuntimeError(f"Unexpected affected-file count: {len(files)}")
    return rows, files


def verify_backup(files):
    if not BACKUP_MARKER.is_file():
        raise RuntimeError("Affected-file backup has not been verified")
    world_root = WORLD.resolve(strict=True)
    backup_root = BACKUP.resolve(strict=True)
    total = 0
    for relative, source, backup in files:
        if source.exists():
            if not source.resolve(strict=True).is_relative_to(world_root):
                raise RuntimeError(f"Unsafe source path: {source}")
            left = source.stat()
            total += left.st_size
            if not backup.is_file() or not backup.resolve(strict=True).is_relative_to(backup_root):
                raise RuntimeError(f"Backup missing or outside backup root: {relative}")
            right = backup.stat()
            if left.st_size != right.st_size or abs(left.st_mtime_ns - right.st_mtime_ns) > 2_000_000_000:
                raise RuntimeError(f"Backup differs from source: {relative}")
        elif not backup.is_file():
            raise RuntimeError(f"Both source and backup are missing: {relative}")
    return total


def write_undo_manifest(files):
    with UNDO_MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("world_relative_path", "bytes_in_backup"))
        for relative, _, backup in files:
            writer.writerow((relative.as_posix(), backup.stat().st_size))


def apply(files):
    if DONE.exists():
        print("Trim already marked complete; no files changed")
        return
    if not PROGRESS.exists():
        write_undo_manifest(files)
        PROGRESS.write_text(
            f"Started UTC: {datetime.now(timezone.utc).isoformat()}\n"
            "Recovery: python maintenance/apply-world-trim.py --restore\n",
            encoding="utf-8",
        )
    removed = 0
    bytes_removed = 0
    for relative, source, _ in files:
        if not source.exists():
            continue  # Resume an interrupted trim.
        size = source.stat().st_size
        source.unlink()
        removed += 1
        bytes_removed += size
        if removed % 500 == 0:
            print(f"Removed {removed:,} backed-up files", flush=True)
    if CHUNKY_TASK.is_file():
        if CHUNKY_DISABLED.exists():
            raise RuntimeError("Both active and disabled Chunky tasks exist")
        task_backup = BACKUP / "config" / "chunky" / "tasks" / "minecraft" / CHUNKY_TASK.name
        task_backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CHUNKY_TASK, task_backup)
        os.replace(CHUNKY_TASK, CHUNKY_DISABLED)
    remaining = sum(1 for path in (WORLD / "region").glob("r.*.*.mca") if path.is_file())
    if remaining != 1883:
        raise RuntimeError(f"Unexpected number of kept regions: {remaining}")
    DONE.write_text(
        f"Completed UTC: {datetime.now(timezone.utc).isoformat()}\n"
        f"Affected files: {len(files)}\nMoved to verified backup: yes\n"
        f"Removed this run: {removed}\nBytes removed this run: {bytes_removed}\n"
        "Recovery: python maintenance/apply-world-trim.py --restore\n",
        encoding="utf-8",
    )
    PROGRESS.unlink(missing_ok=True)
    print(f"Trim complete: {remaining:,} terrain regions remain; removed {bytes_removed / 2**30:.2f} GiB this run")


def restore(files):
    restored = 0
    for relative, source, backup in files:
        if source.exists():
            continue
        source.parent.mkdir(parents=True, exist_ok=True)
        temporary = source.with_name(source.name + ".restoring")
        shutil.copy2(backup, temporary)
        if temporary.stat().st_size != backup.stat().st_size:
            raise RuntimeError(f"Restore copy differs: {relative}")
        os.replace(temporary, source)
        restored += 1
        if restored % 500 == 0:
            print(f"Restored {restored:,} files", flush=True)
    if CHUNKY_DISABLED.is_file() and not CHUNKY_TASK.exists():
        os.replace(CHUNKY_DISABLED, CHUNKY_TASK)
    DONE.unlink(missing_ok=True)
    PROGRESS.unlink(missing_ok=True)
    print(f"Restored {restored:,} world files from backup")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true")
    group.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    require_server_off()
    rows, files = planned_files()
    total = verify_backup(files)
    if args.apply:
        if not PROGRESS.exists() and not DONE.exists():
            existing = sum(1 for path in (WORLD / "region").glob("r.*.*.mca") if path.is_file())
            if existing != len(rows):
                raise RuntimeError(f"World changed since preview: {existing} regions versus {len(rows)}")
        apply(files)
    elif args.restore:
        restore(files)
    else:
        print(f"DRY RUN: {len(files):,} affected files, {total / 2**30:.2f} GiB currently on source")
        print("Use --apply to perform the reviewed trim; --restore copies removed files back")


if __name__ == "__main__":
    main()
