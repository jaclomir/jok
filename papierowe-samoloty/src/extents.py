import sys, importlib
sys.path.insert(0,'.')
from model3d import view_affine
from fold import apply
from shapely.ops import unary_union
for spec in sys.argv[1:]:
    mod, cls = spec.split(':')
    M = getattr(importlib.import_module('models.'+mod), cls)()
    by = {}
    for p in M.pieces:
        g = apply(view_affine(p), p.paper)
        by.setdefault((p.view, p.printed), []).append(g)
    print(mod, 'steps', M.sheet.nstep)
    for k, gs in sorted(by.items()):
        u = unary_union(gs)
        print('   ', k, [round(v) for v in u.bounds], 'area', round(u.area))
