"""Jour 17 : SAUTEUR 80. Rebonds automatiques, le doigt dirige, la hauteur fait le score."""

import random
import time

from arcade import GOLD, H, W, Game, overlap, rgb, sprite

SKY = rgb(8, 10, 36)
STAR = rgb(210, 214, 240)
STAR2 = rgb(90, 96, 140)
FP = 256
PX = 3
PY = 12
HX = 8
HY = 9
PW = 32
PH = 6
HW = 16
HH = 20
MAXP = 9
GRAV = 88
JUMP = -9 * FP
SPRING = -12 * FP
VMAX = 9 * FP
STEER = 8
SCROLL = 140

HERO = (
    "...ww...",
    "..wyyw..",
    "..wywy..",
    "..yyyy..",
    "...cc...",
    "..cccc..",
    ".cc..cc.",
    "..b..b..",
    "..b..b..",
    ".bb..bb.",
)
HERO_PAL = {"w": rgb(240, 80, 40), "y": rgb(250, 200, 150), "c": rgb(40, 170, 230),
            "b": rgb(40, 50, 90)}
BAR = (
    "gggggggggggggggg",
    "gGggggggggggggGg",
    "GGGGGGGGGGGGGGGG",
)
PALS = (
    {"g": rgb(40, 200, 80), "G": rgb(20, 130, 50)},
    {"g": rgb(40, 180, 230), "G": rgb(20, 90, 160)},
    {"g": rgb(180, 110, 50), "G": rgb(120, 60, 30)},
    {"g": rgb(240, 210, 40), "G": rgb(200, 140, 20)},
)


