"""Saw level at the waveform switch after the R124 change (U103D gain = -R124/R123).

Swing at C101 is measured in the transient (it includes the flyback undershoot),
then multiplied by the amplifier gain; the other waveforms sit at about 7 Vpp.
"""
import subprocess, os, re

NGSPICE = r'C:\Users\timod\AppData\Local\ngspice\Spice64\bin\ngspice_con.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'models', 'models.lib').replace('\\', '/')
C1, GAIN = 56e-9, 56e3 / 10e3
CORNERS = {'typ': (2.70, 1.75), 'low thresholds': (2.05, 1.40), 'high thresh.': (3.40, 2.05)}


def swing(rpot, vtp, vtn):
    vtc, vthy = (vtp + vtn) / 2, (vtp - vtn) / 2
    rtot = rpot + 10e3
    t_est = 0.6 * rtot * C1 + 20e-6
    step = min(t_est / 4000, 0.2e-6)
    net = f"""* saw level
.include {LIB}
Vp5 p5 0 DC 5
Rch p5 ramp {rtot}
C101 ramp 0 {C1}
R103 ramp qc 220
Q101 qc qb 0 QBC547
R102 qb sq 1k
Bsch nst 0 v='2.5*(1+tanh((v(ramp) - ({vtc} - {vthy}*(v(sq)/2.5 - 1)))/1m))'
Rd nst sq 20
Cd sq 0 100p
.ic v(ramp)=0
.tran {step} {6 * t_est} 0 {step} uic
.meas tran vmin MIN v(ramp) from={3 * t_est} to={6 * t_est}
.meas tran vmax MAX v(ramp) from={3 * t_est} to={6 * t_est}
.end
"""
    p = os.path.join(HERE, '_lvl_tmp.cir')
    open(p, 'w').write(net)
    out = subprocess.run([NGSPICE, '-b', p], capture_output=True, text=True, cwd=HERE).stdout
    os.remove(p)
    lo = float(re.search(r'vmin\s*=\s*([0-9.eE+-]+)', out).group(1))
    hi = float(re.search(r'vmax\s*=\s*([0-9.eE+-]+)', out).group(1))
    return hi - lo


if __name__ == '__main__':
    for name, (vtp, vtn) in CORNERS.items():
        a, b = swing(0, vtp, vtn), swing(1e6, vtp, vtn)
        print('%-15s swing %.2f..%.2f V  ->  saw %.1f..%.1f Vpp' % (name, a, b, a * GAIN, b * GAIN))
