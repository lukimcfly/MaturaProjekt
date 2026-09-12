# Synthesizer project — handoff (state as of 2026-09-11, rev 4.0)

Read this first when resuming. The schematic work is **finished**; the next step is
PCB layout of three boards.

---

## 1. Current state in one paragraph

`SynthesizerFinal.kicad_sch` is the complete system schematic (KiCad 10 native format,
rev 4.0, 365 symbols). It is **ERC-clean: 0 errors, 0 warnings.** All 305 board parts
carry a verified footprint; the 60 panel-mounted parts are marked *exclude from board*
but stay in the BOM. The design is split into **three board projects** under `boards/`,
each ERC-clean and each proven to carry exactly the master's sub-netlist for its module.

```
OSC 1/2/3  ->  Mixer  ->  Filter A  ->  Filter B  ->  LM386  ->  speaker
                    (Filters C and D are patched in by jack cable)
```

---

## 2. Files

| Path | What |
|---|---|
| `SynthesizerFinal.kicad_sch` / `.kicad_pro` | master system schematic + project |
| `boards/osc/` | oscillator board — **build 3x** — 57 parts |
| `boards/filter/` | filter board — **build 4x** — 22 parts |
| `boards/main/` | mixer + LM386 + power — **build 1x** — 46 parts |
| `docs/VERDRAHTUNG.md` | wiring guide: cable list + every panel wire, generated from the netlist |
| `docs/BOM_osc.csv`, `BOM_filter.csv`, `BOM_main.csv` | per-board BOMs incl. footprints |
| `tools/` | the scripts that produced all of this (see §6) |
| `sim/` | SPICE models + netlists; `work/sim/` holds this session's runs |

The three oscillators are electrically identical, as are the four filters — that is why
there are only three layouts. On a single board the references are always those of the
first group (R101, U103, J112 …); the master keeps 1xx/2xx/3xx and 4xx–7xx apart.

---

## 3. Defects found and fixed this session

All four were found by systematic checks, not by reading — and all are verified against
the exported netlist.

1. **Filters C and D did not work at all.** The output jack's ground symbol had been
   placed exactly on integrator 2's summing node, shorting the op-amp's virtual ground
   to real ground (`#PWR6060`/`J602.S` on `U601.9`). Filters A and B were fine.
   Found by a general rule — *an op-amp with both inputs on the same net cannot work* —
   then swept across all 46 op-amp units; only these two were faulty. Fixed by moving
   the jack ground; all four filter modules are now topologically identical.
2. **C804 was reverse-biased** by ~1.8 V (its + terminal on the 0 V node, − on the
   transistor base at +1.83 V). Rotated 180°.
3. **No local decoupling anywhere.** 17 ICs had only bulk supply caps. Added
   **29 × 100 nF** (one per supply pin) and **14 × 10 µF** per-board bulk, since each
   board now feeds its rails over a cable.
4. **Mixer gain staging.** The oscillator output buffer U104A has a gain of 2, so
   OSC_OUT maxes at 14 Vpp, but the mixer's BC547 stage stayed linear only to ~8 Vpp —
   the top half of six pots did nothing but clip. Fixed with `R801/802/803 47k → 100k`
   and `R806 330 → 470` (which also recentres the collector at 6.77 V so any deliberate
   overdrive clips symmetrically). Chain is now clean over the whole range, 87 mW max.

## 4. Deliberate changes

