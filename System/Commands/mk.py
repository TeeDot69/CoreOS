#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: mk <filename>")
    sys.exit(1)

path = Path(sys.argv[1])
if not path.is_absolute():
    path = Path(os.getenv("PWD", ".")) / path
path = path.resolve()

path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("", encoding="utf-8")
