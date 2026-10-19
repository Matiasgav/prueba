"""Análisis de la traba de las arandelas: cuánto torque aguanta cada forma
antes de que el borde de la arandela (o la cara de la placa) se aplaste.

Modelo: cada arandela recibe rozamiento por sus dos caras y lo pasa a su
eslabón por la traba. Con la pila de espesor total P y n arandelas, cada una
carga ~2T/n y su traba aguanta sigma * t * K, donde K = ∫ (brazo) d(largo de
contacto) [mm²]. Como n * t = P:

    T_max = sigma * P * K / 2        (no depende del espesor de cada arandela)

Uso: python3 analisis_traba.py
"""

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

from dibujar_arandelas import B, B_SOFT, A_SOFT, STEEL, RED, INK, MUTED, R, CARA, arco

AQUI = Path(__file__).resolve().parent
SIGMA = 40e6          # Pa: aplastamiento admisible de un borde de PLA impreso
P = 4.8e-3            # m: espesor total de la pila
MU, F_PRE = 0.3, 625  # rozamiento PLA/PLA y precarga con 0,5 N·m de apriete
R_EFF, R_CAB = 5.14e-3, 3.35e-3


def k_cara_plana(z0, z1):
    """Cara plana contra la placa: la fuerza es normal a la placa y el brazo es
    la altura z del punto de contacto. Al girar apoya solo una mitad."""
    return (z1**2 - z0**2) / 2


def k_lengueta(r0, r1):
    """Costado de una lengüeta metida en un bolsillo: fuerza tangencial, brazo r."""
    return (r1**2 - r0**2) / 2


OPCIONES = [
    # clave, nombre, K [mm²], nota
    ("actual", "D actual\nR1,5 + hendidura 7", k_cara_plana(3.5, 5.5),
     "apoya en 2 mm a 3,5–5,5 del centro"),
    ("sin_hend", "D sin hendidura\n(R1,5)", k_cara_plana(0, 5.5), ""),
    ("viva", "D de esquina viva\nsin hendidura", k_cara_plana(0, 7.0),
     "solo reimprimir arandelas"),
    ("perno", "Perno pasante Ø3\na 5 mm del eje", 3 * 5.0,
     "el «palito» axial: brazo corto"),
    ("talon", "D viva\n+ talón", 2 * k_cara_plana(0, 7.0),
     "las trabas llenan toda la pila"),
    ("lengueta", "Lengüeta en bolsillo\nde la placa (r 8→13)", k_lengueta(8, 13),
     "empuje tangencial, no se escapa"),
    ("leng_talon", "Lengüeta en bolsillo\n+ talón", 2 * k_lengueta(8, 13), ""),
]


def t_max(k_mm2):
    return SIGMA * P * k_mm2 * 1e-6 / 2


def t_rozamiento(caras):
    return MU * F_PRE * (caras * R_EFF + R_CAB)


def d_viva():
    return arco(0, 0, R, 90, 270) + [(7.8, -R), (7.8, R)]


def d_r15(hend=0.0):
    pts = arco(0, 0, R, 90, 270) + arco(6.3, -5.5, 1.5, -90, 0)
    if hend:
        for i in range(1, 60):
            z = -3.5 + 7 * i / 60
            pts.append((7.8 - hend * (1 + math.cos(2 * math.pi * z / 7)) / 2, z))
    return pts + arco(6.3, 5.5, 1.5, 0, 90)


