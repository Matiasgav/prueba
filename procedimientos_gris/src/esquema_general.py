"""Esquema general de conexiones del sistema GRIS (SVG).

Basado en «Esquema de conexión para ensayo ELCID» (P. Pelegrina, 03/07/2025),
00503-00-EPG002 y la información de campo del sistema GRIS.
Uso: python3 esquema_general.py  → img/esquema_general.svg
"""
import base64
import math
from pathlib import Path

AQUI = Path(__file__).parent
W, H = 1700, 1200
NAR, AZ, NEG, VERDE, VIOL = "#E36C0A", "#4F6F7A", "#2B2F33", "#2E9E3E", "#7B3FA0"
GRIS_L, FONDO = "#C9D2D5", "#F6F8F8"
el = []
HALO = 'paint-order="stroke" stroke="#FFFFFF" stroke-width="4" stroke-linejoin="round"'


# ---------------------------------------------------------------- primitivas
def linea(pts, color=NEG, ancho=2.4, trazo=False, r=8):
    """Polilínea ortogonal con esquinas redondeadas."""
    pts = [p for i, p in enumerate(pts) if i == 0 or math.dist(p, pts[i - 1]) > 0.5]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1, l2 = math.dist((x0, y0), (x1, y1)), math.dist((x1, y1), (x2, y2))
        k = min(r, l1 / 2, l2 / 2)
        a = (x1 - (x1 - x0) / l1 * k, y1 - (y1 - y0) / l1 * k)
        b = (x1 + (x2 - x1) / l2 * k, y1 + (y2 - y1) / l2 * k)
        d += f" L{a[0]:.1f},{a[1]:.1f} Q{x1:.1f},{y1:.1f} {b[0]:.1f},{b[1]:.1f}"
    d += f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
    da = ' stroke-dasharray="9 6"' if trazo else ""
    el.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-linecap="round"{da}/>')


def texto(x, y, t, tam=13, color=NEG, ancla="start", peso="normal", estilo="normal", halo=False):
    h = f" {HALO}" if halo else ""
    for i, renglon in enumerate(t.split("\n")):
        el.append(f'<text x="{x}" y="{y + i * (tam + 3)}" font-size="{tam}" fill="{color}" text-anchor="{ancla}"'
                  f' font-weight="{peso}" font-style="{estilo}"{h}>{renglon}</text>')


def punto(x, y, color=NEG, r=4):
    el.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')


def borne(x, y, color=NEG):
    el.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#FFFFFF" stroke="{color}" stroke-width="2.2"/>')


def nro(x, y, n, color=AZ):
    el.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#FFFFFF" stroke="{color}" stroke-width="2"/>')
    texto(x, y + 4.5, str(n), 12, color, "middle", "bold")


def zona(x, y, w, h, titulo, derecha=False):
    el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{FONDO}" stroke="{GRIS_L}" stroke-width="1.5"/>')
    ancho = len(titulo) * 7.6 + 28
    x0 = x + w - 16 - ancho if derecha else x + 16
    el.append(f'<rect x="{x0}" y="{y - 11}" width="{ancho}" height="22" rx="11" fill="{AZ}"/>')
    texto(x0 + ancho / 2, y + 4.5, titulo, 12, "#FFFFFF", "middle", "bold")


def equipo(x, y, w, h, titulo, sub="", acento=AZ, enchufe=False):
    el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#FFFFFF" stroke="{acento}" stroke-width="1.8" filter="url(#sombra)"/>')
    el.append(f'<path d="M{x},{y + 26} V{y + 7} Q{x},{y} {x + 7},{y} H{x + w - 7} Q{x + w},{y} {x + w},{y + 7} V{y + 26} Z" fill="{acento}"/>')
    texto(x + w / 2, y + 18, titulo, 14, "#FFFFFF", "middle", "bold")
    if sub:
        texto(x + w / 2, y + 26 + (h - 26) / 2 + 4 - (8 if "\n" in sub else 0), sub, 12, "#55666C", "middle")
    if enchufe:
        tx, ty = x + w - 52, y + h - 9
        el.append(f'<rect x="{tx}" y="{ty}" width="46" height="18" rx="9" fill="{NEG}"/>')
        texto(tx + 23, ty + 13, "220 V", 11, "#FFFFFF", "middle", "bold")


