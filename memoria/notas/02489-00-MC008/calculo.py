"""02489-00-MC008 - Conector Fischer MiniMax Size 08, 19 contactos.

Calcula: caida de tension y perdida en el par de potencia (2 x AWG24 por
polaridad), corriente maxima para una caida admisible y geometria del corte
de panel (plano superior).

Datos: Fischer Technical Specification Vol. 2 MiniMax (pp. J-8, J-9, J-15,
J-16, J-18, J-27) y datasheets P/N 131600 y 131633 (ver fuentes/).
Resistividad AWG24: 0,0858 ohm/m a 25 C (dato de la nota de seleccion; ver
supuestos en el .tex). Resistencia de contacto: 5 mohm tipico (J-27).
Escribe resultados.json y figuras/corte_panel.png.
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

R25 = 0.0858          # ohm/m, AWG24 Cu 25 C, un conductor
ALPHA = 0.00393       # 1/K, cobre
RC_CONT = 0.005       # ohm por contacto acoplado (tipico)
V0 = 48.0
n_par = 2             # conductores en paralelo por polaridad

def rloop(L, T=25.0):
    r = R25 * (1 + ALPHA * (T - 25.0))
    return 2 * (r / n_par) * L + 2 * (RC_CONT / n_par)   # ida+retorno + contactos

res = {"R25_ohm_m": R25, "tabla": [], "Imax_5pc": {}}
for L in (10, 15):
    for I in (2, 3, 4, 5, 10):
        R = rloop(L); Rc = R - 2 * (RC_CONT / n_par)
        res["tabla"].append(dict(L=L, I=I, dV_cable=round(I*Rc, 2),
             dV_total=round(I*R, 2), V_robot=round(V0 - I*R, 1),
             P_cable=round(I*I*Rc, 1), dV_60C=round(I*rloop(L, 60), 2)))
    res["Imax_5pc"][str(L)] = round(0.05 * V0 / rloop(L), 2)

# corte de panel: circulo X=10,45 y distancia plano-opuesto Y=10,2
X, Y = 10.45, 10.2
r = X / 2; h = X - Y
chord = 2 * math.sqrt(r**2 - (r - h)**2)
res["corte"] = dict(X=X, Y=Y, profundidad_plano=round(h, 2), cuerda_plano=round(chord, 2))
json.dump(res, open("resultados.json", "w"), indent=1)

# figura del corte
fig, ax = plt.subplots(figsize=(5.2, 4.6))
t = np.linspace(0, 2*np.pi, 721)
xs, ys = r*np.cos(t), r*np.sin(t)
ymax = r - h        # plano superior a y = r-h
m = ys <= ymax
ax.fill(np.r_[xs[m], xs[m][0]], np.r_[ys[m], ys[m][0]], fc="#eef0f2", ec="#1E2328", lw=1.6)
ax.plot([-chord/2, chord/2], [ymax, ymax], color="#1E2328", lw=1.6)
ax.annotate("", (-r, -r-1.2), (r, -r-1.2), arrowprops=dict(arrowstyle="<->", lw=.9))
ax.text(0, -r-2.0, r"$\varnothing X = 10{,}45\;{}^{+0{,}1}_{\ 0}$", ha="center", fontsize=10)
ax.annotate("", (r+1.3, -r), (r+1.3, ymax), arrowprops=dict(arrowstyle="<->", lw=.9))
ax.text(r+1.7, 0, r"$Y = 10{,}2\;{}^{+0{,}1}_{\ 0}$", rotation=90, va="center", fontsize=10)
ax.annotate("plano (Top)\ncuerda $\\approx$ %s" % f"{chord:.1f}".replace(".", ","), (0, ymax), (0, r+1.5),
            ha="center", fontsize=9, arrowprops=dict(arrowstyle="->", lw=.8))
ax.plot([0], [0], "+", color="#6B7280"); ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-8, 9); ax.set_ylim(-8, 8)
fig.savefig("figuras/corte_panel.png", dpi=250, bbox_inches="tight")
print(json.dumps(res, indent=1))
