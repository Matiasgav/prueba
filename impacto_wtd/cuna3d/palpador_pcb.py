"""Palpador con la PCB como carro: dos láminas rectas y la punta de chapa, soldadas a la placa.

Variante del palpador de una tira (cuna3d/palpador_tira.py) sin pliegues en los brazos:

  * la PCB (FR4 de 1,6 mm) va vertical y es el carro. El ADXL1004 va soldado en
    su cara exterior: su eje sensible está en el plano de la placa y queda
    vertical. No hace falta flex con refuerzo;
  * dos láminas rectas de 17-7PH CH900 por nivel (niqueladas y estañadas para
    poder soldarlas), arriba y abajo, forman el paralelogramo entre una PCB fija (con el conector) y la
    PCB del carro. Las cuatro tiras llevan además alimentación, masa, salida y
    sobrerrango: no hay cable que vaya al carro;
  * la punta es una tira del mismo acero soldada a la cara exterior de la PCB:
    baja vertical hasta quedar dentro de la carcasa, sigue en rampa a 35°, y
    termina en la lengüeta horizontal (el filtro) con el hoyuelo, el extremo
    redondeado y la nariz.

Las láminas entran en muescas metalizadas abiertas al borde de la PCB del carro
(y en ranuras de la PCB fija), soldadas y
con epoxi: la soldadura sola fluye con el momento permanente de la precarga.

Coordenadas en estado cargado: x a lo largo de la ranura, y radial (y = 0 en
la cara de la cuña), z a lo ancho. Medidas en mm.

Uso:  python -m cuna3d.palpador_pcb
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
E_CB, RHO_CB, SY_CB = 197e9, 7800.0, 1600.0      # 17-7PH CH900 niquelado y estañado: módulo, densidad, fluencia típica [MPa]
# (con cobre-berilio C17200, que se suelda directo, la punta llega a la fluencia en el tope y los modos bajan a 3,2 kHz)
E_FR4, RHO_FR4 = 20e9, 1850.0
T = 0.15                       # espesor de las láminas y de la punta
L_BRAZO = 13.0                 # luz libre de las láminas, entre placas
B_TIRA, N_TIRAS = 1.5, 2       # dos tiras por nivel (cuatro conductores), a los costados
Z_TIRA = 1.3                   # borde interior de cada tira: entre las dos de abajo pasa el pad de la punta
T_PCB, B_PCB = 1.6, 6.0        # PCB del carro: espesor (x) y ancho (z)
Y_INF, Y_SUP = 2.3, 8.5        # niveles de las láminas: abajo y arriba de la zona del chip
Y_PCB0, Y_PCB1 = 1.9, 8.9      # bordes inferior y superior de la PCB del carro
X_PCB = L_BRAZO + T_PCB / 2    # plano medio de la PCB del carro (las láminas llegan a su cara interior)
X_PUNTA = L_BRAZO + T_PCB + T / 2   # línea media de la tira de la punta, pegada a la cara exterior
H_HOY, R_HOY = 0.25, 2.0
Y_T = H_HOY + T / 2
Y_CODO, ANG_RAMPA = 1.2, 35.0
X_LENG = X_PUNTA + (Y_CODO - Y_T) / math.tan(math.radians(ANG_RAMPA))
L_RAMPA = (Y_CODO - Y_T) / math.sin(math.radians(ANG_RAMPA))
L_LENG = 2.0
PLANO, NARIZ, ANG_NARIZ = 0.6, 0.4, 30.0
B_LENG = 2.4
Y_SOLD = 0.8                   # largo de la tira de la punta soldado sobre la PCB, debajo del chip y entre las láminas
M_SENSOR = 0.205e-3            # ADXL1004 + capacitores
Y_CHIP0 = Y_PCB0 + Y_SOLD + 0.1   # chip de 5 × 5 mm entre la zona soldada de la punta y las ranuras de arriba
Y_SENSOR = Y_CHIP0 + 2.5
E_SENSOR = T_PCB / 2 + 0.9     # centro de masa del chip desde el plano medio de la PCB
BANDA_C1 = (1000, 3000)
ZETA = 0.002
MU = (0.3, 0.15)
TOL_LENG = 0.15
CARCASA = dict(y0=1.0, piso=0.5, techo=1.0, juego_lateral=0.2)
CARCASA["y_techo"] = Y_PCB1 + 1.0                 # retracción de 1 mm hasta el techo
CARCASA["y1"] = CARCASA["y_techo"] + CARCASA["techo"]


def geometria(d_leng=0.0):
    x_hoy = X_LENG + L_LENG + d_leng
    x_fin = x_hoy + PLANO
    xn, yn = x_fin + NARIZ * math.cos(math.radians(ANG_NARIZ)), Y_T + NARIZ * math.sin(math.radians(ANG_NARIZ))
    return x_hoy, x_fin, xn, yn


def lamina(zeta=ZETA, d_leng=0.0) -> Lamina:
    x_hoy, x_fin, xn, yn = geometria(d_leng)
    L = L_BRAZO
    # 0 tope PCB, 1 lámina sup, 2 lámina inf, 3 borde inf PCB, 4-5 PCB fija, 6 raíz de la punta, 7 codo, 8 raíz lengüeta,
    # 9 vértice, 10 fin del plano, 11 nariz
    P = [(X_PCB, Y_PCB1), (X_PCB, Y_SUP), (X_PCB, Y_INF), (X_PCB, Y_PCB0), (0, Y_SUP), (0, Y_INF),
         (X_PUNTA, Y_PCB0), (X_PUNTA, Y_CODO), (X_LENG, Y_T), (x_hoy, Y_T), (x_fin, Y_T), (xn, yn)]
    fr, cb = (E_FR4, RHO_FR4), (E_CB, RHO_CB)
    bb = N_TIRAS * B_TIRA
    S = [(0, 1, B_PCB, T_PCB) + fr, (1, 2, B_PCB, T_PCB) + fr, (2, 3, B_PCB, T_PCB) + fr,
         (4, 1, bb, T) + cb, (5, 2, bb, T) + cb,
         (3, 6, B_PCB, T_PCB) + fr,                    # unión soldada de la punta: rígida
         (6, 7, B_LENG, T) + cb, (7, 8, B_LENG, T) + cb, (8, 9, B_LENG, T) + cb, (9, 10, B_LENG, T) + cb, (10, 11, B_LENG, T) + cb]
    return Lamina(nombre="PCB + dos láminas rectas", t=T * mm, P=[(x * mm, y * mm) for x, y in P],
                  S=[(s[0], s[1], s[2] * mm, s[3] * mm) + tuple(s[4:]) for s in S], fijos=[4, 5], i_apex=9, seg_sensor=1,
                  y_sensor=Y_SENSOR * mm, m_sensor=M_SENSOR, e_sensor=E_SENSOR * mm,
                  J_sensor=M_SENSOR * (5e-3 ** 2 + 1.8e-3 ** 2) / 12, zeta=zeta, R_hoyuelo=R_HOY * mm)


def robustez(F0=2.0, mu=0.3):
    st = lamina().estatica(F0)
    k, d0, s0 = st["k_vertice_N_mm"], st["flecha_vertice_mm"], st["sigma_max_MPa"]
    C = CARCASA
    retraccion = C["y_techo"] - Y_PCB1
    caida = Y_PCB0 - (C["y0"] + C["piso"])
    d_max = d0 + retraccion
    EI = E_CB * 1e-6 * N_TIRAS * B_TIRA * T ** 3 / 12
    Pcr = math.pi ** 2 * EI / L_BRAZO ** 2
    sep = Y_SUP - Y_INF
    Fv = k * d_max
    return {"k_N_mm": k, "flecha_precarga_mm": d0, "sigma_precarga_MPa": s0, "asoma_mm": C["y0"],
            "retraccion_mm": retraccion, "caida_max_mm": caida, "sigma_tope_techo_MPa": s0 * d_max / d0,
            "sigma_lengueta_tope_MPa": Fv * L_LENG * (T / 2) / (B_LENG * T ** 3 / 12), "fluencia_MPa": SY_CB,
            "F_horizontal_pandeo_N": {"empuje hacia atrás": Pcr / (1 + Y_INF / sep), "empuje hacia adelante": Pcr / (Y_INF / sep)},
            "F_horizontal_para_subir_N": {"rampa trasera 35°": Fv * math.tan(math.radians(ANG_RAMPA) + math.atan(mu)),
                                          "nariz 30°": Fv * math.tan(math.radians(ANG_NARIZ) + math.atan(mu))},
            "F0_por_altura_N": [F0 - 0.3 * k, F0, F0 + 0.3 * k]}


def _eval(arg):
    z, F0, tg, mu, dl = arg
    e = evaluar(replace(lamina(z, dl), tangencial=tg, mu=mu), F0, BANDA_C1)
    c1 = {n: [r["C1"] for r in e["filas"] if r["estado"] == n] for n in NIVELES}
    return {"zeta": z, "F0": F0, "tg": tg, "mu": mu, "d_leng": dl, **{k: v for k, v in e.items() if k != "filas"},
            "satura_en": sorted({r["estado"] for r in e["filas"] if r["satura"]}),
            "Fc_min_sin_muy_floja": min(r["Fc_min"] for r in e["filas"] if r["estado"] != "muy_floja_juego"),
            "C1_rango": {n: [min(v), max(v)] for n, v in c1.items()}}


def umbrales(ev, F0=2.0):
    sel = [e for e in ev if e["F0"] == F0 and e["tg"] == "coulomb" and e["d_leng"] == 0.0]
    out = []
    for a, b in zip(NIVELES[1:], NIVELES[2:]):
        hi = max(e["C1_rango"][a][1] for e in sel)
        lo = min(e["C1_rango"][b][0] for e in sel)
        out.append({"entre": f"{a}/{b}", "umbral": (hi + lo) / 2, "hueco": lo - hi})
    return out


def verificar():
    lam = lamina()
    st = lam.estatica(2.0)
    f, _, part = lam.modos(2.0, 8)
    fs = np.linspace(300, 3000, 2701)
    H = lam.frf(2.0, fs)
    res = {"estatica": st, "modos_Hz": f.tolist(), "f0_Hz": float(fs[np.argmax(H)]), "pico": float(H.max()),
           "masa_carro_g": (M_SENSOR + RHO_FR4 * B_PCB * T_PCB * (Y_PCB1 - Y_PCB0) * 1e-9) * 1e3, "banda_C1_Hz": BANDA_C1}
    print("estática:", st)
    print("modos:", np.round(f), " f0:", res["f0_Hz"], " pico:", round(res["pico"], 1))
    casos = ([(ZETA, F0, "coulomb", mu, 0.0) for mu in MU for F0 in (1.6, 2.0, 2.4)]
             + [(ZETA, 2.0, "coulomb", MU[0], dl) for dl in (-TOL_LENG, TOL_LENG)]
             + [(ZETA, 2.0, tg, 0.0, 0.0) for tg in ("libre", "adherido")])
    with Pool(4) as pool:
        ev = pool.map(_eval, casos)
    for e in ev:
        print(f"F0={e['F0']:.1f} [{e['tg']:8s} μ={e['mu']:.2f} dL={e['d_leng']:+.2f}] despega={sorted(set(x.split('·')[0] for x in e['despega']))}  "
              f"satura={e['satura_en']}  Fc_min={e['Fc_min_sin_muy_floja']:.2f} N  gaps C1={np.round(e['gaps_C1'], 2)}  "
              f"gap C2={e['gap_C2_Hz']:.0f} Hz", flush=True)
    res["verificacion"] = ev
    res["robustez"] = robustez()
    res["umbrales_C1"] = umbrales(ev)
    print("robustez:", res["robustez"])
    print("umbrales:", res["umbrales_C1"])
    with open(OUT / "palpador_pcb.json", "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    return res


if __name__ == "__main__":
    verificar()
