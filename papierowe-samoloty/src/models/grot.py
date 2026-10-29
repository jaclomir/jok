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
    style = "realistyczny: myśliwiec w cyfrowym kamuflażu"
    fly = "Rzucaj mocno i prosto, lekko w dół. Leci szybko i daleko – to klasyczna strzała."
    difficulty = 1
    inks = {"main": "#1f86d6"}

    def camo(self, ctx, bbox, seed):
        from paint import digital_camo, fill_geom
        lv = digital_camo(bbox, cell=3.0, seed=seed)
        tones = [self.dots(0.18), self.dots(0.42), self.dots(0.5, k=0.45), self.dots(0.55, k=0.75)]
        for g, t in zip(lv, tones):
            fill_geom(ctx, g, t)

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, ellipse, checker, Dots
        L = self.H
        white = hx("#ffffff")
        if view == "top":
            fill(ctx, self.dots(0.08))
            self.camo(ctx, (-10, -70, 300, 70), 3)
            for s in (1, -1):
                # jasne pasy od nosa do tylnej krawędzi
                for y_end, w in ((63, 7), (36, 6)):
                    poly(ctx, [(L - 40, 0.8 * s), (L - 44, 4 * s), (0, (y_end - w / 2) * s), (0, (y_end + w / 2) * s)],
                         self.dots(0.3))
                    line(ctx, [(L - 42, 2.4 * s), (0, y_end * s)], white, lw=0.6)
                p = self.fit("top", 16, 16, (55, 22 * s))
                if p:
                    checker(ctx, p[0], p[1], 12)
            # grot na nosie: dwa ciemne trójkąty
            poly(ctx, [(L - 62, 0), (L - 20, -9), (L - 20, 9)], self.dots(0.65, k=0.15))
            poly(ctx, [(L - 18, -6), (L + 4, 0), (L - 18, 6)], self.dots(0.7, k=0.2))
            ellipse(ctx, L - 88, 0, 18, 3, Dots(hx("#9fd2f5"), 0.55), stroke=white, lw=0.4)
        elif view == "bottom":
            fill(ctx, self.dots(0.06))
            self.camo(ctx, (-10, -70, 300, 70), 7)
            for s in (1, -1):
                p = self.fit("bottom", 15, 15, (180, 24 * s))
                if p:
                    checker(ctx, p[0], p[1], 11)
        else:
            u = -1 if view == "left" else 1
            fill(ctx, self.dots(0.08))
            self.camo(ctx, (-300, -10, 300, 60), 11 if u > 0 else 12)
            line(ctx, [(140 * u, 2.5), (290 * u, 0.6)], white, lw=1.4)
