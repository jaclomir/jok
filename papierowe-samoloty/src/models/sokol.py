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
    style = "realistyczny: myśliwiec w tygrysim malowaniu pokazowym"
    fly = "Rzucaj średnio mocno, poziomo. Przednie skrzydełka stabilizują lot – płynie długo i prosto."
    difficulty = 3
    inks = {"main": "#ef7d1a"}

    def stripes(self, ctx, s, x0, x1, ymax, seed, col):
        """Tygrysie pręgi: zwężające się klinowate pasy od krawędzi spływu do przodu."""
        import random
        from paint import poly, bez_pts
        rnd = random.Random(seed)
        y = 6
        while y < ymax:
            w = rnd.uniform(3.0, 5.0)
            ln = rnd.uniform(28, 55)
            bend = rnd.uniform(-6, 6)
            xa = x0 + rnd.uniform(-4, 10)
            top = bez_pts((xa, y), (xa + ln * 0.4, y + bend), (xa + ln * 0.7, y + bend * 0.6 + w * 0.3), (xa + ln, y + w * 0.4), 16)
            bot = bez_pts((xa + ln, y + w * 0.4), (xa + ln * 0.7, y + w * 0.9), (xa + ln * 0.4, y + w + bend), (xa, y + w), 16)
            poly(ctx, [(px, py * s) for px, py in top + bot], col)
            y += w + rnd.uniform(4.5, 8.0)

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, ellipse, Dots
        L = 192.0
        black = Dots(hx("#1d1a18"), 0.62)
        white = hx("#ffffff")
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.42))
            for k in range(3):
                poly(ctx, [(-300, 4 + k * 6), (300, 6 + k * 6), (300, 8 + k * 6), (-300, 6.5 + k * 6)], black)
            return
        if view == "top":
            fill(ctx, self.dots(0.34))
            for s in (1, -1):
                self.stripes(ctx, s, 0, 0, 66, 11, black)
                self.stripes(ctx, s, 70, 0, 36, 23, black)
                # przednie skrzydełka: biel z czarną krawędzią
                poly(ctx, [(L - 75, 22 * s), (L - 40, 22 * s), (L - 70, 60 * s), (L - 95, 60 * s)], white,
                     stroke=hx("#1d1a18"), lw=0.5)
                for k in range(2):
                    line(ctx, [(L - 84 + k * 8, 50 * s), (L - 66 + k * 8, 30 * s)], self.c(), lw=1.6)
                line(ctx, [(L - 30, 4 * s), (2, 70 * s)], white, lw=0.7)
                self.label(ctx, "top", "TIGER", (128, 30 * s), 4.5, rgb=hx("#1d1a18"))
            # grzbiet: czarny pas z kabiną, nos w kolorze
            poly(ctx, [(L - 120, -3), (L - 22, -3.5), (L - 22, 3.5), (L - 120, 3)], black)
            ellipse(ctx, L - 50, 0, 16, 3, Dots(hx("#5aa0d8"), 0.5), stroke=white, lw=0.4)
            ellipse(ctx, L - 46, 0.8, 6, 0.8, white)
            poly(ctx, [(L - 22, -7), (L + 6, 0), (L - 22, 7)], self.dots(0.5, k=0.25))
        elif view == "bottom":
            fill(ctx, self.dots(0.08))
            for s in (1, -1):
                self.stripes(ctx, s, 60, 0, 40, 5, Dots(hx("#1d1a18"), 0.35))
            poly(ctx, [(95, -2), (150, -2), (158, 0), (150, 2), (95, 2)], white, stroke=hx("#1d1a18"), lw=0.3)
            poly(ctx, [(L - 22, -6), (L + 6, 0), (L - 22, 6)], self.dots(0.4))
        else:
            u = -1 if view == "left" else 1
            fill(ctx, self.dots(0.4))
            for k in range(6):
                x = (70 + k * 17) * u
                poly(ctx, [(x, -2), (x + 4 * u, -2), (x + 10 * u, 14), (x + 7 * u, 14)], black)
            self.label(ctx, view, "21", (160 * u, 8), 5, rgb=hx("#1d1a18"))
