#!/usr/bin/env python3
"""Demo-Stammbaum 1.9 -> 1.10: DNA-Einträge in der Schreibweise des webtrees-Moduls dna4webtrees (Stand 2026-11-28).

Version 1.9 enthält DNA-Daten nur in der Schreibweise von Gramps (`1 ASSO` mit `2 RELA DNA`, `1 FACT` mit
`2 TYPE Y-DNA`). Sie bleiben unverändert. Dazu kommen die Formen, die dna4webtrees schreibt:

  Test         1 EVEN <Autosomal|Y-DNA|mtDNA> / 2 TYPE DNA Test / 2 DATE / 2 AGNC / 2 NOTE / 2 RESN
  Haplogruppe  1 FACT <Haplogruppe> / 2 TYPE Y-DNA Haplogroup oder mtDNA Haplogroup / 2 DATE / 2 AGNC / 2 RESN
  Treffer      1 FACT <cM> / 2 TYPE DNA Match / 2 DATE / 2 AGNC / 2 _ASSO @I…@ / 3 RELA DNA / 2 NOTE / 2 RESN
               ohne Datensatz der anderen Person: kein _ASSO, Notizzeile `Match: <Name>`

`RESN` ist `confidential` bei einer lebenden Person und `privacy` bei einer verstorbenen; ein Treffer ist
`confidential`, außer beide Personen stehen im Baum und sind verstorben.

Alle Werte sind ausgedacht. Drei Einträge sind mit Absicht falsch, damit ein Programm seinen Hinweis zeigen kann:

  I27  Haplogruppe I-DF29 auf der Männerlinie, auf der I8 R-U106 hat
  I5   Treffer mit der Cousine I13 mit 180 cM (üblich 396 bis 1397, Shared cM Project 4.0)
  I93  Treffer mit I1 in der Schreibweise von Gramps mit einem Segment auf dem X, ohne gemeinsamen X-Vorfahren

Aufruf:  python3 werkzeuge/dna2.py versionen/falkenrath-1.9.ged versionen/falkenrath-1.10.ged
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

NAMEN = {
    "I1": "Jonas /Falkenrath/", "I5": "Lena /Falkenrath/", "I8": "Bernd /Falkenrath/", "I13": "Anke /Marwede/",
    "I16": "Hannelore /Oberlin/", "I20": "Margarete /Krümmel/", "I27": "Robert /Falkenrath/",
    "I35": "Mathilde /Oberlin/", "I93": "Michael /Falkenrath/",
}
VERSTORBEN = {"I16", "I20", "I35"}


def test(art, datum, anbieter, notiz, resn):
    zeilen = [f"1 EVEN {art}", "2 TYPE DNA Test", f"2 DATE {datum}", f"2 AGNC {anbieter}"]
    if notiz:
        zeilen.append(f"2 NOTE {notiz}")
    return zeilen + [f"2 RESN {resn}"]


def haplogruppe(art, wert, datum, anbieter, resn):
    return [f"1 FACT {wert}", f"2 TYPE {art} Haplogroup", f"2 DATE {datum}", f"2 AGNC {anbieter}", f"2 RESN {resn}"]


def treffer(cm, datum, anbieter, xref, name, anzahl, laengstes, resn):
    zeilen = [f"1 FACT {cm}", "2 TYPE DNA Match", f"2 DATE {datum}", f"2 AGNC {anbieter}"]
    notiz = [f"Segments: {anzahl}", f"Longest segment: {laengstes}"]
    if xref:
        zeilen += [f"2 _ASSO @{xref}@", "3 RELA DNA"]
    else:
        notiz.insert(0, f"Match: {name}")
    return zeilen + ["2 NOTE " + notiz[0]] + ["3 CONT " + z for z in notiz[1:]] + [f"2 RESN {resn}"]


def segmente(xref, summe, anzahl, x_cm):
    """Erfundene Segmente wie in dna.py: mindestens 8 cM, etwa 1 cM je Megabase, ohne Überlappung."""
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
        wahl = [k for k in FOLGE[:22] if LAENGE[k] > (cm * 1.2 + 6) * 1_000_000 and len(belegt[k]) < 2]
        zufall.shuffle(wahl)
        if not any(legen(k, cm) for k in wahl):
            sys.exit(f"{xref}: Segment mit {cm} cM passt nirgends")
    if x_cm:
        legen("X", float(x_cm))
    zeilen.sort(key=lambda z: (FOLGE.index(z[0]), z[1]))
    return ["Chromosome,Start,End,cM,SNPs"] + [f"{c},{a},{e},{cm:.1f},{snp}" for c, a, e, cm, snp in zeilen]


def gramps_treffer(von, zu, summe, anzahl, x_cm):
    zeilen = segmente(von + "-" + zu, summe, anzahl, x_cm)
    return [f"1 ASSO @{zu}@", "2 RELA DNA", "2 NOTE " + zeilen[0]] + ["3 CONT " + z for z in zeilen[1:]]


NEU = {
    "I8": test("Y-DNA", "MAY 2023", "FamilyTreeDNA", "Big Y-700", "confidential")
        + haplogruppe("Y-DNA", "R-U106", "MAY 2023", "FamilyTreeDNA", "confidential"),
    "I27": test("Y-DNA", "SEP 2023", "FamilyTreeDNA", "Y-37", "confidential")
        + haplogruppe("Y-DNA", "I-DF29", "SEP 2023", "FamilyTreeDNA", "confidential"),
    "I20": test("mtDNA", "2009", "FamilyTreeDNA", "", "privacy")
        + haplogruppe("mtDNA", "H1a1", "2009", "FamilyTreeDNA", "privacy"),
    "I5": test("mtDNA", "FEB 2024", "FamilyTreeDNA", "", "confidential")
        + haplogruppe("mtDNA", "H1a1", "FEB 2024", "FamilyTreeDNA", "confidential")
        + test("Autosomal", "2022", "MyHeritage", "", "confidential")
        + treffer("2580.4", "2022", "MyHeritage", "I1", "", 41, "172.3", "confidential")
        + treffer("180", "2022", "MyHeritage", "I13", "", 7, "41.2", "confidential")
        + treffer("62", "2023", "MyHeritage", "", "J. S.", 3, "28.4", "confidential"),
    "I16": treffer("2655.1", "2013", "FamilyTreeDNA", "I35", "", 44, "158.6", "privacy"),
    "I93": gramps_treffer("I93", "I1", 195, 8, 12),
}


def datensatz(text, xref):
    anfang = text.index(f"\n0 @{xref}@ INDI\n") + 1
    ende = text.index("\n0 ", anfang)
    satz = text[anfang:ende]
    if f"\n1 NAME {NAMEN[xref]}\n" not in satz + "\n":
        sys.exit(f"{xref} heißt nicht {NAMEN[xref]}")
    if ("\n1 DEAT" in satz) != (xref in VERSTORBEN):
        sys.exit(f"{xref}: lebend/verstorben anders als erwartet")
    return anfang, ende, satz


def einfuegen(satz, neu):
    """Neue Zeilen vor Bildern, Familien und Kennung des Datensatzes, wie in dna.py."""
    stellen = [satz.find(m) for m in ("\n1 OBJE ", "\n1 FAMC ", "\n1 FAMS ", "\n1 _UID ") if m in satz]
    if not stellen:
        sys.exit("keine Stelle zum Einfügen gefunden")
    i = min(stellen)
    return satz[:i] + "\n" + "\n".join(neu) + satz[i:]


quelle, ziel = sys.argv[1], sys.argv[2]
text = open(quelle, encoding="utf-8").read()
if "\n2 VERS 1.9\n" not in text.split("\n0 ", 1)[0] + "\n":
    sys.exit("Kopf ist nicht Version 1.9")
if "\n2 TYPE DNA Test\n" in text or "\n2 TYPE DNA Match\n" in text:
    sys.exit("Einträge in der Schreibweise von dna4webtrees gibt es schon")

for xref in NAMEN:
    datensatz(text, xref)
for xref, zeilen in NEU.items():
    anfang, ende, satz = datensatz(text, xref)
    text = text[:anfang] + einfuegen(satz, zeilen) + text[ende:]
    print(f"  {xref} {NAMEN[xref].replace('/', '')}: {sum(z.startswith('1 ') for z in zeilen)} Einträge")

kopf, rest = text.split("\n0 ", 1)
for alt, neu_ in (("\n2 VERS 1.9\n", "\n2 VERS 1.10\n"), ("\n1 DATE 27 NOV 2026\n", "\n1 DATE 28 NOV 2026\n"),
                  ("\n1 FILE falkenrath-1.9.ged\n", "\n1 FILE falkenrath-1.10.ged\n")):
    if alt not in kopf:
        sys.exit(f"Kopfzeile fehlt: {alt.strip()}")
    kopf = kopf.replace(alt, neu_, 1)
open(ziel, "w", encoding="utf-8", newline="").write(kopf + "\n0 " + rest)
print(f"{ziel}: DNA-Einträge in der Schreibweise von dna4webtrees an I5, I8, I16, I20, I27, I93")
