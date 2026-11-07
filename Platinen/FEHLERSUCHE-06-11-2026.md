# Fehlersuche Filterplatine Nr. 1 — Plan für den 06.11.2026

---

## ERGEBNIS, 06.11.2026 abends — Ursache gefunden und behoben

**Zwei Fehler in Reihe, jeder einzeln harmlos, zusammen tödlich.**

| # | Fehler | Wirkung allein |
|---|---|---|
| 1 | **Beide DC-Buchsen am Netzteil-Platinchen hatten + und − vertauscht** | Schienen spiegelbildlich: `/VIN_P` = −9 V, `/VIN_N` = +9 V |
| 2 | **D907 und D908 waren mit Draht überbrückt** | kein Verpolschutz |

Mit intaktem Verpolschutz hätten beide Dioden gesperrt und beide Schienen auf
0 V gelegen — der Chip wäre kalt geblieben. Überbrückt gelangten die
**18 V spiegelbildlich** direkt an `U401` Pin 4 und Pin 11. Die Sperrschicht im
Chip leitet, und weil `F901`/`F902` ebenfalls gebrückt waren, begrenzte nichts
den Strom ausser dem Adapter. Der Golddraht im Gehäuse verdampft bei 1–2 A.

Das erklärt alles: beide Chips auf dieselbe Weise, der langsame Hochlauf
(strombegrenzter Adapter), das Platzen nach ~10 s, und warum **jede**
Durchgangsprüfung bestanden wurde — ein Piepser zeigt Verbindungen, **nie**
die Polarität.

**Mitgestorben:** `U990`, der 78L05. Er hatte −9 V am Eingang. Ersetzt.

### Was nicht die Ursache war

| geprüft | Ergebnis |
|---|---|
| Kabel `J811` → `J410` gekreuzt | ❌ sauber 1:1 (rot/schwarz/blau auf 1/2/3 an beiden Enden) |
| Chip 180° verdreht | ❌ Punkt sitzt über dem Siebdruck-Dreieck |
| Zinn in der 3-mm-Lücke (Platine 2) | ❌ 84 kΩ zwischen den Schienen |
| Elkos verpolt eingelötet | ❌ Streifen bei beiden im Loch ohne `+` |
| Siebelkos Hauptplatine beschädigt | ❌ alle vier auf Raumtemperatur |
| Überspannung / 5-V-Theorie | ❌ kein 5-V-Netz auf der Filterplatine |

### Stand am Ende des Tages

| | |
|---|---|
| Netzteil-Platinchen | ±9 V / −12 V, Polarität korrigiert ✓ |
| D907 / D908 | Brücken entfernt, beide arbeiten ✓ |
| +12-V-Schiene | +8,8 V (mit 100 Ω: 8 V) ✓ |
| −12-V-Schiene | −11,7 V ✓ |
| +5-V-Schiene | +5,0 V, neuer 78L05 ✓ |
| **Filterplatine 2** | **am Netz, ~8 mA, Polarität belegt richtig** ✓ |
| **Brummtest Hauptplatine** | **bestanden** — Etappe 2 abgehakt ✓ |
| **Funktionstest Filter 2** | **bestanden — filtert, Grenzfrequenz verstellbar** ✓ |

### Die beiden Funktionstests, wie sie wirklich gehen

`AUFBAU.md` beschreibt beide Tests über Wege, die **durch das Bedienfeld**
laufen. Das ist nicht gebaut, also funktionieren die Anweisungen so nicht.
Die Ersatzwege, die am 06.11.2026 funktioniert haben:

**Brummtest Hauptplatine.** Nicht `J813` Pin 1 berühren — von dort läuft das
Signal über `C801` nach `J812` Pin 1 zu den Mixer-Fadern am Bedienfeld und über
das Lautstärkepoti zurück auf `J812` Pin 11. Die Kette ist an zwei Stellen
offen. **Stattdessen `J812` Pin 11 direkt berühren** — der Pin geht unmittelbar
auf `U901` Pin 3, den Eingang des LM386, und ist unbeschaltet also eine gute
Antenne. Brummt sofort.

**Funktionstest Filter.** Statt `J816` → `J413` und `J414` → `J817`:

| von | nach | was |
|---|---|---|
| `J412` Pin 1 | `J412` Pin 2 | 47 kΩ (Cutoff A) |
| `J412` Pin 3 | `J412` Pin 4 | 47 kΩ (Cutoff B) |
| `J412` Pin 5 | `J412` Pin 6 | 20 kΩ (Resonanz) |
| `J412` Pin 7 | `J812` Pin 11 | Draht **mit 10 kΩ in Reihe** |

Die Brücke Pin 7 → Pin 12 aus der Anleitung entfällt: **Pin 7 ist selbst der
Tiefpass-Ausgang** (`/F4_LP`, `U401` Pin 8). Pin 12 ist nur der Verteilerpunkt,
auf den der Wahlschalter am Bedienfeld einen der vier Ausgänge legt.

Signal rein: **Finger auf `J412` Pin 11** (`/MIX_OUT`, der Filtereingang).

**Die 10 kΩ in der Leitung sind nicht optional.** Der LM386 verträgt als
absoluten Grenzwert **±0,4 V am Eingang**, ein TL074-Ausgang liefert ±10 V.
Vor dem Anstecken deshalb `J412` Pin 7 gegen Masse messen: muss ~0 V sein.

Nachweis der Filterwirkung über den Widerstand auf Pin 1/2, mit `C401` = 15 nF
und `R401` = 1 kΩ in Reihe:

| Widerstand | Grenzfrequenz | Klang |
|---|---|---|
| 100 kΩ | ca. 105 Hz | dumpf |
| 47 kΩ | ca. 220 Hz | mittel |
| 10 kΩ | ca. 1 kHz | hell |

### Offen

1. Platinen 3 und 4 mit derselben Dreier-Prüffolge freigeben
   (Chip-Ausrichtung, Pin 4 gegen Pin 11, Elko-Polung)
2. Platine 1: toten Chip auslösen, 3-mm-Lücke reinigen, neuer Chip
3. Sicherungsfrage: Clips passen nicht in `F901`/`F902` (dokumentiert
   04.11.2026), gehört aufs Platinchen, braucht `T 1 A` — nicht beschaffbar
4. **Etappe 4, Oszillatoren — aber Nr. 1 allein bauen und prüfen, bevor
   Nr. 2 und 3 angefangen werden.** Genau diese Regel steht in `AUFBAU.md`
   und wurde bei den Filtern übergangen

