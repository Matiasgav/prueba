import { chromium } from 'playwright-core';
const [,, url, out] = process.argv;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 950 } });
const errs = [];
page.on('pageerror', (e) => errs.push('PAGEERROR ' + e.message));
page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
await page.goto(url + '?tab=planos');
await page.waitForTimeout(9000);
const ids = ['pl-Fachadas', 'pl-Electricidad', 'pl-Sanitaria', 'pl-Gas', 'pl-Pared', 'pl-Estructura', 'pl-Entramados'];
for (const id of ids) {
  await page.evaluate((i) => document.getElementById(i).scrollIntoView(), id);
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${out}/p-${id}.png` });
}
for (const t of ['computo', 'despiece', 'memoria']) {
  await page.goto(url + '?tab=' + t);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${out}/tab-${t}.png` });
}
console.log(errs.join('\n'));
await browser.close();
