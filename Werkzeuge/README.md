# Werkzeuge

Die Python-Skripte, mit denen der Schaltplan bearbeitet und die drei Platinen
erzeugt wurden. Sie liegen hier, damit das Ergebnis **nachvollziehbar und
wiederholbar** ist — jede Platine lässt sich aus dem Schaltplan neu erzeugen,
statt von Hand nachgezeichnet werden zu müssen.

Ausgeführt werden sie mit dem Python, das bei KiCad dabei ist:
`C:\Program Files\KiCad\10.0\bin\python.exe` (Version 3.11, enthält `pcbnew`).

```
"C:\Program Files\KiCad\10.0\bin\python.exe" tools/buildall.py osc filter main
```

> **Achtung:** Einige Skripte in diesem Ordner sind **Einmal-Skripte**
> (`addsafety.py`, `adddecoup.py`, `addconn.py`, `footprints.py` und ähnliche).
> Sie erledigen ihre Arbeit **beim Importieren**, nicht erst beim Aufruf — wer
> sie nur „mal kurz importiert", um zu schauen ob sie noch laufen, verändert
> damit den Schaltplan. Nicht reihenweise importieren.

## Die wichtigsten

| Datei | Aufgabe |
|---|---|
| `buildall.py` | Einstiegspunkt: baut eine Platine aus ihrer Platzierung, routet sie und gibt den Prüfbericht aus |
| `pinplace.py` | Die Platzierungsregel: ein Bauteil steht neben dem IC-Pin, den es bedient — die Koordinaten werden aus den echten Pad-Positionen **berechnet**, nicht eingetippt |
| `place_osc.py`, `place_filter.py`, `place_main.py` | Der Aufbau je Platine: welches Bauteil zu welchem IC gehört, auf welcher Seite, wie weit aussen |
| `router.py` | Der Autorouter: A\* auf einem 0,25-mm-Raster über (x, y, Lage), mit Kosten fürs Abbiegen, für Durchkontaktierungen und fürs Fahren auf der Rückseite |
| `routeboard.py` | Masse-Vias, Sperrflächen, Reihenfolge (Versorgung zuerst), Aufreissen-und-neu-Routen, Massefläche |
| `reorderconn.py` | Vertauscht die Netze auf den Stiften eines Steckers — damit die Leitungen den Stecker in derselben Reihenfolge verlassen wie die Bauteile stehen, die sie versorgen |
| `crtyd.py` | Prüft die Platzierung gegen die echten Courtyards der Footprints, **bevor** gebaut wird |
| `checkpcb.py` | Der Prüfbericht: DRC, Massefläche, Platinengrösse, Bestückungsdruck, Verknüpfung Footprint↔Symbol |
| `fabout.py` | Gerber, Bohrdateien und ZIP für den Platinenhersteller |
| `sexp.py`, `geom.py`, `schedit.py` | Grundlage: KiCad-Dateien lesen, Verbindungen geometrisch bestimmen, Symbole ändern |

## Ordnernamen

Die Skripte arbeiten mit dem Arbeitsverzeichnis, in dem sie entstanden sind, und
erwarten dort `boards/osc/`, `boards/filter/` und `boards/main/`. In diesem
Repository liegen dieselben Projekte unter deutschen Ordnernamen:

| Skript erwartet | liegt hier unter |
|---|---|
| `boards/osc/osc.*` | `Platinen/Oszillator/osc.*` |
| `boards/filter/filter.*` | `Platinen/Filter/filter.*` |
| `boards/main/main.*` | `Platinen/Hauptplatine/main.*` |

Die Dateinamen bleiben absichtlich englisch — sie gehören zusammen
(`.kicad_pro`, `.kicad_sch`, `.kicad_pcb` müssen denselben Namen tragen) und
werden von den Skripten so referenziert.

`HANDOFF.md` (englisch) beschreibt den vollständigen Stand, was geprüft wurde
und welche Fallstricke Zeit gekostet haben.
