"""Esquema general de conexiones del sistema GRIS (SVG).

Mismo estilo que «Esquema de conexión para ensayo ELCID» (P. Pelegrina, 03/07/2025):
líneas finas y etiquetas sobre las líneas. El control box, el tablero EL CID y el
tablero de excitación se dibujan a partir de fotos, con sus colores y proporciones.
A la izquierda, alimentación; al centro, los tableros; a la derecha, las PC y el estator.
Uso: python3 esquema_general.py  → img/esquema_general.svg
"""
import math
from pathlib import Path

AQUI = Path(__file__).parent
W, H = 1820, 1280
NEG, VERDE, NAR, VIOL, ARNES = "#000000", "#21B33A", "#E36C0A", "#7B3FA0", "#D5DADD"
# colores de los 5 hilos del cable de excitación (mismo color en ambos extremos)
HILOS = ["#7B4A2A", "#1A1A1A", "#8C8C8C", "#2A62C9", "#2E9B48"]
fondo, cables, frente = [], [], []
lineas = []


# ======================================================================== primitivas
def rect(capa, x, y, w, h, relleno, borde="none", ancho=1.0, rx=0):
    capa.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{relleno}" stroke="{borde}" stroke-width="{ancho}"/>')


def circ(capa, cx, cy, r, relleno, borde="none", ancho=1.0):
    capa.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{relleno}" stroke="{borde}" stroke-width="{ancho}"/>')


def poli(capa, pts, color, ancho, cierre=False, relleno="none", extra=""):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    tag = "polygon" if cierre else "polyline"
    capa.append(f'<{tag} points="{d}" fill="{relleno}" stroke="{color}" stroke-width="{ancho}" stroke-linejoin="round" stroke-linecap="round"{extra}/>')


def texto(x, y, t, tam=12, ancla="start", color=NEG, rot=None, peso="normal", capa=None):
    capa = frente if capa is None else capa
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
    for i, renglon in enumerate(t.split("\n")):
        capa.append(f'<text x="{x:.1f}" y="{y + i * (tam + 2):.1f}" font-size="{tam}" fill="{color}" text-anchor="{ancla}"'
                    f' font-weight="{peso}"{tr}>{renglon}</text>')


def linea(pts, color=NEG, ancho=1.4, trazo=None, puentes=True):
    lineas.append({"pts": pts, "color": color, "ancho": ancho, "trazo": trazo, "puentes": puentes})


def tornillo(capa, x, y, r=2.2, color="#3A3A3A"):
    circ(capa, x, y, r, color, "#111", 0.4)
    capa.append(f'<line x1="{x - r * 0.6:.1f}" y1="{y:.1f}" x2="{x + r * 0.6:.1f}" y2="{y:.1f}" stroke="#888" stroke-width="0.5"/>')


