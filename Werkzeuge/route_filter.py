"""Route the filter board and pour the ground plane."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math
import pcbnew
import router as R
import place_filter

MM = pcbnew.FromMM
BOARD = os.path.abspath('boards/filter/filter.kicad_pcb')

# U401 is the only SMD part, so its three ground pins are the only ones that
# cannot reach the plane through their own barrel.  Short stub, then a via.
GND_VIAS = [           # SOIC-14: 1.27 mm pitch leaves room beside each pin
    ('U401', '5',  [(-1.40, 0.0)], (-1.40, 0.0)),
    ('U401', '10', [(1.20, 0.0)],  (1.20, 0.0)),
    ('U401', '12', [(1.20, 0.0)],  (1.20, 0.0)),
]

WIDTH = {'+12V': 0.6, '-12V': 0.6}     # matches the Power netclass in the project


def route_order(rt):
    """Shortest nets first.

    The op-amp's own feedback loops are short and have nowhere else to go, so they
    get the corridor beside the package; the long runs down to the panel connector
    can detour around the outside."""
    spans = []
    for net in set(p['net'] for p in rt.pads):
        if not net or net == 'GNDREF':
            continue
        pts = [(p['x'], p['y']) for p in rt.pads if p['net'] == net]
        if len(pts) < 2:
            continue
        w = max(x for x, y in pts) - min(x for x, y in pts)
        h = max(y for x, y in pts) - min(y for x, y in pts)
        spans.append((math.hypot(w, h), net))
    return [n for _, n in sorted(spans)]


def pad_pos(board, ref, num):
    for fp in board.GetFootprints():
        if fp.GetReference() != ref:
            continue
        for p in fp.Pads():
            if p.GetNumber() == num:
                return pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
    raise KeyError('%s.%s' % (ref, num))


def add_gnd_vias(board):
    gnd = board.FindNet('GNDREF')
    n = 0
    for ref, num, stub, via in GND_VIAS:
        px, py = pad_pos(board, ref, num)
        pts = [(px, py)] + [(px + dx, py + dy) for dx, dy in stub]
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
            t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            t.SetWidth(MM(0.3))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(gnd)
            board.Add(t)
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(MM(px + via[0]), MM(py + via[1])))
        v.SetWidth(MM(0.8))
        v.SetDrill(MM(0.4))
        v.SetNet(gnd)
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        board.Add(v)
        n += 1
    return n


def solid_ground_pads(board, refs):
    """Power-entry ground pads connect to the plane solidly rather than through
    thermal spokes: lower impedance, and the middle pin of a 3-way connector has
    its side spokes blocked by the rails leaving its neighbours anyway."""
    n = 0
    for fp in board.GetFootprints():
        if fp.GetReference() not in refs:
            continue
        for p in fp.Pads():
            if p.GetNetname() == 'GNDREF':
                p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
                n += 1
    return n


def add_ground_pour(board, outline, inset=0.4):
    gnd = board.FindNet('GNDREF')
    x0, y0, x1, y1 = outline
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.B_Cu)
    z.SetNet(gnd)
    z.SetIsFilled(False)
    z.SetLocalClearance(MM(0.3))
    z.SetMinThickness(MM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    o = z.Outline()
    o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(MM(x), MM(y))
    board.Add(z)
    return z


def main():
    # rebuild the board from the placement so this script is always re-runnable
    import mkpcb
    mkpcb.build('work/net_filter.net', place_filter.placement(), place_filter.outline(),
                place_filter.holes(), BOARD, labels=place_filter.labels(),
                sch_path='boards/filter/filter.kicad_sch')
    board = pcbnew.LoadBoard(BOARD)

    add_gnd_vias(board)
    rt = R.Router(board, place_filter.outline())
    # keep the ground plane solid under the op-amp: a back-layer track there
    # would break the return path for its own decoupling capacitors
    u = [fp for fp in board.GetFootprints() if fp.GetReference() == 'U401'][0]
    bb = u.GetBoundingBox(False, False)
    M = 0.6
    rt.keepout.append((R.BOT,
                       pcbnew.ToMM(bb.GetLeft()) - M, pcbnew.ToMM(bb.GetTop()) - M,
                       pcbnew.ToMM(bb.GetRight()) + M, pcbnew.ToMM(bb.GetBottom()) + M))
    # seed the router with the ground stubs and vias already placed
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_TRACK':
            rt.occupied.append((t.GetNetname(), R.TOP,
                                pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y),
                                pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)))
        elif t.GetClass() == 'PCB_VIA':
            rt.vias.append((t.GetNetname(),
                            pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)))
    rt._cache.clear()

    failed = []
    for net in route_order(rt):
        ok, segs, nvia = rt.route_net(net, width=WIDTH.get(net, 0.3))
        print('  %-16s %-7s %2d segments, %d via%s'
              % (net, 'ok' if ok else 'FAILED', segs, nvia, '' if nvia == 1 else 's'))
        if not ok:
            failed.append(net)

    # power entry and every decoupling capacitor: lowest-inductance return,
    # and these are exactly the pads whose thermal spokes get blocked by the
    # rails running past them
    solid_ground_pads(board, {'J410', 'J411', 'C403', 'C404', 'C405', 'C406'})
    add_ground_pour(board, place_filter.outline())
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    pcbnew.SaveBoard(BOARD, board)
    # pcbnew.SaveBoard writes a default .kicad_pro over ours, so put the real
    # design rules back afterwards
    import mkproject
    mkproject.make(os.path.join(os.path.dirname(BOARD), 'filter.kicad_sch'))
    tracks = [t for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK']
    vias = [t for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
    print('\nvias: %d   tracks: %d   failed nets: %s'
          % (len(vias), len(tracks), failed if failed else 'none'))
    return failed


if __name__ == '__main__':
    main()
