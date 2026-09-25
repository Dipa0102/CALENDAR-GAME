"""Jour 10 : HELICO 80. Doigt pose : l'helico monte ; doigt leve : il descend.
La grotte est dessinee en gros pixels 2x2 (120 x 120 cases) par des fonctions viper."""

import random
import time

import micropython
from micropython import const

from arcade import GOLD, W, Game, rgb, sprite

FY0 = const(40)
FH = const(240)
NR = const(16)
LR = const(8)
LW = const(120)
CX = const(40)
SW = const(24)
SH = const(14)
RING = const(256)

COPTER = (
    ("wwwwwwwwwww.", "....k.......", ".rrrrrr.....", "rrwwrrrrrrrr", "rrwwrrrr...k", ".rrrrrr.....", "..k..k......"),
    ("...wwwww....", "....k.......", ".rrrrrr.....", "rrwwrrrrrrrr", "rrwwrrrr...k", ".rrrrrr.....", "..k..k......"),
)
COPTER_PAL = {"w": rgb(230, 230, 255), "k": rgb(40, 40, 50), "r": rgb(255, 200, 30)}


def _sw(c):
    return ((c & 0xFF) << 8) | (c >> 8)


@micropython.viper
def _render(buf: ptr32, r0: int, st, dummy: int):
    top = ptr8(st[0])
    bot = ptr8(st[1])
    ot = ptr8(st[2])
    ob = ptr8(st[3])
    pal = ptr32(st[4])
    head = int(st[5])
    r1 = r0 + LR
    bgc = pal[4 + ((r0 * 17) >> 9)]
    edge = pal[2]
    obc = pal[3]
    ra = pal[0]
    rb = pal[1]
    i = 0
    while i < LW:
        c = (head + i) & 255
        t = int(top[c])
        b = int(bot[c])
        y = r0
        p = i
        e = t - 1
        if e > r1:
            e = r1
        while y < e:
            if y & 2:
                buf[p] = rb
                buf[p + LW] = rb
            else:
                buf[p] = ra
                buf[p + LW] = ra
            y += 1
            p += 2 * LW
        e = t
        if e > r1:
            e = r1
        while y < e:
            buf[p] = edge
            buf[p + LW] = edge
            y += 1
            p += 2 * LW
        e = b
        if e > r1:
            e = r1
        while y < e:
            buf[p] = bgc
            buf[p + LW] = bgc
            y += 1
            p += 2 * LW
        e = b + 1
        if e > r1:
            e = r1
        while y < e:
            buf[p] = edge
            buf[p + LW] = edge
            y += 1
            p += 2 * LW
        while y < r1:
            if y & 2:
                buf[p] = rb
                buf[p + LW] = rb
            else:
                buf[p] = ra
                buf[p + LW] = ra
            y += 1
            p += 2 * LW
        q = int(ot[c])
        if q:
            y = q
            if y < r0:
                y = r0
            e = int(ob[c])
            if e > r1:
                e = r1
            p = (y - r0) * 2 * LW + i
            while y < e:
                buf[p] = obc
                buf[p + LW] = obc
                y += 1
                p += 2 * LW
        i += 1


@micropython.viper
def _copter(buf: ptr16, r0: int, st, sy: int):
    spr = ptr16(st[0])
    msk = ptr8(st[1])
    r1 = r0 + NR
    y = sy
    if y < r0:
        y = r0
    e = sy + SH
    if e > r1:
        e = r1
    while y < e:
        k = (y - sy) * SW
        p = (y - r0) * 240 + CX
        x = 0
        while x < SW:
            if msk[k + x]:
                buf[p + x] = spr[k + x]
            x += 1
        y += 1


