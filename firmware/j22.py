"""Jour 22 : REACTION 80. Toucher la case qui s'allume, de plus en plus vite. Case blanche = piege."""

import random
import time

from arcade import BLACK, NIGHT, PINK, WHITE, Game, rgb
from font8 import draw_text

QX = (4, 122)
QY = (26, 172)
QW = 114
QH = 142
DIM = (rgb(70, 10, 20), rgb(10, 60, 20), rgb(10, 20, 80), rgb(80, 70, 0))
LIT = (rgb(255, 50, 60), rgb(40, 240, 90), rgb(60, 120, 255), rgb(255, 220, 0))
NOTES = (523, 659, 784, 1047)


class Reaction(Game):
    TITLE = "REACTION 80"
    HELP = ("TOUCHE LA CASE QUI", "S'ALLUME AU PLUS VITE", "BLANCHE : NE TOUCHE PAS")
    BG = NIGHT

    def preview(self, y):
        for q in range(4):
            x = 60 + (q % 2) * 62
            yy = y + (q // 2) * 48
            self.t.fill_rect(x, yy, 58, 44, LIT[q] if q == 2 else DIM[q])

    def quad(self, q, c):
        x = QX[q % 2]
        y = QY[q // 2]
        self.t.fill_rect(x, y, QW, QH, c)

    def setup(self):
        for q in range(4):
            self.quad(q, DIM[q])
        self.window = 1300
        self.rounds = 0
        self.wait(time.ticks_ms())

    def wait(self, now):
        self.lit = None
        self.trap = False
        self.go_at = time.ticks_add(now, random.randint(400, 1300))

    def light(self, now):
        self.rounds += 1
        self.lit = random.randint(0, 3)
        self.trap = self.rounds > 5 and random.random() < 0.18
        self.quad(self.lit, WHITE if self.trap else LIT[self.lit])
        if not self.trap:
            x = QX[self.lit % 2] + QW // 2 - 8
            y = QY[self.lit // 2] + QH // 2 - 8
            draw_text(self.t, "!", x, y, BLACK, None, 2)
        self.sfx.tone(200 if self.trap else NOTES[self.lit], 80)
        self.t_lit = now
        self.until = time.ticks_add(now, self.window)

    def off(self, now):
        self.quad(self.lit, DIM[self.lit])
        self.wait(now)

    def miss(self, now, why):
        self.lives -= 1
        self.sfx.tone(110, 350)
        self.quad(self.lit, PINK)
        self.text_c(why, 150, WHITE, 2, BLACK)
        time.sleep_ms(600)
        for q in range(4):
            self.quad(q, DIM[q])
        self.wait(time.ticks_ms())

    def step(self, pt, now):
        p = self.tap(pt)
        if self.lit is None:
            if time.ticks_diff(now, self.go_at) >= 0:
                self.light(now)
            return True
        late = time.ticks_diff(now, self.until) >= 0
        if p:
            q = (1 if p[0] >= QX[1] else 0) + (2 if p[1] >= QY[1] else 0)
            if self.trap:
                if q == self.lit:
                    self.miss(now, "PIEGE !")
                    return self.lives > 0
            elif q == self.lit:
                dt = time.ticks_diff(now, self.t_lit)
                self.score += 10 + max(0, self.window - dt) // 10
                self.sfx.tone(NOTES[q] * 2, 60)
                self.window = max(380, self.window * 94 // 100)
                self.off(now)
                return True
            else:
                self.miss(now, "RATE !")
                return self.lives > 0
        if late:
            if self.trap:
                self.score += 50
                self.sfx.tone(1319, 80)
                self.off(now)
            else:
                self.miss(now, "TROP LENT")
                return self.lives > 0
        return True

    def bot(self, n):
        if not hasattr(self, "lit"):
            return (120, 160) if n % 4 < 2 else None
        if self.lit is None or self.trap or n % 3:
            return None
        return (QX[self.lit % 2] + 50, QY[self.lit // 2] + 60)


GAME = Reaction


def play(tft, touch, day):
    GAME(tft, touch, day).run()
