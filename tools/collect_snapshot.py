#!/usr/bin/env python3
"""Create a sanitized, reproducible Goldcraft operations snapshot.

The collector never copies player lists, IP addresses, authentication tokens,
world seeds, chat, or raw log lines. It records metadata and aggregate counts.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

SENSITIVE_PROPERTY_KEYS = {
    "rcon.password", "level-seed", "server-ip", "resource-pack",
    "resource-pack-id", "resource-pack-sha1", "resource-pack-prompt",
}
LOG_PATTERNS = {
    "cant_keep_up": re.compile(r"Can't keep up|server is overloaded", re.I),
    "tick_stall": re.compile(r"took [0-9.]+ seconds|running [0-9]+ms or [0-9]+ ticks behind", re.I),
    "out_of_memory": re.compile(r"OutOfMemory|Java heap space", re.I),
    "dh_activity": re.compile(r"Distant Horizons|\bDH\b|LOD", re.I),
    "vss_activity": re.compile(r"\bVSS\b|vsslod|receivedColumns", re.I),
    "chunky_activity": re.compile(r"\[Chunky\]|chunky", re.I),
    "sqlite_problem": re.compile(r"SQLite.*(?:error|exception)|SQLException", re.I),
    "connection_problem": re.compile(r"timed out|connection reset|disconnect", re.I),
    "join_event": re.compile(r" joined the game$"),
    "leave_event": re.compile(r" left the game$"),
}

def command(args: list[str]) -> str:
    try:
        process = subprocess.run(args, text=True, capture_output=True, timeout=20, check=False)
        return (process.stdout + process.stderr).strip()
    except (OSError, subprocess.SubprocessError):
        return ""

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def fabric_metadata(jar: Path) -> dict:
    row = {
        "file": jar.name,
        "bytes": jar.stat().st_size,
        "sha256": sha256(jar),
        "id": "",
        "name": jar.stem,
        "version": "",
        "environment": "unknown",
    }
    try:
        with zipfile.ZipFile(jar) as archive:
            meta = json.loads(archive.read("fabric.mod.json"))
        row.update({
            "id": str(meta.get("id", "")),
            "name": str(meta.get("name", meta.get("id", jar.stem))),
            "version": str(meta.get("version", "")),
            "environment": str(meta.get("environment", "*")),
            "depends": sorted((meta.get("depends") or {}).keys()),
        })
    except Exception as error:
        row["metadata_error"] = type(error).__name__
    return row

def properties(path: Path) -> dict:
    result = {}
    if not path.is_file():
        return result
    for line in path.read_text(errors="replace").splitlines():
        if "=" not in line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        result[key] = "[redacted]" if key in SENSITIVE_PROPERTY_KEYS else value
    return result

def directory_size(path: Path) -> int | None:
    if not path.exists():
        return None
    output = command(["du", "-sb", str(path)])
    try:
        return int(output.split()[0])
    except (ValueError, IndexError):
        return None

def config_values(path: Path, wanted: list[str]) -> dict:
    result = {}
    if not path.is_file():
        return result
    text = path.read_text(errors="replace")
    for key in wanted:
        matches = re.findall(rf"(?m)^\s*{re.escape(key)}\s*[:=]\s*([^#\r\n]+)", text)
        if matches:
            result[key] = matches[-1].strip().strip('"')
    return result

def open_log(path: Path):
    return gzip.open(path, "rt", errors="replace") if path.suffix == ".gz" else path.open(errors="replace")

def aggregate_logs(log_dir: Path) -> dict:
    totals = Counter()
    by_day = defaultdict(Counter)
    files = []
    candidates = sorted(log_dir.glob("*.log.gz")) + ([log_dir / "latest.log"] if (log_dir / "latest.log").is_file() else [])
    for path in candidates:
        local = Counter()
        try:
            with open_log(path) as handle:
                for line in handle:
                    if "/WARN]" in line or "[WARN]" in line:
                        local["warn"] += 1
                    if "/ERROR]" in line or "[ERROR]" in line:
                        local["error"] += 1
                    for name, pattern in LOG_PATTERNS.items():
                        if pattern.search(line):
                            local[name] += 1
        except OSError:
            local["read_error"] += 1
        date_match = re.search(r"(20\d\d-\d\d-\d\d)", path.name)
        day = date_match.group(1) if date_match else dt.datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
        by_day[day].update(local)
        totals.update(local)
        files.append({"file": path.name, "bytes": path.stat().st_size, "counts": dict(local)})
    return {
        "files_scanned": len(files),
        "totals": dict(totals),
        "by_day": {day: dict(counts) for day, counts in sorted(by_day.items())},
        "files": files,
        "note": "Counts are pattern matches, not confirmed root causes. Raw log lines and player identifiers are excluded.",
    }

def crash_reports(folder: Path) -> list[dict]:
    rows = []
    for path in sorted(folder.glob("*.txt")):
        description = ""
        cause = ""
        try:
            for line in path.read_text(errors="replace").splitlines():
                if line.startswith("Description:") and not description:
                    description = line.split(":", 1)[1].strip()
                if "Caused by:" in line and not cause:
                    cause = line.split("Caused by:", 1)[1].strip()[:240]
        except OSError:
            pass
        rows.append({"file": path.name, "description": description, "first_cause": cause})
    return rows

def backup_timeline(server: Path) -> list[dict]:
    patterns = [
        "config/*.bak", "config/*.before-*", "server.properties.before-*",
        "start*.before-*", "maintenance/*2026*", "stutter-*",
    ]
    seen = set()
    rows = []
    for pattern in patterns:
        for path in server.glob(pattern):
            if path in seen:
                continue
            seen.add(path)
            rows.append({
                "path": str(path.relative_to(server)),
                "type": "directory" if path.is_dir() else "file",
                "modified": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(),
                "bytes": directory_size(path) if path.is_dir() else path.stat().st_size,
            })
    return sorted(rows, key=lambda row: (row["modified"], row["path"]))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-root", type=Path, required=True)
    parser.add_argument("--client-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    server = args.server_root.resolve()
    client = args.client_root.resolve() if args.client_root else None

    server_mods = [fabric_metadata(path) for path in sorted((server / "mods").glob("*.jar"), key=lambda p: p.name.lower())]
    client_mods = [fabric_metadata(path) for path in sorted((client / "mods").glob("*.jar"), key=lambda p: p.name.lower())] if client else []
    props = properties(server / "server.properties")
    inventory = {}
    inventory_file = Path.home() / ".local/state/goldcraft-control/client-inventory.json"
    try:
        inventory = json.loads(inventory_file.read_text())
    except (OSError, ValueError):
        pass

    dh_wanted = [
        "synchronizeOnLoad", "enableRealTimeUpdates", "maxSyncOnLoadRequestDistance",
        "maxGenerationRequestDistance", "generationRequestRateLimit", "syncOnLoadRateLimit",
        "globalBandwidthLimit", "playerBandwidthLimit", "enableAdaptiveTransferSpeed",
        "numberOfThreads", "generatorPlan", "chunkGeneratorMode", "rendererMode",
    ]
    vss_wanted = [
        "enabled", "max_size_mib", "max_mib_per_second_per_player",
        "max_mib_per_second_global", "background_backfill_enabled",
        "max_concurrent_disk_reads", "disk_reader_threads",
    ]

    disk = shutil.disk_usage(server)
    memory = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            memory[key] = int(value.strip().split()[0]) * 1024
    except OSError:
        pass

    payload = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "privacy": {
            "raw_logs_included": False,
            "player_names_included": False,
            "ips_included": False,
            "tokens_included": False,
            "world_seed_included": False,
        },
        "runtime": {
            "minecraft": "1.21.1",
            "loader": "Fabric",
            "java": command([str(Path.home() / "adoptium-jdk21/bin/java"), "-version"]).splitlines()[:3],
            "kernel": platform.release(),
            "os": platform.freedesktop_os_release().get("PRETTY_NAME", ""),
        },
        "hardware": {
            "cpu": command(["bash", "-lc", "lscpu | awk -F: '/Model name/{gsub(/^[ \\t]+/,\"\",$2);print $2;exit}'"]),
            "logical_cpus": os.cpu_count(),
            "gpu": command(["bash", "-lc", "lspci | grep -Ei 'VGA|3D|Display' | sed 's/^[^ ]* //'"]),
            "memory_total_bytes": memory.get("MemTotal"),
            "swap_total_bytes": memory.get("SwapTotal"),
            "disk_total_bytes": disk.total,
            "disk_used_bytes": disk.used,
            "disk_free_bytes": disk.free,
        },
        "server_properties": props,
        "security_flags": {
            "online_mode": props.get("online-mode"),
            "whitelist": props.get("white-list"),
            "enforce_whitelist": props.get("enforce-whitelist"),
            "log_ips": props.get("log-ips"),
            "rcon_enabled": props.get("enable-rcon"),
            "status_enabled": props.get("enable-status"),
        },
        "sizes": {
            "server_root": directory_size(server),
            "world": directory_size(server / "world"),
            "world_region": directory_size(server / "world/region"),
            "world_vss_lod": directory_size(server / "world/vss-lod"),
            "logs": directory_size(server / "logs"),
            "bluemap": directory_size(server / "bluemap"),
        },
        "mods": {
            "server_count": len(server_mods),
            "client_count": len(client_mods),
            "server": server_mods,
            "client": client_mods,
            "server_disabled": sorted(path.name for path in (server / "mods.disabled").glob("*.jar")),
        },
        "client_assets": {
            "active_resource_packs": inventory.get("activeResourcePacks", []),
            "resource_packs": inventory.get("resourcePacks", []),
            "active_shader": inventory.get("activeShader", ""),
            "shader_packs": inventory.get("shaderPacks", []),
            "profiles": inventory.get("profiles", {}),
        },
        "lod": {
            "distant_horizons": config_values(server / "config/DistantHorizons.toml", dh_wanted),
            "vss": config_values(server / "config/vss-server-config.yaml", vss_wanted),
            "chunky": properties(server / "config/chunky/config.json"),
            "vss_directories": [
                {"path": str(path.relative_to(server)), "bytes": directory_size(path)}
                for path in (
                    list((server / "world").glob("*vss*"))
                    + list((server / "validation-world").glob("*vss*"))
                    + list((server / "maintenance").glob("*vss*"))
                    + list((server / "maintenance").glob("*voxy*"))
                )
                if path.is_dir()
            ][:100],
        },
        "logs": aggregate_logs(server / "logs"),
        "crashes": crash_reports(server / "crash-reports"),
        "change_timeline": backup_timeline(server),
        "automation": {
            "goldcraft_control_active": command(["systemctl", "--user", "is-active", "goldcraft-control.service"]),
            "goldcraft_inventory_timer": command(["systemctl", "--user", "is-enabled", "goldcraft-inventory.timer"]),
            "next_inventory_run": command(["systemctl", "--user", "list-timers", "goldcraft-inventory.timer", "--no-legend"]),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    os.replace(temporary, args.output)
    print(json.dumps({
        "output": str(args.output),
        "server_mods": len(server_mods),
        "client_mods": len(client_mods),
        "logs_scanned": payload["logs"]["files_scanned"],
        "crashes": len(payload["crashes"]),
        "world_bytes": payload["sizes"]["world"],
    }))

if __name__ == "__main__":
    main()
