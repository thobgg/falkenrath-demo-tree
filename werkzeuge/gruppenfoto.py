#!/usr/bin/env python3
"""Demo-Stammbaum 1.3 -> 1.4: Gruppenbild der Hochzeit 1924 (Stand 2026-10-10).

Das Bild hochzeit-1924.jpg (M135, an F8) ist jetzt ein Gruppenbild mit 21 Personen, montiert mit
werkzeuge/gruppenbild_montage.py. Jede abgebildete Person bekommt `1 OBJE @M135@`, das Medienobjekt
eine Notiz mit der Aufstellung (Reihe für Reihe von links nach rechts), wie auf der Rückseite alter Fotos.

Aufruf:  python3 werkzeuge/gruppenfoto.py falkenrath.ged
"""
import sys

sys.path.insert(0, sys.path[0])
import ged  # noqa: E402
from ged import Node  # noqa: E402

PATH = sys.argv[1]
text = open(PATH, encoding='utf-8').read()
if '\n2 VERS 1.3\n' not in text[:5000]:
    sys.exit('Abbruch: gruppenfoto.py läuft nur auf Version 1.3.')
root = ged.parse(text)
recs = {r.xref: r for r in root.children if r.xref}

MEDIA = '@M135@'
ROWS = [
    ('hinten', ['I79', 'I80', 'I28', 'I29', 'I72', 'I274', 'I105']),
    ('Mitte', ['I305', 'I63', 'I45', 'I44', 'I273', 'I271', 'I104']),
    ('vorn', ['I300', 'I39', 'I40', 'I21', 'I22', 'I42', 'I43']),
]


def name(x):
    return recs[f'@{x}@'].val('NAME').replace('/', '').strip()


linked = 0
for _, ids in ROWS:
    for x in ids:
        r = recs[f'@{x}@']
        if any(o.value == MEDIA for o in r.all('OBJE')):
            continue
        # hinter die vorhandenen OBJE, sonst vor FAMC/FAMS/SOUR/NOTE/CHAN
        objs = [i for i, c in enumerate(r.children) if c.tag == 'OBJE']
        if objs:
            pos = objs[-1] + 1
        else:
            pos = next((i for i, c in enumerate(r.children) if c.tag in ('FAMC', 'FAMS', 'SOUR', 'NOTE', 'CHAN')),
                       len(r.children))
        r.children.insert(pos, Node('OBJE', MEDIA))
        linked += 1

m = recs[MEDIA]
assert m.val('FILE') == 'hochzeit-1924.jpg', m.val('FILE')
note = m.add('NOTE', 'Aufstellung von links nach rechts')
for row, ids in ROWS:
    line = f'{row}: ' + ', '.join(name(x) for x in ids)
    assert len(line) < 240, line
    note.add('CONT', line)

root.children[0].first('SOUR').first('VERS').value = '1.4'
open(PATH, 'w', encoding='utf-8').write(ged.serialize(root))
print({'OBJE verknüpft': linked})
