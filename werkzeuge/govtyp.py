#!/usr/bin/env python3
"""Demo-Stammbaum 1.5 -> 1.6: GOV-Typnummern an den Ortsdatensätzen (Stand 2026-10-13).

GEDCOM-L erlaubt unter "1 TYPE" die Zeile "2 _GOVTYPE <Nummer>" (Typliste gov.genealogy.net/type/list). Die Nummer
ist eindeutig, der Text davor bleibt frei - darum behalten die Gebäude ihre Texte (Mühle, Hof, Haus) und bekommen
die Nummer dazu: Programme und Online-Ortsfamilienbücher erkennen ein Gebäude an der Nummer statt an einem Wort.

    1 TYPE Mühle
    2 _GOVTYPE 87

Nummern: Gemeinde 18, Mühle 87, Hof 24, Gebäude 17. Sonst ändert sich nichts.

Aufruf:  python3 werkzeuge/govtyp.py falkenrath.ged
"""
import sys

GOVTYP = {"Gemeinde": "18", "Mühle": "87", "Hof": "24", "Haus": "17"}

path = sys.argv[1]
lines = open(path, encoding="utf-8").read().split("\n")
out, in_loc, n = [], False, 0
for i, line in enumerate(lines):
    if line.startswith("0 "):
        in_loc = line.endswith(" _LOC")
    if line == "2 VERS 1.5" and out and out[-1].startswith("2 NAME Demo"):
        line = "2 VERS 1.6"
    out.append(line)
    if in_loc and line.startswith("1 TYPE ") and not (i + 1 < len(lines) and lines[i + 1].startswith("2 _GOVTYPE")):
        typ = line[7:].strip()
        if typ in GOVTYP:
            out.append("2 _GOVTYPE " + GOVTYP[typ])
            n += 1
open(path, "w", encoding="utf-8").write("\n".join(out))
print(f"{n} _GOVTYPE-Zeilen ergänzt")
