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

    def swift(self, ctx, x, y, s, col):
        """Sylwetka jerzyka (logo)."""
        from paint import poly
        pts = [(0, 0), (-6, 1.2), (-14, 7), (-9, 1.3), (-16, -1), (-9, -1.5), (-14, -7), (-6, -1.2)]
        poly(ctx, [(x + px * s, y + py * s) for px, py in pts], col)

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, text, circle, lgrad, paint_src
        L = self.H - 90
        navy, red, grey = hx("#14213d"), hx("#e63946"), hx("#dfe3e8")
        if piece.zone == "winglet":
            fill(ctx, navy)
            u = -1 if view == "left" else 1
            self.swift(ctx, (60 if u > 0 else -45), 52, 1.3 * u, hx("#ffffff"))
            rect(ctx, -400, 36, 400, 38, red)
            return
        if view == "top":
            fill(ctx, grey)
            for s in (1, -1):
                # ścieżka chodnika na skrzydle i krawędzie
                line(ctx, [(20, 8 * s), (80, 8 * s), (80, 30 * s), (20, 30 * s), (20, 8 * s)], hx("#7f8a96"),
                     lw=0.35, dash=[2, 1.5])
                line(ctx, [(L + 2, 0), (L - 20, 93 * s)], hx("#b8bec6"), lw=4)
                for k in range(4):
                    line(ctx, [(4, (25 + 18 * k) * s), (4, (40 + 18 * k) * s)], hx("#8d99a6"), lw=0.35)
                rect(ctx, -10, min(84 * s, 96 * s), 200, max(84 * s, 96 * s), navy)
            text(ctx, "JERZYK", 50, 52, 9, rgb=navy)
            text(ctx, "SP-JRZ", 50, -52, 9, rgb=navy)
            rect(ctx, -10, -3, 200, 3, hx("#ffffff"))
        elif view == "bottom":
            fill(ctx, hx("#f4f5f7"))
            text(ctx, "SP-JRZ", 66, 40, 12, rgb=navy)
            text(ctx, "JERZYK", 66, -40, 12, rgb=navy)
            for s in (1, -1):
                rect(ctx, -10, min(84 * s, 96 * s), 200, max(84 * s, 96 * s), navy)
        else:
            u = -1 if view == "left" else 1
            X = lambda x: x * u
            fill(ctx, hx("#ffffff"))
            # granatowy brzuch i czerwona linia
            rect(ctx, -400, -2, 400, 9, navy)
            rect(ctx, -400, 9, 400, 11, red)
            # okna
            for k in range(14):
                x = X(L - 20 - k * 6.2)
                if k in (0, 9):
                    rect(ctx, x - 1.6, 13, x + 1.6, 22, hx("#9aa5b1"))
                    continue
                circle(ctx, x, 17.5, 1.25, hx("#1d3557"))
            # kokpit
            poly(ctx, [(X(L - 2), 16), (X(L - 9), 16), (X(L - 11), 19.5), (X(L - 3), 19.5)], hx("#1d3557"))
            text(ctx, "JERZYK", X(55), 27, 7, rgb=navy)
            self.swift(ctx, X(90), 27, 0.75 * u, red)
            text(ctx, "SP-JRZ", X(22), 13.5, 2.6, rgb=navy, bold=False)
