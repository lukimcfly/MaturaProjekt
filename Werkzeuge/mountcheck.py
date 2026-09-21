"""Mounting holes per board: position, distance to the board edge, and how close any
copper (track, via, pad, or the filled ground plane) comes to each hole centre -
which decides whether a metal screw head or standoff could touch a live net.
"""
import sys, math
import pcbnew

mm = pcbnew.ToMM


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def check(path):
    b = pcbnew.LoadBoard(path)
    bb = b.GetBoardEdgesBoundingBox()
    x0, y0, x1, y1 = mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())
    holes = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                pos = p.GetPosition()
                holes.append((fp.GetReference(), mm(pos.x), mm(pos.y), mm(p.GetDrillSize().x)))
    rows = []
    for ref, hx, hy, d in holes:
        near = {'F.Cu': 1e9, 'B.Cu': 1e9}
        for t in b.GetTracks():
            if t.GetClass() == 'PCB_TRACK':
                w = mm(t.GetWidth()) / 2
                dd = seg_dist(hx, hy, mm(t.GetStart().x), mm(t.GetStart().y),
                              mm(t.GetEnd().x), mm(t.GetEnd().y)) - w
                ly = 'F.Cu' if t.GetLayer() == pcbnew.F_Cu else 'B.Cu'
                near[ly] = min(near[ly], dd)
            elif t.GetClass() == 'PCB_VIA':
                dd = math.hypot(hx - mm(t.GetPosition().x), hy - mm(t.GetPosition().y)) \
                     - mm(t.GetWidth(pcbnew.F_Cu)) / 2
                near['F.Cu'] = min(near['F.Cu'], dd); near['B.Cu'] = min(near['B.Cu'], dd)
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    continue
                sz = p.GetSize(pcbnew.F_Cu)
                dd = math.hypot(hx - mm(p.GetPosition().x), hy - mm(p.GetPosition().y)) \
                     - max(mm(sz.x), mm(sz.y)) / 2
                for ly, lid in (('F.Cu', pcbnew.F_Cu), ('B.Cu', pcbnew.B_Cu)):
                    if p.IsOnLayer(lid):
                        near[ly] = min(near[ly], dd)
        # ground plane: nearest filled point, sampled on rings around the hole
        plane = 1e9
        for z in b.Zones():
            poly = z.GetFilledPolysList(z.GetLayer())
            for r in [x / 10 for x in range(int(d * 5), 80)]:
                hit = False
                for k in range(72):
                    a = 2 * math.pi * k / 72
                    pt = pcbnew.VECTOR2I(pcbnew.FromMM(hx + r * math.cos(a)), pcbnew.FromMM(hy + r * math.sin(a)))
                    if poly.Contains(pt):
                        hit = True; break
                if hit:
                    plane = min(plane, r); break
        edge = min(hx - x0, x1 - hx, hy - y0, y1 - hy)
        rows.append((ref, round(hx - x0, 1), round(hy - y0, 1), d, round(edge, 1),
                     round(near['F.Cu'], 1), round(near['B.Cu'], 1), round(plane, 1)))
    return (round(x1 - x0, 1), round(y1 - y0, 1)), rows


if __name__ == '__main__':
    for name in sys.argv[1:]:
        size, rows = check('boards/%s/%s.kicad_pcb' % (name, name))
        print('=== %s  %s mm' % (name, size))
        print('   ref   x     y     hole  edge  top-Cu  bot-Cu  plane   (mm from hole centre)')
        for r in rows:
            print('   %-4s %5.1f %5.1f  %4.1f  %4.1f  %6.1f  %6.1f  %5.1f' % r)
