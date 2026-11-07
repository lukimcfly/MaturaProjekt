# Aufbau – Schritt für Schritt

**Stand 04.11.2026.** Gilt für Rev 4.0 der Platinen. Begleitpapiere:
`VERDRAHTUNG.md` (jede Ader), `BEDIENFELD-ERGAENZUNGEN.md` (Netzteil, Panel-Extras),
`../Einkauf/BESTELLEN.md` (Teileliste).

> **Zuerst lesen: Abschnitt 11 „Fehler in den alten Dokumenten".**
> Zwei Zeilen in `VERDRAHTUNG.md` sind veraltet. Eine davon führt zu falsch
> gebohrten Löchern in der Frontplatte – das lässt sich nachher nicht mehr heilen.

---

## 1. Die zwei Regeln

**Regel 1 – Eine Platine fertig, testen, erst dann die nächste.**
Es gibt 3 gleiche Oszillatoren und 4 gleiche Filter. Die Versuchung ist gross,
alle gleichzeitig zu bestücken. Nicht tun. Ein systematischer Fehler (Chip
verdreht, Wert vertauscht, Elko falsch herum) steckt sonst sieben Mal in der
Schaltung, und das Suchen dauert länger als das Bauen. Von JLCPCB sind je
5 Stück da – eine verlorene Platine ist kein Drama, eine verlorene Woche schon.

**Regel 2 – SMD immer zuerst.**
Auf jeder Platine kommen die SMD-Chips **vor allem anderen** drauf. Solange die
Platine flach und leer ist, kannst du sie beschweren, drehen und mit der Lupe
daran. Sobald ein einziger Widerstand steht, wackelt sie, und der SOT-23-6 wird
zur Qual.

---

## 2. Reihenfolge der Baugruppen

Die Reihenfolge ist nicht beliebig: jede Etappe wird mit der vorigen geprüft,
und der Schwierigkeitsgrad steigt genau richtig an.

| # | Baugruppe | SMD? | Teile | Zeit | Warum hier |
|---|---|---|---|---|---|
| 1 | Netzteil-Platinchen | – | ~8 | 2 h | Ohne geprüfte Spannung darf keine Platine ans Netz |
| 2 | **Hauptplatine** | **nein** | 46 | 4 h | Reines THT – gute Aufwärmrunde. Danach hast du Verstärker + Lautsprecher zum Testen |
| 3 | **Filter Nr. 1** | 1 × SOIC-14 | 22 | 2,5 h | Kleinste Platine, einfachster SMD-Chip – die SMD-Übungsrunde |
| 4 | **Oszillator Nr. 1** | 3 Chips | 57 | 5 h | Der schwierigste. Hier kommt **der erste Ton** |
| 5 | Oszillator 2 + 3 | | je 57 | je 3,5 h | Routine |
| 6 | Filter 2–4 | | je 22 | je 2 h | Routine |
| 7 | Frontplatte bohren | | | 6 h | Erst wenn alle Bedienteile physisch da sind |
| 8 | Bedienfeld verdrahten | | 153 Adern | 12 h | Der längste Posten – nicht unterschätzen |
| 9 | Arduino-Oszilloskop | | ~15 | 3 h | Unabhängig, kann als Lückenfüller dazwischen |
| 10 | Gehäuse + Abgleich | | | 8 h | |

**Summe ≈ 60 h.** Der erste Ton kommt nach Etappe 4, also nach rund **14 Stunden** –
das ist der Meilenstein, auf den du hinarbeitest. Danach ist alles Vervielfachung
und Verdrahtung, also planbar.

---

## 3. Vorbereitung (einmalig, 1 h)

**Arbeitsplatz**
- Helles Licht von vorne, Lupe oder Handykamera mit Zoom für die SMD-Kontrolle.
- Lötkolben auf **320–340 °C** für normale Stellen.
- Messingwolle statt nassem Schwamm, wenn vorhanden (kühlt die Spitze nicht aus).
- Ein Blatt weisses Papier unter der Platine: heruntergefallene SMD-Teile sind
  darauf zu finden, auf einem dunklen Tisch nicht.

**Teile sortieren – das spart später Stunden.**
Widerstände sind der Knackpunkt: auf der Oszillatorplatine sitzen **27 Stück in
12 verschiedenen Werten**, und Farbringe bei 1 %-Metallschicht (blauer Körper,
5 Ringe) liest man schnell falsch. Einmal alle mit dem Multimeter durchmessen,
in beschriftete Tütchen oder in einen Papierstreifen mit angeschriebenen Werten
stecken. **Nie** nach Farbe allein bestücken.

**Platinen zuordnen.** Die drei Layouts unterscheiden sich in der Grösse:
Oszillator 108 × 108 mm, Hauptplatine 96 × 98 mm, Filter 80 × 68 mm.

---

## 4. Etappe 1 – Stromversorgung

