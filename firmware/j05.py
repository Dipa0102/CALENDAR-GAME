"""Jour 5 : ENVAHISSEURS. Le canon suit le doigt et tire un seul missile a la fois ; les abris s'effritent."""

import random

from arcade import BLACK, GOLD, HUD, RED, W, WHITE, Game, rgb, sprite
from font8 import draw_text

COLS = 5
ROWS = 4
CS = 36
RS = 24
IW = 24
IH = 16
IPX = 6
DY = 8
X0 = (W - (COLS - 1) * CS - IW) // 2
Y0 = 50
KIND = (0, 1, 1, 2)
PTS = (30, 20, 10)
HITX = ((4, 20), (0, 22), (0, 24))
BEAT = (196, 175, 156, 147)

UFO_Y = 26
UFO_W = 32
UFO_PTS = (50, 100, 150, 300)

BUNK_X = (20, 76, 132, 188)
BUNK_Y = 244
BUNK = ("..####..", ".######.", "########", "###..###", "##....##")

CANNON_Y = 290
CW = 26
CPX = 6
GROUND_Y = 310
MV = 11
BVM = 6

SQUID = ((
    ".....PP.....",
    "....PPPP....",
    "...pppppp...",
    "..ppwppwpp..",
    "..pppppppp..",
    "....p..p....",
    "...p.pp.p...",
    "..p.p..p.p..",
), (
    ".....PP.....",
    "....PPPP....",
    "...pppppp...",
    "..ppwppwpp..",
    "..pppppppp..",
    "...p.pp.p...",
    "..p......p..",
    "...p....p...",
))
CRAB = ((
    "..c.....c...",
    "...c...c....",
    "..CCCCCCC...",
    ".CCwCCCwCC..",
    "ccccccccccc.",
    "c.ccccccc.c.",
    "c.c.....c.c.",
    "...cc.cc....",
), (
    "..c.....c...",
    "c..c...c..c.",
    "c.CCCCCCC.c.",
    "CCCwCCCwCCC.",
    "ccccccccccc.",
    ".ccccccccc..",
    "..c.....c...",
    ".c.......c..",
))
OCTO = ((
    "....OOOO....",
    ".OOOOOOOOOO.",
    "oooooooooooo",
    "oooRRooRRooo",
    "oooooooooooo",
    "...oo..oo...",
    "..oo.oo.oo..",
    "oo........oo",
), (
    "....OOOO....",
    ".OOOOOOOOOO.",
    "oooooooooooo",
    "oooRRooRRooo",
    "oooooooooooo",
    "..ooo..ooo..",
    ".oo..oo..oo.",
    "..oo....oo..",
))
INVADERS = (
    (SQUID, {"p": rgb(255, 40, 200), "P": rgb(255, 150, 240), "w": rgb(255, 255, 255)}),
    (CRAB, {"c": rgb(0, 200, 255), "C": rgb(140, 240, 255), "w": rgb(255, 255, 255)}),
    (OCTO, {"o": rgb(255, 170, 20), "O": rgb(255, 230, 90), "R": rgb(255, 40, 40)}),
)
CANNON = (
    "......w......",
    ".....www.....",
    ".....ggg.....",
    ".ggggggggggg.",
    "ggggggggggggg",
    "gGGGGGGGGGGGg",
    "ggggggggggggg",
    "ggggggggggggg",
)
CANNON_PAL = {"g": rgb(60, 230, 110), "G": rgb(20, 130, 60), "w": rgb(255, 255, 255)}
BLASTS = ((
    "....o...o....",
    ".o....o....o.",
    "...o.ooo.o...",
    "..oo.oyo.oo..",
    ".oooyyyyyooo.",
    "ooyyywwwyyyoo",
    "oyywwwwwwwyyo",
    "yywwwwwwwwwyy",
), (
    ".o.....o...o.",
    "...o.o...o...",
    "o....ooo....o",
    "..o.oyyyo.o..",
    "..ooyywyyoo..",
    ".oyyywwwyyyo.",
    "ooyywwwwwyyoo",
    "oyyyywwwyyyyo",
))
BLAST_PAL = {"o": rgb(255, 110, 30), "y": rgb(255, 230, 60), "w": rgb(255, 255, 255)}
POP = (
    "y....y.....y",
    ".y...y....y.",
    "..y.....yy..",
    "yy..ywwy....",
    "....ywwy..yy",
    "..yy.....y..",
    ".y....y...y.",
    "y.....y....y",
)
POP_PAL = {"y": rgb(255, 230, 60), "w": rgb(255, 255, 255)}
UFO = (
    ".....RRRRRR.....",
    "...rrrrrrrrrr...",
    "..rrrrrrrrrrrr..",
    ".rryrryrryrryrr.",
    "rrrrrrrrrrrrrrrr",
    "..rrr..rr..rrr..",
    "...r........r...",
)
UFO_PAL = {"r": rgb(240, 40, 50), "R": rgb(255, 140, 160), "y": rgb(255, 230, 60)}
BOMBS = (
    ((".w.", "w..", ".w.", "..w"), (".w.", "..w", ".w.", "w..")),
    ((".o.", ".o.", ".o.", "ooo"), ("ooo", ".o.", ".o.", ".o.")),
)
BOMB_PAL = {"w": rgb(255, 255, 255), "o": rgb(255, 120, 30)}
BUNK_C = rgb(40, 220, 90)


