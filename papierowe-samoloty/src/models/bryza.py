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


class Bryza(Model):
    """Tępy nos z zamkiem – stabilny w domu."""
    slug = "bryza"
    half_flip = True
    name = "Bryza"

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
    style = "realistyczny: samolot akrobacyjny w klasyczne promienie"
    fly = "Rzucaj delikatnie przed siebie. Ciężki, zablokowany nos daje bardzo stabilny lot w pokoju."
    difficulty = 3
    inks = {"main": "#1d8fa8"}

    def art(self, ctx, view, piece):
        import math
        from paint import hx, fill, poly, rect, line, ellipse, Dots
        L = 138.0
        white, navy, red = hx("#ffffff"), hx("#22324f"), hx("#e2434f")
        if piece.zone == "winglet":
            fill(ctx, Dots(navy, 0.5))
            line(ctx, [(-300, 40), (300, 40)], white, lw=1.2)
            return
        if view in ("top", "bottom"):
            top = view == "top"
            fill(ctx, white)
            cov = 0.55 if top else 0.4
            cx = L - 6
            for s in (1, -1):
                # promienie od nosa przez całe skrzydło, na przemian kolor / biel
                n = 9
                a0, a1 = math.radians(180), math.radians(180 - 62 * s)
                for k in range(0, n, 2):
                    pa = a0 + (a1 - a0) * k / n
                    pb = a0 + (a1 - a0) * (k + 1) / n
                    poly(ctx, [(cx, 0), (cx + 300 * math.cos(pa), 300 * math.sin(pa) * -1 * -1),
                               (cx + 300 * math.cos(pb), 300 * math.sin(pb))], self.dots(cov))
                # granatowe końcówki skrzydeł z czerwoną linią
                poly(ctx, [(-10, 80 * s), (L + 10, 80 * s), (L + 10, 110 * s), (-10, 110 * s)], Dots(navy, cov))
                line(ctx, [(-10, 78.5 * s), (L + 10, 78.5 * s)], red, lw=1.0)
            # granatowa krawędź natarcia z czerwoną linią
            rect(ctx, L - 7, -110, L + 10, 110, Dots(navy, cov))
            line(ctx, [(L - 8.5, -110), (L - 8.5, 110)], red, lw=0.9)
        else:
            u = -1 if view == "left" else 1
            fill(ctx, white)
            for k in range(5):
                x = (L - 20 - k * 22) * u
                poly(ctx, [(x, -5), (x - 9 * u, -5), (x - 20 * u, 60), (x - 11 * u, 60)], self.dots(0.5))
            rect(ctx, -300, 14, 300, 15.2, red)
