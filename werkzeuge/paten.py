#!/usr/bin/env python3
"""Taufpaten und Trauzeugen im Demo-Stammbaum ergänzen (Stand 2026-10-01).

Regeln (siehe README, Abschnitt „Paten und Trauzeugen“):
- Hauptform wie webtrees:  2 _ASSO @I…@ / 3 RELA godparent  bzw.  witness
- Personen ohne eigenen Datensatz:  2 NOTE Paten: Name, Beruf zu Ort; …  bzw.  Trauzeugen: …
- Direkte Linie von I1: jede Taufe mit Paten, jede standesamtliche Heirat mit zwei Zeugen,
  kirchliche Trauungen vor 1875 etwa zur Hälfte. Seitenlinien bleiben, wie sie sind.
- Einige Testfälle bleiben bewusst abweichend (godfather/godmother, Godparent, 1 ASSO).

Aufruf:  python3 werkzeuge/paten.py falkenrath.ged  (schreibt die Datei neu, Bericht nach stdout)
"""
import datetime
import json
import random
import sys
from collections import Counter, defaultdict

sys.path.insert(0, sys.path[0])
import ged  # noqa: E402
from ged import Node, event_date, to_date  # noqa: E402

PATH = sys.argv[1]
# Schutz: nur einmal anwenden – auf Version 1.1 des Demo-Baums
if '\n2 VERS 1.1\n' not in open(PATH, encoding='utf-8').read(5000):
    sys.exit('Abbruch: paten.py ist schon angewendet (erwartet HEAD … 2 VERS 1.1).')
rnd = random.Random(20261001)
root = ged.parse(open(PATH, encoding='utf-8').read())
R = {r.xref: r for r in root.children if r.xref}
INDI = {k: r for k, r in R.items() if r.tag == 'INDI'}
FAM = {k: r for k, r in R.items() if r.tag == 'FAM'}
TODAY = datetime.date(2026, 10, 1)

# ------------------------------------------------------------------ Hilfen


def name(i):
    return ' '.join(INDI[i].val('NAME', '?').replace('/', ' ').split())


def sex(i):
    return INDI[i].val('SEX')


def reli(i):
    return INDI[i].val('RELI')


def birth(i):
    return event_date(INDI[i].first('BIRT')) or event_date(INDI[i].first('CHR'))


def death(i):
    return event_date(INDI[i].first('DEAT')) or event_date(INDI[i].first('BURI'))


def famc(i):
    f = INDI[i].val('FAMC')
    return FAM.get(f)


def parents(i):
    f = famc(i)
    return (f.val('HUSB'), f.val('WIFE')) if f is not None else (None, None)


def children(fam):
    return [c.value for c in fam.all('CHIL')] if fam is not None else []


def spouses(i):
    out = []
    for fs in INDI[i].all('FAMS'):
        f = FAM[fs.value]
        for t in ('HUSB', 'WIFE'):
            p = f.val(t)
            if p and p != i:
                out.append(p)
    return out


def siblings(i):
    return [c for c in children(famc(i)) if c != i]


def age_at(i, d):
    b = birth(i)
    if not b or not d:
        return None
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))


def alive_at(i, d):
    dd = death(i)
    if dd:
        return dd > d
    a = age_at(i, d)
    return a is not None and a < 80


def living(i):
    return death(i) is None and (age_at(i, TODAY) or 999) < 100


AHNEN = {'@I1@'}
q = ['@I1@']
while q:
    for p in parents(q.pop()):
        if p and p not in AHNEN:
            AHNEN.add(p)
            q.append(p)


def direct_fam(f):
    return FAM[f].val('HUSB') in AHNEN and FAM[f].val('WIFE') in AHNEN


# ------------------------------------------------------------------ Namen für Personen ohne Datensatz
NACHNAMEN = ['Meyer', 'Müller', 'Schulze', 'Behrens', 'Peters', 'Ahrens', 'Garbers', 'Heuer', 'Bostelmann',
             'Dralle', 'Wrede', 'Brammer', 'Niebuhr', 'Gerdau', 'Bockelmann', 'Wiese', 'Kruse', 'Rabe', 'Stöver',
             'Hogrefe', 'Lange', 'Wolters', 'Plate', 'Söhl', 'Thies', 'Cohrs', 'Bruns', 'Vollmer', 'Kahle']
