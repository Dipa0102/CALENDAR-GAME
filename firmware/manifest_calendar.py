# Firmware MicroPython de Calendar Game : modules de l'application geles en flash.
# Chemins relatifs a ce fichier : build_firmware.py le copie avec les sources dans WSL
# (chemin sans espace) avant de compiler.
include("$(PORT_DIR)/boards/manifest.py")

freeze(
    ".",
    (
        "ili9341.py", "font8.py", "xpt2046.py", "store.py", "net.py", "battery.py",
        "arcade.py", "advent.py", "kartcal.py", "game.py", "musique.py",
        "j02.py", "j03.py", "j04.py", "j07.py", "j08.py", "j09.py", "j10.py",
        "j11.py", "j13.py", "j21.py", "j22.py",
    ),
)
