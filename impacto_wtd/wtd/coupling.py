"""Acoplamiento del impacto con los modos de la cuña (brief §4.6).

Modelo cerrado:
    eta_0      = 4 m1 m2 / (m1+m2)^2          transferencia ideal por masas
    S(f)/S(0)  = |cos(pi f tc) / (1 - (2 f tc)^2)|   espectro de medio seno
    eta        = eta_0 * [S(f1)/S(0)]^2
    E1         = eta * E_impacto
    a_pk       = w1 * sqrt(2 E1 / m_eff)

Se cruza (ver `wtd.impact_sim`) contra una simulación no lineal completa
martillo-Hertz-modos, que no usa ninguna de estas hipótesis.

Interpretación de eta: fracción de la energía cinética incidente que queda
en el primer modo de la cuña. El coeficiente de restitución del martillo
sale de e = sqrt(1 - eta_total), con eta_total sumada sobre los modos
excitados más las pérdidas locales (plásticas) del contacto.
"""

from __future__ import annotations

import math

import numpy as np


def half_sine_spectrum(f: float | np.ndarray, t_c: float):
    """|S(f)/S(0)| de un pulso de medio seno de duración t_c."""
    u = np.asarray(f, dtype=float) * t_c
    out = np.empty_like(u)
    near = np.abs(np.abs(u) - 0.5) < 1e-6
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.abs(np.cos(math.pi * u) / (1.0 - (2.0 * u) ** 2))
    out = np.where(near, math.pi / 4.0, val)
    return out if out.ndim else float(out)


def mass_ratio_efficiency(m1: float, m2: float) -> float:
    """eta_0 = 4 m1 m2 / (m1+m2)^2."""
    return 4.0 * m1 * m2 / (m1 + m2) ** 2


def modal_coupling(m_hammer: float, m_eff: float, f1: float,
                   t_c: float) -> dict:
    eta0 = mass_ratio_efficiency(m_hammer, m_eff)
    S = half_sine_spectrum(f1, t_c)
    eta = eta0 * S ** 2
    return {"eta_0": eta0, "S_ratio": float(S), "eta": float(eta),
            "f_tc": f1 * t_c}


def modal_response(E_impact: float, m_hammer: float, m_eff: float,
                   f1: float, t_c: float) -> dict:
    """Respuesta del primer modo a un impacto de energía E_impact."""
    c = modal_coupling(m_hammer, m_eff, f1, t_c)
    E1 = c["eta"] * E_impact
    w1 = 2.0 * math.pi * f1
    v_modal = math.sqrt(2.0 * E1 / m_eff)
    a_pk = w1 * v_modal
    x_pk = v_modal / w1
    return {
        **c,
        "E_modal_J": E1,
        "E_modal_mJ": E1 * 1e3,
        "v_modal_ms": v_modal,
        "a_pk_ms2": a_pk,
        "a_pk_g": a_pk / 9.80665,
        "x_pk_um": x_pk * 1e6,
        "restitution_from_eta": math.sqrt(max(0.0, 1.0 - c["eta"])),
    }


def ring_down(f1: float, zeta: float, floor_db: float = -60.0) -> dict:
    """Constante de tiempo y duración útil del ring-down."""
    w1 = 2.0 * math.pi * f1
    tau = 1.0 / (zeta * w1)
    t_floor = -tau * math.log(10.0 ** (floor_db / 20.0))
    n_cycles = t_floor * f1
    Q = 1.0 / (2.0 * zeta)
    return {"tau_s": tau, "tau_ms": tau * 1e3, "Q": Q,
            "t_to_floor_ms": t_floor * 1e3, "n_cycles": n_cycles,
            "half_power_bw_Hz": f1 / Q}


def leeb_index(v_incident: float, v_rebound: float) -> float:
    """Índice Leeb clásico L = 1000 * v_r / v_i."""
    return 1000.0 * v_rebound / v_incident


def optimal_hammer_mass(m_eff: float, f1: float, R: float, E_kin: float,
                        tip, target, m_grid=None) -> dict:
    """Masa de martillo que maximiza la energía entregada al primer modo.

    Hay dos efectos opuestos:
      * eta_0 crece hasta m_hammer = m_eff (transferencia ideal por masas).
      * t_c crece como m^0.4, y el factor espectral S(f1) cae cuando
        f1*t_c pasa de ~0.5  ->  la energía deja de entrar al modo.
    El óptimo depende de f1, es decir DEL VANO DE LA CUÑA.
    """
    from .hertz import hertz_impact

    if m_grid is None:
        m_grid = np.geomspace(0.3e-3, 60e-3, 400)
    best = None
    rows = []
    for m in m_grid:
        h = hertz_impact(E_kin, float(m), R, tip, target)
        r = modal_response(E_kin, float(m), m_eff, f1, h.t_c)
        row = {"m_g": m * 1e3, "t_c_us": h.t_c * 1e6, "eta": r["eta"],
               "E_modal_mJ": r["E_modal_mJ"], "a_pk_g": r["a_pk_g"],
               "p_max_MPa": h.p_max / 1e6, "v_ms": h.v}
        rows.append(row)
        if best is None or row["E_modal_mJ"] > best["E_modal_mJ"]:
            best = row
    return {"best": best, "curve": rows}
