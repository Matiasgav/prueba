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


def test_el_error_de_escala_cancela_exacto_en_el_cociente():
    """Si v_i y v_r salen del mismo canal, cualquier K común se cancela.

    Es la idea del usuario, y es exacta: e = (K v_r)/(K v_i) = v_r/v_i para
    cualquier K. Así que la calibración de K_F —que era TODO el residual del
    modo de circuito abierto— desaparece del índice de rebote y del Leeb.
    """
    from wtd.backemf import velocity_from_open_circuit
    import numpy as np
    c = CoilSpec()
    v_i, v_r = 1.48, 1.169
    u = np.array([c.emf(v_i), c.emf(v_r)])
    # medir con un K_F equivocado en un 30 % no cambia el cociente
    c_malo = CoilSpec(K_F0=c.K_F0 * 1.30)
    e_bien = velocity_from_open_circuit(u, c)
    e_mal = velocity_from_open_circuit(u, c_malo)
    assert e_bien[1] / e_bien[0] == pytest.approx(e_mal[1] / e_mal[0], rel=1e-12)
    assert e_bien[1] / e_bien[0] == pytest.approx(v_r / v_i, rel=1e-9)
    # pero la velocidad absoluta sí se va un 30 %
    assert e_mal[0] / e_bien[0] == pytest.approx(1 / 1.30, rel=1e-9)


def test_conviene_que_el_impacto_caiga_en_el_centro_de_la_carrera():
    """Lo que sobrevive no es el valor de K_F sino su VARIACIÓN entre las dos
    medidas, o sea la pendiente local dK/dx.

    La curva del LAH04 tiene un máximo en el centro, donde dK/dx = 0: ahí el
    residual es de segundo orden. Es una condición de geometría gratis.
    """
    from wtd.backemf import ratio_error_budget
    c = CoilSpec()
    centro = ratio_error_budget(c, x_impact=0.0)
    borde = ratio_error_budget(c, x_impact=1.5e-3)
    assert centro["e_variacion_KF_pct"] < 0.1
    assert borde["e_variacion_KF_pct"] > 5 * centro["e_variacion_KF_pct"]
    # en el centro el término dominante pasa a ser el ruido, no K_F
    assert centro["e_ruido_pct"] > 2 * centro["e_variacion_KF_pct"]


def test_en_el_cociente_el_backemf_le_gana_al_inductivo():
    """Comparación justa: al inductivo también se le cancela la escala, así
    que quedan los dos ruidos. El back-EMF gana porque su señal es grande."""
    from wtd.backemf import compare_ratio_with_inductive
    r = compare_ratio_with_inductive(CoilSpec())
    assert r["backemf_restitucion_pct"] < r["inductivo_restitucion_pct"]
    assert r["ventaja_backemf"] > 1.5
    # y los dos dan resolución de sobra contra el rango del Leeb (20 %)
    assert 20.0 / r["backemf_restitucion_pct"] > 100


def test_la_repetibilidad_es_lo_que_importa_para_clasificar():
    """La exactitud absoluta de la energía queda con el 4 % de K_F, pero es
    sistemática: corre el umbral y se absorbe calibrando. Lo que ensucia la
    clasificación es la dispersión tiro a tiro, y ésa viene sólo del ruido."""
    from wtd.backemf import repeatability_of_absolute_energy
    r = repeatability_of_absolute_energy(CoilSpec())
    assert r["sigma_E_pct"] < 0.5
    b = error_budget(CoilSpec())
    assert b["modo_B_energia_pct"] > 20 * r["sigma_E_pct"]
