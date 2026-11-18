#!/usr/bin/env python3
"""Render human-readable reports from data/current-snapshot.json."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data/current-snapshot.json").read_text())

def gib(value):
    return "unknown" if value is None else f"{value / 1024**3:.2f} GiB"

def mib(value):
    return "unknown" if value is None else f"{value / 1024**2:.1f} MiB"

def write(relative, text):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")

h = data["hardware"]
p = data["server_properties"]
s = data["sizes"]
lod = data["lod"]
current = [
    "# Current state",
    "",
    f"Snapshot generated: {data['generated_at']}",
    "",
    "## Runtime and hardware",
    "",
    "| Item | Value |",
    "|---|---|",
    f"| Minecraft | {data['runtime']['minecraft']} |",
    f"| Loader | {data['runtime']['loader']} |",
    f"| OS / kernel | {data['runtime']['os']} / {data['runtime']['kernel']} |",
    f"| CPU | {h['cpu']} |",
    f"| Logical CPUs | {h['logical_cpus']} |",
    f"| GPU | {h['gpu']} |",
    f"| RAM / swap | {gib(h['memory_total_bytes'])} / {gib(h['swap_total_bytes'])} |",
    f"| Disk total / free | {gib(h['disk_total_bytes'])} / {gib(h['disk_free_bytes'])} |",
    "",
    "## Server baseline",
    "",
    "| Setting | Value |",
    "|---|---|",
    f"| Max players / tested target | {p.get('max-players')} / 15 |",
    f"| View / simulation distance | {p.get('view-distance')} / {p.get('simulation-distance')} chunks |",
    f"| Game mode / difficulty | {p.get('gamemode')} / {p.get('difficulty')} |",
    "| Heap | 4 GiB initial, 12 GiB maximum, 10 GiB soft maximum |",
    "| GC | Generational ZGC |",
    f"| Region compression | {p.get('region-file-compression')} |",
    f"| Synchronous chunk writes | {p.get('sync-chunk-writes')} |",
    "",
    "## Storage",
    "",
    "| Component | Size |",
    "|---|---:|",
    f"| Entire server directory | {gib(s['server_root'])} |",
    f"| Active world | {gib(s['world'])} |",
    f"| Overworld region data | {gib(s['world_region'])} |",
    f"| VSS/Voxy derived LOD store | {gib(s['world_vss_lod'])} |",
    f"| Archived logs | {mib(s['logs'])} |",
    f"| BlueMap | {mib(s['bluemap'])} |",
    "",
    "## Current Distant Horizons values",
    "",
    "| Key | Value |",
    "|---|---|",
]
current.extend(f"| {key} | {value} |" for key, value in lod["distant_horizons"].items())
current.extend(["", "## Current VSS/Voxy values", ""])
current.extend(f"- {key}: {value}" for key, value in lod["vss"].items())
current.extend([
    "",
    "The VSS service is currently disabled, but the active world's derived store remains on disk.",
    "Read the current incident record in docs/issues/lod-download-loop.md before changing DH or VSS.",
])
write("docs/current-state.md", "\n".join(current))

for scope in ("server", "client"):
    rows = data["mods"][scope]
    lines = [
        f"# {scope.title()} mod inventory",
        "",
        f"Count: **{len(rows)}**",
        "",
        "SHA-256 identifies the exact tested JAR. JAR binaries are not committed.",
        "",
        "| Mod | ID | Version | Environment | Size | SHA-256 |",
        "|---|---|---|---|---:|---|",
    ]
    for row in rows:
        name = row["name"].replace("|", "\\|")
        lines.append(
            f"| {name} | {row.get('id','')} | {row.get('version','')} | "
            f"{row.get('environment','')} | {mib(row['bytes'])} | {row['sha256']} |"
        )
    write(f"inventory/{scope}-mods.md", "\n".join(lines))
    with (ROOT / f"inventory/{scope}-mods.csv").open("w", newline="") as handle:
        fields = ["file", "id", "name", "version", "environment", "bytes", "sha256"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})

assets = data["client_assets"]
asset_lines = [
    "# Client assets and generated profiles",
    "",
    f"Active shader: {assets.get('active_shader') or 'disabled'}",
    "",
    "## Active resource packs",
    "",
]
asset_lines.extend(f"- {name}" for name in assets.get("active_resource_packs", []))
asset_lines.extend([
    "",
    "## Generated client profiles",
    "",
    "| Profile | Mods | Size | Target | SHA-256 |",
    "|---|---:|---:|---|---|",
])
for key, profile in assets.get("profiles", {}).items():
    asset_lines.append(
        f"| {profile.get('title', key)} | {profile.get('modCount')} | "
        f"{mib(profile.get('bytes'))} | {profile.get('target','')} | {profile.get('sha256','')} |"
    )
write("inventory/client-assets.md", "\n".join(asset_lines))

logs = data["logs"]
log_lines = [
    "# Log evidence summary",
    "",
    f"Files scanned: **{logs['files_scanned']}**",
    "",
    "> Counts are string matches, not unique incidents or confirmed root causes. Repeated startup warnings inflate totals.",
    "",
    "## Totals",
    "",
    "| Pattern | Matches |",
    "|---|---:|",
]
for key, value in sorted(logs["totals"].items(), key=lambda item: item[1], reverse=True):
    log_lines.append(f"| {key} | {value:,} |")
log_lines.extend([
    "",
    "## Daily evidence",
    "",
    "| Date | Warnings | Errors | Can't keep up | Tick stalls | DH | VSS | Chunky | Connections |",
    "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
])
for day, counts in logs["by_day"].items():
    log_lines.append(
        f"| {day} | {counts.get('warn',0)} | {counts.get('error',0)} | {counts.get('cant_keep_up',0)} | "
        f"{counts.get('tick_stall',0)} | {counts.get('dh_activity',0)} | {counts.get('vss_activity',0)} | "
        f"{counts.get('chunky_activity',0)} | {counts.get('connection_problem',0)} |"
    )
log_lines.extend(["", "## Crash reports", "", "| File | Description | First captured cause |", "|---|---|---|"])
for crash in data["crashes"]:
    log_lines.append(f"| {crash['file']} | {crash['description']} | {crash['first_cause']} |")
write("docs/log-evidence.md", "\n".join(log_lines))

timeline = [
    "# Change and backup timeline",
    "",
    "Derived from configuration backups and dated maintenance artifacts. Existence does not prove success.",
    "",
    "| Modified (UTC) | Artifact | Type | Size |",
    "|---|---|---|---:|",
]
for row in data["change_timeline"]:
    size = mib(row["bytes"]) if row["bytes"] is not None else "unknown"
    timeline.append(f"| {row['modified']} | {row['path']} | {row['type']} | {size} |")
write("docs/change-timeline.md", "\n".join(timeline))

sanitized = ["# Generated by tools/collect_snapshot.py; sensitive values are redacted."]
for key, value in sorted(p.items()):
    sanitized.append(f"{key}={value}")
write("configs/server.properties.sanitized", "\n".join(sanitized))

print(json.dumps({
    "server_mods": len(data["mods"]["server"]),
    "client_mods": len(data["mods"]["client"]),
    "days": len(logs["by_day"]),
    "timeline_items": len(data["change_timeline"]),
}))
