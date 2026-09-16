"""Minimal, lossless-enough s-expression parser for KiCad files."""
import re

BS = chr(92)

class Sym(str):
    """A bare token (not a quoted string)."""
    __slots__ = ()

def parse(text):
    """Parse text into nested lists. Quoted strings -> str, bare tokens -> Sym."""
    i, n = 0, len(text)
    stack, cur = [], []
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c == '(':
            stack.append(cur); cur = []; i += 1
        elif c == ')':
            done = cur; cur = stack.pop(); cur.append(done); i += 1
        elif c == '"':
            j = i + 1; buf = []
            while j < n:
                if text[j] == BS:
                    buf.append(text[j:j+2]); j += 2
                elif text[j] == '"':
                    break
                else:
                    buf.append(text[j]); j += 1
            cur.append(''.join(buf)); i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in ('(', ')', chr(34)):
                j += 1
            cur.append(Sym(text[i:j])); i = j
    if len(cur) == 1:
        return cur[0]
    return cur

def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return parse(f.read())

def head(node):
    return node[0] if isinstance(node, list) and node and isinstance(node[0], Sym) else None

def kids(node, name):
    """Direct children lists whose head == name."""
    if not isinstance(node, list):
        return []
    return [c for c in node if isinstance(c, list) and head(c) == name]

def kid(node, name):
    k = kids(node, name)
    return k[0] if k else None

def val(node, name, default=None):
    """First value of the first child list named `name`."""
    k = kid(node, name)
    if k is None or len(k) < 2:
        return default
    return k[1]

def prop(sym, name, default=None):
    """Read a (property "Name" "Value") from a symbol node."""
    for p in kids(sym, 'property'):
        if len(p) >= 3 and p[1] == name:
            return p[2]
    return default

def walk(node):
    """Yield every list node, depth-first."""
    if isinstance(node, list):
        yield node
        for c in node:
            if isinstance(c, list):
                yield from walk(c)


def esc(s):
    """parse() preserves escape sequences verbatim, so text read from a file is
    already escaped; only escape characters that arrive raw from our own code."""
    BS = chr(92); Q = chr(34)
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == BS and i + 1 < len(s):
            out.append(s[i:i+2]); i += 2; continue
        out.append(BS + Q if c == Q else c); i += 1
    return "".join(out)

def dump(node, indent=1):
    """Serialise back to KiCad's tab-indented s-expression style."""
    TAB = chr(9)
    if not isinstance(node, list):
        if isinstance(node, Sym):
            return str(node)
        return chr(34) + esc(str(node)) + chr(34)
    atoms, lists = [], []
    for i, c in enumerate(node):
        if isinstance(c, list):
            lists.append(c)
        else:
            if lists:
                lists.append(c)      # keep ordering if atoms follow lists
            else:
                atoms.append(c)
    headline = "(" + " ".join(dump(a, 0) for a in atoms)
    if not lists:
        return TAB*indent + headline + ")"
    out = [TAB*indent + headline]
    for c in lists:
        if isinstance(c, list):
            out.append(dump(c, indent+1))
        else:
            out.append(TAB*(indent+1) + dump(c, 0))
    out.append(TAB*indent + ")")
    return chr(10).join(out)
