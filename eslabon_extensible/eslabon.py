"""Eslabón de ancho regulable con mecanismo de doble Scott Russell — versión 3.

Modelo paramétrico en CadQuery para mecanizado CNC en aluminio 7075-T651.
Ejes globales:
  X = ancho (dimensión regulable, 35..105 mm)
  Y = largo (190 mm, dirección de los ejes de acople)
  Z = espesor (13 mm)

Arquitectura en tres capas a lo largo del espesor:
  capa media (z 3..10)       eslabón largo 1 y eslabón largo 2 (7 mm)
  capas exteriores (z 0..2,8 y 10,2..13)
                             eslabón corto, hecho de dos placas que abrazan al eslabón 1 en C
  Barras y carro trabajan como horquillas: todos los pernos quedan en doble corte.

Los huecos de cada pieza se calculan barriendo el contorno de los eslabones por todo el rango
de anchos, así se quita solo el material imprescindible.

Piezas:
  barra A        lado fijo, pivotes Q1 y Q2
  barra B        columna exterior + bloque del pivote O + canal del carro con cremallera
  carro          corre en el canal de B, retenido por ganchos; lleva P1 y P2 y, entre ellos, el trinquete
  eslabón 1      lado del paralelogramo con vientre en gota hacia B (trabaja a flexión), agujero en C
  eslabón 2      lado del paralelogramo (biela), vientre hacia A
  placa corta    x2, eslabón corto del Scott Russell (O-C)
  trinquete      traba dentada paso 0,5 mm, empujada por un tornillo cónico M4 desde arriba
  pernos Ø5      pasadores templados rectificados g6
  arandela       arandela ondulada de precarga en cada pivote (juego axial cero)

Uso:
  python eslabon.py            exporta piezas, ensambles, verificación y visor 3D (visor.html)
"""

import json
import math
import os

import cadquery as cq
import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

# ---------------------------------------------------------------- parámetros
LARGO = 190.0
ESP = 13.0
W_MIN, W_MAX = 35.0, 105.0

D_ACOPLE, P_ACOPLE = 5.0, 10.0
X_ACOPLE = 5.0               # eje de acople a 5 mm de la cara exterior de cada barra
Z_EJE = ESP / 2

D_PERNO = 5.0                 # pasador templado rectificado Ø5 g6 (ISO 8734 5m6 como referencia de material)
R_ANILLO = D_PERNO / 2 + 2.0  # material mínimo alrededor de un perno en barras y carro
HOLG = 0.1                    # juego entre capas
HOLG_PLANO = 0.3              # juego en el plano entre piezas que se mueven

# capas
Z_MED = (3.0, 10.0)                       # eslabones largos
PIEL = 0.6                                # piel de las barras que tapa los rebajes del eslabón corto
Z_PLACA = ((PIEL, 2.8), (10.2, ESP - PIEL))  # placas del eslabón corto, hundidas bajo la piel
Z_MED_CORTE = (Z_MED[0] - HOLG, Z_MED[1] + HOLG)
Z_PLACA_CORTE = ((PIEL - HOLG, Z_PLACA[0][1] + HOLG), (Z_PLACA[1][0] - HOLG, ESP - PIEL + HOLG))

