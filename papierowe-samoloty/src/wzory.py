"""Lekkie wzory malowań wspólne dla wszystkich modeli: dużo bieli, cienkie linie i jasne plamy.
Każdy wzór rysuje się w układzie złożonego samolotu (jak `art` modelu), więc pasuje do każdego
modelu. Kolor główny (rola "main") można zmienić na stronie; neutralny beż zostaje stały."""
import math

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from paint import hx, fill, poly, line, circle, band, bez_pts, fill_geom, lines_geom, feat, Dots

WHITE = hx("#ffffff")
NEU = hx("#bdb3a2")


# ----------------------------------------------------------------------
# geometria modelu w widokach
def geo(M):
    g = M.__dict__.get("_geo")
    if g:
        return g
    from fold import apply
    from model3d import view_affine
    d = {}
    for p in M.pieces:
        if p.printed:
            d.setdefault((p.view, p.zone == "winglet"), []).append(apply(view_affine(p), p.paper))
    u = {k: unary_union(v) for k, v in d.items()}
    top = u[("top", False)]
    T, _, N, S = top.bounds
    cut = top.intersection(LineString([(T - 10, S * 0.92), (N + 10, S * 0.92)]))
    xt = cut.bounds[2] if not cut.is_empty else T
    side = u.get(("right", False))
    wl = u.get(("right", True))
    g = dict(N=N, T=T, S=S, xt=xt, top=top, side=side.bounds if side else (0, 0, N, 30),
             wl=wl.bounds if wl else None)
    M.__dict__["_geo"] = g
    return g


def halves(ctx, fn):
    """fn(s) osobno dla połówki y>0 (s=1) i y<0 (s=-1), przycięte do tej połówki."""
    for s in (1, -1):
        ctx.save()
        ctx.rectangle(-500, 0, 1000, 500 * s)
        ctx.clip()
        fn(s)
        ctx.restore()


def le_frame(g, s):
    """Krawędź natarcia: punkt na nosie, kierunek do końcówki i normalna do środka skrzydła."""
    p0 = np.array([g["N"], 0.0])
    p1 = np.array([g["xt"], g["S"] * s])
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    n = np.array([-d[1], d[0]])
    if n[0] > 0:  # do tyłu, w stronę krawędzi spływu
        n = -n
    return p0, d, n


def le_pts(g, s, off, a=-0.3, b=1.4):
    p0, d, n = le_frame(g, s)
    L = np.linalg.norm(np.array([g["xt"], g["S"]]) - np.array([g["N"], 0]))
    return [tuple(p0 + d * L * t + n * off) for t in (a, b)]


def strip(p, d, w, L=600):
    """Pas szerokości w przez punkt p w kierunku d."""
    p, d = np.array(p, float), np.array(d, float) / np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * w / 2
    return [tuple(p - d * L + n), tuple(p + d * L + n), tuple(p + d * L - n), tuple(p - d * L - n)]


def draw_lines(ctx, geom, col, lw, dash=None):
    if geom is None or geom.is_empty:
        return
    for gg in getattr(geom, "geoms", [geom]):
        if hasattr(gg, "exterior"):
            for r in [gg.exterior, *gg.interiors]:
                line(ctx, list(r.coords), col, lw=lw, dash=dash)
        elif hasattr(gg, "coords"):
            line(ctx, list(gg.coords), col, lw=lw, dash=dash)
        else:
            draw_lines(ctx, gg, col, lw, dash)


def star(ctx, x, y, r, col, n=4, inner=0.28, rot=0.0):
    pts = []
    for k in range(2 * n):
        a = rot + math.pi * k / n
        rr = r if k % 2 == 0 else r * inner
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    poly(ctx, pts, col)


def is_side(view):
    return view in ("left", "right")


def u_of(view):
    return -1 if view == "left" else 1


