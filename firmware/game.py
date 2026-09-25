"""Magic Harry : casse-briques magique, sprites pixel art."""

import math
import random
import time

import micropython
from micropython import const

from font8 import draw_text, glyph
from ili9341 import rgb

W = const(240)
H = const(320)
HUD_H = const(22)
FX = const(10)
FW = const(220)
FR = const(230)
TOP = const(32)
BY = const(50)
ROWS = const(8)
COLS = const(10)
BW = const(22)
BH = const(10)
PW = const(36)
PH = const(14)
PY = const(288)
SHIELD_Y = const(314)
BALL = const(7)

BG = rgb(10, 10, 32)
WHITE = rgb(255, 255, 255)
GOLD = rgb(255, 200, 60)
ORANGE = rgb(255, 120, 40)
PURPLE = rgb(90, 40, 150)
CYAN = rgb(80, 220, 255)
SKY = rgb(150, 240, 255)
DARK = rgb(24, 18, 48)

RUNES = (
    ("..#..", ".###.", "#.#.#", "..#..", ".#.#."),
    (".##..", "#..#.", "..#..", ".#..#", "..##."),
    ("#...#", ".#.#.", "..#..", "..#..", ".###."),
    ("#.#.#", ".###.", "..#..", ".###.", "#.#.#"),
)
LOCK = ("..#..", ".#.#.", "#...#", ".#.#.", "..#..")
CRACK = ((4, 3), (5, 4), (6, 4), (7, 5), (8, 6), (9, 6), (10, 5), (11, 4), (12, 4), (13, 5), (14, 6), (15, 6), (16, 7))

HOUSES = (
    ("MAISON DU PHENIX", (205, 45, 35), (235, 185, 45)),
    ("MAISON DE LA VOUIVRE", (40, 160, 80), (175, 185, 195)),
    ("MAISON DE LA LICORNE", (45, 90, 210), (190, 120, 55)),
    ("MAISON DE LA SALAMANDRE", (235, 200, 45), (80, 70, 95)),
)

LEVELS = (
    ("..aaaaaa..", ".abbbbbba.", "abbsbbsbba", "abbbbbbbba", ".aabbbbaa.", "..aa..aa..", ".a......a.", "s........s"),
    ("s.s.s.s.s.", ".a.a.a.a.a", "b.b.b.b.b.", ".a.a.a.a.a", "b.b.b.b.b.", ".a.a.a.a.a", "..........", "ssssssssss"),
    ("....ss....", "...sbbs...", "..sbaabs..", ".sbaaaabs.", "sbaaaaaabs", ".sbaaaabs.", "..sbaabs..", "...sbbs..."),
    ("aaaaaaaaaa", "b........b", "b.aaaaaa.b", "b.bssssb.b", "b.bssssb.b", "b.aaaaaa.b", "b........b", "aaaaaaaaaa"),
)

WIZARD = (
    "................kk",
    "...............khHk",
    "..............khhHk..........w",
    ".............khyhhHk........wyw",
    "...........kkkkkkkkkkk.......wk",
    "............kssssssk........kW",
    "............kskssksk.......kW",
    "............kssssssk......kW",
    "...........krrrsssrrk...kW",
    "..GG......krrrrrrrrrRkkssk",
    ".GggG.kkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "GgGgGkbbbbbbbbbbbbbbbbbbbbbbbbbbbbbk",
    ".GgGgkBBBBBrrRBBBBBBBrrRBBBBBBBBBBk",
    "..GG..kkkkkRRkkkkkkkkRRkkkkkkkkkkk",
)
WIZ_PAL = {
    "k": rgb(20, 12, 30),
    "h": rgb(130, 60, 210),
    "H": rgb(70, 25, 130),
    "y": rgb(255, 220, 60),
    "s": rgb(250, 200, 150),
    "r": rgb(60, 90, 220),
    "R": rgb(30, 45, 140),
    "b": rgb(160, 100, 45),
    "B": rgb(100, 55, 20),
    "g": rgb(245, 205, 90),
    "G": rgb(185, 135, 40),
    "w": WHITE,
    "W": rgb(120, 70, 30),
}

