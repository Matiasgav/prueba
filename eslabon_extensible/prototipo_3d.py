"""Prototipo impreso en 3D del eslabón regulable, para tenerlo en la mano y sentir los esfuerzos.

No es el diseño a fabricar: es la misma geometría (190 × 13, ancho 35 a 105) adaptada a una
impresora FDM y a tornillos M3 de cabeza fresada (DIN 7991 / ISO 10642).

Cómo se adapta:
  * Cada barra, el carro y el eslabón 1 se parten en dos mitades por el plano medio (z = 6,5).
    El diseño es simétrico en z, así que cada mitad se imprime con su cara exterior sobre la cama
    y todos los huecos quedan abiertos hacia arriba: sin soportes. Los eslabones 2 y corto se
    imprimen enteros, acostados.
  * Articulaciones sin juego: pivote de doble cono. Cada ojo lleva un avellanado a 45° en sus dos
    caras y cada mejilla un cono macho que entra en él. El tornillo M3 del pivote solo aprieta:
    al ajustarlo, las mejillas (que flexionan un poco) asientan los conos y el juego radial y
    axial se va a cero, aunque la impresión no sea precisa. El par del tornillo regula la
    fricción. Las seis articulaciones llevan tornillo.
  * Sin tuercas: todos los M3 roscan directo en el plástico (agujero piloto de 2,7).
  * Las mitades de A y de B se unen con tornillos M3 × 12 (cabeza fresada al ras arriba, rosca en
    la mitad de abajo). En B van a lo largo de toda la columna, al lado del riel.
  * Tornillería: M3 × 12 y M3 × 8 de cabeza fresada (los que hay a mano), todos con rosca directa en
    el plástico. Todos los pivotes llevan tornillo:
      Q1, Q2, O: M3 × 12 desde arriba (cabeza rebajada 1 mm).
      P1, P2: M3 × 12 desde abajo del carro, ACORTADO a 9,5 mm (la cabeza queda rebajada 0,2 en la
      cara de abajo del carro; un M3 × 12 entero asomaría por arriba contra el ala de B).
      C: M3 × 8 desde arriba, cabeza al ras, ACORTADO a 7 mm (el eslabón 1 tiene 7 mm).
    Las mitades del carro se unen además con 2 × M3 × 8 desde abajo en el lomo.
  * Traba provisoria: un tornillo M3 × 12 (con la arandela impresa) pasa por uno de los agujeros del
    ala de arriba de B y rosca en el carro: hace de perno (traba positiva). Un agujero por ancho a
    probar: W = 35, 55, 70, 85 y 105.
  * B v2: alas 1,2 mm más gruesas hacia afuera (B queda de 15,4 de espesor) y labios más grandes.
  * Sin cable, sin resortes de disco y sin remaches: no hacen falta para sentir el mecanismo.

Uso:
  python prototipo_3d.py      exporta salida/prototipo/*.stl (ya orientadas para imprimir),
                              el ensamble en STEP, una lámina de piezas y verifica choques.
"""
import math
import os

import cadquery as cq
import numpy as np

import eslabon as E

# ---------------------------------------------------------------- ajustes para impresión FDM
E.cortar_cable = lambda sol, *a, **k: sol          # sin cable
E.avellanar = lambda sol, *a, **k: sol             # sin avellanados de remache
E.rebaje_arandela = lambda sol, *a, **k: sol       # sin resortes de disco
E.HOLG_PLANO = 0.45                                # juego en el plano entre piezas que se mueven
E.Z_MED_CORTE = (2.75, 10.25)                      # 0,25 de luz entre ojos de 7 y mejillas
E.Z_PLACA_CORTE = ((5.0, 8.0),)                    # ídem para el eslabón corto (2,5)
E.Z_EMBOC = (5.0, 8.0)
E.Z_CARRO = (1.45, 11.55)                          # 0,25 de luz entre el carro y las alas de B

ZM = E.ESP / 2                                      # plano de partición
SPLIT_GAP = 0.15                                    # luz en el plano de partición del carro (cola)
M3 = dict(paso=3.4, piloto=2.7, cab=6.6, rebaje_cab=1.0)   # piloto: el M3 rosca directo en el plástico
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida", "prototipo")

