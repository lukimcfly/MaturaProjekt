"""Reference-based editor for a flat .kicad_sch (preserves CRLF)."""
import re, sys

class Sch:
    def __init__(self, path):
        with open(path, 'r', encoding='utf-8', newline='') as f:
            self.txt = f.read()
        self.nl = '\r\n' if '\r\n' in self.txt else '\n'
        self.lines = self.txt.split(self.nl)

    def _blocks(self):
        """Yield (start, end, ref) for each top-level (symbol ... ) instance."""
        out = []
        i = 0
        while i < len(self.lines):
            if self.lines[i] == '\t(symbol':
                depth = 0; j = i
                while j < len(self.lines):
                    depth += self.lines[j].count('(') - self.lines[j].count(')')
                    if depth == 0 and j > i: break
                    j += 1
                ref = None
                for k in range(i, j+1):
                    m = re.search(r'\(property "Reference" "([^"]*)"', self.lines[k])
                    if m: ref = m.group(1); break
                out.append((i, j, ref))
                i = j + 1
            else:
                i += 1
        return out

    def set_value(self, ref, newval):
        old = None; n = 0
        for a, b, r in self._blocks():
            if r != ref: continue
            for k in range(a, b+1):
                if '(property "Value" "' in self.lines[k]:
                    old = re.search(r'\(property "Value" "([^"]*)"', self.lines[k]).group(1)
                    self.lines[k] = re.sub(r'(\(property "Value" ")[^"]*(")', r'\g<1>'+newval+r'\g<2>', self.lines[k])
                    n += 1
                    break
        if not n: raise KeyError(f"Value not set for {ref}")
        return old, n

    def set_libid(self, ref, newlib):
        old = None; n = 0
        for a, b, r in self._blocks():
            if r != ref: continue
            for k in range(a, b+1):
                if '(lib_id "' in self.lines[k]:
                    old = re.search(r'\(lib_id "([^"]*)"', self.lines[k]).group(1)
                    self.lines[k] = re.sub(r'(\(lib_id ")[^"]*(")', r'\g<1>'+newlib+r'\g<2>', self.lines[k])
                    n += 1
                    break
        if not n: raise KeyError(f"lib_id not set for {ref}")
        return old, n

    def dup_libsymbol(self, srcname, dstname):
        """Duplicate a (symbol "Lib:Name" ...) definition inside lib_symbols."""
        start = None
        for i, l in enumerate(self.lines):
            if l.strip().startswith(f'(symbol "{srcname}"'):
                start = i; break
        if start is None: raise KeyError(srcname)
        depth = 0; j = start
        while j < len(self.lines):
            depth += self.lines[j].count('(') - self.lines[j].count(')')
            if depth == 0 and j > start: break
            j += 1
        blk = self.lines[start:j+1]
        short_src = srcname.split(':')[1]; short_dst = dstname.split(':')[1]
        new = []
        for l in blk:
            l = l.replace(f'(symbol "{srcname}"', f'(symbol "{dstname}"')
            l = l.replace(f'(symbol "{short_src}_', f'(symbol "{short_dst}_')
            l = re.sub(r'(\(property "Value" ")'+re.escape(short_src)+r'(")', r'\g<1>'+short_dst+r'\g<2>', l)
            new.append(l)
        self.lines[start:start] = new
        return len(new)

    def move_symbol(self, ref, nx, ny):
        """Move a symbol (and all its property anchors) so its (at) becomes (nx, ny)."""
        for a, b, r in self._blocks():
            if r != ref: continue
            m = None
            for k in range(a, b+1):
                m = re.match(r'		\(at ([-\d.]+) ([-\d.]+)( [-\d.]+)?\)$', self.lines[k])
                if m: break
            if not m: raise KeyError(f"no (at) in {ref}")
            ox, oy = float(m.group(1)), float(m.group(2))
            dx, dy = nx - ox, ny - oy
            for k in range(a, b+1):
                mm = re.match(r'(\s*\(at )([-\d.]+) ([-\d.]+)(.*)$', self.lines[k])
                if mm:
                    self.lines[k] = f"{mm.group(1)}{round(float(mm.group(2))+dx,4)} {round(float(mm.group(3))+dy,4)}{mm.group(4)}"
            return (ox, oy), (nx, ny)
        raise KeyError(ref)

    def del_zero_wires(self):
        n = 0
        for a, b, w0, w1 in reversed(self.wires()):
            if abs(w0[0]-w1[0]) < 1e-6 and abs(w0[1]-w1[1]) < 1e-6:
                del self.lines[a:b+1]; n += 1
        return n

    def set_prop(self, ref, prop, value):
        """Set a (property "<prop>" "<value>") on every unit of a symbol."""
        n = 0
        for a, b, r in self._blocks():
            if r != ref: continue
            for k in range(a, b+1):
                if f'(property "{prop}" "' in self.lines[k]:
                    self.lines[k] = re.sub(r'(\(property "' + re.escape(prop) + r'" ")[^"]*(")',
                                           lambda m: m.group(1) + value + m.group(2), self.lines[k])
                    n += 1
                    break
        if not n: raise KeyError(f"{prop} not found on {ref}")
        return n

    def set_attr(self, ref, attr, value):
        """Set a bare attribute such as (on_board no) / (in_bom yes)."""
        n = 0
        for a, b, r in self._blocks():
            if r != ref: continue
            for k in range(a, b+1):
                m = re.match(r'(\s*)\(' + re.escape(attr) + r' (\w+)\)$', self.lines[k])
                if m:
                    self.lines[k] = f"{m.group(1)}({attr} {value})"
                    n += 1
                    break
        if not n: raise KeyError(f"{attr} not found on {ref}")
        return n

    def refs(self):
        return [r for _, _, r in self._blocks() if r]

    def save(self, path):
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(self.nl.join(self.lines))

    def wires(self):
        """Yield (start,end,(x1,y1),(x2,y2)) for each top-level wire."""
        out=[]; i=0
        while i < len(self.lines):
            if self.lines[i] == '\t(wire':
                depth=0; j=i
                while j < len(self.lines):
                    depth += self.lines[j].count('(') - self.lines[j].count(')')
                    if depth==0 and j>i: break
                    j += 1
                pts=[]
                for k in range(i,j+1):
                    m=re.search(r'\(xy ([-\d.]+) ([-\d.]+)\)', self.lines[k])
                    if m: pts.append((float(m.group(1)), float(m.group(2))))
                out.append((i,j,pts[0],pts[1]))
                i=j+1
            else: i+=1
        return out

    def del_wire(self, p, q, tol=0.01):
        """Delete the wire joining points p and q (either order)."""
        for a,b,w0,w1 in self.wires():
            same = (abs(w0[0]-p[0])<tol and abs(w0[1]-p[1])<tol and abs(w1[0]-q[0])<tol and abs(w1[1]-q[1])<tol) or \
                   (abs(w0[0]-q[0])<tol and abs(w0[1]-q[1])<tol and abs(w1[0]-p[0])<tol and abs(w1[1]-p[1])<tol)
            if same:
                del self.lines[a:b+1]
                return True
        raise KeyError(f"no wire {p}-{q}")

    def append_raw(self, text):
        """Insert raw top-level s-expr lines before (sheet_instances)."""
        for i,l in enumerate(self.lines):
            if l == '\t(sheet_instances':
                new = text.split('\n') if isinstance(text,str) else text
                self.lines[i:i] = [x.rstrip('\r') for x in new if x != '']
                return i
        raise KeyError('sheet_instances not found')

    def insert_libsymbol(self, text):
        """Insert a lib_symbol definition at the start of lib_symbols."""
        for i,l in enumerate(self.lines):
            if l == '\t(lib_symbols':
                new = text.split('\n') if isinstance(text,str) else text
                self.lines[i+1:i+1] = [x.rstrip('\r') for x in new if x != '']
                return i
        raise KeyError('lib_symbols not found')
