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
    rect(fondo, X(0.028), Y(0.023), w * 0.944, h * 0.954, "#3A3D40")             # tapa negra (aclarada para que se distingan líneas y conectores)
    rect(fondo, X(0.028), Y(0.023), w * 0.944, 2, "#4A4D50")
    for fx, fy in ((0.06, 0.045), (0.94, 0.045), (0.06, 0.955), (0.94, 0.955), (0.5, 0.045), (0.5, 0.955)):
        tornillo(fondo, X(fx), Y(fy), 1.6, "#55595D")
    rect(fondo, x - 6, Y(0.42), 8, h * 0.1, "#B8BDC1", "#7D8286", 0.6, 2)        # cierre lateral
    iec(X(0.211), Y(0.107), w * 0.165, h * 0.063)
    llave(X(0.232), Y(0.194), w * 0.097, h * 0.069)
    rejilla(X(0.705), Y(0.180), w * 0.185, h * 0.176, 3.6, "#26292B", "#5E6266")  # ventilador
    for fx, fy in ((0.705, 0.18), (0.89, 0.18), (0.705, 0.356), (0.89, 0.356)):
        tornillo(fondo, X(fx), Y(fy), 1.8, "#26292B")
    rejilla(X(0.165), Y(0.772), w * 0.447, h * 0.10, 3.6, "#26292B", "#5E6266")   # rejilla inferior
    # conector del cable principal
    rect(fondo, X(0.79), Y(0.500), w * 0.13, h * 0.056, "#8E9396", "#5F6468", 0.6, 1.5)
    rect(fondo, X(0.802), Y(0.509), w * 0.105, h * 0.038, "#C3C7CA", "#6F7478", 0.6, 1)
    for fx in (0.797, 0.913):
        tornillo(fondo, X(fx), Y(0.528), 1.3, "#7A7F83")
    bnc(X(0.840), Y(0.593), w * 0.017)                                           # BNC posición
    rect(fondo, X(0.803), Y(0.640), w * 0.086, h * 0.094, "#1A1C1E", "#777", 0.6, 2)  # USB (Neutrik)
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
    # riel DIN de 35 mm (proporciones de la foto: alto ≈ la mitad de un borne de paso)
    rect(fondo, X(0.20), Y(0.40), w * 0.67, h * 0.12, "#C9CCCE", "#8E9194", 0.6)
    rect(fondo, X(0.20), Y(0.418), w * 0.67, h * 0.084, "#B1B4B7", "#8E9194", 0.4)
    for i in range(17):
        rect(fondo, X(0.215) + i * w * 0.038, Y(0.449), w * 0.022, h * 0.022, "#8A8D90", "none", 0, 3)
    # bornera EXCITATION: 7 bornes de paso juntos (tornillo superior e inferior del mismo borne enfrentados)
    bx0, bx1 = X(0.224), X(0.361)
    paso = (bx1 - bx0) / 7

    def bornes(x0, n, y0, y1, nombre, et_sup=None, et_inf=None, paso=paso):
        et_sup = et_sup or [str(k + 1) for k in range(n)]
        et_inf = et_inf or [str(k + 1) for k in range(n)]
        rect(fondo, x0 - 1.5, y0, n * paso + 3, y1 - y0, "#1B1B1B", "#000", 0.5, 1)
        for k in range(n):
            xk = x0 + k * paso
            rect(fondo, xk + 0.5, y0 + 1, paso - 1, y1 - y0 - 2, "#EDEDE9", "#9A9A95", 0.5)
            for yy in (y0 + (y1 - y0) * 0.14, y0 + (y1 - y0) * 0.86):
                rt = min(paso * 0.3, 4.2)
                circ(fondo, xk + paso / 2, yy, rt, "#C8C8C4", "#8A8A86", 0.4)
                fondo.append(f'<line x1="{xk + paso / 2 - rt * 0.73:.1f}" y1="{yy:.1f}" x2="{xk + paso / 2 + rt * 0.73:.1f}" y2="{yy:.1f}" stroke="#777" stroke-width="0.6"/>')
            for yy, et in ((y0 + (y1 - y0) * 0.37, et_sup[k]), (y0 + (y1 - y0) * 0.76, et_inf[k])):
                texto(xk + paso / 2, yy, et, 8.5, "middle", "#111", peso="bold", capa=fondo)
        rect(fondo, x0 - 1.5, y0 + (y1 - y0) * 0.43, n * paso + 3, (y1 - y0) * 0.16, "#1B1B1B")
        texto(x0 + n * paso / 2, y0 + (y1 - y0) * 0.555, nombre, 7, "middle", "#F2F2F2", peso="bold", capa=fondo)

    yb0, yb1 = Y(0.335), Y(0.605)
    bornes(bx0, 7, yb0, yb1, "EXCITATION", ["1", "2", "3", "4", "5", "", ""], ["", "1", "2", "3", "4", "5", ""])
    # llave del circuito de la espira auxiliar: junto a la bornera EXCITATION, pero sin conexión con ella
    mx, my, mw, mh = X(0.372), Y(0.255), w * 0.055, h * 0.45
    rect(fondo, mx, my, mw, mh, "#F8F8F8", "#9A9A9A", 0.7, 1.5)
    rect(fondo, mx + mw * 0.1, my + mh * 0.05, mw * 0.8, mh * 0.13, "#ECECEC", "#BBB", 0.4)
    rect(fondo, mx + mw * 0.28, my + mh * 0.38, mw * 0.44, mh * 0.24, "#E6E6E6", "#999", 0.5, 1)
    rect(fondo, mx + mw * 0.35, my + mh * 0.40, mw * 0.3, mh * 0.11, "#1A1A1A")
    rect(fondo, mx + mw * 0.68, my + mh * 0.06, mw * 0.2, mh * 0.06, "#2E9B48")
    for fy in (0.1, 0.9):
        circ(fondo, mx + mw / 2, my + mh * fy, w * 0.007, "#C8C8C4", "#888", 0.4)
    # tope de fin de riel a la derecha de la llave
    rect(fondo, X(0.431), Y(0.37), w * 0.022, h * 0.23, "#E9E9E6", "#9A9A95", 0.5, 1)
    for fy in (0.42, 0.55):
        circ(fondo, X(0.442), Y(fy), w * 0.006, "#C8C8C4", "#888", 0.4)
    # bornera AUXILIAR: mismo borne de paso (mismo ancho) que EXCITATION, 2 bornes
    pa = paso
    ax0 = X(0.686) - pa
    bornes(ax0, 2, yb0, yb1, "AUX", paso=pa)
    etiqueta(ax0 + 2 * pa + w * 0.006, Y(0.30), w * 0.085, h * 0.05, "AUXILIAR", 0, 8)
    # protoboard bajo el riel, desde la llave hasta el lado derecho
    px0, px1, py0, py1 = X(0.437), X(0.863), Y(0.68), Y(0.90)
    rect(fondo, px0, py0, px1 - px0, py1 - py0, "#F8F8F3", "#BDBDB7", 0.7, 1.5)
    for fy, col in ((0.08, "#D33"), (0.15, "#36C"), (0.83, "#D33"), (0.91, "#36C")):
        rect(fondo, px0 + 6, py0 + fy * (py1 - py0), px1 - px0 - 12, 0.7, col)
    for jj in range(8):
        for ii in range(40):
            if jj != 4:
                circ(fondo, px0 + 8 + ii * (px1 - px0 - 16) / 39, py0 + (0.24 + jj * 0.075) * (py1 - py0), 0.55, "#B8B8B2")
    texto((px0 + px1) / 2, py0 + 0.44 * (py1 - py0), "Resistencias de calibración", 8.5, "middle", "#7A7A75", capa=fondo)
    # fichas banana (medición de tensión por espira) y llave del circuito auxiliar
    for fx, fy, col in ((0.803, 0.10, "#151515"), (0.836, 0.073, "#C8202A")):
        circ(fondo, X(fx), Y(fy), w * 0.013, col, "#000", 0.5)
        circ(fondo, X(fx), Y(fy), w * 0.005, "#777")
    term = [bx0 + (i + 0.5) * paso for i in range(7)]
    aux_t = [ax0 + (i + 0.5) * pa for i in range(2)]
    rs = w * 0.022
    fc = (X(0.579), Y(0.167))
    return {"ficha": (X(0.637), Y(-0.07)), "sup": term, "y_sup": yb0 + 1, "y_inf": yb1 - 1, "izq": bx0, "der": bx1,
            "L": (fc[0] + rs * math.cos(math.radians(210)), fc[1] + rs * 0.5), "N": (fc[0] + rs * math.cos(math.radians(330)), fc[1] + rs * 0.5),
            "mcb_sup": (mx + mw / 2, my + mh * 0.1), "mcb_inf": (mx + mw / 2, my + mh * 0.9), "mcb_der": mx + mw,
            "aux": tuple(aux_t), "y_aux": yb0 + 1, "y_aux_inf": yb1 - 1,
            "bus": (px1 - 8, py0 + 0.83 * (py1 - py0), py0 + 0.91 * (py1 - py0)), "proto": (px0, px1, py0, py1),
            "j_neg": (X(0.803), Y(0.10)), "j_roj": (X(0.836), Y(0.073)), "h": h}


