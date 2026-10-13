#!/usr/bin/env python3
"""Demo-Stammbaum 1.4 -> 1.5: Gäste ohne Datensatz im Gruppenbild der Hochzeit 1924 (Stand 2026-10-10).

hochzeit-1924.jpg (M135) zeigt jetzt zusätzlich den Trauzeugen Wilhelm Niebuhr (an F8 nur `2 _WITN`) und
einen unbekannten Gast. Die Aufstellungs-Notiz an M135 nennt alle 23 Abgebildeten an ihrem Platz.

Aufruf:  python3 werkzeuge/gruppenfoto_gaeste.py falkenrath.ged
"""
import sys

sys.path.insert(0, sys.path[0])
import ged  # noqa: E402

PATH = sys.argv[1]
text = open(PATH, encoding='utf-8').read()
if '\n2 VERS 1.4\n' not in text[:5000]:
    sys.exit('Abbruch: gruppenfoto_gaeste.py läuft nur auf Version 1.4.')
root = ged.parse(text)
recs = {r.xref: r for r in root.children if r.xref}

ROWS = [
    ('hinten', ['?', 'I79', 'I80', 'I28', 'I29', 'I72', 'I274', 'I105']),
    ('Mitte', ['I305', 'I63', 'I45', 'I44', 'Wilhelm Niebuhr (Trauzeuge)', 'I273', 'I271', 'I104']),
    ('vorn', ['I300', 'I39', 'I40', 'I21', 'I22', 'I42', 'I43']),
]


def name(x):
    if x == '?':
        return 'unbekannt'
    if f'@{x}@' in recs:
        return recs[f'@{x}@'].val('NAME').replace('/', '').strip()
    return x


m = recs['@M135@']
note = next(n for n in m.all('NOTE') if n.value == 'Aufstellung von links nach rechts')
note.children = []
for row, ids in ROWS:
    line = f'{row}: ' + ', '.join(name(x) for x in ids)
    assert len(line) < 240, line
    note.add('CONT', line)

root.children[0].first('SOUR').first('VERS').value = '1.5'
open(PATH, 'w', encoding='utf-8').write(ged.serialize(root))
print('Notiz an M135 neu:', len(note.children), 'Reihen')
