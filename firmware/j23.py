"""Jour 23 : AIGUILLAGES. Toucher les aiguillages pour mener chaque train a la gare de sa couleur."""

import random
import time

from arcade import CYAN, GOLD, NIGHT, PINK, WHITE, W, Game, overlap, rgb, sprite
from font8 import draw_text

GROUND = rgb(16, 34, 58)
SNOW = rgb(190, 205, 235)
BALLAST = rgb(84, 76, 86)
SLEEPER = rgb(150, 96, 52)
RAIL = rgb(215, 220, 235)
DOOR = rgb(24, 18, 34)
OFF = rgb(40, 40, 50)
R = 16
TOUCH2 = 30 * 30
Y_IN = 28
ST_Y = 282
COLORS = ((235, 40, 50), (50, 120, 255), (255, 210, 0), (40, 220, 90), (235, 70, 235))

# (x de l'entree, aiguillages (x, y, gauche, droite), x des gares) ; noeud 100 + k = gare k.
# Chaque branche s'ecarte d'au moins R + 8 px : le train ressort du disque sans le chevaucher.
LAYOUTS = (
    (120, ((120, 86, 1, 2), (60, 176, 100, 101), (180, 176, 102, 103)), (30, 90, 150, 210)),
    (114, ((114, 70, 1, 2), (48, 170, 100, 101), (180, 140, 3, 104), (144, 214, 102, 103)),
     (24, 72, 120, 168, 216)),
)

LOCO = (
    "................",
    "...kkkkkkkkkk...",
    "..kCCCCCCCCCCk..",
    "..kCwwCCCCwwCk..",
    "..kCwwCCCCwwCk..",
    "..kCCCCCCCCCCk..",
    "..kkkkkkkkkkkk..",
    "...kcHcccccck...",
    "...kcHcKKccck...",
    "...kcHcKKccck...",
    "...kcHcccccck...",
    "...kcHcyyccck...",
    "...kcHcyyccck...",
    "...kcccccccck...",
    "..gggggggggggg..",
    "...W........W...",
)
DISC = (
    ".....oooooo.....",
    "...oobbyybboo...",
    "..obbbbyybbbbo..",
    ".obbbbbyybbbbbo.",
    ".obbbybyybbbbbo.",
    "obbbyybyybbbbbbo",
    "obbyyybyybbbbbbo",
    "obyyyyyyybbbbbbo",
    "obyyyyyyybbbbbbo",
    "obbyyybbbbbbbbbo",
    "obbbyybbbbbbbbbo",
    ".obbbybbbbbbbbo.",
    ".obbbbbbbbbbbbo.",
    "..obbbbbbbbbbo..",
    "...oobbbbbboo...",
    ".....oooooo.....",
)
TREE = ("...w...", "..wgw..", "..ggg..", ".wgggw.", ".ggggg.", "wgggggw", "ggggggg", "...t...", "...t...")
TREE_PAL = {"g": rgb(30, 150, 70), "w": rgb(235, 240, 255), "t": rgb(120, 70, 30)}


def _rev(s):
    c = list(s)
    c.reverse()
    return "".join(c)


def _over(art, base):
    return tuple("".join(a if a != "." else b for a, b in zip(ra, rb)) for ra, rb in zip(art, base))


def _disc_base():
    rows = []
    for j in range(16):
        s = ""
        for i in range(16):
            h = 4 <= j <= 11
            v = 4 <= i <= 11 and j <= 7
            if (h and j in (5, 10)) or (v and i in (5, 10)):
                s += "R"
            elif h or v:
                s += "B"
            else:
                s += "."
        rows.append(s)
    return rows


def _px(buf, p, c):
    buf[p] = c >> 8
    buf[p + 1] = c & 255


