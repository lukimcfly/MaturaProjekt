# Bestellen – Schritt für Schritt (Stand 22.09.2026)

Alles für **2 Geräte**, inklusive Reserve, Versand und MWST: **rund CHF 378**
(CHF 189 pro Gerät). Die alte Liste lag bei CHF 850 – und da waren die Platinen,
der Versand und der Zoll noch nicht einmal dabei.

| # | Shop | Was | Warenkorb | Versand | Total ca. |
|---|---|---|---|---|---|
| 1 | **JLCPCB** (China) | 3 Platinensorten, SMD-Chips bestückt | **Login nötig** – siehe unten | DHL DDP ~35 USD | ~108 USD ≈ CHF 91 |
| 2 | **LCSC** (China) | JST-Stecker (original), DC/DC-Wandler, LM386, Sicherungen, SMD-Reserve | **fertig** im Browser | 17.52 USD | 64.01 USD ≈ CHF 54 |
| 3 | **Tayda** (Thailand) | alle übrigen Bauteile, Potis, Schalter, Buchsen, Knöpfe, Arduino, Display, Bolzen, Crimpzange | **fertig** im Browser | DHL Express **DDP** 21.23 USD | 222.55 USD ≈ CHF 188 |
| 4 | **Conrad** (CH) | 2 × Netzteil Mean Well, Litze 100 m | **fertig** im Browser | CHF 9.95 | CHF 45.60 |

Genaue Liste mit jeder Position: `Einkaufsliste_Synthesizer.xlsx`. Falls ein
Warenkorb verloren geht: `warenkorb-tayda.csv`, `warenkorb-lcsc.csv` und
`warenkorb-conrad.csv` enthalten genau den Inhalt (Import siehe unten).

> **Zeitplan:** In China sind vom **25.09. bis 07.10.** Feiertage. JLCPCB schliesst
> die Fabrik am 25.09., 27.09. und 1.–4.10.; LCSC arbeitet eingeschränkt.
> **JLCPCB und LCSC möglichst bis 24.09. bestellen**, sonst kommen die Platinen
> erst Mitte Oktober.

---

## 1. JLCPCB – Platinen (braucht ein Konto)

Die Bestückung lässt sich erst nach dem Login hochladen, deshalb liegt hier kein
fertiger Warenkorb. **Am einfachsten:** im Browser-Fenster von Claude bei JLCPCB
einloggen und Claude Bescheid geben – dann lädt Claude alle Dateien hoch und
stellt alles ein (ca. 10 Minuten). Oder selbst so:

Für **jede** der drei Platinen auf https://cart.jlcpcb.com/quote :

1. **Add gerber file** → Datei aus `Platinen/Fertigung/`:
   `oszillator-gerber.zip`, `filter-gerber.zip`, `hauptplatine-gerber.zip`.
2. Einstellungen – alles andere auf Standard lassen:

   | | Oszillator | Filter | Hauptplatine |
   |---|---|---|---|
   | Layers | 2 | 2 | 2 |
   | PCB Qty | **10** | **10** | **5** |
   | PCB Thickness | 1.6 mm | 1.6 mm | 1.6 mm |
   | Surface Finish | HASL (with lead) | HASL (with lead) | HASL (with lead) |
   | PCB Assembly | **an** | **an** | aus |

