// Convierte un SVG a PNG o PDF (A4 o A3 apaisado) con Chromium (Playwright).
// Uso: node svg_a_png.js entrada.svg salida.(png|pdf) [escala] [A4|A3]
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const [entrada, salida, escala = "2", hoja = "A4"] = process.argv.slice(2);
  const svg = fs.readFileSync(entrada, "utf8");
  const [, , , w, h] = svg.match(/viewBox="(-?[\d.]+) (-?[\d.]+) ([\d.]+) ([\d.]+)"/).map(Number);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: Number(escala) });
  await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  if (salida.endsWith(".pdf")) {
    await page.setContent(`<html><head><style>@page{size:${hoja} landscape;margin:8mm}body{margin:0}svg{width:100%;height:auto}</style></head><body>${svg}</body></html>`);
    await page.pdf({ path: path.resolve(salida), format: hoja, landscape: true, printBackground: true });
  } else {
    await page.screenshot({ path: path.resolve(salida), clip: { x: 0, y: 0, width: w, height: h } });
  }
  await browser.close();
})();
