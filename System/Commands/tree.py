#!/usr/bin/env python3
import os
import sys
from pathlib import Path

path = Path(os.getenv("PWD", "."))
if len(sys.argv) > 1:
    path = Path(sys.argv[1])
    if not path.is_absolute():
        path = Path(os.getenv("PWD", ".")) / path
    path = path.resolve()

if not path.exists():
    print("Path not found")
    sys.exit(1)

for root, dirs, files in os.walk(path):
    level = root.replace(str(path), "").count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{Path(root).name}/")
    for file in files:
        print(f"{indent}  {file}")
