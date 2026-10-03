"""Config et notes sur la flash de l'ESP32."""

import json

DEFAULT = {
    "ssid": "",
    "password": "",
    "tz": 2,
    "vol": 6,
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
    cfg["vol"] = sound_level(cfg)
    cfg["lat"] = float(cfg.get("lat") or DEFAULT["lat"])
    cfg["lon"] = float(cfg.get("lon") or DEFAULT["lon"])
    if isinstance(cur, dict) and isinstance(cur.get("touch"), dict):
        cfg["touch"] = cur["touch"]
    known = cur.get("known") if isinstance(cur, dict) else None
    if isinstance(known, list):
        cfg["known"] = [k for k in known if isinstance(k, list) and len(k) == 2 and k[0]]
    else:
        cfg["known"] = [[cfg["ssid"], cfg["password"]]] if cfg["ssid"] else []
    return cfg


def sound_level(cfg=None):
    """Volume 0 (muet) a 10. 6 est le niveau d'origine."""
    if cfg is None:
        cfg = load_config()
    try:
        v = int(cfg.get("vol", 6))
    except (TypeError, ValueError):
        v = 6
    if v < 0:
        return 0
    if v > 10:
        return 10
    return v


def sound_gain(level=None):
    """Gain 0..5. 20 % de l'echelle precedente : le niveau 1 reste audible, 10 est le maximum."""
    if level is None:
        level = sound_level()
    if level <= 0:
        return 0
    if level >= 10:
        full = 256
    elif level <= 6:
        full = 200 * level // 6
    else:
        full = 200 + 56 * (level - 6) // 4
    return max(1, full // 50)


def remember_wifi(cfg, ssid, password):
    """Reseaux qui ont fonctionne, le plus recent en tete (boot.py essaie ceux qu'il voit)."""
    known = [k for k in cfg.get("known") or [] if k[0] != ssid]
    known.insert(0, [ssid, password or ""])
    cfg["known"] = known[:5]


def forget_wifi(cfg, ssid):
    cfg["known"] = [k for k in cfg.get("known") or [] if k[0] != ssid]


def known_password(cfg, ssid):
    for k in cfg.get("known") or []:
        if k[0] == ssid:
            return k[1]
    return None


def save_config(cfg):
    out = {}
    for k in DEFAULT:
        out[k] = cfg.get(k, DEFAULT[k])
    if isinstance(cfg.get("touch"), dict):
        out["touch"] = cfg["touch"]
    out["known"] = cfg.get("known") or []
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


def log_error(e, where):
    """Ajoute la trace dans erreur.txt ; l'ancien journal passe en erreur_old.txt a 8 Ko."""
    import gc
    import os
    import sys
    import time

    try:
        if os.stat("erreur.txt")[6] > 8192:
            os.rename("erreur.txt", "erreur_old.txt")
    except OSError:
        pass
    try:
        with open("erreur.txt", "a") as f:
            f.write("%d %s libre %d\n" % (time.time(), where, gc.mem_free()))
            sys.print_exception(e, f)
    except Exception:
        pass
