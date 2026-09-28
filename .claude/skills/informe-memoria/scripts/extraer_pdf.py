#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae el texto y las imágenes de un PDF (informe de partida).

Uso: python3 extraer_pdf.py informe.pdf carpeta_salida
Escribe texto.txt y p<página>_<n>.<ext>; imprime tamaño de cada imagen para
distinguir fotos (grandes, verticales) de gráficos.
"""
import pathlib
import sys

import pymupdf


def main():
    pdf, salida = sys.argv[1], pathlib.Path(sys.argv[2])
    salida.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf)
    texto = []
    for i, pag in enumerate(doc, 1):
        texto.append(f'===== página {i}\n{pag.get_text()}')
        for j, img in enumerate(pag.get_images(full=True)):
            x = doc.extract_image(img[0])
            nombre = salida / f'p{i}_{j}.{x["ext"]}'
            nombre.write_bytes(x['image'])
            print(f'{nombre}  {x["width"]}x{x["height"]}  {len(x["image"]) // 1024} kB')
    (salida / 'texto.txt').write_text('\n'.join(texto), encoding='utf-8')
    print(salida / 'texto.txt', f'({doc.page_count} páginas)')


if __name__ == '__main__':
    main()
