"""Palpador de acople blando con 1 N de precarga: sintesis y verificacion.

Responde la pregunta de diseño: como medir la cuña a 10-15 mm del golpe
cuando la precarga disponible es 1 N como maximo.

Salida: results/softprobe.json
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wtd.impact_sim import HammerSpec, SimConfig, simulate
from wtd.palpator import ACELEROMETROS, noise_floor
from wtd.softprobe import (G, SoftProbe, apply_soft_probe, design,
                           noise_in_feature, probe_features)
from wtd.wedge import WedgeSpec, standard_states

OUT = pathlib.Path(__file__).resolve().parent.parent / "results"
WEDGE = WedgeSpec()
HAMMER = HammerSpec(mass=4.0e-3)
X_STRIKE = WEDGE.span / 2.0
DIST = (10e-3, 12.5e-3, 15e-3)          # distancias al golpe
ENERGIES = (1.0, 2.0, 3.0, 5.0, 8.0, 12.0)   # [mJ]


def v_of(E_mJ: float) -> float:
    return float((2.0 * E_mJ * 1e-3 / HAMMER.mass) ** 0.5)


def run_wedge(dist: float, E_mJ: float) -> list[dict]:
    """Simula los 7 estados y devuelve el movimiento en el palpador."""
    out = []
    for s in standard_states():
        r = simulate(WEDGE, s, HAMMER, v_of(E_mJ),
                     SimConfig(x_strike=X_STRIKE, x_palpator=X_STRIKE - dist,
                               t_end=3.0e-3))
        out.append({"label": s.label, "w": r["w_palp"], "dt": r["dt_rec"],
                    "E_abs_mJ": r["E_absorbed_mJ"], "leeb": r["leeb"]})
    return out


# --------------------------------------------------------------------------

def main() -> dict:
    res: dict = {}

    # ---- 1. Cuanto se mueve la cuña, y con que magnitud discriminar ----
    # El punto de partida: el pico de ACELERACION no es monotono con la
    # soltura, el de DESPLAZAMIENTO si. Es lo que decide toda la arquitectura
    # del palpador.
    motion = {}
    for d in DIST:
        rows = []
        for E in ENERGIES:
            for st in run_wedge(d, E):
                w = st["w"]
                vw = np.gradient(w, st["dt"])
                aw = np.gradient(vw, st["dt"])
                rows.append({
                    "E_mJ": E, "estado": st["label"],
                    "x_pico_um": float(np.abs(w).max()) * 1e6,
                    "v_pico_ms": float(np.abs(vw).max()),
                    "a_pico_g": float(np.abs(aw).max()) / G,
                    "E_abs_mJ": st["E_abs_mJ"],
                })
        motion[f"{d*1e3:.1f}mm"] = rows
    res["movimiento_cuña"] = motion

    # monotonia: numero de inversiones en la escalera S0->S6
    def inversions(vals: list[float]) -> int:
        return sum(1 for a, b in zip(vals, vals[1:]) if b < a)

    mono = []
    for d in DIST:
        for E in ENERGIES:
            rows = [r for r in motion[f"{d*1e3:.1f}mm"] if r["E_mJ"] == E]
            mono.append({
                "dist_mm": d * 1e3, "E_mJ": E,
                "inv_desplazamiento": inversions([r["x_pico_um"] for r in rows]),
                "inv_aceleracion": inversions([r["a_pico_g"] for r in rows]),
                "rango_desplazamiento": (max(r["x_pico_um"] for r in rows)
                                         / min(r["x_pico_um"] for r in rows)),
                "rango_aceleracion": (max(r["a_pico_g"] for r in rows)
                                      / min(r["a_pico_g"] for r in rows)),
            })
    res["monotonia"] = mono

    # ---- 2. Sintesis del palpador -------------------------------------
    x_max = max(r["x_pico_um"] for rows in motion.values() for r in rows) * 1e-6
    probe = design(preload=1.0, a_liftoff_g=150.0,
                   x_wedge_max=x_max * 1.15, a_full_scale_g=100.0)
    res["x_cuña_max_um"] = x_max * 1e6
    res["palpador"] = probe.summary()

    # ---- 3. Verificacion en el tiempo, todos los casos -----------------
    check = []
    for d in DIST:
        for E in ENERGIES:
            for st in run_wedge(d, E):
                o = apply_soft_probe(st["w"], st["dt"], probe)
                check.append({
                    "dist_mm": d * 1e3, "E_mJ": E, "estado": st["label"],
                    "E_abs_mJ": st["E_abs_mJ"],
                    "x_real_um": o["x_pico_cuña_um"],
                    "x_est_um": o["x_estimado_um"],
                    "a_leida_g": o["a_pico_palpador_g"],
                    "a_cuña_g": o["a_pico_cuña_g"],
                    "margen": o["margen_despegue"],
                    "despega": o["despega"],
                })
    res["verificacion"] = check
    res["despegues"] = sum(1 for c in check if c["despega"])
    res["n_casos"] = len(check)
    res["a_leida_min_g"] = min(c["a_leida_g"] for c in check)
    res["a_leida_max_g"] = max(c["a_leida_g"] for c in check)
    # sesgo de la inversion: el pico dinamico supera al cuasi-estatico
    ratio = [c["x_est_um"] / c["x_real_um"] for c in check]
    res["sesgo_inversion"] = {"min": min(ratio), "max": max(ratio),
                              "mediana": float(np.median(ratio))}

    # ---- 4. Sensibilidad a la precarga ---------------------------------
    # El crawler no puede sostener la precarga con precision. La ganancia
    # omega_n^2 = k_serie/m depende de la precarga SOLO por el termino de
    # Hertz, que aporta ~5 % de la flexibilidad: la lectura casi no se entera.
    sens = []
    base_gain = probe.gain()
    for F in (0.5, 0.7, 1.0, 1.3, 1.5):
        p = SoftProbe(mass=probe.mass, k_soft=probe.k_soft, preload=F,
                      zeta=probe.zeta, tip_radius=probe.tip_radius)
        sens.append({"F_N": F, "f0_Hz": p.f0(),
                     "ganancia_rel": p.gain() / base_gain,
                     "a_despegue_g": p.a_liftoff() / G,
                     "x_despegue_um": p.x_liftoff() * 1e6})
    res["sensibilidad_precarga"] = sens

    # ---- 5. Barrido del espacio de diseño ------------------------------
    grid = []
    for m_g in (0.4, 0.5, 0.68, 0.8, 1.0):
        for f0_Hz in (800.0, 1200.0, 1820.0, 2500.0, 3500.0):
            m = m_g * 1e-3
            k_ser = m * (2 * np.pi * f0_Hz) ** 2
            p = SoftProbe(mass=m, k_soft=k_ser, preload=1.0)
            kh = p.k_hertz()
            if k_ser >= kh:
                continue
            p.k_soft = 1.0 / (1.0 / k_ser - 1.0 / kh)
            o = [apply_soft_probe(st["w"], st["dt"], p)
                 for st in run_wedge(12.5e-3, 12.0)]
            grid.append({
                "m_g": m_g, "f0_Hz": f0_Hz,
                "k_soft_N_mm": p.k_soft * 1e-3,
                "a_despegue_g": p.a_liftoff() / G,
                "x_despegue_um": p.x_liftoff() * 1e6,
                "a_max_leida_g": max(x["a_pico_palpador_g"] for x in o),
                "despega": any(x["despega"] for x in o),
                "flecha_estatica_um": p.static_deflection() * 1e6,
            })
    res["espacio_diseño"] = grid

    # ---- 6. Eleccion del acelerometro ----------------------------------
    # Ancho de banda util: el palpador ya filtra, no hace falta mas de ~5 kHz.
    bw = 5.0e3
    a_min = res["a_leida_min_g"]
    sensors = []
    for name, rng, sbw, dens, m_g in ACELEROMETROS:
        n = noise_floor(dens, min(sbw, bw))
        sensors.append({
            "sensor": name, "rango_g": rng, "masa_g": m_g,
            "ruido_g_rms": n,
            "SNR_peor_caso_dB": 20 * float(np.log10(a_min / n)),
            "entra_en_masa": m_g <= probe.mass * 1e3 * 0.6,
            "satura": res["a_leida_max_g"] > rng,
        })
    res["acelerometros"] = sensors
    res["bw_util_Hz"] = bw

    # ---- 6b. Que lectura separa mejor -----------------------------------
    # Se compara pico contra energia de la señal. La metrica que importa no
    # es la monotonia fina de la escalera sino la SEPARACION entre el grupo
    # asentado (S0-S2) y el suelto (S4-S6), que es la pregunta del ensayo.
    read = []
    for E in ENERGIES:
        cols: dict[str, list[float]] = {"pico_g": [], "energia_g2ms": [],
                                        "abs_int_g_ms": []}
        for st in run_wedge(12.5e-3, E):
            o = apply_soft_probe(st["w"], st["dt"], probe)
            f = probe_features(o["a_palpador"], st["dt"])
            for k in cols:
                cols[k].append(f[k])
        row = {"E_mJ": E}
        for k, v in cols.items():
            row[k] = v
            row[f"sep_{k}"] = min(v[4:]) / max(v[:3])
        read.append(row)
    res["lectura"] = read
    res["ruido_lectura"] = noise_in_feature(75e-6, bw, 3.0e-3)

    # ---- 7. Discriminacion: se separan los estados? ---------------------
    # A energia conocida (la mide el sensor inductivo del proyectil), la
    # lectura del palpador ordena los estados. Se reporta el salto relativo
    # entre estados contiguos a 12.5 mm.
    disc = []
    for E in ENERGIES:
        rows = [c for c in check if c["dist_mm"] == 12.5 and c["E_mJ"] == E]
        a = [r["a_leida_g"] for r in rows]
        disc.append({
            "E_mJ": E,
            "lecturas_g": a,
            "rango": max(a) / min(a),
            "min_salto_rel": min(b / x for x, b in zip(a, a[1:])),
            "monotona": all(b >= x for x, b in zip(a, a[1:])),
        })
    res["discriminacion"] = disc

    return res


if __name__ == "__main__":
    out = main()
    OUT.mkdir(exist_ok=True)
    (OUT / "softprobe.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False, default=float))

    p = out["palpador"]
    print("PALPADOR DE ACOPLE BLANDO")
    for k in ("m_g", "k_soft_N_mm", "k_series_N_mm", "frac_hertz_pct",
              "f0_Hz", "ganancia_g_por_um", "a_despegue_g", "x_despegue_um"):
        print("  %-20s %10.2f" % (k, p[k]))
    print("\nVERIFICACION  %d casos, %d despegues, lectura %.1f - %.1f g"
          % (out["n_casos"], out["despegues"],
             out["a_leida_min_g"], out["a_leida_max_g"]))
    s = out["sesgo_inversion"]
    print("  sesgo de la inversion x_est/x_real: %.2f - %.2f (mediana %.2f)"
          % (s["min"], s["max"], s["mediana"]))

    print("\nMONOTONIA (inversiones en la escalera S0->S6, sobre %d casos)"
          % len(out["monotonia"]))
    print("  desplazamiento: %d    aceleracion: %d"
          % (sum(m["inv_desplazamiento"] for m in out["monotonia"]),
             sum(m["inv_aceleracion"] for m in out["monotonia"])))

    print("\nSENSIBILIDAD A LA PRECARGA")
    for r in out["sensibilidad_precarga"]:
        print("  F=%.1f N  f0=%6.0f Hz  ganancia x%.4f  despegue %5.0f g"
              % (r["F_N"], r["f0_Hz"], r["ganancia_rel"], r["a_despegue_g"]))

    print("\nDISCRIMINACION a 12.5 mm")
    for d in out["discriminacion"]:
        print("  E=%5.1f mJ  rango x%5.1f  salto min x%.2f  monotona %s"
              % (d["E_mJ"], d["rango"], d["min_salto_rel"], d["monotona"]))

    print("\nSEPARACION ASENTADA (S0-S2) | SUELTA (S4-S6), segun la lectura")
    print("  %-8s %10s %10s %10s" % ("E [mJ]", "pico", "energia", "abs int"))
    for r in out["lectura"]:
        print("  %-8.1f %10.1f %10.1f %10.1f"
              % (r["E_mJ"], r["sep_pico_g"], r["sep_energia_g2ms"],
                 r["sep_abs_int_g_ms"]))
    n = out["ruido_lectura"]
    print("  piso de ruido (ADXL1005, 5 kHz, 3 ms): %.2e g^2 ms"
          % n["energia_g2ms"])
