# Analoger Synthesizer – finaler Gesamtschaltplan (Rev. 3)

Ein einziger, **durchgehend verdrahteter** Schaltkreis auf einem flachen
KiCad-9-Blatt (890 × 934 mm). Öffnen mit `SynthesizerFinal.kicad_pro`.

Alle Baugruppen sind mit echten Leitungen verbunden – der Signalweg lässt sich
vom Oszillator bis zum Lautsprecher mit dem Finger verfolgen. Die Netznamen
(`OSC1_TRI`, `MIX_OUT` …) stehen zusätzlich auf den Leitungen, damit man in
Eeschema weiterhin nach ihnen suchen kann.

**Prüfstand:** `kicad-cli 9.0.7`, ERC **0 Fehler, 0 Warnungen**. Die Netzliste
wurde exportiert und die Signalkette Knoten für Knoten nachgeprüft.
274 Bauteile, 228 Netze. Die Verdrahtung wurde gegen die zuvor geprüfte
Version Netz für Netz verglichen und ist elektrisch identisch.

```
OSZ 1 ┐
OSZ 2 ├─► MIXER ─► FILTER A ─► FILTER B ─► LM386 ─► Lautsprecher
OSZ 3 ┘
```

Filter C und D sind eigenständige Solo-Filter mit eigenen Klinkenbuchsen; sie
werden über Send/Return in den Filter-Port eines Oszillators eingeschleift.

---

## 1  Kontrolle deiner Reglerliste

| Regler | Bauteil | Bereich | Status |
|---|---|---|---|
| **Frequenz** je Oszillator | `RV_02` (Ebene A) + `RV_01` (Ebene B), 2-fach-Gleichlauf 1 MΩ | ca. 95 Hz … 9,6 kHz | neu gekoppelt |
| **Amplitude** je Oszillator | `RV_05`, 10 kΩ log | 0 … voll | **neu** |
| **Wellenform** je Oszillator | `SW_01`, 4 Stellungen | Sinus / Dreieck / Rechteck / Sägezahn | war vorhanden |
| **Mixer-Pegel** je Kanal | `RV801/802/803`, 10 kΩ | 0 … voll | war vorhanden |
| **Filter-Cutoff** je Filter | `RV_01`/`RV_02`, 2-fach-Gleichlauf 100 kΩ | 106 Hz … 10,6 kHz | **neu** |
| **Filter-Pegel** je Filter | `RV_03`, 47 kΩ | Verstärkung 1 … 5,7 | war vorhanden |
| **Master-Lautstärke** | `RV901`, 10 kΩ log | 0 … voll | war vorhanden |
| **Distortion** | `SW_03` ein/aus, `SW_02` weich/hart, `RV_03`/`RV_04` Drive | – | war vorhanden |

Der Frequenzknopf ist ein **2-fach-Gleichlaufpoti**: Ebene A stellt den
Funktionsgenerator (Sinus/Dreieck/Rechteck), Ebene B den Sägezahn. Ein Knopf,
beide Bereiche laufen innerhalb ca. 15 % parallel — das war dein ToDo
*„Frequency Regulators kombinieren"*.

---

## 2  Geänderte Werte

Im Original hatten der ganze Filter und grosse Teile des Oszillators **keine
Werte**. Diese Tabelle listet, was gegenüber `KicadCircuit/` anders ist.

### Oszillator (je Einheit, `n` = 1/2/3)

