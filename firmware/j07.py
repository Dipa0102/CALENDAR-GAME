"""Jour 7 : ROUTE 80. Traverser les deux routes sans se faire ecraser."""

import random
import time

from arcade import GOLD, W, Game, rgb, sprite

ROW_H = 22
Y0 = 24
ROWS = 13
GRASS = rgb(40, 130, 60)
ROAD = rgb(46, 46, 58)
PAVE = rgb(140, 130, 115)
LINE = rgb(230, 230, 230)
LANES = (1, 2, 3, 4, 5, 7, 8, 9, 10, 11)
PX = 112

FROG = ("g......g", "gg.gg.gg", ".gwggwg.", ".gkggkg.", "..gggg..", ".gggggg.", "gg.gg.gg", "g......g")
FROG_PAL = {"g": rgb(90, 230, 70), "w": rgb(255, 255, 255), "k": rgb(0, 0, 0)}
SPLAT = ("r.r..r.r", ".rrrrrr.", "rrrrrrrr", ".rrrrrr.", "rrrrrrrr", ".rrrrrr.", "r.r..r.r", "........")
SPLAT_PAL = {"r": rgb(220, 30, 40)}
CAR = (
    "...cccccc.....",
    "..cwwcwwwc....",
    "ccccccccccccccy",
    "cCCCCCCCCCCCCc",
    "cCCCCCCCCCCCCc",
    ".kk.......kk..",
    ".kk.......kk..",
)
TRUCK = (
    "CCCCCCCCCCCCC.ccc...",
    "CwwwwwwwwwwwC.cwwc..",
    "CwwwwwwwwwwwC.cwwcc.",
    "CCCCCCCCCCCCCcccccccy",
    "CCCCCCCCCCCCCccccccc",
    ".kk...kk.....kk..kk.",
    ".kk...kk.....kk..kk.",
)
COLORS = ((230, 50, 50), (60, 120, 255), (255, 200, 40), (180, 60, 220), (40, 200, 200), (255, 130, 30))


