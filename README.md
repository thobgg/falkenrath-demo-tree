# Demo-Stammbaum „Familie Falkenrath“

Ein kleiner, **frei erfundener** Stammbaum zum Ausprobieren und Testen von webtrees, dem Modul
*api4webtrees* und der Apps *wtAnd*, *wtWin* und *wtTux*: 492 Personen, 154 Familien, 204 Quellen,
40 Archive, 142 Bilder, von um 1750 bis heute.

**Alle Personen, Lebensdaten und Dokumente sind ausgedacht.** Übereinstimmungen mit lebenden oder
verstorbenen Personen sind Zufall. Die Orte gibt es wirklich – sie tragen Koordinaten, damit Karten etwas
zu zeigen haben.

**Die Porträts sind echte alte Atelierfotos unbekannter Personen** aus dem Rijksmuseum Amsterdam (CC0, über
Wikimedia Commons). Die Abgebildeten haben mit den erfundenen Namen nichts zu tun; Liste der Quellen in
[FOTOS.md](FOTOS.md). Bewusst nicht jeder hat ein Bild – wie in echten Stammbäumen: die direkten Vorfahren
meist, Seitenlinien seltener, vor 1860 niemand, und ab 1920 Geborene keine (freie Fotos aus dieser Zeit gibt es
kaum, und die Jüngeren sind privat). Urkunden, Kirchenbuch- und Registerauszüge, Werkstatt und Hochzeitsbild sind gezeichnet.

Lizenz: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/deed.de) – frei verwendbar, auch für
Screenshots und Vorführungen.

## Was der Baum abdeckt

Lebende Personen (Datenschutz), zwei Ehen mit früh verstorbenem Kind, Gefallene beider Weltkriege,
zwei Auswanderungen nach Milwaukee (1888 und 1952) samt amerikanischem Zweig, eine Scheidung, eine unbekannte
Mutter an der Spitze, Vettern und Cousinen auf Vater- und Mutterseite, Quellen mit Seitenangaben, Notizen,
Rufname, Orte mit Koordinaten, Medien an Personen, Familien und Quellen.

Seit September 2026 außerdem: die Vorfahren von Jonas **lückenlos über sieben Generationen** (127 Ahnen),
dahinter mit Lücken; **Ahnenschwund** (die Eltern von Nr. 37 sind auch Nr. 88/89); Geschwister der Vorfahren;
ein breiter **Stamm** ab Johann Friedrich Falkenrath (* 1843) bis heute; Taufen mit **Paten**, Trauungen mit
**Zeugen**, Begräbnisse, **Konfession** (eine katholische Linie aus dem Paderborner Land), **Todesursachen**;
Kirchenbücher und Standesämter als Quellen mit Seitenangaben – Stoff für Tafeln, Listen und Bücher.
Proband: **Jonas Falkenrath (I1)**.

## Quellen – dreistufig

Seit Version 1.1 (September 2026) sind die Quellen so angelegt, wie man es vorbildlich macht, und decken dabei jede
Variante ab, die GEDCOM 5.5.1 bei Quellen kennt – gedacht zum Testen von Apps wie *wtWin* und *wtTux*.
**Archive, Signaturen, Adressen und Bandlaufzeiten sind erfunden**; Web-Adressen enden auf `.example.org`.

| Ebene | Frage | GEDCOM | webtrees |
| - | - | - | - |
| 1 | Wo liegt die Quelle? | `0 @R…@ REPO` | Archiv |
| 2 | Was ist die Quelle? | `0 @S…@ SOUR` mit `1 REPO` → `2 CALN` (Signatur) → `3 MEDI` | Quelle |
| 3 | Wo genau steht es? | am Fakt `2 SOUR @S…@` mit `3 PAGE`, `3 QUAY` … | Quellenangabe |

**Kirchenbücher** (140): je Ort ein Mischbuch bis zu einem Wechseljahr zwischen 1790 und 1815, danach getrennte
Bücher für Taufen, Trauungen und Begräbnisse in je drei Bänden. Angelegt sind nur Bände, aus denen zitiert wird –
die Signaturen (`KB Eschede Nr. 1` …) haben deshalb Lücken. Titel: `KB Eschede ev. Taufen 1812-1845`,
`KB Paderborn kath. Taufen 1854-1905` (lateinischer Originaltitel als Notiz).

**Standesämter** (61): je Amt Geburten, Heiraten, Tode. Die **Sperrfristen** (Geburt 110, Heirat 80, Tod 30 Jahre)
teilen die Register: Ältere liegen im Stadt- bzw. Kreisarchiv (`StA Celle Geburten 1874-1916`), jüngere noch beim
Standesamt (`StA Celle Geburten 1917-`). Für die jüngere direkte Linie gibt es stattdessen die
**Urkundensammlung Familie Falkenrath** (S203) im Familienbesitz.

