"""El eslabón que faltaba: la máquina que CARGA el acumulador.

Crítica válida del usuario: el estudio dimensionó cuánta energía puede
almacenar un resorte o una barra de torsión dentro de 10 x 10 x 60 mm, pero
no dimensionó el mecanismo de amartillado. Y en un envolvente así, el
cargador es el problema difícil: cargar 190 mJ contra 80 N de fuerza en el
cigüeñal no lo hace cualquier cosa que entre en 10 mm de altura.

Se evalúan tres formas de convertir un actuador chico en un golpe grande,
todas compatibles con el LAH04 que ya está en el proyecto (1.89 N pico,
4 mm de carrera, 10.1 mm de diámetro):

  1. `direct_charge`     — el actuador carga el acumulador de un tirón.
                           Es lo que el estudio suponía sin decirlo.
  2. `ratchet_charge`    — el actuador bombea el acumulador con un trinquete
                           a lo largo de N ciclos. Multiplica la energía
                           por N sin multiplicar la fuerza.
  3. `resonant_charge`   — el actuador excita un resonador en resonancia y
                           la amplitud crece sola. Multiplica por Q en vez
                           de por N, sin trinquete y sin traba.

La tercera es la más interesante porque no tiene ninguna pieza que se
desgaste bajo carga: la separación ocurre en el paso por cero del resorte,
donde la fuerza de contacto vale cero por construcción.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Actuator:
    """Actuador lineal disponible para cargar."""

    name: str
    F_peak: float          # fuerza pico [N]
    stroke: float          # carrera [m]
    R_ohm: float
    K_F: float             # constante de fuerza [N/A]
    moving_mass: float     # [kg]
    diameter: float        # [m]
    length: float          # [m]
    P_cont: float          # potencia continua admisible [W]

    @property
    def work_per_stroke(self) -> float:
        """Trabajo mecánico de una carrera completa a fuerza pico [J]."""
        return self.F_peak * self.stroke

    def force_at(self, I: float) -> float:
        return self.K_F * I

    def fits(self, w: float, h: float, l: float) -> bool:
        return self.diameter <= min(w, h) and self.length <= l


LAH04 = Actuator(name="Sensata LAH04-10-000A", F_peak=1.89, stroke=4.0e-3,
                 R_ohm=5.1, K_F=1.897, moving_mass=3.49e-3,
                 diameter=10.1e-3, length=25.4e-3, P_cont=1.75)


# --------------------------------------------------------------------------
# 1) carga directa
# --------------------------------------------------------------------------

def direct_charge(E_target: float, act: Actuator, I: float = 1.0,
                  reduction: float = 1.0) -> dict:
    """El actuador carga el acumulador en una sola carrera.

    Con una reducción `reduction` = (carrera del actuador)/(carrera del
    acumulador) la fuerza se multiplica por `reduction` y la carrera se
    divide. El trabajo disponible NO cambia: sigue siendo F * carrera.
    Por eso la carga directa está limitada por el trabajo del actuador y no
    hay palanca que lo arregle.
    """
    W = act.force_at(I) * act.stroke
    return {
        "metodo": "carga directa",
        "W_actuador_mJ": W * 1e3,
        "E_objetivo_mJ": E_target * 1e3,
        "alcanza": W >= E_target,
        "deficit_x": E_target / W if W > 0 else float("inf"),
        "F_necesaria_N": E_target / act.stroke * reduction,
        "nota": ("una reducción cambia fuerza por carrera pero no crea "
                 "trabajo: si W_actuador < E_objetivo, no hay relación de "
                 "transmisión que lo resuelva"),
    }


# --------------------------------------------------------------------------
# 2) carga por trinquete
# --------------------------------------------------------------------------

def ratchet_charge(E_target: float, act: Actuator, I: float = 1.0,
                   eff: float = 0.75, rate_hz: float = 60.0) -> dict:
    """El actuador bombea el acumulador a lo largo de N ciclos.

    Cada carrera del actuador mete W_util = eff * F * s en el acumulador y
    el trinquete impide que se devuelva. Después de N ciclos hay N * W_util.

    Multiplica ENERGÍA por N sin multiplicar FUERZA, que es exactamente lo
    que hace falta: el problema del envolvente no es la energía, es que la
    fuerza de cocción del acumulador (decenas de newton) no la da un
    actuador de 1.9 N.

    Precio: el trinquete es una pieza que desliza bajo carga N veces por
    tiro. Con N = 35 y 10^7 tiros son 3.5 x 10^8 ciclos de diente: hay que
    diseñarlo como un escape de reloj, no como un trinquete de llave.
    """
    W_util = eff * act.force_at(I) * act.stroke
    N = math.ceil(E_target / W_util)
    t_charge = N / rate_hz
    P_mech = E_target / t_charge
    # potencia eléctrica: I^2 R durante todo el ciclo de carga
    P_elec = I ** 2 * act.R_ohm
    return {
        "metodo": "trinquete",
        "W_util_por_ciclo_mJ": W_util * 1e3,
        "N_ciclos": N,
        "rate_hz": rate_hz,
        "t_carga_s": t_charge,
        "P_mecanica_W": P_mech,
        "P_electrica_W": P_elec,
        "duty_termico": P_elec / act.P_cont,
        "ok_termico": P_elec <= act.P_cont,
        "ciclos_de_diente_por_vida": N * 1e7,
        "F_max_actuador_N": act.force_at(I),
    }


# --------------------------------------------------------------------------
# 3) carga resonante
# --------------------------------------------------------------------------

def resonant_charge(E_target: float, act: Actuator, m_res: float,
                    x_max: float, Q: float = 50.0, I: float = 1.0) -> dict:
    """El actuador excita un resonador en su frecuencia natural.

    En régimen permanente la amplitud vale x = F Q / k, así que la energía
    almacenada es E = 1/2 k x^2 con x limitada por la carrera disponible.
    Fijando E y x queda determinada la rigidez, y con ella la frecuencia:

        k = 2 E / x^2
        f = sqrt(k/m) / 2pi
        F_necesaria = k x / Q

    El factor Q hace el trabajo que en el trinquete hace N, pero sin ninguna
    pieza que deslice bajo carga. Y la liberación es gratis: el proyectil
    apoyado contra el resonador se separa solo en el paso por cero, que es
    donde el resorte no ejerce fuerza y la velocidad es máxima.

    Tiempo de establecimiento: tau = 2Q/omega, y se llega al 98 % en 4 tau.
    """
    k = 2.0 * E_target / x_max ** 2
    omega = math.sqrt(k / m_res)
    f = omega / (2.0 * math.pi)
    F_req = k * x_max / Q
    v_max = omega * x_max
    tau = 2.0 * Q / omega
    P_mech = E_target / (4.0 * tau)
    P_elec = (F_req / act.K_F) ** 2 * act.R_ohm
    return {
        "metodo": "resonante",
        "k_N_m": k,
        "f_Hz": f,
        "x_max_mm": x_max * 1e3,
        "v_max_ms": v_max,
        "F_necesaria_N": F_req,
        "F_disponible_N": act.force_at(I),
        "alcanza": F_req <= act.force_at(I),
        "margen_fuerza": act.force_at(I) / F_req if F_req > 0 else
                         float("inf"),
        "Q": Q,
        "tau_ms": tau * 1e3,
        "t_98pct_ms": 4.0 * tau * 1e3,
        "P_mecanica_W": P_mech,
        "P_electrica_W": P_elec,
        "ok_termico": P_elec <= act.P_cont,
        "ciclos_por_tiro": 4.0 * tau * f,
    }


def resonant_split(E_res: float, m_res: float, m_proj: float) -> dict:
    """Reparto de energía cuando el resonador suelta al proyectil.

    Los dos viajan juntos hasta el paso por cero; ahí el resonador empieza a
    frenar y el proyectil sigue. La energía se reparte por masas, que es el
    teorema del tren de transmisión con i = 1.
    """
    frac = m_proj / (m_proj + m_res)
    return {"m_res_g": m_res * 1e3, "m_proj_g": m_proj * 1e3,
            "frac_al_proyectil": frac, "E_proyectil_mJ": E_res * frac * 1e3,
            "E_perdida_mJ": E_res * (1 - frac) * 1e3}


def resonant_impact_split(m_res: float, m_proj: float) -> float:
    """Si el resonador GOLPEA al proyectil en vez de empujarlo.

    Transferencia de un choque elástico: eta = 4 m1 m2 / (m1+m2)^2, máxima
    e igual a 1 con masas iguales. Deja el resonador atado a su flexura
    (nada vuela) a costa de un contacto más.
    """
    return 4.0 * m_res * m_proj / (m_res + m_proj) ** 2


# --------------------------------------------------------------------------
# Lo que cada acumulador le exige a su cargador
# --------------------------------------------------------------------------

def charger_demand(E: float, F_cock: float, stroke_cock: float,
                   t_available: float = 0.5) -> dict:
    """Qué tiene que dar el cargador para un acumulador dado."""
    P = E / t_available
    return {
        "E_mJ": E * 1e3,
        "F_cocción_N": F_cock,
        "carrera_cocción_mm": stroke_cock * 1e3,
        "P_media_W": P,
        "t_disponible_s": t_available,
        "veces_la_fuerza_del_LAH04": F_cock / LAH04.F_peak,
        "veces_el_trabajo_del_LAH04": E / LAH04.work_per_stroke,
    }
