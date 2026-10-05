# Versionen des Demo-Stammbaums

Jede Version ist hier **eingefroren** und wird nie wieder geändert. `../falkenrath.ged` ist immer die neueste
Version; neue Finessen kommen nur als Änderung an der neuesten Version hinzu, nie durch Neuerzeugen.

| Version | Datum | Inhalt | Werkzeug |
| - | - | - | - |
| [1.0](falkenrath-1.0.ged) | 26.09.2026 | 492 Personen, 154 Familien, 43 Quellen, 135 Bilder; 7 Generationen lückenlos, Ahnenschwund, katholische Linie, Paten (`godfather`/`godmother`), Zeugen, Todesursachen | `tools/make_demo_tree.py` |
| [1.1](falkenrath-1.1.ged) | 29.09.2026 | Quellen dreistufig: 40 Archive, 204 Quellen (Kirchenbuch-Bände, Standesamtsregister mit Sperrfristen, Urkundensammlung), 1.413 Quellenangaben, `MARR TYPE civil/religious`, 20 Abschriften, 7 neue Scans, Testfall-Tabelle | Umbau-Skript (nicht erhalten) |
| [1.2](falkenrath-1.2.ged) | 01.10.2026 | Paten und Trauzeugen: jede Taufe der direkten Linie mit Paten (`_ASSO` + `RELA godparent`, sonst Notiz `Paten: …; …`), zwei Trauzeugen je Standesamt-Heirat, Testfälle für `godfather`, `Godparent`, `1 ASSO`; Taufe von Jonas mit lebender Patin | `falkenrath/werkzeuge/paten.py` |
| [1.3](falkenrath-1.3.ged) | 01.10.2026 | Paten/Trauzeugen ohne Datensatz als GEDCOM-L-Tags `2 _GODP` / `2 _WITN`, eine Zeile je Person (GEDCOM-L); alte Notiz-Form `Paten: …` bleibt als Testfall bei I140, I141, F60 | `falkenrath/werkzeuge/godp.py` |
| [1.4](falkenrath-1.4.ged) | 05.10.2026 | Höfe und Häuser in Bienenbüttel als GEDCOM-L-Ortsdatensätze: `_LOC` Bienenbüttel (Gemeinde) und vier Gebäude mit `TYPE` (Mühle, Hof, Haus), `1 _LOC` auf den Ort, Ereignissen am Gebäude (`EVEN` mit `TYPE` Brand, Neubau, Verkauf, Umbau, Abbruch, Stilllegung) und Koordinaten; 11 Bewohner-Einträge (`RESI FROM … TO …`), 6 Besitzer (`PROP`) an Hinrichs, Mohwinkel, Winkelmann; Häuslingshaus Nr. 12 als Testfall „Bewohner ohne Besitz“ | `falkenrath/werkzeuge/hoefe.py` |

## Regeln

1. **Nie neu erzeugen.** `tools/make_demo_tree.py` erzeugt nur 1.0.
2. **Neue Version:**
   - mit einem Skript, das nur auf der vorigen Version läuft (prüft `2 VERS` im Kopf) und die Version erhöht;
   - danach die Datei hier als `falkenrath-<version>.ged` ablegen, `SHA256SUMS` ergänzen und die Tabelle fortschreiben.
3. **Prüfen:** `sha256sum -c SHA256SUMS` zeigt sofort, ob eine eingefrorene Version verändert wurde.

Die Bilder (`../media/`) gelten für alle Versionen: Neue Bilder kommen hinzu, alte werden nicht entfernt.
