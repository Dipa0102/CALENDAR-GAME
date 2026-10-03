"""Calendrier de l'Avent : un mini-jeu par jour du 1er au 25 decembre."""

import gc
import math
import random
import sys
import time

from font8 import draw_text
from ili9341 import rgb

import arcade
from arcade import BLACK, CYAN, GOLD, GREY, NIGHT, PINK, RED, VIOLET, WHITE, H, W, blit_lines, line_sprite, sprite

# (jour, module charge a la demande, titre). None : jeu pas encore livre.
GAMES = (
    (1, "game", "MAGIC HARRY"),
    (2, "j02", "STAR RAID"),
    (3, "j03", "SERPENT 80"),
    (4, "j04", "PING 80"),
    (5, "j05", "ENVAHISSEURS"),
    (6, "j06", "ROCHERS 80"),
    (7, "j07", "ROUTE 80"),
    (8, "j08", "BOMB DODGE"),
    (9, "j09", "TURBO 80"),
    (10, "j10", "HELICO 80"),
    (11, "j11", "PAIRES 80"),
    (12, "j12", "BLOCS 80"),
    (13, "j13", "CIBLES 80"),
    (14, "j14", "DEFENSEUR"),
    (15, "j15", "MINEUR 80"),
    (16, "j16", "ALUNISSAGE"),
    (17, "j17", "SAUTEUR 80"),
    (18, "j18", "FIRE ESCAPE"),
    (19, "j19", "ZOMBIE NIGHT"),
    (20, "j20", "LABYRINTHE"),
    (21, "j21", "CRYSTAL CATCH"),
    (22, "j22", "REACTION 80"),
    (23, "j23", "AIGUILLAGES"),
    (24, "j24", "BOSS RUSH"),
    (25, "j25", "CHAMPIONNAT"),
)

GIFT = (
    "..kkk......kkk..",
    ".kyyyk....kyyyk.",
    ".kyYyyk..kyyYyk.",
    "..kyYyykkyyYyk..",
    "...kkyyyyyykk...",
    "kkkkkkkyykkkkkkk",
    "kwrrrrryYrrrrrRk",
    "kRRRRRRyYRRRRRRk",
    "kkkkkkkyykkkkkkk",
    ".kwrrrryYrrrrRk.",
    ".krrrrryYrrrrRk.",
    ".krrrrryYrrrrRk.",
    ".krrrrryYrrrrRk.",
    ".kRRRRRyYRRRRRk.",
    ".kkkkkkkkkkkkkk.",
)
GIFT_PAL = {
    "k": rgb(30, 10, 40),
    "r": rgb(230, 40, 60),
    "R": rgb(150, 20, 50),
    "w": rgb(255, 150, 160),
    "y": rgb(255, 215, 40),
    "Y": rgb(200, 140, 20),
}
MINI = (
    ".yy...yy.",
    "y..y.y..y",
    ".yyyyyyy.",
    "RRRRyRRRR",
    "rrrryrrrr",
    ".rrryrrr.",
    ".rrryrrr.",
    ".rrryrrr.",
    ".RRRyRRR.",
)
LOCK = ("..kkk..", ".k...k.", ".k...k.", "ggggggg", "gggkggg", "gggkggg", "ggggggg")
LOCK_PAL = {"k": GREY, "g": rgb(90, 90, 110)}

MOIS_DEC = "DECEMBRE"
_minis = {}


def title(day):
    return GAMES[day - 1][2]


def mini(bg, s=1):
    key = (bg, s)
    if key not in _minis:
        _minis[key] = sprite(MINI, GIFT_PAL, s, bg)
    return _minis[key]


def sync(rec, today):
    """En decembre, memorise les jours passes : ils restent jouables apres Noel."""
    if today[1] != 12:
        return
    opened = rec.get("open") or []
    changed = False
    for k in range(1, min(today[2], 25) + 1):
        if k not in opened:
            opened.append(k)
            changed = True
    if changed:
        rec["open"] = opened
        arcade.save_rec(rec)


def unlocked(rec, day, today):
    if day == 1 or rec.get("test") or day in (rec.get("open") or ()):
        return True
    return today[1] == 12 and today[2] >= day


def due(rec, today):
    """Jour dont le cadeau s'affiche tout seul aujourd'hui, sinon 0."""
    if today[1] != 12 or today[2] > 25:
        return 0
    if rec.get("seen") == "%04d-%02d-%02d" % today:
        return 0
    return today[2]


