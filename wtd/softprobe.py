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

Si entre la punta y la masa movil se pone un resorte BLANDO, el conjunto se
vuelve un PASA-BAJOS de segundo orden con corte en su resonancia f0. Como la
cuña asentada responde a ~33 kHz y la suelta a 50-225 Hz (ver mas abajo), un
corte plantado en el medio rechaza a una y deja pasar a la otra. Eso, y no
otra cosa, es lo que separa los estados.

(Una version anterior de este modulo explicaba el mecanismo como un cambio
de regimen -- el palpador pasando de acelerometro a sismometro para medir
desplazamiento. Esa lectura es correcta como descripcion de la respuesta
forzada, pero NO es lo que produce la discriminacion, y llevaba a creer que
la eleccion de f0 era critica. Lo que discrimina es el filtrado.)

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

POR QUE NO SIRVE LA ACELERACION DE LA CUÑA

Barrido de los siete estados de ajuste a 5 mJ, palpador a 12.5 mm del golpe:

    estado            x_pico [um]     a_pico [g]
    S0 ajustada           0.30             848
    S2 50 %               0.40            1625
    S3 25 %               2.38            4855
    S4 residual           7.11            1549
    S6 floja 200 um       6.89            1069

El pico de aceleracion NO ES MONOTONO: sube hasta S3 y despues baja, de modo
que un mismo valor (~1500 g) corresponde a la cuña al 50 % y a la cuña
practicamente suelta. El pico esta dominado por el transitorio rapido del
impacto, que no sigue al estado. El de desplazamiento si es monotono, porque
sigue a la excursion lenta, que es la que cambia con el ajuste.

BONUS: EL RESORTE BLANDO LINEALIZA EL CONTACTO

El resorte queda en serie con la rigidez de Hertz de la punta. Con k ~ 1e5
N/m contra 1.6e6 N/m de Hertz, el blando se lleva el 94 % de la flexibilidad
y la no linealidad hertziana (F ~ d^1.5, y k_t ~ F^1/3) queda diluida a
~1.5 % sobre el total. El acople pasa a ser lineal y por lo tanto
CALIBRABLE, que es lo que hace falta para que la lectura signifique una
energia y no solo una alarma.

DONDE ESTA REALMENTE LA SEÑAL  (corregido, sep 2026)

Una version anterior de este modulo decia que el primer modo de la cuña
asentada esta en 6.1 kHz y construia el argumento sobre eso. ESTA MAL: los
6094 Hz salen del modelo de apoyo en EXTREMOS ('ends'), que la rev. B
reemplazo por apoyo DISTRIBUIDO tras el dato de campo del usuario. Con el
modelo vigente, medido sobre el espectro de la simulacion no lineal a
12.5 mm y 5 mJ:

    estado          pico   90 % de la energia   por debajo de f0
                                                  del palpador
    S0 ajustada   33 350 Hz   33 325 - 33 375 Hz        0.0 %
    S3 25 %       33 075 Hz   13 375 - 34 625 Hz         1.5 %
    S6 floja          50 Hz       50 -    225 Hz       100.0 %

(Espectro del DESPLAZAMIENTO, que es lo que excita al palpador; el de la
aceleracion pesa las altas por omega^4 y da otra cosa. Resolucion 25 Hz,
ventana de 40 ms: una version anterior de esta tabla decia "125 Hz" para la
cuña floja, que era literalmente el primer bin de una ventana de 8 ms.)

El resultado es mas fuerte de lo que parecia: la cuña asentada pone el 0 % de
su energia por debajo del corte del palpador y la suelta pone el 100 %. No es
que el filtro "atenue bastante" a una y "deje pasar bastante" a la otra: las
separa enteras.

El modelo linealizado lo confirma: con el hombro CERRADO los cuatro primeros
modos estan en 32.9 / 33.4 / 33.6 / 40.0 kHz (la cuña acoplada al nucleo en
toda su longitud es altisimamente impedante); con el hombro ABIERTO, solo
sobre el ripple, quedan 1.28 / 1.29 kHz (los dos modos de cuerpo rigido
montados en el resorte) y recien despues 10.6 y 24.9 kHz de flexion.

