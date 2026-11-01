#!/usr/bin/env python3
"""Demo-Stammbaum 1.7 -> 1.7.1: Tippfehler in der GOV-Kennung von Bienenbüttel (Stand 2026-11-01).

gedcoml.py (1.6 -> 1.7) schrieb an 94 Orten der Ereignisse `3 _GOV BIETELJO53FD` (Buchstabe L), der Ortsdatensatz L1
trägt die echte Kennung `1 _GOV BIETE1JO53FD` (Ziffer 1). Gefunden beim Import in wisetrees, der die abweichende
Kennung als Widerspruch zum Ortsdatensatz meldete. Sonst ändert sich nur der Kopf (Version, Datum, Dateiname).

Aufruf:  python3 werkzeuge/govfix.py versionen/falkenrath-1.7.ged versionen/falkenrath-1.7.1.ged
"""
import sys

quelle, ziel = sys.argv[1], sys.argv[2]
text = open(quelle, encoding="utf-8").read()
if "\n2 VERS 1.7\n" not in text.split("\n0 ", 1)[0] + "\n":
    sys.exit("Kopf ist nicht Version 1.7")
falsch = "\n3 _GOV BIETELJO53FD\n"
anzahl = text.count(falsch)
if anzahl != 94:
    sys.exit(f"erwartet 94 falsche _GOV, gefunden {anzahl}")
text = text.replace(falsch, "\n3 _GOV BIETE1JO53FD\n")
kopf, rest = text.split("\n0 ", 1)
kopf = kopf.replace("\n2 VERS 1.7\n", "\n2 VERS 1.7.1\n", 1)
kopf = kopf.replace("\n1 DATE 15 OCT 2026\n", "\n1 DATE 1 NOV 2026\n", 1)
kopf = kopf.replace("\n1 FILE falkenrath-1.7.ged\n", "\n1 FILE falkenrath-1.7.1.ged\n", 1)
open(ziel, "w", encoding="utf-8", newline="").write(kopf + "\n0 " + rest)
print(f"{ziel}: {anzahl} _GOV berichtigt")
