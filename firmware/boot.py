# Connexion et scan ici, avant main.py : ensuite la memoire interne
# ne suffit plus au pilote Wi-Fi.
import json
import time
import network
from machine import Pin, SPI
import boardio


def _saved_wifi():
    """(ssid, mot de passe) : le reseau choisi d'abord, puis les autres deja connus."""
    try:
        with open("config.json") as handle:
            cfg = json.load(handle)
    except Exception:
        return []
    if not isinstance(cfg, dict):
        return []
    nets = []
    if cfg.get("ssid"):
        nets.append((cfg["ssid"], cfg.get("password") or ""))
    for k in cfg.get("known") or []:
        try:
            if k[0] and k[0] != cfg.get("ssid"):
                nets.append((k[0], k[1] or ""))
        except Exception:
            pass
    return nets


try:
    boardio.wlan = network.WLAN(network.STA_IF)
    boardio.wlan.active(True)
except Exception:
    boardio.wlan = None

if boardio.wlan is not None:
    w = boardio.wlan
    for _ in range(2):
        try:
            boardio.cached = w.scan() or []
        except Exception:
            boardio.cached = []
        if boardio.cached:
            break
        time.sleep_ms(500)
    seen = set()
    for r in boardio.cached:
        try:
            seen.add(r[0].decode())
        except Exception:
            pass
    nets = _saved_wifi()
    pick = None
    for cand in nets:
        if cand[0] in seen:
            pick = cand
            break
    # Aucun connu en vue : on tente quand meme le choisi (reseau masque).
    if pick is None and nets:
        pick = nets[0]
    if pick:
        # Reseau vu au scan : un "introuvable" n'est que passager, le pilote reessaie.
        patient = pick[0] in seen
        try:
            w.connect(pick[0], pick[1])
            t0 = time.ticks_ms()
            while not w.isconnected() and time.ticks_diff(time.ticks_ms(), t0) < 15000:
                st = w.status()
                if st == 202 or (st in (201, 203) and not patient):
                    break
                time.sleep_ms(200)
        except Exception:
            pass
        boardio.status = w.status()
        # Sans ca le pilote reessaie en boucle et bloque scan().
        if not w.isconnected():
            try:
                w.disconnect()
            except Exception:
                pass

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
