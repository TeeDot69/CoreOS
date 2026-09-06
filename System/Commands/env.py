#!/usr/bin/env python3
import os
from pathlib import Path

from pathutils import display_path

# Environment variables that hold filesystem paths.  These are displayed
# relative to the CoreOS root so the host absolute path is never revealed.
PATH_VARS = {"COREOS_HOME", "COREOS_ROOT", "PWD"}

print("=== CoreOS Environment Variables ===")
coreos_vars = {k: v for k, v in os.environ.items() if k.startswith("COREOS_")}
if coreos_vars:
    for key in sorted(coreos_vars.keys()):
        value = coreos_vars[key]
        if key in PATH_VARS and value:
            value = display_path(Path(value))
        print(f"{key}={value}")
else:
    print("No CoreOS environment variables set")
