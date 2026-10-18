"""Lámina 2D con las propuestas de arandela D. Uso: python3 dibujar_arandelas.py"""

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle, RegularPolygon

AQUI = Path(__file__).resolve().parent
A, B = "#d4842a", "#2d6c8c"
A_SOFT, B_SOFT, FREE = "#f0c58f", "#9cc6dc", "#e9e4d8"
STEEL, RED, INK, MUTED = "#9aa3a8", "#c8402f", "#1d2326", "#5d686d"
R, CARA = 7.0, 8.0

plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans",
                     "axes.edgecolor": MUTED})


def arco(cx, cy, r, a0, a1, n=40):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def d_actual(largo=7.8):
    return arco(0, 0, R, 90, 270) + [(largo, -R), (largo, R)]


def d_mejorada(largo=7.9, rc=1.5, bultos=(-4.0, 4.0), h=0.15, rb=0.6):
    pts = arco(0, 0, R, 90, 270)
    pts += arco(largo - rc, -R + rc, rc, -90, 0)
    # cara plana de abajo hacia arriba con dos bultos
    for zb in bultos:
        pts += [(largo, zb - rb)]
        pts += [(largo + h * math.sin(math.pi * i / 12), zb - rb + 2 * rb * i / 12)
                for i in range(1, 12)]
        pts += [(largo, zb + rb)]
    pts += arco(largo - rc, R - rc, rc, 0, 90)
    return pts


def angulo_juego(largo, z):
    # giro hasta que la esquina (largo, z) toca la placa en y = CARA
    r, a = math.hypot(largo, z), math.atan2(z, largo)
    return math.degrees(a - math.acos(CARA / r)) if r > CARA else float("nan")


def placas(ax, ylim=9.5):
    ax.add_patch(Rectangle((CARA, -ylim), 3, 2 * ylim, fc=B, alpha=.85, ec="none"))
    ax.text(CARA + 1.5, ylim - 1, "placa B", color="white", ha="center",
            va="top", rotation=90, fontsize=8)
    ax.add_patch(Rectangle((-CARA - 3, -ylim), 3, 2 * ylim, fc=A, alpha=.85, ec="none"))
    ax.text(-CARA - 1.5, ylim - 1, "placa A", color="white", ha="center",
            va="top", rotation=90, fontsize=8)


