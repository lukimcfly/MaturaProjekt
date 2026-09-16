import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexp

sch = sexp.load(sys.argv[1] if len(sys.argv) > 1 else 'SynthesizerFinal.kicad_sch')

# top-level symbol instances
insts = [c for c in sch if sexp.head(c) == 'symbol']
print(f"top-level symbol instances: {len(insts)}")

rows = []
for s in insts:
    ref = sexp.prop(s, 'Reference', '?')
    valu = sexp.prop(s, 'Value', '?')
    fp  = sexp.prop(s, 'Footprint', '')
    lib = sexp.val(s, 'lib_id', '?')
    unit = sexp.val(s, 'unit', '1')
    dnp = sexp.kid(s, 'dnp')
    excl = sexp.kid(s, 'exclude_from_sim')
    inbom = sexp.val(s, 'in_bom', 'yes')
    onboard = sexp.val(s, 'on_board', 'yes')
    rows.append(dict(ref=ref, val=valu, fp=fp, lib=lib, unit=str(unit),
                     inbom=str(inbom), onboard=str(onboard)))

# unique components (multi-unit share a ref)
byref = collections.OrderedDict()
for r in rows:
    byref.setdefault(r['ref'], []).append(r)

print(f"unique references:          {len(byref)}")

nofp = [r for r, v in byref.items() if not v[0]['fp']]
withfp = [r for r, v in byref.items() if v[0]['fp']]
print(f"WITH footprint:             {len(withfp)}")
print(f"WITHOUT footprint:          {len(nofp)}")

# power symbols don't need footprints
def is_power(v):
    return v[0]['lib'].startswith('power:')
nofp_real = [r for r in nofp if not is_power(byref[r])]
pwr = [r for r in nofp if is_power(byref[r])]
print(f"  of which power symbols:   {len(pwr)}")
print(f"  REAL parts missing fp:    {len(nofp_real)}")

print("\n--- parts WITH a footprint already ---")
for r in withfp:
    print(f"  {r:8s} {byref[r][0]['val'][:28]:30s} {byref[r][0]['fp']}")

print("\n--- unannotated / odd references ---")
import re
for r in byref:
    if not re.fullmatch(r'[A-Z#]+[A-Z]*\d+', r):
        print(f"  {r!r}  ({byref[r][0]['lib']})")

print("\n--- reference prefix histogram (non-power) ---")
h = collections.Counter()
for r, v in byref.items():
    if is_power(v): continue
    m = re.match(r'[A-Za-z_]+', r)
    h[m.group(0) if m else '?'] += 1
for k, c in sorted(h.items()):
    print(f"  {k:6s} {c}")

print("\n--- lib_id histogram (non-power) ---")
h2 = collections.Counter()
for r, v in byref.items():
    if is_power(v): continue
    h2[v[0]['lib']] += 1
for k, c in sorted(h2.items(), key=lambda x: -x[1]):
    print(f"  {c:4d}  {k}")
