# Leiterplatten

Aus dem Gesamtschaltplan ([`../SynthesizerFinal/`](../SynthesizerFinal/README.md))
sind **drei** Leiterplatten abgeleitet. Nicht neun: die drei Oszillatoren sind
elektrisch identisch, die vier Filter ebenfalls — es gibt also drei Layouts, von
denen zwei mehrfach bestückt werden.

| Platine | Ordner | Stück | Grösse | Bauteile | Stand |
|---|---|---|---|---|---|
| Oszillator | [`Oszillator/`](Oszillator/) | **3×** | 108,1 × 108,1 mm | 57 | fertig geroutet, DRC sauber |
| Filter | [`Filter/`](Filter/) | **4×** | 80,1 × 68,1 mm | 22 | fertig geroutet, DRC sauber |
| Hauptplatine | [`Hauptplatine/`](Hauptplatine/) | 1× | 96,1 × 98,1 mm | 46 | fertig geroutet, DRC sauber |

Bei allen drei Platinen gilt: **kein DRC-Fehler, kein offenes Netz, Massefläche in
einem zusammenhängenden Stück.** Die Fertigungsdaten in `Fertigung/` sind
vollständig und gehören zu genau diesem Stand.

Filter und Hauptplatine bleiben unter **100 × 100 mm**. Das ist keine
willkürliche Grenze: die meisten günstigen Platinenhersteller haben genau dort
ihre Preisstufe.

Die **Oszillator-Platine ist grösser** — 108,1 × 108,1 mm. Sie trägt 57 Bauteile,
wo die Hauptplatine 46 auf ähnlicher Fläche trägt, und wurde vergrössert, weil
sich zwei Netze partout nicht routen liessen und Platzmangel als Ursache vermutet
wurde.

> **Diese Vermutung war falsch.** Die beiden Netze scheiterten an zwei *selbst
> gesetzten* Sperrflächen, nicht an der Fläche (siehe unten). Ob die Platine
> deshalb auch wieder unter 100 × 100 mm passt, ist **noch nicht nachgeprüft** —
> das steht als offener Punkt im [Tagebuch](../diary/2026-09-16.md). Solange das
> offen ist, gilt die 108-mm-Version: sie ist vollständig geroutet und geprüft.

> **Beim Bestellen beachten:** Mit 108 mm fällt diese eine Platine aus der
> 100-×-100-mm-Preisstufe, und sie wird **dreimal** gebraucht. Wer Geld sparen
> will, prüft vorher den offenen Punkt oben.

## Was wo liegt

