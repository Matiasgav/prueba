"""Modelo 3D de la cuña de ranura: elementos finitos + contactos unilaterales.

QUÉ RESUELVE

La cuña es un sólido elástico 3D (trapecio extruido) metido en la cola de
milano del núcleo. Tiene tres tipos de contacto, todos UNILATERALES (sólo
empujan, se pueden abrir):

    flancos   cuña contra el núcleo (hierro laminado, rígido)   ley de Hertz
              + rozamiento de Coulomb con tramo adherido (Mindlin)
    fondo     cuña contra la barra, a través del ripple spring  resorte
              precomprimido, o contacto de Hertz si no hay ripple
    golpe     punta esférica del impactador sobre la cara superior   Hertz

Ejes:  x axial (a lo largo de la ranura, 0..L)
       y radial, positivo hacia el entrehierro (la barra está en y < 0)
       z circunferencial (ancho de la cuña)

Sección: trapecio con la base mayor B contra la barra (y = 0) y la menor b
hacia el entrehierro (y = e). Los flancos inclinados apoyan contra los
hombros de la cola de milano, que están por ENCIMA de ellos: la barra empuja
la cuña hacia arriba y los hombros la frenan.

DISCRETIZACIÓN

Hexaedros cuadráticos de Lagrange de 27 nodos (Q2) con los nodos en los
puntos de Gauss-Lobatto (-1, 0, 1). Rigidez integrada con 3x3x3 puntos de
Gauss. Masa integrada con la cuadratura de Gauss-Lobatto en los propios
nodos, que da una matriz de masa DIAGONAL sin pesos negativos (esquema de
elementos espectrales de orden 2): es lo que permite integrar en el tiempo
de forma explícita.

Como la sección no cambia a lo largo de x, las 18 matrices elementales de
la sección se calculan una vez y se reusan en todos los tramos axiales.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

# ---------------------------------------------------------------------------
# Material: G11 ortótropo
# ---------------------------------------------------------------------------


@dataclass
class Ortotropo:
    """Laminado tejido vidrio-epoxi con las capas paralelas a las caras anchas.

    Ejes del material = ejes del modelo: 1 = x (axial), 2 = y (normal a las
    capas, radial), 3 = z (circunferencial). En el plano de las capas (x, z)
    el tejido es casi balanceado; a través del espesor manda la resina.
    Todos son valores típicos [E], no medidos sobre la cuña real.
    """

    E1: float = 24e9     # axial, en el plano de las capas   (= repo, G11_BEAM)
    E2: float = 12e9     # a través del espesor
    E3: float = 24e9     # circunferencial, en el plano
    G12: float = 4.5e9   # corte xy (interlaminar)
    G13: float = 5.5e9   # corte xz (en el plano)
    G23: float = 4.5e9   # corte yz (interlaminar)
    nu12: float = 0.30   # contracción en y al traccionar en x
    nu13: float = 0.12   # contracción en z al traccionar en x
    nu32: float = 0.30   # contracción en y al traccionar en z
    rho: float = 1900.0

    def D(self) -> np.ndarray:
        """Matriz constitutiva 6x6, orden de Voigt [xx, yy, zz, yz, xz, xy]."""
        S = np.zeros((6, 6))
        S[0, 0], S[1, 1], S[2, 2] = 1 / self.E1, 1 / self.E2, 1 / self.E3
        S[0, 1] = S[1, 0] = -self.nu12 / self.E1
        S[0, 2] = S[2, 0] = -self.nu13 / self.E1
        S[1, 2] = S[2, 1] = -self.nu32 / self.E3
        S[3, 3], S[4, 4], S[5, 5] = 1 / self.G23, 1 / self.G13, 1 / self.G12
        D = np.linalg.inv(S)
        assert np.all(np.linalg.eigvalsh(D) > 0), "material no definido positivo"
        return D


def isotropo(E: float, nu: float, rho: float) -> Ortotropo:
    """Caso isótropo, para verificar contra soluciones analíticas."""
    G = E / (2 * (1 + nu))
    return Ortotropo(E, E, E, G, G, G, nu, nu, nu, rho)


# ---------------------------------------------------------------------------
# Geometría y malla
# ---------------------------------------------------------------------------


@dataclass
class Geometria:
    L: float = 200e-3      # largo axial
    B: float = 35e-3       # base mayor, contra la barra (y = 0)
    b: float = 25e-3       # base menor, hacia el entrehierro (y = e)
    e: float = 10e-3       # espesor radial
    ne_x: int = 40         # elementos axiales
    ne_y: int = 3          # elementos en el espesor
    ne_z: int = 6          # elementos en el ancho

    def ancho(self, y):
        return self.B - (self.B - self.b) * np.asarray(y) / self.e

    @property
    def alfa_flanco(self) -> float:
        """Ángulo del flanco respecto de la dirección radial [rad]."""
        return math.atan(0.5 * (self.B - self.b) / self.e)

    @property
    def masa(self) -> float:
        return 0.5 * (self.B + self.b) * self.e * self.L


GLL = np.array([-1.0, 0.0, 1.0])
W_GLL = np.array([1 / 3, 4 / 3, 1 / 3])
GAUSS = np.array([-math.sqrt(0.6), 0.0, math.sqrt(0.6)])
W_GAUSS = np.array([5 / 9, 8 / 9, 5 / 9])


def _N1(s):
    s = np.asarray(s, float)
    return np.stack([0.5 * s * (s - 1), 1 - s * s, 0.5 * s * (s + 1)], -1)


def _dN1(s):
    s = np.asarray(s, float)
    return np.stack([s - 0.5, -2 * s, s + 0.5], -1)


class Malla:
    """Malla estructurada de Q2. Nodo (ix, iy, iz) -> ix*ny*nz + iy*nz + iz."""

    def __init__(self, g: Geometria):
        self.g = g
        self.nx, self.ny, self.nz = 2 * g.ne_x + 1, 2 * g.ne_y + 1, 2 * g.ne_z + 1
        ix, iy, iz = np.meshgrid(np.arange(self.nx), np.arange(self.ny),
                                 np.arange(self.nz), indexing="ij")
        x = ix * g.L / (self.nx - 1)
        y = iy * g.e / (self.ny - 1)
        z = (iz / (self.nz - 1) - 0.5) * g.ancho(y)
        self.X = np.stack([x.ravel(), y.ravel(), z.ravel()], 1)
        self.n_nodos = self.X.shape[0]
        self.n_dof = 3 * self.n_nodos

    def nodo(self, ix, iy, iz):
        return (np.asarray(ix) * self.ny + np.asarray(iy)) * self.nz + np.asarray(iz)

    def nodos_elem(self, ex, ey, ez):
        a, b, c = np.meshgrid(np.arange(3), np.arange(3), np.arange(3), indexing="ij")
        return self.nodo(2 * ex + a.ravel(), 2 * ey + b.ravel(), 2 * ez + c.ravel())


# ---------------------------------------------------------------------------
# Matrices elementales y ensamblado
# ---------------------------------------------------------------------------


def _forma3(xi, eta, zeta):
    """N (27,) y dN/d(xi,eta,zeta) (27, 3), orden local a*9 + b*3 + c."""
    Na, Nb, Nc = _N1(xi), _N1(eta), _N1(zeta)
    da, db, dc = _dN1(xi), _dN1(eta), _dN1(zeta)
    N = np.einsum("a,b,c->abc", Na, Nb, Nc).ravel()
    dN = np.stack([np.einsum("a,b,c->abc", da, Nb, Nc).ravel(),
                   np.einsum("a,b,c->abc", Na, db, Nc).ravel(),
                   np.einsum("a,b,c->abc", Na, Nb, dc).ravel()], 1)
    return N, dN


def _B(dNx):
    """Matriz deformación-desplazamiento 6 x 81 (Voigt, deformaciones de ingeniería)."""
    n = dNx.shape[0]
    B = np.zeros((6, 3 * n))
    B[0, 0::3] = dNx[:, 0]
    B[1, 1::3] = dNx[:, 1]
    B[2, 2::3] = dNx[:, 2]
    B[3, 1::3], B[3, 2::3] = dNx[:, 2], dNx[:, 1]   # gamma_yz
    B[4, 0::3], B[4, 2::3] = dNx[:, 2], dNx[:, 0]   # gamma_xz
    B[5, 0::3], B[5, 1::3] = dNx[:, 1], dNx[:, 0]   # gamma_xy
    return B


def elemento(Xe: np.ndarray, D: np.ndarray, rho: float):
    """Rigidez (81x81, Gauss 3x3x3) y masa diagonal (27, Gauss-Lobatto)."""
    Ke = np.zeros((81, 81))
    for i, xi in enumerate(GAUSS):
        for j, et in enumerate(GAUSS):
            for k, ze in enumerate(GAUSS):
                _, dN = _forma3(xi, et, ze)
                J = dN.T @ Xe                      # 3x3, filas d/dxi
                detJ = np.linalg.det(J)
                dNx = dN @ np.linalg.inv(J).T
                B = _B(dNx)
                Ke += B.T @ D @ B * detJ * W_GAUSS[i] * W_GAUSS[j] * W_GAUSS[k]
    me = np.zeros(27)
    for a, xi in enumerate(GLL):
        for b, et in enumerate(GLL):
            for c, ze in enumerate(GLL):
                _, dN = _forma3(xi, et, ze)
                detJ = np.linalg.det(dN.T @ Xe)
                me[a * 9 + b * 3 + c] = rho * detJ * W_GLL[a] * W_GLL[b] * W_GLL[c]
    return Ke, me


def ensamblar(m: Malla, mat: Ortotropo):
    """K (CSR) y diagonal de masa por dof."""
    D = mat.D()
    g = m.g
    rows, cols, vals = [], [], []
    mdiag = np.zeros(m.n_nodos)
    ex = np.arange(g.ne_x)
    for ey in range(g.ne_y):
        for ez in range(g.ne_z):
            n0 = m.nodos_elem(0, ey, ez)
            Ke, me = elemento(m.X[n0], D, mat.rho)
            nodes = np.stack([m.nodos_elem(e, ey, ez) for e in ex])      # (ne_x, 27)
            dofs = (3 * nodes[:, :, None] + np.arange(3)).reshape(len(ex), 81)
            rows.append(np.repeat(dofs, 81, axis=1).ravel())
            cols.append(np.tile(dofs, (1, 81)).ravel())
            vals.append(np.tile(Ke.ravel(), len(ex)))
            np.add.at(mdiag, nodes.ravel(), np.tile(me, len(ex)))
    K = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(m.n_dof, m.n_dof)).tocsr()
    K = 0.5 * (K + K.T)
    return K, np.repeat(mdiag, 3)


# ---------------------------------------------------------------------------
# Superficies de contacto: nodos, áreas tributarias y normales
# ---------------------------------------------------------------------------


def _pesos_1d(n_elem: int, largo: float) -> np.ndarray:
    """Pesos tributarios de Gauss-Lobatto sobre una línea de n_elem elementos Q2."""
    w = np.zeros(2 * n_elem + 1)
    for e in range(n_elem):
        w[2 * e:2 * e + 3] += W_GLL * (largo / n_elem) / 2
    return w


@dataclass
class Superficie:
    nodos: np.ndarray      # (n,)
    area: np.ndarray       # (n,) área tributaria [m^2]
    normal: np.ndarray     # (n, 3) normal SALIENTE de la cuña
    x: np.ndarray          # (n,) posición axial
    ij: tuple = ()         # forma (nx, nt) para graficar


def superficies(m: Malla) -> dict[str, Superficie]:
    g = m.g
    wx = _pesos_1d(g.ne_x, g.L)
    s_fl = math.hypot(g.e, 0.5 * (g.B - g.b))
    ws = _pesos_1d(g.ne_y, s_fl)
    ix, iy = np.meshgrid(np.arange(m.nx), np.arange(m.ny), indexing="ij")
    out = {}
    a = g.alfa_flanco
    for nombre, iz, sz in (("flanco_der", m.nz - 1, 1.0), ("flanco_izq", 0, -1.0)):
        nod = m.nodo(ix, iy, iz).ravel()
        n = np.array([0.0, math.sin(a), sz * math.cos(a)])
        out[nombre] = Superficie(nod, np.outer(wx, ws).ravel(), np.tile(n, (nod.size, 1)),
                                 m.X[nod, 0], (m.nx, m.ny))
    for nombre, iy0, ancho, ny_ in (("fondo", 0, g.B, -1.0), ("tapa", m.ny - 1, g.b, 1.0)):
        wz = _pesos_1d(g.ne_z, ancho)
        jx, jz = np.meshgrid(np.arange(m.nx), np.arange(m.nz), indexing="ij")
        nod = m.nodo(jx, iy0, jz).ravel()
        out[nombre] = Superficie(nod, np.outer(wx, wz).ravel(),
                                 np.tile([0.0, ny_, 0.0], (nod.size, 1)), m.X[nod, 0], (m.nx, m.nz))
    return out


# ---------------------------------------------------------------------------
# Leyes de contacto
# ---------------------------------------------------------------------------


@dataclass
class Contactos:
    """Parámetros de las interfaces. Todo lo marcado [E] es estimado.

    FLANCOS (cuña G11 contra chapa laminada). El contacto es plano sobre
    plano, pero rugoso: la carga la llevan las asperezas, cada una un
    contacto de Hertz. Con asperezas de altura pareja eso da la misma ley
    potencial que Hertz,

        p = C_fl * delta^(3/2)          (presión de contacto)
        k_n = dp/d(delta) = 1.5 C^(2/3) p^(1/3)

    o sea una rigidez normal que CRECE con la presión: la cuña más apretada
    es más rígida en sus apoyos. C_fl se fija dando k_n a 1 MPa [E].

    ROZAMIENTO: Coulomb con tramo adherido elástico (Mindlin):
        k_t = kappa_t * k_n,   |q| <= mu * p
    """

    kn_flanco_1MPa: float = 2.0e12    # [N/m^3]  rigidez normal por área a 1 MPa [E]
    kappa_t: float = 0.8              # k_t / k_n  (Mindlin, 2(1-nu)/(2-nu)) [E]
    mu: float = 0.30                  # rozamiento G11 / acero laminado [E]

    # FONDO con ripple spring: resorte por unidad de área, unilateral.
    # 1 MPa con ~1,4 mm de compresión (resorte de 1,8 mm al 80 %) [E]
    k_ripple: float = 7.0e8           # [N/m^3]
    kappa_t_ripple: float = 0.3       # adherencia tangencial en las crestas [E]
    mu_ripple: float = 0.30
    ripple: bool = True               # False: fondo rígido con ley de Hertz como flancos
    d_solido_ripple: float = 1.8e-3   # compresión a la que el ripple queda aplastado [E]

    # CHOQUES. Los contactos normales disipan con la ley de Hunt-Crossley,
    #     p = C delta^(3/2) (1 + chi * d(delta)/dt)_+
    # que da un coeficiente de restitución e al cerrar a velocidad v_ref con
    # chi = 8 (1 - e) / (5 e v_ref)   (Flores et al. 2011; la de Lankarani-
    # Nikravesh, 3(1-e^2)/(4 v), sólo vale cerca de e = 1 y da 0,80 si se pide 0,7).
    # Se aplica a los contactos que en reposo están abiertos o sin presión:
    # son los que CHOCAN. Un asiento precargado disipa por microdeslizamiento
    # (el rozamiento); Hunt-Crossley ahí daría un amortiguamiento irreal.
    e_rest: float = 0.7               # restitución G11 contra acero [E]
    v_ref_rest: float = 0.05          # velocidad a la que vale e_rest [m/s]

    # PARED LATERAL de la cola de milano: la esquina inferior de la cuña
    # contra la pared vertical del núcleo, a juego_lateral [E]. Contacto de
    # línea, casi lineal: q = k_linea * delta por unidad de largo.
    juego_lateral: float = 0.3e-3     # [m]
    k_linea: float = 1.5e10           # ~ (pi/4) E* para G11 contra acero [N/m por m]

    def chi(self) -> float:
        return 8 * (1 - self.e_rest) / (5 * self.e_rest * self.v_ref_rest)

    def C_hertz(self) -> float:
        """C de p = C delta^1.5 que da kn_flanco_1MPa a p = 1 MPa."""
        p = 1e6
        return (self.kn_flanco_1MPa / (1.5 * p ** (1 / 3))) ** 1.5


@dataclass
class Estado:
    """Estado de ajuste de la cuña: perfil de presión de asiento a lo largo de x.

    p_fondo(x)   presión que la barra (vía ripple) hace sobre la cuña [Pa],
                 en el equilibrio. 0 = la barra apenas toca.
    juego_fondo(x)  si p = 0, separación entre ripple y cuña [m] (>= 0).
    juego_flanco(x) separación entre flanco y hombro de la cola de milano [m].
    """

    nombre: str
    p_fondo: callable
    juego_fondo: callable = lambda x: 0.0 * x
    juego_flanco: callable = lambda x: 0.0 * x
    nivel: str = ""
    nota: str = ""


# ---------------------------------------------------------------------------
# El modelo completo
# ---------------------------------------------------------------------------


class ModeloCuna:
    def __init__(self, g: Geometria | None = None, mat: Ortotropo | None = None,
                 cont: Contactos | None = None):
        self.g = g or Geometria()
        self.mat = mat or Ortotropo()
        self.cont = cont or Contactos()
        self.m = Malla(self.g)
        self.K, self.M = ensamblar(self.m, self.mat)
        self.S = superficies(self.m)
        fl = [self.S["flanco_der"], self.S["flanco_izq"]]
        self.fl_nod = np.concatenate([s.nodos for s in fl])
        self.fl_A = np.concatenate([s.area for s in fl])
        self.fl_n = np.concatenate([s.normal for s in fl])
        self.fl_x = np.concatenate([s.x for s in fl])
        f = self.S["fondo"]
        self.fo_nod, self.fo_A, self.fo_x = f.nodos, f.area, f.x
        self.C = self.cont.C_hertz()
        # esquinas inferiores (y = 0 de cada flanco) contra la pared vertical
        esq = np.isclose(self.m.X[self.fl_nod, 1], 0.0)
        self.la_nod = self.fl_nod[esq]
        self.la_n = np.zeros((self.la_nod.size, 3))
        self.la_n[:, 2] = np.sign(self.fl_n[esq, 2])
        wx = _pesos_1d(self.g.ne_x, self.g.L)
        self.la_L = np.concatenate([wx, wx])            # largo tributario por nodo

    # ---- estado de precarga ------------------------------------------------
    def cargar_estado(self, est: Estado):
        """Fija interferencias: el ripple precomprimido y el juego de flancos."""
        self.est = est
        c = self.cont
        p = np.maximum(np.asarray(est.p_fondo(self.fo_x), float) * np.ones_like(self.fo_x), 0.0)
        gap = np.asarray(est.juego_fondo(self.fo_x), float) * np.ones_like(self.fo_x)
        if c.ripple:
            # compresión inicial del ripple tal que, con la cuña en su sitio,
            # empuje p. Se recalcula tras el equilibrio para que la presión
            # FINAL sea la pedida (la cuña se mueve un poco al asentarse).
            self.d_rip0 = np.where(p > 0, p / c.k_ripple, -gap)
            self.p_obj = p
        else:
            self.d_rip0 = np.where(p > 0, (p / self.C) ** (2 / 3), -gap)
            self.p_obj = p
        self.d_fl0 = -np.asarray(est.juego_flanco(self.fl_x), float) * np.ones_like(self.fl_x)

    # ---- fuerzas de contacto (vectorizadas) ---------------------------------
    def _uy_fondo(self, u):
        return u[3 * self.fo_nod + 1]

    def fondo_presion(self, u):
        """Presión del ripple (o barra rígida) sobre la cuña, >= 0."""
        d = self.d_rip0 - self._uy_fondo(u)          # compresión del ripple
        if self.cont.ripple:
            # más allá de la compresión de aplastado, la cuña apoya en la barra (Hertz)
            tope = self.C * np.maximum(d - self.cont.d_solido_ripple, 0.0) ** 1.5
            return self.cont.k_ripple * np.maximum(d, 0.0) + tope, d
        return self.C * np.maximum(d, 0.0) ** 1.5, d

    def flanco_penetracion(self, u):
        un = np.einsum("ij,ij->i", u.reshape(-1, 3)[self.fl_nod], self.fl_n)
        return self.d_fl0 + un

    def flanco_presion(self, u):
        d = self.flanco_penetracion(u)
        return self.C * np.maximum(d, 0.0) ** 1.5, d

    def fuerza_contacto_normal(self, u):
        """Fuerza nodal de los contactos normales (sobre la cuña)."""
        f = np.zeros(self.m.n_dof)
        p_f, _ = self.fondo_presion(u)
        np.add.at(f, 3 * self.fo_nod + 1, p_f * self.fo_A)            # empuja +y
        p_l, _ = self.flanco_presion(u)
        F = -(p_l * self.fl_A)[:, None] * self.fl_n                    # hacia adentro
        np.add.at(f, (3 * self.fl_nod[:, None] + np.arange(3)).ravel(), F.ravel())
        return f

    def rigidez_contacto(self, u, tangencial: bool = True, k_reg: float = 0.0):
        """Rigidez tangente de los contactos alrededor de u (para Newton y modos)."""
        c = self.cont
        n_dof = self.m.n_dof
        rows, cols, vals = [], [], []

        def add_block(nod, k_n, k_t, n):
            # k_n n n^T + k_t (I - n n^T) por nodo
            I = np.eye(3)
            nn = n[:, :, None] * n[:, None, :]
            blk = k_n[:, None, None] * nn + k_t[:, None, None] * (I - nn)
            d = 3 * nod[:, None] + np.arange(3)
            rows.append(np.repeat(d, 3, axis=1).ravel())
            cols.append(np.tile(d, (1, 3)).ravel())
            vals.append(blk.ravel())

        # flancos
        p_l, d_l = self.flanco_presion(u)
        kn = np.where(d_l > 0, 1.5 * self.C * np.sqrt(np.maximum(d_l, 0)), 0.0) * self.fl_A
        kt = (c.kappa_t * kn if tangencial else 0 * kn) + k_reg * self.fl_A
        add_block(self.fl_nod, kn, kt, self.fl_n)
        # fondo
        p_f, d_f = self.fondo_presion(u)
        if c.ripple:
            kn = np.where(d_f > 0, c.k_ripple, 0.0) * self.fo_A
            kt = c.kappa_t_ripple * kn if tangencial else 0 * kn
        else:
            kn = np.where(d_f > 0, 1.5 * self.C * np.sqrt(np.maximum(d_f, 0)), 0.0) * self.fo_A
            kt = c.kappa_t * kn if tangencial else 0 * kn
        nf = np.tile([0.0, -1.0, 0.0], (self.fo_nod.size, 1))
        add_block(self.fo_nod, kn, kt, nf)
        return sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                             shape=(n_dof, n_dof)).tocsr()

    # ---- equilibrio estático con precarga -----------------------------------
    def equilibrio(self, tol: float = 1e-9, max_it: int = 60, ajustar_presion: bool = True):
        """Newton sobre K u = f_contacto(u). Devuelve u (y guarda self.u0).

        El ripple impone una compresión; la cuña sube contra los hombros
        hasta que los flancos (Hertz) equilibran. Como la cuña se mueve al
        asentarse, la presión final difiere un poco de la pedida: se
        impone como carga conocida y la interferencia se fija al final.
        """
        k_reg = 1e-6 * self.cont.kn_flanco_1MPa       # sólo para fijar el modo axial libre
        u = np.zeros(self.m.n_dof)
        if not np.any(self.d_rip0 > 0) and not np.any(self.d_fl0 > 0):
            # cuña sin ninguna precarga: nada la empuja, el equilibrio es u = 0
            self.u0, self.it_equilibrio = u, 0
            return u
        # arranque: traslación radial rígida que equilibra las resultantes
        if np.any(self.d_rip0 > 0):
            ny = self.fl_n[:, 1]

            def res(t):
                d = np.maximum(self.d_rip0 - t, 0)
                up = np.sum((self.cont.k_ripple * d if self.cont.ripple else self.C * d ** 1.5) * self.fo_A)
                dl = np.maximum(self.d_fl0 + t * ny, 0)
                return up - np.sum(self.C * dl ** 1.5 * self.fl_A * ny)
            lo, hi = 0.0, float(np.max(self.d_rip0)) + 1e-6
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                lo, hi = (mid, hi) if res(mid) > 0 else (lo, mid)
            u[1::3] = 0.5 * (lo + hi)

        # La presión de asiento pedida se impone como CARGA conocida en los
        # nodos del fondo que la tienen (p_obj > 0); los demás nodos del fondo
        # (sin presión, con o sin juego) siguen con su ley de contacto. Se
        # resuelve un solo Newton y después se fija la interferencia del fondo
        # que da exactamente esa presión en la posición final. (Una versión
        # anterior corregía la interferencia en un lazo exterior que, con el
        # fondo rígido, no llegaba a converger y dejaba la cuña fuera de
        # equilibrio.)
        act = self.p_obj > 0
        dof_fo = 3 * self.fo_nod + 1
        F_obj = np.where(act, self.p_obj * self.fo_A, 0.0)
        d_rip_libre = self.d_rip0.copy()

        def f_eq(u):
            f = self.fuerza_contacto_normal(u)
            p_f, _ = self.fondo_presion(u)
            f[dof_fo] += np.where(act, F_obj - p_f * self.fo_A, 0.0)   # reemplaza la ley por la carga
            return f

        def K_eq(u):
            Kc = self.rigidez_contacto(u, tangencial=False, k_reg=k_reg)
            _, d_f = self.fondo_presion(u)
            if self.cont.ripple:
                kn = np.where(d_f > 0, self.cont.k_ripple, 0.0)
            else:
                kn = np.where(d_f > 0, 1.5 * self.C * np.sqrt(np.maximum(d_f, 0)), 0.0)
            quitar = sp.coo_matrix((-np.where(act, kn * self.fo_A, 0.0), (dof_fo, dof_fo)),
                                   shape=Kc.shape)
            return (self.K + Kc + quitar).tocsc()

        for it in range(max_it):
            r = self.K @ u - f_eq(u)
            du = spla.spsolve(K_eq(u), -r)
            a, r0 = 1.0, np.linalg.norm(r)
            for _ in range(12):                          # búsqueda lineal
                un = u + a * du
                if np.linalg.norm(self.K @ un - f_eq(un)) < r0 or a < 1e-3:
                    break
                a *= 0.5
            u = un
            if np.linalg.norm(a * du) < tol * max(1e-9, np.abs(u).max()) + 1e-15:
                break
        # interferencia del fondo que da la presión pedida en la posición final
        if self.cont.ripple:
            self.d_rip0 = np.where(act, self._uy_fondo(u) + self.p_obj / self.cont.k_ripple, d_rip_libre)
        else:
            self.d_rip0 = np.where(act, self._uy_fondo(u) + (self.p_obj / self.C) ** (2 / 3), d_rip_libre)
        self.vueltas_equilibrio = it + 1
        # control: el equilibrio tiene que cerrar el balance de fuerzas
        r = self.K @ u - self.fuerza_contacto_normal(u)
        ref = max(float(np.abs(self.fuerza_contacto_normal(u)).max()), 1e-12)
        self.residuo_equilibrio = float(np.abs(r).max()) / ref
        if self.residuo_equilibrio > 1e-6:
            raise RuntimeError(f"equilibrio no convergido: residuo relativo {self.residuo_equilibrio:.2e}")
        self.u0 = u
        self.it_equilibrio = it
        return u

    def resumen_equilibrio(self) -> dict:
        u = self.u0
        p_f, _ = self.fondo_presion(u)
        p_l, _ = self.flanco_presion(u)
        F_fondo = float(np.sum(p_f * self.fo_A))
        F_fl = float(np.sum(p_l * self.fl_A))
        return {
            "F_fondo_N": F_fondo,
            "F_flancos_normal_N": F_fl,
            "F_flancos_radial_N": float(np.sum(p_l * self.fl_A * self.fl_n[:, 1])),
            "p_flanco_max_MPa": float(p_l.max() / 1e6),
            "p_fondo_max_MPa": float(p_f.max() / 1e6),
            "frac_flanco_en_contacto": float(np.mean(p_l > 0)),
            "frac_fondo_en_contacto": float(np.mean(p_f > 0)),
            "uy_medio_um": float(u[1::3].mean() * 1e6),
            "residuo_equilibrio": float(getattr(self, "residuo_equilibrio", 0.0)),
            "vueltas_equilibrio": int(getattr(self, "vueltas_equilibrio", 0)),
        }

    # ---- modos linealizados alrededor del equilibrio --------------------------
    def modos(self, n: int = 12, f_shift: float = 50.0):
        """Autovalores de (K + K_contacto(u0)) phi = w^2 M phi, alrededor de la precarga."""
        KT = (self.K + self.rigidez_contacto(self.u0, tangencial=True)).tocsc()
        Md = sp.diags(self.M).tocsc()
        sigma = -(2 * math.pi * f_shift) ** 2       # corrimiento negativo: tolera modos rígidos
        w2, phi = spla.eigsh(KT, k=n, M=Md, sigma=sigma, which="LM")
        o = np.argsort(w2)
        w2, phi = w2[o], phi[:, o]
        f = np.sqrt(np.maximum(w2, 0)) / (2 * math.pi)
        return f, phi

    # ---- integración explícita (golpe y choques) ------------------------------
    def _fuerzas_dinamicas(self, ut, choca_fl, choca_fo):
        """Fuerzas de contacto normales ELÁSTICAS y datos del amortiguamiento de choque.

        La parte disipativa de Hunt-Crossley, F_d = chi * F_e * d(delta)/dt,
        no se suma acá: se integra de forma semi-implícita en la dirección
        normal de cada nodo (ver golpe), porque en un choque fuerte supera lo
        que tolera un paso explícito. Cada grupo devuelve (nodos, normales
        salientes, F_e por nodo, chi por nodo).
        """
        c = self.cont
        chi = c.chi()
        f = np.zeros(self.m.n_dof)
        U = 0.0
        grupos = []
        # flancos
        d_l = self.flanco_penetracion(ut)
        dp = np.maximum(d_l, 0.0)
        p_l = self.C * dp ** 1.5
        Fe = p_l * self.fl_A
        f[(3 * self.fl_nod[:, None] + np.arange(3))] -= Fe[:, None] * self.fl_n
        U += float(np.sum(0.4 * self.C * dp ** 2.5 * self.fl_A))
        grupos.append((self.fl_nod, self.fl_n, Fe, np.where(choca_fl, chi, 0.0)))
        # fondo (ripple elástico + tope de aplastado, o Hertz contra la barra)
        d_f = self.d_rip0 - self._uy_fondo(ut)
        nb = self._n_fondo
        if c.ripple:
            dt_ = np.maximum(d_f - c.d_solido_ripple, 0.0)
            pt = self.C * dt_ ** 1.5
            p_f = c.k_ripple * np.maximum(d_f, 0.0) + pt
            U += float(np.sum((0.5 * c.k_ripple * np.maximum(d_f, 0.0) ** 2 + 0.4 * self.C * dt_ ** 2.5) * self.fo_A))
            grupos.append((self.fo_nod, nb, pt * self.fo_A, np.full(self.fo_nod.size, chi)))
        else:
            dpf = np.maximum(d_f, 0.0)
            p_f = self.C * dpf ** 1.5
            U += float(np.sum(0.4 * self.C * dpf ** 2.5 * self.fo_A))
            grupos.append((self.fo_nod, nb, p_f * self.fo_A, np.where(choca_fo, chi, 0.0)))
        f[3 * self.fo_nod + 1] += p_f * self.fo_A
        # pared lateral (contacto de línea)
        d_a = -c.juego_lateral + np.einsum("ij,ij->i", ut.reshape(-1, 3)[self.la_nod], self.la_n)
        da = np.maximum(d_a, 0.0)
        q_a = c.k_linea * da * self.la_L
        f[(3 * self.la_nod[:, None] + np.arange(3))] -= q_a[:, None] * self.la_n
        U += float(np.sum(0.5 * c.k_linea * da ** 2 * self.la_L))
        grupos.append((self.la_nod, self.la_n, q_a, np.full(self.la_nod.size, chi)))
        return f, p_l, d_l, p_f, d_f, q_a, U, grupos

    def paso_estable(self, p_diseno: float = 50e6, cfl: float = 0.7, beta: float = 0.0) -> float:
        """Paso de tiempo estable con TODOS los contactos cerrados y cargados a p_diseno.

        La versión anterior usaba la rigidez de contacto de la precarga, que
        en una cuña floja vale casi cero: un choque fuerte podía volver
        inestable la integración. Acá se usa la rigidez que tendrían los
        contactos a una presión de diseño alta, y el integrador avisa si en
        algún momento la presión real la supera.
        """
        c = self.cont
        kn_p = 1.5 * self.C ** (2 / 3) * p_diseno ** (1 / 3)        # por área
        n_dof = self.m.n_dof
        rows, cols, vals = [], [], []

        def add(nod, kn, kt, n):
            I = np.eye(3)
            nn = n[:, :, None] * n[:, None, :]
            blk = kn[:, None, None] * nn + kt[:, None, None] * (I - nn)
            d = 3 * nod[:, None] + np.arange(3)
            rows.append(np.repeat(d, 3, axis=1).ravel())
            cols.append(np.tile(d, (1, 3)).ravel())
            vals.append(blk.ravel())
        kn = kn_p * self.fl_A
        add(self.fl_nod, kn, c.kappa_t * kn, self.fl_n)
        kb = (c.k_ripple + kn_p) * self.fo_A if c.ripple else kn_p * self.fo_A
        add(self.fo_nod, kb, c.kappa_t * kb, np.tile([0.0, -1.0, 0.0], (self.fo_nod.size, 1)))
        add(self.la_nod, c.k_linea * self.la_L, 0 * self.la_L, self.la_n)
        Kc = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                           shape=(n_dof, n_dof)).tocsr()
        Kmax = self.K + Kc
        Minv = 1.0 / self.M
        x = np.random.default_rng(0).standard_normal(n_dof)
        for _ in range(80):
            x = Minv * (Kmax @ x)
            lam = np.linalg.norm(x)
            x /= lam
        w_max = math.sqrt(lam * 1.05)
        xi = beta * w_max / 2
        return cfl * 2 / w_max * (math.sqrt(1 + xi ** 2) - xi)

    def golpe(self, x_golpe: float, z_golpe: float = 0.0, energia: float = 5e-3,
              m_imp: float = 3e-3, R_punta: float = 3e-3, t_fin: float = 3e-3,
              zeta: tuple = (0.01, 2e3, 30e3), x_palp: float | None = None,
              frames_t: np.ndarray | None = None, nodos_vis: np.ndarray | None = None,
              E_punta: float = 210e9, nu_punta: float = 0.29,
              E_cuna_hertz: float = 20e9, nu_cuna_hertz: float = 0.20,
              v_cuna0: np.ndarray | None = None, p_diseno: float = 50e6,
              chi_punta: float = 0.0, x_palps: list | None = None,
              cfl: float = 0.7, verbose: bool = False) -> dict:
        """Golpe del impactador, o choque libre de la cuña: dinámica no lineal completa.

        Ecuación de movimiento (u medido desde el equilibrio con precarga u0):

            M a + C v + K (u0 + u) = f_c(u0+u, v, historia) + f_golpe - r0
            m_imp s'' = -F_H,   F_H = K_H <s + u_y,parche>^(3/2) (1 + chi_punta * d(pen)/dt)_+

        chi_punta es la pérdida local bajo la punta (viscoelasticidad y daño
        de la matriz del G11). Se calibra con la dureza Leeb medida (ver
        cuna3d/leeb.py); con 0 el contacto de la punta es elástico.

        f_c reúne flancos (Hertz + Hunt-Crossley + Coulomb), fondo (ripple
        con tope de aplastado, o Hertz), y pared lateral. r0 es el residuo
        del equilibrio estático, para que el reposo sea exactamente reposo.
        Con energia = 0 no hay impactador y la cuña arranca con v_cuna0.

        Balance de energía, que se verifica en cada corrida:

            E_entrada = T_cuna + U_elastica + U_contactos + T_imp + U_Hertz
                        + D_Rayleigh + D_Hunt-Crossley + D_rozamiento
        """
        m = self.m
        c = self.cont
        con_imp = energia > 0
        Est = 1 / ((1 - nu_punta ** 2) / E_punta + (1 - nu_cuna_hertz ** 2) / E_cuna_hertz)
        K_H = 4 / 3 * Est * math.sqrt(R_punta)
        v0 = math.sqrt(2 * energia / m_imp) if con_imp else 0.0
        # parche de golpe: las caras superiores que tocan el nodo golpeado
        ixg = int(round(x_golpe / self.g.L * (m.nx - 1)))
        izg = int(round((z_golpe / self.g.b + 0.5) * (m.nz - 1)))
        wpatch = np.zeros(m.n_nodos)
        for ex in ((ixg // 2 - 1, ixg // 2) if ixg % 2 == 0 else (ixg // 2,)):
            for ez in ((izg // 2 - 1, izg // 2) if izg % 2 == 0 else (izg // 2,)):
                if 0 <= ex < self.g.ne_x and 0 <= ez < self.g.ne_z:
                    for a in range(3):
                        for cc in range(3):
                            wpatch[m.nodo(2 * ex + a, m.ny - 1, 2 * ez + cc)] += W_GLL[a] * W_GLL[cc]
        pn = np.nonzero(wpatch)[0]
        pw = wpatch[pn] / wpatch[pn].sum()
        pdof = 3 * pn + 1
        x_palp = x_golpe + 10e-3 if x_palp is None else x_palp
        n_palp = int(m.nodo(int(round(x_palp / self.g.L * (m.nx - 1))), m.ny - 1, izg))
        # puntos extra de la cara superior (barrido de distancia del palpador)
        x_palps = [] if x_palps is None else list(x_palps)
        n_palps = np.array([int(m.nodo(int(round(xp / self.g.L * (m.nx - 1))), m.ny - 1, izg)) for xp in x_palps], int)
        x_palps_real = (n_palps // (m.ny * m.nz)) * self.g.L / (m.nx - 1) if n_palps.size else np.array([])
        # Rayleigh
        z0, f1, f2 = zeta
        w1, w2 = 2 * math.pi * f1, 2 * math.pi * f2
        alfa = 2 * z0 * w1 * w2 / (w1 + w2)
        beta = 2 * z0 / (w1 + w2)
        dt = self.paso_estable(p_diseno, cfl, beta)
        n_pasos = int(math.ceil(t_fin / dt))
        # estado
        u0 = self.u0
        u = np.zeros(m.n_dof)
        v = np.zeros(m.n_dof) if v_cuna0 is None else np.asarray(v_cuna0, float).copy()
        s, sd = (0.0, v0) if con_imp else (-1.0, 0.0)
        self._n_fondo = np.tile([0.0, -1.0, 0.0], (self.fo_nod.size, 1))
        # chocan (llevan Hunt-Crossley) los contactos sin presión en reposo
        choca_fl = self.flanco_presion(u0)[0] <= 0.0
        choca_fo = self.fondo_presion(u0)[0] <= 0.0
        f0c, *_ = self._fuerzas_dinamicas(u0, choca_fl, choca_fo)
        r0 = self.K @ u0 - f0c                                 # residuo del equilibrio (~0)
        U_ref = None
        qf = np.zeros((self.fl_nod.size, 3))
        qb = np.zeros((self.fo_nod.size, 3))
        fl_dofs = (3 * self.fl_nod[:, None] + np.arange(3))
        fo_dofs = (3 * self.fo_nod[:, None] + np.arange(3))
        u_prev_fl = np.zeros((self.fl_nod.size, 3))
        u_prev_fo = np.zeros((self.fo_nod.size, 3))
        frames_t = np.array([]) if frames_t is None else np.asarray(frames_t)
        nodos_vis = np.array([], int) if nodos_vis is None else np.asarray(nodos_vis)
        fr_u, fr_pf, fr_pb, fr_t = [], [], [], []
        k_frame = 0
        rec_every = max(1, int(round(0.5e-6 / dt)))
        claves = ("t", "F_H", "s", "uy_golpe", "uy_palp", "vy_palp", "ay_palp", "F_flancos", "F_fondo",
                  "F_lateral", "frac_fl_abierto", "frac_fo_abierto", "E_cin_cuna", "E_balance")
        hist = {k: [] for k in claves}
        hist["uy_palps"], hist["vy_palps"] = [], []
        D_ray = D_hc = D_roz = D_tip = 0.0
        p_max = 0.0
        E_in = 0.5 * m_imp * v0 ** 2 + 0.5 * float(np.sum(self.M * v * v))
        for n in range(n_pasos + 1):
            t = n * dt
            ut = u0 + u
            fK = self.K @ ut
            fc, p_l, d_l, p_f, d_f, q_a, U_c, grupos = self._fuerzas_dinamicas(ut, choca_fl, choca_fo)
            Kv = self.K @ v
            f = -fK - beta * Kv - alfa * self.M * v + fc + r0
            # rozamiento con adherencia elástica (Coulomb + Mindlin), flancos
            ul = u[fl_dofs]
            du = ul - u_prev_fl
            du_t = du - np.einsum("ij,ij->i", du, self.fl_n)[:, None] * self.fl_n
            kn_l = 1.5 * self.C * np.sqrt(np.maximum(d_l, 0)) * self.fl_A
            kt_l = c.kappa_t * kn_l
            qtr = qf + kt_l[:, None] * du_t
            qtr -= np.einsum("ij,ij->i", qtr, self.fl_n)[:, None] * self.fl_n
            lim = c.mu * p_l * self.fl_A
            nq = np.linalg.norm(qtr, axis=1)
            esc = np.where(nq > lim, lim / np.maximum(nq, 1e-30), 1.0)
            qnew = qtr * esc[:, None]
            slip = qtr - qnew                                   # parte que excede el cono
            ok = kt_l > 0
            D_roz += float(np.sum(np.einsum("ij,ij->i", slip[ok], qnew[ok]) / kt_l[ok]))
            qf = qnew
            u_prev_fl = ul
            f[fl_dofs] -= qf
            # rozamiento en el fondo
            ub = u[fo_dofs]
            dub = ub - u_prev_fo
            dub[:, 1] = 0.0
            if c.ripple:
                kn_b = np.where(d_f > 0, c.k_ripple, 0.0) * self.fo_A
                kt_b, mu_b = c.kappa_t_ripple * kn_b, c.mu_ripple
            else:
                kn_b = 1.5 * self.C * np.sqrt(np.maximum(d_f, 0)) * self.fo_A
                kt_b, mu_b = c.kappa_t * kn_b, c.mu
            qtr = qb + kt_b[:, None] * dub
            qtr[:, 1] = 0.0
            lim = mu_b * p_f * self.fo_A
            nq = np.linalg.norm(qtr, axis=1)
            esc = np.where(nq > lim, lim / np.maximum(nq, 1e-30), 1.0)
            qnew = qtr * esc[:, None]
            okb = kt_b > 0
            D_roz += float(np.sum(np.einsum("ij,ij->i", (qtr - qnew)[okb], qnew[okb]) / kt_b[okb]))
            qb = qnew
            u_prev_fo = ub
            f[fo_dofs] -= qb
            # golpe (Hertz de la punta)
            uy_p = float(np.dot(pw, u[pdof]))
            pen = s + uy_p
            if con_imp and pen > 0:
                F_He = K_H * pen ** 1.5
                pen_d = sd + float(np.dot(pw, v[pdof]))
                F_H = max(0.0, F_He * (1 + chi_punta * pen_d))
                D_tip += dt * (F_H - F_He) * pen_d
            else:
                F_H = 0.0
            f[pdof] -= F_H * pw
            a = f / self.M
            p_max = max(p_max, float(p_l.max()))
            # energía (con v en el paso entero, promedio de los medios pasos)
            if n % rec_every == 0 or n == n_pasos:
                U_el = 0.5 * float(ut @ fK) - float(r0 @ u)
                U_t = float(np.sum(np.einsum("ij,ij->i", qf[ok], qf[ok]) / (2 * kt_l[ok])))
                if U_ref is None:
                    U_ref = U_el + U_c
                T = 0.5 * float(np.sum(self.M * v * v))
                E_tot = (T + (U_el + U_c - U_ref) + U_t + 0.5 * m_imp * sd ** 2
                         + (0.4 * K_H * pen ** 2.5 if pen > 0 and con_imp else 0.0) + D_ray + D_hc + D_roz + D_tip)
            if n % rec_every == 0:
                hist["t"].append(t)
                hist["F_H"].append(F_H)
                hist["s"].append(s)
                hist["uy_golpe"].append(uy_p)
                hist["uy_palp"].append(u[3 * n_palp + 1])
                hist["vy_palp"].append(v[3 * n_palp + 1])
                hist["ay_palp"].append(a[3 * n_palp + 1])
                if n_palps.size:
                    hist["uy_palps"].append(u[3 * n_palps + 1].copy())
                    hist["vy_palps"].append(v[3 * n_palps + 1].copy())
                hist["F_flancos"].append(float(np.sum(p_l * self.fl_A)))
                hist["F_fondo"].append(float(np.sum(p_f * self.fo_A)))
                hist["F_lateral"].append(float(np.sum(q_a)))
                hist["frac_fl_abierto"].append(float(np.mean(p_l <= 0)))
                hist["frac_fo_abierto"].append(float(np.mean(p_f <= 0)))
                hist["E_cin_cuna"].append(T)
                hist["E_balance"].append(E_tot)
            while k_frame < frames_t.size and t >= frames_t[k_frame]:
                fr_u.append(u.reshape(-1, 3)[nodos_vis].copy())
                fr_pf.append(p_l.copy())
                fr_pb.append(p_f.copy())
                fr_t.append(t)
                k_frame += 1
            # disipación de Rayleigh del paso (con v del medio paso)
            D_ray += dt * float(alfa * np.sum(self.M * v * v) + beta * (v @ Kv))
            # avance (leapfrog; v en medio paso)
            h = dt if n > 0 else 0.5 * dt
            v_old = v.copy()
            v += h * a
            # Hunt-Crossley semi-implícito en la normal de cada nodo en contacto:
            #   v_n+ = v_n* - (h c / m) (v_n- + v_n+)/2,   c = chi F_e
            # con la condición de que el contacto no tire: F_e + F_d >= 0
            for nod, nrm, Fe, chi_n in grupos:
                act = (Fe > 0) & (chi_n > 0)
                if not np.any(act):
                    continue
                nd, nr, F, cc = nod[act], nrm[act], Fe[act], chi_n[act] * Fe[act]
                mi = self.M[3 * nd]
                d3 = 3 * nd[:, None] + np.arange(3)
                vn_old = np.einsum("ij,ij->i", v_old[d3], nr)
                vn_tr = np.einsum("ij,ij->i", v[d3], nr)
                g = h * cc / (2 * mi)
                vn_new = (vn_tr - g * vn_old) / (1 + g)
                Fd = cc * 0.5 * (vn_old + vn_new)
                tira = F + Fd < 0
                Fd = np.where(tira, -F, Fd)
                vn_new = np.where(tira, vn_tr + h * F / mi, vn_new)
                v[d3] += (vn_new - vn_tr)[:, None] * nr
                D_hc += dt * float(np.sum(Fd * 0.5 * (vn_old + vn_new)))
            u += dt * v
            sd += -h * F_H / m_imp
            s += dt * sd
            if verbose and n % 5000 == 0:
                print(f"  paso {n}/{n_pasos}  t={t*1e6:.0f} us  F_H={F_H:.1f} N")
        H = {k: np.asarray(vv) for k, vv in hist.items()}
        E_cuna = 0.5 * float(np.sum(self.M * v * v)) + (U_el + U_c - U_ref) + U_t
        v_reb = -sd if (con_imp and sd < 0) else 0.0
        sep = H["F_H"] > 0
        t_c = float(H["t"][sep][-1] - H["t"][sep][0]) if sep.any() else 0.0
        err_E = float(np.max(np.abs(H["E_balance"] - E_in))) / max(E_in, 1e-30)
        return {
            "dt": dt, "n_pasos": n_pasos, "K_H": K_H, "v0": v0,
            "hist": H, "v_rebote": v_reb,
            "E_entrada_mJ": E_in * 1e3,
            "E_rebote_mJ": 0.5 * m_imp * v_reb ** 2 * 1e3,
            "E_transmitida_mJ": 0.5 * m_imp * (v0 ** 2 - v_reb ** 2) * 1e3,
            "E_rozamiento_mJ": D_roz * 1e3, "E_choques_mJ": D_hc * 1e3, "E_rayleigh_mJ": D_ray * 1e3,
            "E_punta_mJ": D_tip * 1e3, "restitucion": v_reb / v0 if con_imp else 0.0,
            "E_cuna_final_mJ": E_cuna * 1e3,
            "error_balance_energia": err_E,
            "p_flanco_max_MPa": p_max / 1e6, "p_diseno_MPa": p_diseno / 1e6,
            "F_H_max": float(H["F_H"].max()), "t_contacto_us": t_c * 1e6,
            "F_lateral_max": float(H["F_lateral"].max()),
            "golpe_rebota_aun": bool(con_imp and sd > 0),
            "frames": {"t": np.asarray(fr_t), "u": np.asarray(fr_u),
                       "p_flanco": np.asarray(fr_pf), "p_fondo": np.asarray(fr_pb)},
            "nodo_palp": n_palp, "parche_nodos": pn, "parche_pesos": pw,
            "x_palps": x_palps_real,
            "rayleigh": {"alfa": alfa, "beta": beta},
            "v_final": v.copy(), "u_final": u.copy(),
        }
