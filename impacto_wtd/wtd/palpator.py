"""El palpador: qué mide realmente un acelerómetro apoyado sobre la cuña.

Hasta acá la simulación reportaba la aceleración del NODO de la cuña, o sea
un sensor ideal sin masa y perfectamente acoplado. Un palpador real es una
masa apoyada contra la cuña con una precarga, y eso mete dos límites duros
que no son de ruido sino de física:

  1. RESONANCIA DE CONTACTO. El palpador y la rigidez hertziana de su punta
     forman un sistema de segundo orden. Por encima de esa frecuencia el
     palpador deja de seguir a la cuña. Con punta de acero de R = 2 mm
     precargada a 5 N, la rigidez de contacto vale ~2.8e6 N/m: con 0.5 g de
     masa la resonancia queda en 11.9 kHz y con 2 g, en 6.0 kHz. La cuña
     asentada tiene su primer modo en 6.1 kHz. O sea que un palpador de 2 g
     resuena JUSTO encima de la señal.

  2. DESPEGUE. El palpador sólo sigue a la cuña mientras la fuerza de
     contacto sea de compresión. La aceleración máxima que puede seguir es

         a_max = F_precarga / m_palpador

     Con 5 N y 0.5 g son 1020 g. Los picos simulados a 10 mm del golpe son
     de miles de g: el palpador salta.

Las dos cosas empujan en direcciones opuestas: subir la precarga sube el
límite de despegue y también la rigidez (bien), pero bajar la masa es lo
único que sube las dos a la vez. Y la masa mínima la fija el acelerómetro.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .hertz import contact_stiffness
from .materials import G11_HERTZ, STEEL, Material


@dataclass
class Palpator:
    """Vástago con acelerómetro, apoyado contra la cuña con precarga."""

    mass: float = 0.8e-3        # masa del vástago + acelerómetro [kg]
    tip_radius: float = 2.0e-3  # radio de la punta [m]
    preload: float = 5.0        # fuerza de apoyo [N]
    tip_material: Material = STEEL
    zeta: float = 0.05          # amortiguamiento del contacto

    def contact_stiffness(self) -> float:
        """Rigidez tangente del contacto de Hertz en el punto de precarga.

        F = k_H d^1.5  =>  dF/dd = 1.5 k_H d^0.5, con d = (F/k_H)^(2/3).
        """
        kH = contact_stiffness(self.tip_radius, self.tip_material, G11_HERTZ)
        delta = (self.preload / kH) ** (2.0 / 3.0)
        return 1.5 * kH * math.sqrt(delta)

    def f0(self) -> float:
        return math.sqrt(self.contact_stiffness() / self.mass) / (2 * math.pi)

    def a_liftoff(self) -> float:
        """Aceleración a la que el palpador se despega [m/s^2]."""
        return self.preload / self.mass

    def transmissibility(self, f: np.ndarray) -> np.ndarray:
        """|X_palpador / X_cuña| para excitación por la base."""
        r = np.asarray(f, dtype=float) / self.f0()
        num = 1.0 + (2.0 * self.zeta * r) ** 2
        den = (1.0 - r ** 2) ** 2 + (2.0 * self.zeta * r) ** 2
        return np.sqrt(num / den)

    def summary(self) -> dict:
        return {
            "m_g": self.mass * 1e3,
            "R_mm": self.tip_radius * 1e3,
            "F_precarga_N": self.preload,
            "k_contacto_N_m": self.contact_stiffness(),
            "f0_kHz": self.f0() / 1e3,
            "a_despegue_g": self.a_liftoff() / 9.80665,
            "delta_precarga_um": (self.preload
                                  / contact_stiffness(self.tip_radius,
                                                      self.tip_material,
                                                      G11_HERTZ)) ** (2 / 3) * 1e6,
        }


def apply_palpator(w_wedge: np.ndarray, dt: float, palp: Palpator) -> dict:
    """Pasa el movimiento de la cuña por la dinámica del palpador.

    Se excita con el DESPLAZAMIENTO de la cuña, no con su aceleración: doble
    integrar la aceleración simulada mete una deriva que hace que el
    palpador parezca despegarse siempre (se verificó: daba 97 % de despegue
    en todos los casos, incluidos los que no despegan).

        m x'' = -k (x - w) - c (x' - w')        (x medido desde el equilibrio)
        F_contacto = precarga - k (x - w) - c (x' - w')

    Despegue cuando F_contacto <= 0. En vuelo el palpador no tiene fuerza
    (aceleración nula) hasta que vuelve a tocar.
    """
    k = palp.contact_stiffness()
    w0 = 2 * math.pi * palp.f0()
    c = 2.0 * palp.zeta * palp.mass * w0

    n = len(w_wedge)
    ww = np.asarray(w_wedge, dtype=float)
    vw = np.gradient(ww, dt)

    x = np.zeros(n)
    v = np.zeros(n)
    a_out = np.zeros(n)
    Fc = np.zeros(n)
    lift = np.zeros(n, dtype=bool)
    x[0] = ww[0]
    v[0] = vw[0]
    for i in range(n - 1):
        rel = k * (x[i] - ww[i]) + c * (v[i] - vw[i])
        F = palp.preload - rel
        if F <= 0.0:
            lift[i] = True
            Fc[i] = 0.0
            a = -palp.preload / palp.mass   # sólo el resorte de precarga lo empuja
        else:
            Fc[i] = F
            a = -rel / palp.mass
        a_out[i] = a
        v[i + 1] = v[i] + a * dt
        x[i + 1] = x[i] + v[i + 1] * dt
    a_out[-1] = a_out[-2]

    a_wedge = np.gradient(vw, dt)
    return {
        "a_palpador": a_out,
        "F_contacto": Fc,
        "frac_despegado": float(lift.mean()),
        "despega": bool(lift.any()),
        "t_primer_despegue_us": (float(np.argmax(lift)) * dt * 1e6
                                 if lift.any() else float("nan")),
        "a_pico_cuña_g": float(np.abs(a_wedge).max() / 9.80665),
        "a_pico_palpador_g": float(np.abs(a_out).max() / 9.80665),
        "atenuacion": float(np.abs(a_out).max()
                            / max(np.abs(a_wedge).max(), 1e-12)),
    }


# --------------------------------------------------------------------------
# Ruido de acelerómetros reales
# --------------------------------------------------------------------------

ACELEROMETROS = [
    # nombre, rango [g], ancho de banda [Hz], densidad de ruido [g/sqrt(Hz)], masa [g]
    ("MEMS ADXL1005 (±100 g)", 100, 23e3, 75e-6, 0.03),
    ("MEMS ADXL1002 (±50 g)", 50, 11e3, 25e-6, 0.03),
    ("Piezo IEPE miniatura (±500 g)", 500, 20e3, 350e-6, 0.4),
    ("Piezo de choque (±10000 g)", 10000, 50e3, 5e-3, 1.5),
    ("Piezo de choque miniatura (±5000 g)", 5000, 40e3, 3e-3, 0.2),
]


def noise_floor(density: float, bandwidth: float) -> float:
    """Ruido de banda ancha [g rms]."""
    return density * math.sqrt(bandwidth)


def sensor_table(a_pk_g: float, f_max: float = 20e3) -> list[dict]:
    out = []
    for name, rng, bw, dens, m in ACELEROMETROS:
        bw_eff = min(bw, f_max)
        n = noise_floor(dens, bw_eff)
        out.append({
            "sensor": name, "rango_g": rng, "bw_kHz": bw / 1e3,
            "masa_g": m, "ruido_g_rms": n,
            "SNR_dB": 20 * math.log10(a_pk_g / n) if n > 0 else float("inf"),
            "satura": a_pk_g > rng,
            "bw_suficiente": bw >= f_max,
        })
    return out
