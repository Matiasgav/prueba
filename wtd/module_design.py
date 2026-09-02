"""Diseño del módulo de impacto 10 x 10 x (50-60) mm.

DECISIÓN DE ORIENTACIÓN — la incógnita #1, resuelta como bifurcación

El usuario pide un módulo de 10 x 10 x 50 (o 60) mm. No dice cómo se orienta
el eje largo, y de eso depende TODO:

  * FAMILIA A — el eje de 50 mm es RADIAL (dirección del golpe).
    El módulo es un cañón: el proyectil acelera a lo largo de 20-30 mm y sale
    por la boca. Es la arquitectura de una sonda Leeb.
    REQUISITO: unos 55 mm de espacio radial. Incompatible con el chasis de
    10 mm del brief §2, pero perfectamente compatible con un ensayo con el
    rotor afuera.

  * FAMILIA B — el eje de 50 mm es AXIAL (a lo largo del eje del generador),
    y quedan 10 mm en la dirección radial.
    Compatible con el chasis de 10 mm. La carrera de aceleración se reduce a
    ~4.5 mm y hace falta un acumulador de energía que trabaje con ángulo en
    vez de con carrera lineal.

No se adivina cuál corresponde: se dimensionan las dos y se reporta el costo
en mJ de elegir la que cabe en 10 mm.

EL TEOREMA DEL TREN DE TRANSMISIÓN (por qué no sirve convertir dirección)

Para una transmisión de relación i = v_proyectil / v_accionamiento, la
fracción de energía que llega al proyectil es

        E_proj / E_total = m_p / (m_p + m_acc / i^2)

Bajar i (reducir velocidad en el proyectil para ganar fuerza) amplifica la
inercia reflejada del accionamiento por 1/i^2. Cualquier arquitectura que
cambie carrera por fuerza paga cuadráticamente en inercia reflejada. Las
únicas salidas son i = 1 (accionamiento directo) o masa de accionamiento
despreciable.

Ese teorema explica de una los tres resultados sueltos del brief:
  * la palanca en L con relación 1.66 deja el 43 % de la energía en el
    actuador (§5);
  * una leva de conversión X->Y con angulo chico es todavía peor;
  * la barra de torsión es la excepción: su "carrera" es un ÁNGULO, su
    inercia reflejada al proyectil es del orden de 1e-4 g, y por eso es el
    acumulador correcto cuando la carrera lineal está limitada.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .materials import STEEL, TUNGSTEN_HEAVY, Material
from .springs import (HelicalSpring, LeafSpring, TorsionBar,
                      wire_tensile_strength)


# --------------------------------------------------------------------------

def transmission_efficiency(m_proj: float, m_drive: float, i: float) -> float:
    """Fracción de la energía que termina en el proyectil."""
    return m_proj / (m_proj + m_drive / i ** 2)


@dataclass
class Envelope:
    width: float = 10e-3     # [m]  Z, circunferencial
    height: float = 10e-3    # [m]  Y
    length: float = 55e-3    # [m]  X
    wall: float = 1.0e-3     # espesor de pared/estructura [m]

    @property
    def volume(self) -> float:
        return self.width * self.height * self.length


@dataclass
class Projectile:
    """Proyectil libre. La masa es la variable de diseño principal."""

    diameter: float = 7.8e-3
    length: float = 14e-3
    material: Material = STEEL
    tip_radius: float = 8e-3
    tip_material: Material = STEEL

    @property
    def volume(self) -> float:
        return math.pi * self.diameter ** 2 / 4.0 * self.length

    @property
    def mass(self) -> float:
        return self.material.rho * self.volume

    def summary(self) -> dict:
        return {"d_mm": self.diameter * 1e3, "L_mm": self.length * 1e3,
                "material": self.material.name, "mass_g": self.mass * 1e3,
                "R_punta_mm": self.tip_radius * 1e3}


def prism_projectile_mass(w: float, h: float, l: float,
                          material: Material = STEEL) -> float:
    return material.rho * w * h * l


# --------------------------------------------------------------------------
# FAMILIA A — cañón radial
# --------------------------------------------------------------------------

def design_barrel_spring(stroke: float, E_target: float, bore: float,
                         L_available: float = 42e-3,
                         d_grid=None, C_grid=None,
                         peened: bool = True,
                         preload_ratio: float = 0.35,
                         n_min: float = 3.0, n_max: float = 60.0) -> dict:
    """Dimensiona el resorte helicoidal del cañón.

    Para cada par (diámetro de alambre, índice C = D/d) la rigidez que hace
    falta queda FIJADA por la energía y la carrera, así que el número de
    espiras se DESPEJA en vez de barrerse:

        F2 = 2 E / (s (1 + r)),   F1 = r F2,   k = (F2 - F1)/s
        n  = G d^4 / (8 D^3 k)

    La precarga r aplana la curva de fuerza: para la misma energía baja la
    fuerza pico y por lo tanto la tensión. El precio es longitud libre.

    Restricciones de empaque:
        OD = D + d <= bore - holgura
        longitud ocupada = L_solida + carrera <= L_available
        (la longitud ocupada es la del resorte en su posición MÁS LARGA, o
         sea al final del disparo, todavía con la precarga F1 aplicada)
    """
    d_grid = d_grid if d_grid is not None else np.arange(0.20, 1.60, 0.01) * 1e-3
    C_grid = C_grid if C_grid is not None else np.arange(4.0, 16.0, 0.25)
    F2 = 2.0 * E_target / (stroke * (1.0 + preload_ratio))
    F1 = preload_ratio * F2
    k_req = (F2 - F1) / stroke
    best = None
    for d in d_grid:
        for C in C_grid:
            D = C * d
            if D + d > bore - 0.4e-3:
                continue
            n = STEEL_G_SPRING * d ** 4 / (8.0 * D ** 3 * k_req)
            if not (n_min <= n <= n_max):
                continue
            sp = HelicalSpring(float(d), float(D), float(n), peened=peened)
            L_occupied = sp.solid_length + stroke
            if L_occupied > L_available:
                continue
            fat = sp.fatigue(F2, F1)
            tau = sp.shear_stress(F2)
            cand = {
                "d_mm": d * 1e3, "D_mm": D * 1e3, "n_a": float(n),
                "C": float(C), "k_N_m": sp.k, "F1_N": F1, "F2_N": F2,
                "tau_max_MPa": tau / 1e6, "n_goodman": fat.n_goodman,
                "vida_infinita": fat.infinite_life,
                "Sse_MPa": fat.Sse / 1e6, "Ssu_MPa": fat.Ssu / 1e6,
                "L_occupied_mm": L_occupied * 1e3,
                "L_solid_mm": sp.solid_length * 1e3,
                "L_free_mm": (sp.solid_length + F2 / sp.k + 0.5e-3) * 1e3,
                "OD_mm": sp.outer_diameter * 1e3,
                "mass_g": sp.mass * 1e3, "m_eff_g": sp.mass / 3.0 * 1e3,
                "f_surge_Hz": sp.surge_frequency(),
                "E_mJ": 0.5 * (F1 + F2) * stroke * 1e3,
                "stroke_mm": stroke * 1e3,
            }
            key = (not cand["vida_infinita"], -cand["n_goodman"])
            if best is None or key < best[0]:
                best = (key, cand)
    return best[1] if best else {}


STEEL_G_SPRING = 79.3e9


# --------------------------------------------------------------------------
# FAMILIA B — módulo acostado, acumulador de torsión
# --------------------------------------------------------------------------

def torsion_energy_limit(d: float, phi: float, tau: float = 600e6) -> float:
    """E_max = pi d^3 phi tau / 32.

    Se obtiene de E = (1/2) G Jp phi^2 / L con la restricción
    tau = G phi d / (2 L): la longitud desaparece. La energía de una barra de
    torsión sólo depende del diámetro, del ángulo utilizable y de la tensión
    admisible; la longitud es la que hace falta para llegar a ese ángulo.
    """
    return math.pi * d ** 3 * phi * tau / 32.0


def torsion_length_needed(d: float, phi: float, tau: float = 600e6,
                          Gmod: float = 79.3e9) -> float:
    """L = phi G d / (2 tau)."""
    return phi * Gmod * d / (2.0 * tau)


def design_torsion_accumulator(stroke: float, crank_r: float,
                               module_len: float, n_folds: int = 2,
                               tau: float = 600e6, Gmod: float = 79.3e9,
                               margin: float = 0.92) -> dict:
    """Dimensiona la barra de torsión del módulo acostado.

    El cigüeñal barre simétricamente respecto de la perpendicular, así que
        stroke = 2 * crank_r * sin(phi/2)
    Con `n_folds` tramos en serie (barra en U, en W, ...) la longitud activa
    es n_folds veces la longitud del módulo: es lo que permite llegar a
    ángulos grandes con diámetros útiles.
    """
    ratio = stroke / (2.0 * crank_r)
    if ratio >= 1.0:
        return {"feasible": False,
                "reason": "carrera mayor que el diámetro del cigüeñal"}
    phi = 2.0 * math.asin(ratio)
    L_active = n_folds * module_len * margin
    d = 2.0 * tau * L_active / (Gmod * phi)
    E = torsion_energy_limit(d, phi, tau)
    Jp = math.pi * d ** 4 / 32.0
    k_t = Gmod * Jp / L_active
    T = tau * Jp / (d / 2.0)
    F_crank = T / crank_r
    bar = TorsionBar(d=d, L=L_active, tau_allow=tau, G=Gmod)
    # inercia reflejada al proyectil
    J_bar = bar.mass * (d / 2.0) ** 2 / 2.0 / 3.0
    m_refl = J_bar / crank_r ** 2
    return {
        "feasible": True,
        "phi_rad": phi, "phi_deg": math.degrees(phi),
        "d_mm": d * 1e3, "L_active_mm": L_active * 1e3, "n_folds": n_folds,
        "k_t_Nm_rad": k_t, "T_max_Nm": T, "F_crank_N": F_crank,
        "E_mJ": E * 1e3, "E_check_mJ": 0.5 * k_t * phi ** 2 * 1e3,
        "bar_mass_g": bar.mass * 1e3,
        "m_reflected_g": m_refl * 1e3,
        "crank_r_mm": crank_r * 1e3, "stroke_mm": stroke * 1e3,
        # La excursión VERTICAL de la punta del cigüeñal es la carrera, no el
        # diámetro de giro: la punta recorre un arco de radio crank_r pero su
        # proyección en Y vale 2 r sin(phi/2) = carrera. Lo que hay que alojar
        # en altura es carrera + diámetro de la barra + holgura.
        "height_needed_mm": (stroke + d + 1.0e-3) * 1e3,
        "x_swing_mm": crank_r * (1.0 - math.cos(phi / 2.0)) * 1e3,
        "fits_height": (stroke + d + 1.0e-3) < 8.0e-3,
    }


# --------------------------------------------------------------------------
# Catálogo de arquitecturas
# --------------------------------------------------------------------------

@dataclass
class Architecture:
    aid: str
    name: str
    family: str            # 'A' cañón radial | 'B' módulo acostado | 'X' descartada
    principle: str
    free_flight: str       # calidad del vuelo libre
    E_proj_mJ: float
    m_proj_g: float
    v_ms: float
    stroke_mm: float
    parasitic_pct_weight: float   # fuerzas parásitas en vuelo, % del peso
    rate_hz: float
    wear_parts: str
    cocking_power_W: float
    fits_10mm: bool
    trl: int               # 1-9
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    notes: str = ""

    def as_dict(self) -> dict:
        d = dict(self.__dict__)
        return d
