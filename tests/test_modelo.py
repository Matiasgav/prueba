"""Anclas del modelo integrado.

Estos tests no verifican fisica nueva: verifican que el MODELO como documento
sigue siendo coherente con el codigo que lo sostiene. Es lo que impide que el
relato y los numeros se separen sin que nadie se entere.
"""

import pytest

from wtd.modelo import (BANCO, EXTERNAS, K_HOMBRO_SENS, MODELO, ORIGENES,
                        riesgos, verificar_cadena)
from wtd.softprobe import G, design


def test_la_cadena_cierra():
    """Ningun bloque consume un simbolo que nadie produce.

    Es la propiedad que hace que el modelo se pueda leer de arriba hacia
    abajo sin saltos: cada entrada o viene de afuera (EXTERNAS) o la produjo
    un bloque anterior.
    """
    inf = verificar_cadena()
    assert inf["huerfanos"] == [], f"simbolos sin productor: {inf['huerfanos']}"
    assert inf["banco_inexistente"] == []
    assert inf["cierra"] is True
    assert inf["orden"] == ["B1", "B2", "B3", "B4", "B5", "B6"]


def test_todo_bloque_dice_como_se_verifica_y_que_pasa_si_falla():
    for b in MODELO:
        assert b.anclas or b.banco, f"{b.id} no declara verificacion"
        assert b.si_falla, f"{b.id} no dice que se cae si falla"
        assert b.pregunta.endswith("?"), f"{b.id} no contesta una pregunta"
        assert b.salidas, f"{b.id} no produce nada"


def test_los_valores_del_palpador_salen_del_codigo_y_no_del_relato():
    """B3 no puede quedar desactualizado respecto de `softprobe.design()`."""
    p = design()
    b3 = [b for b in MODELO if b.id == "B3"][0]
    assert b3.valor("m_movil") == pytest.approx(p.mass * 1e3, rel=1e-9)
    assert b3.valor("f0") == pytest.approx(p.f0(), rel=1e-9)
    assert b3.valor("k_medicion") == pytest.approx(p.k_series() / 1e3, rel=1e-9)
    assert b3.valor("a_despegue") == pytest.approx(p.a_liftoff() / G, rel=1e-9)
    # y el invariante sigue siendo F/m
    assert b3.valor("a_despegue") == pytest.approx(150.0, rel=1e-3)


def test_el_corte_del_palpador_cae_dentro_del_hueco_de_la_cuña():
    """La razon de ser de la cadena B2 -> B3, en una desigualdad."""
    b2 = [b for b in MODELO if b.id == "B2"][0]
    b3 = [b for b in MODELO if b.id == "B3"][0]
    f_suelta = b2.valor("f_suelta")
    f_asentada = b2.valor("f_asentada")
    f0 = b3.valor("f0")
    assert f_suelta < f0 < f_asentada
    #  y con holgura de mas de un orden de magnitud a cada lado
    assert f0 / f_suelta > 10
    assert f_asentada / f0 > 10
    #  el reparto de energia es total, no parcial
    assert b2.valor("banda_baja_S0") == 0.0
    assert b2.valor("banda_baja_S6") == 100.0


def test_el_riesgo_numero_uno_es_k_hombro():
    """La lista de riesgos tiene que nombrar la incognita que puede tumbar todo."""
    rs = riesgos()
    assert rs, "el modelo no declara ninguna hipotesis estimada"
    texto = " ".join(r["hipotesis"] for r in rs)
    assert "k_hombro" in texto
    #  y k_hombro tiene que ser externa y marcada como estimada
    kh = [m for m in EXTERNAS if m.simbolo == "k_hombro"][0]
    assert kh.origen == "E"
    #  la sensibilidad muestra la rodilla: con el hombro 10x mas blando la
    #  separacion se INVIERTE, y eso no lo arregla ningun palpador
    por_rel = dict((r, sep) for r, _f, sep in K_HOMBRO_SENS)
    assert por_rel[1.0] > 100
    assert por_rel[1 / 10] < 1
    assert por_rel[1 / 100] < por_rel[1 / 10]


def test_cada_ensayo_de_banco_mata_una_hipotesis_de_algun_bloque():
    ids = {e.id for e in BANCO}
    usados = {x for b in MODELO for x in b.banco}
    assert usados == ids, "hay ensayos que no le sirven a ningun bloque"
    for e in BANCO:
        assert e.criterio, f"el ensayo {e.id} no tiene criterio de aceptacion"
        assert e.mata, f"el ensayo {e.id} no dice que hipotesis mata"
        for bid in e.bloques:
            assert bid in {b.id for b in MODELO}
    #  el ensayo A es el que puede invalidar el enfoque, y no necesita palpador
    a = [e for e in BANCO if e.id == "A"][0]
    assert "NO necesita palpador" in a.instrumentos


def test_el_unico_bloque_abierto_es_el_clasificador():
    """Si algun dia se abre otro bloque, este test lo hace visible."""
    inf = verificar_cadena()
    assert inf["abiertos"] == ["B6"]
    b6 = [b for b in MODELO if b.id == "B6"][0]
    assert b6.valor("clasificador") == "PENDIENTE"


def test_toda_magnitud_declara_de_donde_sale():
    for m in EXTERNAS:
        assert m.origen in ORIGENES
    for b in MODELO:
        for s in b.salidas:
            assert s.origen in ORIGENES
            assert s.unidad, f"{b.id}/{s.simbolo} sin unidad"
