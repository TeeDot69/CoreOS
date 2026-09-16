#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: mkdir <directory>")
    sys.exit(1)

path = Path(sys.argv[1])
if not path.is_absolute():
    path = Path(os.getenv("PWD", ".")) / path
path = path.resolve()

path.mkdir(parents=True, exist_ok=True)