| Neu | Alt | Wert alt → neu | Warum |
|---|---|---|---|
| `RV_01` | `0Ω-25kΩ` | 25 kΩ → **1 MΩ lin** | muss gleich gross sein wie Ebene A, damit ein Gleichlaufpoti funktioniert |
| `R_01` | `RHigh` | 5 kΩ → **10 kΩ** | setzt zusammen mit RV_01 den Sägezahnbereich auf 82 Hz … 8,2 kHz |
| `C_01` | `C4` | 100 nF → **33 nF** | Sägezahnbereich an den Funktionsgenerator angeglichen |
| `R_02` | `RB` | 220 Ω → **1 kΩ** | 4,3 mA Basisstrom reichen; 220 Ω hätten das Gatter überlastet |
| `R_03` | `RLow` | 220 Ω → **220 Ω** | unverändert; Rücklaufzeit 3,3 µs = 2,7 % der Periode |
| `RV_02` | `R6` | 100 kΩ → **1 MΩ lin** | Frequenzpoti, Ebene A |
| `C_02` | `C7` | 33 nF → **6,8 nF** | ergibt zusammen mit RV_02 den Bereich 95 Hz … 9,6 kHz |
| `R_04` | `R8` | 100 kΩ → **47 kΩ** | Hysterese, bestimmt zusammen mit R_05 die Dreieckamplitude |
| `R_05` | `R9` | 22 kΩ → **18 kΩ** | Dreieck 8 Vss (= 2 × Vsat × R_05/R_04) |
| `R_06` | `R10` | 10 kΩ → **10 kΩ** | unverändert, jetzt Vorwiderstand des Frequenzpotis |
| `R_07` | `R13` | 10 kΩ → **10 kΩ** | unverändert |
| `R_08` | `R12` | 100 kΩ → **47 kΩ** | dämpft das Dreieck auf den Bereich, in dem die Dioden runden |
| `R_09` | `R15` | 220 kΩ → **10 kΩ** | Gegenkopplung des Sinus-Formers |
| `R_10` | `R14` | 100 kΩ → **10 kΩ** | Eingangsableitung |
| `C_03` | – | – → **1 µF** | **neu**: trennt den Gleichanteil hinter dem Wellenformschalter |
| `C_04` | – | – → **1 µF** | **neu**: Gleichspannungstrennung des Sägezahns |
| `R_23/24/25` | – | – → **10 k / 68 k / 10 kΩ** | **neu**: hebt den Sägezahn (nur ~1 Vss) auf Pegel |
| `R_26/27` | – | – → **22 k / 10 kΩ** | **neu**: teilt das Rechteck von 21 Vss auf ~6,6 Vss |
| `R_14` | `R16` | – → **10 kΩ** | Eingang weiche Verzerrung |
| `RV_03` | `R1` | – → **100 kΩ** | Drive weich |
| `RV_04` | `R2` | – → **100 kΩ** | Drive hart |
| `R_15` | `R7` | – → **100 kΩ** | Gegenkopplung harte Verzerrung |
| `R_16` | `R17` | – → **2,2 kΩ** | Serienwiderstand vor den Begrenzerdioden |
| `R_17` | – | – → **100 kΩ** | **neu**: hält den Filter-Port definiert, wenn kein Kabel steckt |
| `R_18/19/20` | `R18/R19/R21` | – → **10 kΩ** | Ausgangsstufe, Verstärkung 2 |
| `RV_05` | – | – → **10 kΩ log** | **neu**: Amplitude |
| `R_21` | `R20` | – → **100 Ω** | Kurzschlussschutz am Ausgang |
| `R_22` | `R4` | – → **100 kΩ** | Ableitwiderstand an der Ausgangsbuchse |
| `Q_01` | `Q4` | SPICE-NPN → **BC547** | echtes Bauteil statt Simulationsmodell |
| – | `C6` (1 µF) | **entfällt** | Zeitglied wird nicht mehr gebraucht (siehe 3.4) |
| – | `C8` (10 nF) | **entfällt** | zweiter Integrator ersetzt durch Dioden-Former |
| – | `R11` (100 kΩ) | **entfällt** | Integrator liegt jetzt im Regelkreis |

### Filter (je Modul, `t` = 4/5/6/7)

Alle Werte sind **neu** – im Original war kein einziger gesetzt.

| Bauteil | Wert | Funktion |
|---|---|---|
| `R_01` + `RV_01` | 1 kΩ + 100 kΩ | Tiefpass: Serienwiderstand, Cutoff-Poti Ebene A |
| `C_01` | 15 nF | Tiefpass-Querkondensator → 106 Hz … 10,6 kHz |
| `C_02` | 15 nF | Hochpass-Serienkondensator |
| `RV_02` + `R_02` | 100 kΩ + 1 kΩ | Hochpass: Cutoff-Poti Ebene B → 106 Hz … 10,6 kHz |
| `L_01` / `C_03` | 33 mH / 100 nF | Bandpass, obere Ecke ≈ 5,5 kHz |
| `C_04` / `L_02` | 220 nF / 68 mH | Bandpass, untere Ecke ≈ 650 Hz |
| `C_05` ∥ `L_03` | 680 nF ∥ 33 mH | Bandsperre, Kerbe bei 1,06 kHz |
| `R_03` | 600 Ω | Abschluss der Bandsperre |
| `RV_03` / `R_05` | 47 kΩ / 10 kΩ | Ausgangsverstärker, Verstärkung 1 … 5,7 |

