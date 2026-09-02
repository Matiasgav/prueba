"""Presupuesto de repetibilidad por Monte Carlo.

La pregunta que responde: ¿cuánto varía la energía entregada tiro a tiro, y
qué tolerancia hay que apretar para llegar al 1 %?

Y la pregunta que responde DESPUÉS, que es la que importa: dado que el sensor
inductivo MIDE la velocidad de impacto, ¿cuánto de esa dispersión sobrevive
en la magnitud reportada? La respuesta cambia el diseño: si la energía se
mide, la repetibilidad del lanzador deja de ser un requisito de fabricación y
pasa a ser un requisito de RANGO del sensor.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .materials import G


@dataclass
class ToleranceSpec:
    """Tolerancias de fabricación y de operación (1 sigma salvo aclaración)."""

    # acumulador
    k_rel: float = 0.03            # rigidez del resorte / barra, +-3 % (1s)
    cock_abs: float = 20e-6        # posición de amartillado [m]
    preload_rel: float = 0.03      # precarga remanente
    # tren mecánico
    mu_guide: tuple = (0.10, 0.04)  # (media, sigma) coef. de fricción
    normal_load: float = 0.15      # carga normal parásita en la guía [N]
    release_rel: float = 0.02      # dispersión del disparo (traba)
    # entorno
    temp_C: tuple = (35.0, 15.0)   # (media, sigma) temperatura [C]
    dG_dT: float = -2.5e-4         # variación relativa de G por grado
    clock_deg: tuple = (0.0, 180.0)  # posición horaria: uniforme 0-360
    # geometría de operación
    gap: tuple = (3.0e-3, 0.3e-3)  # (media, sigma) separación módulo-cuña
    tilt_deg: tuple = (0.0, 1.5)   # inclinación del crawler -> oblicuidad
    # medición
    sensor_sigma_v_rel: float = 0.0015   # error relativo de v medida


@dataclass
class LauncherPoint:
    """Punto de diseño nominal del lanzador."""

    m_proj: float = 8e-3
    k: float = 300.0             # rigidez reducida al proyectil [N/m]
    stroke: float = 22e-3
    preload_force: float = 3.5
    m_drive_eff: float = 0.6e-3  # masa efectiva del acumulador [kg]

    def energy(self, k: float, stroke: float, preload: float) -> float:
        return 0.5 * k * stroke ** 2 + preload * stroke


def run(point: LauncherPoint, tol: ToleranceSpec, n: int = 200_000,
        seed: int = 20260902) -> dict:
    rng = np.random.default_rng(seed)

    k = point.k * (1.0 + tol.k_rel * rng.standard_normal(n))
    stroke = point.stroke + tol.cock_abs * rng.standard_normal(n)
    preload = point.preload_force * (1.0 + tol.preload_rel
                                     * rng.standard_normal(n))
    mu = np.clip(tol.mu_guide[0] + tol.mu_guide[1] * rng.standard_normal(n),
                 0.01, 0.5)
    T = tol.temp_C[0] + tol.temp_C[1] * rng.standard_normal(n)
    k = k * (1.0 + tol.dG_dT * (T - 20.0))
    clock = rng.uniform(0.0, 360.0, n)
    gap = np.clip(tol.gap[0] + tol.gap[1] * rng.standard_normal(n),
                  1.0e-3, 6e-3)
    tilt = np.deg2rad(tol.tilt_deg[0] + tol.tilt_deg[1]
                      * rng.standard_normal(n))
    rel = 1.0 + tol.release_rel * rng.standard_normal(n)

    # energía almacenada
    E_stored = (0.5 * k * stroke ** 2 + preload * stroke) * rel
    # pérdidas por fricción sobre la carrera
    E_fric = mu * tol.normal_load * stroke
    # trabajo de la gravedad sobre carrera + vuelo
    a_g = -G * np.cos(np.deg2rad(clock))
    E_grav = point.m_proj * a_g * (stroke + gap)
    E_kin = np.maximum(E_stored - E_fric + E_grav, 1e-9)
    # reparto con la masa del acumulador
    E_proj = E_kin * point.m_proj / (point.m_proj + point.m_drive_eff)
    v = np.sqrt(2.0 * E_proj / point.m_proj)
    # componente normal (oblicuidad por inclinación del crawler)
    E_normal = E_proj * np.cos(tilt) ** 2

    # energía REPORTADA: la que mide el sensor a partir de v
    v_meas = v * (1.0 + tol.sensor_sigma_v_rel * rng.standard_normal(n))
    E_meas = 0.5 * point.m_proj * v_meas ** 2

    def stats(x, name):
        return {"nombre": name, "media": float(x.mean()),
                "sigma": float(x.std()),
                "cv_pct": float(100.0 * x.std() / abs(x.mean())),
                "p05": float(np.percentile(x, 5)),
                "p95": float(np.percentile(x, 95))}

    # sensibilidad: correlación de cada entrada con la energía normal
    inputs = {"rigidez k": k, "carrera (amartillado)": stroke,
              "precarga": preload, "fricción µ": mu, "temperatura": T,
              "posición horaria": np.cos(np.deg2rad(clock)),
              "separación (gap)": gap, "inclinación": np.abs(tilt),
              "disparo (traba)": rel}
    sens = []
    y = E_normal
    for name, x in inputs.items():
        sx = x.std()
        if sx < 1e-15:
            continue
        r = float(np.corrcoef(x, y)[0, 1])
        # contribución a la varianza por regresión lineal estandarizada
        beta = r * y.std() / sx
        sens.append({"variable": name, "corr": r,
                     "contrib_var_pct": 100.0 * r ** 2})
    sens.sort(key=lambda d: -abs(d["contrib_var_pct"]))

    return {
        "n": n,
        "E_almacenada_mJ": stats(E_stored * 1e3, "energía almacenada"),
        "E_proyectil_mJ": stats(E_proj * 1e3, "energía del proyectil"),
        "E_normal_mJ": stats(E_normal * 1e3, "energía normal al impacto"),
        "E_medida_mJ": stats(E_meas * 1e3, "energía medida por el sensor"),
        "v_ms": stats(v, "velocidad de impacto"),
        # LO QUE IMPORTA: el lanzador dispersa un 3 %, pero el sensor sabe
        # cuánto disparó. El error que sobrevive en la magnitud REPORTADA es
        # el del sensor, no el del lanzador.
        "error_residual_medicion_pct": float(
            100.0 * np.std((E_meas - E_proj) / E_proj)),
        "cv_lanzador_pct": float(100.0 * E_proj.std() / E_proj.mean()),
        "sensibilidad": sens,
    }


def tolerance_targets(point: LauncherPoint, tol: ToleranceSpec,
                      target_cv: float = 1.0, n: int = 60_000) -> list[dict]:
    """¿Qué tolerancia hay que apretar y cuánto para llegar al objetivo?

    Se apaga una fuente por vez y se mide cuánto baja el CV. Eso da el orden
    de ataque; después se busca el factor de apriete necesario en la
    dominante.
    """
    base = run(point, tol, n=n)["E_normal_mJ"]["cv_pct"]
    rows = [{"variable": "TODAS (base)", "cv_pct": base, "delta_pct": 0.0}]
    fields = {
        "rigidez k": ("k_rel", 0.0),
        "carrera (amartillado)": ("cock_abs", 0.0),
        "precarga": ("preload_rel", 0.0),
        "fricción µ": ("mu_guide", (0.10, 0.0)),
        "temperatura": ("temp_C", (35.0, 0.0)),
        "posición horaria": ("clock_deg", (0.0, 0.0)),
        "separación (gap)": ("gap", (3.0e-3, 0.0)),
        "inclinación": ("tilt_deg", (0.0, 0.0)),
        "disparo (traba)": ("release_rel", 0.0),
    }
    for name, (attr, val) in fields.items():
        import copy
        t2 = copy.deepcopy(tol)
        setattr(t2, attr, val)
        if name == "posición horaria":
            # fijar la hora en el peor caso no es realista: se fija a 3 en punto
            t2.clock_deg = (90.0, 0.0)
        cv = run(point, t2, n=n)["E_normal_mJ"]["cv_pct"]
        rows.append({"variable": f"sin {name}", "cv_pct": cv,
                     "delta_pct": base - cv})
    rows[1:] = sorted(rows[1:], key=lambda r: -r["delta_pct"])
    return rows
