"""Wi-Fi, NTP et meteo Open-Meteo (sans cle)."""

import gc
import json
import socket
import time


def _quote(s):
    out = ""
    for c in s:
        if ("A" <= c <= "Z") or ("a" <= c <= "z") or ("0" <= c <= "9") or c in "-_.":
            out += c
        elif c == " ":
            out += "%20"
        else:
            out += "%%%02X" % ord(c)
    return out


last_status = None


def connect_wifi(ssid, password, timeout_s=15, patient=False):
    """patient : reseau qu'on vient de voir, on laisse le pilote reessayer jusqu'au bout."""
    global last_status
    import network

    if not ssid:
        return False
    wlan = network.WLAN(network.STA_IF)
    try:
        if wlan.isconnected() and _current_ssid(wlan) == ssid:
            return True
        # Aussi hors connexion : pendant une tentative en cours (reconnexion
        # automatique), connect() echoue en "Wifi Internal State Error".
        wlan.disconnect()
        t0 = time.ticks_ms()
        while wlan.isconnected() and time.ticks_diff(time.ticks_ms(), t0) < 2000:
            time.sleep_ms(50)
        wlan.connect(ssid, password or "")
        t0 = time.ticks_ms()
        # status() garde le code du dernier echec (201...) tant que la nouvelle
        # tentative n'a pas abouti : seul un echec vu apres un autre code compte.
        fresh = False
        while not wlan.isconnected():
            last_status = wlan.status()
            if last_status not in (201, 202, 203):
                fresh = True
            elif fresh and (last_status == 202 or not patient):
                break
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_s * 1000:
                break
            time.sleep_ms(200)
    except Exception as e:
        last_status = "mem" if isinstance(e, MemoryError) or e.args[:1] == (12,) else "occupe"
    if wlan.isconnected() and _current_ssid(wlan) == ssid:
        last_status = wlan.status()
        return True
    # Sans disconnect le pilote reessaie en boucle et bloque scan().
    try:
        wlan.disconnect()
    except Exception:
        pass
    return False


def status_text(code):
    if code == 202:
        return "MOT DE PASSE FAUX"
    if code == 201:
        return "RESEAU INTROUVABLE"
    if code == "mem":
        return "MEMOIRE PLEINE"
    if code == "occupe":
        return "WIFI OCCUPE, REESSAIE"
    if code == 1001:
        return "MOT DE PASSE OU SIGNAL ?"
    return "WIFI KO %s" % code


def _current_ssid(wlan):
    cur = ""
    try:
        cur = wlan.config("essid")
    except Exception:
        try:
            cur = wlan.config("ssid")
        except Exception:
            return ""
    if isinstance(cur, bytes):
        try:
            cur = cur.decode()
        except Exception:
            return ""
    return cur or ""


def _decode_ssid(raw):
    if isinstance(raw, bytes):
        try:
            raw = raw.decode()
        except Exception:
            return ""
    return (raw or "").replace("\x00", "").strip()


def _pack(found):
    best = {}
    for item in found or []:
        if not item:
            continue
        if isinstance(item, dict):
            name = item.get("ssid") or ""
            rssi = int(item.get("rssi") or -100)
            opened = bool(item.get("open"))
        else:
            name = _decode_ssid(item[0])
            rssi = int(item[3]) if len(item) > 3 else -100
            sec = int(item[4]) if len(item) > 4 else 1
            opened = sec == 0
        if not name:
            continue
        prev = best.get(name)
        if prev is None or rssi > prev["rssi"]:
            best[name] = {"ssid": name, "rssi": rssi, "open": opened}
    nets = []
    for name in best:
        nets.append(best[name])
    nets.sort(key=lambda n: n["rssi"], reverse=True)
    return nets


# Le tas MicroPython grandit en prenant la memoire systeme ; sous ce seuil
# (plus grand bloc libre), le pilote Wi-Fi ne peut plus chercher ni se connecter.
WIFI_ROOM = 8192


def wifi_room():
    try:
        import esp32

        return max(r[2] for r in esp32.idf_heap_info(esp32.HEAP_DATA))
    except Exception:
        return WIFI_ROOM


def scan_wifi():
    """Reseaux visibles, ou None si le pilote n'a plus la memoire de chercher."""
    import network

    if wifi_room() < WIFI_ROOM:
        return None
    try:
        wlan = network.WLAN(network.STA_IF)
        if not wlan.active():
            return None
        if not wlan.isconnected():
            # Une reconnexion automatique en cours fait echouer scan().
            wlan.disconnect()
        return _pack(wlan.scan())
    except Exception:
        return None


