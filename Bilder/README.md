# Bilder

Alle Bilder zum Projekt. Jedes Bild bekommt hier unten eine Zeile im Index —
sonst weiß in zwei Monaten niemand mehr, was auf `IMG_4471.jpg` zu sehen ist.

## Unterordner

| Ordner | Inhalt |
|---|---|
| `Schaltplaene/` | KiCad-Screenshots, Schaltplanausschnitte, PCB-Layouts |
| `Aufbau/` | Fotos von Breadboard-Aufbauten, Bauteilen, Gehäuse |
| `Messungen/` | Oszilloskop-Screenshots, Spektren, Messprotokolle |

## Bild aus der Zwischenablage speichern

Statt von Hand abzuspeichern: Bild kopieren (Snipping Tool, Strg+C in KiCad),
dann im Projektordner in PowerShell:

```
.\Bilder\zwischenablage-speichern.ps1 saw-oszillator-v3
.\Bilder\zwischenablage-speichern.ps1 breadboard-mixer -Ordner Aufbau
```

Das Datum wird automatisch vorangestellt.

## Dateibenennung

`JJJJ-MM-TT_kurzbeschreibung.png`

Beispiele:
- `2026-08-12_oszillator-schmitt-trigger.png`
- `2026-09-05_breadboard-mixer.jpg`
- `2026-09-10_oszi-saegezahn-440hz.png`

Das Datum vorne sortiert die Bilder automatisch chronologisch und lässt sich
direkt dem passenden Tagebucheintrag zuordnen.

---

## Index

| Datei | Datum | Was ist zu sehen |
|---|---|---|
| `Schaltplaene/2026-08-19_saw-oszillator-kicad-v2.png` | 19.08.2026 | KiCad-Schaltplan Sägezahn-Oszillator, aktuelle Revision mit RVar zur Frequenzeinstellung |
| `Schaltplaene/2026-08-19_saw-oszillator-stromfluss.png` | 19.08.2026 | Erklärskizze zum Stromfluss mit Sägezahn-Kurve und Schaltschwellen V_T+ / V_T− |
| `Messungen/2026-08-19_falstad-simulation-saegezahn.mp4` | 19.08.2026 | Bildschirmaufnahme der Falstad-Simulation: Schaltung und Sägezahn-Kurvenform mit Frequenzregelung |
| *(fehlt noch)* `Schaltplaene/2026-08-12_oszillator-schmitt-trigger.png` | 12.08.2026 | erste Revision des Oszillators (RHigh 20 kΩ, RLow/RB 270 Ω) |

---

## Beschreibungen

### 2026-08-19 — Sägezahn-Oszillator, aktuelle Revision (`...kicad-v2.png`)

| Bauteil | Wert | Funktion |
|---|---|---|
| U2A | 74LVC2G17 | Schmitt-Trigger-Buffer, Eingang Pin 1, Ausgang Pin 6 |
| RVar | 0 Ω – 25 kΩ | **einstellbarer Ladewiderstand → bestimmt die Tonhöhe** |
| RHigh | 5 kΩ | fester Anteil des Ladewiderstands, begrenzt die höchste Frequenz |
| C4 | 100 nF | zeitbestimmender Kondensator |
| Q4 | NPN | Entladeschalter, vom Schmitt-Trigger-Ausgang gesteuert |
| RLow | 220 Ω | Entladewiderstand vom Kondensatorknoten zum Kollektor |
| RB | 220 Ω | Basiswiderstand |

**Funktionsprinzip:** C4 lädt sich langsam über RVar + RHigh auf. Bei Erreichen der
oberen Schaltschwelle V_T+ kippt der Schmitt-Trigger-Ausgang auf HIGH, schaltet Q4
durch und entlädt C4 schnell über RLow gegen Masse. Bei V_T− kippt der Ausgang
zurück und der Ladevorgang beginnt von vorn.

Weil der Ladewiderstand (5 – 30 kΩ) rund hundertmal grösser ist als der
Entladewiderstand (220 Ω), dauert das Aufladen sehr viel länger als das Entladen —
genau diese **Asymmetrie erzeugt die Sägezahnform**. Mit RVar lässt sich die
Ladezeit und damit die Frequenz einstellen.

### 2026-08-19 — Erklärskizze Stromfluss (`...stromfluss.png`)

Dieselbe Schaltung mit eingezeichnetem Strompfad und der resultierenden
Sägezahn-Kurve zwischen den beiden Schaltschwellen V_T+ und V_T−. Zeigt anschaulich
den langsamen Anstieg und den steilen Abfall. Bauteilwerte in dieser Skizze noch
aus der ersten Revision (RHigh 20 kΩ, RLow 270 Ω, RB 2,2 kΩ).

### 2026-08-12 — erste Revision (Bilddatei fehlt noch)

Gleiche Topologie, andere Werte: RHigh 20 kΩ, RLow 270 Ω, RB 270 Ω, C4 ohne
festen Wert. Noch ohne einstellbaren Widerstand, also mit fester Frequenz.

### 2026-08-19 — Falstad-Simulation (`Messungen/...saegezahn.mp4`)

Bildschirmaufnahme der laufenden Simulation auf `falstad.com/circuit`. Zu sehen
sind die nachgebaute Schaltung und die erzeugte Sägezahnspannung; über den
einstellbaren Widerstand ändert sich die Frequenz.

**Erster Funktionsnachweis des selbst entworfenen Oszillators.**

Standbilder aus dem Video (Kurvenform, Frequenz an beiden Anschlagpunkten von
RVar) sollten noch als PNG gesichert werden — im schriftlichen Kommentar lässt
sich kein Video abdrucken.

### 2026-09-12 — Leiterplatten-Layouts (`Schaltplaene/2026-09-12_platine-*.png`)

3D-Ansichten der fertig gerouteten Platinen, jeweils Ober- und Unterseite.

| Datei | Inhalt |
|---|---|
| `2026-09-12_platine-hauptplatine-oben.png` | Hauptplatine, Bestückungsseite. Oben die Versorgung (Sicherungen, Verpolschutz, Siebung), in der Mitte der Mixer, unten rechts die LM386-Endstufe |
| `2026-09-12_platine-hauptplatine-unten.png` | Hauptplatine, Rückseite — fast durchgehende Massefläche, nur wenige kurze Leiterbahnen |
| `2026-09-12_platine-filter-oben.png` | Filter-Platine, Bestückungsseite. Die beiden Integratoren spiegeln sich um `U401` |
| `2026-09-12_platine-filter-unten.png` | Filter-Platine, Rückseite |

Warum die Rückseite fast leer ist: auf einer zweilagigen Platine **ist** die
Rückseite die Massefläche. Jede Leiterbahn dort schneidet einen Schlitz hinein,
den der Rückstrom umfliessen muss — deshalb kostet der Router das Fahren auf der
Rückseite extra und benutzt sie nur zum Kreuzen.
