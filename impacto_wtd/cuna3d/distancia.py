"""Movimiento de la cara superior de la cuña entre 5 y 20 mm del golpe, con incertidumbres.

Para elegir la distancia del palpador y comprobar que los 5 niveles de
ajuste se distinguen "con seguridad", cada nivel se corre con las
incertidumbres que más pesan:

    base      5 mJ, rigidez de flancos nominal (2e12 N/m^3 a 1 MPa)
    E-10/E+10 energía del golpe 4,5 / 5,5 mJ
    k-30/k+30 rigidez de flancos x 0,7 / x 1,3  (la incógnita más grande del modelo)

Salida: results/cuna3d/distancia/<nivel>__<variante>.npz  (t, uy[t, d], vy[t, d])

Uso:  python -m cuna3d.distancia
"""

from __future__ import annotations

import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.estudio import ESTADOS, OUT, chi_punta  # noqa: E402
from cuna3d.fem import Contactos, ModeloCuna  # noqa: E402

DIST = OUT / "distancia"
NIVELES = ["muy_ajustada", "ajustada", "moderada", "floja", "muy_floja_juego"]
D_MM = np.arange(5.0, 20.01, 2.5)
X_GOLPE = 0.10
VARIANTES = {"base": (5e-3, 1.0), "E-10": (4.5e-3, 1.0), "E+10": (5.5e-3, 1.0),
             "k-30": (5e-3, 0.7), "k+30": (5e-3, 1.3)}


def correr(arg):
    nivel, var = arg
    E, fk = VARIANTES[var]
    # punto de golpe de cada estado (en las holguras parciales, sobre la zona floja)
    est, x_g, ripple = next((e, x, rp) for e, x, rp in ESTADOS if e.nombre == nivel)
    mod = ModeloCuna(cont=Contactos(kn_flanco_1MPa=2.0e12 * fk, ripple=ripple))
    mod.cargar_estado(est)
    mod.equilibrio()
    r = mod.golpe(x_g, energia=E, t_fin=3e-3, chi_punta=chi_punta(),
                  x_palps=list(x_g + D_MM * 1e-3))
    H = r["hist"]
    DIST.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DIST / f"{nivel}__{var}.npz", t=H["t"], uy=H["uy_palps"], vy=H["vy_palps"],
                        d_mm=(r["x_palps"] - x_g) * 1e3, E=E, fk=fk, x_golpe=x_g,
                        restitucion=r["restitucion"], E_transmitida_mJ=r["E_transmitida_mJ"],
                        error_balance=r["error_balance_energia"])
    print(f"{nivel:18s} {var:5s} e={r['restitucion']:.3f}  balance={r['error_balance_energia']*100:.2f} %", flush=True)


def main():
    tareas = [(n, v) for n in NIVELES for v in VARIANTES]
    sel = [a for a in sys.argv[1:] if not a.startswith("--")]
    if sel:
        tareas = [t for t in tareas if t[0] in sel or t[1] in sel]
    with Pool(4) as pool:
        pool.map(correr, tareas)


if __name__ == "__main__":
    main()
