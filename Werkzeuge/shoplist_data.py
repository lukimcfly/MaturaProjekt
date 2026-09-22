"""Shopping-list rows for the synthesizer, as JSON for the Excel builder.

Rev. 22.09.2026 - the economical version. Everything is sourced where it is cheapest
without giving up quality: Tayda (Thailand) for the through-hole parts and the whole
panel, LCSC (China) for genuine JST connectors and the few odd parts, Conrad (CH) for
the mains adapters and the wire. The PCBs come from JLCPCB (separate table in the
workbook). Prices are the cart prices of 22.09.2026 in the shop's own currency.

Board parts are counted straight from the master BOM (SynthesizerFinal BOM.csv), so the
list cannot drift from the schematic. Quantities are PER DEVICE; the workbook multiplies
by the device count. Shops sell some parts only in steps (resistors in tens, LCSC
minimum quantities), so CART holds what is really in each cart: the last row that uses
a part number takes up the rounding, and the builder checks that the rows add up to it.
"""
import csv, json, re, sys, math

BOM = 'MaturaProjekt/SynthesizerFinal/BOM.csv'
DEVICES = 2

TAY, LCS, CON = 'Tayda (TH)', 'LCSC (CN)', 'Conrad (CH)'

# ---- what is in the carts (quantity for 2 devices, incl. spares) ----
CART = {
    # Tayda
    'A-2244': 10, 'A-2198': 10, 'A-2245': 20, 'A-2246': 20, 'A-2247': 10, 'A-2621': 10,
    'A-2200': 40, 'A-2341': 20, 'A-2328': 30, 'A-2203': 170, 'A-2182': 10, 'A-2206': 20,
    'A-2207': 10, 'A-2339': 20, 'A-2279': 30, 'A-2191': 20, 'A-2334': 10, 'A-2338': 20,
    'A-2248': 30, 'A-2330': 20,
    'A-704': 9, 'A-702': 27, 'A-563': 11, 'A-707': 6, 'A-620': 3, 'A-703': 3, 'A-566': 5,
    'A-8409': 25, 'A-553': 80, 'A-4534': 40, 'A-4784': 7, 'A-5713': 4, 'A-4541': 8,
    'A-4783': 6, 'A-6355': 4, 'A-157': 50, 'A-484': 6, 'A-137': 13, 'A-176': 4, 'A-1138': 8,
    'A-1317': 7, 'A-857': 3, 'A-1194': 5, 'A-991': 2, 'A-6806': 2, 'A-2854': 1, 'A-8181': 1,
    'A-8590': 7, 'A-4749': 9, 'A-5617': 7, 'A-2401': 7, 'A-4875': 9, 'A-2398': 9,
    'A-1617': 7, 'A-5396': 7, 'A-1893': 15, 'A-3186': 27, 'A-2566': 28, 'A-6751': 59,
    'A-3487': 3, 'A-6484': 3, 'A-6483': 3, 'A-1264': 98, 'A-1250': 100, 'A-5362': 1,
    'A-7409': 1,
    # LCSC
    'C158012': 40, 'C144394': 30, 'C144395': 20, 'C144397': 10, 'C158031': 10, 'C158027': 15,
    'C158022': 10, 'C144401': 50, 'C144402': 40, 'C144403': 20, 'C144405': 20, 'C157889': 10,
    'C157888': 20, 'C157886': 10, 'C140573': 1000, 'C151075': 10, 'C5365309': 3,
    'C12594': 5, 'C882794': 1, 'C10429': 5, 'C194458': 3, 'C142727': 15, 'C3760872': 3,
    'C3312828': 10,
    # Conrad
    '3164222': 2, '2620403': 1,
}


def expand(refs):
    out = []
    for part in refs.split(','):
        m = re.match(r'([A-Z]+)(\d+)-([A-Z]+)?(\d+)$', part)
        if m:
            p, a, _, b = m.groups()
            out += ['%s%d' % (p, i) for i in range(int(a), int(b) + 1)]
        else:
            out.append(part)
    return out


