// Planos 2D (SVG) generados desde el modelo.
import { SPECS } from './specs.js';
import { CIRC, WALLS } from './model.js';
import { r2 } from './geom.js';

const S = 100; // px por metro (1:50 -> 2 px/mm en pantalla)
const M = 160; // margen en px
const FONT = "font-family='Inter, Arial, sans-serif'";

const STYLE = `
<style>
 .wall{fill:#2b2f33} .wallc{fill:#cfcac0;stroke:#2b2f33;stroke-width:1.2}
 .ins{fill:url(#ins)} .thin{stroke:#2b2f33;stroke-width:.8;fill:none}
 .open{fill:#fff;stroke:none} .glass{stroke:#3b82c4;stroke-width:1.2;fill:none}
 .swing{stroke:#555;stroke-width:.8;fill:none;stroke-dasharray:4 3}
 .furn{fill:#f6f3ec;stroke:#7a6f60;stroke-width:1} .furnhi{fill:none;stroke:#7a6f60;stroke-width:1;stroke-dasharray:6 4}
 .art{fill:#fff;stroke:#3a4a5a;stroke-width:1.2}
 .lbl{font-size:12px;fill:#333} .lbls{font-size:10px;fill:#555} .room{font-size:15px;font-weight:600;fill:#222}
 .area{font-size:12px;fill:#666} .dim{stroke:#a33;stroke-width:.8;fill:none} .dimt{font-size:11px;fill:#a33}
 .ttl{font-size:20px;font-weight:700;fill:#1f2933} .sub{font-size:12px;fill:#52606d}
 .stair{stroke:#555;stroke-width:.8;fill:#efe7dc} .staird{stroke:#777;stroke-width:.8;fill:none;stroke-dasharray:5 4}
 .ghost{opacity:.35} .grid{stroke:#e6e2da;stroke-width:.5}
</style>
<defs>
 <pattern id="ins" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#f6e7a5"/><line x1="0" y1="0" x2="0" y2="10" stroke="#d8b84c" stroke-width="2"/></pattern>
 <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker>
 <marker id="tick" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M2,8 L8,2" stroke="#a33" stroke-width="1.4"/></marker>
</defs>`;

const fmt = (m) => (Math.round(m * 100) / 100).toFixed(2).replace('.', ',');
const cm = (m) => String(Math.round(m * 100));
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// ------------------------------------------------------------------ planta: transformación
function planTf(D) {
  const x0 = D.cOut, x1 = D.Li - D.cOut, y0 = D.cOut, y1 = D.Wi - D.cOut;
  const W = (y1 - y0) * S + 2 * M, H = (x1 - x0) * S + 2 * M + 60;
  // frente abajo, pared de servicios a la izquierda (vista desde arriba)
  const X = (x, y) => M + (y1 - y) * S;
  const Y = (x, y) => M + 60 + (x1 - x) * S;
  const P = (x, y) => `${r2(X(x, y))},${r2(Y(x, y))}`;
  return { W, H, X, Y, P, x0, x1, y0, y1 };
}

function poly(tf, pts, cls, extra = '') {
  return `<polygon points="${pts.map(([x, y]) => tf.P(x, y)).join(' ')}" class="${cls}" ${extra}/>`;
}
function rectXY(tf, x0, y0, x1, y1, cls, extra = '') {
  return poly(tf, [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], cls, extra);
}
function line(tf, a, b, cls, extra = '') {
  return `<line x1="${r2(tf.X(...a))}" y1="${r2(tf.Y(...a))}" x2="${r2(tf.X(...b))}" y2="${r2(tf.Y(...b))}" class="${cls}" ${extra}/>`;
}
function text(tf, x, y, t, cls = 'lbl', anchor = 'middle', extra = '') {
  return `<text x="${r2(tf.X(x, y))}" y="${r2(tf.Y(x, y))}" class="${cls}" text-anchor="${anchor}" ${FONT} ${extra}>${esc(t)}</text>`;
}

// cota entre dos puntos del plano (en coordenadas modelo) desplazada "off" px perpendicular
function dimPx(x1, y1, x2, y2, off, label) {
  const dx = x2 - x1, dy = y2 - y1;
  const L = Math.hypot(dx, dy) || 1;
  const nx = -dy / L, ny = dx / L;
  const a = [x1 + nx * off, y1 + ny * off], b = [x2 + nx * off, y2 + ny * off];
  const mx = (a[0] + b[0]) / 2 + nx * 10, my = (a[1] + b[1]) / 2 + ny * 10;
  const ang = (Math.atan2(dy, dx) * 180) / Math.PI;
  const rot = ang > 90 || ang < -90 ? ang + 180 : ang;
  return `<line x1="${x1}" y1="${y1}" x2="${a[0]}" y2="${a[1]}" class="dim" stroke-dasharray="2 2"/><line x1="${x2}" y1="${y2}" x2="${b[0]}" y2="${b[1]}" class="dim" stroke-dasharray="2 2"/>
<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" class="dim" marker-start="url(#tick)" marker-end="url(#tick)"/>
<text x="${mx}" y="${my + 4}" class="dimt" text-anchor="middle" ${FONT} transform="rotate(${rot} ${mx} ${my})">${label}</text>`;
}
function dim(tf, a, b, off, label) {
  return dimPx(r2(tf.X(...a)), r2(tf.Y(...a)), r2(tf.X(...b)), r2(tf.Y(...b)), off, label ?? cm(Math.hypot(b[0] - a[0], b[1] - a[1])));
}
// cadena de cotas sobre un lado
function dimChain(tf, pts, off) {
  let s = '';
  for (let i = 0; i < pts.length - 1; i++) s += dim(tf, pts[i], pts[i + 1], off);
  return s;
}

function header(title, sub, W) {
  return `<text x="24" y="34" class="ttl" ${FONT}>${esc(title)}</text><text x="24" y="54" class="sub" ${FONT}>${esc(sub)}</text>
<text x="24" y="72" class="sub" ${FONT}>Casa Bariloche · etapa 1 · escala 1:50 en impresión A3</text>`;
}

