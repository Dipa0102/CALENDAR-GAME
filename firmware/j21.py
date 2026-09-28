"""Jour 21 : CRYSTAL CATCH. Attraper les cristaux dans le chaudron, eviter les bombes."""

from arcade import rgb
from j08 import BOMB, BOMB_PAL, Fall

CAULDRON = (
    "k..........k",
    "kk........kk",
    ".kggggggggk.",
    "kGgwggggggGk",
    "kGggggggggGk",
    "kkkkkkkkkkkk",
    ".kMMMMMMMMk.",
    "kMMmMMMMMMMk",
    "kMMMMMMMMMMk",
    ".kMMMMMMMMk.",
    "..kk....kk..",
)
CAULDRON_PAL = {"k": rgb(20, 20, 30), "g": rgb(80, 255, 120), "G": rgb(30, 160, 70), "w": rgb(220, 255, 220),
                "M": rgb(70, 70, 90), "m": rgb(150, 150, 170)}
GEM = ("..cc..", ".cwCc.", "cwCCCc", "cCCCCc", ".cCCc.", "..cc..")


def _gem(light, mid):
    return {"c": rgb(*light), "C": rgb(*mid), "w": rgb(255, 255, 255)}


class CrystalCatch(Fall):
    TITLE = "CRYSTAL CATCH"
    HELP = ("GLISSE LE CHAUDRON", "ATTRAPE LES CRISTAUX", "EVITE LES BOMBES")
    PLAYER = CAULDRON
    PLAYER_PAL = CAULDRON_PAL
    ITEMS = (
        (BOMB, BOMB_PAL, 0, True),
        (GEM, _gem((120, 220, 255), (40, 120, 230)), 50, False),
        (GEM, _gem((255, 140, 230), (200, 40, 160)), 100, False),
        (GEM, _gem((255, 240, 120), (230, 160, 20)), 200, False),
    )
    GOOD_RATE = 1


GAME = CrystalCatch


def play(tft, touch, day):
    GAME(tft, touch, day).run()
