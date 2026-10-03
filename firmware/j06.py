"""Jour 6 : ROCHERS 80. Vaisseau fixe au centre, vise le doigt, les rochers se fendent."""

import math
import random

from arcade import BLACK, CYAN, HUD, W, H, Game, overlap, rgb, sprite

NANG = 16
MAXR = 10
SW = 14
SH = 14
CX = (W - SW) // 2
CY = HUD + (H - HUD - SH) // 2
SCX = CX + SW // 2
SCY = CY + SH // 2
SPD = 5
FIRE = 6

SHIP = (
    "...w...",
    "..www..",
    ".wwCww.",
    "wwCCCCw",
    ".wwCww.",
    "..r.r..",
    "...r...",
)
SHIP_PAL = {"w": rgb(220, 240, 255), "C": rgb(40, 120, 255), "r": rgb(255, 90, 40)}
BIG = ((
    "..gggg..",
    ".gwwggg.",
    "ggggwggg",
    "ggggggwg",
    "gwgggggg",
    "gggwgggg",
    ".ggggwg.",
    "..gggg..",
), (
    "...ggg..",
    ".ggwggg.",
    "gggggwgg",
    "ggwggggg",
    "gggggwgg",
    "gwggggg.",
    ".ggwggg.",
    "..ggg...",
))
MED = ((
    ".gggg.",
    "gwgggg",
    "gggwgg",
    "ggggwg",
    "gwgggg",
    ".gggg.",
), (
    "..ggg.",
    "ggwggg",
    "ggggwg",
    "gwgggg",
    "gggwgg",
    ".ggg..",
))
SML = ((
    ".gg.",
    "gwgg",
    "ggwg",
    ".gg.",
), (
    "gg..",
    "gwwg",
    "gwwg",
    "..gg",
))
ROCK_PAL = {"g": rgb(170, 150, 130), "w": rgb(220, 210, 190)}
BOOM = (
    ".y.o.",
    "yoyoy",
    ".owo.",
    "yoyoy",
    ".o.y.",
)
BOOM_PAL = {"y": rgb(255, 220, 50), "o": rgb(255, 110, 30), "w": rgb(255, 255, 255)}
ARTS = (SML, MED, BIG)
PTS = (100, 50, 20)


def _rot(rows, k, n):
    rad = k * 3.14159265 / 8.0
    c = math.cos(rad)
    s = math.sin(rad)
    mid = (n - 1) * 0.5
    out = []
    for nj in range(n):
        line = []
        for ni in range(n):
            x = ni - mid
            y = nj - mid
            oi = int(x * c + y * s + mid + 0.5)
            oj = int(-x * s + y * c + mid + 0.5)
            if 0 <= oi < n and 0 <= oj < n:
                line.append(rows[oj][oi])
            else:
                line.append(".")
        out.append("".join(line))
    return tuple(out)


def _dir16(dx, dy):
    if dx == 0 and dy == 0:
        return -1
    ax = dx if dx >= 0 else -dx
    ay = dy if dy >= 0 else -dy
    if ax * 5 <= ay:
        r = 0
    elif ax * 3 <= ay * 2:
        r = 1
    elif ax * 2 <= ay * 3:
        r = 2
    elif ax <= ay * 5:
        r = 3
    else:
        r = 4
    if dy < 0:
        return r if dx >= 0 else (16 - r) & 15
    if dy > 0:
        return (8 - r) if dx >= 0 else (8 + r)
    return 4 if dx > 0 else 12


def _ir(v):
    return int(v + 0.5) if v >= 0 else int(v - 0.5)


SHOTV = tuple((_ir(SPD * math.sin(k * 3.14159265 / 8.0)),
               _ir(-SPD * math.cos(k * 3.14159265 / 8.0))) for k in range(NANG))


