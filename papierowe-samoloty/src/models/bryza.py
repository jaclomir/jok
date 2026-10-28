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
    style = "realistyczny: dwusilnikowy samolot ratowniczy z pasami ostrzegawczymi"
    fly = "Rzucaj delikatnie przed siebie. Ciężki, zablokowany nos daje bardzo stabilny lot w pokoju."
    difficulty = 3
    inks = {"main": "#e0542a"}

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, circle, Dots
        L = 138.0
        grey, dark, white = hx("#8d97a2"), hx("#2b3036"), hx("#ffffff")
        fill(ctx, white)
        if piece.zone == "winglet":
            fill(ctx, self.dots(0.4))
            for k in range(3):
                line(ctx, [(-300, 48 + k * 7), (300, 48 + k * 7)], white, lw=2.2)
            return
        if view == "top":
            for s in (1, -1):
                # końcówki skrzydeł w ukośne pasy ostrzegawcze
                ctx.save()
                ctx.rectangle(-10, min(56 * s, 80 * s), 210, 24)
                ctx.clip()
                fill(ctx, self.dots(0.62))
                for k in range(-6, 30):
                    x = k * 9
                    poly(ctx, [(x, 50 * s), (x + 4, 50 * s), (x + 4 + 26, 86 * s), (x + 26, 86 * s)], white)
                ctx.restore()
                line(ctx, [(-10, 56 * s), (200, 56 * s)], self.c(0.2), lw=0.6)
                # gondole silników ze śmigłami
                p = self.fit("top", 46, 28, (L - 30, 30 * s))
                if p:
                    ctx.save()
                    ctx.translate(p[0] + 22 - L, 0)
                    y = p[1]
                    poly(ctx, [(L - 52, y - 4.5), (L - 18, y - 5), (L - 12, y), (L - 18, y + 5), (L - 52, y + 4.5)],
                         Dots(grey, 0.35), stroke=dark, lw=0.35)
                    line(ctx, [(L - 30, y - 5), (L - 30, y + 5)], self.c(), lw=1.0)
                    circle(ctx, L - 10, y, 2.2, self.c(0.2))
                    line(ctx, [(L - 9, y - 13), (L - 9, y + 13)], dark, lw=0.6)
                    ctx.restore()
                line(ctx, [(9, 4 * s), (9, 54 * s)], grey, lw=0.3)
                for yy in (4, 28, 54):
                    line(ctx, [(0, yy * s), (9, yy * s)], grey, lw=0.3)
            # pas na grzbiecie, okna kabiny, nos
            rect(ctx, -10, -3, L - 14, 3, self.dots(0.6))
            poly(ctx, [(L - 13, -6), (L - 4, -5), (L - 4, 5), (L - 13, 6)], Dots(hx("#2f6aa8"), 0.5), stroke=dark, lw=0.3)
            self.label(ctx, "top", "SP-BRZ", (55, 30), 7, rgb=dark, bold=False)
            self.label(ctx, "top", "RATUNEK", (55, -30), 6, rgb=self.c(0.25))
        elif view == "bottom":
            fill(ctx, Dots(grey, 0.06))
            self.label(ctx, "bottom", "SP-BRZ", (L - 25, 18), 6, rgb=dark)
            rect(ctx, L - 50, -40, L - 46, 40, self.c())
        else:
            u = -1 if view == "left" else 1
            rect(ctx, -300, 1, 300, 4, self.dots(0.42))
            rect(ctx, min((L - 50) * u, (L - 46) * u), -5, max((L - 50) * u, (L - 46) * u), 60, self.c())
            for k in range(4):
                circle(ctx, (L - 18 - k * 7) * u, 12, 1.3, Dots(hx("#2f6aa8"), 0.5))
