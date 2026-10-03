"""Jour 3 : SERPENT 80. Le serpent part vers le doigt ; manger sans se mordre."""

import random
import time

from arcade import GOLD, PINK, W, Game, rgb, sprite

CELL = 12
COLS = 20
ROWS = 24
FY = 26
TILE_A = rgb(16, 24, 20)
TILE_B = rgb(22, 32, 26)

BODY = (".gggg.", "gGhhGg", "gGGGGg", "gGGGGg", "gGGGGg", ".gggg.")
HEAD = (".gggg.", "gGGGGg", "gwGGwg", "gkGGkg", "gGrrGg", ".gggg.")
SNAKE_PAL = {"g": rgb(20, 110, 40), "G": rgb(70, 220, 90), "h": rgb(190, 255, 170),
             "w": rgb(255, 255, 255), "k": rgb(0, 0, 0), "r": rgb(240, 40, 60)}
APPLE = ("...G..", "..G...", ".rrrr.", "rwrrrr", "rrrrrR", ".rRRR.")
APPLE_PAL = {"G": rgb(60, 200, 60), "r": rgb(235, 40, 50), "R": rgb(150, 20, 30), "w": rgb(255, 200, 200)}
STAR = ("..yy..", ".yYYy.", "yYwYYy", "yYYYYy", ".yYYy.", "..yy..")
STAR_PAL = {"y": rgb(255, 170, 20), "Y": rgb(255, 230, 60), "w": rgb(255, 255, 255)}

DIRS = ((1, 0), (0, 1), (-1, 0), (0, -1))


class Snake(Game):
    TITLE = "SERPENT 80"
    HELP = ("POSE LE DOIGT : LE SERPENT", "VA VERS TON DOIGT")
    LIVES = 1

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.spr = {}
        for name, art, pal in (("body", BODY, SNAKE_PAL), ("head", HEAD, SNAKE_PAL),
                               ("apple", APPLE, APPLE_PAL), ("star", STAR, STAR_PAL)):
            self.spr[name] = (sprite(art, pal, 2, TILE_A), sprite(art, pal, 2, TILE_B))

    def preview(self, y):
        for i in range(6):
            spr = self.spr["head" if i == 5 else "body"][0]
            self.t.blit(spr[0], 72 + i * 14, y + 40, 12, 12)
        a = self.spr["apple"][0]
        self.t.blit(a[0], 160, y + 40, 12, 12)
        self.big_sprite(HEAD, SNAKE_PAL, 6, y)

    def tile(self, c, r):
        return TILE_A if (c + r) & 1 == 0 else TILE_B

    def draw(self, name, c, r):
        spr = self.spr[name][(c + r) & 1]
        self.t.blit(spr[0], c * CELL, FY + r * CELL, CELL, CELL)

    def erase(self, c, r):
        self.t.fill_rect(c * CELL, FY + r * CELL, CELL, CELL, self.tile(c, r))

    def setup(self):
        t = self.t
        t.fill_rect(0, FY, W, ROWS * CELL, TILE_A)
        for r in range(ROWS):
            for c in range((r & 1) ^ 1, COLS, 2):
                t.fill_rect(c * CELL, FY + r * CELL, CELL, CELL, TILE_B)
        t.fill_rect(0, FY - 3, W, 2, PINK)
        t.fill_rect(0, FY + ROWS * CELL + 1, W, 2, PINK)
        self.body = [(8, 12), (9, 12), (10, 12)]
        for c, r in self.body[:-1]:
            self.draw("body", c, r)
        self.draw("head", 10, 12)
        self.cells = set(self.body)
        self.apple = None
        self.want = None
        self.dir = 0
        self.grow = 0
        self.eaten = 0
        self.delay = 150
        self.next = time.ticks_ms()
        self.star = None
        self.place_apple()

    def free_cell(self):
        while True:
            c, r = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
            if (c, r) not in self.cells and (c, r) != self.apple:
                return c, r

    def place_apple(self):
        self.apple = self.free_cell()
        self.draw("apple", *self.apple)

    def steer(self, pt):
        hc, hr = self.body[-1]
        dx = pt[0] - (hc * CELL + CELL // 2)
        dy = pt[1] - (FY + hr * CELL + CELL // 2)
        if abs(dx) < CELL and abs(dy) < CELL:
            return
        want = (0 if dx > 0 else 2) if abs(dx) > abs(dy) else (1 if dy > 0 else 3)
        if want != (self.dir + 2) % 4:
            self.want = want

    def step(self, pt, now):
        if pt:
            self.steer(pt)
        if time.ticks_diff(now, self.next) < 0:
            return True
        self.next = time.ticks_add(now, self.delay)
        if self.want is not None and self.want != (self.dir + 2) % 4:
            self.dir = self.want
        hc, hr = self.body[-1]
        dc, dr = DIRS[self.dir]
        nc, nr = hc + dc, hr + dr
        if not (0 <= nc < COLS and 0 <= nr < ROWS) or ((nc, nr) in self.cells and (nc, nr) != self.body[0]):
            self.sfx.tone(110, 400)
            self.flash()
            return False
        if self.grow:
            self.grow -= 1
        else:
            tail = self.body.pop(0)
            self.cells.discard(tail)
            if tail != (nc, nr):
                self.erase(*tail)
        self.draw("body", hc, hr)
        self.body.append((nc, nr))
        self.cells.add((nc, nr))
        self.draw("head", nc, nr)
        if (nc, nr) == self.apple:
            self.eaten += 1
            self.grow += 2
            self.score += 10 * (1 + len(self.body) // 6)
            self.delay = max(70, self.delay - 4)
            self.sfx.tone(880, 40)
            self.place_apple()
            if self.eaten % 5 == 0 and self.star is None:
                sc, sr = self.free_cell()
                self.star = (sc, sr, time.ticks_add(now, 5000))
                self.draw("star", sc, sr)
        if self.star:
            sc, sr, until = self.star
            if (nc, nr) == (sc, sr):
                self.score += 100
                self.sfx.tune(((1047, 40), (1319, 60)))
                self.star = None
            elif time.ticks_diff(now, until) > 0:
                if (sc, sr) not in self.cells:
                    self.erase(sc, sr)
                self.star = None
        return True

    def flash(self):
        for c, r in self.body:
            self.t.fill_rect(c * CELL + 3, FY + r * CELL + 3, 6, 6, GOLD)
        time.sleep_ms(500)

GAME = Snake


def play(tft, touch, day):
    GAME(tft, touch, day).run()
