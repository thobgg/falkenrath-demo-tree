#!/usr/bin/env python3
"""Demo-Stammbaum 1.8 -> 1.9: erfundene DNA-Daten für Jonas Falkenrath (Stand 2026-11-27).

GEDCOM kennt keine eigene Form für DNA-Treffer. Gramps und Gramps Web lesen einen Treffer aus einer Beziehung
(`ASSO`) mit der Art `DNA` und einer Notiz, in der die gemeinsamen Segmente als Tabelle stehen (Chromosom, Start,
Ende, cM, SNPs) – so, wie die Testanbieter sie ausgeben. Die Y-DNA steht als Eigenschaft `FACT` mit `TYPE Y-DNA`,
der Wert ist eine Liste getesteter SNPs mit `+` (vorhanden) oder `-` (nicht vorhanden). Andere Programme zeigen
beides als gewöhnliche Beziehung mit Notiz und als gewöhnliche Eigenschaft.

Alle Werte sind ausgedacht; die Summen passen zur Verwandtschaft im Baum (Richtwerte: Shared cM Project):

  I1 Jonas Falkenrath, Treffer mit
    I12  Sven Marwede      Cousin, väterlich                       etwa 850 cM
    I88  Florian Ahlers    Cousin, mütterlich                      etwa 900 cM, mit X-Chromosom
    I97  Andrea Bock       Cousine der Mutter                      etwa 430 cM, mit X-Chromosom
    I37  Birgit Kass       Cousine des Vaters                      etwa 400 cM
    I94  Emily Falkenrath  Cousine zweiten Grades, väterlich       etwa 230 cM, Tabelle mit Semikolon und Komma
  Y-DNA (gleiche Männerlinie ab Heinrich Falkenrath, I21; SNP-Namen aus dem YFull-Baum 14.06, geprüft mit yclade)
    I1   Jonas Falkenrath    R-S263 (unter R-U106)
    I93  Michael Falkenrath  R-U106, weniger SNPs getestet

Segmente auf dem X-Chromosom haben nur die Verwandten der Mutter: ein Mann erbt sein X von der Mutter.
Die Segmente entstehen aus einem festen Startwert je Person, jeder Lauf ergibt dieselbe Datei.

Aufruf:  python3 werkzeuge/dna.py versionen/falkenrath-1.8.ged versionen/falkenrath-1.9.ged
"""
import random
import sys

# Länge der Chromosomen in Basenpaaren (GRCh37), wie sie Gramps Web zeichnet
LAENGE = {
    "1": 249250621, "2": 243199373, "3": 198022430, "4": 191154276, "5": 180915260, "6": 171115067,
    "7": 159138663, "8": 146364022, "9": 141213431, "10": 135534747, "11": 135006516, "12": 133851895,
    "13": 115169878, "14": 107349540, "15": 102531392, "16": 90354753, "17": 81195210, "18": 78077248,
    "19": 59128983, "20": 63025520, "21": 48129895, "22": 51304566, "X": 155270560,
}
FOLGE = list(LAENGE)

GETESTET = "I1"
# Kennung, Name (zur Prüfung), cM gesamt, Zahl der Segmente, cM auf dem X (0 = keins), deutsche Tabelle
TREFFER = [
    ("I12", "Sven /Marwede/", 850, 25, 0, False),
    ("I88", "Florian /Ahlers/", 900, 27, 38, False),
    ("I97", "Andrea /Bock/", 430, 15, 21, False),
    ("I37", "Birgit /Kass/", 400, 14, 0, False),
    ("I94", "Emily /Falkenrath/", 230, 9, 0, True),
]
YDNA = [
    ("I1", "Jonas /Falkenrath/", "M269+, U106+, Y477958+, Z381+, Z301-"),
    ("I93", "Michael /Falkenrath/", "M269+, U106+"),
]


