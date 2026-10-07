// Estudio de disposición de la planta baja: alternativas evaluadas con un análisis de circulación.
// Para cada alternativa se arma un mapa de obstáculos (muros, escalera, mesada, muebles) en una grilla
// de 2,5 cm, se calcula la distancia de cada celda libre al obstáculo más cercano y, para cada recorrido
// de uso diario, el ANCHO LIBRE MÍNIMO del mejor camino (cuello de botella). Criterios usados:
//   >= 0,80 m  paso cómodo (circulación principal)      0,60–0,80  paso de servicio (estrecho)
//   <  0,60 m  no se puede pasar con comodidad / bloqueado
const RES = 0.025;
const Li = 4.36, Wi = 3.36;

const FIXED = [
  // escalera (tramo recto) — bajo los compensados (x<0,85) queda libre con 1,90 de alto
  { r: [0.85, 0, 3.25, 0.85], k: 'Escalera' },
  // mesada y artefactos de cocina
  { r: [0, 2.76, 2.33, Wi], k: 'Mesada / heladera' },
  // tabiques del baño y el baño mismo
  { r: [2.33, 1.965, Li, Wi], k: 'Baño' },
];

export const OPTIONS = [
  {
    id: 'v1',
    name: 'Alternativa A — versión 1 (anterior)',
    resumen: 'Acceso por el frente. Banco-sofá contra la escalera usado también para comer, mesa en el medio y una sola silla.',
    entry: [0.45, 1.4], door: { x: 0, y0: 0.95, y1: 1.85 },
    furniture: [
      { r: [1.05, 0.85, 2.45, 1.4], k: 'Banco-sofá' },
      { r: [1.35, 1.47, 2.15, 2.07], k: 'Mesa 80x60' },
      { r: [0.9, 1.57, 1.32, 1.99], k: 'Silla' },
      { r: [4.12, 1.12, Li, 1.68], k: 'Calefactor' },
      { r: [0.05, 0, 0.8, 0.32], k: 'Zapatero' },
    ],
    seatsDining: 1, seatsLiving: 2, eatOnSofa: true, sofaFacesTv: false,
    targets: { stair: [3.8, 0.42], bath: [2.88, 1.45], sink: [0.3, 2.45], stove: [1.48, 2.45], fridge: [2.05, 2.35], seat1: [0.75, 1.78], sofa: [1.75, 1.42] },
  },
  {
    id: 'v2',
    name: 'Alternativa B — sillón contra la escalera + mesa central',
    resumen: 'Acceso por el frente. Sillón de 2 cuerpos contra la escalera mirando a la cocina, mesa de 70x70 con dos sillas en el centro.',
    entry: [0.45, 1.4], door: { x: 0, y0: 0.95, y1: 1.85 },
    furniture: [
      { r: [0.95, 0.85, 2.35, 1.51], k: 'Sillón 140' },
      { r: [0.95, 1.85, 1.65, 2.55], k: 'Mesa 70x70' },
      { r: [0.5, 1.99, 0.92, 2.41], k: 'Silla' },
      { r: [1.68, 1.99, 2.1, 2.41], k: 'Silla' },
      { r: [4.12, 1.12, Li, 1.68], k: 'Calefactor' },
    ],
    seatsDining: 2, seatsLiving: 2, eatOnSofa: false, sofaFacesTv: false,
    targets: { stair: [3.8, 0.42], bath: [2.88, 1.45], sink: [0.3, 2.5], stove: [1.48, 2.6], fridge: [2.05, 2.5], seat1: [0.3, 2.2], seat2: [1.95, 2.2], sofa: [1.65, 1.6] },
  },
  {
    id: 'v3',
    name: 'Alternativa C — ELEGIDA: acceso por el fondo, sillón bajo la escalera, comedor al ventanal',
    resumen: 'Se entra por el hall (junto a la escalera y el baño). El frente queda sin paso cruzado: sillón de 2 cuerpos en el nicho bajo los compensados mirando al TV, mesa de 72x65 con dos sillas contra el ventanal y calefactor bajo la ventana.',
    entry: [3.95, 1.4], door: { x: Li, y0: 0.95, y1: 1.85 },
    furniture: [
      { r: [0.05, 0.04, 1.45, 0.7], k: 'Sillón 140' },
      { r: [1.53, 0.07, 1.98, 0.52], k: 'Mesa aux.' },
      { r: [0.02, 1.45, 0.67, 2.17], k: 'Mesa 72x65' },
      { r: [0.62, 1.375, 1.2, 1.809], k: 'Silla' },
      { r: [0.62, 1.811, 1.2, 2.245], k: 'Silla' },
      { r: [0, 0.88, 0.24, 1.44], k: 'Calefactor' },
    ],
    seatsDining: 2, seatsLiving: 2, eatOnSofa: false, sofaFacesTv: true,
    targets: { stair: [3.8, 0.42], bath: [2.88, 1.45], sink: [0.3, 2.45], stove: [1.48, 2.45], fridge: [2.05, 2.35], seat1: [1.35, 1.59], seat2: [1.35, 2.03], sofa: [1.32, 1.02] },
  },
];

