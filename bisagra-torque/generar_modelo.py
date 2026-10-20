"""Bisagra de dos eslabones para ensayar torque de trabado con arandelas D con
lengüeta.

Genera las piezas con manifold3d, exporta los .stl a stl/ y arma visor.html
con las mallas embebidas.

Ejes del modelo (mm):
  X  eje de la bisagra (largo 50)
  Y  hacia afuera de la articulación (+Y eslabón B, -Y eslabón A)
  Z  espesor (14), Z=0 en el plano medio

Uso:  python3 generar_modelo.py
"""

import base64
import json
import math
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh

AQUI = Path(__file__).resolve().parent
SEG = 96  # segmentos por círculo

# --- Parámetros ------------------------------------------------------------
L = 50.0           # largo sobre el eje de la bisagra
T = 14.0           # espesor de los eslabones = diámetro del nudillo
R = T / 2
HOLGURA_R = 1.0    # luz radial entre nudillo y la cara del otro eslabón
CARA = R + HOLGURA_R          # cara plana de cada placa, a 8 mm del eje
ANCHO_PLACA = 20.0            # placa: de 8 a 28 mm del eje; después la palanca

# Aligerado: la placa tiene el espesor completo solo cerca de la bisagra y
# después baja a 8 mm (apoyada en la cama).
Y_GRUESO = 15.5               # hasta acá 14 mm de espesor
Y_RAMPA = 21.5                # rampa a 45° hasta el espesor delgado
Z_DELGADO = 1.0               # cara superior de la parte delgada (8 mm)
# Forma de T vista desde arriba: la barra de la T es la franja de la bisagra
# (todo el largo, hasta Y_BARRA) y el palo es la palanca de 20 mm de ancho.
Y_BARRA = 24.0
R_ENCUENTRO = 4.0             # radio en los rincones donde la palanca sale de la barra

# Lado de la pila (x = 0): cabeza | oreja A | pila | nudillo B.
# La pila siempre suma PILA mm: arandelas D de un espesor + redondas de
# relleno. Así el hombro entra siempre lo mismo y nunca toca fondo.
OREJA = 4.0                   # espesor de cada oreja del eslabón A
PILA = 4.8
ESPESORES = (0.2, 0.4, 0.8)
HOLGURA_PILA = 0.2            # juego axial al armar
ZONA = PILA + HOLGURA_PILA    # 5.0 mm entre la oreja y el nudillo
JUEGO_FLOJO = 0.2             # oreja x = 50, sin arandelas: gira libre

PALANCA_ANCHO = 20.0
PALANCA_LARGO = 50.0

# Tornillo Accu SSHE-M4-5-10-A2 (ISO 7379): hombro Ø5 x 10, rosca M4 x 5,
# cabeza Ø8 x 4
D_HOMBRO, L_HOMBRO = 5.0, 10.0
L_ROSCA = 5.0
D_CABEZA, H_CABEZA = 8.0, 4.0

D_AGUJERO_OREJA = 5.2      # el hombro gira en la oreja
D_ALOJ_HOMBRO = 5.4
D_AGUJERO_ARANDELA = 5.2
D_REDONDA = T

# Arandela D con lengüeta. La cara plana queda a 0.2 de la placa (esquinas
# vivas) y la lengüeta entra en una ranura de la placa: empuja de costado,
# con brazo de 8 a 12.5 mm del eje.
LARGO_D = CARA - 0.2
LENGUETA_ANCHO = 7.0
# Largo óptimo para 7 mm de ancho: con la punta a 12 mm del eje la lengüeta
# llega al límite de aplastamiento y al de flexión a la vez (largo dentro de
# la ranura = ancho / raíz de 3). Más larga se doblaría antes; más angosta
# aguanta menos.
LENGUETA_HASTA = 12.0      # distancia al eje de la punta
R_RAIZ_LENGUETA = 0.4
RANURA_ANCHO = LENGUETA_ANCHO + 0.3
RANURA_FONDO = 12.2
CHAFLAN_RANURA = 0.6       # boca de la ranura, deja lugar al radio de la raíz

# Cuánto entra el hombro en el nudillo con todo apretado: 10 - 4 - 4.8 = 1.2
ENTRADA_PILA = L_HOMBRO - OREJA - PILA
# Lado libre: el hombro hace tope y la oreja queda con 0.2 de juego.
TOPE_LIBRE = L_HOMBRO - OREJA - 2 * JUEGO_FLOJO

