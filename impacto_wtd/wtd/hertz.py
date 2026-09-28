"""Contacto de Hertz esfera-plano para el impacto martillo/cuña.

Implementa literalmente las ecuaciones del brief §4.4 y §4.5:

    1/E* = (1-v1^2)/E1 + (1-v2^2)/E2
    k    = (4/3) E* sqrt(R)
    delta= (5 Ecin / (2k))^0.4
    F    = k delta^1.5
    a    = sqrt(R delta)
    p_med= F/(pi a^2)
    p_max= 1.5 p_med
    t_c  = 2.943 (5m/(4k))^0.4 v^(-1/5)

Verificado contra el ancla empírica del brief §9 (bola de acero de 8 mm
soltada desde 70 mm sobre cuña de G11):
    F = 165 N, p_max = 900 MPa, t_c = 55 us.

Nota sobre el modelo: es Hertz elástico cuasi-estático con la corrección
clásica de Timoshenko para la duración de contacto de un impacto sin
deformación plástica ni disipación. Sobrestima la fuerza pico y subestima
la duración cuando hay fluencia local (>640 MPa en G11), que es el régimen
en el que se trabaja. Ver `hertz_plastic_correction`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .materials import G11_DAMAGE, Material


def reduced_modulus(m1: Material, m2: Material) -> float:
    """Módulo de contacto equivalente E* [Pa]."""
    inv = (1.0 - m1.nu ** 2) / m1.E + (1.0 - m2.nu ** 2) / m2.E
    return 1.0 / inv


def contact_stiffness(R: float, m1: Material, m2: Material) -> float:
    """k = (4/3) E* sqrt(R)  [N/m^1.5]."""
    return (4.0 / 3.0) * reduced_modulus(m1, m2) * math.sqrt(R)


@dataclass(frozen=True)
class HertzResult:
    E_kin: float       # energía cinética normal incidente [J]
    v: float           # velocidad normal incidente [m/s]
    m: float           # masa impactante efectiva [kg]
    R: float           # radio de la punta [m]
    E_star: float      # módulo reducido [Pa]
    k: float           # rigidez de contacto [N/m^1.5]
    delta: float       # indentación máxima [m]
    F: float           # fuerza máxima de contacto [N]
    a: float           # radio del círculo de contacto [m]
    p_mean: float      # presión media [Pa]
    p_max: float       # presión hertziana pico [Pa]
    t_c: float         # duración de contacto [s]
    f_knee: float      # 1/(2 t_c): frecuencia donde el espectro cae [Hz]
    regime: str        # 'elastico' | 'fluencia_local' | 'plastificacion'

    def as_dict(self) -> dict:
        return {
            "E_kin_mJ": self.E_kin * 1e3,
            "v_ms": self.v,
            "m_g": self.m * 1e3,
            "R_mm": self.R * 1e3,
            "E_star_GPa": self.E_star / 1e9,
            "delta_um": self.delta * 1e6,
            "F_N": self.F,
            "a_mm": self.a * 1e3,
            "p_max_MPa": self.p_max / 1e6,
            "t_c_us": self.t_c * 1e6,
            "f_knee_kHz": self.f_knee / 1e3,
            "regime": self.regime,
        }


def classify_regime(p_max: float) -> str:
    if p_max < G11_DAMAGE["elastic_max"]:
        return "elastico"
    if p_max < G11_DAMAGE["yield_local_max"]:
        return "fluencia_local"
    return "plastificacion"


def hertz_impact(
    E_kin: float,
    m: float,
    R: float,
    tip: Material,
    target: Material,
) -> HertzResult:
    """Impacto de una esfera de radio R y masa m con energía cinética E_kin."""
    if E_kin <= 0 or m <= 0 or R <= 0:
        raise ValueError("E_kin, m y R deben ser positivos")
    E_star = reduced_modulus(tip, target)
    k = contact_stiffness(R, tip, target)
    v = math.sqrt(2.0 * E_kin / m)
    delta = (5.0 * E_kin / (2.0 * k)) ** 0.4
    F = k * delta ** 1.5
    a = math.sqrt(R * delta)
    p_mean = F / (math.pi * a ** 2)
    p_max = 1.5 * p_mean
    t_c = 2.943 * (5.0 * m / (4.0 * k)) ** 0.4 * v ** (-0.2)
    return HertzResult(
        E_kin=E_kin, v=v, m=m, R=R, E_star=E_star, k=k, delta=delta,
        F=F, a=a, p_mean=p_mean, p_max=p_max, t_c=t_c,
        f_knee=0.5 / t_c, regime=classify_regime(p_max),
    )


def hertz_from_velocity(v: float, m: float, R: float,
                        tip: Material, target: Material) -> HertzResult:
    return hertz_impact(0.5 * m * v * v, m, R, tip, target)


def max_energy_for_pressure(
    p_limit: float, m: float, R: float, tip: Material, target: Material,
) -> float:
    """Energía cinética máxima que mantiene p_max <= p_limit.

    Cerrada analíticamente: p_max ∝ E_kin^0.2, así que se resuelve
    escalando desde un punto de referencia.
    """
    ref = hertz_impact(1e-3, m, R, tip, target)   # 1 mJ de referencia
    return 1e-3 * (p_limit / ref.p_max) ** 5.0


def hertz_plastic_correction(res: HertzResult, target: Material,
                             p_y: float | None = None) -> dict:
    """Corrección de primer orden por fluencia local (modelo de Tabor/Johnson).

    Cuando p_max supera la presión de fluencia p_y del material, el contacto
    deja de ser hertziano: la presión media se satura en ~p_y (luego ~H, la
    dureza) y el área crece más rápido. Consecuencias para el ensayo:

      * La fuerza pico REAL es menor que la hertziana.
      * La duración de contacto REAL es MAYOR (contacto más blando).
      * Aparece disipación: parte de la energía no vuelve al martillo,
        lo que baja el coeficiente de restitución independientemente
        del ajuste de la cuña  ->  sesgo sistemático en el índice Leeb.

    Se usa el modelo de área saturada: A_p = F/p_y con p_y = 640 MPa (umbral
    elástico de §4.5, coherente con p_y ~ H/3).

    Devuelve estimaciones y NO reemplaza al resultado hertziano: se reporta
    como banda de incertidumbre.
    """
    if p_y is None:
        p_y = G11_DAMAGE["elastic_max"]
    if res.p_max <= p_y:
        return {"plastic": False, "F_ratio": 1.0, "tc_ratio": 1.0,
                "e_plastic": 1.0, "energy_lost_frac": 0.0}

    # Johnson (1985) §11.4: para impacto elastoplástico completamente
    # desarrollado el coeficiente de restitución escala como
    #     e ≈ 3.8 (p_y/E*)^(1/2) * (E* / (rho v^2))^(1/8) ... (forma reducida)
    # Se usa la forma práctica e = (v_y/v)^(1/4) válida para v >> v_y,
    # con v_y la velocidad a la que se inicia la fluencia.
    #
    # La energía de fluencia sale del escalado exacto p_max ∝ E_cin^0.2, sin
    # reconstruir materiales: hacerlo con un material equivalente de E = E*
    # volvía a sumar la flexibilidad del blanco y daba una E_y ~2.5 veces
    # menor de la correcta.
    E_y = res.E_kin * (p_y / res.p_max) ** 5.0
    v_y = math.sqrt(2.0 * E_y / res.m)
    e_pl = min(1.0, (v_y / res.v) ** 0.25)
    # Fuerza saturada: F ~ p_y * pi * a^2 con a creciendo por conservación
    # de energía plástica. Aproximación: F_p / F_h = (p_y/p_max)^(?) -> se usa
    # el cociente de presiones medias, acotado.
    F_ratio = min(1.0, (p_y / res.p_max) ** 0.5)
    tc_ratio = 1.0 / max(F_ratio, 1e-3) ** 0.5
    return {
        "plastic": True,
        "p_y_MPa": p_y / 1e6,
        "v_yield_ms": v_y,
        "E_yield_mJ": E_y * 1e3,
        "F_ratio": F_ratio,
        "tc_ratio": tc_ratio,
        "e_plastic": e_pl,
        "energy_lost_frac": 1.0 - e_pl ** 2,
    }


def indentation_fatigue_cycles(p_max: float, target: Material) -> dict:
    """Estimación gruesa de daño acumulado por impactos repetidos en G11.

    No hay curva S-N de indentación esférica sobre G11 en la literatura
    abierta. Se usa la regla práctica de "shakedown" de contacto rodante /
    percusivo (Johnson §9.3): por debajo del límite de shakedown
    p_max <= 1.6 p_y no hay acumulación de deformación plástica: el primer
    impacto genera tensiones residuales que hacen elásticos los siguientes.

    Con p_y = 640 MPa  ->  límite de shakedown ~1024 MPa.

    Es una ESTIMACIÓN [E]. Resuelve la incógnita "cuántos golpes aguanta el
    mismo punto" sólo cualitativamente; hay que verificarla en mock-up.
    """
    p_y = G11_DAMAGE["elastic_max"]
    shakedown = 1.6 * p_y
    if p_max <= p_y:
        verdict = "elastico_puro"
        n_ok = float("inf")
    elif p_max <= shakedown:
        verdict = "shakedown"          # se acomoda tras los primeros golpes
        n_ok = float("inf")
    elif p_max <= G11_DAMAGE["yield_local_max"]:
        verdict = "ratcheting_lento"
        # Ratcheting: delta_plastica por golpe ~ (p/p_sd - 1) * delta_elastica.
        # Se limita a que la huella acumulada no supere 50 um en N golpes.
        n_ok = 1.0 / max(1e-6, (p_max / shakedown - 1.0)) * 100.0
    else:
        verdict = "indentacion_visible"
        n_ok = 1.0
    return {"p_max_MPa": p_max / 1e6, "p_shakedown_MPa": shakedown / 1e6,
            "verdict": verdict, "N_golpes_admisibles": n_ok}
