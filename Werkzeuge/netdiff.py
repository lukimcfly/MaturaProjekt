"""Compare two exported netlists: component values/footprints and every net's pin set.

Proves an edit changed exactly what it meant to and no connection moved.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlib


def diff(a, b):
    ca, na, _ = netlib.load(a)
    cb, nb, _ = netlib.load(b)
    vals = [(r, ca[r]['value'], cb[r]['value']) for r in sorted(set(ca) & set(cb))
            if ca[r]['value'] != cb[r]['value']]
    fps = [(r, ca[r]['fp'], cb[r]['fp']) for r in sorted(set(ca) & set(cb))
           if ca[r]['fp'] != cb[r]['fp']]
    parts = (sorted(set(ca) - set(cb)), sorted(set(cb) - set(ca)))
    pa = {n: sorted((r, p) for r, p, _, _ in pins) for n, pins in na.items()}
    pb = {n: sorted((r, p) for r, p, _, _ in pins) for n, pins in nb.items()}
    netch = [n for n in sorted(set(pa) | set(pb)) if pa.get(n) != pb.get(n)]
    return vals, fps, parts, netch, len(pa)


if __name__ == '__main__':
    vals, fps, parts, netch, n = diff(sys.argv[1], sys.argv[2])
    print('value changes     :', len(vals))
    for v in vals:
        print('    %-6s %s -> %s' % v)
    print('footprint changes :', fps or 'none')
    print('parts removed/added:', parts)
    print('nets compared     : %d, changed: %s' % (n, netch or 'none'))
