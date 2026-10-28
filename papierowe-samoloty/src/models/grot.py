import math
from base import Model, text
from model3d import Hinge


class Grot(Model):
    slug = "grot"
    half_flip = True
    name = "Grot"

    def build(self, s):
        W, H = self.W, self.H
        c = W / 2
        s.fold((c, H), (W, H - c), move=(W, H), text="Połóż wydruk nadrukiem do stołu, górną krawędzią od siebie (jak na rysunku obok). Zegnij prawy górny róg do siebie tak, by górna krawędź legła na środku kartki. Na zaginanej części pojawi się linia 1 – zagniataj dokładnie po niej.")
        s.fold((c, H), (0, H - c), move=(0, H), text="Tak samo zegnij lewy górny róg (linia 2).")
        y3 = H - c / math.tan(math.radians(22.5))
        s.fold((c, H), (W, y3), move=(W - 1, 100), text="Zegnij prawą skośną krawędź do środka wzdłuż linii 3. Czubek ma zostać ostry.")
        s.fold((c, H), (0, y3), move=(1, 100), text="To samo po lewej stronie (linia 4).")
        self.fold_half(s)

    def hinges(self):
        return [Hinge((self.H, 0), (0, 48), 90, "skrzydlo")]

    # ------------------------------------------------------------------
    tagline = "Klasyczna strzała – szybka i prosta"
    style = "realistyczny: myśliwiec w szarym kamuflażu"
    fly = "Rzucaj mocno i prosto, lekko w dół. Leci szybko i daleko, ale krótko – to klasyczna strzała."
    difficulty = 1

    def art(self, ctx, view, piece):
        from paint import (hx, fill, poly, rect, circle, ellipse, line, checker, splinter, text, lgrad,
                           paint_src)
        L = self.H
        if view == "top":
            fill(ctx, hx("#7d8a96"))
            splinter(ctx, -10, -70, 300, 70, [hx("#5e6b77"), hx("#9aa6b1"), hx("#6c7884")], n=22, seed=7)
            # radar w nosie
            poly(ctx, [(L - 40, -8), (L + 5, 0), (L - 40, 8)], hx("#3d4650"))
            # kabina na grzbiecie (rozdzielona zgięciem kadłuba)
            ellipse(ctx, L - 75, 0, 24, 4.2, hx("#1d3557"))
            ellipse(ctx, L - 70, 1.2, 10, 1.4, hx("#a8dadc", 0.7))
            # krawędź natarcia i szachownice
            for s in (1, -1):
                line(ctx, [(L, 0), (0, 63 * s)], hx("#c8d0d6"), lw=1.2)
                checker(ctx, 62, 36 * s, 15, rot=0)
                text(ctx, "07", 120, 22 * s, 9, rgb=hx("#2b2f33"), rot=0)
                # lotki
                line(ctx, [(2, 30 * s), (2, 58 * s)], hx("#3d4650"), lw=0.5)
                line(ctx, [(2, 30 * s), (22, 30 * s)], hx("#3d4650"), lw=0.4)
            # linie paneli
            for x in range(40, 280, 30):
                line(ctx, [(x, -60), (x, 60)], hx("#000000", 0.08), lw=0.3)
            text(ctx, "GROT", 175, 0, 6, rgb=hx("#ffffff"), alpha=0.6)
        elif view == "bottom":
            fill(ctx, hx("#d5dbe0"))
            for s in (1, -1):
                checker(ctx, 70, 34 * s, 14)
                # pocisk pod skrzydłem
                y = 22 * s
                rect(ctx, 120, y - 1.6, 185, y + 1.6, hx("#f1f3f5"))
                poly(ctx, [(185, y - 1.6), (194, y), (185, y + 1.6)], hx("#d4213d"))
                poly(ctx, [(120, y - 1.6), (112, y - 5), (124, y - 1.6)], hx("#8d99a6"))
                poly(ctx, [(120, y + 1.6), (112, y + 5), (124, y + 1.6)], hx("#8d99a6"))
                line(ctx, [(140, y), (175, y)], hx("#8d99a6"), lw=0.3)
            poly(ctx, [(L - 40, -6), (L + 5, 0), (L - 40, 6)], hx("#56606a"))
        else:
            # burty kadłuba: przód nadrukowany, tył zostaje biały
            u = -1 if view == "left" else 1
            paint_src(ctx, lgrad(ctx, 0, 0, 0, 40, [(0, hx("#b9c2ca")), (1, hx("#8d99a6"))]))
            X = lambda x: x * u
            poly(ctx, [(X(L + 5), -1), (X(L - 35), -1), (X(L - 35), 30), (X(L + 5), 30)], hx("#3d4650"))
            rect(ctx, min(X(150), X(230)), 3, max(X(150), X(230)), 5.5, hx("#d4213d"))
            rect(ctx, min(X(150), X(230)), 5.5, max(X(150), X(230)), 7, hx("#ffffff"))
            text(ctx, "07", X(200), 14, 9, rgb=hx("#2b2f33"))
            checker(ctx, X(160), 14, 9)
            text(ctx, "SIŁY POWIETRZNE KARTKI", X(232), 9, 2.1, rgb=hx("#2b2f33"), alpha=0.8)
            # wlot powietrza
            poly(ctx, [(X(140), 2), (X(165), 2), (X(165), 8), (X(140), 10)], hx("#2a3038"))