class Aiguillages(Game):
    TITLE = "AIGUILLAGES"
    HELP = ("TOUCHE UN AIGUILLAGE", "POUR LE BASCULER", "CHAQUE TRAIN A SA GARE")
    BG = GROUND

    def __init__(self, tft, touch, day):
        Game.__init__(self, tft, touch, day)
        down = LOCO
        right = tuple("".join(down[j][i] for j in range(16)) for i in range(16))
        left = tuple(_rev(r) for r in right)
        vbase = ("..RR........RR..",) * 16
        hbase = tuple(("R" if j in (2, 3, 12, 13) else ".") * 16 for j in range(16))
        arts = (_over(down, vbase), _over(left, hbase), _over(right, hbase))
        self.locos = []
        for c in COLORS:
            pal = {"c": rgb(*c), "C": rgb(c[0] * 3 // 5, c[1] * 3 // 5, c[2] * 3 // 5),
                   "H": rgb(min(255, c[0] + 110), min(255, c[1] + 110), min(255, c[2] + 110)),
                   "k": rgb(30, 28, 40), "w": rgb(170, 220, 255), "K": rgb(8, 8, 8),
                   "y": GOLD, "g": rgb(150, 150, 165), "W": rgb(255, 250, 190), "R": RAIL}
            for a in arts:
                self.locos.append(sprite(a, pal, 1, BALLAST)[0])
        base = _disc_base()
        dpal = {"o": WHITE, "b": rgb(20, 24, 80), "y": GOLD, "B": BALLAST, "R": RAIL}
        dl = _over(DISC, base)
        self.discs = (sprite(dl, dpal, 2, GROUND), sprite(tuple(_rev(r) for r in dl), dpal, 2, GROUND))
        self.tree = sprite(TREE, TREE_PAL, 2, GROUND)
        # voie verticale : ligne r = ordonnee y avec y % 8 == r % 8 (traverses sur y % 8 < 2)
        vt = bytearray(16 * 24 * 2)
        for r in range(24):
            for i in range(16):
                _px(vt, (r * 16 + i) * 2, RAIL if i in (2, 3, 12, 13) else (SLEEPER if r % 8 < 2 else BALLAST))
        self.vt = memoryview(vt)
        self.sc = bytearray(16 * 26 * 2)
        self.strips = {}
        self.obst = []

    # --- decor ------------------------------------------------------------
    def vtrack(self, x, y0, y1):
        if y1 <= y0:
            return
        t = self.t
        t.fill_rect(x - 8, y0, 16, y1 - y0, BALLAST)
        for y in range(y0 - y0 % 8, y1, 8):
            a = max(y, y0)
            b = min(y + 2, y1)
            if b > a:
                t.fill_rect(x - 8, a, 16, b - a, SLEEPER)
        t.fill_rect(x - 6, y0, 2, y1 - y0, RAIL)
        t.fill_rect(x + 4, y0, 2, y1 - y0, RAIL)
        self.obst.append((x - 10, y0, 20, y1 - y0))

    def htrack(self, x0, x1, y):
        if x1 <= x0:
            return
        t = self.t
        t.fill_rect(x0, y - 8, x1 - x0, 16, BALLAST)
        for x in range(x0 - x0 % 8, x1, 8):
            a = max(x, x0)
            b = min(x + 2, x1)
            if b > a:
                t.fill_rect(a, y - 8, b - a, 16, SLEEPER)
        t.fill_rect(x0, y - 6, x1 - x0, 2, RAIL)
        t.fill_rect(x0, y + 4, x1 - x0, 2, RAIL)
        self.obst.append((x0, y - 10, x1 - x0, 20))

    def strip(self, ph, tw):
        """Bande de voie horizontale de tw colonnes commencant a x % 8 == ph."""
        k = ph * 16 + tw
        b = self.strips.get(k)
        if b is None:
            b = bytearray(tw * 32)
            for j in range(16):
                for i in range(tw):
                    c = RAIL if j in (2, 3, 12, 13) else (SLEEPER if (ph + i) % 8 < 2 else BALLAST)
                    _px(b, (j * tw + i) * 2, c)
            self.strips[k] = b
        return b

    def preview(self, y):
        t = self.t
        t.fill_rect(24, y, 192, 96, GROUND)
        t.rect(24, y, 192, 96, CYAN)
        self.htrack(68, 104, y + 46)
        self.htrack(136, 172, y + 46)
        self.vtrack(120, y + 1, y + 46)
        self.vtrack(60, y + 38, y + 95)
        self.vtrack(180, y + 38, y + 95)
        s = self.discs[1]
        t.blit(s[0], 104, y + 30, 32, 32)
        t.blit(self.locos[0], 112, y + 6, 16, 16)
        t.blit(self.locos[5], 172, y + 70, 16, 16)
        t.blit(self.locos[7], 52, y + 64, 16, 16)
        t.blit(self.tree[0], 32, y + 8, 14, 18)
        t.blit(self.tree[0], 196, y + 12, 14, 18)

    def nx(self, n):
        return self.lay[2][n - 100] if n >= 100 else self.sws[n][0]

    def ny(self, n):
        return ST_Y - 8 if n >= 100 else self.sws[n][1] - R - 8

    def disc(self, s, c=None):
        sx, sy = self.sws[s][0], self.sws[s][1]
        self.t.blit(self.discs[self.state[s]][0], sx - 16, sy - 16, 32, 32)
        if c is not None:
            self.t.fill_rect(sx - 4, sy + 6, 8, 6, c)

    def station(self, k, door=DOOR):
        t = self.t
        x = self.lay[2][k]
        if door == DOOR:
            t.fill_rect(x - 21, ST_Y, 42, 36, rgb(*COLORS[self.st_col[k]]))
            t.fill_rect(x - 21, ST_Y, 42, 3, WHITE)
            t.fill_rect(x - 17, ST_Y + 20, 7, 7, rgb(255, 240, 160))
            t.fill_rect(x + 10, ST_Y + 20, 7, 7, rgb(255, 240, 160))
            t.fill_rect(x - 21, ST_Y + 34, 42, 2, rgb(10, 10, 20))
        t.fill_rect(x - 8, ST_Y, 16, 16, door)

    def lamp(self):
        c = rgb(*COLORS[self.nextc]) if self.spawned < self.quota else OFF
        self.t.fill_rect(self.lay[0] + 13, 24, 10, 10, c)

    def scene(self):
        t = self.t
        ex, sws, sts = self.lay
        t.fill_rect(0, 20, W, 300, GROUND)
        for _ in range(46):
            t.fill_rect(random.randint(0, 237), random.randint(22, 316), 2, 2, SNOW)
        self.obst = [(ex + 8, 20, 32, 20), (184, 20, 56, 16)]
        for sx, sy, a, b in sws:
            for c in (a, b):
                cx = self.nx(c)
                if cx < sx:
                    self.htrack(cx + 8, sx - R, sy)
                else:
                    self.htrack(sx + R, cx - 8, sy)
        self.vtrack(ex, 20, sws[0][1])
        for sx, sy, a, b in sws:
            for c in (a, b):
                self.vtrack(self.nx(c), sy - 8, ST_Y if c >= 100 else sws[c][1])
        for s in range(len(sws)):
            self.disc(s)
            self.obst.append((sws[s][0] - 18, sws[s][1] - 18, 36, 36))
        for k in range(len(sts)):
            self.station(k)
        self.obst.append((0, ST_Y - 4, W, 40))
        n = 0
        for _ in range(40):
            x = random.randint(2, W - 16)
            y = random.randint(24, ST_Y - 22)
            ok = True
            for o in self.obst:
                if overlap(x - 2, y - 2, 18, 22, o[0], o[1], o[2], o[3]):
                    ok = False
                    break
            if ok:
                t.blit(self.tree[0], x, y, 14, 18)
                self.obst.append((x, y, 14, 18))
                n += 1
                if n >= 7:
                    break
        t.fill_rect(ex + 11, 22, 14, 14, WHITE)
        self.lamp()
        draw_text(t, "NIV %d" % self.level, 192, 24, CYAN, GROUND)

    # --- niveaux ----------------------------------------------------------
    def setup(self):
        self.level = 1
        self.trains = []
        self.new_level()

    def new_level(self):
        lv = self.level
        self.lay = LAYOUTS[0 if lv < 3 else 1]
        self.sws = self.lay[1]
        n = len(self.lay[2])
        cols = list(range(n))
        if lv > 1:
            for i in range(n - 1, 0, -1):
                j = random.randint(0, i)
                cols[i], cols[j] = cols[j], cols[i]
        self.st_col = cols
        self.state = [0] * len(self.sws)
        self.lock = [0] * len(self.sws)
        self.route = []
        for s in range(len(self.sws)):
            d = {}
            for b in (0, 1):
                stack = [self.sws[s][2 + b]]
                while stack:
                    c = stack.pop()
                    if c >= 100:
                        d[cols[c - 100]] = b
                    else:
                        stack.append(self.sws[c][2])
                        stack.append(self.sws[c][3])
            self.route.append(d)
        self.v16 = min(80, 26 + 6 * lv)
        self.gap = max(1100, 3500 - 280 * lv)
        self.quota = 6 + 2 * lv
        self.spawned = 0
        self.errors = 0
        self.trains = []
        self.flash = []
        self.nextc = self.pick()
        self.scene()
        self.next_at = time.ticks_add(time.ticks_ms(), 1200)

    def pick(self):
        return self.st_col[random.randint(0, len(self.st_col) - 1)]

    def level_up(self):
        lv = self.level
        bonus = 50 * lv * (2 if self.errors == 0 else 1)
        self.score += bonus
        self.draw_score()
        t = self.t
        t.fill_rect(20, 124, 200, 60, NIGHT)
        t.rect(20, 124, 200, 60, CYAN)
        self.text_c("NIVEAU %d" % (lv + 1), 134, GOLD, 2, PINK)
        self.text_c(("SANS FAUTE +%d" if self.errors == 0 else "BONUS +%d") % bonus, 162, WHITE)
        self.sfx.tune(((784, 90), (988, 90), (1175, 90), (1568, 180)))
        time.sleep_ms(700)
        self.level += 1
        self.new_level()

    # --- trains -----------------------------------------------------------
    def spawn(self, now):
        ex = self.lay[0]
        for tr in self.trains:
            if tr[2] == 0 and tr[5] == 0 and tr[1] < (Y_IN + 34) << 4:
                return
        self.trains.append([ex << 4, Y_IN << 4, 0, ex, self.ny(0), 0, self.nextc, None, None, 0, 0])
        self.spawned += 1
        self.next_at = time.ticks_add(now, self.gap)
        self.nextc = self.pick()
        self.lamp()

    def draw(self, tr):
        nx = tr[0] >> 4
        ny = tr[1] >> 4
        ox = tr[7]
        oy = tr[8]
        if ox == nx and oy == ny:
            return
        tr[7] = nx
        tr[8] = ny
        d = tr[2]
        spr = self.locos[tr[6] * 3 + d]
        t = self.t
        if ox is None:
            t.blit(spr, nx - 8, ny - 8, 16, 16)
        elif d == 0:
            tw = ny - oy
            p = ((oy - 8) & 7) * 32
            n = tw * 32
            sc = self.sc
            sc[0:n] = self.vt[p:p + n]
            sc[n:n + 512] = spr
            t.blit(sc, nx - 8, oy - 8, 16, 16 + tw)
        else:
            t.blit(spr, nx - 8, ny - 8, 16, 16)
            if d == 2:
                x0 = ox - 8
                tw = nx - ox
            else:
                x0 = nx + 8
                tw = ox - nx
            t.blit(self.strip(x0 & 7, tw), x0, ny - 8, tw, 16)

    def erase(self, tr):
        x = tr[7]
        if x is not None:
            y = tr[8] - 8
            self.t.blit(self.vt[(y & 7) * 32:], x - 8, y, 16, 16)

    def enter(self, tr, now):
        node = tr[5]
        if node >= 100:
            k = node - 100
            if self.st_col[k] == tr[6]:
                self.score += 10 * self.level
                self.sfx.tone(1047, 90)
                self.station(k, GOLD)
            else:
                self.lives -= 1
                self.errors += 1
                self.sfx.tone(120, 350)
                self.station(k, rgb(255, 30, 30))
            self.flash.append((time.ticks_add(now, 350), k))
            return False
        st = self.state[node]
        self.lock[node] += 1
        self.disc(node, rgb(*COLORS[tr[6]]))
        tr[2] = 3
        tr[9] = 48 << 4
        tr[10] = node
        tr[5] = self.sws[node][2 + st]
        return True

    def leave(self, tr):
        s = tr[10]
        sx, sy = self.sws[s][0], self.sws[s][1]
        cx = self.nx(tr[5])
        tr[0] = (sx - 24 if cx < sx else sx + 24) << 4
        tr[1] = sy << 4
        tr[2] = 1 if cx < sx else 2
        tr[3] = cx
        tr[7] = None
        self.lock[s] -= 1
        if not self.lock[s]:
            self.disc(s)

    def touch_at(self, p):
        best = -1
        bd = TOUCH2
        for s in range(len(self.sws)):
            dx = p[0] - self.sws[s][0]
            dy = p[1] - self.sws[s][1]
            d = dx * dx + dy * dy
            if d <= bd:
                bd = d
                best = s
        if best < 0:
            return
        if self.lock[best]:
            self.sfx.tone(160, 70)
            return
        self.state[best] ^= 1
        self.disc(best)
        self.sfx.tone(880 if self.state[best] else 660, 30)

    def step(self, pt, now):
        p = self.tap(pt)
        if p:
            self.touch_at(p)
        if self.flash and time.ticks_diff(now, self.flash[0][0]) >= 0:
            self.station(self.flash.pop(0)[1], DOOR)
        if self.spawned < self.quota and time.ticks_diff(now, self.next_at) >= 0:
            self.spawn(now)
        v = self.v16
        keep = []
        for tr in self.trains:
            d = tr[2]
            if d == 3:
                tr[9] -= v
                if tr[9] <= 0:
                    self.leave(tr)
                keep.append(tr)
                continue
            turn = False
            if d == 0:
                y = tr[1] + v
                if y >= tr[4] << 4:
                    self.erase(tr)
                    if self.enter(tr, now):
                        keep.append(tr)
                    elif self.lives <= 0:
                        return False
                    continue
                tr[1] = y
            else:
                tx = tr[3] << 4
                if d == 2:
                    x = tr[0] + v
                    if x >= tx:
                        x = tx
                        turn = True
                else:
                    x = tr[0] - v
                    if x <= tx:
                        x = tx
                        turn = True
                tr[0] = x
            self.draw(tr)
            if turn:
                tr[2] = 0
                tr[4] = self.ny(tr[5])
            keep.append(tr)
        self.trains = keep
        if not keep and self.spawned >= self.quota and not self.flash:
            self.level_up()
        return self.lives > 0

    def bot(self, n):
        if not hasattr(self, "trains") or self.lives <= 0:
            return (120, 160) if n % 4 < 2 else None
        if n % 2 or (n // 210) % 7 == 6:
            return None
        near = {}
        for tr in self.trains:
            s = tr[5]
            if s >= 100:
                continue
            if tr[2] == 3:
                d = 5000 + tr[9]
            else:
                d = (self.ny(s) << 4) - tr[1] + abs((tr[3] << 4) - tr[0])
            if s not in near or d < near[s][0]:
                near[s] = (d, tr[6])
        for s in near:
            if self.route[s].get(near[s][1], 0) != self.state[s] and not self.lock[s]:
                return (self.sws[s][0] + n % 5 - 2, self.sws[s][1] + n % 7 - 3)
        return None


GAME = Aiguillages


def play(tft, touch, day):
    GAME(tft, touch, day).run()
