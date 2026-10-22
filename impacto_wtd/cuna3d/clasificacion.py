"""¿Distingue el palpador los 5 niveles de ajuste con seguridad? ¿A qué distancia?

Para cada distancia (5 a 20 mm), precarga (1,0 y 1,3 N), variante de
incertidumbre de la cuña (energía del golpe ±10 %, rigidez de flancos
±30 %) y realización de ruido del sensor, se simula el palpador y se
calculan dos características de la señal del acelerómetro:

  C1  log10(E_b / E_golpe)  energía de la banda 150 Hz - 5 kHz en 3 ms,
      normalizada por la energía del golpe (la mide el impactador).
      Sigue el movimiento lento de la cuña: crece con la soltura.
  C2  f_asiento  centroide espectral entre 12 y 24 kHz en los primeros
      2 ms. Es la vibración de la cuña sobre sus asientos, que llega
      atenuada por la flexura pero muy por encima del ruido, y cuya
      frecuencia sube con la presión de asiento (rigidez de Hertz).

"Con seguridad" se mide como el MARGEN entre niveles vecinos:

    margen = (mín del nivel más flojo - máx del nivel más ajustado) / rango típico

sobre todas las variantes juntas. Margen > 0: los intervalos no se tocan.

Uso:  python -m cuna3d.clasificacion
"""

from __future__ import annotations

import json
import os
import zlib
import sys
from multiprocessing import Pool

import numpy as np
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.distancia import D_MM, DIST, NIVELES, VARIANTES  # noqa: E402
from cuna3d.sensor import ADXL1004, G, M_PUNTA, OUT, Palpador, _flexura  # noqa: E402

M_CARRO = 0.40e-3
PRECARGAS = (1.0, 1.3)
N_RUIDO = 8


def palpador(F0: float, tipo: str = "flexura_liviana") -> Palpador:
    if tipo == "doble_etapa":
        return Palpador(tipo, [M_PUNTA, 0.12e-3, 0.30e-3], [5.0e4, 6.0e4], [0.03, 0.03], F0=F0)
    return Palpador(tipo, [M_PUNTA, M_CARRO], [_flexura(1250, M_CARRO, M_PUNTA, F0)], [0.02], F0=F0)


def caracteristicas(ts, y, E_mJ, banda=(150, 5000)):
    fs = 1 / (ts[1] - ts[0])
    w3 = ts <= 3e-3
    sos = butter(4, list(banda), btype="band", fs=fs, output="sos")
    Eb = float(np.sum(sosfiltfilt(sos, y[w3]) ** 2) / fs * 1e3)
    w2 = (ts > 0.05e-3) & (ts <= 2.05e-3)
    seg = y[w2] * np.hanning(w2.sum())
    A = np.abs(np.fft.rfft(seg, 8 * seg.size)) ** 2
    f = np.fft.rfftfreq(8 * seg.size, 1 / fs)
    b = (f >= 12e3) & (f <= 24e3)
    fc = float(np.sum(f[b] * A[b]) / np.sum(A[b]))
    E_alta = float(np.sum(A[b]))
    return {"C1": float(np.log10(max(Eb, 1e-9) / E_mJ)), "Eb": Eb, "C2": fc, "E_alta": E_alta}


def _caso(arg):
    nivel, var, i_d, F0, tipo = arg
    d = np.load(DIST / f"{nivel}__{var}.npz")
    t, w, vw = d["t"], d["uy"][:, i_d], d["vy"][:, i_d]
    E_mJ = float(d["E"]) * 1e3
    pal = palpador(F0, tipo)
    tt, a, Fc = pal.simular(t, w, vw)
    rng = np.random.default_rng(zlib.crc32(f"{nivel}{var}{i_d}{F0}{tipo}".encode()))
    feats = []
    sat = False
    for _ in range(N_RUIDO):
        ts, y, s_ = ADXL1004.leer(tt, a, rng=rng)
        sat |= s_
        feats.append(caracteristicas(ts, y, E_mJ))
    return {"nivel": nivel, "var": var, "d_mm": float(D_MM[i_d]), "F0": F0, "tipo": tipo,
            "despega": bool(np.any(Fc <= 0)), "Fc_min": float(Fc.min()), "satura": sat,
            "a_pico_g": float(np.abs(a).max() / G),
            "C1": [f["C1"] for f in feats], "C2": [f["C2"] for f in feats]}


def margenes(filas, clave, variantes):
    """Margen entre niveles vecinos para una característica, sobre las variantes dadas."""
    vals = {n: np.concatenate([r[clave] for r in filas if r["nivel"] == n and r["var"] in variantes]) for n in NIVELES}
    rango = np.median([np.ptp(v) for v in vals.values()]) + 1e-12
    out = []
    for a, b in zip(NIVELES, NIVELES[1:]):
        va, vb = vals[a], vals[b]
        if clave == "C1":       # sube con la soltura
            gap = vb.min() - va.max()
        else:                   # C2 baja con la soltura
            gap = va.min() - vb.max()
        out.append({"par": f"{a}/{b}", "gap": float(gap), "margen": float(gap / rango),
                    "a": [float(va.min()), float(va.max())], "b": [float(vb.min()), float(vb.max())]})
    return out


def main():
    tipos = ["flexura_liviana", "doble_etapa"]
    tareas = [(n, v, i, F0, tp) for tp in tipos for n in NIVELES for v in VARIANTES
              for i in range(len(D_MM)) for F0 in PRECARGAS if not (tp == "doble_etapa" and F0 != 1.0)]
    with Pool(4) as pool:
        filas = pool.map(_caso, tareas, chunksize=4)
    todas = list(VARIANTES)
    sin_k = ["base", "E-10", "E+10"]
    resumen = {}
    for tp in tipos:
        for i, d in enumerate(D_MM):
            fs = [r for r in filas if r["tipo"] == tp and r["d_mm"] == d]
            desp = [r for r in fs if r["despega"]]
            res = {"despega_en": sorted({f"{r['nivel']}·{r['var']}·{r['F0']}N" for r in desp}),
                   "Fc_min_N": min(r["Fc_min"] for r in fs),
                   "Fc_min_1N": min(r["Fc_min"] for r in fs if r["F0"] == 1.0),
                   "satura": any(r["satura"] for r in fs),
                   "C1_todas": margenes(fs, "C1", todas), "C2_todas": margenes(fs, "C2", todas),
                   "C1_k_conocida": margenes(fs, "C1", sin_k), "C2_k_conocida": margenes(fs, "C2", sin_k)}
            resumen[f"{tp}@{d:.1f}"] = res
            m1 = [m["margen"] for m in res["C1_todas"]]
            m2 = [m["margen"] for m in res["C2_todas"]]
            m2k = [m["margen"] for m in res["C2_k_conocida"]]
            print(f"{tp:16s} d={d:4.1f} mm  despega={len(desp):2d}  Fc_min(1 N)={res['Fc_min_1N']:.3f} N  "
                  f"C1 márgenes={np.round(m1, 2)}  C2={np.round(m2, 2)}  C2(k conocida)={np.round(m2k, 2)}", flush=True)
    with open(OUT / "clasificacion.json", "w") as fh:
        json.dump({"filas": filas, "resumen": resumen, "d_mm": D_MM.tolist(), "niveles": NIVELES,
                   "variantes": VARIANTES}, fh)


if __name__ == "__main__":
    main()
