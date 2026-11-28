#!/usr/bin/env python3
"""Static security checks for the Goldcraft same-origin dashboard."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


failures: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


app = read("site/app.js")
index = read("site/index.html")
worker = read("site/sw.js")
bridge = read("automation/bridge.py")

private_host = re.compile(r"\.ts\.net", re.IGNORECASE)
home_path = re.compile(r"/home/[A-Za-z0-9._-]+")
for relative, content in (
    ("site/app.js", app),
    ("site/index.html", index),
    ("site/styles.css", read("site/styles.css")),
    ("site/sw.js", worker),
    ("automation/bridge.py", bridge),
    ("README.md", read("README.md")),
    ("docs/joining.md", read("docs/joining.md")),
):
    require(not private_host.search(content), f"{relative}: private tunnel hostname detected")
    require(not home_path.search(content), f"{relative}: account-specific absolute home path detected")

csp = re.search(r'http-equiv="Content-Security-Policy"\s+content="([^"]+)"', index)
require(csp is not None, "index.html: CSP meta policy missing")
if csp:
    require("connect-src 'self'" in csp.group(1), "index.html: API must be same-origin")
    require(re.search(r"connect-src[^;]*https?://", csp.group(1)) is None,
            "index.html: external API origin remains in CSP")

require(re.search(r'const API_BASE = (""|window\.location\.origin);', app) is not None,
        "app.js: API base must remain same-origin")
require('adminRequest("/logs?lines=400")' in app, "app.js: owner console log request missing")

download_block = bridge.split("    def send_download(self, requested):", 1)[1].split("    def send_static", 1)[0]
bridge_downloads = set(re.findall(r'"(goldcraft-[^"]+\.zip)"', download_block))
app_downloads = set(re.findall(r'"/download/(goldcraft-[^"]+\.zip)"', app))
require(bridge_downloads == app_downloads,
        "app.js: browser download allowlist must match the bridge allowlist")
require("function safeDownloadUrl(value)" in app,
        "app.js: download URLs must pass the same-origin allowlist")
require("url.origin !== window.location.origin" in app and "!DOWNLOAD_PATHS.has(url.pathname)" in app,
        "app.js: download URL validation must reject external and unlisted paths")
require("link.href = downloadUrl;" in app and "link.href = API_BASE + item.url" not in app and "link.href = API_BASE + profile.url" not in app,
        "app.js: untrusted inventory URLs must not be assigned directly to links")
require('aria-keyshortcuts="Control+Alt+B"' in index and "event.repeat" in app,
        "dashboard: document the Ctrl+Alt+B fallback and ignore key-repeat toggles")
require("consoleStopButton" in app and "window.confirm(" in app,
        "app.js: graceful-stop confirmation missing")
require("innerHTML" not in app, "app.js: do not inject untrusted log text as HTML")

require('const CACHE = "goldcraft-dashboard-v5"' in worker,
        "sw.js: cache version must invalidate the old dynamic cache")
require("const STATIC_URLS = new Set(" in worker, "sw.js: exact static asset allowlist missing")
require("!STATIC_URLS.has(url.href)" in worker,
        "sw.js: non-static same-origin requests must bypass Cache Storage")
require("cache.put(request, response.clone())" in worker,
        "sw.js: static response caching missing")

require('ThreadingHTTPServer(("127.0.0.1", 8765)' in bridge,
        "bridge.py: listener must remain loopback-only")
require("Access-Control-Allow-Origin" not in bridge,
        "bridge.py: same-origin API must not enable wildcard CORS")
require("def do_OPTIONS" not in bridge,
        "bridge.py: CORS preflight handler should not be present")
require("def authorized(self):" in bridge, "bridge.py: bearer authorization helper missing")
do_get = bridge.split("    def do_GET(self):", 1)[1].split("    def do_POST(self):", 1)[0]
auth_at = do_get.find("if not self.authorized():")
logs_at = do_get.find('if request_path == "/logs":')
require(auth_at >= 0 and logs_at > auth_at,
        "bridge.py: /logs must remain behind bearer authorization")
public_status = bridge.split("def public_status():", 1)[1].split("class Handler", 1)[0]
require('result.pop("pid", None)' in public_status,
        "bridge.py: public status must omit process PID")
require('"port":' not in public_status,
        "bridge.py: public status must omit the server port")
require('self.send_header("Content-Security-Policy"' in bridge,
        "bridge.py: static responses need a CSP header")

if failures:
    for failure in failures:
        print(f"FAIL: {failure}")
    sys.exit(1)
print("Dashboard security checks passed.")
