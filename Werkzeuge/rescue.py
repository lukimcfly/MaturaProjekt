"""Rip up the neighbours of a net that will not route, then put them back.

The global rip-up in `routeboard` throws away *everything* and reorders, which is a
blunt instrument: it re-routes forty-five nets to help one.  This is the targeted
version - find the handful of nets whose copper is actually crowding the failed
one, remove only those, route the failed net first while the space is free, then
route the neighbours again around it.

That ordering is the whole point.  A net fails because it arrives last; giving it
first refusal over its own immediate neighbourhood is what a person does by hand.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import router as R


def crowding_nets(rt, net, radius=6.0, most=8):
    """Nets whose copper lies near this one's pads, nearest first."""
    pads = []
    for p in rt.pads:
        if p['net'] == net:
            pads.append((p['x'], p['y']))
    if not pads:
        return []
    near = {}
    for onet, layer, ax, ay, bx, by in rt.occupied:
        if onet == net or onet == 'GNDREF' or not onet:
            continue
        mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
        d = min(math.hypot(mx - px, my - py) for px, py in pads)
        if d < radius and (onet not in near or d < near[onet]):
            near[onet] = d
    return [n for n, _ in sorted(near.items(), key=lambda kv: kv[1])][:most]


def strip(board, rt, nets):
    """Remove those nets' routed copper from the board and from the router's view."""
    stub_geom = {(n, round(ax, 4), round(ay, 4), round(bx, 4), round(by, 4))
                 for n, _l, ax, ay, bx, by in rt.stubs}
    gone = 0
    for t in list(board.GetTracks()):
        if t.GetNetname() not in nets:
            continue
        if t.GetClass() == 'PCB_TRACK':
            key = (t.GetNetname(),
                   round(pcbnew.ToMM(t.GetStart().x), 4), round(pcbnew.ToMM(t.GetStart().y), 4),
                   round(pcbnew.ToMM(t.GetEnd().x), 4), round(pcbnew.ToMM(t.GetEnd().y), 4))
            if key in stub_geom:
                continue                      # a fan-out stub is not routed copper
        board.Remove(t)
        gone += 1
    rt.occupied = [o for o in rt.occupied
                   if o[0] not in nets
                   or (o[0], round(o[2], 4), round(o[3], 4),
                       round(o[4], 4), round(o[5], 4)) in stub_geom]
    rt.vias = [v for v in rt.vias if v[0] not in nets]
    rt._cache.clear()
    return gone


def rescue(board, rt, net, width_for, radius=6.0, most=8, **kw):
    """Try to route `net` by clearing its neighbourhood first.

    Returns (routed_ok, [nets that could not be put back]).
    """
    neighbours = crowding_nets(rt, net, radius=radius, most=most)
    if not neighbours:
        return False, []
    strip(board, rt, set(neighbours))
    ok, _, _ = rt.route_net(net, width=width_for(net), **kw)
    lost = []
    for n in neighbours:                      # put the neighbours back around it
        good, _, _ = rt.route_net(n, width=width_for(n), **kw)
        if not good:
            lost.append(n)
    return ok, lost
