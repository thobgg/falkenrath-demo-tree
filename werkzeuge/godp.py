#!/usr/bin/env python3
"""Demo-Stammbaum 1.2 -> 1.3: freie Paten/Trauzeugen als GEDCOM-L-Tags (Stand 2026-10-01).

    2 NOTE Paten: A, Beruf zu Ort; B, …     ->   2 _GODP A, Beruf zu Ort
                                                  2 _GODP B, …
    2 NOTE Trauzeugen: A, …; B, …           ->   2 _WITN A, …  (je Person eine Zeile)

So schreiben es manche Programme (eine Zeile je Person), webtrees kennt beide Tags als GEDCOM-L-Tags.
Testfälle: zwei Taufen und eine Heirat behalten die alte Notiz-Form.

Aufruf:  python3 werkzeuge/godp.py falkenrath.ged
"""
import sys

sys.path.insert(0, sys.path[0])
import ged  # noqa: E402
from ged import Node  # noqa: E402

PATH = sys.argv[1]
text = open(PATH, encoding='utf-8').read()
if '\n2 VERS 1.2\n' not in text[:5000]:
    sys.exit('Abbruch: godp.py läuft nur auf Version 1.2.')
root = ged.parse(text)

KEEP_NOTE = {'@I140@', '@I141@'}   # Taufen mit alter Notiz-Form (Testfall)
KEEP_NOTE_FAM = {'@F60@'}           # Heirat mit alter Notiz-Form (Testfall)
PREFIX = {'CHR': ('Paten: ', '_GODP'), 'BAPM': ('Paten: ', '_GODP'), 'MARR': ('Trauzeugen: ', '_WITN')}

count = {'_GODP': 0, '_WITN': 0, 'Notizen umgewandelt': 0, 'Notizen behalten': 0}
for r in root.children:
    if r.tag not in ('INDI', 'FAM'):
        continue
    for ev in r.children:
        if ev.tag not in PREFIX:
            continue
        prefix, tag = PREFIX[ev.tag]
        for n in list(ev.all('NOTE')):
            if not (n.value or '').startswith(prefix) or n.children:
                continue
            if r.xref in KEEP_NOTE | KEEP_NOTE_FAM:
                count['Notizen behalten'] += 1
                continue
            people = [p.strip() for p in n.value[len(prefix):].split(';') if p.strip()]
            i = ev.children.index(n)
            ev.children[i:i + 1] = [Node(tag, p) for p in people]
            count[tag] += len(people)
            count['Notizen umgewandelt'] += 1

root.children[0].first('SOUR').first('VERS').value = '1.3'
open(PATH, 'w', encoding='utf-8').write(ged.serialize(root))
print(count)