# ----------------------------------------------------------------------
# 01 Mapa – poziomice
def _ridges(rnd, box, n, along_x=False):
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        if along_x:
            ya = rnd.uniform(y0, y1)
            pts = [(x0 - 20, ya), (rnd.uniform(x0, x1), rnd.uniform(y0, y1)),
                   (rnd.uniform(x0, x1), rnd.uniform(y0, y1)), (x1 + 20, rnd.uniform(y0, y1))]
        else:
            c = (rnd.uniform(x0, x1), rnd.uniform(y0, y1))
            a = rnd.uniform(0, math.pi)
            L = rnd.uniform(15, 45)
            pts = [(c[0] - L * math.cos(a), c[1] - L * math.sin(a)),
                   (c[0] + rnd.uniform(-20, 20), c[1] + rnd.uniform(-20, 20)),
                   (c[0] + rnd.uniform(-20, 20), c[1] + rnd.uniform(-20, 20)),
                   (c[0] + L * math.cos(a), c[1] + L * math.sin(a))]
        out.append(LineString(bez_pts(*pts, 30)))
    return out


_MAPA = {}


def _contours(key, box, n, along_x, step, levels):
    if key in _MAPA:
        return _MAPA[key]
    rnd = np.random.default_rng(key[0])
    rid = _ridges(rnd, box, n, along_x)
    base = unary_union(rid)
    lines = [base.buffer(step * (k + 1), quad_segs=4).boundary.simplify(0.45) for k in range(levels)]
    patches = [r.buffer(step * 1.2).simplify(0.3) for r in rid]
    _MAPA[key] = (lines, patches)
    return _MAPA[key]


def mapa(self, ctx, view, piece):
    g = geo(self)
    N, T, S = g["N"], g["T"], g["S"]
    cl = self.c(0.2, alpha=0.85)
    if piece.zone == "winglet":
        b = g["wl"] or (-50, 20, 50, 70)
        lines, patches = _contours((41, "wl"), (b[0] * u_of(view), b[1], b[2] * u_of(view), b[3]), 2, True, 3.2, 4)
        lines_geom(ctx, unary_union(lines), cl, 0.3)
        return
    if is_side(view):
        sx0, _, sx1, sy1 = g["side"]
        lines, patches = _contours((31, "side"), (-sx1, 0, sx1, sy1), 3, True, 3.2, 5)
        fill_geom(ctx, patches[0], self.dots(0.22))
        lines_geom(ctx, unary_union(lines), cl, 0.3)
        return

    def half(s):
        seed = (7 if view == "top" else 13) + (s > 0)
        lines, patches = _contours((seed, view, s), (T, 0, N, S), 9, False, 3.2, 9)
        mir = (lambda x: x) if s > 0 else (lambda x: affinity.scale(x, 1, -1, origin=(0, 0)))
        if s < 0:
            lines = [mir(x) for x in lines]
            patches = [mir(x) for x in patches]
        fill_geom(ctx, patches[0], self.dots(0.36 if view == "top" else 0.24))
        fill_geom(ctx, patches[3], self.dots(0.36 if view == "top" else 0.24))
        fill_geom(ctx, patches[2], Dots(NEU, 0.35))
        lines_geom(ctx, unary_union(lines), cl, 0.3)
        # szlak
        p = le_pts(g, s, 16, 0.05, 0.9)
        line(ctx, p, self.c(0.3, alpha=0.8), lw=0.45, dash=[2.2, 1.6])
    halves(ctx, half)


# ----------------------------------------------------------------------
# 02 Nawigacja – podwójne pasy, siatka, róża wiatrów bez liter
def rose(ctx, x, y, r, col_dark, col_light):
    circle(ctx, x, y, r * 0.62, WHITE, stroke=col_light, lw=0.35)
    star(ctx, x, y, r * 0.72, col_light, n=4, inner=0.22, rot=math.pi / 4)
    star(ctx, x, y, r, col_dark, n=4, inner=0.18)
    circle(ctx, x, y, r * 0.09, WHITE)


