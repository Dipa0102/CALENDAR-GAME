"""Jour 19 : ZOMBIE NIGHT. Cimetiere, zombies qui avancent, fusil a 6 coups."""

import random
import time

from arcade import GOLD, HUD, W, WHITE, Game, overlap, rgb, sprite
from font8 import draw_text

NITE = rgb(18, 14, 32)
DIRT = rgb(48, 40, 28)
WOOD = rgb(120, 78, 36)
WOOD2 = rgb(90, 56, 24)
MOON = rgb(230, 220, 140)
BAR = 264
AX0 = 188
AY0 = 292
AW = 48
AH = 26
SMW = 10
SMH = 16
BGW = 16
BGH = 22
PM = 3
BATW = 16
BATH = 10

Z1 = (
    ".ggg.",
    "gkwkg",
    ".ggg.",
    ".nnn.",
    "n.n.n",
    ".n.n.",
    "n...n",
    ".n.n.",
)
Z2 = (
    ".ggg.",
    "gkwkg",
    ".ggg.",
    ".nnn.",
    "n.n.n",
    "n..n.",
    ".n..n",
    "n..n.",
)
ZPAL = {"g": rgb(70, 140, 60), "k": rgb(20, 20, 20), "w": WHITE, "n": rgb(50, 90, 40)}
B1 = (
    "..gggg..",
    ".gkwkwg.",
    ".gggggg.",
    "..nnnn..",
    ".nnnnnn.",
    "nn.nn.nn",
    ".n.nn.n.",
    "n..nn..n",
    "n..n...n",
    ".n....n.",
    "n......n",
)
B2 = (
    "..gggg..",
    ".gkwkwg.",
    ".gggggg.",
    "..nnnn..",
    ".nnnnnn.",
    "n.nnnn.n",
    "n..nn..n",
    ".n.nn.n.",
    "..n..n..",
    ".n....n.",
    ".n....n.",
)
BPAL = {"g": rgb(90, 160, 70), "k": rgb(20, 20, 20), "w": WHITE, "n": rgb(40, 80, 35)}
TOMB = (
    "..mmmm..",
    ".mwwmmm.",
    "mmmmmmmm",
    "mmwwmmmm",
    "mmmmmmmm",
    "mmmwwmmm",
    "mmmmmmmm",
    "..kkkk..",
)
TOMB_PAL = {"m": rgb(110, 110, 120), "w": rgb(160, 160, 170), "k": rgb(70, 60, 40)}
BAT1 = (
    "w...w...w",
    ".w.wkw.w.",
    "..wwwww..",
    "...w.w...",
)
BAT2 = (
    ".........",
    "ww.wkw.ww",
    ".wwwwwww.",
    "...w.w...",
)
BAT_PAL = {"w": rgb(40, 30, 50), "k": rgb(200, 60, 60)}
CRATE = (
    "yyyyyyyyyyyy",
    "ykkkkkkkkkky",
    "ykwwkkkkkwky",
    "ykkkkkkkkkky",
    "yyyyyyyyyyyy",
    "ykkkkRRkkkky",
    "ykkkkkkkkkky",
    "yyyyyyyyyyyy",
)
CRATE_PAL = {"y": rgb(180, 120, 40), "k": rgb(120, 70, 20), "w": rgb(220, 180, 80), "R": rgb(200, 40, 40)}
SHELL = (("rr", "rr", "yy"), {"r": rgb(180, 40, 40), "y": GOLD})
BOOM = (
    "y..o..y",
    ".yoyo.y",
    "ooywyoo",
    ".yoyo.y",
    "y..o..y",
)
BOOM_PAL = {"y": rgb(255, 220, 40), "o": rgb(255, 100, 20), "w": WHITE}
GRAVES = (24, 76, 128, 180)


