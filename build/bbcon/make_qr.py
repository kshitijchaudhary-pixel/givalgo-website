#!/usr/bin/env python3
"""Generate a printable bbcon lucky-draw QR code (banners, table tents, slides).

The booth screen (givalgo.ai/bbcon/booth/#<key>) draws its own QR code in the
browser; this is only for print. The code carries the entry key, so it is
written to build/bbcon/out/, which is git-ignored. Never commit it: the
website repo is public. Get the key from the leads sheet (bbcon → Show booth
link, the part after #). If you open entries again, the key changes and any
print made with the old key stops working.

  build/bbcon/out/qr.svg   vector, for print
  build/bbcon/out/qr.png   raster, for slides

Error correction is H (~30% recoverable) so the Givalgo "G" in the middle can
sit on top of modules without breaking the scan. The script decodes its own
PNG before writing anything, so a logo that grew too big fails here and not at
the booth.

    pip install segno pillow opencv-python-headless
    python3 build/bbcon/make_qr.py <entry key>
"""

import io
import re
import sys
from pathlib import Path

import segno
from PIL import Image, ImageDraw

FORM_URL = "https://givalgo.ai/bbcon/#"

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAVY = "#0c1830"
TEAL = "#00b4b3"
TEAL_DEEP = "#00848b"

# The "G" mark from the site logo (build/logo.svg).
G_VIEWBOX = (17.08, 47.83, 89.27, 111.36)  # x, y, w, h of the mark
G_BODY = "M70.01,130.83c-3.61,0-6.95-.74-10-2.23-3.06-1.49-5.7-3.47-7.94-5.96-2.24-2.48-4-5.37-5.29-8.66-1.29-3.29-1.94-6.79-1.94-10.49s.65-7.06,1.94-10.35c1.29-3.29,3.05-6.2,5.29-8.73,2.24-2.53,4.91-4.51,8-5.96,3.1-1.44,6.45-2.17,10.07-2.17.89,0,31.32-.03,32.2.07v-28.5c-.92-.05-31.4,0-32.33,0-7.4,0-14.31,1.47-20.72,4.4-6.41,2.93-12.01,6.95-16.78,12.05-4.78,5.1-8.54,11.01-11.3,17.73-2.76,6.72-4.13,13.87-4.13,21.45s1.38,14.73,4.13,21.45c2.75,6.72,6.52,12.63,11.3,17.73,4.78,5.1,10.37,9.12,16.78,12.05,6.41,2.93,13.32,4.4,20.72,4.4,2.06,0,4.09-.12,6.09-.35v-28.71c-1.96.51-3.98.77-6.09.77Z"
G_ARROW = "M106.34,103.47h-33.05l12.54,21.15c-1.86,1.7-3.9,3.07-6.12,4.1-1.17.55-2.38.99-3.62,1.35v-.02c-1.96.51-3.98.77-6.09.77-3.61,0-6.95-.74-10-2.23-.05-.02-.1-.05-.14-.07v29.61c3.27.65,6.66.98,10.15.98,2.06,0,4.09-.12,6.09-.35v-.03c5.21-.77,9.67-2.52,14.43-4.86,3.27-1.61,6.32-3.57,9.19-5.86l6.63,11.18v-55.72Z"

BORDER = 4          # quiet zone, in modules (the spec minimum)
LOGO_FRACTION = 0.22  # logo plate width as a share of the symbol width
PNG_SCALE = 40      # px per module


def build(url):
    qr = segno.make(url, error="h", micro=False, boost_error=False)
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    # Logo plate: an odd number of modules, centred on the grid, left blank
    # (no modules drawn) with the G mark on top.
    plate = int(round(n * LOGO_FRACTION)) | 1
    lo = (n - plate) // 2
    return qr, matrix, n, plate, lo


def svg(matrix, n, plate, lo, label):
    total = n + 2 * BORDER
    d = []
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            if dark and not (lo <= x < lo + plate and lo <= y < lo + plate):
                d.append(f"M{x + BORDER},{y + BORDER}h1v1h-1z")
    px, py = lo + BORDER, lo + BORDER
    # The mark sits inside the plate with a module of padding each side.
    inner = plate - 2
    gx, gy, gw, gh = G_VIEWBOX
    s = inner / max(gw, gh)
    tx = px + 1 + (inner - gw * s) / 2 - gx * s
    ty = py + 1 + (inner - gh * s) / 2 - gy * s
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total} {total}" '
        f'role="img" aria-label="QR code: {label}" shape-rendering="crispEdges">'
        f'<rect width="{total}" height="{total}" fill="#fff"/>'
        f'<path fill="{NAVY}" d="{"".join(d)}"/>'
        f'<g transform="translate({tx:.3f} {ty:.3f}) scale({s:.5f})" shape-rendering="geometricPrecision">'
        f'<path fill="{TEAL_DEEP}" d="{G_BODY}"/><path fill="{TEAL}" d="{G_ARROW}"/></g>'
        "</svg>"
    )


def png(matrix, n, plate, lo):
    total = (n + 2 * BORDER) * PNG_SCALE
    img = Image.new("RGB", (total, total), "white")
    draw = ImageDraw.Draw(img)
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            if dark and not (lo <= x < lo + plate and lo <= y < lo + plate):
                x0, y0 = (x + BORDER) * PNG_SCALE, (y + BORDER) * PNG_SCALE
                draw.rectangle([x0, y0, x0 + PNG_SCALE - 1, y0 + PNG_SCALE - 1], fill=NAVY)
    p0 = (lo + BORDER) * PNG_SCALE
    # g-mark.png is the same G mark on a transparent canvas.
    mark = Image.open(HERE / "g-mark.png").convert("RGBA")
    mark = mark.crop(mark.getchannel("A").getbbox())
    inner = (plate - 2) * PNG_SCALE
    k = inner / max(mark.size)
    mark = mark.resize((round(mark.width * k), round(mark.height * k)), Image.LANCZOS)
    ox = p0 + PNG_SCALE + (inner - mark.width) // 2
    oy = p0 + PNG_SCALE + (inner - mark.height) // 2
    img.paste(mark, (ox, oy), mark)
    return img


def decodes_to(img, url):
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("⚠️  opencv not installed — skipping the decode check", file=sys.stderr)
        return True
    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    for size in (img.width, 600, 300):  # full size, then phone-camera-ish sizes
        got, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.resize(arr, (size, size)))
        if got != url:
            print(f"❌  decode at {size}px returned {got!r}, expected {url!r}", file=sys.stderr)
            return False
    return True


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"[a-z0-9]{6,40}", sys.argv[1], re.I):
        sys.exit(__doc__.split("\n\n")[-1].strip())
    url = FORM_URL + sys.argv[1].lower()
    label = "the bbcon entry form"
    qr, matrix, n, plate, lo = build(url)
    raster = png(matrix, n, plate, lo)
    if not decodes_to(raster, url):
        sys.exit(1)

    OUT.mkdir(exist_ok=True)
    (OUT / "qr.svg").write_text(svg(matrix, n, plate, lo, label) + "\n")
    buf = io.BytesIO()
    raster.save(buf, "PNG", optimize=True)
    (OUT / "qr.png").write_bytes(buf.getvalue())
    print(f"✅  version {qr.version}-{qr.error.upper()}, {n}x{n} modules, logo plate {plate}x{plate} → {OUT}/qr.svg, qr.png")


if __name__ == "__main__":
    main()
