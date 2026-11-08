#!/usr/bin/env python3
"""Variante: arandela A con DOS orejas opuestas (encastre 2 mm, punta en 8,5 mm)."""
import json, sys
import numpy as np
from scipy.spatial import cKDTree
import fea_arandelas as F


def contorno_A2(tip):
    sup = np.array([[tip, 2.5], [5.5, 2.5], [5.0, 4.07], [1.87, 5.31], [0.0, 5.56],
                    [-1.66, 5.31], [-5.0, 4.07], [-5.5, 2.5], [-tip, 2.5]])
    inf = sup[::-1] * [1, -1]
    return np.vstack([sup, inf])


def caso_A2(tip=8.5, e=2.0):
    ap = [
        (lambda x, y: (np.abs(y + 2.5) < 1e-6) & (x <= -tip + e + 1e-6), lambda x, y: (0, 1), "oreja"),
        (lambda x, y: (np.abs(y - 2.5) < 1e-6) & (x >= tip - e - 1e-6), lambda x, y: (0, -1), "oreja"),
        (lambda x, y: np.abs(np.hypot(x, y) - F.R_HOLE) < 1e-3, lambda x, y: (x, y), "vastago"),
    ]
    return contorno_A2(tip), ap


mesh = F.malla(caso_A2()[0])
ib, u, cands, fz, q = F.resolver(mesh, caso_A2()[1])
vm = F.von_mises(ib, u, mesh)
vm_avg = F.promedio(mesh, vm)
c = np.array([[k[4], k[5]] for k in cands]); tags = np.array([k[3] for k in cands])
act = fz > 1e-3 * fz.max()
d, _ = cKDTree(c[act]).query(mesh.p.T)
oreja = act & (tags == "oreja")
izq = oreja & (c[:, 0] < 0)
F_izq = fz[izq].sum()
largo = c[izq, 0].max() - c[izq, 0].min()
_, p_loc = F.presion_pared([k for k, m in zip(cands, izq) if m], fz[izq], ["oreja"], 0)
res = dict(elementos=int(mesh.t.shape[1]), vm_prom_1Nm=float(vm_avg.max()),
           vm_lejos_1Nm=float(vm_avg[d > 0.3].max()), F_oreja_1Nm=float(F_izq),
           F_vastago_1Nm=float(fz[tags == "vastago"].sum()),
           p_pared_1Nm=float(p_loc), p_media_1Nm=float(F_izq / (largo * F.T)))
print(json.dumps(res, indent=1))
json.dump(res, open("resultados_dos_orejas_1Nm.json", "w"), indent=2)
