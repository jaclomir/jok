// Składa PDF arkusza z danych JSON (ten sam kod co w przeglądarce). Użycie: node pdf-node.js dane.json wynik.pdf [#kolor]
const fs = require('fs');
const path = require('path');
const PDFLib = require(process.env.PDFLIB || path.join(__dirname, 'pdf-lib.min.js'));
const S = require('./samoloty-core.js');
(async () => {
  const [, , wej, wyj, kol] = process.argv;
  const model = JSON.parse(fs.readFileSync(wej, 'utf8'));
  const kolory = Object.assign({}, model.kolory, kol ? { main: kol } : {});
  const bytes = await S.pdf(PDFLib, model, kolory);
  fs.writeFileSync(wyj, bytes);
})().catch(e => { console.error(e); process.exit(1); });
