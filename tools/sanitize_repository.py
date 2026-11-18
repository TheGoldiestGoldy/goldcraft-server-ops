#!/usr/bin/env python3
"""Remove machine-specific paths and obvious secret assignments from text assets."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
TEXT_SUFFIXES = {
    ".cfg", ".conf", ".csv", ".json", ".log", ".md", ".properties",
    ".service", ".timer", ".toml", ".txt", ".yaml", ".yml",
}
PATH_PATTERNS = (
    (re.compile(r"/home/[^/\\s\"']+"), "<HOME>"),
    (re.compile(r"C:\\\\Users\\\\[^\\\\\s\"']+", re.IGNORECASE), "%USERPROFILE%"),
    (re.compile(r"/run/media/[^/\\s\"']+/[^/\\s\"']+"), "<EXTERNAL_DRIVE>"),
)
SECRET_ASSIGNMENT = re.compile(
    r"(?im)^(\s*(?:token|password|secret|api[_-]?key)\s*[:=]\s*).+$"
)

changed = 0
for path in ROOT.rglob("*"):
    if (
        path == SELF
        or not path.is_file()
        or ".git" in path.parts
        or path.suffix.lower() not in TEXT_SUFFIXES
    ):
        continue
    try:
        source = path.read_text()
    except (OSError, UnicodeDecodeError):
        continue
    updated = source
    for pattern, replacement in PATH_PATTERNS:
        updated = pattern.sub(replacement, updated)
    updated = SECRET_ASSIGNMENT.sub(r"\1[redacted]", updated)
    if updated != source:
        path.write_text(updated)
        changed += 1

print(f"sanitized_files={changed}")