// ------------------------------------------------------------------ muros + aberturas en planta
function wallsPlan(tf, D, level, opts = {}) {
  const { Li, Wi, cOut, sOut, OPEN } = D;
  let s = '';
  // anillo de muros exteriores
  const outer = [[cOut, cOut], [Li - cOut, cOut], [Li - cOut, Wi - cOut], [cOut, Wi - cOut]];
  const inner = [[0, 0], [Li, 0], [Li, Wi], [0, Wi]];
  const toPath = (pts) => 'M' + pts.map(([x, y]) => tf.P(x, y)).join(' L') + ' Z';
  s += `<path d="${toPath(outer)} ${toPath(inner)}" fill-rule="evenodd" class="ins"/>`;
  // capas: chapa/siding, OSB, placa interior
  s += `<path d="${toPath(outer)} ${toPath([[D.bOut, D.bOut], [Li - D.bOut, D.bOut], [Li - D.bOut, Wi - D.bOut], [D.bOut, Wi - D.bOut]])}" fill-rule="evenodd" fill="#2b2f33"/>`;
  s += `<path d="${toPath([[D.oOut, D.oOut], [Li - D.oOut, D.oOut], [Li - D.oOut, Wi - D.oOut], [D.oOut, Wi - D.oOut]])} ${toPath([[sOut, sOut], [Li - sOut, sOut], [Li - sOut, Wi - sOut], [sOut, Wi - sOut]])}" fill-rule="evenodd" fill="#b8925a"/>`;
  s += `<path d="${toPath([[-D.tD, -D.tD], [Li + D.tD, -D.tD], [Li + D.tD, Wi + D.tD], [-D.tD, Wi + D.tD]])} ${toPath(inner)}" fill-rule="evenodd" fill="#8d8a84"/>`;
  s += poly(tf, outer, 'thin');
  s += poly(tf, inner, 'thin');
  if (level === 'PB') {
    s += rectXY(tf, 2.33, 1.965, 2.425, Wi, 'wallc');
    s += rectXY(tf, 2.33, 1.965, Li, 2.06, 'wallc');
  }
  // aberturas
  for (const [k, o] of Object.entries(OPEN)) {
    if (o.level !== level || opts.noOpen) continue;
    if (o.wall === 'TAB_B') {
      s += rectXY(tf, o.s0, 1.96, o.s1, 2.065, 'open');
      // abre hacia el pasillo (y<1.965), bisagra en s0
      const r = o.leaf;
      const hx = o.s0 + 0.03, hy = 1.965;
      s += line(tf, [hx, hy], [hx, hy - r], 'thin', 'stroke-width="1.6"');
      s += `<path d="M${tf.P(hx, hy - r)} A${r * S},${r * S} 0 0 0 ${tf.P(hx + r, hy)}" class="swing"/>`;
      s += text(tf, (o.s0 + o.s1) / 2, 2.0, `${k}`, 'lbls', 'middle', 'dy="16"');
      continue;
    }
    const front = o.wall === 'FRENTE';
    const xa = front ? cOut - 0.005 : Li + 0.005, xb = front ? 0.005 : Li - cOut + 0.005;
    s += rectXY(tf, Math.min(xa, xb), o.s0, Math.max(xa, xb), o.s1, 'open');
    s += line(tf, [front ? cOut : Li - cOut, o.s0], [front ? 0 : Li, o.s0], 'thin');
    s += line(tf, [front ? cOut : Li - cOut, o.s1], [front ? 0 : Li, o.s1], 'thin');
    if (o.door) {
      // puerta de entrada: abre hacia adentro, bisagra del lado s1
      const r = o.leaf;
      const hy = o.s1 - 0.05, hx = 0;
      s += line(tf, [hx, hy], [hx + r, hy], 'thin', 'stroke-width="1.6"');
      s += `<path d="M${tf.P(hx + r, hy)} A${r * S},${r * S} 0 0 1 ${tf.P(hx, hy - r)}" class="swing"/>`;
      s += text(tf, front ? -0.45 : Li + 0.45, (o.s0 + o.s1) / 2, `${k}`, 'lbl');
    } else {
      const xm = front ? D.sOut + 0.03 : Li - D.sOut - 0.03;
      s += line(tf, [xm - 0.02, o.s0], [xm - 0.02, o.s1], 'glass');
      s += line(tf, [xm + 0.02, o.s0], [xm + 0.02, o.s1], 'glass');
      s += line(tf, [front ? 0 : Li, o.s0], [front ? 0 : Li, o.s1], 'thin');
      s += text(tf, front ? -0.42 : Li + 0.42, (o.s0 + o.s1) / 2, `${k} ${cm(o.s1 - o.s0)}x${cm(o.z1 - o.z0)}`, 'lbls');
      if (opts.sill) s += text(tf, front ? -0.42 : Li + 0.42, (o.s0 + o.s1) / 2, `antepecho ${cm(o.z0 - (level === 'PA' ? D.ZF1 : 0))}`, 'lbls', 'middle', 'dy="13"');
    }
  }
  return s;
}

// ------------------------------------------------------------------ escalera en planta
function stairPlan(tf, D, level) {
  const { ST, fGF } = D;
  let s = '';
  const cutK = 6; // corte de la planta a ~1,2 m
  if (level === 'PB') {
    for (let k = 1; k <= 10; k++) {
      const xa = ST.xBottom - ST.going * k;
      const cls = k <= cutK ? 'stair' : 'staird';
      s += rectXY(tf, xa, 0.0, xa + ST.going, ST.width, cls);
    }
    // compensados (punteados: por encima del corte)
    const P = [ST.xTop, ST.width];
    const t = Math.tan(Math.PI / 6) * ST.width;
    for (const q of [[ST.xTop, 0], [ST.xTop - t, 0], [0, ST.width - t], [0, ST.width]]) s += line(tf, P, q, 'staird');
    s += rectXY(tf, 0, 0, ST.xTop, ST.width, 'staird');
    // línea de corte y flecha
    const xc = ST.xBottom - ST.going * cutK;
    s += line(tf, [xc + 0.05, 0], [xc - 0.15, ST.width], 'thin', 'stroke-width="1.4"');
    s += `<path d="M${tf.P(ST.xBottom + 0.1, ST.width / 2)} L${tf.P(ST.xTop + 0.2, ST.width / 2)}" stroke="#333" stroke-width="1.2" fill="none" marker-end="url(#arr)"/>`;
    s += text(tf, ST.xBottom - 0.4, ST.width / 2, 'SUBE 14 alzadas', 'lbls', 'middle', 'dy="-6"');
    s += text(tf, 1.8, ST.width / 2, `a=${(ST.rise * 100).toFixed(1)} h=${ST.going * 100}`, 'lbls', 'middle', 'dy="14"');
  } else {
    const H = ST.hole;
    for (let k = 1; k <= 10; k++) {
      const xa = ST.xBottom - ST.going * k;
      s += rectXY(tf, xa, 0.0, xa + ST.going, ST.width, 'stair');
    }
    const P = [ST.xTop, ST.width];
    const t = Math.tan(Math.PI / 6) * ST.width;
    s += rectXY(tf, 0, 0, ST.xTop, ST.width, 'stair');
    for (const q of [[ST.xTop, 0], [ST.xTop - t, 0], [0, ST.width - t], [0, ST.width]]) s += line(tf, P, q, 'thin');
    s += rectXY(tf, H.x0, H.y0, H.x1, H.y1, 'thin', 'stroke-dasharray="8 4"');
    // baranda
    s += line(tf, [ST.xTop, H.y1], [H.x1, H.y1], 'thin', 'stroke-width="3"');
    s += line(tf, [H.x1, H.y1], [H.x1, 0], 'thin', 'stroke-width="3"');
    s += `<path d="M${tf.P(ST.xTop + 0.4, ST.width / 2)} L${tf.P(2.7, ST.width / 2)}" stroke="#333" stroke-width="1.2" fill="none" marker-end="url(#arr)"/>`;
    s += text(tf, 1.7, ST.width / 2, 'BAJA', 'lbls', 'middle', 'dy="-6"');
    s += text(tf, 1.6, ST.width / 2, 'hueco 290x85 · baranda h 95', 'lbls', 'middle', 'dy="14"');
  }
  void fGF;
  return s;
}

