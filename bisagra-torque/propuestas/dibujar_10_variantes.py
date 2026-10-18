"""Lámina con 10 variantes de arandela para la pila de la bisagra.
Uso: python3 dibujar_10_variantes.py"""

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle, RegularPolygon

from dibujar_arandelas import (A, B, A_SOFT, B_SOFT, STEEL, RED, INK, MUTED, R,
                               CARA, arco, d_mejorada, placas)

AQUI = Path(__file__).resolve().parent
BG = "white"


def base(ax, n, titulo, pie):
    ax.set_aspect("equal")
    ax.set_xlim(-11.5, 11.5)
    ax.set_ylim(-9.5, 9.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"{n} · {titulo}", loc="left", fontsize=10.5, fontweight="bold", color=INK)
    ax.set_xlabel(pie, fontsize=8.2, color=INK, linespacing=1.35)


def agujero(ax, r=2.6):
    ax.add_patch(Circle((0, 0), r, fc=BG, ec=INK, lw=.8))


def apriete(ax):
    ax.add_patch(Circle((0, 0), R, fc="none", ec=INK, ls="--", lw=.6))


def nota(ax, xy, txt, xytext, color=RED):
    ax.annotate(txt, xy, xytext, fontsize=7.5, color=color,
                arrowprops=dict(arrowstyle="->", color=color, lw=.8))


fig, axs = plt.subplots(2, 5, figsize=(22, 11.5))
axs = axs.ravel()

# 1 · D gruesa con bultos
ax = axs[0]
base(ax, 1, "D gruesa con bultos",
     "0,8 mm, esquinas R 1,5, luz 0,1 y 2 bultos.\n"
     "+ cambio mínimo, juego 0, 2× superficie\n− las esquinas siguen sin apoyo")
placas(ax)
ax.add_patch(Polygon(d_mejorada(), fc=B_SOFT, ec=INK, lw=1))
apriete(ax); agujero(ax)
nota(ax, (8.0, 4), "bultos", (3.2, 7.6))

# 2 · D con talón (peine)
ax = axs[1]
base(ax, 2, "D con talón escalonado",
     "La traba (fuera de Ø14) tiene 2 capas: ocupa el\nhueco vacío de la arandela vecina.\n"
     "+ las trabas se apoyan entre sí: no pandean\n− arandela de 2 espesores; orden fijo")
placas(ax)
ax.add_patch(Polygon(d_mejorada(), fc=B_SOFT, ec=INK, lw=1))
talon = arco(0, 0, R + 0.2, -90, 90)[::-1] + [(6.4, -R), (7.9, -5.5), (7.9, 5.5), (6.4, R)]
ax.add_patch(Polygon(talon, fc=B, alpha=.45, ec="none"))
apriete(ax); agujero(ax)
ax.text(4.1, -0.3, "talón\n2 capas", fontsize=7.5, color=INK, ha="center", va="center")
# corte axial de la pila: peine
ins = ax.inset_axes([0.02, 0.02, 0.36, 0.3])
ins.set_xlim(0, 7)
ins.set_ylim(-2.4, 2.4)
ins.set_xticks([]); ins.set_yticks([])
ins.set_facecolor(BG)
for k in range(6):
    c = B_SOFT if k % 2 == 0 else A_SOFT
    ins.add_patch(Rectangle((0.5 + k, -1.2), 1, 2.4, fc=c, ec=INK, lw=.4))
for k in (0, 2, 4):
    ins.add_patch(Rectangle((0.5 + k, 1.2), 2, 1.0, fc=B, alpha=.6, ec=INK, lw=.4))
for k in (1, 3, 5):
    ins.add_patch(Rectangle((0.5 + k, -2.2), 2 if k < 5 else 1, 1.0, fc=A, alpha=.6, ec=INK, lw=.4))
ins.text(3.5, 0, "corte", fontsize=6.5, ha="center", va="center", color=MUTED)

# 3 · lengüeta en ranura
ax = axs[2]
base(ax, 3, "Lengüeta en ranura de la placa",
     "Lengüeta de 5 mm entra 1,8 mm en una ranura\ntallada en la placa, en la zona de la pila.\n"
     "+ empuja de costado (tangencial), sin esquinas\n− hay que ranurar placas; lengüeta suelta")
