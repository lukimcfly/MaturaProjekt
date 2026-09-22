# Bedienfeld – Ergänzungen vom 21./22.09.2026

Diese Teile sind **nachträglich** dazugekommen. Sie sitzen alle im Bedienfeld bzw.
neben dem Arduino und ändern **nichts an den Platinen** – die bestellten
Leiterplatten bleiben, wie sie sind. `VERDRAHTUNG.md` wird aus dem Schaltplan
erzeugt und kennt diese Teile deshalb nicht; hier steht, wie sie angeschlossen
werden. Übersichtsbild: `Bilder/Schaltplaene/2026-09-21_bedienfeld-uebersicht.png`.

## 1. Oszillator ein/aus – `SW_05` (je Oszillator)

Kippschalter **EIN-EIN (1 × UM, SPDT)**, gleicher Typ wie die anderen.

Normalerweise geht die Ader von **J_12 Pin 11** (`O1_LVL_W`) an den Schleifer des
Amplituden-Potis `RV_05`. Neu läuft sie über den Schalter:

| Ader / Anschluss | geht an |
|---|---|
| J_12 Pin 11 (`O1_LVL_W`) | **SW_05 Mitte** (statt an RV_05 Lug 2) |
| SW_05 Stellung „ein" | RV_05 **Lug 2** (Schleifer) |
| SW_05 Stellung „aus" | RV_05 **Lug 3** (CCW, Masse – dort liegt schon J_12 Pin 8) |

**Warum so und nicht einfach die Leitung auftrennen:** Dahinter sitzt der Eingang
eines Operationsverstärkers (`U104B`). Offen gelassen würde er Brummen und
Rauschen einfangen. Der Umschalter legt ihn in „aus" sauber auf Masse. Den
Schleifer direkt auf Masse zu schalten wäre falsch: steht das Poti auf Voll, würde
das den Ausgang von `U104A` kurzschliessen.

Mit „aus" ist der Oszillator im Mixer **und** an seiner Buchse „Ausgang" stumm;
er schwingt intern weiter, was nicht stört.

## 2. Mixer als Schieberegler – `RV801`–`RV803`

**Schiebepoti 10 kΩ log**, mono, **60 mm** Schiebeweg (Alpha, Tayda `A-1617`; die
45-mm-Ausführung ist dort ausverkauft). Elektrisch identisch mit den
Drehpotis – die drei Anschlüsse aus `VERDRAHTUNG.md` (Hauptplatine J_12
Pin 1–9) bleiben gleich:

| Poti-Anschluss | Ader |
|---|---|
| Ende, an dem der Regler **oben** steht | „Lug 1 (CW)" – das Signal |
| Schleifer | „Lug 2 (Schleifer)" |
| Ende, an dem der Regler **unten** steht | „Lug 3 (CCW)" – Masse |

So bedeutet **oben = laut**. Welches Ende welches ist, mit dem Multimeter prüfen:
zwischen Schleifer und Masse-Ende muss der Widerstand steigen, wenn man den Regler
nach oben schiebt. Die Front braucht dafür je einen **Schlitz** (ca. 62 × 3 mm)
statt eines Lochs; das Poti wird mit zwei M2- oder M3-Schrauben von hinten
an die Front geschraubt (Gewindelöcher an den Stirnseiten).

Der Master (`RV901`) bleibt ein Drehknopf.

## 3. Lautsprecher: nur noch ein eigener, über Polklemmen

Es gibt **keinen eingebauten Lautsprecher** mehr. Stattdessen zwei
**Lautsprecherklemmen** (Polklemmen, rot und schwarz) – sie nehmen blanken Draht
und 4-mm-Bananenstecker.

| Anschluss | geht an |
|---|---|
| Hauptplatine **J904 Pin 1** (Lautsprecher, schon gleichspannungsfrei hinter `C904`) | Klemme **rot (+)** |
| Hauptplatine **J904 Pin 2** (Masse) | Klemme **schwarz (−)** |

Ein Lautsprecher hat zwar zwei Anschlüsse, aber das ist kein „Ein und Aus" wie bei
Send/Return: der Strom fliesst durch die Schwingspule hin und zurück, beide Adern
gehören an dieselbe Stelle. Deshalb reicht **ein** Klemmenpaar.

