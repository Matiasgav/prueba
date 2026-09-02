/* ═══════════════════ SECCIONES · informe de desempeño ═══════════════════ */

function T(id) { return document.getElementById(id); }
function txt(id, s) { var e = T(id); if (e) e.innerHTML = s; }

/* ── 01 · qué se evalúa ─────────────────────────────────────────────── */
function secConfig() {
  var sg = D.signatures || {}, cfg = sg.config || {}, pal = cfg.palpador || {};
  table(T("config-table"), [
    { h: "Elemento", f: function (r) { return r[0]; } },
    { h: "Valor", f: function (r) { return '<b class="num">' + r[1] + "</b>"; } },
    { h: "Por qué", f: function (r) { return '<span style="font-family:var(--serif);font-size:.83rem;color:var(--ink-2)">' + r[2] + "</span>"; } }
  ], [
    ["Envolvente", "10 × 10 × 50 mm, acostado", "el eje largo va a lo largo del generador; es el único donde hay lugar"],
    ["Accionamiento", "voice coil LAH04 + palanca en L", "entrega la energía de una sola carrera: no necesita acumulador ni amartillado"],
    ["Corriente", "≈1,7 A", "lineal con la fuerza; el margen térmico es 2,6×"],
    ["Energía en la maza", num(cfg.E_mJ, 1) + " mJ", "0,7 veces el trabajo que el actuador da por carrera"],
    ["Maza", num(cfg.m_maza_g, 2) + " g · " + num(cfg.v_ms, 2) + " m/s", "la de la palanca en L existente"],
    ["Punta", "calota esférica R = " + num(cfg.R_punta_mm, 0) + " mm, WC", "mantiene el contacto elástico puro; el material se elige por abrasión"],
    ["Sensor de posición", "inductivo por corrientes de Foucault", "da v_i, v_r, energía y t_c sin tocar la cuña"],
    ["Palpador", "MEMS " + num(pal.m_g, 2) + " g @ " + num(pal.F_precarga_N, 1) + " N",
     "f₀ = " + num(pal.f0_kHz, 1) + " kHz, por encima de la banda de la señal. " +
     "<b>Con esta precarga despega</b>: hay que subirla a 3 N (§6)"],
    ["Punto de medición", num(cfg.x_palpador_mm, 0) + " mm del golpe", "sobre la misma cuña"],
    ["Cuña de referencia", "G11, vano " + num(cfg.vano_mm, 0) + " mm, sección 30 × 8 mm", "la del brief; el vano de 100 mm se corre en paralelo"]
  ], { compact: true });

  var tab = sg.tabla || [];
  if (!tab.length) return;
  var a = tab[0], z = tab[tab.length - 1];
  var sep = D.separability || {};
  var dk = (sep.dprime_extremos || {}).kurtosis;
  table(T("perf-table"), [
    { h: "Magnitud", f: function (r) { return r[0]; } },
    { h: "Cuña ajustada", f: function (r) { return r[1]; } },
    { h: "Cuña floja", f: function (r) { return r[2]; } },
    { h: "Separación", f: function (r) { return '<b>' + r[3] + "</b>"; } },
    { h: "", f: function (r) { return pill(r[4], r[5]); } }
  ], [
    ["Índice Leeb", num(a.leeb, 0), num(z.leeb, 0),
     num(100 * (a.leeb - z.leeb) / a.leeb, 1) + " %", "monótono", "ok"],
    ["Energía absorbida por la cuña", num(100 * a.eta_absorbed, 1) + " %",
     num(100 * z.eta_absorbed, 1) + " %", "×" + num(z.eta_absorbed / a.eta_absorbed, 1),
     "monótona", "ok"],
    ["Curtosis del ring-down", num(a.kurtosis, 1), num(z.kurtosis, 1),
     "×" + num(z.kurtosis / a.kurtosis, 1), "monótona", "ok"],
    ["Duración del contacto", num(a.t_c1_us, 1) + " µs", num(z.t_c1_us, 1) + " µs",
     num(z.t_c1_us - a.t_c1_us, 1) + " µs", "no monótona", "crit"],
    ["Aceleración pico a 10 mm", num(a.a_pk_g, 0) + " g", num(z.a_pk_g, 0) + " g",
     "—", "exige sensor de choque", "warn"],
    ["Presión de contacto", "596 MPa", "596 MPa", "—", "elástico puro", "ok"]
  ]);

  txt("verdict-text",
    "Con la maza de " + num(cfg.m_maza_g, 2) + " g y " + num(cfg.E_mJ, 0) +
    " mJ el índice Leeb va de <b>" + num(a.leeb, 0) + " a " + num(z.leeb, 0) +
    "</b> y la energía que la cuña se queda pasa de " + num(100 * a.eta_absorbed, 1) +
    " % a " + num(100 * z.eta_absorbed, 1) + " %: el sentido es el que dice el dato de " +
    "campo, y el índice Leeb y la curtosis son monótonos con la soltura. " +
    (dk ? "Con las tolerancias reales sorteadas, la separación entre los extremos de la " +
     "escalera da d′ = " + num(dk, 1) + " en curtosis. " : "") +
    "<b>El voice coil directo alcanza y no hace falta acumulador.</b> Tres límites " +
    "quedan en pie: la duración de contacto <b>no</b> ordena los estados y hay que " +
    "descartarla como característica; el índice satura a partir del 5 % de precarga, " +
    "así que una vez suelta la cuña no se puede graduar; y la magnitud de la separación " +
    "depende de la rigidez real del asiento de la cola de milano, que no está medida (§8).");
}

