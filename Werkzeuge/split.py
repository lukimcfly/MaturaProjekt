"""Derive a single-board schematic from the master by keeping one module's elements."""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexp, geom

MODULES = {'1':'OSC1','2':'OSC2','3':'OSC3','4':'FLT_A','5':'FLT_B','6':'FLT_C','7':'FLT_D'}

def mod_of_ref(ref):
    """Module a reference belongs to, or None for #PWR/#FLG (resolved by wiring)."""
    if ref.startswith('#'): return None
    if ref in ('J904', 'J990'): return 'MAIN'
    if re.match(r'[A-Z]+99', ref): return 'MAIN'
    m = re.match(r'([A-Z]+)(\d)(\d+)$', ref)
    if not m: return 'MAIN'
    return MODULES.get(m.group(2), 'MAIN')

def classify(path):
    g = geom.Geom(path)
    groups = g.components()
    # module of each wire component, from the refs it touches
    comp_mod, pt_comp = {}, {}
    for root, pts in groups.items():
        mods = {mod_of_ref(r) for p in pts for r, _ in g.pins.get(p, [])}
        mods.discard(None)
        assert len(mods) <= 1, f"component spans {mods}"
        comp_mod[root] = next(iter(mods)) if mods else None
        for p in pts: pt_comp[p] = root
    def mod_at(pt):
        root = pt_comp.get(geom.key(pt))
        return comp_mod.get(root) if root else None
    # symbols: real refs first, then anchors for proximity lookup
    sym_mod, anchors = {}, []
    pending = []
    for s in g.sch:
        if sexp.head(s) != 'symbol': continue
        ref = sexp.prop(s, 'Reference')
        a = sexp.kid(s, 'at'); x, y = float(a[1]), float(a[2])
        m = mod_of_ref(ref)
        if m is None:                      # #PWR / #FLG : follow its wire
            pins = g.sympins.get(ref, [])
            m = mod_at(pins[0][1]) if pins else None
        if m is None:
            pending.append((ref, x, y)); continue
        sym_mod.setdefault(ref, m)
        anchors.append((x, y, m))

    def nearest(x, y):
        best, bd = None, 1e18
        for ax, ay, m in anchors:
            d = (ax-x)**2 + (ay-y)**2
            if d < bd: bd, best = d, m
        return best, bd ** 0.5

    for ref, x, y in pending:              # power flags with no component on their net
        m = nearest(x, y)[0]
        sym_mod[ref] = m
        # claim their wiring too, otherwise the flag arrives unconnected
        for _, pt in g.sympins.get(ref, []):
            root = pt_comp.get(geom.key(pt))
            if root is not None and comp_mod.get(root) is None:
                comp_mod[root] = m
    return g, sym_mod, mod_at, nearest

def derive(path, target, out_path, title=None, extra=None, text_owner=None):
    g, sym_mod, mod_at, nearest = classify(path)
    drop = collections.Counter()
    NEAR = 60.0
    def in_box(x, y):
        m, d = nearest(x, y)
        return m == target and d <= NEAR
    head, body = [], []
    for c in g.sch:
        if not isinstance(c, list): continue     # the bare 'kicad_sch' token
        h = sexp.head(c)
        if h in ('version','generator','generator_version','uuid','paper','title_block',
                 'lib_symbols','sheet_instances','embedded_fonts'):
            head.append(c); continue
        if h == 'symbol':
            if sym_mod.get(sexp.prop(c, 'Reference')) == target: body.append(c)
            else: drop['symbol'] += 1
            continue
        if h == 'wire':
            xy = sexp.kids(sexp.kid(c,'pts'), 'xy')
            pt = (float(xy[0][1]), float(xy[0][2]))
            if mod_at(pt) == target: body.append(c)
            else: drop['wire'] += 1
            continue
        if h in ('junction','label','global_label','no_connect'):
            a = sexp.kid(c, 'at'); pt = (float(a[1]), float(a[2]))
            m = mod_at(pt)
            if m == target: body.append(c)
            elif m is None and in_box(pt[0], pt[1]): body.append(c)
            else: drop[h] += 1
            continue
        if h == 'text':
            a = sexp.kid(c, 'at')
            txt = str(c[1])
            owner = None
            for prefix, who in (text_owner or {}).items():
                if txt.startswith(prefix): owner = who; break
            if owner is not None:
                if owner == target: body.append(c)
                else: drop['text'] += 1
                continue
            if in_box(float(a[1]), float(a[2])): body.append(c)
            else: drop['text'] += 1
            continue
        body.append(c)
    # rebuild
    lines = ['(kicad_sch']
    for c in head:
        if sexp.head(c) in ('sheet_instances','embedded_fonts'): continue
        if sexp.head(c) == 'title_block' and title:
            c = [x for x in c]
            for i, k in enumerate(c):
                if isinstance(k, list) and sexp.head(k) == 'title':
                    c[i] = [sexp.Sym('title'), title]
        lines.append(sexp.dump(c, 1))
    for c in body:
        lines.append(sexp.dump(c, 1))
    if extra:
        lines.extend(extra)
    for c in head:
        if sexp.head(c) in ('sheet_instances','embedded_fonts'):
            lines.append(sexp.dump(c, 1))
    lines.append(')')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    kept = collections.Counter(sexp.head(c) for c in body)
    return kept, drop
