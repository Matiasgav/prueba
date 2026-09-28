#!/usr/bin/env python3
"""Genera las capturas del catálogo KG usadas en el informe.

Renderiza las páginas oficiales descargadas en fuentes/, resalta las filas
del producto m0,5 × 20 dientes y recorta la zona relevante.
"""
import os
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'fuentes')
OUT = os.path.join(ROOT, 'capturas')
DPI = 160

# (archivo, índice de página, textos a resaltar, recorte en fracción de página
#  (x0, y0, x1, y1), nombre de salida)
CAPTURAS = [
    ('KG4001WEB-7.pdf', 0, [], (0, 0.28, 1, 0.56), 'kg_codigo_producto'),
    ('KG4001WEB-7.pdf', 27, ['M50S 20', 'M50S 25', 'JGMA'],
     (0, 0.2, 1, 0.41), 'kg_s45c_datos'),
    ('KG4001WEB-7.pdf', 28, ['M50S 20', 'M50S 25'], (0, 0.29, 1, 0.47), 'kg_s45c_potencia'),
    ('KG4001WEB-7.pdf', 39, ['M50B 20'], (0, 0, 1, 0.47), 'kg_laton_datos'),
    ('KG5001JP_reference.pdf', 19, [], (0, 0.04, 1, 0.35), 'kg_condiciones_conicos'),
    ('KG5001JP_reference.pdf', 21, [], (0, 0.76, 1, 0.94), 'kg_conversion_potencia'),
    ('TechnicalData_KGSTOCKGEARS.pdf', 136, ['Outer transverse module'],
     (0, 0.05, 0.5, 0.56), 'kg_jgma403_alcance'),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for fname, pno, marks, crop, name in CAPTURAS:
        doc = pymupdf.open(os.path.join(SRC, fname))
        page = doc[pno]
        for txt in marks:
            hits = page.search_for(txt)
            if not hits:
                continue
            # Un solo recuadro por producto: abarca todas sus filas (las
            # tablas de potencia combinan las dos variantes en una celda).
            r = hits[0]
            for h in hits[1:]:
                r = r | h
            box = pymupdf.Rect(r.x0 - 3, r.y0 - 3, r.x1 + 3, r.y1 + 3)
            if txt.startswith('M50'):
                # Código a la izquierda: la fila sigue hacia la derecha;
                # código a la derecha: la fila viene desde la izquierda.
                if r.x0 < page.rect.width * 0.3:
                    box.x1 = page.rect.width * 0.94
                else:
                    box.x0 = page.rect.width * 0.08
            a = page.add_rect_annot(box)
            a.set_colors(stroke=(0.85, 0.1, 0.1))
            a.set_border(width=1.6)
            a.update()
        W, H = page.rect.width, page.rect.height
        clip = pymupdf.Rect(crop[0] * W, crop[1] * H, crop[2] * W, crop[3] * H)
        pix = page.get_pixmap(dpi=DPI, clip=clip, annots=True)
        pix.save(os.path.join(OUT, name + '.png'))
        print(name, pix.width, pix.height)


if __name__ == '__main__':
    main()
