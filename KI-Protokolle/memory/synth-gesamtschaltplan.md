---
name: synth-gesamtschaltplan
description: "Aufbau, Designentscheidungen und offene Punkte des finalen Synthesizer-Schaltplans in SynthesizerFinal/."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1fea6b0a-24cf-402c-9ea6-93644efb6f1b
  modified: 2026-09-09T18:18:12.575Z
---

Der finale Gesamtschaltplan liegt in `MaturaProjekt/SynthesizerFinal/` als **ein
flaches Blatt** (834 × 825 mm, KiCad 9, Rev. 2). ERC sauber (0/0), Netzliste
knotenweise geprüft. Ausgangsmaterial: `KicadCircuit/Oscillator1.kicad_sch`,
`KicadCircuit/Filter.kicad_sch`, Mixer aus einer Falstad-Simulation.

Kette: 3 Oszillatoren → Mixer → Filter A → Filter B → LM386 → Lautsprecher.
Filter C/D sind Solo-Module mit eigenen Buchsen (Send/Return am Filter-Port).

Vom Benutzer freigegebene Entscheidungen (Stand 2026-09-09):

- Versorgung **±12 V**, daraus **+5 V** (78L05) für die 74LVC2G17-Gatter.
- Filter: Dioden raus, **2-poliger Drehschalter** (Ebene A Eingang, Ebene B
  Ausgang), Ein-/Ausgangspuffer, LC-Zweige auf **600 Ω** ausgelegt.
- „Filterstärke" = **Grenzfrequenz** (Cutoff-Poti auf Tief-/Hochpass).
- Frequenz + Amplitude je Oszillator nachgerüstet, Frequenz über ein
  **2-fach-Gleichlaufpoti** (Ebene A Funktionsgenerator, Ebene B Sägezahn).

**Der Oszillatorkern wurde neu aufgebaut** — das liess sich nicht über Werte
lösen: im Original schwang U1A eigenständig und U1B/U1C integrierten nur nach,
wodurch die Amplitude ∝ 1/f war (Dreieck clippt unten, verschwindet oben).
Jetzt bilden Komparator und Integrator einen Regelkreis; der Sinus entsteht
über einen Dioden-Former statt durch zweite Integration.

Erzeugt wird der Plan von Python-Skripten im Scratchpad (`assemble2.py`,
`osc.py`, `flt.py`, `blocks.py`, `parts.py`, `kilib.py`, `sexpr.py`) — die sind
nicht im Projektordner und beim nächsten Mal weg; der `.kicad_sch` ist die
Quelle der Wahrheit.

Zwei Fallstricke beim programmatischen Erzeugen von KiCad-Dateien, die viel Zeit
gekostet haben: Unit-Untersymbole in `lib_symbols` dürfen **kein** `Lib:`-Präfix
tragen, und KiCad verbindet nur an **Leitungsenden** — Leitungen müssen an
Verbindungspunkten *und* an Bauteil-Pins aufgetrennt werden.

Siehe [[matura-projekt-inhalt]] und [[matura-diary-workflow]].