class Envahisseurs(Game):
    TITLE = "ENVAHISSEURS"
    HELP = ("GLISSE LE DOIGT : LE CANON", "DOIGT POSE : IL TIRE", "UN SEUL MISSILE A LA FOIS")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.inv = [(sprite(a[0], p, 2, BLACK, IPX, 0), sprite(a[1], p, 2, BLACK, IPX, 0)) for a, p in INVADERS]
        self.cannon = sprite(CANNON, CANNON_PAL, 2, BLACK, CPX, 0)
        self.blast = [sprite(a, BLAST_PAL, 2, BLACK, CPX, 0) for a in BLASTS]
        self.pop = sprite(POP, POP_PAL, 2, BLACK)
        self.ufo_spr = sprite(UFO, UFO_PAL, 2, BLACK, 2, 0)
        # Fond seulement sous le missile / au-dessus des bombes : la trace s'efface
        # sans rogner ce qu'il y a devant (abris, envahisseurs).
        self.mspr = sprite(("cc",) + ("ww",) * 6 + ("cc",) + ("..",) * MV, {"c": rgb(0, 220, 255), "w": rgb(255, 255, 255)}, 1, BLACK)
        pad = ("...",) * (BVM // 2)
        self.bspr = [[sprite(pad + a, BOMB_PAL, 2, BLACK) for a in k] for k in BOMBS]
        self.dmg = sprite(("g.g.", ".g..", "..gg", "g..g"), {"g": BUNK_C}, 1, BLACK)

    def preview(self, y):
        t = self.t
        rows = ((self.ufo_spr, "= ? MYSTERE", RED), (self.inv[0][0], "= 30 POINTS", WHITE),
                (self.inv[1][0], "= 20 POINTS", WHITE), (self.inv[2][0], "= 10 POINTS", WHITE))
        for i, (spr, txt, c) in enumerate(rows):
            t.blit(spr[0], 92 - spr[1] // 2 - 20, y + 6 + i * 22, spr[1], spr[2])
            draw_text(t, txt, 100, y + 10 + i * 22, c, BLACK)

    # --- mise en place ------------------------------------------------------
    def setup(self):
        self.t.fill_rect(0, GROUND_Y, W, 2, BUNK_C)
        self.frame = 0
        self.wave = 0
        self.cx = (W - CW) // 2
        self.target = self.cx
        self.dead = 0
        self.bonus = False
        self.new_wave()

    def new_wave(self):
        self.wave += 1
        self.clear(0, HUD, W, GROUND_Y - HUD)
        self.cdirty = True
        y0 = Y0 + 10 * min(5, self.wave - 1)
        self.rx = [X0] * ROWS
        self.ry = [y0 + r * RS for r in range(ROWS)]
        self.alive = bytearray(b"\x01" * (ROWS * COLS))
        self.rowcnt = [COLS] * ROWS
        self.n = ROWS * COLS
        self.cmin, self.cmax = 0, COLS - 1
        self.dir = 1
        self.cyc = ()
        self.ci = 0
        self.rest = 10
        self.stepx = 2
        self.drop = False
        self.anim = 0
        self.beat = 0
        self.my = None
        self.mx = 0
        self.reload = 0
        self.bombs = []
        self.pops = []
        self.ufo = None
        self.label = None
        self.next_ufo = self.frame + random.randint(450, 750)
        self.bk = bytearray(4 * 40)
        t = self.t
        for b in range(4):
            for j in range(5):
                row = BUNK[j]
                i = 0
                while i < 8:
                    if row[i] == "#":
                        i0 = i
                        while i < 8 and row[i] == "#":
                            self.bk[b * 40 + j * 8 + i] = 2
                            i += 1
                        t.fill_rect(BUNK_X[b] + i0 * 4, BUNK_Y + j * 4, (i - i0) * 4, 4, BUNK_C)
                    else:
                        i += 1
        for r in range(ROWS):
            self.draw_row(r, None)

    # --- abris --------------------------------------------------------------
    def bunker_find(self, x0, x1, y0, y1, down):
        for b in range(4):
            bx = BUNK_X[b]
            if x1 < bx or x0 >= bx + 32:
                continue
            c0 = (x0 - bx) >> 2 if x0 > bx else 0
            c1 = (x1 - bx) >> 2
            if c1 > 7:
                c1 = 7
            j0 = (y0 - BUNK_Y) >> 2 if y0 > BUNK_Y else 0
            j1 = (y1 - 1 - BUNK_Y) >> 2
            if j1 > 4:
                j1 = 4
            bk = self.bk
            js = range(j0, j1 + 1) if down else range(j1, j0 - 1, -1)
            for j in js:
                base = b * 40 + j * 8
                for c in range(c0, c1 + 1):
                    if bk[base + c]:
                        return base + c
            return -1
        return -1

    def damage(self, k):
        hp = self.bk[k] - 1
        self.bk[k] = hp
        b, rem = divmod(k, 40)
        x = BUNK_X[b] + (rem & 7) * 4
        y = BUNK_Y + (rem >> 3) * 4
        if hp:
            self.t.blit(self.dmg[0], x, y, 4, 4)
        else:
            self.t.fill_rect(x, y, 4, 4, BLACK)

    def crush(self, x0, x1, y0, y1):
        """Les envahisseurs qui descendent sur un abri le rongent."""
        if y1 <= BUNK_Y or y0 >= BUNK_Y + 20:
            return
        j0 = (y0 - BUNK_Y) >> 2 if y0 > BUNK_Y else 0
        j1 = (y1 - 1 - BUNK_Y) >> 2
        if j1 > 4:
            j1 = 4
        bk = self.bk
        for b in range(4):
            bx = BUNK_X[b]
            if x1 <= bx or x0 >= bx + 32:
                continue
            c0 = (x0 - bx) >> 2 if x0 > bx else 0
            c1 = (x1 - 1 - bx) >> 2
            if c1 > 7:
                c1 = 7
            hit = False
            for j in range(j0, j1 + 1):
                for c in range(c0, c1 + 1):
                    k = b * 40 + j * 8 + c
                    if bk[k]:
                        bk[k] = 0
                        hit = True
            if hit:
                self.t.fill_rect(bx + c0 * 4, BUNK_Y + j0 * 4, (c1 - c0 + 1) * 4, (j1 - j0 + 1) * 4, BLACK)

    # --- formation ----------------------------------------------------------
    def draw_row(self, r, old_y):
        x0 = self.rx[r]
        y = self.ry[r]
        lo = x0 + self.cmin * CS - IPX
        hi = x0 + self.cmax * CS + IW + IPX
        if old_y is not None:
            self.t.fill_rect(lo, old_y, hi - lo, DY, BLACK)
        if y + IH > BUNK_Y:
            self.crush(lo, hi, y if old_y is None else old_y, y + IH)
        spr = self.inv[KIND[r]][self.anim]
        a = self.alive
        base = r * COLS
        put = self.put
        for c in range(COLS):
            if a[base + c]:
                put(spr, x0 + c * CS, y)

    def march(self):
        # Une rangee par image, comme la borne : la formation ondule et accelere.
        if self.ci >= len(self.cyc):
            if self.rest > 0:
                self.rest -= 1
                return
            cyc = [r for r in (3, 2, 1, 0) if self.rowcnt[r]]
            if not cyc:
                return
            self.cyc = cyc
            self.ci = 0
            n = self.n
            s = 2 if n > 10 else (3 if n > 5 else (4 if n > 2 else 5))
            self.stepx = s
            x = self.rx[cyc[0]]
            if (self.dir > 0 and x + self.cmax * CS + IW + s > W - IPX) or \
                    (self.dir < 0 and x + self.cmin * CS - s < IPX):
                self.drop = True
                self.dir = -self.dir
            else:
                self.drop = False
            self.anim ^= 1
            self.sfx.tone(BEAT[self.beat & 3], 50)
            self.beat += 1
        r = self.cyc[self.ci]
        self.ci += 1
        if self.rowcnt[r]:
            if self.drop:
                old = self.ry[r]
                self.ry[r] = old + DY
                self.draw_row(r, old)
            else:
                self.rx[r] += self.dir * self.stepx
                self.draw_row(r, None)
            if self.ry[r] + IH >= CANNON_Y:
                self.result = "INVASION !"
                self.lives = 1
                self.hit()
                return
        if self.ci >= len(self.cyc):
            self.rest = max(0, (self.n - 6) // 5 - (self.wave - 1) // 2)

    def kill(self, r, c):
        self.alive[r * COLS + c] = 0
        self.rowcnt[r] -= 1
        self.n -= 1
        x = self.rx[r] + c * CS
        y = self.ry[r]
        self.put(self.pop, x, y)
        self.pops.append((x, y, self.frame + 7))
        self.score += PTS[KIND[r]]
        self.sfx.tone(260, 70)
        a = self.alive
        lo, hi = COLS, -1
        for k in range(COLS):
            for j in range(ROWS):
                if a[j * COLS + k]:
                    if k < lo:
                        lo = k
                    hi = k
                    break
        if hi >= 0:
            self.cmin, self.cmax = lo, hi

    # --- tirs ---------------------------------------------------------------
    def shoot(self, mx, y0, old):
        t = self.t
        y1 = old + 8
        for b in self.bombs:
            if b[0] < mx + 2 and mx < b[0] + 6 and b[1] < y1 and b[1] + 8 > y0:
                t.fill_rect(mx, old, 2, 8, BLACK)
                self.bombs.remove(b)
                t.fill_rect(b[0], b[1], 6, 8, BLACK)
                self.sfx.tone(900, 30)
                return True
        if y1 > BUNK_Y and y0 < BUNK_Y + 20:
            k = self.bunker_find(mx, mx + 1, y0, y1, False)
            if k >= 0:
                t.fill_rect(mx, old, 2, 8, BLACK)
                self.damage(k)
                return True
        for r in (3, 2, 1, 0):
            if self.rowcnt[r]:
                y = self.ry[r]
                if y < y1 and y + IH > y0:
                    dx = mx - self.rx[r]
                    c = dx // CS
                    if 0 <= c < COLS:
                        off = dx - c * CS
                        a, b = HITX[KIND[r]]
                        if off + 2 > a and off < b and self.alive[r * COLS + c]:
                            t.fill_rect(mx, old, 2, 8, BLACK)
                            self.kill(r, c)
                            return True
        u = self.ufo
        if u and y0 < UFO_Y + 14 and y1 > UFO_Y and mx + 2 > u[0] + 2 and mx < u[0] + UFO_W - 2:
            t.fill_rect(mx, old, 2, 8, BLACK)
            self.ufo_hit(u[0])
            return True
        return False

    def ufo_hit(self, x):
        self.ufo = None
        self.next_ufo = self.frame + random.randint(600, 900)
        self.clear(max(0, x - 2), UFO_Y, min(W, x + UFO_W + 2) - max(0, x - 2), 14)
        pts = UFO_PTS[random.randint(0, 3)]
        self.score += pts
        s = "%d" % pts
        lx = max(0, min(W - 8 * len(s), x + (UFO_W - 8 * len(s)) // 2))
        draw_text(self.t, s, lx, UFO_Y + 3, RED, BLACK)
        self.label = (lx, self.frame + 30, len(s))
        self.sfx.tone(1500, 120)

    def drop_bomb(self):
        a = self.alive
        aimed = random.getrandbits(2) == 0
        if aimed:
            cx = self.cx + CW // 2
            c = (cx - self.rx[3] - IW // 2 + CS // 2) // CS
            c = max(self.cmin, min(self.cmax, c))
        else:
            c = random.randint(self.cmin, self.cmax)
        for r in (3, 2, 1, 0):
            if a[r * COLS + c]:
                self.bombs.append([self.rx[r] + c * CS + 9, self.ry[r] + IH + 3, 1 if aimed else 0])
                return

    def hit(self):
        self.lives -= 1
        self.dead = 36
        self.sfx.tone(110, 400)
        for b in self.bombs:
            self.t.fill_rect(b[0], b[1], 6, 8, BLACK)
        self.bombs = []
        if self.my is not None:
            self.t.fill_rect(self.mx, self.my, 2, 8, BLACK)
            self.my = None

    def dying(self):
        self.dead -= 1
        d = self.dead
        if d & 3 == 3:
            self.put(self.blast[(d >> 2) & 1], self.cx, CANNON_Y)
        if d == 0:
            self.clear(self.cx - CPX, CANNON_Y, CW + 2 * CPX, 16)
            self.cdirty = True
            return self.lives > 0
        return True

    # --- boucle -------------------------------------------------------------
    def step(self, pt, now):
        self.frame += 1
        f = self.frame
        t = self.t
        if self.pops:
            keep = []
            for p in self.pops:
                if f >= p[2]:
                    t.fill_rect(p[0], p[1], IW, IH, BLACK)
                else:
                    keep.append(p)
            self.pops = keep
        if self.label and f >= self.label[1]:
            t.fill_rect(self.label[0], UFO_Y + 3, 8 * self.label[2], 8, BLACK)
            self.label = None
        if self.dead:
            return self.dying()

        if pt:
            self.target = pt[0] - CW // 2
        d = self.target - self.cx
        d = CPX if d > CPX else (-CPX if d < -CPX else d)
        nx = self.cx + d
        nx = CPX if nx < CPX else (W - CW - CPX if nx > W - CW - CPX else nx)
        if nx != self.cx or self.cdirty:
            self.cx = nx
            self.cdirty = False
            self.put(self.cannon, nx, CANNON_Y)

        self.march()
        if self.dead:
            return True

        if pt and self.my is None and f >= self.reload:
            self.mx = self.cx + 12
            self.my = CANNON_Y - 8
            self.sfx.tone(1300, 25)
        if self.my is not None:
            mx = self.mx
            old = self.my
            my = old - MV
            if self.shoot(mx, my, old):
                self.my = None
                self.reload = f + 3
            elif my < HUD + 4:
                t.fill_rect(mx, old, 2, 8, BLACK)
                self.my = None
                self.reload = f + 2
            else:
                self.put(self.mspr, mx, my)
                self.my = my

        wave = self.wave
        if self.n and len(self.bombs) < min(4, 1 + wave) and random.getrandbits(8) < 5 + 2 * wave:
            self.drop_bomb()
        if self.bombs:
            bv = 3 if wave < 3 else (4 if wave < 5 else 5)
            fr = (f >> 2) & 1
            cx = self.cx
            keep = []
            for b in self.bombs:
                bx = b[0]
                old = b[1]
                by = old + bv
                if by + 8 >= GROUND_Y:
                    t.fill_rect(bx, old, 6, 8, BLACK)
                    continue
                if by + 8 > BUNK_Y and old < BUNK_Y + 20:
                    k = self.bunker_find(bx, bx + 5, old, by + 8, True)
                    if k >= 0:
                        t.fill_rect(bx, old, 6, 8, BLACK)
                        self.damage(k)
                        if k % 40 < 32 and self.bk[k + 8]:
                            self.damage(k + 8)
                        continue
                if bx < cx + CW - 2 and bx + 6 > cx + 2 and by + 8 > CANNON_Y + 2 and old < CANNON_Y + 16:
                    t.fill_rect(bx, old, 6, 8, BLACK)
                    self.hit()
                    return True
                b[1] = by
                self.put(self.bspr[b[2]][fr], bx, by - BVM)
                keep.append(b)
            self.bombs = keep

        u = self.ufo
        if u is None:
            if f >= self.next_ufo and self.n >= 6:
                d = 1 if random.getrandbits(1) else -1
                self.ufo = [-UFO_W if d > 0 else W, d]
        else:
            x = u[0] + 2 * u[1]
            u[0] = x
            if x > W or x < -UFO_W - 2:
                self.ufo = None
                self.next_ufo = f + random.randint(600, 900)
            else:
                self.put(self.ufo_spr, x, UFO_Y)
                if f & 7 == 0:
                    self.sfx.tone(1100 if f & 8 else 950, 40)

        if not self.bonus and self.score >= 1500:
            self.bonus = True
            self.lives = min(5, self.lives + 1)
            self.sfx.tone(1760, 200)

        if self.n == 0:
            self.score += 100 * wave
            self.text_c("VAGUE %d" % (wave + 1), 150, GOLD, 2)
            self.sfx.tune(((523, 80), (659, 80), (784, 140)))
            self.new_wave()
        return True

    def bot(self, n):
        if not hasattr(self, "alive"):
            return (120, 160) if n % 4 < 2 else None
        if n % 12 == 11:
            return None
        cx = self.cx + CW // 2
        tx = cx
        u = self.ufo
        if u and 0 < u[0] < W - UFO_W:
            tx = u[0] + UFO_W // 2 + u[1] * 24
        else:
            best = 999
            for r in (3, 2, 1, 0):
                if self.rowcnt[r]:
                    for c in range(COLS):
                        if self.alive[r * COLS + c]:
                            x = self.rx[r] + c * CS + IW // 2
                            if abs(x - cx) < abs(best - cx):
                                best = x
                    break
            if best < 999:
                tx = best + self.dir * 6
        if (n // 60) % 3:
            for b in self.bombs:
                if b[1] > 170 and abs(b[0] + 3 - cx) < 20:
                    tx = cx + (40 if b[0] + 3 < cx else -40)
                    break
        tx += (n // 40) % 5 * 3 - 6
        return (max(8, min(232, tx)), 300)


GAME = Envahisseurs


def play(tft, touch, day):
    GAME(tft, touch, day).run()