NACHNAMEN_KATH = ['Brinkmann', 'Schäfers', 'Tölle', 'Hillebrand', 'Kemper', 'Lütkehaus', 'Wienströer', 'Hagemeier',
                  'Rüsing', 'Bunte', 'Kleeschulte', 'Füller']
VORNAMEN = {
    'M': {1800: ['Johann Heinrich', 'Hans Jürgen', 'Johann Friedrich', 'Christoph', 'Jürgen', 'Hinrich', 'Claus'],
          1850: ['Heinrich', 'Friedrich', 'Wilhelm', 'Carl', 'August', 'Hermann', 'Christian'],
          1900: ['Wilhelm', 'Otto', 'Ernst', 'Hermann', 'Karl', 'Walter', 'Paul'],
          1950: ['Günter', 'Hans-Jürgen', 'Klaus', 'Dieter', 'Werner', 'Horst'],
          2000: ['Thomas', 'Michael', 'Stefan', 'Andreas', 'Frank']},
    'F': {1800: ['Anna Maria', 'Catharina', 'Ilsabe', 'Anna Dorothea', 'Margaretha', 'Engel'],
          1850: ['Sophie', 'Dorothea', 'Caroline', 'Wilhelmine', 'Louise', 'Friederike'],
          1900: ['Anna', 'Marie', 'Frieda', 'Martha', 'Emma', 'Elise'],
          1950: ['Ursula', 'Gisela', 'Ingrid', 'Helga', 'Renate'],
          2000: ['Sabine', 'Petra', 'Andrea', 'Claudia', 'Susanne']},
}
VORNAMEN_KATH = {'M': ['Franz', 'Anton', 'Johann Bernhard', 'Franz Anton', 'Joseph', 'Theodor'],
                 'F': ['Maria Anna', 'Franziska', 'Anna Maria', 'Elisabeth', 'Theresia', 'Gertrud']}
BERUF_M = {1800: ['Ackermann', 'Halbhöfner', 'Kötner', 'Brinksitzer', 'Häusling', 'Schäfer', 'Schmied', 'Krüger'],
           1850: ['Hofbesitzer', 'Anbauer', 'Schmied', 'Müller', 'Zimmermann', 'Stellmacher', 'Gastwirt'],
           1900: ['Landwirt', 'Tischler', 'Lokomotivführer', 'Kaufmann', 'Maurer', 'Bäckermeister', 'Postbote'],
           1950: ['Schlosser', 'Angestellter', 'Elektriker', 'Lehrer', 'Kaufmann', 'Landwirt'],
           2000: ['Ingenieur', 'Lehrer', 'Bankkaufmann', 'Polizeibeamter', 'Arzt']}
BERUF_F = {1800: ['Jungfer', 'Dienstmagd'], 1850: ['Jungfer', 'Dienstmagd'], 1900: ['ledig', 'Haustochter'],
           1950: ['Verkäuferin', 'Hausfrau', 'Krankenschwester'], 2000: ['Lehrerin', 'Ärztin', 'Bürokauffrau']}


def era(y):
    return max(k for k in (1800, 1850, 1900, 1950, 2000) if k <= max(y, 1800))


def free_person(s, y, town, kath):
    e = era(y)
    vn = rnd.choice(VORNAMEN_KATH[s] if kath and y < 1900 else VORNAMEN[s][e])
    nn = rnd.choice(NACHNAMEN_KATH if kath else NACHNAMEN)
    if s == 'M':
        beruf = rnd.choice(BERUF_M[e])
        return f'{vn} {nn}, {beruf} zu {town}' if y < 1900 else f'{vn} {nn}, {beruf}, {town}'
    if rnd.random() < 0.5 and y < 1950:
        mann = rnd.choice(VORNAMEN_KATH['M'] if kath and y < 1900 else VORNAMEN['M'][e])
        beruf = rnd.choice(BERUF_M[e])
        return f'{vn} {nn}, Ehefrau des {beruf}s {mann} {nn} zu {town}' if y < 1900 else \
            f'{vn} {nn}, Ehefrau des {beruf}s {mann} {nn}, {town}'
    return f'{vn} {nn}, {rnd.choice(BERUF_F[e])} zu {town}' if y < 1900 else \
        f'{vn} {nn}, {rnd.choice(BERUF_F[e])}, {town}'


