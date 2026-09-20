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


def test_frecuencia_sube_con_el_apriete():
    """La cuña asentada es MUCHO mas rapida que la suelta, no mas lenta.

    Corrige el 6.1 kHz que arrastraba el modelo de apoyo en extremos: con
    apoyo distribuido, el hombro cerrado pone el primer modo en ~33 kHz, y
    con el hombro abierto quedan los dos modos de cuerpo rigido sobre el
    ripple, en ~1.3 kHz. Factor ~26 entre los dos.
    """
    from wtd.wedge import WedgeModel, WedgeSpec, standard_states
    m = WedgeModel(WedgeSpec(), standard_states()[0], n_modes=8)
    b = m.bounding_frequencies(4)
    assert b["seated_Hz"][0] == pytest.approx(32874, rel=0.02)
    assert b["lifted_Hz"][0] == pytest.approx(1275, rel=0.02)
    assert b["seated_Hz"][0] / b["lifted_Hz"][0] > 20


def test_design_space_ordena_el_compromiso():
    """f0 decide la calidad; la masa decide si sobrevivis. Son independientes.

    Con el amortiguamiento real de una flexura (zeta = 0.005) el optimo esta
    en ~1.3 kHz, justo donde ya cae el diseño. Con el zeta pesimista de la
    rev. C (0.08) parecia estar en 2 kHz.
    """
    from wtd.softprobe import design_space
    sp = design_space(preload=1.0, margin=1.4)
    by = {r["f0_Hz"]: r for r in sp}
    # el optimo con flexura esta en 1273 Hz
    assert max(sp, key=lambda r: r["separacion"])["f0_Hz"] == 1273
    assert by[600]["separacion"] < by[1273]["separacion"] > by[2000]["separacion"]
    # subir f0 obliga a bajar la masa
    for a, b in zip(sp, sp[1:]):
        assert b["m_max_g"] < a["m_max_g"]
    # el punto elegido: 0,68 g cae dentro de lo admisible a 1273 Hz
    assert by[1273]["m_max_g"] > 0.68
    assert by[1600]["m_max_g"] < 0.68
    # con el zeta conservador el optimo se corria a 2 kHz
    sp8 = design_space(preload=1.0, margin=1.4, zeta=0.08)
    assert max(sp8, key=lambda r: r["separacion"])["f0_Hz"] == 2000
    # duplicar la precarga duplica el techo de despegue
    sp2 = design_space(preload=2.0, margin=1.4)
    assert sp2[0]["m_max_g"] == pytest.approx(2 * sp[0]["m_max_g"], rel=1e-9)


def test_el_amortiguamiento_es_el_parametro_dominante():
    """Flexura metálica o el ensayo no sirve. Es LA decisión de construcción.

    Entre zeta = 0.005 (acero) y zeta = 0.15 (elastómero blando) la separación
    cae de x150 a x3 sin que cambie ningún otro número del diseño.
    """
    from wtd.softprobe import ZETA_SWEEP
    by = {z: (a, s) for z, a, s in ZETA_SWEEP}
    assert by[0.005][1] > 100.0          # flexura: excelente
    assert by[0.080][1] < 20.0           # lo que suponía la rev. C
    assert by[0.150][1] < 5.0            # elastómero: inservible
    assert by[0.005][1] / by[0.150][1] > 40.0
    # y es monótono: más amortiguamiento, peor separación
    seps = [s for _, _, s in ZETA_SWEEP]
    for a, b in zip(seps, seps[1:]):
        assert b < a
    # el pico leído casi no se mueve mientras zeta se mantenga bajo
    assert by[0.002][0] == pytest.approx(by[0.020][0], rel=0.01)


