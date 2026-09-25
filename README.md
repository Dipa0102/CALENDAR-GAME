<p align="center"><img src="logo.webp" alt="Calendar Game by Parchap" width="480"></p>

# Calendar Game

Une mini-télé rétro à écran tactile. Toute l'année, c'est un agenda avec la météo de la semaine. Du 1<sup>er</sup> au 25 décembre, c'est un calendrier de l'Avent : chaque jour, une fenêtre cadeau s'ouvre sur un jeu d'arcade façon années 80.

Le programme est écrit en MicroPython pour la carte **E32R28T**, une carte ESP32 avec écran tactile 2,8" de la famille « Cheap Yellow Display ». La page de présentation du projet est [`index.html`](index.html), publiée avec GitHub Pages.

| Calendrier | Météo | Fenêtre cadeau |
|:---:|:---:|:---:|
| <img src="docs/calendrier.png" width="220" alt="Page calendrier"> | <img src="docs/meteo.png" width="220" alt="Page météo"> | <img src="docs/avent_cadeau.png" width="220" alt="Fenêtre cadeau du 9 décembre"> |
| **Calendrier de l'Avent** | **Jour 1 : Magic Harry** | **Jour 9 : Turbo 80** |
| <img src="docs/avent_grille.png" width="220" alt="Grille des 25 portes"> | <img src="docs/jeu_magic_harry.png" width="220" alt="Écran titre de Magic Harry"> | <img src="docs/jeu_turbo80.png" width="220" alt="Jeu Turbo 80"> |

## Fonctionnalités

- **Calendrier (onglet CAL)** : le mois avec l'icône météo de chaque jour, l'heure et la jauge de batterie dans le bandeau, les trois prochains événements en bas de l'écran et le compte à rebours jusqu'à la première porte de l'Avent.
- **Notes** : une note par jour, saisie au clavier tactile, avec cinq thèmes (anniversaire, événement, oubli, rappel, tâche).
- **Météo (onglet METEO)** : température actuelle et prévisions sur 7 jours (mini et maxi) pour la ville choisie. La ville se cherche par son nom. L'heure et la météo se mettent à jour toutes seules par le Wi-Fi.
- **Calendrier de l'Avent** : du 1<sup>er</sup> au 25 décembre, une fenêtre cadeau s'ouvre au premier allumage de la journée. Un bouton croix permet de la fermer sans jouer. Chaque jeu se lance aussi depuis sa case du calendrier. Les portes s'ouvrent à leur date, et un jeu déjà ouvert reste jouable ensuite.
- **Jeux (onglet JEU)** : la salle d'arcade, avec le record de chaque jeu enregistré sur la carte. Le jour 1 est jouable toute l'année. Un appui long de 2 secondes sur le titre de la salle active un mode test qui débloque tous les jeux.
- **Réglages (onglet REGL)** : heure, date et fuseau horaire, synchronisation par Internet, choix du réseau Wi-Fi, saisie de l'heure au clavier (CLAVIER) et calibration de l'écran tactile (POINTEUR).

### Les jeux

| Jour | Jeu | Principe |
|---:|---|---|
| 1 | Magic Harry | Casse-briques magique |
| 2 | Star Raid | Tir vertical, le vaisseau suit le doigt |
| 3 | Serpent 80 | Le serpent part vers le doigt : manger sans se mordre |
| 4 | Ping 80 | Duel de raquettes contre l'ordinateur, premier à 7 |
| 7 | Route 80 | Traverser deux routes sans se faire écraser |
| 8 | Bomb Dodge | Esquiver les bombes et ramasser les pièces |
| 9 | Turbo 80 | Course vue de dessus, doubler sans toucher |
| 10 | Hélico 80 | Doigt posé, l'hélico monte ; doigt levé, il descend |
| 11 | Paires 80 | Retrouver les paires avant la fin du temps |
| 13 | Cibles 80 | Toucher les oiseaux avant qu'ils s'envolent |
| 21 | Crystal Catch | Attraper les cristaux, éviter les bombes |
| 22 | Réaction 80 | Toucher la case qui s'allume, de plus en plus vite |

Les autres jours (5, 6, 12, 14 à 20, 23 à 25) affichent « EN PRÉPARATION ».

## Matériel

### La carte

