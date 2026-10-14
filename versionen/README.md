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
| [1.5](falkenrath-1.5.ged) | 11.10.2026 | Gruppenbild der Hochzeit 1924 (`hochzeit-1924.jpg`, M135): Montage aus 21 Porträts, alle Abgebildeten mit `1 OBJE @M135@` verknüpft, dazu zwei Gäste ohne Datensatz (Trauzeuge Wilhelm Niebuhr, ein Unbekannter); Aufstellung als Notiz an M135; 23 Gesichtsrahmen als XMP (MWG Regions) im Bild, `hochzeit-1924-unmarkiert.jpg` ohne Rahmen | `falkenrath/werkzeuge/gruppenfoto.py`, `gruppenfoto_gaeste.py`, `xmp_bereiche.py`, Bild: `gruppenbild_montage.py` |
| [1.6](falkenrath-1.6.ged) | 13.10.2026 | GOV-Typnummern an den Ortsdatensätzen (GEDCOM-L `2 _GOVTYPE` unter `1 TYPE`): Gemeinde 18, Mühle 87, Hof 24, Gebäude 17; die Texte der Art bleiben (Mühle, Hof, Haus) – Programme und Online-Ortsfamilienbücher erkennen ein Gebäude an der Nummer | `falkenrath/werkzeuge/govtyp.py` |
| [1.7](falkenrath-1.7.ged) | 14.10.2026 | Die übrigen Angaben des GEDCOM-L-Addendums: Addendum-Angabe im Kopf, `_UID` an allen Datensätzen, `_RUFNAME` (22 Personen), hervorgehobenes Bild `_PRIM Y` an den Porträts der Personen auf dem Gruppenbild, drei Forschungsaufgaben `_TODO` mit allen Unterfeldern, Familienstand `_STAT UNKNOWN` an F22, `_GOV`/`_POST`/`_MAIDENHEAD` an den Orten in Bienenbüttel, Empfänger `_NAME` an der Adresse von R3; Ortsdatensatz Bienenbüttel mit echten Angaben aus GOV und Wikipedia: GOV-Kennung, früherer Name und frühere Art (Kirchspiel, Kirchdorf bis 1885), Gemeindeschlüssel `_AIDN`, Einwohner 1880 `_DMGD`, Maidenhead-Locator, Religion, Postleitzahl 3116 bis 1993 und 29553 seitdem | `falkenrath/werkzeuge/gedcoml.py` |

## Regeln

1. **Nie neu erzeugen.** `tools/make_demo_tree.py` erzeugt nur 1.0.
2. **Neue Version:**
   - mit einem Skript, das nur auf der vorigen Version läuft (prüft `2 VERS` im Kopf) und die Version erhöht;
   - danach die Datei hier als `falkenrath-<version>.ged` ablegen, `SHA256SUMS` ergänzen und die Tabelle fortschreiben.
3. **Prüfen:** `sha256sum -c SHA256SUMS` zeigt sofort, ob eine eingefrorene Version verändert wurde.

Die Bilder (`../media/`) gelten für alle Versionen: Neue Bilder kommen hinzu, alte werden nicht entfernt. Ausnahme: `hochzeit-1924.jpg` war bis 1.4 eine gezeichnete Grafik und ist seit 1.5 das Gruppenbild (gleiche Datei, in allen Versionen an F8).
