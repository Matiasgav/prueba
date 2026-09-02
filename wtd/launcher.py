"""Dinámica del lanzamiento, la separación y el vuelo libre del proyectil.

El requisito del usuario es explícito: la aceleración ocurre con la punta
DENTRO del volumen del módulo, y el tramo de 2 a 4 mm fuera del volumen
tiene que ser lo más parecido posible a un movimiento libre.

Este módulo:
  1. Integra la fase acelerada (resorte + fricción + gravedad + aire).
  2. Determina el instante de SEPARACIÓN (contacto unilateral: el empujador
     deja de empujar cuando la fuerza de contacto se anularía).
  3. Cuantifica TODAS las fuerzas que sobreviven en el vuelo libre y las
     compara contra el peso del proyectil, que es la referencia natural.
  4. Dimensiona la ventilación del cañón, que es la fuerza parásita más
     grande y la más fácil de pasar por alto (el brief ya avisa en §7.1 que
     con 0.25 mm de huelgo el bombeo llega al 22 % del peso de la bola).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp

from .materials import G

RHO_AIR = 1.204        # [kg/m^3] a 20 C, 1 atm
MU_AIR = 1.82e-5       # viscosidad dinámica [Pa s]


# --------------------------------------------------------------------------
# Fase acelerada
# --------------------------------------------------------------------------

@dataclass
class LaunchSpec:
    """Definición del lanzador de resorte."""

    m_proj: float            # masa del proyectil [kg]
    k_spring: float          # rigidez del acumulador reducida al proyectil [N/m]
    x_cock: float            # deflexión inicial del acumulador [m]
    x_release: float = 0.0   # deflexión a la que el empujador deja de empujar
    m_spring_eff: float = 0.0   # masa efectiva del acumulador [kg]
    preload_force: float = 0.0  # fuerza a deflexión x_release [N]
    mu_guide: float = 0.10   # coeficiente de fricción de la guía
    normal_load: float = 0.0  # carga normal en la guía (por gravedad, etc) [N]
    clock_deg: float = 0.0   # posición horaria del crawler (0 = 12 en punto)
    bore_area: float = 0.0   # área del pistón [m^2]; 0 = sin efecto de aire
    vent_area: float = 1e-4  # área de venteo [m^2]
    vent_Cd: float = 0.6
    barrel_clearance: float = 0.0   # huelgo radial [m]; 0 = no viscoso
    barrel_engaged_len: float = 10e-3

    @property
    def stroke(self) -> float:
        return self.x_cock - self.x_release

    @property
    def g_along_flight(self) -> float:
        """Componente de gravedad a lo largo de la dirección del golpe.

        La dirección del golpe es radialmente HACIA AFUERA (del crawler hacia
        la cuña). A las 12 en punto eso apunta hacia arriba => la gravedad se
        opone. A las 6 en punto apunta hacia abajo => la gravedad ayuda.
        """
        return -G * math.cos(math.radians(self.clock_deg))

    @property
    def E_stored(self) -> float:
        return (0.5 * self.k_spring * (self.x_cock ** 2 - self.x_release ** 2)
                + self.preload_force * self.stroke)


def air_back_force(spec: LaunchSpec, v: float) -> float:
    """Fuerza de contrapresión del aire barrido por el proyectil [N].

    Suma de dos mecanismos, se toma el mayor:
      * inercial: descarga por orificio,  dp = rho (A_p v/(Cd A_v))^2 / 2
      * viscoso : flujo anular de Poiseuille, dp ∝ 1/h^3  (el que explota
        cuando el huelgo es chico; es el que arruina el ensayo de caída
        libre con tubo guía ajustado del brief §7.1)
    """
    if spec.bore_area <= 0.0 or v <= 0.0:
        return 0.0
    Q = spec.bore_area * v
    dp_inertial = (RHO_AIR / 2.0) * (Q / (spec.vent_Cd * spec.vent_area)) ** 2
    dp_visc = 0.0
    if spec.barrel_clearance > 0.0:
        # Flujo entre placas paralelas de ancho = perímetro, huelgo h.
        r = math.sqrt(spec.bore_area / math.pi)
        w = 2.0 * math.pi * r
        h = spec.barrel_clearance
        dp_visc = 12.0 * MU_AIR * spec.barrel_engaged_len * Q / (w * h ** 3)
    return max(dp_inertial, dp_visc) * spec.bore_area


def simulate_launch(spec: LaunchSpec, t_max: float = 0.05,
                    n_out: int = 2000) -> dict:
    """Integra la fase acelerada hasta la separación.

    Estado: [x, v] con x = deflexión remanente del acumulador (decrece).
    La separación ocurre cuando x llega a x_release.
    """
    m = spec.m_proj + spec.m_spring_eff

    def rhs(t, y):
        x, v = y
        F_spring = spec.k_spring * (x - spec.x_release) + spec.preload_force
        F_fric = -spec.mu_guide * spec.normal_load * np.sign(v) if v != 0 else 0.0
        F_air = -air_back_force(spec, v)
        F_grav = spec.m_proj * spec.g_along_flight
        a = (F_spring + F_fric + F_air + F_grav) / m
        return [-v, a]

    def event_release(t, y):
        return y[0] - spec.x_release
    event_release.terminal = True
    event_release.direction = -1

    sol = solve_ivp(rhs, (0.0, t_max), [spec.x_cock, 0.0],
                    events=event_release, max_step=1e-5, rtol=1e-9,
                    atol=1e-12, dense_output=True)
    if not sol.t_events[0].size:
        raise RuntimeError("el proyectil no completó la carrera: "
                           "verificar precarga vs fricción/gravedad")
    t_sep = float(sol.t_events[0][0])
    v_sep = float(sol.y_events[0][0][1])
    ts = np.linspace(0.0, t_sep, n_out)
    ys = sol.sol(ts)
    E_kin_total = 0.5 * m * v_sep ** 2
    E_proj = 0.5 * spec.m_proj * v_sep ** 2
    return {
        "t_sep_s": t_sep,
        "t_sep_ms": t_sep * 1e3,
        "v_sep_ms": v_sep,
        "E_stored_mJ": spec.E_stored * 1e3,
        "E_kin_total_mJ": E_kin_total * 1e3,
        "E_proj_mJ": E_proj * 1e3,
        "eff_stored_to_proj": E_proj / spec.E_stored if spec.E_stored else 0.0,
        "frac_to_spring": (spec.m_spring_eff / m) if m else 0.0,
        "a_mean_ms2": v_sep / t_sep,
        "a_max_ms2": (spec.k_spring * spec.stroke + spec.preload_force)
                     / m,
        "t": ts, "x": ys[0], "v": ys[1],
    }


# --------------------------------------------------------------------------
# Vuelo libre
# --------------------------------------------------------------------------

@dataclass
class FreeFlightForces:
    """Inventario de fuerzas parásitas durante el tramo libre.

    Todas en newtons, referidas al peso del proyectil para dar escala.
    """

    weight: float
    gravity_component: float
    residual_magnetic: float = 0.0
    sensor_eddy_drag: float = 0.0
    aero_drag: float = 0.0
    tether: float = 0.0

    def total_parasitic(self) -> float:
        """Todo lo que NO es gravedad (la gravedad es inevitable y conocida)."""
        return (abs(self.residual_magnetic) + abs(self.sensor_eddy_drag)
                + abs(self.aero_drag) + abs(self.tether))

    def as_dict(self) -> dict:
        w = self.weight
        return {
            "peso_N": w,
            "gravedad_N": self.gravity_component,
            "gravedad_%peso": 100.0 * self.gravity_component / w,
            "magnetica_residual_N": self.residual_magnetic,
            "magnetica_%peso": 100.0 * self.residual_magnetic / w,
            "eddy_sensor_N": self.sensor_eddy_drag,
            "eddy_%peso": 100.0 * self.sensor_eddy_drag / w,
            "aero_N": self.aero_drag,
            "aero_%peso": 100.0 * self.aero_drag / w,
            "parasitas_total_N": self.total_parasitic(),
            "parasitas_%peso": 100.0 * self.total_parasitic() / w,
        }


def aero_drag_force(v: float, d: float, Cd: float = 0.9) -> float:
    A = math.pi * d ** 2 / 4.0
    return 0.5 * RHO_AIR * Cd * A * v ** 2


def sensor_eddy_force(L_coil: float, I_coil: float,
                      dLdx: float | None = None,
                      x_scale: float = 2e-3) -> float:
    """Fuerza de un sensor inductivo sobre su blanco.

    F = (1/2) I^2 dL/dx.  Con dL/dx ~ L/x_escala.
    Para un LDC de MHz con corriente de excitación de miliamperes la fuerza
    resulta del orden de 1e-8 N: siete órdenes de magnitud por debajo del
    peso del proyectil. El sensado inductivo NO perturba el vuelo libre.
    """
    if dLdx is None:
        dLdx = L_coil / x_scale
    return 0.5 * I_coil ** 2 * dLdx


def magnet_wall_force(B_r: float, A_mag: float, gap: float,
                      t_mag: float) -> float:
    """Atracción de un imán permanente del proyectil hacia una pared de acero.

    Modelo de imagen especular con circuito magnético abierto:
        B_gap ≈ B_r * t_mag / (t_mag + 2*gap)      (desmagnetización 1D)
        F     = B_gap^2 * A / (2 mu0)

    Es una ESTIMACIÓN de primer orden [E], pero alcanza para la conclusión
    de diseño: si el proyectil lleva un imán permanente como blanco del
    sensor, la fuerza contra cualquier pieza ferromagnética cercana es del
    orden del NEWTON, es decir 10 a 100 veces el peso del proyectil, y el
    "vuelo libre" deja de serlo. El blanco tiene que ser un conductor NO
    magnético (aluminio o cobre) y la estructura cercana, no ferromagnética.
    """
    from .materials import MU0
    B_gap = B_r * t_mag / (t_mag + 2.0 * gap)
    return B_gap ** 2 * A_mag / (2.0 * MU0)


def solenoid_residual_force(I0: float, tau_decay: float, t: float,
                            dLdx: float) -> float:
    """Fuerza residual de un lanzador electromagnético tras el corte.

    La corriente decae como I0*exp(-t/tau) y la fuerza va con I^2, así que
    decae con tau/2. Es la razón por la que un lanzador electromagnético NO
    da vuelo libre limpio salvo que se apague la corriente con sobretensión
    (snubber Zener) antes de la separación.
    """
    I = I0 * math.exp(-t / tau_decay)
    return 0.5 * I ** 2 * dLdx


def free_flight(v0: float, gap: float, m: float, clock_deg: float = 0.0,
                extra_force: float = 0.0, d_proj: float = 8e-3,
                n: int = 400) -> dict:
    """Integra el tramo libre y devuelve la velocidad de impacto."""
    a_g = -G * math.cos(math.radians(clock_deg))

    def rhs(t, y):
        x, v = y
        F = m * a_g + extra_force - math.copysign(
            aero_drag_force(abs(v), d_proj), v)
        return [v, F / m]

    def hit(t, y):
        return y[0] - gap
    hit.terminal = True
    hit.direction = 1

    sol = solve_ivp(rhs, (0.0, 0.05), [0.0, v0], events=hit,
                    max_step=1e-6, rtol=1e-10, atol=1e-14)
    if not sol.t_events[0].size:
        raise RuntimeError("el proyectil no alcanza la cuña")
    t_f = float(sol.t_events[0][0])
    v_i = float(sol.y_events[0][0][1])
    return {
        "t_flight_s": t_f, "t_flight_us": t_f * 1e6,
        "v_impact_ms": v_i, "v0_ms": v0,
        "dv_ms": v_i - v0, "dv_rel": (v_i - v0) / v0,
        "dE_rel": (v_i ** 2 - v0 ** 2) / v0 ** 2,
        "E_impact_mJ": 0.5 * m * v_i ** 2 * 1e3,
        "gap_mm": gap * 1e3,
    }


def clock_sensitivity(v0: float, gap: float, m: float, stroke: float,
                      n: int = 25) -> list[dict]:
    """Sensibilidad a la posición horaria del crawler.

    Incluye el efecto de la gravedad sobre TODA la trayectoria (carrera
    acelerada + vuelo libre), que es el que importa: es el error que
    Westinghouse compensa activamente con la tensión del resorte según la
    hora del carro (patente US 5.295.388).
    """
    out = []
    for th in np.linspace(0.0, 360.0, n):
        a_g = -G * math.cos(math.radians(th))
        # Trabajo de la gravedad sobre carrera + vuelo.
        dE = m * a_g * (stroke + gap)
        E0 = 0.5 * m * v0 ** 2
        E = E0 + dE
        out.append({"clock_deg": float(th),
                    "hora": (th / 30.0) % 12,
                    "dE_mJ": dE * 1e3,
                    "dE_rel": dE / E0,
                    "E_mJ": E * 1e3,
                    "v_ms": math.sqrt(2.0 * E / m)})
    return out


# --------------------------------------------------------------------------
# Ventilación del cañón
# --------------------------------------------------------------------------

def size_vent(bore_d: float, v_max: float, F_launch: float,
              frac_allowed: float = 0.01, Cd: float = 0.6) -> dict:
    """Área de venteo necesaria para que el aire no robe más de `frac`."""
    A_p = math.pi * bore_d ** 2 / 4.0
    F_allowed = frac_allowed * F_launch
    dp_allowed = F_allowed / A_p
    A_v = A_p * v_max / (Cd * math.sqrt(2.0 * dp_allowed / RHO_AIR))
    return {
        "A_piston_mm2": A_p * 1e6,
        "v_max_ms": v_max,
        "F_allowed_N": F_allowed,
        "dp_allowed_Pa": dp_allowed,
        "A_vent_mm2": A_v * 1e6,
        "d_vent_equiv_mm": 2.0 * math.sqrt(A_v / math.pi) * 1e3,
        "n_agujeros_2mm": A_v / (math.pi * (1e-3) ** 2),
    }


def piston_effect_check(bore_d: float, clearance: float, v: float,
                        engaged_len: float, weight: float) -> dict:
    """Reproduce y generaliza la advertencia del brief §7.1.

    Con tubo guía ajustado el bombeo viscoso escala con 1/h^3.
    """
    A_p = math.pi * bore_d ** 2 / 4.0
    Q = A_p * v
    w = math.pi * bore_d
    dp = 12.0 * MU_AIR * engaged_len * Q / (w * clearance ** 3)
    F = dp * A_p
    return {"clearance_mm": clearance * 1e3, "dp_Pa": dp, "F_N": F,
            "F_%peso": 100.0 * F / weight}