rows = {}
for r in csv.DictReader(open(BOM, encoding='utf-8')):
    rows.setdefault((r['Value'], r['Footprint']), []).extend(expand(r['Reference']))


def count(value, fp_contains=''):
    n, refs = 0, []
    for (v, fp), rr in rows.items():
        if v == value and fp_contains in fp:
            n += len(rr); refs += rr
    return n, refs


def reflist(refs):
    refs = sorted(refs, key=lambda s: (re.sub(r'\d', '', s), int(re.sub(r'\D', '', s))))
    return ', '.join(refs) if len(refs) <= 8 else ', '.join(refs[:6]) + ', … (%d)' % len(refs)


ALL = []          # every row, in order, so shared part numbers can be balanced


def item(part, value, spec, refs, per, supplier, pn, price, cur='USD', note='', extra=None, have=0):
    r = dict(part=part, value=value, spec=spec, refs=refs, per=per, extra=extra, have=have,
             supplier=supplier, pn=pn, price=price, cur=cur, note=note)
    ALL.append(r)
    return r


sheets = {}

# ---------------- board parts (THT, hand-soldered) ----------------
P = []
RES = {'1': 'A-2244', '10': 'A-2198', '100': 'A-2245', '220': 'A-2246', '470': 'A-2247',
       '1k': 'A-2200', '2.2k': 'A-2341', '6.8k': 'A-2328', '10k': 'A-2203', '16k': 'A-2206',
       '20k': 'A-2339', '47k': 'A-2279', '56k': 'A-2191', '68k': 'A-2334', '82k': 'A-2338',
       '100k': 'A-2248', '330k': 'A-2330'}
for v, sku in RES.items():
    n, refs = count(v, 'Resistor')
    P.append(item('Widerstand', v + ' Ω' if not v.endswith('k') else v + 'Ω',
                  'Metallschicht 1 %, 0,25 W, 0207 (Royal Ohm)', reflist(refs), n, TAY, sku, 0.015,
                  note='nur in 10er-Schritten erhältlich'))
FILM = [('56nF', 'A-704', 0.12, '7,2 × 2,5 mm', 'Zeitkondensator Sägezahn - Folie, keine Keramik! (Keramik lag 56 % daneben)'),
        ('15nF', 'A-702', 0.10, '7,2 × 3,5 mm - passt, neben C102/C401/C402 ist 1,7 mm Luft', 'Zeitkondensator Funktionsgenerator + Filter - Folie'),
        ('47nF', 'A-563', 0.065, '7,2 × 2,5 mm', ''),
        ('330nF', 'A-566', 0.14, '7,2 × 3,5 mm (Hauptplatine, viel Platz)', ''),
        ('1uF', 'A-8409', 0.25, '7,2 × 5 mm, 63 V - passt, neben C104 bleibt 1 mm Luft', '')]
for v, sku, pr, dim, note in FILM:
    n, refs = count(v, 'C_Rect')
    P.append(item('Folienkondensator', v.replace('uF', ' µF').replace('nF', ' nF'),
                  'Polyester, RM 5 mm, ' + dim, reflist(refs), n, TAY, sku, pr, note=note))
n, refs = count('100nF', 'C_Disc')
P.append(item('Keramikkondensator', '100 nF', '50 V, Scheibe, RM 5 mm', reflist(refs), n, TAY, 'A-553', 0.01,
              note='nur Abblockkondensatoren an den Versorgungspins - dort reicht Scheibenkeramik'))
ELKO = [('10 µF / 25 V', ['10uF/25V', '10uF/16V'], 'A-4534', 0.02, 'radial 5 × 11 mm, 105 °C', '10 µF/16 V der Hauptplatine durch 25-V-Typ ersetzt'),
        ('47 µF / 25 V', ['47uF/25V'], 'A-5713', 0.02, 'radial 5 × 11 mm, 105 °C', ''),
        ('100 µF / 25 V', ['100uF/25V'], 'A-4541', 0.03, 'radial 6,3 × 11 mm, 105 °C', ''),
        ('470 µF / 25 V', ['470uF/16V', '470uF/25V'], 'A-4783', 0.08, 'radial 10 × 13 mm, RM 5 mm', '470 µF/16 V durch 25-V-Typ ersetzt'),
        ('10 µF bipolar', ['10uF/25V bipolar'], 'A-6355', 0.06, 'bipolar 35 V, 5 × 11 mm', 'liegt auf 0 V Gleichspannung - bipolar nötig')]
