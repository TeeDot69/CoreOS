#!/usr/bin/env python3
import os

print("=== CoreOS Environment Variables ===")
coreos_vars = {k: v for k, v in os.environ.items() if k.startswith("COREOS_")}
if coreos_vars:
    for key in sorted(coreos_vars.keys()):
        print(f"{key}={coreos_vars[key]}")
else:
    print("No CoreOS environment variables set")
