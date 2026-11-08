#!/usr/bin/env python3
"""Arandela A con UNA oreja, encastre 1,5 mm (punta 8,0 mm, pared en r = 6,5 mm)."""
import json
import numpy as np
from scipy.spatial import cKDTree
import fea_arandelas as F

cont, ap = F.caso_A(8.0, 1.5)
mesh = F.malla(cont)
ib, u, cands, fz, q = F.resolver(mesh, ap)
vm = F.von_mises(ib, u, mesh); vm_avg = F.promedio(mesh, vm)
c = np.array([[k[4], k[5]] for k in cands]); tags = np.array([k[3] for k in cands])
act = fz > 1e-3 * fz.max()
d, _ = cKDTree(c[act]).query(mesh.p.T)
o = act & (tags == "oreja")
Fw = fz[o].sum(); largo = c[o, 0].max() - c[o, 0].min()
_, ploc = F.presion_pared(cands, fz, ["oreja"], 0)
res = dict(vm_prom_1Nm=float(vm_avg.max()), vm_lejos_1Nm=float(vm_avg[d > 0.3].max()),
           F_pared_1Nm=float(Fw), p_pared_1Nm=float(ploc), p_media_1Nm=float(Fw / (largo * F.T)),
           largo=float(largo))
print(json.dumps(res, indent=1))
json.dump(res, open("resultados_oreja15_1Nm.json", "w"), indent=2)
