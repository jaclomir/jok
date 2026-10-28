"""Wspólna baza modeli."""
from __future__ import annotations

import math

import cairocffi as cairo
import numpy as np

from fold import Sheet
from model3d import Hinge, Plane3D


class Model:
    slug = "model"
    name = "Model"
    W, H = 210.0, 297.0
    ppmm = 6
    hidden_fill = None
    hide_steps: set = set()
    step_label: dict = {}
    dihedral = 6.0
    difficulty = 1
    tagline = ""
    style = ""
    fly = ""

    def __init__(self):
        self.sheet = Sheet(self.W, self.H, printed_up=self.printed_up)
        self.build(self.sheet)
        self.plane = Plane3D(self.sheet, self.half_of, self.hinges(), dihedral=self.dihedral)
        self.pieces = self.plane.pieces()
        from fold import Crease
        self.n_flat = self.sheet.nstep
        for seg, kind, st in self.plane.hinge_creases(self.n_flat + 1):
            self.sheet.creases.append(Crease(seg, kind, st))
        self.final_steps = self.finish_steps()
        self._wm = self.find_watermark()

    printed_up = False
    half_flip = False

    def fold_half(self, s, text=None):
        W, H = self.W, self.H
        c = W / 2
        if self.half_flip:
            s.flip()
        text = text or (f"Złóż model na pół wzdłuż środkowej linii {s.nstep + 1} – prawą połowę na lewą. "
                        "Zagnieć mocno paznokciem.")
        s.fold((c, 0), (c, H), move=(W - 1, 10), text=text)
        self.half_step = s.nstep
        s.rotate(-90)
        s.translate(0, c)

    def build(self, s: Sheet):
        raise NotImplementedError

    def half_of(self, f):
        return "B" if self.half_step in f.tag.get("moves", ()) else "A"

    def hinges(self) -> list[Hinge]:
        return []

    wing_text = "Zegnij skrzydło w dół wzdłuż linii {n}, tak by leżało na kadłubie. Odwróć model i powtórz z drugim skrzydłem."
    winglet_text = "Zegnij końcówki skrzydeł (winglety) do góry wzdłuż linii {n}."
    trim_text = ("Rozłóż skrzydła poziomo, lekko w kształt litery V. Jeśli model nurkuje, podegnij lekko "
                 "tylne krawędzie skrzydeł do góry; jeśli wznosi się i przepada – wyprostuj je.")

    def finish_steps(self):
        """Kroki po złożeniu na pół: (numer, tekst, indeks zawiasu albo None)."""
        out = []
        n = self.n_flat
        for i, h in enumerate(self.hinges()):
            n += 1
            t = self.wing_text if i == 0 else self.winglet_text
            if i > 0 and h.angle > 0:
                t = "Zegnij końcówki skrzydeł (winglety) w dół wzdłuż linii {n}."
            out.append((n, t.format(n=n), i))
        out.append((n + 1, self.trim_text, None))
        return out

    wm_text = "domowydrukarz.pl"

    def find_watermark(self):
        """Szuka miejsca na napis, które po złożeniu będzie całkowicie schowane."""
        from shapely import affinity
        from shapely.geometry import box
        from shapely.ops import unary_union
        vis = unary_union([p.paper for p in self.pieces if p.printed]).buffer(7)
        hidden = box(4, 4, self.W - 4, self.H - 4).difference(vis)
        best = None
        for size in (4.0, 3.2, 2.6, 2.0):
            w, h = len(self.wm_text) * size * 0.62, size * 1.3
            for ang in (0, 90, 45, -45, 30, -30, 60, -60):
                r = affinity.rotate(box(-w / 2, -h / 2, w / 2, h / 2), ang, origin=(0, 0))
                for x in np.arange(10, self.W - 10, 3):
                    for y in np.arange(10, self.H - 10, 3):
                        if hidden.contains(affinity.translate(r, x, y)):
                            best = (x, y, ang, size)
                            break
                    if best:
                        break
                if best:
                    return best
        return None

    def watermark(self, ctx):
        if not self._wm:
            return
        x, y, ang, size = self._wm
        text(ctx, self.wm_text, x, y, size, rgb=(0.55, 0.57, 0.6), rot=ang, alpha=0.8)

    def art(self, ctx, view, piece):
        """Domyślny wzór kontrolny: kolor wg widoku i siatka 10 mm."""
        col = {"top": (0.95, 0.6, 0.2), "bottom": (0.3, 0.6, 0.95), "left": (0.4, 0.8, 0.4),
               "right": (0.85, 0.4, 0.7)}[view]
        ctx.set_source_rgb(*col)
        ctx.paint()
        ctx.set_source_rgba(0, 0, 0, 0.5)
        ctx.set_line_width(0.3)
        for i in range(-40, 41):
            ctx.move_to(i * 10, -400)
            ctx.line_to(i * 10, 400)
            ctx.move_to(-400, i * 10)
            ctx.line_to(400, i * 10)
        ctx.stroke()
        for x in range(0, 300, 50):
            for y in range(-150, 151, 50):
                text(ctx, f"{view[0].upper()}{x},{y}", x, y, 4)


# ----------------------------------------------------------------------
def text(ctx, t, x, y, size, rgb=(0, 0, 0), bold=True, rot=0.0, align="center", font="DejaVu Sans",
         alpha=1.0, italic=False):
    """Tekst w układzie y-w-górę (współrzędne widoku)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(rot))
    ctx.scale(1, -1)
    ctx.select_font_face(font, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    xb, yb, ew, eh, _, _ = ctx.text_extents(t)
    dx = {"center": -ew / 2 - xb, "left": -xb, "right": -ew - xb}[align]
    ctx.move_to(dx, -yb / 2)
    ctx.set_source_rgba(*rgb, alpha)
    ctx.show_text(t)
    ctx.restore()
