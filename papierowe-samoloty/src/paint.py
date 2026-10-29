"""Proste narzędzia do malowania w cairo (układ y w górę, mm)."""
from __future__ import annotations

import math
import random

import cairocffi as cairo

from shapely.geometry import Polygon

REC = []  # zarejestrowane detale: (widok, nazwa, wielokąt we współrzędnych widoku)
REC_ON = [False]
REC_VIEW = [None]


def feat(ctx, name, x0, y0, x1, y1):
    """Rejestruje detal (prostokąt w bieżącym układzie) do sprawdzenia, czy nie jest ucięty."""
    if not REC_ON[0]:
        return
    M = ctx.get_matrix()
    pts = [M.transform_point(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    REC.append((REC_VIEW[0], name, Polygon(pts)))


from base import text  # noqa: E402,F401  (re-eksport)


PAPER_DEV = [None]  # cairo.Matrix kartka(mm) -> urządzenie, ustawiane przez render.paper_ctx
DOT_PITCH = 1.0  # mm, odstęp kropek w rastrze


def mix(rgb, k):
    """Przyciemnia kolor: k=0 bez zmian, k=1 czerń."""
    return tuple(c * (1 - k) for c in rgb)


def to_hex(rgb):
    return "#" + "".join("%02x" % max(0, min(255, round(c * 255))) for c in rgb[:3])


class Ink(tuple):
    """Kolor przypisany do roli (np. 'main'), który użytkownik może zmienić. k – przyciemnienie."""

    def __new__(cls, rgb, role=None, k=0.0, alpha=None):
        t = tuple(mix(rgb, k)) + ((alpha,) if alpha is not None else ())
        o = super().__new__(cls, t)
        o.role, o.k = role, k
        return o

    def spec(self):
        if self.role:
            return {"r": self.role, "k": round(self.k, 3)}
        return {"h": to_hex(self)}


class Dots:
    """Raster kolorowych kropek: z daleka wygląda jak jasny odcień koloru, a zużywa mało tuszu."""

    def __init__(self, ink, cov):
        self.ink = ink if isinstance(ink, Ink) else Ink(tuple(ink[:3]))
        self.cov = cov

    def spec(self):
        s = dict(self.ink.spec())
        s["d"] = round(self.cov, 3)
        return s

    def radius(self, pitch=None):
        p = pitch or DOT_PITCH
        # siatka heksagonalna: na komórkę p * p*sqrt(3)/2 przypada jedna kropka
        return math.sqrt(self.cov * p * p * math.sqrt(3) / 2 / math.pi)

    def pattern(self, ctx):
        p = DOT_PITCH
        h = p * math.sqrt(3) / 2
        r = self.radius()
        tile = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, (0, 0, p, 2 * h))
        t = cairo.Context(tile)
        t.set_source_rgb(*self.ink[:3])
        for x, y in ((p / 2, h / 2), (0, 1.5 * h), (p, 1.5 * h)):
            t.arc(x, y, r, 0, 2 * math.pi)
            t.close_path()
        t.fill()
        pat = cairo.SurfacePattern(tile)
        pat.set_extend(cairo.EXTEND_REPEAT)
        m = ctx.get_matrix()
        if PAPER_DEV[0] is not None:
            inv = cairo.Matrix(*PAPER_DEV[0].as_tuple())
            inv.invert()
            m = m.multiply(inv)
        pat.set_matrix(m)
        return pat


def hx(h, a=None):
    h = h.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else (*c, a)


def fill(ctx, col):
    setc(ctx, col)
    ctx.paint()


def setc(ctx, col):
    if hasattr(ctx, "set_source_spec"):
        ctx.set_source_spec(col)
        return
    if isinstance(col, Dots):
        ctx.set_source(col.pattern(ctx))
        return
    ctx.set_source_rgba(*col) if len(col) == 4 else ctx.set_source_rgb(*col)


def poly(ctx, pts, col, stroke=None, lw=0.4):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    setc(ctx, col)
    if stroke:
        ctx.fill_preserve()
        setc(ctx, stroke)
        ctx.set_line_width(lw)
        ctx.stroke()
    else:
        ctx.fill()


def rect(ctx, x0, y0, x1, y1, col):
    poly(ctx, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col)


def circle(ctx, x, y, r, col, stroke=None, lw=0.4):
    ctx.new_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    setc(ctx, col)
    if stroke:
        ctx.fill_preserve()
        setc(ctx, stroke)
        ctx.set_line_width(lw)
        ctx.stroke()
    else:
        ctx.fill()


def ellipse(ctx, x, y, rx, ry, col, rot=0.0, stroke=None, lw=0.4):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(rot))
    ctx.scale(rx, ry)
    ctx.new_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    setc(ctx, col)
    if stroke:
        ctx.fill_preserve()
        setc(ctx, stroke)
        ctx.set_line_width(lw)
        ctx.stroke()
    else:
        ctx.fill()


def line(ctx, pts, col, lw=0.4, dash=None, cap=cairo.LINE_CAP_ROUND):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    setc(ctx, col)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cap)
    ctx.set_dash(dash or [])
    ctx.stroke()
    ctx.set_dash([])


