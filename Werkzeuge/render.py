"""Renders of a board, for looking at rather than for fabrication."""
import sys, os, subprocess

KICAD = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
OUT = 'work/render'


def render(pcb, name, side='top', width=1400, height=1400, quality='high'):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, '%s_%s.png' % (name, side))
    r = subprocess.run([KICAD, 'pcb', 'render', '--side', side,
                        '--quality', quality, '--background', 'opaque',
                        '--width', str(width), '--height', str(height),
                        '-o', path, pcb], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:400])
    return path


def plot_layers(pcb, name, width=1600):
    """A flat top-view plot: easier to read tracks on than a 3-D render."""
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, '%s_layers.svg' % name)
    r = subprocess.run([KICAD, 'pcb', 'export', 'svg', '--page-size-mode', '2',
                        '--layers', 'F.Cu,B.Cu,Edge.Cuts,F.Silkscreen',
                        '-o', path, pcb], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:400])
    return path


if __name__ == '__main__':
    for name in sys.argv[1:]:
        pcb = 'boards/%s/%s.kicad_pcb' % (name, name)
        for side in ('top', 'bottom'):
            print(render(pcb, name, side))
        print(plot_layers(pcb, name))
