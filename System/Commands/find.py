#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from pathutils import display_path

target = Path(os.getenv("PWD", "."))
if len(sys.argv) > 1:
    target = Path(sys.argv[1])
    if not target.is_absolute():
        target = Path(os.getenv("PWD", ".")) / target
    target = target.resolve()

if not target.exists():
    print("Path not found")
    sys.exit(1)

for root, dirs, files in os.walk(target):
    for name in dirs + files:
        print(display_path(Path(os.path.join(root, name))))
