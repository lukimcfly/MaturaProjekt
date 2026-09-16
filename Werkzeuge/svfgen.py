"""Emit a state-variable filter module as kicad_sch s-expressions."""
PRJ = "/0f1e2d3c-4b5a-4697-8899-aabbccddeeff"
_c = [0]
def uid():
    _c[0] += 1
    return "5f000000-%04x-4a01-9b01-%012x" % (_c[0], _c[0])

def _prop(nm, val, x, y, hide, rot=0):
    L = [f'\t\t(property "{nm}" "{val}"', f'\t\t\t(at {x} {y} {rot})', '\t\t\t(effects',
         '\t\t\t\t(font', '\t\t\t\t\t(size 1.27 1.27)', '\t\t\t\t)']
    L += ['\t\t\t\t(hide yes)'] if hide else ['\t\t\t\t(justify left)']
    L += ['\t\t\t)', '\t\t)']
    return L

def sym(lib, ref, val, x, y, rot=0, unit=1, rx=None, ry=None, vx=None, vy=None):
    rx = x + 2.54 if rx is None else rx; ry = y - 2.54 if ry is None else ry
    vx = x + 2.54 if vx is None else vx; vy = y + 2.54 if vy is None else vy
    L = ['\t(symbol', f'\t\t(lib_id "{lib}")', f'\t\t(at {x} {y} {rot})', f'\t\t(unit {unit})',
         '\t\t(exclude_from_sim no)', '\t\t(in_bom yes)', '\t\t(on_board yes)', '\t\t(dnp no)',
         f'\t\t(uuid "{uid()}")']
    L += _prop("Reference", ref, rx, ry, False)
    L += _prop("Value", val, vx, vy, False)
    for p in ("Footprint", "Datasheet", "Description"):
        L += _prop(p, "~" if p == "Datasheet" else "", x, y, True)
    L += ['\t\t(instances', '\t\t\t(project ""', f'\t\t\t\t(path "{PRJ}"',
          f'\t\t\t\t\t(reference "{ref}")', f'\t\t\t\t\t(unit {unit})', '\t\t\t\t)', '\t\t\t)', '\t\t)', '\t)']
    return L

def pwrsym(ref, val, x, y, rot=0):
    L = ['\t(symbol', f'\t\t(lib_id "power:{val}")', f'\t\t(at {x} {y} {rot})', '\t\t(unit 1)',
         '\t\t(exclude_from_sim no)', '\t\t(in_bom yes)', '\t\t(on_board yes)', '\t\t(dnp no)',
         f'\t\t(uuid "{uid()}")']
    L += _prop("Reference", ref, x, y, True)
    L += _prop("Value", val, x, y + (6.35 if rot == 0 else -6.35), False)
    for p in ("Footprint", "Datasheet", "Description"):
        L += _prop(p, "", x, y, True)
    L += ['\t\t(instances', '\t\t\t(project ""', f'\t\t\t\t(path "{PRJ}"',
          f'\t\t\t\t\t(reference "{ref}")', '\t\t\t\t\t(unit 1)', '\t\t\t\t)', '\t\t\t)', '\t\t)', '\t)']
    return L

def wire(x1, y1, x2, y2):
    return ['\t(wire', '\t\t(pts', f'\t\t\t(xy {x1} {y1})', f'\t\t\t(xy {x2} {y2})', '\t\t)',
            '\t\t(stroke', '\t\t\t(width 0)', '\t\t\t(type default)', '\t\t)', f'\t\t(uuid "{uid()}")', '\t)']

def label(nm, x, y, rot=0):
    return [f'\t(label "{nm}"', f'\t\t(at {x} {y} {rot})', '\t\t(fields_autoplaced yes)', '\t\t(effects',
            '\t\t\t(font', '\t\t\t\t(size 1.27 1.27)', '\t\t\t)', '\t\t\t(justify left bottom)', '\t\t)',
            f'\t\t(uuid "{uid()}")', '\t)']

def junction(x, y):
    return ['\t(junction', f'\t\t(at {x} {y})', '\t\t(diameter 0)', '\t\t(color 0 0 0 0)',
            f'\t\t(uuid "{uid()}")', '\t)']

def textnote(t, x, y):
    return [f'\t(text "{t}"', '\t\t(exclude_from_sim no)', f'\t\t(at {x} {y} 0)', '\t\t(effects',
            '\t\t\t(font', '\t\t\t\t(size 1.27 1.27)', '\t\t\t)', '\t\t\t(justify left top)', '\t\t)',
            f'\t\t(uuid "{uid()}")', '\t)']