O SEA QUE LA FRECUENCIA SUBE CON EL APRIETE, y muchisimo: entre los picos de
asentada y suelta hay un factor ~670 (33.4 kHz contra 50 Hz). Esa separacion es el verdadero fundamento del
metodo, y es mucho mas robusta de lo que suponia el argumento viejo:

  * la cuña ASENTADA pone toda su energia a 33 kHz, muy por encima de la
    resonancia del palpador, que la rechaza como 1/r^2 (~1/400);
  * la cuña SUELTA hace una excursion lenta y grande (50-225 Hz, ~7 um) que
    para el palpador es practicamente un escalon: lo excita y lo deja
    sonando a SU propia frecuencia.

El palpador es entonces un PASA-BAJOS DISCRIMINANTE, que es exactamente la
intuicion original del usuario. Su f0 se planta en el hueco enorme que hay
entre los dos estados. Con el amortiguamiento real de una flexura el optimo
queda en ~1.3 kHz y vale x150; la banda util (>x100) va de ~700 Hz a
~1.7 kHz (ver `design_space`).

LIMITES DEL METODO

  * El palpador es ciego por debajo de su resonancia: ahi sigue a la cuña y
    no comprime el resorte. Importa menos de lo que parece, porque la
    DERIVA de cuerpo rigido resulto despreciable en este modelo: tras el
    golpe la cuña vuelve a su posicion (la posicion media al final vale
    0.00-0.01 um contra picos de 0.3-6.9 um, o sea <0.2 %). El ripple la
    reasienta. Queda como caveat para un efecto real que este modelo no
    reproduce: una cuña que migre axialmente tiro a tiro.
  * EL AMORTIGUAMIENTO DEL ACOPLE ES EL PARAMETRO MAS SENSIBLE DEL DISEÑO,
    y por lejos. Entre zeta = 0.005 (flexura de acero) y zeta = 0.15
    (elastomero blando) la separacion pasa de x150 a x3, sin que cambie
    ningun otro numero; en zeta = 0.30 el palpador ademas despega. Ver
    ZETA_SWEEP. FLEXURA METALICA, NUNCA ELASTOMERO, y hay que MEDIR el zeta
    del palpador construido: es el primer numero a verificar en banco.
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

    mass: float = 0.68e-3        # masa movil: carro + acelerometro [kg]
    k_soft: float = 9.5e4        # rigidez del acople blando [N/m]
    preload: float = 1.0         # precarga de apoyo [N]
    tip_mass: float = 0.0        # masa del lado PUNTA del resorte [kg]
    #  La punta va del lado de la cuña, o sea que la cuña la arrastra
    #  cinematicamente a miles de g. Ver `apply_soft_probe`: no cambia la
    #  lectura, pero fija un limite duro  m_punta <= F / a_cuña_max.
    zeta: float = 0.005          # amortiguamiento del acople [-]
    #  0.005 = flexura de acero, que es lo que hay que construir.
    #  La rev. C usaba 0.08 y por eso reportaba separaciones 10x peores.
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