def rejilla(x, y, w, h, paso, fondo_c="#0C0C0C", agujero="#3E3E3E"):
    rect(fondo, x, y, w, h, fondo_c, "#2A2A2A", 0.6)
    nx, ny = int(w // paso), int(h // paso)
    ox, oy = x + (w - nx * paso) / 2, y + (h - ny * paso) / 2
    for i in range(nx):
        for j in range(ny):
            circ(fondo, ox + paso / 2 + i * paso, oy + paso / 2 + j * paso, paso * 0.32, agujero)


def etiqueta(x, y, w, h, t, rot=0, tam=6.5):
    rect(fondo, x, y, w, h, "#F7F7F5", "#A0A0A0", 0.5)
    texto(x + w / 2, y + h / 2 + tam * 0.36, t, tam, "middle", "#1E1E1E", rot, capa=fondo)


def bnc(cx, cy, r):
    circ(fondo, cx, cy, r * 1.25, "#8E9396")                     # tuerca
    circ(fondo, cx, cy, r, "#D3D6D8", "#7A7F83", 0.6)
    circ(fondo, cx, cy, r * 0.62, "#B6BABD", "#7A7F83", 0.5)
    circ(fondo, cx, cy, r * 0.28, "#2B2B2B")
    for a in (0, 180):
        circ(fondo, cx + r * 1.05 * math.cos(math.radians(a)), cy + r * 1.05 * math.sin(math.radians(a)), r * 0.16, "#9EA3A6")


def iec(x, y, w, h):
    rect(fondo, x, y, w, h, "#0B0B0B", "#3C3C3C", 0.7, 2)
    poli(fondo, [(x + w * 0.2, y + h * 0.25), (x + w * 0.8, y + h * 0.25), (x + w * 0.8, y + h * 0.62),
                 (x + w * 0.65, y + h * 0.8), (x + w * 0.35, y + h * 0.8), (x + w * 0.2, y + h * 0.62)], "#2E2E2E", 0.6, True, "#1C1C1C")
    for fx, fy in ((0.36, 0.5), (0.5, 0.4), (0.64, 0.5)):
        rect(fondo, x + w * fx - 0.8, y + h * fy - 1.6, 1.6, 3.2, "#A5A5A5")


def llave(x, y, w, h):
    rect(fondo, x, y, w, h, "#0B0B0B", "#3C3C3C", 0.7, 1)
    rect(fondo, x + w * 0.14, y + h * 0.14, w * 0.72, h * 0.72, "#C9202A", "#8E141B", 0.5)
    rect(fondo, x + w * 0.14, y + h * 0.14, w * 0.72, h * 0.3, "#E2434B")
    texto(x + w * 0.5, y + h * 0.42, "I", h * 0.2, "middle", "#F3D0D2", capa=fondo)
    circ(fondo, x + w * 0.5, y + h * 0.7, h * 0.08, "none", "#F3D0D2", 0.6)


# ======================================================================== ilustraciones
def control_box(x, y, w):
    """Control box (foto 2). Fracciones medidas sobre la foto."""
    h = w * 1445 / 1185
    X = lambda f: x + f * w
    Y = lambda f: y + f * h
    rect(fondo, x - 3, y - 3, w + 6, h + 6, "#AEB3B7", "#7D8286", 1.0, 3)        # perfil de aluminio
    rect(fondo, x, y, w, h, "#C9CDD0", "#8C9195", 0.6, 2)
    for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):              # esquineros
        rect(fondo, cx - 7, cy - 7, 14, 14, "#B8BDC1", "#7D8286", 0.6, 3)
    rect(fondo, X(0.028), Y(0.023), w * 0.944, h * 0.954, "#141414")             # tapa negra
    rect(fondo, X(0.028), Y(0.023), w * 0.944, 2, "#2A2A2A")
    for fx, fy in ((0.06, 0.045), (0.94, 0.045), (0.06, 0.955), (0.94, 0.955), (0.5, 0.045), (0.5, 0.955)):
        tornillo(fondo, X(fx), Y(fy), 1.6, "#2E2E2E")
    rect(fondo, x - 6, Y(0.42), 8, h * 0.1, "#B8BDC1", "#7D8286", 0.6, 2)        # cierre lateral
    iec(X(0.211), Y(0.107), w * 0.165, h * 0.063)
    llave(X(0.232), Y(0.194), w * 0.097, h * 0.069)
    rejilla(X(0.705), Y(0.180), w * 0.185, h * 0.176, 3.6)                      # ventilador
    for fx, fy in ((0.705, 0.18), (0.89, 0.18), (0.705, 0.356), (0.89, 0.356)):
        tornillo(fondo, X(fx), Y(fy), 1.8, "#1E1E1E")
    rejilla(X(0.165), Y(0.772), w * 0.447, h * 0.10, 3.6)                       # rejilla inferior
    # conector del cable principal
    rect(fondo, X(0.79), Y(0.500), w * 0.13, h * 0.056, "#8E9396", "#5F6468", 0.6, 1.5)
    rect(fondo, X(0.802), Y(0.509), w * 0.105, h * 0.038, "#C3C7CA", "#6F7478", 0.6, 1)
    for fx in (0.797, 0.913):
        tornillo(fondo, X(fx), Y(0.528), 1.3, "#7A7F83")
    bnc(X(0.840), Y(0.593), w * 0.017)                                           # BNC posición
    rect(fondo, X(0.803), Y(0.640), w * 0.086, h * 0.094, "#0B0B0B", "#555", 0.6, 2)  # USB (Neutrik)
    rect(fondo, X(0.826), Y(0.667), w * 0.04, h * 0.035, "#2C5BD6", "#1B3C93", 0.5)
    for fx, fy in ((0.812, 0.648), (0.880, 0.726)):
        tornillo(fondo, X(fx), Y(fy), 1.1, "#555")
    rect(fondo, X(0.818), Y(0.764), w * 0.077, h * 0.081, "#C2C6C9", "#6F7478", 0.6, 1.5)  # etherCON
    rect(fondo, X(0.836), Y(0.787), w * 0.041, h * 0.035, "#262626")
    for fx, fy in ((0.825, 0.771), (0.888, 0.838)):
        tornillo(fondo, X(fx), Y(fy), 1.1, "#7A7F83")
    return {"iec": (X(0.211), Y(0.1385)), "principal": (X(0.92), Y(0.528)), "bnc": (X(0.862), Y(0.593)),
            "usb": (X(0.889), Y(0.687)), "eth": (X(0.895), Y(0.805)), "h": h}


