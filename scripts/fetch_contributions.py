#!/usr/bin/env python3
"""Fetch SeanL128's public contribution calendar (no token needed) and write
data/contributions.json. Stdlib only."""

import json
import pathlib
import re
import urllib.request

USER = "SeanL128"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "contributions.json"

url = f"https://github.com/users/{USER}/contributions"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode()
days = {}
for m in re.finditer(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html):
    days[m.group(1)] = int(m.group(2))
total_m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
if not days:
    raise SystemExit("no contribution cells parsed - GitHub markup may have changed")
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({"days": days, "total": total_m.group(1) if total_m else None}))
print(f"wrote contributions.json ({len(days)} days)")