3. Bei Oszillator und Filter unter **PCB Assembly**: PCBA Type **Economic**,
   Assembly Side **Top Side**, PCBA Qty **10** (bei 10 Platinen gibt es nur
   „alle"). **NEXT**.
4. BOM und CPL hochladen: `oszillator-BOM-jlcpcb.csv` + `oszillator-CPL-jlcpcb.csv`
   bzw. `filter-BOM-jlcpcb.csv` + `filter-CPL-jlcpcb.csv`.
5. Teile-Liste prüfen: es müssen genau diese sein – sonst nichts ankreuzen:

   | Platine | Bauteil | LCSC-Nr. |
   |---|---|---|
   | Oszillator | U102 SN74LVC2G17DBVR | C10429 |
   | Oszillator | U103 TL074CDR | C12594 |
   | Oszillator | U104 OPA1662AIDR | C882794 |
   | Filter | U401 TL074CDR | C12594 |

6. **Bestückungs-Vorschau – wichtig:** Bei jedem Chip muss der **Punkt für Pin 1**
   auf der Pin-1-Markierung im Bestückungsdruck liegen. Liegt ein Chip verdreht,
   dort mit dem Drehen-Knopf korrigieren (meist 90° oder 180°). Ein verdrehter Chip
   geht beim ersten Einschalten kaputt.
7. Die Geschäftsbedingungen der Bestückung bestätigen, **Save to Cart**.
8. Hauptplatine: nur Gerber hochladen, Qty 5, **Save to Cart**.
9. Kasse: Versand **DHL Express (DDP)** – da sind MWST und Gebühren schon dabei.

Kosten (Schätzung, der echte Preis steht nach dem Hochladen im Warenkorb):
Platinen 24.30 USD, Bestückung ~48.50 USD, Versand ~35 USD.

## 2. LCSC – Stecker und Sonderteile

Warenkorb ist fertig (24 Positionen, 46.67 USD Ware). Kasse:

* Mit Konto oder als Gast (LCSC legt beim Bezahlen mit PayPal automatisch ein Konto an).
* Versand **Global Direct Standard Line** (17.52 USD, 7–15 Werktage). Warenwert
  inkl. Versand liegt unter CHF 62 → keine Schweizer MWST, keine Zollgebühr.
* Falls der Warenkorb leer ist: https://www.lcsc.com/bom → `warenkorb-lcsc.csv`
  hochladen, oder im Warenkorb unten „LCSC#/MPN" Zeile für Zeile.
* Wer Versand sparen will, kann die LCSC-Bestellung mit JLCPCB zusammen schicken
  lassen („Combine with JLCPCB order") – geht aber nur mit demselben Konto und
  verlangt eine besondere Lieferadresse. Für ~15 USD lohnt der Aufwand kaum.

## 3. Tayda – fast alles Übrige

Warenkorb ist fertig (66 Positionen, 1270 Teile, 2,36 kg, 201.32 USD Ware).

* **Versandart: „DHL Express DDP Shipping" (21.23 USD) wählen**, nicht das
  „DHL Express 1.00 USD". Beim billigen muss man bei der Lieferung MWST (~CHF 14)
  plus eine DHL-Gebühr (~CHF 15–20) nachzahlen; DDP enthält alles.
* Tayda bittet, sich vor dem Befüllen einzuloggen, weil Gast-Warenkörbe verloren
  gehen können. Falls er leer ist: Warenkorb → **Import** → `warenkorb-tayda.csv`
  („Add to current cart"). Die Datei hat genau das Format, das Tayda verlangt.

## 4. Conrad – Netzteile und Litze

Warenkorb ist fertig: 2 × Mean Well NGE12E12-P1J (Bestell-Nr. 3164222) und
1 × Litzensortiment 0,14 mm², 10 Farben à 10 m (2620403). Als **Privatkunde**
bestellen. Wer in der Nähe einer Conrad-Filiale ist, spart mit Abholung die
CHF 9.95 Versand.

---

## Was sich gegenüber der Liste vom 21.09. geändert hat

| Änderung | spart (2 Geräte) |
|---|---|
| Bauteile bei Tayda/LCSC statt Distrelec/Musikding (gleiche Hersteller: Alpha-Potis, Royal-Ohm-Widerstände, original JST) | ~CHF 350 |
| Vierfach-Op-Amp **TL074CDR statt OPA4196** (gleiche Anschlüsse, Simulation deckungsgleich) | ~CHF 55 |
| −12 V aus einem 1-USD-Wandler statt TRACO ±12 V; +12 V direkt vom Netzteil | ~CHF 45 |
| Messing-Abstandsbolzen direkt ins Holz statt Einschraubmuffen + Bolzen | ~CHF 45 |
| Crimpzange SN-28B bei Tayda statt Galaxus | ~CHF 25 |
| Litze: ein 100-m-Set statt 8 Einzelrollen | ~CHF 25 |

Dazu zwei Korrekturen, die mit Sparen nichts zu tun haben:

* **Tonhöhe- und Cutoff-Potis mit Kennlinie C** statt A – mit der Verdrahtung auf
  dem Bedienfeld wäre A schlechter als linear gewesen
  (`Platinen/BEDIENFELD-ERGAENZUNGEN.md`, Abschnitt 7).
* Die Gerber-Dateien von Oszillator und Filter enthalten jetzt die
  **Lotpasten-Lage** – ohne sie hätte JLCPCB keine Schablone für die Bestückung
  schneiden können.

Nicht verändert, obwohl möglich: die Oszillator-Platine auf 100 × 100 mm
verkleinern (spart ~10 USD, müsste aber neu geroutet werden) und die SMD-Chips
selbst löten (spart ~40 USD, aber der SOT-23-6-Chip mit 0,95 mm Raster ist von Hand
heikel).

## Vor dem Bezahlen kurz prüfen

- [ ] Lötzinn und Entlötlitze vorhanden? Sonst bei Conrad dazu (nicht im Warenkorb).
- [ ] Frontplatte: höchstens ~3 mm dick an den Buchsen (sonst von hinten aussenken).
- [ ] Gerät 1 behält das vorhandene 2,2"-Display und den vorhandenen Arduino; für
      Gerät 2 kommt ein 2,8"-Display (gleicher Chip, grösserer Ausschnitt).
