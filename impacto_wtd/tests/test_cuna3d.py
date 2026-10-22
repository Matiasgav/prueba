"""Verificación del modelo 3D de la cuña contra soluciones cerradas."""

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.fem import Contactos, Estado, Geometria, ModeloCuna, isotropo  # noqa: E402

E, RHO, L = 24e9, 1900.0, 0.2


@pytest.fixture(scope="module")
def barra_libre():
    """Barra rectangular 30 x 10 x 200 isótropa, sin contactos (libre-libre)."""
    g = Geometria(B=30e-3, b=30e-3)
    mod = ModeloCuna(g, isotropo(E, 0.3, RHO))
    mod.cargar_estado(Estado("libre", lambda x: 0 * x, lambda x: 1e-6 + 0 * x, lambda x: 1e-6 + 0 * x))
    mod.u0 = np.zeros(mod.m.n_dof)
    f, _ = mod.modos(16, f_shift=10)
    return mod, f


def test_masa(barra_libre):
    mod, _ = barra_libre
    assert mod.M.sum() / 3 == pytest.approx(RHO * mod.g.masa, rel=1e-12)


def test_seis_modos_rigidos(barra_libre):
    _, f = barra_libre
    assert np.sum(f < 1.0) == 6


def test_flexion_euler(barra_libre):
    """1.er modo de flexión en el espesor: Euler-Bernoulli libre-libre (4,730^2).
    El de Timoshenko queda un poco por debajo; se acepta -2 % / +0,5 %."""
    _, f = barra_libre
    c = math.sqrt(E * 0.01 ** 2 / 12 / RHO)
    f_eb = 4.7300 ** 2 / (2 * math.pi * L ** 2) * c
    f1 = f[f > 1][0]
    assert 0.98 * f_eb < f1 < 1.005 * f_eb


def test_axial(barra_libre):
    _, f = barra_libre
    fa = math.sqrt(E / RHO) / (2 * L)
    assert np.min(np.abs(f - fa)) / fa < 0.005


def test_torsion(barra_libre):
    """Torsión de Saint-Venant de la sección rectangular (Roark)."""
    _, f = barra_libre
    G = E / 2.6
    a, b = 0.015, 0.005
    k = a * b ** 3 * (16 / 3 - 3.36 * b / a * (1 - b ** 4 / (12 * a ** 4)))
    Ip = 0.03 * 0.01 * (0.03 ** 2 + 0.01 ** 2) / 12
    ft = math.sqrt(G * k / (RHO * Ip)) / (2 * L)
    assert np.min(np.abs(f - ft)) / ft < 0.01


@pytest.fixture(scope="module")
def cuna_ajustada():
    mod = ModeloCuna()
    mod.cargar_estado(Estado("u", lambda x: 0.7e6 + 0 * x))
    mod.equilibrio()
    return mod


def test_equilibrio_fuerzas(cuna_ajustada):
    """La fuerza del fondo la equilibra la componente radial de los flancos,
    y la normal vale la radial / sen(alfa) (sin rozamiento en el asiento)."""
    r = cuna_ajustada.resumen_equilibrio()
    assert r["F_fondo_N"] == pytest.approx(0.7e6 * 0.035 * 0.2, rel=3e-3)
    assert r["F_flancos_radial_N"] == pytest.approx(r["F_fondo_N"], rel=1e-6)
    a = cuna_ajustada.g.alfa_flanco
    assert r["F_flancos_normal_N"] == pytest.approx(r["F_fondo_N"] / math.sin(a), rel=1e-6)


def test_hertz_golpe(cuna_ajustada):
    """El golpe sobre la cuña ajustada se parece al de Hertz contra una masa
    infinita y rígida, con algo menos de fuerza y algo más de duración
    porque la cuña cede."""
    r = cuna_ajustada.golpe(0.1, t_fin=0.15e-3)
    m, R, v = 3e-3, 3e-3, r["v0"]
    Est = r["K_H"] / (4 / 3 * math.sqrt(R))
    dmax = (15 * m * v ** 2 / (16 * Est * math.sqrt(R))) ** 0.4
    F_rig, tc_rig = r["K_H"] * dmax ** 1.5, 2.94 * dmax / v
    assert 0.75 * F_rig < r["F_H_max"] < F_rig
    assert tc_rig < r["t_contacto_us"] * 1e-6 < 1.3 * tc_rig


def test_conservacion_energia():
    """Sin amortiguamiento ni rozamiento, con la cuña libre: lo que pierde el
    impactador lo tiene la cuña (cinética + elástica)."""
    mod = ModeloCuna(cont=Contactos(mu=0.0, mu_ripple=0.0))
    mod.cargar_estado(Estado("libre", lambda x: 0 * x, lambda x: 1e-3 + 0 * x, lambda x: 1e-3 + 0 * x))
    mod.equilibrio()
    r = mod.golpe(0.1, t_fin=0.12e-3, zeta=(1e-9, 2e3, 30e3))
    H = r["hist"]
    assert H["F_H"][-1] == 0.0                     # ya se separaron
    assert r["E_cuna_final_mJ"] == pytest.approx(r["E_transmitida_mJ"], rel=0.01)