// ------------------------------------------------------------------ muebles y artefactos en planta
function footprint(el) {
  if (el.kind === 'box') return { t: 'r', x0: el.min[0], y0: el.min[1], x1: el.max[0], y1: el.max[1] };
  if (el.kind === 'cyl' && el.axis === 'z') return { t: 'c', x: el.c[0], y: el.c[1], r: el.r };
  return null;
}
function furniturePlan(tf, model, level, faint = false) {
  let s = '';
  const want = (p) => p === level || (level === 'PB' && p === 'PB-alto');
  for (const el of model.elements) {
    if (!el.plan || !want(el.plan)) continue;
    const f = footprint(el);
    if (!f) continue;
    const cls = el.plan === 'PB-alto' ? 'furnhi' : ['cocina', 'bano', 'calefaccion', 'electrico'].includes(el.layer) ? 'art' : 'furn';
    if (f.t === 'r') s += rectXY(tf, f.x0, f.y0, f.x1, f.y1, cls);
    else s += `<circle cx="${r2(tf.X(f.x, f.y))}" cy="${r2(tf.Y(f.x, f.y))}" r="${f.r * S}" class="${cls}"/>`;
    if (!faint) {
      const lbl = shortName(el.planName ?? el.name);
      if (lbl) {
        const cx = f.t === 'r' ? (f.x0 + f.x1) / 2 : f.x, cy = f.t === 'r' ? (f.y0 + f.y1) / 2 : f.y;
        s += text(tf, cx, cy, lbl, 'lbls', 'middle', 'dy="4"');
      }
    }
  }
  return faint ? `<g class="ghost">${s}</g>` : s;
}
function shortName(n) {
  const map = [
    [/^Bajomesada/, 'bacha'], [/^Lavarropas/, 'lavarropas'], [/^Mesada/, ''], [/^Cocina a gas/, 'cocina 51'], [/^Heladera/, 'heladera'], [/^Alacena/, 'alacena (alta)'],
    [/^Receptáculo/, 'ducha 80x120'], [/^Mochila/, ''], [/^Taza/, 'inodoro'], [/^Lavatorio/, 'lav.'], [/^Calefactor/, 'TB 3000'],
    [/^Zapatero/, 'zapatero'], [/^Banco-sofá/, 'banco-sofá'], [/^Mesa 80/, 'mesa 80x60'], [/^Silla/, ''], [/^Escritorio/, 'escritorio'],
    [/^Placard/, 'placard 150'], [/^Cama 2/, 'cama 2 pl. 140x190'], [/^Cama 1/, 'cama 1 pl.'], [/^Mesa de luz/, 'm.luz'], [/^Tablero/, 'TP'],
  ];
  for (const [re, t] of map) if (re.test(n)) return t;
  return '';
}

function roomsPlan(tf, model, level) {
  let s = '';
  for (const r of model.rooms) {
    if (r.level !== level || r.id === 'esc') continue;
    let a = 0;
    const ring = [...r.ring, r.ring[0]];
    for (let i = 0; i < ring.length - 1; i++) a += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1];
    a = Math.abs(a) / 2;
    s += text(tf, r.label[0], r.label[1], r.name, 'room');
    s += text(tf, r.label[0], r.label[1], `${fmt(a)} m²`, 'area', 'middle', 'dy="16"');
  }
  return s;
}

function dimsPlan(tf, D, level) {
  const { Li, Wi, cOut, OPEN } = D;
  let s = '';
  // totales exteriores
  s += dim(tf, [cOut, Wi - cOut], [cOut, cOut], 70, `${cm(Wi - 2 * cOut)} ext.`);
  s += dim(tf, [cOut, cOut], [Li - cOut, cOut], 70, `${cm(Li - 2 * cOut)} ext.`);
  // interiores
  s += dim(tf, [0, Wi], [0, 0], 42, `${cm(Wi)} int.`);
  s += dim(tf, [0, 0], [Li, 0], 42, `${cm(Li)} int.`);
  // aberturas del frente y fondo
  for (const wall of ['FRENTE', 'FONDO']) {
    const x = wall === 'FRENTE' ? cOut : Li - cOut;
    const ops = Object.values(OPEN).filter((o) => o.wall === wall && o.level === level).sort((a, b) => a.s0 - b.s0);
    const pts = [0, ...ops.flatMap((o) => [o.s0, o.s1]), Wi];
    const arr = pts.map((y) => [x, y]);
    if (wall === 'FRENTE') s += dimChain(tf, arr.slice().reverse(), -20);
    else s += dimChain(tf, arr, -20);
  }
  if (level === 'PB') {
    s += dim(tf, [2.33, Wi], [0, Wi], 42, '233');
    s += dim(tf, [Li, Wi], [2.425, Wi], 42, '194');
  }
  return s;
}

function sectionMarks(tf, D) {
  const { Li, Wi, cOut } = D;
  let s = '';
  const mk = (a, b, n) => {
    s += line(tf, a, b, 'thin', 'stroke-dasharray="14 4 3 4" stroke="#1f6feb" stroke-width="1.2"');
    s += `<circle cx="${r2(tf.X(...a))}" cy="${r2(tf.Y(...a))}" r="11" fill="#1f6feb"/><text x="${r2(tf.X(...a))}" y="${r2(tf.Y(...a)) + 4}" fill="#fff" font-size="11" text-anchor="middle" ${FONT}>${n}</text>`;
    s += `<circle cx="${r2(tf.X(...b))}" cy="${r2(tf.Y(...b))}" r="11" fill="#1f6feb"/><text x="${r2(tf.X(...b))}" y="${r2(tf.Y(...b)) + 4}" fill="#fff" font-size="11" text-anchor="middle" ${FONT}>${n}</text>`;
  };
  mk([cOut - 0.5, 1.6], [Li - cOut + 0.5, 1.6], 'A');
  mk([3.0, cOut - 0.5], [3.0, Wi - cOut + 0.5], 'B');
  return s;
}

