"""Front-panel overview of every user control, generated from one list so nothing is
drawn twice or forgotten. Functional overview - not to scale, not the final layout.
Control names and references follow Platinen/VERDRAHTUNG.md.
"""
import math, sys

W, H = 1400, 1096
out = []
def add(s): out.append(s)

C_OSC, C_OSC_S = '#E1F5EE', '#0F6E56'
C_FIL, C_FIL_S = '#EEEDFE', '#534AB7'
C_MIX, C_MIX_S = '#FAEEDA', '#854F0B'
C_SCO, C_SCO_S = '#F1EFE8', '#5F5E5A'
INK, MUTED, REF = '#2C2C2A', '#5F5E5A', '#888780'

def text(x, y, s, size=12, weight=400, fill=INK, anchor='middle', italic=False):
    st = ' font-style="italic"' if italic else ''
    add('<text x="%.1f" y="%.1f" font-size="%s" font-weight="%d" fill="%s" text-anchor="%s"%s>%s</text>'
        % (x, y, size, weight, fill, anchor, st, s))

def panel(x, y, w, h, title, fill, stroke, sub=None):
    add('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="1.5"/>' % (x, y, w, h, fill, stroke))
    text(x + w / 2, y + 26, title, 15, 700, stroke)
    if sub:
        text(x + w / 2, y + 43, sub, 11, 400, stroke, italic=True)

def knob(cx, cy, r, label, ref, rng=None, pointer=-50):
    add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#3a3a38" stroke="#1c1c1b" stroke-width="2"/>' % (cx, cy, r))
    add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#4a4a47"/>' % (cx, cy, r * 0.72))
    a = math.radians(pointer - 90)
    add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
        % (cx + 0.2 * r * math.cos(a), cy + 0.2 * r * math.sin(a), cx + 0.85 * r * math.cos(a), cy + 0.85 * r * math.sin(a)))
    # scale ticks
    for k in range(11):
        t = math.radians(-135 + 27 * k - 90)
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2"/>'
            % (cx + (r + 4) * math.cos(t), cy + (r + 4) * math.sin(t), cx + (r + 8) * math.cos(t), cy + (r + 8) * math.sin(t), MUTED))
    text(cx, cy + r + 24, label, 13, 700)
    yy = cy + r + 38
    if rng:
        text(cx, yy, rng, 11, 400, MUTED); yy += 13
    text(cx, yy, ref, 10, 400, REF)

def rotary(cx, cy, r, label, ref, positions, lab_r=None, start=-120, span=240):
    lab_r = lab_r or r + 16
    n = len(positions)
    for i, p in enumerate(positions):
        ang = start + (span * i / (n - 1) if n > 1 else 0)
        t = math.radians(ang - 90)
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5"/>'
            % (cx + (r + 3) * math.cos(t), cy + (r + 3) * math.sin(t), cx + (r + 9) * math.cos(t), cy + (r + 9) * math.sin(t), INK))
        lx, ly = cx + lab_r * math.cos(t), cy + lab_r * math.sin(t) + 4
        anchor = 'middle' if abs(math.cos(t)) < 0.3 else ('start' if math.cos(t) > 0 else 'end')
        text(lx, ly, p, 11, 400, INK, anchor)
    add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#3a3a38" stroke="#1c1c1b" stroke-width="2"/>' % (cx, cy, r))
    t = math.radians(start - 90)
    add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
        % (cx, cy, cx + 0.85 * r * math.cos(t), cy + 0.85 * r * math.sin(t)))
    text(cx, cy + r + 24, label, 13, 700)
    text(cx, cy + r + 38, ref, 10, 400, REF)

def toggle(cx, cy, label, up, down, ref):
    add('<rect x="%.1f" y="%.1f" width="22" height="34" rx="4" fill="#d9d7ce" stroke="%s" stroke-width="1.5"/>' % (cx - 11, cy - 17, MUTED))
    add('<circle cx="%.1f" cy="%.1f" r="5" fill="#8a8880"/>' % (cx, cy))
    add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#555" stroke-width="4" stroke-linecap="round"/>' % (cx, cy, cx, cy - 13))
    text(cx, cy - 24, up, 10, 400, MUTED)
    text(cx, cy + 30, down, 10, 400, MUTED)
    text(cx, cy + 46, label, 12, 700)
    text(cx, cy + 59, ref, 10, 400, REF)

