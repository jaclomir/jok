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
    style = "realistyczny: myśliwiec-agresor w kanciastym kamuflażu"
    fly = "Rzucaj płasko i średnio mocno. Leci szybko i prosto; podegnij tylne krawędzie, jeśli nurkuje."
    difficulty = 1
    inks = {"main": "#a9773a"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, ellipse, checker, splinter_camo, fill_geom, Dots
        L = self.H - self.NOS
        white = hx("#ffffff")
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.55, k=0.5))
            return
        tones = [self.dots(0.12), self.dots(0.34), self.dots(0.5, k=0.35), self.dots(0.55, k=0.7)]
        if view in ("top", "bottom"):
            fill(ctx, tones[0])
            lv = splinter_camo((-10, -90, 200, 90), n=46, seed=5 if view == "top" else 9, angle=-25)
            for g, t in zip(lv[1:], tones[1:]):
                fill_geom(ctx, g, t)
            for s in (1, -1):
                p = self.fit(view, 15, 15, (70, 28 * s))
                if p:
                    checker(ctx, p[0], p[1], 12)
                line(ctx, [(L - 2, 0.6 * s), (12, 75 * s)], white, lw=0.9)
            # ciemny nos i kabina
            poly(ctx, [(L - 40, -5), (L + 6, 0), (L - 40, 5)], tones[3])
            if view == "top":
                ellipse(ctx, L - 56, 0, 15, 3.1, Dots(hx("#9fd2f5"), 0.55), stroke=white, lw=0.4)
        else:
            fill(ctx, tones[1])
            lv = splinter_camo((-300, -10, 300, 60), n=30, seed=13, angle=10)
            for g, t in zip(lv[2:], tones[2:]):
                fill_geom(ctx, g, t)
