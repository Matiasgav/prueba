// Aplicación: visor 3D + planos + cómputo + despiece + memoria, todo desde el mismo modelo.
import { buildModel, CIRC, WALLS } from './model.js';
import { takeoff, areas, SHEETS } from './takeoff.js';
import { createViewer, LAYERS, PRESETS } from './viewer.js';
import { planArq, planElec, planAgua, planGas, servicesWall, planEstructura, wallFraming, faceMap, sheetSvg, unifilar } from './plans.js';
import { SPECS, PALETA } from './specs.js';
import { MEMORIA_HTML } from './memoria.gen.js';
import { analyze, studySvg } from './studies.js';

const $ = (s, r = document) => r.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const nf = (n, d = 2) => Number(n).toLocaleString('es-AR', { maximumFractionDigits: d, minimumFractionDigits: 0 });

const model = buildModel();
const T = takeoff(model);
const A = areas(model.D);
window.__casa = { model, T, A };

// ------------------------------------------------------------------ cabecera / pestañas
$('#kpis').innerHTML = [
  ['Sup. cubierta', `${nf(A.cubiertaTotal)} m²`, `${nf(A.cubiertaPorPlanta)} m² por planta`],
  ['Sup. útil', `${nf(A.utilPB + A.utilPA)} m²`, `PB ${nf(A.utilPB)} · PA ${nf(A.utilPA)}`],
  ['Exterior', `${nf(model.D.ext.L)} x ${nf(model.D.ext.W)} m`, '2 plantas · techo 2 aguas 30°'],
  ['Placas de yeso', `${T.sheets.durlock_std.length + (T.sheets.durlock_rh?.length ?? 0)}`, `+ ${T.sheets.cementicia?.length ?? 0} cementicias`],
  ['Placas OSB', `${T.sheets.osb_11.length + T.sheets.osb_18.length}`, `${T.sheets.osb_11.length} de 11 mm + ${T.sheets.osb_18.length} de 18 mm`],
].map(([a, b, c]) => `<div class="kpi"><span>${a}</span><b>${b}</b><small>${c}</small></div>`).join('');

const tabs = [...document.querySelectorAll('.tabs button')];
let viewer = null;
function showTab(id) {
  for (const b of tabs) b.classList.toggle('on', b.dataset.tab === id);
  for (const p of document.querySelectorAll('.pane')) p.hidden = p.id !== 'pane-' + id;
  viewer?.setRunning(id === '3d');
  if (id === 'planos') renderPlanos();
  if (id === 'despiece') renderDespiece();
  if (id === 'computo') renderComputo();
  if (id === 'estudio') renderEstudio();
  try { localStorage.setItem('casa.tab', id); } catch {}
}
for (const b of tabs) b.addEventListener('click', () => showTab(b.dataset.tab));

