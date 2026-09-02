(function () {
"use strict";
var D = {};
try { D = JSON.parse(document.getElementById("wtd-data").textContent); }
catch (e) { console.error("datos no disponibles", e); }

/* ───────────────────────── utilidades ───────────────────────── */
var NBSP = " ";
function num(v, d) {
  if (v === null || v === undefined || (typeof v === "number" && !isFinite(v)))
    return "—";
  var n = Number(v);
  if (n === 0 || Math.abs(n) < Math.pow(10, -(d === undefined ? 2 : d)) / 2) n = 0;
  var s = n.toLocaleString("es-AR", { minimumFractionDigits: d === undefined ? 2 : d,
                                      maximumFractionDigits: d === undefined ? 2 : d });
  return s;
}
function resolve(path) {
  var cur = D, parts = path.split(".");
  for (var i = 0; i < parts.length; i++) {
    if (cur === undefined || cur === null) return undefined;
    cur = cur[parts[i]];
  }
  return cur;
}
function bindNumbers() {
  document.querySelectorAll("[data-n]").forEach(function (el) {
    var spec = el.getAttribute("data-n").split("|");
    var v = resolve(spec[0]);
    var d = spec.length > 1 ? parseInt(spec[1], 10) : 2;
    var mods = (spec[2] || "").split("+");
    if (mods.indexOf("pct") >= 0 && typeof v === "number") v = v * 100;
    if (mods.indexOf("abs") >= 0 && typeof v === "number") v = Math.abs(v);
    el.textContent = v === undefined ? "—" : num(v, d);
  });
}
function el(tag, attrs, kids) {
  var e = document.createElement(tag);
  if (attrs) for (var k in attrs) {
    if (k === "class") e.className = attrs[k];
    else if (k === "html") e.innerHTML = attrs[k];
    else e.setAttribute(k, attrs[k]);
  }
  (kids || []).forEach(function (c) {
    e.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  });
  return e;
}
function table(host, cols, rows, opts) {
  opts = opts || {};
  var t = host.tagName === "TABLE" ? host : el("table");
  if (opts.compact) t.className = "compact";
  t.innerHTML = "";
  var thead = el("thead"), tr = el("tr");
  cols.forEach(function (c) { tr.appendChild(el("th", null, [c.h])); });
  thead.appendChild(tr); t.appendChild(thead);
  var tb = el("tbody");
  rows.forEach(function (r, i) {
    var q = el("tr");
    if (opts.rowAttr) { var a = opts.rowAttr(r, i); for (var k in a) q.setAttribute(k, a[k]); }
    cols.forEach(function (c) {
      var v = c.f ? c.f(r, i) : r[c.k];
      var td = el("td");
      if (v instanceof Node) td.appendChild(v);
      else td.innerHTML = v === undefined || v === null ? "—" : v;
      q.appendChild(td);
    });
    tb.appendChild(q);
  });
  t.appendChild(tb);
  if (host !== t && !host.contains(t)) { host.innerHTML = ""; host.appendChild(t); }
  return t;
}
function pill(txt, cls) { return '<span class="pill ' + cls + '">' + txt + "</span>"; }

/* ───────────────────────── gráficos SVG ───────────────────────── */
var PAL = ["--c1", "--c2", "--c3", "--c4", "--c5", "--c6", "--c7"];
function cvar(i) { return "var(" + PAL[i % PAL.length] + ")"; }

function niceTicks(lo, hi, n) {
  if (!isFinite(lo) || !isFinite(hi) || lo === hi) return [lo];
  var span = hi - lo, step = Math.pow(10, Math.floor(Math.log10(span / n)));
  var err = span / n / step;
  if (err >= 7.5) step *= 10; else if (err >= 3.5) step *= 5;
  else if (err >= 1.5) step *= 2;
  var out = [], v = Math.ceil(lo / step) * step;
  for (; v <= hi + step * 1e-6; v += step) out.push(Math.round(v / step) * step);
  return out;
}
function logTicks(lo, hi) {
  var out = [];
  for (var p = Math.floor(Math.log10(lo)); p <= Math.ceil(Math.log10(hi)); p++)
    for (var m = 1; m < 10; m++) {
      var v = m * Math.pow(10, p);
      if (v >= lo * 0.999 && v <= hi * 1.001 && (m === 1 || m === 2 || m === 5)) out.push(v);
    }
  return out;
}

function chart(host, cfg) {
  var W = cfg.width || 760, H = cfg.height || 300;
  var m = { l: cfg.ml || 62, r: cfg.mr || 16, t: 14, b: cfg.mb || 44 };
  var iw = W - m.l - m.r, ih = H - m.t - m.b;
  var xs = [], ys = [];
  cfg.series.forEach(function (s) {
    s.points.forEach(function (p) {
      if (isFinite(p[0])) xs.push(p[0]);
      if (isFinite(p[1])) ys.push(p[1]);
    });
  });
  if (!xs.length) { host.innerHTML = '<p class="srcnote">sin datos</p>'; return; }
  var x0 = cfg.xdomain ? cfg.xdomain[0] : Math.min.apply(null, xs);
  var x1 = cfg.xdomain ? cfg.xdomain[1] : Math.max.apply(null, xs);
  var y0 = cfg.ydomain ? cfg.ydomain[0] : Math.min.apply(null, ys);
  var y1 = cfg.ydomain ? cfg.ydomain[1] : Math.max.apply(null, ys);
  if (!cfg.ydomain) { var pad = (y1 - y0) * 0.08 || Math.abs(y1) * .1 || 1; y0 -= pad; y1 += pad; }
  if (cfg.ylog) { y0 = Math.max(y0, Math.min.apply(null, ys.filter(function (v) { return v > 0; }))); }
  if (x1 === x0) x1 = x0 + 1;
  if (y1 === y0) y1 = y0 + 1;
  function X(v) {
    return cfg.xlog ? m.l + iw * (Math.log10(v) - Math.log10(x0)) / (Math.log10(x1) - Math.log10(x0))
                    : m.l + iw * (v - x0) / (x1 - x0);
  }
  function Y(v) {
    return cfg.ylog ? m.t + ih - ih * (Math.log10(v) - Math.log10(y0)) / (Math.log10(y1) - Math.log10(y0))
                    : m.t + ih - ih * (v - y0) / (y1 - y0);
  }
  var s = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' +
          (cfg.aria || cfg.ylabel || "gráfico") + '" style="width:100%;height:auto;font-family:var(--mono)">';
  var xt = cfg.xticks ? cfg.xticks
         : cfg.xlog ? logTicks(x0, x1) : niceTicks(x0, x1, cfg.nx || 6);
  var yt = cfg.ylog ? logTicks(y0, y1) : niceTicks(y0, y1, cfg.ny || 5);
  yt.forEach(function (v) {
    s += '<line x1="' + m.l + '" y1="' + Y(v).toFixed(1) + '" x2="' + (m.l + iw) +
         '" y2="' + Y(v).toFixed(1) + '" stroke="var(--rule)" stroke-width="1"/>';
    s += '<text x="' + (m.l - 8) + '" y="' + (Y(v) + 3.5).toFixed(1) +
         '" text-anchor="end" font-size="10" fill="var(--ink-3)">' +
         (cfg.yfmt ? cfg.yfmt(v) : num(v, cfg.yd === undefined ? 2 : cfg.yd)) + "</text>";
  });
  xt.forEach(function (v) {
    s += '<line x1="' + X(v).toFixed(1) + '" y1="' + (m.t + ih) + '" x2="' + X(v).toFixed(1) +
         '" y2="' + (m.t + ih + 4) + '" stroke="var(--rule-2)" stroke-width="1"/>';
    s += '<text x="' + X(v).toFixed(1) + '" y="' + (m.t + ih + 17) +
         '" text-anchor="middle" font-size="10" fill="var(--ink-3)">' +
         (cfg.xfmt ? cfg.xfmt(v) : num(v, cfg.xd === undefined ? 0 : cfg.xd)) + "</text>";
  });
  s += '<line x1="' + m.l + '" y1="' + (m.t + ih) + '" x2="' + (m.l + iw) + '" y2="' + (m.t + ih) +
       '" stroke="var(--rule-2)" stroke-width="1.2"/>';
  if (cfg.hline !== undefined)
    s += '<line x1="' + m.l + '" y1="' + Y(cfg.hline).toFixed(1) + '" x2="' + (m.l + iw) +
         '" y2="' + Y(cfg.hline).toFixed(1) + '" stroke="var(--ink-3)" stroke-width="1" stroke-dasharray="4 3"/>';
  cfg.series.forEach(function (ser, i) {
    var col = ser.color || cvar(i);
    var pts = ser.points.filter(function (p) { return isFinite(p[0]) && isFinite(p[1]); });
    if (ser.kind === "scatter") {
      pts.forEach(function (p) {
        s += '<circle cx="' + X(p[0]).toFixed(1) + '" cy="' + Y(p[1]).toFixed(1) + '" r="' +
             (p[2] || ser.r || 4) + '" fill="' + col + '" fill-opacity="' + (ser.op || .72) +
             '" stroke="' + col + '" stroke-width="1"/>';
      });
    } else if (ser.kind === "bar") {
      var bw = Math.max(3, iw / pts.length * 0.62);
      pts.forEach(function (p) {
        var yy = Y(Math.max(p[1], y0 < 0 ? 0 : y0));
        var yb = Y(y0 < 0 ? 0 : y0);
        s += '<rect x="' + (X(p[0]) - bw / 2).toFixed(1) + '" y="' + Math.min(yy, yb).toFixed(1) +
             '" width="' + bw.toFixed(1) + '" height="' + Math.abs(yb - yy).toFixed(1) +
             '" fill="' + col + '" fill-opacity=".8"/>';
      });
    } else {
      var d = pts.map(function (p, j) { return (j ? "L" : "M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1); }).join(" ");
      s += '<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="' +
           (ser.w || 1.9) + '" stroke-linejoin="round" stroke-linecap="round"' +
           (ser.dash ? ' stroke-dasharray="' + ser.dash + '"' : "") + "/>";
      if (ser.dots) pts.forEach(function (p) {
        s += '<circle cx="' + X(p[0]).toFixed(1) + '" cy="' + Y(p[1]).toFixed(1) +
             '" r="2.8" fill="' + col + '"/>';
      });
    }
  });
  if (cfg.annot) cfg.annot.forEach(function (a) {
    s += '<text x="' + X(a.x).toFixed(1) + '" y="' + Y(a.y).toFixed(1) + '" font-size="10.5" fill="' +
         (a.color || "var(--ink-2)") + '" text-anchor="' + (a.anchor || "start") + '">' + a.t + "</text>";
  });
  if (cfg.xlabel)
    s += '<text x="' + (m.l + iw / 2) + '" y="' + (H - 4) +
         '" text-anchor="middle" font-size="10.5" fill="var(--ink-2)" font-family="var(--sans)">' + cfg.xlabel + "</text>";
  if (cfg.ylabel)
    s += '<text transform="translate(13,' + (m.t + ih / 2) + ') rotate(-90)" text-anchor="middle" ' +
         'font-size="10.5" fill="var(--ink-2)" font-family="var(--sans)">' + cfg.ylabel + "</text>";
  s += "</svg>";
  host.innerHTML = s;
}
function legend(host, items) {
  host.innerHTML = items.map(function (it, i) {
    return '<span><i style="background:' + (it.color || cvar(i)) + '"></i>' + it.name + "</span>";
  }).join("");
}

/* ───────────────────────── FFT ───────────────────────── */
function fft(re, im) {
  var n = re.length;
  for (var i = 1, j = 0; i < n; i++) {
    var bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) { var t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
  }
  for (var len = 2; len <= n; len <<= 1) {
    var ang = -2 * Math.PI / len, wr = Math.cos(ang), wi = Math.sin(ang);
    for (var s = 0; s < n; s += len) {
      var cr = 1, ci = 0;
      for (var k = 0; k < len / 2; k++) {
        var ur = re[s + k], ui = im[s + k];
        var vr = re[s + k + len / 2] * cr - im[s + k + len / 2] * ci;
        var vi = re[s + k + len / 2] * ci + im[s + k + len / 2] * cr;
        re[s + k] = ur + vr; im[s + k] = ui + vi;
        re[s + k + len / 2] = ur - vr; im[s + k + len / 2] = ui - vi;
        var ncr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = ncr;
      }
    }
  }
}
function spectrum(sig, dt) {
  var n = 1; while (n * 2 <= sig.length) n *= 2;
  var mean = 0, i;
  for (i = 0; i < n; i++) mean += sig[i];
  mean /= n;
  var re = new Float64Array(n), im = new Float64Array(n);
  for (i = 0; i < n; i++) re[i] = (sig[i] - mean) * (0.5 - 0.5 * Math.cos(2 * Math.PI * i / (n - 1)));
  fft(re, im);
  var out = [];
  for (i = 1; i < n / 2; i++) out.push([i / (n * dt), Math.sqrt(re[i] * re[i] + im[i] * im[i])]);
  return out;
}

/* ───────────────────────── física en el navegador ───────────────────────── */
var MAT = {
  steel: { E: 210e9, nu: 0.29, n: "Acero" },
  wc: { E: 600e9, nu: 0.22, n: "WC" },
  si3n4: { E: 310e9, nu: 0.27, n: "Si₃N₄" }
};
var G11 = { E: 20e9, nu: 0.20 };
function hertz(E_kin, m, R, tip) {
  var Es = 1 / ((1 - tip.nu * tip.nu) / tip.E + (1 - G11.nu * G11.nu) / G11.E);
  var k = (4 / 3) * Es * Math.sqrt(R);
  var v = Math.sqrt(2 * E_kin / m);
  var delta = Math.pow(5 * E_kin / (2 * k), 0.4);
  var F = k * Math.pow(delta, 1.5);
  var a = Math.sqrt(R * delta);
  var pmax = 1.5 * F / (Math.PI * a * a);
  var tc = 2.943 * Math.pow(5 * m / (4 * k), 0.4) * Math.pow(v, -0.2);
  return { Es: Es, v: v, delta: delta, F: F, a: a, pmax: pmax, tc: tc };
}

/* ───────────────────────── arranque ───────────────────────── */
function buildTOC() {
  var toc = document.getElementById("toc");
  document.querySelectorAll("main section").forEach(function (sec) {
    var eb = sec.querySelector(".eyebrow");
    var h = sec.querySelector("h2");
    if (!h) return;
    var raw = eb ? eb.textContent.trim() : "";
    var numTxt = raw.split("·")[0].trim();
    var a = el("a", { href: "#" + sec.id }, []);
    a.appendChild(el("span", null, [numTxt]));
    a.appendChild(el("i", { style: "font-style:normal" }, [h.textContent]));
    toc.appendChild(a);
  });
  var links = Array.prototype.slice.call(toc.querySelectorAll("a"));
  var secs = Array.prototype.slice.call(document.querySelectorAll("main section"));
  function onScroll() {
    var y = window.scrollY + 130, cur = 0;
    secs.forEach(function (s, i) { if (s.offsetTop <= y) cur = i; });
    links.forEach(function (l, i) { l.classList.toggle("on", i === cur); });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

function themeToggle() {
  var btn = document.getElementById("themebtn");
  btn.addEventListener("click", function () {
    var r = document.documentElement;
    var cur = r.getAttribute("data-theme");
    var dark = cur ? cur === "dark"
      : window.matchMedia("(prefers-color-scheme: dark)").matches;
    r.setAttribute("data-theme", dark ? "light" : "dark");
    redraw();
  });
}

function seg(id, onPick) {
  var host = document.getElementById(id);
  if (!host) return;
  host.addEventListener("click", function (ev) {
    var b = ev.target.closest("button");
    if (!b) return;
    host.querySelectorAll("button").forEach(function (x) {
      x.setAttribute("aria-pressed", String(x === b));
    });
    onPick(b.getAttribute("data-v"), b);
  });
}
function segValue(id) {
  var b = document.querySelector("#" + id + " button[aria-pressed=true]");
  return b ? b.getAttribute("data-v") : null;
}

var redrawFns = [];
function redraw() { redrawFns.forEach(function (f) { try { f(); } catch (e) { console.error(e); } }); }

/* ═════════════════════════ SECCIONES ═════════════════════════ */

function secVerdicts() {
  var a = D.anchors || {}, dmg = D.damage || {}, cat = D.catalog || [];
  var b1 = cat[4] || {}, mc = (D.montecarlo && D.montecarlo.escenarios) || {};
  var sear = mc["traba mecánica (sear)"] || {};
  var items = [
    { k: "Verificación", v: (a.n_ok || 0) + "/" + (a.n_total || 0),
      n: "casos ancla del brief §9 reproducidos dentro de tolerancia" },
    { k: "Energía en 10×10×60", v: num(b1.E_max_mJ, 0) + "<small> mJ</small>",
      n: "acumulador de torsión plegado, contra 2,3 mJ de la palanca en L" },
    { k: "Energía sin dañar", v: num((dmg.severidad_constante || [])[4] && dmg.severidad_constante[4].E_mJ, 0) + "<small> mJ</small>",
      n: "con punta de R = 12 mm, a la misma severidad que tu ensayo de la bola" },
    { k: "Error de energía", v: num(sear.error_residual_medicion_pct, 2) + "<small> %</small>",
      n: "en la magnitud reportada, con el lanzador dispersando 3 %" }
  ];
  document.getElementById("verdicts").innerHTML = items.map(function (i) {
    return '<div class="verdict"><div class="k">' + i.k + '</div><div class="v">' + i.v +
           '</div><div class="n">' + i.n + "</div></div>";
  }).join("");
  var badge = document.getElementById("anchor-badge");
  if (badge) badge.innerHTML = (a.n_ok || 0) + "/" + (a.n_total || 0) + " anclas OK";
  var gd = document.getElementById("gendate");
  if (gd) gd.textContent = D._meta ? D._meta.fecha : "";
}

function secAnchors() {
  var a = D.anchors; if (!a) return;
  table(document.getElementById("anchors-table"), [
    { h: "Caso ancla", k: "caso" },
    { h: "Obtenido", f: function (r) { return num(r.obtenido, Math.abs(r.obtenido) > 100 ? 1 : 4); } },
    { h: "Objetivo", f: function (r) { return num(r.objetivo, Math.abs(r.objetivo) > 100 ? 1 : 4); } },
    { h: "Unidad", k: "unidad" },
    { h: "Error", f: function (r) { return num(r.error_pct, 3) + " %"; } },
    { h: "", f: function (r) { return pill(r.ok ? "OK" : "FALLA", r.ok ? "ok" : "crit"); } }
  ], a.filas, { compact: true });

  var lands = [[2, 4736], [3, 5064], [5, 6094], [8, 7518], [12, 11017]];
  table(document.getElementById("land-table"), [
    { h: "Ancho del apoyo de cola de milano", f: function (r) { return num(r[0], 0) + " mm"; } },
    { h: "f₁ cuña asentada", f: function (r) { return num(r[1], 0) + " Hz"; } },
    { h: "Respecto del empotrado ideal (9376 Hz)", f: function (r) { return num(100 * (r[1] / 9376 - 1), 1) + " %"; } }
  ], lands, { compact: true });
}

function secFamily() {
  var cat = D.catalog || [];
  var rows = [
    { f: "A · cañón radial", alt: "≈55 mm radiales", e: (cat[0] || {}).E_max_mJ, s: 22,
      fit: false, trl: 8, nota: "arquitectura de sonda Leeb; la más madura" },
    { f: "B · módulo acostado", alt: "10 mm radiales", e: (cat[4] || {}).E_max_mJ, s: 4.5,
      fit: true, trl: 5, nota: "acumulador de torsión; entra en el chasis del brief" }
  ];
  table(document.getElementById("family-table"), [
    { h: "Familia", k: "f" },
    { h: "Espacio radial requerido", k: "alt" },
    { h: "Carrera de aceleración", f: function (r) { return num(r.s, 1) + " mm"; } },
    { h: "Energía máxima", f: function (r) { return num(r.e, 0) + " mJ"; } },
    { h: "¿Entra en 10 mm?", f: function (r) { return pill(r.fit ? "sí" : "no", r.fit ? "ok" : "crit"); } },
    { h: "Madurez (TRL)", f: function (r) { return r.trl; } },
    { h: "Nota", k: "nota" }
  ], rows);
}

function secDamage() {
  var d = D.damage; if (!d) return;
  table(document.getElementById("severity-table"), [
    { h: "Radio de la punta", f: function (r) { return num(r.R_mm, 0) + " mm"; } },
    { h: "Energía admisible a 900 MPa", f: function (r) { return num(r.E_mJ, 2) + " mJ"; } },
    { h: "Veces la energía del ensayo de la bola", f: function (r) { return "×" + num(r.factor_vs_ancla, 1); } },
    { h: "Clase de equipo comparable", f: function (r) {
        var e = r.E_mJ;
        if (e < 3) return "por debajo de Leeb C";
        if (e < 11.5) return "Leeb C (3 mJ)";
        if (e < 90) return "Leeb D (11,5 mJ)";
        if (e < 1356) return "Leeb G (90 mJ)";
        return "umbral Westinghouse (1356 mJ)";
      } }
  ], d.severidad_constante);

  table(document.getElementById("damage-table"), [
    { h: "Radio", f: function (r) { return num(r.R_mm, 0) + " mm"; } },
    { h: "Elástico puro (< 640 MPa)", f: function (r) { return num(r.E_elastico_640_mJ, 2); } },
    { h: "Shakedown (< 1024 MPa)", f: function (r) { return num(r.E_shakedown_1024_mJ, 1); } },
    { h: "Antes de marca visible (< 1800 MPa)", f: function (r) { return num(r.E_visible_1800_mJ, 0); } }
  ], d.limites, { compact: true });

  table(document.getElementById("tip-table"), [
    { h: "Material de la punta", k: "material" },
    { h: "E* con G11", f: function (r) { return num(r.E_star_GPa, 2) + " GPa"; } },
    { h: "Δ respecto del acero", f: function (r) { return num(r.delta_E_star_pct, 1) + " %"; } },
    { h: "p_max a 60 mJ, R=12", f: function (r) { return num(r.p_max_MPa, 0) + " MPa"; } },
    { h: "t_c", f: function (r) { return num(r.t_c_us, 1) + " µs"; } }
  ], d.puntas);
}

function toolHertz() {
  var out = document.getElementById("hz-out"), bar = document.getElementById("hz-bar");
  if (!out) return;
  function upd() {
    var E = parseFloat(document.getElementById("hz-E").value) * 1e-3;
    var m = parseFloat(document.getElementById("hz-m").value) * 1e-3;
    var R = parseFloat(document.getElementById("hz-R").value) * 1e-3;
    var tip = MAT[segValue("hz-tip") || "wc"];
    document.getElementById("hz-E-v").textContent = num(E * 1e3, 1) + " mJ";
    document.getElementById("hz-m-v").textContent = num(m * 1e3, 1) + " g";
    document.getElementById("hz-R-v").textContent = num(R * 1e3, 1) + " mm";
    var h = hertz(E, m, R, tip);
    var reg = h.pmax < 640e6 ? ["elástico · sin marca", "ok"]
            : h.pmax < 1024e6 ? ["shakedown · sin acumulación", "ok"]
            : h.pmax < 1800e6 ? ["fluencia local · marca leve acumulativa", "warn"]
            : ["plastificación · indentación visible", "crit"];
    var cells = [
      ["velocidad", num(h.v, 2) + " m/s"], ["fuerza pico", num(h.F, 0) + " N"],
      ["presión pico", num(h.pmax / 1e6, 0) + " MPa"], ["indentación", num(h.delta * 1e6, 1) + " µm"],
      ["duración", num(h.tc * 1e6, 1) + " µs"], ["banda 1/2t_c", num(0.5 / h.tc / 1e3, 1) + " kHz"],
      ["huella 2a", num(2 * h.a * 1e3, 2) + " mm"], ["impulso", num(m * h.v * 1e3, 2) + " mN·s"]
    ];
    out.innerHTML = cells.map(function (c) {
      return '<div><div class="k">' + c[0] + '</div><div class="v">' + c[1] + "</div></div>";
    }).join("");
    var frac = Math.min(1, h.pmax / 2200e6);
    bar.innerHTML =
      '<div style="font-family:var(--sans);font-size:.78rem;margin-bottom:6px;color:var(--ink-2)">Régimen de contacto en el G11 ' +
      pill(reg[0], reg[1]) + "</div>" +
      '<div style="position:relative;height:26px;border:1px solid var(--rule);border-radius:3px;overflow:hidden;background:var(--surface-2)">' +
      '<div style="position:absolute;left:0;top:0;bottom:0;width:' + (640 / 2200 * 100) + '%;background:var(--ok-soft)"></div>' +
      '<div style="position:absolute;left:' + (640 / 2200 * 100) + '%;top:0;bottom:0;width:' + ((1800 - 640) / 2200 * 100) + '%;background:var(--warn-soft)"></div>' +
      '<div style="position:absolute;left:' + (1800 / 2200 * 100) + '%;top:0;bottom:0;right:0;background:var(--crit-soft)"></div>' +
      '<div style="position:absolute;left:' + (frac * 100) + '%;top:-2px;bottom:-2px;width:3px;background:var(--ink)"></div>' +
      "</div>" +
      '<div style="display:flex;justify-content:space-between;font-family:var(--mono);font-size:.66rem;color:var(--ink-3);margin-top:4px">' +
      "<span>0</span><span>640 MPa</span><span>1024</span><span>1800</span><span>2200</span></div>";
  }
  ["hz-E", "hz-m", "hz-R"].forEach(function (id) {
    document.getElementById(id).addEventListener("input", upd);
  });
  seg("hz-tip", upd);
  upd();
}

function secTransmission() {
  var a = D.accumulators; if (!a) return;
  table(document.getElementById("transmission-table"), [
    { h: "Relación i = v_proyectil / v_accionamiento", f: function (r) { return num(r.i, 3); } },
    { h: "Inercia reflejada de 2 g", f: function (r) { return num(2 / (r.i * r.i), 2) + " g"; } },
    { h: "Energía que llega al proyectil de 8 g", f: function (r) { return num(100 * r.eff, 1) + " %"; } },
    { h: "", f: function (r) {
        return r.eff > .9 ? pill("directo", "ok") : r.eff > .7 ? pill("aceptable", "warn")
                                                              : pill("descartado", "crit");
      } }
  ], a.transmision, { compact: true });

  table(document.getElementById("specific-table"), [
    { h: "Modo de almacenamiento", k: "n" },
    { h: "Densidad de energía", f: function (r) { return num(r.v / 1e3, 0) + " kJ/m³"; } },
    { h: "Relativo a la torsión", f: function (r) { return "×" + num(r.v / D.accumulators.densidad_especifica.torsion_pura_J_m3, 2); } },
    { h: "Dónde se usa", k: "u" }
  ], [
    { n: "Torsión pura (barra, alambre de resorte)", v: a.densidad_especifica.torsion_pura_J_m3, u: "resorte helicoidal y barra de torsión" },
    { n: "Flexión, sección prismática", v: a.densidad_especifica.flexion_prismatica_J_m3, u: "ballesta simple" },
    { n: "Flexión, viga de igual resistencia", v: a.densidad_especifica.flexion_igual_resistencia_J_m3, u: "ballesta triangular" },
    { n: "Tracción pura", v: a.densidad_especifica.traccion_pura_J_m3, u: "no realizable en este envolvente" }
  ]);
}

function secAccumulators() {
  var a = D.accumulators; if (!a) return;
  table(document.getElementById("barrel-table"), [
    { h: "Energía objetivo", f: function (r) { return num(r.E_objetivo_mJ, 0) + " mJ"; } },
    { h: "Carrera", f: function (r) { return num(r.stroke_mm, 0) + " mm"; } },
    { h: "Alambre ⌀", f: function (r) { return num(r.d_mm, 2); } },
    { h: "Espira ⌀", f: function (r) { return num(r.D_mm, 2); } },
    { h: "Espiras", f: function (r) { return num(r.n_a, 1); } },
    { h: "F máx", f: function (r) { return num(r.F2_N, 1) + " N"; } },
    { h: "τ máx", f: function (r) { return num(r.tau_max_MPa, 0); } },
    { h: "Goodman", f: function (r) { return num(r.n_goodman, 2); } },
    { h: "Ocupa", f: function (r) { return num(r.L_occupied_mm, 1) + " mm"; } },
    { h: "Vida", f: function (r) { return pill(r.vida_infinita ? "infinita" : "finita", r.vida_infinita ? "ok" : "crit"); } }
  ], a.canon, { compact: true });

  table(document.getElementById("surge-table"), [
    { h: "Tramos del modelo distribuido", f: function (r) { return "N = " + r.N; } },
    { h: "Velocidad simulada", f: function (r) { return num(r.v_proj_ms, 3) + " m/s"; } },
    { h: "Modelo m/3", f: function (r) { return num(r.v_simple_ms, 3) + " m/s"; } },
    { h: "Error del modelo simple", f: function (r) { return num(r.error_v_pct, 2) + " %"; } },
    { h: "Duración del lanzamiento", f: function (r) { return num(r.t_launch_ms, 2) + " ms"; } },
    { h: "Períodos de surge en el lanzamiento", f: function (r) { return num(r.surge_periods_in_launch, 2); } }
  ], a.surge, { compact: true });

  var tor = a.torsion.filter(function (r) { return Math.abs(r.crank_r_mm - 4) < .01; });
  table(document.getElementById("torsion-table"), [
    { h: "Cigüeñal", f: function (r) { return "r = " + num(r.crank_r_mm, 1) + " mm"; } },
    { h: "Pliegues", f: function (r) { return r.n_folds; } },
    { h: "Módulo", f: function (r) { return num(r.L_modulo_mm, 0) + " mm"; } },
    { h: "Ángulo", f: function (r) { return num(r.phi_deg, 1) + "°"; } },
    { h: "⌀ barra", f: function (r) { return num(r.d_mm, 2) + " mm"; } },
    { h: "Fuerza en el cigüeñal", f: function (r) { return num(r.F_crank_N, 1) + " N"; } },
    { h: "Energía", f: function (r) { return num(r.E_mJ, 0) + " mJ"; } },
    { h: "Altura necesaria", f: function (r) { return num(r.height_needed_mm, 2) + " mm"; } },
    { h: "Inercia reflejada", f: function (r) { return num(r.m_reflected_g, 4) + " g"; } },
    { h: "", f: function (r) { return pill(r.fits_height ? "entra" : "no entra", r.fits_height ? "ok" : "crit"); } }
  ], tor, { compact: true });
}

function secCatalog() {
  var cat = D.catalog || [];
  var host = document.getElementById("cat-table");
  var detail = document.getElementById("cat-detail");
  var filter = "all";
  function render() {
    var rows = cat.filter(function (r) {
      if (filter === "all") return true;
      if (filter === "fit") return r.fits_10mm && r.family !== "X";
      return r.family === filter;
    });
    table(host, [
      { h: "ID", f: function (r) { return '<b style="font-family:var(--sans)">' + r.aid + "</b>"; } },
      { h: "Arquitectura", f: function (r) { return '<span style="font-family:var(--serif)">' + r.name + "</span>"; } },
      { h: "E máx", f: function (r) { return r.E_max_mJ ? num(r.E_max_mJ, 0) + " mJ" : "—"; } },
      { h: "Carrera", f: function (r) { return num(r.stroke_mm, 1) + " mm"; } },
      { h: "10 mm", f: function (r) { return pill(r.fits_10mm ? "sí" : "no", r.fits_10mm ? "ok" : "neutral"); } },
      { h: "Vuelo libre", f: function (r) {
          var t = r.free_flight, c = /limpio/.test(t) ? "ok" : /comprometido/.test(t) ? "warn" : "crit";
          return pill(t.split("(")[0].trim(), c);
        } },
      { h: "Parásitas", f: function (r) { return num(r.parasitic_pct_weight, 1) + " %"; } },
      { h: "TRL", k: "trl" },
      { h: "Desgaste", f: function (r) { return '<span style="font-family:var(--serif);font-size:.8rem">' + r.wear_parts + "</span>"; } }
    ], rows, {
      rowAttr: function (r) { return { "data-aid": r.aid, style: "cursor:pointer" }; }
    });
  }
  host.addEventListener("click", function (ev) {
    var tr = ev.target.closest("tr[data-aid]");
    if (!tr) return;
    var r = cat.filter(function (x) { return x.aid === tr.getAttribute("data-aid"); })[0];
    if (!r) return;
    detail.innerHTML =
      '<div style="border:1px solid var(--rule-2);border-radius:4px;padding:18px 20px;margin-top:16px;background:var(--surface-2)">' +
      '<div style="font-family:var(--sans);font-weight:700;font-size:1.05rem;margin-bottom:8px">' + r.aid + " · " + r.name + "</div>" +
      '<p style="font-size:.92rem;margin:0 0 14px;max-width:70ch">' + r.principle + "</p>" +
      '<div class="cols2">' +
      '<div><h4 style="margin-top:0;color:var(--ok)">A favor</h4><ul style="font-size:.88rem;padding-left:1.1em;margin:0">' +
      r.pros.map(function (p) { return "<li>" + p + "</li>"; }).join("") + "</ul></div>" +
      '<div><h4 style="margin-top:0;color:var(--crit)">En contra</h4><ul style="font-size:.88rem;padding-left:1.1em;margin:0">' +
      r.cons.map(function (p) { return "<li>" + p + "</li>"; }).join("") + "</ul></div></div></div>";
    detail.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
  seg("cat-filter", function (v) { filter = v; render(); });
  render();
}

function secSpec() {
  var cat = D.catalog || [], b1 = cat[4] || {}, det = b1.detail || {};
  var rows = [
    ["Envolvente", "10 × 10 × 60 mm", "el eje de 60 mm va a lo largo del eje del generador"],
    ["Acumulador", "barra de torsión en U, ⌀" + num(det.d_mm, 2) + " mm, " + num(det.L_active_mm, 0) + " mm activos", "acero de resorte granallado, τ_adm 600 MPa"],
    ["Ángulo de trabajo", num(det.phi_deg, 1) + "°", "cigüeñal r = " + num(det.crank_r_mm, 1) + " mm"],
    ["Energía máxima", num(det.E_mJ, 0) + " mJ", "programable de 2 a " + num(det.E_mJ, 0) + " mJ por profundidad de amartillado"],
    ["Energía nominal", "60 mJ", "entre Leeb D (11,5) y Leeb G (90)"],
    ["Proyectil", "4,0 g · placa 6 × 3 × 28 mm", "rama ascendente de transferencia en los dos vanos"],
    ["Punta", "calota esférica R = 12 mm, WC-Co", "p_max 980 MPa a 60 mJ: bajo el límite de shakedown"],
    ["Carrera de aceleración", num(det.stroke_mm, 1) + " mm", "íntegramente dentro del volumen"],
    ["Vuelo libre", "2 a 4 mm", "fuerzas parásitas 0,56 % del peso"],
    ["Fuerza en el cigüeñal", num(det.F_crank_N, 1) + " N", "reacción sobre el chasis durante 1,3 ms"],
    ["Inercia reflejada", num(det.m_reflected_g, 4) + " g", "contra 2,41 g de la palanca en L"],
    ["Altura ocupada por el mecanismo", num(det.height_needed_mm, 2) + " mm", "carrera + ⌀ barra + holgura"],
    ["Sensor de posición", "inductivo por corrientes de Foucault, blanco de aluminio", "0,5 µm rms, 1 MSPS"],
    ["Cadencia", "2 golpes/s", "limitada por el amartillado, no por la térmica"],
    ["Potencia media", "0,35 W", "muy por debajo de cualquier límite térmico"],
    ["Vida de diseño", "10⁷ ciclos", "factor 5 sobre el uso estimado"]
  ];
  table(document.getElementById("spec-table"), [
    { h: "Parámetro", f: function (r) { return r[0]; } },
    { h: "Valor", f: function (r) { return '<b style="font-family:var(--mono)">' + r[1] + "</b>"; } },
    { h: "Nota", f: function (r) { return '<span style="font-family:var(--serif);font-size:.82rem;color:var(--ink-2)">' + r[2] + "</span>"; } }
  ], rows, { compact: true });
}

function secFreeFlight() {
  var f = D.freeflight; if (!f) return;
  var fz = f.fuerzas;
  var rows = [
    { n: "Gravedad (conocida, y medida por el sensor)", v: fz.gravedad_N, p: fz["gravedad_%peso"], c: "neutral" },
    { n: "Arrastre aerodinámico a 4 m/s", v: fz.aero_N, p: fz["aero_%peso"], c: "ok" },
    { n: "Corrientes de Foucault del sensor inductivo", v: fz.eddy_sensor_N, p: fz["eddy_%peso"], c: "ok" },
    { n: "Magnética residual (lanzador de resorte)", v: 0, p: 0, c: "ok" },
    { n: "TOTAL parásitas (todo menos gravedad)", v: fz.parasitas_total_N, p: fz["parasitas_%peso"], c: "ok" },
    { n: "⚠ Si el blanco fuera un imán permanente", v: f.iman_permanente_N, p: f.iman_veces_peso * 100, c: "crit" }
  ];
  table(document.getElementById("ff-table"), [
    { h: "Fuerza durante el tramo libre", k: "n" },
    { h: "Magnitud", f: function (r) { return r.v === 0 ? "0" : r.v.toExponential(2) + " N"; } },
    { h: "Respecto del peso del proyectil", f: function (r) {
        return r.p === 0 ? "0 %" : (r.p < 0.001 ? r.p.toExponential(1) : num(r.p, r.p < 1 ? 3 : 0)) + " %"; } },
    { h: "", f: function (r) { return pill(r.c === "crit" ? "inaceptable" : r.c === "neutral" ? "inevitable" : "despreciable", r.c); } }
  ], rows);

  table(document.getElementById("piston-table"), [
    { h: "Geometría del proyectil", k: "caso" },
    { h: "Longitud de engrane", f: function (r) { return num(r.L_engrane_mm, 1) + " mm"; } },
    { h: "Huelgo radial", f: function (r) { return num(r.clearance_mm * 1000, 0) + " µm"; } },
    { h: "Sobrepresión", f: function (r) { return num(r.dp_Pa, 0) + " Pa"; } },
    { h: "Fuerza de bombeo", f: function (r) { return num(r["F_%peso"], 1) + " % del peso"; } }
  ], f.piston.filter(function (r) { return [100, 250, 600, 1000].indexOf(Math.round(r.clearance_mm * 1000)) >= 0; }),
     { compact: true });

  redrawFns.push(function () {
    var host = document.getElementById("clock-chart");
    if (!host) return;
    chart(host, {
      height: 260, xlabel: "posición horaria del crawler en el bore",
      ylabel: "variación de la energía [%]",
      xdomain: [0, 360], xticks: [0, 60, 120, 180, 240, 300, 360],
      xfmt: function (v) { var h = (v / 30) % 12; return h === 0 ? "12" : String(h); },
      yd: 1, hline: 0,
      aria: "Variación de la energía entregada según la posición horaria del crawler, para las dos familias",
      series: [
        { name: "A", points: f.hora_familiaA.map(function (r) { return [r.clock_deg, r.dE_rel * 100]; }) },
        { name: "B", points: f.hora_familiaB.map(function (r) { return [r.clock_deg, r.dE_rel * 100]; }), color: cvar(1) }
      ],
      annot: [
        { x: 20, y: f.hora_familiaA[0].dE_rel * 100 * 0.85, t: "familia A · carrera 22 mm", color: cvar(0) },
        { x: 20, y: f.hora_familiaB[0].dE_rel * 100 - 0.5, t: "familia B · carrera 4,5 mm", color: cvar(1) }
      ]
    });
  });
}

function secWedge() {
  var ws = D.wedge_states, wf = D.waveforms, mech = D.mechanisms, sep = D.separability;
  if (!ws) return;
  var rows50 = ws.vano_50mm.filter(function (r) { return r.E_mJ === 60; });
  table(document.getElementById("states-table"), [
    { h: "Estado de asiento", k: "estado" },
    { h: "Precarga", f: function (r) { return num(r.precarga_N, 0) + " N"; } },
    { h: "Juego", f: function (r) { return num(r.gap_um, 0) + " µm"; } },
    { h: "Restitución", f: function (r) { return num(r.restitution, 3); } },
    { h: "Índice Leeb", f: function (r) { return num(r.leeb, 0); } },
    { h: "Energía absorbida", f: function (r) { return num(r.eta_absorbed * 100, 1) + " %"; } },
    { h: "t_c primer contacto", f: function (r) { return num(r.t_c1_us, 1) + " µs"; } },
    { h: "Contactos", k: "n_contacts" },
    { h: "Curtosis", f: function (r) { return num(r.kurtosis, 1); } },
    { h: "Pico", f: function (r) { return num(r.a_pk_g, 0) + " g"; } }
  ], rows50, { compact: true });

  if (mech) {
    var m50 = mech.vano_50mm, m100 = mech.vano_100mm;
    var ests = [];
    m50.forEach(function (r) { if (ests.indexOf(r.estado) < 0) ests.push(r.estado); });
    var rows = ests.map(function (e) {
      function g(arr, v) {
        var f = arr.filter(function (r) { return r.estado === e && r.variante === v; })[0];
        return f ? f.restitution : null;
      }
      return { e: e, a: g(m50, "completo"), b: g(m50, "sin fricción de junta"),
               c: g(m100, "completo"), d: g(m100, "sin fricción de junta") };
    });
    table(document.getElementById("mech-table"), [
      { h: "Estado", f: function (r) { return r.e; } },
      { h: "50 mm · modelo completo", f: function (r) { return num(r.a, 3); } },
      { h: "50 mm · sin fricción de junta", f: function (r) { return num(r.b, 3); } },
      { h: "100 mm · modelo completo", f: function (r) { return num(r.c, 3); } },
      { h: "100 mm · sin fricción de junta", f: function (r) { return num(r.d, 3); } }
    ], rows, { compact: true });
  }

  if (sep) {
    var keys = [
      ["kurtosis", "Curtosis de la señal", 1],
      ["t_c1_us", "Duración del primer contacto [µs]", 1],
      ["restitution", "Restitución", 3],
      ["eta_absorbed", "Fracción absorbida", 3],
      ["a_pk_norm", "Pico normalizado por energía", 2],
      ["centroid_Hz", "Centroide espectral [Hz]", 0]
    ];
    var labs = sep.labels;
    var cols = [{ h: "Característica", f: function (r) { return r.name; } }];
    labs.forEach(function (l, i) {
      cols.push({ h: l.split("·")[0].trim(), f: function (r) {
        var s = r.stats[l];
        return s ? num(s.media, r.d) + '<span style="color:var(--ink-3)"> ±' + num(s.sigma, r.d) + "</span>" : "—";
      } });
    });
    cols.push({ h: "d′ extremos", f: function (r) {
      var v = sep.dprime_extremos[r.k];
      if (!isFinite(v)) return pill("binario", "acc");
      return '<b>' + num(v, 2) + "</b>";
    } });
    cols.push({ h: "Monótona", f: function (r) {
      var vals = labs.map(function (l) { return r.stats[l] ? r.stats[l].media : NaN; });
      var inc = true, dec = true;
      for (var i = 1; i < vals.length; i++) { if (vals[i] < vals[i - 1]) inc = false; if (vals[i] > vals[i - 1]) dec = false; }
      return pill(inc || dec ? "sí" : "no", inc || dec ? "ok" : "crit");
    } });
    table(document.getElementById("sep-table"), cols,
      keys.map(function (k) { return { k: k[0], name: k[1], d: k[2], stats: sep.stats[k[0]] || {} }; }),
      { compact: true });
  }

  /* ── visor de formas de onda ── */
  if (wf) {
    var names = Object.keys(wf);
    var sel = { }; names.forEach(function (n, i) { sel[n] = (i === 0 || i === names.length - 1); });
    var host = document.getElementById("wave-states");
    host.innerHTML = names.map(function (n, i) {
      return '<button data-w="' + i + '" aria-pressed="' + (sel[n] ? "true" : "false") + '">' +
             n.split("·")[0].trim() + "</button>";
    }).join("");
    host.addEventListener("click", function (ev) {
      var b = ev.target.closest("button"); if (!b) return;
      var n = names[parseInt(b.getAttribute("data-w"), 10)];
      sel[n] = !sel[n];
      b.setAttribute("aria-pressed", String(sel[n]));
      drawWaves();
    });
    function drawWaves() {
      var sig = segValue("wave-sig") || "a_palp_g";
      var series = [], leg = [];
      names.forEach(function (n, i) {
        if (!sel[n]) return;
        var w = wf[n], pts;
        if (sig === "spec") {
          var dt = (w.t_us[1] - w.t_us[0]) * 1e-6;
          pts = spectrum(w.a_palp_g, dt).filter(function (p) { return p[0] > 300 && p[0] < 45000; });
        } else {
          pts = w.t_us.map(function (t, j) { return [t, w[sig][j]]; })
                      .filter(function (p) { return p[0] <= (sig === "F_N" ? 250 : 1600); });
        }
        series.push({ name: n, points: pts, color: cvar(i), w: 1.5 });
        leg.push({ name: n, color: cvar(i) });
      });
      var isSpec = sig === "spec";
      chart(document.getElementById("wave-chart"), {
        height: 330, series: series,
        xlabel: isSpec ? "frecuencia [Hz]" : "tiempo [µs]",
        ylabel: isSpec ? "amplitud espectral" : ({ a_palp_g: "aceleración en el palpador [g]",
                 F_N: "fuerza de contacto [N]", w_palp_um: "desplazamiento [µm]" })[sig],
        xlog: isSpec, ylog: isSpec, yd: isSpec ? 0 : 0,
        yfmt: isSpec ? function (v) { return v >= 1 ? num(v, 0) : v.toExponential(0); } : null,
        xfmt: isSpec ? function (v) { return v >= 1000 ? num(v / 1000, 0) + "k" : num(v, 0); } : null,
        aria: "Respuesta simulada de la cuña para los estados de ajuste seleccionados"
      });
      var lg = document.getElementById("wave-chart").parentNode.querySelector(".chart-legend");
      if (!lg) { lg = el("div", { class: "chart-legend" }); document.getElementById("wave-chart").after(lg); }
      legend(lg, leg);
    }
    seg("wave-sig", drawWaves);
    redrawFns.push(drawWaves);
  }

  /* ── espacio de características ── */
  if (sep) {
    var fkeys = [["kurtosis", "curtosis"], ["t_c1_us", "t_c [µs]"], ["restitution", "restitución"],
                 ["eta_absorbed", "absorbida"], ["centroid_Hz", "centroide"], ["a_pk_norm", "pico/E"]];
    ["fx", "fy"].forEach(function (id, k) {
      document.getElementById(id).innerHTML = fkeys.map(function (f, i) {
        return '<button data-v="' + f[0] + '" aria-pressed="' + (i === (k ? 2 : 0)) + '">' + f[1] + "</button>";
      }).join("");
    });
    function drawFeat() {
      var xk = segValue("fx") || "kurtosis", yk = segValue("fy") || "restitution";
      var labs = Object.keys(sep.raw);
      chart(document.getElementById("feat-chart"), {
        height: 320,
        xlabel: (fkeys.filter(function (f) { return f[0] === xk; })[0] || [])[1],
        ylabel: (fkeys.filter(function (f) { return f[0] === yk; })[0] || [])[1],
        xd: xk === "restitution" || xk === "eta_absorbed" ? 2 : 0,
        yd: yk === "restitution" || yk === "eta_absorbed" ? 2 : 0,
        aria: "Nube de puntos de las simulaciones con tolerancias, en el espacio de dos características",
        series: labs.map(function (l, i) {
          return { name: l, kind: "scatter", r: 4.2, color: cvar(i),
                   points: sep.raw[l].map(function (r) { return [r[xk], r[yk]]; }) };
        })
      });
      legend(document.getElementById("feat-legend"),
             labs.map(function (l, i) { return { name: l.split("·")[0].trim() + " " + l.split("·")[1], color: cvar(i) }; }));
    }
    seg("fx", drawFeat); seg("fy", drawFeat);
    redrawFns.push(drawFeat);
  }

  /* ── no linealidad con la energía ── */
  redrawFns.push(function () {
    var host = document.getElementById("nl-chart"); if (!host) return;
    var metric = segValue("nl-metric") || "restitution";
    var rows = ws.vano_50mm, ests = [];
    rows.forEach(function (r) { if (ests.indexOf(r.estado) < 0) ests.push(r.estado); });
    chart(host, {
      height: 300, xlabel: "energía del golpe [mJ]", ylabel: metric, xlog: true,
      xfmt: function (v) { return num(v, 0); },
      yd: metric === "restitution" ? 2 : metric === "t_c1_us" ? 0 : 0,
      aria: "Dependencia de la firma con la energía del golpe para cada estado de ajuste",
      series: ests.map(function (e, i) {
        return { name: e, dots: true, color: cvar(i),
                 points: rows.filter(function (r) { return r.estado === e; })
                             .map(function (r) { return [r.E_mJ, r[metric]]; })
                             .sort(function (a, b) { return a[0] - b[0]; }) };
      })
    });
    legend(document.getElementById("nl-legend"),
           ests.map(function (e, i) { return { name: e.split("·")[0].trim(), color: cvar(i) }; }));
  });
  seg("nl-metric", redraw);
}

function secWaveReturn() {
  var w = D.wave_return_sim, sp = D.strike_position;
  if (w) {
    redrawFns.push(function () {
      var host = document.getElementById("wave-scatter"); if (!host) return;
      var groups = {};
      w.forEach(function (r) {
        var k = r.m_g <= 4 ? "maza 2–4 g" : r.m_g <= 8 ? "maza 8 g" : "maza 16–24 g";
        (groups[k] = groups[k] || []).push(r);
      });
      chart(host, {
        height: 320, xlabel: "t_c / t_retorno", ylabel: "Δ restitución entre ajustada y floja",
        xd: 2, yd: 2, hline: 0,
        aria: "Diferencia de restitución entre cuña ajustada y floja contra la relación entre duración de contacto y tiempo de retorno de la onda",
        series: Object.keys(groups).map(function (k, i) {
          return { name: k, kind: "scatter", color: cvar(i),
                   points: groups[k].map(function (r) { return [r.ratio, r.delta_e, 3 + r.m_g / 5]; }) };
        }),
        annot: [{ x: 0.42, y: 0.045, t: "régimen ciego: Δe = 0,000", color: "var(--crit)" }]
      });
      legend(document.getElementById("wave-legend"),
             Object.keys(groups).map(function (k, i) { return { name: k, color: cvar(i) }; }));
    });
  }
  if (sp) {
    var rows = sp.vano_50mm.filter(function (r) { return r.m_g === 8; });
    var xs = []; rows.forEach(function (r) { if (xs.indexOf(r.x_rel) < 0) xs.push(r.x_rel); });
    var ests = []; rows.forEach(function (r) { if (ests.indexOf(r.estado) < 0) ests.push(r.estado); });
    var data = xs.map(function (x) {
      var o = { x: x };
      ests.forEach(function (e, i) {
        var r = rows.filter(function (q) { return q.x_rel === x && q.estado === e; })[0];
        o["e" + i] = r ? r.restitution : null;
        o["k" + i] = r ? r.kurtosis : null;
      });
      return o;
    });
    var cols = [{ h: "Posición del golpe", f: function (r) { return num(r.x * 100, 0) + " % del vano"; } }];
    ests.forEach(function (e, i) {
      cols.push({ h: "e · " + e.split("·")[0].trim(), f: function (r) { return num(r["e" + i], 3); } });
    });
    ests.forEach(function (e, i) {
      cols.push({ h: "curtosis · " + e.split("·")[0].trim(), f: function (r) { return num(r["k" + i], 1); } });
    });
    table(document.getElementById("strike-table"), cols, data, { compact: true });
  }
}

function secMass() {
  var mech = D.mechanisms, ms = D.mass_sim;
  if (mech && mech.cruce_formula_cerrada) {
    var rows = mech.cruce_formula_cerrada.filter(function (r) { return r.vano_mm === 50 && (r.E_mJ === 20 || r.E_mJ === 60); });
    table(document.getElementById("cross-table"), [
      { h: "Energía", f: function (r) { return num(r.E_mJ, 0) + " mJ"; } },
      { h: "Masa de la maza", f: function (r) { return num(r.m_g, 0) + " g"; } },
      { h: "m / m_eff", f: function (r) { return num(r.m_g / 9.77, 2); } },
      { h: "η fórmula §4.6", f: function (r) { return num(r.eta_cerrada, 3); } },
      { h: "η simulación", f: function (r) { return num(r.eta_simulada, 3); } },
      { h: "Error", f: function (r) {
          var e = 100 * (r.eta_cerrada - r.eta_simulada) / r.eta_simulada;
          var c = Math.abs(e) < 15 ? "ok" : Math.abs(e) < 60 ? "warn" : "crit";
          return pill(num(e, 0) + " %", c);
        } },
      { h: "t_c Hertz", f: function (r) { return num(r.t_c_hertz_us, 1) + " µs"; } },
      { h: "t_c simulado", f: function (r) { return num(r.t_c_sim_us, 1) + " µs"; } }
    ], rows, { compact: true });
  }
  if (ms) {
    redrawFns.push(function () {
      var host = document.getElementById("mass-chart"); if (!host) return;
      var span = segValue("ms-span") || "vano_50mm";
      var metric = segValue("ms-metric") || "E_abs_mJ";
      var rows = ms[span].filter(function (r) { return r.E_mJ === 60; });
      var ests = []; rows.forEach(function (r) { if (ests.indexOf(r.estado) < 0) ests.push(r.estado); });
      chart(host, {
        height: 320, xlabel: "masa del proyectil [g]", ylabel: ({
          E_abs_mJ: "energía entregada a la cuña [mJ]", eta: "fracción transferida",
          t_c1_us: "duración del primer contacto [µs]", a_pk_g: "pico de aceleración [g]"
        })[metric], xlog: true, xfmt: function (v) { return num(v, v < 10 ? 0 : 0); },
        yd: metric === "eta" ? 2 : 0,
        aria: "Energía entregada contra masa del proyectil, medida con la simulación no lineal",
        series: ests.map(function (e, i) {
          return { name: e, dots: true, color: cvar(i),
                   points: rows.filter(function (r) { return r.estado === e; })
                               .map(function (r) { return [r.m_g, r[metric]]; }) };
        }),
        annot: metric === "E_abs_mJ" || metric === "eta"
          ? [{ x: 8.6, y: rows[0] ? rows[0][metric] * 0.5 : 0, t: "acantilado", color: "var(--crit)" }] : null
      });
      legend(document.getElementById("mass-legend"),
             ests.map(function (e, i) { return { name: e.split("·")[0].trim() + " " + e.split("·")[1], color: cvar(i) }; }));
    });
    seg("ms-span", redraw); seg("ms-metric", redraw);

    var p50 = ms.vano_50mm.filter(function (r) { return r.E_mJ === 60 && /S0/.test(r.estado); });
    table(document.getElementById("pareto-table"), [
      { h: "Masa", f: function (r) { return num(r.m_g, 1) + " g"; } },
      { h: "Velocidad", f: function (r) { return num(r.v_ms, 2) + " m/s"; } },
      { h: "Energía entregada", f: function (r) { return num(r.E_abs_mJ, 1) + " mJ"; } },
      { h: "Fracción η", f: function (r) { return num(r.eta, 3); } },
      { h: "t_c", f: function (r) { return num(r.t_c1_us, 1) + " µs"; } },
      { h: "Banda 1/2t_c", f: function (r) { return num(r.f_knee_kHz, 1) + " kHz"; } },
      { h: "Pico de aceleración", f: function (r) { return num(r.a_pk_g, 0) + " g"; } },
      { h: "p_max", f: function (r) { return num(r.p_max_MPa, 0) + " MPa"; } },
      { h: "", f: function (r) {
          if (r.m_g >= 8) return pill("después del acantilado", "crit");
          if (r.m_g >= 3 && r.m_g <= 6) return pill("zona de diseño", "ok");
          return pill("subóptima", "neutral");
        } }
    ], p50, { compact: true });
  }
}

function secMC() {
  var mc = D.montecarlo; if (!mc) return;
  var names = Object.keys(mc.escenarios);
  document.getElementById("mc-scn").innerHTML = names.map(function (n, i) {
    return '<button data-v="' + n + '" aria-pressed="' + (i === 0) + '">' + n + "</button>";
  }).join("");
  function draw() {
    var n = segValue("mc-scn") || names[0], s = mc.escenarios[n];
    var cells = [
      ["CV del lanzador", num(s.cv_lanzador_pct, 2) + " %"],
      ["Error reportado", num(s.error_residual_medicion_pct, 2) + " %"],
      ["Energía media", num(s.E_normal_mJ.media, 1) + " mJ"],
      ["σ energía", num(s.E_normal_mJ.sigma, 2) + " mJ"],
      ["p5 – p95", num(s.E_normal_mJ.p05, 0) + "–" + num(s.E_normal_mJ.p95, 0)],
      ["CV velocidad", num(s.v_ms.cv_pct, 2) + " %"]
    ];
    document.getElementById("mc-out").innerHTML = cells.map(function (c) {
      return '<div><div class="k">' + c[0] + '</div><div class="v">' + c[1] + "</div></div>";
    }).join("");
    chart(document.getElementById("mc-chart"), {
      height: 250, ml: 150, mb: 40,
      xlabel: "contribución a la varianza [%]", xd: 0,
      aria: "Contribución de cada fuente de variación a la varianza de la energía entregada",
      series: [{ kind: "bar", points: [] }]
    });
    var host = document.getElementById("mc-chart");
    var items = s.sensibilidad.slice(0, 7);
    var maxv = Math.max.apply(null, items.map(function (i) { return i.contrib_var_pct; }));
    host.innerHTML = '<div style="display:grid;gap:7px">' + items.map(function (i) {
      var w = Math.max(1, 100 * i.contrib_var_pct / Math.max(maxv, 1));
      return '<div style="display:grid;grid-template-columns:150px 1fr 56px;gap:10px;align-items:center">' +
        '<span style="font-family:var(--sans);font-size:.78rem;color:var(--ink-2);text-align:right">' + i.variable + "</span>" +
        '<div style="height:16px;background:var(--surface-3);border-radius:2px;overflow:hidden">' +
        '<div style="height:100%;width:' + w + '%;background:var(--accent)"></div></div>' +
        '<span class="num" style="font-size:.78rem">' + num(i.contrib_var_pct, 1) + " %</span></div>";
    }).join("") + "</div>";
  }
  seg("mc-scn", draw);
  redrawFns.push(draw);

  table(document.getElementById("mc-target-table"), [
    { h: "Fuente eliminada", k: "variable" },
    { h: "CV resultante", f: function (r) { return num(r.cv_pct, 2) + " %"; } },
    { h: "Cuánto baja", f: function (r) { return r.delta_pct ? num(r.delta_pct, 2) + " pts" : "—"; } },
    { h: "", f: function (r, i) {
        if (i === 0) return "";
        return r.delta_pct > 0.5 ? pill("apretar acá", "ok")
             : r.delta_pct > 0.2 ? pill("segundo orden", "warn") : pill("no vale la pena", "neutral");
      } }
  ], mc.objetivos, { compact: true });
}

function secReliability() {
  var r = D.reliability; if (!r) return;
  table(document.getElementById("wear-table"), [
    { h: "Carga normal en la guía", f: function (x) { return num(x.F_N, 2) + " N"; } },
    { h: "Distancia deslizada en 10⁷ ciclos", f: function (x) { return num(x.s_km, 0) + " km"; } },
    { h: "Volumen desgastado", f: function (x) { return num(x.V_mm3, 4) + " mm³"; } },
    { h: "Profundidad", f: function (x) { return num(x.profundidad_um, 3) + " µm"; } },
    { h: "", f: function (x) { return pill(x.aceptable ? "aceptable" : "revisar", x.aceptable ? "ok" : "warn"); } }
  ], r.desgaste_guia, { compact: true });

  table(document.getElementById("fmea-table"), [
    { h: "Elemento", k: "item" },
    { h: "Modo de falla", k: "mode" },
    { h: "Efecto", f: function (x) { return '<span style="font-family:var(--serif);font-size:.82rem">' + x.effect + "</span>"; } },
    { h: "S", k: "severity" }, { h: "O", k: "likelihood" }, { h: "D", k: "detection" },
    { h: "RPN", f: function (x) {
        var c = x.rpn >= 150 ? "crit" : x.rpn >= 80 ? "warn" : "ok";
        return pill(String(x.rpn), c);
      } },
    { h: "Mitigación", f: function (x) { return '<span style="font-family:var(--serif);font-size:.82rem">' + x.mitigation + "</span>"; } }
  ], r.fmea, { compact: true });
}

function secSensing() {
  var s = D.sensing; if (!s) return;
  function upd() {
    var sx = parseFloat(document.getElementById("sn-x").value) * 1e-6;
    var fs = parseFloat(document.getElementById("sn-f").value) * 1e3;
    var gap = parseFloat(document.getElementById("sn-g").value) * 1e-3;
    var v = parseFloat(document.getElementById("sn-v").value);
    document.getElementById("sn-x-v").textContent = num(sx * 1e6, 1) + " µm";
    document.getElementById("sn-f-v").textContent = num(fs / 1e3, 0) + " kHz";
    document.getElementById("sn-g-v").textContent = num(gap * 1e3, 1) + " mm";
    document.getElementById("sn-v-v").textContent = num(v, 1) + " m/s";
    var tf = gap / v, tw = 0.5 * tf;
    var N = Math.max(2, Math.round(fs * tw));
    var sv = sx / tw * Math.sqrt(12 * (N - 1) / (N * (N + 1)));
    var sE = 2 * sv / v;
    var cells = [
      ["tiempo de vuelo", num(tf * 1e6, 0) + " µs"],
      ["muestras por tramo", String(N)],
      ["σ velocidad", num(sv * 1e3, 3) + " mm/s"],
      ["σ v relativa", num(100 * sv / v, 4) + " %"],
      ["σ energía", num(100 * sE, 4) + " %"],
      ["resolución de t_c", num(1e6 / fs, 2) + " µs"]
    ];
    document.getElementById("sn-out").innerHTML = cells.map(function (c) {
      return '<div><div class="k">' + c[0] + '</div><div class="v">' + c[1] + "</div></div>";
    }).join("");
  }
  ["sn-x", "sn-f", "sn-g", "sn-v"].forEach(function (id) {
    var e = document.getElementById(id); if (e) e.addEventListener("input", upd);
  });
  upd();

  var d = s.daq;
  table(document.getElementById("daq-table"), [
    { h: "Parámetro", f: function (r) { return r[0]; } },
    { h: "Valor", f: function (r) { return '<b class="num">' + r[1] + "</b>"; } },
    { h: "Criterio", f: function (r) { return '<span style="font-family:var(--serif);font-size:.82rem;color:var(--ink-2)">' + r[2] + "</span>"; } }
  ], [
    ["Frecuencia de muestreo del acelerómetro", num(d.fs_recomendada_kHz, 0) + " kHz", "10× la máxima del espectro y ≥20 muestras en el pulso de contacto"],
    ["Frecuencia de muestreo del sensor de posición", "1 MHz", "para medir t_c con 5 % de resolución sobre 60 µs"],
    ["Antialias analógico", num(d.f_antialias_kHz, 0) + " kHz, " + d.polos_antialias + " polos", "f_s/2,5"],
    ["Resolución del ADC", d.bits_recomendados + " bits", "72 dB de rango dinámico más 2 bits de margen"],
    ["Ventana de registro", num(d.ventana_registro_ms, 2) + " ms", "5 constantes de tiempo del ring-down"],
    ["Muestras por registro", num(d.muestras_por_registro, 0), ""],
    ["Rango del acelerómetro", num(s.acelerometro.rango_comercial_g, 0) + " g", "pico esperado más 6 dB"],
    ["Resonancia de montaje mínima", num(s.acelerometro.f_resonancia_min_kHz, 0) + " kHz", "3× la frecuencia máxima de interés"],
    ["Micrófono", "MEMS ≥ 20 kHz a 15–25 mm", "la cuña es acústicamente compacta: radia como monopolo"]
  ], { compact: true });

  redrawFns.push(function () {
    var host = document.getElementById("palp-chart"); if (!host || !s.palpador) return;
    chart(host, {
      height: 240, xlabel: "frecuencia [Hz]", ylabel: "|H| del palpador",
      xlog: true, ylog: true, hline: 1,
      xfmt: function (v) { return v >= 1000 ? num(v / 1000, 0) + "k" : num(v, 0); },
      yfmt: function (v) { return v >= 1 ? num(v, 0) : num(v, 2); },
      aria: "Transferencia del palpador: por encima de su resonancia de montaje deja de seguir a la cuña",
      series: [{ name: "palpador", points: s.palpador.f_Hz.map(function (f, i) { return [f, s.palpador.H[i]]; }) }],
      annot: [{ x: 14000, y: 0.25, t: "por encima de la resonancia el palpador no sigue", color: "var(--crit)" }]
    });
  });
}

function secPending() {
  table(document.getElementById("dec-table"), [
    { h: "Decisión", f: function (r) { return r[0]; } },
    { h: "De qué depende", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[1] + "</span>"; } },
    { h: "Qué cambia", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[2] + "</span>"; } }
  ], [
    ["Orientación del módulo", "si los 10 mm del brief son chasis o entrehierro con rotor puesto",
     "familia A (más simple, TRL 8) contra familia B (entra en 10 mm, TRL 5). Es la única decisión que bloquea el diseño de detalle."],
    ["Separación requerida entre clases", "qué necesita distinguir el cliente: ¿tres clases o una escala?",
     "dimensiona TODO lo demás. La simulación dice que 3 clases son cómodas y que graduar cuán floja está una cuña floja no se puede."],
    ["Energía nominal de trabajo", "el principio de medición que se adopte",
     "60 mJ es un punto razonable entre Leeb D y Leeb G; el hardware llega a 190 mJ y baja a 2 mJ sin cambios"],
    ["Estrategia de energía", "normalizar las características por la energía medida, o cerrar lazo para entregar siempre la misma",
     "el lazo es mejor para comparar mapas entre máquinas; la normalización es más simple"],
    ["Punta: fija o reemplazable", "cuántos golpes por punta antes de que el radio derive",
     "una punta reemplazable agrega una interfaz mecánica pero permite verificar el radio fuera de máquina"]
  ]);

  table(document.getElementById("unk-table"), [
    { h: "#", f: function (r) { return '<b style="font-family:var(--mono)">' + r[0] + "</b>"; } },
    { h: "Dato faltante", f: function (r) { return r[1]; } },
    { h: "Impacto si se equivoca", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[2] + "</span>"; } },
    { h: "Cómo se consigue", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[3] + "</span>"; } },
    { h: "Estado", f: function (r) { return pill(r[4], r[5]); } }
  ], [
    ["5", "κ, factor de corrección por corte", "±10 % en f₁ de la cuña corta", "resuelto: los dos vanos dan 5/6 de forma independiente", "cerrada", "ok"],
    ["2", "J_L, inercia de la palanca", "±20 % en la energía a la maza del diseño anterior", "reconstruida como barra de acero 3 × 8 mm; sale del CAD en cinco minutos", "reconstruida", "warn"],
    ["6", "E y ν transversales del G11", "entra en Hertz y en el modal; hoy es [E]", "indentación instrumentada con esfera de R = 4 mm sobre probeta", "abierta", "crit"],
    ["—", "Rigidez y precarga del resorte ripple", "define toda la escalera de estados", "ficha del proveedor + ensayo de compresión en el mock-up", "abierta", "crit"],
    ["—", "Ancho y rigidez del apoyo de cola de milano", "mueve f₁ de la cuña asentada de 4,7 a 11 kHz", "medición sobre estator real o plano de fabricación", "abierta", "crit"],
    ["—", "Umbral de daño real del G11", "fija la energía máxima admisible", "escalera de energías con inspección de huella", "abierta", "warn"],
    ["—", "Geometría de la cuña: qué dirección es el vano", "el brief dice 30 mm axiales y a la vez vano de 50–100 mm; son incompatibles", "aclaración de una línea", "abierta", "warn"],
    ["3", "Corriente de pulso máxima del LAH04", "sólo afecta a la línea base con palanca", "consulta a Sensata", "no aplica al módulo nuevo", "neutral"],
    ["4", "Curva K_F(x) real del LAH04", "ídem", "pedido a Sensata", "no aplica al módulo nuevo", "neutral"],
    ["8", "Ancho de ranura y de diente", "envolvente del crawler", "investigación pendiente del proyecto", "abierta", "warn"],
    ["7", "Separación requerida entre clases", "dimensiona todo", "es una decisión, no un dato", "decisión", "crit"]
  ], { compact: true });

  table(document.getElementById("plan-table"), [
    { h: "Paso", f: function (r) { return '<b style="font-family:var(--mono)">' + r[0] + "</b>"; } },
    { h: "Qué se hace", f: function (r) { return r[1]; } },
    { h: "Qué cierra", f: function (r) { return '<span style="font-family:var(--serif);font-size:.85rem">' + r[2] + "</span>"; } }
  ], [
    ["1", "Caracterización estática: rigidez del ripple y precarga contra deflexión", "la escalera de estados deja de ser hipótesis"],
    ["2", "Modal por martillo instrumentado en cada estado", "f₁ real de la cuña asentada y el efecto del ancho de apoyo"],
    ["3", "Indentación instrumentada sobre probeta de G11", "E* real e incógnita #6"],
    ["4", "Escalera de energía con inspección de huella", "umbral de daño y validación del criterio de shakedown"],
    ["5", "30 golpes por estado con v_i, v_r, acelerómetro y micrófono simultáneos", "distribuciones reales de cada característica"],
    ["6", "Repetición con el golpe al 20 %, 30 % y 50 % del vano", "confirma o refuta la recomendación de golpear cerca del apoyo"],
    ["7", "Repetición a dos energías (20 y 60 mJ)", "valida el discriminante no lineal"],
    ["8", "d′ real entre clases y elección del vector de características", "la incógnita #7, que es la que decide si el sistema sirve"]
  ], { compact: true });
}

/* ───────────────────────── init ───────────────────────── */
function init() {
  bindNumbers();
  secVerdicts(); secAnchors(); secFamily(); secDamage(); toolHertz();
  secTransmission(); secAccumulators(); secCatalog(); secSpec();
  secFreeFlight(); secWedge(); secWaveReturn(); secMass(); secMC();
  secReliability(); secSensing(); secPending();
  buildTOC(); themeToggle();
  redraw();
  window.addEventListener("resize", function () {
    clearTimeout(window.__rt); window.__rt = setTimeout(redraw, 200);
  });
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
else init();
})();
