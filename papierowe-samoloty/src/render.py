"""Rysowanie arkusza do druku, schematów kroków i podglądu 3D."""
from __future__ import annotations

import io
import math

import cairocffi as cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

from fold import apply, polys
from model3d import view_affine

MM = 72 / 25.4  # pt na mm
PAPER = (250, 249, 245)  # kolor nienadrukowanej kartki w podglądach


# ----------------------------------------------------------------------
# pomocnicze rysowanie w cairo
def path_poly(ctx, g):
    for p in polys(g):
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            ctx.move_to(*pts[0])
            for q in pts[1:]:
                ctx.line_to(*q)
            ctx.close_path()


def cairo_matrix(M):
    """Macierz 3x3 (x' = M @ [x,y,1]) -> cairo.Matrix."""
    return cairo.Matrix(M[0, 0], M[1, 0], M[0, 1], M[1, 1], M[0, 2], M[1, 2])


def paper_ctx(surface, W, H, scale):
    import paint
    ctx = cairo.Context(surface)
    ctx.scale(scale, -scale)
    ctx.translate(0, -H)
    paint.PAPER_DEV[0] = ctx.get_matrix()
    return ctx


# ----------------------------------------------------------------------
def paint_sheet(ctx, model, pieces, bleed=3.0, lines=True, numbers=True):
    """Rysuje cały nadruk na kartce (współrzędne kartki, y w górę)."""
    W, H = model.W, model.H
    printed = [p for p in pieces if p.printed]
    # tło w miejscach ukrytych
    if model.hidden_fill:
        ctx.save()
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(*model.hidden_fill)
        ctx.fill()
        ctx.restore()
    # 1) spady: każdy fragment poszerzony o `bleed`, 2) fragmenty dokładnie
    sheet = Polygon([(0, 0), (W, 0), (W, H), (0, H)])
    for pass_ in ("bleed", "exact"):
        for p in sorted(printed, key=lambda p: p.paper.area):
            g = p.paper.buffer(bleed, join_style=2).intersection(sheet) if pass_ == "bleed" else p.paper.buffer(0.05)
            ctx.save()
            path_poly(ctx, g)
            ctx.clip()
            V = view_affine(p)
            ctx.transform(cairo_matrix(np.linalg.inv(V)))
            model.art(ctx, p.view, p)
            ctx.restore()
    if model.watermark:
        model.watermark(ctx)
    if lines:
        draw_creases(ctx, model, numbers)


def draw_creases(ctx, model, numbers=True):
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    for c in model.sheet.creases:
        if c.step in model.hide_steps:
            continue
        pts = list(c.seg.coords)
        if c.kind == "cut":
            ctx.new_path()
            ctx.move_to(*pts[0])
            for q in pts[1:]:
                ctx.line_to(*q)
            ctx.set_line_width(0.35)
            ctx.set_dash([0.5, 1.0])
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_source_rgba(0.05, 0.05, 0.08, 0.7)
            ctx.stroke()
            ctx.set_dash([])
            ctx.set_line_cap(cairo.LINE_CAP_BUTT)
            continue
        # podkład jasny, potem ciemne kreski
        ctx.move_to(*pts[0])
        ctx.line_to(*pts[-1])
        ctx.set_line_width(0.55)
        ctx.set_dash([])
        ctx.set_source_rgba(1, 1, 1, 0.32)
        ctx.stroke()
        ctx.move_to(*pts[0])
        ctx.line_to(*pts[-1])
        ctx.set_line_width(0.3)
        if c.kind == "valley":
            ctx.set_dash([3.0, 1.6])
        else:
            ctx.set_dash([3.0, 1.0, 0.5, 1.0])
        ctx.set_source_rgba(0.05, 0.05, 0.08, 0.5)
        ctx.stroke()
    ctx.set_dash([])
    if numbers:
        # numer kroku przy najdłuższym odcinku danego kroku
        best = {}
        for c in model.sheet.creases:
            if c.step in model.hide_steps:
                continue
            k = model.step_label.get(c.step, c.step)
            if k is None:
                continue
            if k not in best or c.seg.length > best[k].seg.length:
                best[k] = c
        for k, c in best.items():
            p = c.seg.interpolate(0.5, normalized=True)
            a, b = np.array(c.seg.coords[0]), np.array(c.seg.coords[-1])
            d = (b - a) / np.linalg.norm(b - a)
            n = np.array([-d[1], d[0]]) * 2.2
            x, y = p.x + n[0], p.y + n[1]
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(1, -1)
            ctx.new_path()
            ctx.arc(0, 0, 1.9, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.45)
            ctx.fill_preserve()
            ctx.set_source_rgba(0, 0, 0, 0.45)
            ctx.set_line_width(0.2)
            ctx.stroke()
            ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(2.4)
            t = str(k)
            xb, yb, ew, eh, _, _ = ctx.text_extents(t)
            ctx.move_to(-ew / 2 - xb, -yb / 2)
            ctx.show_text(t)
            ctx.restore()
    ctx.restore()


