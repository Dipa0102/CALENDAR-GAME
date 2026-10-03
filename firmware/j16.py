"""Jour 16 : ALUNISSAGE. Doigt pose : le moteur pousse vers le haut et vers le doigt ; se poser en douceur sur une piste."""

import random
import time

from arcade import BLACK, CYAN, GOLD, GREEN, GREY, ORANGE, RED, VIOLET, W, WHITE, Game, rgb, sprite
from font8 import draw_text

COL = 4
NC = W // COL
FP = 256
M = 4
# La marge du sprite efface une avance d'au plus M pixels par image.
VMAX = M * FP - 1
MW = 24
MH = 22
SPR_H = 32 + 2 * M
YMIN = 42
XMIN = M
XMAX = W - MW - M
THRUST = 16
AX = 6
VX_OK = 6
VY_OK = 12
PANEL_Y = 25
BAR_X = 190
BAR_W = 46
ROCK = rgb(92, 88, 110)
EDGE = rgb(196, 192, 212)
CRATER = rgb(62, 58, 78)
DARK = rgb(34, 30, 56)
STAR = rgb(220, 220, 255)
STAR2 = rgb(90, 90, 140)
PAD_C = (CYAN, GOLD)
MULT = (2, 5)

BODY = (
    ".....ww.....",
    "....wccw....",
    "...wcbbcw...",
    "..wcbwbbcw..",
    "..wcbbbbcw..",
    "...wccccw...",
    ".gggggggggg.",
    ".gGgGggGgGg.",
    "..k..kk..k..",
    ".k..kkkk..k.",
)
TAILS = (
    ("kk........kk", "............", "............", "............", "............", "............"),
    ("kk..oyyo..kk", "....oyyo....", ".....oo.....", ".....o......", "............", "............"),
    ("kk.oyyyyo.kk", "...oywwyo...", "....oyyo....", "....oyyo....", ".....oo.....", "......o....."),
)
LANDER_PAL = {"w": WHITE, "c": rgb(170, 170, 190), "b": rgb(40, 110, 255), "g": rgb(255, 200, 0),
              "G": rgb(190, 110, 0), "k": rgb(180, 180, 200), "o": rgb(255, 100, 20), "y": rgb(255, 230, 60)}
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
BOOM_PAL = {"y": rgb(255, 230, 60), "o": rgb(255, 110, 30), "w": WHITE}


