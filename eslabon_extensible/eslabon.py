"""Eslabón de ancho regulable con mecanismo de doble Scott Russell — versión 5.

Modelo paramétrico en CadQuery para mecanizado CNC en aluminio 7075-T651.
Ejes globales:
  X = ancho (dimensión regulable, 35..105 mm)
  Y = largo (190 mm, dirección de los ejes de acople)
  Z = espesor (13 mm)

Capas a lo largo del espesor:
  alas de B (z 0..1,5 y 11,5..13)  riel en C: tapan el carro y trabajan con la columna
  carro (z 1,6..11,4)               horquillas de P1 y P2 entre las alas
  capa media (z 3..10)              eslabones largos 1 y 2 (7 mm); el 1 se engrosa en el vientre
  capa central (z 4,2..8,8)         eslabón corto, embutido en el eslabón 1 (C) y en B (O)
Todos los pernos quedan en doble corte.

Los huecos de cada pieza se calculan barriendo el contorno de los eslabones por todo el rango
de anchos, así se quita solo el material imprescindible.

Piezas:
  barra A        lado fijo, pivotes Q1 y Q2
  barra B        columna exterior + bloque del pivote O + riel en C del carro, abierto en y = 190
  tapa           cierra la boca del riel en y = 190
  carro          corre en el riel de B, retenido por los labios de las alas; lleva P1 y P2
  eslabón 1      lado del paralelogramo con vientre en gota hacia B y embocadura del corto en C
  eslabón 2      lado del paralelogramo (biela), vientre hacia A
  eslabón corto  una pieza, O-C
  pernos Ø5      pasadores ISO 8734 m6 templados, a presión en las mejillas; el ojo gira sobre ellos
  arandela       resorte de disco 8 × 5,2 × 0,4 en Q1, Q2, P1 y P2 (≈ 250 N de precarga)
  arandela_corto arandela ondulada en O y C (solo juego axial)
La traba del carro queda pendiente: el modelo no la incluye.

Uso:
  python eslabon.py            exporta piezas, ensambles, verificación y visor 3D (visor.html)
"""

import json
import math
import os

import cadquery as cq
import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

# ---------------------------------------------------------------- parámetros
LARGO = 190.0
ESP = 13.0
W_MIN, W_MAX = 35.0, 105.0

D_ACOPLE, P_ACOPLE = 5.0, 10.0
ACORTE_A = 25.0              # la barra A (la fina) se acorta por la punta del voladizo (y = 190)
LARGO_A = LARGO - ACORTE_A
X_ACOPLE = 5.0               # eje de acople a 5 mm de la cara exterior de cada barra
Z_EJE = ESP / 2

D_PERNO = 5.0                 # pasador templado rectificado Ø5 g6 (ISO 8734 5m6 como referencia de material)
R_ANILLO = D_PERNO / 2 + 2.0  # material mínimo alrededor de un perno en barras y carro
HOLG = 0.1                    # juego entre capas
HOLG_PLANO = 0.3              # juego en el plano entre piezas que se mueven

# capas
T_ESL = 7.0                                # espesor de los eslabones largos
Z_MED = (ESP / 2 - T_ESL / 2, ESP / 2 + T_ESL / 2)   # eslabones largos
ALA = 1.2                                 # alas del riel de B: tapan el carro y trabajan con la columna
Z_CANAL = (ALA, ESP - ALA)                 # interior del riel
Z_CARRO = (ALA + HOLG, ESP - ALA - HOLG)   # el carro corre entre las alas
T_CORTO = 2.5                              # espesor del eslabón corto (solo trabaja a tracción y compresión)
Z_CORTO = (ESP / 2 - T_CORTO / 2, ESP / 2 + T_CORTO / 2)   # centrado, embutido en el eslabón 1
Z_EMBOC = (Z_CORTO[0] - HOLG, Z_CORTO[1] + HOLG)
Z_MED_CORTE = (Z_MED[0] - HOLG, Z_MED[1] + HOLG)
Z_PLACA_CORTE = (Z_EMBOC,)                 # el corto barre solo la capa central

# Geometría principal. configurar() recalcula todo lo que depende de estos valores.
#   D_A      línea de pivotes Q1-Q2, medida desde la cara exterior de A
#   E_B      línea de pivotes O-P1-P2, medida desde la cara interior de B
#   COLUMNA  ancho de la columna maciza de B detrás del carro
#   GAP_MIN  luz entre barras a W mínimo
COLA = 7.0                                 # carro por encima de P2: solo cierra el ojo de P2
Y_FIN_CARRO = 185.0                        # el canal corre por dentro del eje de acople (otra zona de la columna)
R_OJO_MAX = 4.5                            # ojo máximo: deja nervio en el fondo de las horquillas
Y0 = 20.0                                  # recta O-Q1 (deja lugar al cable por encima de los acoples)
R_CORTO = 4.5                              # semiancho del eslabón corto (ojo igual a los largos)
# Vientres de los eslabones largos (arco R_GOTA tangente a los ojos). Profundidades máximas
# halladas con ajuste_vientres.py: el eslabón 1 no toca la columna de B a W mínimo y el 2 no
# come la barra A más allá del fondo que ya deja el ojo.
R_GOTA = 60.0
DX_GOTA1 = 0.0                             # vientre simétrico: los dos eslabones largos son iguales, espejados
QUILLA = 9.9                                # profundidad del vientre (eslabón 1 hacia B, eslabón 2 hacia A)
PANZA_2 = QUILLA
# pivotes de los eslabones largos (Q1, Q2, P1, P2): resorte de disco 8 × 5,2 × 0,4 (h0 0,2) en un rebaje
# de la cara superior del ojo. Con el ojo apoyado en la mejilla de abajo queda comprimido 0,15 mm: ≈ 250 N.
# El modelo dibuja el ojo centrado y el resorte como un anillo plano del alto que le queda en esa posición.
ARANDELA = dict(d_int=D_PERNO + 0.2, d_ext=8.0, rebaje=0.25, alto=0.35)
# pivotes del eslabón corto (O, C): arandela ondulada liviana, solo para el juego axial
ARANDELA_CORTO = dict(d_int=D_PERNO + 0.2, d_ext=7.9, rebaje=0.15, alto=0.25)


