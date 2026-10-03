"""Jour 14 : DEFENSEUR. Vaisseau a gauche, landers qui emportent les humains."""

import random
import time

from arcade import BLACK, GOLD, HUD, PINK, W, WHITE, Game, overlap, rgb, sprite
from font8 import draw_text

SW = 24
SH = 14
SM = 4
LW = 16
LH = 10
LM = 4
HW = 6
HH = 10
HM = 4
SHOT_V = 8
GY = 280
HY = 240
DIRT = rgb(86, 64, 36)
ROCK = rgb(72, 78, 92)
SNOW = rgb(168, 172, 188)
STAR1 = rgb(200, 200, 230)
STAR2 = rgb(80, 80, 120)

SHIP = (
    "....ww......",
    "..wwwccw....",
    "wwcCCCccwwww",
    "rrCCCCCCccww",
    "wwcCCCccwwww",
    "..wwwccw....",
    "....ww......",
)
SHIP_PAL = {"w": WHITE, "c": rgb(0, 200, 255), "C": rgb(30, 80, 210), "r": rgb(240, 50, 70)}
LANDER = (
    "..cccc..",
    ".cwwwwc.",
    "ccyyyycc",
    ".yyyyyy.",
    "y.y..y.y",
)
LAND_PAL = {"c": rgb(40, 200, 80), "w": WHITE, "y": rgb(220, 210, 40)}
MUTANT = (
    "p.p..p.p",
    ".pppppp.",
    "pwwrrwwp",
    ".pyyyyp.",
    "yy.yy.yy",
)
MUT_PAL = {"p": PINK, "w": WHITE, "r": rgb(240, 40, 50), "y": rgb(255, 220, 40)}
HUMAN = (
    ".w.",
    "sss",
    ".n.",
    "n.n",
    "n.n",
)
HUM_PAL = {"w": rgb(255, 220, 160), "s": rgb(40, 120, 220), "n": rgb(200, 160, 80)}
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
BOOM_PAL = {"y": rgb(255, 230, 60), "o": rgb(255, 120, 30), "w": WHITE}


def _step(cur, tgt, m):
    d = tgt - cur
    if d > m:
        d = m
    elif d < -m:
        d = -m
    return cur + d