| | |
|---|---|
| Modèle | E32R28T, vendue par LCDWIKI sous le nom « 2.8inch ESP32-32E Display » |
| Processeur | ESP32-D0WD-V3 (module ESP32-32E), 2 cœurs à 240 MHz |
| Mémoire | 520 Ko de RAM, sans PSRAM, 4 Mo de flash |
| Radio | Wi-Fi 2,4 GHz (802.11 b/g/n) et Bluetooth 4.2, classique et BLE (le Bluetooth n'est pas utilisé) |
| Écran | TFT couleur 2,8", 240 × 320 pixels, contrôleur ILI9341 en SPI |
| Tactile | Résistif, contrôleur XPT2046 |
| USB | USB-C, convertisseur série CH340C |
| Son | Sortie haut-parleur avec amplificateur |
| Stockage | Lecteur microSD (pas utilisé par le programme) |
| Alimentation | 5 V par l'USB-C, ou batterie LiPo 1S avec chargeur TP4054 intégré |

### Brochage utilisé par le programme

| Fonction | Broches (GPIO) |
|---|---|
| Écran ILI9341 (SPI matériel) | SCK 14, MOSI 13, MISO 12, CS 15, DC 2, rétroéclairage 21 |
| Tactile XPT2046 (SPI logiciel) | SCK 25, MOSI 32, MISO 39, CS 33 |
| Haut-parleur | Signal PWM sur 26, amplificateur activé par 4 à l'état bas |
| Tension de la batterie | 34 (entrée analogique, derrière un pont diviseur par 2) |
| microSD (libre) | CS 5, SCK 18, MISO 19, MOSI 23 |
| Connecteur d'extension (libre) | 35 (entrée seulement), 27, 3,3 V, GND |

### Batterie

La carte fonctionne sur batterie et la recharge par l'USB-C. On peut laisser la batterie branchée en permanence, même avec l'USB : quand l'USB est branché, un transistor isole la batterie du reste de la carte, l'USB alimente la carte et la batterie ne fait que se charger.

| | |
|---|---|
| Type | LiPo ou Li-ion à **un seul élément (1S)** : 3,7 V nominal, 4,2 V chargée, avec circuit de protection intégré |
| Capacité | 300 mAh minimum (le courant de charge est d'environ 290 mA), 1000 mAh ou plus conseillé |
| Connecteur | 2 broches au pas de 1,25 mm (type MX1.25) : **rouge = +**, **noir = −** |
| Charge | Puce TP4054, environ 290 mA, arrêt à 4,2 V |
| Autonomie | Pas encore mesurée sur une décharge complète |

> [!WARNING]
> Vérifie la polarité au multimètre avant de brancher une batterie : un connecteur inversé grille la carte. Ne branche jamais sur la prise batterie une LiPo 2S (7,4 V), une batterie LiFePO4, des piles ou une alimentation 5 V.

#### La jauge de batterie

Le module [`battery.py`](firmware/battery.py) affiche le pourcentage à droite du bandeau du calendrier :

- **Sur USB** : l'icône est verte et se remplit en boucle, le pourcentage est en vert. À 100 %, l'icône reste pleine.
- **Sur batterie** : l'icône est fixe. La jauge est verte au-dessus de 50 %, jaune entre 20 et 50 %, rouge en dessous de 20 %.

La carte n'a aucun signal qui indique si l'USB est branché. Le programme le devine à partir de la tension de la batterie :

- **Au branchement et au débranchement**, la tension saute d'environ 65 mV : elle monte quand la charge commence, elle baisse quand la batterie se met à alimenter la carte. Le sens du saut indique si l'USB vient d'être branché ou débranché.
- **Au démarrage**, le programme éteint six fois le rétroéclairage pendant 25 ms, pendant que l'écran est encore noir. Sur USB, la batterie est isolée de la carte et sa tension ne bouge pas. Sur batterie seule, elle remonte de quelques millivolts parce que la batterie débite moins. L'effet étant proche du bruit de mesure, le programme retient la valeur médiane des six essais.
- **Toutes les 5 minutes**, il compare la tension à celle d'il y a 10 minutes. Si elle monte alors qu'il se croyait sur batterie, ou baisse alors qu'il se croyait sur USB, il corrige.

Le pourcentage vient de la tension mesurée sur IO34, corrigée de l'effet du courant : on retire 45 mV pendant la charge et on ajoute 25 mV sur batterie. La tension corrigée est ensuite convertie en pourcentage par cette courbe de décharge LiPo :

| Tension (V) | 4,20 | 4,10 | 4,00 | 3,90 | 3,80 | 3,75 | 3,70 | 3,65 | 3,60 | 3,50 | 3,40 | 3,30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Charge | 100 % | 90 % | 79 % | 67 % | 52 % | 42 % | 30 % | 18 % | 10 % | 4 % | 1 % | 0 % |

Pour éviter que le chiffre fasse du yo-yo, il ne peut que baisser sur batterie et que monter en charge. C'est une estimation à 5 ou 10 % près, surtout pendant la charge.

## Installation

### Ce qu'il faut

- La carte E32R28T et un câble USB-C qui transmet les données (certains câbles ne font que charger).
- Python 3.11 ou plus récent sur l'ordinateur (Windows, macOS ou Linux).
- Sous Windows, le pilote CH340 si la carte n'apparaît pas comme port COM.
- Les outils Python :

```sh
pip install -r firmware/requirements.txt
```

Les scripts utilisent le port `COM4` par défaut. Si ta carte est sur un autre port, définis la variable `PORT_CARTE` avant de lancer les scripts :

```powershell
$env:PORT_CARTE = "COM5"            # PowerShell
```

```sh
export PORT_CARTE=/dev/ttyUSB0      # macOS / Linux
```

### Première installation

Cette commande **efface complètement la carte** : elle télécharge MicroPython 1.29.0, l'installe, puis copie le programme.

```sh
cd firmware
python flash.py
```

### Mettre à jour le programme

Cette commande garde les notes, les réglages et les records. Elle compile les modules en `.mpy`, les copie sur la carte et la redémarre.

```sh
cd firmware
python deploy.py
```

### Premier démarrage

1. Dans **REGL**, touche **WIFI**, choisis ton réseau et tape le mot de passe sur le clavier de l'écran.
2. Dans **METEO**, touche **VILLE** et cherche ta ville par son nom.
3. L'heure se règle toute seule par Internet. Pour la France, le fuseau est +2 en été et +1 en hiver (réglage FUSEAU dans REGL).

## Organisation du code

Tout le programme est dans [`firmware/`](firmware). Les fichiers de la carte sont compilés en `.mpy` par `deploy.py`, sauf `boot.py`, `boardio.py` et `main.py`, qui sont copiés tels quels.

| Fichier | Rôle |
|---|---|
| `boot.py` | Se connecte au Wi-Fi et cherche les réseaux dès le démarrage, avant de charger le reste : ensuite la mémoire serait trop morcelée pour le pilote Wi-Fi |
| `boardio.py` | Garde les objets créés par `boot.py` (Wi-Fi, bus SPI) |
| `main.py` | Lance l'application |
| `kartcal.py` | L'application : calendrier, notes, météo, réglages, clavier, boucle principale |
| `ili9341.py` | Pilote de l'écran |
| `font8.py` | Police 8 × 8 pixels et affichage rapide du texte |
| `xpt2046.py` | Lecture et calibration de l'écran tactile |
| `store.py` | Enregistrement des réglages et des notes sur la carte |
| `net.py` | Wi-Fi, heure par Internet, recherche de ville et météo |
| `battery.py` | Mesure de la batterie, détection de l'USB, pourcentage |
| `arcade.py` | Moteur commun des jeux : sprites, score, sons, records |
| `advent.py` | Calendrier de l'Avent : fenêtre cadeau, grille des portes, lancement des jeux |
| `game.py`, `j02.py` … `j22.py` | Les jeux (`game.py` est le jour 1) |
| `logo.raw`, `wxn18.raw`, `wxp18.raw`, `wxa64.raw` | Logo et icônes météo, déjà converties au format de l'écran |

Outils à lancer sur l'ordinateur :

| Fichier | Rôle |
|---|---|
| `flash.py` | Installe MicroPython puis le programme (efface la carte) |
| `deploy.py` | Met à jour le programme sans effacer les données |
| `restore_backup.py` | Recopie des réglages et des notes sauvegardés dans `firmware/backup_carte/` |
| `make_logo.py` | Convertit `logo.png` en `logo.raw` |
| `make_wx.py` | Découpe la planche `meteo_icones.png` en icônes `wx*.raw` |

Les réglages (`config.json`, `wifi.json`, avec le mot de passe Wi-Fi), les notes (`notes.json`) et les records (`records.json`) restent sur la carte. Ils ne font pas partie du dépôt, et le fichier `.gitignore` les exclut.

### Choix techniques

- **Modules précompilés** : la carte n'a pas assez de mémoire pour compiler elle-même les gros fichiers, donc `deploy.py` les compile sur l'ordinateur avec `mpy-cross`.
- **Météo en HTTP** : une connexion HTTPS demande environ 40 Ko de mémoire d'un seul bloc, que la carte n'a plus une fois le programme chargé. Open-Meteo accepte le HTTP simple et ne demande pas de clé.
- **Affichage** : les icônes sont préparées sur l'ordinateur pour chaque couleur de fond, et le texte passe par une fonction compilée en code machine (`@micropython.viper`). Un rafraîchissement complet du calendrier prend environ 0,7 s.

## Crédits

- [MicroPython](https://micropython.org/)
- Données météo : [Open-Meteo](https://open-meteo.com/) (licence CC BY 4.0), avec les modèles de Météo-France (AROME et ARPEGE) pour les 4 premiers jours
- Police 8 × 8 pixels du domaine public
- Icônes météo : planche générée par IA, découpée et convertie par `make_wx.py`
