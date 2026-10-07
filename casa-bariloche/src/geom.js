// Primitivas geométricas del modelo (independientes de three.js).
// Sistema de coordenadas del proyecto (metros):
//   x = largo (0 = cara interior del frente, crece hacia el fondo)
//   y = ancho (0 = cara interior del lateral ciego, crece hacia la pared de servicios)
//   z = altura (0 = nivel superior de platea)
import pc from 'polygon-clipping';

export const r3 = (n) => Math.round(n * 1000) / 1000;
export const r2 = (n) => Math.round(n * 100) / 100;

export function box(min, max, extra = {}) {
  return { kind: 'box', min: [...min], max: [...max], ...extra };
}

// Polígono plano (en coordenadas u,v de un plano) extruido t metros en la dirección n.
// poly: multipolígono estilo polygon-clipping: [ [ [ [u,v],... ] (anillo exterior), [hueco]... ], ... ]
export function prism(o, u, v, n, t, poly, extra = {}) {
  return { kind: 'prism', o: [...o], u: [...u], v: [...v], n: [...n], t, poly, ...extra };
}

export function tube(pts, r, extra = {}) {
  return { kind: 'tube', pts: pts.map((p) => [...p]), r, ...extra };
}

export function cyl(c, axis, r, h, extra = {}) {
  return { kind: 'cyl', c: [...c], axis, r, h, ...extra };
}

// Chapa acanalada/trapezoidal: plano con nervios.
// o: esquina, u: dirección transversal a los nervios, v: dirección de los nervios, n: normal exterior.
// width: ancho en u, len(uLocal) -> largo en v (permite cortes inclinados), period y depth del nervio.
export function ribbed(o, u, v, n, width, lenFn, extra = {}) {
  return { kind: 'ribbed', o: [...o], u: [...u], v: [...v], n: [...n], width, lens: sampleLens(width, lenFn), ...extra };
}

function sampleLens(width, lenFn) {
  // muestreo cada 1 cm para poder evaluar el largo en cualquier punto del perfil
  const out = [];
  const N = Math.max(2, Math.ceil(width / 0.01));
  for (let i = 0; i <= N; i++) {
    const s = (i / N) * width;
    out.push([r3(s), r3(typeof lenFn === 'function' ? lenFn(s) : lenFn)]);
  }
  return out;
}

export function rectRing(u0, v0, u1, v1) {
  return [[u0, v0], [u1, v0], [u1, v1], [u0, v1], [u0, v0]];
}

export function polyArea(ring) {
  let a = 0;
  for (let i = 0; i < ring.length - 1; i++) a += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1];
  return Math.abs(a) / 2;
}

export function multiArea(mp) {
  let a = 0;
  for (const poly of mp) {
    a += polyArea(poly[0]);
    for (let k = 1; k < poly.length; k++) a -= polyArea(poly[k]);
  }
  return a;
}

export function bboxOf(poly) {
  let u0 = Infinity, v0 = Infinity, u1 = -Infinity, v1 = -Infinity;
  for (const [u, v] of poly[0]) {
    u0 = Math.min(u0, u); v0 = Math.min(v0, v); u1 = Math.max(u1, u); v1 = Math.max(v1, v);
  }
  return [u0, v0, u1, v1];
}

