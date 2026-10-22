"""Verificación del modelo del palpador contra la teoría de vibraciones."""

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cuna3d.sensor import ADXL1004, Palpador, _flexura  # noqa: E402


def test_frecuencia_de_corte():
    """La flexura dimensionada da f0 con Hertz en serie (1.er modo del 2 GDL ~ f0)."""
    p = Palpador("t", [10e-6, 0.4e-3], [_flexura(1250, 0.4e-3, 10e-6)], [0.02])
    assert p.modos()[0] == pytest.approx(1250, rel=0.01)


def _seno(p, f, A, T=20e-3):
    t = np.arange(0, T, 0.5e-6)
    w = A * np.sin(2 * math.pi * f * t) * np.minimum(t / 5e-3, 1)        # arranque suave
    vw = np.gradient(w, t)
    return p.simular(t, w, vw)


def test_transmisibilidad_y_despegue():
    """Base armónica muy por debajo de f0: el carro sigue a la cuña (T ~ 1) y el
    contacto se pierde cuando la aceleración de la cuña supera F0/m (el invariante)."""
    p = Palpador("t", [10e-6, 0.4e-3], [_flexura(1250, 0.4e-3, 10e-6)], [0.02])
    f = 200.0
    a_lim = p.a_despegue_g() * 9.81
    # 80 % del límite: no despega y la lectura sigue a la cuña con T = 1/(1-r^2)
    # (régimen: el transitorio de arranque se apaga con tau = 1/(zeta w0) ~ 6 ms)
    A = 0.8 * a_lim / (2 * math.pi * f) ** 2
    t, a, Fc = _seno(p, f, A, T=45e-3)
    r = f / p.modos()[0]
    T = 1 / abs(1 - r ** 2)
    reg = t > 35e-3
    assert Fc[reg].min() > 0
    assert np.abs(a[reg]).max() == pytest.approx(T * 0.8 * a_lim, rel=0.03)
    # 120 % del límite (1,5 x 80 %): despega
    t, a, Fc = _seno(p, f, 1.5 * A, T=45e-3)
    assert np.any(Fc[t > 35e-3] <= 0)


def test_rechazo_alta_frecuencia():
    """A 30 kHz el filtro de 2.º orden con flexura metálica rechaza ~ (f0/f)^2."""
    p = Palpador("t", [10e-6, 0.4e-3], [_flexura(1250, 0.4e-3, 10e-6)], [0.02])
    f, aw = 30e3, 500 * 9.81
    t, a, Fc = _seno(p, f, aw / (2 * math.pi * f) ** 2, T=8e-3)
    rech = np.abs(a[t > 6e-3]).max() / aw
    assert rech < 3 * (1250 / f) ** 2


def test_acelerometro_ganancia_dc_y_resonancia():
    t = np.arange(0, 4e-3, 0.1e-6)
    for f, G_esp in ((1e3, 1.0), (10e3, 1 / (1 - (10 / 45) ** 2))):
        a = 9.81 * np.sin(2 * math.pi * f * t)
        ts, y, _ = ADXL1004.leer(t, a)
        g_med = np.abs(y[ts > 2e-3]).max()
        assert g_med == pytest.approx(G_esp, rel=0.06)


# ---------------------------------------------------------------------------
# El filtro mecánico contra la solución lineal exacta, incluida la resonancia
# ---------------------------------------------------------------------------

def _amplitud_regimen(p, f, a_base, T, t_med):
    """Amplitud de la aceleración del carro en régimen, por mínimos cuadrados a f."""
    t = np.arange(0, T, 0.5e-6)
    A = a_base / (2 * math.pi * f) ** 2
    w = A * np.sin(2 * math.pi * f * t)
    vw = np.gradient(w, t)
    tt, a, Fc = p.simular(t, w, vw)
    m = tt > t_med
    X = np.column_stack([np.sin(2 * math.pi * f * tt[m]), np.cos(2 * math.pi * f * tt[m])])
    c, *_ = np.linalg.lstsq(X, a[m], rcond=None)
    return float(np.hypot(*c)) / a_base, bool(np.any(Fc <= 0))


@pytest.mark.parametrize("f", [300.0, 900.0, 1250.0, 1600.0, 4000.0, 18000.0])
def test_frf_contra_solucion_lineal(f):
    """Transmisibilidad simulada (no lineal, en el tiempo) contra la lineal exacta.
    zeta = 0,05 para que el transitorio se apague rápido; amplitud chica (lineal)."""
    p = Palpador("t", [10e-6, 0.4e-3], [_flexura(1250, 0.4e-3, 10e-6)], [0.05])
    T_lin = float(p.frf(f)[0])
    a_base = 0.05 * p.a_despegue_g() * 9.81 / max(T_lin, 1.0)
    T_sim, despega = _amplitud_regimen(p, f, a_base, T=25e-3, t_med=15e-3)
    assert not despega
    assert T_sim == pytest.approx(T_lin, rel=0.03)


def test_pico_de_resonancia():
    """Con zeta = 0,02 el pico en f0 vale ~ 1/(2 zeta) = 25 (Q de la flexura)."""
    p = Palpador("t", [10e-6, 0.4e-3], [_flexura(1250, 0.4e-3, 10e-6)], [0.02])
    f = np.linspace(1150, 1350, 401)
    H = p.frf(f)
    assert f[np.argmax(H)] == pytest.approx(1250, rel=0.01)
    assert H.max() == pytest.approx(1 / (2 * 0.02), rel=0.08)
    a_base = 0.05 * p.a_despegue_g() * 9.81 / H.max()
    T_sim, _ = _amplitud_regimen(p, float(f[np.argmax(H)]), a_base, T=60e-3, t_med=45e-3)
    assert T_sim == pytest.approx(H.max(), rel=0.05)


def test_convergencia_paso_de_tiempo():
    """Con la mitad del paso, la respuesta a un golpe real de la cuña no cambia."""
    import pathlib
    f = pathlib.Path(__file__).resolve().parent.parent / "results/cuna3d/palpador/floja.npz"
    if not f.exists():
        pytest.skip("falta correr cuna3d.estudio")
    d = np.load(f)
    p = Palpador("t", [10e-6, 0.4e-3], [_flexura(1250, 0.4e-3, 10e-6)], [0.02])
    t1, a1, F1 = p.simular(d["t"], d["uy"], d["vy"])
    t2, a2, F2 = p.simular(d["t"], d["uy"], d["vy"], dt=0.05e-6)
    a2i = np.interp(t1, t2, a2)
    assert np.max(np.abs(a2i - a1)) < 0.01 * np.max(np.abs(a1))
    assert abs(F1.min() - F2.min()) < 0.01