---

## Bekannte, akzeptierte Abweichungen

### Oszillatorplatine Nr. 2, `U102`: Zinnbrücke Pin 3 ↔ Pin 4

Festgestellt 07.11.2026. Unter dem Gehäuse des `74LVC2G17` sitzt Zinn, das
Pin 3 und Pin 4 verbindet. Von aussen nicht sichtbar, mit Entlötlitze nicht
erreichbar.

**Bleibt drin. Elektrisch nachweislich wirkungslos:**

| Pin | Funktion | im Schaltplan |
|---|---|---|
| 3 | Eingang 2A | an Masse |
| 4 | Ausgang 2Y | unbeschaltet |

Der `74LVC2G17` ist ein nicht-invertierender Puffer. Eingang 2A an Masse heisst
Ausgang 2Y auf 0 V — der Chip treibt Pin 4 selbst auf Masse. Die Brücke
verbindet 0 V mit 0 V, es kann kein Strom fliessen, auch im Betrieb nicht.
Der zweite Puffer ist im Entwurf ungenutzt.

**Geprüft und ausgeschlossen:** +5 V gegen Masse (`C107` näheres gegen ferneres
Loch) piepst **nicht** — der Klecks reicht also nicht bis Pin 5, der nur
0,95 mm von Pin 4 entfernt liegt. Das wäre der einzige gefährliche Fall
gewesen.

**Nicht behoben, weil** die Reparatur das Auslöten eines SOT-23-6 mit 0,95 mm
Raster erfordert hätte. Risiko für Pads und Platine grösser als ein Fehler mit
nachweislich null Wirkung.

### Erste Oszillatorplatine verworfen

Platine Nr. 1 wurde am 06.11.2026 beim Entlöten einer Brücke an `U102`
beschädigt und ersetzt. Sie bleibt als Übungsstück für Entlötlitze und
Auslöttechnik.

**Lehre daraus, für die nächste Platine übernommen:** die Reihenfolge der drei
SMD-Chips in `AUFBAU.md` (`U103` → `U104` → `U102`) ist eine **Lernreihenfolge**,
keine technische Vorgabe. Der schwierigste Chip wird auf dem **leeren** Brett
gelötet, also **`U102` zuerst**, dann `U103`, dann `U104`. Die Regel, dass alle
SMD-Chips vor allen bedrahteten Teilen kommen, bleibt.

### Chipbestand

10 bestellt, **2 zerstört**, 3 auf Platinen 2/3/4. Noch gebraucht: Platine 1
plus 3 Oszillatoren = 4. **Reserve: 1.**

---

Stand 05.11.2026 abends. Zwei TL074 auf Filterplatine Nr. 1 zerstört:
Chip 1 wurde heiss (Zinn unter dem Gehäuse, Pin 4 gegen Pin 11 ≈ 100 Ω),
Chip 2 ist nach etwa 10 Sekunden geplatzt.

---

## 1. Was ein geplatztes Gehäuse bedeutet

Das ist die wichtigste Erkenntnis des Abends, und sie dreht die
Verdachtsreihenfolge um.

Im Chip sitzt der Silizium-Würfel (das Die), und von ihm gehen vierzehn
Golddrähte von 25 Tausendstel Millimeter Dicke zu den Beinchen. Diese Drähte
schmelzen bei etwa 1 bis 2 Ampere. Wenn das passiert, verdampft im Inneren
Metall, der Druck steigt, und das Gehäuse reisst auf. Genau das ist passiert.

**Daraus folgt: der Strom ist durch das Die geflossen, nicht daneben vorbei.**

Und das schliesst etwas aus, was gestern noch der Hauptverdacht war:

> Eine Zinnbrücke zwischen Pad 4 und Pad 11 **unter** dem Gehäuse kann den Chip
> nicht zum Platzen bringen. Eine solche Brücke hat fast null Ohm. Der Strom
> nimmt den Weg durch das Zinn und läuft am Die vorbei. Die Leistung fällt dann
> im Netzteil und in den Kabeln an, nicht im Chip. Das Netzteil würde warm, der
> Chip nicht.

Chip 1 passt genau in dieses Bild: 100 Ω Brücke, 4 W im Zinn, der Chip wurde
heiss, ist aber nicht geplatzt.

Chip 2 passt **nicht** in dieses Bild. Da ist Strom durch das Die geflossen.
Und es gibt nur einen realistischen Weg, auf dem das passiert:

**Die Versorgung lag verkehrt an — Pin 4 negativ, Pin 11 positiv.**

Ein Operationsverstärker hat zwischen den beiden Versorgungspins eine
Sperrschicht, die in dieser Richtung leitet wie eine Diode. Der Chip wird dann
zum Kurzschluss mit etwa 1 V Spannungsabfall, und das ganze Netzteil fliesst
durch den Golddraht. Nach Sekundenbruchteilen ist es vorbei.

---

## 2. Abgleich mit KiCad — was ich überprüft habe

Alles mit `pcbnew` direkt aus den Projektdateien gelesen, nicht aus dem
Gedächtnis.

### Die Schaltung selbst ist in Ordnung

Zuordnung Pad → Netz → Funktion des TL074, komplett:

| Pad | Netz | TL074-Funktion | stimmt |
|---:|---|---|:--:|
| 1 | `/F4_HP` | Ausgang A | ✓ |
| 2 | `Net-(U401A--)` | Eingang A − | ✓ |
| 3 | `Net-(U401A-+)` | Eingang A + | ✓ |
| **4** | **`+12V`** | **V+** | ✓ |
| 5 | `GNDREF` | Eingang B + | ✓ |
| 6 | `Net-(U401B--)` | Eingang B − | ✓ |
| 7 | `/F4_BP` | Ausgang B | ✓ |
| 8 | `/F4_LP` | Ausgang C | ✓ |
| 9 | `Net-(U401C--)` | Eingang C − | ✓ |
| 10 | `GNDREF` | Eingang C + | ✓ |
| **11** | **`-12V`** | **V−** | ✓ |
| 12 | `GNDREF` | Eingang D + | ✓ |
| 13 | `Net-(U401D--)` | Eingang D − | ✓ |
| 14 | `/F4_NOTCH` | Ausgang D | ✓ |

Die Fertigungs-Stückliste `filter-BOM-jlcpcb.csv` sagt `TL074CDR`, `C12594`,
`SOIC-14`. Die alten Dateien in `work/BOM_*.csv` nennen noch `OPA4196` — die
sind veraltet, der Chip wurde später getauscht. Beide haben ohnehin dieselbe
Pinbelegung, das ist also kein Problem.

