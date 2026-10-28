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
    style = "realistyczny: biały szybowiec wyczynowy z czerwonymi końcówkami"
    fly = "Wypuszczaj delikatnie, poziomo, z ręki nad głową. Szybuje wolno i długo – idealny do mieszkania."
    difficulty = 2

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, text, ellipse, lgrad, paint_src
        L = self.H - 68
        red, navy = hx("#e63946"), hx("#1d3557")
        if piece.zone == "winglet":
            fill(ctx, red)
            u = -1 if view == "left" else 1
            for k in range(3):
                rect(ctx, -400, 52 + k * 5, 400, 53.5 + k * 5, hx("#ffffff"))
            return
        if view == "top":
            fill(ctx, hx("#fbfbf8"))
            for s in (1, -1):
                # czerwone końcówki i pasy
                poly(ctx, [(-10, 72 * s), (200, 72 * s), (200, 100 * s), (-10, 100 * s)], red)
                rect(ctx, -10, min(66 * s, 69 * s), 200, max(66 * s, 69 * s), red)
                # linia krawędzi natarcia
                line(ctx, [(L, 0), (L - 90, 90 * s)], navy, lw=2.2)
                # lotki i klapy
                line(ctx, [(4, 20 * s), (4, 64 * s)], hx("#9aa3ab"), lw=0.35)
                line(ctx, [(4, 20 * s), (12, 20 * s)], hx("#9aa3ab"), lw=0.35)
                line(ctx, [(4, 42 * s), (12, 42 * s)], hx("#9aa3ab"), lw=0.35)
            text(ctx, "SP-3415", 40, 40, 11, rgb=navy, rot=0)
            text(ctx, "SP-3415", 40, -40, 11, rgb=navy, rot=0)
            # kabina (od góry, przy grzbiecie)
            ellipse(ctx, L - 20, 0, 18, 4, hx("#457b9d"))
            ellipse(ctx, L - 16, 1.2, 7, 1.2, hx("#ffffff", 0.6))
            text(ctx, "ALBATROS", 70, 0, 4.5, rgb=navy, alpha=0.7)
        elif view == "bottom":
            fill(ctx, hx("#eef0f1"))
            for s in (1, -1):
                poly(ctx, [(-10, 72 * s), (200, 72 * s), (200, 100 * s), (-10, 100 * s)], red)
            text(ctx, "SP-3415", 60, 38, 13, rgb=navy)
            text(ctx, "SP-3415", 60, -38, 13, rgb=navy)
        else:
            u = -1 if view == "left" else 1
            X = lambda x: x * u
            paint_src(ctx, lgrad(ctx, 0, 0, 0, 36, [(0, hx("#e9ecef")), (1, hx("#ffffff"))]))
            poly(ctx, [(X(L + 5), -2), (X(L - 30), -2), (X(L - 30), 40), (X(L + 5), 40)], red)
            rect(ctx, min(X(10), X(L - 30)), 8, max(X(10), X(L - 30)), 10, navy)
            text(ctx, "ALBATROS", X(70), 17, 6.5, rgb=navy)
            text(ctx, "SP-3415", X(40), 4, 3.5, rgb=navy)
