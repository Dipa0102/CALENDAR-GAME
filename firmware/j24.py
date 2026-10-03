"""Jour 24 : BOSS RUSH. Tir vertical, quatre boss aux salves differentes."""

import random

from arcade import BLACK, CYAN, GOLD, HUD, RED, W, H, Game, overlap, rgb, sprite

SHIP_Y = 284
SW = 26
SH = 16
PVX = 8
SHOT_V = 16
MAXB = 4
HP_X = 20
HP_Y = 22
HP_W = 200
HP_H = 5
BOSS_Y = 42

SHIP = (
    "......w......",
    ".....wcw.....",
    "....wcCcw....",
    "...wCCCCCw...",
    "..ccCbbbCcc..",
    ".r.cCbbbCc.r.",
    "rrccCCCCCccrr",
    "..oo.....oo..",
)
SHIP_PAL = {"w": rgb(255, 255, 255), "c": CYAN, "C": rgb(50, 90, 220),
            "b": rgb(10, 20, 80), "r": rgb(240, 50, 70), "o": rgb(255, 160, 30)}

B1 = (
    "......wwwwww......",
    "....wwccccccww....",
    "..wwcccyyyycccww..",
    ".wccyyyyyyyyyyccw.",
    "wwyyyywwyywwyyyyww",
    ".wccyyyyyyyyyyccw.",
    "..www........www..",
    "....r........r....",
)
P1 = {"w": rgb(200, 220, 255), "c": rgb(80, 160, 255), "y": rgb(255, 230, 80), "r": rgb(255, 60, 40)}

B2 = (
    "..c..........c..",
    ".ccr........rcc.",
    "ccrrr......rrrcc",
    ".cRRRRRRRRRRrc..",
    "..rRRwRRwRRrr...",
    "...RRRRRRRRr....",
    "...r.r..r.r.....",
    "..r......r......",
)
P2 = {"c": rgb(255, 80, 40), "r": rgb(200, 40, 30), "R": rgb(255, 120, 50), "w": rgb(255, 255, 200)}

B3 = (
    "....kkkkkkkk....",
    "...kggggggggk...",
    "..kgGGggggGGgk..",
    ".kggggwwwwggggk.",
    "kkgggwwyywwgggkk",
    ".kkgggwwwwgggkk.",
    "..k.kkkkkkkk.k..",
    "....y......y....",
)
P3 = {"k": rgb(60, 70, 90), "g": rgb(40, 180, 70), "G": rgb(20, 110, 40),
      "w": rgb(220, 240, 255), "y": GOLD}

B4 = (
    "....ww....ww....",
    "...wvvw..wvvw...",
    "..wvvvvwwvvvvw..",
    ".wvvwwvvvvwwvvw.",
    "wvvvvvvvvvvvvvvw",
    ".wvvw.wwww.wvvw.",
    "..www..yy..www..",
    "....r......r....",
)
P4 = {"w": rgb(180, 80, 220), "v": rgb(120, 40, 180), "y": rgb(255, 60, 90), "r": rgb(255, 100, 40)}

BOSSES = ((B1, P1, 16, 28), (B2, P2, 20, 24), (B3, P3, 24, 20), (B4, P4, 28, 16))
BPAD = 4
BOOM = (
    "y...o...y",
    ".y.ooo.y.",
    "..ooyoo..",
    ".oyywyyo.",
    "ooywwwyoo",
    ".oyywyyo.",
    "..ooyoo..",
    ".y.ooo.y.",
)
BOOM_PAL = {"y": rgb(255, 230, 60), "o": rgb(255, 120, 30), "w": rgb(255, 255, 255)}


