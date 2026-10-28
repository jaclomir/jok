from shapely.geometry import box
from base import Model
from model3d import Hinge


class Albatros(Model):
    """Szybowiec z kartki w poziomie: tępy nos, wzmocniona krawędź natarcia."""
    slug = "albatros"
    half_flip = True
    name = "Albatros"
    W, H = 297.0, 210.0

    def build(self, s):
        W, H = self.W, self.H
        c = W / 2
        s.fold((c, H), (0, H - c), move=(0, H), text="Połóż wydruk poziomo, nadrukiem do stołu, górną krawędzią od siebie. Zegnij lewy górny róg do siebie tak, by górna krawędź legła na środku. Na zaginanej części pojawi się linia 1.")
        s.fold((c, H), (W, H - c), move=(W, H), text="Tak samo zegnij prawy róg (linia 2). Powstaje szeroki trójkąt.")
        yn = H - 68
        s.fold((0, yn), (W, yn), move=(c, H), text="Zegnij czubek trójkąta w dół, do siebie, wzdłuż poziomej linii 3 – nos robi się tępy.")
        # krawędzie natarcia: linia równoległa do pierwszego zgięcia, cofnięta o 44 mm
        off = 44
        s.fold((c - (c - off), H - c + 0), (c, H - off), move=(10, 160), region=box(0, 0, c, H),
               text="Zawiń lewą skośną krawędź do środka wzdłuż linii 4 (biegnie równolegle do krawędzi). To wzmocniona krawędź natarcia.")
        s.fold((W - off, H - c), (c, H - off), move=(W - 10, 160), region=box(c, 0, W, H),
               text="To samo po prawej stronie (linia 5).")
        self.fold_half(s)

    def hinges(self):
        return [Hinge((self.H - 68, 26), (0, 36), 90, "skrzydlo"),
                Hinge((60, 123), (0, 126), -90, "winglet")]

    # ------------------------------------------------------------------
    tagline = "Szeroki szybowiec – długi, spokojny lot w domu"
    style = "realistyczny: biały szybowiec wyczynowy z kolorowymi łukami"
    fly = "Wypuszczaj delikatnie, poziomo, z ręki nad głową. Szybuje wolno i długo – idealny do mieszkania."
    difficulty = 2
    inks = {"main": "#d62f3d"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, ellipse, band, bez_pts, Dots
        L = self.H - 68
        navy, grey = hx("#24375e"), hx("#a9b1ba")
        fill(ctx, hx("#ffffff"))
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.4))
            line(ctx, [(-300, 58), (300, 58)], hx("#ffffff"), lw=1.4)
            return
        if view in ("top", "bottom"):
            cov = 0.62 if view == "top" else 0.4
            for s in (1, -1):
                # dwa łuki koloru zakręcające do końca skrzydła
                a = bez_pts((-10, 54 * s), (40, 54 * s), (70, 64 * s), (110, 88 * s), 40)
                b = bez_pts((-10, 64 * s), (30, 64 * s), (55, 72 * s), (85, 92 * s), 40)
                poly(ctx, band(a, 5, 9), self.dots(cov))
                poly(ctx, band(b, 3, 6), self.dots(cov, k=0.35))
                poly(ctx, [(-10, 78 * s), (60, 78 * s), (95, 100 * s), (-10, 100 * s)], self.dots(cov))
                if view == "top":
                    line(ctx, [(L - 2, 1 * s), (L - 92, 90 * s)], self.c(0.3), lw=0.6)
                    for y in (22, 44):
                        line(ctx, [(0, y * s), (9, y * s)], grey, lw=0.3)
                    line(ctx, [(9, 22 * s), (9, 44 * s)], grey, lw=0.3)
            if view == "top":
                self.label(ctx, "top", "SP-3415", (60, 30), 9, rgb=navy, bold=False)
                self.label(ctx, "top", "SP-3415", (60, -30), 9, rgb=navy, bold=False)
                ellipse(ctx, L - 22, 0, 16, 3.2, Dots(hx("#2f6aa8"), 0.45), stroke=navy, lw=0.3)
                ellipse(ctx, L - 18, 0.8, 6, 0.8, hx("#ffffff"))
            else:
                self.label(ctx, "bottom", "SP-3415", (70, 30), 9, rgb=navy, bold=False)
        else:
            u = -1 if view == "left" else 1
            line(ctx, [(10 * u, 9), ((L - 8) * u, 9)], self.c(), lw=1.2)
            line(ctx, [(10 * u, 11.5), ((L - 8) * u, 11.5)], self.c(0.35), lw=0.5)
            poly(ctx, [((L + 4) * u, -2), ((L - 14) * u, -2), ((L - 14) * u, 40), ((L + 4) * u, 40)], self.dots(0.4))
            self.label(ctx, view, "ALBATROS", (90 * u, 20), 4.5, rgb=navy)