# Geometría principal. configurar() recalcula todo lo que depende de estos valores.
#   D_A      línea de pivotes Q1-Q2, medida desde la cara exterior de A
#   E_B      línea de pivotes O-P1-P2, medida desde la cara interior de B
#   COLUMNA  ancho de la columna maciza de B detrás del carro
#   GAP_MIN  luz entre barras a W mínimo
TRINQ_LARGO = 6.0                          # trinquete: 11 dientes de paso 0,5
COLA = 7.0                                 # carro por encima de P2: solo cierra el ojo de P2
Y_FIN_CARRO = 185.0                        # el canal corre por dentro del eje de acople (otra zona de la columna)
R_OJO_MAX = 4.5                            # ojo máximo: deja nervio en el fondo de las horquillas
Y0 = 15.0                                  # recta O-Q1
R_CORTO = 4.5                              # semiancho de las placas cortas (ojo igual a los largos)
# Vientres de los eslabones largos (arco R_GOTA tangente a los ojos). Profundidades máximas
# halladas con ajuste_vientres.py: el eslabón 1 no toca la columna de B a W mínimo y el 2 no
# come la barra A más allá del fondo que ya deja el ojo.
R_GOTA = 60.0
DX_GOTA1 = -12.0                           # el vientre del eslabón 1 se corre hacia Q1 (gota)
QUILLA = 12.5                              # profundidad del vientre del eslabón 1 (hacia B)
PANZA_2 = 10.6                             # profundidad del vientre del eslabón 2 (hacia A)
# pivote precargado: arandela ondulada de acero en un rebaje de la cara superior del ojo
ARANDELA = dict(d_int=D_PERNO + 0.2, d_ext=7.9, rebaje=0.15, alto=0.25)


def configurar(d_a=6.5, e_b=6.3, columna=10.5, gap_min=0.8, margen_l2=4.0):
    global D_A, E_B, COLUMNA, GAP_MIN, C_CARRO, BWB, BWA, D_B, S_MIN, L2, L1, P_MAX, DP
    global SEP_MIN, R_OJO, CARRO_Y, TRINQ_Y
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
    # trinquete justo arriba de P1, del lado de la columna: zona que ningún eslabón barre
    TRINQ_Y = (R_OJO + HOLG_PLANO + 1.2, R_OJO + HOLG_PLANO + 1.2 + TRINQ_LARGO)


TRINQ_PROF = 4.0
TRINQ_Z = (3.8, 9.2)
PASO_DIENTE = 0.5
ALTO_DIENTE = 0.3
GANCHO = 2.9                               # cuánto entran los ganchos del carro en la columna


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
    """Misma familia, vientre hacia el lado libre (+y local, hacia A)."""
    return _casco([(0.0, 0.0, R_OJO), (L2, 0.0, R_OJO), (L1, PANZA_2 - R_GOTA, R_GOTA)])


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


def agujeros_acople(sol, x):
    for y0, sentido in ((0.0, 1), (LARGO, -1)):
        h = (cq.Workplane("XZ", origin=(0, y0, 0)).center(x, Z_EJE)
             .circle(D_ACOPLE / 2).extrude(-sentido * P_ACOPLE))
        sol = sol.cut(h)
        # avellanado de entrada 0,5 x 45°
        cono = cq.Solid.makeCone(D_ACOPLE / 2 + CANTO + 0.5, D_ACOPLE / 2 - 0.5, CANTO + 1.0,
                                 cq.Vector(x, y0 - sentido * 0.5, Z_EJE), cq.Vector(0, sentido, 0))
        sol = sol.cut(cq.Workplane().add(cono))
    return sol


R_LATERAL = ESP / 2   # lateral exterior en semicilindro (R 6,5) y puntas con el mismo radio


def barra_base(ancho, exterior_izq=True):
    """Barra con el lateral exterior en semicilindro R 6,5 a todo lo largo. Las puntas
    (caras de 13 x ancho) quedan planas; la cara interior lleva un redondeo de 0,3."""
    r = R_LATERAL
    piezas = [
        cq.Solid.makeBox(ancho - r, LARGO, ESP, cq.Vector(r, 0, 0)),
        cq.Solid.makeCylinder(r, LARGO, cq.Vector(r, 0, r), cq.Vector(0, 1, 0)),
    ]
    b = cq.Workplane().add(piezas[0])
    for p in piezas[1:]:
        b = b.union(cq.Workplane().add(p))
    b = b.intersect(caja(0, ancho, 0, LARGO, 0, ESP))
    if not exterior_izq:
        b = b.mirror("YZ").translate((ancho, 0, 0))
    try:
        b = b.faces(">X" if exterior_izq else "<X").edges().fillet(CANTO)
    except Exception:
        pass
    return b


