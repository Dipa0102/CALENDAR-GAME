"""Jour 25 : CHAMPIONNAT. Finale Track and Field : 4 epreuves, score cumule, 3 vies."""

import random
import time

from arcade import CYAN, GOLD, GREEN, NIGHT, PINK, RED, W, WHITE, Game, overlap, rgb, sprite
from font8 import draw_text

SKY = rgb(70, 140, 210)
DIRT = rgb(196, 110, 60)
GRASS = rgb(36, 140, 52)
STAND = rgb(92, 32, 42)
NAVY = rgb(28, 32, 58)
LANE = rgb(236, 214, 170)
BTN = rgb(48, 78, 158)
SAUT_C = rgb(176, 78, 24)
BAR_BG = rgb(24, 70, 28)
HUR = rgb(220, 220, 240)
FIN = 196
BOARD = 132
RY = 156
PAD = 8
BTN_Y = 248
NAMES = ("100 M", "SAUT EN LONGUEUR", "TIR AU PIGEON", "110 M HAIES")
SHORT = ("100 M", "SAUT", "PIGEON", "HAIES")
HX = (52, 96, 140, 184)

R1 = (
    "..www...",
    ".wwrww..",
    "...kk...",
    "...rr...",
    "..rrrr..",
    "..rrbb..",
    ".yy..b..",
    ".y...bb.",
)
R2 = (
    "..www...",
    ".wwrww..",
    "...kk...",
    "..rrr...",
    ".brrrr..",
    "..rrr.b.",
    "..y..y..",
    ".y....y.",
)
R3 = (
    "..www...",
    ".wwrww..",
    "...kk...",
    ".b.rr...",
    "..rrrrb.",
    "...rr...",
    "..y..y..",
    ".y....y.",
)
RPAL = {"w": WHITE, "r": rgb(220, 36, 46), "b": rgb(28, 36, 90), "y": rgb(36, 36, 44), "k": rgb(255, 196, 140)}
CUP = (
    "...ggg...",
    "..g.y.g..",
    "...yYy...",
    "...yyy...",
    "..yyyyy..",
    ".yy...yy.",
    ".yyyyyyy.",
    "..yyyyy..",
    "...www...",
)
CPAL = {"g": GREEN, "y": GOLD, "Y": rgb(255, 240, 160), "w": WHITE}
BIRD = ("..www..", ".wyyyw.", "wyyyyyw", ".wyyyw.", "..www..")
BOOM = ("w.y.y.w", ".wyyy.w", "yyywyyy", ".wyyy.w", "w.y.y.w")
BPAL = {"w": WHITE, "y": rgb(230, 210, 160)}


