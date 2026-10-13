#!/usr/bin/env python3
"""Demo-Stammbaum 1.3 -> 1.4: Höfe und Häuser in Bienenbüttel als GEDCOM-L-Ortsdatensätze (Stand 2026-10-05).

Gebäude sind eigene _LOC mit Art und übergeordnetem Ort, so wie es GEDCOM-L vorsieht und Ortsfamilienbücher mit
Höfelisten es brauchen:

    0 @L2@ _LOC
    1 NAME Hof Nr. 1 (Mühle)
    1 TYPE Mühle
    1 _LOC @L1@            <- Bienenbüttel
    2 TYPE POLI
    1 EVEN                 <- Ereignis des Gebäudes (Brand, Umbau, Verkauf ...)
    2 TYPE Brand
    2 DATE 1851

Personen hängen über Ereignisse am Haus: Bewohner mit RESI (FROM ... TO ...), Besitzer zusätzlich mit PROP; am PLAC
steht der volle Name ("Hof Nr. 1 (Mühle), Bienenbüttel, Uelzen, Niedersachsen, Deutschland") und der Verweis
3 _LOC. Vorhandene Ereignisse bleiben unverändert.

Vier Gebäude: die Mühle (Hinrichs, dann Winkelmann), der Vollhof Nr. 3 (Mohwinkel), die Schmiede Nr. 7 (Mohwinkel)
und das Häuslingshaus Nr. 12 (nur Bewohner, nie Besitzer - der Testfall für "Bewohner ohne Besitz").

Aufruf:  python3 werkzeuge/hoefe.py falkenrath.ged
"""
import sys

sys.path.insert(0, sys.path[0])
import ged  # noqa: E402
from ged import Node  # noqa: E402

PATH = sys.argv[1]
text = open(PATH, encoding='utf-8').read()
if '\n2 VERS 1.3\n' not in text[:5000]:
    sys.exit('Abbruch: hoefe.py läuft nur auf Version 1.3.')
root = ged.parse(text)

ORT = 'Bienenbüttel, Uelzen, Niedersachsen, Deutschland'
LAT, LNG = 53.1417, 10.4867

# (xref, Name, Art, Breite, Länge, Notiz, Ereignisse am Gebäude [(Art, Datum, Notiz)])
HAEUSER = [
    ('L2', 'Hof Nr. 1 (Mühle)', 'Mühle', 53.1431, 10.4902, 'Wassermühle an der Ilmenau mit Wohnhaus und Scheune.', [
        ('Brand', '14 AUG 1851', 'Mühle und Scheune abgebrannt; das Wohnhaus blieb stehen.'),
        ('Neubau', '1852', 'Mühle in Backstein neu errichtet.'),
        ('Verkauf', '1865', 'Von den Erben Hinrichs an den Müller Hermann Winkelmann verkauft.'),
        ('Stilllegung', '1912', 'Mühlbetrieb eingestellt.'),
    ]),
    ('L3', 'Hof Nr. 3', 'Hof', 53.1409, 10.4851, 'Vollhof am Kirchplatz.', [
        ('Umbau', '1884', 'Neues Wohnhaus aus Backstein anstelle des Fachwerkhauses.'),
    ]),
    ('L4', 'Haus Nr. 7 (Schmiede)', 'Haus', 53.1422, 10.4873, 'Schmiede mit Wohnhaus an der Dorfstraße.', [
        ('Umbau', '1895', 'Neuer Schornstein und neue Esse.'),
    ]),
    ('L5', 'Haus Nr. 12 (Häuslingshaus)', 'Haus', 53.1398, 10.4839, 'Häuslingshaus, gehörte zum Hof Nr. 3; vermietet an Tagelöhner und Handwerker.', [
        ('Abbruch', '1911', 'Haus abgebrochen.'),
    ]),
]

