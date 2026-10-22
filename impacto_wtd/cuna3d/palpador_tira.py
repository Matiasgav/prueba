"""Palpador de una tira: C plegada + punta liviana con rampas, protegida por la carcasa.

Dos piezas y dos tornillos: la chapa y el flex con el ADXL1004. Sin amortiguador
(C1 se mide en 1,5–5 kHz, por encima de f0) ni rigidizador.

La chapa es una sola pieza de 17-7PH de 0,15 mm, fotograbada, acuñada, plegada
y envejecida a CH900:

  * brazo superior (3 mm de ancho) y brazo inferior (dos tiras de 1,5 mm a
    los costados), de 13 mm, forman un paralelogramo: el carro baja derecho y
    la flecha da la precarga;
  * alma vertical (6 mm de ancho): por fuera, pegado, el extremo rígido del
    flex con el ADXL1004;
  * el centro del alma (2,4 mm) baja vertical hasta quedar dentro de la
    carcasa, sigue con una rampa a 35° (sólo debajo del piso) y termina en la
    lengüeta horizontal, que es el filtro: trabaja en flexión pura aunque la
    punta quede trabada por rozamiento. En la punta, el hoyuelo acuñado, el
    extremo redondeado siguiendo el hoyuelo y una nariz corta levantada 30°.

La punta tiene que ser liviana: el extremo redondeado (equivale a 0,6 mm de
lengüeta más allá del hoyuelo) y la nariz de 0,4 mm. Con 1 mm recto y una nariz
de 0,8 mm la separación ajustada/moderada se pierde.

Robustez: la carcasa limita todo. El piso es el tope de caída, el techo el de
retracción (la punta entra hasta quedar al ras del piso) y la ranura del piso,
0,2 mm más ancha que la punta, el tope lateral.

El rozamiento en la punta se modela como Coulomb (traba hasta μ·Fc y desliza);
se verifica también con los dos extremos, punta libre (μ = 0) y trabada.

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
from cuna3d.palpador_lamina import E_AC, Lamina, evaluar  # noqa: E402
from cuna3d.sensor import OUT  # noqa: E402

mm = 1e-3
T = 0.15            # espesor de la chapa
H_HOY = 0.25        # altura del hoyuelo (Ø de base 1,94 mm con R 2)
R_HOY = 2.0         # radio del hoyuelo
Y_T = H_HOY + T / 2  # línea media de la lengüeta (el vértice del hoyuelo en y = 0)
Y_INF, Y_SUP = 2.1, 7.0
L_BRAZO = 13.0
Y_CODO, ANG_RAMPA = 1.2, 35.0      # el centro baja vertical hasta Y_CODO (dentro de la carcasa) y sigue en rampa
L_RAMPA = (Y_CODO - Y_T) / math.sin(math.radians(ANG_RAMPA))
X_LENG = L_BRAZO + (Y_CODO - Y_T) / math.tan(math.radians(ANG_RAMPA))   # raíz de la lengüeta horizontal
L_LENG = 2.0                       # de la raíz al vértice del hoyuelo: el filtro
PLANO = 0.6                        # extremo redondeado más allá del hoyuelo, como largo equivalente
NARIZ, ANG_NARIZ = 0.4, 30.0
X_HOY = X_LENG + L_LENG
X_NARIZ = X_HOY + PLANO
B_SUP, B_TIRA, B_ALMA, RANURA = 3.0, 1.5, 6.0, 0.3
B_CENTRO = B_ALMA - 2 * B_TIRA - 2 * RANURA      # centro: rampa, lengüeta y nariz (2,4)
B_LENG = B_CENTRO
PCB = (5.0, 6.0, 0.4)          # extremo rígido del flex (refuerzo de FR4 del propio flex): y, z, x
CHIP = 1.8                     # espesor del ADXL1004 (LFCSP 5 × 5 mm)
Y_PCB = Y_INF - 0.1            # borde inferior del sensor sobre el alma
M_SENSOR = 0.200e-3 + 1850 * PCB[0] * PCB[1] * PCB[2] * 1e-9 + 10e-6 + 5e-6   # ADXL + refuerzo + flex + 0402 y adhesivo
E_SENSOR = 1.2                 # centro de masa del sensor, desde la línea media del alma hacia afuera
OREJA = 2.5
BANDA_C1 = (1500, 5000)        # por encima de f0: la resonancia sin amortiguar no entra en C1
ZETA = 0.002                   # acero + adhesivo, sin amortiguador
MU = (0.3, 0.15)               # rozamiento punta-cuña: nominal y superficie lubricada o barnizada
# carcasa (supuesto: piso a 1,0 ± 0,3 mm de la cuña); techo a 1,0 mm del brazo superior: la punta llega al ras del piso
CARCASA = dict(y0=1.0, piso=0.5, techo=1.0, juego_lateral=0.2)
CARCASA["y_techo"] = Y_SUP + T / 2 + CARCASA["y0"]
CARCASA["y1"] = CARCASA["y_techo"] + CARCASA["techo"]
SIGMA_C, SIGMA_CH900 = 1300.0, 1600.0   # fluencia típica de 17-7PH en condición C y envejecido CH900 [MPa]


def lamina(zeta=ZETA) -> Lamina:
    xn = X_NARIZ + NARIZ * math.cos(math.radians(ANG_NARIZ))
    yn = Y_T + NARIZ * math.sin(math.radians(ANG_NARIZ))
    P = [(0, Y_SUP), (L_BRAZO, Y_SUP), (L_BRAZO, Y_INF), (0, Y_INF), (L_BRAZO, Y_CODO), (X_LENG, Y_T),
         (X_HOY, Y_T), (X_NARIZ, Y_T), (xn, yn)]
    S = [(0, 1, B_SUP), (1, 2, B_ALMA), (2, 3, 2 * B_TIRA), (2, 4, B_CENTRO), (4, 5, B_CENTRO), (5, 6, B_LENG),
         (6, 7, B_LENG), (7, 8, B_LENG)]
    m = M_SENSOR
    return Lamina(nombre="tira: C plegada + punta liviana con rampas", t=T * mm,
                  P=[(x * mm, y * mm) for x, y in P], S=[(i, j, b * mm) for i, j, b in S], fijos=[0, 3], i_apex=6,
                  seg_sensor=1, y_sensor=(Y_PCB + PCB[0] / 2) * mm, m_sensor=m, e_sensor=E_SENSOR * mm,
                  J_sensor=m * (5e-3 ** 2 + CHIP ** 2 * 1e-6) / 12, zeta=zeta, R_hoyuelo=R_HOY * mm)


def robustez(F0=2.0, mu=0.3):
    """Topes de la carcasa y enganches: tensiones y fuerzas, desde la estática del modelo y vigas."""
    st = lamina().estatica(F0)
    k, d0, s0 = st["k_vertice_N_mm"], st["flecha_vertice_mm"], st["sigma_max_MPa"]
    C = CARCASA
    asoma = C["y0"]                                       # la punta sobresale del piso (nominal)
    retraccion = C["y_techo"] - Y_SUP - T / 2             # hasta el tope del techo
    caida = Y_INF - T / 2 - (C["y0"] + C["piso"])         # hasta el tope del piso
    d_max = d0 + retraccion
    s_techo = s0 * d_max / d0
    EI = lambda b: E_AC * 1e-6 * b * T ** 3 / 12          # N·mm²
    Pcr_inf = math.pi ** 2 * EI(2 * B_TIRA) / L_BRAZO ** 2   # empotrado-guiado
    Pcr_sup = math.pi ** 2 * EI(B_SUP) / L_BRAZO ** 2
    sep = Y_SUP - Y_INF
    F_atras, F_adelante = Pcr_inf / (1 + Y_INF / sep), Pcr_sup / (Y_INF / sep)
    Fv = k * d_max                                         # fuerza vertical en la punta, retraída al tope
    subir = {"rampa trasera 35°": Fv * math.tan(math.radians(ANG_RAMPA) + math.atan(mu)),
             "nariz 30°": Fv * math.tan(math.radians(ANG_NARIZ) + math.atan(mu))}
    I_l = B_LENG * T ** 3 / 12
    s_leng = Fv * L_LENG * (T / 2) / I_l
    brazo_lat = (X_HOY - L_BRAZO)                          # del alma al hoyuelo
    F_lat = SIGMA_CH900 * T * B_CENTRO ** 2 / 6 / brazo_lat
    return {"k_N_mm": k, "flecha_precarga_mm": d0, "sigma_precarga_MPa": s0, "asoma_mm": asoma,
            "retraccion_mm": retraccion, "caida_max_mm": caida, "sigma_tope_techo_MPa": s_techo,
            "sigma_lengueta_tope_MPa": s_leng, "fluencia_C_MPa": SIGMA_C, "fluencia_CH900_MPa": SIGMA_CH900,
            "F_horizontal_pandeo_N": {"empuje hacia atrás": F_atras, "empuje hacia adelante": F_adelante},
            "F_horizontal_para_subir_N": subir, "F_lateral_fluencia_N": F_lat,
            "F0_por_altura_N": [F0 - 0.3 * k, F0, F0 + 0.3 * k]}


def _eval(arg):
    z, F0, tg, mu = arg
    lam = replace(lamina(z), tangencial=tg, mu=mu)
    e = evaluar(lam, F0, BANDA_C1)
    c1 = {n: [r["C1"] for r in e["filas"] if r["estado"] == n] for n in NIVELES}
    return {"zeta": z, "F0": F0, "tg": tg, "mu": mu, **{k: v for k, v in e.items() if k != "filas"},
            "satura_en": sorted({r["estado"] for r in e["filas"] if r["satura"]}),
            "Fc_min_sin_muy_floja": min(r["Fc_min"] for r in e["filas"] if r["estado"] != "muy_floja_juego"),
            "C1_rango": {n: [min(v), max(v)] for n, v in c1.items()}}


def umbrales(ev, F0=2.0):
    """Umbrales de C1 que valen para los rozamientos reales (Coulomb, μ 0,3 y 0,15): punto medio de los huecos."""
    sel = [e for e in ev if e["F0"] == F0 and e["tg"] == "coulomb"]
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
    res = {"estatica": st, "modos_Hz": f.tolist(), "participacion": part.tolist(), "f0_Hz": float(fs[np.argmax(H)]),
           "pico": float(H.max()), "T_18k": float(lam.frf(2.0, np.array([18e3]))[0]),
           "T_43k": float(lam.frf(2.0, np.array([43e3]))[0]), "masa_carro_g": M_SENSOR * 1e3, "banda_C1_Hz": BANDA_C1}
    print("estática:", st)
    print("modos:", np.round(f), " f0:", res["f0_Hz"], " pico:", round(res["pico"], 1))
    casos = ([(ZETA, F0, "coulomb", mu) for mu in MU for F0 in (1.6, 2.0, 2.4)]
             + [(ZETA, 2.0, tg, 0.0) for tg in ("libre", "adherido")])
    with Pool(4) as pool:
        ev = pool.map(_eval, casos)
    for e in ev:
        print(f"F0={e['F0']:.1f} [{e['tg']:8s} μ={e['mu']:.2f}] despega={sorted(set(x.split('·')[0] for x in e['despega']))}  "
              f"satura={e['satura_en']}  Fc_min (sin la muy floja)={e['Fc_min_sin_muy_floja']:.2f} N  "
              f"gaps C1={np.round(e['gaps_C1'], 2)}  gap C2={e['gap_C2_Hz']:.0f} Hz", flush=True)
    res["verificacion"] = ev
    res["robustez"] = robustez()
    res["umbrales_C1"] = umbrales(ev)
    print("robustez:", res["robustez"])
    print("umbrales (Coulomb, 2 N):", res["umbrales_C1"])
    with open(OUT / "palpador_tira.json", "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    return res


if __name__ == "__main__":
    verificar()