def tablero_elcid(x, y, w):
    """Tablero EL CID (foto 1). Fracciones medidas sobre la foto."""
    h = w * 522 / 424
    X = lambda f: x + f * w
    Y = lambda f: y + f * h
    rect(fondo, x, y, w, h, "#E2E2DE", "#9C9C98", 1.0, 3)                       # caja pintada
    rect(fondo, x, y, w, 3, "#F0F0EC")
    rect(fondo, X(0.028), Y(0.020), w * 0.944, h * 0.960, "#262626", "none", 0, 2)  # burlete
    rect(fondo, X(0.047), Y(0.038), w * 0.92, h * 0.929, "#BFC2C3")              # panel galvanizado
    for fx in (0.09, 0.30, 0.50, 0.70, 0.91):
        for fy in (0.065, 0.945):
            tornillo(fondo, X(fx), Y(fy), 1.7)
    for fy in (0.25, 0.45, 0.65, 0.85):
        for fx in (0.075, 0.94):
            tornillo(fondo, X(fx), Y(fy), 1.7)
    # USB-B
    rect(fondo, X(0.814), Y(0.092), w * 0.094, h * 0.134, "#121212", "#404040", 0.6, 3)
    poli(fondo, [(X(0.838), Y(0.135)), (X(0.884), Y(0.135)), (X(0.884), Y(0.19)), (X(0.838), Y(0.19))], "#555", 0.5, True, "#3A3A3A")
    etiqueta(X(0.918), Y(0.115), w * 0.04, h * 0.09, "USB", 90)
    for fy, nombre in ((0.523, "Señal posición 0-10V"), (0.690, "Captor magnético")):
        bnc(X(0.854), Y(fy), w * 0.028)
        etiqueta(X(0.918), Y(fy - 0.075), w * 0.04, h * 0.15, nombre, 90, 5.2)
    # borne de tierra
    circ(fondo, X(0.146), Y(0.661), w * 0.03, "#9FA3A6", "#5F6468", 0.6)
    circ(fondo, X(0.146), Y(0.661), w * 0.018, "#C4C7C9", "#7A7F83", 0.5)
    circ(fondo, X(0.146), Y(0.661), w * 0.007, "#555")
    etiqueta(X(0.19), Y(0.615), w * 0.04, h * 0.10, "Ground", 90)
    iec(X(0.094), Y(0.805), w * 0.095, h * 0.115)
    llave(X(0.248), Y(0.766), w * 0.125, h * 0.115)
    for fx in (0.618, 0.821):                                                     # bornes banana
        circ(fondo, X(fx), Y(0.866), w * 0.068, "#0C0C0C", "#333", 0.6)
        circ(fondo, X(fx), Y(0.866), w * 0.045, "#1C1C1C")
        circ(fondo, X(fx), Y(0.866), w * 0.028, "#C98A2E", "#8A5E1C", 0.5)
        circ(fondo, X(fx), Y(0.866), w * 0.011, "#3A2A10")
    etiqueta(X(0.555), Y(0.935), w * 0.33, h * 0.028, "Corriente de excitación", 0, 6)
    rb = w * 0.068
    return {"usb": (X(0.908), Y(0.159)), "pos": (X(0.882), Y(0.523)), "captor": (X(0.882), Y(0.690)),
            "ground": (X(0.116), Y(0.661)), "iec": (X(0.094), Y(0.8625)),
            "b1": (X(0.618), Y(0.866) + rb), "b2": (X(0.821), Y(0.866) + rb), "h": h}