@micropython.viper
def _span(st, out: ptr16):
    top = ptr8(st[0])
    bot = ptr8(st[1])
    ot = ptr8(st[2])
    ob = ptr8(st[3])
    head = int(st[5])
    mt = 255
    xt = 0
    mb = 255
    xb = 0
    mo = 255
    xo = 0
    i = 0
    while i < LW:
        c = (head + i) & 255
        t = int(top[c])
        b = int(bot[c])
        if t < mt:
            mt = t
        if t > xt:
            xt = t
        if b < mb:
            mb = b
        if b > xb:
            xb = b
        q = int(ot[c])
        if q:
            if q < mo:
                mo = q
            e = int(ob[c])
            if e > xo:
                xo = e
        i += 1
    out[0] = mt
    out[1] = xt
    out[2] = mb
    out[3] = xb
    out[4] = mo
    out[5] = xo


class Helico(Game):
    TITLE = "HELICO 80"
    HELP = ("DOIGT POSE : MONTE", "DOIGT LEVE : DESCEND", "EVITE LES PAROIS")
    FRAME = 30

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        cols = (rgb(84, 36, 112), rgb(66, 28, 94), rgb(255, 60, 200), rgb(0, 200, 255),
                rgb(10, 8, 30), rgb(14, 10, 40), rgb(18, 12, 50), rgb(22, 14, 60))
        self.pal = bytearray(32)
        for k, c in enumerate(cols):
            s = _sw(c)
            for j in (0, 2):
                self.pal[4 * k + j] = s & 255
                self.pal[4 * k + j + 1] = s >> 8
        self.frames = []
        for art in COPTER:
            spr = bytearray(SW * SH * 2)
            msk = bytearray(SW * SH)
            for j, row in enumerate(art):
                for i, ch in enumerate(row):
                    if ch != ".":
                        s = _sw(COPTER_PAL[ch])
                        for dy in range(2):
                            for dx in range(2):
                                k = (j * 2 + dy) * SW + i * 2 + dx
                                spr[2 * k] = s & 255
                                spr[2 * k + 1] = s >> 8
                                msk[k] = 1
            self.frames.append((spr, msk))
        self.buf = bytearray(W * NR * 2)
        self.ctop = bytearray(RING)
        self.cbot = bytearray(RING)
        self.ot = bytearray(RING)
        self.ob = bytearray(RING)
        self.sp = bytearray(12)
        self.was = bytearray(FH // NR)

    def preview(self, y):
        spr = sprite(COPTER[0], COPTER_PAL, 6, rgb(0, 0, 0))
        self.t.blit(spr[0], (W - spr[1]) // 2, y + 10, spr[1], spr[2])

    def rock_band(self, y, h):
        t = self.t
        t.fill_rect(0, y, W, h, rgb(66, 28, 94))
        for yy in range(y, y + h, 8):
            t.fill_rect(0, yy, W, 4, rgb(84, 36, 112))

    def setup(self):
        self.rock_band(20, FY0 - 20)
        self.rock_band(FY0 + FH, 320 - FY0 - FH)
        self.t.fill_rect(0, FY0 - 2, W, 2, rgb(255, 60, 200))
        self.t.fill_rect(0, FY0 + FH, W, 2, rgb(255, 60, 200))
        self.reset_cave()

    def reset_cave(self):
        self.head = 0
        self.center = FH / 2
        self.gap = 170.0
        self.drift = 0.0
        self.next_ob = 70
        self.ob_left = 0
        self.ob_y = 0
        self.wp = 0
        for i in range(RING):
            self.ctop[i] = (FH // 2 - 85) >> 1
            self.cbot[i] = (FH // 2 + 85) >> 1
            self.ot[i] = 0
            self.ob[i] = 0
        self.gen(LW)
        self.y = float(FH // 2 - SH // 2)
        self.vy = 0.0
        self.v = 2
        self.full = True
        self.osy = int(self.y)

    def gen(self, n):
        """Ajoute n colonnes de 2 pixels au bout de la grotte."""
        for _ in range(n):
            self.drift = max(-4.4, min(4.4, self.drift + (random.random() - 0.5) * 1.6))
            self.center += self.drift
            half = self.gap / 2
            if self.center < half + 8:
                self.center = half + 8
                self.drift = abs(self.drift)
            elif self.center > FH - half - 8:
                self.center = FH - half - 8
                self.drift = -abs(self.drift)
            c = self.wp
            self.wp = (c + 1) & 255
            self.ctop[c] = int(self.center - half) >> 1
            self.cbot[c] = int(self.center + half) >> 1
            self.ot[c] = 0
            self.ob[c] = 0
            self.next_ob -= 1
            if self.next_ob <= 0:
                self.ob_left = 6
                y = random.randint(int(self.center - half) + 8, int(self.center + half) - 48)
                self.ob_y = max(2, y) >> 1
                self.next_ob = random.randint(45, 75)
            if self.ob_left > 0:
                self.ob_left -= 1
                self.ot[c] = self.ob_y
                self.ob[c] = self.ob_y + 20
            self.gap = max(84.0, self.gap - 0.06)

    def crashed(self):
        y0 = int(self.y) + 2
        y1 = int(self.y) + SH - 2
        if y0 < 0 or y1 > FH:
            return True
        for x in range(CX + 2, CX + SW - 2, 2):
            c = (self.head + (x >> 1)) & 255
            if y0 < 2 * self.ctop[c] or y1 > 2 * self.cbot[c]:
                return True
            q = self.ot[c]
            if q and y1 > 2 * q and y0 < 2 * self.ob[c]:
                return True
        return False

    def step(self, pt, now):
        if pt:
            self.vy = max(-4.5, self.vy - 0.55)
        else:
            self.vy = min(4.5, self.vy + 0.4)
        self.y += self.vy
        self.head = (self.head + self.v) & 255
        self.gen(self.v)
        self.score += 2 * self.v
        self.v = 2 if self.score < 3000 else 3
        sy = int(self.y)
        st = (self.ctop, self.cbot, self.ot, self.ob, self.pal, self.head)
        cp = self.frames[(now // 60) & 1]
        _span(st, self.sp)
        sp = self.sp
        mt, xt, mb, xb, mo, xo = sp[0], sp[2], sp[4], sp[6], sp[8], sp[10]
        c0 = min(sy, self.osy)
        c1 = max(sy, self.osy) + SH
        full = self.full
        was = self.was
        for k in range(FH // NR):
            r0 = k * LR
            r1 = r0 + LR
            quiet = (r1 <= mt - 1 or (r0 >= xt and r1 <= mb) or r0 >= xb + 1) \
                and (mo == 255 or r1 <= mo or r0 >= xo) and (2 * r1 <= c0 or 2 * r0 >= c1)
            if quiet and not full and not was[k]:
                continue
            was[k] = 0 if quiet else 1
            _render(self.buf, r0, st, 0)
            _copter(self.buf, 2 * r0, cp, sy)
            self.t.blit(self.buf, 0, FY0 + 2 * r0, W, NR)
        self.full = False
        self.osy = sy
        if self.crashed():
            self.lives -= 1
            self.sfx.tone(90, 450)
            self.t.fill_rect(CX - 4, max(FY0, FY0 + sy - 4), SW + 8, SH + 8, GOLD)
            time.sleep_ms(500)
            if self.lives > 0:
                self.reset_cave()
            self.full = True
        return self.lives > 0

    def bot(self, n):
        if not hasattr(self, "wp"):
            return (120, 160) if n % 4 < 2 else None
        c = (self.head + (CX + SW + 24) // 2) & 255
        t, b = 2 * self.ctop[c], 2 * self.cbot[c]
        for k in range(0, 30, 3):
            d = (self.head + CX // 2 + k) & 255
            if self.ot[d]:
                q, e = 2 * self.ot[d], 2 * self.ob[d]
                t, b = (t, q) if q - t > b - e else (e, b)
                break
        mid = (t + b) // 2
        return (120, 160) if self.y + SH // 2 + self.vy * 5 > mid else None


GAME = Helico


def play(tft, touch, day):
    GAME(tft, touch, day).run()
