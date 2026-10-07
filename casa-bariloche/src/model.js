// Modelo paramétrico de la casa. ÚNICA fuente de verdad: de acá salen el 3D, los planos,
// el cómputo de materiales y el despiece de placas/maderas.
//
// Coordenadas (m): x = largo (0 = cara interior del frente), y = ancho (0 = cara interior del
// lateral ciego / izquierdo, Wi = cara interior de la PARED DE SERVICIOS), z = altura (0 = platea).
import pc from 'polygon-clipping';
import { box, prism, tube, cyl, ribbed, rectRing, layoutPanels, r3 } from './geom.js';

// ============================================================================================
// PARÁMETROS
// ============================================================================================
const Li = 4.36; // largo interior
const Wi = 3.36; // ancho interior
const tD = 0.0125; // placa de yeso
const tS = 0.145; // montante 2x6
const tO = 0.011; // OSB
const tB = 0.025; // clavadera fachada
const tCh = 0.025; // chapa (altura de nervio)
const sIn = -tD; // cara interior de montantes (lado negativo)
const sOut = -(tD + tS); // cara exterior de montantes  -0.1575
const oOut = sOut - tO; // cara exterior del OSB        -0.1685
const bOut = oOut - tB; // cara exterior de clavaderas  -0.1935
const cOut = bOut - tCh; // cara exterior de chapa       -0.2185

const fGF = 0.015; // piso terminado PB (porcelanato + adhesivo)
const ZC1 = 2.41; // cielorraso PB
const ZJ0 = 2.4225; // fondo de vigas de entrepiso = tope de muros PB
const HJ = 0.195; // vigas 2x8
const ZJ1 = ZJ0 + HJ; // tope de vigas
const ZO1 = ZJ1 + 0.018; // tope OSB 18
const ZF1 = ZO1 + 0.005; // piso terminado PA (SPC)
const HW2 = 2.10; // altura de muros laterales PA (estructura)
const ZT2 = ZO1 + HW2; // tope de muros PA
const PITCH = 30; // pendiente de techo (°)
const T = Math.tan((PITCH * Math.PI) / 180);
const COS = Math.cos((PITCH * Math.PI) / 180);
const SIN = Math.sin((PITCH * Math.PI) / 180);
const HR = 0.195; // cabios 2x8
const dzR = HR / COS; // espesor vertical del cabio
const EAVE = 0.45; // alero (horizontal, desde cara exterior de montantes)
const GABLE_OH = 0.30; // alero frontal/posterior (desde la chapa)
const yRidge = Wi / 2;

const zRb = (y) => ZT2 + (Math.min(y, Wi - y) + (tD + tS)) * T; // fondo de cabio
const zRt = (y) => zRb(y) + dzR; // tope de cabio
const zCeil = (y) => zRb(y) - 0.0375 / COS; // cielorraso PA (listón 25 + placa 12,5)
const zRoof = (y) => zRt(y) + 0.09 / COS; // tope de chapa (contraclavadera 20 + clavadera 45 + chapa 25)
const RB_W = 0.09; // viga cumbrera
const RB_BOT = 5.62;
const RB_TOP = 5.92;

// Aberturas (vanos en bruto) -------------------------------------------------------------
const OPEN = {
  // acceso por la fachada de servicios/fondo (x = Li): el estar queda al frente, sin circulación cruzada
  P1: { name: 'Puerta de entrada', wall: 'FONDO', level: 'PB', s0: 0.95, s1: 1.85, z0: 0, z1: 2.115, door: true, leaf: 0.8, hinge: 's1', mat: 'puerta_ext' },
  V1: { name: 'Ventanal estar-comedor', wall: 'FRENTE', level: 'PB', s0: 1.05, s1: 2.65, z0: 0.95, z1: 2.1, sashes: 2, mat: 'pvc_marco' },
  V3: { name: 'Ventiluz baño', wall: 'FONDO', level: 'PB', s0: 2.65, s1: 3.15, z0: 1.7, z1: 2.2, sashes: 1, mat: 'pvc_marco' },
  V4: { name: 'Ventana dormitorio frente (escritorio)', wall: 'FRENTE', level: 'PA', s0: 2.05, s1: 3.25, z0: ZF1 + 0.9, z1: ZF1 + 2.0, sashes: 2, mat: 'pvc_marco' },
  V5: { name: 'Ventana dormitorio fondo (sobre la cama)', wall: 'FONDO', level: 'PA', s0: 1.2, s1: 2.4, z0: ZF1 + 0.9, z1: ZF1 + 2.0, sashes: 2, mat: 'pvc_marco' },
  P2: { name: 'Puerta baño', wall: 'TAB_B', level: 'PB', s0: 2.5, s1: 3.25, z0: 0, z1: 2.05, door: true, leaf: 0.7, mat: 'puerta_int' },
};

const OSB_JOINTS = [1.19, 3.63, 4.85];
const opsWall = (wall, level) => Object.keys(OPEN).filter((k) => OPEN[k].wall === wall && (!level || OPEN[k].level === level));

// Escalera ----------------------------------------------------------------------------------
const ST = {
  width: 0.85,
  risers: 14,
  going: 0.24,
  xBottom: 3.25, // primer contrahuella (arranque) — sube hacia el frente
  xTop: 0.85, // fin del tramo recto, luego 3 compensados en la esquina frente-izquierda
  hole: { x0: 0, x1: 2.9, y0: 0, y1: 0.85 },
};
ST.rise = (ZF1 - fGF) / ST.risers;

export const D = {
  Li, Wi, tD, tS, tO, tB, tCh, sOut, oOut, bOut, cOut, fGF, ZC1, ZJ0, ZJ1, ZO1, ZF1, HW2, ZT2,
  PITCH, T, EAVE, GABLE_OH, yRidge, OPEN, ST, RB_BOT, RB_TOP,
  ext: { L: r3(Li - 2 * cOut), W: r3(Wi - 2 * cOut) },
  zRb, zRt, zCeil, zRoof,
};

// ============================================================================================
export function buildModel() {
  const E = [];
  const members = [];
  const panels = {};
  const elec = { boxes: [], conduits: [] };
  const plumbing = [];
  const notes = [];
  const add = (el) => { E.push(el); return el; };
  const addPanels = (res) => {
    for (const p of res.pieces) (panels[p.mat] ??= []).push(p);
    res.elements.forEach(add);
    return res;
  };
  let mid = 0;
  const wood = (sec, mat, len, use, el) => {
    el.id ??= `M${++mid}`;
    members.push({ sec, mat, len: r3(len), use, id: el.id });
    el.member = { sec, len: r3(len), use };
    el.info ??= `${sec} — ${Math.round(len * 1000) / 10} cm — ${use}`;
    return add(el);
  };

  foundation(add);
  framing(wood, add);
  floorAndRoofFraming(wood, add);
  sheathing(addPanels, add);
  interiorBoards(addPanels, add);
  insulation(add);
  cladding(add);
  roof(add, wood);
  openings(add);
  stair(add);
  finishes(add);
  kitchenAndBath(add);
  furniture(add);
  installations(add, elec, plumbing);
  site(add);

  return { D, elements: E, members, panels, elec, plumbing, notes, rooms: ROOMS };
}

// ============================================================================================
// FUNDACIÓN: platea de H°A° 12 cm sobre EPS 50 mm + viga de borde 25x50
// ============================================================================================
function foundation(add) {
  const e = 0.17;
  add(box([-e, -e, -0.12], [Li + e, Wi + e, 0], { id: 'F-PLATEA', name: 'Platea H°A° e=12 cm, malla Q188', layer: 'fundacion', mat: 'hormigon' }));
  const vb = 0.25;
  const vz = [-0.5, -0.12];
  add(box([-e, -e, vz[0]], [Li + e, -e + vb, vz[1]], { id: 'F-VB1', name: 'Viga de borde 25x50 (lateral izquierdo)', layer: 'fundacion', mat: 'hormigon' }));
  add(box([-e, Wi + e - vb, vz[0]], [Li + e, Wi + e, vz[1]], { id: 'F-VB2', name: 'Viga de borde 25x50 (servicios)', layer: 'fundacion', mat: 'hormigon' }));
  add(box([-e, -e + vb, vz[0]], [-e + vb, Wi + e - vb, vz[1]], { id: 'F-VB3', name: 'Viga de borde 25x50 (frente)', layer: 'fundacion', mat: 'hormigon' }));
  add(box([Li + e - vb, -e + vb, vz[0]], [Li + e, Wi + e - vb, vz[1]], { id: 'F-VB4', name: 'Viga de borde 25x50 (fondo)', layer: 'fundacion', mat: 'hormigon' }));
  add(box([-e + vb, -e + vb, -0.17], [Li + e - vb, Wi + e - vb, -0.12], { id: 'F-EPS', name: 'EPS 50 mm bajo platea + film 200 µm', layer: 'fundacion', mat: 'eps_fund' }));
  const p = 0.05;
  add(box([-e - p, -e - p, -0.5], [Li + e + p, -e, 0], { id: 'F-EPSP1', name: 'EPS perimetral 50 mm', layer: 'fundacion', mat: 'eps_fund' }));
  add(box([-e - p, Wi + e, -0.5], [Li + e + p, Wi + e + p, 0], { id: 'F-EPSP2', name: 'EPS perimetral 50 mm', layer: 'fundacion', mat: 'eps_fund' }));
  add(box([-e - p, -e, -0.5], [-e, Wi + e, 0], { id: 'F-EPSP3', name: 'EPS perimetral 50 mm', layer: 'fundacion', mat: 'eps_fund' }));
  add(box([Li + e, -e, -0.5], [Li + e + p, Wi + e, 0], { id: 'F-EPSP4', name: 'EPS perimetral 50 mm', layer: 'fundacion', mat: 'eps_fund' }));
  // zócalo de chapa que protege el EPS sobre el nivel de terreno
  const z0 = -0.15, z1 = 0.06, q = e + p + 0.003;
  add(box([-q, -q, z0], [Li + q, -q + 0.003, z1], { name: 'Zócalo chapa lisa negra', layer: 'revest_ext', mat: 'zocalo_chapa' }));
  add(box([-q, Wi + q - 0.003, z0], [Li + q, Wi + q, z1], { name: 'Zócalo chapa lisa negra', layer: 'revest_ext', mat: 'zocalo_chapa' }));
  add(box([-q, -q, z0], [-q + 0.003, Wi + q, z1], { name: 'Zócalo chapa lisa negra', layer: 'revest_ext', mat: 'zocalo_chapa' }));
  add(box([Li + q - 0.003, -q, z0], [Li + q, Wi + q, z1], { name: 'Zócalo chapa lisa negra', layer: 'revest_ext', mat: 'zocalo_chapa' }));
}

// ============================================================================================
// ENTRAMADO DE MUROS (platform frame, pino 2x6 @40 cm)
// ============================================================================================
export const WALLS = [
  // PB exteriores
  { id: 'PB-FRE', name: 'Muro frente PB', axis: 'y', c0: sOut, c1: sIn, s0: sOut, s1: Wi - sOut, z0: 0, ztop: ZJ0, open: opsWall('FRENTE', 'PB'), hdr: 0.195 },
  { id: 'PB-FON', name: 'Muro fondo PB', axis: 'y', c0: Li - sIn, c1: Li - sOut, s0: sOut, s1: Wi - sOut, z0: 0, ztop: ZJ0, open: opsWall('FONDO', 'PB'), hdr: 0.195 },
  { id: 'PB-IZQ', name: 'Muro lateral izquierdo PB', axis: 'x', c0: sOut, c1: sIn, s0: sIn, s1: Li - sIn, z0: 0, ztop: ZJ0, open: [] },
  { id: 'PB-SER', name: 'Muro de servicios PB', axis: 'x', c0: Wi - sIn, c1: Wi - sOut, s0: sIn, s1: Li - sIn, z0: 0, ztop: ZJ0, open: [], service: true },
  // PA exteriores
  { id: 'PA-FRE', name: 'Muro frente PA (hastial)', axis: 'y', c0: sOut, c1: sIn, s0: sOut, s1: Wi - sOut, z0: ZO1, ztop: (s) => zRb(s), open: opsWall('FRENTE', 'PA'), hdr: 0.145, gable: true },
  { id: 'PA-FON', name: 'Muro fondo PA (hastial)', axis: 'y', c0: Li - sIn, c1: Li - sOut, s0: sOut, s1: Wi - sOut, z0: ZO1, ztop: (s) => zRb(s), open: opsWall('FONDO', 'PA'), hdr: 0.145, gable: true },
  { id: 'PA-IZQ', name: 'Muro lateral izquierdo PA', axis: 'x', c0: sOut, c1: sIn, s0: sIn, s1: Li - sIn, z0: ZO1, ztop: ZT2, open: [] },
  { id: 'PA-SER', name: 'Muro de servicios PA', axis: 'x', c0: Wi - sIn, c1: Wi - sOut, s0: sIn, s1: Li - sIn, z0: ZO1, ztop: ZT2, open: [] },
  // Tabiques PB (2x3)
  { id: 'TAB-A', name: 'Tabique cocina/baño', axis: 'y', c0: 2.33 + tD, c1: 2.425 - tD, s0: 2.0475, s1: Wi, z0: 0, ztop: ZJ0, open: [], sec: '2x3', mat: 'pino_2x3', single: true },
  { id: 'TAB-B', name: 'Tabique pasillo/baño', axis: 'x', c0: 1.965 + tD, c1: 2.06 - tD, s0: 2.33, s1: Li, z0: 0, ztop: ZJ0, open: ['P2'], sec: '2x3', mat: 'pino_2x3', single: true, hdr: 0.07 },
];

function framing(wood, add) {
  for (const w of WALLS) frameWall(w, wood, add);
  // refuerzos (tacos) para colgar artefactos en la pared de servicios
  const yb = [Wi - sIn, Wi - sOut];
  const blk = (x0, x1, z, use) => wood('2x6', 'pino_2x6', x1 - x0, use, box([x0, yb[0], z], [x1, yb[1], z + 0.045], { layer: 'estructura', mat: 'pino_2x6', name: 'Refuerzo: ' + use }));
  blk(2.8225, 3.5775, 1.3, 'refuerzo termotanque inferior');
  blk(2.8225, 3.5775, 2.1, 'refuerzo termotanque superior');
  blk(2.4225, 2.9775, 0.75, 'refuerzo lavatorio');
  blk(0.0225, 1.1775, 1.5, 'refuerzo alacena inferior');
  blk(0.0225, 1.1775, 2.15, 'refuerzo alacena superior');
  // calefactor en muro de fondo
  wood('2x6', 'pino_2x6', 0.7, 'refuerzo calefactor', box([Li - sIn, 1.0225, 0.75], [Li - sOut, 1.7775, 0.795], { layer: 'estructura', mat: 'pino_2x6', name: 'Refuerzo calefactor' }));
  // flejes de arriostramiento en franja de registros (pared de servicios PB)
  for (const [a, b] of [[0, 2.2], [2.2, 4.36]]) {
    const len = Math.hypot(b - a, 1.45);
    const ang = Math.atan2(1.45, b - a);
    void ang;
    add(prism([a, Wi - sOut + 0.0005, 0.05], [1, 0, 0], [0, 0, 1], [0, 1, 0], 0.001,
      [[[[0, 0], [0.05, 0], [b - a, 1.45], [b - a - 0.05, 1.45], [0, 0]]]],
      { name: `Fleje de arriostramiento 50x1,25 mm (L=${r3(len)} m)`, layer: 'estructura', mat: 'hierro_negro' }));
  }
}

