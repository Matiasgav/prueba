"""Eslabón de ancho regulable con mecanismo de doble Scott Russell.

Modelo paramétrico en CadQuery. Ejes globales:
  X = ancho (dimensión regulable, 35..105 mm)
  Y = largo (190 mm, dirección de los ejes de acople)
  Z = espesor (13 mm)

Piezas:
  barra A        lado fijo, con 2 pivotes del paralelogramo (Q1, Q2)
  barra B        lado con guía para el carro y pivote fijo O del Scott Russell
  carro          se desliza en la guía de B; lleva los pivotes P1, P2
  eslabón largo  x2, lados del paralelogramo (Q-P, 2L = 92 mm)
  eslabón corto  une O (en B) con el punto medio C del eslabón largo 1 (L = 46 mm)
  perno          D3 en todas las articulaciones
  tornillo       M4 de bloqueo con perilla moleteada (regulación manual)

Uso:
  python eslabon.py            exporta piezas, ensambles y el visor 3D (visor.html)
"""

import json
import math
import os

import cadquery as cq

# ---------------------------------------------------------------- parámetros
LARGO = 190.0          # largo del eslabón (Y)
ESP = 13.0             # espesor (Z)
W_MIN, W_MAX = 35.0, 105.0
BW = 14.0              # ancho de cada barra lateral (X)

D_ACOPLE = 5.0         # agujeros de acople
P_ACOPLE = 10.0        # profundidad
Z_EJE = ESP / 2        # ejes centrados en el espesor
X_EJE = BW / 2         # ejes centrados en el ancho de cada barra

E_PIV = 4.0            # distancia del pivote a la cara interior de la barra
L2 = 92.0              # largo del eslabón largo (centro a centro) = 2L
L1 = L2 / 2            # largo del eslabón corto = L
Y0 = 22.0              # Y de O y Q1 (recta del Scott Russell)
DP = 48.0              # separación de los pivotes del paralelogramo

D_PERNO = 3.0
D_AG_PERNO = 3.2
ANCHO_ESL = 7.0
HOLG = 0.2

# capas en Z
Z_LARGO = (4.0, 7.5)   # eslabones largos
Z_CORTO = (8.5, 11.5)  # eslabón corto
Z_CANAL = (1.5, 11.5)  # canal del carro en B
Z_CARRO = (1.7, 11.3)

# carro (coordenadas locales: P1 en y=0, cara interior en x=0)
CARRO_Y = (-6.0, DP + 14.0)
CARRO_X = 10.8
Y_TORN = DP + 8.0      # tornillo de bloqueo

CANAL_Y = (44.0, 176.0)
CANAL_X = 11.0         # la pared exterior de B queda de 3 mm


def s_de(w):
    """Distancia entre las rectas de pivotes de A y B."""
    return w - 2 * (BW - E_PIV)


def p_de(w):
    """Distancia O-P1 a lo largo de B (posición del carro)."""
    s = s_de(w)
    return math.sqrt(L2 ** 2 - s ** 2)


def y_tornillo(w):
    return Y0 + p_de(w) + Y_TORN


Y_RANURA = (y_tornillo(W_MAX) - 2.7, y_tornillo(W_MIN) + 2.7)


