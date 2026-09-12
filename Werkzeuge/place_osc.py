"""Placement for the oscillator board (96 x 96 mm).

The rule is that a part sits beside the pin it serves.  Earlier versions of this
file said so in a docstring but wrote the coordinates by hand, and the two drifted
apart badly: R125 ended up 21 mm from the single pin it connects to, and the
oscillator's timing node was smeared over 29 mm of board.  So the y of every
column part is now derived from the actual pad coordinates of the IC it belongs
to, and the part is rotated so the pad that joins the IC is the one facing it.

Only the architecture is written down here - which IC each part belongs to, which
side of it, and how far out - because that is the part that carries engineering
judgement.  Everything else is computed.

Three of the four ICs are small SMD packages whose fourteen pins span 7.6 mm, so a
column of seven parts can never hug them; `spread` therefore places each part as
close to its own pin as least squares allows while holding the column in pin order.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinplace

OX, OY = 100.0, 60.0
W, H = 99.4, 99.4     # the brief is "under 100 x 100"; this is the densest
                      # board by a quarter and it needs every millimetre
NET = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work', 'net_osc.net')

PITCH = 4.6          # column pitch: tallest passive is 3.0 mm plus clearance

# ---- the architecture --------------------------------------------------
ICS = {
    #        x   y  rot  footprint
    'U101': (68, 42, 0, 'Package_DIP:DIP-14_W7.62mm_Socket'),
    'U103': (23, 46, 0, 'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm'),
    'U104': (68, 72, 0, 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'),
}

# (ic, column x, side, refs); side -1 = left of the IC, +1 = right
COLUMNS = [
    # U103 A/B: the distortion, on the pins facing the panel connectors
    ('U103', 16.0, -1, ['R116', 'R114', 'R115']),
    ('U103',  8.0, -1, ['D105', 'D106', 'D103', 'D104']),
    # U103 C/D: the sawtooth core and its output amplifier
    ('U103', 31.5, +1, ['R124', 'R123', 'R125', 'C101', 'C104']),
    # U101 A/B: the function generator
    ('U101', 50.0, -1, ['R126', 'R106', 'R104', 'R105', 'R107', 'C102']),
    # U101 C/D: the sine shaper.  Two columns, because eight parts cannot sit
    # against a package whose pins span 15 mm without one of them ending up 12 mm
    # from the pin it serves.
    ('U101', 84.0, +1, ['R112', 'R113', 'R110', 'R111']),
    ('U101', 91.0, +1, ['R109', 'R108']),
    # U104: the output buffer
    ('U104', 52.0, -1, ['R120', 'R119', 'R118']),
    ('U104', 83.0, +1, ['R121']),
]

# parts with no pin of their own to sit beside: an explicit spot, and why
FIXED = {
    'J110': (17, 7, 0),       # supply in
    'C112': (29, 7, 0),       # bulk +12
    'C113': (45, 7, 180),     # bulk -12
    'J111': (63, 7, 0),       # supply on to the next board
    'C108': (23, 36, 90),     # +12 V on U103 pin 4, straight above the package
    'C109': (23, 57, 90),     # -12 V on U103 pin 11, straight below it
    'C105': (58, 42, 180),    # +12 V on U101 pin 4
    'C106': (77.5, 42, 180),    # -12 V on U101 pin 11, that pad facing the IC
    'C111': (59.5, 72, 180),    # -12 V on U104 pin 4
    'C110': (76.5, 72, 180),    # +12 V on U104 pin 8
    # The timing node is the one net on this board where stray capacitance and
    # leakage move the pitch, so its five pads are kept in one tight cluster
    # against U103 pin 10 rather than strung out along a column.
    'U102': (36, 46, 0),      # Schmitt trigger, senses C101
    'C107': (36.5, 39, 90),     # +5 V on U102, right at the package
    'R103': (41, 45, 0),      # discharge path from the transistor
    'R101': (41, 50, 180),    # charges C101 from the pitch pot
    'R102': (42, 56, 180),    # Schmitt output to the transistor base
    'Q101': (33, 62, 0),      # discharge transistor, between R102 and R103
    # the sine-shaper diodes go below U101, where a 9.8 mm body still fits
    # inside the board margin that the outer column does not leave
    'D101': (81, 54, 0),
    'D102': (81, 59, 0),
    'R127': (50, 24, 0),      # divider leg on the square-wave output
    'R117': (50, 82, 0),      # load on the signal going into U104
    'R122': (83, 80, 180),    # output level divider leg
    'C103': (13, 64, 90),     # couples the wave-select switch to the wave bus
    # All three jack signals land in the right-hand half, so the connector
    # belongs on the right edge; on the left it dragged /OSC1_OUT across 98 mm
    # of board for nothing.
    'J114': (93, 64, 90),     # panel jacks
    'J115': (93, 80, 90),     # audio out to the mixer
    'J112': (24, 92.4, 0),      # panel pots, nearest the distortion it feeds
    'J113': (59, 92.4, 0),      # panel switches
}

HOLES_LOCAL = [(4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4)]

LABELS_LOCAL = [
    ('Oszillator-Platine 4.0  -  3x bestuecken', 48, 18, 1.3),
    ('+12 GND -12 +5', 13, 12.5, 0.9),
    ('+12 GND -12 +5', 61, 12.5, 0.9),
    ('BUCHSEN', 81, 66, 0.9),
    ('OUT', 86, 87, 1.0),
    ('POTIS', 24, 97.4, 0.9),
    ('SCHALTER', 59, 97.4, 0.9),
]

_cache = {}


def _build():
    if _cache:
        return _cache['p']
    import netlib
    nets = pinplace.load_nets(os.path.normpath(NET))
    pn = pinplace.part_nets(nets)
    comps = netlib.load(os.path.normpath(NET))[0]

    place = dict(FIXED)
    for ref, (x, y, rot, fp) in ICS.items():
        place[ref] = (x, y, rot)

    for ic, cx, side, refs in COLUMNS:
        icx, icy, icrot, icfp = ICS[ic]
        pins = pinplace.pin_xy(icfp, icrot, icx, icy)
        direct, rots = {}, {}
        for r in refs:
            wy, own = pinplace.serves(nets, pn, r, ic, pins)
            direct[r] = wy
            rots[r] = pinplace.facing(own, side, comps[r]['fp']) if own else 0
        want = []
        for r in refs:
            wy = direct[r]
            if wy is None:
                # No pin of its own.  Sit with whichever column-mate it shares a
                # net with - electrically it is in parallel with that part anyway.
                mates = set()
                for name, _ in pn.get(r, ()):
                    if name in pinplace.PWR:
                        continue
                    mates.update(r2 for r2, _ in nets[name])
                peers = [direct[o] for o in refs if o in mates and direct[o] is not None]
                wy = sum(peers) / len(peers) if peers else icy
            want.append((r, wy))
        for r, y in pinplace.spread(want, PITCH, lo=16.0, hi=86.0).items():
            place[r] = (cx, y, rots[r])
    _cache['p'] = place
    return place


def placement():
    return {r: (x + OX, y + OY, rot) for r, (x, y, rot) in _build().items()}


def outline():
    return (OX, OY, OX + W, OY + H)


def holes():
    return [(x + OX, y + OY) for x, y in HOLES_LOCAL]


def labels():
    return [(t, x + OX, y + OY, s) for t, x, y, s in LABELS_LOCAL]
