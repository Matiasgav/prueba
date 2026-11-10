#!/usr/bin/env python3
"""FEA 2D con los contornos EXACTOS del STEP 02489-00-M40000 (una articulación).

A: oreja a −x, punta 8,0 mm, encastre 1,5 mm en el eslabón opuesto (pared en r = 6,5).
B: retenida por el alojamiento del eslabón: caras z = ±5,5 (x desde −4,38) y perfil
   derecho (chaflanes + R5,5), que copia el contorno de B. Lado −x abierto.
Resultados por 1 N·m con t = 0,5 mm (escalan con 1/t).
"""
import json
import numpy as np
from scipy.spatial import cKDTree
import fea_arandelas as F

CT = json.load(open("contornos_step.json"))


def normales(P):
    P = np.asarray(P); n = len(P)
    t = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    nrm = np.c_[t[:, 1], -t[:, 0]]
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    # orientar hacia afuera (área con signo)
    area = 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
    return nrm if area > 0 else -nrm


def caso_A():
    P = np.array(CT["A"])
    ap = [(lambda x, y: (y < -2.4) & (y > -2.6) & (x <= -6.5 + 1e-6) & (x > -8.05), lambda x, y: (0, 1), "oreja"),
          (lambda x, y: np.abs(np.hypot(x, y) - F.R_HOLE) < 1e-3, lambda x, y: (x, y), "vastago")]
    return P, ap


def caso_B():
    P = np.array(CT["B"]); N = normales(P); tree = cKDTree(P)
    def en_bolsillo(x, y):
        d, _ = tree.query(np.c_[x, y])
        return (d < 0.03) & (x >= -4.383) & (np.hypot(x, y) > 4.0)
    def m(x, y):
        _, i = tree.query([x, y]); return tuple(-N[i])
    ap = [(en_bolsillo, m, "bolsillo"),
          (lambda x, y: np.abs(np.hypot(x, y) - F.R_HOLE) < 1e-3, lambda x, y: (x, y), "vastago")]
    return P, ap


if __name__ == "__main__":
    res = {}
    for nombre, (cont, ap) in {"A_real": caso_A(), "B_real": caso_B()}.items():
        mesh = F.malla(cont)
        ib, u, cands, fz, q = F.resolver(mesh, ap)
        vm = F.von_mises(ib, u, mesh); vm_avg = F.promedio(mesh, vm)
        c = np.array([[k[4], k[5]] for k in cands]); tags = np.array([k[3] for k in cands])
        act = fz > 1e-3 * fz.max()
        d, _ = cKDTree(c[act]).query(mesh.p.T)
        pared = act & (tags != "vastago")
        r = dict(vm_prom_1Nm=float(vm_avg.max()), vm_lejos_1Nm=float(vm_avg[d > 0.3].max()),
                 pos_max=mesh.p[:, int(np.argmax(vm_avg))].round(2).tolist(),
                 F_pared_total_1Nm=float(fz[pared].sum()))
        # fuerzas de contacto sobre la pared (para cargar el modelo 3D del eslabón)
        r["contacto"] = [[float(c[i, 0]), float(c[i, 1]), float(fz[i]), *map(float, cands[i][2])]
                         for i in np.where(pared)[0]]
        if nombre == "A_real":
            o = pared; largo = c[o, 0].max() - c[o, 0].min()
            r["p_media_1Nm"] = float(fz[o].sum() / (largo * F.T))
            _, r["p_pared_1Nm"] = F.presion_pared(cands, fz, ["oreja"], 0)
        res[nombre] = r
        print(nombre, {k: v for k, v in r.items() if k != "contacto"}, flush=True)
        np.savez(f"{nombre}.npz", p=mesh.p, t=mesh.t, vm_avg=vm_avg,
                 cx=c[:, 0], cy=c[:, 1], cf=fz)
    json.dump(res, open("resultados_real_1Nm.json", "w"), indent=1)
