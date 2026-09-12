"""Build a .kicad_pcb from a board netlist plus an explicit placement table.

Placement is hand-designed per board (see tools/place_*.py) rather than generated,
because part position is the part of PCB design that actually carries the engineering.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import netlib, sexp

FPDIR = r'C:\Program Files\KiCad\10.0\share\kicad\footprints'
MM = pcbnew.FromMM


def vec(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def centre_on(fp, x, y, rot):
    """Place a footprint so its PAD CENTROID lands on (x, y).

    KiCad THT footprints put their origin on pad 1, not in the middle, so a naive
    SetPosition leaves every part offset by half its length.  Setting the rotation
    first and then correcting by the measured centroid is exact for any angle.
    """
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(vec(x, y))
    pads = list(fp.Pads())
    if not pads:
        return
    cx = sum(p.GetPosition().x for p in pads) / len(pads)
    cy = sum(p.GetPosition().y for p in pads) / len(pads)
    pos = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(int(pos.x + (MM(x) - cx)),
                                   int(pos.y + (MM(y) - cy))))


def load_fp(fpid):
    lib, name = fpid.split(':')
    fp = pcbnew.FootprintLoad(os.path.join(FPDIR, lib + '.pretty'), name)
    if fp is None:
        raise RuntimeError('footprint not found: ' + fpid)
    return fp


def symbol_uuids(sch_path):
    """ref -> schematic symbol uuid, so each footprint can be linked back."""
    out = {}
    for s in sexp.load(sch_path):
        if not isinstance(s, list) or sexp.head(s) != 'symbol':
            continue
        ref = sexp.prop(s, 'Reference')
        uid = sexp.val(s, 'uuid')
        if ref and uid and not ref.startswith('#'):
            out[ref] = uid
    return out


def build(netfile, placement, outline, holes, out_path, labels=(), sch_path=None):
    comps, nets, libparts = netlib.load(netfile)
    board = pcbnew.CreateEmptyBoard()

    # ---- nets -------------------------------------------------------------
    netmap = {}
    for n in sorted(nets):
        if n.startswith('unconnected'):
            continue
        ni = pcbnew.NETINFO_ITEM(board, n)
        board.Add(ni)
        netmap[n] = ni
    padnet = {}
    for n, pins in nets.items():
        if n.startswith('unconnected'):
            continue
        for r, p, fn, t in pins:
            padnet[(r, str(p))] = n

    # ---- footprints -------------------------------------------------------
    missing = [r for r in comps if r not in placement]
    if missing:
        raise RuntimeError('no placement for: ' + ', '.join(sorted(missing)))
    unused = [r for r in placement if r not in comps]
    if unused:
        raise RuntimeError('placement for parts not on this board: ' + ', '.join(unused))

    uuids = symbol_uuids(sch_path) if sch_path else {}
    for ref, (x, y, rot) in sorted(placement.items()):
        c = comps[ref]
        fp = load_fp(c['fp'])
        fp.SetReference(ref)
        fp.SetValue(c['value'])
        centre_on(fp, x, y, rot)
        # reference text always upright and just above the body, whatever the
        # part's rotation - otherwise a 180-degree part throws its label onto its
        # neighbour and the silkscreen reads upside down
        bb = fp.GetBoundingBox(False, False)
        r = fp.Reference()
        r.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        # exactly the project's DRC minimum: the library default is sized for a
        # roomier board, and at this density it is the labels, not the parts, that
        # run out of room.  Going below 1.0 mm / 0.15 mm trips min_text_height.
        r.SetTextSize(pcbnew.VECTOR2I(MM(1.0), MM(1.0)))
        r.SetTextThickness(MM(0.15))
        r.SetPosition(pcbnew.VECTOR2I(int((bb.GetLeft() + bb.GetRight()) / 2),
                                      int(bb.GetTop() - MM(0.9))))
        if ref in uuids:
            # link the footprint to its schematic symbol, otherwise
            # "Update PCB from Schematic" cannot match them up
            fp.SetPath(pcbnew.KIID_PATH('/' + uuids[ref]))
        board.Add(fp)
        for pad in fp.Pads():
            nn = padnet.get((ref, pad.GetNumber()))
            if nn:
                pad.SetNet(netmap[nn])

    # ---- mounting holes ---------------------------------------------------
    for i, (x, y) in enumerate(holes, 1):
        fp = load_fp('MountingHole:MountingHole_3.2mm_M3')
        fp.SetReference('H%d' % i)
        fp.SetPosition(vec(x, y))
        fp.Reference().SetVisible(False)   # a hole needs no silkscreen label
        fp.Value().SetVisible(False)
        board.Add(fp)

    # ---- board outline ----------------------------------------------------
    x0, y0, x1, y1 = outline
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(vec(*a))
        s.SetEnd(vec(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        board.Add(s)

    for text, tx, ty, size in labels:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetPosition(vec(tx, ty))
        t.SetLayer(pcbnew.F_SilkS)
        size = max(size, 1.0)                     # project rule: min text height 1.0 mm
        t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
        t.SetTextThickness(MM(max(0.15, size * 0.16)))
        board.Add(t)

    _tidy_refs(board, outline)
    pcbnew.SaveBoard(out_path, board)
    return board, comps, nets


def _tidy_refs(board, outline=None, passes=5):
    """Move each reference label off whatever it lands on.

    Scores every candidate spot by how much it still overlaps and keeps the best
    one, rather than stopping at the first miss - on a dense board there is often
    no clear spot at all, and the earlier version then left the label wherever it
    happened to try last.  Several passes, because moving one label changes what
    the next one collides with.
    """
    def overlap(a, b):
        dx = min(a.GetRight(), b.GetRight()) - max(a.GetLeft(), b.GetLeft())
        dy = min(a.GetBottom(), b.GetBottom()) - max(a.GetTop(), b.GetTop())
        return (dx / 1e6) * (dy / 1e6) if dx > 0 and dy > 0 else 0.0

    fps = list(board.GetFootprints())
    for _ in range(passes):
        moved = 0
        for fp in fps:
            r = fp.Reference()
            if not r.IsVisible():
                continue
            bb = fp.GetBoundingBox(False, False)
            cx = int((bb.GetLeft() + bb.GetRight()) / 2)
            cy = int((bb.GetTop() + bb.GetBottom()) / 2)
            w2 = int((bb.GetRight() - bb.GetLeft()) / 2)
            h2 = int((bb.GetBottom() - bb.GetTop()) / 2)
            others = []
            for f in fps:
                if f is not fp:
                    others.append(f.GetBoundingBox(False, False))
                    rr = f.Reference()
                    if rr.IsVisible():
                        others.append(rr.GetBoundingBox())
                # a part's OWN silkscreen outline counts too - KiCad's silk
                # clearance check does not exempt a footprint from itself, and a
                # designator sitting on its own connector outline is unreadable
                for d in f.GraphicalItems():
                    if d.GetLayer() == pcbnew.F_SilkS:
                        others.append(d.GetBoundingBox())
            for d in board.GetDrawings():
                if d.GetLayer() == pcbnew.F_SilkS:
                    others.append(d.GetBoundingBox())
            # pads too: silkscreen printed across a solder-mask opening gets
            # clipped by the fab, so the designator would come out chopped
            for f in fps:
                for pad in f.Pads():
                    others.append(pad.GetBoundingBox())
            cands = []
            for d in (0.75, 1.5, 2.6, 3.8, 5.2, 6.8):
                for ox, oy in ((0, -1), (0, 1), (-1, 0), (1, 0),
                               (-1, -1), (1, -1), (-1, 1), (1, 1)):
                    cands.append((cx + ox * (w2 + MM(d)), cy + oy * (h2 + MM(d))))
            best, bestscore = None, None
            for px, py in cands:
                r.SetPosition(pcbnew.VECTOR2I(int(px), int(py)))
                rb = r.GetBoundingBox()
                if outline:
                    x0, y0, x1, y1 = outline
                    if (pcbnew.ToMM(rb.GetLeft()) < x0 + 0.3
                            or pcbnew.ToMM(rb.GetRight()) > x1 - 0.3
                            or pcbnew.ToMM(rb.GetTop()) < y0 + 0.3
                            or pcbnew.ToMM(rb.GetBottom()) > y1 - 0.3):
                        continue          # would be clipped by the board edge
                score = sum(overlap(rb, ob) for ob in others)
                # all else equal prefer the spot nearest the part it names
                score += 0.001 * (abs(px - cx) + abs(py - cy)) / 1e6
                if bestscore is None or score < bestscore:
                    best, bestscore = (px, py), score
                if score == 0:
                    break
            if best:
                r.SetPosition(pcbnew.VECTOR2I(int(best[0]), int(best[1])))
                moved += 1
        if not moved:
            break


def report(board, comps):
    fps = list(board.GetFootprints())
    unassigned = []
    for fp in fps:
        for pad in fp.Pads():
            if pad.GetNetname() == '' and not fp.GetReference().startswith('H'):
                unassigned.append('%s.%s' % (fp.GetReference(), pad.GetNumber()))
    return len(fps), unassigned


def silk_check(board_path):
    """Report silkscreen text that lands on a part body or on other silk text."""
    b = pcbnew.LoadBoard(board_path)
    def box(bb, pad=0.0):
        return (pcbnew.ToMM(bb.GetLeft())-pad, pcbnew.ToMM(bb.GetTop())-pad,
                pcbnew.ToMM(bb.GetRight())+pad, pcbnew.ToMM(bb.GetBottom())+pad)
    bodies, texts = [], []
    for fp in b.GetFootprints():
        bodies.append((fp.GetReference(), box(fp.GetBoundingBox(False, False))))
        for d in fp.GraphicalItems():
            if d.GetLayer() == pcbnew.F_SilkS:
                bodies.append((fp.GetReference() + ' silk', box(d.GetBoundingBox())))
        r = fp.Reference()
        if r.IsVisible() and r.GetLayer() == pcbnew.F_SilkS:
            texts.append((fp.GetReference() + ' (ref)', box(r.GetBoundingBox())))
    for d in b.GetDrawings():
        if d.GetClass() == 'PCB_TEXT' and d.GetLayer() == pcbnew.F_SilkS:
            texts.append(('"%s"' % d.GetText()[:24], box(d.GetBoundingBox())))
    def hit(a, c):
        return a[0] < c[2] and c[0] < a[2] and a[1] < c[3] and c[1] < a[3]
    out = []
    for tn, tb in texts:
        for bn, bb in bodies:
            # a part's own reference belongs near its own body and its own silk;
            # only the bounding boxes touch, and KiCad's silk check agrees
            if tn.split()[0] == bn.split()[0]:
                continue
            if hit(tb, bb):
                out.append('%s over body of %s' % (tn, bn))
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            if hit(texts[i][1], texts[j][1]):
                out.append('%s over %s' % (texts[i][0], texts[j][0]))
    return out
