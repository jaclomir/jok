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
    style = "realistyczny: myśliwiec w kamuflażu z szachownicą"
    fly = "Rzucaj mocno i prosto, lekko w dół. Leci szybko i daleko – to klasyczna strzała."
    difficulty = 1
    inks = {"main": "#5f6e7d"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, ellipse, line, checker, splinter, Dots
        L = self.H
        panel = self.c(0.15)
        if view == "top":
            fill(ctx, self.dots(0.11))
            splinter(ctx, -10, -70, 300, 70, [self.dots(0.2), self.dots(0.28), self.dots(0.16)], n=22, seed=7)
            for s in (1, -1):
                line(ctx, [(L - 6, 0.5 * s), (0, 63 * s)], hx("#ffffff"), lw=0.8)
                for x in (60, 110, 160, 210):
                    line(ctx, [(x, 2 * s), (x, 63 * (1 - x / L) * s)], panel, lw=0.2)
                line(ctx, [(10, 26 * s), (10, 54 * s)], panel, lw=0.35)
                line(ctx, [(0, 26 * s), (10, 26 * s)], panel, lw=0.35)
                p = self.fit("top", 16, 16, (62, 36 * s))
                if p:
                    checker(ctx, p[0], p[1], 13)
                self.label(ctx, "top", "07", (125, 22 * s), 8, rgb=self.c(0.35))
                self.label(ctx, "top", "NIE STAWAĆ", (95, 9 * s), 2.2, rgb=self.c(0.3), bold=False)
            poly(ctx, [(L - 100, -3), (L - 40, -3.5), (L - 40, 3.5), (L - 100, 3)], self.dots(0.45))
            ellipse(ctx, L - 72, 0, 22, 3.4, Dots(hx("#2f6aa8"), 0.42), stroke=self.c(0.4), lw=0.3)
            ellipse(ctx, L - 66, 1.0, 8, 1.0, hx("#ffffff"))
            poly(ctx, [(L - 34, -4.5), (L + 4, 0), (L - 34, 4.5)], self.dots(0.4))
        elif view == "bottom":
            fill(ctx, self.dots(0.06))
            for s in (1, -1):
                p = self.fit("bottom", 15, 15, (180, 28 * s))
                if p:
                    checker(ctx, p[0], p[1], 12)
                y, x0 = 14 * s, 205
                poly(ctx, [(x0, y - 1.4), (x0 + 50, y - 1.4), (x0 + 58, y), (x0 + 50, y + 1.4), (x0, y + 1.4)],
                     hx("#ffffff"), stroke=self.c(0.2), lw=0.3)
                poly(ctx, [(x0 + 50, y - 1.4), (x0 + 58, y), (x0 + 50, y + 1.4)], hx("#d4213d"))
                line(ctx, [(x0 + 2, y), (x0 - 5, y + 4 * s)], self.c(0.2), lw=0.3)
            line(ctx, [(60, 0), (L, 0)], panel, lw=0.2)
        else:
            u = -1 if view == "left" else 1
            fill(ctx, self.dots(0.12))
            line(ctx, [(150 * u, 4), (290 * u, 1.5)], hx("#d4213d"), lw=0.9)
            poly(ctx, [(150 * u, 1), (172 * u, 1), (172 * u, 5), (150 * u, 6)], self.dots(0.4), stroke=panel, lw=0.25)
            self.label(ctx, view, "07", (215 * u, 8), 6, rgb=self.c(0.35))
