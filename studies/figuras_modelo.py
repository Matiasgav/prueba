"""Datos de las figuras del modelo integrado, y verificacion de los barridos.

Salida: results/figuras_modelo.json

Hace dos cosas:

1. Produce los datos que dibujan las figuras de `docs/MODELO.md` y del
   artefacto publicado: la escalera S0-S6 con las dos magnitudes que la
   ordenan y la que no, las trazas del acelerometro, la firma del despegue,
   el optimo de energia del golpe y la curva K_F del LAH04.

2. Recalcula los barridos de zeta y de f0 REUSANDO las trazas de la cuña.
   La cuña no depende del palpador, asi que alcanza con simular una vez por
   (energia, estado) y despues aplicarle cada palpador: un barrido que
   simulado entero tarda horas, aca tarda minutos.

   Esa reutilizacion es lo que permite VERIFICAR que `F0_SWEEP_FLEXURA` y
   `ZETA_SWEEP` siguen siendo lo que da el codigo vigente -- y es lo que
   encontro que el default de `x_wedge_max` en `design()` devolvia un
   palpador de 1820 Hz mientras todo el documento decia 1273.

LA METRICA DE SEPARACION, que las tablas publicadas usan sin decirlo:

    separacion = min( sobre los estados SUELTOS de int a^2 dt )
                 / max( sobre los estados ASENTADOS )

    tomada en la PEOR de las seis energias de golpe, que siempre es 12 mJ.

Con el palpador de diseño (f0 = 1273 Hz, zeta = 0.02) da x112, que es el
numero publicado.
"""

from __future__ import annotations

import json
import math
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wtd.actuator import LAH04_CURVE_F, LAH04_CURVE_X
from wtd.impact_sim import HammerSpec, SimConfig, simulate
from wtd.softprobe import (G, SoftProbe, apply_soft_probe, design,
                           probe_features)
from wtd.wedge import WedgeSpec, standard_states

OUT = pathlib.Path(__file__).resolve().parent.parent / "results"
WEDGE = WedgeSpec()
HAMMER = HammerSpec(mass=4.0e-3)
X_STRIKE = WEDGE.span / 2.0
DIST = 12.5e-3
ENERGIES = (1.0, 2.0, 3.0, 5.0, 8.0, 12.0)
ZETA = 0.02                      # el del diseño


def v_of(E_mJ: float) -> float:
    return float((2.0 * E_mJ * 1e-3 / HAMMER.mass) ** 0.5)


def wedge_traces(E_mJ: float) -> list[tuple[str, np.ndarray, float]]:
    """Los siete estados a una energia. Es la parte cara: se cachea."""
    out = []
    for s in standard_states():
        r = simulate(WEDGE, s, HAMMER, v_of(E_mJ),
                     SimConfig(x_strike=X_STRIKE, x_palpator=X_STRIKE - DIST,
                               t_end=3.0e-3))
        out.append((s.label, r["w_palp"], r["dt_rec"]))
    return out


def separation(traces, probe_of) -> dict:
    """La metrica de las tablas publicadas, sobre un juego de trazas."""
    sig, pico, lift = [], [], False
    for _lab, w, dt in traces:
        o = apply_soft_probe(w, dt, probe_of())
        f = probe_features(o["a_palpador"], dt)
        sig.append(f["energia_g2ms"])
        pico.append(f["pico_g"])
        lift = lift or o["despega"]
    return {"sep": min(sig[4:]) / max(sig[:3]),
            "sep_pico": min(pico[4:]) / max(pico[:3]),
            "a_max": max(pico), "despega": lift}


