"""Flashe MicroPython puis copie Calendar Game sur l'E32R28T.

Avec firmware_calendar.bin (build_firmware.py, modules geles) : flash SANS effacer,
notes et reglages restent sur la carte, puis deploy.py --frozen.
Sinon : telecharge MicroPython officiel, efface, flashe, deploy.py puis restore_backup.py.
"""
from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from deploy import FROZEN_FW, PORT

HERE = Path(__file__).resolve().parent
FW_URL = "https://micropython.org/resources/firmware/ESP32_GENERIC-20260824-v1.29.0.bin"
FW = HERE / "ESP32_GENERIC-v1.29.0.bin"
ESPTOOL = [sys.executable, "-m", "esptool", "--chip", "esp32", "--port", PORT, "--baud", "460800"]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def main() -> None:
    run([sys.executable, "-m", "pip", "install", "-q", "mpremote"])
    if FROZEN_FW.exists():
        print("flash", FROZEN_FW.name, "sur", PORT, "sans effacer")
        # Meme table de partitions : le systeme de fichiers (notes, reglages) reste intact.
        run(ESPTOOL + ["write-flash", "-z", "0x1000", str(FROZEN_FW)])
        time.sleep(3)
        run([sys.executable, str(HERE / "deploy.py"), "--frozen"])
        print("Calendar Game doit s'afficher.")
        return
    if not FW.exists():
        print("telechargement firmware MicroPython...")
        urllib.request.urlretrieve(FW_URL, FW)
        print("ok", FW.stat().st_size, "octets")
    print("efface + flash MicroPython sur", PORT)
    run(ESPTOOL + ["erase-flash"])
    run(ESPTOOL + ["write-flash", "-z", "0x1000", str(FW)])
    run([sys.executable, "-m", "pip", "install", "-q", "mpy-cross"])
    # Premier demarrage de MicroPython : il formate sa memoire et refuse mpremote.
    time.sleep(10)
    run([sys.executable, str(HERE / "deploy.py")])
    # Le calendrier demarre des la fin de deploy.py : restore_backup.py l'interrompt avant de copier.
    if (HERE / "backup_carte").is_dir():
        run([sys.executable, str(HERE / "restore_backup.py")])
    print("Calendar Game doit s'afficher.")


if __name__ == "__main__":
    main()
