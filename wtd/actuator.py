"""Actuadores: el LAH04 de catálogo y los modelos de escalado que hacen
falta para evaluar alternativas dentro del envolvente 10x10x(50-60).

Contiene:
  * `LAH04`               — datos verificados de ficha + curva K_F(x) digitizada.
  * `work_over_window`    — trabajo electromagnético integrado.
  * `FlatVoiceCoil`       — VCA plano tipo "racetrack", escalado por B·I·L.
  * `ReluctanceActuator`  — solenoide plano, escalado por B^2·A/(2·mu0).
  * `thermal_budget`      — duty, I_rms, potencia media.

Todo lo que sale de escalado va marcado [E]: son modelos de primer orden
verificados dimensionalmente, no reemplazan un FEM magnético.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .materials import MU0

# --------------------------------------------------------------------------
# Sensata / BEI Kimco LAH04-10-000A
# --------------------------------------------------------------------------

LAH04 = {
    "name": "Sensata/BEI Kimco LAH04-10-000A",
    "F_peak_N": 1.89,          # [V] ficha
    "F_cont_N": 1.11,          # [V] ficha
    "K_actuator_N_sqrtW": 0.84,  # [V] ficha
    "stroke_m": 4.0e-3,        # [V] ficha
    "OD_m": 10.1e-3,           # [V] ficha
    "length_mid_m": 25.4e-3,   # [V] ficha
    "R_ohm": 5.1,              # [E] informe original
    "L_H": 220e-6,             # [E]
    "tau_e_s": 43.1e-6,        # [E]
    "moving_mass_kg": 3.49e-3,  # [E]
    "total_mass_kg": 10e-3,    # [E]
    "life_cycles": 500e6,      # [V] familia housed
}

# Curva K_F(x) digitizada del informe original [E]. x respecto del centro.
LAH04_CURVE_X = np.array(
    [-2.0, -1.6, -1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0]) * 1e-3
LAH04_CURVE_F = np.array(
    [1.31, 1.55, 1.72, 1.82, 1.87, 1.89, 1.87, 1.82, 1.72, 1.55, 1.31])


def force_constant_from_datasheet(K_act: float = LAH04["K_actuator_N_sqrtW"],
                                  R: float = LAH04["R_ohm"]) -> float:
    """K_F = K_actuator * sqrt(R)  [N/A]  (brief §3.2)."""
    return K_act * math.sqrt(R)


def work_over_window(window: float, current: float = 1.0,
                     x: np.ndarray = LAH04_CURVE_X,
                     F: np.ndarray = LAH04_CURVE_F,
                     n: int = 4001) -> float:
    """Trabajo electromagnético sobre una ventana centrada [J].

    Integración trapezoidal con interpolación lineal en los extremos, que es
    exactamente lo que reproduce los valores ancla del brief §3.3
    (5.39 mJ en 3.0 mm, 6.16 mJ en 3.5 mm, 6.85 mJ en 4.0 mm).
    """
    half = window / 2.0
    if half > x[-1] + 1e-15:
        raise ValueError("ventana mayor que la carrera disponible")
    xs = np.linspace(-half, half, n)
    Fs = np.interp(xs, x, F) * current
    return float(np.trapezoid(Fs, xs))


def thermal_budget(I_pulse: float, t_pulse: float, rate_hz: float,
                   R: float = LAH04["R_ohm"],
                   P_cont: float | None = None) -> dict:
    """Duty, corriente eficaz y potencia media frente al límite continuo."""
    if P_cont is None:
        I_cont = LAH04["F_cont_N"] / force_constant_from_datasheet()
        P_cont = I_cont ** 2 * R
    duty = t_pulse * rate_hz
    I_rms = I_pulse * math.sqrt(duty)
    P_avg = I_rms ** 2 * R
    return {"duty": duty, "I_rms_A": I_rms, "P_avg_W": P_avg,
            "P_cont_W": P_cont, "margin": P_cont / P_avg if P_avg > 0 else
            float("inf")}


# --------------------------------------------------------------------------
# Escalados para el envolvente 10 x 10 x 50
# --------------------------------------------------------------------------

@dataclass
class FlatVoiceCoil:
    """VCA plano de bobina tipo 'racetrack' (pista de atletismo).

    El brief §2.1 propone el VCA plano como la salida correcta al problema de
    empaque. Con el módulo de 50 mm de largo, la bobina puede ser mucho más
    grande que la del LAH04 cilíndrico de 10.1 mm.

    Modelo [E]: F = B * I * L_wire_activo, con L_wire = N * 2 * l_recta
    (sólo los dos tramos rectos, de longitud l_recta, están en el entrehierro
    útil; las curvas no aportan fuerza neta útil).

    Límite térmico: densidad de corriente J en el cobre, con factor de
    llenado kf sobre la sección de bobina (w_coil x h_coil).
    """

    l_straight: float = 40e-3    # largo del tramo recto de la espira [m]
    w_coil: float = 2.0e-3       # ancho de la sección de bobina [m]
    h_coil: float = 6.0e-3       # alto de la sección de bobina [m]
    B_gap: float = 0.55          # densidad de flujo en el entrehierro [T]
    fill_factor: float = 0.55    # factor de llenado de cobre [-]
    stroke: float = 4.0e-3       # carrera [m]
    rho_cu: float = 1.72e-8      # resistividad del cobre a 20 C [ohm m]
    moving_mass: float = 4.0e-3  # masa móvil (imán + porta) [kg]

    @property
    def copper_area(self) -> float:
        return self.w_coil * self.h_coil * self.fill_factor

    def force(self, J: float) -> float:
        """Fuerza a densidad de corriente J [A/m^2] en el cobre.

        F = B * J * A_cu * l_straight * 2  (los dos lados de la espira).
        La fuerza NO depende del número de vueltas: sólo del producto
        corriente x vueltas, que es lo que fija A_cu * J.
        """
        return 2.0 * self.B_gap * J * self.copper_area * self.l_straight

    def power(self, J: float) -> float:
        """Disipación [W]: P = rho * J^2 * Volumen_cu."""
        # Longitud media de la espira: 2*(l_straight + w_coil) aprox.
        vol_cu = self.copper_area * 2.0 * (self.l_straight + self.h_coil)
        return self.rho_cu * J ** 2 * vol_cu

    def force_constant_N_sqrtW(self, J_ref: float = 5e6) -> float:
        return self.force(J_ref) / math.sqrt(self.power(J_ref))

    def work(self, J: float) -> float:
        """Trabajo sobre la carrera (fuerza constante, VCA ideal) [J]."""
        return self.force(J) * self.stroke

    def summary(self, J: float = 20e6) -> dict:
        F = self.force(J)
        P = self.power(J)
        return {
            "J_A_mm2": J / 1e6,
            "F_N": F,
            "P_W": P,
            "K_N_sqrtW": self.force_constant_N_sqrtW(),
            "W_stroke_mJ": self.work(J) * 1e3,
            "a_max_ms2": F / self.moving_mass,
            "stroke_mm": self.stroke * 1e3,
        }


@dataclass
class ReluctanceActuator:
    """Actuador de reluctancia (solenoide) plano tipo E, de tracción.

    Modelo [E] de primer orden: fuerza de Maxwell sobre las caras polares,
        F = B^2 * A_polo / (2 mu0)
    con B limitada por saturación del hierro y por la fmm disponible:
        B = mu0 * N I / (2 g)   mientras no sature.

    Es el actuador más fuerte por unidad de volumen a entrehierro chico, y
    es la razón por la que el solenoide existente de GRIS (53.5 mJ) le gana
    por 20x al voice coil. Su problema es que la fuerza va como 1/g^2: casi
    todo el trabajo se hace al final de la carrera.
    """

    A_pole: float = 240e-6      # área polar TOTAL (suma de polos) [m^2]
    B_sat: float = 1.6          # saturación del circuito magnético [T]
    gap_start: float = 4.0e-3   # entrehierro inicial [m]
    gap_end: float = 0.3e-3     # entrehierro final (tope) [m]
    NI: float = 800.0           # amperivueltas disponibles [A]
    moving_mass: float = 6.0e-3

    def B(self, gap: float) -> float:
        return min(self.B_sat, MU0 * self.NI / (2.0 * gap))

    def force(self, gap: float) -> float:
        return self.B(gap) ** 2 * self.A_pole / (2.0 * MU0)

    def work(self, n: int = 2001) -> float:
        g = np.linspace(self.gap_start, self.gap_end, n)
        F = np.array([self.force(float(gi)) for gi in g])
        return float(np.trapezoid(F, self.gap_start - g))

    def summary(self) -> dict:
        return {
            "F_start_N": self.force(self.gap_start),
            "F_end_N": self.force(self.gap_end),
            "F_sat_N": self.B_sat ** 2 * self.A_pole / (2.0 * MU0),
            "W_mJ": self.work() * 1e3,
            "stroke_mm": (self.gap_start - self.gap_end) * 1e3,
            "a_max_ms2": self.force(self.gap_end) / self.moving_mass,
        }
