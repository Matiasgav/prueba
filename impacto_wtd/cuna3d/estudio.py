"""Corre el modelo 3D de la cuña en los estados de ajuste y exporta resultados.

Para cada estado:
  1. equilibrio estático con la precarga (presiones en flancos y fondo)
  2. modos linealizados alrededor de ese equilibrio
  3. golpe de 5 mJ del impactador (Takaha CA0422, 3 g, punta R 3 mm),
     dinámica no lineal completa durante 3 ms

Salidas:
  results/cuna3d/resumen.json         números por estado
  docs/cuna3d/datos/malla.json        superficie para la animación
  docs/cuna3d/datos/<estado>.json     señales, modos y presiones
  docs/cuna3d/datos/<estado>.b64.txt  cuadros de la animación del golpe (int8, base64)

Uso:  python -m cuna3d.estudio  [--rapido]
"""

from __future__ import annotations

import base64
import json
import math
import os
import pathlib
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.fem import Contactos, Estado, ModeloCuna  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
OUT = RAIZ / "results" / "cuna3d"
WEB = RAIZ / "docs" / "cuna3d" / "datos"

PALP = OUT / "palpador"

MPa = 1e6


def chi_punta() -> float:
    """Pérdida local bajo la punta calibrada con HL 800 en la cuña ajustada (cuna3d/leeb.py)."""
    f = OUT / "leeb.json"
    return float(json.loads(f.read_text())["chi_punta_s_m"]) if f.exists() else 0.0
L = 200e-3

# Escala de 5 niveles (propuesta, ver docs/cuna3d): valor representativo de cada nivel
NIVELES = {"muy ajustada": 1.2 * MPa, "ajustada": 0.7 * MPa, "moderada": 0.3 * MPa,
           "floja": 0.08 * MPa, "muy floja": 0.0}


def _zona(x, a, b):
    return (x >= a) & (x <= b)


ESTADOS = [
    # nombre, estado, x_golpe, ripple
    (Estado("muy_ajustada", lambda x: NIVELES["muy ajustada"] + 0 * x, nivel="muy ajustada",
            nota="1,2 MPa uniforme"), 0.10, True),
    (Estado("ajustada", lambda x: NIVELES["ajustada"] + 0 * x, nivel="ajustada",
            nota="0,7 MPa uniforme"), 0.10, True),
    (Estado("moderada", lambda x: NIVELES["moderada"] + 0 * x, nivel="moderada",
            nota="0,3 MPa uniforme"), 0.10, True),
    (Estado("floja", lambda x: NIVELES["floja"] + 0 * x, nivel="floja",
            nota="0,08 MPa uniforme: menos que la fuerza de cortocircuito"), 0.10, True),
    (Estado("muy_floja_juego", lambda x: 0 * x, juego_fondo=lambda x: 50e-6 + 0 * x,
            nivel="muy floja", nota="sin presión, 50 µm de juego contra el ripple"), 0.10, True),
    (Estado("extremo_flojo", lambda x: np.where(x < 60e-3, 0.0, NIVELES["ajustada"]),
            nivel="holgura parcial", nota="0 MPa en los primeros 60 mm, 0,7 MPa en el resto; golpe en la zona floja"),
     0.03, True),
    (Estado("extremo_poca_presion", lambda x: np.where(x < 60e-3, 0.05 * MPa, NIVELES["ajustada"]),
            nivel="holgura parcial", nota="0,05 MPa en los primeros 60 mm, 0,7 MPa en el resto; golpe en la zona floja"),
     0.03, True),
    (Estado("medio_flojo", lambda x: np.where(_zona(x, 60e-3, 140e-3), 0.0, NIVELES["ajustada"]),
            nivel="holgura parcial", nota="0 MPa entre 60 y 140 mm, 0,7 MPa en los extremos; golpe en el centro"),
     0.10, True),
    (Estado("extremo_libre_juego", lambda x: np.where(x < 60e-3, 0.0, NIVELES["ajustada"]),
            juego_fondo=lambda x: np.where(x < 60e-3, 20e-6, 0.0),
            juego_flanco=lambda x: np.where(x < 60e-3, 10e-6, 0.0),
            nivel="holgura parcial", nota="primeros 60 mm libres: 20 µm de juego contra el ripple y 10 µm contra "
            "los hombros; 0,7 MPa en el resto. Golpe en la zona libre: choca contra el ripple y rebota contra los hombros"),
     0.03, True),
    (Estado("medio_libre_juego", lambda x: np.where(_zona(x, 60e-3, 140e-3), 0.0, NIVELES["ajustada"]),
            juego_fondo=lambda x: np.where(_zona(x, 60e-3, 140e-3), 10e-6, 0.0),
            juego_flanco=lambda x: np.where(_zona(x, 60e-3, 140e-3), 5e-6, 0.0),
            nivel="holgura parcial", nota="tramo central de 80 mm libre, con 10 µm de juego contra el ripple y "
            "5 µm contra los hombros; 0,7 MPa en los extremos. Golpe en el centro"),
     0.10, True),
    (Estado("ajustada_sin_ripple", lambda x: NIVELES["ajustada"] + 0 * x, nivel="ajustada",
            nota="0,7 MPa, fondo rígido (sin ripple): contacto de Hertz contra la barra"), 0.10, False),
]