# Agujero liso para que el M4 se enrosque solo en el plástico
D_AUTORROSCANTE = 3.5
L_AUTORROSCANTE = 8.0      # 5 de rosca del tornillo + margen para la punta

# Tuerca M4 (DIN 934: 7 entre caras, 3,2 de alto) cautiva, metida de costado
AF_TUERCA, E_TUERCA = 7.0, 3.2
AF_CAJERA = AF_TUERCA + 0.1      # entre caras: ajustada, la tuerca no gira
E_CAJERA = E_TUERCA + 0.4        # a lo largo del eje
SOBRE_RECORRIDO = 0.4            # el hexágono baja 0.4 más allá del eje
D_PASO_TORNILLO = 4.4
# La rosca del tornillo va de 1.2 a 6.2 mm dentro del nudillo; la tuerca
# empieza a 2.8 y queda entera dentro de la rosca, con 2.8 mm de pared.
TUERCA_PILA = 2.8

X_NUDILLO = (OREJA + ZONA, L - OREJA - JUEGO_FLOJO)

# --- Primitivas ------------------------------------------------------------


def caja(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cil_x(r, x0, x1, y=0.0, z=0.0):
    """Cilindro con eje paralelo a X."""
    c = m3d.Manifold.cylinder(x1 - x0, r, r, SEG)
    return c.rotate([0, 90, 0]).translate([x0, y, z])


def cil_z(r, x, y, z0, z1):
    return m3d.Manifold.cylinder(z1 - z0, r, r, SEG).translate([x, y, z0])


def extruir_x(perfil_yz, x0, x1):
    """Extruye un perfil del plano (y, z) a lo largo de X."""
    m = m3d.Manifold.extrude(m3d.CrossSection([perfil_yz]), x1 - x0)
    # local (x, y, z) -> modelo (Y, Z, X)
    return m.transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])


def placa(signo):
    """Eslabón visto desde arriba con forma de T: barra a lo largo de la
    bisagra y palanca centrada hacia afuera. Gruesa (14 mm) junto a la
    bisagra y delgada (8 mm) en el resto."""
    y_fin = CARA + ANCHO_PLACA + PALANCA_LARGO
    perfil = [(CARA, -R), (y_fin, -R), (y_fin, Z_DELGADO), (Y_RAMPA, Z_DELGADO),
              (Y_GRUESO, R), (CARA, R)]
    x0 = (L - PALANCA_ANCHO) / 2
    planta = (m3d.CrossSection.square([L, Y_BARRA - CARA]).translate([0, CARA]) +
              m3d.CrossSection.square([PALANCA_ANCHO, y_fin - CARA]).translate([x0, CARA]))
    # radio en los rincones interiores de la T (cerrar: agrandar y achicar)
    rr = R_ENCUENTRO
    planta = planta.offset(rr, m3d.JoinType.Round).offset(-rr, m3d.JoinType.Round)
    p = extruir_x(perfil, 0, L) ^ m3d.Manifold.extrude(planta, T).translate([0, 0, -R])
    return p.mirror([0, 1, 0]) if signo < 0 else p


def ranura(signo):
    """Ranura de la cara de la placa para las lengüetas, en la zona de la
    pila (entre la oreja y el nudillo)."""
    a, c = RANURA_ANCHO / 2, CHAFLAN_RANURA
    perfil = [(CARA - 0.3, -a - c - 0.3), (CARA + c, -a), (RANURA_FONDO, -a),
              (RANURA_FONDO, a), (CARA + c, a), (CARA - 0.3, a + c + 0.3)]
    r = extruir_x(perfil, OREJA, OREJA + ZONA)
    return r.mirror([0, 1, 0]) if signo < 0 else r


# --- Piezas ----------------------------------------------------------------


def eslabon_a():
    """Horquilla: placa en -Y y dos orejas de 4 mm en los extremos."""
    s = placa(-1)
    for x0, x1 in [(0, OREJA), (L - OREJA, L)]:
        s += cil_x(R, x0, x1) + caja(x0, x1, -CARA - 0.5, 0, -R, R)
        s -= cil_x(D_AGUJERO_OREJA / 2, x0 - 1, x1 + 1)
    return s - ranura(-1)


