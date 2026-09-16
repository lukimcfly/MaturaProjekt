"""Footprint assignment for the synth boards (THT-first, SMD only where no DIP exists)."""
R_AX   = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
C_DISC = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
FILM_S = "Capacitor_THT:C_Rect_L7.0mm_W2.5mm_P5.00mm"
FILM_L = "Capacitor_THT:C_Rect_L7.0mm_W4.5mm_P5.00mm"
EL_5   = "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm"
EL_63  = "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"
EL_10  = "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"

CAP_BY_VALUE = {
    "100nF": C_DISC, "330nF": FILM_S, "47nF": FILM_S, "15nF": FILM_S, "6.8nF": FILM_S,
    "1uF": FILM_L,
    "10uF/25V bipolar": EL_5,
    "10uF/16V": EL_5, "10uF/25V": EL_5,
    "47uF/25V": EL_63, "100uF/25V": EL_63,
    "470uF/16V": EL_10, "470uF/25V": EL_10,
}
BY_PART = {
    "R_US":         R_AX,
    "1N4148":       "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal",
    "1N4148WT":     "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal",
    "1N5819":       "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
    "BC547":        "Package_TO_SOT_THT:TO-92_Inline_Wide",   # 2.54 mm: 1.27 mm fails clearance
    "LM78L05_TO92": "Package_TO_SOT_THT:TO-92_Inline_Wide",
    "TL074":        "Package_DIP:DIP-14_W7.62mm_Socket",
    "LM386":        "Package_DIP:DIP-8_W7.62mm_Socket",
    "OPA4196xPW":   "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
    "OPA4196xD":    "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",   # 1.27mm pitch: hand-solderable
    "OPA1662D":     "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
    "74LVC2G17":    "Package_TO_SOT_SMD:SOT-363_SC-70-6",
    "Fuse":         "Fuse:Fuseholder_Clip-5x20mm_Littelfuse_111_Inline_P20.00x5.00mm_D1.05mm_Horizontal",
}
JST = {2:  "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
       3:  "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical",
       4:  "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
       6:  "Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical",
       11: "Connector_JST:JST_XH_B11B-XH-A_1x11_P2.50mm_Vertical",
       12: "Connector_JST:JST_XH_B12B-XH-A_1x12_P2.50mm_Vertical",
       14: "Connector_JST:JST_XH_B14B-XH-A_1x14_P2.50mm_Vertical"}

PANEL_JACKS = {'J101','J102','J103','J201','J202','J203','J301','J302','J303',
               'J601','J602','J701','J702'}

def is_panel(ref):
    return ref.startswith(('RV', 'SW')) or ref in PANEL_JACKS

def footprint_for(ref, part, value):
    if is_panel(ref):
        return None
    if part.startswith('Conn_01x'):
        return JST[int(part[8:])]
    if part in ('C', 'C_Polarized_US'):
        return CAP_BY_VALUE[value]
    return BY_PART[part]