class Championnat(Game):
    TITLE = "CHAMPIONNAT"
    HELP = ("4 EPREUVES, 3 VIES", "ALTERNE GAUCHE DROITE", "SAUT AVANT LA LIGNE")
    BG = SKY

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.leg = [sprite(a, RPAL, 2, DIRT, PAD, PAD) for a in (R1, R2, R3)]
        self.bird = sprite(BIRD, BPAL, 2, SKY, 6, 6)
        self.boom = sprite(BOOM, BPAL, 2, SKY, 6, 6)
        self.cup = sprite(CUP, CPAL, 2, SKY)

    def preview(self, y):
        t = self.t
        t.fill_rect(20, y, 200, 96, SKY)
        t.fill_rect(20, y + 48, 200, 28, DIRT)
        t.fill_rect(20, y + 76, 200, 20, GRASS)
        t.fill_rect(20, y + 48, 200, 1, LANE)
        self.put(self.leg[1], 50, y + 40)
        self.put(self.cup, 176, y + 8)
        t.fill_rect(28, y + 80, 72, 14, BTN)
        t.fill_rect(140, y + 80, 72, 14, BTN)
        draw_text(t, "GAUCHE", 36, y + 83, WHITE, BTN, 1)
        draw_text(t, "DROITE", 148, y + 83, WHITE, BTN, 1)

    def setup(self):
        self.round = 1
        self.ev = 0
        self.marks = [-1, -1, -1, -1]
        self.last_ok = True
        self.begin(time.ticks_ms())

    def begin(self, now):
        self.phase = "clay" if self.ev == 2 else "go"
        self.t0 = now
        self.x = 16.0
        self.power = 0.0
        self.lastb = -1
        self.air = 0
        self.hits = 0
        self.n_bird = 0
        self.birds = []
        self.next_b = now
        self.try_n = 0
        self.best = 0
        self.hitb = [0, 0, 0, 0]
        self.drawn = None
        self.st = ""
        self.pw = -1
        self.ui = None
        self.board_on = 0
        self.dec = max(0.90, 0.958 - 0.01 * (self.round - 1))
        self.limit = max(3800, 9800 - 1400 * (self.round - 1))
        self.stadium()

    def stadium(self):
        t = self.t
        ev = self.ev
        t.fill_rect(0, 20, W, 228, SKY)
        t.fill_rect(0, 20, W, 34, STAND)
        for k in range(10):
            t.fill_rect(8 + k * 24, 24, 10, 8, rgb(40, 20, 28) if k & 1 else rgb(160, 50, 60))
        if ev != 2:
            t.fill_rect(0, 126, W, 76, DIRT)
            t.fill_rect(0, 126, W, 2, LANE)
            t.fill_rect(0, 200, W, 2, LANE)
            t.fill_rect(FIN, 126, 3, 76, WHITE)
            if ev == 1:
                t.fill_rect(BOARD, 126, 3, 76, WHITE)
                t.fill_rect(BOARD - 4, 192, 11, 8, GOLD)
            if ev == 3:
                for hx in HX:
                    self.hurdle(hx, 0)
        t.fill_rect(0, 202, W, 46, GRASS)
        for _ in range(18):
            t.fill_rect(random.randint(0, 237), random.randint(56, 118), 2, 2, WHITE)
        self.put(self.cup, 4, 56)
        s = NAMES[ev]
        draw_text(t, s, (W - len(s) * 8) // 2, 38, GOLD, STAND, 1)
        draw_text(t, "TOUR %d" % self.round, 168, 26, CYAN, STAND, 1)
        self.btns()

    def hurdle(self, x, hit):
        c = RED if hit else HUR
        t = self.t
        t.fill_rect(x, 170, 4, 32, c)
        t.fill_rect(x - 5, 168, 14, 4, RED if hit else GOLD)

    def btns(self):
        t = self.t
        t.fill_rect(0, BTN_Y, W, 72, NAVY)
        ev = self.ev
        if ev == 2:
            draw_text(t, "TOUCHE LES PIGEONS", 48, 276, WHITE, NAVY, 1)
            return
        if ev in (1, 3):
            boxes = ((4, 76, "GAUCHE", BTN), (84, 72, "SAUT", SAUT_C), (160, 76, "DROITE", BTN))
        else:
            boxes = ((4, 112, "GAUCHE", BTN), (124, 112, "DROITE", BTN))
        for x, w, name, c in boxes:
            t.fill_rect(x, 252, w, 64, c)
            t.rect(x, 252, w, 64, GOLD)
            draw_text(t, name, x + (w - len(name) * 8) // 2, 278, WHITE, c, 1)

    def line(self, s):
        s = (s + "                  ")[:18]
        if s == self.st:
            return
        self.st = s
        draw_text(self.t, s, 8, 210, WHITE, GRASS, 1)

    def bar(self):
        n = int(self.power)
        if n == self.pw:
            return
        self.pw = n
        self.t.fill_rect(8, 224, 70, 6, BAR_BG)
        if n:
            self.t.fill_rect(8, 224, n * 10, 6, GOLD)

    def wipe(self):
        d = self.drawn
        if d:
            spr = self.leg[0]
            self.t.fill_rect(d[0] - PAD, d[1] - PAD, spr[1], spr[2], DIRT)
            self.drawn = None

    def repair(self, x):
        t = self.t
        if abs(x - FIN) < 28:
            t.fill_rect(FIN, 126, 3, 76, WHITE)
        if self.ev == 1 and abs(x - BOARD) < 28:
            t.fill_rect(BOARD, 126, 3, 76, WHITE)
            t.fill_rect(BOARD - 4, 192, 11, 8, GOLD)
        if self.ev == 3:
            for i, hx in enumerate(HX):
                if abs(hx - x) < 30:
                    self.hurdle(hx, self.hitb[i])

    def runner(self, now):
        hop = 0
        if self.air > 0:
            hop = min(self.air, 24 - self.air)
            fr = 2
        elif self.power > 0.5:
            fr = 1 + ((now // 80) & 1)
        else:
            fr = 0
        ix, iy = int(self.x), RY - hop
        st = (ix, iy, fr)
        if st != self.drawn:
            self.put(self.leg[fr], ix, iy)
            self.drawn = st
            self.repair(ix)

    def which(self, p):
        if p[1] < BTN_Y:
            return -1
        if self.ev in (1, 3):
            if p[0] < 84:
                return 0
            if p[0] < 160:
                return 2
            return 1
        return 0 if p[0] < 124 else 1

    def mash(self, btn):
        if btn == 0 or btn == 1:
            if btn != self.lastb:
                self.power = min(7.0, self.power + 1.55)
                self.sfx.tone(640 + int(self.power) * 50, 18)
            self.lastb = btn

    def decay(self):
        self.power *= self.dec
        if self.power < 0.08:
            self.power = 0.0

    def end_ev(self, now, pts, ok):
        self.score += pts
        self.marks[self.ev] = pts
        self.last_ok = ok
        if not ok:
            self.lives -= 1
            self.sfx.tone(140, 350)
            if self.lives <= 0:
                self.result = "ELIMINE"
                return False
        else:
            self.sfx.tone(1047, 100)
        self.phase = "board"
        self.board_t = now
        self.board_on = 0
        return True

    def show_board(self):
        t = self.t
        t.fill_rect(16, 72, 208, 156, NIGHT)
        t.rect(16, 72, 208, 156, GOLD)
        draw_text(t, "TABLEAU", 88, 82, GOLD, NIGHT, 1)
        draw_text(t, "TOUR %d" % self.round, 88, 94, CYAN, NIGHT, 1)
        for i in range(4):
            mk = self.marks[i]
            if mk < 0:
                msg = SHORT[i] + "  ---"
            else:
                msg = SHORT[i] + "  %d" % mk
                if i == self.ev:
                    msg += " OK" if self.last_ok else " NON"
            c = WHITE
            if i == self.ev:
                c = GREEN if self.last_ok else RED
            draw_text(t, msg, 32, 112 + i * 16, c, NIGHT, 1)
        draw_text(t, "TOUCHE POUR CONTINUER", 36, 204, PINK, NIGHT, 1)

    def next_ev(self, now):
        self.ev += 1
        if self.ev >= 4:
            self.ev = 0
            self.round += 1
            self.marks = [-1, -1, -1, -1]
        self.begin(now)

    def quali_t(self):
        return max(4500, 10000 - 900 * (self.round - 1))

    def jump_mark(self):
        return 320 + 48 * (self.round - 1)

    def clay_mark(self):
        return min(9, 4 + self.round)

    def hud_t(self, el):
        sec = el // 1000
        if self.ev == 3:
            key = (self.hits, sec)
            if key != self.ui:
                self.ui = key
                self.line("HAIES %d %d S" % (self.hits, sec))
        elif sec != self.ui:
            self.ui = sec
            self.line("%d S" % sec)

    def step_run(self, pt, now):
        p = self.tap(pt)
        if p:
            b = self.which(p)
            if b == 2:
                if self.ev == 3 and self.air <= 0:
                    self.air = 24
                    self.sfx.tone(880, 40)
                elif self.ev == 1 and self.air <= 0:
                    return self.takeoff(now)
            elif b >= 0:
                self.mash(b)
        self.decay()
        self.x += self.power * 0.22
        if self.air > 0:
            self.air -= 1
        if self.ev == 3 and self.air <= 0:
            ix = int(self.x)
            for i, hx in enumerate(HX):
                if not self.hitb[i] and hx - 2 <= ix <= hx + 8:
                    self.hitb[i] = 1
                    self.hits += 1
                    self.power *= 0.42
                    self.hurdle(hx, 1)
                    self.sfx.tone(160, 120)
        el = time.ticks_diff(now, self.t0)
        if self.x >= FIN:
            pts = max(10, (self.limit - el) // 8)
            if self.ev == 3:
                pts = max(10, pts - self.hits * 70)
            return self.end_ev(now, pts, el <= self.quali_t())
        if el >= self.limit + 5000:
            return self.end_ev(now, 0, False)
        self.hud_t(el)
        self.bar()
        self.runner(now)
        return True

    def takeoff(self, now):
        if self.x > BOARD:
            dist = 0
            foul = 1
        else:
            early = max(0, BOARD - 8 - int(self.x))
            dist = max(0, int(self.power * 88) - early * 3)
            foul = 0
        self.sfx.tone(120 if foul else 980, 80)
        self.phase = "air"
        self.air = 24
        self.vx = 0.8 + self.power * 0.55
        self.fly = 20 + int(self.power * 2)
        self.pend = dist
        self.foul = foul
        self.line("SAUT")
        return True

    def step_air(self, pt, now):
        self.tap(pt)
        if self.air > 0:
            self.air -= 1
        self.x += self.vx
        if self.x > 210:
            self.x = 210.0
        self.fly -= 1
        self.runner(now)
        if self.fly > 0:
            return True
        dist = 0 if self.foul else self.pend
        if dist > self.best:
            self.best = dist
        self.try_n += 1
        self.phase = "land"
        self.land_t = now
        if self.foul:
            self.line("FAUTE  ESSAI %d/3" % self.try_n)
        else:
            self.line("%d.%02d M  BEST %d.%02d" % (dist // 100, dist % 100, self.best // 100, self.best % 100))
        return True

    def step_land(self, pt, now):
        self.tap(pt)
        if time.ticks_diff(now, self.land_t) < 500:
            return True
        if self.try_n >= 3:
            ok = self.best >= self.jump_mark()
            return self.end_ev(now, self.best // 2, ok)
        self.wipe()
        self.x = 16.0
        self.power = 0.0
        self.lastb = -1
        self.air = 0
        self.pw = -1
        self.ui = None
        self.phase = "go"
        self.t0 = now
        self.line("ESSAI %d/3  BEST %d.%02d" % (self.try_n + 1, self.best // 100, self.best % 100))
        return True

    def spawn(self, now):
        left = random.randint(0, 1)
        sp = 0.7 + 0.08 * self.round + random.random() * 0.25
        x = 10.0 if left else 212.0
        vx = sp if left else -sp
        vy = -2.5 - random.random() * 0.4
        self.birds.append([x, 158.0, vx, vy, 0, 0, None])
        self.n_bird += 1

    def step_clay(self, pt, now):
        p = self.tap(pt)
        keep = []
        for b in self.birds:
            if b[4]:
                b[5] -= 1
                if b[5] <= 0:
                    self.t.fill_rect(int(b[0]) - 6, int(b[1]) - 6, self.boom[1], self.boom[2], SKY)
                    self.next_b = time.ticks_add(now, 400)
                    continue
                keep.append(b)
                ix, iy = int(b[0]), int(b[1])
                key = (ix, iy, 1)
                if key != b[6]:
                    self.put(self.boom, ix, iy)
                    b[6] = key
                continue
            b[0] += b[2]
            b[1] += b[3]
            b[3] += 0.05 + 0.006 * self.round
            ix, iy = int(b[0]), int(b[1])
            if p and overlap(p[0] - 16, p[1] - 16, 32, 32, ix, iy, 22, 18):
                b[4] = 1
                b[5] = 5
                self.hits += 1
                self.sfx.tone(1320, 35)
                p = None
                keep.append(b)
                continue
            if iy > 178 or ix < -24 or ix > 248:
                self.t.fill_rect(ix - 6, iy - 6, self.bird[1], self.bird[2], SKY)
                self.next_b = time.ticks_add(now, 350)
                continue
            keep.append(b)
            key = (ix, iy, 0)
            if key != b[6]:
                self.put(self.bird, ix, iy)
                b[6] = key
        self.birds = keep
        if self.n_bird < 10 and len(keep) < 2 and time.ticks_diff(now, self.next_b) >= 0:
            self.spawn(now)
            self.next_b = time.ticks_add(now, 500)
        elif not keep and self.n_bird >= 10:
            return self.end_ev(now, self.hits * 80, self.hits >= self.clay_mark())
        key = (self.n_bird, self.hits)
        if key != self.ui:
            self.ui = key
            self.line("%d/10  OK %d" % key)
        return True

    def step(self, pt, now):
        ph = self.phase
        if ph == "board":
            if not self.board_on:
                self.show_board()
                self.board_on = 1
            p = self.tap(pt)
            if p or time.ticks_diff(now, self.board_t) >= 2000:
                self.next_ev(now)
            return True
        if ph == "clay":
            return self.step_clay(pt, now)
        if ph == "air":
            return self.step_air(pt, now)
        if ph == "land":
            return self.step_land(pt, now)
        return self.step_run(pt, now)

    def bot(self, n):
        if not hasattr(self, "phase"):
            return (120, 160) if n % 4 < 2 else None
        if self.lives <= 0 or self.phase == "board":
            return (120, 160) if n % 4 < 2 else None
        if n % 4 >= 2:
            return None
        ph = self.phase
        if ph == "clay":
            for b in self.birds:
                if b[4] == 0 and b[3] > 0 and b[1] > 145:
                    return (int(b[0]) + 10, int(b[1]) + 8)
            return None
        if ph != "go":
            return None
        if self.ev == 1 and self.x >= 108:
            return (120, 278)
        if self.ev == 3 and self.air <= 0:
            x = self.x
            for hx in HX:
                if hx - 10 <= x <= hx + 2:
                    return (120, 278)
        if (n // 4) & 1:
            return (200, 278)
        return (40, 278)


GAME = Championnat


def play(tft, touch, day):
    GAME(tft, touch, day).run()
