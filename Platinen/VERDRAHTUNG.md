# Synthesizer - Aufbau und Verdrahtung

Abgeleitet aus `SynthesizerFinal.kicad_sch` Rev 4.0. Jede Zeile stammt aus der
exportierten Netzliste, nicht aus dem Gedaechtnis.

## 1. Die drei Platinen

| Platine | Projekt | Stueck | Bauteile auf der Platine |
|---|---|---|---|
| Oszillator | `boards/osc/` | **3x** | 57 |
| Filter | `boards/filter/` | **4x** | 22 |
| Hauptplatine | `boards/main/` | **1x** | 46 |

Die drei Oszillatoren sind elektrisch identisch, ebenso die vier Filter.
Darum gibt es nur **drei Layouts**. Im Gesamtschaltplan heissen sie 1xx / 2xx / 3xx
(Oszillatoren) und 4xx / 5xx / 6xx / 7xx (Filter A bis D); auf der einzelnen
Platine stehen immer die Nummern der ersten Gruppe, also R101, U103, J_12 usw.

## 2. Kabel zwischen den Platinen

| Von | Nach | Pins | Signal |
|---|---|---|---|
| Hauptplatine J810 | Oszillator 1  J_10 | 4 | +12 V / GND / -12 V / +5 V |
| Oszillator 1 J_11 | Oszillator 2  J_10 | 4 | Versorgung durchgeschleift |
| Oszillator 2 J_11 | Oszillator 3  J_10 | 4 | Versorgung durchgeschleift |
| Hauptplatine J811 | Filter A  J_10 | 3 | +12 V / GND / -12 V |
| Filter A J_11 | Filter B  J_10 | 3 | Versorgung durchgeschleift |
| Filter B J_11 | Filter C  J_10 | 3 | Versorgung durchgeschleift |
| Filter C J_11 | Filter D  J_10 | 3 | Versorgung durchgeschleift |
| Oszillator 1 J_15 | Hauptplatine J813 | 2 | OSC1_OUT |
| Oszillator 2 J_15 | Hauptplatine J814 | 2 | OSC2_OUT |
| Oszillator 3 J_15 | Hauptplatine J815 | 2 | OSC3_OUT |
| Hauptplatine J816 | Filter A  J_13 | 2 | MIX_OUT, Mixer in Filter A |
| Filter A J_14 | Filter B  J_13 | 2 | FILT_A_OUT |
| Filter B J_14 | Hauptplatine J817 | 2 | FILT_B_OUT, Filter B in den LM386 |
| Filter C J_13 / J_14 | Klinkenbuchsen J_01 / J_02 | 2 | Solo-Filter 1 |
| Filter D J_13 / J_14 | Klinkenbuchsen J_01 / J_02 | 2 | Solo-Filter 2 |

Alle Steckverbinder sind **JST-XH 2,50 mm**, vertikal, gerade. Die Polzahl
unterscheidet sich je Funktion, damit sich Versorgung und Audio nicht
vertauschen lassen.

## 3. Verdrahtung Platine zum Bedienfeld

Eine Ader pro Loetfahne. Die Tabellen gelten fuer **jede** Platine dieses Typs.

### Oszillator-Platine (3x gleich)