/* ── 02 · verificación ──────────────────────────────────────────────── */
function secVerif() {
  var a = D.anchors || {};
  txt("v1-res", '<span class="pill ok">' + (a.n_ok || 0) + "/" + (a.n_total || 0) + " OK</span>");
  txt("v2-res", '<span class="pill ok">6 cifras en dt<br>0,14 % en modos</span>');
  var mech = D.mechanisms || {};
  txt("v3-res", '<span class="pill warn">coincide sólo<br>con maza liviana</span>');
  txt("v4-res", '<span class="pill crit">refutó el modelo<br>y se corrigió</span>');
  var sv = D.sensitivity || [];
  var s5 = sv.filter(function (r) { return r.E_mJ === 5; });
  var s5ok = s5.filter(function (r) { return r.e_monotona; }).length;
  txt("v5-res", s5.length
    ? '<span class="pill ' + (s5ok === s5.length ? "ok" : "warn") + '">orden intacto<br>' +
      s5ok + "/" + s5.length + " variantes</span>"
    : '<span class="pill warn">—</span>');

  if (a.filas) {
    table(T("anchors-table"), [
      { h: "Caso ancla", k: "caso" },
      { h: "Obtenido", f: function (r) { return num(r.obtenido, Math.abs(r.obtenido) > 100 ? 1 : 4); } },
      { h: "Objetivo", f: function (r) { return num(r.objetivo, Math.abs(r.objetivo) > 100 ? 1 : 4); } },
      { h: "Unidad", k: "unidad" },
      { h: "Error", f: function (r) { return num(r.error_pct, 3) + " %"; } },
      { h: "", f: function (r) { return pill(r.ok ? "OK" : "FALLA", r.ok ? "ok" : "crit"); } }
    ], a.filas, { compact: true });
  }

  table(T("conv-table"), [
    { h: "Parámetro numérico", f: function (r) { return r[0]; } },
    { h: "Barrido", f: function (r) { return r[1]; } },
    { h: "Variación del resultado", f: function (r) { return r[2]; } },
    { h: "Valor adoptado", f: function (r) { return '<b class="num">' + r[3] + "</b>"; } }
  ], [
    ["Paso de integración", "2 × 10⁻⁷ a 10⁻⁸ s", "restitución estable en la 6ª cifra", "5 × 10⁻⁸ s"],
    ["Modos retenidos", "8 a 60", "0,14 % entre 20 y 60 modos", "24"],
    ["Elementos de viga", "10 a 160", "0,17 % en f₁ entre 40 y 160", "60"],
    ["Puntos de la curva K_F", "11 tabulados, 4001 interpolados", "trabajo reproducido al 0,03 %", "trapecio + interpolación lineal"]
  ], { compact: true });

  if (mech.cruce_formula_cerrada) {
    var rows = mech.cruce_formula_cerrada.filter(function (r) {
      return r.vano_mm === 50 && (r.E_mJ === 5 || r.E_mJ === 20);
    });
    table(T("cross-table"), [
      { h: "Energía", f: function (r) { return num(r.E_mJ, 0) + " mJ"; } },
      { h: "Masa", f: function (r) { return num(r.m_g, 0) + " g"; } },
      { h: "m / m_eff", f: function (r) { return num(r.m_g / 9.77, 2); } },
      { h: "η fórmula cerrada", f: function (r) { return num(r.eta_cerrada, 3); } },
      { h: "η simulación", f: function (r) { return num(r.eta_simulada, 3); } },
      { h: "Discrepancia", f: function (r) {
          var e = 100 * (r.eta_cerrada - r.eta_simulada) / Math.max(r.eta_simulada, 1e-6);
          return pill(num(e, 0) + " %", Math.abs(e) < 15 ? "ok" : Math.abs(e) < 60 ? "warn" : "crit");
        } },
      { h: "t_c Hertz", f: function (r) { return num(r.t_c_hertz_us, 1) + " µs"; } },
      { h: "t_c simulado", f: function (r) { return num(r.t_c_sim_us, 1) + " µs"; } }
    ], rows, { compact: true });
  }

  table(T("support-table"), [
    { h: "Estado", f: function (r) { return r[0]; } },
    { h: "e · apoyo sólo en los extremos", f: function (r) { return num(r[1], 3); } },
    { h: "e · apoyo distribuido", f: function (r) { return num(r[2], 3); } },
    { h: "Leeb distribuido", f: function (r) { return num(1000 * r[2], 0); } },
    { h: "", f: function (r) { return r[3] ? pill("coinciden", "acc") : ""; } }
  ], [
    ["S0 · ajustada", 0.678, 0.986, false],
    ["S1 · 75 %", 0.688, 0.973, false],
    ["S2 · 50 %", 0.701, 0.920, false],
    ["S3 · 25 %", 0.721, 0.841, false],
    ["S4 · residual", 0.756, 0.782, false],
    ["S5 · floja 50 µm", 0.782, 0.782, true],
    ["S6 · floja 200 µm", 0.782, 0.782, true]
  ], { compact: true });

  var sensAll = D.sensitivity;
  if (sensAll) {
    var LBL = { "k_ripple": "rigidez del ripple", "k_shoulder": "rigidez del hombro",
                "c_slide x": "disipación de junta ×", "land_width": "ancho del apoyo",
                "zeta": "amort. del material" };
    // el barrido se corrió a dos energías; la evaluada es la primera
    var energias = [];
    sensAll.forEach(function (r) {
      if (energias.indexOf(r.energia) < 0) energias.push(r.energia);
    });
    var hostE = T("sn-energy");
    if (hostE && energias.length > 1) {
      hostE.innerHTML = energias.map(function (e, i) {
        return '<button data-v="' + e + '" aria-pressed="' + (i === 0) + '">' + e + "</button>";
      }).join("");
    }
    var curE = function () { return segValue("sn-energy") || energias[0]; };
    var sensOf = function () {
      return sensAll.filter(function (r) { return (r.energia || energias[0]) === curE(); });
    };
    var sens = sensOf();

    // conteo de monotonía por energía, para el resumen
    var resumen = energias.map(function (e) {
      var rr = sensAll.filter(function (r) { return r.energia === e; });
      var c = function (k) { return rr.filter(function (r) { return r[k]; }).length; };
      return { energia: e, n: rr.length, e_mon: c("e_monotona"),
               kurt_mon: c("kurt_monotona"), tc1_mon: c("tc1_monotona") };
    });
    table(T("sens-summary"), [
      { h: "Energía del golpe", f: function (r) { return r.energia; } },
      { h: "Variantes barridas", f: function (r) { return num(r.n, 0); } },
      { h: "Índice Leeb ordenado", f: function (r) {
          return pill(r.e_mon + "/" + r.n, r.e_mon === r.n ? "ok" : r.e_mon > r.n / 2 ? "warn" : "crit"); } },
      { h: "Curtosis ordenada", f: function (r) {
          return pill(r.kurt_mon + "/" + r.n, r.kurt_mon === r.n ? "ok" : r.kurt_mon > r.n / 2 ? "warn" : "crit"); } },
      { h: "Duración de contacto ordenada", f: function (r) {
          return pill(r.tc1_mon + "/" + r.n, r.tc1_mon === r.n ? "ok" : r.tc1_mon > r.n / 2 ? "warn" : "crit"); } }
    ], resumen, { compact: true });
    var fmtVal = function (r) {
      if (r.parametro === "land_width") return num(r.valor * 1e3, 1) + " mm";
      if (r.parametro === "zeta") return num(r.valor, 3);
      if (r.parametro === "c_slide x") return "×" + num(r.valor, 2);
      return r.valor.toExponential(0).replace("e+", "e");
    };
    redrawFns.push(function () {
      var host = T("sens-chart"); if (!host) return;
      var sn = sensOf();
      var metric = segValue("sn-metric") || "e_rango";
      var groups = [];
      sn.forEach(function (r) { if (groups.indexOf(r.parametro) < 0) groups.push(r.parametro); });
      var maxv = Math.max.apply(null, sn.map(function (r) { return r[metric]; }));
      var base = sn.filter(function (r) { return r.parametro === "c_slide x" && r.valor === 1; })[0];
      host.innerHTML = '<div style="display:grid;gap:14px">' + groups.map(function (g, gi) {
        var rows = sn.filter(function (r) { return r.parametro === g; });
        return '<div><div style="font-family:var(--sans);font-weight:600;font-size:.8rem;' +
          'color:var(--ink-2);margin-bottom:5px">' + (LBL[g] || g) + "</div>" +
          rows.map(function (r) {
            var w = Math.max(0.6, 100 * r[metric] / maxv);
            var crit = r[metric] < 0.25 * (base ? base[metric] : maxv);
            return '<div style="display:grid;grid-template-columns:82px 1fr 62px;gap:9px;' +
              'align-items:center;margin-bottom:3px">' +
              '<span class="num" style="font-size:.72rem;color:var(--ink-3);text-align:right">' +
              fmtVal(r) + "</span>" +
              '<div style="height:13px;background:var(--surface-3);border-radius:2px;overflow:hidden">' +
              '<div style="height:100%;width:' + w + '%;background:' +
              (crit ? "var(--crit)" : cvar(gi)) + '"></div></div>' +
              '<span class="num" style="font-size:.72rem">' +
              num(r[metric], metric === "e_rango" ? 3 : metric === "kurt_rango" ? 0 : 2) +
              "</span></div>";
          }).join("") + "</div>";
      }).join("") + "</div>";
    });
    var sensCols = [
      { h: "Parámetro barrido", f: function (r) { return LBL[r.parametro] || r.parametro; } },
      { h: "Valor", f: fmtVal },
      { h: "e ajustada", f: function (r) { return num(r.serie[0].e, 3); } },
      { h: "e floja", f: function (r) { return num(r.serie[r.serie.length - 1].e, 3); } },
      { h: "Rango de e", f: function (r) { return num(r.e_rango, 3); } },
      { h: "Rango de curtosis", f: function (r) { return num(r.kurt_rango, 0); } },
      { h: "Leeb ordenado", f: function (r) {
          return pill(r.e_monotona ? "sí" : "no", r.e_monotona ? "ok" : "crit"); } },
      { h: "Curtosis ordenada", f: function (r) {
          return pill(r.kurt_monotona ? "sí" : "no", r.kurt_monotona ? "ok" : "crit"); } }
    ];
    var drawSensTable = function () { table(T("sens-table"), sensCols, sensOf(), { compact: true }); };
    seg("sn-metric", redraw);
    seg("sn-energy", function () { drawSensTable(); redraw(); });
    redrawFns.push(drawSensTable);
  }

  table(T("bugs-table"), [
    { h: "Nivel", f: function (r) { return '<b class="num">' + r[0] + "</b>"; } },
    { h: "Qué se encontró", f: function (r) { return r[1]; } },
    { h: "Consecuencia", f: function (r) { return '<span style="font-family:var(--serif);font-size:.83rem">' + r[2] + "</span>"; } }
  ], [
    ["1", "Empotramiento modelado con resorte de penalidad de 10¹⁴ N/m",
     "+13,7 % en f₁ sin ningún síntoma visible: la rigidez estática seguía exacta. Se detectó sólo porque el caso empotrado no cerraba contra el ancla. Se eliminan los GDL en vez de penalizarlos."],
    ["3", "La fórmula cerrada de acoplamiento modal se rompe con maza pesada",
     "predice η = 0,77 donde la simulación da 0,39. Recomienda como óptima una masa a la cual ella misma es inválida."],
    ["4", "La cuña ajustada estaba modelada apoyada sólo en dos puntos",
     "el índice Leeb salía creciente con la soltura, al revés del dato de campo. Se corrigió a apoyo distribuido y el signo se invierte."],
    ["—", "El palpador se excitaba con la doble integral de la aceleración",
     "la deriva daba 97 % de despegue en todos los casos, incluidos los que no despegan. Se excita con el desplazamiento, que la simulación ya entrega."],
    ["—", "Energía de fluencia calculada reconstruyendo un material de E = E*",
     "volvía a sumar la flexibilidad del blanco y daba un valor 2,5 veces menor. Ahora sale del escalado exacto p ∝ E^0,2."],
    ["—", "Acumulador dimensionado sin la máquina que lo carga",
     "la barra de torsión de 192 mJ pasa a 7 mJ con el cargador adentro del envolvente. Tiró abajo la arquitectura recomendada."]
  ], { compact: true });
}

