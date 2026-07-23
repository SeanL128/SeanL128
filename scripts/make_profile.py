#!/usr/bin/env python3
"""Render assets/profile.svg: the whole profile as ONE terminal window —
typing header, status/contact, robot pipeline, contribution graph, project
listing. Pure stdlib; reads data/contributions.json (run
fetch_contributions.py first). All animation is CSS keyframes; everything is
visible by default so paused renderers show the finished frame. Palette
mirrors seanlindsay.xyz."""

import datetime
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "profile.svg"

BG = "#0d0d0c"
PANEL = "#151513"
BORDER = "#2a2926"
ACCENT = "#8a8f86"
INK = "#e8e6e1"
MUTED = "#7a7873"
BRIGHT = "#ffffff"
FONT = "ui-monospace, 'SF Mono', 'Cascadia Code', Menlo, Consolas, monospace"
RAMP = ["#1d1d1b", "#383934", "#5c5f58", "#8a8f86", "#e8e6e1"]

W = 830
X0 = 30
CPS = 55  # typing chars/sec


def esc(s):
    return html.escape(s, quote=True)


def typed_line(y, prompt, text, start, fill=INK, size=14):
    parts = []
    if prompt:
        parts.append(f'<text x="{X0}" y="{y}" font-size="{size}" fill="{ACCENT}">{esc(prompt)}</text>')
    px = X0 + 8.5 * len(prompt)
    tspans = "".join(
        f'<tspan class="ch" style="animation-delay:{start + i / CPS:.2f}s">{esc(ch)}</tspan>'
        for i, ch in enumerate(text)
    )
    parts.append(f'<text x="{px:.0f}" y="{y}" font-size="{size}" fill="{fill}" xml:space="preserve">{tspans}</text>')
    return "".join(parts), start + len(text) / CPS


def fade_group(inner, start):
    return f'<g class="row" style="animation-delay:{start:.2f}s">{inner}</g>'


def robot(x, y, label, delay):
    return f"""<g transform="translate({x},{y})"><g style="animation: bob 2.6s ease-in-out {delay}s infinite alternate">
<line x1="18" y1="-34" x2="18" y2="-42" stroke="{MUTED}" stroke-width="2"/>
<circle cx="18" cy="-44" r="3" fill="{ACCENT}"/>
<rect x="2" y="-34" width="32" height="24" rx="5" fill="{PANEL}" stroke="{ACCENT}" stroke-width="1.5"/>
<circle cx="12" cy="-22" r="2.6" fill="{INK}" style="animation: blinkeye 4.7s linear {delay + 1:.1f}s infinite"/>
<circle cx="24" cy="-22" r="2.6" fill="{INK}" style="animation: blinkeye 4.7s linear {delay + 1:.1f}s infinite"/>
<rect x="6" y="-8" width="24" height="20" rx="4" fill="{PANEL}" stroke="{MUTED}" stroke-width="1.5"/>
<line x1="6" y1="2" x2="-4" y2="8" stroke="{MUTED}" stroke-width="2" stroke-linecap="round"/>
<line x1="30" y1="2" x2="40" y2="8" stroke="{MUTED}" stroke-width="2" stroke-linecap="round"/>
</g><text x="18" y="28" font-size="11" fill="{MUTED}" text-anchor="middle">{label}</text>
</g>"""


