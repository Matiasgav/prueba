"""Esquema general de conexiones del sistema GRIS (SVG).

Mismo estilo que «Esquema de conexión para ensayo ELCID» (P. Pelegrina, 03/07/2025):
líneas finas y etiquetas sobre las líneas. El control box, el tablero EL CID y el
tablero de excitación se dibujan a partir de fotos, con sus colores y proporciones.
A la izquierda lo que va en el estator; a la derecha, los equipos de la mesa de trabajo.
Uso: python3 esquema_general.py  → img/esquema_general.svg
"""
import math
from pathlib import Path

AQUI = Path(__file__).parent
W, H = 1500, 1050
NEG, VERDE, NAR, VIOL, ARNES = "#000000", "#21B33A", "#E36C0A", "#7B3FA0", "#D9DDE0"
fondo, frente, lineas = [], [], []   # capas: ilustraciones, rótulos; las líneas se dibujan aparte (con puentes)


# ---------------------------------------------------------------- primitivas
def rect(capa, x, y, w, h, relleno, borde="none", ancho=1, rx=0):
    capa.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{relleno}" stroke="{borde}" stroke-width="{ancho}"/>')


def circ(capa, cx, cy, r, relleno, borde="none", ancho=1):
    capa.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{relleno}" stroke="{borde}" stroke-width="{ancho}"/>')


def texto(x, y, t, tam=12, ancla="start", color=NEG, rot=None, peso="normal", capa=None):
    capa = frente if capa is None else capa
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
    for i, renglon in enumerate(t.split("\n")):
        capa.append(f'<text x="{x:.1f}" y="{y + i * (tam + 2):.1f}" font-size="{tam}" fill="{color}" text-anchor="{ancla}"'
                    f' font-weight="{peso}"{tr}>{renglon}</text>')


def linea(pts, color=NEG, ancho=1.4, trazo=None, puentes=True):
    lineas.append({"pts": pts, "color": color, "ancho": ancho, "trazo": trazo, "puentes": puentes})


def caja(x, y, w, h):
    rect(fondo, x, y, w, h, "#FFFFFF", NEG, 1.4)


