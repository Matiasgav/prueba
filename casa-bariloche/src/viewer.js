// Visor 3D (three.js) del modelo paramétrico.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { GroundedSkybox } from 'three/addons/objects/GroundedSkybox.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { SPECS } from './specs.js';
import { ASSETS } from './assets.gen.js';

// ---------------------------------------------------------------- texturas PBR (Poly Haven, CC0)
// material -> [textura, escala (m por repetición), mapas, mezcla del color de la especificación (0 = color de la foto)]
const TEXMAP = {
  spc: ['oak_wood_planks', 1.6, 'dnr', 0],
  porcelanato: ['brushed_concrete', 1.2, 'dnr', 0.1],
  siding: ['japanese_cedar_planks', 1.0, 'dnr', 0.55, true],
  deck: ['wood_floor_deck', 1.2, 'dnr', 0],
  lenga: ['fine_grained_wood', 0.8, 'dn', 0.55],
  pasamanos: ['fine_grained_wood', 0.8, 'dn', 0.55],
  mesa: ['fine_grained_wood', 0.8, 'dn', 0.35],
  escritorio: ['fine_grained_wood', 0.8, 'dn', 0.35],
  mesa_luz: ['fine_grained_wood', 0.8, 'dn', 0.35],
  zanca: ['fine_grained_wood', 1.2, 'dn', 0.2],
  laminada: ['fine_grained_wood', 1.5, 'dn', 0.3],
  pino_2x6: ['fine_grained_wood', 1.5, 'dn', 0.2], pino_2x8: ['fine_grained_wood', 1.5, 'dn', 0.2], pino_2x3: ['fine_grained_wood', 1.5, 'dn', 0.2],
  pino_2x2: ['fine_grained_wood', 1.5, 'dn', 0.2], pino_1x2: ['fine_grained_wood', 1.5, 'dn', 0.2],
  textil_mostaza: ['rough_linen', 0.35, 'dn', 0.85], textil_terracota: ['rough_linen', 0.35, 'dn', 0.85],
  cama_simple: ['rough_linen', 0.35, 'dn', 0.5], respaldo: ['rough_linen', 0.35, 'dn', 0.85],
  cortina: ['rough_linen', 0.5, 'dn', 0.6],
  pintura_blanco: ['painted_plaster_wall', 1.6, 'n', 1], pintura_salvia: ['painted_plaster_wall', 1.6, 'n', 1], pintura_antihongo: ['painted_plaster_wall', 1.6, 'n', 1],
  grava: ['gravel', 1.0, 'dn', 0],
};
const texCache = {};
function tex(name, kind, srgb) {
  const key = `${name}_${kind}`;
  if (texCache[key]) return texCache[key];
  const url = ASSETS.tex[key];
  if (!url) return null;
  const t = new THREE.TextureLoader().load(url);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  texCache[key] = t;
  return t;
}
function b64buf(b64) {
  const bin = atob(b64);
  const u = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return u.buffer;
}
// UV por proyección en caja (coordenadas del mundo) para que las texturas tengan escala real
function worldUV(geo, scale, rot) {
  const g = geo.index ? geo.toNonIndexed() : geo;
  if (!g.attributes.normal) g.computeVertexNormals();
  const p = g.attributes.position, n = g.attributes.normal;
  const uv = new Float32Array(p.count * 2);
  for (let i = 0; i < p.count; i++) {
    const ax = Math.abs(n.getX(i)), ay = Math.abs(n.getY(i)), az = Math.abs(n.getZ(i));
    let u, v;
    if (ay >= ax && ay >= az) { u = p.getX(i); v = p.getZ(i); } else if (ax >= az) { u = p.getZ(i); v = p.getY(i); } else { u = p.getX(i); v = p.getY(i); }
    uv[2 * i] = (rot ? v : u) / scale;
    uv[2 * i + 1] = (rot ? u : v) / scale;
  }
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  return g;
}

// modelo (x,y,z) -> three (x, z, -y)
const V = (p) => new THREE.Vector3(p[0], p[2], -p[1]);
const MAP = new THREE.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1);

