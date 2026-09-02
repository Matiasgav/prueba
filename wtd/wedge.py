"""Dinámica de la cuña de ranura con estados de ajuste y soltura.

MODELO FÍSICO (y por qué éste y no el del informe original)

El brief §4.7 ya advierte que el modelo empotrado-empotrado describe la cuña
AJUSTADA, que es justamente el caso que NO hay que detectar. Acá se modela la
física del asiento completa, y el empotrado-empotrado aparece como caso
límite en vez de como hipótesis.

    ranura del estator, vista en corte
    ---------------------------------------------------
      barras / bobinado          (fondo de la ranura)
      relleno
      RESORTE RIPPLE             empuja la cuña radialmente HACIA ADENTRO
      CUÑA G11                   apoyada contra los hombros de la cola de
      hombros de cola de milano  milano de los dientes
    ------------------ boca de la ranura ---------------
      entrehierro / bore         <- acá está el crawler

El golpe es radial HACIA AFUERA (el crawler empuja la cuña más adentro de la
ranura). Por lo tanto el golpe DESPEGA la cuña de los hombros y COMPRIME el
resorte ripple.

Con w(x,t) = desplazamiento en la dirección del golpe (positivo = hacia el
fondo de la ranura), el apoyo es BILINEAL y UNILATERAL:

    hombro (cola de milano)   R(x) = k_sh * max(0, i0 - w - gap)     >= 0
    resorte ripple            S(x) = -max(0, p0 + k_rs * w)          <= 0

con i0 = p0/k_sh la interferencia estática equivalente a la precarga. En
reposo, con la cuña ajustada, R = p0 y S = -p0: equilibrio.

La viga se resuelve LIBRE-LIBRE (incluye los dos modos de cuerpo rígido) y
todo el apoyo lo dan los contactos unilaterales. Así el modelo pasa de forma
continua de "empotrada-empotrada" (precarga alta, contactos siempre
cerrados) a "cuerpo libre sobre el ripple" (precarga nula, contactos
abiertos) sin cambiar de modelo.

CONSECUENCIA CLAVE: la cuña ajustada despega del hombro con apenas
i0 = p0/k_sh de movimiento (del orden del micrón), muy por debajo de los
~30 um de un impacto útil. Toda cuña despega; lo que cambia con el ajuste es
cuánta energía hace falta, cuánto tarda en reasentarse y con qué fuerza
vuelve. Por eso el sistema es NO LINEAL y la firma depende de la ENERGÍA DEL
GOLPE: un discriminante que un martillo de energía fija no puede aprovechar
y que esta arquitectura, que mide la energía tiro a tiro, sí.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .beam import BeamModel, BeamSection, BoundaryElastic
from .materials import G11_BEAM, Material


@dataclass
class WedgeSpec:
    """Geometría y material de la cuña.

    ADVERTENCIA DE GEOMETRÍA (incógnita abierta): el brief dice que la cuña
    es de sección 30 x 8 mm con los 30 mm "en profundidad, a lo largo del eje
    del generador", y a la vez analiza vanos de 50 y 100 mm. Un vano de 50 a
    100 mm en la dirección circunferencial es mayor que el ancho de cualquier
    ranura real. Las dos lecturas posibles son:

      (a) vano = longitud axial del tramo libre de cuña, sección 30 (circ.)
          x 8 (radial).  <- la que reproduce los anclas de §9, y la que se usa
      (b) vano = luz entre los apoyos de la cola de milano (ancho de ranura),
          y entonces el "30" es la longitud del tramo golpeado.

    Se usa (a) porque es la única compatible con los valores ancla, y la
    ambigüedad queda listada como incógnita abierta.
    """

    span: float = 50e-3        # vano libre [m]
    width: float = 30e-3       # ancho [m]
    thickness: float = 8e-3    # espesor (dirección del golpe) [m]
    material: Material = G11_BEAM
    kappa: float = 5.0 / 6.0
    n_elem: int = 60

    def section(self) -> BeamSection:
        return BeamSection(self.width, self.thickness, self.material.E,
                           self.material.rho, self.material.shear_modulus,
                           self.kappa)

    @property
    def mass(self) -> float:
        return self.material.rho * self.width * self.thickness * self.span

    @property
    def footprint(self) -> float:
        return self.span * self.width


@dataclass
class SupportSpec:
    """Estado de asiento de la cuña. Es LA variable del ensayo.

    preload        precarga total del ripple [N]  <- variable de ajuste
    k_ripple       rigidez del ripple por unidad de longitud [N/m^2]
    k_shoulder     rigidez de contacto del hombro por unidad de longitud
                   EFECTIVA sobre la zona de apoyo [N/m^2]
    gap            huelgo radial antes de tocar el hombro [m]
    support_mode   'ends'        apoyo sólo en las dos zonas extremas
                   'distributed' apoyo a lo largo de todo el vano
    land_width     ancho de cada zona de apoyo [m] (modo 'ends')
    zeta           amortiguamiento modal del material [-]
    c_slide        amortiguamiento distribuido por fricción de asiento
                   [N s/m por metro] = [N s/m^2]
    """

    preload: float = 1800.0
    k_ripple: float = 3.0e7
    k_shoulder: float = 2.0e10
    gap: float = 0.0
    support_mode: str = "ends"
    land_width: float = 5e-3
    zeta: float = 0.012
    c_slide: float = 0.0
    label: str = ""

    def describe(self) -> dict:
        return {"label": self.label, "preload_N": self.preload,
                "gap_um": self.gap * 1e6, "zeta": self.zeta,
                "k_ripple_N_m2": self.k_ripple,
                "k_shoulder_N_m2": self.k_shoulder,
                "support_mode": self.support_mode,
                "c_slide": self.c_slide}


def standard_states(P_tight: float = 1800.0,
                    support_mode: str = "distributed") -> list[SupportSpec]:
    """Escalera de estados de ajuste, de apretada a floja con juego.

    CORRECCIÓN (dato empírico del usuario, sep 2026): el modo por defecto era
    'ends', o sea la cuña apoyada SÓLO en sus dos extremos sobre un vano libre
    de 50 mm. Con ese modelo la cuña ajustada resulta poco impedante, se lleva
    mucha energía a sus modos de flexión y el martillo rebota MENOS que en la
    cuña floja: el índice Leeb salía creciente con la soltura.

    Empíricamente es al revés: la cuña floja disipa más y el Leeb baja. La
    razón es que una cuña realmente ajustada está acoplada al núcleo a lo
    largo de TODA su longitud, no en dos puntos, y por lo tanto su impedancia
    en el punto de golpe es altísima. Con apoyo distribuido el modelo
    reproduce el dato:

        estado        e (apoyo en extremos)   e (apoyo distribuido)
        S0 ajustada           0.678                  0.986
        S6 floja              0.782                  0.782

    Los dos modelos coinciden EXACTAMENTE en los estados flojos, porque ahí no
    hay apoyo en ninguno de los dos; difieren sólo en cuánta impedancia tiene
    la cuña ajustada, que es justo lo que el dato empírico resuelve.

    Nota sobre el otro mecanismo propuesto (rozamiento en los flancos): en
    este modelo un amortiguador sobre el apoyo SUBE el rebote, porque frena
    a la cuña y el martillo se encuentra un blanco más rígido. O sea que la
    fricción de flancos no explica el signo observado; la impedancia sí. La
    fricción sigue siendo relevante para el decaimiento del ring-down.

    La precarga de referencia de 1800 N sobre una huella de 50 x 30 mm son
    1.2 MPa de presión de asiento, que es el orden de magnitud típico de un
    resorte ripple correctamente instalado [E]. Es una incógnita abierta y
    está parametrizada.
    """
    kw = dict(k_ripple=3.0e7, k_shoulder=2.0e10, support_mode=support_mode)
    return [
        SupportSpec(preload=P_tight, gap=0.0, zeta=0.012, c_slide=0.0,
                    label="S0 · ajustada (100 %)", **kw),
        SupportSpec(preload=0.75 * P_tight, gap=0.0, zeta=0.014, c_slide=2e3,
                    label="S1 · 75 % precarga", **kw),
        SupportSpec(preload=0.50 * P_tight, gap=0.0, zeta=0.018, c_slide=5e3,
                    label="S2 · 50 % precarga", **kw),
        SupportSpec(preload=0.25 * P_tight, gap=0.0, zeta=0.025, c_slide=1e4,
                    label="S3 · 25 % precarga", **kw),
        SupportSpec(preload=0.05 * P_tight, gap=0.0, zeta=0.035, c_slide=2e4,
                    label="S4 · precarga residual (5 %)", **kw),
        SupportSpec(preload=0.0, gap=50e-6, zeta=0.045, c_slide=3e4,
                    label="S5 · floja, juego 50 µm", **kw),
        SupportSpec(preload=0.0, gap=200e-6, zeta=0.055, c_slide=3e4,
                    label="S6 · floja, juego 200 µm", **kw),
    ]


def asymmetric_states(P_tight: float = 1800.0) -> list[SupportSpec]:
    """Estados con un extremo suelto y el otro ajustado (caso real frecuente)."""
    out = []
    for frac in (0.0, 0.25, 0.5):
        s = SupportSpec(preload=P_tight, gap=0.0, zeta=0.03, c_slide=1e4,
                        support_mode="ends",
                        label=f"A · extremo izq. al {int(frac*100)} %")
        s.asym_left = frac          # atributo dinámico leído por WedgeModel
        out.append(s)
    return out


# --------------------------------------------------------------------------

class WedgeModel:
    """Modelo modal de la cuña LIBRE-LIBRE + apoyos unilaterales."""

    def __init__(self, wedge: WedgeSpec, support: SupportSpec,
                 n_modes: int = 24):
        self.wedge = wedge
        self.support = support
        self.beam = BeamModel(
            section=wedge.section(), length=wedge.span, n_elem=wedge.n_elem,
            left=BoundaryElastic.free(), right=BoundaryElastic.free(),
            foundation_k=0.0, shear=True, rotary=True)
        self.f, self.V = self.beam.modes(n_modes)
        self.n_modes = len(self.f)
        self.omega = 2.0 * math.pi * self.f
        self.x_nodes = self.beam.nodes
        w_dofs = np.arange(0, self.beam.ndof, 2)
        self.Phi = self.V[w_dofs, :]              # (n_nodes, n_modes)
        self.n_nodes = self.Phi.shape[0]

        # longitud tributaria de cada nodo
        dl = wedge.span / wedge.n_elem
        self.node_len = np.full(self.n_nodes, dl)
        self.node_len[0] *= 0.5
        self.node_len[-1] *= 0.5

        # máscara de la zona de apoyo del hombro
        x = self.x_nodes
        if support.support_mode == "ends":
            self.shoulder_mask = ((x <= support.land_width)
                                  | (x >= wedge.span - support.land_width))
        else:
            self.shoulder_mask = np.ones_like(x, dtype=bool)
        # el ripple actúa donde NO está el hombro (entre apoyos), o en todo
        # el vano si el apoyo es distribuido
        self.ripple_mask = (~self.shoulder_mask
                            if support.support_mode == "ends"
                            else np.ones_like(x, dtype=bool))

        L_sh = float((self.node_len * self.shoulder_mask).sum())
        L_rp = float((self.node_len * self.ripple_mask).sum())
        self.L_shoulder = L_sh
        self.L_ripple = L_rp
        # precarga por unidad de longitud sobre la zona de ripple
        self.p0_lin = support.preload / max(L_rp, 1e-12)
        # reacción por unidad de longitud sobre la zona de hombro
        self.r0_lin = support.preload / max(L_sh, 1e-12)
        self.i0 = self.r0_lin / support.k_shoulder

        # asimetría opcional: factor de precarga por nodo del hombro
        self.shoulder_scale = np.ones(self.n_nodes)
        frac = getattr(support, "asym_left", None)
        if frac is not None:
            left = x < wedge.span / 2.0
            self.shoulder_scale[left] = frac

        self._k_sh_node = (support.k_shoulder * self.node_len
                           * self.shoulder_mask)
        self._k_rp_node = (support.k_ripple * self.node_len
                           * self.ripple_mask)
        self._c_node = support.c_slide * self.node_len
        self._i0_node = self.i0 * self.shoulder_scale
        self._p0_node = self.p0_lin * self.node_len * self.ripple_mask

    # ---- fuerzas del apoyo --------------------------------------------
    def support_force(self, w: np.ndarray, wd: np.ndarray) -> np.ndarray:
        """Fuerza NODAL del apoyo, positiva en la dirección del golpe [N]."""
        s = self.support
        R = self._k_sh_node * np.maximum(0.0, self._i0_node - w - s.gap)
        S = -np.maximum(0.0, self._p0_node + self._k_rp_node * w)
        return R + S - self._c_node * wd

    def contact_state(self, w: np.ndarray) -> dict:
        s = self.support
        seated = (self._i0_node - w - s.gap) > 0.0
        n_sh = max(int(self.shoulder_mask.sum()), 1)
        return {"frac_seated": float((seated & self.shoulder_mask).sum()
                                     / n_sh)}

    def static_equilibrium(self, tol: float = 1e-14, it: int = 200
                           ) -> np.ndarray:
        """Equilibrio estático modal bajo la precarga (Newton amortiguado)."""
        q = np.zeros(self.n_modes)
        w2 = self.omega ** 2
        for _ in range(it):
            w = self.Phi @ q
            f = self.support_force(w, np.zeros_like(w))
            res = self.Phi.T @ f - w2 * q
            if np.max(np.abs(res)) < tol:
                break
            # Jacobiano aproximado: rigidez tangente de los contactos activos
            s = self.support
            act_sh = (self._i0_node - w - s.gap) > 0.0
            act_rp = (self._p0_node + self._k_rp_node * w) > 0.0
            kt = -(self._k_sh_node * act_sh) - (self._k_rp_node * act_rp)
            J = (self.Phi.T * kt) @ self.Phi - np.diag(w2)
            try:
                dq = np.linalg.solve(J, -res)
            except np.linalg.LinAlgError:
                break
            q = q + 0.5 * dq
        return q

    # ---- referencias lineales -----------------------------------------
    def seated_linear_beam(self) -> BeamModel:
        """Viga con los apoyos CERRADOS, linealizada. Cuña ajustada."""
        s = self.support
        extra = []
        for i, xi in enumerate(self.x_nodes):
            if self.shoulder_mask[i]:
                extra.append((float(xi),
                              s.k_shoulder * self.node_len[i], 0.0))
        return BeamModel(
            section=self.wedge.section(), length=self.wedge.span,
            n_elem=self.wedge.n_elem,
            left=BoundaryElastic.free(), right=BoundaryElastic.free(),
            foundation_k=s.k_ripple if s.support_mode == "distributed" else 0.0,
            shear=True, rotary=True, extra_springs=tuple(extra))

    def lifted_linear_beam(self) -> BeamModel:
        """Viga con el hombro ABIERTO: sólo el ripple. Cuña floja."""
        s = self.support
        return BeamModel(
            section=self.wedge.section(), length=self.wedge.span,
            n_elem=self.wedge.n_elem,
            left=BoundaryElastic.free(), right=BoundaryElastic.free(),
            foundation_k=s.k_ripple, shear=True, rotary=True)

    def bounding_frequencies(self, n: int = 4) -> dict:
        fs, _ = self.seated_linear_beam().modes(n)
        fl, _ = self.lifted_linear_beam().modes(n)
        return {"seated_Hz": [float(v) for v in fs],
                "lifted_Hz": [float(v) for v in fl]}