function sheetWrap(tf, title, sub, body, legend = '') {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${tf.W} ${tf.H + (legend ? 150 : 0)}" width="${tf.W}" height="${tf.H + (legend ? 150 : 0)}" ${FONT}>${STYLE}
<rect width="100%" height="100%" fill="#fff"/>${header(title, sub, tf.W)}${body}${legend ? `<g transform="translate(24,${tf.H - 10})">${legend}</g>` : ''}
<text x="24" y="${tf.H + (legend ? 150 : 0) - 12}" class="sub" ${FONT}>Frente (acceso) abajo · pared de servicios a la izquierda · cotas en cm</text></svg>`;
}

// ================================================================== PLANOS
export function planArq(model, level) {
  const D = model.D;
  const tf = planTf(D);
  let b = wallsPlan(tf, D, level, { sill: true });
  b += stairPlan(tf, D, level);
  b += furniturePlan(tf, model, level);
  b += roomsPlan(tf, model, level);
  b += dimsPlan(tf, D, level);
  if (level === 'PB') b += sectionMarks(tf, D);
  b += text(tf, D.cOut - 0.9, D.Wi / 2, 'FRENTE / ACCESO', 'sub', 'middle', 'dy="40"');
  b += text(tf, D.Li / 2, D.Wi - D.cOut + 1.0, 'PARED DE SERVICIOS (registrable desde el exterior)', 'sub', 'middle', `transform="rotate(-90 ${r2(tf.X(D.Li / 2, D.Wi - D.cOut + 1.0))} ${r2(tf.Y(D.Li / 2, D.Wi - D.cOut + 1.0))})"`);
  const t = level === 'PB' ? 'Planta baja — arquitectura y amoblamiento' : 'Planta alta — dormitorio/estudio (loft)';
  const sub = level === 'PB' ? `NPT ±0,00 (platea +0,15 s/terreno) · cielorraso +2,41` : `NPT +${fmt(D.ZF1)} · muros laterales 2,10 · cielorraso inclinado 30° hasta 3,10 en cumbrera`;
  return sheetWrap(tf, t, sub, b);
}

function basePlan(model, level) {
  const D = model.D;
  const tf = planTf(D);
  let b = `<g opacity=".55">${wallsPlan(tf, D, level)}${stairPlan(tf, D, level)}</g>`;
  b += furniturePlan(tf, model, level, true);
  return { tf, b, D };
}

export function planElec(model, level) {
  const { tf, D } = basePlan(model, level);
  let { b } = basePlan(model, level);
  const lv = (bx) => bx.nivel === level;
  for (const c of model.elec.conduits) {
    if (!c.pts) continue;
    const bx = model.elec.boxes.find((x) => x.id === c.to);
    if (!bx || !lv(bx)) continue;
    const col = CIRC[c.circuito]?.color ?? '#555';
    const pts = c.pts.map(([x, y]) => tf.P(x, y)).join(' ');
    b += `<polyline points="${pts}" fill="none" stroke="${col}" stroke-width="1.6" stroke-dasharray="${c.route === 'platea' ? '2 3' : '7 4'}" opacity=".85"/>`;
  }
  // tablero
  if (level === 'PB') {
    b += rectXY(tf, 2.33, 2.25, 2.39, 2.55, '', 'fill="#222"');
    b += text(tf, 2.36, 2.4, 'TP', 'lbl', 'middle', 'dx="-22" dy="4" font-weight="700"');
  }
  const groupsLbl = {};
  for (const bx of model.elec.boxes.filter(lv)) {
    const [x, y] = bx.pos;
    const cx = r2(tf.X(x, y)), cy = r2(tf.Y(x, y));
    const col = CIRC[bx.circuito].color;
    let sym;
    if (bx.tipo === 'oct') sym = `<circle cx="${cx}" cy="${cy}" r="9" fill="#fff" stroke="${col}" stroke-width="2"/><path d="M${cx - 6},${cy - 6} L${cx + 6},${cy + 6} M${cx - 6},${cy + 6} L${cx + 6},${cy - 6}" stroke="${col}" stroke-width="1.6"/>`;
    else if (/^S/.test(bx.id)) sym = `<circle cx="${cx}" cy="${cy}" r="7" fill="${col}"/><text x="${cx}" y="${cy + 3.5}" font-size="9" fill="#fff" text-anchor="middle" ${FONT}>S</text>`;
    else if (/^(A|LE|LB|LK)/.test(bx.id)) sym = `<circle cx="${cx}" cy="${cy}" r="7" fill="#fff" stroke="${col}" stroke-width="2"/><path d="M${cx - 7},${cy} A7,7 0 0 1 ${cx + 7},${cy} Z" fill="${col}"/>`;
    else sym = `<rect x="${cx - 7}" y="${cy - 7}" width="14" height="14" fill="#fff" stroke="${col}" stroke-width="2"/><path d="M${cx - 4},${cy} L${cx + 4},${cy}" stroke="${col}" stroke-width="2"/>`;
    b += sym;
    const key = `${Math.round(x * 20)}_${Math.round(y * 20)}`;
    (groupsLbl[key] ??= { cx, cy, items: [] }).items.push(`${bx.id} ${bx.tipo === 'oct' ? 'techo' : 'h' + cm(bx.alturaPiso)}`);
  }
  for (const g of Object.values(groupsLbl)) {
    g.items.forEach((t, i) => { b += `<text x="${g.cx + 11}" y="${g.cy - 4 + i * 12}" font-size="10" font-weight="600" fill="#222" ${FONT}>${t}</text>`; });
  }
  let lg = '';
  Object.entries(CIRC).forEach(([k, c], i) => {
    lg += `<rect x="${(i % 2) * 360}" y="${Math.floor(i / 2) * 22}" width="22" height="4" fill="${c.color}"/><text x="${(i % 2) * 360 + 30}" y="${Math.floor(i / 2) * 22 + 6}" font-size="11" ${FONT}>${esc(c.name)} · PIA ${c.pia} · ${esc(c.cable)}</text>`;
  });
  lg += `<g transform="translate(0,52)"><circle cx="8" cy="0" r="7" fill="#fff" stroke="#333" stroke-width="2"/><path d="M3,-5 L13,5 M3,5 L13,-5" stroke="#333"/><text x="22" y="4" font-size="11" ${FONT}>boca de techo (caja octogonal)</text>
  <rect x="200" y="-7" width="14" height="14" fill="#fff" stroke="#333" stroke-width="2"/><text x="222" y="4" font-size="11" ${FONT}>toma (caja rect. 5x10)</text>
  <circle cx="368" cy="0" r="7" fill="#333"/><text x="368" y="3.5" font-size="9" fill="#fff" text-anchor="middle">S</text><text x="382" y="4" font-size="11" ${FONT}>llave de luz</text>
  <circle cx="488" cy="0" r="7" fill="#fff" stroke="#333" stroke-width="2"/><path d="M481,0 A7,7 0 0 1 495,0 Z" fill="#333"/><text x="502" y="4" font-size="11" ${FONT}>aplique</text>
  <line x1="580" y1="0" x2="620" y2="0" stroke="#333" stroke-dasharray="7 4" stroke-width="1.6"/><text x="626" y="4" font-size="11" ${FONT}>cañería por cielorraso/muro</text>
  <line x1="580" y1="18" x2="620" y2="18" stroke="#333" stroke-dasharray="2 3" stroke-width="1.6"/><text x="626" y="22" font-size="11" ${FONT}>cañería embutida en platea</text></g>
  <text x="0" y="96" font-size="11" fill="#555" ${FONT}>h = altura de eje de caja sobre piso terminado. Tomas a h 30 / 110 (mesada) / 85 (escritorio) / 65 (mesas de luz). Tablero con disyuntor 40A 30mA, PAT con jabalina.</text>`;
  return sheetWrap(tf, `Instalación eléctrica — ${level === 'PB' ? 'planta baja' : 'planta alta'}`, 'Ubicación de cada caja según el amoblamiento propuesto · circuitos AEA 90364 (vivienda)', b, lg);
}

function pipesPlan(model, level, layers, title, sub, legendItems) {
  const { tf, D } = basePlan(model, level);
  let { b } = basePlan(model, level);
  const cols = { agua_fria: '#2f7fd6', agua_caliente: '#d83b2d', desague: '#c26a12', ventilacion: '#8a5a2b', gas: '#c9a400' };
  for (const el of model.elements) {
    if (!layers.includes(el.layer)) continue;
    if (el.kind === 'tube') {
      const pts = el.pts.map(([x, y]) => tf.P(x, y)).join(' ');
      const w = el.r > 0.04 ? 5 : el.r > 0.02 ? 3.5 : 2.4;
      b += `<polyline points="${pts}" fill="none" stroke="${cols[el.layer]}" stroke-width="${w}" stroke-linejoin="round" opacity=".9"/>`;
    } else if (el.kind === 'cyl' && el.mat === 'llave_paso') {
      b += `<circle cx="${r2(tf.X(el.c[0], el.c[1]))}" cy="${r2(tf.Y(el.c[0], el.c[1]))}" r="5" fill="#c33" stroke="#fff"/>`;
    } else {
      const f = footprint(el);
      if (f?.t === 'r') b += rectXY(tf, f.x0, f.y0, f.x1, f.y1, '', `fill="none" stroke="${cols[el.layer] ?? '#555'}" stroke-width="1.5"`);
      if (f?.t === 'c') b += `<circle cx="${r2(tf.X(f.x, f.y))}" cy="${r2(tf.Y(f.x, f.y))}" r="${f.r * S}" fill="none" stroke="${cols[el.layer] ?? '#555'}" stroke-width="1.5"/>`;
    }
  }
  for (const [x, y, t, anchor = 'start'] of legendItems.labels ?? []) b += text(tf, x, y, t, 'lbls', anchor);
  let lg = '';
  legendItems.keys.forEach(([c, t], i) => {
    lg += `<rect x="${(i % 3) * 300}" y="${Math.floor(i / 3) * 22}" width="22" height="5" fill="${c}"/><text x="${(i % 3) * 300 + 30}" y="${Math.floor(i / 3) * 22 + 6}" font-size="11" ${FONT}>${esc(t)}</text>`;
  });
  lg += `<text x="0" y="70" font-size="11" fill="#555" ${FONT}>${esc(legendItems.note ?? '')}</text>`;
  return sheetWrap(tf, title, sub, b, lg);
}

export function planAgua(model) {
  const W = model.D.Wi;
  return pipesPlan(model, 'PB', ['agua_fria', 'agua_caliente', 'desague', 'ventilacion'], 'Instalación sanitaria — agua fría, caliente y desagües', 'Todo en una sola pared de servicios · llaves de paso accesibles desde los registros exteriores R1–R4', {
    keys: [['#2f7fd6', 'Agua fría PPR Ø20'], ['#d83b2d', 'Agua caliente PPR Ø20 (aislada)'], ['#c26a12', 'Desagüe PVC Ø110 / Ø63 / Ø50 / Ø40'], ['#8a5a2b', 'Ventilación Ø63 a techo'], ['#c33', '● llave de paso']],
    labels: [[3.22, W + 0.85, 'CI 60x60'], [0.55, W + 0.6, 'BA cocina'], [2.95, 2.45, 'PPA Ø63'], [2.25, W + 1.6, 'acometida agua (medidor en LM)'], [3.0, W + 1.3, '→ red cloacal o sistema séptico']],
    note: 'Termotanque eléctrico 50 l sobre el inodoro. Cañerías en la cavidad del lado caliente de la aislación: se accede retirando el registro exterior y corriendo la lana.',
  });
}

export function planGas(model) {
  const W = model.D.Wi, L = model.D.Li;
  return pipesPlan(model, 'PB', ['gas', 'calefaccion'], 'Instalación de gas', 'Cocina 56 cm + calefactor tiro balanceado 3000 kcal/h · cañería termofusión PE-AL-PE aprobada · sin uniones dentro de muros fuera de registros', {
    keys: [['#c9a400', 'Gas (Ø20/25)'], ['#c33', '● llave de paso'], ['#888', 'Rejillas de ventilación alta y baja (cocina)']],
    labels: [[2.15, W + 1.4, 'acometida gas desde medidor en LM'], [L - 0.3, 1.4, 'TB 3000', 'end'], [1.2, W - 0.4, 'cocina'], [L + 0.5, 1.25, 'terminal exterior']],
    note: 'Proyecto, cálculo de diámetros y aprobación: gasista matriculado (Camuzzi Gas del Sur, normas NAG-200). Verificar distancias del terminal TB a aberturas.',
  });
}

// ------------------------------------------------------------------ pared de servicios (vista desde el exterior sin registros)
export function servicesWall(model) {
  const D = model.D;
  const x0 = D.cOut - 0.2, x1 = D.Li - D.cOut + 0.2, z0 = -0.9, z1 = D.ZT2 + 0.7;
  const s = 120;
  const W = (x1 - x0) * s + 60 + 260, H = (z1 - z0) * s + 160;
  // vista desde el exterior: x crece hacia la izquierda (el frente queda a la derecha)
  const X = (x) => 60 + (x1 - x) * s;
  const Z = (z) => 110 + (z1 - z) * s;
  let b = '';
  b += `<rect x="${X(x1)}" y="${Z(0)}" width="${(x1 - x0) * s}" height="${(0 - z0) * s}" fill="#efe9df"/>`;
  b += `<line x1="${X(x1)}" y1="${Z(-0.15)}" x2="${X(x0)}" y2="${Z(-0.15)}" stroke="#7a6f60" stroke-dasharray="6 4"/><text x="${X(x0) - 4}" y="${Z(-0.15) - 4}" font-size="11" text-anchor="end" ${FONT}>terreno -0,15</text>`;
  b += `<rect x="${X(D.Li + 0.17)}" y="${Z(0)}" width="${(D.Li + 0.34) * s}" height="${0.5 * s}" fill="#d4d0c8" stroke="#888"/>`;
  // entramado del muro de servicios (PB y PA)
  for (const el of model.elements) {
    if (el.wall !== 'PB-SER' && el.wall !== 'PA-SER') continue;
    if (el.kind !== 'box') continue;
    b += `<rect x="${X(el.max[0])}" y="${Z(el.max[2])}" width="${(el.max[0] - el.min[0]) * s}" height="${(el.max[2] - el.min[2]) * s}" fill="#f1dcb3" stroke="#b8925a" stroke-width=".8"/>`;
  }
  for (const el of model.elements) {
    if (el.layer === 'estructura' && el.name?.startsWith('Refuerzo')) b += `<rect x="${X(el.max[0])}" y="${Z(el.max[2])}" width="${(el.max[0] - el.min[0]) * s}" height="${(el.max[2] - el.min[2]) * s}" fill="#e2b866" stroke="#9a6d2a"/>`;
    if (el.kind === 'box' && el.layer === 'estructura' && el.max[1] > D.Wi + 0.1 && el.min[2] > 2.3 && el.min[2] < 2.7 && el.name?.includes('borde entrepiso')) b += `<rect x="${X(el.max[0])}" y="${Z(el.max[2])}" width="${(el.max[0] - el.min[0]) * s}" height="${(el.max[2] - el.min[2]) * s}" fill="#e7c98f" stroke="#b8925a"/>`;
  }
  // artefactos (fantasma)
  for (const el of model.elements) {
    if (!['cocina', 'bano'].includes(el.layer) || el.kind !== 'box') continue;
    if (el.max[1] < D.Wi - 0.75) continue;
    b += `<rect x="${X(el.max[0])}" y="${Z(el.max[2])}" width="${(el.max[0] - el.min[0]) * s}" height="${(el.max[2] - el.min[2]) * s}" fill="none" stroke="#9aa5b1" stroke-width=".8" stroke-dasharray="3 3"/>`;
  }
  // registros
  const cw = (D.Li - 2 * D.cOut) / 4;
  for (let i = 0; i < 4; i++) {
    const a = D.cOut + i * cw;
    b += `<rect x="${X(a + cw)}" y="${Z(1.5)}" width="${cw * s}" height="${(1.5 - 0.06) * s}" fill="none" stroke="#1f2933" stroke-width="2.2" stroke-dasharray="10 5"/>`;
    b += `<text x="${X(a + cw / 2)}" y="${Z(1.5) - 6}" font-size="13" font-weight="700" text-anchor="middle" ${FONT}>R${i + 1}</text>`;
  }
  // cañerías
  const cols = { agua_fria: '#2f7fd6', agua_caliente: '#d83b2d', desague: '#c26a12', ventilacion: '#8a5a2b', gas: '#c9a400', electrico: '#666', calefaccion: '#888' };
  for (const el of model.elements) {
    if (!cols[el.layer] || el.kind !== 'tube') continue;
    const inWall = el.pts.some(([x, y]) => y > D.Wi - 0.4);
    if (!inWall) continue;
    const pts = el.pts.filter(([, y]) => y > D.Wi - 0.45).map(([x, , z]) => `${r2(X(x))},${r2(Z(z))}`).join(' ');
    const w = el.r > 0.04 ? 7 : el.r > 0.02 ? 4.5 : el.layer === 'electrico' ? 1.6 : 3.2;
    b += `<polyline points="${pts}" fill="none" stroke="${cols[el.layer]}" stroke-width="${w}" stroke-linejoin="round" ${el.layer === 'electrico' ? 'stroke-dasharray="5 3"' : ''}/>`;
  }
  for (const p of model.plumbing.filter((q) => q.pos)) {
    const [x, , z] = p.pos;
    b += `<circle cx="${X(x)}" cy="${Z(z)}" r="6" fill="#c33" stroke="#fff" stroke-width="1.5"/>`;
  }
  for (const bx of model.elec.boxes.filter((q) => q.normal === 'y-' && q.pos[1] > D.Wi - 0.01)) {
    b += `<rect x="${X(bx.pos[0]) - 4}" y="${Z(bx.pos[2]) - 7}" width="8" height="14" fill="#fff" stroke="#333"/><text x="${X(bx.pos[0]) + 6}" y="${Z(bx.pos[2]) + 3}" font-size="9" ${FONT}>${bx.id}</text>`;
  }
  // cotas de altura de conexiones
  const hs = [[0.2, 'inodoro AF 20'], [0.4, 'gas/llave gral 30-40'], [0.55, 'bacha/lavatorio AF-AC 55'], [1.1, 'ducha mezcladora 110'], [1.35, 'termotanque 135'], [2.0, 'flor ducha 200']];
  for (const [z, t] of hs) b += `<line x1="${X(x0)}" y1="${Z(z)}" x2="${X(x0) + 10}" y2="${Z(z)}" stroke="#a33"/><text x="${X(x0) + 14}" y="${Z(z) + 4}" font-size="11" fill="#a33" ${FONT}>${t}</text>`;
  b += `<text x="${X(D.Li / 2)}" y="${Z(z1) + 16}" font-size="11" text-anchor="middle" fill="#555" ${FONT}>← fondo · frente →</text>`;
  const ttl = `<text x="24" y="34" class="ttl" ${FONT}>Pared de servicios — vista desde el exterior sin registros</text><text x="24" y="54" class="sub" ${FONT}>Montantes 2x6 @40 · registros R1–R4 (cassettes atornillados) · todas las conexiones y llaves de paso quedan detrás de un registro</text>`;
  const lg = `<g transform="translate(24,${H - 30})" ${FONT} font-size="11">${[['#2f7fd6', 'agua fría'], ['#d83b2d', 'agua caliente'], ['#c9a400', 'gas'], ['#c26a12', 'desagües'], ['#8a5a2b', 'ventilación'], ['#666', 'eléctrico'], ['#e2b866', 'refuerzos para colgar artefactos']].map(([c, t], i) => `<rect x="${i * 150}" y="-6" width="22" height="6" fill="${c}"/><text x="${i * 150 + 28}" y="0">${t}</text>`).join('')}</g>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">${STYLE}<rect width="100%" height="100%" fill="#fff"/>${ttl}${b}${lg}</svg>`;
}

