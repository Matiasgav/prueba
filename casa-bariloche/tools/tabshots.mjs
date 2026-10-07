// Capturas de las pestañas (verificación visual)
import { chromium } from 'playwright-core';
const [,, url, out, ...ids] = process.argv;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 950 } });
const errs = [];
page.on('pageerror', (e) => errs.push('PAGEERROR ' + e.message));
page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
for (const t of ids.length ? ids : ['estudio', 'planos', 'computo', 'despiece', 'memoria']) {
  const [tab, anchor] = t.split('#');
  await page.goto(url + '?tab=' + tab);
  await page.waitForTimeout(tab === 'planos' ? 12000 : 3000);
  if (anchor) { await page.evaluate((a) => document.getElementById(a)?.scrollIntoView(), anchor); await page.waitForTimeout(500); }
  await page.screenshot({ path: `${out}/tab-${t.replace('#', '-')}.png` });
}
console.log(errs.join('\n'));
await browser.close();
