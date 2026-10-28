/* Papierowe samoloty – rysowanie arkusza, podglądów i PDF z danych wyeksportowanych przez export.py.
   Działa w przeglądarce (canvas + pdf-lib) i w Node (sam PDF, do budowania plików w repo). */
(function (root) {
  'use strict';
  const MM = 72 / 25.4; // punktów PDF na milimetr

  /* ---------- kolory ---------- */
  function hexRgb(h) {
    const v = parseInt(String(h).replace('#', ''), 16);
    return [(v >> 16) & 255, (v >> 8) & 255, v & 255].map(c => c / 255);
  }
  function rgbHex(c) {
    return '#' + c.map(v => Math.round(Math.max(0, Math.min(1, v)) * 255).toString(16).padStart(2, '0')).join('');
  }
  // spec: {h:'#rrggbb'} albo {r:'main', k:przyciemnienie}; kolory: {main:'#rrggbb'}
  function kolor(spec, kolory) {
    if (spec.h) return hexRgb(spec.h);
    const base = hexRgb(kolory[spec.r] || '#808080');
    const k = spec.k || 0;
    return base.map(c => c * (1 - k));
  }

  /* ---------- ścieżki ---------- */
  function parsePath(d) {
    const out = [];
    const re = /([MLCZ])([^MLCZ]*)/g;
    let m;
    while ((m = re.exec(d))) {
      const n = m[2].trim() ? m[2].trim().split(/[\s,]+/).map(Number) : [];
      out.push([m[1], n]);
    }
    return out;
  }
  function pathBox(segs) {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const [, n] of segs) for (let i = 0; i < n.length; i += 2) {
      x0 = Math.min(x0, n[i]); x1 = Math.max(x1, n[i]); y0 = Math.min(y0, n[i + 1]); y1 = Math.max(y1, n[i + 1]);
    }
    return [x0, y0, x1, y1];
  }

  /* ---------- raster kropek ---------- */
  // siatka heksagonalna w milimetrach kartki, liczona od lewego górnego rogu.
  // Każdy rząd kropek to jeden odcinek rysowany kreską o zerowej długości i okrągłym końcu:
  // cb(x0, x1, y) – odcinek od pierwszej do ostatniej kropki rzędu, kropki co `p` punktów.
  function rzedy(box, pitch, cb) {
    const p = pitch * MM, h = p * Math.sqrt(3) / 2;
    const j0 = Math.floor(box[1] / h) - 1, j1 = Math.ceil(box[3] / h) + 1;
    for (let j = j0; j <= j1; j++) {
      const off = (j & 1) ? p / 2 : 0;
      const i0 = Math.floor((box[0] - off) / p) - 1, i1 = Math.ceil((box[2] - off) / p) + 1;
      cb(i0 * p + off, i1 * p + off + 0.02, j * h);
    }
    return p;
  }
  const r2 = v => Math.round(v * 100) / 100;
  function promien(cov, pitch) {
    const p = pitch * MM;
    return Math.sqrt(cov * p * p * Math.sqrt(3) / 2 / Math.PI);
  }

  /* ---------- canvas ---------- */
  function path2d(d, W, H) {
    if (d === 'PAGE') { const p = new Path2D(); p.rect(-5, -5, W + 10, H + 10); return p; }
    return new Path2D(d);
  }
  // rysuje arkusz na kontekście canvas; skala: pikseli na punkt PDF
  function rysujArkusz(ctx, model, kolory, skala, opcje) {
    opcje = opcje || {};
    const W = model.W * MM, H = model.H * MM;
    ctx.save();
    ctx.setTransform(skala, 0, 0, skala, 0, 0);
    ctx.fillStyle = opcje.papier || '#ffffff';
    ctx.fillRect(0, 0, W, H);
    for (const op of model.ops) {
      const t = op[0];
      if (t === 'q') ctx.save();
      else if (t === 'Q') ctx.restore();
      else if (t === 'W') ctx.clip(path2d(op[1], W, H));
      else if (t === 'f') {
        const c = kolor(op[2], kolory);
        ctx.globalAlpha = op[3];
        ctx.fillStyle = rgbHex(c);
        ctx.fill(path2d(op[1], W, H));
        ctx.globalAlpha = 1;
      } else if (t === 's') {
        if (opcje.bezLinii && op[2].h && op[5].length) continue;
        const c = kolor(op[2], kolory);
        ctx.globalAlpha = op[3];
        ctx.strokeStyle = rgbHex(c);
        ctx.lineWidth = op[4];
        ctx.setLineDash(op[5]);
        ctx.lineCap = ['butt', 'round', 'square'][op[6]];
        ctx.stroke(path2d(op[1], W, H));
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      } else if (t === 'dots') {
        const spec = op[2], box = op[3];
        const c = rgbHex(kolor(spec, kolory));
        ctx.save();
        ctx.clip(path2d(op[1], W, H));
        const r = promien(spec.d, model.kropka);
        if (opcje.gladko) {
          // na małym podglądzie kropki zlewają się – rysujemy średni odcień
          const k = kolor(spec, kolory), a = Math.min(1, spec.d);
          ctx.fillStyle = rgbHex(k.map(v => 1 - a * (1 - v)));
          ctx.fillRect(box[0], box[1], box[2] - box[0], box[3] - box[1]);
        } else {
          ctx.strokeStyle = c;
          ctx.lineWidth = 2 * r;
          ctx.lineCap = 'round';
          ctx.beginPath();
          const p = rzedy(box, model.kropka, (x0, x1, y) => { ctx.moveTo(x0, y); ctx.lineTo(x1, y); });
          ctx.setLineDash([0.01, p - 0.01]);
          ctx.stroke();
          ctx.setLineDash([]);
        }
        ctx.restore();
      }
    }
    ctx.restore();
  }

  // obraz arkusza (canvas) w zadanej rozdzielczości: pikseli na milimetr
  function arkuszCanvas(model, kolory, ppmm, opcje) {
    const c = document.createElement('canvas');
    c.width = Math.round(model.W * ppmm);
    c.height = Math.round(model.H * ppmm);
    rysujArkusz(c.getContext('2d'), model, kolory, ppmm / MM, opcje);
    return c;
  }

  /* ---------- sceny: model 3D i schematy kroków ---------- */
  const PAPIER = '#faf9f5';
  function rysujScene(canvas, scena, model, arkusz, ppmm, opcje) {
    opcje = opcje || {};
    const dpr = opcje.dpr || 1;
    canvas.width = Math.round(scena.w * dpr);
    canvas.height = Math.round(scena.h * dpr);
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, scena.w, scena.h);
    if (opcje.tlo) { ctx.fillStyle = opcje.tlo; ctx.fillRect(0, 0, scena.w, scena.h); }
    const H = model.H;
    // piksel arkusza -> mm kartki (y w górę)
    const T = new DOMMatrix([1 / ppmm, 0, 0, -1 / ppmm, 0, H]);
    for (const it of scena.items) {
      if (!it.p.length) continue;
      ctx.save();
      ctx.beginPath();
      it.p.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.closePath();
      ctx.clip();
      if (it.pr) {
        const m = new DOMMatrix(it.m).multiply(T);
        ctx.setTransform(new DOMMatrix([dpr, 0, 0, dpr, 0, 0]).multiply(m));
        ctx.drawImage(arkusz, 0, 0);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      } else {
        ctx.fillStyle = PAPIER;
        ctx.fillRect(0, 0, scena.w, scena.h);
      }
      if (it.sh !== undefined && it.sh < 1) {
        ctx.fillStyle = 'rgba(40,30,20,' + (1 - it.sh).toFixed(3) + ')';
        ctx.fillRect(0, 0, scena.w, scena.h);
      }
      ctx.restore();
      ctx.beginPath();
      it.p.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.closePath();
      ctx.strokeStyle = 'rgba(60,55,50,.55)';
      ctx.lineWidth = 0.6;
      ctx.stroke();
    }
    for (const [x0, y0, x1, y1, k] of scena.lines || []) {
      ctx.strokeStyle = k === 'r' ? '#d7263d' : '#2a6fd6';
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 4]);
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
      ctx.setLineDash([]);
    }
    for (const seg of scena.cut || []) {
      ctx.strokeStyle = '#d7263d'; ctx.lineWidth = 2; ctx.setLineDash([3, 3]);
      ctx.beginPath(); seg.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.stroke();
      ctx.setLineDash([]);
    }
    if (scena.arrow) strzalka(ctx, scena.arrow);
    if (scena.flip) obrot(ctx, scena.w, scena.h);
  }
  function strzalka(ctx, a) {
    const [x0, y0, x1, y1] = a;
    const mx = (x0 + x1) / 2, my = (y0 + y1) / 2, vx = x1 - x0, vy = y1 - y0;
    const L = Math.hypot(vx, vy);
    if (L < 2) return;
    const cx = mx - vy * 0.25, cy = my + vx * 0.25;
    ctx.strokeStyle = '#26221d'; ctx.fillStyle = '#26221d'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.quadraticCurveTo(cx, cy, x1, y1); ctx.stroke();
    const tx = x1 - cx, ty = y1 - cy, tl = Math.hypot(tx, ty) || 1, ux = tx / tl, uy = ty / tl, s = 9;
    ctx.beginPath(); ctx.moveTo(x1, y1);
    ctx.lineTo(x1 - ux * s - uy * s * 0.5, y1 - uy * s + ux * s * 0.5);
    ctx.lineTo(x1 - ux * s + uy * s * 0.5, y1 - uy * s - ux * s * 0.5);
    ctx.closePath(); ctx.fill();
  }
  function obrot(ctx, w, h) {
    const cx = w * 0.84, cy = h * 0.15, r = Math.min(w, h) * 0.08;
    ctx.strokeStyle = '#d7263d'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(cx, cy, r, 0.3, 2 * Math.PI - 0.3); ctx.stroke();
    ctx.fillStyle = '#d7263d';
    ctx.beginPath(); ctx.moveTo(cx + r - 6, cy + 2); ctx.lineTo(cx + r + 6, cy + 2); ctx.lineTo(cx + r, cy + 11); ctx.fill();
  }

  /* ---------- PDF (pdf-lib) ---------- */
  async function pdf(PDFLib, model, kolory, meta) {
    const L = PDFLib;
    const doc = await L.PDFDocument.create();
    meta = meta || {};
    doc.setTitle(meta.tytul || (model.nazwa + ' – papierowy samolot'));
    doc.setAuthor('domowydrukarz.pl');
    doc.setCreator('domowydrukarz.pl – papierowe samoloty');
    const W = model.W * MM, H = model.H * MM;
    const page = doc.addPage([W, H]);
    const gs = {};
    function alfa(a) {
      const key = a.toFixed(2);
      if (!gs[key]) {
        const ref = doc.context.register(doc.context.obj({ Type: 'ExtGState', ca: a, CA: a }));
        gs[key] = page.node.newExtGState('GS', ref);
      }
      return gs[key];
    }
    const ops = [];
    const sciezka = d => {
      if (d === 'PAGE') { const w = r2(W + 5), h = r2(H + 5); ops.push(L.moveTo(-5, -5), L.lineTo(w, -5), L.lineTo(w, h), L.lineTo(-5, h), L.closePath()); return; }
      for (const [c, n] of parsePath(d)) {
        if (c === 'M') ops.push(L.moveTo(n[0], n[1]));
        else if (c === 'L') ops.push(L.lineTo(n[0], n[1]));
        else if (c === 'C') ops.push(L.appendBezierCurve(n[0], n[1], n[2], n[3], n[4], n[5]));
        else ops.push(L.closePath());
      }
    };
    ops.push(L.pushGraphicsState(), L.concatTransformationMatrix(1, 0, 0, -1, 0, r2(H)));
    for (const op of model.ops) {
      const t = op[0];
      if (t === 'q') ops.push(L.pushGraphicsState());
      else if (t === 'Q') ops.push(L.popGraphicsState());
      else if (t === 'W') { sciezka(op[1]); ops.push(L.clip(), L.endPath()); }
      else if (t === 'f') {
        const c = kolor(op[2], kolory);
        ops.push(L.pushGraphicsState());
        if (op[3] < 1) ops.push(L.setGraphicsState(alfa(op[3])));
        ops.push(L.setFillingRgbColor(c[0], c[1], c[2]));
        sciezka(op[1]);
        ops.push(L.fill(), L.popGraphicsState());
      } else if (t === 's') {
        const c = kolor(op[2], kolory);
        ops.push(L.pushGraphicsState());
        if (op[3] < 1) ops.push(L.setGraphicsState(alfa(op[3])));
        ops.push(L.setStrokingRgbColor(c[0], c[1], c[2]), L.setLineWidth(op[4]), L.setDashPattern(op[5], 0),
          L.setLineCap(op[6]));
        sciezka(op[1]);
        ops.push(L.stroke(), L.popGraphicsState());
      } else if (t === 'dots') {
        const spec = op[2], c = kolor(spec, kolory), r = promien(spec.d, model.kropka);
        ops.push(L.pushGraphicsState());
        sciezka(op[1]);
        ops.push(L.clip(), L.endPath(), L.setStrokingRgbColor(c[0], c[1], c[2]), L.setLineWidth(r2(2 * r)),
          L.setLineCap(L.LineCapStyle.Round));
        const p = MM * model.kropka;
        ops.push(L.setDashPattern([0.01, r2(p - 0.01)], 0));
        rzedy(op[3], model.kropka, (x0, x1, y) => ops.push(L.moveTo(r2(x0), r2(y)), L.lineTo(r2(x1), r2(y))));
        ops.push(L.stroke(), L.popGraphicsState());
      }
    }
    ops.push(L.popGraphicsState());
    for (let i = 0; i < ops.length; i += 4000) page.pushOperators(...ops.slice(i, i + 4000));
    return doc.save();
  }

  const API = { MM, kolor, hexRgb, rgbHex, rysujArkusz, arkuszCanvas, rysujScene, pdf };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  else root.Samoloty = API;
})(typeof globalThis !== 'undefined' ? globalThis : this);
