#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from core_settings import load_settings
from pathutils import display_path

target = Path(os.getenv("PWD", "."))
if len(sys.argv) > 1:
    target = Path(sys.argv[1])
    if not target.is_absolute():
        target = Path(os.getenv("PWD", ".")) / target
    target = target.resolve()

if target.exists() and target.is_dir():
    sett = load_settings()
    show_hidden = bool(sett.get("show_hidden_files", False))
    dirs_first = bool(sett.get("list_directories_first", True))

    entries = sorted(target.iterdir(), key=lambda p: p.name.lower())
    if not show_hidden:
        entries = [e for e in entries if not e.name.startswith(".")]

    if dirs_first:
        dirs = [e.name + "/" for e in entries if e.is_dir()]
        files = [e.name for e in entries if not e.is_dir()]
        names = dirs + files
    else:
        names = [e.name + "/" if e.is_dir() else e.name for e in entries]

    print(display_path(target))
    for name in names:
        print(name)
else:
    print("Directory not found")
