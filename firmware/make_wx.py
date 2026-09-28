"""Decoupe la planche d'icones meteo en fichiers wx*.raw (RGB565 big-endian).

Planche 4 x 3 dans cet ordre : soleil, eclaircies, nuages, pluie, orage, neige,
brouillard, vent, nuit, canicule, tempete, arc-en-ciel.
Chaque icone est pre-composee sur le fond ou elle sera affichee : la carte n'a
plus qu'a faire un blit, sans transparence a calculer.
"""
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance
from scipy import ndimage

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "meteo_icones.png"

COLS, ROWS = 4, 3
SHEETS = {
    "n18": ((20, 10, 36), 18),
    "p18": ((28, 28, 44), 18),
    "a64": ((18, 18, 28), 64),
}


def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def split(px):
    border = np.concatenate([px[0], px[-1], px[:, 0], px[:, -1]])
    bg = np.median(border, axis=0)
    fg = np.abs(px - bg).sum(axis=2) > 14
    lab, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    fg = np.isin(lab, 1 + np.flatnonzero(sizes >= 60))
    groups, n = ndimage.label(ndimage.binary_dilation(fg, iterations=14))
    sizes = ndimage.sum(fg, groups, range(1, n + 1))
    keep = 1 + np.argsort(sizes)[::-1][: COLS * ROWS]
    boxes = ndimage.find_objects(groups)
    found = []
    for g in keep:
        sl = boxes[g - 1]
        m = fg[sl] & (groups[sl] == g)
        ys, xs = np.nonzero(m)
        tight = (
            slice(sl[0].start + ys.min(), sl[0].start + ys.max() + 1),
            slice(sl[1].start + xs.min(), sl[1].start + xs.max() + 1),
        )
        found.append((tight, m[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]))
    found.sort(key=lambda it: (it[0][0].start + it[0][0].stop) // 2)
    rows = []
    for r in range(ROWS):
        row = found[r * COLS : (r + 1) * COLS]
        row.sort(key=lambda it: it[0][1].start)
        rows += row
    return rows


def silhouette(fg):
    pad = 12
    parts, n = ndimage.label(np.pad(fg, pad))
    m = np.zeros(parts.shape, bool)
    for sl, i in zip(ndimage.find_objects(parts), range(1, n + 1)):
        box = tuple(slice(max(0, s.start - pad), s.stop + pad) for s in sl)
        m[box] |= ndimage.binary_closing(parts[box] == i, iterations=7)
    holes = ndimage.binary_fill_holes(m) & ~m
    hl, hn = ndimage.label(holes)
    hs = ndimage.sum(holes, hl, range(1, hn + 1))
    m |= np.isin(hl, 1 + np.flatnonzero(hs < 2500))
    return m[pad:-pad, pad:-pad]


def cut(px, sl, fg):
    h, w, _ = px.shape
    alpha = silhouette(fg).astype(float)
    y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
    side = int(max(y1 - y0, x1 - x0) * 1.03)
    oy, ox = (side - (y1 - y0)) // 2, (side - (x1 - x0)) // 2
    out = np.zeros((side, side, 3))
    oa = np.zeros((side, side))
    out[oy : oy + y1 - y0, ox : ox + x1 - x0] = px[y0:y1, x0:x1]
    oa[oy : oy + y1 - y0, ox : ox + x1 - x0] = alpha
    return out, oa


def render(rgb, alpha, bg, size):
    comp = rgb * alpha[..., None] + np.array(bg, float) * (1 - alpha[..., None])
    im = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
    im = im.resize((size, size), Image.BOX if size < 32 else Image.LANCZOS)
    return ImageEnhance.Color(im).enhance(1.3)


def main():
    sheet = np.asarray(Image.open(SRC).convert("RGB"), float)
    icons = [cut(sheet, sl, fg) for sl, fg in split(sheet)]
    for name, (bg, size) in SHEETS.items():
        data = bytearray()
        preview = Image.new("RGB", (size * COLS + COLS + 1, size * ROWS + ROWS + 1), bg)
        for i, (rgb, alpha) in enumerate(icons):
            im = render(rgb, alpha, bg, size)
            for p in im.get_flattened_data():
                data += struct.pack(">H", rgb565(*p))
            preview.paste(im, (1 + (i % COLS) * (size + 1), 1 + (i // COLS) * (size + 1)))
        (HERE / ("wx%s.raw" % name)).write_bytes(data)
        zoom = max(1, 256 // size)
        preview.resize((preview.width * zoom, preview.height * zoom), Image.NEAREST).save(
            HERE / ("wx_apercu_%s.png" % name)
        )
        print("wx%s.raw" % name, size, "px", len(data), "octets")


if __name__ == "__main__":
    main()