def terminal(x, y, w, h):
    rect(fondo, x, y, w, h, "#F3F3EF", "#9A9A95", 0.5)
    circ(fondo, x + w / 2, y + h * 0.42, min(w, h) * 0.3, "#C8C8C4", "#8A8A86", 0.4)
    fondo.append(f'<line x1="{x + w / 2 - w * 0.18:.1f}" y1="{y + h * 0.42:.1f}" x2="{x + w / 2 + w * 0.18:.1f}" y2="{y + h * 0.42:.1f}" stroke="#777" stroke-width="0.6"/>')


def tablero_excitacion(x, y, w):
    """Tablero de excitación (foto 3, vista superior, sin pasacables)."""
    h = w * 480 / 915
    X = lambda f: x + f * w
    Y = lambda f: y + f * h
    # ficha industrial: tapa azul que sobresale del borde superior
    rect(fondo, X(0.528), Y(-0.17), w * 0.109, h * 0.19, "#2D4DB0", "#1D347A", 0.8, 4)
    rect(fondo, X(0.548), Y(-0.15), w * 0.07, h * 0.05, "#3C61C9")
    rect(fondo, X(0.57), Y(-0.12), w * 0.026, h * 0.035, "#1B2F6E")
    # caja abierta: paredes y fondo
    rect(fondo, x, y, w, h, "#E6E7E3", "#9EA09C", 1.0, 2)
    rect(fondo, X(0.022), Y(0.035), w * 0.956, h * 0.93, "#D4D6D1", "#B5B7B2", 0.6)
    rect(fondo, X(0.022), Y(0.035), w * 0.956, h * 0.03, "#C6C8C3")
    # ficha (base)
    circ(fondo, X(0.579), Y(0.167), w * 0.066, "#F4F4F2", "#9A9A9A", 0.8)
    circ(fondo, X(0.579), Y(0.167), w * 0.045, "#FFFFFF", "#B5B5B5", 0.6)
    for a in (210, 330, 90):
        circ(fondo, X(0.579) + w * 0.022 * math.cos(math.radians(a)), Y(0.167) - w * 0.022 * math.sin(math.radians(a)), w * 0.006, "#C48A2C")
    # riel DIN
    rect(fondo, X(0.20), Y(0.425), w * 0.76, h * 0.045, "#B4B7B9", "#8E9194", 0.5)
    for i in range(30):
        rect(fondo, X(0.21) + i * w * 0.025, Y(0.44), w * 0.012, h * 0.015, "#9DA0A2")
    # bornera EXCITATION: 7 bornes arriba (1–5 y 2 de salida al tablero EL CID), 5 abajo
    bx0, bx1 = X(0.224), X(0.361)
    paso = (bx1 - bx0) / 7
    rect(fondo, bx0 - 1, Y(0.335), bx1 - bx0 + 2, h * 0.27, "#1B1B1B", "#000", 0.5, 1)
    for i in range(7):
        terminal(bx0 + i * paso + 0.5, Y(0.344), paso - 1, h * 0.065)
        texto(bx0 + (i + 0.5) * paso, Y(0.403), str(i + 1) if i < 5 else "", 5, "middle", "#333", capa=fondo)
    for i in range(5):
        terminal(bx0 + i * paso + 0.5, Y(0.530), paso - 1, h * 0.065)
        texto(bx0 + (i + 0.5) * paso, Y(0.525), str(i + 1), 5, "middle", "#DDD", capa=fondo)
    rect(fondo, X(0.237), Y(0.44), w * 0.11, h * 0.055, "#FAFAFA", "#AAA", 0.4)
    texto(X(0.292), Y(0.478), "EXCITATION", 5.4, "middle", "#111", peso="bold", capa=fondo)
    # interruptor termomagnético
    rect(fondo, X(0.372), Y(0.252), w * 0.06, h * 0.446, "#F8F8F8", "#9A9A9A", 0.7, 1.5)
    rect(fondo, X(0.378), Y(0.27), w * 0.048, h * 0.06, "#ECECEC", "#BBB", 0.4)
    rect(fondo, X(0.389), Y(0.41), w * 0.026, h * 0.11, "#E6E6E6", "#999", 0.5, 1)
    rect(fondo, X(0.393), Y(0.415), w * 0.018, h * 0.05, "#1A1A1A")
    rect(fondo, X(0.413), Y(0.275), w * 0.013, h * 0.026, "#2E9B48")
    for fy in (0.29, 0.66):
        circ(fondo, X(0.402), Y(fy), w * 0.007, "#C8C8C4", "#888", 0.4)
    texto(X(0.402), Y(0.36), "Schneider", 3.8, "middle", "#2E9B48", capa=fondo)
    # bornera AUXILIAR
    rect(fondo, X(0.628), Y(0.365), w * 0.104, h * 0.239, "#E9E9E6", "#9A9A9A", 0.7, 1)
    for fx in (0.638, 0.684):
        for fy in (0.38, 0.525):
            terminal(X(fx), Y(fy), w * 0.04, h * 0.065)
    etiqueta(X(0.61), Y(0.27), w * 0.13, h * 0.05, "AUXILIAR", 0, 6)
    # protoboard con las resistencias de calibración
    rect(fondo, X(0.432), Y(0.615), w * 0.426, h * 0.218, "#F8F8F3", "#BDBDB7", 0.7, 1.5)
    for fy, col in ((0.632, "#D33"), (0.645, "#36C"), (0.800, "#D33"), (0.813, "#36C")):
        rect(fondo, X(0.44), Y(fy), w * 0.41, 0.7, col)
    for j in range(6):
        for i in range(40):
            if j != 3:
                circ(fondo, X(0.442) + i * w * 0.0102, Y(0.665) + j * h * 0.022, 0.55, "#B8B8B2")
    for fx in (0.53, 0.62):
        rect(fondo, X(fx), Y(0.77), w * 0.048, h * 0.028, "#D9B98A", "#A88A5E", 0.5, 2.5)
        for k, col in enumerate(("#7A3B12", "#111", "#C62", "#C9A23A")):
            rect(fondo, X(fx) + w * (0.008 + k * 0.009), Y(0.77), 1.3, h * 0.028, col)
        poli(fondo, [(X(fx) - w * 0.012, Y(0.784)), (X(fx), Y(0.784))], "#999", 0.8)
        poli(fondo, [(X(fx + 0.048), Y(0.784)), (X(fx + 0.06), Y(0.784))], "#999", 0.8)
    # fichas banana (medición de tensión por espira) y llave del circuito auxiliar
    for fx, fy, col in ((0.803, 0.10, "#151515"), (0.836, 0.073, "#C8202A")):
        circ(fondo, X(fx), Y(fy), w * 0.013, col, "#000", 0.5)
        circ(fondo, X(fx), Y(fy), w * 0.005, "#777")
    rect(fondo, X(0.918), Y(0.4375), w * 0.06, h * 0.0725, "#FBFBFB", "#999", 0.7, 2)
    rect(fondo, X(0.935), Y(0.452), w * 0.025, h * 0.04, "#E5E5E5", "#AAA", 0.4)
    term_sup = [bx0 + (i + 0.5) * paso for i in range(7)]
    return {"ficha": (X(0.637), Y(-0.02)), "sup": term_sup, "y_sup": Y(0.344), "y_inf": Y(0.595),
            "izq": bx0, "aux": (X(0.658), X(0.704)), "y_aux": Y(0.38), "h": h}


