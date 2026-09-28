#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figuras del informe de seleccion del LED OSLON SSL 80.

Genera en assets/:
    led-geometria, led-captura, led-sensibilidad   esquemas y graficos propios
    led-ds-*                                       capturas del datasheet oficial

Cada figura sale en SVG (HTML) y en PDF (LaTeX). Las capturas se recortan del
PDF oficial en forma vectorial para el LaTeX y rasterizadas para el HTML.

Uso:
    python3 tools/led_figures.py [--datasheet ruta.pdf]

Si no se indica --datasheet, se descarga a tools/.cache/ desde la URL oficial.
Requiere: numpy, pymupdf, cairosvg.
"""
import base64
import math
import os
import sys
import urllib.request

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_figures import (OUT, INK, SEC, MUT, NAV, S1, S2, S3, SURF, GRID,  # noqa: E402
                          svg, txt, rect, line, wrap, _head, _legend, esc)
import led_montecarlo as mc  # noqa: E402

DS_URL = 'https://look.ams-osram.com/m/16996c4989af2a7d/original/GW-CS8PM1-PM.pdf'
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache')
FUENTE_DS = ('Fuente: ams OSRAM, datasheet GW CS8PM1.PM, versión 1.10, '
             '2026-03-05.')
ALU = '#b9bec6'
ALU_D = '#8d949e'
AMBAR = '#fab219'


# =========================================================================
# Esquema de geometria
# =========================================================================
def led_geometria():
    W, H = 720, 470
    b, _ = _head('Geometría del módulo: LED, conducto y ventana',
                 'Corte longitudinal a escala 1 mm = 30 px. El cono verde es lo '
                 'que la ventana ve en forma directa; las líneas punteadas marcan '
                 'la media intensidad del LED (±40°).')
    k = 30.0
    cx = 250
    y_base = 400            # cara superior del PCB
    y_led = y_base - 2.2 * k  # cima de la lente ~2.2 mm
    y_emit = y_base - 0.6 * k  # plano del emisor (aprox.)
    y_win = y_emit - 7 * k   # ventana a 7 mm del LED
    r = 2.5 * k
    # cuerpo de aluminio
    b.append('<defs><pattern id="hal" width="7" height="7" '
             'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<rect width="7" height="7" fill="%s"/>'
             '<line x1="0" y1="0" x2="0" y2="7" stroke="%s" stroke-width="1.2"/>'
             '</pattern></defs>' % (ALU, ALU_D))
    wall = 38
    b.append(rect(cx - r - wall, y_win - 10, wall, y_base - y_win + 10, 'url(#hal)'))
    b.append(rect(cx + r, y_win - 10, wall, y_base - y_win + 10, 'url(#hal)'))
    # PCB
    b.append(rect(cx - r - wall - 10, y_base, 2 * (r + wall) + 20, 16, '#3d6b50', rx=2))
    b.append(txt(cx + r + wall + 16, y_base + 12, 'PCB / MCPCB', 't-small'))
    # LED: cuerpo ceramico 3.0 mm y lente
    b.append(rect(cx - 1.5 * k, y_base - 1.0 * k, 3.0 * k, 1.0 * k, '#e9e4d6', rx=2,
                  extra='stroke="%s" stroke-width="1"' % ALU_D))
    b.append('<path d="M%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f Z" fill="#fff4cf" '
             'stroke="%s" stroke-width="1"/>'
             % (cx - 1.2 * k, y_base - 1.0 * k, 1.2 * k, 1.2 * k,
                cx + 1.2 * k, y_base - 1.0 * k, AMBAR))
    # ventana/difusor
    b.append(rect(cx - r - wall, y_win - 10, 2 * (r + wall), 10, '#dbe7f3',
                  extra='stroke="%s" stroke-width="1"' % NAV))
    # cono directo (alfa)
    b.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" '
             'fill-opacity="0.18" stroke="%s" stroke-width="1.4"/>'
             % (cx, y_emit, cx - r, y_win, cx + r, y_win, S3, S3))
    # lineas de media intensidad (40 grados) hasta la pared
    t40 = math.tan(math.radians(40))
    for s in (-1, 1):
        yh = y_emit - r / t40
        b.append('<path d="M%.1f %.1f L%.1f %.1f" class="st-dash"/>'
                 % (cx, y_emit, cx + s * r, yh))
    # arco alfa
    ra = 70
    al = math.atan(2.5 / 7)
    b.append('<path d="M%.1f %.1f A%d %d 0 0 1 %.1f %.1f" class="st-hair"/>'
             % (cx, y_emit - ra, ra, ra, cx + ra * math.sin(al),
                y_emit - ra * math.cos(al)))
    b.append(line(cx, y_emit, cx, y_win, 'grid'))
    b.append(txt(cx + 20, y_emit - ra - 8, 'α = 19,65°', 't-labb'))
    # cotas
    xd = cx - r - wall - 34
    b.append(line(xd, y_emit, xd, y_win, 'st-thin'))
    for yy in (y_emit, y_win):
        b.append(line(xd - 6, yy, xd + 6, yy, 'st-thin'))
    b.append(txt(xd - 10, (y_emit + y_win) / 2, '7 mm', 't-labb', 'end'))
    b.append(line(cx - r, y_win - 26, cx + r, y_win - 26, 'st-thin'))
    for xx in (cx - r, cx + r):
        b.append(line(xx, y_win - 32, xx, y_win - 20, 'st-thin'))
    b.append(txt(cx, y_win - 34, 'Ø 5 mm (ventana / difusor)', 't-labb', 'middle'))
    # rotulos a la derecha
    xr = 470
    notas = [
        (y_win - 5, 'Ventana circular con difusor', 'transmisión supuesta 75–90 %'),
        (y_emit - 5.2 * k, 'Pared de aluminio fresado, no pulido',
         'reflectividad y especularidad inciertas'),
        (y_emit - 2.2 * k, 'Media intensidad (±40°)',
         'impacta la pared a ≈3 mm del emisor'),
        (y_base - 0.9 * k, 'OSLON SSL 80, 3,0 × 3,0 mm',
         'lente de silicona, emisión 80°'),
    ]
    for yy, t1, t2 in notas:
        b.append('<path d="M%.1f %.1f H%.1f" class="st-hair"/>'
                 % (cx + r + wall + 4, yy, xr - 8))
        b.append(txt(xr, yy - 2, t1, 't-lab'))
        b.append(txt(xr, yy + 13, t2, 't-small'))
    b.append(txt(2, H - 8, 'Esquema del autor sobre la geometría indicada; plano '
                           'del emisor aproximado dentro de la lente.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Geometría del conducto óptico',
               'Corte del LED en el fondo de un conducto de aluminio de 5 mm de '
               'diámetro y 7 mm de largo, con el cono directo de 19,65 grados '
               'hacia la ventana.')


# =========================================================================
# Fraccion de flujo acumulada vs semiangulo
# =========================================================================
def _m(semi):
    return math.log(0.5) / math.log(math.cos(math.radians(semi)))


def led_captura():
    W, H = 720, 452
    b, y = _head('Fracción del flujo total dentro de un semiángulo',
                 'Modelo I(θ) = I0·cosᵐθ ajustado a la media intensidad de cada '
                 'LED. La ventana de Ø 5 mm a 7 mm captura en directo hasta '
                 'α = 19,65°.')
    x0, y0, pw, ph = 70, y + 26, 560, 250
    yb = y0 + ph
    for gv in range(0, 101, 20):
        gy = yb - gv / 100.0 * ph
        b.append(line(x0, gy, x0 + pw, gy, 'grid'))
        b.append(txt(x0 - 8, gy + 4, '%d %%' % gv, 't-axis', 'end'))
    for gx in range(0, 91, 10):
        xx = x0 + gx / 90.0 * pw
        b.append(txt(xx, yb + 18, '%d°' % gx, 't-axis', 'middle'))
    b.append(line(x0, yb, x0 + pw, yb, 'axis'))
    b.append(txt(x0 + pw / 2, yb + 36, 'semiángulo desde el eje del LED',
                 't-note', 'middle'))
    alfa = math.degrees(math.atan(2.5 / 7))
    xa = x0 + alfa / 90.0 * pw
    b.append(rect(x0, y0, xa - x0, ph, '#eef5f1'))
    b.append('<path d="M%.1f %.1f V%.1f" class="st-dash"/>' % (xa, y0, yb))
    b.append(txt(xa + 6, y0 + 12, 'α = 19,65°: borde de la ventana', 't-small'))
    capt = []
    series = [(S1, 40, 'OSLON SSL 80 (2φ = 80°)'),
              (S2, 60, 'LED lambertiano (2φ = 120°)'),
              (S3, 75, 'LED de 150°')]
    for color, semi, lab in series:
        m = _m(semi)
        pts = []
        for i in range(0, 91):
            f = 1 - math.cos(math.radians(i)) ** (m + 1)
            pts.append('%.1f,%.1f' % (x0 + i / 90.0 * pw, yb - f * ph))
        b.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
                 'stroke-linejoin="round"/>' % (' '.join(pts), color))
        fa = 1 - math.cos(math.radians(alfa)) ** (m + 1)
        b.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="%s" '
                 'stroke-width="2"/>' % (xa, yb - fa * ph, color, SURF))
        capt.append('%s: %s %% en α' % (lab, ('%.1f' % (fa * 100)).replace('.', ',')))
    m80 = _m(40)
    f40 = 1 - math.cos(math.radians(40)) ** (m80 + 1)
    x40 = x0 + 40 / 90.0 * pw
    b.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="%s" '
             'stroke-width="2"/>' % (x40, yb - f40 * ph, S1, SURF))
    b.append(txt(x40 + 9, yb - f40 * ph + 18,
                 '%.0f %% dentro de ±40°: el resto sale más abierto' % (f40 * 100),
                 't-small'))
    b.extend(_legend([(c, l) for (c, _, _), l in zip(series, capt)], x0, H - 58,
                     cols=2, colw=300))
    b.append(txt(2, H - 8, 'Cálculo propio: F(θ) = 1 − cos^(m+1) θ. 2φ del OSLON '
                           'SSL 80 según datasheet ams OSRAM v1.10.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Fracción de flujo capturada por la ventana',
               'Curvas de flujo acumulado vs semiángulo para LEDs de 80, 120 y '
               '150 grados; en 19,65 grados capturan 19,4, 11,3 y 8,7 por ciento.')


# =========================================================================
# Sensibilidad del flujo de salida
# =========================================================================
def led_sensibilidad():
    W, H = 720, 440
    b, y = _head('Flujo de salida estimado vs reflectividad de la pared',
                 'LED bin LUMQ a 350 mA (valor medio 187 lm). Cada banda cubre '
                 'un difusor de 75 % (borde inferior) a 90 % (borde superior).')
    x0, y0, pw, ph = 70, y + 22, 560, 270
    yb = y0 + ph
    fmax = 180.0
    rmin, rmax = 0.50, 0.95
    for gv in range(0, 181, 30):
        gy = yb - gv / fmax * ph
        b.append(line(x0, gy, x0 + pw, gy, 'grid'))
        b.append(txt(x0 - 8, gy + 4, '%d' % gv, 't-axis', 'end'))
    b.append(txt(x0 - 8, y0 - 10, 'lm', 't-axis', 'end'))
    rs = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    for rv in rs:
        xx = x0 + (rv - rmin) / (rmax - rmin) * pw
        b.append(txt(xx, yb + 18, '%.2f' % rv, 't-axis', 'middle'))
    b.append(line(x0, yb, x0 + pw, yb, 'axis'))
    b.append(txt(x0 + pw / 2, yb + 36, 'reflectividad de la pared del conducto',
                 't-note', 'middle'))

    def X(rv):
        return x0 + (rv - rmin) / (rmax - rmin) * pw

    def Y(v):
        return yb - v / fmax * ph

    flujo = 187.0
    for modo, color, lab in (('difusa', S2, 'Pared difusa (conservador)'),
                             ('especular', S1, 'Pared especular (optimista)')):
        eta = [mc.eficiencia(rv, modo, n=120000) for rv in rs]
        hi = [(X(rv), Y(e * flujo * 0.90)) for rv, e in zip(rs, eta)]
        lo = [(X(rv), Y(e * flujo * 0.75)) for rv, e in zip(rs, eta)]
        poly = ' '.join('%.1f,%.1f' % p for p in hi + lo[::-1])
        b.append('<polygon points="%s" fill="%s" fill-opacity="0.22"/>' % (poly, color))
        for pts in (hi, lo):
            b.append('<polyline points="%s" fill="none" stroke="%s" '
                     'stroke-width="2"/>' % (' '.join('%.1f,%.1f' % p for p in pts),
                                             color))
        if modo == 'especular':
            xl, yl = hi[-1]
            b.append(txt(xl - 4, yl - 8, lab, 't-labb', 'end'))
        else:
            xl, yl = lo[1]
            b.append(txt(xl, yl + 20, lab, 't-labb'))
    # objetivo y captura directa
    b.append('<path d="M%.1f %.1f H%.1f" stroke="%s" stroke-width="1.5" '
             'stroke-dasharray="6 4"/>' % (x0, Y(100), x0 + pw, INK))
    b.append(txt(x0 + 6, Y(100) - 6, 'Objetivo: 100 lm útiles', 't-labb'))
    fd = mc.captura_directa()[0] * flujo
    b.append('<path d="M%.1f %.1f H%.1f" class="st-dash"/>' % (x0, Y(fd), x0 + pw))
    b.append(txt(x0 + pw - 4, Y(fd) + 14,
                 'Solo luz directa, sin difusor: %.0f lm' % fd, 't-small', 'end'))
    b.append(txt(2, H - 8, 'Cálculo propio: Monte Carlo de tools/led_montecarlo.py '
                           '(fuente puntual cos^2,6, fondo absorbente).', 't-note'))
    return svg(W, H, '\n'.join(b), 'Sensibilidad del flujo de salida',
               'Dos bandas de flujo de salida en lúmenes contra la reflectividad '
               'de la pared, para pared difusa y especular, con la línea de '
               'objetivo en 100 lúmenes.')


# =========================================================================
# Capturas del datasheet
# =========================================================================
# id, pagina (1-based), recorte (x0, y0, x1, y1) en puntos, textos a resaltar
CAPTURAS = [
    ('led-ds-portada', 2, (40, 88, 560, 640), []),
    ('led-ds-pedido', 3, (40, 92, 560, 512), ['LUMQ-A333-1', 'LUMQ-XX53-1']),
    ('led-ds-maximos', 4, (40, 92, 560, 402), []),
    ('led-ds-caracteristicas', 5, (40, 92, 560, 290), []),
    ('led-ds-grupos', 6, (40, 92, 560, 500), ['LU', 'MP', 'MQ']),
    ('led-ds-radiacion', 12, (36, 418, 560, 730), []),
    ('led-ds-corriente', 13, (36, 92, 560, 395), []),
    ('led-ds-temperatura', 14, (36, 92, 560, 395), []),
    ('led-ds-derating', 15, (36, 92, 300, 395), []),
    ('led-ds-dimensiones', 16, (36, 92, 560, 420), []),
    ('led-ds-footprint', 17, (36, 92, 560, 395), []),
    ('led-ds-reflow', 18, (36, 92, 560, 730), []),
]


def _datasheet(ruta):
    if ruta:
        return ruta
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, 'GW-CS8PM1-PM.pdf')
    if not os.path.exists(ruta):
        print('descargando datasheet oficial...')
        urllib.request.urlretrieve(DS_URL, ruta)
    return ruta


def _filas(page, textos, clip):
    """Rectangulos de fila completa para los textos a resaltar."""
    out = []
    for t in textos:
        for r in page.search_for(t, clip=clip):
            if len(t) <= 2 and r.x0 > clip[0] + 60:
                continue    # grupos: solo la etiqueta de la primera columna
            out.append(pymupdf.Rect(clip[0] + 2, r.y0 - 2.5, clip[2] - 2, r.y1 + 2.5))
    return out


def capturas(ruta):
    src = pymupdf.open(_datasheet(ruta))
    for fid, pno, clip, textos in CAPTURAS:
        page = src[pno - 1]
        c = pymupdf.Rect(*clip)
        filas = _filas(page, textos, clip)
        doc = pymupdf.open()
        np_ = doc.new_page(width=c.width, height=c.height)
        np_.show_pdf_page(np_.rect, src, pno - 1, clip=c)
        for fr in filas:
            fr = pymupdf.Rect(fr.x0 - c.x0, fr.y0 - c.y0, fr.x1 - c.x0, fr.y1 - c.y0)
            np_.draw_rect(fr, color=(0.65, 0.41, 0.05), fill=(0.98, 0.70, 0.10),
                          fill_opacity=0.22, width=0.8)
        doc.save(os.path.join(OUT, fid + '.pdf'), garbage=4, deflate=True)
        pix = np_.get_pixmap(dpi=170)
        png = pix.tobytes('png')
        w, h = pix.width, pix.height
        cuerpo = ('<image width="%d" height="%d" href="data:image/png;base64,%s"/>'
                  % (w, h, base64.b64encode(png).decode()))
        s = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
             'width="%d" height="%d" role="img" aria-labelledby="ti de">\n'
             '<title id="ti">%s</title><desc id="de">%s</desc>\n%s\n</svg>\n'
             % (w, h, w, h, esc('Captura del datasheet GW CS8PM1.PM'),
                esc(FUENTE_DS), cuerpo))
        with open(os.path.join(OUT, fid + '.svg'), 'w', encoding='utf-8') as fh:
            fh.write(s)
        print('%-26s p.%-2d %4dx%-4d %7d bytes' % (fid, pno, w, h, len(s)))


PROPIAS = [('led-geometria', led_geometria), ('led-captura', led_captura),
           ('led-sensibilidad', led_sensibilidad)]


def main():
    import cairosvg
    ruta = None
    if '--datasheet' in sys.argv:
        ruta = sys.argv[sys.argv.index('--datasheet') + 1]
    os.makedirs(OUT, exist_ok=True)
    for name, fn in PROPIAS:
        path = os.path.join(OUT, name + '.svg')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(fn())
        cairosvg.svg2pdf(url=path, write_to=os.path.join(OUT, name + '.pdf'))
        print('%-26s ok' % name)
    capturas(ruta)


if __name__ == '__main__':
    main()
