"""Moteur commun des jeux du calendrier : sprites, HUD, ecrans, sons, records."""

import json
import time

from font8 import draw_text, glyph
from ili9341 import rgb

W = 240
H = 320
HUD = 20

BLACK = rgb(0, 0, 0)
WHITE = rgb(255, 255, 255)
GOLD = rgb(255, 210, 0)
ORANGE = rgb(255, 140, 30)
RED = rgb(230, 40, 50)
PINK = rgb(255, 40, 200)
CYAN = rgb(0, 220, 255)
GREEN = rgb(40, 220, 90)
BLUE = rgb(60, 110, 255)
VIOLET = rgb(150, 40, 220)
GREY = rgb(120, 120, 140)
NIGHT = rgb(10, 10, 30)
BANDS = ((255, 214, 60), (255, 160, 40), (255, 92, 80), (232, 40, 140), (150, 40, 200))

REC_FILE = "records.json"


def load_rec():
    try:
        with open(REC_FILE) as f:
            rec = json.load(f)
        if isinstance(rec, dict):
            return rec
    except Exception:
        pass
    return {}


def save_rec(rec):
    try:
        with open(REC_FILE, "w") as f:
            json.dump(rec, f)
    except Exception:
        pass


def sprite(rows, pal, s=1, bg=0, px=0, py=0):
    """Sprite pre-compose sur la couleur de fond, avec une marge (px, py) de fond
    qui efface l'ancienne position quand l'objet bouge d'au plus cette marge."""
    h = len(rows)
    w = 0
    for r in rows:
        if len(r) > w:
            w = len(r)
    sw = w * s + 2 * px
    sh = h * s + 2 * py
    buf = bytearray(sw * sh * 2)
    hi, lo = bg >> 8, bg & 255
    for k in range(0, len(buf), 2):
        buf[k] = hi
        buf[k + 1] = lo
    for j in range(h):
        row = rows[j]
        for i in range(len(row)):
            ch = row[i]
            if ch == ".":
                continue
            c = pal[ch]
            ch_hi, ch_lo = c >> 8, c & 255
            for dy in range(s):
                p = ((py + j * s + dy) * sw + px + i * s) * 2
                for dx in range(s):
                    buf[p] = ch_hi
                    buf[p + 1] = ch_lo
                    p += 2
    return (buf, sw, sh, px, py)


def line_sprite(rows, pal, s=1, bg=0, px=0, py=0):
    """Meme image que sprite(), mais une ligne d'ecran par ligne du motif (les lignes
    identiques sont partagees) : petits tampons au lieu d'un gros bloc, que le tas
    morcele ne peut plus fournir. blit_lines() fait le zoom vertical a l'envoi."""
    w = 0
    for r in rows:
        if len(r) > w:
            w = len(r)
    sw = w * s + 2 * px
    hi, lo = bg >> 8, bg & 255
    done = {}
    out = []
    for row in rows:
        ln = done.get(row)
        if ln is None:
            ln = bytearray(sw * 2)
            for k in range(0, len(ln), 2):
                ln[k] = hi
                ln[k + 1] = lo
            for i in range(len(row)):
                ch = row[i]
                if ch == ".":
                    continue
                c = pal[ch]
                ch_hi, ch_lo = c >> 8, c & 255
                p = (px + i * s) * 2
                for dx in range(s):
                    ln[p] = ch_hi
                    ln[p + 1] = ch_lo
                    p += 2
            done[row] = ln
        out.append(ln)
    return (out, sw, len(rows) * s + 2 * py, s, py, bg)


def blit_lines(t, spr, x, y):
    out, sw, sh, s, py, bg = spr
    if py:
        t.fill_rect(x, y, sw, py, bg)
    y += py
    for ln in out:
        t._window(x, y, x + sw - 1, y + s - 1)
        for _ in range(s):
            t.spi.write(ln)
        y += s
    t.cs(1)
    if py:
        t.fill_rect(x, y, sw, py, bg)


class Sfx:
    """Haut-parleur : PWM sur GPIO26, ampli active par GPIO4 a l'etat bas."""

    def __init__(self):
        self.pwm = None
        self.until = 0
        try:
            from machine import PWM, Pin

            self.en = Pin(4, Pin.OUT, value=0)
            self.pwm = PWM(Pin(26), freq=440)
            self._duty(0)
        except Exception:
            self.pwm = None

    def _duty(self, v):
        try:
            self.pwm.duty_u16(v)
        except AttributeError:
            self.pwm.duty(v >> 6)

    def tone(self, freq, ms):
        if not self.pwm:
            return
        try:
            self.pwm.freq(int(freq))
        except Exception:
            return
        self._duty(5000)
        self.until = time.ticks_add(time.ticks_ms(), ms)

    def tick(self):
        if self.until and time.ticks_diff(time.ticks_ms(), self.until) >= 0:
            self.until = 0
            if self.pwm:
                self._duty(0)

    def tune(self, notes):
        for f, ms in notes:
            if f:
                self.tone(f, ms)
            time.sleep_ms(ms)
            if self.pwm:
                self._duty(0)
            time.sleep_ms(15)
        self.until = 0

    def off(self):
        if self.pwm:
            self._duty(0)
            try:
                self.pwm.deinit()
            except Exception:
                pass
            self.pwm = None
        try:
            self.en.value(1)
        except Exception:
            pass


