#!/usr/bin/env python3
"""Generate assets/header.svg (self-typing terminal) and assets/info-card.svg.
Pure stdlib. Animation is CSS keyframes inside each SVG; every element is
visible by default and keyframes only add the reveal (fill-mode: backwards),
so renderers that pause animations show the final frame instead of a blank
card. Palette mirrors seanlindsay.xyz: near-monochrome dark, muted
gray-green accent."""

import html
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"

BG = "#0d0d0c"
PANEL = "#151513"
BORDER = "#2a2926"
ACCENT = "#8a8f86"
INK = "#e8e6e1"
MUTED = "#7a7873"
BRIGHT = "#ffffff"
FONT = "ui-monospace, 'SF Mono', 'Cascadia Code', Menlo, Consolas, monospace"

CPS = 28  # typing speed, chars/sec

STYLE = """<style>
@keyframes appear { from { opacity: 0 } to { opacity: 1 } }
@keyframes blink { 0%,55% { opacity: 1 } 56%,100% { opacity: 0 } }
.ch { animation: appear 0.01s both }
.row { animation: appear 0.35s both }
@media (prefers-reduced-motion: reduce) { * { animation: none !important } }
</style>"""


def esc(s):
    return html.escape(s, quote=True)


def chrome(w, h, title):
    return (
        f'<rect width="{w}" height="{h}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
        f'<rect width="{w}" height="34" rx="12" fill="{PANEL}"/><rect y="22" width="{w}" height="12" fill="{PANEL}"/>'
        f'<circle cx="22" cy="17" r="5.5" fill="{BORDER}"/><circle cx="42" cy="17" r="5.5" fill="{BORDER}"/>'
        f'<circle cx="62" cy="17" r="5.5" fill="{ACCENT}"/>'
        f'<text x="{w//2}" y="21" font-size="12" fill="{MUTED}" text-anchor="middle">{esc(title)}</text>'
    )


def typed_line(x, y, prompt, text, start, fill=INK, size=15):
    """Static prompt, then per-char reveal. Chars are visible by default."""
    parts = []
    if prompt:
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{ACCENT}">{esc(prompt)}</text>')
    px = x + 9.1 * len(prompt)
    tspans = "".join(
        f'<tspan class="ch" style="animation-delay:{start + i / CPS:.2f}s">{esc(ch)}</tspan>'
        for i, ch in enumerate(text)
    )
    parts.append(
        f'<text x="{px:.0f}" y="{y}" font-size="{size}" fill="{fill}" xml:space="preserve">{tspans}</text>'
    )
    return "\n".join(parts), start + len(text) / CPS


def header_svg():
    w, h = 830, 190
    lines = []
    t = 0.4
    l1, t = typed_line(28, 74, "$ ", "whoami", t)
    lines.append(l1)
    l2, t = typed_line(28, 106, "", "Sean Lindsay", t + 0.35, fill=BRIGHT, size=26)
    lines.append(l2)
    l3, t = typed_line(28, 140, "> ", "I build agent tooling for Claude Code.", t + 0.3)
    lines.append(l3)
    l4, t = typed_line(28, 166, "> ", "plugins - orchestration - autonomous build pipelines", t + 0.15, fill=MUTED, size=13)
    lines.append(l4)
    cursor = (
        f'<rect x="{28 + 8.0 * 54:.0f}" y="154" width="8" height="15" fill="{ACCENT}" '
        f'style="animation: blink 1.1s {t + 0.4:.2f}s infinite backwards"/>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="{FONT}" role="img" aria-label="Sean Lindsay - I build agent tooling for Claude Code">'
        f'{STYLE}{chrome(w, h, "sean@github: ~")}' + "\n".join(lines) + cursor + "</svg>"
    )


def info_card_svg():
    w, h = 410, 266
    rows = [
        ("role", "AI agent tooling engineer"),
        ("open to", "agent infra / dev-tools work"),
        ("building", "alloyd, nightcrew, autodev"),
        ("plugins", "deslop, shush, blueprint-forge"),
        ("stack", "Python, TypeScript, Swift"),
        ("web", "seanlindsay.xyz"),
        ("mail", "seanlindsay2008@gmail.com"),
    ]
    t = 0.5
    body = [
        f'<text x="24" y="58" font-size="14" fill="{BRIGHT}" font-weight="bold">SeanL128@github</text>',
        f'<text x="24" y="74" font-size="12" fill="{MUTED}">{"-" * 24}</text>',
    ]
    for i, (k, v) in enumerate(rows):
        body.append(
            f'<g class="row" style="animation-delay:{t + i * 0.14:.2f}s">'
            f'<text x="24" y="{98 + i * 21}" font-size="13.5" fill="{ACCENT}">{esc(k)}</text>'
            f'<text x="116" y="{98 + i * 21}" font-size="13.5" fill="{INK}">{esc(v)}</text></g>'
        )
    sw = "".join(
        f'<rect x="{24 + i * 22}" y="{h - 24}" width="16" height="9" rx="2" fill="{c}"/>'
        for i, c in enumerate(["#1d1d1b", "#383934", "#5c5f58", "#7a7873", "#8a8f86", "#c9cdc4", "#e8e6e1"])
    )
    body.append(f'<g class="row" style="animation-delay:{t + len(rows) * 0.14 + 0.2:.2f}s">{sw}</g>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="{FONT}" role="img" aria-label="Profile info card">'
        f'{STYLE}{chrome(w, h, "SeanL128")}' + "".join(body) + "</svg>"
    )


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header_svg())
    (OUT / "info-card.svg").write_text(info_card_svg())
    print("wrote header.svg, info-card.svg")