**J_10** - Versorgung ein (4-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | +12V | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |
| 3 | -12V | Nachbarplatine |
| 4 | +5V | Nachbarplatine |

**J_11** - Versorgung weiter (4-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | +12V | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |
| 3 | -12V | Nachbarplatine |
| 4 | +5V | Nachbarplatine |

**J_12** - Panel Potis (11-polig)

| Pin | Netz | Loetfahne | Bedienelement |
|---|---|---|---|
| 1 | O1_CLIP | **RV_04** Lug 1 | Distortion-Pegel |
| 2 | O1_MKUP_A | **RV_04** Lug 2 (Schleifer) | Distortion-Pegel |
| 3 | O1_AINV | **RV_03** Lug 1 | Drive |
| 4 | O1_DRIVE | **RV_03** Lug 2 (Schleifer) | Drive |
| 5 | +5V | **RV_01** Lug 1 | Tonhoehe (Ebene B) |
| 6 | O1_PITCH | **RV_01** Lug 2 (Schleifer) | Tonhoehe (Ebene B) |
| 7 | O1_FGF_A | **RV_02** Lug 1 | Tonhoehe (Ebene A) |
| 8 | GNDREF | **RV_05** Lug 3 (CCW) | Amplitude |
| 9 | O1_FGF_B | **RV_02** Lug 2 (Schleifer) | Tonhoehe (Ebene A) |
| 10 | O1_LVL_A | **RV_05** Lug 1 (CW) | Amplitude |
| 11 | O1_LVL_W | **RV_05** Lug 2 (Schleifer) | Amplitude |

**J_13** - Panel Schalter (14-polig)

| Pin | Netz | Loetfahne | Bedienelement |
|---|---|---|---|
| 1 | O1_SOFT | **SW_02** Pin 2 (Mitte/Common) | weich / hart |
| 2 | OSC1_DIST | **SW_03** Pin 2 (Mitte/Common) | Distortion ein/aus |
| 3 | O1_WSEL | **SW_01** Common (Schleifer) | Wellenform |
| 4 | OSC1_WAVE | **SW_03** Pin 3 (Stellung B) | Distortion ein/aus |
| 5 | O1_AINV | **SW_02** Pin 1 (Stellung A) | weich / hart |
| 6 | O1_MKUP | **SW_03** Pin 1 (Stellung A) | Distortion ein/aus |
| 7 | O1_DRIVE | **SW_02** Pin 3 (Stellung B) | weich / hart |
| 8 | OSC1_SAW | **SW_01** Pos 4 | Wellenform |
| 9 | OSC1_SQ | **SW_01** Pos 3 | Wellenform |
| 10 | OSC1_TRI | **SW_01** Pos 2 | Wellenform |
| 11 | OSC1_DIST | **SW_04** Pin 2 (Mitte/Common) | Solo-Filter ein/aus |
| 12 | OSC1_SIG | **SW_04** Pin 3 (Stellung B) | Solo-Filter ein/aus |
| 13 | OSC1_SINE | **SW_01** Pos 1 | Wellenform |
| 14 | O1_SEND | **SW_04** Pin 1 (Stellung A) | Solo-Filter ein/aus |

**J_14** - Panel Buchsen (6-polig)

| Pin | Netz | Loetfahne | Bedienelement |
|---|---|---|---|
| 1 | O1_SEND | **J_01** Tip (Signal) | Filter-Send |
| 2 | GNDREF | **J_01** Sleeve (Masse) | Filter-Send |
| 3 | OSC1_SIG | **J_02** Tip (Signal) | Filter-Return |
| 4 | GNDREF | **J_02** Sleeve (Masse) | Filter-Return |
| 5 | OSC1_OUT | **J_03** Tip (Signal) | Ausgang |
| 6 | GNDREF | **J_03** Sleeve (Masse) | Ausgang |

**J_15** - Audio aus -> Mixer (2-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | OSC1_OUT | Hauptplatine J813/J814/J815 Pin 1 |
| 2 | GNDREF | Hauptplatine, Masse |

Fuer Oszillator 2 und 3 gilt dieselbe Tabelle.

### Filter-Platine (4x gleich)

**J_10** - Versorgung ein (3-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | +12V | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |
| 3 | -12V | Nachbarplatine |

**J_11** - Versorgung weiter (3-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | +12V | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |
| 3 | -12V | Nachbarplatine |

**J_12** - Panel Poti + Wahlschalter (12-polig)

| Pin | Netz | Loetfahne | Bedienelement |
|---|---|---|---|
| 1 | F4_HP | **RV_01** Lug 1 | Cutoff (Ebene A) |
| 2 | F4_T1W | **RV_01** Lug 2 (Schleifer) | Cutoff (Ebene A) |
| 3 | F4_BP | **RV_02** Lug 1 | Cutoff (Ebene B) |
| 4 | F4_T2W | **RV_02** Lug 2 (Schleifer) | Cutoff (Ebene B) |
| 5 | F4_BP | **RV_03** Lug 1 | Resonanz |
| 6 | F4_RESW | **RV_03** Lug 2 (Schleifer) | Resonanz |
| 7 | F4_LP | **SW_01** Pos 1 | Filterwahl |
| 8 | F4_HP | **SW_01** Pos 2 | Filterwahl |
| 9 | F4_BP | **SW_01** Pos 3 | Filterwahl |
| 10 | F4_NOTCH | **SW_01** Pos 4 | Filterwahl |
| 11 | MIX_OUT | **SW_01** Pos 5 | Filterwahl |
| 12 | FILT_A_OUT | **SW_01** Common (Schleifer) | Filterwahl |

**J_13** - Audio ein (2-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | MIX_OUT | Hauptplatine J816 |
| 2 | GNDREF | Masse |

**J_14** - Audio aus (2-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | FILT_A_OUT | Filter B J_13 |
| 2 | GNDREF | Masse |

Bei Filter A und B gehen J_13 / J_14 an die Nachbarplatinen, bei Filter C und D an die Klinkenbuchsen.

### Hauptplatine (1x)

**J_10** - Versorgung -> Oszillatoren (4-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | +12V | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |
| 3 | -12V | Nachbarplatine |
| 4 | +5V | Nachbarplatine |

**J_11** - Versorgung -> Filter (3-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | +12V | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |
| 3 | -12V | Nachbarplatine |

**J_12** - Panel Potis (12-polig)

| Pin | Netz | Loetfahne | Bedienelement |
|---|---|---|---|
| 1 | M_LVL1_A | **RV_01** Lug 1 (CW) | Kanal 1 Pegel |
| 2 | M_LVL1_W | **RV_01** Lug 2 (Schleifer) | Kanal 1 Pegel |
| 3 | GNDREF | **RV_01** Lug 3 (CCW) | Kanal 1 Pegel |
| 4 | M_LVL2_A | **RV_02** Lug 1 (CW) | Kanal 2 Pegel |
| 5 | M_LVL2_W | **RV_02** Lug 2 (Schleifer) | Kanal 2 Pegel |
| 6 | GNDREF | **RV_02** Lug 3 (CCW) | Kanal 2 Pegel |
| 7 | M_LVL3_A | **RV_03** Lug 1 (CW) | Kanal 3 Pegel |
| 8 | M_LVL3_W | **RV_03** Lug 2 (Schleifer) | Kanal 3 Pegel |
| 9 | GNDREF | **RV_03** Lug 3 (CCW) | Kanal 3 Pegel |
| 10 | M_VOL_A | **RV_01** Lug 1 (CW) | Master-Lautstaerke |
| 11 | M_VOL_W | **RV_01** Lug 2 (Schleifer) | Master-Lautstaerke |
| 12 | GNDREF | **RV_01** Lug 3 (CCW) | Master-Lautstaerke |

**J_13** - OSC 1 ein (2-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | OSC1_OUT | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |

**J_14** - OSC 2 ein (2-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | OSC2_OUT | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |

**J_15** - OSC 3 ein (2-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | OSC3_OUT | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |

**J_16** - -> Filter A (2-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | MIX_OUT | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |

**J_17** - Filter B -> (2-polig)

| Pin | Netz | Kabel geht an |
|---|---|---|
| 1 | FILT_B_OUT | Nachbarplatine |
| 2 | GNDREF | Nachbarplatine |

## 4. Bedienelemente - Einkaufsliste Frontplatte

| Anzahl | Bauteil | Wert / Typ | Funktion |
|---|---|---|---|
| 3 | Doppel-Potentiometer | 1M linear, 2-fach-Gleichlauf | Tonhoehe je Oszillator (RV_01 + RV_02) |
| 3 | Potentiometer | 100k linear | Drive (RV_03) |
| 3 | Potentiometer | 100k logarithmisch | Distortion-Pegel (RV_04) |
| 3 | Potentiometer | 10k logarithmisch | Amplitude (RV_05) |
| 3 | Drehschalter | 1-polig, 4 Stellungen | Wellenform (SW_01) |
| 9 | Kippschalter | SPDT, ein-ein | weich/hart, Distortion, Solo-Filter |
| 4 | Doppel-Potentiometer | 100k linear, 2-fach-Gleichlauf | Filter-Cutoff (RV_01 + RV_02) |
| 4 | Potentiometer | 47k linear | Filter-Resonanz (RV_03) |
| 4 | Drehschalter | 1-polig, 5 Stellungen | Filterwahl (SW_01) |
| 3 | Potentiometer | 10k logarithmisch | Kanalpegel Mixer (RV801/802/803) |
| 1 | Potentiometer | 10k logarithmisch | Master-Lautstaerke (RV901) |
| 13 | Klinkenbuchse 6,3 mm mono |  | 3x Send, 3x Return, 3x Ausgang, 2x Filter-In, 2x Filter-Out |

**Rheostat-Verdrahtung:** RV_01 bis RV_04 im Oszillator und RV_01 bis RV_03 im
Filter haengen nur mit zwei Anschluessen in der Schaltung (Schleifer + ein Ende).
Den **dritten, unbenutzten Aussenanschluss immer mit dem Schleifer verbinden** -
dann bleibt der Widerstand definiert, falls der Schleifer einmal Kontaktprobleme
bekommt, statt die Stufe stumm oder instabil zu machen.

**Wichtig:** RV_01 und RV_02 sind in jedem Oszillator *und* in jedem Filter
**ein einziges Doppelpoti**, nicht zwei getrennte. Im Schaltplan stehen sie als
zwei Symbole, weil die beiden Ebenen an verschiedenen Stellen der Schaltung
haengen. Beim Einkauf also 3 + 4 = 7 Doppelpotis.

## 5. Hinweise zum Bestuecken

| Bauteil | Hinweis |
|---|---|
| Widerstaende **Oszillator-Platine** | stehend montiert, Rastermass 2,54 mm - einen Draht um 180 Grad zurueckbiegen. Nur so passen 27 Widerstaende neben die vier ICs, ohne dass die Leiterbahnen keinen Platz mehr haben. |
| Widerstaende **Filter- und Hauptplatine** | liegend, Rastermass 7,62 mm |
| BC547 und 78L05 | Beine auf 2,54 mm spreizen (TO-92 Inline Wide). Bei 1,27 mm waere der Abstand der Loetaugen kleiner als die Entwurfsregel erlaubt. |
| TL074 und LM386 | Fassung vorgesehen - ICs also nicht direkt einloeten, sondern stecken |
| OPA4196 / OPA1662 / 74LVC2G17 | SMD. OPA4196 im SOIC-14 (1,27 mm Raster) statt TSSOP - deutlich leichter von Hand zu loeten. |
| Masse-Pins an Versorgungssteckern und Abblockkondensatoren | direkt mit der Massflaeche verbunden (kein Thermal). Dafuer den Loetkolben etwas heisser stellen und laenger halten. |
| Sicherungen F901/F902 | 5 x 20 mm Halteclips, je zwei Loetfahnen pro Clip - beide loeten |
| Polung | Elkos und Dioden sind auf dem Bestueckungsdruck markiert; C904 und C805 sind die grossen liegenden Elkos |