> **Geändert am 04.11.2026.** Der DC/DC-Wandler `B1212S-2WR3` und die
> rückstellende Sicherung `RXEF110` waren bei LCSC rückständig und wurden nicht
> geliefert; für eine Nachbestellung reicht die Zeit nicht. Statt des Wandlers
> stehen jetzt **zwei 12-V-Steckernetzteile in Reihe**. Begründung und
> Konsequenzen in `BEDIENFELD-ERGAENZUNGEN.md`, Abschnitt 9.

### Das Prinzip

Zwei galvanisch getrennte 12-V-Quellen werden hintereinandergeschaltet wie zwei
Batterien. Der **Verbindungspunkt in der Mitte wird die Masse**: von dort liegt
Netzteil A 12 V darüber (`+12 V`), Netzteil B 12 V darunter (`−12 V`). Zwischen
`+12 V` und `−12 V` stehen 24 V.

Das funktioniert nur, weil der Ausgang eines Steckernetzteils keine Verbindung
zum Stromnetz hat. Ein Netzteil mit **Schutzleiter** darf deshalb nicht
verwendet werden – es würde eine der beiden Schienen auf Erde legen und die
andere Quelle kurzschliessen.

### Netzteil B prüfen – vier Bedingungen

Alle vier müssen stimmen, sonst nicht verwenden:

| Prüfung | Anforderung | warum |
|---|---|---|
| Stecker | **zweipolig**, kein Schutzleiter | sonst Kurzschluss über Erde |
| Leerlaufspannung | **12,0 – 12,6 V** | über 13 V hiesse unreguliert; dann würden die Schienen unsymmetrisch |
| Strom | **≥ 150 mA** | die −12-V-Schiene zieht 65 mA typisch, 110 mA im schlechtesten Fall |
| Polarität | **Mitte = Plus** | Standard, aber messen |

Ein leichtes Schaltnetzteil (Aufdruck `INPUT 100-240V~`) ist reguliert. Ein
schwerer Steckertrafo (`INPUT 230V~`) ist es meist nicht – der zeigt im
Leerlauf oft 16–18 V und fällt damit durch.

### Teile

| Teil | Nummer | Bestellung |
|---|---|---|
| Netzteil A, Mean Well NGE12E12-P1J | `3164222` | Conrad 2020184489 |
| Netzteil B, zweites 12-V-Netzteil | – | vorhanden |
| DC-Einbaubuchse, **2 ×** | `A-991` | Tayda #1000487221 |
| Kippschalter als Netzschalter | `A-3186` | Tayda #1000487221 |
| Lochrasterplatine 50 × 70 mm | `A-1194` | Tayda #1000487221 |
| JST-XH 3-polig: Stift / Gehäuse / 3 Kontakte | `C144394` / `C144402` / `C140573` | LCSC |
| DC-Kabel 5,5/2,1 für den Arduino | `A-6806` | Tayda #1000487221 |
| Sicherungsclips, 2 von 6 übrigen | `C151075` | LCSC |

**Entfallen:** DC/DC-Wandler, Elko 22 µF, RXEF110.

### Aufbau

Drei Schienen auf dem Lochraster, je ein blanker Draht über eine Lochreihe:
`+12 V`, `Masse`, `−12 V`. Dann neun Verbindungen:

| # | von | nach |
|---|---|---|
| 1 | Buchse A **Mitte (+)** | Netzschalter |
| 2 | Netzschalter | **+12-V-Schiene** (über die Sicherungsclips) |
| 3 | Buchse A **Aussen (−)** | **Masse-Schiene** |
| 4 | Buchse B **Mitte (+)** | **Masse-Schiene** ← umgekehrt zu Buchse A |
| 5 | Buchse B **Aussen (−)** | **−12-V-Schiene** |
| 6 | +12-V-Schiene | Stiftleiste Pin 1 |
| 7 | Masse-Schiene | Stiftleiste Pin 2 |
| 8 | −12-V-Schiene | Stiftleiste Pin 3 |
| 9 | +12-V- und Masse-Schiene | DC-Kabel zum Arduino |

> **Die Stelle, an der man sich vergreift:** bei Buchse B geht der **Plus** an
> Masse und der **Minus** auf die −12-V-Schiene – genau umgekehrt zu Buchse A.
> Vertauscht man es, liegt `+12 V` auf der `−12-V`-Schiene. `D908` auf der
> Hauptplatine fängt das ab, aber verlassen sollte man sich darauf nicht.

**Sicherung:** zwei der sechs übrigen Clips (`C151075`) kommen in Leitung 2,
vorerst mit einer **Drahtbrücke** statt einer Sicherung. Sobald eine 5 × 20 mm
**T 1 A** verfügbar ist, wird sie eingesteckt – ohne umzulöten. Die vorhandenen
`T 500 mA` passen nicht: das Gerät zieht rund 0,5 A.

### Prüfung 1 – bevor irgendeine Platine angeschlossen wird

