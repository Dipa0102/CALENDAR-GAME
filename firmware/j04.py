"""Jour 4 : PING 80, duel de raquettes contre l'ordinateur. Premier a 7."""

import random
import time

from arcade import BLACK, CYAN, GOLD, GREY, NIGHT, PINK, W, Game, rgb, sprite
from font8 import draw_text

TOP_Y = 34
BOT_Y = 292
PW = 44
PH = 8
BALL = 8
MID = 176
WIN = 7

PADDLE_P = ("wwwwwwwwwwwwwwwwwwwwww", "cccccccccccccccccccccc", "CCCCCCCCCCCCCCCCCCCCCC", ".CCCCCCCCCCCCCCCCCCCC.")
PADDLE_A = ("pppppppppppppppppppppp", "PPPPPPPPPPPPPPPPPPPPPP", "PPPPPPPPPPPPPPPPPPPPPP", ".PPPPPPPPPPPPPPPPPPPP.")
PAL = {"w": rgb(220, 255, 255), "c": CYAN, "C": rgb(0, 120, 200), "p": rgb(255, 150, 230), "P": PINK}
BALL_ART = (".yy.", "ywyy", "yyyy", ".yy.")
BALL_PAL = {"y": GOLD, "w": rgb(255, 255, 255)}


class Ping(Game):
    TITLE = "PING 80"
    HELP = ("GLISSE LE DOIGT POUR", "RENVOYER LA BALLE", "PREMIER A 7 POINTS")
    LIVES = 1

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.me = sprite(PADDLE_P, PAL, 2, BLACK, 9, 0)
        self.cpu = sprite(PADDLE_A, PAL, 2, BLACK, 9, 0)
        self.ball = sprite(BALL_ART, BALL_PAL, 2, BLACK, 7, 7)
        self.pts = [0, 0]

    def preview(self, y):
        self.t.blit(self.cpu[0], 60, y + 4, self.cpu[1], self.cpu[2])
        self.t.blit(self.me[0], 110, y + 76, self.me[1], self.me[2])
        self.t.blit(self.ball[0], 120, y + 40, self.ball[1], self.ball[2])

    def draw_lives(self):
        s = "%d:%d" % (self.pts[0], self.pts[1])
        if s == self.shown_lives:
            return
        self.t.fill_rect(186, 2, 54, 16, NIGHT)
        draw_text(self.t, s, 194, 6, CYAN, None, 1)
        self.shown_lives = s

    def midline(self, x0=0, x1=W):
        for x in range(x0 - x0 % 16, min(x1, W), 16):
            self.t.fill_rect(x + 2, MID, 10, 2, GREY)

    def setup(self):
        self.pts = [0, 0]
        self.px = self.ax = (W - PW) // 2
        self.target = self.px
        self.speed_ai = 2.6
        self.midline()
        self.serve(1)

    def serve(self, toward):
        self.bx, self.by = W / 2 - 4, MID - 20 if toward < 0 else MID + 12
        self.vx = random.choice((-1.6, 1.6))
        self.vy = 3.0 * toward
        self.speed = 3.4
        self.rally = 0
        self.wait = time.ticks_add(time.ticks_ms(), 700)
        self.put(self.ball, int(self.bx), int(self.by))

    def point(self, who):
        self.clear(int(self.bx) - 7, int(self.by) - 7, 22, 22)
        self.pts[who] += 1
        if who == 0:
            self.score += 500 + 50 * self.rally
            self.sfx.tune(((784, 80), (1047, 120)))
        else:
            self.sfx.tune(((196, 160),))
        self.midline()
        if max(self.pts) >= WIN:
            if self.pts[0] >= WIN:
                self.score += 3000
                self.result = "VICTOIRE !"
            else:
                self.result = "PERDU !"
            return False
        self.speed_ai = min(4.2, self.speed_ai + 0.15)
        self.serve(-1 if who == 0 else 1)
        return True

    def bounce(self, pad_x, down):
        off = ((self.bx + BALL / 2) - (pad_x + PW / 2)) / (PW / 2 + 4)
        off = max(-1.0, min(1.0, off))
        self.speed = min(6.0, self.speed + 0.2)
        self.vx = self.speed * off * 0.9
        vy = max(1.8, (self.speed * self.speed - self.vx * self.vx) ** 0.5)
        self.vy = vy if down else -vy

    def step(self, pt, now):
        if pt:
            self.target = pt[0] - PW // 2
        d = max(-9, min(9, self.target - self.px))
        self.px = max(0, min(W - PW, self.px + d))

        if self.vy < 0:
            goal = self.bx + BALL / 2 - PW / 2 + (self.vx * 6)
        else:
            goal = (W - PW) / 2
        da = goal - self.ax
        lim = self.speed_ai if self.vy < 0 else 1.5
        self.ax += max(-lim, min(lim, da))
        self.ax = max(0, min(W - PW, self.ax))

        if time.ticks_diff(now, self.wait) < 0:
            self.put(self.me, self.px, BOT_Y)
            self.put(self.cpu, int(self.ax), TOP_Y)
            return True
        oy = self.by
        self.bx += self.vx
        self.by += self.vy
        if self.bx < 0:
            self.bx, self.vx = 0, abs(self.vx)
            self.sfx.tone(600, 15)
        elif self.bx > W - BALL:
            self.bx, self.vx = W - BALL, -abs(self.vx)
            self.sfx.tone(600, 15)
        if self.vy > 0 and BOT_Y - BALL <= self.by <= BOT_Y - BALL + 7 and self.px - BALL < self.bx < self.px + PW:
            self.by = BOT_Y - BALL
            self.bounce(self.px, False)
            self.rally += 1
            self.score += 10 * self.rally
            self.sfx.tone(988, 25)
        elif self.vy < 0 and TOP_Y + PH - 7 <= self.by <= TOP_Y + PH and self.ax - BALL < self.bx < self.ax + PW:
            self.by = TOP_Y + PH
            self.bounce(self.ax, True)
            self.sfx.tone(740, 25)
        if self.by > 316:
            return self.point(1)
        if self.by < TOP_Y - 6:
            return self.point(0)
        self.put(self.ball, int(self.bx), int(self.by))
        if _on_mid(oy) and not _on_mid(self.by):
            self.midline(max(0, int(self.bx) - 24), int(self.bx) + 32)
        self.put(self.me, self.px, BOT_Y)
        self.put(self.cpu, int(self.ax), TOP_Y)
        return True


def _on_mid(y):
    return MID - BALL - 7 <= y <= MID + 8


GAME = Ping


def play(tft, touch, day):
    GAME(tft, touch, day).run()