def agujero(tope, tipo):
    """Agujero del nudillo en coordenadas locales: eje +Z hacia adentro,
    z=0 en la cara del nudillo. `tope`: profundidad donde empieza la rosca
    (o la tuerca)."""
    h = m3d.Manifold.cylinder(tope + 1, D_ALOJ_HOMBRO / 2, D_ALOJ_HOMBRO / 2,
                              SEG).translate([0, 0, -1])
    if tipo == "autorroscante":
        r = D_AUTORROSCANTE / 2
        h += m3d.Manifold.cylinder(L_AUTORROSCANTE, r, r, SEG).translate(
            [0, 0, tope - 0.01])
        # chaflán de entrada para que la rosca arranque derecha
        return h + m3d.Manifold.cylinder(0.5, r + 0.5, r, SEG).translate(
            [0, 0, tope - 0.01])
    # tuerca: paso libre a través de la cajera y para la punta del tornillo
    r = D_PASO_TORNILLO / 2
    return h + m3d.Manifold.cylinder(E_CAJERA + 4, r, r, SEG).translate(
        [0, 0, tope - 0.01])


def cajera_tuerca(xa):
    """Alojamiento de la tuerca, de xa a xa + E_CAJERA (coordenadas del
    modelo). Hexágono con las caras planas verticales y una ranura abierta
    hacia +Z para meter la tuerca de costado."""
    r = AF_CAJERA / math.sqrt(3)
    hexa = m3d.Manifold.cylinder(E_CAJERA, r, r, 6).rotate([0, 90, 0]).translate(
        [xa, 0, 0])
    # sobre-recorrido: si el fondo sale corto al imprimir, la tuerca igual
    # llega a quedar centrada con el agujero
    hexa += hexa.translate([0, 0, -SOBRE_RECORRIDO])
    return hexa + caja(xa, xa + E_CAJERA, -AF_CAJERA / 2, AF_CAJERA / 2, 0, R + 1)


def eslabon_b():
    """Nudillo entre las orejas: tuerca M4 cautiva del lado de la pila y
    agujero autorroscante del lado libre. Los agujeros se ubican solo con
    rotaciones."""
    x0, x1 = X_NUDILLO
    s = placa(1)
    s += cil_x(R, x0, x1) + caja(x0, x1, 0, CARA + 0.5, -R, R)
    s -= ranura(1)
    s -= agujero(TUERCA_PILA, "tuerca").rotate([0, 90, 0]).translate([x0, 0, 0])
    s -= cajera_tuerca(x0 + TUERCA_PILA)
    s -= agujero(TOPE_LIBRE, "autorroscante").rotate([0, -90, 0]).translate([x1, 0, 0])
    return s


