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
        ("plugins", "deslop, shush"),
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


def pipeline_svg():
    """Three little robots pass a spec sheet down the line: plan writes on it,
    build adds to it, verify stamps it, and it exits as a merged PR. Loops.
    All motion is CSS keyframes; a paused renderer shows the full scene."""
    w, h = 410, 266
    CYC = 9  # seconds per loop

    def robot(x, y, label, delay):
        # simple geometric bot: antenna, head with eyes, body, two arms
        return f"""<g transform="translate({x},{y})"><g style="animation: bob 2.6s ease-in-out {delay}s infinite alternate">
<line x1="18" y1="-34" x2="18" y2="-42" stroke="{MUTED}" stroke-width="2"/>
<circle cx="18" cy="-44" r="3" fill="{ACCENT}"/>
<rect x="2" y="-34" width="32" height="24" rx="5" fill="{PANEL}" stroke="{ACCENT}" stroke-width="1.5"/>
<circle cx="12" cy="-22" r="2.6" fill="{INK}" style="animation: blinkeye 4.7s linear {delay + 1:.1f}s infinite"/>
<circle cx="24" cy="-22" r="2.6" fill="{INK}" style="animation: blinkeye 4.7s linear {delay + 1:.1f}s infinite"/>
<rect x="6" y="-8" width="24" height="20" rx="4" fill="{PANEL}" stroke="{MUTED}" stroke-width="1.5"/>
<line x1="6" y1="2" x2="-4" y2="8" stroke="{MUTED}" stroke-width="2" stroke-linecap="round"/>
<line x1="30" y1="2" x2="40" y2="8" stroke="{MUTED}" stroke-width="2" stroke-linecap="round"/>
</g><text x="18" y="28" font-size="10.5" fill="{MUTED}" text-anchor="middle">{label}</text>
</g>"""

    bots = robot(64, 150, "plan", 0) + robot(178, 150, "build", 0.9) + robot(292, 150, "verify", 1.7)

    # desk line the paper slides along
    desk = f'<line x1="24" y1="164" x2="386" y2="164" stroke="{BORDER}" stroke-width="2"/>'

    # the paper: a small sheet that gains lines at each station, then exits up-right
    paper_lines = "".join(
        f'<line x1="3" y1="{4 + i * 3.5}" x2="15" y2="{4 + i * 3.5}" stroke="{MUTED}" stroke-width="1.2" '
        f'opacity="0" style="animation: ink{i} {CYC}s linear infinite"/>'
        for i in range(4)
    )
    stamp = (f'<text x="9" y="14" font-size="9" fill="{ACCENT}" text-anchor="middle" opacity="0" '
             f'style="animation: stampin {CYC}s linear infinite">\u2713</text>')
    paper = (f'<g style="animation: carry {CYC}s ease-in-out infinite">'
             f'<rect x="0" y="0" width="18" height="20" rx="2" fill="{BG}" stroke="{INK}" stroke-width="1.3"/>'
             f'{paper_lines}{stamp}</g>')

    # PR slot, top right; lights up when the paper lands
    prslot = (f'<g style="animation: prglow {CYC}s linear infinite">'
              f'<text x="352" y="70" font-size="12" fill="{INK}" xml:space="preserve">PR \u2713</text>'
              f'<text x="342" y="86" font-size="9.5" fill="{MUTED}">merged</text></g>')

    caption = (f'<text x="24" y="240" font-size="10.5" fill="{MUTED}">'
               f'spec \u2192 plan \u2192 build \u2192 verify \u2192 PR \u00b7 no PR ships unverified</text>')

    style = f"""<style>
@keyframes bob {{ from {{ transform: translateY(0) }} to {{ transform: translateY(-3px) }} }}
@keyframes blinkeye {{ 0%, 91%, 100% {{ opacity: 1 }} 93%, 96% {{ opacity: 0.15 }} }}
@keyframes carry {{
  0%   {{ transform: translate(24px, 142px); opacity: 0 }}
  4%   {{ transform: translate(24px, 142px); opacity: 1 }}
  16%  {{ transform: translate(55px, 142px) }}
  30%  {{ transform: translate(55px, 142px) }}
  42%  {{ transform: translate(169px, 142px) }}
  56%  {{ transform: translate(169px, 142px) }}
  68%  {{ transform: translate(283px, 142px) }}
  82%  {{ transform: translate(283px, 142px) }}
  94%  {{ transform: translate(348px, 58px); opacity: 1 }}
  96%, 100% {{ transform: translate(348px, 58px); opacity: 0 }}
}}
@keyframes ink0 {{ 0%, 18% {{ opacity: 0 }} 24%, 100% {{ opacity: 1 }} }}
@keyframes ink1 {{ 0%, 24% {{ opacity: 0 }} 30%, 100% {{ opacity: 1 }} }}
@keyframes ink2 {{ 0%, 44% {{ opacity: 0 }} 50%, 100% {{ opacity: 1 }} }}
@keyframes ink3 {{ 0%, 50% {{ opacity: 0 }} 56%, 100% {{ opacity: 1 }} }}
@keyframes stampin {{ 0%, 70% {{ opacity: 0 }} 76%, 100% {{ opacity: 1 }} }}
@keyframes prglow {{ 0%, 88% {{ opacity: 0.45 }} 94%, 100% {{ opacity: 1 }} }}
text {{ font-family: {FONT} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important }} }}
</style>"""
    body = desk + bots + paper + prslot + caption
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'font-family="{FONT}" role="img" aria-label="Robots passing a spec through plan, build, verify to a merged PR">'
        f'{style}{chrome(w, h, "$ nightcrew run")}' + body + "</svg>"
    )


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header_svg())
    (OUT / "info-card.svg").write_text(info_card_svg())
    (OUT / "pipeline.svg").write_text(pipeline_svg())
    print("wrote header.svg, info-card.svg, pipeline.svg")
