"""Viga de Timoshenko por elementos finitos, con fundación de Winkler y
restricciones elásticas en los extremos.

Es el motor de la dinámica de la cuña. Cubre desde la cuña perfectamente
ajustada (empotrada-empotrada, el caso de §4.7 del brief) hasta la cuña
completamente suelta (libre-libre sobre el resorte ripple), pasando por
todos los estados intermedios con restricciones elásticas parametrizadas.

Elemento: 2 nodos, 2 gdl por nodo (w = flecha, theta = giro de la sección).
Matriz de rigidez exacta de Timoshenko (sin bloqueo por corte) y matriz de
masa consistente de Przemieniecki (traslación + inercia rotatoria).

Verificación (ver tests/test_anclas.py):
  * kappa -> inf  y  sin inercia rotatoria  ==>  Euler-Bernoulli exacto
    L = 50 mm  -> f1 = 11691 Hz   (ancla §9)
    L = 100 mm -> f1 = 2922.7 Hz  (ancla §9)
  * rigidez estática a medio vano  -> 192 EI/L^3 = 47.19 MN/m (L = 50 mm)
  * masa modal EB / masa total     -> 0.39648
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.linalg import eigh

# Un empotramiento NO se modela con un resorte muy rígido: una penalidad de
# 1e14 N/m frente a una rigidez de elemento de 1e12 N/m arruina el número de
# condición de K y el problema de autovalores generalizado devuelve valores
# groseramente erróneos (se verificó: +13.7% en f1 de la viga empotrada).
# Los grados de libertad con rigidez infinita se ELIMINAN del sistema.
BIG = math.inf


@dataclass
class BeamSection:
    """Sección rectangular de la cuña."""

    width: float      # ancho b [m] (dimensión perpendicular al golpe)
    thickness: float  # espesor h [m] (dimensión en la dirección del golpe)
    E: float          # módulo de Young [Pa]
    rho: float        # densidad [kg/m^3]
    G: float          # módulo de corte [Pa]
    kappa: float = 5.0 / 6.0   # factor de corrección por corte [-]

    @property
    def A(self) -> float:
        return self.width * self.thickness

    @property
    def I(self) -> float:
        return self.width * self.thickness ** 3 / 12.0

    @property
    def EI(self) -> float:
        return self.E * self.I

    @property
    def rhoA(self) -> float:
        return self.rho * self.A

    @property
    def rhoI(self) -> float:
        return self.rho * self.I

    @property
    def GAk(self) -> float:
        return self.kappa * self.G * self.A


def _elem_K(sec: BeamSection, Le: float, shear: bool) -> np.ndarray:
    """Rigidez exacta del elemento de Timoshenko."""
    EI = sec.EI
    phi = 12.0 * EI / (sec.GAk * Le ** 2) if shear else 0.0
    c = EI / ((1.0 + phi) * Le ** 3)
    L = Le
    K = np.array([
        [12.0,        6.0 * L,               -12.0,       6.0 * L],
        [6.0 * L,     (4.0 + phi) * L * L,   -6.0 * L,    (2.0 - phi) * L * L],
        [-12.0,      -6.0 * L,                12.0,      -6.0 * L],
        [6.0 * L,     (2.0 - phi) * L * L,   -6.0 * L,    (4.0 + phi) * L * L],
    ])
    return c * K


def _elem_M(sec: BeamSection, Le: float, shear: bool,
            rotary: bool) -> np.ndarray:
    """Masa consistente de Timoshenko (Przemieniecki, 1968)."""
    EI = sec.EI
    phi = 12.0 * EI / (sec.GAk * Le ** 2) if shear else 0.0
    L = Le
    p = phi
    p2 = phi * phi
    d = (1.0 + p) ** 2

    a11 = 13.0 / 35.0 + 7.0 * p / 10.0 + p2 / 3.0
    a12 = (11.0 / 210.0 + 11.0 * p / 120.0 + p2 / 24.0) * L
    a13 = 9.0 / 70.0 + 3.0 * p / 10.0 + p2 / 6.0
    a14 = -(13.0 / 420.0 + 3.0 * p / 40.0 + p2 / 24.0) * L
    a22 = (1.0 / 105.0 + p / 60.0 + p2 / 120.0) * L * L
    a24 = -(1.0 / 140.0 + p / 60.0 + p2 / 120.0) * L * L

    Mt = np.array([
        [a11,  a12,  a13,  a14],
        [a12,  a22, -a14,  a24],
        [a13, -a14,  a11, -a12],
        [a14,  a24, -a12,  a22],
    ]) * (sec.rhoA * L / d)

    if not rotary:
        return Mt

    b11 = 6.0 / 5.0
    b12 = (1.0 / 10.0 - p / 2.0) * L
    b22 = (2.0 / 15.0 + p / 6.0 + p2 / 3.0) * L * L
    b24 = (-1.0 / 30.0 - p / 6.0 + p2 / 6.0) * L * L

    Mr = np.array([
        [b11,   b12,  -b11,   b12],
        [b12,   b22,  -b12,   b24],
        [-b11, -b12,   b11,  -b12],
        [b12,   b24,  -b12,   b22],
    ]) * (sec.rhoI / (d * L))

    return Mt + Mr


@dataclass
class BoundaryElastic:
    """Restricción elástica en un extremo (o en un nodo interior)."""

    k_trans: float = 0.0   # [N/m]
    k_rot: float = 0.0     # [N·m/rad]

    @staticmethod
    def clamped() -> "BoundaryElastic":
        return BoundaryElastic(BIG, BIG)

    @staticmethod
    def pinned() -> "BoundaryElastic":
        return BoundaryElastic(BIG, 0.0)

    @staticmethod
    def free() -> "BoundaryElastic":
        return BoundaryElastic(0.0, 0.0)


@dataclass
class BeamModel:
    """Viga discretizada. Ensambla K, M y resuelve modos."""

    section: BeamSection
    length: float
    n_elem: int = 60
    left: BoundaryElastic = field(default_factory=BoundaryElastic.clamped)
    right: BoundaryElastic = field(default_factory=BoundaryElastic.clamped)
    foundation_k: float = 0.0     # rigidez de Winkler [N/m por metro] = [N/m^2]
    shear: bool = True            # incluir deformación por corte
    rotary: bool = True           # incluir inercia rotatoria
    extra_springs: tuple = ()     # ((x, k_trans, k_rot), ...) resortes interiores
    extra_masses: tuple = ()      # ((x, m, J), ...) masas concentradas

    def __post_init__(self):
        self._assemble()

    # -- geometría -------------------------------------------------------
    @property
    def nodes(self) -> np.ndarray:
        return np.linspace(0.0, self.length, self.n_elem + 1)

    @property
    def ndof(self) -> int:
        return 2 * (self.n_elem + 1)

    def node_index(self, x: float) -> int:
        return int(np.argmin(np.abs(self.nodes - x)))

    def dof_w(self, node: int) -> int:
        return 2 * node

    def dof_t(self, node: int) -> int:
        return 2 * node + 1

    # -- ensamble --------------------------------------------------------
    def _assemble(self) -> None:
        n = self.ndof
        K = np.zeros((n, n))
        M = np.zeros((n, n))
        Le = self.length / self.n_elem
        Ke = _elem_K(self.section, Le, self.shear)
        Me = _elem_M(self.section, Le, self.shear, self.rotary)
        for e in range(self.n_elem):
            idx = np.array([2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3])
            K[np.ix_(idx, idx)] += Ke
            M[np.ix_(idx, idx)] += Me

        # Fundación de Winkler consistente: k_f * integral(N^T N) dx.
        # Para las funciones de forma de Hermite el resultado es la matriz de
        # masa consistente de Euler-Bernoulli con rhoA -> k_f.
        if self.foundation_k > 0.0:
            L = Le
            Nf = np.array([
                [156.0,   22.0 * L,   54.0,   -13.0 * L],
                [22.0 * L, 4.0 * L * L, 13.0 * L, -3.0 * L * L],
                [54.0,    13.0 * L,   156.0,  -22.0 * L],
                [-13.0 * L, -3.0 * L * L, -22.0 * L, 4.0 * L * L],
            ]) * (self.foundation_k * L / 420.0)
            for e in range(self.n_elem):
                idx = np.array([2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3])
                K[np.ix_(idx, idx)] += Nf

        # Restricciones elásticas de extremo (inf => GDL eliminado).
        fixed: set[int] = set()

        def add_spring(dof: int, k: float) -> None:
            if k == math.inf:
                fixed.add(dof)
            elif k > 0.0:
                K[dof, dof] += k

        add_spring(0, self.left.k_trans)
        add_spring(1, self.left.k_rot)
        add_spring(n - 2, self.right.k_trans)
        add_spring(n - 1, self.right.k_rot)

        for (x, kt, kr) in self.extra_springs:
            i = self.node_index(x)
            add_spring(self.dof_w(i), kt)
            add_spring(self.dof_t(i), kr)

        for (x, m, J) in self.extra_masses:
            i = self.node_index(x)
            M[self.dof_w(i), self.dof_w(i)] += m
            M[self.dof_t(i), self.dof_t(i)] += J

        self.K_full = K
        self.M_full = M
        self.fixed = np.array(sorted(fixed), dtype=int)
        self.free_dofs = np.array(
            [d for d in range(n) if d not in fixed], dtype=int)
        self.K = K[np.ix_(self.free_dofs, self.free_dofs)]
        self.M = M[np.ix_(self.free_dofs, self.free_dofs)]

    def _expand(self, u_red: np.ndarray) -> np.ndarray:
        """Lleva un vector del sistema reducido al sistema completo."""
        if u_red.ndim == 1:
            u = np.zeros(self.ndof)
            u[self.free_dofs] = u_red
            return u
        u = np.zeros((self.ndof, u_red.shape[1]))
        u[self.free_dofs, :] = u_red
        return u

    # -- resultados ------------------------------------------------------
    @property
    def total_mass(self) -> float:
        return self.section.rhoA * self.length

    def static_stiffness_at(self, x: float) -> float:
        """Rigidez estática puntual vista en x [N/m]."""
        i = self.dof_w(self.node_index(x))
        if i in set(self.fixed.tolist()):
            return float("inf")
        j = int(np.searchsorted(self.free_dofs, i))
        f = np.zeros(len(self.free_dofs))
        f[j] = 1.0
        u = np.linalg.solve(self.K, f)
        return 1.0 / u[j]

    def modes(self, n_modes: int = 12) -> tuple[np.ndarray, np.ndarray]:
        """Frecuencias [Hz] y modos normalizados en masa (phi^T M phi = I).

        Los modos se devuelven en el sistema COMPLETO (con ceros en los GDL
        restringidos), de modo que `V[dof_w(i), r]` siempre es válido.
        """
        w2, V = eigh(self.K, self.M)
        w2 = np.clip(w2, 0.0, None)
        f = np.sqrt(w2) / (2.0 * math.pi)
        k = min(n_modes, len(f))
        return f[:k], self._expand(V[:, :k])

    def modal_properties_at(self, x: float, n_modes: int = 6) -> list[dict]:
        """Masa y rigidez modal referidas al desplazamiento en x."""
        f, V = self.modes(n_modes)
        i = self.dof_w(self.node_index(x))
        out = []
        for r in range(len(f)):
            phi = V[i, r]
            if abs(phi) < 1e-12:
                m_eff = float("inf")
                k_eff = float("inf")
            else:
                m_eff = 1.0 / (phi ** 2)     # phi normalizado en masa
                k_eff = m_eff * (2.0 * math.pi * f[r]) ** 2
            out.append({
                "mode": r + 1,
                "f_Hz": float(f[r]),
                "m_eff_kg": float(m_eff),
                "k_eff_N_m": float(k_eff),
                "participation": float(phi),
            })
        return out

    def first_mode_at(self, x: float) -> dict:
        return self.modal_properties_at(x, n_modes=1)[0]


# --------------------------------------------------------------------------
# Constructores de conveniencia
# --------------------------------------------------------------------------

def euler_bernoulli_clamped(section: BeamSection, length: float,
                            n_elem: int = 60) -> BeamModel:
    """Viga Euler-Bernoulli empotrada-empotrada (para reproducir anclas)."""
    return BeamModel(section=section, length=length, n_elem=n_elem,
                     left=BoundaryElastic.clamped(),
                     right=BoundaryElastic.clamped(),
                     shear=False, rotary=False)


def timoshenko_clamped(section: BeamSection, length: float,
                       n_elem: int = 60) -> BeamModel:
    return BeamModel(section=section, length=length, n_elem=n_elem,
                     left=BoundaryElastic.clamped(),
                     right=BoundaryElastic.clamped(),
                     shear=True, rotary=True)


def solve_kappa_for_frequency(section: BeamSection, length: float,
                              f_target: float, n_elem: int = 60,
                              bracket: tuple[float, float] = (0.05, 5.0)
                              ) -> float:
    """Encuentra el kappa que reproduce una f1 dada.

    Sirve para responder la incógnita abierta #5 del brief: el informe
    original declara f1 = 9376 Hz para el vano de 50 mm con G = 5.7 GPa pero
    NO declara kappa. Esta función devuelve el kappa implícito.
    """
    from scipy.optimize import brentq

    def err(kappa: float) -> float:
        sec = BeamSection(section.width, section.thickness, section.E,
                          section.rho, section.G, kappa)
        m = timoshenko_clamped(sec, length, n_elem)
        f, _ = m.modes(1)
        return f[0] - f_target

    lo, hi = bracket
    return float(brentq(err, lo, hi, xtol=1e-6))
