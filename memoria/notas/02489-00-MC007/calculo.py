#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota 02489-00-MC007 - Selección del LED OSLON SSL 80 (GW CS8PM1.PM).

Uso (desde esta carpeta):
    python3 calculo.py      # escribe resultados.json, figuras/fig_*.pdf/png
                            # y figuras/ds_*.png (capturas del datasheet)

Datos: datasheet oficial ams OSRAM GW CS8PM1.PM, versión 1.10, 2026-03-05,
en fuentes/GW-CS8PM1-PM_v1.10.pdf. Geometría del módulo dada por el usuario:
LED a 7 mm de una ventana de Ø 5 mm, conducto de aluminio fresado no pulido.

1. Curvas del datasheet, sin lectura a ojo: se toman los trazos vectoriales
   del PDF (IF-VF y flujo relativo vs IF en p. 13, flujo relativo vs Tj en
   p. 14) y se calibran con las líneas de la grilla de cada gráfico.
2. Captura directa de la ventana, modelo I(theta) = I0 cos^m(theta):
       m = ln(0,5) / ln(cos 40°)           (2phi = 80° a 50 % de intensidad)
       alfa = atan(r / d),  F = 1 - cos^(m+1)(alfa)
3. Eficiencia del conducto: Monte Carlo con fuente puntual en el centro del
   fondo de un cilindro de Ø 5 x 7 mm, fondo absorbente (SUPUESTO), salida por
   toda la boca, pared difusa (lambertiana) o especular ideal con
   reflectividad Rw por rebote. El difusor es un factor de transmisión
   constante (0,75-0,90, SUPUESTO) sin retrorreflexión.
