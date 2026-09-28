#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota 02489-00-MC003 - Resorte de torsión simple de cuerda de piano Ø0,50 mm
para un eje de Ø3 mm: 5 N·mm al montar y 10 N·mm tras 60° de recorrido.

Uso (desde esta carpeta):
    python3 calculo.py        # escribe resultados.json y figuras/

Método: Shigley, Diseño en ingeniería mecánica, cap. 10 (resortes de torsión):
  * rigidez con la ec. 10-51 (constante 10,8, incluye la fricción entre espiras);
  * brazos por la ec. 10-47: Ne = Nb + (l1 + l2) / (3·π·D);
  * tensión de flexión en la fibra interior con Ki (ec. 10-43);
  * estática con Sy = 0,78·Sut (cuerda de piano, ec. 10-57);
  * fatiga con la tabla 10-6 (ASTM A228 sin granallar, R = 0) y criterio de Gerber.
"""
import json
import math
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(ROOT, 'figuras')
os.makedirs(FIG, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Requisitos y diseño
# ---------------------------------------------------------------------------
REQ = {
    'T_ini': 5.0,            # N·mm, al montar
    'T_fin': 10.0,           # N·mm, al final del recorrido
    'recorrido': 60.0,       # grados
    'eje': 3.0,              # mm
    'ciclos_mes': 200,
}
DIS = {
    'material': 'Cuerda de piano ASTM A228 (≈ EN 10270-1 SH/DH)',
    'd': 0.50,               # mm
    'ID': 3.60,              # mm, diámetro interior libre
    'l1': 8.0, 'l2': 8.0,    # mm, brazos rectos tangenciales
    'Nb': 9 + 1 / 6,         # espiras del cuerpo: 9 vueltas + 60°
    'E': 203.4e3,            # MPa, cuerda de piano d < 0,8 mm (tabla 10-5)
    'A': 2211.0, 'm': 0.145, # Sut = A / d^m (tabla 10-4)
    'sentido': 'a derechas',
}

d, ID, E = DIS['d'], DIS['ID'], DIS['E']
D = ID + d
OD = D + d
C = D / d
Nb = DIS['Nb']
l1, l2 = DIS['l1'], DIS['l2']

k_req = (REQ['T_fin'] - REQ['T_ini']) / REQ['recorrido']       # N·mm/°
Ne_req = E * d**4 / (10.8 * D * k_req * 360)
Nb_req = Ne_req - (l1 + l2) / (3 * math.pi * D)

Ne = Nb + (l1 + l2) / (3 * math.pi * D)
k_vuelta = E * d**4 / (10.8 * D * Ne)                           # N·mm/vuelta
k = k_vuelta / 360                                              # N·mm/°


def momento(theta):
    """Par [N·mm] con el resorte girado theta [°] desde libre."""
    return k * np.asarray(theta, dtype=float)


th_mont = REQ['T_ini'] / k_req                                  # 60°
th_fin = th_mont + REQ['recorrido']                             # 120°
M_mont, M_fin = float(momento(th_mont)), float(momento(th_fin))


def diam_cargado(theta):
    """Diámetro medio con theta [°] de carga (cierra espiras), ec. 10-54."""
    return D * Nb / (Nb + theta / 360)


D_mont, D_fin = diam_cargado(th_mont), diam_cargado(th_fin)
L0 = d * (Nb + 1)
L_fin = d * (Nb + 1 + th_fin / 360)
largo_alambre = math.pi * D * Nb + l1 + l2
masa = 7.85e-3 * math.pi / 4 * d**2 * largo_alambre             # g

# ángulo entre los brazos (vista axial), brazos tangenciales:
# brazo 1 sale hacia -y en φ = 0; el brazo 2 gira con el extremo de la hélice.
def ang_brazos(theta):
    phi = (360 * Nb + theta) % 360
    return (270 - (phi + 90)) % 360


a_libre, a_mont, a_fin = ang_brazos(0), ang_brazos(th_mont), ang_brazos(th_fin)

# ---------------------------------------------------------------------------
# 2. Tensiones y estática
# ---------------------------------------------------------------------------
Ki = (4 * C**2 - C - 1) / (4 * C * (C - 1))
Sut = DIS['A'] / d**DIS['m']
Sy = 0.78 * Sut


def sigma(M):
    return Ki * 32 * M / (math.pi * d**3)


s_min, s_max = sigma(M_mont), sigma(M_fin)
n_est = Sy / s_max
M_y = Sy * math.pi * d**3 / (32 * Ki)                           # par al límite elástico
th_y = M_y / k

# ---------------------------------------------------------------------------
# 3. Fatiga (Shigley tabla 10-6: A228 sin granallar, R = 0)
# ---------------------------------------------------------------------------
TABLA_106 = {1e5: 0.53, 1e6: 0.50}                              # Sr / Sut
b_sn = math.log10(TABLA_106[1e6] / TABLA_106[1e5])              # pendiente por década


def Sr(N):
    """Resistencia a la fatiga R = 0 [MPa]. Bajo 1e5 se mantiene el valor de
    1e5 (conservador); sobre 1e6 se extrapola la recta log-log de la tabla."""
    N = max(N, 1e5)
    return Sut * TABLA_106[1e5] * (N / 1e5)**b_sn


sa, sm = (s_max - s_min) / 2, (s_max + s_min) / 2
r = sa / sm


def n_fatiga(N):
    Se = (Sr(N) / 2) / (1 - (Sr(N) / 2 / Sut)**2)                # Gerber, R = 0 -> alternada
    Sa = r**2 * Sut**2 / (2 * Se) * (-1 + math.sqrt(1 + (2 * Se / (r * Sut))**2))
    return Sa / sa


# Sr necesaria para n = 1 y ciclos admisibles (extrapolados)
Se_req = sa / (1 - (sm / Sut)**2)
x = Se_req
for _ in range(50):
    x = Se_req * (1 - (x / Sut)**2)
Sr_req = 2 * x
N_adm = 1e5 * (Sr_req / (Sut * TABLA_106[1e5]))**(1 / b_sn)

ciclos_anio = REQ['ciclos_mes'] * 12
anios = [1, 10, 20, 50]
caso_uso = {a: {'N': ciclos_anio * a, 'n_f': n_fatiga(ciclos_anio * a)} for a in anios}
anios_1e6 = 1e6 / ciclos_anio

res = {
    'D': D, 'OD': OD, 'C': C, 'Ki': Ki, 'k_req': k_req, 'Nb_req': Nb_req,
    'Nb': Nb, 'Ne': Ne, 'k': k, 'k_vuelta': k_vuelta,
    'th_mont': th_mont, 'th_fin': th_fin, 'M_mont': M_mont, 'M_fin': M_fin,
    'F_mont': M_mont / l2, 'F_fin': M_fin / l2,
    'ID_mont': D_mont - d, 'ID_fin': D_fin - d, 'holgura_fin': D_fin - d - REQ['eje'],
    'L0': L0, 'L_fin': L_fin, 'largo_alambre': largo_alambre, 'masa_g': masa,
    'ang_brazos': {'libre': a_libre, 'montaje': a_mont, 'final': a_fin},
    'Sut': Sut, 'Sy': Sy, 's_min': s_min, 's_max': s_max, 's_a': sa, 's_m': sm,
    'n_est': n_est, 'M_y': M_y, 'th_y': th_y,
    'Sr_1e5': Sr(1e5), 'Sr_1e6': Sr(1e6), 'n_f_1e6': n_fatiga(1e6),
    'n_f_1e7': n_fatiga(1e7), 'n_f_1e8': n_fatiga(1e8),
    'Sr_req': Sr_req, 'Sr_req_frac': Sr_req / Sut, 'N_adm_extrapolado': N_adm,
    'ciclos_anio': ciclos_anio, 'anios_hasta_1e6': anios_1e6,
    'uso': {str(a): v for a, v in caso_uso.items()},
}
with open(os.path.join(ROOT, 'resultados.json'), 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------------
# 4. Figuras de la nota (mismo estilo que MC001/MC002)
# ---------------------------------------------------------------------------
TXT, TXT2, GRID = '#0b0b0b', '#52514e', '#e4e3df'
AZUL, BANDA = '#2a78d6', '#cde2fb'
_LM = '/usr/share/texmf/fonts/opentype/public/lm/lmroman10-regular.otf'
if os.path.exists(_LM):
    from matplotlib import font_manager
    font_manager.fontManager.addfont(_LM)
    font_manager.fontManager.addfont(_LM.replace('regular', 'bold'))
plt.rcParams.update({'font.family': 'serif',
                     'font.serif': ['Latin Modern Roman', 'DejaVu Serif'],
                     'mathtext.fontset': 'cm', 'font.size': 9,
                     'pdf.fonttype': 42})


def coma(v, dec=2):
    return f'{v:.{dec}f}'.replace('.', ',')


def estilo(ax, xlabel=None, ylabel=None):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color('#b8b7b1')
    ax.tick_params(colors=TXT2, labelsize=8.5)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel, color=TXT2)
    if ylabel:
        ax.set_ylabel(ylabel, color=TXT2)


def guardar(fig, nombre, exts=('pdf', 'png')):
    from matplotlib.ticker import FuncFormatter, ScalarFormatter
    for ax in fig.axes:
        for eje, escala in ((ax.xaxis, ax.get_xscale()), (ax.yaxis, ax.get_yscale())):
            if escala == 'linear' and type(eje.get_major_formatter()) is ScalarFormatter:
                eje.set_major_formatter(FuncFormatter(lambda v, _p: f'{v:g}'.replace('.', ',')))
    for ext in exts:
        fig.savefig(os.path.join(FIG, f'{nombre}.{ext}'), dpi=200,
                    bbox_inches='tight', facecolor='white')
    plt.close(fig)


def fig_momento():
    th = np.linspace(0, 280, 300)
    fig, axs = plt.subplots(2, 1, figsize=(6.4, 5.2), sharex=True,
                            gridspec_kw={'hspace': 0.28})
    for ax, fac, uni, nom in ((axs[0], 1, 'N·mm', 'Par $M$'),
                              (axs[1], 1 / l2, 'N', f'Fuerza $F$ en la punta del brazo ({coma(l2, 0)} mm)')):
        y = momento(th) * fac
        estilo(ax, ylabel=f'{nom.split(" en")[0]} [{uni}]')
        ax.axvspan(th_mont, th_fin, color=BANDA, lw=0, zorder=0)
        ax.axvline(th_y, color=TXT2, lw=1, ls='--')
        ax.plot(th, y, color=AZUL, lw=2)
        for t, M in ((th_mont, M_mont), (th_fin, M_fin)):
            v = M * fac
            ax.plot(t, v, 'o', ms=6, color=AZUL, mec='white', mew=1.5, zorder=4)
            ax.annotate(f'{coma(v)} {uni}', (t, v), xytext=(-8, 8), textcoords='offset points',
                        ha='right', fontsize=8.5, color=TXT)
        ax.set_title(nom, loc='left', color=TXT, fontsize=10)
        ax.set_ylim(0, M_y * fac * 1.12)
    top = axs[0].get_ylim()[1]
    axs[0].text((th_mont + th_fin) / 2, top * 0.93, 'rango de trabajo\n60°–120°',
                ha='center', va='top', fontsize=8.5, color=TXT)
    axs[0].text(th_y - 4, top * 0.06, f'límite elástico\n{coma(M_y, 1)} N·mm a {th_y:.0f}°',
                ha='right', va='bottom', fontsize=8.5, color=TXT2)
    axs[0].text(th_mont - 3, top * 0.55, 'montaje', ha='right', fontsize=8.5, color=TXT2)
    axs[0].text(th_fin + 3, top * 0.55, 'fin de\nrecorrido', ha='left', fontsize=8.5, color=TXT2)
    axs[1].set_xlabel('Giro desde la posición libre $\\theta$ [°]', color=TXT2)
    axs[1].set_xlim(0, 280)
    axs[1].set_xticks(range(0, 281, 30))
    guardar(fig, 'fig_momento')


def fig_fatiga():
    N = np.logspace(3, 9, 400)
    nf = np.array([n_fatiga(n) for n in N])
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    estilo(ax, 'Ciclos $N$', 'Coeficiente de seguridad')
    ax.set_xscale('log')
    dentro = N <= 1e6
    ax.plot(N[dentro], nf[dentro], color=AZUL, lw=2, label='Fatiga (Gerber, tabla 10-6)')
    ax.plot(N[~dentro], nf[~dentro], color=AZUL, lw=2, ls=(0, (4, 3)),
            label='Fatiga, extrapolado más allá de $10^6$')
    ax.axhline(n_est, color=TXT2, lw=1.2, ls='--', label=f'Estático ($S_y$): {coma(n_est)}')
    ax.axhline(1, color='#b8b7b1', lw=1)
    for a, txt in ((1, '1 año'), (20, '20 años')):
        n = ciclos_anio * a
        ax.axvline(n, color=GRID, lw=1, zorder=1)
        ax.plot(n, n_fatiga(n), 'o', ms=5.5, color=AZUL, mec='white', mew=1.2, zorder=4)
        ax.text(n, 0.18, f'{txt}\n{n:,.0f}'.replace(',', '.'), ha='center', fontsize=7.5, color=TXT2)
    ax.plot(1e6, n_fatiga(1e6), 'o', ms=5.5, color=AZUL, mec='white', mew=1.2, zorder=4)
    ax.annotate(f'$10^6$ ciclos = {anios_1e6:.0f} años\n$n_f$ = {coma(n_fatiga(1e6))}',
                (1e6, n_fatiga(1e6)), xytext=(10, -34), textcoords='offset points',
                fontsize=8, color=TXT)
    ax.set_ylim(0, 2.8)
    ax.set_xlim(1e3, 1e9)
    ax.set_title('Coeficiente de seguridad según los ciclos acumulados (200 ciclos/mes)',
                 loc='left', color=TXT, fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc='upper right', labelcolor=TXT)
    guardar(fig, 'fig_fatiga')


# ---------------------------------------------------------------------------
# 5. Geometría 3D del resorte (para el plano)
# ---------------------------------------------------------------------------
def linea_media(theta_carga=0.0, n_seg=40):
    """Puntos de la línea media: brazo 1, hélice, brazo 2 (mm)."""
    Dm = diam_cargado(theta_carga)
    R = Dm / 2
    nb = Nb + theta_carga / 360
    phi_f = 2 * math.pi * nb
    paso = d * 1.02
    br1 = [np.array([R, -l1 * (1 - s), 0.0]) for s in np.linspace(0, 1, 6)]
    phi = np.linspace(0, phi_f, int(n_seg * nb))
    hel = [np.array([R * math.cos(p), R * math.sin(p), paso * p / (2 * math.pi)]) for p in phi]
    pf = hel[-1]
    tf = np.array([-math.sin(phi_f), math.cos(phi_f), 0.0])
    br2 = [pf + tf * l2 * s for s in np.linspace(0, 1, 6)[1:]]
    return np.array(br1[:-1] + hel + br2)


def tubo(pts, radio, n_circ=14):
    """Anillos de un tubo alrededor de la polilínea."""
    anillos = []
    for i, p in enumerate(pts):
        t = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        t = t / np.linalg.norm(t)
        a = np.array([0, 0, 1.0]) if abs(t[2]) < 0.9 else np.array([1.0, 0, 0])
        u = np.cross(t, a); u /= np.linalg.norm(u)
        v = np.cross(t, u)
        ang = np.linspace(0, 2 * math.pi, n_circ, endpoint=False)
        anillos.append([p + radio * (math.cos(g) * u + math.sin(g) * v) for g in ang])
    return np.array(anillos)


def proyectar(P, cam, obj, f):
    """Perspectiva central: devuelve (x, y, profundidad)."""
    w = obj - cam; w /= np.linalg.norm(w)
    u = np.cross(w, [0, 0, 1.0]); u /= np.linalg.norm(u)
    v = np.cross(u, w)
    Q = P - cam
    z = Q @ w
    return np.stack([f * (Q @ u) / z, f * (Q @ v) / z, z], axis=-1)


def dibujar_3d(ax, x0, y0, ancho, alto=None, cam_dir=(1.0, -1.3, 0.9), dist=45.0):
    """Perspectiva sombreada del resorte libre, centrada en (x0, y0) con el
    ancho indicado (unidades de ax)."""
    pts = linea_media(0.0)
    centro = np.array([-1.5, -2.0, L0 / 2])
    cam = centro + dist * np.array(cam_dir) / np.linalg.norm(cam_dir)
    A = tubo(pts, d / 2)
    luz = np.array([0.3, -0.5, 0.8]); luz /= np.linalg.norm(luz)
    base = np.array([0.40, 0.44, 0.50])
    polys, prof, cols = [], [], []
    for i in range(len(A) - 1):
        for j in range(A.shape[1]):
            jn = (j + 1) % A.shape[1]
            quad = np.array([A[i, j], A[i + 1, j], A[i + 1, jn], A[i, jn]])
            n = np.cross(quad[1] - quad[0], quad[3] - quad[0])
            if np.linalg.norm(n) == 0:
                continue
            n /= np.linalg.norm(n)
            c = quad.mean(axis=0)
            vista = (cam - c) / np.linalg.norm(cam - c)
            if n @ vista < 0:                                    # cara trasera
                continue
            pr = proyectar(quad, cam, centro, 1.0)
            polys.append(pr[:, :2]); prof.append(pr[:, 2].mean())
            dif = max(0.0, n @ luz)
            esp = max(0.0, (2 * (n @ luz) * n - luz) @ vista) ** 20
            cols.append(np.clip(base * (0.40 + 0.80 * dif) + 0.6 * esp, 0, 1))
    orden = np.argsort(prof)[::-1]
    polys = [polys[i] for i in orden]; cols = [cols[i] for i in orden]
    todos = np.concatenate(polys)
    xmin, xmax = todos[:, 0].min(), todos[:, 0].max()
    ymin, ymax = todos[:, 1].min(), todos[:, 1].max()
    s = ancho / (xmax - xmin)
    if alto is not None:
        s = min(s, alto / (ymax - ymin))
    cx, cy = (xmax + xmin) / 2, (ymax + ymin) / 2
    polys = [np.column_stack([x0 + (p[:, 0] - cx) * s, y0 + (p[:, 1] - cy) * s]) for p in polys]
    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors=cols, linewidths=0.2,
                                     zorder=5))
    return (xmax - xmin) * s, (ymax - ymin) * s


# ---------------------------------------------------------------------------
# 6. Plano (A4 apaisado, unidades del papel en mm)
# ---------------------------------------------------------------------------
LW_G, LW_F = 0.5, 0.25                                          # mm de trazo
PT = 72 / 25.4                                                  # pt por mm
ESC = 5                                                         # escala 5:1


def plano():
    W, H = 297.0, 210.0
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect('equal'); ax.axis('off')
    k_ = dict(color='black', lw=LW_G * PT)
    kf = dict(color='black', lw=LW_F * PT)
    kc = dict(color='black', lw=LW_F * PT, ls=(0, (10, 2, 1.5, 2)))       # eje
    ko = dict(color='black', lw=LW_F * PT, ls=(0, (3, 1.5)))              # oculta
    kp = dict(color='#444444', lw=LW_F * PT, ls=(0, (7, 1.5, 1.5, 1.5, 1.5, 1.5)))  # fantasma
    fs = 7.5
    bb = dict(fc='white', ec='none', pad=0.4)

    ax.add_patch(Rectangle((10, 10), W - 20, H - 20, fill=False, lw=0.7 * PT))

    def flecha(a, b, estilo='<|-|>'):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle=estilo, mutation_scale=6,
                                     lw=LW_F * PT, color='black', shrinkA=0, shrinkB=0))

    def cota(p1, p2, n, off, texto, rot=None):
        """Cota lineal entre p1 y p2, desplazada off en la dirección n."""
        p1, p2, n = np.array(p1, float), np.array(p2, float), np.array(n, float)
        a, b = p1 + n * off, p2 + n * off
        for p, q in ((p1, a), (p2, b)):
            ax.plot(*zip(p + n * 1.0 * np.sign(off), q + n * 1.5 * np.sign(off)), **kf)
        flecha(a, b)
        t = b - a
        ang = math.degrees(math.atan2(t[1], t[0])) if rot is None else rot
        if ang > 90 or ang < -90:
            ang += 180
        m = (a + b) / 2 + n * np.sign(off) * 1.8
        ax.text(*m, texto, fontsize=fs, ha='center', va='center', rotation=ang, bbox=bb)

    def titulo_vista(x, y, t1, t2=None):
        ax.text(x, y, t1, fontsize=8.5, weight='bold')
        if t2:
            ax.text(x, y - 4.2, t2, fontsize=fs)

    # ---------------- vista A: axial ----------------
    cx, cy = 80, 135
    R_o, R_i, Rm, r_ = OD / 2 * ESC, ID / 2 * ESC, D / 2 * ESC, d / 2 * ESC
    ax.add_patch(Circle((cx, cy), R_o, fill=False, **k_))
    ax.add_patch(Circle((cx, cy), R_i, fill=False, **k_))
    ax.add_patch(Circle((cx, cy), REQ['eje'] / 2 * ESC, fill=False, **kp))
    ax.plot([cx - 17, cx + 17], [cy, cy], **kc); ax.plot([cx, cx], [cy - 17, cy + 17], **kc)

    def brazo(phi_deg, signo, L, estilo):
        ph = math.radians(phi_deg)
        nrm = np.array([math.cos(ph), math.sin(ph)])
        p = np.array([cx, cy]) + Rm * nrm
        t = signo * np.array([-math.sin(ph), math.cos(ph)])
        q = p + t * L * ESC
        for sg in (-1, 1):
            ax.plot(*zip(p + nrm * sg * r_, q + nrm * sg * r_), **estilo)
        ax.plot(*zip(q + nrm * r_, q - nrm * r_), **estilo)
        return p, q, t

    phi2 = (360 * Nb) % 360
    p1, q1, t1 = brazo(0, -1, l1, k_)                            # brazo 1 (fijo)
    p2, q2, t2 = brazo(phi2, +1, l2, k_)                         # brazo 2, libre
    pm, qm, _ = brazo(phi2 + th_mont, +1, l2, kp)                # montaje
    pf, qf, _ = brazo(phi2 + th_fin, +1, l2, kp)                 # fin de recorrido
    ax.text(q1[0] + 1, q1[1] - 1.5, 'brazo 1 (apoyo fijo)', fontsize=fs, ha='left', va='top')
    ax.text(q2[0], q2[1] + 2, 'brazo 2 — libre (0 N·mm)', fontsize=fs, ha='center', va='bottom')
    ax.text(qm[0] - 1.5, qm[1], f'montaje, 60°\n{coma(M_mont, 1)} N·mm', fontsize=fs, ha='right',
            va='center', color='#333333')
    ax.text(qf[0] - 2, qf[1] - 1, f'fin, 120°\n{coma(M_fin, 1)} N·mm', fontsize=fs, ha='right',
            va='top', color='#333333')
    # recorrido de la punta del brazo 2 (arco de trabajo) y sentido de carga
    rr = np.linalg.norm(qm - np.array([cx, cy]))
    a_l = math.degrees(math.atan2(q2[1] - cy, q2[0] - cx))
    a_m, a_f = a_l + th_mont, a_l + th_fin                     # la punta gira con el brazo
    ax.add_patch(Arc((cx, cy), 2 * rr, 2 * rr, theta1=a_l, theta2=a_m, lw=LW_F * PT, color='#444444',
                     ls=(0, (2, 1.5))))
    ax.add_patch(Arc((cx, cy), 2 * rr, 2 * rr, theta1=a_m, theta2=a_f, lw=LW_G * PT, color='black'))
    af = math.radians(a_f)
    pa = np.array([cx, cy]) + rr * np.array([math.cos(af), math.sin(af)])
    ta = np.array([-math.sin(af), math.cos(af)])
    ax.add_patch(FancyArrowPatch(pa - ta * 2.5, pa, arrowstyle='-|>', mutation_scale=8,
                                 lw=LW_G * PT, color='black', shrinkA=0, shrinkB=0))
    a_med = math.radians((a_m + a_f) / 2)
    ax.text(cx + (rr + 3) * math.cos(a_med), cy + (rr + 3) * math.sin(a_med),
            'carrera de\ntrabajo 60°', fontsize=fs, ha='right', va='center')
    # cota del brazo
    cota(p1, q1, np.array([1, 0]), 5, coma(l1, 0))
    cota(p2, q2, np.array([-t2[1], t2[0]]), 5, coma(l2, 0))
    titulo_vista(20, 190, 'VISTA A — axial (escala 5:1)',
                 f'Ángulo entre brazos: libre {a_libre:.0f}°, montaje {a_mont:.0f}°, fin {a_fin:.0f}° (paralelos)')

    # ---------------- vista B: lateral ----------------
    bx, by = 138, 140                                            # extremo del brazo 1, eje
    Lb = L0 * ESC
    ax.plot([bx - 6, bx + Lb + 6], [by, by], **kc)
    # contorno del cuerpo y hélice visible (línea media en la cara frontal)
    ax.plot([bx, bx + Lb, bx + Lb, bx, bx], [by - R_o, by - R_o, by + R_o, by + R_o, by - R_o], **k_)
    n_sec = int(round(Nb + 1))
    for i in range(n_sec):
        x_ = bx + i * d * ESC
        ax.plot([x_, x_ + d * ESC], [by - R_o, by + R_o], **kf)
    for sg in (-1, 1):
        ax.plot([bx, bx + Lb], [by + sg * R_i] * 2, **ko)
    # brazo 1: cae desde la primera espira (y del mundo = vertical del papel)
    xa = bx
    ax.add_patch(Rectangle((xa, by - l1 * ESC), d * ESC, l1 * ESC, fill=False, **k_))
    # brazo 2: en la última espira, sube (proyección de su componente y)
    ph2 = math.radians(phi2)
    y_raiz = by + Rm * math.sin(ph2)
    alto2 = l2 * math.cos(ph2) * ESC
    ax.add_patch(Rectangle((bx + Lb - d * ESC, y_raiz - r_), d * ESC, alto2 + r_, fill=False, **k_))
    cota((bx, by - R_o), (bx + Lb, by - R_o), (0, -1), 8, f'L0 = {coma(L0)}')
    cota((bx + Lb, by + R_o), (bx + Lb, by - R_o), (1, 0), 9, f'Ø{coma(OD)}')
    cota((bx + Lb, by + R_i), (bx + Lb, by - R_i), (1, 0), 17, f'Ø{coma(ID)}')
    ax.annotate(f'd = Ø{coma(d)}', xy=(bx + d * ESC, by - l1 * ESC + 6), xytext=(bx + 12, by - l1 * ESC + 3),
                fontsize=fs, va='center', arrowprops=dict(arrowstyle='-|>', lw=LW_F * PT, color='black',
                                                            mutation_scale=6, shrinkA=1, shrinkB=0))
    ax.text(bx + Lb + 3, y_raiz + alto2 - 1, 'brazo 2', fontsize=fs, va='top')
    ax.text(bx + 3, by - l1 * ESC + 12, 'brazo 1', fontsize=fs)
    titulo_vista(128, 190, 'VISTA B — lateral (escala 5:1)',
                 f'{coma(Nb)} espiras juntas (9 + 60°), hélice a derechas')

    # ---------------- perspectiva ----------------
    dibujar_3d(ax, 248, 132, 60, 72)
    titulo_vista(212, 190, 'PERSPECTIVA (sin escala)', 'resorte libre')

    # ---------------- tabla de datos ----------------
    filas = [
        ('Material', 'Cuerda de piano ASTM A228'),
        ('Diámetro de alambre d', f'{coma(d)} mm'),
        ('Diámetro interior libre Di', f'{coma(ID)} mm (mín. cargado {coma(D_fin - d)} mm)'),
        ('Diámetro exterior De', f'{coma(OD)} mm'),
        ('Espiras de cuerpo Nb', f'{coma(Nb)} (9 + 60°), hélice a derechas'),
        ('Largo del cuerpo L0', f'{coma(L0)} mm libre; {coma(L_fin)} mm a 120°'),
        ('Brazos', f'2 rectos tangenciales de {coma(l1, 0)} mm'),
        ('Rigidez', f'{coma(k, 4)} N·mm/° ({coma(k_vuelta, 1)} N·mm/vuelta)'),
        ('M1 (montaje, 60°)', f'{coma(M_mont)} N·mm ± 10 %'),
        ('M2 (fin de recorrido, 120°)', f'{coma(M_fin)} N·mm ± 10 %'),
        ('Tensión máx. / FS estático', f'{s_max:.0f} MPa / {coma(n_est)}'),
        ('Alambre / masa', f'{coma(largo_alambre, 0)} mm / {coma(masa, 2)} g'),
        ('Tratamiento', 'Alivio de tensiones tras enrollar'),
    ]
    tx, ty, tw, hf, c1 = 15, 73.8, 145, 4.6, 50
    ax.add_patch(Rectangle((tx, ty - hf * len(filas)), tw, hf * (len(filas) + 1), fill=False, lw=LW_G * PT))
    ax.text(tx + 2, ty + 1.3, 'DATOS DEL RESORTE', fontsize=fs + 0.5, weight='bold')
    for i, (a, b) in enumerate(filas):
        y_ = ty - hf * (i + 1)
        ax.plot([tx, tx + tw], [y_ + hf, y_ + hf], **kf)
        ax.text(tx + 2, y_ + 1.3, a, fontsize=fs)
        ax.text(tx + c1 + 2, y_ + 1.3, b, fontsize=fs)
    ax.plot([tx + c1, tx + c1], [ty - hf * len(filas), ty], **kf)

    # ---------------- notas ----------------
    notas = ['NOTAS',
             '1. Cotas en mm. Tolerancias no indicadas: ± 0,1 mm; ángulos ± 5°.',
             '2. Montar con 60° de precarga: brazos a 60° entre sí.',
             '3. Cargar solo en el sentido que cierra las espiras.',
             '4. Extremos de los brazos cortados rectos, sin rebaba.',
             '5. Verificar M1 y M2 en el primer lote; si salen de',
             '    tolerancia, ajustar Nb de a ¼ de vuelta.',
             '6. Circunferencia de trazo fantasma en la vista A: eje Ø3.',
             '7. Cálculo: nota 02489-00-MC003.']
    for i, t in enumerate(notas):
        ax.text(172, 82 - 4.4 * i, t, fontsize=fs, weight='bold' if i == 0 else 'normal')

    # ---------------- cajetín ----------------
    cx0, cy0, cw, ch = 172, 10, 115, 32
    ax.add_patch(Rectangle((cx0, cy0), cw, ch, fill=False, lw=0.7 * PT))
    for yy in (cy0 + 8, cy0 + 16, cy0 + 24):
        ax.plot([cx0, cx0 + cw], [yy, yy], **kf)
    ax.plot([cx0 + 62, cx0 + 62], [cy0, cy0 + 24], **kf)
    ax.text(cx0 + 2, cy0 + 26.8, 'Resorte de torsión Ø0,50 para eje Ø3', fontsize=10, weight='bold')
    for (x_, y_, t) in ((2, 18.8, 'Proyecto 00503 · Mecanalisis'), (64, 18.8, 'Nota 02489-00-MC003'),
                        (2, 10.8, 'Dibujó: Matías Gaviño'), (64, 10.8, 'Fecha: 24/09/2026'),
                        (2, 2.8, 'Escala: 5:1 (vistas A y B)'), (64, 2.8, 'Hoja 1 de 1 · A4')):
        ax.text(cx0 + x_, cy0 + y_, t, fontsize=fs)
    fig.savefig(os.path.join(FIG, 'plano.pdf'))
    fig.savefig(os.path.join(FIG, 'plano.png'), dpi=150, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    fig_momento()
    fig_fatiga()
    plano()
    for clave in ('C', 'Ki', 'Nb_req', 'Ne', 'k', 'M_mont', 'M_fin', 'F_mont', 'F_fin',
                  'ID_fin', 'holgura_fin', 'L0', 'L_fin', 's_min', 's_max', 'Sut', 'Sy',
                  'n_est', 'M_y', 'th_y', 'n_f_1e6', 'n_f_1e7', 'Sr_req_frac',
                  'N_adm_extrapolado', 'anios_hasta_1e6', 'largo_alambre', 'masa_g'):
        print(f'{clave:20s} {res[clave]:.4g}')
    print('ángulos entre brazos', res['ang_brazos'])
    for a, v in caso_uso.items():
        print(f'{a:3d} años  N = {v["N"]:>8,.0f}  n_f = {v["n_f"]:.3f}')