/* ── 03 · estados ───────────────────────────────────────────────────── */
function secStates() {
  var sg = D.signatures; if (!sg) return;
  table(T("states-table"), [
    { h: "Estado", k: "estado" },
    { h: "Precarga", f: function (r) { return num(r.precarga_N, 0) + " N"; } },
    { h: "Juego", f: function (r) { return num(r.gap_um, 0) + " µm"; } },
    { h: "Leeb", f: function (r) { return '<b>' + num(r.leeb, 0) + "</b>"; } },
    { h: "Absorbida", f: function (r) { return num(100 * r.eta_absorbed, 1) + " %"; } },
    { h: "t_c", f: function (r) { return num(r.t_c1_us, 1) + " µs"; } },
    { h: "Curtosis", f: function (r) { return '<b>' + num(r.kurtosis, 1) + "</b>"; } },
    { h: "F pico", f: function (r) { return num(r.F_peak_N, 0) + " N"; } },
    { h: "a pico", f: function (r) { return num(r.a_pk_g, 0) + " g"; } },
    { h: "f dominante", f: function (r) { return num(r.f_peak_Hz / 1e3, 1) + " kHz"; } }
  ], sg.tabla, { compact: true });
}

/* ── 04 · firmas ────────────────────────────────────────────────────── */
function secSignatures() {
  var sg = D.signatures; if (!sg) return;
  var wf = sg.firmas, names = Object.keys(wf);
  var sel = {}; names.forEach(function (n, i) { sel[n] = (i === 0 || i === 3 || i === names.length - 1); });
  var host = T("wave-states");
  host.innerHTML = names.map(function (n, i) {
    return '<button data-w="' + i + '" aria-pressed="' + (sel[n] ? "true" : "false") + '">' +
           n.split("·")[0].trim() + "</button>";
  }).join("");
  host.addEventListener("click", function (ev) {
    var b = ev.target.closest("button"); if (!b) return;
    var n = names[parseInt(b.getAttribute("data-w"), 10)];
    sel[n] = !sel[n]; b.setAttribute("aria-pressed", String(sel[n])); drawWaves();
  });
  function drawWaves() {
    var sig = segValue("wave-sig") || "a_palp_g";
    var series = [], leg = [];
    names.forEach(function (n, i) {
      if (!sel[n]) return;
      var w = wf[n], pts;
      if (sig === "spec") {
        var dt = (w.t_us[1] - w.t_us[0]) * 1e-6;
        pts = spectrum(w.a_palp_g, dt).filter(function (p) { return p[0] > 400 && p[0] < 45000; });
      } else {
        pts = w.t_us.map(function (t, j) { return [t, w[sig][j]]; })
                    .filter(function (p) { return p[0] <= (sig === "F_N" ? 120 : 1200); });
      }
      series.push({ name: n, points: pts, color: cvar(i), w: 1.5 });
      leg.push({ name: n, color: cvar(i) });
    });
    var isSpec = sig === "spec";
    chart(T("wave-chart"), {
      height: 340, series: series,
      xlabel: isSpec ? "frecuencia [Hz]" : "tiempo [µs]",
      ylabel: isSpec ? "amplitud espectral" : ({ a_palp_g: "aceleración en el palpador [g]",
               F_N: "fuerza de contacto [N]", w_palp_um: "desplazamiento de la cuña [µm]" })[sig],
      xlog: isSpec, ylog: isSpec, yd: 0,
      yfmt: isSpec ? function (v) { return v >= 1 ? num(v, 0) : v.toExponential(0); } : null,
      xfmt: isSpec ? function (v) { return v >= 1000 ? num(v / 1000, 0) + "k" : num(v, 0); } : null,
      aria: "Firma simulada de la cuña para los estados de ajuste seleccionados"
    });
    var lg = T("wave-chart").parentNode.querySelector(".chart-legend");
    if (!lg) { lg = el("div", { class: "chart-legend" }); T("wave-chart").after(lg); }
    legend(lg, leg);
  }
  seg("wave-sig", drawWaves);
  redrawFns.push(drawWaves);

  // pequeños múltiples
  redrawFns.push(function () {
    var grid = T("sig-grid"); if (!grid) return;
    var amax = 0;
    names.forEach(function (n) {
      wf[n].a_palp_g.forEach(function (v) { amax = Math.max(amax, Math.abs(v)); });
    });
    grid.innerHTML = "";
    names.forEach(function (n, i) {
      var w = wf[n], row = (sg.tabla || [])[i] || {};
      var box = el("div", { class: "sig" });
      box.innerHTML = '<div class="t">' + n + "</div>" +
        '<div class="m">Leeb ' + num(row.leeb, 0) + " · curtosis " + num(row.kurtosis, 1) +
        " · absorbe " + num(100 * row.eta_absorbed, 0) + " %</div>";
      var c = el("div");
      box.appendChild(c);
      grid.appendChild(box);
      chart(c, {
        width: 300, height: 118, ml: 34, mr: 6, mb: 22, nx: 3, ny: 3,
        ydomain: [-amax, amax], xdomain: [0, 1200], yd: 0,
        series: [{ name: n, color: cvar(i), w: 1.1,
                   points: w.t_us.map(function (t, j) { return [t, w.a_palp_g[j]]; })
                                 .filter(function (p) { return p[0] <= 1200; }) }],
        aria: "Firma de aceleración del estado " + n
      });
    });
  });

  // las tres características a lo largo de la escalera
  redrawFns.push(function () {
    var host2 = T("f3-chart"); if (!host2) return;
    var m = segValue("f3-metric") || "leeb";
    var pts = sg.tabla.map(function (r, i) {
      return [i, m === "eta_absorbed" ? r[m] * 100 : r[m]];
    });
    chart(host2, {
      height: 280, series: [{ name: m, points: pts, dots: true, w: 2.4 }],
      xlabel: "estado de ajuste", xdomain: [-0.3, sg.tabla.length - 0.7],
      xticks: sg.tabla.map(function (_, i) { return i; }),
      xfmt: function (v) { var r = sg.tabla[Math.round(v)]; return r ? r.estado.split("·")[0].trim() : ""; },
      ylabel: ({ leeb: "índice Leeb", kurtosis: "curtosis",
                 t_c1_us: "duración del contacto [µs]",
                 eta_absorbed: "energía absorbida [%]" })[m],
      yd: m === "kurtosis" || m === "t_c1_us" ? 1 : 0,
      aria: "Evolución de la característica a lo largo de la escalera de ajuste"
    });
  });
  seg("f3-metric", redraw);

  // no linealidad con la energía
  var ws = D.wedge_states;
  if (ws) {
    redrawFns.push(function () {
      var host3 = T("nl-chart"); if (!host3) return;
      var metric = segValue("nl-metric") || "restitution";
      // maza del punto evaluado; el barrido también trae 4 y 8 g
      var rows = ws.vano_50mm.filter(function (r) {
        return r.m_g === undefined || Math.abs(r.m_g - 2.105) < 1e-6;
      });
      var ests = []; rows.forEach(function (r) { if (ests.indexOf(r.estado) < 0) ests.push(r.estado); });
      chart(host3, {
        height: 300, xlabel: "energía del golpe [mJ]", ylabel: metric, xlog: true,
        xfmt: function (v) { return num(v, 0); },
        yd: metric === "restitution" ? 2 : 0,
        aria: "Dependencia de la firma con la energía del golpe",
        series: ests.map(function (e, i) {
          return { name: e, dots: true, color: cvar(i),
                   points: rows.filter(function (r) { return r.estado === e; })
                               .map(function (r) { return [r.E_mJ, r[metric]]; })
                               .sort(function (a, b) { return a[0] - b[0]; }) };
        })
      });
      legend(T("nl-legend"), ests.map(function (e, i) {
        return { name: e.split("·")[0].trim(), color: cvar(i) };
      }));
    });
    seg("nl-metric", redraw);
  }
}

