from base import Model
from model3d import Hinge
from models.mops import waterbomb


class Trzmiel(Model):
    """Krótki, krępy model w kształcie trapezu z dużymi wingletami."""
    slug = "trzmiel"
    half_flip = True
    name = "Trzmiel"

    def build(self, s):
        W, H = self.W, self.H
        wb = waterbomb(s, W, H, "Złóż „bombę wodną”: zegnij górę w dół po poziomej linii 2 i jednocześnie wepchnij boki do środka po przekątnych. Powstaje trójkątny daszek.")
        c, yb, yc = wb.c, wb.yb, wb.yc
        yn = yc - 65
        s.fold((0, yn), (W, yn), move=(c, yc), text="Zegnij czubek daszka w dół, do siebie, wzdłuż linii 3. Czubek wystaje poza daszek – tak ma być.")
        nose = s.nstep
        sel = lambda f: wb.flap(f) and nose not in f.tag.get("moves", ())
        s.fold((39, yb), (39, yb + 60), move=(1, yb + 1), select=sel, text="Zegnij lewą klapkę daszka do środka wzdłuż pionowej linii 4.")
        s.fold((W - 39, yb), (W - 39, yb + 60), move=(W - 1, yb + 1), select=sel, text="To samo z prawą klapką (linia 5).")
        self.fold_half(s)

    def hinges(self):
        return [Hinge((200, 19.5), (0, 19.5), 90, "skrzydlo"),
                Hinge((127, 65), (35, 104), -90, "winglet")]

    # ------------------------------------------------------------------
    tagline = "Krępy trapez z wielkimi wingletami"
    style = "kreskówkowy: puchaty trzmiel"
    fly = "Rzucaj spokojnie i poziomo. Duże winglety trzymają kurs – dobry na pierwsze zawody na odległość."
    difficulty = 3

    def art(self, ctx, view, piece):
        import random
        from paint import hx, fill, poly, rect, line, text, circle, ellipse, curve
        L = 127.0
        yel, blk = hx("#ffcc29"), hx("#231f20")
        if piece.zone == "winglet":
            # skrzydełka owada: półprzezroczysty błękit z żyłkami
            fill(ctx, hx("#d7f0fb"))
            u = -1 if view == "left" else 1
            for k in range(6):
                curve(ctx, (-300, 20 + k * 9), (-100, 30 + k * 8), (100, 22 + k * 9), (300, 30 + k * 8),
                      hx("#7fb7d1"), lw=0.35)
            for x in range(-140, 141, 14):
                line(ctx, [(x, 0), (x + 6, 120)], hx("#7fb7d1"), lw=0.3)
            return
        if view in ("top", "left", "right"):
            fill(ctx, yel)
            if view == "top":
                stripes = [(8, 22), (36, 50), (64, 78)]
                for x0, x1 in stripes:
                    rect(ctx, x0, -100, x1, 100, blk)
                rnd = random.Random(3)
                for _ in range(500):
                    x, y = rnd.uniform(0, L), rnd.uniform(-85, 85)
                    line(ctx, [(x, y), (x + rnd.uniform(-1, 1), y + rnd.uniform(-1, 1))], hx("#000000", 0.12),
                         lw=0.35)
                # głowa
                ellipse(ctx, L - 6, 0, 22, 30, blk)
                for s in (1, -1):
                    ellipse(ctx, L - 12, 14 * s, 7, 9, hx("#ffffff"), rot=20 * s)
                    circle(ctx, L - 10, 15 * s, 4, blk)
                    circle(ctx, L - 9, 16 * s, 1.3, hx("#ffffff"))
                    curve(ctx, (L - 26, 6 * s), (L - 32, 18 * s), (L - 26, 34 * s), (L - 16, 40 * s), blk, lw=1.1)
                    circle(ctx, L - 16, 40 * s, 2.3, blk)
                # uśmiech
                curve(ctx, (L - 2, -6), (L + 2, -2), (L + 2, 2), (L - 2, 6), hx("#ffcc29"), lw=0.9)
                text(ctx, "BZZ!", 30, 60, 6, rgb=blk)
                text(ctx, "BZZ!", 30, -60, 6, rgb=blk)
            else:
                u = -1 if view == "left" else 1
                X = lambda x: x * u
                for x0, x1 in [(8, 22), (36, 50), (64, 78)]:
                    rect(ctx, min(X(x0), X(x1)), -5, max(X(x0), X(x1)), 60, blk)
                ellipse(ctx, X(L - 6), 10, 18, 16, blk)
        else:
            fill(ctx, blk)
            for s in (1, -1):
                for k in range(3):
                    line(ctx, [(L - 30 + k * 6, 12 * s), (L - 40 + k * 6, 26 * s)], yel, lw=0.9)
