"""Constructive placer for the passives.

The architectural decisions - where the ICs sit, which edge each connector lives on -
stay manual, because those carry the engineering.  Everything else is placed to pull
its own nets short: each part goes to the centroid of whatever it connects to that is
already placed, then to the nearest free slot, most-constrained part first.  A few
refinement passes lift each part out and put it back at its updated ideal spot.
"""
import sys, os, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlib

FPDIR = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'
STEP = 1.27          # placement grid
_fpcache = {}


def fp_size(fpid, rot):
    """(width, height) of the footprint body at this rotation, in mm."""
    key = (fpid, rot)
    if key in _fpcache:
        return _fpcache[key]
    lib, name = fpid.split(':')
    fp = pcbnew.FootprintLoad(os.path.join(FPDIR, lib + '.pretty'), name)
    fp.SetOrientationDegrees(rot)
    bb = fp.GetBoundingBox(False, False)
    _fpcache[key] = (pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight()))
    return _fpcache[key]


_padcache = {}


def pad_offsets(fpid, rot):
    """{pad: (dx, dy)} from the pad centroid, at this rotation.  Cached - loading
    a footprint from disk inside the placement loop is ruinously slow."""
    key = (fpid, rot)
    if key in _padcache:
        return _padcache[key]
    lib, name = fpid.split(':')
    fp = pcbnew.FootprintLoad(os.path.join(FPDIR, lib + '.pretty'), name)
    fp.SetOrientationDegrees(rot)
    pads = list(fp.Pads())
    cx = sum(p.GetPosition().x for p in pads) / len(pads)
    cy = sum(p.GetPosition().y for p in pads) / len(pads)
    _padcache[key] = {p.GetNumber(): (pcbnew.ToMM(p.GetPosition().x - cx),
                                      pcbnew.ToMM(p.GetPosition().y - cy)) for p in pads}
    return _padcache[key]


