"""Decoupe la planche des 12 ecrans de veille en veille.raw (RGB565 big-endian).

Planche 4 x 3 : chaque vignette imite un ecran avec une fausse barre d'etat
(heure, Wi-Fi, batterie) qu'on retire. Les images sont mises bout a bout,
IMG_W x IMG_H chacune, sans en-tete.
Usage : python make_veille.py [planche.png] [--debug]
"""
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC = Path(ARGS[0]) if ARGS else HERE / "veille.png"
DEBUG = "--debug" in sys.argv

IMG_W, IMG_H = 240, 150
# Ecran de chaque vignette dans la planche 1536 x 1024 : colonnes, puis haut et
# hauteur de chaque rangee.
COL_X = (44, 422, 800, 1174)
SCR_W = 320
ROWS = ((150, 232), (455, 222), (744, 214))
STATUS_H = 28
INSET = 2


def boxes():
    """Zone utile de chaque ecran aux proportions IMG_W x IMG_H : recadrage centre en
    largeur, par le haut en hauteur (la signature est en bas)."""
    for top, h in ROWS:
        for x in COL_X:
            x0, y0 = x + INSET, top + STATUS_H
            x1, y1 = x + SCR_W - INSET, top + h - INSET
            w, h2 = x1 - x0, y1 - y0
            if w * IMG_H > h2 * IMG_W:
                cut = (w - h2 * IMG_W // IMG_H) // 2
                x0, x1 = x0 + cut, x1 - cut
            else:
                y0 = y1 - w * IMG_H // IMG_W
            yield (x0, y0, x1, y1)


def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def main():
    sheet = Image.open(SRC).convert("RGB")
    if DEBUG:
        dbg = sheet.copy()
        d = ImageDraw.Draw(dbg)
        for x0, y0, x1, y1 in boxes():
            d.rectangle((x0, y0, x1, y1), outline=(255, 0, 0))
        dbg.save(HERE / "veille_debug.png")
        print("veille_debug.png")
        return
    data = bytearray()
    preview = Image.new("RGB", (IMG_W * 4 + 5, IMG_H * 3 + 4), (40, 40, 40))
    for i, box in enumerate(boxes()):
        im = sheet.crop(box).resize((IMG_W, IMG_H), Image.LANCZOS)
        for p in im.get_flattened_data():
            data += struct.pack(">H", rgb565(*p))
        preview.paste(im, (1 + (i % 4) * (IMG_W + 1), 1 + (i // 4) * (IMG_H + 1)))
    (HERE / "veille.raw").write_bytes(data)
    preview.save(HERE / "veille_apercu.png")
    print("veille.raw", 12, "images", IMG_W, "x", IMG_H, len(data), "octets")


if __name__ == "__main__":
    main()
