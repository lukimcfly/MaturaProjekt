import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schedit import Sch
F = r'C:\Users\timod\Documents\Claude\SynthesizerFinal.kicad_sch'
s = Sch(F)
PRJ = "/0f1e2d3c-4b5a-4697-8899-aabbccddeeff"
c = [0]
def uid():
    c[0] += 1
    return "b5a7f1%02d-0001-4d01-9e01-cc00000000%02d" % (c[0], c[0])

def sym(lib, ref, val, x, y, rot, rx, ry, vx, vy):
    L = [f'\t(symbol', f'\t\t(lib_id "{lib}")', f'\t\t(at {x} {y} {rot})', '\t\t(unit 1)',
         '\t\t(exclude_from_sim no)', '\t\t(in_bom yes)', '\t\t(on_board yes)', '\t\t(dnp no)',
         f'\t\t(uuid "{uid()}")']
    for nm, vv, px, py, hide in (("Reference", ref, rx, ry, False), ("Value", val, vx, vy, False),
                                 ("Footprint", "", x, y, True), ("Datasheet", "~", x, y, True),
                                 ("Description", "", x, y, True)):
        L += [f'\t\t(property "{nm}" "{vv}"', f'\t\t\t(at {px} {py} 0)', '\t\t\t(effects',
              '\t\t\t\t(font', '\t\t\t\t\t(size 1.27 1.27)', '\t\t\t\t)']
        L += ['\t\t\t\t(hide yes)'] if hide else ['\t\t\t\t(justify left)']
        L += ['\t\t\t)', '\t\t)']
    L += ['\t\t(instances', '\t\t\t(project ""', f'\t\t\t\t(path "{PRJ}"',
          f'\t\t\t\t\t(reference "{ref}")', '\t\t\t\t\t(unit 1)', '\t\t\t\t)', '\t\t\t)', '\t\t)', '\t)']
    return L

def pwr(ref, val, x, y):
    L = [f'\t(symbol', f'\t\t(lib_id "power:{val}")', f'\t\t(at {x} {y} 0)', '\t\t(unit 1)',
         '\t\t(exclude_from_sim no)', '\t\t(in_bom yes)', '\t\t(on_board yes)', '\t\t(dnp no)',
         f'\t\t(uuid "{uid()}")']
    for nm, vv, hide in (("Reference", ref, True), ("Value", val, False),
                         ("Footprint", "", True), ("Datasheet", "", True), ("Description", "", True)):
        yy = y - 6.35 if nm == "Value" else y
        L += [f'\t\t(property "{nm}" "{vv}"', f'\t\t\t(at {x} {yy} 0)', '\t\t\t(effects',
              '\t\t\t\t(font', '\t\t\t\t\t(size 1.27 1.27)', '\t\t\t\t)']
        L += ['\t\t\t\t(hide yes)'] if hide else ['\t\t\t\t)']
        L += (['\t\t\t)', '\t\t)'] if hide else ['\t\t)'])
    L += ['\t\t(instances', '\t\t\t(project ""', f'\t\t\t\t(path "{PRJ}"',
          f'\t\t\t\t\t(reference "{ref}")', '\t\t\t\t\t(unit 1)', '\t\t\t\t)', '\t\t\t)', '\t\t)', '\t)']
    return L

def wire(x1, y1, x2, y2):
    return ['\t(wire', '\t\t(pts', f'\t\t\t(xy {x1} {y1})', f'\t\t\t(xy {x2} {y2})', '\t\t)',
            '\t\t(stroke', '\t\t\t(width 0)', '\t\t\t(type default)', '\t\t)', f'\t\t(uuid "{uid()}")', '\t)']

def label(nm, x, y):
    return [f'\t(label "{nm}"', f'\t\t(at {x} {y} 0)', '\t\t(fields_autoplaced yes)', '\t\t(effects',
            '\t\t\t(font', '\t\t\t\t(size 1.27 1.27)', '\t\t\t)', '\t\t\t(justify left bottom)', '\t\t)',
            f'\t\t(uuid "{uid()}")', '\t)']

def text(t, x, y):
    return [f'\t(text "{t}"', '\t\t(exclude_from_sim no)', f'\t\t(at {x} {y} 0)', '\t\t(effects',
            '\t\t\t(font', '\t\t\t\t(size 1.27 1.27)', '\t\t\t)', '\t\t\t(justify left top)', '\t\t)',
            f'\t\t(uuid "{uid()}")', '\t)']

out = []
# --- tap J990 pins 1 and 3 onto named nets ---
out += wire(668.02, 839.47, 675.64, 839.47) + label("VIN_P", 675.64, 839.47)
out += wire(668.02, 844.55, 675.64, 844.55) + label("VIN_N", 675.64, 844.55)
# --- +12 V protection chain:  VIN_P -> F901 -> D907(anode left) -> +12V ---
out += label("VIN_P", 600.71, 878.84) + wire(600.71, 878.84, 603.25, 878.84)
out += sym("Device:Fuse", "F901", "T500mA", 607.06, 878.84, 90, 607.06, 873.76, 607.06, 883.92)
out += wire(610.87, 878.84, 613.41, 878.84)
out += sym("Diode:1N5819", "D907", "1N5819", 617.22, 878.84, 180, 617.22, 873.76, 617.22, 883.92)
out += wire(621.03, 878.84, 623.57, 878.84)
out += pwr("#PWR8320", "+12V", 623.57, 878.84)
# --- -12 V protection chain:  -12V <- D908(anode right) <- F902 <- VIN_N ---
out += label("VIN_N", 600.71, 891.54) + wire(600.71, 891.54, 603.25, 891.54)
out += sym("Device:Fuse", "F902", "T500mA", 607.06, 891.54, 90, 607.06, 886.46, 607.06, 896.62)
out += wire(610.87, 891.54, 613.41, 891.54)
out += sym("Diode:1N5819", "D908", "1N5819", 617.22, 891.54, 0, 617.22, 886.46, 617.22, 896.62)
out += wire(621.03, 891.54, 623.57, 891.54)
out += pwr("#PWR8321", "-12V", 623.57, 891.54)
out += text("VERPOLUNGS- UND UEBERSTROMSCHUTZ", 600.71, 862.33)
out += text("F901/F902 begrenzen den Strom bei einem Kurzschluss.\nD907/D908 (Schottky) sperren, wenn der Netzstecker verpolt ist:\n+12 V und -12 V koennen dann nicht vertauscht an die ICs gelangen.\nSpannungsverlust ca. 0,3 V pro Schiene.", 600.71, 900.43)
s.append_raw(out)
s.save(F)
print(f"inserted {len(out)} lines: F901 F902 D907 D908 + 8 wires + 4 labels + 2 power symbols + notes")