def boot_nets():
    """Reseaux vus par boot.py au demarrage, memoire encore libre."""
    import boardio

    return _pack(boardio.cached)


def connected_ssid():
    import network

    wlan = network.WLAN(network.STA_IF)
    return _current_ssid(wlan) if wlan.isconnected() else ""


def sync_ntp(tz_hours):
    import machine
    import ntptime

    ntptime.host = "pool.ntp.org"
    ntptime.timeout = 8
    ntptime.settime()
    t = time.time() + int(tz_hours) * 3600
    tm = time.localtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
    return True


# HTTP simple : le TLS demande ~40 Ko de RAM interne et leve ENOMEM ici.
def http_json(host, path):
    gc.collect()
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.settimeout(12)
    try:
        s.connect(addr)
        s.send(("GET %s HTTP/1.0\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path, host)).encode())
        status = s.readline()
        if b" 200 " not in status:
            raise OSError("HTTP " + status[:40].decode())
        while s.readline() not in (b"\r\n", b"\n", b""):
            pass
        # Lu au fil du flux : pas de reponse entiere en memoire (tas fragmente).
        return json.load(s)
    finally:
        s.close()


def search_cities(name):
    q = _quote(name.strip())
    if not q:
        return []
    data = http_json("geocoding-api.open-meteo.com", "/v1/search?name=%s&count=4&language=fr&format=json" % q)
    out = []
    for item in data.get("results") or []:
        out.append(
            {
                "name": item.get("name") or "?",
                "country": item.get("country") or "",
                "lat": float(item.get("latitude")),
                "lon": float(item.get("longitude")),
            }
        )
    return out


def _forecast(lat, lon, model):
    path = (
        "/v1/forecast?latitude=%.4f&longitude=%.4f"
        "&current=temperature_2m,weather_code,is_day,wind_gusts_10m"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,wind_gusts_10m_max,"
        "relative_humidity_2m_mean,sunrise,sunset"
        "&timezone=auto&forecast_days=7" % (float(lat), float(lon))
    )
    if model:
        path += "&models=" + model
    return http_json("api.open-meteo.com", path)


_DAILY = (
    "weather_code", "temperature_2m_max", "temperature_2m_min", "wind_gusts_10m_max",
    "relative_humidity_2m_mean", "sunrise", "sunset",
)


def _rows(daily, mf):
    """[date, code, maxi, mini, meteo-france, rafales, humidite, lever, coucher] par jour."""
    cols = [daily.get(k) or [] for k in _DAILY]
    rows = []
    for i, date in enumerate(daily.get("time") or []):
        c, hi, lo, gust, hum, rise, sset = [col[i] if i < len(col) else None for col in cols]
        # "2026-09-28T07:45" -> "07:45", deja a l'heure locale (timezone=auto)
        rows.append([date, c, hi, lo, mf and c is not None, gust, hum, rise and rise[11:16], sset and sset[11:16]])
    return rows


def _incomplete(row):
    return row[1] is None or row[2] is None or row[3] is None


def fetch_weather(lat, lon):
    # Modeles Meteo-France (AROME/ARPEGE) : ~4 jours seulement,
    # la suite de la semaine vient du modele par defaut.
    mf = _forecast(lat, lon, "meteofrance_seamless")
    cur = mf.get("current") or {}
    days = _rows(mf.get("daily") or {}, True)
    mf = None
    gc.collect()
    if len(days) < 7 or any(_incomplete(d) for d in days) or cur.get("temperature_2m") is None:
        try:
            alt = _forecast(lat, lon, "")
            if cur.get("temperature_2m") is None:
                cur = alt.get("current") or {}
            rows = _rows(alt.get("daily") or {}, False)
            alt = None
            for i, row in enumerate(rows):
                if i >= len(days):
                    days.append(row)
                elif _incomplete(days[i]):
                    days[i] = row
                elif days[i][6] is None:
                    days[i][6] = row[6]
        except Exception:
            pass
    return {
        "temp": cur.get("temperature_2m"),
        "code": int(cur.get("weather_code") or 0),
        "night": cur.get("is_day") == 0,
        "gust": cur.get("wind_gusts_10m"),
        "days": [d for d in days if d[1] is not None],
    }
