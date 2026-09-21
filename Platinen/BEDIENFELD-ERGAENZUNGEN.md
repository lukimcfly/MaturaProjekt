# Bedienfeld – Ergänzungen vom 21.09.2026

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

**Schiebepoti 10 kΩ log**, mono, 45 mm Schiebeweg. Elektrisch identisch mit den
Drehpotis – die drei Anschlüsse aus `VERDRAHTUNG.md` (Hauptplatine J_12
Pin 1–9) bleiben gleich:

| Poti-Anschluss | Ader |
|---|---|
| Ende, an dem der Regler **oben** steht | „Lug 1 (CW)" – das Signal |
| Schleifer | „Lug 2 (Schleifer)" |
| Ende, an dem der Regler **unten** steht | „Lug 3 (CCW)" – Masse |

So bedeutet **oben = laut**. Welches Ende welches ist, mit dem Multimeter prüfen:
zwischen Schleifer und Masse-Ende muss der Widerstand steigen, wenn man den Regler
nach oben schiebt. Die Front braucht dafür je einen **Schlitz** statt eines Lochs.

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
* **Gemeinsame Masse:** 0 V des TRACO-Wandlers mit dem Minus des 12-V-Netzteils
  verbinden – sonst misst der Arduino ohne Bezug.
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