def configurar(d_a=10.0, e_b=6.3, columna=8.6, gap_min=0.8, margen_l2=4.0):
    global D_A, E_B, COLUMNA, GAP_MIN, C_CARRO, BWB, BWA, D_B, S_MIN, L2, L1, P_MAX, DP
    global SEP_MIN, R_OJO, CARRO_Y
    D_A, E_B, COLUMNA, GAP_MIN = d_a, e_b, columna, gap_min
    C_CARRO = E_B + R_ANILLO + 0.6
    BWB = C_CARRO + COLUMNA
    BWA = W_MIN - GAP_MIN - BWB
    D_B = BWB - E_B
    S_MIN = W_MIN - D_A - D_B
    L2 = round(W_MAX - D_A - D_B + margen_l2, 1)
    L1 = L2 / 2
    P_MAX = math.sqrt(L2 ** 2 - S_MIN ** 2)
    DP = math.floor(Y_FIN_CARRO - COLA - Y0 - P_MAX)
    # separación perpendicular entre eslabones a W mínimo -> radio de ojo
    SEP_MIN = DP * S_MIN / L2
    R_OJO = min(R_OJO_MAX, math.floor((SEP_MIN - 0.5) / 2 * 20) / 20)
    CARRO_Y = (-6.0, DP + COLA)


# Guía del carro: las alas de B terminan en un labio que baja junto a la cara interior y
# retiene al carro cuando los eslabones lo tiran hacia A. No hay guía mecanizada en la columna.
LABIO_X = 1.5                              # ancho del labio (desde la cara interior de B)
LABIO_Z = 0.9                              # cuánto baja el labio desde el ala


def cinematica(w):
    xq = D_A
    xo = w - D_B
    s = xo - xq
    p = math.sqrt(L2 ** 2 - s ** 2)
    q1 = np.array([xq, Y0])
    p1 = q1 + np.array([s, p])
    c = (q1 + p1) / 2
    o = np.array([xo, Y0])
    return dict(
        s=s, p=p, xb=w - BWB, Q1=q1, Q2=q1 + [0, DP], P1=p1, P2=p1 + [0, DP], C=c, O=o,
        ang_largo=math.atan2(p, s), ang_corto=math.atan2(c[1] - o[1], c[0] - o[0]),
    )


configurar()


# ---------------------------------------------------------------- contornos 2D (marco local del miembro)
def _estadio(largo, r):
    return Point(0, 0).buffer(r, 64).union(Point(largo, 0).buffer(r, 64)).convex_hull


def _panza(largo, r, prof, lado):
    """Contorno de un eslabón con un lado recto y el otro en arco ("panza de pez").

    El arco grande es tangente a los dos ojos (radio r) y llega a `prof` del eje en el medio.
    lado = -1: panza hacia -y local; +1: hacia +y. Devuelve la lista de tramos
    [("linea", a, b) | ("arco", a, medio, b)] en sentido horario para lado = -1.
    """
    m = largo / 2
    rb = (m ** 2 + prof ** 2 - r ** 2) / (2 * (prof - r))
    cb = np.array([m, -prof + rb])
    q, p = np.array([0.0, 0.0]), np.array([largo, 0.0])
    tq = q + r * (q - cb) / np.linalg.norm(q - cb)
    tp = p + r * (p - cb) / np.linalg.norm(p - cb)
    def en_circulo(c, rad, a0, a1):
        a = (a0 + a1) / 2
        return c + rad * np.array([math.cos(a), math.sin(a)])
    ang = lambda c, t: math.atan2(t[1] - c[1], t[0] - c[0])
    # ojo derecho: de 90° bajando hasta la tangencia (abajo a la derecha)
    # ojo izquierdo: desde la tangencia (abajo a la izquierda, entre 180° y 270°) subiendo por 180° hasta 90°
    a_tq = ang(q, tq) % (2 * math.pi)
    tramos = [
        ("linea", np.array([0.0, r]), np.array([largo, r])),
        ("arco", np.array([largo, r]), en_circulo(p, r, math.pi / 2, ang(p, tp)), tp),
        ("arco", tp, np.array([m, -prof]), tq),
        ("arco", tq, en_circulo(q, r, a_tq, math.pi / 2), np.array([0.0, r])),
    ]
    if lado > 0:
        espejo = lambda v: np.array([v[0], -v[1]])
        tramos = [(t[0], *[espejo(v) for v in t[1:]]) for t in tramos]
    return tramos


