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
    # bornera EXCITATION: 7 bornes de paso juntos (tornillo superior e inferior del mismo borne enfrentados)
    bx0, bx1 = X(0.224), X(0.361)
    paso = (bx1 - bx0) / 7

    def bornes(x0, n, y0, y1, nombre, et_sup=None, et_inf=None):
        et_sup = et_sup or [str(k + 1) for k in range(n)]
        et_inf = et_inf or [str(k + 1) for k in range(n)]
        rect(fondo, x0 - 1.5, y0, n * paso + 3, y1 - y0, "#1B1B1B", "#000", 0.5, 1)
        for k in range(n):
            xk = x0 + k * paso
            rect(fondo, xk + 0.5, y0 + 1, paso - 1, y1 - y0 - 2, "#EDEDE9", "#9A9A95", 0.5)
            for yy in (y0 + (y1 - y0) * 0.14, y0 + (y1 - y0) * 0.86):
                circ(fondo, xk + paso / 2, yy, paso * 0.3, "#C8C8C4", "#8A8A86", 0.4)
                fondo.append(f'<line x1="{xk + paso * 0.28:.1f}" y1="{yy:.1f}" x2="{xk + paso * 0.72:.1f}" y2="{yy:.1f}" stroke="#777" stroke-width="0.6"/>')
            for yy, et in ((y0 + (y1 - y0) * 0.33, et_sup[k]), (y0 + (y1 - y0) * 0.72, et_inf[k])):
                texto(xk + paso / 2, yy, et, 5.5, "middle", "#222", peso="bold", capa=fondo)
        rect(fondo, x0 - 1.5, y0 + (y1 - y0) * 0.43, n * paso + 3, (y1 - y0) * 0.16, "#1B1B1B")
        texto(x0 + n * paso / 2, y0 + (y1 - y0) * 0.545, nombre, 4.6, "middle", "#F2F2F2", peso="bold", capa=fondo)

    yb0, yb1 = Y(0.335), Y(0.605)
    bornes(bx0, 7, yb0, yb1, "EXCITATION", ["1", "2", "3", "4", "5", "", ""], ["", "1", "2", "3", "4", "5", ""])
    # llave del circuito de la espira auxiliar (separada de la bornera de excitación)
    mx, my, mw, mh = X(0.80), Y(0.435), w * 0.06, h * 0.42
    rect(fondo, mx, my, mw, mh, "#F8F8F8", "#9A9A9A", 0.7, 1.5)
    rect(fondo, mx + mw * 0.1, my + mh * 0.05, mw * 0.8, mh * 0.13, "#ECECEC", "#BBB", 0.4)
    rect(fondo, mx + mw * 0.28, my + mh * 0.38, mw * 0.44, mh * 0.24, "#E6E6E6", "#999", 0.5, 1)
    rect(fondo, mx + mw * 0.35, my + mh * 0.40, mw * 0.3, mh * 0.11, "#1A1A1A")
    rect(fondo, mx + mw * 0.68, my + mh * 0.06, mw * 0.2, mh * 0.06, "#2E9B48")
    for fy in (0.1, 0.9):
        circ(fondo, mx + mw / 2, my + mh * fy, w * 0.007, "#C8C8C4", "#888", 0.4)
    texto(mx + mw / 2, my + mh * 0.3, "Schneider", 3.8, "middle", "#2E9B48", capa=fondo)
    # bornera AUXILIAR: mismo tipo de borne de paso, 2 bornes
    ax0 = X(0.66) - paso
    bornes(ax0, 2, yb0, yb1, "AUX")
    etiqueta(ax0 - w * 0.02, Y(0.27), 2 * paso + w * 0.04, h * 0.05, "AUXILIAR", 0, 5.5)
    # protoboard: espacio libre para las resistencias de calibración
    rect(fondo, X(0.432), Y(0.615), w * 0.158, h * 0.218, "#F8F8F3", "#BDBDB7", 0.7, 1.5)
    for fy, col in ((0.632, "#D33"), (0.645, "#36C"), (0.800, "#D33"), (0.813, "#36C")):
        rect(fondo, X(0.44), Y(fy), w * 0.142, 0.7, col)
    for jj in range(6):
        for ii in range(15):
            if jj != 3:
                circ(fondo, X(0.442) + ii * w * 0.0095, Y(0.665) + jj * h * 0.022, 0.55, "#B8B8B2")
    texto(X(0.511), Y(0.72), "Espacio para las", 5.5, "middle", "#7A7A75", capa=fondo)
    texto(X(0.511), Y(0.745), "resistencias de calibración", 5.5, "middle", "#7A7A75", capa=fondo)
    # fichas banana (medición de tensión por espira) y llave del circuito auxiliar
    for fx, fy, col in ((0.803, 0.10, "#151515"), (0.836, 0.073, "#C8202A")):
        circ(fondo, X(fx), Y(fy), w * 0.013, col, "#000", 0.5)
        circ(fondo, X(fx), Y(fy), w * 0.005, "#777")
    term = [bx0 + (i + 0.5) * paso for i in range(7)]
    aux_t = [ax0 + (i + 0.5) * paso for i in range(2)]
    rs = w * 0.022
    fc = (X(0.579), Y(0.167))
    return {"ficha": (X(0.637), Y(-0.07)), "sup": term, "y_sup": yb0 + 1, "y_inf": yb1 - 1, "izq": bx0, "der": bx1,
            "L": (fc[0] + rs * math.cos(math.radians(210)), fc[1] + rs * 0.5), "N": (fc[0] + rs * math.cos(math.radians(330)), fc[1] + rs * 0.5),
            "mcb_sup": (X(0.83), Y(0.477)), "mcb_inf": (X(0.83), Y(0.813)),
            "aux": tuple(aux_t), "y_aux": yb0 + 1, "y_aux_inf": yb1 - 1,
            "bus": (X(0.58), Y(0.800), Y(0.813)),
            "j_neg": (X(0.803), Y(0.10)), "j_roj": (X(0.836), Y(0.073)), "h": h}


