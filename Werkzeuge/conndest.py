"""Which panel lug each connector pin was created for.

connspec says *which net* a connector pin joins; this says *which physical lug*
the wire goes to.  Both are checked against the netlist by mkdocs, so a mistake
here shows up as an error rather than as a wrong wiring table.

BOARD means the pin goes to another board over a cable, not to the panel.
"""
BOARD = None


def osc(n):
    d = {}
    for ref in (f"J{n}10", f"J{n}11"):
        d[ref] = [BOARD] * 4
    d[f"J{n}12"] = [f"RV{n}04.1", f"RV{n}04.2", f"RV{n}03.1", f"RV{n}03.2",
                    f"RV{n}01.1", f"RV{n}01.2", f"RV{n}02.1", f"RV{n}05.3",
                    f"RV{n}02.2", f"RV{n}05.1", f"RV{n}05.2"]
    d[f"J{n}13"] = [f"SW{n}02.2", f"SW{n}03.2", f"SW{n}01.5", f"SW{n}03.3",
                    f"SW{n}02.1", f"SW{n}03.1", f"SW{n}02.3", f"SW{n}01.4",
                    f"SW{n}01.3", f"SW{n}01.2", f"SW{n}04.2", f"SW{n}04.3",
                    f"SW{n}01.1", f"SW{n}04.1"]
    d[f"J{n}14"] = [f"J{n}01.T", f"J{n}01.S", f"J{n}02.T", f"J{n}02.S",
                    f"J{n}03.T", f"J{n}03.S"]
    d[f"J{n}15"] = [BOARD, BOARD]
    return d


def flt(m):
    d = {}
    for ref in (f"J{m}10", f"J{m}11"):
        d[ref] = [BOARD] * 3
    d[f"J{m}12"] = [f"RV{m}01.1", f"RV{m}01.2", f"RV{m}02.1", f"RV{m}02.2",
                    f"RV{m}03.1", f"RV{m}03.2",
                    f"SW{m}01.1", f"SW{m}01.2", f"SW{m}01.3", f"SW{m}01.4",
                    f"SW{m}01.5", f"SW{m}01.6"]
    d[f"J{m}13"] = [BOARD, BOARD]
    d[f"J{m}14"] = [BOARD, BOARD]
    return d


def main():
    d = {"J810": [BOARD] * 4, "J811": [BOARD] * 3}
    d["J812"] = ["RV801.1", "RV801.2", "RV801.3",
                 "RV802.1", "RV802.2", "RV802.3",
                 "RV803.1", "RV803.2", "RV803.3",
                 "RV901.1", "RV901.2", "RV901.3"]
    for r in ("J813", "J814", "J815", "J816", "J817"):
        d[r] = [BOARD, BOARD]
    return d


def all_dests():
    d = {}
    for n in (1, 2, 3):
        d.update(osc(n))
    for m in (4, 5, 6, 7):
        d.update(flt(m))
    d.update(main())
    return d


# how to name a lug, by the symbol's library part
LUGNAME = {
    'R_Potentiometer_US': {'1': 'Lug 1 (CW)', '2': 'Lug 2 (Schleifer)', '3': 'Lug 3 (CCW)'},
    'R_Variable_US':      {'1': 'Lug 1', '2': 'Lug 2 (Schleifer)'},
    'AudioJack2':         {'T': 'Tip (Signal)', 'S': 'Sleeve (Masse)'},
    'SW_Nidec_CAS-120A1': {'1': 'Pin 1 (Stellung A)', '2': 'Pin 2 (Mitte/Common)',
                           '3': 'Pin 3 (Stellung B)'},
    'SW_Rotary_1x4_MP':   {'1': 'Pos 1', '2': 'Pos 2', '3': 'Pos 3', '4': 'Pos 4',
                           '5': 'Common (Schleifer)'},
    'SW_Rotary_1x5_MP':   {'1': 'Pos 1', '2': 'Pos 2', '3': 'Pos 3', '4': 'Pos 4',
                           '5': 'Pos 5', '6': 'Common (Schleifer)'},
}


def lug(part, pin):
    return LUGNAME.get(part, {}).get(str(pin), 'Pin ' + str(pin))