def robots_scene(y0, start):
    """Robot assembly line, positioned relative to y0. ~200px tall."""
    CYC = 9
    ry = y0 + 108
    bots = robot(150, ry, "plan", 0) + robot(370, ry, "build", 0.9) + robot(590, ry, "verify", 1.7)
    desk = f'<line x1="{X0}" y1="{ry + 14}" x2="{W - X0}" y2="{ry + 14}" stroke="{BORDER}" stroke-width="2"/>'
    paper_lines = "".join(
        f'<line x1="3" y1="{4 + i * 3.5}" x2="15" y2="{4 + i * 3.5}" stroke="{MUTED}" stroke-width="1.2" '
        f'opacity="0" style="animation: ink{i} {CYC}s linear {start + 0.5:.2f}s infinite"/>'
        for i in range(4)
    )
    stamp = (f'<text x="9" y="14" font-size="9" fill="{ACCENT}" text-anchor="middle" opacity="0" '
             f'style="animation: stampin {CYC}s linear {start + 0.5:.2f}s infinite">✓</text>')
    paper = (f'<g opacity="0" style="animation: carry {CYC}s ease-in-out {start + 0.5:.2f}s infinite">'
             f'<rect x="0" y="0" width="18" height="20" rx="2" fill="{BG}" stroke="{INK}" stroke-width="1.3"/>'
             f'{paper_lines}{stamp}</g>')
    prslot = (f'<g style="animation: prglow {CYC}s linear {start + 0.5:.2f}s infinite">'
              f'<text x="{W - 120}" y="{y0 + 30}" font-size="13" fill="{INK}" xml:space="preserve">PR ✓</text>'
              f'<text x="{W - 128}" y="{y0 + 47}" font-size="10" fill="{MUTED}">merged</text></g>')
    # keyframes for carry are y0-dependent, so emit them here
    py = ry - 8
    kf = f"""@keyframes carry {{
  0%   {{ transform: translate({X0}px, {py}px); opacity: 0 }}
  4%   {{ transform: translate({X0}px, {py}px); opacity: 1 }}
  16%  {{ transform: translate(141px, {py}px) }}
  30%  {{ transform: translate(141px, {py}px) }}
  42%  {{ transform: translate(361px, {py}px) }}
  56%  {{ transform: translate(361px, {py}px) }}
  68%  {{ transform: translate(581px, {py}px) }}
  82%  {{ transform: translate(581px, {py}px) }}
  94%  {{ transform: translate({W - 124}px, {y0 + 18}px); opacity: 1 }}
  96%, 100% {{ transform: translate({W - 124}px, {y0 + 18}px); opacity: 0 }}
}}"""
    return fade_group(desk + bots + prslot, start) + paper, kf


def heatmap(y0, start):
    """53x7 contribution grid from data/contributions.json. ~140px tall."""
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days, total = data["days"], data["total"]
    CELL, GAP = 11, 3
    dates = sorted(days)
    first = datetime.date.fromisoformat(dates[0])
    off = (first.weekday() + 1) % 7
    cells = []
    for ds in dates:
        d = datetime.date.fromisoformat(ds)
        delta = (d - first).days + off
        col, row = delta // 7, delta % 7
        x = X0 + col * (CELL + GAP)
        y = y0 + row * (CELL + GAP)
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{RAMP[days[ds]]}" '
            f'class="c" style="animation-delay:{start + (col + row) * 0.012:.3f}s"/>'
        )
    gh = 7 * (CELL + GAP)
    lx = W - X0 - 34 - 5 * (CELL + GAP)
    legend = "".join(
        f'<rect x="{lx + i * (CELL + GAP)}" y="{y0 + gh + 8}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(RAMP)
    )
    footer = (
        f'<text x="{X0}" y="{y0 + gh + 18}" font-size="12" fill="{MUTED}">{total} contributions in the last year</text>'
        f'<text x="{lx - 32}" y="{y0 + gh + 17}" font-size="11" fill="{MUTED}">less</text>{legend}'
        f'<text x="{lx + 5 * (CELL + GAP) + 4}" y="{y0 + gh + 17}" font-size="11" fill="{MUTED}">more</text>'
    )
    return "".join(cells) + fade_group(footer, start + 0.9)


