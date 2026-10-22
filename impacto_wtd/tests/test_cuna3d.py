"""Verificación del modelo 3D de la cuña contra soluciones cerradas."""

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.fem import Contactos, Estado, Geometria, ModeloCuna, Ortotropo, isotropo  # noqa: E402

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


@pytest.mark.parametrize("ripple", [True, False])
def test_equilibrio_fuerzas(ripple):
    """La fuerza del fondo la equilibra la componente radial de los flancos,
    y la normal vale la radial / sen(alfa) (sin rozamiento en el asiento).
    Con ripple y sin ripple (fondo rígido con Hertz, que es el caso difícil)."""
    mod = ModeloCuna(cont=Contactos(ripple=ripple))
    mod.cargar_estado(Estado("u", lambda x: 0.7e6 + 0 * x))
    mod.equilibrio()
    r = mod.resumen_equilibrio()
    assert r["F_fondo_N"] == pytest.approx(0.7e6 * 0.035 * 0.2, rel=1e-6)
    assert r["F_flancos_radial_N"] == pytest.approx(r["F_fondo_N"], rel=1e-6)
    a = mod.g.alfa_flanco
    assert r["F_flancos_normal_N"] == pytest.approx(r["F_fondo_N"] / math.sin(a), rel=1e-6)
    assert r["residuo_equilibrio"] < 1e-9


def test_equilibrio_tramo_libre():
    """Tramo central libre con juego: equilibrio exacto y la presión pedida en los extremos."""
    zona = lambda x: (x > 60e-3) & (x < 140e-3)
    mod = ModeloCuna()
    mod.cargar_estado(Estado("m", lambda x: np.where(zona(x), 0.0, 0.7e6),
                             lambda x: np.where(zona(x), 10e-6, 0.0), lambda x: np.where(zona(x), 5e-6, 0.0)))
    mod.equilibrio()
    r = mod.resumen_equilibrio()
    p_f, _ = mod.fondo_presion(mod.u0)
    assert np.allclose(p_f[~zona(mod.fo_x)], 0.7e6, rtol=1e-6)
    assert r["F_flancos_radial_N"] == pytest.approx(r["F_fondo_N"], rel=1e-6)
    assert r["residuo_equilibrio"] < 1e-9


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


# ---------------------------------------------------------------------------
# Choques de un tramo libre contra los hombros, la barra y la pared lateral.
# Con el material 100 veces más rígido la cuña es un cuerpo rígido, y cada
# choque tiene solución cerrada (Hertz de un grado de libertad).
# ---------------------------------------------------------------------------

V = 0.05
RIGIDO = Ortotropo(*(np.array([24e9, 12e9, 24e9, 4.5e9, 5.5e9, 4.5e9]) * 100), 0.30, 0.12, 0.30, RHO)


def _choque(comp, signo, cont, juego_flanco, juego_fondo, clave, t_fin, mat=RIGIDO):
    mod = ModeloCuna(mat=mat, cont=cont)
    mod.cargar_estado(Estado("libre", lambda x: 0 * x, lambda x: juego_fondo + 0 * x,
                             lambda x: juego_flanco + 0 * x))
    mod.equilibrio()
    v = np.zeros(mod.m.n_dof)
    v[comp::3] = signo * V
    r = mod.golpe(0.1, energia=0, v_cuna0=v, t_fin=t_fin, zeta=(1e-9, 2e3, 30e3), cfl=0.5)
    H = r["hist"]
    on = H[clave] > 0
    i0 = int(np.argmax(on))
    i1 = i0 + int(np.argmax(~on[i0:]))
    t_c = float(H["t"][i1] - H["t"][i0])
    v_cm = float(np.sum(mod.M[comp::3] * r["v_final"][comp::3]) / np.sum(mod.M[comp::3]))
    return mod, r, t_c, -v_cm / (signo * V)


def _t_hertz(K, m):
    return 2.94 * (5 * m * V ** 2 / (4 * K)) ** 0.4 / V


