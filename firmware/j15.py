"""Jour 15 : MINEUR 80. Creuser, ramasser les diamants sans se faire ecraser, puis filer a la sortie."""

import random
import time

from arcade import BLACK, CYAN, GOLD, NIGHT, PINK, RED, WHITE, W, Game, rgb, sprite
from font8 import draw_text

COLS = 12
ROWS = 13
N = COLS * ROWS
CELL = 20
Y0 = 24
BAND = Y0 + ROWS * CELL
MOVE_F = 5
EMPTY = 0
DIRT = 1
WALL = 2
ROCK = 3
GEM = 4
EXIT = 5
OPEN = 6
MINER = 7
F = 16

DIRT_ART = (
    "bbbdbbbbbb",
    "bbbbbbbdbb",
    "bdbbblbbbb",
    "bbbbbdbbbb",
    "bbbbbbbbdb",
    "bbdbbbbbbb",
    "bbbbbbdbbb",
    "blbbbbbbbb",
    "bdbbbbbbdb",
    "bbbbdbbbbb",
)
WALL_ART = (
    "rrrrhmrrrr",
    "rrrrrmrrrr",
    "rrrrrmrrrr",
    "mmmmmmmmmm",
    "rrmrrrrhmr",
    "rrmrrrrrmr",
    "rrmrrrrrmr",
    "mmmmmmmmmm",
    "rrrrhmrrrr",
    "rrrrrmrrrr",
)
ROCK_ART = (
    "...gggg...",
    ".gGGGGgg..",
    ".gGwGGGgg.",
    "gGwGGGGGgk",
    "gGGGGGGGgk",
    "gGGGGGGggk",
    "ggGGGGgggk",
    ".gggggggk.",
    "..gggggkk.",
    "...kkkk...",
)
GEM_ART = (
    "..........",
    "...cccc...",
    "..cwwccC..",
    ".cwcccCCC.",
    "cccccccCCC",
    ".cccccCCC.",
    "..cccCCC..",
    "...cCCC...",
    "....CC....",
    "..........",
)
DOOR_ART = (
    "hhhhhhhhhk",
    "hggggggggk",
    "hgwggggwgk",
    "hggkkkkggk",
    "hggkyykggk",
    "hggkyykggk",
    "hggkkkkggk",
    "hgwggggwgk",
    "hggggggggk",
    "kkkkkkkkkk",
)
MINER_ART = (
    (
        "...yyyy...",
        "..yyyyyyw.",
        "..ssssss..",
        "..sssksk..",
        "...ssss...",
        ".bbbbbbbs.",
        "s.bbbbb...",
        "..bbbbb...",
        "..bb.bb...",
        ".kk...kk..",
    ),
    (
        "...yyyy...",
        "..yyyyyyw.",
        "..ssssss..",
        "..sssksk..",
        "...ssss...",
        "..bbbbbbs.",
        ".sbbbbb...",
        "..bbbbb...",
        "...bbb....",
        "...kkk....",
    ),
)
BOOM_ART = (
    "y..o..o..y",
    ".o.yooy.o.",
    "..oywwyo..",
    ".oywwwwyo.",
    "oywwwwwwyo",
    "oywwwwwwyo",
    ".oywwwwyo.",
    "..oywwyo..",
    ".o.yooy.o.",
    "y..o..o..y",
)
MINER_PAL = {"y": rgb(255, 210, 0), "w": WHITE, "s": rgb(255, 190, 140), "k": rgb(40, 30, 30),
             "b": rgb(60, 110, 255)}
BOOM_PAL = {"y": rgb(255, 230, 60), "o": rgb(255, 120, 30), "w": WHITE}


def _rev(s):
    c = list(s)
    c.reverse()
    return "".join(c)


