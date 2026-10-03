"""Jour 18 : FIRE ESCAPE. Trois rebonds fixes vers l'ambulance, le doigt pose le tremplin."""

import random
import time

from arcade import GOLD, RED, W, Game, rgb, sprite

SKY = rgb(28, 24, 48)
BRICK = rgb(120, 48, 44)
BRICK2 = rgb(88, 32, 36)
STREET = rgb(48, 44, 62)
AMB_W = rgb(230, 230, 240)
AMB_R = rgb(210, 30, 40)
FIRE = rgb(255, 140, 30)
FIRE2 = rgb(255, 220, 70)
NET = rgb(240, 210, 40)
NSTEP = 24
PX = 6
PY = 10
TW = 36
TH = 12
TRAY_Y = 252
BX = (54, 102, 150)
CX = (72, 120, 168)

GUY = (
    "..yy..",
    ".ywwy.",
    ".yyyy.",
    "..rr..",
    ".rrrr.",
    "r.rr.r",
    "..bb..",
    ".b..b.",
)
GUY_PAL = {"y": rgb(250, 200, 150), "w": rgb(30, 20, 20), "r": rgb(40, 90, 200),
           "b": rgb(40, 40, 70)}
TRAY = (
    "r.r............r.r",
    "byb............byb",
    "bbbbbbbbbbbbbbbbbb",
    "yyyyyyyyyyyyyyyyyy",
    ".y..............y.",
    "..yyyyyyyyyyyyyy..",
)
TRAY_PAL = {"r": rgb(250, 200, 150), "b": rgb(230, 50, 40), "y": NET}
AMB = (
    "....wwwwwwww....",
    "...wwwwwwwwww...",
    "rrrrwwwwwwwwrrrr",
    "rwwwwkkkkwwwwwwr",
    "rwwwwwwwwwwwwwwr",
    "rrrrrrrrrrrrrrrr",
    "rwwwwwwwwwwwwwwr",
    "rwwwwwwwwwwwwwwr",
    ".rkkrrrrrrrrkkr.",
    "..kk........kk..",
    "..kk........kk..",
    "................",
)
AMB_PAL = {"w": AMB_W, "r": AMB_R, "k": rgb(20, 20, 28)}


def _arc(x0, y0, x1, y1, amp, n):
    pts = []
    nn = n * n
    for i in range(1, n + 1):
        x = x0 + (x1 - x0) * i // n
        y = y0 + (y1 - y0) * i // n - (4 * amp * i * (n - i)) // nn
        pts.append((x, y))
    return tuple(pts)


PATH = (
    _arc(52, 96, 66, 240, 6, NSTEP),
    _arc(66, 240, 114, 240, 58, NSTEP),
    _arc(114, 240, 162, 240, 52, NSTEP),
    _arc(162, 240, 200, 250, 14, NSTEP),
)


