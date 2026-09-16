"""Fabrication output: the layers a two-layer board actually needs, and nothing else.

The first pass exported every layer KiCad knows about, which meant fifteen empty
files (Adhesive, Eco1/2, User_1..4, Margin) sitting in the fab package.  Empty
layers are not harmful but they are an invitation for a board house to ask which
one is the real silkscreen, so only the seven that carry anything are written.
"""
import sys, os, glob, zipfile, subprocess

KICAD = r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
LAYERS = 'F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts'


def _run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(' '.join(args[:4]) + ': ' + (r.stderr or r.stdout).strip()[:500])
    return r.stdout


def export(pcb, outdir):
    if os.path.isdir(outdir):
        for f in glob.glob(os.path.join(outdir, '*')):
            os.remove(f)
    os.makedirs(outdir, exist_ok=True)
    _run([KICAD, 'pcb', 'export', 'gerbers', '--layers', LAYERS,
          '--no-protel-ext', '--subtract-soldermask', '-o', outdir, pcb])
    _run([KICAD, 'pcb', 'export', 'drill', '--format', 'excellon',
          '--drill-origin', 'absolute', '--excellon-units', 'mm',
          '--excellon-separate-th', '--generate-map', '--map-format', 'gerberx2',
          '-o', outdir, pcb])
    return sorted(os.path.basename(f) for f in glob.glob(os.path.join(outdir, '*')))


def zip_up(outdir, zippath):
    with zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(os.path.join(outdir, '*'))):
            z.write(f, os.path.basename(f))
    return os.path.getsize(zippath)


if __name__ == '__main__':
    for name in sys.argv[1:]:
        pcb = 'boards/%s/%s.kicad_pcb' % (name, name)
        out = 'fab/%s' % name
        files = export(pcb, out)
        size = zip_up(out, 'fab/%s.zip' % name)
        empty = [f for f in files if os.path.getsize(os.path.join(out, f)) < 400
                 and f.endswith('.gbr')]
        print('%-7s %2d files -> fab/%s.zip (%d kB)%s'
              % (name, len(files), name, size // 1024,
                 '  suspiciously small: %s' % empty if empty else ''))