# cuadros de la animación: densos durante el contacto, ralos después
FRAMES_T = np.concatenate([np.arange(0, 200e-6, 4e-6), np.arange(200e-6, 3.0e-3 + 1e-9, 50e-6)])


def nodos_visibles(mod: ModeloCuna):
    """Superficie de la cuña submuestreada en x (cada nodo de esquina de elemento)."""
    m = mod.m
    ixs = np.arange(0, m.nx, 2)
    per = ([(0, iz) for iz in range(m.nz)] + [(iy, m.nz - 1) for iy in range(1, m.ny)]
           + [(m.ny - 1, iz) for iz in range(m.nz - 2, -1, -1)] + [(iy, 0) for iy in range(m.ny - 2, 0, -1)])
    nod, tri = [], []
    idx = {}
    for i, ix in enumerate(ixs):
        for j, (iy, iz) in enumerate(per):
            idx[(ix, iy, iz)] = len(nod)
            nod.append(int(m.nodo(ix, iy, iz)))
    P = len(per)
    for i in range(len(ixs) - 1):
        for j in range(P):
            a = idx[(ixs[i], *per[j])]
            b = idx[(ixs[i], *per[(j + 1) % P])]
            c = idx[(ixs[i + 1], *per[(j + 1) % P])]
            d = idx[(ixs[i + 1], *per[j])]
            tri += [(a, b, c), (a, c, d)]
    for ix, sgn in ((0, -1), (ixs[-1], 1)):          # tapas en los extremos
        for iy in range(m.ny):
            for iz in range(m.nz):
                if (ix, iy, iz) not in idx:
                    idx[(ix, iy, iz)] = len(nod)
                    nod.append(int(m.nodo(ix, iy, iz)))
        for iy in range(m.ny - 1):
            for iz in range(m.nz - 1):
                a, b = idx[(ix, iy, iz)], idx[(ix, iy, iz + 1)]
                c, d = idx[(ix, iy + 1, iz + 1)], idx[(ix, iy + 1, iz)]
                tri += [(a, b, c), (a, c, d)] if sgn > 0 else [(a, c, b), (a, d, c)]
    return np.array(nod), np.array(tri)