class Placer:
    def __init__(self, netfile, outline, fixed, margin=2.0, keepaway=()):
        self.comps, self.nets, _ = netlib.load(netfile)
        self.x0, self.y0, self.x1, self.y1 = outline
        self.margin = margin
        self.place = dict(fixed)          # ref -> (x, y, rot)
        self.keepaway = list(keepaway)    # extra forbidden rectangles
        self.netpins = collections.defaultdict(list)
        for n, pins in self.nets.items():
            if n.startswith('unconnected'):
                continue
            for r, p, fn, t in pins:
                self.netpins[r].append((n, str(p)))
        # a rail touches nearly everything, so it must not drag the placement around
        self.ignore = {'GNDREF', '+12V', '-12V', '+5V'}

    def box(self, ref, x, y, rot):
        w, h = fp_size(self.comps[ref]['fp'], rot)
        return (x - w / 2 - 0.6, y - h / 2 - 0.6, x + w / 2 + 0.6, y + h / 2 + 0.6)

    def collides(self, ref, x, y, rot, skip=None):
        a = self.box(ref, x, y, rot)
        if a[0] < self.x0 + self.margin or a[1] < self.y0 + self.margin \
           or a[2] > self.x1 - self.margin or a[3] > self.y1 - self.margin:
            return True
        for k in self.keepaway:
            if a[0] < k[2] and k[0] < a[2] and a[1] < k[3] and k[1] < a[3]:
                return True
        for other, (ox, oy, orot) in self.place.items():
            if other == ref or other == skip:
                continue
            b = self.box(other, ox, oy, orot)
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                return True
        return False

    def neighbours(self, ref):
        """(net, pad) pairs of this part that reach something already placed."""
        out = []
        for n, p in self.netpins.get(ref, []):
            if n in self.ignore:
                continue
            for r2, p2, fn, t in self.nets[n]:
                if r2 != ref and r2 in self.place:
                    out.append((n, p, r2, str(p2)))
        return out

    def pad_xy(self, ref, pad):
        x, y, rot = self.place[ref]
        d = pad_offsets(self.comps[ref]['fp'], rot).get(pad, (0, 0))
        return (x + d[0], y + d[1])

    def ideal(self, ref, rot):
        """Where this part wants to be: centroid of what its pads connect to,
        corrected for where its own pads sit relative to its centre."""
        links = self.neighbours(ref)
        if not links:
            return None
        offs = pad_offsets(self.comps[ref]['fp'], rot)
        xs, ys = [], []
        sx = sy = sw = 0.0
        for n, p, r2, p2 in links:
            tx, ty = self.pad_xy(r2, p2)
            dx, dy = offs.get(p, (0, 0))
            w = 1.0 / max(1, len(self.nets[n]) - 1)   # small nets pull hardest
            sx += (tx - dx) * w
            sy += (ty - dy) * w
            sw += w
        return (sx / sw, sy / sw)

    def best_spot(self, ref, rots=(0, 180, 90, 270), skip=None):
        best = None
        for rot in rots:
            want = self.ideal(ref, rot)
            if want is None:
                continue
            gx = round(want[0] / STEP) * STEP
            gy = round(want[1] / STEP) * STEP
            for ring in range(0, 45):
                cands = []
                for i in range(-ring, ring + 1):
                    for j in (-ring, ring) if ring else (0,):
                        cands.append((gx + i * STEP, gy + j * STEP))
                        cands.append((gx + j * STEP, gy + i * STEP))
                for cx, cy in cands:
                    if self.collides(ref, cx, cy, rot, skip=skip):
                        continue
                    cost = math.hypot(cx - want[0], cy - want[1])
                    if best is None or cost < best[0]:
                        best = (cost, cx, cy, rot)
                    break
                if best and best[0] <= ring * STEP:
                    break
        return best

    def place_decoupling(self, pairs, gap=5.0):
        """pairs: [(cap, ic, pin, side)] - put each cap beside the supply pin it
        serves, on the given side ('L' or 'R'), pad facing the IC."""
        for cap, ic, pin, side in pairs:
            if ic not in self.place:
                continue
            px, py = self.pad_xy(ic, pin)
            rot = 180 if side == 'L' else 0
            for d in [gap + k * STEP for k in range(0, 30)]:
                x = px - d if side == 'L' else px + d
                if not self.collides(cap, x, py, rot):
                    self.place[cap] = (x, py, rot)
                    break

    def run(self, parts, passes=3):
        todo = [p for p in parts if p not in self.place]
        # most-constrained first: the part with most links to already-placed things
        while todo:
            todo.sort(key=lambda r: -len(self.neighbours(r)))
            ref = todo[0]
            spot = self.best_spot(ref)
            if spot is None:                  # nothing placed yet that it touches
                todo.append(todo.pop(0))
                if all(not self.neighbours(r) for r in todo):
                    break
                continue
            _, x, y, rot = spot
            self.place[ref] = (x, y, rot)
            todo.pop(0)
        for _ in range(passes):
            for ref in parts:
                if ref not in self.place:
                    continue
                old = self.place[ref]
                del self.place[ref]
                spot = self.best_spot(ref)
                self.place[ref] = (spot[1], spot[2], spot[3]) if spot else old
        return self.place

    def resolve(self, desired, anchors=(), rings=40):
        """Take a hand-made placement and make it legal.

        Each part keeps the position and rotation it was given; anything that
        overlaps is nudged to the nearest free spot on the grid.  Anchors (ICs,
        connectors, mounting holes) are placed first and never moved, so the
        structure of the layout survives and only the strays shift."""
        self.place = {r: desired[r] for r in anchors if r in desired}
        moved = []
        rest = [r for r in desired if r not in self.place]
        # biggest parts first: they have the least freedom to move
        rest.sort(key=lambda r: -max(fp_size(self.comps[r]['fp'], desired[r][2])))
        for ref in rest:
            x, y, rot = desired[ref]
            if not self.collides(ref, x, y, rot):
                self.place[ref] = (x, y, rot)
                continue
            found = None
            for ring in range(1, rings):
                for i in range(-ring, ring + 1):
                    for dx, dy in ((i * STEP, -ring * STEP), (i * STEP, ring * STEP),
                                   (-ring * STEP, i * STEP), (ring * STEP, i * STEP)):
                        if not self.collides(ref, x + dx, y + dy, rot):
                            found = (x + dx, y + dy, rot)
                            break
                    if found:
                        break
                if found:
                    break
            self.place[ref] = found or (x, y, rot)
            if found:
                moved.append((ref, round(math.hypot(found[0]-x, found[1]-y), 1)))
        return self.place, moved

    def total_net_length(self):
        tot = 0.0
        for n, pins in self.nets.items():
            if n.startswith('unconnected') or n in self.ignore:
                continue
            pts = [self.pad_xy(r, str(p)) for r, p, fn, t in pins if r in self.place]
            if len(pts) < 2:
                continue
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            tot += sum(math.hypot(p[0] - cx, p[1] - cy) for p in pts)
        return tot