**Die Platine ist richtig entworfen. Der Fehler sitzt im Aufbau.**

### Die Versorgung auf der Hauptplatine hat einen Verpolschutz

```
J990.1 (/VIN_P) -> F901 -> D907 Anode   -> D907 Kathode = +12V -> J811.1, J810.1
J990.2                                           GNDREF -> J811.2, J810.2
J990.3 (/VIN_N) -> F902 -> D908 Kathode -> D908 Anode   = -12V -> J811.3, J810.3
```

D907 und D908 sind Schottky-Dioden und sperren, wenn am Eingang die Polung
vertauscht ist. Die Notiz im Schaltplan sagt das auch so:

> "D907/D908 (Schottky) sperren, wenn der Netzstecker verpolt ist:
> +12 V und −12 V koennen dann nicht vertauscht an die ICs gelangen."

**Das heisst: ein verpoltes Netzteil kann den Chip normalerweise nicht
erreichen.** Mit einer Ausnahme — der Flickdraht an D907. Wenn der die Diode
überbrückt, ist der Schutz auf der Plusschiene weg. Das ist Prüfung A5 morgen.

### Und genau da liegt eine Falle in der Geometrie

Nachtrag vom späten Abend, aus den Kupferdaten der Hauptplatine:

| Punkt | x-Lage |
|---|---|
| D907 **Kathode** (= `+12V`, das richtige Ziel) | 151,92 |
| D907 **Anode** (= `Net-(D907-A)`, vor der Diode) | 162,08 |
| `C931` Plus | 170,75 |

Alle drei liegen auf derselben Linie bei y = 68.

- Kathode → `C931` Plus: **18,8 mm**
- Anode → `C931` Plus: **8,7 mm**

**Der falsche Anschluss ist der nähere und damit der verlockendere.** Ein
Flickdraht von der Anode zu `C931` überbrückt D907 vollständig und legt den
Verpolschutz still — und sieht dabei aus wie eine saubere kurze Reparatur.

Dazu kommt: die Anoden-Bahn läuft direkt neben der Diode, bei etwa
(159 / 65,5), mit nur **0,55 mm freiem Spalt** an der +12-V-Bahn vorbei
(0,30 mm und 0,60 mm Bahnbreite, 1,00 mm Mitte zu Mitte). Genau dort wurde beim
Reparieren des gerissenen Lochs geschabt und gelötet. Ein Zinnrest an dieser
Stelle wirkt genauso wie der falsch gesetzte Flickdraht.

Zwei weitere Abstände, zur Vollständigkeit:

- `/VIN_P` gegen `/VIN_N` kommen bei J990 auf **1,65 mm** heran — dort sitzt
  das Dupont-Provisorium. Eine Brücke dort liegt aber **vor** den Dioden und
  schliesst nur den Eingang kurz, sie erreicht keinen Chip.
- `+12V` gegen `-12V` zeigen rechnerisch 1,00 mm, aber auf **verschiedenen
  Lagen** (B.Cu gegen F.Cu). Dazwischen liegt das Platinenmaterial, das ist
  kein Risiko.

### Geometrie unter dem Chip

- Gehäuse `SOIC-14_3.9x8.7mm_P1.27mm`, Pads 1,95 × 0,6 mm, Raster 1,27 mm
- Pad 4 liegt bei x 137,525, Pad 11 bei x 142,475 — **genau gegenüber**
- Dazwischen: **3,0 mm blankes Platinenmaterial**, vollständig unter dem
  Gehäuse verborgen (Gehäusebreite 3,9 mm, Kanten bei 138,05 und 141,95)
- kein Kupfer in dieser Lücke, nur Lötstopplack

Das ist die Stelle, an der bei Chip 1 das Zinn sass. Sichtbar ist sie nur,
wenn man flach über die Platine ins Licht schaut — oder gar nicht.

### Es gibt doch eine Pin-1-Markierung

Ich hatte dir gesagt, auf dem Siebdruck sei nur ein Rechteck. Das war
unvollständig. Auf `F.Silkscreen` liegt ein **Dreieck** mit den Eckpunkten
(137,40 / 91,63), (137,16 / 91,30), (137,64 / 91,30) — also etwa einen halben
Millimeter gross, direkt aussen an der Ecke des aufgedruckten Rechtecks, an dem
Ende, wo `U401` steht. **Die Spitze zeigt auf Pad 1.**

Damit ist die Ausrichtung eindeutig prüfbar, ohne irgendwas zu messen.

### Wo +12 V und −12 V sich sonst nahe kommen

Kleinster Abstand der beiden Versorgungsbahnen auf der ganzen Filterplatine:
**1,25 mm Mitte zu Mitte**, bei 0,6 mm Bahnbreite, also 0,65 mm freier Spalt.
Das ist am oberen Rand, bei y 65,1 und 66,35, über etwa 15 mm Länge — in dem
Bereich zwischen der einen dreipoligen Stiftleiste und den beiden Elkos.

Dort kann ein Zinnspritzer oder ein abgeknipstes Drahtende brücken. Das wäre
aber wieder nur ein Kurzschluss **neben** dem Chip — der Chip würde davon nicht
platzen. Also Nebenverdacht, nicht Hauptverdacht.

### Die Elkos — eine echte Falle

| Teil | Loch mit `+` | anderes Loch |
|---|---|---|
| C405 | **+12 V** | Masse |
| C406 | **Masse** | **−12 V** |

C406 ist der "verkehrte" Elko: sein Plus gehört an Masse, sein Minus an −12 V.
Die Regel **"langes Bein in das Loch mit dem `+`"** stimmt für beide. Wer aber
nach Gefühl "Plus an die Schiene" steckt, hat C406 verpolt. Ein verpolter
10-µF-Elko an 9 V gast nach einigen Sekunden aus und platzt — mit Knall. Das
sieht aus wie ein geplatzter Chip, ist aber einer der Elkos.

**Darum morgen zuerst anschauen, was genau geplatzt ist.**

### Was als Ursache ausgeschlossen ist