# pivotes: profundidad del cono en el ojo y radio en la cara del ojo
CONO_LARGO = dict(prof=1.4, rf=3.4)                 # ojos de 7 mm (Q1, Q2, P1, P2)
CONO_CORTO = dict(prof=0.8, rf=3.0)                 # ojos de 2,5 mm (O, C)
D_OJO = 3.6                                         # agujero del ojo (el tornillo no apoya)


def cil(x, y, d, z0, z1):
    return E.cil_z(x, y, d, z0, z1)


def cono(x, y, r0, r1, z0, z1):
    """Tronco de cono entre z0 (radio r0) y z1 (radio r1)."""
    if z1 < z0:
        z0, z1, r0, r1 = z1, z0, r1, r0
    return cq.Workplane().add(cq.Solid.makeCone(r0, r1, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1)))


# ---------------------------------------------------------------- pivotes
def horquilla(sol, x, y, ojo, mej, c, tornillo):
    """Mejillas con conos machos. ojo = (z0, z1) del ojo; mej = (z0, z1) de las caras de las mejillas."""
    (e0, e1), (m0, m1) = ojo, mej
    zb0, zb1 = sol.val().BoundingBox().zmin, sol.val().BoundingBox().zmax
    sol = sol.union(cil(x, y, E.D_PERNO + 0.1, zb0, m0)).union(cil(x, y, E.D_PERNO + 0.1, m1, zb1))
    alto = c["prof"] - 0.2                              # el cono no toca el fondo del avellanado
    sol = sol.union(cono(x, y, c["rf"] + (e0 - m0), c["rf"] - alto, m0, e0 + alto))
    sol = sol.union(cono(x, y, c["rf"] + (m1 - e1), c["rf"] - alto, m1, e1 - alto))
    if tornillo == "arriba":                            # M3 × 12, cabeza fresada arriba rebajada 1 mm
        sol = sol.cut(cil(x, y, M3["piloto"], zb0 - 1, zb1 + 1))
        sol = sol.cut(cil(x, y, M3["paso"], (e0 + e1) / 2, zb1 + 1))
        sol = sol.cut(cil(x, y, M3["cab"], zb1 - M3["rebaje_cab"], zb1 + 1))
        sol = sol.cut(cono(x, y, M3["cab"] / 2, M3["paso"] / 2, zb1 - M3["rebaje_cab"],
                           zb1 - M3["rebaje_cab"] - (M3["cab"] - M3["paso"]) / 2))
    elif tornillo == "arriba_ras":                      # cabeza fresada al ras de la cara de arriba
        sol = sol.cut(cil(x, y, M3["piloto"], zb0 - 1, zb1 + 1))
        sol = sol.cut(cil(x, y, M3["paso"], (e0 + e1) / 2, zb1 + 1))
        sol = sol.cut(cono(x, y, M3["cab"] / 2 + 0.5, M3["paso"] / 2, zb1 + 0.5, zb1 - (M3["cab"] - M3["paso"]) / 2))
    elif tornillo == "abajo":                           # cabeza fresada abajo, rebajada 0,2 (carro)
        zc = zb0 + 0.2
        sol = sol.cut(cil(x, y, M3["piloto"], zb0 - 1, zb1 + 1))
        sol = sol.cut(cil(x, y, M3["paso"], zb0 - 1, (e0 + e1) / 2))
        sol = sol.cut(cil(x, y, M3["cab"], zb0 - 1, zc))
        sol = sol.cut(cono(x, y, M3["cab"] / 2, M3["paso"] / 2, zc, zc + (M3["cab"] - M3["paso"]) / 2))
    return sol


def ojo(sol, x, y, z, c):
    """Ojo con avellanado hembra a 45° en las dos caras."""
    z0, z1 = z
    sol = sol.union(cil(x, y, E.D_PERNO + 0.1, z0, z1).intersect(cil(x, y, 2 * E.R_OJO, z0, z1)))
    sol = sol.cut(cono(x, y, c["rf"] + 0.5, c["rf"] - c["prof"], z0 - 0.5, z0 + c["prof"]))
    sol = sol.cut(cono(x, y, c["rf"] + 0.5, c["rf"] - c["prof"], z1 + 0.5, z1 - c["prof"]))
    return sol.cut(cil(x, y, D_OJO, z0 - 1, z1 + 1))


