#!/usr/bin/env python3
"""Dateikopf von Version 1.7 berichtigen (Stand 2026-10-15).

Der Kopf bis dahin war in drei Punkten falsch:
  - `1 SOUR webtreesAnd-demo` (später `PYTHON`): SOUR nennt das Programm, mit dem die Datei erstellt wurde. Das sind
    die Python-Skripte dieses Repos, weder webtrees noch eine App. Der Name des Programms, nicht der des Inhalts.
  - `1 SUBM` fehlte, ist in GEDCOM 5.5.1 aber Pflicht.
  - `_ADDENDUM GEDCOM-L` mit `VERS 2.0`: das Addendum empfiehlt (Kap. 7.3) `_ADDENDUM GEDCOM-L Addendum`,
    Version R2 vom 2020-12-01, und https://genealogy.net/GEDCOM.
Die Daten bleiben unverändert, die Version bleibt 1.7.

Aufruf:  python3 werkzeuge/kopf.py versionen/falkenrath-1.7.ged
"""
import sys

sys.path.insert(0, sys.path[0])
import ged  # noqa: E402
from ged import Node  # noqa: E402

PATH = sys.argv[1]
root = ged.parse(open(PATH, encoding='utf-8').read())
head = root.children[0]
assert head.tag == 'HEAD' and head.first('SOUR').val('VERS') == '1.7', 'nur für Version 1.7'
assert head.first('SUBM') is None, 'Kopf ist schon berichtigt'

sour = Node('SOUR', 'PYTHON')
sour.add('VERS', '1.7')
sour.add('NAME', 'Python-Skripte')
corp = sour.add('CORP', 'Thomas Bugge')
corp.add('WWW', 'https://github.com/thobgg/falkenrath-demo-tree')

gedc = Node('GEDC')
vers = gedc.add('VERS', '5.5.1')
add = vers.add('_ADDENDUM', 'GEDCOM-L Addendum')
add.add('VERS', 'R2 (2020-12-01)')
add.add('WWW', 'https://genealogy.net/GEDCOM')
gedc.add('FORM', 'LINEAGE-LINKED')

note = Node('NOTE', 'Demo-Stammbaum Familie Falkenrath.')
note.add('CONT', 'Alle Personen und Lebensdaten sind frei erfunden. Daten und Bilder: CC0.')

head.children = [sour, Node('DATE', '15 OCT 2026'), Node('SUBM', '@U1@'), Node('FILE', 'falkenrath-1.7.ged'),
                 Node('COPR', 'CC0 1.0'), gedc, Node('CHAR', 'UTF-8'), Node('LANG', 'German'), note]

subm = Node('SUBM', xref='@U1@')
subm.add('NAME', 'Thomas Bugge')
subm.add('WWW', 'https://github.com/thobgg/falkenrath-demo-tree')
root.children.insert(1, subm)

open(PATH, 'w', encoding='utf-8').write(ged.serialize(root))
print('\n'.join(head.lines() + subm.lines()))
