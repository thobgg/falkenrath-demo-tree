#!/usr/bin/env python3
"""Demo-Stammbaum als FamilySearch GEDCOM 7.0 ausgeben (Stand 2026-10-14).

Die Hauptdatei bleibt GEDCOM 5.5.1 (webtrees 2.2 liest nur 5.5.1). Dieses Skript leitet daraus eine gleichwertige
GEDCOM-7.0-Fassung ab – für das GEDZIP (.gdz), das nach dem Standard eine GEDCOM-7-Datei enthalten muss, und als
Testmaterial für Programme, die GEDCOM 7 lesen. Was sich ändert:

  Kopf          GEDC VERS 7.0 ohne _ADDENDUM (gilt für 5.5.1), ohne GEDC.FORM, CHAR und FILE; LANG German -> de
  CONC          entfällt, Fortsetzungen werden an die Zeile angehängt
  _UID, _ASSO   werden die Standard-Tags UID und ASSO (Werte unverändert)
  RELA          wird ROLE mit Aufzählungswert (godparent -> GODP, witness -> WITN; godfather/godmother -> GODP mit
                PHRASE); `ROLE (Pate)` an Quellenangaben -> ROLE OTHER mit PHRASE Pate
  _GODP, _WITN  Paten/Zeugen ohne Datensatz -> ASSO @VOID@ mit PHRASE (Name) und ROLE GODP/WITN – so sieht GEDCOM 7
                Personen ohne eigenen Datensatz vor
  _GOV am Ort   wird PLAC.EXID mit TYPE https://gov.genealogy.net/ (registrierter Typ); im Ortsdatensatz _LOC bleibt
                _GOV, denn der ganze _LOC-Datensatz ist GEDCOM-L-Erweiterung
  Medien        FORM jpg -> image/jpeg, FORM.TYPE -> FORM.MEDI (photo -> PHOTO, document -> OTHER mit PHRASE)
  CALN.MEDI     book -> BOOK, electronic -> ELECTRONIC
  Textquelle    `SOUR <Text>` ohne Datensatz -> eigener SOUR-Datensatz mit TITL, TEXT unter DATA

Alle übrigen GEDCOM-L-Tags (_LOC, _GOVTYPE, _POST, _MAIDENHEAD, _RUFNAME, _PRIM, _TODO, _STAT, …) bleiben als
Erweiterungen stehen. Sie sind nicht über HEAD.SCHMA angemeldet, weil GEDCOM-L (noch) keine URIs dafür
veröffentlicht hat; GEDCOM 7 erlaubt solche „undokumentierten“ Erweiterungs-Tags.

Aufruf:  python3 werkzeuge/gedcom7.py versionen/falkenrath-1.7.ged <ziel.ged>
"""
import sys

sys.path.insert(0, sys.path[0])
import ged  # noqa: E402
from ged import Node  # noqa: E402

SRC, OUT = sys.argv[1:3]
root = ged.parse(open(SRC, encoding='utf-8').read())
recs = {r.xref: r for r in root.children if r.xref}

ROLE = {'godparent': ('GODP', None), 'godfather': ('GODP', 'godfather'), 'godmother': ('GODP', 'godmother'),
        'witness': ('WITN', None)}
ROLES = {'CHIL', 'CLERGY', 'FATH', 'FRIEND', 'GODP', 'HUSB', 'MOTH', 'MULTIPLE', 'NGHBR', 'OFFICIATOR', 'OTHER',
         'PARENT', 'SPOU', 'WIFE', 'WITN'}
MEDI = {'AUDIO', 'BOOK', 'CARD', 'ELECTRONIC', 'FICHE', 'FILM', 'MAGAZINE', 'MANUSCRIPT', 'MAP', 'NEWSPAPER', 'OTHER',
        'PHOTO', 'TOMBSTONE', 'VIDEO'}
MIME = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'pdf': 'application/pdf'}
LANG = {'German': 'de', 'English': 'en'}
GOV_TYPE = 'https://gov.genealogy.net/'
count = {}


def tally(what):
    count[what] = count.get(what, 0) + 1


def enum(node, tag, value, allowed):
    """Aufzählungswert setzen; Unbekanntes wird OTHER mit PHRASE."""
    v = value.strip().strip('()')
    if v.upper() in allowed:
        node.tag, node.value = tag, v.upper()
    else:
        node.tag, node.value = tag, 'OTHER'
        node.children.insert(0, Node('PHRASE', v))


def merge_conc(node):
    kept = []
    for c in node.children:
        if c.tag == 'CONC':
            target = kept[-1] if kept and kept[-1].tag == 'CONT' else node
            target.value = (target.value or '') + (c.value or '')
            tally('CONC entfernt')
        else:
            kept.append(c)
    node.children = kept


