"""Place the parts around an IC at the pin each one serves.

The layout principle is simply that a part belongs next to the pin it connects to:
that makes every track short, keeps high-impedance nodes compact, and leaves the
channels between packages free for the nets that genuinely have to cross the board.

`want_y` comes from the netlist rather than from hand-written coordinates, so the
placement cannot drift out of step with the schematic the way a literal table does.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexp


def load_nets(path):
    d = sexp.parse(open(path, encoding='utf-8').read())

    def walk(n, tag):
        if isinstance(n, list):
            if n and n[0] == tag:
                yield n
            for c in n:
                yield from walk(c, tag)

    nets = {}
    for n in walk(d, 'net'):
        name = [c[1] for c in n if isinstance(c, list) and c[0] == 'name'][0].strip('"')
        nodes = []
        for nd in n:
            if isinstance(nd, list) and nd[0] == 'node':
                r = [c[1] for c in nd if isinstance(c, list) and c[0] == 'ref'][0].strip('"')
                p = [c[1] for c in nd if isinstance(c, list) and c[0] == 'pin'][0].strip('"')
                nodes.append((r, p))
        nets[name] = nodes
    return nets


def dip_pins(cx, cy, n=14, pitch=2.54, row=7.62):
    """Pin centres of a DIP at rotation 0.

    KiCad's DIP footprints run pin 1 down the left side and back up the right,
    so pin 1 is top-left and pin n is top-right.
    """
    half = n // 2
    out = {}
    y0 = cy - pitch * (half - 1) / 2.0
    for i in range(1, half + 1):
        out[str(i)] = (cx - row / 2.0, y0 + (i - 1) * pitch)
    for i in range(half + 1, n + 1):
        out[str(i)] = (cx + row / 2.0, y0 + (n - i) * pitch)
    return out


def want_y(nets, ref, ic, pins, ignore=('GNDREF', '+12V', '-12V', '+5V')):
    """The y of the IC pin this part serves; the mean if it serves several."""
    ys = []
    for name, nodes in nets.items():
        if name in ignore:
            continue
        if (ref, '1') in nodes or (ref, '2') in nodes or any(r == ref for r, _ in nodes):
            if not any(r == ref for r, _ in nodes):
                continue
            for r, p in nodes:
                if r == ic and p in pins:
                    ys.append(pins[p][1])
    return sum(ys) / len(ys) if ys else None


def spread(items, pitch, lo=None, hi=None):
    """Order-preserving placement with a minimum spacing, as close to each
    requested y as least squares allows (pool-adjacent-violators)."""
    items = sorted(items, key=lambda t: t[1])
    n = len(items)
    if not n:
        return {}
    z = [items[i][1] - i * pitch for i in range(n)]
    vals, wts = [], []
    for v in z:
        vals.append(float(v))
        wts.append(1)
        while len(vals) > 1 and vals[-2] > vals[-1]:
            v2, w2 = vals.pop(), wts.pop()
            v1, w1 = vals.pop(), wts.pop()
            vals.append((v1 * w1 + v2 * w2) / (w1 + w2))
            wts.append(w1 + w2)
    flat = []
    for v, w in zip(vals, wts):
        flat.extend([v] * w)
    ys = [flat[i] + i * pitch for i in range(n)]
    shift = 0.0
    if lo is not None and ys[0] + shift < lo:
        shift = lo - ys[0]
    if hi is not None and ys[-1] + shift > hi:
        shift = min(shift, hi - ys[-1])
        if ys[0] + shift < lo if lo is not None else False:
            shift = (lo - ys[0] + hi - ys[-1]) / 2.0
    return {items[i][0]: round(ys[i] + shift, 2) for i in range(n)}


def pin_xy(fpid, rot, cx, cy):
    """Absolute pad centres of a part placed at (cx, cy) with this rotation."""
    import autoplace
    return {k: (cx + dx, cy + dy)
            for k, (dx, dy) in autoplace.pad_offsets(fpid, rot).items()}


PWR = ('GNDREF', '+12V', '-12V', '+5V')


def part_nets(nets):
    out = {}
    for name, nodes in nets.items():
        for r, p in nodes:
            out.setdefault(r, []).append((name, p))
    return out


def serves(nets, pnets, ref, ic, pins, ignore=PWR):
    """(want_y, own_pad) - the y of the IC pin(s) this part serves, and which of
    the part's own pads carries that connection."""
    ys, mine = [], []
    for name, p in pnets.get(ref, ()):
        if name in ignore:
            continue
        for r2, p2 in nets[name]:
            if r2 == ic and p2 in pins:
                ys.append(pins[p2][1])
                mine.append(p)
    if not ys:
        return None, None
    return sum(ys) / len(ys), mine[0]


