"""Anclas del estudio de velocidad por back-EMF del voice coil."""

import pytest

from wtd.backemf import (CoilSpec, compare_with_inductive, error_budget,
                         LEVER_RATIO)


def test_la_arquitectura_decide_si_el_metodo_sirve():
    """Con separación el back-EMF no ve el impacto; sin separación sí.

    El lanzador de resorte (`wtd.launcher`) separa el proyectil en x_release
    y lo manda en vuelo libre: la bobina queda desacoplada y sólo da la
    velocidad de separación. La palanca en L (`wtd.lever`) no separa, así
    que la bobina acompaña el impacto y el rebote.
    """
    # la relación de palanca es cercana a 1: el back-EMF ve casi toda la señal
    assert 0.7 < LEVER_RATIO < 1.0
    c = CoilSpec()
    # con la maza a 1,48 m/s el EMF es una señal grande, no marginal
    assert c.emf(1.48) == pytest.approx(2.33, rel=0.02)
    # y el salto en el impacto (restitución ~0,79) es aún mayor
    assert c.emf(1.48) * 1.79 > 4.0


def test_tau_e_es_del_orden_de_la_duracion_del_contacto():
    """43 µs contra ~60 µs de contacto: por eso el término L·di/dt cae justo
    encima del evento que hay que medir."""
    c = CoilSpec()
    assert c.tau_e() * 1e6 == pytest.approx(43.1, rel=0.02)
    assert 0.5 < c.tau_e() / 60e-6 < 1.5


def test_K_F_varia_31_por_ciento_sobre_la_carrera():
    """Es el error de fondo que queda en el mejor modo de medición."""
    c = CoilSpec()
    s = c.summary()
    assert s["variacion_K_F_pct"] == pytest.approx(-30.7, abs=1.0)
    # y en el centro coincide con la ficha
    assert s["K_F_centro_N_A"] == pytest.approx(1.897, rel=0.01)


def test_abrir_el_circuito_mejora_el_error_cinco_veces():
    """Modo A (drive conectado) vs modo B (circuito abierto).

    Con el drive conectado domina la deriva de R sin compensar. Abriendo el
    circuito desaparecen R y L·di/dt de una, y queda sólo K_F(x).
    """
    b = error_budget(CoilSpec())
    assert b["e_deriva_R_ms"] > 5 * b["e_calibracion_KF_ms"]   # R domina el A
    assert b["modo_A_energia_pct"] > 20.0
    assert b["modo_B_energia_pct"] < 5.0
    assert b["modo_A_energia_pct"] / b["modo_B_energia_pct"] > 4.0
    # en modo B el error es ENTERAMENTE la calibración de K_F
    assert b["modo_B_ms"] == pytest.approx(b["e_calibracion_KF_ms"], rel=0.01)


def test_no_reemplaza_al_sensor_inductivo():
    """Ni en el mejor modo: 4 % contra 0,27 % de error en energía."""
    cm = compare_with_inductive(CoilSpec())
    assert cm["inductivo_energia_pct"] < 0.5
    assert cm["penalizacion_B"] > 10.0
    assert cm["penalizacion_A"] > 50.0


def test_el_error_del_modo_B_escala_con_la_calibracion_de_KF():
    """Como sólo queda esa fuente, el error en energía es 2× el de K_F."""
    for d in (0.5, 1.0, 2.0, 5.0):
        b = error_budget(CoilSpec(), dKF_pct=d)
        assert b["modo_B_energia_pct"] == pytest.approx(2 * d, rel=0.02)
