"""A small two-layer maze router for these boards.

B.Cu is mostly a ground pour, so the router strongly prefers F.Cu and only drops to
the back when it has no other way through - each via costs the equivalent of several
millimetres of track, so the plane stays as close to solid as the board allows.

A* on a 0.25 mm grid over (x, y, layer), 8-directional, with a turn penalty so runs
come out straight instead of staircased.  Each net is grown as a tree: every new pad
is routed to whatever of that net is already down, not back to the first pad.
"""
import sys, os, math, heapq
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew

GRID = 0.25          # mm
TURN = 2.5           # cost of changing direction
VIA = 24.0           # cost of changing layer (grid steps) - keeps the plane intact
VIA_R = 0.4          # via radius: a via needs more room than the track leading to it
LIMIT = 1200000      # A* states before giving up
HWEIGHT = 1.1        # heuristic weight.
# A greedier heuristic (1.5) was tried while the budget was small: it found paths
# sooner but worse ones, and a worse path blocks the next net - the filter board
# went from routing completely to failing a net on nothing but that change.  With
# LIMIT raised four-fold the search can afford to stay close to admissible.
BACK = 3.0           # cost per grid step on the back layer.
# The back layer IS the ground plane on a two-layer board, so every millimetre of
# track there is a slot cut through it.  Charging three times the price per step
# (rather than only charging for the via) makes the router treat the back as a
# place to hop across something, not a place to travel.
MM = pcbnew.FromMM
TOP, BOT = 0, 1


def to_mm(v):
    return pcbnew.ToMM(v)