# ---------------------------------------------------------------- utilidades
def caja(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cil_z(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def agujeros_acople(barra, x):
    for y0, sentido in ((0.0, 1), (LARGO, -1)):
        h = (cq.Workplane("XZ", origin=(0, y0, 0)).center(x, Z_EJE)
             .circle(D_ACOPLE / 2).extrude(-sentido * P_ACOPLE))
        barra = barra.cut(h)
    return barra


# ---------------------------------------------------------------- piezas
def barra_a():
    """Lado fijo. Cara interior en x=BW. Pivotes Q1, Q2 en x = BW - E_PIV."""
    b = caja(0, BW, 0, LARGO, 0, ESP)
    b = agujeros_acople(b, X_EJE)
    xp = BW - E_PIV
    # horquilla para los eslabones largos
    b = b.cut(caja(xp - 4 - HOLG, BW + 1, Y0 - 4.5, Y0 + DP + 50,
                   Z_LARGO[0] - HOLG, Z_LARGO[1] + HOLG))
    for y in (Y0, Y0 + DP):
        b = b.cut(cil_z(xp, y, D_AG_PERNO, -1, ESP + 1))
    # alivio para el extremo C del eslabón corto cuando el ancho es mínimo
    b = b.cut(caja(BW - 1.5, BW + 1, Y0 + 10, Y0 + 58,
                   Z_CORTO[0] - HOLG, Z_CORTO[1] + HOLG))
    return b


def barra_b():
    """Lado con carro. Local: cara interior en x=0, exterior en x=BW."""
    b = caja(0, BW, 0, LARGO, 0, ESP)
    b = agujeros_acople(b, X_EJE)
    xp = E_PIV
    # canal guía del carro (abierto hacia el lado interior)
    b = b.cut(caja(-1, CANAL_X, CANAL_Y[0], CANAL_Y[1], *Z_CANAL))
    # horquilla del eslabón corto en O
    b = b.cut(caja(-1, xp + 4 + HOLG, Y0 - 4.5, Y0 + 50,
                   Z_CORTO[0] - HOLG, Z_CORTO[1] + HOLG))
    b = b.cut(cil_z(xp, Y0, D_AG_PERNO, -1, ESP + 1))
    # ranura del tornillo de bloqueo en la pared exterior
    largo_r = Y_RANURA[1] - Y_RANURA[0]
    ranura = (cq.Workplane("YZ", origin=(CANAL_X - 1, 0, 0))
              .center((Y_RANURA[0] + Y_RANURA[1]) / 2, Z_EJE)
              .slot2D(largo_r, 4.4).extrude(BW - CANAL_X + 2))
    b = b.cut(ranura)
    # escala grabada: marca cada 5 mm de ancho, número cada 10
    for w in range(int(W_MIN), int(W_MAX) + 1, 5):
        y = y_tornillo(w)
        alto = 2.6 if w % 10 == 5 else 1.6
        b = b.cut(caja(BW - 0.4, BW + 1, y - 0.25, y + 0.25, 13 - 0.6 - alto, 13 - 0.6))
        if w % 10 == 5:
            txt = (cq.Workplane("YZ", origin=(BW - 0.4, 0, 0))
                   .center(y, 2.6).text(str(w), 2.6, 1.0, kind="regular"))
            b = b.cut(txt)
    return b


def carro():
    c = caja(0, CARRO_X, CARRO_Y[0], CARRO_Y[1], *Z_CARRO)
    # ranura para los eslabones largos (solo hasta P2: los eslabones van hacia -Y)
    c = c.cut(caja(-1, E_PIV + 4 + HOLG, CARRO_Y[0] - 1, DP + 4 + 0.5,
                   Z_LARGO[0] - HOLG, Z_LARGO[1] + HOLG))
    for y in (0.0, DP):
        c = c.cut(cil_z(E_PIV, y, D_AG_PERNO, 0, ESP))
    # agujero roscado M4 del tornillo de bloqueo (modelado a diámetro nominal)
    rosca = (cq.Workplane("YZ", origin=(CARRO_X + 0.1, 0, 0)).center(Y_TORN, Z_EJE)
             .circle(2).extrude(-7))
    return c.cut(rosca)


def eslabon(largo, z, agujero_medio):
    """Eslabón plano en el plano XY, de (0,0) a (largo,0)."""
    e = (cq.Workplane("XY").workplane(offset=z[0]).center(largo / 2, 0)
         .slot2D(largo + ANCHO_ESL, ANCHO_ESL).extrude(z[1] - z[0]))
    xs = [0.0, largo] + ([largo / 2] if agujero_medio else [])
    for x in xs:
        e = e.cut(cil_z(x, 0, D_AG_PERNO, z[0] - 1, z[1] + 1))
    return e


def perno(z0, z1):
    return cil_z(0, 0, D_PERNO, z0, z1)


def separador():
    return cil_z(0, 0, 6, Z_LARGO[1], Z_CORTO[0]).cut(cil_z(0, 0, D_AG_PERNO, 0, ESP))


def tornillo():
    """Local: eje en X, cabeza fuera de la cara exterior de B (x>=BW)."""
    vastago = cq.Workplane("YZ", origin=(BW + 1, 0, 0)).circle(2).extrude(-(BW + 1 - CARRO_X + 6))
    arandela = cq.Workplane("YZ", origin=(BW, 0, 0)).circle(4.5).circle(2.2).extrude(1)
    perilla = cq.Workplane("YZ", origin=(BW + 1, 0, 0)).polygon(16, 12).extrude(6)
    return vastago.union(arandela).union(perilla)


# ---------------------------------------------------------------- ensamble
PIEZAS = {
    "barra_A": barra_a,
    "barra_B": barra_b,
    "carro": carro,
    "eslabon_largo": lambda: eslabon(L2, Z_LARGO, True),
    "eslabon_corto": lambda: eslabon(L1, Z_CORTO, False),
    "perno_barra": lambda: perno(0, ESP),
    "perno_carro": lambda: perno(*Z_CARRO),
    "perno_C": lambda: perno(Z_LARGO[0], Z_CORTO[1]),
    "separador": separador,
    "tornillo": tornillo,
}

COLORES = {
    "barra_A": (0.55, 0.60, 0.66), "barra_B": (0.55, 0.60, 0.66),
    "carro": (0.85, 0.45, 0.15), "eslabon_largo": (0.20, 0.45, 0.80),
    "eslabon_corto": (0.15, 0.65, 0.45), "perno_barra": (0.85, 0.85, 0.85),
    "perno_carro": (0.85, 0.85, 0.85), "perno_C": (0.85, 0.85, 0.85),
    "separador": (0.85, 0.85, 0.85), "tornillo": (0.20, 0.20, 0.22),
}


def poses(w):
    """Lista de (nombre_instancia, pieza, (x, y, z), ángulo_Z_grados) para un ancho w."""
    assert W_MIN - 1e-9 <= w <= W_MAX + 1e-9, "ancho fuera de rango"
    s, p = s_de(w), p_de(w)
    xb = w - BW                       # origen local de B
    xq = BW - E_PIV                   # recta de pivotes de A
    xo = xb + E_PIV                   # recta de pivotes de B (O, P1, P2)
    ang_largo = math.degrees(math.atan2(p, s))          # de Q hacia P
    ang_corto = math.degrees(math.atan2(p / 2, -s / 2))  # de O hacia C
    yc = Y0 + p / 2
    return [
        ("barra_A", "barra_A", (0, 0, 0), 0),
        ("barra_B", "barra_B", (xb, 0, 0), 0),
        ("carro", "carro", (xb, Y0 + p, 0), 0),
        ("eslabon_largo_1", "eslabon_largo", (xq, Y0, 0), ang_largo),
        ("eslabon_largo_2", "eslabon_largo", (xq, Y0 + DP, 0), ang_largo),
        ("eslabon_corto", "eslabon_corto", (xo, Y0, 0), ang_corto),
        ("perno_Q1", "perno_barra", (xq, Y0, 0), 0),
        ("perno_Q2", "perno_barra", (xq, Y0 + DP, 0), 0),
        ("perno_O", "perno_barra", (xo, Y0, 0), 0),
        ("perno_P1", "perno_carro", (xo, Y0 + p, 0), 0),
        ("perno_P2", "perno_carro", (xo, Y0 + p + DP, 0), 0),
        ("perno_C", "perno_C", (w / 2, yc, 0), 0),
        ("separador_C", "separador", (w / 2, yc, 0), 0),
        ("tornillo", "tornillo", (xb, Y0 + p + Y_TORN, Z_EJE), 0),
    ]


def ensamble(w, piezas):
    a = cq.Assembly(name=f"eslabon_W{w:g}")
    for nombre, pieza, (x, y, z), ang in poses(w):
        loc = cq.Location(cq.Vector(x, y, z), cq.Vector(0, 0, 1), ang)
        a.add(piezas[pieza], name=nombre, loc=loc, color=cq.Color(*COLORES[pieza]))
    return a


def interferencias(w, piezas):
    """Volumen de intersección entre cada par de piezas (debe ser ~0)."""
    solidos = []
    for nombre, pieza, (x, y, z), ang in poses(w):
        sh = piezas[pieza].val().rotate((0, 0, 0), (0, 0, 1), ang).translate(cq.Vector(x, y, z))
        solidos.append((nombre, sh))
    res = []
    for i in range(len(solidos)):
        for j in range(i + 1, len(solidos)):
            v = solidos[i][1].intersect(solidos[j][1]).Volume()
            if v > 0.01:
                res.append((solidos[i][0], solidos[j][0], v))
    return res


def malla_json(forma, tol=0.05):
    verts, tris = forma.val().tessellate(tol, 0.3)
    return {
        "v": [round(c, 3) for p in verts for c in (p.x, p.y, p.z)],
        "i": [k for t in tris for k in t],
    }


if __name__ == "__main__":
    aqui = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(aqui, "salida")
    os.makedirs(os.path.join(out, "piezas"), exist_ok=True)
    piezas = {k: f() for k, f in PIEZAS.items()}

    for k, f in piezas.items():
        cq.exporters.export(f, os.path.join(out, "piezas", f"{k}.step"))
        cq.exporters.export(f, os.path.join(out, "piezas", f"{k}.stl"), tolerance=0.02)

    for w in (W_MIN, 70.0, W_MAX):
        ensamble(w, piezas).save(os.path.join(out, f"ensamble_W{w:g}.step"))

    # verificación de interferencias en todo el recorrido
    for w in [W_MIN + 2.5 * k for k in range(int((W_MAX - W_MIN) / 2.5) + 1)]:
        inter = interferencias(w, piezas)
        print(f"W={w:g}: s={s_de(w):.1f} p={p_de(w):.2f} tornillo y={y_tornillo(w):.1f} "
              f"interferencias={inter or 'ninguna'}")

    geo = {
        "param": {"LARGO": LARGO, "ESP": ESP, "W_MIN": W_MIN, "W_MAX": W_MAX, "BW": BW,
                  "E_PIV": E_PIV, "L2": L2, "Y0": Y0, "DP": DP, "Y_TORN": Y_TORN, "Z_EJE": Z_EJE},
        "colores": {k: "#%02x%02x%02x" % tuple(int(c * 255) for c in v) for k, v in COLORES.items()},
        "mallas": {k: malla_json(f) for k, f in piezas.items()},
    }
    with open(os.path.join(aqui, "visor_plantilla.html")) as fh:
        plantilla = fh.read()
    with open(os.path.join(aqui, "visor.html"), "w") as fh:
        fh.write(plantilla.replace("/*GEOMETRIA*/null", json.dumps(geo, separators=(",", ":"))))
    print("listo:", out)