4. Térmica: Tj - Ts = RthJS,el * P_el  (RthJS,el = 3,7 K/W del datasheet).
"""
import json
import math
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pymupdf  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(AQUI, 'fuentes', 'GW-CS8PM1-PM_v1.10.pdf')
FIG = os.path.join(AQUI, 'figuras')

# --- datos del datasheet (v1.10) -------------------------------------------
IF_NOM = 0.350                      # A
VF = {'min': 2.70, 'tip': 2.85, 'max': 3.20}   # V a 350 mA, Tj 85 °C
RTH_JS = 3.7                        # K/W, eléctrica
FLUJO_BIN = {'min': 164.0, 'medio': 187.0, 'max': 210.0}   # lm, LUMQ a 350 mA
SEMI = 40.0                         # grados, 2phi = 80°

# --- geometría ---------------------------------------------------------------
R, L = 2.5, 7.0                     # mm, radio de ventana/conducto y distancia
RW = [0.55, 0.65, 0.75, 0.85, 0.92]
TRANS = [0.75, 0.90]

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e4e6ea',
                     'axes.edgecolor': '#8a8880', 'savefig.dpi': 200})
AZUL, NARANJA, VERDE, TINTA, GRIS = '#2a78d6', '#eb6834', '#1baf7a', '#1e2328', '#6b7280'


def coma(x, nd=1):
    return ('%.*f' % (nd, x)).replace('.', ',')


# =========================================================================
# 1. Curvas vectoriales del datasheet
# =========================================================================
def _bez(p0, p1, p2, p3, n=16):
    t = np.linspace(0, 1, n + 1)[:, None]
    P = np.array([[p.x, p.y] for p in (p0, p1, p2, p3)])
    return ((1 - t) ** 3 * P[0] + 3 * t * (1 - t) ** 2 * P[1]
            + 3 * t * t * (1 - t) * P[2] + t ** 3 * P[3])


def trazo(page, clip, ancho):
    """Puntos (x, y) de los trazos negros de grosor 'ancho' dentro de clip."""
    pts = []
    for dr in page.get_drawings():
        r = dr['rect']
        if not (dr.get('width') and abs(dr['width'] - ancho) < 0.02):
            continue
        if not (r.x0 >= clip[0] and r.x1 <= clip[2] and r.y0 >= clip[1] and r.y1 <= clip[3]):
            continue
        for it in dr['items']:
            if it[0] == 'l':
                pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == 'c':
                pts += [tuple(p) for p in _bez(*it[1:5])]
    pts = np.array(sorted(set(pts)))
    return pts


def curvas():
    doc = pymupdf.open(DS)
    # p. 13, derecha: flujo relativo vs IF. Grilla vertical 381,07 (100 mA) a
    # 513,56 (1300 mA); horizontal 142,62 (2,75) cada 21,64 pt = 0,25.
    p = trazo(doc[12], (370, 130, 530, 360), 1.698)
    i_ma = 100 + (p[:, 0] - 381.07) / (513.56 - 381.07) * 1200
    rel_i = 2.75 - (p[:, 1] - 142.62) / 21.64 * 0.25
    # p. 13, izquierda: IF vs VF. VF 2,70 V en x = 130,45 y 3,30 V en 252,38;
    # IF 100 mA en y = 360,21 y 1300 mA en 145,92.
    q = trazo(doc[12], (100, 130, 300, 380), 1.698)
    vf = 2.70 + (q[:, 0] - 130.45) / (252.38 - 130.45) * 0.60
    i_vf = 100 + (360.21 - q[:, 1]) / (360.21 - 145.92) * 1200
    # p. 14, derecha: flujo relativo vs Tj. Tj -40 °C en x = 381,07 y 120 °C
    # en 516,33; 1,2 en y = 145,92 y 0,1 en 342,40.
    t = trazo(doc[13], (370, 130, 530, 360), 1.729)
    tj = -40 + (t[:, 0] - 381.07) / (516.33 - 381.07) * 160
    rel_t = 1.2 - (t[:, 1] - 145.92) / (342.40 - 145.92) * 1.1

    def interp(x, xs, ys):
        o = np.argsort(xs)
        return float(np.interp(x, xs[o], ys[o]))

    c = {
        'flujo_rel_350mA_control': interp(350, i_ma, rel_i),
        'flujo_rel_500mA': interp(500, i_ma, rel_i),
        'flujo_rel_700mA': interp(700, i_ma, rel_i),
        'vf_tip_350mA_control': interp(350, i_vf, vf),
        'vf_tip_500mA': interp(500, i_vf, vf),
        'flujo_rel_25C': interp(25, tj, rel_t),
        'flujo_rel_85C_control': interp(85, tj, rel_t),
        'flujo_rel_120C': interp(120, tj, rel_t),
    }
    return c, (i_ma, rel_i, i_vf, vf, tj, rel_t)


# =========================================================================
# 2-3. Óptica
# =========================================================================
M = math.log(0.5) / math.log(math.cos(math.radians(SEMI)))


def m_de(semi):
    return math.log(0.5) / math.log(math.cos(math.radians(semi)))


def captura(alfa_deg, m=M):
    return 1 - math.cos(math.radians(alfa_deg)) ** (m + 1)


def _lambert(n, rng):
    u = rng.random(n)
    return np.sqrt(u), np.sqrt(1 - u), 2 * np.pi * rng.random(n)


def eficiencia(rw, modo, fondo=0.0, n=400000, seed=1, max_rebotes=80):
    """Fracción del flujo del LED que sale por la ventana (antes del difusor)."""
    rng = np.random.default_rng(seed)
    u = rng.random(n)
    ct = (1 - u) ** (1 / (M + 1))
    st = np.sqrt(1 - ct ** 2)
    ph = 2 * np.pi * rng.random(n)
    d = np.stack([st * np.cos(ph), st * np.sin(ph), ct], 1)
    p = np.zeros((n, 3))
    w = np.ones(n)
    salida = 0.0
    for _ in range(max_rebotes):
        if not len(w):
            break
        a = d[:, 0] ** 2 + d[:, 1] ** 2
        b = 2 * (p[:, 0] * d[:, 0] + p[:, 1] * d[:, 1])
        c = p[:, 0] ** 2 + p[:, 1] ** 2 - R ** 2
        with np.errstate(divide='ignore', invalid='ignore'):
            tc = np.where(a > 1e-12,
                          (-b + np.sqrt(np.maximum(b * b - 4 * a * c, 0))) / (2 * a), np.inf)
            tz = np.where(d[:, 2] > 0, (L - p[:, 2]) / d[:, 2],
                          np.where(d[:, 2] < 0, -p[:, 2] / d[:, 2], np.inf))
        tc = np.where(tc > 1e-9, tc, np.inf)
        tapa = tz < tc
        arriba, abajo, pared = tapa & (d[:, 2] > 0), tapa & (d[:, 2] < 0), ~tapa
        salida += w[arriba].sum()
        np_, nd, nw = [], [], []
        if fondo > 0 and abajo.any():
            k = abajo.sum()
            ct, st, ph = _lambert(k, rng)
            np_.append(p[abajo] + d[abajo] * tz[abajo, None])
            nd.append(np.stack([st * np.cos(ph), st * np.sin(ph), ct], 1))
            nw.append(w[abajo] * fondo)
        if pared.any():
            k = pared.sum()
            pw = p[pared] + d[pared] * tc[pared, None]
            nrm = np.stack([-pw[:, 0] / R, -pw[:, 1] / R, np.zeros(k)], 1)
            if modo == 'especular':
                dw = d[pared]
                dn = dw - 2 * (dw * nrm).sum(1)[:, None] * nrm
            else:
                ct, st, ph = _lambert(k, rng)
                t1 = np.tile([0.0, 0.0, 1.0], (k, 1))
                t2 = np.cross(nrm, t1)
                dn = ct[:, None] * nrm + st[:, None] * (np.cos(ph)[:, None] * t1
                                                        + np.sin(ph)[:, None] * t2)
            np_.append(pw + nrm * 1e-7)
            nd.append(dn)
            nw.append(w[pared] * rw)
        if not np_:
            break
        p, d, w = np.concatenate(np_), np.concatenate(nd), np.concatenate(nw)
        viva = w > 1e-4
        p, d, w = p[viva], d[viva], w[viva]
    return salida / n


def rw_para(objetivo, modo, trans, flujo):
    """Reflectividad mínima de pared para 'objetivo' lm (bisección)."""
    lo, hi = 0.3, 0.99
    if eficiencia(hi, modo, n=100000) * trans * flujo < objetivo:
        return None
    for _ in range(14):
        mid = (lo + hi) / 2
        if eficiencia(mid, modo, n=100000) * trans * flujo >= objetivo:
            hi = mid
        else:
            lo = mid
    return round(hi, 3)


# =========================================================================
# Figuras propias
# =========================================================================
def guardar(fig, nombre):
    fig.savefig(os.path.join(FIG, nombre + '.pdf'), bbox_inches='tight')
    fig.savefig(os.path.join(FIG, nombre + '.png'), bbox_inches='tight')
    plt.close(fig)


def fig_geometria(alfa):
    from matplotlib.patches import Rectangle, Wedge, Polygon
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    ax.set_aspect('equal')
    ax.axis('off')
    y_emit = 0.6
    y_win = y_emit + L
    alu = dict(facecolor='#c9cdd3', edgecolor='#8d949e', hatch='///', lw=0.8)
    ax.add_patch(Rectangle((-R - 1.4, 0), 1.4, y_win + 0.3, **alu))
    ax.add_patch(Rectangle((R, 0), 1.4, y_win + 0.3, **alu))
    ax.add_patch(Rectangle((-R - 1.8, -0.5), 2 * R + 3.6, 0.5, color='#3d6b50'))
    ax.add_patch(Rectangle((-1.5, 0), 3.0, 1.0, facecolor='#e9e4d6', edgecolor='#8d949e'))
    ax.add_patch(Wedge((0, 1.0), 1.2, 0, 180, facecolor='#fff4cf', edgecolor='#d9a400'))
    ax.add_patch(Rectangle((-R, y_win), 2 * R, 0.3, facecolor='#dbe7f3', edgecolor=TINTA, lw=0.8))
    ax.add_patch(Polygon([(0, y_emit), (-R, y_win), (R, y_win)], closed=True,
                         facecolor=VERDE, alpha=0.18, edgecolor=VERDE, lw=1.2))
    yh = y_emit + R / math.tan(math.radians(SEMI))
    for s in (-1, 1):
        ax.plot([0, s * R], [y_emit, yh], ls='--', color=GRIS, lw=0.9)
    ax.plot([0, 0], [y_emit, y_win], color='#b0b5bb', lw=0.6)
    ax.annotate('', xy=(-R - 2.3, y_emit), xytext=(-R - 2.3, y_win),
                arrowprops=dict(arrowstyle='<->', color=TINTA, lw=0.8))
    ax.text(-R - 2.5, (y_emit + y_win) / 2, '7 mm', ha='right', va='center', fontweight='bold')
    ax.annotate('', xy=(-R, y_win + 0.9), xytext=(R, y_win + 0.9),
                arrowprops=dict(arrowstyle='<->', color=TINTA, lw=0.8))
    ax.text(0, y_win + 1.1, 'Ø 5 mm (ventana y difusor)', ha='center', va='bottom',
            fontweight='bold')
    ax.text(0.35, y_emit + 3.1, 'α = %s°' % coma(alfa, 2), fontweight='bold')
    notas = [(y_win + 0.15, 'Difusor: transmisión 75–90 % (supuesto)'),
             (y_emit + 5.0, 'Aluminio fresado, no pulido:\nreflectividad incierta'),
             (yh, 'Media intensidad (±40°):\ntoca la pared a %s mm' % coma(yh - y_emit, 1)),
             (0.6, 'OSLON SSL 80\n3,0 × 3,0 mm, lente de silicona')]
    for y, t in notas:
        ax.plot([R + 1.5, R + 2.3], [y, y], color=GRIS, lw=0.6)
        ax.text(R + 2.45, y, t, va='center', fontsize=8.5)
    ax.set_xlim(-R - 4.2, R + 11)
    ax.set_ylim(-0.7, y_win + 1.9)
    guardar(fig, 'fig_geometria')


def fig_captura(alfa):
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    th = np.linspace(0, 90, 181)
    for semi, color, lab in ((40, AZUL, 'OSLON SSL 80 (2φ = 80°)'),
                             (60, NARANJA, 'LED lambertiano (2φ = 120°)'),
                             (75, VERDE, 'LED de 2φ = 150°')):
        m = m_de(semi)
        ax.plot(th, [100 * captura(x, m) for x in th], color=color, lw=1.8,
                label='%s: %s %% en α' % (lab, coma(100 * captura(alfa, m))))
        ax.plot(alfa, 100 * captura(alfa, m), 'o', color=color, ms=5, mec='white')
    ax.axvspan(0, alfa, color='#eef5f1')
    ax.axvline(alfa, ls='--', color=GRIS, lw=0.9)
    f40 = 100 * captura(40)
    ax.plot(40, f40, 'o', color=AZUL, ms=5, mec='white')
    ax.annotate('%s %% dentro de ±40°' % coma(f40, 0), (40, f40), xytext=(21, 74),
                fontsize=8.5)
    ax.text(alfa + 1, 93, 'borde de la ventana', fontsize=8.5, color=GRIS)
    ax.set_xlim(0, 90)
    ax.set_ylim(0, 100)
    ax.set_xticks(range(0, 91, 10))
    ax.set_xlabel('Semiángulo desde el eje del LED [°]')
    ax.set_ylabel('Flujo acumulado [%]')
    ax.legend(loc='lower right', fontsize=8, frameon=False)
    guardar(fig, 'fig_captura')


def fig_sensibilidad(fd):
    rs = np.round(np.arange(0.50, 0.951, 0.05), 2)
    fig, ax = plt.subplots(figsize=(6.2, 3.5))
    flujo = FLUJO_BIN['medio']
    for modo, color, lab in (('especular', AZUL, 'Pared especular (optimista)'),
                             ('difusa', NARANJA, 'Pared difusa (conservador)')):
        eta = np.array([eficiencia(r, modo, n=120000) for r in rs])
        ax.fill_between(rs, eta * flujo * 0.75, eta * flujo * 0.90, color=color, alpha=0.22,
                        lw=0, label=lab)
        ax.plot(rs, eta * flujo * 0.90, color=color, lw=1.6)
        ax.plot(rs, eta * flujo * 0.75, color=color, lw=1.6)
    ax.axhline(100, color=TINTA, ls='--', lw=1.1)
    ax.text(0.505, 103, 'Objetivo: 100 lm', fontweight='bold', fontsize=8.5)
    ax.axhline(fd, color=GRIS, ls=':', lw=1.0)
    ax.text(0.945, fd + 3, 'solo luz directa, sin difusor: %s lm' % coma(fd, 0), ha='right',
            fontsize=8, color=GRIS)
    ax.set_xlim(0.50, 0.95)
    ax.set_ylim(0, 180)
    ax.set_xticks(rs)
    ax.set_xticklabels([coma(r, 2) for r in rs])
    ax.set_xlabel('Reflectividad de la pared del conducto')
    ax.set_ylabel('Flujo a la salida [lm]')
    ax.legend(loc='upper left', bbox_to_anchor=(0, 0.93), fontsize=8, frameon=False)
    guardar(fig, 'fig_sensibilidad')


# =========================================================================
# Capturas del datasheet (con filas resaltadas)
# =========================================================================
CAPTURAS = [
    ('ds_portada', 2, (40, 88, 560, 640), []),
    ('ds_pedido', 3, (40, 92, 560, 512), ['LUMQ-A333-1', 'LUMQ-XX53-1']),
    ('ds_maximos', 4, (40, 92, 560, 402), []),
    ('ds_caracteristicas', 5, (40, 92, 560, 290), []),
    ('ds_grupos', 6, (40, 92, 560, 500), ['LU', 'MP', 'MQ']),
    ('ds_radiacion', 12, (36, 418, 560, 730), []),
    ('ds_corriente', 13, (36, 92, 560, 395), []),
    ('ds_temperatura', 14, (36, 92, 560, 395), []),
    ('ds_derating', 15, (36, 92, 300, 395), []),
    ('ds_dimensiones', 16, (36, 92, 560, 420), []),
    ('ds_footprint', 17, (36, 92, 560, 395), []),
    ('ds_reflow', 18, (36, 92, 560, 730), []),
]


def capturas():
    src = pymupdf.open(DS)
    for nombre, pno, clip, textos in CAPTURAS:
        page = src[pno - 1]
        c = pymupdf.Rect(*clip)
        filas = []
        for t in textos:
            for r in page.search_for(t, clip=c):
                if len(t) <= 2 and r.x0 > c.x0 + 60:
                    continue
                filas.append(pymupdf.Rect(2, r.y0 - 2.5 - c.y0, c.width - 2, r.y1 + 2.5 - c.y0))
        doc = pymupdf.open()
        np_ = doc.new_page(width=c.width, height=c.height)
        np_.show_pdf_page(np_.rect, src, pno - 1, clip=c)
        for fr in filas:
            np_.draw_rect(fr, color=(0.65, 0.41, 0.05), fill=(0.98, 0.70, 0.10),
                          fill_opacity=0.22, width=0.8)
        np_.get_pixmap(dpi=220).save(os.path.join(FIG, nombre + '.png'))


# =========================================================================
def main():
    os.makedirs(FIG, exist_ok=True)
    c, _ = curvas()
    alfa = math.degrees(math.atan(R / L))
    fdir = captura(alfa)
    tabla = {}
    for modo in ('difusa', 'especular'):
        tabla[modo] = []
        for rw in RW:
            eta = eficiencia(rw, modo)
            f = eta * FLUJO_BIN['medio']
            tabla[modo].append({'Rw': rw, 'eta': round(eta, 3), 'antes_difusor_lm': round(f, 1),
                                'difusor_75_lm': round(f * 0.75, 1),
                                'difusor_90_lm': round(f * 0.90, 1)})
    fondo = {modo: {rw: round(eficiencia(rw, modo, fondo=0.5), 3) for rw in (0.55, 0.92)}
             for modo in ('difusa', 'especular')}
    eta_total_100 = 100 / FLUJO_BIN['medio']
    p_el = IF_NOM * VF['tip']
    p500 = 0.5 * c['vf_tip_500mA']
    res = {
        'm': round(M, 3),
        'alfa_grados': round(alfa, 2),
        'captura_directa': round(fdir, 4),
        'captura_120': round(captura(alfa, m_de(60)), 4),
        'captura_150': round(captura(alfa, m_de(75)), 4),
        'fraccion_dentro_40': round(captura(40), 3),
        'directa_lm': {k: round(v * fdir, 1) for k, v in FLUJO_BIN.items()},
        'tabla_conducto': tabla,
        'eficiencia_con_fondo_0_5': fondo,
        'para_100lm': {
            'eta_total_min': round(eta_total_100, 3),
            'eta_conducto_min_T90': round(eta_total_100 / 0.90, 3),
            'eta_conducto_min_T75': round(eta_total_100 / 0.75, 3),
            'Rw_especular_T90': rw_para(100, 'especular', 0.90, FLUJO_BIN['medio']),
            'Rw_especular_T75': rw_para(100, 'especular', 0.75, FLUJO_BIN['medio']),
            'Rw_difusa_T90': rw_para(100, 'difusa', 0.90, FLUJO_BIN['medio']),
            'bin_min_especular_075_T85_lm': round(
                eficiencia(0.75, 'especular') * 0.85 * FLUJO_BIN['min'], 1),
        },
        'curvas_datasheet': {k: round(v, 3) for k, v in c.items()},
        'electrico': {
            'P_350mA_W': round(p_el, 3),
            'P_500mA_W': round(p500, 3),
            'dT_JS_350mA_K': round(RTH_JS * p_el, 2),
            'dT_JS_500mA_K': round(RTH_JS * p500, 2),
            'P_regulador_lineal_5V_W': round((5 - VF['tip']) * IF_NOM, 2),
            'difusa_085_T90_a_500mA_lm': round(
                eficiencia(0.85, 'difusa') * 0.90 * FLUJO_BIN['medio'] * c['flujo_rel_500mA'], 1),
        },
        'flujo_medio_a_85C_si_bin_referido_a_25C_lm': round(FLUJO_BIN['medio'] / c['flujo_rel_25C'], 1),
    }
    with open(os.path.join(AQUI, 'resultados.json'), 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    fig_geometria(alfa)
    fig_captura(alfa)
    fig_sensibilidad(fdir * FLUJO_BIN['medio'])
    capturas()
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