const ROUTES = [
  ['entry', 'stair', 'Entrada → escalera'],
  ['entry', 'bath', 'Entrada → baño'],
  ['entry', 'fridge', 'Entrada → heladera'],
  ['entry', 'stove', 'Entrada → cocina (anafe)'],
  ['stove', 'sink', 'Cocina → bacha'],
  ['stove', 'seat1', 'Cocina → silla 1'],
  ['stove', 'seat2', 'Cocina → silla 2'],
  ['entry', 'sofa', 'Entrada → sillón'],
  ['bath', 'sofa', 'Baño → sillón'],
];

function grid(opt) {
  const nx = Math.round(Li / RES), ny = Math.round(Wi / RES);
  const occ = new Uint8Array(nx * ny);
  const mark = ([x0, y0, x1, y1]) => {
    for (let i = Math.max(0, Math.floor(x0 / RES)); i < Math.min(nx, Math.ceil(x1 / RES)); i++)
      for (let j = Math.max(0, Math.floor(y0 / RES)); j < Math.min(ny, Math.ceil(y1 / RES)); j++) occ[i * ny + j] = 1;
  };
  FIXED.forEach((f) => mark(f.r));
  opt.furniture.forEach((f) => mark(f.r));
  // la puerta de acceso es la única abertura del perímetro; el resto del perímetro es muro
  const bound = [];
  for (let i = -1; i <= nx; i++) for (const j of [-1, ny]) bound.push([i, j]);
  for (let j = 0; j < ny; j++) for (const i of [-1, nx]) bound.push([i, j]);
  const obs = [];
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    if (!occ[i * ny + j]) continue;
    // sólo bordes
    let edge = false;
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const a = i + di, b = j + dj;
      if (a < 0 || b < 0 || a >= nx || b >= ny || !occ[a * ny + b]) edge = true;
    }
    if (edge) obs.push([i, j]);
  }
  obs.push(...bound);
  const dist = new Float32Array(nx * ny);
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    if (occ[i * ny + j]) { dist[i * ny + j] = 0; continue; }
    let m = Infinity;
    for (const [a, b] of obs) {
      const d = (a - i) * (a - i) + (b - j) * (b - j);
      if (d < m) m = d;
    }
    dist[i * ny + j] = Math.sqrt(m) * RES - RES / 2;
  }
  return { nx, ny, occ, dist };
}

function bottleneck(g, p, q) {
  const { nx, ny, dist } = g;
  const cell = ([x, y]) => [Math.min(nx - 1, Math.max(0, Math.floor(x / RES))), Math.min(ny - 1, Math.max(0, Math.floor(y / RES)))];
  const [si, sj] = cell(p), [ti, tj] = cell(q);
  const near = (i, j, ci, cj) => Math.hypot(i - ci, j - cj) * RES < 0.12;
  const ok = (w) => {
    const seen = new Uint8Array(nx * ny);
    const st = [[si, sj]];
    seen[si * ny + sj] = 1;
    while (st.length) {
      const [i, j] = st.pop();
      if (near(i, j, ti, tj)) return true;
      for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const a = i + di, b = j + dj;
        if (a < 0 || b < 0 || a >= nx || b >= ny || seen[a * ny + b]) continue;
        const free = g.occ[a * ny + b] === 0 && (dist[a * ny + b] * 2 >= w || near(a, b, si, sj) || near(a, b, ti, tj));
        if (!free) continue;
        seen[a * ny + b] = 1;
        st.push([a, b]);
      }
    }
    return false;
  };
  let lo = 0, hi = 2;
  if (!ok(0.05)) return 0;
  for (let k = 0; k < 14; k++) { const m = (lo + hi) / 2; if (ok(m)) lo = m; else hi = m; }
  return Math.round(lo * 100) / 100;
}

export function analyze() {
  return OPTIONS.map((opt) => {
    const g = grid(opt);
    const pts = { entry: opt.entry, ...opt.targets };
    const routes = ROUTES.filter(([a, b]) => pts[a] && pts[b]).map(([a, b, name]) => ({ name, w: bottleneck(g, pts[a], pts[b]) }));
    const minMain = Math.min(...routes.filter((r) => /Entrada → (escalera|baño|heladera)/.test(r.name)).map((r) => r.w));
    // ¿el recorrido entrada → escalera/baño atraviesa la zona de estar-comedor (x < 2,33)?
    const crossesLiving = opt.entry[0] < 2.33;
    return { ...opt, routes, minMain, crossesLiving };
  });
}

