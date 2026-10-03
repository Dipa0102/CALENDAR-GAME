"""Convertit un son (mp3, wav...) en fichier .adp joue par la carte.

    python convert_music.py chemin/vers/musique.mp3
    python convert_music.py oiseaux.wav meteo_soleil.adp --boucle
    python convert_music.py orage.wav meteo_orage.adp --duree 14.5 --boucle

Sortie par defaut : musique.adp, la musique de la salle d'arcade. Les ambiances meteo
de la page note s'appellent meteo_soleil.adp, meteo_pluie.adp et meteo_orage.adp.
--debut / --duree gardent un extrait (en secondes). --boucle fond la derniere demi-seconde
dans le debut, pour qu'un son d'ambiance tourne en boucle sans raccord audible.

.adp : IMA ADPCM 4 bits, mono, 11025 Hz (5,5 Ko par seconde), joue par le module C audio
du firmware maison. <nom>_apercu.wav : ce que la carte jouera.
Demande imageio-ffmpeg et numpy (pip install imageio-ffmpeg numpy).
"""
from __future__ import annotations

import argparse
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np

HERE = Path(__file__).resolve().parent
RATE = 11025
FADE = 0.5
# Le petit haut-parleur ne rend pas les basses : les retirer laisse plus de volume au reste.
FILTERS = "highpass=f=150,acompressor=threshold=0.05:ratio=6:attack=3:release=80:makeup=4,alimiter=limit=0.9"

STEPS = [
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
    50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130, 143, 157, 173, 190, 209, 230,
    253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963,
    1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327,
    3660, 4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487,
    12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767,
]
ADJUST = [-1, -1, -1, -1, 2, 4, 6, 8]


def decode_source(src: Path, start: float, length: float | None) -> np.ndarray:
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-ss", str(start), "-i", str(src)]
    if length:
        cmd += ["-t", str(length)]
    cmd += ["-af", FILTERS, "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"]
    pcm = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype="<i2")
    return pcm.astype(np.float64)


def make_loop(x: np.ndarray) -> np.ndarray:
    """La fin se fond dans le debut (puissance constante) : x[-1] de la boucle enchaine sur x[0]."""
    n = int(FADE * RATE)
    y = x[:-n].copy()
    t = np.linspace(0, np.pi / 2, n)
    y[:n] = y[:n] * np.sin(t) + x[-n:] * np.cos(t)
    return y


def normalize(x: np.ndarray) -> np.ndarray:
    return np.clip(x * (0.95 * 32767 / max(1.0, np.abs(x).max())), -32768, 32767).astype(np.int32)


def encode(samples: np.ndarray) -> tuple[bytes, list[int]]:
    """Meme etat que le decodeur de audio.c : predicteur 0, index 0, quartet bas d'abord."""
    pred = idx = 0
    nibbles = []
    out = []
    for s in samples.tolist():
        step = STEPS[idx]
        d = s - pred
        n = 8 if d < 0 else 0
        d = abs(d)
        diff = step >> 3
        if d >= step:
            n |= 4
            d -= step
            diff += step
        if d >= step >> 1:
            n |= 2
            d -= step >> 1
            diff += step >> 1
        if d >= step >> 2:
            n |= 1
            diff += step >> 2
        pred += -diff if n & 8 else diff
        pred = max(-32768, min(32767, pred))
        idx = max(0, min(88, idx + ADJUST[n & 7]))
        nibbles.append(n)
        out.append((pred >> 8) + 128)
    if len(nibbles) & 1:
        nibbles.append(0)
    data = bytes(nibbles[i] | (nibbles[i + 1] << 4) for i in range(0, len(nibbles), 2))
    return data, out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", type=Path)
    p.add_argument("sortie", nargs="?", default="musique.adp")
    p.add_argument("--debut", type=float, default=0.0)
    p.add_argument("--duree", type=float)
    p.add_argument("--boucle", action="store_true")
    args = p.parse_args()
    x = decode_source(args.source, args.debut, args.duree)
    if args.boucle:
        x = make_loop(x)
    data, preview = encode(normalize(x))
    out = HERE / args.sortie
    out.write_bytes(data)
    with wave.open(str(out.with_name(out.stem + "_apercu.wav")), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(RATE)
        w.writeframes(bytes(preview))
    rms = np.sqrt(np.mean((np.array(preview, dtype=np.float64) - 128) ** 2))
    print("%s : %d octets, %.1f s a %d Hz, niveau moyen %.0f/128" % (out.name, len(data), len(x) / RATE, RATE, rms))


if __name__ == "__main__":
    main()