def base(ax, titulo):
    ax.set_aspect("equal")
    ax.set_xlim(-11.5, 11.5)
    ax.set_ylim(-9.5, 9.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(titulo, loc="left", fontsize=11, fontweight="bold", color=INK)


def main():
    fig = plt.figure(figsize=(16, 11.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.95], hspace=0.22, wspace=0.12)

    # (a) actual -------------------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    base(ax, "A · D actual: 0,4 mm")
    placas(ax)
    ax.add_patch(Polygon(d_actual(), fc=B_SOFT, ec=INK, lw=1))
    # zonas sin apoyo: la D fuera del círculo de apriete
    for s in (1, -1):
        pts = [(math.sqrt(R**2 - z**2) if abs(z) < R else 0, z)
               for z in [s * (R * i / 30) for i in range(31)]]
        zona = pts + [(7.8, s * R), (7.8, 0)]
        ax.add_patch(Polygon(zona, fc="none", ec=RED, hatch="////", lw=0))
    ax.add_patch(Circle((0, 0), R, fc="none", ec=INK, ls="--", lw=.8))
    ax.add_patch(Circle((0, 0), 2.6, fc="white", ec=INK, lw=1))
    ax.annotate("esquina: primer contacto, r = 10,6 mm, se aplasta", (7.8, -7), (-7.2, -8.6),
                arrowprops=dict(arrowstyle="->", color=RED), color=RED, ha="left", fontsize=8)
    ax.text(1.6, -3.7, "zona sin apoyo\n(fuera de Ø14)", color=RED, fontsize=8)
    ax.text(-6.6, 3.0, "círculo de apriete\nØ14 (oreja / nudillo)", color=MUTED, fontsize=7.5)
    ax.annotate("", (8, 1.2), (7.8, 1.2), arrowprops=dict(arrowstyle="<->", lw=.8))
    ax.text(8.6 - 3.6, 1.6, "luz 0,2", fontsize=8, bbox=dict(fc="white", ec="none", pad=1))
    ax.set_xlabel(f"juego ≈ {angulo_juego(7.8, 7):.1f}°  ·  presión con la cara plana apoyada ≈ 45 MPa"
                  .replace(".", ","), fontsize=9, color=INK)

    # (b) mejorada -----------------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    base(ax, "B · D mejorada: 0,8 mm (propuesta)")
    placas(ax)
    ax.add_patch(Polygon(d_mejorada(), fc=B_SOFT, ec=INK, lw=1))
    ax.add_patch(Circle((0, 0), R, fc="none", ec=INK, ls="--", lw=.8))
    ax.add_patch(Circle((0, 0), 2.6, fc="white", ec=INK, lw=1))
    ax.annotate("esquinas R 1,5", (7.45, 6.55), (2.0, 8.5),
                arrowprops=dict(arrowstyle="->"), fontsize=8)
    for zb in (-4, 4):
        ax.annotate("", (7.95, zb), (4.6, -0.6 if zb < 0 else 0.6),
                    arrowprops=dict(arrowstyle="->", color=RED))
    ax.text(1.0, -0.4, "2 bultos\naplastables", color=RED, fontsize=8, va="center")
    ax.set_xlabel("luz 0,1 + bultos de 0,15 → juego 0 al armar  ·  presión ≈ 22 MPa",
                  fontsize=9, color=INK)

    # (c) detalle del bulto --------------------------------------------------
    ax = fig.add_subplot(gs[0, 2])
    ax.set_aspect("equal")
    ax.set_xlim(6.9, 8.4)
    ax.set_ylim(2.9, 5.2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("C · Detalle del bulto (ampliado)", loc="left", fontsize=11,
                 fontweight="bold", color=INK)
    ax.add_patch(Rectangle((CARA, 2), 1, 4, fc=B, alpha=.85, ec="none"))
    ax.add_patch(Polygon(d_mejorada(), fc=B_SOFT, ec=INK, lw=1.2))
    ax.axvline(7.9, color=MUTED, lw=.6, ls=":")
    ax.annotate("", (7.9, 3.15), (8.0, 3.15), arrowprops=dict(arrowstyle="<->", lw=.8))
    ax.text(7.55, 3.05, "luz 0,1", fontsize=8)
    ax.annotate("", (7.9, 4.0), (8.05, 4.0), arrowprops=dict(arrowstyle="<->", lw=.8, color=RED))
    ax.annotate("bulto de 0,15: pasa 0,05 la placa\ny se aplasta al meter la arandela",
                (7.95, 4.3), (7.0, 4.9), arrowprops=dict(arrowstyle="->", color=RED),
                fontsize=8, color=RED, va="center")
    ax.text(8.2, 4.0, "placa B", color="white", rotation=90, ha="center", va="center")
    ax.text(7.62, 3.55, "largo 1,2", fontsize=8)

    # (d) corte de la pila ----------------------------------------------------
    ax = fig.add_subplot(gs[1, 0:2])
    ax.set_aspect("equal")
    ax.set_xlim(-6.5, 36)
    ax.set_ylim(-26, 9.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("D · Corte por el eje: pila actual y propuesta", loc="left",
                 fontsize=11, fontweight="bold", color=INK)


    def pila(y0, e, etiqueta, colores):
        zona = 6 * e + 0.2
        x = 0
        ax.add_patch(Rectangle((-4, y0 - 4), 4, 8, fc=STEEL, ec=INK, lw=.6))   # cabeza
        ax.add_patch(Rectangle((0, y0 - R), 4, 2 * R, fc=A, ec=INK, lw=.8))    # oreja
        x = 4
        for c in colores:
            ax.add_patch(Rectangle((x, y0 - R), e, 2 * R, fc=c, ec=INK, lw=.5))
            x += e
        xk = 4 + zona
        ax.add_patch(Rectangle((xk, y0 - R), 36 - xk, 2 * R, fc=B, ec=INK, lw=.8))  # nudillo
        ent = 10 - 4 - 6 * e
        ax.add_patch(Rectangle((0, y0 - 2.5), 10, 5, fc=STEEL, ec=INK, lw=.6, alpha=.95))  # hombro
        ax.add_patch(Rectangle((10, y0 - 2), 5, 4, fc=STEEL, ec=INK, lw=.6, hatch="||||"))  # rosca
        ax.text(-5.8, y0, etiqueta, rotation=90, va="center", ha="center", fontsize=9,
                fontweight="bold")
        ax.annotate("", (4, y0 + R + 0.8), (xk, y0 + R + 0.8),
                    arrowprops=dict(arrowstyle="<->", lw=.8))
        ax.text((4 + xk) / 2, y0 + R + 1.2, f"pila {zona:.1f}".replace(".", ","),
                ha="center", fontsize=8)
        ax.text(xk + 0.3, y0 - R + 0.6,
                f"hombro entra {ent:.1f} mm · rosca desde {ent + 0.6:.1f}".replace(".", ","),
                fontsize=8, color="white")


    alt = [B_SOFT, A_SOFT] * 3
    pila(0, 0.4, "actual", alt)
    pila(-17, 0.8, "", alt)
    ax.text(-5.8, -17, "propuesta", rotation=90, va="center", ha="center", fontsize=9,
            fontweight="bold")
    ax.set_xlabel("cabeza · oreja A 4 mm · 6 discos (D·B y D·A alternadas) · nudillo B. "
                  "El torque no cambia: depende de las caras que deslizan, no del espesor.",
                  fontsize=9, color=INK)

    # (e) embrague -----------------------------------------------------------
    ax = fig.add_subplot(gs[1, 2])
    base(ax, "E · Variante tipo embrague")
    placas(ax)
    ax.add_patch(Polygon(d_mejorada(), fc=A_SOFT, ec=INK, lw=1, alpha=.55,
                         closed=True, transform=ax.transData))
    pts = [(-x, y) for x, y in d_mejorada()]
    ax.patches[-1].set_xy(pts)
    ax.add_patch(Circle((0, 0), R, fc=B_SOFT, ec=INK, lw=1))
    ax.add_patch(RegularPolygon((0, 0), 6, radius=4.3, fc=B, ec=INK, lw=1))
    ax.add_patch(Circle((0, 0), 2.7, fc="white", ec=INK, lw=.8))
    ax.text(0, -5.6, "buje hexagonal\ndel nudillo B", ha="center", fontsize=8, color="white")
    ax.text(-6.8, -8.4, "D·A: traba contra placa A", fontsize=8)
    ax.text(1.0, 7.6, "D·B redonda,\nagujero hexagonal", fontsize=8)
    ax.set_xlabel("La traba de B queda dentro de Ø14, apretada\npor ambas caras: no pandea.",
                  fontsize=9, color=INK)

    fig.suptitle("Arandelas de la bisagra de torque — vistas a lo largo del eje, medidas en mm",
                 x=0.125, ha="left", fontsize=13, fontweight="bold", color=INK)
    for ext in ("png", "svg"):
        fig.savefig(AQUI / f"propuestas_arandela_D.{ext}", dpi=150, bbox_inches="tight",
                    facecolor="white")


if __name__ == "__main__":
    main()
