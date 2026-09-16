#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from core_settings import load_settings

if len(sys.argv) != 2:
    print("Usage: rm <file>")
    sys.exit(1)

path = Path(sys.argv[1])
if not path.is_absolute():
    path = Path(os.getenv("PWD", ".")) / path
path = path.resolve()

if path.exists() and path.is_file():
    if load_settings().get("confirm_delete", True):
        answer = input(f"Delete {path.name}? (y/N): ").strip().lower()
        if answer not in ("y", "yes"):
            print("Cancelled.")
            sys.exit(0)
    path.unlink()
else:
    print("File not found")
