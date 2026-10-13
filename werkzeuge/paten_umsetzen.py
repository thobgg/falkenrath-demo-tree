#!/usr/bin/env python3
"""Verschiebt Paten-ASSO (GEDCOM 5.5.1, Ebene 1) in die Taufe (webtrees-Stil).

    1 ASSO @I5@            ->   1 CHR
    2 RELA Godfather              ...
                                  2 _ASSO @I5@
                                  3 RELA Godparent

Aufruf:  python3 paten_umsetzen.py eingabe.ged ausgabe.ged
Unterstrukturen des ASSO (SOUR, NOTE …) wandern mit. Personen ohne CHR/BAPM
bleiben unverändert und werden am Ende aufgelistet.
"""
import re
import sys

PATEN = {'godfather', 'godmother', 'godparent', 'pate', 'patin', 'taufpate', 'taufpatin'}
TAUFE = ('CHR', 'BAPM')
NEU_RELA = 'Godparent'

src, dst = sys.argv[1], sys.argv[2]
raw = open(src, encoding='utf-8-sig').read()
nl = '\r\n' if '\r\n' in raw else '\n'
lines = raw.splitlines()


def level(l):
    return int(l.split(' ', 1)[0])


def records(lines):
    rec = []
    for l in lines:
        if l.startswith('0 ') and rec:
            yield rec
            rec = []
        rec.append(l)
    if rec:
        yield rec


out, verschoben, ohne_taufe = [], 0, []
for rec in records(lines):
    if not re.match(r'0 @[^@]+@ INDI', rec[0]):
        out.extend(rec)
        continue
    # Ebene-1-Blöcke bilden
    blocks, cur = [], None
    for l in rec[1:]:
        if level(l) == 1:
            cur = [l]
            blocks.append(cur)
        else:
            cur.append(l)
    paten, rest = [], []
    for b in blocks:
        m = re.match(r'1 ASSO (@[^@]+@)', b[0])
        rela = next((x.split(' ', 2)[2] for x in b[1:] if re.match(r'2 RELA ', x)), '')
        if m and rela.strip().lower() in PATEN:
            paten.append(b)
        else:
            rest.append(b)
    taufe = next((b for b in rest if b[0].split(' ')[1] in TAUFE), None)
    if paten and taufe is None:
        ohne_taufe.append(rec[0].split(' ')[1])
        rest = blocks  # nichts ändern
        paten = []
    for b in paten:
        neu = []
        for l in b:
            lv, tail = l.split(' ', 1)
            l2 = f'{int(lv) + 1} {tail}'
            l2 = re.sub(r'^2 ASSO ', '2 _ASSO ', l2)
            l2 = re.sub(r'^3 RELA .*', f'3 RELA {NEU_RELA}', l2)
            neu.append(l2)
        taufe.extend(neu)
        verschoben += 1
    out.append(rec[0])
    for b in rest:
        out.extend(b)

open(dst, 'w', encoding='utf-8', newline='').write(nl.join(out) + nl)
print(f'{verschoben} Paten in die Taufe verschoben.')
if ohne_taufe:
    print(f'{len(ohne_taufe)} Personen haben Paten, aber keine Taufe (unverändert):', ' '.join(ohne_taufe))