Die LC-Zweige sind auf **600 Ω** Wellenwiderstand ausgelegt – damit bleiben die
Spulen bei 33 / 68 mH und sind als normale Drosseln beschaffbar.

### Mixer und Endstufe

Unverändert gegenüber Rev. 1 (Mixer 1:1 aus deiner Falstad-Simulation,
LM386-Endstufe mit 10 µF Eingangskopplung, 10 k Master-Poti, Verstärkung 200,
Zobel-Glied 10 Ω/47 nF, 220 µF an den Lautsprecher).

---

## 3  Strukturelle Änderungen

### 3.1  Die drei Punkte aus Rev. 1 (erledigt)

1. **Ausgangsbuchse entdreht.** `J_03` führt jetzt das Signal am *Tip*, der
   *Sleeve* liegt auf Masse.
2. **Gegenkopplung des Filterverstärkers korrigiert.** `RV_03` geht jetzt vom
   Ausgang auf den **−**-Eingang (vorher auf den +-Eingang = Mitkopplung).
3. **Oszillatorkern und Ausgangsstufe verbunden.** Das lose `power:AC`-Symbol
   ist weg; die Kette läuft durchgehend
   Kern → Wellenformwahl → Distortion → Filter-Port → Ausgangsstufe.

### 3.2  Dioden aus dem Filter-Signalweg (von dir freigegeben)

`D1`–`D5` lagen **in Serie** im Signalweg und hätten das Audiosignal
gleichgerichtet statt gefiltert. Sie sind entfallen. Damit die vier Zweige sich
nicht gegenseitig belasten, schaltet jetzt ein **2-poliger Drehschalter**
(`SW_01` Ebene A am Eingang, `SW_02` Ebene B am Ausgang) jeden Zweig beidseitig
frei. Stellung 5 = Bypass.

Dasselbe Diodenmuster (`D5`/`D6`) lag am Filter-Port des Oszillators und ist
ebenfalls entfallen.

### 3.3  Pufferstufen im Filter (von dir freigegeben)

Jeder Filter hat jetzt einen **Eingangspuffer** (`U_01B`) und den
**Ausgangsverstärker** (`U_01A`) – beide Hälften des ohnehin vorhandenen
ADA4625-2. Ohne den Puffer würden die beiden Filter im Hauptweg sich
gegenseitig verstimmen und der Mixer bräche unter der Last ein.

> Das ersetzt deine Notiz *„first one without amplifier"*: mit passiven
> LC-Zweigen braucht jeder Filter zwingend eine niederohmige Quelle und einen
> hochohmigen Abschluss.

### 3.4  Oszillatorkern neu aufgebaut

Das war der grösste Eingriff und er liess sich nicht über Werte lösen. Im
Original schwang `U1A` eigenständig, `U1B` und `U1C` integrierten nur nach. Die
Ausgangsamplitude eines Integrators ist ∝ 1/f – bei 95 Hz hätte das Dreieck
über 300 V gewollt und hart geclippt, bei 9 kHz wären 3 V übrig geblieben.

Jetzt bilden **Komparator `U_01A` und Integrator `U_01B` einen Regelkreis**
(Standard-Funktionsgenerator): die Dreieckamplitude ist über den ganzen
Frequenzbereich konstant und hängt nur vom Verhältnis `R_05/R_04` ab.

Der Sinus entsteht nicht mehr durch zweite Integration, sondern durch einen
**Dioden-Former** (`D_01`/`D_02` runden die Dreieckspitzen) mit
Nachverstärkung – ebenfalls frequenzunabhängig.

### 3.5  +5 V für die Schmitt-Trigger

`U_02` (74LVC2G17) ist ein **1,65 … 5,5 V**-Baustein. In Rev. 1 hing er an
+12 V, und der Sägezahn lud seinen Eingang direkt aus +12 V – beides hätte ihn
zerstört. Neu erzeugt ein **78L05** (`U990`) eine +5 V-Schiene für die drei
Gatter und die Sägezahn-Ladung.

### 3.6  Pegelabgleich der Wellenformen

Nach dem Umbau liegen alle vier Kurven in derselben Grössenordnung:

| Wellenform | Amplitude |
|---|---|
| Rechteck (nach Teiler `R_26/27`) | ≈ 6,6 Vss |
| Dreieck | ≈ 8 Vss |
| Sinus | ≈ 7 Vss |
| Sägezahn (nach `U_03D`) | ≈ 6,8 Vss |