def curve(ctx, p0, c1, c2, p1, col, lw=0.4):
    ctx.new_path()
    ctx.move_to(*p0)
    ctx.curve_to(*c1, *c2, *p1)
    setc(ctx, col)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def lgrad(ctx, x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for t, col in stops:
        g.add_color_stop_rgba(t, *(col if len(col) == 4 else (*col, 1)))
    return g


def rgrad(ctx, x, y, r0, r1, stops):
    g = cairo.RadialGradient(x, y, r0, x, y, r1)
    for t, col in stops:
        g.add_color_stop_rgba(t, *(col if len(col) == 4 else (*col, 1)))
    return g


def paint_src(ctx, src):
    ctx.set_source(src)
    ctx.paint()


def checker(ctx, x, y, s, rot=0.0, border=0.6):
    """Biało-czerwona szachownica 2x2 o boku s, środek (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(rot))
    h = s / 2
    feat(ctx, "szachownica", -h - border, -h - border, h + border, h + border)
    w = hx("#ffffff")
    r = hx("#d4213d")
    rect(ctx, -h - border, -h - border, h + border, h + border, hx("#ffffff"))
    rect(ctx, -h, 0, 0, h, r)
    rect(ctx, 0, 0, h, h, w)
    rect(ctx, -h, -h, 0, 0, w)
    rect(ctx, 0, -h, h, 0, r)
    ctx.set_source_rgb(*hx("#8a1426"))
    ctx.set_line_width(0.3)
    ctx.rectangle(-h, -h, s, s)
    ctx.stroke()
    ctx.restore()


def splinter(ctx, x0, y0, x1, y1, cols, n=14, seed=1):
    """Kamuflaż z ostrych wielokątów."""
    rnd = random.Random(seed)
    for i in range(n):
        cx = rnd.uniform(x0, x1)
        cy = rnd.uniform(y0, y1)
        r = rnd.uniform(18, 45)
        k = rnd.randint(4, 6)
        a0 = rnd.uniform(0, math.pi)
        pts = []
        for j in range(k):
            a = a0 + j * 2 * math.pi / k + rnd.uniform(-0.3, 0.3)
            rr = r * rnd.uniform(0.5, 1.1)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.7))
        poly(ctx, pts, cols[i % len(cols)])


def mirror_y(ctx, fn):
    """Rysuje fn dwukrotnie: normalnie i odbite względem osi v=0."""
    fn(1)
    ctx.save()
    ctx.scale(1, -1)
    fn(-1)
    ctx.restore()


def bez_pts(p0, c1, c2, p1, n=40):
    """Punkty krzywej Béziera trzeciego stopnia."""
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        out.append((a * p0[0] + b * c1[0] + c * c2[0] + d * p1[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p1[1]))
    return out


def band(pts, w0, w1=None, off=0.0):
    """Wielokąt pasa wzdłuż łamanej `pts`: szerokość zmienia się od w0 do w1, `off` przesuwa go w bok."""
    w1 = w0 if w1 is None else w1
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2
        left.append((x + nx * (off + w), y + ny * (off + w)))
        right.append((x + nx * (off - w), y + ny * (off - w)))
    return left + right[::-1]


def offset_line(pts, off):
    out = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        out.append((x - dy / L * off, y + dx / L * off))
    return out


_CAMO = {}


def digital_camo(bbox, cell=3.0, seed=1, fracs=(0.42, 0.22, 0.14, 0.08), scale=7.0):
    """Cyfrowy kamuflaż: piksele `cell` mm pogrupowane w plamy (szum o skali `scale` komórek).
    Zwraca listę wielokątów dla kolejnych poziomów (od najjaśniejszego), każdy poziom to
    sklejone komórki, żeby rysować kilka kształtów zamiast tysięcy kwadratów."""
    import numpy as np
    from shapely.geometry import box
    from shapely.ops import unary_union
    key = (tuple(round(v, 1) for v in bbox), cell, seed, fracs, scale)
    if key in _CAMO:
        return _CAMO[key]
    x0, y0, x1, y1 = bbox
    nx, ny = int((x1 - x0) / cell) + 2, int((y1 - y0) / cell) + 2
    rnd = np.random.default_rng(seed)
    # gładki szum: losowa siatka zgrubna, interpolowana dwuliniowo, plus drobny szum na brzegach plam
    def smooth(sc):
        gx, gy = int(nx / sc) + 3, int(ny / sc) + 3
        g = rnd.random((gy, gx))
        xs = np.arange(nx) / sc
        ys = np.arange(ny) / sc
        xi, yi = np.floor(xs).astype(int), np.floor(ys).astype(int)
        fx, fy = xs - xi, ys - yi
        a = g[yi][:, xi]
        b = g[yi][:, xi + 1]
        c = g[yi + 1][:, xi]
        d = g[yi + 1][:, xi + 1]
        fx, fy = fx[None, :], fy[:, None]
        return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy
    out = []
    for lvl, frac in enumerate(fracs):
        v = 0.65 * smooth(scale) + 0.25 * smooth(scale / 2.5) + 0.10 * rnd.random((ny, nx))
        thr = np.quantile(v, 1 - frac)
        cells = [box(x0 + i * cell, y0 + j * cell, x0 + (i + 1) * cell, y0 + (j + 1) * cell)
                 for j in range(ny) for i in range(nx) if v[j, i] >= thr]
        out.append(unary_union(cells) if cells else None)
    _CAMO[key] = out
    return out


def fill_geom(ctx, g, col):
    """Wypełnia geometrię shapely (wielokąty z dziurami)."""
    if g is None or g.is_empty:
        return
    from shapely.geometry.polygon import orient
    ctx.new_path()
    geoms = getattr(g, "geoms", [g])
    for p in geoms:
        if not hasattr(p, "exterior"):
            continue
        p = orient(p, 1.0)  # dziury w przeciwnym kierunku – wypełnienie „nonzero” je zostawia
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            ctx.move_to(*pts[0])
            for q in pts[1:]:
                ctx.line_to(*q)
            ctx.close_path()
    setc(ctx, col)
    ctx.fill()
