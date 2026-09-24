#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nota 02489-00-MC002 - Efecto del grado del imán con entrehierro mínimo de
1,5 mm (conjunto de dos imanes NdFeB D20x4 avellanados).

Uso (desde esta carpeta):
    python3 calculo.py        # escribe resultados.json

Referencia: curva FEMM ajustada del conjunto actual (Br efectivo 1,051 T, se
comporta como N35), tabla 1 del informe 02489-00-ZIT200. Entre puntos se
interpola en logaritmo de la fuerza.

Otros grados: F_g(x) = (Br_g / Br_N35)^2 * F_N35(x + s), con remanencias
nominales de catálogo y s = espesor del separador no magnético.

Los alcances a 2 N se toman de las curvas FEMM de la figura (el cálculo por
interpolación solo llega hasta 10,23 mm); aquí se verifica que con separador
el alcance es el de sin separador menos s.
"""
import json

import numpy as np
from scipy.optimize import brentq

# Tabla 1 de 02489-00-ZIT200: entrehierro [mm] y fuerza FEMM ajustada [N]
X = np.array([0.15, 0.21, 0.28, 0.34, 0.41, 0.47, 0.80, 1.12, 1.45, 1.77, 2.10,
              2.75, 3.40, 4.05, 4.70, 5.35, 6.00, 6.65, 7.30, 7.95, 8.60, 9.25,
              9.90, 10.23])
F = np.array([61.06, 57.50, 54.42, 51.71, 49.18, 46.89, 37.78, 31.27, 26.28,
              22.43, 19.33, 14.78, 11.63, 9.34, 7.62, 6.29, 5.23, 4.38, 3.70,
              3.14, 2.68, 2.30, 1.98, 1.84])

X_MIN = 1.5                      # entrehierro mínimo impuesto por el montaje [mm]
BR = {'N35': 1.19, 'N42': 1.30, 'N52': 1.45}   # remanencia nominal [T]
# Alcance a 2 N de las curvas FEMM (figura de la nota) [mm]
X_2N = {'N35': 9.85, 'N42': 10.65, 'N42+s': 10.28, 'N52': 11.69, 'N52+s': 10.81}


def f35(x):
    return float(np.exp(np.interp(x, X, np.log(F))))


def main():
    f_max = f35(X_MIN)
    res = {'F_N35_1p5_N': round(f_max, 2), 'grados': {}}
    for g in ('N42', 'N52'):
        k = (BR[g] / BR['N35']) ** 2
        s = brentq(lambda d: k * f35(X_MIN + d) - f_max, 0.0, 3.0)
        res['grados'][g] = {
            'Br_T': BR[g],
            'factor_fuerza': round(k, 3),
            'F_1p5_sin_separador_N': round(k * f_max, 1),
            'aumento_F_max_pct': round(100 * (k - 1), 0),
            'separador_mm': round(s, 2),
            'x2N_sin_separador_mm': X_2N[g],
            'x2N_con_separador_mm': X_2N[g + '+s'],
            'x2N_sin_menos_s_mm': round(X_2N[g] - s, 2),
            'ganancia_sin_separador_mm': round(X_2N[g] - X_2N['N35'], 2),
            'ganancia_con_separador_mm': round(X_2N[g + '+s'] - X_2N['N35'], 2),
        }
    with open('resultados.json', 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
