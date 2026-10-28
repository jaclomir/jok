"""Generuje PDF-y (wydruk + instrukcja) i podglądy PNG dla wszystkich modeli.

Użycie:  python3 build.py [slug ...]
"""
from __future__ import annotations

import importlib
import io
import json
import math
import os
import sys

import cairocffi as cairo
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(__file__))
from fold import apply, halfplane, reflection  # noqa: E402
from render import MM, paint_sheet, paper_ctx, render_3d, render_flat, sheet_image  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "wyniki")
MODELS = [("grot", "Grot"), ("albatros", "Albatros"), ("jerzyk", "Jerzyk"), ("sokol", "Sokol"),
          ("iskra", "Iskra"), ("bryza", "Bryza")]
ACCENT = (0.10, 0.16, 0.30)
FONT = "DejaVu Sans"


# ----------------------------------------------------------------------
def pil_to_surface(im):
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "PNG")
    buf.seek(0)
    return cairo.ImageSurface.create_from_png(buf)


def place_image(ctx, im, x, y, w, h=None):
    """Wstawia obraz PIL w prostokąt (mm, y w dół), zachowując proporcje."""
    s = pil_to_surface(im)
    iw, ih = im.size
    sc = w / iw if h is None else min(w / iw, h / ih)
    ctx.save()
    dx = x + (w - iw * sc) / 2
    dy = y + ((h - ih * sc) / 2 if h else 0)
    ctx.translate(dx, dy)
    ctx.scale(sc, sc)
    ctx.set_source_surface(s, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BEST)
    ctx.paint()
    ctx.restore()
    return ih * sc


def font(ctx, size, bold=False):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def wrap(ctx, txt, width):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if ctx.text_extents(t)[4] > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def para(ctx, txt, x, y, width, size, lh=1.3, bold=False, rgb=(0.1, 0.1, 0.12)):
    font(ctx, size, bold)
    ctx.set_source_rgb(*rgb)
    for i, ln in enumerate(wrap(ctx, txt, width)):
        ctx.move_to(x, y + size + i * size * lh)
        ctx.show_text(ln)
    return y + size + (len(wrap(ctx, txt, width)) - 1) * size * lh + size * 0.4


# ----------------------------------------------------------------------
def step_images(M, tex, px=420):
    """Obrazki kroków: lista (numer, tekst, PIL)."""
    out = []
    for i, st in enumerate(M.sheet.steps, 1):
        if st.flip:
            im = render_flat(st.state, tex, M, size=(px, px))
            d = ImageDraw.Draw(im)
            draw_flip_icon(d, px)
        elif st.line is None:
            im = render_flat(st.state, tex, M, size=(px, px), cut=st.extra[0])
        else:
            arrow = None
            allg = unary_union([f.flat for f in st.state])
            hp = halfplane(st.line[0], st.line[1], st.move)
            mv = allg.intersection(hp)
            if not mv.is_empty and mv.area > 1:
                c = mv.representative_point()
                R = reflection(st.line[0], st.line[1])
                c2 = R @ np.array([c.x, c.y, 1])
                arrow = ((c.x, c.y), (c2[0], c2[1]))
            im = render_flat(st.state, tex, M, size=(px, px), line=st.line, arrow=arrow)
        out.append((i, st.text, im))
    hs = M.plane.hinges
    for n, txt, hi in M.final_steps:
        if hi is not None:
            h = hs[hi]
            im = render_flat(M.sheet.facets, tex, M, size=(px, px), line=(h.a, h.b),
                             extra=[(x.a, x.b) for j, x in enumerate(hs) if j < hi])
        else:
            im = render_3d(M.pieces, tex, M, az=-150, el=18, size=(px, px), margin=18, shadow=False)
        out.append((n, txt, im))
    return out


def draw_flip_icon(d, px):
    cx, cy, r = px * 0.82, px * 0.16, px * 0.1
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(220, 30, 40), width=6)
    d.polygon([(cx + r - 14, cy - 4), (cx + r + 14, cy - 4), (cx + r, cy + 14)], fill=(220, 30, 40))