# LAS DOS FLEXURAS HACEN TRABAJOS DISTINTOS Y NO COMPITEN
#
# La de MEDICION va en SERIE, en el camino de carga cuña -> punta -> carro.
# Es la que filtra, y su rigidez NO se elige: sale de k = m * omega_0^2, con m
# fijada por el despegue (F/m) y omega_0 por donde tiene que caer el corte.
# Cero grados de libertad.
#
# La de PRECARGA va en PARALELO, colgando del carro contra el cuerpo. No divide
# el movimiento: solo SUMA rigidez. Por eso pueden diferir 85x sin estorbarse.
#
#   contacto de Hertz punta/cuña   1636 N/mm    2.6 % de la flexibilidad en serie
#   flexura de MEDICION              43.5 N/mm  97.4 %
#   flexura de PRECARGA               0.5 N/mm  en paralelo, +1.1 % sobre k
#
# CUANTO IMPORTA LA RIGIDEZ DE PRECARGA: MUCHO MENOS DE LO QUE PARECE.
# Barrido con todo lo demas fijo (m = 0.68 g, 1 N, zeta = 0.005):
#
#     k_p [N/mm]   f0 [Hz]   separacion   recorrido   tolerancia +-20 %
#        0.1        1274       x150        10.0 mm        +-2.00 mm
#        0.5        1280       x148         2.0 mm        +-0.40 mm   <- elegida
#        2.0        1302       x143         0.5 mm        +-0.10 mm
#        5.0        1344       x140         0.2 mm        +-0.04 mm
#       20.0        1538       x121        0.05 mm        +-0.01 mm
#
# Subir k_p 200 veces cuesta solo un 20 % de separacion. Lo que se desploma es
# la TOLERANCIA DE POSICIONAMIENTO del crawler, que cae de +-2 mm a +-0.01 mm.
#
# O sea que el factor 85 NO sale de mantener limpia la medicion, como decia una
# version anterior de esta nota: sale de cuanto puede errarle el brazo al
# estacionar. La regla de diseño correcta es elegir k_p por la tolerancia que
# hace falta y despues verificar que no sea una fraccion grande de 43.5 N/mm.
PRELOAD_SWEEP = [   # k_p [N/mm], f0 [Hz], separacion, tolerancia +-20 % [mm]
    (0.1, 1274, 149.8, 2.00), (0.2, 1276, 149.3, 1.00), (0.5, 1280, 148.1, 0.40),
    (1.0, 1287, 146.1, 0.20), (2.0, 1302, 143.0, 0.10), (5.0, 1344, 140.3, 0.04),
    (10.0, 1412, 135.9, 0.02), (20.0, 1538, 120.6, 0.01),
]

# EL AMORTIGUAMIENTO DEL ACOPLE ES EL PARAMETRO MAS SENSIBLE DE TODO EL DISEÑO.
# Barrido con m = 0.68 g, f0 = 1273 Hz, 1 N (studies/soft_probe.py):
#
#     zeta     a_max [g]   separacion   ring-down al 1 %
#     0.002       78.5        x155          288 ms
#     0.005       78.4        x150          115 ms   <- flexura metalica
#     0.010       78.4        x140           58 ms
#     0.020       78.8        x112           29 ms
#     0.050       86.6         x40           12 ms
#     0.080       99.6         x14            7 ms   <- lo que suponia la rev. C
#     0.150      135.6          x3            4 ms   <- elastomero blando
#     0.300      215.7        x0.7            2 ms   y ADEMAS DESPEGA
#
# O sea que "flexura metalica y NO elastomero" no es una recomendacion de
# segundo orden: es LA decision de construccion. Entre zeta = 0.005 y 0.15 el
# ensayo pasa de excelente a inservible, sin que cambie ningun otro numero.
#
# La rev. C reporto todo con zeta = 0.08, que era una suposicion pesimista:
# los numeros reales de una flexura de acero son ~10x mejores.
ZETA_SWEEP = [
    (0.002, 78.5, 154.9), (0.005, 78.4, 150.2), (0.010, 78.4, 139.9),
    (0.020, 78.8, 112.2), (0.050, 86.6, 39.5), (0.080, 99.6, 14.1),
    (0.150, 135.6, 2.9), (0.300, 215.7, 0.7),
]

# Barrido de f0 con la cuña simulada a 12.5 mm y 2/5/12 mJ. a_max y la
# separacion NO dependen de la masa: son funcion de f0 (y de zeta) sola. La
# masa solo fija el techo de despegue F/m. Por eso el diseño se hace en dos
# pasos independientes: f0 elige la CALIDAD, m elige si SOBREVIVIS.
#   f0 [Hz], a_max leida [g], separacion asentada|suelta
F0_SWEEP_FLEXURA = [          # zeta = 0.005, flexura metalica: el caso real
    (600, 17.9, 91.3), (800, 31.7, 119.1), (1000, 49.0, 139.1),
    (1273, 78.4, 150.2), (1600, 137.5, 113.6), (2000, 235.4, 80.3),
    (2500, 368.2, 48.9), (3200, 581.2, 26.0), (4000, 869.3, 13.7),
]
F0_SWEEP = [                  # zeta = 0.08, conservador (el de la rev. C)
    (400, 20.3, 1.5), (600, 34.0, 3.2), (800, 50.3, 6.0),
    (1000, 69.2, 9.9), (1273, 99.6, 14.1), (1600, 142.7, 16.0),
    (2000, 204.7, 16.9), (2500, 295.2, 16.8), (3200, 460.0, 15.6),
    (4000, 694.7, 13.9), (5000, 1039.1, 12.7), (6500, 1633.9, 10.8),
]


