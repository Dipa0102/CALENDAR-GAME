"""Recopie sur la carte les reglages et notes sauvegardes dans backup_carte/.

Ce dossier contient le mot de passe Wi-Fi : il est exclu du depot git.
"""
import subprocess
import sys
import time
from pathlib import Path

import serial

from deploy import PORT

HERE = Path(__file__).resolve().parent

s = serial.Serial(PORT, 115200, timeout=0.2)
s.dtr = False
s.rts = False
out = b""
for _ in range(30):
    s.write(b"\x03")
    time.sleep(0.1)
    out += s.read(4096)
    if b">>>" in out:
        break
s.close()
print("REPL" if b">>>" in out else "pas de REPL", out[-200:])

mp = [sys.executable, "-m", "mpremote", "connect", PORT, "resume"]
for name in ("config.json", "wifi.json", "notes.json"):
    f = HERE / "backup_carte" / name
    if f.exists():
        r = subprocess.run(mp + ["cp", str(f), ":" + name])
        print(name, "ok" if r.returncode == 0 else "ECHEC")
subprocess.run(mp + ["ls"])
subprocess.run(mp + ["reset"])