def segmente(xref, summe, anzahl, x_cm):
    """Erfundene Segmente: Längen aus zufälligen Anteilen (mindestens 8 cM), etwa 1 cM je Megabase, ohne Überlappung."""
    zufall = random.Random("falkenrath-dna-" + xref)
    autosomal = anzahl - (1 if x_cm else 0)
    anteile = [zufall.uniform(0.5, 1.6) for _ in range(autosomal)]
    rest = summe - x_cm - 8 * autosomal
    laengen = [round(8 + rest * a / sum(anteile), 1) for a in anteile]
    belegt = {k: [] for k in FOLGE}
    zeilen = []

    def legen(chromosom, cm):
        bp = int(cm * zufall.uniform(0.85, 1.2) * 1_000_000)
        for _ in range(200):
            start = zufall.randrange(1_000_000, LAENGE[chromosom] - bp - 1_000_000)
            if all(start > e + 2_000_000 or start + bp < a - 2_000_000 for a, e in belegt[chromosom]):
                belegt[chromosom].append((start, start + bp))
                zeilen.append((chromosom, start, start + bp, cm, int(cm * zufall.uniform(190, 240))))
                return True
        return False

    for cm in sorted(laengen, reverse=True):
        # große Chromosomen tragen eher lange Segmente
        wahl = [k for k in FOLGE[:22] if LAENGE[k] > (cm * 1.2 + 6) * 1_000_000 and len(belegt[k]) < 2]
        zufall.shuffle(wahl)
        if not any(legen(k, cm) for k in wahl):
            sys.exit(f"{xref}: Segment mit {cm} cM passt nirgends")
    if x_cm:
        legen("X", float(x_cm))
    zeilen.sort(key=lambda z: (FOLGE.index(z[0]), z[1]))
    return zeilen


def tabelle(zeilen, deutsch):
    """Rohdaten wie aus dem Export eines Anbieters: englisch mit Komma und Punkt oder deutsch mit Semikolon und Komma."""
    if deutsch:
        kopf = "Chromosom;Startposition;Endposition;cM;SNPs"
        return [kopf] + [f"{c};{a};{e};{cm:.1f};{snp}".replace(".", ",") for c, a, e, cm, snp in zeilen]
    return ["Chromosome,Start,End,cM,SNPs"] + [f"{c},{a},{e},{cm:.1f},{snp}" for c, a, e, cm, snp in zeilen]


def datensatz(text, xref, name):
    anfang = text.index(f"\n0 @{xref}@ INDI\n") + 1
    ende = text.index("\n0 ", anfang)
    satz = text[anfang:ende]
    if f"\n1 NAME {name}\n" not in satz + "\n":
        sys.exit(f"{xref} heißt nicht {name}")
    return anfang, ende, satz


def einfuegen(satz, neu):
    """Neue Zeilen vor Bildern, Familien und Kennung des Datensatzes, wo auch die vorhandenen Beziehungen stehen."""
    stellen = [satz.find(m) for m in ("\n1 OBJE ", "\n1 FAMC ", "\n1 FAMS ", "\n1 _UID ") if m in satz]
    if not stellen:
        sys.exit("keine Stelle zum Einfügen gefunden")
    i = min(stellen)
    return satz[:i] + "\n" + "\n".join(neu) + satz[i:]


quelle, ziel = sys.argv[1], sys.argv[2]
text = open(quelle, encoding="utf-8").read()
if "\n2 VERS 1.8\n" not in text.split("\n0 ", 1)[0] + "\n":
    sys.exit("Kopf ist nicht Version 1.8")
if "\n2 RELA DNA\n" in text or "\n2 TYPE Y-DNA\n" in text:
    sys.exit("DNA-Daten gibt es schon")

neu = {}
for xref, name, snps in YDNA:
    neu.setdefault(xref, []).extend([f"1 FACT {snps}", "2 TYPE Y-DNA"])
for xref, name, summe, anzahl, x_cm, deutsch in TREFFER:
    datensatz(text, xref, name)
    zeilen = tabelle(segmente(xref, summe, anzahl, x_cm), deutsch)
    block = [f"1 ASSO @{xref}@", "2 RELA DNA", "2 NOTE " + zeilen[0]] + ["3 CONT " + z for z in zeilen[1:]]
    neu.setdefault(GETESTET, []).extend(block)
    print(f"  {xref} {name.replace('/', '')}: {len(zeilen) - 1} Segmente")

namen = {x: n for x, n, _ in YDNA}
namen.setdefault(GETESTET, "Jonas /Falkenrath/")
for xref, zeilen in neu.items():
    anfang, ende, satz = datensatz(text, xref, namen[xref])
    text = text[:anfang] + einfuegen(satz, zeilen) + text[ende:]

kopf, rest = text.split("\n0 ", 1)
for alt, neu_ in (("\n2 VERS 1.8\n", "\n2 VERS 1.9\n"), ("\n1 DATE 4 NOV 2026\n", "\n1 DATE 27 NOV 2026\n"),
                  ("\n1 FILE falkenrath-1.8.ged\n", "\n1 FILE falkenrath-1.9.ged\n")):
    if alt not in kopf:
        sys.exit(f"Kopfzeile fehlt: {alt.strip()}")
    kopf = kopf.replace(alt, neu_, 1)
open(ziel, "w", encoding="utf-8", newline="").write(kopf + "\n0 " + rest)
print(f"{ziel}: 5 DNA-Treffer an I1, Y-DNA an I1 und I93")