class Mineur(Game):
    TITLE = "MINEUR 80"
    HELP = ("GARDE LE DOIGT : LE MINEUR", "CREUSE VERS TON DOIGT", "DIAMANTS PUIS SORTIE")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        mk = lambda art, pal: sprite(art, pal, 2, BLACK)
        gem = {"c": CYAN, "C": rgb(0, 110, 210), "w": WHITE}
        door = {"h": rgb(170, 170, 190), "g": rgb(100, 100, 120), "k": rgb(40, 40, 50), "w": WHITE,
                "y": rgb(60, 60, 70)}
        self.spr = [
            None,
            mk(DIRT_ART, {"b": rgb(150, 80, 30), "d": rgb(90, 45, 15), "l": rgb(210, 130, 60)}),
            mk(WALL_ART, {"r": rgb(200, 60, 40), "h": rgb(255, 130, 90), "m": rgb(90, 90, 100)}),
            mk(ROCK_ART, {"g": rgb(120, 120, 135), "G": rgb(175, 175, 190), "w": WHITE, "k": rgb(60, 60, 72)}),
            mk(GEM_ART, gem),
            mk(DOOR_ART, door),
            mk(DOOR_ART, {"h": GOLD, "g": PINK, "k": rgb(120, 20, 90), "w": WHITE, "y": GOLD}),
        ]
        self.door2 = mk(DOOR_ART, {"h": PINK, "g": GOLD, "k": rgb(160, 80, 0), "w": WHITE, "y": PINK})
        self.spark = mk(GEM_ART, {"c": WHITE, "C": CYAN, "w": WHITE})
        self.miners = []
        for art in MINER_ART:
            self.miners.append(mk(art, MINER_PAL))
        for art in MINER_ART:
            self.miners.append(mk(tuple(_rev(r) for r in art), MINER_PAL))
        self.boom = mk(BOOM_ART, BOOM_PAL)

    def preview(self, y):
        t = self.t
        scene = ("1133411", "1400041", "1307331", "2222201", "4100056")
        x0 = (W - 7 * CELL) // 2
        for j, row in enumerate(scene):
            for i, ch in enumerate(row):
                v = int(ch)
                spr = self.miners[0] if v == MINER else self.spr[v]
                if spr is None:
                    t.fill_rect(x0 + i * CELL, y + 2 + j * CELL, CELL, CELL, BLACK)
                else:
                    t.blit(spr[0], x0 + i * CELL, y + 2 + j * CELL, CELL, CELL)

    # --- niveaux -------------------------------------------------------------
    def setup(self):
        t = self.t
        t.fill_rect(0, BAND, W, 320 - BAND, NIGHT)
        t.fill_rect(0, BAND + 1, W, 2, PINK)
        t.blit(self.spr[GEM][0], 4, BAND + 8, CELL, CELL)
        self.level = 1
        self.fc = 0
        self.new_level()

    def new_level(self):
        lv = self.level
        g = bytearray(N)
        for i in range(N):
            g[i] = DIRT
        for _ in range(4 + lv):
            g[random.randint(COLS, N - 1)] = EMPTY
        for _ in range(min(7, 1 + lv)):
            y = random.randint(2, ROWS - 3)
            x = random.randint(0, COLS - 4)
            for k in range(random.randint(3, 6)):
                if x + k < COLS:
                    g[y * COLS + x + k] = WALL
        for _ in range(min(44, 14 + 3 * lv)):
            i = random.randint(COLS, N - 1)
            if g[i] == DIRT:
                g[i] = ROCK
        self.need = min(20, 4 + 2 * lv)
        gems = []
        while len(gems) < self.need + 3:
            i = random.randint(COLS, N - 1)
            if g[i] == DIRT or g[i] == EMPTY:
                g[i] = GEM
                gems.append(i)
        sx = random.randint(0, 3)
        ex = random.randint(COLS - 4, COLS - 1)
        if random.getrandbits(1):
            sx, ex = COLS - 1 - sx, COLS - 1 - ex
        exit_i = (ROWS - 1) * COLS + ex
        # Chemin creuse du depart vers chaque diamant puis la sortie : tout reste accessible.
        cx, cy = sx, 0
        for tgt in gems + [exit_i]:
            tx, ty = tgt % COLS, tgt // COLS
            while (cx, cy) != (tx, ty):
                if cx != tx and (cy == ty or random.getrandbits(1)):
                    cx += 1 if tx > cx else -1
                else:
                    cy += 1 if ty > cy else -1
                j = cy * COLS + cx
                if g[j] == WALL or g[j] == ROCK:
                    g[j] = DIRT
        g[sx] = MINER
        g[exit_i] = EXIT
        self.start = (bytes(g), sx, exit_i)
        self.limit = max(60, 130 - 8 * lv)
        self.banner()
        self.restart()

    def banner(self):
        t = self.t
        t.fill(BLACK)
        self.hud()
        self.text_c("NIVEAU %d" % self.level, 130, GOLD, 2, PINK)
        self.text_c("%d DIAMANTS" % self.need, 160, CYAN)
        self.sfx.tune(((523, 80), (659, 80), (784, 120)))
        time.sleep_ms(500)
        t.fill_rect(0, BAND, W, 320 - BAND, NIGHT)
        t.fill_rect(0, BAND + 1, W, 2, PINK)
        t.blit(self.spr[GEM][0], 4, BAND + 8, CELL, CELL)

    def restart(self):
        g0, sx, exit_i = self.start
        self.grid = bytearray(g0)
        self.pos = sx
        self.exit = exit_i
        self.got = 0
        self.face = 0
        self.walk = 0
        self.dead = False
        self.sp = -1
        self.left = self.limit
        self.t_next = time.ticks_add(time.ticks_ms(), 1000)
        self.todo = []
        for i in range(N):
            v = self.grid[i]
            self.draw(i)
            if v == ROCK or v == GEM:
                self.todo.append(i)
        self.fc = 0
        self.band()

    def band(self):
        t = self.t
        draw_text(t, "/", 44, BAND + 14, WHITE, NIGHT)
        draw_text(t, "NIV", 96, BAND + 14, CYAN, NIGHT)
        draw_text(t, "TEMPS", 162, BAND + 14, GOLD, NIGHT)
        self.shown_n = [None, None, None, None]
        self.draw_count()
        self.digits_at(1, "%02d" % min(self.need, 99), 52)
        self.digits_at(2, "%02d" % min(self.level, 99), 128)
        self.draw_time()

    def digits_at(self, k, s, x):
        old = self.shown_n[k]
        for j in range(len(s)):
            if old is None or old[j] != s[j]:
                self.t.blit(self.digits[ord(s[j]) - 48], x + j * 8, BAND + 14, 8, 8)
        self.shown_n[k] = s

    def draw_count(self):
        self.digits_at(0, "%02d" % min(self.got, 99), 28)

    def draw_time(self):
        if self.left == 15:
            draw_text(self.t, "TEMPS", 162, BAND + 14, RED, NIGHT)
        self.digits_at(3, "%03d" % max(0, self.left), 210)

    def draw(self, i):
        v = self.grid[i] & 15
        x = (i % COLS) * CELL
        y = Y0 + (i // COLS) * CELL
        if v == EMPTY:
            self.t.fill_rect(x, y, CELL, CELL, BLACK)
            return
        spr = self.miners[self.face * 2 + self.walk] if v == MINER else self.spr[v]
        self.t.blit(spr[0], x, y, CELL, CELL)

    # --- physique ------------------------------------------------------------
    def wake(self, i):
        x = i % COLS
        t = self.todo
        if i >= COLS:
            a = i - COLS
            t.append(a)
            if x > 0:
                t.append(a - 1)
            if x < COLS - 1:
                t.append(a + 1)
        if x > 0:
            t.append(i - 1)
        if x < COLS - 1:
            t.append(i + 1)

    def settle(self, i, j, v):
        g = self.grid
        g[j] = v | F
        g[i] = EMPTY
        self.draw(i)
        self.draw(j)
        self.wake(i)
        self.todo.append(j)

    def physics(self):
        if not self.todo:
            return
        todo = sorted(set(self.todo))
        todo.reverse()
        self.todo = []
        g = self.grid
        for i in todo:
            v = g[i]
            k = v & 15
            if k != ROCK and k != GEM:
                continue
            x = i % COLS
            b = i + COLS
            w = g[b] & 15 if b < N else DIRT
            if w == EMPTY:
                self.settle(i, b, k)
                continue
            if w == MINER and v & F:
                if k == ROCK:
                    self.dead = True
                    return
                g[i] = EMPTY
                self.draw(i)
                self.wake(i)
                self.collect()
                continue
            if w == ROCK or w == GEM or w == WALL:
                if x > 0 and g[i - 1] == EMPTY and g[b - 1] == EMPTY:
                    self.settle(i, i - 1, k)
                    continue
                if x < COLS - 1 and g[i + 1] == EMPTY and g[b + 1] == EMPTY:
                    self.settle(i, i + 1, k)
                    continue
            if v & F:
                g[i] = k
                if k == ROCK:
                    self.sfx.tone(90, 25)

    # --- mineur --------------------------------------------------------------
    def collect(self):
        self.got += 1
        self.score += (20 if self.got > self.need else 10) * self.level
        self.sfx.tone(1320, 40)
        if self.got == self.need:
            self.grid[self.exit] = OPEN
            self.draw(self.exit)
            self.sfx.tone(1760, 120)
        self.draw_count()

    def go(self, j):
        g = self.grid
        i = self.pos
        g[i] = EMPTY
        self.draw(i)
        g[j] = MINER
        self.pos = j
        self.walk ^= 1
        self.draw(j)
        self.wake(i)

    def try_step(self, dx, dy):
        i = self.pos
        x = i % COLS + dx
        y = i // COLS + dy
        if x < 0 or x >= COLS or y < 0 or y >= ROWS:
            return 0
        if dx:
            self.face = 0 if dx > 0 else 1
        j = y * COLS + x
        v = self.grid[j]
        k = v & 15
        if k == EMPTY or k == DIRT:
            self.go(j)
            return 1
        if k == GEM:
            self.go(j)
            self.collect()
            return 1
        if k == OPEN:
            self.go(j)
            return 2
        if k == ROCK and dy == 0 and not v & F:
            b = j + dx
            if 0 <= x + dx < COLS and self.grid[b] == EMPTY:
                self.grid[b] = ROCK
                self.draw(b)
                self.todo.append(b)
                self.go(j)
                self.sfx.tone(140, 30)
                return 1
        return 0

    def move(self, pt):
        i = self.pos
        dx = pt[0] - ((i % COLS) * CELL + CELL // 2)
        dy = pt[1] - (Y0 + (i // COLS) * CELL + CELL // 2)
        ax = abs(dx)
        ay = abs(dy)
        if ax < 8 and ay < 8:
            return 0
        sx = 1 if dx > 0 else -1
        sy = 1 if dy > 0 else -1
        if ax >= ay:
            r = self.try_step(sx, 0)
            if not r and ay >= CELL // 2:
                r = self.try_step(0, sy)
        else:
            r = self.try_step(0, sy)
            if not r and ax >= CELL // 2:
                r = self.try_step(sx, 0)
        return r

    def lose(self):
        i = self.pos
        self.t.blit(self.boom[0], (i % COLS) * CELL, Y0 + (i // COLS) * CELL, CELL, CELL)
        self.sfx.tone(90, 500)
        time.sleep_ms(700)
        self.lives -= 1
        if self.lives <= 0:
            return False
        self.restart()
        return True

    def step(self, pt, now):
        self.fc += 1
        ph = self.fc % MOVE_F
        if ph == 0 and pt:
            if self.move(pt) == 2:
                self.score += self.left * 5 * self.level
                self.sfx.tune(((784, 90), (988, 90), (1175, 90), (1568, 220)))
                self.level += 1
                if self.level % 3 == 1 and self.lives < 5:
                    self.lives += 1
                self.new_level()
                return True
        elif ph == 2:
            self.physics()
            if self.dead:
                return self.lose()
        elif ph == 4 and self.fc % 10 == 4:
            if self.sp >= 0 and self.grid[self.sp] == GEM:
                self.draw(self.sp)
            self.sp = random.randint(0, N - 1)
            if self.grid[self.sp] == GEM:
                self.t.blit(self.spark[0], (self.sp % COLS) * CELL, Y0 + (self.sp // COLS) * CELL, CELL, CELL)
        elif ph == 1 and self.fc % 10 == 1 and self.grid[self.exit] == OPEN:
            e = self.exit
            spr = self.door2 if self.fc % 20 == 1 else self.spr[OPEN]
            self.t.blit(spr[0], (e % COLS) * CELL, Y0 + (e // COLS) * CELL, CELL, CELL)
        if time.ticks_diff(now, self.t_next) >= 0:
            self.t_next = time.ticks_add(self.t_next, 1000)
            self.left -= 1
            self.draw_time()
            if 0 < self.left <= 10:
                self.sfx.tone(880, 30)
            if self.left <= 0:
                self.text_c("TEMPS ECOULE", 150, RED, 2, BLACK)
                time.sleep_ms(600)
                return self.lose()
        return True

    # --- doigt simule --------------------------------------------------------
    def bot(self, n):
        if not hasattr(self, "grid") or self.lives <= 0:
            return (120, 160) if n % 4 < 2 else None
        g = self.grid
        start = self.pos
        if getattr(self, "bpos", -1) == start and n % 12:
            return self.bpt
        prev = bytearray(N)
        seen = bytearray(N)
        seen[start] = 1
        q = [start]
        k = 0
        goal = -1
        want = OPEN if self.got >= self.need else GEM
        while k < len(q):
            i = q[k]
            k += 1
            if g[i] == want:
                goal = i
                break
            x = i % COLS
            for j, ok in ((i + 1, x < COLS - 1), (i - 1, x > 0), (i + COLS, i + COLS < N), (i - COLS, i >= COLS)):
                if ok and not seen[j]:
                    v = g[j]
                    if v == EMPTY or v == DIRT or v == GEM or v == OPEN:
                        if j >= COLS and g[j - COLS] & F:
                            continue
                        seen[j] = 1
                        prev[j] = i
                        q.append(j)
        if goal < 0:
            j = random.randint(0, N - 1)
        else:
            j = goal
            while prev[j] != start and j != start:
                j = prev[j]
        self.bpos = start
        self.bpt = ((j % COLS) * CELL + CELL // 2, Y0 + (j // COLS) * CELL + CELL // 2)
        return self.bpt


GAME = Mineur


def play(tft, touch, day):
    GAME(tft, touch, day).run()