# Wer wann wo: (Person, Haus, RESI-Zeitraum, PROP-Wert oder None, Notiz)
BEWOHNER = [
    ('I246', 'L2', 'FROM 1790 TO 1842', 'Wassermühle mit Wohnhaus', 'Müller; Mühle 1790 übernommen.'),
    ('I247', 'L2', 'FROM 1842 TO 1856', None, 'Witwe, führte die Mühle mit einem Mühlenknecht fort.'),
    ('I365', 'L2', 'FROM 1810 TO 1830', None, 'Als Kind und Lehrling in der Mühle der Eltern.'),
    ('I134', 'L2', 'FROM 1865 TO 1897', 'Wassermühle mit Wohnhaus', 'Mühle 1865 gekauft.'),
    ('I130', 'L3', 'FROM 1861 TO 1919', 'Vollhof mit 48 Morgen Acker und Wiesen', 'Hof 1861 gekauft.'),
    ('I288', 'L3', 'FROM 1919 TO 1964', 'Vollhof', 'Übernahm den Hof nach dem Tod des Vaters.'),
    ('I178', 'L4', 'FROM 1828 TO 1872', 'Schmiede mit Wohnhaus', 'Schmiede zur Heirat erworben.'),
    ('I365', 'L4', 'FROM 1830 TO 1860', None, 'Geselle in der Schmiede des Schwagers.'),
    ('I289', 'L4', 'FROM 1890 TO 1914', 'Schmiede mit Wohnhaus', 'Nahm die Schmiede des Großvaters wieder in Betrieb.'),
    ('I244', 'L5', 'FROM 1798 TO 1826', None, 'Häusling, zur Miete.'),
    ('I186', 'L5', 'FROM 1837 TO 1888', None, 'Holzhauer, zur Miete.'),
]

haus_name = {x: name for x, name, *_ in HAEUSER}
haus_koord = {x: (lat, lng) for x, _n, _a, lat, lng, *_ in HAEUSER}


def koord(node, lat, lng):
    m = node.add('MAP')
    m.add('LATI', f"{'N' if lat >= 0 else 'S'}{abs(lat):.4f}")
    m.add('LONG', f"{'E' if lng >= 0 else 'W'}{abs(lng):.4f}")


def plac(node, haus):
    p = node.add('PLAC', f'{haus_name[haus]}, {ORT}')
    koord(p, *haus_koord[haus])
    p.add('_LOC', f'@{haus}@')


# Ortsdatensätze: der Ort selbst und seine Gebäude
locs = []
ort = Node('_LOC', xref='@L1@')
ort.add('NAME', 'Bienenbüttel')
ort.add('TYPE', 'Gemeinde')
koord(ort, LAT, LNG)
ort.add('_POST', '29553')
ort.add('_STAE', 'Niedersachsen')
ort.add('_CTRY', 'Deutschland')
locs.append(ort)
for xref, name, art, lat, lng, notiz, ereignisse in HAEUSER:
    h = Node('_LOC', xref=f'@{xref}@')
    h.add('NAME', name)
    h.add('TYPE', art)
    h.add('_LOC', '@L1@').add('TYPE', 'POLI')
    koord(h, lat, lng)
    for e_art, e_datum, e_notiz in ereignisse:
        e = h.add('EVEN')
        e.add('TYPE', e_art)
        e.add('DATE', e_datum)
        e.add('NOTE', e_notiz)
    h.add('NOTE', notiz)
    locs.append(h)

# Bewohner und Besitzer an die Personen - vor DEAT, damit der Lebenslauf im GEDCOM lesbar bleibt
personen = {r.xref: r for r in root.children if r.tag == 'INDI'}
count = {'RESI': 0, 'PROP': 0}
for xref, haus, zeit, besitz, notiz in BEWOHNER:
    p = personen[f'@{xref}@']
    neu = []
    if besitz:
        prop = Node('PROP', besitz)
        prop.add('DATE', zeit)
        plac(prop, haus)
        prop.add('NOTE', notiz)
        neu.append(prop)
        count['PROP'] += 1
    resi = Node('RESI')
    resi.add('DATE', zeit)
    plac(resi, haus)
    if not besitz:
        resi.add('NOTE', notiz)
    neu.append(resi)
    count['RESI'] += 1
    ziel = next((i for i, c in enumerate(p.children) if c.tag in ('DEAT', 'BURI', 'OBJE', 'FAMC', 'FAMS')), len(p.children))
    p.children[ziel:ziel] = neu

# _LOC vor TRLR
trlr = root.children.index(next(r for r in root.children if r.tag == 'TRLR'))
root.children[trlr:trlr] = locs

root.children[0].first('SOUR').first('VERS').value = '1.4'
open(PATH, 'w', encoding='utf-8').write(ged.serialize(root))
print({**count, '_LOC': len(locs)})
