"""Jour 12 : BLOCS 80. Deplacer et tourner les pieces qui tombent pour completer des lignes."""

import random
import time

from arcade import BLACK, CYAN, GOLD, GREY, PINK, VIOLET, WHITE, Game, rgb, sprite
from font8 import draw_text, glyph

COLS = 10
ROWS = 20
CELL = 11
WX = 14
WY = 28
NX = 141
NY = 42
BY = 262
BH = 54
LOCK = 350
GRAV = (800, 680, 570, 470, 380, 300, 240, 190, 150, 120, 95, 75, 60)
LINE_PTS = (0, 100, 300, 500, 800)
WELL = rgb(10, 10, 34)
BTN = rgb(50, 16, 90)
BTN_HI = rgb(100, 50, 160)
KICKS = ((0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0))

COLORS = ((0, 230, 255), (255, 215, 0), (190, 70, 255), (40, 230, 80), (255, 50, 60), (50, 110, 255), (255, 140, 20))
SHAPES = (
    (4, ((0, 1), (1, 1), (2, 1), (3, 1))),
    (2, ((0, 0), (1, 0), (0, 1), (1, 1))),
    (3, ((1, 0), (0, 1), (1, 1), (2, 1))),
    (3, ((1, 0), (2, 0), (0, 1), (1, 1))),
    (3, ((0, 0), (1, 0), (1, 1), (2, 1))),
    (3, ((0, 0), (0, 1), (1, 1), (2, 1))),
    (3, ((2, 0), (0, 1), (1, 1), (2, 1))),
)

TILE = (
    "llllllllll.",
    "llllllllld.",
    "llbbbbbbdd.",
    "llbwbbbbdd.",
    "llbbbbbbdd.",
    "llbbbbbbdd.",
    "llbbbbbbdd.",
    "llbbbbbbdd.",
    "lddddddddd.",
    "dddddddddd.",
    "...........",
)
EMPTY = ("...........",) * 5 + (".....g.....",) + ("...........",) * 5
ROT_ICON = (
    "..wwww.w",
    ".w....ww",
    "w....www",
    "w.......",
    "w.......",
    "w......w",
    ".w....w.",
    "..wwww..",
)
DOWN_ICON = (
    "..wwww..",
    "..wwww..",
    "..wwww..",
    "wwwwwwww",
    ".wwwwww.",
    "..wwww..",
    "...ww...",
    "........",
)
PREVIEW = (
    "....3.....",
    "...333....",
    "..........",
    "..........",
    "1.......7.",
    "1.55..6.7.",
    "1.2556667.",
    "1.22.44477",
)


def _rotations():
    out = []
    for n, cells in SHAPES:
        rots = []
        for _ in range(4):
            rots.append(cells)
            cells = tuple((n - 1 - y, x) for x, y in cells)
        out.append(rots)
    return out


ROT = _rotations()


