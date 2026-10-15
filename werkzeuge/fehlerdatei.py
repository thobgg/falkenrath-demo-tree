#!/usr/bin/env python3
"""Fehlerdateien zum Demo-Stammbaum: jede Pruefregel von gedaudit/wtWin soll mindestens einmal anschlagen.

Basis ist versionen/falkenrath-1.7.ged. Angehaengt wird ein Block mit Fehlerfaellen (Personen @E...@, Familien @EF...@,
pro Regel ein Fall), dazu Fehler im Kopf und eine Zeile, die kein GEDCOM ist.

  fehler/falkenrath-1.7-fehler.ged          GEDCOM 5.5.1, alle Regeln ausser 624 (nur GEDCOM 7)
  fehler/falkenrath-1.7-fehler-gedcom7.ged  GEDCOM 7.0, alle Regeln ausser 621 (FILE gibt es in 7 nicht)
  fehler/fehlerfaelle.tsv                   Regel, Version, Kennungen, Fehler

Aufruf:  python3 werkzeuge/fehlerdatei.py
"""
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASE, 'versionen', 'falkenrath-1.7.ged')
ZIEL = os.path.join(BASE, 'fehler')

CELLE = ('Celle, Niedersachsen, Deutschland', 'N52.6226', 'E10.0815')
PADERBORN = ('Paderborn, Nordrhein-Westfalen, Deutschland', 'N51.7189', 'E8.7575')


def ort(o=CELLE, stufe=2):
    name, lat, lon = o
    return [f'{stufe} PLAC {name}', f'{stufe + 1} MAP', f'{stufe + 2} LATI {lat}', f'{stufe + 2} LONG {lon}']


def ev(tag, datum=None, o=CELLE, wert=None, extra=()):
    z = [f'1 {tag}' + (f' {wert}' if wert else '')]
    if datum:
        z.append(f'2 DATE {datum}')
    if o:
        z += ort(o)
    return z + list(extra)


class Block:
    """Fehlerfaelle als GEDCOM-Zeilen, dazu je Regel eine Zeile fuer die Tabelle."""

    def __init__(self, sieben):
        self.sieben = sieben
        self.zeilen = []
        self.tabelle = []

    def fall(self, regel, kennungen, text):
        self.tabelle.append((regel, '7.0' if self.sieben else '5.5.1', ' '.join(kennungen), text))

    def person(self, x, name=None, sex='M', fakten=(), famc=(), fams=(), rest=()):
        z = [f'0 @{x}@ INDI']
        if name is not None:
            z.append(f'1 NAME {name}')
        if sex:
            z.append(f'1 SEX {sex}')
        for f in fakten:
            z += f
        z += [f'1 FAMC @{f}@' for f in famc] + [f'1 FAMS @{f}@' for f in fams] + list(rest)
        self.zeilen += z

    def familie(self, x, mann=None, frau=None, kinder=(), heirat=None, rest=()):
        z = [f'0 @{x}@ FAM']
        if mann:
            z.append(f'1 HUSB @{mann}@')
        if frau:
            z.append(f'1 WIFE @{frau}@')
        if heirat:
            z += ev('MARR', heirat)
        z += [f'1 CHIL @{k}@' for k in kinder] + list(rest)
        self.zeilen += z

    def pate(self, x, rolle='godparent'):
        if self.sieben:
            return [f'2 ASSO @{x}@', '3 ROLE GODP']
        return [f'2 _ASSO @{x}@', f'3 RELA {rolle}']

    def eltern_kind(self, nr, vater=None, mutter=None, kinder=(), heirat=None, nachname='Muster'):
        """Familie EF<nr> mit Vater E<nr>V, Mutter E<nr>M und Kindern E<nr>K1 usw., Angaben als (geb, tod)."""
        f = f'EF{nr}'
        v = m = None
        if vater:
            v = f'E{nr}V'
            self.person(v, f'Heinrich /{nachname}/', 'M', [ev('BIRT', vater[0])] + ([ev('DEAT', vater[1])] if vater[1] else []), fams=[f])
        if mutter:
            m = f'E{nr}M'
            self.person(m, f'Anna /{nachname}geb/', 'F', [ev('BIRT', mutter[0])] + ([ev('DEAT', mutter[1])] if mutter[1] else []), fams=[f])
        ks = []
        for i, (geb, vorname, sex) in enumerate(kinder, 1):
            k = f'E{nr}K{i}'
            self.person(k, f'{vorname} /{nachname}/', sex, [ev('BIRT', geb)], famc=[f])
            ks.append(k)
        self.familie(f, v, m, ks, heirat)
        return f, v, m, ks


