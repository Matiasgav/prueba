// Cómputo de materiales derivado del modelo.
import { SPECS } from './specs.js';
import { packSheets, packBars, multiArea, r2, r3 } from './geom.js';
import { CIRC } from './model.js';

export const SHEETS = {
  durlock_std: { w: 1.2, h: 2.4 },
  durlock_rh: { w: 1.2, h: 2.4 },
  cementicia: { w: 1.2, h: 2.4 },
  osb_11: { w: 1.22, h: 2.44 },
  osb_18: { w: 1.22, h: 2.44 },
};
const STOCK = [3.05, 3.66, 4.27, 4.88, 5.49];

export function takeoff(model) {
  const { D, elements, members, panels, elec, plumbing } = model;
  const rows = []; // { cap, item, spec, cant, unidad, detalle }
  const R = (cap, spec, cant, unidad, detalle = '', item) => rows.push({ cap, spec, item: item ?? SPECS[spec]?.nombre ?? spec, cant: r2(cant), unidad, detalle, criterio: SPECS[spec]?.criterio ?? '' });

  // ---------------- Fundación ----------------
  const e = 0.17;
  const Ls = D.Li + 2 * e, Ws = D.Wi + 2 * e;
  const vSlab = Ls * Ws * 0.12;
  const per = 2 * (Ls + Ws) - 4 * 0.25;
  const vBeam = per * 0.25 * 0.38;
  R('1. Fundación', 'hormigon', vSlab + vBeam, 'm³', `platea ${r2(Ls)}x${r2(Ws)}x0,12 = ${r2(vSlab)} m³ + viga de borde 25x38 bajo platea (${r2(per)} ml) = ${r2(vBeam)} m³`);
  R('1. Fundación', 'hormigon', Math.ceil((Ls * Ws) / (2.4 * 6) * 1.15), 'paños', 'Malla Q188 (2,40x6,00)', 'Malla electrosoldada Q188');
  R('1. Fundación', 'hormigon', Math.ceil((per * 4 * 1.1) / 12), 'barras', 'Viga de borde: 4 Ø10 + estribos Ø6 c/20', 'Hierro Ø10 (barras de 12 m)');
  R('1. Fundación', 'eps_fund', (Ls - 0.5) * (Ws - 0.5) + per * 0.55, 'm²', 'bajo platea + perimetral vertical');
  R('1. Fundación', 'film', Ls * Ws * 1.15, 'm²');
  R('1. Fundación', 'hormigon', Math.ceil(per / 0.6), 'u', 'Anclajes químicos/varilla roscada Ø10 c/60 cm para soleras', 'Anclajes de solera a platea');
  R('1. Fundación', 'zocalo_chapa', 2 * (D.ext.L + D.ext.W), 'ml');

  // ---------------- Maderas ----------------
  const bySec = {};
  for (const m of members) {
    if (m.sec.startsWith('lam')) continue;
    (bySec[m.sec] ??= { mat: m.mat, pieces: [] }).pieces.push({ len: m.len, use: m.use, id: m.id });
  }
  const wood = {};
  for (const [sec, g] of Object.entries(bySec)) {
    const bars = packBars(g.pieces, STOCK);
    wood[sec] = { mat: g.mat, bars, pieces: g.pieces };
    const byStock = {};
    for (const b of bars) byStock[b.stock] = (byStock[b.stock] ?? 0) + 1;
    const total = g.pieces.reduce((s, p) => s + p.len, 0);
    const bought = bars.reduce((s, b) => s + b.stock, 0);
    R('2. Estructura de madera', g.mat, bars.length, 'piezas', `${Object.entries(byStock).sort((a, b) => a[0] - b[0]).map(([s, n]) => `${n} x ${s} m`).join(' + ')} · ${g.pieces.length} cortes · ${r2(total)} ml netos / ${r2(bought)} ml comprados (desperdicio ${Math.round((1 - total / bought) * 100)}%)`, `Pino ${sec}`);
  }
  R('2. Estructura de madera', 'laminada', 1, 'u', `L = ${r2(D.Li + 2 * 0.1575)} m`);
  R('2. Estructura de madera', 'hierro_negro', 2, 'u', 'Fleje 50x1,25 mm en franja de registros (servicios PB)', 'Fleje de arriostramiento galvanizado');
  R('2. Estructura de madera', 'herrajes', 18 * 2 + 2, 'u', 'Estribos/colgadores para cabios en cumbrera + escuadras', 'Conectores metálicos galvanizados');
  R('2. Estructura de madera', 'herrajes', 12, 'kg', 'Clavos espiralados 3½" y 2½" + tornillos estructurales', 'Clavos y tornillos estructurales');

  // ---------------- Placas ----------------
  const sheets = {};
  for (const [mat, list] of Object.entries(panels)) {
    const S = SHEETS[mat];
    const packed = packSheets(list, S);
    sheets[mat] = packed;
    const area = list.reduce((s, p) => s + p.area, 0);
    const cap = mat.startsWith('osb') ? '3. Placas OSB' : '4. Placas interiores';
    R(cap, mat, packed.length, 'placas', `${list.length} piezas (${list.filter((p) => p.full).length} enteras) · ${r2(area)} m² netos · aprovechamiento ${Math.round((area / (packed.length * S.w * S.h)) * 100)}%`);
  }
  const ydArea = ['durlock_std', 'durlock_rh'].reduce((s, m) => s + (panels[m] ?? []).reduce((a, p) => a + p.area, 0), 0);
  R('4. Placas interiores', 'durlock_std', Math.ceil(ydArea * 2.4 / 2.6), 'perfiles', 'Listones/omegas 35 mm para cielorrasos y nivelación (estimado)', 'Perfiles omega galvanizados 2,60 m');
  R('4. Placas interiores', 'durlock_std', Math.ceil(ydArea * 25 / 1000), 'cajas x1000', '25 tornillos T2 por m²', 'Tornillos para placa de yeso (madera) 6x1¼"');
  R('4. Placas interiores', 'durlock_std', Math.ceil(ydArea * 0.9 / 32), 'baldes 32 kg', '0,9 kg/m²', 'Masilla de juntas lista para usar');
  R('4. Placas interiores', 'durlock_std', Math.ceil(ydArea * 1.6 / 150), 'rollos 150 m', '1,6 ml/m²', 'Cinta de papel para juntas');
  R('4. Placas interiores', 'durlock_std', 30, 'ml', 'aristas de aberturas y escalera', 'Cantonera metálica');

  // ---------------- Aislaciones ----------------
  const wallA = osbArea(panels, ['osb_11']);
  const roofA = roofArea(D);
  R('5. Aislaciones y barreras', 'lana_150', wallA + roofA, 'm²', `muros ${r2(wallA)} m² + techo ${r2(roofA)} m²`);
  R('5. Aislaciones y barreras', 'barrera_vapor', (wallA + roofA) * 1.12, 'm²', 'con solapes 10 cm + cinta');
  R('5. Aislaciones y barreras', 'membrana', wallA * 1.15, 'm²', 'sobre el OSB de muros, solapes 15 cm, encintada');
  R('5. Aislaciones y barreras', 'membrana_techo', roofA * 1.2 * 1.15, 'm²', 'sobre cabios, bajo contraclavaderas (incluye aleros)');

  // ---------------- Envolvente exterior ----------------
  const chapaMuro = elements.filter((x) => x.kind === 'ribbed' && x.mat === 'chapa_muro');
  const sheetsWall = {};
  for (const c of chapaMuro) {
    const key = `${c.facade}-${c.sheetNo ?? c.name}`;
    sheetsWall[key] = Math.max(sheetsWall[key] ?? 0, Math.ceil(c.sheetLen * 20) / 20);
  }
  const lensW = Object.values(sheetsWall);
  R('6. Revestimiento exterior y cubierta', 'chapa_muro', lensW.reduce((s, x) => s + x, 0), 'ml', `${lensW.length} hojas T-101 (ancho útil 1,00): ${countLens(lensW)}`);
  const chapaTecho = elements.filter((x) => x.kind === 'ribbed' && x.mat === 'chapa_techo');
  const lensT = chapaTecho.map((c) => c.sheetLen);
  R('6. Revestimiento exterior y cubierta', 'chapa_techo', lensT.reduce((s, x) => s + x, 0), 'ml', `${lensT.length} hojas T-101: ${countLens(lensT)}`);
  R('6. Revestimiento exterior y cubierta', 'chapa_techo', Math.ceil((lensW.length + lensT.length) * 14 * 1.1), 'u', 'Autoperforantes 14x1" con arandela EPDM', 'Tornillos autoperforantes p/chapa');
  const sid = elements.filter((x) => x.siding).reduce((s, x) => s + x.siding.len, 0);
  R('6. Revestimiento exterior y cubierta', 'siding', sid * 0.2, 'm²', `${r2(sid)} ml de tabla → ${Math.ceil((sid * 1.1) / 3.6)} tablas de 3,60 m`);
  R('6. Revestimiento exterior y cubierta', 'fibro_reg', 4, 'u', 'R1..R4 de 1,20 x 1,45 (OSB + fibrocemento + burlete), 10 tornillos inox c/u');
  R('6. Revestimiento exterior y cubierta', 'pino_1x2', Math.ceil((2 * D.ext.L + 2 * D.ext.W) * 8 / 3.05), 'piezas 3,05', 'Clavaderas horizontales de fachada @60 cm', 'Clavaderas 1x2 fachada');
  const xr = D.ext.L + 2 * D.GABLE_OH;
  const rake = 4 * ((D.yRidge + 0.6) / Math.cos((D.PITCH * Math.PI) / 180));
  R('6. Revestimiento exterior y cubierta', 'zinguerias', xr + rake + 2 * xr + 4 * 4.5 + 4.8 + 6, 'ml', `cumbrera ${r2(xr)} + frentines hastial ${r2(rake)} + frentines alero ${r2(2 * xr)} + esquineros 4x4,5 + babeta registros + cupertinas/babetas aberturas`);
  R('6. Revestimiento exterior y cubierta', 'canaleta', 2 * xr + 2 * 5, 'ml', '2 canaletas + 2 bajadas');
  R('6. Revestimiento exterior y cubierta', 'alero_fibro', 2 * D.ext.L * D.EAVE, 'm²');
  R('6. Revestimiento exterior y cubierta', 'visera', 1, 'u');
  R('6. Revestimiento exterior y cubierta', 'deck', 1.2 * 2.4, 'm²', 'deck de acceso 120x240 (12 tablas 1x4 x 2,44 + 3 tirantes 2x4 x 1,22)');

  // ---------------- Aberturas ----------------
  for (const [k, o] of Object.entries(D.OPEN)) {
    const w = Math.round((o.s1 - o.s0) * 100), h = Math.round((o.z1 - o.z0) * 100);
    R('7. Aberturas', o.mat, 1, 'u', `${k} — ${o.name} — vano ${w}x${h} cm${o.sashes === 2 ? ' (1 paño fijo + 1 oscilobatiente)' : o.door ? '' : ' (oscilobatiente)'}`, `${k}: ${SPECS[o.mat].nombre}`);
  }
  R('7. Aberturas', 'cortina', 4, 'u', 'V1, V2, V4, V5');

  // ---------------- Escalera ----------------
  const ST = D.ST;
  R('8. Escalera', 'lenga', 13 * 0.27 * 0.81 * 1.15, 'm²', `13 huellas (10 rectas 27x81 + 3 compensadas) · alzada ${Math.round(ST.rise * 1000) / 10} cm · huella ${ST.going * 100} cm · 2a+h = ${r2(2 * ST.rise + ST.going)} m`);
  R('8. Escalera', 'zanca', 2 * 3.4, 'ml');
  R('8. Escalera', 'pasamanos', 3.3 + 2.1 + 0.9, 'ml');
  R('8. Escalera', 'hierro_negro', 3.3 + 2.1 + 0.9, 'ml', 'baranda escalera + baranda de hueco PA, barrotes c/11 cm');
  R('8. Escalera', 'lenga', 1, 'u', 'Poste de giro 90x90 L=3,60 + poste de arranque 70x70', 'Postes de lenga');

  // ---------------- Pisos y revestimientos ----------------
  const tiles = elements.filter((x) => x.mat === 'porcelanato' && x.tile);
  const nt = tiles.length;
  R('9. Pisos y revestimientos', 'porcelanato', (D.Li * D.Wi) * 1.08, 'm²', `${nt} piezas en planta (${tiles.filter((t) => t.tile === 'entera').length} enteras + ${tiles.filter((t) => t.tile === 'cortada').length} cortadas) + 8% reposición`);
  const pa = (D.Li * D.Wi - (ST.hole.x1 - ST.hole.x0) * (ST.hole.y1 - ST.hole.y0));
  R('9. Pisos y revestimientos', 'spc', pa * 1.07, 'm²', `${r2(pa)} m² netos + 7%`);
  const cd = elements.filter((x) => x.mat === 'ceramica_ducha').length;
  R('9. Pisos y revestimientos', 'ceramica_ducha', ((0.8 * 2 + 1.3) * 2.1) * 1.1, 'm²', `${cd} piezas 30x60 en planta`);
  R('9. Pisos y revestimientos', 'ceramica_cocina', 1.71 * 0.58 * 1.1, 'm²');
  R('9. Pisos y revestimientos', 'zocalo', 2 * (D.Li + D.Wi) * 2 + 6, 'ml');
  R('9. Pisos y revestimientos', 'porcelanato', Math.ceil(((D.Li * D.Wi) * 1.08) / 4), 'bolsas 30 kg', 'Adhesivo para porcelanato', 'Adhesivo porcelanato');

  // ---------------- Pintura ----------------
  const fin = {};
  for (const list of Object.values(panels)) for (const p of list) if (p.finish) fin[p.finish] = (fin[p.finish] ?? 0) + p.area;
  for (const [f, a] of Object.entries(fin)) {
    if (/Cerámica/i.test(f)) continue;
    const spec = /salvia/i.test(f) ? 'pintura_salvia' : /antihongo/i.test(f) ? 'pintura_antihongo' : 'pintura_blanco';
    R('10. Pintura', spec, a, 'm²', `${f} — 2 manos (${Math.ceil((a * 2) / 10)} l aprox.)`);
  }
  R('10. Pintura', 'pintura_blanco', 1, 'jgo', 'Sellador/fijador al agua + enduido de terminación', 'Fijador y enduido');

  // ---------------- Cocina, baño, artefactos ----------------
  for (const s of ['bacha', 'cocina', 'heladera', 'lavarropas', 'purificador', 'griferia_cocina', 'inodoro', 'lavatorio', 'plato_ducha', 'griferia_bano', 'cortina_bano', 'espejo', 'accesorios', 'termotanque', 'calefactor', 'tablero']) {
    R('11. Equipamiento', s, 1, SPECS[s].unidad);
  }
  R('11. Equipamiento', 'melamina_blanca', 1, 'jgo', 'Bajomesada 60 + alacena 80 + módulo 56 s/heladera (muebles estándar de línea)');
  R('11. Equipamiento', 'granito', 1.2, 'ml', 'con calado de bacha y zócalo');

  // ---------------- Instalaciones ----------------
  const pipeSum = {};
  for (const p of plumbing) {
    const k = p.mat;
    pipeSum[k] ??= { len: 0, elbows: 0, count: 0, items: [] };
    pipeSum[k].len += p.len;
    pipeSum[k].elbows += p.elbows ?? 0;
    pipeSum[k].count += p.count ?? 0;
    pipeSum[k].items.push(p);
  }
  const capIns = { ppr_20: '12. Agua', ppr_20c: '12. Agua', pvc_110: '13. Desagües', pvc_63: '13. Desagües', pvc_50: '13. Desagües', gas_pipe: '14. Gas', llave_paso: '12-14. Llaves' };
  for (const [k, v] of Object.entries(pipeSum)) {
    if (k === 'llave_paso') {
      R(capIns[k], k, v.count, 'u', v.items.map((i) => i.name).join(' · '));
    } else {
      R(capIns[k] ?? 'Instalaciones', k, v.len * 1.1, 'ml', `${r2(v.len)} ml en modelo + 10% · ${v.elbows} codos/curvas`);
    }
  }
  R('13. Desagües', 'camara', 1, 'u', 'CI 60x60 + boca de acceso 30x30 cocina + pileta de patio Ø63 baño');
  R('14. Gas', 'rejilla', 2, 'u', 'alta y baja (cocina)');
  // electricidad (cantidades exactas desde la planilla de tramos)
  const nb = (t) => elec.boxes.filter((b) => b.tipo === t);
  R('15. Electricidad', 'caja_rect', nb('rect').length, 'u', nb('rect').map((b) => b.id).join(', '));
  R('15. Electricidad', 'caja_oct', nb('oct').length, 'u', nb('oct').map((b) => b.id).join(', '));
  R('15. Electricidad', 'caja_cuad', nb('cuad').length, 'u', 'CP (acometida)');
  const byRs = {};
  let curvas = 0;
  for (const c of elec.conduits) {
    if (c.circuito === 'AC' && c.from === 'Pilar') continue;
    byRs[c.rs] = (byRs[c.rs] ?? 0) + c.len;
    curvas += c.curves;
  }
  for (const [rs, l] of Object.entries(byRs)) R('15. Electricidad', 'conduit', Math.ceil((l * 1.1) / 3) , 'tiras de 3 m', `${rs}: ${r2(l)} ml en modelo + 10%`, `Caño de acero semipesado ${rs} roscado`);
  R('15. Electricidad', 'conduit', curvas + 10, 'u', 'curvas a 90° de acero roscadas (según planilla) + 10 de reserva', 'Curvas de acero semipesado');
  R('15. Electricidad', 'conduit', elec.conduits.length * 2 + 20, 'u', 'cuplas, tuercas y boquillas', 'Cuplas, tuercas y boquillas de acero');
  const cab = {};
  for (const c of elec.conduits) {
    if (c.circuito === 'TD') continue;
    for (const k of c.cables) {
      const key = `${k.sec} mm² ${k.color}`;
      cab[key] = (cab[key] ?? 0) + c.len + 0.3;
    }
  }
  for (const [s2, l] of Object.entries(cab).sort()) R('15. Electricidad', 'cable', Math.ceil(l * 1.1), 'ml', 'suma de tramos + 30 cm por caja + 10%', `Cable IRAM NM 247-3 ${s2}`);
  const td = elec.conduits.filter((c) => c.circuito === 'TD').reduce((a, c) => a + c.len, 0);
  R('15. Electricidad', 'conduit_td', Math.ceil(td * 1.2 + 2), 'ml', 'UTP cat. 6 + coaxil RG6 + fibra drop hasta el router', 'Cableado de datos/TV');
  const lum = elec.boxes.filter((b) => /^(L\d|A\d|LE|LB|LK)/.test(b.id));
  R('15. Electricidad', 'luminaria', lum.length, 'u', lum.map((b) => b.id).join(', '));
  const disp = elec.boxes.filter((b) => b.tipo === 'rect' && /^(S|T)/.test(b.id) && b.id !== 'TT');
  R('15. Electricidad', 'caja_rect', disp.length, 'u', 'tomas 2x10+T con obturador (IRAM 2071) y llaves de 1, 2 y 4 módulos, combinación', 'Llaves y tomas (línea estándar blanca)');

  // ---------------- Muebles ----------------
  R('16. Amoblamiento', 'cama_simple', 2, 'u', '2 camas de 1 plaza que se unen en 160x190 (pareja o dos personas)');
  for (const s3 of ['respaldo', 'placard', 'escritorio', 'mesa', 'sillon', 'tv']) R('16. Amoblamiento', s3, 1, 'u');
  R('16. Amoblamiento', 'mesa_luz', 3, 'u', '2 mesas de luz + mesa auxiliar del estar');
  R('16. Amoblamiento', 'silla', 3, 'u', '2 sillas de comedor + 1 silla de escritorio');
  R('16. Amoblamiento', 'textil_mostaza', 1, 'jgo', 'acolchados, almohadones (fundas lavables)');

  return { rows, sheets, wood, sheetsWall: lensW, lensT };
}

function countLens(lens) {
  const c = {};
  for (const l of lens) c[l.toFixed(2)] = (c[l.toFixed(2)] ?? 0) + 1;
  return Object.entries(c).sort((a, b) => b[0] - a[0]).map(([l, n]) => `${n} x ${l.replace('.', ',')} m`).join(' + ');
}

function osbArea(panels, mats) {
  let a = 0;
  for (const m of mats) for (const p of panels[m] ?? []) a += p.area;
  return a;
}

function roofArea(D) {
  return 2 * D.Li * (D.yRidge / Math.cos((D.PITCH * Math.PI) / 180));
}

export function areas(D) {
  const cub = D.ext.L * D.ext.W;
  return {
    cubiertaPorPlanta: r2(cub),
    cubiertaTotal: r2(cub * 2),
    utilPB: r2(D.Li * D.Wi - 0.095 * (3.36 - 1.965) - 0.095 * (D.Li - 2.33)),
    utilPA: r2(D.Li * D.Wi - (D.ST.hole.x1 * D.ST.hole.y1)),
  };
}

export { multiArea, r3 };
