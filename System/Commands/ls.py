#!/usr/bin/env python3
import os
import sys
from pathlib import Path

target = Path(os.getenv("PWD", "."))
if len(sys.argv) > 1:
    target = Path(sys.argv[1])
    if not target.is_absolute():
        target = Path(os.getenv("PWD", ".")) / target
    target = target.resolve()

if target.exists() and target.is_dir():
    for item in sorted(target.iterdir()):
        print(item.name)
else:
    print("Directory not found")
