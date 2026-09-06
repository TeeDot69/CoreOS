#!/usr/bin/env python3
import os
from pathlib import Path

from pathutils import display_path

print(display_path(Path(os.getenv("PWD", "."))))