def town(ev):
    p = ev.val('PLAC') or ''
    return p.split(',')[0] or 'unbekannt'


# ------------------------------------------------------------------ Einfügen


def has_transcript(ev):
    return any(s.first('DATA') is not None and s.first('DATA').first('TEXT') is not None for s in ev.all('SOUR'))




def insert_before_sour(ev, nodes):
    i = next((k for k, c in enumerate(ev.children) if c.tag in ('SOUR', 'OBJE')), len(ev.children))
    ev.children[i:i] = nodes


def asso(x, rela):
    n = Node('_ASSO', x)
    n.add('RELA', rela)
    return n


report = Counter()
EXAMPLES = defaultdict(list)

# ------------------------------------------------------------------ 0) bestehende Paten-Notizen: Personen mit „;“ trennen
for r in INDI.values():
    ev = r.first('CHR')
    for n in (ev.all('NOTE') if ev is not None else []):
        if n.value and n.value.startswith('Paten: ') and ';' not in n.value:
            parts = n.value[7:].split(', ')
            if len(parts) % 2 == 0:
                n.value = 'Paten: ' + '; '.join(', '.join(parts[k:k + 2]) for k in range(0, len(parts), 2))
                report['Paten-Notizen auf „;“ umgestellt'] += 1

# ------------------------------------------------------------------ 1) bestehende RELA vereinheitlichen
KEEP_OLD = set()  # Taufen, die godfather/godmother behalten (Testfall)
side_chr = [(i, r.first('CHR')) for i, r in INDI.items()
            if i not in AHNEN and r.first('CHR') is not None and r.first('CHR').all('_ASSO')]
side_chr.sort(key=lambda x: int(x[0][2:-1]))
for i, ev in side_chr[:2]:
    KEEP_OLD.add(i)
    EXAMPLES['RELA godfather/godmother (alt, webtrees)'].append(i)
CAPITAL = side_chr[2][0]
LEVEL1 = side_chr[3][0]
for i, r in INDI.items():
    ev = r.first('CHR')
    if ev is None:
        continue
    for a in ev.all('_ASSO'):
        rl = a.first('RELA')
        if rl is not None and rl.value in ('godfather', 'godmother') and i not in KEEP_OLD:
            rl.value = 'godparent'
            report['RELA → godparent'] += 1
# Testfall Großschreibung (Import aus anderen Programmen)
for a in INDI[CAPITAL].first('CHR').all('_ASSO'):
    a.first('RELA').value = 'Godparent'
EXAMPLES['RELA Godparent (Grossschreibung)'].append(CAPITAL)
# Testfall alte Form 1 ASSO an der Person (GEDCOM 5.5.1)
ev = INDI[LEVEL1].first('CHR')
moved = ev.all('_ASSO')
ev.children = [c for c in ev.children if c.tag != '_ASSO']
pos = next(k for k, c in enumerate(INDI[LEVEL1].children) if c.tag in ('OBJE', 'FAMC', 'FAMS', 'NOTE'))
for a in moved:
    n = Node('ASSO', a.value)
    n.add('RELA', 'Godfather' if sex(a.value) == 'M' else 'Godmother')
    INDI[LEVEL1].children.insert(pos, n)
    pos += 1
EXAMPLES['1 ASSO an der Person (GEDCOM 5.5.1)'].append(LEVEL1)

