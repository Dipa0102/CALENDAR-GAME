"""Jour 9 : TURBO 80. Course vue de dessus : doubler sans toucher les autres voitures."""

import random
import time

from arcade import GOLD, W, Game, overlap, rgb, sprite

ROAD = rgb(60, 60, 70)
GRASS = rgb(40, 140, 50)
RX0 = 36
RX1 = 204
LANE = (RX1 - RX0) // 3
VMAX = 10
PY = 250
PVX = 7
DASH_GAP = 64
BUSH_GAP = 160

CAR = (
    "..yccccy..",
    ".cccccccc.",
    "kcCwwwwCck",
    "kcwwwwwwck",
    ".cccccccc.",
    ".cCccccCc.",
    ".cCccccCc.",
    ".cCccccCc.",
    ".cccccccc.",
    "kcwwwwwwck",
    "kcCwwwwCck",
    ".cccccccc.",
    ".rccccccr.",
)
BUSH = ("..gggg..", ".gGggGg.", "gGgggggg", "ggggGgGg", "gGgggggg", ".gggGgg.", "..gggg..")
BUSH_PAL = {"g": rgb(30, 100, 40), "G": rgb(110, 210, 90)}
TRAFFIC = ((60, 120, 255), (255, 200, 40), (180, 60, 220), (40, 200, 200), (255, 255, 255))


def _car_pal(c):
    return {"c": rgb(*c), "C": rgb(c[0] // 2, c[1] // 2, c[2] // 2), "w": rgb(40, 50, 80),
            "k": rgb(10, 10, 10), "y": rgb(255, 255, 180), "r": rgb(255, 40, 40)}


class Turbo(Game):
    TITLE = "TURBO 80"
    HELP = ("GLISSE LE DOIGT POUR", "CHANGER DE FILE", "NE TOUCHE PERSONNE")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.me = sprite(CAR, _car_pal((230, 40, 50)), 2, ROAD, PVX, 0)
        self.others = [sprite(CAR, _car_pal(c), 2, ROAD, 0, VMAX) for c in TRAFFIC]
        self.dash = sprite(("ww",) * 10, {"w": rgb(230, 230, 230)}, 2, ROAD, 0, VMAX)
        self.bush = sprite(BUSH, BUSH_PAL, 2, GRASS, 0, VMAX)

    def preview(self, y):
        self.big_sprite(CAR, _car_pal((230, 40, 50)), 3, y)

    def setup(self):
        t = self.t
        t.fill_rect(0, 20, RX0 - 6, 300, GRASS)
        t.fill_rect(RX1 + 6, 20, W - RX1 - 6, 300, GRASS)
        t.fill_rect(RX0, 20, RX1 - RX0, 300, ROAD)
        for y in range(20, 320, 16):
            c = rgb(230, 40, 40) if (y // 16) & 1 else rgb(240, 240, 240)
            t.fill_rect(RX0 - 6, y, 6, 16, c)
            t.fill_rect(RX1, y, 6, 16, c)
        self.x = RX0 + LANE + (LANE - 20) // 2
        self.target = self.x
        self.speed = 4.0
        self.phase = 0.0
        self.dist = 0.0
        self.cars = []
        self.next_car = time.ticks_add(time.ticks_ms(), 800)
        self.t0 = time.ticks_ms()
        self.inv_until = 0

    def crash(self, now):
        self.lives -= 1
        self.sfx.tone(100, 400)
        for k in range(4):
            self.t.fill_rect(self.x, PY, 20, 26, GOLD if k % 2 == 0 else ROAD)
            time.sleep_ms(90)
        for c in self.cars:
            self.clear(c[0], int(c[1]) - VMAX, 20, 26 + 2 * VMAX, ROAD)
        self.cars = []
        self.speed = max(4.0, self.speed - 2)
        self.inv_until = time.ticks_add(now, 1200)

    def step(self, pt, now):
        el = time.ticks_diff(now, self.t0)
        self.speed = min(9.0, self.speed + 0.004)
        v = self.speed
        self.phase += v
        self.dist += v
        self.score = int(self.dist) // 4

        ph = self.phase % DASH_GAP
        for lx in (RX0 + LANE - 2, RX0 + 2 * LANE - 2):
            for k in range(7):
                self.put(self.dash, lx, int(ph) - DASH_GAP + k * DASH_GAP)
        pb = self.phase % BUSH_GAP
        for k in range(3):
            y = int(pb) - BUSH_GAP + k * BUSH_GAP
            self.put(self.bush, 6, y)
            self.put(self.bush, W - 22, y + BUSH_GAP // 2)

        if time.ticks_diff(now, self.next_car) >= 0 and len(self.cars) < 4:
            lane = random.randint(0, 2)
            if not any(c[3] == lane and c[1] < 60 for c in self.cars):
                x = RX0 + lane * LANE + (LANE - 20) // 2
                rv = min(VMAX, 1.5 + random.random() * 2 + v * 0.3)
                self.cars.append([x, -10.0, rv, lane, random.randint(0, len(self.others) - 1)])
            self.next_car = time.ticks_add(now, max(350, 1100 - el // 60))
        keep = []
        hit = False
        for c in self.cars:
            c[1] += c[2]
            y = int(c[1])
            if y > 330:
                continue
            self.put(self.others[c[4]], c[0], y)
            if overlap(c[0] + 2, y + 2, 16, 22, self.x + 3, PY + 2, 14, 22):
                hit = True
            keep.append(c)
        self.cars = keep

        if pt:
            self.target = pt[0] - 10
        d = max(-PVX, min(PVX, self.target - self.x))
        self.x = max(RX0 + 2, min(RX1 - 22, self.x + d))
        if time.ticks_diff(self.inv_until, now) > 0 and (now // 100) % 2:
            self.clear(self.x - PVX, PY, 20 + 2 * PVX, 26, ROAD)
        else:
            self.put(self.me, self.x, PY)
        if hit and time.ticks_diff(self.inv_until, now) <= 0:
            self.crash(now)
        return self.lives > 0


GAME = Turbo


def play(tft, touch, day):
    GAME(tft, touch, day).run()