* Lautsprecher mit **8 Ω oder mehr**. Ein 4-Ω-Lautsprecher geht bei mässiger
  Lautstärke, bringt den LM386 an 12 V bei voller Lautstärke aber an seine
  Wärmegrenze.
* Die beiden Klemmen **nie direkt verbinden** (Kurzschluss am Ausgang).
* Ohne angeschlossenen Lautsprecher passiert nichts – das Zobel-Glied (`R901`,
  `C905`) hält den LM386 auch ohne Last stabil.

## 4. Modus-Taster für das Oszilloskop

**Taster, Schliesser, tastend.** Ein Anschluss an den **RESET**-Pin des Arduino,
der andere an **GND**. Wirkt genau wie der RESET-Knopf auf dem Arduino, der im
Gehäuse sitzt: jeder Druck schaltet ZEIT → FIGUR → FREI weiter.

## 5. Arduino: Versorgung und Messeingang (schon eingeplant)

* **Strom:** 12 V vom Netzteil-Platinchen an die **Rundbuchse des Arduino**
  (DC-Kabel 5,5/2,1 mm). Der Arduino macht daraus selbst 5 V für sich, das
  Display und die Eingangsstufe. USB ist nur noch zum Programmieren nötig.
* **Gemeinsame Masse:** ist mit der neuen Stromversorgung (Abschnitt 6) automatisch
  gegeben – die Masse des Synthesizers *ist* das Minus des 12-V-Netzteils.
* **Messeingang:** `FILT_B_OUT` (Hauptplatine **J817 Pin 1**) über die
  Eingangsstufe an **A0**: 1 µF → 47 kΩ → Knoten (47 kΩ nach +5 V, 47 kΩ nach
  GND) → 1 kΩ → A0, dazu zwei BAT85 von A0 nach +5 V und nach GND. Teilt durch 3
  und hebt auf 2,5 V: ±7 V → 0,2 … 4,8 V; auch ±11 V schaden nicht.

## Nicht geändert: Distortion weich/hart

Der Schalter `SW_02` bleibt ein Umschalter. Die harte Begrenzung (`D105/D106`)
ist **immer** im Signalweg; `SW_02` schaltet nur die weichen Dioden
(`D103/D104`) in die Gegenkopplung von `U103A` dazu. In „weich" arbeiten also
beide – die weichen runden zuerst ab, die harten kappen danach nur noch die
Spitzen. Eine dritte Stellung „beide" gäbe es elektrisch nicht.

## 6. Stromversorgung (neu am 22.09.2026, sparsame Variante)

Statt des TRACO-Doppelwandlers (±12 V, rund CHF 25 pro Stück) kommt **+12 V direkt
vom Netzteil**, und nur **−12 V** macht ein kleiner isolierter Wandler
**B1212S-2WR3** (12 V → 12 V, 2 W, rund 1 USD). Weil sein Ausgang galvanisch getrennt
ist, darf man seinen **Plus-Ausgang an Masse** legen – dann liegt sein 0-V-Ausgang
12 V *unter* Masse. Die Hauptplatine merkt davon nichts: an `J990` kommen wie
vorher +12 V, Masse und −12 V an, und ihre Sicherungen, Verpolschutzdioden und
Siebelkos bleiben im Einsatz.

Netzteil-Platinchen (Lochraster 50 × 70 mm):

| von | nach |
|---|---|
| DC-Einbaubuchse **Mitte (+12 V)** | rückstellende Sicherung RXEF110 → **Netzschalter** → Knoten „+12 V" |
| DC-Einbaubuchse **Aussen (Minus)** | Knoten „Masse" |
| Knoten „+12 V" | `J990` **Pin 1**, DC-Kabel zum Arduino **Mitte**, Wandler **Vin** |
| Knoten „Masse" | `J990` **Pin 2**, DC-Kabel zum Arduino **Aussen**, Wandler **GND** (Eingang) **und** Wandler **+Vo** |
| Wandler **0V** (Ausgang) | `J990` **Pin 3** (= −12 V) |
| 22 µF / 25 V | zwischen Wandler **Vin** (+) und **GND** (−), direkt an den Pins |