class BossRush(Game):
    TITLE = "BOSS RUSH"
    HELP = ("GLISSE : LE VAISSEAU", "IL TIRE TOUT SEUL", "4 BOSS, 3 VIES")
    LIVES = 3

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.ship = sprite(SHIP, SHIP_PAL, 2, BLACK, PVX, 0)
        self.boss_spr = [sprite(a, p, 3, BLACK, BPAD, BPAD) for a, p, _hp, _cd in BOSSES]
        self.shot = sprite(("cc", "cc", "ww", "ww", "cc"), {"c": CYAN, "w": rgb(255, 255, 255)}, 1, BLACK, 0, SHOT_V)
        self.bomb = sprite(("oyo", "yyy", "oyo"), {"o": rgb(255, 120, 30), "y": GOLD}, 1, BLACK, 4, 5)
        self.boom = sprite(BOOM, BOOM_PAL, 2, BLACK, 4, 4)
        self.bw = []
        self.bh = []
        for s in self.boss_spr:
            self.bw.append(s[1] - 2 * s[3])
            self.bh.append(s[2] - 2 * s[4])

    def preview(self, y):
        self.big_sprite(B1, P1, 4, y + 6)
        s = self.ship
        self.t.blit(s[0], (W - s[1]) // 2, y + 72, s[1], s[2])

    def setup(self):
        self.frame = 0
        self.sx = (W - SW) // 2
        self.target = self.sx
        self.shots = []
        self.bombs = []
        self.booms = []
        self.inv = 0
        self.reload = 0
        self.kind = 0
        self.round = 0
        self.shown_hp = -1
        self.spawn_boss()

    def spawn_boss(self):
        k = self.kind
        self.bx = (W - self.bw[k]) // 2
        self.by = BOSS_Y
        self.bvx = 1 if random.getrandbits(1) else -1
        if k == 3:
            self.bvx *= 2
        self.bvy = 1 if k == 3 else 0
        extra = self.round * 6
        self.hpmax = BOSSES[k][2] + extra
        self.hp = self.hpmax
        self.cd = max(8, BOSSES[k][3] - self.round)
        self.cool = self.cd
        self.shown_hp = -1
        self.draw_hp()

    def draw_hp(self):
        if self.hp == self.shown_hp:
            return
        t = self.t
        t.fill_rect(HP_X, HP_Y, HP_W, HP_H, rgb(40, 10, 20))
        w = HP_W * self.hp // self.hpmax if self.hpmax else 0
        if w > 0:
            t.fill_rect(HP_X, HP_Y, w, HP_H, RED)
        self.shown_hp = self.hp

    def aim_shot(self, x, y):
        dx = self.sx + SW // 2 - x
        dy = SHIP_Y - y
        if dy < 6:
            dy = 6
        ax = dx if dx >= 0 else -dx
        sp = 3
        if dy >= ax:
            vx = dx * sp // dy
            vy = sp
        else:
            vx = sp if dx > 0 else -sp
            vy = dy * sp // ax if ax else sp
            if vy < 2:
                vy = 2
        self.bombs.append([x, y, vx, vy])

    def boss_fire(self):
        if len(self.bombs) >= MAXB:
            return
        k = self.kind
        x = self.bx + self.bw[k] // 2
        y = self.by + self.bh[k] - 2
        if k == 0:
            self.aim_shot(x, y)
        elif k == 1:
            self.bombs.append([x, y, 0, 4])
            if len(self.bombs) < MAXB:
                self.bombs.append([x, y, -2, 3])
            if len(self.bombs) < MAXB:
                self.bombs.append([x, y, 2, 3])
        elif k == 2:
            self.bombs.append([self.bx + 4, y, 0, 4])
            if len(self.bombs) < MAXB:
                self.bombs.append([self.bx + self.bw[k] - 8, y, 0, 4])
        else:
            self.aim_shot(x, y)
            if len(self.bombs) < MAXB:
                self.bombs.append([self.bx + 2, y, -1, 4])
            if len(self.bombs) < MAXB:
                self.bombs.append([self.bx + self.bw[k] - 6, y, 1, 4])
        self.sfx.tone(520, 20)

    def hurt(self):
        if self.inv:
            return
        self.lives -= 1
        self.inv = 50
        self.sfx.tone(120, 280)
        self.booms.append([self.sx + 4, SHIP_Y, 6])

    def kill_boss(self):
        k = self.kind
        self.clear(self.bx - BPAD, self.by - BPAD, self.bw[k] + 2 * BPAD, self.bh[k] + 2 * BPAD)
        self.booms.append([self.bx + self.bw[k] // 2 - 8, self.by, 8])
        self.score += 500 + 200 * k + 100 * self.round
        self.sfx.tone(880, 120)
        for b in self.bombs:
            self.clear(b[0], b[1] - 5, 3, 12)
        self.bombs = []
        self.kind += 1
        if self.kind >= 4:
            self.kind = 0
            self.round += 1
        self.spawn_boss()

    def step(self, pt, now):
        self.frame += 1
        f = self.frame
        k = self.kind
        bw, bh = self.bw[k], self.bh[k]
        if self.inv:
            self.inv -= 1

        if pt:
            self.target = pt[0] - SW // 2
        d = self.target - self.sx
        d = PVX if d > PVX else (-PVX if d < -PVX else d)
        self.sx = 0 if self.sx + d < 0 else (W - SW if self.sx + d > W - SW else self.sx + d)

        if self.reload:
            self.reload -= 1
        elif len(self.shots) < 2:
            self.shots.append([self.sx + SW // 2 - 1, SHIP_Y - 4])
            self.reload = 7
            self.sfx.tone(1500, 12)

        keep = []
        for s in self.shots:
            old = s[1]
            y = old - SHOT_V
            hit = overlap(s[0], y, 2, SHOT_V + 5, self.bx, self.by, bw, bh)
            gone = y < self.by + 2
            if hit or gone:
                self.clear(s[0], old, 2, 5)
                if hit:
                    self.hp -= 1
                    self.score += 10
                    self.sfx.tone(200, 25)
                    if self.hp <= 0:
                        self.kill_boss()
                        k = self.kind
                        bw, bh = self.bw[k], self.bh[k]
                continue
            s[1] = y
            self.put(self.shot, s[0], y)
            keep.append(s)
        self.shots = keep
        self.draw_hp()

        if f & 1 == 0:
            self.bx += self.bvx
            if self.bx < 6 or self.bx > W - bw - 6:
                self.bvx = -self.bvx
                self.bx += self.bvx
            if k == 1:
                p = f % 280
                self.bx = 8 + (p if p < 140 else 280 - p)
                if self.bx > W - bw - 6:
                    self.bx = W - bw - 6
            if k == 3:
                self.by += self.bvy
                if self.by < BOSS_Y or self.by > 84:
                    self.bvy = -self.bvy
                    self.by += self.bvy
            elif k == 2:
                self.by = BOSS_Y + ((f >> 5) & 7)

        self.cool -= 1
        if self.cool <= 0:
            self.cool = self.cd
            self.boss_fire()

        keep = []
        for b in self.bombs:
            b[0] += b[2]
            b[1] += b[3]
            if b[1] > H - 4 or b[0] < 1 or b[0] > W - 4:
                self.clear(b[0] - b[2] - 4, b[1] - b[3] - 5, 11, 13)
                continue
            if overlap(b[0], b[1], 3, 3, self.sx + 4, SHIP_Y + 4, SW - 8, SH - 6):
                self.clear(b[0] - 4, b[1] - 5, 11, 13)
                self.hurt()
                continue
            self.put(self.bomb, b[0], b[1])
            keep.append(b)
        self.bombs = keep

        self.put(self.boss_spr[k], self.bx, self.by)
        if not self.inv and overlap(self.sx + 4, SHIP_Y + 4, SW - 8, SH - 8, self.bx + 4, self.by + 4, bw - 8, bh - 6):
            self.hurt()

        if self.inv == 0 or (f & 2):
            self.put(self.ship, self.sx, SHIP_Y)
        else:
            self.clear(self.sx - PVX, SHIP_Y, SW + 2 * PVX, SH)

        keep = []
        for b in self.booms:
            b[2] -= 1
            if b[2] <= 0:
                self.clear(b[0] - 4, b[1] - 4, 26, 26)
            else:
                self.put(self.boom, b[0], b[1])
                keep.append(b)
        self.booms = keep
        return self.lives > 0

    def bot(self, n):
        if not hasattr(self, "bx"):
            return (120, 160) if n % 4 < 2 else None
        if n % 8 == 7:
            return None
        tx = self.bx + self.bw[self.kind] // 2 + self.bvx * 6
        sx = self.sx + SW // 2
        for b in self.bombs:
            if b[1] > 150 and abs(b[0] - sx) < 18:
                tx = sx + (55 if b[0] <= sx else -55)
                break
        return (max(12, min(228, tx)), 300)


GAME = BossRush


def play(tft, touch, day):
    GAME(tft, touch, day).run()
