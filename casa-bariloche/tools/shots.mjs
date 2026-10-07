// Capturas del visor con Chromium headless (para verificar y documentar).
import { chromium } from 'playwright-core';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const outDir = process.argv[2] ?? path.join(root, 'docs', 'img');
fs.mkdirSync(outDir, { recursive: true });
const shots = (process.argv[3] ?? 'exterior,servicios,interior,pb,pa,instalaciones,estructura,placas,escalera,bano').split(',');
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 950 } });
const errs = [];
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.text()); });
page.on('pageerror', (e) => errs.push('PAGEERROR ' + e.message));
const url = 'file://' + path.join(root, 'dist', 'casa-bariloche.html');
for (const s of shots) {
  const [preset, amb] = s.split(':');
  await page.goto(`${url}?tab=3d&preset=${preset}${amb ? '&amb=' + amb : ''}`);
  await page.waitForTimeout(2500);
  await page.locator('#view').screenshot({ path: path.join(outDir, `3d-${preset}${amb ? '-' + amb : ''}.png`) });
  console.log('ok', s);
}
if (process.argv[4] === 'tabs') {
  for (const t of ['planos', 'computo', 'despiece', 'memoria']) {
    await page.goto(`${url}?tab=${t}`);
    await page.waitForTimeout(t === 'planos' ? 6000 : 1500);
    await page.screenshot({ path: path.join(outDir, `tab-${t}.png`), fullPage: false });
  }
}
console.log(errs.slice(0, 20).join('\n'));
await browser.close();
