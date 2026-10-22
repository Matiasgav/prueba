"""La resonancia del filtro mecánico: ¿despega?, ¿cambia la lectura?

El palpador amplifica en su frecuencia de corte (Q = 1/(2 zeta)). Acá se
barre lo que no se controla bien en el palpador real, a 15 mm del golpe:

    zeta   0,005 / 0,01 / 0,02 / 0,04   (amortiguamiento de la flexura)
    f0     1,10 / 1,25 / 1,40 kHz       (tolerancia de fabricación de la flexura)
    F0     1,0 / 2,5 N                  (precarga)

contra los 5 niveles con sus variantes (energía ±10 %, rigidez de flancos
±30 %) y los 6 estados de holgura parcial. Se mira: despegue, fuerza mínima,
C1, C2, si la regla de 5 niveles sigue acertando, y cuánto de C1 viene de la
banda de la resonancia.

Uso:  python -m cuna3d.resonancia
"""

from __future__ import annotations

import json
import math
import os
import sys
import zlib
from multiprocessing import Pool

import numpy as np
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.clasificacion import M_CARRO, caracteristicas  # noqa: E402
from cuna3d.distancia import D_MM, DIST, NIVELES, VARIANTES  # noqa: E402
from cuna3d.sensor import ADXL1004, G, M_PUNTA, OUT, Palpador, _flexura  # noqa: E402

D_SEL = 15.0
PARCIALES = ["extremo_poca_presion", "extremo_flojo", "medio_flojo", "medio_libre_juego",
             "extremo_libre_juego", "ajustada_sin_ripple"]
ZETAS = (0.005, 0.01, 0.02, 0.04)
F0S = (1100.0, 1250.0, 1400.0)
PRECARGAS = (1.0, 2.5)
R_PUNTA = 2e-3
UMBRALES = (0.35, 1.40, 2.95)          # regla de decisión a 15 mm (diseño nominal)


def palpador(zeta, f0, F0):
    k = _flexura(f0, M_CARRO, M_PUNTA, 1.0, R_PUNTA)        # la flexura se fabrica para f0 con 1 N
    return Palpador("p", [M_PUNTA, M_CARRO], [k], [zeta], F0=F0, R_punta=R_PUNTA)


def _caso(arg):
    estado, var, zeta, f0, F0 = arg
    i_d = int(np.argmin(np.abs(D_MM - D_SEL)))
    d = np.load(DIST / f"{estado}__{var}.npz")
    p = palpador(zeta, f0, F0)
    tt, a, Fc = p.simular(d["t"], d["uy"][:, i_d], d["vy"][:, i_d])
    rng = np.random.default_rng(zlib.crc32(f"{estado}{var}{zeta}{f0}{F0}".encode()))
    ts, y, sat = ADXL1004.leer(tt, a, rng=rng)
    c = caracteristicas(ts, y, float(d["E"]) * 1e3)
    # parte de C1 que cae en la banda de la resonancia (0,8 f0 a 1,25 f0)
    fs = 1 / (ts[1] - ts[0])
    w3 = ts <= 3e-3
    sos = butter(4, [0.8 * f0, 1.25 * f0], btype="band", fs=fs, output="sos")
    E_res = float(np.sum(sosfiltfilt(sos, y[w3]) ** 2) / fs * 1e3)
    return {"estado": estado, "var": var, "zeta": zeta, "f0": f0, "F0": F0,
            "despega": bool(np.any(Fc <= 0)), "frac_despegado": float(np.mean(Fc <= 0)),
            "Fc_min": float(Fc.min()), "satura": sat, "a_pico_g": float(np.abs(a).max() / G),
            "C1": c["C1"], "C2": c["C2"], "frac_resonancia": E_res / max(c["Eb"], 1e-12)}


