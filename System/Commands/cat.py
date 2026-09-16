#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: cat <file>")
    sys.exit(1)

path = Path(sys.argv[1])
if not path.is_absolute():
    path = Path(os.getenv("PWD", ".")) / path
path = path.resolve()

if path.exists() and path.is_file():
    print(path.read_text(encoding="utf-8", errors="ignore"))
else:
    print("File not found")
