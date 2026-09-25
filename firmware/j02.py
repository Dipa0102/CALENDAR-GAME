"""Jour 2 : STAR RAID, tir vertical. Le vaisseau suit le doigt et tire tout seul."""

import random
import time

from arcade import BLACK, CYAN, GOLD, HUD, W, Game, overlap, rgb, sprite

SHIP = (
    "......w......",
    ".....wcw.....",
    ".....cCc.....",
    "....cCwCc....",
    "...ccCCCcc...",
    ".r.cCCCCCc.r.",
    ".rccCbbbCccr.",
    "rrcCCbbbCCcrr",
    "rcCCCCCCCCCcr",
    "..oo.....oo..",
    "...o.....o...",
)
SHIP_PAL = {"w": rgb(255, 255, 255), "c": CYAN, "C": rgb(40, 90, 230), "b": rgb(10, 20, 90),
            "r": rgb(240, 50, 70), "o": rgb(255, 170, 30)}
ENEMIES = (
    ((
        "....ppp....",
        "..ppwwppp..",
        ".pppppppppp",
        "yPyPyPyPyPy",
        ".PPPPPPPPP.",
        "..P.....P..",
    ), {"p": rgb(255, 80, 200), "P": rgb(150, 30, 140), "w": rgb(255, 255, 255), "y": rgb(255, 230, 60)}, 100),
    ((
        ".g.......g.",
        "..g.....g..",
        "..ggggggg..",
        ".gGwgggwGg.",
        "ggGGgggGGgg",
        "g.ggggggg.g",
        "..g.g.g.g..",
    ), {"g": rgb(80, 230, 90), "G": rgb(20, 120, 40), "w": rgb(255, 255, 255)}, 150),
    ((
        ".....o.....",
        "....ooo....",
        "...oOwOo...",
        "..oOOwOOo..",
        ".oOOOOOOOo.",
        "..oOOrOOo..",
        "...oOOOo...",
        "....ooo....",
        ".....o.....",
    ), {"o": rgb(255, 170, 40), "O": rgb(200, 80, 20), "w": rgb(255, 255, 200), "r": rgb(255, 40, 40)}, 200),
)
BOOM = (
    "y...o...y",
    ".y.ooo.y.",
    "..ooyoo..",
    ".oyywyyo.",
    "ooywwwyoo",
    ".oyywyyo.",
    "..ooyoo..",
    ".y.ooo.y.",
    "y...o...y",
)
BOOM_PAL = {"y": rgb(255, 230, 60), "o": rgb(255, 120, 30), "w": rgb(255, 255, 255)}

SHIP_Y = 282
SW = 26
SH = 22
EW = 22
EH = 18
EP = 6
SHOT_V = 10
BOMB_V = 5


