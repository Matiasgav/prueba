"""Anclas del palpador de acople blando."""

import math

import numpy as np
import pytest

from wtd.softprobe import (G, SoftProbe, apply_soft_probe, design,
                           noise_in_feature, probe_features)


def test_fondo_de_escala_es_F_sobre_m_y_no_depende_del_resorte():
    """El invariante que ordena el diseño: a_despegue = F/m, sea cual sea k.

    Es la razon por la que ablandar el acople NO cuesta rango de medida: lo
    unico que cambia es que parte del movimiento de la cuña cae adentro.
    """
    ref = None
    for k in (1e4, 5e4, 2e5, 8e5):
        p = SoftProbe(mass=0.68e-3, k_soft=k, preload=1.0)
        a = p.a_liftoff()
        if ref is None:
            ref = a
        assert a == pytest.approx(ref, rel=1e-12)
        # y el producto ganancia x desplazamiento de despegue lo reproduce
        assert p.gain() * p.x_liftoff() == pytest.approx(a, rel=1e-9)
    assert ref / G == pytest.approx(150.0, rel=1e-3)


def test_design_cumple_la_especificacion():
    p = design(preload=1.0, a_liftoff_g=150.0, x_wedge_max=8.6e-6,
               a_full_scale_g=100.0)
    assert p.a_liftoff() / G == pytest.approx(150.0, rel=1e-9)
    # el mayor desplazamiento esperado cae en el fondo de escala elegido
    assert p.gain() * 8.6e-6 / G == pytest.approx(100.0, rel=1e-6)
    assert p.mass * 1e3 == pytest.approx(0.68, abs=0.01)


def test_el_resorte_blando_domina_y_linealiza_el_contacto():
    """Hertz debe aportar una fraccion chica de la flexibilidad total."""
    p = design(preload=1.0, a_liftoff_g=150.0, x_wedge_max=8.6e-6,
               a_full_scale_g=100.0)
    assert p.hertz_share() < 0.05
    assert p.k_soft < p.k_hertz() / 10.0


def test_ganancia_insensible_a_la_precarga():
    """La ganancia depende de la precarga solo por el termino de Hertz.

    Es la ventaja practica decisiva: el crawler no puede sostener la
    precarga con precision, y no hace falta que lo haga.
    """
    base = SoftProbe(mass=0.68e-3, k_soft=44.7e3, preload=1.0)
    for F in (0.5, 1.5):
        p = SoftProbe(mass=base.mass, k_soft=base.k_soft, preload=F)
        assert abs(p.gain() / base.gain() - 1.0) < 0.01


def _seno_con_rampa(amp, f, p, dt, t_ramp=15e-3, t_end=30e-3):
    """Seno de amplitud `amp` con envolvente suave.

    Arrancar el seno de golpe mete un salto de velocidad que excita la
    resonancia del palpador, y ese transitorio (que decae con tau = 1/(zeta
    omega_n) = 6 ms) enmascara la respuesta estacionaria por un factor
    ~r. La envolvente lo evita; es lo mismo que hace falta en el banco real
    si se quiere calibrar con un shaker.
    """
    t = np.arange(0.0, t_end, dt)
    env = np.where(t < t_ramp, 0.5 * (1.0 - np.cos(np.pi * t / t_ramp)), 1.0)
    return t, amp * env * np.sin(2 * math.pi * f * t)


def test_regimen_sismico_lee_desplazamiento():
    """Muy por encima de la resonancia, a_leida -> omega_n^2 x_cuña.

    El factor exacto es sqrt(1 + (2 zeta r)^2); con zeta = 0.02 y r = 8 son
    1.05, de ahi la tolerancia del 10 %.
    """
    p = SoftProbe(mass=0.68e-3, k_soft=44.7e3, preload=1.0, zeta=0.02)
    f = 8.0 * p.f0()
    dt = 1.0 / (100.0 * f)
    amp = 1.0e-6
    t, w = _seno_con_rampa(amp, f, p, dt)
    o = apply_soft_probe(w, dt, p)
    # medir sobre la cola, ya en estacionario
    cola = o["a_palpador"][t > 20e-3]
    leido = float(np.abs(cola).max()) / G
    esperado = p.gain() * amp / G
    assert leido == pytest.approx(esperado, rel=0.10)
    assert not o["despega"]


def test_despegue_cuando_se_pasa_el_desplazamiento_limite():
    """Por encima de x_despegue = F/k el palpador salta; por debajo no.

    En regimen sismico la masa se queda quieta, asi que la compresion del
    acople es el propio desplazamiento de la cuña: despega cuando ese
    desplazamiento supera la flecha estatica F/k.
    """
    p = SoftProbe(mass=0.68e-3, k_soft=44.7e3, preload=1.0, zeta=0.02)
    f = 8.0 * p.f0()
    dt = 1.0 / (100.0 * f)
    _, seguro = _seno_con_rampa(0.5 * p.x_liftoff(), f, p, dt)
    _, excesivo = _seno_con_rampa(3.0 * p.x_liftoff(), f, p, dt)
    assert not apply_soft_probe(seguro, dt, p)["despega"]
    assert apply_soft_probe(excesivo, dt, p)["despega"]


def test_probe_features_y_piso_de_ruido():
    dt = 1e-6
    t = np.arange(0.0, 3.0e-3, dt)
    a = 50.0 * G * np.sin(2 * math.pi * 3000.0 * t)
    f = probe_features(a, dt)
    assert f["pico_g"] == pytest.approx(50.0, rel=1e-3)
    assert f["rms_g"] == pytest.approx(50.0 / math.sqrt(2.0), rel=1e-2)
    # energia de un seno: A^2/2 * T
    assert f["energia_g2ms"] == pytest.approx(50.0 ** 2 / 2 * 3.0, rel=1e-2)

    n = noise_in_feature(75e-6, 5.0e3, 3.0e-3)
    assert n["sigma_g_rms"] == pytest.approx(5.3e-3, rel=0.05)
    # el peor caso real (cuña ajustada a 1 mJ) son 0.108 g^2 ms: >100x margen
    assert n["energia_g2ms"] < 0.108 / 100.0


def test_design_rechaza_lo_imposible():
    """Si la rigidez pedida supera la de Hertz no hay resorte blando."""
    with pytest.raises(ValueError):
        design(preload=1.0, a_liftoff_g=150.0, x_wedge_max=1e-9,
               a_full_scale_g=100.0)