def dientes(x_cara, y0, y1, z0, z1, hacia, fase=0.0):
    """Prisma de dientes en V (60°) sobre la cara x=x_cara, hacia +1/-1 en X."""
    respaldo = x_cara - hacia * 0.5
    pts = [(respaldo, y0), (x_cara, y0)]
    y = y0 + ((fase - y0) % PASO_DIENTE)
    while y + PASO_DIENTE <= y1:
        pts += [(x_cara, y), (x_cara + hacia * ALTO_DIENTE, y + PASO_DIENTE / 2), (x_cara, y + PASO_DIENTE)]
        y += PASO_DIENTE
    pts += [(x_cara, y1), (respaldo, y1)]
    pts = [pts[0]] + [q for i, q in enumerate(pts[1:]) if abs(q[0] - pts[i][0]) + abs(q[1] - pts[i][1]) > 1e-9]
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


# ---------------------------------------------------------------- piezas
def canal_carro():
    """Recorrido del carro en el marco de B."""
    ps = [cinematica(w)["p"] for w in (W_MIN, W_MAX)]
    return (Y0 + min(ps) + CARRO_Y[0] - HOLG_PLANO, Y0 + max(ps) + CARRO_Y[1] + HOLG_PLANO)


def barra_a():
    b = barra_base(BWA)
    b = agujeros_acople(b, X_ACOPLE)
    huella = box(-1, -1, BWA + 1, LARGO + 1)
    b = cortar(b, barrido(["eslabon1", "eslabon2"], "A").intersection(huella), [Z_MED_CORTE])
    corto = barrido(["corto"], "A", SUAVE).intersection(huella)
    b = cortar(b, corto, Z_PLACA_CORTE)
    for y in (Y0, Y0 + DP):
        b = b.cut(cil_z(D_A, y, D_PERNO, -1, ESP + 1))
    return b


def barra_b():
    b = barra_base(BWB, exterior_izq=False)
    b = agujeros_acople(b, BWB - X_ACOPLE)
    huella = box(-1, -1, BWB + 1, LARGO + 1)
    y0c, y1c = canal_carro()
    b = b.cut(caja(-1, C_CARRO + HOLG, y0c, y1c, -1, ESP + 1))
    # alojamiento de los ganchos del carro (abajo y arriba, simétricos)
    c = C_CARRO
    # canal de los ganchos: cuello pegado a la cara (abajo y arriba) + bolsillo del pie;
    # entre ambos queda el labio de la columna (x c+0,1..c+1,6), que cuelga de la capa media
    for (zc0, zc1), (zp0, zp1) in (((-1, 1.7), (-1, 3.0)), ((ESP - 1.7, ESP + 1), (ESP - 3.0, ESP + 1))):
        b = b.cut(caja(-1, c + GANCHO + 0.1, y0c, y1c, zc0, zc1))
        b = b.cut(caja(c + 1.6, c + GANCHO + 0.1, y0c, y1c, zp0, zp1))
    # cremallera en la cara de la columna (capa media)
    b = b.cut(dientes(c + HOLG, y0c, y1c, *TRINQ_Z, +1))
    b = cortar(b, barrido(["eslabon1", "eslabon2"], "B").intersection(huella), [Z_MED_CORTE])
    # en el bloque de O la barra es casi maciza: el rebaje se redondea con más radio para que no quede la V
    corto = barrido(["corto"], "B", 5.0).intersection(huella)
    corto = redondear_con_cara(corto, box(-10, -5, 0, LARGO + 5), 4.0).intersection(huella)
    b = cortar(b, corto, Z_PLACA_CORTE)   # rebaje interior, tapado por la piel de las caras
    b = b.cut(cil_z(E_B, Y0, D_PERNO, -1, ESP + 1))
    b = rebaje_arandela(b, E_B, Y0, Z_PLACA_CORTE[1][0])
    return b