/* ── 05 · desempeño de discriminación ───────────────────────────────── */
function secPerf() {
  var sep = D.separability;
  if (sep) {
    var keys = [["kurtosis", "Curtosis", 1], ["leeb", "Índice Leeb", 0],
                ["restitution", "Restitución", 3], ["eta_absorbed", "Fracción absorbida", 3],
                ["t_c1_us", "Duración del contacto [µs]", 1],
                ["centroid_Hz", "Centroide espectral [Hz]", 0]];
    var labs = sep.labels;
    var cols = [{ h: "Característica", f: function (r) { return r.name; } }];
    labs.forEach(function (l) {
      cols.push({ h: l.split("·")[0].trim(), f: function (r) {
        var s = r.stats[l];
        return s ? num(s.media, r.d) + '<span style="color:var(--ink-3)"> ±' + num(s.sigma, r.d) + "</span>" : "—";
      } });
    });
    cols.push({ h: "d′ extremos", f: function (r) {
      var v = sep.dprime_extremos[r.k];
      if (v === undefined || !isFinite(v) || v > 1e6) return pill("binario", "acc");
      return '<b>' + num(v, 2) + "</b>";
    } });
    table(T("sep-table"), cols,
      keys.map(function (k) { return { k: k[0], name: k[1], d: k[2], stats: sep.stats[k[0]] || {} }; }),
      { compact: true });

    redrawFns.push(function () {
      var host = T("adj-chart"); if (!host) return;
      var ks = ["kurtosis", "leeb", "t_c1_us"];
      var pares = (sep.dprime_adyacentes[ks[0]] || []).map(function (r) { return r.par; });
      var series = ks.map(function (k, i) {
        return { name: k, kind: "bar", color: cvar(i),
                 points: (sep.dprime_adyacentes[k] || []).map(function (r, j) {
                   return [j + (i - 1) * 0.26, Math.min(r.d_prime, 14)];
                 }) };
      });
      chart(host, {
        height: 280, series: series, ydomain: [0, 14], hline: 2,
        xdomain: [-0.6, pares.length - 0.4],
        xticks: pares.map(function (_, i) { return i; }),
        xfmt: function (v) { return pares[Math.round(v)] || ""; },
        xlabel: "par de estados consecutivos", ylabel: "d′", yd: 0,
        aria: "Separación d prima entre cada par consecutivo de estados, por característica"
      });
      legend(T("adj-legend"), [{ name: "curtosis", color: cvar(0) },
                               { name: "índice Leeb", color: cvar(1) },
                               { name: "duración de contacto (descartada)", color: cvar(2) },
                               { name: "umbral práctico d′ = 2", color: "var(--ink-3)" }]);
    });

    // texto de lectura. Sólo se combinan las dos características que el barrido
    // de sensibilidad dejó en pie: t_c queda afuera porque no ordena la escalera.
    var adj = sep.dprime_adyacentes.kurtosis || [];
    var peor = adj.reduce(function (a, b) { return b.d_prime < a.d_prime ? b : a; }, adj[0] || { par: "—", d_prime: 0 });
    var comb = adj.map(function (_, i) {
      return Math.sqrt(["kurtosis", "leeb"].reduce(function (s, k) {
        var v = (sep.dprime_adyacentes[k] || [])[i];
        return s + (v ? v.d_prime * v.d_prime : 0);
      }, 0));
    });
    var buenos = comb.filter(function (c) { return c >= 2; }).length;
    var ult = comb[comb.length - 1];
    var dk0 = ((sep.dprime_adyacentes.kurtosis || [])[0] || {}).d_prime;
    var dl0 = ((sep.dprime_adyacentes.leeb || [])[0] || {}).d_prime;
    txt("sep-text",
      "Combinando curtosis e índice Leeb —las dos que sobrevivieron al barrido de sensibilidad, " +
      "y suponiéndolas independientes— <b>" + buenos + " de los " + comb.length +
      " pares consecutivos</b> superan el umbral práctico de d′ = 2. " +
      "Y lo hacen porque <b>las dos características son complementarias, no redundantes</b>: en el " +
      "primer escalón, el de la cuña que recién empieza a aflojarse, el índice Leeb da d′ = " +
      num(dl0, 2) + " —no lo ve— mientras la curtosis da " + num(dk0, 2) + "; en el medio de la " +
      "escalera se invierte. Cada una cubre donde la otra falla, y por eso hay que llevar las dos. " +
      "El par más difícil es <b>" + peor.par + "</b>, los dos estados flojos: con d′ = " +
      num(ult, 2) + " no se distinguen, y era esperable porque a esa altura la cuña ya despegó " +
      "y agrandarle el juego no cambia nada. " +
      "La escalera de siete estados es más fina de lo que el ensayo puede resolver: " +
      "<b>una partición en tres clases —ajustada, intermedia, floja— es cómoda; una escala " +
      "continua de soltura no lo es</b>.");

    var fkeys = [["kurtosis", "curtosis"], ["leeb", "Leeb"], ["t_c1_us", "t_c [µs]"],
                 ["eta_absorbed", "absorbida"], ["centroid_Hz", "centroide"]];
    ["fx", "fy"].forEach(function (id, k) {
      T(id).innerHTML = fkeys.map(function (f, i) {
        return '<button data-v="' + f[0] + '" aria-pressed="' + (i === (k ? 1 : 0)) + '">' + f[1] + "</button>";
      }).join("");
    });
    function drawFeat() {
      var xk = segValue("fx") || "kurtosis", yk = segValue("fy") || "leeb";
      var lb = Object.keys(sep.raw);
      chart(T("feat-chart"), {
        height: 320,
        xlabel: (fkeys.filter(function (f) { return f[0] === xk; })[0] || [])[1],
        ylabel: (fkeys.filter(function (f) { return f[0] === yk; })[0] || [])[1],
        xd: xk === "eta_absorbed" ? 2 : 0, yd: yk === "eta_absorbed" ? 2 : 0,
        aria: "Nube de clases en el espacio de dos características",
        series: lb.map(function (l, i) {
          return { name: l, kind: "scatter", r: 4.2, color: cvar(i),
                   points: sep.raw[l].map(function (r) { return [r[xk], r[yk]]; }) };
        })
      });
      legend(T("feat-legend"), lb.map(function (l, i) {
        return { name: l.split("·")[0].trim() + " " + l.split("·")[1], color: cvar(i) };
      }));
    }
    seg("fx", drawFeat); seg("fy", drawFeat);
    redrawFns.push(drawFeat);
  }

  var le = D.low_energy || {}, pl = D.palpator || {};
  var rows = (pl.barrido_energia || []).map(function (r) {
    var u = ((le._umbral_despegue || []).filter(function (x) {
      return Math.abs(x.E_mJ - r.E_mJ) < 0.6; })[0]) || {};
    return { E: r.E_mJ, I: r.I_VCM_A, ea: r.e_ajustada, ef: r.e_floja,
             de: r.dprime_ext_e, dk: r.dprime_ext_kurt, desp: u.despega };
  });
  if (rows.length) {
    table(T("energy-table"), [
      { h: "Energía", f: function (r) { return num(r.E, 1) + " mJ"; } },
      { h: "Corriente del VCM", f: function (r) { return num(r.I, 2) + " A"; } },
      { h: "e ajustada", f: function (r) { return num(r.ea, 3); } },
      { h: "e floja", f: function (r) { return num(r.ef, 3); } },
      { h: "d′ extremos (restitución)", f: function (r) { return num(r.de, 1); } },
      { h: "d′ extremos (curtosis)", f: function (r) { return num(r.dk, 1); } },
      { h: "¿Despega la cuña ajustada?", f: function (r) {
          return r.desp === undefined ? "—" : pill(r.desp ? "sí" : "no", r.desp ? "ok" : "neutral"); } }
    ], rows, { compact: true });
  }
}

