"""Symulator płaskiego składania kartki.

Kartka to zbiór ścianek (facet). Każda ścianka pamięta swój kształt we
współrzędnych kartki (mm, początek w lewym dolnym rogu, oś y w górę),
przekształcenie kartka -> stan złożony (izometria 2D) i numer warstwy z.
Strona z nadrukiem (P) jest zwrócona do góry, gdy wyznacznik
przekształcenia jest dodatni.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.validation import make_valid
import shapely

BIG = 5000.0
EPS_AREA = 0.05  # mm², mniejsze kawałki wyrzucamy


def polys(g):
    """Zwraca listę wielokątów z dowolnej geometrii."""
    if g.is_empty:
        return []
    if not g.is_valid:
        g = make_valid(g)
    return [p for p in _polys(g)]


def _polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g] if g.area > EPS_AREA else []
    if isinstance(g, MultiPolygon):
        return [p for p in g.geoms if p.area > EPS_AREA]
    out = []
    for p in getattr(g, "geoms", []):
        out += _polys(p)
    return out


def apply(M, g):
    """Przekształca geometrię shapely macierzą 3x3."""
    return affinity.affine_transform(g, [M[0, 0], M[0, 1], M[1, 0], M[1, 1], M[0, 2], M[1, 2]])


def reflection(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = (b - a) / np.linalg.norm(b - a)
    R = np.array([[d[0] ** 2 - d[1] ** 2, 2 * d[0] * d[1]], [2 * d[0] * d[1], d[1] ** 2 - d[0] ** 2]])
    M = np.eye(3)
    M[:2, :2] = R
    M[:2, 2] = a - R @ a
    return M


def halfplane(a, b, side):
    """Półpłaszczyzna po lewej (side='L') lub prawej ('R') stronie prostej a->b."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([-d[1], d[0]])
    if side == "R":
        n = -n
    p1, p2 = a - d * BIG, a + d * BIG
    return Polygon([p1, p2, p2 + n * BIG, p1 + n * BIG])


@dataclass
class Facet:
    poly: Polygon  # kształt we współrzędnych kartki
    M: np.ndarray  # kartka -> stan złożony
    z: float
    tag: dict = field(default_factory=dict)

    @property
    def flat(self):
        return apply(self.M, self.poly)

    @property
    def p_up(self):
        return np.linalg.det(self.M[:2, :2]) > 0

    @property
    def c(self):
        """Środek ścianki we współrzędnych kartki."""
        return self.poly.representative_point()


@dataclass
class Crease:
    seg: LineString  # odcinek we współrzędnych kartki
    kind: str  # 'valley' / 'mountain' widziane od strony nadruku
    step: int


@dataclass
class Step:
    text: str
    line: tuple | None  # (a, b) w układzie stanu przed krokiem
    move: str | None
    mode: str | None
    flip: bool = False
    state: list | None = None  # migawka ścianek przed krokiem
    extra: list = field(default_factory=list)  # dodatkowe linie (np. drugie zgięcie)


