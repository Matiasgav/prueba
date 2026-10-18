"""Bisagra de dos eslabones para ensayar torque de trabado con arandelas en D.

Genera las piezas con manifold3d, exporta los .stl a stl/ y arma visor.html
con las mallas embebidas. El eslabón B sale en dos variantes según qué lado
lleva tuerca M4 cautiva y cuál agujero autorroscante.

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

# La pila siempre suma PILA mm: arandelas D de un espesor + redondas de
# relleno. Así el hombro entra siempre lo mismo y nunca toca fondo.
PILA = 4.8
ESPESORES = (0.2, 0.4, 0.8)
JUEGO_AXIAL = 0.2
ZONA = PILA + JUEGO_AXIAL  # 5.0 mm, solo en la oreja x=0
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
R_ESQUINA_D = 1.5
HENDIDURA = (7.0, 0.5)     # ancho y profundidad, centrada en la cara plana
D_REDONDA = T

# Cuánto entra el hombro en el nudillo, medido desde la cara del nudillo.
# Lado de la pila: con los 6 discos apretados entra 3.6; la rosca empieza
# 0.6 más adentro para que el hombro nunca toque fondo y el apriete vaya a
# la pila.
ENTRADA_PILA = L_HOMBRO - OREJA - PILA
TOPE_PILA = ENTRADA_PILA + 0.6
# Lado libre: el hombro hace tope y la oreja queda con 0.2 de juego.
TOPE_LIBRE = L_HOMBRO - OREJA - 2 * JUEGO_FLOJO

# Agujero liso para que el M4 se enrosque solo en el plástico
D_AUTORROSCANTE = 3.5
L_AUTORROSCANTE = 8.0      # 5 de rosca del tornillo + margen para la punta

# Tuerca M4 (DIN 934: 7 entre caras, 3,2 de alto) cautiva, metida de costado
AF_TUERCA, E_TUERCA = 7.0, 3.2
AF_CAJERA = AF_TUERCA + 0.3
E_CAJERA = E_TUERCA + 0.3
D_PASO_TORNILLO = 4.4
# Lado de la pila: la tuerca empieza a 2,8 mm de la cara del nudillo, así
# la rosca del tornillo (de 1,2 a 6,2 mm) la atraviesa entera y queda 2,8 mm
# de pared para tomar la precarga.
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
    return hexa + caja(xa, xa + E_CAJERA, -AF_CAJERA / 2, AF_CAJERA / 2, 0, R + 1)


def eslabon_b(tuerca_en="ambos"):
    """Nudillo central entre las orejas. Cada lado lleva una tuerca M4
    cautiva o un agujero autorroscante; `tuerca_en`: "ambos", "pila" o
    "ninguno". Los agujeros se ubican solo con rotaciones."""
    x0, x1 = X_NUDILLO
    s = placa(1) + palanca(1)
    s += cil_x(R, x0, x1) + caja(x0, x1, 0, CARA + 0.5, -R, R)
    t_pila = tuerca_en in ("ambos", "pila")
    t_libre = tuerca_en == "ambos"
    if t_pila:
        s -= agujero(TUERCA_PILA, "tuerca").rotate([0, 90, 0]).translate([x0, 0, 0])
        s -= cajera_tuerca(x0 + TUERCA_PILA)
    else:
        s -= agujero(TOPE_PILA, "autorroscante").rotate([0, 90, 0]).translate([x0, 0, 0])
    if t_libre:
        # el hombro hace tope sobre la cara de la tuerca: el apriete queda
        # entre tornillo y tuerca, sin plástico en medio
        s -= agujero(TOPE_LIBRE, "tuerca").rotate([0, -90, 0]).translate([x1, 0, 0])
        s -= cajera_tuerca(x1 - TOPE_LIBRE - E_CAJERA)
    else:
        s -= agujero(TOPE_LIBRE, "autorroscante").rotate([0, -90, 0]).translate([x1, 0, 0])
    return s


def arco(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def perfil_d():
    """Medio círculo R7, esquinas R1.5 y cara plana con una hendidura central
    de perfil coseno (entra y sale tangente, sin aristas)."""
    rc, (ancho, prof) = R_ESQUINA_D, HENDIDURA
    pts = arco(0, 0, R, 90, 270, SEG // 2)
    pts += arco(LARGO_D - rc, -R + rc, rc, -90, 0)
    n = 60
    for i in range(1, n):
        z = -ancho / 2 + ancho * i / n
        pts.append((LARGO_D - prof * (1 + math.cos(2 * math.pi * z / ancho)) / 2, z))
    pts += arco(LARGO_D - rc, R - rc, rc, 0, 90)
    return pts


def arandela_d(e):
    """Arandela D de espesor e, acostada (espesor en Z) para imprimir."""
    perfil = m3d.CrossSection([perfil_d()])
    perfil -= m3d.CrossSection.circle(D_AGUJERO_ARANDELA / 2, SEG)
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


def lote(pieza, n, cols, paso=18.0):
    m = m3d.Manifold()
    for k in range(n):
        m += pieza.translate([(k % cols) * paso, (k // cols) * paso, 0])
    return m


def main():
    a = eslabon_a()
    b_ambos, b_pila = eslabon_b("ambos"), eslabon_b("pila")
    b_sin = eslabon_b("ninguno")

    for b in (b_ambos, b_pila, b_sin):
        assert (a ^ b).volume() < 1e-6, "A y B se interfieren"
    giro = rango_giro(a, b_ambos)

    out = AQUI / "stl"
    out.mkdir(exist_ok=True)
    for viejo in out.glob("*.stl"):
        viejo.unlink()
    # A y B se imprimen acostados (Z hacia arriba); las orejas y el nudillo
    # llegan al plano de la cama porque su diámetro es el espesor.
    piezas = {
        "eslabon_A_horquilla.stl": a.translate([0, 0, R]),
        "eslabon_B_tuercas.stl": b_ambos.translate([0, 0, R]),
        "eslabon_B_tuerca_en_pila.stl": b_pila.translate([0, 0, R]),
        "eslabon_B_sin_tuerca.stl": b_sin.translate([0, 0, R]),
    }
    # Cantidades: con 0.2 entran hasta 24 D; con 0.4, 12; con 0.8, 6.
    # Las redondas alcanzan para rellenar cualquier combinación.
    cant_d = {0.2: (24, 6), 0.4: (12, 4), 0.8: (8, 4)}
    cant_r = {0.2: (4, 4), 0.4: (4, 4), 0.8: (6, 3)}
    for e in ESPESORES:
        n, cols = cant_d[e]
        piezas[f"arandelas_D_{e:.1f}mm_x{n}.stl".replace(".", "_", 1)] = \
            lote(arandela_d(e), n, cols)
        n, cols = cant_r[e]
        piezas[f"arandelas_redondas_{e:.1f}mm_x{n}.stl".replace(".", "_", 1)] = \
            lote(arandela_redonda(e), n, cols, 17.0)
    for nombre, man in piezas.items():
        a_trimesh(man).export(out / nombre)

    x0, x1 = X_NUDILLO
    datos = {
        "A": malla_json(a), "Bambos": malla_json(b_ambos), "Bpila": malla_json(b_pila),
        "Bsin": malla_json(b_sin),
        # arandelas de 1 mm: el visor las escala al espesor de cada una
        "WD": malla_json(arandela_d(1.0)), "WR": malla_json(arandela_redonda(1.0)),
        "S": malla_json(tornillo()), "N": malla_json(tuerca()),
        "p": {
            "L": L, "T": T, "cara": CARA, "ancho": ANCHO_PLACA,
            "oreja": OREJA, "zona": ZONA, "pila": PILA,
            "espesores": ESPESORES, "juego": JUEGO_AXIAL,
            "hendidura": HENDIDURA, "rEsquinaD": R_ESQUINA_D,
            "palancaAncho": PALANCA_ANCHO, "palancaLargo": PALANCA_LARGO,
            "agujeros": AGUJEROS_PALANCA, "largoD": LARGO_D,
            "nudillo": X_NUDILLO, "hombro": [D_HOMBRO, L_HOMBRO],
            "rosca": L_ROSCA, "cabeza": [D_CABEZA, H_CABEZA],
            "entradaPila": ENTRADA_PILA, "topePila": TOPE_PILA,
            "topeLibre": TOPE_LIBRE, "juegoFlojo": JUEGO_FLOJO,
            "autorroscante": [D_AUTORROSCANTE, L_AUTORROSCANTE],
            "tuerca": [AF_TUERCA, E_TUERCA], "cajera": [AF_CAJERA, E_CAJERA],
            "tuercaPila": TUERCA_PILA,
            "xTuerca": {"pila": x0 + TUERCA_PILA,
                        "libre": x1 - TOPE_LIBRE - E_TUERCA},
            "giro": giro,
            "vol": {"A": a.volume(), "B": b_ambos.volume()},
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
