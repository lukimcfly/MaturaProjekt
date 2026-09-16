"""Finish the two nets the autorouter could not place, on the existing board.

Rebuilding the whole board to solve two nets costs an hour; this loads what is
already routed, reconstructs the router's view of it, and works on just those two.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import router as R
import place_osc, buildall, rescue, mkproject, checkpcb

PCB = 'boards/osc/osc.kicad_pcb'
SCH = 'boards/osc/osc.kicad_sch'


def width_for(n):
    return 0.6 if n in ('+12V', '-12V') else 0.3


def load(keepouts=True):
    """Rebuild the router's view of the board as it stands.

    `keepouts=False` drops the two self-imposed rules - no back-layer copper under
    an IC, none between connector pins - which exist to protect the ground plane.
    For one or two short nets that is a trade worth making knowingly: a small notch
    in the plane costs far less than a hand-soldered wire onto a 1.27 mm pad.
    """
    b = pcbnew.LoadBoard(PCB)
    spec = buildall.BOARDS['osc']
    rt = R.Router(b, place_osc.outline())
    for ref in (spec['keepout'] if keepouts else ()):
        fps = [f for f in b.GetFootprints() if f.GetReference() == ref]
        if not fps:
            continue
        bb = fps[0].GetBoundingBox(False, False)
        m = 0.6
        rt.keepout.append((R.BOT,
                           pcbnew.ToMM(bb.GetLeft()) - m, pcbnew.ToMM(bb.GetTop()) - m,
                           pcbnew.ToMM(bb.GetRight()) + m, pcbnew.ToMM(bb.GetBottom()) + m))
    for ref in (spec['keepout_pins'] if keepouts else ()):
        fps = [f for f in b.GetFootprints() if f.GetReference() == ref]
        if not fps:
            continue
        xs, ys = [], []
        for p in fps[0].Pads():
            pb = p.GetBoundingBox()
            xs += [pcbnew.ToMM(pb.GetLeft()), pcbnew.ToMM(pb.GetRight())]
            ys += [pcbnew.ToMM(pb.GetTop()), pcbnew.ToMM(pb.GetBottom())]
        rt.keepout.append((R.BOT, min(xs) - 0.8, min(ys) - 0.8,
                           max(xs) + 0.8, max(ys) + 0.8))
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_TRACK':
            rt.occupied.append((t.GetNetname(),
                                R.TOP if t.GetLayer() == pcbnew.F_Cu else R.BOT,
                                pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y),
                                pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y)))
        elif t.GetClass() == 'PCB_VIA':
            rt.vias.append((t.GetNetname(), pcbnew.ToMM(t.GetPosition().x),
                            pcbnew.ToMM(t.GetPosition().y)))
    rt._cache.clear()
    return b, rt


def save(b):
    for z in b.Zones():
        z.SetIsFilled(False)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(PCB, b)
    mkproject.make(SCH)


if __name__ == '__main__':
    args = sys.argv[1:]
    relaxed = '--relaxed' in args
    nets = [a for a in args if not a.startswith('--')] or ['/O1_AINV', '/O1_WSEL']
    b, rt = load(keepouts=not relaxed)
    if relaxed:
        print('keepouts lifted for these nets - the plane may take a small notch')
        still = []
        for net in nets:
            t0 = time.time()
            ok, _, _ = rt.route_net(net, width=width_for(net), turn=0.5, via=8.0,
                                    back=1.0, limit=4000000)
            print('%-12s routed=%-5s (%ds)' % (net, ok, time.time() - t0), flush=True)
            if not ok:
                still.append(net)
        print('STILL UNROUTED:', still or 'NONE')
        if len(still) < len(nets):
            save(b)
            print('saved')
        sys.exit(0)
    still = []
    for net in nets:
        t0 = time.time()
        ok, lost = rescue.rescue(b, rt, net, width_for, radius=8.0, most=10,
                                 turn=0.8, via=14.0, back=1.2)
        print('%-12s routed=%-5s neighbours lost=%s  (%ds)'
              % (net, ok, lost or 'none', time.time() - t0), flush=True)
        if not ok:
            still.append(net)
    print('STILL UNROUTED:', still or 'NONE')
    if len(still) < len(nets):
        save(b)
        print('saved')