new_sources = []
next_s = max(int(x.strip('@S')) for x in recs if x.startswith('@S')) + 1


def convert(node, parent, record):
    global next_s
    merge_conc(node)
    t = node.tag
    if t == '_UID':
        node.tag = 'UID'; tally('_UID -> UID')
    elif t == '_ASSO':
        node.tag = 'ASSO'; tally('_ASSO -> ASSO')
    elif t == 'RELA':
        role, phrase = ROLE.get(node.value.lower(), ('OTHER', node.value))
        node.tag, node.value = 'ROLE', role
        if phrase:
            node.children.insert(0, Node('PHRASE', phrase))
        tally('RELA -> ROLE')
    elif t == 'ROLE' and parent.tag == 'EVEN':
        enum(node, 'ROLE', node.value, ROLES); tally('ROLE (…) -> ROLE OTHER')
    elif t == 'LANG' and node.value in LANG:
        node.value = LANG[node.value]; tally('LANG -> BCP 47')
    elif t == 'FORM' and parent.tag == 'FILE':
        node.value = MIME[node.value.lower()]; tally('FORM -> Medientyp')
        for c in node.children:
            if c.tag == 'TYPE':
                enum(c, 'MEDI', c.value, MEDI); tally('FORM.TYPE -> MEDI')
    elif t == 'MEDI' and parent.tag == 'CALN':
        enum(node, 'MEDI', node.value, MEDI); tally('CALN.MEDI groß')
    elif t == '_GOV' and parent.tag == 'PLAC':
        node.tag = 'EXID'; node.children.append(Node('TYPE', GOV_TYPE)); tally('PLAC._GOV -> EXID')
    elif t == 'SOUR' and record.tag != 'SOUR' and node.value and not node.value.startswith('@'):
        xref = f'@S{next_s}@'; next_s += 1
        rec = Node('SOUR', xref=xref); rec.add('TITL', node.value); new_sources.append(rec)
        node.value = xref
        texts = [c for c in node.children if c.tag == 'TEXT']
        if texts:
            data = Node('DATA', None, children=texts)
            node.children = [c for c in node.children if c.tag != 'TEXT']
            node.children.insert(0, data)
        tally('Textquelle -> SOUR-Datensatz')
    for c in list(node.children):
        convert(c, node, record)
    # Paten/Zeugen ohne Datensatz: ASSO @VOID@ an derselben Stelle
    out = []
    for c in node.children:
        if c.tag in ('_GODP', '_WITN') and node.tag in ('CHR', 'BAPM', 'MARR'):
            a = Node('ASSO', '@VOID@')
            a.add('PHRASE', c.value)
            a.add('ROLE', 'GODP' if c.tag == '_GODP' else 'WITN')
            a.children.extend(c.children)
            out.append(a); tally(f'{c.tag} -> ASSO @VOID@')
        else:
            out.append(c)
    node.children = out


head, body = root.children[0], root.children[1:]
for r in body:
    convert(r, root, r)

# Kopf: 7.0 ohne CHAR und GEDC.FORM
gedc = head.first('GEDC')
gedc.first('VERS').value = '7.0'
gedc.first('VERS').children = []          # das GEDCOM-L-Addendum gilt für 5.5.1
gedc.children = [c for c in gedc.children if c.tag != 'FORM']
head.children = [c for c in head.children if c.tag not in ('CHAR', 'FILE')]
for c in head.children:
    merge_conc(c)
    if c.tag == 'LANG':
        c.value = LANG.get(c.value, c.value)
note = head.first('NOTE') or head.add('NOTE', '')     # HEAD.NOTE darf in 7.0 nur einmal vorkommen
note.add('CONT', 'Umgewandelt aus der GEDCOM-5.5.1-Fassung.')

trlr = [r for r in body if r.tag == 'TRLR']
body = [r for r in body if r.tag != 'TRLR'] + new_sources + (trlr or [Node('TRLR')])
root.children = [head] + body


def lines(n, level):
    v = n.value
    if v and v.startswith('@') and not (v.startswith('@') and v.endswith('@') and ' ' not in v):
        v = '@' + v                     # GEDCOM 7: führendes @ im Text verdoppeln
    parts = [str(level)] + ([n.xref] if n.xref else []) + [n.tag] + ([v] if v not in (None, '') else [])
    yield ' '.join(parts)
    for c in n.children:
        yield from lines(c, level + 1)


with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    for r in root.children:
        for line in lines(r, 0):
            f.write(line + '\n')
for k, v in sorted(count.items()):
    print(f'{v:5} {k}')
