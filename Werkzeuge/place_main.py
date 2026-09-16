"""Placement for the main board (96 x 94 mm) - mixer, LM386 and power entry.

This board has a genuinely linear signal flow, so it is laid out as three bands:

  top     power entry: inlet -> fuses -> reverse-polarity diodes -> bulk -> rails out
  middle  mixer: three oscillator inputs on the left, through the BC547 stage,
          out to filter A on the right
  bottom  output: filter B back in, LM386, speaker terminal

Mains-side separation matters here: the LM386 draws the only large current on the
board, so its parts are kept at the bottom, away from the mixer's input coupling
capacitors at the top left.
"""

OX, OY = 100.0, 60.0
W, H = 96.0, 98.0

LOCAL = {
    # ---------- power entry, top band ----------------------------------
    'J990': (15, 8, 0),        # Netzteil +/-12 V in
    'F901': (34, 8, 0),        # T500mA, +12 V rail
    'F902': (34, 19, 0),       # T500mA, -12 V rail
    'D907': (57, 8, 0),        # 1N5819 reverse-polarity guard, +12 V
    'D908': (57, 19, 0),       # 1N5819 reverse-polarity guard, -12 V
    'C931': (72, 8, 0),        # 100u bulk, +12 V
    'C932': (72, 19, 180),     # 100u bulk, -12 V
    'C921': (83, 8, 0),        # 100n, +12 V
    'C922': (83, 19, 180),     # 100n, -12 V
    'U990': (57, 30, 0),       # 78L05
    'C941': (47, 30, 180),     # 330n at the regulator input
    'C942': (68, 30, 0),       # 100n at the regulator output
    'J810': (14, 30, 0),       # rails out -> oscillator chain (4-way)
    'J811': (32, 30, 0),       # rails out -> filter chain (3-way)

    # ---------- mixer, middle band --------------------------------------
    # three rows on a 12 mm column pitch and a 10 mm row pitch: an axial resistor
    # plus clearance is 11.2 mm wide, a side-entry connector 9.6 mm tall
    'J813': (6, 42, 90),
    'C801': (17, 42, 0),
    'R801': (29, 42, 0),
    'R804': (41, 42, 0),
    'R806': (53, 42, 0),
    'C806': (66, 42, 0),
    'R809': (77, 42, 0),
    'J816': (88, 46, 90),

    'J814': (6, 54, 90),
    'C802': (17, 52, 0),
    'R802': (29, 52, 0),
    'C804': (41, 52, 0),
    'Q801': (53, 52, 0),

    'J815': (6, 66, 90),
    'C803': (17, 62, 0),
    'R803': (29, 62, 0),
    'R805': (41, 62, 0),
    'R807': (53, 62, 0),
    'R808': (65, 62, 0),
    'C805': (77, 62, 0),

    # ---------- output stage, bottom band --------------------------------
    # Laid out around the LM386's pins rather than along a row.  The first version
    # of this band put the 100 n supply cap 41 mm from pin 6 and the Zobel network
    # 32 and 46 mm from pin 5; an LM386 with its decoupling and its damping network
    # that far away is a reliable way to build an oscillator instead of an amplifier.
    # The whole stage then sits to the RIGHT, because the panel harness below it has
    # to fan eight mixer nets up the left-hand side and the amplifier was standing in
    # the middle of that path.
    'J817': (6, 78, 90),       # filter B back in
    'C901': (14, 78, 0),       # input coupling
    'R902': (24, 78, 0),       # on to the volume pot
    'U901': (40, 82, 0),       # LM386
    'C903': (51, 76, 180),     # bypass, pin 7
    'C907': (51, 83.3, 0),     # 100 n supply decoupling, hard against pin 6
    'R901': (51, 89.5, 0),     # Zobel resistor, pin 5
    'C905': (63, 89.5, 0),     # Zobel capacitor, on to ground
    'C906': (63, 79, 0),       # 100 u bulk for the output stage
    'C904': (76, 82, 0),       # 470 u output coupling
    'J904': (89, 82, 90),      # speaker

    # ---------- panel harness -------------------------------------------
    # Sits under the mixer column it feeds, so its eight level/pan nets run almost
    # straight up instead of crossing the board diagonally: pin 11 is within 0.1 mm
    # of the LM386 input pin it drives.
    'J812': (25, 93, 0),
}

HOLES_LOCAL = [(4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4)]

LABELS_LOCAL = [
    ('Hauptplatine 4.0', 80, 94, 1.3),
    ('NETZ +/-12V', 15, 13.5, 0.9),
    ('-> OSZ', 14, 35, 0.9),
    ('-> FILTER', 32, 35, 0.9),
    ('LS 8R', 88, 71, 0.9),
]


def placement():
    return {r: (x + OX, y + OY, rot) for r, (x, y, rot) in LOCAL.items()}


def outline():
    return (OX, OY, OX + W, OY + H)


def holes():
    return [(x + OX, y + OY) for x, y in HOLES_LOCAL]


def labels():
    return [(t, x + OX, y + OY, s) for t, x, y, s in LABELS_LOCAL]
