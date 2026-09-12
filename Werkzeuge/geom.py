"""Geometric connectivity for a flat .kicad_sch: wires, junctions, labels, symbol pins."""
import sys, os, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexp

TOL = 0.01
def key(p): return (round(p[0], 2), round(p[1], 2))

def rot(dx, dy, ang):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    return (dx * c - dy * s, dx * s - dy * c)   # KiCad Y is inverted

class Geom:
    def __init__(self, path):
        self.sch = sexp.load(path)
        self.wires = []
        for w in self.sch:
            if sexp.head(w) == 'wire':
                pts = sexp.kid(sexp.kid(w, 'pts'), 'xy'), sexp.kids(sexp.kid(w, 'pts'), 'xy')
                xy = sexp.kids(sexp.kid(w, 'pts'), 'xy')
                self.wires.append((key((float(xy[0][1]), float(xy[0][2]))),
                                   key((float(xy[1][1]), float(xy[1][2])))))
        self.junctions = {key((float(sexp.kid(j,'at')[1]), float(sexp.kid(j,'at')[2])))
                          for j in self.sch if sexp.head(j) == 'junction'}
        self.labels = collections.defaultdict(list)     # point -> [names]
        for kind in ('label', 'global_label', 'hierarchical_label'):
            for l in self.sch:
                if sexp.head(l) == kind:
                    a = sexp.kid(l, 'at')
                    self.labels[key((float(a[1]), float(a[2])))].append(l[1])
        # symbol pins
        self.lib = {s[1]: s for s in sexp.kids(sexp.kid(self.sch, 'lib_symbols'), 'symbol')}
        self.pins = collections.defaultdict(list)       # point -> [(ref, pinnum)]
        self.sympins = collections.defaultdict(list)    # ref -> [(pinnum, point)]
        for s in self.sch:
            if sexp.head(s) != 'symbol': continue
            libid = sexp.val(s, 'lib_id'); ref = sexp.prop(s, 'Reference')
            unit = int(sexp.val(s, 'unit', 1))
            a = sexp.kid(s, 'at'); x, y = float(a[1]), float(a[2])
            ang = float(a[3]) if len(a) > 3 else 0
            mir = sexp.val(s, 'mirror')
            ls = self.lib.get(libid)
            if ls is None: continue
            for sub in sexp.kids(ls, 'symbol'):
                nm = sub[1]
                try: u = int(nm.split('_')[-2])
                except Exception: continue
                if u not in (0, unit): continue
                for p in sexp.kids(sub, 'pin'):
                    pa = sexp.kid(p, 'at')
                    dx, dy = float(pa[1]), float(pa[2])
                    if mir == 'y': dx = -dx
                    if mir == 'x': dy = -dy
                    rx, ry = rot(dx, dy, ang)
                    pt = key((x + rx, y + ry))
                    num = str(sexp.val(p, 'number'))
                    self.pins[pt].append((ref, num))
                    self.sympins[ref].append((num, pt))

    def on_segment(self, p, a, b):
        if key(p) in (a, b): return False
        L2 = (b[0]-a[0])**2 + (b[1]-a[1])**2
        if L2 < 1e-9: return False                      # zero-length wire joins nothing
        cross = (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])
        if abs(cross) > TOL * (L2 ** 0.5): return False
        dot = (p[0]-a[0])*(b[0]-a[0]) + (p[1]-a[1])*(b[1]-a[1])
        return 0 < dot < L2

    def components(self):
        """Union-find over wire endpoints; endpoint-on-segment also joins."""
        parent = {}
        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb: parent[ra] = rb
        for a, b in self.wires: union(a, b)
        endpoints = {p for w in self.wires for p in w}
        for p in list(endpoints) + list(self.pins.keys()) + list(self.labels.keys()):
            for a, b in self.wires:
                if self.on_segment(p, a, b): union(key(p), a)
        for p in list(self.pins) + list(self.labels):
            find(key(p))
        groups = collections.defaultdict(set)
        for p in list(parent):
            groups[find(p)].add(p)
        return groups

    def net_at(self, pt):
        """Everything electrically joined to point pt."""
        groups = self.components()
        pt = key(pt)
        for root, pts in groups.items():
            if pt in pts:
                labs = sorted({l for p in pts for l in self.labels.get(p, [])})
                pins = sorted({f"{r}.{n}" for p in pts for r, n in self.pins.get(p, [])})
                return pts, labs, pins
        return {pt}, sorted(self.labels.get(pt, [])), sorted(f"{r}.{n}" for r, n in self.pins.get(pt, []))
