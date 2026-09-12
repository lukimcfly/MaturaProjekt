"""Give an auto-named net an explicit label, placed on one of its existing wires."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom

def label_point(g, groups, ref, pin):
    """Pick a point on this net's wiring that is safe to put a label on."""
    start = None
    for p, lst in g.pins.items():
        if (ref, str(pin)) in lst:
            start = p; break
    if start is None:
        raise KeyError(f"pin {ref}.{pin} not found")
    comp = None
    for root, pts in groups.items():
        if start in pts: comp = pts; break
    if comp is None:
        raise KeyError(f"{ref}.{pin} has no wires (direct pin-to-pin)")
    # prefer a wire endpoint that carries no pin and no label
    cands = [p for p in comp if p not in g.pins and p not in g.labels]
    if cands:
        # the one furthest from any pin, so the label has room
        def clearance(p):
            return min((abs(p[0]-q[0]) + abs(p[1]-q[1])) for q in g.pins) if g.pins else 0
        return max(cands, key=clearance), comp
    # fallback: midpoint of the longest axis-aligned wire in the component
    best = None
    for a, b in g.wires:
        if a not in comp and b not in comp: continue
        if a[0] == b[0]:
            L = abs(a[1]-b[1]); mid = (a[0], round((a[1]+b[1])/2 / 1.27) * 1.27)
        elif a[1] == b[1]:
            L = abs(a[0]-b[0]); mid = (round((a[0]+b[0])/2 / 1.27) * 1.27, a[1])
        else:
            continue
        if L >= 2.53 and (best is None or L > best[0]):
            best = (L, mid)
    if best is not None:
        return geom.key(best[1]), comp
    # last resort: sit on a wire endpoint (prefer a panel part's pin - that wire
    # leaves the board anyway).  Electrically valid, just visually tight.
    def panel_first(p):
        return 0 if any(r[:2] in ('RV', 'SW') or r[0] == 'J' for r, _ in g.pins.get(p, [])) else 1
    ends = sorted(comp, key=panel_first)
    if ends:
        return ends[0], comp
    raise KeyError(f"no place for a label on {ref}.{pin}")
