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
    style = "kreskówkowy: żółte kaczątko"
    fly = "Rzucaj średnio mocno, poziomo. Przednie skrzydełka stabilizują lot – płynie długo i prosto."
    difficulty = 3

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, text, circle, ellipse, curve, rgrad, paint_src
        L = 192.0
        yel, yel2, ora = hx("#ffd23f"), hx("#f4b400"), hx("#ff8c1a")
        if piece.zone == "winglet":
            fill(ctx, ora)
            return
        if view == "top":
            fill(ctx, yel)
            # pióra na tylnej krawędzi skrzydeł
            for s in (1, -1):
                for row, (x0, col) in enumerate(((0, yel2), (16, hx("#ffc61a")))):
                    for k in range(9):
                        y = (8 + k * 9) * s
                        ellipse(ctx, x0 + 8, y, 12, 5.5, col, stroke=hx("#e09b00"), lw=0.3)
                # kropki-piórka na skrzydle
                for k in range(6):
                    curve(ctx, (60 + k * 14, 20 * s), (66 + k * 14, 26 * s), (70 + k * 14, 26 * s),
                          (74 + k * 14, 20 * s), hx("#e09b00"), lw=0.5)
            # dziób
            poly(ctx, [(L - 22, -9), (L + 6, 0), (L - 22, 9)], ora, stroke=hx("#d66a00"), lw=0.4)
            line(ctx, [(L - 20, 0), (L + 4, 0)], hx("#d66a00"), lw=0.5)
            # oczy
            for s in (1, -1):
                circle(ctx, L - 34, 9 * s, 5.5, hx("#ffffff"), stroke=hx("#333333"), lw=0.4)
                circle(ctx, L - 32.5, 9.5 * s, 2.6, hx("#222222"))
                circle(ctx, L - 31.6, 10.4 * s, 0.9, hx("#ffffff"))
            # przednie skrzydełka (kaczka) – pomarańczowe
            for s in (1, -1):
                poly(ctx, [(L - 75, 22 * s), (L - 40, 22 * s), (L - 70, 60 * s), (L - 95, 60 * s)], ora)
        elif view == "bottom":
            fill(ctx, hx("#fff3c4"))
            for s in (1, -1):
                circle(ctx, 60, 25 * s, 6, ora)
                for k in (-1, 0, 1):
                    line(ctx, [(60, 25 * s), (52 + 0, (25 + 6 * k) * s)], hx("#d66a00"), lw=0.6)
            poly(ctx, [(L - 22, -8), (L + 6, 0), (L - 22, 8)], ora)
        else:
            u = -1 if view == "left" else 1
            X = lambda x: x * u
            fill(ctx, yel)
            # policzek i oko z boku
            circle(ctx, X(L - 30), 6, 3.5, hx("#ff9eaa", 0.7))
            # dziób z boku
            poly(ctx, [(X(L - 18), 3), (X(L + 5), 1), (X(L - 18), 10)], ora)
            # skrzydełko złożone
            for k in range(5):
                ellipse(ctx, X(60 + k * 15), 10, 9, 4, yel2, stroke=hx("#e09b00"), lw=0.3)
            text(ctx, "KWA!", X(120), 18, 6, rgb=hx("#d66a00"))