// --------------------------------------------------------------------- dibujo
const S = 95;
export function studySvg(res) {
  const M = 30;
  const W = Wi * S + 2 * M, H = Li * S + 2 * M + 30;
  const X = (x, y) => M + (Wi - y) * S;
  const Y = (x, y) => M + 30 + (Li - x) * S;
  const R = ([x0, y0, x1, y1], fill, stroke = '#555', extra = '') => `<rect x="${X(x0, y1)}" y="${Y(x1, y0)}" width="${(y1 - y0) * S}" height="${(x1 - x0) * S}" fill="${fill}" stroke="${stroke}" stroke-width="1" ${extra}/>`;
  let b = `<rect x="${X(0, Wi)}" y="${Y(Li, 0)}" width="${Wi * S}" height="${Li * S}" fill="#fff" stroke="#2b2f33" stroke-width="7"/>`;
  b += R([0.85, 0, 3.25, 0.85], '#efe7dc', '#8a7a66');
  for (let k = 1; k < 10; k++) { const x = 3.25 - 0.24 * k; b += `<line x1="${X(x, 0)}" y1="${Y(x, 0)}" x2="${X(x, 0.85)}" y2="${Y(x, 0.85)}" stroke="#b9ab98" stroke-width=".8"/>`; }
  b += R([0, 0, 0.85, 0.85], 'none', '#b9ab98', 'stroke-dasharray="4 3"');
  b += R([0, 2.76, 2.33, Wi], '#dfe3e6', '#555');
  b += R([2.33, 1.965, Li, Wi], '#eef1f3', '#2b2f33');
  b += `<text x="${X(3.3, 2.7)}" y="${Y(3.3, 2.7)}" font-size="11" text-anchor="middle" fill="#555">baño</text>`;
  b += `<text x="${X(1.15, 3.06)}" y="${Y(1.15, 3.06) + 4}" font-size="10" text-anchor="middle" fill="#555">mesada · cocina · heladera</text>`;
  b += `<text x="${X(2.05, 0.42)}" y="${Y(2.05, 0.42) + 4}" font-size="10" text-anchor="middle" fill="#8a7a66">escalera (sube →frente)</text>`;
  // puerta
  const d = res.door;
  b += `<line x1="${X(d.x, d.y0)}" y1="${Y(d.x, d.y0)}" x2="${X(d.x, d.y1)}" y2="${Y(d.x, d.y1)}" stroke="#c6902f" stroke-width="9"/>`;
  b += `<text x="${X(d.x, (d.y0 + d.y1) / 2)}" y="${Y(d.x, 0) + (d.x === 0 ? 24 : -14)}" font-size="11" font-weight="700" text-anchor="middle" fill="#9a5b00">ENTRADA</text>`;
  for (const f of res.furniture) {
    b += R(f.r, f.k === 'Calefactor' ? '#f6d8cc' : '#f3ecdf', '#7a6f60');
    const [x0, y0, x1, y1] = f.r;
    b += `<text x="${X((x0 + x1) / 2, (y0 + y1) / 2)}" y="${Y((x0 + x1) / 2, (y0 + y1) / 2) + 3}" font-size="9" text-anchor="middle" fill="#333">${f.k}</text>`;
  }
  // recorridos (líneas rectas entre puntos, coloreadas por el ancho libre del mejor camino)
  const pts = { entry: res.entry, ...res.targets };
  const col = (w) => (w >= 0.8 ? '#2a7a4b' : w >= 0.6 ? '#d08a00' : '#c0392b');
  ROUTES.forEach(([a, c2, name]) => {
    if (!pts[a] || !pts[c2]) return;
    const r = res.routes.find((q) => q.name === name);
    b += `<line x1="${X(...pts[a])}" y1="${Y(...pts[a])}" x2="${X(...pts[c2])}" y2="${Y(...pts[c2])}" stroke="${col(r.w)}" stroke-width="2" stroke-dasharray="6 4" opacity=".8"/>`;
  });
  for (const [k, p] of Object.entries(pts)) b += `<circle cx="${X(...p)}" cy="${Y(...p)}" r="4" fill="#1f2933"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" font-family="Inter, Arial, sans-serif"><rect width="100%" height="100%" fill="#fff"/><text x="${M}" y="20" font-size="13" font-weight="700">${res.name.split(' — ')[0]}</text>${b}</svg>`;
}
