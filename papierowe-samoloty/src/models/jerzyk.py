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
    style = "realistyczny: liniowiec fikcyjnych linii JERZYK"
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
        from paint import hx, fill, poly, rect, line, circle
        L = self.H - 90
        red, grey = hx("#e2434f"), hx("#9aa4b0")
        if piece.zone == "winglet":
            fill(ctx, hx("#ffffff"))
            u = -1 if view == "left" else 1
            rect(ctx, -400, 37, 400, 38.6, red)
            p = self.fit(view, 22, 16, (30 * u, 52))
            if p:
                self.swift(ctx, p[0] + 8 * u, p[1], 1.1 * u, self.dots(0.3), stroke=self.c())
            return
        if view == "top":
            fill(ctx, self.dots(0.06))
            for s in (1, -1):
                # krawędź natarcia z przednimi klapami, lotki i klapy na tylnej krawędzi
                line(ctx, [(L - 4, 1 * s), (L - 22, 92 * s)], hx("#ffffff"), lw=2.5)
                line(ctx, [(L - 10, 12 * s), (L - 26, 86 * s)], grey, lw=0.25)
                line(ctx, [(10, 6 * s), (10, 84 * s)], grey, lw=0.3)
                for y in (30, 52, 70):
                    line(ctx, [(0, y * s), (10, y * s)], grey, lw=0.3)
                rect(ctx, -10, min(87 * s, 90 * s), 200, max(87 * s, 90 * s), self.c())
            self.label(ctx, "top", "JERZYK", (50, 50), 8, rgb=self.c())
            self.label(ctx, "top", "SP-JRZ", (50, -50), 7, rgb=self.c(), bold=False)
        elif view == "bottom":
            fill(ctx, self.dots(0.03))
            self.label(ctx, "bottom", "SP-JRZ", (75, 40), 9, rgb=self.c(), bold=False)
            self.label(ctx, "bottom", "JERZYK", (75, -40), 9, rgb=self.c(), bold=False)
            for s in (1, -1):
                rect(ctx, -10, min(87 * s, 90 * s), 200, max(87 * s, 90 * s), self.c())
        else:
            u = -1 if view == "left" else 1
            fill(ctx, hx("#ffffff"))
            rect(ctx, -400, -2, 400, 5, self.dots(0.25))
            rect(ctx, -400, 5, 400, 6.4, self.c())
            rect(ctx, -400, 6.4, 400, 7.4, red)
            for k in range(14):
                x = (L - 18 - k * 5.8) * u
                if k in (0, 9):
                    line(ctx, [(x - 1.4, 10), (x - 1.4, 17.5), (x + 1.4, 17.5), (x + 1.4, 10), (x - 1.4, 10)], grey, lw=0.25)
                    continue
                circle(ctx, x, 13.5, 1.0, self.c(0.1))
            poly(ctx, [((L - 1) * u, 12.5), ((L - 8) * u, 12.5), ((L - 10) * u, 15.5), ((L - 2) * u, 15.5)], self.c(0.1))
            self.label(ctx, view, "JERZYK", (50 * u, 22), 5.5, rgb=self.c())