def test_choque_contra_hombros():
    """Tramo libre que sube 1 µm y choca contra los dos flancos inclinados."""
    mod, r, t_c, e = _choque(1, +1, Contactos(mu=0.0, e_rest=1.0), 1e-6, 1e-3, "F_flancos", 160e-6)
    g, C = mod.g, mod.C
    K = 2 * g.L * math.hypot(g.e, 0.5 * (g.B - g.b)) * C * math.sin(g.alfa_flanco) ** 2.5
    assert t_c == pytest.approx(_t_hertz(K, RHO * g.masa), rel=0.03)
    assert e == pytest.approx(1.0, abs=0.02)
    assert r["error_balance_energia"] < 0.01


def test_choque_contra_barra():
    """Sin ripple: tramo libre que baja 1 µm y choca contra la barra."""
    mod, r, t_c, e = _choque(1, -1, Contactos(mu=0.0, e_rest=1.0, ripple=False), 1e-3, 1e-6, "F_fondo", 80e-6)
    K = mod.g.B * mod.g.L * mod.C
    assert t_c == pytest.approx(_t_hertz(K, RHO * mod.g.masa), rel=0.05)
    assert e == pytest.approx(1.0, abs=0.02)
    assert r["error_balance_energia"] < 0.01


def test_choque_contra_pared_lateral():
    """Desplazamiento lateral: la esquina inferior choca contra la pared vertical.
    Cuerpo rígido que además gira, porque el contacto está debajo del centro de masa."""
    mod, r, t_c, _ = _choque(2, +1, Contactos(mu=0.0, e_rest=1.0, juego_lateral=1e-6), 1e-3, 1e-3,
                             "F_lateral", 100e-6)
    m = RHO * mod.g.masa
    Mn, X = mod.M[0::3], mod.m.X
    yc = np.sum(Mn * X[:, 1]) / m
    Ix = np.sum(Mn * ((X[:, 1] - yc) ** 2 + X[:, 2] ** 2))
    m_ef = 1 / (1 / m + yc ** 2 / Ix)
    t_an = math.pi * math.sqrt(m_ef / (mod.cont.k_linea * mod.g.L))
    assert t_c == pytest.approx(t_an, rel=0.08)
    assert r["error_balance_energia"] < 0.01


def test_restitucion_hunt_crossley():
    """Choque de frente contra la barra a v_ref: la restitución tiene que ser e_rest."""
    _, r, _, e = _choque(1, -1, Contactos(mu=0.0, e_rest=0.7, v_ref_rest=V, ripple=False),
                         1e-3, 1e-6, "F_fondo", 80e-6)
    assert e == pytest.approx(0.7, abs=0.03)
    assert r["E_choques_mJ"] > 0
    assert r["error_balance_energia"] < 0.01


def test_conservacion_energia():
    """Cuña libre sin pérdidas golpeada: lo que pierde el impactador lo tiene la cuña."""
    mod = ModeloCuna(cont=Contactos(mu=0.0, mu_ripple=0.0, e_rest=1.0))
    mod.cargar_estado(Estado("libre", lambda x: 0 * x, lambda x: 1e-3 + 0 * x, lambda x: 1e-3 + 0 * x))
    mod.equilibrio()
    r = mod.golpe(0.1, t_fin=0.12e-3, zeta=(1e-9, 2e3, 30e3))
    assert r["hist"]["F_H"][-1] == 0.0                     # ya se separaron
    assert r["E_cuna_final_mJ"] == pytest.approx(r["E_transmitida_mJ"], rel=0.01)


def test_balance_energia_tramo_libre_con_choques():
    """Golpe real sobre un extremo libre con juego: rebota contra el ripple y los
    hombros. La energía tiene que cerrar con rozamiento, choques y Rayleigh."""
    mod = ModeloCuna()
    mod.cargar_estado(Estado("x", lambda x: np.where(x < 60e-3, 0.0, 0.7e6),
                             lambda x: np.where(x < 60e-3, 20e-6, 0.0),
                             lambda x: np.where(x < 60e-3, 10e-6, 0.0)))
    mod.equilibrio()
    r = mod.golpe(0.03, t_fin=1.0e-3)
    assert r["error_balance_energia"] < 0.02
    assert r["p_flanco_max_MPa"] < r["p_diseno_MPa"]