def pc(x, y, nombre):
    rect(fondo, x, y, 110, 70, "#FFFFFF", NEG, 1.6, 4)
    rect(fondo, x + 7, y + 7, 96, 56, "#F4F6F7", NEG, 1)
    fondo.append(f'<path d="M{x - 8},{y + 82} L{x},{y + 70} H{x + 110} L{x + 118},{y + 82} Z" fill="#FFFFFF" stroke="{NEG}" stroke-width="1.6"/>')
    texto(x + 55, y - 10, nombre, 14, "middle")


def zapatilla(x, y, etiqueta_txt):
    rect(fondo, x, y, 120, 34, "#FFFFFF", NEG, 1.4)
    for i in range(4):
        rect(fondo, x + 6 + i * 29, y + 7, 21, 20, "#FFFFFF", NEG, 1)
    texto(x + 60, y + 52, etiqueta_txt, 13, "middle")
    return [x + 16.5 + i * 29 for i in range(4)]


def red(x, y):
    rect(fondo, x, y, 45, 70, "#FFFFFF", NEG, 1.4)
    texto(x + 27, y + 35, "RED", 14, "middle", rot=-90)


def simbolo_tierra(x, y):
    poli(fondo, [(x, y - 12), (x, y)], NEG, 1.4)
    for i, w in enumerate((14, 9, 4)):
        poli(fondo, [(x - w, y + i * 5), (x + w, y + i * 5)], NEG, 1.4)