def carro():
    c = C_CARRO
    k = caja(0, c, CARRO_Y[0], CARRO_Y[1], 0, ESP)
    k = k.edges("|Z").edges("<X").fillet(R_PUNTA)
    k = k.edges("|Y").edges("<X").chamfer(CANTO)
    # ganchos: cuello en la cara (abajo y arriba) y pie que sube detrás del labio de la columna
    for (zc0, zc1), (zp0, zp1) in (((0, 1.6), (0, 2.9)), ((ESP - 1.6, ESP), (ESP - 2.9, ESP))):
        k = k.union(caja(c - 0.01, c + GANCHO, CARRO_Y[0], CARRO_Y[1], zc0, zc1))
        k = k.union(caja(c + 1.7, c + GANCHO, CARRO_Y[0], CARRO_Y[1], zp0, zp1))
    huella = box(-1, CARRO_Y[0] - 1, c + 3, CARRO_Y[1] + 1)
    k = cortar(k, barrido(["eslabon1", "eslabon2"], "carro").intersection(huella), [Z_MED_CORTE])
    k = cortar(k, barrido(["corto"], "carro", SUAVE).intersection(huella), Z_PLACA_CORTE)
    for y in (0.0, DP):
        k = k.cut(cil_z(E_B, y, D_PERNO, -1, ESP + 1))
    # alojamiento del trinquete y tornillo cónico
    k = k.cut(caja(c - TRINQ_PROF - 0.1, c + 1, *TRINQ_Y, TRINQ_Z[0] - 0.1, TRINQ_Z[1] + 0.1))
    k = k.cut(cil_z(c - TRINQ_PROF - 1.5, sum(TRINQ_Y) / 2, 4.0, TRINQ_Z[0], ESP + 1))
    return k


def trinquete():
    """En posición liberada (dientes 0,05 mm dentro del carro). Al apretar avanza ALTO_DIENTE."""
    c = C_CARRO
    y0, y1 = TRINQ_Y[0] + 0.1, TRINQ_Y[1] - 0.1
    t = caja(c - TRINQ_PROF, c - ALTO_DIENTE - 0.05, y0, y1, *TRINQ_Z)
    t = t.union(dientes(c - ALTO_DIENTE - 0.05, y0, y1, *TRINQ_Z, +1, fase=0.25).translate((0, 0, 0)))
    t = t.cut(cil_z(c - TRINQ_PROF - 1.5, sum(TRINQ_Y) / 2, 4.1, TRINQ_Z[0] - 1, ESP))
    return t


def tornillo_conico():
    y = sum(TRINQ_Y) / 2
    x = C_CARRO - TRINQ_PROF - 1.5
    cuerpo = cil_z(x, y, 4.0, 6.0, ESP - 0.5)
    punta = cq.Workplane("XY").workplane(offset=4.0).center(x, y).circle(0.5).workplane(offset=2.0).circle(2.0).loft()
    return cuerpo.union(punta)


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


def rebaje_arandela(sol, x, y, z_cara):
    """Rebaje anular en la cara superior de un ojo para la arandela ondulada de precarga."""
    a = ARANDELA
    anillo = (cq.Workplane("XY").workplane(offset=z_cara - a["rebaje"]).center(x, y)
              .circle(a["d_ext"] / 2).circle(a["d_int"] / 2).extrude(a["rebaje"] + 1))
    return sol.cut(anillo)


def eslabon1():
    sol = pieza_miembro(lambda wp: _tramos_a_cq(wp, tramos_eslabon1()), Z_MED, [0.0, L1, L2])
    for x in (0.0, L1, L2):
        sol = rebaje_arandela(sol, x, 0, Z_MED[1])
    return sol


def eslabon2():
    sol = pieza_miembro(lambda wp: _tramos_a_cq(wp, tramos_eslabon2()), Z_MED, [0.0, L2])
    for x in (0.0, L2):
        sol = rebaje_arandela(sol, x, 0, Z_MED[1])
    return sol


def arandela():
    a = ARANDELA
    z0 = Z_MED[1] - a["rebaje"]
    return (cq.Workplane("XY").workplane(offset=z0).circle(a["d_ext"] / 2 - 0.1)
            .circle(a["d_int"] / 2 + 0.05).extrude(a["alto"] - 0.01))