| Messung | Erwartung |
|---|---|
| Durchgang +12-V-Schiene ↔ Masse | **kein Durchgang** |
| Durchgang −12-V-Schiene ↔ Masse | **kein Durchgang** |
| +12-V-Schiene gegen Masse | +11,8 … +12,6 V |
| −12-V-Schiene gegen Masse | −11,8 … −12,6 V |
| **+12 gegen −12** | **24 V** |
| Stiftleiste Pin 1 / 2 / 3 | +12 V / 0 V / −12 V |

Zeigt das Messgerät an der −12-V-Schiene **plus** 12 V, sind an Buchse B Mitte
und Aussen vertauscht. Stehen zwischen `+12` und `−12` nur 12 V statt 24 V, ist
eine der beiden Quellen nicht galvanisch getrennt – dann Netzteil B
austauschen.

### Ausschalten

Der Netzschalter trennt nur die `+12-V`-Schiene. Beim Ausschalten steht `−12 V`
also noch kurz an. Das schadet den ICs nicht – sie laufen einen Moment mit
einseitiger Versorgung und dann aus –, kann aber im Lautsprecher knacken. Wer
es sauber will, hängt **beide Netzteile an eine schaltbare Steckdosenleiste**
und benutzt diese als Hauptschalter.

## 5. Etappe 2 – Hauptplatine (46 Teile, kein SMD)

Reihenfolge immer **flach nach hoch**: so liegt die Platine beim Löten auf dem
Tisch und hält die Teile selbst fest.

| Schritt | Teile | Anzahl | Hinweis |
|---|---|---|---|
| 1 | Widerstände `R801`–`R809`, `R901`, `R902` | 11 | **liegend**, Rastermass 7,62 mm |
| 2 | Schottky-Dioden `D907`, `D908` (1N5819) | 2 | **Polung!** Ring = Kathode, auf Druck markiert |
| 3 | IC-Fassung DIP-8 für `U901` | 1 | Kerbe nach dem Druck ausrichten |
| 4 | Keramik 100 nF `C907`, `C921`, `C922`, `C942` | 4 | ungepolt |
| 5 | Folie `C905` 47 nF, `C941` 330 nF, `C801`–`C803` 1 µF | 5 | ungepolt |
| 6 | `Q801` BC547, `U990` 78L05 | 2 | **Beine auf 2,54 mm spreizen** |
| 7 | **Drahtbrücken** über `F901`, `F902` | 2 Drähte | Clips passen nicht – siehe Hinweis unten |
| 8 | Elkos (Liste unten) | 9 | **Polung!** |
| 9 | JST-XH-Stiftleisten `J810`–`J817`, `J904`, `J990` | 10 | zum Schluss, sie sind am höchsten |

> **Revision 04.11.2026 – Sicherungen entfallen auf der Hauptplatine.**
> Der bestellte Clip `C151075` (Littelfuse 111) hat die Lötfahnen **quer** zur
> Sicherungsachse, der Footprint `Fuseholder_Clip-5x20mm_Littelfuse_111_Inline`
> erwartet sie **längs**. Eingesetzt stünde die Sicherung 90° verdreht und könnte
> die 15 mm zum zweiten Clip nicht überbrücken.
>
> **Lösung:** `F901` und `F902` bleiben unbestückt. Je eine Drahtbrücke vom
> **zweiten zum dritten Loch** der Viererreihe (10 mm). Die Absicherung der
> `+12 V` sitzt auf dem Netzteil-Platinchen, wo die Clips frei platziert und
> deshalb unproblematisch sind. Die `−12 V` ist danach nur noch durch die
> interne Sicherung des Steckernetzteils geschützt – für den Betrieb
> vertretbar, bei Zeit später mit zwei der vier übrigen Clips nachrüstbar.
>
> **Prüfung:** Loch 1 gegen Loch 4 der Viererreihe muss piepsen, in beiden Reihen.

**Elkos der Hauptplatine:** `C804` 10 µF, `C903` 10 µF, `C806` 47 µF,
`C906`/`C931`/`C932` 100 µF, `C805` 470 µF, `C904` 470 µF, und
**`C901` 10 µF bipolar**. Der bipolare darf **nicht** durch einen normalen
ersetzt werden – er sitzt auf 0 V Gleichspannung und hat deshalb keine
definierte Polung.

> **Falle 78L05.** Die TO-92-Version hat **nicht** dieselbe Reihenfolge wie der
> grosse 7805 im TO-220. Beim L78L05ACZ ist es, mit der flachen Seite zu dir,
> von links nach rechts: **Ausgang – Masse – Eingang**. Beim TO-220 ist es genau
> andersherum. Einmal im Datenblatt nachsehen, bevor du ihn einlötest; verkehrt
> herum stirbt er sofort.

