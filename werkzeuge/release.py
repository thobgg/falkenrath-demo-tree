#!/usr/bin/env python3
"""Release-Dateien bauen (Stand 2026-10-14).

    python3 werkzeuge/release.py <zielordner>

Erzeugt aus versionen/falkenrath-<v>.ged (GEDCOM 5.5.1) und media/:

  falkenrath-<v>.zip            GEDCOM 5.5.1: falkenrath-<v>.ged und alle Bilder im selben Ordner (die FILE-Angaben sind
                                nackte Dateinamen, so findet jedes Programm die Bilder), dazu README, FOTOS.md, LICENSE
  falkenrath-<v>.gdz            GEDZIP nach GEDCOM 7.0: gedcom.ged in GEDCOM 7.0 (werkzeuge/gedcom7.py) und die Bilder,
                                auf die es verweist, auf oberster Ebene
  falkenrath-<v>-gedcom7.ged    dieselbe GEDCOM-7.0-Datei einzeln

Die früheren Releases enthielten in der .gdz – wie der GEDZIP-Export von webtrees 2.2 – die GEDCOM-5.5.1-Datei;
nach dem Standard gehört in ein GEDZIP aber GEDCOM 7.
"""
import glob
import os
import re
import subprocess
import sys
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1])
os.makedirs(OUT, exist_ok=True)

ged551 = sorted(glob.glob(os.path.join(BASE, 'versionen', 'falkenrath-*.ged')))[-1]
text = open(ged551, encoding='utf-8').read()
version = re.search(r'^1 SOUR .*\n2 VERS (\S+)$', text, re.M).group(1)
media = sorted(f for f in os.listdir(os.path.join(BASE, 'media')) if not f.startswith('.'))
stamp = (2026, 1, 1, 0, 0, 0)        # feste Zeitstempel: gleiche Eingabe -> byte-gleiches Archiv


def add(z, name, path):
    info = zipfile.ZipInfo(name, stamp)
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, open(path, 'rb').read())


# GEDCOM 7.0
g7 = os.path.join(OUT, f'falkenrath-{version}-gedcom7.ged')
subprocess.run([sys.executable, os.path.join(BASE, 'werkzeuge', 'gedcom7.py'), ged551, g7], check=True,
               stdout=subprocess.DEVNULL)
refs = re.findall(r'^\d+ FILE (.+)$', open(g7, encoding='utf-8').read(), re.M)
missing = [r for r in refs if r not in media]
assert not missing, missing

with zipfile.ZipFile(os.path.join(OUT, f'falkenrath-{version}.zip'), 'w') as z:
    add(z, os.path.basename(ged551), ged551)
    for f in media:
        add(z, f, os.path.join(BASE, 'media', f))
    for f in ('README.md', 'README.en.md', 'FOTOS.md', 'LICENSE'):
        if os.path.exists(os.path.join(BASE, f)):
            add(z, f, os.path.join(BASE, f))

with zipfile.ZipFile(os.path.join(OUT, f'falkenrath-{version}.gdz'), 'w') as z:
    add(z, 'gedcom.ged', g7)
    for f in sorted(set(refs)):
        add(z, f, os.path.join(BASE, 'media', f))

for f in sorted(os.listdir(OUT)):
    print(f'{os.path.getsize(os.path.join(OUT, f)):>10}  {f}')
