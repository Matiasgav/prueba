"""Velocidad de la maza a partir de la tension y la corriente del voice coil.

LA PREGUNTA

El ensayo necesita la energia del golpe tiro a tiro: E = 1/2 m v^2 a la
entrada, y el rebote v_r a la salida. Hoy eso lo da un sensor inductivo
dedicado. La pregunta es si midiendo u(t) e i(t) del propio actuador se puede
sacar lo mismo sin ese sensor.

LO PRIMERO: ¿ESTA ACOPLADA LA BOBINA CUANDO PEGA?

Depende de la arquitectura, y las dos del proyecto se comportan al reves:

  * LANZADOR DE RESORTE (`wtd.launcher`): el proyectil SE SEPARA del empujador
    en x_release y llega a la cuña en vuelo libre. La bobina no esta acoplada
    en el impacto, asi que el back-EMF da la velocidad DE SEPARACION y nada
    mas: no ve el impacto ni el rebote. Para el ensayo no alcanza.

  * PALANCA EN L CON VOICE COIL (`wtd.lever`, la configuracion recomendada):
    no hay separacion. La maza va en la palanca y la palanca en el actuador,
    asi que la bobina esta acoplada durante todo el impacto y el rebote.
    Ademas el acoplamiento es fuerte: el 49 % de la masa equivalente ES el
    actuador. Aca el metodo tiene sentido.

Todo lo que sigue es para la palanca. Relacion cinematica:

    v_bobina / v_maza = r_eff / r_h = 5.297 / 6.381 = 0.830

o sea que la bobina se mueve un 17 % mas lento que la maza, no un factor
grande: el back-EMF ve casi toda la señal.

MAGNITUDES

    K_F = K_actuator * sqrt(R) = 0.84 * sqrt(5.1) = 1.897 N/A  (= V s/m)
    R   = 5.1 ohm       L = 220 uH       tau_e = 43.1 us

Con la maza a 1.48 m/s la bobina va a 1.23 m/s y el back-EMF vale 2.33 V. En
el impacto la velocidad se invierte (restitucion ~0.79), asi que el EMF salta
4.18 V en unos 60 us. Es una señal grande y facil de medir; el problema no es
la amplitud.

EL PROBLEMA ES tau_e, Y TIENE UNA SALIDA LIMPIA

La constante electrica del actuador (43 us) es del mismo orden que la
duracion del contacto (~60 us). Con el drive conectado hay que resolver

    u = R i + L di/dt + K_F v      ->      v = (u - R i - L di/dt) / K_F

y el termino L di/dt, que es el que hay que restar justo durante el evento,
sale de DERIVAR la corriente medida: amplifica ruido exactamente donde mas
molesta.

La salida es no medir con el drive conectado. Si se ABRE el circuito unos
cientos de microsegundos antes del impacto, i = 0 y los dos terminos molestos
desaparecen de una:

    u_circuito_abierto = K_F(x) * v_bobina

La maza ya es balistica en ese tramo, asi que apagar el drive no cuesta nada
de energia de golpe. Queda una medicion directa de velocidad, sin R, sin
L di/dt y sin derivar nada.

LO QUE QUEDA COMO ERROR

En circuito abierto el unico error de fondo es K_F(x): la ficha del LAH04 da
1.89 N/A en el centro y 1.31 N/A a +-2 mm, o sea **-31 % sobre la carrera**.
Hay que calibrar K_F(x) y saber en que x esta la maza al pegar. Como x sale
de integrar la propia velocidad, es resoluble, pero es una calibracion mas,
no un dato de ficha.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .actuator import (LAH04, LAH04_CURVE_F, LAH04_CURVE_X,
                       force_constant_from_datasheet)

# Cinematica de la palanca recomendada (wtd.lever, D_ball = 8 mm, carrera 3 mm)
LEVER_RATIO = 0.8301        # v_bobina / v_maza
M_EQ_HAMMER_KG = 4.910e-3   # masa equivalente referida a la maza
M_HAMMER_KG = 2.104e-3


@dataclass
class CoilSpec:
    """Parametros electricos y de acoplamiento del voice coil."""

    R: float = LAH04["R_ohm"]              # [ohm]
    L: float = LAH04["L_H"]                # [H]
    K_F0: float = force_constant_from_datasheet()   # [N/A] en el centro
    ratio: float = LEVER_RATIO             # v_bobina / v_maza

    def tau_e(self) -> float:
        return self.L / self.R

    def K_F(self, x: float | np.ndarray) -> float | np.ndarray:
        """Constante de fuerza en funcion de la posicion [N/A].

        Interpola la curva digitizada de ficha. Fuera de la carrera se
        satura al extremo, que es conservador.
        """
        return np.interp(x, LAH04_CURVE_X, LAH04_CURVE_F) * (
            self.K_F0 / LAH04_CURVE_F.max())

    def emf(self, v_hammer: float, x: float = 0.0) -> float:
        """Back-EMF de circuito abierto para una velocidad de maza [V]."""
        return float(self.K_F(x)) * self.ratio * v_hammer

    def summary(self) -> dict:
        return {
            "R_ohm": self.R, "L_uH": self.L * 1e6,
            "tau_e_us": self.tau_e() * 1e6,
            "K_F_centro_N_A": self.K_F0,
            "K_F_extremo_N_A": float(self.K_F(2.0e-3)),
            "variacion_K_F_pct": 100.0 * (float(self.K_F(2.0e-3)) / self.K_F0 - 1.0),
            "ratio_bobina_maza": self.ratio,
        }


# --------------------------------------------------------------------------
# Los dos modos de medicion
# --------------------------------------------------------------------------

def velocity_from_uv(u: np.ndarray, i: np.ndarray, dt: float,
                     coil: CoilSpec, x: float = 0.0,
                     R_assumed: float | None = None) -> np.ndarray:
    """Modo A — drive conectado. v = (u - R i - L di/dt) / (K_F * ratio).

    Hay que derivar la corriente, y ese es el termino caro.
    """
    R = coil.R if R_assumed is None else R_assumed
    didt = np.gradient(np.asarray(i, dtype=float), dt)
    return (np.asarray(u, dtype=float) - R * np.asarray(i) - coil.L * didt) / (
        float(coil.K_F(x)) * coil.ratio)


def velocity_from_open_circuit(u: np.ndarray, coil: CoilSpec,
                               x: float = 0.0) -> np.ndarray:
    """Modo B — drive abierto. v = u / (K_F * ratio). Sin R, sin di/dt."""
    return np.asarray(u, dtype=float) / (float(coil.K_F(x)) * coil.ratio)


# --------------------------------------------------------------------------
# Presupuesto de error
# --------------------------------------------------------------------------

def error_budget(coil: CoilSpec, v_hammer: float = 1.48,
                 i_drive: float = 1.0,
                 sigma_u_mV: float = 2.0, sigma_i_mA: float = 5.0,
                 fs: float = 1e6, t_win: float = 20e-6,
                 dR_pct: float = 5.0, dKF_pct: float = 2.0) -> dict:
    """Error de velocidad de cada fuente, en los dos modos.

    `dR_pct` es la deriva de R sin compensar: el cobre sube 0.393 %/C, asi
    que 5 % son ~13 C de deriva. `dKF_pct` es el error residual tras
    calibrar la curva K_F(x).
    """
    K = float(coil.K_F(0.0)) * coil.ratio          # [V s/m]
    N = max(int(fs * t_win), 2)

    # --- fuentes comunes a los dos modos ---
    e_u = sigma_u_mV * 1e-3 / K                     # ruido de tension
    e_KF = dKF_pct / 100.0 * v_hammer               # calibracion de K_F

    # --- fuentes que SOLO existen con el drive conectado ---
    e_R = (dR_pct / 100.0) * coil.R * i_drive / K   # deriva de R
    # derivada de i por minimos cuadrados sobre la ventana
    sigma_didt = (sigma_i_mA * 1e-3) / t_win * math.sqrt(12.0 * (N - 1)
                                                         / (N * (N + 1)))
    e_didt = coil.L * sigma_didt / K

    modoA = math.sqrt(e_u ** 2 + e_KF ** 2 + e_R ** 2 + e_didt ** 2)
    modoB = math.sqrt(e_u ** 2 + e_KF ** 2)
    return {
        "K_V_s_m": K,
        "e_ruido_tension_ms": e_u,
        "e_calibracion_KF_ms": e_KF,
        "e_deriva_R_ms": e_R,
        "e_derivada_i_ms": e_didt,
        "modo_A_ms": modoA, "modo_A_pct": 100 * modoA / v_hammer,
        "modo_B_ms": modoB, "modo_B_pct": 100 * modoB / v_hammer,
        # la energia va como v^2: dE/E = 2 dv/v
        "modo_A_energia_pct": 200 * modoA / v_hammer,
        "modo_B_energia_pct": 200 * modoB / v_hammer,
    }


def compare_with_inductive(coil: CoilSpec, **kw) -> dict:
    """Contra el sensor inductivo del proyecto (0.27 % de error en energia).

    Referencia: `wtd.sensing.velocity_estimator_error` con sigma_x = 1 um,
    200 kS/s y ventana de 200 us.
    """
    from .sensing import energy_error_from_velocity, velocity_estimator_error
    ind = velocity_estimator_error(1e-6, 200e3, 200e-6)
    e_ind = 100 * energy_error_from_velocity(ind["sigma_v_ms"], 2.0)
    b = error_budget(coil, **kw)
    return {
        "inductivo_energia_pct": e_ind,
        "backemf_modo_A_energia_pct": b["modo_A_energia_pct"],
        "backemf_modo_B_energia_pct": b["modo_B_energia_pct"],
        "penalizacion_A": b["modo_A_energia_pct"] / e_ind,
        "penalizacion_B": b["modo_B_energia_pct"] / e_ind,
    }
