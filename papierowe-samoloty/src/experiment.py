import sys, importlib
sys.path.insert(0,'.')
for spec in sys.argv[1:]:
    mod, cls = spec.split(':')
    C = getattr(importlib.import_module('models.'+mod), cls)
    for pu in (False, True):
        for hf in (False, True):
            K = type('K',(C,),{'printed_up':pu,'half_flip':hf})
            try:
                M = K()
            except Exception as e:
                print(mod, pu, hf, 'ERR', e); continue
            agg = {}
            for p in M.pieces:
                agg.setdefault(p.view,[0,0])[0 if p.printed else 1] += p.paper.area
            score = sum(agg.get(v,[0,0])[0]*w for v,w in (('top',2),('left',1.5),('right',1.5),('bottom',1)))
            tot = sum(sum(v) for v in agg.values())
            print(f"{mod:9s} printed_up={pu!s:5} half_flip={hf!s:5} " + ' '.join(f"{v}:{a[0]/1000:.1f}/{a[1]/1000:.1f}" for v,a in sorted(agg.items())) + f"  score={score/1000:.0f} P%={100*sum(a[0] for a in agg.values())/tot:.0f}")