def build():
    body = []
    kf_extra = ""
    t = 0.4

    # ── $ whoami ──────────────────────────────────────────────
    ln, t = typed_line(64, "$ ", "whoami", t)
    body.append(ln)
    ln, t = typed_line(98, "", "Sean Lindsay", t + 0.15, fill=BRIGHT, size=27)
    body.append(ln)
    ln, t = typed_line(128, "> ", "I build agent tooling for Claude Code.", t + 0.12)
    body.append(ln)

    # ── $ status ──────────────────────────────────────────────
    ln, t = typed_line(172, "$ ", "status", t + 0.25)
    body.append(ln)
    body.append(fade_group(
        f'<text x="{X0}" y="196" font-size="13" fill="{INK}">open to <tspan fill="{BRIGHT}">agent-infrastructure / developer-tools</tspan> work</text>'
        f'<text x="{X0}" y="216" font-size="13" fill="{MUTED}">mail seanlindsay2008@gmail.com · web seanlindsay.xyz</text>', t + 0.1))
    t += 0.3

    # ── $ nightcrew run (robots) ──────────────────────────────
    ln, t = typed_line(258, "$ ", "nightcrew run", t + 0.2)
    body.append(ln)
    scene, kf = robots_scene(270, t + 0.2)
    body.append(scene)
    kf_extra += kf
    body.append(fade_group(
        f'<text x="{X0}" y="446" font-size="12" fill="{MUTED}">spec → plan → build → verify → PR · alloyd routes each task · no PR ships unverified</text>', t + 0.15))
    t += 0.5

    # ── $ git log --graph (heatmap) ───────────────────────────
    ln, t = typed_line(492, "$ ", "git log --graph", t + 0.15)
    updated = datetime.date.today().isoformat()
    body.append(ln)
    body.append(fade_group(
        f'<text x="{X0 + 150}" y="492" font-size="12" fill="{MUTED}">(refreshes daily · {updated})</text>', t))
    body.append(heatmap(510, t + 0.1))
    t += 0.7

    # ── $ ls ~/projects ───────────────────────────────────────
    ln, t = typed_line(668, "$ ", "ls ~/projects", t + 0.15)
    body.append(ln)
    projects = [
        ("alloyd/", "local router load-balancing one workload across Claude + ChatGPT subscriptions"),
        ("nightcrew/", "spec-to-PR build agent — no PR ships unverified"),
        ("deslop/", "Claude Code plugin that strips AI-isms from prose"),
        ("shush/", "Claude Code plugin that cuts verbosity without losing substance"),
    ]
    for i, (name, desc) in enumerate(projects):
        y = 694 + i * 22
        body.append(fade_group(
            f'<text x="{X0}" y="{y}" font-size="13" fill="{BRIGHT}" font-weight="bold">{esc(name)}</text>'
            f'<text x="{X0 + 110}" y="{y}" font-size="12.5" fill="{INK}">{esc(desc)}</text>', t + 0.08 * i))
    t += 0.4

    # blinking cursor on final prompt line
    ln, t2 = typed_line(806, "$ ", "", t + 0.2)
    body.append(ln)
    body.append(f'<rect x="{X0 + 17}" y="794" width="8" height="15" fill="{ACCENT}" '
                f'style="animation: blink 1.1s {t + 0.3:.2f}s infinite backwards"/>')

    H = 830
    chrome = (
        f'<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
        f'<rect width="{W}" height="36" rx="12" fill="{PANEL}"/><rect y="24" width="{W}" height="12" fill="{PANEL}"/>'
        f'<circle cx="24" cy="18" r="5.5" fill="{BORDER}"/><circle cx="44" cy="18" r="5.5" fill="{BORDER}"/>'
        f'<circle cx="64" cy="18" r="5.5" fill="{ACCENT}"/>'
        f'<text x="{W // 2}" y="22" font-size="12" fill="{MUTED}" text-anchor="middle">sean@github: ~</text>'
    )
    style = f"""<style>
@keyframes appear {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
@keyframes blink {{ 0%,55% {{ opacity: 1 }} 56%,100% {{ opacity: 0 }} }}
@keyframes bob {{ from {{ transform: translateY(0) }} to {{ transform: translateY(-3px) }} }}
@keyframes blinkeye {{ 0%, 91%, 100% {{ opacity: 1 }} 93%, 96% {{ opacity: 0.15 }} }}
@keyframes ink0 {{ 0%, 18% {{ opacity: 0 }} 24%, 100% {{ opacity: 1 }} }}
@keyframes ink1 {{ 0%, 22% {{ opacity: 0 }} 28%, 100% {{ opacity: 1 }} }}
@keyframes ink2 {{ 0%, 44% {{ opacity: 0 }} 50%, 100% {{ opacity: 1 }} }}
@keyframes ink3 {{ 0%, 48% {{ opacity: 0 }} 54%, 100% {{ opacity: 1 }} }}
@keyframes stampin {{ 0%, 70% {{ opacity: 0 }} 76%, 100% {{ opacity: 1 }} }}
@keyframes prglow {{ 0%, 88% {{ opacity: 0.45 }} 94%, 100% {{ opacity: 1 }} }}
{kf_extra}
.ch {{ animation: appear 0.01s both }}
.row {{ animation: appear 0.4s both }}
.c {{ animation: appear 0.3s backwards }}
text {{ font-family: {FONT} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important }} }}
</style>"""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="{FONT}" role="img" aria-label="Sean Lindsay - terminal profile: status, pipeline robots, contributions, projects">'
        f'{style}{chrome}' + "".join(body) + "</svg>"
    )


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(build())
    print("wrote profile.svg")
