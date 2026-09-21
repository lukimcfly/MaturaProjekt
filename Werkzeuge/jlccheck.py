"""Measure every board against JLCPCB's published 2-layer limits.

DRC only proves the board obeys the project's own rules; this checks the numbers a
fab actually rejects on: annular rings, holes, hole-to-hole gaps, slots, silkscreen.
Limits are the stricter reading of https://jlcpcb.com/capabilities/pcb-capabilities
(fetched 2026-09-21).

Note: every width query passes a layer. PCB_VIA.GetWidth() without one raises a
wxWidgets assert that blocks the process with an invisible dialog.
"""
import sys, math, itertools
import pcbnew

mm = pcbnew.ToMM

LIMITS = {
    'track':        0.127,  # min track width (4-5 mil; 5 mil = the conservative figure)
    'via_drill':    0.30,   # 0.15 is possible but costs extra; 0.3 is the standard price
    'via_ring':     0.15,
    'pth_ring':     0.18,   # absolute minimum; 0.25 recommended
    'pth_ring_rec': 0.25,
    'npth':         0.50,
    'hole_gap':     0.45,   # pad hole to pad hole (vias: 0.2)
    'slot':         0.50,   # min plated slot width
    'silk_line':    0.15,
    'silk_text_h':  1.00,
    'edge':         0.20,
}


def audit(path):
    b = pcbnew.LoadBoard(path)
    out = {}
    tr = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']
    vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
    out['track_min'] = min(mm(t.GetWidth()) for t in tr) if tr else None
    out['via_drill_min'] = min(mm(v.GetDrillValue()) for v in vias) if vias else None
    out['via_ring_min'] = min((mm(v.GetWidth(pcbnew.F_Cu)) - mm(v.GetDrillValue())) / 2
                              for v in vias) if vias else None

    holes = []            # (x, y, r, owner) for hole-to-hole spacing
    pth_ring, npth, slots, worst_ring = [], [], [], []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            attr = p.GetAttribute()
            ds = p.GetDrillSize()
            dx, dy = mm(ds.x), mm(ds.y)
            if dx <= 0:
                continue
            pos = p.GetPosition()
            holes.append((mm(pos.x), mm(pos.y), min(dx, dy) / 2, fp.GetReference()))
            if attr == pcbnew.PAD_ATTRIB_NPTH:
                npth.append((min(dx, dy), fp.GetReference()))
                continue
            if abs(dx - dy) > 1e-6:
                slots.append((min(dx, dy), fp.GetReference() + '.' + p.GetNumber()))
            sz = p.GetSize(pcbnew.F_Cu)
            ring = min(mm(sz.x) - dx, mm(sz.y) - dy) / 2
            pth_ring.append(ring)
            worst_ring.append((ring, fp.GetReference() + '.' + p.GetNumber(),
                               round(mm(sz.x), 2), round(mm(sz.y), 2), dx))
    for v in vias:
        pos = v.GetPosition()
        holes.append((mm(pos.x), mm(pos.y), mm(v.GetDrillValue()) / 2, 'via'))

    out['pth_ring_min'] = min(pth_ring) if pth_ring else None
    out['pth_ring_worst'] = sorted(worst_ring)[:4]
    out['npth_min'] = min(npth) if npth else None
    out['slots'] = sorted(slots)[:4]

    gap = (1e9, None)
    for a, c in itertools.combinations(holes, 2):
        if a[3] == c[3] and a[3] != 'via' and False:
            continue
        g = math.hypot(a[0] - c[0], a[1] - c[1]) - a[2] - c[2]
        if g < gap[0]:
            gap = (g, (a[3], c[3]))
    out['hole_gap_min'] = (round(gap[0], 3), gap[1])

    # silkscreen: visible texts and graphic line widths on both silk layers
    silk = {pcbnew.F_SilkS, pcbnew.B_SilkS}
    th, tw, lw = [], [], []
    for fp in b.GetFootprints():
        for t in (fp.Reference(), fp.Value()):
            if t.IsVisible() and t.GetLayer() in silk:
                th.append((mm(t.GetTextHeight()), fp.GetReference()))
                tw.append((mm(t.GetTextThickness()), fp.GetReference()))
        for g in fp.GraphicalItems():
            if g.GetLayer() in silk:
                if g.GetClass() in ('PCB_TEXT', 'FP_TEXT'):
                    if g.IsVisible():
                        th.append((mm(g.GetTextHeight()), fp.GetReference()))
                        tw.append((mm(g.GetTextThickness()), fp.GetReference()))
                elif hasattr(g, 'GetWidth'):
                    w = mm(g.GetWidth())
                    if w > 0:
                        lw.append((w, fp.GetReference()))
    for d in b.GetDrawings():
        if d.GetLayer() in silk:
            if d.GetClass() == 'PCB_TEXT':
                th.append((mm(d.GetTextHeight()), 'board text'))
                tw.append((mm(d.GetTextThickness()), 'board text'))
            elif hasattr(d, 'GetWidth') and mm(d.GetWidth()) > 0:
                lw.append((mm(d.GetWidth()), 'board graphic'))
    out['silk_text_h_min'] = min(th) if th else None
    out['silk_text_w_min'] = min(tw) if tw else None
    out['silk_line_min'] = min(lw) if lw else None

    bb = b.GetBoardEdgesBoundingBox()
    out['size'] = (round(mm(bb.GetWidth()), 1), round(mm(bb.GetHeight()), 1))
    ds = b.GetDesignSettings()
    out['rule_edge_clearance'] = mm(ds.m_CopperEdgeClearance)
    return out


if __name__ == '__main__':
    for name in sys.argv[1:]:
        a = audit('boards/%s/%s.kicad_pcb' % (name, name))
        print('=== %s' % name)
        for k, v in a.items():
            print('   %-20s %s' % (k, v))
