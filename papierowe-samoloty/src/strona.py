"""Składa strona/index.html – narzędzie „Papierowe samoloty” w stylu domowydrukarz.pl.

Wszystko jest w jednym pliku (style, pdf-lib, dane modeli, skrypt), więc strona działa bez internetu,
tak jak pozostałe narzędzia Domowego drukarza. Style i elementy wspólne są skopiowane z domowydrukarz.pl
(katalog web/dd/).
"""
import html
import json
import os

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
WEB = os.path.join(HERE, "web")
KOLEJNOSC = ["grot", "iskra", "albatros", "jerzyk", "sokol", "bryza"]


def czytaj(*p):
    with open(os.path.join(*p), encoding="utf-8") as f:
        return f.read()


def strona():
    dane = [json.loads(czytaj(ROOT, "wyniki", "dane", f"{s}.json")) for s in KOLEJNOSC]
    dd = lambda n: czytaj(WEB, "dd", n)  # noqa: E731
    js_dane = "window.SAMOLOTY_DANE=" + json.dumps(dane, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";"
    pytania = [
        ("Po co kropki zamiast jednolitego koloru?",
         ["Kolorowe pola są wydrukowane drobnymi kropkami co milimetr. Z odległości ręki oko zlewa je w jeden, jaśniejszy odcień, "
          "a drukarka kładzie kilka razy mniej tuszu niż przy pełnym kolorze.",
          "Mniej tuszu to kartka, która się nie wygina. Pełna apla z drukarki atramentowej potrafi pofalować zwykły papier 80 g, "
          "a samolot z pofalowanej kartki lata krzywo."]),
        ("Czy mogę wybrać dowolny kolor?",
         ["Tak. Wzór zostaje ten sam, a zmienia się kolor główny. Wybierz jedną z próbek albo własny kolor w kółku na końcu listy. "
          "Detale, takie jak szachownica czy beżowe plamy, mają stałe kolory.",
          "Każdy model ma własne malowanie, a do tego sześć lekkich wzorów do wyboru: Mapa, Nawigacja, Kliny, Fale, Gwiazdozbiór i Pasy. "
          "Pasują do każdego modelu i zużywają bardzo mało tuszu."]),
        ("Czemu część samolotu jest biała?",
         ["Drukujemy jednostronnie, a po złożeniu część kartki pokazuje stronę bez nadruku – zwykle spód kadłuba i kawałek spodu skrzydeł. "
          "Malowanie jest pod to ułożone: wierzch skrzydeł jest zawsze zadrukowany, a biały spód to część wzoru."]),
        ("Linie nie trafiają w krawędzie kartki",
         ["Prawie zawsze to skalowanie w oknie drukowania. Wybierz <b>skalę 100%</b> albo „rozmiar rzeczywisty” i wyłącz "
          "„dopasuj do strony”. Linie zgięć są liczone od krawędzi kartki, więc nawet 3% różnicy przesuwa je o kilka milimetrów."]),
        ("Drukarka nie drukuje przy samym brzegu",
         ["To normalne: domowe drukarki zostawiają 3–6 mm białego paska. Napisy, oczy i znaki stoją co najmniej 5 mm od brzegu "
          "i 2,5 mm od zgięć, więc nic ważnego nie zostanie ucięte. Na końcach skrzydeł zostanie najwyżej cienki biały brzeg."]),
        ("Da się wydrukować same linie, bez malowania?",
         ["Tak. Zaznacz „Bez malowania” przy kolorach. Drukują się tylko linie zgięć z numerami kroków, więc tuszu prawie nie ubywa. "
          "Biały samolot możesz pomalować kredkami albo flamastrami – linie podpowiedzą, gdzie po złożeniu będzie skrzydło, a gdzie kadłub."]),
        ("Jak złożyć samolot bez drukarki?",
         ["Weź zwykłą kartkę A4 i pobierz szablon z sekcji „Bez drukarki”. Każdy krok ma schemat z wymiarami: niebieska liczba to odległość "
          "w centymetrach od najbliższego rogu, w której zaczyna się zgięcie. Większość zgięć to „róg do środka” albo „krawędź do krawędzi”, "
          "więc mierzysz tylko kilka miejsc."]),
        ("Czy coś zostaje wysłane?",
         ["Nie. PDF powstaje w Twojej przeglądarce, nic nie idzie na serwer. Wczytaj stronę, odłącz internet i dalej działa.",
          "Wybrany model i kolor są w adresie strony, więc wyślesz komuś link do dokładnie tego samolotu."]),
    ]
    faq = "\n".join(
        f'''   <details class="pyt">
    <summary><h3>{html.escape(q)}</h3></summary>
    <div class="odp">
{"".join(f"     <p>{p}</p>" + chr(10) for p in ps)}    </div>
   </details>''' for q, ps in pytania)
    wlasne_css = '''
/* papierowe samoloty – własny kolor narzędzia (na stronie głównej: .k-samoloty{--k:#5F7A14;--kn:#A9C653}) */
:root{--akcent:#5F7A14;--akcent-noc:#A9C653}
#modele{grid-template-columns:repeat(3,minmax(0,1fr))}
#modele canvas{display:block;width:100%;height:auto;border-radius:6px;border:1px solid var(--linia);background:#fff}
#modele small{display:block}
.przel{display:inline-flex;flex-wrap:wrap;border:1.5px solid var(--obrys);border-radius:999px;overflow:hidden}
.przel button{font:inherit;font-size:14px;font-weight:600;padding:6px 14px;background:transparent;color:var(--tusz);border:0;cursor:pointer}
.przel button+button{border-left:1.5px solid var(--obrys)}
.przel button[aria-pressed=true]{background:var(--sygnal);color:var(--na-sygnale)}
.podglad canvas{display:block;width:100%;height:auto;border:1px solid var(--obrys);background:#fff;border-radius:var(--r-maly)}
.podglad .pod{margin:8px 0 0;color:var(--szary);font-size:14.5px}
.lupa{display:flex;gap:12px;align-items:center;margin-top:14px}
.lupa canvas{width:220px;height:120px;border:1px solid var(--obrys);border-radius:var(--r-maly);background:#fff;flex:0 0 auto}
.lupa span{color:var(--szary);font-size:14px;line-height:1.45}
.karta-modelu{display:flex;flex-direction:column;gap:6px}
.karta-modelu h3{margin:0;font-family:var(--black);font-weight:800;font-size:26px;line-height:1.1}
.karta-modelu p{margin:0}
.karta-modelu .szary{color:var(--szary);font-size:15px}
.skladanie{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}
.skladanie li{background:var(--karta);border:1.5px solid var(--linia);border-radius:var(--r-maly);padding:10px 12px 12px;display:grid;grid-template-columns:auto minmax(0,1fr);gap:8px 10px;align-content:start}
.skladanie canvas{grid-column:1/-1;width:100%;height:auto;aspect-ratio:1;object-fit:contain;background:#fff;border-radius:6px}
.skladanie .nr{color:var(--sygnal);font-weight:700;font-size:15px}
.skladanie p{margin:0;font-size:15px;line-height:1.45}
.kolory.wylaczone,.przel.wylaczone{opacity:.35}
#wzory{border:0;border-radius:0;gap:8px;overflow:visible}
#wzory button{padding:6px 14px;border:1.5px solid var(--obrys);border-radius:999px}
.zaznacz{display:flex;gap:10px;align-items:flex-start;margin-top:16px;font-size:15px;max-width:62ch}
.zaznacz input{width:20px;height:20px;margin-top:2px;accent-color:var(--sygnal)}
@media (max-width:560px){#modele{grid-template-columns:repeat(2,minmax(0,1fr))}.lupa{flex-direction:column;align-items:flex-start}}
'''
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<script>{dd("motyw-start.js")}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Papierowe samoloty do druku – 6 modeli z malowaniem | Papierowe samoloty</title>
<meta name="description" content="Papierowe samoloty do wydrukowania na zwykłej kartce A4: linie zgięć i malowanie, które po złożeniu trafia na skrzydła i kadłub. Sześć modeli, dowolny kolor, PDF w przeglądarce, za darmo.">
<link rel="canonical" href="https://domowydrukarz.pl/samoloty/">
<meta property="og:type" content="website">
<meta property="og:url" content="https://domowydrukarz.pl/samoloty/">
<meta property="og:locale" content="pl_PL">
<meta property="og:title" content="Papierowe samoloty">
<meta property="og:description" content="Sześć papierowych samolotów z jednej kartki A4. Malowanie z kolorowych kropek, dowolny kolor, PDF w przeglądarce.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cstyle%3E.k%7Bstroke:%23151412%7D.p%7Bfill:%23151412%7D@media (prefers-color-scheme:dark)%7B.k%7Bstroke:%23EEEAE3%7D.p%7Bfill:%23EEEAE3%7D%7D%3C/style%3E%3Cmask id='w'%3E%3Crect width='64' height='64' fill='%23fff'/%3E%3Cpath d='M32 15v34M15 32h34' stroke='%23000' stroke-width='4.5'/%3E%3C/mask%3E%3Cpath class='k' d='M32 0v64M0 32h64' stroke-width='5'/%3E%3Ccircle class='k' cx='32' cy='32' r='22' fill='none' stroke-width='5'/%3E%3Ccircle class='p' cx='32' cy='32' r='16' mask='url(%23w)'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{dd("styl.css")}{wlasne_css}</style>
</head>
<body data-dd="samoloty">
{dd("sprite.svg")}

<div class="ticket mono">
 <div class="wrap"><a class="logo" href="https://domowydrukarz.pl/">{dd("logo.svg")}Domowy drukarz</a><span class="okruszek"><a href="https://domowydrukarz.pl/">Wszystkie narzędzia</a> › <b>Papierowe samoloty</b></span><span><span class="dot" aria-hidden="true"></span>Działa bez internetu</span><button type="button" class="motyw mono" id="motyw" aria-label="Przełącz jasny i ciemny wygląd"><span aria-hidden="true">◐</span> <span id="motywNapis">Ciemny</span></button></div>
</div>

<header class="hero">
 <div class="wrap">
  <h1>Papierowe samoloty{dd("reg.svg")}</h1>
  <p class="lead">Odskocznia od poważnych wydruków. Sześć samolotów z jednej kartki A4: linie zgięć są wtopione w malowanie, a wzór po złożeniu trafia dokładnie na skrzydła i kadłub.</p>
  <ol class="kroki">
   <li><span class="nr mono">1</span><strong>Wybierz model</strong><span class="op">Od klasycznej strzały po szybowiec i samolot patrolowy. Bez nożyczek i kleju. Podgląd pokazuje gotowy samolot.</span></li>
   <li><span class="nr mono">2</span><strong>Wybierz kolor</strong><span class="op">Wzór zostaje, kolor zmieniasz – albo drukujesz same linie. Pola są z drobnych kropek, więc drukarka atramentowa nie pofaluje kartki.</span></li>
   <li><span class="nr mono">3</span><strong>Drukuj i składaj</strong><span class="op">PDF w skali 100%, jedna strona, jednostronnie. Bez drukarki? Jest szablon z wymiarami na zwykłą kartkę.</span></li>
  </ol>
 </div>
</header>

<main>
<section aria-labelledby="h-model">
 <div class="wrap">
  <div class="nag"><span class="nr mono">1</span><h2 id="h-model">Model, wzór i kolor</h2></div>
  <div class="typy" id="modele" role="group" aria-label="Model samolotu"></div>

  <div class="rozklad" style="margin-top:28px">
   <div>
    <div class="karta-modelu">
     <h3 id="mNazwa"></h3>
     <p id="mOpis"></p>
     <p class="szary"><span id="mStyl"></span> · <span id="mTrud"></span></p>
    </div>
    <div class="opts waskie" style="margin-top:20px">
     <div class="fld"><span class="et">Wzór malowania</span><div class="przel" id="wzory" role="group" aria-label="Wzór malowania"></div><span class="pom">Każdy wzór pasuje do każdego modelu i trafia na skrzydła po złożeniu.</span></div>
     <div class="fld"><span class="et">Kolor główny</span><div class="kolory" id="kolory" role="group" aria-label="Kolor główny"></div><span class="pom" id="kolorNazwa"></span></div>
     <label class="zaznacz" style="margin-top:4px"><input type="checkbox" id="bezMal"> <span>Bez malowania – drukuj same linie zgięć. Najmniej tuszu, a samolot pomalujesz sam kredkami.</span></label>
    </div>
    <div class="druk">
     <span class="mono">Jak rzucać</span>
     <span id="mLot"></span>
    </div>
   </div>
   <figure class="podglad">
    <figcaption>Podgląd</figcaption>
    <div class="przel" id="widoki" role="group" aria-label="Widok">
     <button type="button" data-w="gora" aria-pressed="true">Złożony</button><button type="button" data-w="spod" aria-pressed="false">Od spodu</button><button type="button" data-w="arkusz" aria-pressed="false">Arkusz</button>
    </div>
    <canvas id="podglad" style="margin-top:10px" role="img" aria-label="Podgląd samolotu"></canvas>
    <p class="pod" id="podpisPodgladu"></p>
    <div class="lupa"><canvas id="lupa" aria-hidden="true"></canvas><span>Kropki w mniej więcej prawdziwej wielkości. Z odległości ręki zlewają się w jeden jasny odcień.</span></div>
   </figure>
  </div>
 </div>
</section>

<section aria-labelledby="h-wynik" id="res">
 <div class="wrap">
  <div class="nag"><span class="nr mono">2</span><h2 id="h-wynik">Do druku</h2></div>
  <div class="stat" id="stats">Składam PDF…</div>
  <div class="rzad" style="opacity:1">
   <button class="btn" id="save" type="button" disabled>Pobierz PDF</button>
   <a class="btn2" id="open" target="_blank" rel="noopener">Otwórz w nowej karcie</a>
  </div>
  <label class="zaznacz"><input type="checkbox" id="instr"> <span>Dołącz instrukcję jako drugą stronę. Drukuj ją na osobnej kartce – samolot to zawsze tylko strona 1.</span></label>
  <div class="druk">
   <span class="mono">Ustawienia drukarki</span>
   <ul>
    <li><b>Skala 100%</b> albo „rozmiar rzeczywisty”. Wyłącz „dopasuj do strony”, bo inaczej linie zgięć rozjadą się z krawędziami kartki.</li>
    <li id="orientRada">Papier <b>A4</b>.</li>
    <li>Drukuj <b>jednostronnie</b>. Wystarczy zwykła drukarka atramentowa albo laserowa.</li>
   </ul>
  </div>
 </div>
</section>

<section aria-labelledby="h-bez">
 <div class="wrap">
  <div class="nag"><span class="nr mono">3</span><h2 id="h-bez">Bez drukarki</h2></div>
  <div class="reader">
   <p class="skrot"><b>Siedzisz na lekcji albo w pracy bez drukarki? To nic.</b> Bez drukarki też złożysz. Pobierz szablon z liniami gięcia i startuj :)</p>
   <p>Szablon to kroki składania z wymiarami: niebieska liczba mówi, ile centymetrów od rogu kartki zaczyna się zgięcie. Wystarczy zwykła kartka A4, linijka albo dobre oko. Otworzysz go na telefonie obok kartki.</p>
  </div>
  <div class="rzad" style="opacity:1">
   <button class="btn" id="szablon" type="button">Pobierz szablon</button>
   <button class="btn2" id="pokazBez" type="button">Pokaż kroki z wymiarami</button>
  </div>
 </div>
