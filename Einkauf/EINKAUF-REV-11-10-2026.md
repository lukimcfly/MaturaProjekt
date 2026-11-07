# Einkauf neu gerechnet – 1 Gerät, Lieferung in einer Woche

**Stand 11.10.2026** · Lieferadresse 5210 Windisch · Ziel: **≤ CHF 400**, da **bis ~18.10.**

Die Liste vom 22.09. galt für 2 Geräte, ohne Termindruck. Beides hat sich geändert,
und zwei Dinge daran sind nicht nur eine Rechenaufgabe.

---

## 1. Was sich allein durch „1 Gerät" ändert

Der Bedarf ist aus derselben Stückliste gerechnet wie vorher, also kann er nicht
von der Schaltung abweichen: **88 Positionen, 808 Teile** für ein Gerät.

| | 2 Geräte (22.09.) | 1 Gerät |
|---|---|---|
| Tayda, Ware | 202.67 USD | **74.87 USD** |
| LCSC, Ware | 46.47 USD | **12.65 USD** |
| Conrad, Ware | 35.65 CHF | **9.85 CHF** |

Zwei Posten fallen ganz weg: **Arduino und Display**. Beide sind vorhanden, und für
ein Gerät braucht es keinen zweiten. Damit entfällt auch das 2,8"-Display – das
vorhandene 2,2" bleibt, der Frontausschnitt wird kleiner als geplant.

Weniger als die Hälfte wird es trotzdem nicht: Widerstände gehen nur in Zehnerschritten,
LCSC hat Mindestmengen (Crimpkontakte erst ab 1000), und Versand und Werkzeug halbieren
sich nicht.

---

## 2. Der Termin schliesst die Bestückung aus

**Bestätigt:** JLCPCB braucht für Economic PCBA rund 5–7 Tage Fertigung, dazu 3–5 Tage
DHL. Das sind ~2 Wochen. JLCPCBs eigener Hinweis zu den Feiertagen (25.09.–07.10., also
vor vier Tagen zu Ende) warnt ausdrücklich davor, dass es direkt danach **länger** dauert
als sonst, und empfiehlt 3–5 Werktage Vorlauf.

**Unbestückte Platinen** sind etwa 2–3 Tage Fertigung plus Versand und passen in die Woche.

Entscheidung (deine): unbestückt, SMD selbst löten. Das heisst pro Gerät von Hand:

| Anzahl | Chip | Gehäuse | Raster | Einschätzung |
|---|---|---|---|---|
| 6 | TL074CDR | SOIC-14 | 1,27 mm | machbar |
| 3 | OPA1662AIDR | SOIC-8 | 1,27 mm | machbar |
| 3 | SN74LVC2G17DBVR | SOT-23-6 | **0,95 mm** | heikel |

Dafür braucht es Flussmittel und eine feine Spitze. Reserve einplanen – die SOT-23-6
sind die, bei denen der erste Versuch misslingt.

---

## 3. Drei Lücken: „nur Europa" geht nicht

Das ist der eigentliche Fund. Ich habe heute in den Shops nachgesehen, nicht geschätzt.

### 3.1 Das 1-MΩ-Tandempoti mit Kennlinie C gibt es in Europa nicht

Das ist die **Tonhöhe**, 3 Stück, ein Knopf pro Oszillator für beide Ebenen
(Sägezahn *und* Funktionsgenerator, siehe `VERDRAHTUNG.md`).

| Shop | 1 MΩ Stereo C |
|---|---|
| Musikding | nicht im Katalog; 1 MΩ Stereo lin/log **nicht verfügbar** |
| Reichelt CH | Stereo endet bei 470 kΩ, **keine** C-Kennlinie |
| Thonk (UK) | nur 9 mm vertikal, falsche Bauform |
| Tubetown | 1 MΩ Stereo **log**, 2,80 € – falsche Kennlinie |
| Tayda | **A-8590, 0.99 USD** |

Warum C zwingend ist, steht in `BEDIENFELD-ERGAENZUNGEN.md` Abschnitt 7: bei halbem
Drehweg ergibt C ~440 Hz (3,2 Oktaven links, 3,5 rechts), linear ~95 Hz, log ~54 Hz.
Mit 100 kΩ statt 1 MΩ müssten die Zeitkondensatoren zehnmal grösser werden und passen
dann nicht mehr in die Footprints.

Das **100-kΩ-Tandem C** (Filter-Cutoff, 4 Stück) gibt es bei Musikding für 2,85 €
– aber auch bei Tayda für 0.80 USD.

