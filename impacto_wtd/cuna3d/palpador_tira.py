"""Palpador de una tira, versión robusta: C plegada + punta con rampas, protegida por la carcasa.

Dos piezas y dos tornillos: la chapa y el flex con el ADXL1004. Sin amortiguador
(C1 se mide en 1,5–5 kHz, por encima de f0) ni rigidizador.

La chapa es una sola pieza de 17-7PH de 0,20 mm, fotograbada y plegada:

  * brazo superior (3 mm de ancho) y brazo inferior (dos tiras de 1,5 mm a
    los costados), de 18 mm, forman un paralelogramo: el carro baja derecho y
    la flecha da la precarga;
  * alma vertical (6 mm de ancho): por fuera, pegado, el extremo rígido del
    flex con el ADXL1004;
  * el centro del alma (2,4 mm) baja inclinado 35° desde la unión con el brazo
    inferior (pierna: rampa trasera), sigue un tramo plano con el hoyuelo
    acuñado (el contacto) y termina en una nariz levantada 30° (rampa
    delantera). Es el filtro, y no tiene cantos de frente en ningún sentido de
    marcha.

Robustez: la carcasa limita todo. El piso es el tope de caída (sin cuña la
punta baja como mucho 0,5 mm), el techo es el tope de retracción (la punta
entra entera en la carcasa) y la ranura del piso, 0,2 mm más ancha que la
pierna, es el tope lateral. En todos los topes la chapa queda elástica.

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
T = 0.20            # espesor de la chapa
H_HOY = 0.25        # altura del hoyuelo (Ø de base 1,94 mm con R 2)
R_HOY = 2.0         # radio del hoyuelo
Y_T = H_HOY + T / 2  # línea media del tramo plano (el vértice del hoyuelo en y = 0)
Y_INF, Y_SUP = 2.1, 8.6
L_BRAZO = 18.0
ANG_PIERNA, PLANO, NARIZ, ANG_NARIZ = 35.0, 1.0, 0.8, 30.0   # pierna inclinada, plano a cada lado del hoyuelo, nariz
L_PIERNA = (Y_INF - Y_T) / math.sin(math.radians(ANG_PIERNA))
X_PLANO = L_BRAZO + L_PIERNA * math.cos(math.radians(ANG_PIERNA))   # comienzo del tramo plano
X_HOY = X_PLANO + PLANO                                            # vértice del hoyuelo
X_NARIZ = X_HOY + PLANO
B_SUP, B_TIRA, B_ALMA, RANURA = 3.0, 1.5, 6.0, 0.3
B_CENTRO = B_ALMA - 2 * B_TIRA - 2 * RANURA      # parte central: pierna, plano y nariz (2,4)
B_LENG = B_CENTRO
PCB = (5.0, 6.0, 0.4)          # extremo rígido del flex (refuerzo de FR4 del propio flex): y, z, x
CHIP = 1.8                     # espesor del ADXL1004 (LFCSP 5 × 5 mm)
Y_PCB = Y_INF + 0.5            # borde inferior del sensor sobre el alma
M_SENSOR = 0.200e-3 + 1850 * PCB[0] * PCB[1] * PCB[2] * 1e-9 + 10e-6 + 5e-6   # ADXL + refuerzo + flex + 0402 y adhesivo
E_SENSOR = 1.2                 # centro de masa del sensor, desde la línea media del alma hacia afuera
OREJA = 2.5
BANDA_C1 = (1500, 5000)        # por encima de f0: la resonancia sin amortiguar no entra en C1
ZETA = 0.002                   # acero + adhesivo, sin amortiguador
# carcasa (supuesto: piso a 1,0 ± 0,3 mm de la cuña)
CARCASA = dict(y0=1.0, y1=11.0, piso=0.5, techo=1.0, juego_lateral=0.2)
SIGMA_FLUENCIA = 1300.0        # 17-7PH condición C, típico [MPa]; el envejecido CH900 lo sube


def lamina(zeta=ZETA) -> Lamina:
    xn = X_NARIZ + NARIZ * math.cos(math.radians(ANG_NARIZ))
    yn = Y_T + NARIZ * math.sin(math.radians(ANG_NARIZ))
    P = [(0, Y_SUP), (L_BRAZO, Y_SUP), (L_BRAZO, Y_INF), (0, Y_INF),
         (X_PLANO, Y_T), (X_HOY, Y_T), (X_NARIZ, Y_T), (xn, yn)]
    S = [(0, 1, B_SUP), (1, 2, B_ALMA), (2, 3, 2 * B_TIRA), (2, 4, B_CENTRO), (4, 5, B_LENG), (5, 6, B_LENG), (6, 7, B_LENG)]
    m = M_SENSOR
    return Lamina(nombre="tira robusta: C plegada + punta con rampas", t=T * mm,
                  P=[(x * mm, y * mm) for x, y in P], S=[(i, j, b * mm) for i, j, b in S], fijos=[0, 3], i_apex=5,
                  seg_sensor=1, y_sensor=(Y_PCB + PCB[0] / 2) * mm, m_sensor=m, e_sensor=E_SENSOR * mm,
                  J_sensor=m * (5e-3 ** 2 + CHIP ** 2 * 1e-6) / 12, zeta=zeta, R_hoyuelo=R_HOY * mm)


def robustez(F0=2.0, mu=0.3):
    """Topes de la carcasa y enganches: tensiones y fuerzas, desde la estática del modelo y vigas."""
    lam = lamina()
    st = lam.estatica(F0)
    k, d0, s0 = st["k_vertice_N_mm"], st["flecha_vertice_mm"], st["sigma_max_MPa"]
    C = CARCASA
    asoma = C["y0"]                                    # la punta sobresale del piso (nominal)
    gap_techo = C["y1"] - C["techo"] - Y_SUP - T / 2   # retracción hasta el tope del techo
    gap_piso = Y_INF - T / 2 - (C["y0"] + C["piso"])   # caída hasta el tope del piso
    d_max = d0 + gap_techo
    s_techo = s0 * d_max / d0
    # pandeo de los brazos (empotrado-guiado) y fuerza horizontal en la punta que los lleva al pandeo
    EI = lambda b: E_AC * 1e-6 * b * T ** 3 / 12        # N·mm²
    Pcr_inf = math.pi ** 2 * EI(2 * B_TIRA) / L_BRAZO ** 2
    Pcr_sup = math.pi ** 2 * EI(B_SUP) / L_BRAZO ** 2
    sep = Y_SUP - Y_INF
    c_inf = 1 + Y_INF / sep        # empuje hacia atrás (−x): brazo inferior comprimido
    c_sup = Y_INF / sep            # empuje hacia adelante (+x): brazo superior comprimido
    F_x_menos, F_x_mas = Pcr_inf / c_inf, Pcr_sup / c_sup
    # fuerza horizontal para subir un escalón por cada rampa, con la punta ya retraída al tope
    Fv = k * d_max
    subir = {f"rampa {a:.0f}°": Fv * math.tan(math.radians(a) + math.atan(mu)) for a in (ANG_PIERNA, ANG_NARIZ)}
    # pierna: flexión con la fuerza del tope y pandeo
    I_p = B_CENTRO * T ** 3 / 12
    s_pierna = Fv * L_PIERNA * math.cos(math.radians(ANG_PIERNA)) * (T / 2) / I_p
    F_lat = SIGMA_FLUENCIA * T * B_CENTRO ** 2 / 6 / (L_PIERNA + PLANO)   # lateral (z) en la punta, contra la ranura
    return {"k_N_mm": k, "flecha_precarga_mm": d0, "sigma_precarga_MPa": s0, "asoma_mm": asoma,
            "retraccion_mm": gap_techo, "caida_max_mm": gap_piso, "sigma_tope_techo_MPa": s_techo,
            "sigma_pierna_tope_MPa": s_pierna, "fluencia_MPa": SIGMA_FLUENCIA,
            "F_horizontal_pandeo_N": {"empuje hacia atrás": F_x_menos, "empuje hacia adelante": F_x_mas},
            "F_horizontal_para_subir_N": subir, "F_lateral_fluencia_pierna_N": F_lat,
            "F0_por_altura_N": [F0 - 0.3 * k, F0, F0 + 0.3 * k]}


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
    res["robustez"] = robustez()
    print("robustez:", res["robustez"])
    res["umbrales_C1"] = {f"{z}_{F0}": umbrales(ev, z, F0) for z in (0.002, 0.005) for F0 in (1.6, 2.0, 2.4)}
    print("umbrales (ζ 0,002, 2 N):", res["umbrales_C1"]["0.002_2.0"])
    with open(OUT / "palpador_tira.json", "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    return res


if __name__ == "__main__":
    verificar()
