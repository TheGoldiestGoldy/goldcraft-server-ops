#!/usr/bin/env python3
import hmac
import json
import mimetypes
import os
import re
import signal
import subprocess
import threading
import time
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOME_DIR = Path.home()
SERVER_DIR = (HOME_DIR / "Minecraft Fabric server 1.21.1").resolve()
CLIENT_MODS_DIR = (HOME_DIR / ".local/share/PollyMC-Local/instances/1.21.1/minecraft/mods").resolve()
INVENTORY_FILE = HOME_DIR / ".local/state/goldcraft-control/client-inventory.json"
DOWNLOAD_DIR = INVENTORY_FILE.parent / "downloads"
HERE = Path(__file__).resolve().parent
DEFAULT_SITE_DIR = HERE.parent / "site" if (HERE.parent / "site").is_dir() else HERE / "site"
SITE_DIR = Path(os.environ.get("GOLDCRAFT_SITE_DIR", DEFAULT_SITE_DIR)).resolve()
START_COMMAND = ["/bin/bash", "./start.sh"]
AUTH_VALUE = (HOME_DIR / ".config/goldcraft-control/token").read_text().strip()
LOG_DIR = HOME_DIR / ".local/state/goldcraft-control"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOCK = threading.Lock()
OWNED_PROCESS = None
STOP_REQUESTED = False

def find_server():
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            cmd = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            if cmd.startswith(str(HOME_DIR / "adoptium-jdk21/bin/java") + " ") and " -jar fabric-server-launch.jar nogui" in cmd:
                stat = (entry / "stat").read_text().split()
                started_ticks = int(stat[21])
                uptime = float(Path("/proc/uptime").read_text().split()[0])
                hz = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
                return int(entry.name), max(0, int(uptime - started_ticks / hz))
        except (FileNotFoundError, PermissionError, ProcessLookupError, ValueError):
            continue
    return None, None

def response_state(message=None):
    pid, uptime = find_server()
    state = "running" if pid else "stopped"
    if STOP_REQUESTED and pid:
        state = "stopping"
    result = {"state": state, "pid": pid, "uptimeSeconds": uptime}
    if message:
        result["message"] = message
    return result

def client_mods():
    mods = []
    newest = 0
    for jar in sorted(CLIENT_MODS_DIR.glob("*.jar"), key=lambda p: p.name.lower()):
        newest = max(newest, jar.stat().st_mtime)
        item = {"file": jar.name, "name": jar.stem, "id": "", "version": ""}
        try:
            with zipfile.ZipFile(jar) as archive:
                meta = json.loads(archive.read("fabric.mod.json"))
            item["id"] = str(meta.get("id", ""))
            raw_name = meta.get("name")
            item["name"] = raw_name if isinstance(raw_name, str) else item["id"] or jar.stem
            item["version"] = str(meta.get("version", ""))
        except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError):
            pass
        mods.append(item)
    return mods, newest

def online_player_count():
    players = set()
    try:
        for line in (SERVER_DIR / "logs/latest.log").read_text(errors="replace").splitlines():
            joined = re.search(r": ([A-Za-z0-9_]{1,16}) joined the game$", line)
            left = re.search(r": ([A-Za-z0-9_]{1,16}) left the game$", line)
            if joined:
                players.add(joined.group(1))
            elif left:
                players.discard(left.group(1))
    except OSError:
        pass
    return len(players)

def server_properties():
    values = {}
    public_keys = {"max-players", "view-distance", "simulation-distance"}
    try:
        for line in (SERVER_DIR / "server.properties").read_text(errors="replace").splitlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                if key in public_keys:
                    values[key] = value
    except OSError:
        pass
    return values

def public_status():
    result = response_state()
    result.pop("pid", None)
    mods, newest = client_mods()
    props = server_properties()
    inventory = {}
    try:
        inventory = json.loads(INVENTORY_FILE.read_text())
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    result.update({
        "onlinePlayers": online_player_count() if result["state"] == "running" else 0,
        "maxPlayers": int(props.get("max-players", "20")),
        "targetPlayers": 15,
        "minecraft": "1.21.1",
        "loader": "Fabric",
        "viewDistance": int(props.get("view-distance", "8")),
        "simulationDistance": int(props.get("simulation-distance", "5")),
        "modCount": len(mods),
        "mods": mods,
        "modsUpdatedAt": newest,
        "inventoryUpdatedAt": inventory.get("generatedAt"),
        "resourcePackCount": inventory.get("resourcePackCount", 0),
        "resourcePacks": inventory.get("resourcePacks", []),
        "activeResourcePacks": inventory.get("activeResourcePacks", []),
        "shaderPackCount": inventory.get("shaderPackCount", 0),
        "shaderPacks": inventory.get("shaderPacks", []),
        "activeShader": inventory.get("activeShader", ""),
        "shadersEnabled": inventory.get("shadersEnabled", False),
        "downloads": inventory.get("downloads", {}),
        "profiles": inventory.get("profiles", {}),
        "profileGeneratedAt": inventory.get("profileGeneratedAt"),
        "source": "Live from the server operator's active PollyMC 1.21.1 client",
    })
    return result

