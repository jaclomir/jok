"""Eksport modeli do danych dla strony: arkusz jako lista operacji wektorowych z kolorami-rolami,
sceny 3D i schematy kroków (współrzędne gotowe do narysowania w przeglądarce).

Kolor główny modelu jest w operacjach zapisany jako rola ("r": "main", "k": przyciemnienie),
więc przeglądarka może go podmienić i złożyć PDF w dowolnym kolorze.
"""
from __future__ import annotations

import math

import cairocffi as cairo
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union

import paint
from fold import apply, halfplane, polys, reflection
from render import MM, camera, fit, paint_sheet

R1 = lambda v: round(float(v), 1)  # noqa: E731
R2 = lambda v: round(float(v), 2)  # noqa: E731


class Rec:
    """Udaje kontekst cairo i zapisuje to, co zostałoby narysowane, w punktach PDF (y w dół)."""

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.surf = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        self.c = cairo.Context(self.surf)
        self.c.scale(MM, -MM)
        self.c.translate(0, -H)
        paint.PAPER_DEV[0] = self.c.get_matrix()
        self.ops = []
        self.src, self.alpha = {"h": "#000000"}, 1.0
        self.stack = []
        self.page = (0, 0, W * MM, H * MM)
        self.clipbox = [self.page]

    def __getattr__(self, name):
        return getattr(self.c, name)

    # stan ---------------------------------------------------------------
    def save(self):
        self.c.save()
        self.stack.append((self.src, self.alpha))
        self.clipbox.append(self.clipbox[-1])
        self.ops.append(["q"])

    def restore(self):
        self.c.restore()
        self.src, self.alpha = self.stack.pop()
        self.clipbox.pop()
        if self.ops and self.ops[-1] == ["q"]:
            self.ops.pop()  # pusta para q/Q
        else:
            self.ops.append(["Q"])

    def set_source_rgb(self, r, g, b):
        self.src, self.alpha = {"h": paint.to_hex((r, g, b))}, 1.0

    def set_source_rgba(self, r, g, b, a=1.0):
        self.src, self.alpha = {"h": paint.to_hex((r, g, b))}, float(a)

    def set_source_spec(self, col):
        if isinstance(col, paint.Dots):
            self.src, self.alpha = col.spec(), 1.0
        elif isinstance(col, paint.Ink):
            self.src = col.spec()
            self.alpha = float(col[3]) if len(col) == 4 else 1.0
        else:
            self.src = {"h": paint.to_hex(col)}
            self.alpha = float(col[3]) if len(col) == 4 else 1.0

    def set_source(self, pattern):
        raise NotImplementedError("gradienty i wzory cairo nie są eksportowane – użyj paint.Dots")

    # ścieżki ------------------------------------------------------------
    def _dev_path(self):
        self.c.save()
        self.c.identity_matrix()
        path = self.c.copy_path()
        ext = self.c.path_extents()
        self.c.restore()
        out = []
        for kind, pts in path:
            if kind == cairo.PATH_MOVE_TO:
                out.append("M%s %s" % (R1(pts[0]), R1(pts[1])))
            elif kind == cairo.PATH_LINE_TO:
                out.append("L%s %s" % (R1(pts[0]), R1(pts[1])))
            elif kind == cairo.PATH_CURVE_TO:
                out.append("C%s %s %s %s %s %s" % tuple(R1(v) for v in pts))
            elif kind == cairo.PATH_CLOSE_PATH:
                out.append("Z")
        return "".join(out), ext

    def _visible(self, ext, pad=0.0):
        x0, y0, x1, y1 = ext
        cx0, cy0, cx1, cy1 = self.clipbox[-1]
        return not (x1 + pad < cx0 or x0 - pad > cx1 or y1 + pad < cy0 or y0 - pad > cy1)

    def _box(self, ext):
        x0, y0, x1, y1 = ext
        cx0, cy0, cx1, cy1 = self.clipbox[-1]
        return [R1(max(x0, cx0)), R1(max(y0, cy0)), R1(min(x1, cx1)), R1(min(y1, cy1))]

    def clip(self):
        d, ext = self._dev_path()
        self.c.clip()
        cb = self.clipbox[-1]
        self.clipbox[-1] = (max(cb[0], ext[0]), max(cb[1], ext[1]), min(cb[2], ext[2]), min(cb[3], ext[3]))
        self.ops.append(["W", d])

    def _fill(self, d, ext):
        if not d or not self._visible(ext):
            return
        if "d" in self.src:
            self.ops.append(["dots", d, self.src, self._box(ext)])
        else:
            self.ops.append(["f", d, self.src, R2(self.alpha)])

    def fill(self):
        d, ext = self._dev_path()
        self.c.new_path()
        self._fill(d, ext)

    def fill_preserve(self):
        d, ext = self._dev_path()
        self._fill(d, ext)

    def paint(self):
        self._fill("PAGE", self.clipbox[-1])

    def stroke(self):
        d, ext = self._dev_path()
        lw = self.c.get_line_width()
        sx, sy = self.c.user_to_device_distance(lw, 0)
        w = math.hypot(sx, sy)
        dash, _ = self.c.get_dash()
        sc = w / lw if lw else 1
        self.c.new_path()
        if not d or not self._visible(ext, w):
            return
        cap = {cairo.LINE_CAP_BUTT: 0, cairo.LINE_CAP_ROUND: 1, cairo.LINE_CAP_SQUARE: 2}[self.c.get_line_cap()]
        self.ops.append(["s", d, self.src, R2(self.alpha), R2(w), [R2(v * sc) for v in dash], cap])

    def show_text(self, t):
        self.c.text_path(t)
        self.fill()


