"""Generate the build documentation: wiring tables, cable list, panel parts list."""
import sys, os, re, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlib, connspec, split, conndest

OSC_CTRL = {
    'RV01': 'Tonhoehe (Ebene B)',
    'RV02': 'Tonhoehe (Ebene A)',
    'RV03': 'Drive',
    'RV04': 'Distortion-Pegel',
    'RV05': 'Amplitude',
    'SW01': 'Wellenform',
    'SW02': 'weich / hart',
    'SW03': 'Distortion ein/aus',
    'SW04': 'Solo-Filter ein/aus',
    'J01': 'Filter-Send',
    'J02': 'Filter-Return',
    'J03': 'Ausgang',
}
FLT_CTRL = {
    'RV01': 'Cutoff (Ebene A)',
    'RV02': 'Cutoff (Ebene B)',
    'RV03': 'Resonanz',
    'SW01': 'Filterwahl',
    'J01': 'Filter-In',
    'J02': 'Filter-Out',
}
MAIN_CTRL = {
    'RV801': 'Kanal 1 Pegel',
    'RV802': 'Kanal 2 Pegel',
    'RV803': 'Kanal 3 Pegel',
    'RV901': 'Master-Lautstaerke',
}
LUG = {'1': 'Lug 1', '2': 'Lug 2 (Schleifer)', '3': 'Lug 3 (Masse)',
       'T': 'Tip', 'S': 'Sleeve'}

CONNREF = re.compile(r'^J\d1[0-7]$')

CABLE = {}
for _n in (1, 2, 3):
    CABLE[(f"J{_n}15", 1)] = f"Hauptplatine J813/J814/J815 Pin 1"
    CABLE[(f"J{_n}15", 2)] = "Hauptplatine, Masse"
for _m, _a, _b in ((4, "Hauptplatine J816", "Filter B J_13"),
                   (5, "Filter A J_14", "Hauptplatine J817"),
                   (6, "Klinkenbuchse J_01 Tip", "Klinkenbuchse J_02 Tip"),
                   (7, "Klinkenbuchse J_01 Tip", "Klinkenbuchse J_02 Tip")):
    CABLE[(f"J{_m}13", 1)] = _a
    CABLE[(f"J{_m}13", 2)] = "Masse"
    CABLE[(f"J{_m}14", 1)] = _b
    CABLE[(f"J{_m}14", 2)] = "Masse"


def generic(ref):
    return re.sub(r'^([A-Z]+)\d(\d\d)$', r'\1_\2', ref)


def control_name(ref):
    if ref in MAIN_CTRL:
        return MAIN_CTRL[ref]
    m = re.match(r'([A-Z]+)(\d)(\d\d)$', ref)
    if not m:
        return ''
    key = m.group(1) + m.group(3)
    grp = m.group(2)
    if grp in '123':
        return OSC_CTRL.get(key, '')
    if grp in '4567':
        return FLT_CTRL.get(key, '')
    return ''


def is_panel(ref):
    if ref in ('J904', 'J990') or CONNREF.match(ref):
        return False
    return ref.startswith(('RV', 'SW', 'J'))


def sch_parts(sch_path):
    """{reference: library part name} read straight from the schematic.

    Panel hardware carries `on_board no`, so it is absent from the exported
    netlist - and the wiring tables are exactly the part that needs it.  Reading
    the lib_id from the schematic keeps this working without a stale netlist.
    """
    import sexp
    d = sexp.parse(io.open(sch_path, encoding='utf-8').read())
    out = {}
    for el in d:
        if not (isinstance(el, list) and el and el[0] == 'symbol'):
            continue
        lib = ref = None
        for c in el:
            if isinstance(c, list) and c[0] == 'lib_id':
                lib = str(c[1]).strip('"').split(':')[-1]
            elif (isinstance(c, list) and c[0] == 'property'
                  and str(c[1]).strip('"') == 'Reference'):
                ref = str(c[2]).strip('"')
        if lib and ref:
            out[ref] = lib
    return out


