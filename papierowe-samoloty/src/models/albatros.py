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
    style = "realistyczny: szybowiec pokazowy z jodełkami na skrzydłach"
    fly = "Wypuszczaj delikatnie, poziomo, z ręki nad głową. Szybuje wolno i długo – idealny do mieszkania."
    difficulty = 2
    inks = {"main": "#d62f3d"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, ellipse, Dots
        L = self.H - 68
        white = hx("#ffffff")
        navy = hx("#24375e")
        fill(ctx, white)
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.6))
            line(ctx, [(-300, 58), (300, 58)], white, lw=1.4)
            return
        if view in ("top", "bottom"):
            cov = 0.6 if view == "top" else 0.4
            for s in (1, -1):
                # jodełki: szerokie pasy w kształcie V skierowane do nosa, na przemian kolor i ciemny kolor
                for k in range(4):
                    x = 128 - k * 30
                    w = 11
                    col = self.dots(cov) if k % 2 == 0 else self.dots(cov, k=0.45)
                    poly(ctx, [(x, 0), (x - w, 0), (x - w - 62, 90 * s), (x - 62, 90 * s)], col)
                # końcówki skrzydeł
                poly(ctx, [(-10, 80 * s), (60, 80 * s), (60, 100 * s), (-10, 100 * s)], self.dots(cov, k=0.45))
            if view == "top":
                ellipse(ctx, L - 22, 0, 16, 3.2, Dots(hx("#2f6aa8"), 0.5), stroke=navy, lw=0.5)
                ellipse(ctx, L - 18, 0.8, 6, 0.8, white)
        else:
            u = -1 if view == "left" else 1
            for k in range(4):
                x = (128 - k * 30) * u
                poly(ctx, [(x, -5), (x - 11 * u, -5), (x - 14 * u, 60), (x - 3 * u, 60)],
                     self.dots(0.5) if k % 2 == 0 else self.dots(0.5, k=0.45))
