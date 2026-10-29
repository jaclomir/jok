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
    style = "realistyczny: pokazowy myśliwiec z biało-czerwoną wstęgą"
    fly = "Rzucaj mocno i prosto, lekko w dół. Leci szybko i daleko – to klasyczna strzała."
    difficulty = 1
    inks = {"main": "#3b4b5e"}

    def ribbon(self, s):
        """Wstęga przez skrzydło: od grzbietu przy kabinie łukiem do końca skrzydła."""
        from paint import bez_pts
        return bez_pts((205, 1 * s), (150, 8 * s), (95, 52 * s), (20, 62 * s), 50)

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, ellipse, line, checker, band, offset_line, Dots
        L = self.H
        red = hx("#d4213d")
        white = hx("#ffffff")
        if view == "top":
            fill(ctx, self.dots(0.4))
            # jaśniejszy klin przy krawędzi natarcia (efekt światła)
            for s in (1, -1):
                poly(ctx, [(L, 0), (0, 63 * s), (0, 52 * s), (L - 30, 4 * s)], self.dots(0.26))
                r = self.ribbon(s)
                poly(ctx, band(r, 14, 9), white)
                line(ctx, offset_line(r, 3.2 * s), red, lw=2.2)
                line(ctx, offset_line(r, -5.6 * s), red, lw=0.6)
                line(ctx, offset_line(r, 6.4 * s), red, lw=0.6)
                # linie paneli, lotki
                for x in (60, 120, 230):
                    line(ctx, [(x, 2 * s), (x, 63 * (1 - x / L) * s)], self.c(0.35), lw=0.18)
                line(ctx, [(10, 22 * s), (10, 52 * s)], self.c(0.4), lw=0.35)
                line(ctx, [(0, 22 * s), (10, 22 * s)], self.c(0.4), lw=0.35)
                p = self.fit("top", 17, 17, (55, 40 * s))
                if p:
                    checker(ctx, p[0], p[1], 14)
            # kabina, pas przeciwodblaskowy, stożek nosa
            poly(ctx, [(L - 110, -3), (L - 38, -3.5), (L - 38, 3.5), (L - 110, 3)], self.dots(0.6, k=0.35))
            ellipse(ctx, L - 75, 0, 22, 3.4, Dots(hx("#5aa0d8"), 0.5), stroke=hx("#ffffff"), lw=0.4)
            ellipse(ctx, L - 69, 1.0, 8, 1.0, white)
            poly(ctx, [(L - 34, -4.5), (L + 4, 0), (L - 34, 4.5)], self.dots(0.55, k=0.3))
            poly(ctx, [(L - 12, -1.6), (L + 4, 0), (L - 12, 1.6)], red)
            for s in (1, -1):
                # czerwone końcówki skrzydeł
                for k in range(2):
                    line(ctx, [(0, (56 - k * 3.2) * s), (30, (53.6 - k * 3.2) * s)], red, lw=1.0)
        elif view == "bottom":
            fill(ctx, Dots(hx("#8d97a2"), 0.08))
            for s in (1, -1):
                p = self.fit("bottom", 16, 16, (180, 28 * s))
                if p:
                    checker(ctx, p[0], p[1], 12)
                y, x0 = 14 * s, 205
                poly(ctx, [(x0, y - 1.4), (x0 + 50, y - 1.4), (x0 + 58, y), (x0 + 50, y + 1.4), (x0, y + 1.4)],
                     white, stroke=self.c(0.2), lw=0.3)
                poly(ctx, [(x0 + 50, y - 1.4), (x0 + 58, y), (x0 + 50, y + 1.4)], red)
        else:
            u = -1 if view == "left" else 1
            fill(ctx, self.dots(0.36))
            line(ctx, [(140 * u, 3.5), (290 * u, 1.2)], white, lw=1.6)
            line(ctx, [(140 * u, 2.2), (290 * u, 0.5)], red, lw=0.6)
            poly(ctx, [(150 * u, 4.5), (172 * u, 4.5), (172 * u, 8), (150 * u, 9)], self.dots(0.5, k=0.3))
