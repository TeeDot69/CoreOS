#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: rmdir <directory>")
    sys.exit(1)

path = Path(sys.argv[1])
if not path.is_absolute():
    path = Path(os.getenv("PWD", ".")) / path
path = path.resolve()

if path.exists() and path.is_dir():
    try:
        path.rmdir()
    except OSError:
        print("Directory not empty")
else:
    print("Directory not found")
