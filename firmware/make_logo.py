"""Convertit le logo PNG en logo.raw (RGB565 big-endian, en-tete largeur/hauteur)."""
import struct
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "logo.png"
MAX_W = 236

im = Image.open(SRC).convert("RGB")
mask = im.convert("L").point(lambda v: 255 if v > 24 else 0)
im = im.crop(mask.getbbox())
h = round(im.height * MAX_W / im.width)
im = im.resize((MAX_W, h), Image.LANCZOS)
canvas = Image.new("RGB", (240, h), (0, 0, 0))
canvas.paste(im, ((240 - MAX_W) // 2, 0))

data = bytearray(struct.pack(">HH", 240, h))
for r, g, b in canvas.getdata():
    c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    data += struct.pack(">H", c)
(HERE / "logo.raw").write_bytes(data)
canvas.resize((480, h * 2), Image.NEAREST).save(HERE / "logo_apercu.png")
print("logo.raw", 240, "x", h, len(data), "octets")