// ------------------------------------------------------------------ 3D
function initViewer() {
  const info = $('#info');
  viewer = createViewer($('#view'), model, {
    onSelect: (el) => {
      if (!el) { info.innerHTML = '<p class="muted">Hacé clic en cualquier pieza para ver su material y medidas.</p>'; return; }
      const sp = SPECS[el.mat];
      const crit = sp?.criterio ? `<span class="crit ${sp.criterio}">${sp.criterio}</span>` : '';
      info.innerHTML = `<h4>${esc(el.name ?? el.id)}</h4>${crit}<p>${esc(sp?.nombre ?? el.mat)}</p>${el.info ? `<p class="muted">${esc(el.info)}</p>` : ''}${el.member ? `<p class="muted">Pieza de madera ${esc(el.member.sec)} · L = ${nf(el.member.len * 100, 1)} cm · ${esc(el.member.use)}</p>` : ''}<p class="muted">Capa: ${esc(LAYERS.find((l) => l.id === el.layer)?.name ?? el.layer)}${el.id ? ' · ID ' + esc(el.id) : ''}</p>`;
    },
    onChange: syncLayerUI,
  });
  // presets
  $('#presets').innerHTML = Object.entries(PRESETS).map(([k, p]) => `<button data-p="${k}">${esc(p.label)}</button>`).join('');
  $('#presets').addEventListener('click', (e) => {
    const k = e.target.dataset.p;
    if (!k) return;
    viewer.applyPreset(k);
    for (const b of $('#presets').children) b.classList.toggle('on', b.dataset.p === k);
    syncClipUI();
  });
  // capas
  const groups = {};
  for (const L of LAYERS) (groups[L.group] ??= []).push(L);
  $('#layers').innerHTML = Object.entries(groups).map(([g, ls]) => `<fieldset><legend>${g}</legend>${ls.map((L) => `<label><input type="checkbox" data-l="${L.id}"> ${esc(L.name)}</label>`).join('')}</fieldset>`).join('');
  $('#layers').addEventListener('change', (e) => { const id = e.target.dataset.l; if (id) viewer.setLayer(id, e.target.checked); });
  // ambiente
  $('#ambiente').addEventListener('change', (e) => viewer.setMode(e.target.value));
  // corte
  const clipAxis = $('#clipAxis'), clipV = $('#clipV'), clipOut = $('#clipOut');
  const ranges = { none: [0, 1, 0], y: [0.2, 6.5, 1.5], x: [-0.4, 4.8, 2.0], z: [-3.8, 0.4, -1.6] };
  function applyClip() {
    const a = clipAxis.value;
    if (a === 'none') { viewer.setClip(null); clipOut.textContent = ''; return; }
    const v = +clipV.value;
    viewer.setClip({ axis: a, v });
    clipOut.textContent = a === 'y' ? `altura ${nf(v)} m` : a === 'x' ? `x = ${nf(v)} m (desde el frente)` : `y = ${nf(-v)} m (desde lateral izq.)`;
  }
  clipAxis.addEventListener('change', () => {
    const [mn, mx, d] = ranges[clipAxis.value];
    Object.assign(clipV, { min: mn, max: mx, step: 0.01, value: d });
    applyClip();
  });
  clipV.addEventListener('input', applyClip);
  function syncClipUI() {
    const c = viewer.state.clip;
    clipAxis.value = c ? c.axis : 'none';
    if (c) { const [mn, mx] = ranges[c.axis]; Object.assign(clipV, { min: mn, max: mx, step: 0.01 }); clipV.value = c.v; }
    clipOut.textContent = c ? (c.axis === 'y' ? `altura ${nf(c.v)} m` : '') : '';
  }
  $('#hq').addEventListener('change', (e) => viewer.setHQ(e.target.checked));
  $('#shot').addEventListener('click', () => {
    const a = document.createElement('a');
    a.href = viewer.shot();
    a.download = 'casa-bariloche-render.png';
    a.click();
  });
  syncLayerUI();
  for (const b of $('#presets').children) b.classList.toggle('on', b.dataset.p === 'exterior');
}
function syncLayerUI() {
  if (!viewer) return;
  for (const i of document.querySelectorAll('#layers input')) i.checked = viewer.isLayerOn(i.dataset.l);
}

