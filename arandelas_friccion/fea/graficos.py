#!/usr/bin/env python3
"""Diagramas y tabla de capacidad a partir de los resultados del FEA (por 1 N·m)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri

D = "."
res = json.load(open(f"{D}/resultados_1Nm.json"))
CASOS = [("A_oreja_1mm", "Tipo A – oreja encastrada 1 mm (actual)"),
         ("A_oreja_2mm", "Tipo A – oreja alargada, encastre 2 mm"),
         ("B", "Tipo B – caras de 11 mm")]

# ---------------------------------------------------- demanda
F_MANO = 2.5e3 / (0.25 * 5)            # 2,5 N·m con Allen 3 -> ~2000 N
R_EFF = 4.08
def T_arandela(mu, F=F_MANO):          # par que debe transmitir una arandela intermedia [N·m]
    return 2 * mu * F * R_EFF / 1000

MAT = {"AISI 304 recocido": 215, "AISI 301 1/2 duro": 760, "AISI 301 duro": 965,
       "AISI 420 templado": 1350, "17-7PH CH900": 1585}
SY_AL = 460                            # Al 7075-T6, Rp0,2 mínimo

# ---------------------------------------------------- figura 1: mapas
T_PLOT = 1.0
fig, axs = plt.subplots(1, 3, figsize=(16, 5.6), constrained_layout=True)
vmax = 500
for ax, (k, titulo) in zip(axs, CASOS):
    z = np.load(f"{D}/{k}.npz")
    p, t, vm = z["p"], z["t"], z["vm_avg"] * T_PLOT
    amp = 0.6 / max(1e-12, np.abs(np.r_[z["ux"], z["uy"]]).max())
    tri = mtri.Triangulation(p[0], p[1], t.T)
    trd = mtri.Triangulation(p[0] + amp * z["ux"], p[1] + amp * z["uy"], t.T)
    cs = ax.tricontourf(tri, np.clip(vm, 0, vmax), levels=np.linspace(0, vmax, 26), cmap="turbo")
    ax.triplot(trd, lw=0.05, color="k", alpha=0.15)
    sel = z["cf"] > 1e-3 * z["cf"].max()
    ax.scatter(z["cx"][sel], z["cy"][sel], s=6 + 60 * z["cf"][sel] / z["cf"].max(),
               c="magenta", edgecolors="none", label="contacto activo")
    ax.add_patch(plt.Circle((0, 0), 5.0, fill=False, ls="--", lw=0.8, color="w"))
    r = res[k]
    ax.set_title(f"{titulo}\nσvM máx (prom. 0,1 mm) = {r['vm_prom_1Nm']:.0f} MPa por N·m\n"
                 f"presión pared máx = {r['p_pared_1Nm']:.0f} MPa por N·m", fontsize=10)
    ax.set_aspect("equal"); ax.set_xlim(-9, 7); ax.set_ylim(-6.5, 6.5)
    ax.annotate("par de fricción ↺", (0, 0), ha="center", va="center", color="w", fontsize=8)
    if k.startswith("A"):
        tip = 7.5 if "1mm" in k else 8.5
        e = 1.0 if "1mm" in k else 2.0
        ax.add_patch(plt.Rectangle((-tip - 0.6, -3.4), e + 0.6, 0.9, color="silver", alpha=0.8))
        ax.text(-tip - 0.5, -4.0, "pared Al 7075", fontsize=7)
    else:
        for y0 in (5.5, -6.4):
            ax.add_patch(plt.Rectangle((-5, y0), 10, 0.9, color="silver", alpha=0.8))
    ax.legend(loc="lower right", fontsize=7)
cb = fig.colorbar(cs, ax=axs, shrink=0.85)
cb.set_label("von Mises [MPa] para 1 N·m por arandela (escala lineal con el par)")
fig.suptitle("FEA tensión plana, t = 0,5 mm, inox – deformada ampliada", fontsize=12)
fig.savefig(f"{D}/fea_mapas_1Nm.png", dpi=150)

# ---------------------------------------------------- figura 2: zoom oreja
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), constrained_layout=True)
for ax, k in zip(axs, ["A_oreja_1mm", "A_oreja_2mm"]):
    z = np.load(f"{D}/{k}.npz")
    tri = mtri.Triangulation(z["p"][0], z["p"][1], z["t"].T)
    cs = ax.tricontourf(tri, np.clip(z["vm_avg"], 0, vmax), levels=np.linspace(0, vmax, 26), cmap="turbo")
    ax.tricontour(tri, z["vm_avg"], levels=[215], colors="w", linewidths=1)
    ax.set_xlim(-9, -3.5); ax.set_ylim(-3.8, 3.8); ax.set_aspect("equal")
    ax.set_title(dict(CASOS)[k] + "\n(línea blanca: zona que fluye en 304 recocido con 1 N·m)", fontsize=9)
fig.colorbar(cs, ax=axs, label="von Mises [MPa] por N·m")
fig.savefig(f"{D}/fea_oreja_zoom.png", dpi=150)

# ---------------------------------------------------- tensiones lejos del contacto y aplastamiento medio
from scipy.spatial import cKDTree
for k, _ in CASOS:
    z = np.load(f"{D}/{k}.npz")
    sel = z["cf"] > 1e-3 * z["cf"].max()
    d, _i = cKDTree(np.c_[z["cx"][sel], z["cy"][sel]]).query(z["p"].T)
    lejos = d > 0.3
    res[k]["vm_lejos_1Nm"] = float(z["vm_avg"][lejos].max())
    # aplastamiento medio sobre la pared: fuerza / (largo de contacto x t)
    pared = sel & ((np.abs(np.abs(z["cy"]) - 2.5) < 1e-6) if k.startswith("A")
                   else (np.abs(np.abs(z["cy"]) - 5.5) < 1e-6))
    xs = z["cx"][pared]; ys = z["cy"][pared]; fs = z["cf"][pared]
    largo = 0.0; F = 0.0
    for sgn in (1, -1):
        m = np.sign(ys) == sgn
        if m.sum() > 1:
            largo = max(largo, xs[m].max() - xs[m].min()); F = max(F, fs[m].sum())
    res[k]["p_media_1Nm"] = F / (largo * 0.5)
    res[k]["F_pared_lado_1Nm"] = F
    res[k]["largo_contacto"] = largo
    print(k, {kk: round(v, 2) if isinstance(v, float) else v for kk, v in res[k].items()})

# ---------------------------------------------------- tabla de capacidad
filas = []
for k, titulo in CASOS:
    r = res[k]
    for m, sy in MAT.items():
        t_w = sy / r["vm_prom_1Nm"]
        t_al = SY_AL / r["p_pared_1Nm"]
        t_w2 = min(sy / r["vm_lejos_1Nm"], sy / r["p_media_1Nm"])
        t_al2 = SY_AL / r["p_media_1Nm"]
        filas.append((k, m, sy, t_w, t_al, min(t_w, t_al), "arandela" if t_w < t_al else "Al 7075",
                      t_w2, t_al2, min(t_w2, t_al2), "arandela" if t_w2 < t_al2 else "Al 7075"))

# figura 3: capacidad vs demanda
fig, ax = plt.subplots(figsize=(11, 5), constrained_layout=True)
w = 0.26
mats = list(MAT)
x = np.arange(len(mats))
for i, (k, titulo) in enumerate(CASOS):
    vals = [f[5] for f in filas if f[0] == k]
    vals2 = [f[9] for f in filas if f[0] == k]
    b = ax.bar(x + (i - 1) * w, vals, w, label=titulo, color=f"C{i}")
    ax.bar(x + (i - 1) * w, vals2, w, fill=False, edgecolor=f"C{i}", hatch="//", lw=0.8,
           label="nivel 2 (deformación apreciable)" if i == 0 else None)
    for xi, v2 in zip(x + (i - 1) * w, vals2):
        ax.text(xi, v2 + 0.05, f"{v2:.1f}", ha="center", fontsize=6, color=f"C{i}")
    for xi, f in zip(x + (i - 1) * w, [f for f in filas if f[0] == k]):
        ax.text(xi, f[5] + 0.05, f"{f[5]:.2f}" + ("*" if f[6] == "Al 7075" else ""),
                ha="center", fontsize=7)
for mu, ls in [(0.15, ":"), (0.3, "--"), (0.4, "-")]:
    ax.axhline(T_arandela(mu), ls=ls, color="r", lw=1)
    ax.text(len(mats) - 0.45, T_arandela(mu), f"demanda μ={mu}\n(Allen 2,5 N·m)", color="r",
            fontsize=7, va="center")
ax.set_xticks(x, mats, fontsize=8)
ax.set_ylabel("Par admisible por arandela [N·m]\nlleno: sin marcas (nivel 1) · rayado: nivel 2")
ax.set_title("Capacidad por arandela (FEA) vs. par que le impone la fricción con apriete a mano\n"
             "* = limita la pared de Al 7075 (460 MPa), no la arandela")
ax.legend(fontsize=8, loc="upper left")
fig.savefig(f"{D}/capacidad_vs_demanda.png", dpi=150)

with open(f"{D}/tabla_capacidad.md", "w") as fh:
    fh.write("| Caso | Material | Rp0,2 | T arandela [N·m] | T pared Al [N·m] | T adm [N·m] | Limita | "
             "F máx p/ deslizar μ=0,3 [N] | Apriete [N·m] | Traba máx 6 arandelas [N·m] |\n")
    fh.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for k, m, sy, tw, tal, tad, lim, *_ in filas:
        Fm = tad * 1000 / (2 * 0.3 * R_EFF)
        fh.write(f"| {k} | {m} | {sy} | {tw:.2f} | {tal:.2f} | **{tad:.2f}** | {lim} | {Fm:.0f} | "
                 f"{Fm*0.25*5/1000:.2f} | {2.5*tad:.1f} |\n")
with open(f"{D}/tabla_capacidad.md", "a") as fh:
    fh.write("\n**Nivel 2: deformación apreciable** (aplastamiento medio sobre el largo de contacto y tensión del cuerpo lejos del contacto; se aceptan marcas locales)\n\n")
    fh.write("| Caso | Material | T arandela [N·m] | T pared Al [N·m] | T adm [N·m] | Limita | Traba máx 6 arandelas [N·m] |\n|---|---|---|---|---|---|---|\n")
    for k, m, sy, tw, tal, tad, lim, tw2, tal2, tad2, lim2 in filas:
        fh.write(f"| {k} | {m} | {tw2:.2f} | {tal2:.2f} | **{tad2:.2f}** | {lim2} | {2.5*tad2:.1f} |\n")
json.dump(res, open(f"{D}/resultados_1Nm.json", "w"), indent=2)
print(open(f"{D}/tabla_capacidad.md").read())
print("Demanda por arandela con Allen 2,5 N·m:", {mu: round(T_arandela(mu), 2) for mu in (0.15, 0.3, 0.4)})
