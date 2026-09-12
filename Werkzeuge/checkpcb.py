"""One audit for every board: DRC, plane integrity, node extents, silkscreen, rules."""
import sys, os, math, json, subprocess, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
import mkpcb

KICAD = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
mm = pcbnew.ToMM


def drc(pcb, rpt):
    subprocess.run([KICAD, 'pcb', 'drc', '--severity-all', '--format', 'report',
                    '-o', rpt, pcb], capture_output=True, text=True)
    txt = open(rpt, encoding='utf-8').read()
    kinds = collections.Counter()
    for line in txt.splitlines():
        if line.startswith('['):
            kinds[line.split(']')[0][1:]] += 1
    unconn = 0
    for line in txt.splitlines():
        if 'Found' in line and 'unconnected' in line:
            unconn = int(line.split()[2])
    return kinds, unconn


def audit(pcb, ic_refs=(), rpt=None, no_connect=()):
    rpt = rpt or os.path.join('work', os.path.basename(pcb) + '.drc')
    out = {}
    b = pcbnew.LoadBoard(pcb)
    kinds, unconn = drc(pcb, rpt)
    out['drc'] = dict(kinds)
    out['unconnected'] = unconn

    tr = [t for t in b.GetTracks() if t.GetClass() == 'PCB_TRACK']
    vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
    bot = [t for t in tr if t.GetLayer() == pcbnew.B_Cu]
    out['tracks'] = len(tr)
    out['vias'] = len(vias)
    out['back_pct'] = round(100 * len(bot) / max(1, len(tr)))

    zones = list(b.Zones())
    out['plane_mm2'] = round(sum(z.GetFilledArea() for z in zones) / 1e12)
    # one entry per copper layer that carries ground; a healthy plane is a single
    # polygon on each, because an island is a return path that has to detour
    out['planes'] = [(b.GetLayerName(z.GetLayer()),
                      round(z.GetFilledArea() / 1e12),
                      z.GetFilledPolysList(z.GetLayer()).OutlineCount())
                     for z in zones]
    out['plane_polys'] = max([p[2] for p in out['planes']] or [0])

    bb = b.GetBoardEdgesBoundingBox()
    out['size'] = (round(mm(bb.GetWidth()), 1), round(mm(bb.GetHeight()), 1))
    out['fits_100'] = out['size'][0] <= 100 and out['size'][1] <= 100

    # nothing on the back may cut the plane under an IC
    cut = 0
    for ref in ic_refs:
        fps = [f for f in b.GetFootprints() if f.GetReference() == ref]
        if not fps:
            continue
        box = fps[0].GetBoundingBox(False, False)
        cut += sum(1 for t in bot
                   if mm(box.GetLeft()) <= mm(t.GetStart().x) <= mm(box.GetRight())
                   and mm(box.GetTop()) <= mm(t.GetStart().y) <= mm(box.GetBottom()))
    out['plane_cuts_under_ics'] = cut

    out['silk'] = mkpcb.silk_check(pcb)

    # footprint <-> schematic linkage
    out['unlinked'] = sorted(f.GetReference() for f in b.GetFootprints()
                             if not f.GetPath().AsString() and not f.GetReference().startswith('H'))

    # every pad on a net
    nc = set(no_connect)
    out['pads_no_net'] = sorted(f.GetReference() + '.' + p.GetNumber()
                                for f in b.GetFootprints() for p in f.Pads()
                                if not p.GetNetname() and not f.GetReference().startswith('H')
                                and f.GetReference() + '.' + p.GetNumber() not in nc)

    # track widths vs the project's netclasses
    pro = os.path.splitext(pcb)[0] + '.kicad_pro'
    if os.path.exists(pro):
        d = json.load(open(pro, encoding='utf-8'))
        cls = {c['name']: c['track_width'] for c in d['net_settings']['classes']}
        out['netclasses'] = cls
        pw = set(round(mm(t.GetWidth()), 2) for t in tr
                 if t.GetNetname() in ('+12V', '-12V', '+5V'))
        out['power_widths'] = sorted(pw)
        out['power_matches_class'] = (not pw) or pw == {cls.get('Power')}
    return out


def hiz_extents(pcb, nets):
    b = pcbnew.LoadBoard(pcb)
    pads = collections.defaultdict(list)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            pads[p.GetNetname()].append((mm(p.GetPosition().x), mm(p.GetPosition().y)))
    out = {}
    for n in nets:
        ps = pads.get(n)
        if not ps or len(ps) < 2:
            continue
        out[n] = round(max(math.hypot(a[0] - c[0], a[1] - c[1]) for a in ps for c in ps), 1)
    return out


def report(name, a):
    ok = (not a['drc'] and a['unconnected'] == 0 and not a['silk']
          and a['plane_polys'] == 1 and a['plane_cuts_under_ics'] == 0
          and not a['unlinked'] and not a['pads_no_net']
          and a['fits_100'] and a.get('power_matches_class', True))
    print("%-8s %s" % (name, 'PASS' if ok else 'ISSUES'))
    print("   size %.1f x %.1f mm (<=100: %s)" % (a['size'][0], a['size'][1], a['fits_100']))
    print("   DRC %s   unconnected %d" % (a['drc'] or 'clean', a['unconnected']))
    print("   tracks %d (%d%% on back), vias %d" % (a['tracks'], a['back_pct'], a['vias']))
    print("   ground %s; cuts under ICs: %d"
          % (', '.join('%s %d mm2 in %d poly' % p for p in a.get('planes', ()))
             or '%d mm2' % a['plane_mm2'], a['plane_cuts_under_ics']))
    print("   silkscreen collisions %s" % (a['silk'] or 0))
    print("   unlinked footprints %s; pads with no net %s"
          % (a['unlinked'] or 0, a['pads_no_net'] or 0))
    if 'power_widths' in a:
        print("   power tracks %s vs netclass Power %s -> %s"
              % (a['power_widths'], a['netclasses'].get('Power'),
                 'match' if a['power_matches_class'] else 'MISMATCH'))
    return ok