def multimetro(x, y, w=82):
    """Multímetro UNI-T (rojo y gris)."""
    h = w * 1.6
    rect(fondo, x, y, w, h, "#C8102E", "#8E0B20", 1, 8)
    rect(fondo, x + w * 0.08, y + h * 0.06, w * 0.84, h * 0.88, "#3A3A3A", "#222", 0.6, 5)
    rect(fondo, x + w * 0.16, y + h * 0.1, w * 0.68, h * 0.2, "#B9C7A6", "#6E7A60", 0.6, 2)
    texto(x + w * 0.5, y + h * 0.235, "0.124", w * 0.17, "middle", "#1F261A", peso="bold", capa=fondo)
    circ(fondo, x + w * 0.5, y + h * 0.56, w * 0.24, "#555", "#222", 0.8)
    circ(fondo, x + w * 0.5, y + h * 0.56, w * 0.17, "#6A6A6A")
    poli(fondo, [(x + w * 0.5, y + h * 0.56), (x + w * 0.5 - w * 0.12, y + h * 0.56 - w * 0.12)], "#FFFFFF", 2)
    jacks = []
    for i, col in enumerate(("#C8102E", "#111", "#111")):
        cx = x + w * (0.25 + i * 0.25)
        circ(fondo, cx, y + h * 0.84, w * 0.06, col, "#000", 0.6)
        circ(fondo, cx, y + h * 0.84, w * 0.025, "#888")
        jacks.append((cx, y + h * 0.84))
    return {"v": jacks[0], "com": jacks[1], "h": h}


def pinza(cx_m, cy_m, w=64, giro=90):
    """Dibuja la pinza con la mordaza centrada en (cx_m, cy_m), girada `giro` grados."""
    antes = len(frente)
    _pinza(cx_m - w / 2, cy_m - w * 0.36, w)
    grupo = "".join(frente[antes:])
    del frente[antes:]
    frente.append(f'<g transform="rotate({giro} {cx_m:.1f} {cy_m:.1f})">{grupo}</g>')
    return (cx_m, cy_m)