def _arco_pts(a, m, b, n=48):
    """Puntos de un arco por tres puntos."""
    ax, ay = a; bx, by = m; cx, cy = b
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax ** 2 + ay ** 2) * (by - cy) + (bx ** 2 + by ** 2) * (cy - ay) + (cx ** 2 + cy ** 2) * (ay - by)) / d
    uy = ((ax ** 2 + ay ** 2) * (cx - bx) + (bx ** 2 + by ** 2) * (ax - cx) + (cx ** 2 + cy ** 2) * (bx - ax)) / d
    c = np.array([ux, uy]); rad = np.linalg.norm(np.array(a) - c)
    t0, t1, tm = (math.atan2(v[1] - uy, v[0] - ux) for v in (a, b, m))
    # elegir el sentido que pasa por el punto medio
    def entre(x, y, z):
        return (x <= z <= y) if x <= y else (x <= z or z <= y)
    if entre(t0, t1, tm) if t0 <= t1 else entre(t0, t1 + 2 * math.pi, tm if tm >= t0 else tm + 2 * math.pi):
        ts = np.linspace(t0, t1 if t1 >= t0 else t1 + 2 * math.pi, n)
    else:
        ts = np.linspace(t0, t1 if t1 <= t0 else t1 - 2 * math.pi, n)
    return [tuple(c + rad * np.array([math.cos(t), math.sin(t)])) for t in ts]


def _tramos_a_poligono(tramos):
    pts = []
    for t in tramos:
        if t[0] == "linea":
            pts += [tuple(t[1]), tuple(t[2])]
        else:
            pts += _arco_pts(*t[1:])
    return Polygon(pts).buffer(0)


def _tramos_a_cq(wp, tramos):
    wp = wp.moveTo(*tramos[0][1])
    for t in tramos:
        if t[0] == "linea":
            wp = wp.lineTo(*t[2])
        else:
            wp = wp.threePointArc(tuple(t[2]), tuple(t[3]))
    return wp.close()


def _casco(circulos):
    """Contorno convexo de varios círculos [(x, y, r)] dados en sentido antihorario:
    tangentes exteriores rectas + arcos sobre cada círculo."""
    n = len(circulos)
    c = [np.array([x, y]) for x, y, _ in circulos]
    r = [rr for _, _, rr in circulos]
    tang = []
    for i in range(n):
        j = (i + 1) % n
        d = c[j] - c[i]
        L = np.linalg.norm(d)
        dh = d / L
        k = (r[i] - r[j]) / L
        nrm = k * dh + math.sqrt(1 - k * k) * np.array([dh[1], -dh[0]])
        tang.append((c[i] + r[i] * nrm, c[j] + r[j] * nrm))
    tramos = []
    for i in range(n):
        j = (i + 1) % n
        sale, entra = tang[i]
        tramos.append(("linea", sale, entra))
        sale_sig = tang[j][0]
        a0 = math.atan2(entra[1] - c[j][1], entra[0] - c[j][0])
        a1 = math.atan2(sale_sig[1] - c[j][1], sale_sig[0] - c[j][0])
        if a1 < a0:
            a1 += 2 * math.pi
        am = (a0 + a1) / 2
        tramos.append(("arco", entra, c[j] + r[j] * np.array([math.cos(am), math.sin(am)]), sale_sig))
    # quitar líneas de largo nulo
    return [t for t in tramos if not (t[0] == "linea" and np.linalg.norm(t[2] - t[1]) < 1e-6)]


LADO_VIENTRE1 = -1                         # -1: vientre hacia B; +1: hacia el eslabón 2 (lado de A)


def tramos_eslabon1():
    """Gota con el punto más profundo cerca de C."""
    if LADO_VIENTRE1 < 0:
        return _casco([(0.0, 0.0, R_OJO), (L1 + DX_GOTA1, -(QUILLA - R_GOTA), R_GOTA), (L2, 0.0, R_OJO)])
    return _casco([(0.0, 0.0, R_OJO), (L2, 0.0, R_OJO), (L1 + DX_GOTA1, QUILLA - R_GOTA, R_GOTA)])


def tramos_eslabon2():
    """Espejo del eslabón 1 respecto de su eje: vientre hacia A (+y local)."""
    return _casco([(0.0, 0.0, R_OJO), (L2, 0.0, R_OJO), (L1 + DX_GOTA1, PANZA_2 - R_GOTA, R_GOTA)])


def perfil_eslabon1():
    return _tramos_a_poligono(tramos_eslabon1())


def perfil_eslabon2():
    return _tramos_a_poligono(tramos_eslabon2())


def perfil_corto():
    return _estadio(L1, R_CORTO)


def colocar(poly, origen, ang):
    return affinity.translate(affinity.rotate(poly, ang, origin=(0, 0), use_radians=True), *origen)


def miembros(w):
    k = cinematica(w)
    return {
        "eslabon1": colocar(perfil_eslabon1(), k["Q1"], k["ang_largo"]),
        "eslabon2": colocar(perfil_eslabon2(), k["Q2"], k["ang_largo"]),
        "corto": colocar(perfil_corto(), k["O"], k["ang_corto"]),
    }


def marco(pieza, w):
    """Desplazamiento global -> local de cada pieza."""
    k = cinematica(w)
    if pieza == "A":
        return (0.0, 0.0)
    if pieza == "B":
        return (-k["xb"], 0.0)
    if pieza == "carro":
        return (-k["xb"], -(Y0 + k["p"]))
    raise ValueError(pieza)