- **Die zwölfpolige Steckerleiste `J412`.** Dort liegt überhaupt keine
  Versorgung an, nur Signale: `/F4_HP`, `/F4_T1W`, `/F4_BP`, `/F4_T2W`,
  `/F4_BP`, `/F4_RESW`, `/F4_LP`, `/F4_HP`, `/F4_BP`, `/F4_NOTCH`,
  `/MIX_OUT`, `/FILT_A_OUT`. Eine falsch gesetzte Drahtbrücke dort kann
  höchstens zwei Ausgänge gegeneinander schalten — das sind etwa 40 mA und
  0,7 W, der Chip wird warm, platzt aber nicht.
- **Die Eingänge.** Alle Signale kommen über mindestens 1 kΩ an den Chip. Da
  kann kein zerstörender Strom durch.
- **Falsche Versorgungsspannung.** 9 V, der TL074 verträgt ±18 V.
- **Verwechselter Chip.** Die anderen beiden SMD-Typen im Projekt sind
  SOIC-8 und SOT-23-6 — die passen gar nicht auf das Feld.

---

## 3. Die Fehlerliste, nach Wahrscheinlichkeit

| # | Verdacht | warum | Prüfung | Dauer |
|---:|---|---|---|---|
| 1 | **Chip 180° verdreht** | Pin 4 sitzt dann auf Pad 11 und umgekehrt → Versorgung verkehrt → Golddraht verdampft. Erklärt das Platzen vollständig. **Und alle vier Chips wurden im gleichen Arbeitsgang gelötet.** | Dreieck auf dem Siebdruck gegen Punkt/Delle auf dem Chip, bei Platine 2, 3, 4 | 5 min |
| 2 | **Dreipoliges Kabel gekreuzt** | Pin 1 auf Pin 3 → Versorgung verkehrt, gleiche Wirkung. Diese Prüfung steht seit dem ersten Einschalten offen. | Durchgang `J811` Pin 1 → `J410` Pin 1 und Pin 3 | 5 min |
| 3 | **Elko C406 verpolt** | dann ist nicht der Chip geplatzt, sondern der Elko | anschauen: langes Bein im Loch mit `+`? | 2 min |
| **4** ★ | **Flickdraht überbrückt D907** | dann ist der Verpolschutz weg, und ein vertauschter Netzteilstecker kommt am Chip an. **Die Geometrie macht genau diesen Fehler wahrscheinlich: das falsche Bein liegt 8,7 mm von `C931` entfernt, das richtige 18,8 mm.** Siehe Abschnitt 2 | Diodenmessung über die beiden Beine von D907 | 3 min |
| 5 | **Zinnrest unter dem Gehäuse** von der ersten Reparatur | die 3-mm-Lücke wird von Entlötlitze auf den Pads nicht erreicht | Ohm Pad 4 gegen Pad 11 **ohne Chip** | 2 min |
| 6 | **Brücke zwischen den Versorgungsbahnen** am Platinenrand | 0,65 mm Spalt | dieselbe Messung wie #5 deckt das mit ab | 0 min |
| 7 | **Netzteil-Platinchen liefert verkehrt** | das ist das einzige Stück der Kette, von dem es keine KiCad-Datei gibt | Spannung an `J990` Pin 1 und Pin 3 gegen Pin 2 | 3 min |

### Nachtrag 06.11.2026 — die Rangfolge kippt noch einmal

Beim systematischen Durchgehen aller Ursachen wird ein Hinweis entscheidend,
den ich zu leicht genommen hatte: **beide Chips sind fortschreitend warm
geworden, nicht schlagartig.** Chip 1 "wurde heisser", Chip 2 "blieb zuerst
kühl, und dann begann er wärmer zu werden".

Eine verkehrte Versorgung ist **konstant** — gestecktes Kabel, sitzender Chip.
Sie hätte beim ersten Einschalten getötet. Es hat aber dreimal gedauert, also
hat sich etwas **verändert**.

Und die Leistungsrechnung zeigt, was. Entscheidend ist nicht, *ob* eine
Zinnbrücke unter dem Gehäuse sitzt, sondern **welchen Widerstand** sie hat:

| Widerstand der Brücke | Strom | Leistung in der Brücke | Folge |
|---|---|---|---|
| 1,5 mΩ (sauberes Zinn) | 1 A | 0,0015 W | Netzteil wird warm, Platine nicht |
| **100 Ω** | 180 mA | **3,2 W** | Chip wird heiss, überlebt → **Chip 1** |
| **5 bis 30 Ω** | ~1 A | **10 bis 20 W** | Gehäuse kocht von unten auf → **Chip 2** |

Die 10 bis 20 W fallen in einem 3-mm-Fleck an, 0,1 mm unter dem Kunststoff.
Das Harz verkohlt, gast aus, das Gehäuse reisst auf.

Chip 1 hatte gemessene **100 Ω**. Ein verkohlter Pfad aus Flussmittelrest und
angebranntem Platinenmaterial wird mit jedem Einschalten leitfähiger und wandert
von 100 Ω **durch das tödliche Band von 5 bis 30 Ω**. Dazu passt, dass die
Lücke nie gereinigt wurde: Entlötlitze auf den Pads erreicht sie nicht.

**Damit lautet das Fazit:**

- **Hauptursache, hohe Sicherheit:** widerstandsbehafteter Schluss zwischen den
  Versorgungspins in der 3-mm-Lücke unter dem Gehäuse. Ein Befund erklärt
  alles: warum nur Platine 1, warum zweimal, warum Verlauf statt Schlag, warum
  10 Sekunden, warum schon einmal 100 Ω gemessen wurden.
- **Zweitverdacht, nicht ausgeschlossen:** Versorgung verkehrt (Verdacht 1, 2,
  4). Dagegen spricht der Verlauf, dafür spricht, dass es ungeprüft ist.
- **Mitverdacht:** C406 verpolt — erklärt einen Knall, keinen toten Chip.
- **Zusätzlich ausgeschlossen:** offene Integratoren. 50 pA in 15 nF sind
  3,3 mV/s, also **90 Minuten** bis zur Schiene, bei 0,1 W. Für 10 Sekunden um
  Grössenordnungen zu träge. Meine Beruhigung vom 04.11. ist damit endgültig
  vom Tisch.
- **Ebenfalls ausgeschlossen:** ein **harter** Kurzschluss unter dem Gehäuse —
  der kocht das Netzteil, nicht die Platine.

**Folge für den Ablauf:** Prüfung B4 (Ohm Pad 4 gegen Pad 11, ohne Chip) ist
nicht mehr Schritt fünf, sondern die Messung, die alles entscheidet. Sie macht
eine überprüfbare Vorhersage:

