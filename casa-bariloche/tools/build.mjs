// Build: memoria (md -> html), bundle de la app en un único HTML autocontenido,
// y exportación de planos SVG + cómputo CSV/MD al repositorio.
import { build } from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const P = (...a) => path.join(root, ...a);

// ---------------------------------------------------------------- markdown mínimo
export function md2html(md) {
  const inline = (s) => s
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
    .replace(/(^|[\s(])_([^_]+)_(?=[\s).,;:]|$)/g, '$1<i>$2</i>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  const lines = md.replace(/\r/g, '').split('\n');
  let out = '', i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (!l.trim()) { i++; continue; }
    let m;
    if ((m = l.match(/^(#{1,4})\s+(.*)/))) { const n = m[1].length; out += `<h${n}>${inline(m[2])}</h${n}>\n`; i++; continue; }
    if (/^---+$/.test(l.trim())) { out += '<hr>'; i++; continue; }
    if (l.startsWith('|')) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith('|')) { rows.push(lines[i]); i++; }
      const cells = (r) => r.replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      const head = cells(rows[0]);
      const body = rows.slice(2).map(cells);
      out += `<table><thead><tr>${head.map((h) => `<th>${inline(h)}</th>`).join('')}</tr></thead><tbody>${body.map((r) => `<tr>${r.map((c) => `<td>${inline(c)}</td>`).join('')}</tr>`).join('')}</tbody></table>\n`;
      continue;
    }
    if (l.startsWith('>')) {
      const b = [];
      while (i < lines.length && lines[i].startsWith('>')) { b.push(lines[i].replace(/^>\s?/, '')); i++; }
      out += `<blockquote>${b.map(inline).join('<br>')}</blockquote>\n`;
      continue;
    }
    if (/^\s*([-*]|\d+\.)\s+/.test(l)) {
      const ordered = /^\s*\d+\./.test(l);
      const items = [];
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
        let it = lines[i].replace(/^\s*([-*]|\d+\.)\s+/, '');
        i++;
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i])) { it += ' ' + lines[i].trim(); i++; }
        items.push(it);
      }
      out += `<${ordered ? 'ol' : 'ul'}>${items.map((x) => `<li>${inline(x)}</li>`).join('')}</${ordered ? 'ol' : 'ul'}>\n`;
      continue;
    }
    const para = [];
    while (i < lines.length && lines[i].trim() && !/^(#|\||>|\s*([-*]|\d+\.)\s)/.test(lines[i])) { para.push(lines[i]); i++; }
    out += `<p>${inline(para.join(' '))}</p>\n`;
  }
  return out;
}

const memo = fs.readFileSync(P('docs', 'memoria.md'), 'utf8');
fs.writeFileSync(P('src', 'memoria.gen.js'), `// generado por tools/build.mjs desde docs/memoria.md\nexport const MEMORIA_HTML = ${JSON.stringify(md2html(memo))};\n`);

// ---------------------------------------------------------------- recursos (Poly Haven CC0) embebidos
{
  const A = P('assets');
  const b64 = (f) => fs.readFileSync(f).toString('base64');
  const tex = {};
  for (const f of fs.readdirSync(path.join(A, 'tex'))) tex[f.replace('.jpg', '')] = 'data:image/jpeg;base64,' + b64(path.join(A, 'tex', f));
  const glb = {};
  for (const f of fs.readdirSync(path.join(A, 'models'))) glb[f.replace('.glb', '')] = b64(path.join(A, 'models', f));
  const hdr = b64(path.join(A, 'hdri', 'alps_field_1k.hdr'));
  const bg = 'data:image/jpeg;base64,' + b64(path.join(A, 'hdri', 'alps_field_bg.jpg'));
  fs.writeFileSync(P('src', 'assets.gen.js'), `// generado por tools/build.mjs desde assets/ (Poly Haven, CC0)\nexport const ASSETS = ${JSON.stringify({ tex, glb, hdr, bg })};\n`);
}

// ---------------------------------------------------------------- bundle
const res = await build({ entryPoints: [P('src', 'app.js')], bundle: true, minify: true, format: 'iife', write: false, target: 'es2020', legalComments: 'none' });
const js = res.outputFiles[0].text;
const html = fs.readFileSync(P('src', 'index.html'), 'utf8').replace('<!--APP-->', () => `<script>${js.replace(/<\/script/g, '<\\/script')}</script>`);
fs.mkdirSync(P('dist'), { recursive: true });
fs.writeFileSync(P('dist', 'casa-bariloche.html'), html);
// variante para publicar como Artifact (el visor agrega su propio esqueleto de documento)
const art = html
  .replace(/<!doctype html>\s*/i, '')
  .replace(/<html[^>]*>\s*/i, '').replace(/<\/html>\s*$/i, '')
  .replace(/<head>\s*/i, '').replace(/<\/head>\s*/i, '')
  .replace(/<meta charset="utf-8">\s*/i, '').replace(/<meta name="viewport"[^>]*>\s*/i, '')
  .replace(/<body>\s*/i, '').replace(/<\/body>\s*/i, '')
  .replace('<!--ARTFLAG-->', '');
