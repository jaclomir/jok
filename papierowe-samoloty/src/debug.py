import sys, importlib
sys.path.insert(0, '.')
from render import *
from PIL import Image
mod, cls = sys.argv[1], sys.argv[2]
M = getattr(importlib.import_module('models.' + mod), cls)()
out = sys.argv[3]
tex = sheet_image(M, M.pieces, ppmm=M.ppmm)
tex.save(out + '_sheet.png')
imgs = [render_flat(st.state, tex, M, size=(300, 300), line=st.line) for st in M.sheet.steps]
imgs.append(render_flat(M.sheet.facets, tex, M, size=(300, 300)))
row = Image.new('RGB', (300 * len(imgs), 300), 'white')
for i, im in enumerate(imgs): row.paste(im, (300 * i, 0))
row.save(out + '_steps.png')
a = render_3d(M.pieces, tex, M, az=-130, el=28, size=(700, 450))
b = render_3d(M.pieces, tex, M, az=-60, el=-25, size=(700, 450))
c = render_3d(M.pieces, tex, M, az=-90, el=80, size=(700, 450))
d = render_3d(M.pieces, tex, M, az=180, el=10, size=(700, 450))
g = Image.new('RGB', (1400, 900), 'white')
for i, im in enumerate([a, b, c, d]): g.paste(im, (700 * (i % 2), 450 * (i // 2)))
g.save(out + '_3d.png')
vis = sum(p.paper.area for p in M.pieces if p.printed); un = sum(p.paper.area for p in M.pieces if not p.printed)
print('pieces', len(M.pieces), 'printed visible %.0f mm2, unprinted visible %.0f mm2' % (vis, un))
from collections import Counter
print(Counter((p.view, p.printed) for p in M.pieces))
