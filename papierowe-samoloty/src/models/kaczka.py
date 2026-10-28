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
    tagline = "Odrzutowiec z przednimi skrzydełkami – stabilny i długo leci"
    style = "realistyczny: myśliwiec w układzie kaczki, dwubarwny kamuflaż"
    fly = "Rzucaj średnio mocno, poziomo. Przednie skrzydełka stabilizują lot – płynie długo i prosto."
    difficulty = 3
    inks = {"main": "#3d6a94"}

    def blob(self, ctx, pts, col):
        """Gładka plama kamuflażu przez zadane punkty (zamknięta krzywa)."""
        from paint import setc
        n = len(pts)
        ctx.new_path()
        mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)  # noqa: E731
        ctx.move_to(*mid(pts[-1], pts[0]))
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            m = mid(p, q)
            ctx.curve_to(p[0], p[1], p[0], p[1], m[0], m[1])
        ctx.close_path()
        setc(ctx, col)
        ctx.fill()

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, line, ellipse, checker, Dots
        L = 192.0
        panel = self.c(0.2)
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.22))
            return
        if view == "top":
            fill(ctx, self.dots(0.09))
            # dwubarwny kamuflaż: łagodne plamy w ciemniejszym odcieniu
            for s in (1, -1):
                self.blob(ctx, [(20, 8 * s), (70, 5 * s), (95, 22 * s), (60, 40 * s), (15, 36 * s)], self.dots(0.22))
                self.blob(ctx, [(110, 6 * s), (150, 8 * s), (140, 24 * s), (105, 30 * s)], self.dots(0.22))
                self.blob(ctx, [(5, 50 * s), (40, 52 * s), (30, 68 * s), (2, 66 * s)], self.dots(0.22))
                # krawędź natarcia, lotki, klapy
                line(ctx, [(L - 30, 4 * s), (2, 70 * s)], hx("#ffffff"), lw=0.8)
                line(ctx, [(9, 12 * s), (9, 64 * s)], panel, lw=0.3)
                for y in (12, 38, 64):
                    line(ctx, [(0, y * s), (9, y * s)], panel, lw=0.3)
                # przednie skrzydełka
                poly(ctx, [(L - 75, 22 * s), (L - 40, 22 * s), (L - 70, 60 * s), (L - 95, 60 * s)], self.dots(0.28),
                     stroke=panel, lw=0.3)
                p = self.fit("top", 14, 14, (55, 45 * s))
                if p:
                    checker(ctx, p[0], p[1], 11)
                self.label(ctx, "top", "21", (120, 32 * s), 7, rgb=self.c(0.4))
            # kabina na grzbiecie, ciemny stożek nosa i pas przeciwodblaskowy
            poly(ctx, [(L - 70, -2.6), (L - 22, -3), (L - 22, 3), (L - 70, 2.6)], self.dots(0.45))
            ellipse(ctx, L - 48, 0, 16, 3, Dots(hx("#2f6aa8"), 0.42), stroke=self.c(0.4), lw=0.3)
            ellipse(ctx, L - 44, 0.8, 6, 0.8, hx("#ffffff"))
            poly(ctx, [(L - 22, -7), (L + 6, 0), (L - 22, 7)], self.dots(0.5))
        elif view == "bottom":
            fill(ctx, self.dots(0.04))
            for s in (1, -1):
                p = self.fit("bottom", 13, 13, (110, 24 * s))
                if p:
                    checker(ctx, p[0], p[1], 10)
            # podwieszony zbiornik paliwa
            poly(ctx, [(95, -2), (150, -2), (158, 0), (150, 2), (95, 2)], hx("#ffffff"), stroke=panel, lw=0.3)
            poly(ctx, [(L - 22, -6), (L + 6, 0), (L - 22, 6)], self.dots(0.4))
        else:
            u = -1 if view == "left" else 1
            fill(ctx, self.dots(0.1))
            line(ctx, [(60 * u, 3), (180 * u, 3)], panel, lw=0.3)
            self.label(ctx, view, "21", (150 * u, 8), 5, rgb=self.c(0.4))