def sheet_image(model, pieces, ppmm=6, lines=True, numbers=True):
    W, H = model.W, model.H
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, int(W * ppmm), int(H * ppmm))
    ctx = paper_ctx(s, W, H, ppmm)
    ctx.set_source_rgb(*[c / 255 for c in PAPER])
    ctx.paint()
    paint_sheet(ctx, model, pieces, lines=lines, numbers=numbers)
    return surface_to_pil(s)


def surface_to_pil(s):
    buf = io.BytesIO()
    s.write_to_png(buf)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


# ----------------------------------------------------------------------
def warp_paste(canvas, tex, ppmm, H, M_paper_to_screen, poly_screen, shade=1.0, flat_color=None):
    """Nakłada fragment tekstury kartki na płótno przez przekształcenie afiniczne."""
    W_, H_ = canvas.size
    # piksel tekstury: tx = x*ppmm, ty = (H-y)*ppmm
    Tpx = np.array([[ppmm, 0, 0], [0, -ppmm, H * ppmm], [0, 0, 1]])
    S = M_paper_to_screen @ np.linalg.inv(Tpx)  # piksel tekstury -> ekran
    Si = np.linalg.inv(S)
    mask = Image.new("L", canvas.size, 0)
    d = ImageDraw.Draw(mask)
    for p in polys(poly_screen):
        d.polygon([tuple(q) for q in p.exterior.coords], fill=255)
    if flat_color is not None:
        layer = Image.new("RGB", canvas.size, flat_color)
    else:
        layer = tex.transform(canvas.size, Image.AFFINE,
                              data=(Si[0, 0], Si[0, 1], Si[0, 2], Si[1, 0], Si[1, 1], Si[1, 2]),
                              resample=Image.BILINEAR)
    if shade != 1.0:
        layer = Image.eval(layer, lambda v: max(0, min(255, int(v * shade))))
    canvas.paste(layer, (0, 0), mask)


def fit(bounds, size, margin):
    x0, y0, x1, y1 = bounds
    sc = min((size[0] - 2 * margin) / (x1 - x0), (size[1] - 2 * margin) / (y1 - y0))
    ox = (size[0] - (x1 - x0) * sc) / 2 - x0 * sc
    oy = (size[1] - (y1 - y0) * sc) / 2 + y1 * sc
    return np.array([[sc, 0, ox], [0, -sc, oy], [0, 0, 1]])


def render_flat(facets, tex, model, size=(520, 520), line=None, extra=(), arrow=None, view=None, margin=24,
                ss=2, cut=None):
    """Schemat stanu płaskiego: ścianki od dołu do góry, strona widoczna z góry."""
    size2 = (size[0] * ss, size[1] * ss)
    canvas = Image.new("RGB", size2, (255, 255, 255))
    allg = unary_union([f.flat for f in facets])
    bb = allg.bounds
    if view is not None:
        bb = view
    F = fit(bb, size2, margin * ss)
    outline = []
    for f in sorted(facets, key=lambda f: f.z):
        scr = apply(F, f.flat)
        if f.p_up:
            warp_paste(canvas, tex, model.ppmm, model.H, F @ f.M, scr)
        else:
            warp_paste(canvas, tex, model.ppmm, model.H, F @ f.M, scr, flat_color=PAPER)
        outline.append(scr)
    d = ImageDraw.Draw(canvas)
    for scr in outline:
        for p in polys(scr):
            d.line(list(p.exterior.coords), fill=(60, 60, 70), width=max(1, ss))
    for ln, col in ([(line, (220, 30, 40))] if line else []) + [(e, (40, 90, 220)) for e in extra]:
        a, b = np.array(ln[0], float), np.array(ln[1], float)
        L = LineString([a - (b - a) * 3, b + (b - a) * 3]).intersection(allg.buffer(4))
        for seg in getattr(L, "geoms", [L]):
            if seg.is_empty or not hasattr(seg, "coords"):
                continue
            pts = [tuple((F @ np.array([x, y, 1]))[:2]) for x, y in seg.coords]
            dashed(d, pts[0], pts[-1], col, 3 * ss, 9 * ss, 5 * ss)
    if arrow is not None:
        draw_arrow(d, F, arrow, ss)
    if cut is not None:
        edge = cut.boundary.intersection(allg.buffer(0.5))
        for seg in getattr(edge, "geoms", [edge]):
            if not hasattr(seg, "coords"):
                continue
            pts = [tuple((F @ np.array([x, y, 1]))[:2]) for x, y in seg.coords]
            for a, b in zip(pts[:-1], pts[1:]):
                dashed(d, a, b, (220, 30, 40), 3 * ss, 4 * ss, 4 * ss)
    return canvas.resize(size, Image.LANCZOS)


