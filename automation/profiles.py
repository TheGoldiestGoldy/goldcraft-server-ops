#!/usr/bin/env python3
import hashlib
import io
import json
import os
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

HOME_DIR = Path.home()
CLIENT = HOME_DIR / ".local/share/PollyMC-Local/instances/1.21.1/minecraft"
SERVER_MODS = HOME_DIR / "Minecraft Fabric server 1.21.1/mods"
STATE = HOME_DIR / ".local/state/goldcraft-control"
DOWNLOAD_DIR = STATE / "downloads"
EXTRA_DIR = STATE / "profile-extras"
PROFILE_JSON = STATE / "client-profiles.json"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXTRA_DIR.mkdir(parents=True, exist_ok=True)

BUILTINS = {"minecraft", "java", "fabricloader", "fabric", "fabric-api"}
OPTIONAL_SERVER_MODS = {
    "distanthorizons", "seedrenderer", "spark", "worldedit", "xaeroworldmap",
    "flyspeed", "dynamiclights", "effortlessbuilding", "mr_no_caves"
}
PERFORMANCE_MODS = {
    "badoptimizations", "complexleafculling", "entityculling", "immediatelyfast",
    "iris", "modmenu", "sodium", "sodium-extra"
}

def read_metadata(path):
    try:
        with zipfile.ZipFile(path) as z:
            return json.loads(z.read("fabric.mod.json"))
    except Exception:
        return {}

def scan(folder):
    rows = {}
    for jar in sorted(folder.glob("*.jar")):
        meta = read_metadata(jar)
        mid = str(meta.get("id", jar.stem))
        rows[mid] = {
            "id": mid,
            "file": jar.name,
            "path": jar,
            "environment": str(meta.get("environment", "*")),
            "depends": set((meta.get("depends") or {}).keys()),
            "name": str(meta.get("name", mid)),
            "version": str(meta.get("version", "")),
        }
    return rows

def fetch_modrinth(project, loader, target, validator):
    params = urllib.parse.urlencode({
        "game_versions": json.dumps(["1.21.1"]),
        "loaders": json.dumps([loader]),
    })
    url = f"https://api.modrinth.com/v2/project/{project}/version?{params}"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "GoldcraftProfileBuilder/1.0"})
        versions = json.loads(urllib.request.urlopen(request, timeout=30).read())
        releases = [v for v in versions if v.get("version_type") == "release"] or versions
        releases.sort(key=lambda v: v.get("date_published", ""), reverse=True)
        file_info = next(f for f in releases[0]["files"] if f.get("primary")) if releases else None
        if file_info is None and releases:
            file_info = releases[0]["files"][0]
        if file_info:
            payload = urllib.request.urlopen(
                urllib.request.Request(file_info["url"], headers={"User-Agent": "GoldcraftProfileBuilder/1.0"}),
                timeout=60,
            ).read()
            if not validator(payload):
                raise ValueError("downloaded file failed validation")
            temporary = target.with_suffix(target.suffix + ".tmp")
            temporary.write_bytes(payload)
            os.replace(temporary, target)
            return {
                "project": project,
                "version": releases[0].get("version_number", ""),
                "source": f"https://modrinth.com/project/{project}",
                "file": file_info.get("filename", target.name),
                "refreshed": True,
            }
    except Exception as error:
        if not target.is_file():
            raise
        return {
            "project": project,
            "version": "cached compatible release",
            "source": f"https://modrinth.com/project/{project}",
            "file": target.name,
            "refreshed": False,
            "refreshError": type(error).__name__,
        }

def valid_podium(payload):
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            meta = json.loads(z.read("fabric.mod.json"))
            return str(meta.get("id", "")).lower() == "podium"
    except Exception:
        return False

def valid_shader(payload):
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            return any(name.startswith("shaders/") for name in z.namelist())
    except Exception:
        return False

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def add_file(archive, source, destination):
    archive.write(source, destination)

