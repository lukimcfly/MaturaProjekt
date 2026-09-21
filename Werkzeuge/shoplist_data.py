"""Shopping-list rows for the synthesizer, as JSON for the Excel builder.

Board parts are counted straight from the master BOM (SynthesizerFinal BOM.csv), so the
list cannot drift from the schematic. Everything else - panel hardware, cables, power,
Arduino, mounting, tools - is added by hand below with the reasoning in 'note'.
Quantities are PER DEVICE; the workbook multiplies by the device count.
"""
import csv, json, re, sys, math

BOM = 'MaturaProjekt/SynthesizerFinal/BOM.csv'

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
    refs = expand(r['Reference'])
    key = (r['Value'], r['Footprint'])
    rows.setdefault(key, []).extend(refs)

def count(value, fp_contains=''):
    n, refs = 0, []
    for (v, fp), rr in rows.items():
        if v == value and fp_contains in fp:
            n += len(rr); refs += rr
    return n, refs

def reflist(refs):
    refs = sorted(refs, key=lambda s: (re.sub(r'\d', '', s), int(re.sub(r'\D', '', s))))
    return ', '.join(refs) if len(refs) <= 8 else ', '.join(refs[:6]) + ', … (%d)' % len(refs)

DIS, MUS, BAS, GAL, CON = 'Distrelec (CH)', 'Musikding (DE)', 'Bastelgarage (CH)', 'Galaxus (CH)', 'Conrad (CH)'

def spare(n, pct, mn):
    return max(mn, math.ceil(n * 2 * pct))       # reserve sized for the default of 2 devices

sheets = {}

# ---------------- board parts (THT, hand-soldered) ----------------
P = []
res_vals = ['1', '10', '100', '220', '470', '1k', '2.2k', '6.8k', '10k', '16k', '20k',
            '47k', '56k', '68k', '82k', '100k', '330k']
for v in res_vals:
    n, refs = count(v, 'Resistor')
    if n:
        P.append(dict(part='Widerstand', value=v + ' Ω' if not v.endswith('k') else v + 'Ω',
                      spec='Metallschicht 1 %, 0,25 W, Bauform 0207', refs=reflist(refs),
                      per=n, extra=spare(n, 0.2, 5), have=0, supplier=DIS,
                      pn='Metallschichtwiderstand 0207 1%% %s' % v, price=0.10, note=''))
film = [('56nF', 'Folienkondensator', 'PET (z.B. WIMA MKS2), 63 V, RM 5 mm, 7,2 × 2,5 mm', 0.45,
         'Zeitkondensator Sägezahn - Folie, keine Keramik! (Keramik lag 56 % daneben)'),
        ('15nF', 'Folienkondensator', 'PET (z.B. WIMA MKS2), 63 V, RM 5 mm, 7,2 × 2,5 mm', 0.40,
         'Zeitkondensator Funktionsgenerator + Filter - Folie'),
        ('47nF', 'Folienkondensator', 'PET, 63 V, RM 5 mm, 7,2 × 2,5 mm', 0.40, ''),
        ('330nF', 'Folienkondensator', 'PET, 63 V, RM 5 mm, max. 7,2 × 3,5 mm', 0.50, ''),
        ('1uF', 'Folienkondensator', 'PET (z.B. WIMA MKS2), 63 V, RM 5 mm, 7,2 × 4,5 mm', 0.60, '')]
for v, part, spec, pr, note in film:
    n, refs = count(v, 'C_Rect')
    P.append(dict(part=part, value=v.replace('uF', ' µF').replace('nF', ' nF'), spec=spec,
                  refs=reflist(refs), per=n, extra=spare(n, 0.2, 3), have=0, supplier=DIS,
                  pn='WIMA MKS2 ' + v.replace('uF', 'µF'), price=pr, note=note))