/* ── 06 · sensado ───────────────────────────────────────────────────── */
function secSensing() {
  var rows = [];
  [0.2, 0.5, 1.0].forEach(function (sx) {
    [10e3, 30e3, 60e3].forEach(function (B) {
      var sa = sx * 1e-6 * Math.pow(2 * Math.PI, 2) * B * B / Math.sqrt(5) / 9.80665;
      rows.push({ sx: sx, B: B / 1e3, sa: sa, snr_m: 17972 / sa, snr_c: 3134 / sa });
    });
  });
  table(T("dd-table"), [
    { h: "Resolución de posición", f: function (r) { return num(r.sx, 1) + " µm"; } },
    { h: "Banda del filtro", f: function (r) { return num(r.B, 0) + " kHz"; } },
    { h: "Ruido en aceleración", f: function (r) { return num(r.sa, 0) + " g"; } },
    { h: "SNR sobre la maza (18 000 g)", f: function (r) {
        return pill(num(r.snr_m, 0) + "×", r.snr_m > 10 ? "ok" : "warn"); } },
    { h: "SNR sobre la cuña (3 100 g)", f: function (r) {
        return pill(num(r.snr_c, 1) + "×", r.snr_c > 10 ? "ok" : r.snr_c > 3 ? "warn" : "crit"); } }
  ], rows, { compact: true });

  var pl = D.palpator;
  if (pl && pl.palpadores) {
    table(T("palp-table"), [
      { h: "Configuración del palpador", k: "config" },
      { h: "Masa", f: function (r) { return r.m_g === undefined ? "—" : num(r.m_g, 2) + " g"; } },
      { h: "Precarga", f: function (r) { return r.F_precarga_N === undefined ? "—" : num(r.F_precarga_N, 1) + " N"; } },
      { h: "f₀ de contacto", f: function (r) {
          return isFinite(r.f0_kHz) && r.f0_kHz < 1e6 ? num(r.f0_kHz, 1) + " kHz" : "∞"; } },
      { h: "Aceleración de despegue", f: function (r) {
          return isFinite(r.a_despegue_g) && r.a_despegue_g < 1e6 ? num(r.a_despegue_g, 0) + " g" : "∞"; } },
      { h: "¿Despega?", f: function (r) { return pill(r.despega ? "sí" : "no", r.despega ? "warn" : "ok"); } },
      { h: "Rango de curtosis", f: function (r) { return '<b>×' + num(r.rango, 1) + "</b>"; } },
      { h: "Orden", f: function (r) { return pill(r.monotona ? "monótono" : "se rompe", r.monotona ? "ok" : "crit"); } }
    ], pl.palpadores, { compact: true });
  }
}