# ---------------------------------------------------------------- uniones entre mitades
def columnas_macizas(sol, x, ys, d=7.0, z=(0.0, E.ESP)):
    """Posiciones (x, y) donde una columna de diámetro d atraviesa la pieza sin tocar huecos."""
    lleno = math.pi * d * d / 4 * (z[1] - z[0])
    ok = []
    for y in ys:
        v = sol.intersect(cil(x, y, d, *z)).val().Volume()
        if v > 0.995 * lleno:
            ok.append(y)
    return ok


def elegir(ys, n, sep):
    """Hasta n posiciones repartidas, separadas al menos sep."""
    if not ys:
        return []
    obj = np.linspace(min(ys), max(ys), n)
    out = []
    for t in obj:
        y = min(ys, key=lambda v: abs(v - t))
        if all(abs(y - o) >= sep for o in out):
            out.append(y)
    return out


def unir_mitades(sol, puntos):
    for x, y in puntos:
        sol = horquilla_union(sol, x, y)
    return sol


def horquilla_union(sol, x, y):
    """Tornillo de unión M3 × 12: cabeza fresada al ras arriba, pasa la mitad de arriba y rosca en la
    de abajo (piloto ciego: la cara de abajo queda lisa). Sin tuerca."""
    sol = sol.cut(cil(x, y, M3["piloto"], 0.6, E.ESP + 1))
    sol = sol.cut(cil(x, y, M3["paso"], ZM, E.ESP + 1))
    return sol.cut(cono(x, y, M3["cab"] / 2 + 0.5, M3["paso"] / 2, E.ESP + 0.5,
                        E.ESP - (M3["cab"] - M3["paso"]) / 2))


# ---------------------------------------------------------------- piezas
# Tornillos que unen las mitades (M3 × 12, cabeza al ras): solo donde entran sin tocar huecos.
# En B van repartidos a lo largo de toda la columna, al lado del riel, porque el carro tiende a
# abrir las mitades; en A alcanza con dos más los de Q1 y Q2.
UNION_A = [(7.5, 57.0), (6.5, 153.0)]
# carro: lomo macizo solo entre y = 8 y 38 (el resto lo barren los eslabones)
UNION_CARRO = [(8.0, 12.0), (8.0, 28.0)]
UNION_B = [(6.5, 9.0), (13.5, 24.0), (13.6, 48.0), (13.6, 76.0), (13.6, 104.0), (13.6, 152.0), (13.6, 176.0)]  # lejos de los agujeros de la traba

Y_TRABA_CARRO = E.DP / 2                             # tornillo de la traba, en el marco del carro
# Un agujero en el ala de B por cada ancho a probar. A anchos chicos el carro casi no se mueve
# (de W = 35 a 55 recorre 5 mm), así que no entran agujeros para anchos más cercanos.
ANCHOS_TRABA = (35, 55, 70, 85, 105)

# v2 de B (después de imprimir la v1): la ranura de la traba cortaba el ala de arriba a lo largo y la
# dejaba suelta. Ahora: alas más gruesas hacia afuera (+1,2 por cara: B pasa de 13 a 15,4), labios
# más grandes, y una fila de agujeros en lugar de la ranura (traba positiva: el tornillo hace de perno).
ALA_EXTRA = 1.2
LABIO_V2 = dict(ancho=1.65, alto=1.3)                # el carro v1 sin la pestaña fina deja lugar


def _huella(sol, z):
    """Caras de la sección horizontal de una pieza a la altura z."""
    return sol.intersect(E.caja(-100, 100, -100, 400, z - 0.01, z + 0.01)).faces("<Z").vals()


def x_traba():
    """x de la traba: el lomo del carro (macizo de arriba abajo) más cercano a la columna."""
    k = E.carro()
    for x in np.arange(10.2, 6.0, -0.2):
        if columnas_macizas(k, x, [Y_TRABA_CARRO], d=4.2, z=E.Z_CARRO):
            return float(x)
    raise RuntimeError("no hay lomo macizo para la traba")