// ------------------------------------------------------------------ estructura
export function planEstructura(model, which) {
  const D = model.D;
  const tf = planTf(D);
  let b = '';
  const H = D.ST.hole;
  if (which === 'fund') {
    const e = 0.17;
    b += rectXY(tf, -e - 0.05, -e - 0.05, D.Li + e + 0.05, D.Wi + e + 0.05, '', 'fill="#f6f2d0" stroke="#999"');
    b += rectXY(tf, -e, -e, D.Li + e, D.Wi + e, '', 'fill="#d7d3cb" stroke="#333" stroke-width="1.5"');
    b += rectXY(tf, -e + 0.25, -e + 0.25, D.Li + e - 0.25, D.Wi + e - 0.25, '', 'fill="#e8e5df" stroke="#333" stroke-dasharray="8 4"');
    b += text(tf, 1.0, D.Wi / 2 - 0.3, 'Platea H°A° e=12 cm · malla Q188', 'lbl');
    b += text(tf, 1.0, D.Wi / 2 - 0.3, 'sobre EPS 50 + film · viga de borde 25x50', 'lbls', 'middle', 'dy="16"');
    b += text(tf, 1.0, D.Wi / 2 - 0.3, '(4Ø10, est. Ø6 c/20) · EPS perimetral 50', 'lbls', 'middle', 'dy="30"');
    // pases (camisas) en platea
    const pases = [
      [3.22, D.Wi - 0.3, 'P1 Ø110 inodoro'], [2.95, 2.45, 'P2 PPA Ø63'], [3.96, 2.76, 'P3 ducha Ø50'], [2.7, D.Wi + 0.04, 'P4 lavatorio Ø40 (en muro)'],
      [0.55, D.Wi + 0.04, 'P5 bacha Ø50 (en muro)'], [2.25, D.Wi + 0.04, 'P6 agua Ø20'], [2.15, D.Wi + 0.12, 'P7 gas'], [2.38, 2.4, 'P8 acometida eléctrica 1¼"'], [3.36, D.Wi + 0.06, 'P9 ventilación Ø63'], [-0.07, 0.72, 'P10 caño eléctrico (frente)'],
    ];
    pases.forEach(([x, y, t], i) => {
      b += `<circle cx="${r2(tf.X(x, y))}" cy="${r2(tf.Y(x, y))}" r="8" fill="#c26a12"/><text x="${r2(tf.X(x, y))}" y="${r2(tf.Y(x, y)) + 3.5}" font-size="9" fill="#fff" text-anchor="middle" ${FONT}>${i + 1}</text>`;
      b += `<text x="${tf.W - 250}" y="${300 + i * 18}" font-size="11.5" ${FONT}>${esc(t)}</text>`;
    });
    b += `<text x="${tf.W - 250}" y="280" font-size="12" font-weight="700" ${FONT}>Pases a dejar en platea</text>`;
    // anclajes
    for (let x = 0.3; x < D.Li; x += 0.6) for (const y of [-0.085, D.Wi + 0.085]) b += `<rect x="${r2(tf.X(x, y)) - 2}" y="${r2(tf.Y(x, y)) - 2}" width="4" height="4" fill="#333"/>`;
    for (let y = 0.3; y < D.Wi; y += 0.6) for (const x of [-0.085, D.Li + 0.085]) b += `<rect x="${r2(tf.X(x, y)) - 2}" y="${r2(tf.Y(x, y)) - 2}" width="4" height="4" fill="#333"/>`;
    b += dim(tf, [-e, D.Wi + e], [-e, -e], 70, cm(D.Wi + 2 * e));
    b += dim(tf, [-e, -e], [D.Li + e, -e], 70, cm(D.Li + 2 * e));
    tf.W += 0; return sheetWrap({ ...tf, W: tf.W + 260 }, 'Fundación — platea y pases', 'Dejar todas las camisas/pases antes de hormigonar · ■ anclaje de solera c/60 cm', b);
  }
  if (which === 'entrepiso') {
    b += wallsPlan(tf, D, 'PB', { noOpen: true }).replace(/<polygon[^>]*class="wallc"[^>]*\/>/g, '');
    for (const el of model.elements) {
      if (el.layer !== 'estructura' || el.kind !== 'box') continue;
      if (!(el.min[2] >= D.ZJ0 - 0.01 && el.max[2] <= D.ZJ1 + 0.01)) continue;
      b += rectXY(tf, el.min[0], el.min[1], el.max[0], el.max[1], '', `fill="${/Brochal|doble/.test(el.name) ? '#c98f3d' : '#e7c98f'}" stroke="#8a6327" stroke-width=".8"`);
    }
    b += rectXY(tf, H.x0, H.y0, H.x1, H.y1, '', 'fill="none" stroke="#a33" stroke-width="1.5" stroke-dasharray="6 4"');
    b += text(tf, 1.45, 0.42, 'HUECO ESCALERA 290x85', 'lbl');
    b += dimChain(tf, [[0, D.Wi + 0.5], [0.4, D.Wi + 0.5], [0.8, D.Wi + 0.5]], -10);
    b += `<text x="24" y="${tf.H - 40}" class="lbl" ${FONT}>Vigas 2x8 (45x195) @40 cm · luz 3,36 m · OSB 18 mm machihembrado encolado y clavado</text><text x="24" y="${tf.H - 24}" class="lbls" ${FONT}>Brochal y vigas de borde de hueco dobles · bloqueo a media luz · cotas en cm</text>`;
    return sheetWrap(tf, 'Estructura de entrepiso', 'Planta de vigas (por encima de muros PB) — verificación final por calculista', b);
  }
  // techo
  b += poly(tf, [[D.cOut - D.GABLE_OH, D.sOut - D.EAVE], [D.Li - D.cOut + D.GABLE_OH, D.sOut - D.EAVE], [D.Li - D.cOut + D.GABLE_OH, D.Wi - D.sOut + D.EAVE], [D.cOut - D.GABLE_OH, D.Wi - D.sOut + D.EAVE]], 'thin', 'stroke-dasharray="8 4"');
  for (const el of model.elements) {
    if (el.layer !== 'estructura') continue;
    if (el.kind === 'prism' && el.name?.startsWith('Cabio')) {
      const xs = el.o[0];
      const ys = el.poly[0][0].map((p) => p[0]);
      b += rectXY(tf, xs, Math.min(...ys), xs + 0.045, Math.max(...ys), '', 'fill="#e7c98f" stroke="#8a6327" stroke-width=".8"');
    }
    if (el.id === 'CUMBRERA') b += rectXY(tf, el.min[0], el.min[1], el.max[0], el.max[1], '', 'fill="#c98f3d" stroke="#6b4a1b"');
  }
  b += text(tf, D.Li / 2, D.Wi / 2, 'Viga cumbrera laminada 90x300', 'lbl', 'middle', 'dy="-12"');
  b += text(tf, D.Li / 2, 0.6, 'Cabios 2x8 @60 · pendiente 30° · alero 45 cm', 'lbls');
  b += text(tf, D.Li / 2, 0.6, 'membrana + contraclavadera 1x2 + clavadera 2x2 @80 + chapa T-101', 'lbls', 'middle', 'dy="14"');
  return sheetWrap(tf, 'Estructura de techo', 'Planta de cabios — cielorraso inclinado bajo cabios (sin entretecho: lana 150 mm entre cabios + cámara ventilada)', b);
}