def options_text(profile):
    values = {
        "version": 3955,
        "ao": str(profile["ao"]).lower(),
        "biomeBlendRadius": profile["biomeBlend"],
        "enableVsync": "false",
        "entityDistanceScaling": profile["entityDistance"],
        "entityShadows": "false",
        "graphicsMode": 0,
        "guiScale": profile["guiScale"],
        "maxFps": profile["maxFps"],
        "mipmapLevels": profile["mipmaps"],
        "particles": profile["particles"],
        "prioritizeChunkUpdates": 0,
        "renderClouds": '"false"',
        "renderDistance": profile["renderDistance"],
        "simulationDistance": profile["simulationDistance"],
        "useNativeTransport": "true",
    }
    return "".join(f"{key}:{value}\n" for key, value in values.items())

def sodium_config(profile):
    return {
        "quality": {
            "weather_quality": "FAST",
            "leaves_quality": "FAST",
            "enable_vignette": False,
            "use_closest_point_entity_sort": False,
        },
        "advanced": {
            "enable_memory_tracing": False,
            "use_advanced_staging_buffers": True,
            "cpu_render_ahead_limit": profile["renderAhead"],
        },
        "performance": {
            "chunk_builder_threads": profile["chunkThreads"],
            "chunk_build_defer_mode": "ALWAYS",
            "animate_only_visible_textures": True,
            "use_entity_culling": True,
            "use_fog_occlusion": True,
            "use_block_face_culling": True,
            "use_no_error_g_l_context": True,
            "quad_splitting_mode": "SAFE",
        },
        "notifications": {"has_cleared_donation_button": False, "has_seen_donation_prompt": True},
        "debug": {"terrain_sorting_enabled": True},
    }

def nested_metadata(blob, provided, required, depth=0):
    if depth > 3:
        return
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            meta = json.loads(z.read("fabric.mod.json"))
            provided.add(str(meta.get("id", "")))
            provided.update(str(x) for x in (meta.get("provides") or []))
            required.update((meta.get("depends") or {}).keys())
            for entry in meta.get("jars") or []:
                name = entry.get("file") if isinstance(entry, dict) else None
                if name and name in z.namelist():
                    nested_metadata(z.read(name), provided, required, depth + 1)
    except Exception:
        return

def validate_dependencies(paths, external_ids):
    provided, required = set(external_ids), set()
    for path in paths:
        nested_metadata(path.read_bytes(), provided, required)
    unresolved = sorted(x for x in required if x not in provided and x not in BUILTINS and not x.startswith("fabric-"))
    return unresolved

client = scan(CLIENT / "mods")
server = scan(SERVER_MODS)
required_ids = {
    mid for mid, row in client.items()
    if mid in server and row["environment"] != "client" and mid not in OPTIONAL_SERVER_MODS
}
base_ids = required_ids | PERFORMANCE_MODS
missing_ids = sorted(mid for mid in base_ids if mid not in client)
if missing_ids:
    raise RuntimeError("Required local mods are missing: " + ", ".join(missing_ids))

podium_path = EXTRA_DIR / "podium.jar"
shader_path = EXTRA_DIR / "MakeUp-Ultra-Fast.zip"
podium_info = fetch_modrinth("podium", "fabric", podium_path, valid_podium)
shader_info = fetch_modrinth("makeup-ultra-fast-shaders", "iris", shader_path, valid_shader)

