import numpy as np
from shapely.geometry import Polygon, box
from base import Model
from model3d import Hinge


def bezier(p0, p1, p2, p3, n=40):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return list(map(tuple, (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3))


class Wazka(Model):
    """Dwie pary skrzydeł z jednej kartki: zwinięta krawędź natarcia i wycięcie w kształcie fali."""
    slug = "wazka"
    half_flip = True
    name = "Ważka"
    W, H = 297.0, 210.0
    STRIP, NROLL = 12.0, 7

    def build(self, s):
        W, H = self.W, self.H
        c = W / 2
        for k in range(1, self.NROLL + 1):
            y = H - self.STRIP * k
            s.fold((0, y), (W, y), move=(c, H), record=(k == 1),
                   text=(f"Połóż wydruk poziomo, nadrukiem do stołu, górną krawędzią od siebie. Zegnij górny pas do siebie "
                         f"wzdłuż linii 1 i zwijaj go dalej, pas po pasie, aż do linii STOP ({self.NROLL} zgięć)."))
        self.fold_half(s)
        L = H - self.STRIP * self.NROLL  # długość po zwinięciu
        self.L = L
        curve = bezier((L - 13, 160), (L - 13, 70), (L - 40, 38), (64, 38)) + \
            bezier((64, 38), (40, 38), (12, 80), (3, 160))
        s.cut(Polygon(curve + [(3, 200), (L - 13, 200)]),
              text="Przytrzymaj obie połówki razem i wytnij nożyczkami falę wzdłuż kropkowanej linii – przez wszystkie warstwy naraz.")

    def hinges(self):
        L = self.H - self.STRIP * self.NROLL
        return [Hinge((L, 19), (0, 19), 90, "skrzydlo"),
                Hinge((L, 124), (L - 30, 124), -90, "winglet", region=box(L - 30, 0, L + 5, 200)),
                Hinge((40, 120), (0, 120), 90, "winglet", region=box(-5, 0, 40, 200))]

    def finish_steps(self):
        n = self.n_flat
        return [(n + 1, f"Zegnij skrzydła w dół wzdłuż linii {n + 1}, po jednym z każdej strony.", 0),
                (n + 2, f"Końcówki przednich skrzydeł zegnij do góry (linia {n + 2}), tylnych – w dół (linia {n + 3}).", 1),
                (n + 4, self.trim_text, None)]

    # ------------------------------------------------------------------
    tagline = "Dwie pary skrzydeł – zwinna akrobatka"
    style = "realistyczny: ważka o przezroczystych skrzydłach"
    fly = "W domu rzucaj lekko, poziomo. Na dworze, rzucona mocniej, robi pętle. Potrzebne nożyczki (jedno cięcie)."
    difficulty = 2
    inks = {"main": "#1f9a93"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, circle, ellipse, feat
        L = self.H - self.STRIP * self.NROLL
        vein = self.c(-0.0)
        fill(ctx, hx("#ffffff"))
        if piece.zone == "winglet":
            for k in range(5):
                line(ctx, [(-300, k * 4), (300, k * 4 + 2)], vein, lw=0.25)
            return
        if view == "top":
            ellipse(ctx, L - 40, 0, 70, 40, self.dots(0.06))
            for s in (1, -1):
                for k in range(5):
                    xs = L - 3 - k * 3.2
                    line(ctx, [(xs, 4 * s), (xs - 2, 150 * s)], vein, lw=0.28)
                for k in range(7):
                    line(ctx, [(8 + k * 7, 4 * s), (2 + k * 2, 150 * s)], vein, lw=0.28)
                for y in range(10, 150, 6):
                    line(ctx, [(L - 20, y * s), (L, y * s)], vein, lw=0.16)
                    line(ctx, [(0, y * s), (55, (y + 3) * s)], vein, lw=0.16)
                for near in ((L - 7, 132 * s), (12, 132 * s)):
                    p = self.fit("top", 6, 5, near)
                    if p:
                        poly(ctx, [(p[0] - 2.5, p[1]), (p[0], p[1] - 2 * s), (p[0] + 2.5, p[1]), (p[0], p[1] + 2 * s)], self.c(0.3))
                        feat(ctx, "plamka", p[0] - 2.5, p[1] - 2, p[0] + 2.5, p[1] + 2)
                p = self.fit("top", 11, 11, (L - 8, 7 * s))
                if p:
                    circle(ctx, p[0], p[1], 4.8, self.dots(0.45), stroke=self.c(0.35), lw=0.45)
                    circle(ctx, p[0] + 1.2, p[1] + 0.5 * s, 1.6, hx("#1d2b33"))
                    circle(ctx, p[0] + 1.8, p[1] + 1.1 * s, 0.6, hx("#ffffff"))
                    feat(ctx, "oko", p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5)
            ellipse(ctx, L - 22, 0, 8, 4.2, self.dots(0.45), stroke=self.c(0.35), lw=0.4)
            for k in range(9):
                ellipse(ctx, L - 36 - k * 9.5, 0, 4.6, 3.0 - k * 0.15, self.dots(0.48 if k % 2 else 0.3),
                        stroke=self.c(0.35), lw=0.35)
        elif view == "bottom":
            for k in range(3):
                line(ctx, [(L - 3 - k * 3.5, -150), (L - 3 - k * 3.5, 150)], vein, lw=0.25)
        else:
            for k in range(4):
                line(ctx, [(-300, 2 + k * 3), (300, 2 + k * 3)], vein, lw=0.25)