def piezas_prototipo():
    xt = x_traba()
    # barra A
    a = E.barra_a()
    for y in (E.Y0, E.Y0 + E.DP):
        a = horquilla(a, E.D_A, y, E.Z_MED, E.Z_MED_CORTE, CONO_LARGO, "arriba")
    a = unir_mitades(a, UNION_A)
    # barra B (con la tapa incorporada: el carro entra antes de cerrar las mitades)
    b = E.barra_b().union(E.tapa())
    b = horquilla(b, E.E_B, E.Y0, E.Z_CORTO, E.Z_PLACA_CORTE[0], CONO_CORTO, "arriba")
    b = unir_mitades(b, UNION_B)
    # labios más grandes (el carro va sin la pestaña fina de 0,55 sobre la muesca)
    y0c = E.canal_carro()[0]
    b = b.union(E.caja(0, LABIO_V2["ancho"], y0c, E.LARGO, E.Z_CANAL[0], E.Z_CANAL[0] + LABIO_V2["alto"]))
    b = b.union(E.caja(0, LABIO_V2["ancho"], y0c, E.LARGO, E.Z_CANAL[1] - LABIO_V2["alto"], E.Z_CANAL[1]))
    # alas más gruesas: se prolonga la huella de cada cara 1,2 mm hacia afuera
    for z, sg in ((0.05, -1), (E.ESP - 0.05, 1)):
        for cara in _huella(b, z):
            b = b.union(cq.Workplane().add(cq.Solid.extrudeLinear(cara, cq.Vector(0, 0, sg * (ALA_EXTRA + 0.05)))))
    # traba: fila de agujeros en el ala de arriba (el tornillo pasa por uno y rosca en el carro)
    ys_traba = [E.Y0 + E.cinematica(w)["p"] + Y_TRABA_CARRO for w in ANCHOS_TRABA]
    y0, y1 = min(ys_traba), max(ys_traba)
    for y in ys_traba:
        b = b.cut(cil(xt, y, M3["paso"], E.Z_CANAL[1] - 0.5, E.ESP + ALA_EXTRA + 1))
    # carro: conos en P1 y P2, sin tornillos; agujero piloto de la traba
    k = E.carro()
    for y in (0.0, E.DP):
        k = horquilla(k, E.E_B, y, E.Z_MED, E.Z_MED_CORTE, CONO_LARGO, "abajo")
    k = k.cut(cil(xt, Y_TRABA_CARRO, M3["piloto"], E.Z_CARRO[0] + 1.0, E.ESP))
    # sin la pestaña fina (0,55) sobre la muesca de los labios: no hace falta y deja lugar al labio v2
    for z0, z1 in ((E.Z_CARRO[0] - 1, E.Z_MED_CORTE[0]), (E.Z_MED_CORTE[1], E.Z_CARRO[1] + 1)):
        k = k.cut(E.caja(-1, E.LABIO_X + E.HOLG_PLANO, E.CARRO_Y[0] - 1, E.CARRO_Y[1] + 1, z0, z1))
    for x, y in UNION_CARRO:                            # M3 × 8 desde abajo, cabeza rebajada 0,2
        zc = E.Z_CARRO[0] + 0.2
        k = k.cut(cil(x, y, M3["piloto"], ZM, zc + 8.4)).cut(cil(x, y, M3["paso"], zc, ZM))
        k = k.cut(cil(x, y, M3["cab"], E.Z_CARRO[0] - 1, zc))
        k = k.cut(cono(x, y, M3["cab"] / 2, M3["paso"] / 2, zc, zc + (M3["cab"] - M3["paso"]) / 2))
    # eslabón 1: ojos en Q1 y P1; horquilla en C (el corto entra en la embocadura)
    l1 = E.eslabon1()
    for x in (0.0, E.L2):
        l1 = ojo(l1, x, 0, E.Z_MED, CONO_LARGO)
    l1 = horquilla(l1, E.L1, 0, E.Z_CORTO, E.Z_EMBOC, CONO_CORTO, "arriba_ras")
    # eslabón 2 y corto: enteros
    l2 = E.eslabon2()
    for x in (0.0, E.L2):
        l2 = ojo(l2, x, 0, E.Z_MED, CONO_LARGO)
    lc = E.eslabon_corto()
    for x in (0.0, E.L1):
        lc = ojo(lc, x, 0, E.Z_CORTO, CONO_CORTO)
    return dict(barra_A=a, barra_B=b, carro=k, eslabon_1=l1, eslabon_2=l2, eslabon_corto=lc), \
        dict(union_a=UNION_A, union_b=UNION_B, x_traba=xt, ranura=(y0, y1), agujeros_traba=ys_traba)


