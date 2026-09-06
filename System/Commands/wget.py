#!/usr/bin/env python3
import sys
import urllib.request
import os
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: wget <url> [destination]")
    sys.exit(1)

url = sys.argv[1]
home = Path(os.getenv("COREOS_HOME", "."))
downloads_dir = home / "Downloads"
downloads_dir.mkdir(exist_ok=True)

# Destination: specified as arg2 or default to Downloads
if len(sys.argv) > 2:
    dest_path = Path(sys.argv[2])
    if not dest_path.is_absolute():
        dest_path = Path(os.getenv("PWD", ".")) / dest_path
else:
    filename = url.split("/")[-1] or "download"
    dest_path = downloads_dir / filename

try:
    response = urllib.request.urlopen(url)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(response.read())
    # Show relative path from COREOS_ROOT if possible
    coreos_root = Path(os.getenv("COREOS_ROOT", "."))
    try:
        display_path = dest_path.relative_to(coreos_root)
    except ValueError:
        display_path = dest_path
    print(f"Downloaded to: {display_path}")
except Exception as exc:
    print(f"Download failed: {exc}")