def _pinza(x, y, w=64):
    """Pinza amperométrica UNI-T (UT211B): mordaza abierta arriba, gatillo lateral, cuerpo rojo y gris."""
    cx, cy, ra = x + w / 2, y + w * 0.36, w * 0.30
    # mordaza: anillo con una pequeña apertura arriba a la derecha
    C = 2 * math.pi * ra
    for col, wd in (("#2E2E2E", w * 0.17), ("#D7192D", w * 0.06)):
        frente.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{ra:.1f}" fill="none" stroke="{col}" stroke-width="{wd:.1f}" '
                      f'stroke-dasharray="{C * 0.93:.1f} {C * 0.07:.1f}" transform="rotate(-70 {cx:.1f} {cy:.1f})"/>')
    # cuerpo
    yb = y + w * 0.62
    frente.append(f'<path d="M{x + w * 0.12:.1f},{yb:.1f} Q{cx:.1f},{yb - w * 0.1:.1f} {x + w * 0.88:.1f},{yb:.1f} L{x + w * 0.96:.1f},{yb + w * 0.5:.1f} '
                  f'L{x + w * 0.9:.1f},{y + w * 2.45:.1f} Q{cx:.1f},{y + w * 2.58:.1f} {x + w * 0.1:.1f},{y + w * 2.45:.1f} L{x + w * 0.04:.1f},{yb + w * 0.5:.1f} Z" '
                  f'fill="#D7192D" stroke="#8E0B20" stroke-width="1"/>')
    rect(frente, x - w * 0.06, yb + w * 0.18, w * 0.12, w * 0.34, "#2E2E2E", "#111", 0.6, 3)             # gatillo
    rect(frente, x + w * 0.16, yb + w * 0.2, w * 0.68, w * 1.6, "#333", "#1A1A1A", 0.6, 4)             # frente gris
    rect(frente, x + w * 0.24, yb + w * 0.3, w * 0.52, w * 0.34, "#B9C7A6", "#6E7A60", 0.6, 2)        # display
    texto(cx, yb + w * 0.55, "0.150", w * 0.15, "middle", "#1F261A", peso="bold", capa=frente)
    for k in range(3):
        rect(frente, x + w * (0.25 + k * 0.18), yb + w * 0.74, w * 0.13, w * 0.08, "#5A5A5A", "none", 0, 2)
    circ(frente, cx, yb + w * 1.18, w * 0.2, "#4A4A4A", "#1A1A1A", 0.8)                                 # selector
    poli(frente, [(cx, yb + w * 1.18), (cx + w * 0.1, yb + w * 1.06)], "#FFFFFF", 1.6)
    for k, col in enumerate(("#111", "#C8102E")):
        circ(frente, x + w * (0.36 + k * 0.28), yb + w * 1.72, w * 0.05, col, "#000", 0.5)
    return (cx, cy)


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
# orden de izquierda a derecha: alimentación y PC · tableros · estator
cb = control_box(520, 160, 240)
texto(640, 145, "Control box", 14, "middle")
te = tablero_elcid(520, 560, 240)
texto(640, 548, "Tablero EL CID", 14, "middle")
tx = tablero_excitacion(450, 900, 560)
texto(730, 900 + tx["h"] + 20, "Tablero de excitación", 14, "middle")
pc(230, 470, "PC GRIS")
pc(230, 610, "PC EL CID")
z1 = zapatilla(110, 1000, "Zapatilla")
red(147, 1070)
linea([(170, 1034), (170, 1070)], NEG, 2)
circ(frente, 236, 1017, 4, "#FFFFFF", VERDE, 1.6)                       # borne de tierra de la zapatilla

# Variac: en línea con la ficha del tablero de excitación
vx, vy = 1060, 850
rect(fondo, vx, vy, 140, 100, "#FFFFFF", NEG, 1.4)
fondo.append(f'<path d="M{vx + 70},{vy + 20} ' + " ".join("a7,6 0 1 1 0,12" for _ in range(5)) + f'" fill="none" stroke="{NEG}" stroke-width="1.4"/>')
poli(fondo, [(vx + 85, vy + 18), (vx + 59, vy + 82)], NEG, 1.4)
fondo.append(f'<path d="M{vx + 59},{vy + 82} l-1,-9 l7,4 z" fill="{NEG}"/>')
texto(vx + 6, vy + 62, "0–250 V", 11)
texto(vx + 134, vy + 62, "220 V", 11, "end")
texto(vx + 70, vy - 10, "Variac", 14, "middle")
red(1235, vy + 15)
linea([(vx + 140, vy + 50), (1235, vy + 50)], NEG, 2)
poli(cables, [(vx, tx["ficha"][1]), tx["ficha"]], "#111", 6)              # salida del Variac: cable grueso
texto(930, tx["ficha"][1] - 8, "Salida del Variac", 11.5, "middle")

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
# robot en la parte superior del entrehierro
ry0 = c1[1] - r + 5
rect(frente, c1[0] - 22, ry0, 44, 14, "#4A4F54", "#2B2F33", 1, 3)                # cuerpo
rect(frente, c1[0] - 25, ry0 + 12, 50, 6, "#1E1E1E", "none", 0, 3)              # orugas
for dx in (-18, -6, 6, 18):
    circ(frente, c1[0] + dx, ry0 + 15, 1.6, "#777")
rect(frente, c1[0] - 6, ry0 + 3, 12, 5, NAR, "none", 0, 1)                       # captor
poli(frente, [(c1[0] - 26, ry0 + 6), (c1[0] - 70, ry0 - 20)], NEG, 1)
texto(c1[0] - 74, ry0 - 22, "Robot", 13, "end")