</section>

<section aria-labelledby="h-kroki">
 <div class="wrap">
  <div class="nag"><span class="nr mono">4</span><h2 id="h-kroki">Jak złożyć</h2></div>
  <div class="przel" id="trybKrokow" role="group" aria-label="Wersja kroków" style="margin-bottom:14px">
   <button type="button" data-t="druk" aria-pressed="true">Z wydruku</button><button type="button" data-t="bez" aria-pressed="false">Bez drukarki, z wymiarami</button>
  </div>
  <p class="legenda" id="legendaKrokow">Linie <b>przerywane</b> to zgięcia w dolinę (od strony nadruku zgięcie robi rowek), <b>kreska z kropką</b> to grzbiet. Numery przy liniach to numery kroków. Na schematach czerwona linia pokazuje zgięcie z danego kroku.</p>
  <ol class="skladanie" id="kroki"></ol>
 </div>
</section>

<section aria-labelledby="h-pytania">
 <div class="wrap">
  <div class="nag"><span class="nr mono">?</span><h2 id="h-pytania">Pytania</h2></div>
  <div class="reader">
{faq}
  </div>
 </div>
</section>
</main>

<div class="oNim">
 <div class="wrap">
  <p class="seria mono"><a href="https://domowydrukarz.pl/">Domowy drukarz</a> · <a href="https://domowydrukarz.pl/kalendarz/">Kalendarz ze zdjęć</a> · <a href="https://domowydrukarz.pl/etykiety/">Etykiety po cztery</a> · <a href="https://domowydrukarz.pl/papier/">Papier w kratkę i linie</a> · <a href="https://domowydrukarz.pl/odbitki/">Odbitki z drukarki</a> · <a href="https://domowydrukarz.pl/kolaz/">Kolaż ze zdjęć</a> · <a href="https://domowydrukarz.pl/plakat/">Plakat z kartek</a> · <a href="https://domowydrukarz.pl/ebook/">Papierowy ebook</a> · <b>Papierowe samoloty</b></p>
 </div>
</div>
<footer class="mono"><div class="wrap"><span id="wersjaDol">Papierowe samoloty</span><span>część serii <a href="https://domowydrukarz.pl/">Domowy drukarz</a></span><span>zrobił <a href="https://melin.pl/">Jacek Melin</a></span><a class="kawa" href="https://buycoffee.to/melin" target="_blank" rel="noopener"><img src="https://buycoffee.to/static/img/share/share-button-primary--pl.png" width="146" height="38" alt="Postaw kawę – buycoffee.to"></a></div></footer>

<script>{dd("motyw.js")}</script>
<script>{czytaj(WEB, "pdf-lib.min.js")}</script>
<script>{czytaj(WEB, "samoloty-core.js")}</script>
<script>{js_dane}</script>
<script>{czytaj(WEB, "app.js")}</script>
</body>
</html>
'''


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "strona"), exist_ok=True)
    out = os.path.join(ROOT, "strona", "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(strona())
    print(out, os.path.getsize(out) // 1024, "KB")
