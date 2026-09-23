// Imprime el informe HTML a PDF con Chromium (Playwright).
// Uso: NODE_PATH=$(npm root -g) node tools/pdf.js entrada.html salida.pdf
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const exe = process.env.CHROMIUM || undefined;
  const b = await chromium.launch(exe ? { executablePath: exe } : {});
  const p = await b.newPage();
  await p.goto('file://' + path.resolve(process.argv[2]), { waitUntil: 'load' });
  await p.emulateMedia({ media: 'print', colorScheme: 'light' });
  await p.pdf({ path: process.argv[3], format: 'A4', printBackground: true,
    margin: { top: '16mm', bottom: '16mm', left: '14mm', right: '14mm' },
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888">' +
      'Mitras KG m0,5 z20 — página <span class="pageNumber"></span> de <span class="totalPages"></span></div>' });
  await b.close();
})();
