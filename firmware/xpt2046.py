"""XPT2046 — lecture par pression, sans la broche IRQ (GPIO36, entree seule)."""

from machine import Pin, SoftSPI


class XPT2046:
    def __init__(self, sck=25, mosi=32, miso=39, cs=33):
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.spi = SoftSPI(
            baudrate=250000,
            polarity=0,
            phase=0,
            sck=Pin(sck),
            mosi=Pin(mosi),
            miso=Pin(miso),
        )
        self.x_min, self.x_max = 280, 3850
        self.y_min, self.y_max = 280, 3850
        self.swap_xy = False
        self.invert_x = True
        self.invert_y = False
        self.x_off = 0
        self.y_off = 0
        self.width = 240
        self.height = 320
        self.z_min = 80

    def _xfer(self, cmd):
        buf = bytearray((cmd, 0, 0))
        self.cs(0)
        self.spi.write_readinto(buf, buf)
        self.cs(1)
        return ((buf[1] << 8) | buf[2]) >> 3

    def raw(self):
        z = self._xfer(0xB0)
        if z < self.z_min:
            return None
        xs = [self._xfer(0xD0) for _ in range(3)]
        ys = [self._xfer(0x90) for _ in range(3)]
        xs.sort()
        ys.sort()
        x, y = xs[1], ys[1]
        if x < 40 or x > 4050 or y < 40 or y > 4050:
            return None
        if self._xfer(0xB0) < self.z_min:
            return None
        return x, y, z

    def point(self):
        r = self.raw()
        if r is None:
            return None
        rx, ry, z = r
        if self.swap_xy:
            rx, ry = ry, rx
        span_x = self.x_max - self.x_min
        span_y = self.y_max - self.y_min
        if span_x <= 0 or span_y <= 0:
            return None
        x = (rx - self.x_min) * self.width // span_x
        y = (ry - self.y_min) * self.height // span_y
        if self.invert_x:
            x = self.width - 1 - x
        if self.invert_y:
            y = self.height - 1 - y
        x += self.x_off
        y += self.y_off
        if x < 0:
            x = 0
        elif x >= self.width:
            x = self.width - 1
        if y < 0:
            y = 0
        elif y >= self.height:
            y = self.height - 1
        return x, y

    def read_cal(self):
        return {
            "x_min": int(self.x_min),
            "x_max": int(self.x_max),
            "y_min": int(self.y_min),
            "y_max": int(self.y_max),
            "swap_xy": bool(self.swap_xy),
            "invert_x": bool(self.invert_x),
            "invert_y": bool(self.invert_y),
            "x_off": int(self.x_off),
            "y_off": int(self.y_off),
        }

    def write_cal(self, c):
        if not isinstance(c, dict):
            return
        try:
            self.x_min = int(c.get("x_min", self.x_min))
            self.x_max = int(c.get("x_max", self.x_max))
            self.y_min = int(c.get("y_min", self.y_min))
            self.y_max = int(c.get("y_max", self.y_max))
            self.swap_xy = bool(c.get("swap_xy", self.swap_xy))
            self.invert_x = bool(c.get("invert_x", self.invert_x))
            self.invert_y = bool(c.get("invert_y", self.invert_y))
            self.x_off = int(c.get("x_off", 0))
            self.y_off = int(c.get("y_off", 0))
        except Exception:
            return
        if self.x_max - self.x_min < 200 or self.y_max - self.y_min < 200:
            self.reset_cal()

    def reset_cal(self):
        self.x_min, self.x_max = 280, 3850
        self.y_min, self.y_max = 280, 3850
        self.swap_xy = False
        self.invert_x = True
        self.invert_y = False
        self.x_off = 0
        self.y_off = 0

    def fit_corners(self, pts):
        """pts : haut-gauche, haut-droite, bas-droite, bas-gauche, en brut."""
        tl, tr, br, bl = pts
        hx = ((tr[0] - tl[0]) + (br[0] - bl[0])) // 2
        hy = ((tr[1] - tl[1]) + (br[1] - bl[1])) // 2
        vx = ((bl[0] - tl[0]) + (br[0] - tr[0])) // 2
        vy = ((bl[1] - tl[1]) + (br[1] - tr[1])) // 2
        swap = abs(hy) + abs(vx) > abs(hx) + abs(vy)
        if swap:
            tl, tr, br, bl = (tl[1], tl[0]), (tr[1], tr[0]), (br[1], br[0]), (bl[1], bl[0])
        left = (tl[0] + bl[0]) // 2
        right = (tr[0] + br[0]) // 2
        top = (tl[1] + tr[1]) // 2
        bot = (bl[1] + br[1]) // 2
        self.swap_xy = swap
        self.invert_x = left > right
        self.invert_y = top > bot
        self.x_min, self.x_max = _edges(left, right, 28, 211, self.width)
        self.y_min, self.y_max = _edges(top, bot, 28, 291, self.height)
        self.x_off = 0
        self.y_off = 0


def _edges(a, b, sa, sb, size):
    if sb <= sa:
        return 280, 3850
    per_num = b - a
    per_den = sb - sa
    r0 = a - sa * per_num // per_den
    r1 = a + (size - 1 - sa) * per_num // per_den
    lo, hi = (r0, r1) if r0 < r1 else (r1, r0)
    if lo < 0:
        lo = 0
    if hi > 4095:
        hi = 4095
    if hi - lo < 300:
        return 280, 3850
    return int(lo), int(hi)