def facing(own_pad, side, fpid, rot_a=0, rot_b=180):
    """Rotation that turns the part's IC-facing pad toward the IC.

    `side` is -1 when the part sits left of the IC (so the connecting pad must end
    up on the part's right) and +1 when it sits right of it.
    """
    import autoplace
    for rot in (rot_a, rot_b):
        off = autoplace.pad_offsets(fpid, rot)
        if own_pad in off and off[own_pad][0] * -side >= 0:
            return rot
    return rot_a


def widen_channels(place, comps, ics, target=3.2, margin=2.0, board=None,
                   rounds=6, reach=14.0):
    """Push parts away from fine-pitch ICs until each has a real fan-out channel.

    Nothing fits between pads 1.27 mm apart, so every pin of a SOIC has to escape
    straight outward, and the clear space beside the package is what decides whether
    the board routes at all.  U103 had 1.54 mm - room for a single track against
    seven pins.  Solving that by hand meant moving one column, which collided with
    the next, which collided with the one after; this does the same thing as a
    relaxation and cascades the pushes properly.
    """
    import crtyd
    place = dict(place)

    def box(r, p=None):
        x, y, rot = p or place[r]
        a, b, c, d = crtyd.extent(comps[r]['fp'], rot)
        return (x + a, y + b, x + c, y + d)

    moved = {}
    for _ in range(rounds):
        shifted = False
        for ic in ics:
            if ic not in place:
                continue
            u = box(ic)
            # only genuinely adjacent parts: something 50 mm away shares the row
            # but is not in this package's channel, and shoving it is how the first
            # version of this walked half the board off the edge
            band = [r for r in place
                    if r in comps and r != ic and r not in ics
                    and not (box(r)[3] < u[1] or box(r)[1] > u[3])
                    and box(r)[0] < u[2] + reach and box(r)[2] > u[0] - reach]
            # left of the package: order by how close they are, push the nearest
            # first and let it shove its own neighbour along
            left = sorted((r for r in band if box(r)[2] <= u[0]),
                          key=lambda r: -box(r)[2])
            limit = u[0] - target
            for r in left:
                bb = box(r)
                if bb[2] <= limit:
                    limit = min(limit, bb[0] - 0.6)
                    continue
                d = bb[2] - limit
                x, y, rot = place[r]
                place[r] = (round(x - d, 2), y, rot)
                moved[r] = round(moved.get(r, 0) - d, 2)
                shifted = True
                limit = box(r)[0] - 0.6
            right = sorted((r for r in band if box(r)[0] >= u[2]),
                           key=lambda r: box(r)[0])
            limit = u[2] + target
            for r in right:
                bb = box(r)
                if bb[0] >= limit:
                    limit = max(limit, bb[2] + 0.6)
                    continue
                d = limit - bb[0]
                x, y, rot = place[r]
                place[r] = (round(x + d, 2), y, rot)
                moved[r] = round(moved.get(r, 0) + d, 2)
                shifted = True
                limit = box(r)[2] + 0.6
        if not shifted:
            break

    off = []
    if board:
        x0, y0, x1, y1 = board
        for r in place:
            if r not in comps:
                continue
            bb = box(r)
            if bb[0] < x0 + margin or bb[2] > x1 - margin:
                off.append(r)
    return place, moved, off