| Messwert ohne Chip | bedeutet |
|---|---|
| **stabiler Wert, wenige Ω bis einige 100 Ω** | Hauptursache **bestätigt** — Lücke reinigen, Sache erledigt |
| Wert **steigt** ins Unendliche | Hauptursache **widerlegt** — dann rückt die verkehrte Versorgung auf Platz 1 |

Die beiden kostenlosen Sichtprüfungen A2 (Dreieck) und A4 (C406) bleiben
trotzdem vorgeschaltet, weil sie drei weitere Chips schützen.

Einschränkung: das alles hängt daran, dass die Beschreibung "kühl, dann wärmer"
den Verlauf richtig wiedergibt. Die Ohm-Messung entscheidet es in beide
Richtungen.

### Korrektur am Fazit, noch am 06.11.2026

Zwei Pfeiler der Begründung oben halten nicht:

1. **"Nur Platine 1 ist gestorben" ist kein Argument.** Platine 1 ist die
   einzige, die überhaupt je Strom gesehen hat. Dass 2, 3 und 4 leben, sagt
   nichts über ihren Zustand.
2. **"Verlauf statt Schlag" trennt schwächer als behauptet.** Begrenzen die
   9-V-Adapter den Strom, fallen bei verkehrter Versorgung etwa 0,3 W im Die
   an — das wird langsam warm, heizt sich selbst hoch und platzt dann. Also
   ebenfalls ein Verlauf.

**Damit stehen zwei Ursachen gleichauf:**

| Ursache | dafür spricht |
|---|---|
| **Gekreuztes Kabel** (falsch geladene Hülsen) | nie geprüft; erklärt beide Chips; piepst bei jeder bisherigen Prüfung brav mit |
| **Widerstandsbehafteter Schluss in der Lücke** | dort wurde Zinn **gesehen**; 100 Ω wurden dort gemessen; die Lücke wurde nie gereinigt |

Beim 100-Ω-Wert von Chip 1 ist zu beachten: den liefert auch ein **bereits
geschädigter** Chip quer über seine Versorgungspins. Der Wert allein trennt die
zwei Ursachen nicht, das gesehene Zinn schon.

**Folge für die Reihenfolge: A2b (Hülsen, zehn Sekunden, kein Werkzeug) geht
vor allem anderen.** Danach A2, A3, A4, dann der Chip und die Lücke.

★ = nach dem Kupfer-Abgleich am Abend hochgestuft. Gearbeitet wird in der
Reihenfolge von Abschnitt 6 (A1 bis A6), nicht in der Nummerierung dieser
Tabelle — die Tabelle ist nur die Liste zum Abhaken.

Die drei Verdachtsmomente 1, 2 und 4 haben alle **dieselbe Wirkung**: Pin 4
wird negativ und Pin 11 positiv. Sie unterscheiden sich nur darin, **wo** die
Vertauschung passiert — im Chip, im Kabel oder auf der Hauptplatine. Das ist
der Grund, warum alle drei geprüft werden müssen, auch wenn einer davon schon
ein Ergebnis liefert.

Zusammen: **20 Minuten, ohne einen einzigen Lötkolben und ohne Strom**, und
damit ist jede Ursache erfasst, die einen Chip platzen lassen kann.

Das ist der Zeitgewinn gegenüber heute: nicht einschalten und schauen, sondern
erst messen, dann einschalten.

---

## 4. Werkzeug und Material für morgen

### Hast du wahrscheinlich schon

- Multimeter — gebraucht werden: Durchgangsprüfer, Ohm, Gleichspannung,
  **Diodenmessung**
- Lötkolben mit feiner Spitze, auf **320 °C**
- Entlötlitze
- Seitenschneider, fein
- Pinzette
- Isopropanol und Wattestäbchen oder ein Pinsel
- Lötzinn

### Brauchst du neu oder solltest du bereitlegen

| Was | wofür |
|---|---|
| **Lupe** oder Handy mit Makro und gutem Licht | das Pin-1-Dreieck ist 0,5 mm gross, der Punkt auf dem Chip noch kleiner |
| **Flussmittel** (Stift oder Spritze, No-Clean) | ohne das wird SMD-Löten Glücksspiel |
| **Krokodilklemmen oder Messklemmen**, 2 Paar | damit du beim Messen zwei Hände frei hast statt null |
| **1 × Widerstand 1 kΩ** | die Strombremse, siehe Abschnitt 5. Du hast 30 Stück bestellt (`A-2200`), mehr als genug |
| **ein opferbares dreipoliges Kabel** oder etwas Litze | die rote Ader wird durchgeschnitten |
| **Schutzbrille** | es ist dir heute schon einmal ein Bauteil geplatzt |
| Kreppband oder Kaptonband | hält den Chip beim ersten Beinchen fest |

### Brauchst du **nicht** zu kaufen

- **Sicherungen.** Du hast 5 Stück `T 500 mA` (`C142727`) und 10
  Sicherungsclips (`C151075`) bestellt — nur 4 Clips werden gebraucht. Das
  liegt alles da.
- **Einen zweiten 12-V-Adapter.** Mit der Strombremse aus Abschnitt 5 reichen
  die 9-V-Adapter für die Fehlersuche vollkommen. Das ist ein Thema für
  später, nicht für morgen.

---

## 5. Die Strombremse — damit nichts mehr sterben kann

### Erst die Rechnung, die weh tut

SOIC-14-Chips im Projekt: `U103`, `U203`, `U303` (Oszillatoren) und `U401`,
`U501`, `U601`, `U701` (Filter) = **7 Stück gebraucht**.
Bestellt: **10**. Zerstört: **2**. Bleiben **8**.

**Du hast genau einen Chip Reserve.** Das ist der Grund, warum morgen nichts
mehr ohne Strombegrenzung eingeschaltet wird.

### Warum eine Sicherung das nicht löst

Eine Sicherung schützt die Leitung vor Feuer. Sie schützt keinen Chip. Der
Golddraht im Chip verdampft bei 1 bis 2 A in Millisekunden, eine träge
500-mA-Sicherung braucht bei 2 A noch Zehntelsekunden. Zu langsam.

**Nur ein Widerstand in Reihe schützt einen Chip.** Der kann gar nicht zu
langsam sein, weil er den Strom von Anfang an nicht durchlässt.

### Der Aufbau

Nimm das dreipolige Kabel zur Filterplatine und schneide **nur die rote Ader**
(Pin 1, +12 V) in der Mitte durch. Beide Enden abisolieren. Dazwischen klemmst
du den 1-kΩ-Widerstand.

