"""Bisagra de dos eslabones para ensayar torque de trabado con arandelas en D.

Genera las piezas con manifold3d, exporta los .stl a stl/ y arma visor.html
con las mallas embebidas. El eslabón B sale en dos variantes según qué lado
lleva el inserto térmico y cuál el agujero autorroscante.

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
ANCHO_PLACA = 30.0            # placa: de 8 a 38 mm del eje
OREJA = 4.0                   # espesor de cada oreja del eslabón A

RANURAS = 6        # discos en la pila: arandelas D + redondas, siempre 6
E_ARANDELA = 0.4
JUEGO_AXIAL = 0.2
ZONA = RANURAS * E_ARANDELA + JUEGO_AXIAL  # 2.6 mm, solo en la oreja x=0
JUEGO_FLOJO = 0.2  # oreja x=50, sin arandelas: gira libre

PALANCA_ANCHO = 20.0
PALANCA_LARGO = 50.0
AGUJEROS_PALANCA = [60.0, 80.0]  # distancia al eje, para colgar peso
D_AGUJERO_PALANCA = 5.0

# Tornillo Accu SSHE-M4-5-10-A2 (ISO 7379): hombro Ø5 x 10, rosca M4 x 5,
# cabeza Ø8 x 4
D_HOMBRO, L_HOMBRO = 5.0, 10.0
L_ROSCA = 5.0
D_CABEZA, H_CABEZA = 8.0, 4.0

D_AGUJERO_OREJA = 5.2      # el hombro gira en la oreja
D_ALOJ_HOMBRO = 5.4
D_AGUJERO_ARANDELA = 5.2
LARGO_D = CARA - 0.2       # la cara plana de la D queda a 0.2 de la placa
D_REDONDA = T

# Cuánto entra el hombro en el nudillo, medido desde la cara del nudillo.
# Lado de la pila: con los 6 discos apretados entra 3.6; la rosca empieza
# 0.6 más adentro para que el hombro nunca toque fondo y el apriete vaya a
# la pila.
ENTRADA_PILA = L_HOMBRO - OREJA - RANURAS * E_ARANDELA
TOPE_PILA = ENTRADA_PILA + 0.6
# Lado libre: el hombro hace tope y la oreja queda con 0.2 de juego.
TOPE_LIBRE = L_HOMBRO - OREJA - 2 * JUEGO_FLOJO

# Agujero liso para que el M4 se enrosque solo en el plástico
D_AUTORROSCANTE = 3.5
L_AUTORROSCANTE = 8.0      # 5 de rosca del tornillo + margen para la punta

# Inserto térmico M4 (tipo Ruthex M4 x 8.1): agujero Ø5.6; se empuja hasta
# que asienta en el escalón del fondo
D_INSERTO, L_INSERTO = 5.6, 8.1
D_PASO_PUNTA = 4.4         # después del inserto, por si la punta sobresale

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


def palanca(signo):
    x0 = (L - PALANCA_ANCHO) / 2
    y0, y1 = CARA + ANCHO_PLACA, CARA + ANCHO_PLACA + PALANCA_LARGO
    p = caja(x0, x0 + PALANCA_ANCHO, y0 - 1, y1, -R, R)
    for d in AGUJEROS_PALANCA:
        p -= cil_z(D_AGUJERO_PALANCA / 2, L / 2, d, -R - 1, R + 1)
    return p.mirror([0, 1, 0]) if signo < 0 else p


def placa(signo):
    p = caja(0, L, CARA, CARA + ANCHO_PLACA, -R, R)
    return p.mirror([0, 1, 0]) if signo < 0 else p


# --- Piezas ----------------------------------------------------------------


def eslabon_a():
    """Horquilla: placa en -Y y dos orejas de 4 mm en los extremos."""
    s = placa(-1) + palanca(-1)
    for x0, x1 in [(0, OREJA), (L - OREJA, L)]:
        s += cil_x(R, x0, x1) + caja(x0, x1, -CARA - 0.5, 0, -R, R)
        s -= cil_x(D_AGUJERO_OREJA / 2, x0 - 1, x1 + 1)
    return s


def agujero(tope, tipo):
    """Agujero del nudillo en coordenadas locales: eje +Z hacia adentro,
    z=0 en la cara del nudillo. `tope`: profundidad donde empieza la rosca."""
    if tipo == "autorroscante":
        h = m3d.Manifold.cylinder(tope + 1, D_ALOJ_HOMBRO / 2, D_ALOJ_HOMBRO / 2,
                                  SEG).translate([0, 0, -1])
        r = D_AUTORROSCANTE / 2
        h += m3d.Manifold.cylinder(L_AUTORROSCANTE, r, r, SEG).translate(
            [0, 0, tope - 0.01])
        # chaflán de entrada para que la rosca arranque derecha
        return h + m3d.Manifold.cylinder(0.5, r + 0.5, r, SEG).translate(
            [0, 0, tope - 0.01])
    # inserto: entra por la cara y asienta en el escalón de tope + L_INSERTO
    fondo = tope + L_INSERTO
    h = m3d.Manifold.cylinder(fondo + 1, D_INSERTO / 2, D_INSERTO / 2,
                              SEG).translate([0, 0, -1])
    return h + m3d.Manifold.cylinder(3, D_PASO_PUNTA / 2, D_PASO_PUNTA / 2,
                                     SEG).translate([0, 0, fondo - 0.01])


def eslabon_b(inserto_en="pila"):
    """Nudillo central entre las orejas. Un lado lleva agujero autorroscante y el
    otro inserto térmico; `inserto_en` elige el lado ("pila" o "libre").
    Los agujeros se ubican solo con rotaciones para no invertir la rosca."""
    x0, x1 = X_NUDILLO
    s = placa(1) + palanca(1)
    s += cil_x(R, x0, x1) + caja(x0, x1, 0, CARA + 0.5, -R, R)
    tipo_pila = "inserto" if inserto_en == "pila" else "autorroscante"
    tipo_libre = "autorroscante" if inserto_en == "pila" else "inserto"
    s -= agujero(TOPE_PILA, tipo_pila).rotate([0, 90, 0]).translate([x0, 0, 0])
    s -= agujero(TOPE_LIBRE, tipo_libre).rotate([0, -90, 0]).translate([x1, 0, 0])
    return s


def arandela_d():
    """D de 14 de alto: medio círculo R7 + rectángulo hasta la cara plana.
    Modelada acostada (espesor en Z) para imprimir."""
    perfil = m3d.CrossSection.circle(R, SEG) + m3d.CrossSection.square(
        [LARGO_D, T]).translate([0, -R])
    perfil -= m3d.CrossSection.circle(D_AGUJERO_ARANDELA / 2, SEG)
    return m3d.Manifold.extrude(perfil, E_ARANDELA)


def arandela_redonda():
    """Arandela libre: no se traba con ningún eslabón. Rellena la pila."""
    perfil = m3d.CrossSection.circle(D_REDONDA / 2, SEG)
    perfil -= m3d.CrossSection.circle(D_AGUJERO_ARANDELA / 2, SEG)
    return m3d.Manifold.extrude(perfil, E_ARANDELA)


def inserto():
    """Solo para el visor. Eje X, desde x=0."""
    return cil_x(D_INSERTO / 2 - 0.1, 0, L_INSERTO) - cil_x(2.0, -1, L_INSERTO + 1)


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


def lote(pieza, n, cols, paso=18.0):
    m = m3d.Manifold()
    for k in range(n):
        m += pieza.translate([(k % cols) * paso, (k // cols) * paso, 0])
    return m


def main():
    a = eslabon_a()
    b_pila, b_libre = eslabon_b("pila"), eslabon_b("libre")
    wd, wr = arandela_d(), arandela_redonda()

    for b in (b_pila, b_libre):
        assert (a ^ b).volume() < 1e-6, "A y B se interfieren"
    giro = rango_giro(a, b_pila)

    out = AQUI / "stl"
    out.mkdir(exist_ok=True)
    for viejo in out.glob("*.stl"):
        viejo.unlink()
    # A y B se imprimen acostados (Z hacia arriba); las orejas y el nudillo
    # llegan al plano de la cama porque su diámetro es el espesor.
    piezas = {
        "eslabon_A_horquilla.stl": a.translate([0, 0, R]),
        "eslabon_B_inserto_en_pila.stl": b_pila.translate([0, 0, R]),
        "eslabon_B_inserto_en_libre.stl": b_libre.translate([0, 0, R]),
        "arandelas_D_x8.stl": lote(wd, 8, 4),
        "arandelas_redondas_x6.stl": lote(wr, 6, 3, 17.0),
    }
    for nombre, man in piezas.items():
        a_trimesh(man).export(out / nombre)

    x0, x1 = X_NUDILLO
    datos = {
        "A": malla_json(a), "Bp": malla_json(b_pila), "Bl": malla_json(b_libre),
        "WD": malla_json(wd), "WR": malla_json(wr),
        "S": malla_json(tornillo()), "I": malla_json(inserto()),
        "p": {
            "L": L, "T": T, "cara": CARA, "ancho": ANCHO_PLACA,
            "oreja": OREJA, "zona": ZONA, "ranuras": RANURAS,
            "eArandela": E_ARANDELA, "juego": JUEGO_AXIAL,
            "palancaAncho": PALANCA_ANCHO, "palancaLargo": PALANCA_LARGO,
            "agujeros": AGUJEROS_PALANCA, "largoD": LARGO_D,
            "nudillo": X_NUDILLO, "hombro": [D_HOMBRO, L_HOMBRO],
            "rosca": L_ROSCA, "cabeza": [D_CABEZA, H_CABEZA],
            "entradaPila": ENTRADA_PILA, "topePila": TOPE_PILA,
            "topeLibre": TOPE_LIBRE, "juegoFlojo": JUEGO_FLOJO,
            "autorroscante": [D_AUTORROSCANTE, L_AUTORROSCANTE],
            "inserto": [D_INSERTO, L_INSERTO],
            "xInserto": {"pila": x0 + TOPE_PILA,
                         "libre": x1 - TOPE_LIBRE - L_INSERTO},
            "giro": giro,
            "vol": {"A": a.volume(), "B": b_pila.volume()},
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
