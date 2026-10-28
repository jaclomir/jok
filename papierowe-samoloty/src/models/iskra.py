import math
from base import Model
from model3d import Hinge


class Iskra(Model):
    """Szeroka delta z kartki w poziomie – szybka i prosta: rogi, boki, nos, na pół i gotowe."""
    slug = "iskra"
    name = "Iskra"
    W, H = 297.0, 210.0
    NOS = 19.0

    def build(self, s):
        W, H = self.W, self.H
        c = W / 2
        s.fold((c, H), (0, H - c), move=(0, H), text=("Połóż wydruk poziomo, nadrukiem do stołu, górną krawędzią od siebie. "
                                                     "Zegnij lewy górny róg do siebie tak, by górna krawędź legła na środku. "
                                                     "Na zaginanej części pojawi się linia 1."))
        s.fold((c, H), (W, H - c), move=(W, H), text="Tak samo zegnij prawy róg (linia 2).")
        x2 = H * math.tan(math.radians(22.5))
        s.fold((c, H), (c - x2, 0), move=(1, 150), text="Zegnij lewą skośną krawędź jeszcze raz do środka (linia 3).")
        s.fold((c, H), (c + x2, 0), move=(W - 1, 150), text="To samo po prawej (linia 4).")
        s.fold((0, H - self.NOS), (W, H - self.NOS), move=(c, H),
               text="Zegnij sam czubek nosa w dół, do siebie, wzdłuż krótkiej linii 5.")
        self.fold_half(s)

    def hinges(self):
        L = self.H - self.NOS
        return [Hinge((L - 27, 20), (0, 30.5), 90, "skrzydlo"),
                Hinge((50, 66), (0, 77), -90, "winglet")]

    # ------------------------------------------------------------------
    tagline = "Szeroka delta – złożysz ją w minutę"
    style = "realistyczny: biało-kolorowy samolot szkolno-akrobacyjny"
    fly = "Rzucaj płasko i średnio mocno. Leci szybko i prosto; podegnij tylne krawędzie, jeśli nurkuje."
    difficulty = 1
    inks = {"main": "#d62f3d"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, ellipse, checker, Dots
        L = self.H - self.NOS
        grey = hx("#9aa4b0")
        fill(ctx, hx("#ffffff"))
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.45))
            return
        if view == "top" or view == "bottom":
            tint = 0.42 if view == "top" else 0.3
            # kolorowy pas wzdłuż tylnej krawędzi i dwa skośne pasy jak na samolotach akrobacyjnych
            poly(ctx, [(-10, -100), (26, -100), (26, 100), (-10, 100)], self.dots(tint))
            line(ctx, [(26, -100), (26, 100)], self.c(0.1), lw=0.5)
            for s in (1, -1):
                for k, w in ((0, 2.2), (1, 1.2)):
                    off = 9 * k
                    line(ctx, [(L - 40 - off, 2 * s), (30 - off, 72 * s)], self.c(0.05), lw=w)
                line(ctx, [(8, 8 * s), (8, 56 * s)], grey, lw=0.3)
                p = self.fit(view, 14, 14, (75, 22 * s))
                if p:
                    checker(ctx, p[0], p[1], 11 if view == "top" else 10)
            poly(ctx, [(L - 22, -6), (L + 6, 0), (L - 22, 6)], self.dots(0.45))
            if view == "top":
                ellipse(ctx, L - 42, 0, 15, 3, Dots(hx("#2f6aa8"), 0.42), stroke=hx("#3b4552"), lw=0.3)
                ellipse(ctx, L - 38, 0.8, 6, 0.8, hx("#ffffff"))
                self.label(ctx, "top", "1", (120, 30), 8, rgb=self.c(0.3))
        else:
            u = -1 if view == "left" else 1
            line(ctx, [(30 * u, 4), (170 * u, 4)], self.c(), lw=1.0)
            self.label(ctx, view, "ISKRA", (110 * u, 11), 5, rgb=self.c(0.3))
