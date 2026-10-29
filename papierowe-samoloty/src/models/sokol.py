from base import Model
from model3d import Hinge


class Sokol(Model):
    """Model z przednimi skrzydełkami (układ canard)."""
    slug = "sokol"
    half_flip = True
    name = "Sokół"

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
                   text=("Odegnij do siebie wystający róg klapki wzdłuż linii {n} – to przednie skrzydełko."
                         if st == 2 else "To samo z drugą klapką (linia {n}).").format(n=s.nstep + 1))

    def hinges(self):
        return [Hinge((192, 16.5), (0, 35), 90, "skrzydlo"),
                Hinge((79, 83.6), (0, 89.4), 90, "winglet")]

    # ------------------------------------------------------------------
    tagline = "Odrzutowiec z przednimi skrzydełkami – stabilny i długo leci"
    style = "realistyczny: myśliwiec w zielonym cyfrowym kamuflażu"
    fly = "Rzucaj średnio mocno, poziomo. Przednie skrzydełka stabilizują lot – płynie długo i prosto."
    difficulty = 3
    inks = {"main": "#4d7a35"}

    def camo(self, ctx, bbox, seed):
        from paint import digital_camo, fill_geom
        lv = digital_camo(bbox, cell=3.0, seed=seed, fracs=(0.45, 0.25, 0.14, 0.07))
        tones = [self.dots(0.2), self.dots(0.42), self.dots(0.48, k=0.45), self.dots(0.55, k=0.75)]
        for g, t in zip(lv, tones):
            fill_geom(ctx, g, t)

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, ellipse, Dots
        L = 192.0
        white = hx("#ffffff")
        sand = hx("#c9b37a")
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.5, k=0.5))
            return
        if view == "top":
            fill(ctx, Dots(sand, 0.18))
            self.camo(ctx, (-10, -70, 200, 70), 21)
            for s in (1, -1):
                # przednie skrzydełka: ciemne z białą krawędzią
                poly(ctx, [(L - 75, 22 * s), (L - 40, 22 * s), (L - 70, 60 * s), (L - 95, 60 * s)], self.dots(0.6, k=0.6),
                     stroke=white, lw=0.6)
                line(ctx, [(L - 30, 4 * s), (2, 70 * s)], white, lw=0.6)
            poly(ctx, [(L - 120, -3), (L - 22, -3.5), (L - 22, 3.5), (L - 120, 3)], self.dots(0.6, k=0.7))
            ellipse(ctx, L - 50, 0, 16, 3, Dots(hx("#e8b04a"), 0.55), stroke=white, lw=0.4)
            ellipse(ctx, L - 46, 0.8, 6, 0.8, white)
            poly(ctx, [(L - 22, -7), (L + 6, 0), (L - 22, 7)], self.dots(0.6, k=0.7))
        elif view == "bottom":
            fill(ctx, Dots(sand, 0.12))
            self.camo(ctx, (-10, -70, 200, 70), 33)
            poly(ctx, [(95, -2), (150, -2), (158, 0), (150, 2), (95, 2)], white, stroke=self.c(0.6), lw=0.3)
        else:
            fill(ctx, Dots(sand, 0.18))
            self.camo(ctx, (-300, -10, 300, 60), 41)
