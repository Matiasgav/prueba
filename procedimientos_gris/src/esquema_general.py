"""Esquema general de conexiones del sistema GRIS (SVG).

Mismo estilo que «Esquema de conexión para ensayo ELCID» (P. Pelegrina, 03/07/2025):
rectángulos simples, líneas finas y etiquetas sobre las líneas.
A la izquierda lo que va en el estator; a la derecha, los equipos de la mesa de trabajo.
Uso: python3 esquema_general.py  → img/esquema_general.svg
"""
import math
from pathlib import Path

AQUI = Path(__file__).parent
W, H = 1300, 880
NEG, VERDE, NAR, ARNES = "#000000", "#21B33A", "#E36C0A", "#D9DDE0"
el = []


def linea(pts, color=NEG, ancho=1.4, trazo=None):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    da = f' stroke-dasharray="{trazo}"' if trazo else ""
    el.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-linejoin="miter"{da}/>')


def texto(x, y, t, tam=12, ancla="start", color=NEG, rot=None):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    for i, renglon in enumerate(t.split("\n")):
        el.append(f'<text x="{x}" y="{y + i * (tam + 2)}" font-size="{tam}" fill="{color}" text-anchor="{ancla}"{tr}>{renglon}</text>')


def caja(x, y, w, h):
    el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.4"/>')


def circulo(c, r, relleno="none"):
    el.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{r}" fill="{relleno}" stroke="{NEG}" stroke-width="1.4"/>')


def borne(x, y):
    el.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.4"/>')


def pc(x, y, nombre):
    """Notebook: pantalla y base, en línea simple."""
    el.append(f'<rect x="{x}" y="{y}" width="110" height="70" rx="4" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.6"/>')
    el.append(f'<rect x="{x + 7}" y="{y + 7}" width="96" height="56" fill="none" stroke="{NEG}" stroke-width="1"/>')
    el.append(f'<path d="M{x - 8},{y + 82} L{x},{y + 70} H{x + 110} L{x + 118},{y + 82} Z" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.6"/>')
    texto(x + 55, y - 10, nombre, 14, "middle")


def tierra_horizontal(y, x0, x1, saltos):
    """Tierra horizontal de x0 hacia x1 (< x0) con puentes sobre las líneas que cruza."""
    d = f"M{x0},{y}"
    for xs in sorted(saltos, reverse=True):
        d += f" H{xs + 6} A6,6 0 0 0 {xs - 6},{y}"
    d += f" H{x1}"
    el.append(f'<path d="{d}" fill="none" stroke="{VERDE}" stroke-width="2.6"/>')


def simbolo_tierra(x, y):
    linea([(x, y - 14), (x, y)], NEG)
    for i, w in enumerate((14, 9, 4)):
        el.append(f'<line x1="{x - w}" y1="{y + i * 5}" x2="{x + w}" y2="{y + i * 5}" stroke="{NEG}" stroke-width="1.4"/>')