for label, vals, sku, pr, spec, note in ELKO:
    n, refs = 0, []
    for v in vals:
        a, b = count(v); n += a; refs += b
    P.append(item('Elektrolytkondensator', label, spec, reflist(refs), n, TAY, sku, pr, note=note))
SEMI = [('Diode', '1N4148', 'DO-35', 'A-157', 0.01, TAY, ''),
        ('Schottky-Diode', '1N5819', 'DO-41', 'A-484', 0.05, TAY, 'Verpolschutz'),
        ('Transistor', 'BC547', 'TO-92 (Beine auf 2,54 mm spreizen)', 'A-137', 0.08, TAY, ''),
        ('Spannungsregler', '78L05', 'TO-92, L78L05ACZ', 'A-176', 0.15, TAY, ''),
        ('Op-Amp', 'TL074', 'DIP-14, TL074CN', 'A-1138', 0.59, TAY, 'gesockelt - Tausch ohne Löten'),
        ('Endstufe', 'LM386', 'DIP-8, LM386N-4/NOPB (TI)', 'C194458', 1.0451, LCS,
         'N-4 (bis 18 V) statt N-1 (nur bis 12 V) - bei Tayda nicht lieferbar, deshalb LCSC')]
for part, v, spec, sku, pr, sup, note in SEMI:
    n, refs = count(v)
    P.append(item(part, v, spec, reflist(refs), n, sup, sku, pr, note=note))
P.append(item('IC-Fassung', 'DIP-14', 'gedreht (Präzision)', 'U101, U201, U301', 3, TAY, 'A-1317', 0.24))
P.append(item('IC-Fassung', 'DIP-8', 'gedreht (Präzision)', 'U901', 1, TAY, 'A-857', 0.12))
P.append(item('Feinsicherung', 'T 500 mA', 'träge, 5 × 20 mm, Littelfuse 0218.500MXP', 'F901, F902', 2, LCS, 'C142727', 0.1559,
              note='Reserve bewusst gross - Sicherungen sind Verbrauchsmaterial'))
P.append(item('Sicherungsclip', '5 × 20 mm', 'Littelfuse 01110501Z (111er-Serie)', 'F901, F902 (je 2 Clips)', 4, LCS, 'C151075', 0.202,
              note='Footprint ist für genau diese Serie gezeichnet'))
sheets['Platine'] = P

# ---------------- connectors and wiring ----------------
V = []
hdr = {}
for (v, fp), rr in rows.items():
    m = re.search(r'B(\d+)B-XH-A', fp)
    if m:
        hdr[int(m.group(1))] = hdr.get(int(m.group(1)), 0) + len(rr)
pins = sum(k * n for k, n in hdr.items())
HDR = {2: ('C158012', 0.0409), 3: ('C144394', 0.0548), 4: ('C144395', 0.0625), 6: ('C144397', 0.092),
       11: ('C158031', 0.1955), 12: ('C158027', 0.2166), 14: ('C158022', 0.2686)}
HOU = {2: ('C144401', 0.0202), 3: ('C144402', 0.0271), 4: ('C144403', 0.0239), 6: ('C144405', 0.0281),
       11: ('C157889', 0.0651), 12: ('C157888', 0.0597), 14: ('C157886', 0.0735)}
for k in sorted(hdr):
    V.append(item('JST-XH Stiftleiste', '%d-polig' % k, 'B%dB-XH-A, original JST, RM 2,50 mm' % k, 'auf den Platinen',
                  hdr[k], LCS, HDR[k][0], HDR[k][1]))