// ------------------------------------------------------------------ Planos
let planosDone = false;
function card(title, svg, file, note = '') {
  const id = 'd' + Math.random().toString(36).slice(2, 8);
  return `<section class="card"><header><h3>${esc(title)}</h3><a download="${file}" href="data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}" class="dl">SVG</a></header>${note ? `<p class="muted">${note}</p>` : ''}<div class="draw" id="${id}">${svg}</div></section>`;
}
function renderPlanos() {
  if (planosDone) return;
  planosDone = true;
  const m = model;
  let h = '';
  h += `<nav class="toc">${['Arquitectura', 'Fachadas y cortes', 'Electricidad', 'Sanitaria', 'Gas', 'Pared de servicios', 'Estructura', 'Entramados'].map((t) => `<a href="#pl-${t.split(' ')[0]}">${t}</a>`).join('')}</nav>`;
  h += `<h2 id="pl-Arquitectura">Arquitectura</h2><div class="grid2">${card('Planta baja', planArq(m, 'PB'), 'planta-baja.svg')}${card('Planta alta', planArq(m, 'PA'), 'planta-alta.svg')}</div>`;
  h += `<h2 id="pl-Fachadas">Fachadas y cortes (render ortográfico del modelo 3D)</h2><div class="grid2" id="ortho"><p class="muted">Generando vistas…</p></div>`;
  h += `<h2 id="pl-Electricidad">Instalación eléctrica</h2><div class="grid2">${card('Eléctrico PB', planElec(m, 'PB'), 'electrico-pb.svg')}${card('Eléctrico PA', planElec(m, 'PA'), 'electrico-pa.svg')}</div>${card('Unifilar', unifilar(), 'unifilar.svg')}${elecTable()}${segTable()}${rulesTable()}`;
  h += `<h2 id="pl-Sanitaria">Instalación sanitaria</h2>${card('Agua y desagües', planAgua(m), 'sanitaria.svg')}`;
  h += `<h2 id="pl-Gas">Gas</h2>${card('Gas', planGas(m), 'gas.svg')}`;
  h += `<h2 id="pl-Pared">Pared de servicios</h2>${card('Pared de servicios (vista exterior sin registros)', servicesWall(m), 'pared-servicios.svg', 'El corazón del concepto: retirás un registro atornillado y tenés a la vista llaves de paso, uniones y conexiones.')}`;
  h += `<h2 id="pl-Estructura">Estructura</h2><div class="grid2">${card('Fundación y pases', planEstructura(m, 'fund'), 'fundacion.svg')}${card('Entrepiso', planEstructura(m, 'entrepiso'), 'entrepiso.svg')}</div>${card('Techo', planEstructura(m, 'techo'), 'techo.svg')}`;
  h += `<h2 id="pl-Entramados">Entramados de muros</h2><div class="grid2">${WALLS.map((w) => card(w.name, wallFraming(m, w.id), `entramado-${w.id}.svg`)).join('')}</div>`;
  $('#pane-planos').innerHTML = h;
  setTimeout(renderOrtho, 30);
}
function elecTable() {
  const rows = model.elec.boxes.map((b) => `<tr><td><b>${b.id}</b></td><td>${b.tipo === 'oct' ? 'octogonal' : 'rect. 5x10'}</td><td>${b.circuito}</td><td>${b.nivel}</td><td>${b.tipo === 'oct' ? 'techo' : nf(b.alturaPiso * 100, 0) + ' cm'}</td><td>${esc(b.desc)}</td></tr>`).join('');
  return `<details class="card"><summary>Planilla de cajas eléctricas (${model.elec.boxes.length})</summary><table class="t"><thead><tr><th>ID</th><th>Caja</th><th>Circuito</th><th>Nivel</th><th>Altura</th><th>Uso</th></tr></thead><tbody>${rows}</tbody></table></details>`;
}
function segTable() {
  const rows = model.elec.conduits.map((c) => `<tr><td><b>${c.n || '—'}</b></td><td>${esc(c.circuito)}</td><td>${esc(c.from)} → ${esc(c.to)}</td><td class="n">${nf(c.len)}</td><td class="n">${c.curves}</td><td>${esc(c.rs)}</td><td>${c.cables.map((k) => `${k.sec ? nf(k.sec) + ' mm² ' : ''}${esc(k.desc)} <span class="muted">(${esc(k.color)})</span>`).join('<br>')}</td></tr>`).join('');
  return `<details class="card" open><summary>Planilla de tramos de cañería y conductores (${model.elec.conduits.length})</summary><p class="muted small">Cada tramo es un caño de acero entre dos cajas. Conductores IRAM NM 247-3. Colores AEA: fase marrón, neutro celeste, protección verde-amarillo, retornos negro, viajeros de combinación gris.</p><div class="scroll"><table class="t"><thead><tr><th>Tramo</th><th>Circ.</th><th>Desde → hasta</th><th class="n">Long. (m)</th><th class="n">Curvas</th><th>Caño</th><th>Cables que lleva</th></tr></thead><tbody>${rows}</tbody></table></div></details>`;
}
function rulesTable() {
  const rows = model.elec.rules.map((r) => `<tr><td>${r.pass ? '<span class="crit DURABLE">CUMPLE</span>' : '<span class="crit ECONOMICO">REVISAR</span>'}</td><td>${esc(r.rule)}</td><td>${esc(r.detail)}</td></tr>`).join('');
  return `<details class="card" open><summary>Verificación automática — AEA 90364-7-770</summary><table class="t"><thead><tr><th></th><th>Regla</th><th>Resultado en el proyecto</th></tr></thead><tbody>${rows}</tbody></table></details>`;
}
let estudioDone = false;
function renderEstudio() {
  if (estudioDone) return;
  estudioDone = true;
  const res = analyze();
  const col = (w) => (w >= 0.8 ? 'DURABLE' : w >= 0.6 ? 'ESTANDAR' : 'ECONOMICO');
  const routes = res[0].routes.map((r) => r.name);
  const head = `<tr><th>Recorrido (ancho libre mínimo del mejor camino)</th>${res.map((r) => `<th>${esc(r.name.split(' — ')[0])}</th>`).join('')}</tr>`;
  const body = routes.map((name) => `<tr><td>${esc(name)}</td>${res.map((r) => { const q = r.routes.find((x) => x.name === name); return `<td>${q ? `<span class="crit ${col(q.w)}">${nf(q.w)} m</span>` : '—'}</td>`; }).join('')}</tr>`).join('');
  const extra = [
    ['Sillas para comer', (r) => r.seatsDining], ['Asientos de estar', (r) => r.seatsLiving],
    ['¿Se come en el sillón?', (r) => (r.eatOnSofa ? 'sí ✗' : 'no ✓')], ['¿El sillón mira al TV?', (r) => (r.sofaFacesTv ? 'sí ✓' : 'no ✗')],
    ['¿La entrada cruza el estar?', (r) => (r.crossesLiving ? 'sí ✗' : 'no ✓')],
  ].map(([t, f]) => `<tr><td>${t}</td>${res.map((r) => `<td>${f(r)}</td>`).join('')}</tr>`).join('');
  $('#pane-estudio').innerHTML = `<div class="memo"><h2>Estudio de disposición de la planta baja</h2>
  <p>Antes de detallar, se compararon alternativas de ubicación de muebles y de acceso con un análisis de circulación: el plano se discretiza en una grilla de 2,5 cm, se calcula para cada punto libre la distancia al obstáculo más cercano (muros, escalera, mesada, muebles) y, para cada recorrido de uso diario, el <b>ancho libre mínimo</b> del mejor camino posible. Referencias de diseño: pasos de 0,80–0,90 m para circulación principal y 0,60 m entre muebles (valores habituales de Neufert, <i>Arte de proyectar en arquitectura</i>, y Panero y Zelnik, <i>Las dimensiones humanas en los espacios interiores</i>).</p>
  <p><span class="crit DURABLE">≥ 0,80</span> cómodo · <span class="crit ESTANDAR">0,60–0,80</span> estrecho · <span class="crit ECONOMICO">&lt; 0,60</span> incómodo o bloqueado (con la silla ocupada o el mueble en uso).</p>
  <div class="scroll"><table class="t">${head}${body}${extra}</table></div>
  <div class="grid3">${res.map((r) => `<section class="card"><h3>${esc(r.name)}</h3><p class="muted small">${esc(r.resumen)}</p><div class="draw">${studySvg(r)}</div></section>`).join('')}</div>
  <h3>Conclusión</h3>
  <ul><li>La <b>versión 1</b> no funcionaba: para ir de la entrada a la escalera o al baño había que pasar por 17 cm entre la mesa y el tabique, se comía en el banco-sofá y había una sola silla.</li>
  <li>Poner un sillón contra la escalera y la mesa en el medio (<b>B</b>) bloquea la cocina: el planta baja tiene 14,6 m² y la franja libre entre escalera y mesada es de sólo 1,0 m.</li>
  <li>La <b>alternativa C</b> resuelve con tres decisiones: entrar por el hall (junto a la escalera y el baño, así el estar-comedor queda sin paso cruzado), usar el nicho de 1,90 m de alto bajo los escalones compensados para el sillón (espacio que antes se perdía) y poner la mesa con dos sillas contra el ventanal, mirando la vista. Todas las circulaciones principales quedan entre 0,77 y 1,02 m.</li>
  <li>Punto ajustado que queda: con alguien sentado en la segunda silla, el paso entre la silla y la mesada es de 0,47 m. Se acepta para 1–2 personas (cuando se cocina, la silla se empuja bajo la mesa).</li>
  <li>Planta alta: con el pedido de “una cama doble o dos simples” se pasó de 3 plazas a <b>dos camas de 1 plaza que se unen (160x190)</b>: sirven a una pareja o a dos personas, liberan lugar para dos mesas de luz y dejan 0,76 m de paso a cada lado.</li></ul></div>`;
}
function renderOrtho() {
  if (!viewer) return;
  const D = model.D;
  const cx = D.Li / 2, cy = -D.Wi / 2;
  const views = [
    ['Fachada frente (acceso)', { dir: [-1, 0, 0], center: [cx, 3.0, cy], size: 7.6, layersOff: ['aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'entorno'] }],
    ['Fachada fondo', { dir: [1, 0, 0], center: [cx, 3.0, cy], size: 7.6, layersOff: ['aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'entorno'] }],
    ['Lateral pared de servicios (registros R1–R4)', { dir: [0, 0, -1], center: [cx, 3.0, cy], size: 7.6, layersOff: ['aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'entorno'] }],
    ['Lateral izquierdo (ciego)', { dir: [0, 0, 1], center: [cx, 3.0, cy], size: 7.6, layersOff: ['aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'entorno'] }],
    ['Corte A-A longitudinal (mirando a servicios)', { dir: [0, 0, 1], center: [cx, 3.0, cy], size: 7.6, clip: { axis: 'z', v: -1.6 }, layersOff: ['aislacion', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'entorno'] }],
    ['Corte B-B transversal (mirando al frente)', { dir: [1, 0, 0], center: [cx, 3.0, cy], size: 7.6, clip: { axis: 'x', v: 3.0, flip: true }, layersOff: ['aislacion', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'entorno'] }],
    ['Corte A-A — instalaciones sin placas (pared de servicios desde adentro)', { dir: [0, 0, 1], center: [cx, 2.6, cy], size: 7.0, clip: { axis: 'z', v: -1.6 }, layersOff: ['aislacion', 'durlock', 'muebles', 'terminaciones', 'entorno', 'escalera'] }],
    ['Atardecer (render)', { dir: [-0.8, 0.35, 0.6], center: [cx, 2.6, cy], size: 8.5, layersOff: ['aislacion', 'estructura', 'osb', 'agua_fria', 'agua_caliente', 'desague', 'ventilacion', 'gas', 'electrico', 'entorno'], night: true }],
  ];
  $('#ortho').innerHTML = views.map(([t, v]) => `<section class="card"><header><h3>${esc(t)}</h3></header><img alt="${esc(t)}" src="${viewer.orthoShot(v)}"></section>`).join('');
}

// ------------------------------------------------------------------ Cómputo
let precios = {};
try { precios = JSON.parse(localStorage.getItem('casa.precios') || '{}'); } catch {}
function renderComputo() {
  const caps = {};
  T.rows.forEach((r, i) => (caps[r.cap] ??= []).push({ ...r, i }));
  const key = (r) => `${r.cap}|${r.item}`;
  let total = 0;
  const body = Object.entries(caps).map(([cap, rs]) => {
    let sub = 0;
    const trs = rs.map((r) => {
      const p = +precios[key(r)] || 0;
      const t = p * r.cant;
      sub += t;
      return `<tr><td>${esc(r.item)}${r.detalle ? `<div class="muted small">${esc(r.detalle)}</div>` : ''}</td><td class="n">${nf(r.cant)}</td><td>${esc(r.unidad)}</td><td>${r.criterio ? `<span class="crit ${r.criterio}">${r.criterio}</span>` : ''}</td><td><input class="pu" data-k="${esc(key(r))}" value="${p || ''}" placeholder="0" inputmode="decimal"></td><td class="n">${t ? nf(t, 0) : ''}</td></tr>`;
    }).join('');
    total += sub;
    return `<tbody><tr class="cap"><th colspan="5">${esc(cap)}</th><th class="n">${sub ? nf(sub, 0) : ''}</th></tr>${trs}</tbody>`;
  }).join('');
  $('#pane-computo').innerHTML = `<div class="card"><header><h3>Cómputo de materiales</h3><button id="csv">Descargar CSV</button></header>
  <p class="muted">Cantidades calculadas desde el modelo 3D (no estimadas a ojo). Cargá precios unitarios de tu corralón y se calcula el total (se guardan en este navegador). <b>DURABLE</b> = zona de desgaste, se paga calidad · <b>ECONOMICO</b> = lo que el inquilino puede romper, barato y reemplazable.</p>
  <table class="t comp"><thead><tr><th>Ítem</th><th class="n">Cant.</th><th>Unidad</th><th>Criterio</th><th>Precio unit.</th><th class="n">Subtotal</th></tr></thead>${body}<tfoot><tr><th colspan="5">TOTAL MATERIALES (según precios cargados)</th><th class="n" id="tot">${nf(total, 0)}</th></tr></tfoot></table></div>`;
  $('#pane-computo').querySelectorAll('.pu').forEach((i) => i.addEventListener('change', (e) => {
    precios[e.target.dataset.k] = e.target.value.replace(',', '.');
    try { localStorage.setItem('casa.precios', JSON.stringify(precios)); } catch {}
    renderComputo();
  }));
  $('#csv').addEventListener('click', () => {
    const lines = [['Capitulo', 'Item', 'Cantidad', 'Unidad', 'Criterio', 'Detalle'].join(';'), ...T.rows.map((r) => [r.cap, r.item, String(r.cant).replace('.', ','), r.unidad, r.criterio, r.detalle].map((x) => `"${String(x).replace(/"/g, '""')}"`).join(';'))];
    const a = document.createElement('a');
    a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent('﻿' + lines.join('\n'));
    a.download = 'computo-casa-bariloche.csv';
    a.click();
  });
}

// ------------------------------------------------------------------ Despiece
let despDone = false;
function renderDespiece() {
  if (despDone) return;
  despDone = true;
  const names = { durlock_std: 'Placa de yeso estándar 12,5 mm (1,20 x 2,40)', durlock_rh: 'Placa de yeso RH verde 12,5 mm (1,20 x 2,40)', cementicia: 'Placa cementicia 10 mm (1,20 x 2,40)', osb_11: 'OSB 11,1 mm (1,22 x 2,44)', osb_18: 'OSB 18 mm (1,22 x 2,44)' };
  let h = `<nav class="toc">${Object.keys(T.sheets).map((m) => `<a href="#dp-${m}">${names[m]}</a>`).join('')}<a href="#dp-madera">Maderas</a><a href="#dp-chapa">Chapas</a></nav>`;
  h += `<p class="muted">Cada pieza tiene un código (ej. <b>Y-PB-FRE-02</b> = placa de yeso, planta baja, muro de frente, pieza 2). Arriba: <b>dónde va</b> cada pieza (mapa por cara). Abajo: <b>de qué placa sale</b> y cómo cortarla (optimizado por guillotina). En el 3D, el modo “Despiece de placas” muestra los mismos códigos sobre el modelo.</p>`;
  for (const [mat, sheets] of Object.entries(T.sheets)) {
    const pcs = model.panels[mat];
    const faces = [...new Set(pcs.map((p) => p.face))];
    h += `<h2 id="dp-${mat}">${names[mat]} — ${sheets.length} placas · ${pcs.length} piezas</h2>`;
    h += `<h3>Posición de cada pieza</h3><div class="flow">${faces.map((f) => `<div class="card mini">${faceMap(model, f)}</div>`).join('')}</div>`;
    h += `<h3>Plan de corte por placa</h3><div class="flow">${sheets.map((s) => `<div class="card mini">${sheetSvg(s, SHEETS[mat], mat)}</div>`).join('')}</div>`;
    h += `<details class="card"><summary>Planilla de piezas (${pcs.length})</summary><table class="t"><thead><tr><th>Código</th><th>Cara</th><th>Local</th><th>Ancho x alto (cm)</th><th>Corte</th><th>Placa N°</th><th>Terminación</th></tr></thead><tbody>${pcs.map((p) => {
      const sn = sheets.find((s) => s.items.some((it) => it.piece.id === p.id))?.n;
      return `<tr><td><b>${p.id}</b></td><td>${esc(p.face)}</td><td>${esc(p.room ?? '')}</td><td>${nf(p.pw * 100, 1)} x ${nf(p.ph * 100, 1)}</td><td>${esc(p.cut)}</td><td>${sn}</td><td>${esc(p.finish ?? '')}</td></tr>`;
    }).join('')}</tbody></table></details>`;
  }
  h += `<h2 id="dp-madera">Maderas — lista de compra y cortes</h2>`;
  for (const [sec, w] of Object.entries(T.wood)) {
    const byUse = {};
    for (const p of w.pieces) { const k = `${p.use}|${p.len}`; byUse[k] = (byUse[k] ?? 0) + 1; }
    const uses = Object.entries(byUse).sort((a, b) => b[0].split('|')[1] - a[0].split('|')[1]).map(([k, n]) => { const [u, l] = k.split('|'); return `<tr><td>${esc(u)}</td><td class="n">${nf(l * 100, 1)}</td><td class="n">${n}</td></tr>`; }).join('');
    const bars = w.bars.map((b, i) => `<div class="bar"><span>${i + 1}. ${nf(b.stock)} m</span><div class="track">${b.cuts.map((c) => `<i style="width:${(c.len / b.stock) * 100}%" title="${esc(c.use)} ${nf(c.len * 100, 1)} cm">${nf(c.len * 100, 0)}</i>`).join('')}</div><em>sobra ${nf(b.rest * 100, 0)} cm</em></div>`).join('');
    h += `<div class="card"><header><h3>Pino ${sec} — ${w.bars.length} piezas comerciales</h3></header><div class="grid2"><table class="t"><thead><tr><th>Uso</th><th class="n">Largo (cm)</th><th class="n">Cant.</th></tr></thead><tbody>${uses}</tbody></table><div class="bars">${bars}</div></div></div>`;
  }
  h += `<h2 id="dp-chapa">Chapas — pedido a medida</h2><div class="card"><p>Revestimiento de muros (T-101 gris grafito, ancho útil 1,00 m): ${T.sheetsWall.map((l) => nf(l) + ' m').join(' · ')}</p><p>Techo (T-101 negra): ${T.lensT.length} hojas de ${nf(T.lensT[0])} m</p><p class="muted">Las chapas se piden cortadas a largo en fábrica: no hay desperdicio de largo; los cortes de hastial (inclinados) se hacen en obra con cizalla.</p></div>`;
  $('#pane-despiece').innerHTML = h;
}

// ------------------------------------------------------------------ Memoria
$('#pane-memoria').innerHTML = `<article class="memo">${MEMORIA_HTML}<h2>Paleta de colores</h2><div class="pal">${PALETA.map((p) => `<div><i style="background:${p.hex}"></i><b>${esc(p.nombre)}</b><small>${esc(p.uso)} · ${p.hex}</small></div>`).join('')}</div></article>`;

// ------------------------------------------------------------------ arranque
initViewer();
if (window.__ARTIFACT__) document.documentElement.classList.add('artifact');
const TABS = ['3d', 'estudio', 'planos', 'computo', 'despiece', 'memoria'];
let start = '3d';
try { const h = location.hash.slice(1); start = TABS.includes(h) ? h : new URLSearchParams(location.search).get('tab') || localStorage.getItem('casa.tab') || '3d'; } catch {}
if (!TABS.includes(start)) start = '3d';
showTab(start);
const pp = new URLSearchParams(location.search).get('preset');
if (pp && PRESETS[pp]) { viewer.applyPreset(pp, false); const p = PRESETS[pp]; viewer.camera.position.set(...p.cam[0]); viewer.controls.target.set(...p.cam[1]); }
const amb = new URLSearchParams(location.search).get('amb');
if (amb) viewer.setMode(amb);
window.__viewer = viewer;
void CIRC;