ANCHOS_BARRIDO = np.linspace(W_MIN, W_MAX, 561)
SUAVE = 1.5        # cierre morfológico que alisa los rebajes del eslabón corto (los visibles en las caras)
CANTO = 0.3        # bisel de las aristas exteriores de barras y carro
R_PUNTA = 4.0      # redondeo en planta de las puntas de las barras (mismo radio que los ojos)
CANTO_ESL = 0.3    # bisel del contorno de eslabones y placas (no se biselan los agujeros)


def barrido(nombres, pieza, suave=0.0):
    polys = []
    for w in ANCHOS_BARRIDO:
        m = miembros(w)
        dx, dy = marco(pieza, w)
        for n in nombres:
            polys.append(affinity.translate(m[n], dx, dy))
    # el cierre (agrandar y achicar) rellena los serruchos entre posiciones sucesivas:
    # el hueco queda con bordes continuos y nunca más chico que el barrido real
    u = unary_union(polys)
    if suave > 0:
        return u.buffer(HOLG_PLANO + suave, 32).buffer(-suave, 32).simplify(0.01)
    return u.buffer(HOLG_PLANO, 16).simplify(0.01)


# ---------------------------------------------------------------- shapely -> CadQuery
def _limpiar(coords):
    out = []
    for p in coords:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > 1e-4:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) <= 1e-4:
        out.pop()
    return out


def extruir(geom, z0, z1):
    geoms = [g for g in getattr(geom, "geoms", [geom]) if g.geom_type == "Polygon"]
    sol = None
    for g in geoms:
        if g.is_empty or g.area < 1e-3:
            continue
        pts = _limpiar(list(g.exterior.coords)[:-1])
        s = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)
        for hole in g.interiors:
            h = _limpiar(list(hole.coords)[:-1])
            if len(h) < 3:
                continue
            s = s.cut(cq.Workplane("XY").workplane(offset=z0 - 1).polyline(h).close().extrude(z1 - z0 + 2))
        sol = s if sol is None else sol.union(s)
    return sol


def cortar(sol, geom, zs):
    for z0, z1 in zs:
        c = extruir(geom, z0, z1)
        if c is not None:
            sol = sol.cut(c)
    return sol


def redondear_con_cara(corte, lado_vacio, r):
    """Redondea con radio r los ángulos agudos donde un rebaje corta una cara de la pieza.
    lado_vacio es la región fuera de la pieza del otro lado de esa cara."""
    u = unary_union([corte, lado_vacio]).buffer(r, 32).buffer(-r, 32)
    return u.difference(lado_vacio).union(corte).buffer(0).simplify(0.01)