- **Distortion stage restructured** (the open item from last session). Was ~15 dB
  quieter than the clean path. Now: `U103A` = drive + soft clipper, a passive hard
  clipper hangs off its output, and `U103B` became the **make-up amplifier** instead of
  the hard-clipper driver. `SW102` now switches the soft-clip diodes in and out of
  `U103A`'s feedback rather than selecting an output. One value change (`R115 100k →
  330k`), three rewires, **no new parts**.

  | | clean | soft | hard |
  |---|---|---|---|
  | before | 7.0 Vpp | 1.07 Vpp (−16 dB) | 1.27 Vpp (−15 dB) |
  | after | 7.0 Vpp | 5.7 Vpp (−1.8 dB) | 8.7 Vpp (+1.9 dB) |

  Side effect: `RV103` is now **Drive** and `RV104` is **Distortion level** (100k log).
- **46 JST-XH connectors added** at every board boundary — 240 pins, each verified to
  land on the right net. Panel hardware is wired, one wire per lug (153 wires total).
- **All 27 `lib_symbol_mismatch` warnings eliminated** by replacing the embedded symbol
  definitions with the official library ones (flattening `extends` where needed). The
  `Conn_01x02` swap moved pins by 1.27 mm, so `J904` was shifted to compensate —
  its netlist is unchanged. **This is why you should not blind-click "Update Symbols
  from Library"** on an old file: it would have silently disconnected J904.
- Pot tapers normalised (`RV104` → log, `RV801-803` → log), `C901` → bipolar (it sits at
  0 V DC), 18 diodes retargeted from `1N4148WT` (SMD) to `1N4148` (THT), title block
  bumped to rev 4.0, file format upgraded to KiCad 10.

## 5. Verification performed

| Check | Result |
|---|---|
| ERC, master + 3 boards | 0 errors, 0 warnings each |
| Symbol pin → footprint pad mapping | 25 distinct pairings, **0 mismatches** |
| Every footprint exists on disk | 305/305 |
| Board netlists vs master sub-netlists | identical for all three |
| Connector pins on the intended net | 240/240 |
| Panel wiring destinations vs netlist | 153/153 |
| Op-amp topology (both inputs on one net / shorted outputs) | 46 units clean |
| Polarised caps vs their DC bias | all correct after the C804 fix |
| Module-to-module identity | OSC 1≡2≡3, Filter A≡B≡C≡D |
| Cross-module wiring (must be none, all links go through connectors) | 0 |

SPICE: distortion restructure swept over drive and input level; full chain re-simulated
with the current values (`work/sim/chain_final.cir`). Mixer bias re-checked at
Vb 1.824 / Ve 1.127 / Vc 6.772 V.

---

## 6. Tooling (`tools/`)

Written this session, all reusable:

- **`sexp.py`** — s-expression parser **and serialiser** for KiCad files. Round-trips
  byte-exactly. `parse()` keeps escape sequences verbatim, so `dump()` must **not**
  re-escape them (that bug corrupted the German text notes once).
- **`geom.py`** — geometric connectivity: wires, junctions, labels, symbol pins, and
  `components()` (union-find). Handles labels sitting mid-segment, endpoint-on-segment
  joins, and ignores zero-length wires.
- **`schedit.py`** — reference-based editor: `set_value`, `set_libid`, `set_prop`,
  `set_attr`, `move_symbol`, `del_wire`, `del_zero_wires`, `append_raw`, `insert_libsymbol`.
- **`libembed.py`** — pull an official library symbol into a schematic's `lib_symbols`,
  including `flatten()` for `extends`-derived symbols.
- **`split.py` / `mkboards.py`** — derive the per-board schematics from the master.
- **`connspec.py` / `conndest.py` / `addconn.py`** — the connector specification (net per
  pin) and the physical destination (lug per pin), plus the generator.
- **`footprints.py`**, **`adddecoup.py`**, **`mkproject.py`**, **`mkdocs.py`**, `netlib.py`,
  `audit.py`, `netname.py`.

**PCB side**, added while laying the boards out:

- **`buildall.py`** — one entry point: `python tools/buildall.py [osc|filter|main]`
  rebuilds a board from its placement spec, routes it and prints the audit. This is
  the only command needed to reproduce any board from scratch.
- **`pinplace.py`** — the placement rule. `dip_pins`/`pin_xy` give real pad
  coordinates, `serves()` finds which IC pin a part belongs to, `facing()` rotates it
  so the connecting pad points at the IC, and `spread()` places a column in pin order
  as close to each part's own pin as least squares allows.
- **`place_osc.py` / `place_filter.py` / `place_main.py`** — per-board architecture:
  which IC each part belongs to, which side, how far out. Coordinates are computed.
- **`router.py`** — two-layer A* on a 0.25 mm grid over (x, y, layer), with costs for
  turning, for changing layer, and **for travelling on the back at all**.
- **`routeboard.py`** — ground vias, keepouts, route order (power first, then shortest),
  rip-up-and-reroute, the ground pour, and the project-file restore after `SaveBoard`.
- **`fanout.py`** — finds pads with literally no free neighbouring cell (a 0.65 mm-pitch
  package can seal a pin in) and draws it a stub into open copper.
- **`crtyd.py`** — courtyard check on the *placement*, before anything is built.
- **`checkpcb.py`** — the audit: DRC, plane integrity per layer, board size, silkscreen,
  footprint-to-schematic linkage, pads with no net, track width vs netclass.
- **`fabout.py`** — gerbers, drill files and a zip, with only the layers a two-layer
  board actually has.
- **`stitch.py`** — ground on both layers plus stitching vias. Written, measured, and
  **not used**: once the back-layer cost kept B.Cu whole it added 110 drill hits and
  21 islands of front copper for no benefit. Kept because a denser board would want it
  (`front_pour=True`).
- **`render.py`** — top/bottom renders and a flat layer plot, for looking at.

Older: `svfgen.py` (symbol/wire/label emitters), `svfmodule.py`, `applysvf.py`, `addsafety*.py`.

---

## 7. What is left

**PCB layout** — that is the whole remaining job. Nothing in the schematic is
outstanding. For each board: open the project, *Update PCB from Schematic*, draw the
outline, place, route.

Design rules are already set in each `.kicad_pro`: 0.3 mm default track / 0.25 mm
clearance, a **Power** class at 0.8 mm (matched to `+12V`, `-12V`, `+5V`, `GNDREF`,
`/VIN_*`), an **Audio** class, 0.8/0.4 vias, and DRC minimums that any cheap 2-layer
fab can make (0.2 mm track, 0.3 mm hole, 0.3 mm copper-to-edge).

Worth doing during layout:
- Keep each 100 nF hard against its IC's supply pin — that is the entire point of them.
- Star the grounds back toward the power connector; keep the LM386's return away from
  the oscillator grounds on the main board.
- `U103A`'s summing node and the `RV103`/`RV104` wires leave the board; keep those
  traces short on the board side.
- The 5×20 mm fuse clips (F901/F902) need ~25 mm of edge space each.

---

## 8. Gotchas that cost real time

- **Escaped `\n` in s-expression strings.** Writing a literal newline into a quoted
  string makes KiCad refuse the file with only "Failed to load schematic". `parse()`
  already stores the escape verbatim — do not escape it again on the way out.
- **`(paper "User" …)` and every coordinate must sit on the 1.27 mm grid**, or ERC
  reports `endpoint_off_grid` for every stub you generated.
- **A zero-length wire merges the whole schematic** in a naive union-find. Skip them.
- **A label can sit mid-segment**, not only at a wire endpoint — a connectivity tool that
  only looks at endpoints will report nets as unnamed when they are not.
- **KiCad's root list starts with the bare token `kicad_sch`**, which is not a list;
  iterating top-level elements without checking will emit it into the body.
- **Replacing an embedded symbol can move pins.** Always snapshot pin coordinates
  before and after and shift the instance to compensate.
- **`on_board no` removes a part from the netlist but not from the BOM** — exactly what
  panel hardware needs.
- **`PCB_VIA.GetWidth()` without a layer argument raises a wxWidgets assert**, which in
  a headless script is a dialog box nobody can answer: the process sits at 0 % CPU and
  looks like an infinite loop. Use `GetDrillValue()`. Any unexplained hang at ~0 % CPU
  in a `pcbnew` script is almost certainly an assert dialog.
- **`SaveBoard()` overwrites the `.kicad_pro`** beside the board with a default one, so
  the netclasses have to be rewritten after every save.
- **THT footprints put their origin on pad 1, not in the middle** — place by pad centroid.
- **The obstacle-map cache must be keyed on track width.** It was not, so the 0.6 mm
  power rails were routed against a map built for 0.3 mm tracks and only "fitted" by
  under-counting their own clearance.
- **Never fold already-routed copper into a pad's own cell set.** Doing that let a retry
  treat a finished path as part of the pad, so A* returned a one-cell path and the
  emitted track ran pad-centre to pad-centre — straight through whatever lay between.
- **The one-shot scripts in `tools/` do their work at import time.** `addsafety.py`,
  `adddecoup.py`, `addconn.py`, `footprints.py` and friends were written to be run
  once; importing one - even just to check that it still parses - edits the master
  schematic. Anything that sweeps the directory importing modules must skip them.
- **A greedier A* heuristic is a false economy.** Weighting the heuristic up (1.1 to
  1.5) to beat a small search budget found paths sooner but worse ones, and a worse
  path blocks the next net: the filter board went from routing completely to failing
  a net on nothing but that change. Raise the state budget instead.
- **Validate a placement against each footprint's own courtyard**, not a fixed margin: a
  blanket 0.6 mm guess reported 26 clashes on a layout KiCad's own DRC passed, and the
  collision resolver then "fixed" them by scrambling the deliberate placement.
- **KiCad's silk clearance check does not exempt a footprint from itself** — a reference
  designator sitting on its own connector outline is an error, so a part's own silkscreen
  graphics have to be obstacles when placing its label.
- ngspice `wrdata`: 2 columns per vector for transient, **3 for AC**.
- Op-amp macromodels must clamp the internal integrator node to the rails.
- Relaxation oscillators need a genuinely bistable Schmitt model, not XSPICE `hyst`.
- Always run a timestep convergence check on fast edges.

---

## 9. Backups

`SynthesizerFinal.kicad_sch.bak` is the untouched **original rev 3.0**. `.bak2`–`.bak14`
are successive snapshots from both sessions; `.bak14` is the state immediately before the
KiCad 10 format upgrade. They can be deleted once you are happy with rev 4.0.