# ------------------------------------------------------------------ 2) Taufen der direkten Linie
# I52: Paten wie im Scan taufeintrag-1801.jpg (M130)
i52 = INDI['@I52@'].first('CHR')
insert_before_sour(i52, [Node('NOTE', 'Paten: Heinrich Eggers, Ackermann zu Eschede; '
                                      'Johann Lüders, Schäfer zu Eschede')])
report['Taufen nur mit Text-Paten'] += 1


def godparent_candidates(c, d):
    f, m = parents(c)
    cands = []
    for p in (f, m):
        if not p:
            continue
        cands += [x for x in parents(p) if x]                 # Großeltern
        for s in siblings(p):                                  # Onkel/Tanten
            cands.append(s)
            cands += spouses(s)
    cands += [s for s in siblings(c) if (age_at(s, d) or 0) >= 14]  # ältere Geschwister (konfirmiert)
    out = []
    for x in cands:
        if x in (c, f, m) or x in out or x not in INDI:
            continue
        a = age_at(x, d)
        if a is None or a < 14 or not alive_at(x, d):
            continue
        if reli(c) and reli(x) and reli(c) != reli(x):
            continue
        out.append(x)
    return out


for c in sorted(AHNEN, key=lambda x: int(x[2:-1])):
    ev = INDI[c].first('CHR')
    if ev is None or ev.all('_ASSO') or ev.all('NOTE'):
        continue
    d = event_date(ev)
    if d is None:
        continue
    n = 3 if d.year < 1850 else 2
    cands = godparent_candidates(c, d)
    rnd.shuffle(cands)
    # erster Pate gleichen Geschlechts wie der Täufling
    want = [sex(c) or 'M'] + [('F' if sex(c) == 'M' else 'M')] + [rnd.choice('MF')]
    linked, free = [], []
    for s in want[:n]:
        pick = next((x for x in cands if sex(x) == s and x not in linked), None)
        if pick and rnd.random() < 0.55:
            linked.append(pick)
        else:
            free.append(free_person(s, d.year, town(ev), reli(c) == 'römisch-katholisch'))
    nodes = [asso(x, 'godparent') for x in linked]
    if free:
        nodes.append(Node('NOTE', 'Paten: ' + '; '.join(free)))
    insert_before_sour(ev, nodes)
    report['Paten verlinkt'] += len(linked)
    report['Paten als Text'] += len(free)
    kind = 'gemischt' if linked and free else 'nur verlinkt' if linked else 'nur Text'
    report[f'Taufen {kind}'] += 1
    EXAMPLES[f'Taufe {kind}'].append(c)
    if any(living(x) for x in linked):
        EXAMPLES['lebender Pate'].append(c)

# gemischt: verlinkte Paten + weitere Paten als Text (ohne Abschrift, damit Text und Daten übereinstimmen)
mixed = 0
for c in sorted(AHNEN, key=lambda x: int(x[2:-1])):
    ev = INDI[c].first('CHR')
    if ev is None or not ev.all('_ASSO') or ev.all('NOTE') or has_transcript(ev) or mixed >= 6:
        continue
    d = event_date(ev)
    k = 3 - len(ev.all('_ASSO')) if d.year < 1850 else 1
    if k < 1:
        continue
    free = [free_person(rnd.choice('MF'), d.year, town(ev), reli(c) == 'römisch-katholisch') for _ in range(k)]
    insert_before_sour(ev, [Node('NOTE', 'Paten: ' + '; '.join(free))])
    report['Taufen gemischt'] += 1
    report['Paten als Text'] += k
    EXAMPLES['Taufe gemischt'].append(c)
    mixed += 1

# lebende Patin: Taufe von Jonas (I1) mit Tante Ute (I10) und einem Freund der Familie
j = INDI['@I1@']
chr_j = Node('CHR')
chr_j.add('DATE', '2 JUN 1985')
pl = j.first('BIRT').first('PLAC')
chr_j.children.append(pl)
chr_j.children += [asso('@I10@', 'godparent'),
                   Node('NOTE', 'Paten: Martin Hoppe, Bauingenieur, Hannover')]