def test_el_filtro_separa_las_dos_bandas_enteras():
    """0 % de la cuña asentada por debajo del corte; 100 % de la suelta.

    Medido sobre el espectro del DESPLAZAMIENTO (que es lo que excita al
    palpador) con resolución de 25 Hz. Una versión anterior reportaba
    "125 Hz" para la cuña floja: era el primer bin de una ventana de 8 ms.
    """
    import numpy as np
    from wtd.wedge import WedgeSpec, standard_states
    from wtd.impact_sim import HammerSpec, SimConfig, simulate

    w, ham = WedgeSpec(), HammerSpec(mass=4e-3)
    frac = {}
    for idx, nm in ((0, "S0"), (6, "S6")):
        r = simulate(w, standard_states()[idx], ham, 1.58,
                     SimConfig(x_palpator=12.5e-3, t_end=40e-3))
        dt, n = r["dt_rec"], len(r["w_palp"])
        sig = (r["w_palp"] - r["w_palp"].mean()) * np.hanning(n)
        P = np.abs(np.fft.rfft(sig))
        f = np.fft.rfftfreq(n, dt)
        m = f >= 40
        E = np.cumsum(P[m] ** 2)
        E /= E[-1]
        frac[nm] = float(E[int(np.searchsorted(f[m], 1273.0))])
    assert frac["S0"] < 0.001      # la asentada no le entrega nada al filtro
    assert frac["S6"] > 0.999      # la suelta le entrega todo


def test_la_masa_de_punta_no_cambia_la_lectura_pero_adelanta_el_despegue():
    """El resorte va ENTRE la cuña y la masa, así que la punta queda del lado
    de la cuña y ésta la arrastra a miles de g.

    Mientras haya contacto la ecuación de la masa no cambia, así que la lectura
    es idéntica; lo único que hace la masa de punta es adelantar el despegue.
    Cota: m_punta <= F / a_cuña_max.
    """
    from wtd.wedge import WedgeSpec, standard_states
    from wtd.impact_sim import HammerSpec, SimConfig, simulate

    w, ham = WedgeSpec(), HammerSpec(mass=4e-3)
    r = simulate(w, standard_states()[3], ham, 1.58,
                 SimConfig(x_palpator=12.5e-3, t_end=3e-3))
    ww, dt = r["w_palp"], r["dt_rec"]

    def probe(mt):
        return SoftProbe(mass=0.68e-3, k_soft=4.47e4, preload=1.0,
                         zeta=0.005, tip_mass=mt)

    base = apply_soft_probe(ww, dt, probe(0.0))
    assert not base["despega"]
    # mientras haya contacto, la lectura es idéntica: la masa de punta no
    # entra en la ecuación de la masa, sólo en la fuerza de contacto
    for mt_mg in (5, 20):
        o = apply_soft_probe(ww, dt, probe(mt_mg * 1e-6))
        assert not o["despega"]
        assert o["a_pico_palpador_g"] == pytest.approx(
            base["a_pico_palpador_g"], rel=1e-9)
    # una punta pesada despega, y ahí la lectura se arruina: en vuelo la única
    # fuerza es la precarga, así que satura exactamente en F/m = 150 g. Es una
    # firma reconocible en el banco -- un recorte plano en el fondo de escala.
    o = apply_soft_probe(ww, dt, probe(100e-6))
    assert o["despega"]
    assert o["a_pico_palpador_g"] == pytest.approx(150.0, rel=0.01)
    # y la cota teórica cae donde debe
    assert 15.0 < base["m_punta_max_mg"] < 30.0


def test_la_rigidez_de_precarga_la_fija_el_posicionamiento_no_la_medicion():
    """Las dos flexuras no compiten: una va en serie y la otra en paralelo.

    Subir la rigidez de precarga 200× cuesta sólo un 20 % de separación, pero
    la tolerancia de posicionamiento cae de ±2 mm a ±0,01 mm. El factor 85
    entre las dos no sale de mantener limpia la medición: sale de cuánto
    puede errarle el brazo del crawler al estacionar.
    """
    from wtd.softprobe import PRELOAD_SWEEP
    kp = {r[0]: r for r in PRELOAD_SWEEP}
    # la medición casi no se entera
    assert kp[20.0][2] / kp[0.1][2] > 0.75
    # el posicionamiento sí
    assert kp[0.1][3] / kp[20.0][3] == pytest.approx(200.0, rel=0.05)
    # la elegida da una tolerancia que un brazo puede sostener
    assert kp[0.5][3] >= 0.4
    # y suma poco a la rigidez que fija f0
    assert 0.5 / 43.5 < 0.02
    # monotonía: más rígida, peor separación y menos tolerancia
    for a, b in zip(PRELOAD_SWEEP, PRELOAD_SWEEP[1:]):
        assert b[2] < a[2] and b[3] < a[3]


