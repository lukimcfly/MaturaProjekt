"""Rewrite the PCB section of HANDOFF.md from the boards themselves.

Numbers typed by hand go stale the moment a board is rebuilt, so the table is
generated from the actual `.kicad_pcb` files and the DRC run.
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checkpcb
import buildall

TITLES = {'osc': ('Oszillator', '`boards/osc/`, 3x', 57),
          'filter': ('Filter', '`boards/filter/`, 4x', 22),
          'main': ('Hauptplatine', '`boards/main/`', 46)}


def row(name):
    a = checkpcb.audit('boards/%s/%s.kicad_pcb' % (name, name),
                       ic_refs=buildall.BOARDS[name]['ics'],
                       no_connect=buildall.BOARDS[name].get('nc', ()))
    title, where, parts = TITLES[name]
    planes = a.get('planes', [])
    back = [p for p in planes if p[0] == 'B.Cu']
    plane = ('%d mm2, %s' % (back[0][1], 'one piece' if back[0][2] == 1
                             else '%d pieces' % back[0][2])) if back else '-'
    ok = (not a['drc'] and a['unconnected'] == 0 and not a['silk']
          and a['plane_polys'] == 1 and not a['unlinked'] and not a['pads_no_net']
          and a['fits_100'])
    return ('| %s (%s) | %.1f x %.1f mm | %d | %d | %d %% | %d | %s |'
            % (title, where, a['size'][0], a['size'][1], parts,
               a['tracks'], a['back_pct'], a['vias'], plane)), ok, a


if __name__ == '__main__':
    rows, allok = [], True
    for n in ('osc', 'filter', 'main'):
        r, ok, a = row(n)
        rows.append(r)
        allok = allok and ok
        print('%-7s %s  drc=%s unconnected=%d silk=%d planes=%s'
              % (n, 'PASS' if ok else 'ISSUES', a['drc'] or 'clean',
                 a['unconnected'], len(a['silk']), a.get('planes')))
    print()
    print('\n'.join(rows))