placas(ax)
ax.add_patch(Rectangle((CARA, -2.6), 2.0, 5.2, fc=BG, ec=INK, lw=.6))
perfil = arco(0, 0, R, 20, 340) + [(9.8, -2.4), (9.8, 2.4)]
ax.add_patch(Polygon(perfil, fc=B_SOFT, ec=INK, lw=1))
agujero(ax)
nota(ax, (9.8, 2.4), "apoyo lateral", (2.0, 7.8))

# 4 · dedo elástico
ax = axs[3]
base(ax, 4, "D con dedo elástico",
     "Un corte deja un dedo flexible que apoya con\nprecarga contra la placa.\n"
     "+ juego 0 y se puede reutilizar\n− más blando al empezar a cargar")
placas(ax)
ax.add_patch(Polygon(d_mejorada(bultos=()), fc=B_SOFT, ec=INK, lw=1))
ax.add_patch(Rectangle((6.4, -3.5), 0.5, 11, fc=BG, ec="none"))
ax.plot([6.4, 6.4], [-3.5, 7], color=INK, lw=.8)
ax.plot([6.9, 6.9], [-3.5, 7], color=INK, lw=.8)
ax.plot([6.4, 6.9], [-3.5, -3.5], color=INK, lw=.8)
ax.add_patch(Circle((7.95, 5.0), 0.3, fc=B_SOFT, ec=INK, lw=.8))
apriete(ax); agujero(ax)
nota(ax, (7.3, 2.5), "dedo", (2.5, -6.5))

# 5 · herradura
ax = axs[4]
base(ax, 5, "Herradura (D abierta)",
     "Abierta hacia arriba: entra y sale de costado\naflojando el tornillo, sin sacarlo.\n"
     "+ cambiar la pila lleva segundos\n− anillo abierto, algo más flexible")
