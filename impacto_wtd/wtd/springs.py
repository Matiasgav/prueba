"""Acumuladores elásticos: el elemento que resuelve el problema de energía.

RAZÓN DE SER (el argumento central del diseño):

El actuador directo tiene que entregar TODA la energía del golpe durante los
pocos milisegundos de la carrera. Eso convierte un problema de energía
(fácil: 1 W x 0.5 s = 500 mJ por ciclo) en un problema de POTENCIA PICO
(difícil: 150 mJ en 3 ms = 50 W mecánicos).

Un acumulador elástico desacopla las dos cosas: se carga lento con potencia
media baja y se descarga rápido. El límite deja de ser el actuador y pasa a
ser (a) la energía específica del resorte y (b) el umbral de daño del G11.

Se implementan tres topologías con verificación de fatiga:
  * `HelicalSpring`  — resorte helicoidal de compresión (familia A, cañón).
  * `LeafSpring`     — resorte de ballesta empotrado-empotrado (familia B).
  * `TorsionBar`     — barra de torsión (familia B, la de mayor densidad).

Energía específica teórica (material trabajando a tensión admisible):
    torsión pura (helicoidal, barra):  u = tau^2 / (4 G)
    flexión, sección rectangular:      u = sigma^2 / (18 E)   (viga prismática)
                                       u = sigma^2 / (6 E)    (viga de igual
                                                               resistencia)
La torsión gana por ~3x a igualdad de volumen, y por eso la barra de torsión
es la opción correcta cuando el envolvente es plano.

Fatiga: método de Goodman con los datos de Zimmerli (Shigley, Mechanical
Engineering Design, cap. 10), que es el estándar para resortes helicoidales
y el único con datos experimentales de tensión admisible independientes del
tamaño del alambre.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Datos de Zimmerli para alambre de resorte (Shigley tabla 10-4).
# Componente alterna y media admisibles en corte, INDEPENDIENTES del diámetro.
ZIMMERLI_UNPEENED = (241e6, 379e6)   # (Ssa, Ssm) [Pa]
ZIMMERLI_PEENED = (398e6, 534e6)     # (Ssa, Ssm) [Pa] granallado

STEEL_G = 79.3e9      # módulo de corte del alambre de resorte [Pa]
STEEL_E = 200e9
STEEL_RHO = 7850.0


def wire_tensile_strength(d: float, A: float = 2211e6, m: float = 0.145
                          ) -> float:
    """Sut del alambre por la ley de Sines: Sut = A / d^m, d en mm.

    A y m por defecto: alambre musical ASTM A228 (Shigley tabla 10-4).
    """
    return A / (d * 1e3) ** m


@dataclass
class FatigueCheck:
    tau_a: float
    tau_m: float
    Sse: float
    Ssu: float
    n_goodman: float
    infinite_life: bool

    def as_dict(self) -> dict:
        return {"tau_a_MPa": self.tau_a / 1e6, "tau_m_MPa": self.tau_m / 1e6,
                "Sse_MPa": self.Sse / 1e6, "Ssu_MPa": self.Ssu / 1e6,
                "n_goodman": self.n_goodman,
                "vida_infinita": self.infinite_life}


def goodman_shear(tau_a: float, tau_m: float, Sut: float,
                  peened: bool = True) -> FatigueCheck:
    Ssa, Ssm = ZIMMERLI_PEENED if peened else ZIMMERLI_UNPEENED
    Ssu = 0.67 * Sut
    Sse = Ssa / (1.0 - (Ssm / Ssu) ** 2)
    if tau_a <= 0:
        n = float("inf")
    else:
        n = 1.0 / (tau_a / Sse + tau_m / Ssu)
    return FatigueCheck(tau_a, tau_m, Sse, Ssu, n, n >= 1.0)


# --------------------------------------------------------------------------

@dataclass
class HelicalSpring:
    """Resorte helicoidal de compresión."""

    d: float          # diámetro de alambre [m]
    D: float          # diámetro medio de espira [m]
    n_a: float        # espiras activas
    G: float = STEEL_G
    rho: float = STEEL_RHO
    peened: bool = True
    ends_squared_ground: bool = True

    @property
    def C(self) -> float:
        return self.D / self.d

    @property
    def k(self) -> float:
        return self.G * self.d ** 4 / (8.0 * self.D ** 3 * self.n_a)

    @property
    def n_total(self) -> float:
        return self.n_a + (2.0 if self.ends_squared_ground else 0.0)

    @property
    def solid_length(self) -> float:
        return self.n_total * self.d

    @property
    def wire_volume(self) -> float:
        return (math.pi * self.d ** 2 / 4.0) * (math.pi * self.D
                                                * self.n_total)

    @property
    def mass(self) -> float:
        return self.rho * self.wire_volume

    @property
    def outer_diameter(self) -> float:
        return self.D + self.d

    def K_B(self) -> float:
        """Factor de Bergsträsser (corrección por curvatura + cortante)."""
        C = self.C
        return (4.0 * C + 2.0) / (4.0 * C - 3.0)

    def shear_stress(self, F: float) -> float:
        return self.K_B() * 8.0 * F * self.D / (math.pi * self.d ** 3)

    def energy(self, x_max: float, x_min: float = 0.0) -> float:
        """Trabajo entregado al pasar de x_max a x_min de deflexión [J]."""
        return 0.5 * self.k * (x_max ** 2 - x_min ** 2)

    def surge_frequency(self) -> float:
        """Primer modo de surge [Hz] (Shigley ec. 10-25, ambos extremos
        apoyados en placas planas):  f = (1/2) sqrt(k/m).

        Si el tiempo de lanzamiento no es bastante mayor que 1/f_surge, parte
        de la energía queda atrapada en ondas dentro del resorte y no llega
        al proyectil. Ver `wtd.surge`, que lo cuantifica con un modelo
        distribuido: para el resorte de referencia la pérdida es del 3 %.
        """
        return 0.5 * math.sqrt(self.k / self.mass)

    def fatigue(self, F_max: float, F_min: float = 0.0) -> FatigueCheck:
        F_a = (F_max - F_min) / 2.0
        F_m = (F_max + F_min) / 2.0
        return goodman_shear(self.shear_stress(F_a), self.shear_stress(F_m),
                             wire_tensile_strength(self.d), self.peened)

    def summary(self, x_max: float, x_min: float = 0.0) -> dict:
        F_max = self.k * x_max
        fat = self.fatigue(F_max, self.k * x_min)
        return {
            "d_mm": self.d * 1e3, "D_mm": self.D * 1e3, "n_a": self.n_a,
            "C": self.C, "k_N_m": self.k, "OD_mm": self.outer_diameter * 1e3,
            "L_solid_mm": self.solid_length * 1e3,
            "L_min_needed_mm": (self.solid_length + x_max) * 1e3,
            "F_max_N": F_max,
            "tau_max_MPa": self.shear_stress(F_max) / 1e6,
            "E_mJ": self.energy(x_max, x_min) * 1e3,
            "mass_g": self.mass * 1e3,
            "m_eff_g": self.mass / 3.0 * 1e3,
            "f_surge_Hz": self.surge_frequency(),
            **fat.as_dict(),
        }


@dataclass
class LeafSpring:
    """Ballesta prismática empotrada-empotrada con carga central."""

    L: float          # luz entre empotramientos [m]
    b: float          # ancho [m]
    t: float          # espesor [m]
    E: float = STEEL_E
    rho: float = STEEL_RHO
    sigma_allow: float = 700e6   # admisible a fatiga (pulsante, granallado)

    @property
    def I(self) -> float:
        return self.b * self.t ** 3 / 12.0

    @property
    def k(self) -> float:
        return 192.0 * self.E * self.I / self.L ** 3

    @property
    def mass(self) -> float:
        return self.rho * self.b * self.t * self.L

    @property
    def m_eff(self) -> float:
        """Masa modal en el punto central (primer modo empotrado-empotrado)."""
        return 0.39648 * self.mass

    def stress(self, delta: float) -> float:
        """Tensión máxima de flexión (en los empotramientos) [Pa]."""
        F = self.k * delta
        M = F * self.L / 8.0
        return M * (self.t / 2.0) / self.I

    def max_deflection(self) -> float:
        F = self.sigma_allow * self.I / ((self.t / 2.0) * (self.L / 8.0))
        return F / self.k

    def energy(self, delta: float) -> float:
        return 0.5 * self.k * delta ** 2

    def summary(self, delta: float) -> dict:
        return {
            "L_mm": self.L * 1e3, "b_mm": self.b * 1e3, "t_mm": self.t * 1e3,
            "k_N_m": self.k, "F_N": self.k * delta,
            "delta_mm": delta * 1e3,
            "delta_max_mm": self.max_deflection() * 1e3,
            "sigma_MPa": self.stress(delta) / 1e6,
            "sigma_allow_MPa": self.sigma_allow / 1e6,
            "E_mJ": self.energy(delta) * 1e3,
            "mass_g": self.mass * 1e3, "m_eff_g": self.m_eff * 1e3,
            "ok_fatiga": self.stress(delta) <= self.sigma_allow,
            "u_espec_J_kg": self.energy(delta) / self.mass,
        }


@dataclass
class TorsionBar:
    """Barra de torsión maciza."""

    d: float          # diámetro [m]
    L: float          # longitud activa [m]
    G: float = STEEL_G
    rho: float = STEEL_RHO
    tau_allow: float = 600e6   # admisible a fatiga pulsante [Pa]

    @property
    def Jp(self) -> float:
        return math.pi * self.d ** 4 / 32.0

    @property
    def k_t(self) -> float:
        """Rigidez torsional [N·m/rad]."""
        return self.G * self.Jp / self.L

    @property
    def volume(self) -> float:
        return math.pi * self.d ** 2 / 4.0 * self.L

    @property
    def mass(self) -> float:
        return self.rho * self.volume

    def torque_max(self) -> float:
        return self.tau_allow * self.Jp / (self.d / 2.0)

    def angle_max(self) -> float:
        return self.torque_max() / self.k_t

    def energy_max(self) -> float:
        return 0.5 * self.k_t * self.angle_max() ** 2

    def summary(self) -> dict:
        return {
            "d_mm": self.d * 1e3, "L_mm": self.L * 1e3,
            "k_t_Nm_rad": self.k_t,
            "T_max_Nm": self.torque_max(),
            "phi_max_deg": math.degrees(self.angle_max()),
            "E_max_mJ": self.energy_max() * 1e3,
            "mass_g": self.mass * 1e3,
            "u_espec_J_kg": self.energy_max() / self.mass,
            "u_espec_teor_J_m3": self.tau_allow ** 2 / (4.0 * self.G),
        }


def specific_energy_comparison(tau: float = 600e6, sigma: float = 700e6,
                               G: float = STEEL_G, E: float = STEEL_E) -> dict:
    """Densidad de energía teórica por topología [J/m^3]."""
    return {
        "torsion_pura_J_m3": tau ** 2 / (4.0 * G),
        "flexion_prismatica_J_m3": sigma ** 2 / (18.0 * E),
        "flexion_igual_resistencia_J_m3": sigma ** 2 / (6.0 * E),
        "traccion_pura_J_m3": sigma ** 2 / (2.0 * E),
        "nota": ("La torsión gana en volumen; la tracción pura gana en "
                 "teoría pero no es realizable con una geometría que quepa "
                 "y se pueda cargar y descargar."),
    }
