"""Re-assign which net sits on which pin of a board-boundary connector.

Which pin of a panel plug carries which signal is a free variable: the loom is
hand-wired one wire per lug, so the only thing that changes is a column in the
wiring table.  On the board it matters a great deal - the oscillator's two panel
connectors had 61 crossing pin-pairs between them, and every crossing costs the
router a via or a detour at the most congested edge of the board.

Only the label text at each connector pin changes.  Net membership, connectivity
and ERC are untouched: the same nets reach the same connector, through different
pins.  `addconn.py` puts each pin's label at exactly (pin_x - 7.62, pin_y), which
is how they are found here.
"""
import sys, os, io, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom

STUB = 7.62
LABEL = re.compile(r'^(\s*\(label\s+")([^"]*)(".*)$')
AT = re.compile(r'^\s*\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s')


def pin_labels(path, conn):
    """{pin number: (anchor point, current label text)} for one connector."""
    g = geom.Geom(path)
    pins = {}
    for pt, lst in g.pins.items():
        for ref, pin in lst:
            if ref == conn:
                pins[int(pin)] = pt
    if not pins:
        raise KeyError('connector %s not found' % conn)
    out = {}
    for k, (px, py) in pins.items():
        anchor = (round(px - STUB, 2), round(py, 2))
        names = g.labels.get((px - STUB, py)) or g.labels.get(anchor)
        out[k] = (anchor, sorted(names)[0] if names else None)
    return out


def reorder(path, conn, new_order, out_path=None, dry_run=False):
    """Rewrite the connector's pin labels to `new_order` (pin 1 first).

    Edited line by line rather than by re-serialising the schematic: a 27,000-line
    round trip through the s-expression writer reformats the whole file and risks
    the escaping traps documented in HANDOFF, for a change that touches fourteen
    strings.
    """
    current = pin_labels(path, conn)
    if len(new_order) != len(current):
        raise ValueError('%s has %d pins, got %d names'
                         % (conn, len(current), len(new_order)))
    if sorted(v[1] for v in current.values()) != sorted(new_order):
        raise ValueError('%s: new order is not a permutation of the old one'
                         % conn)
    want = {current[k][0]: new_order[k - 1] for k in sorted(current)}

    text = io.open(path, encoding='utf-8', newline='').read()
    lines = text.split('\n')
    hits = 0
    for i, line in enumerate(lines):
        m = LABEL.match(line)
        if not m:
            continue
        for j in (i + 1, i + 2):
            if j >= len(lines):
                break
            a = AT.match(lines[j])
            if not a:
                continue
            key = (round(float(a.group(1)), 2), round(float(a.group(2)), 2))
            if key in want:
                lines[i] = m.group(1) + want[key] + m.group(3)
                hits += 1
            break
    if hits != len(current):
        raise RuntimeError('%s: rewrote %d labels, expected %d'
                           % (conn, hits, len(current)))
    if not dry_run:
        io.open(out_path or path, 'w', encoding='utf-8',
                newline='').write('\n'.join(lines))
    return hits