def fehlerblock(sieben):
    b = Block(sieben)
    P, F = b.person, b.familie

    # 0xx Chronologie
    P('E010', 'Diedrich /Abel/', 'M', [ev('BIRT', '1 MAR 1850'), ev('DEAT', '1 MAR 1840')])
    b.fall('010', ['E010'], 'Tod 1840 vor Geburt 1850')
    P('E011A', 'Georg /Bauer/', 'M', [ev('BIRT', '1 JUN 1850')], fams=['EF011'])
    P('E011B', 'Emma /Christ/', 'F', [ev('BIRT', '1 JUN 1830')], fams=['EF011'])
    F('EF011', 'E011A', 'E011B', heirat='1 MAY 1845')
    b.fall('011', ['E011A', 'EF011'], 'Heirat 1845 vor der Geburt des Mannes 1850')
    P('E012A', 'Gustav /Dorn/', 'M', [ev('BIRT', '1 JUN 1830'), ev('DEAT', '1 JAN 1870')], fams=['EF012'])
    P('E012B', 'Berta /Ebel/', 'F', [ev('BIRT', '1 JUN 1835')], fams=['EF012'])
    F('EF012', 'E012A', 'E012B', heirat='1 MAY 1875')
    b.fall('012', ['E012A', 'EF012'], 'Heirat 1875 nach dem Tod des Mannes 1870')
    b.eltern_kind('013', vater=('1 JAN 1840', None), mutter=('1 JAN 1880', None), kinder=[('1 JAN 1870', 'Ernst', 'M')], nachname='Fink')
    b.fall('013', ['E013K1', 'EF013'], 'Kind 1870 vor der Mutter 1880 geboren')
    b.eltern_kind('014', vater=('1 JAN 1880', None), mutter=('1 JAN 1840', None), kinder=[('1 JAN 1870', 'Ernst', 'M')], nachname='Gast')
    b.fall('014', ['E014K1', 'EF014'], 'Kind 1870 vor dem Vater 1880 geboren')
    b.eltern_kind('015', vater=('1 JAN 1840', None), mutter=('1 JAN 1845', '1 JAN 1880'), kinder=[('1 JUN 1880', 'Ernst', 'M')], nachname='Horn')
    b.fall('015', ['E015K1', 'EF015'], 'Kind Juni 1880, Mutter im Januar 1880 gestorben')
    b.eltern_kind('016', vater=('1 JAN 1840', '1 JAN 1880'), mutter=('1 JAN 1845', None), kinder=[('1 DEC 1880', 'Ernst', 'M')], nachname='Imhof')
    b.fall('016', ['E016K1', 'EF016'], 'Kind Dezember 1880, Vater 11 Monate vorher gestorben (Grenze 9,5)')
    b.eltern_kind('017', vater=('1 JAN 1840', None), mutter=('1 JAN 1845', None), kinder=[('1 JAN 1870', 'Ernst', 'M')], heirat='1 JAN 1875', nachname='Jahn')
    b.fall('017', ['E017K1', 'EF017'], 'Kind 1870, Eltern heiraten erst 1875')
    P('E018', 'Hinrich /Kern/', 'M', [ev('BIRT', '31 APR 1850')])
    b.fall('018', ['E018'], 'Geburt am 31. April')
    P('E019', 'Hinrich /Lenz/', 'M', [ev('BIRT', '1 JAN 2099')])
    b.fall('019', ['E019'], 'Geburt 2099')
    P('E020', 'Hinrich /Mohr/', 'M', [ev('BIRT', '1 MAY 1850'), ev('CHR', '1 APR 1850')])
    b.fall('020', ['E020'], 'Taufe einen Monat vor der Geburt')
    P('E021', 'Hinrich /Nolte/', 'M', [ev('BIRT', '1 MAY 1820'), ev('DEAT', '1 MAY 1900'), ev('BURI', '1 APR 1900')])
    b.fall('021', ['E021'], 'Begräbnis einen Monat vor dem Tod')
    P('E022A', 'Hinrich /Opitz/', 'M', [ev('BIRT', '1 JUN 1850')], fams=['EF022'])
    P('E022B', 'Martha /Pohl/', 'F', [ev('BIRT', '1 JUN 1852')], fams=['EF022'])
    F('EF022', 'E022A', 'E022B', heirat='1 JUN 1850')
    b.fall('022', ['E022A', 'EF022'], 'Geburtsdatum gleich Heiratsdatum')
    b.eltern_kind('023', vater=('1 JAN 1840', None), mutter=('1 JAN 1845', None),
                  kinder=[('1 JAN 1875', 'Ernst', 'M'), ('1 JAN 1870', 'Otto', 'M')], nachname='Quast')
    b.fall('023', ['E023K2', 'EF023'], 'Kinder nicht in Geburtsreihenfolge (1875 vor 1870)')
    P('E024P', 'Wilhelm /Rose/', 'M', [ev('BIRT', '1 JAN 1800'), ev('DEAT', '1 JAN 1850')])
    P('E024', 'Ludwig /Sander/', 'M', [ev('BIRT', '1 JAN 1860'), ev('CHR', '5 JAN 1860', extra=b.pate('E024P'))])
    b.fall('024', ['E024'], 'Pate 1850 gestorben, Taufe 1860')

    # 1xx Altersgrenzen
    P('E110', 'Hinrich /Thiel/', 'M', [ev('BIRT', '1 JAN 1700'), ev('DEAT', '1 JAN 1820')])
    b.fall('110', ['E110'], '120 Jahre alt (Grenze 110)')
    b.eltern_kind('111', vater=('1 JAN 1840', None), mutter=('1 JAN 1870', None), kinder=[('1 JAN 1880', 'Ernst', 'M')], nachname='Ulrich')
    b.fall('111', ['E111K1', 'EF111'], 'Mutter bei der Geburt 10 Jahre (Grenze 14)')
    b.eltern_kind('112', vater=('1 JAN 1800', None), mutter=('1 JAN 1800', None), kinder=[('1 JAN 1860', 'Ernst', 'M')], nachname='Vogt')
    b.fall('112', ['E112K1', 'EF112'], 'Mutter bei der Geburt 60 Jahre (Grenze 55)')
    b.eltern_kind('113', vater=('1 JAN 1870', None), mutter=('1 JAN 1855', None), kinder=[('1 JAN 1880', 'Ernst', 'M')], nachname='Wenz')
    b.fall('113', ['E113K1', 'EF113'], 'Vater bei der Geburt 10 Jahre (Grenze 14)')
    b.eltern_kind('114', vater=('1 JAN 1780', None), mutter=('1 JAN 1825', None), kinder=[('1 JAN 1860', 'Ernst', 'M')], nachname='Zahn')
    b.fall('114', ['E114K1', 'EF114'], 'Vater bei der Geburt 80 Jahre (Grenze 75)')
    P('E115A', 'Hinrich /Ahrens/', 'M', [ev('BIRT', '1 JAN 1860')], fams=['EF115'])
    P('E115B', 'Martha /Bode/', 'F', [ev('BIRT', '1 JAN 1870')], fams=['EF115'])
    F('EF115', 'E115A', 'E115B', heirat='1 JAN 1880')
    b.fall('115', ['E115B', 'EF115'], 'Frau heiratet mit 10 Jahren (Grenze 15)')
    P('E116A', 'Hinrich /Claus/', 'M', [ev('BIRT', '1 JAN 1780')], fams=['EF116'])
    P('E116B', 'Martha /Dreyer/', 'F', [ev('BIRT', '1 JAN 1790')], fams=['EF116'])
    F('EF116', 'E116A', 'E116B', heirat='1 JAN 1875')
    b.fall('116', ['E116A', 'EF116'], 'Mann heiratet mit 95 Jahren (Grenze 90)')
    P('E117A', 'Hinrich /Eggers/', 'M', [ev('BIRT', '1 JAN 1800')], fams=['EF117'])
    P('E117B', 'Martha /Fricke/', 'F', [ev('BIRT', '1 JAN 1850')], fams=['EF117'])
    F('EF117', 'E117A', 'E117B')
    b.fall('117', ['E117A', 'EF117'], '50 Jahre zwischen den Ehepartnern (Grenze 40)')
    b.eltern_kind('118', vater=('1 JAN 1840', None), mutter=('1 JAN 1845', None),
                  kinder=[('1 JAN 1880', 'Ernst', 'M'), ('1 MAY 1880', 'Otto', 'M')], nachname='Gerdes')
    b.fall('118', ['E118K1', 'E118K2', 'EF118'], 'Geschwister 4 Monate auseinander (Grenze 8)')
    b.eltern_kind('119', vater=('1 JAN 1820', None), mutter=None,
                  kinder=[('1 JAN 1845', 'Ernst', 'M'), ('1 JAN 1857', 'Otto', 'M'), ('1 JAN 1868', 'Paul', 'M'), ('1 JAN 1880', 'Karl', 'M')], nachname='Harms')
    b.fall('119', ['EF119'], '35 Jahre zwischen ältestem und jüngstem Kind (Grenze 30)')
    # 120 und 123: 17 Kinder in einer Ehe, mit der zweiten Ehe 21 Kinder derselben Mutter
    vor = ['Ernst', 'Otto', 'Paul', 'Karl', 'Georg', 'Hans', 'Peter', 'Adam', 'Jakob', 'Martin', 'Christian', 'Hermann', 'Johann',
           'Diedrich', 'Anton', 'Franz', 'Lorenz', 'August', 'Fritz', 'Gustav', 'Albert']
    P('E120V', 'Heinrich /Kahle/', 'M', [ev('BIRT', '1 JAN 1825')], fams=['EF120'])
    P('E123M', 'Anna /Lange/', 'F', [ev('BIRT', '1 JAN 1830')], fams=['EF120', 'EF123'])
    P('E123V', 'Johann /Meyer/', 'M', [ev('BIRT', '1 JAN 1828')], fams=['EF123'])
    k120 = [f'E120K{i}' for i in range(1, 18)]
    for i, k in enumerate(k120):
        P(k, f'{vor[i]} /Kahle/', 'M', [ev('BIRT', f'1 JAN {1850 + i}')], famc=['EF120'])
    F('EF120', 'E120V', 'E123M', k120)
    k123 = [f'E123K{i}' for i in range(1, 5)]
    for i, k in enumerate(k123):
        P(k, f'{vor[17 + i]} /Meyer/', 'M', [ev('BIRT', f'1 JUN {1867 + i}')], famc=['EF123'])
    F('EF123', 'E123V', 'E123M', k123)
    b.fall('120', ['EF120'], '17 Kinder in einer Ehe (Grenze 16)')
    b.fall('123', ['E123M'], 'Mutter mit 21 Kindern aus zwei Ehen (Grenze 20)')
    P('E121', 'Hinrich /Nagel/', 'M', [ev('BIRT', '1 JAN 1820')], fams=[f'EF121{c}' for c in 'ABCD'])
    for i, c in enumerate('ABCD'):
        P(f'E121{c}', f'{["Martha", "Emma", "Berta", "Ida"][i]} /{["Oltmann", "Peters", "Reese", "Stolte"][i]}/', 'F',
          [ev('BIRT', f'1 JAN {1822 + i}')], fams=[f'EF121{c}'])
        F(f'EF121{c}', 'E121', f'E121{c}')
    b.fall('121', ['E121'], 'Vier Ehen (Grenze 3)')
    P('E122', 'Hinrich /Tamm/', 'M', [ev('BIRT', '1 JAN 1840')], fams=['EF122A', 'EF122B'])
    P('E122A', 'Martha /Uhde/', 'F', [ev('BIRT', '1 JAN 1842'), ev('DEAT', '1 JAN 1880')], fams=['EF122A'])
    P('E122B', 'Emma /Voss/', 'F', [ev('BIRT', '1 JAN 1850')], fams=['EF122B'])
    F('EF122A', 'E122', 'E122A', heirat='1 MAY 1865')
    F('EF122B', 'E122', 'E122B', heirat='15 JAN 1880')
    b.fall('122', ['E122', 'EF122B'], 'Wiederheirat zwei Wochen nach dem Tod der ersten Frau (Grenze 2 Monate)')
    b.eltern_kind('124', vater=('1 JAN 1820', None), mutter=None,
                  kinder=[('1 JAN 1850', 'Ernst', 'M'), ('1 JAN 1870', 'Otto', 'M')], nachname='Wolter')
    b.fall('124', ['E124K2', 'EF124'], '20 Jahre zwischen zwei Geschwistern (Grenze 12)')
    P('E125A', 'Hinrich /Zander/', 'M', [ev('BIRT', '1 JAN 1830'), ev('DEAT', '1 JAN 1870')], fams=['EF125'])
    P('E125B', 'Martha /Albers/', 'F', [ev('BIRT', '1 JAN 1840')], fams=['EF125'])
    F('EF125', 'E125A', 'E125B', heirat='1 JAN 1875')
    b.fall('125', ['E125A', 'EF125'], 'Heirat 1875 nach dem eigenen Tod 1870')
    P('E126P', 'Wilhelm /Brandt/', 'M', [ev('BIRT', '1 JAN 1850')])
    P('E126', 'Ludwig /Cordes/', 'M', [ev('BIRT', '1 JAN 1860'), ev('CHR', '5 JAN 1860', extra=b.pate('E126P'))])
    b.fall('126', ['E126'], 'Pate bei der Taufe 10 Jahre alt (Grenze 12)')
    P('E127', 'Hinrich /Dettmer/', 'M', [ev('BIRT', '1 JAN 1850')])
    b.fall('127', ['E127'], 'Geboren 1850, keine Sterbeangabe')

    # 2xx Struktur
    P('E210', None, None)
    b.fall('210', ['E210'], 'Person ohne Namen, ohne Angaben, ohne Familie')
    P('E211', 'Hinrich /Engel/', 'M', [ev('BIRT', '1 JAN 1850')])
    b.fall('211', ['E211'], 'Person in keiner Familie')
    P('E212A', 'Hinrich /Fuchs/', 'M', [ev('BIRT', '1 JAN 1850')], fams=['EF212'])
    P('E212B', None, None, fams=['EF212'])
    F('EF212', 'E212A', 'E212B')
    b.fall('212', ['E212B', 'EF212'], 'Ehefrau ohne jede Angabe, Ehe ohne Kinder')
    P('E213', 'Ernst /Grote/', 'M', [ev('BIRT', '1 JAN 1870')], famc=['EF213A', 'EF213B'])
    P('E213A', 'Heinrich /Grote/', 'M', [ev('BIRT', '1 JAN 1840')], fams=['EF213A'])
    P('E213B', 'Johann /Hahn/', 'M', [ev('BIRT', '1 JAN 1842')], fams=['EF213B'])
    F('EF213A', 'E213A', None, ['E213'])
    F('EF213B', 'E213B', None, ['E213'])
    b.fall('213', ['E213'], 'Kind in zwei Familien')
    P('E214', 'Hinrich /Hesse/', 'M', [ev('BIRT', '1 JAN 1850')], famc=['EF214'], fams=['EF214'])
    F('EF214', 'E214', None, ['E214'])
    b.fall('214', ['E214', 'EF214'], 'Vater und Kind derselben Familie')
    P('E215A', 'Hinrich /Jansen/', 'M', [ev('BIRT', '1 JAN 1850')], fams=['EF215'])
    P('E215B', 'Ludwig /Kruse/', 'M', [ev('BIRT', '1 JAN 1852')], fams=['EF215'])
    F('EF215', 'E215A', 'E215B')
    b.fall('215', ['E215A', 'EF215'], 'Beide Ehepartner männlich')
    P('E216A', 'Martha /Lohmann/', 'F', [ev('BIRT', '1 JAN 1850')], fams=['EF216'])
    P('E216B', 'Hinrich /Mertens/', 'M', [ev('BIRT', '1 JAN 1852')], fams=['EF216'])
    F('EF216', 'E216A', 'E216B')
    b.fall('216', ['E216A', 'E216B', 'EF216'], 'Frau als Vater, Mann als Mutter eingetragen')
    F('EF217', rest=ev('MARR', '1 JAN 1880'))
    b.fall('217', ['EF217'], 'Familie ohne Partner und ohne Kinder')
    P('E219A', 'Wilhelm /Niemann/', 'M', [ev('BIRT', '3 MAR 1855')])
    P('E219B', 'Wilhelm /Niemann/', 'M', [ev('BIRT', '3 MAR 1855')])
    b.fall('219', ['E219A', 'E219B'], 'Gleicher Name und gleiches Geburtsdatum')
    b.eltern_kind('220P', vater=('1 JAN 1820', None), mutter=('1 JAN 1825', None),
                  kinder=[('1 JAN 1850', 'Hinrich', 'M'), ('1 JAN 1852', 'Martha', 'F')], nachname='Otten')
    # die beiden Geschwister heiraten einander: FAMS nachtragen
    for x in ('E220PK1', 'E220PK2'):
        i = b.zeilen.index(f'0 @{x}@ INDI')
        b.zeilen.insert(b.zeilen.index('1 FAMC @EF220P@', i) + 1, '1 FAMS @EF220@')
    F('EF220', 'E220PK1', 'E220PK2')
    b.fall('220', ['E220PK1', 'EF220'], 'Ehepartner sind Geschwister')
    P('E221V', 'Hinrich /Pape/', 'M', [ev('BIRT', '1 JAN 1820')], fams=['EF221P', 'EF221'])
    P('E221T', 'Martha /Pape/', 'F', [ev('BIRT', '1 JAN 1850')], famc=['EF221P'], fams=['EF221'])
    F('EF221P', 'E221V', None, ['E221T'])
    F('EF221', 'E221V', 'E221T')
    b.fall('221', ['E221V', 'EF221'], 'Vater heiratet seine Tochter')
    P('E222', 'Hinrich /Rieck/', 'M', [ev('BIRT', '1 JAN 1840')], fams=['EF222A', 'EF222B'])
    P('E222A', 'Martha /Sasse/', 'F', [ev('BIRT', '1 JAN 1842'), ev('DEAT', '1 JAN 1900')], fams=['EF222A'])
    P('E222B', 'Emma /Thode/', 'F', [ev('BIRT', '1 JAN 1850')], fams=['EF222B'])
    F('EF222A', 'E222', 'E222A', heirat='1 MAY 1865')
    F('EF222B', 'E222', 'E222B', heirat='1 MAY 1890')
    b.fall('222', ['E222', 'EF222B'], 'Zweite Heirat 1890, erste Frau lebt bis 1900')
    P('E223A', 'Hinrich /Gleich/', 'M', [ev('BIRT', '1 JAN 1850')], fams=['EF223'])
    P('E223B', 'Martha /Gleich/', 'F', [ev('BIRT', '1 JAN 1852')], fams=['EF223'])
    F('EF223', 'E223A', 'E223B')
    b.fall('223', ['E223A', 'EF223'], 'Beide Ehepartner heißen Gleich')
    b.eltern_kind('224', vater=('1 JAN 1920', None), mutter=('1 JAN 1925', None),
                  kinder=[('1 JAN 1950', 'Peter', 'M'), ('1 JAN 1955', 'Peter', 'M')], nachname='Vietz')
    b.fall('224', ['E224K2', 'EF224'], 'Zwei lebende Brüder heißen Peter')
    P('E225A', 'Hinrich /Wille/', 'M', [ev('BIRT', '1 JAN 1850')], famc=['EF225A'], fams=['EF225B'])
    P('E225B', 'Ludwig /Wille/', 'M', [ev('BIRT', '1 JAN 1820')], famc=['EF225B'], fams=['EF225A'])
    F('EF225A', 'E225B', None, ['E225A'])
    F('EF225B', 'E225A', None, ['E225B'])
    b.fall('225', ['E225A', 'E225B'], 'Zwei Personen sind gegenseitig Vater (eigener Vorfahr)')
    P('E226A', 'Hinrich /Ahlers/', 'M', [ev('BIRT', '1 JAN 1850')], fams=['EF226A', 'EF226B'])
    P('E226B', 'Martha /Bruns/', 'F', [ev('BIRT', '1 JAN 1852')], fams=['EF226A', 'EF226B'])
    F('EF226A', 'E226A', 'E226B', heirat='1 MAY 1875')
    F('EF226B', 'E226A', 'E226B', heirat='1 MAY 1875')
    b.fall('226', ['EF226B'], 'Dasselbe Paar zweimal als Familie')
    P('E228A', 'Friedrich /Mustermann/', 'M', [ev('BIRT', '1 JAN 1850')])
    P('E228B', 'Friedrich /Mustermann/', 'M', [ev('BIRT', '1 JUN 1851')])
    b.fall('228', ['E228A', 'E228B'], 'Gleicher Name, Geburt 1850 und 1851')
    P('E319A', 'Hinrich /Dirks/', 'M', [ev('BIRT', '1 JAN 1850')], fams=['EF319'])
    P('E319B', 'Friedel /Eilers/', 'U', [ev('BIRT', '1 JAN 1852')], fams=['EF319'])
    F('EF319', 'E319A', 'E319B')
    b.fall('319', ['E319B', 'EF319'], 'Ehepartner mit unbekanntem Geschlecht')

    # 3xx Namen
    P('E310', 'Hans /Maria/', 'M', [ev('BIRT', '1 JAN 1850')])
    b.fall('310', ['E310'], 'Nachname Maria')
    P('E311', 'N.N. /Busch/', 'M', [ev('BIRT', '1 JAN 1850')])
    b.fall('311', ['E311'], 'Vorname N.N.')
    P('E315', 'Hans /Meier 1850/', 'M', [ev('BIRT', '1 JAN 1850')])
    b.fall('315', ['E315'], 'Jahreszahl im Nachnamen')
    P('E330', 'Anna /Friese/', 'M', [ev('BIRT', '1 JAN 1850')])
    b.fall('330', ['E330'], 'Mann mit Vornamen Anna')

    # 4xx Quellen (beide Regeln sind standardmaessig aus)
    P('E420', 'Hinrich /Haase/', 'M', [ev('BIRT', '1 JAN 1850')], rest=['1 SOUR @S1@', '2 PAGE Personenquelle'])
    b.fall('420', ['E420'], 'Geburt ohne Quelle, die Person selbst hat eine')
    P('E421', 'Hinrich /Jürgens/', 'M', [ev('BIRT', '1 JAN 1850')])
    b.fall('421', ['E421'], 'Person ganz ohne Quelle')

    # 5xx Orte
    herrmannsburg = ('Herrmannsburg, Celle, Niedersachsen, Deutschland', 'N52.8297', 'E10.0931')
    P('E510', 'Hinrich /Kuhlmann/', 'M', [ev('BIRT', '1 JAN 1850', herrmannsburg)])
    b.fall('510', ['E510'], 'Herrmannsburg neben Hermannsburg')
    P('E511', 'Hinrich /Lüdeke/', 'M', [['1 BIRT', '2 DATE 1 JAN 1850', '2 PLAC Hambühren, Celle, Niedersachsen, Deutschland']])
    b.fall('511', ['E511'], 'Ort Hambühren ohne Koordinaten')
    P('E512', 'Hinrich /Meinke/', 'M', [ev('BIRT', '1 JAN 1850'), ev('CHR', '1 JAN 1850', PADERBORN)])
    b.fall('512', ['E512'], 'Geburt in Celle, Taufe am selben Tag in Paderborn (ca. 170 km)')
    P('E513', 'Hinrich /Nordmann/', 'M', [ev('BIRT', '1 JAN 1850', ('Celle,, Niedersachsen, Deutschland', 'N52.6226', 'E10.0815'))])
    b.fall('513', ['E513'], 'Ortsname mit doppeltem Komma')

    # 6xx Form
    P('E611', 'Hinrich /Ohlsen/', 'M', [ev('BIRT', '1 JAN 1850')], famc=['EF999'])
    b.fall('611', ['E611'], 'FAMC zeigt auf @EF999@, die es nicht gibt')
    P('E612', 'Hinrich /Prieß/', 'M', [ev('BIRT', '1 JAN 1850')])
    P('E612', 'Ludwig /Prieß/', 'M', [ev('BIRT', '1 JAN 1852')])
    b.fall('612', ['E612'], 'Kennung @E612@ zweimal vergeben')
    P('E613', 'Hinrich /Riemer/', 'M', [ev('BIRT', '15.03.1850')])
    b.fall('613', ['E613'], 'Datum 15.03.1850')
    P('E614', None, 'M', [ev('BIRT', '1 JAN 1850')])
    b.fall('614', ['E614'], 'Person ohne NAME')
    P('E615', 'Hinrich /Schütte/', 'M', [ev('BIRT', '1 JAN 1850'), ev('BIRT', '1 JAN 1851')])
    b.fall('615', ['E615'], 'Zwei Geburten')
    P('E616', 'Hinrich /Timm/', 'M', [ev('BIRT', '1 JAN 1850')], famc=['EF616'])
    P('E616V', 'Heinrich /Timm/', 'M', [ev('BIRT', '1 JAN 1820')], fams=['EF616'])
    F('EF616', 'E616V')
    b.fall('616', ['E616'], 'FAMC zu einer Familie, die das Kind nicht als CHIL hat')
    P('E618', 'Hinrich /Uhlig/', 'M', [ev('BIRT', '1 JAN 1850')], rest=['1 HOBBY Angeln'])
    b.fall('618', ['E618'], 'Tag HOBBY (Regel standardmaessig aus)')
    P('E619', 'Friedel /Vollmer/', 'U', [ev('BIRT', '1 JAN 1850')])
    b.fall('619', ['E619'], 'Geschlecht U (Regel standardmaessig aus)')
    P('E625', 'Hinrich /Wiebe/', 'M', [ev('BIRT', '1 JAN 1850'), ev('EMIG', '1 MAY 1880', wert='Mit dem Dampfer nach New York')])
    b.fall('625', ['E625'], 'Text hinter EMIG')
    if sieben:
        P('E624', 'Hinrich /Zeller/', 'f', [['1 BIRT', '2 DATE 1 JAN 1850'] + ort() + ['3 EXID ZELLERJO52', '3 LANG German']],
          rest=['1 NOTE Erste Zeile', '2 CONC  und Fortsetzung', '1 ASSO @E024P@', '2 RELA godparent', '1 ASSO @E024P@', '2 ROLE godparent'])
        b.zeilen += ['0 @E624M@ OBJE', '1 FILE fehler.jpg', '2 FORM jpg', '3 TYPE photo']
        b.fall('624', ['E624', 'E624M'], 'CONC, RELA, ROLE godparent, SEX f, EXID ohne TYPE, LANG German, FORM jpg mit TYPE, CHAR und FILE im Kopf')
    return b