class Handler(BaseHTTPRequestHandler):
    server_version = "GoldcraftControl/1"
    def log_message(self, *_):
        return
    def send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)
    def send_download(self, requested):
        allowed = {
            "goldcraft-mods.zip",
            "goldcraft-active-resourcepacks.zip",
            "goldcraft-shaderpacks.zip",
            "goldcraft-client-files.zip",
            "goldcraft-profile-mobile-amethyst.zip",
            "goldcraft-profile-basic-laptop.zip",
            "goldcraft-profile-nice-laptop.zip",
        }
        if requested not in allowed:
            return self.send_json(404, {"error": "Download not found"})
        path = DOWNLOAD_DIR / requested
        if not path.is_file():
            return self.send_json(503, {"error": "Download package is still being prepared"})
        size = path.stat().st_size
        start, end, status = 0, size - 1, 200
        value = self.headers.get("Range", "")
        if value:
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", value)
            if not match:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            left, right = match.groups()
            if left:
                start = int(left)
                end = min(int(right), size - 1) if right else size - 1
            elif right:
                length = min(int(right), size)
                start, end = size - length, size - 1
            if start > end or start >= size:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            status = 206
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(length))
        self.send_header("Content-Disposition", f'attachment; filename="{requested}"')
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "public, max-age=300")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        try:
            with path.open("rb") as handle:
                handle.seek(start)
                remaining = length
                while remaining:
                    block = handle.read(min(1024 * 1024, remaining))
                    if not block:
                        break
                    self.wfile.write(block)
                    remaining -= len(block)
        except (BrokenPipeError, ConnectionResetError):
            pass
    def send_static(self, request_path):
        allowed = {
            "/": "index.html",
            "/index.html": "index.html",
            "/styles.css": "styles.css",
            "/app.js": "app.js",
            "/manifest.webmanifest": "manifest.webmanifest",
            "/sw.js": "sw.js",
            "/icon.svg": "icon.svg",
            "/404.html": "404.html",
        }
        filename = allowed.get(request_path)
        if filename is None:
            return False
        path = SITE_DIR / filename
        if not path.is_file():
            self.send_json(503, {"error": "Dashboard files are not installed"})
            return True
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix == ".webmanifest":
            content_type = "application/manifest+json"
        self.send_response(200)
        self.send_header("Content-Type", content_type + ("; charset=utf-8" if content_type.startswith("text/") or content_type.endswith("json") or content_type.endswith("javascript") else ""))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache" if path.suffix == ".html" else "public, max-age=300")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)
        return True
    def authorized(self):
        return hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + AUTH_VALUE)
    def do_GET(self):
        request_path = self.path.split("?", 1)[0]
        if self.send_static(request_path):
            return
        if request_path.startswith("/download/"):
            return self.send_download(request_path.removeprefix("/download/"))
        if request_path == "/public":
            with LOCK:
                return self.send_json(200, public_status())
        if not self.authorized():
            return self.send_json(401, {"error": "Unauthorized"})
        if request_path == "/status":
            with LOCK:
                return self.send_json(200, response_state("Status read from the actual Fabric server process."))
        if request_path == "/logs":
            match = re.search(r"(?:^|&)lines=(\d+)(?:&|$)", self.path.partition("?")[2])
            limit = max(25, min(500, int(match.group(1)) if match else 250))
            log_path = SERVER_DIR / "logs/latest.log"
            try:
                with log_path.open("rb") as handle:
                    handle.seek(0, os.SEEK_END)
                    size = handle.tell()
                    handle.seek(max(0, size - 256 * 1024))
                    raw = handle.read().decode("utf-8", errors="replace")
                lines = raw.splitlines()[-limit:]
                return self.send_json(200, {"lines": lines, "updatedAt": log_path.stat().st_mtime, "source": "Fabric logs/latest.log"})
            except OSError as error:
                return self.send_json(503, {"error": f"Could not read the Fabric log: {error}"})
        return self.send_json(404, {"error": "Not found"})
    def do_POST(self):
        global OWNED_PROCESS, STOP_REQUESTED
        if not self.authorized():
            return self.send_json(401, {"error": "Unauthorized"})
        if self.headers.get("Content-Length", "0") not in ("", "0"):
            return self.send_json(400, {"error": "Request body not accepted"})
        with LOCK:
            pid, _ = find_server()
            if self.path == "/start":
                if pid:
                    return self.send_json(409, response_state("The Fabric server is already running."))
                log = open(LOG_DIR / "server-console.log", "ab", buffering=0)
                try:
                    OWNED_PROCESS = subprocess.Popen(
                        START_COMMAND, cwd=SERVER_DIR, stdin=subprocess.PIPE,
                        stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                    )
                finally:
                    log.close()
                STOP_REQUESTED = False
                for _ in range(20):
                    time.sleep(0.25)
                    pid, _ = find_server()
                    if pid:
                        break
                return self.send_json(200, response_state("Started with the existing start.sh configuration."))
            if self.path == "/stop":
                if not pid:
                    STOP_REQUESTED = False
                    return self.send_json(200, response_state("The Fabric server is already stopped."))
                if OWNED_PROCESS is not None and OWNED_PROCESS.poll() is None and OWNED_PROCESS.stdin:
                    OWNED_PROCESS.stdin.write(b"stop\n")
                    OWNED_PROCESS.stdin.flush()
                    message = "Minecraft stop command sent; the world is saving."
                else:
                    os.kill(pid, signal.SIGTERM)
                    message = "Graceful SIGTERM sent to the existing Minecraft JVM; its shutdown hook is saving the world."
                STOP_REQUESTED = True
                return self.send_json(200, response_state(message))
            return self.send_json(404, {"error": "Not found"})

ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
