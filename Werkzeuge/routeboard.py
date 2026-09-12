"""Route one board and pour its ground plane.

Same recipe for every board:
  - SMD ground pins get a short stub and a via down to the plane (through-hole
    pads reach it through their own barrel)
  - a keep-out under each IC so nothing on the back cuts the return path for its
    own decoupling capacitors
  - everything except ground routed on the front, shortest nets first, so the
    op-amps' feedback loops get the tight space beside the package
  - power-entry and decoupling ground pads connect to the plane solidly; the rest
    keep thermal spokes so they can still be hand-soldered
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import router as R
import fanout
import stitch
import mkproject

MM = pcbnew.FromMM


def pad_pos(board, ref, num):
    for fp in board.GetFootprints():
        if fp.GetReference() != ref:
            continue
        for p in fp.Pads():
            if p.GetNumber() == str(num):
                return pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
    raise KeyError('%s.%s' % (ref, num))


def add_gnd_vias(board, specs, width=0.3):
    """specs: [(ref, pad, [(dx, dy), ...])] - stub waypoints, via at the last one."""
    gnd = board.FindNet('GNDREF')
    for ref, num, waypoints in specs:
        px, py = pad_pos(board, ref, num)
        pts = [(px, py)] + [(px + dx, py + dy) for dx, dy in waypoints]
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
            t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            t.SetWidth(MM(width))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(gnd)
            board.Add(t)
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(MM(pts[-1][0]), MM(pts[-1][1])))
        v.SetWidth(MM(0.8))
        v.SetDrill(MM(0.4))
        v.SetNet(gnd)
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        board.Add(v)


def auto_gnd_vias(board, refs, via_r=0.4, clearance=0.3, track_w=0.3):
    """Give every SMD ground pad on `refs` a stub and a via to the plane.

    The spot is searched for rather than hardcoded: step outward from the pad,
    away from the package centre, until the via clears every other pad and via.
    """
    gnd = board.FindNet('GNDREF')
    obstacles = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            obstacles.append((pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()),
                              pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()),
                              p.GetNetname()))
    placed = []
    made = []
    for fp in board.GetFootprints():
        if fp.GetReference() not in refs:
            continue
        c = fp.GetPosition()
        cx, cy = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
        for p in fp.Pads():
            if p.GetNetname() != 'GNDREF':
                continue
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                continue                      # a plated hole already reaches the plane
            px, py = pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
            ux, uy = px - cx, py - cy
            n = math.hypot(ux, uy) or 1.0
            ux, uy = ux / n, uy / n
            spot = None
            for d in [0.8 + 0.1 * k for k in range(0, 60)]:
                vx, vy = px + ux * d, py + uy * d
                ok = True
                for x0, y0, x1, y1, net in obstacles:
                    if net == 'GNDREF':
                        continue
                    dx = max(x0 - vx, 0, vx - x1)
                    dy = max(y0 - vy, 0, vy - y1)
                    if math.hypot(dx, dy) < via_r + clearance:
                        ok = False
                        break
                if ok:
                    for qx, qy in placed:
                        if math.hypot(vx - qx, vy - qy) < 2 * via_r + clearance:
                            ok = False
                            break
                if ok:
                    spot = (vx, vy)
                    break
            if spot is None:
                continue
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(MM(px), MM(py)))
            t.SetEnd(pcbnew.VECTOR2I(MM(spot[0]), MM(spot[1])))
            t.SetWidth(MM(track_w))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(gnd)
            board.Add(t)
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(MM(spot[0]), MM(spot[1])))
            v.SetWidth(MM(2 * via_r)); v.SetDrill(MM(via_r))
            v.SetNet(gnd); v.SetViaType(pcbnew.VIATYPE_THROUGH)
            board.Add(v)
            placed.append(spot)
            made.append('%s.%s' % (fp.GetReference(), p.GetNumber()))
    return made


def solid_ground_pads(board, refs):
    for fp in board.GetFootprints():
        if fp.GetReference() not in refs:
            continue
        for p in fp.Pads():
            if p.GetNetname() == 'GNDREF':
                p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)


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
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    o = z.Outline()
    o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(MM(x), MM(y))
    board.Add(z)
    return z


POWER = ('+12V', '-12V', '+5V')


def rip_up(board, rt):
    """Remove every routed track and via, keeping the fan-out stubs and the ground
    vias placed before routing began.

    Stubs are matched on their exact geometry, not on the pad they start from - a
    routed track starts at a pad centre too, so matching by pad would keep copper
    that was supposed to be ripped up.
    """
    stub_geom = {(net, round(ax, 4), round(ay, 4), round(bx, 4), round(by, 4))
                 for net, _layer, ax, ay, bx, by in rt.stubs}
    kept_occ, kept_via = [], []
    for t in list(board.GetTracks()):
        if t.GetClass() == 'PCB_TRACK':
            ax, ay = pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y)
            bx, by = pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)
            if (t.GetNetname(), round(ax, 4), round(ay, 4),
                    round(bx, 4), round(by, 4)) in stub_geom:
                kept_occ.append((t.GetNetname(), R.TOP, ax, ay, bx, by))
                continue
            board.Remove(t)
        elif t.GetClass() == 'PCB_VIA':
            if t.GetNetname() == 'GNDREF':
                kept_via.append((t.GetNetname(), pcbnew.ToMM(t.GetPosition().x),
                                 pcbnew.ToMM(t.GetPosition().y)))
                continue
            board.Remove(t)
    rt.occupied = kept_occ
    rt.vias = kept_via
    rt._cache.clear()


def route_order(rt):
    """Power rails first, then the shortest signal nets.

    The rails are twice as wide as a signal track and touch every IC on the board,
    so they need the open channels while there still are some; left until last they
    simply do not fit.  Among the signals, shortest first - the feedback loops beside
    each op-amp have nowhere else to go, while the long runs to the panel connector
    can afford to detour.
    """
    spans = []
    for net in set(p['net'] for p in rt.pads):
        if not net or net == 'GNDREF':
            continue
        pts = [(p['x'], p['y']) for p in rt.pads if p['net'] == net]
        if len(pts) < 2:
            continue
        w = max(x for x, y in pts) - min(x for x, y in pts)
        h = max(y for x, y in pts) - min(y for x, y in pts)
        spans.append((0 if net in POWER else 1, math.hypot(w, h), net))
    return [n for _, _, n in sorted(spans)]


def run(pcb_path, sch_path, outline, gnd_vias=(), smd_refs=(), keepout_ics=(),
        solid_refs=(), power_width=0.6, signal_width=0.3, keepout_margin=0.6,
        stitch_step=7.0, front_pour=False, rounds=3,
        keepout_pins=(), pin_keepout_margin=0.8, back_cost=None,
        clearance=0.25):
    board = pcbnew.LoadBoard(pcb_path)
    if gnd_vias:
        add_gnd_vias(board, gnd_vias)
    if smd_refs:
        auto_gnd_vias(board, set(smd_refs))
    # clearance is a per-board lever: the project's own DRC minimum is 0.20 mm,
    # and 0.05 mm off the track pitch is about ten percent more routing channel
    rt = R.Router(board, outline, clearance=clearance)
    for ref in keepout_ics:
        fps = [f for f in board.GetFootprints() if f.GetReference() == ref]
        if not fps:
            continue
        bb = fps[0].GetBoundingBox(False, False)
        m = keepout_margin
        rt.keepout.append((R.BOT,
                           pcbnew.ToMM(bb.GetLeft()) - m, pcbnew.ToMM(bb.GetTop()) - m,
                           pcbnew.ToMM(bb.GetRight()) + m, pcbnew.ToMM(bb.GetBottom()) + m))
    # Connectors get a keepout over the pad ROW only, not the whole body.  What
    # strands a pocket of plane is a track threaded between two pins 2.5 mm apart;
    # forbidding that costs almost no routing area, whereas blocking the back under
    # the entire connector left its twelve nets no room to escape.
    for ref in keepout_pins:
        fps = [f for f in board.GetFootprints() if f.GetReference() == ref]
        if not fps:
            continue
        xs, ys = [], []
        for p in fps[0].Pads():
            pb = p.GetBoundingBox()
            xs += [pcbnew.ToMM(pb.GetLeft()), pcbnew.ToMM(pb.GetRight())]
            ys += [pcbnew.ToMM(pb.GetTop()), pcbnew.ToMM(pb.GetBottom())]
        if not xs:
            continue
        m = pin_keepout_margin
        rt.keepout.append((R.BOT, min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m))
    for t in board.GetTracks():
        if t.GetClass() == 'PCB_TRACK':
            rt.occupied.append((t.GetNetname(), R.TOP,
                                pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y),
                                pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)))
        elif t.GetClass() == 'PCB_VIA':
            rt.vias.append((t.GetNetname(),
                            pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)))
    rt._cache.clear()

    def width_for(n):
        return power_width if n in ('+12V', '-12V', '+5V') else signal_width

    # A fine-pitch pad can be sealed in by its own neighbours, leaving the search
    # no first move to make.  Give only those pads a stub into open copper.
    nets_to_route = route_order(rt)
    stubs = fanout.add_stubs(board, rt, fanout.walled_in(rt, nets_to_route), width_for)

    def one_round(order):
        """Route every net in `order`; returns the ones that would not fit."""
        rt.limit_hits = 0
        bad = []
        for net in order:
            w = width_for(net)
            ok, _, _ = rt.route_net(net, width=w, back=back_cost)
            if not ok:
                bad.append(net)
        if bad:
            # anything that would not fit gets to wander, to use more vias and to
            # spend more time on the back.  A tidy route is better than an untidy
            # one, but a routed net beats an unrouted one.
            retry, bad = bad, []
            for net in retry:
                w = width_for(net)
                relaxed = min(1.5, back_cost) if back_cost else 1.5
                ok, _, _ = rt.route_net(net, width=w, turn=0.8, via=14.0,
                                        back=relaxed)
                if not ok:
                    bad.append(net)
        return bad

    # Rip up and reroute.  A net usually fails not because there is no room for it
    # but because a net routed earlier took the one channel it needed; putting the
    # failures first next time round lets them claim that channel instead.  Nets
    # are ordered by priority, not committed, so each round starts from clean copper.
    order = list(nets_to_route)
    failed = []
    for attempt in range(rounds):
        if attempt:
            rip_up(board, rt)
        failed = one_round(order)
        if not failed:
            break
        # promote the failures, but never ahead of the power rails - they are
        # twice as wide and touch every IC, and a round that routes them late
        # simply fails them instead, which then promotes them, which cycles
        promoted = [n for n in failed if n not in POWER]
        order = ([n for n in order if n in POWER]
                 + promoted
                 + [n for n in order if n not in POWER and n not in promoted])
    fanout.drop_stubs(board, rt, set(failed))
    solid_ground_pads(board, set(solid_refs))
    add_ground_pour(board, outline)
    spots = []
    if front_pour:
        stitch.add_front_pour(board, outline)
        spots, _ = stitch.clear_spots(board, outline, step=stitch_step)
        stitch.add_vias(board, spots)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(pcb_path, board)
    # SaveBoard writes a default .kicad_pro over ours, so restore the real rules
    mkproject.make(sch_path)

    tracks = [t for t in board.GetTracks() if t.GetClass() == 'PCB_TRACK']
    vias = [t for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
    return dict(tracks=len(tracks), vias=len(vias), failed=failed,
                stubs=[s[1] for s in stubs], stitch=len(spots),
                back=sum(1 for t in tracks if t.GetLayer() == pcbnew.B_Cu))