for k in sorted(hdr):
    V.append(item('JST-XH Gehäuse', '%d-polig' % k, 'XHP-%d, original JST' % k, 'Kabelseite', hdr[k], LCS, HOU[k][0], HOU[k][1]))
V.append(item('JST-XH Crimpkontakt', 'Buchse', 'SXH-001T-P0.6, original JST, AWG 28-22', '%d Kontakte pro Gerät' % pins,
              pins, LCS, 'C140573', 0.01, note='Grosse Reserve: die ersten Crimps gehen erfahrungsgemäss daneben'))
V.append(item('Litze', '0,14 mm² (AWG 26)', 'Quadrios 22CW001: 10 Farben × 10 m = 100 m', '153 Bedienfeld-Drähte + Platinenkabel',
              0, CON, '2620403', 15.95, cur='CHF', note='ca. 40 m pro Gerät - ein Set reicht für beide'))
sheets['Verbinder'] = V

# ---------------- panel ----------------
B = [
    item('Tandem-Poti (Stereo)', '1 MΩ, Kennlinie C (umgekehrt log.)', 'Alpha 16 mm, Achse 6 mm rund, Printstifte', 'RV_01 + RV_02 je Oszillator',
         3, TAY, 'A-8590', 0.99, note='Tonhöhe. C, nicht A: verdrahtet wird Lug 1 (CW) + Schleifer - nur mit C verteilen sich die Oktaven gleichmässig. Siehe BEDIENFELD-ERGAENZUNGEN.md'),
    item('Tandem-Poti (Stereo)', '100 kΩ, Kennlinie C (umgekehrt log.)', 'Alpha 16 mm, Achse 6,35 mm, Printstifte', 'RV_01 + RV_02 je Filter',
         4, TAY, 'A-4749', 0.80, note='Cutoff - gleiche Begründung wie bei der Tonhöhe'),
    item('Poti', '100 kΩ lin (B)', '16 mm, Lötfahnen, Achse 6,35 mm', 'RV_03 je Oszillator (Drive)', 3, TAY, 'A-5617', 0.39),
    item('Poti', '100 kΩ log (A)', 'Alpha 16 mm, Lötfahnen, Achse 6,35 mm', 'RV_04 je Oszillator (Distortion-Pegel)', 3, TAY, 'A-2401', 0.50),
    item('Poti', '10 kΩ log (A)', 'Alpha 16 mm, Lötfahnen, Achse 6,35 mm', 'RV_05 je Osz. (Amplitude), Master (RV901)', 4, TAY, 'A-4875', 0.50),
    item('Schiebepoti (Fader)', '10 kΩ log (A)', 'Alpha, 60 mm Schiebeweg, Metallhebel', 'Mixer Kanal 1-3 (RV801-RV803)', 3, TAY, 'A-1617', 1.69,
         note='gleiche 3 Anschlüsse wie im Verdrahtungsplan. Schlitz in der Front ca. 62 mm'),
    item('Fader-Knopf', 'schwarz', 'für Schiebepoti', 'Mixer', 3, TAY, 'A-5396', 0.39),
    item('Poti', '50 kΩ lin (B)', 'Alpha 16 mm, Lötfahnen, Achse 6,35 mm', 'RV_03 je Filter (Resonanz)', 4, TAY, 'A-2398', 0.50,
         note='Schaltplan sagt 47 kΩ - 50 kΩ ist der gängige Wert und geht genauso'),
    item('Drehschalter', '1 × 12, Anschlag einstellbar', 'Alpha SR2611F, Lötfahnen, runde Achse', 'SW_01 Oszillator (4 Stell.), SW_01 Filter (5 Stell.)',
         7, TAY, 'A-1893', 1.69, note='Anschlag mit der Scheibe auf 4 bzw. 5 Stellungen setzen'),
    item('Kippschalter', 'EIN-EIN (1 × UM)', 'SPDT, 1M-Serie, 6 mm Einbau', 'SW_02..SW_05 je Oszillator', 12, TAY, 'A-3186', 0.70,
         note='SW_05 = Oszillator ein/aus, siehe BEDIENFELD-ERGAENZUNGEN.md'),
    item('Klinkenbuchse', '3,5 mm mono', 'PJ-301BM, Einbau, isoliert', 'J_01..J_03 je Osz., Filter C/D ein/aus', 13, TAY, 'A-2566', 0.29,
         note='Frontplatte höchstens ca. 3 mm dick (kurzes Gewinde) - bei dickerem Holz von hinten aussenken'),
    item('Drehknopf', 'für 6,35-mm-Achse, Madenschraube', 'KN8E, 20 × 16 mm', '21 Drehpotis + 7 Drehschalter', 28, TAY, 'A-6751', 0.40,
         note='Madenschraube hält auch auf den 6-mm-Achsen der 1-MΩ-Tandempotis'),
    item('Taster', 'Schliesser, tastend', 'rund, schwarz', 'Oszilloskop-Modus ZEIT/FIGUR/FREI', 1, TAY, 'A-3487', 1.09,
         note='zwischen Arduino-Pin RESET und GND'),
    item('Lautsprecherklemme', 'rot', 'Polklemme 4 mm, vergoldet', '+ an J904 Pin 1', 1, TAY, 'A-6484', 0.45),
    item('Lautsprecherklemme', 'schwarz', 'Polklemme 4 mm, vergoldet', '− an J904 Pin 2', 1, TAY, 'A-6483', 0.45),
]
sheets['Bedienfeld'] = B