placas(ax)
ax.add_patch(Polygon(d_mejorada(), fc=B_SOFT, ec=INK, lw=1))
ax.add_patch(Rectangle((-2.65, 0), 5.3, 7.6, fc=BG, ec="none"))
ax.plot([-2.65, -2.65], [0, R], color=INK, lw=.8)
ax.plot([2.65, 2.65], [0, R], color=INK, lw=.8)
ax.add_patch(Circle((0, 0), 2.6, fc=BG, ec="none"))
ax.add_patch(Polygon(arco(0, 0, 2.6, 180, 360), closed=False, fill=False, ec=INK, lw=.8))
ax.annotate("", (0, 4.6), (0, 8.8), arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
apriete(ax)

# 6 · embrague hexagonal
ax = axs[5]
base(ax, 6, "Embrague: buje hexagonal",
     "Las de B son redondas y entran en un buje\nhexagonal del nudillo; las de A siguen en D.\n"
     "+ la traba de B queda dentro de Ø14: no pandea\n− el nudillo lleva un buje; radio de traba chico")
placas(ax)
pts = [(-x, y) for x, y in d_mejorada()]
ax.add_patch(Polygon(pts, fc=A_SOFT, ec=INK, lw=1, alpha=.6))
ax.add_patch(Circle((0, 0), R, fc=B_SOFT, ec=INK, lw=1))
ax.add_patch(RegularPolygon((0, 0), 6, radius=4.3, fc=B, ec=INK, lw=1))
agujero(ax, 2.7)
ax.text(0, -5.7, "buje", fontsize=7.5, ha="center", color=INK)

# 7 · pernos pasantes con colisos
ax = axs[6]
base(ax, 7, "Pernos pasantes con colisos",
     "2 pernos Ø1,5 de A y 2 de B cruzan la pila; cada\narandela es redonda: agujeros a su lado, colisos al otro.\n"
     "+ todo dentro de Ø14, sin pandeo ni esquinas\n− el giro queda en ±55°; agujeros extra")
placas(ax)
ax.add_patch(Circle((0, 0), R, fc=B_SOFT, ec=INK, lw=1))
for ang in (0, 180):
    exterior = arco(0, 0, 5.6, ang - 60, ang + 60)
    interior = arco(0, 0, 4.0, ang + 60, ang - 60)
    ax.add_patch(Polygon(exterior + interior, fc=BG, ec=INK, lw=.8))
    ax.add_patch(Circle((4.8 * math.cos(math.radians(ang)), 4.8 * math.sin(math.radians(ang))),
                        0.75, fc=A, ec=INK, lw=.6))
for ang in (90, 270):
    ax.add_patch(Circle((4.8 * math.cos(math.radians(ang)), 4.8 * math.sin(math.radians(ang))),
                        0.75, fc=B, ec=INK, lw=.6))
agujero(ax)
ax.text(-6.8, -8.8, "perno de A en coliso", fontsize=7.5, color=A)
ax.text(-2.2, 8.2, "perno de B", fontsize=7.5, color=B)

# 8 · chapa de acero
ax = axs[7]
base(ax, 8, "Chapa de acero inoxidable",
     "D cortada a láser en chapa de 0,3–0,5 mm.\n"
     "+ no pandea, no se aplasta, no fluye con el tiempo\n− hay que encargarla; μ acero/PLA más bajo")
placas(ax)
ax.add_patch(Polygon(d_mejorada(bultos=()), fc=STEEL, ec=INK, lw=1))
apriete(ax); agujero(ax)
ax.text(1.6, -4.4, "AISI 304\n0,4 mm", fontsize=8, color=INK)

# 9 · arandela de resorte bajo la cabeza
ax = axs[8]
base(ax, 9, "Resorte bajo la cabeza",
     "Arandela Belleville (cónica) M5 entre cabeza y oreja.\n"
     "+ mantiene la precarga aunque el PLA fluya\n− suma 1 mm al apilado; no es una D")
ax.set_xlim(-6, 17)
ax.add_patch(Rectangle((-4, -4), 4, 8, fc=STEEL, ec=INK, lw=.8))
ax.add_patch(Polygon([(0, -5.5), (0.5, -5.5), (1.3, -2.6), (0.8, -2.6)], fc=RED, ec=INK, lw=.6))
ax.add_patch(Polygon([(0, 5.5), (0.5, 5.5), (1.3, 2.6), (0.8, 2.6)], fc=RED, ec=INK, lw=.6))
ax.add_patch(Rectangle((1.3, -R), 4, 2 * R, fc=A, ec=INK, lw=.8))
for k in range(6):
    ax.add_patch(Rectangle((5.3 + k * .8, -R), .8, 2 * R, fc=B_SOFT if k % 2 == 0 else A_SOFT,
                           ec=INK, lw=.4))
ax.add_patch(Rectangle((10.3, -R), 6.7, 2 * R, fc=B, ec=INK, lw=.8))
ax.add_patch(Rectangle((0, -2.5), 10.5, 5, fc=STEEL, ec=INK, lw=.6, alpha=.9))
ax.text(-2, 7.6, "cabeza", fontsize=7.5, ha="center")
ax.text(1.0, -8.6, "Belleville", fontsize=7.5, color=RED)
ax.text(13.6, 7.6, "nudillo", fontsize=7.5, ha="center")
ax.text(3.3, 7.6, "oreja", fontsize=7.5, ha="center")

# 10 · muesca sobre pasador
ax = axs[9]
base(ax, 10, "Muesca sobre pasador de acero",
     "Pasador Ø2 metido en la placa, a lo largo de la pila;\ncada D tiene una muesca que lo abraza.\n"
     "+ traba en acero, centrada y sin juego\n− pasador en cada placa; ajuste fino de la muesca")
ax.add_patch(Polygon(d_mejorada(bultos=()), fc=B_SOFT, ec=INK, lw=1))
ax.add_patch(Circle((8.25, 0), 1.05, fc=BG, ec="none"))
placas(ax)
ax.add_patch(Circle((8.25, 0), 1.0, fc=STEEL, ec=INK, lw=.8))
apriete(ax); agujero(ax)
nota(ax, (7.4, 0.6), "pasador Ø2", (1.5, 6.5))

fig.suptitle("10 variantes de arandela para la pila — vista a lo largo del eje (mm). "
             "Celeste: trabada con B · naranja claro: trabada con A",
             x=0.125, ha="left", fontsize=13, fontweight="bold", color=INK)
fig.subplots_adjust(hspace=0.42, wspace=0.08)
for ext in ("png", "svg"):
    fig.savefig(AQUI / f"variantes_arandela.{ext}", dpi=130, bbox_inches="tight", facecolor=BG)
