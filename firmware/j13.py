"""Jour 13 : CIBLES 80. Toucher les oiseaux avant qu'ils ne s'envolent (3 tirs par oiseau)."""

import random
import time

from arcade import GOLD, W, Game, overlap, rgb, sprite

SKY = rgb(70, 150, 235)
GRASS_Y = 272
PAD = 7
BW = 32
BH = 24
YMAX = GRASS_Y - 10 - BH - PAD

F1 = (
    "..........gg....",
    ".........gggg...",
    ".........ggwkoo.",
    "..ww.....gggg...",
    ".wwww...bbbb....",
    "..wwwwbbbbbbb...",
    "...bbbbbbbbbbb..",
    "...bbbbbbbbbb...",
    "....bbbbbbbb....",
    ".....oo..oo.....",
    "................",
    "................",
)
F2 = (
    "..........gg....",
    ".........gggg...",
    ".........ggwkoo.",
    ".........gggg...",
    "........bbbb....",
    "...bbbbbbbbbb...",
    "..bbbbbbbbbbbb..",
    ".wwwwbbbbbbbb...",
    "..wwww.bbbbb....",
    "...ww..oo.oo....",
    "................",
    "................",
)
HIT = tuple(reversed(F1))
BIRD_PAL = {"g": rgb(30, 160, 60), "w": rgb(255, 255, 255), "k": rgb(0, 0, 0), "o": rgb(255, 150, 20),
            "b": rgb(150, 80, 40)}


def _rev(s):
    c = list(s)
    c.reverse()
    return "".join(c)


def _flip(rows):
    return tuple(_rev(r) for r in rows)


class Cibles(Game):
    TITLE = "CIBLES 80"
    HELP = ("TOUCHE L'OISEAU", "3 TIRS PAR OISEAU", "NE LE LAISSE PAS FUIR")
    BG = SKY

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.spr = {}
        for k, art in (("r1", F1), ("r2", F2), ("h", HIT)):
            self.spr[k] = sprite(art, BIRD_PAL, 2, SKY, PAD, PAD)
        self.spr["l1"] = sprite(_flip(F1), BIRD_PAL, 2, SKY, PAD, PAD)
        self.spr["l2"] = sprite(_flip(F2), BIRD_PAL, 2, SKY, PAD, PAD)
        self.shell = sprite(("rr", "rr", "rr", "yy"), {"r": rgb(230, 40, 50), "y": GOLD}, 3, rgb(40, 110, 40))

    def preview(self, y):
        self.big_sprite(F1, BIRD_PAL, 5, y)

    def setup(self):
        t = self.t
        t.fill_rect(0, 20, W, GRASS_Y - 20, SKY)
        t.fill_rect(0, GRASS_Y, W, 320 - GRASS_Y, rgb(40, 110, 40))
        for x in range(0, W, 24):
            t.fill_rect(x, GRASS_Y - 6, 14, 6, rgb(60, 170, 60))
            t.fill_rect(x + 12, GRASS_Y - 10, 8, 10, rgb(50, 140, 50))
        self.level = 1
        self.count = 0
        self.cross = None
        self.new_bird(time.ticks_ms())

    def new_bird(self, now):
        sp = min(PAD - 1.0, 2.0 + self.level * 0.6)
        self.x = float(random.randint(20, W - 60))
        self.y = float(YMAX)
        self.vx = sp * (1 if random.random() < 0.5 else -1)
        self.vy = -sp * (0.5 + random.random() * 0.5)
        self.shots = 3
        self.mode = "fly"
        self.t_end = time.ticks_add(now, 7000)
        self.drawn = None
        self.draw_ammo()

    def draw_ammo(self):
        self.t.fill_rect(8, 294, 60, 14, rgb(40, 110, 40))
        for k in range(self.shots):
            self.t.blit(self.shell[0], 10 + k * 12, 296, self.shell[1], self.shell[2])

    def erase_bird(self):
        self.clear(int(self.x) - PAD, int(self.y) - PAD, BW + 2 * PAD, BH + 2 * PAD)

    def step(self, pt, now):
        if self.cross:
            cx, cy = self.cross
            self.clear(cx - 6, cy - 1, 13, 3)
            self.clear(cx - 1, cy - 6, 3, 13)
            self.cross = None
            self.drawn = None
        p = self.tap(pt)
        if p and self.mode == "fly" and p[1] < YMAX + BH:
            self.shots -= 1
            self.draw_ammo()
            self.sfx.tone(1400, 30)
            if overlap(p[0] - 8, p[1] - 8, 16, 16, int(self.x), int(self.y), BW, BH):
                self.mode = "fall"
                self.score += 100 * self.level + 50 * self.shots
                self.sfx.tone(300, 200)
                self.hold = time.ticks_add(now, 300)
            else:
                self.cross = p
                self.t.fill_rect(p[0] - 6, p[1], 13, 1, GOLD)
                self.t.fill_rect(p[0], p[1] - 6, 1, 13, GOLD)
                if self.shots <= 0:
                    self.mode = "flee"
        elif self.mode == "fly" and time.ticks_diff(now, self.t_end) >= 0:
            self.mode = "flee"

        if self.mode == "fly":
            self.x += self.vx
            self.y += self.vy
            if self.x < 2 or self.x > W - BW - 2:
                self.vx = -self.vx
                self.x = max(2, min(W - BW - 2, self.x))
            if self.y < 24 or self.y > YMAX:
                self.vy = -self.vy
                self.y = max(24, min(YMAX, self.y))
            if random.random() < 0.02:
                self.vy = -self.vy
            key = ("r" if self.vx > 0 else "l") + ("1" if (now // 120) & 1 else "2")
        elif self.mode == "fall":
            key = "h"
            if time.ticks_diff(now, self.hold) >= 0:
                self.y += 6
            if self.y > YMAX:
                self.erase_bird()
                self.t.fill_rect(0, GRASS_Y - 10, W, 10, SKY)
                self.repair_grass()
                return self.next_bird(now)
        else:
            self.y -= 6
            key = ("r" if self.vx > 0 else "l") + ("1" if (now // 60) & 1 else "2")
            if self.y < -BH:
                self.lives -= 1
                self.sfx.tone(150, 300)
                return self.next_bird(now) if self.lives > 0 else False
        st = (int(self.x), int(self.y), key)
        if st != self.drawn:
            self.put(self.spr[key], st[0], st[1])
            self.drawn = st
        return True

    def repair_grass(self):
        t = self.t
        for x in range(0, W, 24):
            t.fill_rect(x, GRASS_Y - 6, 14, 6, rgb(60, 170, 60))
            t.fill_rect(x + 12, GRASS_Y - 10, 8, 10, rgb(50, 140, 50))

    def next_bird(self, now):
        self.count += 1
        if self.count % 5 == 0:
            self.level += 1
        self.new_bird(now)
        return True

    def bot(self, n):
        if not hasattr(self, "mode"):
            return (120, 160) if n % 4 < 2 else None
        if n % 6 >= 3:
            return None
        return (int(self.x) + 16 + (n % 3) * 20 - 20, int(self.y) + 12)


GAME = Cibles


def play(tft, touch, day):
    GAME(tft, touch, day).run()
