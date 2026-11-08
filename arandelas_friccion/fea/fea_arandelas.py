#!/usr/bin/env python3
"""FEA 2D (tensión plana) de las arandelas de fricción tipo A y B.

Modelo:
- Elementos triangulares cuadráticos (P2), espesor t, inox E=193 GPa, nu=0,29.
- Carga: fricción de las DOS caras de una arandela intermedia, como tracción
  tangencial uniforme sobre la corona apretada por la cabeza (r = 3 a 5 mm).
  Se resuelve para un par de 1 N·m por arandela; el modelo es lineal, así que
  todo escala con el par.
- Apoyos de contacto unilateral (solo compresión, iteración de conjunto activo
  con penalización) contra paredes rígidas:
    A: costado de la oreja dentro del eslabón (largo de encastre e) + vástago Ø6.
    B: caras paralelas de 11 mm contra el eslabón + vástago Ø6.
- Criterio: von Mises promediado en un radio de 0,1 mm (filtra las
  singularidades de canto vivo, que en la realidad se asientan localmente).
"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.colors import BoundaryNorm
from meshpy import triangle
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from scipy.spatial import cKDTree
from skfem import (MeshTri, Basis, ElementVector, ElementTriP2, ElementTriP1,
                   BilinearForm, LinearForm, asm)
from skfem.helpers import dot, ddot, sym_grad, trace, eye

E, NU, T = 193e3, 0.29, 0.5        # MPa, -, mm
R_HOLE, R_CLAMP = 3.0, 5.0
H = 0.07                            # tamaño de elemento aprox. [mm]
R_AVG = 0.10                        # radio de promedio del criterio [mm]


# ------------------------------------------------------------------ geometría
def arc(r, a0, a1, n):
    a = np.radians(np.linspace(a0, a1, n))
    return np.c_[r * np.cos(a), r * np.sin(a)]


def contorno_B():
    c = np.cos(np.radians(20)); s = np.sin(np.radians(20))
    xf = (6 - 5.5 * s) / c                     # 4.38: fin de la cara de 11 mm
    der = np.vstack([arc(6, -20, 20, 25), [[xf, 5.5]]])
    pts = np.vstack([der, [[-xf, 5.5]], -der, [[xf, -5.5]]])
    return pts


def contorno_A(tip):
    c = np.cos(np.radians(20)); s = np.sin(np.radians(20))
    y1 = 4.07
    x1 = (6 - y1 * s) / c                      # recta tangente al R6 a 20°
    sup = arc(6, 0, 20, 12)[1:].tolist() + [[x1, y1], [1.87, 5.31], [0.0, 5.56],
                                           [-1.66, 5.31], [-5.0, 4.07], [-5.5, 2.5],
                                           [-tip, 2.5]]
    sup = np.array(sup)
    inf = sup[::-1] * [1, -1]
    return np.vstack([[[6.0, 0.0]], sup, inf])


def malla(contorno):
    hole = arc(R_HOLE, 0, 360, 121)[:-1]
    # densificar contorno exterior
    pts = []
    for p, q in zip(contorno, np.roll(contorno, -1, axis=0)):
        n = max(1, int(np.ceil(np.linalg.norm(q - p) / H)))
        pts += [p + (q - p) * k / n for k in range(n)]
    pts = np.array(pts)
    n0 = len(pts)
    facets = [(i, (i + 1) % n0) for i in range(n0)]
    facets += [(n0 + i, n0 + (i + 1) % len(hole)) for i in range(len(hole))]
    info = triangle.MeshInfo()
    info.set_points(np.vstack([pts, hole]).tolist())
    info.set_facets(facets)
    info.set_holes([(0.0, 0.0)])
    m = triangle.build(info, max_volume=H**2 * 0.45, min_angle=30)
    return MeshTri(np.array(m.points).T, np.array(m.elements).T)


# ------------------------------------------------------------------ FEM
lam = E * NU / ((1 + NU) * (1 - 2 * NU)); mu = E / (2 * (1 + NU))
lam_ps = 2 * lam * mu / (lam + 2 * mu)


@BilinearForm
def rigidez(u, v, w):
    eps_u, eps_v = sym_grad(u), sym_grad(v)
    sig = 2 * mu * eps_u + lam_ps * eye(trace(eps_u), 2)
    return T * ddot(sig, eps_v)


def resolver(mesh, apoyos, T_Nmm=1000.0):
    """apoyos: lista de (máscara(x,y)->bool, normal(x,y)->(mx,my), etiqueta)."""
    ib = Basis(mesh, ElementVector(ElementTriP2()))
    K = asm(rigidez, ib).tocsr()
    # carga de fricción: q tangencial en la corona r∈[3,5], torque total T_Nmm
    A_c = np.pi * (R_CLAMP**2 - R_HOLE**2)
    r_m = 2 / 3 * (R_CLAMP**3 - R_HOLE**3) / (R_CLAMP**2 - R_HOLE**2)
    q = T_Nmm / (A_c * r_m)                    # N/mm² (ambas caras)

    @LinearForm
    def carga(v, w):
        x, y = w.x
        r = np.sqrt(x**2 + y**2)
        on = (r <= R_CLAMP + 1e-9)
        return on * q * (-y / r * v[0] + x / r * v[1])
    f = asm(carga, ib)

    X = ib.doflocs                              # (2, ndof) posiciones de cada dof
    nod = ib.nodal_dofs                         # vértices
    # puntos de contorno (vértices + medios de arista)
    bdofs = np.unique(ib.get_dofs().flatten())
    xs, ys = X[0, bdofs[0::2]], X[1, bdofs[0::2]]
    dx_dofs, dy_dofs = bdofs[0::2], bdofs[1::2]
    cands = []
    for mask, normal, tag in apoyos:
        sel = mask(xs, ys)
        for i in np.where(sel)[0]:
            m = np.array(normal(xs[i], ys[i]), float); m /= np.linalg.norm(m)
            cands.append((dx_dofs[i], dy_dofs[i], m, tag, xs[i], ys[i]))
    kpen = 1e3 * E * T
    active = np.ones(len(cands), bool)
    eps = sp.identity(K.shape[0], format="csr") * 1e-10 * E * T
    for it in range(60):
        rows, cols, vals = [], [], []
        for a, (ix, iy, m, *_r) in zip(active, cands):
            if not a:
                continue
            idx = [ix, iy]
            for p in range(2):
                for qq in range(2):
                    rows.append(idx[p]); cols.append(idx[qq]); vals.append(kpen * m[p] * m[qq])
        Kp = K + eps + sp.csr_matrix((vals, (rows, cols)), shape=K.shape)
        u = spsolve(Kp.tocsc(), f)
        un = np.array([u[ix] * m[0] + u[iy] * m[1] for ix, iy, m, *_r in cands])
        new = un < 0                         # penetra -> contacto activo
        if np.array_equal(new, active):
            break
        active = new
    fuerzas = np.where(active, -kpen * un, 0.0)  # N, compresión positiva
    # normalizar al par realmente aplicado (la máscara r<=5 se integra por puntos de Gauss)
    xd = X[0]; yd = X[1]
    es_x = np.zeros(len(f), bool); es_x[np.r_[ib.nodal_dofs[0], ib.facet_dofs[0]]] = True
    M_ap = float(np.sum(np.where(es_x, -yd * f, xd * f)))
    esc = T_Nmm / M_ap
    u = u * esc; fuerzas = fuerzas * esc
    # chequeo de equilibrio de reacciones
    Mr = sum(fz * (c[4] * c[2][1] - c[5] * c[2][0]) for c, fz in zip(cands, fuerzas))
    print(f"  par aplicado {M_ap*esc:.1f} N·mm, momento de reacciones {Mr:.1f} N·mm, iter {it}", flush=True)
    return ib, u, cands, fuerzas, q


def von_mises(ib, u, mesh):
    pb = ib.with_element(ElementTriP1())
    du = ib.interpolate(u).grad                 # (2,2,nel,nqp)
    exx, eyy = du[0, 0], du[1, 1]; exy = 0.5 * (du[0, 1] + du[1, 0])
    c = E / (1 - NU**2)
    sxx = c * (exx + NU * eyy); syy = c * (eyy + NU * exx); sxy = 2 * mu * exy
    vm = np.sqrt(sxx**2 - sxx * syy + syy**2 + 3 * sxy**2)
    return pb.project(vm)                       # nodal (P1)


def promedio(mesh, campo, r=R_AVG):
    tree = cKDTree(mesh.p.T)
    vec = tree.query_ball_point(mesh.p.T, r)
    return np.array([campo[v].mean() for v in vec])


# ------------------------------------------------------------------ casos
def caso_A(tip, e):
    x_pared = -tip + e
    ap = [
        (lambda x, y: (np.abs(y + 2.5) < 1e-6) & (x <= x_pared + 1e-6),
         lambda x, y: (0, 1), "oreja"),
        (lambda x, y: np.abs(np.hypot(x, y) - R_HOLE) < 1e-3,
         lambda x, y: (x, y), "vastago"),
    ]
    return contorno_A(tip), ap


def caso_B():
    ap = [
        (lambda x, y: np.abs(y - 5.5) < 1e-6, lambda x, y: (0, -1), "cara_sup"),
        (lambda x, y: np.abs(y + 5.5) < 1e-6, lambda x, y: (0, 1), "cara_inf"),
        (lambda x, y: np.abs(np.hypot(x, y) - R_HOLE) < 1e-3,
         lambda x, y: (x, y), "vastago"),
    ]
    return contorno_B(), ap


def presion_pared(cands, fuerzas, tags, eje):
    """Presión de contacto sobre la pared (N/mm²) promediada en 0,1 mm."""
    pts = [(c[4], c[5], f) for c, f in zip(cands, fuerzas) if c[3] in tags]
    pts = np.array(sorted(pts, key=lambda p: p[eje]))
    s = pts[:, eje]
    F = pts[:, 2]
    # fuerza total, y máximo de fuerza contenida en una ventana de 0,1 mm
    pmax = 0.0
    for x0 in s:
        win = (s >= x0) & (s < x0 + R_AVG)
        pmax = max(pmax, F[win].sum() / (R_AVG * T))
    return F.sum(), pmax


def main(salida):
    casos = {
        "A_oreja_1mm": caso_A(7.5, 1.0),
        "A_oreja_2mm": caso_A(8.5, 2.0),     # oreja alargada a 8,5 (pared en r=6,5)
        "B": caso_B(),
    }
    res = {}
    for nombre, (cont, ap) in casos.items():
        mesh = malla(cont)
        ib, u, cands, fz, q = resolver(mesh, ap)
        vm = von_mises(ib, u, mesh)
        vm_avg = promedio(mesh, vm)
        tags_pared = ["oreja"] if nombre.startswith("A") else ["cara_sup", "cara_inf"]
        eje = 0
        Fw, pw = presion_pared(cands, fz, tags_pared, eje)
        Fsh = sum(f for c, f in zip(cands, fz) if c[3] == "vastago")
        i_max = int(np.argmax(vm_avg))
        res[nombre] = dict(
            elementos=int(mesh.t.shape[1]),
            vm_pico_1Nm=float(vm.max()),
            vm_prom_1Nm=float(vm_avg.max()),
            pos_max=[float(mesh.p[0, i_max]), float(mesh.p[1, i_max])],
            F_pared_1Nm=float(Fw),
            p_pared_1Nm=float(pw),
            F_vastago_1Nm=float(Fsh),
        )
        np.savez(f"{salida}/{nombre}.npz", p=mesh.p, t=mesh.t, vm=vm, vm_avg=vm_avg,
                 u=ib.interpolate(u).value if False else 0)
        # desplazamientos nodales para la deformada
        ux = u[ib.nodal_dofs[0]]; uy = u[ib.nodal_dofs[1]]
        np.savez(f"{salida}/{nombre}.npz", p=mesh.p, t=mesh.t, vm=vm, vm_avg=vm_avg,
                 ux=ux, uy=uy,
                 cx=np.array([c[4] for c in cands]), cy=np.array([c[5] for c in cands]),
                 cf=fz)
        print(nombre, json.dumps(res[nombre]), flush=True)
    with open(f"{salida}/resultados_1Nm.json", "w") as fh:
        json.dump(res, fh, indent=2)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