def main() -> dict:
    res: dict = {}
    base = design()
    res["palpador"] = {"f0_Hz": base.f0(), "k_series_N_mm": base.k_series() / 1e3,
                       "m_g": base.mass * 1e3, "zeta": ZETA}

    cache = {E: wedge_traces(E) for E in ENERGIES}

    # ---- 1. La escalera a 5 mJ: lo que ordena y lo que no --------------
    #  a_cuña NO es monotona (pasa por 4808 g en S3 y baja a 1062 en S6);
    #  la excursion SI. Es el argumento de fondo contra medir la
    #  aceleracion cruda de la cuña, y no depende de la precarga.
    esc = []
    p = design(); p.zeta = ZETA
    for lab, w, dt in cache[5.0]:
        o = apply_soft_probe(w, dt, p)
        f = probe_features(o["a_palpador"], dt)
        a = np.gradient(np.gradient(w, dt), dt)
        esc.append({"estado": lab.split("·")[0].strip(),
                    "x_um": float(np.max(np.abs(w)) * 1e6),
                    "a_cuña_g": float(np.max(np.abs(a)) / G),
                    "lectura_g": f["pico_g"],
                    "rasgo_g2ms": f["energia_g2ms"]})
    res["escalera_5mJ"] = esc

    # ---- 2. Las trazas que se verian en un osciloscopio ----------------
    tr = {}
    for idx, key in ((0, "S0"), (3, "S3"), (6, "S6")):
        lab, w, dt = cache[5.0][idx]
        o = apply_soft_probe(w, dt, p)
        a = o["a_palpador"] / G
        step = max(1, len(a) // 500)
        tr[key] = {"estado": lab, "dt_ms": dt * step * 1e3,
                   "a_g": [round(float(x), 2) for x in a[::step]],
                   "rasgo": probe_features(o["a_palpador"], dt)}
    res["trazas_5mJ"] = tr

    # ---- 3. La firma del despegue: el riel plano en -F/m ---------------
    #  En vuelo la unica fuerza sobre el carro es la precarga, asi que la
    #  lectura se clava EXACTAMENTE en -F/m. Se busca la punta mas liviana
    #  que lo produzca con el golpe mas fuerte.
    _lab, w12, dt12 = cache[12.0][6]
    lift = None
    for t_mg in (20, 30, 40, 50, 60, 80, 120, 200, 400):
        pl = design(); pl.zeta = ZETA; pl.tip_mass = t_mg * 1e-6
        o = apply_soft_probe(w12, dt12, pl)
        if o["despega"]:
            n = int(0.25e-3 / dt12)
            a = o["a_palpador"] / G
            ref = apply_soft_probe(w12, dt12, p)["a_palpador"] / G
            lift = {"tip_mg": t_mg, "frac_pct": o["frac_despegado"] * 100,
                    "riel_g": p.a_liftoff() / G, "dt_ms": dt12 * 1e3,
                    "a_g": [round(float(x), 2) for x in a[:n]],
                    "ref_g": [round(float(x), 2) for x in ref[:n]]}
            break
    res["despegue_12mJ"] = lift

    # ---- 4. El optimo de energia del golpe -----------------------------
    #  Techo: con el golpe fuerte hasta la cuña ajustada despega del hombro.
    #  Piso: a 1 mJ S0 devuelve mas señal que S1 y S2 y deja de ordenar.
    ener = []
    for E in ENERGIES:
        sig = []
        for _lab, w, dt in cache[E]:
            o = apply_soft_probe(w, dt, p)
            sig.append(probe_features(o["a_palpador"], dt)["energia_g2ms"])
        ener.append({"E_mJ": E, "sep": min(sig[4:]) / max(sig[:3]),
                     "salto_S3_S4": sig[4] / sig[3]})
    res["energia_golpe"] = ener

    # ---- 5. K_F(x) del LAH04: el maximo esta en el centro --------------
    res["kf_lah04"] = {"x_mm": [float(x) * 1e3 for x in LAH04_CURVE_X],
                       "F_N_A": [float(f) for f in LAH04_CURVE_F]}

    # ---- 6. Verificacion de las tablas publicadas ----------------------
    kh = SoftProbe(mass=base.mass, k_soft=1e9, preload=1.0).k_hertz()
    zs, fs = [], []
    for z in (0.002, 0.005, 0.010, 0.020, 0.050, 0.080, 0.150, 0.300):
        rows = [separation(cache[E], lambda z=z: SoftProbe(
            mass=base.mass, k_soft=base.k_soft, preload=1.0, zeta=z))
            for E in ENERGIES]
        zs.append({"zeta": z, "a_max": max(r["a_max"] for r in rows),
                   "sep_min": min(r["sep"] for r in rows),
                   "despega": any(r["despega"] for r in rows)})
    for f0 in (600, 800, 1000, 1273, 1600, 2000, 2500, 3200, 4000):
        k = base.mass * (2 * math.pi * f0) ** 2
        if k >= kh:
            continue
        ks = 1.0 / (1.0 / k - 1.0 / kh)
        rows = [separation(cache[E], lambda ks=ks: SoftProbe(
            mass=base.mass, k_soft=ks, preload=1.0, zeta=0.005))
            for E in ENERGIES]
        fs.append({"f0_Hz": f0, "a_max": max(r["a_max"] for r in rows),
                   "sep_min": min(r["sep"] for r in rows)})
    res["barrido_zeta"] = zs
    res["barrido_f0"] = fs
    return res


if __name__ == "__main__":        # pragma: no cover
    out = main()
    OUT.mkdir(exist_ok=True)
    (OUT / "figuras_modelo.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False, default=float))

    print("PALPADOR", {k: round(v, 3) for k, v in out["palpador"].items()})
    print("\nESCALERA a 5 mJ")
    for r in out["escalera_5mJ"]:
        print(f"  {r['estado']:>3}  x {r['x_um']:6.2f} um   "
              f"a_cuña {r['a_cuña_g']:7.0f} g   lectura {r['lectura_g']:6.1f} g")
    print("\nENERGIA DEL GOLPE")
    for r in out["energia_golpe"]:
        print(f"  {r['E_mJ']:5.1f} mJ   separacion x{r['sep']:7.1f}   "
              f"salto S3|S4 x{r['salto_S3_S4']:7.1f}")
    d = out["despegue_12mJ"]
    print(f"\nDESPEGUE: punta de {d['tip_mg']} mg -> {d['frac_pct']:.2f} % "
          f"de las muestras clavadas en -{d['riel_g']:.0f} g")
    print("\nVERIFICACION DE LAS TABLAS PUBLICADAS")
    for r in out["barrido_zeta"]:
        print(f"  zeta {r['zeta']:<6} a_max {r['a_max']:6.1f} g  "
              f"sep x{r['sep_min']:6.1f}")
    for r in out["barrido_f0"]:
        print(f"  f0 {r['f0_Hz']:<5} a_max {r['a_max']:6.1f} g  "
              f"sep x{r['sep_min']:6.1f}")