def placa_corta(z):
    return pieza_miembro(_contorno_estadio(L1, R_CORTO), z, [0.0, L1])


def perno():
    return cil_z(0, 0, D_PERNO, 0, ESP)


def perno_c():
    """Perno de C: queda entre las placas hundidas, sin llegar a la piel de las barras."""
    return cil_z(0, 0, D_PERNO, Z_PLACA[0][0], Z_PLACA[1][1])


def perno_a():
    """Pernos Q1 y Q2: al ras de la superficie curva del lateral de A."""
    y = LARGO / 2
    p = cil_z(D_A, y, D_PERNO, 0, ESP).intersect(barra_base(BWA))
    return p.translate((-D_A, -y, 0))


PIEZAS = {
    "barra_A": barra_a,
    "barra_B": barra_b,
    "carro": carro,
    "trinquete": trinquete,
    "tornillo": tornillo_conico,
    "eslabon_1": eslabon1,
    "eslabon_2": eslabon2,
    "placa_corta_inf": lambda: placa_corta(Z_PLACA[0]),
    "placa_corta_sup": lambda: placa_corta(Z_PLACA[1]),
    "perno": perno,
    "perno_A": perno_a,
    "perno_C": perno_c,
    "arandela": arandela,
}

COLORES = {
    "barra_A": (0.55, 0.60, 0.66), "barra_B": (0.55, 0.60, 0.66),
    "carro": (0.85, 0.45, 0.15), "trinquete": (0.95, 0.75, 0.25), "tornillo": (0.20, 0.20, 0.22),
    "eslabon_1": (0.20, 0.45, 0.80), "eslabon_2": (0.35, 0.60, 0.90),
    "placa_corta_inf": (0.15, 0.65, 0.45), "placa_corta_sup": (0.15, 0.65, 0.45),
    "perno": (0.85, 0.85, 0.85), "perno_A": (0.85, 0.85, 0.85), "perno_C": (0.85, 0.85, 0.85), "arandela": (0.70, 0.72, 0.75),
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
        ("trinquete", "trinquete", (xb, yc, 0), 0),
        ("tornillo", "tornillo", (xb, yc, 0), 0),
        ("eslabon_1", "eslabon_1", (*k["Q1"], 0), al),
        ("eslabon_2", "eslabon_2", (*k["Q2"], 0), al),
        ("placa_corta_inf", "placa_corta_inf", (*k["O"], 0), ac),
        ("placa_corta_sup", "placa_corta_sup", (*k["O"], 0), ac),
    ]
    for n in ("Q1", "Q2", "P1", "P2", "C", "O"):
        tipo = "perno_A" if n in ("Q1", "Q2") else ("perno_C" if n == "C" else "perno")
        r.append((f"perno_{n}", tipo, (*k[n], 0), 0))
        dz = Z_PLACA_CORTE[1][0] - Z_MED[1] if n == "O" else 0.0
        r.append((f"arandela_{n}", "arandela", (*k[n], dz), 0))
    return r


def ensamble(w, piezas):
    a = cq.Assembly(name=f"eslabon_W{w:g}")
    for nombre, pieza, (x, y, z), ang in poses(w):
        loc = cq.Location(cq.Vector(x, y, z), cq.Vector(0, 0, 1), ang)
        a.add(piezas[pieza], name=nombre, loc=loc, color=cq.Color(*COLORES[pieza]))
    return a


def solidos(w, piezas):
    out = []
    for nombre, pieza, (x, y, z), ang in poses(w):
        sh = piezas[pieza].val().rotate((0, 0, 0), (0, 0, 1), ang).translate(cq.Vector(x, y, z))
        out.append((nombre, sh))
    return out


def interferencias(w, piezas):
    sol = solidos(w, piezas)
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
                      "D_A": D_A, "D_B": D_B, "L2": L2, "Y0": Y0, "DP": DP, "PASO": PASO_DIENTE,
                      "X_ACOPLE": X_ACOPLE, "DZ_O": Z_PLACA_CORTE[1][0] - Z_MED[1]},
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
