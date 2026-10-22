"""Palpador de una tira: C plegada + lengüeta. Geometría final, verificación y planos.

Dos piezas y dos tornillos: la chapa y el flex con el ADXL1004 (sin amortiguador
ni rigidizador). La resonancia del filtro queda sin amortiguar (ζ ≈ 0,002 del
acero) y se saca de la medición con la banda de C1, 1,5–5 kHz, por encima de f0.

La chapa es una sola pieza de 17-7PH de 0,15 mm, fotograbada y plegada:

  * brazo superior (3 mm de ancho) y brazo inferior (dos tiras de 1,5 mm a
    los costados) forman un paralelogramo: el carro baja derecho y la flecha
    da la precarga;
  * alma vertical (6 mm de ancho): por fuera, pegado, el extremo rígido del
    flex con el ADXL1004;
  * el centro del alma sigue 1,3 mm más abajo que las tiras laterales y se
    pliega hacia adelante: es la lengüeta (2,4 mm de ancho), el filtro, con un
    hoyuelo esférico acuñado en la punta que apoya en la cuña.

Coordenadas en estado cargado: x a lo largo de la ranura, y radial (y = 0 en
la cara de la cuña), z a lo ancho. Medidas en mm.

Uso:  python -m cuna3d.palpador_tira
"""

from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.distancia import NIVELES  # noqa: E402
from cuna3d.palpador_lamina import Lamina, evaluar  # noqa: E402
from cuna3d.sensor import OUT  # noqa: E402

mm = 1e-3
T = 0.15            # espesor de la chapa
H_HOY = 0.25        # altura del hoyuelo (Ø de base 1,94 mm con R 2)
R_HOY = 2.0         # radio del hoyuelo
Y_T = H_HOY + T / 2  # línea media de la lengüeta (el vértice del hoyuelo en y = 0)
Y_INF, Y_SUP = 1.6, 6.5
L_BRAZO, L_LENG = 13.0, 2.3
B_SUP, B_TIRA, B_ALMA, RANURA = 3.0, 1.5, 6.0, 0.3
B_CENTRO = B_ALMA - 2 * B_TIRA - 2 * RANURA      # parte central del alma bajo el brazo inferior (2,4)
B_LENG = B_CENTRO                                 # la lengüeta sigue con el mismo ancho: tira continua
PCB = (5.0, 6.0, 0.4)          # extremo rígido del flex (refuerzo de FR4 del propio flex): y, z, x
CHIP = 1.8                     # espesor del ADXL1004 (LFCSP 5 × 5 mm)
M_SENSOR = 0.200e-3 + 1850 * PCB[0] * PCB[1] * PCB[2] * 1e-9 + 10e-6 + 5e-6   # ADXL + refuerzo + flex + 0402 y adhesivo
E_SENSOR = 1.2                 # centro de masa del sensor, desde la línea media del alma hacia afuera
OREJA = 2.5
BANDA_C1 = (1500, 5000)        # por encima de f0: la resonancia sin amortiguar no entra en C1
ZETA = 0.002                   # acero + adhesivo, sin amortiguador


def lamina(zeta=ZETA) -> Lamina:
    P = [(0, Y_SUP * mm), (L_BRAZO * mm, Y_SUP * mm), (L_BRAZO * mm, Y_INF * mm), (0, Y_INF * mm),
         (L_BRAZO * mm, Y_T * mm), ((L_BRAZO + L_LENG) * mm, Y_T * mm)]
    S = [(0, 1, B_SUP * mm), (1, 2, B_ALMA * mm), (2, 3, 2 * B_TIRA * mm), (2, 4, B_CENTRO * mm), (4, 5, B_LENG * mm)]
    m = M_SENSOR
    return Lamina(nombre="tira: C plegada + lengüeta", t=T * mm, P=P, S=S, fijos=[0, 3], i_apex=5, seg_sensor=1,
                  y_sensor=3.9 * mm, m_sensor=m, e_sensor=E_SENSOR * mm, J_sensor=m * (5e-3 ** 2 + CHIP ** 2 * 1e-6) / 12,
                  zeta=zeta, R_hoyuelo=R_HOY * mm)


def _eval(arg):
    z, F0, tg = arg
    lam = replace(lamina(z), tangencial=tg)
    e = evaluar(lam, F0, BANDA_C1)
    c1 = {n: [r["C1"] for r in e["filas"] if r["estado"] == n] for n in NIVELES}
    return {"zeta": z, "F0": F0, "tg": tg, **{k: v for k, v in e.items() if k != "filas"},
            "Fc_min_sin_muy_floja": min(r["Fc_min"] for r in e["filas"] if r["estado"] != "muy_floja_juego"),
            "C1_rango": {n: [min(v), max(v)] for n, v in c1.items()}}


def umbrales(ev, z, F0):
    """Umbrales de C1 que valen con la punta libre y trabada: punto medio de los huecos de la unión."""
    out = []
    for a, b in zip(NIVELES[1:], NIVELES[2:]):
        hi = max(e["C1_rango"][a][1] for e in ev if (e["zeta"], e["F0"]) == (z, F0))
        lo = min(e["C1_rango"][b][0] for e in ev if (e["zeta"], e["F0"]) == (z, F0))
        out.append({"entre": f"{a}/{b}", "umbral": (hi + lo) / 2, "hueco": lo - hi})
    return out


def verificar():
    lam = lamina()
    st = lam.estatica(2.0)
    f, _, part = lam.modos(2.0, 8)
    fs = np.linspace(500, 3000, 2501)
    H = lam.frf(2.0, fs)
    res = {"estatica": st, "modos_Hz": f.tolist(), "participacion": part.tolist(), "f0_Hz": float(fs[np.argmax(H)]),
           "pico": float(H.max()), "T_18k": float(lam.frf(2.0, np.array([18e3]))[0]),
           "T_43k": float(lam.frf(2.0, np.array([43e3]))[0]), "masa_carro_g": M_SENSOR * 1e3, "banda_C1_Hz": BANDA_C1}
    print("estática:", st)
    print("modos:", np.round(f), " f0:", res["f0_Hz"], " pico:", round(res["pico"], 1))
    casos = [(z, F0, tg) for z in (0.002, 0.005) for F0 in (1.6, 2.0, 2.4) for tg in ("libre", "adherido")]
    with Pool(4) as pool:
        ev = pool.map(_eval, casos)
    for e in ev:
        print(f"ζ={e['zeta']:.3f} F0={e['F0']:.1f} [{e['tg']:8s}] despega={len(e['despega'])} ({sorted(set(x.split('·')[0] for x in e['despega']))})  "
              f"Fc_min (sin la muy floja)={e['Fc_min_sin_muy_floja']:.2f} N  satura={e['satura']}  "
              f"gaps C1={np.round(e['gaps_C1'], 2)}  gap C2={e['gap_C2_Hz']:.0f} Hz", flush=True)
    res["verificacion"] = ev
    res["umbrales_C1"] = {f"{z}_{F0}": umbrales(ev, z, F0) for z in (0.002, 0.005) for F0 in (1.6, 2.0, 2.4)}
    print("umbrales (ζ 0,002, 2 N):", res["umbrales_C1"]["0.002_2.0"])
    with open(OUT / "palpador_tira.json", "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    return res


if __name__ == "__main__":
    verificar()
