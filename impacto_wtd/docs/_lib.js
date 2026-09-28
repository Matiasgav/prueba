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

