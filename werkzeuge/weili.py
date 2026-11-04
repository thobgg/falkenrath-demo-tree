#!/usr/bin/env python3
"""Demo-Stammbaum 1.7.1 -> 1.8: Wei Li, Einwanderer aus China, heiratet Julia Schnehage (Stand 2026-11-04).

Neu ist ein Datum aus einem anderen Kalender: Wei Lis Geburt steht in seinen Papieren nach dem chinesischen
Mondkalender, 庚辰年八月十五 (15. Tag des 8. Monats im Jahr Gengchen, das Mondfest), umgerechnet der 12.9.2000.
GEDCOM 5.5.1 schreibt das als interpretiertes Datum mit dem Wortlaut in Klammern (`INT 12 SEP 2000 (…)`), GEDCOM 7.0
als `DATE 12 SEP 2000` mit `PHRASE` – so bleibt der Wortlaut der Quelle erhalten, und jedes Programm kann sortieren.

  I493   Wei Li, geboren 2000 in Suzhou, Einwanderung 2019 nach Lüneburg, Ingenieur
  F155   Wei Li und Julia Schnehage (I489), standesamtliche Heirat 10.9.2022 in Lüneburg (Quelle S195)
  I489   bekommt FAMS @F155@

Aufruf:  python3 werkzeuge/weili.py versionen/falkenrath-1.7.1.ged versionen/falkenrath-1.8.ged
"""
import sys
import uuid


def paf_uid(xref):
    """Wie gedcoml.py: UUID5 aus der Kennung, Großbuchstaben ohne Striche, dazu die Prüfsumme nach Gordon Clarke."""
    uid = uuid.uuid5(uuid.NAMESPACE_URL, "https://github.com/thobgg/falkenrath-demo-tree/" + xref).hex.upper()
    a = b = 0
    for i in range(0, 32, 2):
        a += int(uid[i:i + 2], 16)
        b += a
    return uid + f"{a & 0xff:02X}{b & 0xff:02X}"


LUENEBURG = "Lüneburg, Niedersachsen, Deutschland\n3 MAP\n4 LATI N53.2509\n4 LONG E10.4141"

WEI_LI = f"""0 @I493@ INDI
1 NAME Wei /Li/
2 GIVN Wei
2 SURN Li
1 SEX M
1 BIRT
2 DATE INT 12 SEP 2000 (庚辰年八月十五)
2 PLAC Suzhou, Jiangsu, China
3 MAP
4 LATI N31.2989
4 LONG E120.5853
1 IMMI
2 DATE 2019
2 PLAC {LUENEBURG}
1 OCCU Ingenieur
1 FAMS @F155@
1 _UID {paf_uid("I493")}
"""

FAMILIE = f"""0 @F155@ FAM
1 HUSB @I493@
1 WIFE @I489@
1 MARR
2 TYPE civil
2 DATE 10 SEP 2022
2 PLAC {LUENEBURG}
2 SOUR @S195@
3 PAGE Heirat 2022/41
1 _UID {paf_uid("F155")}
"""

quelle, ziel = sys.argv[1], sys.argv[2]
text = open(quelle, encoding="utf-8").read()
if "\n2 VERS 1.7.1\n" not in text.split("\n0 ", 1)[0] + "\n":
    sys.exit("Kopf ist nicht Version 1.7.1")
if "\n0 @I493@ " in text or "\n0 @F155@ " in text:
    sys.exit("I493 oder F155 gibt es schon")


def einfuegen(text, vor, neu):
    """Neuen Datensatz vor dem Datensatz `vor` einfügen."""
    marke = "\n" + vor
    if text.count(marke) != 1:
        sys.exit(f"{vor!r} nicht genau einmal gefunden")
    return text.replace(marke, "\n" + neu.rstrip("\n") + marke, 1)


# Personen stehen vor den Familien, Familien vor den Quellen
text = einfuegen(text, "0 @F1@ FAM\n", WEI_LI)
text = einfuegen(text, "0 @S1@ SOUR\n", FAMILIE)

julia = "0 @I489@ INDI\n"
anfang = text.index(julia)
ende = text.index("\n0 ", anfang)
datensatz = text[anfang:ende]
if "\n1 FAMC @F153@" not in datensatz or "\n1 FAMS " in datensatz:
    sys.exit("I489 sieht anders aus als erwartet")
text = text[:anfang] + datensatz.replace("\n1 FAMC @F153@", "\n1 FAMC @F153@\n1 FAMS @F155@", 1) + text[ende:]

kopf, rest = text.split("\n0 ", 1)
kopf = kopf.replace("\n2 VERS 1.7.1\n", "\n2 VERS 1.8\n", 1)
kopf = kopf.replace("\n1 DATE 1 NOV 2026\n", "\n1 DATE 4 NOV 2026\n", 1)
kopf = kopf.replace("\n1 FILE falkenrath-1.7.1.ged\n", "\n1 FILE falkenrath-1.8.ged\n", 1)
open(ziel, "w", encoding="utf-8", newline="").write(kopf + "\n0 " + rest)
print(f"{ziel}: I493 Wei Li und F155 ergänzt")