def _dark(c):
    return (c[0] // 2, c[1] // 2, c[2] // 2)


def _rev(s):
    c = list(s)
    c.reverse()
    return "".join(c)


def _flip(rows):
    n = max(len(r) for r in rows)
    return tuple(_rev(r + "." * (n - len(r))) for r in rows)


class Road(Game):
    TITLE = "ROUTE 80"
    HELP = ("TOUCHE AU-DESSUS : AVANCE", "EN DESSOUS : RECULE", "EVITE LES VOITURES")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.frog = {bg: sprite(FROG, FROG_PAL, 2, bg) for bg in (GRASS, ROAD, PAVE)}
        self.splat = sprite(SPLAT, SPLAT_PAL, 2, ROAD)
        self.cars = {}

    def car_sprite(self, kind, color, right):
        key = (kind, color, right)
        if key not in self.cars:
            art = TRUCK if kind else CAR
            if not right:
                art = _flip(art)
            pal = {"c": rgb(*color), "C": rgb(*_dark(color)), "w": rgb(170, 220, 255),
                   "k": rgb(10, 10, 10), "y": rgb(255, 255, 150)}
            self.cars[key] = sprite(art, pal, 2, ROAD, 8, 0)
        return self.cars[key]

    def preview(self, y):
        self.big_sprite(FROG, FROG_PAL, 6, y)
        c = self.car_sprite(0, COLORS[0], True)
        self.t.blit(c[0], 20, y + 60, c[1], c[2])
        c = self.car_sprite(1, COLORS[1], False)
        self.t.blit(c[0], 170, y + 60, c[1], c[2])

    def row_bg(self, r):
        if r == 6:
            return PAVE
        if r in LANES:
            return ROAD
        return GRASS

    def row_y(self, r):
        return Y0 + r * ROW_H

    def scene(self):
        t = self.t
        for r in range(ROWS):
            t.fill_rect(0, self.row_y(r), W, ROW_H, self.row_bg(r))
        t.fill_rect(0, Y0 + ROWS * ROW_H, W, 320 - Y0 - ROWS * ROW_H, GRASS)
        for r in (2, 3, 4, 5, 8, 9, 10, 11):
            y = self.row_y(r)
            for x in range(4, W, 24):
                t.fill_rect(x, y, 12, 1, LINE)
        random.seed(3)
        for r in (0, 12):
            for _ in range(10):
                x, y = random.randint(4, 230), self.row_y(r) + random.randint(3, 17)
                t.fill_rect(x, y, 2, 2, (GOLD, rgb(255, 120, 200), rgb(255, 255, 255))[_ % 3])
        random.seed(time.ticks_ms())

    def setup(self):
        self.scene()
        self.fc = 0
        self.level = 1
        self.make_traffic()
        self.reset_frog()

    def make_traffic(self):
        self.traffic = []
        for i, r in enumerate(LANES):
            right = i % 2 == 0
            speed = (0.8 + 0.45 * (i % 5)) * (1 + 0.12 * (self.level - 1))
            speed = min(4.0, speed)
            n = 2 if i % 3 else 1
            gap = W // n + 40
            color = COLORS[i % len(COLORS)]
            truck = 1 if i in (2, 7) else 0
            for k in range(n):
                x = k * gap + random.randint(0, 40) - (40 if truck else 28)
                self.traffic.append([float(x), r, speed if right else -speed, truck, color, None])

    def reset_frog(self):
        self.row = 12
        self.drawn = None
        self.draw_frog()

    def draw_frog(self):
        if self.drawn is not None:
            r = self.drawn
            self.t.fill_rect(PX, self.row_y(r) + 3, 16, 16, self.row_bg(r))
        spr = self.frog[self.row_bg(self.row)]
        self.t.blit(spr[0], PX, self.row_y(self.row) + 3, 16, 16)
        self.drawn = self.row

    def squash(self):
        self.sfx.tone(110, 350)
        spr = self.splat
        self.t.fill_rect(PX, self.row_y(self.row) + 3, 16, 16, ROAD)
        self.t.blit(spr[0], PX, self.row_y(self.row) + 3, spr[1], spr[2])
        time.sleep_ms(600)
        self.t.fill_rect(PX, self.row_y(self.row) + 3, 16, 16, ROAD)
        self.lives -= 1
        self.drawn = None
        self.row = 12
        if self.lives > 0:
            self.draw_frog()

    def step(self, pt, now):
        tp = self.tap(pt)
        if tp:
            fy = self.row_y(self.row) + 11
            if tp[1] < fy and self.row > 0:
                self.row -= 1
            elif tp[1] > fy + 11 and self.row < 12:
                self.row += 1
            self.sfx.tone(660, 20)
            self.draw_frog()
            if self.row == 0:
                self.score += 100 + 50 * self.level
                self.sfx.tune(((784, 70), (988, 70), (1175, 120)))
                self.level += 1
                self.text_c("NIVEAU %d" % self.level, self.row_y(0) + 7, GOLD)
                time.sleep_ms(700)
                self.scene()
                self.make_traffic()
                self.reset_frog()
                return True
        hit = False
        self.fc += 1
        for i, c in enumerate(self.traffic):
            spr = self.car_sprite(c[3], c[4], c[2] > 0)
            w = spr[1] - 16
            if (i + self.fc) & 1:
                x = int(c[0])
                if c[1] == self.row and x + 2 < PX + 14 and PX + 2 < x + w - 2:
                    hit = True
                continue
            c[0] += 2 * c[2]
            if c[2] > 0 and c[0] > W + 8:
                c[0] = -w - 8.0
            elif c[2] < 0 and c[0] < -w - 8:
                c[0] = W + 8.0
            x = int(c[0])
            if x != c[5]:
                self.put(spr, x, self.row_y(c[1]) + 4)
                c[5] = x
            if c[1] == self.row and x + 2 < PX + 14 and PX + 2 < x + w - 2:
                hit = True
        if hit:
            self.squash()
        return self.lives > 0


GAME = Road


def play(tft, touch, day):
    GAME(tft, touch, day).run()