class Rochers(Game):
    TITLE = "ROCHERS 80"
    HELP = ("VISE AVEC LE DOIGT", "DOIGT POSE : CA TIRE", "LES ROCHERS SE FENDENT")

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        self.ships = [sprite(_rot(SHIP, k, 7), SHIP_PAL, 2, BLACK) for k in range(NANG)]
        self.rspr = []
        self.rw = []
        self.rh = []
        self.rpad = []
        for art in ARTS:
            pair = [sprite(a, ROCK_PAL, 2, BLACK, SPD, SPD) for a in art]
            self.rspr.append(pair)
            s = pair[0]
            self.rpad.append(s[3])
            self.rw.append(s[1] - 2 * s[3])
            self.rh.append(s[2] - 2 * s[4])
        self.shot = sprite(("cc", "cc"), {"c": CYAN}, 1, BLACK, SPD, SPD)
        self.boom = sprite(BOOM, BOOM_PAL, 2, BLACK)

    def preview(self, y):
        t = self.t
        b = self.rspr[2][0]
        m = self.rspr[1][0]
        s = self.rspr[0][0]
        sh = self.ships[0]
        t.blit(b[0], 16, y + 16, b[1], b[2])
        t.blit(m[0], 168, y + 8, m[1], m[2])
        t.blit(s[0], 196, y + 52, s[1], s[2])
        t.blit(sh[0], CX - 4, y + 36, sh[1], sh[2])
        t.blit(self.ships[4][0], 70, y + 58, self.ships[4][1], self.ships[4][2])

    def setup(self):
        self.frame = 0
        self.wave = 0
        self.ang = 0
        self.reload = 0
        self.inv = 0
        self.rocks = []
        self.shots = []
        self.booms = []
        self.new_wave()

    def new_wave(self):
        self.wave += 1
        sp = 1 + min(4, self.wave)
        n = 3 + min(3, self.wave - 1)
        if n > 6:
            n = 6
        for _ in range(n):
            self.spawn(2, sp)

    def spawn(self, sz, sp):
        if len(self.rocks) >= MAXR:
            return
        rw, rh = self.rw[sz], self.rh[sz]
        side = random.randint(0, 3)
        if side == 0:
            x, y = random.randint(0, W - rw), HUD + 2
        elif side == 1:
            x, y = random.randint(0, W - rw), H - rh - 2
        elif side == 2:
            x, y = 2, random.randint(HUD, H - rh)
        else:
            x, y = W - rw - 2, random.randint(HUD, H - rh)
        vx = random.randint(-sp, sp)
        vy = random.randint(-sp, sp)
        if vx == 0 and vy == 0:
            vx = sp if side < 2 else 0
            vy = 0 if side < 2 else sp
        if overlap(x, y, rw, rh, CX - 10, CY - 10, SW + 20, SH + 20):
            x, y = 4, HUD + 4
            vx, vy = sp, sp
        self.rocks.append([x, y, vx, vy, sz])

    def _clip_clear(self, x, y, w, h):
        if x < 0:
            w += x
            x = 0
        if x + w > W:
            w = W - x
        if y < HUD:
            h -= HUD - y
            y = HUD
        if y + h > H:
            h = H - y
        if w > 0 and h > 0:
            self.clear(x, y, w, h)

    def erase_rock(self, r):
        p = self.rpad[r[4]]
        self._clip_clear(r[0] - p, r[1] - p, self.rw[r[4]] + 2 * p, self.rh[r[4]] + 2 * p)

    def bust(self, i):
        r = self.rocks[i]
        sz = r[4]
        x, y, vx, vy = r[0], r[1], r[2], r[3]
        self.erase_rock(r)
        self.score += PTS[sz]
        del self.rocks[i]
        self.sfx.tone(220 + sz * 90, 45)
        self.booms.append([x, y, 5])
        if sz == 0:
            return
        room = MAXR - len(self.rocks)
        nnew = 2 if room >= 2 else room
        sp = 1 + min(4, self.wave)
        for k in range(nnew):
            sign = 1 if k == 0 else -1
            nvx = vx - sign * vy // 2
            nvy = vy + sign * vx // 2
            if nvx == 0:
                nvx = sign
            if nvy == 0:
                nvy = -sign
            if nvx > SPD:
                nvx = SPD
            if nvx < -SPD:
                nvx = -SPD
            if nvy > SPD:
                nvy = SPD
            if nvy < -SPD:
                nvy = -SPD
            nx = x + sign * 6
            ny = y + sign * 4
            if nx < 0:
                nx += W
            elif nx > W - 8:
                nx -= W
            if ny < HUD:
                ny += H - HUD
            elif ny > H - 8:
                ny -= H - HUD
            self.rocks.append([nx, ny, nvx, nvy, sz - 1])

    def hurt(self):
        if self.inv:
            return
        self.lives -= 1
        self.inv = 45
        self.sfx.tone(110, 280)
        self.booms.append([CX, CY, 8])

    def step(self, pt, now):
        self.frame += 1
        f = self.frame
        if self.inv:
            self.inv -= 1

        if pt:
            d = _dir16(pt[0] - SCX, pt[1] - SCY)
            if d >= 0:
                self.ang = d
            if self.reload == 0 and len(self.shots) < 2:
                vx, vy = SHOTV[self.ang]
                self.shots.append([SCX - 1, SCY - 1, vx, vy])
                self.reload = FIRE
                self.sfx.tone(1400, 18)
        if self.reload:
            self.reload -= 1

        keep = []
        for s in self.shots:
            ox, oy = s[0], s[1]
            nx = ox + s[2]
            ny = oy + s[3]
            if nx < 1 or nx > W - 3 or ny < HUD + 1 or ny > H - 3:
                self._clip_clear(ox - SPD, oy - SPD, 2 + 2 * SPD, 2 + 2 * SPD)
                continue
            s[0], s[1] = nx, ny
            hit = -1
            for i in range(len(self.rocks) - 1, -1, -1):
                r = self.rocks[i]
                if overlap(nx, ny, 2, 2, r[0], r[1], self.rw[r[4]], self.rh[r[4]]):
                    hit = i
                    break
            if hit >= 0:
                self._clip_clear(ox - SPD, oy - SPD, 2 + 2 * SPD, 2 + 2 * SPD)
                self.bust(hit)
            else:
                self.put(self.shot, nx, ny)
                keep.append(s)
        self.shots = keep

        fr = (f >> 3) & 1
        for r in self.rocks:
            sz = r[4]
            ox, oy = r[0], r[1]
            nx = ox + r[2]
            ny = oy + r[3]
            rw, rh = self.rw[sz], self.rh[sz]
            jumped = False
            if nx < -rw:
                nx = W
                jumped = True
            elif nx > W:
                nx = -rw
                jumped = True
            if ny < HUD - rh:
                ny = H
                jumped = True
            elif ny > H:
                ny = HUD - rh
                jumped = True
            if jumped:
                self.erase_rock(r)
            r[0], r[1] = nx, ny
            self.put(self.rspr[sz][fr], nx, ny)
            if not self.inv and overlap(CX + 3, CY + 3, 8, 8, nx + 1, ny + 1, rw - 2, rh - 2):
                self.hurt()

        keep = []
        for b in self.booms:
            b[2] -= 1
            if b[2] <= 0:
                self._clip_clear(b[0], b[1], 10, 10)
            else:
                self.put(self.boom, b[0], b[1])
                keep.append(b)
        self.booms = keep

        if self.inv == 0 or (f & 2):
            self.put(self.ships[self.ang], CX, CY)
        else:
            self._clip_clear(CX, CY, SW, SH)

        if not self.rocks:
            self.score += 100 * self.wave
            self.sfx.tone(880, 80)
            self.new_wave()
        return self.lives > 0

    def bot(self, n):
        if not hasattr(self, "rocks"):
            return (120, 160) if n % 4 < 2 else None
        if n % 10 == 9:
            return None
        best = None
        bd = 999999
        for r in self.rocks:
            dx = r[0] + self.rw[r[4]] // 2 - SCX
            dy = r[1] + self.rh[r[4]] // 2 - SCY
            d = dx * dx + dy * dy
            if d < bd:
                bd = d
                best = r
        if best is None:
            return (SCX + 20, SCY)
        tx = best[0] + self.rw[best[4]] // 2
        ty = best[1] + self.rh[best[4]] // 2
        return (max(8, min(232, tx)), max(HUD + 8, min(310, ty)))


GAME = Rochers


def play(tft, touch, day):
    GAME(tft, touch, day).run()
