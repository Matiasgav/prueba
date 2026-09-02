"""Confiabilidad: vida, desgaste, deriva y modos de falla del módulo.

Población de referencia (estimada, marcar como [E] y confirmar con el
usuario): un generador grande tiene del orden de 40 a 60 ranuras y entre 15
y 25 cuñas por ranura, o sea 600 a 1500 posiciones. Con 20 golpes por
posición son 12.000 a 30.000 golpes por máquina. Una herramienta que atienda
100 máquinas en su vida acumula 1.2 a 3 millones de ciclos. Se dimensiona
para 1e7, que da un factor 3 a 8 sobre el uso previsto.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

DESIGN_CYCLES = 1e7


def duty_estimate(slots: int = 48, wedges_per_slot: int = 20,
                  hits_per_point: int = 20, machines: int = 100) -> dict:
    per_machine = slots * wedges_per_slot * hits_per_point
    return {"posiciones_por_maquina": slots * wedges_per_slot,
            "golpes_por_maquina": per_machine,
            "golpes_vida_util": per_machine * machines,
            "ciclos_de_diseño": DESIGN_CYCLES,
            "factor": DESIGN_CYCLES / (per_machine * machines)}


def archard_wear(F_normal: float, sliding_m: float, hardness_Pa: float,
                 K: float = 1e-7) -> dict:
    """Volumen desgastado por Archard: V = K F s / H."""
    V = K * F_normal * sliding_m / hardness_Pa
    return {"V_mm3": V * 1e9, "F_N": F_normal, "s_km": sliding_m / 1e3,
            "K": K}


def guide_wear(cycles: float, travel_per_cycle: float, F_normal: float,
               hardness_HV: float = 700.0, K: float = 1e-7,
               contact_area_mm2: float = 20.0) -> dict:
    H = hardness_HV * 9.80665e6   # HV -> Pa
    s = cycles * travel_per_cycle
    w = archard_wear(F_normal, s, H, K)
    depth_um = w["V_mm3"] / contact_area_mm2 * 1e3
    return {**w, "ciclos": cycles, "profundidad_um": depth_um,
            "aceptable": depth_um < 10.0}


def tip_wear_note() -> dict:
    """El material de la punta no cambia la mecánica pero sí el desgaste.

    E* está dominado por el G11: pasar de acero (E=210 GPa) a carburo de
    tungsteno (600 GPa) sube E* apenas 5.6 %, porque 1/E* = (1-v1^2)/E1 +
    (1-v2^2)/E2 con el segundo término 11 veces mayor. O sea que elegir la
    punta por rigidez de contacto no tiene sentido.

    Lo que sí cambia es el desgaste: el G11 es epoxi CON FIBRA DE VIDRIO, y
    la fibra de vidrio es abrasiva (dureza ~ 600 HV, comparable a un acero
    templado). Un millón de impactos contra fibra de vidrio redondea una
    punta de acero. Por eso la punta va de carburo de tungsteno o de nitruro
    de silicio: por abrasión, no por rigidez.
    """
    return {
        "delta_E_star_acero_a_WC_pct": 5.6,
        "criterio_correcto": "resistencia a la abrasión, no rigidez",
        "recomendado": "WC-Co 6 % o Si3N4, radio >= 8 mm, rugosidad Ra <= 0.1 um",
        "riesgo": ("una punta que se desgasta CAMBIA el radio y por lo tanto "
                   "t_c y p_max: es una deriva sistemática del instrumento, "
                   "no un ruido. Hay que verificar el radio con un patrón "
                   "cada cierto número de golpes"),
    }


@dataclass
class FailureMode:
    item: str
    mode: str
    effect: str
    severity: int      # 1-10
    likelihood: int    # 1-10
    detection: int     # 1-10 (10 = no se detecta)
    mitigation: str

    @property
    def rpn(self) -> int:
        return self.severity * self.likelihood * self.detection

    def as_dict(self) -> dict:
        return {**self.__dict__, "rpn": self.rpn}


def fmea() -> list[dict]:
    modes = [
        FailureMode(
            "Proyectil", "Agarrotamiento en la guía por contaminación",
            "No hay golpe, o golpe de energía desconocida", 8, 5, 3,
            "Guía con huelgo diametral >= 40 um, venteo con laberinto, "
            "recubrimiento DLC, y detección por el propio sensor inductivo "
            "(si no ve el vuelo, el tiro es inválido)"),
        FailureMode(
            "Proyectil", "Doble impacto por rebote no capturado",
            "Corrompe el ring-down y el índice de rebote", 6, 7, 2,
            "Tope elastomérico en la culata dimensionado para dejar el "
            "segundo impacto por debajo del 5 % de energía; la ventana de "
            "análisis se cierra antes, y el sensor VE el segundo impacto"),
        FailureMode(
            "Acumulador", "Fatiga del resorte / barra de torsión",
            "Deriva de energía y eventual rotura", 9, 2, 6,
            "Diseño a vida infinita por Goodman con n >= 1.5, granallado, "
            "presetting; verificación de energía por el sensor en cada tiro"),
        FailureMode(
            "Traba de disparo", "Desgaste del diente de la traba mecánica",
            "Deriva del punto de disparo -> deriva de energía", 5, 8, 4,
            "Traba MAGNÉTICA sin contacto deslizante bajo carga; si se usa "
            "traba mecánica, superficies de WC y verificación periódica"),
        FailureMode(
            "Punta", "Redondeo por abrasión contra fibra de vidrio",
            "Cambia R -> cambia t_c y p_max -> deriva del espectro", 6, 6, 7,
            "Punta de WC o Si3N4; patrón de verificación de radio; "
            "seguimiento del t_c medido, que es un testigo directo de R"),
        FailureMode(
            "Cuña (objeto)", "Indentación acumulada por golpes repetidos",
            "Daño al activo del cliente; inaceptable", 10, 3, 5,
            "Radio de punta >= 12 mm para mantener p_max por debajo del "
            "límite de shakedown (1024 MPa); ver estudio de daño"),
        FailureMode(
            "Sensor inductivo", "Deriva térmica del demodulador",
            "Error de velocidad -> error de energía", 5, 5, 5,
            "Referencia diferencial (dos bobinas), calibración por el tramo "
            "de vuelo libre con aceleración conocida (g)"),
        FailureMode(
            "Módulo", "Choque contra la cuña por error de posicionamiento",
            "Daño al módulo y a la cuña", 7, 3, 3,
            "Palpador de contacto que define la separación mecánicamente y "
            "actúa de tope; el palpador ya está en la arquitectura para el "
            "acelerómetro"),
        FailureMode(
            "Amartillado", "Motor/husillo trabado por par excesivo en frío",
            "Se pierde el ciclo", 4, 4, 2,
            "Límite de corriente y detección de calado; el amartillado es "
            "cuasiestático, sobra par"),
        FailureMode(
            "Cadena de medida", "Saturación del acelerómetro",
            "Se pierde el pico y el índice queda mal", 6, 5, 4,
            "Rango >= 2x el pico esperado con margen de 6 dB, y detección "
            "de recorte por software"),
    ]
    return sorted([m.as_dict() for m in modes], key=lambda d: -d["rpn"])


def recoil_analysis(m_proj: float, v: float, m_crawler: float,
                    t_contact: float, hold_force: float) -> dict:
    """Reacción sobre el crawler.

    RESULTADO IMPORTANTE, y es una ventaja estructural del vuelo libre: la
    reacción del IMPACTO no pasa por el módulo. El proyectil está en vuelo
    libre, así que la fuerza de contacto sólo se cierra entre el proyectil y
    la cuña. Lo único que el crawler siente es la reacción del LANZAMIENTO,
    que dura mil veces más y vale una décima parte.

    Un martillo rígido (palanca, actuador directo) sí cierra el lazo de
    fuerza contra el chasis y le mete al crawler el pico completo.
    """
    p = m_proj * v
    F_impact_peak = math.pi / 2.0 * p / t_contact     # pulso medio seno
    return {
        "impulso_mNs": p * 1e3,
        "F_pico_impacto_N": F_impact_peak,
        "F_pico_sobre_crawler_vuelo_libre_N": 0.0,
        "dv_crawler_si_rigido_mm_s": p / m_crawler * 1e3,
        "desplazamiento_durante_contacto_um": p / m_crawler * t_contact * 1e6,
        "fuerza_de_retencion_N": hold_force,
        "margen_si_rigido": hold_force / F_impact_peak,
        "conclusion": ("con vuelo libre la reacción del impacto NO pasa por "
                       "el crawler; con martillo rígido haría falta una "
                       "retención de " + f"{F_impact_peak:.0f} N"),
    }


def launch_reaction(E: float, stroke: float, m_proj: float,
                    m_drive_eff: float) -> dict:
    """Reacción del lanzamiento sobre el chasis (la que sí existe)."""
    F_avg = E / stroke
    m = m_proj + m_drive_eff
    t = math.sqrt(2.0 * stroke * m / F_avg)
    return {"F_media_N": F_avg, "t_lanzamiento_ms": t * 1e3,
            "impulso_mNs": F_avg * t * 1e3}
