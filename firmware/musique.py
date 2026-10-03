"""Musique en boucle de la salle d'arcade (musique.adp). Fichier IMA ADPCM 4 bits, mono,
11025 Hz, fait par convert_music.py, joue sur le DAC de GPIO26 par le module C audio
du firmware maison. feed() doit etre appele au moins toutes les secondes. Sans module
audio ou sans fichier (firmware officiel), rien ne se passe."""

from machine import Pin

FILE = "musique.adp"
RATE = 11025
VOLUME = 200  # 0..256, niveau du reglage 6


def _saved_gain():
    try:
        import store

        return store.sound_gain()
    except Exception:
        return 4


def available(name=FILE):
    try:
        import os

        import audio  # noqa: F401

        os.stat(name)
        return True
    except Exception:
        return False


class Music:
    def __init__(self, name=FILE, volume=VOLUME):
        self.name = name
        self.volume = volume
        self.f = None
        self.buf = bytearray(512)
        self.off = self.n = 0

    def start(self):
        self.stop()
        try:
            import audio

            self.f = open(self.name, "rb")
            audio.start(RATE)
            audio.volume(_saved_gain())
        except Exception:
            self.stop()
            return False
        self.a = audio
        self.off = self.n = 0
        # Ampli du haut-parleur : actif a l'etat bas.
        Pin(4, Pin.OUT, value=0)
        self.feed()
        return True

    def feed(self):
        f = self.f
        if f is None:
            return
        a = self.a
        while True:
            if self.off >= self.n:
                self.off, self.n = 0, f.readinto(self.buf)
                if not self.n:
                    f.seek(0)
                    a.reset()
                    self.n = f.readinto(self.buf)
                    if not self.n:
                        self.stop()
                        return
            k = a.write(self.buf, self.off, self.n)
            self.off += k
            if self.off < self.n:
                return

    def stop(self):
        if self.f is not None:
            try:
                self.f.close()
            except Exception:
                pass
            self.f = None
            try:
                self.a.stop()
            except Exception:
                pass
            Pin(4, Pin.OUT, value=1)