export const LAYERS = [
  { id: 'entorno', name: 'Terreno y entorno', group: 'Obra gruesa' },
  { id: 'fundacion', name: 'Fundación (platea, EPS)', group: 'Obra gruesa' },
  { id: 'estructura', name: 'Estructura de madera', group: 'Obra gruesa' },
  { id: 'osb', name: 'Placas OSB', group: 'Obra gruesa' },
  { id: 'aislacion', name: 'Aislación lana de vidrio', group: 'Obra gruesa' },
  { id: 'revest_ext', name: 'Revestimiento exterior', group: 'Envolvente' },
  { id: 'techo', name: 'Cubierta (chapa, zinguería)', group: 'Envolvente' },
  { id: 'aberturas', name: 'Aberturas', group: 'Envolvente' },
  { id: 'durlock', name: 'Placas de yeso / cementicias', group: 'Interior' },
  { id: 'terminaciones', name: 'Pisos y cerámicos', group: 'Interior' },
  { id: 'escalera', name: 'Escalera y barandas', group: 'Interior' },
  { id: 'cocina', name: 'Cocina', group: 'Interior' },
  { id: 'bano', name: 'Baño', group: 'Interior' },
  { id: 'muebles', name: 'Muebles y cortinas', group: 'Interior' },
  { id: 'agua_fria', name: 'Agua fría', group: 'Instalaciones' },
  { id: 'agua_caliente', name: 'Agua caliente', group: 'Instalaciones' },
  { id: 'desague', name: 'Desagües cloacales', group: 'Instalaciones' },
  { id: 'ventilacion', name: 'Ventilación cloacal', group: 'Instalaciones' },
  { id: 'gas', name: 'Gas', group: 'Instalaciones' },
  { id: 'calefaccion', name: 'Calefactor tiro balanceado', group: 'Instalaciones' },
  { id: 'electrico', name: 'Cajas y cañerías eléctricas', group: 'Instalaciones' },
  { id: 'iluminacion', name: 'Luminarias, llaves y tomas', group: 'Instalaciones' },
];

