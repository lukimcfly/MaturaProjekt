# Maturaprojekt — Analoger Synthesizer

Physisches Produkt: analoger Synthesizer mit 3 Oszillatoren, Mixer, Amplifier
und Distortion. Dazu eine Fourier-Analyse von analogem und digitalem Ton sowie
die schriftlichen Abgabedokumente.

**Abgabetermin: 10. November 2026**
**Zwischenziel: physisches Produkt fertig bis zu den Herbstferien**

## Stand (16.09.2026)

**Schaltplan fertig, alle drei Platinen fertig geroutet — bestellbar.**

| | |
|---|---|
| Gesamtschaltplan | ERC-sauber: 0 Fehler, 0 Warnungen |
| Oszillator-Platine (**3×**) | DRC-sauber, 0 offene Netze |
| Filter-Platine (**4×**) | DRC-sauber, 0 offene Netze |
| Hauptplatine (1×) | DRC-sauber, 0 offene Netze |
| Fertigungsdaten | vollständig in [`Platinen/Fertigung/`](Platinen/Fertigung/) |

Nächster Schritt: Gerber in einem Viewer durchsehen, dann Platinen und Bauteile
bestellen. Details und der eine noch offene Punkt (Grösse der Oszillator-Platine)
stehen in [`Platinen/README.md`](Platinen/README.md) und im
[Tagebuch vom 16.09.](diary/2026-09-16.md).

## Ordnerstruktur

| Ordner | Inhalt |
|---|---|
| [`diary/`](diary/README.md) | Arbeitstagebuch, eine Datei pro Arbeitstag |
| [`plan/`](plan/zeitplan-bis-herbstferien.md) | Zeitpläne |
| [`quellen/`](quellen/lernmaterial.md) | Lernmaterial, später Quellenverzeichnis |
| [`Bilder/`](Bilder/README.md) | Schaltpläne, Aufbaufotos, Messungen |
| [`Schul-Unterlagen/`](Schul-Unterlagen/README.md) | Vorgaben, Kriterien, Formulare von der Schule |
| [`Unsere-Materialien/`](Unsere-Materialien/README.md) | Logbuch und schriftlicher Kommentar zur Abgabe |
| [`SynthesizerFinal/`](SynthesizerFinal/README.md) | Gesamtschaltplan des Synthesizers (KiCad) |
| [`Platinen/`](Platinen/README.md) | Die drei Leiterplatten: Layout, Gerber, Stücklisten, Verdrahtung |
| [`Werkzeuge/`](Werkzeuge/README.md) | Die Skripte, mit denen Schaltplan und Platinen erzeugt wurden |
| `KicadCircuit/` | Ursprüngliche Einzelschaltpläne (Vorstufe, nur noch als Vergleich) |

## Arbeitsregel

Der Arbeitsprozess wird **immer direkt nach dem Arbeiten** dokumentiert.