> **Falle Masseflächen.** Die Massepins der Versorgungsstecker und der
> Abblockkondensatoren hängen **ohne Thermal** direkt an der Kupferfläche. Die
> Fläche zieht die Wärme weg: Kolben auf ~360 °C, länger halten, bis das Zinn
> wirklich fliesst. Eine kalte Lötstelle an einem Massepin ist später der Fehler,
> den du am längsten suchst.

### Prüfung 2 – Hauptplatine

**Ohne ICs in den Fassungen**, Netzteil über `J990`:

| Messpunkt | Erwartung |
|---|---|
| `J810` Pin 1 / 2 / 3 / 4 | +11,7 V / 0 V / −11,7 V / **+5,0 V** |
| `J811` Pin 1 / 2 / 3 | +11,7 V / 0 V / −11,7 V |
| DIP-8-Fassung Pin 6 (LM386 V+) | +11,7 V |
| DIP-8-Fassung Pin 4 (LM386 GND) | 0 V |

**+11,7 V statt +12 V ist richtig so**: die Schottky-Dioden `D907/D908` kosten
rund 0,3 V pro Schiene. Das ist der Verpolschutz, nicht ein Fehler.

Dann: Strom aus, **LM386 einsetzen** (Kerbe!), Lautsprecherklemmen an `J904`,
Strom ein. Mit dem Finger an `J813` Pin 1 tippen → es muss im Lautsprecher
brummen. Damit sind Netzteil, Drahtbrücken, Verpolschutz, 78L05 und Endstufe
abgehakt.

---

## 6. Etappe 3 – Filter Nr. 1 (22 Teile, 1 SMD-Chip)

| Schritt | Teile | Anzahl | Hinweis |
|---|---|---|---|
| 1 | **`U401` TL074CDR (SOIC-14)** | 1 | **zuerst**, siehe Abschnitt 9 |
| 2 | Widerstände `R401`–`R410` | 10 | liegend, 7,62 mm |
| 3 | Keramik `C403`, `C404` 100 nF | 2 | |
| 4 | Folie `C401`, `C402` 15 nF | 2 | **Folie, keine Keramik** – Zeitkondensatoren |
| 5 | Elkos `C405`, `C406` 10 µF | 2 | Polung |
| 6 | JST `J410`(3), `J411`(3), `J412`(12), `J413`(2), `J414`(2) | 5 | |

### Prüfung 3 – Filter

Versorgung an `J410`. An `U401` messen: **Pin 4 = +11,7 V, Pin 11 = −11,7 V**.
Fehlt eine Schiene oder sind beide gleich, ist der Chip verdreht oder eine
Lötbrücke drin.

> ⚠ **Der Chip wird ohne Bedienfeld warm – das ist normal.** `U401B` und
> `U401C` sind Integratoren: ihre Gegenkopplung besteht nur aus `C401` bzw.
> `C402`. Der Gleichstromweg läuft über die beiden Cutoff-Potis am Bedienfeld
> und zurück über `R401`/`R402`. Hängt an `J412` nichts, ist diese Schleife
> offen, und die zwei Ausgänge driften langsam an eine Schiene. Ein Ausgang an
> der Schiene treibt dann über die 10-kΩ-Summenwiderstände je rund 0,8 mA – ein
> paar Milliampere mehr, etwa 0,1 W, rund 10 °C über Raumtemperatur.
>
> Daran erkennt man den Unterschied: **handwarm, Finger beliebig lange drauf =
> harmlos. Nach zwei Sekunden muss der Finger weg = Fehler** (dann Zinn unter
> dem Gehäuse, siehe Abschnitt 9, Schritt 9).
>
> Und daran, dass es **langsam** kommt: Zuerst bleibt der Chip kühl, das Driften
> braucht Sekunden bis Minuten. Ein echter Kurzschluss ist sofort heiss.
>
> Soll der Chip beim Prüfen kalt bleiben, schliesst man die Schleife mit zwei
> Drahtbrücken auf `J412`: **Pin 1 → Pin 2** und **Pin 3 → Pin 4**. Das
> entspricht beiden Cutoff-Potis auf Anschlag.

Für einen echten Funktionstest braucht der Filter sein Poti und seinen
Wahlschalter. Schnellvariante mit Drahtbrücken auf `J412`:

| Brücke | Wirkung |
|---|---|
| ~47 kΩ zwischen Pin 1 und Pin 2 | Cutoff Ebene A auf Mitte |
| ~47 kΩ zwischen Pin 3 und Pin 4 | Cutoff Ebene B auf Mitte |
| ~25 kΩ zwischen Pin 5 und Pin 6 | Resonanz auf Mitte |
| Draht Pin 12 → Pin 7 | Ausgang = **Tiefpass** |

Signal von der Hauptplatine (`J816`) auf `J413`, Ausgang `J414` zurück auf
`J817` → Ton muss durchkommen und beim Verstellen des Ersatzwiderstands an
Pin 1/2 hörbar dumpfer/heller werden.

---

## 7. Etappe 4 – Oszillator Nr. 1 (57 Teile, 3 SMD-Chips)

