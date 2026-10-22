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