def dashed(d, p0, p1, col, w, on, off):
    p0, p1 = np.array(p0), np.array(p1)
    L = np.linalg.norm(p1 - p0)
    if L < 1:
        return
    u = (p1 - p0) / L
    t = 0
    while t < L:
        a = p0 + u * t
        b = p0 + u * min(L, t + on)
        d.line([tuple(a), tuple(b)], fill=col, width=w)
        t += on + off


def draw_arrow(d, F, arrow, ss):
    """Łuk ze strzałką: arrow = (p_from, p_to) we współrzędnych płaskich."""
    p0 = (F @ np.array([*arrow[0], 1]))[:2]
    p1 = (F @ np.array([*arrow[1], 1]))[:2]
    mid = (p0 + p1) / 2
    v = p1 - p0
    n = np.array([-v[1], v[0]])
    if np.linalg.norm(n) < 1:
        return
    n = n / np.linalg.norm(n) * np.linalg.norm(v) * 0.25
    pts = []
    for t in np.linspace(0, 1, 30):
        q = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * (mid + n) + t ** 2 * p1
        pts.append(tuple(q))
    col = (20, 20, 30)
    d.line(pts, fill=col, width=3 * ss)
    a, b = np.array(pts[-4]), np.array(pts[-1])
    u = (b - a) / (np.linalg.norm(b - a) + 1e-9)
    w = np.array([-u[1], u[0]])
    L = 11 * ss
    d.polygon([tuple(b), tuple(b - u * L + w * L * 0.5), tuple(b - u * L - w * L * 0.5)], fill=col)


# ----------------------------------------------------------------------
def camera(az, el):
    az, el = math.radians(az), math.radians(el)
    D = -np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])  # kierunek patrzenia
    up0 = np.array([0, 0, 1.0])
    R = np.cross(D, up0)
    R /= np.linalg.norm(R)
    U = np.cross(R, D)
    return R, U, D


def render_3d(pieces, tex, model, az=-130, el=25, size=(900, 600), ss=2, bg=(255, 255, 255), margin=30,
              shadow=True):
    R, U, D = camera(az, el)
    size2 = (size[0] * ss, size[1] * ss)
    canvas = Image.new("RGB", size2, bg)
    light = np.array([0.3, 0.5, 0.9])
    light /= np.linalg.norm(light)
    items = []
    for p in pieces:
        n = p.normal / np.linalg.norm(p.normal)
        if np.dot(n, D) > 0:  # tyłem do kamery
            continue
        P2 = np.vstack([R, U]) @ p.A[:3, [0, 1, 3]]  # kartka -> ekran (mm)
        M = np.eye(3)
        M[:2, :] = P2
        scr = apply(M, p.paper)
        c = p.paper.centroid
        c3 = p.A @ np.array([c.x, c.y, 0, 1])
        depth = np.dot(c3[:3], D) - 0.01 * p.facet.z * 0
        shade = 0.72 + 0.28 * abs(np.dot(n, light))
        items.append((depth, M, scr, p, shade))
    allg = unary_union([i[2] for i in items])
    F = fit(allg.bounds, size2, margin * ss)
    if shadow:
        # cień na „podłodze”: rzut pionowy
        sh = Image.new("L", size2, 0)
        dsh = ImageDraw.Draw(sh)
        for p in pieces:
            pts3 = [p.A @ np.array([x, y, 0, 1]) for x, y in p.paper.exterior.coords]
            pts = []
            for q in pts3:
                q = q[:3].copy()
                q[2] = -40
                s2 = F @ np.array([np.dot(R, q), np.dot(U, q), 1])
                pts.append((s2[0], s2[1] + 0))
            dsh.polygon(pts, fill=70)
        sh = sh.filter(ImageFilter.GaussianBlur(10 * ss))
        canvas.paste((185, 190, 200), (0, 0), sh)
    for depth, M, scr, p, shade in sorted(items, key=lambda t: -t[0]):
        MM_ = F @ M
        g = apply(F, scr)
        if p.printed:
            warp_paste(canvas, tex, model.ppmm, model.H, MM_, g, shade=shade)
        else:
            warp_paste(canvas, tex, model.ppmm, model.H, MM_, g, shade=shade, flat_color=PAPER)
    d = ImageDraw.Draw(canvas)
    for depth, M, scr, p, shade in sorted(items, key=lambda t: -t[0]):
        for q in polys(apply(F, scr)):
            d.line(list(q.exterior.coords), fill=(90, 90, 100), width=1)
    return canvas.resize(size, Image.LANCZOS)
