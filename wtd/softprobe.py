"""Palpador de acople blando: medir la cuña con 1 N de precarga.

EL PROBLEMA

`wtd.palpator` modela el palpador "obvio": una punta de acero apoyada
directamente sobre la cuña. Ese palpador es rígido (la rigidez de Hertz de
la punta, ~1.6e6 N/m a 1 N) y por lo tanto SIGUE a la cuña: mide su
aceleración. Y la aceleración de la cuña a 10-15 mm del golpe es de miles de
g, con lo cual

    a_despegue = F_precarga / m_palpador

manda al diseño a un callejón: con 1 N de precarga, seguir 5000 g pide una
masa móvil de 20 mg, que no existe una vez que se le suma el acelerómetro,
el vástago y el cable.

LA SALIDA: BAJAR LA FRECUENCIA DE ACOPLE, NO LA MASA

Si entre la punta y la masa móvil se pone un resorte BLANDO, el conjunto
deja de seguir a la cuña por encima de su resonancia y la masa se queda
quieta en el espacio. El resorte se comprime lo que se mueve la cuña, y el
acelerómetro montado sobre la masa lee

    a_leida = (k/m) * x_cuña = omega_n^2 * x_cuña          (regimen sismico)

O sea que el palpador deja de ser un ACELEROMETRO de la cuña y pasa a ser un
MEDIDOR DE DESPLAZAMIENTO de la cuña, con ganancia omega_n^2 elegible por
diseño. No es un filtro que recorta el pico: es un cambio de escala, y el
pico recortado es una consecuencia.

EL INVARIANTE QUE ORDENA TODO EL DISEÑO

El despegue ocurre cuando la fuerza de contacto se anula, o sea cuando la
compresion dinamica del resorte iguala la estatica:

    x_cuña > delta_0 = F_precarga / k

y en ese instante la aceleracion leida vale

    a_leida = omega_n^2 * delta_0 = (k/m) * (F/k) = F / m

IDENTICA a la del palpador rigido. La conclusion es fuerte y no depende del
resorte:

    EL FONDO DE ESCALA UTIL DE CUALQUIER PALPADOR APOYADO VALE F/m.

El limite es de un solo lado: acota la excursion que DESCARGA el contacto,
que es la que termina en despegue. En compresion la lectura no esta acotada,
porque ahi el contacto se cierra mas. Como la señal es oscilatoria las dos
semiondas son parecidas, asi que |a|_max ~ F/m sirve como fondo de escala
practico, pero conviene verificarlo en el tiempo y no darlo por sentado (en
los 126 casos simulados el pico llega a 109 g contra 150 g de despegue).

La rigidez NO cambia cuanta aceleracion se puede leer antes de despegar:
cambia QUE PARTE del movimiento de la cuña cae dentro de ese fondo de
escala. Con acople rigido, el fondo de escala F/m se gasta en los picos de
aceleracion de alta frecuencia, que no llevan la informacion. Con acople
blando se gasta en el desplazamiento, que si la lleva.

POR QUE EL DESPLAZAMIENTO Y NO LA ACELERACION

Barrido de los siete estados de ajuste a 5 mJ, palpador a 12.5 mm del golpe:

    estado            x_pico [um]     a_pico [g]
    S0 ajustada           0.30             848
    S2 50 %               0.40            1625
    S3 25 %               2.38            4855
    S4 residual           7.11            1549
    S6 floja 200 um       6.89            1069

El pico de aceleracion NO ES MONOTONO: sube hasta S3 y despues baja, de modo
que un mismo valor (~1500 g) corresponde a la cuña al 50 % y a la cuña
practicamente suelta. El pico de desplazamiento si es monotono y satura, con
un recorrido de 20 a 40x entre ajustada y floja. Medir desplazamiento no es
una concesion a la falta de precarga: es el mejor discriminante.

BONUS: EL RESORTE BLANDO LINEALIZA EL CONTACTO

El resorte queda en serie con la rigidez de Hertz de la punta. Con k ~ 1e5
N/m contra 1.6e6 N/m de Hertz, el blando se lleva el 94 % de la flexibilidad
y la no linealidad hertziana (F ~ d^1.5, y k_t ~ F^1/3) queda diluida a
~1.5 % sobre el total. El acople pasa a ser lineal y por lo tanto
CALIBRABLE, que es lo que hace falta para que la lectura signifique una
energia y no solo una alarma.

LIMITES DEL METODO

  * El palpador es ciego por debajo de su resonancia: ahi sigue a la cuña y
    no comprime el resorte. Es un pasa-altos de 2do orden sobre el
    desplazamiento. El primer modo de la cuña asentada esta en 6.1 kHz, muy
    por encima de los ~2 kHz de acople, asi que la señal pasa; pero la
    deriva de cuerpo rigido de la cuña suelta NO se mide.
  * El amortiguamiento del acople decide el rechazo de alta frecuencia:
    sin amortiguar cae como 1/r^2, muy amortiguado como 1/r. Conviene un
    resorte metalico (flexura) y NO un elastomero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .hertz import contact_stiffness
from .materials import G11_HERTZ, STEEL, Material

G = 9.80665


@dataclass
class SoftProbe:
    """Palpador de masa `mass` acoplado por un resorte blando `k_soft`."""

    mass: float = 0.68e-3        # masa movil: vastago + acelerometro [kg]
    k_soft: float = 9.5e4        # rigidez del acople blando [N/m]
    preload: float = 1.0         # precarga de apoyo [N]
    zeta: float = 0.08           # amortiguamiento del acople [-]
    tip_radius: float = 2.0e-3   # radio de la punta [m]
    tip_material: Material = STEEL

    # ---- rigideces -----------------------------------------------------
    def k_hertz(self) -> float:
        """Rigidez tangente del contacto punta/cuña en el punto de precarga."""
        kH = contact_stiffness(self.tip_radius, self.tip_material, G11_HERTZ)
        delta = (self.preload / kH) ** (2.0 / 3.0)
        return 1.5 * kH * math.sqrt(delta)

    def k_series(self) -> float:
        """Resorte blando en serie con el contacto de Hertz."""
        kh = self.k_hertz()
        return 1.0 / (1.0 / self.k_soft + 1.0 / kh)

    def hertz_share(self) -> float:
        """Fraccion de la flexibilidad total que aporta Hertz (no lineal)."""
        return (1.0 / self.k_hertz()) / (1.0 / self.k_series())

    # ---- magnitudes de diseño ------------------------------------------
    def f0(self) -> float:
        return math.sqrt(self.k_series() / self.mass) / (2.0 * math.pi)

    def gain(self) -> float:
        """Ganancia sismica omega_n^2 [ (m/s^2) por m de desplazamiento ]."""
        return self.k_series() / self.mass

    def a_liftoff(self) -> float:
        """Aceleracion leida en el instante de despegue [m/s^2]. Vale F/m."""
        return self.preload / self.mass

    def x_liftoff(self) -> float:
        """Desplazamiento de cuña que despega el palpador [m]. Vale F/k."""
        return self.preload / self.k_series()

    def static_deflection(self) -> float:
        """Compresion estatica del acople bajo la precarga [m]."""
        return self.x_liftoff()

    def transmissibility(self, f: np.ndarray) -> np.ndarray:
        """|X_masa / X_cuña| por excitacion de base."""
        r = np.asarray(f, dtype=float) / self.f0()
        num = 1.0 + (2.0 * self.zeta * r) ** 2
        den = (1.0 - r ** 2) ** 2 + (2.0 * self.zeta * r) ** 2
        return np.sqrt(num / den)

    def summary(self) -> dict:
        return {
            "m_g": self.mass * 1e3,
            "k_soft_N_mm": self.k_soft * 1e-3,
            "k_hertz_N_mm": self.k_hertz() * 1e-3,
            "k_series_N_mm": self.k_series() * 1e-3,
            "frac_hertz_pct": 100.0 * self.hertz_share(),
            "F_precarga_N": self.preload,
            "f0_Hz": self.f0(),
            "ganancia_g_por_um": self.gain() * 1e-6 / G,
            "a_despegue_g": self.a_liftoff() / G,
            "x_despegue_um": self.x_liftoff() * 1e6,
            "flecha_estatica_um": self.static_deflection() * 1e6,
        }


# --------------------------------------------------------------------------
# Sintesis: de la especificacion al resorte
# --------------------------------------------------------------------------

def design(preload: float = 1.0, a_liftoff_g: float = 150.0,
           x_wedge_max: float = 7.5e-6, a_full_scale_g: float = 100.0,
           **kw) -> SoftProbe:
    """Resuelve el palpador a partir de la especificacion del ensayo.

    La masa sale del despegue, que no depende del resorte:

        m = F / a_despegue

    y la rigidez sale de mapear el mayor desplazamiento esperado de la cuña
    al fondo de escala elegido del acelerometro:

        omega_n^2 = a_fondo_escala / x_cuña_max      ->   k = m omega_n^2

    El cociente a_despegue/a_fondo_escala es el margen contra el despegue, y
    conviene >= 1.5 porque el pico real supera al cuasi-estatico.
    """
    mass = preload / (a_liftoff_g * G)
    gain = (a_full_scale_g * G) / x_wedge_max
    k_needed = mass * gain
    # despejar el resorte blando que, EN SERIE con Hertz, da k_needed
    probe = SoftProbe(mass=mass, k_soft=k_needed, preload=preload, **kw)
    kh = probe.k_hertz()
    if k_needed >= kh:
        raise ValueError("la rigidez pedida supera la de Hertz: no hay "
                         "resorte blando posible, subir x_wedge_max o bajar "
                         "el fondo de escala")
    probe.k_soft = 1.0 / (1.0 / k_needed - 1.0 / kh)
    return probe


# --------------------------------------------------------------------------
# Respuesta temporal
# --------------------------------------------------------------------------

def apply_soft_probe(w_wedge: np.ndarray, dt: float, probe: SoftProbe) -> dict:
    """Pasa el desplazamiento de la cuña por la dinamica del palpador.

    Igual que `palpator.apply_palpator`, se excita con el DESPLAZAMIENTO y no
    con la aceleracion: doble integrar mete deriva y falsea el despegue.

        m x'' = -k (x - w) - c (x' - w')
        F_contacto = F_precarga - [ k (x - w) + c (x' - w') ]

    En vuelo (F_contacto <= 0) la unica fuerza es la precarga, que empuja al
    palpador de vuelta contra la cuña.
    """
    k = probe.k_series()
    w0 = 2.0 * math.pi * probe.f0()
    c = 2.0 * probe.zeta * probe.mass * w0

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
        F = probe.preload - rel
        if F <= 0.0:
            lift[i] = True
            Fc[i] = 0.0
            a = -probe.preload / probe.mass
        else:
            Fc[i] = F
            a = -rel / probe.mass
        a_out[i] = a
        v[i + 1] = v[i] + a * dt
        x[i + 1] = x[i] + v[i + 1] * dt
    a_out[-1] = a_out[-2]

    a_wedge = np.gradient(vw, dt)
    a_pk = float(np.abs(a_out).max())
    return {
        "a_palpador": a_out,
        "F_contacto": Fc,
        "despega": bool(lift.any()),
        "frac_despegado": float(lift.mean()),
        "a_pico_palpador_g": a_pk / G,
        "a_pico_cuña_g": float(np.abs(a_wedge).max()) / G,
        "x_pico_cuña_um": float(np.abs(ww).max()) * 1e6,
        # inversion: de la lectura al desplazamiento de la cuña
        "x_estimado_um": a_pk / probe.gain() * 1e6,
        "margen_despegue": probe.a_liftoff() / max(a_pk, 1e-12),
    }


# --------------------------------------------------------------------------
# Lectura: que numero sacarle a la señal del palpador
# --------------------------------------------------------------------------

def probe_features(a: np.ndarray, dt: float) -> dict:
    """Candidatos a lectura, a partir de la señal del acelerometro [m/s^2].

    QUE MIDE REALMENTE EL PALPADOR

    Se verifico por regresion contra 126 casos simulados: el pico leido NO
    es ni omega_n^2 x_cuña (regimen sismico puro, R2 = 0.92 pero 40 % de
    error mediano) ni omega_n v_cuña (regimen impulsivo, R2 = 0.84 y 26 %).
    El palpador queda en la TRANSICION, porque la cuña no lo excita con un
    impulso sino con una rafaga de ~2 ms a 6 kHz. La lectura es un valor de
    espectro de respuesta al choque a f0, y por lo tanto hay que CALIBRARLA:
    no se invierte a una magnitud fisica con una formula cerrada.

    Eso no es un problema para el ensayo, porque lo que se pide no es el
    desplazamiento de la cuña sino separar asentada de suelta. Y para eso la
    mejor lectura no es el pico sino la ENERGIA DE LA SEÑAL:

        estado        pico [g]   int a^2 [g^2 ms]     (E_golpe = 3 mJ)
        S0 ajustada      4.95          13.8
        S2 50 %          4.63           0.59
        S3 25 %         19.1           17.5
        S4 residual     63.6          670
        S6 floja        63.5         1270

        separacion ajustada|floja:   x13.7 con el pico,  x38 con la energia

    Integrar en vez de picar tiene ademas la ventaja practica de siempre:
    promedia el ruido en lugar de perseguir una sola muestra, y no depende
    de acertarle al instante del pico.
    """
    a = np.asarray(a, dtype=float)
    return {
        "pico_g": float(np.abs(a).max()) / G,
        # energia de la señal: la mejor separacion asentada/suelta
        "energia_g2ms": float(((a / G) ** 2).sum() * dt * 1e3),
        "abs_int_g_ms": float((np.abs(a) / G).sum() * dt * 1e3),
        "rms_g": float(np.sqrt(((a / G) ** 2).mean())),
    }


def noise_in_feature(density_g_rtHz: float, bandwidth: float,
                     window_s: float) -> dict:
    """Piso de ruido de las lecturas, para dimensionar el acelerometro.

    El ruido del acelerometro tambien se integra: sobre una ventana T, la
    energia de la señal acumula sigma^2 T. Con un ADXL1005 (75 ug/sqrt(Hz))
    limitado a 5 kHz son 5.3 mg rms, y sobre 3 ms dan 8.4e-5 g^2 ms, casi
    tres ordenes por debajo del caso mas desfavorable (la cuña ajustada a
    1 mJ, 0.108 g^2 ms). Hay margen de sobra.
    """
    sigma = density_g_rtHz * math.sqrt(bandwidth)
    return {"sigma_g_rms": sigma,
            "energia_g2ms": sigma ** 2 * window_s * 1e3,
            "abs_int_g_ms": sigma * window_s * 1e3}
