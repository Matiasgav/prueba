"""Casos ancla del brief §9. Si esto no pasa, nada de lo que sigue vale."""

from __future__ import annotations

import math

import numpy as np
import pytest

from wtd.actuator import (LAH04, force_constant_from_datasheet,
                          thermal_budget, work_over_window)
from wtd.beam import (BeamSection, euler_bernoulli_clamped,
                      solve_kappa_for_frequency, timoshenko_clamped)
from wtd.hertz import hertz_impact, max_energy_for_pressure
from wtd.lever import sweep_ball_diameter, sweep_contact_height
from wtd.materials import G11_HERTZ, STEEL

SEC = BeamSection(0.030, 0.008, 24e9, 1900.0, 5.7e9, 5.0 / 6.0)
NEL = 80


# -- cinemática básica -----------------------------------------------------

def test_cinematica_basica():
    """E = 5 mJ, m = 4 g -> v = 1.5811 m/s ; p = 6.3246 mN s."""
    E, m = 5e-3, 4e-3
    v = math.sqrt(2 * E / m)
    assert v == pytest.approx(1.5811, abs=1e-4)
    assert m * v * 1e3 == pytest.approx(6.3246, abs=1e-4)


# -- modal Euler-Bernoulli -------------------------------------------------

@pytest.mark.parametrize("L,f_obj,tol", [(0.050, 11691.0, 1.0),
                                         (0.100, 2922.7, 0.5)])
def test_eb_frecuencias(L, f_obj, tol):
    m = euler_bernoulli_clamped(SEC, L, NEL)
    f, _ = m.modes(1)
    assert f[0] == pytest.approx(f_obj, abs=tol)


def test_eb_rigidez_estatica():
    """192 EI/L^3 = 47.19 MN/m para L = 50 mm."""
    m = euler_bernoulli_clamped(SEC, 0.050, NEL)
    k = m.static_stiffness_at(0.025)
    assert k / 1e6 == pytest.approx(47.19, abs=0.02)
    assert k == pytest.approx(192 * SEC.EI / 0.050 ** 3, rel=1e-4)


def test_eb_masa_modal():
    """Masa modal EB / masa total = 0.39648."""
    m = euler_bernoulli_clamped(SEC, 0.050, NEL)
    p = m.first_mode_at(0.025)
    assert p["m_eff_kg"] / m.total_mass == pytest.approx(0.39648, abs=1e-4)


# -- modal Timoshenko ------------------------------------------------------

@pytest.mark.parametrize("L,f_obj,m_obj,k_obj", [
    (0.050, 9376.0, 9.77e-3, 33.90e6),
    (0.100, 2738.0, 18.56e-3, 5.493e6),
])
def test_timoshenko(L, f_obj, m_obj, k_obj):
    m = timoshenko_clamped(SEC, L, NEL)
    f, _ = m.modes(1)
    p = m.first_mode_at(L / 2)
    assert f[0] == pytest.approx(f_obj, rel=2e-4)
    assert p["m_eff_kg"] == pytest.approx(m_obj, rel=2e-3)
    assert p["k_eff_N_m"] == pytest.approx(k_obj, rel=2e-3)


def test_kappa_implicito():
    """Incógnita abierta #5 del brief: kappa no declarado.

    Los dos vanos, resueltos de forma independiente, dan el MISMO kappa y es
    el valor estándar 5/6. La incógnita queda cerrada.
    """
    k50 = solve_kappa_for_frequency(SEC, 0.050, 9376.0, NEL)
    k100 = solve_kappa_for_frequency(SEC, 0.100, 2738.0, NEL)
    assert k50 == pytest.approx(5.0 / 6.0, rel=5e-3)
    assert k100 == pytest.approx(5.0 / 6.0, rel=5e-3)
    assert k50 == pytest.approx(k100, rel=2e-3)


# -- curva del actuador ----------------------------------------------------

def test_constante_de_fuerza():
    assert force_constant_from_datasheet() == pytest.approx(1.897, abs=1e-3)


@pytest.mark.parametrize("win,obj", [(3.0e-3, 5.39e-3), (3.5e-3, 6.16e-3),
                                     (4.0e-3, 6.85e-3)])
def test_trabajo_ventana(win, obj):
    assert work_over_window(win) == pytest.approx(obj, rel=1.5e-3)


def test_presupuesto_termico():
    """Brief §3.4: 6.6 ms, 20 golpes a 5 Hz -> duty 3.3 %, 0.38 W."""
    r = thermal_budget(1.5, 6.6e-3, 5.0)
    assert r["duty"] == pytest.approx(0.033, abs=0.001)
    assert r["I_rms_A"] == pytest.approx(0.27, abs=0.01)
    assert r["P_avg_W"] == pytest.approx(0.38, abs=0.02)
    assert r["P_cont_W"] == pytest.approx(1.75, abs=0.03)


