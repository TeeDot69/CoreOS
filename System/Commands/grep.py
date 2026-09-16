#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: grep <pattern> <file>")
    sys.exit(1)

pattern = sys.argv[1]
path = Path(sys.argv[2])
if not path.is_absolute():
    path = Path(os.getenv("PWD", ".")) / path
path = path.resolve()

if not path.exists() or not path.is_file():
    print("File not found")
    sys.exit(1)

for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
    if pattern in line:
        print(line)
