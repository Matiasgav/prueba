#!/usr/bin/env python3
"""FEA 3D del extremo del eslabón (STEP 02489-00-M40000, mitad M40003, articulación izquierda).

Carga: las 3 arandelas B (0,5 mm) empujan las paredes del alojamiento con las fuerzas de
contacto del FEA 2D real (B_real), 1 N·m por arandela. Al 7075-T6: E = 71,7 GPa, ν = 0,33.
Apoyos: caras de corte (y = 70 y x = −7) empotradas.
"""
import json, sys
import numpy as np
import gmsh
from scipy.spatial import cKDTree
import scipy.sparse.linalg as spla
from skfem import MeshTet, Basis, FacetBasis, ElementVector, ElementTetP2, ElementTetP1, asm, condense, solve
from skfem.models.elasticity import linear_elasticity, lame_parameters
from skfem import LinearForm

STEP = sys.argv[1]
C = np.array([-15.288, -110.875])            # centro de la articulación (x, z)
BANDAS = [(80.75, 81.25), (82.25, 82.75), (83.75, 84.25)][:int(sys.argv[5]) if len(sys.argv) > 5 else 3]
H_FINO, H_GRUESO = float(sys.argv[2]) if len(sys.argv) > 2 else 0.22, 1.2

gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
gmsh.model.occ.importShapes(STEP); gmsh.model.occ.synchronize()
vol = [t for d, t in gmsh.model.getEntities(3) if gmsh.model.getEntityName(3, t).endswith("M40003")
       and gmsh.model.getBoundingBox(3, t)[0] < -20][0]
others = [(3, t) for d, t in gmsh.model.getEntities(3) if t != vol]
gmsh.model.occ.remove(others, recursive=True)
box = gmsh.model.occ.addBox(-22.5, 70, -118.5, 15.5, 14.3, 15)
res_i, _ = gmsh.model.occ.intersect([(3, vol)], [(3, box)])
VAR = (sys.argv[3] if len(sys.argv) > 3 else "real") + (f"_{sys.argv[5]}B" if len(sys.argv) > 5 else "")
extra = []
if "pared2" in VAR:      # paredes de 1 -> 2 mm (engrosadas hacia afuera)
    extra += [gmsh.model.occ.addBox(-19.67, 79.75, -104.45, 7.9, 4.5, 1.075),
              gmsh.model.occ.addBox(-19.67, 79.75, -118.375, 7.9, 4.5, 1.075)]
if "puente" in VAR:      # cierre del lado abierto con puentes de 0,5 mm a la altura de cada B
    for a, bb in BANDAS:
        extra.append(gmsh.model.occ.addBox(C[0] - 7.0, a, C[1] - 6.5, 0.95, bb - a, 13.0))
        # unión puente-pared: rellenar entre el canto libre (x=-19.67) y el puente
        extra.append(gmsh.model.occ.addBox(C[0] - 7.0, a, C[1] - 6.5, 2.85, bb - a, 1.05))
        extra.append(gmsh.model.occ.addBox(C[0] - 7.0, a, C[1] + 5.45, 2.85, bb - a, 1.05))
if extra:
    out_f, _ = gmsh.model.occ.fuse(res_i, [(3, e) for e in extra])
    print("volúmenes tras fusionar:", out_f, flush=True)
gmsh.model.occ.synchronize()
f = gmsh.model.mesh.field
b = f.add("Box"); f.setNumber(b, "VIn", H_FINO); f.setNumber(b, "VOut", H_GRUESO)
for k, v in dict(XMin=-21.5, XMax=-8.8, YMin=78.8, YMax=84.5, ZMin=-118, ZMax=-104, Thickness=2).items():
    f.setNumber(b, k, v)
f.setAsBackgroundMesh(b)
for o in ("Mesh.MeshSizeExtendFromBoundary", "Mesh.MeshSizeFromPoints", "Mesh.MeshSizeFromCurvature"):
    gmsh.option.setNumber(o, 0)
gmsh.model.mesh.generate(3)
nt, xyz, _ = gmsh.model.mesh.getNodes()
et, etags, enodes = gmsh.model.mesh.getElements(3)
gmsh.finalize()
idx = {t: i for i, t in enumerate(nt)}
P = xyz.reshape(-1, 3).T
T = np.vectorize(idx.get)(enodes[0].reshape(-1, 4)).T
used = np.unique(T); remap = -np.ones(P.shape[1], int); remap[used] = np.arange(len(used))
mesh = MeshTet(P[:, used], remap[T])
print("tetras", mesh.t.shape[1], flush=True)

E, NU = 71.7e3, 0.33
ib = Basis(mesh, ElementVector(ElementTetP2()))
K = asm(linear_elasticity(*lame_parameters(E, NU)), ib)
print("gdl", K.shape[0], flush=True)

# ---- carga: fuerzas de contacto de B sobre la pared
B = json.load(open("resultados_real_1Nm.json"))["B_real"]["contacto"]
B = np.array(B)                                       # x, z, f, mx, mz  (local)
B = B[B[:, 2] > 1e-6]
src = B[:, :2]; fvec = -B[:, 2:3] * B[:, 3:5]         # fuerza sobre la pared, dirección -m
SIG = float(sys.argv[4]) if len(sys.argv) > 4 else 0.4
tree = cKDTree(src)

