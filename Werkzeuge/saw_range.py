"""Sawtooth core of the oscillator board: frequency range over pot setting and
Schmitt-trigger corners.

Circuit exactly as on the board (osc netlist, 2026-09-21):
  +5V -> RV_01 (0..1M, pitch pot) -> R101 10k -> node;  C101 node->GND
  node -> 74LVC2G17 input;  output -> R102 1k -> BC547 base;  node -> R103 220 -> collector
Thresholds from the TI SN74LVC2G17 datasheet, interpolated to VCC = 5 V:
  VT+ 2.05 .. 3.4 V,  VT- 1.25 .. 2.25 V (typicals are only given at 3.3 V).
"""
import subprocess, os, re, sys

STEP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.2e-6   # max time step: the flyback lasts ~1 us

NGSPICE = r'C:\Users\timod\AppData\Local\ngspice\Spice64\bin\ngspice_con.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'models', 'models.lib').replace('\\', '/')

CORNERS = {                  # (VT+, VT-)
    'typ':            (2.70, 1.75),
    'low thresholds': (2.05, 1.40),
    'high thresh.':   (3.40, 2.05),
}


def period(c1, rpot, vtp, vtn):
    vtc, vthy = (vtp + vtn) / 2, (vtp - vtn) / 2
    rtot = rpot + 10e3
    t_est = 0.6 * rtot * c1 + 20e-6          # generous upper bound for one period
    tstop = 6 * t_est
    step = min(t_est / 4000, STEP)
    net = f"""* saw core
.include {LIB}
Vp5 p5 0 DC 5
Rch p5 ramp {rtot}
C101 ramp 0 {c1}
R103 ramp qc 220
Q101 qc qb 0 QBC547
R102 qb sq 1k
Bsch nst 0 v='2.5*(1+tanh((v(ramp) - ({vtc} - {vthy}*(v(sq)/2.5 - 1)))/1m))'
Rd nst sq 20
Cd sq 0 100p
.ic v(ramp)=0
.tran {step} {tstop} 0 {step} uic
.meas tran t1 when v(sq)=2.5 rise=2
.meas tran t2 when v(sq)=2.5 rise=4
.end
"""
    p = os.path.join(HERE, '_saw_tmp.cir')
    open(p, 'w').write(net)
    r = subprocess.run([NGSPICE, '-b', p], capture_output=True, text=True, cwd=HERE)
    m1 = re.search(r't1\s*=\s*([0-9.eE+-]+)', r.stdout)
    m2 = re.search(r't2\s*=\s*([0-9.eE+-]+)', r.stdout)
    if not (m1 and m2):
        return None
    return (float(m2.group(1)) - float(m1.group(1))) / 2


if __name__ == '__main__':
    for c1 in (47e-9, 56e-9):
        print('C101 = %.0f nF' % (c1 * 1e9))
        for name, (vtp, vtn) in CORNERS.items():
            fs = []
            for rpot in (0, 1e6):
                t = period(c1, rpot, vtp, vtn)
                fs.append(1 / t if t else float('nan'))
            print('   %-15s  pot 0: %7.0f Hz   pot 1M: %6.1f Hz' % (name, fs[0], fs[1]))
