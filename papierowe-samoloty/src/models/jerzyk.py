from base import Model
from model3d import Hinge


class Jerzyk(Model):
    """Szybowiec z ciężkim, zwiniętym nosem – do latania na dworze."""
    slug = "jerzyk"
    half_flip = True
    name = "Jerzyk"
    W, H = 297.0, 210.0

    def build(self, s):
        W, H = self.W, self.H
        c = W / 2
        s.fold((c - 14, H), (0, H - 200), move=(0, H), text="Połóż wydruk poziomo, nadrukiem do stołu, górną krawędzią od siebie. Zegnij lewy górny róg do siebie wzdłuż długiej, płaskiej linii 1. Róg zajdzie trochę za środek kartki.")
        s.fold((c + 14, H), (W, H - 200), move=(W, H), text="Tak samo zegnij prawy róg (linia 2) – zachodzi na lewy.")
        for i, d in enumerate((30, 60, 90)):
            s.fold((0, H - d), (W, H - d), move=(c, H), text=["Zwiń nos w dół, do siebie, wzdłuż linii 3 (3 cm od czubka).", "Zwiń nos jeszcze raz, wzdłuż linii 4.", "I trzeci raz, wzdłuż linii 5. Nos jest teraz gruby i ciężki – tak ma być."][i])
        self.fold_half(s)

    def hinges(self):
        return [Hinge((self.H - 90, 25), (0, 35), 90, "skrzydlo"),
                Hinge((60, 124), (0, 127), -90, "winglet")]

    # ------------------------------------------------------------------
    tagline = "Szybowiec z ciężkim nosem – do latania na dworze"
    style = "realistyczny: liniowiec z łukiem barw na skrzydłach"
    fly = "Na dworze: rzuć mocno do góry, zakręci i zejdzie długim, spokojnym ślizgiem. W domu – lekko, poziomo."
    difficulty = 2
    inks = {"main": "#1f3566"}

    def swift(self, ctx, x, y, s, col, stroke=None):
        """Sylwetka jerzyka (logo fikcyjnej linii)."""
        from paint import poly, feat
        pts = [(0, 0), (-6, 1.2), (-14, 7), (-9, 1.3), (-16, -1), (-9, -1.5), (-14, -7), (-6, -1.2)]
        poly(ctx, [(x + px * s, y + py * s) for px, py in pts], col, stroke=stroke, lw=0.3)
        feat(ctx, "logo", x - 16 * abs(s), y - 7 * abs(s), x + 1 * abs(s), y + 7 * abs(s))

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, circle, band, bez_pts
        L = self.H - 90
        red, grey = hx("#e2434f"), hx("#9aa4b0")
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.12))
            u = -1 if view == "left" else 1
            rect(ctx, -400, 34, 400, 40, self.dots(0.6))
            rect(ctx, -400, 40, 400, 41.2, red)
            p = self.fit(view, 22, 16, (30 * u, 54))
            if p:
                self.swift(ctx, p[0] + 8 * u, p[1], 1.1 * u, hx("#ffffff"), stroke=self.c())
            return
        if view in ("top", "bottom"):
            fill(ctx, self.dots(0.06 if view == "top" else 0.03))
            for s in (1, -1):
                # łuk barw linii przechodzący w końcówkę skrzydła
                a = bez_pts((-10, 58 * s), (40, 60 * s), (80, 72 * s), (120, 96 * s), 40)
                poly(ctx, band(a, 10, 16), self.dots(0.55 if view == "top" else 0.4))
                b = bez_pts((-10, 50 * s), (40, 52 * s), (85, 66 * s), (125, 92 * s), 40)
                poly(ctx, band(b, 1.6), red)
                rect(ctx, -10, min(84 * s, 100 * s), 200, max(84 * s, 100 * s), self.dots(0.55 if view == "top" else 0.4))
                if view == "top":
                    line(ctx, [(L - 4, 1 * s), (L - 22, 92 * s)], hx("#ffffff"), lw=2.5)
                    line(ctx, [(L - 10, 12 * s), (L - 26, 86 * s)], grey, lw=0.25)
                    line(ctx, [(10, 6 * s), (10, 46 * s)], grey, lw=0.3)
                    for y in (6, 26, 46):
                        line(ctx, [(0, y * s), (10, y * s)], grey, lw=0.3)
                    for y in (16, 34):
                        line(ctx, [(10, y * s), (22, y * s)], grey, lw=0.6)
        else:
            u = -1 if view == "left" else 1
            fill(ctx, hx("#ffffff"))
            rect(ctx, -400, -2, 400, 5, self.dots(0.35))
            rect(ctx, -400, 5, 400, 6.4, self.c())
            rect(ctx, -400, 6.4, 400, 7.4, red)
            for k in range(14):
                x = (L - 18 - k * 5.8) * u
                if k in (0, 9):
                    line(ctx, [(x - 1.4, 10), (x - 1.4, 17.5), (x + 1.4, 17.5), (x + 1.4, 10), (x - 1.4, 10)], grey, lw=0.25)
                    continue
                circle(ctx, x, 13.5, 1.0, self.c(0.1))
            poly(ctx, [((L - 1) * u, 12.5), ((L - 8) * u, 12.5), ((L - 10) * u, 15.5), ((L - 2) * u, 15.5)], self.c(0.1))