def boceto(ax, clave):
    ax.set_aspect("equal")
    ax.set_xlim(-8.5, 14.5)
    ax.set_ylim(-8.5, 8.5)
    ax.axis("off")
    bolsillo = clave in ("lengueta", "leng_talon")
    ax.add_patch(Rectangle((CARA, -8.5), 6.5, 17, fc=B, alpha=.85, ec="none"))
    if bolsillo:
        ax.add_patch(Rectangle((CARA, -3.1), 5.2, 6.2, fc="white", ec=INK, lw=.6))
    if clave == "actual":
        perfil = d_r15(0.5)
    elif clave == "sin_hend":
        perfil = d_r15()
    elif clave == "perno":
        perfil = None
    else:
        perfil = d_viva()
    if bolsillo:
        perfil = arco(0, 0, R, 25, 335) + [(13, -3), (13, 3)]
    if perfil:
        ax.add_patch(Polygon(perfil, fc=B_SOFT, ec=INK, lw=.9))
    else:
        ax.add_patch(Circle((0, 0), R, fc=B_SOFT, ec=INK, lw=.9))
        ax.add_patch(Circle((0, 5), 1.5, fc=STEEL, ec=INK, lw=.7))
    if clave in ("talon", "leng_talon"):
        if clave == "talon":
            talon = arco(0, 0, R + .2, -90, 90)[::-1] + [(7.8, -R), (7.8, R)]
        else:
            talon = [(7.3, -3), (13, -3), (13, 3), (7.3, 3)]
        ax.add_patch(Polygon(talon, fc=B, alpha=.45, ec="none"))
    ax.add_patch(Circle((0, 0), 2.6, fc="white", ec=INK, lw=.8))
    # zonas de contacto que trabajan
    c = dict(color=RED, lw=3.2, solid_capstyle="round")
    if clave == "actual":
        ax.plot([7.8, 7.8], [3.5, 5.5], **c)
    elif clave == "sin_hend":
        ax.plot([7.8, 7.8], [0.3, 5.5], **c)
    elif clave in ("viva", "talon"):
        ax.plot([7.8, 7.8], [0.3, 7.0], **c)
    elif clave == "perno":
        ax.add_patch(Circle((0, 5), 1.5, fc="none", ec=RED, lw=2.2))
    else:
        ax.plot([8.1, 12.9], [3.0, 3.0], **c)


def main():
    fig = plt.figure(figsize=(17, 10.5))
    gs = fig.add_gridspec(2, len(OPCIONES), height_ratios=[1, 1.35], hspace=0.35,
                          wspace=0.05)
    for i, (clave, nombre, k, nota) in enumerate(OPCIONES):
        ax = fig.add_subplot(gs[0, i])
        boceto(ax, clave)
        ax.set_title(f"{i + 1} · {nombre}", fontsize=9.5, fontweight="bold", color=INK)
        ax.text(3, -10.2, f"K = {k:.0f} mm²".replace(".", ","), ha="center",
                fontsize=9, color=INK)
        if nota:
            ax.text(3, -12.0, nota, ha="center", fontsize=7.8, color=MUTED)

    ax = fig.add_subplot(gs[1, :])
    nombres = [f"{i + 1} · {n.replace(chr(10), ' ')}" for i, (_, n, _, _) in enumerate(OPCIONES)]
    valores = [t_max(k) for _, _, k, _ in OPCIONES]
    y = list(range(len(OPCIONES)))[::-1]
    ax.barh(y, valores, height=0.55, color=B, edgecolor="white", linewidth=2)
    for yi, v, (_, _, k, _) in zip(y, valores, OPCIONES):
        rel = v / valores[0]
        ax.text(v + 0.12, yi, f"{v:.1f} N·m".replace(".", ",") +
                ("" if rel < 1.05 else f"   ×{rel:.1f}".replace(".", ",")),
                va="center", fontsize=9.5, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(nombres, fontsize=9.5, color=INK)
    t7 = t_rozamiento(7)
    ax.axvline(t7, color=RED, lw=1.2, ls="--")
    ax.text(t7 + 0.1, len(OPCIONES) - 0.45,
            f"rozamiento con 6 D y 0,5 N·m de apriete ≈ {t7:.1f} N·m".replace(".", ","),
            color=RED, fontsize=9, va="top")
    ax.set_xlim(0, 12)
    ax.set_xlabel("Torque de la articulación que aguanta la traba antes de aplastarse "
                  "(N·m) — σ = 40 MPa, pila de 4,8 mm", fontsize=9.5, color=INK)
    ax.grid(axis="x", color="#d3d8da", lw=.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED)

    fig.suptitle("Traba de las arandelas: torque máximo antes de que se abollen. "
                 "En rojo, la zona de contacto que trabaja.",
                 x=0.06, ha="left", fontsize=13, fontweight="bold", color=INK)
    for ext in ("png", "svg"):
        fig.savefig(AQUI / f"analisis_traba.{ext}", dpi=130, bbox_inches="tight",
                    facecolor="white")
    for (clave, nombre, k, _), v in zip(OPCIONES, valores):
        print(f"{clave:11s} K={k:6.1f} mm²  Tmax={v:5.2f} N·m  x{v / valores[0]:.1f}")
    print(f"rozamiento 7 caras: {t7:.2f} N·m")


if __name__ == "__main__":
    main()
