import math
from base import Model
from model3d import Hinge


class Iskra(Model):
    """Szeroka delta z kartki w poziomie – szybka i prosta: rogi, boki, nos, na pół i gotowe."""
    slug = "iskra"
    name = "Iskra"
    W, H = 297.0, 210.0
    NOS = 19.0

    def build(self, s):
        W, H = self.W, self.H
        c = W / 2
        s.fold((c, H), (0, H - c), move=(0, H), text=("Połóż wydruk poziomo, nadrukiem do stołu, górną krawędzią od siebie. "
                                                     "Zegnij lewy górny róg do siebie tak, by górna krawędź legła na środku. "
                                                     "Na zaginanej części pojawi się linia 1."))
        s.fold((c, H), (W, H - c), move=(W, H), text="Tak samo zegnij prawy róg (linia 2).")
        x2 = H * math.tan(math.radians(22.5))
        s.fold((c, H), (c - x2, 0), move=(1, 150), text="Zegnij lewą skośną krawędź jeszcze raz do środka (linia 3).")
        s.fold((c, H), (c + x2, 0), move=(W - 1, 150), text="To samo po prawej (linia 4).")
        s.fold((0, H - self.NOS), (W, H - self.NOS), move=(c, H),
               text="Zegnij sam czubek nosa w dół, do siebie, wzdłuż krótkiej linii 5.")
        self.fold_half(s)

    def hinges(self):
        L = self.H - self.NOS
        return [Hinge((L - 27, 20), (0, 30.5), 90, "skrzydlo"),
                Hinge((50, 66), (0, 77), -90, "winglet")]

    # ------------------------------------------------------------------
    tagline = "Szeroka delta – złożysz ją w minutę"
    style = "realistyczny: samolot akrobacyjny z promieniami od nosa"
    fly = "Rzucaj płasko i średnio mocno. Leci szybko i prosto; podegnij tylne krawędzie, jeśli nurkuje."
    difficulty = 1
    inks = {"main": "#d62f3d"}

    def art(self, ctx, view, piece):
        import math
        from paint import hx, fill, poly, line, ellipse, checker, Dots
        L = self.H - self.NOS
        white = hx("#ffffff")
        fill(ctx, white)
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.5))
            return
        if view in ("top", "bottom"):
            cov = 0.62 if view == "top" else 0.4
            # promienie z punktu przed nosem, na przemian kolor i biel
            ox, oy = L + 40, 0
            for s in (1, -1):
                for k in range(5):
                    a0 = math.radians(158 + k * 5.2)
                    a1 = math.radians(158 + k * 5.2 + 2.9)
                    R = 400
                    poly(ctx, [(ox, oy), (ox + R * math.cos(a0), oy + s * R * math.sin(a0)),
                               (ox + R * math.cos(a1), oy + s * R * math.sin(a1))], self.dots(cov))
                # końcówki skrzydeł
                poly(ctx, [(-10, 64 * s), (60, 64 * s), (60, 100 * s), (-10, 100 * s)], self.dots(cov))
                line(ctx, [(-10, 64 * s), (60, 64 * s)], self.c(0.1), lw=0.6)
                p = self.fit(view, 15, 15, (95, 26 * s))
                if p:
                    checker(ctx, p[0], p[1], 12 if view == "top" else 10)
            poly(ctx, [(L - 24, -6.5), (L + 6, 0), (L - 24, 6.5)], self.dots(0.55, k=0.2))
            if view == "top":
                ellipse(ctx, L - 46, 0, 16, 3.2, Dots(hx("#2f6aa8"), 0.45), stroke=hx("#3b4552"), lw=0.3)
                ellipse(ctx, L - 42, 0.8, 6, 0.8, white)
                self.label(ctx, "top", "1", (40, 30), 9, rgb=self.c(0.3))
        else:
            u = -1 if view == "left" else 1
            line(ctx, [(20 * u, 3), (175 * u, 3)], self.c(), lw=1.6)
            line(ctx, [(20 * u, 5.5), (175 * u, 5.5)], self.c(), lw=0.5)
            self.label(ctx, view, "ISKRA", (110 * u, 12), 6, rgb=self.c(0.3))