| Ordner / Datei | Inhalt |
|---|---|
| `Oszillator/`, `Filter/`, `Hauptplatine/` | je ein vollständiges KiCad-Projekt (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`). Zum Ansehen das `.kicad_pro` öffnen |
| `Fertigung/*.zip` | die Dateien für den Platinenhersteller: Gerber, Bohrdaten, Bohrplan. So hochladen wie sie sind |
| `Stuecklisten/` | eine Stückliste pro Platine |
| [`VERDRAHTUNG.md`](VERDRAHTUNG.md) | **die wichtigste Datei beim Zusammenbau**: welches Kabel von wo nach wo, Draht für Draht |
| [`BEDIENFELD-ERGAENZUNGEN.md`](BEDIENFELD-ERGAENZUNGEN.md) | nachträglich dazugekommen: Oszillator ein/aus, Mixer-Fader, Lautsprecherklemmen statt eingebautem Lautsprecher, Modus-Taster, Arduino-Anschluss |
| `*-bestueckung.pdf` | Bestückungsplan zum Ausdrucken |

## Aufbau der Platinen

Zweilagig, Signale auf der Oberseite, **die ganze Unterseite ist Massefläche**.
Das ist bei Audio die entscheidende Entscheidung: der Rückstrom findet immer den
kürzesten Weg direkt unter seiner Leiterbahn, statt einen Umweg zu suchen und
dabei Störungen einzusammeln.

Leiterbahnen: 0,3 mm für Signale, 0,6 mm für die Versorgung.

### Eine bewusste Ausnahme auf der Oszillator-Platine

Beim Routen galt zusätzlich die selbst gesetzte Regel: **keine Leiterbahn auf der
Rückseite unter einem IC**. Ein Schlitz in der Massefläche zwingt den Rückstrom
zu einem Umweg, und ausgerechnet unter einem IC ist das am unangenehmsten.

Für **ein** Netz — `O1_AINV`, den Summierknoten von `U103` — ist diese Regel
aufgehoben. Ohne sie kam das Netz nicht durch, und zwar nachweislich: mit
Sperrfläche scheitert die Wegsuche auch nach **444 Sekunden**.

Was das kostet, ist nachgemessen und nicht geschätzt:

| | |
|---|---|
| Verlust an Massefläche | **73 mm² von 10 517 mm² = 0,69 %** |
| Massefläche danach | **ein** zusammenhängendes Stück, keine Inseln |
| Betroffenes IC | `U103` — **das IC, zu dem das Netz selbst führt** |

Der Schlitz liegt also unter dem Baustein, an dessen Pin die Leitung ohnehin
ankommt, nicht quer unter einem unbeteiligten IC. Und bei Audiofrequenzen
(≤ 20 kHz) fliesst der Rückstrom ohnehin breit verteilt; eng an der Leiterbahn
klebt er erst weit oberhalb von 1 MHz. Für eine Digitalplatine wäre das ein
Fehler, hier ist es vertretbar.

> Wer dieses Layout später überarbeitet: **den Schlitz nicht „aufräumen"**, ohne
> das Netz neu zu routen — sonst ist die Platine wieder unvollständig.

## Die Bedienelemente sitzen **nicht** auf den Platinen

Potis, Schalter und Buchsen kommen ins Bedienfeld und werden mit Kabeln an die
Platinen gesteckt (JST-XH, 2,5 mm). Das sind 153 Drähte, einer pro Lötfahne.
Alle stehen in [`VERDRAHTUNG.md`](VERDRAHTUNG.md).

> **Die Tabelle in `VERDRAHTUNG.md` genau befolgen.** Die Reihenfolge der Netze
> auf den Steckern ist nicht willkürlich, sondern so gewählt, dass die Leitungen
> den Stecker in derselben Reihenfolge verlassen wie die Bauteile stehen, die sie
> versorgen. Auf der Oszillator-Platine hat das **61 sich kreuzende Leitungspaare
> auf null** gebracht — und jede Kreuzung hätte den Router eine Durchkontaktierung
> oder einen Umweg gekostet, an der engsten Stelle der Platine. Wer die Drähte
> „logisch" umsortiert, macht das wieder kaputt.

## Wie das Layout entstanden ist

Die Platzierung ist **gerechnet, nicht gezeichnet**. Jedes Bauteil steht neben
dem IC-Pin, den es bedient, und seine Koordinaten kommen aus den echten
Pad-Positionen des Footprints. Der Schaltplan und das Layout können deshalb
nicht auseinanderlaufen.

Zwei Fehler hat das gefunden, die kein DRC je gemeldet hätte, weil es keine
Regelverletzungen sind:

- Der **Stützkondensator des LM386 stand 41 mm von seinem Versorgungspin** weg
  und das Zobel-Glied 32 bzw. 46 mm vom Ausgang. Ein LM386 mit so weit entfernter
  Abblockung und Bedämpfung ist ein zuverlässiges Rezept für einen Verstärker,
  der schwingt statt zu verstärken. Jetzt sind es 4,7 mm und 5,0 mm.
- Die **Klinkenbuchsen-Steckerleiste des Oszillators sass auf der linken
  Plattenkante**, obwohl alle drei Signale in die rechte Hälfte gehen — das hat
  `OSC1_OUT` über 98 mm quer über die Platine gezogen.

Die Skripte dazu liegen in [`../Werkzeuge/`](../Werkzeuge/README.md).

## Geprüft gegen die Fertigungsgrenzen von JLCPCB (21.09.2026)

Hersteller: **JLCPCB** (https://jlcpcb.com). Alle drei Platinen wurden mit
[`../Werkzeuge/jlccheck.py`](../Werkzeuge/jlccheck.py) direkt aus den Platinendateien
vermessen und mit der Tabelle unter https://jlcpcb.com/capabilities/pcb-capabilities
verglichen – bei widersprüchlichen Angaben dort jeweils mit dem strengeren Wert.

| Prüfpunkt | JLCPCB min. | Unsere Platinen |
|---|---|---|
| Leiterbahnbreite | 0,127 mm | 0,3 mm |
| Via-Bohrung | 0,3 mm | 0,4 mm |
| Via-Restring | 0,15 mm | 0,2 mm |
| Restring bedrahteter Pads | 0,25 mm (empfohlen) | 0,35 mm |
| Befestigungslöcher (NPTH) | 0,5 mm | 3,2 mm |
| Loch-zu-Loch | 0,45 mm | ≥ 0,85 mm |
| Kupfer zur Platinenkante | 0,2 mm | 0,3 mm |
| Bestückungsdruck: Schrifthöhe / Strichstärke | 1,0 / 0,15 mm | 1,0 / 0,15 mm |
| Bestückungsdruck: Linien | 0,15 mm | 0,15 mm |

**Eine Änderung war nötig:** Die Bauteil-Umrisse aus der KiCad-Standardbibliothek
sind mit 0,12 mm gezeichnet – dünner als die 0,15 mm, die JLCPCB zuverlässig druckt.
[`silkwiden.py`](../Werkzeuge/silkwiden.py) hat alle 2 468 solchen Linien auf 0,15 mm
verbreitert. Nur die Strichstärke hat sich geändert; an Kupfer, Bohrungen und
Bauteilpositionen nichts. Danach erneut geprüft: DRC fehlerfrei, kein offenes Netz,
Masseflächen auf den Quadratmillimeter gleich wie vorher. Der Stand davor liegt im
Archiv (`archiv/<platine>/rev4-pre-jlc/`).

**Einstellungen beim Bestellen** (alles andere auf Standard lassen): Layers 2 ·
PCB Thickness 1,6 mm · Surface Finish **HASL (with lead)** – das bleifreie HASL kostet
1,60 USD pro Platinensorte mehr und bringt beim Handlöten nichts · Stückzahl siehe
unten. Die Schritt-für-Schritt-Anleitung steht in [`../Einkauf/BESTELLEN.md`](../Einkauf/BESTELLEN.md).

## Bestückung: gemischt (JLCPCB + von Hand)

Entschieden am 21.09.2026: **JLCPCB lötet nur die SMD-Chips** – drei auf der
Oszillator-Platine, einer auf der Filter-Platine –, alles andere wird von Hand
bestückt. Diese winzigen Chips sind das Einzige, was sich von Hand schwer löten lässt; alles Übrige ist bedrahtet,
lässt sich leicht tauschen, und die Potis sitzen ohnehin im Bedienfeld.

| Bauteil | Typ | Gehäuse | LCSC-Nr. |
|---|---|---|---|
| U102 | SN74LVC2G17DBVR | SOT-23-6 | C10429 |
| U103 | **TL074CDR** | SOIC-14 | **C12594** |
| U104 | OPA1662AIDR | SOIC-8 | C882794 |
| U401 (Filter) | **TL074CDR** | SOIC-14 | **C12594** |

**Geändert am 22.09.2026: TL074CDR statt OPA4196.** Beide sind Vierfach-Op-Amps mit
derselben Anschlussbelegung im selben Gehäuse; am Layout ändert sich nichts. Der
OPA4196 kostet 3,62 USD, der TL074CDR 0,29 USD – und weil JLCPCB bei 10 Platinen
alle 10 bestücken muss, wären es 20 Stück gewesen. Geprüft:

* Netzliste vorher/nachher: **genau 7 Wertänderungen** (U103, U203, U303, U401–U701),
  keine Netz- und keine Footprint-Änderung; ERC und DRC fehlerfrei.
* Filter (U401): Simulation mit beiden Op-Amp-Modellen über den ganzen Cutoff- und
  Resonanzbereich – Unterschied **unter 0,1 dB**. Der TL074 ist hier sogar schneller
  (3 MHz / 13 V/µs gegenüber 2,5 MHz / 5,5 V/µs).
* Oszillator (U103): Puffer der Sägezahn-Kapazität (Eingang 0…3,4 V, Eingangsstrom
  des TL074 30 pA gegen ≥ 1,6 µA Ladestrom – vernachlässigbar), Drive-,
  Make-up- und Sägezahn-Ausgangsstufe mit Signalen weit unter ±10 V. Die
  Tonhöhe hängt nicht vom Op-Amp ab, sondern von den Schmitt-Trigger-Schwellen.
* Der Wert steht nur auf der Fab-Lage, nicht im Bestückungsdruck – die Gerber-Dateien
  sind dadurch nicht verändert.

**Neu im Gerber-Paket:** die **Lotpasten-Lage** (`F_Paste`) bei Oszillator und
Filter. Ohne sie kann JLCPCB keine Schablone für die SMD-Chips schneiden; die
Hauptplatine hat keine SMD-Teile und braucht keine. Die übrigen Lagen sind
byte-gleich bis auf den Zeitstempel.

Dateien für die Bestellung in `Fertigung/`: je eine `…-BOM-jlcpcb.csv` und
`…-CPL-jlcpcb.csv` für Oszillator und Filter. Bei diesen beiden Platinen
**PCB Assembly** einschalten (Economic, Top Side) und die passenden zwei Dateien
hochladen.

**Stückzahl:** JLCPCB lässt bei 10 Platinen nur „alle 10 bestücken" zu (eine
Teilbestückung gibt es nur bei 5 Stück: 2 von 5). Für 2 Geräte also: Oszillator
**10 Stück, alle bestückt** (6 gebraucht), Filter **10 Stück, alle bestückt**
(8 gebraucht), Hauptplatine **5 Stück, ohne Bestückung** (2 gebraucht). Die
überzähligen bestückten Platinen sind Reserve – die Mehrkosten sind mit dem TL074
nur noch rund 6 USD.

> **In der Vorschau von JLCPCB die Ausrichtung prüfen:** Der Punkt für Pin 1 jedes
> Chips muss auf der Markierung im Bestückungsdruck liegen. JLCPCB zählt die
> Drehung bei manchen Gehäusen anders als KiCad; falls ein Chip verdreht angezeigt
> wird, dort drehen, bevor bestellt wird.

Die Hauptplatine hat keine SMD-Teile – dort **keine** Bestückung wählen.

## Vor dem Bestellen

- [ ] Die Gerber in einem Viewer ansehen (z. B. der kostenlose Online-Viewer des
      Herstellers) — nicht blind hochladen.
- [ ] Stückzahl für 2 Geräte: Oszillator 10, Filter 10, Hauptplatine 5 (siehe oben).
- [ ] Die Oszillator-Platine (108 mm) fällt aus der 100-mm-Preisstufe: 15,30 statt
      5,00 USD für 10 Stück. Sie zu verkleinern hiesse, die dichteste Platine neu zu
      routen – für rund 10 USD bewusst nicht gemacht.