def multimetro(x, y, w=82):
    """Multímetro (rojo y gris)."""
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
    """Vaina negra del cable de 5 hilos; termina en una funda y los hilos de colores se abren hacia los bornes 1–5."""
    poli(cables, pts, "#111", 6)
    ex, ey = extremo
    sg = -1 if desde_abajo else 1                     # sentido hacia los bornes
    largo = 12                                        # funda de terminación
    cables.append(f'<path d="M{ex - 3.5},{ey - sg * 2} L{ex + 3.5},{ey - sg * 2} L{ex + 5},{ey + sg * largo} L{ex - 5},{ey + sg * largo} Z" fill="#000"/>')
    y_sal = ey + sg * largo
    for i, tx in enumerate(terminales):
        x0 = ex + (i - 2) * 2.0
        y_t = y_term - sg * 4
        d = (f"M{x0:.1f},{y_sal:.1f} C{x0:.1f},{y_sal + sg * 14:.1f} {tx:.1f},{y_t - sg * 14:.1f} {tx:.1f},{y_t:.1f} L{tx:.1f},{y_term:.1f}")
        cables.append(f'<path d="{d}" fill="none" stroke="{HILOS[i]}" stroke-width="2.2"/>')
        if i == 4:
            cables.append(f'<path d="{d}" fill="none" stroke="#E5D21C" stroke-width="2.2" stroke-dasharray="3 3"/>')
        rect(cables, tx - 1.6, y_term - (4 if not desde_abajo else 0), 3.2, 4, "#B9BDC0", "#777", 0.4)