def kopf_ersetzen(text, sieben):
    """Fehler im Kopf: CHAR UNICODE (617), SUBM @U9@ (620), FILE (621), _ADDENDUM 2.0 (622), DATE 15.10.2026 (623)."""
    kopf, rest = text.split('\n0 @', 1)
    neu = []
    for z in kopf.split('\n'):
        if z == '1 SUBM @U1@':
            z = '1 SUBM @U9@'
        elif z.startswith('1 DATE '):
            z = '1 DATE 15.10.2026'
        elif z.startswith('1 FILE '):
            z = '1 FILE falkenrath-1.7.ged'
        elif z == '1 CHAR UTF-8':
            z = '1 CHAR UNICODE'
        elif z.startswith('3 _ADDENDUM'):
            z = '3 _ADDENDUM GEDCOM-L'
        elif z.startswith('4 VERS R2'):
            z = '4 VERS 2.0'
        neu.append(z)
        if z == '2 CONT Alle Personen und Lebensdaten sind frei erfunden. Daten und Bilder: CC0.':
            neu.append('2 CONT Fehlerdatei mit absichtlichen Fehlern, siehe fehlerfaelle.tsv.')
    if sieben:
        i = neu.index('2 VERS 7.0')
        neu[i + 1:i + 1] = ['3 _ADDENDUM GEDCOM-L Addendum', '4 VERS R2 (2020-12-01)']
        i = neu.index('1 SUBM @U9@')
        neu[i + 1:i + 1] = ['1 FILE falkenrath-1.7.ged']
        i = neu.index('1 LANG de')
        neu[i:i] = ['1 CHAR UNICODE']
    return '\n'.join(neu) + '\n0 @' + rest


