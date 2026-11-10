#!/usr/bin/env python3
"""Búsqueda de la combinación óptima del paquete (una articulación, geometría real).

Modos de falla verificados en el punto de diseño (μ máx, F máx, factor de seguridad SF):
  1. Pared del alojamiento (Al 7075, FEA 3D por superposición de bandas) - carga de las B
  2. Oreja de A contra el otro eslabón (Al 7075, aplastamiento)          - cA·tA
  3. Cuerpo de B (301 duro o CuSn8)                                       - cB·tB
  4. Cuello del tornillo A2-50 (1640 N)                                   - F
Variables: n° de B, terminación (A o B arriba), tA, tB, par de materiales, refuerzo de paredes.
Objetivo: máxima traba GARANTIZADA (μ mín y F mín por dispersión del apriete).
"""
import itertools, json, sys
import numpy as np
from scipy.spatial import cKDTree

SF, R, H_MAX = 1.25, 4.08, 4.5
SY_AL, F_TORN = 460.0, 1640.0
DISP_F = 0.66                       # F mín / F máx con destornillador dinamométrico en seco
C = np.array([-15.288, -110.875]); Y0 = 79.75
cA = min(965 / 361, SY_AL / 191) * 2          # N·m por mm de espesor (A, 1 oreja 1,5 mm)
PARES = {"inox/inox": dict(mu=(0.3, 0.6), cB=965 / 213 * 2),
         "inox/bronce CuSn8": dict(mu=(0.2, 0.35), cB=600 / 213 * 2)}
ESP = [0.3, 0.4, 0.5, 0.6, 0.8, 1.0]


def cargar(var):
    z = np.load(f"bandas_{var}.npz")
    return z["p"], z["S"], z["src"], (z["bandas"].mean(axis=1) - Y0)


def vm(s):
    sxx, syy, szz, sxy, syz, sxz = s
    return np.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) + 3 * (sxy ** 2 + syz ** 2 + sxz ** 2))


def capacidades(var):
    """cA, cB(301), cB(CuSn8) en N·m/mm y radio eficaz para cada variante de alojamiento."""
    if "_d" in var:
        d = float(var.split("_d")[1])
        r = json.load(open(f"resultados_real_d{d}_1Nm.json"))
        ro = min(5.0, r["r_ext_A"])
    else:
        r = json.load(open("resultados_real_1Nm.json")); ro = 5.0
    a, b = r["A_real"], r["B_real"]
    cA = min(965 / a["vm_lejos_1Nm"], SY_AL / a["p_media_1Nm"]) * 2   # resultados con t = 0,5 -> por mm
    cB = {"inox/inox": 965 / b["vm_lejos_1Nm"] * 2, "inox/bronce CuSn8": 600 / b["vm_lejos_1Nm"] * 2}
    reff = 2 / 3 * (ro**3 - 27) / (ro**2 - 9)
    return cA, cB, reff


class Pared:
    def __init__(self, var):
        self.p, self.S, src, self.yc = cargar(var)
        self.src = src
        self.cache = {}

    def sigma_unit(self, centros, tB):
        """σ máx. de pared (MPa) con 1 N·m en cada B ubicada en 'centros' (mm desde el fondo)."""
        key = (tuple(np.round(centros, 3)), tB)
        if key in self.cache: return self.cache[key]
        tot = np.zeros_like(self.S[0])
        for c in centros:
            j = np.clip(np.searchsorted(self.yc, c) - 1, 0, len(self.yc) - 2)
            w = np.clip((c - self.yc[j]) / (self.yc[j + 1] - self.yc[j]), 0, 1)
            tot += (1 - w) * self.S[j] + w * self.S[j + 1]
        LP = np.array([[x + C[0], Y0 + c + dy, z + C[1]] for x, z in self.src for c in centros
                       for dy in np.linspace(-tB / 2, tB / 2, 3)])
        dl, _ = cKDTree(LP).query(self.p.T)
        m = (self.p[1] >= Y0 + 0.3) & (dl > 0.4)
        val = float(vm(tot)[m].max())
        self.cache[key] = val
        return val