def correr(arg):
    i, rapido = arg
    est, x_golpe, ripple = ESTADOS[i]
    t0 = time.time()
    mod = ModeloCuna(cont=Contactos(ripple=ripple))
    mod.cargar_estado(est)
    mod.equilibrio()
    eq = mod.resumen_equilibrio()
    f, phi = mod.modos(12)
    nod_vis, tri = nodos_visibles(mod)
    t_fin = 0.4e-3 if rapido else 3.0e-3
    fr = FRAMES_T[FRAMES_T <= t_fin]
    r = mod.golpe(x_golpe, t_fin=t_fin, frames_t=fr, nodos_vis=nod_vis, chi_punta=chi_punta())
    # movimiento del punto del palpador a resolución completa (para cuna3d/sensor.py)
    PALP.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(PALP / f"{est.nombre}.npz", t=r["hist"]["t"], uy=r["hist"]["uy_palp"],
                        vy=r["hist"]["vy_palp"], ay=r["hist"]["ay_palp"], F_H=r["hist"]["F_H"],
                        x_golpe=x_golpe, x_palp=x_golpe + 10e-3)
    H = r["hist"]
    # ---- presiones estáticas sobre los flancos y el fondo (para mapas)
    p_l, _ = mod.flanco_presion(mod.u0)
    p_f, _ = mod.fondo_presion(mod.u0)
    m = mod.m
    nfl = m.nx * m.ny
    # ---- modos: forma sobre la superficie visible, normalizada a 1
    modos = []
    for k in range(phi.shape[1]):
        if f[k] < 1.0:
            continue
        sh = phi[:, k].reshape(-1, 3)[nod_vis]
        sh = sh / np.abs(sh).max()
        modos.append({"f_Hz": round(float(f[k]), 1),
                      "forma": np.round(sh * 127).astype(int).ravel().tolist()})
    n_rigidos = int(np.sum(f < 1.0))
    # ---- aceleración como la vería un acelerómetro real: el modelo resuelve
    # hasta cientos de kHz, y el pico crudo depende de ese ancho de banda.
    fs = 1.0 / float(H["t"][1] - H["t"][0])
    a_f = {fc: sosfiltfilt(butter(4, fc, fs=fs, output="sos"), H["ay_palp"]) for fc in (20e3, 50e3)}
    # ---- señales decimadas (la aceleración, filtrada a 50 kHz antes de submuestrear)
    step = max(1, len(H["t"]) // 1500)
    Hs = dict(H)
    Hs["ay_palp"] = a_f[50e3]
    sig = {k: np.round(np.asarray(v[::step], float), 9).tolist() for k, v in Hs.items()}
    # ---- cuadros del golpe a binario: int8 por cuadro con su escala
    U = r["frames"]["u"]                                         # (nf, nv, 3)
    esc = np.maximum(np.abs(U).reshape(len(U), -1).max(axis=1), 1e-15)
    q = np.round(U / esc[:, None, None] * 127).astype(np.int8)
    # presión de flancos en los nodos de esquina (ix par), por cuadro
    PF = r["frames"]["p_flanco"].reshape(len(U), 2, m.nx, m.ny)[:, :, ::2, :]
    p_ref = max(float(PF.max()), 1.0)
    qp = np.round(np.clip(PF / p_ref, 0, 1) * 255).astype(np.uint8)
    WEB.mkdir(parents=True, exist_ok=True)
    # en base64 dentro de un .txt: la página publicada sólo sirve tipos de texto
    (WEB / f"{est.nombre}.b64.txt").write_text(base64.b64encode(q.tobytes() + qp.tobytes()).decode())
    a_g = np.abs(H["ay_palp"]) / 9.81
    res = {
        "nombre": est.nombre, "nivel": est.nivel, "nota": est.nota, "ripple": ripple,
        "x_golpe_mm": x_golpe * 1e3, "x_palp_mm": x_golpe * 1e3 + 10,
        "equilibrio": eq,
        "modos_Hz": [round(float(v), 1) for v in f if v >= 1.0], "modos_rigidos": n_rigidos,
        "golpe": {
            "F_H_max_N": r["F_H_max"], "t_contacto_us": r["t_contacto_us"],
            "E_entrada_mJ": r["E_entrada_mJ"], "E_rebote_mJ": r["E_rebote_mJ"],
            "E_transmitida_mJ": r["E_transmitida_mJ"],
            "a_palp_max_g": float(a_g.max()),
            "a_palp_max_g_50k": float(np.abs(a_f[50e3]).max() / 9.81),
            "a_palp_max_g_20k": float(np.abs(a_f[20e3]).max() / 9.81), "uy_palp_max_um": float(np.abs(H["uy_palp"]).max() * 1e6),
            "frac_flanco_abierto_max": float(H["frac_fl_abierto"].max()),
            "frac_fondo_abierto_max": float(H["frac_fo_abierto"].max()),
            "dt_ns": r["dt"] * 1e9, "pasos": r["n_pasos"],
            "E_rozamiento_mJ": r["E_rozamiento_mJ"], "E_choques_mJ": r["E_choques_mJ"],
            "E_punta_mJ": r["E_punta_mJ"], "restitucion": r["restitucion"], "chi_punta": chi_punta(),
            "E_rayleigh_mJ": r["E_rayleigh_mJ"], "E_cuna_final_mJ": r["E_cuna_final_mJ"],
            "error_balance_energia": r["error_balance_energia"],
            "p_flanco_max_golpe_MPa": r["p_flanco_max_MPa"], "p_diseno_MPa": r["p_diseno_MPa"],
            "F_lateral_max_N": r["F_lateral_max"],
        },
        "tiempo_s": time.time() - t0,
    }
    web = {**res, "senales": sig, "modos": modos,
           "frames_t": r["frames"]["t"].tolist(), "frames_escala": esc.tolist(), "p_flanco_ref": p_ref,
           "n_vis": int(len(nod_vis)),
           "p_flanco_static": np.round(p_l.reshape(2, m.nx, m.ny) / 1e6, 4).tolist(),
           "p_fondo_static": np.round(p_f.reshape(m.nx, m.nz) / 1e6, 4).tolist()}
    with open(WEB / f"{est.nombre}.json", "w") as fh:
        json.dump(web, fh, separators=(",", ":"))
    print(f"{est.nombre:24s} {res['tiempo_s']:6.0f} s  f1={res['modos_Hz'][0] if res['modos_Hz'] else 0:7.0f} Hz  "
          f"E_tr={res['golpe']['E_transmitida_mJ']:.3f} mJ  a={res['golpe']['a_palp_max_g']:.0f} g  "
          f"a50k={res['golpe']['a_palp_max_g_50k']:.0f} g  balance={res['golpe']['error_balance_energia']*100:.2f} %  "
          f"choques={res['golpe']['E_choques_mJ']:.3f} mJ  pmax={res['golpe']['p_flanco_max_golpe_MPa']:.1f} MPa", flush=True)
    return res


def malla_web():
    mod = ModeloCuna()
    nod, tri = nodos_visibles(mod)
    m = mod.m
    # índice, dentro de los nodos visibles, de los nodos de flanco de esquina (para colorear presión)
    pos = {int(n): i for i, n in enumerate(nod)}
    fl = []
    for lado, iz in ((0, m.nz - 1), (1, 0)):
        for ix in range(0, m.nx, 2):
            for iy in range(m.ny):
                fl.append(pos[int(m.nodo(ix, iy, iz))])
    WEB.mkdir(parents=True, exist_ok=True)
    g = mod.g
    with open(WEB / "malla.json", "w") as fh:
        json.dump({"X": np.round(m.X[nod] * 1e3, 4).ravel().tolist(), "tri": tri.ravel().tolist(),
                   "flanco_vis": fl, "nx_vis": len(range(0, m.nx, 2)), "ny": m.ny, "nz": m.nz,
                   "nx": m.nx, "geom": {"L": g.L, "B": g.B, "b": g.b, "e": g.e,
                                        "ne": [g.ne_x, g.ne_y, g.ne_z]},
                   "n_dof": m.n_dof}, fh, separators=(",", ":"))


def main():
    rapido = "--rapido" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    malla_web()
    sel = [a for a in sys.argv[1:] if not a.startswith("--")]
    tareas = [(i, rapido) for i, (e, _, _) in enumerate(ESTADOS) if not sel or e.nombre in sel]
    with Pool(min(4, len(tareas))) as pool:
        res = pool.map(correr, tareas)
    previo = {}
    if (OUT / "resumen.json").exists():
        previo = {r["nombre"]: r for r in json.loads((OUT / "resumen.json").read_text())["estados"]}
    for r in res:
        previo[r["nombre"]] = r
    orden = [e.nombre for e, _, _ in ESTADOS]
    with open(OUT / "resumen.json", "w") as fh:
        json.dump({"estados": [previo[n] for n in orden if n in previo]}, fh, indent=1)


if __name__ == "__main__":
    main()
