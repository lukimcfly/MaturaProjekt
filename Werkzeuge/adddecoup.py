"""Add local decoupling (100nF per IC supply pin) + per-module bulk caps."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schedit import Sch
from svfgen import sym, pwrsym, wire, textnote
import svfgen

svfgen._c[0] = 700000

CER  = "Device:C"
POL  = "Device:C_Polarized_US"

# (ref, value, lib, rail) grouped per module column
def osc(n):
    return [ (f"C{n}05", "100nF",   CER, "+12V"),   # U{n}01 TL074  pin4
             (f"C{n}06", "100nF",   CER, "-12V"),   # U{n}01 TL074  pin11
             (f"C{n}07", "100nF",   CER, "+5V"),    # U{n}02 74LVC2G17 pin5
             (f"C{n}08", "100nF",   CER, "+12V"),   # U{n}03 OPA4196 pin4
             (f"C{n}09", "100nF",   CER, "-12V"),   # U{n}03 OPA4196 pin11
             (f"C{n}10", "100nF",   CER, "+12V"),   # U{n}04 OPA1662 pin8
             (f"C{n}11", "100nF",   CER, "-12V"),   # U{n}04 OPA1662 pin4
             (f"C{n}12", "10uF/25V", POL, "+12V"),  # board bulk
             (f"C{n}13", "10uF/25V", POL, "-12V") ]
def flt(m):
    return [ (f"C{m}03", "100nF",   CER, "+12V"),   # U{m}01 OPA4196 pin4
             (f"C{m}04", "100nF",   CER, "-12V"),   # U{m}01 OPA4196 pin11
             (f"C{m}05", "10uF/25V", POL, "+12V"),
             (f"C{m}06", "10uF/25V", POL, "-12V") ]

COLS = [("OSC 1", osc(1)), ("OSC 2", osc(2)), ("OSC 3", osc(3)),
        ("Filter A / B", flt(4) + flt(5)), ("Filter C / D", flt(6) + flt(7))]

X0, Y0, DX, DY = 688.34, 365.76, 38.1, 26.67   # all multiples of 1.27 mm (KiCad grid)
assert all(abs(v/1.27 - round(v/1.27)) < 1e-9 for v in (X0, Y0, DX, DY)), 'off-grid'

def build():
    out = []
    pw = [9500]
    def nextpwr():
        pw[0] += 1
        return f"#PWR{pw[0]}"
    for ci, (title, items) in enumerate(COLS):
        cx = X0 + ci * DX
        out += textnote(f"Entkopplung {title}", cx - 7.62, Y0 - 12.7)
        for ri, (ref, val, lib, rail) in enumerate(items):
            cy = Y0 + ri * DY
            out += sym(lib, ref, val, cx, cy, 0, 1,
                       cx + 2.54, cy - 2.54, cx + 2.54, cy + 2.54)
            top, bot = (rail, "GNDREF") if rail != "-12V" else ("GNDREF", "-12V")
            out += wire(cx, cy - 3.81, cx, cy - 10.16)
            out += pwrsym(nextpwr(), top, cx, cy - 10.16, 0)
            out += wire(cx, cy + 3.81, cx, cy + 10.16)
            out += pwrsym(nextpwr(), bot, cx, cy + 10.16, 0 if bot == "GNDREF" else 180)
    return out

if __name__ == "__main__":
    path = sys.argv[1]
    s = Sch(path)
    existing = set(s.refs())
    new = [r for _, items in COLS for (r, *_ ) in items]
    dup = [r for r in new if r in existing]
    assert not dup, f"reference collision: {dup}"
    s.append_raw(build())
    s.save(path)
    print(f"added {len(new)} decoupling caps: "
          f"{sum(1 for _,i in COLS for x in i if x[1]=='100nF')} x 100nF, "
          f"{sum(1 for _,i in COLS for x in i if x[1].startswith('10uF'))} x 10uF bulk")