def instruction_page(ctx, M, tex, hero, top, steps):
    W, H = 210, 297
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    # nagłówek
    ctx.rectangle(0, 0, W, 26)
    ctx.set_source_rgb(*ACCENT)
    ctx.fill()
    font(ctx, 13, True)
    ctx.set_source_rgb(1, 1, 1)
    ctx.move_to(12, 15)
    ctx.show_text(M.name.upper())
    font(ctx, 4.2)
    ctx.move_to(12, 21.5)
    ctx.show_text(M.tagline)
    font(ctx, 3.2)
    ctx.move_to(W - 12 - ctx.text_extents("domowydrukarz.pl · papierowe samoloty")[4], 9)
    ctx.show_text("domowydrukarz.pl · papierowe samoloty")
    lvl = "Trudność: " + "●" * M.difficulty + "○" * (3 - M.difficulty)
    font(ctx, 4.2, True)
    ctx.move_to(W - 12 - ctx.text_extents(lvl)[4], 21.5)
    ctx.show_text(lvl)
    # podgląd i informacje
    place_image(ctx, hero, 8, 29, 112, 66)
    place_image(ctx, top, 120, 29, 40, 66)
    x0 = 163
    y = para(ctx, "Malowanie", x0, 30, 40, 3.4, bold=True, rgb=ACCENT)
    y = para(ctx, M.style, x0, y, 40, 2.9)
    y = para(ctx, "Drukowanie", x0, y + 2, 40, 3.4, bold=True, rgb=ACCENT)
    y = para(ctx, ("Tylko strona 1, jednostronnie, A4 80 g, " +
                   ("w poziomie. " if M.W > M.H else "w pionie. ") +
                   "Skala 100% („rozmiar rzeczywisty”) – bez dopasowania do strony, inaczej linie się rozjadą."),
             x0, y, 40, 2.9)
    y = para(ctx, "Latanie", x0, y + 2, 40, 3.4, bold=True, rgb=ACCENT)
    para(ctx, M.fly, x0, y, 40, 2.9)
    # legenda linii
    ly = 99
    ctx.set_line_width(0.5)
    ctx.set_source_rgb(0.15, 0.15, 0.2)
    ctx.set_dash([3.0, 1.6])
    ctx.move_to(12, ly)
    ctx.line_to(30, ly)
    ctx.stroke()
    ctx.set_dash([3.0, 1.0, 0.5, 1.0])
    ctx.move_to(84, ly)
    ctx.line_to(102, ly)
    ctx.stroke()
    ctx.set_dash([])
    font(ctx, 2.9)
    ctx.move_to(33, ly + 1)
    ctx.show_text("dolina (od nadruku: rowek)")
    ctx.move_to(105, ly + 1)
    ctx.show_text("grzbiet (od nadruku: grzbiet)")
    # siatka kroków
    cols = 4
    cw = (W - 16) / cols
    gy = 104
    rows = math.ceil((len(steps) + 1) / cols)
    ch = (H - gy - 8) / rows
    imgh = min(cw - 4, ch - 25)
    cells = [(0, "Tak wygląda wydruk od strony nadruku. Strzałka pokazuje górną krawędź. Do składania połóż go "
                 "nadrukiem do stołu (odwróć jak stronę w książce).", None)] + steps
    for k, (n, txt, im) in enumerate(cells):
        cx = 8 + (k % cols) * cw
        cy = gy + (k // cols) * ch
        ctx.set_source_rgb(0.95, 0.96, 0.97)
        rounded(ctx, cx + 1, cy + 1, cw - 2, ch - 2, 2.5)
        ctx.fill()
        if im is None:
            place_sheet_thumb(ctx, M, tex, cx + 2, cy + 2, cw - 4, imgh)
        else:
            place_image(ctx, im, cx + 2, cy + 2, cw - 4, imgh)
        ctx.set_source_rgb(*ACCENT)
        ctx.arc(cx + 6, cy + 6, 3.4, 0, 2 * math.pi)
        ctx.fill()
        font(ctx, 3.6, True)
        ctx.set_source_rgb(1, 1, 1)
        t = str(n)
        e = ctx.text_extents(t)
        ctx.move_to(cx + 6 - e[2] / 2 - e[0], cy + 6 + e[3] / 2)
        ctx.show_text(t)
        avail = ch - imgh - 5
        size = 2.6
        while size > 1.9:
            font(ctx, size)
            if len(wrap(ctx, txt, cw - 6)) * size * 1.25 + size * 0.3 <= avail:
                break
            size -= 0.1
        para(ctx, txt, cx + 3, cy + imgh + 2.5, cw - 6, size, lh=1.25)


def place_sheet_thumb(ctx, M, tex, x, y, w, h):
    hgt = place_image(ctx, tex.resize((tex.width // 4, tex.height // 4)), x, y, w, h)
    sc = min(w / tex.width, h / tex.height) * 1
    tw, th = tex.width * sc, tex.height * sc
    ox, oy = x + (w - tw) / 2, y + (h - th) / 2
    ctx.set_source_rgb(0.3, 0.3, 0.35)
    ctx.set_line_width(0.3)
    ctx.rectangle(ox, oy, tw, th)
    ctx.stroke()
    # strzałka „góra”
    ctx.set_source_rgb(0.86, 0.12, 0.16)
    ax = ox + tw / 2
    ctx.move_to(ax, oy - 0.5)
    ctx.line_to(ax - 2.5, oy + 3.5)
    ctx.line_to(ax + 2.5, oy + 3.5)
    ctx.close_path()
    ctx.fill()


def rounded(ctx, x, y, w, h, r):
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


# ----------------------------------------------------------------------
def build(slug, cls):
    M = getattr(importlib.import_module("models." + slug), cls)()
    od = os.path.join(OUT, slug)
    os.makedirs(od, exist_ok=True)
    tex = sheet_image(M, M.pieces, ppmm=M.ppmm)
    hero = render_3d(M.pieces, tex, M, az=-140, el=32, size=(1500, 900), margin=40)
    top = render_3d(M.pieces, tex, M, az=-90, el=89, size=(600, 1000), margin=20, shadow=False).rotate(90, expand=True)
    top = top.crop(top.getbbox() if False else (0, 0, top.width, top.height))
    hero.save(os.path.join(od, f"{slug}-podglad.png"))
    render_3d(M.pieces, tex, M, az=-60, el=-30, size=(1500, 900), margin=40, shadow=False).save(
        os.path.join(od, f"{slug}-spod.png"))
    tex.resize((tex.width // 2, tex.height // 2)).save(os.path.join(od, f"{slug}-arkusz.png"))
    steps = step_images(M, tex)
    # dane dla strony i arkusz PDF – składany tym samym kodem JS (pdf-lib) co w przeglądarce
    import export
    import subprocess
    import pymupdf
    dd = os.path.join(OUT, "dane")
    os.makedirs(dd, exist_ok=True)
    js = os.path.join(dd, f"{slug}.json")
    with open(js, "w") as f:
        json.dump(export.model_data(M), f, ensure_ascii=False, separators=(",", ":"))
    arkusz = os.path.join(od, f"{slug}-tylko-wydruk.pdf")
    node = os.path.join(os.path.dirname(__file__), "web", "pdf-node.js")
    subprocess.run(["node", node, js, arkusz], check=True)
    subprocess.run(["node", node, js, os.path.join(od, f"{slug}-same-linie.pdf"), "linie"], check=True)
    # instrukcja (A4 pionowo) z cairo, doklejona jako strona 2
    instr = os.path.join(od, f".{slug}-instrukcja.pdf")
    surf = cairo.PDFSurface(instr, 210 * MM, 297 * MM)
    ctx = cairo.Context(surf)
    ctx.scale(MM, MM)
    instruction_page(ctx, M, tex, hero, top, steps)
    surf.show_page()
    surf.finish()
    doc = pymupdf.open(arkusz)
    doc.insert_pdf(pymupdf.open(instr))
    doc.set_metadata({"title": f"{M.name} – papierowy samolot (domowydrukarz.pl)", "author": "domowydrukarz.pl"})
    doc.rewrite_images(dpi_threshold=200, dpi_target=170, quality=82, lossy=True, lossless=True)
    doc.save(os.path.join(od, f"{slug}.pdf"), garbage=3, deflate=True)
    os.remove(instr)
    from views import ink
    mean, mx, frac = ink(M)
    bad = M.check_features()
    for b in bad:
        print("  UWAGA – ucięty detal:", b, file=sys.stderr)
    if mean > 0.15 or mx > 0.5:
        print(f"  UWAGA – dużo tuszu: średnio {mean:.2f}, lokalnie {mx:.2f}", file=sys.stderr)
    stats = {
        "slug": slug, "nazwa": M.name, "opis": M.tagline, "styl": M.style, "trudnosc": M.difficulty,
        "orientacja": "pozioma" if M.W > M.H else "pionowa",
        "widoczny_nadruk_proc": round(100 * sum(p.paper.area for p in M.pieces if p.printed) /
                                      sum(p.paper.area for p in M.pieces)),
        "kroki": len(M.sheet.steps) + len(M.final_steps),
        "tusz_srednio_proc": round(100 * mean),
        "tusz_max_30mm_proc": round(100 * mx),
    }
    print(json.dumps(stats, ensure_ascii=False))
    return M, stats


if __name__ == "__main__":
    want = sys.argv[1:]
    allstats = []
    for slug, cls in MODELS:
        if want and slug not in want:
            continue
        _, st = build(slug, cls)
        allstats.append(st)
    if not want:
        with open(os.path.join(OUT, "modele.json"), "w") as f:
            json.dump(allstats, f, ensure_ascii=False, indent=2)