def caja(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cil_z(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def agujeros_acople(sol, x, largo=LARGO):
    for y0, sentido in ((0.0, 1), (largo, -1)):
        h = (cq.Workplane("XZ", origin=(0, y0, 0)).center(x, Z_EJE)
             .circle(D_ACOPLE / 2).extrude(-sentido * P_ACOPLE))
        sol = sol.cut(h)
        # avellanado de entrada 0,5 x 45°
        cono = cq.Solid.makeCone(D_ACOPLE / 2 + CANTO + 0.5, D_ACOPLE / 2 - 0.5, CANTO + 1.0,
                                 cq.Vector(x, y0 - sentido * 0.5, Z_EJE), cq.Vector(0, sentido, 0))
        sol = sol.cut(cq.Workplane().add(cono))
    return sol


# Lateral exterior: arco R 5 centrado en el eje de acople, tangente al plano de la cara exterior.
# Cubre un giro de ±GIRO_ACOPLE alrededor del eje sin pasar ese plano; fuera del arco siguen rectas
# tangentes hasta las caras anchas, con un chaflán de CHAFLAN_NARIZ en esas aristas.
GIRO_ACOPLE = 25.0
R_NARIZ = X_ACOPLE
CHAFLAN_NARIZ = 0.5


def perfil_lateral(ancho):
    """Contorno de la sección (x, z) de una barra con la cara exterior en x = 0."""
    zc, R, g = ESP / 2, R_NARIZ, math.radians(GIRO_ACOPLE)
    a1, a2 = math.pi - g, math.pi + g
    def corte(a, zp):
        u = (math.cos(a), math.sin(a))
        return np.array([X_ACOPLE + (R - (zp - zc) * u[1]) / u[0], zp])
    sup, inf = corte(a1, ESP), corte(a2, 0.0)
    arco = [np.array([X_ACOPLE + R * math.cos(t), zc + R * math.sin(t)]) for t in np.linspace(a1, a2, 41)]
    def chaflan(esq, hacia_cara, hacia_arco):
        d1 = (hacia_cara - esq) / np.linalg.norm(hacia_cara - esq)
        d2 = (hacia_arco - esq) / np.linalg.norm(hacia_arco - esq)
        return [esq + CHAFLAN_NARIZ * d1, esq + CHAFLAN_NARIZ * d2]
    pts = [np.array([ancho, 0.0]), np.array([ancho, ESP])]
    pts += chaflan(sup, np.array([ancho, ESP]), arco[0])
    pts += arco
    pts += chaflan(inf, arco[-1], np.array([ancho, 0.0]))
    return [(float(p[0]), float(p[1])) for p in pts]


def barra_base(ancho, exterior_izq=True, largo=LARGO):
    """Barra con el lateral exterior en arco R 5 centrado en el eje de acople (giro ±25°) a todo lo
    largo. Las puntas (caras de 13 x ancho) quedan planas; la cara interior lleva un redondeo de 0,3."""
    p = perfil_lateral(ancho)
    a_ini, a_fin = p[4], p[-3]                      # extremos del arco
    zc, R = ESP / 2, R_NARIZ
    medio = (X_ACOPLE - R, zc)
    wp = cq.Workplane("XZ").moveTo(*p[0]).lineTo(*p[1]).lineTo(*p[2]).lineTo(*p[3]).lineTo(*a_ini)
    wp = wp.threePointArc(medio, a_fin).lineTo(*p[-2]).lineTo(*p[-1]).close()
    b = wp.extrude(-largo)
    if not exterior_izq:
        b = b.mirror("YZ").translate((ancho, 0, 0))
    try:
        b = b.faces(">X" if exterior_izq else "<X").edges().fillet(CANTO)
    except Exception:
        pass
    return b


def canal_carro():
    """Recorrido del carro en el marco de B."""
    ps = [cinematica(w)["p"] for w in (W_MIN, W_MAX)]
    return (Y0 + min(ps) + CARRO_Y[0] - HOLG_PLANO, Y0 + max(ps) + CARRO_Y[1] + HOLG_PLANO)


def barra_a():
    b = barra_base(BWA, largo=LARGO_A)
    b = agujeros_acople(b, X_ACOPLE, LARGO_A)
    huella = box(-1, -1, BWA + 1, LARGO_A + 1)
    b = cortar(b, barrido(["eslabon1", "eslabon2"], "A").intersection(huella), [Z_MED_CORTE])
    corto = barrido(["corto"], "A", SUAVE).intersection(huella)
    b = cortar(b, corto, Z_PLACA_CORTE)

    for y in (Y0, Y0 + DP):
        b = b.cut(cil_z(D_A, y, D_PERNO, -1, ESP + 1))
    return cortar_cable(b, "A", box(-5, -1, BWA + 1, LARGO_A + 1))


def barra_b():
    """Columna + riel en C: las alas de 1,5 mm tapan el carro y trabajan con la columna.
    El canal se abre en la punta de y = 190 para meter el carro y se cierra con una tapa."""
    b = barra_base(BWB, exterior_izq=False)
    b = agujeros_acople(b, BWB - X_ACOPLE)
    huella = box(-1, -1, BWB + 1, LARGO + 1)
    y0c, _ = canal_carro()
    c = C_CARRO
    b = b.cut(caja(-1, c + HOLG, y0c, LARGO + 1, *Z_CANAL))
    for z0, z1 in labios():
        b = b.union(caja(0, LABIO_X, y0c, LARGO, z0, z1))
    b = cortar(b, barrido(["eslabon1", "eslabon2"], "B").intersection(huella), [Z_MED_CORTE])
    # alojamiento del eslabón corto en el bloque de O (capa central, oculto)
    corto = barrido(["corto"], "B", 5.0).intersection(huella)
    corto = redondear_con_cara(corto, box(-10, -5, 0, LARGO + 5), 4.0).intersection(huella)
    b = cortar(b, corto, Z_PLACA_CORTE)
    b = b.cut(cil_z(E_B, Y0, D_PERNO, -1, ESP + 1))
    return cortar_cable(b, "B", box(-1, -1, BWB + 5, LARGO + 1))


def labios():
    """Franjas en z de los dos labios de las alas de B."""
    return ((Z_CANAL[0], Z_CANAL[0] + LABIO_Z), (Z_CANAL[1] - LABIO_Z, Z_CANAL[1]))


def _sin_labios(sol, y0, y1):
    """Quita a una pieza que corre en el riel el lugar de los labios (con juego)."""
    for z0, z1 in labios():
        sol = sol.cut(caja(-1, LABIO_X + HOLG_PLANO, y0 - 1, y1 + 1, z0 - 1 if z0 < ESP / 2 else z0 - HOLG,
                           z1 + HOLG if z0 < ESP / 2 else z1 + 1))
    return sol


def tapa():
    """Cierra la boca del riel en la punta de y = 190 (entra como el carro, bajo los labios)."""
    c = C_CARRO
    y0 = canal_carro()[1] + 0.2
    return _sin_labios(caja(0, c + HOLG, y0, LARGO, *Z_CANAL), y0, LARGO)


def carro():
    """Corre entre las alas de B: las alas lo guían en z, la columna y los labios en x."""
    c = C_CARRO
    k = caja(0, c, CARRO_Y[0], CARRO_Y[1], *Z_CARRO)
    k = k.edges("|Z").edges("<X").fillet(R_PUNTA)
    k = _sin_labios(k, *CARRO_Y)
    huella = box(-1, CARRO_Y[0] - 1, c + 1, CARRO_Y[1] + 1)
    k = cortar(k, barrido(["eslabon1", "eslabon2"], "carro").intersection(huella), [Z_MED_CORTE])
    k = cortar(k, barrido(["corto"], "carro", SUAVE).intersection(huella), Z_PLACA_CORTE)
    for y in (0.0, DP):
        k = k.cut(cil_z(E_B, y, D_PERNO, -1, ESP + 1))
    return k


def pieza_miembro(contorno, z, agujeros):
    """Eslabón con contorno de arcos verdaderos, bisel exterior y agujeros sin biselar."""
    z0, z1 = z
    sol = contorno(cq.Workplane("XY").workplane(offset=z0)).extrude(z1 - z0)
    sol = sol.faces(">Z or <Z").chamfer(CANTO_ESL)
    for x in agujeros:
        sol = sol.cut(cil_z(x, 0, D_PERNO, z0 - 1, z1 + 1))
    return sol


def _contorno_estadio(largo, r):
    return lambda wp: wp.center(largo / 2, 0).slot2D(largo + 2 * r, 2 * r)


def rebaje_arandela(sol, x, y, z_cara, a=None):
    """Rebaje anular en la cara superior de un ojo para el resorte de precarga."""
    a = a or ARANDELA
    anillo = (cq.Workplane("XY").workplane(offset=z_cara - a["rebaje"]).center(x, y)
              .circle(a["d_ext"] / 2).circle(a["d_int"] / 2).extrude(a["rebaje"] + 1))
    return sol.cut(anillo)


def embocadura():
    """Barrido del eslabón corto en el marco del eslabón 1: hueco central donde se embute."""
    polys = []
    for w in ANCHOS_BARRIDO:
        k = cinematica(w)
        corto = colocar(perfil_corto(), k["O"], k["ang_corto"])
        loc = affinity.rotate(affinity.translate(corto, -k["Q1"][0], -k["Q1"][1]), -k["ang_largo"],
                              origin=(0, 0), use_radians=True)
        polys.append(loc)
    return unary_union(polys).buffer(HOLG_PLANO, 16).simplify(0.01)


def eslabon1():
    sol = pieza_miembro(lambda wp: _tramos_a_cq(wp, tramos_eslabon1()), Z_MED, [0.0, L1, L2])
    sol = cortar(sol, embocadura().intersection(perfil_eslabon1().buffer(1)), [Z_EMBOC])
    for x in (0.0, L1, L2):
        sol = sol.cut(cil_z(x, 0, D_PERNO, -1, ESP + 1))
    for x in (0.0, L2):
        sol = rebaje_arandela(sol, x, 0, Z_MED[1])
    return cortar_cable(sol, "eslabon1", perfil_eslabon1().buffer(1))


def eslabon2():
    sol = pieza_miembro(lambda wp: _tramos_a_cq(wp, tramos_eslabon2()), Z_MED, [0.0, L2])
    for x in (0.0, L2):
        sol = rebaje_arandela(sol, x, 0, Z_MED[1])
    return sol


def arandela(a=None, z_cara=None):
    """Resorte de disco de los eslabones largos (anillo plano equivalente en el modelo)."""
    a = a or ARANDELA
    z0 = (Z_MED[1] if z_cara is None else z_cara) - a["rebaje"]
    return (cq.Workplane("XY").workplane(offset=z0).circle(a["d_ext"] / 2 - 0.1)
            .circle(a["d_int"] / 2 + 0.05).extrude(a["alto"] - 0.01))


def arandela_corto():
    """Arandela ondulada de los pivotes del eslabón corto (O y C)."""
    return arandela(ARANDELA_CORTO, Z_CORTO[1])


def eslabon_corto():
    """Eslabón corto de una pieza, embutido en el eslabón 1 (C) y en la horquilla de B (O)."""
    sol = pieza_miembro(_contorno_estadio(L1, R_CORTO), Z_CORTO, [0.0, L1])
    for x in (0.0, L1):
        sol = rebaje_arandela(sol, x, 0, Z_CORTO[1], ARANDELA_CORTO)
    return sol


def perno():
    return cil_z(0, 0, D_PERNO, 0, ESP)


def perno_c():
    """Perno de C: atraviesa las dos alas de la embocadura del eslabón 1."""
    return cil_z(0, 0, D_PERNO, Z_MED[0], Z_MED[1])


def perno_p():
    """Pernos P1 y P2: ocultos bajo las alas del riel."""
    return cil_z(0, 0, D_PERNO, Z_CARRO[0], Z_CARRO[1])


def perno_a():
    """Pernos Q1 y Q2: al ras de la superficie curva del lateral de A."""
    y = LARGO / 2
    p = cil_z(D_A, y, D_PERNO, 0, ESP).intersect(barra_base(BWA))
    return p.translate((-D_A, -y, 0))


# ---------------------------------------------------------------- cable Ø4 de largo fijo
# El cable rodea O, C y Q1 siempre por el lado de afuera del recorrido y al mismo radio. Los giros
# en esos pivotes suman siempre 180°, así que el largo no cambia con el ancho. Dentro de cada barra
# el recorrido es fijo: entra por el lateral de B y sale por el lateral de A, con curvas de R 5.
D_CABLE = 4.0
R_CABLE = R_OJO + HOLG_PLANO + D_CABLE / 2 + 0.2    # radio de giro alrededor de los pivotes (7,0)
R_CURVA = 5.0                                       # curvas fijas dentro de las barras
Z_CABLE = ESP / 2
# sección del corte del cable, en escalones que contienen un círculo de R 2,2: (semiancho, semialto)
CORTE_CABLE = ((2.2, 1.0), (1.95, 1.7), (1.4, 2.2))
SOLIDO_CABLE = ((2.0, 1.0), (1.73, 1.6), (1.2, 2.0))  # el cable, para verificar choques


def _arco(c, a0, a1, r, ccw=True, paso=0.4):
    d = (a1 - a0) % (2 * math.pi) if ccw else -((a0 - a1) % (2 * math.pi))
    n = max(2, int(abs(d) * r / paso) + 1)
    return [np.asarray(c) + r * np.array([math.cos(t), math.sin(t)]) for t in np.linspace(a0, a0 + d, n)]


def angulos_cable():
    """Ángulos (en Q1 y en O) donde el cable deja de rodear el pivote y dobla hacia el lateral.
    Son los de W mínimo: lo justo para que el arco nunca sea negativo, así sale lo más arriba posible."""
    k = cinematica(W_MIN)
    hO = math.atan2(*(k["C"] - k["O"])[::-1])
    hC = math.atan2(*(k["Q1"] - k["C"])[::-1])
    return hO - math.pi / 2, (hC - math.pi / 2) % (2 * math.pi)


def ruta_cable(w):
    """Eje del cable en coordenadas globales, de B (lateral exterior) a A (lateral exterior)."""
    k = cinematica(w)
    O, C, Q = k["O"], k["C"], k["Q1"]
    hO = math.atan2(*(C - O)[::-1])
    hC = math.atan2(*(Q - C)[::-1])
    R, Rc, h = R_CABLE, R_CURVA, math.pi / 2
    a_ini, a_fin = angulos_cable()
    ua = lambda a: np.array([math.cos(a), math.sin(a)])
    # B: entra por el lateral hacia -x y dobla (R 5, sentido horario) hasta llegar tangente a O
    cb = O + (R + Rc) * ua(a_ini)
    giro_b = math.pi - (a_ini + h)                        # de rumbo 180° a rumbo a_ini + 90°
    pts = [cb + Rc * ua(a_ini + math.pi + giro_b) + np.array([2.5, 0.0])]
    pts += _arco(cb, a_ini + math.pi + giro_b, a_ini + math.pi, Rc, ccw=False)
    pts += _arco(O, a_ini, hO - h, R)
    pts += _arco(C, hO - h, hC - h, R)
    pts += _arco(Q, hC - h, a_fin, R)
    # A: deja Q1 con rumbo a_fin + 90° y dobla (R 5, horario) hasta rumbo 180°, hacia el lateral
    ca = Q + (R + Rc) * ua(a_fin)
    giro_a = (a_fin + h) - math.pi
    pts += _arco(ca, a_fin + math.pi, a_fin + math.pi - giro_a, Rc, ccw=False)
    pts.append(pts[-1] + np.array([-2.5, 0.0]))
    return np.array(pts)


def largo_cable(w):
    p = ruta_cable(w)
    return float(np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1)))