ORB = (".kccck.", "kcwwcck", "cwwcccv", "cwcccvv", "ccccvvv", "kccvvvk", ".kvvvk.")
ORB_PAL = {"k": rgb(60, 20, 110), "c": rgb(90, 220, 255), "w": WHITE, "v": rgb(160, 80, 255)}

BOLT = (".w.", "wyw", "wyw", ".y.", ".y.", ".o.", ".o.")
BOLT_PAL = {"w": WHITE, "y": rgb(255, 240, 120), "o": ORANGE}

GLYPHS = {
    "B": ("##.", "#.#", "##.", "#.#", "##."),
    "M": ("#.#", "###", "###", "#.#", "#.#"),
    "T": ("###", ".#.", ".#.", ".#.", ".#."),
    "F": ("..#..", ".###.", "#####", ".###.", ".#.#."),
}
CAPS = {"B": (40, 120, 255), "M": (255, 130, 30), "T": (60, 200, 90), "F": (250, 210, 40)}


@micropython.viper
def _over(dst: ptr8, dw: int, spr: ptr8, msk: ptr8, sw: int, sh: int, ox: int, oy: int):
    j = 0
    while j < sh:
        i = 0
        while i < sw:
            k = j * sw + i
            if msk[k]:
                d = ((oy + j) * dw + ox + i) * 2
                dst[d] = spr[k * 2]
                dst[d + 1] = spr[k * 2 + 1]
            i += 1
        j += 1


@micropython.viper
def _region(buf: ptr8, x: int, y: int, w: int, h: int, grid: ptr8, bank: ptr8, bghi: int, bglo: int):
    fx1 = FX + COLS * BW
    by1 = BY + ROWS * BH
    o = 0
    j = 0
    while j < h:
        yy = y + j
        inrow = 0
        r = 0
        ry = 0
        if yy >= BY:
            if yy < by1:
                inrow = 1
                r = (yy - BY) // BH
                ry = yy - BY - r * BH
        i = 0
        while i < w:
            xx = x + i
            hi = bghi
            lo = bglo
            if inrow:
                if xx >= FX:
                    if xx < fx1:
                        c = (xx - FX) // BW
                        v = int(grid[r * COLS + c])
                        if v:
                            k = (v * BW * BH + ry * BW + xx - FX - c * BW) * 2
                            hi = int(bank[k])
                            lo = int(bank[k + 1])
            buf[o] = hi
            buf[o + 1] = lo
            o += 2
            i += 1
        j += 1


