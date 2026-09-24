#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota 02489-00-MC005 - Selección del solenoide del impactador (WTT).

Uso (desde esta carpeta):
    python3 calculo.py     # escribe curvas.json, resultados.json, figuras/fig_*.pdf/png
                           # y figuras/ds_*.png (capturas de las hojas de datos)

Datos: hojas de datos oficiales en fuentes/ (Geeplus catálogo 2024, Takaha,
Ledex/Johnson Electric 2020 y hoja RS, Kendrion, Magnet-Schultz, Transmotec).

1. Extracción de las curvas fuerza-carrera, sin lectura a ojo:
   - Geeplus 110C/141C/144C y Takaha CA0422/CA0425: trazos vectoriales del PDF
     (rectas y Bézier), calibrados con la posición de las etiquetas de los ejes
     (eje logarítmico de Geeplus ajustado por mínimos cuadrados).
   - Ledex B12, Geeplus RD-A420 y Transmotec K0420S: el gráfico es una imagen;
     se buscan los píxeles del color de cada curva y se calibra con la grilla.
   - Magnet-Schultz 312: tabla de la hoja. Kendrion BI 13: solo fuerza inicial
     y final (recta entre ambas, SUPUESTO).
2. Energía útil sin tocar el tope interno (x = distancia al tope, x = 0 asentado):
       W_util = integral de F(x) dx entre x_imp = 0,5 mm y x_ini
       S_0.1  = F(x_imp) * 0,1 mm / W_util      (sensibilidad a la posición)
       v      = sqrt(2 eta W_util / m),  m = émbolo + 1 g de punta (SUPUESTO)
   Las curvas son estáticas: W_util es una cota superior (eta = 1).
