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
    style = "realistyczny: dwusilnikowy samolot patrolowy"
    fly = "Rzucaj delikatnie przed siebie. Ciężki, zablokowany nos daje bardzo stabilny lot w pokoju."
    difficulty = 3
    inks = {"main": "#e0542a"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, circle, ellipse, feat, Dots
        L = 138.0
        grey, dark = hx("#8d97a2"), hx("#2b3036")
        fill(ctx, Dots(hx("#8d97a2"), 0.06))
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.22))
            line(ctx, [(-300, 52), (300, 52)], hx("#ffffff"), lw=1.2)
            return
        if view == "top":
            for s in (1, -1):
                # końcówki skrzydeł w kolorze ostrzegawczym
                rect(ctx, -10, min(56 * s, 80 * s), 200, max(56 * s, 80 * s), self.dots(0.3))
                line(ctx, [(-10, 56 * s), (200, 56 * s)], self.c(0.1), lw=0.6)
                # gondole silników z kołpakami i śmigłami
                p = self.fit("top", 46, 28, (L - 30, 33 * s))
                if not p:
                    continue
                x0, y = p[0] + 22 - L, p[1]
                ctx.save()
                ctx.translate(x0, 0)
                poly(ctx, [(L - 52, y - 4.5), (L - 18, y - 5), (L - 12, y), (L - 18, y + 5), (L - 52, y + 4.5)],
                     Dots(grey, 0.32), stroke=grey, lw=0.35)
                circle(ctx, L - 10, y, 2.2, dark)
                line(ctx, [(L - 9, y - 13), (L - 9, y + 13)], dark, lw=0.6)
                ctx.restore()
                # lotki i klapy
                line(ctx, [(9, 4 * s), (9, 54 * s)], grey, lw=0.3)
                for yy in (4, 28, 54):
                    line(ctx, [(0, yy * s), (9, yy * s)], grey, lw=0.3)
            # okna kabiny przy nosie (na grzbiecie)
            poly(ctx, [(L - 12, -6), (L - 4, -5), (L - 4, 5), (L - 12, 6)], Dots(hx("#2f6aa8"), 0.45), stroke=dark, lw=0.3)
            self.label(ctx, "top", "SP-BRZ", (60, 26), 7, rgb=dark, bold=False)
            self.label(ctx, "top", "1017", (60, -26), 7, rgb=dark)
        elif view == "bottom":
            self.label(ctx, "bottom", "1017", (L - 25, 18), 6, rgb=dark)
            rect(ctx, L - 50, -40, L - 47, 40, self.c())
        else:
            u = -1 if view == "left" else 1
            rect(ctx, min((L - 50) * u, (L - 47) * u), -5, max((L - 50) * u, (L - 47) * u), 60, self.c())
            for k in range(4):
                circle(ctx, (L - 18 - k * 7) * u, 12, 1.3, Dots(hx("#2f6aa8"), 0.5))
