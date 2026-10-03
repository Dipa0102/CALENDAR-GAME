"""Convertit l'embleme de l'affiche en logo.raw (RGB565, fond papier)."""
import struct
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\Utilisateur\Downloads\Calendar Game-3\emblem.webp")
MAX_W = 240


def paper_of(im):
    return im.getpixel((2, 2))


def is_paper(p, bg):
    return abs(p[0] - bg[0]) < 18 and abs(p[1] - bg[1]) < 18 and abs(p[2] - bg[2]) < 18


im = Image.open(SRC).convert("RGB")
bg = paper_of(im)
w, h = im.size
pix = im.load()
top = 0
while top < h and all(is_paper(pix[x, top], bg) for x in range(0, w, 3)):
    top += 1
bot = h - 1
while bot > top and all(is_paper(pix[x, bot], bg) for x in range(0, w, 3)):
    bot -= 1
left = 0
while left < w and all(is_paper(pix[left, y], bg) for y in range(0, h, 3)):
    left += 1
right = w - 1
while right > left and all(is_paper(pix[right, y], bg) for y in range(0, h, 3)):
    right -= 1
im = im.crop((left, top, right + 1, bot + 1))
th = round(im.height * MAX_W / im.width)
im = im.resize((MAX_W, th), Image.LANCZOS)

data = bytearray(struct.pack(">HH", MAX_W, th))
for r, g, b in im.getdata():
    c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    data += struct.pack(">H", c)
(HERE / "logo.raw").write_bytes(data)
im.resize((MAX_W * 2, th * 2), Image.NEAREST).save(HERE / "logo_apercu.png")
print("logo.raw", MAX_W, "x", th, len(data), "octets, fond", bg)
