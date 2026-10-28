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
    style = "kreskówkowy: mops z czarną mordką"
    fly = "Rzucaj delikatnie przed siebie. Ciężki, zablokowany nos daje bardzo stabilny lot w pokoju."
    difficulty = 3

    def art(self, ctx, view, piece):
        from paint import hx, fill, poly, rect, line, text, circle, ellipse, curve
        L = 138.0
        fawn, fawn2, dark = hx("#e7c39b"), hx("#d6a874"), hx("#2b2320")
        if piece.zone == "winglet":
            fill(ctx, dark)  # uszy
            return
        if view == "top":
            fill(ctx, fawn)
            for s in (1, -1):
                # łaty i fałdki
                ellipse(ctx, 40, 40 * s, 22, 14, fawn2)
                # łapki na tylnej krawędzi
                for k in range(4):
                    circle(ctx, 4, (44 + k * 5.5) * s, 2.3, dark)
                circle(ctx, 9, 50 * s, 4, dark)
                # uszy przy nosie
                poly(ctx, [(L - 40, 26 * s), (L - 18, 34 * s), (L - 34, 52 * s)], dark)
            # czarna mordka
            ellipse(ctx, L - 6, 0, 26, 24, dark)
            # oczy
            for s in (1, -1):
                circle(ctx, L - 22, 13 * s, 6.5, hx("#ffffff"))
                circle(ctx, L - 20.5, 13 * s, 4.3, hx("#3b2a1e"))
                circle(ctx, L - 19.2, 14.2 * s, 1.4, hx("#ffffff"))
                curve(ctx, (L - 38, 5 * s), (L - 42, 10 * s), (L - 42, 16 * s), (L - 38, 21 * s), dark, lw=0.8)
            # nosek
            ellipse(ctx, L - 4, 0, 4, 7, hx("#000000"))
            # obroża z blaszką
            rect(ctx, L - 50, -70, L - 44, 70, hx("#e63946"))
            circle(ctx, L - 47, 0, 4.2, hx("#f2c14e"), stroke=hx("#b8860b"), lw=0.4)
            text(ctx, "M", L - 47, 0, 4, rgb=hx("#7a5b00"))
            # ogonek-precelek
            curve(ctx, (2, 0), (14, 10), (20, -6), (8, -4), fawn2, lw=2.4)
        elif view == "bottom":
            fill(ctx, hx("#f6e6d2"))
            # język
            ellipse(ctx, L - 14, 0, 8, 5, hx("#ff7a90"), stroke=hx("#d4506a"), lw=0.4)
            line(ctx, [(L - 20, 0), (L - 9, 0)], hx("#d4506a"), lw=0.4)
        else:
            u = -1 if view == "left" else 1
            X = lambda x: x * u
            fill(ctx, fawn)
            ellipse(ctx, X(L - 8), 10, 18, 16, dark)
            rect(ctx, min(X(L - 50), X(L - 44)), -5, max(X(L - 50), X(L - 44)), 60, hx("#e63946"))
            text(ctx, "MOPS", X(60), 12, 9, rgb=hx("#8a5a2b"))
            for k in range(3):
                curve(ctx, (X(100 - k * 6), 4), (X(98 - k * 6), 9), (X(98 - k * 6), 13), (X(100 - k * 6), 18),
                      fawn2, lw=0.8)