def jack(cx, cy, label, ref):
    add('<circle cx="%.1f" cy="%.1f" r="11" fill="#c9c7be" stroke="%s" stroke-width="1.5"/>' % (cx, cy, MUTED))
    add('<circle cx="%.1f" cy="%.1f" r="4.5" fill="#1c1c1b"/>' % (cx, cy))
    text(cx, cy + 27, label, 12, 700)
    text(cx, cy + 40, ref, 10, 400, REF)

add('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Segoe UI, Arial, sans-serif">' % (W, H, W, H))
add('<rect width="100%" height="100%" fill="#ffffff"/>')
text(20, 38, 'Bedienfeld – alle Bedienelemente eines Geräts', 22, 700, INK, 'start')
text(20, 60, 'Funktionsübersicht, nicht massstäblich · Namen und Referenzen wie in Platinen/VERDRAHTUNG.md · Stand 21.09.2026', 12, 400, MUTED, 'start')

# ---------------- oscillators ----------------
for i in range(3):
    x0, y0, w, h = 20 + i * 460, 78, 440, 432
    panel(x0, y0, w, h, 'OSZILLATOR %d' % (i + 1), C_OSC, C_OSC_S, 'Klangquelle')
    knob(x0 + 62, y0 + 128, 36, 'Tonhöhe', 'RV_01 + RV_02 (Tandem)', '48 Hz – 4,9 kHz', pointer=-20)
    knob(x0 + 180, y0 + 250, 25, 'Amplitude', 'RV_05', pointer=40)
    rotary(x0 + 180, y0 + 128, 25, 'Wellenform', 'SW_01', ['Sinus', 'Dreieck', 'Rechteck', 'Sägezahn'], lab_r=42, start=-100, span=200)
    # distortion block
    dx, dy = x0 + 285, y0 + 56
    add('<rect x="%d" y="%d" width="144" height="232" rx="8" fill="#ffffff" fill-opacity="0.55" stroke="%s" stroke-dasharray="4 3"/>' % (dx, dy, C_OSC_S))
    text(dx + 72, dy + 18, 'DISTORTION', 12, 700, C_OSC_S)
    toggle(dx + 38, dy + 66, 'ein/aus', 'ein', 'aus', 'SW_03')
    toggle(dx + 106, dy + 66, 'Charakter', 'weich', 'hart', 'SW_02')
    knob(dx + 38, dy + 168, 20, 'Drive', 'RV_03', pointer=-80)
    knob(dx + 106, dy + 168, 20, 'Pegel', 'RV_04', pointer=10)
    # bottom strip: solo filter + jacks
    add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-opacity="0.35"/>' % (x0 + 14, y0 + 328, x0 + w - 14, y0 + 328, C_OSC_S))
    toggle(x0 + 180, y0 + 360, 'Solo-Filter', 'ein', 'aus', 'SW_04')
    jack(x0 + 62, y0 + 366, 'Ausgang', 'J_03')
    jack(x0 + 300, y0 + 366, 'Send', 'J_01')
    jack(x0 + 380, y0 + 366, 'Return', 'J_02')

# ---------------- mixer ----------------
x0, y0, w, h = 20, 528, 190, 460
panel(x0, y0, w, h, 'MIXER', C_MIX, C_MIX_S, 'Hauptplatine')
for k, (cy, pt) in enumerate(((y0 + 110, -30), (y0 + 240, 20), (y0 + 370, -60))):
    knob(x0 + 95, cy, 23, 'Kanal %d' % (k + 1), 'RV80%d · Pegel OSZ %d' % (k + 1, k + 1), pointer=pt)

# ---------------- filters ----------------
names = [('A', 'fest nach dem Mixer'), ('B', 'fest nach Filter A'), ('C', 'frei per Patchkabel'), ('D', 'frei per Patchkabel')]
for k, (nm, sub) in enumerate(names):
    x0, y0, w, h = 224 + k * 188, 528, 176, 460
    panel(x0, y0, w, h, 'FILTER %s' % nm, C_FIL, C_FIL_S, sub)
    knob(x0 + 88, y0 + 98, 30, 'Cutoff', 'RV_01 + RV_02 (Tandem)', '106 Hz – 10,6 kHz', pointer=-10)
    knob(x0 + 88, y0 + 216, 21, 'Resonanz', 'RV_03', pointer=30)
    rotary(x0 + 88, y0 + 332, 20, 'Filterart', 'SW_01', ['Tief', 'Hoch', 'Band', 'Kerbe', 'aus'], lab_r=34, start=-110, span=220)
    if nm in 'CD':
        jack(x0 + 50, y0 + 410, 'In', 'J_01')
        jack(x0 + 126, y0 + 410, 'Out', 'J_02')
    else:
        text(x0 + 88, y0 + 422, '(keine Buchsen)', 11, 400, MUTED, italic=True)