def mark_seen(rec, today):
    rec["seen"] = "%04d-%02d-%02d" % today
    arcade.save_rec(rec)


def _text_c(t, s, y, color, scale=1, shadow=None):
    x = (W - len(s) * 8 * scale) // 2
    if shadow is not None:
        draw_text(t, s, x + scale, y + scale, shadow, None, scale)
    draw_text(t, s, x, y, color, None, scale)


def _wait_release(touch):
    while touch.point():
        time.sleep_ms(20)


def _inside(pt, box, m=6):
    x, y, w, h = box
    return x - m <= pt[0] < x + w + m and y - m <= pt[1] < y + h + m


# --- fenetre cadeau -------------------------------------------------------
BOX = (16, 56, 208, 212)
CLOSE = (194, 58, 28, 22)
GIFT_S = 5
GIFT_XY = ((W - 16 * GIFT_S) // 2, 108)


def _button(t, box, label, bg, fg):
    x, y, w, h = box
    t.fill_rect(x, y, w, h, bg)
    t.rect(x, y, w, h, arcade.CREAM)
    draw_text(t, label, x + (w - len(label) * 8) // 2, y + (h - 8) // 2, fg, None, 1)


def _close_button(t):
    x, y, w, h = CLOSE
    t.fill_rect(x, y, w, h, RED)
    t.rect(x, y, w, h, WHITE)
    cx, cy = x + w // 2, y + h // 2
    for k in range(-5, 6):
        t.fill_rect(cx + k - 1, cy + k, 3, 1, WHITE)
        t.fill_rect(cx - k - 1, cy + k, 3, 1, WHITE)


def popup(t, touch, day, note=False):
    """Fenetre du jour : toucher le cadeau lance le jeu, la croix ferme.
    Renvoie "play", "note" ou None."""
    rec = arcade.load_rec()
    x, y, w, h = BOX
    for k in range(1, 7):
        ww, hh = w * k // 6, h * k // 6
        t.rect(x + (w - ww) // 2, y + (h - hh) // 2, ww, hh, arcade.REDP if k % 2 else arcade.TEAL)
        time.sleep_ms(20)
    t.fill_rect(x, y, w, h, arcade.SLATE)
    t.rect(x, y, w, h, arcade.TEAL)
    t.rect(x + 2, y + 2, w - 4, h - 4, arcade.REDP)
    for i, c in enumerate(arcade.BANDS):
        t.fill_rect(x + 4, y + 4 + i * 3, w - 8, 3, rgb(*c))
    _close_button(t)
    _text_c(t, "%d %s" % (day, MOIS_DEC), y + 26, arcade.CREAM, 2, arcade.REDP)
    gift = line_sprite(GIFT, GIFT_PAL, GIFT_S, arcade.SLATE, 3, 3)
    gx, gy = GIFT_XY
    blit_lines(t, gift, gx - 3, gy - 3)
    played = day in (rec.get("played") or ())
    _text_c(t, title(day) if played else "SURPRISE !", y + 150, arcade.CREAM)
    best = int(rec.get(str(day), 0))
    if best:
        _text_c(t, "RECORD %06d" % best, y + 164, GREY)
    play_box = (x + w - 90, y + h - 30, 80, 22)
    note_box = (x + 10, y + h - 30, 80, 22)
    _button(t, play_box, "JOUER", rgb(40, 150, 70), WHITE)
    if note:
        _button(t, note_box, "NOTE", arcade.TEAL, arcade.CREAM)
    gbox = (gx, gy, 16 * GIFT_S, 15 * GIFT_S)
    _wait_release(touch)
    last = 0
    on = False
    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, last) > 450:
            last = now
            on = not on
            t.fill_rect(x + 6, y + 134, w - 12, 8, arcade.SLATE)
            if on:
                _text_c(t, "TOUCHE LE CADEAU", y + 134, arcade.CREAM)
        pt = touch.point()
        if pt:
            _wait_release(touch)
            if _inside(pt, CLOSE, 10):
                return None
            if _inside(pt, gbox) or _inside(pt, play_box, 2):
                _open_anim(t, gift, day)
                return "play"
            if note and _inside(pt, note_box, 2):
                return "note"
        time.sleep_ms(25)


def _open_anim(t, gift, day):
    sfx = arcade.Sfx()
    gx, gy = GIFT_XY
    for k in range(8):
        dx = (3, -3, 2, -2, 3, -3, 1, 0)[k]
        blit_lines(t, gift, gx - 3 + dx, gy - 3)
        sfx.tone(300 + k * 60, 40)
        time.sleep_ms(45)
    t.fill_rect(gx - 6, gy - 3, gift[1] + 6, gift[2], arcade.SLATE)
    cx, cy = gx + 40, gy + 36
    cols = (arcade.REDP, arcade.CREAM, arcade.TEAL, WHITE, rgb(226, 82, 65), rgb(96, 148, 182))
    parts = []
    for i in range(28):
        a = random.random() * 6.283
        v = 2 + random.random() * 5
        parts.append([cx, cy, v * math.cos(a), v * math.sin(a), cols[i % len(cols)]])
    x0, y0, x1, y1 = BOX[0] + 4, BOX[1] + 60, BOX[0] + BOX[2] - 8, BOX[1] + 146
    for f in range(12):
        sfx.tone(700 + f * 90, 30)
        for p in parts:
            t.fill_rect(int(p[0]), int(p[1]), 3, 3, arcade.SLATE)
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.25
            if x0 <= p[0] < x1 and y0 <= p[1] < y1:
                t.fill_rect(int(p[0]), int(p[1]), 3, 3, p[4])
        time.sleep_ms(35)
    t.fill_rect(BOX[0] + 4, BOX[1] + 56, BOX[2] - 8, 110, arcade.SLATE)
    name = title(day)
    _text_c(t, name, BOX[1] + 94, arcade.CREAM, 2 if len(name) <= 12 else 1, arcade.REDP)
    sfx.tune(arcade.START)
    time.sleep_ms(500)
    sfx.off()


# --- lancement ------------------------------------------------------------
def launch(t, touch, day):
    rec = arcade.load_rec()
    played = rec.get("played") or []
    if day not in played:
        played.append(day)
        rec["played"] = played
        arcade.save_rec(rec)
    rec = None
    mod = GAMES[day - 1][1]
    gc.collect()
    if mod is None:
        _soon(t, touch, day)
        return
    err = None
    try:
        m = __import__(mod)
        if mod == "game":
            m.play(t, touch)
        else:
            m.play(t, touch, day)
    except Exception as e:
        err = e
    finally:
        m = None
        for g in GAMES:
            if g[1]:
                sys.modules.pop(g[1], None)
        gc.collect()
    if err is not None:
        import store

        sys.print_exception(err)
        store.log_error(err, "jeu " + mod)
        _oops(t, touch, day, isinstance(err, MemoryError))


def _oops(t, touch, day, memory):
    t.forget_window()
    t.fill(arcade.SLATE)
    for i, c in enumerate(arcade.BANDS):
        t.fill_rect(0, 60 + i * 3, W, 3, rgb(*c))
    _text_c(t, "JOUR %d" % day, 90, arcade.CREAM, 2)
    _text_c(t, "MEMOIRE PLEINE" if memory else "LE JEU A PLANTE", 140, RED, 2)
    _text_c(t, "REESSAIE DANS UN MOMENT" if memory else "C'EST NOTE DANS LE JOURNAL", 180, arcade.CREAM)
    _text_c(t, "TOUCHE POUR REVENIR", 280, arcade.CREAM)
    _wait_release(touch)
    while not touch.point():
        time.sleep_ms(30)
    _wait_release(touch)


def _soon(t, touch, day):
    t.fill(arcade.SLATE)
    for i, c in enumerate(arcade.BANDS):
        t.fill_rect(0, 60 + i * 3, W, 3, rgb(*c))
    _text_c(t, "JOUR %d" % day, 90, arcade.CREAM, 2)
    _text_c(t, title(day), 130, arcade.CREAM, 2, arcade.REDP)
    _text_c(t, "EN PREPARATION", 180, arcade.CREAM)
    _text_c(t, "IL ARRIVE BIENTOT !", 196, GREY)
    _text_c(t, "TOUCHE POUR REVENIR", 280, arcade.CREAM)
    _wait_release(touch)
    while not touch.point():
        time.sleep_ms(30)
    _wait_release(touch)


# --- salle d'arcade (onglet JEU) -----------------------------------------
CELL_W = 46
CELL_H = 48
GRID_Y = 46
BACK = (0, 292, W, 28)


def _cell_box(day):
    r, c = divmod(day - 1, 5)
    return 5 + c * CELL_W, GRID_Y + r * CELL_H, CELL_W - 4, CELL_H - 4


def _draw_sound(t, rec):
    t.fill_rect(4, 38, 32, 8, arcade.SLATE)
    draw_text(t, "MUET" if rec.get("muet") else "SON", 4, 38, GREY if rec.get("muet") else arcade.CREAM, None, 1)


def _draw_menu(t, rec, today, sound=False, feed=None):
    """feed : appele apres chaque case (dessin complet ~3 s, la musique n'a que 1,5 s d'avance)."""
    t.fill(arcade.SLATE)
    for i, c in enumerate(arcade.BANDS):
        t.fill_rect(0, i * 3, W, 3, rgb(*c))
    _text_c(t, "CALENDAR GAME", 20, arcade.CREAM, 2, arcade.REDP)
    if rec.get("test"):
        draw_text(t, "TEST", 204, 38, RED, None, 1)
    if sound:
        _draw_sound(t, rec)
    played = rec.get("played") or ()
    door = rgb(14, 42, 54)
    lock = sprite(LOCK, LOCK_PAL, 2, arcade.SLATE)
    for day in range(1, 26):
        x, y, w, h = _cell_box(day)
        s = str(day)
        if unlocked(rec, day, today):
            bg = door
            t.fill_rect(x, y, w, h, bg)
            t.rect(x, y, w, h, arcade.REDP if day != today[2] or today[1] != 12 else arcade.CREAM)
            g = mini(bg, 2)
            t.blit(g[0], x + (w - g[1]) // 2, y + 5, g[1], g[2])
            draw_text(t, s, x + (w - len(s) * 8) // 2, y + 28, arcade.CREAM if day in played else WHITE, None, 1)
        else:
            bg = arcade.SLATE
            t.fill_rect(x, y, w, h, bg)
            t.rect(x, y, w, h, rgb(30, 58, 72))
            t.blit(lock[0], x + (w - lock[1]) // 2, y + 6, lock[1], lock[2])
            draw_text(t, s, x + (w - len(s) * 8) // 2, y + 28, GREY, None, 1)
        if feed:
            feed()
    bx, by, bw, bh = BACK
    t.fill_rect(bx + 2, by + 2, bw - 4, bh - 4, arcade.REDP)
    t.rect(bx + 2, by + 2, bw - 4, bh - 4, arcade.CREAM)
    _text_c(t, "RETOUR AU CALENDRIER", by + 10, arcade.CREAM)


def menu(t, touch, today):
    """Grille des 25 jours, en musique (coupee pendant les jeux, qui ont leurs sons).
    Un appui long sur le titre bascule le mode test (tous les jours ouverts), pratique
    avant decembre ; un appui court sur SON / MUET coupe ou remet la musique."""
    import musique

    rec = arcade.load_rec()
    sync(rec, today)
    music = musique.Music()
    sound = musique.available()
    if sound and not rec.get("muet"):
        music.start()
    try:
        _draw_menu(t, rec, today, sound, music.feed)
        _wait_release(touch)
        while True:
            music.feed()
            pt = touch.point()
            if not pt:
                time.sleep_ms(25)
                continue
            if pt[1] < 42:
                t0 = time.ticks_ms()
                held = False
                while touch.point():
                    music.feed()
                    if time.ticks_diff(time.ticks_ms(), t0) > 2000:
                        rec["test"] = not rec.get("test")
                        arcade.save_rec(rec)
                        _draw_menu(t, rec, today, sound, music.feed)
                        held = True
                        break
                    time.sleep_ms(30)
                _wait_release(touch)
                if sound and not held and pt[0] < 60:
                    rec["muet"] = not rec.get("muet")
                    arcade.save_rec(rec)
                    if rec["muet"]:
                        music.stop()
                    else:
                        music.start()
                    _draw_sound(t, rec)
                continue
            _wait_release(touch)
            if _inside(pt, BACK, 0):
                return
            for day in range(1, 26):
                if _inside(pt, _cell_box(day), 1):
                    if unlocked(rec, day, today):
                        rec = None
                        music.stop()
                        launch(t, touch, day)
                        rec = arcade.load_rec()
                        if sound and not rec.get("muet"):
                            music.start()
                        _draw_menu(t, rec, today, sound, music.feed)
                    break
    finally:
        music.stop()