### 3.2 Zwei SMD-Chips führt Reichelt nicht

`OPA1662` → 0 Treffer. `SN74LVC2G17` → 0 Treffer. Beide sind Pflicht.
Bleiben Mouser/Digikey (teurer, aber schnell) oder LCSC.

### 3.3 Das JST-XH-System führt Reichelt nicht

Gebraucht werden Stiftleisten `B2/3/4/6/11/12/14B-XH-A` **gerade, durchgesteckt** –
so sind die Footprints gezeichnet –, dazu Gehäuse und **245 Crimpkontakte**.
Reichelt hat genau 3 Treffer, alle **SMD, gewinkelt**, in 3/4/6-polig. Keine
Crimpkontakte. Unbrauchbar.

---

## 4. Was das kostet

Beide Wege brauchen eine Tayda-Sendung (Punkt 3.1) und eine JLCPCB-Sendung.

### Weg A – wie im September, nur mit Express

| Shop | Ware | Versand | Total |
|---|---|---|---|
| Tayda (TH) | ~110 USD inkl. Zange, Rundung | DHL Express DDP 21.23 USD | ~CHF 110 |
| LCSC (CN) | ~35 USD | DHL Express ~30 USD | ~CHF 55 |
| Conrad (CH) | 26 CHF | 9.95 CHF | CHF 36 |
| JLCPCB | 3 Platinen unbestückt | DHL | ~CHF 50 |
| | | | **~CHF 251** |

### Weg B – Europa, wo Europa liefert

| Shop | Ware | Versand | Total |
|---|---|---|---|
| Reichelt CH | ~215 CHF | ~25 CHF | ~CHF 240 |
| Mouser/Digikey CH | SMD-Chips + JST ~73 CHF | ~20 CHF | ~CHF 93 |
| Tayda (TH) | 7 Tandempotis, 6.17 USD | DHL Express DDP 21.23 USD | ~CHF 23 |
| JLCPCB | 3 Platinen unbestückt | DHL | ~CHF 50 |
| | | | **~CHF 406** |

**Weg B kostet rund CHF 155 mehr** und liegt damit genau auf der Grenze – und das mit
Schätzpreisen, die um ±15 % danebenliegen können. Die Gewissheit, für die der Aufpreis
gedacht war, ist ausserdem nur teilweise zu haben: die Tonhöhepotis kommen in beiden
Fällen aus Thailand.

Verlässlich geprüft (heute, live im Shop): Reichelt CH rechnet in CHF **inkl. 8,1 % MWST**
und liefert in **3–4 Werktagen** – das ist der stärkste Punkt für Weg B. Musikding
nennt 3–7 Werktage Bearbeitung, was für die Woche knapp wäre.

---

## 5. Preise, die ich heute bestätigt habe

| Teil | Shop | Preis | Lager |
|---|---|---|---|
| Alpha Poti 16 mm mono (Achse **6,3 mm rund**, 8 mm) | Musikding | 1,10 € / ab 5 St. 1,00 € | ja |
| Alpha Poti 16 mm **Stereo 100k rev log** | Musikding | 2,85 € | ja |
| Drehschalter 1×12 gekapselt | Musikding | 1,90 € | ja |
| Kippschalter SPDT 1× UM | Musikding | 0,80 € | ja |
| Klinkenbuchse 3,5 mm mono | Musikding | 0,25 € | ja |
| Schiebeknopf | Musikding | 0,60 € | rot/grün |
| ALPS RS60112-LOG10K Fader, 60 mm Weg | Reichelt CH | CHF 2.68 | ab 13.10. |

Achtung bei den Knöpfen: die Musikding-Knöpfe für 0,50 € sind **Steckknöpfe für
6-mm-Zahnachsen**. Die Alpha-Potis dort haben eine **runde 6,3-mm-Achse** – dafür
braucht es Knöpfe mit Madenschraube. Poti und Knopf müssen zusammenpassen.

---

## 6. Offen

- Reichelt-Einzelpreise für Passive, Knöpfe, Buchsen, Netzteil, Zange, Bolzen
  (geschätzt, nicht geprüft)
- Mouser/Digikey: Preise nicht lesbar, die Seite blockt automatisierte Zugriffe
- JLCPCB: echter Preis für 3× unbestückt erst nach dem Hochladen
- `LM386N-4` bei Reichelt? (N-1 reicht nur bis 12 V, wir brauchen 18 V)
- DC/DC-Wandler `B1212S-2WR3`: in Europa evtl. nur als Traco zu CHF 20+ statt 1.26 USD
