#!/usr/bin/env python3
"""Turn a photo into assets/portrait.svg: monochrome ASCII art whose rows
wipe in top to bottom. Run locally, once per photo:

    pip install pillow numpy rembg   # rembg optional but much better
    python scripts/make_portrait.py path/to/photo.jpg

Bright areas map to sparse glyphs (spaces), so backgrounds vanish."""

import html
import pathlib
import sys

import numpy as np
from PIL import Image, ImageOps

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "portrait.svg"

COLS, ROWS = 96, 58          # character grid
RAMP = " .`:-=+*cs#%@"        # bright (sparse) -> dark (dense)
BG = "#0d0d0c"
BORDER = "#2a2926"
FILL = "#c9cdc4"              # single light gray -- monochrome on purpose
CW, CH = 6.0, 10              # cell size in px


def prep(path):
    img = Image.open(path)
    try:
        from rembg import remove
        img = remove(img)  # isolate subject
    except ImportError:
        print("rembg not installed - keeping original background")
    # composite onto white so background maps to spaces
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    img = Image.alpha_composite(bg, img.convert("RGBA")).convert("L")
    # lift facial midtones: blend histogram-equalized version into original
    img = Image.blend(img, ImageOps.equalize(img), 0.5)
    img = ImageOps.autocontrast(img, cutoff=2)
    return img


def to_svg(img):
    img = img.resize((COLS, ROWS))
    px = np.asarray(img) / 255.0
    rows_svg = []
    for r in range(ROWS):
        chars = "".join(RAMP[int((1 - px[r, c]) * (len(RAMP) - 1))] for c in range(COLS))
        if not chars.strip():
            continue
        y = 18 + r * CH
        rows_svg.append(
            f'<text x="16" y="{y}" class="ln" style="animation-delay:{r * 0.045:.3f}s" '
            f'xml:space="preserve">{html.escape(chars)}</text>'
        )
    w, h = int(COLS * CW + 32), int(ROWS * CH + 28)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="ui-monospace, Menlo, Consolas, monospace" role="img" aria-label="ASCII portrait of Sean">
<style>
@keyframes appear {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
.ln {{ animation: appear 0.25s backwards; font-size: 10px; fill: {FILL} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important }} }}
</style>
<rect width="{w}" height="{h}" rx="12" fill="{BG}" stroke="{BORDER}"/>
{"".join(rows_svg)}
</svg>"""


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: make_portrait.py photo.jpg")
    OUT.write_text(to_svg(prep(sys.argv[1])))
    print(f"wrote {OUT}")
