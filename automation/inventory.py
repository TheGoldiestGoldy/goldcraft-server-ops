#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import time
import zipfile
from pathlib import Path

HOME_DIR = Path.home()
CLIENT = HOME_DIR / ".local/share/PollyMC-Local/instances/1.21.1/minecraft"
OUTPUT = HOME_DIR / ".local/state/goldcraft-control/client-inventory.json"
DOWNLOAD_DIR = OUTPUT.parent / "downloads"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

def fabric_mods():
    rows = []
    for jar in sorted((CLIENT / "mods").glob("*.jar"), key=lambda p: p.name.lower()):
        row = {"file": jar.name, "name": jar.stem, "id": "", "version": "", "bytes": jar.stat().st_size}
        try:
            with zipfile.ZipFile(jar) as archive:
                meta = json.loads(archive.read("fabric.mod.json"))
            row["id"] = str(meta.get("id", ""))
            name = meta.get("name")
            row["name"] = name if isinstance(name, str) else row["id"] or jar.stem
            row["version"] = str(meta.get("version", ""))
        except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError):
            pass
        rows.append(row)
    return rows

def options_list(key):
    try:
        for line in (CLIENT / "options.txt").read_text(errors="replace").splitlines():
            if line.startswith(key + ":"):
                value = json.loads(line.split(":", 1)[1])
                return [str(item).removeprefix("file/") for item in value if str(item).startswith("file/")]
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    return []

def pack_description(path):
    try:
        if path.is_dir():
            raw = (path / "pack.mcmeta").read_text(errors="replace")
        else:
            with zipfile.ZipFile(path) as archive:
                raw = archive.read("pack.mcmeta").decode(errors="replace")
        description = json.loads(raw).get("pack", {}).get("description", "")
        if isinstance(description, str):
            return description
        if isinstance(description, dict):
            return str(description.get("text", ""))
    except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError):
        pass
    return ""

def resource_packs():
    active = set(options_list("resourcePacks"))
    rows = []
    folder = CLIENT / "resourcepacks"
    if folder.exists():
        for path in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
            if path.name.startswith("."):
                continue
            rows.append({
                "name": path.name,
                "active": path.name in active,
                "description": pack_description(path),
                "bytes": path.stat().st_size if path.is_file() else 0,
            })
    return rows

def iris_settings():
    values = {}
    try:
        for line in (CLIENT / "config/iris.properties").read_text(errors="replace").splitlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                values[key] = value
    except OSError:
        pass
    return values

def shader_packs():
    iris = iris_settings()
    active = iris.get("shaderPack", "") if iris.get("enableShaders", "false").lower() == "true" else ""
    rows = []
    folder = CLIENT / "shaderpacks"
    if folder.exists():
        for path in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
            if path.name.startswith(".") or path.name.endswith(".txt"):
                continue
            rows.append({
                "name": path.name,
                "active": path.name == active,
                "bytes": path.stat().st_size if path.is_file() else 0,
            })
    return rows, active, iris.get("enableShaders", "false").lower() == "true"

def add_to_zip(archive, source, folder):
    if source.is_file():
        archive.write(source, str(Path(folder) / source.name))
    elif source.is_dir():
        for item in source.rglob("*"):
            if item.is_file():
                archive.write(item, str(Path(folder) / source.name / item.relative_to(source)))

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def build_archive(filename, groups, manifest):
    target = DOWNLOAD_DIR / filename
    temporary = DOWNLOAD_DIR / (filename + ".tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        archive.writestr("goldcraft-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        for folder, paths in groups:
            for source in paths:
                add_to_zip(archive, source, folder)
    os.replace(temporary, target)
    return {
        "file": filename,
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
        "updatedAt": int(target.stat().st_mtime),
        "url": "/download/" + filename,
    }

mods = fabric_mods()
resources = resource_packs()
shaders, active_shader, shaders_enabled = shader_packs()
generated = int(time.time())
active_resources = [item["name"] for item in resources if item["active"]]
mod_paths = [CLIENT / "mods" / item["file"] for item in mods]
resource_paths = [CLIENT / "resourcepacks" / name for name in active_resources]
shader_paths = [CLIENT / "shaderpacks" / item["name"] for item in shaders]
manifest = {
    "generatedAt": generated,
    "minecraft": "1.21.1",
    "loader": "Fabric",
    "modCount": len(mods),
    "activeResourcePacks": active_resources,
    "activeShader": active_shader,
    "notes": "Files copied from the server operator's active PollyMC client. Extract into the matching Minecraft instance. Pack activation order is not automatically applied.",
}
downloads = {
    "mods": build_archive("goldcraft-mods.zip", [("mods", mod_paths)], manifest),
    "resourcePacks": build_archive("goldcraft-active-resourcepacks.zip", [("resourcepacks", resource_paths)], manifest),
    "shaders": build_archive("goldcraft-shaderpacks.zip", [("shaderpacks", shader_paths)], manifest),
    "combined": build_archive("goldcraft-client-files.zip", [("mods", mod_paths), ("resourcepacks", resource_paths), ("shaderpacks", shader_paths)], manifest),
}
profile_snapshot = {}
try:
    subprocess.run(
        ["python3", str(HOME_DIR / ".local/share/goldcraft-control/profiles.py")],
        check=True,
        timeout=900,
    )
except (OSError, subprocess.SubprocessError):
    pass
try:
    profile_snapshot = json.loads((OUTPUT.parent / "client-profiles.json").read_text())
except (OSError, ValueError, json.JSONDecodeError):
    pass
payload = {
    "generatedAt": generated,
    "source": "Active PollyMC Fabric 1.21.1 client",
    "mods": mods,
    "modCount": len(mods),
    "resourcePacks": resources,
    "resourcePackCount": len(resources),
    "activeResourcePacks": active_resources,
    "shaderPacks": shaders,
    "shaderPackCount": len(shaders),
    "activeShader": active_shader,
    "shadersEnabled": shaders_enabled,
    "downloads": downloads,
    "profiles": profile_snapshot.get("profiles", {}),
    "profileGeneratedAt": profile_snapshot.get("generatedAt"),
}
temporary = OUTPUT.with_suffix(".tmp")
temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
os.replace(temporary, OUTPUT)
print(json.dumps({
    "generatedAt": payload["generatedAt"],
    "modCount": payload["modCount"],
    "resourcePackCount": payload["resourcePackCount"],
    "activeResourcePacks": len(payload["activeResourcePacks"]),
    "shaderPackCount": payload["shaderPackCount"],
    "activeShader": payload["activeShader"],
    "downloads": {key: value["bytes"] for key, value in downloads.items()},
}))
