#!/usr/bin/env python3
"""Métricas comparables de las variantes del eslabón (por 1 N·m en cada B)."""
import json, sys
import numpy as np
from scipy.spatial import cKDTree
C = np.array([-15.288, -110.875]); BANDAS = [(80.75, 81.25), (82.25, 82.75), (83.75, 84.25)]
B = np.array(json.load(open("resultados_real_1Nm.json"))["B_real"]["contacto"]); B = B[B[:, 2] > 1e-6]
LP = np.array([[x + C[0], y, z + C[1]] for x, z in B[:, :2] for a, b in BANDAS for y in np.linspace(a, b, 3)])
out = {}
for v in sys.argv[1:]:
    z = np.load(f"eslabon3d_{v}.npz"); p = z["p"]; vm = z["vm"]; u = np.c_[z["ux"], z["uy"], z["uz"]] * 1000
    dl, _ = cKDTree(LP).query(p.T)
    m = (p[1] >= 80.05) & (dl > 0.4)
    i = int(np.argmax(np.where(m, vm, 0)))
    t = cKDTree(p.T)
    _, it = t.query([-15.3, 84.25, -105.375]); _, ib_ = t.query([-15.3, 84.25, -116.375])
    _, ic = t.query([-19.67, 84.25, -116.375])
    out[v] = dict(sigma_cuerpo=float(vm[i]), pos=p[:, i].round(2).tolist(),
                  apertura_um=float(u[it, 2] - u[ib_, 2]), esquina_um=float(np.linalg.norm(u[ic])))
    print(v, {k: (round(x, 1) if isinstance(x, float) else x) for k, x in out[v].items()})
json.dump(out, open("variantes_eslabon_1Nm.json", "w"), indent=1)