def traccion(xg, yg, zg):
    loc = np.c_[(xg - C[0]).ravel(), (zg - C[1]).ravel()]
    yy = yg.ravel()
    banda = np.zeros_like(yy, bool)
    for a, bb in BANDAS:
        banda |= (yy >= a) & (yy <= bb)
    tx = np.zeros_like(yy); tz = np.zeros_like(yy)
    near = tree.query_ball_point(loc, 4 * SIG)
    for k, lst in enumerate(near):
        if not banda[k] or not lst: continue
        d = np.linalg.norm(src[lst] - loc[k], axis=1)
        w = np.exp(-0.5 * (d / SIG) ** 2) / (SIG * np.sqrt(2 * np.pi))
        tx[k] = (w * fvec[lst, 0]).sum() / 0.5; tz[k] = (w * fvec[lst, 1]).sum() / 0.5
    return tx.reshape(xg.shape), tz.reshape(xg.shape)

bf = mesh.boundary_facets()
mid = mesh.p[:, mesh.facets[:, bf]].mean(axis=1)
loc = np.c_[mid[0] - C[0], mid[2] - C[1]]
d, _ = tree.query(loc)
cargadas = bf[(d < 0.12) & (mid[1] > 80.5)]
fb = FacetBasis(mesh, ElementVector(ElementTetP2()), facets=cargadas)

@LinearForm
def carga(v, w):
    x, y, z = w.x
    tx, tz = traccion(x, y, z)
    return tx * v[0] + tz * v[2]
fload = asm(carga, fb)
Ftot = np.array([fload[ib.nodal_dofs[i]].sum() + fload[ib.edge_dofs[i]].sum() for i in range(3)])
X = ib.doflocs
comp = np.zeros(len(fload), int); comp[ib.nodal_dofs[1]] = 1; comp[ib.edge_dofs[1]] = 1
comp[ib.nodal_dofs[2]] = 2; comp[ib.edge_dofs[2]] = 2
Mz = np.sum(np.where(comp == 0, (X[2] - C[1]) * fload, 0) - np.where(comp == 2, (X[0] - C[0]) * fload, 0))
print("momento aplicado sobre la pared (3 arandelas) N·mm:", round(float(Mz), 1), "-> normalizado a 1000 por banda", flush=True)
fload *= 1000.0 * len(BANDAS) / abs(Mz)
print("fuerza neta aplicada", Ftot.round(2), " suma |f| esperada por banda", round(np.abs(B[:, 2]).sum(), 1), flush=True)

fix = mesh.facets_satisfying(lambda x: (np.abs(x[1] - 70) < 1e-6) | (np.abs(x[0] + 7) < 1e-6))
D = ib.get_dofs(fix).all()
Kc, fc, _, I = condense(K, fload, D=D)
import pyamg
ml = pyamg.smoothed_aggregation_solver(Kc.tocsr(), B=None)
uI, info = spla.cg(Kc, fc, rtol=1e-9, maxiter=4000, M=ml.aspreconditioner())
print("cg info", info, flush=True)
u = np.zeros(K.shape[0]); u[I] = uI

# von Mises nodal (proyección P1)
pb = ib.with_element(ElementTetP1())
G = ib.interpolate(u).grad
lam, mu = lame_parameters(E, NU)
eps = 0.5 * (G + np.transpose(G, (1, 0, 2, 3)))
tr = eps[0, 0] + eps[1, 1] + eps[2, 2]
s = 2 * mu * eps
for i in range(3): s[i, i] = s[i, i] + lam * tr
vm = np.sqrt(0.5 * ((s[0, 0] - s[1, 1]) ** 2 + (s[1, 1] - s[2, 2]) ** 2 + (s[2, 2] - s[0, 0]) ** 2)
             + 3 * (s[0, 1] ** 2 + s[1, 2] ** 2 + s[0, 2] ** 2))
vmn = pb.project(vm)
tr3 = cKDTree(mesh.p.T)
vma = np.array([vmn[l].mean() for l in tr3.query_ball_point(mesh.p.T, 0.15)])
i = int(np.argmax(vma))
ux = u[ib.nodal_dofs[0]]; uy = u[ib.nodal_dofs[1]]; uz = u[ib.nodal_dofs[2]]
umag = np.sqrt(ux**2 + uy**2 + uz**2)
lp = np.array([[x0 + C[0], 0, z0 + C[1]] for x0, z0 in src])
yb = np.concatenate([np.linspace(a, bb, 3) for a, bb in BANDAS])
LP = np.array([[q[0], y, q[2]] for q in lp for y in yb])
dl, _ = cKDTree(LP).query(mesh.p.T)
lejos = dl > 0.4
res_l = float(vma[lejos].max())
pos_l = mesh.p[:, int(np.argmax(np.where(lejos, vma, 0)))].round(2).tolist()
print("vm lejos de la carga", round(res_l), "en", pos_l, flush=True)
res = dict(vm_lejos_carga_1Nm=res_l, pos_lejos=pos_l, tetras=int(mesh.t.shape[1]), gdl=int(K.shape[0]), vm_pico_1Nm=float(vmn.max()),
           vm_prom_1Nm=float(vma.max()), pos=mesh.p[:, i].round(2).tolist(),
           u_max_um_1Nm=float(umag.max() * 1000), pos_umax=mesh.p[:, int(np.argmax(umag))].round(2).tolist())
print(json.dumps(res), flush=True)
json.dump(res, open(f"resultados_eslabon3d_{VAR}_1Nm.json", "w"), indent=1)
np.savez(f"eslabon3d_{VAR}.npz", p=mesh.p, t=mesh.t, vm=vma, ux=ux, uy=uy, uz=uz)
