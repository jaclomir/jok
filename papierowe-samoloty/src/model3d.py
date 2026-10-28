"""Złożony model w 3D: kadłub, skrzydła, winglety; widoczne fragmenty kartki.

Po zakończeniu płaskiego składania (łącznie ze złożeniem na pół) model leży
na boku: nos w stronę +x, stępka na dole (małe y), skrzydła u góry.
Układ 3D: X – do przodu, Y – w lewo, Z – w górę.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import shapely
from shapely.geometry import Point
from shapely.ops import unary_union

from fold import Facet, Sheet, apply, halfplane, polys

LAYER = 0.12  # mm grubości warstwy (tylko do porządku rysowania)


def rot_axis(p0, d, ang):
    """Macierz 4x4 obrotu o kąt `ang` wokół osi przez p0 o kierunku d."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    x, y, z = d
    c, s, C = math.cos(ang), math.sin(ang), 1 - math.cos(ang)
    R = np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                  [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                  [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = np.asarray(p0) - R @ np.asarray(p0)
    return T


@dataclass
class Hinge:
    a: tuple  # punkt osi (współrzędne płaskie)
    b: tuple
    angle: float  # stopnie; 90 = skrzydło poziomo
    zone: str  # nazwa strefy za zawiasem


@dataclass
class Piece:
    facet: Facet
    face: str  # 'top' / 'bottom' (względem warstw w stanie płaskim)
    paper: object  # wielokąt na kartce
    printed: bool  # czy widać stronę z nadrukiem
    A: np.ndarray  # 3x4: [px, py, 1] -> punkt 3D (dla wygody 4x4 jest niżej)
    normal: np.ndarray
    zone: str
    half: str

    @property
    def view(self):
        n = self.normal
        if n[2] > 0.55:
            return "top"
        if n[2] < -0.55:
            return "bottom"
        return "left" if n[1] > 0 else "right"


VIEW_AXES = {
    # (u, v) = rzut punktu 3D; patrz komentarz w README
    "top": np.array([[1, 0, 0], [0, 1, 0]], float),
    "bottom": np.array([[1, 0, 0], [0, -1, 0]], float),
    "left": np.array([[-1, 0, 0], [0, 0, 1]], float),
    "right": np.array([[1, 0, 0], [0, 0, 1]], float),
}


class Plane3D:
    def __init__(self, sheet: Sheet, half_of, hinges: list[Hinge], dihedral=6.0):
        """half_of(facet) -> 'A' lub 'B'; hinges uporządkowane od kadłuba na zewnątrz."""
        self.sheet = sheet
        self.half_of = half_of
        self.hinges = hinges
        self.dihedral = dihedral
        self.facets = [Facet(f.poly, f.M.copy(), f.z, dict(f.tag)) for f in sheet.facets]
        for f in self.facets:
            f.tag["half"] = half_of(f)
        # cięcie ścianek wzdłuż zawiasów
        for h in hinges:
            out = []
            for f in self.facets:
                fl = f.flat
                Minv = np.linalg.inv(f.M)
                for side in "LR":
                    for part in polys(fl.intersection(halfplane(h.a, h.b, side))):
                        out.append(Facet(apply(Minv, part), f.M.copy(), f.z, dict(f.tag)))
            self.facets = out
        zs = sorted(f.z for f in self.facets)
        self.zmid = (zs[0] + zs[-1]) / 2
        # strona półówki: B ma większe z (bliżej +Y)
        za = [f.z for f in self.facets if f.tag["half"] == "A"]
        zb = [f.z for f in self.facets if f.tag["half"] == "B"]
        self.sign = {"A": 1.0, "B": -1.0} if (np.mean(za) > np.mean(zb)) else {"A": -1.0, "B": 1.0}
        for f in self.facets:
            f.tag["zone"] = "kadlub"
            f.tag["T"] = self._transform(f)

    def _zone_side(self, h, f):
        c = f.flat.representative_point()
        return halfplane(h.a, h.b, "L").contains(c)

    def _rot(self, h, s, extra=0.0):
        a3 = np.array([h.a[0], 0, h.a[1]])
        b3 = np.array([h.b[0], 0, h.b[1]])
        ang = h.angle - (self.dihedral if h is self.hinges[0] else 0.0)
        return rot_axis(a3, b3 - a3, math.radians(ang) * self._rot_sign(h, s))

    def _chain(self, f):
        return [h for h in self.hinges if self._far_side(h).contains(f.flat.representative_point())]

    def _transform(self, f):
        """Macierz 4x4: punkt (x_flat, y_flat, 0) -> 3D."""
        half = f.tag["half"]
        s = self.sign[half]
        base = np.array([[1, 0, 0, 0], [0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
        base[1, 3] = (f.z - self.zmid) * LAYER
        chain = self._chain(f)
        if chain:
            f.tag["zone"] = chain[-1].zone
        T = np.eye(4)
        # najpierw zewnętrzne zawiasy, potem wewnętrzne
        for h in reversed(chain):
            T = self._rot(h, s) @ T
        f.tag["R"] = T
        return T @ base

    def hinge_creases(self, step0):
        """Linie zgięć skrzydeł/wingletów na kartce: lista (odcinek, rodzaj, krok)."""
        from shapely.geometry import LineString
        out = []
        for i, h in enumerate(self.hinges):
            a, b = np.array(h.a, float), np.array(h.b, float)
            ln = LineString([a - (b - a) * 50, b + (b - a) * 50])
            far = self._far_side(h)
            d2 = np.array([-(b - a)[1], (b - a)[0]])
            d2 /= np.linalg.norm(d2)
            if far.contains(Point(*((a + b) / 2 + d2))):
                d2 = -d2  # d2: w stronę części nieruchomej
            for f in self.facets:
                if h not in self._chain(f):
                    continue
                seg = f.flat.intersection(ln)
                for g in getattr(seg, "geoms", [seg]):
                    if not isinstance(g, LineString) or g.length < 0.5:
                        continue
                    s = self.sign[f.tag["half"]]
                    inner = np.eye(4)
                    for hh in reversed(self.hinges[:i]):
                        if hh in self._chain(f):
                            inner = self._rot(hh, s) @ inner
                    R = f.tag["R"]
                    pn = R[:3, :3] @ np.array([0, 1.0 if f.p_up else -1.0, 0])
                    dfix = inner[:3, :3] @ np.array([d2[0], 0, d2[1]])
                    kind = "valley" if np.dot(pn, dfix) > 0 else "mountain"
                    out.append((apply(np.linalg.inv(f.M), g), kind, step0 + i))
        return out

    def _far_side(self, h):
        # strona prostej po której leży punkt najdalszy od stępki (największe y)
        bb = unary_union([f.flat for f in self.facets]).bounds
        far = Point((bb[0] + bb[2]) / 2, bb[3] + 1000)
        hpL = halfplane(h.a, h.b, "L")
        return hpL if hpL.contains(far) else halfplane(h.a, h.b, "R")

    def _rot_sign(self, h, s):
        """Znak obrotu tak, by część za zawiasem poszła w stronę s*Y."""
        a3 = np.array([h.a[0], 0, h.a[1]])
        b3 = np.array([h.b[0], 0, h.b[1]])
        d = b3 - a3
        # punkt testowy za zawiasem
        n2 = np.array([-(h.b[1] - h.a[1]), h.b[0] - h.a[0]])
        far = self._far_side(h)
        mid = (np.array(h.a) + np.array(h.b)) / 2
        test = mid + n2 / np.linalg.norm(n2) * 5
        if not far.contains(Point(*test)):
            test = mid - n2 / np.linalg.norm(n2) * 5
        p = np.array([test[0], 0, test[1], 1])
        q = rot_axis(a3, d, math.radians(45)) @ p
        return 1.0 if np.sign(q[1]) == np.sign(s) else -1.0

    # ------------------------------------------------------------------
    def pieces(self):
        """Widoczne fragmenty: dla każdego panelu wierzch i spód stosu."""
        groups = {}
        for f in self.facets:
            key = ("kadlub",) if f.tag["zone"] == "kadlub" else (f.tag["zone"], f.tag["half"])
            groups.setdefault(key, []).append(f)
        out = []
        for key, fs in groups.items():
            fs = sorted(fs, key=lambda f: f.z)
            flats = [shapely.set_precision(f.flat, 0.001) for f in fs]
            for i, f in enumerate(fs):
                above = unary_union(flats[i + 1:]) if i + 1 < len(fs) else None
                below = unary_union(flats[:i]) if i > 0 else None
                for face, cover in (("top", above), ("bottom", below)):
                    vis = flats[i] if cover is None else flats[i].difference(cover)
                    Minv = np.linalg.inv(f.M)
                    for part in polys(vis):
                        if part.area < 1.0:
                            continue
                        T = f.tag["T"]
                        # kartka -> płaskie -> 3D
                        M = f.M
                        A = T @ np.array([[M[0, 0], M[0, 1], 0, M[0, 2]],
                                          [M[1, 0], M[1, 1], 0, M[1, 2]],
                                          [0, 0, 1, 0], [0, 0, 0, 1]])
                        nflat = np.array([0, 1.0, 0]) if face == "top" else np.array([0, -1.0, 0])
                        n = f.tag["R"][:3, :3] @ nflat
                        printed = f.p_up if face == "top" else not f.p_up
                        out.append(Piece(f, face, apply(Minv, part), printed, A, n,
                                         f.tag["zone"], f.tag["half"]))
        return out


def view_affine(piece: Piece, view=None):
    """Macierz 3x3: kartka (mm) -> współrzędne widoku (u, v) dla danego fragmentu."""
    view = view or piece.view
    P = VIEW_AXES[view]
    A = piece.A
    L = P @ A[:3, [0, 1, 3]]  # 2x3
    M = np.eye(3)
    M[:2, :] = L
    return M
