"""Widen every silkscreen line thinner than JLCPCB's 0.15 mm minimum.

KiCad's standard footprints draw their outlines at 0.12 mm; JLCPCB lists 0.15 mm as
the thinnest line it prints reliably. Only line widths change - nothing moves, no
copper is touched, so routing and DRC results on copper stay exactly as they were.
"""
import sys
import pcbnew

MIN_W = pcbnew.FromMM(0.15)
SILK = {pcbnew.F_SilkS, pcbnew.B_SilkS}


def widen(path):
    b = pcbnew.LoadBoard(path)
    n = 0
    items = list(b.GetDrawings())
    for fp in b.GetFootprints():
        items += list(fp.GraphicalItems())
    for g in items:
        if g.GetLayer() not in SILK or g.GetClass() in ('PCB_TEXT', 'FP_TEXT', 'PCB_TEXTBOX'):
            continue
        if not hasattr(g, 'GetWidth'):
            continue
        w = g.GetWidth()
        if 0 < w < MIN_W:
            g.SetWidth(MIN_W)
            n += 1
    pcbnew.SaveBoard(path, b)
    return n


if __name__ == '__main__':
    for name in sys.argv[1:]:
        print('%-7s %d silkscreen lines widened to 0.15 mm'
              % (name, widen('boards/%s/%s.kicad_pcb' % (name, name))))
