# Maturaprojekt — Analoger Synthesizer

Physisches Produkt: analoger Synthesizer mit 3 Oszillatoren, Mixer, Amplifier
und Distortion. Dazu eine Fourier-Analyse von analogem und digitalem Ton sowie
die schriftlichen Abgabedokumente.

**Abgabetermin: 10. November 2026**
**Zwischenziel: physisches Produkt fertig bis zu den Herbstferien**

## Stand (22.09.2026)

**Alles bestellbereit.** Schaltplan, drei Platinen und Einkauf sind fertig; die
Warenkörbe bei Tayda, LCSC und Conrad sind gefüllt, JLCPCB braucht noch den Login.

| | |
|---|---|
| Gesamtschaltplan | ERC-sauber: 0 Fehler, 0 Warnungen |
| Oszillator-Platine (**3×** pro Gerät) | DRC-sauber, 0 offene Netze |
| Filter-Platine (**4×** pro Gerät) | DRC-sauber, 0 offene Netze |
| Hauptplatine (1×) | DRC-sauber, 0 offene Netze |
| Fertigungsdaten | vollständig in [`Platinen/Fertigung/`](Platinen/Fertigung/), inkl. Bestückung der SMD-Chips |
| Einkauf für 2 Geräte | **rund CHF 378** inkl. Platinen, Versand und MWST – [`Einkauf/BESTELLEN.md`](Einkauf/BESTELLEN.md) |

Nächster Schritt: bestellen, möglichst bis 24.09. (danach chinesische Feiertage).
Was sich am 22.09. geändert hat, steht im [Tagebuch vom 22.09.](diary/2026-09-22.md).

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
| [`Einkauf/`](Einkauf/BESTELLEN.md) | Einkaufsliste (Excel), Bestellanleitung, Sicherungskopien der Warenkörbe |
| [`Werkzeuge/`](Werkzeuge/README.md) | Die Skripte, mit denen Schaltplan und Platinen erzeugt wurden |
| `KicadCircuit/` | Ursprüngliche Einzelschaltpläne (Vorstufe, nur noch als Vergleich) |

## Arbeitsregel

Der Arbeitsprozess wird **immer direkt nach dem Arbeiten** dokumentiert.
