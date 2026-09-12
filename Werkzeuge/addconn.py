"""Add board-boundary connectors + name the boundary nets."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexp, geom, netname, libembed, connspec
from schedit import Sch
import svfgen
from svfgen import sym, wire, uid

svfgen._c[0] = 300000
G = 1.27
COLX0, COLDX = 900.43, 69.85
ROWY = [60.96, 330.2]
CXOFF, VSPACE, STUB = 30.48, 15.24, 7.62

def rlabel(nm, x, y):
    """Local label whose text runs leftwards from the anchor."""
    return [f'\t(label "{nm}"', f'\t\t(at {x} {y} 0)', '\t\t(effects',
            '\t\t\t(font', '\t\t\t\t(size 1.27 1.27)', '\t\t\t)',
            '\t\t\t(justify right bottom)', '\t\t)', f'\t\t(uuid "{uid()}")', '\t)']

def note(t, x, y):
    return [f'\t(text "{t}"', '\t\t(exclude_from_sim no)', f'\t\t(at {x} {y} 0)', '\t\t(effects',
            '\t\t\t(font', '\t\t\t\t(size 2.032 2.032)', '\t\t\t\t(bold yes)', '\t\t\t)',
            '\t\t\t(justify left top)', '\t\t)', f'\t\t(uuid "{uid()}")', '\t)']

def ongrid(*vals):
    for v in vals:
        assert abs(v / G - round(v / G)) < 1e-6, f"off-grid: {v}"

def build(path):
    # ---------- 1. label the boundary nets that have auto-generated names ----------
    g = geom.Geom(path); groups = g.components()
    lab_lines, placed = [], {}
    for (ref, pin), name in sorted(connspec.renames().items()):
        pt, _ = netname.label_point(g, groups, ref, pin)
        assert pt not in placed, f"two labels at {pt}: {name} / {placed.get(pt)}"
        placed[pt] = name
        lab_lines += rlabel(name, pt[0], pt[1])
    # ---------- 2. embed the connector symbols we need ----------
    need = sorted({n for _, cs in connspec.COLUMNS for _, n, _, _ in cs})
    embeds, pinpos = [], {}
    for n in need:
        nm = f"Conn_01x{n:02d}"
        e = libembed.embedded_form('Connector_Generic', nm)
        pinpos[n] = libembed.pin_positions(e)
        embeds.append((f"Connector_Generic:{nm}", sexp.dump(e, 2)))
    # ---------- 3. connector instances ----------
    out = []
    for ci, (title, conns) in enumerate(connspec.COLUMNS):
        col, row = ci % 4, ci // 4
        colx = COLX0 + col * COLDX
        cx = colx + CXOFF
        y = ROWY[row]
        out += note(title, colx + 2.54, y - 12.7)
        for ref, npins, val, nets in conns:
            pp = pinpos[npins]
            top = max(v[1] for v in pp.values())
            cy = y + top                      # so the top pin sits at screen y
            ongrid(cx, cy)
            out += sym(f"Connector_Generic:Conn_01x{npins:02d}", ref, val, cx, cy, 0, 1,
                       cx + 3.81, cy - top - 3.81, cx + 3.81, cy - top - 1.27)
            for k in range(1, npins + 1):
                px, py = pp[str(k)]
                ax, ay = cx + px, cy - py     # KiCad Y is inverted
                out += wire(ax, ay, ax - STUB, ay)
                out += rlabel(nets[k - 1], ax - STUB, ay)
            y = cy + abs(min(v[1] for v in pp.values())) + VSPACE
    return lab_lines, embeds, out

if __name__ == "__main__":
    path = sys.argv[1]
    labs, embeds, conns = build(path)
    s = Sch(path)
    have = set(re.findall(r'\(symbol "([^"]+)"', "\n".join(s.lines[:1])) )
    existing = set(s.refs())
    dup = [r for _, cs in connspec.COLUMNS for (r, *_ ) in cs if r in existing]
    assert not dup, f"reference collision: {dup}"
    # paper size
    for i, l in enumerate(s.lines):
        if l.startswith('\t(paper'):
            s.lines[i] = '\t(paper "User" 1200 934)'
            print("paper ->", s.lines[i].strip()); break
    # embed symbols not already present
    txt = "\n".join(s.lines)
    for name, block in embeds:
        if f'(symbol "{name}"' in txt:
            print(f"  {name} already embedded"); continue
        s.insert_libsymbol(block)
    s.append_raw(labs)
    s.append_raw(conns)
    s.save(path)
    print(f"added {sum(1 for _,cs in connspec.COLUMNS for _ in cs)} connectors, "
          f"{len(connspec.renames())} net labels")
