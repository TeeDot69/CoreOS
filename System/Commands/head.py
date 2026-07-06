#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: head <file>")
    sys.exit(1)

path = Path(sys.argv[1])
if not path.is_absolute():
    path = Path(os.getenv("PWD", ".")) / path
path = path.resolve()

if not path.exists() or not path.is_file():
    print("File not found")
    sys.exit(1)

lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
for line in lines[:10]:
    print(line)