**Das Standesamt beurkundet, die Kirche vollzieht:**

| Quelle | Ereignis | Fakt | `PAGE` |
| - | - | - | - |
| Standesamt | Geburt / Heirat / Tod | `BIRT` / `MARR` + `TYPE civil` / `DEAT` | `Geburt 1913/24` · `Heirat 1924/58` · `Tod 1941/24` |
| Kirchenbuch | Taufe / Trauung / Begräbnis | `CHR` / `MARR` + `TYPE religious` / `BURI` | `Taufe 1811/6` · `Trauung 1797/3` · `Begräbnis 1837/5` |

Vor 1875 gab es kein Standesamt: Geburt und Tod zitieren dann denselben Eintrag wie Taufe bzw. Begräbnis,
mit `3 EVEN CHR` / `3 EVEN BURI` und `QUAY 2`. Die 15 Paare der direkten Linie ab 1890 haben **zwei Heiraten**:
standesamtlich und kirchlich.

**QUAY**: 3 = Eintrag zum Ereignis selbst, 2 = abgeleitet (Geburt aus Taufeintrag), Familienbibel, Verlustliste,
1 = fraglich, 0 = unzuverlässig. Rund ein Drittel der Angaben (Seitenlinien) ist bewusst ohne `QUAY`.

### Testfälle – wo zu finden

| Testfall | Fundstelle |
| - | - |
| Archiv mit Adresse, Telefon, E-Mail, Web | R5 Kirchenbuchamt Celle, R22 Stadtarchiv Celle |
| Archiv nur mit Name | R6 Pfarrarchiv Bergen |
| Archiv nur mit Web-Adresse und Notiz | R4 KirchenbuchDigital |
| Archiv ohne Quelle | R40 Heimatverein Eschede |
| Quelle mit zwei Archiven (Original + Digitalisat) | alle Bände des Kirchenkreises Uelzen, z. B. S5 |
| Quelle mit Kurztitel (`ABBR`) | Bände des Kirchenkreises Celle, z. B. S1 |
| Quelle mit `DATA/AGNC` | Bände des Kirchenkreises Lüneburg, z. B. S8 |
| Quelle mit Bild (Titelblatt) | S1 KB Eschede ev. Mischbuch |
| Quelle mit Text, Verlag, Bild | S3 Familienbibel |
| Quelle ohne Archiv | S4 Deutsche Verlustlisten |
| Signatur ohne Medium | Standesamtsregister im Archiv, z. B. S2 |
| Archivverweis ohne Signatur | Register beim Standesamt, z. B. S40; S203 Urkundensammlung |
| Quelle ohne Zitat | S204 KB Eschede ev. Konfirmationen |
| Abschrift (`DATA/TEXT`), auch mehrzeilig mit `CONT`/`CONC` | 20 Einträge, z. B. I130 Taufe, F8 Heirat, I276 Geburt |
| Scan an der Quellenangabe | I130 Taufe, I111 Taufe (lat.), F76 Trauung, I214 Begräbnis, I276 Geburt, I182 Tod, I52 Taufe 1801, F8 Heirat |
| Zwei Quellen an einem Fakt | I15 Geburt, F8 standesamtliche Heirat |
| Widersprüchliche Quellen (zwei Geburtsdaten) | I39 Carl Falkenrath |
| Quelle an der Person mit `EVEN`/`ROLE` (Pate) | I62, I271, I371 |
| Quelle direkt an der Familie | F8 (Familienstammbuch) |
| Quelle am Namen (Rufname) | I19 Friedrich „Fritz“ Ilgner |
| Quellenangabe mit Notiz, `QUAY 1` | I52 Begräbnis (schwer lesbar), I39 zweite Geburt |
| Quelle als reiner Text ohne Datensatz, `QUAY 0` | I65 Auswanderung 1888 |
| Heirat ohne `TYPE` | amerikanischer Zweig, z. B. F10 |
| Kirchliche Trauung mit Trauschein statt Kirchenbuch | F3, F6, F7 |

## In webtrees laden

1. *Verwaltung → Stammbäume verwalten → Stammbaum anlegen*, z. B. `falkenrath`.
2. `falkenrath.ged` importieren.
3. Dem Baum einen **eigenen Medienordner** geben (*Einstellungen → Medienordner*, z. B. `media/falkenrath/`)
   und die Dateien aus `media/` dorthin hochladen (*Verwaltung → Medien → Mediendateien hochladen*).