Die anspruchsvollste Platine. Hier sitzen alle drei SMD-Typen, und die
27 Widerstände stehen **hochkant**.

| Schritt | Teile | Anzahl | Hinweis |
|---|---|---|---|
| 1 | **`U103` TL074CDR (SOIC-14)** | 1 | der einfachste – zum Warmwerden |
| 2 | **`U104` OPA1662 (SOIC-8)** | 1 | gleiches Raster, nur kürzer |
| 3 | **`U102` 74LVC2G17 (SOT-23-6)** | 1 | **der schwierigste Chip im Projekt** |
| 4 | Widerstände `R101`–`R127` | 27 | **stehend**, Rastermass 2,54 mm |
| 5 | Dioden `D101`–`D106` (1N4148) | 6 | **Polung!** Glas, Ring = Kathode |
| 6 | IC-Fassung DIP-14 für `U101` | 1 | |
| 7 | Keramik `C105`–`C111` 100 nF | 7 | |
| 8 | Folie `C101` 56 nF, `C102` 15 nF, `C103`/`C104` 1 µF | 4 | siehe Warnung |
| 9 | `Q101` BC547 | 1 | Beine auf 2,54 mm |
| 10 | Elkos `C112`, `C113` 10 µF | 2 | Polung |
| 11 | JST `J110`(4), `J111`(4), `J112`(11), `J113`(14), `J114`(6), `J115`(2) | 6 | |

> **Stehende Widerstände.** Einen Draht am Körper um 180° zurückbiegen, sodass
> beide Drähte 2,54 mm auseinander nach unten zeigen. Nur so passen 27 Stück
> neben die vier ICs. Alle in dieselbe Richtung ausrichten (Toleranzring oben),
> dann sind sie später lesbar.

> **`C101` muss Folie sein.** Der 56-nF-Zeitkondensator des Sägezahns bestimmt
> die Frequenz. Mit Keramik lag die Messung **56 % daneben**. Dasselbe gilt für
> `C102` (15 nF). Die blauen Kästchen (A-704 / A-702), nicht die braunen Scheiben.

### Prüfung 4 – Oszillator, und der erste Ton

1. Versorgung an `J110`. Spannungen an den Chips messen:

   | Chip | V+ | V− |
   |---|---|---|
   | `U101` TL074 (DIP-14, Fassung) | Pin 4 = +11,7 V | Pin 11 = −11,7 V |
   | `U103` TL074CDR (SOIC-14) | Pin 4 = +11,7 V | Pin 11 = −11,7 V |
   | `U104` OPA1662 (SOIC-8) | Pin 8 = +11,7 V | Pin 4 = −11,7 V |
   | `U102` 74LVC2G17 (SOT-23-6) | Pin 5 = **+5,0 V** | Pin 2 = 0 V |

   Der 74LVC2G17 läuft auf **+5 V**, nicht auf 12 V. Liegen dort 12 V an, stimmt
   etwas mit der Versorgungsleitung nicht – sofort abschalten.

2. Strom aus, `U101` (TL074 DIP) einsetzen.

3. Ersatz-Beschaltung auf `J112` / `J113`, damit die Platine ohne Frontplatte
   schwingt:

   | Brücke auf `J112` | Wirkung |
   |---|---|
   | ~470 kΩ zwischen Pin 5 und Pin 6 | Tonhöhe Ebene B, Mitte |
   | ~470 kΩ zwischen Pin 7 und Pin 9 | Tonhöhe Ebene A, Mitte |
   | ~5 kΩ zwischen Pin 10 und Pin 11 | Amplitude, Mitte |

   | Brücke auf `J113` | Wirkung |
   |---|---|
   | Draht Pin 3 → Pin 8 | Wellenform = **Sägezahn** |
   | Draht Pin 1 → Pin 7 | Distortion „hart" |
   | Draht Pin 2 → Pin 4 | Distortion **aus** (sauberer Weg) |
   | Draht Pin 11 → Pin 12 | Solo-Filter aus |

4. `J115` → Hauptplatine `J813`. Mixer-Poti ersetzen oder kurz
   10 kΩ zwischen `J812` Pin 1 und Pin 3 mit Abgriff auf Pin 2.

5. **Einschalten. Es muss tönen.**

Tut es das, hast du den gesamten Signalweg bewiesen: Oszillator → Mixer →
Endstufe → Lautsprecher. Ab hier ist der Rest Fleissarbeit.

---

## 8. Etappen 5–6 – Vervielfachen

Erst **jetzt** die übrigen zwei Oszillatoren und drei Filter bestücken, in
derselben Reihenfolge. Pro Platine dieselbe Prüfung 3 bzw. 4. Tipp: alle
gleichen Arbeitsschritte über alle Platinen hinweg machen (also erst alle SMD,
dann alle Widerstände …) – das ist schneller, aber **nur**, wenn Platine Nr. 1
vorher nachweislich funktioniert hat.

---

