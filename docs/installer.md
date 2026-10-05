# Installer Calendar Game sur la carte

Ce texte suffit pour mettre le programme sur une carte **E32R28T** tout seul. Pas besoin de l’IDE Arduino, ni de compiler quoi que ce soit pour une première installation.

Le programme est écrit en **MicroPython**. On l’envoie avec **Python** et deux commandes. Le branchement (USB, batterie, haut-parleur) est dans [raccordement.md](raccordement.md).

## Ce qu’il te faut

- La carte E32R28T
- Un câble USB-C **qui transmet les données** (beaucoup de câbles ne font que charger : la carte s’allume mais l’ordinateur ne la voit pas)
- Un ordinateur Windows, macOS ou Linux
- **Python 3.11** ou plus récent ([python.org](https://www.python.org/downloads/))  
  À l’installation sous Windows, coche **Add python.exe to PATH**
- Sous Windows : le [pilote CH340](https://www.wch-ic.com/downloads/CH341SER_EXE.html) si aucun port COM n’apparaît
- Le dossier du projet, avec le sous-dossier `firmware`

## Étape 1 — Brancher et trouver le port

1. Branche la carte à l’ordinateur (batterie pas obligatoire).
2. L’écran doit s’allumer.
3. Note le nom du port :
   - **Windows** : Gestionnaire de périphériques → Ports (COM et LPT) → `USB-SERIAL CH340 (COMx)`. Souvent `COM4`.
   - **macOS / Linux** : en général `/dev/cu.usbserial-…` ou `/dev/ttyUSB0`.

Si rien n’apparaît : autre câble, autre prise USB, puis le pilote CH340. Relance l’ordinateur après le pilote.

## Étape 2 — Installer les outils Python

Ouvre un terminal dans le dossier `firmware` :

```sh
cd firmware
pip install -r requirements.txt
```

Si le port n’est pas `COM4`, dis-le **avant** les commandes suivantes.

Windows (PowerShell) :

```powershell
$env:PORT_CARTE = "COM5"
```

macOS / Linux :

```sh
export PORT_CARTE=/dev/ttyUSB0
```

## Étape 3 — Envoyer le programme

### Première fois sur une carte vide

```sh
python flash.py
```

Ça dure une ou deux minutes. La carte redémarre. Tu dois voir l’écran Calendar Game (logo, puis le bouton pour démarrer).

- S’il y a un fichier `firmware_calendar.bin` dans `firmware`, c’est **cette** version qui est écrite, **sans** effacer notes et réglages déjà sur la carte.
- S’il n’y est pas, le script télécharge MicroPython officiel, **efface** toute la carte, puis copie le programme.

### Plus tard, pour une mise à jour

Notes, Wi-Fi et records restent :

```sh
python deploy.py
```

Si tu as changé le code gelé (calendrier, jeux, etc.) et que tu reconstruis le firmware maison :

```sh
python build_firmware.py
python flash.py
```

`build_firmware.py` demande WSL + ESP-IDF la première fois. Ce n’est **pas** nécessaire pour juste installer le programme déjà fourni.

## Étape 4 — Premier allumage

1. **REGL** → **WIFI** → ton réseau **2,4 GHz** → mot de passe sur le clavier de l’écran.
2. **METEO** → **VILLE** → cherche ta ville.
3. L’heure se règle toute seule. Fuseau France : +1 en hiver, +2 en été (**FUSEAU** dans REGL).
4. Le volume va de **0** (muet) à **10** dans REGL.

iPhone : dans Partage de connexion, active **Maximiser la compatibilité**, et garde cet écran ouvert. Android : bande **2,4 GHz**, plutôt **WPA2**.

## Si ça bloque

| Problème | Quoi essayer |
|---|---|
| `could not open port COM4` | Mauvais numéro de port, ou câble sans données. Vérifie COMx et `PORT_CARTE`. |
| La carte s’allume, pas de port COM | Pilote CH340, autre câble, autre prise USB. |
| `flash.py` échoue au milieu | Débranche, rebranche, relance la même commande. Ferme Thonny / Arduino / un autre programme qui tient le port. |
| Écran noir après le flash | Attends 10 secondes. Si rien : `python flash.py` une seconde fois. |
| Pas de Wi-Fi | Uniquement le 2,4 GHz. Le 5 GHz est invisible pour cette carte. |

Un seul programme à la fois sur le port USB. Ferme l’IDE Arduino, Thonny ou le moniteur série avant `flash.py`.

## Quel logiciel pour modifier le code

Tu n’as **pas** besoin d’un IDE pour installer. Un éditeur + un terminal suffisent.

| Logiciel | Pour quoi |
|---|---|
| Un terminal + Python | **C’est la méthode prévue** : `flash.py` et `deploy.py` |
| Cursor, VS Code, Bloc-notes | Lire et changer les `.py` |
| Thonny | Voir les fichiers sur la carte (MicroPython). L’installation se fait quand même avec les scripts |

## Et l’IDE Arduino ?

**On ne peut pas envoyer ce programme avec l’IDE Arduino.**

Arduino attend un sketch en C++ (fichier `.ino`) et le bouton « Téléverser ». Calendar Game est du **MicroPython** : des fichiers `.py` qui tournent dans MicroPython. Arduino ne les compile pas et ne les copie pas.

| | IDE Arduino | Ce projet |
|---|---|---|
| Langage | C++ / `.ino` | MicroPython / `.py` |
| Envoi | Bouton Téléverser | `python flash.py` puis `python deploy.py` |
| Compatible ? | Non, tel quel | Oui |

**Si tu tiens à Arduino**, il faudrait tout réécrire (écran, tactile, calendrier, 25 jeux, météo, son). Ce n’est pas une option d’installation, c’est un autre logiciel.

Arduino IDE peut servir à **d’autres** programmes ESP32 sur la même carte. Dès que tu téléverses un sketch Arduino, MicroPython et Calendar Game sont écrasés. Pour revenir : `python flash.py` depuis ce dossier.

## Rappel des commandes

```sh
cd firmware
pip install -r requirements.txt
# $env:PORT_CARTE = "COM5"     # seulement si ce n'est pas COM4

python flash.py                # première installation
python deploy.py               # mises à jour, notes gardées
```
