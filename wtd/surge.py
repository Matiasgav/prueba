"""Surge del resorte: ¿el acumulador entrega su energía de forma coherente?

Un resorte helicoidal NO es un elemento sin masa. Al soltarlo, la
perturbación viaja como una onda longitudinal a lo largo del alambre. Si el
tiempo de lanzamiento no es mucho mayor que el tiempo de tránsito de esa
onda, parte de la energía queda oscilando dentro del resorte y no llega al
proyectil.

El modelo de "masa efectiva = m_resorte/3" supone perfil de velocidad lineal,
o sea tránsito instantáneo. Acá se comprueba con un modelo distribuido de N
masas y N resortes, y se mide el error del modelo simplificado.

Referencia de contexto: la sonda Leeb D del estándar ISO 16859 trabaja
exactamente en este régimen (relación tiempo de lanzamiento / período de
surge ~2) y su repetibilidad publicada es del orden del 0.5 %. O sea que el
régimen es utilizable; lo que no se puede es ignorarlo.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.integrate import solve_ivp


def simulate_distributed_spring(k: float, m_spring: float, m_proj: float,
                                x_cock: float, x_release: float = 0.0,
                                preload_force: float = 0.0,
                                N: int = 40) -> dict:
    """Lanzamiento con el resorte discretizado en N tramos.

    Extremo 0 anclado al chasis; extremo N unido (contacto unilateral) al
    proyectil. Cada tramo tiene rigidez N*k y masa m_spring/N.
    """
    k_seg = N * k
    m_seg = m_spring / N
    # coordenadas: u[0..N-1] son las masas del resorte, u[N] el proyectil.
    # Estado inicial: resorte comprimido uniformemente.
    n_dof = N + 1
    u0 = np.zeros(n_dof)
    total_defl = x_cock - x_release
    for i in range(n_dof):
        u0[i] = -total_defl * (i / N)
    v0 = np.zeros(n_dof)
    masses = np.full(n_dof, m_seg)
    masses[-1] = m_proj + m_seg / 2.0

    def rhs(t, y):
        u = y[:n_dof]
        v = y[n_dof:]
        # elongación de cada tramo respecto de la longitud libre
        du = np.diff(np.concatenate(([0.0], u)))
        f_seg = k_seg * du + preload_force
        a = np.zeros(n_dof)
        a[:-1] = (f_seg[1:] - f_seg[:-1]) / masses[:-1]
        # el último tramo empuja al proyectil sólo si está en compresión
        f_last = f_seg[-1]
        a[-1] = (-f_last) / masses[-1] if f_last < 0 else 0.0
        return np.concatenate([v, a])

    def separation(t, y):
        u = y[:n_dof]
        du = np.diff(np.concatenate(([0.0], u)))
        return (k_seg * du[-1] + preload_force)
    separation.terminal = True
    separation.direction = 1

    sol = solve_ivp(rhs, (0.0, 0.2), np.concatenate([u0, v0]),
                    events=separation, rtol=1e-9, atol=1e-12, max_step=1e-5)
    if sol.t_events[0].size:
        t_sep = float(sol.t_events[0][0])
        v_proj = float(sol.y_events[0][0][-1])
    else:
        t_sep = float(sol.t[-1])
        v_proj = float(sol.y[-1, -1])

    E_stored = 0.5 * k * total_defl ** 2 + preload_force * total_defl
    E_proj = 0.5 * m_proj * v_proj ** 2
    # modelo simplificado
    v_simple = math.sqrt(2.0 * E_stored / (m_proj + m_spring / 3.0))
    E_simple = 0.5 * m_proj * v_simple ** 2
    f_surge = 0.5 * math.sqrt(k / m_spring)
    return {
        "N": N,
        "v_proj_ms": abs(v_proj),
        "v_simple_ms": v_simple,
        "error_v_pct": 100.0 * (abs(v_proj) - v_simple) / v_simple,
        "E_proj_mJ": E_proj * 1e3,
        "E_simple_mJ": E_simple * 1e3,
        "E_stored_mJ": E_stored * 1e3,
        "eff_distributed": E_proj / E_stored,
        "eff_simple": E_simple / E_stored,
        "t_launch_ms": t_sep * 1e3,
        "f_surge_Hz": f_surge,
        "surge_periods_in_launch": t_sep * f_surge,
        "mass_ratio": m_spring / m_proj,
    }


def surge_study(k: float, m_spring: float, m_proj: float, x_cock: float,
                preload_force: float = 0.0,
                N_list=(10, 20, 40, 80)) -> list[dict]:
    return [simulate_distributed_spring(k, m_spring, m_proj, x_cock,
                                        preload_force=preload_force, N=N)
            for N in N_list]