def bauen(sieben, quelle_text):
    text = kopf_ersetzen(quelle_text, sieben)
    b = fehlerblock(sieben)
    zeilen = b.zeilen
    zeilen.insert(zeilen.index('0 @E611@ INDI'), 'Diese Zeile ist kein GEDCOM.')
    b.fall('610', ['(Datei)'], 'Zeile "Diese Zeile ist kein GEDCOM." vor @E611@')
    b.fall('617', ['(Kopf)'], '1 CHAR UNICODE (UTF-16), Datei ist UTF-8')
    b.fall('620', ['(Kopf)'], '1 SUBM @U9@, den Einsender gibt es nicht')
    if not sieben:
        b.fall('621', ['(Kopf)'], '1 FILE falkenrath-1.7.ged, Datei heisst anders')
    b.fall('622', ['(Kopf)'], '_ADDENDUM GEDCOM-L mit VERS 2.0' if not sieben else '_ADDENDUM in einer GEDCOM-7-Datei')
    b.fall('623', ['(Kopf)'], '1 DATE 15.10.2026')
    assert text.endswith('0 TRLR\n')
    text = text[:-len('0 TRLR\n')] + '\n'.join(zeilen) + '\n0 TRLR\n'
    return text, sorted(b.tabelle)


def main():
    os.makedirs(ZIEL, exist_ok=True)
    quelle = open(QUELLE, encoding='utf-8').read()
    with tempfile.TemporaryDirectory() as tmp:
        g7 = os.path.join(tmp, 'g7.ged')
        subprocess.run([sys.executable, os.path.join(BASE, 'werkzeuge', 'gedcom7.py'), QUELLE, g7], check=True, stdout=subprocess.DEVNULL)
        quelle7 = open(g7, encoding='utf-8').read()
    alle = []
    for sieben, name, q in ((False, 'falkenrath-1.7-fehler.ged', quelle), (True, 'falkenrath-1.7-fehler-gedcom7.ged', quelle7)):
        text, tabelle = bauen(sieben, q)
        open(os.path.join(ZIEL, name), 'w', encoding='utf-8', newline='\n').write(text)
        alle += tabelle
        print(f'{name}: {len(tabelle)} Fehlerfaelle')
    with open(os.path.join(ZIEL, 'fehlerfaelle.tsv'), 'w', encoding='utf-8') as f:
        f.write('regel\tversion\tkennungen\tfehler\n')
        for r in sorted(alle, key=lambda r: (r[0], r[1])):
            f.write('\t'.join(r) + '\n')


if __name__ == '__main__':
    main()
