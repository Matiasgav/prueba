"""Plano 2D de la arandela D con hendidura central. Uso: python3 dibujar_d_hendidura.py"""

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

from dibujar_arandelas import B, B_SOFT, RED, INK, MUTED, R, CARA, arco

AQUI = Path(__file__).resolve().parent
LARGO = 7.8          # cara plana, a 0.2 de la placa
RC = 1.5             # radio de las esquinas
H_ANCHO, H_PROF = 5.0, 0.5
D_AGUJERO = 5.2


def perfil_d():
    """Medio círculo R7, esquinas R1.5 y cara plana con hendidura coseno:
    entra y sale tangente, sin aristas."""
    pts = arco(0, 0, R, 90, 270)
    pts += arco(LARGO - RC, -R + RC, RC, -90, 0)
    n = 60
    for i in range(n + 1):
        z = -H_ANCHO / 2 + H_ANCHO * i / n
        pts.append((LARGO - H_PROF * (1 + math.cos(2 * math.pi * z / H_ANCHO)) / 2, z))
    pts += arco(LARGO - RC, R - RC, RC, 0, 90)
    return pts


def cota(ax, p0, p1, txt, off=(0, 0), color=INK, fs=8.5, rot=0):
    ax.annotate("", p0, p1, arrowprops=dict(arrowstyle="<->", lw=.8, color=color,
                                            shrinkA=0, shrinkB=0))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], txt,
            ha="center", va="center", fontsize=fs, color=color, rotation=rot,
            bbox=dict(fc="white", ec="none", pad=1))


def main():
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(17, 6.6),
                                     gridspec_kw=dict(width_ratios=[1.15, 1, 0.8]))
    for ax in (a1, a2, a3):
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor(MUTED)

    # 1 · plano acotado
    ax = a1
    ax.set_title("1 · Arandela D: plano", loc="left", fontsize=11, fontweight="bold")
    ax.set_xlim(-10, 12.5)
    ax.set_ylim(-10.5, 10.5)
    ax.add_patch(Polygon(perfil_d(), fc=B_SOFT, ec=INK, lw=1.2))
    ax.add_patch(Circle((0, 0), D_AGUJERO / 2, fc="white", ec=INK, lw=1))
    ax.plot([-8.5, 9.5], [0, 0], color=MUTED, lw=.5, ls="-.")
    ax.plot([0, 0], [-8.5, 8.5], color=MUTED, lw=.5, ls="-.")
    cota(ax, (-9, -R), (-9, R), "14", off=(-.6, 0), rot=90)
    ax.plot([-9.3, 0], [R, R], color=MUTED, lw=.4)
    ax.plot([-9.3, 0], [-R, -R], color=MUTED, lw=.4)
    cota(ax, (-R, -9), (LARGO, -9), "14,8", off=(0, -.6))
    ax.plot([-R, -R], [-9.3, 0], color=MUTED, lw=.4)
    ax.plot([LARGO, LARGO], [-9.3, -R], color=MUTED, lw=.4)
    cota(ax, (0, 8.6), (LARGO, 8.6), "7,8", off=(0, .6))
    ax.plot([LARGO, LARGO], [R, 8.9], color=MUTED, lw=.4)
    ax.text(-1.8, 1.1, "Ø5,2", fontsize=8.5, ha="center")
    ax.annotate("R7", (-R * .707, R * .707), (-8.5, 7.8), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=.7))
    ax.annotate("R1,5", (LARGO - .44, R - .44), (10.0, 8.6), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", lw=.7))
    ax.annotate("hendidura\n5 × 0,5", (LARGO - .5, 0), (9.0, -4.5), fontsize=8.5,
                color=RED, arrowprops=dict(arrowstyle="->", color=RED, lw=.8))
    ax.set_xlabel("Espesor según la pila elegida (0,4 hoy). Agujero concéntrico con el R7.",
                  fontsize=8.5, color=INK)

    # 2 · detalle de la hendidura
    ax = a2
    ax.set_title("2 · Detalle de la hendidura (×6)", loc="left", fontsize=11,
                 fontweight="bold")
    ax.set_xlim(5.6, 9.0)
    ax.set_ylim(-4.0, 4.0)
    ax.add_patch(Polygon(perfil_d(), fc=B_SOFT, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((CARA, -5), 2, 10, fc=B, alpha=.85, ec="none"))
    ax.text(8.5, 2.9, "placa B", color="white", rotation=90, ha="center", fontsize=9)
    ax.plot([LARGO, LARGO], [-3.6, 3.6], color=MUTED, lw=.5, ls=":")
    cota(ax, (8.3, -2.5), (8.3, 2.5), "5", off=(0, 0), color="white", fs=9)
    ax.texts[-1].set_bbox(dict(fc=B, ec="none", pad=1))
    ax.plot([LARGO, 8.4], [-2.5, -2.5], color=MUTED, lw=.4)
    ax.plot([LARGO, 8.4], [2.5, 2.5], color=MUTED, lw=.4)
    cota(ax, (LARGO - .5, -.0), (LARGO, 0), "", color=RED)
    ax.text(LARGO - .9, 0, "0,5", color=RED, fontsize=9, ha="center", va="center")
    cota(ax, (LARGO, -3.3), (CARA, -3.3), "", fs=8)
    ax.text(LARGO + .1, -3.75, "luz 0,2", fontsize=8.5, ha="center")
    ax.text(6.1, 2.9, "entra y sale tangente:\nsin aristas", fontsize=8.5, color=INK)
    ax.set_xlabel("Perfil coseno: el fondo y los dos bordes son curvas suaves.",
                  fontsize=8.5, color=INK)

    # 3 · cómo apoya
    ax = a3
    ax.set_title("3 · Cómo apoya en la placa", loc="left", fontsize=11, fontweight="bold")
    ax.set_xlim(-8.5, 11)
    ax.set_ylim(-10.5, 10.5)
    ax.add_patch(Rectangle((LARGO, -10), 3, 20, fc=B, alpha=.85, ec="none"))
    ax.add_patch(Polygon(perfil_d(), fc=B_SOFT, ec=INK, lw=1))
    ax.add_patch(Circle((0, 0), D_AGUJERO / 2, fc="white", ec=INK, lw=1))
    for z0, z1 in ((2.5, R - RC), (-(R - RC), -2.5)):
        ax.plot([LARGO, LARGO], [z0, z1], color=RED, lw=4, solid_capstyle="round")
    ax.text(-7.8, -7.3, "Ya asentada, la D apoya en los dos\ntramos planos de 3 mm a los lados\nde la hendidura.",
            fontsize=8.5, color=INK, va="top")
    ax.set_xlabel("Rojo: contacto con la placa una vez tomada la luz de 0,2.", fontsize=8.5,
                  color=INK)

    fig.suptitle("Arandela D con hendidura central — vista a lo largo del eje, mm",
                 x=0.125, ha="left", fontsize=13, fontweight="bold", color=INK)
    for ext in ("png", "svg"):
        fig.savefig(AQUI / f"arandela_D_hendidura.{ext}", dpi=140, bbox_inches="tight",
                    facecolor="white")


if __name__ == "__main__":
    main()
