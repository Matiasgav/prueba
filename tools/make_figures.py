#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las figuras del informe como SVG (y PDF para la version LaTeX).

Todas las figuras son esquemas y graficos originales. Los graficos con datos
llevan la fuente en el pie; los esquemas se marcan como esquema del autor.

Paleta categorica validada (dataviz): slots 1-3 sobre superficie blanca.
"""
import os
import subprocess
import sys

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'assets')

# --- tokens ---------------------------------------------------------------
INK = '#16202b'
SEC = '#52514e'
MUT = '#8a8880'
GRID = '#e4e6ea'
BASE = '#c3c2b7'
SURF = '#ffffff'
NAV = '#14496b'
S1 = '#2a78d6'      # slot 1 - azul
S2 = '#eb6834'      # slot 2 - naranja
S3 = '#1baf7a'      # slot 3 - aqua
GOOD = '#0ca30c'
WARN = '#fab219'
CRIT = '#d03b3b'
# rampa ordinal azul (paso mas claro >= 250 sobre blanco)
RAMP = ['#0d366b', '#184f95', '#256abf', '#3987e5', '#6da7ec', '#9ec5f4']
PIRA = ['#123f76', '#256abf', '#5598e7', '#9ec5f4']
FONT = ('system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",'
        '"DejaVu Sans",Arial,sans-serif')

STYLE = """
  text {{ font-family: {font}; fill: {ink}; }}
  .t-title {{ font-size: 15px; font-weight: 700; }}
  .t-sub   {{ font-size: 12px; fill: {sec}; }}
  .t-lab   {{ font-size: 12px; }}
  .t-labb  {{ font-size: 12px; font-weight: 600; }}
  .t-small {{ font-size: 11px; fill: {sec}; }}
  .t-axis  {{ font-size: 11px; fill: {mut}; font-variant-numeric: tabular-nums; }}
  .t-val   {{ font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums; }}
  .t-note  {{ font-size: 10.5px; fill: {mut}; }}
  .t-inv   {{ fill: #ffffff; }}
  .grid    {{ stroke: {grid}; stroke-width: 1; }}
  .axis    {{ stroke: {base}; stroke-width: 1; }}
  .st-thin {{ fill: none; stroke: {nav}; stroke-width: 1.6; }}
  .st-hair {{ fill: none; stroke: {mut}; stroke-width: 1; }}
  .st-dash {{ fill: none; stroke: {mut}; stroke-width: 1; stroke-dasharray: 4 3; }}
""".format(font=FONT, ink=INK, sec=SEC, mut=MUT, grid=GRID, base=BASE, nav=NAV)


def svg(width, height, body, title, desc=''):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'width="%d" height="%d" role="img" aria-labelledby="ti de">\n'
        '<title id="ti">%s</title><desc id="de">%s</desc>\n'
        '<style>%s</style>\n'
        '<rect width="%d" height="%d" fill="%s"/>\n%s\n</svg>\n'
        % (width, height, width, height, esc(title), esc(desc), STYLE,
           width, height, SURF, body))


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def txt(x, y, s, cls='t-lab', anchor='start', extra=''):
    return ('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s"%s>%s</text>'
            % (x, y, cls, anchor, (' ' + extra) if extra else '', esc(s)))


def rect(x, y, w, h, fill, rx=0, extra=''):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
            'rx="%.1f"%s/>' % (x, y, w, h, fill, rx, (' ' + extra) if extra else ''))


def bar_h(x, y, w, h, fill):
    """Barra horizontal: extremo redondeado (4px) del lado del dato."""
    if w <= 5:
        return rect(x, y, max(w, 1.5), h, fill)
    r = 4.0
    return ('<path d="M%.1f %.1f H%.1f a%.1f %.1f 0 0 1 %.1f %.1f V%.1f '
            'a%.1f %.1f 0 0 1 %.1f %.1f H%.1f Z" fill="%s"/>'
            % (x, y, x + w - r, r, r, r, r, y + h - r, r, r, -r, r, x, fill))


def line(x1, y1, x2, y2, cls='axis'):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"/>'
            % (x1, y1, x2, y2, cls))


def wrap(x, y, text, cls, width_chars, lh=14, anchor='start'):
    """Texto en varias lineas por conteo de caracteres."""
    words, lines, cur = text.split(), [], ''
    for w in words:
        if len(cur) + len(w) + 1 <= width_chars:
            cur = (cur + ' ' + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return '\n'.join(txt(x, y + i * lh, ln, cls, anchor)
                     for i, ln in enumerate(lines))


def footer(width, y, source):
    return txt(0 + 2, y, source, 't-note')


# =========================================================================
# F1 - Jerarquia de evidencia
# =========================================================================
def fig_evidencia():
    W, H = 720, 372
    b, _ = _head('Jerarquía de evidencia aplicada al estudio',
                 'La conclusión de cada afirmación se pondera por el nivel '
                    'de la fuente que la sostiene.')
    cx, top, bot = 140, 70, 336
    hw0, hw1 = 22.0, 124.0
    bands = [
        ('A', 'Máxima prioridad',
         'EPRI · DOE / NRC / IAEA / EIA / FERC / NERC · IEEE / IEC / ASME / API / '
         'AMPP · CIGRE · documentos oficiales de utilities · papers revisados por '
         'pares · patentes originales · documentación técnica de fabricante · '
         'licitaciones y contratos oficiales'),
        ('B', 'Respaldo sólido',
         'Proceedings de congresos · tesis · informes institucionales · '
         'presentaciones técnicas EPRI/OEM · casos técnicos de utilities · '
         'asociaciones industriales (HRSG Forum, CCJ)'),
        ('C', 'Indicativo',
         'Páginas de proveedores de servicios · casos comerciales · notas '
         'técnicas secundarias · prensa especializada'),
        ('D', 'Solo para descubrir la fuente primaria',
         'Agregadores de contratos · blogs · repositorios no revisados · notas '
         'de marketing de terceros. No se usa como evidencia final si el '
         'original es localizable.'),
    ]
    n = len(bands)
    bh = (bot - top) / n
    for i, (letra, titulo, fuentes) in enumerate(bands):
        y1 = top + i * bh
        y2 = y1 + bh - 2
        f = lambda y: hw0 + (y - top) * (hw1 - hw0) / (bot - top)
        p = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f Z" '
             'fill="%s"/>' % (cx - f(y1), y1, cx + f(y1), y1,
                              cx + f(y2), y2, cx - f(y2), y2, PIRA[i]))
        b.append(p)
        cls = 't-labb t-inv' if i < 2 else 't-labb'
        b.append(txt(cx, y1 + bh / 2 + 4, 'Nivel ' + letra, cls, 'middle'))
        b.append(txt(288, y1 + 14, titulo, 't-labb'))
        b.append(wrap(288, y1 + 30, fuentes, 't-small', 66, 12.5))
    b.append(txt(2, H - 6, 'Esquema del autor a partir del marco metodológico '
                           'del estudio.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Jerarquía de evidencia',
               'Pirámide de cuatro niveles A a D con las familias de fuentes '
               'de cada nivel.')


# =========================================================================
# F2 - Escala de madurez comercial
# =========================================================================
def fig_madurez():
    W, H = 720, 230
    b, _ = _head('Escala de madurez comercial (M0–M5)',
                 'Mide despliegue real en el mercado, no nivel tecnológico '
                    '(TRL): un TRL alto con un solo cliente sigue siendo M2.')
    items = [
        ('M0', 'Sólo papers y conceptos'),
        ('M1', 'Prototipos de laboratorio'),
        ('M2', 'Demostración industrial aislada'),
        ('M3', 'Servicios comerciales iniciales'),
        ('M4', 'Múltiples proveedores y despliegues'),
        ('M5', 'Mercado maduro / commodity'),
    ]
    x0, y0, seg_h = 2, 60, 34
    total_w = W - 4
    seg_w = (total_w - 5 * 2) / 6.0
    ramp = ['#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
    for i, (code, label) in enumerate(items):
        x = x0 + i * (seg_w + 2)
        b.append(rect(x, y0, seg_w, seg_h, ramp[i],
                      rx=(4 if i in (0, 5) else 0)))
        b.append(txt(x + seg_w / 2, y0 + 22, code,
                     't-labb' + (' t-inv' if i >= 2 else ''), 'middle'))
        b.append(wrap(x + seg_w / 2, y0 + seg_h + 18, label, 't-small', 17, 13,
                      'middle'))
    y1 = y0 + seg_h + 74
    b.append(line(2, y1, W - 2, y1, 'grid'))
    b.append(txt(2, y1 + 20, 'Dónde compite un producto nuevo', 't-labb'))
    b.append(wrap(2, y1 + 38,
                  'M0–M2 · el riesgo dominante es técnico: hay que demostrar '
                  'que el robot resuelve el problema físico.', 't-small', 52))
    b.append(wrap(370, y1 + 38,
                  'M3–M5 · el riesgo dominante es comercial: hay que demostrar '
                  'una ventaja frente a un incumbente que ya cobra.',
                  't-small', 52))
    b.append(txt(2, H - 6, 'Esquema del autor.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Escala de madurez comercial M0 a M5',
               'Barra segmentada en seis niveles de madurez comercial.')


# =========================================================================
# F3 - Proceso de investigacion
# =========================================================================
def fig_proceso():
    W, H = 720, 300
    b, _ = _head('Proceso de evaluación por candidato',
                 'Cada etapa puede descartar el candidato; el orden evita '
                    'gastar esfuerzo en oportunidades ya cerradas.')
    fases = [
        ('1', 'Dolor económico', 'Costo actual, outage,\nhoras-hombre,\nriesgo'),
        ('2', 'Búsqueda histórica', 'Programas previos,\nEPRI, patentes,\nfracasos'),
        ('3', 'Landscape 2026', 'Productos vivos,\ndiscontinuados,\nadquiridos'),
        ('4', 'Whitespace', 'Qué no resuelve\nel incumbente'),
        ('5', 'Caso de negocio', 'Ticket, frecuencia,\nreutilización RI,\nmoat'),
    ]
    bw, gap, y0, bh = 128, 20, 62, 96
    for i, (num, tit, det) in enumerate(fases):
        x = 2 + i * (bw + gap)
        b.append(rect(x, y0, bw, bh, '#f2f6fa', rx=5))
        b.append(rect(x, y0, 3, bh, NAV))
        b.append(txt(x + 12, y0 + 20, 'Etapa ' + num, 't-note'))
        b.append(wrap(x + 12, y0 + 38, tit, 't-labb', 16, 14))
        yy = y0 + (56 if len(tit) < 16 else 70)
        for k, ln in enumerate(det.split('\n')):
            b.append(txt(x + 12, yy + k * 13, ln, 't-small'))
        if i < len(fases) - 1:
            ax = x + bw + 4
            b.append('<path d="M%.1f %.1f h10 l-4 -4 m4 4 l-4 4" fill="none" '
                     'stroke="%s" stroke-width="1.6"/>'
                     % (ax, y0 + bh / 2, MUT))
    yg = y0 + bh + 26
    b.append(rect(2, yg, W - 4, 62, '#fff8e8', rx=5))
    b.append(rect(2, yg, 3, 62, WARN))
    b.append(txt(14, yg + 20, 'Filtro aplicado en toda etapa', 't-labb'))
    b.append(wrap(14, yg + 38,
                  'Toda afirmación se clasifica como hecho verificado, '
                  'declaración de fabricante, inferencia de ingeniería o '
                  'estimación propia. Una estimación nunca se presenta como '
                  'dato publicado.', 't-small', 108))
    b.append(txt(2, H - 6, 'Esquema del autor.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Proceso de evaluación por candidato',
               'Cinco etapas encadenadas con un filtro de clasificación de '
               'evidencia aplicado a todas.')


# =========================================================================
# F4 - Cronologia de prior art
# =========================================================================
def fig_cronologia():
    W, H = 720, 210
    b, _ = _head('Línea temporal que debe reconstruirse para cada candidato',
                 'El objetivo es detectar programas anteriores y las razones '
                 'físicas o económicas por las que se detuvieron.')
    hitos = ['Problema\nidentificado', 'Primer\nprototipo', 'Investigación\nEPRI',
             'Familias de\npatentes', 'Primeros\ndespliegues',
             'Productos\ncomerciales', 'Estado\n2026']
    y = 92
    x0, x1 = 30, W - 30
    step = (x1 - x0) / (len(hitos) - 1)
    b.append(line(x0, y, x1, y, 'axis'))
    for i, h in enumerate(hitos):
        x = x0 + i * step
        last = i == len(hitos) - 1
        b.append('<circle cx="%.1f" cy="%.1f" r="5.5" fill="%s" stroke="%s" '
                 'stroke-width="2"/>' % (x, y, S1 if not last else NAV, SURF))
        for k, ln in enumerate(h.split('\n')):
            b.append(txt(x, y - 26 + k * 13 - (13 if len(h.split('\n')) > 1 else 0),
                         ln, 't-small', 'middle'))
    b.append(rect(2, 132, W - 4, 52, '#f7f9fb', rx=5))
    b.append(txt(14, 151, 'Evidencia negativa: el hallazgo más valioso', 't-labb'))
    b.append(wrap(14, 169,
                  'Productos discontinuados · programas abandonados · resultados '
                  'insuficientes · robots atascados · herramientas que no '
                  'entraron · fallas de tether · NDE sin sensibilidad · costos '
                  'que destruyeron el caso de negocio.', 't-small', 110))
    b.append(txt(2, H - 6, 'Esquema del autor.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Línea temporal de prior art',
               'Siete hitos desde la identificación del problema hasta el '
               'estado 2026.')


# =========================================================================
# F5 - Pesos de los dos rankings
# =========================================================================
def fig_pesos():
    W = 720
    filas = [
        ('Dolor económico / costo evitado', 20, 20),
        ('Whitespace y competencia (IP en B)', 15, 20),
        ('Barrera técnica: factibilidad (A) / defensa (B)', 15, 20),
        ('Tamaño de mercado', 10, 15),
        ('Ticket y margen', 10, 10),
        ('Reutilización de la plataforma RI', 15, 5),
        ('Frecuencia y recurrencia', 10, 5),
        ('Overlap de clientes / canal comercial', 5, None),
        ('Carga regulatoria (inversa)', None, 5),
    ]
    top, rh = 96, 34
    H = top + len(filas) * rh + 56
    b, _ = _head('Pesos de los dos criterios de ranking',
                 'Ranking A prioriza el próximo producto de bajo riesgo; '
                 'Ranking B, la defensa a largo plazo. Los pesos son una '
                 'decisión de método, no un dato medido.')
    # leyenda
    b += [rect(2, 52, 10, 10, S1, rx=2), txt(18, 61, 'Ranking A — fast-follow',
                                             't-small'),
          rect(190, 52, 10, 10, S2, rx=2),
          txt(206, 61, 'Ranking B — moat / upside', 't-small')]
    lx, bx, bw_max = 2, 360, 250
    scale = bw_max / 20.0
    b.append(line(bx, top - 8, bx, top + len(filas) * rh - 6, 'axis'))
    for gv in (5, 10, 15, 20):
        gx = bx + gv * scale
        b.append(line(gx, top - 8, gx, top + len(filas) * rh - 6, 'grid'))
        b.append(txt(gx, top - 14, '%d%%' % gv, 't-axis', 'middle'))
    for i, (lab, a, bb) in enumerate(filas):
        y = top + i * rh
        b.append(wrap(lx, y + 9, lab, 't-small', 52, 12))
        for j, (v, color) in enumerate(((a, S1), (bb, S2))):
            yy = y - 4 + j * 13
            if v is None:
                b.append(txt(bx + 6, yy + 9, 'no aplica en este ranking',
                             't-note'))
                continue
            b.append(bar_h(bx, yy, v * scale, 11, color))
            b.append(txt(bx + v * scale + 6, yy + 9, '%d%%' % v, 't-val'))
    b.append(txt(2, H - 30, 'Sensibilidad obligatoria: se recalcula el orden '
                            'moviendo ±20 % el peso de competencia, desarrollo '
                            'y mercado.', 't-small'))
    b.append(txt(2, H - 8, 'Fuente: marco de evaluación del estudio. Los pesos '
                           'son síntesis de ingeniería y negocio, no una '
                           'medición.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Pesos de los dos rankings',
               'Barras horizontales agrupadas comparando el peso de cada '
               'criterio en el Ranking A y en el Ranking B.')


# =========================================================================
# F6 - Economia de la inspeccion de bus isofasico (IPB)
# =========================================================================
def fig_ipb_economia():
    W, H = 720, 322
    b, _ = _head('Bus isofásico: costo relativo de la inspección',
                 'Caso único reportado por una utility. La razón 10× es de '
                    'ese caso; no está generalizada al mercado.')
    x0, y0, rowh = 210, 96, 46
    maxw = 340
    datos = [('Inspección manual con acceso y andamiaje', 10.0, '#c9ced6'),
             ('Inspección con crawler robótico', 1.0, S1)]
    for gv in (0, 2, 4, 6, 8, 10):
        gx = x0 + gv / 10.0 * maxw
        b.append(line(gx, y0 - 6, gx, y0 + 2 * rowh - 10, 'grid'))
        b.append(txt(gx, y0 - 12, '%d' % gv, 't-axis', 'middle'))
    b.append(txt(x0 + maxw / 2, y0 - 30, 'costo relativo (base = 1)',
                 't-note', 'middle'))
    for i, (lab, v, color) in enumerate(datos):
        y = y0 + i * rowh
        b.append(wrap(2, y + 14, lab, 't-small', 30, 13))
        b.append(bar_h(x0, y, v / 10.0 * maxw, 22, color))
        b.append(txt(x0 + v / 10.0 * maxw + 8, y + 16, '%.0f×' % v, 't-val'))
    b.append(line(x0, y0 + 2 * rowh - 10, x0 + maxw, y0 + 2 * rowh - 10, 'axis'))

    ty = y0 + 2 * rowh + 16
    tiles = [('≈ USD 100.000', 'costo de vendor por implementación,\nexperiencia '
              'de una utility'),
             ('< 1 día', 'duración de la ejecución\nde la inspección'),
             ('Inmediato', 'payback según la evaluación\nEPRI SWEEP')]
    tw = (W - 4 - 2 * 12) / 3.0
    for i, (val, lab) in enumerate(tiles):
        x = 2 + i * (tw + 12)
        b.append(rect(x, ty, tw, 78, '#f2f6fa', rx=5))
        b.append(rect(x, ty, 3, 78, NAV))
        b.append(txt(x + 12, ty + 30, val, 't-title'))
        for k, ln in enumerate(lab.split('\n')):
            b.append(txt(x + 12, ty + 48 + k * 13, ln, 't-small'))
    b.append(txt(2, H - 8, 'Fuente: EPRI, Plant Modernization Toolbox, '
                           'MTA-MA-029 (dato publicado por EPRI sobre un caso '
                           'de utility).', 't-note'))
    return svg(W, H, '\n'.join(b), 'Costo relativo de la inspección de bus '
                                   'isofásico',
               'Dos barras comparando el costo relativo de la inspección '
               'manual y la robótica, y tres indicadores del caso EPRI.')


# =========================================================================
# F7 - Economia del crawler NDE en piping enterrado
# =========================================================================
def fig_piping_economia():
    W, H = 720, 268
    b, _ = _head('Piping enterrado: rango de valor por utilización',
                 'Evaluación EPRI SWEEP. El ahorro se expresa como rango '
                    'acotado, no como valor puntual.')
    x0, y0 = 200, 92
    maxw, maxv = 400, 5.0
    for gv in (0, 1, 2, 3, 4, 5):
        gx = x0 + gv / maxv * maxw
        b.append(line(gx, y0 - 10, gx, y0 + 84, 'grid'))
        b.append(txt(gx, y0 - 16, 'USD %d M' % gv if gv else '0', 't-axis',
                     'middle'))
    # costo de implementacion: < 1 M
    b.append(wrap(2, y0 + 12, 'Costo de implementación', 't-small', 26, 13))
    b.append(bar_h(x0, y0, 1 / maxv * maxw, 20, '#c9ced6'))
    b.append(txt(x0 + 1 / maxv * maxw + 8, y0 + 15, '< 1 M', 't-val'))
    # ahorro esperado: banda 1 a 5 M
    y1 = y0 + 48
    b.append(wrap(2, y1 + 12, 'Ahorro esperado por utilización', 't-small', 26, 13))
    bx1 = x0 + 1 / maxv * maxw
    bx2 = x0 + 5 / maxv * maxw
    b.append(rect(bx1, y1, bx2 - bx1, 20, S1, rx=4))
    b.append(txt((bx1 + bx2) / 2, y1 + 15, '> 1 M   y   < 5 M', 't-val t-inv',
                 'middle'))
    b.append(line(x0, y0 + 84, x0 + maxw, y0 + 84, 'axis'))

    ty = y0 + 100
    b.append(rect(2, ty, W - 4, 70, '#f2f6fa', rx=5))
    b.append(rect(2, ty, 3, 70, NAV))
    b.append(txt(14, ty + 20, 'Lectura de negocio', 't-labb'))
    b.append(wrap(14, ty + 38,
                  'Payback inmediato o menor a un año y tecnología ya '
                  'comercialmente implementada en el sector nuclear: valor alto '
                  'con madurez alta. Un crawler genérico de tuberías no es una '
                  'oportunidad; sólo lo es un whitespace geométrico o de '
                  'despliegue concreto.', 't-small', 108))
    b.append(txt(2, H - 8, 'Fuente: EPRI, Plant Modernization Toolbox, '
                           'MTA-MA-017.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Rango de valor por utilización en piping '
                                   'enterrado',
               'Barra del costo de implementación y banda del ahorro esperado '
               'por utilización.')


# =========================================================================
# F8 - Mapa de candidatos
# =========================================================================
def fig_mapa_candidatos():
    W, H = 720, 500
    b, _ = _head('Posicionamiento de partida de los siete candidatos',
                 'Hipótesis de entrada al estudio, no una medición: cada '
                 'posición debe confirmarse o corregirse con evidencia.')
    px0, py0, pw, ph = 60, 74, 500, 280
    b.append(rect(px0, py0, pw, ph, '#fafbfc', rx=4))
    # rejilla
    for i in range(6):
        x = px0 + i * pw / 5.0
        b.append(line(x, py0, x, py0 + ph, 'grid'))
        b.append(txt(x, py0 + ph + 16, 'M%d' % i, 't-axis', 'middle'))
    for i in range(4):
        y = py0 + i * ph / 3.0
        b.append(line(px0, y, px0 + pw, y, 'grid'))
    b.append(txt(px0 + pw / 2, py0 + ph + 34,
                 'madurez comercial hipotética  →', 't-note', 'middle'))
    b.append('<text x="%.1f" y="%.1f" class="t-note" text-anchor="middle" '
             'transform="rotate(-90 %.1f %.1f)">reutilización de la plataforma '
             'RI  →</text>' % (px0 - 50, py0 + ph / 2, px0 - 50, py0 + ph / 2))
    for lab, yy in (('alta', 0.15), ('media', 0.5), ('baja', 0.85)):
        b.append(txt(px0 - 8, py0 + ph * yy + 4, lab, 't-axis', 'end'))

    # zonas de lectura
    b.append(txt(px0 + 12, py0 + 20, 'riesgo técnico dominante', 't-note'))
    b.append(txt(px0 + pw - 12, py0 + 20, 'riesgo comercial dominante',
                 't-note', 'end'))

    cands = [
        ('A', 3.4, 0.18, 'Bus isofásico (IPB)'),
        ('B', 4.0, 0.40, 'HRSG: headers y tubos'),
        ('C', 1.6, 0.45, 'Vaults subterráneos'),
        ('D', 4.5, 0.62, 'Piping enterrado'),
        ('E', 3.0, 0.55, 'Dry casks'),
        ('F', 4.0, 0.75, 'Penstocks y túneles'),
        ('G', 1.0, 0.86, 'Vine / everting'),
    ]
    for code, mx, my, name in cands:
        x = px0 + mx / 5.0 * pw
        y = py0 + my * ph
        b.append('<circle cx="%.1f" cy="%.1f" r="13" fill="%s" stroke="%s" '
                 'stroke-width="2"/>' % (x, y, S1, SURF))
        b.append(txt(x, y + 4, code, 't-labb t-inv', 'middle'))
        anchor = 'end' if mx > 3.6 else 'start'
        dx = -20 if anchor == 'end' else 20
        b.append(txt(x + dx, y + 4, name, 't-small', anchor))
    b.append(rect(2, py0 + ph + 54, W - 4, 62, '#fff8e8', rx=5))
    b.append(rect(2, py0 + ph + 54, 3, 62, WARN))
    b.append(wrap(14, py0 + ph + 76,
                  'Ninguna posición del mapa es un dato: son hipótesis '
                  'construidas con las fuentes seed. Un candidato puede moverse '
                  'de cuadrante al primer hallazgo de campo.', 't-small', 108))
    b.append(txt(2, H - 6, 'Esquema del autor.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Mapa de posicionamiento de los candidatos',
               'Dispersión de los siete candidatos según madurez comercial '
               'hipotética y reutilización de la plataforma existente.')


# =========================================================================
# F9 - Ecuacion de valor para el cliente
# =========================================================================
def fig_valor():
    W, H = 720, 250
    b, _ = _head('Cómo se construye el valor para el cliente',
                 'La venta no es el robot: es la información de condición '
                    'confiable y el costo de mantenimiento que se evita.')
    comps = [
        ('+', 'Costo convencional\nevitado', S3),
        ('+', 'Outage\nevitado', S3),
        ('+', 'Riesgo\nevitado', S3),
        ('+', 'Cobertura\nadicional', S3),
        ('−', 'Costo de\nrobotización', S2),
    ]
    bw, gap, y0, bh = 108, 14, 78, 76
    for i, (sign, lab, color) in enumerate(comps):
        x = 2 + i * (bw + gap)
        b.append(rect(x, y0, bw, bh, SURF, rx=5,
                      extra='stroke="%s" stroke-width="1.4"' % color))
        b.append(txt(x + 12, y0 + 24, sign, 't-title'))
        for k, ln in enumerate(lab.split('\n')):
            b.append(txt(x + 12, y0 + 44 + k * 14, ln, 't-labb'))
        if i < len(comps) - 1:
            b.append(txt(x + bw + gap / 2, y0 + bh / 2 + 5,
                         '+' if comps[i + 1][0] == '+' else '−', 't-sub',
                         'middle'))
    yr = y0 + bh + 22
    b.append(rect(2, yr, W - 4, 52, '#f2f6fa', rx=5))
    b.append(rect(2, yr, 3, 52, NAV))
    b.append(txt(14, yr + 22, '=  Valor creado por inspección', 't-title'))
    b.append(txt(14, yr + 42, 'Cada componente se documenta por separado y con '
                              'su fuente. La seguridad no recibe un valor '
                              'monetario arbitrario.', 't-small'))
    b.append(txt(2, H - 8, 'Esquema del autor.', 't-note'))
    return svg(W, H, '\n'.join(b), 'Ecuación de valor para el cliente',
               'Cuatro componentes de valor menos el costo de robotización '
               'igual al valor creado.')


# =========================================================================
# Esquemas de activos
# =========================================================================
def _head(title, sub):
    """Encabezado con subtitulo envuelto. Devuelve (bloques, y_siguiente)."""
    out = [txt(2, 18, title, 't-title')]
    out.append(wrap(2, 36, sub, 't-sub', 104, 15))
    lineas = 1 + max(0, (len(sub) - 1) // 104)
    return out, 36 + lineas * 15


def leader(xt, yt, xp, yp, text, anchor='middle', cls='t-small'):
    """Etiqueta con linea guia fina hasta el punto que nombra."""
    return [
        '<path d="M%.1f %.1f L%.1f %.1f" class="st-hair"/>' % (xt, yt, xp, yp),
        '<circle cx="%.1f" cy="%.1f" r="2" fill="%s"/>' % (xp, yp, MUT),
        txt(xt, yt + (-6 if yt < yp else 12), text, cls, anchor),
    ]


def _legend(items, x, y, cols=2, colw=300):
    out = []
    for i, (color, label) in enumerate(items):
        cx = x + (i % cols) * colw
        cy = y + (i // cols) * 17
        out.append(rect(cx, cy - 8, 9, 9, color, rx=2))
        out.append(txt(cx + 15, cy, label, 't-small'))
    return out


def esq_ipb():
    W, H = 720, 370
    yl, yn, yg, yf = H - 94, H - 60, H - 32, H - 8
    b, _ = _head('Bus isofásico: geometría de acceso',
                 'Ducto continuo de gran diámetro, obstáculos internos '
                 'periódicos y una ventana de acceso por tramo.')
    dx0, dx1, dy0, dy1 = 60, 640, 120, 200
    cy = (dy0 + dy1) / 2
    b.append(rect(dx0, dy0, dx1 - dx0, dy1 - dy0, '#f4f6f8', rx=6,
                  extra='stroke="%s" stroke-width="1.6"' % NAV))
    b.append(rect(dx0 + 12, cy - 9, dx1 - dx0 - 24, 18, '#d9dee5', rx=9,
                  extra='stroke="%s" stroke-width="1"' % MUT))
    for xi in (200, 350, 500):
        b.append(line(xi, dy0 + 4, xi, cy - 9, 'st-hair'))
        b.append(line(xi, cy + 9, xi, dy1 - 4, 'st-hair'))
        b.append('<circle cx="%d" cy="%.1f" r="5" fill="#b9c0c9"/>' % (xi, cy))
    b.append(rect(92, dy0 - 9, 56, 9, SURF,
                  extra='stroke="%s" stroke-width="1.4"' % NAV))
    b.append(rect(262, dy1 - 28, 58, 20, S2, rx=4))
    for wx in (276, 306):
        b.append('<circle cx="%d" cy="%.1f" r="5" fill="#8c4520"/>'
                 % (wx, dy1 - 5))
    b.append('<path d="M320 %.1f l13 -7 v14 Z" fill="%s"/>' % (dy1 - 25, S1))
    b.append('<path d="M262 %.1f C 220 %.1f, 150 %.1f, 120 %.1f" class="st-dash"/>'
             % (dy1 - 20, dy1 - 40, dy0 + 26, dy0 - 9))
    b += leader(120, 90, 120, dy0 - 9, 'ventana de acceso')
    b += leader(330, 90, 330, dy0, 'envolvente de aluminio')
    b += leader(560, 90, 560, cy - 9, 'conductor central')
    b += leader(210, yl, 290, dy1 - 8, 'crawler: cámara, iluminación y tether')
    b += leader(510, yl, 500, dy1 - 4, 'aislador soporte')
    b.append(txt(W / 2, yn,
                 'Entre dos accesos el robot debe superar cada aislador soporte '
                 'sin perder tracción ni control del tether.', 't-small',
                 'middle'))
    b += _legend([(S2, 'Plataforma robótica'),
                  (S1, 'Sensado embarcado'),
                  ('#b9c0c9', 'Obstáculo interno')], 2, yg, 3, 240)
    b.append(txt(W - 2, yf, 'Esquema del autor. No a escala.', 't-note', 'end'))
    return svg(W, H, '\n'.join(b), 'Esquema de acceso al bus isofásico',
               'Corte longitudinal del ducto con conductor central, aisladores '
               'soporte, ventana de acceso y crawler con tether.')


def esq_hrsg():
    W, H = 720, 396
    yl, yn, yg, yf = H - 94, H - 60, H - 32, H - 8
    b, _ = _head('HRSG: acceso a header, soldaduras y tubos',
                 'El interior de los tubos no se alcanza con ensayo no '
                 'destructivo convencional sin acceso destructivo.')
    hx, hy, hw_, hh = 96, 228, 544, 52
    tubo_top = 104
    for i in range(13):
        tx = hx + 38 + i * 39
        b.append(rect(tx, tubo_top, 15, hy - tubo_top, '#e7eaee', rx=3,
                      extra='stroke="%s" stroke-width="1"' % MUT))
        b.append('<path d="M%d %d h21" stroke="%s" stroke-width="2.6" '
                 'fill="none"/>' % (tx - 3, hy - 1, S3))
    b.append(rect(hx, hy, hw_, hh, '#f4f6f8', rx=26,
                  extra='stroke="%s" stroke-width="1.6"' % NAV))
    b.append(rect(hx - 30, hy + 6, 20, hh - 12, SURF, rx=3,
                  extra='stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"'
                        % MUT))
    b.append(rect(hx + 24, hy + 13, 58, 26, S2, rx=4))
    tubo_x = hx + 38 + 3 * 39 + 7
    b.append('<path d="M%d %.1f C %d %.1f, %d %.1f, %d %.1f" fill="none" '
             'stroke="%s" stroke-width="2.4"/>'
             % (hx + 82, hy + 26, tubo_x - 40, hy + 26, tubo_x, hy + 4,
                tubo_x, 150, S1))
    b.append('<circle cx="%d" cy="%d" r="5" fill="%s" stroke="%s" '
             'stroke-width="2"/>' % (tubo_x, 150, S1, SURF))
    b += leader(140, 88, 128, tubo_top, 'tubos')
    b += leader(430, 132, tubo_x + 8, 150,
                'sonda de corrientes inducidas + video', 'start')
    b += leader(560, 190, 545, hy - 3, 'soldadura tubo-header')
    b += leader(56, 190, hx - 20, hy + hh / 2, 'end cap retirado', 'start')
    b += leader(200, yl, hx + 53, hy + 39, 'crawler dentro del header')
    b.append(txt(W / 2, yn,
                 'La cobertura real depende del diámetro de acceso, del tipo de '
                 'header y del alcance de la sonda dentro de cada tubo.',
                 't-small', 'middle'))
    b += _legend([(S2, 'Plataforma robótica'),
                  (S3, 'Zona de falla'),
                  (S1, 'Sonda dentro del tubo')], 2, yg, 3, 240)
    b.append(txt(W - 2, yf, 'Esquema del autor. No a escala.', 't-note', 'end'))
    return svg(W, H, '\n'.join(b), 'Esquema de acceso a header y tubos de HRSG',
               'Header con tubos y soldaduras, end cap retirado, crawler '
               'interno y sonda empujada dentro de un tubo.')


def esq_vault():
    W, H = 720, 396
    yl, yn, yg, yf = H - 94, H - 60, H - 32, H - 8
    b, _ = _head('Vault subterráneo de transmisión',
                 'Espacio confinado, cables energizados y un único acceso por '
                 'boca de registro.')
    b.append(rect(2, 112, W - 4, 176, '#f4f1ec'))
    b.append(rect(2, 100, 296, 12, '#dfe2e6'))
    b.append(rect(362, 100, W - 366, 12, '#dfe2e6'))
    b.append(rect(238, 88, 56, 8, '#b9c0c9', rx=2))
    vx, vy, vw, vh = 150, 150, 450, 130
    b.append(rect(vx, vy, vw, vh, SURF,
                  extra='stroke="%s" stroke-width="2"' % NAV))
    for yy in (vy + 40, vy + 70, vy + 100):
        b.append('<path d="M%d %d H%d" fill="none" stroke="#c9ced6" '
                 'stroke-width="7" stroke-linecap="round"/>'
                 % (vx + 12, yy, vx + vw - 12))
        b.append(rect(vx + 232, yy - 11, 76, 22, '#dfe4ea', rx=4,
                      extra='stroke="%s" stroke-width="1"' % MUT))
    b.append(rect(404, 62, 100, 28, S2, rx=4))
    b.append('<path d="M330 100 V172" class="st-dash"/>')
    b.append(rect(306, 172, 48, 22, S2, rx=4))
    b += leader(196, 84, 300, 102, 'boca de registro', 'end')
    b += leader(620, 128, 504, 78, 'unidad de superficie y carrete', 'end')
    b += leader(70, 150, vx, vy + 14, 'vault de hormigón', 'start')
    b += leader(660, 214, vx + vw - 40, vy + 40, 'cables energizados', 'end')
    b += leader(300, yl, 330, 194, 'plataforma desplegable')
    b += leader(520, yl, vx + 270, vy + 100, 'empalmes')
    b.append(txt(W / 2, yn,
                 'El acceso humano exige permiso de espacio confinado, control '
                 'de gases y, en muchos casos, salida de servicio del circuito.',
                 't-small', 'middle'))
    b += _legend([(S2, 'Plataforma robótica'),
                  ('#c9ced6', 'Cable energizado'),
                  ('#dfe4ea', 'Empalme')], 2, yg, 3, 240)
    b.append(txt(W - 2, yf, 'Esquema del autor. No a escala.', 't-note', 'end'))
    return svg(W, H, '\n'.join(b), 'Esquema de vault subterráneo',
               'Vault con cables energizados y empalmes inspeccionado desde una '
               'unidad de superficie a través de la boca de registro.')


def esq_piping():
    W, H = 720, 380
    yl, yn, yg, yf = H - 94, H - 60, H - 32, H - 8
    b, _ = _head('Piping enterrado: inspección sin excavación',
                 'Un único punto de acceso debe cubrir codos, derivaciones y '
                 'cambios de plano a lo largo de la traza.')
    b.append(rect(2, 104, W - 4, 12, '#dfe2e6'))
    b.append(rect(2, 116, W - 4, 160, '#f4f1ec'))
    path = ('M70 158 H250 a28 28 0 0 1 28 28 V212 H420 a28 28 0 0 0 28 -28 '
            'V158 H656')
    b.append('<path d="%s" fill="none" stroke="#d3d8de" stroke-width="20" '
             'stroke-linecap="round" stroke-linejoin="round"/>' % path)
    b.append('<path d="M540 158 v-28" stroke="#d3d8de" stroke-width="14" '
             'stroke-linecap="round" fill="none"/>')
    b.append(rect(44, 128, 32, 32, SURF, rx=3,
                  extra='stroke="%s" stroke-width="1.4"' % NAV))
    b.append(rect(150, 149, 54, 18, S2, rx=4))
    b.append('<path d="M120 158 H150" class="st-dash"/>')
    b += leader(60, 92, 60, 128, 'acceso único')
    b += leader(566, 92, 540, 132, 'derivación (tee)')
    b += leader(178, yl, 178, 167, 'crawler con NDE embarcado')
    b += leader(316, yl, 288, 196, 'codo 1D')
    b += leader(452, yl, 448, 190, 'codo de retorno')
    b.append(txt(W / 2, yn,
                 'El valor está en evitar la excavación; el riesgo está en el '
                 'atascamiento. La recuperación es parte del producto.',
                 't-small', 'middle'))
    b += _legend([(S2, 'Plataforma robótica'),
                  ('#d3d8de', 'Tubería enterrada revestida')], 2, yg, 2, 300)
    b.append(txt(W - 2, yf, 'Esquema del autor. No a escala.', 't-note', 'end'))
    return svg(W, H, '\n'.join(b), 'Esquema de inspección de piping enterrado',
               'Tubería enterrada con codos y una derivación, recorrida por un '
               'crawler desde un acceso único.')


def esq_cask():
    W, H = 720, 396
    yl, yn, yg, yf = H - 94, H - 60, H - 32, H - 8
    b, _ = _head('Contenedor de combustible gastado en seco',
                 'La inspección ocurre en un espacio anular estrecho, con dosis '
                 'y sin mover el canister.')
    cx, cy, cw, ch = 286, 96, 180, 194
    b.append(rect(cx, cy, cw, ch, '#f4f6f8', rx=6,
                  extra='stroke="%s" stroke-width="1.8"' % NAV))
    b.append(rect(cx + 30, cy + 14, cw - 60, ch - 28, '#e7eaee', rx=4,
                  extra='stroke="%s" stroke-width="1"' % MUT))
    b.append(txt(cx + cw / 2, cy + ch / 2 + 4, 'canister', 't-small', 'middle'))
    b.append(rect(cx + 12, cy + 14, 18, ch - 28, '#dbe9fb',
                  extra='stroke="%s" stroke-width="0.8"' % S1))
    for yy in (cy + 24, cy + ch - 36):
        b.append(rect(cx - 16, yy, 16, 12, '#d9dee5',
                      extra='stroke="%s" stroke-width="1"' % MUT))
        b.append(rect(cx + cw, yy, 16, 12, '#d9dee5',
                      extra='stroke="%s" stroke-width="1"' % MUT))
    b.append(rect(cx + 16, cy + 106, 10, 26, S2, rx=3))
    b += leader(250, 140, cx + 21, cy + 44,
                'espacio anular de pocos centímetros', 'end')
    b += leader(250, 250, cx + 16, cy + 119, 'robot trepador', 'end')
    b += leader(500, 140, cx + cw + 16, cy + 30,
                'respiraderos de entrada y salida', 'start')
    b += leader(500, 250, cx + cw, cy + 150, 'sobre-contenedor de hormigón',
                'start')
    b.append(txt(W / 2, yn,
                 'La alternativa convencional exige mover el canister o una '
                 'maniobra de izaje pesado: ahí está el costo evitado.',
                 't-small', 'middle'))
    b += _legend([(S2, 'Plataforma robótica'),
                  ('#dbe9fb', 'Espacio anular de inspección'),
                  ('#e7eaee', 'Canister')], 2, yg, 3, 240)
    b.append(txt(W - 2, yf, 'Esquema del autor. No a escala.', 't-note', 'end'))
    return svg(W, H, '\n'.join(b), 'Esquema de contenedor de almacenamiento en '
               'seco', 'Sobre-contenedor, canister, espacio anular, '
               'respiraderos y robot trepador.')


def esq_penstock():
    W, H = 720, 370
    yl, yn, yg, yf = H - 94, H - 60, H - 32, H - 8
    b, _ = _head('Penstock y túnel hidroeléctrico',
                 'Kilómetros de conducto lleno, sin referencia satelital y con '
                 'un único punto de lanzamiento.')
    b.append('<path d="M112 140 H300 L620 244 V282 L300 178 H112 Z" '
             'fill="#eef4fb" stroke="%s" stroke-width="1.6"/>' % NAV)
    b.append(rect(42, 112, 68, 28, S2, rx=4))
    b.append('<path d="M110 156 C 200 154, 300 168, 424 202" class="st-dash"/>')
    b.append('<ellipse cx="436" cy="205" rx="17" ry="10" fill="%s"/>' % S2)
    b.append('<path d="M452 205 L536 183 L536 229 Z" fill="%s" opacity="0.18"/>'
             % S1)
    b += leader(76, 96, 76, 112, 'carrete, consola y energía')
    b += leader(330, 112, 300, 140, 'conducto forzado lleno de agua')
    b += leader(330, yl, 436, 215, 'vehículo remoto con tether')
    b += leader(640, 250, 520, 200, 'barrido sonar', 'end')
    b.append(txt(W / 2, yn,
                 'El alcance útil lo fija el tether, el arrastre del flujo y la '
                 'garantía de recuperación, no la cámara.', 't-small', 'middle'))
    b += _legend([(S2, 'Plataforma robótica'),
                  (S1, 'Visual y sonar'),
                  (S3, 'Espesor por ultrasonido')], 2, yg, 3, 240)
    b.append(txt(W - 2, yf, 'Esquema del autor. No a escala.', 't-note', 'end'))
    return svg(W, H, '\n'.join(b), 'Esquema de inspección de penstock',
               'Conducto forzado inclinado con vehículo remoto, tether y cono '
               'de sonar.')


def esq_vine():
    W, H = 720, 360
    yl, yn, yf = H - 94, H - 56, H - 8
    b, _ = _head('Robot everting (vine) en equipos de planta',
                 'Avanza por eversión: el cuerpo no roza la pared, por eso entra '
                 'donde el crawler no pasa.')
    b.append(rect(176, 96, 464, 152, '#f9fafb', rx=6,
                  extra='stroke="%s" stroke-width="1.2"' % MUT))
    duct = ('M192 174 H268 a24 24 0 0 0 24 -24 V132 a24 24 0 0 1 24 -24 H424 '
            'a24 24 0 0 1 24 24 V200 a24 24 0 0 0 24 24 H622')
    b.append('<path d="%s" fill="none" stroke="#dfe4ea" stroke-width="24" '
             'stroke-linecap="round" stroke-linejoin="round"/>' % duct)
    grow = 'M192 174 H268 a24 24 0 0 0 24 -24 V132 a24 24 0 0 1 24 -24 H398'
    b.append('<path d="%s" fill="none" stroke="%s" stroke-width="9" '
             'stroke-linecap="round" stroke-linejoin="round"/>' % (grow, S2))
    b.append('<circle cx="398" cy="108" r="6.5" fill="%s" stroke="%s" '
             'stroke-width="2"/>' % (S1, SURF))
    b.append(rect(72, 158, 100, 32, S2, rx=4))
    b += leader(398, 74, 398, 101, 'punta con cámara y sensor')
    b += leader(122, yl, 122, 190, 'base: presión y carrete')
    b += leader(600, yl, 566, 224, 'tramo que el crawler no alcanza', 'end')
    b.append(txt(W / 2, yn,
                 'Es una tecnología, no un mercado: sólo se justifica sobre un '
                 'activo donde además el desmontaje es caro.', 't-small',
                 'middle'))
    b.append(txt(W - 2, yf, 'Esquema del autor. No a escala.', 't-note', 'end'))
    return svg(W, H, '\n'.join(b), 'Esquema de robot everting',
               'Cuerpo everting avanzando por un conducto ramificado desde una '
               'base con carrete.')


FIGURAS = [
    ('fig-evidencia', fig_evidencia),
    ('fig-madurez', fig_madurez),
    ('fig-proceso', fig_proceso),
    ('fig-cronologia', fig_cronologia),
    ('fig-pesos', fig_pesos),
    ('fig-ipb-economia', fig_ipb_economia),
    ('fig-piping-economia', fig_piping_economia),
    ('fig-mapa-candidatos', fig_mapa_candidatos),
    ('fig-valor', fig_valor),
    ('esq-ipb', esq_ipb),
    ('esq-hrsg', esq_hrsg),
    ('esq-vault', esq_vault),
    ('esq-piping', esq_piping),
    ('esq-cask', esq_cask),
    ('esq-penstock', esq_penstock),
    ('esq-vine', esq_vine),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    pdf = '--pdf' in sys.argv
    for name, fn in FIGURAS:
        content = fn()
        path = os.path.join(OUT, name + '.svg')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print('%-22s %6d bytes' % (name + '.svg', len(content)))
    if pdf:
        import cairosvg
        for name, _ in FIGURAS:
            cairosvg.svg2pdf(url=os.path.join(OUT, name + '.svg'),
                             write_to=os.path.join(OUT, name + '.pdf'))
        print('PDF generados en %s' % OUT)


if __name__ == '__main__':
    main()