def arco(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def perfil_d():
    """D de esquinas vivas con lengüeta hacia la placa. La raíz de la
    lengüeta lleva un radio para que no se fisure; la punta, redondeada para
    entrar fácil en la ranura."""
    d = m3d.CrossSection([arco(0, 0, R, 90, 270, SEG // 2) +
                          [(LARGO_D, -R), (LARGO_D, R)]])
    a = LENGUETA_ANCHO / 2
    leng = m3d.CrossSection.square([LENGUETA_HASTA - 5.0, LENGUETA_ANCHO]).translate(
        [5.0, -a])
    leng = leng.offset(-0.5, m3d.JoinType.Round).offset(0.5, m3d.JoinType.Round)
    r = R_RAIZ_LENGUETA
    return (d + leng).offset(r, m3d.JoinType.Round).offset(-r, m3d.JoinType.Round)


def arandela_d(e):
    """Arandela D con lengüeta, de espesor e, acostada para imprimir."""
    perfil = perfil_d() - m3d.CrossSection.circle(D_AGUJERO_ARANDELA / 2, SEG)
    return m3d.Manifold.extrude(perfil, e)


def arandela_redonda(e):
    """Arandela libre: no se traba con ningún eslabón. Rellena la pila."""
    perfil = m3d.CrossSection.circle(D_REDONDA / 2, SEG)
    perfil -= m3d.CrossSection.circle(D_AGUJERO_ARANDELA / 2, SEG)
    return m3d.Manifold.extrude(perfil, e)


def tuerca():
    """Solo para el visor. Eje X, desde x=0."""
    r = AF_TUERCA / math.sqrt(3)
    t = m3d.Manifold.cylinder(E_TUERCA, r, r, 6).rotate([0, 90, 0])
    return t - cil_x(1.7, -1, E_TUERCA + 1)


def tornillo():
    """Solo para el visor. Eje X, cara de apoyo de la cabeza en X=0."""
    t = cil_x(D_CABEZA / 2, -H_CABEZA, 0)
    t -= cil_x(1.45, -H_CABEZA - 1, -H_CABEZA + 2.5)  # hexágono simplificado
    t += cil_x(D_HOMBRO / 2, 0, L_HOMBRO)
    t += cil_x(1.95, L_HOMBRO, L_HOMBRO + L_ROSCA)
    return t


# --- Salida ----------------------------------------------------------------


def a_trimesh(man):
    mg = man.to_mesh()
    return trimesh.Trimesh(np.asarray(mg.vert_properties)[:, :3],
                           np.asarray(mg.tri_verts), process=True)


def b64(arr, dt):
    return base64.b64encode(np.ascontiguousarray(arr, dtype=dt).tobytes()).decode()


def malla_json(man):
    mg = man.to_mesh()
    v = np.asarray(mg.vert_properties)[:, :3]
    return {"v": b64(v, "<f4"), "i": b64(np.asarray(mg.tri_verts).ravel(), "<u4")}


def rango_giro(a, b):
    """Ángulo máximo de giro de B en cada sentido antes de chocar con A."""
    res = {}
    for sentido in (1, -1):
        lim = 0
        for g in range(1, 181):
            bb = b.rotate([sentido * g, 0, 0])
            if (a ^ bb).volume() > 1e-3:
                break
            lim = g
        res["+" if sentido > 0 else "-"] = lim
    return res


def main():
    a = eslabon_a()
    b = eslabon_b()

    assert (a ^ b).volume() < 1e-6, "A y B se interfieren"
    giro = rango_giro(a, b)

    out = AQUI / "stl"
    out.mkdir(exist_ok=True)
    for viejo in out.glob("*.stl"):
        viejo.unlink()
    # A y B se imprimen acostados (Z hacia arriba); las orejas y el nudillo
    # llegan al plano de la cama porque su diámetro es el espesor.
    piezas = {
        "eslabon_A_horquilla.stl": a.translate([0, 0, R]),
        "eslabon_B_nudillo.stl": b.translate([0, 0, R]),
    }
    # Una arandela por archivo; las cantidades van en el README.
    for e in ESPESORES:
        mm = f"{e:.1f}".replace(".", "_")
        piezas[f"arandela_D_{mm}mm.stl"] = arandela_d(e)
        piezas[f"arandela_redonda_{mm}mm.stl"] = arandela_redonda(e)
    for nombre, man in piezas.items():
        a_trimesh(man).export(out / nombre)

    x0, x1 = X_NUDILLO
    datos = {
        "A": malla_json(a), "B": malla_json(b),
        # arandelas de 1 mm: el visor las escala al espesor de cada una
        "WD": malla_json(arandela_d(1.0)), "WR": malla_json(arandela_redonda(1.0)),
        "S": malla_json(tornillo()), "N": malla_json(tuerca()),
        "p": {
            "L": L, "T": T, "cara": CARA, "ancho": ANCHO_PLACA,
            "oreja": OREJA, "zona": ZONA, "pila": PILA, "espesores": ESPESORES,
            "holguraPila": HOLGURA_PILA,
            "lengueta": [LENGUETA_ANCHO, LENGUETA_HASTA],
            "ranura": [RANURA_ANCHO, RANURA_FONDO],
            "palancaAncho": PALANCA_ANCHO, "palancaLargo": PALANCA_LARGO,
            "largoD": LARGO_D,
            "nudillo": X_NUDILLO, "hombro": [D_HOMBRO, L_HOMBRO],
            "rosca": L_ROSCA, "cabeza": [D_CABEZA, H_CABEZA],
            "entradaPila": ENTRADA_PILA,
            "topeLibre": TOPE_LIBRE, "juegoFlojo": JUEGO_FLOJO,
            "autorroscante": [D_AUTORROSCANTE, L_AUTORROSCANTE],
            "tuerca": [AF_TUERCA, E_TUERCA], "cajera": [AF_CAJERA, E_CAJERA, SOBRE_RECORRIDO],
            "tuercaPila": TUERCA_PILA,
            "xTuerca": x0 + TUERCA_PILA,
            "giro": giro,
            "vol": {"A": a.volume(), "B": b.volume()},
        },
    }
    plantilla = (AQUI / "visor_plantilla.html").read_text(encoding="utf-8")
    html = plantilla.replace("/*__DATOS__*/null", json.dumps(datos))
    (AQUI / "visor.html").write_text(html, encoding="utf-8")

    print("giro libre de B respecto de A:", giro)
    for k, man in piezas.items():
        print(f"{k:34s} {man.volume() / 1000:7.2f} cm3")


if __name__ == "__main__":
    main()