class Lander(Game):
    TITLE = "ALUNISSAGE"
    HELP = ("DOIGT POSE : MOTEUR", "LE DOIGT GUIDE LA POUSSEE", "POSE-TOI EN DOUCEUR")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.frames = [sprite(BODY + tl, LANDER_PAL, 2, BLACK, M, M) for tl in TAILS]
        self.boom = sprite(BOOM, BOOM_PAL, 3, BLACK)
        self.hm = [300] * NC
        self.kind = bytearray(NC)

    def preview(self, y):
        t = self.t
        for k in range(12):
            t.fill_rect((k * 83) % 236, y + (k * 37) % 60, 1, 1, STAR)
        self.big_sprite(BODY + TAILS[2], LANDER_PAL, 3, y)
        for c in range(NC):
            h = y + 80 if 25 <= c < 35 else y + 66 + (c * 37) % 23
            t.fill_rect(c * COL, h, COL, 2, GOLD if 25 <= c < 35 else EDGE)
            t.fill_rect(c * COL, h + 2, COL, y + 96 - h - 2, ROCK)
        draw_text(t, "X5", 112, y + 86, GOLD, ROCK)

    def setup(self):
        self.level = 1
        self.n = 0
        self.new_level(True)

    # --- terrain ----------------------------------------------------------
    def gen(self):
        L = self.level
        hm, kind = self.hm, self.kind
        top = max(120, 200 - 10 * L)
        v = []
        y = random.randint(230, 290)
        for _ in range(NC // 3 + 1):
            y = max(top, min(300, y + random.randint(-50, 50)))
            v.append(y)
        for c in range(NC):
            k, f = c // 3, c % 3
            hm[c] = v[k] + (v[k + 1] - v[k]) * f // 3
            kind[c] = 0
        self.pads = []
        widths = (max(8, 13 - L), max(7, 10 - L // 2))
        for i in (0, 1):
            w = widths[i]
            for _ in range(50):
                c = random.randint(1, NC - w - 1)
                if all(kind[j] == 0 for j in range(max(0, c - 3), min(NC, c + w + 3))):
                    break
            py = max(160, min(298, hm[c + w // 2]))
            for j in range(c, c + w):
                hm[j] = py
                kind[j] = i + 1
            if i == 1:
                for j in (c - 2, c - 1, c + w, c + w + 1):
                    if 0 <= j < NC and not kind[j]:
                        hm[j] = max(top, min(hm[j], py - random.randint(16, 40)))
            self.pads.append((c, w, py, i))
        self.craters = []
        for _ in range(12):
            c = random.randint(0, NC - 3)
            y = max(hm[c], hm[c + 1], hm[c + 2]) + random.randint(28, 50)
            if y < 312:
                self.craters.append((c * COL + random.randint(0, 3), y, random.randint(4, 10), random.randint(2, 4)))
        self.stars = []
        for _ in range(26):
            x, y = random.randint(0, W - 1), random.randint(40, 290)
            if y < hm[x // COL] - 6:
                self.stars.append((x, y))

    def ground(self, c0, c1, ybot):
        """Redessine les colonnes c0..c1-1 de la surface jusqu'a ybot (colonnes egales regroupees)."""
        t = self.t
        hm, kind = self.hm, self.kind
        c = c0
        while c < c1:
            h, k = hm[c], kind[c]
            e = c + 1
            while e < c1 and hm[e] == h and kind[e] == k:
                e += 1
            if h < ybot:
                x, w = c * COL, (e - c) * COL
                eh = 3 if k else 2
                t.fill_rect(x, h, w, min(eh, ybot - h), PAD_C[k - 1] if k else EDGE)
                if ybot > h + eh:
                    t.fill_rect(x, h + eh, w, ybot - h - eh, ROCK)
            c = e

    def new_level(self, fresh):
        t = self.t
        L = self.level
        if fresh:
            self.gen()
        t.fill_rect(0, 20, W, 300, BLACK)
        if fresh:
            self.text_c("NIVEAU %d" % L, 110, CYAN, 2, VIOLET)
            self.sfx.tune(((523, 70), (659, 70), (784, 120)))
            time.sleep_ms(500)
            t.fill_rect(0, 110, W, 20, BLACK)
        for x, y in self.stars:
            t.fill_rect(x, y, 1, 1, STAR)
        self.ground(0, NC, 320)
        for x, y, w, h in self.craters:
            t.fill_rect(x, y, w, h, CRATER)
        for c, w, y, i in self.pads:
            draw_text(t, "X%d" % MULT[i], c * COL + w * COL // 2 - 8, y + 6, PAD_C[i], ROCK)
        t.fill_rect(0, 37, W, 1, DARK)
        draw_text(t, "NIV%d" % min(99, L), 4, PANEL_Y, GREY, BLACK)
        draw_text(t, "FUEL", 152, PANEL_Y, GREY, BLACK)
        t.rect(BAR_X - 1, PANEL_Y - 1, BAR_W + 2, 10, GREY)
        t.fill_rect(BAR_X, PANEL_Y, BAR_W, 8, GREEN)
        self.bar = BAR_W
        self.low = False
        self.fmax = max(150, 340 - 20 * L)
        self.fuel = self.fmax
        self.grav = min(10, 4 + L)
        self.shown_h = self.shown_v = None
        x = random.randint(XMIN, XMAX)
        self.fx, self.fy = x * FP, YMIN * FP
        self.mx, self.my = x, YMIN
        self.vx = random.randint(30, 50 + 12 * L) * (1 if random.getrandbits(1) else -1)
        self.vy = 0
        self.goal = random.getrandbits(1)
        self.draw_module(x, YMIN, 0)
        self.panel()

    # --- dessin -----------------------------------------------------------
    def draw_module(self, x, y, k):
        buf, w, h = self.frames[k][:3]
        x0, y0 = x - M, y - M
        hm = self.hm
        c0, c1 = x0 // COL, min(NC, (x0 + w - 1) // COL + 1)
        lim = 320
        for c in range(c0, c1):
            if hm[c] < lim:
                lim = hm[c]
        self.t.blit(buf, x0, y0, w, h)
        # La marge noire et la flamme ont mordu sur le sol : on le repeint.
        if lim < y0 + h:
            self.ground(c0, c1, y0 + h)

    def panel(self, both=True):
        t = self.t
        # Une seule vitesse reecrite par image : le texte coute un envoi complet.
        odd = self.n & 1
        if both or odd:
            sx = min(99, abs(self.vx) * 10 // FP)
            a = ("VX %02d" % sx, GREEN if sx <= VX_OK else RED)
            if a != self.shown_h:
                draw_text(t, a[0], 60, PANEL_Y, a[1], BLACK)
                self.shown_h = a
        if both or not odd:
            sy = self.vy * 10 // FP
            up = sy < 0
            sy = min(99, -sy if up else sy)
            b = (("VY^%02d" if up else "VY %02d") % sy, GREEN if up or sy <= VY_OK else RED)
            if b != self.shown_v:
                draw_text(t, b[0], 106, PANEL_Y, b[1], BLACK)
                self.shown_v = b
        bw = self.fuel * BAR_W // self.fmax
        if bw != self.bar:
            low = self.fuel * 4 < self.fmax
            if low != self.low:
                self.low = low
                t.fill_rect(BAR_X, PANEL_Y, bw, 8, RED)
                t.fill_rect(BAR_X + bw, PANEL_Y, BAR_W - bw, 8, DARK)
            elif bw < self.bar:
                t.fill_rect(BAR_X + bw, PANEL_Y, self.bar - bw, 8, DARK)
            self.bar = bw
            if self.fuel <= 0:
                draw_text(t, "VIDE", BAR_X + 7, PANEL_Y, RED, DARK)

    # --- jeu --------------------------------------------------------------
    def step(self, pt, now):
        self.n += 1
        n = self.n
        fire = 0
        if pt and self.fuel > 0:
            self.fuel -= 1
            d = pt[0] - self.mx - MW // 2
            if d > 10 or d < -10:
                a = d * AX // 50
                self.vx += AX if a > AX else (-AX if a < -AX else a)
            self.vy -= THRUST
            fire = 1 + ((n >> 1) & 1)
            if n % 3 == 0:
                self.sfx.tone(60 + (n & 7) * 6, 80)
        elif self.low and self.fuel > 0 and n % 24 == 0:
            self.sfx.tone(1500, 30)
        vy = self.vy + self.grav
        self.vy = VMAX if vy > VMAX else (-VMAX if vy < -VMAX else vy)
        vx = self.vx
        self.vx = VMAX if vx > VMAX else (-VMAX if vx < -VMAX else vx)
        self.fx += self.vx
        self.fy += self.vy
        if self.fx < XMIN * FP:
            self.fx, self.vx = XMIN * FP, 0
        elif self.fx > XMAX * FP:
            self.fx, self.vx = XMAX * FP, 0
        if self.fy < YMIN * FP:
            self.fy = YMIN * FP
            if self.vy < 0:
                self.vy = 0
        x, y = self.fx >> 8, self.fy >> 8
        self.mx, self.my = x, y
        feet = y + MH
        hm = self.hm
        c0, c1 = (x + 1) // COL, (x + MW - 2) // COL + 1
        for c in range(c0, c1):
            if feet >= hm[c]:
                return self.touchdown(c0, c1)
        self.draw_module(x, y, fire)
        self.panel(False)
        st = self.stars
        if st:
            sx, sy = st[n % len(st)]
            if not (x - M <= sx < x + MW + M and y - M <= sy < y + SPR_H):
                self.t.fill_rect(sx, sy, 1, 1, STAR if (n >> 4) & 1 else STAR2)
        return True

    def touchdown(self, c0, c1):
        k = self.kind[c0]
        pad = k and all(self.kind[c] == k for c in range(c0, c1))
        sx = abs(self.vx) * 10 // FP
        sy = self.vy * 10 // FP
        self.panel()
        if pad and sx <= VX_OK and sy <= VY_OK:
            self.my = self.hm[c0] - MH
            self.draw_module(self.mx, self.my, 0)
            return self.landed(k - 1)
        why = "HORS PISTE" if not pad else "TROP VITE"
        return self.crash(why)

    def landed(self, i):
        mult = MULT[i]
        pts = (100 + 25 * self.level) * mult + self.fuel
        self.score += pts
        self.draw_score()
        self.sfx.tune(((784, 80), (988, 80), (1319, 180)))
        self.text_c("BRAVO !", 76, GOLD, 2, ORANGE)
        s = "X%d  +%d" % (mult, pts)
        draw_text(self.t, s, (W - 8 * len(s)) // 2, 100, WHITE, BLACK)
        time.sleep_ms(1100)
        self.level += 1
        self.new_level(True)
        return True

    def crash(self, why):
        t = self.t
        self.sfx.tone(70, 500)
        bx, by = self.mx + MW // 2 - 13, self.my + MH - 22
        self.put(self.boom, bx, by)
        time.sleep_ms(200)
        t.fill_rect(bx + 8, by + 8, 11, 11, WHITE)
        time.sleep_ms(100)
        self.put(self.boom, bx, by)
        draw_text(t, why, (W - 8 * len(why)) // 2, 80, RED, BLACK)
        time.sleep_ms(900)
        self.lives -= 1
        self.draw_lives()
        if self.lives <= 0:
            return False
        self.new_level(False)
        return True

    def bot(self, n):
        if not hasattr(self, "fuel") or self.lives <= 0:
            return (120, 160) if n % 4 < 2 else None
        if self.fuel <= 0:
            return None
        c, w, py, _i = self.pads[self.goal]
        tx = c * COL + w * COL // 2
        cx = self.mx + MW // 2
        ex = tx - cx
        feet = self.my + MH
        a, b = min(cx, tx) // COL, max(cx, tx) // COL
        hi = min(self.hm[max(0, a - 4):min(NC, b + 5)])
        if abs(ex) > w * COL // 2 - 12:
            vxd = max(-220, min(220, ex * 4))
            vyd = max(-160, min(240, (hi - 40 - feet) * 4))
        else:
            vxd = ex * 6
            vyd = max(40, min(400, (py - feet) * 3))
        dv = vxd - self.vx
        side = dv > 16 or dv < -16
        if self.vy > vyd or (side and self.vy > vyd - 150):
            off = 12 + min(48, abs(dv) // 4) if side else 0
            return (max(0, min(W - 1, cx + (off if dv > 0 else -off))), 200)
        return None


GAME = Lander


def play(tft, touch, day):
    GAME(tft, touch, day).run()