profiles = [
    {
        "key": "mobile",
        "title": "Amethyst + Podium",
        "description": "Android profile for Amethyst with MobileGlues or LTW. Podium is included beside Sodium. Shader is included but disabled by default.",
        "target": "Modern Android phone, Java 21, 3–4 GB heap",
        "recommendedMemoryMb": 3072,
        "renderDistance": 5, "simulationDistance": 4, "maxFps": 45,
        "mipmaps": 0, "biomeBlend": 0, "entityDistance": 0.5,
        "particles": 2, "ao": False, "guiScale": 3,
        "chunkThreads": 2, "renderAhead": 2, "shaderEnabled": False,
        "extraMods": [podium_path],
        "filename": "goldcraft-profile-mobile-amethyst.zip",
        "notes": [
            "Select MobileGlues first; LTW is an alternative if the device supports it.",
            "Podium only removes Sodium's launcher block and cannot guarantee renderer compatibility.",
            "Start without shaders. Enable MakeUp only after the server is stable.",
        ],
    },
    {
        "key": "basicLaptop",
        "title": "Basic 8 GB laptop",
        "description": "Conservative profile for an older i5, integrated or weak graphics, and 8 GB system RAM. Shader is included but disabled by default.",
        "target": "Older Intel i5, integrated/old laptop GPU, 8 GB RAM",
        "recommendedMemoryMb": 3072,
        "renderDistance": 6, "simulationDistance": 4, "maxFps": 45,
        "mipmaps": 0, "biomeBlend": 0, "entityDistance": 0.6,
        "particles": 2, "ao": False, "guiScale": 2,
        "chunkThreads": 2, "renderAhead": 2, "shaderEnabled": False,
        "extraMods": [],
        "filename": "goldcraft-profile-basic-laptop.zip",
        "notes": [
            "Use 1280×720 or 1600×900 if 1080p cannot hold the target frame rate.",
            "Keep the included shader disabled for the first test.",
            "Close browsers and other memory-heavy applications before launching.",
        ],
    },
    {
        "key": "niceLaptop",
        "title": "16 GB / GTX 1060 class",
        "description": "Stable 1080p starting point for a newer i5/i7 and a 4–6 GB VRAM GPU. MakeUp Ultra Fast is enabled.",
        "target": "i5/i7, 16 GB RAM, GTX 1060-class or 4–6 GB VRAM GPU",
        "recommendedMemoryMb": 6144,
        "renderDistance": 8, "simulationDistance": 5, "maxFps": 60,
        "mipmaps": 2, "biomeBlend": 1, "entityDistance": 0.75,
        "particles": 1, "ao": True, "guiScale": 2,
        "chunkThreads": 3, "renderAhead": 3, "shaderEnabled": True,
        "extraMods": [],
        "filename": "goldcraft-profile-nice-laptop.zip",
        "notes": [
            "MakeUp Ultra Fast is enabled; disable it first if frame pacing drops below the target.",
            "Distant Horizons is intentionally omitted to protect frame-time stability.",
            "Raise render distance only after testing a busy MTR area.",
        ],
    },
]

generated = int(time.time())
results = {}
local_paths = [client[mid]["path"] for mid in sorted(base_ids)]
local_mod_rows = [
    {"id": mid, "name": client[mid]["name"], "version": client[mid]["version"], "file": client[mid]["file"]}
    for mid in sorted(base_ids)
]

