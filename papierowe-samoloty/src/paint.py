"""Proste narzędzia do malowania w cairo (układ y w górę, mm)."""
from __future__ import annotations

import math
import random

import cairocffi as cairo

from base import text  # noqa: F401  (re-eksport)


def hx(h, a=None):
    h = h.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else (*c, a)


def fill(ctx, col):
    ctx.set_source_rgba(*col) if len(col) == 4 else ctx.set_source_rgb(*col)
    ctx.paint()


def setc(ctx, col):
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