def _al_marco(pts, pieza, w):
    k = cinematica(w)
    if pieza in ("A", "B", "carro"):
        dx, dy = marco(pieza, w)
        return pts + np.array([dx, dy])
    org, ang = {"eslabon1": (k["Q1"], k["ang_largo"]), "eslabon2": (k["Q2"], k["ang_largo"]),
                "corto": (k["O"], k["ang_corto"])}[pieza]
    c, s_ = math.cos(-ang), math.sin(-ang)
    q = pts - org
    return np.c_[q[:, 0] * c - q[:, 1] * s_, q[:, 0] * s_ + q[:, 1] * c]


def barrido_cable(pieza, semiancho):
    """Lugar que ocupa el cable (eje engrosado) en el marco de una pieza, en todo el rango de anchos."""
    polys = [LineString(_al_marco(ruta_cable(w), pieza, w)).simplify(0.01).buffer(semiancho, 12)
             for w in ANCHOS_BARRIDO[::2]]
    return unary_union(polys).buffer(0.02).buffer(-0.02).simplify(0.01)


def cortar_cable(sol, pieza, huella):
    for semiancho, semialto in CORTE_CABLE:
        g = barrido_cable(pieza, semiancho).intersection(huella)
        if not g.is_empty:
            sol = cortar(sol, g, [(Z_CABLE - semialto, Z_CABLE + semialto)])
    return sol