def build(netfull, out, sch='SynthesizerFinal.kicad_sch'):
    comps, nets, libparts = netlib.load(netfull)
    from_sch = sch_parts(sch)
    netpins = {n: [(r, p) for r, p, fn, t in pins] for n, pins in nets.items()}

    def dest_of(net, exclude):
        hits = []
        for r, p in netpins.get(net, []):
            if r == exclude or not is_panel(r):
                continue
            hits.append((r, p))
        return hits

    L = []
    w = L.append
    w("# Synthesizer - Aufbau und Verdrahtung")
    w("")
    w("Abgeleitet aus `SynthesizerFinal.kicad_sch` Rev 4.0. Jede Zeile stammt aus der")
    w("exportierten Netzliste, nicht aus dem Gedaechtnis.")
    w("")

    w("## 1. Die drei Platinen")
    w("")
    w("| Platine | Projekt | Stueck | Bauteile auf der Platine |")
    w("|---|---|---|---|")
    for name, proj, mod, qty in (('Oszillator', 'osc', 'OSC1', 3),
                                 ('Filter', 'filter', 'FLT_A', 4),
                                 ('Hauptplatine', 'main', 'MAIN', 1)):
        cnt = sum(1 for r in comps
                  if split.mod_of_ref(r) == mod and not is_panel(r))
        w("| %s | `boards/%s/` | **%dx** | %d |" % (name, proj, qty, cnt))
    w("")
    w("Die drei Oszillatoren sind elektrisch identisch, ebenso die vier Filter.")
    w("Darum gibt es nur **drei Layouts**. Im Gesamtschaltplan heissen sie 1xx / 2xx / 3xx")
    w("(Oszillatoren) und 4xx / 5xx / 6xx / 7xx (Filter A bis D); auf der einzelnen")
    w("Platine stehen immer die Nummern der ersten Gruppe, also R101, U103, J_12 usw.")
    w("")

    w("## 2. Kabel zwischen den Platinen")
    w("")
    w("| Von | Nach | Pins | Signal |")
    w("|---|---|---|---|")
    for a, b, n, s in (
            ("Hauptplatine J810", "Oszillator 1  J_10", 4, "+12 V / GND / -12 V / +5 V"),
            ("Oszillator 1 J_11", "Oszillator 2  J_10", 4, "Versorgung durchgeschleift"),
            ("Oszillator 2 J_11", "Oszillator 3  J_10", 4, "Versorgung durchgeschleift"),
            ("Hauptplatine J811", "Filter A  J_10", 3, "+12 V / GND / -12 V"),
            ("Filter A J_11", "Filter B  J_10", 3, "Versorgung durchgeschleift"),
            ("Filter B J_11", "Filter C  J_10", 3, "Versorgung durchgeschleift"),
            ("Filter C J_11", "Filter D  J_10", 3, "Versorgung durchgeschleift"),
            ("Oszillator 1 J_15", "Hauptplatine J813", 2, "OSC1_OUT"),
            ("Oszillator 2 J_15", "Hauptplatine J814", 2, "OSC2_OUT"),
            ("Oszillator 3 J_15", "Hauptplatine J815", 2, "OSC3_OUT"),
            ("Hauptplatine J816", "Filter A  J_13", 2, "MIX_OUT, Mixer in Filter A"),
            ("Filter A J_14", "Filter B  J_13", 2, "FILT_A_OUT"),
            ("Filter B J_14", "Hauptplatine J817", 2, "FILT_B_OUT, Filter B in den LM386"),
            ("Filter C J_13 / J_14", "Klinkenbuchsen J_01 / J_02", 2, "Solo-Filter 1"),
            ("Filter D J_13 / J_14", "Klinkenbuchsen J_01 / J_02", 2, "Solo-Filter 2")):
        w("| %s | %s | %d | %s |" % (a, b, n, s))
    w("")
    w("Alle Steckverbinder sind **JST-XH 2,50 mm**, vertikal, gerade. Die Polzahl")
    w("unterscheidet sich je Funktion, damit sich Versorgung und Audio nicht")
    w("vertauschen lassen.")
    w("")

    w("## 3. Verdrahtung Platine zum Bedienfeld")
    w("")
    w("Eine Ader pro Loetfahne. Die Tabellen gelten fuer **jede** Platine dieses Typs.")
    w("")
    for title, conns, note in (
            ("Oszillator-Platine (3x gleich)", connspec.osc(1),
             "Fuer Oszillator 2 und 3 gilt dieselbe Tabelle."),
            ("Filter-Platine (4x gleich)", connspec.flt(4),
             "Bei Filter A und B gehen J_13 / J_14 an die Nachbarplatinen, "
             "bei Filter C und D an die Klinkenbuchsen."),
            ("Hauptplatine (1x)", connspec.main(), "")):
        w("### %s" % title)
        w("")
        for ref, npins, val, netnames in conns:
            gref = generic(ref)
            dl = conndest.all_dests()[ref]
            w("**%s** - %s (%d-polig)" % (gref, val, npins))
            w("")
            if all(d is None for d in dl):
                w("| Pin | Netz | Kabel geht an |")
                w("|---|---|---|")
                for i, n in enumerate(netnames, 1):
                    w("| %d | %s | %s |" % (i, n, CABLE.get((ref, i), "Nachbarplatine")))
                w("")
                continue
            w("| Pin | Netz | Loetfahne | Bedienelement |")
            w("|---|---|---|---|")
            for i, (n, dst) in enumerate(zip(netnames, dl), 1):
                if dst is None:
                    w("| %d | %s | %s | |" % (i, n, CABLE.get((ref, i), "Nachbarplatine")))
                    continue
                r, pin = dst.split('.')
                part = comps[r]['part'] if r in comps else from_sch.get(r)
                w("| %d | %s | **%s** %s | %s |"
                  % (i, n, generic(r), conndest.lug(part, pin), control_name(r)))
            w("")
        if note:
            w(note)
            w("")

    w("## 4. Bedienelemente - Einkaufsliste Frontplatte")
    w("")
    w("| Anzahl | Bauteil | Wert / Typ | Funktion |")
    w("|---|---|---|---|")
    for row in (
            (3, "Doppel-Potentiometer", "1M linear, 2-fach-Gleichlauf", "Tonhoehe je Oszillator (RV_01 + RV_02)"),
            (3, "Potentiometer", "100k linear", "Drive (RV_03)"),
            (3, "Potentiometer", "100k logarithmisch", "Distortion-Pegel (RV_04)"),
            (3, "Potentiometer", "10k logarithmisch", "Amplitude (RV_05)"),
            (3, "Drehschalter", "1-polig, 4 Stellungen", "Wellenform (SW_01)"),
            (9, "Kippschalter", "SPDT, ein-ein", "weich/hart, Distortion, Solo-Filter"),
            (4, "Doppel-Potentiometer", "100k linear, 2-fach-Gleichlauf", "Filter-Cutoff (RV_01 + RV_02)"),
            (4, "Potentiometer", "47k linear", "Filter-Resonanz (RV_03)"),
            (4, "Drehschalter", "1-polig, 5 Stellungen", "Filterwahl (SW_01)"),
            (3, "Potentiometer", "10k logarithmisch", "Kanalpegel Mixer (RV801/802/803)"),
            (1, "Potentiometer", "10k logarithmisch", "Master-Lautstaerke (RV901)"),
            (13, "Klinkenbuchse 6,3 mm mono", "", "3x Send, 3x Return, 3x Ausgang, 2x Filter-In, 2x Filter-Out")):
        w("| %d | %s | %s | %s |" % row)
    w("")
    w("**Rheostat-Verdrahtung:** RV_01 bis RV_04 im Oszillator und RV_01 bis RV_03 im")
    w("Filter haengen nur mit zwei Anschluessen in der Schaltung (Schleifer + ein Ende).")
    w("Den **dritten, unbenutzten Aussenanschluss immer mit dem Schleifer verbinden** -")
    w("dann bleibt der Widerstand definiert, falls der Schleifer einmal Kontaktprobleme")
    w("bekommt, statt die Stufe stumm oder instabil zu machen.")
    w("")
    w("**Wichtig:** RV_01 und RV_02 sind in jedem Oszillator *und* in jedem Filter")
    w("**ein einziges Doppelpoti**, nicht zwei getrennte. Im Schaltplan stehen sie als")
    w("zwei Symbole, weil die beiden Ebenen an verschiedenen Stellen der Schaltung")
    w("haengen. Beim Einkauf also 3 + 4 = 7 Doppelpotis.")
    w("")

    w("## 5. Hinweise zum Bestuecken")
    w("")
    w("| Bauteil | Hinweis |")
    w("|---|---|")
    w("| Widerstaende **Oszillator-Platine** | stehend montiert, Rastermass 2,54 mm - einen Draht um 180 Grad zurueckbiegen. Nur so passen 27 Widerstaende neben die vier ICs, ohne dass die Leiterbahnen keinen Platz mehr haben. |")
    w("| Widerstaende **Filter- und Hauptplatine** | liegend, Rastermass 7,62 mm |")
    w("| BC547 und 78L05 | Beine auf 2,54 mm spreizen (TO-92 Inline Wide). Bei 1,27 mm waere der Abstand der Loetaugen kleiner als die Entwurfsregel erlaubt. |")
    w("| TL074 und LM386 | Fassung vorgesehen - ICs also nicht direkt einloeten, sondern stecken |")
    w("| OPA4196 / OPA1662 / 74LVC2G17 | SMD. OPA4196 im SOIC-14 (1,27 mm Raster) statt TSSOP - deutlich leichter von Hand zu loeten. |")
    w("| Masse-Pins an Versorgungssteckern und Abblockkondensatoren | direkt mit der Massflaeche verbunden (kein Thermal). Dafuer den Loetkolben etwas heisser stellen und laenger halten. |")
    w("| Sicherungen F901/F902 | 5 x 20 mm Halteclips, je zwei Loetfahnen pro Clip - beide loeten |")
    w("| Polung | Elkos und Dioden sind auf dem Bestueckungsdruck markiert; C904 und C805 sind die grossen liegenden Elkos |")
    w("")

    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    return len(L)


if __name__ == '__main__':
    n = build(sys.argv[1], sys.argv[2])
    print("wrote %s (%d lines)" % (sys.argv[2], n))