def polar(r, ang):
    return CX + r * math.cos(math.radians(ang)), CY - r * math.sin(math.radians(ang))


# ---------------------------------------------------------------- definiciones
logo = base64.b64encode((AQUI / "img" / "logo_mecanalisis.jpeg").read_bytes()).decode()
defs = """<defs>
<filter id="sombra" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="1.5" stdDeviation="1.8" flood-color="#000" flood-opacity="0.12"/></filter>
<radialGradient id="gEstator" cx="50%" cy="45%" r="55%"><stop offset="0.6" stop-color="#E4E8EA"/><stop offset="1" stop-color="#C8D0D3"/></radialGradient>
<radialGradient id="gRotor" cx="45%" cy="40%" r="60%"><stop offset="0" stop-color="#D2D8DA"/><stop offset="1" stop-color="#9FAAAE"/></radialGradient>
</defs>"""

# ---------------------------------------------------------------- marco y zonas
el.append(f'<rect x="12" y="12" width="{W - 24}" height="{H - 24}" fill="none" stroke="{AZ}" stroke-width="1.5"/>')
zona(30, 290, 620, 690, "GENERADOR – ROTOR MONTADO", derecha=True)
zona(680, 40, 950, 430, "PUESTO DE OPERACIÓN")
zona(680, 610, 950, 320, "EXCITACIÓN DEL NÚCLEO")

# ---------------------------------------------------------------- generador
CX, CY = 340, 610
el.append(f'<circle cx="{CX}" cy="{CY}" r="250" fill="url(#gEstator)" stroke="{AZ}" stroke-width="2"/>')
el.append(f'<circle cx="{CX}" cy="{CY}" r="165" fill="#FFFFFF" stroke="{AZ}" stroke-width="1.8"/>')
for ang in range(0, 360, 10):  # ranuras
    a = math.radians(ang)
    el.append(f'<rect x="-3.5" y="-24" width="7" height="24" fill="#FFFFFF" stroke="#8C9CA1" stroke-width="1"'
              f' transform="translate({CX + 188 * math.cos(a):.1f},{CY - 188 * math.sin(a):.1f}) rotate({90 - ang})"/>')
el.append(f'<circle cx="{CX}" cy="{CY}" r="138" fill="url(#gRotor)" stroke="{AZ}" stroke-width="2"/>')
texto(CX, CY + 10, "ROTOR", 15, "#3E4A4F", "middle", "bold")
texto(CX, CY + 30, "aislado de tierra en un extremo", 12, "#3E4A4F", "middle")
texto(*polar(207, 232), "Núcleo estatórico", 13, "#3E4A4F", "middle", "bold")

# rampa sobre el rotor
p0, p1 = polar(142, 62), polar(142, 118)
el.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} A142,142 0 0 1 {p0[0]:.1f},{p0[1]:.1f}" fill="none" stroke="#7D8E94" stroke-width="7" stroke-linecap="square"/>')
# robot
rx, ry = polar(151, 90)
el.append(f'<rect x="{rx - 30}" y="{ry - 10}" width="60" height="20" rx="4" fill="{NEG}"/>')
el.append(f'<rect x="{rx - 9}" y="{ry - 10}" width="18" height="5" fill="{NAR}"/>')
for dx in (-20, 20):
    el.append(f'<circle cx="{rx + dx}" cy="{ry + 5}" r="4" fill="#5C666B"/>')

