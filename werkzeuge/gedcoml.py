#!/usr/bin/env python3
"""Demo-Stammbaum 1.6 -> 1.7: die übrigen Angaben des GEDCOM-L-Addendums (Stand 2026-10-14).

Bis 1.6 nutzte der Baum aus GEDCOM-L schon Paten und Zeugen (_GODP, _WITN, _ASSO), Ortsdatensätze (_LOC) mit Art und
GOV-Typnummer. 1.7 ergänzt den Rest, damit Programme jede Angabe des Addendums an echten Daten zeigen und prüfen können:

  Dateikopf        3 _ADDENDUM GEDCOM-L mit Version und Adresse unter GEDC
  alle Datensätze  1 _UID (32 Hexziffern + Prüfsumme wie webtrees/PAF, aus der Kennung abgeleitet, also stabil)
  Personen         2 _RUFNAME bei jeder dritten Person mit zwei Vornamen (der zweite Vorname)
                   2 _PRIM Y am Porträt der Personen, die auch auf dem Gruppenbild M135 sind
                   1 _TODO mit DESC, _CAT, _PRTY, TYPE, STAT, DATE, _RDATE/_CDATE, DATA, REPO, NOTE (drei Aufgaben)
  Familie F22      1 _STAT UNKNOWN (Mutter unbekannt, keine Heirat belegt) mit Notiz
  Ereignisse       3 _GOV, 3 _POST mit Datum, 3 _MAIDENHEAD unter den Orten in Bienenbüttel und seinen Höfen
  Archiv R3        2 _NAME unter ADDR (Empfänger)
  Ortsdatensatz L1 (Bienenbüttel) mit echten Angaben aus GOV und Wikipedia: _GOV BIETE1JO53FD, Name „Kirchspiel
                   Bienenbüttel“ bis 1885, Art Kirchdorf (GOV-Typ 66) bis 1885 vor der Gemeinde, _AIDN 03360004 (AGS),
                   _DMGD 974 Einwohner am 1.12.1880 (GOV, Quelle dort), _MAIDENHEAD JO53FD, RELI, _POST 3116 bis
                   30.6.1993 und 29553 ab 1.7.1993 (GOV)

Aufruf:  python3 werkzeuge/gedcoml.py falkenrath.ged
"""
import re
import sys
import uuid


def paf_uid(xref):
    """Stabile _UID: UUID5 aus der Kennung, Großbuchstaben ohne Striche, dazu die Prüfsumme nach Gordon Clarke."""
    uid = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/thobgg/falkenrath-demo-tree/" + xref).hex.upper()
    a = b = 0
    for i in range(0, 32, 2):
        a += int(uid[i:i + 2], 16)
        b += a
    return uid + f"{a & 0xff:02X}{b & 0xff:02X}"


