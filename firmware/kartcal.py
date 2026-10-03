"""
Calendar Game — calendrier, meteo, notes, reglages, calendrier de l'Avent arcade.
E32R28T / ESP32-32E / ILI9341 / XPT2046. MicroPython.

Pastilles de notes : icones originales (champignon, drapeau, etoile,
cloche, coche). Pas de personnages proteges.
"""

import time
from machine import Pin, SPI
import boardio

from ili9341 import ILI9341, rgb
from font8 import draw_text, text_width
from xpt2046 import XPT2046
import store
import net
import arcade
import advent
import battery

ASPHALT = rgb(18, 18, 28)
PANEL = rgb(28, 28, 44)
WHITE = rgb(255, 255, 255)
BLACK = rgb(0, 0, 0)
MUTED = rgb(150, 150, 170)
YELLOW = rgb(255, 210, 0)
RED = rgb(220, 40, 50)
GREEN = rgb(40, 210, 90)
CYAN = rgb(0, 210, 255)
ORANGE = rgb(255, 140, 0)
BLUE = rgb(70, 120, 255)
PINK = rgb(255, 120, 180)

# Page calendrier : rouge, creme et ardoise, comme l'affiche.
NIGHT = rgb(18, 32, 40)
MAGENTA = rgb(219, 53, 43)
INK = rgb(246, 235, 220)
LILAC = rgb(175, 160, 142)
SKY = rgb(96, 148, 182)
SUN = rgb(226, 82, 65)
GOLD = rgb(246, 235, 220)
LINE = rgb(30, 58, 72)
LIME = rgb(60, 255, 122)
ALERT = rgb(255, 68, 54)

W, H = 240, 320
TAB_H = 28
BAND_H = 22
GY, CH = 37, 31
EV_Y = 242
MOIS = ("JANV", "FEVR", "MARS", "AVRIL", "MAI", "JUIN", "JUIL", "AOUT", "SEPT", "OCT", "NOV", "DEC")
JOURS = ("L", "M", "M", "J", "V", "S", "D")
MOIS_LONG = ("JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE")
JOURS_LONG = ("LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE")
# Ecran de veille : images de veille.raw (make_veille.py) mises bout a bout.
VEILLE_W, VEILLE_H, VEILLE_N = 240, 150, 12
SAVER_IDLE = 3 * 60 * 1000
SAVER_NEXT = 30 * 1000
SAVER_DARK = 10 * 60 * 1000
BIG_X, BIG_Y = 20, 180
THEMES = (
    ("anniv", "ANNIV"),
    ("event", "EVENT"),
    ("oubli", "OUBLI"),
    ("rappel", "RAPPEL"),
    ("tache", "TACHE"),
)

AZ = ("AZERTYUIOP", "QSDFGHJKLM", "WXCVBN'-./")
NUM = ("1234567890", "@#&_+*=!?%", "$()[]:;,<>")


def leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def dim(y, m):
    if m == 2:
        return 29 if leap(y) else 28
    return (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[m]


def dow_mon(y, m, d):
    t = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    yy = y - (1 if m < 3 else 0)
    sun = (yy + yy // 4 - yy // 100 + yy // 400 + t[m - 1] + d) % 7
    return (sun + 6) % 7


def now():
    t = time.localtime()
    return t[0], t[1], t[2], t[3], t[4], t[5]


def auto_boots():
    """Redemarrages automatiques recents (memoire RTC, perdue si la carte s'eteint)."""
    import machine

    m = machine.RTC().memory()
    try:
        return int(m[4:]) if m[:4] == b"auto" else 0
    except ValueError:
        return 0


def reboot():
    """Redemarre sans attendre START ; renonce apres 3 essais pour ne pas boucler."""
    import machine

    n = auto_boots() + 1
    if n > 3:
        return
    machine.RTC().memory(("auto%d" % n).encode())
    machine.reset()


def wifi_tag():
    """Redemarrage demande par l'ecran Wi-Fi : b"wscan" (chercher) ou b"wjoin" (rejoindre)."""
    import machine

    m = machine.RTC().memory()
    if m in (b"wscan", b"wjoin"):
        machine.RTC().memory(b"")
        return m
    return None


def set_rtc(y, m, d, hh, mm, ss):
    import machine

    if m < 1:
        m = 1
    if m > 12:
        m = 12
    if d < 1:
        d = 1
    md = dim(y, m)
    if d > md:
        d = md
    machine.RTC().datetime((y, m, d, 0, hh % 24, mm % 60, ss % 60, 0))


_ACC = {
    "àâä": "a", "éèêë": "e", "îï": "i", "ôö": "o", "ùûü": "u", "ç": "c", "ÿ": "y",
    "ÀÂÄ": "A", "ÉÈÊË": "E", "ÎÏ": "I", "ÔÖ": "O", "ÙÛÜ": "U", "Ç": "C",
}


def ascii_fold(s):
    out = ""
    for c in s or "":
        o = ord(c)
        if 32 <= o <= 126:
            out += c
            continue
        rep = "?"
        for group in _ACC:
            if c in group:
                rep = _ACC[group]
                break
        out += rep
    return out


def icon(tft, kind, x, y):
    if kind == "anniv":
        tft.fill_rect(x + 1, y, 8, 5, RED)
        tft.fill_rect(x + 3, y + 5, 4, 4, PINK)
        tft.fill_rect(x + 2, y + 1, 2, 2, WHITE)
    elif kind == "event":
        tft.fill_rect(x + 1, y, 2, 9, WHITE)
        tft.fill_rect(x + 3, y, 6, 5, GREEN)
    elif kind == "oubli":
        tft.fill_rect(x + 3, y, 4, 4, YELLOW)
        tft.fill_rect(x + 1, y + 3, 8, 6, YELLOW)
        tft.fill_rect(x + 4, y + 2, 2, 2, BLACK)
    elif kind == "rappel":
        tft.fill_rect(x + 3, y, 4, 2, YELLOW)
        tft.fill_rect(x + 2, y + 2, 6, 5, CYAN)
        tft.fill_rect(x + 4, y + 7, 2, 2, WHITE)
    else:
        tft.fill_rect(x, y, 10, 10, ORANGE)
        tft.fill_rect(x + 2, y + 4, 6, 2, WHITE)


# Index dans les planches wx*.raw (ordre de meteo_icones.png, voir make_wx.py).
WX_SUN, WX_MIX, WX_CLOUD, WX_RAIN, WX_STORM, WX_SNOW = 0, 1, 2, 3, 4, 5
WX_FOG, WX_WIND, WX_NIGHT, WX_HOT, WX_GALE, WX_SHOWER = 6, 7, 8, 9, 10, 11
WX_TXT = (
    "CIEL CLAIR", "PEU NUAGEUX", "NUAGEUX", "PLUIE", "ORAGE", "NEIGE",
    "BROUILLARD", "VENT FORT", "NUIT CLAIRE", "CANICULE", "TEMPETE", "AVERSES",
)

def wkind(code, gust=None, temp=None, night=False):
    code = int(code or 0)
    gust = gust or 0
    if gust >= 90:
        return WX_GALE
    if code >= 95:
        return WX_STORM
    if code in (71, 73, 75, 77, 85, 86):
        return WX_SNOW
    if code in (80, 81) and not night:
        return WX_SHOWER
    if code >= 51:
        return WX_RAIN
    if code in (45, 48):
        return WX_FOG
    if gust >= 60:
        return WX_WIND
    if temp is not None and temp >= 35:
        return WX_HOT
    if night and code <= 2:
        return WX_NIGHT
    if code == 0:
        return WX_SUN
    if code <= 2:
        return WX_MIX
    return WX_CLOUD


def wicon(t, kind, x, y, sheet="p", n=18):
    # Par tranches de 1 Ko au plus : le tas morcele n'a souvent plus 8 Ko d'un bloc.
    row = n * 2
    buf = bytearray(row * min(n, 1024 // row))
    try:
        with open("wx%s%d.raw" % (sheet, n), "rb") as f:
            f.seek(kind * row * n)
            j = 0
            while j < n:
                k = min(f.readinto(buf) // row, n - j)
                if k <= 0:
                    break
                t.blit(buf, x, y + j, n, k)
                j += k
    except OSError:
        pass


JOURS3 = ("LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM")


class App:
    def __init__(self):
        spi = boardio.spi
        if spi is None:
            spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
        self.tft = ILI9341(spi, cs=15, dc=2, bl=21, rotation=0)
        self.bat = battery.Battery(self.tft.bl)
        self.touch = XPT2046()
        self.cfg = store.load_config()
        self.touch.write_cal(self.cfg.get("touch"))
        self.notes = store.load_notes()
        y, m, d, hh, mm, ss = now()
        self.vy, self.vm = y, m
        self.sel = (y, m, d)
        self.mode = "cal"
        self.weather = None
        self.advent_day = None
        self._events = []
        self.status = ""
        self.press = False
        self.idle_at = time.ticks_ms()
        self.saver_from = "cal"
        self.clock = ""
        self.edit_buf = ""
        self.edit_theme = "anniv"
        self.edit_for = None
        self.note_kind = None
        self.kbd_num = False
        self.kbd_low = True
        self.kbd_target = ""
        self.cities = []
        self.nets = []
        self.wifi_page = 0
        self.wremember = True
        self.msg = ""
        self._tz_dirty = False
        self.hold_key = None
        self.hold_rep = False
        self.hold_at = 0
        self.wx_at = time.ticks_ms()
        self.errs = []
        self.boots = auto_boots()
        self.started = time.ticks_ms()
        self.wifi_boot = wifi_tag()
        self.sync_joined()

    def sync_joined(self):
        """boot.py a pu rejoindre un autre reseau connu que celui des reglages."""
        cur = net.connected_ssid()
        if not cur:
            return
        pw = self.cfg["password"] if cur == self.cfg["ssid"] else store.known_password(self.cfg, cur)
        if pw is None:
            return
        self.cfg["ssid"] = cur
        self.cfg["password"] = pw
        if (self.cfg.get("known") or [None])[0] != [cur, pw]:
            store.remember_wifi(self.cfg, cur, pw)
            store.save_config(self.cfg)

    def online(self):
        """Reseau des reglages, sinon un autre reseau connu en vue (comme boot.py)."""
        if net.connected_ssid():
            return True
        cands = [(self.cfg.get("ssid") or "", self.cfg.get("password") or "")]
        cands += [(k[0], k[1]) for k in self.cfg.get("known") or [] if k[0] != cands[0][0]]
        nets = net.scan_wifi()
        if nets is None:
            return net.connect_wifi(*cands[0])
        seen = [n["ssid"] for n in nets]
        for ssid, pw in cands:
            if ssid in seen and net.connect_wifi(ssid, pw, 15, True):
                self.sync_joined()
                return True
        if not any(c[0] in seen for c in cands):
            net.last_status = 201
        return False

    def online_sync(self):
        self.flush_tz()
        self.msg = "WIFI..."
        self._banner()
        ok = self.online()
        if not ok:
            self.msg = net.status_text(net.last_status)
            self.status = "wifi"
            return False
        try:
            net.sync_ntp(int(self.cfg.get("tz") or 0))
            y, m, d, hh, mm, ss = now()
            self.vy, self.vm = y, m
            self.sel = (y, m, d)
            self.msg = "HEURE OK"
        except Exception:
            self.msg = "NTP KO"
        ntp = self.msg
        if not self.pull_weather() and ntp == "HEURE OK":
            self.msg = "HEURE OK / METEO KO"
        self.status = ""
        return True

    def _banner(self):
        self.tft.fill_rect(0, 0, W, 16, MAGENTA)
        draw_text(self.tft, self.msg[:26], 4, 4, INK, None, 1)

    def tabs(self):
        labels = (("CAL", "cal"), ("METEO", "meteo"), ("JEU", "game"), ("REGL", "set"))
        y = H - TAB_H
        self.tft.fill_rect(0, y, W, TAB_H, BLACK)
        for i, (lab, mode) in enumerate(labels):
            x = i * 60
            bg = MAGENTA if self.mode == mode else rgb(14, 42, 54)
            fg = INK
            self.tft.fill_rect(x + 1, y + 2, 58, TAB_H - 4, bg)
            draw_text(self.tft, lab, x + 8, y + 10, fg, bg)

    def hit_tab(self, x, y):
        if y < H - TAB_H:
            return None
        return ("cal", "meteo", "game", "set")[min(3, x // 60)]

    def draw_cal(self):
        t = self.tft
        t.fill(NIGHT)
        y, m, d, hh, mm, ss = now()
        today = (y, m, d)
        t.fill_rect(0, 0, W, BAND_H, MAGENTA)
        draw_text(t, "<", 6, 7, WHITE, MAGENTA)
        draw_text(t, "%s %d" % (MOIS[self.vm - 1], self.vy), 26, 7, WHITE, MAGENTA)
        draw_text(t, ">", 112, 7, WHITE, MAGENTA)
        for i, j in enumerate(JOURS):
            draw_text(t, j, i * 34 + 13, 26, SUN if i >= 5 else SKY, NIGHT)
        first = dow_mon(self.vy, self.vm, 1)
        rec = arcade.load_rec() if self.vm == 12 else None
        fc = {}
        if self.weather:
            for row in self.weather.get("days") or []:
                fc[row[0]] = wkind(row[1], row[5], row[2])
        for day in range(1, dim(self.vy, self.vm) + 1):
            idx = first + day - 1
            x = (idx % 7) * 34
            yy = GY + (idx // 7) * CH
            key = store.day_key(self.vy, self.vm, day)
            s = str(day)
            sx = x + 17 - len(s) * 4
            if today == (self.vy, self.vm, day):
                t.fill_rect(x + 6, yy + 1, 22, 10, SKY)
                draw_text(t, s, sx, yy + 2, NIGHT, SKY)
            else:
                draw_text(t, s, sx, yy + 2, LILAC if idx % 7 >= 5 else INK, NIGHT)
            gift = rec is not None and day <= 25 and advent.unlocked(rec, day, today)
            wk = fc.get(key)
            if wk is not None:
                wicon(t, wk, x + (4 if gift else 8), yy + 11, "n")
            if gift:
                g = advent.mini(NIGHT)
                t.blit(g[0], x + 23, yy + 19, g[1], g[2])
            if key in self.notes:
                t.fill_rect(x + 29, yy + 2, 3, 3, GOLD)
            if self.sel == (self.vy, self.vm, day):
                t.rect(x + 1, yy, 32, CH - 1, GOLD)
        self.draw_events(today)
        self._clock_band(hh, mm, ss)
        self.tabs()

    def draw_events(self, today):
        t = self.tft
        t.fill_rect(6, 225, W - 12, 2, LINE)
        draw_text(t, "A VENIR", 6, 231, GOLD, NIGHT)
        if self.weather and self.weather.get("temp") is not None:
            wt = "%s %dC" % (ascii_fold(self.cfg.get("city") or "").upper()[:12], int(self.weather["temp"]))
            draw_text(t, wt, W - 6 - text_width(wt), 231, SKY, NIGHT)
        start = store.day_key(*today)
        self._events = sorted(k for k in self.notes if k >= start)[:3]
        if not self._events:
            draw_text(t, "RIEN DE PREVU", 6, EV_Y, MUTED, NIGHT)
        for i, k in enumerate(self._events):
            yy = EV_Y + i * 12
            note = self.notes[k]
            draw_text(t, "%s/%s" % (k[8:10], k[5:7]), 6, yy, SKY, NIGHT)
            icon(t, note.get("t") or "tache", 50, yy - 1)
            draw_text(t, ascii_fold(note.get("txt") or "").upper()[:20], 66, yy, INK, NIGHT)

    def countdown_text(self):
        y, m, d = now()[:3]
        if m == 12:
            return "PORTE %d OUVERTE !" % d if d <= 25 else ""
        left = (time.mktime((y, 12, 1, 0, 0, 0, 0, 0)) - time.mktime((y, m, d, 0, 0, 0, 0, 0))) // 86400
        return "J-%d AVANT LA PORTE 1" % left

    def countdown(self, on):
        t = self.tft
        t.fill_rect(0, 280, W, 8, NIGHT)
        s = self.countdown_text()
        if on and s:
            draw_text(t, s, (W - text_width(s)) // 2, 280, LIME, NIGHT)

    def draw_battery(self, frame, top=4, bg=MAGENTA):
        t = self.tft
        b = self.bat
        t.fill_rect(174, top, 62, 14, bg)
        if b.pct is None:
            if b.usb:
                draw_text(t, "USB", W - 6 - 24, top + 3, LIME, bg)
            return
        x, y = W - 6 - 17, top + 2
        t.rect(x, y, 15, 9, WHITE)
        t.fill_rect(x + 15, y + 2, 2, 5, WHITE)
        t.fill_rect(x + 1, y + 1, 13, 7, NIGHT)
        w = (11 * b.pct + 50) // 100
        if b.usb:
            col = LIME
            if b.pct < 100:
                w += (11 - w) * frame // 3
        else:
            col = LIME if b.pct >= 50 else (GOLD if b.pct >= 20 else ALERT)
        if w:
            t.fill_rect(x + 2, y + 2, w, 5, col)
        s = "%d%%" % b.pct
        draw_text(t, s, x - 8 - text_width(s), top + 3, LIME if b.usb else (WHITE if b.pct >= 20 else ALERT), bg)

    def _clock_band(self, hh, mm, ss):
        self.clock = "%02d%s%02d" % (hh, " " if ss & 1 else ":", mm)
        draw_text(self.tft, self.clock, 130, 7, WHITE, MAGENTA)
        self.draw_battery(ss & 3)
        self.countdown(not ss & 1)

    def tick_clock(self):
        if self.mode != "cal":
            return
        y, m, d, hh, mm, ss = now()
        if "%02d%s%02d" % (hh, " " if ss & 1 else ":", mm) != self.clock:
            self._clock_band(hh, mm, ss)
            if (y, m, d) != self.advent_day:
                self.check_advent()

    def start_saver(self):
        self.saver_from = self.mode
        self.mode = "saver"
        self.saver_at = time.ticks_ms()
        self.saver_img = time.ticks_ms() % VEILLE_N
        self.draw_saver()

    def draw_saver(self):
        t = self.tft
        t.fill(NIGHT)
        for i, c in enumerate(arcade.BANDS):
            t.fill_rect(0, VEILLE_H + 2 + i * 3, W, 3, rgb(*c))
        self.saver_dark = False
        self.saver_min = None
        self.saver_sec = -1
        self.saver_image()

    def saver_image(self):
        self.saver_next = time.ticks_ms()
        row = VEILLE_W * 2
        try:
            f = open("veille.raw", "rb")
        except OSError:
            return
        f.seek(self.saver_img * row * VEILLE_H)
        buf = bytearray(row * 4)
        y = 0
        while y < VEILLE_H:
            n = min(f.readinto(buf) // row, VEILLE_H - y)
            if n <= 0:
                break
            self.tft.blit(buf, 0, y, VEILLE_W, n)
            y += n
        f.close()
        self.saver_img = (self.saver_img + 1) % VEILLE_N

    def saver_tick(self):
        t = self.tft
        if self.saver_dark:
            if self.bat.usb:
                t.bl(1)
                self.saver_at = time.ticks_ms()
                self.draw_saver()
            return
        ms = time.ticks_ms()
        if not self.bat.usb and time.ticks_diff(ms, self.saver_at) > SAVER_DARK:
            t.bl(0)
            self.bat.settle()
            self.saver_dark = True
            return
        if time.ticks_diff(ms, self.saver_next) >= SAVER_NEXT:
            self.saver_image()
        y, m, d, hh, mm, ss = now()
        if ss == self.saver_sec:
            return
        self.saver_sec = ss
        if (y, m, d, hh, mm) != self.saver_min:
            self.saver_min = (y, m, d, hh, mm)
            self.saver_text(y, m, d, hh, mm)
        self.big_colon(not ss & 1)
        self.draw_battery(ss & 3, 296, NIGHT)

    def saver_text(self, y, m, d, hh, mm):
        t = self.tft
        t.fill_rect(0, BIG_Y, W, 104, NIGHT)
        s = "%02d:%02d" % (hh, mm)
        draw_text(t, s, BIG_X + 3, BIG_Y + 3, MAGENTA, None, 5)
        draw_text(t, s, BIG_X, BIG_Y, GOLD, None, 5)
        s = "%s %d %s" % (JOURS_LONG[time.localtime()[6]], d, MOIS_LONG[m - 1])
        draw_text(t, s, (W - text_width(s)) // 2, 234, INK, NIGHT)
        nxt = sorted(k for k in self.notes if k >= store.day_key(y, m, d))[:1]
        if nxt:
            k = nxt[0]
            s = "%s/%s %s" % (k[8:10], k[5:7], ascii_fold(self.notes[k].get("txt") or "").upper()[:20])
            draw_text(t, s, (W - text_width(s)) // 2, 252, SKY, NIGHT)
        s = self.countdown_text()
        if s:
            draw_text(t, s, (W - text_width(s)) // 2, 268, LIME, NIGHT)
        t.fill_rect(0, 296, 172, 14, NIGHT)
        if self.weather and self.weather.get("temp") is not None:
            s = "%s %dC" % (ascii_fold(self.cfg.get("city") or "").upper()[:12], int(self.weather["temp"]))
            draw_text(t, s, 6, 299, SKY, NIGHT)

    def big_colon(self, on):
        t = self.tft
        x = BIG_X + 80
        t.fill_rect(x, BIG_Y, 40, 43, NIGHT)
        if on:
            draw_text(t, ":", x + 3, BIG_Y + 3, MAGENTA, None, 5)
            draw_text(t, ":", x, BIG_Y, GOLD, None, 5)

    def stop_saver(self):
        self.tft.bl(1)
        self.mode = self.saver_from
        self.show()
        if self.mode == "cal":
            self.check_advent()

    def shift_month(self, delta):
        m = self.vm + delta
        y = self.vy
        if m < 1:
            m, y = 12, y - 1
        elif m > 12:
            m, y = 1, y + 1
        self.vy, self.vm = y, m
        sd = self.sel[2]
        if sd > dim(y, m):
            sd = dim(y, m)
        self.sel = (y, m, sd)
        self.draw_cal()

    def open_note(self):
        key = store.day_key(*self.sel)
        note = self.notes.get(key) or {}
        self.edit_for = key
        self.edit_buf = note.get("txt") or ""
        self.edit_theme = note.get("t") or "anniv"
        self.kbd_num = False
        self.mode = "note"
        self.draw_note()

    def draw_note(self):
        t = self.tft
        t.fill(ASPHALT)
        y, m, d = self.sel
        draw_text(t, "%02d %s %d" % (d, MOIS[m - 1], y), 4, 2, YELLOW, None, 1)
        for i, (tid, lab) in enumerate(THEMES):
            x = i * 48
            bg = YELLOW if tid == self.edit_theme else PANEL
            t.fill_rect(x + 1, 14, 46, 36, bg)
            icon(t, tid, x + 18, 16)
            draw_text(t, lab[:4], x + 6, 36, BLACK if tid == self.edit_theme else WHITE, None, 1)
        t.fill_rect(4, 54, 232, 16, BLACK)
        shown = self.edit_buf[-26:]
        draw_text(t, shown, 6, 58, WHITE, None, 1)
        self.draw_kbd(74)
        self.draw_note_wx(166)
        t.fill_rect(4, H - 26, 70, 22, RED)
        t.fill_rect(80, H - 26, 70, 22, PANEL)
        t.fill_rect(156, H - 26, 80, 22, GREEN)
        draw_text(t, "VIDE", 16, H - 20, WHITE, None, 1)
        draw_text(t, "ABC" if self.kbd_num else "123", 96, H - 20, WHITE, None, 1)
        draw_text(t, "OK", 184, H - 20, BLACK, None, 1)

    def draw_note_wx(self, y):
        """Meteo du jour de la note, ou d'aujourd'hui si ce jour sort des 7 jours de previsions."""
        t = self.tft
        t.fill_rect(6, y, W - 12, 2, LINE)
        today = store.day_key(*now()[:3])
        row = None
        for r in (self.weather or {}).get("days") or []:
            if r[0] == self.edit_for:
                row = r
                break
            if r[0] == today:
                row = r
        self.note_kind = None
        # Fond ASPHALT donne : chaque texte part en une seule image (sinon ~20 ms par lettre).
        if row is None:
            draw_text(t, "METEO : PAS DE PREVISIONS", 20, y + 50, MUTED, ASPHALT)
            return
        date, code, hi, lo, mf, gust, hum, rise, sset = row
        if date == today:
            title = "METEO AUJOURD'HUI"
        else:
            yy, mm, dd = int(date[0:4]), int(date[5:7]), int(date[8:10])
            title = "METEO %s %02d %s" % (JOURS3[dow_mon(yy, mm, dd)], dd, MOIS[mm - 1])
        draw_text(t, title, 8, y + 8, GOLD, ASPHALT)
        city = ascii_fold(self.cfg.get("city") or "").upper()[:10]
        draw_text(t, city, W - 8 - text_width(city), y + 8, MUTED, ASPHALT)
        kind = self.note_kind = wkind(code, gust, hi)
        wicon(t, kind, 8, y + 22, "a", 64)
        draw_text(t, WX_TXT[kind], 84, y + 24, WHITE, ASPHALT)
        draw_text(t, "MAX", 84, y + 42, MUTED, ASPHALT)
        draw_text(t, "--" if hi is None else "%dC" % round(hi), 116, y + 38, ORANGE, None, 2)
        draw_text(t, "MIN", 84, y + 62, MUTED, ASPHALT)
        draw_text(t, "--" if lo is None else "%dC" % round(lo), 116, y + 58, CYAN, None, 2)
        draw_text(t, "HUMIDITE", 84, y + 80, MUTED, ASPHALT)
        draw_text(t, "--" if hum is None else "%d%%" % round(hum), 156, y + 80, WHITE, ASPHALT)
        draw_text(t, "LEVER", 8, y + 98, MUTED, ASPHALT)
        draw_text(t, rise or "--:--", 56, y + 98, SUN, ASPHALT)
        draw_text(t, "COUCHER", 120, y + 98, MUTED, ASPHALT)
        draw_text(t, sset or "--:--", 184, y + 98, LILAC, ASPHALT)

    def draw_kbd(self, y0):
        self._kbd_y0 = y0
        rows = NUM if self.kbd_num else AZ
        self._keys = []
        for r, row in enumerate(rows):
            if not row:
                continue
            if self.kbd_low and not self.kbd_num:
                row = row.lower()
            n = len(row)
            kw = W // n
            for i, ch in enumerate(row):
                x = i * kw
                y = y0 + r * 22
                self.tft.fill_rect(x + 1, y, kw - 2, 20, PANEL)
                lab = "SP" if ch == " " else ch
                draw_text(self.tft, lab, x + 4, y + 6, WHITE, None, 1)
                self._keys.append((ch, x, y, kw, 22))
        y = y0 + 66
        self.tft.fill_rect(4, y, 70, 22, ORANGE)
        self.tft.fill_rect(78, y, 84, 22, PANEL)
        draw_text(self.tft, "EFF", 22, y + 6, BLACK, None, 1)
        draw_text(self.tft, "ESPACE", 90, y + 6, WHITE, None, 1)
        self._keys.append(("BS", 4, y, 70, 22))
        self._keys.append((" ", 78, y, 84, 22))
        if not self.kbd_num:
            self.tft.fill_rect(166, y, 70, 22, CYAN if self.kbd_low else YELLOW)
            draw_text(self.tft, "abc" if self.kbd_low else "MAJ", 186, y + 6, BLACK, None, 1)
            self._keys.append(("SH", 166, y, 70, 22))

    def kbd_hit(self, x, y):
        for ch, kx, ky, kw, kh in self._keys:
            if kx <= x < kx + kw and ky <= y < ky + kh:
                if ch == "SH":
                    self.kbd_low = not self.kbd_low
                    self.tft.fill_rect(0, self._kbd_y0, W, 88, ASPHALT)
                    self.draw_kbd(self._kbd_y0)
                    return None
                return ch
        return None

    def apply_key(self, ch):
        if ch == "BS":
            self.edit_buf = self.edit_buf[:-1]
        elif len(self.edit_buf) < 60:
            self.edit_buf += ch

    def save_note(self):
        key = self.edit_for
        txt = self.edit_buf.strip()
        if not txt:
            if key in self.notes:
                del self.notes[key]
        else:
            self.notes[key] = {"t": self.edit_theme, "txt": txt}
        store.save_notes(self.notes)
        self.mode = "cal"
        self.draw_cal()

    def open_gift(self, day, note=False):
        res = advent.popup(self.tft, self.touch, day, note)
        self.press = True
        if res == "note":
            self.open_note()
            return
        if res == "play":
            advent.launch(self.tft, self.touch, day)
        self.mode = "cal"
        self.draw_cal()

    def check_advent(self):
        today = now()[:3]
        self.advent_day = today
        if self.mode != "cal" or today[0] < 2020:
            return
        rec = arcade.load_rec()
        advent.sync(rec, today)
        day = advent.due(rec, today)
        if day:
            advent.mark_seen(rec, today)
            self.open_gift(day)

    def delete_note(self):
        if self.edit_for in self.notes:
            del self.notes[self.edit_for]
            store.save_notes(self.notes)
        self.mode = "cal"
        self.draw_cal()

    def draw_meteo(self):
        t = self.tft
        t.fill(ASPHALT)
        draw_text(t, "METEO", 8, 6, YELLOW, None, 2)
        city = ascii_fold(self.cfg.get("city") or "?")
        draw_text(t, city[:16], 8, 28, WHITE, None, 1)
        kind = None
        if self.weather and self.weather.get("temp") is not None:
            w = self.weather
            temp = "%s C" % int(w["temp"])
            kind = wkind(w.get("code"), w.get("gust"), w["temp"], w.get("night"))
            desc = WX_TXT[kind]
        else:
            temp = "--"
            desc = "PAS DE DONNEES"
        draw_text(t, temp, 8, 48, CYAN, None, 2)
        draw_text(t, desc, 8, 70, WHITE, None, 1)
        if kind is not None:
            wicon(t, kind, 170, 22, "a", 64)
        t.fill_rect(8, 92, 100, 24, YELLOW)
        t.fill_rect(116, 92, 116, 24, GREEN)
        draw_text(t, "VILLE", 28, 100, BLACK, None, 1)
        draw_text(t, "ACTUALISER", 124, 100, BLACK, None, 1)
        draw_text(t, self.msg[:26], 8, 122, MUTED, None, 1)
        self._city_boxes = []
        if self.cities:
            y = 146
            for i, c in enumerate(self.cities[:4]):
                t.fill_rect(8, y, 224, 28, PANEL)
                line = ascii_fold("%s, %s" % (c["name"], c["country"]))[:24]
                draw_text(t, line, 12, y + 10, WHITE, None, 1)
                self._city_boxes.append((8, y, 224, 28, i))
                y += 32
        else:
            self.draw_week(136)
        self.tabs()

    def draw_week(self, y):
        t = self.tft
        days = (self.weather or {}).get("days") or []
        if not days:
            draw_text(t, "PAS DE PREVISIONS", 48, y + 60, MUTED, None, 1)
            return
        for row in days[:7]:
            date, code, hi, lo, mf, gust = row[:6]
            yy, mm, dd = int(date[0:4]), int(date[5:7]), int(date[8:10])
            t.fill_rect(4, y, 232, 20, PANEL)
            lab = "%s %02d" % (JOURS3[dow_mon(yy, mm, dd)], dd)
            draw_text(t, lab, 8, y + 6, WHITE, None, 1)
            wicon(t, wkind(code, gust, hi), 66, y + 1)
            if mf:
                draw_text(t, "MF", 92, y + 6, MUTED, None, 1)
            if lo is not None and hi is not None:
                draw_text(t, "%d" % round(lo), 150, y + 6, CYAN, None, 1)
                draw_text(t, "%d" % round(hi), 196, y + 6, ORANGE, None, 1)
            y += 21

    def draw_set(self):
        t = self.tft
        t.fill(ASPHALT)
        y, m, d, hh, mm, ss = now()
        rows = (
            ("HEURE", "%02d" % hh, "hh"),
            ("MIN", "%02d" % mm, "mi"),
            ("JOUR", "%02d" % d, "dd"),
            ("MOIS", "%02d" % m, "mo"),
            ("ANNEE", "%04d" % y, "yy"),
            ("FUSEAU", "%+d" % int(self.cfg.get("tz") or 0), "tz"),
            ("VOLUME", self._vol_label(), "vol"),
        )
        self._set_rows = []
        yy = 2
        for lab, val, key in rows:
            draw_text(t, lab, 4, yy + 4, MUTED, None, 1)
            draw_text(t, val, 78, yy + 4, WHITE, None, 1)
            t.fill_rect(140, yy, 40, 20, PANEL)
            t.fill_rect(186, yy, 40, 20, YELLOW)
            draw_text(t, "-", 156, yy + 6, WHITE, None, 1)
            draw_text(t, "+", 202, yy + 6, BLACK, None, 1)
            self._set_rows.append((key, 140, yy, 186))
            yy += 22
        t.fill_rect(8, yy + 2, 108, 22, CYAN)
        t.fill_rect(124, yy + 2, 108, 22, GREEN)
        draw_text(t, "SYNC NET", 16, yy + 9, BLACK, None, 1)
        draw_text(t, "WIFI", 156, yy + 9, BLACK, None, 1)
        self._sync_box = (8, yy + 2, 108, 22)
        self._wifi_box = (124, yy + 2, 108, 22)
        draw_text(t, self.msg[:26], 8, yy + 28, YELLOW, None, 1)
        ssid = ascii_fold(net.connected_ssid() or self.cfg.get("ssid") or "(pas de wifi)")
        draw_text(t, ssid[:26], 8, yy + 40, MUTED, None, 1)
        t.fill_rect(8, 210, 224, 28, CYAN)
        draw_text(t, "CLAVIER", 88, 220, BLACK, None, 1)
        self._key_box = (8, 210, 224, 28)
        t.fill_rect(8, 244, 224, 32, YELLOW)
        draw_text(t, "POINTEUR", 80, 256, BLACK, None, 1)
        self._ptr_box = (8, 244, 224, 32)
        self.tabs()

    def _vol_label(self):
        v = store.sound_level(self.cfg)
        return "MUET" if v == 0 else str(v)

    def _vol_beep(self):
        sfx = arcade.Sfx()
        sfx.tone(880, 50)
        time.sleep_ms(60)
        sfx.off()

    def arm_hold(self, key, delta):
        self.hold_key = (key, delta)
        self.hold_rep = False
        self.hold_at = time.ticks_ms()

    def tweak(self, key, delta):
        y, m, d, hh, mm, ss = now()
        if key == "hh":
            hh = (hh + delta) % 24
        elif key == "mi":
            mm = (mm + delta) % 60
        elif key == "dd":
            d += delta
        elif key == "mo":
            m += delta
        elif key == "yy":
            y += delta
        elif key == "tz":
            self.cfg["tz"] = int(self.cfg.get("tz") or 0) + delta
            if self.cfg["tz"] > 14:
                self.cfg["tz"] = 14
            elif self.cfg["tz"] < -12:
                self.cfg["tz"] = -12
            self._tz_dirty = True
            self.paint_set_vals()
            return
        if key == "vol":
            self.cfg["vol"] = store.sound_level({"vol": store.sound_level(self.cfg) + delta})
            store.save_config(self.cfg)
            self.paint_set_vals()
            self._vol_beep()
            return
        if m < 1:
            m = 12
            y -= 1
        if m > 12:
            m = 1
            y += 1
        if y < 2024:
            y = 2024
        if y > 2099:
            y = 2099
        set_rtc(y, m, d, hh, mm, ss)
        yy, mmn, dd, _, _, _ = now()
        self.vy, self.vm = yy, mmn
        self.sel = (yy, mmn, dd)
        self.paint_set_vals()

    def flush_tz(self):
        if not self._tz_dirty:
            return
        store.save_config(self.cfg)
        self._tz_dirty = False

    def paint_set_vals(self):
        y, m, d, hh, mm, ss = now()
        vals = {
            "hh": "%02d" % hh,
            "mi": "%02d" % mm,
            "dd": "%02d" % d,
            "mo": "%02d" % m,
            "yy": "%04d" % y,
            "tz": "%+d" % int(self.cfg.get("tz") or 0),
            "vol": self._vol_label(),
        }
        for key, _xm, yy, _xp in self._set_rows:
            self.tft.fill_rect(72, yy, 66, 20, ASPHALT)
            draw_text(self.tft, vals[key], 78, yy + 4, WHITE, None, 1)

    def paint_line(self, x, y, w, h, text):
        self.tft.fill_rect(x, y, w, h, BLACK)
        draw_text(self.tft, text[-26:], x + 2, y + 4, WHITE, None, 1)

    def start_clock(self, field="h"):
        self.flush_tz()
        y, m, d, hh, mm, ss = now()
        self.buf_h = "%02d%02d%02d" % (hh, mm, ss)
        self.buf_d = "%02d%02d%04d" % (d, m, y)
        self.buf_z = "%+d" % int(self.cfg.get("tz") or 0)
        self.fresh = {"h": True, "d": True, "z": True}
        self.clock_field = field
        self.kbd_num = True
        self.hold_key = None
        self.mode = "clock"
        self.draw_clock()

    def _mask(self, buf, groups, sep):
        width = 0
        for g in groups:
            width += g
        raw = (buf + ("_" * width))[:width]
        parts = []
        i = 0
        for g in groups:
            parts.append(raw[i:i + g])
            i += g
        return sep.join(parts)

    def paint_clock_fields(self):
        rows = (
            ("h", "HEURE", self._mask(self.buf_h, (2, 2, 2), ":"), 18),
            ("d", "DATE", self._mask(self.buf_d, (2, 2, 4), "/"), 40),
            ("z", "FUSEAU", self.buf_z or "_", 62),
        )
        self._clock_boxes = []
        for fid, lab, val, y in rows:
            on = fid == self.clock_field
            self.tft.fill_rect(4, y, 232, 20, YELLOW if on else PANEL)
            fg = BLACK if on else WHITE
            draw_text(self.tft, lab, 8, y + 6, fg, None, 1)
            draw_text(self.tft, val, 80, y + 6, fg, None, 1)
            self._clock_boxes.append((fid, 4, y, 232, 20))

    def draw_clock(self):
        t = self.tft
        t.fill(ASPHALT)
        draw_text(t, "SAISIE", 8, 2, YELLOW, None, 1)
        self.draw_kbd(88)
        t.fill_rect(4, H - 26, 74, 22, PANEL)
        t.fill_rect(82, H - 26, 74, 22, PANEL)
        t.fill_rect(160, H - 26, 76, 22, GREEN)
        draw_text(t, "ABC" if self.kbd_num else "123", 16, H - 20, WHITE, None, 1)
        draw_text(t, "RETOUR", 90, H - 20, WHITE, None, 1)
        draw_text(t, "OK", 184, H - 20, BLACK, None, 1)
        self.paint_clock_fields()

    def clock_msg(self, text):
        self.tft.fill_rect(96, 0, 140, 14, ASPHALT)
        draw_text(self.tft, text, 100, 2, RED, None, 1)

    def clock_key(self, ch):
        fid = self.clock_field
        if fid == "h":
            buf, lim = self.buf_h, 6
        elif fid == "d":
            buf, lim = self.buf_d, 8
        else:
            buf, lim = self.buf_z, 3
        if ch == "BS":
            buf = "" if self.fresh[fid] else buf[:-1]
            self.fresh[fid] = False
        elif fid == "z":
            if self.fresh[fid]:
                buf = ""
                self.fresh[fid] = False
            if ch in "+-" and buf in ("", "+", "-"):
                buf = ch
            elif ch.isdigit() and len(buf) < lim:
                buf += ch
            else:
                return
        elif ch.isdigit():
            if self.fresh[fid]:
                buf = ""
                self.fresh[fid] = False
            if len(buf) >= lim:
                return
            buf += ch
        else:
            return
        if fid == "h":
            self.buf_h = buf
        elif fid == "d":
            self.buf_d = buf
        else:
            self.buf_z = buf
        self.paint_clock_fields()

    def _parse_h(self, buf):
        if len(buf) not in (4, 6):
            return None
        hh = int(buf[0:2])
        mm = int(buf[2:4])
        ss = int(buf[4:6]) if len(buf) == 6 else 0
        if hh > 23 or mm > 59 or ss > 59:
            return None
        return hh, mm, ss

    def _parse_d(self, buf):
        if len(buf) != 8:
            return None
        d = int(buf[0:2])
        m = int(buf[2:4])
        y = int(buf[4:8])
        if y < 2024 or y > 2099 or m < 1 or m > 12 or d < 1 or d > dim(y, m):
            return None
        return d, m, y

    def _parse_z(self, buf):
        try:
            tz = int(buf)
        except Exception:
            return None
        if tz < -12 or tz > 14:
            return None
        return tz

    def commit_clock(self):
        y, m, d, hh, mm, ss = now()
        if not self.fresh["h"]:
            got = self._parse_h(self.buf_h)
            if not got:
                self.clock_msg("HEURE KO")
                return
            hh, mm, ss = got
        if not self.fresh["d"]:
            got = self._parse_d(self.buf_d)
            if not got:
                self.clock_msg("DATE KO")
                return
            d, m, y = got
        if not self.fresh["z"]:
            got = self._parse_z(self.buf_z)
            if got is None:
                self.clock_msg("FUSEAU KO")
                return
            self.cfg["tz"] = got
            self._tz_dirty = True
        set_rtc(y, m, d, hh, mm, ss)
        self.flush_tz()
        yy, mmn, dd, _, _, _ = now()
        self.vy, self.vm = yy, mmn
        self.sel = (yy, mmn, dd)
        self.msg = "HEURE OK"
        self.mode = "set"
        self.draw_set()

    def draw_wifi(self):
        t = self.tft
        t.fill(ASPHALT)
        n = len(self.nets)
        draw_text(t, "WIFI", 8, 6, YELLOW, None, 1)
        draw_text(t, "%d RESEAUX" % n if n else "AUCUN RESEAU", 72, 6, MUTED, None, 1)
        per = 7
        start = self.wifi_page * per
        chunk = self.nets[start:start + per]
        self._wifi_rows = []
        y = 28
        if not chunk:
            draw_text(t, "APPUIE SUR SCAN", 32, 120, WHITE, None, 1)
        for netw in chunk:
            t.fill_rect(4, y, 232, 32, PANEL)
            draw_text(t, ascii_fold(netw["ssid"])[:16], 8, y + 12, WHITE, None, 1)
            if store.known_password(self.cfg, netw["ssid"]) is not None:
                mark, col = "CONNU", CYAN
            elif netw.get("open"):
                mark, col = "LIBRE", GREEN
            else:
                mark, col = "CLE", YELLOW
            draw_text(t, mark, 176, y + 12, col, None, 1)
            self._wifi_rows.append((4, y, 232, 32, start))
            start += 1
            y += 36
        t.fill_rect(4, H - 30, 74, 26, PANEL)
        t.fill_rect(82, H - 30, 74, 26, CYAN)
        t.fill_rect(160, H - 30, 76, 26, PANEL)
        left = "PREC" if self.wifi_page else "RETOUR"
        right = "SUIV" if (self.wifi_page + 1) * per < n else "AUTRE"
        draw_text(t, left, 16, H - 22, WHITE, None, 1)
        draw_text(t, "SCAN", 98, H - 22, BLACK, None, 1)
        draw_text(t, right, 172, H - 22, WHITE, None, 1)

    def open_wifi(self):
        self.mode = "wifi"
        self.wifi_page = 0
        self.hold_key = None
        self.tft.fill(ASPHALT)
        draw_text(self.tft, "SCAN...", 56, 140, YELLOW, None, 2)
        nets = net.scan_wifi()
        if nets is None:
            self.restore_wifi()
            self.wifi_reboot(b"wscan")
        self.nets = nets
        self.draw_wifi()

    def wifi_reboot(self, tag):
        """Le pilote Wi-Fi n'a plus de memoire : boot.py cherche ou se connecte, puis on revient ici."""
        import machine

        t = self.tft
        t.fill(ASPHALT)
        draw_text(t, "REDEMARRAGE", 32, 120, YELLOW, None, 2)
        lines = ("MEMOIRE WIFI PLEINE,", "LA CARTE REDEMARRE",
                 "POUR CHERCHER" if tag == b"wscan" else "POUR SE CONNECTER")
        for i, s in enumerate(lines):
            draw_text(t, s, (W - text_width(s, 1)) // 2, 160 + i * 16, WHITE, None, 1)
        machine.RTC().memory(tag)
        time.sleep_ms(1500)
        machine.reset()

    def restore_wifi(self):
        """Abandon du reseau choisi : retour au dernier qui a fonctionne."""
        known = self.cfg.get("known") or []
        ssid, pw = known[0] if known else ("", "")
        if self.cfg.get("ssid") != ssid or self.cfg.get("password") != pw:
            self.cfg["ssid"], self.cfg["password"] = ssid, pw
            store.save_config(self.cfg)

    def pick_net(self, idx):
        item = self.nets[idx]
        name = item["ssid"]
        self.wremember = True
        if item.get("open"):
            self.cfg["ssid"] = name
            self.cfg["password"] = ""
            self.finish_wifi()
            return
        self.cfg["ssid"] = name
        self.cfg["password"] = store.known_password(self.cfg, name) or ""
        self.edit_buf = self.cfg["password"]
        self.kbd_num = False
        self.mode = "wpass"
        self.draw_wpass()

    def draw_wpass(self):
        t = self.tft
        t.fill(ASPHALT)
        draw_text(t, "MOT DE PASSE", 8, 4, YELLOW, None, 1)
        draw_text(t, ascii_fold(self.cfg.get("ssid") or "")[:26], 8, 18, CYAN, None, 1)
        t.fill_rect(8, 32, 224, 16, BLACK)
        draw_text(t, ascii_fold(self.edit_buf)[-26:], 10, 36, WHITE, None, 1)
        self.draw_kbd(54)
        self._rem_box = (8, 156, 224, 28)
        self.draw_remember()
        draw_text(t, "RECONNEXION AUTO SI EN VUE", 16, 192, MUTED, None, 1)
        t.fill_rect(4, H - 26, 74, 22, PANEL)
        t.fill_rect(82, H - 26, 74, 22, PANEL)
        t.fill_rect(160, H - 26, 76, 22, GREEN)
        draw_text(t, "RETOUR", 12, H - 20, WHITE, None, 1)
        draw_text(t, "123" if not self.kbd_num else "ABC", 98, H - 20, WHITE, None, 1)
        draw_text(t, "OK", 184, H - 20, BLACK, None, 1)

    def draw_remember(self):
        t = self.tft
        x, y, w, h = self._rem_box
        t.fill_rect(x, y, w, h, PANEL)
        t.fill_rect(x + 6, y + 6, 16, 16, WHITE)
        if self.wremember:
            t.fill_rect(x + 9, y + 9, 10, 10, GREEN)
        draw_text(t, "RETENIR LE MOT DE PASSE", x + 30, y + 10, WHITE, None, 1)

    def draw_wssid(self):
        t = self.tft
        t.fill(ASPHALT)
        draw_text(t, "NOM DU RESEAU", 8, 4, YELLOW, None, 1)
        t.fill_rect(8, 20, 224, 16, BLACK)
        draw_text(t, ascii_fold(self.edit_buf)[-26:], 10, 24, WHITE, None, 1)
        self.draw_kbd(42)
        t.fill_rect(4, H - 26, 74, 22, PANEL)
        t.fill_rect(82, H - 26, 74, 22, PANEL)
        t.fill_rect(160, H - 26, 76, 22, GREEN)
        draw_text(t, "RETOUR", 12, H - 20, WHITE, None, 1)
        draw_text(t, "123" if not self.kbd_num else "ABC", 98, H - 20, WHITE, None, 1)
        draw_text(t, "OK", 184, H - 20, BLACK, None, 1)

    def finish_wifi(self):
        self.tft.fill(ASPHALT)
        draw_text(self.tft, "CONNEXION...", 24, 130, YELLOW, None, 2)
        draw_text(self.tft, ascii_fold(self.cfg.get("ssid") or "")[:22], 8, 160, WHITE, None, 1)
        ssid = self.cfg.get("ssid") or ""
        pw = self.cfg.get("password") or ""
        if not self.wremember:
            store.forget_wifi(self.cfg, ssid)
        if net.wifi_room() < net.WIFI_ROOM:
            store.save_config(self.cfg)
            self.wifi_reboot(b"wjoin")
        ok = net.connect_wifi(ssid, pw, 20, True)
        if not ok and net.wifi_room() < net.WIFI_ROOM:
            store.save_config(self.cfg)
            self.wifi_reboot(b"wjoin")
        if not ok:
            self.wifi_failed(net.status_text(net.last_status))
            return
        if self.wremember:
            store.remember_wifi(self.cfg, ssid, pw)
            store.save_config(self.cfg)
        else:
            # Connecte pour cette fois : les reglages gardent le dernier reseau retenu.
            self.restore_wifi()
        self.online_sync()
        self.mode = "set"
        self.draw_set()

    def wifi_failed(self, why):
        self.edit_buf = self.cfg.get("password") or ""
        self.kbd_num = False
        self.mode = "wpass"
        self.draw_wpass()
        self.tft.fill_rect(0, 0, W, 14, RED)
        draw_text(self.tft, why[:29], 4, 3, WHITE, None, 1)

    def draw_city_kbd(self):
        t = self.tft
        t.fill(ASPHALT)
        draw_text(t, "VILLE / PAYS", 8, 4, YELLOW, None, 1)
        t.fill_rect(8, 20, 224, 16, BLACK)
        draw_text(t, ascii_fold(self.edit_buf)[-26:], 10, 24, WHITE, None, 1)
        self.draw_kbd(42)
        t.fill_rect(4, H - 26, 70, 22, PANEL)
        t.fill_rect(78, H - 26, 74, 22, RED)
        t.fill_rect(156, H - 26, 80, 22, GREEN)
        draw_text(t, "123" if not self.kbd_num else "ABC", 16, H - 20, WHITE, None, 1)
        draw_text(t, "RETOUR", 88, H - 20, WHITE, None, 1)
        draw_text(t, "CHERCHER", 160, H - 20, BLACK, None, 1)

    def search_city(self):
        self.msg = "RECHERCHE..."
        self.tft.fill(BLACK)
        draw_text(self.tft, self.msg, 8, 40, YELLOW, None, 1)
        try:
            if not self.online():
                self.msg = "WIFI KO"
                self.cities = []
            else:
                self.cities = net.search_cities(self.edit_buf)
                self.msg = "%d VILLES" % len(self.cities) if self.cities else "AUCUNE VILLE"
        except Exception:
            self.msg = "RESEAU KO"
            self.cities = []
        self.mode = "meteo"
        self.draw_meteo()

    def choose_city(self, idx):
        c = self.cities[idx]
        self.cfg["city"] = c["name"]
        self.cfg["lat"] = c["lat"]
        self.cfg["lon"] = c["lon"]
        store.save_config(self.cfg)
        self.cities = []
        self.pull_weather()
        self.draw_meteo()

    def refresh_weather(self):
        self.msg = "METEO..."
        self.draw_meteo()
        self.pull_weather()
        self.draw_meteo()

    def pull_weather(self):
        self.wx_at = time.ticks_ms()
        try:
            if not self.online():
                self.msg = net.status_text(net.last_status)
                return False
            self.weather = net.fetch_weather(self.cfg["lat"], self.cfg["lon"])
        except Exception as e:
            import sys

            sys.print_exception(e)
            self.msg = "METEO KO"
            return False
        y, m, d, hh, mm, ss = now()
        self.msg = "MAJ %02d:%02d" % (hh, mm)
        return True

    def auto_weather(self):
        if not (self.cfg.get("ssid") or net.connected_ssid()) or self.mode not in ("cal", "meteo", "saver"):
            return
        if time.ticks_diff(time.ticks_ms(), self.wx_at) < 30 * 60 * 1000:
            return
        if self.pull_weather():
            self.show()

    def show(self):
        if self.mode == "cal":
            self.draw_cal()
        elif self.mode == "note":
            self.draw_note()
        elif self.mode == "meteo":
            self.draw_meteo()
        elif self.mode == "set":
            self.draw_set()
        elif self.mode == "wifi":
            self.draw_wifi()
        elif self.mode == "city":
            self.draw_city_kbd()

    def on_tap(self, x, y):
        if self.mode in ("cal", "meteo", "set"):
            tab = self.hit_tab(x, y)
            if tab:
                if self.mode == "set":
                    self.flush_tz()
                if tab == "game":
                    advent.menu(self.tft, self.touch, now()[:3])
                    self.press = True
                    self.mode = "cal"
                    self.show()
                    return
                self.mode = tab
                self.show()
                return
        if self.mode == "cal":
            if y < BAND_H + 4:
                if x < 24:
                    self.shift_month(-1)
                elif 104 <= x < 128:
                    self.shift_month(1)
                elif x < 104:
                    yy, mm, dd, _, _, _ = now()
                    if yy >= 2020:
                        self.vy, self.vm = yy, mm
                        self.sel = (yy, mm, dd)
                        self.draw_cal()
                return
            if EV_Y - 2 <= y < EV_Y + 34:
                i = (y - EV_Y + 2) // 12
                if i < len(self._events):
                    k = self._events[i]
                    self.vy, self.vm = int(k[:4]), int(k[5:7])
                    self.sel = (self.vy, self.vm, int(k[8:10]))
                    self.open_note()
                return
            if GY <= y < GY + 6 * CH:
                col = x // 34
                row = (y - GY) // CH
                if 0 <= col < 7 and 0 <= row < 6:
                    first = dow_mon(self.vy, self.vm, 1)
                    nd = dim(self.vy, self.vm)
                    day = row * 7 + col - first + 1
                    if 1 <= day <= nd:
                        picked = (self.vy, self.vm, day)
                        if picked == self.sel:
                            if self.vm == 12 and day <= 25 and advent.unlocked(arcade.load_rec(), day, now()[:3]):
                                self.open_gift(day, True)
                            else:
                                self.open_note()
                        else:
                            self.sel = picked
                            self.draw_cal()
            return
        if self.mode == "note":
            if y < 14:
                return
            if y < 52 and y >= 14:
                self.edit_theme = THEMES[min(4, x // 48)][0]
                self.draw_note()
                return
            if y >= H - 26:
                if x < 76:
                    self.delete_note()
                elif x < 150:
                    self.kbd_num = not self.kbd_num
                    self.draw_note()
                else:
                    self.save_note()
                return
            ch = self.kbd_hit(x, y)
            if ch:
                self.apply_key(ch)
                self.paint_line(4, 54, 232, 16, self.edit_buf)
            return
        if self.mode == "meteo":
            if 92 <= y < 116:
                if x < 112:
                    self.edit_buf = ""
                    self.kbd_num = False
                    self.mode = "city"
                    self.draw_city_kbd()
                else:
                    self.refresh_weather()
                return
            for bx, by, bw, bh, idx in getattr(self, "_city_boxes", []):
                if bx <= x < bx + bw and by <= y < by + bh:
                    self.choose_city(idx)
                    return
            return
        if self.mode == "set":
            for key, xm, yy, xp in self._set_rows:
                if yy <= y < yy + 20:
                    if xm <= x < xm + 40:
                        self.arm_hold(key, -1)
                        self.tweak(key, -1)
                        return
                    if xp <= x < xp + 40:
                        self.arm_hold(key, 1)
                        self.tweak(key, 1)
                        return
                    if x < xm:
                        if key == "vol":
                            return
                        if key == "tz":
                            field = "z"
                        elif key in ("dd", "mo", "yy"):
                            field = "d"
                        else:
                            field = "h"
                        self.start_clock(field)
                        return
            sx, sy, sw, sh = self._sync_box
            if sx <= x < sx + sw and sy <= y < sy + sh:
                self.online_sync()
                self.draw_set()
                return
            wx, wy, ww, wh = self._wifi_box
            if wx <= x < wx + ww and wy <= y < wy + wh:
                self.flush_tz()
                self.open_wifi()
                return
            kx, ky, kw, kh = self._key_box
            if kx <= x < kx + kw and ky <= y < ky + kh:
                self.start_clock("h")
                return
            px, py, pw, ph = self._ptr_box
            if px <= x < px + pw and py <= y < py + ph:
                self.flush_tz()
                self.start_ptr()
            return
        if self.mode == "wifi":
            if y >= H - 30:
                per = 7
                if x < 80:
                    if self.wifi_page:
                        self.wifi_page -= 1
                        self.draw_wifi()
                    else:
                        if net.connected_ssid() != self.cfg.get("ssid"):
                            self.restore_wifi()
                        self.mode = "set"
                        self.draw_set()
                elif x < 158:
                    self.open_wifi()
                elif (self.wifi_page + 1) * per < len(self.nets):
                    self.wifi_page += 1
                    self.draw_wifi()
                else:
                    self.edit_buf = ""
                    self.kbd_num = False
                    self.mode = "wssid"
                    self.draw_wssid()
                return
            for bx, by, bw, bh, idx in self._wifi_rows:
                if bx <= x < bx + bw and by <= y < by + bh:
                    self.pick_net(idx)
                    return
            return
        if self.mode == "wpass":
            if y >= H - 26:
                if x < 80:
                    self.mode = "wifi"
                    self.draw_wifi()
                elif x < 158:
                    self.kbd_num = not self.kbd_num
                    self.draw_wpass()
                else:
                    self.cfg["password"] = self.edit_buf
                    self.finish_wifi()
                return
            rx, ry, rw, rh = self._rem_box
            if rx <= x < rx + rw and ry <= y < ry + rh:
                self.wremember = not self.wremember
                self.draw_remember()
                return
            ch = self.kbd_hit(x, y)
            if ch:
                self.apply_key(ch)
                self.cfg["password"] = self.edit_buf
                self.paint_line(8, 32, 224, 16, ascii_fold(self.edit_buf))
            return
        if self.mode == "wssid":
            if y >= H - 26:
                if x < 80:
                    self.mode = "wifi"
                    self.draw_wifi()
                elif x < 158:
                    self.kbd_num = not self.kbd_num
                    self.draw_wssid()
                else:
                    name = self.edit_buf.strip()
                    if not name:
                        return
                    self.cfg["ssid"] = name
                    self.cfg["password"] = ""
                    self.edit_buf = ""
                    self.wremember = True
                    self.kbd_num = False
                    self.mode = "wpass"
                    self.draw_wpass()
                return
            ch = self.kbd_hit(x, y)
            if ch:
                self.apply_key(ch)
                self.paint_line(8, 20, 224, 16, ascii_fold(self.edit_buf))
            return
        if self.mode == "clock":
            if y >= H - 26:
                if x < 80:
                    self.kbd_num = not self.kbd_num
                    self.draw_clock()
                elif x < 158:
                    self.mode = "set"
                    self.draw_set()
                else:
                    self.commit_clock()
                return
            for fid, bx, by, bw, bh in self._clock_boxes:
                if bx <= x < bx + bw and by <= y < by + bh:
                    self.clock_field = fid
                    self.paint_clock_fields()
                    return
            ch = self.kbd_hit(x, y)
            if ch:
                self.clock_key(ch)
            return
        if self.mode == "city":
            if y >= H - 26:
                if x < 76:
                    self.kbd_num = not self.kbd_num
                    self.draw_city_kbd()
                elif x < 154:
                    self.mode = "meteo"
                    self.draw_meteo()
                else:
                    self.search_city()
                return
            ch = self.kbd_hit(x, y)
            if ch:
                self.apply_key(ch)
                self.paint_line(8, 20, 224, 16, ascii_fold(self.edit_buf))

    PTR_XY = ((28, 28), (211, 28), (211, 291), (28, 291))
    PTR_NAME = ("HAUT GAUCHE", "HAUT DROITE", "BAS DROITE", "BAS GAUCHE")

    def start_ptr(self):
        self.mode = "ptr"
        self.ptr_step = 0
        self.ptr_pts = []
        self.ptr_backup = self.touch.read_cal()
        self.ptr_hold = ""
        self._dot = None
        self.press = True
        self.draw_ptr()

    def draw_ptr(self):
        t = self.tft
        t.fill(BLACK)
        if self.ptr_step < 4:
            name = self.PTR_NAME[self.ptr_step]
            draw_text(t, "CALIBRAGE", 64, 132, YELLOW, None, 1)
            draw_text(t, "TOUCHE LA CROIX", 48, 148, WHITE, None, 1)
            draw_text(t, name, (W - text_width(name)) // 2, 166, CYAN, None, 1)
            draw_text(t, "%d / 4" % (self.ptr_step + 1), 96, 182, MUTED, None, 1)
            cx, cy = self.PTR_XY[self.ptr_step]
            t.fill_rect(cx - 16, cy - 1, 33, 3, YELLOW)
            t.fill_rect(cx - 1, cy - 16, 3, 33, YELLOW)
            t.fill_rect(cx - 3, cy - 3, 7, 7, RED)
            return
        draw_text(t, "POINTEUR", 8, 2, YELLOW, None, 1)
        draw_text(t, "CARRE SOUS LE DOIGT", 8, 14, WHITE, None, 1)
        draw_text(t, "X%+d Y%+d" % (self.touch.x_off, self.touch.y_off), 8, 26, CYAN, None, 1)
        t.rect(6, 40, 228, 200, PANEL)
        self._ptr_btns = (
            (0, 246, 60, 32, "<", "xl", PANEL, WHITE),
            (60, 246, 60, 32, ">", "xr", PANEL, WHITE),
            (120, 246, 60, 32, "HAUT", "yu", PANEL, WHITE),
            (180, 246, 60, 32, "BAS", "yd", PANEL, WHITE),
            (0, 282, 80, 38, "OK", "ok", GREEN, BLACK),
            (80, 282, 80, 38, "RAZ", "raz", RED, WHITE),
            (160, 282, 80, 38, "RETOUR", "back", YELLOW, BLACK),
        )
        for x, y, w, h, lab, _key, bg, fg in self._ptr_btns:
            t.fill_rect(x + 2, y + 2, w - 4, h - 4, bg)
            draw_text(t, lab, x + 10, y + 12, fg, None, 1)
        self._dot = None

    def ptr_hit(self, x, y):
        for bx, by, bw, bh, _lab, key, _bg, _fg in self._ptr_btns:
            if bx <= x < bx + bw and by <= y < by + bh:
                return key
        return None

    def ptr_action(self, key):
        if key == "xl":
            self.touch.x_off -= 4
        elif key == "xr":
            self.touch.x_off += 4
        elif key == "yu":
            self.touch.y_off -= 4
        elif key == "yd":
            self.touch.y_off += 4
        elif key == "ok":
            self.cfg["touch"] = self.touch.read_cal()
            store.save_config(self.cfg)
            self.msg = "POINTEUR OK"
            self.mode = "set"
            self.draw_set()
            return
        elif key == "raz":
            self.touch.reset_cal()
        elif key == "back":
            self.touch.write_cal(self.ptr_backup)
            self.mode = "set"
            self.draw_set()
            return
        if self.touch.x_off > 80:
            self.touch.x_off = 80
        elif self.touch.x_off < -80:
            self.touch.x_off = -80
        if self.touch.y_off > 80:
            self.touch.y_off = 80
        elif self.touch.y_off < -80:
            self.touch.y_off = -80
        self.draw_ptr()

    def _ptr_dot(self, x, y):
        if not (14 <= x <= 224 and 48 <= y <= 230):
            return
        old = self._dot
        if old:
            self.tft.fill_rect(old[0] - 4, old[1] - 4, 9, 9, BLACK)
        self.tft.fill_rect(x - 3, y - 3, 7, 7, YELLOW)
        self._dot = (x, y)

    def ptr_frame(self):
        if self.ptr_step < 4:
            sample = self.touch.raw()
            if sample and not self.press:
                self.press = True
                self.ptr_pts.append((sample[0], sample[1]))
                self.ptr_step += 1
                if self.ptr_step == 4:
                    self.touch.fit_corners(self.ptr_pts)
                    print("ptr", self.touch.read_cal())
                self.draw_ptr()
            elif not sample:
                self.press = False
            return
        pt = self.touch.point()
        if pt and not self.press:
            self.press = True
            key = self.ptr_hit(pt[0], pt[1])
            if key:
                self.ptr_hold = "btn"
                self.ptr_action(key)
            else:
                self.ptr_hold = "dot"
                self._ptr_dot(pt[0], pt[1])
        elif pt and self.press and self.ptr_hold == "dot":
            self._ptr_dot(pt[0], pt[1])
        elif not pt:
            self.press = False
            self.ptr_hold = ""

    def draw_logo(self, y):
        t = self.tft
        try:
            f = open("logo.raw", "rb")
        except OSError:
            draw_text(t, "CALENDAR", 56, y + 30, INK, None, 2)
            draw_text(t, "GAME", 88, y + 56, MAGENTA, None, 2)
            return
        hd = f.read(4)
        w = (hd[0] << 8) | hd[1]
        h = (hd[2] << 8) | hd[3]
        buf = bytearray(w * 2 * 4)
        r = 0
        while r < h:
            n = f.readinto(buf) // (w * 2)
            if n <= 0:
                break
            t.blit(buf, 0, y + r, w, n)
            r += n
        f.close()

    START_BTN = (36, 188, 168, 44)

    def start_button(self, pressed=False):
        t = self.tft
        x, y, w, h = self.START_BTN
        t.fill_rect(x, y, w, h, rgb(140, 28, 22) if pressed else MAGENTA)
        t.rect(x - 1, y - 1, w + 2, h + 2, INK)
        t.rect(x - 2, y - 2, w + 4, h + 4, rgb(14, 82, 108))
        tx = x + (w - text_width("DEMARRER", 2)) // 2
        draw_text(t, "DEMARRER", tx + 2, y + 16, rgb(80, 16, 14), None, 2)
        draw_text(t, "DEMARRER", tx, y + 14, INK, None, 2)

    def splash(self):
        t = self.tft
        t.fill(rgb(236, 228, 208))
        self.draw_logo(18)
        self.msg = "CHARGEMENT..."
        self._banner()
        if self.cfg.get("ssid"):
            self.online_sync()
        else:
            self.msg = "REGLAGES > WIFI"
        self._banner()
        if self.boots or self.wifi_boot:
            return
        self.start_button()
        bx, by, bw, bh = self.START_BTN
        while True:
            pt = self.touch.point()
            if pt and bx - 8 <= pt[0] < bx + bw + 8 and by - 8 <= pt[1] < by + bh + 8:
                self.start_button(True)
                while self.touch.point():
                    time.sleep_ms(20)
                return
            time.sleep_ms(20)

    def loop(self):
        print("kartcal start")
        self.splash()
        if self.wifi_boot:
            self.nets = net.boot_nets()
            self.wifi_page = 0
        if self.wifi_boot == b"wscan":
            self.mode = "wifi"
            self.draw_wifi()
        elif self.wifi_boot == b"wjoin" and self.status == "wifi":
            self.wifi_failed(self.msg)
        elif self.wifi_boot == b"wjoin":
            self.mode = "set"
            self.draw_set()
        else:
            self.mode = "cal"
            self.draw_cal()
            self.check_advent()
        while True:
            try:
                self.step()
            except Exception as e:
                self.recover(e)
            time.sleep_ms(12)

    def step(self):
        if self.mode == "ptr":
            self.ptr_frame()
            return
        if self.boots and time.ticks_diff(time.ticks_ms(), self.started) > 10 * 60 * 1000:
            import machine

            machine.RTC().memory(b"")
            self.boots = 0
        self.bat.tick()
        self.tick_clock()
        if not self.press:
            self.auto_weather()
        if self.mode == "saver":
            self.saver_tick()
        elif self.mode in ("cal", "meteo") and time.ticks_diff(time.ticks_ms(), self.idle_at) > SAVER_IDLE:
            self.start_saver()
        pt = self.touch.point()
        if pt:
            self.idle_at = time.ticks_ms()
        if pt and not self.press:
            self.press = True
            print("touch", pt[0], pt[1])
            if self.mode == "saver":
                self.stop_saver()
            else:
                self.on_tap(pt[0], pt[1])
            # Un jeu peut durer longtemps : le delai repart a la sortie.
            self.idle_at = time.ticks_ms()
        elif pt and self.press and self.mode == "set" and self.hold_key:
            wait = 120 if self.hold_rep else 350
            if time.ticks_diff(time.ticks_ms(), self.hold_at) >= wait:
                self.hold_rep = True
                self.hold_at = time.ticks_ms()
                self.tweak(self.hold_key[0], self.hold_key[1])
        elif not pt:
            self.press = False
            self.hold_key = None

    def recover(self, e):
        """Journalise l'erreur et revient au calendrier ; 3 erreurs en 2 min : redemarrage."""
        import gc
        import sys

        sys.print_exception(e)
        store.log_error(e, self.mode)
        gc.collect()
        ms = time.ticks_ms()
        self.errs = [t for t in self.errs if time.ticks_diff(ms, t) < 2 * 60 * 1000]
        self.errs.append(ms)
        if len(self.errs) >= 3:
            reboot()
        self.tft.forget_window()
        self.tft.bl(1)
        self.press = True
        self.hold_key = None
        self.idle_at = ms
        self.mode = "cal"
        self.draw_cal()


def main():
    try:
        App().loop()
    except Exception as e:
        import gc
        import sys

        sys.print_exception(e)
        gc.collect()
        store.log_error(e, "main")
        try:
            spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
            tft = ILI9341(spi, cs=15, dc=2, bl=21)
            tft.fill(rgb(40, 0, 0))
            draw_text(tft, "ERREUR", 8, 20, rgb(255, 220, 0), None, 2)
            draw_text(tft, ascii_fold(str(e))[:26], 8, 50, rgb(255, 255, 255), None, 1)
            again = "REDEMARRAGE DANS 15 S" if auto_boots() < 3 else "APPUIE SUR RESET"
            draw_text(tft, again, 8, 80, rgb(255, 255, 255), None, 1)
        except Exception:
            pass
        time.sleep(15)
        reboot()
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
