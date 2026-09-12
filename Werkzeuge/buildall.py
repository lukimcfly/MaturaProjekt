"""Rebuild, route and audit every board from its placement spec."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autoplace, mkpcb, routeboard, checkpcb
import place_filter, place_osc, place_main

BOARDS = {
    'filter': dict(
        mod=place_filter, net='work/net_filter.net',
        anchors=('U401', 'J410', 'J411', 'J412', 'J413', 'J414',
                 'C403', 'C404', 'C405', 'C406'),
        smd=('U401',), keepout=('U401',), keepout_pins=('J412',),
        solid=('J410', 'J411', 'J412', 'C403', 'C404', 'C405', 'C406'),
        ics=('U401',), nc=()),
    'osc': dict(
        mod=place_osc, net='work/net_osc.net',
        anchors=('U101', 'U102', 'U103', 'U104', 'J110', 'J111', 'J112', 'J113',
                 'J114', 'J115', 'C105', 'C106', 'C107', 'C108', 'C109', 'C110',
                 'C111', 'C112', 'C113'),
        smd=('U102', 'U103', 'U104'),
        keepout=('U101', 'U102', 'U103', 'U104'),
        keepout_pins=('J112', 'J113', 'J114'),
        solid=('J110', 'J111', 'J112', 'J113', 'J114', 'J115', 'C105', 'C106',
               'C107', 'C108', 'C109', 'C110', 'C111', 'C112', 'C113'),
        ics=('U101', 'U102', 'U103', 'U104'),
        # place_osc derives every position from the pin each part serves and is
        # already clean against the real courtyards, so the collision resolver
        # has nothing to add - letting it nudge only scrambled that work
        all_anchored=True,
        # This is much the densest board - 57 parts where the main board has 46 in
        # the same area - and it simply needs the back layer.  Charging extra per step
        # there, which the other two boards pass easily with, bought nothing here: the
        # plane came out in one piece either way and it cost nets.  The connector
        # pad-row keepouts are what actually stop the plane fragmenting.
        back_cost=1.0,
        # 0.20 mm clearance on this board only - its own DRC minimum, and about ten
        # percent more room between tracks.  The other two do not need it.
        clearance=0.20,
        # second Schmitt gate output is unused by design
        nc=('U102.4',)),
    'main': dict(
        mod=place_main, net='work/net_main.net',
        anchors=('U901', 'U990', 'Q801', 'J810', 'J811', 'J812', 'J813', 'J814',
                 'J815', 'J816', 'J817', 'J904', 'J990', 'F901', 'F902',
                 'C921', 'C922', 'C931', 'C932', 'C941', 'C942', 'C906', 'C907'),
        smd=(), keepout=('U901', 'U990'), keepout_pins=('J812',),
        solid=('J990', 'J810', 'J811', 'J812', 'C921', 'C922', 'C931', 'C932',
               'C941', 'C942', 'C906', 'C907'),
        ics=('U901', 'U990'),
        all_anchored=True,
        # the LM386's gain pins are deliberately left open
        nc=('U901.1', 'U901.8')),
}


def build_one(name, spec, route=True):
    mod = spec['mod']
    pcb = os.path.abspath('boards/%s/%s.kicad_pcb' % (name, name))
    sch = 'boards/%s/%s.kicad_sch' % (name, name)
    p = autoplace.Placer(spec['net'], mod.outline(), {}, margin=2.0)
    want = mod.placement()
    anchors = tuple(want) if spec.get('all_anchored') else spec['anchors']
    place, moved = p.resolve(want, anchors=anchors)
    mkpcb.build(spec['net'], place, mod.outline(), mod.holes(), pcb,
                labels=mod.labels(), sch_path=sch)
    json.dump({k: list(v) for k, v in place.items()},
              open('work/%s_place.json' % name, 'w'))
    out = dict(nudged=len(moved),
               max_nudge=round(max([d for _, d in moved], default=0), 1),
               silk=mkpcb.silk_check(pcb))
    if route:
        t = time.time()
        r = routeboard.run(pcb, sch, mod.outline(), smd_refs=spec['smd'],
                           keepout_ics=spec['keepout'], solid_refs=spec['solid'],
                           keepout_pins=spec.get('keepout_pins', ()),
                           back_cost=spec.get('back_cost'),
                           clearance=spec.get('clearance', 0.25))
        out.update(r, seconds=round(time.time() - t))
    return out


if __name__ == '__main__':
    which = sys.argv[1:] or list(BOARDS)
    for name in which:
        r = build_one(name, BOARDS[name])
        print('%-7s nudged %-3d silk %-3s | tracks %-4d back %-4d vias %-3d failed %-2d (%ds)'
              % (name, r['nudged'], len(r['silk']), r['tracks'], r['back'],
                 r['vias'], len(r['failed']), r['seconds']))
        if r['failed']:
            print('        failed:', r['failed'])
        if r['silk']:
            print('        silk:', r['silk'][:4])
        a = checkpcb.audit('boards/%s/%s.kicad_pcb' % (name, name),
                           ic_refs=BOARDS[name]['ics'],
                           no_connect=BOARDS[name].get('nc', ()))
        checkpcb.report(name, a)
        print()