class FireEscape(Game):
    TITLE = "FIRE ESCAPE"
    HELP = ("DOIGT : TREMPLIN", "3 REBONDS PUIS L AMBU", "NE LES LAISSE PAS TOMBER")
    BG = SKY

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.guy = sprite(GUY, GUY_PAL, 2, SKY, PX, PY)
        self.tray = sprite(TRAY, TRAY_PAL, 2, SKY, 0, 0)
        self.amb = sprite(AMB, AMB_PAL, 2, SKY)

    def preview(self, y):
        t = self.t
        t.fill_rect(0, y, W, 95, SKY)
        t.fill_rect(8, y + 8, 40, 86, BRICK)
        t.fill_rect(16, y + 18, 12, 14, FIRE2)
        t.fill_rect(16, y + 40, 12, 14, GOLD)
        t.fill_rect(188, y + 52, 40, 28, AMB_W)
        t.fill_rect(188, y + 52, 40, 8, AMB_R)
        t.fill_rect(194, y + 76, 8, 6, rgb(20, 20, 28))
        t.fill_rect(216, y + 76, 8, 6, rgb(20, 20, 28))
        t.fill_rect(70, y + 78, TW, 8, NET)
        self.put(self.guy, 108, y + 28)

    def scenery(self):
        t = self.t
        t.fill_rect(0, 20, W, 260, SKY)
        t.fill_rect(0, 280, W, 40, STREET)
        t.fill_rect(0, 36, 44, 244, BRICK)
        t.fill_rect(0, 36, 44, 8, BRICK2)
        t.fill_rect(4, 28, 10, 16, FIRE)
        t.fill_rect(18, 22, 14, 22, FIRE2)
        t.fill_rect(32, 30, 10, 14, FIRE)
        for i in range(4):
            wy = 64 + i * 44
            t.fill_rect(10, wy, 14, 16, GOLD if i != 1 else FIRE2)
            t.fill_rect(28, wy, 10, 16, rgb(40, 30, 50))
        t.fill_rect(40, 92, 8, 18, FIRE2)
        self.put(self.amb, 200, 252)
        for x in CX:
            t.fill_rect(x - 5, TRAY_Y + TH + 4, 10, 2, rgb(70, 66, 90))

    def setup(self):
        self.scenery()
        self.guys = []
        self.pos = 1
        self.old = 1
        self.put(self.tray, BX[1], TRAY_Y)
        self.n = 0
        self.next_g = 8
        self.maxg = 1

    def slot(self, x):
        if x < 96:
            return 0
        if x < 144:
            return 1
        return 2

    def spawn(self):
        gap = 72 - self.score // 12 + random.randint(0, 16)
        if gap < 28:
            gap = 28
        self.next_g = self.n + gap
        if len(self.guys) >= self.maxg:
            return
        self.guys.append([0, -1])

    def miss(self, g, x, y):
        self.wipe_guy(g)
        self.lives -= 1
        self.sfx.tone(110, 280)
        self.t.fill_rect(x, min(300, y + 8), 12, 6, RED)
        time.sleep_ms(220)
        self.t.fill_rect(x, min(300, y + 8), 12, 6, SKY if y + 8 < 280 else STREET)
        self.put(self.tray, BX[self.pos], TRAY_Y)
        self.put(self.amb, 200, 252)

    def wipe_guy(self, g):
        si, k = g[0], g[1]
        if si > 3:
            return
        x, y = PATH[si][k]
        self.clear(x - PX, y - PY, self.guy[1], self.guy[2])

    def step(self, pt, now):
        self.n += 1
        if pt:
            self.pos = self.slot(pt[0])
        if self.pos != self.old:
            self.clear(BX[self.old], TRAY_Y, TW, TH)
            self.old = self.pos
        self.put(self.tray, BX[self.pos], TRAY_Y)
        if self.n >= self.next_g:
            self.maxg = 1 + self.score // 40
            if self.maxg > 3:
                self.maxg = 3
            self.spawn()
        if (self.n & 3) == 0:
            self.t.fill_rect(18, 22, 14, 10, FIRE if (self.n >> 2) & 1 else FIRE2)
        keep = []
        for g in self.guys:
            si, k = g[0], g[1]
            k += 1
            if k >= NSTEP:
                x, y = PATH[si][NSTEP - 1]
                if si < 3:
                    if self.pos == si:
                        self.sfx.tone(784 + si * 80, 35)
                        si += 1
                        k = 0
                    else:
                        self.miss(g, x, y)
                        if self.lives <= 0:
                            return False
                        continue
                else:
                    self.wipe_guy(g)
                    self.score += 10
                    self.sfx.tone(1175, 50)
                    continue
            g[0], g[1] = si, k
            x, y = PATH[si][k]
            self.put(self.guy, x, y)
            keep.append(g)
        self.guys = keep
        self.put(self.amb, 200, 252)
        return True

    def bot(self, n):
        if not hasattr(self, "guys"):
            return (120, 160) if n % 4 < 2 else None
        best = None
        bd = 99
        for g in self.guys:
            si, k = g[0], g[1]
            if si > 2:
                continue
            left = NSTEP - k
            if left < bd:
                bd = left
                best = si
        if best is None:
            return (CX[self.pos], 260)
        return (CX[best], 260)


GAME = FireEscape


def play(tft, touch, day):
    GAME(tft, touch, day).run()