def solido_cable(w):
    linea = LineString(ruta_cable(w))
    sol = None
    for semiancho, semialto in SOLIDO_CABLE:
        e = extruir(linea.buffer(semiancho, 16), Z_CABLE - semialto, Z_CABLE + semialto)
        sol = e if sol is None else sol.union(e)
    return sol


PIEZAS = {
    "barra_A": barra_a,
    "barra_B": barra_b,
    "carro": carro,
    "eslabon_1": eslabon1,
    "eslabon_2": eslabon2,
    "eslabon_corto": eslabon_corto,
    "tapa": tapa,
    "perno_P": perno_p,
    "perno": perno,
    "perno_A": perno_a,
    "perno_C": perno_c,
    "arandela": arandela,
    "arandela_corto": arandela_corto,
}

COLORES = {
    "barra_A": (0.55, 0.60, 0.66), "barra_B": (0.55, 0.60, 0.66),
    "carro": (0.85, 0.45, 0.15),
    "eslabon_1": (0.20, 0.45, 0.80), "eslabon_2": (0.35, 0.60, 0.90),
    "eslabon_corto": (0.15, 0.65, 0.45), "tapa": (0.55, 0.60, 0.66), "perno_P": (0.85, 0.85, 0.85),
    "cable": (0.10, 0.10, 0.11),
    "perno": (0.85, 0.85, 0.85), "perno_A": (0.85, 0.85, 0.85), "perno_C": (0.85, 0.85, 0.85), "arandela": (0.10, 0.37, 0.71), "arandela_corto": (0.70, 0.72, 0.75),
}


