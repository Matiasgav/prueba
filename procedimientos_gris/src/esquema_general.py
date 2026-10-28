"""Esquema general de conexiones del sistema GRIS (SVG).

Mismo estilo que «Esquema de conexión para ensayo ELCID» (P. Pelegrina, 03/07/2025):
rectángulos simples, líneas finas y etiquetas sobre las líneas.
Uso: python3 esquema_general.py  → img/esquema_general.svg
"""
import math
from pathlib import Path

AQUI = Path(__file__).parent
W, H = 1300, 880
NEG, VERDE, NAR = "#000000", "#21B33A", "#E36C0A"
el = []


def linea(pts, color=NEG, ancho=1.4):
    d = " ".join(f"{x},{y}" for x, y in pts)
    el.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-linejoin="miter"/>')


def texto(x, y, t, tam=12, ancla="start", color=NEG, rot=None):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    for i, renglon in enumerate(t.split("\n")):
        el.append(f'<text x="{x}" y="{y + i * (tam + 2)}" font-size="{tam}" fill="{color}" text-anchor="{ancla}"{tr}>{renglon}</text>')


def caja(x, y, w, h):
    el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.4"/>')


def borne(x, y):
    el.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.4"/>')


def pc(x, y, nombre):
    """Notebook: pantalla y base, en línea simple."""
    el.append(f'<rect x="{x}" y="{y}" width="110" height="70" rx="4" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.6"/>')
    el.append(f'<rect x="{x + 7}" y="{y + 7}" width="96" height="56" fill="none" stroke="{NEG}" stroke-width="1"/>')
    el.append(f'<path d="M{x - 8},{y + 82} L{x},{y + 70} H{x + 110} L{x + 118},{y + 82} Z" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.6"/>')
    texto(x + 55, y - 10, nombre, 14, "middle")


def tierra_salto(y, x0, x1, saltos):
    """Línea de tierra horizontal (de x0 hacia x1 < x0) con puentes sobre los cruces."""
    d = f"M{x0},{y}"
    for xs in sorted(saltos, reverse=True):
        d += f" H{xs + 6} A6,6 0 0 0 {xs - 6},{y}"
    d += f" H{x1}"
    el.append(f'<path d="{d}" fill="none" stroke="{VERDE}" stroke-width="2.6"/>')