# ======================================================================== utilidades de composición
T = 32          # tamaño mínimo de rótulos en la figura 1 (≥ 10 pt impreso en A4)


def segmentos(pts):
    return list(zip(pts[:-1], pts[1:]))


def verticales_de(objs):
    out = []
    for o in objs:
        for (x0, y0), (x1, y1) in segmentos(o["pts"]):
            if abs(x0 - x1) < 0.1 and abs(y1 - y0) > 1:
                out.append((x0, min(y0, y1), max(y0, y1), o))
    return out


def render(l, verticales):
    pts = l["pts"]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for (x0, y0), (x1, y1) in segmentos(pts):
        if l["puentes"] and abs(y0 - y1) < 0.1 and abs(x1 - x0) > 1:
            s_ = 1 if x1 > x0 else -1
            cruces = sorted(((vx, o) for (vx, va, vb, o) in verticales
                             if o is not l and min(x0, x1) + 8 < vx < max(x0, x1) - 8 and va + 3 < y0 < vb - 3),
                            key=lambda t_: s_ * t_[0])
            for vx, o in cruces:
                rr = max(6, o["ancho"] / 2 + 4)
                d += f" L{vx - s_ * rr:.1f},{y0:.1f} A{rr},{rr} 0 0 {1 if s_ > 0 else 0} {vx + s_ * rr:.1f},{y0:.1f}"
        d += f" L{x1:.1f},{y1:.1f}"
    da = f' stroke-dasharray="{l["trazo"]}"' if l["trazo"] else ""
    return f'<path d="{d}" fill="none" stroke="{l["color"]}" stroke-width="{l["ancho"]}" stroke-linejoin="miter"{da}/>'


