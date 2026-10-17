"""Dónde están las tensiones más grandes en las articulaciones Q1, Q2, O y C (ver ARTICULACIONES_ESFUERZOS.md).

Métodos de manual, sin elementos finitos:
  - pasador como viga sobre apoyo elástico (Hetényi / Winkler): reparto real de la carga a lo largo
    del pasador, momento máximo y picos de presión en los bordes de cada apoyo;
  - presión alrededor del agujero con ajuste estrecho: reparto en coseno (Persson), pico = 4/π · q/d;
  - orejeta del ojo: tensión neta con factor de concentración (Frocht y Hill, en Peterson),
    desgarro por el plano a 40° y aplastamiento (método de la Fuerza Aérea de EE.UU.).
Cargas: la carga entre ejes que rompe la estructura a W = 35 (salida/capacidad.json).
"""
import json
import math
import os

import numpy as np

import articulaciones_calc as AC

D = 5.0
I_PIN = math.pi * D ** 4 / 64
E_PIN = 200000.0                    # 440C
S_PIN = 1500.0                      # admisible a flexión del pasador templado (como analisis.py)
TAU_PIN = 0.577 * 1650.0            # fluencia en corte del 440C templado (Sy ≈ 1650)
AL = dict(E=71700.0, Sy=503.0, nombre="7075-T651")
H900 = dict(E=197000.0, Sy=1170.0, nombre="17-4PH H900")
R_OJO = 4.5                         # radio exterior de los ojos (largos y corto)
C_APOYO = 0.6                       # módulo de apoyo k = C · E* (indicativo; se prueba 0,3 a 1,0)

# capas a lo largo del pasador (z0, z1, quién, material): "mej" apoya en tierra, "ojo" lleva la carga
PIVOTES = {
    "Q1": dict(f=AC.FZ["eslabon1_Q1"], capas=[(0, 2.9, "mej", AL), (3.0, 10.0, "ojo", H900), (10.1, 13.0, "mej", AL)]),
    "Q2": dict(f=AC.FZ["eslabon2"], capas=[(0, 2.9, "mej", AL), (3.0, 10.0, "ojo", H900), (10.1, 13.0, "mej", AL)]),
    "O": dict(f=AC.FZ["corto"], capas=[(0, 5.15, "mej", AL), (5.25, 7.75, "ojo", H900), (7.85, 13.0, "mej", AL)]),
    "C": dict(f=AC.FZ["corto"], capas=[(3.0, 5.15, "mej", H900), (5.25, 7.75, "ojo", H900), (7.85, 10.0, "mej", H900)]),
}


def e_estrella(m):
    return 1 / ((1 - 0.3 ** 2) / E_PIN + (1 - 0.33 ** 2) / m["E"])


def viga_winkler(capas, F, c=C_APOYO, h=0.02):
    """Pasador de Euler-Bernoulli con resortes distribuidos. Las mejillas son tierra; el ojo es un
    cuerpo rígido (gdl extra) cargado con F. Devuelve z, carga por unidad de largo q(z) y momento M(z)."""
    z0, z1 = capas[0][0], capas[-1][1]
    n = int(round((z1 - z0) / h))
    z = np.linspace(z0, z1, n + 1)
    ndof = 2 * (n + 1) + 1
    K = np.zeros((ndof, ndof))
    EI = E_PIN * I_PIN
    ke = EI / h ** 3 * np.array([[12, 6 * h, -12, 6 * h], [6 * h, 4 * h * h, -6 * h, 2 * h * h],
                                 [-12, -6 * h, 12, -6 * h], [6 * h, 2 * h * h, -6 * h, 4 * h * h]])
    kf = h / 420 * np.array([[156, 22 * h, 54, -13 * h], [22 * h, 4 * h * h, 13 * h, -3 * h * h],
                             [54, 13 * h, 156, -22 * h], [-13 * h, -3 * h * h, -22 * h, 4 * h * h]])
    zm = (z[:-1] + z[1:]) / 2
    tipo = np.full(n, "", dtype=object)
    kk = np.zeros(n)
    for a, b, quien, m in capas:
        sel = (zm > a) & (zm < b)
        tipo[sel] = quien
        kk[sel] = c * e_estrella(m)
    iD = ndof - 1
    for e in range(n):
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += ke
        if kk[e] > 0:
            Kf = kk[e] * kf
            K[np.ix_(idx, idx)] += Kf
            if tipo[e] == "ojo":            # resorte entre el pasador y el ojo (desplazamiento Δ)
                Nint = h / 2 * np.array([1, h / 6, 1, -h / 6])   # ∫N dx
                K[idx, iD] -= kk[e] * Nint
                K[iD, idx] -= kk[e] * Nint
                K[iD, iD] += kk[e] * h
    f = np.zeros(ndof)
    f[iD] = F
    u = np.linalg.solve(K, f)
    w = u[0:2 * (n + 1):2]
    th = u[1:2 * (n + 1):2]
    Dl = u[iD]
    wm = (w[:-1] + w[1:]) / 2
    q = np.where(tipo == "ojo", kk * (Dl - wm), kk * wm)        # N/mm, presión de contacto (siempre > 0)
    qs = np.where(tipo == "ojo", q, -q)                          # con signo: el ojo empuja, las mejillas sostienen
    # momento en los nodos por equilibrio (integrando desde el extremo libre)
    V = np.r_[0, np.cumsum(qs * h)]
    M = np.r_[0, np.cumsum(V[:-1] * h + qs * h * h / 2)]
    return z, zm, q, M, tipo


