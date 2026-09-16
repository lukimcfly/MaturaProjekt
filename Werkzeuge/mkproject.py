"""Create a .kicad_pro for a schematic, with hobby-fab-friendly design rules."""
import json, os, sys, copy, re

TEMPLATE = r'C:\Program Files\KiCad\10.0\share\kicad\template\Arduino_Nano\Arduino_Nano.kicad_pro'

def root_uuid(sch_path):
    with open(sch_path, encoding='utf-8') as f:
        for line in f:
            m = re.match(r'\s*\(uuid "([0-9a-f-]+)"\)', line)
            if m: return m.group(1)
    raise ValueError("no root uuid")

def make(sch_path, pro_path=None, title="Root"):
    pro_path = pro_path or os.path.splitext(sch_path)[0] + '.kicad_pro'
    d = json.load(open(TEMPLATE, encoding='utf-8'))
    d['meta']['filename'] = os.path.basename(pro_path)
    d['sheets'] = [[root_uuid(sch_path), title]]
    d['boards'] = []
    d['text_variables'] = {}
    d['pcbnew']['last_paths'] = {k: "" for k in d['pcbnew'].get('last_paths', {})}

    ns = d['net_settings']
    default = copy.deepcopy(ns['classes'][0])
    default.update(name="Default", clearance=0.25, track_width=0.3,
                   via_diameter=0.8, via_drill=0.4)
    power = copy.deepcopy(default)
    power.update(name="Power", clearance=0.3, track_width=0.6,
                 via_diameter=1.0, via_drill=0.5, priority=0,
                 pcb_color="rgba(200, 52, 52, 1.000)")
    audio = copy.deepcopy(default)
    audio.update(name="Audio", clearance=0.3, track_width=0.3, priority=1,
                 pcb_color="rgba(72, 148, 72, 1.000)")
    ns['classes'] = [default, power, audio]
    ns['netclass_patterns'] = [
        {"netclass": "Power", "pattern": "+12V"},
        {"netclass": "Power", "pattern": "-12V"},
        {"netclass": "Power", "pattern": "+5V"},
        {"netclass": "Power", "pattern": "GNDREF"},
        {"netclass": "Power", "pattern": "/VIN_P"},
        {"netclass": "Power", "pattern": "/VIN_N"},
    ]

    rules = d['board']['design_settings']['rules']
    rules.update(min_track_width=0.2, min_via_diameter=0.45,
                 min_through_hole_diameter=0.3, min_hole_to_hole=0.5,
                 min_copper_edge_clearance=0.3, min_clearance=0.2,
                 min_silk_clearance=0.15, min_text_height=1.0,
                 min_text_thickness=0.15)
    d['board']['design_settings']['track_widths'] = [0.0, 0.3, 0.5, 0.8, 1.2]
    d['board']['design_settings']['via_dimensions'] = [
        {"diameter": 0.0, "drill": 0.0},
        {"diameter": 0.8, "drill": 0.4},
        {"diameter": 1.0, "drill": 0.5}]

    with open(pro_path, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2)
        f.write("\n")
    return pro_path

if __name__ == "__main__":
    print("wrote", make(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