# ---------------------------------------------------------------- título y marco
el.append(f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="none" stroke="{NEG}" stroke-width="1"/>')
texto(W / 2, 85, "ESQUEMA GENERAL DE CONEXIONES – SISTEMA GRIS", 30, "middle")

# ================================================================ ESTATOR (izquierda)
c1, c2, R, r = (200, 620), (330, 530), 82, 50          # caras frontal y trasera, radio exterior y del entrehierro
ax, ay = c2[0] - c1[0], c2[1] - c1[1]
n = math.hypot(ax, ay)
nx, ny = -ay / n, ax / n
circulo(c2, R)
for s_ in (1, -1):
    linea([(c1[0] + s_ * R * nx, c1[1] + s_ * R * ny), (c2[0] + s_ * R * nx, c2[1] + s_ * R * ny)])
circulo(c1, R)
circulo(c1, r)
texto(95, 520, "Núcleo", 14, "middle")
texto(95, 536, "estatórico", 14, "middle")

# robot dentro del entrehierro (parte superior)
rbx, rby = c1[0] - 20, c1[1] - r + 4
caja(rbx, rby + 4, 40, 15)
caja(rbx, rby, 40, 3)
texto(c1[0], c1[1] + 12, "Robot", 13, "middle")

# arrollamiento de excitación: entra por la cara trasera, recorre el entrehierro (oculto) y vuelve por fuera
pt, pf = (c2[0], c2[1] + 22), (c1[0], c1[1] + 30)
linea([(650, 524.5), (650, 560), (420, 560), pt], NAR, 2.4)
linea([pt, pf], NAR, 2.4, "7 5")
linea([pf, (140, 740), (140, 770), (800, 770), (800, 755), (820, 755)], NAR, 2.4)
texto(480, 763, "Arrollamiento de excitación", 12, "middle")

# puesta a tierra del núcleo
linea([(c1[0], c1[1] + R), (c1[0], c1[1] + R + 10)], VERDE, 2.6)
simbolo_tierra(c1[0], c1[1] + R + 24)

# ================================================================ MESA DE TRABAJO (derecha)
# control box y PC
caja(600, 200, 150, 110)
texto(675, 190, "Control box", 14, "middle")
pc(850, 190, "PC GRIS")
pc(1010, 190, "PC EL CID")
linea([(750, 230), (850, 230)])
texto(800, 223, "USB", 11.5, "middle")
linea([(750, 265), (846, 265)])
texto(800, 258, "Ethernet", 11.5, "middle")

# tablero EL CID
caja(600, 430, 150, 90)
texto(675, 470, "Tablero", 13, "middle")
texto(675, 486, "EL CID", 13, "middle")
linea([(675, 310), (675, 430)])
texto(683, 378, "Señal de posición", 11.5)
linea([(750, 500), (1140, 500), (1140, 225), (1120, 225)])
texto(950, 493, "USB", 11.5, "middle")

# arnés del robot: cable principal + señal del captor, juntos hasta la mesa
banda = [(206, rby), (206, 285), (556, 285)]
linea(banda, ARNES, 16)
linea([(202, rby), (202, 280), (600, 280)])                       # cable principal → control box
linea([(210, rby), (210, 290), (560, 290), (560, 480), (600, 480)])  # señal del captor → tablero EL CID
texto(380, 268, "Arnés del robot (cable principal y señal del captor)", 12, "middle")
texto(568, 350, "Señal del\ncaptor", 11.5)

# zapatilla y red
zx, zy = 860, 400
caja(zx, zy, 120, 34)
for i in range(4):
    el.append(f'<rect x="{zx + 6 + i * 29}" y="{zy + 7}" width="21" height="20" fill="#FFFFFF" stroke="{NEG}" stroke-width="1"/>')
texto(zx - 8, zy + 34, "Zapatilla", 13, "end")
caja(1030, 382, 45, 70)
texto(1057, 417, "RED", 14, "middle", rot=-90)
linea([(zx + 120, 417), (1030, 417)], NEG, 2)

# alimentaciones (una toma por equipo)
linea([(750, 295), (875, 295), (875, zy)])
linea([(905, 272), (905, zy)])
linea([(1065, 272), (1065, 335), (965, 335), (965, zy)])
linea([(750, 470), (935, 470), (935, zy + 34)])
texto(812, 289, "Alimentación", 11, "middle")
texto(1015, 329, "Alimentación", 11, "middle")
texto(843, 486, "Alimentación", 11, "middle")

# tierras: principal (zapatilla → núcleo) y del tablero EL CID
tierra_horizontal(412, zx, 480, [675, 560])
linea([(480, 412), (480, c2[1]), (c2[0] + R, c2[1])], VERDE, 2.6)
texto(770, 405, "Tierra principal", 11.5, "middle")
linea([(750, 445), (870, 445), (870, zy + 34)], VERDE, 2.6)
texto(810, 459, "Tierra tablero", 11, "middle")

# circuito de excitación
borne(650, 520)
borne(700, 520)
texto(708, 545, "I excitación", 11)
linea([(700, 524.5), (700, 705), (820, 705)], NEG, 2)
caja(820, 680, 120, 100)
coil = "M880,700 " + " ".join("a7,6 0 1 1 0,12" for _ in range(5))
el.append(f'<path d="{coil}" fill="none" stroke="{NEG}" stroke-width="1.4"/>')
linea([(895, 698), (869, 762)])
el.append(f'<path d="M869,762 l-1,-9 l7,4 z" fill="{NEG}"/>')
texto(826, 742, "0–250 V", 11)
texto(934, 742, "220 V", 11, "end")
texto(880, 802, "Variac", 14, "middle")
linea([(940, 730), (1000, 730)], NEG, 2)
caja(1000, 690, 90, 80)
texto(1045, 722, "Tablero de", 12, "middle")
texto(1045, 736, "control", 12, "middle")
texto(1045, 750, "del Variac", 12, "middle")
linea([(1090, 730), (1130, 730)], NEG, 2)
caja(1130, 695, 45, 70)
texto(1157, 730, "RED", 14, "middle", rot=-90)

# pie
texto(W - 36, H - 34, "Mecanálisis – 00503-00-EPG001 – 28/10/2026", 11, "end")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Arial, Liberation Sans, Helvetica, sans-serif"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
       + "".join(el) + "</svg>")
salida = AQUI / "img" / "esquema_general.svg"
salida.write_text(svg, encoding="utf-8")
print(salida)