class Sauteur(Game):
    TITLE = "SAUTEUR 80"
    HELP = ("LE DOIGT DIRIGE", "REBONDIS SUR LES BARRES", "NE TOMBE PAS")
    BG = SKY

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.hero = sprite(HERO, HERO_PAL, 2, SKY, HX, HY)
        self.pspr = [sprite(BAR, pal, 2, SKY, PX, PY) for pal in PALS]

    def preview(self, y):
        t = self.t
        t.fill_rect(0, y, W, 95, SKY)
        for k in range(6):
            t.fill_rect((k * 97) % 230 + 4, y + 6 + (k * 17) % 80, 1, 1, STAR)
        t.fill_rect(28, y + 78, PW, PH, rgb(40, 200, 80))
        t.fill_rect(92, y + 48, PW, PH, rgb(40, 180, 230))
        t.fill_rect(158, y + 70, PW, PH, rgb(240, 210, 40))
        self.put(self.hero, 108, y + 26)

    def setup(self):
        self.t.fill_rect(0, 20, W, 300, SKY)
        self.stars = []
        for i in range(7):
            sx = 10 + i * 32
            sy = 32 + (i * 53) % 260
            self.stars.append((sx, sy))
            self.t.fill_rect(sx, sy, 1, 1, STAR)
        self.plats = []
        y = 292
        self.add_plat((W - PW) // 2, y, 0)
        for _ in range(8):
            y -= random.randint(28, 40)
            self.add_plat(None, y, None)
        self.hx = (W - HW) // 2
        self.ox = self.hx
        self.hy = 292 - HH
        self.oy = self.hy
        self.fy = self.hy * FP
        self.vy = JUMP
        self.tx = self.hx
        self.n = 0
        self.full = True

    def kind_roll(self):
        r = random.randint(0, 11)
        if self.score > 700:
            if r < 3:
                return 0
            if r < 7:
                return 1
            if r < 10:
                return 2
            return 3
        if r < 7:
            return 0
        if r < 9:
            return 1
        if r < 11:
            return 2
        return 3

    def add_plat(self, x, y, kind):
        if kind is None:
            kind = self.kind_roll()
            nb = 0
            for p in self.plats:
                if p[2] == 2:
                    nb += 1
            if kind == 2 and nb > 3:
                kind = 0
        if x is None:
            x = random.randint(PX, W - PW - PX)
        vx = 0
        if kind == 1:
            vx = 2 if random.getrandbits(1) else -2
        self.plats.append([x, y, kind, vx])
        if y < H and y + PH > 20:
            self.put(self.pspr[kind], x, y)

    def spawn_top(self):
        if len(self.plats) >= MAXP:
            return
        top = 320
        for p in self.plats:
            if p[1] < top:
                top = p[1]
        gap = random.randint(28, 44)
        if self.score > 500:
            gap = random.randint(32, 52)
        self.add_plat(None, top - gap, None)

    def wipe(self, p):
        k = p[2]
        if k > 3:
            k = 2
        spr = self.pspr[k]
        self.clear(p[0] - PX, p[1] - PY, spr[1], spr[2])

    def land(self, p):
        k = p[2]
        self.fy = (p[1] - HH) * FP
        self.hy = p[1] - HH
        self.vy = SPRING if k == 3 else JUMP
        if k == 3:
            self.sfx.tone(988, 40)
        else:
            self.sfx.tone(660 if k else 523, 30)
        if k == 2:
            self.wipe(p)
            return True
        return False

    def die(self):
        self.lives -= 1
        self.sfx.tone(90, 400)
        self.t.fill_rect(self.hx - 2, min(300, self.hy), HW + 4, 8, GOLD)
        time.sleep_ms(350)
        if self.lives <= 0:
            return False
        self.setup()
        self.vy = JUMP
        return True

    def step(self, pt, now):
        self.n += 1
        if pt:
            self.tx = pt[0] - HW // 2
        d = self.tx - self.hx
        if d > STEER:
            d = STEER
        elif d < -STEER:
            d = -STEER
        nx = self.hx + d
        if nx < HX:
            nx = HX
        elif nx > W - HW - HX:
            nx = W - HW - HX
        self.ox = self.hx
        self.hx = nx
        self.vy += GRAV
        if self.vy > VMAX:
            self.vy = VMAX
        self.fy += self.vy
        hy = self.fy >> 8
        dy = 0
        if hy < SCROLL and self.vy < 0:
            dy = SCROLL - hy
            hy = SCROLL
            self.fy = SCROLL * FP
            self.score += dy
        self.oy = self.hy
        self.hy = hy
        if hy > 304:
            return self.die()
        feet = hy + HH
        ofeet = self.oy + HH
        i = 0
        plats = self.plats
        while i < len(plats):
            p = plats[i]
            if dy:
                p[1] += dy
            if p[2] == 1:
                p[0] += p[3]
                if p[0] < PX or p[0] > W - PW - PX:
                    p[3] = -p[3]
                    p[0] += p[3]
            if p[1] > 314:
                self.wipe(p)
                plats.pop(i)
                self.spawn_top()
                continue
            if self.vy > 0 and ofeet <= p[1] + 4 and feet >= p[1] and feet <= p[1] + 14:
                if self.hx + 2 < p[0] + PW and self.hx + HW - 2 > p[0]:
                    if self.land(p):
                        plats.pop(i)
                        self.spawn_top()
                        continue
            i += 1
        dx0 = self.hx if self.hx < self.ox else self.ox
        dy0 = self.hy if self.hy < self.oy else self.oy
        dw = HW + HX * 2 + abs(self.hx - self.ox)
        dh = HH + HY * 2 + abs(self.hy - self.oy)
        hx0 = dx0 - HX
        hy0 = dy0 - HY
        full = self.full or dy
        self.full = False
        st = self.stars
        if st and not full:
            sx, sy = st[self.n % 7]
            if not (hx0 <= sx < hx0 + dw and hy0 <= sy < hy0 + dh):
                self.t.fill_rect(sx, sy, 1, 1, STAR if (self.n >> 4) & 1 else STAR2)
        for p in plats:
            if full or p[2] == 1 or overlap(p[0] - PX, p[1] - PY, PW + 2 * PX, PH + 2 * PY,
                                            hx0, hy0, dw, dh):
                self.put(self.pspr[p[2]], p[0], p[1])
        self.put(self.hero, self.hx, self.hy)
        return True

    def bot(self, n):
        if not hasattr(self, "plats"):
            return (120, 160) if n % 4 < 2 else None
        hy = self.hy
        vy = self.vy
        if vy < 0:
            v = -vy
            hy = hy - (v * v) // (2 * GRAV * FP)
        feet = hy + HH
        best = None
        bd = 1000
        for p in self.plats:
            d = p[1] - feet
            if d < -6:
                continue
            if d < bd:
                bd = d
                best = p
        if best is None:
            return (self.hx + HW // 2, 200)
        tx = best[0] + PW // 2 + best[3] * 6
        if tx < 8:
            tx = 8
        elif tx > 231:
            tx = 231
        return (tx, 200)


GAME = Sauteur


def play(tft, touch, day):
    GAME(tft, touch, day).run()
