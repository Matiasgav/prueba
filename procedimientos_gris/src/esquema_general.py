"""Esquema general de conexiones del sistema GRIS (SVG).

Basado en «Esquema de conexión para ensayo ELCID» (P. Pelegrina, 03/07/2025) y en
00503-00-EPG002. Las líneas a trazos son conexiones a confirmar.
Uso: python3 esquema_general.py  → img/esquema_general.svg
"""
import math
from pathlib import Path

W, H = 1600, 1100
NAR, GRIS, NEG, VERDE, VIOL = "#E36C0A", "#5B7A84", "#262626", "#2E9E3E", "#7B3FA0"
el = []


def linea(pts, color=NEG, ancho=2.2, trazo=False):
    d = " ".join(f"{x},{y}" for x, y in pts)
    da = ' stroke-dasharray="9 6"' if trazo else ""
    el.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{ancho}"'
              f' stroke-linejoin="round"{da}/>')


def texto(x, y, t, tam=15, color=NEG, ancla="start", peso="normal", estilo="normal"):
    for i, renglon in enumerate(t.split("\n")):
        el.append(f'<text x="{x}" y="{y + i * (tam + 3)}" font-size="{tam}" fill="{color}" text-anchor="{ancla}"'
                  f' font-weight="{peso}" font-style="{estilo}">{renglon}</text>')


def caja(x, y, w, h, titulo, sub="", relleno="#FFFFFF", borde=GRIS):
    el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{relleno}" stroke="{borde}" stroke-width="2"/>')
    cy = y + h / 2 + (0 if sub else 5)
    texto(x + w / 2, cy - (4 if sub else 0), titulo, 16, NEG, "middle", "bold")
    if sub:
        texto(x + w / 2, cy + 16, sub, 13, GRIS, "middle")


def borne(x, y, color=NEG):
    el.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#FFFFFF" stroke="{color}" stroke-width="2"/>')


def polar(r, ang):
    return CX + r * math.cos(math.radians(ang)), CY - r * math.sin(math.radians(ang))


# ---------------- generador (corte transversal) ----------------
CX, CY = 320, 640
el.append('<rect x="40" y="300" width="560" height="640" rx="12" fill="#FAFBFB" stroke="#A6B4B8" stroke-width="1.5" stroke-dasharray="6 5"/>')
texto(420, 328, "GENERADOR", 15, GRIS, peso="bold")
texto(420, 346, "rotor montado, corte transversal", 12, GRIS)
el.append(f'<circle cx="{CX}" cy="{CY}" r="230" fill="#D9DEE0" stroke="{GRIS}" stroke-width="2"/>')
el.append(f'<circle cx="{CX}" cy="{CY}" r="150" fill="#FFFFFF" stroke="{GRIS}" stroke-width="2"/>')
el.append(f'<circle cx="{CX}" cy="{CY}" r="125" fill="#BFC7CA" stroke="{GRIS}" stroke-width="2"/>')
texto(CX, CY - 8, "Rotor", 15, NEG, "middle", "bold")
texto(CX, CY + 12, "(aislado de tierra\nen un extremo)", 13, NEG, "middle")
texto(470, 455, "Núcleo\nestatórico", 14, NEG, "start", "bold")

# rampa sobre el cuerpo del rotor
a0, a1 = 62, 118
p0, p1 = polar(127, a0), polar(127, a1)
el.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} A127,127 0 0 1 {p0[0]:.1f},{p0[1]:.1f}" fill="none" stroke="{GRIS}" stroke-width="7"/>')
texto(CX, CY - 72, "Rampa", 14, NEG, "middle", "bold")
# robot en el entrehierro (ranura inspeccionada)
rx, ry = polar(137, 90)
el.append(f'<rect x="{rx - 30}" y="{ry - 9}" width="60" height="18" rx="3" fill="{NEG}"/>')
texto(rx + 40, ry - 30, "Robot GRIS\n(captor Chattock)", 13, NEG, "start", "bold")

# espira auxiliar (en una ranura)
ei, ee = polar(152, 150), polar(245, 150)
for pt in (ei, ee):
    el.append(f'<circle cx="{pt[0]:.1f}" cy="{pt[1]:.1f}" r="5" fill="{VIOL}"/>')
linea([ei, ee], VIOL, 1.6, True)
texto(ee[0] - 8, ee[1] - 48, "Espira\nauxiliar", 13, VIOL, "end", "bold")

# arrollamiento de excitación a 120° del robot
bi, be = polar(137, -30), polar(258, -30)
for pt in (bi, be):
    for dx, dy in ((-5, 0), (5, 0), (0, -8)):
        el.append(f'<circle cx="{pt[0] + dx:.1f}" cy="{pt[1] + dy:.1f}" r="4.5" fill="{NAR}"/>')
linea([bi, be], NAR, 1.6, True)
texto(560, 850, "Arrollamiento de excitación\n(a 120° del robot)", 13, NAR, "start", "bold")

# tierra del estator
linea([(CX, CY + 230), (CX, 915)], VERDE, 3)
for i, w in enumerate((26, 16, 7)):
    linea([(CX - w, 922 + i * 6), (CX + w, 922 + i * 6)], VERDE, 2.5)

# ---------------- equipos ----------------
caja(50, 120, 200, 60, "Multímetro (V)", "Tensión por espira")
caja(660, 60, 200, 80, "Control box", "Control del robot y la rampa")
caja(1000, 60, 200, 80, "PC portátil", "Software GRIS / ELCSoft")
caja(820, 360, 220, 110, "Tablero EL CID", "Adquisición (DAQ)")
caja(1240, 360, 180, 60, "Zapatilla", "con barra de tierra")
caja(1480, 365, 90, 50, "RED", "220 V")
caja(820, 640, 220, 90, "Variac", "Entrada 220 V / Salida 0–250 V")
caja(840, 800, 180, 60, "Tablero de control", "del Variac")
caja(1100, 805, 90, 50, "RED", "220 V")