"""
import json
import math
import os
import sys

import pymupdf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def bezier(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * p0.x + b * p1.x + c * p2.x + d * p3.x,
                    a * p0.y + b * p1.y + c * p2.y + d * p3.y))
    return out


def trazo(d):
    pts = []
    for it in d['items']:
        if it[0] == 'l':
            seg = [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == 'c':
            seg = bezier(*it[1:5])
        else:
            continue
        if pts and abs(pts[-1][0] - seg[0][0]) < 1e-3 and abs(pts[-1][1] - seg[0][1]) < 1e-3:
            seg = seg[1:]
        pts.extend(seg)
    return pts


def spans(page):
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                yield s['text'].strip(), pymupdf.Rect(s['bbox'])


def num(t):
    try:
        return float(t.replace(',', '.'))
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Geeplus push-pull (eje de fuerza logaritmico)
# --------------------------------------------------------------------------
GEEPLUS_COLORES = {
    (0.31, 0.51, 0.74): '10% ED',
    (0.75, 0.31, 0.3): '25% ED',
    (0.89, 0.42, 0.04): '50% ED',
    (0.5, 0.39, 0.63): '100% ED',
}


def geeplus(page):
    dr = [d for d in page.get_drawings() if d.get('color')]
    curvas = [d for d in dr
              if tuple(round(c, 2) for c in d['color']) in GEEPLUS_COLORES
              and len(d['items']) > 3 and d['rect'].x1 < 300]
    x0 = min(d['rect'].x0 for d in curvas)
    y_top = min(d['rect'].y0 for d in curvas)
    # etiquetas del eje x inferior (mm) y del eje y izquierdo (N)
    tx, ty = [], []
    for t, r in spans(page):
        v = num(t)
        if v is None:
            continue
        if r.x1 < x0 - 3 and r.x0 > x0 - 30 and r.y0 > y_top - 20:
            ty.append((v, (r.y0 + r.y1) / 2))
        elif r.y0 > max(d['rect'].y1 for d in curvas) - 30 and x0 - 10 < r.x0 < 300 \
                and r.y0 < max(d['rect'].y1 for d in curvas) + 20:
            tx.append((v, (r.x0 + r.x1) / 2))
    tx.sort()
    # x lineal
    (va, pa), (vb, pb) = tx[0], tx[-1]
    fx = lambda px: va + (px - pa) * (vb - va) / (pb - pa)
    # y logaritmico: ajuste por minimos cuadrados log10(F) = a + b*py
    xs = [p for v, p in ty if v > 0]
    ys = [math.log10(v) for v, p in ty if v > 0]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    fy = lambda py: 10 ** (a + b * py)
    out = {}
    for d in curvas:
        k = GEEPLUS_COLORES[tuple(round(c, 2) for c in d['color'])]
        out[k] = [(round(fx(x), 4), round(fy(y), 4)) for x, y in trazo(d)]
    return out


# --------------------------------------------------------------------------
# Takaha (ejes lineales; curvas en negro)
# --------------------------------------------------------------------------
def takaha(page):
    # marco del grafico: rectangulo mas grande en la mitad inferior derecha
    dr = page.get_drawings()
    tx, ty = {}, {}
    for t, r in spans(page):
        v = num(t)
        if v is None or r.y0 < 480:
            continue
        if r.x0 > 300 and r.y0 > 750 and v in (0, 1, 2, 3):
            tx.setdefault(v, (r.x0 + r.x1) / 2)
        if 300 < r.x0 < 340 and v in (1.0, 2.0, 3.0, 4.0):
            ty.setdefault(v, (r.y0 + r.y1) / 2)
    # ejes: se ajustan con las etiquetas
    (va, pa), (vb, pb) = min(tx.items()), max(tx.items())
    fx = lambda px: va + (px - pa) * (vb - va) / (pb - pa)
    (wa, qa), (wb, qb) = min(ty.items()), max(ty.items())
    fy = lambda py: wa + (py - qa) * (wb - wa) / (qb - qa)
    curvas = []
    for d in dr:
        c = d.get('color')
        if not c or round(c[0], 2) != 0.14 or len(d['items']) < 15:
            continue
        r = d['rect']
        if r.x0 < pa - 5 or r.y1 > page.rect.y1 - 60:
            continue
        pts = [(round(fx(x), 4), round(fy(y), 4)) for x, y in trazo(d)]
        if max(p[0] for p in pts) - min(p[0] for p in pts) < 1.5:
            continue
        curvas.append(pts)
    # ordenar de mayor a menor fuerza media
    curvas.sort(key=lambda p: -sum(q[1] for q in p) / len(p))
    nombres = ['24 W (6% ED)', '15 W (10% ED)', '6 W (25% ED)', '3 W (50% ED)',
               '1.5 W (100% ED)']
    return dict(zip(nombres, curvas)), (tx, ty)


# --------------------------------------------------------------------------
# Curvas en mapa de bits (Ledex B12 y Geeplus RD-A420): se renderiza el
# grafico, se buscan los pixeles del color de cada curva y se calibra con la
# posicion de las etiquetas o de la grilla.
# --------------------------------------------------------------------------
def raster(page, clip, zoom, colores, fx, fy, tol=40, excluir=None):
    import numpy as np
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3].astype(int)
    out = {}
    for nombre, rgb in colores.items():
        m = (abs(a - np.array(rgb)).max(2) < tol)
        if excluir:  # recuadro de la leyenda, en pt
            r = excluir
            m[int((r.y0 - clip.y0) * zoom):int((r.y1 - clip.y0) * zoom),
              int((r.x0 - clip.x0) * zoom):int((r.x1 - clip.x0) * zoom)] = False
        pts = []
        for x in range(0, pix.w, 2):
            ys = np.where(m[:, x])[0]
            if len(ys) >= 2:
                pts.append((round(fx(x), 4), round(fy(float(np.median(ys))), 4)))
        out[nombre] = pts
    return out


def ledex_b12(pdf):
    # Catalogo Ledex Open Frame (2020), pagina "Box Frame Size B12" (p. 10).
    # Calibracion con los centros de las etiquetas: x "0" = 343.25 pt,
    # x "0.200 in" = 553.45 pt; y "0" = 452.15 pt, y "14.0 oz" = 168.4 pt.
    page = pymupdf.open(pdf)[1]
    z, clip = 4, pymupdf.Rect(340, 160, 570, 460)
    fx = lambda px: (clip.x0 + px / z - 343.25) * 5.08 / (553.45 - 343.25)
    fy = lambda py: (452.15 - (clip.y0 + py / z)) * 14.0 / (452.15 - 168.4) * 0.2780139
    return raster(page, clip, z, {'13 W (10% ED)': (0, 108, 68),
                                  '5.2 W (25% ED)': (0, 116, 188)}, fx, fy,
                  excluir=pymupdf.Rect(444, 215, 540, 275))


def geeplus_rda420(pdf):
    # Hoja RD-A420 (grafico en mapa de bits). Grilla detectada a zoom 4 sobre
    # el recorte: x = 0 mm en 23.5 px y 85.86 px/mm; y = 0 N en 411.5 px y
    # 122.8 px/N.
    page = pymupdf.open(pdf)[0]
    z, clip = 4, pymupdf.Rect(95, 460, 260, 570)
    fx = lambda px: (px - 23.5) / 85.86
    fy = lambda py: (411.5 - py) / 122.83
    return raster(page, clip, z, {'11 W (10% ED)': (88, 150, 212),
                                  '4.4 W (25% ED)': (230, 118, 54)}, fx, fy)


def transmotec_k0420s(pdf):
    # Hoja K0420S (grafico en mapa de bits, fuerza en gf). Grilla detectada a
    # zoom 4 sobre el recorte: x = 0.5 mm en 25 px, 153.4 px/mm;
    # y = 0 gf en 645 px, 3.465 px/gf. La curva de 10 W se identifica como la
    # de mayor fuerza (el orden de la leyenda coincide con el de las curvas).
    page = pymupdf.open(pdf)[0]
    z, clip = 4, pymupdf.Rect(95, 530, 315, 700)
    fx = lambda px: 0.5 + (px - 25) / 153.4
    fy = lambda py: (645 - py) / 3.465 * 0.00980665
    c = raster(page, clip, z, {'10 W (10% ED)': (240, 100, 40),
                               '4 W (25% ED)': (64, 84, 164)}, fx, fy,
               excluir=pymupdf.Rect(270, 530, 315, 612))
    # la curva de 10 W sale del grafico por arriba (>180 gf) antes de 2 mm;
    # a la izquierda solo quedan las lineas guia de la leyenda. Se completa
    # con el tope del grafico (180 gf), que es una cota inferior.
    c['10 W (10% ED)'] = [(x / 10, 180 * 0.00980665) for x in range(5, 20)] + \
        [p for p in c['10 W (10% ED)'] if 2.0 <= p[0] <= 5.5]
    c['4 W (25% ED)'] = [p for p in c['4 W (25% ED)'] if 0.5 <= p[0] <= 5.5]
    return c


# --------------------------------------------------------------------------
# Datos tabulados en la hoja (no hace falta digitalizar)
# --------------------------------------------------------------------------
TABULADOS = {
    # Magnet-Schultz 312, tabla "Performance and dimensional data", F_M en N
    'MSA 312': {
        '40 W (10% pulso)': [(0, 13.4), (1, 9.7), (2, 7.8), (3, 6.0), (4, 4.5),
                             (6, 2.5), (8, 1.5), (10, 0.8)],
        '9 W (25% ED)': [(0, 12.5), (1, 2.8), (2, 1.7), (3, 1.3), (4, 0.9), (6, 0.3)],
    },
    # Ledex B12 hoja RS/Mouser, "Typical Pull Force (oz.)", 25% ED.
    # El valor "18." a 0.080 in es una errata de la hoja (1.8 oz).
    'Ledex B12 (tabla)': {
        '5.2 W (25% ED)': [(0.254 * k, 0.2780139 * f) for k, f in
                           ((1, 9.0), (2, 6.5), (3, 5.3), (4, 4.0), (5, 3.6),
                            (6, 3.0), (8, 1.8), (10, 1.3))],
    },
    # Kendrion BI 13: la hoja solo da fuerza inicial y final
    'Kendrion BI 13': {'7 W (25% ED)': [(3.0, 1.0), (0.0, 4.0)]},
}


HERE = os.path.dirname(os.path.abspath(__file__))
FUE = os.path.join(HERE, 'fuentes')
FIG = os.path.join(HERE, 'figuras')
GEEPLUS = os.path.join(FUE, 'geeplus_catalogo2024_p22-51-54-56-57-58.pdf')
LEDEX = os.path.join(FUE, 'ledex_openframe_2020_p3-10.pdf')


def extraer():
    cat = pymupdf.open(GEEPLUS)
    res = {}
    # páginas del extracto: 3 = p. 56 (110C), 4 = p. 57 (141C), 5 = p. 58 (144C)
    for modelo, pg in (('Geeplus 110C', 3), ('Geeplus 141C', 4), ('Geeplus 144C', 5)):
        res[modelo] = geeplus(cat[pg])
    for modelo in ('CA0422', 'CA0425'):
        c, _ = takaha(pymupdf.open(os.path.join(FUE, 'takaha_' + modelo + '.pdf'))[0])
        res['Takaha ' + modelo] = c
    res['Ledex B12'] = ledex_b12(LEDEX)
    res['Geeplus RD-A420'] = geeplus_rda420(os.path.join(FUE, 'geeplus_RD-A420.pdf'))
    res['Transmotec K0420S'] = transmotec_k0420s(os.path.join(FUE, 'transmotec_K0420S.pdf'))
    res.update(TABULADOS)
    return res


X_IMP = 0.5
M_PUNTA = 1.0e-3   # masa de punta de impacto supuesta [kg]

# (clave en json, curva, x_ini [mm], masa movil [g] o None, etiqueta corta)
CANDIDATOS = [
    ('Geeplus 141C', '10% ED', 3.0, 2.5, '141C'),
    ('Takaha CA0422', '24 W (6% ED)', 3.0, None, 'CA0422'),
    ('Geeplus 110C', '10% ED', 2.0, 1.0, '110C'),
    ('Takaha CA0425', '24 W (6% ED)', 3.0, None, 'CA0425'),
    ('Geeplus 144C', '10% ED', 3.5, 3.0, '144C'),
    ('Kendrion BI 13', '7 W (25% ED)', 3.0, 6.0, 'BI 13'),
    ('Ledex B12', '13 W (10% ED)', 3.0, 1.4, 'B12 (10%)'),
    ('Ledex B12', '5.2 W (25% ED)', 2.54, 1.4, 'B12P-255 (25%)'),
    ('MSA 312', '40 W (10% pulso)', 3.0, 7.0, 'MSA 312'),
    ('Transmotec K0420S', '10 W (10% ED)', 3.0, None, 'K0420S'),
    ('Geeplus RD-A420', '11 W (10% ED)', 3.0, 2.0, 'RD-A420'),
]
# Embolo sin dato: acero phi 4 mm x ~20 mm (CA04xx) o phi 3 x ~16 (K0420S)
MASA_ESTIMADA = {'CA0422': 2.0, 'CA0425': 2.2, 'K0420S': 1.0}


def curva(data, modelo, clave):
    p = sorted(data[modelo][clave])
    x = np.array([q[0] for q in p])
    f = np.array([q[1] for q in p])
    # quitar duplicados en x
    x, idx = np.unique(np.round(x, 4), return_index=True)
    return x, f[idx]


def integral(x, f, a, b):
    xs = np.linspace(a, b, 400)
    return float(np.trapezoid(np.interp(xs, x, f), xs))


def analizar(data):
    res = []
    for modelo, clave, x0, m, et in CANDIDATOS:
        x, f = curva(data, modelo, clave)
        xmin = x.min()
        w_util = integral(x, f, X_IMP, x0)
        w_tope = integral(x, f, max(xmin, 0.0), x0)
        f_imp = float(np.interp(X_IMP, x, f))
        f_ini = float(np.interp(x0, x, f))
        masa = m if m is not None else MASA_ESTIMADA[et]
        mt = masa * 1e-3 + M_PUNTA
        res.append(dict(
            modelo=modelo, curva=clave, etiqueta=et, x_ini=x0,
            x_min_dato=round(float(xmin), 2),
            W_util_mJ=round(w_util, 2), W_hasta_tope_mJ=round(w_tope, 2),
            frac_ultimo_medio_mm=round(1 - w_util / w_tope, 2) if xmin < 0.3 else None,
            F_imp_N=round(f_imp, 2), F_ini_N=round(f_ini, 2),
            relacion_F=round(f_imp / f_ini, 1),
            S_01=round(f_imp * 0.1 / w_util * 100, 1),
            masa_g=masa, masa_estimada=m is None,
            v_max=round((2 * w_util * 1e-3 / mt) ** 0.5, 2),
            v_4mJ=round((2 * 4e-3 / mt) ** 0.5, 2)))
    return res


def validacion(data):
    """Controles cruzados contra valores publicados."""
    out = {}
    for mod, k, ref in (('Takaha CA0422', '24 W (6% ED)', 2.00),
                        ('Takaha CA0425', '24 W (6% ED)', 2.50),
                        ('Takaha CA0422', '1.5 W (100% ED)', 0.18)):
        x, f = curva(data, mod, k)
        out[f'{mod} {k} a 3 mm'] = dict(publicado=ref, extraido=round(float(np.interp(3.0, x, f)), 3))
    x, f = curva(data, 'Ledex B12', '5.2 W (25% ED)')
    tab = TABULADOS['Ledex B12 (tabla)']['5.2 W (25% ED)']
    out['Ledex B12 25% curva vs tabla'] = [
        dict(x_mm=round(xx, 3), tabla=round(ff, 3), curva=round(float(np.interp(xx, x, f)), 3))
        for xx, ff in tab]
    return out


# ---------------------------------------------------------------- figuras
INK, SEC, MUT, GRID = '#1e2328', '#52514e', '#8a8880', '#e4e6ea'
S1, S2, S3 = '#2a78d6', '#eb6834', '#1baf7a'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'axes.edgecolor': MUT, 'axes.labelcolor': SEC,
                     'xtick.color': SEC, 'ytick.color': SEC,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'pdf.fonttype': 42})


def guardar(fig, nombre):
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(FIG, f'{nombre}.{ext}'), dpi=200)
    plt.close(fig)


def figuras(data, res):
    orden = [r for r in res if r['etiqueta'] != 'B12P-255 (25%)']
    fig, axs = plt.subplots(3, 4, figsize=(7.2, 6.4), sharex=True)
    for ax in axs.flat[len(orden):]:
        ax.axis('off')
    for ax, r in zip(axs.flat, orden):
        x, f = curva(data, r['modelo'], r['curva'])
        sel = x <= 5.0
        ax.plot(x[sel], f[sel], color=S1, lw=1.6)
        xs = np.linspace(X_IMP, r['x_ini'], 100)
        ax.fill_between(xs, 0, np.interp(xs, x, f), color=S1, alpha=0.18, lw=0)
        ax.axvline(X_IMP, color=S2, lw=1.0, ls=(0, (3, 2)))
        ax.set_title(f"{r['etiqueta']} · {r['curva']}", fontsize=7, color=INK, loc='left')
        ax.text(0.96, 0.92, f"{r['W_util_mJ']:.1f} mJ".replace('.', ','), transform=ax.transAxes,
                ha='right', va='top', fontsize=8.5, fontweight='bold', color=INK)
        ax.set_ylim(0, max(4.2, min(14, float(np.interp(0.4, x, f)) * 1.15)))
        ax.set_xlim(0, 5)
        ax.grid(color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.xaxis.set_tick_params(labelbottom=True)
    for ax in axs[:, 0]:
        ax.set_ylabel('F [N]')
    for ax in list(axs[2, :2]) + list(axs[1, 2:]):
        ax.set_xlabel('x [mm]')
    fig.tight_layout(h_pad=1.0, w_pad=0.6)
    guardar(fig, 'fig_curvas')

    rs = sorted(res, key=lambda r: r['W_util_mJ'])
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    y = np.arange(len(rs))
    ax.set_ylim(-1.1, len(rs) - 0.5)
    ax.axvspan(3, 5, color=S3, alpha=0.15, lw=0)
    ax.text(4, -0.75, 'objetivo 3–5 mJ', ha='center', va='center', fontsize=7.5, color=SEC)
    ax.barh(y, [min(r['W_util_mJ'], 12) for r in rs], height=0.62, color=S1,
            edgecolor='white', linewidth=1.5)
    for i, r in enumerate(rs):
        v = r['W_util_mJ']
        ax.text(min(v, 12) + 0.15, i, f"{v:.1f}".replace('.', ',') + (' →' if v > 12 else ''),
                va='center', fontsize=7.5, color=INK)
    ax.set_yticks(y, [f"{r['etiqueta']} · {r['curva']}" for r in rs], fontsize=7)
    ax.set_xlim(0, 13.5)
    ax.set_xlabel('trabajo magnético estático entre x_ini y x = 0,5 mm [mJ]')
    ax.grid(axis='x', color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    guardar(fig, 'fig_energia')

    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    for et, col in (('141C', S1), ('CA0422', S2), ('110C', S3)):
        r = next(q for q in res if q['etiqueta'] == et)
        x, f = curva(data, r['modelo'], r['curva'])
        xs = np.linspace(X_IMP, r['x_ini'], 200)
        ax.plot(xs, np.interp(xs, x, f) / r['F_ini_N'], color=col, lw=1.8)
        ax.text(X_IMP - 0.05, float(np.interp(X_IMP, x, f)) / r['F_ini_N'], et,
                ha='right', va='center', fontsize=7.5, color=INK)
    ax.axhline(1, color=MUT, lw=0.8)
    ax.set_xlim(0, 3.1)
    ax.set_xlabel('distancia al tope x [mm]')
    ax.set_ylabel('F(x) / F(x_ini)')
    ax.grid(color=GRID, lw=0.5)
    fig.tight_layout()
    guardar(fig, 'fig_forma')


# ------------------------------------------------- capturas de las hojas
ROJO = (0.85, 0.1, 0.1)
R = pymupdf.Rect


def hojas():
    """Capturas de página completa; recuadros rojos sobre los datos citados."""
    trabajos = [
        (GEEPLUS, 4, 'ds_geeplus_141C', ['Life Expectancy (cycles): >5M'], [R(172, 279, 278, 304)]),
        (GEEPLUS, 3, 'ds_geeplus_110C', ['Life Expectancy (cycles): >5M'], [R(215, 290, 336, 313)]),
        (GEEPLUS, 5, 'ds_geeplus_144C', ['Life Expectancy (cycles): >5M'], [R(378, 266, 484, 300)]),
        (GEEPLUS, 1, 'ds_geeplus_vida', [], [R(69, 481, 565, 621)]),
        (GEEPLUS, 2, 'ds_geeplus_personalizacion', [], []),
        (GEEPLUS, 0, 'ds_geeplus_VM1614', [], []),
        (os.path.join(FUE, 'takaha_CA0422.pdf'), 0, 'ds_takaha_CA0422', [], []),
        (os.path.join(FUE, 'takaha_CA0425.pdf'), 0, 'ds_takaha_CA0425', [], []),
        (LEDEX, 1, 'ds_ledex_B12', ['Plunger Weight'], []),
        (LEDEX, 0, 'ds_ledex_vida', ['Life ratings', 'extend to 3 million cycles'], []),
        (os.path.join(FUE, 'ledex_B12_RS.pdf'), 0, 'ds_ledex_B12_RS', ['Plunger Weight'], []),
        (os.path.join(FUE, 'geeplus_RD-A420.pdf'), 0, 'ds_geeplus_RD-A420', [], []),
        (os.path.join(FUE, 'kendrion_BI13.pdf'), 0, 'ds_kendrion_BI13', ['Bistable design', 'Armature weight'], []),
        (os.path.join(FUE, 'transmotec_K0420S.pdf'), 0, 'ds_transmotec_K0420S', ['Life time'], [R(140, 378, 238, 391)]),
        (os.path.join(FUE, 'msa_312.pdf'), 1, 'ds_msa_312', ['Armature Weight'], []),
    ]
    for f, i, nombre, textos, rects in trabajos:
        p = pymupdf.open(f)[i]
        for t in textos:
            for r in p.search_for(t):
                p.draw_rect(r + (-2, -1, 2, 1), color=ROJO, width=1.2)
        for r in rects:
            p.draw_rect(r, color=ROJO, width=1.2)
        p.get_pixmap(matrix=pymupdf.Matrix(2, 2)).save(os.path.join(FIG, nombre + '.png'))


def main():
    os.makedirs(FIG, exist_ok=True)
    data = extraer()
    json.dump(data, open(os.path.join(HERE, 'curvas.json'), 'w'), indent=0)
    res = analizar(data)
    val = validacion(data)
    json.dump(dict(supuestos=dict(x_imp_mm=X_IMP, masa_punta_g=M_PUNTA * 1e3,
                                  masa_estimada_g=MASA_ESTIMADA),
                   validacion=val, candidatos=res),
              open(os.path.join(HERE, 'resultados.json'), 'w'), indent=1, ensure_ascii=False)
    for r in res:
        print(f"{r['etiqueta']:16s} W={r['W_util_mJ']:5.2f} mJ (tope {r['W_hasta_tope_mJ']:5.2f})"
              f"  F {r['F_ini_N']:.2f}->{r['F_imp_N']:.2f} N  S={r['S_01']}%  "
              f"v={r['v_max']} v4={r['v_4mJ']}")
    print(json.dumps(val, indent=1))
    figuras(data, res)
    hojas()


if __name__ == '__main__':
    main()
