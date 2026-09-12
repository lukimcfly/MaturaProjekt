"""Board-boundary connector specification for the modular synth build."""

# nets that currently have auto-generated names and must be labelled
# (representative pin) -> label
def renames():
    out = {}
    for n in (1, 2, 3):
        out[(f"SW{n}04", "1")]  = f"O{n}_SEND"
        out[(f"RV{n}01", "2")]  = f"O{n}_PITCH"
        out[(f"RV{n}02", "1")]  = f"O{n}_FGF_A"
        out[(f"RV{n}02", "2")]  = f"O{n}_FGF_B"
        out[(f"RV{n}04", "2")]  = f"O{n}_MKUP_A"
        out[(f"RV{n}05", "1")]  = f"O{n}_LVL_A"
        out[(f"RV{n}05", "2")]  = f"O{n}_LVL_W"
        out[(f"SW{n}01", "5")]  = f"O{n}_WSEL"
    for m in (4, 5, 6, 7):
        out[(f"RV{m}01", "2")]  = f"F{m}_T1W"
        out[(f"RV{m}02", "2")]  = f"F{m}_T2W"
        out[(f"RV{m}03", "2")]  = f"F{m}_RESW"
    for i, p in ((1, "801"), (2, "802"), (3, "803")):
        out[(f"RV{p}", "1")] = f"M_LVL{i}_A"
        out[(f"RV{p}", "2")] = f"M_LVL{i}_W"
    out[("RV901", "1")] = "M_VOL_A"
    out[("RV901", "2")] = "M_VOL_W"
    return out

GND = "GNDREF"

def osc(n):
    """Connectors for one oscillator board. (ref, npins, value, [nets by pin])"""
    return [
        (f"J{n}10", 4,  "Versorgung ein",    ["+12V", GND, "-12V", "+5V"]),
        (f"J{n}11", 4,  "Versorgung weiter", ["+12V", GND, "-12V", "+5V"]),
        # Pin order chosen so the eleven wires leave the connector in the same
        # left-to-right order as the parts they feed: that removed every crossing
        # pair at the board's most congested edge.
        (f"J{n}12", 11, "Panel Potis",
            [f"O{n}_CLIP", f"O{n}_MKUP_A", f"O{n}_AINV", f"O{n}_DRIVE", "+5V",
             f"O{n}_PITCH", f"O{n}_FGF_A", GND, f"O{n}_FGF_B", f"O{n}_LVL_A",
             f"O{n}_LVL_W"]),
        (f"J{n}13", 14, "Panel Schalter",
            [f"O{n}_SOFT", f"OSC{n}_DIST", f"O{n}_WSEL", f"OSC{n}_WAVE", f"O{n}_AINV",
             f"O{n}_MKUP", f"O{n}_DRIVE", f"OSC{n}_SAW", f"OSC{n}_SQ", f"OSC{n}_TRI",
             f"OSC{n}_DIST", f"OSC{n}_SIG", f"OSC{n}_SINE", f"O{n}_SEND"]),
        (f"J{n}14", 6,  "Panel Buchsen",
            [f"O{n}_SEND", GND, f"OSC{n}_SIG", GND, f"OSC{n}_OUT", GND]),
        (f"J{n}15", 2,  "Audio aus -> Mixer", [f"OSC{n}_OUT", GND]),
    ]

FLT_IO = {4: ("MIX_OUT", "FILT_A_OUT"), 5: ("FILT_A_OUT", "FILT_B_OUT"),
          6: ("F6_IN", "F6_OUT"),       7: ("F7_IN", "F7_OUT")}

def flt(m):
    fin, fout = FLT_IO[m]
    return [
        (f"J{m}10", 3,  "Versorgung ein",    ["+12V", GND, "-12V"]),
        (f"J{m}11", 3,  "Versorgung weiter", ["+12V", GND, "-12V"]),
        (f"J{m}12", 12, "Panel Poti + Wahlschalter",
            [f"F{m}_HP", f"F{m}_T1W", f"F{m}_BP", f"F{m}_T2W", f"F{m}_BP", f"F{m}_RESW",
             f"F{m}_LP", f"F{m}_HP", f"F{m}_BP", f"F{m}_NOTCH", fin, fout]),
        (f"J{m}13", 2,  "Audio ein",  [fin, GND]),
        (f"J{m}14", 2,  "Audio aus",  [fout, GND]),
    ]

def main():
    return [
        ("J810", 4,  "Versorgung -> Oszillatoren", ["+12V", GND, "-12V", "+5V"]),
        ("J811", 3,  "Versorgung -> Filter",       ["+12V", GND, "-12V"]),
        ("J812", 12, "Panel Potis",
            ["M_LVL1_A", "M_LVL1_W", GND, "M_LVL2_A", "M_LVL2_W", GND,
             "M_LVL3_A", "M_LVL3_W", GND, "M_VOL_A", "M_VOL_W", GND]),
        ("J813", 2, "OSC 1 ein", ["OSC1_OUT", GND]),
        ("J814", 2, "OSC 2 ein", ["OSC2_OUT", GND]),
        ("J815", 2, "OSC 3 ein", ["OSC3_OUT", GND]),
        ("J816", 2, "-> Filter A", ["MIX_OUT", GND]),
        ("J817", 2, "Filter B ->", ["FILT_B_OUT", GND]),
    ]

COLUMNS = [("OSC 1", osc(1)), ("OSC 2", osc(2)), ("OSC 3", osc(3)),
           ("Filter A", flt(4)), ("Filter B", flt(5)),
           ("Filter C", flt(6)), ("Filter D", flt(7)),
           ("Mixer / Endstufe", main())]
