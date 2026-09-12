# Leiterplatten

Aus dem Gesamtschaltplan ([`../SynthesizerFinal/`](../SynthesizerFinal/README.md))
sind **drei** Leiterplatten abgeleitet. Nicht neun: die drei Oszillatoren sind
elektrisch identisch, die vier Filter ebenfalls — es gibt also drei Layouts, von
denen zwei mehrfach bestückt werden.

| Platine | Ordner | Stück | Grösse | Bauteile |
|---|---|---|---|---|
| Oszillator | [`Oszillator/`](Oszillator/) | **3×** | 108 × 108 mm | 57 |
| Filter | [`Filter/`](Filter/) | **4×** | 80,1 × 68,1 mm | 22 |
| Hauptplatine | [`Hauptplatine/`](Hauptplatine/) | 1× | 96,1 × 98,1 mm | 46 |

Filter und Hauptplatine bleiben unter **100 × 100 mm**. Das ist keine
willkürliche Grenze: die meisten günstigen Platinenhersteller haben genau dort
ihre Preisstufe.

Die **Oszillator-Platine ist bewusst grösser**. Sie trägt 57 Bauteile, wo die
Hauptplatine 46 auf derselben Fläche trägt. Beide Platinen, die sich problemlos
routen lassen, liegen bei rund 205 mm² pro Bauteil — bei 99,5 mm im Quadrat lag
der Oszillator bei 173 und liess sich nicht vollständig verdrahten. 108 × 108 mm
bringt ihn auf dieselben 205 mm².

> **Beim Bestellen beachten:** Diese eine Platine fällt damit aus der
> 100-×-100-mm-Preisstufe, und sie wird **dreimal** gebraucht. Das war eine
> bewusste Entscheidung: lieber etwas mehr für die Platine zahlen als ein paar
> Netze von Hand mit Drahtbrücken nachverdrahten zu müssen.

## Was wo liegt

| Ordner / Datei | Inhalt |
|---|---|
| `Oszillator/`, `Filter/`, `Hauptplatine/` | je ein vollständiges KiCad-Projekt (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb`). Zum Ansehen das `.kicad_pro` öffnen |
| `Fertigung/*.zip` | die Dateien für den Platinenhersteller: Gerber, Bohrdaten, Bohrplan. So hochladen wie sie sind |
| `Stuecklisten/` | eine Stückliste pro Platine |
| [`VERDRAHTUNG.md`](VERDRAHTUNG.md) | **die wichtigste Datei beim Zusammenbau**: welches Kabel von wo nach wo, Draht für Draht |
| `*-bestueckung.pdf` | Bestückungsplan zum Ausdrucken |

## Aufbau der Platinen

Zweilagig, Signale auf der Oberseite, **die ganze Unterseite ist Massefläche**.
Das ist bei Audio die entscheidende Entscheidung: der Rückstrom findet immer den
kürzesten Weg direkt unter seiner Leiterbahn, statt einen Umweg zu suchen und
dabei Störungen einzusammeln.

Leiterbahnen: 0,3 mm für Signale, 0,6 mm für die Versorgung.

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

## Vor dem Bestellen

- [ ] Die Gerber in einem Viewer ansehen (z. B. der kostenlose Online-Viewer des
      Herstellers) — nicht blind hochladen.
- [ ] Bei der Oszillator- und der Filter-Platine die **Stückzahl** nicht
      vergessen: 3× bzw. 4×.
- [ ] Prüfen, ob der Hersteller die Platinengrösse in der günstigen Stufe
      abrechnet.
