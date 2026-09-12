"""Derive the three board projects (oscillator, filter, main) from the master schematic."""
import sys, os, re, shutil, subprocess, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexp, split, mkproject, svfgen
from svfgen import pwrsym, wire

KICAD = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'

# system-level notes that proximity mis-assigns; force them onto MAIN
TEXT_OWNER = {
    "Uebernommen aus der Falstad-Simulation": "MAIN",
    "STROMVERSORGUNG DER OPERATIONSVERSTAERKER": "MAIN",
    "VERSORGUNG, ABBLOCKUNG UND +5 V": "MAIN",
    "SIGNALWEG": "MAIN",
}

BOARDS = {
    # name        module   title                                       rails needing a PWR_FLAG
    'osc':    ('OSC1',  'Oszillator-Platine (3x bestuecken)',  ['+12V', '-12V', '+5V', 'GNDREF']),
    'filter': ('FLT_A', 'Filter-Platine (4x bestuecken)',      ['+12V', '-12V', 'GNDREF']),
    'main':   ('MAIN',  'Hauptplatine - Mixer, LM386, Versorgung', []),
}

def flags(rails, x0, y0):
    """PWR_FLAG + rail symbol pairs so ERC sees each incoming rail as driven."""
    out = []
    for i, rail in enumerate(rails):
        x = x0 + i * 20.32
        out += pwrsym(f"#PWR98{i+1:02d}", rail, x, y0, 0 if rail != '-12V' else 180)
        out += wire(x, y0, x, y0 + 8.89)
        out += pwrsym(f"#FLG88{i+1}", "PWR_FLAG", x, y0 + 8.89, 180)
    return out

def build(master, outroot):
    made = []
    for name, (mod, title, rails) in BOARDS.items():
        d = os.path.join(outroot, name)
        os.makedirs(d, exist_ok=True)
        sch = os.path.join(d, name + '.kicad_sch')
        svfgen._c[0] = 600000 + 1000 * len(made)
        extra = [sexp.dump(sexp.parse('(' + ' '.join([]) + ')'), 1)] if False else None
        extra_lines = flags(rails, 900.43, 699.77) if rails else None
        kept, drop = split.derive(master, mod, sch, title=title,
                                  extra=extra_lines, text_owner=TEXT_OWNER)
        mkproject.make(sch, title=title)
        made.append((name, mod, sch, kept, drop))
    return made

if __name__ == '__main__':
    for name, mod, sch, kept, drop in build(sys.argv[1], sys.argv[2]):
        print(f"{name:7s} <- {mod:6s} {sch}")
        print(f"         kept {dict(kept)}")