const PRESETS = {
  exterior: { label: 'Exterior', off: ['aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico'], cam: [[-6.2, 4.2, 5.6], [2.2, 2.2, -1.6]] },
  servicios: { label: 'Pared de servicios (registros)', off: ['aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico'], cam: [[7.4, 3.0, -10.6], [2.1, 2.0, -2.0]] },
  interior: { label: 'Interior amoblado (sin techo)', off: ['techo', 'aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico'], clip: { axis: 'y', v: 4.2 }, cam: [[-2.4, 7.6, 3.6], [2.2, 2.4, -1.7]] },
  pb: { label: 'Planta baja (corte a 1,5 m)', off: ['techo', 'aislacion', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'estructura', 'osb'], clip: { axis: 'y', v: 1.5 }, cam: [[2.18, 8.5, 2.6], [2.18, 0, -1.68]] },
  pa: { label: 'Planta alta (corte a 1,4 m)', off: ['techo', 'aislacion', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'estructura', 'osb'], clip: { axis: 'y', v: 4.05 }, cam: [[2.18, 10.5, 2.4], [2.18, 2.6, -1.68]] },
  instalaciones: { label: 'Instalaciones (rayos X)', off: ['techo', 'aislacion', 'osb', 'muebles', 'terminaciones', 'revest_ext', 'entorno'], ghost: ['durlock', 'estructura', 'cocina', 'bano', 'escalera', 'aberturas', 'fundacion'], cam: [[6.8, 4.4, -7.4], [2.2, 1.4, -2.4]] },
  estructura: { label: 'Estructura', only: ['fundacion', 'estructura', 'entorno'], cam: [[-5.6, 5.2, 4.8], [2.2, 2.2, -1.7]] },
  placas: { label: 'Despiece OSB (exterior)', only: ['osb', 'fundacion', 'entorno'], panels: true, cam: [[-4.4, 5.8, 5.2], [2.2, 2.4, -1.7]] },
  yeso: { label: 'Despiece placas de yeso (interior)', only: ['durlock', 'fundacion', 'entorno'], panels: true, clip: { axis: 'y', v: 4.7 }, cam: [[-2.6, 8.2, 3.2], [2.2, 1.8, -1.7]] },
  escalera: { label: 'Escalera (corte lateral)', off: ['techo', 'aislacion', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico'], clip: { axis: 'z', v: 0.0 }, cam: [[1.6, 2.4, 4.6], [1.7, 1.75, -0.6]] },
  bano: { label: 'Baño', off: ['techo', 'aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico'], clip: { axis: 'y', v: 2.35 }, cam: [[3.3, 5.6, -0.6], [3.4, 0.6, -2.7]] },
};

function matFor(key, cache, opts = {}) {
  const k = key + (opts.shade !== undefined ? '#' + Math.round(opts.shade * 5) : '') + (opts.variant ?? '');
  if (cache[k]) return cache[k];
  const sp = SPECS[key] ?? { color: '#ff00ff' };
  const color = new THREE.Color(sp.color);
  if (opts.shade !== undefined) color.offsetHSL(0, 0, (opts.shade - 0.5) * 0.08);
  let m;
  const P = { color, roughness: 0.8, metalness: 0 };
  if (/chapa|zinguer|canaleta|zocalo_chapa|visera/.test(key)) Object.assign(P, { roughness: 0.62, metalness: 0.15 });
  if (/hierro_negro/.test(key)) Object.assign(P, { roughness: 0.5, metalness: 0.4 });
  if (/griferia|herrajes|bacha|accesorios/.test(key)) Object.assign(P, { roughness: 0.2, metalness: 0.9 });
  if (/porcelanato|ceramica|inodoro|lavatorio|plato/.test(key)) Object.assign(P, { roughness: 0.25 });
  if (/granito/.test(key)) Object.assign(P, { roughness: 0.3 });
  if (key === 'vidrio' || key === 'espejo') {
    m = new THREE.MeshPhysicalMaterial({ color, roughness: 0.03, metalness: 0, transparent: true, opacity: key === 'espejo' ? 0.95 : 0.28, envMapIntensity: 1.5, depthWrite: false });
  } else if (key === 'lana_150') {
    m = new THREE.MeshStandardMaterial({ ...P, transparent: true, opacity: 0.45, depthWrite: false });
  } else if (key === 'luminaria') {
    m = new THREE.MeshStandardMaterial({ ...P, emissive: new THREE.Color('#fff1c9'), emissiveIntensity: 0.4 });
  } else if (/chapa_muro|chapa_techo/.test(key)) {
    m = new THREE.MeshStandardMaterial({ ...P, side: THREE.DoubleSide });
  } else {
    const tm = TEXMAP[key];
    if (tm) {
      const [name, , maps, mix] = tm;
      if (maps.includes('d')) { P.map = tex(name, 'diffuse', true); P.color = new THREE.Color('#ffffff').lerp(color, mix); }
      if (maps.includes('n')) { P.normalMap = tex(name, 'nor_gl', false); P.normalScale = new THREE.Vector2(0.8, 0.8); }
      if (maps.includes('r')) { P.roughnessMap = tex(name, 'rough', false); P.roughness = 1; }
    }
    m = new THREE.MeshStandardMaterial(P);
    m.userData.texScale = tm?.[1];
    m.userData.texRot = tm?.[4];
  }
  cache[k] = m;
  return m;
}

// ---------------------------------------------------------------- geometrías
function geomBox(el) {
  const [x0, y0, z0] = el.min, [x1, y1, z1] = el.max;
  const g = new THREE.BoxGeometry(Math.max(x1 - x0, 1e-4), Math.max(z1 - z0, 1e-4), Math.max(y1 - y0, 1e-4));
  g.translate((x0 + x1) / 2, (z0 + z1) / 2, -(y0 + y1) / 2);
  return g;
}

function geomPrism(el) {
  let u = new THREE.Vector3(...el.u), v = new THREE.Vector3(...el.v), n = new THREE.Vector3(...el.n);
  let flip = 1;
  if (new THREE.Matrix3().set(u.x, v.x, n.x, u.y, v.y, n.y, u.z, v.z, n.z).determinant() < 0) { u = u.clone().negate(); flip = -1; }
  const shapes = [];
  for (const poly of el.poly) {
    const ring = poly[0].map(([a, b]) => new THREE.Vector2(a * flip, b));
    if (ring.length > 1 && ring[0].equals(ring[ring.length - 1])) ring.pop();
    const sh = new THREE.Shape(ring);
    for (let i = 1; i < poly.length; i++) {
      const h = poly[i].map(([a, b]) => new THREE.Vector2(a * flip, b));
      if (h[0].equals(h[h.length - 1])) h.pop();
      sh.holes.push(new THREE.Path(h));
    }
    shapes.push(sh);
  }
  const g = new THREE.ExtrudeGeometry(shapes, { depth: el.t, bevelEnabled: false, curveSegments: 4 });
  const B = new THREE.Matrix4().makeBasis(u, v, n).setPosition(new THREE.Vector3(...el.o));
  g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(MAP, B));
  return g;
}

function geomTube(el) {
  const parts = [];
  const pts = el.pts.map(V);
  for (let i = 0; i < pts.length - 1; i++) {
    const a = pts[i], b = pts[i + 1];
    const d = new THREE.Vector3().subVectors(b, a);
    const L = d.length();
    if (L < 1e-5) continue;
    const g = new THREE.CylinderGeometry(el.r, el.r, L, 10, 1, true);
    g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().normalize()));
    g.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2);
    parts.push(g.toNonIndexed());
  }
  for (let i = 0; i < pts.length; i++) {
    const s = new THREE.SphereGeometry(el.r * (i === 0 || i === pts.length - 1 ? 1.0 : 1.25), 10, 6);
    s.translate(pts[i].x, pts[i].y, pts[i].z);
    parts.push(s.toNonIndexed());
  }
  return mergeGeometries(parts);
}

