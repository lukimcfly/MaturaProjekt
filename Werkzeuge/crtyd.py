"""Courtyard check on a placement, before anything is built.

KiCad's DRC does this on the finished board, but by then the collision resolver
has already nudged parts around and the layout is no longer the one that was
designed.  Checking the placement itself against each footprint's own courtyard
means the design can be made correct rather than repaired afterwards.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlib

FPDIR = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'
_cache = {}


def extent(fpid, rot):
    """(dx0, dy0, dx1, dy1) of the courtyard relative to the pad centroid."""
    key = (fpid, rot)
    if key in _cache:
        return _cache[key]
    lib, name = fpid.split(':')
    fp = pcbnew.FootprintLoad(os.path.join(FPDIR, lib + '.pretty'), name)
    fp.SetOrientationDegrees(rot)
    pads = list(fp.Pads())
    cx = sum(p.GetPosition().x for p in pads) / len(pads)
    cy = sum(p.GetPosition().y for p in pads) / len(pads)
    xs, ys = [], []
    for d in fp.GraphicalItems():
        if d.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            bb = d.GetBoundingBox()
            xs += [pcbnew.ToMM(bb.GetLeft() - cx), pcbnew.ToMM(bb.GetRight() - cx)]
            ys += [pcbnew.ToMM(bb.GetTop() - cy), pcbnew.ToMM(bb.GetBottom() - cy)]
    if not xs:                      # no courtyard drawn: fall back to the body
        bb = fp.GetBoundingBox(False, False)
        xs = [pcbnew.ToMM(bb.GetLeft() - cx), pcbnew.ToMM(bb.GetRight() - cx)]
        ys = [pcbnew.ToMM(bb.GetTop() - cy), pcbnew.ToMM(bb.GetBottom() - cy)]
    _cache[key] = (min(xs), min(ys), max(xs), max(ys))
    return _cache[key]


def check(place, netfile, outline=None, holes=(), hole_r=3.2, edge=0.5):
    """[] if the placement is clean, else a list of problems."""
    comps = netlib.load(netfile)[0]
    boxes = {}
    for ref, (x, y, rot) in place.items():
        if ref not in comps:
            continue
        a, b, c, d = extent(comps[ref]['fp'], rot)
        boxes[ref] = (x + a, y + b, x + c, y + d)
    bad = []
    keys = sorted(boxes)
    for i, r in enumerate(keys):
        ax0, ay0, ax1, ay1 = boxes[r]
        if outline:
            x0, y0, x1, y1 = outline
            if (ax0 < x0 + edge or ay0 < y0 + edge
                    or ax1 > x1 - edge or ay1 > y1 - edge):
                bad.append('EDGE %s (%.1f,%.1f)-(%.1f,%.1f)' % (r, ax0, ay0, ax1, ay1))
        for hx, hy in holes:
            if (ax0 - hole_r < hx < ax1 + hole_r
                    and ay0 - hole_r < hy < ay1 + hole_r):
                bad.append('HOLE %s vs mounting hole (%g,%g)' % (r, hx, hy))
        for s in keys[i + 1:]:
            bx0, by0, bx1, by1 = boxes[s]
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > 0 and oy > 0:
                bad.append('COURTYARD %s/%s overlap %.2f x %.2f' % (r, s, ox, oy))
    return bad