# ---------------- power ----------------
S = [
    item('Steckernetzteil', '12 V DC, 1 A', 'Mean Well NGE12E12-P1J, Eurostecker, Hohlstecker 5,5/2,1', 'versorgt alles',
         1, CON, '3164222', 9.85, cur='CHF', note='Netzspannung bleibt ausserhalb des Holzgehäuses. Bedarf ca. 0,5 A'),
    item('DC/DC-Wandler, isoliert', '12 V → 12 V, 2 W (für −12 V)', 'B1212S-2WR3 (HI-LINK), SIP-4', 'erzeugt −12 V',
         1, LCS, 'C5365309', 1.2554, note='+Vo an Masse, 0V-Ausgang ist dann −12 V. +12 V kommt direkt vom Netzteil. Siehe BEDIENFELD-ERGAENZUNGEN.md'),
    item('Elektrolytkondensator', '22 µF / 25 V', '5 × 11 mm', 'Eingang DC/DC-Wandler', 1, TAY, 'A-4784', 0.07),
    item('Lochrasterplatine', '50 × 70 mm', 'doppelseitig', 'Netzteil-Platinchen', 1, TAY, 'A-1194', 0.99),
    item('DC-Einbaubuchse', '5,5 / 2,1 mm', 'rund, Gehäuseeinbau', 'Rückwand', 1, TAY, 'A-991', 0.28),
    item('Kippschalter', 'Netzschalter', 'wie die übrigen (A-3186), nur zwei Anschlüsse benutzt', 'Hauptschalter', 1, TAY, 'A-3186', 0.70),
    item('Rückstellende Sicherung', '1,1 A', 'Littelfuse RXEF110, bedrahtet', '12-V-Eingang', 1, LCS, 'C3760872', 0.4692),
    item('JST-XH Stiftleiste', '3-polig', 'B3B-XH-A', 'Netzteil-Platinchen → J990', 1, LCS, 'C144394', 0.0548),
    item('JST-XH Gehäuse', '3-polig', 'XHP-3', 'Netzteil-Platinchen → J990', 1, LCS, 'C144402', 0.0271),
    item('JST-XH Crimpkontakt', 'Buchse', 'SXH-001T-P0.6', 'Netzteil-Platinchen → J990', 3, LCS, 'C140573', 0.01),
    item('DC-Kabel', 'Stecker 5,5/2,1 mit Litze', '', '12 V an die Arduino-Buchse', 1, TAY, 'A-6806', 0.15,
         note='Der Arduino läuft an 12 V über seine eigene Buchse; kein USB mehr nötig'),
]
sheets['Stromversorgung'] = S

