"""Decoupe la planche des 12 ecrans de veille en veille.raw (RGB565 big-endian).

Planche 1254 x 1254, 4 x 3. Chaque vignette a une fausse barre d'etat
(heure, Wi-Fi, batterie) qu'on retire. Les images sont mises bout a bout,
240 x 150 chacune, sans en-tete.
Usage : python make_veille.py [planche.png]
"""
import struct
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC = Path(ARGS[0]) if ARGS else HERE / "veille.png"

IMG_W, IMG_H = 240, 150
# Coins des 12 ecrans sur la planche 1254 x 1254 (sans la legende sous chaque case).
COLS = ((24, 322), (336, 618), (636, 922), (937, 1228))
ROWS = ((257, 489), (558, 771), (867, 1062))
STATUS = 40
INSET = 4


def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def frames(sheet):
    for y0, y1 in ROWS:
        for x0, x1 in COLS:
            card = sheet.crop((x0 + INSET, y0 + STATUS, x1 - INSET, y1 - INSET))
            w, h = card.size
            if w / h > IMG_W / IMG_H:
                nw = int(h * IMG_W / IMG_H)
                left = (w - nw) // 2
                card = card.crop((left, 0, left + nw, h))
            else:
                nh = int(w * IMG_H / IMG_W)
                card = card.crop((0, h - nh, w, h))
            yield card.resize((IMG_W, IMG_H), Image.LANCZOS)


def main():
    sheet = Image.open(SRC).convert("RGB")
    if sheet.size != (1254, 1254):
        raise SystemExit("planche attendue 1254x1254, recu %sx%s" % sheet.size)
    data = bytearray()
    preview = Image.new("RGB", (IMG_W * 4 + 5, IMG_H * 3 + 4), (18, 32, 40))
    for i, im in enumerate(frames(sheet)):
        for r, g, b in im.get_flattened_data():
            data += struct.pack(">H", rgb565(r, g, b))
        preview.paste(im, (1 + (i % 4) * (IMG_W + 1), 1 + (i // 4) * (IMG_H + 1)))
    (HERE / "veille.raw").write_bytes(data)
    preview.save(HERE / "veille_apercu.png")
    print("veille.raw", 12, "images", IMG_W, "x", IMG_H, len(data), "octets")


if __name__ == "__main__":
    main()
