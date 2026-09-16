"""Load a kicadsexpr netlist into {net: [(ref,pin,pinfn,pintype)]} and {ref: {...}}."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexp

def load(path):
    d = sexp.load(path)
    comps = {}
    for c in sexp.kids(sexp.kid(d, 'components') or [], 'comp'):
        ref = sexp.val(c, 'ref')
        comps[ref] = dict(
            ref=ref,
            value=sexp.val(c, 'value', ''),
            fp=sexp.val(c, 'footprint', ''),
            libsource=sexp.kid(c, 'libsource'),
        )
        ls = comps[ref]['libsource']
        comps[ref]['lib'] = sexp.val(ls, 'lib', '') if ls else ''
        comps[ref]['part'] = sexp.val(ls, 'part', '') if ls else ''
    nets = {}
    for n in sexp.kids(sexp.kid(d, 'nets') or [], 'net'):
        name = sexp.val(n, 'name')
        pins = []
        for nd in sexp.kids(n, 'node'):
            pins.append((sexp.val(nd, 'ref'), str(sexp.val(nd, 'pin')),
                         sexp.val(nd, 'pinfunction', ''), sexp.val(nd, 'pintype', '')))
        nets[name] = pins
    # libparts: pin definitions per part
    libparts = {}
    for lp in sexp.kids(sexp.kid(d, 'libparts') or [], 'libpart'):
        key = (sexp.val(lp, 'lib', ''), sexp.val(lp, 'part', ''))
        pins = []
        for p in sexp.kids(sexp.kid(lp, 'pins') or [], 'pin'):
            pins.append((str(sexp.val(p, 'num')), sexp.val(p, 'name', ''), sexp.val(p, 'type', '')))
        libparts[key] = pins
    return comps, nets, libparts

def pins_of(nets, ref):
    """All (net, pin, pinfn, pintype) for a reference."""
    out = []
    for nm, pins in nets.items():
        for r, p, fn, t in pins:
            if r == ref:
                out.append((nm, p, fn, t))
    return sorted(out, key=lambda x: (len(x[1]), x[1]))
