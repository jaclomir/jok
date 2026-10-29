"""Propozycje malowań: po 3 na model. Każda propozycja to funkcja art(self, ctx, view, piece)
plus kolor główny. Uruchom: python3 propozycje.py <katalog>  – zapisze arkusz porównawczy na model."""
import math
import os
import sys

from paint import (hx, fill, poly, rect, line, ellipse, circle, checker, band, bez_pts, offset_line,
                   fill_geom, splinter_camo, Dots)

WHITE = hx("#ffffff")
BLACK = hx("#23272e")

# geometria w widoku z góry: nos (x), ogon (x), półrozpiętość (y)
GEO = {"grot": (297, -8, 63), "iskra": (161, -44, 47), "albatros": (140, -6, 90),
       "jerzyk": (120, -7, 93), "sokol": (192, -5, 55), "bryza": (138, 0, 67)}


def G(self):
    return GEO[self.slug]


def side(view):
    return -1 if view == "left" else 1


def halves(ctx, fn):
    """Rysuje fn(s) osobno na każdej połówce (y>0 i y<0), przycięte do połówki."""
    for s in (1, -1):
        ctx.save()
        ctx.rectangle(-400, 0, 800, 400 * s)
        ctx.clip()
        fn(s)
        ctx.restore()


def stripes(ctx, region, angle, width, gap, col, phase=0.0):
    """Równoległe pasy pod kątem `angle` (stopnie) przycięte do geometrii shapely `region`."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    a = math.radians(angle)
    d, n = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    cx, cy = region.centroid.x, region.centroid.y
    R = 700
    out = []
    t = -R + phase
    while t < R:
        p = [(cx + n[0] * t + d[0] * e, cy + n[1] * t + d[1] * e) for e in (-R, R)]
        q = [(cx + n[0] * (t + width) + d[0] * e, cy + n[1] * (t + width) + d[1] * e) for e in (R, -R)]
        out.append(Polygon(p + q))
        t += width + gap
    fill_geom(ctx, unary_union(out).intersection(region), col)


def blobs(bbox, n, seed, levels, r):
    """Kamuflaż z obłymi plamami: komórki Woronoja z zaokrąglonymi rogami."""
    out = []
    for g in splinter_camo(bbox, n=n, seed=seed, levels=levels):
        out.append(None if g is None else g.buffer(-r).buffer(2 * r).buffer(-r))
    return out


def box(x0, y0, x1, y1):
    from shapely.geometry import box as b
    return b(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def canopy(self, ctx, x, rx, col=None):
    ellipse(ctx, x, 0, rx, 3.1, col or Dots(hx("#5aa0d8"), 0.5), stroke=WHITE, lw=0.4)
    ellipse(ctx, x + rx * 0.3, 0.9, rx * 0.35, 0.9, WHITE)


# ======================================================================
# GROT
def grot_wahadlowiec(self, ctx, view, piece):
    N, T, S = G(self)
    if view == "top":
        fill(ctx, Dots(hx("#c9ced4"), 0.06))
        for s in (1, -1):
            # czarna krawędź natarcia (osłony termiczne) i panele kafli
            poly(ctx, [(N + 5, 0), (T - 5, (S + 5) * s), (T - 5, (S - 7) * s), (N - 40, 0)], self.dots(0.55))
            for x in range(20, 260, 24):
                y = (S - 7) * (1 - x / N) * s
                line(ctx, [(x, 2 * s), (x, y)], Dots(hx("#8d97a2"), 0.5), lw=0.2)
            line(ctx, [(T, 32 * s), (60, 18 * s)], Dots(hx("#8d97a2"), 0.5), lw=0.25)
        poly(ctx, [(N - 45, -5), (N + 5, 0), (N - 45, 5)], self.dots(0.55))
        canopy(self, ctx, N - 70, 14, Dots(BLACK, 0.5))
    elif view == "bottom":
        fill(ctx, self.dots(0.42))
        for s in (1, -1):
            line(ctx, [(N, 0), (T, S * s)], WHITE, lw=1.2)
    else:
        u = side(view)
        fill(ctx, WHITE)
        rect(ctx, -400, 20, 400, 40, self.dots(0.5))
        for k in range(3):
            poly(ctx, [((N - 34 - k * 7) * u, 3), ((N - 29 - k * 7) * u, 3), ((N - 30 - k * 7) * u, 7),
                       ((N - 35 - k * 7) * u, 7)], Dots(BLACK, 0.55))


def grot_dazzle(self, ctx, view, piece):
    N, T, S = G(self)
    if view in ("top", "bottom"):
        fill(ctx, WHITE)
        cells = splinter_camo((T - 20, -S - 20, N + 20, S + 20), n=11, seed=4 if view == "top" else 8, levels=11)
        angs = [20, 75, -35, 50, -70, 5, 35, -15, 85, -50, 60]
        for k, c in enumerate(cells):
            if c is None:
                continue
            col = self.dots(0.55 if view == "top" else 0.4) if k % 3 else Dots(BLACK, 0.5)
            stripes(ctx, c, angs[k], 4 + k % 3 * 2, 5 + k % 2 * 3, col)
    else:
        fill(ctx, WHITE)
        stripes(ctx, box(-400, -10, 400, 50), 70 * side(view), 4, 6, self.dots(0.5))


def grot_wyscig(self, ctx, view, piece):
    N, T, S = G(self)
    red = hx("#d4213d")
    if view == "top":
        fill(ctx, Dots(hx("#c9ced4"), 0.1))
        for s in (1, -1):
            # dwa szerokie pasy wzdłuż kadłuba – przez obie połówki wyglądają jak pasy wyścigowe
            rect(ctx, T - 10, 3 * s, N - 30, 11 * s, self.dots(0.55))
            rect(ctx, T - 10, 14 * s, N - 80, 18 * s, self.dots(0.55))
            # szachownica na końcówkach skrzydeł
            for i in range(8):
                for j in range(4):
                    if (i + j) % 2 == 0:
                        x, y = T + i * 6, (S - 4 - j * 6) * s
                        rect(ctx, x, y, x + 6, y - 6 * s, Dots(BLACK, 0.55))
        poly(ctx, [(N - 30, -6), (N + 5, 0), (N - 30, 6)], Dots(red, 0.55))
        canopy(self, ctx, N - 60, 16)
    elif view == "bottom":
        fill(ctx, Dots(hx("#c9ced4"), 0.08))
        for s in (1, -1):
            rect(ctx, T, 6 * s, N - 30, 12 * s, self.dots(0.45))
    else:
        fill(ctx, Dots(hx("#c9ced4"), 0.1))
        rect(ctx, -400, 4, 400, 9, self.dots(0.55))
        rect(ctx, -400, 11, 400, 13, self.dots(0.55))
        u = side(view)
        poly(ctx, [((N - 30) * u, -2), ((N + 5) * u, -2), ((N + 5) * u, 40), ((N - 30) * u, 40)], Dots(red, 0.55))


# ======================================================================
# ISKRA
def iskra_arktyka(self, ctx, view, piece):
    N, T, S = G(self)
    if view in ("top", "bottom"):
        fill(ctx, WHITE)
        cov = 0.6 if view == "top" else 0.45
        rect(ctx, N - 38, -60, N + 10, 60, self.dots(cov))
        for s in (1, -1):
            rect(ctx, T - 10, 28 * s, N, 60 * s, self.dots(cov))
            line(ctx, [(T - 10, 26.5 * s), (N, 26.5 * s)], BLACK, lw=0.7)
        line(ctx, [(N - 39.5, -60), (N - 39.5, 60)], BLACK, lw=0.7)
        if view == "top":
            poly(ctx, [(N - 70, -3), (N - 38, -3.5), (N - 38, 3.5), (N - 70, 3)], Dots(BLACK, 0.5))
            canopy(self, ctx, N - 56, 13)
    else:
        u = side(view)
        fill(ctx, WHITE)
        rect(ctx, (N - 38) * u, -5, (N + 10) * u, 60, self.dots(0.6))
        rect(ctx, -60 * u, -5, 10 * u, 60, self.dots(0.6))
        rect(ctx, -400, 3, 400, 4.2, BLACK)


def iskra_jaszczurka(self, ctx, view, piece):
    N, T, S = G(self)
    tan = Dots(hx("#c8ad7c"), 0.4)
    if view == "bottom":
        fill(ctx, Dots(hx("#b9bfb5"), 0.16))
        return
    fill(ctx, tan)
    bb = (T - 20, -S - 20, N + 20, S + 20) if view == "top" else (-220, -10, 220, 60)
    lv = blobs(bb, 26, 17 if view != "right" else 19, 3, 5)
    fill_geom(ctx, lv[1], self.dots(0.45))
    fill_geom(ctx, lv[2], self.dots(0.5, k=0.45))
    if view == "top":
        canopy(self, ctx, N - 56, 13, Dots(hx("#3b4a3a"), 0.5))


def iskra_gradient(self, ctx, view, piece):
    N, T, S = G(self)
    if view == "winglet" or piece.zone == "winglet":
        fill(ctx, self.dots(0.6, k=0.4))
        return
    fill(ctx, WHITE)
    top = view == "top"
    if view in ("top", "bottom"):
        # półton: kolor gęstnieje od nosa do krawędzi spływu
        n = 14
        for i in range(n):
            x0 = T - 10 + (N - T + 10) * i / n
            x1 = T - 10 + (N - T + 10) * (i + 1) / n
            cov = 0.62 * (1 - i / n) ** 1.3 * (1 if top else 0.7)
            if cov > 0.03:
                rect(ctx, x0, -60, x1 + 0.01, 60, self.dots(cov))
        for s in (1, -1):
            line(ctx, [(N - 10, 1 * s), (T, (S - 6) * s)], WHITE, lw=1.3)
            line(ctx, [(N - 25, 1 * s), (T, (S - 14) * s)], WHITE, lw=0.5)
        if top:
            canopy(self, ctx, N - 56, 13, Dots(BLACK, 0.5))
    else:
        u = side(view)
        for i in range(10):
            x0 = (N - (N + 10) * i / 10) * u
            x1 = (N - (N + 10) * (i + 1) / 10) * u
            rect(ctx, x0, -5, x1, 60, self.dots(0.62 * (i / 10) ** 1.3))


# ======================================================================
# ALBATROS
def albatros_szybowiec(self, ctx, view, piece):
    N, T, S = G(self)
    if piece.zone == "winglet":
        fill(ctx, self.dots(0.6))
        return
    fill(ctx, WHITE)
    if view in ("top", "bottom"):
        cov = 0.6 if view == "top" else 0.45
        rect(ctx, N - 22, -100, N + 10, 100, self.dots(cov))
        for s in (1, -1):
            rect(ctx, T - 10, 68 * s, N + 10, 110 * s, self.dots(cov))
            line(ctx, [(T - 10, 64 * s), (N - 22, 64 * s)], Dots(hx("#8d97a2"), 0.6), lw=0.5)
        if view == "top":
            canopy(self, ctx, N - 40, 15, Dots(hx("#3d4a5c"), 0.5))
    else:
        u = side(view)
        rect(ctx, (N - 22) * u, -5, (N + 10) * u, 60, self.dots(0.6))
        rect(ctx, -400, 5, 400, 6, Dots(hx("#8d97a2"), 0.6))


def albatros_szachownica(self, ctx, view, piece):
    N, T, S = G(self)
    if piece.zone == "winglet":
        fill(ctx, WHITE)
        for i in range(-10, 10):
            for j in range(0, 12):
                if (i + j) % 2 == 0:
                    rect(ctx, i * 8, j * 8, i * 8 + 8, j * 8 + 8, self.dots(0.55))
        return
    fill(ctx, Dots(hx("#c9ced4"), 0.08))
    if view in ("top", "bottom"):
        cov = 0.58 if view == "top" else 0.42
        q = 10
        for s in (1, -1):
            for i in range(-1, 16):
                for j in range(0, 5):
                    if (i + j) % 2 == 0:
                        y = (S + 2 - j * q) * s
                        rect(ctx, T + i * q, y, T + (i + 1) * q, y - q * s, self.dots(cov))
            rect(ctx, T - 10, (S + 2 - 5 * q) * s, N + 10, (S + 2 - 5 * q - 1.5) * s, Dots(BLACK, 0.55))
        poly(ctx, [(N - 25, -30), (N + 10, -30), (N + 10, 30), (N - 25, 30)], self.dots(cov))
        if view == "top":
            canopy(self, ctx, N - 45, 15)
    else:
        u = side(view)
        rect(ctx, (N - 25) * u, -5, (N + 10) * u, 60, self.dots(0.58))
        rect(ctx, -400, 4, 400, 5.5, Dots(BLACK, 0.55))


def albatros_eskadra(self, ctx, view, piece):
    N, T, S = G(self)
    alu = Dots(hx("#a9b0b8"), 0.3)
    if piece.zone == "winglet":
        fill(ctx, self.dots(0.6))
        line(ctx, [(-300, 50), (300, 50)], BLACK, lw=1.5)
        return
    fill(ctx, alu)
    if view in ("top", "bottom"):
        cov = 0.6 if view == "top" else 0.45
        for s in (1, -1):
            # pasy eskadry w poprzek skrzydła, z czarnymi obwódkami
            for y0 in (38, 62):
                rect(ctx, T - 10, (y0 - 1.5) * s, N + 10, (y0 + 11.5) * s, Dots(BLACK, 0.55))
                rect(ctx, T - 10, y0 * s, N + 10, (y0 + 10) * s, self.dots(cov))
        rect(ctx, N - 18, -60, N + 10, 60, self.dots(cov))
        if view == "top":
            poly(ctx, [(N - 70, -3), (N - 18, -3.5), (N - 18, 3.5), (N - 70, 3)], Dots(BLACK, 0.5))
            canopy(self, ctx, N - 45, 15)
    else:
        u = side(view)
        rect(ctx, (N - 18) * u, -5, (N + 10) * u, 60, self.dots(0.6))
        rect(ctx, -400, 6, 400, 9, Dots(BLACK, 0.55))
        rect(ctx, -400, 6.8, 400, 8.2, self.dots(0.6))


# ======================================================================
# JERZYK
def jerzyk_retro(self, ctx, view, piece):
    N, T, S = G(self)
    if piece.zone == "winglet":
        fill(ctx, WHITE)
        for k, kk in enumerate((0.0, 0.3, 0.6)):
            rect(ctx, -300, 46 + k * 6, 300, 50.5 + k * 6, self.dots(0.6, k=kk))
        return
    fill(ctx, WHITE)
    if view in ("top", "bottom"):
        cov = 0.6 if view == "top" else 0.42
        for s in (1, -1):
            # trzy równoległe pasy w odcieniach koloru, odchodzące od nosa łukiem w stronę końcówek
            for k, kk in enumerate((0.0, 0.3, 0.6)):
                o = k * 8.5
                pts = bez_pts((N + 10, (2 + o) * s), (N - 40, (6 + o) * s), (60, (30 + o) * s), (T - 10, (60 + o) * s), 50)
                poly(ctx, band(pts, 6), self.dots(cov, k=kk))
    else:
        for k, kk in enumerate((0.0, 0.3, 0.6)):
            rect(ctx, -400, 4 + k * 4, 400, 7 + k * 4, self.dots(0.6, k=kk))


def jerzyk_anioly(self, ctx, view, piece):
    N, T, S = G(self)
    yel = hx("#f4c20d")
    if piece.zone == "winglet":
        fill(ctx, self.dots(0.55))
        line(ctx, [(-300, 52), (300, 52)], Dots(yel, 0.7), lw=2.0)
        return
    if view in ("top", "bottom"):
        top = view == "top"
        fill(ctx, self.dots(0.5 if top else 0.38))
        for s in (1, -1):
            # żółta krawędź natarcia i lamówka po końcówce
            pts = bez_pts((N + 5, 0), (N - 20, 30 * s), (70, 55 * s), (T - 10, (S - 2) * s), 40)
            poly(ctx, band(offset_line(pts, -4 * s), 5), Dots(yel, 0.7))
            line(ctx, offset_line(pts, -9.5 * s), Dots(yel, 0.7), lw=0.8)
        rect(ctx, T - 10, -1.6, N - 30, 1.6, Dots(yel, 0.7))
        if top:
            canopy(self, ctx, N - 34, 14)
    else:
        fill(ctx, self.dots(0.5))
        rect(ctx, -400, 8, 400, 10, Dots(yel, 0.7))


def jerzyk_morski(self, ctx, view, piece):
    N, T, S = G(self)
    grey = Dots(hx("#aeb5bd"), 0.28)
    if piece.zone == "winglet":
        fill(ctx, self.dots(0.6))
        for k in range(-30, 30):
            line(ctx, [(k * 6, 40), (k * 6 + 30, 80)], WHITE, lw=1.2)
        return
    fill(ctx, grey)
    if view in ("top", "bottom"):
        cov = 0.6 if view == "top" else 0.45
        for s in (1, -1):
            # kolorowe końcówki z białymi skośnymi pasami i linią kratki na granicy
            reg = box(T - 20, 66 * s, N + 20, 110 * s)
            fill_geom(ctx, reg, self.dots(cov))
            stripes(ctx, reg, 55 * s, 2.0, 8, WHITE)
            for i in range(-3, 30):
                if i % 2 == 0:
                    rect(ctx, T + i * 4, 62 * s, T + i * 4 + 4, 66 * s, Dots(BLACK, 0.55))
                else:
                    rect(ctx, T + i * 4, 62 * s, T + i * 4 + 4, 66 * s, WHITE)
        if view == "top":
            canopy(self, ctx, N - 34, 14)
            poly(ctx, [(N - 20, -4), (N + 5, 0), (N - 20, 4)], Dots(BLACK, 0.5))
    else:
        u = side(view)
        rect(ctx, -400, 3, 400, 7, self.dots(0.6))
        for i in range(0, 60):
            rect(ctx, -400 + i * 16, 7, -392 + i * 16, 9, Dots(BLACK, 0.55))


# ======================================================================
# SOKÓŁ
def sokol_blyskawica(self, ctx, view, piece):
    N, T, S = G(self)
    if piece.zone == "winglet":
        fill(ctx, self.dots(0.6))
        return
    fill(ctx, Dots(hx("#c9ced4"), 0.12))
    if view in ("top", "bottom"):
        cov = 0.6 if view == "top" else 0.45
        for s in (1, -1):
            # błyskawica od nosa przez skrzydło do końcówki
            b = [(N - 20, 3), (110, 22), (120, 26), (55, 40), (68, 44), (T - 10, S + 5)]
            o = [(x, (y + 0) * s) for x, y in b]
            pts = []
            for (x, y) in o:
                pts.append((x, y))
            poly(ctx, band(pts, 7), WHITE)
            poly(ctx, band(pts, 4.5), self.dots(cov))
        if view == "top":
            poly(ctx, [(N - 30, -4.5), (N + 5, 0), (N - 30, 4.5)], self.dots(0.6, k=0.4))
            canopy(self, ctx, N - 50, 15)
    else:
        u = side(view)
        pts = [((N - 10) * u, 5), (130 * u, 9), (125 * u, 5), (60 * u, 10)]
        poly(ctx, band(pts, 6), WHITE)
        poly(ctx, band(pts, 3.5), self.dots(0.6))


def sokol_stealth(self, ctx, view, piece):
    N, T, S = G(self)
    if piece.zone == "winglet":
        fill(ctx, self.dots(0.45, k=0.3))
        return
    base = self.dots(0.3 if view != "bottom" else 0.2)
    fill(ctx, base)
    if view in ("top", "bottom"):
        for s in (1, -1):
            # panele z ząbkowanymi krawędziami w jaśniejszym i ciemniejszym tonie
            for k, (x0, x1) in enumerate(((20, 70), (95, 140))):
                zz = [(x0 + i * 5, (12 + 3 * (i % 2)) * s) for i in range(int((x1 - x0) / 5) + 1)]
                zz2 = [(x1 - i * 5, (40 + 3 * (i % 2)) * s) for i in range(int((x1 - x0) / 5) + 1)]
                poly(ctx, zz + zz2, Dots(hx("#c9ced4"), 0.25) if k == 0 else self.dots(0.42, k=0.35))
            line(ctx, [(N - 10, 2 * s), (T, (S - 3) * s)], self.dots(0.55, k=0.5), lw=0.3)
            p = self.fit(view, 12, 12, (60, 26 * s))
            if p:
                circle(ctx, p[0], p[1], 5, self.c(0.5))
                circle(ctx, p[0], p[1], 4, base)
                circle(ctx, p[0], p[1], 2, self.c(0.5))
        if view == "top":
            canopy(self, ctx, N - 50, 15, Dots(hx("#c79a3c"), 0.5))
    else:
        u = side(view)
        zz = [((N - 20 - i * 5) * u, 8 + 2 * (i % 2)) for i in range(24)]
        poly(ctx, zz + [(-400 * u, 40), (N * u, 40)], self.dots(0.42, k=0.35))


def sokol_strzaly(self, ctx, view, piece):
    N, T, S = G(self)
    blue = hx("#1f3f8a")
    if piece.zone == "winglet":
        fill(ctx, self.dots(0.6))
        line(ctx, [(-300, 32), (300, 32)], WHITE, lw=2)
        return
    if view in ("top", "bottom"):
        top = view == "top"
        fill(ctx, self.dots(0.55) if top else WHITE)
        for s in (1, -1):
            # białe smugi od nosa łukiem przez skrzydła
            for k in range(2):
                pts = bez_pts((N - 10, (2 + k * 7) * s), (120, (5 + k * 8) * s), (70, (25 + k * 10) * s),
                              (T - 10, (40 + k * 12) * s), 40)
                poly(ctx, band(pts, 5.5 - k * 2), WHITE if top else self.dots(0.45))
                if top:
                    line(ctx, offset_line(pts, (4 - k) * s), Dots(blue, 0.6), lw=0.6)
        if top:
            canopy(self, ctx, N - 50, 15, Dots(blue, 0.5))
    else:
        fill(ctx, self.dots(0.55))
        rect(ctx, -400, 6, 400, 9, WHITE)
        rect(ctx, -400, 9.5, 400, 10.5, Dots(blue, 0.6))


# ======================================================================
# BRYZA
def bryza_gasniczy(self, ctx, view, piece):
    N, T, S = G(self)
    red = hx("#d8262f")
    if piece.zone == "winglet":
        fill(ctx, Dots(red, 0.55))
        line(ctx, [(-300, 36), (300, 36)], WHITE, lw=1.6)
        return
    if view in ("top", "bottom"):
        cov = 0.5 if view == "top" else 0.4
        fill(ctx, self.dots(cov))
        for s in (1, -1):
            rect(ctx, T - 10, 50 * s, N + 10, 90 * s, Dots(red, cov + 0.05))
            rect(ctx, T - 10, 47 * s, N + 10, 49 * s, WHITE)
        rect(ctx, T - 10, -5, N + 10, 5, WHITE)
        rect(ctx, N - 10, -60, N + 10, 60, Dots(red, cov + 0.05))
    else:
        fill(ctx, WHITE)
        rect(ctx, -400, 10, 400, 40, Dots(red, 0.5))


def bryza_inwazja(self, ctx, view, piece):
    N, T, S = G(self)
    if piece.zone == "winglet":
        fill(ctx, self.dots(0.5))
        for k in range(5):
            if k % 2 == 0:
                rect(ctx, -300, 29 + k * 3.2, 300, 32.2 + k * 3.2, WHITE)
            else:
                rect(ctx, -300, 29 + k * 3.2, 300, 32.2 + k * 3.2, Dots(BLACK, 0.55))
        return
    if view in ("top", "bottom"):
        fill(ctx, self.dots(0.45 if view == "top" else 0.12, k=0 if view == "top" else -0.0))
        for s in (1, -1):
            # pasy inwazyjne: biały-czarny-biały-czarny-biały w poprzek skrzydła
            for k in range(5):
                y0 = (26 + k * 6.5) * s
                rect(ctx, T - 10, y0, N + 10, y0 + 6.5 * s, WHITE if k % 2 == 0 else Dots(BLACK, 0.55))
        if view == "top":
            rect(ctx, N - 30, -3, N - 8, 3, Dots(BLACK, 0.5))
    else:
        fill(ctx, self.dots(0.45))
        for k in range(5):
            u = side(view)
            x0 = (N - 30 - k * 6) * u
            rect(ctx, x0, -5, x0 - 6 * u, 60, WHITE if k % 2 == 0 else Dots(BLACK, 0.55))


def bryza_zima(self, ctx, view, piece):
    N, T, S = G(self)
    if piece.zone == "winglet":
        fill(ctx, WHITE)
        lv = blobs((-120, 20, 120, 60), 14, 5, 2, 2.5)
        fill_geom(ctx, lv[1], self.dots(0.4))
        return
    fill(ctx, WHITE)
    bb = (T - 20, -S - 20, N + 20, S + 20) if view in ("top", "bottom") else (-160, -10, 160, 50)
    lv = blobs(bb, 30, 23 if view == "top" else 29, 3, 4)
    fill_geom(ctx, lv[1], self.dots(0.42 if view == "top" else 0.3))
    fill_geom(ctx, lv[2], Dots(hx("#9aa4b0"), 0.35))
    if view == "top":
        rect(ctx, N - 8, -60, N + 10, 60, self.dots(0.55, k=0.4))
        for s in (1, -1):
            rect(ctx, T - 10, (S - 6) * s, N + 10, (S + 10) * s, Dots(hx("#d4213d"), 0.5))


PROPOZYCJE = {
    "grot": [("Wahadłowiec", "#23272e", grot_wahadlowiec), ("Kamuflaż olśniewający", "#2c3e64", grot_dazzle),
             ("Wyścigowy", "#1f5fb8", grot_wyscig)],
    "iskra": [("Polarny", "#f2541b", iskra_arktyka), ("Jaszczurka", "#55703c", iskra_jaszczurka),
              ("Półton", "#7b2fbf", iskra_gradient)],
    "albatros": [("Szybowiec", "#ff4a2a", albatros_szybowiec), ("Szachownica", "#1f6fb8", albatros_szachownica),
                 ("Pasy eskadry", "#f2c200", albatros_eskadra)],
    "jerzyk": [("Lata 70.", "#ef7d1a", jerzyk_retro), ("Niebieskie anioły", "#1d2f5e", jerzyk_anioly),
               ("Morski", "#d62030", jerzyk_morski)],
    "sokol": [("Błyskawica", "#1f5fb8", sokol_blyskawica), ("Niewidzialny", "#5d6670", sokol_stealth),
              ("Czerwone strzały", "#d0202e", sokol_strzaly)],
    "bryza": [("Gaśniczy", "#f3b800", bryza_gasniczy), ("Pasy inwazyjne", "#5a6236", bryza_inwazja),
              ("Zimowy", "#6f8fb0", bryza_zima)],
}


def warianty(slug, cls):
    for i, (nazwa, kolor, fn) in enumerate(PROPOZYCJE[slug]):
        C = type(cls.__name__, (cls,), {"art": fn, "inks": {"main": kolor}, "slug": slug,
                                         "style": nazwa})
        yield i + 1, nazwa, C


if __name__ == "__main__":
    import importlib
    from PIL import Image, ImageDraw, ImageFont
    from build import MODELS
    from render import sheet_image, render_3d
    from views import ink
    out = sys.argv[1]
    only = sys.argv[2:] or None
    os.makedirs(out, exist_ok=True)
    f1 = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
    f2 = ImageFont.truetype("DejaVuSans.ttf", 22)
    for slug, cname in MODELS:
        if only and slug not in only:
            continue
        cls = getattr(importlib.import_module("models." + slug), cname)
        cols = []
        for i, nazwa, C in warianty(slug, cls):
            M = C()
            mean, mx, _ = ink(M)
            import cairocffi as cairo
            import paint
            orig = paint.Dots.pattern
            # podgląd: kropki jako gładki odcień (bez mory przy zmniejszeniu)
            paint.Dots.pattern = lambda d, ctx: cairo.SolidPattern(*[c * d.cov + 1 - d.cov for c in d.ink[:3]])
            tex = sheet_image(M, M.pieces, ppmm=M.ppmm)
            paint.Dots.pattern = orig
            a = render_3d(M.pieces, tex, M, az=-140, el=32, size=(760, 470), margin=24)
            b = render_3d(M.pieces, tex, M, az=-60, el=-30, size=(380, 235), margin=14, shadow=False)
            bad = M.check_features()
            im = Image.new("RGB", (760, 790), "white")
            d = ImageDraw.Draw(im)
            d.text((20, 14), f"{cls.name} {i}. {nazwa}", fill=(30, 30, 35), font=f1)
            im.paste(a, (0, 60))
            im.paste(b, (0, 535))
            sh = tex.resize((int(tex.width * 235 / tex.height), 235))
            im.paste(sh, (380 + (380 - sh.width) // 2, 535))
            d.text((20, 750), f"tusz: średnio {round(100 * mean)}%, lokalnie {round(100 * mx)}%"
                   + ("  · ucięte detale!" if bad else ""), fill=(110, 110, 120), font=f2)
            cols.append(im)
            print(slug, i, nazwa, round(100 * mean), round(100 * mx), bad, flush=True)
        g = Image.new("RGB", (760 * len(cols), 790), "white")
        for k, im in enumerate(cols):
            g.paste(im, (760 * k, 0))
        g.save(os.path.join(out, f"propozycje-{slug}.png"))