n, refs = count('100nF', 'C_Disc')
P.append(dict(part='Keramikkondensator', value='100 nF', spec='X7R, 50 V, RM 5 mm',
              refs=reflist(refs), per=n, extra=spare(n, 0.2, 5), have=0, supplier=DIS,
              pn='Keramik 100nF 50V X7R RM5', price=0.10, note='Abblockkondensatoren'))
elkos = [('10 µF / 25 V', ['10uF/25V', '10uF/16V'], 'Elko radial, Ø 5 mm, RM 2,5 mm, 105 °C', 0.20, '10 µF/16 V der Hauptplatine durch 25-V-Typ ersetzt'),
         ('47 µF / 25 V', ['47uF/25V'], 'Elko radial, Ø 6,3 mm, RM 2,5 mm', 0.25, ''),
         ('100 µF / 25 V', ['100uF/25V'], 'Elko radial, Ø 6,3 mm, RM 2,5 mm', 0.25, ''),
         ('470 µF / 25 V', ['470uF/16V', '470uF/25V'], 'Elko radial, Ø 10 mm, RM 5 mm', 0.50, '470 µF/16 V durch 25-V-Typ ersetzt'),
         ('10 µF bipolar', ['10uF/25V bipolar'], 'bipolarer Elko, max. Ø 5 mm, RM 2,5 mm, ≥ 16 V', 0.40, 'liegt auf 0 V Gleichspannung - bipolar nötig')]
for label, vals, spec, pr, note in elkos:
    n, refs = 0, []
    for v in vals:
        a, b = count(v); n += a; refs += b
    P.append(dict(part='Elektrolytkondensator', value=label, spec=spec, refs=reflist(refs),
                  per=n, extra=spare(n, 0.2, 2), have=0, supplier=DIS, pn='Elko ' + label.replace(' ', ''),
                  price=pr, note=note))
semis = [('Diode', '1N4148', 'DO-35', 0.05, 10, ''),
         ('Schottky-Diode', '1N5819', 'DO-41', 0.15, 2, 'Verpolschutz'),
         ('Transistor', 'BC547', 'TO-92 (Beine auf 2,54 mm spreizen)', 0.15, 5, 'BC547B'),
         ('Spannungsregler', '78L05', 'TO-92, 100 mA', 0.30, 2, 'z.B. L78L05ACZ'),
         ('Op-Amp', 'TL074', 'DIP-14', 0.60, 2, 'TL074CN - gesockelt, Tausch ohne Löten'),
         ('Endstufe', 'LM386', 'DIP-8', 1.00, 2, 'LM386N-4 (bis 18 V) statt N-1 (nur bis 12 V) - mehr Reserve an 12 V')]
for part, v, spec, pr, ex, note in semis:
    n, refs = count(v)
    P.append(dict(part=part, value=v, spec=spec, refs=reflist(refs), per=n, extra=ex, have=0,
                  supplier=DIS, pn={'TL074': 'TL074CN', 'LM386': 'LM386N-4', 'BC547': 'BC547B',
                                    '78L05': 'L78L05ACZ'}.get(v, v), price=pr, note=note))
P.append(dict(part='IC-Fassung', value='DIP-14', spec='Präzisionsfassung, 7,62 mm', refs='U101, U201, U301',
              per=3, extra=1, have=0, supplier=DIS, pn='IC-Fassung DIP-14 gedreht', price=0.40, note=''))
P.append(dict(part='IC-Fassung', value='DIP-8', spec='Präzisionsfassung, 7,62 mm', refs='U901',
              per=1, extra=1, have=0, supplier=DIS, pn='IC-Fassung DIP-8 gedreht', price=0.30, note=''))
P.append(dict(part='Feinsicherung', value='T 500 mA', spec='träge, 5 × 20 mm', refs='F901, F902',
              per=2, extra=10, have=0, supplier=DIS, pn='Feinsicherung 5x20 T500mA', price=0.30,
              note='Reserve bewusst gross - Sicherungen sind Verbrauchsmaterial'))