class Router:
    def __init__(self, board, outline, track_w=0.3, clearance=0.25, inset=0.6):
        self.b = board
        self.tw = track_w
        self.cl = clearance
        x0, y0, x1, y1 = outline
        self.ox, self.oy = x0 + inset, y0 + inset
        self.nx = int((x1 - x0 - 2 * inset) / GRID)
        self.ny = int((y1 - y0 - 2 * inset) / GRID)
        self.pads = []
        for fp in board.GetFootprints():
            for p in fp.Pads():
                bb = p.GetBoundingBox()
                through = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
                self.pads.append({
                    'pad': p,
                    'ref': fp.GetReference(), 'num': p.GetNumber(),
                    'net': p.GetNetname(), 'through': through,
                    'layer': TOP if p.IsOnLayer(pcbnew.F_Cu) else BOT,
                    'x': to_mm(p.GetPosition().x), 'y': to_mm(p.GetPosition().y),
                    'box': (to_mm(bb.GetLeft()), to_mm(bb.GetTop()),
                            to_mm(bb.GetRight()), to_mm(bb.GetBottom())),
                })
        self.pads.sort(key=lambda p: (p['ref'], len(p['num']), p['num']))
        self._cache = {}
        self.keepout = []       # (layer, x0, y0, x1, y1) - routing forbidden
        self.occupied = []      # (net, layer, x0,y0,x1,y1)
        self.vias = []          # (net, x, y)
        self.stubs = []         # (net, layer, x0,y0,x1,y1) fan-out only
        self.limit_hits = 0     # searches that ran out of budget, not of room

    # ---- grid helpers ---------------------------------------------------
    def cell(self, x, y):
        return (int(round((x - self.ox) / GRID)), int(round((y - self.oy) / GRID)))

    def pos(self, c):
        return (self.ox + c[0] * GRID, self.oy + c[1] * GRID)

    def inside(self, c):
        return 0 <= c[0] < self.nx and 0 <= c[1] < self.ny

    def _rect_cells(self, box, margin):
        x0, y0, x1, y1 = box
        c0 = self.cell(x0 - margin, y0 - margin)
        c1 = self.cell(x1 + margin, y1 + margin)
        for i in range(c0[0], c1[0] + 1):
            for j in range(c0[1], c1[1] + 1):
                yield (i, j)

    def obstacles(self, net, extra=0.0):
        """(blocked_top, blocked_bot) for copper of `net`.

        `extra` widens the margin - used for vias, which are fatter than the
        track that leads into them and so need their own, stricter map."""
        key = (net, extra, self.tw)
        if key in self._cache:
            return self._cache[key]
        margin = self.cl + self.tw / 2.0 + extra
        top, bot = set(), set()
        for p in self.pads:
            if p['net'] == net:
                continue
            cells = list(self._rect_cells(p['box'], margin))
            if p['through']:
                top.update(cells); bot.update(cells)
            elif p['layer'] == TOP:
                top.update(cells)
            else:
                bot.update(cells)
        for onet, layer, ax, ay, bx, by in self.occupied:
            if onet == net:
                continue
            tgt = top if layer == TOP else bot
            n = max(2, int(math.hypot(bx - ax, by - ay) / (GRID / 2)))
            for k in range(n + 1):
                t = k / n
                for c in self._rect_cells((ax + (bx - ax) * t, ay + (by - ay) * t,
                                           ax + (bx - ax) * t, ay + (by - ay) * t),
                                          margin + self.tw / 2.0):
                    tgt.add(c)
        for layer, kx0, ky0, kx1, ky1 in self.keepout:
            tgt = top if layer == TOP else bot
            for c in self._rect_cells((kx0, ky0, kx1, ky1), 0.0):
                tgt.add(c)
        for onet, vx, vy in self.vias:
            if onet == net:
                continue
            for c in self._rect_cells((vx, vy, vx, vy), 0.4 + margin):
                top.add(c); bot.add(c)
        self._cache[key] = (top, bot)
        return top, bot

    def pad_centres(self, net):
        out, seen = {}, {}
        for p in self.pads:
            if p['net'] != net:
                continue
            k = (p['ref'], p['num'])
            seen[k] = seen.get(k, 0) + 1
            out[(p['ref'], p['num'], seen[k])] = (p['x'], p['y'])
        return out

    def own_pad_cells(self, net):
        out, seen = {}, {}
        for p in self.pads:
            if p['net'] != net:
                continue
            k = (p['ref'], p['num'])
            seen[k] = seen.get(k, 0) + 1
            key = (p['ref'], p['num'], seen[k])
            layers = (TOP, BOT) if p['through'] else (p['layer'],)
            cells = set()
            for c in self._rect_cells(p['box'], 0.0):
                if not self.inside(c):
                    continue
                x, y = self.pos(c)
                # the bounding box overshoots a round pad - test the real shape,
                # otherwise a branch can start on bare laminate
                if not p['pad'].HitTest(pcbnew.VECTOR2I(MM(x), MM(y)), 0):
                    continue
                for L in layers:
                    cells.add((c[0], c[1], L))
            if not cells:
                cx, cy = self.cell(p['x'], p['y'])
                cells = {(cx, cy, L) for L in layers}
            out[key] = cells
        # pre-placed fan-out stubs are copper of this net: fold each one into the
        # pad it grows from, so reaching the stub end counts as reaching the pad.
        # Only stubs - folding ordinary routed copper would make a second attempt
        # at a net think its pads were already one object.
        for onet, layer, ax, ay, bx, by in self.stubs:
            if onet != net:
                continue
            start = self.cell(ax, ay)
            best = None
            for key, cells in out.items():
                if (start[0], start[1], layer) in cells:
                    best = key
                    break
            if best is None:
                continue
            n = max(2, int(math.hypot(bx - ax, by - ay) / (GRID / 2)))
            for k in range(n + 1):
                t = k / n
                c = self.cell(ax + (bx - ax) * t, ay + (by - ay) * t)
                if self.inside(c):
                    out[best].add((c[0], c[1], layer))
        return out

    # ---- A* -------------------------------------------------------------
    NEIGH = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
             (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]

    def astar(self, sources, targets, blk, free, blkv=None, turn=None, via=None,
              back=None):
        if not sources or not targets:
            return None
        tx = sum(c[0] for c in targets) / len(targets)
        ty = sum(c[1] for c in targets) / len(targets)
        def h(c):
            return math.hypot(c[0] - tx, c[1] - ty)
        def ok(c):
            if not self.inside((c[0], c[1])):
                return False
            if c in free:
                return True
            return (c[0], c[1]) not in blk[c[2]]

        def via_ok(c):
            """a via sits on both layers, so both must be clear at via width"""
            if blkv is None:
                return True
            if c in free:
                return True
            xy = (c[0], c[1])
            return xy not in blkv[TOP] and xy not in blkv[BOT]
        turncost = TURN if turn is None else turn
        viacost = VIA if via is None else via
        backcost = BACK if back is None else back
        openq, g, came, seen = [], {}, {}, set()
        for s in sources:
            if not ok(s):
                continue
            g[(s, (0, 0))] = 0.0
            heapq.heappush(openq, (h(s), s, (0, 0)))
        tset = set(targets)
        while openq:
            if len(seen) > LIMIT:
                self.limit_hits += 1
                return None
            _, cur, d = heapq.heappop(openq)
            if (cur, d) in seen:
                continue
            seen.add((cur, d))
            if cur in tset:
                path, k = [cur], (cur, d)
                while k in came:
                    k = came[k]
                    path.append(k[0])
                return path[::-1]
            base = g[(cur, d)]
            # same-layer moves
            for dx, dy, w in self.NEIGH:
                n = (cur[0] + dx, cur[1] + dy, cur[2])
                if not ok(n):
                    continue
                if dx and dy:
                    if not ok((cur[0] + dx, cur[1], cur[2])) or not ok((cur[0], cur[1] + dy, cur[2])):
                        continue
                nd = (dx, dy)
                step = w * (backcost if cur[2] == BOT else 1.0)
                ng = base + step + (turncost if d != (0, 0) and nd != d else 0.0)
                if ng < g.get((n, nd), 1e18):
                    g[(n, nd)] = ng
                    came[(n, nd)] = (cur, d)
                    heapq.heappush(openq, (ng + h(n) * HWEIGHT, n, nd))
            # layer change
            n = (cur[0], cur[1], 1 - cur[2])
            if ok(n) and via_ok(n) and via_ok(cur):
                ng = base + viacost
                if ng < g.get((n, (0, 0)), 1e18):
                    g[(n, (0, 0))] = ng
                    came[(n, (0, 0))] = (cur, d)
                    heapq.heappush(openq, (ng + h(n) * HWEIGHT, n, (0, 0)))
        return None

    # ---- path -> copper --------------------------------------------------
    def simplify(self, path):
        pts = [path[0]]
        for i in range(1, len(path) - 1):
            a = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1], path[i][2] - path[i - 1][2])
            b = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1], path[i + 1][2] - path[i][2])
            if a != b:
                pts.append(path[i])
        pts.append(path[-1])
        return pts

    def add_path(self, net_name, pts, start_xy=None, end_xy=None):
        """pts are grid cells; start_xy/end_xy snap the ends onto real pad centres
        so KiCad sees a connection rather than a dangling track end."""
        ni = self.b.FindNet(net_name)
        layer_of = {TOP: pcbnew.F_Cu, BOT: pcbnew.B_Cu}
        mm = [(self.pos((c[0], c[1]))[0], self.pos((c[0], c[1]))[1], c[2]) for c in pts]
        # APPEND the pad centre rather than moving the grid endpoint - other
        # branches of this net start from those grid cells and need copper there
        if start_xy:
            mm.insert(0, (start_xy[0], start_xy[1], mm[0][2]))
        if end_xy:
            mm.append((end_xy[0], end_xy[1], mm[-1][2]))
        for a, b in zip(mm, mm[1:]):
            if a[2] != b[2]:                      # via
                x, y = a[0], a[1]
                if any(o == net_name and abs(vx - x) < 1e-6 and abs(vy - y) < 1e-6
                       for o, vx, vy in self.vias):
                    continue          # two branches met here; one via is enough
                v = pcbnew.PCB_VIA(self.b)
                v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
                v.SetWidth(MM(0.8)); v.SetDrill(MM(0.4))
                v.SetNet(ni); v.SetViaType(pcbnew.VIATYPE_THROUGH)
                self.b.Add(v)
                self.vias.append((net_name, x, y))
                continue
            ax, ay = a[0], a[1]
            bx, by = b[0], b[1]
            if abs(ax - bx) < 1e-6 and abs(ay - by) < 1e-6:
                continue
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(pcbnew.VECTOR2I(MM(ax), MM(ay)))
            t.SetEnd(pcbnew.VECTOR2I(MM(bx), MM(by)))
            t.SetWidth(MM(self.tw))
            t.SetLayer(layer_of[a[2]])
            t.SetNet(ni)
            self.b.Add(t)
            self.occupied.append((net_name, a[2], ax, ay, bx, by))
        self._cache.clear()

    # ---- route one net --------------------------------------------------
    def route_net(self, net_name, width=None, turn=None, via=None,
                  back=None, partial=False):
        if width:
            self.tw = width
        pc = self.own_pad_cells(net_name)
        if len(pc) < 2:
            return True, 0, 0
        centres = self.pad_centres(net_name)
        free = set().union(*pc.values())
        keys = sorted(pc.keys())
        # start from the pad nearest the net's centroid: deterministic, and it
        # grows a compact tree instead of a chain from whichever pad came first
        cx = sum(centres[k][0] for k in keys) / len(keys)
        cy = sum(centres[k][1] for k in keys) / len(keys)
        first = min(keys, key=lambda k: (centres[k][0]-cx)**2 + (centres[k][1]-cy)**2)
        tree = set(pc[first])
        done = {first}
        nseg = nvia = 0
        pending = []
        while len(done) < len(keys):
            top, bot = self.obstacles(net_name)
            tv, bv = self.obstacles(net_name, extra=VIA_R - self.tw / 2.0)
            blk = {TOP: top, BOT: bot}
            blkv = {TOP: tv, BOT: bv}
            best = None
            for k in keys:
                if k in done:
                    continue
                p = self.astar(tree, pc[k], blk, free, blkv, turn=turn, via=via,
                               back=back)
                if p and (best is None or len(p) < len(best[1])):
                    best = (k, p)
            if best is None:
                if partial:
                    # last attempt: keep the branches that did route
                    for pts, s_xy, e_xy in pending:
                        self.add_path(net_name, pts, start_xy=s_xy, end_xy=e_xy)
                return False, nseg, nvia
            k, path = best
            pts = self.simplify(path)
            # snap onto the pad centre at each end that actually lands on a pad
            s_xy = centres[first] if tuple(path[0]) in pc[first] and len(done) == 1 else None
            pending.append((pts, s_xy, centres[k]))
            nvia += sum(1 for a, b in zip(pts, pts[1:]) if a[2] != b[2])
            nseg += sum(1 for a, b in zip(pts, pts[1:]) if a[2] == b[2])
            tree |= set(path) | pc[k]
            done.add(k)
        for pts, s_xy, e_xy in pending:
            self.add_path(net_name, pts, start_xy=s_xy, end_xy=e_xy)
        return True, nseg, nvia