# ---------------- Arduino ----------------
A = [
    item('Arduino Uno R3', 'kompatibel, mit ATmega16U2', '', 'Oszilloskop', 1, TAY, 'A-2854', 9.99, have=1, note='1 ist vorhanden'),
    item('TFT-Display', 'ILI9341, 240 × 320, SPI', '2,8" (2,2" hat Tayda nicht) - gleicher Chip, Sketch läuft unverändert', 'Oszilloskop',
         1, TAY, 'A-8181', 7.99, have=1, note='1 (2,2") ist vorhanden. Front-Ausschnitt für das 2,8"-Modul grösser machen'),
    item('Widerstand', '510 Ω', '0207, 1 %', 'Pegelwandler Display', 4, TAY, 'A-2621', 0.015),
    item('Widerstand', '1 kΩ', '0207, 1 %', 'Pegelwandler Display (4) + Schutzwiderstand vor A0 (1)', 5, TAY, 'A-2200', 0.015, extra=3),
    item('Widerstand', '220 Ω', '0207, 1 %', 'Display-Hintergrundlicht', 1, TAY, 'A-2246', 0.015, extra=1),
    item('Widerstand', '47 kΩ', '0207, 1 %', 'Eingangsstufe Oszilloskop', 3, TAY, 'A-2279', 0.015, extra=2,
         note='Eingangsstufe: 1 µF → 47k → Knoten (47k nach +5 V, 47k nach GND) → 1k → A0. Abgriff: FILT_B_OUT an J817'),
    item('Folienkondensator', '1 µF', 'RM 5 mm', 'Eingangsstufe Oszilloskop', 1, TAY, 'A-8409', 0.25, extra=1),
    item('Schottky-Diode', 'BAT85', 'DO-35, Vishay BAT85S', 'Eingangsschutz A0', 2, LCS, 'C3312828', 0.0938,
         note='leiten alles über 5 V und unter 0 V ab - schützt A0 auch bei ±11 V'),
    item('Lochrasterplatine', '50 × 70 mm', 'doppelseitig', 'Display-Pegelwandler + Eingangsstufe', 1, TAY, 'A-1194', 0.99, extra=0),
]
sheets['Arduino'] = A

# ---------------- mechanics ----------------
holes = 8 * 4 + 4 + 4 + 4        # 8 boards, Arduino, display, power board
M = [
    item('Abstandsbolzen', 'M3 × 8 mm, Aussen-/Innengewinde', 'Messing', '%d Löcher pro Gerät' % holes, holes, TAY, 'A-1264', 0.08,
         note='Aussengewinde direkt ins Holz (2,5-mm-Loch vorbohren), Platine oben mit der Schraube'),
    item('Schraube', 'M3 × 6 mm', 'Linsenkopf, Stahl', 'Platine auf Bolzen', holes, TAY, 'A-1250', 0.02),
]
sheets['Mechanik'] = M

# ---------------- tuning + spares ----------------
R = [
    item('Folienkondensator', '47 nF', 'wie C101', 'Abgleich Sägezahn (C101 kleiner → höher)', 0, TAY, 'A-563', 0.065,
         note='nur falls ein Oszillator neben den anderen Wellenformen liegt'),
    item('Folienkondensator', '68 nF', 'wie C101', 'Abgleich Sägezahn (C101 grösser → tiefer)', 0, TAY, 'A-707', 0.12),
    item('Folienkondensator', '12 nF', 'wie C102', 'Bereich Funktionsgenerator höher', 0, TAY, 'A-620', 0.08),
    item('Folienkondensator', '18 nF', 'wie C102', 'Bereich Funktionsgenerator tiefer', 0, TAY, 'A-703', 0.10),
    item('Widerstand', '15 kΩ', '0207, 1 %', 'R105 kleiner → FG-Bereich höher', 0, TAY, 'A-2182', 0.015),
    item('Widerstand', '18 kΩ', '0207, 1 %', 'R105 grösser → FG-Bereich tiefer', 0, TAY, 'A-2207', 0.015),
    item('Op-Amp (SMD, Reserve)', 'TL074CDR', 'SOIC-14', 'für Reparaturen', 0, LCS, 'C12594', 0.2887,
         note='wird sonst von JLCPCB bestückt; LCSC verkauft mindestens 5'),
    item('Op-Amp (SMD, Reserve)', 'OPA1662', 'SOIC-8', 'für Reparaturen', 0, LCS, 'C882794', 1.0769),
    item('Schmitt-Trigger (SMD, Reserve)', 'SN74LVC2G17DBVR', 'SOT-23-6', 'Tausch bei grosser Abweichung', 0, LCS, 'C10429', 0.2575,
         note='Schwellen streuen stark - ein Tauschchip kann einen Oszillator retten'),
]
sheets['Abgleich+Reserve'] = R

