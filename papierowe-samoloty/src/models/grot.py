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
    style = "realistyczny: jasnoszary myśliwiec z szachownicą"
    fly = "Rzucaj mocno i prosto, lekko w dół. Leci szybko i daleko – to klasyczna strzała."
    difficulty = 1

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, ellipse, line, checker, splinter, feat
        L = self.H
        panel = hx("#8e98a3")
        if view == "top":
            fill(ctx, hx("#dde2e7"))
            splinter(ctx, -10, -70, 300, 70, [hx("#c8d0d8"), hx("#d2d9e0"), hx("#bfc8d1")], n=22, seed=7)
            # linie paneli i krawędź natarcia
            for s in (1, -1):
                line(ctx, [(L - 6, 0.5 * s), (0, 63 * s)], hx("#b9c1c9"), lw=0.6)
                for x in (60, 110, 160, 210):
                    yy = 63 * (1 - x / L)
                    line(ctx, [(x, 2 * s), (x, yy * s)], panel, lw=0.2)
                # lotki przy tylnej krawędzi
                line(ctx, [(10, 26 * s), (10, 54 * s)], panel, lw=0.35)
                line(ctx, [(0, 26 * s), (10, 26 * s)], panel, lw=0.35)
                p = self.fit("top", 16, 16, (62, 36 * s))
                if p:
                    checker(ctx, p[0], p[1], 13)
                self.label(ctx, "top", "07", (125, 22 * s), 8, rgb=hx("#4a535d"))
                self.label(ctx, "top", "NIE STAWAĆ", (95, 9 * s), 2.2, rgb=hx("#6b737c"), bold=False)
            # kabina na grzbiecie i stożek nosa
            poly(ctx, [(L - 100, -3), (L - 40, -3.5), (L - 40, 3.5), (L - 100, 3)], hx("#a3acb6"))
            ellipse(ctx, L - 72, 0, 22, 3.4, hx("#7fa6c4"), stroke=hx("#3d5a75"), lw=0.3)
            ellipse(ctx, L - 66, 1.0, 8, 1.0, hx("#e8f1f8"))
            poly(ctx, [(L - 34, -4.5), (L + 4, 0), (L - 34, 4.5)], hx("#b3bcc6"))
        elif view == "bottom":
            fill(ctx, hx("#f1f3f5"))
            for s in (1, -1):
                p = self.fit("bottom", 15, 15, (180, 28 * s))
                if p:
                    checker(ctx, p[0], p[1], 12)
                # podwieszony pocisk – tylko kontur
                y = 14 * s
                x0 = 205
                poly(ctx, [(x0, y - 1.4), (x0 + 50, y - 1.4), (x0 + 58, y), (x0 + 50, y + 1.4), (x0, y + 1.4)],
                     hx("#fbfbfb"), stroke=hx("#7b8591"), lw=0.3)
                poly(ctx, [(x0 + 50, y - 1.4), (x0 + 58, y), (x0 + 50, y + 1.4)], hx("#e05a6b"))
                line(ctx, [(x0 + 2, y), (x0 - 5, y + 4 * s)], hx("#7b8591"), lw=0.3)
            line(ctx, [(60, 0), (L, 0)], panel, lw=0.2)
        else:
            u = -1 if view == "left" else 1
            fill(ctx, hx("#e2e6ea"))
            # pas wzdłuż burty
            line(ctx, [(150 * u, 4), (290 * u, 1.5)], hx("#e05a6b"), lw=0.9)
            # wlot powietrza
            poly(ctx, [(150 * u, 1), (172 * u, 1), (172 * u, 5), (150 * u, 6)], hx("#c3cad1"), stroke=panel, lw=0.25)
            self.label(ctx, view, "07", (215 * u, 8), 6, rgb=hx("#4a535d"), outline=0.3)