cj = chr_j.add('SOUR', next(s.xref for s in root.children if s.tag == 'SOUR'
                            and s.val('TITL') == 'Urkundensammlung Familie Falkenrath'))
cj.add('PAGE', 'Taufschein Jonas Falkenrath, 1985')
cj.add('QUAY', '3')
j.children.insert(j.children.index(j.first('BIRT')) + 1, chr_j)
EXAMPLES['lebende Patin'].append('@I1@')
report['Taufe neu angelegt (I1)'] += 1

# Pate mit Notiz und mit Quellenangabe unter _ASSO
def relation(c, x):
    f, m = parents(c)
    for p, seite in ((f, 'des Vaters'), (m, 'der Mutter')):
        if not p:
            continue
        if x in parents(p):
            return ('Vater ' if sex(x) == 'M' else 'Mutter ') + seite
        for s in siblings(p):
            if x == s:
                return ('Bruder ' if sex(x) == 'M' else 'Schwester ') + seite
            if x in spouses(s):
                return ('Schwager ' if sex(x) == 'M' else 'Schwägerin ') + seite
    if x in siblings(c):
        return 'Bruder des Täuflings' if sex(x) == 'M' else 'Schwester des Täuflings'
    return None


for c in sorted(AHNEN, key=lambda x: int(x[2:-1])):
    ev = INDI[c].first('CHR')
    if ev is None or not ev.all('_ASSO') or 'Pate mit Notiz' in EXAMPLES:
        continue
    a = ev.all('_ASSO')[0]
    rel = relation(c, a.value)
    if rel is None:
        continue
    a.add('NOTE', rel)
    EXAMPLES['Pate mit Notiz'].append(c)
for c in sorted(AHNEN, key=lambda x: int(x[2:-1])):
    ev = INDI[c].first('CHR')
    if ev is None or not ev.all('_ASSO') or not ev.all('SOUR') or 'Pate mit Quellenangabe' in EXAMPLES:
        continue
    s = ev.first('SOUR')
    if not (s.val('PAGE') or '').startswith('Taufe'):
        continue
    a = ev.all('_ASSO')[-1]
    cs = a.add('SOUR', s.value)
    cs.add('PAGE', s.val('PAGE'))
    cs.add('QUAY', '3')
    EXAMPLES['Pate mit Quellenangabe'].append(c)

# ------------------------------------------------------------------ 3) Trauzeugen der direkten Linie


def witness_candidates(f, d):
    h, w = FAM[f].val('HUSB'), FAM[f].val('WIFE')
    cands = []
    for p in (h, w):
        cands += [x for x in parents(p) if x]
        for s in siblings(p):
            cands.append(s)
            cands += spouses(s)
    out = []
    for x in cands:
        if x in (h, w) or x in out or x not in INDI:
            continue
        a = age_at(x, d)
        if a is None or a < (21 if d.year < 1975 else 18) or not alive_at(x, d):
            continue
        if d.year < 1920 and sex(x) != 'M':
            continue
        out.append(x)
    return out


def append_text(ev, line):
    for s in ev.all('SOUR'):
        d = s.first('DATA')
        if d is not None and d.first('TEXT') is not None:
            d.first('TEXT').add('CONT', line)