def poses(w):
    """(instancia, pieza, (x, y, z), ángulo Z en grados) para un ancho w."""
    assert W_MIN - 1e-9 <= w <= W_MAX + 1e-9, "ancho fuera de rango"
    k = cinematica(w)
    xb, yc = k["xb"], Y0 + k["p"]
    al, ac = math.degrees(k["ang_largo"]), math.degrees(k["ang_corto"])
    r = [
        ("barra_A", "barra_A", (0, 0, 0), 0),
        ("barra_B", "barra_B", (xb, 0, 0), 0),
        ("carro", "carro", (xb, yc, 0), 0),
        ("eslabon_1", "eslabon_1", (*k["Q1"], 0), al),
        ("eslabon_2", "eslabon_2", (*k["Q2"], 0), al),
        ("eslabon_corto", "eslabon_corto", (*k["O"], 0), ac),
        ("tapa", "tapa", (xb, 0, 0), 0),
    ]
    for n in ("Q1", "Q2", "P1", "P2", "C", "O"):
        tipo = {"Q1": "perno_A", "Q2": "perno_A", "C": "perno_C", "P1": "perno_P", "P2": "perno_P"}.get(n, "perno")
        r.append((f"perno_{n}", tipo, (*k[n], 0), 0))
        r.append((f"arandela_{n}", "arandela_corto" if n in ("C", "O") else "arandela", (*k[n], 0), 0))
    return r


def ensamble(w, piezas):
    a = cq.Assembly(name=f"eslabon_W{w:g}")
    for nombre, pieza, (x, y, z), ang in poses(w):
        loc = cq.Location(cq.Vector(x, y, z), cq.Vector(0, 0, 1), ang)
        a.add(piezas[pieza], name=nombre, loc=loc, color=cq.Color(*COLORES[pieza]))
    a.add(solido_cable(w), name="cable", color=cq.Color(*COLORES["cable"]))
    return a


def solidos(w, piezas):
    out = []
    for nombre, pieza, (x, y, z), ang in poses(w):
        sh = piezas[pieza].val().rotate((0, 0, 0), (0, 0, 1), ang).translate(cq.Vector(x, y, z))
        out.append((nombre, sh))
    return out


def interferencias(w, piezas):
    sol = solidos(w, piezas) + [("cable", solido_cable(w).val())]
    res = []
    for i in range(len(sol)):
        bi = sol[i][1].BoundingBox()
        for j in range(i + 1, len(sol)):
            bj = sol[j][1].BoundingBox()
            if bi.xmax < bj.xmin or bj.xmax < bi.xmin or bi.ymax < bj.ymin or bj.ymax < bi.ymin:
                continue
            v = sol[i][1].intersect(sol[j][1]).Volume()
            if v > 0.01:
                res.append((sol[i][0], sol[j][0], round(v, 3)))
    return res


def malla_json(forma, tol=0.05):
    verts, tris = forma.val().tessellate(tol, 0.3)
    return {"v": [round(c, 3) for p in verts for c in (p.x, p.y, p.z)], "i": [k for t in tris for k in t]}


def resumen():
    return dict(BWA=BWA, BWB=BWB, D_A=D_A, D_B=D_B, E_B=E_B, C_CARRO=C_CARRO, S_MIN=S_MIN, L2=L2, DP=DP,
                SEP_MIN=SEP_MIN, R_OJO=R_OJO, QUILLA=QUILLA, P_MAX=P_MAX, canal=canal_carro())


if __name__ == "__main__":
    import sys
    aqui = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(aqui, "salida")
    os.makedirs(os.path.join(out, "piezas"), exist_ok=True)
    print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in resumen().items()})
    piezas = {k: f() for k, f in PIEZAS.items()}
    rapido = "--rapido" in sys.argv

    if not rapido:
        for k, f in piezas.items():
            cq.exporters.export(f, os.path.join(out, "piezas", f"{k}.step"))
            cq.exporters.export(f, os.path.join(out, "piezas", f"{k}.stl"), tolerance=0.02)
        for w in (W_MIN, 70.0, W_MAX):
            ensamble(w, piezas).export(os.path.join(out, f"ensamble_W{w:g}.step"))

    pasos = [W_MIN + 2.5 * k for k in range(int((W_MAX - W_MIN) / 2.5) + 1)]
    for w in (pasos[::4] + [W_MAX] if rapido else pasos):
        inter = interferencias(w, piezas)
        print(f"W={w:g}: p={cinematica(w)['p']:.2f} interferencias={inter or 'ninguna'}")

    if not rapido:
        geo = {
            "param": {"LARGO": LARGO, "ESP": ESP, "W_MIN": W_MIN, "W_MAX": W_MAX, "BWA": BWA, "BWB": BWB,
                      "D_A": D_A, "D_B": D_B, "L2": L2, "Y0": Y0, "DP": DP, 
                      "X_ACOPLE": X_ACOPLE, "DZ_O": Z_CORTO[1] - Z_MED[1],
                      "R_CABLE": R_CABLE, "R_CURVA": R_CURVA,
                      "A_INI": angulos_cable()[0], "A_FIN": angulos_cable()[1], "D_CABLE": D_CABLE, "Z_CABLE": Z_CABLE},
            "colores": {k: "#%02x%02x%02x" % tuple(int(c * 255) for c in v) for k, v in COLORES.items()},
            "mallas": {k: malla_json(f) for k, f in piezas.items()},
        }
        cap = os.path.join(aqui, "salida", "capacidad.json")
        if os.path.exists(cap):
            with open(cap) as fh:
                geo["capacidad"] = json.load(fh)
        with open(os.path.join(aqui, "visor_plantilla.html")) as fh:
            plantilla = fh.read()
        with open(os.path.join(aqui, "visor.html"), "w") as fh:
            fh.write(plantilla.replace("/*GEOMETRIA*/null", json.dumps(geo, separators=(",", ":"))))
    print("listo")