Ohne den Teiler hätte das Rechteck mit 21 Vss die Ausgangsstufe (Verstärkung 2)
in die Begrenzung getrieben. Der Sägezahn läuft durch die invertierende
Verstärkung als **fallende** Rampe – im Fourier-Spektrum identisch.

### 3.7  Durchgehende Verdrahtung (Rev. 3)

In Rev. 2 lagen die Baugruppen noch als getrennte Inseln nebeneinander und
waren nur über Netznamen verbunden. Jetzt ist alles ausgezeichnet:

* Die Blöcke sind in Signalrichtung angeordnet – jeder hat seine Eingänge
  links und die Ausgänge rechts.
* Innerhalb eines Oszillators laufen Sägezahn-, Rechteck-, Dreieck- und
  Sinuszweig als vier Leitungen in den Wellenformschalter zusammen.
* Die Dreieck-Rückführung des Funktionsgenerators ist blockintern um den
  Verstärker herum gezeichnet.
* Die drei Oszillatorausgänge laufen rechts hinunter in den Mixer, dessen
  Ausgang unterhalb der Oszillatoren nach links zu Filter A führt.
* Für den Wellenformschalter musste die Schaltrichtung gedreht werden
  (Eingänge links, gemeinsamer Kontakt rechts).

Nicht als Leitung gezeichnet sind bewusst nur zwei Dinge:

* **Versorgung und Masse** bleiben Spannungssymbole (+12 V, −12 V, +5 V, GND).
  112 Masseverbindungen als Leitungen würden den Plan unlesbar machen; das ist
  in jedem Schaltplan so gelöst.
* **Die Solo-Filter C und D** hängen an Klinkenbuchsen – sie werden ja per
  Kabel eingeschleift und sind im Gerät tatsächlich nicht fest verdrahtet.

### 3.8  Kleinere Änderungen

* `SW_02` (weich/hart) war ein DPDT, von dem nur eine Ebene gebraucht wird →
  jetzt ein SPDT wie `SW_03`/`SW_04`.
* Der Filter-Port hat jetzt **zwei** Buchsen (`J_01` Send, `J_02` Return); mit
  einer 2-poligen Klinkenbuchse ist ein Insert nicht sauber machbar.
* Filterkondensatoren sind **ungepolt** (Folie) statt Elko – im Signalweg liegt
  keine Gleichspannung an. Dasselbe gilt für die beiden Koppelkondensatoren
  `C_03` und `C_04` im Oszillator.
* Alle Bezeichner sind blockweise neu vergeben (Oszillatoren 1xx/2xx/3xx,
  Filter 4xx–7xx, Mixer 8xx, Endstufe/Versorgung 9xx).

---

## 4  Versorgung

Symmetrisch **±12 V** an `J990` (Pin 1 = +12 V, Pin 2 = GND, Pin 3 = −12 V),
daraus **+5 V** über `U990`. Alle Operationsverstärker an ±12 V, die
BC547-Mixerstufe und der LM386 an +12 V/GND, die Schmitt-Trigger an +5 V.
Die Versorgungs-Einheiten aller 16 ICs liegen gesammelt im Block
*„Stromversorgung der Operationsverstärker"*.

---

## 5  Was du noch prüfen solltest

* **Spulen 33 mH / 68 mH** sind bei den Filtern die teuersten und
  toleranzbehaftetsten Teile (oft ±10 %). Die angegebenen Eckfrequenzen
  verschieben sich entsprechend.
* Der **Gleichlauf** der Frequenzpotis stimmt auf ca. 15 % – exakt ist er
  nicht, weil Sägezahn und Funktionsgenerator unterschiedliche Zeitgesetze
  haben. Für einen Knopf pro Oszillator reicht es; feiner ginge nur mit zwei
  getrennten Reglern.
* Die **Sinusqualität** des Dioden-Formers liegt bei ca. 3–5 % Klirrfaktor.
  Für die Fourier-Analyse ist das gut sichtbar (schwache ungerade Oberwellen)
  und ehrlicher als ein idealer Sinus.
* Ein paar **Beschriftungen** stehen dicht beieinander; in Eeschema lassen sie
  sich mit einem Klick verschieben, ohne dass sich etwas am Netz ändert.

---

## 6  Dateien

| Datei | Inhalt |
|---|---|
| `SynthesizerFinal.kicad_pro` / `.kicad_sch` | das Projekt |
| `SynthesizerFinal.pdf` | Ausdruck des Schaltplans |
| `BOM.csv` | Stückliste, 57 Positionen |
| `erc.txt` | ERC-Bericht (0 Fehler, 0 Warnungen) |
