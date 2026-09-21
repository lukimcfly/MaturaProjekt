"""Change component values in a .kicad_sch and the matching .kicad_pcb, nothing else.

A line-level edit of exactly one (property "Value" ...) per symbol - no s-expression
round trip, because re-serialising a schematic reformats it wholesale (see HANDOFF).
Each change is checked: the symbol must exist once, and its old value must match.

Oscillator frequency fix of 2026-09-21: the 74LVC2G17's real thresholds (TI data
sheet, VCC = 5 V: VT+ 2.05..3.4 V, VT- 1.25..2.25 V) put the saw an octave below the
function generator and its level at 7-15 Vpp. New values move both sections to
~48 Hz - 4.9 kHz, in step, and the saw to ~6 Vpp like the other waveforms.
"""
import sys, re

CHANGES_OSC = {           # per oscillator unit n = 1, 2, 3: ref suffix -> (old, new)
    'C%d01': ('47nF', '56nF'),
    'C%d02': ('6.8nF', '15nF'),
    'R%d24': ('110k', '56k'),
}


def edit_sch(path, changes, dry=False):
    s = open(path, encoding='utf-8', newline='').read()
    done = []
    for ref, (old, new) in changes.items():
        tag = '(property "Reference" "%s"' % ref
        hits = [m.start() for m in re.finditer(re.escape(tag), s)]
        if len(hits) != 1:
            raise SystemExit('%s: expected 1 symbol %s, found %d' % (path, ref, len(hits)))
        i = hits[0]
        nxt = s.find('(property "Reference"', i + len(tag))
        j = s.find('(property "Value" "', i)
        if j < 0 or (nxt >= 0 and j > nxt):
            raise SystemExit('%s: no Value property for %s' % (path, ref))
        k = s.index('"', j + len('(property "Value" "'))
        cur = s[j + len('(property "Value" "'):k]
        if cur != old:
            raise SystemExit('%s: %s is %r, expected %r' % (path, ref, cur, old))
        s = s[:j] + '(property "Value" "%s"' % new + s[k + 1:]
        done.append((ref, old, new))
    if not dry:
        open(path, 'w', encoding='utf-8', newline='').write(s)
    return done


def edit_pcb(path, changes):
    import pcbnew
    b = pcbnew.LoadBoard(path)
    done = []
    for fp in b.GetFootprints():
        r = fp.GetReference()
        if r in changes:
            old, new = changes[r]
            if fp.GetValue() != old:
                raise SystemExit('%s: %s is %r, expected %r' % (path, r, fp.GetValue(), old))
            fp.SetValue(new)
            done.append((r, old, new))
    if len(done) != len(changes):
        raise SystemExit('%s: only found %s' % (path, done))
    pcbnew.SaveBoard(path, b)
    return done


def expand(units):
    out = {}
    for pat, v in CHANGES_OSC.items():
        for n in units:
            out[pat % n] = v
    return out


if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'master':
        print(edit_sch('SynthesizerFinal.kicad_sch', expand((1, 2, 3))))
    elif what == 'osc-sch':
        print(edit_sch('boards/osc/osc.kicad_sch', expand((1,))))
    elif what == 'osc-pcb':
        print(edit_pcb('boards/osc/osc.kicad_pcb', expand((1,))))
