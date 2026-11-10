#!/usr/bin/env python3
"""FEA 2D de A y B achicadas para paredes engrosadas hacia adentro en Δ mm.

Alojamiento: caras planas pasan de z = ±5,5 a ±(5,5 − Δ).
B: contorno real recortado a |z| ≤ 5,5 − Δ.
A: contorno real ∩ (disco R = 5,5 − Δ − 0,05  ∪  oreja |z| ≤ 2,5 hacia −x), para poder girar
   dentro del alojamiento sin tocar las caras planas.
Uso: python3 fea_real_delta.py 0.5
"""
import json, sys
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from scipy.spatial import cKDTree
import fea_arandelas as F
import fea_real as R0   # reutiliza normales(); al importarlo no recalcula nada si se protege

D = float(sys.argv[1])
CT = json.load(open("contornos_step.json"))
zf = 5.5 - D
PB = Polygon(CT["B"]).intersection(box(-10, -zf, 10, zf))
PA = Polygon(CT["A"]).intersection(unary_union([Point(0, 0).buffer(zf - 0.05, 256),
                                                box(-9, -2.6, -2.0, 2.6)])).buffer(0.4, 64).buffer(-0.4, 64)  # R0,4 en la raíz de la oreja
def coords(P):
    c = np.array(P.exterior.coords)[:-1]
    # densificar a 0,05 mm
    out = []
    for p, q in zip(c, np.roll(c, -1, 0)):
        n = max(1, int(np.ceil(np.linalg.norm(q - p) / 0.05)))
        out += [p + (q - p) * k / n for k in range(n)]
    return np.array(out)
cA, cB = coords(PA), coords(PB)
json.dump({"A": cA.round(4).tolist(), "B": cB.round(4).tolist()}, open(f"contornos_d{D}.json", "w"))
NB = R0.normales(cB); treeB = cKDTree(cB)

def ap_A():
    return [(lambda x, y: (y < -2.4) & (y > -2.6) & (x <= -6.5 + 1e-6) & (x > -8.05), lambda x, y: (0, 1), "oreja"),
            (lambda x, y: np.abs(np.hypot(x, y) - F.R_HOLE) < 1e-3, lambda x, y: (x, y), "vastago")]
def ap_B():
    def en(x, y):
        d, _ = treeB.query(np.c_[x, y]); return (d < 0.03) & (x >= -4.383) & (np.hypot(x, y) > 3.6)
    def m(x, y):
        _, i = treeB.query([x, y]); return tuple(-NB[i])
    return [(en, m, "bolsillo"),
            (lambda x, y: np.abs(np.hypot(x, y) - F.R_HOLE) < 1e-3, lambda x, y: (x, y), "vastago")]

res = {"delta": D, "r_ext_A": zf - 0.05}
SOLO = sys.argv[2:] or ["A_real", "B_real"]
for nombre, cont, ap in [x for x in (("A_real", cA, ap_A()), ("B_real", cB, ap_B())) if x[0] in SOLO]:
    mesh = F.malla(cont)
    ib, u, cands, fz, q = F.resolver(mesh, ap)
    vm = F.von_mises(ib, u, mesh); vm_avg = F.promedio(mesh, vm)
    c = np.array([[k[4], k[5]] for k in cands]); tags = np.array([k[3] for k in cands])
    act = fz > 1e-3 * fz.max(); d, _ = cKDTree(c[act]).query(mesh.p.T)
    pared = act & (tags != "vastago")
    r = dict(vm_prom_1Nm=float(vm_avg.max()), vm_lejos_1Nm=float(vm_avg[d > 0.3].max()),
             pos_max=mesh.p[:, int(np.argmax(np.where(d > 0.3, vm_avg, 0)))].round(2).tolist(),
             F_pared_total_1Nm=float(fz[pared].sum()))
    r["contacto"] = [[float(c[i, 0]), float(c[i, 1]), float(fz[i]), *map(float, cands[i][2])] for i in np.where(pared)[0]]
    if nombre == "A_real":
        largo = c[pared, 0].max() - c[pared, 0].min()
        r["p_media_1Nm"] = float(fz[pared].sum() / (largo * F.T))
    res[nombre] = r
    np.savez(f"{nombre}_d{D}.npz", p=mesh.p, t=mesh.t, vm_avg=vm_avg)
    print(D, nombre, {k: v for k, v in r.items() if k != "contacto"}, flush=True)
import os
fn = f"resultados_real_d{D}_1Nm.json"
old = json.load(open(fn)) if os.path.exists(fn) else {}
old.update(res); json.dump(old, open(fn, "w"), indent=1)
