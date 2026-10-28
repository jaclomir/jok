/* Papierowe samoloty – logika strony: wybór modelu i koloru, podgląd, kroki składania, PDF. */
(function () {
  'use strict';
  const S = window.Samoloty;
  const DANE = window.SAMOLOTY_DANE;
  const $ = id => document.getElementById(id);

  const KOLORY = [
    ['naturalny', null], ['czerwony', '#d62f3d'], ['różowy', '#e2508c'], ['pomarańczowy', '#ee7a22'],
    ['żółty', '#e9b500'], ['zielony', '#2e9d5b'], ['turkusowy', '#1c9aa3'], ['niebieski', '#2a6fd6'],
    ['fioletowy', '#7b4fc9'], ['grafitowy', '#4a4f57'],
  ];
  const TRUDNOSC = ['', 'łatwy', 'średni', 'trudniejszy'];

  const st = { model: DANE[0].slug, kolor: null, widok: 'gora', instr: false, linie: false, bezDrukarki: false };
  const cache = new Map();
  let pdfUrl = null, pdfTimer = null, pdfNr = 0;

  const model = () => DANE.find(m => m.slug === st.model);
  const kolory = m => Object.assign({}, m.kolory, st.kolor ? { main: st.kolor } : {});
  const nazwaKoloru = () => (KOLORY.find(k => k[1] === st.kolor) || ['własny'])[0];
  const dpr = () => Math.min(2, window.devicePixelRatio || 1);

  // arkusz jako obraz – gładki odcień zamiast kropek, bo na ekranie kropki dają mory
  function arkusz(m, ppmm, gladko) {
    const k = m.slug + '|' + (st.kolor || '') + '|' + ppmm + '|' + gladko + '|' + st.linie;
    if (!cache.has(k)) cache.set(k, S.arkuszCanvas(m, kolory(m), ppmm, { gladko, bezMalowania: st.linie }));
    return cache.get(k);
  }

  /* ---------- adres strony ---------- */
  function czytajAdres() {
    const q = new URLSearchParams(location.search);
    if (DANE.some(m => m.slug === q.get('model'))) st.model = q.get('model');
    const k = q.get('kolor');
    if (k && /^[0-9a-f]{6}$/i.test(k)) st.kolor = '#' + k.toLowerCase();
    st.linie = q.get('malowanie') === '0';
    st.bezDrukarki = q.get('drukarka') === '0';
  }
  function zapiszAdres() {
    const q = new URLSearchParams();
    q.set('model', st.model);
    if (st.kolor) q.set('kolor', st.kolor.slice(1));
    if (st.linie) q.set('malowanie', '0');
    if (st.bezDrukarki) q.set('drukarka', '0');
    try { history.replaceState(null, '', '?' + q.toString()); } catch (e) { /* plik lokalny */ }
  }

  /* ---------- modele ---------- */
  function rysujModele() {
    const box = $('modele');
    box.innerHTML = '';
    for (const m of DANE) {
      const b = document.createElement('button');
      b.type = 'button';
      b.dataset.slug = m.slug;
      b.setAttribute('aria-pressed', String(m.slug === st.model));
      const c = document.createElement('canvas');
      c.setAttribute('aria-hidden', 'true');
      b.appendChild(c);
      const n = document.createElement('span');
      n.textContent = m.nazwa;
      b.appendChild(n);
      const sm = document.createElement('small');
      sm.textContent = TRUDNOSC[m.trudnosc];
      b.appendChild(sm);
      b.addEventListener('click', () => { st.model = m.slug; zmiana(); });
      box.appendChild(b);
    }
    miniatury();
  }
  function miniatury() {
    for (const b of $('modele').querySelectorAll('button')) {
      const m = DANE.find(x => x.slug === b.dataset.slug);
      b.setAttribute('aria-pressed', String(m.slug === st.model));
      const sc = m.widoki.gora;
      const c = b.querySelector('canvas');
      S.rysujScene(c, sc, m, arkusz(m, 2, true), 2, { dpr: dpr() * 0.34 });
    }
  }

  /* ---------- kolory ---------- */
  function rysujKolory() {
    const k = $('kolory');
    k.innerHTML = '';
    for (const [n, hex] of KOLORY) {
      const b = document.createElement('button');
      b.type = 'button';
      b.title = n;
      b.setAttribute('aria-label', 'Kolor: ' + n);
      b.dataset.hex = hex || '';
      b.style.background = hex || 'conic-gradient(#d62f3d, #e9b500, #2e9d5b, #2a6fd6, #7b4fc9, #d62f3d)';
      b.addEventListener('click', () => { st.kolor = hex; st.linie = false; zmiana(); });
      k.appendChild(b);
    }
    const inp = document.createElement('input');
    inp.type = 'color';
    inp.id = 'kolorWlasny';
    inp.title = 'Własny kolor';
    inp.setAttribute('aria-label', 'Własny kolor');
    inp.addEventListener('input', () => { st.kolor = inp.value.toLowerCase(); st.linie = false; zmiana(); });
    k.appendChild(inp);
  }
  function zaznaczKolor() {
    for (const b of $('kolory').querySelectorAll('button')) b.setAttribute('aria-pressed', String((b.dataset.hex || null) === st.kolor));
    $('kolorWlasny').value = st.kolor || model().kolory.main;
    $('bezMal').checked = st.linie;
    $('kolory').classList.toggle('wylaczone', st.linie);
    if (st.linie) { $('kolorNazwa').textContent = 'malowanie wyłączone – drukują się same linie zgięć'; return; }
    $('kolorNazwa').textContent = st.kolor ? nazwaKoloru() + (nazwaKoloru() === 'własny' ? ' ' + st.kolor : '') : 'naturalny dla modelu';
  }

  /* ---------- podgląd ---------- */
  function podglad() {
    const m = model();
    const c = $('podglad');
    for (const b of document.querySelectorAll('#widoki button')) b.setAttribute('aria-pressed', String(b.dataset.w === st.widok));
    if (st.widok === 'arkusz') {
      const a = arkusz(m, 3, true);
      c.width = a.width; c.height = a.height;
      const x = c.getContext('2d');
      x.setTransform(1, 0, 0, 1, 0, 0);
      x.drawImage(a, 0, 0);
      $('podpisPodgladu').textContent = 'Arkusz od strony nadruku. Białe pola zostają w środku modelu.';
    } else {
      S.rysujScene(c, m.widoki[st.widok], m, arkusz(m, 4, true), 4, { dpr: dpr(), tlo: '#ffffff' });
      $('podpisPodgladu').textContent = st.widok === 'gora' ? 'Złożony model, widok z góry.'
        : 'Złożony model od spodu. Białe miejsca to strona kartki bez nadruku.';
    }
    // lupa: fragment arkusza z prawdziwymi kropkami, mniej więcej w skali 1:1
    const l = $('lupa');
    l.parentElement.hidden = st.linie;
    const ppmm = 3.78 * dpr();
    const k = 'lupa|' + m.slug + '|' + (st.kolor || '') + '|' + st.linie;
    if (!cache.has(k)) cache.set(k, S.arkuszCanvas(m, kolory(m), ppmm, { gladko: false, bezMalowania: st.linie }));
    const big = cache.get(k);
    l.width = Math.round(220 * dpr()); l.height = Math.round(120 * dpr());
    const fx = m.lupa ? m.lupa[0] : 0.5, fy = m.lupa ? m.lupa[1] : 0.5;
    l.getContext('2d').drawImage(big, Math.max(0, big.width * fx - l.width / 2), Math.max(0, big.height * fy - l.height / 2),
      l.width, l.height, 0, 0, l.width, l.height);
  }

  function opis() {
    const m = model();
    $('mNazwa').textContent = m.nazwa;
    $('mOpis').textContent = m.opis;
    $('mStyl').textContent = m.styl;
    $('mTrud').textContent = TRUDNOSC[m.trudnosc] + ' · ' + m.kroki.length + ' kroków';
    $('mLot').textContent = m.lot;
    $('orientRada').innerHTML = 'Papier <b>A4</b>, ' + (m.W > m.H ? 'poziomo' : 'pionowo') + '. Zwykły papier biurowy 80 g/m².';
  }

  /* ---------- kroki składania ---------- */
  // tekst kroku w wersji bez drukarki: czysta kartka zamiast wydruku, bez odwołań do numerów linii
  function bezWydruku(t, m) {
    const orient = m.W > m.H ? 'poziomo' : 'pionowo';
    return t
      .replace(/Połóż wydruk[^.]*\./, 'Połóż czystą kartkę A4 ' + (m.W > m.H ? 'poziomo, dłuższym bokiem do siebie.' : 'pionowo, krótszym bokiem do siebie.'))
      .replace(/[^.]*pojawi się linia[^.]*\.\s*/g, '')
      .replace(/wzdłuż (krótkiej |długiej, płaskiej |poziomej |pionowej |środkowej |kropkowanej )?linii \d+( (i|–) \d+)?/g, 'wzdłuż czerwonej linii ze schematu')
      .replace(/ \((linia|linie) [\d–, ]+\)/g, '')
      .replace(/ do linii STOP \((\d+) zgięć\)/, ' – razem $1 zgięć')
      .trim();
  }
  function kartyKrokow(m, bez) {
    const out = [];
    const a = arkusz(m, 3, true);
    const pusta = bez ? (() => { const c = document.createElement('canvas'); c.width = a.width; c.height = a.height;
      const x = c.getContext('2d'); x.fillStyle = '#ffffff'; x.fillRect(0, 0, c.width, c.height); return c; })() : a;
    const orient = m.W > m.H ? 'poziomo' : 'pionowo';
    const t0 = bez
      ? 'Zwykła kartka A4, ' + orient + '. Niebieskie liczby to centymetry od najbliższego rogu, wzdłuż krawędzi.'
      : 'Tak wygląda wydruk od strony nadruku. Czerwony trójkąt pokazuje górną krawędź. ' +
        'Do składania połóż go nadrukiem do stołu (odwróć jak stronę w książce).';
    out.push(kartaKroku('0', t0, c => {
      const s = Math.min(280 / a.width, 280 / a.height);
      c.width = Math.round(a.width * s * dpr()); c.height = Math.round(a.height * s * dpr());
      const x = c.getContext('2d');
      x.drawImage(pusta, 0, 0, c.width, c.height);
      x.strokeStyle = '#b9ae9d'; x.lineWidth = dpr(); x.strokeRect(0.5, 0.5, c.width - 1, c.height - 1);
      if (bez) {
        x.fillStyle = '#2a6fd6'; x.font = (700 * 1) + ' ' + Math.round(14 * dpr()) + 'px Figtree, system-ui, sans-serif';
        x.textAlign = 'center'; x.textBaseline = 'middle';
        x.fillText((m.W > m.H ? '29,7' : '21') + ' cm', c.width / 2, 16 * dpr());
        x.save(); x.translate(16 * dpr(), c.height / 2); x.rotate(-Math.PI / 2);
        x.fillText((m.W > m.H ? '21' : '29,7') + ' cm', 0, 0); x.restore();
      } else {
        x.fillStyle = '#d7263d';
        x.beginPath(); x.moveTo(c.width / 2, 2); x.lineTo(c.width / 2 - 10 * dpr(), 16 * dpr()); x.lineTo(c.width / 2 + 10 * dpr(), 16 * dpr()); x.fill();
      }
    }));
    for (const k of m.kroki) {
      out.push(kartaKroku(String(k.n), bez ? bezWydruku(k.t, m) : k.t,
        c => S.rysujScene(c, k.s, m, pusta, 3, { dpr: dpr(), tlo: '#ffffff', miary: bez })));
    }
    return out;
  }
  function kroki() {
    const m = model();
    const box = $('kroki');
    box.innerHTML = '';
    for (const li of kartyKrokow(m, st.bezDrukarki)) box.appendChild(li);
    const lg = $('legendaKrokow');
    if (!lg.dataset.druk) lg.dataset.druk = lg.innerHTML;
    lg.innerHTML = st.bezDrukarki
      ? 'Czerwona linia to zgięcie z danego kroku. <b>Niebieska liczba</b> to odległość w centymetrach od najbliższego rogu, ' +
        'mierzona wzdłuż krawędzi – tam zaczyna się zgięcie. „Środek” znaczy połowę krawędzi.'
      : lg.dataset.druk;
    for (const b of document.querySelectorAll('#trybKrokow button')) b.setAttribute('aria-pressed', String((b.dataset.t === 'bez') === st.bezDrukarki));
  }
  function kartaKroku(nr, tekst, rysuj) {
    const li = document.createElement('li');
    const c = document.createElement('canvas');
    c.setAttribute('aria-hidden', 'true');
    rysuj(c);
    const n = document.createElement('span');
    n.className = 'nr mono';
    n.textContent = nr;
    const p = document.createElement('p');
    p.textContent = tekst;
    li.append(c, n, p);
    return li;
  }

  /* ---------- PDF ---------- */
  function planujPdf() {
    clearTimeout(pdfTimer);
    $('save').disabled = true;
    $('open').removeAttribute('href');
    $('stats').textContent = 'Składam PDF…';
    pdfTimer = setTimeout(robPdf, 150);
  }
  async function robPdf() {
    const nr = ++pdfNr;
    const m = model();
    try {
      let bytes = await S.pdf(window.PDFLib, m, kolory(m), { tytul: m.nazwa + ' – papierowy samolot (domowydrukarz.pl)' }, st.linie);
      if (st.instr) bytes = await dolaczInstrukcje(bytes, m);
      if (nr !== pdfNr) return;
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
      pdfUrl = URL.createObjectURL(new Blob([bytes], { type: 'application/pdf' }));
      const plik = 'samolot-' + m.slug + (st.linie ? '-same-linie' : st.kolor ? '-' + nazwaKoloru().replace(/[^a-zżźćńółęąś]/gi, '') : '') + '.pdf';
      $('save').disabled = false;
      $('save').onclick = () => { const a = document.createElement('a'); a.href = pdfUrl; a.download = plik; document.body.appendChild(a); a.click(); a.remove(); };
      $('open').href = pdfUrl;
      $('stats').innerHTML = '<b>' + m.nazwa + '</b>, A4 ' + (m.W > m.H ? 'poziomo' : 'pionowo') + ', ' + (st.linie ? 'same linie zgięć' : 'kolor: ' + (st.kolor ? nazwaKoloru() : 'naturalny')) +
        ' · ' + (st.instr ? '2 strony' : '1 strona') + ' · ' + Math.max(1, Math.round(bytes.length / 1024)) + ' KB';
    } catch (e) {
      console.error(e);
      $('stats').textContent = 'Nie udało się złożyć PDF. Odśwież stronę i spróbuj jeszcze raz.';
    }
  }
  // instrukcja jako druga strona: obrazek złożony z kart kroków
  async function dolaczInstrukcje(bytes, m) {
    const doc = await window.PDFLib.PDFDocument.load(bytes);
    await stronaKrokow(doc, m, kartyKrokow(m, false), m.nazwa + ' – jak złożyć', 'domowydrukarz.pl · papierowe samoloty · ' + m.lot);
    return doc.save();
  }
  async function szablonBezDrukarki() {
    const m = model();
    const L = window.PDFLib;
    const doc = await L.PDFDocument.create();
    doc.setTitle(m.nazwa + ' – składanie bez drukarki (domowydrukarz.pl)');
    doc.setAuthor('domowydrukarz.pl');
    await stronaKrokow(doc, m, kartyKrokow(m, true), m.nazwa + ' – bez drukarki',
      'Zwykła kartka A4 i ta instrukcja. Niebieskie liczby: odległość w cm od najbliższego rogu kartki. domowydrukarz.pl');
    const bytes = await doc.save();
    const url = URL.createObjectURL(new Blob([bytes], { type: 'application/pdf' }));
    const a = document.createElement('a');
    a.href = url; a.download = 'samolot-' + m.slug + '-bez-drukarki.pdf';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }
  async function stronaKrokow(doc, m, karty, tytul, podtytul) {
    const W = 595.28, H = 841.89, sk = 2; // 144 dpi
    const c = document.createElement('canvas');
    c.width = W * sk; c.height = H * sk;
    const x = c.getContext('2d');
    x.scale(sk, sk);
    x.fillStyle = '#fff'; x.fillRect(0, 0, W, H);
    x.fillStyle = '#26221d';
    x.font = '800 26px Figtree, system-ui, sans-serif';
    x.fillText(tytul, 32, 52);
    x.font = '500 11px Figtree, system-ui, sans-serif';
    x.fillStyle = '#6b645a';
    x.fillText(podtytul, 32, 72, W - 64);
    const kol = 4, cw = (W - 64) / kol, ch = (H - 100) / Math.ceil(karty.length / kol);
    karty.forEach((li, i) => {
      const cx = 32 + (i % kol) * cw, cy = 92 + Math.floor(i / kol) * ch;
      const cv = li.querySelector('canvas');
      const s = Math.min((cw - 10) / cv.width, (ch * 0.55) / cv.height);
      x.drawImage(cv, cx + (cw - cv.width * s) / 2, cy, cv.width * s, cv.height * s);
      x.fillStyle = '#26221d';
      x.font = '800 12px Figtree, system-ui, sans-serif';
      const nr = li.querySelector('.nr').textContent + '.';
      x.fillText(nr, cx, cy + ch * 0.55 + 14);
      const wn = x.measureText(nr).width + 5;
      x.font = '400 9px Figtree, system-ui, sans-serif';
      zawijaj(x, li.querySelector('p').textContent, cx + wn, cy + ch * 0.55 + 14, cw - wn - 6, 11);
    });
    const jpg = await doc.embedJpg(c.toDataURL('image/jpeg', 0.85));
    const p = doc.addPage([W, H]);
    p.drawImage(jpg, { x: 0, y: 0, width: W, height: H });
  }
  function zawijaj(x, t, px, py, w, lh) {
    let linia = '', y = py;
    for (const s of t.split(' ')) {
      const p = linia ? linia + ' ' + s : s;
      if (x.measureText(p).width > w && linia) { x.fillText(linia, px, y); y += lh; linia = s; } else linia = p;
    }
    if (linia) x.fillText(linia, px, y);
  }

  /* ---------- całość ---------- */
  function zmiana() {
    zapiszAdres();
    miniatury();
    zaznaczKolor();
    opis();
    podglad();
    kroki();
    planujPdf();
  }

  function start() {
    czytajAdres();
    rysujModele();
    rysujKolory();
    for (const b of document.querySelectorAll('#widoki button')) b.addEventListener('click', () => { st.widok = b.dataset.w; podglad(); });
    $('instr').addEventListener('change', e => { st.instr = e.target.checked; planujPdf(); });
    $('bezMal').addEventListener('change', e => { st.linie = e.target.checked; zmiana(); });
    $('szablon').addEventListener('click', () => szablonBezDrukarki().catch(e => console.error(e)));
    for (const b of document.querySelectorAll('#trybKrokow button')) b.addEventListener('click', () => { st.bezDrukarki = b.dataset.t === 'bez'; zapiszAdres(); kroki(); });
    $('pokazBez').addEventListener('click', () => { st.bezDrukarki = true; zapiszAdres(); kroki(); $('h-kroki').scrollIntoView({ behavior: 'smooth' }); });
    zmiana();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
