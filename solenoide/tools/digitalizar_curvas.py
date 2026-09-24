#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae las curvas fuerza-carrera de las hojas de datos en PDF.

Las curvas de Geeplus y Takaha son trazos vectoriales dentro del PDF: se leen
los segmentos (rectas y Bezier) y se convierten a unidades fisicas con la
posicion de las etiquetas de los ejes. No hay lectura a ojo.

Uso:
    python3 digitalizar_curvas.py <carpeta_pdfs> <salida.json>
"""
import json
import math
import os
import sys

import pymupdf


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
    # Catalogo Ledex Open Frame (2020), pagina "Box Frame Size B12".
    # Calibracion con los centros de las etiquetas: x "0" = 343.25 pt,
    # x "0.200 in" = 553.45 pt; y "0" = 452.15 pt, y "14.0 oz" = 168.4 pt.
    page = pymupdf.open(pdf)[9]
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


def main():
    src, dst = sys.argv[1], sys.argv[2]
    cat = pymupdf.open(os.path.join(src, 'GEEPLUS-ELECTROMECHANICAL-ACTUATORS-CATALOGUE-2024-1.pdf'))
    res = {}
    for modelo, pg in (('Geeplus 110C', 56), ('Geeplus 141C', 57), ('Geeplus 144C', 58)):
        res[modelo] = geeplus(cat[pg])
    for modelo in ('CA0422', 'CA0425'):
        c, cal = takaha(pymupdf.open(os.path.join(src, modelo + '.pdf'))[0])
        print(modelo, 'calibracion', cal, file=sys.stderr)
        res['Takaha ' + modelo] = c
    res['Ledex B12'] = ledex_b12(os.path.join(src, 'ledex_openframe_2020.pdf'))
    res['Geeplus RD-A420'] = geeplus_rda420(os.path.join(src, 'geeplus_RD-A420.pdf'))
    res['Transmotec K0420S'] = transmotec_k0420s(os.path.join(src, 'transmotec_K0420S.pdf'))
    res.update(TABULADOS)
    with open(dst, 'w') as f:
        json.dump(res, f, indent=1)
    for m, cs in res.items():
        for k, p in cs.items():
            p = sorted(p)
            print(f'{m:14s} {k:16s} x={p[0][0]:.2f}..{p[-1][0]:.2f}  '
                  f'F={p[0][1]:.2f}..{p[-1][1]:.2f} N  n={len(p)}')


if __name__ == '__main__':
    main()