Das reicht, obwohl nur eine Ader unterbrochen ist. Denn jeder Fehler, der einen
Chip tötet — Versorgung verkehrt, +12 V gegen −12 V, +12 V gegen Masse — führt
den Strom durch diese rote Ader. Der einzige Fehler, der daran vorbeikommt, ist
−12 V gegen Masse, und der bringt höchstens die Minusschiene zum Einbrechen.

### Der Widerstand ist dein Strommesser

Multimeter auf Gleichspannung, die beiden Spitzen links und rechts an den
Widerstand. Dann gilt, weil es 1 kΩ sind:

> **Jedes Volt über dem Widerstand ist genau ein Milliampere Strom.**

| Anzeige | bedeutet |
|---|---|
| **0 V** | es fliesst nichts. Kein Chip drin, oder eine Unterbrechung |
| **1 bis 3 V** | 1 bis 3 mA — **genau richtig** für einen TL074 im Ruhezustand |
| **4 bis 6 V** | zu viel. Ein Fehler, aber kein Kurzschluss |
| **über 7 V** | Kurzschluss. Ausschalten und suchen |

Und das Beste daran: bei einem **vollen** Kurzschluss fliessen durch 1 kΩ nur
9 mA. Das sind 0,08 Watt. **Da kann nichts kaputtgehen, auch nicht in einer
Stunde.** Du kannst in Ruhe messen, drehen, nachdenken.

Wenn alles sauber ist, ersetzt du den Widerstand durch ein Stück Draht, und
dann läuft der Filter mit voller Spannung.

---

## 6. Ablauf morgen

### Teil A — 20 Minuten, kein Lötkolben, kein Strom

**A1. Was ist überhaupt geplatzt?**
Schau Platine 1 genau an. Ist der schwarze 14-beinige Chip aufgerissen, oder
ist einer der beiden Elkos (die kleinen Töpfchen) oben aufgeplatzt? Danach
richtet sich alles Weitere. Mach ein Foto und schick es mir.

**A2. Chip-Ausrichtung auf Platine 2, 3 und 4 — der wichtigste Handgriff**

An dem Ende, wo `U401` auf die Platine gedruckt ist, sitzt direkt aussen an der
Ecke des aufgedruckten Rechtecks ein **winziges Dreieck**, etwa einen halben
Millimeter gross. Es zeigt auf Pin 1.

Auf dem Chip selbst ist eine **Delle oder ein aufgedruckter Punkt** in einer
Ecke. Der muss über dem Dreieck liegen.

- **Liegt er dort** → Ausrichtung in Ordnung, Verdacht 1 ist weg.
- **Liegt er am anderen Ende** → **das ist die Ursache.** Dann sind alle vier
  Chips verdreht, und du hast gerade drei weitere gerettet. Sofort aufhören und
  mir schreiben.

**A2b. Die Hülsen im Stecker — zehn Sekunden, ohne Messgerät, zuerst**

Die Gehäuse lassen sich nicht verkehrt einstecken. Die **Kontakte** lassen sich
aber in jede Kammer laden, und dann ist das Kabel gekreuzt, obwohl jeder
Stecker perfekt passt und jede Durchgangsprüfung piepst.

Die typische Falle: beim Bestücken legt man die zwei Gehäuse **einander
zugewandt** hin, weil sie später zwei Platinen verbinden. Dadurch wird eines
gespiegelt, und Rot landet am einen Ende in Kammer 1, am anderen in Kammer 3.

Prüfung — Kabel in die Hand, beide Enden **gleich** halten:

1. beide Rasthaken zu dir
2. beide Steckflächen (die Löcher) zu dir
3. beide gleich herum, **nicht** gegenüber

> **Rot muss auf derselben Seite liegen.** Links bei einem Ende und rechts beim
> anderen heisst: gekreuzt.

Beim Prüfen denselben Fehler vermeiden wie beim Bauen: die Enden einander
zugewandt halten spiegelt eines, und ein richtiges Kabel sieht falsch aus.

Drei weitere Hülsen-Fehler, die einen Blick wert sind:

| Fehler | Symptom |
|---|---|
| Kontakt nicht ganz eingeschoben, rutscht beim Stecken zurück | eine Schiene fehlt oder wackelt. Leicht an jeder Ader ziehen, der Kontakt darf sich nicht bewegen |
| Kontakt verkehrt herum eingeschoben, rastet nicht | dasselbe |
| einzelne Litze reicht in die Nachbarkammer | schliesst eine Schiene gegen Masse. Mit der Lupe in die Steckfläche schauen |

Keiner davon lässt einen Chip platzen — **nur die Kreuzung tut das.**

**A3. Das dreipolige Kabel** — steht seit dem ersten Einschalten offen

Pin 1 ist auf der Platine markiert: **an einem Ende des aufgedruckten
Steckerumrisses sitzt aussen ein kleiner Winkel, zwei kurze Striche, die eine
Ecke bilden.** Das Ende mit dem Winkel ist Pin 1, und Pin 1 ist **+12 V**. Das
gilt für `J410`, `J411`, `J811`, `J990` und `J810` gleich.

Kabel in `J811` auf der Hauptplatine und in `J410` auf der Filterplatine
gesteckt. Durchgangsprüfer:

| schwarz | rot | soll |
|---|---|---|
| `J811` Endpin | `J410` Endpin auf derselben Seite | **piepst** |
| `J811` Endpin | `J410` Endpin auf der anderen Seite | **piepst nicht** |
| `J811` Mittelpin | `J410` Mittelpin | **piepst** |

Welches Ende Pin 1 ist, spielt hier keine Rolle. Entscheidend ist nur, dass du
beide Platinen so hinlegst, dass die Stiftleisten gleich ausgerichtet sind, und
dass es dann von Endpin zu Endpin auf **derselben** Seite piepst.

**A4. Die Elkos auf allen vier Platinen**

Es sind die beiden kleinen Töpfchen mit je zwei Beinen. An einem Loch jedes
Elkos steht ein `+` im Siebdruck.

So findest du heraus, welcher welcher ist, ganz ohne links und rechts:

1. Der **Mittelpin** jeder dreipoligen Stiftleiste ist **Masse**.
2. Miss von jedem `+`-Loch zum Mittelpin.
3. Der Elko, bei dem es **piepst**, ist **C406** — sein Plus gehört an Masse.
4. Der Elko, bei dem es **nicht piepst**, ist **C405** — sein Plus gehört an
   +12 V.