for profile in profiles:
    all_mod_paths = local_paths + profile["extraMods"]
    unresolved = validate_dependencies(all_mod_paths, {"podium"} if profile["key"] == "mobile" else set())
    if unresolved:
        raise RuntimeError(f"{profile['key']} unresolved dependencies: {', '.join(unresolved)}")
    target = DOWNLOAD_DIR / profile["filename"]
    temporary = target.with_suffix(".zip.tmp")
    manifest = {
        "profile": profile["key"],
        "title": profile["title"],
        "generatedAt": generated,
        "minecraft": "1.21.1",
        "loader": "Fabric",
        "targetHardware": profile["target"],
        "recommendedMemoryMb": profile["recommendedMemoryMb"],
        "performanceTarget": "35–45 FPS starting target; not a hardware guarantee",
        "modCount": len(all_mod_paths),
        "mods": local_mod_rows + ([{"id": "podium", "name": "Podium", "version": podium_info["version"], "file": "podium.jar"}] if profile["key"] == "mobile" else []),
        "omittedByDesign": sorted(OPTIONAL_SERVER_MODS | {
            "controlflex", "entity_model_features", "entity_texture_features", "jei",
            "litematica", "malilib", "packforge", "polyweather", "reflex",
            "xaerominimap", "yet_another_config_lib_v3"
        }),
        "shader": {
            "name": "MakeUp Ultra Fast",
            "enabledByDefault": profile["shaderEnabled"],
            "source": shader_info["source"],
            "version": shader_info["version"],
        },
        "notes": profile["notes"],
    }
    readme = f"""GOLDCRAFT — {profile['title']}
Minecraft 1.21.1 / Fabric

Target: {profile['target']}
Recommended Java heap: {profile['recommendedMemoryMb']} MB
Performance goal: stable 35–45 FPS as a starting target, not a guarantee.

INSTALL
1. Create or select a clean Fabric 1.21.1 instance using Java 21.
2. Back up that instance.
3. Extract this ZIP into the instance's .minecraft folder.
4. Apply the recommended memory value in the launcher.
5. Test the server before raising render distance or enabling extra packs.

NOTES
- This pack keeps the server's required content mods and their libraries.
- Distant Horizons, maps, creator tools, high-end entity features, and the old heavy shader are omitted.
- Active MTR/resource packs are a separate website download so players can choose them.
- MakeUp Ultra Fast is included. It is disabled by default on mobile/basic and enabled on the nice-laptop profile.
- No fixed hardware can guarantee FPS in every build or crowded MTR area.

""" + "\n".join("- " + note for note in profile["notes"]) + "\n"
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        archive.writestr("goldcraft-profile.json", json.dumps(manifest, indent=2) + "\n")
        archive.writestr("README-GOLDCRAFT.txt", readme)
        archive.writestr("options.txt", options_text(profile))
        archive.writestr("config/sodium-options.json", json.dumps(sodium_config(profile), indent=2) + "\n")
        archive.writestr(
            "config/iris.properties",
            "allowUnknownShaders=false\ncolorSpace=SRGB\ndisableUpdateMessage=false\n"
            f"enableShaders={'true' if profile['shaderEnabled'] else 'false'}\n"
            "maxShadowRenderDistance=8\nshaderPack=MakeUp-Ultra-Fast.zip\n",
        )
        for path in local_paths:
            add_file(archive, path, "mods/" + path.name)
        for path in profile["extraMods"]:
            add_file(archive, path, "mods/" + path.name)
        add_file(archive, shader_path, "shaderpacks/MakeUp-Ultra-Fast.zip")
    os.replace(temporary, target)
    results[profile["key"]] = {
        "key": profile["key"],
        "title": profile["title"],
        "description": profile["description"],
        "target": profile["target"],
        "recommendedMemoryMb": profile["recommendedMemoryMb"],
        "renderDistance": profile["renderDistance"],
        "simulationDistance": profile["simulationDistance"],
        "shaderDefault": "enabled" if profile["shaderEnabled"] else "included, off by default",
        "modCount": len(all_mod_paths),
        "file": profile["filename"],
        "url": "/download/" + profile["filename"],
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
        "updatedAt": int(target.stat().st_mtime),
        "performanceTarget": "35–45 FPS starting target",
        "validated": True,
        "notes": profile["notes"],
    }

payload = {
    "generatedAt": generated,
    "source": "Derived daily from the server operator's active client and the actual server mod set",
    "podium": podium_info,
    "shader": shader_info,
    "profiles": results,
}
temporary_json = PROFILE_JSON.with_suffix(".tmp")
temporary_json.write_text(json.dumps(payload, indent=2) + "\n")
os.replace(temporary_json, PROFILE_JSON)
print(json.dumps({
    "profiles": {k: {"mods": v["modCount"], "bytes": v["bytes"], "sha256": v["sha256"]} for k, v in results.items()},
    "podium": podium_info,
    "shader": shader_info,
}))
