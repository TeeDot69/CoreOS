#!/usr/bin/env python3
import os
from pathlib import Path

programs_dir = Path(os.getenv("COREOS_ROOT", ".")) / "Programs"

print("=== Available Programs ===")
if programs_dir.exists():
    programs = sorted([f.stem for f in programs_dir.glob("*.py") if f.is_file()])
    if programs:
        for i, prog in enumerate(programs, 1):
            print(f"{i}. {prog}")
    else:
        print("No programs found")
else:
    print(f"Programs directory not found: {programs_dir}")

print("\nUsage: <program_name> [args]")
print("Example: calculator")