P.append(dict(part='Sicherungsclip', value='5 × 20 mm', spec='Printclip, Littelfuse 111er-Serie', refs='F901, F902 (je 2 Clips)',
              per=4, extra=2, have=0, supplier=DIS, pn='Littelfuse 01110501Z', price=0.30,
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
for k in sorted(hdr):
    V.append(dict(part='JST-XH Stiftleiste', value='%d-polig' % k, spec='gerade, stehend, RM 2,50 mm',
                  refs='auf den Platinen', per=hdr[k], extra=max(1, math.ceil(hdr[k] * 0.1)), have=0,
                  supplier=DIS, pn='JST B%dB-XH-A' % k, price=0.15 + 0.03 * k, note=''))
for k in sorted(hdr):
    V.append(dict(part='JST-XH Gehäuse', value='%d-polig' % k, spec='Buchsengehäuse zum Crimpen',
                  refs='Kabelseite', per=hdr[k], extra=max(2, math.ceil(hdr[k] * 0.2)), have=0,
                  supplier=DIS, pn='JST XHP-%d' % k, price=0.05 + 0.01 * k, note=''))
V.append(dict(part='JST-XH Crimpkontakt', value='Buchse', spec='für Litze AWG 28-22', refs='%d Kontakte pro Gerät' % pins,
              per=pins, extra=100, have=0, supplier=DIS, pn='JST SXH-001T-P0.6', price=0.03,
              note='Grosse Reserve: die ersten Crimps gehen erfahrungsgemäss daneben'))
V.append(dict(part='Litze', value='0,14 mm² (AWG 26)', spec='verzinnt, 8 Farben à 10 m', refs='153 Bedienfeld-Drähte + Platinenkabel',
              per=4, extra=0, have=0, supplier=DIS, pn='Schaltlitze LiY 0,14 mm² 10 m', price=5.00,
              note='Menge = Rollen à 10 m; ca. 40 m pro Gerät. Farben: rot, schwarz, blau, gelb, grün, weiss, orange, braun'))
sheets['Verbinder'] = V

# ---------------- panel ----------------
B = []
panel = [
    ('Tandem-Poti (Stereo)', '1 MΩ log (A)', '16 mm, Achse 6 mm, Löt­fahnen', 'RV_01 + RV_02 je Oszillator', 3, 1, MUS, 'Alpha 16mm Stereo 1M log', 2.60,
     'Tonhöhe. LOG statt lin: verteilt die Oktaven gleichmässig über den Drehweg (lin: höchste Oktave auf 1 % des Drehwegs)'),
    ('Tandem-Poti (Stereo)', '100 kΩ log (A)', '16 mm, Achse 6 mm', 'RV_01 + RV_02 je Filter', 4, 1, MUS, 'Alpha 16mm Stereo 100k log', 2.60,
     'Cutoff. Gleiches Problem wie bei der Tonhöhe - log empfohlen'),
    ('Poti', '100 kΩ lin (B)', '16 mm, Achse 6 mm', 'RV_03 je Oszillator (Drive)', 3, 1, MUS, 'Alpha 16mm 100k lin', 1.20, ''),
    ('Poti', '100 kΩ log (A)', '16 mm, Achse 6 mm', 'RV_04 je Oszillator (Distortion-Pegel)', 3, 1, MUS, 'Alpha 16mm 100k log', 1.20, ''),
    ('Poti', '10 kΩ log (A)', '16 mm, Achse 6 mm', 'RV_05 je Osz. (Amplitude), Master (RV901)', 4, 1, MUS, 'Alpha 16mm 10k log', 1.20, ''),
    ('Schiebepoti (Fader)', '10 kΩ log (A)', 'mono, 45 mm Schiebeweg, Lötfahnen', 'Mixer Kanal 1-3 (RV801-RV803)', 3, 1, MUS, 'Schiebepoti 10k log 45mm mono', 2.50,
     'statt Drehpoti; gleiche 3 Anschlüsse wie im Verdrahtungsplan. Braucht einen Schlitz in der Front'),
    ('Fader-Knopf', 'passend zum Schiebepoti', '', 'Mixer', 3, 1, MUS, 'Faderknopf', 1.00, 'Schaftbreite mit dem Schiebepoti abgleichen'),
    ('Poti', '47 kΩ lin (B)', '16 mm, Achse 6 mm', 'RV_03 je Filter (Resonanz)', 4, 1, MUS, 'Alpha 16mm 50k lin', 1.20, '50 kΩ lin ist gängiger und geht genauso'),
    ('Drehschalter', '1 × 12, Anschlag einstellbar', 'Achse 6 mm, Lötfahnen', 'SW_01 Oszillator (4 Stellungen), SW_01 Filter (5 Stellungen)', 7, 1, MUS,
     'Drehschalter 1x12 einstellbar (Lorlin/Alpha)', 3.50, 'Anschlag mit der Scheibe auf 4 bzw. 5 Stellungen setzen'),
    ('Kippschalter', 'EIN-EIN (1 × UM)', 'SPDT, 6 mm Einbau', 'SW_02, SW_03, SW_04 + neu SW_05 (Oszillator ein/aus) je Oszillator', 12, 1, MUS, 'Kippschalter SPDT ON-ON', 1.80,
     'SW_05 schaltet den Buffer-Eingang zwischen Amplituden-Poti und Masse um - siehe Platinen/BEDIENFELD-ERGAENZUNGEN.md'),
    ('Klinkenbuchse', '3,5 mm mono', 'Einbaubuchse, isoliert', 'J_01..J_03 je Osz., Filter C/D ein/aus', 13, 2, MUS, 'Klinkenbuchse 3,5mm mono isoliert', 1.00, ''),
    ('Drehknopf', 'für 6-mm-Achse', 'mit Madenschraube', '21 Drehpotis + 7 Drehschalter', 28, 3, MUS, 'Drehknopf 6mm Achse', 1.00,
     'Achse der Potis vor dem Kauf abgleichen (6 mm oder 1/4")'),
    ('Taster', 'Schliesser, tastend', 'Einbau ca. 7 mm', 'Oszilloskop-Modus ZEIT/FIGUR/FREI', 1, 1, MUS, 'Taster Schliesser tastend', 1.50,
     'zwischen Arduino-Pin RESET und GND - wirkt wie der RESET-Knopf auf dem Arduino, der im Gehäuse sitzt'),
    ('Lautsprecherklemme', 'Paar rot/schwarz', 'Polklemme für 4-mm-Bananenstecker und blanken Draht', 'Anschluss für den eigenen Lautsprecher (an J904)', 2, 0, DIS,
     'Polklemme 4mm rot + schwarz', 1.50, 'Menge = Stück (1 rot + 1 schwarz). Kein eingebauter Lautsprecher mehr. Lautsprecher mit 8 Ω oder mehr'),
    ('Patchkabel', '3,5 mm mono', '30 cm', 'Filter C/D einschleifen', 4, 0, MUS, 'Patchkabel 3,5mm 30cm', 2.00, ''),
]
for part, v, spec, refs, per, ex, sup, pn, pr, note in panel:
    B.append(dict(part=part, value=v, spec=spec, refs=refs, per=per, extra=ex, have=0, supplier=sup,
                  pn=pn, price=pr, note=note))
sheets['Bedienfeld'] = B

# ---------------- power ----------------
S = [
    dict(part='Tischnetzteil', value='12 V DC, 2 A', spec='5,5/2,1 mm Stecker, Kaltgeräte-Buchse C8', refs='versorgt alles',
         per=1, extra=0, have=0, supplier=DIS, pn='Mean Well GST25E12-P1J', price=15.00,
         note='Netzspannung bleibt ausserhalb des Holzgehäuses'),
    dict(part='Netzkabel', value='Schweizer Stecker (Typ J) auf C7', spec='1,5 m', refs='zum Netzteil',
         per=1, extra=0, have=0, supplier=DIS, pn='Netzkabel CH Typ J C7', price=5.00, note=''),
    dict(part='DC/DC-Wandler, isoliert', value='12 V → ±12 V, 250 mA', spec='TRACO TMR 6-1222, SIP-8', refs='erzeugt ±12 V für den Synthesizer',
         per=1, extra=0, have=0, supplier=DIS, pn='TRACO TMR 6-1222', price=22.00,
         note='TRACO = Schweizer Firma. Ausgang 0 V mit dem 12-V-Minus verbinden (gemeinsame Masse mit dem Arduino)'),
    dict(part='Elektrolytkondensator', value='22 µF / 25 V', spec='Ø 5 mm', refs='Ein-/Ausgang Wandler',
         per=3, extra=1, have=0, supplier=DIS, pn='Elko 22µF 25V', price=0.20, note='Beschaltung nach Datenblatt TMR 6'),
    dict(part='Lochrasterplatine', value='ca. 50 × 70 mm', spec='Streifen- oder Punktraster', refs='Netzteil-Platine',
         per=1, extra=1, have=0, supplier=DIS, pn='Lochrasterplatine 50x70', price=2.00, note=''),
    dict(part='DC-Einbaubuchse', value='5,5 / 2,1 mm', spec='Gehäuseeinbau', refs='Rückwand',
         per=1, extra=0, have=0, supplier=DIS, pn='DC Einbaubuchse 5.5x2.1', price=1.50, note=''),
    dict(part='Kippschalter', value='EIN-AUS', spec='≥ 2 A, 12 V', refs='Hauptschalter',
         per=1, extra=0, have=0, supplier=MUS, pn='Kippschalter SPST', price=1.80, note=''),
    dict(part='Rückstellende Sicherung', value='1,1 A', spec='PTC, bedrahtet', refs='12-V-Eingang',
         per=1, extra=1, have=0, supplier=DIS, pn='PTC 1.1A radial', price=0.50, note='schützt Netzteil und Verdrahtung'),
    dict(part='JST-XH Stiftleiste', value='3-polig', spec='gerade, stehend, RM 2,50 mm', refs='Netzteil-Platine → J990',
         per=1, extra=1, have=0, supplier=DIS, pn='JST B3B-XH-A', price=0.25, note='zweites Kabelende der Versorgung'),
    dict(part='JST-XH Gehäuse', value='3-polig', spec='Buchsengehäuse zum Crimpen', refs='Netzteil-Platine → J990',
         per=1, extra=1, have=0, supplier=DIS, pn='JST XHP-3', price=0.08, note=''),
    dict(part='JST-XH Crimpkontakt', value='Buchse', spec='für Litze AWG 28-22', refs='Netzteil-Platine → J990',
         per=3, extra=0, have=0, supplier=DIS, pn='JST SXH-001T-P0.6', price=0.03, note=''),
    dict(part='DC-Kabel', value='5,5/2,1-Stecker, offenes Ende', spec='ca. 30 cm', refs='12 V an die Arduino-Buchse',
         per=1, extra=0, have=0, supplier=DIS, pn='DC Kabel 5.5x2.1 offen', price=3.00,
         note='Der Arduino läuft an 12 V über seine eigene Buchse; kein USB mehr nötig'),
]
sheets['Stromversorgung'] = S

# ---------------- Arduino ----------------
A = [
    dict(part='Arduino Uno R3', value='oder kompatibel', spec='', refs='Oszilloskop', per=1, extra=0, have=1,
         supplier=BAS, pn='Arduino Uno R3', price=20.00, note='1 ist vorhanden'),
    dict(part='TFT-Display', value='2,2" ILI9341, 240 × 320, SPI', spec='', refs='Oszilloskop', per=1, extra=0, have=1,
         supplier=BAS, pn='2.2 TFT ILI9341 SPI', price=12.00, note='1 ist vorhanden'),
    dict(part='Widerstand', value='510 Ω', spec='0207, 1 %', refs='Pegelwandler Display', per=4, extra=2, have=0,
         supplier=DIS, pn='Metallschichtwiderstand 0207 1% 510', price=0.10, note=''),
    dict(part='Widerstand', value='1 kΩ', spec='0207, 1 %', refs='Pegelwandler Display (4) + Schutzwiderstand vor A0 (1)', per=5, extra=2, have=0,
         supplier=DIS, pn='Metallschichtwiderstand 0207 1% 1k', price=0.10, note=''),
    dict(part='Widerstand', value='220 Ω', spec='0207, 1 %', refs='Display-Hintergrundlicht', per=1, extra=1, have=0,
         supplier=DIS, pn='Metallschichtwiderstand 0207 1% 220', price=0.10, note=''),
    dict(part='Widerstand', value='47 kΩ', spec='0207, 1 %', refs='Eingangsstufe Oszilloskop', per=3, extra=2, have=0,
         supplier=DIS, pn='Metallschichtwiderstand 0207 1% 47k', price=0.10,
         note='Eingangsstufe: 1 µF → 47k → Knoten (47k nach +5 V, 47k nach GND) → 1k → A0. Teilt durch 3 und hebt auf 2,5 V: ±7 V → 0,2..4,8 V. Abgriff: FILT_B_OUT an J817'),
    dict(part='Folienkondensator', value='1 µF', spec='RM 5 mm', refs='Eingangsstufe Oszilloskop', per=1, extra=1, have=0,
         supplier=DIS, pn='WIMA MKS2 1µF', price=0.60, note='sperrt Gleichspannung'),
    dict(part='Schottky-Diode', value='BAT85', spec='DO-34', refs='Eingangsschutz A0', per=2, extra=2, have=0,
         supplier=DIS, pn='BAT85', price=0.10, note='leiten alles über 5 V und unter 0 V ab - schützt A0 auch bei ±11 V'),
    dict(part='Lochrasterplatine', value='ca. 50 × 70 mm', spec='', refs='Display-Pegelwandler + Eingangsstufe', per=1, extra=0, have=0,
         supplier=DIS, pn='Lochrasterplatine 50x70', price=2.00, note='ersetzt das Steckbrett im fertigen Gerät'),
]
sheets['Arduino'] = A

# ---------------- mechanics ----------------
holes = 8 * 4 + 4 + 4 + 4        # 8 boards, Arduino, display, power board
M = [
    dict(part='Einschraubmuffe für Holz', value='M3', spec='Stahl verzinkt oder Messing', refs='%d Löcher pro Gerät' % holes,
         per=holes, extra=10, have=0, supplier=DIS, pn='Einschraubmutter M3 Holz', price=0.25, note='hält auch bei häufigem Auf- und Zuschrauben'),
    dict(part='Abstandsbolzen', value='M3 × 10 mm', spec='Aussen-/Innengewinde, Messing oder Nylon', refs='zwischen Holz und Platine',
         per=holes, extra=10, have=0, supplier=DIS, pn='Abstandsbolzen M3 10mm AG/IG', price=0.30, note='Aussengewinde in die Muffe, Platine oben drauf'),
    dict(part='Schraube', value='M3 × 6 mm', spec='Linsen- oder Zylinderkopf', refs='Platine auf Bolzen',
         per=holes, extra=10, have=0, supplier=DIS, pn='Schraube M3x6 Linsenkopf', price=0.05, note='Kopf-Ø ≤ 6 mm'),
]
sheets['Mechanik'] = M

# ---------------- tuning + spares ----------------
R = [
    dict(part='Folienkondensator', value='47 nF', spec='wie C101', refs='Abgleich Sägezahn (C101 kleiner → höher)', per=0, extra=6, have=0,
         supplier=DIS, pn='WIMA MKS2 47nF', price=0.40, note='nur falls ein Oszillator neben den anderen Wellenformen liegt'),
    dict(part='Folienkondensator', value='68 nF', spec='wie C101', refs='Abgleich Sägezahn (C101 grösser → tiefer)', per=0, extra=6, have=0,
         supplier=DIS, pn='WIMA MKS2 68nF', price=0.45, note=''),
    dict(part='Folienkondensator', value='12 nF', spec='wie C102', refs='Bereich Funktionsgenerator höher', per=0, extra=3, have=0,
         supplier=DIS, pn='WIMA MKS2 12nF', price=0.40, note=''),
    dict(part='Folienkondensator', value='18 nF', spec='wie C102', refs='Bereich Funktionsgenerator tiefer', per=0, extra=3, have=0,
         supplier=DIS, pn='WIMA MKS2 18nF', price=0.40, note=''),
    dict(part='Widerstandssortiment', value='E12, 10 Ω - 1 MΩ', spec='Metallschicht 1 %, 0,25 W, je 10 Stück', refs='für alle Wertänderungen', per=0, extra=1, have=0,
         supplier=GAL, pn='Metallschicht Widerstandssortiment E12 1%', price=15.00, note='deckt R124-, R105- und jede andere Wertänderung ab'),
    dict(part='Op-Amp (SMD, Reserve)', value='OPA4196', spec='SOIC-14', refs='für Reparaturen', per=0, extra=2, have=0,
         supplier=DIS, pn='OPA4196IDR', price=2.50, note='wird sonst von JLCPCB bestückt'),
    dict(part='Op-Amp (SMD, Reserve)', value='OPA1662', spec='SOIC-8', refs='für Reparaturen', per=0, extra=1, have=0,
         supplier=DIS, pn='OPA1662AIDR', price=1.00, note=''),
    dict(part='Schmitt-Trigger (SMD, Reserve)', value='SN74LVC2G17DBVR', spec='SOT-23-6', refs='für Reparaturen / Tausch bei grosser Abweichung', per=0, extra=3, have=0,
         supplier=DIS, pn='SN74LVC2G17DBVR', price=0.40, note='Schwellen streuen stark - ein Tauschchip kann einen Oszillator retten'),
]
sheets['Abgleich+Reserve'] = R

# ---------------- tools / consumables ----------------
T = [
    dict(part='Crimpzange', value='für JST-XH', spec='z.B. Engineer PA-09 oder IWISS SN-28B', refs='', per=0, extra=1, have=0,
         supplier=GAL, pn='Crimpzange JST XH', price=35.00, note='ohne sie lassen sich die 490 Kontakte nicht sauber anschlagen'),
    dict(part='Lötzinn', value='0,5-0,7 mm, mit Flussmittel', spec='bleifrei Sn99,3Cu0,7', refs='', per=0, extra=1, have=0,
         supplier=GAL, pn='Lötzinn 0.7mm bleifrei 100g', price=15.00, note='falls nicht vorhanden'),
    dict(part='Flussmittelstift', value='', spec='No-Clean', refs='', per=0, extra=1, have=0,
         supplier=DIS, pn='Flussmittelstift', price=8.00, note='für eventuelle SMD-Reparaturen'),
    dict(part='Entlötlitze', value='2 mm', spec='', refs='', per=0, extra=1, have=0,
         supplier=DIS, pn='Entlötlitze 2mm', price=5.00, note='zum Tauschen von Bauteilen'),
    dict(part='Schrumpfschlauch-Set', value='', spec='sortiert', refs='Lötfahnen im Bedienfeld', per=0, extra=1, have=0,
         supplier=GAL, pn='Schrumpfschlauch Sortiment', price=10.00, note=''),
    dict(part='Kabelbinder', value='klein', spec='100 Stück', refs='Kabelbäume', per=0, extra=1, have=0,
         supplier=GAL, pn='Kabelbinder 100mm', price=4.00, note=''),
]
sheets['Werkzeug'] = T

json.dump(dict(sheets=sheets, pins=pins, headers=hdr), open(sys.argv[1], 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
for k, v in sheets.items():
    print('%-17s %3d rows' % (k, len(v)))
print('JST pins per device:', pins, 'headers:', hdr)