# ---------------- señales y datos ----------------
linea([(rx - 10, ry - 9), (rx - 10, 240), (700, 240), (700, 140)], GRIS, 2.4)
texto(420, 236, "Cable principal GRIS", 13, GRIS)
linea([(rx + 10, ry - 9), (rx + 10, 300), (780, 300), (780, 415), (820, 415)], GRIS, 2.4)
texto(420, 293, "Señal del captor Chattock", 13, GRIS)
rp = polar(127, 116)
linea([rp, (rp[0], 220), (680, 220), (680, 140)], GRIS, 2, True)
texto(420, 214, "Control de la rampa (a confirmar)", 13, GRIS, estilo="italic")
linea([(840, 140), (840, 360)], GRIS, 2.4)
texto(848, 250, "Señal de posición\naxial 0–10 V", 13, GRIS)
linea([(1020, 140), (1020, 360)], GRIS, 2.4)
texto(1028, 250, "USB\n(ELCSoft)", 13, GRIS)
linea([(1000, 100), (860, 100)], GRIS, 2, True)
texto(930, 92, "Comunicación", 12, GRIS, "middle", estilo="italic")
texto(930, 120, "(a confirmar)", 12, GRIS, "middle", estilo="italic")
# multímetro sobre la espira auxiliar
linea([ee, (ee[0], 180)], VIOL, 2)

# ---------------- alimentación 220 V ----------------
linea([(1480, 390), (1420, 390)], NEG, 2.6)
linea([(1240, 400), (1040, 400)], NEG, 2.2)
texto(1140, 393, "Alimentación", 13, NEG, "middle")
linea([(1270, 360), (1270, 100), (1200, 100)], NEG, 2.2)
linea([(1330, 360), (1330, 30), (760, 30), (760, 60)], NEG, 2.2)
texto(1045, 24, "Alimentación del control box", 13, NEG, "middle")
texto(1262, 230, "Alimentación\nde la PC", 13, NEG, "end")
linea([(1100, 830), (1020, 830)], NEG, 2.6)
linea([(930, 800), (930, 730)], NEG, 2.6)

# ---------------- circuito de excitación ----------------
borne(870, 470, NAR); borne(990, 470, NAR)
texto(930, 492, "I excitación", 12, NAR, "middle")
linea([(be[0] + 5, be[1] - 7), (760, be[1] - 7), (760, 500), (870, 500), (870, 475)], NAR, 2.6)
linea([(990, 475), (990, 600), (800, 600), (800, 665), (820, 665)], NAR, 2.6)
linea([(be[0], be[1] + 5), (be[0], be[1] + 20), (800, be[1] + 20), (800, 705), (820, 705)], NAR, 2.6)
# pinza amperométrica
px, py = 655, be[1] - 7
el.append(f'<circle cx="{px}" cy="{py}" r="15" fill="#FFFFFF" stroke="{NAR}" stroke-width="2.2"/>')
texto(px, py + 5, "A", 15, NAR, "middle", "bold")
texto(px, py + 36, "Pinza amperométrica\n(corriente de excitación)", 12, NAR, "middle")

# ---------------- puesta a tierra ----------------
linea([(CX, 915), (1400, 915), (1400, 420)], VERDE, 3)
texto(700, 908, "Tierra principal: desde el núcleo estatórico (puesta a tierra única)", 13, VERDE, peso="bold")
borne(1040, 445, VERDE)
linea([(1045, 445), (1380, 445), (1380, 420)], VERDE, 3)
texto(1210, 462, "Tierra del tablero EL CID (borne «Ground»)", 12, VERDE, "middle")

# ---------------- leyenda y rótulo ----------------
lx, ly = 40, 965
el.append(f'<rect x="{lx}" y="{ly}" width="900" height="110" rx="8" fill="#FFFFFF" stroke="#A6B4B8"/>')
texto(lx + 16, ly + 24, "REFERENCIAS", 13, GRIS, peso="bold")
items = [(NEG, False, "Alimentación 220 V CA"), (GRIS, False, "Señales y datos"), (NAR, False, "Circuito de excitación"),
         (VERDE, False, "Puesta a tierra"), (VIOL, False, "Espira auxiliar"), (GRIS, True, "Conexión a confirmar")]
for i, (c, t, nombre) in enumerate(items):
    x0, y0 = lx + 16 + (i % 3) * 290, ly + 52 + (i // 3) * 34
    linea([(x0, y0), (x0 + 50, y0)], c, 3, t)
    texto(x0 + 62, y0 + 5, nombre, 14)
el.append(f'<rect x="960" y="{ly}" width="600" height="110" rx="8" fill="#FFFFFF" stroke="{NAR}" stroke-width="2"/>')
texto(980, ly + 32, "ESQUEMA GENERAL DE CONEXIONES – SISTEMA GRIS", 17, NAR, peso="bold")
texto(980, ly + 58, "Inspección visual, EL CID y WTT con rotor montado", 14, GRIS)
texto(980, ly + 86, "Mecanálisis · 00503-00-EPG001 · Rev. 00 · 28/10/2026", 13, GRIS)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Calibri, Carlito, Arial, sans-serif"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
       + "".join(el) + "</svg>")
salida = Path(__file__).with_name("img") / "esquema_general.svg"
salida.write_text(svg, encoding="utf-8")
print(salida)