# espira auxiliar (ranura a 150°)
ei, ee = polar(178, 150), polar(278, 150)
linea([ei, ee], VIOL, 1.8, True)
punto(*ei, VIOL, 5)
punto(*ee, VIOL, 5)
texto(ee[0] - 8, ee[1] + 30, "Espira\nauxiliar", 12, VIOL, "end", "bold")

# arrollamiento de excitación (a 120° del robot)
bi, be = polar(151, -30), polar(282, -30)
linea([bi, be], NAR, 1.8, True)
for c in (bi, be):
    for dx, dy in ((-5, 2), (5, 2), (0, -6)):
        punto(c[0] + dx, c[1] + dy, NAR, 4.5)


def rotulo(desde, hasta, t, color=NEG, ancla="start"):
    el.append(f'<polyline points="{desde[0]:.1f},{desde[1]:.1f} {hasta[0]:.1f},{hasta[1]:.1f}" fill="none" stroke="{color}" stroke-width="1"/>')
    punto(*desde, color, 2.5)
    texto(hasta[0] + (4 if ancla == "start" else -4), hasta[1] + 4, t, 12.5, color, ancla, "bold", halo=True)


rotulo((rx + 30, ry - 4), (470, 345), "Robot GRIS\n(captor Chattock, detector WTT)")
rotulo(polar(142, 112), (170, 360), "Rampa", NEG, "end")
rotulo((be[0] - 4, be[1] + 10), (640, 860), "Arrollamiento de excitación\n(a 120° del robot)", NAR, "end")

# ---------------------------------------------------------------- equipos
equipo(50, 110, 190, 72, "Multímetro (V)", "Tensión por espira")
equipo(700, 80, 150, 100, "PC GRIS", "Software de control\ndel robot", enchufe=True)
equipo(980, 80, 160, 100, "Control box", "Control del robot", enchufe=True)
equipo(1180, 300, 220, 110, "Tablero EL CID", "Adquisición (DAQ)", enchufe=True)
equipo(1460, 300, 160, 100, "PC EL CID", "Software ELCSoft", enchufe=True)
equipo(1400, 80, 160, 70, "Zapatilla", "con barra de tierra", NEG)
equipo(1435, 190, 90, 56, "RED", "220 V", NEG)
equipo(1180, 820, 220, 80, "Variac", "Salida 0–250 V", NAR)
equipo(1440, 830, 150, 70, "Tablero control", "del Variac", NEG)
equipo(1470, 715, 90, 56, "RED", "220 V", NEG)

# ---------------------------------------------------------------- señales y datos
# 1 cable principal: robot → control box
linea([(rx - 15, ry - 10), (rx - 15, 230), (1030, 230), (1030, 180)], AZ)
texto(420, 225, "Cable principal GRIS", 12, AZ, halo=True)
nro(560, 230, 1)
# 5 captor y 6 posición: robot → tablero EL CID
linea([(rx, ry - 10), (rx, 250), (1155, 250), (1155, 340), (1180, 340)], AZ)
texto(700, 246, "Señal del captor Chattock", 12, AZ, halo=True)
nro(640, 250, 5)
linea([(rx + 15, ry - 10), (rx + 15, 270), (1135, 270), (1135, 375), (1180, 375)], AZ)
texto(700, 286, "Señal de posición axial", 12, AZ, halo=True)
nro(870, 270, 6)
# 2 USB y 3 Ethernet: PC GRIS ↔ control box
for y, nombre, n in ((115, "USB", 2), (155, "Ethernet", 3)):
    linea([(850, y), (980, y)], AZ)
    punto(850, y, AZ, 3)
    punto(980, y, AZ, 3)
    texto(935, y - 6, nombre, 11.5, AZ, "middle", halo=True)
    nro(878, y, n)
# 4 USB: tablero EL CID ↔ PC EL CID
linea([(1400, 350), (1460, 350)], AZ)
texto(1430, 344, "USB", 11.5, AZ, "middle", halo=True)
nro(1430, 370, 4)
# 8 espira auxiliar → multímetro
linea([ee, (ee[0], 182)], VIOL, 2.2)
nro(ee[0], 250, 8, VIOL)

