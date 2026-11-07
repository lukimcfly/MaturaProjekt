# Bestellen – Schritt für Schritt (Stand 11.10.2026)

Alles für **1 Gerät**, inklusive Reserve, Versand und MWST: **CHF 247**.

Lieferadresse: **5210 Windisch**. Ziel: alles da bis **~18.10.2026**.

| # | Shop | Was | Warenkorb | Versand | Total |
|---|---|---|---|---|---|
| 1 | **JLCPCB** (CN) | 3 Platinensorten, **unbestückt** | Login nötig – siehe unten | DHL Express DDP ~28 USD | ~43 USD ≈ CHF 36 |
| 2 | **LCSC** (CN) | JST-Stecker, **die 13 SMD-Chips**, DC/DC, LM386, Sicherungen | `warenkorb-lcsc.csv` | **DHL Express** ~30 USD | 73.84 USD ≈ CHF 62 |
| 3 | **Tayda** (TH) | alles Übrige: Potis, Schalter, Buchsen, Knöpfe, Passive, Bolzen, Crimpzange | `warenkorb-tayda.csv` | DHL Express **DDP** 21.23 USD | 134.94 USD ≈ CHF 113 |
| 4 | **Conrad** (CH) | Netzteil, Litze | `warenkorb-conrad.csv` | CHF 9.95 | CHF 35.75 |

Jede Position mit Preis: `Einkaufsliste_Synthesizer.xlsx`.
Hintergrund zur Lieferantenwahl: `EINKAUF-REV-11-10-2026.md`.

> **Reihenfolge:** zuerst JLCPCB (längste Laufzeit), dann LCSC, dann Tayda, dann
> Conrad. Die chinesischen Feiertage (25.09.–07.10.) sind vorbei, aber JLCPCB warnt
> vor Rückstau direkt danach.

> **Der wichtigste Klick:** bei **LCSC nicht** die „Global Direct Standard Line"
> nehmen. Die braucht 7–15 Werktage und kommt zu spät. **DHL Express** wählen,
> auch wenn das ~13 USD mehr kostet.

---

## 1. JLCPCB – Platinen, unbestückt

Kein BOM, kein CPL, keine Bestückungs-Vorschau, keine Pin-1-Prüfung. Nur Gerber
hochladen. Für **jede** der drei Platinen auf https://cart.jlcpcb.com/quote :

1. **Add gerber file** → Datei aus `Platinen/Fertigung/`:
   `oszillator-gerber.zip`, `filter-gerber.zip`, `hauptplatine-gerber.zip`.
2. Einstellungen – alles andere auf Standard lassen:

   | | Oszillator | Filter | Hauptplatine |
   |---|---|---|---|
   | Layers | 2 | 2 | 2 |
   | PCB Qty | **5** | **5** | **5** |
   | PCB Thickness | 1,6 mm | 1,6 mm | 1,6 mm |
   | Surface Finish | HASL (with lead) | HASL (with lead) | HASL (with lead) |
   | PCB Assembly | **aus** | **aus** | **aus** |

3. **Save to Cart**.
4. Kasse: Versand **DHL Express (DDP)** – MWST und Gebühren sind damit bezahlt.

Gebraucht werden 3 Oszillator-, 4 Filter- und 1 Hauptplatine. 5 ist die
Mindestmenge, der Rest ist Reserve.

Schätzung: Oszillator 11 USD (108 × 108 mm, über dem 100-×-100-Sonderangebot),
Filter 2 USD, Hauptplatine 2 USD, Versand 28 USD. Der echte Preis steht nach dem
Hochladen im Warenkorb.

---

## 2. LCSC – Stecker und **alle SMD-Chips**

24 Positionen, 1236 Teile, 43.84 USD Ware.

Neu gegenüber September: weil JLCPCB nicht bestückt, liegen die **SMD-Chips jetzt
hier im Warenkorb**:

