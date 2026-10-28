from base import Model
from model3d import Hinge


class Kaczka(Model):
    """Model z przednimi lotkami (kaczka/canard)."""
    slug = "kaczka"
    half_flip = True
    name = "Kaczka"

    def build(self, s):
        W, H = self.W, self.H
        c = W / 2
        y1 = 192
        s.fold((0, y1), (W, y1), move=(c, H), text="Połóż wydruk nadrukiem do stołu, górną krawędzią od siebie (jak na rysunku obok). Zegnij górny pas (ok. 10 cm) w dół, do siebie, wzdłuż linii 1.")
        # linia z krawędzi zgięcia (17 mm od środka) do dolnej krawędzi pasa (35 mm od boku)
        y0 = y1 - (H - y1)
        s.fold((c + 16.5, y1), (W - 35, y0), move=(W - 1, y1 - 1), text="Zegnij prawy górny róg skośnie w dół wzdłuż linii 2. Zgięcie zaczyna się ok. 1,5 cm od środka górnej krawędzi.")
        s.fold((c - 16.5, y1), (35, y0), move=(1, y1 - 1), text="To samo z lewym rogiem (linia 3). Lewa klapka zachodzi na prawą.")
        self.canard(s)
        self.fold_half(s)

    def canard(self, s):
        # linia 4: na kartce od (56,4; 192) do (0; 92) i lustrzanie
        for (p1, p2), corner, st in ((((56.4, 192), (0, 92)), (0.5, 191), 2), (((210 - 56.4, 192), (210, 92)), (209.5, 191), 3)):
            a = s.paper_to_flat(*p1)
            b = s.paper_to_flat(*p2)
            mv = s.paper_to_flat(*corner)
            s.fold(a, b, move=mv, select=lambda f, st=st: st in f.tag.get("moves", ()),
                   text=("Odegnij do siebie wystający róg klapki wzdłuż linii {n} – to przednie skrzydełko „kaczki”."
                         if st == 2 else "To samo z drugą klapką (linia {n}).").format(n=s.nstep + 1))

    def hinges(self):
        return [Hinge((192, 16.5), (0, 35), 90, "skrzydlo"),
                Hinge((79, 83.6), (0, 89.4), 90, "winglet")]

    # ------------------------------------------------------------------
    tagline = "Kaczka z przednimi skrzydełkami – stabilna i zabawna"
    style = "kreskówkowy: kaczątko"
    fly = "Rzucaj średnio mocno, poziomo. Przednie skrzydełka stabilizują lot – płynie długo i prosto."
    difficulty = 3
    inks = {"main": "#f2b705"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, circle, ellipse, curve, feat, Dots
        L = 192.0
        ora = hx("#f07a1a")
        beak = Dots(ora, 0.24)
        fill(ctx, self.dots(0.08))
        if piece.zone == "winglet":
            for k in range(4):
                line(ctx, [(-300, 4 + k * 3), (300, 4 + k * 3)], self.c(0.35), lw=0.3)
            return
        if view == "top":
            for s in (1, -1):
                for row, x0 in enumerate((2, 17)):
                    for k in range(8):
                        y = (10 + k * 9 + row * 4.5) * s
                        ellipse(ctx, x0 + 9, y, 10, 4.6, self.dots(0.13), stroke=self.c(0.35), lw=0.35)
                for k in range(7):
                    curve(ctx, (55 + k * 15, 18 * s), (60 + k * 15, 23 * s), (64 + k * 15, 23 * s), (69 + k * 15, 18 * s),
                          self.c(0.35), lw=0.35)
                poly(ctx, [(L - 75, 22 * s), (L - 40, 22 * s), (L - 70, 60 * s), (L - 95, 60 * s)], beak, stroke=ora, lw=0.4)
            poly(ctx, [(L - 22, -8), (L + 6, 0), (L - 22, 8)], beak, stroke=ora, lw=0.5)
            line(ctx, [(L - 20, 0), (L + 2, 0)], ora, lw=0.4)
            for s in (1, -1):
                p = self.fit("top", 11, 11, (L - 36, 11 * s))
                if p:
                    circle(ctx, p[0], p[1], 4.6, hx("#ffffff"), stroke=hx("#333333"), lw=0.4)
                    circle(ctx, p[0] + 1.3, p[1] + 0.4 * s, 2.2, hx("#2a2a2a"))
                    circle(ctx, p[0] + 2.1, p[1] + 1.1 * s, 0.7, hx("#ffffff"))
                    feat(ctx, "oko", p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5)
                    circle(ctx, p[0] - 2, p[1] + 9 * s, 2.6, Dots(hx("#ef6f8f"), 0.35))
        elif view == "bottom":
            fill(ctx, self.dots(0.05))
            for s in (1, -1):
                p = self.fit("bottom", 16, 16, (100, 25 * s))
                if p:
                    x, y = p
                    poly(ctx, [(x + 6, y), (x - 6, y - 6 * s), (x - 3, y), (x - 6, y + 6 * s)], beak, stroke=ora, lw=0.4)
                    feat(ctx, "łapka", x - 7, y - 7, x + 7, y + 7)
            poly(ctx, [(L - 22, -7), (L + 6, 0), (L - 22, 7)], beak)
        else:
            u = -1 if view == "left" else 1
            for k in range(4):
                ellipse(ctx, (75 + k * 16) * u, 9, 8, 3.4, self.dots(0.22), stroke=self.c(0.35), lw=0.3)