// ------------------------------------------------------------------ entramado de cada muro (elevación)
export function wallFraming(model, wallId) {
  const w = WALLS.find((q) => q.id === wallId);
  const els = model.elements.filter((e) => e.wall === wallId);
  const sK = 120;
  let smin = Infinity, smax = -Infinity, zmin = Infinity, zmax = -Infinity;
  const shapes = [];
  for (const el of els) {
    let pts;
    if (el.kind === 'box') {
      const a = w.axis === 'x' ? [el.min[0], el.max[0]] : [el.min[1], el.max[1]];
      pts = [[a[0], el.min[2]], [a[1], el.min[2]], [a[1], el.max[2]], [a[0], el.max[2]]];
    } else if (el.kind === 'prism') pts = el.poly[0][0];
    else continue;
    for (const [s, z] of pts) { smin = Math.min(smin, s); smax = Math.max(smax, s); zmin = Math.min(zmin, z); zmax = Math.max(zmax, z); }
    shapes.push({ pts, el });
  }
  const W = (smax - smin) * sK + 120, H = (zmax - zmin) * sK + 130;
  const X = (s) => 60 + (s - smin) * sK;
  const Z = (z) => 90 + (zmax - z) * sK;
  let b = '';
  const col = (n) => (/dintel/.test(n) ? '#c98f3d' : /solera/.test(n) ? '#d9a95a' : /jack|king/.test(n) ? '#e0b36b' : /antepecho|bloqueo/.test(n) ? '#e9c88e' : '#f1dcb3');
  for (const { pts, el } of shapes) b += `<polygon points="${pts.map(([s, z]) => `${r2(X(s))},${r2(Z(z))}`).join(' ')}" fill="${col(el.name ?? '')}" stroke="#7d5a26" stroke-width=".7"><title>${esc(el.info ?? el.name)}</title></polygon>`;
  for (const k of w.open) {
    const o = model.D.OPEN[k];
    b += `<rect x="${X(o.s0)}" y="${Z(o.z1)}" width="${(o.s1 - o.s0) * sK}" height="${(o.z1 - o.z0) * sK}" fill="#eef6fb" stroke="#3b82c4" stroke-dasharray="4 3"/><text x="${X((o.s0 + o.s1) / 2)}" y="${Z((o.z0 + o.z1) / 2)}" font-size="12" text-anchor="middle" fill="#3b82c4" ${FONT}>${k} ${cm(o.s1 - o.s0)}x${cm(o.z1 - o.z0)}</text>`;
  }
  const nm = els.filter((e) => e.member).length;
  const lm = els.filter((e) => e.member).reduce((a, e) => a + e.member.len, 0);
  const ttl = `<text x="24" y="30" class="ttl" ${FONT}>${esc(w.name)} — entramado</text><text x="24" y="50" class="sub" ${FONT}>${nm} piezas · ${fmt(lm)} ml · ${w.sec ?? '2x6'} @40</text><text x="24" y="66" class="sub" ${FONT}>${w.axis === 'x' ? 'izquierda = frente' : 'izquierda = lateral ciego'}</text>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">${STYLE}<rect width="100%" height="100%" fill="#fff"/>${ttl}${b}</svg>`;
}

