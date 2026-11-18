"""Compare the stopped server world with its backup without changing either."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "world"
BACKUP = Path(r"<EXTERNAL_DRIVE>/backup\Minecraft-Fabric-1.21.1-lod-2026-10-22")


def inventory(folder: Path):
    return {
        path.relative_to(folder).as_posix(): (path.stat().st_size, path.stat().st_mtime_ns)
        for path in folder.rglob("*")
        if path.is_file() and path.name != "INCOMPLETE.txt"
    }


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    if not SOURCE.is_dir() or not BACKUP.is_dir():
        raise SystemExit("Source world or backup folder is missing")
    source = inventory(SOURCE)
    backup = inventory(BACKUP)
    missing = sorted(source.keys() - backup.keys())
    extra = sorted(backup.keys() - source.keys())
    wrong_size = sorted(name for name in source.keys() & backup.keys() if source[name][0] != backup[name][0])
    wrong_time = sorted(
        name for name in source.keys() & backup.keys()
        if source[name][0] == backup[name][0] and abs(source[name][1] - backup[name][1]) > 2_000_000_000
    )
    print(f"Source: {len(source):,} files, {sum(size for size, _ in source.values()) / 2**30:.2f} GiB")
    print(f"Backup: {len(backup):,} files, {sum(size for size, _ in backup.values()) / 2**30:.2f} GiB")
    print(f"Missing: {len(missing)}, extra: {len(extra)}, wrong size: {len(wrong_size)}, wrong timestamp: {len(wrong_time)}")
    for label, names in (("missing", missing), ("extra", extra), ("wrong size", wrong_size), ("wrong timestamp", wrong_time)):
        for name in names[:8]:
            print(f"  {label}: {name}")
    if missing or wrong_size or wrong_time:
        raise SystemExit(1)
    for name in ("level.dat", "data/DistantHorizons.sqlite"):
        a, b = SOURCE / name, BACKUP / name
        if a.exists() and b.exists():
            matches = sha256(a) == sha256(b)
            print(f"SHA-256 {name}: {'match' if matches else 'MISMATCH'}")
            if not matches:
                raise SystemExit(1)
    if extra:
        print("Backup is a safe superset; extra older files are retained for review.")
    else:
        print("Backup file set matches the stopped world.")


if __name__ == "__main__":
    main()
