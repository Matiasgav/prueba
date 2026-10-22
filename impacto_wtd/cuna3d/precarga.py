"""Efecto de la precarga (1 a 2,5 N) sobre el palpador recomendado a 15 mm.

La flexura es una pieza fija: se diseña para f0 = 1,25 kHz con 1 N y se
deja igual al cambiar la precarga (sólo cambia la rigidez de Hertz de la
punta, que está en serie). Se miran la lectura (C1, C2), el despegue y la
presión de contacto de Hertz sobre el G11 (estática y la máxima del golpe).

Uso:  python -m cuna3d.precarga
"""

from __future__ import annotations

import json
import math
import os
import sys
import zlib
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.clasificacion import M_CARRO, caracteristicas  # noqa: E402
from cuna3d.distancia import D_MM, DIST, NIVELES, VARIANTES  # noqa: E402
from cuna3d.sensor import ADXL1004, M_PUNTA, OUT, Palpador, _flexura  # noqa: E402

D_SEL = 15.0
PRECARGAS = (1.0, 1.5, 2.0, 2.5)
RADIOS = (1e-3, 2e-3)
K_FLEX = _flexura(1250, M_CARRO, M_PUNTA, 1.0)       # pieza fija, diseñada con 1 N
E_EST = 1 / ((1 - 0.29 ** 2) / 210e9 + (1 - 0.2 ** 2) / 20e9)


def p0_hertz(F, R):
    """Presión máxima de Hertz esfera-plano [Pa]."""
    a = (3 * F * R / (4 * E_EST)) ** (1 / 3)
    return 3 * F / (2 * math.pi * a * a)


def _caso(arg):
    nivel, var, F0, R = arg
    i_d = int(np.argmin(np.abs(D_MM - D_SEL)))
    d = np.load(DIST / f"{nivel}__{var}.npz")
    pal = Palpador("p", [M_PUNTA, M_CARRO], [K_FLEX], [0.02], F0=F0, R_punta=R)
    tt, a, Fc = pal.simular(d["t"], d["uy"][:, i_d], d["vy"][:, i_d])
    rng = np.random.default_rng(zlib.crc32(f"{nivel}{var}{F0}{R}".encode()))
    f = [caracteristicas(*ADXL1004.leer(tt, a, rng=rng)[:2], float(d["E"]) * 1e3) for _ in range(8)]
    return {"nivel": nivel, "var": var, "F0": F0, "R_mm": R * 1e3, "f0_Hz": float(pal.modos()[0]),
            "despega": bool(np.any(Fc <= 0)), "Fc_min": float(Fc.min()), "Fc_max": float(Fc.max()),
            "p0_est_MPa": p0_hertz(F0, R) / 1e6, "p0_max_MPa": p0_hertz(float(Fc.max()), R) / 1e6,
            "C1": [x["C1"] for x in f], "C2": [x["C2"] for x in f]}


def main():
    tareas = [(n, v, F0, R) for R in RADIOS for F0 in PRECARGAS for n in NIVELES for v in VARIANTES]
    with Pool(4) as pool:
        filas = pool.map(_caso, tareas)
    for R in RADIOS:
        print(f"\n=== punta R = {R*1e3:.0f} mm")
        for F0 in PRECARGAS:
            fs = [r for r in filas if r["F0"] == F0 and r["R_mm"] == R * 1e3]
            print(f"F0={F0:.1f} N  f0={fs[0]['f0_Hz']:.0f} Hz  despega={sum(r['despega'] for r in fs)}  "
                  f"Fc_min={min(r['Fc_min'] for r in fs):.2f} N  p0 estática={fs[0]['p0_est_MPa']:.0f} MPa  "
                  f"p0 máx golpe={max(r['p0_max_MPa'] for r in fs):.0f} MPa")
            for n in NIVELES:
                c1 = np.concatenate([r["C1"] for r in fs if r["nivel"] == n])
                c2b = np.mean([np.mean(r["C2"]) for r in fs if r["nivel"] == n and r["var"] == "base"])
                print(f"    {n:16s} C1 {c1.min():6.3f} a {c1.max():6.3f}   C2(base) {c2b:7.0f} Hz")
    with open(OUT / "precarga.json", "w") as fh:
        json.dump({"filas": filas, "d_mm": D_SEL, "k_flexura_N_m": K_FLEX}, fh)


if __name__ == "__main__":
    main()