/* ── 07 · robustez ──────────────────────────────────────────────────── */
function secRobust() {
  var mc = D.montecarlo, sc = (mc && mc.escenarios) || {};
  var k = Object.keys(sc)[0];
  var s = sc[k] || {};
  table(T("rep-table"), [
    { h: "Magnitud", f: function (r) { return r[0]; } },
    { h: "Valor", f: function (r) { return '<b class="num">' + r[1] + "</b>"; } },
    { h: "Comentario", f: function (r) { return '<span style="font-family:var(--serif);font-size:.83rem;color:var(--ink-2)">' + r[2] + "</span>"; } }
  ], [
    ["Dispersión de energía del actuador", num(s.cv_lanzador_pct, 2) + " %",
     "sin traba ni acumulador las fuentes son pocas: corriente, fricción, temperatura y hora del crawler"],
    ["Error en la energía reportada", num(s.error_residual_medicion_pct, 2) + " %",
     "es el error del sensor, no el del actuador: la energía se mide tiro a tiro"],
    ["Efecto de la posición horaria", "±1 %",
     "carrera corta: el proyectil pasa poca distancia bajo la gravedad. Y se mide, así que no hace falta compensar"],
    ["Estrategia recomendada", "lazo sobre la corriente",
     "entregar siempre la misma energía es mejor que normalizar, para poder comparar mapas entre máquinas"]
  ], { compact: true });

  var d = D.damage;
  if (d && d.severidad_constante) {
    table(T("damage-table"), [
      { h: "Radio de la punta", f: function (r) { return num(r.R_mm, 0) + " mm"; } },
      { h: "Energía admisible a 900 MPa", f: function (r) { return num(r.E_mJ, 2) + " mJ"; } },
      { h: "Veces el ensayo de la bola", f: function (r) { return "×" + num(r.factor_vs_ancla, 1); } },
      { h: "p_max con el golpe de 5 mJ", f: function (r) {
          var p = 900 * Math.pow(5 / 1.4457, 0.2) * Math.pow(r.R_mm / 4, -0.6);
          var c = p < 640 ? "ok" : p < 1024 ? "warn" : "crit";
          return pill(num(p, 0) + " MPa", c);
        } },
      { h: "Régimen", f: function (r) {
          var p = 900 * Math.pow(5 / 1.4457, 0.2) * Math.pow(r.R_mm / 4, -0.6);
          return p < 640 ? "elástico puro" : p < 1024 ? "shakedown" : "acumula huella";
        } }
    ], d.severidad_constante, { compact: true });
  }

  table(T("recoil-table"), [
    { h: "Magnitud", f: function (r) { return r[0]; } },
    { h: "Valor", f: function (r) { return '<b class="num">' + r[1] + "</b>"; } },
    { h: "Qué implica", f: function (r) { return '<span style="font-family:var(--serif);font-size:.83rem;color:var(--ink-2)">' + r[2] + "</span>"; } }
  ], [
    ["Fuerza pico de contacto", "371 N", "carga estructural para el módulo y su montaje"],
    ["Duración del contacto", "38 µs", "el crawler no tiene tiempo de moverse: la reacción se absorbe inercialmente"],
    ["Impulso transferido", "4,6 mN·s", "esto es lo que el imán tiene que arrestar, no los 371 N"],
    ["Retroceso de un crawler de 2 kg", "2,3 mm/s", "un imán de 50 N lo frena en 92 µs"],
    ["Desplazamiento durante el frenado", "0,1 µm", "despreciable frente a los 30 µm de indentación"]
  ], { compact: true });
}