def armar_svg(vista, vainas, nombre):
    x0, y0, w, h = vista
    verticales = verticales_de(lineas) + verticales_de(vainas)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}" width="{w}" height="{h}" '
           f'font-family="Arial, Liberation Sans, Helvetica, sans-serif"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#FFFFFF"/>'
           + "".join(fondo) + "".join(cables) + "".join(render(l, verticales) for l in lineas) + "".join(frente) + "</svg>")
    salida = AQUI / "img" / nombre
    salida.write_text(svg, encoding="utf-8")
    print(salida)


def advertencia_icono(capa, x, y, a=16):
    capa.append(f'<path d="M{x},{y} l{a / 2},{-a * 0.87} l{a / 2},{a * 0.87} z" fill="#F2C200" stroke="#000" stroke-width="1"/>')
    texto(x + a / 2, y - a * 0.15, "!", a * 0.7, "middle", peso="bold", capa=capa)


ROJO, MARRON, AZUL, GRIS_W = "#D32F2F", "#7B4A2A", "#2A62C9", "#4D4D4D"
EX_X, EX_Y, EX_W = 450, 980, 560          # tablero de excitación: posición de referencia de cableado_interno


def cableado_interno(tx):
    """Conexiones internas del tablero de excitación."""
    t = tx["sup"]
    k = EX_W / 560                       # coordenadas de referencia: tablero en (450, 980) con 560 de ancho
    gx = lambda v: EX_X + (v - 450) * k
    gy = lambda v: EX_Y + (v - 980) * k
    # salida del autotransformador (ficha) → bornes 1 y 7 (inferiores), por la izquierda de la bornera
    yi = tx["y_inf"]
    linea([tx["N"], (tx["N"][0], gy(1030)), (gx(566), gy(1030)), (gx(566), yi + 10), (t[0], yi + 10), (t[0], yi)], AZUL, 1.8)
    linea([tx["L"], (tx["L"][0], gy(1037)), (gx(556), gy(1037)), (gx(556), yi + 46), (t[6] + 4, yi + 46), (t[6] + 4, yi + 20), (t[6], yi + 12), (t[6], yi)], MARRON, 1.8)
    # circuito de la espira auxiliar (sin conexión con el de excitación)
    a1, a2 = tx["aux"]
    bx, bya, byb = tx["bus"]
    ms, mi = tx["mcb_sup"], tx["mcb_inf"]
    yai = tx["y_aux_inf"]
    xg = tx["mcb_der"] + 8
    linea([(a1, yai), (a1, yai + 10), (xg, yai + 10), (xg, ms[1] - 18), (ms[0], ms[1] - 18), (ms[0], ms[1] - 3)], GRIS_W, 1.5)
    linea([(mi[0], mi[1] + 3), (mi[0], gy(1254)), (gx(948), gy(1254)), (gx(948), byb), (bx, byb)], GRIS_W, 1.5)
    linea([(a2, yai), (a2, yai + 15), (gx(962), yai + 15), (gx(962), bya), (bx, bya)], GRIS_W, 1.5)
    circ(cables, bx, bya, 1.8, "#C8102E")
    circ(cables, bx, byb, 1.8, "#2A62C9")
    # fichas banana en paralelo con la espira auxiliar
    linea([tx["j_neg"], (tx["j_neg"][0], yai + 5), (a1, yai + 5)], "#151515", 1.4)
    circ(cables, a1, yai + 5, 2.2, "#151515")
    linea([tx["j_roj"], (gx(962), tx["j_roj"][1]), (gx(962), yai + 15)], ROJO, 1.4)
    circ(cables, gx(962), yai + 15, 2.2, ROJO)