# ----------------------------------------------------------------------
def sheet_ops(M):
    rec = Rec(M.W, M.H)
    paint_sheet(rec, M, M.pieces)
    paint.PAPER_DEV[0] = None
    # sklej sąsiednie Q q (nie zmieniają stanu tylko przy pustych parach – zostawiamy jak jest)
    return rec.ops


def _aff(Mx):
    """Macierz 3x3 -> [a, b, c, d, e, f] w konwencji canvas (x' = a x + c y + e)."""
    return [R2(Mx[0, 0]), R2(Mx[1, 0]), R2(Mx[0, 1]), R2(Mx[1, 1]), R2(Mx[0, 2]), R2(Mx[1, 2])]


def _poly(g):
    return [[R1(x), R1(y)] for p in polys(g) for x, y in list(p.exterior.coords)[:-1]] if not g.is_empty else []


def scene_3d(M, az, el, size, margin=24):
    R, U, D = camera(az, el)
    light = np.array([0.3, 0.5, 0.9])
    light /= np.linalg.norm(light)
    items = []
    for p in M.pieces:
        n = p.normal / np.linalg.norm(p.normal)
        if np.dot(n, D) > 0:
            continue
        P2 = np.vstack([R, U]) @ p.A[:3, [0, 1, 3]]
        Mx = np.eye(3)
        Mx[:2, :] = P2
        scr = apply(Mx, p.paper)
        c = p.paper.centroid
        c3 = p.A @ np.array([c.x, c.y, 0, 1])
        items.append((np.dot(c3[:3], D), Mx, scr, p, 0.72 + 0.28 * abs(np.dot(n, light))))
    allg = unary_union([i[2] for i in items])
    F = fit(allg.bounds, size, margin)
    out = []
    for depth, Mx, scr, p, shade in sorted(items, key=lambda t: -t[0]):
        for g in polys(apply(F, scr)):
            out.append({"p": _poly(g), "m": _aff(F @ Mx), "pr": bool(p.printed), "sh": R2(shade)})
    return {"w": size[0], "h": size[1], "items": out}