@micropython.viper
def _cell(grid: ptr8, x: int, y: int) -> int:
    if y >= BY:
        if y < BY + ROWS * BH:
            if x >= FX:
                if x < FX + COLS * BW:
                    i = ((y - BY) // BH) * COLS + (x - FX) // BW
                    if grid[i]:
                        return i
    return -1


@micropython.viper
def _hit(grid: ptr8, x: int, y: int) -> int:
    k = 0
    while k < 4:
        px = x + (BALL - 1) * (k & 1)
        py = y + (BALL - 1) * (k >> 1)
        if py >= BY:
            if py < BY + ROWS * BH:
                if px >= FX:
                    if px < FX + COLS * BW:
                        i = ((py - BY) // BH) * COLS + (px - FX) // BW
                        if grid[i]:
                            return i
        k += 1
    return -1


def _mix(c, f):
    if f >= 1:
        return tuple(min(255, int(v + (255 - v) * (f - 1))) for v in c)
    return tuple(int(v * f) for v in c)


def _put(buf, k, c):
    buf[2 * k] = c >> 8
    buf[2 * k + 1] = c & 255


def _sprite(rows, pal, w, h):
    buf = bytearray(w * h * 2)
    msk = bytearray(w * h)
    for j in range(h):
        row = rows[j] if j < len(rows) else ""
        for i in range(w):
            ch = row[i] if i < len(row) else "."
            if ch != ".":
                k = j * w + i
                _put(buf, k, pal[ch])
                msk[k] = 1
    return (buf, msk, w, h)


def _brick(base, rune, crack=False):
    buf = bytearray(BW * BH * 2)
    c_base = rgb(*base)
    c_hi = rgb(*_mix(base, 1.5))
    c_lo = rgb(*_mix(base, 0.5))
    c_rune = rgb(*_mix(base, 0.6))
    c_emb = rgb(*_mix(base, 1.25))
    c_crk = rgb(*_mix(base, 0.3))
    c_shine = rgb(*_mix(base, 1.85))
    for j in range(BH):
        for i in range(BW):
            if i == BW - 1 or j == BH - 1:
                c = BG
            elif j == 0 or i == 0:
                c = c_hi
            elif j == BH - 2 or i == BW - 2:
                c = c_lo
            else:
                c = c_base
                ri, rj = i - 8, j - 2
                if 0 <= ri < 5 and 0 <= rj < 5 and rune[rj][ri] == "#":
                    c = c_rune
                elif 1 <= ri < 6 and 1 <= rj < 6 and ri - 1 < 5 and rj - 1 < 5 and rune[rj - 1][ri - 1] == "#":
                    c = c_emb
                if (i, j) in ((2, 1), (3, 1), (1, 2)):
                    c = c_shine
                if crack and (i, j) in CRACK:
                    c = c_crk
            _put(buf, j * BW + i, c)
    return buf


def _capsule(kind):
    base = CAPS[kind]
    w, h = 16, 8
    buf = bytearray(w * h * 2)
    msk = bytearray(w * h)
    c_base = rgb(*base)
    c_hi = rgb(*_mix(base, 1.6))
    c_lo = rgb(*_mix(base, 0.5))
    edge = rgb(20, 12, 30)
    g = GLYPHS[kind]
    gw = len(g[0])
    gx = (w - gw) // 2
    ink = rgb(40, 20, 10) if kind == "F" else WHITE
    for j in range(h):
        for i in range(w):
            corner = (i in (0, w - 1)) and (j in (0, h - 1))
            if corner:
                continue
            if i in (0, w - 1) or j in (0, h - 1):
                c = edge
            elif j == 1:
                c = c_hi
            elif j == h - 2:
                c = c_lo
            else:
                c = c_base
            gi, gj = i - gx, j - 1
            if 0 <= gi < gw and 0 <= gj < 5 and g[gj][gi] == "#":
                c = ink
            k = j * w + i
            _put(buf, k, c)
            msk[k] = 1
    return (buf, msk, w, h)


class Breaker:
    def __init__(self, tft, touch):
        self.t = tft
        self.touch = touch
        self.rbuf = bytearray(64 * 24 * 2)
        self.bank = bytearray(5 * BW * BH * 2)
        self.paddle = _sprite(WIZARD, WIZ_PAL, PW, PH)
        self.orb = _sprite(ORB, ORB_PAL, BALL, BALL)
        self.bolt = _sprite(BOLT, BOLT_PAL, 3, 7)
        self.caps = {k: _capsule(k) for k in CAPS}
        self.grid = bytearray(ROWS * COLS)
        mv = memoryview(self.bank)
        n = BW * BH * 2
        self.bspr = [mv[v * n:(v + 1) * n] for v in range(5)]
        self.digits = []
        for d in "0123456789":
            buf = bytearray(128)
            g = glyph(d)
            for j in range(8):
                for i in range(8):
                    _put(buf, j * 8 + i, GOLD if g[j] & (0x80 >> i) else BG)
            self.digits.append(buf)
        self.shown = None

    # --- dessin -----------------------------------------------------------
    def region(self, x, y, w, h):
        n = w * h * 2
        buf = self.rbuf if n <= len(self.rbuf) else bytearray(n)
        _region(buf, x, y, w, h, self.grid, self.bank, BG >> 8, BG & 255)
        return buf

    def paint(self, x, y, w, h, spr=None, sx=0, sy=0, sx2=-1):
        if y + h > H:
            h = H - y
        if h <= 0 or w <= 0:
            return
        buf = self.region(x, y, w, h)
        if spr is not None and sy + spr[3] <= y + h:
            if sx >= 0:
                _over(buf, w, spr[0], spr[1], spr[2], spr[3], sx - x, sy - y)
            if sx2 >= 0:
                _over(buf, w, spr[0], spr[1], spr[2], spr[3], sx2 - x, sy - y)
        self.t.blit(buf, x, y, w, h)

    def move(self, ox, oy, nx, ny, spr):
        sw, sh = spr[2], spr[3]
        x = ox if ox < nx else nx
        y = oy if oy < ny else ny
        w = (ox if ox > nx else nx) + sw - x
        h = (oy if oy > ny else ny) + sh - y
        if w * h * 2 > len(self.rbuf):
            self.paint(ox, oy, sw, sh)
            self.paint(nx, ny, sw, sh, spr, nx, ny)
        else:
            self.paint(x, y, w, h, spr, nx, ny)

    def erase(self, x, y, spr):
        self.paint(x, y, spr[2], spr[3])

    def text_c(self, s, y, color, scale=1, shadow=None):
        x = (W - len(s) * 8 * scale) // 2
        if shadow is not None:
            draw_text(self.t, s, x + scale, y + scale, shadow, None, scale)
        draw_text(self.t, s, x, y, color, None, scale)

    def menu_button(self):
        t = self.t
        t.fill_rect(2, 2, 50, 18, PURPLE)
        t.rect(2, 2, 50, 18, GOLD)
        draw_text(t, "MENU", 11, 7, WHITE, None, 1)

    def walls(self):
        t = self.t
        mortar = rgb(30, 28, 40)
        tones = (rgb(95, 90, 115), rgb(105, 98, 125), rgb(85, 80, 105))
        hi = rgb(145, 140, 165)
        lo = rgb(50, 45, 65)
        t.fill_rect(0, HUD_H, W, TOP - HUD_H, mortar)
        t.fill_rect(0, TOP, FX, H - TOP, mortar)
        t.fill_rect(FR, TOP, W - FR, H - TOP, mortar)

        def stones(x0, y0, x1, y1, bw, bh):
            k = 0
            y = y0
            while y < y1:
                off = (k % 2) * (bw // 2)
                x = x0 - off
                n = 0
                while x < x1:
                    a = x if x > x0 else x0
                    b = x + bw if x + bw < x1 else x1
                    hh = bh if y + bh <= y1 else y1 - y
                    if b - a > 2 and hh > 2:
                        t.fill_rect(a + 1, y + 1, b - a - 1, hh - 1, tones[(k * 3 + n) % 3])
                        t.fill_rect(a + 1, y + 1, b - a - 1, 1, hi)
                        t.fill_rect(a + 1, y + hh - 1, b - a - 1, 1, lo)
                    x += bw
                    n += 1
                y += bh
                k += 1

        stones(0, HUD_H, W, TOP, 16, 5)
        stones(0, TOP, FX, H, 10, 8)
        stones(FR, TOP, W, H, 10, 8)
        for gx in (60, 120, 180):
            t.fill_rect(gx - 2, HUD_H + 3, 5, 5, rgb(120, 40, 200))
            t.fill_rect(gx - 1, HUD_H + 4, 2, 2, rgb(220, 170, 255))

    def hud(self):
        t = self.t
        t.fill_rect(56, 0, W - 56, HUD_H, BG)
        self.shown = None
        self.draw_score()
        draw_text(t, "NV%d" % (self.level + 1), 124, 7, SKY, None, 1)
        for i in range(min(self.lives, 5)):
            self.paint(236 - (i + 1) * 10, 7, BALL, BALL, self.orb, 236 - (i + 1) * 10, 7)

    def draw_score(self):
        s = "%06d" % self.score
        old = self.shown
        for k in range(6):
            if old is None or old[k] != s[k]:
                self.t.blit(self.digits[ord(s[k]) - 48], 60 + k * 8, 7, 8, 8)
        self.shown = s

    def draw_bricks(self):
        for r in range(ROWS):
            for c in range(COLS):
                v = self.grid[r * COLS + c]
                if v:
                    self.t.blit(self.bspr[v], FX + c * BW, BY + r * BH, BW, BH)

    # --- ecrans -----------------------------------------------------------
    def wait_release(self):
        while self.touch.point():
            time.sleep_ms(20)

    def wait_tap(self, blink=None):
        on = False
        last = 0
        while True:
            if blink is not None and time.ticks_diff(time.ticks_ms(), last) > 450:
                last = time.ticks_ms()
                on = not on
                blink(on)
            pt = self.touch.point()
            if pt:
                self.wait_release()
                return pt
            time.sleep_ms(25)

    def castle(self):
        t = self.t
        stone = rgb(28, 22, 58)
        roof = rgb(60, 30, 90)
        lit = rgb(255, 200, 80)
        t.fill_rect(0, 292, W, 28, stone)
        for x in range(0, W, 12):
            t.fill_rect(x, 286, 7, 6, stone)
        for x, w, h in ((8, 26, 60), (46, 30, 88), (98, 44, 110), (158, 30, 78), (200, 28, 54)):
            top = 320 - h
            t.fill_rect(x, top, w, h, stone)
            rh = w // 2 + 8
            for i in range(rh):
                ww = 1 + (i * w) // rh
                t.fill_rect(x + (w - ww) // 2, top - rh + i, ww, 1, roof)
            for wy in range(top + 10, 300, 22):
                t.fill_rect(x + w // 2 - 2, wy, 4, 6, lit)

    def title(self):
        t = self.t
        t.fill(BG)
        random.seed(7)
        for _ in range(70):
            c = rgb(120, 120, 180) if random.getrandbits(1) else rgb(230, 230, 255)
            t.fill_rect(random.randint(0, W - 1), random.randint(24, 250), 1, 1, c)
        t.fill_circle(196, 52, 18, rgb(250, 240, 190))
        t.fill_circle(188, 46, 16, BG)
        self.castle()
        self.text_c("MAGIC", 64, GOLD, 3, PURPLE)
        self.text_c("HARRY", 94, ORANGE, 3, PURPLE)
        buf, msk, w, h = self.paddle
        s = 3
        row = bytearray(w * s * 2 * s)
        x0 = (W - w * s) // 2
        for j in range(h):
            for i in range(w):
                k = j * w + i
                hi, lo = (buf[2 * k], buf[2 * k + 1]) if msk[k] else (BG >> 8, BG & 255)
                for d in range(s):
                    p = (i * s + d) * 2
                    row[p] = hi
                    row[p + 1] = lo
            n = w * s * 2
            for d in range(1, s):
                row[d * n:(d + 1) * n] = row[:n]
            t.blit(row, x0, 134 + j * s, w * s, s)
        self.menu_button()

        def blink(on):
            if on:
                self.text_c("TOUCHE POUR JOUER", 190, WHITE)
            else:
                t.fill_rect(40, 190, 160, 8, BG)

        pt = self.wait_tap(blink)
        return not (pt[1] < HUD_H and pt[0] < 60)

    # --- partie -----------------------------------------------------------
    def load_level(self):
        name, ca, cb = HOUSES[self.level % 4]
        rune = RUNES[self.level % 4]
        n = BW * BH * 2
        for v, spr in ((1, _brick(ca, rune)), (2, _brick(cb, rune)), (3, _brick((170, 175, 190), LOCK)),
                       (4, _brick((170, 175, 190), LOCK, True))):
            self.bank[v * n:(v + 1) * n] = spr
            del spr
        lay = LEVELS[self.level % 4]
        self.left = 0
        for r in range(ROWS):
            for c in range(COLS):
                v = "_abs".find(lay[r][c]) if lay[r][c] != "." else 0
                self.grid[r * COLS + c] = v if v > 0 else 0
                if v > 0:
                    self.left += 1
        self.speed = min(4.6, 2.8 + 0.35 * self.level)
        t = self.t
        t.fill_rect(FX, TOP, FW, H - TOP, BG)
        self.draw_bricks()
        self.hud()
        self.text_c(name, 190, rgb(*ca), 1)
        self.text_c("NIVEAU %d" % (self.level + 1), 206, WHITE, 1)
        time.sleep_ms(1400)
        t.fill_rect(FX, 186, FW, 30, BG)
        self.caps_list = []
        self.shots = []
        self.shield_until = 0
        self.fire_until = 0
        self.reset_ball()

    def reset_ball(self):
        self.balls = [[self.px + PW / 2 - 3, PY - BALL, 0.0, 0.0, None, None]]
        self.stuck = True
        self.stick_ms = time.ticks_ms()

    def cell_at(self, x, y):
        return _cell(self.grid, int(x), int(y))

    def hit_ball(self, x, y):
        return _hit(self.grid, int(x), int(y))

    def break_brick(self, i, drop=True):
        v = self.grid[i]
        r, c = divmod(i, COLS)
        x0, y0 = FX + c * BW, BY + r * BH
        if v == 3:
            self.grid[i] = 4
            self.t.blit(self.bspr[4], x0, y0, BW, BH)
            self.score += 10
        else:
            self.grid[i] = 0
            self.left -= 1
            self.score += 100 if v == 4 else 50
            self.paint(x0, y0, BW, BH)
            if drop and len(self.caps_list) < 3 and random.randint(0, 5) == 0:
                kind = "BMTF"[random.getrandbits(2)]
                self.caps_list.append([x0 + 3, y0 + 1, kind, None])
        self.hud_dirty = True

    def lightning(self):
        cells = [i for i in range(ROWS * COLS) if self.grid[i]]
        t = self.t
        for _ in range(min(10, len(cells))):
            i = cells.pop(random.randint(0, len(cells) - 1))
            r, c = divmod(i, COLS)
            cx = FX + c * BW + BW // 2
            yb = BY + r * BH + BH // 2
            y = TOP
            x = cx
            pts = []
            while y < yb:
                ny = min(yb, y + 8)
                nx = cx + random.randint(-4, 4)
                pts.append((min(x, nx), y, abs(nx - x) + 2, ny - y))
                x, y = nx, ny
            for p in pts:
                t.fill_rect(p[0], p[1], p[2], p[3], WHITE)
                t.fill_rect(p[0] + 1, p[1], 1, p[3], rgb(255, 240, 120))
            time.sleep_ms(45)
            if self.grid[i] == 3:
                self.grid[i] = 4
            self.break_brick(i, False)
            y = TOP
            while y < yb + 2:
                hh = min(80, yb + 2 - y)
                self.paint(cx - 8, y, 17, hh)
                y += hh

    def bounce_paddle(self, b):
        half = PW / 2 + 3
        off = ((b[0] + 3.5) - (self.px + PW / 2)) / half
        if off < -1:
            off = -1.0
        elif off > 1:
            off = 1.0
        b[2] = self.speed * off * 0.8
        b[3] = -math.sqrt(self.speed * self.speed - b[2] * b[2])
        b[1] = PY - BALL

    def step_ball(self, b):
        x, y, vx, vy = b[0], b[1], b[2], b[3]
        nx = x + vx
        if nx < FX:
            nx = FX
            vx = abs(vx)
        elif nx > FR - BALL:
            nx = FR - BALL
            vx = -abs(vx)
        i = self.hit_ball(nx, y)
        if i >= 0:
            vx = -vx
            nx = x
            self.break_brick(i)
        x = nx
        ny = y + vy
        if ny < TOP:
            ny = TOP
            vy = abs(vy)
        i = self.hit_ball(x, ny)
        if i >= 0:
            vy = -vy
            ny = y
            self.break_brick(i)
        y = ny
        b[0], b[1], b[2], b[3] = x, y, vx, vy
        if vy > 0 and PY <= y + BALL <= PY + 8 and x + BALL >= self.px and x <= self.px + PW:
            self.bounce_paddle(b)
        elif vy > 0 and self.shield_until and y + BALL >= SHIELD_Y:
            b[1] = SHIELD_Y - BALL
            b[3] = -abs(vy)
        return b[1] < H

    def draw_shield(self, phase):
        self.t.fill_rect(FX, SHIELD_Y, FW, 2, CYAN if phase else SKY)

    def apply(self, kind, now):
        self.score += 30
        self.hud_dirty = True
        if kind == "B":
            self.shield_until = time.ticks_add(now, 5000)
            self.draw_shield(0)
        elif kind == "M":
            src = self.balls[0]
            for sgn in (-1, 1):
                if len(self.balls) < 5:
                    a = 0.6 * sgn
                    self.balls.append([src[0], src[1], self.speed * math.sin(a), -self.speed * math.cos(a), None, None])
            if self.stuck:
                self.stuck = False
                self.bounce_paddle(self.balls[0])
        elif kind == "T":
            self.fire_until = time.ticks_add(now, 5000)
            self.next_shot = now
        else:
            self.lightning()

    def game_over(self):
        t = self.t
        t.fill_rect(24, 140, 192, 84, DARK)
        t.rect(24, 140, 192, 84, GOLD)
        t.rect(26, 142, 188, 80, PURPLE)
        self.text_c("FIN DE PARTIE", 152, ORANGE, 1)
        self.text_c("SCORE %d" % self.score, 172, GOLD, 1)
        self.text_c("TOUCHE : REJOUER", 196, WHITE, 1)
        self.text_c("MENU : QUITTER", 208, SKY, 1)
        time.sleep_ms(500)
        self.wait_release()
        pt = self.wait_tap()
        return not (pt[1] < HUD_H and pt[0] < 60)

    def new_game(self):
        self.score = 0
        self.lives = 3
        self.level = 0
        self.px = FX + (FW - PW) // 2
        t = self.t
        t.fill(BG)
        self.menu_button()
        self.walls()
        self.load_level()

    def run(self):
        if not self.title():
            return
        self.new_game()
        target = self.px
        drawn_px = None
        touching = False
        frame = 0
        while True:
            t0 = time.ticks_ms()
            frame += 1
            self.hud_dirty = False
            pt = self.touch.point()
            if pt:
                if pt[1] < HUD_H and pt[0] < 60:
                    return
                target = pt[0] - PW // 2
                touching = True
            elif touching:
                touching = False
                if self.stuck:
                    self.stuck = False
                    self.bounce_paddle(self.balls[0])
            if self.stuck and time.ticks_diff(t0, self.stick_ms) > 4000 and not touching:
                self.stuck = False
                self.bounce_paddle(self.balls[0])

            if target < FX:
                target = FX
            if target > FR - PW:
                target = FR - PW
            d = target - self.px
            if d > 10:
                d = 10
            elif d < -10:
                d = -10
            self.px += d
            if drawn_px is None or drawn_px != self.px:
                if drawn_px is None:
                    self.paint(self.px, PY, PW, PH, self.paddle, self.px, PY)
                else:
                    self.move(drawn_px, PY, self.px, PY, self.paddle)
                drawn_px = self.px

            alive = []
            for b in self.balls:
                if self.stuck:
                    b[0] = self.px + PW / 2 - 3
                    b[1] = PY - BALL
                    ok = True
                else:
                    ok = self.step_ball(b)
                ix, iy = int(b[0]), int(b[1])
                if not ok:
                    if b[4] is not None:
                        self.erase(b[4], b[5], self.orb)
                    continue
                if b[4] is None:
                    self.paint(ix, iy, BALL, BALL, self.orb, ix, iy)
                elif (ix, iy) != (b[4], b[5]):
                    self.move(b[4], b[5], ix, iy, self.orb)
                b[4], b[5] = ix, iy
                alive.append(b)
            self.balls = alive

            keep = []
            for cp in self.caps_list:
                cp[1] += 1.7
                iy = int(cp[1])
                spr = self.caps[cp[2]]
                if iy + 8 >= PY and iy <= PY + PH and cp[0] + 16 >= self.px and cp[0] <= self.px + PW:
                    if cp[3] is not None:
                        self.erase(cp[0], cp[3], spr)
                    self.apply(cp[2], t0)
                    continue
                if iy >= H:
                    if cp[3] is not None:
                        self.erase(cp[0], cp[3], spr)
                    continue
                if cp[3] is None:
                    self.paint(cp[0], iy, 16, 8, spr, cp[0], iy)
                elif iy != cp[3]:
                    self.move(cp[0], cp[3], cp[0], iy, spr)
                cp[3] = iy
                keep.append(cp)
            self.caps_list = keep

            if self.fire_until:
                if time.ticks_diff(self.fire_until, t0) <= 0:
                    self.fire_until = 0
                elif time.ticks_diff(t0, self.next_shot) >= 0 and len(self.shots) < 3:
                    self.next_shot = time.ticks_add(t0, 240)
                    self.shots.append([self.px + 5, PY - 8, PY - 8, True, True])
            nxt = []
            gap = PW - 13
            for s in self.shots:
                old = s[2]
                s[1] -= 9
                y = s[1]
                for side in (3, 4):
                    if s[side]:
                        i = self.cell_at(s[0] + 1 + (side - 3) * gap, y)
                        if i >= 0:
                            self.break_brick(i)
                            s[side] = False
                        elif y < TOP:
                            s[side] = False
                w = gap + 3
                if not (s[3] or s[4]):
                    self.paint(s[0], old, w, 7)
                    continue
                self.paint(s[0], y, w, old + 7 - y, self.bolt, s[0] if s[3] else -1, y,
                           s[0] + gap if s[4] else -1)
                s[2] = y
                nxt.append(s)
            self.shots = nxt

            if self.shield_until:
                if time.ticks_diff(self.shield_until, t0) <= 0:
                    self.shield_until = 0
                    self.t.fill_rect(FX, SHIELD_Y - 1, FW, 3, BG)
                elif frame % 6 == 0:
                    self.draw_shield((frame // 6) % 2)

            if self.hud_dirty:
                self.draw_score()

            if self.left <= 0:
                self.level += 1
                self.lives = min(5, self.lives + (1 if self.level % 2 == 0 else 0))
                drawn_px = None
                self.load_level()
                continue

            if not self.balls:
                self.lives -= 1
                if self.lives <= 0:
                    if not self.game_over():
                        return
                    self.new_game()
                    drawn_px = None
                    continue
                self.hud()
                self.shield_until = 0
                self.fire_until = 0
                self.t.fill_rect(FX, SHIELD_Y - 1, FW, 3, BG)
                self.reset_ball()

            dt = time.ticks_diff(time.ticks_ms(), t0)
            if dt < 30:
                time.sleep_ms(30 - dt)


def play(tft, touch):
    import gc

    gc.collect()
    Breaker(tft, touch).run()
    gc.collect()