Bei **beiden** muss das lange Bein in dem Loch mit dem `+` sitzen. Wenn der
Elko schon abgeschnitten ist: die Seite mit dem hellen Streifen und dem `−` auf
dem Becher ist das kurze Bein und gehört in das Loch **ohne** `+`.

**A5. D907 auf der Hauptplatine** — überbrückt der Flickdraht die Diode?

Nach der Geometrie aus Abschnitt 2 ist das der wahrscheinlichste Wegbereiter
für einen verpolten Chip. Diese Prüfung ernst nehmen.

Multimeter auf **Diodenmessung**. Die beiden Beine von D907 messen, einmal so,
einmal umgedreht:

| Ergebnis | bedeutet |
|---|---|
| in einer Richtung 0,2–0,4 V, in der anderen nichts | **gut**, die Diode arbeitet, Verpolschutz steht |
| in **beiden** Richtungen fast 0 V | **die Diode ist überbrückt** → Verpolschutz ist weg |

Falls überbrückt, finde heraus wodurch. So unterscheidest du die beiden Beine
ohne links und rechts:

1. Das Bein, das zum **Endpin von `J811`** piepst (dem Endpin, der nach A6
   positiv war), ist die **Kathode**. Dorthin, und nur dorthin, darf der
   Flickdraht gehen.
2. Das andere Bein ist die **Anode**. Es muss zur **Sicherungsstelle F901**
   piepsen — das ist die längliche Stelle mit vier Löchern in der Nähe.
3. Piepst das Flickdraht-Ende zur **Anode**, sitzt der Draht am falschen Bein.
   Umlöten: er gehört an das Bein, das zu `J811` piepst.
4. Piepst es nirgends falsch, schau mit der Lupe auf die Bahn **neben** der
   Diode. Dort sind nur 0,55 mm Spalt, und ein Zinnrest wirkt genauso.

Und die eine Messung, die die ganze Schutzkette auf einmal prüft —
Diodenmessung von der Sicherungsstelle F901 zum positiven Endpin von `J811`:

| Ergebnis | bedeutet |
|---|---|
| in einer Richtung 0,2–0,4 V, in der anderen nichts | Kette in Ordnung: Brücke, Diode, Schiene |
| in beiden Richtungen fast 0 V | irgendwo überbrückt |
| in beiden Richtungen nichts | Unterbrechung — die Drahtbrücke an F901 fehlt oder ist kalt |

**A6. Was das Netzteil-Platinchen wirklich liefert**

Das ist das einzige Stück der Kette ohne Zeichnung. Hauptplatine mit Strom,
aber **ohne Filterkabel**. Schwarz auf `J990` Mittelpin:

| rot | soll |
|---|---|
| `J990` ein Endpin | etwa **+9 V** |
| `J990` anderer Endpin | etwa **−9 V** |

Steht an beiden Endpins dasselbe Vorzeichen, ist das Platinchen falsch
verdrahtet, und wir haben die Ursache gefunden.

Danach dasselbe an `J811`: ein Endpin positiv, der andere negativ, gegen den
Mittelpin. Und merk dir, **welcher** Endpin positiv war — das ist Pin 1.

---

### Teil B — Platine 1 instandsetzen

Nur wenn Teil A keinen Fehler gefunden hat, oder nachdem er behoben ist.

**B1. Chip herunter.** Alle 14 Beinchen direkt am Gehäuse abknipsen, Gehäuse
abheben, dann die Stummel einzeln: Spitze auf 320 °C, Flussmittel, 1 bis 2
Sekunden, wegziehen. Danach Entlötlitze über jede Fläche.

**B2. Die Lücke säubern** — das ist der Punkt, der beim ersten Mal fehlte.
Zwischen den beiden Pad-Reihen liegen 3,0 mm blankes Material, und da hat beim
ersten Chip das Zinn gesessen. Entlötlitze auf den Pads erreicht diese Stelle
**nicht**. Also: Flussmittel in die Lücke, mit der Lötkolbenspitze flach
darüber, dann Isopropanol und Wattestäbchen, und flach ins Licht schauen, ob
noch etwas glänzt.

**B3. Schaden begutachten.** Sind alle 14 Flächen noch da? Ein platzendes
Gehäuse kann eine Fläche mitreissen. Riecht es verbrannt? Foto an mich.

**B4. Die Messung, die alles entscheidet** — ohne Chip:

Zähle an beiden Langseiten des leeren Chipfeldes vom Ende mit `U401` aus
**vier Pads nach innen**. Diese zwei Pads liegen genau gegenüber: das sind
Pad 4 (+12 V) und Pad 11 (−12 V).

| Messung | soll |
|---|---|
| Ohm, Pad 4 gegen Pad 11 | Wert **steigt** und läuft ins Unendliche |
| Ohm, Pad 4 gegen Mittelpin der Stiftleiste | Wert **steigt** |
| Ohm, Pad 11 gegen Mittelpin der Stiftleiste | Wert **steigt** |

Das Steigen kommt von den Elkos, die sich aufladen — das ist normal und ein
gutes Zeichen. **Ein Wert, der stehen bleibt, ist der Kurzschluss.** Dann hast
du Verdacht 5 oder 6 gefunden.

Dieselbe Messung geht auch an den beiden Endpins einer dreipoligen Stiftleiste,
von Loch zu Loch statt auf den winzigen Flächen. Einfacher zu treffen, gleiches
Ergebnis.

**B5. Leer einschalten, mit Strombremse.** Kabel mit dem 1-kΩ-Widerstand
drin, Platine ohne Chip. Spannung über dem Widerstand messen: **soll fast 0 V
sein**, denn ohne Chip fliesst fast kein Strom. Dann Pad 4 und Pad 11 gegen den
Mittelpin messen:

| Pad | soll |
|---|---|
| Pad 4 | **positiv**, etwa +8,5 V |
| Pad 11 | **negativ**, etwa −8,5 V |

Das ist das, was der Chip gesehen hätte. Stimmt es hier, kann die Versorgung
den nächsten Chip nicht mehr töten.

---

### Teil C — neuer Chip

**C1. Löten.** Platine 1 ist deine Übungsplatine, hier darf es schiefgehen.
Flussmittel, Spitze verzinnen statt die Lötstelle, an der äusseren Pad-Kante
ansetzen, 1 bis 2 Sekunden pro Pin, etwa 3 mm Lötzinn für alle 14.
**Punkt auf dem Chip über das Dreieck im Siebdruck.**