class Sheet:
    def __init__(self, W, H, printed_up=False):
        self.W, self.H = W, H
        M = np.eye(3)
        if not printed_up:
            # odwrócenie kartki „przez lewą krawędź”: widzimy spód
            M = np.array([[-1.0, 0, W], [0, 1, 0], [0, 0, 1]])
        self.facets = [Facet(Polygon([(0, 0), (W, 0), (W, H), (0, H)]), M, 0.0)]
        self.border = Polygon([(0, 0), (W, 0), (W, H), (0, H)]).exterior
        self.creases: list[Crease] = []
        self.steps: list[Step] = []
        self.nstep = 0

    # ------------------------------------------------------------------
    def snapshot(self):
        return [Facet(f.poly, f.M.copy(), f.z, dict(f.tag)) for f in self.facets]

    def renumber(self):
        order = sorted(self.facets, key=lambda f: f.z)
        for i, f in enumerate(order):
            f.z = float(i)

    def zmax(self):
        return max(f.z for f in self.facets)

    def zmin(self):
        return min(f.z for f in self.facets)

    def flip(self, text="Odwróć model na drugą stronę (jak stronę w książce).", axis="y"):
        """Odwraca cały model (obrót wokół osi pionowej przechodzącej przez środek)."""
        self.nstep += 1
        st = Step(text, None, None, None, flip=True, state=self.snapshot())
        self.steps.append(st)
        bb = unary_union([f.flat for f in self.facets]).bounds
        cx = (bb[0] + bb[2]) / 2
        F = np.array([[-1.0, 0, 2 * cx], [0, 1, 0], [0, 0, 1]])
        for f in self.facets:
            f.M = F @ f.M
            f.z = -f.z
        self.renumber()

    def rotate(self, deg, about=(0, 0)):
        """Obraca widok (bez kroku instrukcji)."""
        t = math.radians(deg)
        c, s = math.cos(t), math.sin(t)
        R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])
        T = np.eye(3)
        T[:2, 2] = about
        Ti = np.eye(3)
        Ti[:2, 2] = -np.asarray(about)
        F = T @ R @ Ti
        for f in self.facets:
            f.M = F @ f.M

    def translate(self, dx, dy):
        T = np.array([[1.0, 0, dx], [0, 1, dy], [0, 0, 1]])
        for f in self.facets:
            f.M = T @ f.M

    def fold(self, a, b, move="L", mode="valley", text="", select=None, z=None,
             unfold=False, record=True, mark=True, region=None):
        """Zgina wszystkie (lub wybrane) warstwy po stronie `move` prostej a->b.

        mode='valley' – część ruchoma ląduje na wierzchu, 'mountain' – pod spodem.
        z – jawna wysokość warstwy dla przeniesionych ścianek (do wsuwania).
        unfold=True – tylko zagniecenie (zgnij i rozłóż).
        """
        if not isinstance(move, str):
            d = np.asarray(b, float) - np.asarray(a, float)
            v = np.asarray(move, float) - np.asarray(a, float)
            move = "L" if d[0] * v[1] - d[1] * v[0] > 0 else "R"
        if record:
            self.nstep += 1
            self.steps.append(Step(text, (tuple(a), tuple(b)), move, mode, state=self.snapshot()))
        step = self.nstep
        hp_move = halfplane(a, b, move)
        if region is not None:
            hp_move = hp_move.intersection(region)
        hp_stay = Polygon([(-BIG, -BIG), (BIG, -BIG), (BIG, BIG), (-BIG, BIG)]).difference(hp_move)
        line = LineString([np.asarray(a) + (np.asarray(a) - np.asarray(b)) * 50,
                           np.asarray(b) + (np.asarray(b) - np.asarray(a)) * 50])
        R = reflection(a, b)
        new, moved = [], []
        for f in self.facets:
            if select is not None and not select(f):
                new.append(f)
                continue
            fl = f.flat
            if not fl.intersects(hp_move) or fl.intersection(hp_move).area < EPS_AREA:
                new.append(f)
                continue
            Minv = np.linalg.inv(f.M)
            # linia zgięcia na tej ściance
            if mark:
                cut = fl.intersection(line)
                if region is not None:
                    cut = cut.intersection(region.buffer(0.2))
                for seg in getattr(cut, "geoms", [cut]):
                    if isinstance(seg, LineString) and seg.length > 0.5:
                        ps = apply(Minv, seg)
                        if self.border.buffer(0.3).contains(ps):
                            continue
                        pk = "valley" if (mode == "valley") == f.p_up else "mountain"
                        self.creases.append(Crease(ps, pk, step))
            for part in polys(fl.intersection(hp_stay)):
                new.append(Facet(apply(Minv, part), f.M.copy(), f.z, dict(f.tag)))
            for part in polys(fl.intersection(hp_move)):
                moved.append(Facet(apply(Minv, part), f.M.copy(), f.z, dict(f.tag)))
        if not unfold and moved:
            for f in moved:
                f.tag["moves"] = f.tag.get("moves", ()) + (step,)
            zs = [f.z for f in moved]
            lo, hi = min(zs), max(zs)
            if z is not None:
                base = z
                for f in moved:
                    f.M = R @ f.M
                    f.z = base + (hi - f.z) * 1e-3 if mode == "valley" else base - (f.z - lo) * 1e-3
            elif mode == "valley":
                top = max(f.z for f in new + moved)
                for f in moved:
                    f.M = R @ f.M
                    f.z = top + 1 + (hi - f.z)
            else:
                bot = min(f.z for f in new + moved)
                for f in moved:
                    f.M = R @ f.M
                    f.z = bot - 1 - (f.z - lo)
        self.facets = new + moved
        self.renumber()
        return self

    def cut(self, region, text=""):
        """Odcina nożyczkami fragment `region` (współrzędne stanu złożonego) ze wszystkich warstw."""
        self.nstep += 1
        self.steps.append(Step(text, None, None, None, state=self.snapshot(), extra=[region]))
        edge = region.boundary
        new = []
        for f in self.facets:
            fl = f.flat
            Minv = np.linalg.inv(f.M)
            seg = fl.intersection(edge)
            for g in getattr(seg, "geoms", [seg]):
                if isinstance(g, LineString) and g.length > 0.5:
                    self.creases.append(Crease(apply(Minv, g), "cut", self.nstep))
            for part in polys(fl.difference(region)):
                new.append(Facet(apply(Minv, part), f.M.copy(), f.z, dict(f.tag)))
        self.facets = new
        self.renumber()

    def paper_to_flat(self, x, y):
        """Położenie punktu kartki w stanie złożonym."""
        p = Point(x, y)
        for f in self.facets:
            if f.poly.buffer(0.01).contains(p):
                return tuple(apply(f.M, p).coords[0])
        raise ValueError((x, y))

    def outline(self):
        return unary_union([f.flat.buffer(0.01) for f in self.facets])

    def at(self, x, y):
        """Ścianki pod punktem (x, y) stanu złożonego, od góry."""
        p = Point(x, y)
        return sorted([f for f in self.facets if f.flat.buffer(0.01).contains(p)], key=lambda f: -f.z)