def test_el_amortiguamiento_tiene_piso_no_solo_techo():
    """Bajar ζ sube el Q, y en resonancia el relativo se amplifica por Q.

    Con ζ = 0,005 una vibración SOSTENIDA de 0,25 µm a f0 ya despega el
    palpador. Lo que salva al golpe es que llegar a Q pide ~Q ciclos y el
    transitorio dura ~1,3. Por eso conviene ζ = 0,02 y no menos.
    """
    from wtd.softprobe import RESONANCE_LIFTOFF
    by = {z: (Q, x, s) for z, Q, x, s in RESONANCE_LIFTOFF}
    # el límite de amplitud crece linealmente con zeta
    assert by[0.020][1] / by[0.005][1] == pytest.approx(4.0, rel=0.02)
    # y la fórmula cerrada lo reproduce: x_lim = 2 zeta F / k
    for z, Q, x_um, _ in RESONANCE_LIFTOFF:
        assert 2 * z * 1.0 / 43.5e3 * 1e6 == pytest.approx(x_um, rel=0.02)
    # el punto recomendado conserva la mayor parte de la separación
    assert by[0.020][2] / by[0.005][2] > 0.70


def test_transitorio_corto_no_llega_a_resonar():
    """Un seno de 1 µm a f0 despega con 20 ciclos pero no con 5.

    Es la razón por la que los 126 casos del golpe pasan con ζ = 0,005: el
    transitorio del impacto dura ~1,3 ciclos de f0, muy lejos de los ~Q
    ciclos que hace falta para construir la amplificación resonante.
    """
    p = SoftProbe(mass=0.68e-3, k_soft=4.47e4, preload=1.0, zeta=0.005)
    p.k_soft = 1.0 / (1.0 / 4.351e4 - 1.0 / p.k_hertz())
    f0 = p.f0()
    dt = 1.0 / (60.0 * f0)

    def rafaga(n_ciclos):
        t = np.arange(0.0, n_ciclos / f0, dt)
        return apply_soft_probe(1.0e-6 * np.sin(2 * math.pi * f0 * t), dt, p)

    assert not rafaga(5)["despega"]
    assert rafaga(20)["despega"]


def test_el_despegue_se_detecta_por_el_riel_plano():
    """En vuelo la única fuerza sobre el carro es la precarga, así que la
    lectura se clava en -F/m exacto. Con contacto continuo el riel no se
    toca nunca: es un detector binario sin falsos positivos."""
    from wtd.wedge import WedgeSpec, standard_states
    from wtd.impact_sim import HammerSpec, SimConfig, simulate

    w, ham = WedgeSpec(), HammerSpec(mass=4e-3)
    r = simulate(w, standard_states()[3], ham, 3.46,
                 SimConfig(x_palpator=12.5e-3, t_end=3e-3))
    ww, dt = r["w_palp"], r["dt_rec"]

    def muestras_en_el_riel(F):
        p = SoftProbe(mass=0.68e-3, k_soft=4.47e4, preload=F, zeta=0.02)
        o = apply_soft_probe(ww, dt, p)
        a = o["a_palpador"] / G
        riel = F / p.mass / G
        return o["despega"], int(np.sum(np.abs(a + riel) < 0.01 * riel))

    for F in (1.0, 0.7, 0.5, 0.35):
        despega, n = muestras_en_el_riel(F)
        assert not despega and n == 0
    despega, n = muestras_en_el_riel(0.25)
    assert despega and n > 50