class StarRaid(Game):
    TITLE = "STAR RAID"
    HELP = ("GLISSE LE DOIGT", "LE VAISSEAU TIRE TOUT SEUL")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.ship = sprite(SHIP, SHIP_PAL, 2, BLACK, 7, 0)
        self.foes = [(sprite(r, p, 2, BLACK, EP, EP), v) for r, p, v in ENEMIES]
        self.boom = sprite(BOOM, BOOM_PAL, 2, BLACK, 5, 5)
        self.shot = sprite(("cc", "cc", "ww", "ww", "cc", "cc"), {"c": CYAN, "w": rgb(255, 255, 255)}, 1, BLACK, 0, SHOT_V)
        self.bomb = sprite(("oyo", "yyy", "oyo", ".o."), {"o": rgb(255, 120, 30), "y": GOLD}, 1, BLACK, 0, BOMB_V)

    def preview(self, y):
        self.big_sprite(SHIP, SHIP_PAL, 4, y + 24)
        for i in range(3):
            spr = self.foes[i][0]
            self.t.blit(spr[0], 30 + i * 70, y, spr[1], spr[2])

    def setup(self):
        self.sx = (W - SW) // 2
        self.target = self.sx
        self.shots = []
        self.bombs = []
        self.booms = []
        self.stars = [(random.randint(0, W - 1), random.randint(HUD + 2, 270)) for _ in range(14)]
        for x, y in self.stars:
            self.t.fill_rect(x, y, 1, 1, rgb(160, 160, 220))
        self.frame = 0
        self.wave = 0
        self.inv_until = 0
        self.next_shot = 0
        self.new_wave()

    def new_wave(self):
        self.wave += 1
        self.rows = 3 if self.wave < 3 else 4
        # [x, y, type, vx de plongee (0 = en formation), dessine x, dessine y]
        self.foe = []
        for r in range(self.rows):
            kind = (r + self.wave) % 3
            for c in range(5):
                self.foe.append([16 + c * 40, HUD + 14 + r * 30, kind, 0, None, None, r])
        self.dir = 1
        self.step_px = 2 if self.wave < 4 else 3
        self.drop = False

    def hit_ship(self, now):
        if time.ticks_diff(self.inv_until, now) > 0:
            return
        self.lives -= 1
        self.sfx.tone(120, 300)
        self.booms.append([self.sx + 4, SHIP_Y + 2, now])
        self.inv_until = time.ticks_add(now, 1500)

    def kill(self, e, now):
        self.clear(e[4] - EP, e[5] - EP, EW + 2 * EP, EH + 2 * EP)
        self.score += self.foes[e[2]][1] * (2 if e[3] else 1)
        self.booms.append([e[4] + 2, e[5], now])
        self.sfx.tone(220, 60)

    def step(self, pt, now):
        t = self.t
        self.frame += 1
        x, y = self.stars[self.frame % len(self.stars)]
        t.fill_rect(x, y, 1, 1, rgb(90, 90, 140) if self.frame & 16 else rgb(220, 220, 255))

        if pt:
            self.target = pt[0] - SW // 2
        d = self.target - self.sx
        d = 7 if d > 7 else (-7 if d < -7 else d)
        self.sx = max(0, min(W - SW, self.sx + d))
        if time.ticks_diff(self.inv_until, now) > 0 and (now // 100) % 2:
            self.clear(self.sx - 7, SHIP_Y, SW + 14, SH)
        else:
            self.put(self.ship, self.sx, SHIP_Y)

        if time.ticks_diff(now, self.next_shot) >= 0 and len(self.shots) < 4:
            self.next_shot = time.ticks_add(now, 200)
            self.shots.append([self.sx + 12, SHIP_Y - 6 + SHOT_V, SHIP_Y - 6])
            self.sfx.tone(1400, 15)

        # La formation avance une rangee par image, facon borne d'arcade.
        row = self.frame % self.rows
        if row == 0:
            xs = [e[0] for e in self.foe if not e[3]]
            if xs and ((self.dir > 0 and max(xs) > W - EW - 6) or (self.dir < 0 and min(xs) < 6)):
                self.dir = -self.dir
                self.drop = True
            elif self.drop:
                self.drop = False
        divers = 0
        for e in self.foe:
            if e[3]:
                divers += 1
                e[0] += e[3]
                e[1] += 3
                if e[0] < 2 or e[0] > W - EW - 2:
                    e[3] = -e[3]
            elif e[6] == row:
                e[0] += self.dir * self.step_px * self.rows // 2
                if self.drop:
                    e[1] += 6

        alive = []
        for e in self.foe:
            ex, ey = int(e[0]), int(e[1])
            if not e[3] and divers < 2 and e[6] == row and random.getrandbits(9) < self.wave:
                e[3] = 2 if self.sx > ex else -2
                divers += 1
            hit = False
            for s in self.shots:
                if overlap(s[0], s[1], 2, 6, ex, ey, EW, EH):
                    s[1] = -99
                    hit = True
                    break
            if hit:
                e[4], e[5] = ex, ey
                self.kill(e, now)
                continue
            if ey > 300:
                self.clear(ex - EP, ey - EP, EW + 2 * EP, EH + 2 * EP)
                continue
            if overlap(ex + 2, ey + 2, EW - 4, EH - 6, self.sx + 3, SHIP_Y + 3, SW - 6, SH - 6):
                self.clear(ex - EP, ey - EP, EW + 2 * EP, EH + 2 * EP)
                self.hit_ship(now)
                continue
            if (ex, ey) != (e[4], e[5]):
                self.put(self.foes[e[2]][0], ex, ey)
                e[4], e[5] = ex, ey
            if len(self.bombs) < 3 and random.getrandbits(10) < 2 + self.wave:
                self.bombs.append([ex + 10, ey + EH])
            alive.append(e)
        self.foe = alive

        keep = []
        for s in self.shots:
            if s[1] < 0 or s[1] - SHOT_V < HUD:
                self.clear(s[0], s[2], 2, 6)
                continue
            s[1] -= SHOT_V
            self.put(self.shot, s[0], s[1])
            s[2] = s[1]
            keep.append(s)
        self.shots = keep

        keep = []
        for b in self.bombs:
            b[1] += BOMB_V
            if b[1] >= 316:
                self.clear(b[0], b[1] - BOMB_V, 3, 10)
                continue
            if overlap(b[0], b[1], 3, 4, self.sx + 5, SHIP_Y + 4, SW - 10, SH - 6):
                self.clear(b[0], b[1] - BOMB_V, 3, 10)
                self.hit_ship(now)
                continue
            self.put(self.bomb, b[0], b[1])
            keep.append(b)
        self.bombs = keep

        keep = []
        for b in self.booms:
            if time.ticks_diff(now, b[2]) > 200:
                self.clear(b[0] - 5, b[1] - 5, 28, 28)
            else:
                if len(b) == 3:
                    self.put(self.boom, b[0], b[1])
                    b.append(1)
                keep.append(b)
        self.booms = keep

        if not self.foe:
            self.score += 500 * self.wave
            self.text_c("VAGUE %d" % (self.wave + 1), 150, GOLD, 2)
            self.sfx.tune(((660, 80), (880, 120)))
            time.sleep_ms(600)
            self.clear(0, 150, W, 18)
            self.new_wave()
        return self.lives > 0


GAME = StarRaid


def play(tft, touch, day):
    GAME(tft, touch, day).run()