# ---------------------------------------------------------------- título y marco
el.append(f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="none" stroke="{NEG}" stroke-width="1"/>')
texto(W / 2, 85, "ESQUEMA GENERAL DE CONEXIONES – SISTEMA GRIS", 30, "middle")

# ---------------------------------------------------------------- robot
caja(120, 240, 90, 50)
caja(120, 224, 90, 9)
caja(120, 297, 90, 9)
texto(165, 212, "Robot", 14, "middle")

# ---------------------------------------------------------------- control box y PC GRIS
caja(330, 200, 150, 120)
texto(405, 190, "Control box", 14, "middle")
pc(610, 200, "PC GRIS")
linea([(210, 255), (330, 255)])
texto(270, 248, "Cable principal", 11.5, "middle")
linea([(480, 235), (610, 235)])
texto(541, 228, "USB", 11.5, "middle")
linea([(480, 275), (606, 275)])
texto(541, 268, "Ethernet", 11.5, "middle")

# ---------------------------------------------------------------- tablero EL CID y PC EL CID
caja(560, 470, 110, 80)
texto(615, 506, "Tablero de", 12, "middle")
texto(615, 521, "EL CID", 12, "middle")
pc(730, 520, "PC EL CID")
linea([(670, 540), (730, 540)])
texto(700, 533, "USB", 11.5, "middle")

# señales del robot al tablero EL CID
linea([(210, 278), (285, 278), (285, 500), (560, 500)])
texto(420, 493, "Señal del captor", 11.5, "middle")
linea([(210, 293), (260, 293), (260, 530), (560, 530)])
texto(420, 523, "Señal de posición", 11.5, "middle")

# ---------------------------------------------------------------- zapatilla y red
zx, zy = 1000, 400
caja(zx, zy, 120, 34)
for i in range(4):
    el.append(f'<rect x="{zx + 6 + i * 29}" y="{zy + 7}" width="21" height="20" fill="#FFFFFF" stroke="{NEG}" stroke-width="1"/>')
texto(zx - 6, zy - 2, "Zapatilla", 14, "end")
caja(1170, 382, 45, 70)
texto(1197, 417, "RED", 14, "middle", rot=-90)
linea([(zx + 120, 417), (1170, 417)], NEG, 2)

# alimentaciones (una toma por equipo)
linea([(455, 200), (455, 150), (1105, 150), (1105, zy)])
texto(760, 143, "Alimentación del control box", 11.5, "middle")
linea([(720, 240), (1075, 240), (1075, zy)])
texto(900, 233, "Alimentación PC GRIS", 11.5, "middle")
linea([(670, 480), (1015, 480), (1015, zy + 34)])
texto(840, 473, "Alimentación tablero EL CID", 11.5, "middle")
linea([(840, 560), (1045, 560), (1045, zy + 34)])
texto(945, 553, "Alimentación PC EL CID", 11.5, "middle")

# ---------------------------------------------------------------- núcleo estatórico (cilindro)
c1, c2, r = (250, 720), (360, 645), 58
ax, ay = c2[0] - c1[0], c2[1] - c1[1]
n = math.hypot(ax, ay)
nx, ny = -ay / n, ax / n
for c in (c2, c1):
    el.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{r}" fill="none" stroke="{NEG}" stroke-width="1.4"/>')
for s in (1, -1):
    linea([(c1[0] + s * r * nx, c1[1] + s * r * ny), (c2[0] + s * r * nx, c2[1] + s * r * ny)])
texto(255, 600, "Núcleo", 14, "middle")
texto(255, 616, "estatórico", 14, "middle")

# arrollamiento de excitación: entra por el entrehierro (trazo oculto) y vuelve por fuera del núcleo
linea([(595, 554.5), (595, 600), (c2[0], 600), c2], NAR, 2.4)
el.append(f'<line x1="{c2[0]}" y1="{c2[1]}" x2="{c1[0]}" y2="{c1[1]}" stroke="{NAR}" stroke-width="2.4" stroke-dasharray="7 5"/>')
linea([c1, (c1[0] - 45, c1[1] + 31), (c1[0] - 45, 800), (700, 800), (700, 705), (720, 705)], NAR, 2.4)
texto(450, 793, "Arrollamiento de excitación", 12, "middle")

# ---------------------------------------------------------------- circuito de excitación
borne(595, 550)
borne(635, 550)
texto(645, 572, "I excitación", 11)
linea([(635, 554.5), (635, 655), (720, 655)], NEG, 2)
# Variac (autotransformador)
caja(720, 630, 120, 100)
coil = "M780,650 " + " ".join("a7,6 0 1 1 0,12" for _ in range(5))
el.append(f'<path d="{coil}" fill="none" stroke="{NEG}" stroke-width="1.4"/>')
linea([(795, 648), (769, 712)])
el.append(f'<path d="M769,712 l-1,-9 l7,4 z" fill="{NEG}"/>')
texto(726, 692, "0–250 V", 11)
texto(834, 692, "220 V", 11, "end")
texto(780, 752, "Variac", 14, "middle")
linea([(840, 680), (900, 680)], NEG, 2)
caja(900, 640, 90, 80)
texto(945, 672, "Tablero de", 12, "middle")
texto(945, 686, "control", 12, "middle")
texto(945, 700, "del Variac", 12, "middle")
linea([(990, 680), (1030, 680)], NEG, 2)
caja(1030, 645, 45, 70)
texto(1057, 680, "RED", 14, "middle", rot=-90)

# ---------------------------------------------------------------- puesta a tierra
tierra_salto(410, zx, 100, [285, 260])
linea([(100, 410), (100, 830)], VERDE, 2.6)
linea([(100, c1[1]), (c1[0] - r, c1[1])], VERDE, 2.6)
for i, w in enumerate((14, 9, 4)):
    el.append(f'<line x1="{100 - w}" y1="{830 + i * 5}" x2="{100 + w}" y2="{830 + i * 5}" stroke="{NEG}" stroke-width="1.4"/>')
texto(640, 403, "Tierra principal de la zapatilla (desde el núcleo estatórico)", 11.5, "middle")
linea([(615, 470), (615, 425), (zx, 425)], VERDE, 2.6)
texto(800, 442, "Tierra del tablero EL CID", 11.5, "middle")

# pie
texto(W - 36, H - 34, "Mecanálisis – 00503-00-EPG001 – 28/10/2026", 11, "end")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Arial, Liberation Sans, Helvetica, sans-serif"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
       + "".join(el) + "</svg>")
salida = AQUI / "img" / "esquema_general.svg"
salida.write_text(svg, encoding="utf-8")
print(salida)