def rejilla(x, y, w, h, paso):
    rect(fondo, x, y, w, h, "#0B0B0B")
    for i in range(int(w // paso)):
        for j in range(int(h // paso)):
            circ(fondo, x + paso / 2 + i * paso, y + paso / 2 + j * paso, paso * 0.3, "#3C3C3C")


def etiqueta(x, y, w, h, t, rot=0):
    rect(fondo, x, y, w, h, "#F4F4F4", "#9A9A9A", 0.6)
    texto(x + w / 2, y + h / 2 + 2.2, t, 6, "middle", "#222", rot, capa=fondo)


# ---------------------------------------------------------------- ilustraciones (fracciones medidas sobre las fotos)
def control_box(x, y, w):
    h = w * 1445 / 1185
    X = lambda f: x + f * w
    Y = lambda f: y + f * h
    rect(fondo, x, y, w, h, "#C3C7CA", "#878C90", 1.2, 3)          # marco de aluminio
    rect(fondo, X(0.03), Y(0.025), w * 0.94, h * 0.95, "#141414")  # tapa negra
    for fx, fy in ((0.07, 0.05), (0.93, 0.05), (0.07, 0.95), (0.93, 0.95)):
        circ(fondo, X(fx), Y(fy), 1.4, "#555")
    rect(fondo, X(0.211), Y(0.107), w * 0.165, h * 0.063, "#050505", "#555", 0.8, 1.5)   # entrada IEC
    rect(fondo, X(0.245), Y(0.12), w * 0.097, h * 0.037, "#1E1E1E")
    rect(fondo, X(0.232), Y(0.194), w * 0.097, h * 0.069, "#050505", "#444", 0.8)        # llave
    rect(fondo, X(0.246), Y(0.205), w * 0.069, h * 0.047, "#D7262E")
    rejilla(X(0.705), Y(0.180), w * 0.185, h * 0.176, 3.2)                              # ventilador
    rejilla(X(0.165), Y(0.772), w * 0.447, h * 0.10, 3.2)                               # rejilla inferior
    rect(fondo, X(0.802), Y(0.509), w * 0.105, h * 0.038, "#A9AEB2", "#6F7478", 0.8, 1)  # conector del cable principal
    circ(fondo, X(0.840), Y(0.593), w * 0.022, "#B5B9BC", "#6F7478", 0.8)               # BNC posición
    circ(fondo, X(0.840), Y(0.593), w * 0.009, "#333")
    rect(fondo, X(0.810), Y(0.644), w * 0.072, h * 0.086, "#0A0A0A", "#666", 0.8, 1.5)  # USB
    rect(fondo, X(0.828), Y(0.672), w * 0.036, h * 0.03, "#2C5BD6")
    rect(fondo, X(0.823), Y(0.768), w * 0.067, h * 0.073, "#B9BDC0", "#6F7478", 0.8, 1)  # etherCON
    rect(fondo, X(0.836), Y(0.787), w * 0.041, h * 0.035, "#2A2A2A")
    return {"iec": (X(0.211), Y(0.1385)), "principal": (X(0.907), Y(0.528)), "bnc": (X(0.862), Y(0.593)),
            "usb": (X(0.882), Y(0.687)), "eth": (X(0.890), Y(0.805)), "h": h}


def tablero_elcid(x, y, w):
    h = w * 522 / 424
    X = lambda f: x + f * w
    Y = lambda f: y + f * h
    rect(fondo, x, y, w, h, "#DEDEDA", "#9A9A96", 1.2, 2)          # caja pintada
    rect(fondo, X(0.03), Y(0.022), w * 0.94, h * 0.957, "#262626")  # burlete
    rect(fondo, X(0.047), Y(0.038), w * 0.92, h * 0.929, "#BDC0C1")  # panel galvanizado
    for fx in (0.10, 0.48, 0.90):
        for fy in (0.07, 0.94):
            circ(fondo, X(fx), Y(fy), 1.3, "#3A3A3A")
    rect(fondo, X(0.814), Y(0.092), w * 0.094, h * 0.134, "#111", "#444", 0.8, 3)        # USB-B
    rect(fondo, X(0.838), Y(0.13), w * 0.046, h * 0.06, "#555")
    etiqueta(X(0.918), Y(0.11), w * 0.04, h * 0.10, "USB", 90)
    for fy, nombre in ((0.523, "Señal posición 0-10V"), (0.690, "Captor magnético")):
        circ(fondo, X(0.854), Y(fy), w * 0.035, "#CDD0D2", "#777", 0.8)
        circ(fondo, X(0.854), Y(fy), w * 0.015, "#333")
        etiqueta(X(0.918), Y(fy - 0.075), w * 0.04, h * 0.15, nombre, 90)
    circ(fondo, X(0.146), Y(0.661), w * 0.026, "#A8ABAD", "#666", 0.8)                  # borne de tierra
    circ(fondo, X(0.146), Y(0.661), w * 0.011, "#777")
    etiqueta(X(0.19), Y(0.615), w * 0.04, h * 0.10, "Ground", 90)
    rect(fondo, X(0.094), Y(0.805), w * 0.095, h * 0.115, "#0E0E0E", "#444", 0.8, 2)     # entrada IEC
    rect(fondo, X(0.248), Y(0.766), w * 0.125, h * 0.115, "#111", "#444", 0.8)           # llave
    rect(fondo, X(0.268), Y(0.785), w * 0.085, h * 0.077, "#D7262E")
    for fx in (0.618, 0.821):                                                            # bornes banana
        circ(fondo, X(fx), Y(0.866), w * 0.066, "#0D0D0D")
        circ(fondo, X(fx), Y(0.866), w * 0.03, "#C8862E")
        circ(fondo, X(fx), Y(0.866), w * 0.012, "#3A2A10")
    etiqueta(X(0.56), Y(0.935), w * 0.32, h * 0.028, "Corriente de excitación")
    r_b = w * 0.066
    return {"usb": (X(0.861), Y(0.092)), "pos": (X(0.889), Y(0.523)), "captor": (X(0.889), Y(0.690)),
            "ground": (X(0.12), Y(0.661)), "iec": (X(0.094), Y(0.8625)),
            "b1": (X(0.618), Y(0.866) + r_b), "b2": (X(0.821), Y(0.866) + r_b), "h": h}


def tablero_excitacion(x, y, w):
    h = w * 480 / 915
    X = lambda f: x + f * w
    Y = lambda f: y + f * h
    rect(fondo, X(0.528), Y(-0.17), w * 0.109, h * 0.19, "#2D4DB0", "#1D347A", 0.8, 3)  # ficha industrial (sobresale del borde)
    rect(fondo, x, y, w, h, "#E4E5E1", "#9EA09C", 1.2, 2)                               # caja
    rect(fondo, X(0.025), Y(0.04), w * 0.95, h * 0.92, "#D6D8D3")                       # fondo
    circ(fondo, X(0.579), Y(0.167), w * 0.066, "#F3F3F1", "#9A9A9A", 0.8)              # base de la ficha
    circ(fondo, X(0.579), Y(0.167), w * 0.03, "#FFFFFF", "#B0B0B0", 0.6)
    rect(fondo, X(0.20), Y(0.43), w * 0.76, h * 0.035, "#AEB1B3")                       # riel DIN
    # bornera EXCITATION: 7 bornes arriba (1–5 + 2 al tablero EL CID), 5 abajo
    bx0, bx1 = X(0.224), X(0.361)
    paso = (bx1 - bx0) / 7
    rect(fondo, bx0, Y(0.344), bx1 - bx0, h * 0.25, "#1A1A1A")
    for i in range(7):
        rect(fondo, bx0 + i * paso + 0.6, Y(0.344), paso - 1.2, h * 0.06, "#F5F5F2", "#999", 0.5)
        if i < 5:
            rect(fondo, bx0 + i * paso + 0.6, Y(0.534), paso - 1.2, h * 0.06, "#F5F5F2", "#999", 0.5)
            texto(bx0 + (i + 0.5) * paso, Y(0.395), str(i + 1), 5, "middle", "#333", capa=fondo)
            texto(bx0 + (i + 0.5) * paso, Y(0.585), str(i + 1), 5, "middle", "#333", capa=fondo)
    rect(fondo, X(0.245), Y(0.44), w * 0.095, h * 0.05, "#F4F4F4")
    texto(X(0.2925), Y(0.477), "EXCITATION", 5, "middle", "#111", capa=fondo)
    rect(fondo, X(0.372), Y(0.252), w * 0.06, h * 0.446, "#F7F7F7", "#9A9A9A", 0.8)    # interruptor
    rect(fondo, X(0.392), Y(0.43), w * 0.02, h * 0.09, "#1A1A1A")
    rect(fondo, X(0.415), Y(0.27), w * 0.012, h * 0.025, "#2E9B48")
    rect(fondo, X(0.628), Y(0.365), w * 0.104, h * 0.239, "#EDEDED", "#9A9A9A", 0.8)   # bornera AUXILIAR
    for fx in (0.645, 0.69):
        for fy in (0.38, 0.53):
            rect(fondo, X(fx), Y(fy), w * 0.03, h * 0.055, "#FFFFFF", "#999", 0.5)
    etiqueta(X(0.61), Y(0.27), w * 0.13, h * 0.05, "AUXILIAR")
    rect(fondo, X(0.432), Y(0.615), w * 0.426, h * 0.218, "#F7F7F2", "#BBBBB5", 0.8)   # protoboard
    for j in range(5):
        for i in range(36):
            circ(fondo, X(0.445) + i * w * 0.0113, Y(0.65) + j * h * 0.03, 0.5, "#B5B5B0")
    for fy, col in ((0.632, "#D33"), (0.815, "#36C")):
        rect(fondo, X(0.44), Y(fy), w * 0.41, 0.6, col)
    for fx in (0.53, 0.62):                                                            # resistencias
        rect(fondo, X(fx), Y(0.79), w * 0.045, h * 0.025, "#D9B98A", "#A88A5E", 0.5, 2)
        for k in range(3):
            rect(fondo, X(fx) + w * (0.01 + k * 0.01), Y(0.79), 1.2, h * 0.025, ("#7A3B12", "#111", "#C62")[k])
    circ(fondo, X(0.803), Y(0.10), w * 0.012, "#111")                                  # fichas banana
    circ(fondo, X(0.836), Y(0.073), w * 0.012, "#D22")
    rect(fondo, X(0.918), Y(0.4375), w * 0.06, h * 0.0725, "#FAFAFA", "#999", 0.8, 2)  # llave del circuito auxiliar
    return {"ficha": (X(0.637), Y(-0.10)), "t6": bx0 + 5.5 * paso, "t7": bx0 + 6.5 * paso, "fila_sup": Y(0.344),
            "izq": bx0, "y_sup": Y(0.374), "y_inf": Y(0.564), "aux": (X(0.66), Y(0.365)), "h": h}


def pc(x, y, nombre):
    rect(fondo, x, y, 110, 70, "#FFFFFF", NEG, 1.6, 4)
    rect(fondo, x + 7, y + 7, 96, 56, "none", NEG, 1)
    fondo.append(f'<path d="M{x - 8},{y + 82} L{x},{y + 70} H{x + 110} L{x + 118},{y + 82} Z" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.6"/>')
    texto(x + 55, y - 10, nombre, 14, "middle")


def simbolo_tierra(x, y):
    linea([(x, y - 14), (x, y)], NEG, puentes=False)
    for i, w in enumerate((14, 9, 4)):
        fondo.append(f'<line x1="{x - w}" y1="{y + i * 5}" x2="{x + w}" y2="{y + i * 5}" stroke="{NEG}" stroke-width="1.4"/>')


# ================================================================ marco y título
fondo.append(f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="none" stroke="{NEG}" stroke-width="1"/>')
texto(W / 2, 80, "ESQUEMA GENERAL DE CONEXIONES – SISTEMA GRIS", 30, "middle")

# ================================================================ ESTATOR (izquierda)
c1, c2, R, r = (200, 720), (340, 630), 85, 52
ax, ay = c2[0] - c1[0], c2[1] - c1[1]
nx, ny = -ay / math.hypot(ax, ay), ax / math.hypot(ax, ay)
circ(fondo, *c2, R, "none", NEG, 1.4)
for s_ in (1, -1):
    linea([(c1[0] + s_ * R * nx, c1[1] + s_ * R * ny), (c2[0] + s_ * R * nx, c2[1] + s_ * R * ny)], puentes=False)
circ(fondo, *c1, R, "none", NEG, 1.4)
circ(fondo, *c1, r, "none", NEG, 1.4)
texto(85, 600, "Núcleo\nestatórico", 14, "middle")
rby = c1[1] - r + 6
caja(c1[0] - 20, rby + 4, 40, 15)
caja(c1[0] - 20, rby, 40, 3)
texto(c1[0], c1[1] + 12, "Robot", 13, "middle")
linea([(c1[0], c1[1] + R), (c1[0], c1[1] + R + 10)], VERDE, 2.6, puentes=False)
simbolo_tierra(c1[0], c1[1] + R + 24)

# ================================================================ MESA DE TRABAJO (derecha)
cb = control_box(330, 170, 180)
texto(420, 160, "Control box", 14, "middle")
pc(620, 270, "PC GRIS")
pc(780, 270, "PC EL CID")
te = tablero_elcid(800, 440, 190)
texto(895, 432, "Tablero EL CID", 14, "middle")
tx = tablero_excitacion(560, 775, 380)
texto(750, 775 + tx["h"] + 20, "Tablero de excitación", 14, "middle")

zx, zy = 580, 480
caja(zx, zy, 120, 34)
for i in range(4):
    rect(fondo, zx + 6 + i * 29, zy + 7, 21, 20, "#FFFFFF", NEG, 1)
texto(zx + 60, zy + 52, "Zapatilla", 13, "middle")
caja(510, 462, 45, 70)
texto(537, 497, "RED", 14, "middle", rot=-90)
linea([(zx, 497), (555, 497)], NEG, 2)

caja(1060, 790, 120, 100)
coil = "M1120,810 " + " ".join("a7,6 0 1 1 0,12" for _ in range(5))
fondo.append(f'<path d="{coil}" fill="none" stroke="{NEG}" stroke-width="1.4"/>')
linea([(1135, 808), (1109, 872)], puentes=False)
fondo.append(f'<path d="M1109,872 l-1,-9 l7,4 z" fill="{NEG}"/>')
texto(1066, 852, "0–250 V", 11)
texto(1174, 852, "220 V", 11, "end")
texto(1120, 912, "Variac", 14, "middle")
caja(1230, 805, 45, 70)
texto(1257, 840, "RED", 14, "middle", rot=-90)
linea([(1180, 840), (1230, 840)], NEG, 2)

# ================================================================ conexiones
# arnés del robot: cable principal + señal del captor, juntos desde el robot
fondo.append(f'<polyline points="200,{rby} 200,124 545,124" fill="none" stroke="{ARNES}" stroke-width="18"/>')
linea([(204, rby), (204, 128), (545, 128), (545, cb["principal"][1]), cb["principal"]])
linea([(196, rby), (196, 120), (1015, 120), (1015, te["captor"][1]), te["captor"]])
texto(370, 108, "Arnés del robot (cable principal y señal del captor)", 12, "middle")
texto(1023, 400, "Señal del\ncaptor", 11.5)
# control box
linea([cb["bnc"], (590, cb["bnc"][1]), (590, 215), (1000, 215), (1000, te["pos"][1]), te["pos"]])
texto(800, 208, "Señal de posición", 11.5, "middle")
linea([cb["usb"], (620, cb["usb"][1])])
texto(565, cb["usb"][1] - 6, "USB", 11.5, "middle")
linea([cb["eth"], (616, cb["eth"][1])])
texto(565, cb["eth"][1] - 6, "Ethernet", 11.5, "middle")
# PC EL CID ↔ tablero EL CID
linea([(835, 352), (835, 415), (te["usb"][0], 415), te["usb"]])
texto(885, 409, "USB", 11.5, "middle")
# alimentaciones desde la zapatilla
linea([cb["iec"], (315, cb["iec"][1]), (315, 450), (595, 450), (595, zy)])
linea([(655, 352), (655, zy)])
linea([(810, 352), (810, 462), (685, 462), (685, zy)])
linea([te["iec"], (625, te["iec"][1]), (625, zy + 34)])
texto(450, 444, "Alimentación", 11, "middle")
texto(748, 456, "Alimentación", 11, "middle")
texto(720, te["iec"][1] - 6, "Alimentación", 11, "middle")
# tierras
linea([(586, zy + 34), (586, c2[1]), (c2[0] + R, c2[1])], VERDE, 2.6)
texto(500, c2[1] - 6, "Tierra principal", 11.5, "middle")
linea([te["ground"], (602, te["ground"][1]), (602, zy + 34)], VERDE, 2.6)
texto(715, te["ground"][1] - 6, "Tierra tablero EL CID", 11, "middle")
# corriente de magnetización: tablero de excitación (bornes 6 y 7) → tablero EL CID
linea([te["b1"], (te["b1"][0], 700), (tx["t6"], 700), (tx["t6"], tx["fila_sup"])], NAR, 2)
linea([te["b2"], (te["b2"][0], 710), (tx["t7"], 710), (tx["t7"], tx["fila_sup"])], NAR, 2)
texto(820, 694, "Corriente de excitación", 11.5, "middle")
# Variac → ficha del tablero de excitación
linea([(1060, 815), (1030, 815), (1030, tx["ficha"][1]), tx["ficha"]], NEG, 2)
texto(930, tx["ficha"][1] - 6, "Salida del Variac", 11.5, "middle")
# cable de 5 hilos: sale de la fila superior, pasa por el entrehierro y vuelve a la fila inferior
pt, pf = (c2[0], c2[1] + 25), (c1[0], c1[1] + 25)
linea([(tx["izq"], tx["y_sup"]), (520, tx["y_sup"]), (520, 668), (380, 668), pt], NAR, 3)
linea([pt, pf], NAR, 3, "7 5", puentes=False)
linea([pf, (140, 830), (140, 900), (600, 900), (600, tx["y_inf"]), (tx["izq"], tx["y_inf"])], NAR, 3)
texto(330, 893, "Cable de excitación de 5 hilos (espiras en serie)", 12, "middle")
# espira auxiliar: de una ranura a la bornera AUXILIAR (por arriba)
pa = (c1[0] - r + 6, c1[1])
circ(frente, *pa, 3, VIOL)
linea([pa, (110, pa[1]), (110, 1008), (1000, 1008), (1000, 760), (tx["aux"][0], 760), tx["aux"]], VIOL, 1.8)
texto(330, 1001, "Espira auxiliar", 12, "middle")

texto(W - 36, H - 30, "Mecanálisis – 00503-00-EPG001 – 28/10/2026", 11, "end")


# ================================================================ líneas con puentes en los cruces
def segmentos(pts):
    return list(zip(pts[:-1], pts[1:]))


def render(l, verticales):
    pts = l["pts"]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in segmentos(pts):
        if l["puentes"] and abs(y0 - y1) < 0.1 and abs(x1 - x0) > 1:
            dirx = 1 if x1 > x0 else -1
            cruces = sorted((vx for (vx, va, vb, dueño) in verticales
                             if dueño is not l and min(x0, x1) + 8 < vx < max(x0, x1) - 8 and va + 3 < y0 < vb - 3),
                            key=lambda vx: dirx * vx)
            for vx in cruces:
                d += f" L{vx - dirx * 6:.1f},{y0:.1f} A6,6 0 0 {1 if dirx > 0 else 0} {vx + dirx * 6:.1f},{y0:.1f}"
        d += f" L{x1:.1f},{y1:.1f}"
    da = f' stroke-dasharray="{l["trazo"]}"' if l["trazo"] else ""
    return f'<path d="{d}" fill="none" stroke="{l["color"]}" stroke-width="{l["ancho"]}" stroke-linejoin="miter"{da}/>'


verticales = [(x0, min(y0, y1), max(y0, y1), l) for l in lineas for (x0, y0), (x1, y1) in segmentos(l["pts"])
              if abs(x0 - x1) < 0.1 and abs(y1 - y0) > 1]
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Arial, Liberation Sans, Helvetica, sans-serif"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
       + "".join(fondo) + "".join(render(l, verticales) for l in lineas) + "".join(frente) + "</svg>")
salida = AQUI / "img" / "esquema_general.svg"
salida.write_text(svg, encoding="utf-8")
print(salida)
