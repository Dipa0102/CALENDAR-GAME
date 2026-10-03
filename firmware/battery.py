"""Batterie LiPo 1S sur IO34 (pont diviseur 1/2) et detection de l'USB.

La carte n'a pas de signal "USB present". Avec l'USB, le transistor Q3 isole
la batterie du reste de la carte : elle ne voit plus que le courant de charge.
- Brancher ou debrancher fait sauter sa tension d'environ 65 mV (charge ~290 mA
  contre consommation ~150 mA, resistance interne ~0,15 ohm) : c'est le critere
  principal, sens du saut compris. En fin de charge il ne reste que 20-30 mV,
  guere plus que le bruit d'une mesure : on compare des medianes de mesures.
- Au demarrage, couper le retro-eclairage (~75 mA) ne change rien sur USB et fait
  remonter la tension de quelques mV sur batterie. Le bruit de mesure est du meme
  ordre, d'ou plusieurs coupures et la mediane.
- Toutes les 5 min, la tendance sur 10 min rattrape un saut manque.
"""
import time
from array import array

from machine import ADC, Pin

# Tension a vide (mV) -> %, LiPo 1S.
CURVE = (
    (3300, 0), (3400, 1), (3500, 4), (3600, 10), (3650, 18), (3700, 30),
    (3750, 42), (3800, 52), (3900, 67), (4000, 79), (4100, 90), (4200, 100),
)
DROP_LOAD = 25
RISE_CHARGE = 45
# Mediane des 3 dernieres mesures contre celle des 5 d'avant (2 s d'ecart).
# Sur batterie, les pics de consommation (Wi-Fi) font deja ~20 mV : seuil plus haut.
STEP_UNPLUG = 12
STEP_PLUG = 30
BLIP = 4
RING = 90
TREND = 15
# Au-dessus, la tension retombe toute seule apres la fin de charge.
TREND_TOP = 4100


def percent(ocv):
    if ocv <= CURVE[0][0]:
        return 0
    for i in range(1, len(CURVE)):
        v1, p1 = CURVE[i]
        if ocv <= v1:
            v0, p0 = CURVE[i - 1]
            return p0 + (p1 - p0) * (ocv - v0) // (v1 - v0)
    return 100


def mid(vals):
    return sorted(vals)[len(vals) // 2]


last = None


class Battery:
    def __init__(self, backlight):
        global last
        last = self
        self.bl = backlight
        self.adc = ADC(Pin(34))
        self.adc.atten(ADC.ATTN_11DB)
        self.usb = False
        self.pct = None
        self.ema = 0
        self.win = []
        self.trend = []
        self.ring = array("H", [0] * RING)
        self.ri = 0
        self.at = self.trend_at = time.ticks_ms()
        self.probe()

    def settle(self):
        """A appeler quand la consommation change (retro-eclairage coupe...)."""
        self.win = []

    def read(self, n=128):
        s = 0
        for _ in range(n):
            s += self.adc.read_uv()
        return s // n // 500

    def probe(self):
        diffs = []
        for _ in range(6):
            on = self.read(256)
            self.bl(0)
            time.sleep_ms(25)
            diffs.append(self.read(256) - on)
            self.bl(1)
            time.sleep_ms(25)
        diffs.sort()
        rise = (diffs[2] + diffs[3]) // 2
        self._set(rise < BLIP, self.read(), "sonde %+d" % rise)

    def _set(self, usb, mv, why, keep=None):
        with open("batprobe.txt", "a") as f:
            f.write("%d %d %s %s %s\n" % (time.time(), mv, "USB" if usb else "BATT",
                                          why, self.win))
        if usb != self.usb:
            self.pct = None
        self.usb = usb
        self.win = keep or [mv]
        self.trend = [mv]
        self.trend_at = time.ticks_ms()
        self.ema = mid(self.win)
        self._update()

    def _update(self):
        mv = self.ema
        if mv < 2500:
            self.pct = None
        elif self.usb:
            rise = RISE_CHARGE if mv < 4150 else RISE_CHARGE * max(0, 4200 - mv) // 50
            p = percent(mv - rise)
            self.pct = p if self.pct is None else max(self.pct, p)
        else:
            p = percent(mv + DROP_LOAD)
            self.pct = p if self.pct is None else min(self.pct, p)

    def tick(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.at) < 2000:
            return
        self.at = now
        mv = self.read()
        self.ring[self.ri % RING] = mv
        self.ri += 1
        w = self.win = (self.win + [mv])[-8:]
        if len(w) == 8:
            d = mid(w[5:]) - mid(w[:5])
            if self.usb and d <= -STEP_UNPLUG:
                self._set(False, mv, "chute %d" % d, w[5:])
                return
            if not self.usb and d >= STEP_PLUG:
                self._set(True, mv, "saut %+d" % d, w[5:])
                return
        self.ema = (self.ema * 7 + mv) // 8
        if time.ticks_diff(now, self.trend_at) >= 300000:
            self.trend_at = now
            self.trend = (self.trend + [self.ema])[-3:]
            d = self.ema - self.trend[0]
            if self.usb and d <= -TREND and self.ema < TREND_TOP:
                self._set(False, self.ema, "baisse %d" % d)
                return
            if not self.usb and d >= TREND:
                self._set(True, self.ema, "hausse %+d" % d)
                return
        self._update()
