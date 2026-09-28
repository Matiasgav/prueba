#!/usr/bin/env python3
"""Extrae las curvas vectoriales del datasheet y la nota de aplicación del VCNL36829UM.

Uso:
    pip install pymupdf
    python3 extraer_curvas.py vcnl36829um.pdf designing_vcnl36829um_into_an_application.pdf

PDFs de origen (Vishay):
    https://www.vishay.com/docs/80580/vcnl36829um.pdf                               (Rev. 1.1, 01-Jul-2026)
    https://www.vishay.com/docs/80581/designing_vcnl36829um_into_an_application.pdf (rev. 15-May-2025)

Imprime las curvas Fig. 10 / Fig. 11 (cuentas frente a distancia) y Fig. 38 (relación frente a temperatura).
La calibración de ejes se toma de la posición de los rótulos de marca en la propia página.
Si Vishay publica otra revisión, verificar que las coordenadas de ejes sigan valiendo.
"""
import json
import sys

import pymupdf

COLORES = {0.08: "8mA", 0.94: "12mA", 0.29: "hi"}  # azul, naranja, verde (18 mA en Fig.10, rotulada 20 mA en Fig.11)


def puntos(dibujo):
    pts = []
    for it in dibujo["items"]:
        if it[0] == "l":
            pts += [it[1], it[2]]
        elif it[0] == "c":
            pts += [it[1], it[4]]
    return [(p.x, p.y) for p in pts]


def curvas_distancia(pdf):
    pagina = pymupdf.open(pdf)[7]  # página 8 del datasheet
    salida = {}
    for d in pagina.get_drawings():
        c, w = d.get("color"), round(d.get("width") or 0, 2)
        if not c or w not in (1.48, 1.5):
            continue
        fig = "F10" if d["rect"].x0 < 300 else "F11"
        x0, decada = (98.29, 44.72) if fig == "F10" else (364.75, 42.45)
        serie = {}
        for x, y in puntos(d):
            dist = 10 ** (-1 + (x - x0) / decada)
            cuentas = 10 ** ((243.25 - y) / 26.65) * 0.9836  # 0,9836: ajusta las mesetas a 16 383 / 65 535
            serie[round(dist, 3)] = round(cuentas, 1)
        salida[f"{fig}_{COLORES[round(c[0], 2)]}"] = sorted((k, v) for k, v in serie.items() if k >= 0.9)
    return salida


def curva_temperatura(pdf):
    pagina = pymupdf.open(pdf)[31]
    for d in pagina.get_drawings():
        c = d.get("color")
        if c and c[2] > 0.5 and c[0] < 0.3 and len(d["items"]) > 5:
            return sorted({(round(-40 + (x - 231.52) / 23.617 * 20, 1), round(1.0 - (y - 253.1) / 166.6, 3))
                           for x, y in puntos(d)})
    return []


if __name__ == "__main__":
    print(json.dumps({"distancia": curvas_distancia(sys.argv[1]),
                      "temperatura": curva_temperatura(sys.argv[2])}, indent=1))
