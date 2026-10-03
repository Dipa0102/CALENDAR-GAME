"""Compile le firmware MicroPython de la carte, modules de l'application geles en flash.

Un module gele s'execute directement depuis la flash : il ne prend plus le tas RAM
a l'import et la memoire systeme reste libre pour le Wi-Fi. Resultat :
firmware_calendar.bin, a flasher SANS effacer la carte (notes et reglages gardes).

Installation unique (Windows 11 + WSL2, ~15 min, ~4 Go dans WSL) :
    wsl --install -d Ubuntu-24.04
    python build_firmware.py --setup
--setup installe les paquets (apt, en root), ESP-IDF v5.5.2 dans ~/esp/esp-idf,
MicroPython v1.29.0 dans ~/esp/micropython, mpy-cross et les sous-modules du port esp32.

Ensuite, apres chaque modification du code :
    python build_firmware.py    compile, copie firmware_calendar.bin ici
    python flash.py             flashe sans effacer puis lance deploy.py --frozen
Un .mpy laisse sur la carte masque le module gele du meme nom.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

from deploy import FROZEN, FROZEN_FW

HERE = Path(__file__).resolve().parent
DISTRO = os.environ.get("WSL_DISTRO", "Ubuntu-24.04")
USER = os.environ.get("WSL_USER", "utilisateur")
# Partition factory de partitions-4MiBplus.csv (table d'origine, a ne pas changer).
APP_MAX = 2031616

APT = """set -e
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y git wget flex bison gperf python3 python3-pip \
    python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0 build-essential
"""

SETUP = """set -e
mkdir -p ~/esp && cd ~/esp
[ -d esp-idf/.git ] || git clone -b v5.5.2 --recursive --shallow-submodules --depth 1 \
    https://github.com/espressif/esp-idf.git
./esp-idf/install.sh esp32
[ -d micropython/.git ] || git clone --depth 1 -b v1.29.0 https://github.com/micropython/micropython.git
make -C micropython/mpy-cross
. ~/esp/esp-idf/export.sh
make -C micropython/ports/esp32 BOARD=ESP32_GENERIC submodules
"""

# make et idf.py ne supportent pas l'espace de "calendar ESP32" : copie dans ~/esp/calendar.
BUILD = """set -e
. ~/esp/esp-idf/export.sh > /dev/null
mkdir -p ~/esp/calendar/audio
cp -p {files} ~/esp/calendar/
cp -p {audio} ~/esp/calendar/audio/
cd ~/esp/micropython/ports/esp32
make BOARD=ESP32_GENERIC USER_C_MODULES=$HOME/esp/calendar/audio/micropython.cmake \
    FROZEN_MANIFEST=$HOME/esp/calendar/manifest_calendar.py -j$(nproc)
cp build-ESP32_GENERIC/firmware.bin {out}
"""


def wsl_path(p: Path) -> str:
    s = str(p.resolve())
    return "/mnt/%s%s" % (s[0].lower(), s[2:].replace("\\", "/"))


def wsl(script: str, user: str = USER) -> None:
    # Script dans un fichier : evite les pieges de guillemets entre Windows et bash.
    with tempfile.NamedTemporaryFile("w", suffix=".sh", newline="\n", delete=False) as f:
        f.write(script)
    try:
        cmd = ["wsl", "-d", DISTRO, "-u", user, "--exec", "bash", wsl_path(Path(f.name))]
        print("+", " ".join(cmd))
        if subprocess.run(cmd).returncode != 0:
            raise SystemExit("echec dans WSL")
    finally:
        os.remove(f.name)


def main() -> None:
    if "--setup" in sys.argv:
        wsl(APT, "root")
        wsl(SETUP)
        return
    files = ["manifest_calendar.py"] + [m + ".py" for m in FROZEN]
    audio = sorted((HERE / "audio").iterdir())
    wsl(BUILD.format(files=" ".join(shlex.quote(wsl_path(HERE / n)) for n in files),
                     audio=" ".join(shlex.quote(wsl_path(p)) for p in audio),
                     out=shlex.quote(wsl_path(FROZEN_FW))))
    # firmware.bin commence a 0x1000 (bootloader, table), l'application a 0x10000.
    app = FROZEN_FW.stat().st_size - 0xF000
    print("%s : %d octets, application %d / %d (%d%%, reste %d)" % (FROZEN_FW.name, FROZEN_FW.stat().st_size, app, APP_MAX, 100 * app // APP_MAX, APP_MAX - app))


if __name__ == "__main__":
    main()