def clasificar(C1, C2, f_ref, despega):
    if despega or C1 > UMBRALES[2]:
        return "muy_floja_juego"
    if C1 > UMBRALES[1]:
        return "floja"
    if C1 > UMBRALES[0]:
        return "moderada"
    return "muy_ajustada" if C2 >= f_ref - 225 else "ajustada"


def main():
    casos = [(n, v) for n in NIVELES for v in VARIANTES] + [(n, "base") for n in PARCIALES]
    tareas = [(n, v, z, f0, F0) for n, v in casos for z in ZETAS for f0 in F0S for F0 in PRECARGAS]
    with Pool(4) as pool:
        filas = pool.map(_caso, tareas, chunksize=8)
    resumen = []
    for z in ZETAS:
        for f0 in F0S:
            for F0 in PRECARGAS:
                fs = [r for r in filas if r["zeta"] == z and r["f0"] == f0 and r["F0"] == F0]
                # calibración: f_ref con las cuñas muy ajustadas de rigidez nominal
                ref = [r for r in fs if r["estado"] == "muy_ajustada" and r["var"] in ("base", "E-10", "E+10")]
                f_ref = float(np.mean([r["C2"] for r in ref]))
                aciertos = errores = 0
                err_lista = []
                for r in fs:
                    r["clase"] = clasificar(r["C1"], r["C2"], f_ref, r["despega"])
                    if r["estado"] in NIVELES and r["var"] in ("base", "E-10", "E+10"):
                        ok = r["clase"] == r["estado"]
                        aciertos += ok
                        errores += not ok
                        if not ok:
                            err_lista.append(f"{r['estado']}·{r['var']}→{r['clase']}")
                # con rigidez desconocida (k±30) sólo se exige la clase de 4 niveles
                k4 = [r for r in fs if r["estado"] in NIVELES and r["var"] in ("k-30", "k+30")]
                grupo = lambda c: "ajustada" if c in ("muy_ajustada", "ajustada") else c
                err4 = [f"{r['estado']}·{r['var']}→{r['clase']}" for r in k4 if grupo(r["clase"]) != grupo(r["estado"])]
                desp = [f"{r['estado']}·{r['var']}" for r in fs if r["despega"]]
                parc = {r["estado"]: r["clase"] for r in fs if r["estado"] in PARCIALES}
                res = {"zeta": z, "f0": f0, "F0": F0, "Q": 1 / (2 * z), "f_ref": f_ref,
                       "despega": desp, "Fc_min": min(r["Fc_min"] for r in fs),
                       "aciertos_5": aciertos, "errores_5": err_lista, "errores_4_k30": err4,
                       "parciales": parc,
                       "frac_res_max": max(r["frac_resonancia"] for r in fs)}
                resumen.append(res)
                print(f"zeta={z:5.3f} (Q={1/(2*z):5.0f}) f0={f0:5.0f} F0={F0:.1f}  despega={len(desp)} {desp[:3]}  "
                      f"Fc_min={res['Fc_min']:.2f} N  5 niveles: {aciertos}/{aciertos+errores} {err_lista[:3]}  "
                      f"4 niveles con k±30: {len(err4)} errores  parciales={parc}", flush=True)
    # excitación sostenida que despega el palpador, y tiempo de apagado
    sost = []
    for z in ZETAS:
        p = palpador(z, 1250.0, 1.0)
        H = p.frf(np.linspace(1000, 1500, 1001)).max()
        sost.append({"zeta": z, "Q": 1 / (2 * z), "H_max": float(H),
                     "a_cuna_sostenida_g": p.a_despegue_g() / H,
                     "x_cuna_sostenida_um": p.a_despegue_g() * G / H / (2 * math.pi * 1250) ** 2 * 1e6,
                     "t_apagado_1pc_ms": math.log(100) / (z * 2 * math.pi * 1250) * 1e3})
    for s_ in sost:
        print(s_)
    with open(OUT / "resonancia.json", "w") as fh:
        json.dump({"filas": filas, "resumen": resumen, "sostenida": sost}, fh)


if __name__ == "__main__":
    main()
