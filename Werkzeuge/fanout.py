"""Fan-out stubs for pads the router cannot escape from.

The router works on a 0.25 mm grid.  That is fine for a 2.54 mm DIP and for
1.27 mm SOIC, but a 0.65 mm-pitch package can leave a gap between pads that no
grid cell fits into, and then a pin has literally nowhere to start from - the
search fails before it begins.  A person laying this out by hand would draw a
short stub straight out of the package into open space and start from there, so
that is what this does.

It is deliberately narrow in scope.  Fanning out every fine-pitch pin instead of
only the trapped ones produced shorts, solder-mask bridges and a dozen dangling
stubs, because most of those pins could already escape perfectly well and the
extra copper only got in the way.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import router as R

MM = pcbnew.FromMM


def _escapes(rt, net):
    """{pad key: number of free cells adjacent to that pad}."""
    pc = rt.own_pad_cells(net)
    top, bot = rt.obstacles(net)
    blocked = {R.TOP: top, R.BOT: bot}
    mine = set().union(*pc.values()) if pc else set()
    out = {}
    for key, cells in pc.items():
        n = 0
        for c in cells:
            for dx, dy, _ in R.Router.NEIGH:
                nb = (c[0] + dx, c[1] + dy, c[2])
                if nb in cells or not rt.inside((nb[0], nb[1])):
                    continue
                if nb in mine or (nb[0], nb[1]) not in blocked[nb[2]]:
                    n += 1
        out[key] = n
    return out


def walled_in(rt, nets):
    """Pads with no way off them at all."""
    bad = []
    for net in nets:
        for key, n in _escapes(rt, net).items():
            if n == 0:
                bad.append((net, key))
    return bad


def add_stubs(board, rt, pads, width_for, lengths=(1.6, 1.2, 0.9)):
    """Draw a stub out of each trapped pad, into the first clear spot found.

    Returns [(net, ref.pad, length)] for the stubs actually drawn.
    """
    made = []
    bypos = {}
    for fp in board.GetFootprints():
        for p in fp.Pads():
            bypos[(fp.GetReference(), p.GetNumber())] = (fp, p)
    for net, key in pads:
        ref, num = key[0], key[1]
        if (ref, num) not in bypos:
            continue
        fp, pad = bypos[(ref, num)]
        c = fp.GetPosition()
        px, py = pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y)
        dx, dy = px - pcbnew.ToMM(c.x), py - pcbnew.ToMM(c.y)
        if abs(dx) >= abs(dy):
            ux, uy = (1.0 if dx >= 0 else -1.0), 0.0
        else:
            ux, uy = 0.0, (1.0 if dy >= 0 else -1.0)
        top, _ = rt.obstacles(net)
        own = set()
        for cells in rt.own_pad_cells(net).values():
            own |= {(a, b) for a, b, _ in cells}
        for L in lengths:
            ex, ey = px + ux * L, py + uy * L
            steps = max(2, int(L / (R.GRID / 2)))
            clear = True
            for k in range(1, steps + 1):
                t = k / steps
                cx, cy = rt.cell(px + ux * L * t, py + uy * L * t)[:2]
                if not rt.inside((cx, cy)):
                    clear = False
                    break
                if (cx, cy) in top and (cx, cy) not in own:
                    clear = False
                    break
            if not clear:
                continue
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(MM(px), MM(py)))
            t.SetEnd(pcbnew.VECTOR2I(MM(ex), MM(ey)))
            t.SetWidth(MM(width_for(net)))
            t.SetLayer(pcbnew.F_Cu)
            t.SetNet(pad.GetNet())
            board.Add(t)
            rt.occupied.append((net, R.TOP, px, py, ex, ey))
            rt.stubs.append((net, R.TOP, px, py, ex, ey))
            made.append((net, '%s.%s' % (ref, num), L))
            break
    if made:
        rt._cache.clear()
    return made


def drop_stubs(board, rt, nets):
    """Remove the stubs of nets that ended up unrouted, so they are not left on the
    board as dangling copper.

    Matched on exact geometry from `rt.stubs`, not on the pad they start from: a
    routed track starts at a pad centre too, and a net that routed only partly
    would otherwise have real copper deleted along with its stub.
    """
    if not nets:
        return 0
    want = {(net, round(ax, 4), round(ay, 4), round(bx, 4), round(by, 4))
            for net, _layer, ax, ay, bx, by in rt.stubs if net in nets}
    if not want:
        return 0
    n = 0
    for t in list(board.GetTracks()):
        if t.GetClass() != 'PCB_TRACK':
            continue
        key = (t.GetNetname(),
               round(pcbnew.ToMM(t.GetStart().x), 4), round(pcbnew.ToMM(t.GetStart().y), 4),
               round(pcbnew.ToMM(t.GetEnd().x), 4), round(pcbnew.ToMM(t.GetEnd().y), 4))
        if key in want:
            board.Remove(t)
            n += 1
    return n