/* ── 08 · límites ───────────────────────────────────────────────────── */
function secLimits() {
  table(T("limits-table"), [
    { h: "Límite", f: function (r) { return r[0]; } },
    { h: "Dónde aparece", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[1] + "</span>"; } },
    { h: "Se puede correr", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[2] + "</span>"; } },
    { h: "", f: function (r) { return pill(r[3], r[4]); } }
  ], [
    ["Saturación de la escala", "a partir del 5 % de precarga el índice Leeb deja de moverse y sólo la curtosis sigue separando", "no se puede: una vez suelta, la cuña ya no tiene nada más que soltar. Con otro principio de medición quizás", "estructural", "crit"],
    ["Precarga del palpador", "con 0,05 g y los 0,5 N previstos el umbral de despegue queda en 1020 g contra 3100 g de señal: la curtosis pierde la monotonía y el rango cae a ×9,1", "subir la precarga a 3 N (×29,6 y monótona) o a 5 N (×45,3). Es un resorte, no un rediseño", "corrección pendiente", "crit"],
    ["Masa del palpador", "con 0,8 a 2 g la resonancia de contacto cae dentro de la banda de la señal (6 kHz con 2 g)", "MEMS casi desnudo de 0,05 g: f₀ = 38,8 kHz con 3 N", "resuelto por diseño", "ok"],
    ["Rango del acelerómetro", "a 10 mm del golpe hay 1900 a 3100 g: un IEPE de ±500 g satura", "sensor de choque o MEMS de alto rango", "resuelto por selección", "ok"],
    ["Duración de contacto como característica", "t_c no ordena la escalera en ninguna de las 23 variantes del barrido: se mueve 2,1 µs en total y cambia de signo en el medio", "no se puede arreglar: hay que sacarla del vector de decisión y quedarse con Leeb + curtosis", "estructural", "crit"],
    ["Techo de energía", "a 60 mJ el índice Leeb deja de ordenar la escalera en 20 de 23 variantes: la curva se pliega", "no subir la energía. Los 5 mJ están en el régimen correcto, no apenas alcanzando", "resuelto por diseño", "ok"],
    ["Doble derivada sobre la cuña", "a 3 000 g hay que filtrar a 10 kHz y se pierde el contenido útil", "no: este canal sirve para la maza, no para la cuña", "estructural", "warn"],
    ["Umbral de despegue", "la cuña ajustada empieza a despegar entre 2 y 5 mJ: por debajo se pierde el discriminante no lineal", "los 5 mJ ya están arriba del umbral. Si hiciera falta más margen, subir la corriente", "resuelto por diseño", "ok"],
    ["Magnitud de la separación", "un hombro diez veces más blando que lo supuesto baja el rango de restitución de 0,205 a 0,040", "medir la rigidez del asiento en mock-up; el orden es seguro, la magnitud no", "abierto", "crit"]
  ]);

  txt("dom-limit",
    "De todos los límites anteriores hay uno que no se resuelve con diseño: <b>la magnitud de la " +
    "separación entre clases depende de la rigidez real del asiento de la cola de milano</b>, que " +
    "es una estimación sin ningún dato atrás. El barrido de sensibilidad muestra que la rigidez " +
    "del ripple puede variar 60 veces, el ancho del apoyo 6 veces y el amortiguamiento del " +
    "material 12 veces sin mover el resultado ni un 2 %; pero si el hombro resulta diez veces más " +
    "blando que lo supuesto, el rango de restitución cae de 0,205 a <b>0,040</b> — cinco veces " +
    "menos separación. Y una cuña con el asiento fretado o con óxido es exactamente eso: un " +
    "hombro blando. El segundo en importancia es la disipación de junta, pero ahí el efecto es " +
    "el contrario de lo que se esperaría: la fricción <i>borronea</i> la separación en vez de " +
    "producirla (anularla la sube de 0,205 a 0,307), y cuadruplicarla la baja a 0,111. " +
    "El <i>orden</i> de la escalera es robusto a la energía evaluada; su <i>escala</i> es una " +
    "hipótesis hasta que se mida la rigidez del asiento.");

  table(T("todo-table"), [
    { h: "Prioridad", f: function (r) { return '<b class="num">' + r[0] + "</b>"; } },
    { h: "Qué medir", f: function (r) { return r[1]; } },
    { h: "Cómo", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[2] + "</span>"; } },
    { h: "Qué cierra", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[3] + "</span>"; } }
  ], [
    ["1", "Rigidez del asiento de la cola de milano",
     "indentación instrumentada sobre el hombro de una ranura real, o bien función de respuesta en frecuencia de la cuña montada: la rigidez de contacto sale de la frecuencia del primer modo con la cuña apoyada contra la de la cuña libre",
     "la magnitud de toda la escalera: es el único parámetro que la mueve (×5 sobre el rango de restitución)"],
    ["2", "Disipación de la junta contra amplitud y precarga",
     "ensayo modal con martillo instrumentado a energías crecientes, para tres precargas medidas con celda de carga. En una junta con micro-deslizamiento el amortiguamiento crece con la amplitud; en una pegada es constante",
     "cuánto se borronea la separación, y a qué energía se pliega la curva. Medio día de trabajo"],
    ["3", "Módulo transversal del G11",
     "indentación instrumentada con esfera de R = 4 mm sobre probeta, midiendo fuerza y penetración: de la pendiente F = k·δ^1,5 sale E*",
     "el modelo de contacto, que hoy usa un valor estimado"],
    ["4", "Precarga real del ripple instalado y su rigidez",
     "celda de carga en el mock-up, y ensayo de compresión del resorte",
     "dónde cae cada cuña real dentro de la escalera"],
    ["5", "Umbral de daño real del G11",
     "escalera de energías crecientes en el mismo punto, con inspección de huella al microscopio",
     "el criterio de shakedown, que hoy es teoría de contacto trasladada sin verificar"],
    ["6", "Transferencia real del palpador",
     "excitar la cuña con un shaker de barrido y comparar el MEMS sobre palpador contra un patrón pegado",
     "la corrección de la firma medida, y valida el modelo de despegue"],
    ["—", "Separación entre clases requerida por el cliente",
     "es una decisión, no una medición",
     "sin ese número no se puede decir si el sistema cumple, por más margen que tenga"]
  ], { compact: true });
}