START = ((523, 90), (659, 90), (784, 90), (1047, 180))
LOSE = ((392, 140), (330, 140), (262, 260))
FANFARE = ((523, 100), (523, 100), (784, 100), (1047, 140), (0, 60), (988, 100), (1047, 260))


class Game:
    TITLE = "JEU"
    HELP = ()
    BG = BLACK
    FRAME = 33
    LIVES = 3

    def __init__(self, tft, touch, day):
        try:
            import machine

            machine.freq(240000000)
        except Exception:
            pass
        self.t = tft
        self.touch = touch
        self.day = day
        self.top = HUD
        self.scratch = bytearray(2048)
        self.rec = load_rec()
        self.record = int(self.rec.get(str(day), 0))
        self.sfx = Sfx()
        self.score = 0
        self.lives = self.LIVES
        self.shown = None
        self.shown_lives = None
        self.result = ""
        self.digits = []
        for d in "0123456789":
            buf = bytearray(128)
            g = glyph(d)
            for j in range(8):
                for i in range(8):
                    c = GOLD if g[j] & (0x80 >> i) else NIGHT
                    buf[2 * (j * 8 + i)] = c >> 8
                    buf[2 * (j * 8 + i) + 1] = c & 255
            self.digits.append(buf)
        self.heart = sprite(
            (".rr.rr.", "rwrrrrr", "rrrrrrr", ".rrrrr.", "..rrr..", "...r..."),
            {"r": RED, "w": WHITE},
            1,
            NIGHT,
        )

    # --- dessin -----------------------------------------------------------
    def put(self, spr, x, y):
        buf, w, h, px, py = spr
        x -= px
        y -= py
        t = self.t
        top = self.top
        if x >= 0 and x + w <= W and y >= top and y + h <= H:
            t.blit(buf, x, y, w, h)
            return
        x0 = x if x > 0 else 0
        x1 = x + w if x + w < W else W
        y0 = y if y > top else top
        y1 = y + h if y + h < H else H
        if x0 >= x1 or y0 >= y1:
            return
        mv = memoryview(buf)
        if x0 == x and x1 == x + w:
            t.blit(mv[(y0 - y) * w * 2:], x0, y0, w, y1 - y0)
            return
        cw = (x1 - x0) * 2
        need = cw * (y1 - y0)
        if len(self.scratch) < need:
            self.scratch = bytearray(need)
        sc = self.scratch
        d = 0
        for j in range(y0, y1):
            o = ((j - y) * w + x0 - x) * 2
            sc[d:d + cw] = mv[o:o + cw]
            d += cw
        t.blit(sc, x0, y0, x1 - x0, y1 - y0)

    def clear(self, x, y, w, h, c=None):
        if y < self.top:
            h -= self.top - y
            y = self.top
        if h > 0 and w > 0:
            self.t.fill_rect(x, y, w, h, self.BG if c is None else c)

    def text_c(self, s, y, color, scale=1, shadow=None):
        x = (W - len(s) * 8 * scale) // 2
        if shadow is not None:
            draw_text(self.t, s, x + scale, y + scale, shadow, None, scale)
        draw_text(self.t, s, x, y, color, None, scale)

    def scanlines(self, y, h):
        for k in range(2, h, 3):
            self.t.fill_rect(0, y + k, W, 1, BLACK)

    def bands(self, y, bh=3):
        for i, c in enumerate(BANDS):
            self.t.fill_rect(0, y + i * bh, W, bh, rgb(*c))

    def menu_button(self):
        t = self.t
        t.fill_rect(2, 1, 46, 18, VIOLET)
        t.rect(2, 1, 46, 18, GOLD)
        draw_text(t, "MENU", 9, 6, WHITE, None, 1)

    def hud(self):
        t = self.t
        t.fill_rect(0, 0, W, HUD, NIGHT)
        self.menu_button()
        draw_text(t, "HI", 112, 6, CYAN, None, 1)
        r = "%06d" % min(self.record, 999999)
        for k in range(6):
            draw_text(t, r[k], 130 + k * 8, 6, GREY, None, 1)
        self.shown = None
        self.shown_lives = None
        self.draw_score()
        self.draw_lives()

    def draw_score(self):
        s = "%06d" % min(self.score, 999999)
        old = self.shown
        for k in range(6):
            if old is None or old[k] != s[k]:
                self.t.blit(self.digits[ord(s[k]) - 48], 56 + k * 8, 6, 8, 8)
        self.shown = s

    def draw_lives(self):
        n = max(0, min(self.lives, 5))
        if n == self.shown_lives:
            return
        self.t.fill_rect(186, 2, 54, 16, NIGHT)
        for i in range(n):
            self.put_hud(self.heart, 232 - (i + 1) * 9, 7)
        self.shown_lives = n

    def put_hud(self, spr, x, y):
        self.t.blit(spr[0], x, y, spr[1], spr[2])

    def big_sprite(self, rows, pal, s, y):
        spr = line_sprite(rows, pal, s, BLACK)
        blit_lines(self.t, spr, (W - spr[1]) // 2, y)

    # --- toucher ----------------------------------------------------------
    def wait_release(self):
        while self.touch.point():
            time.sleep_ms(20)

    def wait_tap(self, blink=None):
        on = False
        last = 0
        while True:
            now = time.ticks_ms()
            if blink is not None and time.ticks_diff(now, last) > 450:
                last = now
                on = not on
                blink(on)
            pt = self.touch.point()
            if pt:
                self.wait_release()
                return pt
            time.sleep_ms(25)

    def tap(self, pt):
        """Renvoie le point seulement au moment ou le doigt se pose."""
        if pt:
            if not self.down:
                self.down = True
                return pt
            return None
        self.down = False
        return None

    @staticmethod
    def is_menu(pt):
        return pt[1] < HUD + 4 and pt[0] < 56

    # --- ecrans -----------------------------------------------------------
    def preview(self, y):
        pass

    def title_screen(self):
        t = self.t
        t.fill(BLACK)
        self.menu_button()
        draw_text(t, "JOUR %d" % self.day, 176, 6, CYAN, None, 1)
        self.bands(26)
        name = self.TITLE
        scale = 3 if len(name) <= 9 else 2
        y = 52 if scale == 3 else 56
        self.text_c(name, y, GOLD, scale, PINK)
        self.scanlines(y, 8 * scale + scale)
        self.preview(106)
        for i, line in enumerate(self.HELP[:3]):
            self.text_c(line, 206 + i * 12, WHITE if i == 0 else CYAN)
        self.text_c("RECORD %06d" % self.record, 250, GOLD)
        violet = rgb(90, 20, 140)
        for k in range(1, 5):
            t.fill_rect(0, 296 + k * k, W, 1, violet)
        t.fill_rect(0, 296, W, 2, PINK)

        def blink(on):
            if on:
                self.text_c("TOUCHE POUR JOUER", 274, WHITE)
            else:
                t.fill_rect(0, 274, W, 8, BLACK)

        self.wait_release()
        pt = self.wait_tap(blink)
        return not self.is_menu(pt)

    def ready(self):
        self.text_c("PRET ?", 140, CYAN, 3, VIOLET)
        self.sfx.tune(((440, 120), (0, 200)))
        self.clear(0, 140, W, 28)
        self.text_c("GO !", 140, GOLD, 3, PINK)
        self.sfx.tune(START)
        self.clear(0, 140, W, 28)

    def game_over(self):
        t = self.t
        new = self.score > self.record
        if new:
            self.record = self.score
            self.rec[str(self.day)] = self.score
            save_rec(self.rec)
        t.fill_rect(14, 92, 212, 164, NIGHT)
        t.rect(14, 92, 212, 164, CYAN)
        t.rect(16, 94, 208, 160, PINK)
        self.text_c(self.result or "GAME OVER", 104, PINK, 2, VIOLET)
        self.text_c("SCORE", 132, WHITE)
        self.text_c("%06d" % min(self.score, 999999), 146, GOLD, 3, ORANGE)
        self.text_c("TOUCHE : REJOUER", 222, WHITE)
        self.text_c("MENU : QUITTER", 236, CYAN)
        if new:
            self.text_c("NOUVEAU RECORD !", 186, GOLD, 1)
            self.sfx.tune(FANFARE)
        else:
            self.text_c("RECORD %06d" % self.record, 186, GREY)
            self.sfx.tune(LOSE)
        time.sleep_ms(300)
        self.wait_release()

        def blink(on):
            if new:
                self.text_c("NOUVEAU RECORD !", 186, PINK if on else GOLD)

        pt = self.wait_tap(blink)
        return not self.is_menu(pt)

    # --- a definir dans chaque jeu ---------------------------------------
    def setup(self):
        pass

    def step(self, pt, now):
        return False

    # --- boucle -----------------------------------------------------------
    def run(self):
        try:
            if not self.title_screen():
                return
            while True:
                self.score = 0
                self.lives = self.LIVES
                self.result = ""
                self.t.fill(self.BG)
                self.hud()
                self.ready()
                self.setup()
                self.down = True
                quit = False
                while True:
                    t0 = time.ticks_ms()
                    pt = self.touch.point()
                    if pt and self.is_menu(pt):
                        quit = True
                        break
                    if not self.step(pt, t0):
                        break
                    self.sfx.tick()
                    self.draw_score()
                    self.draw_lives()
                    dt = time.ticks_diff(time.ticks_ms(), t0)
                    if dt < self.FRAME:
                        time.sleep_ms(self.FRAME - dt)
                self.sfx.tick()
                if quit:
                    return
                self.draw_score()
                if not self.game_over():
                    return
        finally:
            self.sfx.off()


def overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah
