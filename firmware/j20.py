"""Jour 20 : LABYRINTHE. La bille glisse vers le doigt dans les couloirs ; etoiles puis la sortie."""

import random
import time

from arcade import BLACK, CYAN, GOLD, NIGHT, PINK, RED, W, WHITE, Game, rgb, sprite

Y0 = 22
BAR_Y = 312
BAR_X = 8
BAR_W = W - 16
BAR_H = 6
WT = 2
FLOOR = rgb(16, 28, 52)
WALL = rgb(78, 128, 168)
DOOR = rgb(70, 70, 92)
OPENC = rgb(40, 120, 70)
BAR_BG = rgb(36, 36, 56)
SIZES = (24, 20, 16)

BALL = (
    "..wwww..",
    ".wCCCCw.",
    "wCwwCCCw",
    "wCCCCCCw",
    "wCCCCCCw",
    "wCCCCCcw",
    ".wCCCCw.",
    "..cccc..",
)
BALL_PAL = {"w": WHITE, "C": rgb(40, 200, 255), "c": rgb(20, 90, 160)}
STAR = (
    "...yy...",
    "...yy...",
    "yyyyyyyy",
    ".yyYYyy.",
    "..yYYy..",
    ".yy..yy.",
    "yy....yy",
    "........",
)
STAR_PAL = {"y": rgb(255, 200, 30), "Y": rgb(255, 255, 180)}


class Labyrinthe(Game):
    TITLE = "LABYRINTHE"
    HELP = ("LA BILLE SUIT TON DOIGT", "RAMASSE LES ETOILES", "SORTIE AVANT LA FIN")
    BG = FLOOR

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.ball = sprite(BALL, BALL_PAL, 1, FLOOR)
        self.star = sprite(STAR, STAR_PAL, 1, FLOOR)
        self.star_on = sprite(STAR, STAR_PAL, 1, OPENC)

    def preview(self, y):
        t = self.t
        cs = 12
        x0, y0 = 36, y + 6
        t.fill_rect(x0, y0, 14 * cs, 7 * cs, FLOOR)
        t.rect(x0, y0, 14 * cs, 7 * cs, WALL)
        t.rect(x0 + 1, y0 + 1, 14 * cs - 2, 7 * cs - 2, WALL)
        for x, h, yy in ((4, 3, 0), (8, 4, 3), (11, 3, 0)):
            t.fill_rect(x0 + x * cs, y0 + yy * cs, WT, h * cs, WALL)
        for yb, w, xx in ((3, 5, 0), (2, 4, 8), (5, 6, 4)):
            t.fill_rect(x0 + xx * cs, y0 + yb * cs, w * cs, WT, WALL)
        t.blit(self.star[0], x0 + 2 * cs + 2, y0 + 5 * cs + 2, 8, 8)
        t.blit(self.star[0], x0 + 12 * cs + 2, y0 + cs + 2, 8, 8)
        t.fill_rect(x0 + 12 * cs + 2, y0 + 5 * cs + 2, 8, 8, OPENC)
        t.blit(self.ball[0], x0 + cs + 2, y0 + cs + 2, 8, 8)

    def setup(self):
        self.level = 1
        self.new_level()

    def new_level(self):
        lv = self.level
        cs = SIZES[2 if lv >= 3 else lv - 1]
        self.cs = cs
        self.mw = W // cs
        self.mh = (BAR_Y - Y0) // cs
        self.x0 = (W - self.mw * cs) // 2
        self.y0 = Y0 + (BAR_Y - Y0 - self.mh * cs) // 2
        self.rad = 4
        self.spd = 3 if cs == 16 else 4
        self.carve()
        if random.getrandbits(1):
            self.sx = 0
        else:
            self.sx = self.mw - 1
        if random.getrandbits(1):
            self.sy = 0
        else:
            self.sy = self.mh - 1
        self.ex = self.mw - 1 - self.sx
        self.ey = self.mh - 1 - self.sy
        self.place()
        self.stamp = bytes(self.rooms)
        self.limit = (28 + self.mw + self.mh) * 1000
        self.banner()
        self.begin()

    def carve(self):
        mw, mh = self.mw, self.mh
        vw = bytearray(mh * (mw + 1))
        hw = bytearray((mh + 1) * mw)
        for i in range(len(vw)):
            vw[i] = 1
        for i in range(len(hw)):
            hw[i] = 1
        vis = bytearray(mw * mh)
        stack = [0]
        vis[0] = 1
        while stack:
            i = stack[-1]
            x = i % mw
            y = i // mw
            nbs = []
            if x > 0 and vis[i - 1] == 0:
                nbs.append(0)
            if x < mw - 1 and vis[i + 1] == 0:
                nbs.append(1)
            if y > 0 and vis[i - mw] == 0:
                nbs.append(2)
            if y < mh - 1 and vis[i + mw] == 0:
                nbs.append(3)
            if not nbs:
                stack.pop()
                continue
            side = nbs[random.randint(0, len(nbs) - 1)]
            if side == 0:
                ni = i - 1
                vw[y * (mw + 1) + x] = 0
            elif side == 1:
                ni = i + 1
                vw[y * (mw + 1) + x + 1] = 0
            elif side == 2:
                ni = i - mw
                hw[y * mw + x] = 0
            else:
                ni = i + mw
                hw[(y + 1) * mw + x] = 0
            vis[ni] = 1
            stack.append(ni)
        self.vwall = vw
        self.hwall = hw

    def place(self):
        mw, mh = self.mw, self.mh
        rooms = bytearray(mw * mh)
        start = self.sy * mw + self.sx
        end = self.ey * mw + self.ex
        rooms[end] = 2
        need = 3 + self.level
        if need > 8:
            need = 8
        n = 0
        guard = 0
        while n < need and guard < 400:
            guard += 1
            i = random.randint(0, mw * mh - 1)
            if i != start and rooms[i] == 0:
                rooms[i] = 1
                n += 1
        self.rooms = rooms
        self.need = n
        self.got = 0

    def banner(self):
        t = self.t
        t.fill(BLACK)
        self.hud()
        self.text_c("NIVEAU %d" % self.level, 128, GOLD, 2, PINK)
        self.text_c("%d ETOILES" % self.need, 158, CYAN)
        self.sfx.tune(((523, 70), (659, 70), (784, 110)))
        time.sleep_ms(400)

    def begin(self):
        self.paint()
        self.bx = self.x0 + self.sx * self.cs + self.cs // 2
        self.by = self.y0 + self.sy * self.cs + self.cs // 2
        self.put_ball()
        self.t_end = time.ticks_add(time.ticks_ms(), self.limit)
        self.barw = -1
        self.draw_bar(time.ticks_ms())

    def paint(self):
        t = self.t
        t.fill_rect(0, Y0, W, BAR_Y - Y0, NIGHT)
        t.fill_rect(self.x0, self.y0, self.mw * self.cs, self.mh * self.cs, FLOOR)
        self.draw_walls()
        self.draw_exit()
        rooms = self.rooms
        for i in range(len(rooms)):
            if rooms[i] == 1:
                self.blit_star(i % self.mw, i // self.mw)
        t.fill_rect(BAR_X, BAR_Y, BAR_W, BAR_H, BAR_BG)

    def vx(self, k):
        p = self.x0 + k * self.cs
        if k == self.mw:
            p -= WT
        return p

    def hy(self, k):
        p = self.y0 + k * self.cs
        if k == self.mh:
            p -= WT
        return p

    def draw_walls(self):
        t = self.t
        mw, mh, cs = self.mw, self.mh, self.cs
        vw, hw = self.vwall, self.hwall
        y0, x0 = self.y0, self.x0
        for y in range(mh):
            py = y0 + y * cs
            row = y * (mw + 1)
            for x in range(mw + 1):
                if vw[row + x]:
                    t.fill_rect(self.vx(x), py, WT, cs + WT, WALL)
        for y in range(mh + 1):
            py = self.hy(y)
            row = y * mw
            for x in range(mw):
                if hw[row + x]:
                    t.fill_rect(x0 + x * cs, py, cs + WT, WT, WALL)

    def draw_exit(self):
        cs = self.cs
        x = self.x0 + self.ex * cs + WT
        y = self.y0 + self.ey * cs + WT
        s = cs - 2 * WT
        c = OPENC if self.got >= self.need else DOOR
        self.t.fill_rect(x, y, s, s, c)

    def blit_star(self, cx, cy):
        cs = self.cs
        x = self.x0 + cx * cs + (cs - 8) // 2
        y = self.y0 + cy * cs + (cs - 8) // 2
        spr = self.star_on if (cx == self.ex and cy == self.ey and self.got >= self.need) else self.star
        self.t.blit(spr[0], x, y, 8, 8)

    def cell_col(self, cx, cy):
        if cx == self.ex and cy == self.ey:
            return OPENC if self.got >= self.need else DOOR
        return FLOOR

    def put_ball(self):
        r = self.rad
        self.put(self.ball, self.bx - r, self.by - r)

    def erase_ball(self, x, y):
        r = self.rad
        cx = (x - self.x0) // self.cs
        cy = (y - self.y0) // self.cs
        if cx < 0:
            cx = 0
        if cy < 0:
            cy = 0
        if cx >= self.mw:
            cx = self.mw - 1
        if cy >= self.mh:
            cy = self.mh - 1
        self.t.fill_rect(x - r, y - r, r * 2, r * 2, self.cell_col(cx, cy))

    def clip_x(self, nx):
        bx, by = self.bx, self.by
        if nx == bx:
            return nx
        R = self.rad
        cs = self.cs
        mw, mh = self.mw, self.mh
        y0 = self.y0
        cy0 = (by - R + 1 - y0) // cs
        cy1 = (by + R - 1 - y0) // cs
        if cy0 < 0:
            cy0 = 0
        if cy1 >= mh:
            cy1 = mh - 1
        cx = (bx - self.x0) // cs
        if cx < 0:
            cx = 0
        if cx >= mw:
            cx = mw - 1
        vw = self.vwall
        if nx > bx:
            k = cx + 1
            for cy in range(cy0, cy1 + 1):
                if vw[cy * (mw + 1) + k]:
                    lim = self.vx(k) - R
                    if nx > lim:
                        nx = lim
        else:
            k = cx
            for cy in range(cy0, cy1 + 1):
                if vw[cy * (mw + 1) + k]:
                    lim = self.vx(k) + WT + R
                    if nx < lim:
                        nx = lim
        return nx

    def clip_y(self, ny):
        bx, by = self.bx, self.by
        if ny == by:
            return ny
        R = self.rad
        cs = self.cs
        mw, mh = self.mw, self.mh
        x0 = self.x0
        cx0 = (bx - R + 1 - x0) // cs
        cx1 = (bx + R - 1 - x0) // cs
        if cx0 < 0:
            cx0 = 0
        if cx1 >= mw:
            cx1 = mw - 1
        cy = (by - self.y0) // cs
        if cy < 0:
            cy = 0
        if cy >= mh:
            cy = mh - 1
        hw = self.hwall
        if ny > by:
            k = cy + 1
            for cx in range(cx0, cx1 + 1):
                if hw[k * mw + cx]:
                    lim = self.hy(k) - R
                    if ny > lim:
                        ny = lim
        else:
            k = cy
            for cx in range(cx0, cx1 + 1):
                if hw[k * mw + cx]:
                    lim = self.hy(k) + WT + R
                    if ny < lim:
                        ny = lim
        return ny

    def slide(self, pt):
        dx = pt[0] - self.bx
        dy = pt[1] - self.by
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        if ax < 3 and ay < 3:
            return
        sp = self.spd
        sx = 0
        sy = 0
        if ax >= ay:
            sx = sp if dx > 0 else -sp
            if ay * 2 >= ax:
                sy = (sp if dy > 0 else -sp) * 3 // 4
        else:
            sy = sp if dy > 0 else -sp
            if ax * 2 >= ay:
                sx = (sp if dx > 0 else -sp) * 3 // 4
        nx = self.clip_x(self.bx + sx)
        ny = self.clip_y(self.by + sy)
        if nx == self.bx and sx:
            if dy:
                ny = self.clip_y(self.by + (sp if dy > 0 else -sp))
        if ny == self.by and sy:
            if dx:
                nx = self.clip_x(self.bx + (sp if dx > 0 else -sp))
        if nx == self.bx and ny == self.by:
            return
        self.erase_ball(self.bx, self.by)
        self.bx = nx
        self.by = ny
        self.touch_cell()
        self.put_ball()

    def touch_cell(self):
        cx = (self.bx - self.x0) // self.cs
        cy = (self.by - self.y0) // self.cs
        if cx < 0 or cy < 0 or cx >= self.mw or cy >= self.mh:
            return 0
        i = cy * self.mw + cx
        v = self.rooms[i]
        if v == 1:
            self.rooms[i] = 0
            self.got += 1
            self.score += 25 * self.level
            self.sfx.tone(1320, 35)
            cs = self.cs
            x = self.x0 + cx * cs + WT
            y = self.y0 + cy * cs + WT
            self.t.fill_rect(x, y, cs - 2 * WT, cs - 2 * WT, self.cell_col(cx, cy))
            if self.got == self.need:
                self.draw_exit()
                self.sfx.tone(1760, 90)
            return 1
        if v == 2 and self.got >= self.need:
            return 2
        return 0

    def draw_bar(self, now):
        left = time.ticks_diff(self.t_end, now)
        if left < 0:
            left = 0
        w = BAR_W * left // self.limit
        old = self.barw
        if w == old:
            return left
        c = GOLD if left > 8000 else RED
        if w > 0:
            self.t.fill_rect(BAR_X, BAR_Y, w, BAR_H, c)
        if old < 0:
            old = BAR_W
        if w < old:
            self.t.fill_rect(BAR_X + w, BAR_Y, old - w, BAR_H, BAR_BG)
        self.barw = w
        return left

    def lose(self):
        self.sfx.tone(110, 350)
        self.lives -= 1
        if self.lives <= 0:
            self.result = "TEMPS ECOULE"
            return False
        self.rooms = bytearray(self.stamp)
        self.got = 0
        self.begin()
        return True

    def win_level(self):
        left = time.ticks_diff(self.t_end, time.ticks_ms())
        if left < 0:
            left = 0
        self.score += (left // 1000) * 8 * self.level + 200
        self.sfx.tune(((784, 80), (988, 80), (1175, 160)))
        self.level += 1
        if self.level % 3 == 1 and self.lives < 5:
            self.lives += 1
        self.new_level()

    def step(self, pt, now):
        left = self.draw_bar(now)
        if left <= 0:
            return self.lose()
        if pt:
            self.slide(pt)
            cx = (self.bx - self.x0) // self.cs
            cy = (self.by - self.y0) // self.cs
            if 0 <= cx < self.mw and 0 <= cy < self.mh:
                if self.rooms[cy * self.mw + cx] == 2 and self.got >= self.need:
                    self.win_level()
        return True

    def bot(self, n):
        if not hasattr(self, "rooms") or self.lives <= 0:
            return (120, 160) if n % 4 < 2 else None
        mw, mh = self.mw, self.mh
        cx = (self.bx - self.x0) // self.cs
        cy = (self.by - self.y0) // self.cs
        if cx < 0:
            cx = 0
        if cy < 0:
            cy = 0
        if cx >= mw:
            cx = mw - 1
        if cy >= mh:
            cy = mh - 1
        start = cy * mw + cx
        if getattr(self, "bpos", -1) == start and n % 10:
            return self.bpt
        want = 2 if self.got >= self.need else 1
        prev = [0] * (mw * mh)
        seen = bytearray(mw * mh)
        seen[start] = 1
        q = [start]
        k = 0
        goal = -1
        vw, hw = self.vwall, self.hwall
        rooms = self.rooms
        while k < len(q):
            i = q[k]
            k += 1
            if rooms[i] == want:
                goal = i
                break
            x = i % mw
            y = i // mw
            if x < mw - 1 and vw[y * (mw + 1) + x + 1] == 0:
                j = i + 1
                if seen[j] == 0:
                    seen[j] = 1
                    prev[j] = i
                    q.append(j)
            if x > 0 and vw[y * (mw + 1) + x] == 0:
                j = i - 1
                if seen[j] == 0:
                    seen[j] = 1
                    prev[j] = i
                    q.append(j)
            if y < mh - 1 and hw[(y + 1) * mw + x] == 0:
                j = i + mw
                if seen[j] == 0:
                    seen[j] = 1
                    prev[j] = i
                    q.append(j)
            if y > 0 and hw[y * mw + x] == 0:
                j = i - mw
                if seen[j] == 0:
                    seen[j] = 1
                    prev[j] = i
                    q.append(j)
        if goal < 0:
            j = start
        else:
            j = goal
            while prev[j] != start and j != start:
                j = prev[j]
        self.bpos = start
        self.bpt = (self.x0 + (j % mw) * self.cs + self.cs // 2,
                    self.y0 + (j // mw) * self.cs + self.cs // 2)
        return self.bpt


GAME = Labyrinthe


def play(tft, touch, day):
    GAME(tft, touch, day).run()
