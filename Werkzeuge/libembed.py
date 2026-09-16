"""Embed official library symbols into a .kicad_sch lib_symbols block."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexp

SYMDIR = r'C:\Program Files\KiCad\10.0\share\kicad\symbols'
# tokens KiCad 10 writes that a 20250114-format file does not carry
STRIP = ('in_pos_files', 'duplicate_pin_numbers_are_jumpers', 'embedded_fonts')

_cache = {}
def _lib(name):
    if name not in _cache:
        _cache[name] = sexp.load(os.path.join(SYMDIR, name + '.kicad_sym'))
    return _cache[name]

def official(libname, symname):
    for s in sexp.kids(_lib(libname), 'symbol'):
        if s[1] == symname:
            return s
    raise KeyError(f"{libname}:{symname}")

def _clean(node):
    out = []
    for c in node:
        if isinstance(c, list):
            if sexp.head(c) in STRIP:
                continue
            out.append(_clean(c))
        else:
            out.append(c)
    return out

def embedded_form(libname, symname):
    """Official symbol -> the form stored inside a schematic's lib_symbols."""
    s = _clean(official(libname, symname))
    s = list(s)
    s[1] = f"{libname}:{symname}"
    return s

def pin_positions(node):
    """{pinnum: (x, y)} in symbol-local coordinates."""
    out = {}
    for x in sexp.walk(node):
        if sexp.head(x) == 'pin' and len(x) > 2:
            num = sexp.val(x, 'number')
            if num is None: continue
            a = sexp.kid(x, 'at')
            out[str(num)] = (float(a[1]), float(a[2]))
    return out

def flatten(libname, symname):
    """Embedded form of a symbol, resolving (extends ...) the way KiCad does."""
    s = official(libname, symname)
    ext = sexp.val(s, 'extends')
    if not ext:
        return embedded_form(libname, symname)
    base = _clean(official(libname, ext))
    derived = _clean(s)
    out = []
    for c in base:
        if isinstance(c, list) and sexp.head(c) == 'property':
            # a property redefined by the derived symbol wins
            own = [p for p in sexp.kids(derived, 'property') if p[1] == c[1]]
            out.append(own[0] if own else c)
        elif isinstance(c, list) and sexp.head(c) == 'symbol':
            sub = list(c)
            sub[1] = str(c[1]).replace(ext, symname, 1)
            out.append(sub)
        else:
            out.append(c)
    # properties the derived symbol adds that the base lacks
    have = {p[1] for p in sexp.kids(base, 'property')}
    extra = [p for p in sexp.kids(derived, 'property') if p[1] not in have]
    if extra:
        last = max(i for i, c in enumerate(out)
                   if isinstance(c, list) and sexp.head(c) == 'property')
        out[last+1:last+1] = extra
    out = list(out)
    out[1] = f"{libname}:{symname}"
    return out
