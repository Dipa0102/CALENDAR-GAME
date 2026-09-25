# Connexion et scan ici, avant main.py : ensuite la memoire interne
# ne suffit plus au pilote Wi-Fi.
import json
import time
import network
from machine import Pin, SPI
import boardio


def _saved_wifi():
    try:
        with open("config.json") as handle:
            cfg = json.load(handle)
    except Exception:
        return "", ""
    if not isinstance(cfg, dict):
        return "", ""
    return cfg.get("ssid") or "", cfg.get("password") or ""


try:
    boardio.wlan = network.WLAN(network.STA_IF)
    boardio.wlan.active(True)
except Exception:
    boardio.wlan = None

if boardio.wlan is not None:
    w = boardio.wlan
    ssid, password = _saved_wifi()
    if ssid:
        try:
            w.connect(ssid, password)
            t0 = time.ticks_ms()
            while not w.isconnected() and time.ticks_diff(time.ticks_ms(), t0) < 15000:
                if w.status() in (201, 202, 203):
                    break
                time.sleep_ms(200)
        except Exception:
            pass
        boardio.status = w.status()
        # Sans ca le pilote reessaie en boucle et scan() echoue.
        if not w.isconnected():
            try:
                w.disconnect()
            except Exception:
                pass
            time.sleep_ms(300)
    for _ in range(2):
        try:
            boardio.cached = w.scan() or []
        except Exception:
            boardio.cached = []
        if boardio.cached:
            break
        time.sleep_ms(500)

try:
    boardio.spi = SPI(
        1,
        baudrate=40000000,
        polarity=0,
        phase=0,
        sck=Pin(14),
        mosi=Pin(13),
        miso=Pin(12),
    )
except Exception:
    boardio.spi = None