**C2. Prüfen, vor dem Strom.**

| Messung | soll |
|---|---|
| Ohm, Pad 4 gegen Pad 11 | **mehrere kΩ** oder steigend. Ein stehender Wert um 100 Ω heisst: Zinn unter dem Gehäuse, nochmal von vorn |
| Durchgang, benachbarte Pins | **kein Paar piepst** — ausser den Masse-Pins |
| Masse-Pins | Pad 5, Pad 10 und Pad 12 piepsen untereinander und zum Mittelpin. **Das ist richtig so, die liegen laut Schaltplan alle an Masse** |

**C3. Einschalten, mit Strombremse.** Spannung über dem 1-kΩ-Widerstand:

| Anzeige | weiter |
|---|---|
| 1 bis 3 V | **gut.** Widerstand durch Draht ersetzen, dann Funktionstest |
| über 7 V | Kurzschluss. Ausschalten, zurück zu B4 |

Lass die Finger vom Chip. Die Temperatur sagt dir nichts Nützliches: das Die
ist nach Millisekunden auf Endtemperatur, der Finger merkt es erst nach
Sekunden. Der Widerstand sagt dir in einer Sekunde mehr als jedes Anfassen.

---

## 7. Was danach kommt

In dieser Reihenfolge, wenn Platine 1 läuft:

1. Die drei anderen Filterplatinen mit derselben Prüffolge durch — jede mit
   Strombremse, und bei jeder vorher Pad 4 gegen Pad 11.
2. Sicherungsclips und die `T 500 mA` einlöten (du hast sie da), damit die
   Drahtbrücken an F901/F902 verschwinden.
3. Den Flickdraht an D907 durch einen gelöteten Fädeldraht ersetzen.
4. Das Dupont-Provisorium an `J990` durch ein gecrimptes Kabel ersetzen.
5. Brummtest: LM386 in die Fassung `U901` (Kerbe beachten), Lautsprecher an
   `J904`, Finger an `J813` Pin 1 → muss brummen.
6. Dann Etappe 4, die Oszillatoren.

### Vorgemerkt für Etappe 4 — die 5-Volt-Falle

Nachtrag 06.11.2026. Auf der **Filterplatine** gibt es kein 5-V-Netz und nur
einen Chip, Überspannung ist dort also kein Thema. Auf dem **Oszillator** schon.

| Chip | Versorgungspins | Grenze |
|---|---|---|
| `U101` TL074 (DIP-14, Fassung) | Pin 4 / Pin 11 | ±18 V |
| **`U102` 74LVC2G17** (SOT-23-6) | **Pin 5 = +5 V**, Pin 2 + 3 = Masse | **6,5 V** |
| `U103` TL074 (SOIC-14) | Pin 4 / Pin 11 | ±18 V |
| `U104` OPA1662 (SOIC-8) | **Pin 8 = +12 V, Pin 4 = −12 V** | ±18 V |

Zwei Konsequenzen:

1. **`J110` und `J111` auf dem Oszillator sind vierpolig:** Pin 1 = +12 V,
   Pin 2 = Masse, Pin 3 = −12 V, **Pin 4 = +5 V**. Auf der Hauptplatine ist das
   `J810`, nicht `J811`. Sitzt das Gehäuse um eine Stelle verschoben, liegt
   +12 V auf dem 5-V-Pin, und der 74LVC2G17 ist sofort hin.
   **Darum vor dem ersten Einschalten: `J110` Pin 4 gegen Masse messen. Es
   müssen +5 V sein, nicht +12 V.**
2. **Die Prüfung "Pin 4 gegen Pin 11" gilt nicht für jeden Chip.** Beim
   OPA1662 im SOIC-8 sind es **Pin 4 gegen Pin 8**. Beim 74LVC2G17 ist es
   **Pin 5 gegen Pin 2**. Die Prüftabelle muss pro Chip angepasst werden.

**Geklärt am 06.11.2026 — der Eingang von `U102` ist sicher.**

Der Knoten `Net-(U103C-+)` verbindet `C101.1`, `R101.2`, `R103.1`, `U102.1`
(Eingang des 5-V-Chips) und `U103.10`. Die beiden Zuleitungen:

| Weg | Bauteil | Richtung |
|---|---|---|
| vom Tonhöhe-Poti am Bedienfeld (`/O1_PITCH`, `J112` Pin 6) | **R101 = 10 kΩ** | kann hochziehen |
| zum Kollektor von `Q101` (Emitter an Masse) | **R103 = 220 Ω** | **nur nach Masse** |

Das ist der Relaxationsoszillator: `C101` lädt über R101 auf, der
Schmitt-Trigger kippt, sein Ausgang treibt über `R102` (1 kΩ) die Basis von
`Q101`, und `Q101` entlädt `C101` über R103. Die 220 Ω sind also der
Entladeweg nach Masse und können den Knoten **nie über 5 V heben**.

Der einzige Weg nach oben läuft über **10 kΩ**. Selbst bei volle 12 V dort:

- (12 V − 5,5 V) / 10 kΩ ≈ **0,65 mA**
- schlimmster Fall, +5 V fehlt und ±12 V liegt an: (12 V − 0,5 V) / 10 kΩ ≈ **1,15 mA**

Grenzwert des 74LVC2G17 für den Eingangs-Klemmstrom: **±50 mA**. Also rund ein
Prozent davon. Der Chip überlebt beides.

**Gefährlich bleibt für ihn allein Versorgungspin 5** — also der um eine Stelle
verschobene vierpolige Stecker. Dagegen hilft die Messung oben: `J110` Pin 4
gegen Masse muss +5 V zeigen, nicht +12 V.

---

## 8. Nachtrag zu AUFBAU.md

Der Hinweiskasten in §6 Prüfung 3 ("Der Chip wird ohne Bedienfeld warm – das
ist normal") stimmt als Aussage über die Schaltung, war aber für diese Platine
die falsche Beruhigung. Er gehört ergänzt um einen Satz:

> Warm werden darf er. **Platzen darf er nicht.** Und ob er warm oder heiss
> wird, misst man nicht mit dem Finger, sondern mit einem 1-kΩ-Widerstand in
> der Plusleitung: jedes Volt darüber ist ein Milliampere. Über 4 mA ist ein
> Fehler, egal wie kühl sich der Chip anfühlt.

Das trage ich nach, sobald die Ursache feststeht — dann weiss ich auch, was
genau dort hingehört.