def cable_5_hilos(pts, extremo, terminales, y_term, desde_abajo=False):
    """Vaina negra del cable de 5 hilos y abanico de hilos de colores a los bornes 1–5."""
    poli(cables, pts, "#111", 6)
    ex, ey = extremo
    for i, tx in enumerate(terminales):
        sep = (i - 2) * 3.2
        medio = ey + (8 if not desde_abajo else -8)
        tramo = [(ex + sep, ey), (ex + sep, medio), (tx, medio + (6 if not desde_abajo else -6)), (tx, y_term)]
        poli(cables, tramo, HILOS[i], 2.2)
        if i == 4:
            poli(cables, tramo, "#E5D21C", 2.2, extra=' stroke-dasharray="3 3"')
        rect(cables, tx - 1.6, y_term - (4 if not desde_abajo else 0), 3.2, 4, "#B9BDC0", "#777", 0.4)


# ======================================================================== marco y título
fondo.append(f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="none" stroke="{NEG}" stroke-width="1"/>')
texto(W / 2, 80, "ESQUEMA GENERAL DE CONEXIONES – SISTEMA GRIS", 30, "middle")

# ======================================================================== equipos
cb = control_box(520, 160, 240)
texto(640, 145, "Control box", 14, "middle")
te = tablero_elcid(520, 560, 240)
texto(640, 548, "Tablero EL CID", 14, "middle")
tx = tablero_excitacion(450, 900, 560)
texto(730, 900 + tx["h"] + 20, "Tablero de excitación", 14, "middle")
pc(960, 350, "PC GRIS")
pc(960, 575, "PC EL CID")
z1 = zapatilla(130, 560, "Zapatilla")
red(60, 542)
z2 = zapatilla(1150, 690, "Zapatilla")
red(1060, 672)
caja_v = (1060, 830, 140, 100)
rect(fondo, *caja_v, "#FFFFFF", NEG, 1.4)
fondo.append('<path d="M1130,850 ' + " ".join("a7,6 0 1 1 0,12" for _ in range(5)) + f'" fill="none" stroke="{NEG}" stroke-width="1.4"/>')
poli(fondo, [(1145, 848), (1119, 912)], NEG, 1.4)
fondo.append(f'<path d="M1119,912 l-1,-9 l7,4 z" fill="{NEG}"/>')
texto(1066, 892, "0–250 V", 11)
texto(1194, 892, "220 V", 11, "end")
texto(1130, 952, "Variac", 14, "middle")
red(1235, 845)

# ======================================================================== estator (derecha)
c1, c2, R, r = (1420, 905), (1565, 805), 105, 65
ax_, ay_ = c2[0] - c1[0], c2[1] - c1[1]
nx_, ny_ = -ay_ / math.hypot(ax_, ay_), ax_ / math.hypot(ax_, ay_)
circ(fondo, *c2, R, "#FFFFFF", NEG, 1.4)
for s_ in (1, -1):
    poli(fondo, [(c1[0] + s_ * R * nx_, c1[1] + s_ * R * ny_), (c2[0] + s_ * R * nx_, c2[1] + s_ * R * ny_)], NEG, 1.4)
circ(fondo, *c1, R, "#FFFFFF", NEG, 1.4)
circ(fondo, *c1, r, "#FFFFFF", NEG, 1.4)
texto(1630, 960, "Núcleo\nestatórico", 14, "middle")
rby = c1[1] - r + 6
rect(fondo, c1[0] - 22, rby + 4, 44, 16, "#FFFFFF", NEG, 1.4)
rect(fondo, c1[0] - 22, rby, 44, 3, "#FFFFFF", NEG, 1.2)
texto(c1[0] - 30, rby + 8, "Robot", 13, "end")

# ======================================================================== conexiones
# arnés del robot: cable principal + señal del captor, juntos hasta el tablero EL CID
poli(fondo, [(c1[0], rby), (c1[0], 304), (cb["principal"][0] + 40, 304)], ARNES, 18)
poli(fondo, [(c1[0], 304), (c1[0], te["captor"][1])], ARNES, 18)
linea([(c1[0] - 4, rby), (c1[0] - 4, cb["principal"][1]), cb["principal"]])
linea([(c1[0] + 4, rby), (c1[0] + 4, te["captor"][1]), te["captor"]])
texto(1060, 292, "Arnés del robot (cable principal y señal del captor)", 12, "middle")
texto(900, te["captor"][1] - 6, "Señal del captor", 11.5, "middle")
# control box ↔ tablero EL CID y PC
linea([cb["bnc"], (790, cb["bnc"][1]), (790, te["pos"][1]), te["pos"]])
texto(798, 520, "Señal de\nposición", 11.5)
linea([cb["usb"], (960, cb["usb"][1])])
texto(875, cb["usb"][1] - 6, "USB", 11.5, "middle")
linea([cb["eth"], (956, cb["eth"][1])])
texto(875, cb["eth"][1] - 6, "Ethernet", 11.5, "middle")
linea([te["usb"], (960, te["usb"][1])])
texto(875, te["usb"][1] - 6, "USB", 11.5, "middle")
# alimentación de la mesa (zapatilla izquierda) y de las PC (zapatilla derecha)
linea([cb["iec"], (z1[2], cb["iec"][1]), (z1[2], 560)])
texto(380, cb["iec"][1] - 6, "Alimentación", 11, "middle")
linea([te["iec"], (z1[2], te["iec"][1]), (z1[2], 594)])
texto(380, te["iec"][1] - 6, "Alimentación", 11, "middle")
linea([(130, 577), (105, 577)], NEG, 2)
linea([(1070, 385), (z2[1], 385), (z2[1], 690)])
linea([(1070, 610), (z2[0], 610), (z2[0], 690)])
texto(1120, 379, "Alimentación", 11, "middle")
texto(1120, 604, "Alimentación", 11, "middle")
linea([(1150, 707), (1105, 707)], NEG, 2)
# tierras: tablero EL CID → zapatilla; zapatilla → núcleo estatórico (por arriba)
linea([te["ground"], (z1[3], te["ground"][1]), (z1[3], 594)], VERDE, 2.6)
texto(380, te["ground"][1] - 6, "Tierra tablero EL CID", 11, "middle")
linea([(z1[0], 560), (z1[0], 130), (1760, 130), (1760, 760), (c2[0] + math.sqrt(R ** 2 - 45 ** 2), 760)], VERDE, 2.6)
texto(940, 124, "Tierra principal (desde el núcleo estatórico)", 11.5, "middle")
simbolo_tierra(1760, 784)
# corriente de magnetización: bornes 6 y 7 → tablero EL CID
linea([te["b1"], (te["b1"][0], 960), (tx["sup"][5], 960), (tx["sup"][5], tx["y_sup"])], NAR, 2)
linea([te["b2"], (te["b2"][0], 975), (tx["sup"][6], 975), (tx["sup"][6], tx["y_sup"])], NAR, 2)
# Variac → ficha del tablero de excitación
linea([(1060, 875), (1030, 875), (1030, tx["ficha"][1]), tx["ficha"]], NEG, 2)
texto(920, tx["ficha"][1] - 6, "Salida del Variac", 11.5, "middle")
linea([(1200, 880), (1235, 880)], NEG, 2)

# cable de excitación de 5 hilos: vaina negra, pasa por el entrehierro y vuelve por fuera del núcleo
pf, pb = (c1[0] - 28, c1[1] + 30), (c2[0] - 28, c2[1] + 30)
sup_x = sum(tx["sup"][:5]) / 5
cable_5_hilos([(sup_x, 965), (sup_x, 880), (420, 880), (420, 1238), (1700, 1238), (1700, pb[1] - 12), (pb[0], pb[1] - 12)],
              (sup_x, 965), tx["sup"][:5], tx["y_sup"])
cable_5_hilos([(sup_x, 1120), (440, 1120), (440, 1224), (1350, 1224), (1350, pf[1]), pf],
              (sup_x, 1120), tx["sup"][:5], tx["y_inf"], desde_abajo=True)
poli(cables, [pf, (pb[0], pb[1] - 12)], "#111", 6, extra=' stroke-dasharray="10 7"')
texto(1180, 1217, "Cable de excitación de 5 hilos (espiras en serie)", 12, "middle")
# espira auxiliar: rodea el núcleo igual que el cable de excitación
pfa, pba = (c1[0] - 48, c1[1] + 12), (c2[0] - 48, c2[1] + 12)
linea([(tx["aux"][0], tx["y_aux"]), (tx["aux"][0], 1003), (1030, 1003), (1030, 1050), (1330, 1050), (1330, pfa[1]), pfa], VIOL, 2)
linea([(tx["aux"][1], tx["y_aux"]), (tx["aux"][1], 1012), (1020, 1012), (1020, 1062), (1680, 1062), (1680, pba[1] - 6), (pba[0], pba[1] - 6)], VIOL, 2)
poli(cables, [pfa, (pba[0], pba[1] - 6)], VIOL, 2, extra=' stroke-dasharray="7 5"')
texto(1180, 1044, "Espira auxiliar", 12, "middle")

texto(W - 36, H - 30, "Mecanálisis – 00503-00-EPG001 – 28/10/2026", 11, "end")


# ======================================================================== líneas con puentes en los cruces
def segmentos(pts):
    return list(zip(pts[:-1], pts[1:]))


def verticales_de(objs):
    out = []
    for o in objs:
        for (x0, y0), (x1, y1) in segmentos(o["pts"]):
            if abs(x0 - x1) < 0.1 and abs(y1 - y0) > 1:
                out.append((x0, min(y0, y1), max(y0, y1), o))
    return out


# vainas del cable de 5 hilos como verticales a saltar
vainas = [{"pts": p, "ancho": 6} for p in ([(1350, 1224), (1350, 935)], [(1700, 1238), (1700, 793)], [(420, 880), (420, 1238)], [(440, 1120), (440, 1224)])]
verticales = verticales_de(lineas) + verticales_de(vainas)


def render(l):
    pts = l["pts"]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in segmentos(pts):
        if l["puentes"] and abs(y0 - y1) < 0.1 and abs(x1 - x0) > 1:
            s = 1 if x1 > x0 else -1
            cruces = sorted(((vx, o) for (vx, va, vb, o) in verticales
                             if o is not l and min(x0, x1) + 8 < vx < max(x0, x1) - 8 and va + 3 < y0 < vb - 3),
                            key=lambda t: s * t[0])
            for vx, o in cruces:
                rr = max(6, o["ancho"] / 2 + 4)
                d += f" L{vx - s * rr:.1f},{y0:.1f} A{rr},{rr} 0 0 {1 if s > 0 else 0} {vx + s * rr:.1f},{y0:.1f}"
        d += f" L{x1:.1f},{y1:.1f}"
    da = f' stroke-dasharray="{l["trazo"]}"' if l["trazo"] else ""
    return f'<path d="{d}" fill="none" stroke="{l["color"]}" stroke-width="{l["ancho"]}" stroke-linejoin="miter"{da}/>'


svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Arial, Liberation Sans, Helvetica, sans-serif"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
       + "".join(fondo) + "".join(cables) + "".join(render(l) for l in lineas) + "".join(frente) + "</svg>")
salida = AQUI / "img" / "esquema_general.svg"
salida.write_text(svg, encoding="utf-8")
print(salida)