// -------------------------------------------------------------------------------------------
// Despiece de placas sobre una cara.
// Devuelve las piezas (con su polígono real, incluyendo calados de aberturas) y los
// elementos 3D. La grilla de placas arranca en (startU,startV) — normalmente la esquina del local.
// sheet: { w, h } (ancho y alto nominal de la placa), along: 'v' = lado largo vertical (según v),
// 'u' = lado largo según u. stagger: desplaza filas alternas medio módulo (pisos).
// -------------------------------------------------------------------------------------------
export function layoutPanels(opt) {
  const {
    face, prefix, mat, o, u, v, n, t, poly, holes = [], sheet, along = 'v', stagger = false,
    layer, group, name, finish, room,
  } = opt;
  const tileW = along === 'v' ? sheet.w : sheet.h; // extensión en u
  const tileH = along === 'v' ? sheet.h : sheet.w; // extensión en v
  const [bu0, bv0, bu1, bv1] = bboxOf([poly]);
  const startU = opt.startU ?? bu0;
  const startV = opt.startV ?? bv0;
  const grid = opt.grid ?? 0.4; // las juntas verticales caen sobre la grilla de montantes/vigas
  const minStrip = opt.minStrip ?? 0.3;
  const holePolys = holes.map((h) => (h.length === 4 && typeof h[0] === 'number' ? [rectRing(...h)] : [h]));
  const pieces = [];
  const elements = [];
  let k = 0;
  let row = 0;
  let prevJoints = [];
  for (let vv = startV; vv < bv1 - 1e-4; vv += tileH, row++) {
    // extensión real de la fila (para medir las piezas de borde)
    const band = pc.intersection([poly], [rectRing(bu0 - 1, vv, bu1 + 1, vv + tileH)]);
    let ra = Infinity, rb = -Infinity;
    for (const pl of band) for (const [u0] of pl[0]) { ra = Math.min(ra, u0); rb = Math.max(rb, u0); }
    if (!isFinite(ra)) continue;
    // elegir el corrimiento (múltiplo de la grilla) que evita tiras angostas y traba juntas con la fila anterior
    let best = null;
    const nCand = Math.max(1, Math.round(tileW / grid));
    for (let j = 0; j < nCand; j++) {
      const off = -j * grid;
      const joints = [];
      for (let uu = startU + off; uu < rb - 1e-4; uu += tileW) if (uu > ra + 1e-4) joints.push(uu);
      const cuts = [ra, ...joints, rb];
      let minW = Infinity;
      for (let i = 0; i < cuts.length - 1; i++) minW = Math.min(minW, cuts[i + 1] - cuts[i]);
      const clash = stagger ? joints.filter((x) => prevJoints.some((q) => Math.abs(q - x) < 0.35)).length : 0;
      const score = (minW >= minStrip ? 10 : minW) - clash * 3 - j * 0.001;
      if (!best || score > best.score) best = { score, off, joints };
    }
    prevJoints = best.joints;
    const off = best.off;
    let col = 0;
    for (let uu = startU + off; uu < bu1 - 1e-4; uu += tileW, col++) {
      const tile = [rectRing(uu, vv, uu + tileW, vv + tileH)];
      let inter = pc.intersection([poly], tile);
      if (holePolys.length && inter.length) inter = pc.difference(inter, ...holePolys);
      for (const p of inter) {
        const ring = p[0];
        const a = polyArea(ring) - p.slice(1).reduce((s, h) => s + polyArea(h), 0);
        if (a < 0.003) continue;
        k++;
        const bb = bboxOf(p);
        const w = r3(bb[2] - bb[0]);
        const h = r3(bb[3] - bb[1]);
        // dimensiones en el marco de la placa (pw = a lo ancho de la placa, ph = a lo largo)
        const pw = along === 'v' ? w : h;
        const ph = along === 'v' ? h : w;
        const full = Math.abs(pw - sheet.w) < 0.005 && Math.abs(ph - sheet.h) < 0.005 && Math.abs(a - sheet.w * sheet.h) < 0.002;
        const id = `${prefix}-${String(k).padStart(2, '0')}`;
        const piece = {
          id, face, mat, poly: p.map((r) => r.map(([a1, b1]) => [r3(a1), r3(b1)])), bbox: bb.map(r3), w, h, pw: r3(pw), ph: r3(ph),
          along, full, area: r3(a), tile: [col, row], room, finish,
          cut: describeCut(p, bb, along),
        };
        pieces.push(piece);
        elements.push(prism(o, u, v, n, t, [piece.poly], {
          id, name: `${name} — placa ${id}`, layer, group, mat, panel: id, paint: opt.paint,
          info: `${pieceLabel(piece)}${finish ? ' · terminación: ' + finish : ''}`,
        }));
      }
    }
  }
  return { pieces, elements };
}

function describeCut(p, bb, along) {
  const ring = p[0];
  const rect = p.length === 1 && Math.abs(polyArea(ring) - (bb[2] - bb[0]) * (bb[3] - bb[1])) < 1e-4;
  if (rect) return 'rectangular';
  if (p.length > 1) return 'con calado interior';
  // detectar corte inclinado
  for (let i = 0; i < ring.length - 1; i++) {
    const du = ring[i + 1][0] - ring[i][0];
    const dv = ring[i + 1][1] - ring[i][1];
    if (Math.abs(du) > 1e-3 && Math.abs(dv) > 1e-3) return 'con corte inclinado';
  }
  return 'con recorte (L/U)';
}

export function pieceLabel(pc0) {
  const cm = (x) => Math.round(x * 1000) / 10;
  return `${pc0.id}: ${cm(pc0.pw)} x ${cm(pc0.ph)} cm${pc0.full ? ' (placa entera)' : ' — ' + pc0.cut}`;
}

