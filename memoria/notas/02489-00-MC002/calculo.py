#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota 02489-00-MC002 - Caracterización de la fuerza de atracción del
conjunto de dos imanes NdFeB D20x4 avellanados.

Uso (desde esta carpeta):
    python3 calculo.py        # escribe resultados.json

1. Relevamiento: convierte las lecturas crudas (hojas, gramos) a entrehierro
   y fuerza, x = x0 + n t y F = m g.
2. Grado: ajusta el factor k = (Br / Br_ref)^2 del modelo FEMM por mínimos
   cuadrados sobre log F (Br_ref = 1,300 T, N42 nominal).
3. Otros grados: con entrehierro mínimo de 1,5 mm, F_g(x) = (Br_g/Br_N35)^2
   F_N35(x + s), con s el separador que conserva la fuerza a 1,5 mm.

La curva FEMM de referencia (N42) son los valores FEMM ajustados de la tabla
de la nota divididos por k = 0,654; se reconstruye aquí porque el modelo FEMM
no está versionado. Entre puntos se interpola en log F. Los alcances a 2 N de
otros grados se toman de las curvas FEMM de la figura de la nota (llegan más
allá de los 10,23 mm medidos).
"""
import json

import numpy as np
from scipy.optimize import brentq

G = 9.80665                 # m/s2
T_HOJA = 0.03250            # mm/hoja (200 hojas = 6,50 mm)
X0 = 0.15                   # entrehierro residual [mm]
BR_REF = 1.300              # Br del modelo FEMM de referencia (N42) [T]

# Lecturas crudas: (hojas, gramos)
CRUDO = [(0, 7000), (2, 6500), (4, 6000), (6, 5600), (8, 5600), (10, 5400),
         (20, 4100), (30, 3140), (40, 2850), (50, 2450), (60, 2000),
         (80, 1500), (100, 1190), (120, 990), (140, 740), (160, 630),
         (180, 520), (200, 480), (220, 345), (240, 295), (260, 245),
         (280, 195), (300, 180), (310, 150)]
# FEMM ajustado (k = 0,654) en los mismos puntos [N]
F_AJ = np.array([61.06, 57.50, 54.42, 51.71, 49.18, 46.89, 37.78, 31.27, 26.28,
                 22.43, 19.33, 14.78, 11.63, 9.34, 7.62, 6.29, 5.23, 4.38, 3.70,
                 3.14, 2.68, 2.30, 1.98, 1.84])
K_NOTA = 0.654

X_MIN = 1.5
BR_CAT = {'N35': 1.19, 'N42': 1.30, 'N52': 1.45}
X_2N_FIG = {'N42': 10.65, 'N42+s': 10.28, 'N52': 11.69, 'N52+s': 10.81}


def main():
    n = np.array([c[0] for c in CRUDO], float)
    m = np.array([c[1] for c in CRUDO], float)
    x = X0 + n * T_HOJA
    f_med = m / 1000 * G
    f_n42 = F_AJ / K_NOTA

    # Ajuste de k sobre log F
    k = float(np.exp(np.mean(np.log(f_med) - np.log(f_n42))))
    br = BR_REF * np.sqrt(k)
    f_fit = k * f_n42
    resid = f_med / f_fit - 1
    desvio = float(np.std(np.log(f_med / f_fit)))

    def f35(q):
        return float(np.exp(np.interp(q, x, np.log(f_fit))))

    caract = {f'{F:g} N': round(brentq(lambda q: f35(q) - F, x[0], x[-1]), 2)
              for F in (20, 10, 5, 2)}
    def f_medida(q):
        return float(np.exp(np.interp(q, x, np.log(f_med))))

    x_mitad = brentq(lambda q: f_medida(q) - f_med[0] / 2, x[0], x[-1])
    x_decima = brentq(lambda q: f_medida(q) - f_med[0] / 10, x[0], x[-1])

    f_max = f35(X_MIN)
    grados = {}
    for g in ('N42', 'N52'):
        kg = (BR_CAT[g] / BR_CAT['N35']) ** 2
        s = brentq(lambda d: kg * f35(X_MIN + d) - f_max, 0.0, 3.0)
        grados[g] = {
            'factor_fuerza': round(kg, 3),
            'F_1p5_sin_separador_N': round(kg * f_max, 1),
            'separador_mm': round(s, 2),
            'x2N_sin_separador_mm (figura)': X_2N_FIG[g],
            'x2N_con_separador_mm (figura)': X_2N_FIG[g + '+s'],
            'x2N_sin_menos_s_mm': round(X_2N_FIG[g] - s, 2),
        }

    res = {
        'relevamiento': {
            'x_mm': [round(v, 2) for v in x],
            'F_medida_N': [round(v, 2) for v in f_med],
            'F_contacto_N': round(f_med[0], 2),
            'F_ultimo_N': round(f_med[-1], 2),
            'x_mitad_de_contacto_mm': round(x_mitad, 2),
            'x_decima_de_contacto_mm': round(x_decima, 2),
            'valores_caracteristicos_mm': caract,
        },
        'grado': {
            'k': round(k, 3),
            'Br_efectivo_T': round(br, 3),
            'desvio_residuos_pct': round(100 * desvio, 1),
            'residuos_pct': [round(100 * r, 1) for r in resid],
        },
        'otros_grados': {'F_N35_1p5_N': round(f_max, 2), 'grados': grados},
    }
    with open('resultados.json', 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    print(json.dumps({kk: vv for kk, vv in res.items()}, indent=1,
                     ensure_ascii=False)[:3000])


if __name__ == '__main__':
    main()