## 9. Löttechnik

### SMD – die drei Chips

Werkzeug: feine Spitze, **Flussmittel** (Stift oder Spritze), Pinzette,
Entlötlitze, Lupe. Flussmittel ist hier kein Luxus, sondern das, was den
Unterschied macht.

**Ablauf, für alle drei Typen gleich:**
1. **Eine** Fläche verzinnen – nur eine, eine Ecke.
2. Flussmittel grosszügig über alle Flächen.
3. Chip mit der Pinzette auflegen, **Pin 1 prüfen** (Punkt/Kerbe gegen den
   Bestückungsdruck), mit dem Kolben die verzinnte Ecke aufschmelzen → der Chip
   zieht sich fest.
4. **Jetzt kontrollieren.** Sitzen alle Beinchen auf ihren Flächen? Wenn nicht:
   die eine Ecke wieder aufschmelzen und schieben. Solange nur ein Pin hält, ist
   das gratis – später nicht mehr.
5. Diagonal gegenüberliegende Ecke löten.
6. Rest Pin für Pin, oder im Zug über mehrere Pins („drag soldering").
7. Brücken mit Entlötlitze abziehen. **Eine Brücke ist normal**, kein Grund zur
   Panik – Flussmittel drauf, Litze drüber, weg.
8. Mit dem Multimeter im Durchgangsmodus zwischen benachbarten Pins prüfen.
9. **Und dann quer über die Versorgungspins messen, im Ohm-Modus** – beim
   TL074 (SOIC-14) also Pin 4 gegen Pin 11. Erwartet werden mehrere kΩ. Ein
   Wert um 100 Ω, der dort stehen bleibt, heisst: Zinn ist **unter** das
   Gehäuse gelaufen und verbindet die beiden Versorgungen.

> ⚠ **Schritt 9 nicht überspringen.** Der Durchgangstest zwischen den
> Nachbarpins findet Zinn unter dem Gehäuse **nicht** – die Brücke läuft quer
> unter dem Chip hindurch, von einer Pinreihe zur anderen, und berührt keine
> zwei Nachbarn. Unter Strom liegen dann bei ~20 V rund 0,2 A an 100 Ω an, also
> **4 Watt in einem Gehäuse von 4 × 9 mm**: der Chip wird in Sekunden heiss.
> Genau das ist am 05.11.2026 auf Filterplatine Nr. 1 passiert.
>
> Unter dem Gehäuse kommt man mit dem Kolben nicht hin. Reparatur nur so:
> alle 14 Beinchen mit einem feinen Seitenschneider **so nah am Gehäuse wie
> möglich** durchtrennen (nur schneiden, nicht ziehen – Ziehen reisst Pads ab),
> Gehäuse abheben, die Stummel einzeln mit 1–2 s Kolben und Pinzette entfernen,
> Restzinn mit Entlötlitze, mit Isopropanol putzen. **320 °C, nie länger als
> 2–3 s auf einem Pad.**
>
> Deshalb gehört der Chip auf eine Platine, **bevor** die durchkontaktierten
> Teile drauf sind: solange nichts aufragt, ist dieser Tausch eine Sache von
> zehn Minuten.

**Der 74LVC2G17 (SOT-23-6, 0,95 mm)** ist der heikelste. Deshalb liegen
**10 Stück** für 3 Plätze bereit – die Reserve ist Absicht, nicht Pessimismus.
Beim ersten ruhig einen „Übungschip" auf eine Reserveplatine setzen und wieder
entfernen, bevor du an die echte gehst.

### Durchkontaktierte Teile

- Bein durchstecken, leicht spreizen, Platine umdrehen.
- Kolben an **Pad und Bein gleichzeitig**, eine Sekunde, dann Zinn zugeben.
  Zinn gehört an die Lötstelle, nicht an die Spitze.
- Gute Lötstelle = kleiner glänzender Kegel. Kugelig und matt = kalt, nochmal.
- Erst **nach** dem Löten abzwicken, dann reisst nichts.

### Polung – die vier Teilearten, bei denen es zählt

| Teil | Merkmal |
|---|---|
| Elkos | **Minus**-Streifen am Gehäuse ↔ markierte Seite auf dem Druck |
| Dioden 1N4148 / 1N5819 | Ring = **Kathode** ↔ Balken im Druck |
| TO-92 (BC547, 78L05) | flache Seite ↔ Umriss im Druck |
| ICs / Fassungen | Kerbe oder Punkt = **Pin 1** |

`C901` auf der Hauptplatine ist **bipolar** und hat deshalb keine Polung.

---

## 10. Crimpen und Kabelbäume

Rund **245 Kontakte** pro Gerät. Mit der SN-28B (A-5362):

1. Litze **2–3 mm** abisolieren – nicht mehr.
2. In die Zange so einlegen, dass die **inneren** Flügel auf das blanke Kupfer
   und die **äusseren** auf die Isolation greifen. Das ist der ganze Trick: die
   Isolation trägt den Zug, das Kupfer leitet.
3. Erst 5–10 Übungskontakte, bis das Bild stimmt. Dann prüfen, ob der Kontakt
   im Gehäuse **hörbar einrastet** und sich nicht herausziehen lässt.

**Farbdisziplin** – du hast 10 Farben à 10 m. Einmal festlegen und durchhalten:

| Netz | Farbe |
|---|---|
| +12 V | rot |
| Masse (GNDREF) | schwarz |
| −12 V | blau |
| +5 V | orange |
| Audio-Signale | je eine eigene Farbe pro Verbindung |

**153 Panel-Adern** sind viel. Immer **einen Stecker komplett** fertig machen
(alle Adern crimpen, einsetzen, beschriften), erst dann den nächsten. Niemals
alle Adern gleichzeitig ablängen – dann weiss man nach zwei Tagen nicht mehr,
welche wohin gehört.

---

## 11. Fehler in den alten Dokumenten

Beide stehen in `VERDRAHTUNG.md`, das aus dem Schaltplan erzeugt wurde und
spätere Einkaufsentscheide nicht kennt.

### ⚠ Klinkenbuchsen: 3,5 mm, **nicht** 6,3 mm

`VERDRAHTUNG.md` Abschnitt 4 listet „Klinkenbuchse 6,3 mm mono". **Falsch.**
Bestellt und geliefert ist der Typ **PJ35293, 3,5 mm** (Tayda A-6978), 13 Stück.

**Das betrifft die Frontplatte.** Eine 6,3-mm-Buchse braucht ein ~9,5-mm-Loch,
eine 3,5-mm-Buchse ein **~6-mm-Loch**. Bohrst du nach der alten Zeile, fallen
alle 13 Buchsen durch die Front. Vor dem Bohren eine Buchse in ein Reststück
Holz einpassen und das Mass dort abnehmen.

### ⚠ Die SMD-Chips werden **nicht** bestückt geliefert

`VERDRAHTUNG.md` Abschnitt 5 sagt „TL074CDR / OPA1662 / 74LVC2G17 – SMD, werden
von JLCPCB bestueckt". Das galt für die alte Planung. Seit dem Entscheid gegen
die Bestückung (spart ~48 USD) kommen die Platinen **nackt**: alle **13 SMD-Chips
lötest du selbst**. Siehe Abschnitt 9.

### Kleinere Abweichungen (kein Handlungsbedarf, nur zur Kenntnis)

- Tonhöhe und Cutoff sind **C-Potis** (umgekehrt logarithmisch), nicht linear
  wie in `VERDRAHTUNG.md` Abschnitt 4 – Begründung in
  `BEDIENFELD-ERGAENZUNGEN.md` Abschnitt 7.
- Filter-Resonanz ist **50 kΩ** statt der im Schaltplan genannten 47 kΩ.
- Der Mixer hat **Schieberegler** statt Drehpotis (Abschnitt 2 dort).
- Es gibt **keinen eingebauten Lautsprecher** mehr, nur Polklemmen (Abschnitt 3).

---

## 12. Frontplatte

- **Dicke höchstens ~3 mm** dort, wo Buchsen und Potis sitzen. Dickeres Holz von
  hinten aussenken, bis 2–3 mm übrig sind.
- **Drehschalter A-1893 sind 1 × 12 mit einstellbarem Anschlag.** Vor dem Einbau
  die Anschlagscheibe setzen: **4 Stellungen** bei den Oszillatoren (Wellenform),
  **5 Stellungen** bei den Filtern (Filterwahl). Nachher kommt man nicht mehr dran.
- Für die drei Schieberegler je ein **Schlitz ca. 62 × 3 mm**, Befestigung mit
  zwei M2/M3-Schrauben von hinten.
- Display-Ausschnitt nach dem vorhandenen **2,2"-Modul** – nicht nach dem 2,8".
- Erst eine **Bohrschablone auf Papier** ausdrucken und alle Teile auflegen, bevor
  gebohrt wird. Knöpfe sind 15 × 18 mm; mit 21 Drehpotis plus 7 Drehschaltern
  wird es eng, wenn man nicht vorher legt.

**Potis vor dem Verdrahten ausmessen.** Bei den C-Potis (Tonhöhe, Cutoff) und bei
den Schiebereglern muss mit dem Multimeter geprüft werden, welcher Anschluss das
CW-Ende ist: zwischen Schleifer und diesem Anschluss muss der Widerstand
**kleiner** werden, wenn man nach rechts dreht bzw. nach oben schiebt. Bei den
Tandempotis für **beide Ebenen** prüfen.

**Rheostat-Regel:** Bei `RV_01`–`RV_04` im Oszillator und `RV_01`–`RV_03` im
Filter hängen nur zwei Anschlüsse in der Schaltung. Den **dritten, unbenutzten
Aussenanschluss immer mit dem Schleifer verbinden** – sonst wird die Stufe stumm
oder instabil, wenn der Schleifer einmal Kontaktprobleme bekommt.

---

## 13. Fehlersuche

| Symptom | Zuerst prüfen |
|---|---|
| Nichts geht, Netzteil wird warm | Kurzschluss. Sofort aus. Durchgang +12/Masse und −12/Masse auf **jeder** Platine einzeln |
| Eine Schiene fehlt | Sicherung `F901`/`F902`, dann `D907`/`D908` auf Polung |
| +5 V fehlt | 78L05 verdreht (siehe Falle in Abschnitt 5) |
| Ein Kanal stumm | Kalte Lötstelle an einem **Massepin** – die häufigste Ursache. Nachlöten mit heisserem Kolben |
| Brummen | Masseschleife oder offener Op-Amp-Eingang. `SW_05` korrekt an Masse? |
| Oszillator schwingt nicht | `C101`/`C102` Folie statt Keramik? `U102` auf +5 V? Tonhöhe-Ersatzwiderstand drin? |
| Verzerrt immer | Distortion-Schalter `SW_03` in Stellung „ein" hängen geblieben |
| Ton zu leise | Mixer-Fader-Enden vertauscht („oben = laut" prüfen) |

**Grundsatz:** immer von der Versorgung her. Erst Spannungen an den Chip-Pins
messen, dann Signale verfolgen. 90 % aller Fehler sind kalte Lötstellen,
vertauschte Polung oder ein verdrehter Chip – nicht die Schaltung. Die ist
ERC-sauber und simuliert.

---

### Instabile Versorgungsspannung bei unbestückter Platine

**Symptom.** Die `+12-V`-Schiene springt, die `−12-V`-Schiene steht ruhig.
Alle Durchgangsprüfungen piepsen, kein Kurzschluss messbar.

**Ursache.** Die unbestückte Hauptplatine zieht nur den Querstrom des
`Q801`-Zweigs: Spannungsteiler `R804`/`R805` legt die Basis auf 2,1 V, über
`R807`+`R808` fließen rund 14 mA — als Ersatzwiderstand etwa 830 Ω, was der
gemessenen 700 Ω entspricht. Ein 1-A-Steckernetzteil arbeitet bei 1,4 % Last
im Burst-Betrieb und pumpt.

Die `−12-V`-Schiene täuscht dabei Gesundheit vor: an ihr hängen ohne ICs nur
Kondensatoren und Stecker, also **gar keine Last**. Eine unbelastete Leitung
zeigt auch über eine schlechte Verbindung den vollen Wert.

**Merkregel.** Der Durchgangsprüfer beweist Kontakt unter Spitzendruck, nicht
Strombelastbarkeit. Bei Verdacht auf Wackelkontakt immer den **Spannungsabfall
über dem Element unter Last** messen, nicht die Spannung gegen Masse.

**Abhilfe.** Netzteil mit kleinerem Nennstrom verwenden, während der Prüfung
eine Grundlast von ~35 mA anklemmen (3 × 1 kΩ parallel), oder erst messen, wenn
die ICs bestückt sind und die Anlage ohnehin Strom zieht.

---

## 14. Abgleich

Weicht ein Oszillator hörbar von den anderen ab, liegt es am Zeitkondensator.
Reserve liegt bereit:

| Problem | Massnahme |
|---|---|
| Sägezahn zu tief | `C101` kleiner: 47 nF (A-563) |
| Sägezahn zu hoch | `C101` grösser: 68 nF (A-707) |
| Funktionsgenerator-Bereich zu tief | `C102` 12 nF (A-620) oder `R105` 15 kΩ |
| Funktionsgenerator-Bereich zu hoch | `C102` 18 nF (A-703) oder `R105` 18 kΩ |

Umfang laut Auslegung: **48 Hz … 4,9 kHz**, bei halbem Drehweg ~440 Hz.

---

## 15. Kurz-Checkliste

```
[ ] Widerstände ausgemessen und sortiert
[ ] Netzteil-Platinchen gebaut
[ ] Prüfung 1 bestanden (±12 V, kein Kurzschluss)
[ ] Hauptplatine bestückt
[ ] Prüfung 2 bestanden (+5 V, Brummen im Lautsprecher)
[ ] Filter 1 bestückt (SMD zuerst!)
[ ] Prüfung 3 bestanden
[ ] Oszillator 1 bestückt
[ ] Prüfung 4 bestanden  >>> ERSTER TON <<<
[ ] Oszillator 2, 3
[ ] Filter 2, 3, 4
[ ] Frontplatte: Lochbild geprüft (3,5 mm!), Drehschalter-Anschläge gesetzt
[ ] Potis ausgemessen (CW-Ende), Rheostat-Regel angewandt
[ ] Bedienfeld verdrahtet, Stecker für Stecker
[ ] Arduino-Oszilloskop
[ ] Gehäuse, Abgleich, fertig
```
