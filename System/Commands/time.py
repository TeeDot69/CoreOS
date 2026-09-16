#!/usr/bin/env python3
from datetime import datetime

from core_settings import load_settings

fmt = load_settings().get("time_format", "24h")
now = datetime.now()
if fmt == "12h":
    print(now.strftime("%I:%M:%S %p"))
else:
    print(now.strftime("%H:%M:%S"))
