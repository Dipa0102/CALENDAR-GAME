"""Compile en .mpy et copie sur la carte sans effacer notes ni reglages.

python deploy.py --frozen : pour le firmware maison (build_firmware.py), ne copie que
les fichiers simples et retire de la carte les .mpy des modules geles, qui les masqueraient.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = os.environ.get("PORT_CARTE", "COM4")
BUILD = HERE / "build"
MODULES = {
    "kartcal.py": "kartcal.mpy",
    "ili9341.py": "ili9341.mpy",
    "font8.py": "font8.mpy",
    "xpt2046.py": "xpt2046.mpy",
    "store.py": "store.mpy",
    "net.py": "net.mpy",
    "game.py": "game.mpy",
    "arcade.py": "arcade.mpy",
    "advent.py": "advent.mpy",
    "battery.py": "battery.mpy",
    "musique.py": "musique.mpy",
}
MODULES.update({"j%02d.py" % d: "j%02d.mpy" % d for d in (2, 3, 4, 7, 8, 9, 10, 11, 13, 21, 22)})
PLAIN = {"boot.py": "boot.py", "boardio.py": "boardio.py", "main.py": "main.py", "logo.raw": "logo.raw"}
PLAIN.update({n: n for n in ("wxn18.raw", "wxp18.raw", "wxa64.raw", "veille.raw")})
# Fait par convert_music.py, absent du depot : copie seulement s'il existe.
OPTIONAL = ("musique.adp", "meteo_soleil.adp", "meteo_pluie.adp", "meteo_orage.adp")
STALE = ["ili9341.py", "font8.py", "xpt2046.py", "store.py", "net.py", "game.py", "kartcal.py"]
# Modules geles dans firmware_calendar.bin : la liste vient du manifeste.
FROZEN = re.findall(r'"(\w+)\.py"', (HERE / "manifest_calendar.py").read_text())
FROZEN_FW = HERE / "firmware_calendar.bin"


def run(cmd: list[str], check: bool = True) -> None:
    print("+", " ".join(cmd))
    if subprocess.run(cmd).returncode != 0 and check:
        raise SystemExit(1)


def interrupt() -> None:
    import time

    import serial

    s = serial.Serial(PORT, 115200, timeout=0.2)
    out = b""
    for _ in range(40):
        s.write(b"\x03")
        time.sleep(0.1)
        out += s.read(4096)
        if b">>>" in out:
            break
    s.close()
    if b">>>" not in out:
        raise SystemExit("la carte ne rend pas la main (REPL introuvable)")


def unmask(names: list[str]) -> None:
    """Retire de la carte des .mpy qui masqueraient les modules geles du firmware maison."""
    mp = [sys.executable, "-m", "mpremote", "connect", PORT, "resume"]
    run(mp + ["exec", "import os\nfor n in %r:\n try: os.remove(n)\n except OSError: pass" % names])


def main() -> None:
    frozen = "--frozen" in sys.argv
    mods = {src: out for src, out in MODULES.items() if not (frozen and src[:-3] in FROZEN)}
    BUILD.mkdir(exist_ok=True)
    for src, out in mods.items():
        run([sys.executable, "-m", "mpy_cross", "-march=xtensawin", "-o", str(BUILD / out), str(HERE / src)])
    interrupt()
    mp = [sys.executable, "-m", "mpremote", "connect", PORT, "resume"]
    for name in STALE:
        run(mp + ["rm", ":" + name], check=False)
    if frozen:
        unmask([m + ".mpy" for m in FROZEN])
    for out in mods.values():
        run(mp + ["cp", str(BUILD / out), ":" + out])
    for src, dst in PLAIN.items():
        run(mp + ["cp", str(HERE / src), ":" + dst])
    for name in OPTIONAL:
        if (HERE / name).exists():
            run(mp + ["cp", str(HERE / name), ":" + name])
    run(mp + ["reset"])


if __name__ == "__main__":
    main()
