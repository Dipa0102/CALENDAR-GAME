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


def connect_wifi(ssid, password, timeout_s=15):
    global last_status
    import network

    if not ssid:
        return False
    wlan = network.WLAN(network.STA_IF)
    try:
        if wlan.isconnected() and _current_ssid(wlan) == ssid:
            return True
        if wlan.isconnected():
            wlan.disconnect()
        wlan.connect(ssid, password or "")
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            last_status = wlan.status()
            if last_status in (201, 202, 203):
                break
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_s * 1000:
                break
            time.sleep_ms(200)
    except Exception:
        last_status = "mem"
    if wlan.isconnected():
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


def scan_wifi():
    import boardio

    found = None
    try:
        import network

        wlan = network.WLAN(network.STA_IF)
        if wlan.active():
            found = wlan.scan()
    except Exception:
        found = None
    if not found:
        found = boardio.cached
    return _pack(found)


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
        data = b""
        while len(data) < 8000:
            chunk = s.recv(512)
            if not chunk:
                break
            data += chunk
    finally:
        s.close()
    i = data.find(b"\r\n\r\n")
    body = data[i + 4 :] if i >= 0 else data
    return json.loads(body)


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
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,wind_gusts_10m_max"
        "&timezone=auto&forecast_days=7" % (float(lat), float(lon))
    )
    if model:
        path += "&models=" + model
    return http_json("api.open-meteo.com", path)


def fetch_weather(lat, lon):
    # Modeles Meteo-France (AROME/ARPEGE) : ~4 jours seulement,
    # la suite de la semaine vient du modele par defaut.
    mf = _forecast(lat, lon, "meteofrance_seamless")
    cur = mf.get("current") or {}
    daily = mf.get("daily") or {}
    dates = daily.get("time") or []
    codes = daily.get("weather_code") or []
    tmax = daily.get("temperature_2m_max") or []
    tmin = daily.get("temperature_2m_min") or []
    gusts = daily.get("wind_gusts_10m_max") or []
    mf = None
    gc.collect()
    days = []
    missing = False
    for i in range(len(dates)):
        c = codes[i] if i < len(codes) else None
        hi = tmax[i] if i < len(tmax) else None
        lo = tmin[i] if i < len(tmin) else None
        if c is None or hi is None or lo is None:
            missing = True
        days.append([dates[i], c, hi, lo, c is not None, gusts[i] if i < len(gusts) else None])
    if missing or len(days) < 7 or cur.get("temperature_2m") is None:
        try:
            alt = _forecast(lat, lon, "")
            acur = alt.get("current") or {}
            ad = alt.get("daily") or {}
            alt = None
            if cur.get("temperature_2m") is None:
                cur = acur
            adates = ad.get("time") or []
            agusts = ad.get("wind_gusts_10m_max") or []
            for i in range(len(adates)):
                g = agusts[i] if i < len(agusts) else None
                row = [adates[i], ad["weather_code"][i], ad["temperature_2m_max"][i], ad["temperature_2m_min"][i], False, g]
                if i < len(days):
                    if days[i][1] is None or days[i][2] is None or days[i][3] is None:
                        days[i] = row
                else:
                    days.append(row)
        except Exception:
            pass
    return {
        "temp": cur.get("temperature_2m"),
        "code": int(cur.get("weather_code") or 0),
        "night": cur.get("is_day") == 0,
        "gust": cur.get("wind_gusts_10m"),
        "days": [d for d in days if d[1] is not None],
    }