def design_space(preload: float = 1.0, margin: float = 1.4,
                 zeta: float = 0.005) -> list[dict]:
    """De que depende realmente el numero de despegue.

    LOS 150 g NO SON UNA ELECCION LIBRE, SON UNA CONSECUENCIA.

    Subir f0 sube la lectura rapido (a_max ~ f0^1.7), y una lectura mas alta
    pide una masa mas chica para no despegar. La cadena es:

        f0 deseado -> a_max(f0) -> m <= F / (margen * a_max) -> a_despegue = F/m

    o sea que el numero de despegue sale de que tan liviano se puede CONSTRUIR
    el palpador, no de una preferencia. Con flexura metalica (zeta = 0.005):

        a_despegue   masa     f0      separacion    (margen 1,4)
            25 g     4,06 g    600 Hz      x91
            44 g     2,30 g    800 Hz     x119
            69 g     1,49 g   1000 Hz     x139
           110 g     0,93 g   1273 Hz     x150     <- OPTIMO
           192 g     0,53 g   1600 Hz     x114
           330 g     0,31 g   2000 Hz      x80

    CON EL AMORTIGUAMIENTO REAL EL OPTIMO SE CORRE A ~1.3 kHz, justo donde ya
    estaba el diseño. Con el zeta pesimista de la rev. C (0.08) el optimo
    parecia estar en 2 kHz y valer solo x17; con flexura vale x150 y esta en
    1273 Hz. El diseño no cambia de numeros: mejora 10x y queda confirmado.

    El diseño propuesto toma esa fila y redondea la masa a 0,68 g, lo que
    sube el margen a 1,91 y el despegue a 150 g. Los 150 g del enunciado caen
    solos: son F/m de la masa mas chica que se puede construir.

    Y el otro camino, SUBIR LA PRECARGA, ahora rinde todavia menos: a 1273 Hz
    ya estamos en el optimo, asi que el segundo newton no compra separacion,
    solo margen contra el despegue. No hace falta.
    """
    table = F0_SWEEP_FLEXURA if zeta <= 0.02 else F0_SWEEP
    out = []
    for f0, a_max, sep in table:
        m = preload / (margin * a_max * G)
        out.append({"f0_Hz": f0, "a_max_leida_g": a_max, "separacion": sep,
                    "m_max_g": m * 1e3, "a_despegue_g": preload / m / G,
                    "k_N_mm": m * (2 * math.pi * f0) ** 2 * 1e-3})
    return out


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
        F_contacto = F_precarga - [ k (x - w) + c (x' - w') ] + m_punta * w''

    En vuelo (F_contacto <= 0) la unica fuerza es la precarga, que empuja al
    palpador de vuelta contra la cuña.

    DONDE VA EL RESORTE (y por que importa)

    El resorte esta EN EL CAMINO DE CARGA, entre la cuña y la masa:

        cuña ── punta ──[ resorte k ]── masa ──[ precarga F ]── cuerpo

    NO entre la masa y el cuerpo con un vastago rigido hasta la punta. Con
    vastago rigido la masa sigue a la cuña sin filtrar nada y el acelerometro
    lee los miles de g de la cuña: es el palpador RIGIDO otra vez, con pasos
    de mas. La compliancia tiene que estar entre lo que toca y lo que mide.

    CONSECUENCIA: LA PUNTA TIENE QUE SER LIVIANA

    Del lado de la cuña, la punta es arrastrada CINEMATICAMENTE por ella. Para
    seguirla hace falta m_punta * a_cuña, y esa fuerza sale del contacto, que
    no puede dar mas que la precarga. De ahi el tercer termino de F_contacto
    y el limite:

        m_punta <= F_precarga / a_cuña_max = 1 N / 4800 g = 21 mg

    Verificado con este modelo: la masa de punta NO cambia la lectura (mientras
    haya contacto la ecuacion de la masa es identica), solo adelanta el
    despegue. A 5 mJ el umbral simulado cae entre 30 y 50 mg y a 12 mJ entre
    20 y 30 mg, algo mas permisivo que la cota porque el pico de aceleracion
    y el de fuerza del resorte no coinciden en el tiempo.
    """
    k = probe.k_series()
    w0 = 2.0 * math.pi * probe.f0()
    c = 2.0 * probe.zeta * probe.mass * w0

    n = len(w_wedge)
    ww = np.asarray(w_wedge, dtype=float)
    vw = np.gradient(ww, dt)
    aw = np.gradient(vw, dt)

    x = np.zeros(n)
    v = np.zeros(n)
    a_out = np.zeros(n)
    Fc = np.zeros(n)
    lift = np.zeros(n, dtype=bool)
    x[0] = ww[0]
    v[0] = vw[0]
    for i in range(n - 1):
        rel = k * (x[i] - ww[i]) + c * (v[i] - vw[i])
        # la punta va del lado de la cuña: seguirla cuesta m_punta * a_cuña,
        # y esa fuerza la tiene que dar el contacto
        F = probe.preload - rel + probe.tip_mass * aw[i]
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

    a_pk = float(np.abs(a_out).max())
    a_wedge = aw
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
        # masa maxima admisible del lado punta para este caso
        "m_punta_max_mg": probe.preload / max(float(np.abs(aw).max()), 1e-12) * 1e6,
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
    El palpador no queda en ninguno de los dos asintotas porque la cuña no
    lo excita con un impulso limpio: la asentada le manda una portadora de
    33 kHz (que el rechaza) y la suelta, una excursion lenta de 125 Hz que
    para el es casi un escalon. En los dos casos el palpador termina
    sonando a SU propia frecuencia, asi que la lectura es un valor de
    espectro de respuesta al choque a f0, y por lo tanto hay que
    CALIBRARLA: no se invierte a una magnitud fisica con formula cerrada.

    Eso no es un problema para el ensayo, porque lo que se pide no es el
    desplazamiento de la cuña sino separar asentada de suelta. Y para eso la
    mejor lectura no es el pico sino la ENERGIA DE LA SEÑAL:

        estado        pico [g]   int a^2 [g^2 ms]     (E_golpe = 3 mJ)
        S0 ajustada      3.48          7.36
        S2 50 %          3.16          0.263
        S3 25 %         14.5           8.52
        S4 residual     40.3         188
        S6 floja        39.8         535

        separacion ajustada|floja:   x11.4 con el pico,  x25.5 con la energia

    Sobre las seis energias de golpe ensayadas la separacion va de x14 a x36
    con la energia de la señal y de x1.6 a x11.8 con el pico.

    Integrar en vez de picar tiene ademas la ventaja practica de siempre:
    promedia el ruido en lugar de perseguir una sola muestra, y no depende
    de acertarle al instante del pico.

    LA ENERGIA DEL GOLPE TIENE OPTIMO, Y NO ES EL MINIMO

    Las dos lecturas no piden lo mismo:

      * el PICO se degrada monotonamente al subir la energia (x11.8 a 2 mJ,
        x1.6 a 12 mJ): ahi conviene pegar lo mas flojo que permita el ruido;
      * la ENERGIA DE LA SEÑAL tiene un maximo ancho en 3-5 mJ (x25 a x36) y
        cae a x23 en 1 mJ y a x14 en 12 mJ.

    El limite de arriba es el conocido (con el golpe fuerte hasta la cuña
    ajustada despega del hombro y todos los estados se parecen). El de abajo
    es distinto: a 1 mJ la cuña ajustada S0 devuelve mas señal que S1 y S2,
    la escalera deja de ordenar en el extremo apretado y es S0 el que limita
    la separacion del grupo.

    Si en cambio lo que se quiere es resolver FINO la frontera S3|S4 (25 %
    contra 5 % de precarga), ahi si conviene lo mas flojo posible: el salto
    S3->S4 vale x459 a 1 mJ y x7.2 a 12 mJ.
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
