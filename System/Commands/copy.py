#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: copy <source> <destination>")
    sys.exit(1)

src = Path(sys.argv[1])
if not src.is_absolute():
    src = Path(os.getenv("PWD", ".")) / src
src = src.resolve()

dst = Path(sys.argv[2])
if not dst.is_absolute():
    dst = Path(os.getenv("PWD", ".")) / dst
dst = dst.resolve()

if not src.exists():
    print("Source not found")
elif src.is_dir():
    print("Use copy on files only")
else:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
