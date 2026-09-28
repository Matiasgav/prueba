"""Palanca en L con chapa plana (arquitectura vigente del brief, §4.1-4.3, §5).

Se implementa para poder comparar contra el módulo nuevo con el MISMO
criterio, y para reproducir la tabla §5 del brief como caso de regresión.

Ecuaciones (brief §4.1-§4.3):

    m_eq  = m_h + J_L/r_h^2 + m_a (r_eff_inst/r_h)^2
    E_maza= W_EM * m_h / m_eq
    v     = sqrt(2 E_maza / m_h)

    r_eff = y_contacto - y_pivote           (chapa plana => normal horizontal)
    theta = carrera / r_eff
    r_eff_inst = r_eff * cos(theta/2)       (barrido simétrico)

    T = 11 - D            recorrido vertical disponible [mm]
    Delta = R - 2.5       altura del centro de la bola sobre el pivote
    sqrt(1-s^2)/s = (T + Delta(1-cos theta)) / (Delta sin theta),  s = sin(alpha)
    r_h = Delta / s

NOTA SOBRE J_L (incógnita abierta #2 del brief): el informe original no
declara la inercia de la palanca. Reverse-engineering de la tabla §5 muestra
que es compatible con una barra de acero de sección 3 x 8 mm (J = m_barra
r_h^2/3), que reproduce las tres filas dentro de +-1.1 %. Se usa eso como
valor por defecto, EXPLÍCITAMENTE marcado como reconstruido.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .materials import STEEL

# Sección de palanca que reproduce la tabla §5 del brief (reconstruida).
LEVER_BAR_SECTION_M2 = 3e-3 * 8e-3
LEVER_LINEAR_DENSITY = STEEL.rho * LEVER_BAR_SECTION_M2   # [kg/m]


def uniform_bar_inertia(r_h: float,
                        lam: float = LEVER_LINEAR_DENSITY) -> float:
    """J de una barra uniforme de longitud r_h respecto del pivote [kg m^2]."""
    m_bar = lam * r_h
    return m_bar * r_h ** 2 / 3.0


def solve_hammer_arm(D_ball: float, theta: float,
                     chassis_h: float = 10e-3,
                     pivot_y: float = 1.5e-3,
                     wedge_clearance: float = 1e-3) -> dict:
    """Cinemática de §4.3: resuelve r_h y la oblicuidad alpha.

    D_ball  diámetro de la bola [m]
    theta   giro total de la palanca [rad]

    Convención del brief: T = 11 mm - D  y  Delta = R - 2.5 mm, con las
    cotas del §2 (chasis 10 mm, cara superior de la cuña en y = -1 mm,
    pivote en y = +1.5 mm).
    """
    R = D_ball / 2.0
    T = (chassis_h + wedge_clearance) - D_ball     # 11 mm - D
    Delta = R - pivot_y - 1e-3                      # R - 2.5 mm
    if T <= 0:
        raise ValueError("la bola no entra en el envolvente")
    if Delta <= 0:
        raise ValueError("centro de la bola por debajo del pivote")
    rhs = (T + Delta * (1.0 - math.cos(theta))) / (Delta * math.sin(theta))
    # sqrt(1-s^2)/s = rhs  =>  s = 1/sqrt(1+rhs^2)
    s = 1.0 / math.sqrt(1.0 + rhs ** 2)
    alpha = math.asin(s)
    r_h = Delta / s
    return {"R_m": R, "T_m": T, "Delta_m": Delta, "sin_alpha": s,
            "alpha_rad": alpha, "alpha_deg": math.degrees(alpha),
            "r_h_m": r_h, "theta_rad": theta,
            "theta_deg": math.degrees(theta)}


@dataclass
class LeverDesign:
    """Punto de diseño de la palanca en L con chapa plana."""

    y_contact: float = 7.0e-3       # altura del contacto actuador-palanca [m]
    y_pivot: float = 1.5e-3         # pivote [m]
    stroke: float = 3.0e-3          # carrera del actuador [m]
    D_ball: float = 8.0e-3          # diámetro de la maza [m]
    m_actuator: float = 3.49e-3     # masa móvil del actuador [kg]
    ball_material = STEEL
    lever_lambda: float = LEVER_LINEAR_DENSITY
    J_lever: float | None = None    # si se da, pisa el modelo de barra

    @property
    def r_eff(self) -> float:
        return self.y_contact - self.y_pivot

    @property
    def m_hammer(self) -> float:
        R = self.D_ball / 2.0
        return self.ball_material.rho * (4.0 / 3.0) * math.pi * R ** 3

    def solve(self, W_em: float) -> dict:
        theta = self.stroke / self.r_eff
        kin = solve_hammer_arm(self.D_ball, theta)
        r_h = kin["r_h_m"]
        r_eff_inst = self.r_eff * math.cos(theta / 2.0)
        J = (uniform_bar_inertia(r_h, self.lever_lambda)
             if self.J_lever is None else self.J_lever)
        m_h = self.m_hammer
        m_eq = (m_h + J / r_h ** 2
                + self.m_actuator * (r_eff_inst / r_h) ** 2)
        E_h = W_em * m_h / m_eq
        v = math.sqrt(2.0 * E_h / m_h)
        p = m_h * v
        return {
            **kin,
            "r_eff_mm": self.r_eff * 1e3,
            "r_eff_inst_mm": r_eff_inst * 1e3,
            "r_h_mm": r_h * 1e3,
            "m_hammer_g": m_h * 1e3,
            "m_eq_g": m_eq * 1e3,
            "J_reflected_g": J / r_h ** 2 * 1e3,
            "m_actuator_reflected_g": (
                self.m_actuator * (r_eff_inst / r_h) ** 2 * 1e3),
            "E_hammer_mJ": E_h * 1e3,
            "E_hammer_J": E_h,
            "v_ms": v,
            "p_mNs": p * 1e3,
            "p_normal_mNs": p * math.cos(kin["alpha_rad"]) * 1e3,
            "frac_actuator": (self.m_actuator * (r_eff_inst / r_h) ** 2) / m_eq,
            "frac_lever": (J / r_h ** 2) / m_eq,
            "frac_hammer": m_h / m_eq,
        }


def sweep_contact_height(W_em: float, heights_mm=(5.05, 7.0, 8.0),
                         **kw) -> list[dict]:
    out = []
    for h in heights_mm:
        d = LeverDesign(y_contact=h * 1e-3, **kw)
        r = d.solve(W_em)
        r["y_contact_mm"] = h
        out.append(r)
    return out


def sweep_ball_diameter(W_em: float, diameters_mm=(6, 7, 8, 9, 10),
                        y_contact_mm: float = 5.05, **kw) -> list[dict]:
    out = []
    for D in diameters_mm:
        try:
            d = LeverDesign(y_contact=y_contact_mm * 1e-3, D_ball=D * 1e-3,
                            **kw)
            r = d.solve(W_em)
            r["D_ball_mm"] = D
            r["feasible"] = True
        except ValueError as exc:
            r = {"D_ball_mm": D, "feasible": False, "reason": str(exc)}
        out.append(r)
    return out