def nawigacja(self, ctx, view, piece):
    g = geo(self)
    N, T, S = g["N"], g["T"], g["S"]
    main = self.dots(0.6 if view != "bottom" else 0.45)
    thin = self.c(0.0)
    grid = self.c(0.0, alpha=0.4)
    if piece.zone == "winglet":
        line(ctx, [(-300, 40), (300, 40)], thin, lw=1.4)
        line(ctx, [(-300, 43), (300, 43)], thin, lw=0.45)
        return
    if is_side(view):
        poly(ctx, [(-500, 4), (500, 4), (500, 6.4), (-500, 6.4)], main)
        line(ctx, [(-500, 8.2), (500, 8.2)], thin, lw=0.45)
        for x in range(-400, 400, 25):
            line(ctx, [(x, 12), (x, 30)], grid, lw=0.2, dash=[1.2, 1.2])
        return

    def half(s):
        # siatka i krzyżyki
        for x in range(int(T) // 25 * 25, int(N) + 25, 25):
            line(ctx, [(x, 4 * s), (x, (S + 10) * s)], grid, lw=0.2, dash=[1.2, 1.4])
        for y in range(25, int(S) + 25, 25):
            line(ctx, [(T - 10, y * s), (N + 10, y * s)], grid, lw=0.2, dash=[1.2, 1.4])
        for i, x in enumerate(range(int(T) // 25 * 25 + 25, int(N), 50)):
            for y in range(25, int(S), 50):
                line(ctx, [(x - 2, y * s), (x + 2, y * s)], thin, lw=0.3)
                line(ctx, [(x, y * s - 2), (x, y * s + 2)], thin, lw=0.3)
        # podwójny pas wzdłuż krawędzi natarcia i przy kadłubie
        p = le_pts(g, s, 8)
        poly(ctx, band(bez_pts(p[0], p[0], p[1], p[1], 2), 2.8), main)
        line(ctx, le_pts(g, s, 11.5), thin, lw=0.5)
        poly(ctx, [(T - 10, 3 * s), (N - 30, 3 * s), (N - 30, 5.4 * s), (T - 10, 5.4 * s)], main)
        line(ctx, [(T - 10, 7.2 * s), (N - 30, 7.2 * s)], thin, lw=0.45)
        if view == "top":
            c = self.fit("top", 24, 24, ((T + N) / 2 - 10, S * 0.45 * s))
            if c:
                rose(ctx, c[0], c[1], 10, self.c(0.1), self.c(0.0, alpha=0.5))
                feat(ctx, "roza", c[0] - 10, c[1] - 10, c[0] + 10, c[1] + 10)
    halves(ctx, half)


# ----------------------------------------------------------------------
# 03 Kliny – szerokie skośne pasy w kolorze i beżu
def kliny(self, ctx, view, piece):
    g = geo(self)
    N, T, S = g["N"], g["T"], g["S"]
    top = view != "bottom"
    m1 = self.dots(0.55 if top else 0.4)
    n1 = Dots(NEU, 0.45 if top else 0.32)
    if piece.zone == "winglet":
        b = g["wl"] or (-50, 20, 50, 70)
        u = u_of(view)
        poly(ctx, strip(((b[0] + b[2]) / 2 * u, (b[1] + b[3]) / 2), (1 * u, -1.3), 7), m1)
        return
    if is_side(view):
        u = u_of(view)
        sx1 = g["side"][2]
        poly(ctx, strip(((sx1 - 25) * u, 10), (1 * u, -1.6), 5), m1)
        poly(ctx, strip(((sx1 - 34) * u, 10), (1 * u, -1.6), 3), n1)
        return

    def half(s):
        p0, d, n = le_frame(g, s)
        L = np.linalg.norm(np.array([g["xt"], S]) - p0)
        a = math.atan2(d[1], d[0])
        q = np.array([math.cos(a - 0.85 * s), math.sin(a - 0.85 * s)])  # kierunek klina
        for t, w, col in ((0.22, 15, m1), (0.22 + 0.1, 7, n1), (0.55, 15, m1), (0.55 + 0.1, 7, n1),
                          (0.88, 9, n1)):
            poly(ctx, strip(p0 + d * L * t, q, w), col)
        poly(ctx, [(T - 10, 2 * s), (N - 20, 2 * s), (N - 20, 4.5 * s), (T - 10, 4.5 * s)], n1)
    halves(ctx, half)


# ----------------------------------------------------------------------
# 04 Fale – płynne wstęgi od kadłuba do końcówek
def fale(self, ctx, view, piece):
    g = geo(self)
    N, T, S, xt = g["N"], g["T"], g["S"], g["xt"]
    top = view != "bottom"
    fillc = self.dots(0.38 if top else 0.26)
    edge = self.c(0.15, alpha=0.75)
    if piece.zone == "winglet":
        b = g["wl"] or (-50, 20, 50, 70)
        u = u_of(view)
        pts = bez_pts((b[0] * u - 10 * u, b[3] - 4), (b[0] * u + 15 * u, b[1]), (b[2] * u - 20 * u, b[3]),
                      (b[2] * u + 10 * u, b[1] + 6), 30)
        poly(ctx, band(pts, 1.0, 5.0), fillc)
        line(ctx, pts, edge, lw=0.3)
        return
    if is_side(view):
        sx1 = g["side"][2]
        u = u_of(view)
        for k in range(2):
            pts = bez_pts((sx1 * u, 6 + k * 8), (sx1 * 0.6 * u, 1 + k * 8), (sx1 * 0.3 * u, 14 + k * 8),
                          (-20 * u, 8 + k * 8), 30)
            poly(ctx, band(pts, 4.0, 0.6), fillc)
            line(ctx, pts, edge, lw=0.3)
        return

    def half(s):
        for k in range(5):
            f = 0.12 + 0.19 * k
            x0 = N - (N - T) * f
            tipx = xt - (xt - T) * (0.15 + 0.2 * k)
            pts = bez_pts((x0 + 15, 1 * s), (x0 - 25, S * 0.35 * s), (tipx + 40, S * 0.55 * s), (tipx - 10, (S + 6) * s), 40)
            if k % 2 == 0:
                poly(ctx, band(pts, 1.5, 15.0 - 2 * k), fillc if k != 2 else Dots(NEU, 0.4))
                line(ctx, pts, edge, lw=0.3)
            else:
                line(ctx, pts, edge, lw=0.35)
    halves(ctx, half)


# ----------------------------------------------------------------------
# 05 Gwiazdozbiór – jasne tło, gwiazdy połączone liniami
def _star_poly(x, y, r, n=4, inner=0.28):
    from shapely.geometry import Polygon
    return Polygon([(x + (r if k % 2 == 0 else r * inner) * math.cos(math.pi * k / n),
                     y + (r if k % 2 == 0 else r * inner) * math.sin(math.pi * k / n)) for k in range(2 * n)])


def gwiazdy(self, ctx, view, piece):
    g = geo(self)
    N, T, S = g["N"], g["T"], g["S"]
    fill(ctx, self.dots(0.13 if view != "bottom" else 0.08))
    dark = self.c(0.35)
    ln = self.c(0.2, alpha=0.75)
    dust = self.c(0.2, alpha=0.6)
    if piece.zone == "winglet" or is_side(view):
        b = g["wl"] if piece.zone == "winglet" else g["side"]
        u = u_of(view)
        rnd = np.random.default_rng(5 if piece.zone == "winglet" else 9)
        pts = [Point(rnd.uniform(b[0], b[2]) * u, rnd.uniform(b[1], b[3])).buffer(rnd.uniform(0.25, 0.55), quad_segs=2)
               for _ in range(14)]
        fill_geom(ctx, unary_union(pts), dust)
        fill_geom(ctx, _star_poly((b[0] + b[2]) / 2 * u, (b[1] + b[3]) / 2, 2.4), dark)
        return

    def half(s):
        rnd = np.random.default_rng((3 if view == "top" else 11) + (s > 0))
        pts = [Point(rnd.uniform(T, N), rnd.uniform(3, S) * s).buffer(rnd.uniform(0.2, 0.5), quad_segs=2)
               for _ in range(int((N - T) * S / 90))]
        fill_geom(ctx, unary_union(pts), dust)
        # konstelacje: kilka łańcuchów gwiazd
        chains, stars = [], []
        for c in range(3):
            cx, cy = T + (N - T) * (0.2 + 0.3 * c), S * rnd.uniform(0.3, 0.65)
            pp = sorted((cx + rnd.uniform(-22, 22), (cy + rnd.uniform(-14, 14)) * s) for _ in range(5))
            chains.append(LineString(pp))
            stars += [_star_poly(x, y, 4.2 if i == 2 else 2.4) for i, (x, y) in enumerate(pp)]
        lines_geom(ctx, unary_union(chains), ln, 0.35)
        fill_geom(ctx, unary_union(stars), dark)
    halves(ctx, half)


# ----------------------------------------------------------------------
# 06 Pasy – podwójne prążki wzdłuż krawędzi natarcia i kokarda
def pasy(self, ctx, view, piece):
    g = geo(self)
    N, T, S = g["N"], g["T"], g["S"]
    top = view != "bottom"
    m1 = self.dots(0.6 if top else 0.45)
    n1 = Dots(hx("#8ea6c0"), 0.5 if top else 0.4)
    if piece.zone == "winglet" or is_side(view):
        y0 = 38 if piece.zone == "winglet" else 5
        poly(ctx, [(-500, y0), (500, y0), (500, y0 + 2.4), (-500, y0 + 2.4)], m1)
        poly(ctx, [(-500, y0 + 3.6), (500, y0 + 3.6), (500, y0 + 5.2), (-500, y0 + 5.2)], n1)
        return

    def half(s):
        for off, w, col in ((7, 2.4, m1), (10.4, 1.6, n1)):
            p = le_pts(g, s, off)
            poly(ctx, band(bez_pts(p[0], p[0], p[1], p[1], 2), w), col)
        for off, w, col in ((3.5, 2.4, m1), (6.6, 1.6, n1)):
            poly(ctx, [(T - 10, off * s), (N - 25, off * s), (N - 25, (off + w) * s), (T - 10, (off + w) * s)], col)
        # skośne prążki przy końcówce
        p0, d, n = le_frame(g, s)
        tip = np.array([g["xt"], S * s]) + n * 12
        for k, (w, col) in enumerate(((2.4, m1), (1.6, n1))):
            q = tip - d * (6 + 4 * k)
            poly(ctx, strip(q, n, w, L=14), col)
        if top:
            c = self.fit(view, 16, 16, ((T + N) / 2 - 20, S * 0.5 * s))
            if c:
                circle(ctx, c[0], c[1], 6.5, m1)
                circle(ctx, c[0], c[1], 4.4, WHITE)
                circle(ctx, c[0], c[1], 2.2, n1)
                feat(ctx, "kokarda", c[0] - 6.5, c[1] - 6.5, c[0] + 6.5, c[1] + 6.5)
    halves(ctx, half)


# id, nazwa na stronie, domyślny kolor, funkcja
WZORY = [
    ("mapa", "Mapa", "#7f9772", mapa),
    ("nawigacja", "Nawigacja", "#4f6f9a", nawigacja),
    ("kliny", "Kliny", "#d9705a", kliny),
    ("fale", "Fale", "#5f9a8a", fale),
    ("gwiazdy", "Gwiazdozbiór", "#7c6fb0", gwiazdy),
    ("pasy", "Pasy", "#e0902e", pasy),
]


def z_wzorem(cls, wid):
    w = next(x for x in WZORY if x[0] == wid)
    return type(cls.__name__, (cls,), {"art": w[3], "inks": {"main": w[2]}})
