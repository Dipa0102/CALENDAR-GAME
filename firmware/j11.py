"""Jour 11 : PAIRES 80. Retrouver les paires de cartes avant la fin du temps."""

import random
import time

from arcade import CYAN, GOLD, NIGHT, PINK, W, Game, rgb, sprite

X0 = 8
Y0 = 26
CELL = 56
CARD = 52
COLS = 4
ROWS = 5
BAR_Y = 310
FACE = rgb(250, 245, 230)

ICONS = (
    ("...yy...", "...yy...", "yyyyyyyy", ".yyyyyy.", "..yyyy..", ".yy..yy.", "yy....yy", "........"),
    (".rr..rr.", "rrrrrrrr", "rwrrrrrr", "rrrrrrrr", ".rrrrrr.", "..rrrr..", "...rr...", "........"),
    ("...yy...", "..yyyy..", ".yyyyyy.", ".yyyyyy.", ".yyyyyy.", "yyyyyyyy", "...oo...", "........"),
    ("...gg...", "..gggg..", "...gg...", ".gggggg.", "..gggg..", "gggggggg", "...oo...", "...oo..."),
    ("b..b..b.", ".b.b.b..", "..bbb...", "bbbbbbb.", "..bbb...", ".b.b.b..", "b..b..b.", "........"),
    ("..rrrr..", ".rwwrrr.", ".rr..rw.", "......r.", "......w.", "......r.", "......w.", "........"),
    ("..r..r..", "...rr...", "gggrrggg", "gggrrggg", "rrrrrrrr", "gggrrggg", "gggrrggg", "gggrrggg"),
    ("..yyy...", ".yy.....", "yy......", "yy......", "yy......", ".yy...y.", "..yyyy..", "........"),
    ("....kkk.", "....k.k.", "....k.k.", "....k.k.", "..kkk.k.", ".kkkk.k.", ".kkk.kk.", "....kkk."),
    ("..rrrr..", ".rwrrwr.", "rrrrrrrr", "rwrrrrwr", "..wwww..", "..wkkw..", "..wwww..", "........"),
)
ICON_PAL = {"y": rgb(255, 200, 0), "r": rgb(230, 40, 50), "w": rgb(255, 255, 255), "g": rgb(40, 170, 70),
            "o": rgb(140, 80, 30), "b": rgb(60, 140, 255), "k": rgb(30, 30, 40)}
BACK = (
    "ppppppppppppp",
    "pbbbbbbbbbbbp",
    "pbbbbbybbbbbp",
    "pbbbbyyybbbbp",
    "pbbbyybyybbbp",
    "pbbyybbbyybbp",
    "pbyybbbbbyybp",
    "pbbyybbbyybbp",
    "pbbbyybyybbbp",
    "pbbbbyyybbbbp",
    "pbbbbbybbbbbp",
    "pbbbbbbbbbbbp",
    "ppppppppppppp",
)


class Paires(Game):
    TITLE = "PAIRES 80"
    HELP = ("TOUCHE DEUX CARTES", "TROUVE LES PAIRES", "AVANT LA FIN DU TEMPS")
    LIVES = 1
    BG = NIGHT

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.back = sprite(BACK, {"p": PINK, "b": rgb(40, 40, 140), "y": CYAN}, 4, NIGHT)

    def preview(self, y):
        for k, x in enumerate((30, 94, 158)):
            if k == 1:
                self.t.blit(self.back[0], x, y + 20, CARD, CARD)
            else:
                self.t.fill_rect(x, y + 20, CARD, CARD, FACE)
                spr = sprite(ICONS[k], ICON_PAL, 5, FACE)
                self.t.blit(spr[0], x + 6, y + 26, spr[1], spr[2])

    def setup(self):
        self.board = 0
        self.new_board(time.ticks_ms())

    def new_board(self, now):
        cards = [k % 10 for k in range(20)]
        for i in range(19, 0, -1):
            j = random.randint(0, i)
            cards[i], cards[j] = cards[j], cards[i]
        self.cards = cards
        self.state = [0] * 20
        self.open = []
        self.hide_at = 0
        self.combo = 0
        self.found = 0
        self.limit = max(30000, 60000 - self.board * 6000)
        self.t_end = time.ticks_add(now, self.limit)
        self.bar = -1
        for i in range(20):
            self.draw_card(i)
        self.t.fill_rect(X0, BAR_Y, W - 2 * X0, 6, rgb(40, 40, 60))

    def pos(self, i):
        return X0 + (i % COLS) * CELL, Y0 + (i // COLS) * CELL

    def draw_card(self, i):
        x, y = self.pos(i)
        if self.state[i]:
            self.t.fill_rect(x, y, CARD, CARD, FACE if self.state[i] == 1 else rgb(200, 255, 200))
            spr = sprite(ICONS[self.cards[i]], ICON_PAL, 5, FACE if self.state[i] == 1 else rgb(200, 255, 200))
            self.t.blit(spr[0], x + 6, y + 6, spr[1], spr[2])
        else:
            self.t.blit(self.back[0], x, y, CARD, CARD)

    def draw_bar(self, now):
        left = max(0, time.ticks_diff(self.t_end, now))
        w = (W - 2 * X0) * left // self.limit
        if w != self.bar:
            if self.bar < 0:
                self.bar = W - 2 * X0
            c = GOLD if left > 10000 else rgb(255, 60, 60)
            self.t.fill_rect(X0, BAR_Y, w, 6, c)
            if w < self.bar:
                self.t.fill_rect(X0 + w, BAR_Y, self.bar - w, 6, rgb(40, 40, 60))
            self.bar = w
        return left

    def step(self, pt, now):
        left = self.draw_bar(now)
        if left <= 0:
            self.result = "TEMPS ECOULE"
            return False
        if self.hide_at and time.ticks_diff(now, self.hide_at) >= 0:
            for i in self.open:
                self.state[i] = 0
                self.draw_card(i)
            self.open = []
            self.hide_at = 0
        p = self.tap(pt)
        if p is None or self.hide_at:
            return True
        cx = (p[0] - X0) // CELL
        cy = (p[1] - Y0) // CELL
        if not (0 <= cx < COLS and 0 <= cy < ROWS):
            return True
        i = cy * COLS + cx
        if self.state[i]:
            return True
        self.state[i] = 1
        self.draw_card(i)
        self.open.append(i)
        self.sfx.tone(660, 40)
        if len(self.open) == 2:
            a, b = self.open
            if self.cards[a] == self.cards[b]:
                self.combo += 1
                self.score += 100 * self.combo
                self.state[a] = self.state[b] = 2
                self.draw_card(a)
                self.draw_card(b)
                self.open = []
                self.found += 1
                self.sfx.tone(1047, 120)
                if self.found == 10:
                    self.score += (left // 1000) * 20 + 500
                    self.sfx.tune(((784, 90), (988, 90), (1319, 200)))
                    self.board += 1
                    self.text_c("BRAVO !", 150, GOLD, 3, PINK)
                    time.sleep_ms(900)
                    self.new_board(time.ticks_ms())
            else:
                self.combo = 0
                self.hide_at = time.ticks_add(now, 700)
                self.sfx.tone(200, 120)
        return True

    def bot(self, n):
        if not hasattr(self, "cards"):
            return (120, 160) if n % 4 < 2 else None
        if n % 4 >= 2:
            return None
        k = (n // 4) % 20
        x, y = self.pos(k)
        return (x + 20, y + 20)


GAME = Paires


def play(tft, touch, day):
    GAME(tft, touch, day).run()
