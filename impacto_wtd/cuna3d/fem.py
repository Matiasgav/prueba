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
            return self.cont.k_ripple * np.maximum(d, 0.0), d
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
        corrige la compresión inicial del ripple y se repite (2-3 vueltas).
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
        for vuelta in range(4 if ajustar_presion else 1):
            for it in range(max_it):
                r = self.K @ u - self.fuerza_contacto_normal(u)
                r[0::3] += 0.0
                KT = self.K + self.rigidez_contacto(u, tangencial=False, k_reg=k_reg)
                du = spla.spsolve(KT.tocsc(), -r)
                # búsqueda lineal simple sobre la norma del residuo
                a, r0 = 1.0, np.linalg.norm(r)
                for _ in range(12):
                    un = u + a * du
                    rn = self.K @ un - self.fuerza_contacto_normal(un)
                    if np.linalg.norm(rn) < r0 or a < 1e-3:
                        break
                    a *= 0.5
                u = un
                if np.linalg.norm(a * du) < tol * max(1e-9, np.abs(u).max()) + 1e-15:
                    break
            if not ajustar_presion or not np.any(self.p_obj > 0):
                break
            p_now, _ = self.fondo_presion(u)
            act = self.p_obj > 0
            err = np.max(np.abs(p_now[act] - self.p_obj[act])) / np.max(self.p_obj)
            if err < 2e-3:
                break
            # corregir la compresión inicial para que la presión final sea la pedida
            if self.cont.ripple:
                self.d_rip0 = np.where(act, self._uy_fondo(u) + self.p_obj / self.cont.k_ripple, self.d_rip0)
            else:
                self.d_rip0 = np.where(act, self._uy_fondo(u) + (self.p_obj / self.C) ** (2 / 3), self.d_rip0)
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

    # ---- integración explícita del golpe --------------------------------------
    def golpe(self, x_golpe: float, z_golpe: float = 0.0, energia: float = 5e-3,
              m_imp: float = 3e-3, R_punta: float = 3e-3, t_fin: float = 3e-3,
              zeta: tuple = (0.01, 2e3, 30e3), x_palp: float | None = None,
              frames_t: np.ndarray | None = None, nodos_vis: np.ndarray | None = None,
              E_punta: float = 210e9, nu_punta: float = 0.29,
              E_cuna_hertz: float = 20e9, nu_cuna_hertz: float = 0.20,
              cfl: float = 0.7, verbose: bool = False) -> dict:
        """Golpe del impactador: dinámica no lineal completa, diferencia central.

        Ecuación de movimiento (u medido desde el equilibrio con precarga u0):

            M a + C v + K (u0 + u) = f_fondo(u0+u) + f_flancos(u0+u, historia)
                                     + f_golpe(u0+u, s)
            m_imp s'' = -F_H,   F_H = K_H max(0, s + u_y,parche)^(3/2)

        con s el avance de la punta (positivo hacia la cuña, -y).
        Amortiguamiento de Rayleigh C = alfa M + beta K con zeta dado a dos
        frecuencias. El rozamiento en los flancos disipa por su cuenta.
        """
        m = self.m
        c = self.cont
        # --- Hertz de la punta
        Est = 1 / ((1 - nu_punta ** 2) / E_punta + (1 - nu_cuna_hertz ** 2) / E_cuna_hertz)
        K_H = 4 / 3 * Est * math.sqrt(R_punta)
        v0 = math.sqrt(2 * energia / m_imp)
        # --- parche de golpe: las caras superiores que tocan el nodo golpeado
        T = self.S["tapa"]
        ixg = int(round(x_golpe / self.g.L * (m.nx - 1)))
        izg = int(round((z_golpe / self.g.b + 0.5) * (m.nz - 1)))
        wpatch = np.zeros(m.n_nodos)
        for ex in (ixg // 2 - 1, ixg // 2) if ixg % 2 == 0 else (ixg // 2,):
            for ez in (izg // 2 - 1, izg // 2) if izg % 2 == 0 else (izg // 2,):
                if 0 <= ex < self.g.ne_x and 0 <= ez < self.g.ne_z:
                    for a in range(3):
                        for cc in range(3):
                            wpatch[m.nodo(2 * ex + a, m.ny - 1, 2 * ez + cc)] += W_GLL[a] * W_GLL[cc]
        pn = np.nonzero(wpatch)[0]
        pw = wpatch[pn] / wpatch[pn].sum()
        pdof = 3 * pn + 1
        # --- palpador
        x_palp = x_golpe + 10e-3 if x_palp is None else x_palp
        n_palp = int(m.nodo(int(round(x_palp / self.g.L * (m.nx - 1))), m.ny - 1, izg))
        # --- amortiguamiento de Rayleigh
        z0, f1, f2 = zeta
        w1, w2 = 2 * math.pi * f1, 2 * math.pi * f2
        alfa = 2 * z0 * w1 * w2 / (w1 + w2)
        beta = 2 * z0 / (w1 + w2)
        # --- paso estable: potencia sobre M^-1 (K + K_c) con contactos bien rígidos
        Kc = self.rigidez_contacto(self.u0, tangencial=True)
        Kmax = self.K + 3.0 * Kc
        Minv = 1.0 / self.M
        x = np.random.default_rng(0).standard_normal(m.n_dof)
        for _ in range(60):
            x = Minv * (Kmax @ x)
            lam = np.linalg.norm(x)
            x /= lam
        w_max = math.sqrt(lam * 1.05)
        dt = cfl * 2 / w_max * (math.sqrt(1 + (beta * w_max / 2) ** 2) - beta * w_max / 2)
        n_pasos = int(math.ceil(t_fin / dt))
        # --- estado
        u0 = self.u0
        u = np.zeros(m.n_dof)
        v = np.zeros(m.n_dof)
        s, sd = 0.0, v0
        # rozamiento: fuerza tangencial acumulada por nodo de flanco y fondo
        qf = np.zeros((self.fl_nod.size, 3))
        qb = np.zeros((self.fo_nod.size, 3))
        nb = np.tile([0.0, -1.0, 0.0], (self.fo_nod.size, 1))
        fl_dofs = (3 * self.fl_nod[:, None] + np.arange(3))
        fo_dofs = (3 * self.fo_nod[:, None] + np.arange(3))
        f_eq = self.K @ u0 - self.fuerza_contacto_normal(u0)       # residuo del equilibrio (~0)
        u_prev_fl = np.zeros((self.fl_nod.size, 3))
        u_prev_fo = np.zeros((self.fo_nod.size, 3))

        frames_t = np.array([]) if frames_t is None else np.asarray(frames_t)
        nodos_vis = np.array([], int) if nodos_vis is None else np.asarray(nodos_vis)
        fr_u, fr_pf, fr_pb, fr_t = [], [], [], []
        k_frame = 0
        rec_every = max(1, int(round(0.5e-6 / dt)))
        hist = {k: [] for k in ("t", "F_H", "s", "uy_golpe", "uy_palp", "vy_palp", "ay_palp",
                                "F_flancos", "F_fondo", "frac_fl_abierto", "frac_fo_abierto", "E_cin_cuna")}
        E_disip_roz = 0.0
        a_palp = 0.0
        for n in range(n_pasos + 1):
            t = n * dt
            ut = u0 + u
            # elástico + Rayleigh(beta) en una sola multiplicación
            f = -(self.K @ (u + beta * v)) - alfa * self.M * v - f_eq
            # fondo (normal)
            p_f, d_f = self.fondo_presion(ut)
            p_f0, _ = self.fondo_presion(u0)
            f[3 * self.fo_nod + 1] += (p_f - p_f0) * self.fo_A
            # flancos (normal)
            p_l, d_l = self.flanco_presion(ut)
            p_l0, _ = self.flanco_presion(u0)
            f[fl_dofs] -= ((p_l - p_l0) * self.fl_A)[:, None] * self.fl_n
            # rozamiento con adherencia elástica (Coulomb + Mindlin), flancos
            ul = u[fl_dofs]
            du = ul - u_prev_fl
            du_t = du - np.einsum("ij,ij->i", du, self.fl_n)[:, None] * self.fl_n
            kn_l = 1.5 * self.C * np.sqrt(np.maximum(d_l, 0)) * self.fl_A
            qtr = qf + (c.kappa_t * kn_l)[:, None] * du_t
            qtr -= np.einsum("ij,ij->i", qtr, self.fl_n)[:, None] * self.fl_n
            lim = c.mu * p_l * self.fl_A
            nq = np.linalg.norm(qtr, axis=1)
            esc = np.where(nq > lim, lim / np.maximum(nq, 1e-30), 1.0)
            qnew = qtr * esc[:, None]
            E_disip_roz += float(np.sum((qtr - qnew) * du_t)) if np.any(esc < 1) else 0.0
            qf = qnew
            u_prev_fl = ul
            f[fl_dofs] -= qf
            # rozamiento en el fondo (crestas del ripple)
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
            qb = qtr * esc[:, None]
            u_prev_fo = ub
            f[fo_dofs] -= qb
            # golpe (Hertz de la punta)
            uy_p = float(np.dot(pw, ut[pdof]))
            uy_p0 = float(np.dot(pw, u0[pdof]))
            pen = s + (uy_p - uy_p0)
            F_H = K_H * pen ** 1.5 if pen > 0 else 0.0
            f[pdof] -= F_H * pw
            a = f / self.M
            # registro
            if n % rec_every == 0:
                hist["t"].append(t)
                hist["F_H"].append(F_H)
                hist["s"].append(s)
                hist["uy_golpe"].append(uy_p - uy_p0)
                hist["uy_palp"].append(u[3 * n_palp + 1])
                hist["vy_palp"].append(v[3 * n_palp + 1])
                hist["ay_palp"].append(a[3 * n_palp + 1])
                hist["F_flancos"].append(float(np.sum(p_l * self.fl_A)))
                hist["F_fondo"].append(float(np.sum(p_f * self.fo_A)))
                hist["frac_fl_abierto"].append(float(np.mean(p_l <= 0)))
                hist["frac_fo_abierto"].append(float(np.mean(p_f <= 0)))
                hist["E_cin_cuna"].append(float(0.5 * np.sum(self.M * v * v)))
            while k_frame < frames_t.size and t >= frames_t[k_frame]:
                fr_u.append(u.reshape(-1, 3)[nodos_vis].copy())
                fr_pf.append(p_l.copy())
                fr_pb.append(p_f.copy())
                fr_t.append(t)
                k_frame += 1
            # avance (leapfrog; v en medio paso)
            v += dt * a if n > 0 else 0.5 * dt * a
            u += dt * v
            sd += -dt * F_H / m_imp if n > 0 else -0.5 * dt * F_H / m_imp
            s += dt * sd
            if verbose and n % 5000 == 0:
                print(f"  paso {n}/{n_pasos}  t={t*1e6:.0f} us  F_H={F_H:.1f} N")
        H = {k: np.asarray(vv) for k, vv in hist.items()}
        # energía mecánica que queda en la cuña (cinética + elástica, desde el equilibrio)
        E_cuna = 0.5 * float(np.sum(self.M * v * v)) + 0.5 * float(u @ (self.K @ u))
        # velocidad de rebote: la del impactador una vez separado
        v_reb = -sd if sd < 0 else 0.0
        sep = H["F_H"] > 0
        t_c = float(H["t"][sep][-1] - H["t"][sep][0]) if sep.any() else 0.0
        return {
            "dt": dt, "n_pasos": n_pasos, "K_H": K_H, "v0": v0,
            "hist": H, "v_rebote": v_reb,
            "E_entrada_mJ": 0.5 * m_imp * v0 ** 2 * 1e3,
            "E_rebote_mJ": 0.5 * m_imp * v_reb ** 2 * 1e3,
            "E_transmitida_mJ": 0.5 * m_imp * (v0 ** 2 - v_reb ** 2) * 1e3,
            "E_rozamiento_mJ": E_disip_roz * 1e3,
            "E_cuna_final_mJ": E_cuna * 1e3,
            "F_H_max": float(H["F_H"].max()), "t_contacto_us": t_c * 1e6,
            "golpe_rebota_aun": bool(sd > 0),
            "frames": {"t": np.asarray(fr_t), "u": np.asarray(fr_u),
                       "p_flanco": np.asarray(fr_pf), "p_fondo": np.asarray(fr_pb)},
            "nodo_palp": n_palp, "parche_nodos": pn, "parche_pesos": pw,
            "rayleigh": {"alfa": alfa, "beta": beta},
        }