def evaluar(pared, nB, fin_B, tA, tB, par, caps=None):
    cA_, cB_, R_ = caps if caps else (cA, {k: v["cB"] for k, v in PARES.items()}, R)
    nA = nB if fin_B else nB + 1
    altura = nA * tA + nB * tB
    if altura > H_MAX + 1e-9: return None
    seq = []
    for i in range(nB):
        seq += ["A", "B"]
    if not fin_B: seq.append("A")
    y = 0.0; centrosB = []
    for s in seq:
        t = tA if s == "A" else tB
        if s == "B": centrosB.append(y + t / 2)
        y += t
    caras = 1 + (len(seq) - 1) + (1 if fin_B else 0)
    mu0, mu1 = PARES[par]["mu"]; cB = cB_[par]
    s_unit = pared.sigma_unit(centrosB, tB)              # MPa por N·m en cada B
    # par por arandela con μ máx: Tw = 2·μ1·F·R  -> límites de F
    lim = {
        "pared Al": SY_AL / SF / s_unit,                  # N·m por B
        "oreja A": cA_ * tA / SF,
        "cuerpo B": cB * tB / SF,
    }
    Tw_adm = min(lim.values())
    F_max = min(Tw_adm * 1000 / (2 * mu1 * R_), F_TORN / SF)
    Tw = 2 * mu1 * F_max * R_ / 1000
    util = {k: Tw / v for k, v in lim.items()}
    util["tornillo"] = F_max / (F_TORN / SF)
    T_max = caras * mu1 * F_max * R_ / 1000
    T_min = caras * mu0 * F_max * DISP_F * R_ / 1000
    return dict(nB=nB, nA=nA, seq="-".join(seq), tA=tA, tB=tB, par=par, altura=round(altura, 2),
                caras=caras, F_max=round(F_max), T_apriete=round(F_max * 0.23 * 5 / 1000, 2), r_eff=round(R_, 2),
                T_min=round(T_min, 2), T_max=round(T_max, 2), limita=max(util, key=util.get),
                util={k: round(v, 2) for k, v in util.items()}, sigma_unit=round(s_unit))


def main():
    variantes = sys.argv[1:] or ["real"]
    todos = []
    for var in variantes:
        pared = Pared(var); caps = capacidades(var)
        print(var, "cA=%.2f N·m/mm, cB=%s, r_eff=%.2f mm" % (caps[0], {k: round(v, 2) for k, v in caps[1].items()}, caps[2]))
        for nB, fin_B, tA, tB, par in itertools.product(range(1, 7), (True, False), ESP, ESP, PARES):
            r = evaluar(pared, nB, fin_B, tA, tB, par, caps)
            if r: r["eslabon"] = var; todos.append(r)
    todos.sort(key=lambda r: -r["T_min"])
    json.dump(todos, open("optimizacion.json", "w"), indent=1)
    print(f"{len(todos)} combinaciones evaluadas")
    for var in variantes:
        print(f"\n== eslabón {var}: mejores 8")
        for r in [r for r in todos if r["eslabon"] == var][:8]:
            print(f"  {r['seq']:<24} tA={r['tA']} tB={r['tB']} {r['par']:<18} h={r['altura']} caras={r['caras']} "
                  f"F={r['F_max']} N  traba {r['T_min']}–{r['T_max']} N·m  limita {r['limita']} {r['util']}")
    ref = [r for r in todos if r["eslabon"] == variantes[0] and r["seq"] == "A-B-A-B-A-B" and r["tA"] == 1.0
           and r["tB"] == 0.5 and r["par"] == "inox/inox"]
    if ref: print("\nactual:", ref[0])


if __name__ == "__main__":
    main()
