"""Mapa widoków: co widać na gotowym modelu z góry, z dołu i z boków (do projektowania malowania)."""
import sys, importlib
import numpy as np
import cairocffi as cairo
sys.path.insert(0, '.')
from fold import apply, polys
from model3d import view_affine
from render import path_poly, surface_to_pil
from shapely.ops import unary_union
from PIL import Image

def view_panel(M, view, ppmm=4, pad=6):
    ps = [p for p in M.pieces if p.view == view]
    if not ps:
        return None
    gs = [(apply(view_affine(p), p.paper), p) for p in ps]
    u = unary_union([g for g, _ in gs])
    x0, y0, x1, y1 = u.bounds
    w, h = int((x1 - x0 + 2 * pad) * ppmm), int((y1 - y0 + 2 * pad) * ppmm)
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(s)
    ctx.set_source_rgb(1, 1, 1); ctx.paint()
    ctx.scale(ppmm, -ppmm); ctx.translate(-x0 + pad, -y1 - pad)
    for g, p in sorted(gs, key=lambda t: t[1].printed):
        ctx.save(); path_poly(ctx, g); ctx.clip()
        if p.printed:
            M.art(ctx, view, p)
        else:
            ctx.set_source_rgb(0.86, 0.86, 0.88); ctx.paint()
            ctx.set_source_rgba(0.5, 0.5, 0.55, 0.6); ctx.set_line_width(0.3)
            for k in range(-200, 400, 4):
                ctx.move_to(k + x0, y0 - 50); ctx.line_to(k + x0 + 200, y0 + 150)
            ctx.stroke()
        ctx.restore()
    ctx.set_line_width(0.25); ctx.set_source_rgb(0.2, 0.2, 0.9)
    for g, p in gs:
        path_poly(ctx, g); ctx.stroke()
    ctx.set_source_rgb(0.0, 0.65, 0.2); ctx.set_line_width(0.5)
    for g in M.safe(view):
        path_poly(ctx, g); ctx.stroke()
    # siatka co 10 mm z opisem
    ctx.set_source_rgba(1, 0, 0, 0.35); ctx.set_line_width(0.15)
    for x in range(int(x0) // 10 * 10, int(x1) + 10, 10):
        ctx.move_to(x, y0 - pad); ctx.line_to(x, y1 + pad)
    for y in range(int(y0) // 10 * 10, int(y1) + 10, 10):
        ctx.move_to(x0 - pad, y); ctx.line_to(x1 + pad, y)
    ctx.stroke()
    ctx.select_font_face("DejaVu Sans"); ctx.set_font_size(2.5)
    for x in range(int(x0) // 20 * 20, int(x1) + 10, 20):
        ctx.save(); ctx.translate(x + 0.5, y0 - pad + 1); ctx.scale(1, -1); ctx.show_text(str(x)); ctx.restore()
    for y in range(int(y0) // 20 * 20, int(y1) + 10, 20):
        ctx.save(); ctx.translate(x0 - pad + 0.5, y + 0.5); ctx.scale(1, -1); ctx.show_text(str(y)); ctx.restore()
    ctx.save(); ctx.translate(x0 - pad + 1, y1 + pad - 4); ctx.scale(1, -1); ctx.set_font_size(4); ctx.set_source_rgb(0, 0, 0); ctx.show_text(view); ctx.restore()
    return surface_to_pil(s)

def panel(M):
    ims = [view_panel(M, v) for v in ("top", "bottom", "right", "left")]
    ims = [i for i in ims if i]
    W = max(i.width for i in ims); H = sum(i.height for i in ims) + 10 * len(ims)
    g = Image.new('RGB', (W, H), (240, 240, 240)); y = 0
    for i in ims:
        g.paste(i, (0, y)); y += i.height + 10
    return g

def ink(M, ppmm=2):
    """Szacunek pokrycia tuszem (TAC, 0..4) z arkusza RGB."""
    from render import sheet_image
    from PIL import ImageFilter
    im = sheet_image(M, M.pieces, ppmm=ppmm, lines=False, numbers=False)
    a = np.asarray(im).astype(float) / 255
    c, m, y = 1 - a[..., 0], 1 - a[..., 1], 1 - a[..., 2]
    k = np.minimum(np.minimum(c, m), y)
    tac = (c - k) + (m - k) + (y - k) + k
    # średnia w oknie 30 mm
    from scipy.ndimage import uniform_filter
    loc = uniform_filter(tac, size=30 * ppmm)
    return tac.mean(), loc.max(), (tac > 0.6).mean()

if __name__ == '__main__':
    out = sys.argv[1]
    for spec in sys.argv[2:]:
        mod, cls = spec.split(':')
        M = getattr(importlib.import_module('models.' + mod), cls)()
        panel(M).save(f'{out}/{mod}_views.png')
        for b in M.check_features(): print('   UCIĘTE:', b)
        mean, mx, frac = ink(M)
        print(f'{mod:9s} tusz: średnio {mean:.2f}  maks. w oknie 30 mm {mx:.2f}  pow. >60%: {100*frac:.0f}%')