class Defenseur(Game):
    TITLE = "DEFENSEUR"
    HELP = ("SUIS LE DOIGT A GAUCHE", "TIRE SUR LES LANDERS", "SAUVE LES HUMAINS")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.ship = sprite(SHIP, SHIP_PAL, 2, BLACK, SM, SM)
        self.land = sprite(LANDER, LAND_PAL, 2, BLACK, LM, LM)
        self.mut = sprite(MUTANT, MUT_PAL, 2, BLACK, LM, LM)
        self.hum_g = sprite(HUMAN, HUM_PAL, 2, BLACK)
        self.hum_f = sprite(HUMAN, HUM_PAL, 2, BLACK, 2, HM)
        self.shot = sprite(("cwwwcc", "cwwwcc", "cwwwcc"), {"c": rgb(0, 220, 255), "w": WHITE}, 1, BLACK, SHOT_V, 0)
        self.boom = sprite(BOOM, BOOM_PAL, 2, BLACK, 4, 4)

    def preview(self, y):
        self.big_sprite(SHIP, SHIP_PAL, 4, y + 18)
        self.t.blit(self.land[0], 28, y + 8, self.land[1], self.land[2])
        self.t.blit(self.hum_f[0], 186, y + 70, self.hum_f[1], self.hum_f[2])

    def setup(self):
        t = self.t
        t.fill_rect(0, HUD, W, 320 - HUD, BLACK)
        t.fill_rect(0, GY, W, 320 - GY, DIRT)
        x = 0
        y0 = GY - 14
        while x < W:
            y1 = GY - 8 - random.randint(0, 18)
            dx = 6 + random.randint(0, 6)
            if x + dx > W:
                dx = W - x
            steps = dx if dx > abs(y1 - y0) else abs(y1 - y0)
            if steps < 1:
                steps = 1
            i = 0
            while i <= steps:
                px = x + dx * i // steps
                py = y0 + (y1 - y0) * i // steps
                t.fill_rect(px, py, 2, 2, SNOW)
                t.fill_rect(px, py + 2, 2, 1, ROCK)
                i += 1
            x += dx
            y0 = y1
        self.stars = []
        for _ in range(8):
            sx = random.randint(4, W - 4)
            sy = random.randint(HUD + 8, 220)
            self.stars.append((sx, sy))
            t.fill_rect(sx, sy, 1, 1, STAR1)
        xs = (52, 92, 132, 172, 212)
        self.hum = []
        for hx in xs:
            self.hum.append([hx, HY, 0, hx, HY])
            t.blit(self.hum_g[0], hx, HY, self.hum_g[1], self.hum_g[2])
        self.nh = 5
        self.sx = 8
        self.sy = 140
        self.tx = 8
        self.ty = 140
        self.foe = []
        self.shots = []
        self.booms = []
        self.frame = 0
        self.wave = 1
        self.next_sp = 20
        self.next_shot = 0
        self.inv_until = 0
        self.shown_h = -1
        self.draw_h()

    def draw_h(self):
        if self.nh != self.shown_h:
            draw_text(self.t, "H%d" % self.nh, 208, 22, GOLD, BLACK)
            self.shown_h = self.nh

    def pick(self):
        taken = []
        for e in self.foe:
            if e[2] < 2 and e[3] >= 0:
                taken.append(e[3])
        i = 0
        while i < 5:
            if self.hum[i][2] == 0:
                used = False
                for k in taken:
                    if k == i:
                        used = True
                        break
                if not used:
                    return i
            i += 1
        return -1

    def hit_ship(self, now):
        if time.ticks_diff(self.inv_until, now) > 0:
            return
        self.lives -= 1
        self.sfx.tone(110, 280)
        self.booms.append([self.sx + 4, self.sy, now])
        self.inv_until = time.ticks_add(now, 1200)

    def kill(self, e, now, pts):
        if e[4] >= 0:
            self.clear(e[4] - LM, e[5] - LM, LW + 2 * LM, LH + 2 * LM)
        self.score += pts
        bx = e[0] if e[4] < 0 else e[4]
        by = e[1] if e[5] < 0 else e[5]
        self.booms.append([bx, by, now])
        self.sfx.tone(240, 50)

    def lose_hum(self, i):
        h = self.hum[i]
        if h[2] == 3:
            return
        if h[2] == 0:
            self.t.fill_rect(h[0], HY, self.hum_g[1], self.hum_g[2], BLACK)
        elif h[2] == 2 and h[3] >= 0:
            self.clear(h[3] - 2, h[4] - HM, HW + 4, HH + 2 * HM)
        h[2] = 3
        self.nh -= 1
        self.draw_h()

    def land_hum(self, i, bonus):
        h = self.hum[i]
        if h[3] >= 0:
            self.clear(h[3] - 2, h[4] - HM, HW + 4, HH + 2 * HM)
        self.t.fill_rect(h[0], HY, self.hum_g[1], self.hum_g[2], BLACK)
        h[1] = HY
        h[2] = 0
        h[3], h[4] = h[0], HY
        self.t.blit(self.hum_g[0], h[0], HY, self.hum_g[1], self.hum_g[2])
        self.score += bonus
        self.sfx.tone(880, 80)

    def step(self, pt, now):
        t = self.t
        self.frame += 1
        fr = self.frame
        x, y = self.stars[fr % 8]
        t.fill_rect(x, y, 1, 1, STAR2 if fr & 16 else STAR1)

        if pt:
            self.ty = pt[1] - SH // 2
            if pt[0] < 80:
                self.tx = pt[0] - SW // 2
            if time.ticks_diff(now, self.next_shot) >= 0 and len(self.shots) < 2:
                self.next_shot = time.ticks_add(now, 180)
                self.shots.append([self.sx + SW - 2, self.sy + 5])
                self.sfx.tone(1300, 12)

        self.tx = 4 if self.tx < 4 else (40 if self.tx > 40 else self.tx)
        self.ty = 24 if self.ty < 24 else (HY - SH - 8 if self.ty > HY - SH - 8 else self.ty)
        self.sx = _step(self.sx, self.tx, SM)
        self.sy = _step(self.sy, self.ty, SM)
        if time.ticks_diff(self.inv_until, now) > 0 and (now // 100) % 2:
            self.clear(self.sx - SM, self.sy - SM, SW + 2 * SM, SH + 2 * SM)
        else:
            self.put(self.ship, self.sx, self.sy)

        keep = []
        for s in self.shots:
            s[0] += SHOT_V
            if s[0] < 0:
                continue
            if s[0] > W - 12:
                self.clear(s[0] - SHOT_V * 2, s[1], 8 + SHOT_V * 2, 2)
                continue
            self.put(self.shot, s[0], s[1])
            keep.append(s)
        self.shots = keep

        if fr == self.next_sp:
            gap = 88 - self.wave * 5
            if gap < 44:
                gap = 44
            self.next_sp = fr + gap
            cap = 2 if self.wave < 5 else 3
            if len(self.foe) < cap:
                hi = self.pick()
                fy = 40 + random.randint(0, 120)
                st = 0 if hi >= 0 else 2
                self.foe.append([W - LW - 6, fy, st, hi, -1, -1])

        sp_seek = 2
        sp_up = 1 if self.wave < 6 else 2
        sp_mut = 3
        alive = []
        for e in self.foe:
            x, y, st, hi = e[0], e[1], e[2], e[3]
            hit = False
            for s in self.shots:
                if s[0] >= 0 and overlap(s[0], s[1], 6, 3, x, y, LW, LH):
                    self.clear(s[0] - SHOT_V, s[1], 8 + SHOT_V * 2, 2)
                    s[0] = -1000
                    hit = True
                    break
            if hit:
                if st == 1 and 0 <= hi < 5 and self.hum[hi][2] == 1:
                    self.hum[hi][2] = 2
                    self.hum[hi][0] = x + 5
                    self.hum[hi][1] = y + LH + 4
                self.kill(e, now, 80 if st == 2 else 50)
                continue
            if st == 0 and 0 <= hi < 5:
                h = self.hum[hi]
                if h[2] != 0:
                    st = 2
                    e[2] = 2
                    e[3] = -1
                else:
                    x = _step(x, h[0] - 4, sp_seek)
                    y = _step(y, h[1] - 18 if abs(x - h[0]) > 14 else h[1] - 4, sp_seek)
                    if overlap(x + 2, y + 2, LW - 4, LH, h[0], h[1], HW, HH):
                        h[2] = 1
                        t.fill_rect(h[0], HY, self.hum_g[1], self.hum_g[2], BLACK)
                        st = 1
                        e[2] = 1
            if st == 1:
                y -= sp_up
                if 0 <= hi < 5:
                    self.hum[hi][0] = x + 5
                    self.hum[hi][1] = y + LH + 4
                if y <= HUD + 2:
                    if 0 <= hi < 5:
                        self.lose_hum(hi)
                    st = 2
                    e[2] = 2
                    e[3] = -1
                    self.sfx.tone(160, 180)
            if st == 2:
                x = _step(x, self.sx, sp_mut)
                y = _step(y, self.sy, sp_mut)
            if y < HUD + 2:
                y = HUD + 2
            if y > HY - 8:
                y = HY - 8
            if x < 2:
                x = 2
            if x > W - LW - 2:
                x = W - LW - 2
            e[0], e[1] = x, y
            if overlap(x + 2, y + 2, LW - 4, LH - 4, self.sx + 4, self.sy + 2, SW - 8, SH - 4):
                if e[4] >= 0:
                    self.clear(e[4] - LM, e[5] - LM, LW + 2 * LM, LH + 2 * LM)
                if st == 1 and 0 <= hi < 5 and self.hum[hi][2] == 1:
                    self.hum[hi][2] = 2
                    self.hum[hi][0] = x + 5
                    self.hum[hi][1] = y + LH + 4
                self.hit_ship(now)
                continue
            if (x, y) != (e[4], e[5]):
                self.put(self.mut if st == 2 else self.land, x, y)
                e[4], e[5] = x, y
            alive.append(e)
        self.foe = alive

        i = 0
        while i < 5:
            h = self.hum[i]
            if h[2] == 1:
                self.put(self.hum_f, h[0], h[1])
                h[3], h[4] = h[0], h[1]
            elif h[2] == 2:
                h[1] += HM
                if overlap(h[0], h[1], HW, HH, self.sx, self.sy, SW, SH):
                    self.land_hum(i, 200)
                    i += 1
                    continue
                if h[1] >= HY:
                    self.land_hum(i, 100)
                    i += 1
                    continue
                self.put(self.hum_f, h[0], h[1])
                h[3], h[4] = h[0], h[1]
            i += 1

        keep = []
        for b in self.booms:
            if time.ticks_diff(now, b[2]) > 180:
                self.clear(b[0] - 4, b[1] - 4, 26, 26)
            else:
                if len(b) == 3:
                    self.put(self.boom, b[0], b[1])
                    b.append(1)
                keep.append(b)
        self.booms = keep

        if fr % 400 == 0 and self.wave < 8:
            self.wave += 1
        i = 0
        while i < 5:
            h = self.hum[i]
            if h[2] == 0:
                self.t.blit(self.hum_g[0], h[0], HY, self.hum_g[1], self.hum_g[2])
            i += 1
        if self.nh <= 0:
            self.result = "HUMAINS PERDUS"
            return False
        return self.lives > 0

    def bot(self, n):
        if not hasattr(self, "sx"):
            return (120, 160) if n % 4 < 2 else None
        ty = self.sy + SH // 2
        tx = 18 + min(50, self.sx)
        best = 999
        for e in self.foe:
            d = abs(e[1] - self.sy)
            if e[2] == 1:
                d -= 20
            if d < best:
                best = d
                ty = e[1] + 5
                tx = 16
        i = 0
        while i < 5:
            h = self.hum[i]
            if h[2] == 2:
                ty = h[1] + 4
                tx = 20
                break
            i += 1
        if ty < 28:
            ty = 28
        if ty > HY - 8:
            ty = HY - 8
        return (tx, ty)


GAME = Defenseur


def play(tft, touch, day):
    GAME(tft, touch, day).run()