// ------------------------------------------------------------------ despiece de placas
export function faceMap(model, face) {
  const pcs = Object.values(model.panels).flat().filter((p) => p.face === face);
  if (!pcs.length) return '';
  let u0 = Infinity, v0 = Infinity, u1 = -Infinity, v1 = -Infinity;
  for (const p of pcs) { u0 = Math.min(u0, p.bbox[0]); v0 = Math.min(v0, p.bbox[1]); u1 = Math.max(u1, p.bbox[2]); v1 = Math.max(v1, p.bbox[3]); }
  const k = Math.min(110, 560 / Math.max(u1 - u0, 0.5));
  const W = (u1 - u0) * k + 40, H = (v1 - v0) * k + 46;
  const X = (u) => 20 + (u - u0) * k, Y = (v) => 30 + (v1 - v) * k;
  const pal = ['#e9c46a', '#8ecae6', '#b5e48c', '#f4a261', '#cdb4db', '#ffafcc', '#90dbf4', '#ffd6a5', '#caffbf', '#bde0fe'];
  let b = '';
  pcs.forEach((p, i) => {
    const d = p.poly.map((ring) => 'M' + ring.map(([u, v]) => `${r2(X(u))},${r2(Y(v))}`).join(' L') + ' Z').join(' ');
    b += `<path d="${d}" fill="${pal[i % pal.length]}" fill-rule="evenodd" stroke="#333" stroke-width="1"/>`;
    const cx = X((p.bbox[0] + p.bbox[2]) / 2), cy = Y((p.bbox[1] + p.bbox[3]) / 2);
    b += `<text x="${r2(cx)}" y="${r2(cy)}" font-size="11" font-weight="700" text-anchor="middle" ${FONT}>${p.id.split('-').pop()}</text><text x="${r2(cx)}" y="${r2(cy + 13)}" font-size="9.5" text-anchor="middle" ${FONT}>${cm(p.w)}x${cm(p.h)}</text>`;
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><text x="20" y="18" font-size="12" font-weight="700" ${FONT}>${esc(face)} · ${pcs.length} piezas · origen ${fmt(u0)} / ${fmt(v0)}</text>${b}</svg>`;
}

export function sheetSvg(sheet, S2, mat) {
  const k = 110;
  const W = S2.w * k + 20, H = S2.h * k + 34;
  let b = `<rect x="10" y="24" width="${S2.w * k}" height="${S2.h * k}" fill="#f4f1ea" stroke="#333" stroke-width="1.4"/>`;
  b += `<text x="10" y="16" font-size="12" font-weight="700" ${FONT}>Placa ${sheet.n} · uso ${sheet.use}%</text>`;
  for (const it of sheet.items) {
    const p = it.piece;
    // transformar polígono de la pieza al marco de la placa
    const [bu0, bv0] = p.bbox;
    const toSheet = ([u, v]) => {
      let sx, sy;
      if (p.along === 'v') { sx = u - bu0; sy = v - bv0; } else { sx = v - bv0; sy = u - bu0; }
      if (it.rot) [sx, sy] = [sy, sx];
      return [10 + (it.x + sx) * k, 24 + (S2.h - it.y - sy) * k];
    };
    const d = p.poly.map((ring) => 'M' + ring.map((q) => toSheet(q).map(r2).join(',')).join(' L') + ' Z').join(' ');
    b += `<path d="${d}" fill="${mat.startsWith('osb') ? '#e3c58f' : mat === 'durlock_rh' ? '#cfe3c6' : mat === 'cementicia' ? '#cfcfc8' : '#fff'}" fill-rule="evenodd" stroke="#1f6feb" stroke-width="1.1"/>`;
    const cx = 10 + (it.x + it.w / 2) * k, cy = 24 + (S2.h - it.y - it.h / 2) * k;
    b += `<text x="${r2(cx)}" y="${r2(cy)}" font-size="${it.w * k < 50 || it.h * k < 30 ? 7.5 : 10}" font-weight="700" text-anchor="middle" ${FONT}>${p.id}</text>`;
    if (it.h * k > 40) b += `<text x="${r2(cx)}" y="${r2(cy + 12)}" font-size="9" text-anchor="middle" ${FONT}>${cm(p.pw)}x${cm(p.ph)}${it.rot ? ' ↻' : ''}</text>`;
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">${b}</svg>`;
}

// ------------------------------------------------------------------ unifilar
export function unifilar() {
  const W = 900, H = 360;
  let b = `<text x="24" y="32" class="ttl" ${FONT}>Esquema unifilar — tablero principal TP</text>`;
  b += `<line x1="60" y1="90" x2="60" y2="140" stroke="#222" stroke-width="2"/><text x="72" y="100" font-size="12" ${FONT}>Acometida subterránea 2x6 mm² desde pilar (medidor) · PAT jabalina 1,5 m</text>`;
  b += `<rect x="40" y="140" width="40" height="40" fill="#fff" stroke="#222" stroke-width="2"/><text x="60" y="165" font-size="11" text-anchor="middle" ${FONT}>ID</text><text x="90" y="165" font-size="12" ${FONT}>Disyuntor 2x40A 30 mA</text>`;
  b += `<line x1="60" y1="180" x2="60" y2="210" stroke="#222" stroke-width="2"/><line x1="60" y1="210" x2="${60 + 3 * 200}" y2="210" stroke="#222" stroke-width="2"/>`;
  Object.entries(CIRC).forEach(([k, c], i) => {
    const x = 60 + i * 200;
    b += `<line x1="${x}" y1="210" x2="${x}" y2="240" stroke="#222" stroke-width="2"/><rect x="${x - 18}" y="240" width="36" height="36" fill="#fff" stroke="${c.color}" stroke-width="2.5"/><text x="${x}" y="263" font-size="11" text-anchor="middle" ${FONT}>${c.pia}</text>`;
    b += `<line x1="${x}" y1="276" x2="${x}" y2="300" stroke="#222" stroke-width="2"/><text x="${x}" y="318" font-size="12" font-weight="700" text-anchor="middle" ${FONT}>${k}</text><text x="${x}" y="334" font-size="10" text-anchor="middle" ${FONT}>${esc(c.name.split('— ')[1])}</text><text x="${x}" y="348" font-size="10" text-anchor="middle" fill="#555" ${FONT}>${esc(c.cable)}</text>`;
  });
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">${STYLE}<rect width="100%" height="100%" fill="#fff"/>${b}</svg>`;
}

export { SPECS };
