import sys, importlib
sys.path.insert(0,'.')
from fold import apply
from shapely.ops import unary_union
for spec in sys.argv[1:]:
    mod, cls = spec.split(':')
    M = getattr(importlib.import_module('models.'+mod), cls)()
    out=[]
    for i, st in enumerate(M.sheet.steps, 1):
        cs = [c for c in M.sheet.creases if c.step == i]
        if not cs: out.append(f"{i}:-"); continue
        fac = st.state
        tot = vis = 0
        for c in cs:
            # odcinek w stanie płaskim: szukamy ścianki, do której należy
            for f in fac:
                seg = c.seg.intersection(f.poly.buffer(0.05))
                if seg.length < 0.3: continue
                fl = apply(f.M, seg)
                above = [g.flat for g in fac if g.z > f.z]
                cov = unary_union(above) if above else None
                free = fl if cov is None else fl.difference(cov)
                tot += fl.length
                if f.p_up: vis += free.length
        out.append(f"{i}:{100*vis/max(tot,1e-9):.0f}%")
    print(mod, ' '.join(out))
