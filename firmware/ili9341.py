"""ILI9341 240x320 SPI — pins E32R28T / LCDWIKI ESP32-32E."""

from machine import Pin, SPI
from micropython import const
import time

_SWRESET = const(0x01)
_SLPOUT = const(0x11)
_DISPON = const(0x29)
_CASET = const(0x2A)
_PASET = const(0x2B)
_RAMWR = const(0x2C)
_MADCTL = const(0x36)
_COLMOD = const(0x3A)
_INVON = const(0x21)
_INVOFF = const(0x20)

# MADCTL bits
_MY = const(0x80)
_MX = const(0x40)
_MV = const(0x20)
_BGR = const(0x08)


def rgb(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


class ILI9341:
    def __init__(
        self,
        spi,
        cs=15,
        dc=2,
        bl=21,
        width=240,
        height=320,
        rotation=0,
        invert=False,
        baudrate=20000000,
    ):
        if spi is None:
            spi = SPI(1, baudrate=baudrate, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
        self.spi = spi
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=0)
        self.bl = Pin(bl, Pin.OUT, value=1)
        self.rotation = rotation
        self._set_rotation(rotation, width, height)
        self._buf = bytearray(240 * 2)
        self._wb = bytearray(4)
        self._wx = self._wy = -1
        self._init(invert)

    def _set_rotation(self, rotation, width, height):
        rotation &= 3
        if rotation == 0:
            mad = _MX | _BGR
            self.width, self.height = width, height
        elif rotation == 1:
            mad = _MV | _BGR
            self.width, self.height = height, width
        elif rotation == 2:
            mad = _MY | _BGR
            self.width, self.height = width, height
        else:
            mad = _MX | _MY | _MV | _BGR
            self.width, self.height = height, width
        self._mad = mad

    def _wcmd(self, cmd, data=None):
        self.cs(0)
        self.dc(0)
        self.spi.write(bytearray([cmd]))
        if data:
            self.dc(1)
            self.spi.write(data if isinstance(data, (bytes, bytearray)) else bytearray(data))
        self.cs(1)

    def _init(self, invert):
        self._wcmd(_SWRESET)
        time.sleep_ms(50)
        self._wcmd(_SLPOUT)
        time.sleep_ms(120)
        self._wcmd(0xCF, b"\x00\xC1\x30")
        self._wcmd(0xED, b"\x64\x03\x12\x81")
        self._wcmd(0xE8, b"\x85\x00\x78")
        self._wcmd(0xCB, b"\x39\x2C\x00\x34\x02")
        self._wcmd(0xF7, b"\x20")
        self._wcmd(0xEA, b"\x00\x00")
        self._wcmd(0xC0, b"\x23")
        self._wcmd(0xC1, b"\x10")
        self._wcmd(0xC5, b"\x3E\x28")
        self._wcmd(0xC7, b"\x86")
        self._wcmd(_MADCTL, bytes([self._mad]))
        self._wcmd(_COLMOD, b"\x55")
        self._wcmd(0xB1, b"\x00\x18")
        self._wcmd(0xB6, b"\x08\x82\x27")
        self._wcmd(0xF2, b"\x00")
        self._wcmd(0x26, b"\x01")
        self._wcmd(0xE0, b"\x0F\x31\x2B\x0C\x0E\x08\x4E\xF1\x37\x07\x10\x03\x0E\x09\x00")
        self._wcmd(0xE1, b"\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F")
        self._wcmd(_INVON if invert else _INVOFF)
        self._wcmd(_DISPON)
        time.sleep_ms(20)

    def _window(self, x0, y0, x1, y1):
        # Chaque transfert SPI coute ~120 us : on ne renvoie que les bords qui changent.
        wb = self._wb
        self.cs(0)
        xs = (x0 << 16) | x1
        if xs != self._wx:
            self._wx = xs
            self.dc(0)
            self.spi.write(b"\x2a")
            self.dc(1)
            wb[0] = x0 >> 8
            wb[1] = x0 & 0xFF
            wb[2] = x1 >> 8
            wb[3] = x1 & 0xFF
            self.spi.write(wb)
        ys = (y0 << 16) | y1
        if ys != self._wy:
            self._wy = ys
            self.dc(0)
            self.spi.write(b"\x2b")
            self.dc(1)
            wb[0] = y0 >> 8
            wb[1] = y0 & 0xFF
            wb[2] = y1 >> 8
            wb[3] = y1 & 0xFF
            self.spi.write(wb)
        self.dc(0)
        self.spi.write(b"\x2c")
        self.dc(1)

    def forget_window(self):
        self._wx = self._wy = -1

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        if x < 0:
            w += x
            x = 0
        if y < 0:
            h += y
            y = 0
        if w <= 0 or h <= 0 or x >= self.width or y >= self.height:
            return
        if x + w > self.width:
            w = self.width - x
        if y + h > self.height:
            h = self.height - y
        hi, lo = color >> 8, color & 0xFF
        row_n = w * 2
        buf = self._buf
        if row_n > len(buf):
            buf = bytearray(row_n)
        cap = len(buf) // row_n
        need = h if h < cap else cap
        for i in range(0, row_n, 2):
            buf[i] = hi
            buf[i + 1] = lo
        filled = 1
        while filled < need:
            take = filled if filled <= need - filled else need - filled
            buf[filled * row_n:(filled + take) * row_n] = buf[:take * row_n]
            filled += take
        left = h
        yy = y
        while left:
            n = need if left > need else left
            self._window(x, yy, x + w - 1, yy + n - 1)
            self.spi.write(memoryview(buf)[:n * row_n])
            yy += n
            left -= n
        self.cs(1)

    def blit(self, buf, x, y, w, h):
        self._window(x, y, x + w - 1, y + h - 1)
        self.spi.write(memoryview(buf)[:w * h * 2])
        self.cs(1)

    def fill(self, color):
        self.fill_rect(0, 0, self.width, self.height, color)

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def rect(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.fill_rect(x, y, 1, 1, color)

    def fill_circle(self, cx, cy, r, color):
        # mid-point, filled via spans
        x, y, err = r, 0, 1 - r
        while x >= y:
            self.hline(cx - x, cy + y, 2 * x + 1, color)
            self.hline(cx - x, cy - y, 2 * x + 1, color)
            self.hline(cx - y, cy + x, 2 * y + 1, color)
            self.hline(cx - y, cy - x, 2 * y + 1, color)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1