def maidenhead(lat, lon):
    lon, lat = lon + 180, lat + 90
    s = chr(65 + int(lon // 20)) + chr(65 + int(lat // 10))
    s += str(int((lon % 20) // 2)) + str(int(lat % 10))
    s += chr(65 + int((lon % 2) * 12)) + chr(65 + int((lat % 1) * 24))
    return s


path = sys.argv[1]
text = open(path, encoding="utf-8").read()
if "\n2 VERS 1.6\n" not in text.split("\n0 ", 1)[0] + "\n":
    sys.exit("Erwartet Version 1.6 im Kopf")
records = re.split(r"\n(?=0 )", text)
zahl = {}


def mehr(k, n=1):
    zahl[k] = zahl.get(k, 0) + n


AUFGABEN = {
    "I54": [
        "1 _TODO Mutter von Johann Heinrich und Anna Margarethe suchen",
        "2 DESC Die Mutter der Kinder von Hans Jürgen Falkenrath ist unbekannt; Taufeinträge in Eschede prüfen.",
        "2 _CAT Kirchenbuch",
        "2 _PRTY 1",
        "2 TYPE 0",
        "2 STAT open",
        "2 DATE 1 OCT 2026",
        "2 _RDATE 1 DEC 2026",
        "2 REPO @R3@",
        "2 NOTE Taufbuch Eschede 1795–1805 ist nur im Kirchenbuchamt einsehbar.",
    ],
    "I21": [
        "1 _TODO Militärpass von Heinrich Falkenrath auswerten",
        "2 DESC Dienstzeit im Infanterie-Regiment 77 aus dem Militärpass übertragen.",
        "2 _CAT Militär",
        "2 _PRTY 4",
        "2 TYPE 0",
        "2 STAT completed",
        "2 DATE 12 SEP 2026",
        "2 _CDATE 3 OCT 2026",
        "2 DATA Dienstzeit 1914–1918 übertragen, Ereignis Kriegsdienst ergänzt.",
        "2 REPO @R1@",
    ],
}
FAM_AUFGABE = {
    "F22": [
        "1 _TODO Heirat von Hans Jürgen Falkenrath suchen",
        "2 _CAT Kirchenbuch",
        "2 _PRTY 2",
        "2 TYPE 1",
        "2 STAT open",
        "2 DATE 1 OCT 2026",
        "2 NOTE Anfrage an das Kirchenbuchamt Celle gestellt.",
    ],
}
# Personen auf dem Gruppenbild: ihr Porträt wird das hervorgehobene Bild
gruppenbild = {m.group(1) for r in records for m in [re.match(r"0 @(\w+)@ INDI", r)] if m and "\n1 OBJE @M135@" in r}

out = []
rufname_zaehler = 0
for rec in records:
    lines = rec.split("\n")
    kopf = lines[0]
    m = re.match(r"0 @([^@]+)@ (\w+)", kopf)
    xref, art = (m.group(1), m.group(2)) if m else (None, kopf[2:].strip())
    neu = []
    i = 0
    prim = False
    while i < len(lines):
        line = lines[i]
        # Kopf: Version und Addendum
        if art == "HEAD":
            if line == "2 VERS 1.6":
                line = "2 VERS 1.7"
            neu.append(line)
            if line == "2 VERS 5.5.1" and neu[-2] == "1 GEDC":
                neu += ["3 _ADDENDUM GEDCOM-L", "4 VERS 2.0", "4 WWW https://genealogy.net/GEDCOM/"]
                mehr("_ADDENDUM")
            i += 1
            continue
        neu.append(line)
        # Rufname: zweiter Vorname bei jeder dritten Person mit zwei Vornamen
        if art == "INDI" and line.startswith("2 GIVN ") and len(line[7:].split()) == 2:
            rufname_zaehler += 1
            if rufname_zaehler % 3 == 0:
                neu.append("2 _RUFNAME " + line[7:].split()[1])
                mehr("_RUFNAME")
        # Hervorgehobenes Bild: das Porträt der Personen auf dem Gruppenbild
        if art == "INDI" and xref in gruppenbild and not prim and re.fullmatch(r"1 OBJE @M\d+@", line) and line != "1 OBJE @M135@":
            neu.append("2 _PRIM Y")
            prim = True
            mehr("_PRIM")
        # Orte in Bienenbüttel: GOV-Kennung, Postleitzahl, Maidenhead-Locator
        pm = re.match(r"2 PLAC (.*)Bienenbüttel, Uelzen, Niedersachsen, Deutschland$", line)
        if pm:
            sub, j = [], i + 1
            while j < len(lines) and lines[j][0] in "3456789":
                sub.append(lines[j])
                j += 1
            neu += sub
            i = j
            lat = re.search(r"4 LATI N([\d.]+)", "\n".join(sub))
            lon = re.search(r"4 LONG E([\d.]+)", "\n".join(sub))
            if pm.group(1) == "":
                neu.append("3 _GOV BIETELJO53FD")
                mehr("PLAC:_GOV")
            neu += ["3 _POST 29553", "4 DATE FROM 1 JUL 1993"]
            mehr("PLAC:_POST")
            if lat and lon:
                neu.append("3 _MAIDENHEAD " + maidenhead(float(lat.group(1)), float(lon.group(1))))
                mehr("PLAC:_MAIDENHEAD")
            continue
        # Archiv R3: Empfänger an der Adresse
        if xref == "R3" and line.startswith("1 ADDR"):
            j = i + 1
            while j < len(lines) and lines[j][0] in "23456789":
                neu.append(lines[j])
                j += 1
            neu.append("2 _NAME Kirchenbuchamt, Leseraum")
            mehr("ADDR:_NAME")
            i = j
            continue
        i += 1

    if art == "_LOC" and xref == "L1":
        body = "\n".join(neu)
        body = body.replace("1 NAME Bienenbüttel\n",
                            "1 NAME Bienenbüttel\n2 DATE FROM 1885\n1 NAME Kirchspiel Bienenbüttel\n2 DATE BEF 1885\n2 LANG German\n", 1)
        body = body.replace("1 TYPE Gemeinde\n2 _GOVTYPE 18",
                            "1 TYPE Kirchdorf\n2 DATE BEF 1885\n2 _GOVTYPE 66\n1 TYPE Gemeinde\n2 DATE FROM 1885\n2 _GOVTYPE 18", 1)
        body = body.replace("1 _POST 29553",
                            "1 _POST 3116\n2 DATE BEF 1 JUL 1993\n1 _POST 29553\n2 DATE FROM 1 JUL 1993", 1)
        body += ("\n1 _GOV BIETE1JO53FD"
                 "\n1 _AIDN 03360004\n2 TYPE AGS\n2 DATE FROM 1 JUL 1972"
                 "\n1 _DMGD 974\n2 TYPE Einwohner\n2 DATE 1 DEC 1880"
                 "\n1 _MAIDENHEAD JO53FD"
                 "\n1 RELI evangelisch-lutherisch")
        neu = body.split("\n")
        mehr("_LOC L1")
    if art == "INDI" and xref in AUFGABEN:
        neu += AUFGABEN[xref]
        mehr("_TODO")
    if art == "FAM" and xref in FAM_AUFGABE:
        neu += FAM_AUFGABE[xref]
        mehr("_TODO")
    if art == "FAM" and xref == "F22":
        neu += ["1 _STAT UNKNOWN", "2 NOTE Die Mutter der Kinder ist unbekannt, eine Heirat ist nicht belegt."]
        mehr("_STAT")
    if xref and art in ("INDI", "FAM", "SOUR", "REPO", "OBJE", "NOTE", "_LOC") and not any(l.startswith("1 _UID") for l in neu):
        neu.append("1 _UID " + paf_uid(xref))
        mehr("_UID")
    out.append("\n".join(neu))

open(path, "w", encoding="utf-8").write("\n".join(out))
for k, v in sorted(zahl.items()):
    print(f"{v:5}  {k}")