/* ── 09 · descartado ────────────────────────────────────────────────── */
function secDiscarded() {
  var ch = D.charger;
  if (ch && ch.volumen_vs_energia) {
    table(T("charger-table"), [
      { h: "Largo disponible para la barra de torsión", f: function (r) { return num(r.L_barra_mm, 0) + " mm"; } },
      { h: "⌀ resultante", f: function (r) { return num(r.d_mm, 2) + " mm"; } },
      { h: "Energía", f: function (r) { return '<b>' + num(r.E_mJ, 1) + " mJ</b>"; } },
      { h: "Qué ocupa el resto", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r.ocupa_el_resto + "</span>"; } }
    ], ch.volumen_vs_energia, { compact: true });
  }
  var cat = (D.catalog || []).filter(function (r) { return r.family !== "A"; });
  table(T("alt-table"), [
    { h: "ID", f: function (r) { return '<b style="font-family:var(--sans)">' + r.aid + "</b>"; } },
    { h: "Alternativa", f: function (r) { return '<span style="font-family:var(--serif)">' + r.name + "</span>"; } },
    { h: "E máx", f: function (r) { return r.E_max_mJ ? num(r.E_max_mJ, 0) + " mJ" : "—"; } },
    { h: "Entra en 10 mm", f: function (r) { return pill(r.fits_10mm ? "sí" : "no", r.fits_10mm ? "ok" : "crit"); } },
    { h: "Necesita cargador", f: function (r) {
        var n = /torsión|Ballesta|Leva/.test(r.name);
        return pill(n ? "sí" : "no", n ? "crit" : "ok"); } },
    { h: "TRL", k: "trl" },
    { h: "Motivo del descarte", f: function (r) {
        return '<span style="font-family:var(--serif);font-size:.82rem">' +
               (r.cons && r.cons[0] ? r.cons[0] : "—") + "</span>"; } }
  ], cat, { compact: true });
}

/* ───────────────────────── init ───────────────────────── */
function init() {
  bindNumbers();
  secConfig(); secVerif(); secStates(); secSignatures(); secPerf();
  secSensing(); secRobust(); secLimits(); secDiscarded();
  buildTOC(); themeToggle();
  redraw();
  var gd = T("gendate");
  if (gd && D._meta) gd.textContent = D._meta.fecha;
  var ab = T("anchor-badge");
  if (ab && D.anchors) ab.innerHTML = D.anchors.n_ok + "/" + D.anchors.n_total + " anclas OK";
  window.addEventListener("resize", function () {
    clearTimeout(window.__rt); window.__rt = setTimeout(redraw, 200);
  });
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();
})();
