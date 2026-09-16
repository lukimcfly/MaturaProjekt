"""Keep every board version, so the current one can be compared with what came before.

Timo asked for this explicitly: whatever gets changed, the previous design has to
stay visible next to the new one. A board is snapshotted under
`archiv/<board>/<tag>/` together with the placement file that produced it and the
audit numbers, so a later version can be held against it.
"""
import sys, os, json, shutil, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = 'archiv'


def snapshot(name, tag, note='', place_module=None):
    """Copy a board, its placement source and its audit into archiv/<name>/<tag>/."""
    dest = os.path.join(ROOT, name, tag)
    os.makedirs(dest, exist_ok=True)
    kept = []
    for ext in ('.kicad_pcb', '.kicad_sch', '.kicad_pro'):
        src = os.path.join('boards', name, name + ext)
        if os.path.exists(src):
            shutil.copy2(src, dest)
            kept.append(os.path.basename(src))
    src = os.path.join('tools', place_module or ('place_%s.py' % name))
    if os.path.exists(src):
        shutil.copy2(src, dest)
        kept.append(os.path.basename(src))

    meta = dict(board=name, tag=tag, note=note,
                when=datetime.datetime.now().isoformat(timespec='seconds'),
                files=kept)
    try:
        import checkpcb, buildall
        spec = buildall.BOARDS.get(name, {})
        a = checkpcb.audit(os.path.join(dest, name + '.kicad_pcb'),
                           ic_refs=spec.get('ics', ()),
                           no_connect=spec.get('nc', ()))
        meta['audit'] = {k: a[k] for k in
                         ('size', 'tracks', 'vias', 'back_pct', 'plane_mm2',
                          'planes', 'drc', 'unconnected') if k in a}
    except Exception as e:                       # a snapshot is worth keeping even
        meta['audit_error'] = str(e)[:200]       # if the audit cannot run on it
    with open(os.path.join(dest, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    return dest, meta


def table(name):
    """One row per archived version, oldest first."""
    base = os.path.join(ROOT, name)
    if not os.path.isdir(base):
        return []
    rows = []
    for tag in sorted(os.listdir(base)):
        p = os.path.join(base, tag, 'info.json')
        if os.path.exists(p):
            rows.append(json.load(open(p, encoding='utf-8')))
    return rows


if __name__ == '__main__':
    d, m = snapshot(sys.argv[1], sys.argv[2], ' '.join(sys.argv[3:]))
    print('archived ->', d)
    print(json.dumps(m.get('audit', m.get('audit_error')), indent=2))
