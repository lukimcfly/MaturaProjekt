"""Placement for the filter board (80 x 62 mm).

Coordinates are the CENTRE of each part (mkpcb solves for the footprint origin).
The OPA4196's four sections sit on the four corners of the package - A on pins 1-3,
B on 5-7, C on 8-10, D on 12-14 - so each section's parts go in the matching quadrant
and no feedback loop crosses another.  Rows are 6 mm apart so the silkscreen
reference of one part does not land on the body of the next.
"""

OX, OY = 100.0, 60.0          # where the board sits on the sheet
W, H = 80.0, 68.0   # taller: OPA4196 in SOIC-14 is 9.4 mm, not 5.7

LOCAL = {
    # ---- supply across the top edge -------------------------------------
    'J410': (14, 8, 0),       # Versorgung ein     (+12 / GND / -12)
    'C405': (30, 8, 0),       # 10u bulk, +12 V
    'C406': (50, 8, 180),     # 10u bulk, -12 V
    'J411': (66, 8, 0),       # Versorgung weiter  (daisy-chain out)

    # ---- quad op-amp; decoupling 3 mm from pins 4 and 11 -----------------
    'U401': (40, 36, 0),
    'C403': (32, 36, 180),    # 100n, pad 1 (+12 V) faces pin 4
    'C404': (48, 36, 180),    # 100n, pad 2 (-12 V) faces pin 11

    # Each part is rotated so the pad that joins the op-amp faces it, and each
    # summing node's parts sit beside their own pin instead of in one long column.
    # ---- left inner column: A's summing node (pin 2), then B (pin 6) -----
    'R406': (27, 20, 0),      # HP feedback    -> pin 2
    'R405': (27, 25, 0),      # LP feedback    -> pin 2
    'R404': (27, 30, 0),      # signal in      -> pin 2
    'R401': (27, 42, 0),      # integrator 1   -> pin 6
    'C401': (27, 47, 180),    # integrator 1 cap

    # ---- left outer column: the Q network (pin 3) ------------------------
    'R403': (16, 36, 0),      # from the resonance pot
    'R407': (16, 41, 0),      # low side to GND

    # ---- right inner column: D's summing node (pin 13), then C (pin 9) ---
    'R408': (53, 20, 180),    # HP in          -> pin 13
    'R409': (53, 25, 180),    # LP in          -> pin 13
    'R410': (53, 30, 0),      # notch feedback -> pin 13
    'R402': (53, 42, 180),    # integrator 2   -> pin 9
    'C402': (53, 47, 0),      # integrator 2 cap

    # ---- audio on the side edges, panel harness along the bottom ---------
    'J413': (6, 30, 90),      # Audio ein
    'J414': (74, 30, 90),     # Audio aus
    'J412': (40, 62, 0),      # Panel: Cutoff-Doppelpoti, Resonanz, Wahlschalter
}

HOLES_LOCAL = [(4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4)]

# extra silkscreen so the board is self-explanatory on the bench
LABELS_LOCAL = [
    ('Filter-Platine 4.0  -  4x bestuecken', 40, 56, 1.3),
    ('+12  GND  -12', 14, 13.3, 1.0),
    ('+12  GND  -12', 66, 13.3, 1.0),
    ('IN', 5, 22, 1.2),
    ('OUT', 75, 22, 1.2),
    ('PANEL', 40, 67.0, 1.0),
]


def placement():
    return {r: (x + OX, y + OY, rot) for r, (x, y, rot) in LOCAL.items()}


def outline():
    return (OX, OY, OX + W, OY + H)


def holes():
    return [(x + OX, y + OY) for x, y in HOLES_LOCAL]


def labels():
    return [(t, x + OX, y + OY, s) for t, x, y, s in LABELS_LOCAL]
