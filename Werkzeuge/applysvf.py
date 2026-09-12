import sys, os, re
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from schedit import Sch
import svfgen
from svfgen import sym, pwrsym, wire, label, junction, textnote
from svfmodule import build
F = r'C:\Users\timod\Documents\Claude\SynthesizerFinal.kicad_sch'
s = Sch(F)

BOX = {4: (28, 272, 632, 756), 5: (272, 470, 632, 756),
       6: (16, 254, 754, 900), 7: (254, 490, 754, 900)}
def inb(p, b): return b[0] < p[0] < b[1] and b[2] < p[1] < b[3]

# ---------- 1. delete symbols inside the boxes ----------
kill = []
for a, b, r in s._blocks():
    at = [l for l in s.lines[a:b+1] if l.startswith('\t\t(at ')]
    if not at: continue
    x, y = [float(v) for v in at[0].strip()[4:-1].split()[:2]]
    if any(inb((x, y), bb) for bb in BOX.values()):
        kill.append((a, b, r))
for a, b, r in sorted(kill, reverse=True):
    del s.lines[a:b+1]
print(f'deleted {len(kill)} symbols')

# ---------- 2. delete wires touching the boxes ----------
n = 0
while True:
    hit = None
    for a, b, w0, w1 in s.wires():
        if any(inb(w0, bb) or inb(w1, bb) for bb in BOX.values()):
            hit = (a, b); break
    if not hit: break
    del s.lines[hit[0]:hit[1]+1]; n += 1
print(f'deleted {n} wires')

# ---------- 3. delete labels / texts / junctions inside the boxes ----------
def del_kind(kind, atoff):
    cnt = 0
    while True:
        found = None
        for i, l in enumerate(s.lines):
            if not l.startswith(f'\t({kind} '): continue
            mm = re.search(r'\(at ([-\d.]+) ([-\d.]+)', s.lines[i+atoff])
            if not mm: continue
            p = (float(mm.group(1)), float(mm.group(2)))
            if any(inb(p, bb) for bb in BOX.values()):
                d = 0; j = i
                while j < len(s.lines):
                    d += s.lines[j].count('(') - s.lines[j].count(')')
                    if d == 0 and j > i: break
                    j += 1
                found = (i, j); break
        if not found: break
        del s.lines[found[0]:found[1]+1]; cnt += 1
    return cnt
print('deleted labels:', del_kind('label', 1), ' texts:', del_kind('text', 2), ' junctions:', del_kind('junction', 1))

# ---------- 4. retarget the surviving power units: ADA4625 unit 3 -> OPA4196 unit 5 ----------
for a, b, r in s._blocks():
    if r not in ('U401', 'U501', 'U601', 'U701'): continue
    blk = s.lines[a:b+1]
    if not any('(unit 3)' in l for l in blk): continue
    for k in range(a, b+1):
        s.lines[k] = s.lines[k].replace('Amplifier_Operational:ADA4625-2ARDZ', 'Amplifier_Operational:OPA4196xPW')
        s.lines[k] = s.lines[k].replace('(unit 3)', '(unit 5)')
        if '(property "Value" "' in s.lines[k]:
            s.lines[k] = re.sub(r'(\(property "Value" ")[^"]*(")', r'\g<1>OPA4196\g<2>', s.lines[k])
    print(f'  {r}: power unit -> OPA4196 unit 5')

# ---------- 5. emit the four modules ----------
MOD = [
 (4, 31.75,  641.35, "MIX_OUT",    "FILT_A_OUT", None,  "FILTER A  (Hauptweg 1 von 2)  -  State-Variable-Filter"),
 (5, 266.70, 641.35, "FILT_A_OUT", "FILT_B_OUT", None,  "FILTER B  (Hauptweg 2 von 2)  -  State-Variable-Filter"),
 (6, 20.32,  760.73, "F6_IN",      "F6_OUT",     "601", "FILTER C  (Solo-Filter 1)  -  State-Variable-Filter"),
 (7, 256.54, 760.73, "F7_IN",      "F7_OUT",     "701", "FILTER D  (Solo-Filter 2)  -  State-Variable-Filter"),
]
out = []
for n_, X0, Y0, inl, outl, jacks, title in MOD:
    lines, _ = build(n_, X0, Y0, inl, outl, 10, title)
    out += lines
    if jacks:
        ja, jb = f"J{jacks}", f"J{int(jacks)+1}"
        for ref, nm, yoff, lab in ((ja, "Filter-In", 45.72, inl), (jb, "Filter-Out", 66.04, outl)):
            jx, jy = X0 + 2.54, Y0 + yoff
            out += sym("Connector_Audio:AudioJack2", ref, nm, jx, jy, 0, 1, jx - 7.62, jy - 6.35, jx - 7.62, jy - 3.81)
            out += wire(jx + 5.08, jy, jx + 12.7, jy) + label(lab, jx + 12.7, jy)
            out += wire(jx + 5.08, jy - 2.54, jx + 15.24, jy - 2.54)
            out += pwrsym(f"#PWR{n_}0{'5' if ref==ja else '6'}0", "GNDREF", jx + 15.24, jy - 2.54)
# restore the FILT_B_OUT feed to C901 (its wire survived outside the box)
out += label("FILT_B_OUT", 490.22, 669.29)
s.append_raw(out)
s.save(F)
print(f'inserted {len(out)} lines for 4 SVF modules')