# ======================================================================== conexiones
# arnés del robot (malla negra) hasta el conector del control box; la señal del captor sale de ese punto
xa = c1[0]
yp = cb["principal"][1]
arnes = [(xa, ry0), (xa, yp), (cb["principal"][0] + 4, yp)]
poli(cables, arnes, "#1E1E1E", 9)
poli(cables, arnes, "#555", 9, extra=' stroke-dasharray="2 4"')
linea([(850, yp + 5), (850, te["captor"][1]), te["captor"]])
rect(frente, 843, yp + 3, 14, 9, "#1E1E1E", "#000", 0.6, 2)                         # salida de la señal del captor desde el arnés
texto(1130, yp - 12, "Arnés del robot (cable principal y señal del captor)", 12, "middle")
texto(858, te["captor"][1] + 4, "Señal del captor", 11.5)
# control box → tablero EL CID (posición) y PC (USB / Ethernet por debajo del control box)
linea([cb["bnc"], (830, cb["bnc"][1]), (830, te["pos"][1]), te["pos"]])
texto(858, te["pos"][1] + 4, "Señal de posición", 11.5)
linea([cb["usb"], (800, cb["usb"][1]), (800, 510), (340, 510)])
linea([cb["eth"], (785, cb["eth"][1]), (785, 500), (340, 500)])
texto(450, 494, "Ethernet", 11.5, "middle")
texto(450, 524, "USB", 11.5, "middle")
linea([te["usb"], (775, te["usb"][1]), (775, 530), (380, 530), (380, 645), (340, 645)])
texto(450, 544, "USB", 11.5, "middle")
# alimentaciones desde la zapatilla
linea([cb["iec"], (z1[0], cb["iec"][1]), (z1[0], 1000)])
texto(340, cb["iec"][1] - 6, "Alimentación", 11, "middle")
linea([(230, 505), (z1[1], 505), (z1[1], 1000)])
linea([(230, 645), (z1[2], 645), (z1[2], 1000)])
linea([te["iec"], (z1[3], te["iec"][1]), (z1[3], 1000)])
texto(380, te["iec"][1] - 6, "Alimentación", 11, "middle")
# tierras: tablero EL CID → zapatilla; zapatilla → núcleo estatórico (por arriba)
linea([te["ground"], (260, te["ground"][1]), (260, 1017), (240, 1017)], VERDE, 2.6)
texto(400, te["ground"][1] - 6, "Tierra tablero EL CID", 11, "middle")
linea([(110, 1017), (80, 1017), (80, 1046)], VERDE, 2.6)
simbolo_tierra(80, 1058)
pt_n = (c2[0] + math.sqrt(R ** 2 - 45 ** 2), 760)
linea([pt_n, (1760, 760), (1760, 790)], VERDE, 2.6)
simbolo_tierra(1760, 802)
texto(1755, 748, "Tierra del núcleo", 11.5, "end")
# corriente de excitación: bornes 6 y 7 → tablero EL CID (rojo)
ROJO = "#D32F2F"
linea([te["b1"], (te["b1"][0], 932), (tx["sup"][5], 932), (tx["sup"][5], tx["y_sup"])], ROJO, 2.4)
linea([te["b2"], (te["b2"][0], 940), (tx["sup"][6], 940), (tx["sup"][6], tx["y_sup"])], ROJO, 2.4)

# cable de excitación de 5 hilos: vaina negra, pasa por el entrehierro y vuelve por fuera del núcleo
pf, pb = (c1[0] - 28, c1[1] + 30), (c2[0] - 28, c2[1] + 30)
sup_x = sum(tx["sup"][:5]) / 5
cable_5_hilos([(sup_x, 965), (sup_x, 880), (420, 880), (420, 1238), (1700, 1238), (1700, pb[1] - 12), (pb[0], pb[1] - 12)],
              (sup_x, 965), tx["sup"][:5], tx["y_sup"])
inf_x = sum(tx["sup"][1:6]) / 5
cable_5_hilos([(inf_x, 1120), (inf_x, 1224), (1350, 1224), (1350, pf[1]), pf],
              (inf_x, 1120), tx["sup"][1:6], tx["y_inf"], desde_abajo=True)
poli(cables, [pf, (pb[0], pb[1] - 12)], "#111", 6, extra=' stroke-dasharray="10 7"')
texto(1180, 1217, "Cable de excitación de 5 hilos (espiras en serie)", 12, "middle")