# -- ensayo de bola (ancla empírica) --------------------------------------

def test_ancla_bola_acero():
    """Bola de acero 8 mm desde 70 mm sobre G11 (brief §7.1 y §9)."""
    R = 4e-3
    m = STEEL.rho * (4 / 3) * math.pi * R ** 3
    assert m * 1e3 == pytest.approx(2.105, abs=0.005)
    v = math.sqrt(2 * 9.80665 * 0.070)
    assert v == pytest.approx(1.172, abs=0.002)
    E = 0.5 * m * v ** 2
    assert E * 1e3 == pytest.approx(1.45, abs=0.01)
    assert m * v * 1e3 == pytest.approx(2.47, abs=0.01)
    h = hertz_impact(E, m, R, STEEL, G11_HERTZ)
    assert h.F == pytest.approx(165.0, rel=0.01)
    assert h.p_max / 1e6 == pytest.approx(900.0, rel=0.01)
    assert h.t_c * 1e6 == pytest.approx(55.0, rel=0.04)


def test_escalados_hertz():
    """p_max ∝ E*^0.8 R^-0.6 E^0.2 ; t_c ∝ m^0.4 k^-0.4 v^-0.2."""
    base = hertz_impact(1.45e-3, 2.105e-3, 4e-3, STEEL, G11_HERTZ)
    doble = hertz_impact(2 * 1.45e-3, 2.105e-3, 4e-3, STEEL, G11_HERTZ)
    assert doble.p_max / base.p_max == pytest.approx(2 ** 0.2, rel=1e-6)
    grande = hertz_impact(1.45e-3, 2.105e-3, 8e-3, STEEL, G11_HERTZ)
    assert grande.p_max / base.p_max == pytest.approx(2 ** -0.6, rel=1e-6)
    pesada = hertz_impact(1.45e-3, 2 * 2.105e-3, 4e-3, STEEL, G11_HERTZ)
    # a energía constante, t_c ∝ m^0.4 v^-0.2 = m^0.4 (E/m)^-0.1 = m^0.5
    assert pesada.t_c / base.t_c == pytest.approx(2 ** 0.5, rel=1e-6)


def test_energia_maxima_por_presion():
    """Coherencia inversa: la energía que da 900 MPa es la del ensayo."""
    E = max_energy_for_pressure(900e6, 2.105e-3, 4e-3, STEEL, G11_HERTZ)
    assert E * 1e3 == pytest.approx(1.45, rel=0.02)


# -- Leeb ------------------------------------------------------------------

def test_leeb_d():
    """5.45 g a 2.05 m/s -> 11.5 mJ, p = 11.2 mN s."""
    m, v = 5.45e-3, 2.05
    assert 0.5 * m * v ** 2 * 1e3 == pytest.approx(11.5, abs=0.05)
    assert m * v * 1e3 == pytest.approx(11.2, abs=0.05)


# -- tabla §5 de la palanca -----------------------------------------------

def test_tabla_palanca_altura_contacto():
    W = work_over_window(3.0e-3)
    obj = {5.05: (3.55, 48.4, 17.8, 2.89, 1.66),
           7.00: (5.50, 31.3, 13.6, 2.33, 1.49),
           8.00: (6.50, 26.4, 11.9, 2.19, 1.44)}
    for r in sweep_contact_height(W):
        o = obj[r["y_contact_mm"]]
        assert r["r_eff_mm"] == pytest.approx(o[0], abs=0.01)
        assert r["theta_deg"] == pytest.approx(o[1], abs=0.1)
        assert r["alpha_deg"] == pytest.approx(o[2], abs=0.15)
        # E y v dependen de J_L, que el brief no declara: se reconstruyó una
        # palanca de acero de 3 x 8 mm. Tolerancia acorde.
        assert r["E_hammer_mJ"] == pytest.approx(o[3], rel=0.02)
        assert r["v_ms"] == pytest.approx(o[4], rel=0.02)


def test_bola_choca_su_pivote():
    """El brief avisa que con brazo corto la bola choca contra el pivote."""
    W = work_over_window(3.0e-3)
    for r in sweep_ball_diameter(W, (8, 9, 10)):
        if not r.get("feasible"):
            continue
        interf = r["r_h_mm"] < r["D_ball_mm"] / 2.0
        if r["D_ball_mm"] >= 9:
            assert interf, f"D={r['D_ball_mm']} debería interferir"
        else:
            assert not interf
