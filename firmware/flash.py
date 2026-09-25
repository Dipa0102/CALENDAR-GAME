"""Telecharge MicroPython, efface et flashe la carte, puis copie Calendar Game sur l'E32R28T."""
from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from deploy import PORT

HERE = Path(__file__).resolve().parent
FW_URL = "https://micropython.org/resources/firmware/ESP32_GENERIC-20260824-v1.29.0.bin"
FW = HERE / "ESP32_GENERIC-v1.29.0.bin"

def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def main() -> None:
    if not FW.exists():
        print("telechargement firmware MicroPython...")
        urllib.request.urlretrieve(FW_URL, FW)
        print("ok", FW.stat().st_size, "octets")
    run([sys.executable, "-m", "pip", "install", "-q", "mpremote"])
    print("efface + flash MicroPython sur", PORT)
    run(
        [
            sys.executable,
            "-m",
            "esptool",
            "--chip",
            "esp32",
            "--port",
            PORT,
            "--baud",
            "460800",
            "erase-flash",
        ]
    )
    run(
        [
            sys.executable,
            "-m",
            "esptool",
            "--chip",
            "esp32",
            "--port",
            PORT,
            "--baud",
            "460800",
            "write-flash",
            "-z",
            "0x1000",
            str(FW),
        ]
    )
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
