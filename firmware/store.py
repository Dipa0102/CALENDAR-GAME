"""Config et notes sur la flash de l'ESP32."""

import json

DEFAULT = {
    "ssid": "",
    "password": "",
    "tz": 2,
    "city": "Paris",
    "lat": 48.8566,
    "lon": 2.3522,
}


def _read(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def load_config():
    cfg = {}
    for k in DEFAULT:
        cfg[k] = DEFAULT[k]
    old = _read("wifi.json")
    if isinstance(old, dict):
        if old.get("ssid"):
            cfg["ssid"] = old.get("ssid") or ""
            cfg["password"] = old.get("password") or ""
        if "tz" in old:
            cfg["tz"] = int(old.get("tz") or 2)
    cur = _read("config.json")
    if isinstance(cur, dict):
        for k in DEFAULT:
            if k in cur and cur[k] not in (None, ""):
                cfg[k] = cur[k]
        if "ssid" in cur:
            cfg["ssid"] = cur.get("ssid") or ""
        if "password" in cur:
            cfg["password"] = cur.get("password") or ""
    cfg["tz"] = int(cfg.get("tz") or 2)
    cfg["lat"] = float(cfg.get("lat") or DEFAULT["lat"])
    cfg["lon"] = float(cfg.get("lon") or DEFAULT["lon"])
    if isinstance(cur, dict) and isinstance(cur.get("touch"), dict):
        cfg["touch"] = cur["touch"]
    return cfg


def save_config(cfg):
    out = {}
    for k in DEFAULT:
        out[k] = cfg.get(k, DEFAULT[k])
    if isinstance(cfg.get("touch"), dict):
        out["touch"] = cfg["touch"]
    with open("config.json", "w") as f:
        json.dump(out, f)
    with open("wifi.json", "w") as f:
        json.dump({"ssid": cfg.get("ssid") or "", "password": cfg.get("password") or "", "tz": int(cfg.get("tz") or 2)}, f)


def load_notes():
    data = _read("notes.json")
    return data if isinstance(data, dict) else {}


def save_notes(notes):
    with open("notes.json", "w") as f:
        json.dump(notes, f)


def day_key(y, m, d):
    return "%04d-%02d-%02d" % (y, m, d)