# ---------------------------------------------------------------- alimentación
linea([(1480, 190), (1480, 150)], NEG, 2.6)
nro(1380, 115, 10, NEG)
linea([(1515, 771), (1515, 830)], NEG, 2.6)
linea([(1400, 865), (1440, 865)], NEG, 2.6)

# ---------------------------------------------------------------- circuito de excitación (7)
borne(1240, 410, NAR)
borne(1340, 410, NAR)
texto(1290, 432, "I excitación", 11.5, NAR, "middle", halo=True)
borne(1290, 820, NAR)
borne(1340, 820, NAR)
linea([(be[0] + 8, be[1] - 6), (be[0] + 8, 745), (1240, 745), (1240, 415.5)], NAR, 2.8)
linea([(1340, 415.5), (1340, 814.5)], NAR, 2.8)
linea([(be[0] - 2, be[1] + 8), (be[0] - 2, 790), (1290, 790), (1290, 814.5)], NAR, 2.8)
nro(1000, 745, 7, NAR)
nro(1000, 790, 7, NAR)
el.append(f'<circle cx="820" cy="745" r="16" fill="#FFFFFF" stroke="{NAR}" stroke-width="2.4"/>')
texto(820, 750.5, "A", 15, NAR, "middle", "bold")
texto(820, 712, "Pinza amperométrica", 11.5, NAR, "middle", halo=True)

# ---------------------------------------------------------------- puesta a tierra (9)
linea([(CX, CY + 250), (CX, 955), (1650, 955), (1650, 115), (1560, 115)], VERDE, 3)
for i, w in enumerate((24, 15, 6)):
    el.append(f'<line x1="{CX - w}" y1="{963 + i * 6}" x2="{CX + w}" y2="{963 + i * 6}" stroke="{VERDE}" stroke-width="2.5"/>')
texto(760, 948, "Tierra principal desde el núcleo estatórico (puesta a tierra única)", 12, VERDE, peso="bold", halo=True)
nro(1180, 955, 9, VERDE)
borne(1375, 300, VERDE)
linea([(1375, 294.5), (1375, 265), (1415, 265), (1415, 150)], VERDE, 2.6)
texto(1367, 284, "Ground", 11, VERDE, "end", "bold", halo=True)

# ---------------------------------------------------------------- leyenda
ly = 1000
el.append(f'<rect x="30" y="{ly}" width="440" height="170" rx="8" fill="#FFFFFF" stroke="{GRIS_L}"/>')
texto(46, ly + 22, "REFERENCIAS", 12, AZ, peso="bold")
items = [(AZ, "Señales y datos"), (NAR, "Circuito de excitación"), (VERDE, "Puesta a tierra"),
         (VIOL, "Espira auxiliar"), (NEG, "Alimentación 220 V CA")]
for i, (c, nombre) in enumerate(items):
    y0 = ly + 46 + i * 24
    linea([(46, y0), (96, y0)], c, 3)
    texto(108, y0 + 4.5, nombre, 12.5)
el.append(f'<rect x="270" y="{ly + 37}" width="40" height="17" rx="8.5" fill="{NEG}"/>')
texto(290, ly + 49.5, "220 V", 10, "#FFFFFF", "middle", "bold")
texto(318, ly + 50, "Alimentado desde\nla zapatilla", 12)
borne(290, ly + 94, NEG)
texto(318, ly + 98, "Borne de conexión", 12)
nro(290, ly + 125, "n")
texto(318, ly + 129, "Nº de cable (ver lista)", 12)