# ======================================================================== FIGURA 1: esquema general
# Hoja A3 apaisada: columnas PC/alimentación · control box y tablero EL CID · tablero de excitación y autotransformador · estator.
W, H = 2600, 1500
fondo.append(f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="none" stroke="{NEG}" stroke-width="1"/>')
texto(W / 2, 82, "ESQUEMA GENERAL DE CONEXIONES", 42, "middle")
EX_X, EX_Y, EX_W = 1150, 1040, 560


def rotulo(x, y, t, color=NEG):
    """Rótulo sobre la línea a la que pertenece (fondo blanco que corta la línea)."""
    a = len(t) * T * 0.53 + 18
    rect(frente, x - a / 2, y - T * 0.62, a, T * 1.2, "#FFFFFF")
    texto(x, y + T * 0.36, t, T, "middle", color)


# ---------------------------------------------------------------- equipos
cb = control_box(760, 190, 240)
texto(880, 168, "Control box", T, "middle")
te = tablero_elcid(760, 660, 240)
texto(745, 745, "Tablero EL CID", T, "end")
tx = tablero_excitacion(EX_X, EX_Y, EX_W)
texto(EX_X + EX_W * 0.68, EX_Y + tx["h"] + 42, "Tablero de excitación", T, "middle")
pc(230, 505, "")
texto(285, 625, "PC GRIS", T, "middle")
pc(230, 760, "")
texto(285, 880, "PC EL CID", T, "middle")
z1 = zapatilla(110, 1180, "")
red(147, 1250)
linea([(170, 1214), (170, 1250)], NEG, 2)
circ(frente, 236, 1197, 4, "#FFFFFF", VERDE, 1.6)
# autotransformador, a la altura de la ficha del tablero de excitación
fy_ = tx["ficha"][1]
vx, vy = 1830, fy_ - 50
rect(fondo, vx, vy, 140, 100, "#FFFFFF", NEG, 1.4)
fondo.append(f'<path d="M{vx + 70},{vy + 20} ' + " ".join("a7,6 0 1 1 0,12" for _ in range(5)) + f'" fill="none" stroke="{NEG}" stroke-width="1.4"/>')
poli(fondo, [(vx + 85, vy + 18), (vx + 59, vy + 82)], NEG, 1.4)
fondo.append(f'<path d="M{vx + 59},{vy + 82} l-1,-9 l7,4 z" fill="{NEG}"/>')
texto(vx + 70, vy + 136, "Autotransformador", T, "middle")
red(vx + 175, vy + 15)
linea([(vx + 140, vy + 50), (vx + 175, vy + 50)], NEG, 2)
poli(cables, [(vx, fy_), tx["ficha"]], "#111", 6)

# ---------------------------------------------------------------- estator
c1, c2, R, r = (2150, 520), (2295, 420), 105, 65
ax_, ay_ = c2[0] - c1[0], c2[1] - c1[1]
nx_, ny_ = -ay_ / math.hypot(ax_, ay_), ax_ / math.hypot(ax_, ay_)
circ(fondo, *c2, R, "#FFFFFF", NEG, 1.4)
for s_ in (1, -1):
    poli(fondo, [(c1[0] + s_ * R * nx_, c1[1] + s_ * R * ny_), (c2[0] + s_ * R * nx_, c2[1] + s_ * R * ny_)], NEG, 1.4)
circ(fondo, *c1, R, "#FFFFFF", NEG, 1.4)
circ(fondo, *c1, r, "#FFFFFF", NEG, 1.4)
texto(2330, 290, "Núcleo estatórico", T, "middle")
ry0 = c1[1] - r + 5
rect(frente, c1[0] - 22, ry0, 44, 14, "#4A4F54", "#2B2F33", 1, 3)
rect(frente, c1[0] - 25, ry0 + 12, 50, 6, "#1E1E1E", "none", 0, 3)
for dx in (-18, -6, 6, 18):
    circ(frente, c1[0] + dx, ry0 + 15, 1.6, "#777")
rect(frente, c1[0] - 6, ry0 + 3, 12, 5, NAR, "none", 0, 1)
poli(frente, [(c1[0] - 26, ry0 + 8), (c1[0] - 70, ry0 + 50)], NEG, 1)
texto(c1[0] - 76, ry0 + 64, "Robot", T, "end")

# ---------------------------------------------------------------- cable del robot: del control box al robot
xa, yp = c1[0], cb["principal"][1]
xb = 1400
poli(cables, [(xa, ry0), (xa, yp), (cb["principal"][0], yp)], "#111", 6)
cables.append(f'<path d="M{xb},{yp - 3.5} L{xb + 14},{yp - 3.5} L{xb + 14},{yp + 3.5} L{xb},{yp + 3.5} Z" fill="#000"/>')
cables.append(f'<path d="M{xb - 2},{yp - 4.5} L{xb + 2},{yp - 4.5} L{xb + 2},{yp + 4.5} L{xb - 2},{yp + 4.5} Z" fill="#000"/>')
xc = 1370
cables.append(f'<path d="M{xb - 2},{yp + 2} C{xb - 22},{yp + 2} {xc},{yp + 6} {xc},{yp + 26} L{xc},{te["captor"][1]} '
              f'L{te["captor"][0]:.1f},{te["captor"][1]:.1f}" stroke="#000" stroke-width="1.6" fill="none"/>')
rotulo(1750, yp, "Cable del robot")

# ---------------------------------------------------------------- control box ↔ tablero EL CID y PC
linea([cb["bnc"], (1330, cb["bnc"][1]), (1330, te["pos"][1]), te["pos"]])
for k_, (con, txt) in enumerate(((te["pos"], "Señal de posición"), (te["captor"], "Señal del captor"))):
    texto(1012, con[1] - 9, txt, T)
    frente.append(f'<path d="M{con[0] + 4:.1f},{con[1]:.1f} l12,-6 l0,12 z" fill="{NEG}"/>')
linea([cb["eth"], (1025, cb["eth"][1]), (1025, 520), (340, 520)])
rotulo(600, 520, "Ethernet")
linea([cb["usb"], (1045, cb["usb"][1]), (1045, 570), (340, 570)])
rotulo(600, 570, "USB")
linea([te["usb"], (1010, te["usb"][1]), (1010, 635), (380, 635), (380, 800), (340, 800)])
rotulo(600, 635, "USB")
# ---------------------------------------------------------------- alimentaciones y tierras
linea([cb["iec"], (z1[0], cb["iec"][1]), (z1[0], 1180)])
rotulo(450, cb["iec"][1], "Alimentación")
linea([(230, 540), (z1[1], 540), (z1[1], 1180)])
linea([(230, 800), (z1[2], 800), (z1[2], 1180)])
linea([te["iec"], (z1[3], te["iec"][1]), (z1[3], 1180)])
rotulo(600, te["iec"][1], "Alimentación")
linea([te["ground"], (400, te["ground"][1]), (400, 1197), (240, 1197)], VERDE, 2.6)
rotulo(600, te["ground"][1], "Tierra", VERDE)
linea([(110, 1197), (80, 1197), (80, 1226)], VERDE, 2.6)
simbolo_tierra(80, 1238)
linea([(c1[0], c1[1] + R), (c1[0], c1[1] + R + 40)], VERDE, 2.6)
simbolo_tierra(c1[0], c1[1] + R + 52)
texto(c1[0] + 26, c1[1] + R + 50, "Tierra", T, color=VERDE)
# ---------------------------------------------------------------- corriente de excitación (bornes 6 y 7 → tablero EL CID)
linea([te["b1"], (te["b1"][0], 1007), (tx["sup"][5], 1007), (tx["sup"][5], tx["y_sup"])], ROJO, 2.4)
linea([te["b2"], (te["b2"][0], 995), (tx["sup"][6], 995), (tx["sup"][6], tx["y_sup"])], ROJO, 2.4)
texto(1015, 946, "Corriente de", T, color=ROJO)
texto(1015, 981, "excitación", T, color=ROJO)
# ---------------------------------------------------------------- cable de excitación de 5 hilos (extremo A al frente, extremo B al fondo)
pf, pb = (2122, 550), (2267, 420)
sup_x = sum(tx["sup"][:5]) / 5
inf_x = sum(tx["sup"][1:6]) / 5
yA, yB = tx["y_sup"] - 36, tx["y_inf"] + 36
cable_5_hilos([(sup_x, yA), (sup_x, 900), (2070, 900), (2070, pf[1]), pf], (sup_x, yA), tx["sup"][:5], tx["y_sup"])
cable_5_hilos([(inf_x, yB), (inf_x, 1420), (2560, 1420), (2560, pb[1]), pb], (inf_x, yB), tx["sup"][1:6], tx["y_inf"], desde_abajo=True)
poli(cables, [pf, pb], "#111", 6, extra=' stroke-dasharray="10 7"')
cableado_interno(tx)
# ---------------------------------------------------------------- espira auxiliar
a1, a2 = tx["aux"]
pfa, pba = (2110, 575), (2247, 450)
linea([(a1, tx["y_aux"]), (a1, 940), (2110, 940), pfa], VIOL, 2)
linea([(a2, tx["y_aux"]), (a2, 952), (2530, 952), (2530, pba[1]), pba], VIOL, 2)
poli(cables, [pfa, pba], VIOL, 2, extra=' stroke-dasharray="7 5"')
rotulo(2320, 952, "Espira auxiliar", VIOL)
# ---------------------------------------------------------------- instrumentos
mm = multimetro(1760, 1170)
texto(1801, 1345, "Voltímetro", T, "middle")
def punta(p0, p1, col, baja):
    cables.append(f'<path d="M{p0[0]:.1f},{p0[1]:.1f} C{p0[0] + 60:.1f},{baja:.1f} {p1[0]:.1f},{baja + 40:.1f} {p1[0]:.1f},{p1[1]:.1f}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>')
punta(tx["j_roj"], mm["v"], "#C8102E", 1180)
punta(tx["j_neg"], mm["com"], "#151515", 1195)
pinza(2110, 760, 60, -90)
texto(2165, 850, "Pinza amperométrica", T)
# ---------------------------------------------------------------- advertencia vinculada a la ficha del autotransformador
# Recuadro de advertencia con flecha a la ficha (tapa azul en el borde superior del tablero de excitación).
bx_, by_, bw_, bh_ = 1440, 690, 575, 160
rect(frente, bx_, by_, bw_, bh_, "#FFF6CC", "#C9A100", 2, 6)
advertencia_icono(frente, bx_ + 16, by_ + 56, 34)
texto(bx_ + 62, by_ + 50, "Ficha del autotransformador:", T, peso="bold")
texto(bx_ + 62, by_ + 95, "no manipularla con el equipo", T)
texto(bx_ + 62, by_ + 137, "conectado a la red.", T)
cap = (tx["ficha"][0] - 30, tx["ficha"][1] - 30)
p0_ = (bx_ + 40, by_ + bh_)
poli(frente, [p0_, (cap[0] + 4, cap[1] - 14)], "#C9A100", 3)
frente.append(f'<path d="M{cap[0] + 4:.1f},{cap[1] - 2:.1f} l-9,-18 l18,0 z" fill="#C9A100"/>')

texto(W - 36, H - 34, "Mecanálisis – 00503-00-EPG001 – 28/10/2026", T, "end")

vainas = [{"pts": p, "ancho": 6} for p in ([(sup_x, 900), (sup_x, yA)], [(2070, pf[1]), (2070, 900)], [(inf_x, yB), (inf_x, 1420)],
                                         [(2560, pb[1]), (2560, 1420)], [(xa, ry0), (xa, yp)])]
armar_svg((0, 0, W, H), vainas, "esquema_general.svg")
