"""Jour 8 : BOMB DODGE. Esquiver les bombes, ramasser les pieces.
La classe Fall sert aussi au jour 21 (Crystal Catch)."""

import random
import time

from arcade import W, Game, overlap, rgb, sprite

SKY = rgb(20, 16, 50)
GROUND_Y = 304
PLAYER_Y = 272
PVX = 9
VMAX = 7

HERO = (
    "...kkkk...",
    "..kyyyyk..",
    "..kywywk..",
    "..kyyyyk..",
    "...kkkk...",
    ".rrrrrrrr.",
    "rrRrrrrRrr",
    "s.rrrrrr.s",
    "..bbbbbb..",
    "..bb..bb..",
    "..bb..bb..",
    ".kkk..kkk.",
)
HERO_PAL = {"k": rgb(30, 20, 20), "y": rgb(250, 200, 150), "w": rgb(20, 20, 20), "r": rgb(230, 50, 60),
            "R": rgb(150, 30, 40), "s": rgb(250, 200, 150), "b": rgb(50, 80, 200)}
BOMB = ("....yo..", "...k.o..", "..kkk...", ".kkwkkk.", "kkwkkkkk", "kkkkkkkk", ".kkkkkk.", "..kkkk..")
BOMB_PAL = {"k": rgb(40, 40, 60), "w": rgb(200, 200, 230), "y": rgb(255, 230, 60), "o": rgb(255, 120, 30)}
COIN = (".yyyy.", "yYwwYy", "yYwYYy", "yYwYYy", "yYYYYy", ".yyyy.")
COIN_PAL = {"y": rgb(255, 180, 20), "Y": rgb(255, 230, 80), "w": rgb(255, 255, 220)}
BOOM = ("..o.o...", ".oyoyo..", "oyywyyo.", ".oyyyo..", "o.oyo.o.")
BOOM_PAL = {"o": rgb(255, 110, 30), "y": rgb(255, 230, 60), "w": rgb(255, 255, 255)}


class Fall(Game):
    """Le joueur suit le doigt en bas de l'ecran ; des objets tombent du ciel."""

    BG = SKY
    PLAYER = HERO
    PLAYER_PAL = HERO_PAL
    # (art, palette, points, mauvais ?)
    ITEMS = ((BOMB, BOMB_PAL, 10, True), (COIN, COIN_PAL, 50, False))
    GOOD_RATE = 3

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.hero = sprite(self.PLAYER, self.PLAYER_PAL, 2, SKY, PVX, 0)
        self.items = [(sprite(a, p, 2, SKY, 0, VMAX), pts, bad) for a, p, pts, bad in self.ITEMS]
        self.boom = sprite(BOOM, BOOM_PAL, 2, SKY)
        self.pw = self.hero[1] - 2 * PVX
        self.ph = self.hero[2]

    def preview(self, y):
        self.big_sprite(self.PLAYER, self.PLAYER_PAL, 4, y)
        for i, (spr, _p, _b) in enumerate(self.items[:3]):
            self.t.blit(spr[0], 30 + i * 150 // max(1, len(self.items) - 1), y + 10, spr[1], spr[2])

    def scenery(self):
        t = self.t
        t.fill_rect(0, GROUND_Y, W, 320 - GROUND_Y, rgb(70, 50, 40))
        t.fill_rect(0, GROUND_Y, W, 3, rgb(90, 200, 80))
        for x in range(6, W, 20):
            t.fill_rect(x, GROUND_Y + 7, 8, 3, rgb(95, 70, 55))

    def setup(self):
        self.scenery()
        self.x = (W - self.pw) // 2
        self.target = self.x
        self.objs = []
        self.booms = []
        self.t_start = time.ticks_ms()
        self.next_drop = 0
        self.combo = 0

    def level(self, now):
        return time.ticks_diff(now, self.t_start) // 15000

    def spawn(self, now):
        lv = self.level(now)
        k = 1 if random.randint(0, self.GOOD_RATE) == 0 else 0
        if len(self.items) > 2 and k == 1:
            k = random.randint(1, len(self.items) - 1)
        spr = self.items[k][0]
        x = random.randint(4, W - spr[1] - 4)
        v = min(VMAX, 2.5 + lv * 0.6 + random.random() * 1.5)
        self.objs.append([x, float(20 - spr[2] + VMAX), v, k])
        self.next_drop = time.ticks_add(now, max(180, 700 - lv * 90))

    def on_item(self, obj, now):
        spr, pts, bad = self.items[obj[3]]
        if bad:
            self.lives -= 1
            self.combo = 0
            self.sfx.tone(90, 300)
            self.explode(obj[0], PLAYER_Y + 4, now)
        else:
            self.combo += 1
            self.score += pts * min(5, 1 + self.combo // 5)
            self.sfx.tone(1200 + 60 * min(10, self.combo), 40)

    def on_ground(self, obj, now):
        spr, pts, bad = self.items[obj[3]]
        if bad:
            self.score += pts
            self.explode(obj[0], GROUND_Y - 10, now)
        else:
            self.combo = 0

    def explode(self, x, y, now):
        self.put(self.boom, x, y)
        self.booms.append((x, y, time.ticks_add(now, 160)))

    def step(self, pt, now):
        if pt:
            self.target = pt[0] - self.pw // 2
        d = max(-PVX, min(PVX, self.target - self.x))
        self.x = max(0, min(W - self.pw, self.x + d))
        if time.ticks_diff(now, self.next_drop) >= 0 and len(self.objs) < 9:
            self.spawn(now)
        keep = []
        for o in self.objs:
            spr = self.items[o[3]][0]
            o[1] += o[2]
            y = int(o[1])
            h = spr[2] - 2 * VMAX
            if overlap(o[0] + 2, y + 2, spr[1] - 4, h - 4, self.x + 2, PLAYER_Y + 2, self.pw - 4, self.ph - 4):
                self.clear(o[0], y - VMAX, spr[1], spr[2])
                self.on_item(o, now)
                continue
            if y + h >= GROUND_Y:
                self.clear(o[0], y - VMAX, spr[1], GROUND_Y - y + VMAX)
                self.on_ground(o, now)
                continue
            self.put(spr, o[0], y)
            keep.append(o)
        self.objs = keep
        self.put(self.hero, self.x, PLAYER_Y)
        keep = []
        for b in self.booms:
            if time.ticks_diff(now, b[2]) > 0:
                self.clear(b[0], b[1], self.boom[1], self.boom[2])
            else:
                keep.append(b)
        self.booms = keep
        return self.lives > 0


class BombDodge(Fall):
    TITLE = "BOMB DODGE"
    HELP = ("GLISSE LE DOIGT", "EVITE LES BOMBES", "RAMASSE LES PIECES")


GAME = BombDodge


def play(tft, touch, day):
    GAME(tft, touch, day).run()