# ---------------------------------------------------------------- lista de cables
cables = [
    ("1", "Robot", "Control box", "Cable principal GRIS"),
    ("2", "PC GRIS", "Control box", "USB"),
    ("3", "PC GRIS", "Control box", "Ethernet"),
    ("4", "Tablero EL CID", "PC EL CID", "USB"),
    ("5", "Robot", "Tablero EL CID", "Señal del captor Chattock"),
    ("6", "Robot", "Tablero EL CID", "Señal de posición axial"),
    ("7", "Variac / Tablero EL CID", "Arrollamiento", "Cable de excitación (50 m)"),
    ("8", "Espira auxiliar", "Multímetro", "Cable de espira auxiliar"),
    ("9", "Núcleo / Tablero EL CID", "Zapatilla", "Tierra (verde/amarillo)"),
    ("10", "Zapatilla", "Equipos 220 V", "Alimentación (IEC C13)"),
]
tx, ty, cw = 490, ly, [34, 160, 130, 196]
el.append(f'<rect x="{tx}" y="{ty}" width="{sum(cw)}" height="170" rx="8" fill="#FFFFFF" stroke="{GRIS_L}"/>')
el.append(f'<path d="M{tx},{ty + 22} V{ty + 8} Q{tx},{ty} {tx + 8},{ty} H{tx + sum(cw) - 8} Q{tx + sum(cw)},{ty} {tx + sum(cw)},{ty + 8} V{ty + 22} Z" fill="#DAE0E2"/>')
x = tx
for c, t in zip(cw, ["Nº", "Desde", "Hasta", "Cable / función"]):
    texto(x + 8, ty + 15.5, t, 11.5, NEG, peso="bold")
    x += c
for i, fila in enumerate(cables):
    y = ty + 36 + i * 13.4
    x = tx
    for c, t in zip(cw, fila):
        texto(x + 8, y, t, 10.8, NEG, peso="bold" if c == cw[0] else "normal")
        x += c

# ---------------------------------------------------------------- rótulo
bx, by, bw, bh = 1040, ly, 640 - 30, 170
el.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#FFFFFF" stroke="{AZ}" stroke-width="1.5"/>')
el.append(f'<image href="data:image/jpeg;base64,{logo}" x="{bx + 14}" y="{by + 14}" width="190" height="53"/>')
el.append(f'<line x1="{bx + 220}" y1="{by}" x2="{bx + 220}" y2="{by + 80}" stroke="{AZ}" stroke-width="1"/>')
texto(bx + 236, by + 32, "ESQUEMA GENERAL DE CONEXIONES", 17, NAR, peso="bold")
texto(bx + 236, by + 56, "Sistema GRIS – inspección visual, EL CID y WTT", 13, "#55666C")
el.append(f'<line x1="{bx}" y1="{by + 80}" x2="{bx + bw}" y2="{by + 80}" stroke="{AZ}" stroke-width="1"/>')
campos = [("DOCUMENTO", "00503-00-EPG001 – Figura 1"), ("REV.", "00"), ("FECHA", "28/10/2026"), ("ESCALA", "S/E")]
anchos = [250, 90, 140, bw - 480]
x = bx
for (et, val), a in zip(campos, anchos):
    if x > bx:
        el.append(f'<line x1="{x}" y1="{by + 80}" x2="{x}" y2="{by + 142}" stroke="{AZ}" stroke-width="1"/>')
    texto(x + 12, by + 104, et, 10.5, "#55666C", peso="bold")
    texto(x + 12, by + 132, val, 14, NEG, peso="bold")
    x += a
el.append(f'<line x1="{bx}" y1="{by + 142}" x2="{bx + bw}" y2="{by + 142}" stroke="{AZ}" stroke-width="1"/>')
texto(bx + 12, by + 161, "Basado en «Esquema de conexión para ensayo ELCID» (P. Pelegrina, 03/07/2025).", 10.5, "#55666C")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Calibri, Carlito, Arial, sans-serif">{defs}<rect width="{W}" height="{H}" fill="#FFFFFF"/>'
       + "".join(el) + "</svg>")
salida = AQUI / "img" / "esquema_general.svg"
salida.write_text(svg, encoding="utf-8")
print(salida)
