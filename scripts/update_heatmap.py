#!/usr/bin/env python3
"""Fetch SeanL128's public contribution calendar (no token needed) and render
assets/heatmap.svg: 53x7 grid, amber phosphor ramp, one-shot diagonal reveal.
Stdlib only, so the daily Action needs nothing but Python."""

import datetime
import pathlib
import re
import urllib.request

USER = "SeanL128"
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "heatmap.svg"

BG = "#100c08"
BORDER = "#3a2c14"
MUTED = "#8a7a5f"
INK = "#e8dcc8"
FONT = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
RAMP = ["#221a10", "#4a3210", "#8a5a24", "#c98a3d", "#ffb454"]  # level 0-4

CELL, GAP, PAD = 11, 3, 24


def fetch():
    url = f"https://github.com/users/{USER}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    days = {}  # date -> level
    for m in re.finditer(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html):
        days[m.group(1)] = int(m.group(2))
    total_m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html)
    total = total_m.group(1) if total_m else None
    if not days:
        raise SystemExit("no contribution cells parsed - GitHub markup may have changed")
    return days, total


def render(days, total):
    dates = sorted(days)
    first = datetime.date.fromisoformat(dates[0])
    # column = week index, row = weekday (Sun=0 like GitHub)
    def pos(d):
        delta = (d - first).days + (first.weekday() + 1) % 7
        return delta // 7, delta % 7

    cells, max_col = [], 0
    for ds in dates:
        d = datetime.date.fromisoformat(ds)
        col, row = pos(d)
        max_col = max(max_col, col)
        x = PAD + col * (CELL + GAP)
        y = 40 + row * (CELL + GAP)
        delay = (col + row) * 0.018
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{RAMP[days[ds]]}" class="c" style="animation-delay:{delay:.3f}s"/>'
        )
    w = PAD * 2 + (max_col + 1) * (CELL + GAP) - GAP
    h = 40 + 7 * (CELL + GAP) + 40
    lx = w - PAD - 34 - 5 * (CELL + GAP)  # legend cells, leaving room for "more"
    legend = "".join(
        f'<rect x="{lx + i*(CELL+GAP)}" y="{h-30}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(RAMP)
    )
    footer = (f'<text x="{PAD}" y="{h-20}" font-size="12" fill="{MUTED}">'
              f'{total} contributions in the last year</text>') if total else ""
    updated = datetime.date.today().isoformat()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}" role="img" aria-label="Contribution calendar">
<style>
@keyframes appear {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
.c {{ animation: appear 0.3s backwards }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect width="{w}" height="{h}" rx="12" fill="{BG}" stroke="{BORDER}"/>
<text x="{PAD}" y="26" font-size="13" fill="{INK}">$ git log --graph  <tspan fill="{MUTED}">(updated {updated})</tspan></text>
{"".join(cells)}
<text x="{lx - 32}" y="{h-21}" font-size="11" fill="{MUTED}">less</text>
{legend}
<text x="{lx + 5*(CELL+GAP) + 4}" y="{h-21}" font-size="11" fill="{MUTED}">more</text>
{footer}
</svg>"""


if __name__ == "__main__":
    days, total = fetch()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(days, total))
    print(f"wrote heatmap.svg ({len(days)} days, total={total})")