# ---------------- tools / consumables ----------------
T = [
    item('Crimpzange', 'für JST-XH', 'SN-28B, AWG 28-18', '', 0, TAY, 'A-5362', 9.70,
         note='ohne sie lassen sich die ~500 Kontakte nicht sauber anschlagen'),
    item('Kabelbinder', '3 × 100 mm', '100 Stück', 'Kabelbäume', 0, TAY, 'A-7409', 0.49),
    item('Lötzinn', '0,5-0,7 mm, mit Flussmittel', 'bleifrei', '', 0, CON, 'nur falls nicht vorhanden', 15.00, cur='CHF', extra=0,
         note='Menge 1 eintragen, falls keins da ist'),
    item('Entlötlitze', '2 mm', '', '', 0, CON, 'nur falls nicht vorhanden', 5.00, cur='CHF', extra=0,
         note='Menge 1 eintragen, falls keine da ist'),
]
sheets['Werkzeug'] = T

# ---------------- balance every part number against its cart ----------------
by_pn = {}
for r in ALL:
    by_pn.setdefault(r['pn'], []).append(r)
problems = []
for pn, rs in by_pn.items():
    if pn not in CART:
        for r in rs:
            if r['extra'] is None:
                r['extra'] = 0
        continue
    fixed = sum(DEVICES * r['per'] + r['extra'] - r['have'] for r in rs if r['extra'] is not None)
    free = [r for r in rs if r['extra'] is None]
    if len(free) > 1:
        for r in free[:-1]:
            r['extra'] = 0
            fixed += DEVICES * r['per'] - r['have']
        free = free[-1:]
    if free:
        r = free[0]
        r['extra'] = CART[pn] - fixed - DEVICES * r['per'] + r['have']
        if r['extra'] < 0:
            problems.append('%s: cart %d is less than needed' % (pn, CART[pn]))
    elif fixed != CART[pn]:
        problems.append('%s: rows give %d, cart has %d' % (pn, fixed, CART[pn]))
missing = [pn for pn in CART if pn not in by_pn]
if problems or missing:
    raise SystemExit('cart mismatch: %s %s' % (problems, missing))

SHIPPING = [  # supplier, cost, currency, what
    (TAY, 21.23, 'USD', 'DHL Express DDP - MWST, Zoll und alle Gebühren inbegriffen, 2-4 Tage'),
    (LCS, 17.52, 'USD', 'Global Direct Standard Line, 7-15 Werktage; Warenwert unter der MWST-Grenze'),
    (CON, 9.95, 'CHF', 'Post'),
]

json.dump(dict(sheets=sheets, pins=pins, headers=hdr, shipping=SHIPPING, cart=CART),
          open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in sheets.items():
    print('%-17s %3d rows' % (k, len(v)))
tot = {}
for r in ALL:
    q = DEVICES * r['per'] + r['extra'] - r['have']
    tot.setdefault((r['supplier'], r['cur']), 0)
    tot[(r['supplier'], r['cur'])] += q * r['price']
print('goods per supplier:', {k: round(v, 2) for k, v in tot.items()})
print('JST pins per device:', pins, 'headers:', hdr)