class Blocs(Game):
    TITLE = "BLOCS 80"
    HELP = ("COMPLETE DES LIGNES", "BOUTONS < TOURNE > BAS", "BAS DEUX FOIS : CHUTE")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        dot = {"g": rgb(40, 40, 84)}
        self.tiles = [sprite(EMPTY, dot, 1, WELL)]
        for r, g, b in COLORS:
            pal = {"l": rgb(r + (255 - r) // 2, g + (255 - g) // 2, b + (255 - b) // 2),
                   "b": rgb(r, g, b), "d": rgb(r // 2, g // 2, b // 2), "w": WHITE}
            self.tiles.append(sprite(TILE, pal, 1, WELL))
        self.row0 = sprite(tuple(r * COLS for r in EMPTY), dot, 1, WELL)
        self.big = []
        for d in "0123456789":
            g = glyph(d)
            rows = tuple("".join("x" if g[j] & (0x80 >> i) else "." for i in range(8)) for j in range(8))
            self.big.append(sprite(rows, {"x": GOLD}, 2, BLACK))
        self.icons = (sprite(ROT_ICON, {"w": WHITE}, 2, BTN), sprite(DOWN_ICON, {"w": WHITE}, 2, BTN))

    def preview(self, y):
        t = self.t
        x0 = 65
        t.fill_rect(x0 - 3, y + 1, COLS * CELL + 6, 94, PINK)
        t.fill_rect(x0 - 1, y + 3, COLS * CELL + 2, 90, WELL)
        for j, row in enumerate(PREVIEW):
            for i, ch in enumerate(row):
                spr = self.tiles[0 if ch == "." else int(ch)]
                t.blit(spr[0], x0 + i * CELL, y + 4 + j * CELL, CELL, CELL)

    # --- decor -------------------------------------------------------------
    def setup(self):
        t = self.t
        t.fill_rect(WX - 4, WY - 4, COLS * CELL + 8, ROWS * CELL + 8, PINK)
        t.fill_rect(WX - 2, WY - 2, COLS * CELL + 4, ROWS * CELL + 4, VIOLET)
        t.fill_rect(WX - 1, WY - 1, COLS * CELL + 2, ROWS * CELL + 2, BLACK)
        self.draw_well()
        draw_text(t, "SUIVANT", 157, 30, CYAN, BLACK)
        t.fill_rect(NX - 2, NY - 2, 92, 48, PINK)
        t.fill_rect(NX, NY, 88, 44, WELL)
        draw_text(t, "NIVEAU", 161, 100, CYAN, BLACK)
        draw_text(t, "LIGNES", 161, 138, CYAN, BLACK)
        draw_text(t, "80", 155, 196, VIOLET, None, 4)
        draw_text(t, "80", 152, 193, PINK, None, 4)
        for i in range(4):
            x = i * 60
            t.fill_rect(x + 2, BY, 56, BH, PINK)
            t.fill_rect(x + 4, BY + 2, 52, BH - 4, BTN)
            t.fill_rect(x + 4, BY + 2, 52, 3, BTN_HI)
            if i == 0 or i == 2:
                draw_text(t, "<" if i == 0 else ">", x + 18, BY + 12, WHITE, None, 3)
            else:
                spr = self.icons[i // 2]
                t.blit(spr[0], x + 22, BY + 9, 16, 16)
                s = "TOURNE" if i == 1 else "BAS"
                draw_text(t, s, x + 30 - len(s) * 4, BY + 30, WHITE, BTN)
            self.light(i, False)
        self.grid = bytearray(COLS * ROWS)
        self.bag = []
        self.nxt = self.pick()
        self.lines = 0
        self.level = 1
        self.grav = GRAV[0]
        self.held = -1
        self.soft_ok = False
        self.pieces = 0
        self.wait = False
        self.shown_lv = None
        self.shown_ln = None
        self.draw_nums()
        now = time.ticks_ms()
        self.last_bas = time.ticks_add(now, -1000)
        self.spawn(now)

    def draw_well(self):
        buf, w, h = self.row0[0], self.row0[1], self.row0[2]
        for y in range(ROWS):
            self.t.blit(buf, WX, WY + y * CELL, w, h)

    def light(self, i, on):
        if i >= 0:
            self.t.fill_rect(i * 60 + 10, BY + BH - 9, 40, 3, GOLD if on else BTN_HI)

    def number(self, s, old, x, y):
        for k in range(len(s)):
            if old is None or old[k] != s[k]:
                self.t.blit(self.big[ord(s[k]) - 48][0], x + k * 16, y, 16, 16)
        return s

    def draw_nums(self):
        self.shown_lv = self.number("%02d" % min(self.level, 99), self.shown_lv, 169, 112)
        self.shown_ln = self.number("%03d" % min(self.lines, 999), self.shown_ln, 161, 150)

    def draw_next(self):
        t = self.t
        t.fill_rect(NX, NY, 88, 44, WELL)
        cells = ROT[self.nxt][0]
        x0 = min(c[0] for c in cells)
        x1 = max(c[0] for c in cells)
        y0 = min(c[1] for c in cells)
        y1 = max(c[1] for c in cells)
        ox = NX + (88 - (x1 - x0 + 1) * CELL) // 2 - x0 * CELL
        oy = NY + (44 - (y1 - y0 + 1) * CELL) // 2 - y0 * CELL
        buf = self.tiles[self.nxt + 1][0]
        for x, y in cells:
            t.blit(buf, ox + x * CELL, oy + y * CELL, CELL, CELL)

    def cell(self, x, y, v):
        if y >= 0:
            self.t.blit(self.tiles[v][0], WX + x * CELL, WY + y * CELL, CELL, CELL)

    # --- pieces ------------------------------------------------------------
    def pick(self):
        if not self.bag:
            b = [0, 1, 2, 3, 4, 5, 6]
            for i in range(6, 0, -1):
                j = random.randint(0, i)
                b[i], b[j] = b[j], b[i]
            self.bag = b
        return self.bag.pop()

    def fits(self, k, r, px, py):
        g = self.grid
        for dx, dy in ROT[k][r]:
            x = px + dx
            y = py + dy
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and g[y * COLS + x]:
                return False
        return True

    def cells(self, k, r, px, py):
        return [(px + dx, py + dy) for dx, dy in ROT[k][r]]

    def try_move(self, r, px, py):
        k = self.k
        if not self.fits(k, r, px, py):
            return False
        old = self.cells(k, self.r, self.px, self.py)
        new = self.cells(k, r, px, py)
        for c in old:
            if c not in new:
                self.cell(c[0], c[1], 0)
        for c in new:
            if c not in old:
                self.cell(c[0], c[1], k + 1)
        self.r, self.px, self.py = r, px, py
        return True

    def spawn(self, now):
        self.k = k = self.nxt
        self.nxt = self.pick()
        self.r = 0
        self.px = 4 if k == 1 else 3
        self.py = -1 if k == 0 else 0
        self.land = 0
        self.soft_ok = False
        self.next_fall = time.ticks_add(now, self.grav)
        self.pieces += 1
        self.draw_next()
        if not self.fits(k, 0, self.px, self.py):
            return self.top_out()
        for x, y in self.cells(k, 0, self.px, self.py):
            self.cell(x, y, k + 1)
        return True

    def rotate(self):
        if self.k == 1:
            return
        r = (self.r + 1) & 3
        for dx, dy in KICKS:
            if self.try_move(r, self.px + dx, self.py + dy):
                self.sfx.tone(700, 15)
                return

    def shift(self, d):
        if self.try_move(self.r, self.px + d, self.py):
            self.sfx.tone(330, 8)

    def hard_drop(self, now):
        y = self.py
        while self.fits(self.k, self.r, self.px, y + 1):
            y += 1
        self.score += 2 * (y - self.py)
        self.try_move(self.r, self.px, y)
        self.sfx.tone(200, 40)
        self.last_bas = time.ticks_add(now, -1000)
        return self.lock(now)

    def lock(self, now):
        g = self.grid
        rows = []
        for x, y in self.cells(self.k, self.r, self.px, self.py):
            if y < 0:
                return self.top_out()
            g[y * COLS + x] = self.k + 1
            if y not in rows:
                rows.append(y)
        full = [y for y in rows if min(g[y * COLS:y * COLS + COLS])]
        if full:
            self.clear_lines(full)
        else:
            self.sfx.tone(150, 25)
        # La piece suivante apparait a l'image d'apres : deux images moins chargees.
        self.wait = True
        return True

    def clear_lines(self, full):
        t = self.t
        full.sort()
        n = len(full)
        for c in (WHITE, GOLD, WHITE):
            for y in full:
                t.fill_rect(WX, WY + y * CELL, COLS * CELL, CELL - 1, c)
            self.sfx.tone(660 + 220 * n, 50)
            time.sleep_ms(60)
        g = self.grid
        old = bytearray(g)
        for y in full:
            for x in range(COLS):
                old[y * COLS + x] = 255
        ng = bytearray(COLS * ROWS)
        d = ROWS
        for y in range(ROWS - 1, -1, -1):
            if y not in full:
                d -= 1
                ng[d * COLS:d * COLS + COLS] = g[y * COLS:y * COLS + COLS]
        self.grid = ng
        for i in range((full[-1] + 1) * COLS):
            if ng[i] != old[i]:
                self.cell(i % COLS, i // COLS, ng[i])
        self.lines += n
        self.score += LINE_PTS[n] * self.level
        if n == 4:
            self.sfx.tune(((523, 60), (659, 60), (784, 60), (1047, 160)))
        lv = 1 + self.lines // 10
        if lv != self.level:
            self.level = lv
            self.grav = GRAV[min(lv - 1, len(GRAV) - 1)]
            self.sfx.tune(((660, 70), (880, 70), (1320, 140)))
        self.draw_nums()

    def top_out(self):
        self.lives -= 1
        self.sfx.tone(110, 500)
        t = self.t
        for y in range(ROWS - 1, -1, -1):
            t.fill_rect(WX, WY + y * CELL, COLS * CELL, CELL - 1, GREY)
            time.sleep_ms(20)
        if self.lives <= 0:
            return False
        time.sleep_ms(400)
        self.grid = bytearray(COLS * ROWS)
        self.draw_well()
        return self.spawn(time.ticks_ms())

    # --- boucle ------------------------------------------------------------
    def button(self, pt):
        if pt is None or pt[1] < BY - 6:
            return -1
        return min(3, pt[0] // 60)

    def step(self, pt, now):
        if self.wait:
            self.wait = False
            return self.spawn(now)
        b = self.button(pt)
        if b != self.held:
            self.light(self.held, False)
            self.light(b, True)
            self.held = b
            self.rep = time.ticks_add(now, 180)
            if b == 0 or b == 2:
                self.shift(b - 1)
            elif b == 1:
                self.rotate()
            elif b == 3:
                if time.ticks_diff(now, self.last_bas) < 300:
                    return self.hard_drop(now)
                self.last_bas = now
                self.next_fall = now
        elif (b == 0 or b == 2) and time.ticks_diff(now, self.rep) >= 0:
            self.rep = time.ticks_add(now, 65)
            self.shift(b - 1)
        if b != 3:
            self.soft_ok = True
        soft = b == 3 and self.soft_ok
        if time.ticks_diff(now, self.next_fall) >= 0:
            self.next_fall = time.ticks_add(now, 35 if soft else self.grav)
            if self.try_move(self.r, self.px, self.py + 1):
                self.land = 0
                if soft:
                    self.score += 1
            elif not self.land:
                self.land = now
        if self.land and time.ticks_diff(now, self.land) >= (120 if soft else LOCK):
            if self.fits(self.k, self.r, self.px, self.py + 1):
                self.land = 0
            else:
                return self.lock(now)
        return True

    # --- doigt simule --------------------------------------------------------
    def plan(self):
        g = self.grid
        top = [ROWS] * COLS
        cnt = [0] * ROWS
        for i in range(COLS * ROWS):
            if g[i]:
                x = i % COLS
                y = i // COLS
                if y < top[x]:
                    top[x] = y
                cnt[y] += 1
        k = self.k
        best = None
        cand = []
        for r in range(1 if k == 1 else 4):
            cells = ROT[k][r]
            lo = -min(c[0] for c in cells)
            hi = COLS - max(c[0] for c in cells)
            for px in range(lo, hi):
                py = min(top[px + dx] - 1 - dy for dx, dy in cells)
                nt = top[:]
                add = {}
                deep = {}
                for dx, dy in cells:
                    x = px + dx
                    y = py + dy
                    if y < nt[x]:
                        nt[x] = y
                    add[y] = add.get(y, 0) + 1
                    if y > deep.get(x, -99):
                        deep[x] = y
                lines = 0
                for y in add:
                    if y >= 0 and cnt[y] + add[y] == COLS:
                        lines += 1
                holes = 0
                for x in deep:
                    holes += top[x] - 1 - deep[x]
                agg = 0
                bump = 0
                for x in range(COLS):
                    agg += ROWS - nt[x]
                    if x:
                        bump += abs(nt[x] - nt[x - 1])
                s = 76 * lines - 51 * agg - 36 * holes - 18 * bump
                cand.append((r, px))
                if best is None or s > best[0]:
                    best = (s, r, px)
        if random.getrandbits(2) == 0:
            r, px = cand[random.randint(0, len(cand) - 1)]
            return r, px, random.getrandbits(1)
        return best[1], best[2], random.getrandbits(1)

    def bot(self, n):
        if not hasattr(self, "grid") or self.lives <= 0:
            return (120, 160) if n % 4 < 2 else None
        if getattr(self, "bp", -1) != self.pieces:
            self.bp = self.pieces
            self.bt = self.plan()
            self.bn = 0
        tr, tx, hard = self.bt
        self.bn += 1
        y = BY + BH // 2
        if self.bn < 60 and (self.r != tr or self.px != tx):
            if n % 2:
                return None
            if self.r != tr:
                return (90, y)
            return (30, y) if self.px > tx else (150, y)
        if hard:
            return (210, y) if n % 2 == 0 else None
        return (210, y)


GAME = Blocs


def play(tft, touch, day):
    GAME(tft, touch, day).run()