# ---------------- master + oscilloscope ----------------
x0, y0, w, h = 980, 528, 400, 460
panel(x0, y0, w, h, 'AUSGANG + OSZILLOSKOP', C_SCO, C_SCO_S, 'Hauptplatine + Arduino')
sx, sy, sw, sh = x0 + 18, y0 + 58, 206, 156
add('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="#0b1016" stroke="#1c1c1b" stroke-width="2"/>' % (sx, sy, sw, sh))
for gx in range(1, 8):
    add('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#1f2c38"/>' % (sx + gx * sw / 8, sy + 16, sx + gx * sw / 8, sy + sh - 6))
pts = []
for i in range(0, 181):
    t = i / 180 * 3.4
    v = (t % 1.0)
    pts.append('%.1f,%.1f' % (sx + 8 + i * (sw - 16) / 180, sy + sh - 20 - v * (sh - 50)))
add('<polyline points="%s" fill="none" stroke="#5fd38a" stroke-width="2"/>' % ' '.join(pts))
add('<text x="%d" y="%d" font-size="10" fill="#dce6ee" font-family="Consolas, monospace">2095 Hz  1.3-3.2V</text>' % (sx + 8, sy + 13))
text(sx + sw / 2, sy + sh + 20, 'Oszilloskop-Display', 13, 700)
text(sx + sw / 2, sy + sh + 34, 'zeigt das Signal nach Filter B', 11, 400, MUTED)
# mode button (not yet planned)
bx, by = sx + sw / 2, y0 + 300
add('<circle cx="%.1f" cy="%.1f" r="16" fill="#c9c7be" stroke="#5F5E5A" stroke-width="1.5"/>' % (bx, by))
add('<circle cx="%.1f" cy="%.1f" r="10" fill="#e24b4a" stroke="#a32d2d" stroke-width="1.5"/>' % (bx, by))
text(bx, by + 34, 'Modus-Taster', 12, 700)
text(bx, by + 47, 'ZEIT → FIGUR → FREI · an Arduino RESET', 10, 400, REF)
knob(x0 + 312, y0 + 104, 34, 'Master', 'RV901 · Lautstärke', pointer=0)
# speaker grille
gx, gy = x0 + 312, y0 + 268
add('<circle cx="%d" cy="%d" r="46" fill="#d9d7ce" stroke="%s" stroke-width="1.5"/>' % (gx, gy, MUTED))
for rr in (10, 20, 30, 40):
    add('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#8a8880" stroke-width="1"/>' % (gx, gy, rr))
text(gx, gy + 64, 'Lautsprecher 8 Ω', 12, 700)
# power
toggle(x0 + 238, y0 + 340, 'Netz', 'ein', 'aus', 'Hauptschalter')

# ---------------- rear + summary ----------------
yb = 1006
add('<rect x="20" y="%d" width="%d" height="78" rx="10" fill="#fafaf7" stroke="#d3d1c7"/>' % (yb, W - 40))
text(36, yb + 24, 'Signalweg:', 12, 700, INK, 'start')
text(118, yb + 24, 'Oszillator 1-3 → Mixer → Filter A → Filter B → Master → Lautsprecher.   Filter C, D: per Patchkabel zwischen Send und Return eines Oszillators (Solo-Filter ein).', 12, 400, INK, 'start')
text(36, yb + 46, 'Pro Gerät:', 12, 700, INK, 'start')
text(118, yb + 46, '24 Drehknöpfe (3 + 4 davon Tandem-Potis) · 7 Drehschalter · 9 Kippschalter + Netzschalter · 1 Taster · 13 Klinkenbuchsen · Display · Lautsprecher', 12, 400, INK, 'start')
text(36, yb + 68, 'Rückseite:', 12, 700, INK, 'start')
text(118, yb + 68, 'DC-Buchse 12 V (Netzteil) · alle Teile stehen in Einkauf/Einkaufsliste_Synthesizer.xlsx', 12, 400, INK, 'start')
add('</svg>')

html = '<html><head><meta charset="utf-8"><style>body{margin:0;background:#fff}</style></head><body>' + '\n'.join(out) + '</body></html>'
open(sys.argv[1], 'w', encoding='utf-8').write(html)
print('ok', W, H)
