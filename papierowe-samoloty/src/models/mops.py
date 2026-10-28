from base import Model
from model3d import Hinge


class WB:
    """Geometria „bomby wodnej” w górnym kwadracie kartki (współrzędne kartki)."""

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.c, self.yb, self.yc = W / 2, H - W, H - W / 2

    def lower(self, f):
        p = f.c
        return p.y < self.yb + 0.01 or (p.y < self.H - p.x and p.y < self.yb + p.x)

    def flap(self, f):
        return not self.lower(f)


def waterbomb(s, W, H, text):
    wb = WB(W, H)
    c, yb, yc = wb.c, wb.yb, wb.yc
    s.fold((0, H), (W, yb), move=(0, yb), unfold=True, text="Połóż wydruk nadrukiem do stołu, górną krawędzią od siebie (jak na rysunku obok). Zagnij i rozłóż obie przekątne górnego kwadratu (linie 1): prawy górny róg do lewej krawędzi, rozłóż, potem lewy róg do prawej.")
    s.fold((W, H), (0, yb), move=(W, yb), unfold=True, record=False)
    s.fold((0, yc), (W, yc), move=(c, H), text=text)
    top = [f for f in s.facets if f.c.y > yc]
    bot = [f for f in s.facets if f.c.y < yc]
    zt = min(f.z for f in top) - 0.3
    zb = max(f.z for f in bot) + 0.3
    for a, b, mv in (((c, yc), (0, yb), (1, yc - 1)), ((c, yc), (W, yb), (W - 1, yc - 1))):
        s.fold(a, b, move=mv, mode="mountain", select=lambda f: f.c.y > yc, z=zt, record=False)
        s.fold(a, b, move=mv, mode="valley", select=lambda f: f.c.y < yc, z=zb, record=False)
    return wb


class Mops(Model):
    """Tępy nos z zamkiem – stabilny w domu."""
    slug = "mops"
    half_flip = True
    name = "Mops"

    def build(self, s):
        W, H = self.W, self.H
        wb = waterbomb(s, W, H, "Złóż „bombę wodną”: zegnij górę w dół po poziomej linii 2 i jednocześnie wepchnij boki do środka po przekątnych. Powstaje trójkątny daszek.")
        c, yb, yc = wb.c, wb.yb, wb.yc
        yn = yc - 54
        s.fold((0, yn), (W, yn), move=(c, yc), text="Zegnij czubek daszka w dół, do siebie, wzdłuż linii 3 – to tępy nos.")
        nose = s.nstep
        nz = min(f.z for f in s.facets if nose in f.tag.get("moves", ())) - 0.5
        sel = lambda f: wb.flap(f) and nose not in f.tag.get("moves", ())
        s.fold((58.3, yb), (42.8, yb + 43), move=(1, yb + 1), select=sel, z=nz,
               text="Zegnij lewą klapkę daszka do środka wzdłuż linii 4 i wsuń jej czubek pod zagięty nos.")
        s.fold((W - 58.3, yb), (W - 42.8, yb + 43), move=(W - 1, yb + 1), select=sel, z=nz,
               text="To samo z prawą klapką (linia 5).")
        self.fold_half(s)

    def hinges(self):
        return [Hinge((200, 22), (0, 22), 90, "skrzydlo"),
                Hinge((200, 89), (0, 89), -90, "winglet")]

    # ------------------------------------------------------------------
    tagline = "Tępy nos z zamkiem – stabilny lot w domu"
    style = "kreskówkowy: mops z obrożą"
    fly = "Rzucaj delikatnie przed siebie. Ciężki, zablokowany nos daje bardzo stabilny lot w pokoju."
    difficulty = 3
    inks = {"main": "#b27a4b"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, circle, ellipse, curve, feat, Dots
        L = 138.0
        dark = hx("#3b2a1e")
        fill(ctx, self.dots(0.1))
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.32))
            for k in range(3):
                line(ctx, [(-300, 54 + k * 6), (300, 54 + k * 6)], self.c(0.3), lw=0.35)
            return
        if view == "top":
            for s in (1, -1):
                for k in range(3):
                    curve(ctx, (L - 44 - k * 5, 8 * s), (L - 48 - k * 5, 14 * s), (L - 48 - k * 5, 20 * s),
                          (L - 44 - k * 5, 26 * s), self.c(0.2), lw=0.5)
                p = self.fit("top", 14, 14, (9, 48 * s))
                if p:
                    x, y = p
                    circle(ctx, x - 1, y, 3.4, self.dots(0.3), stroke=self.c(0.3), lw=0.4)
                    for k in (-1, 0, 1):
                        circle(ctx, x + 4.2, y + k * 3.2, 1.3, self.dots(0.3), stroke=self.c(0.3), lw=0.3)
                    feat(ctx, "łapka", x - 5, y - 5, x + 6, y + 5)
                poly(ctx, [(L - 40, 30 * s), (L - 20, 37 * s), (L - 35, 52 * s)], self.dots(0.35), stroke=self.c(0.35), lw=0.4)
                p = self.fit("top", 13, 13, (L - 22, 14 * s))
                if p:
                    circle(ctx, p[0], p[1], 5.6, hx("#ffffff"), stroke=dark, lw=0.5)
                    circle(ctx, p[0] + 1.4, p[1], 3.4, dark)
                    circle(ctx, p[0] + 2.4, p[1] + 1.0 * s, 1.0, hx("#ffffff"))
                    feat(ctx, "oko", p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6)
            ellipse(ctx, L - 4, 0, 18, 12, self.dots(0.36, k=0.3), stroke=self.c(0.4), lw=0.4)
            ellipse(ctx, L - 3, 0, 3.4, 5.5, dark)
            rect(ctx, L - 56, -70, L - 52.5, 70, hx("#e2434f"))
            ellipse(ctx, L - 54, 0, 3.4, 3.4, hx("#f7d77a"), stroke=hx("#b8860b"), lw=0.3)
            curve(ctx, (3, 2), (14, 12), (20, -6), (8, -4), self.c(0.2), lw=1.0)
        elif view == "bottom":
            fill(ctx, self.dots(0.06))
            ellipse(ctx, L - 15, 0, 7, 4.4, Dots(hx("#ef6f8f"), 0.45), stroke=hx("#d4506a"), lw=0.35)
            line(ctx, [(L - 20, 0), (L - 10, 0)], hx("#d4506a"), lw=0.35)
        else:
            u = -1 if view == "left" else 1
            ellipse(ctx, (L - 6) * u, 9, 12, 10, self.dots(0.36, k=0.3), stroke=self.c(0.4), lw=0.4)
            rect(ctx, min((L - 56) * u, (L - 52.5) * u), -5, max((L - 56) * u, (L - 52.5) * u), 60, hx("#e2434f"))