// -------------------------------------------------------------------------------------------
// Empaquetado de piezas en placas (guillotina, mejor ajuste por lado corto) para minimizar
// desperdicio. Devuelve la lista de placas con la posición de cada pieza.
// -------------------------------------------------------------------------------------------
export function packSheets(pieces, sheet, kerf = 0.004) {
  const sheets = [];
  const items = pieces
    .map((p) => ({ p, w: p.pw, h: p.ph }))
    .sort((a, b) => b.w * b.h - a.w * a.h || Math.max(b.w, b.h) - Math.max(a.w, a.h));
  for (const it of items) {
    let best = null;
    const tryPlace = (sh, si) => {
      sh.free.forEach((fr, fi) => {
        for (const rot of [false, true]) {
          const w = rot ? it.h : it.w;
          const h = rot ? it.w : it.h;
          if (w <= fr.w + 1e-6 && h <= fr.h + 1e-6) {
            const score = Math.min(fr.w - w, fr.h - h);
            if (!best || score < best.score) best = { si, fi, rot, w, h, score };
          }
        }
      });
    };
    sheets.forEach(tryPlace);
    if (!best) {
      sheets.push({ n: sheets.length + 1, items: [], free: [{ x: 0, y: 0, w: sheet.w, h: sheet.h }] });
      tryPlace(sheets[sheets.length - 1], sheets.length - 1);
    }
    if (!best) throw new Error(`Pieza ${it.p.id} no entra en placa ${sheet.w}x${sheet.h}`);
    const sh = sheets[best.si];
    const fr = sh.free.splice(best.fi, 1)[0];
    sh.items.push({ piece: it.p, x: fr.x, y: fr.y, w: best.w, h: best.h, rot: best.rot });
    // corte guillotina: dividir el sobrante según el eje más largo
    const rw = fr.w - best.w - kerf;
    const rh = fr.h - best.h - kerf;
    if (rw > rh) {
      if (rw > 0.02) sh.free.push({ x: fr.x + best.w + kerf, y: fr.y, w: rw, h: fr.h });
      if (rh > 0.02) sh.free.push({ x: fr.x, y: fr.y + best.h + kerf, w: best.w, h: rh });
    } else {
      if (rh > 0.02) sh.free.push({ x: fr.x, y: fr.y + best.h + kerf, w: fr.w, h: rh });
      if (rw > 0.02) sh.free.push({ x: fr.x + best.w + kerf, y: fr.y, w: rw, h: best.h });
    }
  }
  for (const sh of sheets) {
    const used = sh.items.reduce((s, i) => s + i.w * i.h, 0);
    sh.use = r2((used / (sheet.w * sheet.h)) * 100);
    delete sh.free;
  }
  return sheets;
}

// -------------------------------------------------------------------------------------------
// Optimización de cortes lineales (madera) en largos comerciales. First-fit decreasing,
// eligiendo para cada barra nueva el largo comercial que mejor aprovecha.
// -------------------------------------------------------------------------------------------
export function packBars(pieces, stock, kerf = 0.005) {
  const items = [...pieces].sort((a, b) => b.len - a.len);
  const bars = [];
  const maxStock = Math.max(...stock);
  for (const it of items) {
    if (it.len > maxStock) {
      // pieza más larga que la barra comercial: se empalma (se informa)
      bars.push({ stock: it.len, cuts: [it], rest: 0, splice: true });
      continue;
    }
    let bi = -1, bestRest = Infinity;
    bars.forEach((b, i) => {
      const rest = b.rest - it.len - (b.cuts.length ? kerf : 0);
      if (!b.splice && rest >= -1e-6 && rest < bestRest) { bestRest = rest; bi = i; }
    });
    if (bi >= 0) {
      bars[bi].cuts.push(it);
      bars[bi].rest -= it.len + kerf;
    } else {
      // elegir largo comercial: el más corto que permita además alojar piezas pendientes similares
      const st = [...stock].sort((a, b) => a - b).find((s) => s >= it.len) ?? maxStock;
      bars.push({ stock: st, cuts: [it], rest: st - it.len });
    }
  }
  // re-optimizar largo de barras con poco uso: bajar al largo comercial mínimo que contenga los cortes
  for (const b of bars) {
    if (b.splice) continue;
    const used = b.cuts.reduce((s, c) => s + c.len, 0) + kerf * (b.cuts.length - 1);
    const st = [...stock].sort((a, c) => a - c).find((s) => s >= used - 1e-6);
    b.stock = st;
    b.rest = r3(st - used);
  }
  return bars;
}