def arandela_traba():
    """Arandela de la traba: apoya sobre la cara de B, a los lados de la ranura; aloja la cabeza fresada."""
    w = cil(0, 0, 10.0, 0, 2.0)
    w = w.cut(cil(0, 0, M3["paso"], -1, 3))
    return w.cut(cono(0, 0, M3["cab"] / 2, M3["paso"] / 2, 2.0, 2.0 - (M3["cab"] - M3["paso"]) / 2))


def partir(sol, nombre):
    """Mitades por el plano medio; la de arriba se da vuelta para imprimirla con su cara exterior abajo."""
    bb = sol.val().BoundingBox()
    abajo = sol.intersect(E.caja(-500, 500, -500, 500, bb.zmin - 1, ZM))
    arriba = sol.intersect(E.caja(-500, 500, -500, 500, ZM, bb.zmax + 1))
    if nombre in ("carro", "eslabon_1"):          # luz en la partición: los conos asientan antes que el plano
        abajo = abajo.cut(E.caja(-500, 500, -500, 500, ZM - SPLIT_GAP / 2, ZM + 1))
        arriba = arriba.cut(E.caja(-500, 500, -500, 500, ZM - 1, ZM + SPLIT_GAP / 2))
    return abajo, arriba


def a_la_cama(sol, dar_vuelta):
    s = sol.val()
    if dar_vuelta:
        s = s.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-bb.xmin, -bb.ymin, -bb.zmin))


IMPRESION = {
    # pieza: (partir en dos, descripción de la cara que va sobre la cama)
    "barra_A": (True, "cara de 165 × ancho sobre la cama (la de arriba se imprime dada vuelta)"),
    "barra_B": (True, "cara de 190 × ancho sobre la cama (la de arriba se imprime dada vuelta)"),
    "carro": (True, "cara exterior sobre la cama"),
    "eslabon_1": (True, "cara plana sobre la cama"),
    "eslabon_2": (False, "acostado, cara plana sobre la cama"),
    "eslabon_corto": (False, "acostado, cara plana sobre la cama"),
}


def exportar(piezas):
    os.makedirs(SALIDA, exist_ok=True)
    impresas = {}
    for nombre, sol in piezas.items():
        if IMPRESION[nombre][0]:
            ab, ar = partir(sol, nombre)
            impresas[f"{nombre}_abajo"] = a_la_cama(ab, False)
            impresas[f"{nombre}_arriba"] = a_la_cama(ar, True)
        else:
            impresas[nombre] = a_la_cama(sol, False)
    impresas["arandela_traba"] = a_la_cama(arandela_traba(), False)
    for n, s in impresas.items():
        cq.exporters.export(cq.Workplane().add(s), os.path.join(SALIDA, f"{n}.stl"), tolerance=0.02, angularTolerance=0.1)
    return impresas


def ensamble(piezas, w):
    out = []
    for nombre, pieza, (x, y, z), ang in E.poses(w):
        if pieza in piezas:
            out.append((nombre, piezas[pieza].val().rotate((0, 0, 0), (0, 0, 1), ang).translate(cq.Vector(x, y, z))))
    return out


def choques(piezas, w):
    sol = ensamble(piezas, w)
    res = []
    for i in range(len(sol)):
        for j in range(i + 1, len(sol)):
            v = sol[i][1].intersect(sol[j][1]).Volume()
            if v > 0.01:
                res.append((sol[i][0], sol[j][0], round(v, 3)))
    return res


if __name__ == "__main__":
    piezas, info = piezas_prototipo()
    for n, p in piezas.items():
        assert p.val().isValid(), n
    print("uniones A:", info["union_a"], " uniones B:", info["union_b"], " traba x:", round(info["x_traba"], 1),
          " agujeros traba y:", [round(float(v), 1) for v in info["agujeros_traba"]])
    for w in (35, 45, 60, 80, 105):
        print(f"W={w}: choques={choques(piezas, w) or 'ninguno'}")
    impresas = exportar(piezas)
    for n, s in impresas.items():
        bb = s.BoundingBox()
        print(f"{n}: {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm, {s.Volume() / 1000:.1f} cm³")
    asm = cq.Assembly()
    for n, s in ensamble(piezas, 70):
        asm.add(cq.Workplane().add(s), name=n)
    asm.save(os.path.join(SALIDA, "ensamble_prototipo_W70.step"))
    print("listo")