class ZombieNight(Game):
    TITLE = "ZOMBIE NIGHT"
    HELP = ("TIRE SUR LES ZOMBIES", "VISE LA TETE : BONUS", "CAISSE : RECHARGE")
    BG = NITE

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.zs = (
            (sprite(Z1, ZPAL, 2, NITE, 2, PM), sprite(Z2, ZPAL, 2, NITE, 2, PM)),
            (sprite(B1, BPAL, 2, NITE, 2, PM), sprite(B2, BPAL, 2, NITE, 2, PM)),
        )
        self.tomb = sprite(TOMB, TOMB_PAL, 2, NITE)
        self.bats = (
            sprite(BAT1, BAT_PAL, 2, NITE, 4, 1),
            sprite(BAT2, BAT_PAL, 2, NITE, 4, 1),
        )
        self.crate = sprite(CRATE, CRATE_PAL, 2, DIRT)
        self.shell = sprite(SHELL[0], SHELL[1], 2, DIRT)
        self.boom = sprite(BOOM, BOOM_PAL, 2, NITE, 3, 3)

    def preview(self, y):
        self.t.fill_rect(40, y + 8, 160, 84, NITE)
        self.t.blit(self.tomb[0], 48, y + 20, self.tomb[1], self.tomb[2])
        self.big_sprite(B1, BPAL, 4, y + 18)

    def setup(self):
        t = self.t
        t.fill_rect(0, HUD, W, 320 - HUD, NITE)
        t.fill_circle(214, 36, 14, MOON)
        t.fill_circle(220, 32, 5, NITE)
        for k in range(6):
            t.fill_rect(12 + k * 36, 30 + (k * 5) % 11, 1, 1, rgb(180, 180, 210))
        tw, th = self.tomb[1], self.tomb[2]
        for gx in GRAVES:
            t.blit(self.tomb[0], gx, 44, tw, th)
            t.fill_rect(gx + 4, 44 + th - 2, tw - 8, 6, rgb(70, 60, 30))
        t.fill_rect(0, BAR, W, 6, WOOD)
        t.fill_rect(0, BAR + 6, W, 4, WOOD2)
        x = 8
        while x < W:
            t.fill_rect(x, BAR - 10, 4, 10, WOOD)
            x += 28
        t.fill_rect(0, 282, W, 38, DIRT)
        t.blit(self.crate[0], AX0 + 4, AY0, self.crate[1], self.crate[2])
        self.zoms = []
        self.bat = None
        self.booms = []
        self.ammo = 6
        self.reload = 0
        self.wave = 1
        self.left = 6
        self.next_z = 4
        self.next_bat = 70
        self.frame = 0
        self.shown_a = -1
        self.draw_ammo()

    def draw_ammo(self):
        if self.ammo == self.shown_a:
            return
        self.t.fill_rect(8, 300, 72, 14, DIRT)
        k = 0
        while k < self.ammo:
            self.t.blit(self.shell[0], 10 + k * 12, 302, self.shell[1], self.shell[2])
            k += 1
        self.shown_a = self.ammo

    def spawn_z(self):
        if len(self.zoms) >= 5 or self.left <= 0:
            return
        tries = 0
        gx = GRAVES[0]
        while tries < 6:
            gx = GRAVES[random.randint(0, 3)] + random.randint(0, 14)
            busy = False
            for z in self.zoms:
                if z[1] < 120 and gx - 18 < z[0] < gx + 18:
                    busy = True
                    break
            if not busy:
                break
            tries += 1
        big = 1 if random.getrandbits(2) == 0 else 0
        hp = 2 if big else 1
        self.zoms.append([gx, 72, big, hp, 0, 32, -1, -1])
        self.left -= 1

    def die_z(self, z, now, pts):
        zw = BGW if z[2] else SMW
        zh = BGH if z[2] else SMH
        if z[6] >= 0:
            self.clear(z[6] - 2, z[7] - PM, zw + 4, zh + 2 * PM)
        self.score += pts
        self.booms.append([z[0], z[1], now])
        self.sfx.tone(180, 70)

    def step(self, pt, now):
        self.frame += 1
        fr = self.frame
        p = self.tap(pt)

        if self.reload:
            if time.ticks_diff(now, self.reload) >= 0:
                self.reload = 0
                self.ammo = 6
                self.draw_ammo()
                self.t.fill_rect(80, 304, 56, 8, DIRT)
                self.sfx.tone(440, 60)
        elif p and p[0] >= AX0 and p[1] >= AY0:
            if self.ammo < 6:
                self.reload = time.ticks_add(now, 800)
                draw_text(self.t, "RELOAD", 80, 304, GOLD, DIRT)
                self.sfx.tone(220, 80)
        elif p and self.ammo > 0:
            self.ammo -= 1
            self.draw_ammo()
            self.sfx.tone(90, 40)
            hx, hy = p[0] - 12, p[1] - 12
            hit = None
            for z in self.zoms:
                zw = BGW if z[2] else SMW
                zh = BGH if z[2] else SMH
                if overlap(hx, hy, 24, 24, z[0], z[1], zw, zh):
                    if hit is None or z[1] > hit[1]:
                        hit = z
            if hit is not None:
                zw = BGW if hit[2] else SMW
                hh = 8 if hit[2] else 6
                if overlap(p[0] - 6, p[1] - 6, 12, 12, hit[0], hit[1], zw, hh):
                    self.die_z(hit, now, 80 + 40 * hit[2])
                    self.zoms.remove(hit)
                else:
                    hit[3] -= 1
                    if hit[3] <= 0:
                        self.die_z(hit, now, 30 + 20 * hit[2])
                        self.zoms.remove(hit)
                    else:
                        self.sfx.tone(300, 40)
            elif self.bat is not None:
                b = self.bat
                if overlap(hx, hy, 24, 24, b[0], b[1], BATW, BATH):
                    self.clear(b[0] - 4, b[1] - 1, BATW + 8, BATH + 2)
                    self.score += 120
                    self.bat = None
                    self.sfx.tone(980, 70)

        sp = 1 + (self.wave // 2)
        if sp > PM:
            sp = PM
        keep = []
        for z in self.zoms:
            zw = BGW if z[2] else SMW
            zh = BGH if z[2] else SMH
            if z[5] > 0:
                z[5] -= 1
                if fr & 1:
                    z[1] += 1
            else:
                z[4] = (fr // 8) & 1
                step = sp
                if self.wave < 3 and (fr & 1):
                    step = 0
                z[1] += step
                if (fr // 6) & 1:
                    z[0] += 1 if z[4] else -1
            if z[0] < 4:
                z[0] = 4
            if z[0] > W - zw - 4:
                z[0] = W - zw - 4
            if z[1] + zh >= BAR:
                if z[6] >= 0:
                    self.clear(z[6] - 2, z[7] - PM, zw + 4, zh + 2 * PM)
                self.lives -= 1
                self.sfx.tone(100, 280)
                if self.lives <= 0:
                    return False
                continue
            self.put(self.zs[z[2]][z[4]], z[0], z[1])
            z[6], z[7] = z[0], z[1]
            keep.append(z)
        self.zoms = keep

        b = self.bat
        if b is None:
            if fr >= self.next_bat:
                d = 1 if random.getrandbits(1) else -1
                x = -BATW if d > 0 else 172
                self.bat = [x, 26 + random.randint(0, 8), d, -99, -99]
                self.next_bat = fr + 100 + random.randint(0, 80)
        else:
            b[0] += b[2] * 3
            gone = b[0] < -BATW - 4 or (b[2] > 0 and b[0] > 172) or (b[2] < 0 and b[0] > W)
            if gone:
                if b[3] >= 0:
                    self.clear(b[3] - 4, b[4] - 1, BATW + 8, BATH + 2)
                self.bat = None
            else:
                frb = (fr // 6) & 1
                self.put(self.bats[frb], b[0], b[1])
                b[3], b[4] = b[0], b[1]

        keep = []
        for u in self.booms:
            if time.ticks_diff(now, u[2]) > 160:
                self.clear(u[0] - 3, u[1] - 3, 20, 20)
            else:
                if len(u) == 3:
                    self.put(self.boom, u[0], u[1])
                    u.append(1)
                keep.append(u)
        self.booms = keep

        if fr == self.next_z:
            self.spawn_z()
            wait = 22 - self.wave
            if wait < 10:
                wait = 10
            self.next_z = fr + wait
        if self.left <= 0 and not self.zoms:
            self.wave += 1
            self.left = 4 + self.wave
            if self.left > 9:
                self.left = 9
            draw_text(self.t, "VAGUE %d" % self.wave, 88, 140, GOLD, NITE)
            self.sfx.tune(((392, 60), (523, 80)))
            self.t.fill_rect(88, 140, 72, 8, NITE)
            self.next_z = fr + 10
        return self.lives > 0

    def bot(self, n):
        if not hasattr(self, "zoms"):
            return (120, 160) if n % 4 < 2 else None
        if self.reload:
            return None
        if self.ammo <= 0:
            return (AX0 + 20, AY0 + 10) if n % 4 < 2 else None
        if n % 7:
            return None
        best = None
        for z in self.zoms:
            if z[1] < 120:
                continue
            if best is None or z[1] > best[1]:
                best = z
        if best is None:
            if self.bat is not None and 20 < self.bat[0] < 180:
                return (self.bat[0] + 8, self.bat[1] + 4)
            return None
        zw = BGW if best[2] else SMW
        return (best[0] + zw // 2, best[1] + 4)


GAME = ZombieNight


def play(tft, touch, day):
    GAME(tft, touch, day).run()