fs.writeFileSync(P('dist', 'casa-bariloche.artifact.html'), art.replace('<script>', '<script>window.__ARTIFACT__=true;</script><script>'));
console.log('dist/casa-bariloche.html', (html.length / 1024).toFixed(0), 'KB');

// ---------------------------------------------------------------- planos y cómputo al repo
const { buildModel, WALLS } = await import(P('src', 'model.js'));
const { takeoff, areas, SHEETS } = await import(P('src', 'takeoff.js'));
const PL = await import(P('src', 'plans.js'));
const model = buildModel();
const T = takeoff(model);
const out = P('docs', 'planos');
fs.mkdirSync(out, { recursive: true });
const files = {
  '01-planta-baja.svg': PL.planArq(model, 'PB'),
  '02-planta-alta.svg': PL.planArq(model, 'PA'),
  '03-electrico-pb.svg': PL.planElec(model, 'PB'),
  '04-electrico-pa.svg': PL.planElec(model, 'PA'),
  '05-unifilar.svg': PL.unifilar(),
  '06-sanitaria.svg': PL.planAgua(model),
  '07-gas.svg': PL.planGas(model),
  '08-pared-servicios.svg': PL.servicesWall(model),
  '09-fundacion.svg': PL.planEstructura(model, 'fund'),
  '10-entrepiso.svg': PL.planEstructura(model, 'entrepiso'),
  '11-techo.svg': PL.planEstructura(model, 'techo'),
};
WALLS.forEach((w, i) => { files[`20-entramado-${String(i + 1).padStart(2, '0')}-${w.id}.svg`] = PL.wallFraming(model, w.id); });
for (const [f, s] of Object.entries(files)) fs.writeFileSync(path.join(out, f), s);
// despiece
const dsp = P('docs', 'despiece');
fs.mkdirSync(dsp, { recursive: true });
for (const [mat, sheets] of Object.entries(T.sheets)) {
  const faces = [...new Set(model.panels[mat].map((p) => p.face))];
  const maps = faces.map((f) => PL.faceMap(model, f));
  const cuts = sheets.map((s) => PL.sheetSvg(s, SHEETS[mat], mat));
  const page = `<!doctype html><meta charset="utf-8"><title>Despiece ${mat}</title><body style="font-family:Arial;margin:16px"><h1>${mat}: ${sheets.length} placas, ${model.panels[mat].length} piezas</h1><h2>Posición</h2>${maps.join('')}<h2>Cortes por placa</h2><div style="display:flex;flex-wrap:wrap;gap:10px">${cuts.join('')}</div></body>`;
  fs.writeFileSync(path.join(dsp, `${mat}.html`), page);
}
// cómputo
const csv = ['Capitulo;Item;Cantidad;Unidad;Criterio;Detalle', ...T.rows.map((r) => [r.cap, r.item, String(r.cant).replace('.', ','), r.unidad, r.criterio, r.detalle].map((x) => `"${String(x).replace(/"/g, '""')}"`).join(';'))].join('\n');
fs.writeFileSync(P('docs', 'computo.csv'), '﻿' + csv);
const A = areas(model.D);
let mdc = `# Cómputo de materiales (generado desde el modelo)\n\nSuperficie cubierta ${A.cubiertaTotal} m² (${A.cubiertaPorPlanta} m² por planta, medida al exterior del revestimiento) · útil PB ${A.utilPB} m² + PA ${A.utilPA} m².\n\n`;
let cap = '';
for (const r of T.rows) {
  if (r.cap !== cap) { cap = r.cap; mdc += `\n## ${cap}\n\n| Ítem | Cant. | Unidad | Criterio | Detalle |\n|---|---:|---|---|---|\n`; }
  mdc += `| ${r.item} | ${String(r.cant).replace('.', ',')} | ${r.unidad} | ${r.criterio} | ${r.detalle.replace(/\|/g, '/')} |\n`;
}
mdc += `\n## Despiece de placas\n\n| Material | Placas | Piezas | Piezas enteras |\n|---|---:|---:|---:|\n`;
for (const [mat, sh] of Object.entries(T.sheets)) mdc += `| ${mat} | ${sh.length} | ${model.panels[mat].length} | ${model.panels[mat].filter((p) => p.full).length} |\n`;
mdc += `\n## Cajas eléctricas\n\n| ID | Tipo | Circuito | Nivel | Altura (cm) | Uso |\n|---|---|---|---|---:|---|\n`;
for (const b of model.elec.boxes) mdc += `| ${b.id} | ${{ oct: 'octogonal', cuad: 'cuadrada 10x10', tab: 'tablero' }[b.tipo] ?? 'rectangular 5x10'} | ${b.circuito} | ${b.nivel} | ${b.tipo === 'oct' ? 'techo' : Math.round(b.alturaPiso * 100)} | ${b.desc} |\n`;
fs.writeFileSync(P('docs', 'computo.md'), mdc);
console.log('planos:', Object.keys(files).length, '· filas de cómputo:', T.rows.length);