for f in sorted(FAM, key=lambda x: int(x[2:-1])):
    if not direct_fam(f):
        continue
    for ev in FAM[f].all('MARR'):
        if ev.all('_ASSO') or ev.all('NOTE'):
            # vorhandene Zeugen auch in die Abschrift des Standesamtseintrags übernehmen
            names = [name(a.value) for a in ev.all('_ASSO')]
            if ev.val('TYPE') == 'civil' and not ev.all('NOTE') and len(names) < 2:
                # Standesamt: immer zwei Zeugen
                d = event_date(ev)
                extra = free_person('M', d.year, town(ev), False)
                insert_before_sour(ev, [Node('NOTE', 'Trauzeugen: ' + extra)])
                names.append(extra.split(',')[0])
                report['Heiraten civil um zweiten Zeugen ergänzt'] += 1
            if ev.val('TYPE') == 'civil' and has_transcript(ev) and names:
                append_text(ev, 'Als Zeugen waren zugezogen: ' + ' und '.join(names) + '.')
                report['Abschrift um Zeugen ergänzt'] += 1
            continue
        d = event_date(ev)
        ty = ev.val('TYPE')
        if d is None or ty is None:
            continue
        if ty == 'religious':
            if d.year >= 1875 or has_transcript(ev) or rnd.random() < 0.5:
                continue  # Kirche ab 1875: Zeugen stehen beim Standesamt
        cands = witness_candidates(f, d)
        rnd.shuffle(cands)
        linked, free = [], []
        for k in range(2):
            pick = next((x for x in cands if x not in linked), None)
            if pick and rnd.random() < 0.5:
                linked.append(pick)
            else:
                s = 'M' if d.year < 1920 or rnd.random() < 0.6 else 'F'
                free.append(free_person(s, d.year, town(ev), False))
        nodes = [asso(x, 'witness') for x in linked]
        if free:
            nodes.append(Node('NOTE', 'Trauzeugen: ' + '; '.join(free)))
        insert_before_sour(ev, nodes)
        if has_transcript(ev) and ty == 'civil':
            names = [name(x) for x in linked] + [p.split(',')[0] for p in free]
            append_text(ev, 'Als Zeugen waren zugezogen: ' + ' und '.join(names) + '.')
        report[f'Heiraten {ty} mit neuen Zeugen'] += 1
        report['Zeugen verlinkt'] += len(linked)
        report['Zeugen als Text'] += len(free)

# ------------------------------------------------------------------ Prüfen und schreiben
xrefs = set(R)
err = []
for r in root.children:
    for ln in r.lines():
        parts = ln.split(' ', 2)
        if len(parts) == 3 and parts[2].startswith('@') and parts[2].endswith('@') and parts[2] not in xrefs:
            err.append(f'Verweis ins Leere: {ln}')
        if len(ln.encode()) > 255:
            err.append(f'Zeile zu lang: {ln[:40]}')
# Pate darf nicht Elternteil sein, muss leben und konfirmiert (14) sein
for c, r in INDI.items():
    ev = r.first('CHR')
    if ev is None:
        continue
    d = event_date(ev)
    for a in ev.all('_ASSO'):
        if a.value in parents(c):
            err.append(f'{c}: Elternteil als Pate')
        if c in AHNEN and d and (not alive_at(a.value, d) or (age_at(a.value, d) or 0) < 14):
            err.append(f'{c}: Pate {a.value} nicht möglich')
if err:
    print('\n'.join(err[:30]))
    sys.exit(1)

# Mehrfachpaten
cnt = Counter(a.value for r in INDI.values() for e in r.children for a in e.all('_ASSO')
              if a.first('RELA') is not None and a.first('RELA').value.lower() in ('godparent', 'godfather', 'godmother'))
EXAMPLES['Pate bei mehreren Taufen'] = [x for x, n in cnt.most_common(1)]

for c in sorted(AHNEN, key=lambda x: int(x[2:-1])):
    ev = INDI[c].first('CHR')
    if ev is not None and ev.all('_ASSO') and not ev.all('NOTE') and len(EXAMPLES['Taufe nur verlinkt']) < 3:
        EXAMPLES['Taufe nur verlinkt'].append(c)
for f in sorted(FAM, key=lambda x: int(x[2:-1])):
    for ev in FAM[f].all('MARR'):
        k = ('Trauzeugen gemischt' if ev.all('_ASSO') and ev.all('NOTE') else
             'Trauzeugen nur Text' if ev.all('NOTE') else None)
        if k and len(EXAMPLES[k]) < 3:
            EXAMPLES[k].append(f)

open(PATH, 'w', encoding='utf-8').write(ged.serialize(root))
print(json.dumps(dict(report), ensure_ascii=False, indent=1))
print(json.dumps({k: [x.strip('@') for x in v[:3]] for k, v in EXAMPLES.items()}, ensure_ascii=False, indent=1))