function geomCyl(el) {
  if (!el.r || !el.h) return null;
  const g = new THREE.CylinderGeometry(el.r, el.r, el.h, el.r > 0.1 ? 32 : 16);
  const c = el.c;
  if (el.axis === 'z') g.translate(c[0], c[2] + el.h / 2, -c[1]);
  else if (el.axis === 'x') { g.rotateZ(-Math.PI / 2); g.translate(c[0] + el.h / 2, c[2], -c[1]); }
  else { g.rotateX(Math.PI / 2); g.translate(c[0], c[2], -(c[1] + el.h / 2)); }
  return g;
}

function profileT101(width, depth, period) {
  const pat = [[0, 0], [0.06, 0], [0.08, depth], [0.12, depth], [0.14, 0]].map(([a, b]) => [a * (period / 0.2), b]);
  const out = [];
  for (let base = 0; base < width + 1e-6; base += period) {
    for (const [a, b] of pat) {
      const s = base + a;
      if (s <= width + 1e-6) out.push([Math.min(s, width), b]);
    }
  }
  if (out[out.length - 1][0] < width - 1e-4) out.push([width, 0]);
  return out;
}

function geomRibbed(el) {
  const prof = profileT101(el.width, el.depth ?? 0.025, el.period ?? 0.2);
  const lens = el.lens;
  const lenAt = (s) => {
    const i = Math.min(lens.length - 2, Math.max(0, Math.floor((s / el.width) * (lens.length - 1))));
    const [s0, l0] = lens[i], [s1, l1] = lens[i + 1];
    const t = s1 > s0 ? (s - s0) / (s1 - s0) : 0;
    return l0 + (l1 - l0) * Math.min(1, Math.max(0, t));
  };
  const o = new THREE.Vector3(...el.o), u = new THREE.Vector3(...el.u), v = new THREE.Vector3(...el.v), n = new THREE.Vector3(...el.n);
  const P = (s, l, h) => o.clone().addScaledVector(u, s).addScaledVector(v, l).addScaledVector(n, h);
  const pos = [];
  for (let i = 0; i < prof.length - 1; i++) {
    const [s0, h0] = prof[i], [s1, h1] = prof[i + 1];
    const L0 = Math.max(0, lenAt(s0)), L1 = Math.max(0, lenAt(s1));
    const a = P(s0, 0, h0), b = P(s1, 0, h1), c = P(s1, L1, h1), d = P(s0, L0, h0);
    for (const q of [a, b, c, a, c, d]) pos.push(q.x, q.y, q.z);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.applyMatrix4(MAP);
  g.computeVertexNormals();
  return g;
}

export function geometryFor(el) {
  switch (el.kind) {
    case 'box': return geomBox(el);
    case 'prism': return geomPrism(el);
    case 'tube': return geomTube(el);
    case 'cyl': return geomCyl(el);
    case 'ribbed': return geomRibbed(el);
    case 'sphere': { const g = new THREE.SphereGeometry(el.r, 16, 12); g.scale(1, el.sy ?? 1, 1); const p = V(el.c); g.translate(p.x, p.y, p.z); return g; }
    default: return null;
  }
}

// ---------------------------------------------------------------- entorno
function rng(seed) {
  let s = seed;
  return () => ((s = (s * 16807) % 2147483647) - 1) / 2147483646;
}

function buildSurroundings(scene) {
  const g = new THREE.Group();
  g.name = 'surroundings';
  // césped real (Poly Haven) alrededor de la casa, con borde difuminado hacia el fondo fotográfico
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const ctx = c.getContext('2d');
  const gr = ctx.createRadialGradient(128, 128, 40, 128, 128, 128);
  gr.addColorStop(0, '#fff');
  gr.addColorStop(0.75, '#fff');
  gr.addColorStop(1, '#000');
  ctx.fillStyle = gr;
  ctx.fillRect(0, 0, 256, 256);
  const alpha = new THREE.CanvasTexture(c);
  const gd = tex('leafy_grass', 'diffuse', true), gn = tex('leafy_grass', 'nor_gl', false);
  for (const t of [gd, gn]) t.repeat.set(16, 16);
  const ground = new THREE.Mesh(new THREE.CircleGeometry(16, 64), new THREE.MeshStandardMaterial({ map: gd, normalMap: gn, color: '#b9c39a', roughness: 1, alphaMap: alpha, transparent: true, depthWrite: false }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.set(2.2, -0.149, -1.7);
  ground.receiveShadow = true;
  ground.renderOrder = -1;
  g.add(ground);
  // captador de sombras (sobre el suelo fotográfico)
  const sh = new THREE.Mesh(new THREE.CircleGeometry(30, 48), new THREE.ShadowMaterial({ opacity: 0.35 }));
  sh.rotation.x = -Math.PI / 2;
  sh.position.set(2.2, -0.148, -1.7);
  sh.receiveShadow = true;
  g.add(sh);
  scene.add(g);
  return g;
}

function skyTexture(top, bottom) {
  const c = document.createElement('canvas');
  c.width = 2; c.height = 256;
  const ctx = c.getContext('2d');
  const gr = ctx.createLinearGradient(0, 0, 0, 256);
  gr.addColorStop(0, top);
  gr.addColorStop(1, bottom);
  ctx.fillStyle = gr;
  ctx.fillRect(0, 0, 2, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// ---------------------------------------------------------------- visor
export function createViewer(container, model, opts = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;
  container.appendChild(renderer.domElement);
  const labelR = new CSS2DRenderer();
  labelR.domElement.className = 'labels';
  container.appendChild(labelR.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.45;
  // HDRI de montaña (Poly Haven "alps_field", CC0): iluminación + fondo proyectado sobre el suelo
  const ENV_ROT = -1.24;
  let skybox = null;
  try {
    const hdr = new RGBELoader().parse(b64buf(ASSETS.hdr));
    const dt = new THREE.DataTexture(hdr.data, hdr.width, hdr.height, THREE.RGBAFormat, hdr.type);
    dt.mapping = THREE.EquirectangularReflectionMapping;
    dt.colorSpace = THREE.LinearSRGBColorSpace;
    dt.needsUpdate = true;
    scene.environment = pmrem.fromEquirectangular(dt).texture;
    scene.environmentIntensity = 1.15;
    scene.environmentRotation = new THREE.Euler(0, ENV_ROT, 0);
    const bgt = new THREE.TextureLoader().load(ASSETS.bg);
    bgt.mapping = THREE.EquirectangularReflectionMapping;
    bgt.colorSpace = THREE.SRGBColorSpace;
    skybox = new GroundedSkybox(bgt, 9, 120);
    skybox.position.set(2.2, 9 - 0.15, -1.7);
    skybox.rotation.y = ENV_ROT;
    scene.add(skybox);
  } catch (e) { console.warn('HDRI', e); }
  const skies = {
    dia: skyTexture('#7fa7d6', '#dfe9f2'),
    tarde: skyTexture('#5a6fa0', '#f2b98a'),
    noche: skyTexture('#060b18', '#1d2a44'),
  };
  scene.background = skies.dia;
  scene.fog = null;

  const camera = new THREE.PerspectiveCamera(40, 1, 0.05, 600);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.maxPolarAngle = Math.PI * 0.495;

  const hemi = new THREE.HemisphereLight('#e2ecf7', '#5d5a48', 0.35);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff1dc', 2.6);
  // dirección del sol de la foto (u 0,60 / v 0,26 del equirectangular), rotada igual que el fondo
  const sd = new THREE.Vector3(0.59, 0.685, 0.43).applyAxisAngle(new THREE.Vector3(0, 1, 0), ENV_ROT);
  const SUN_DAY = sd.clone().multiplyScalar(18).add(new THREE.Vector3(2.2, 0, -1.7));
  sun.position.copy(SUN_DAY);
  sun.target.position.set(2.2, 1.5, -1.7);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 50 });
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.045;
  scene.add(sun, sun.target);
  const surroundings = buildSurroundings(scene);

  // ---------------- construir mallas
  const cache = {};
  const groups = {};
  for (const L of LAYERS) {
    const g = new THREE.Group();
    g.name = L.id;
    groups[L.id] = g;
    scene.add(g);
  }
  const meshes = [];
  const lightPts = [];
  for (const el of model.elements) {
    if (el.kind === 'none' || !el.layer) continue;
    let geo;
    try { geo = geometryFor(el); } catch (e) { console.warn('geom', el.id, e); continue; }
    if (!geo) continue;
    const mat = matFor(el.paint ?? el.mat, cache, { shade: el.shade });
    if (mat.userData.texScale) geo = worldUV(geo, mat.userData.texScale, mat.userData.texRot);
    const mesh = new THREE.Mesh(geo, mat);
    mesh.userData.el = el;
    mesh.userData.baseMat = mat;
    const transparent = mat.transparent;
    mesh.castShadow = !transparent && el.layer !== 'electrico';
    mesh.receiveShadow = !transparent;
    (groups[el.layer] ?? scene).add(mesh);
    meshes.push(mesh);
    if (el.emissive && el.mat === 'luminaria') {
      const b = new THREE.Box3().setFromObject(mesh);
      lightPts.push(b.getCenter(new THREE.Vector3()));
    }
  }
  // muebles de catálogo (glTF embebidos)
  const loader = new GLTFLoader();
  const glbCache = {};
  for (const el of model.elements.filter((e) => e.kind === 'glb')) {
    const holder = new THREE.Group();
    holder.position.copy(V(el.pos));
    holder.rotation.y = el.rotY;
    holder.scale.set(...el.scale);
    (groups[el.layer] ?? scene).add(holder);
    if (el.layer === 'iluminacion') lightPts.push(V([el.pos[0], el.pos[1], el.pos[2] + 0.3]));
    const data = ASSETS.glb[el.model];
    if (!data) continue;
    glbCache[el.model] ??= new Promise((res, rej) => loader.parse(b64buf(data), '', res, rej));
    glbCache[el.model].then((g) => {
      const o = g.scene.clone(true);
      o.traverse((m) => {
        if (!m.isMesh) return;
        m.castShadow = m.receiveShadow = true;
        m.userData.el = el;
        m.userData.baseMat = m.material;
        meshes.push(m);
      });
      holder.add(o);
      refreshMaterials();
    }).catch((e) => console.warn('glb', el.model, e));
  }
  // luces interiores (modo noche)
  const nightLights = new THREE.Group();
  for (const p of lightPts) {
    const l = new THREE.PointLight('#ffd9a0', 0, 6, 1.6);
    l.position.copy(p).add(new THREE.Vector3(0, -0.12, 0));
    nightLights.add(l);
  }
  scene.add(nightLights);

  // ---------------- etiquetas de placas
  const labelGroup = new THREE.Group();
  labelGroup.visible = false;
  scene.add(labelGroup);
  const panelColors = {};
  const pal = ['#e9c46a', '#8ecae6', '#b5e48c', '#f4a261', '#cdb4db', '#ffafcc', '#90dbf4', '#ffd6a5', '#caffbf', '#bde0fe', '#fdffb6', '#a0c4ff'];
  let pi = 0;
  for (const m of meshes) {
    const el = m.userData.el;
    if (!el.panel) continue;
    panelColors[el.panel] = matFor(el.mat, cache, { variant: '#p' + (pi % pal.length) });
    panelColors[el.panel] = new THREE.MeshStandardMaterial({ color: pal[pi % pal.length], roughness: 0.85 });
    pi++;
    const b = new THREE.Box3().setFromObject(m);
    const div = document.createElement('div');
    div.className = 'plabel';
    div.textContent = el.panel;
    const lab = new CSS2DObject(div);
    lab.position.copy(b.getCenter(new THREE.Vector3()));
    lab.userData.layer = el.layer;
    lab.userData.mesh = m;
    const nv = V(el.n).sub(V([0, 0, 0])).normalize();
    lab.userData.nrm = el.layer === 'durlock' ? nv.negate() : nv;
    labelGroup.add(lab);
  }

  // ---------------- estado
  const state = { preset: 'exterior', ghost: new Set(), panels: false, clip: null, mode: 'dia' };
  const clipPlane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 100);
  const ghostCache = {};
  const ghostMat = (m) => {
    if (!ghostCache[m.uuid]) {
      const g = m.clone();
      g.transparent = true;
      g.opacity = 0.12;
      g.depthWrite = false;
      ghostCache[m.uuid] = g;
    }
    return ghostCache[m.uuid];
  };
  function refreshMaterials() {
    for (const m of meshes) {
      const el = m.userData.el;
      let mat = m.userData.baseMat;
      if (state.panels && el.panel) mat = panelColors[el.panel];
      if (state.ghost.has(el.layer)) mat = ghostMat(mat);
      if (m.userData.selected) {
        mat = mat.clone();
        mat.emissive = new THREE.Color('#ff5a1f');
        mat.emissiveIntensity = 0.55;
      }
      m.material = mat;
    }
    labelGroup.visible = state.panels;
    updateLabels();
  }
  const occ = new THREE.Raycaster();
  function updateLabels() {
    if (!state.panels) return;
    const panelMeshes = meshes.filter((m) => m.userData.el.panel && m.parent.visible);
    const cp = camera.position;
    for (const l of labelGroup.children) {
      let vis = groups[l.userData.layer].visible;
      if (vis && state.clip && clipPlane.distanceToPoint(l.position) < 0) vis = false;
      const to = new THREE.Vector3().subVectors(cp, l.position);
      if (vis && l.userData.nrm.dot(to) <= 0) vis = false;
      if (vis) {
        const d = to.length();
        occ.set(cp, to.clone().negate().normalize());
        occ.far = d - 0.03;
        const hit = occ.intersectObjects(panelMeshes, false).find((h) => !state.clip || clipPlane.distanceToPoint(h.point) >= 0);
        if (hit && hit.object !== l.userData.mesh) vis = false;
      }
      l.visible = vis;
    }
  }
  let lblT = 0;
  controls.addEventListener('change', () => { if (!state.panels) return; clearTimeout(lblT); lblT = setTimeout(updateLabels, 120); });
  function setClip(c) {
    state.clip = c;
    if (!c) { renderer.clippingPlanes = []; return; }
    if (c.axis === 'y') clipPlane.set(new THREE.Vector3(0, -1, 0), c.v);
    if (c.axis === 'x') clipPlane.set(new THREE.Vector3(c.flip ? -1 : 1, 0, 0), c.flip ? c.v : -c.v);
    if (c.axis === 'z') clipPlane.set(new THREE.Vector3(0, 0, c.flip ? 1 : -1), c.flip ? -c.v : c.v);
    renderer.clippingPlanes = [clipPlane];
  }
  function setLayer(id, on) { groups[id].visible = on; refreshMaterials(); opts.onChange?.(); }
  function applyPreset(name, moveCam = true) {
    const p = PRESETS[name];
    state.preset = name;
    for (const L of LAYERS) groups[L.id].visible = p.only ? p.only.includes(L.id) : !(p.off ?? []).includes(L.id);
    state.ghost = new Set(p.ghost ?? []);
    for (const id of state.ghost) groups[id].visible = true;
    state.panels = !!p.panels;
    setClip(p.clip ?? null);
    surroundings.visible = !p.only || p.only.includes('entorno');
    if (skybox) skybox.visible = surroundings.visible && state.mode !== 'noche';
    scene.background = skybox?.visible ? null : skies[state.mode];
    refreshMaterials();
    if (moveCam && p.cam) flyTo(p.cam[0], p.cam[1]);
    opts.onChange?.();
  }
  let fly = null;
  function flyTo(pos, target) {
    fly = { p0: camera.position.clone(), t0: controls.target.clone(), p1: new THREE.Vector3(...pos), t1: new THREE.Vector3(...target), k: 0 };
  }
  function setMode(mode) {
    state.mode = mode;
    const night = mode === 'noche', dusk = mode === 'tarde';
    if (skybox) skybox.visible = !night && surroundings.visible;
    scene.background = skybox && !night ? null : skies[mode];
    sun.intensity = night ? 0.03 : dusk ? 1.4 : 2.6;
    sun.color.set(dusk ? '#ffb070' : '#fff1dc');
    if (dusk) sun.position.set(2.2 + 14, 4, -1.7 + 8); else sun.position.copy(SUN_DAY);
    hemi.intensity = night ? 0.04 : 0.35;
    scene.environmentIntensity = night ? 0.03 : dusk ? 0.5 : 1.15;
    renderer.toneMappingExposure = night ? 1.1 : 1.12;
    for (const l of nightLights.children) l.intensity = night ? 2.2 : dusk ? 0.8 : 0;
    for (const k of Object.keys(cache)) if (k.startsWith('luminaria')) cache[k].emissiveIntensity = night ? 3 : dusk ? 1.2 : 0.4;
  }

  // ---------------- interacción
  const ray = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  const tip = document.createElement('div');
  tip.className = 'tip';
  container.appendChild(tip);
  let hovered = null, selected = null;
  function pick(ev) {
    const r = renderer.domElement.getBoundingClientRect();
    mouse.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(mouse, camera);
    const shown = (o) => { for (let q = o; q; q = q.parent) if (!q.visible) return false; return true; };
    const vis = meshes.filter((m) => shown(m) && !state.ghost.has(m.userData.el.layer));
    const hits = ray.intersectObjects(vis, false).filter((h) => !state.clip || clipPlane.distanceToPoint(h.point) >= -1e-4);
    return hits[0]?.object ?? null;
  }
  let lastMove = 0;
  renderer.domElement.addEventListener('pointermove', (ev) => {
    const now = performance.now();
    if (now - lastMove < 40) return;
    lastMove = now;
    const o = pick(ev);
    hovered = o;
    if (!o) { tip.style.display = 'none'; return; }
    const el = o.userData.el;
    tip.innerHTML = `<b>${esc(el.name ?? el.id)}</b><br><span>${esc(SPECS[el.mat]?.nombre ?? el.mat)}</span>`;
    const r = container.getBoundingClientRect();
    tip.style.left = ev.clientX - r.left + 14 + 'px';
    tip.style.top = ev.clientY - r.top + 14 + 'px';
    tip.style.display = 'block';
  });
  renderer.domElement.addEventListener('pointerleave', () => { tip.style.display = 'none'; });
  let down = null;
  renderer.domElement.addEventListener('pointerdown', (ev) => { down = [ev.clientX, ev.clientY]; });
  renderer.domElement.addEventListener('pointerup', (ev) => {
    if (!down || Math.hypot(ev.clientX - down[0], ev.clientY - down[1]) > 4) return;
    const o = pick(ev);
    if (selected) selected.userData.selected = false;
    selected = o;
    if (o) o.userData.selected = true;
    refreshMaterials();
    opts.onSelect?.(o ? o.userData.el : null);
  });

  // oclusión ambiental (GTAO) para un render más realista
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const gtao = new GTAOPass(scene, camera, 800, 600);
  gtao.updateGtaoMaterial({ radius: 0.35, distanceExponent: 1, thickness: 1, scale: 1 });
  gtao.blendIntensity = 0.85;
  composer.addPass(gtao);
  composer.addPass(new OutputPass());
  state.hq = opts.hq ?? true;
  function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    renderer.setSize(w, h);
    composer.setSize(w, h);
    labelR.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container);
  resize();

  let running = true;
  function loop() {
    if (!running) return;
    requestAnimationFrame(loop);
    if (fly) {
      fly.k = Math.min(1, fly.k + 0.035);
      const t = fly.k < 0.5 ? 2 * fly.k * fly.k : 1 - Math.pow(-2 * fly.k + 2, 2) / 2;
      camera.position.lerpVectors(fly.p0, fly.p1, t);
      controls.target.lerpVectors(fly.t0, fly.t1, t);
      if (fly.k >= 1) fly = null;
    }
    controls.update();
    if (state.hq) composer.render(); else renderer.render(scene, camera);
    if (labelGroup.visible) labelR.render(scene, camera);
  }
  camera.position.set(...PRESETS.exterior.cam[0]);
  controls.target.set(...PRESETS.exterior.cam[1]);
  applyPreset('exterior', false);
  loop();

  // vista ortográfica para fachadas/cortes (captura a imagen)
  function orthoShot({ dir, center, size, clip, layersOff = [], w = 1400, h = 1000, only, night = false }) {
    const prev = { vis: Object.fromEntries(LAYERS.map((L) => [L.id, groups[L.id].visible])), clip: state.clip, sur: surroundings.visible, mode: state.mode, panels: state.panels, ghost: state.ghost };
    for (const L of LAYERS) groups[L.id].visible = only ? only.includes(L.id) : !layersOff.includes(L.id);
    surroundings.visible = false;
    if (skybox) skybox.visible = false;
    state.ghost = new Set();
    state.panels = false;
    refreshMaterials();
    setClip(clip ?? null);
    const bg = scene.background, fog = scene.fog;
    scene.background = new THREE.Color('#ffffff');
    scene.fog = null;
    if (night) { setMode('noche'); scene.background = new THREE.Color('#1a2233'); }
    const hemiI = hemi.intensity;
    if (!night) hemi.intensity = 1.5;
    const asp = w / h;
    const cam = new THREE.OrthographicCamera((-size * asp) / 2, (size * asp) / 2, size / 2, -size / 2, 0.1, 100);
    const c = new THREE.Vector3(...center);
    cam.position.copy(c).add(new THREE.Vector3(...dir).multiplyScalar(30));
    cam.lookAt(c);
    const oldSize = new THREE.Vector2();
    renderer.getSize(oldSize);
    renderer.setSize(w, h, false);
    renderer.render(scene, cam);
    const url = renderer.domElement.toDataURL('image/png');
    renderer.setSize(oldSize.x, oldSize.y, false);
    hemi.intensity = hemiI;
    scene.background = bg;
    scene.fog = fog;
    for (const L of LAYERS) groups[L.id].visible = prev.vis[L.id];
    surroundings.visible = prev.sur;
    if (skybox) skybox.visible = prev.sur && prev.mode !== 'noche';
    state.ghost = prev.ghost;
    state.panels = prev.panels;
    setClip(prev.clip);
    setMode(prev.mode);
    refreshMaterials();
    resize();
    return url;
  }

  function shot() {
    renderer.render(scene, camera);
    return renderer.domElement.toDataURL('image/png');
  }

  const setHQ = (v) => { state.hq = v; };
  return {
    setHQ, applyPreset, setLayer, setClip, setMode, flyTo, orthoShot, shot, groups, state, PRESETS,
    isLayerOn: (id) => groups[id].visible,
    setRunning: (r) => { const was = running; running = r; if (r && !was) loop(); },
    camera, controls, refreshMaterials,
  };
}

function esc(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
}

export { PRESETS };
