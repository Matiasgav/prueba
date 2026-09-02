"""Cadena de sensado: sensor inductivo de posición, acelerómetro, micrófono.

El sensor inductivo es la pieza que cierra el sistema: midiendo la posición
del proyectil en el tramo libre se obtiene

    v_i  antes del impacto   ->  energía entregada  E = 1/2 m v_i^2
    v_r  después del impacto ->  energía devuelta   y el índice Leeb
    E_absorbida = 1/2 m (v_i^2 - v_r^2)

Eso convierte la repetibilidad del lanzador de REQUISITO en MEDICIÓN: ya no
hace falta que el golpe sea idéntico tiro a tiro, alcanza con conocerlo. Es
la diferencia de fondo con la patente de Westinghouse, que compensa la
gravedad con la tensión del resorte según la hora del carro porque no tiene
forma de medir la velocidad.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# --------------------------------------------------------------------------
# Estimación de velocidad a partir de posición muestreada
# --------------------------------------------------------------------------

def velocity_estimator_error(sigma_x: float, fs: float, t_window: float
                             ) -> dict:
    """Error de la velocidad estimada por regresión lineal de la posición.

    Para N muestras equiespaciadas en una ventana T con ruido blanco de
    desviación sigma_x, el ajuste por mínimos cuadrados de la pendiente tiene

        sigma_v = sigma_x / T * sqrt(12 (N-1) / (N (N+1)))  ->  ~ sigma_x/T * sqrt(12/N)

    Es el resultado que dimensiona el sensor: lo que importa NO es la
    resolución de una muestra sino resolución / (ventana * sqrt(N)).
    """
    N = max(int(fs * t_window), 2)
    sigma_v = sigma_x / t_window * math.sqrt(12.0 * (N - 1) / (N * (N + 1)))
    return {"N_muestras": N, "sigma_v_ms": sigma_v,
            "sigma_x_um": sigma_x * 1e6, "fs_kHz": fs / 1e3,
            "t_window_us": t_window * 1e6}


def energy_error_from_velocity(sigma_v: float, v: float) -> float:
    """E = 1/2 m v^2  =>  dE/E = 2 dv/v."""
    return 2.0 * sigma_v / v


@dataclass
class InductiveSensor:
    """Sensor inductivo por corrientes de Foucault (eddy current).

    Se especifica con blanco NO magnético (anillo de aluminio o cobre sobre
    el proyectil). Razón, cuantificada en `wtd.launcher.magnet_wall_force`:
    un imán permanente como blanco genera contra cualquier pieza
    ferromagnética cercana fuerzas del orden del newton, entre 10 y 100 veces
    el peso del proyectil, y destruye el vuelo libre. El sensado por
    corrientes de Foucault, en cambio, ejerce del orden de 1e-8 N.
    """

    f_carrier: float = 5e6        # frecuencia de excitación [Hz]
    L_coil: float = 10e-6         # inductancia [H]
    I_coil: float = 5e-3          # corriente de excitación [A]
    range_m: float = 6e-3         # rango de medición [m]
    resolution_m: float = 0.5e-6  # resolución rms [m]
    fs: float = 500e3             # frecuencia de muestreo [Hz]
    bandwidth: float = 100e3      # ancho de banda del demodulador [Hz]

    def force_on_target(self) -> float:
        return 0.5 * self.I_coil ** 2 * (self.L_coil / 2e-3)

    def evaluate(self, v: float, gap: float, m_proj: float) -> dict:
        t_flight = gap / v
        # se usa la mitad del vuelo para cada estimación (ida y vuelta)
        t_win = 0.5 * t_flight
        est = velocity_estimator_error(self.resolution_m, self.fs, t_win)
        dE = energy_error_from_velocity(est["sigma_v_ms"], v)
        F = self.force_on_target()
        W = m_proj * 9.80665
        return {
            **est,
            "t_flight_us": t_flight * 1e6,
            "sigma_v_rel": est["sigma_v_ms"] / v,
            "sigma_E_rel": dE,
            "F_sensor_N": F,
            "F_sensor_rel_peso": F / W,
            "muestras_por_vuelo": self.fs * t_flight,
            "suficiente": dE < 0.01,
        }


def daq_spec(f_max_signal: float, t_c: float, tau_ringdown: float,
             dynamic_range_db: float = 72.0) -> dict:
    """Especificación de la cadena de adquisición.

    Criterios:
      * f_s >= 10 f_max para reconstruir bien la forma del pulso (no 2.5:
        con 2.5 el pico del pulso de contacto se subestima hasta un 20 %).
      * antialias analógico a f_s/2.5 con al menos 4 polos.
      * ventana de registro >= 5 tau para capturar el decaimiento.
      * el pulso de contacto necesita >= 20 muestras para medir su duración.
    """
    fs_min_signal = 10.0 * f_max_signal
    fs_min_pulse = 20.0 / t_c
    fs = max(fs_min_signal, fs_min_pulse)
    bits = math.ceil((dynamic_range_db - 1.76) / 6.02)
    return {
        "f_max_signal_kHz": f_max_signal / 1e3,
        "t_c_us": t_c * 1e6,
        "fs_min_por_espectro_kHz": fs_min_signal / 1e3,
        "fs_min_por_pulso_kHz": fs_min_pulse / 1e3,
        "fs_recomendada_kHz": fs / 1e3,
        "f_antialias_kHz": fs / 2.5 / 1e3,
        "polos_antialias": 4,
        "bits_min": bits,
        "bits_recomendados": bits + 2,
        "ventana_registro_ms": 5.0 * tau_ringdown * 1e3,
        "muestras_por_registro": fs * 5.0 * tau_ringdown,
        "muestras_en_contacto": fs * t_c,
    }


def accelerometer_spec(a_pk_g: float, f_max: float,
                       margin_db: float = 6.0) -> dict:
    """Rango y ancho de banda del acelerómetro."""
    rng = a_pk_g * 10 ** (margin_db / 20.0)
    return {
        "a_pk_esperada_g": a_pk_g,
        "rango_minimo_g": rng,
        "rango_comercial_g": _next_standard_range(rng),
        "f_max_kHz": f_max / 1e3,
        "f_resonancia_min_kHz": 3.0 * f_max / 1e3,
        "montaje": ("resonancia de montaje >= 3 f_max: pegado con cianoacrilato "
                    "o roscado; el montaje con cera o imán no llega"),
    }


def _next_standard_range(g: float) -> int:
    for r in (50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000):
        if r >= g:
            return r
    return 100000


def mounting_resonance(m_sensor: float, k_mount: float) -> float:
    """Frecuencia de resonancia de montaje del acelerómetro [Hz]."""
    return math.sqrt(k_mount / m_sensor) / (2.0 * math.pi)


def palpator_transfer(m_palp: float, k_contact: float, f: np.ndarray
                      ) -> np.ndarray:
    """Transferencia de un palpador apoyado sobre la cuña.

    El palpador (vástago que toca la cuña y lleva el acelerómetro) es un
    sistema masa-resorte: por encima de su resonancia deja de seguir a la
    cuña. Es la limitación real del acelerómetro montado sobre la cuña, y la
    razón por la que el brief §8 punto 13 dice que está mal rankeado.
    """
    f0 = math.sqrt(k_contact / m_palp) / (2.0 * math.pi)
    r = f / f0
    return 1.0 / np.sqrt((1.0 - r ** 2) ** 2 + (2 * 0.05 * r) ** 2)


def microphone_spec(f1: float, distance: float = 20e-3) -> dict:
    """Nota de dimensionado del micrófono.

    La cuña radia como un pistón chico frente a la longitud de onda: a
    6 kHz, lambda = 57 mm, y una cuña de 50 x 30 mm es acústicamente compacta
    -> radia como monopolo, con eficiencia baja pero espectro fiel. Ventaja
    frente al acelerómetro: no toca la cuña, así que no le agrega masa ni
    depende de la rigidez de montaje. Desventaja: el ruido del crawler y el
    campo reverberante del bore.
    """
    c = 343.0
    lam = c / f1
    return {"f1_kHz": f1 / 1e3, "lambda_mm": lam * 1e3,
            "compacto": lam > 2 * 50e-3,
            "ka": 2 * math.pi * distance / lam,
            "campo": "cercano" if distance < lam / (2 * math.pi) else "lejano",
            "recomendacion": ("MEMS de banda ancha (>= 20 kHz) montado en el "
                              "crawler a 15-25 mm, con pantalla contra el "
                              "ruido de los motores")}