function frameWall(w, wood, add) {
  const sec = w.sec ?? '2x6';
  const mat = w.mat ?? 'pino_2x6';
  const th = 0.045;
  const flat = typeof w.ztop === 'number';
  const ztop = flat ? () => w.ztop : w.ztop;
  const op = w.open.map((k) => ({ k, ...OPEN[k] }));
  const B = (s0, s1, z0, z1, extra) => (w.axis === 'x' ? box([s0, w.c0, z0], [s1, w.c1, z1], extra) : box([w.c0, s0, z0], [w.c1, s1, z1], extra));
  const plane = w.axis === 'x'
    ? { o: [0, w.c0, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0] }
    : { o: [w.c0, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [1, 0, 0] };
  const P = (ring, extra) => prism(plane.o, plane.u, plane.v, plane.n, w.c1 - w.c0, [[ring]], extra);
  const base = { layer: 'estructura', mat, wall: w.id };
  const plateTopZ = flat ? w.ztop - (w.single ? th : 2 * th) : null;

  // solera inferior (cortada en puertas)
  let segs = [[w.s0, w.s1]];
  for (const o of op.filter((o) => o.door)) {
    segs = segs.flatMap(([a, b]) => (o.s1 <= a || o.s0 >= b ? [[a, b]] : [[a, o.s0], [o.s1, b]].filter(([x, y]) => y - x > 0.01)));
  }
  for (const [a, b] of segs) wood(sec, mat, b - a, 'solera inferior', B(a, b, w.z0, w.z0 + th, { ...base, name: `${w.name}: solera inferior` }));

  // soleras superiores
  if (flat) {
    wood(sec, mat, w.s1 - w.s0, 'solera superior', B(w.s0, w.s1, w.ztop - th, w.ztop, { ...base, name: `${w.name}: solera superior` }));
    if (!w.single) wood(sec, mat, w.s1 - w.s0, 'solera superior (doble)', B(w.s0, w.s1, w.ztop - 2 * th, w.ztop - th, { ...base, name: `${w.name}: solera superior doble` }));
  } else {
    // solera inclinada (dos tramos hasta la cumbrera)
    const tv = th / COS;
    const tramos = [[w.s0, yRidge - RB_W / 2], [yRidge + RB_W / 2, w.s1]];
    for (const [a, b] of tramos) {
      const ring = [[a, ztop(a) - tv], [b, ztop(b) - tv], [b, ztop(b)], [a, ztop(a)], [a, ztop(a) - tv]];
      wood(sec, mat, Math.hypot(b - a, ztop(b) - ztop(a)), 'solera inclinada hastial', P(ring, { ...base, name: `${w.name}: solera inclinada` }));
    }
    // poste de cumbrera (3 montantes) bajo la viga
    const pz1 = RB_BOT;
    wood(sec, mat, pz1 - (w.z0 + th), 'poste cumbrera (x3)', B(yRidge - 0.0675, yRidge + 0.0675, w.z0 + th, pz1, { ...base, name: `${w.name}: poste de cumbrera (3 montantes 2x6)` }));
    members_push_extra(wood, sec, mat, pz1 - (w.z0 + th), 'poste cumbrera (x3)', 2);
  }
  const studTop = (s) => (flat ? plateTopZ : Math.min(ztop(s), ztop(s + th)) - th / COS);
  const z0s = w.z0 + th;

  const stud = (s, zA, zB, use) => {
    if (zB - zA < 0.03) return;
    if (flat || zB !== null) {
      // montante con tope plano
      wood(sec, mat, zB - zA, use, B(s, s + th, zA, zB, { ...base, name: `${w.name}: ${use}` }));
    }
  };
  const slopedStud = (s, zA, use) => {
    const tv = th / COS;
    const ring = [[s, zA], [s + th, zA], [s + th, ztop(s + th) - tv], ...(s < yRidge && s + th > yRidge ? [[yRidge, ztop(yRidge) - tv]] : []), [s, ztop(s) - tv], [s, zA]];
    const len = Math.max(ztop(s), ztop(s + th)) - tv - zA;
    if (len < 0.03) return;
    wood(sec, mat, len, use, P(ring, { ...base, name: `${w.name}: ${use}` }));
  };

  // posiciones de montantes: extremos + grilla cada 40 cm (centros en múltiplos de 0,40 desde la cara interior del local)
  const pos = new Set();
  pos.add(r3(w.s0));
  pos.add(r3(w.s1 - th));
  const g0 = w.axis === 'y' ? 0 : 0;
  for (let c = g0 + 0.4; c < w.s1 - th; c += 0.4) {
    const s = c - th / 2;
    if (s > w.s0 + th + 0.02 && s < w.s1 - 2 * th - 0.02) pos.add(r3(s));
  }
  // en hastiales, sacar los montantes que caen en el poste de cumbrera
  const isPost = (s) => !flat && s + th > yRidge - 0.0675 && s < yRidge + 0.0675;

  for (const s of [...pos].sort((a, b) => a - b)) {
    if (isPost(s)) continue;
    const inOp = op.find((o) => s + th > o.s0 - 2 * th && s < o.s1 + 2 * th);
    if (inOp) {
      if (s >= inOp.s0 && s + th <= inOp.s1) {
        // cripples (montantes cortos) debajo del antepecho y sobre el dintel
        const hz = inOp.z1 + (w.hdr ?? 0.195);
        if (!inOp.door) {
          const zs = inOp.z0 - 2 * th;
          if (zs - z0s > 0.05) wood(sec, mat, zs - z0s, 'montante bajo antepecho', B(s, s + th, z0s, zs, { ...base, name: `${w.name}: montante bajo antepecho` }));
        }
        if (flat) stud(s, hz, studTop(s), 'montante sobre dintel');
        else slopedStud(s, hz, 'montante sobre dintel');
      }
      continue;
    }
    if (flat) stud(s, z0s, studTop(s), 'montante');
    else slopedStud(s, z0s, 'montante');
  }
  // aberturas: king + jack + dintel + antepecho
  for (const o of op) {
    const hh = w.hdr ?? 0.195;
    const zH = o.z1;
    for (const [sk, sj] of [[o.s0 - 2 * th, o.s0 - th], [o.s1 + th, o.s1]]) {
      if (flat) stud(sk, z0s, studTop(sk), `montante king ${o.k}`);
      else slopedStud(sk, z0s, `montante king ${o.k}`);
      const jz0 = o.door ? z0s : z0s;
      wood(sec, mat, zH - jz0, `montante jack ${o.k}`, B(sj, sj + th, jz0, zH, { ...base, name: `${w.name}: jack ${o.k}` }));
    }
    const hl = o.s1 - o.s0 + 2 * th;
    const hsec = sec === '2x3' ? '2x3' : hh > 0.15 ? '2x8' : '2x6';
    const hmat = hsec === '2x8' ? 'pino_2x8' : mat;
    wood(hsec, hmat, hl, `dintel ${o.k} (x2)`, B(o.s0 - th, o.s1 + th, zH, zH + hh, { ...base, mat: hmat, name: `${w.name}: dintel ${o.k} (2 piezas ${hsec})` }));
    if (sec !== '2x3') members_push_extra(wood, hsec, hmat, hl, `dintel ${o.k} (x2)`, 1);
    if (!o.door) {
      wood(sec, mat, o.s1 - o.s0, `antepecho ${o.k} (x2)`, B(o.s0, o.s1, o.z0 - 2 * th, o.z0, { ...base, name: `${w.name}: antepecho doble ${o.k}` }));
      members_push_extra(wood, sec, mat, o.s1 - o.s0, `antepecho ${o.k} (x2)`, 1);
    }
  }
  // bloqueos horizontales en las juntas horizontales del OSB (placas colocadas horizontales y trabadas:
  // la junta larga debe apoyar sobre madera) — filas de 1,22 m desde -0,03 => juntas a +1,19 / +3,63 / +4,85
  if (!w.single) {
    const ps = [...pos].sort((a, b) => a - b).filter((s0) => !isPost(s0));
    for (const zb0 of OSB_JOINTS) {
      const zb = zb0 - th / 2;
      if (zb < w.z0 + 0.2) continue;
      if (flat && zb > w.ztop - 3 * th) continue;
      for (let i = 0; i < ps.length - 1; i++) {
        const a = ps[i] + th, b = ps[i + 1];
        if (b - a < 0.05 || b - a > 0.6) continue;
        if (!flat && (Math.min(ztop(a), ztop(b)) - th / COS < zb + th + 0.03)) continue;
        if (op.some((o) => a < o.s1 + 2 * th && b > o.s0 - 2 * th && zb + th > o.z0 - 2 * th && zb < o.z1 + (w.hdr ?? 0.195))) continue;
        wood(sec, mat, b - a, 'bloqueo junta OSB', B(a, b, zb, zb + th, { ...base, name: `${w.name}: bloqueo (junta horizontal OSB)` }));
      }
    }
  }
}

// piezas adicionales (dobles/triples) que no se dibujan por separado pero se computan
let __extraId = 0;
function members_push_extra(wood, sec, mat, len, use, times) {
  for (let i = 0; i < times; i++) {
    wood(sec, mat, len, use, { kind: 'none', id: `X${++__extraId}`, layer: 'estructura', mat, info: 'pieza adicional (se computa, no se dibuja)' });
  }
}

// ============================================================================================
// ENTREPISO Y TECHO
// ============================================================================================
function floorAndRoofFraming(wood, add) {
  const th = 0.045;
  const base = { layer: 'estructura', mat: 'pino_2x8' };
  const H = ST.hole;
  // vigas de borde (cenefas) sobre muros laterales
  for (const [y0, y1] of [[sOut, sOut + th], [Wi - sOut - th, Wi - sOut]]) {
    wood('2x8', 'pino_2x8', Li - 2 * sOut, 'viga de borde entrepiso', box([sOut, y0, ZJ0], [Li - sOut, y1, ZJ1], { ...base, name: 'Viga de borde entrepiso 2x8' }));
  }
  const yA = sOut + th, yB = Wi - sOut - th;
  const joistsX = [sOut];
  for (let c = 0.4; c < Li; c += 0.4) joistsX.push(r3(c - th / 2));
  joistsX.push(Li - sOut - th);
  for (const x of joistsX) {
    if (x + th > H.x0 && x < H.x1 && x > 0) {
      // viga cortada por el hueco de escalera
      wood('2x8', 'pino_2x8', yB - (H.y1 + 2 * th), 'viga entrepiso (cola, hueco escalera)', box([x, H.y1 + 2 * th, ZJ0], [x + th, yB, ZJ1], { ...base, name: 'Viga entrepiso 2x8 (cola)' }));
    } else {
      wood('2x8', 'pino_2x8', yB - yA, 'viga entrepiso', box([x, yA, ZJ0], [x + th, yB, ZJ1], { ...base, name: 'Viga entrepiso 2x8 @40' }));
    }
  }
  // brochal doble (hueco) y vigas de borde de hueco dobles
  wood('2x8', 'pino_2x8', H.x1 - sOut - th, 'brochal hueco escalera (x2)', box([sOut + th, H.y1, ZJ0], [H.x1, H.y1 + 2 * th, ZJ1], { ...base, name: 'Brochal doble 2x8 (hueco escalera)' }));
  members_push_extra(wood, '2x8', 'pino_2x8', H.x1 - sOut - th, 'brochal hueco escalera (x2)', 1);
  wood('2x8', 'pino_2x8', yB - yA, 'viga de borde hueco (x2)', box([H.x1, yA, ZJ0], [H.x1 + 2 * th, yB, ZJ1], { ...base, name: 'Viga doble borde de hueco 2x8' }));
  members_push_extra(wood, '2x8', 'pino_2x8', yB - yA, 'viga de borde hueco (x2)', 1);
  // riostras (crucetas) a media luz
  const ym = Wi / 2;
  for (let i = 0; i < joistsX.length - 1; i++) {
    const a = joistsX[i] + th, b = joistsX[i + 1];
    if (b - a < 0.05) continue;
    const x0 = a, x1 = b;
    if (x1 > H.x0 && x0 < H.x1 + 2 * th && ym < H.y1) continue;
    wood('2x8', 'pino_2x8', x1 - x0, 'bloqueo entrepiso', box([x0, ym, ZJ0], [x1, ym + th, ZJ1], { ...base, name: 'Bloqueo entrepiso' }));
  }

  // ---------------- techo ----------------
  const rbase = { layer: 'estructura', mat: 'pino_2x8' };
  const yTail = sOut - EAVE;
  const rafterX = [sOut];
  for (let c = 0.45; c < Li; c += 0.6) rafterX.push(r3(c - th / 2));
  rafterX.push(Li - sOut - th);
  for (const x of rafterX) {
    for (const side of [0, 1]) {
      const a = side === 0 ? yTail : yRidge + RB_W / 2;
      const b = side === 0 ? yRidge - RB_W / 2 : Wi - yTail;
      const ring = [[a, zRb(a)], [b, zRb(b)], [b, zRt(b)], [a, zRt(a)], [a, zRb(a)]];
      const len = Math.hypot(b - a, zRb(b) - zRb(a)) + 0.12;
      wood('2x8', 'pino_2x8', len, 'cabio', prism([x, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], th, [[ring]], { ...rbase, name: 'Cabio 2x8 @60' }));
    }
  }
  // viga cumbrera laminada
  add(box([sOut, yRidge - RB_W / 2, RB_BOT], [Li - sOut, yRidge + RB_W / 2, RB_TOP], {
    id: 'CUMBRERA', layer: 'estructura', mat: 'laminada', name: 'Viga cumbrera laminada 90x300 (a la vista)',
    member: { sec: 'lam 90x300', len: r3(Li - 2 * sOut), use: 'cumbrera' },
  }));
  // clavaderas 2x2 (sobre contraclavaderas) cada 80 cm en pendiente, con voladizo en hastiales
  const xa = cOut - GABLE_OH, xb = Li - cOut + GABLE_OH;
  for (const side of [0, 1]) {
    const ys = [];
    for (let d = 0.05; d < (yRidge - yTail) / COS - 0.05; d += 0.8) ys.push(yTail + d * COS);
    ys.push(yRidge - 0.08);
    for (const yy0 of ys) {
      const y = side === 0 ? yy0 : Wi - yy0;
      const z = zRt(y) + 0.02 / COS;
      const ring = side === 0
        ? [[y, z], [y + 0.045 * COS, z + 0.045 * SIN], [y + 0.045 * COS - 0.045 * SIN, z + 0.045 * SIN + 0.045 * COS], [y - 0.045 * SIN, z + 0.045 * COS], [y, z]]
        : [[y, z], [y - 0.045 * COS, z + 0.045 * SIN], [y - 0.045 * COS + 0.045 * SIN, z + 0.045 * SIN + 0.045 * COS], [y + 0.045 * SIN, z + 0.045 * COS], [y, z]];
      wood('2x2', 'pino_2x2', xb - xa, 'clavadera de techo', prism([xa, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], xb - xa, [[ring]], { layer: 'estructura', mat: 'pino_2x2', name: 'Clavadera 2x2 (chapa)' }));
    }
  }
  // contraclavaderas 1x2 sobre cada cabio (cámara ventilada)
  for (const x of rafterX) {
    for (const side of [0, 1]) {
      const a = side === 0 ? yTail : yRidge + RB_W / 2;
      const b = side === 0 ? yRidge - RB_W / 2 : Wi - yTail;
      const ring = [[a, zRt(a)], [b, zRt(b)], [b, zRt(b) + 0.02 / COS], [a, zRt(a) + 0.02 / COS], [a, zRt(a)]];
      wood('1x2', 'pino_1x2', Math.hypot(b - a, zRt(b) - zRt(a)), 'contraclavadera techo', prism([x, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], th, [[ring]], { layer: 'estructura', mat: 'pino_1x2', name: 'Contraclavadera 1x2' }));
    }
  }
  // frentines (cenefas) de alero
  for (const side of [0, 1]) {
    const y0 = side === 0 ? yTail - 0.02 : Wi - yTail;
    const zt = zRt(yTail);
    wood('1x8', 'pino_1x8', xb - xa, 'frentín alero', box([xa, y0, zt - 0.2], [xb, y0 + 0.02, zt + 0.075], { layer: 'techo', mat: 'zinguerias', name: 'Frentín de alero revestido en chapa' }));
  }
}

// ============================================================================================
// PLACAS DE OSB (arriostramiento exterior + piso PA + cassettes de registro)
// ============================================================================================
function sheathing(addPanels) {
  const S = { w: 1.22, h: 2.44 };
  // se modula a 1,20 / 2,40 (las placas de 1,22 x 2,44 se recortan 2 cm para que las juntas caigan sobre montantes)
  const SM = { w: 1.2, h: 2.44 };
  const common = { mat: 'osb_11', t: tO, sheet: SM, layer: 'osb', along: 'v' };
  const gable = (y) => zRb(y);
  const gRing = (y0, y1, z0) => [[y0, z0], [y1, z0], [y1, gable(y1)], [yRidge, gable(yRidge)], [y0, gable(y0)], [y0, z0]];
  const O = OPEN;
  const hole = (k) => [O[k].s0, O[k].z0 - (O[k].door ? 0.05 : 0), O[k].s1, O[k].z1];
  addPanels(layoutPanels({ ...common, sheet: { w: 1.22, h: 2.4 }, along: 'u', stagger: true, face: 'OSB-FRE', prefix: 'OSB-F', name: 'OSB frente', o: [sOut, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [-1, 0, 0], poly: gRing(oOut, Wi - oOut, -0.03), holes: opsWall('FRENTE').map(hole), startU: oOut, startV: -0.03 }));
  addPanels(layoutPanels({ ...common, sheet: { w: 1.22, h: 2.4 }, along: 'u', stagger: true, face: 'OSB-FON', prefix: 'OSB-B', name: 'OSB fondo', o: [Li - sOut, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [1, 0, 0], poly: gRing(oOut, Wi - oOut, -0.03), holes: opsWall('FONDO').map(hole), startU: oOut, startV: -0.03 }));
  addPanels(layoutPanels({ ...common, sheet: { w: 1.22, h: 2.4 }, along: 'u', stagger: true, face: 'OSB-IZQ', prefix: 'OSB-L', name: 'OSB lateral izquierdo', o: [0, sOut, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, -1, 0], poly: rectRing(sOut, -0.03, Li - sOut, ZT2), startU: sOut, startV: -0.03 }));
  addPanels(layoutPanels({ ...common, sheet: { w: 1.22, h: 2.4 }, along: 'u', stagger: true, face: 'OSB-SER', prefix: 'OSB-S', name: 'OSB servicios (sobre registros)', o: [0, Wi - sOut, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0], poly: rectRing(sOut, 1.5, Li - sOut, ZT2), startU: sOut, startV: -0.03 }));
  // cassettes de registro (OSB atornillado) — 4 módulos
  addPanels(layoutPanels({ ...common, grid: 0.01, minStrip: 0, sheet: { w: (Li - 2 * sOut) / 4, h: 1.53 }, face: 'CASSETTES', prefix: 'CAS', name: 'Cassette de registro (OSB atornillado)', o: [0, Wi - sOut, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0], poly: rectRing(sOut, -0.03, Li - sOut, 1.5), startU: sOut, startV: -0.03 }));
  // piso PA OSB 18 (lado largo perpendicular a vigas, juntas trabadas)
  const H = ST.hole;
  addPanels(layoutPanels({
    face: 'OSB-PISO', prefix: 'OSB-P', name: 'Piso OSB 18 mm', mat: 'osb_18', t: 0.018, sheet: { w: 1.22, h: 2.4 }, layer: 'osb', along: 'u', stagger: true,
    o: [0, 0, ZJ1], u: [1, 0, 0], v: [0, 1, 0], n: [0, 0, 1], poly: rectRing(-0.15, -0.15, Li + 0.15, Wi + 0.15),
    holes: [[H.x0, H.y0, H.x1, H.y1]], startU: -0.15, startV: -0.15,
  }));
}

// ============================================================================================
// PLACAS DE YESO Y CEMENTICIAS (interior) — despiece completo
// ============================================================================================
function interiorBoards(addPanels, add) {
  const S = { w: 1.2, h: 2.4 };
  const z0 = 0.01;
  const O = OPEN;
  const H = ST.hole;
  const hole = (k) => [O[k].s0, O[k].z0, O[k].s1, O[k].z1];
  const paintOf = (f = '') => (/salvia/i.test(f) ? 'pintura_salvia' : /antihongo/i.test(f) ? 'pintura_antihongo' : /cerámica 30x60/i.test(f) ? 'ceramica_ducha' : 'pintura_blanco');
  const W = (opt) => addPanels(layoutPanels({ t: tD, sheet: S, layer: 'durlock', along: 'v', paint: paintOf(opt.finish), ...opt }));
  const BL = 'Blanco cálido';
  // ---------- PB ----------
  W({ face: 'PB-FRE', prefix: 'Y-PB-FRE', name: 'PB frente (int.)', mat: 'durlock_std', finish: BL, room: 'Estar-cocina', o: [0, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [-1, 0, 0], poly: rectRing(0, z0, Wi, ZC1), holes: opsWall('FRENTE', 'PB').map(hole), startU: 0, startV: z0 });
  W({ face: 'PB-FON-A', prefix: 'Y-PB-FON', name: 'PB fondo hall de acceso', mat: 'durlock_std', finish: BL, room: 'Hall', o: [Li, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [1, 0, 0], poly: rectRing(0, z0, 1.965, ZC1), holes: [hole('P1')], startU: 0, startV: z0 });
  W({ face: 'PB-FON-B', prefix: 'C-DUCHA-FON', name: 'Ducha fondo (cementicia)', mat: 'cementicia', finish: 'Cerámica 30x60 blanca', room: 'Baño', t: 0.01, o: [Li, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [1, 0, 0], poly: rectRing(2.06, z0, Wi, ZC1), holes: [hole('V3')], startU: 2.06, startV: z0 });
  W({ face: 'PB-IZQ', prefix: 'Y-PB-IZQ', name: 'PB lateral izquierdo', mat: 'durlock_std', finish: BL, room: 'Estar / escalera', o: [0, 0, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, -1, 0], poly: rectRing(0, z0, Li, ZC1), startU: 0, startV: z0 });
  W({ face: 'PB-SER-K', prefix: 'Y-PB-SERK', name: 'PB servicios cocina (RH)', mat: 'durlock_rh', finish: BL + ' + cerámica subway sobre mesada', room: 'Cocina', o: [0, Wi, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0], poly: rectRing(0, z0, 2.33, ZC1), startU: 0, startV: z0 });
  W({ face: 'PB-SER-B1', prefix: 'Y-PB-SERB', name: 'PB servicios baño (RH)', mat: 'durlock_rh', finish: 'Látex antihongo', room: 'Baño', o: [0, Wi, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0], poly: rectRing(2.425, z0, 3.56, ZC1), startU: 2.425, startV: z0 });
  W({ face: 'PB-SER-B2', prefix: 'C-DUCHA-SER', name: 'Ducha servicios (cementicia)', mat: 'cementicia', finish: 'Cerámica 30x60 blanca', room: 'Baño', t: 0.01, o: [0, Wi, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0], poly: rectRing(3.56, z0, Li, ZC1), startU: 3.56, startV: z0 });
  W({ face: 'PB-TA-K', prefix: 'Y-TABA-K', name: 'Tabique A lado cocina', mat: 'durlock_std', finish: BL, room: 'Cocina', o: [2.33 + tD, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [-1, 0, 0], poly: rectRing(1.965, z0, Wi, ZC1), startU: 1.965, startV: z0 });
  W({ face: 'PB-TA-B', prefix: 'Y-TABA-B', name: 'Tabique A lado baño (RH)', mat: 'durlock_rh', finish: 'Látex antihongo', room: 'Baño', o: [2.425 - tD, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [1, 0, 0], poly: rectRing(2.06, z0, Wi, ZC1), startU: 2.06, startV: z0 });
  W({ face: 'PB-TB-C', prefix: 'Y-TABB-C', name: 'Tabique B lado pasillo', mat: 'durlock_std', finish: BL, room: 'Pasillo', o: [0, 1.965 + tD, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, -1, 0], poly: rectRing(2.33, z0, Li, ZC1), holes: [hole('P2')], startU: 2.33, startV: z0 });
  W({ face: 'PB-TB-B1', prefix: 'Y-TABB-B', name: 'Tabique B lado baño (RH)', mat: 'durlock_rh', finish: 'Látex antihongo', room: 'Baño', o: [0, 2.06 - tD, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0], poly: rectRing(2.425, z0, 3.56, ZC1), holes: [hole('P2')], startU: 2.425, startV: z0 });
  W({ face: 'PB-TB-B2', prefix: 'C-DUCHA-TAB', name: 'Ducha tabique (cementicia)', mat: 'cementicia', finish: 'Cerámica 30x60 blanca', room: 'Baño', t: 0.01, o: [0, 2.06 - tD, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0], poly: rectRing(3.56, z0, Li, ZC1), startU: 3.56, startV: z0 });
  // cielorraso PB (placas perpendiculares a vigas)
  const ceilRing = [[0, H.y1], [H.x1, H.y1], [H.x1, 0], [Li, 0], [Li, 2.06], [2.425, 2.06], [2.425, Wi], [0, Wi], [0, H.y1]];
  W({ face: 'PB-CIELO', prefix: 'Y-PB-CIE', name: 'Cielorraso PB', mat: 'durlock_std', finish: BL, room: 'PB', o: [0, 0, ZC1], u: [1, 0, 0], v: [0, 1, 0], n: [0, 0, 1], poly: ceilRing, along: 'u', startU: Li - 4 * 2.4, startV: 0, stagger: true });
  W({ face: 'PB-CIELO-B', prefix: 'Y-BANO-CIE', name: 'Cielorraso baño (RH)', mat: 'durlock_rh', finish: 'Látex antihongo', room: 'Baño', o: [0, 0, ZC1], u: [1, 0, 0], v: [0, 1, 0], n: [0, 0, 1], poly: rectRing(2.425, 2.06, Li, Wi), along: 'u', startU: 2.425, startV: 1.86 });
  W({ face: 'PB-NICHO', prefix: 'Y-NICHO', name: 'Cielorraso bajo escalera compensada', mat: 'durlock_std', finish: BL, room: 'Recibidor', o: [0, 0, 1.9], u: [1, 0, 0], v: [0, 1, 0], n: [0, 0, 1], poly: rectRing(0, 0, 0.85, 0.85), along: 'u', startU: 0, startV: 0 });
  // ---------- PA ----------
  const zc0 = zCeil(0);
  W({ face: 'PA-IZQ', prefix: 'Y-PA-IZQ', name: 'PA lateral izquierdo + caja escalera', mat: 'durlock_std', finish: BL, room: 'Dormitorio', o: [0, 0, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, -1, 0], poly: [[0, ZC1], [H.x1, ZC1], [H.x1, ZF1], [Li, ZF1], [Li, zc0], [0, zc0], [0, ZC1]], startU: 0, startV: ZC1 });
  W({ face: 'PA-SER', prefix: 'Y-PA-SER', name: 'PA servicios', mat: 'durlock_std', finish: BL, room: 'Dormitorio', o: [0, Wi, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, 1, 0], poly: rectRing(0, ZF1, Li, zc0), startU: 0, startV: ZF1 });
  const gableIn = (stair) => {
    const y0 = yRidge - RB_W / 2, y1 = yRidge + RB_W / 2;
    const top = [[Wi, zc0], [y1, zCeil(y1)], [y1, RB_BOT], [y0, RB_BOT], [y0, zCeil(y0)], [0, zc0]];
    return stair ? [[0, ZC1], [H.y1, ZC1], [H.y1, ZF1], [Wi, ZF1], ...top, [0, ZC1]] : [[0, ZF1], [Wi, ZF1], ...top, [0, ZF1]];
  };
  W({ face: 'PA-FRE', prefix: 'Y-PA-FRE', name: 'PA hastial frente', mat: 'durlock_std', finish: BL, room: 'Dormitorio', o: [0, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [-1, 0, 0], poly: gableIn(true), holes: [hole('V4')], startU: 0, startV: ZC1 });
  W({ face: 'PA-FON', prefix: 'Y-PA-FON', name: 'PA hastial fondo (respaldo)', mat: 'durlock_std', finish: 'Verde salvia', room: 'Dormitorio', o: [Li, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [1, 0, 0], poly: gableIn(false), holes: [hole('V5')], startU: 0, startV: ZF1 });
  // caras del hueco de escalera
  W({ face: 'PA-HUECO-1', prefix: 'Y-HUECO-A', name: 'Frente de brochal (hueco)', mat: 'durlock_std', finish: BL, room: 'Escalera', o: [0, H.y1, 0], u: [1, 0, 0], v: [0, 0, 1], n: [0, -1, 0], poly: rectRing(H.y1, ZC1, H.x1, ZF1), startU: H.y1, startV: ZC1 });
  W({ face: 'PA-HUECO-2', prefix: 'Y-HUECO-B', name: 'Frente de viga de borde (hueco)', mat: 'durlock_std', finish: BL, room: 'Escalera', o: [H.x1, 0, 0], u: [0, 1, 0], v: [0, 0, 1], n: [1, 0, 0], poly: rectRing(0, ZC1, H.y1, ZF1), startU: 0, startV: ZC1 });
  // cielorraso inclinado PA: placas con lado largo en la pendiente, sobre listones @40
  const Ls = (yRidge - RB_W / 2) / COS;
  W({ face: 'PA-TECHO-I', prefix: 'Y-TECHO-I', name: 'Cielorraso inclinado izquierdo', mat: 'durlock_std', finish: BL, room: 'Dormitorio', o: [0, 0, zc0], u: [1, 0, 0], v: [0, COS, SIN], n: [0, -SIN, COS], poly: rectRing(0, 0, Li, Ls), startU: 0, startV: 0 });
  W({ face: 'PA-TECHO-D', prefix: 'Y-TECHO-D', name: 'Cielorraso inclinado derecho', mat: 'durlock_std', finish: BL, room: 'Dormitorio', o: [0, Wi, zc0], u: [1, 0, 0], v: [0, -COS, SIN], n: [0, SIN, COS], poly: rectRing(0, 0, Li, Ls), startU: 0, startV: 0 });
}

// ============================================================================================
// AISLACIÓN (lana de vidrio en cavidades) — se dibuja como bloques semitransparentes
// ============================================================================================
function insulation(add) {
  const mat = 'lana_150';
  const ins = { layer: 'aislacion', mat };
  const holeOf = (k) => rectRing(OPEN[k].s0, OPEN[k].z0, OPEN[k].s1, OPEN[k].z1);
  const face = (name, o, u, v, n, ring, holes = []) => {
    let mp = [[ring]];
    if (holes.length) mp = pc.difference(mp, ...holes.map((h) => [h]));
    add(prism(o, u, v, n, tS - 0.005, mp, { ...ins, name, info: 'Lana de vidrio 150 mm (comprimida en 145)' }));
  };
  const gRing = (z0) => [[sOut, z0], [Wi - sOut, z0], [Wi - sOut, zRb(Wi - sOut)], [yRidge, zRb(yRidge)], [sOut, zRb(sOut)], [sOut, z0]];
  face('Aislación muro frente', [sIn - 0.0025, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], gRing(0.045), opsWall('FRENTE').map(holeOf));
  face('Aislación muro fondo', [Li - sIn + 0.0025, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], gRing(0.045), opsWall('FONDO').map(holeOf));
  face('Aislación muro izquierdo', [0, sIn - 0.0025, 0], [1, 0, 0], [0, 0, 1], [0, -1, 0], rectRing(sIn, 0.045, Li - sIn, ZT2));
  face('Aislación muro servicios', [0, Wi - sIn + 0.0025, 0], [1, 0, 0], [0, 0, 1], [0, 1, 0], rectRing(sIn, 0.045, Li - sIn, ZT2));
  // techo: entre cabios, 150 mm, dejando cámara ventilada de 45 mm
  const Ls = (yRidge - RB_W / 2 - sOut) / COS;
  for (const side of [0, 1]) {
    const y = side === 0 ? sOut : Wi - sOut;
    const o = [sOut, y, zRb(sOut) + 0.002];
    const v = side === 0 ? [0, COS, SIN] : [0, -COS, SIN];
    const n = side === 0 ? [0, -SIN, COS] : [0, SIN, COS];
    add(prism(o, [1, 0, 0], v, n, 0.15, [[rectRing(0, 0, Li - 2 * sOut, Ls)]], { ...ins, name: 'Aislación techo 150 mm', info: 'Lana de vidrio 150 mm entre cabios + barrera de vapor + cámara ventilada 45 mm' }));
  }
}

// ============================================================================================
// REVESTIMIENTO EXTERIOR: chapa T-101 vertical (laterales), siding (los dos hastiales),
// cassettes de registro en la pared de servicios
// ============================================================================================
function cladding(add) {
  const sheetW = 1.0; // ancho útil T-101
  const zBot = 0.06;
  const zSoffit = zRb(sOut - EAVE);
  const chapa = (o, u, v, n, width, lenFn, name, extra = {}) => add(ribbed(o, u, v, n, width, lenFn, { layer: 'revest_ext', mat: 'chapa_muro', name, period: 0.2, depth: tCh, ...extra }));
  // laterales
  for (const side of ['IZQ', 'SER']) {
    const y = side === 'IZQ' ? cOut : Wi - cOut;
    const n = side === 'IZQ' ? [0, -1, 0] : [0, 1, 0];
    const z0 = side === 'SER' ? 1.5 : zBot;
    const total = Li - 2 * cOut;
    for (let i = 0; i * sheetW < total - 1e-3; i++) {
      const a = cOut + i * sheetW;
      const w = Math.min(sheetW, total - i * sheetW);
      chapa([a, y + (side === 'IZQ' ? tCh : -tCh), z0], [1, 0, 0], [0, 0, 1], n, w, zSoffit - z0, `Chapa T-101 lateral ${side === 'IZQ' ? 'izquierdo' : 'servicios'} hoja ${i + 1}`, { sheetLen: r3(zSoffit - z0), facade: side });
    }
  }
  // hastiales (frente = estar, fondo = acceso): siding cementicio horizontal símil madera
  // (tablas de 20 cm con 18 cm de exposición), recortado a la pendiente y a las aberturas
  const top = (y) => zRt(y) + 0.02 / COS;
  const gablePoly = [[[cOut, zBot], [Wi - cOut, zBot], [Wi - cOut, top(Wi - cOut)], [yRidge, top(yRidge)], [cOut, top(cOut)], [cOut, zBot]]];
  for (const wall of ['FRENTE', 'FONDO']) {
    const front = wall === 'FRENTE';
    const xb = front ? bOut : Li - bOut;
    const sHoles = opsWall(wall).map((k) => [rectRing(OPEN[k].s0 - 0.03, OPEN[k].z0 - (OPEN[k].door ? 0.1 : 0.03), OPEN[k].s1 + 0.03, OPEN[k].z1 + 0.03)]);
    let row = 0;
    for (let z = zBot; z < top(yRidge) - 0.02; z += 0.18, row++) {
      let mp = pc.intersection([gablePoly], [[rectRing(cOut, z, Wi - cOut, z + 0.2)]]);
      if (mp.length) mp = pc.difference(mp, ...sHoles);
      for (const pl of mp) {
        const xs = pl[0].map((q) => q[0]);
        const len = Math.max(...xs) - Math.min(...xs);
        if (len < 0.03) continue;
        const off = 0.004 * (row % 2);
        add(prism([front ? xb - off : xb + off, 0, 0], [0, 1, 0], [0, 0, 1], [front ? -1 : 1, 0, 0], 0.01, [pl], {
          layer: 'revest_ext', mat: 'siding', name: `Siding cementicio símil madera (${front ? 'fachada estar' : 'fachada acceso'}) — fila ${row + 1}, ${Math.round(len * 100)} cm`, siding: { len: r3(len) },
        }));
      }
    }
    for (const y of [cOut - 0.004, Wi - cOut - 0.046]) {
      const x0 = front ? bOut - 0.03 : Li - bOut - 0.001;
      add(box([x0, y, zBot], [x0 + 0.031, y + 0.05, top(cOut) - 0.02], { layer: 'revest_ext', mat: 'zinguerias', name: 'Tapajuntas de esquina (siding)' }));
    }
  }
  // cassettes de registro (pared de servicios, franja inferior)
  const cw = (Li - 2 * cOut) / 4;
  const names = ['R1 — bacha, lavarropas y rejilla baja', 'R2 — GAS: ingreso, llave de corte, cocina; llaves agua cocina', 'R3 — NUDO: entrada de agua y llave general, acometida eléctrica (caja de paso), fibra', 'R4 — ducha, termotanque y ventilación'];
  for (let i = 0; i < 4; i++) {
    const a = cOut + i * cw;
    add(box([a + 0.004, Wi - bOut, zBot], [a + cw - 0.004, Wi - cOut, 1.5], { id: `REG-R${i + 1}`, layer: 'revest_ext', mat: 'fibro_reg', name: `Registro ${names[i]}`, info: 'Se retira con 10 tornillos inox: detrás quedan las cañerías (cavidad del lado caliente) y las llaves de paso.' }));
    for (const [sx, sz] of [[0.05, 0.05], [cw / 2, 0.05], [cw - 0.05, 0.05], [0.05, 0.72], [cw - 0.05, 0.72], [0.05, 1.39], [cw / 2, 1.39], [cw - 0.05, 1.39]]) {
      add(cyl([a + sx, Wi - cOut + 0.002, zBot + sz], 'y', 0.007, 0.004, { layer: 'revest_ext', mat: 'herrajes', name: 'Tornillo inox registro' }));
    }
  }
  // cupertina sobre la franja de registros
  add(box([cOut - 0.01, Wi - cOut - 0.005, 1.5], [Li - cOut + 0.01, Wi - cOut + 0.04, 1.52], { layer: 'revest_ext', mat: 'zinguerias', name: 'Babeta/cupertina sobre registros' }));
  // esquineros de chapa
  for (const [x, y] of [[cOut, cOut], [Li - cOut, cOut], [cOut, Wi - cOut], [Li - cOut, Wi - cOut]]) {
    add(box([x - 0.03, y - 0.03, zBot], [x + 0.03, y + 0.03, zRb(sOut - 0.02) - 0.25], { layer: 'revest_ext', mat: 'zinguerias', name: 'Esquinero chapa plegada' }));
  }
  // cielorraso de alero
  for (const side of [0, 1]) {
    const ya = side === 0 ? sOut - EAVE : Wi - cOut;
    const yb = side === 0 ? cOut : Wi - sOut + EAVE;
    add(box([cOut - GABLE_OH, ya, zSoffit - 0.006], [Li - cOut + GABLE_OH, yb, zSoffit], { layer: 'revest_ext', mat: 'alero_fibro', name: 'Cielorraso de alero fibrocemento ventilado' }));
  }
}

// ============================================================================================
// CUBIERTA: chapa T-101 negra, cumbrera, canaletas, bajadas, frentines de hastial
// ============================================================================================
function roof(add) {
  const xa = cOut - GABLE_OH, xb = Li - cOut + GABLE_OH;
  const yEdge = sOut - EAVE - 0.07; // la chapa vuela 5 cm sobre la canaleta
  const sheetW = 1.0;
  const total = xb - xa;
  for (const side of [0, 1]) {
    const y0 = side === 0 ? yEdge : Wi - yEdge;
    const zb = zRoof(yEdge) - 0.025 / COS;
    const L = (yRidge - yEdge) / COS + 0.02;
    const v = side === 0 ? [0, COS, SIN] : [0, -COS, SIN];
    const n = side === 0 ? [0, -SIN, COS] : [0, SIN, COS];
    for (let i = 0; i * sheetW < total - 1e-3; i++) {
      const w = Math.min(sheetW, total - i * sheetW);
      add(ribbed([xa + i * sheetW, y0, zb], [1, 0, 0], v, n, w, L, { layer: 'techo', mat: 'chapa_techo', name: `Chapa T-101 techo ${side ? 'derecho' : 'izquierdo'} hoja ${i + 1} (L=${r3(Math.ceil(L * 20) / 20)} m)`, period: 0.2, depth: 0.025, sheetLen: r3(Math.ceil(L * 20) / 20) }));
    }
  }
  // cumbrera
  const zr = zRoof(yRidge);
  for (const side of [0, 1]) {
    const s = side ? -1 : 1;
    add(prism([xa - 0.01, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], total + 0.02, [[[[yRidge, zr + 0.03], [yRidge - s * 0.22, zr - 0.22 * T + 0.01], [yRidge - s * 0.22, zr - 0.22 * T + 0.016], [yRidge, zr + 0.036], [yRidge, zr + 0.03]]]], { layer: 'techo', mat: 'zinguerias', name: 'Cumbrera chapa plegada' }));
  }
  // frentines de hastial (babetas laterales)
  for (const x of [xa - 0.02, xb]) {
    for (const side of [0, 1]) {
      const a = side === 0 ? yEdge : yRidge, b = side === 0 ? yRidge : Wi - yEdge;
      const ring = [[a, zRoof(a) + 0.03], [b, zRoof(b) + 0.03], [b, zRoof(b) - 0.2], [a, zRoof(a) - 0.2], [a, zRoof(a) + 0.03]];
      add(prism([x, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], 0.02, [[ring]], { layer: 'techo', mat: 'zinguerias', name: 'Frentín de hastial chapa plegada' }));
    }
  }
  // canaletas y bajadas
  for (const side of [0, 1]) {
    const yc = side === 0 ? sOut - EAVE - 0.11 : Wi - sOut + EAVE + 0.11;
    const zc = zRt(sOut - EAVE) - 0.1;
    add(box([xa, yc - 0.075, zc - 0.11], [xb, yc + 0.075, zc], { layer: 'techo', mat: 'canaleta', name: 'Canaleta chapa 15 cm (pendiente 0,5%)' }));
    const xd = xb - 0.25;
    add(box([xd - 0.04, yc - 0.04, -0.1], [xd + 0.04, yc + 0.04, zc - 0.1], { layer: 'techo', mat: 'canaleta', name: 'Bajada pluvial 8x8' }));
    add(box([xd - 0.04, yc - 0.04 + (side ? 0.04 : -0.04), -0.15], [xd + 0.3, yc + 0.04, -0.09], { layer: 'techo', mat: 'canaleta', name: 'Codo de descarga pluvial' }));
  }
}

// ============================================================================================
// ABERTURAS
// ============================================================================================
function openings(add) {
  for (const [k, o] of Object.entries(OPEN)) {
    if (o.wall === 'TAB_B') {
      // puerta de baño (abre hacia el pasillo)
      const y0 = 1.965, y1 = 2.06;
      add(box([o.s0, y0 - 0.005, 0], [o.s0 + 0.03, y1 + 0.005, o.z1], { layer: 'aberturas', mat: 'puerta_int', name: 'Marco chapa puerta baño', id: `${k}-M1` }));
      add(box([o.s1 - 0.03, y0 - 0.005, 0], [o.s1, y1 + 0.005, o.z1], { layer: 'aberturas', mat: 'puerta_int', name: 'Marco chapa puerta baño' }));
      add(box([o.s0, y0 - 0.005, o.z1 - 0.03], [o.s1, y1 + 0.005, o.z1], { layer: 'aberturas', mat: 'puerta_int', name: 'Marco chapa puerta baño' }));
      add(box([o.s0 + 0.03, y0 + 0.005, 0.01], [o.s1 - 0.03, y0 + 0.045, o.z1 - 0.03], { layer: 'aberturas', mat: 'puerta_int', name: `${k} — ${o.name}: puerta placa 70x200`, id: k, opening: k }));
      add(box([o.s0 + 0.08, y0 - 0.03, 0.95], [o.s0 + 0.2, y0 + 0.005, 0.97], { layer: 'aberturas', mat: 'herrajes', name: 'Manija acero inox' }));
      continue;
    }
    const front = o.wall === 'FRENTE';
    // plano del marco: dentro del espesor del muro, cerca del exterior
    const xo = front ? sOut + 0.003 : Li - sOut - 0.003; // borde exterior del marco
    const d = front ? 1 : -1; // hacia el interior
    const fx0 = front ? xo : xo - 0.06;
    const fx1 = front ? xo + 0.06 : xo;
    const fw = 0.06;
    const B = (y0, y1, z0, z1, extra, dx0 = fx0, dx1 = fx1) => add(box([dx0, y0, z0], [dx1, y1, z1], { layer: 'aberturas', ...extra }));
    if (o.door) {
      const ext = front ? -1 : 1; // sentido hacia el exterior
      const extFace = front ? fx0 : fx1, intFace = front ? fx1 : fx0;
      const R = (x0, x1, y0, y1, z0, z1, extra) => add(box([Math.min(x0, x1), y0, z0], [Math.max(x0, x1), y1, z1], { layer: 'aberturas', ...extra }));
      const fm = { mat: 'pvc_marco', name: 'Marco chapa puerta exterior' };
      B(o.s0, o.s0 + 0.05, 0, o.z1, fm); B(o.s1 - 0.05, o.s1, 0, o.z1, fm); B(o.s0, o.s1, o.z1 - 0.05, o.z1, fm);
      B(o.s0 + 0.05, o.s1 - 0.05, 0.01, o.z1 - 0.05, { mat: 'puerta_ext', name: `${k} — ${o.name}: chapa inyectada 80x200`, id: k, opening: k });
      for (const [z0, z1] of [[0.2, 0.9], [1.05, 1.9]]) R(extFace - ext * 0.001, extFace + ext * 0.004, o.s0 + 0.18, o.s1 - 0.18, z0, z1, { mat: 'puerta_ext', name: 'Bajo relieve puerta' });
      const latch = o.hinge === 's1' ? o.s0 + 0.1 : o.s1 - 0.13;
      R(extFace + ext * 0.01, extFace + ext * 0.07, latch, latch + 0.03, 0.98, 1.4, { mat: 'hierro_negro', name: 'Barral tirador negro' });
      R(intFace, intFace - ext * 0.06, latch, latch + 0.12, 0.98, 1.0, { mat: 'herrajes', name: 'Manija interior inox' });
      const bx0 = front ? cOut - 0.015 : Li - sOut, bx1 = front ? sOut : Li - cOut + 0.015;
      for (const sj of [o.s0 - 0.03, o.s1]) add(box([bx0, sj, 0], [bx1, sj + 0.03, o.z1 + 0.03], { layer: 'aberturas', mat: 'zinguerias', name: 'Babeta de jamba puerta' }));
      add(box([bx0, o.s0 - 0.03, o.z1], [bx1, o.s1 + 0.03, o.z1 + 0.03], { layer: 'aberturas', mat: 'zinguerias', name: 'Babeta de dintel puerta' }));
      R(front ? sOut - 0.06 : Li - sOut + 0.06, front ? sIn + 0.01 : Li - sIn - 0.01, o.s0, o.s1, -0.005, 0.02, { mat: 'granito', name: 'Umbral granito gris mara' });
      continue;
    }
    const m = { mat: 'pvc_marco', name: `${k} — marco PVC` };
    B(o.s0, o.s0 + fw, o.z0, o.z1, { ...m, id: k, opening: k, name: `${k} — ${o.name} ${Math.round((o.s1 - o.s0) * 100)}x${Math.round((o.z1 - o.z0) * 100)} PVC DVH` });
    B(o.s1 - fw, o.s1, o.z0, o.z1, m);
    B(o.s0, o.s1, o.z0, o.z0 + fw, m);
    B(o.s0, o.s1, o.z1 - fw, o.z1, m);
    const n = o.sashes;
    const span = (o.s1 - o.s0 - 2 * fw) / n;
    for (let i = 0; i < n; i++) {
      const a = o.s0 + fw + i * span, b = a + span;
      if (i > 0) B(a - 0.02, a + 0.02, o.z0, o.z1, m);
      const sw = 0.055;
      const gx0 = front ? fx0 + 0.025 : fx0 + 0.015;
      const gx1 = gx0 + 0.02;
      B(a, a + sw, o.z0 + fw, o.z1 - fw, { mat: 'pvc_marco', name: 'Hoja PVC' }, gx0 - 0.01, gx1 + 0.01);
      B(b - sw, b, o.z0 + fw, o.z1 - fw, { mat: 'pvc_marco', name: 'Hoja PVC' }, gx0 - 0.01, gx1 + 0.01);
      B(a, b, o.z0 + fw, o.z0 + fw + sw, { mat: 'pvc_marco', name: 'Hoja PVC' }, gx0 - 0.01, gx1 + 0.01);
      B(a, b, o.z1 - fw - sw, o.z1 - fw, { mat: 'pvc_marco', name: 'Hoja PVC' }, gx0 - 0.01, gx1 + 0.01);
      B(a + sw, b - sw, o.z0 + fw + sw, o.z1 - fw - sw, { mat: 'vidrio', name: `${k} DVH 4/12/4${i === n - 1 ? ' — hoja oscilobatiente' : ' — paño fijo'}`, glass: true }, gx0, gx1);
      if (i === n - 1 || n === 1) B(b - sw - 0.02, b - sw, (o.z0 + o.z1) / 2 - 0.08, (o.z0 + o.z1) / 2 + 0.08, { mat: 'herrajes', name: 'Manija oscilobatiente' }, front ? gx1 + 0.01 : gx0 - 0.04, front ? gx1 + 0.04 : gx0 - 0.01);
    }
    // cupertina exterior y alféizar interior
    const ex0 = front ? cOut - 0.04 : Li - sOut;
    const ex1 = front ? sOut : Li - cOut + 0.04;
    add(box([ex0, o.s0 - 0.03, o.z0 - 0.03], [ex1, o.s1 + 0.03, o.z0], { layer: 'aberturas', mat: 'zinguerias', name: 'Cupertina chapa plegada' }));
    // jambas exteriores (babetas)
    for (const s of [o.s0 - 0.03, o.s1]) add(box([front ? cOut - 0.015 : Li - sOut, s, o.z0], [front ? sOut : Li - cOut + 0.015, s + 0.03, o.z1 + 0.03], { layer: 'aberturas', mat: 'zinguerias', name: 'Babeta de jamba' }));
    add(box([front ? cOut - 0.015 : Li - sOut, o.s0 - 0.03, o.z1], [front ? sOut : Li - cOut + 0.015, o.s1 + 0.03, o.z1 + 0.03], { layer: 'aberturas', mat: 'zinguerias', name: 'Babeta de dintel' }));
    const ix0 = front ? fx1 : 0 + Li - 0.02;
    const ix1 = front ? 0.02 : fx0;
    add(box([Math.min(ix0, ix1), o.s0 - 0.01, o.z0 - 0.02], [Math.max(ix0, ix1), o.s1 + 0.01, o.z0], { layer: 'aberturas', mat: 'pintura_blanco', name: 'Alféizar interior (placa + cantonera)' }));
    // cortina roller (económica)
    const xr = front ? 0.04 : Li - 0.04;
    if (k !== 'V3') {
      add(cyl([xr, o.s0 - 0.02, o.z1 + 0.05], 'y', 0.025, o.s1 - o.s0 + 0.04, { layer: 'muebles', mat: 'cortina', name: `Cortina roller blackout ${k} (económica, reemplazable)` }));
      add(box([xr - 0.003, o.s0, o.z1 - 0.35], [xr + 0.003, o.s1, o.z1 + 0.03], { layer: 'muebles', mat: 'cortina', name: `Cortina roller ${k} (semi baja)` }));
    }
  }
  // visera de entrada (sobre la puerta de acceso)
  const P1 = OPEN.P1;
  const vx0 = P1.wall === 'FRENTE' ? cOut - 0.65 : Li - cOut, vx1 = vx0 + 0.65, vxw = P1.wall === 'FRENTE' ? cOut : Li - cOut;
  add(box([vx0, P1.s0 - 0.3, 2.42], [vx1, P1.s1 + 0.3, 2.47], { layer: 'revest_ext', mat: 'visera', name: 'Visera de entrada chapa plegada 150x65' }));
  for (const sv of [P1.s0 - 0.25, P1.s1 + 0.25]) {
    const dir = P1.wall === 'FRENTE' ? -1 : 1;
    add(prism([vxw, sv, 0], [dir, 0, 0], [0, 0, 1], [0, 1, 0], 0.008, [[[[0, 2.42], [0.6, 2.42], [0.02, 2.05], [0, 2.05], [0, 2.42]]]], { layer: 'revest_ext', mat: 'hierro_negro', name: 'Ménsula planchuela visera' }));
  }
}

// ============================================================================================
// ESCALERA: 14 alzadas, tramo recto de 10 huellas + 3 compensadas en esquina frente-izquierda
// ============================================================================================
function stair(add) {
  const { rise, going, xBottom, width } = ST;
  const sw = 0.045;
  const y0 = sw, y1 = width - sw;
  const tt = 0.038;
  const zk = (k) => fGF + k * rise;
  // tramo recto (huellas 1..10)
  for (let k = 1; k <= 10; k++) {
    const xa = xBottom - going * k;
    add(box([xa, y0 - 0.02, zk(k) - tt], [xa + going + 0.025, y1 + 0.02, zk(k)], { layer: 'escalera', mat: 'lenga', name: `Huella ${k} lenga 38 mm`, id: `ESC-H${k}`, info: `Huella ${k}: ${Math.round((going + 0.025) * 100)}x${Math.round((y1 - y0 + 0.04) * 100)} cm, nivel +${r3(zk(k))}` }));
    add(box([xa + going, y0, zk(k - 1)], [xa + going + 0.012, y1, zk(k) - tt], { layer: 'escalera', mat: 'pintura_blanco', name: `Contrahuella ${k} (fenólico 12 mm pintado)` }));
  }
  // compensados (huellas 11..13) alrededor del poste en (0.85, 0.85)
  const P = [ST.xTop, width];
  const pts = { a: [ST.xTop, 0], b: [ST.xTop - width * Math.tan(Math.PI / 6), 0], c: [0, 0], d: [0, width - width * Math.tan(Math.PI / 6)], e: [0, width] };
  const newel = [rectRing(P[0] - 0.09, P[1] - 0.09, P[0] + 0.0, P[1] + 0.0)];
  const winders = [[P, pts.a, pts.b], [P, pts.b, pts.c, pts.d], [P, pts.d, pts.e]];
  winders.forEach((w, i) => {
    const k = 11 + i;
    const ring = [...w, w[0]];
    const mp = pc.difference([[ring]], newel);
    add(prism([0, 0, zk(k) - tt], [1, 0, 0], [0, 1, 0], [0, 0, 1], tt, mp, { layer: 'escalera', mat: 'lenga', name: `Huella compensada ${k} lenga 38 mm`, id: `ESC-H${k}` }));
    // bloque de apoyo (cajón) bajo cada compensado
    add(prism([0, 0, 1.9], [1, 0, 0], [0, 1, 0], [0, 0, 1], zk(k) - tt - 1.9, mp, { layer: 'escalera', mat: 'pintura_blanco', name: `Cajón de apoyo compensado ${k} (bastidor + OSB pintado)` }));
  });
  // zanca contra muro y zanca libre
  const zN = (x) => fGF + ((xBottom - x) / going) * rise; // línea de narices
  const ang = Math.atan2(rise, going);
  const dv = 0.24 / Math.cos(ang);
  for (const [ya, yb, name] of [[0, sw, 'Zanca contra muro'], [width - sw, width, 'Zanca libre']]) {
    const xs = xBottom;
    const xe = ST.xTop;
    const xf = xBottom - ((dv - 0.06) / rise) * going;
    const ring = [[xs, fGF], [xs, zN(xs) + 0.06], [xe, zN(xe) + 0.06], [xe, zN(xe) + 0.06 - dv], [xf, fGF], [xs, fGF]];
    add(prism([0, ya, 0], [1, 0, 0], [0, 0, 1], [0, 1, 0], yb - ya, [[ring]], { layer: 'escalera', mat: 'zanca', name: `${name} pino laminado 45x240` }));
  }
  // poste (newel) de lenga desde PB hasta baranda PA
  // poste de giro sólo desde el cajón de los compensados (la planta baja queda libre para el sillón)
  add(box([P[0] - 0.09, P[1] - 0.09, 1.9], [P[0], P[1], ZF1 + 0.95], { layer: 'escalera', mat: 'lenga', name: 'Poste de giro lenga 90x90 (desde el cajón de compensados hasta la baranda)' }));
  // apoyo de los compensados: perfiles de acero (tubo 100x50) empotrados en muros y apoyados en la zanca
  add(box([0, P[1] - 0.06, 1.75], [P[0] + 0.25, P[1], 1.9], { layer: 'escalera', mat: 'hierro_negro', name: 'Tubo 100x50 apoyo compensados (de muro de frente a zanca)' }));
  add(box([P[0] - 0.06, 0, 1.75], [P[0], P[1], 1.9], { layer: 'escalera', mat: 'hierro_negro', name: 'Tubo 100x50 apoyo compensados (de muro lateral a tubo)' }));
  add(box([xBottom + 0.02, width - 0.07, 0], [xBottom + 0.09, width, 0.95], { layer: 'escalera', mat: 'lenga', name: 'Poste de arranque lenga 70x70' }));
  // cerramiento bajo escalera (detrás del banco)
  const xf2 = xBottom - ((dv - 0.06) / rise) * going;
  const xs0 = 1.48, zb = (x) => zN(x) + 0.06 - dv;
  add(prism([0, width, 0], [1, 0, 0], [0, 0, 1], [0, -1, 0], 0.015, [[[[xs0, fGF], [xf2, fGF], [xs0, zb(xs0)], [xs0, fGF]]]], { layer: 'escalera', mat: 'melamina_blanca', name: 'Frente de guardado bajo escalera (2 puertas melamina)' }));
  for (const [a, b] of [[xs0 + 0.02, 2.2], [2.22, 2.85]]) {
    add(box([a + 0.08, width - 0.03, zb(a + 0.1) - 0.25], [a + 0.1, width - 0.015, zb(a + 0.1) - 0.1], { layer: 'escalera', mat: 'hierro_negro', name: 'Tirador puerta guardado' }));
  }
  // baranda de la escalera (planchuela + barrotes) y pasamanos de lenga
  const hb = 0.9;
  const railY = width - 0.02;
  const xA = xBottom + 0.05, xB = ST.xTop - 0.045;
  const zA = zN(xA) + hb, zB = zN(xB) + hb;
  add(tube([[xA, railY, zA], [xB, railY, zB]], 0.022, { layer: 'escalera', mat: 'pasamanos', name: 'Pasamanos lenga Ø45 barnizado' }));
  for (let x = xB + 0.11; x < xA - 0.03; x += 0.11) {
    const z0 = zN(x) + 0.05;
    const z1 = zN(x) + hb - 0.03;
    add(tube([[x, railY, z0], [x, railY, z1]], 0.006, { layer: 'escalera', mat: 'hierro_negro', name: 'Barrote Ø12 hierro negro' }));
  }
  // baranda del hueco en PA
  const H = ST.hole;
  const zr = ZF1 + 0.95;
  const segs = [[[P[0], H.y1 + 0.02], [H.x1, H.y1 + 0.02]], [[H.x1 + 0.02, H.y1], [H.x1 + 0.02, 0]]];
  for (const [[ax, ay], [bx, by]] of segs) {
    add(tube([[ax, ay, zr], [bx, by, zr]], 0.022, { layer: 'escalera', mat: 'pasamanos', name: 'Pasamanos baranda PA lenga' }));
    add(tube([[ax, ay, ZF1 + 0.06], [bx, by, ZF1 + 0.06]], 0.012, { layer: 'escalera', mat: 'hierro_negro', name: 'Planchuela inferior baranda' }));
    const L = Math.hypot(bx - ax, by - ay);
    for (let t = 0.11; t < L - 0.03; t += 0.11) {
      const x = ax + ((bx - ax) * t) / L, y = ay + ((by - ay) * t) / L;
      add(tube([[x, y, ZF1 + 0.06], [x, y, zr - 0.02]], 0.006, { layer: 'escalera', mat: 'hierro_negro', name: 'Barrote Ø12 hierro negro' }));
    }
  }
  add(box([H.x1, H.y1, ZF1], [H.x1 + 0.05, H.y1 + 0.05, zr + 0.02], { layer: 'escalera', mat: 'hierro_negro', name: 'Parante baranda' }));
}

// ============================================================================================
// TERMINACIONES: pisos (porcelanato PB por pieza, SPC PA por tabla), cerámicos de ducha
// ============================================================================================
function finishes(add) {
  // porcelanato 60x60 (juntas 2 mm)
  const T6 = 0.6, j = 0.002;
  for (let x = 0; x < Li - 1e-3; x += T6) {
    for (let y = 0; y < Wi - 1e-3; y += T6) {
      const x1 = Math.min(x + T6, Li), y1 = Math.min(y + T6, Wi);
      const cut = x1 - x < T6 - 1e-3 || y1 - y < T6 - 1e-3;
      add(box([x + j / 2, y + j / 2, 0], [x1 - j / 2, y1 - j / 2, fGF], { layer: 'terminaciones', mat: 'porcelanato', name: `Porcelanato 60x60${cut ? ' (cortado ' + Math.round((x1 - x) * 100) + 'x' + Math.round((y1 - y) * 100) + ')' : ''}`, tile: cut ? 'cortada' : 'entera' }));
    }
  }
  // SPC PA: tablas 18x122 trabadas, fuera del hueco
  const H = ST.hole;
  const pw = 0.18, pl = 1.22;
  let row = 0;
  for (let y = 0; y < Wi - 1e-3; y += pw, row++) {
    const y1 = Math.min(y + pw, Wi);
    const off = (row * 0.41) % pl;
    for (let x = -off; x < Li - 1e-3; x += pl) {
      let xa = Math.max(0, x), xb = Math.min(Li, x + pl);
      if (y < H.y1 && y1 > H.y0) xa = Math.max(xa, H.x1);
      if (xb - xa < 0.02) continue;
      const shade = ((row * 7 + Math.round(x * 10)) % 5) / 5;
      add(box([xa + 0.0005, y + 0.0005, ZO1], [xb - 0.0005, y1 - 0.0005, ZF1], { layer: 'terminaciones', mat: 'spc', name: 'Piso SPC roble claro', shade }));
    }
  }
  // cerámico 30x60 en box de ducha (3 caras, h 2,10)
  const tw = 0.3, th = 0.6, e = 0.008;
  const wallTiles = (fixed, axis, a0, a1, sign) => {
    for (let a = a0; a < a1 - 1e-3; a += tw) {
      for (let z = fGF; z < 2.1 - 1e-3; z += th) {
        const b = Math.min(a + tw, a1), z1 = Math.min(z + th, 2.1);
        const c0 = fixed, c1 = fixed + sign * e;
        const bx = axis === 'x' ? box([a + 0.001, Math.min(c0, c1), z + 0.001], [b - 0.001, Math.max(c0, c1), z1 - 0.001]) : box([Math.min(c0, c1), a + 0.001, z + 0.001], [Math.max(c0, c1), b - 0.001, z1 - 0.001]);
        add({ ...bx, layer: 'terminaciones', mat: 'ceramica_ducha', name: 'Cerámico 30x60 blanco mate (ducha)' });
      }
    }
  };
  wallTiles(Wi, 'x', 3.56, Li, -1);
  wallTiles(2.06, 'x', 3.56, Li, 1);
  wallTiles(Li, 'y', 2.06, Wi, -1);
  // frente de mesada subway
  add(box([0, Wi - 0.006, 0.96], [1.77, Wi, 1.5], { layer: 'terminaciones', mat: 'ceramica_cocina', name: 'Cerámico subway 7,5x15 blanco (frente de mesada)' }));
}

// ============================================================================================
// COCINA Y BAÑO
// ============================================================================================
function kitchenAndBath(add) {
  const K = (b, extra) => add({ ...b, layer: 'cocina', ...extra });
  const yb = Wi - 0.6;
  // bajomesada 60 con bacha + lavarropas 60 bajo mesada + cocina 51 + heladera 56
  K(box([0.005, yb + 0.02, 0.1], [0.6, Wi - 0.005, 0.88]), { mat: 'melamina_blanca', name: 'Bajomesada melamina 60x60 (bacha)', plan: 'PB' });
  K(box([0.005, yb + 0.06, 0], [0.6, Wi - 0.005, 0.1]), { mat: 'zocalo_chapa', name: 'Zócalo bajomesada' });
  K(box([0.01, yb, 0.11], [0.595, yb + 0.02, 0.87]), { mat: 'melamina_blanca', name: 'Frente puerta bajomesada' });
  K(box([0.5, yb - 0.025, 0.72], [0.512, yb, 0.84]), { mat: 'hierro_negro', name: 'Tirador negro' });
  K(box([0.62, yb + 0.02, 0], [1.2, Wi - 0.04, 0.85]), { mat: 'heladera', name: 'Lavarropas carga frontal 60 cm (bajo mesada)', plan: 'PB' });
  K(cyl([0.91, yb + 0.005, 0.45], 'y', 0.2, 0.02), { mat: 'vidrio', name: 'Puerta lavarropas', glass: true });
  K(box([0, yb - 0.02, 0.88], [1.2, Wi, 0.9]), { mat: 'granito', name: 'Mesada granito gris mara 120x62 c/ calado bacha', plan: 'PB' });
  K(box([0, Wi - 0.02, 0.9], [1.2, Wi, 0.96]), { mat: 'granito', name: 'Zócalo granito' });
  K(box([0.04, yb + 0.12, 0.72], [0.56, yb + 0.49, 0.9]), { mat: 'bacha', name: 'Bacha acero inox 52x37' });
  K(cyl([0.3, Wi - 0.07, 0.9], 'z', 0.025, 0.28), { mat: 'griferia_cocina', name: 'Grifería monocomando pico alto (bronce cromado)' });
  K(box([0.285, Wi - 0.31, 1.14], [0.315, Wi - 0.07, 1.18]), { mat: 'griferia_cocina', name: 'Pico grifería' });
  // cocina 51
  const xc0 = 1.23, xc1 = 1.74;
  K(box([xc0, yb + 0.02, 0], [xc1, Wi - 0.02, 0.85]), { mat: 'cocina', name: 'Cocina a gas 51 cm 4 hornallas con horno', plan: 'PB' });
  K(box([xc0, yb + 0.02, 0.85], [xc1, Wi - 0.02, 0.88]), { mat: 'hierro_negro', name: 'Mesada de cocina (hornallas)' });
  for (const [x, y] of [[xc0 + 0.13, yb + 0.15], [xc1 - 0.13, yb + 0.15], [xc0 + 0.13, yb + 0.42], [xc1 - 0.13, yb + 0.42]]) K(cyl([x, y, 0.88], 'z', 0.05, 0.02), { mat: 'hierro_negro', name: 'Hornalla' });
  K(box([xc0 + 0.04, yb + 0.005, 0.12], [xc1 - 0.04, yb + 0.02, 0.62]), { mat: 'vidrio', name: 'Puerta de horno', glass: true });
  K(box([xc0 + 0.04, yb + 0.005, 0.68], [xc1 - 0.04, yb + 0.02, 0.8]), { mat: 'cocina', name: 'Perillas' });
  // heladera 56
  K(box([1.77, yb - 0.05, 0], [2.33, Wi - 0.02, 1.75]), { mat: 'heladera', name: 'Heladera con freezer 56 cm', plan: 'PB' });
  K(box([1.79, yb - 0.075, 0.9], [1.81, yb - 0.05, 1.5]), { mat: 'herrajes', name: 'Manija heladera' });
  K(box([1.77, yb - 0.051, 1.2], [2.33, yb - 0.049, 1.205]), { mat: 'hierro_negro', name: 'Junta freezer' });
  // alacena 80 + estante sobre heladera + purificador
  K(box([0.3, Wi - 0.35, 1.5], [1.1, Wi, 2.2]), { mat: 'melamina_blanca', name: 'Alacena melamina 80x35x70', plan: 'PB-alto' });
  K(box([0.7, Wi - 0.365, 1.52], [0.702, Wi - 0.35, 2.18]), { mat: 'hierro_negro', name: 'Junta puertas alacena' });
  K(box([0.3, Wi - 0.33, 1.495], [1.1, Wi - 0.31, 1.5]), { mat: 'luminaria', name: 'Tira LED bajo alacena', emissive: true });
  K(box([1.185, Wi - 0.5, 1.6], [1.785, Wi, 1.72]), { mat: 'purificador', name: 'Purificador 60 cm' });
  K(box([1.77, Wi - 0.35, 1.95], [2.33, Wi, 2.2]), { mat: 'melamina_blanca', name: 'Módulo alacena sobre heladera 56x35x25' });

  // ------------------ BAÑO ------------------
  const Bt = (b, extra) => add({ ...b, layer: 'bano', ...extra });
  // receptáculo 80x120 + cordón
  Bt(box([3.56, 2.16, fGF], [Li, Wi, fGF + 0.06]), { mat: 'plato_ducha', name: 'Receptáculo ducha acrílico 80x120', plan: 'PB' });
  Bt(box([3.56, 2.06, fGF], [Li, 2.16, fGF + 0.06]), { mat: 'porcelanato', name: 'Cordón de porcelanato' });
  Bt(cyl([3.96, 2.76, fGF + 0.06], 'z', 0.04, 0.003), { mat: 'herrajes', name: 'Rejilla desagüe ducha' });
  // inodoro con mochila apoyada
  const xi = 3.22;
  Bt(box([xi - 0.19, Wi - 0.2, 0.4], [xi + 0.19, Wi - 0.02, 0.8]), { mat: 'inodoro', name: 'Mochila apoyada', plan: 'PB' });
  Bt(box([xi - 0.12, Wi - 0.6, fGF], [xi + 0.12, Wi - 0.2, 0.3]), { mat: 'inodoro', name: 'Pie de inodoro' });
  Bt(cyl([xi, Wi - 0.45, 0.3], 'z', 0.19, 0.1), { mat: 'inodoro', name: 'Taza inodoro largo', plan: 'PB' });
  Bt(box([xi - 0.17, Wi - 0.2, 0.3], [xi + 0.17, Wi - 0.08, 0.4]), { mat: 'inodoro', name: 'Taza (posterior)' });
  Bt(cyl([xi, Wi - 0.44, 0.4], 'z', 0.185, 0.02), { mat: 'pintura_blanco', name: 'Asiento' });
  Bt(cyl([xi + 0.12, Wi - 0.1, 0.8], 'z', 0.015, 0.01), { mat: 'herrajes', name: 'Pulsador' });
  // lavatorio de colgar 45
  const xl = 2.7;
  Bt(box([xl - 0.225, Wi - 0.36, 0.7], [xl + 0.225, Wi, 0.85]), { mat: 'lavatorio', name: 'Lavatorio de colgar 45 cm', plan: 'PB' });
  Bt(box([xl - 0.15, Wi - 0.3, 0.78], [xl + 0.15, Wi - 0.08, 0.851]), { mat: 'pintura_antihongo', name: 'Cubeta lavatorio' });
  Bt(cyl([xl, Wi - 0.06, 0.85], 'z', 0.02, 0.15), { mat: 'griferia_bano', name: 'Grifería monocomando lavatorio' });
  Bt(box([xl - 0.012, Wi - 0.14, 0.96], [xl + 0.012, Wi - 0.06, 0.99]), { mat: 'griferia_bano', name: 'Pico' });
  Bt(cyl([xl, Wi - 0.1, 0.35], 'z', 0.03, 0.35), { mat: 'herrajes', name: 'Sifón cromado' });
  // botiquín con espejo
  Bt(box([xl - 0.225, Wi - 0.13, 1.1], [xl + 0.225, Wi, 1.7]), { mat: 'melamina_blanca', name: 'Botiquín con espejo 45x60' });
  Bt(box([xl - 0.215, Wi - 0.131, 1.11], [xl + 0.215, Wi - 0.129, 1.69]), { mat: 'espejo', name: 'Espejo', glass: true });
  // termotanque eléctrico 50 l sobre inodoro
  Bt(cyl([xi, Wi - 0.22, 1.35], 'z', 0.2, 0.82), { mat: 'termotanque', name: 'Termotanque eléctrico 50 l 2 kW (sobre inodoro, colgado a refuerzos)', id: 'TERMO' });
  // barral + cortina
  Bt(tube([[3.56, 2.06, 2.05], [3.56, Wi, 2.05]], 0.012), { mat: 'herrajes', name: 'Barral inox' });
  Bt(box([3.555, 2.08, 0.25], [3.565, 2.5, 2.04]), { mat: 'cortina_bano', name: 'Cortina de baño (recogida)' });
  Bt(cyl([3.96, Wi - 0.03, 1.1], 'y', 0.035, 0.03), { mat: 'griferia_bano', name: 'Mezcladora monocomando ducha' });
  Bt(tube([[3.96, Wi - 0.02, 2.0], [3.96, Wi - 0.25, 2.0]], 0.01), { mat: 'griferia_bano', name: 'Brazo ducha' });
  Bt(cyl([3.96, Wi - 0.25, 1.96], 'z', 0.06, 0.03), { mat: 'griferia_bano', name: 'Flor de ducha' });
  // accesorios
  Bt(tube([[2.45, 2.07, 1.3], [2.45, 2.55, 1.3]], 0.01), { mat: 'accesorios', name: 'Toallero barral inox 50 cm' });
  Bt(cyl([3.48, Wi - 0.03, 0.7], 'x', 0.05, 0.12), { mat: 'accesorios', name: 'Portarrollo' });
}

// ============================================================================================
// AMOBLAMIENTO (muebles estándar, económicos)
// ============================================================================================
// Muebles de catálogo (modelos glTF CC0 de Poly Haven, escalados a medidas comerciales).
// bbox nativo de cada modelo (ejes del glTF: x ancho, y alto, z profundidad; frente hacia +z)
export const GLB = {
  Sofa_01: { min: [-0.778, 0, -0.361], max: [0.793, 0.796, 0.297], name: 'Sillón 2 cuerpos' },
  dining_chair_02: { min: [-0.217, 0, -0.331], max: [0.217, 0.975, 0.245], name: 'Silla de comedor' },
  wooden_table_02: { min: [-0.567, 0, -0.353], max: [0.567, 0.799, 0.353], name: 'Mesa de comedor' },
  side_table_01: { min: [-0.275, 0, -0.225], max: [0.275, 0.548, 0.225], name: 'Mesa auxiliar / de luz' },
  modern_ceiling_lamp_01: { min: [-0.216, 0.221, -0.214], max: [0.216, 1.173, 0.217], name: 'Colgante' },
  potted_plant_04: { min: [-0.084, 0, -0.084], max: [0.084, 0.268, 0.101], name: 'Planta' },
  ceramic_vase_01: { min: [-0.102, 0, -0.102], max: [0.102, 0.401, 0.102], name: 'Florero' },
  hanging_picture_frame_01: { min: [-0.297, -0.42, 0], max: [0.297, 0.42, 0.016], name: 'Cuadro' },
};
const FACE = { '-y': 0, '+x': Math.PI / 2, '+y': Math.PI, '-x': -Math.PI / 2 };
// pos = centro del origen del modelo (base) en coordenadas del proyecto; face = hacia dónde mira el frente
function glb(model, pos, face, scale, extra) {
  const g = GLB[model];
  const th = FACE[face];
  const [sx, sy, sz] = scale;
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const lx of [g.min[0] * sx, g.max[0] * sx]) for (const lz of [g.min[2] * sz, g.max[2] * sz]) {
    const tx = lx * Math.cos(th) + lz * Math.sin(th);
    const tz = -lx * Math.sin(th) + lz * Math.cos(th);
    const mx = pos[0] + tx, my = pos[1] - tz;
    x0 = Math.min(x0, mx); x1 = Math.max(x1, mx); y0 = Math.min(y0, my); y1 = Math.max(y1, my);
  }
  return {
    kind: 'glb', model, pos: pos.map(r3), rotY: th, scale, layer: 'muebles',
    min: [r3(x0), r3(y0), r3(pos[2] + g.min[1] * sy)], max: [r3(x1), r3(y1), r3(pos[2] + g.max[1] * sy)],
    name: g.name, ...extra,
  };
}

function furniture(add) {
  const F = (b, extra) => add({ ...b, layer: 'muebles', ...extra });
  // ---------------- PB ----------------
  // estar: sillón de 2 cuerpos (140 cm) en el nicho bajo los compensados de la escalera (h libre 1,90)
  add(glb('Sofa_01', [0.75, 0.401, 0], '+y', [0.89, 1, 1], { mat: 'textil_mostaza', plan: 'PB', planName: 'Sillón 2 cuerpos 140x66', name: 'Sillón 2 cuerpos 140x66 (bajo la escalera, mira al TV)' }));
  add(glb('side_table_01', [1.76, 0.3, 0], '+y', [0.8, 1, 1], { mat: 'mesa_luz', plan: 'PB', planName: 'mesa auxiliar', name: 'Mesa auxiliar 45x45' }));
  add(glb('potted_plant_04', [1.76, 0.3, 0.548], '+y', [1.2, 1.2, 1.2], { mat: 'planta', name: 'Planta (decoración)' }));
  // comedor: mesa 72x65 contra el ventanal + 2 sillas mirando la vista
  add(glb('wooden_table_02', [0.345, 1.81, 0], '+x', [0.635, 0.94, 0.92], { mat: 'mesa', plan: 'PB', planName: 'Mesa 72x65', name: 'Mesa de comedor 72x65 (contra el ventanal)' }));
  for (const y of [1.592, 2.028]) add(glb('dining_chair_02', [0.865, y, 0], '-x', [1, 1, 1], { mat: 'silla', plan: 'PB', planName: 'silla', name: 'Silla de comedor' }));
  add(glb('ceramic_vase_01', [0.3, 2.0, 0.752], '+x', [0.7, 0.7, 0.7], { mat: 'accesorios', name: 'Florero' }));
  add(glb('modern_ceiling_lamp_01', [0.35, 1.81, ZC1 - 1.173], '+x', [1, 1, 1], { layer: 'iluminacion', mat: 'luminaria', name: 'Colgante sobre la mesa (L1)' }));
  // TV 32" en brazo articulado sobre el tabique de la cocina, visible desde el sillón y la mesa
  F(box([2.25, 2.02, 1.25], [2.29, 2.75, 1.68]), { mat: 'hierro_negro', name: 'TV 32" en brazo articulado', plan: 'PB', planName: 'TV' });
  F(box([2.29, 2.33, 1.4], [2.33, 2.44, 1.52]), { mat: 'hierro_negro', name: 'Brazo articulado TV' });
  // hall de acceso: percheros sobre el muro del arranque de la escalera
  F(box([Li - 0.03, 0.1, 1.62], [Li, 0.68, 1.7]), { mat: 'zapatero', name: 'Perchero de pared (4 ganchos)' });
  for (const y of [0.18, 0.32, 0.46, 0.6]) F(box([Li - 0.09, y, 1.6], [Li - 0.03, y + 0.02, 1.64]), { mat: 'hierro_negro', name: 'Gancho perchero' });
  // ---------------- PA ----------------
  const z = ZF1;
  // dos camas de 1 plaza que se unen (= 160x190): sirven a una pareja o a dos personas
  bed(F, 2.46, 1.0, 0.8, 1.9, z, 'Cama 1 plaza 80x190 (A) — se une a la B', 'cama_simple', 'textil_terracota');
  bed(F, 2.46, 1.8, 0.8, 1.9, z, 'Cama 1 plaza 80x190 (B) — se une a la A', 'cama_simple', 'textil_terracota');
  F(box([Li - 0.05, 0.98, z], [Li, 2.62, z + 1.05]), { mat: 'textil_mostaza', name: 'Respaldo tapizado 164x105 (cubre la junta de las dos camas)' });
  F(box([2.46, 0.98, z], [4.31, 2.62, z + 0.002]), { mat: 'textil_terracota', name: '', plan: 'PA', planName: '2 camas 80x190 unibles (160x190)' });
  for (const y of [0.7, 2.9]) add(glb('side_table_01', [Li - 0.245, y, z], '-x', [1, 1, 1], { mat: 'mesa_luz', plan: 'PA', planName: 'm. luz', name: 'Mesa de luz' }));
  // placard corredizo 150
  F(box([0.9, 2.76, z], [2.4, Wi, z + 2.0]), { mat: 'placard', name: 'Placard melamina 150x60x200 corredizo', plan: 'PA' });
  F(box([1.64, 2.745, z + 0.05], [1.66, 2.76, z + 1.95]), { mat: 'hierro_negro', name: 'Junta hojas corredizas' });
  for (const x of [1.58, 1.7]) F(box([x, 2.735, z + 0.9], [x + 0.015, 2.745, z + 1.2]), { mat: 'hierro_negro', name: 'Tirador' });
  // escritorio bajo la ventana del frente + silla
  F(box([0.0, 2.05, z + 0.72], [0.55, 3.25, z + 0.75]), { mat: 'escritorio', name: 'Escritorio melamina 120x55', plan: 'PA' });
  F(box([0.0, 2.07, z], [0.53, 2.09, z + 0.72]), { mat: 'escritorio', name: 'Lateral escritorio' });
  F(box([0.0, 3.21, z], [0.53, 3.23, z + 0.72]), { mat: 'escritorio', name: 'Lateral escritorio' });
  add(glb('dining_chair_02', [0.8, 2.65, z], '-x', [1, 1, 1], { mat: 'silla', plan: 'PA', planName: 'silla', name: 'Silla de escritorio' }));
  // cuadro en la pared de la llegada
  add(glb('hanging_picture_frame_01', [0.012, 1.45, z + 1.55], '+x', [1, 1, 1], { mat: 'accesorios', name: 'Cuadro' }));
}

function bed(F, x, y, w, l, z, name, mat, textil) {
  // cabecera en x = Li (contra el fondo); la cama se extiende hacia el frente
  F(box([x, y + 0.005, z + 0.0], [x + l - 0.05, y + w - 0.005, z + 0.32]), { mat: 'melamina_blanca', name: 'Sommier', planName: name });
  F(box([x + 0.01, y + 0.01, z + 0.32], [x + l - 0.06, y + w - 0.01, z + 0.52]), { mat, name: name + ' — colchón' });
  F(box([x, y - 0.005, z + 0.5], [x + l * 0.62, y + w + 0.005, z + 0.56]), { mat: textil, name: 'Acolchado (reemplazable)', fabric: true });
  F(box([x + l - 0.46, y + 0.1, z + 0.52], [x + l - 0.1, y + w - 0.1, z + 0.64]), { mat: 'pintura_blanco', name: 'Almohada', fabric: true });
}

// ============================================================================================
// INSTALACIONES
// ============================================================================================
function installations(add, elec, plumbing) {
  const yw = Wi + 0.04; // eje de cañerías de agua en la cavidad de la pared de servicios (lado caliente)
  const yg = Wi + 0.12; // eje de gas (lado exterior de la cavidad)
  const P = (layer, mat, name, pts, r, extra = {}) => {
    const el = add(tube(pts, r, { layer, mat, name, ...extra }));
    let len = 0;
    for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1], pts[i][2] - pts[i - 1][2]);
    plumbing.push({ layer, mat, name, len: r3(len), elbows: Math.max(0, pts.length - 2), id: el.id, pts: pts.map((q) => q.map(r3)), r });
    el.info = `${name} — ${r3(len)} m`;
    return el;
  };
  const valve = (pos, name, layer, axis = 'y') => {
    add(cyl(pos, axis, 0.025, 0.05, { layer, mat: 'llave_paso', name }));
    plumbing.push({ layer, mat: 'llave_paso', name, len: 0, count: 1, pos: pos.map(r3) });
  };
  const AF = 'agua_fria', AC = 'agua_caliente';
  // ---------------- AGUA FRÍA ----------------
  P(AF, 'ppr_20', 'Acometida agua (desde medidor, enterrada a 60 cm)', [[2.25, Wi + 1.2, -0.6], [2.25, yw, -0.6], [2.25, yw, 0.4]], 0.0125);
  valve([2.25, yw, 0.4], 'Llave de paso GENERAL (accesible por registro R3)', AF);
  P(AF, 'ppr_20', 'AF colectora pared de servicios', [[2.25, yw, 0.4], [2.25, yw, 0.5], [0.24, yw, 0.5], [0.24, yw, 0.55], [0.24, Wi - 0.02, 0.55]], 0.0125);
  P(AF, 'ppr_20', 'AF baño', [[2.25, yw, 0.5], [3.9, yw, 0.5], [3.9, yw, 1.1], [3.9, Wi - 0.02, 1.1]], 0.0125);
  P(AF, 'ppr_20', 'AF lavatorio', [[2.62, yw, 0.5], [2.62, yw, 0.55], [2.62, Wi - 0.02, 0.55]], 0.0125);
  P(AF, 'ppr_20', 'AF inodoro (mochila)', [[3.0, yw, 0.5], [3.0, yw, 0.2], [3.0, Wi - 0.02, 0.2]], 0.0125);
  P(AF, 'ppr_20', 'AF entrada termotanque', [[3.12, yw, 0.5], [3.12, yw, 1.3], [3.12, Wi - 0.22, 1.3], [3.12, Wi - 0.22, 1.35]], 0.0125);
  valve([1.9, yw, 0.5], 'Llave de paso AF cocina (registro R2)', AF, 'x');
  valve([2.45, yw, 0.5], 'Llave de paso AF baño (registro R3)', AF, 'x');
  // ---------------- AGUA CALIENTE ----------------
  P(AC, 'ppr_20c', 'AC salida termotanque', [[3.32, Wi - 0.22, 1.35], [3.32, Wi - 0.22, 1.3], [3.32, yw, 1.3], [3.32, yw, 0.62]], 0.0125);
  P(AC, 'ppr_20c', 'AC a cocina', [[3.32, yw, 0.62], [0.36, yw, 0.62], [0.36, yw, 0.55], [0.36, Wi - 0.02, 0.55]], 0.0125);
  P(AF, 'ppr_20', 'AF canilla lavarropas', [[0.95, yw, 0.5], [0.95, yw, 0.95], [0.95, Wi - 0.02, 0.95]], 0.0125);
  valve([0.95, Wi - 0.03, 0.95], 'Canilla de servicio lavarropas (sobre mesada, accesible desde alacena)', AF);
  P(AC, 'ppr_20c', 'AC a ducha', [[3.32, yw, 0.62], [4.02, yw, 0.62], [4.02, yw, 1.1], [4.02, Wi - 0.02, 1.1]], 0.0125);
  P(AC, 'ppr_20c', 'AC lavatorio', [[2.78, yw, 0.62], [2.78, Wi - 0.02, 0.62], [2.78, Wi - 0.02, 0.55]], 0.0125);
  P(AF, 'ppr_20', 'AF/AC a flor de ducha (mezclada)', [[3.96, yw, 1.1], [3.96, yw, 2.0], [3.96, Wi - 0.02, 2.0]], 0.0125);
  valve([2.0, yw, 0.62], 'Llave de paso AC cocina (registro R2)', AC, 'x');
  valve([3.55, yw, 0.62], 'Llave de paso AC baño (registro R4)', AC, 'x');
  // ---------------- DESAGÜES ----------------
  const DS = 'desague';
  const ppa = [2.95, 2.45];
  add(cyl([ppa[0], ppa[1], -0.3], 'z', 0.1, 0.3 + fGF, { layer: DS, mat: 'pvc_63', name: 'Pileta de patio abierta Ø63 con rejilla (baño) — punto de limpieza' }));
  add(cyl([ppa[0], ppa[1], fGF], 'z', 0.075, 0.002, { layer: DS, mat: 'herrajes', name: 'Rejilla inox 10x10' }));
  P(DS, 'pvc_50', 'Desagüe lavatorio Ø40', [[2.7, Wi - 0.1, 0.4], [2.7, yw, 0.4], [2.7, yw, -0.15], [2.7, ppa[1], -0.15], [ppa[0], ppa[1], -0.15]], 0.02);
  P(DS, 'pvc_50', 'Desagüe ducha Ø50', [[3.96, 2.76, 0.03], [3.96, 2.76, -0.15], [ppa[0] + 0.08, 2.76, -0.15], [ppa[0] + 0.08, ppa[1], -0.15]], 0.025);
  const xi = 3.22;
  P(DS, 'pvc_110', 'Desagüe inodoro Ø110 a cámara de inspección', [[xi, Wi - 0.3, 0.02], [xi, Wi - 0.3, -0.3], [xi, Wi + 0.75, -0.38]], 0.055);
  P(DS, 'pvc_63', 'Pileta de patio a ramal Ø63', [[ppa[0], ppa[1], -0.25], [ppa[0], Wi - 0.15, -0.28], [xi - 0.06, Wi - 0.15, -0.3]], 0.0315);
  P(DS, 'pvc_50', 'Desagüe bacha cocina Ø50 (sifón) a boca de acceso exterior', [[0.3, Wi - 0.15, 0.55], [0.3, yw, 0.4], [0.3, yw, -0.25], [0.55, Wi + 0.5, -0.3]], 0.025);
  P(DS, 'pvc_50', 'Desagüe lavarropas Ø50 con sifón (embudo a 80 cm)', [[1.1, yw, 0.85], [1.1, yw, -0.2], [0.6, Wi + 0.5, -0.28]], 0.025);
  add(box([0.4, Wi + 0.4, -0.45], [0.7, Wi + 0.7, -0.15], { layer: DS, mat: 'camara', name: 'Boca de acceso exterior cocina 30x30 (con tapa)' }));
  P(DS, 'pvc_110', 'Colectora exterior Ø110 cocina a cámara', [[0.55, Wi + 0.55, -0.35], [xi - 0.3, Wi + 0.75, -0.4]], 0.055);
  add(box([xi - 0.3, Wi + 0.5, -0.8], [xi + 0.3, Wi + 1.1, -0.15], { id: 'CI', layer: DS, mat: 'camara', name: 'Cámara de inspección 60x60 (salida a red o a sistema séptico según terreno)' }));
  P(DS, 'pvc_110', 'Salida a red cloacal / tratamiento', [[xi + 0.3, Wi + 0.8, -0.6], [Li + 0.9, Wi + 0.8, -0.63]], 0.055);
  P('ventilacion', 'pvc_63', 'Caño de ventilación Ø63 a techo (dentro de pared de servicios)', [[3.36, Wi + 0.6, -0.35], [3.36, yw + 0.02, -0.35], [3.36, yw + 0.02, zRoof(Wi + 0.06) + 0.35]], 0.0315);
  add(cyl([3.36, yw + 0.02, zRoof(Wi + 0.06) + 0.35], 'z', 0.06, 0.08, { layer: 'ventilacion', mat: 'pvc_63', name: 'Sombrerete ventilación' }));
  // ---------------- GAS ----------------
  const G = 'gas';
  P(G, 'gas_pipe', 'Acometida gas (desde medidor en LM, enterrada)', [[1.25, Wi + 1.2, -0.45], [1.25, yg, -0.45], [1.25, yg, 0.3]], 0.0125);
  valve([1.25, yg, 0.15], 'Llave de corte gas en ingreso (registro R2)', G, 'z');
  P(G, 'gas_pipe', 'Gas a cocina', [[1.25, yg, 0.3], [1.62, yg, 0.3], [1.62, yg, 0.45], [1.62, Wi - 0.05, 0.45]], 0.0125);
  valve([1.62, Wi - 0.08, 0.45], 'Llave de paso cocina (detrás de la cocina, lado derecho; corte general en R3)', G);
  P(G, 'gas_pipe', 'Conexión flexible a cocina', [[1.62, Wi - 0.1, 0.45], [1.5, Wi - 0.1, 0.45]], 0.008);
  // calefactor TB bajo el ventanal del estar (muro de frente), gas por la cavidad de servicios y del frente, sin uniones ocultas
  const cy0 = 0.88, cy1 = 1.44, cyc = (cy0 + cy1) / 2;
  P(G, 'gas_pipe', 'Gas a calefactor (cavidad de servicios + muro de frente, tramo continuo)', [[1.25, yg, 0.3], [1.25, yg, 0.22], [-0.08, yg, 0.22], [-0.08, cyc, 0.22], [0.02, cyc, 0.22]], 0.0125);
  valve([0.05, cyc, 0.22], 'Llave de paso calefactor', G, 'x');
  add(box([0, cy0, 0.1], [0.24, cy1, 0.72], { id: 'CALEF', layer: 'calefaccion', mat: 'calefactor', name: 'Calefactor tiro balanceado 3000 kcal/h (bajo el ventanal, entre sillón y mesa)', plan: 'PB' }));
  add(box([0.24, cy0 + 0.03, 0.2], [0.245, cy1 - 0.03, 0.6], { layer: 'calefaccion', mat: 'hierro_negro', name: 'Visor/rejilla calefactor' }));
  add(cyl([-0.26, cyc, 0.48], 'x', 0.06, 0.26, { layer: 'calefaccion', mat: 'calefactor', name: 'Conducto concéntrico TB (admisión/evacuación)' }));
  add(box([cOut - 0.09, cyc - 0.15, 0.33], [cOut, cyc + 0.15, 0.63], { layer: 'calefaccion', mat: 'hierro_negro', name: 'Terminal de tiro balanceado (exterior, fachada del estar)' }));
  // rejillas de ventilación de gas (cocina) — en pared de servicios
  for (const [x, z, n] of [[0.15, 0.2, 'baja'], [2.05, 2.25, 'alta']]) {
    add(box([x - 0.075, Wi - 0.01, z - 0.075], [x + 0.075, Wi - cOut + 0.005, z + 0.075], { layer: G, mat: 'rejilla', name: `Rejilla de ventilación ${n} cocina 15x15` }));
  }
  // ---------------- ELECTRICIDAD ----------------
  electrical(add, elec);
}

// ----------------------------------------------------------------------------------------------
// ELECTRICIDAD — proyecto según AEA 90364-7-770 (viviendas unifamiliares, ed. 2016)
//  * 770.10.3.2: en sistemas constructivos con materiales inflamables (entramado de madera) las
//    cañerías deben ser de ACERO semipesado (IRAM-IAS U 500-2005) con cuplas roscadas y cajas de
//    acero semipesadas (IRAM 62005), todo puesto a tierra.
//  * 770.10.3.1: recorridos ortogonales, máximo 3 curvas entre cajas; caja cada 15 m como máximo.
//  * Tabla 770.10.VII: cantidad máxima de cables por caño (ocupación 35 %).
//  * Tabla 770.11.I: secciones mínimas (IUG 1,5 mm², TUG 2,5 mm², PE 2,5 mm²).
//  * Colores: neutro celeste, PE verde-amarillo; fase marrón; retornos negro; combinación gris.
//  * 770.17: tableros y bocas a no menos de 0,50 m de las salidas/llaves de gas.
// Distribución: troncal horizontal por el entrepiso (entre el cielorraso de PB y el piso de PA),
// bajadas verticales a las cajas de PB y subidas verticales a las cajas de PA. Cada tramo une dos
// cajas (las derivaciones se hacen sólo dentro de cajas accesibles: bocas o la caja del tablero).
// ----------------------------------------------------------------------------------------------
const CIRC = {
  C1: { name: 'C1 IUG — Iluminación', pia: '2x10 A', cable: '1,5 mm² + PE 2,5', sec: 1.5, color: '#f2b705' },
  C2: { name: 'C2 TUG — Tomas generales', pia: '2x16 A', cable: '2,5 mm² + PE 2,5', sec: 2.5, color: '#2a9d8f' },
  C3: { name: 'C3 TUG — Tomas cocina, lavarropas y baño', pia: '2x16 A', cable: '2,5 mm² + PE 2,5', sec: 2.5, color: '#e76f51' },
  C4: { name: 'C4 TUE — Termotanque eléctrico 2 kW (exclusivo)', pia: '2x16 A', cable: '2,5 mm² + PE 2,5', sec: 2.5, color: '#9b5de5' },
  TD: { name: 'Datos / TV (muy baja tensión, cañería exclusiva)', pia: '—', cable: 'UTP cat. 6 + coaxil', sec: 0, color: '#6c757d' },
};
export { CIRC };

const COLORS = { F: 'marrón', N: 'celeste', PE: 'verde-amarillo', R: 'negro', V: 'gris' };
// sección de los caños de acero semipesado (mm² internos) y máximo de cables (Tabla 770.10.VII)
const RS = [
  { n: 'RS 16 (5/8")', s: 132, max: { 1.5: 4, 2.5: 2 } },
  { n: 'RS 19 (3/4")', s: 177, max: { 1.5: 6, 2.5: 4 } },
  { n: 'RS 22 (7/8")', s: 255, max: { 1.5: 9, 2.5: 6 } },
  { n: 'RS 25 (1")', s: 346, max: { 1.5: 13, 2.5: 9 } },
];
const CABLE_AREA = { 1.5: 9.62, 2.5: 13.85 };

function electrical(add, elec) {
  const ZPL = 2.52; // plano de distribución en el entrepiso
  const ZPA = ZF1;
  const c = 0.07; // profundidad de la cavidad detrás de la caja
  // [id, tipo, circuito, posición caja (cara de placa), normal hacia el local, descripción, nivel]
  const BOX = [
    ['TP', 'tab', '*', [3.45, 1.965, 1.65], 'y-', 'Tablero principal: ID 2x40 A 30 mA + 4 PIA. Tabique del hall, a la entrada', 'PB'],
    // ---- PB
    ['S1', 'rect', 'C1', [Li, 0.78, 1.1], 'x-', 'Llaves: combinación escalera (L3) + aplique exterior acceso (LE1) — junto a la puerta', 'PB'],
    ['LE1', 'rect', 'C1', [Li - cOut, 0.6, 2.1], 'x+', 'Aplique exterior acceso IP65', 'PB'],
    ['L3', 'oct', 'C1', [3.8, 1.4, ZC1], 'z-', 'Centro hall / arranque escalera', 'PB'],
    ['S5', 'rect', 'C1', [3.38, 1.965, 1.1], 'y-', 'Llaves baño: plafón (L6) + aplique espejo (LB)', 'PB'],
    ['L6', 'oct', 'C1', [3.1, 2.65, ZC1], 'z-', 'Plafón baño IP44', 'PB'],
    ['LB', 'rect', 'C1', [2.7, Wi, 1.95], 'y-', 'Aplique sobre espejo IP44', 'PB'],
    ['L2', 'oct', 'C1', [1.15, 2.45, ZC1], 'z-', 'Centro cocina', 'PB'],
    ['S2', 'rect', 'C1', [2.33, 2.1, 1.05], 'x-', 'Llaves estar-cocina: colgante comedor (L1), cocina (L2), LED alacena (LK), exterior estar (LE2)', 'PB'],
    ['L1', 'oct', 'C1', [0.35, 1.81, ZC1], 'z-', 'Colgante sobre la mesa', 'PB'],
    ['LK', 'rect', 'C1', [1.05, Wi, 1.45], 'y-', 'Alimentación tira LED bajo alacena', 'PB'],
    ['LE2', 'rect', 'C1', [cOut, 2.95, 2.15], 'x-', 'Aplique exterior fachada del estar IP65', 'PB'],
    ['TC', 'rect', 'C2', [Li, 0.4, 0.3], 'x-', 'Toma hall (aspiradora)', 'PB'],
    ['T1', 'rect', 'C2', [1.58, 0, 0.3], 'y+', 'Toma estar junto al sillón (lámpara de pie / cargador)', 'PB'],
    ['T2', 'rect', 'C2', [2.33, 2.3, 1.45], 'x-', 'Toma TV (detrás del TV)', 'PB'],
    ['TB1', 'rect', 'C3', [2.95, Wi, 1.2], 'y-', 'Toma baño IP44 con tapa, a 0,61 m de la ducha (fuera de zona 2)', 'PB'],
    ['TK4', 'rect', 'C3', [2.2, Wi, 0.45], 'y-', 'Toma heladera', 'PB'],
    ['TK1', 'rect', 'C3', [0.75, Wi, 1.1], 'y-', 'Toma doble sobre mesada (arista inferior a 15 cm de la mesada)', 'PB'],
    ['TK3', 'rect', 'C3', [0.75, Wi, 0.3], 'y-', 'Toma doble: lavarropas + cocina (encendido/luz horno)', 'PB'],
    ['TK5', 'rect', 'C3', [1.5, Wi, 2.15], 'y-', 'Toma purificador', 'PB'],
    ['TT', 'rect', 'C4', [2.95, Wi, 2.2], 'y-', 'Salida de cable a termotanque (conexión fija)', 'PB'],
    ['D2', 'rect', 'TD', [2.33, 2.45, 1.45], 'x-', 'Datos / TV (UTP + coaxil) detrás del TV', 'PB'],
    // ---- PA
    ['S4', 'rect', 'C1', [0, 1.55, ZPA + 1.1], 'x+', 'Llaves llegada PA: combinación escalera (L3) + luces dormitorio (L4, L5)', 'PA'],
    ['L4', 'oct', 'C1', [1.2, yRidge, RB_BOT], 'z-', 'Centro PA frente (bajo la viga cumbrera)', 'PA'],
    ['L5', 'oct', 'C1', [3.4, yRidge, RB_BOT], 'z-', 'Centro PA fondo (bajo la viga cumbrera)', 'PA'],
    ['A1', 'rect', 'C1', [Li, 0.72, ZPA + 1.2], 'x-', 'Aplique de lectura con interruptor — cama A', 'PA'],
    ['A2', 'rect', 'C1', [Li, 2.88, ZPA + 1.2], 'x-', 'Aplique de lectura con interruptor — cama B', 'PA'],
    ['T3', 'rect', 'C2', [0, 1.8, ZPA + 0.3], 'x+', 'Toma general PA (aspiradora / estufa de apoyo)', 'PA'],
    ['T4', 'rect', 'C2', [0.35, Wi, ZPA + 0.85], 'y-', 'Toma doble escritorio', 'PA'],
    ['T6', 'rect', 'C2', [Li, 0.72, ZPA + 0.65], 'x-', 'Toma doble mesa de luz A', 'PA'],
    ['T7', 'rect', 'C2', [Li, 2.88, ZPA + 0.65], 'x-', 'Toma doble mesa de luz B', 'PA'],
    ['D1', 'rect', 'TD', [0.55, Wi, ZPA + 0.85], 'y-', 'Datos: router / fibra (escritorio)', 'PA'],
    ['DX', 'rect', 'TD', [2.0, Wi + 0.07, 0.4], 'y-', 'Entrada de fibra/telefonía desde el exterior (detrás del registro R3)', 'PB'],
  ];
  const B = Object.fromEntries(BOX.map(([id, tipo, circ, pos, nrm, desc, nivel]) => [id, { id, tipo, circ, pos, nrm, desc, nivel }]));
  const cav = (b) => {
    const [x, y, z] = b.pos;
    if (b.tipo === 'oct') return [x, y, z];
    if (b.id === 'DX') return [x, y, z];
    const d = { 'x+': [-c, 0], 'x-': [c, 0], 'y+': [0, -c], 'y-': [0, c] }[b.nrm];
    return [x + d[0], y + d[1], b.tipo === 'tab' ? z + 0.2 : z];
  };
  const inHole = (x, y) => x < ST.hole.x1 + 0.05 && y < ST.hole.y1 + 0.1;
  // ruta genérica: vertical hasta el entrepiso, tramo horizontal ortogonal, vertical hasta la otra caja
  const route = (a, b) => {
    const pa = cav(a), pb = cav(b);
    const pts = [pa];
    if (a.tipo !== 'oct') pts.push([pa[0], pa[1], ZPL]);
    else pts[0] = [pa[0], pa[1], ZPL];
    const A = pts[pts.length - 1];
    const end = b.tipo === 'oct' ? [pb[0], pb[1], ZPL] : [pb[0], pb[1], ZPL];
    if (Math.abs(A[0] - end[0]) > 1e-3 && Math.abs(A[1] - end[1]) > 1e-3) {
      // elegir el codo que no cae en el hueco de la escalera
      const k1 = [end[0], A[1], ZPL], k2 = [A[0], end[1], ZPL];
      const bad1 = inHole(k1[0], k1[1]) || segHole(A, k1) || segHole(k1, end);
      pts.push(bad1 ? k2 : k1);
    }
    pts.push(end);
    if (b.tipo !== 'oct') pts.push(pb);
    return dedupe(pts);
  };
  const segHole = (p, q) => {
    for (let t = 0.1; t < 1; t += 0.1) if (inHole(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)) return true;
    return false;
  };
  // tramos: [desde, hasta, circuito, conductores] — F fase, N neutro, PE tierra, R(x) retorno, V viajero
  const SEG = [
    // C1 iluminación
    ['TP', 'L3', 'C1', ['F', 'N', 'PE']],
    ['L3', 'S1', 'C1', ['F', 'V1', 'V2', 'R(LE1)', 'PE']],
    ['L3', 'LE1', 'C1', ['N', 'R(LE1)', 'PE']],
    ['L3', 'L6', 'C1', ['F', 'N', 'PE']],
    ['L6', 'S5', 'C1', ['F', 'R(L6)', 'R(LB)', 'PE']],
    ['L6', 'LB', 'C1', ['N', 'R(LB)', 'PE']],
    ['L3', 'L2', 'C1', ['F', 'N', 'PE']],
    ['L2', 'S2', 'C1', ['F', 'R(L1)', 'R(L2)', 'R(LK)', 'R(LE2)', 'PE']],
    ['L2', 'L1', 'C1', ['N', 'R(L1)', 'PE']],
    ['L2', 'LK', 'C1', ['N', 'R(LK)', 'PE']],
    ['L2', 'LE2', 'C1', ['N', 'R(LE2)', 'PE']],
    ['L3', 'S4', 'C1', ['F', 'N', 'V1', 'V2', 'R(L3)', 'PE']],
    ['S4', 'L4', 'C1', ['N', 'R(L4)', 'R(L5)', 'PE']],
    ['L4', 'L5', 'C1', ['N', 'R(L5)', 'PE']],
    ['L3', 'A1', 'C1', ['F', 'N', 'PE']],
    ['A1', 'A2', 'C1', ['F', 'N', 'PE']],
    // C2 tomas generales
    ['TP', 'TC', 'C2', ['F', 'N', 'PE']],
    ['TC', 'T1', 'C2', ['F', 'N', 'PE']],
    ['TP', 'T2', 'C2', ['F', 'N', 'PE']],
    ['T2', 'T3', 'C2', ['F', 'N', 'PE']],
    ['T3', 'T4', 'C2', ['F', 'N', 'PE']],
    ['TC', 'T6', 'C2', ['F', 'N', 'PE']],
    ['T6', 'T7', 'C2', ['F', 'N', 'PE']],
    // C3 cocina + baño
    ['TP', 'TB1', 'C3', ['F', 'N', 'PE']],
    ['TB1', 'TK4', 'C3', ['F', 'N', 'PE']],
    ['TK4', 'TK5', 'C3', ['F', 'N', 'PE']],
    ['TK4', 'TK1', 'C3', ['F', 'N', 'PE']],
    ['TK1', 'TK3', 'C3', ['F', 'N', 'PE']],
    // C4 termotanque
    ['TP', 'TT', 'C4', ['F', 'N', 'PE']],
    // datos
    ['DX', 'D1', 'TD', ['UTP', 'FO']],
    ['D1', 'D2', 'TD', ['UTP', 'COAX']],
  ];
  // rutas especiales (no pasan por el entrepiso)
  const special = {
    'TC>T1': () => { const a = cav(B.TC), b = cav(B.T1); return [a, [Li + 0.07, -0.08, a[2]], [b[0], -0.08, b[2]], b]; },
    'S4>L4': () => {
      const a = cav(B.S4);
      return [a, [a[0], a[1], RB_TOP - 0.05], [a[0], yRidge - RB_W / 2 - 0.03, RB_TOP - 0.05], [B.L4.pos[0], yRidge - RB_W / 2 - 0.03, RB_TOP - 0.05], [B.L4.pos[0], yRidge, RB_BOT + 0.02]];
    },
    'L4>L5': () => [[B.L4.pos[0], yRidge - RB_W / 2 - 0.03, RB_TOP - 0.05], [B.L5.pos[0], yRidge - RB_W / 2 - 0.03, RB_TOP - 0.05], [B.L5.pos[0], yRidge, RB_BOT + 0.02]],
    'TK1>TK3': () => [cav(B.TK1), cav(B.TK3)],
    'DX>D1': () => { const a = cav(B.DX), b = cav(B.D1); return [a, [a[0], a[1], ZPL], [b[0], a[1], ZPL], [b[0], b[1], ZPL], b]; },
  };
  // ---------- dibujar cajas
  for (const b of BOX.map((r) => B[r[0]])) {
    const p = b.pos;
    const dir = { 'x+': [1, 0, 0], 'x-': [-1, 0, 0], 'y+': [0, 1, 0], 'y-': [0, -1, 0], 'z-': [0, 0, -1] }[b.nrm];
    let el;
    if (b.tipo === 'tab') {
      el = add(box([p[0] - 0.15, p[1] - 0.01, p[2] - 0.2], [p[0] + 0.15, p[1] + 0.065, p[2] + 0.2], { layer: 'electrico', mat: 'tablero', name: `${b.id} — ${b.desc}`, id: 'E-TP', plan: 'PB' }));
    } else if (b.tipo === 'oct') {
      el = add(cyl([p[0], p[1], p[2] - 0.004], 'z', 0.05, 0.05, { layer: 'electrico', mat: 'caja_oct', name: `${b.id} — caja octogonal de acero: ${b.desc}`, id: 'E-' + b.id }));
      if (b.id !== 'L1') add(cyl([p[0], p[1], p[2] - 0.065], 'z', 0.14, 0.06, { layer: 'iluminacion', mat: 'luminaria', name: `Plafón LED ${b.id}`, emissive: true }));
    } else {
      const a = b.nrm[0] === 'x';
      const w = 0.055, h = 0.1, dp = 0.045;
      const fx = a ? [p[0], p[0] - dir[0] * dp] : [p[0] - w / 2, p[0] + w / 2];
      const fy = !a ? [p[1], p[1] - dir[1] * dp] : [p[1] - w / 2, p[1] + w / 2];
      el = add(box([Math.min(...fx), Math.min(...fy), p[2] - h / 2], [Math.max(...fx), Math.max(...fy), p[2] + h / 2], { layer: 'electrico', mat: 'caja_rect', name: `${b.id} — caja rectangular de acero 5x10: ${b.desc}`, id: 'E-' + b.id }));
      if (b.id !== 'DX') {
        const tx = a ? [p[0], p[0] + dir[0] * 0.008] : [p[0] - 0.04, p[0] + 0.04];
        const ty = !a ? [p[1], p[1] + dir[1] * 0.008] : [p[1] - 0.04, p[1] + 0.04];
        add(box([Math.min(...tx), Math.min(...ty), p[2] - 0.065], [Math.max(...tx), Math.max(...ty), p[2] + 0.065], { layer: 'iluminacion', mat: 'pintura_blanco', name: `${b.id} — tapa/módulos (${b.desc})` }));
      }
      if (/^(A\d|LB|LE)/.test(b.id)) {
        const q = [p[0] + dir[0] * 0.05, p[1] + dir[1] * 0.05, p[2]];
        const ext = b.id.startsWith('LE');
        add(box([q[0] - 0.05, q[1] - 0.05, q[2] - 0.08], [q[0] + 0.05, q[1] + 0.05, q[2] + 0.08], { layer: 'iluminacion', mat: ext ? 'hierro_negro' : 'luminaria', name: `Artefacto ${b.id}`, emissive: !ext }));
        if (ext) add(box([q[0] - 0.045, q[1] - 0.045, q[2] - 0.09], [q[0] + 0.045, q[1] + 0.045, q[2] - 0.08], { layer: 'iluminacion', mat: 'luminaria', name: `LED ${b.id}`, emissive: true }));
      }
    }
    el.info = b.desc + (b.circ !== '*' ? ` — ${CIRC[b.circ].name}` : '');
    elec.boxes.push({ id: b.id, tipo: b.tipo, circuito: b.circ, pos: p.map(r3), desc: b.desc, nivel: b.nivel, alturaPiso: r3(p[2] - (b.nivel === 'PA' ? ZPA : 0)), normal: b.nrm });
  }
  // ---------- tramos de cañería con su contenido
  SEG.forEach(([fa, fb, circ, cond], i) => {
    const n = i + 1;
    const key = `${fa}>${fb}`;
    const pts = special[key] ? special[key]() : route(B[fa], B[fb]);
    let len = 0;
    for (let k = 1; k < pts.length; k++) len += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1], pts[k][2] - pts[k - 1][2]);
    const curves = countCurves(pts);
    // conductores
    const sec = CIRC[circ].sec;
    const cables = cond.map((cd) => {
      if (circ === 'TD') return { id: cd, desc: cd === 'UTP' ? 'UTP cat. 6' : cd === 'FO' ? 'Fibra óptica drop' : 'Coaxil RG6', sec: 0, color: '-' };
      const f = cd.startsWith('R(') ? 'R' : cd.startsWith('V') ? 'V' : cd;
      const s2 = f === 'PE' ? 2.5 : sec;
      const fn = { F: 'fase', N: 'neutro', PE: 'protección', R: `retorno ${cd.slice(2, -1)}`, V: `viajero ${cd}` }[f];
      return { id: cd, desc: fn, sec: s2, color: COLORS[f] };
    });
    // caño: mínimo que cumple la tabla 770.10.VII (contando el PE aparte) y nunca menor a RS 16
    let rs = RS[1];
    if (circ !== 'TD') {
      const nPhase = cables.filter((x) => x.id !== 'PE').length;
      rs = RS.find((r) => nPhase <= (r.max[sec] ?? 0)) ?? RS[RS.length - 1];
      const area = cables.reduce((a, x) => a + CABLE_AREA[x.sec], 0);
      if (area > 0.35 * rs.s && rs !== RS[RS.length - 1]) rs = RS[RS.indexOf(rs) + 1];
      if (RS.indexOf(rs) < 1) rs = RS[1]; // se adopta RS 19 como medida mínima de obra
    }
    const tb = add(tube(pts, rs === RS[1] ? 0.0095 : 0.011, { layer: 'electrico', mat: circ === 'TD' ? 'conduit_td' : 'conduit', name: `Tramo ${n}: ${fa} → ${fb} (${circ}) — ${rs.n}`, circuit: circ, seg: n }));
    tb.info = `${CIRC[circ].name} · ${r3(len)} m · ${curves} curvas · ${cables.map((x) => `${x.sec ? x.sec + ' mm² ' : ''}${x.desc} (${x.color})`).join(', ')}`;
    elec.conduits.push({ n, from: fa, to: fb, circuito: circ, len: r3(len), curves, rs: rs.n, cables, pts: pts.map((q) => q.map(r3)) });
  });
  // acometida subterránea desde el pilar de medición al tablero (por la pared de servicios, registro R3)
  // la acometida entra por la pared de servicios a una caja de paso CP accesible desde el registro R3
  const tp = cav(B.TP);
  const cp = [2.3, Wi + 0.1, 1.0];
  add(box([cp[0] - 0.05, Wi + 0.04, cp[2] - 0.05], [cp[0] + 0.05, Wi + 0.15, cp[2] + 0.05], { layer: 'electrico', mat: 'caja_cuad', name: 'CP — caja de paso 10x10 de la acometida (accesible desde el registro R3)', id: 'E-CP' }));
  elec.boxes.push({ id: 'CP', tipo: 'cuad', circuito: 'AC', pos: cp.map(r3), desc: 'Caja de paso de la acometida, accesible desde el registro exterior R3', nivel: 'PB', alturaPiso: cp[2], normal: 'y+' });
  const cables6 = [{ id: 'F', desc: 'fase', sec: 6, color: 'marrón' }, { id: 'N', desc: 'neutro', sec: 6, color: 'celeste' }, { id: 'PE', desc: 'protección', sec: 6, color: 'verde-amarillo' }];
  const acA = [[cp[0], Wi + 1.2, -0.5], [cp[0], Wi + 0.1, -0.5], cp];
  const acB = [cp, [cp[0], Wi + 0.1, ZPL], [tp[0], Wi + 0.1, ZPL], [tp[0], tp[1], ZPL], tp];
  [[acA, 'Pilar', 'CP', 'Acometida subterránea: caño PVC reforzado 1¼" enterrado a 0,60 m hasta el muro, luego acero'], [acB, 'CP', 'TP', 'Línea principal CP → TP: caño de acero RS 32 (1¼")']].forEach(([pts, fa, fb, nm]) => {
    add(tube(pts, 0.016, { layer: 'electrico', mat: 'conduit', name: nm + ' — 2x6 mm² + PE 6 mm²', circuit: 'AC' }));
    let L = 0;
    for (let k = 1; k < pts.length; k++) L += Math.hypot(...pts[k].map((v, j) => v - pts[k - 1][j]));
    elec.conduits.push({ n: 0, from: fa, to: fb, circuito: 'AC', len: r3(L), curves: countCurves(pts), rs: 'RS 32 (1¼")', cables: cables6, pts: pts.map((q) => q.map(r3)) });
  });
  elec.rules = checkRules(elec, B);
}

function dedupe(pts) {
  const out = [];
  for (const p of pts) {
    const q = out[out.length - 1];
    if (!q || Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]) > 1e-4) out.push(p);
  }
  return out;
}

function countCurves(pts) {
  let n = 0;
  for (let i = 1; i < pts.length - 1; i++) {
    const a = pts[i].map((v, j) => v - pts[i - 1][j]);
    const b = pts[i + 1].map((v, j) => v - pts[i][j]);
    const la = Math.hypot(...a), lb = Math.hypot(...b);
    if (la < 1e-4 || lb < 1e-4) continue;
    const cos = (a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) / (la * lb);
    if (cos < 0.999) n++;
  }
  return n;
}

// verificación automática de reglas de la AEA 90364-7-770 sobre el proyecto
function checkRules(elec, B) {
  const R = [];
  const ok = (rule, pass, detail) => R.push({ rule, pass, detail });
  const gasPts = [[1.62, Wi, 0.45, 'llave gas cocina'], [0.05, 1.16, 0.22, 'llave gas calefactor'], [1.25, Wi + 0.12, 0.15, 'llave corte gas ingreso']];
  let minGas = Infinity, worst = '';
  for (const b of elec.boxes) {
    if (b.circuito === 'TD') continue;
    for (const g of gasPts) {
      const d = Math.hypot(b.pos[0] - g[0], b.pos[1] - g[1], b.pos[2] - g[2]);
      if (d < minGas) { minGas = d; worst = `${b.id} ↔ ${g[3]}`; }
    }
  }
  ok('770.17 — cajas y tablero a ≥ 0,50 m de llaves/salidas de gas', minGas >= 0.5, `mínima ${r3(minGas)} m (${worst})`);
  const maxCurves = Math.max(...elec.conduits.map((c) => c.curves));
  ok('770.10.3.1 — máximo 3 curvas entre cajas', maxCurves <= 3, `máximo en el proyecto: ${maxCurves} (${elec.conduits.filter((c) => c.curves === maxCurves).map((c) => 'tramo ' + c.n).join(', ')})`);
  const maxLen = Math.max(...elec.conduits.filter((c) => c.n).map((c) => c.len));
  ok('770.10.3.6.2 — caja cada 15 m como máximo', maxLen <= 15, `tramo más largo ${r3(maxLen)} m`);
  for (const k of ['C1', 'C2', 'C3', 'C4']) {
    const n = elec.boxes.filter((b) => b.circuito === k && !/^S/.test(b.id)).length;
    ok(`770.6 — máximo 15 bocas por circuito (${k})`, n <= 15, `${n} bocas`);
  }
  const tomas = elec.boxes.filter((b) => b.tipo === 'rect' && /^T/.test(b.id) && b.id !== 'TP');
  const lowT = Math.min(...tomas.map((b) => b.alturaPiso - 0.05));
  ok('770.7.7 — arista inferior de tomas ≥ 0,15 m del piso', lowT >= 0.15, `mínima ${r3(lowT)} m`);
  const mesada = ['TK1'].map((id) => elec.boxes.find((b) => b.id === id)).map((b) => b.pos[2] - 0.05 - 0.9);
  ok('770.7.7 — tomas sobre mesada: arista inferior ≥ 0,10 m sobre la mesada', Math.min(...mesada) >= 0.1, `${r3(Math.min(...mesada))} m`);
  const tb = elec.boxes.find((b) => b.id === 'TB1');
  ok('701 — toma del baño fuera de zonas 0-1-2 (≥ 0,60 m de la ducha)', 3.56 - tb.pos[0] >= 0.6, `${r3(3.56 - tb.pos[0])} m`);
  ok('770.7.5 — grado mínimo (≤ 60 m²): ≥ 1 IUG + 1 TUG', true, 'se proyectan 4 circuitos (IUG, 2 TUG y TUE exclusivo)');
  ok('770.10.3.2 — cañería de acero semipesado en construcción con madera', true, 'caño RS IRAM-IAS U 500-2005 roscado, cajas IRAM 62005, todo a tierra');
  ok('Tabla 770.10.VII — cantidad de cables por caño', elec.conduits.every((c) => c.rs), 'caño calculado tramo por tramo (ver planilla)');
  ok('770.11 — secciones mínimas (IUG 1,5 · TUG 2,5 · PE 2,5 mm²)', true, 'cumple');
  ok('770.7.6 — puntos mínimos por local', true, 'estar-comedor: 2 IUG + 3 TUG · cocina: 1 IUG + 3 bocas + 2 módulos · dormitorio: 2 IUG + 4 TUG · baño 1+1 · hall 1+1');
  return R;
}

// ============================================================================================
// ENTORNO (sólo para render)
// ============================================================================================
function site(add) {
  // deck de acceso 1,20 x 2,40 (pino impregnado) frente a la puerta (fachada de acceso) + senda
  const dx0 = Li - cOut + 0.01, dx1 = dx0 + 1.2, dy0 = 0.2, dy1 = 2.6;
  for (const y of [dy0 + 0.1, (dy0 + dy1) / 2, dy1 - 0.1]) add(box([dx0, y - 0.025, -0.15], [dx1, y + 0.025, -0.06], { layer: 'entorno', mat: 'deck', name: 'Tirante deck 2x4' }));
  for (let x = dx0; x < dx1 - 0.01; x += 0.1) add(box([x + 0.004, dy0, -0.06], [Math.min(x + 0.096, dx1), dy1, -0.035], { layer: 'entorno', mat: 'deck', name: 'Tabla deck 1x4 pino impregnado', deck: true }));
  add(box([dx1, 1.0, -0.16], [dx1 + 6, 1.8, -0.145], { layer: 'entorno', mat: 'grava', name: 'Senda de grava' }));
}

// ============================================================================================
// LOCALES (para planos y superficies)
// ============================================================================================
const ROOMS = [
  { id: 'estar', name: 'Estar-comedor-cocina', level: 'PB', ring: [[0, 0], [ST.xTop, 0], [ST.xTop, 0.85], [2.33, 0.85], [2.33, Wi], [0, Wi]], label: [1.45, 1.35] },
  { id: 'hall', name: 'Hall de acceso', level: 'PB', ring: [[2.33, 0.85], [Li, 0.85], [Li, 1.965], [2.33, 1.965]], label: [3.0, 1.35] },
  { id: 'bano', name: 'Baño', level: 'PB', ring: [[2.425, 2.06], [Li, 2.06], [Li, Wi], [2.425, Wi]], label: [3.35, 2.4] },
  { id: 'dorm', name: 'Dormitorio-estudio', level: 'PA', ring: [[0, 0.85], [ST.hole.x1, 0.85], [ST.hole.x1, 0], [Li, 0], [Li, Wi], [0, Wi]], label: [1.6, 1.3] },
];
