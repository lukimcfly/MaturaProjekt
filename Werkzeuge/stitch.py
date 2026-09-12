"""Ground on both layers, tied together with stitching vias.

A two-layer board with a pour on the back only has a problem: every back-side
track is a slot cut through the plane.  On the oscillator board that left the
ground in six separate islands, which is exactly what a ground plane is supposed
to prevent - return currents have to detour around the slots, and an island that
only reaches the rest of the ground through a thin neck is barely a ground at all.

Pouring ground on the front as well and stitching the two together fixes it: where
a back-side track cuts the plane, the front copper carries the return current
across the gap.  This is ordinary practice for two-layer boards and costs nothing
in fabrication.

Vias go in after routing, so they can only be placed where there is genuinely room;
placing them first would choke the routing channels on an already dense board.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

MM = pcbnew.FromMM
mm = pcbnew.ToMM
GND = 'GNDREF'


def add_front_pour(board, outline, inset=0.4, clearance=0.3, min_thick=0.25):
    gnd = board.FindNet(GND)
    x0, y0, x1, y1 = outline
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.F_Cu)
    z.SetNet(gnd)
    z.SetIsFilled(False)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(min_thick))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    o = z.Outline()
    o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(MM(x), MM(y))
    board.Add(z)
    return z


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def clear_spots(board, outline, step=6.0, margin=3.0, via_r=0.4,
                clearance=0.35, hole_gap=0.6):
    """Grid positions where a stitching via fits without touching anything.

    Anything on a net other than ground has to be cleared properly; ground copper
    is fine to sit on, but a via still may not land on top of a hole.
    """
    x0, y0, x1, y1 = outline
    tracks, pads, holes = [], [], []
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_TRACK':
            tracks.append((t.GetNetname(), mm(t.GetWidth()),
                           mm(t.GetStart().x), mm(t.GetStart().y),
                           mm(t.GetEnd().x), mm(t.GetEnd().y)))
        elif t.GetClass() == 'PCB_VIA':
            # NOT GetWidth(): on a via KiCad 10 asserts "called without a layer
            # argument", which in a headless script is a dialog nobody can answer
            # and the process simply stops.
            holes.append((mm(t.GetPosition().x), mm(t.GetPosition().y),
                          mm(t.GetDrillValue()) / 2 + 0.2))
    for fp in board.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            pads.append((p.GetNetname(), mm(bb.GetLeft()), mm(bb.GetTop()),
                         mm(bb.GetRight()), mm(bb.GetBottom())))
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                holes.append((mm(p.GetPosition().x), mm(p.GetPosition().y),
                              mm(p.GetDrillSize().x) / 2))

    out = []
    n = 0
    y = y0 + margin
    while y <= y1 - margin:
        x = x0 + margin
        while x <= x1 - margin:
            n += 1
            ok = True
            for net, w, ax, ay, bx, by in tracks:
                need = via_r + w / 2 + (0.0 if net == GND else clearance)
                if _seg_dist(x, y, ax, ay, bx, by) < need:
                    ok = False
                    break
            if ok:
                for net, l, t_, r_, b_ in pads:
                    pad = 0.0 if net == GND else clearance
                    if (l - via_r - pad <= x <= r_ + via_r + pad
                            and t_ - via_r - pad <= y <= b_ + via_r + pad):
                        ok = False
                        break
            if ok:
                for hx, hy, hr in holes:
                    if math.hypot(x - hx, y - hy) < via_r + hr + hole_gap:
                        ok = False
                        break
            if ok:
                out.append((x, y))
            x += step
        y += step
    return out, n


def add_vias(board, spots, drill=0.4, diameter=0.8):
    gnd = board.FindNet(GND)
    for x, y in spots:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        v.SetWidth(MM(diameter))
        v.SetDrill(MM(drill))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(gnd)
        board.Add(v)
    return len(spots)


def plane_report(board):
    out = []
    for z in board.Zones():
        layer = 'F.Cu' if z.GetLayer() == pcbnew.F_Cu else 'B.Cu'
        polys = z.GetFilledPolysList(z.GetLayer())
        areas = sorted((polys.COutline(i).Area() / 1e12 for i in range(polys.OutlineCount())),
                       reverse=True)
        out.append((layer, round(z.GetFilledArea() / 1e12), len(areas),
                    [round(a) for a in areas[:6]]))
    return out
