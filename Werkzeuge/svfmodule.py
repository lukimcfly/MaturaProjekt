"""Build one complete state-variable filter module."""
from svfgen import sym, pwrsym, wire, label, junction, textnote
import collections

OPA = "Amplifier_Operational:OPA4196xPW"
R   = "Device:R_US"
RV  = "Device:R_Variable_US"
C   = "Device:C"
SW  = "Switch:SW_Rotary_1x5_MP"
GND = "GNDREF"

def build(n, X0, Y0, in_label, out_label, pwr_idx0, title):
    """n = 4..7 (reference prefix digit). Returns (lines, wires_list)."""
    out, wires = [], []
    pw = [pwr_idx0]
    def gnd(x, y, rot=0):
        pw[0] += 1
        return pwrsym(f"#PWR{n}{pw[0]:03d}", GND, x, y, rot)
    def W(x1, y1, x2, y2):
        wires.append(((x1, y1), (x2, y2)))
        return wire(x1, y1, x2, y2)

    HP, BP, LP, NT = f"F{n}_HP", f"F{n}_BP", f"F{n}_LP", f"F{n}_NOTCH"
    ax1, ay1 = X0 + 63.5,  Y0 + 25.4
    ax2, ay2 = X0 + 152.4, Y0 + 25.4
    ax3, ay3 = X0 + 63.5,  Y0 + 82.55
    ax4, ay4 = X0 + 152.4, Y0 + 82.55
    sx,  sy  = X0 + 201.93, Y0 + 53.34

    # ---------------- A1: summing amp -> HP ----------------
    out += sym(OPA, f"U{n}01", "OPA4196", ax1, ay1, 0, 1, ax1 - 2.54, ay1 - 11.43, ax1 - 2.54, ay1 - 8.89)
    out += sym(R, f"R{n}04", "10k", ax1 - 19.05, ay1 + 2.54, 90, 1, ax1 - 19.05, ay1 - 1.27, ax1 - 19.05, ay1 + 6.35)
    out += W(ax1 - 15.24, ay1 + 2.54, ax1 - 7.62, ay1 + 2.54)
    out += W(ax1 - 22.86, ay1 + 2.54, ax1 - 30.48, ay1 + 2.54) + label(in_label, ax1 - 30.48, ay1 + 2.54)
    out += sym(R, f"R{n}05", "10k", ax1 - 19.05, ay1 + 12.7, 90, 1, ax1 - 19.05, ay1 + 8.89, ax1 - 19.05, ay1 + 16.51)
    out += W(ax1 - 15.24, ay1 + 12.7, ax1 - 7.62, ay1 + 12.7)
    out += W(ax1 - 7.62, ay1 + 12.7, ax1 - 7.62, ay1 + 2.54)
    out += W(ax1 - 22.86, ay1 + 12.7, ax1 - 30.48, ay1 + 12.7) + label(LP, ax1 - 30.48, ay1 + 12.7)
    out += sym(R, f"R{n}06", "10k", ax1 - 19.05, ay1 + 22.86, 90, 1, ax1 - 19.05, ay1 + 19.05, ax1 - 19.05, ay1 + 26.67)
    out += W(ax1 - 15.24, ay1 + 22.86, ax1 - 7.62, ay1 + 22.86)
    out += W(ax1 - 7.62, ay1 + 22.86, ax1 - 7.62, ay1 + 12.7)
    out += W(ax1 - 22.86, ay1 + 22.86, ax1 - 30.48, ay1 + 22.86) + label(HP, ax1 - 30.48, ay1 + 22.86)
    # Q network on the + input
    out += sym(R, f"R{n}03", "6.8k", ax1 - 19.05, ay1 - 2.54, 90, 1, ax1 - 19.05, ay1 - 6.35, ax1 - 19.05, ay1 - 1.27)
    out += W(ax1 - 15.24, ay1 - 2.54, ax1 - 7.62, ay1 - 2.54)
    out += W(ax1 - 22.86, ay1 - 2.54, ax1 - 26.67, ay1 - 2.54)
    out += sym(RV, f"RV{n}03", "47k lin", ax1 - 30.48, ay1 - 2.54, 90, 1, ax1 - 30.48, ay1 - 6.35, ax1 - 30.48, ay1 - 1.27)
    out += W(ax1 - 34.29, ay1 - 2.54, ax1 - 40.64, ay1 - 2.54) + label(BP, ax1 - 40.64, ay1 - 2.54)
    out += sym(R, f"R{n}07", "6.8k", ax1 - 7.62, ay1 - 11.43, 0, 1, ax1 - 5.08, ay1 - 12.7, ax1 - 5.08, ay1 - 10.16)
    out += W(ax1 - 7.62, ay1 - 7.62, ax1 - 7.62, ay1 - 2.54)
    out += gnd(ax1 - 7.62, ay1 - 15.24, 180)
    out += W(ax1 + 7.62, ay1, ax1 + 16.51, ay1) + label(HP, ax1 + 16.51, ay1)

    # ---------------- A2 / A3: integrators ----------------
    for (ax, ay, unit, rin, rvin, cap, src, dst) in (
            (ax2, ay2, 2, f"R{n}01", f"RV{n}01", f"C{n}01", HP, BP),
            (ax3, ay3, 3, f"R{n}02", f"RV{n}02", f"C{n}02", BP, LP)):
        out += sym(OPA, f"U{n}01", "OPA4196", ax, ay, 0, unit, ax - 2.54, ay - 11.43, ax - 2.54, ay - 8.89)
        out += sym(R, rin, "1k", ax - 19.05, ay + 2.54, 90, 1, ax - 19.05, ay - 1.27, ax - 19.05, ay + 6.35)
        out += W(ax - 15.24, ay + 2.54, ax - 7.62, ay + 2.54)
        out += W(ax - 22.86, ay + 2.54, ax - 26.67, ay + 2.54)
        out += sym(RV, rvin, "100k lin", ax - 30.48, ay + 2.54, 90, 1, ax - 30.48, ay - 1.27, ax - 30.48, ay + 6.35)
        out += W(ax - 34.29, ay + 2.54, ax - 40.64, ay + 2.54) + label(src, ax - 40.64, ay + 2.54)
        out += W(ax - 7.62, ay - 2.54, ax - 7.62, ay - 8.89) + gnd(ax - 7.62, ay - 8.89, 180)
        # integrator capacitor, routed around the left so it never crosses the + input
        out += sym(C, cap, "15nF", ax, ay - 19.05, 90, 1, ax - 1.27, ay - 22.86, ax - 1.27, ay - 16.51)
        out += W(ax + 3.81, ay - 19.05, ax + 7.62, ay - 19.05)
        out += W(ax + 7.62, ay - 19.05, ax + 7.62, ay)
        out += W(ax - 3.81, ay - 19.05, ax - 45.72, ay - 19.05)
        out += W(ax - 45.72, ay - 19.05, ax - 45.72, ay + 8.89)
        out += W(ax - 45.72, ay + 8.89, ax - 7.62, ay + 8.89)
        out += W(ax - 7.62, ay + 8.89, ax - 7.62, ay + 2.54)
        out += W(ax + 7.62, ay, ax + 16.51, ay) + label(dst, ax + 16.51, ay)

    # ---------------- A4: notch summer = -(HP + LP) ----------------
    out += sym(OPA, f"U{n}01", "OPA4196", ax4, ay4, 0, 4, ax4 - 2.54, ay4 - 11.43, ax4 - 2.54, ay4 - 8.89)
    out += sym(R, f"R{n}08", "10k", ax4 - 19.05, ay4 + 2.54, 90, 1, ax4 - 19.05, ay4 - 1.27, ax4 - 19.05, ay4 + 6.35)
    out += W(ax4 - 15.24, ay4 + 2.54, ax4 - 7.62, ay4 + 2.54)
    out += W(ax4 - 22.86, ay4 + 2.54, ax4 - 30.48, ay4 + 2.54) + label(HP, ax4 - 30.48, ay4 + 2.54)
    out += sym(R, f"R{n}09", "10k", ax4 - 19.05, ay4 + 12.7, 90, 1, ax4 - 19.05, ay4 + 8.89, ax4 - 19.05, ay4 + 16.51)
    out += W(ax4 - 15.24, ay4 + 12.7, ax4 - 7.62, ay4 + 12.7)
    out += W(ax4 - 7.62, ay4 + 12.7, ax4 - 7.62, ay4 + 2.54)
    out += W(ax4 - 22.86, ay4 + 12.7, ax4 - 30.48, ay4 + 12.7) + label(LP, ax4 - 30.48, ay4 + 12.7)
    out += W(ax4 - 7.62, ay4 - 2.54, ax4 - 7.62, ay4 - 8.89) + gnd(ax4 - 7.62, ay4 - 8.89, 180)
    out += sym(R, f"R{n}10", "10k", ax4, ay4 - 19.05, 90, 1, ax4 - 1.27, ay4 - 22.86, ax4 - 1.27, ay4 - 16.51)
    out += W(ax4 + 3.81, ay4 - 19.05, ax4 + 7.62, ay4 - 19.05)
    out += W(ax4 + 7.62, ay4 - 19.05, ax4 + 7.62, ay4)
    out += W(ax4 - 3.81, ay4 - 19.05, ax4 - 45.72, ay4 - 19.05)
    out += W(ax4 - 45.72, ay4 - 19.05, ax4 - 45.72, ay4 + 19.05)
    out += W(ax4 - 45.72, ay4 + 19.05, ax4 - 7.62, ay4 + 19.05)
    out += W(ax4 - 7.62, ay4 + 19.05, ax4 - 7.62, ay4 + 12.7)
    out += W(ax4 + 7.62, ay4, ax4 + 16.51, ay4) + label(NT, ax4 + 16.51, ay4)

    # ---------------- output selector ----------------
    out += sym(SW, f"SW{n}01", "Filterwahl", sx, sy, 0, 1, sx - 2.54, sy - 12.7, sx - 2.54, sy - 10.16)
    for i, lb in enumerate((LP, HP, BP, NT, in_label)):
        py = sy - 5.08 + i * 2.54
        out += W(sx + 7.62, py, sx + 16.51, py) + label(lb, sx + 16.51, py)
    out += W(sx - 7.62, sy, sx - 16.51, sy) + label(out_label, sx - 16.51, sy)

    out += textnote(title, X0 + 20.32, Y0 + 5.08)
    # ---------------- junctions where 3+ wire ends coincide ----------------
    cnt = collections.Counter()
    for a, b in wires:
        cnt[a] += 1; cnt[b] += 1
    for pt, k in sorted(cnt.items()):
        if k >= 3:
            out += junction(pt[0], pt[1])
    return out, wires
