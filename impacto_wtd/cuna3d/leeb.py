"""Calibración del modelo 3D con la dureza Leeb medida sobre una cuña ajustada.

DATO (usuario, oct 2026): una cuña AJUSTADA mide HL = 800.

Leeb = 1000 v_rebote / v_impacto con el cuerpo de impacto del durómetro
tipo D: 5,45 g, bola de carburo de tungsteno de 3 mm de diámetro, 11 mJ.
HL 800 quiere decir que el martillo pierde 1 - 0,8^2 = 36 % de su energía.

Ese 36 % tiene dos destinos:
  1. la ESTRUCTURA: ondas y vibración de la cuña, y lo que se lleva el
     asiento (rozamiento, choques). Eso es lo que depende del ajuste.
  2. la pérdida LOCAL bajo la punta: viscoelasticidad y daño de la matriz
     del G11 en la huella. Eso no depende del ajuste.

El modelo con contacto elástico en la punta sólo tiene (1). Acá se mide
cuánto da, y se calibra (2) con una disipación de Hunt-Crossley en la
punta, chi_punta, para que la cuña ajustada dé HL 800. Con eso:
  - se predice la escala Leeb de todos los estados (verificable en campo)
  - se recalcula el golpe del Takaha separando pérdida local y estructural

Uso:  python -m cuna3d.leeb
"""

from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.estudio import ESTADOS, OUT  # noqa: E402
from cuna3d.fem import Contactos, ModeloCuna  # noqa: E402

LEEB_D = dict(energia=11e-3, m_imp=5.45e-3, R_punta=1.5e-3, E_punta=600e9, nu_punta=0.22)
TAKAHA = dict(energia=5e-3, m_imp=3e-3, R_punta=3e-3, E_punta=210e9, nu_punta=0.29)
HL_AJUSTADA = 800.0
T_FIN = 0.5e-3

_cache = {}


def _modelo(i):
    if i not in _cache:
        est, _, ripple = ESTADOS[i]
        mod = ModeloCuna(cont=Contactos(ripple=ripple))
        mod.cargar_estado(est)
        mod.equilibrio()
        _cache[i] = mod
    return _cache[i]


def golpear(i, imp, chi):
    est, x_golpe, _ = ESTADOS[i]
    r = _modelo(i).golpe(x_golpe, t_fin=T_FIN, chi_punta=chi, **imp)
    return {"restitucion": r["restitucion"], "HL": 1000 * r["restitucion"],
            "E_entrada_mJ": r["E_entrada_mJ"], "E_transmitida_mJ": r["E_transmitida_mJ"],
            "E_punta_mJ": r["E_punta_mJ"], "E_estructura_mJ": r["E_transmitida_mJ"] - r["E_punta_mJ"],
            "F_H_max_N": r["F_H_max"], "t_contacto_us": r["t_contacto_us"],
            "rebota_aun": r["golpe_rebota_aun"], "error_balance": r["error_balance_energia"]}


def _tarea(arg):
    i, chi = arg
    return ESTADOS[i][0].nombre, {"leeb": golpear(i, LEEB_D, chi), "takaha": golpear(i, TAKAHA, chi)}


def calibrar(i_ref: int) -> tuple[float, list]:
    """Bisección en chi_punta para que el estado de referencia dé HL 800."""
    traza = []
    lo, hi = 0.0, 2.0
    e0 = golpear(i_ref, LEEB_D, 0.0)
    traza.append((0.0, e0["HL"]))
    if e0["HL"] <= HL_AJUSTADA:
        return 0.0, traza
    while golpear(i_ref, LEEB_D, hi)["HL"] > HL_AJUSTADA:
        hi *= 2
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        hl = golpear(i_ref, LEEB_D, mid)["HL"]
        traza.append((mid, hl))
        lo, hi = (mid, hi) if hl > HL_AJUSTADA else (lo, mid)
        if abs(hl - HL_AJUSTADA) < 0.5:
            break
    return 0.5 * (lo + hi), traza


def main():
    nombres = [e.nombre for e, _, _ in ESTADOS]
    i_ref = nombres.index("ajustada")
    chi, traza = calibrar(i_ref)
    print(f"chi_punta = {chi:.4f} s/m   (traza HL: {[(round(c, 4), round(h, 1)) for c, h in traza]})", flush=True)
    with Pool(4) as pool:
        elast = dict(pool.map(_tarea, [(i, 0.0) for i in range(len(ESTADOS))]))
        calib = dict(pool.map(_tarea, [(i, chi) for i in range(len(ESTADOS))]))
    for n in nombres:
        print(f"{n:24s} HL elástico {elast[n]['leeb']['HL']:6.1f}   HL calibrado {calib[n]['leeb']['HL']:6.1f}   "
              f"Takaha: e={calib[n]['takaha']['restitucion']:.3f}  local={calib[n]['takaha']['E_punta_mJ']:.2f} mJ  "
              f"estructura={calib[n]['takaha']['E_estructura_mJ']:.2f} mJ", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "leeb.json", "w") as fh:
        json.dump({"dato": {"HL_ajustada": HL_AJUSTADA, "estado_referencia": "ajustada", "durometro": "Leeb D",
                            **LEEB_D},
                   "chi_punta_s_m": chi, "traza_calibracion": traza,
                   "punta_elastica": elast, "punta_calibrada": calib}, fh, indent=1)


if __name__ == "__main__":
    main()
