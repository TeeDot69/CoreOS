#!/usr/bin/env python3
from datetime import date

from core_settings import load_settings

fmt = load_settings().get("date_format", "ISO")
today = date.today()
if fmt == "US":
    print(today.strftime("%m/%d/%Y"))
elif fmt == "EU":
    print(today.strftime("%d/%m/%Y"))
else:
    print(today.isoformat())
