"""Palpador de una tira: C plegada + lengüeta. Geometría final, verificación y planos.

Una sola pieza de 17-7PH de 0,15 mm, fotograbada y plegada:

  * brazo superior (3 mm de ancho) y brazo inferior (dos tiras de 1,5 mm a
    los costados) forman un paralelogramo: el carro baja derecho y la flecha
    da la precarga;
  * alma vertical (6 mm de ancho): por fuera el flex con el ADXL1004, por
    dentro la aleta de cobre del amortiguador;
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
ALETA = (3.0, 4.0, 0.4)        # cobre: x, y, espesor (z)
M_SENSOR = 0.269e-3            # ADXL1004 + FR4 + flex + componentes
M_ALETA = 8960 * ALETA[0] * ALETA[1] * ALETA[2] * 1e-9
OREJA = 2.5


def lamina(zeta=0.002, F0=2.0) -> Lamina:
    P = [(0, Y_SUP * mm), (L_BRAZO * mm, Y_SUP * mm), (L_BRAZO * mm, Y_INF * mm), (0, Y_INF * mm),
         (L_BRAZO * mm, Y_T * mm), ((L_BRAZO + L_LENG) * mm, Y_T * mm)]
    S = [(0, 1, B_SUP * mm), (1, 2, B_ALMA * mm), (2, 3, 2 * B_TIRA * mm), (2, 4, B_CENTRO * mm), (4, 5, B_LENG * mm)]
    m = M_SENSOR + M_ALETA
    return Lamina(nombre="tira: C plegada + lengüeta", t=T * mm, P=P, S=S, fijos=[0, 3], i_apex=5, seg_sensor=1,
                  y_sensor=3.9 * mm, m_sensor=m, e_sensor=+1.4 * mm, J_sensor=m * (5e-3 ** 2 + 2.4e-3 ** 2) / 12,
                  zeta=zeta, R_hoyuelo=R_HOY * mm)


def _eval(arg):
    z, F0, tg = arg
    lam = replace(lamina(z), tangencial=tg)
    e = evaluar(lam, F0)
    return {"zeta": z, "F0": F0, "tg": tg, **{k: v for k, v in e.items() if k != "filas"},
            "Fc_min_sin_muy_floja": min(r["Fc_min"] for r in e["filas"] if r["estado"] != "muy_floja_juego")}


def verificar():
    lam = lamina()
    st = lam.estatica(2.0)
    f, _, part = lam.modos(2.0, 8)
    fs = np.linspace(500, 3000, 2501)
    H = lam.frf(2.0, fs)
    res = {"estatica": st, "modos_Hz": f.tolist(), "participacion": part.tolist(), "f0_Hz": float(fs[np.argmax(H)]),
           "pico": float(H.max()), "T_18k": float(lam.frf(2.0, np.array([18e3]))[0]),
           "T_43k": float(lam.frf(2.0, np.array([43e3]))[0]), "masa_carro_g": (M_SENSOR + M_ALETA) * 1e3}
    print("estática:", st)
    print("modos:", np.round(f), " f0:", res["f0_Hz"], " pico:", round(res["pico"], 1))
    casos = [(z, F0, tg) for z in (0.002, 0.016) for F0 in (1.6, 2.0, 2.4) for tg in ("libre", "adherido")]
    with Pool(4) as pool:
        ev = pool.map(_eval, casos)
    for e in ev:
        print(f"ζ={e['zeta']:.3f} F0={e['F0']:.1f} [{e['tg']:8s}] despega={len(e['despega'])} ({sorted(set(x.split('·')[0] for x in e['despega']))})  "
              f"Fc_min (sin la muy floja)={e['Fc_min_sin_muy_floja']:.2f} N  satura={e['satura']}  "
              f"gaps C1={np.round(e['gaps_C1'], 2)}  gap C2={e['gap_C2_Hz']:.0f} Hz", flush=True)
    res["verificacion"] = ev
    with open(OUT / "palpador_tira.json", "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    return res


if __name__ == "__main__":
    verificar()
