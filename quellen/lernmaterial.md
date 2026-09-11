# Lernmaterial & Quellen

Sammlung der Materialien, mit denen wir uns die Theorie erarbeitet haben.
Wird laufend ergänzt und dient später als Quellenverzeichnis für die schriftliche Arbeit.

---

## Videos

Hauptquelle ist die Elektronik-Playlist von *The Organic Chemistry Tutor*:
`https://www.youtube.com/playlist?list=PL0o_zxa4K1BV9E-N8tSExU1djL6slnjbL`
Wir arbeiten sie nicht der Reihe nach durch, sondern greifen gezielt die Themen
heraus, die für die einzelnen Baugruppen des Synthesizers gebraucht werden.

### Grundlagen

| Titel | Kanal | Thema | Link |
|---|---|---|---|
| Basic Electronics For Beginners | The Organic Chemistry Tutor | Spannung, Strom, Widerstand, passive Bauteile | https://www.youtube.com/watch?v=uXr4lXYjXuU |
| AC vs DC | The Organic Chemistry Tutor | Gleich- vs. Wechselspannung | https://youtu.be/pWOiOUSQvZc |

### Kondensatoren & Filter → relevant für Filterstufe und Oszillatoren

| Titel | Kanal | Thema | Link |
|---|---|---|---|
| How Do Capacitors Work? | The Organic Chemistry Tutor | Funktionsweise, Kapazität, Ladungsspeicherung | https://www.youtube.com/watch?v=ImpJUHenhTM |
| RC Circuits Physics Problems, Time Constant Explained, Capacitor Charging and Discharging | The Organic Chemistry Tutor | RC-Glied, Zeitkonstante τ = R·C, Lade-/Entladekurve | https://youtu.be/PLQrPqYlPmI |
| Low Pass Filters and High Pass Filters — RC and RL Circuits | The Organic Chemistry Tutor | Tief-/Hochpass, Grenzfrequenz f_g = 1/(2πRC) | https://youtu.be/lagfhNjMuQM |

### Mixer → relevant für die Zusammenführung der drei Oszillatoren

| Titel | Kanal | Thema | Link |
|---|---|---|---|
| Transistor Audio Mixer Circuit | The Organic Chemistry Tutor | Audiosignale über je einen Widerstand pro Kanal summieren, Verstärkung mit Transistorstufe | https://youtu.be/CKaDxZrjaGA |

### Transistoren & Verstärker → relevant für Amplifier und Distortion

| Titel | Kanal | Thema | Link |
|---|---|---|---|
| Transistors Explained — How transistors work | The Engineering Mindset | Aufbau und Funktionsprinzip von BJT/MOSFET | https://youtu.be/J4oO7PT_nzQ |
| Transistor Amplifiers — Class A, AB, B, & C Circuits | The Organic Chemistry Tutor | Verstärkerklassen, Arbeitspunkt, Verzerrung | https://www.youtube.com/watch?v=0e_OUyGCaBs |

---

## Werkzeuge

| Werkzeug | Zweck | Link |
|---|---|---|
| Falstad Circuit Simulator | Schaltungen im Browser simulieren, Kurvenformen sichtbar machen | https://www.falstad.com/circuit/ |
| KiCad | Schaltplan und PCB-Entwurf | https://www.kicad.org |

---

## Zuordnung Theorie → Baugruppe

| Baugruppe | benötigte Theorie | Stand |
|---|---|---|
| Oszillatoren (3×) | RC-Zeitkonstante, Schwingbedingung | **Saw-Oszillator simuliert und funktionsfähig (19.08.)**, Square/Triangle/Sine offen |
| Filter | Tief-/Hochpass, Grenzfrequenz, Flankensteilheit | Passive Filter behandelt, aktive Filter offen |
| Mixer | Summierverstärker, Operationsverstärker oder Transistor | behandelt (19.08.), Bauteilwahl Op-Amp vs. Transistor offen |
| Amplifier | Transistorverstärker, Verstärkerklassen | behandelt |
| Distortion | Übersteuerung, Clipping, Dioden-Clipper | teilweise (über Verstärkerklassen) |