| Anzahl | Chip | LCSC-Nr. | gebraucht | Gehäuse |
|---|---|---|---|---|
| 10 | TL074CDR | C12594 | 7 | SOIC-14 |
| 5 | OPA1662AIDR | C882794 | 3 | SOIC-8 |
| 10 | 74LVC2G17 | C10429 | 3 | **SOT-23-6, 0,95 mm** |

Beim 74LVC2G17 ist die Reserve Absicht: 0,95 mm Raster von Hand ist die heikelste
Lötstelle im ganzen Projekt.

* Warenkorb füllen: https://www.lcsc.com/bom → `warenkorb-lcsc.csv` hochladen.
  Falls eine Mindestmenge nicht stimmt, zeigt LCSC das im Warenkorb an – dann die
  Menge dort korrigieren und mir sagen, damit die Liste nachgeführt wird.
* Mit Konto oder als Gast (LCSC legt beim Bezahlen mit PayPal automatisch eins an).
* **Versand: DHL Express.** Siehe Kasten oben.
* Mit ~74 USD Gesamtwert liegt die Sendung über der Schweizer MWST-Grenze – bei
  DHL Express wird das beim Import abgerechnet.

---

## 3. Tayda – fast alles Übrige

64 Positionen, 689 Teile, 113.71 USD Ware.

* **Versandart: „DHL Express DDP Shipping" (21.23 USD) wählen**, nicht das
  „DHL Express 1.00 USD". Beim billigen muss man bei der Lieferung MWST plus eine
  DHL-Gebühr nachzahlen; DDP enthält alles.
* Vor dem Füllen einloggen – Gast-Warenkörbe gehen über Nacht verloren.
  Warenkorb → **Import** → `warenkorb-tayda.csv` („Add to current cart").

**Nicht durch etwas anderes ersetzen:** die drei **Tandempotis 1 MΩ Kennlinie C**
(`A-8590`, Tonhöhe). Ich habe am 11.10. Musikding, Reichelt, Thonk und Tubetown
geprüft – ein 1-MΩ-Doppelpoti mit umgekehrt logarithmischer Kennlinie gibt es in
Europa nicht, und mit linear oder log verteilen sich die Oktaven falsch
(`BEDIENFELD-ERGAENZUNGEN.md`, Abschnitt 7). Tayda ist die einzige Quelle.

---

## 4. Conrad – Netzteil und Litze

1 × Mean Well NGE12E12-P1J (Bestell-Nr. 3164222) und 1 × Litzensortiment
0,14 mm², 10 Farben à 10 m (2620403). Als **Privatkunde** bestellen. Mit Abholung
in einer Filiale spart man die CHF 9.95.

---

## Was sich gegenüber der Liste vom 22.09. geändert hat

| Änderung | Wirkung |
|---|---|
| 1 Gerät statt 2 | Ware fällt auf etwa ein Drittel, nicht auf die Hälfte: Widerstände nur in Zehnerschritten, LCSC-Mindestmengen, Versand und Zange halbieren sich nicht |
| **Arduino und Display fallen weg** | beide vorhanden; damit auch kein 2,8"-Display – das vorhandene 2,2" bleibt, der Frontausschnitt wird kleiner |
| **Platinen unbestückt** | spart ~48 USD Bestückung, kostet 13 SMD-Lötstellen pro Gerät von Hand |
| LCSC auf DHL Express | ~13 USD mehr, dafür 4–6 statt 7–15 Werktage |

## Vor dem Bezahlen kurz prüfen

- [ ] Bei LCSC **DHL Express** gewählt, nicht Standard Line?
- [ ] Bei Tayda **DDP** gewählt, nicht das 1-USD-Express?
- [ ] Bei JLCPCB **PCB Assembly aus** und **Qty 5** bei allen drei?
- [ ] Lieferadresse 5210 Windisch überall gleich?
- [ ] Lötzinn, Entlötlitze und **Flussmittel** vorhanden? Flussmittel ist für die
      SOT-23-6-Chips kein Luxus. Sonst bei Conrad dazu (nicht im Warenkorb).
- [ ] Frontplatte: höchstens ~3 mm dick an den Buchsen (sonst von hinten aussenken).