# conexiones internas del tablero de excitación
MARRON, AZUL, GRIS_W = "#7B4A2A", "#2A62C9", "#4D4D4D"
t = tx["sup"]
# ficha (salida del Variac) → borne 1 inferior y borne 7 inferior
linea([tx["N"], (tx["N"][0], 952), (566, 952), (566, tx["y_inf"] + 10), (t[0], tx["y_inf"] + 10), (t[0], tx["y_inf"])], AZUL, 1.8)
linea([tx["L"], (tx["L"][0], 970), (655, 970), (655, tx["y_inf"] + 10), (t[6], tx["y_inf"] + 10), (t[6], tx["y_inf"])], MARRON, 1.8)
# circuito auxiliar (sin conexión con el de excitación): la espira llega por arriba a AUX 1 y 2;
# por abajo: AUX 2 → llave → bus de la protoboard; AUX 1 → bus de la protoboard; fichas banana en paralelo
a1, a2 = tx["aux"]
bx, bya, byb = tx["bus"]
ms, mi = tx["mcb_sup"], tx["mcb_inf"]
yai = tx["y_aux_inf"]
linea([(a2, yai), (a2, yai + 7), (880, yai + 7), (880, ms[1] - 16), (ms[0], ms[1] - 16), (ms[0], ms[1] - 3)], GRIS_W, 1.5)
linea([(mi[0], mi[1] + 3), (mi[0], 1162), (765, 1162), (765, bya), (bx, bya)], GRIS_W, 1.5)
linea([(a1, yai), (a1, yai + 19), (785, yai + 19), (785, byb), (bx, byb)], GRIS_W, 1.5)
circ(cables, bx, bya, 1.8, "#C8102E")
circ(cables, bx, byb, 1.8, "#2A62C9")
linea([tx["j_neg"], (tx["j_neg"][0], ms[1] - 16)], "#151515", 1.4)
circ(cables, tx["j_neg"][0], ms[1] - 16, 2.2, "#151515")
linea([tx["j_roj"], (945, tx["j_roj"][1]), (945, 1172), (750, 1172), (750, byb)], ROJO, 1.4)
circ(cables, 750, byb, 2.2, ROJO)

# espira auxiliar: rodea el núcleo igual que el cable de excitación; entra por arriba a AUX 1 y 2
pfa, pba = (c1[0] - 48, c1[1] + 12), (c2[0] - 48, c2[1] + 12)
ya = tx["y_aux"]
linea([(a1, ya), (a1, 905), (1030, 905), (1030, 1170), (1290, 1170), (1290, pfa[1]), pfa], VIOL, 2)
linea([(a2, ya), (a2, 912), (1020, 912), (1020, 1182), (1680, 1182), (1680, pba[1] - 6), (pba[0], pba[1] - 6)], VIOL, 2)
poli(cables, [pfa, (pba[0], pba[1] - 6)], VIOL, 2, extra=' stroke-dasharray="7 5"')
texto(1160, 1164, "Espira auxiliar", 12, "middle")
# voltímetro en las fichas banana (tensión por espira) y pinza en la espira auxiliar (corriente)
mm = multimetro(1065, 975)
def punta(p0, p1, col, baja):
    cables.append(f'<path d="M{p0[0]:.1f},{p0[1]:.1f} C{p0[0] + 60:.1f},{baja:.1f} {p1[0]:.1f},{baja + 40:.1f} {p1[0]:.1f},{p1[1]:.1f}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>')
punta(tx["j_roj"], mm["v"], "#C8102E", 1135)
punta(tx["j_neg"], mm["com"], "#151515", 1150)
texto(1160, 980, "Voltímetro", 11.5)
texto(1160, 994, "(tensión por espira)", 11.5)
pz = pinza(1290, 1075, 60, 90)
texto(1225, 1118, "Pinza amperométrica", 11.5, "middle")
texto(1225, 1132, "(corriente en la espira auxiliar)", 11.5, "middle")
# advertencia junto a la ficha del Variac
fondo.append('<path d="M866,806 l8,-14 l8,14 z" fill="#F2C200" stroke="#000" stroke-width="0.8"/>')
texto(874, 804, "!", 9, "middle", peso="bold")
texto(888, 800, "Tablero en desarrollo:", 10, peso="bold")
texto(888, 813, "no manipular la ficha con el", 10, peso="bold")
texto(888, 826, "Variac conectado a la red.", 10, peso="bold")

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
vainas = [{"pts": p, "ancho": 6} for p in ([(1350, 1224), (1350, 935)], [(1700, 1238), (1700, 793)], [(420, 880), (420, 1238)],
                                         [(inf_x, 1120), (inf_x, 1224)], [(sup_x, 880), (sup_x, 965)])]
vainas.append({"pts": [(xa, ry0), (xa, yp)], "ancho": 9})
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