def picos(nombre, p, c=C_APOYO):
    F = p["f"] * AC.F_ESTR
    z, zm, q, M, tipo = viga_winkler(p["capas"], F, c)
    Mmax = np.max(np.abs(M))
    t_m = p["capas"][0][1] - p["capas"][0][0]
    t_o = p["capas"][1][1] - p["capas"][1][0]
    g = p["capas"][1][0] - p["capas"][0][1]
    M_bruhn = F / 2 * (t_m / 2 + g + t_o / 4)
    out = dict(F=F, M_max=Mmax, M_bruhn=M_bruhn, z_Mmax=float(z[np.argmax(np.abs(M))]))
    out["sigma_flexion"] = 32 * Mmax / (math.pi * D ** 3)
    out["tau_corte"] = 4 / 3 * (F / 2) / (math.pi * D ** 2 / 4)
    for quien in ("ojo", "mej"):
        sel = tipo == quien
        t = t_o if quien == "ojo" else t_m
        Fq = F if quien == "ojo" else F / 2
        q_med = Fq / t
        i = np.argmax(np.where(sel, q, -1e9))
        out[f"q_pico_{quien}"] = float(q[i])
        out[f"z_pico_{quien}"] = float(zm[i])
        out[f"borde_{quien}"] = float(q[i] / q_med)                  # pico del borde / reparto parejo
        out[f"p_nominal_{quien}"] = Fq / (D * t)
        out[f"p_max_{quien}"] = 4 / math.pi * q[i] / D                   # coseno de Persson
    # orejeta del ojo (ojo de R 4,5): tracción neta con Kt y desgarro a 40°
    mat_o = p["capas"][1][3]
    out["sigma_neta_nom"] = F / ((2 * R_OJO - D) * t_o)
    out["Kt_rango"] = (2.5, 3.5)
    out["sigma_neta_pico"] = [k * out["sigma_neta_nom"] for k in out["Kt_rango"]]
    e = R_OJO
    out["tau_desgarro"] = F / (2 * t_o * (e - D / 2 * math.cos(math.radians(40))))
    out["e_sobre_D"] = e / D
    out["W_sobre_D"] = 2 * R_OJO / D
    out["mat_ojo"], out["mat_mej"] = mat_o, p["capas"][0][3]
    return out


def utilizaciones(r):
    mo, mm = r["mat_ojo"], r["mat_mej"]
    return {
        "pasador: flexión (centro del ojo)": r["sigma_flexion"] / S_PIN,
        "pasador: corte (planos ojo-mejilla)": r["tau_corte"] / TAU_PIN,
        "ojo: presión en el borde del agujero": r["p_max_ojo"] / (1.5 * mo["Sy"]),
        "mejilla: presión en el borde interior": r["p_max_mej"] / (1.5 * mm["Sy"]),
        "ojo: tracción neta con Kt (costados del agujero)": r["sigma_neta_pico"][1] / mo["Sy"],
        "ojo: desgarro hacia la corona": r["tau_desgarro"] / (0.577 * mo["Sy"]),
    }


if __name__ == "__main__":
    res = {}
    print(f"Carga entre ejes que rompe la estructura a W = 35: {AC.F_ESTR:.0f} N")
    for n, p in PIVOTES.items():
        r = picos(n, p)
        rs = [picos(n, p, c) for c in (0.3, 1.0)]
        print(f"\n{n}: F = {r['F']:.0f} N   e/D = {r['e_sobre_D']:.2f}   W/D = {r['W_sobre_D']:.2f}")
        print(f"  momento del pasador: {r['M_max']:.0f} N·mm (Bruhn: {r['M_bruhn']:.0f}) en z = {r['z_Mmax']:.2f}"
              f"  -> σ = {r['sigma_flexion']:.0f} MPa")
        print(f"  corte en los planos ojo-mejilla: τ = {r['tau_corte']:.0f} MPa")
        for quien, nom in (("ojo", "ojo"), ("mej", "mejilla")):
            print(f"  {nom}: presión nominal {r['p_nominal_' + quien]:.0f} MPa, pico en el borde z = {r['z_pico_' + quien]:.2f}:"
                  f" ×{r['borde_' + quien]:.2f} del reparto parejo (rango {rs[0]['borde_' + quien]:.2f} a {rs[1]['borde_' + quien]:.2f})"
                  f" -> {r['p_max_' + quien]:.0f} MPa en el fondo del contacto")
        print(f"  ojo: tracción neta nominal {r['sigma_neta_nom']:.0f} MPa -> pico con Kt 2,5 a 3,5:"
              f" {r['sigma_neta_pico'][0]:.0f} a {r['sigma_neta_pico'][1]:.0f} MPa; desgarro τ = {r['tau_desgarro']:.0f} MPa")
        u = utilizaciones(r)
        for k, v in sorted(u.items(), key=lambda kv: -kv[1]):
            print(f"    {v * 100:5.0f} %  {k}")
        res[n] = dict(F=r["F"], M_max=r["M_max"], M_bruhn=r["M_bruhn"], util=u,
                      borde_ojo=r["borde_ojo"], borde_mej=r["borde_mej"],
                      borde_rango=[[rs[0]["borde_ojo"], rs[1]["borde_ojo"]], [rs[0]["borde_mej"], rs[1]["borde_mej"]]],
                      p_max_ojo=r["p_max_ojo"], p_max_mej=r["p_max_mej"], sigma_flexion=r["sigma_flexion"],
                      tau_corte=r["tau_corte"], sigma_neta=r["sigma_neta_pico"], tau_desgarro=r["tau_desgarro"])
    json.dump(res, open(os.path.join(AC.AQUI, "salida", "articulaciones_esfuerzos.json"), "w"), indent=1)