def scene_flat(M, facets, size, line=None, extra=(), arrow=None, cut=None, margin=16):
    allg = unary_union([f.flat for f in facets])
    F = fit(allg.bounds, size, margin)
    items = [{"p": _poly(apply(F, f.flat)), "m": _aff(F @ f.M), "pr": bool(f.p_up)}
             for f in sorted(facets, key=lambda f: f.z)]
    lines = []
    for ln, col in ([(line, "r")] if line else []) + [(e, "b") for e in extra]:
        a, b = np.array(ln[0], float), np.array(ln[1], float)
        L = LineString([a - (b - a) * 3, b + (b - a) * 3]).intersection(allg.buffer(4))
        for seg in getattr(L, "geoms", [L]):
            if seg.is_empty or not hasattr(seg, "coords"):
                continue
            pts = [(F @ np.array([x, y, 1]))[:2] for x, y in seg.coords]
            lines.append([R1(pts[0][0]), R1(pts[0][1]), R1(pts[-1][0]), R1(pts[-1][1]), col])
    sc = {"w": size[0], "h": size[1], "items": items, "lines": lines}
    if arrow is not None:
        p0 = (F @ np.array([*arrow[0], 1]))[:2]
        p1 = (F @ np.array([*arrow[1], 1]))[:2]
        sc["arrow"] = [R1(p0[0]), R1(p0[1]), R1(p1[0]), R1(p1[1])]
    if cut is not None:
        edge = cut.boundary.intersection(allg.buffer(0.5))
        segs = []
        for seg in getattr(edge, "geoms", [edge]):
            if hasattr(seg, "coords"):
                segs.append([[R1(q[0]), R1(q[1])] for q in ((F @ np.array([x, y, 1]))[:2] for x, y in seg.coords)])
        sc["cut"] = segs
    return sc


def steps_data(M, size=(300, 300)):
    out = []
    for i, st in enumerate(M.sheet.steps, 1):
        if st.flip:
            sc = scene_flat(M, st.state, size)
            sc["flip"] = True
        elif st.line is None:
            sc = scene_flat(M, st.state, size, cut=st.extra[0])
        else:
            arrow = None
            allg = unary_union([f.flat for f in st.state])
            mv = allg.intersection(halfplane(st.line[0], st.line[1], st.move))
            if not mv.is_empty and mv.area > 1:
                c = mv.representative_point()
                Rf = reflection(st.line[0], st.line[1])
                c2 = Rf @ np.array([c.x, c.y, 1])
                arrow = ((c.x, c.y), (c2[0], c2[1]))
            sc = scene_flat(M, st.state, size, line=st.line, arrow=arrow)
        out.append({"n": i, "t": st.text, "s": sc})
    hs = M.plane.hinges
    for n, txt, hi in M.final_steps:
        if hi is not None:
            h = hs[hi]
            sc = scene_flat(M, M.sheet.facets, size, line=(h.a, h.b), extra=[(x.a, x.b) for j, x in enumerate(hs) if j < hi])
        else:
            sc = scene_3d(M, -150, 18, size, margin=14)
            sc["d3"] = True
        out.append({"n": n, "t": txt, "s": sc})
    return out


def lupa_point(M):
    """Punkt arkusza (ułamki szerokości/wysokości od lewego górnego rogu) do pokazania kropek w lupie."""
    ps = [p for p in M.pieces if p.printed]
    g = max(ps, key=lambda p: p.paper.area).paper.buffer(-3)
    c = g.representative_point() if not g.is_empty else ps[0].paper.representative_point()
    return [R2(c.x / M.W), R2(1 - c.y / M.H)]


def model_data(M):
    return {
        "lupa": lupa_point(M),
        "slug": M.slug, "nazwa": M.name, "opis": M.tagline, "styl": M.style, "lot": M.fly,
        "trudnosc": M.difficulty, "W": M.W, "H": M.H, "orientacja": "pozioma" if M.W > M.H else "pionowa",
        "kolory": M.inks, "kropka": paint.DOT_PITCH,
        "ops": sheet_ops(M),
        "widoki": {
            "gora": scene_3d(M, -140, 32, (720, 440)),
            "spod": scene_3d(M, -60, -30, (720, 440)),
        },
        "kroki": steps_data(M),
    }