Anschlüsse des Wandlers (SIP-4, Punkt = Pin 1, bei Mornsun-Bauart): **1 = GND,
2 = Vin, 3 = 0V, 4 = +Vo**. Vor dem Einlöten mit dem Datenblatt des gelieferten
Teils vergleichen – Nachbauten anderer Hersteller halten sich meist daran, aber
nicht immer.

Warum das reicht:

* **Strombedarf:** −12 V versorgt nur die Operationsverstärker, rund 65 mA
  (höchstens ~110 mA laut Datenblatt-Maximalwerten). Der Wandler liefert 167 mA.
* **+12 V** trägt zusätzlich den LM386 – bei voller Lautstärke bis ~0,3 A. Das kommt
  jetzt direkt aus dem 1-A-Netzteil statt durch einen 250-mA-Wandler, hat also
  mehr Reserve als vorher.
* **Gesamt** mit Arduino und Display: ca. 0,5 A. Das Netzteil (Mean Well
  NGE12E12-P1J) liefert 1 A.
* **Keinen** zusätzlichen Elko an den Wandler-Ausgang hängen: auf der −12-V-Schiene
  liegen schon rund 170 µF (Hauptplatine + alle Platinen), das ist nahe an dem, was
  so ein kleiner Wandler beim Einschalten laden mag.

## 7. Tonhöhe und Cutoff: Potis mit Kennlinie **C**

Die Tandempotis `RV_01/RV_02` hängen als veränderlicher Widerstand zwischen
**Lug 1 (CW-Ende)** und Schleifer (siehe `VERDRAHTUNG.md`, Ende „CW" wie beim Mixer).
Nach rechts drehen macht den Widerstand kleiner und den Ton höher. Die Frequenz geht
mit 1/R – für gleich breite Oktaven muss R also *exponentiell* abnehmen, und genau
das tut nur ein **C-Poti** (umgekehrt logarithmisch) zwischen Schleifer und
CW-Ende.

Mit 1 MΩ und dem festen Vorwiderstand (Umfang 48 Hz … 4,9 kHz):

| Poti | Ton bei halbem Drehweg | Aufteilung |
|---|---|---|
| linear (B) | ~95 Hz | 1 Oktave auf der ersten Hälfte, 5,7 auf der zweiten |
| logarithmisch (A) | ~54 Hz | noch schlechter – fast alles am rechten Anschlag |
| **umgekehrt log. (C)** | **~440 Hz** | **3,2 Oktaven links, 3,5 rechts** |

**Welcher Anschluss das CW-Ende ist, mit dem Multimeter prüfen:** zwischen Schleifer
und diesem Anschluss muss der Widerstand **kleiner** werden, wenn man nach rechts
dreht – und bei einem C-Poti in der ersten Hälfte des Drehwegs schnell, in der
zweiten langsam. Das gilt für beide Ebenen des Tandempotis.

Die Einkaufsliste vom 21.09. schlug hier noch **A** vor – das war für diese
Verdrahtung falsch und ist korrigiert. Für die Filter-Cutoffs (`RV_01/RV_02` der
Filter, 100 kΩ) gilt dasselbe.

## 8. Frontplatte und Display

* **Dicke höchstens ca. 3 mm.** Die Klinkenbuchsen PJ-301BM haben nur ein kurzes
  Gewinde, die Potis 6,5 mm. Eine dickere Holzfront an diesen Stellen von hinten
  aussenken, bis nur noch 2–3 mm übrig sind.
* **Display:** Tayda führt das 2,2"-Display nicht, nur das **2,8"** mit demselben
  Chip ILI9341 und derselben Auflösung – der Oszilloskop-Sketch läuft unverändert,
  die Anschlüsse sind gleich (die Touch-Pins bleiben frei). Der Ausschnitt in der
  Front ist entsprechend grösser. Gerät 1 kann das vorhandene 2,2"-Display behalten.
* **Knöpfe:** alle mit Madenschraube für 6,35-mm-Achsen; sie halten auch auf den
  6-mm-Achsen der 1-MΩ-Tandempotis.
