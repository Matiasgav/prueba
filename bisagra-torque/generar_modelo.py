"""Bisagra de dos eslabones para ensayar torque de trabado con arandelas en D.

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
ANCHO_PLACA = 30.0            # placa: de 8 a 38 mm del eje
OREJA = 4.0                   # espesor de cada oreja del eslabón A

N_ARANDELAS = 4
E_ARANDELA = 0.4
JUEGO_AXIAL = 0.2
ZONA = N_ARANDELAS * E_ARANDELA + JUEGO_AXIAL  # 1.8 mm, solo en la oreja x=0
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
P_ALOJ_HOMBRO = 6.5        # lado de las arandelas: el hombro no toca fondo
# lado flojo: el hombro hace tope y deja 0.2 de juego axial a la oreja
P_ALOJ_FLOJO = L_HOMBRO - OREJA - JUEGO_FLOJO - JUEGO_FLOJO
D_PILOTO = 3.4             # M4 autorroscante en plástico
P_PILOTO = 8.0
D_AGUJERO_ARANDELA = 5.2
LARGO_D = CARA - 0.2       # la cara plana de la D queda a 0.2 de la placa

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


def eslabon_b():
    """Nudillo central entre las orejas, roscado de ambos lados."""
    x0, x1 = X_NUDILLO
    s = placa(1) + palanca(1)
    s += cil_x(R, x0, x1) + caja(x0, x1, 0, CARA + 0.5, -R, R)
    # lado de las arandelas (x0): el apriete comprime la pila
    s -= cil_x(D_ALOJ_HOMBRO / 2, x0 - 1, x0 + P_ALOJ_HOMBRO)
    s -= cil_x(D_PILOTO / 2, x0 + P_ALOJ_HOMBRO - 0.01,
               x0 + P_ALOJ_HOMBRO + P_PILOTO)
    # lado flojo (x1): el tornillo se aprieta a fondo contra el hombro
    s -= cil_x(D_ALOJ_HOMBRO / 2, x1 - P_ALOJ_FLOJO, x1 + 1)
    s -= cil_x(D_PILOTO / 2, x1 - P_ALOJ_FLOJO - P_PILOTO,
               x1 - P_ALOJ_FLOJO + 0.01)
    return s


def arandela_d():
    """D de 14 de alto: medio círculo R7 + rectángulo hasta la cara plana.
    Modelada acostada (espesor en Z) para imprimir."""
    perfil = m3d.CrossSection.circle(R, SEG) + m3d.CrossSection.square(
        [LARGO_D, T]).translate([0, -R])
    perfil -= m3d.CrossSection.circle(D_AGUJERO_ARANDELA / 2, SEG)
    return m3d.Manifold.extrude(perfil, E_ARANDELA)


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
    a, b = eslabon_a(), eslabon_b()
    w, tor = arandela_d(), tornillo()

    assert (a ^ b).volume() < 1e-6, "A y B se interfieren"
    giro = rango_giro(a, b)

    out = AQUI / "stl"
    out.mkdir(exist_ok=True)
    # A y B se imprimen acostados (Z hacia arriba); las orejas y el nudillo
    # llegan al plano de la cama porque su diámetro es el espesor.
    piezas = {
        "eslabon_A_horquilla.stl": a.translate([0, 0, R]),
        "eslabon_B_nudillo.stl": b.translate([0, 0, R]),
        "arandela_D_x1.stl": w,
    }
    lote = m3d.Manifold()
    for k in range(8):
        lote += w.translate([(k % 4) * 18.0, (k // 4) * 18.0, 0])
    piezas["arandelas_D_x8.stl"] = lote
    for nombre, man in piezas.items():
        a_trimesh(man).export(out / nombre)

    datos = {
        "A": malla_json(a), "B": malla_json(b),
        "W": malla_json(w), "S": malla_json(tor),
        "p": {
            "L": L, "T": T, "cara": CARA, "ancho": ANCHO_PLACA,
            "oreja": OREJA, "zona": ZONA, "nArandelas": N_ARANDELAS,
            "eArandela": E_ARANDELA, "juego": JUEGO_AXIAL,
            "palancaAncho": PALANCA_ANCHO, "palancaLargo": PALANCA_LARGO,
            "agujeros": AGUJEROS_PALANCA, "largoD": LARGO_D,
            "nudillo": X_NUDILLO, "hombro": [D_HOMBRO, L_HOMBRO],
            "rosca": L_ROSCA, "cabeza": [D_CABEZA, H_CABEZA],
            "alojHombro": [D_ALOJ_HOMBRO, P_ALOJ_HOMBRO],
            "alojFlojo": P_ALOJ_FLOJO, "juegoFlojo": JUEGO_FLOJO,
            "piloto": [D_PILOTO, P_PILOTO], "giro": giro,
            "vol": {"A": a.volume(), "B": b.volume(), "W": w.volume()},
        },
    }
    plantilla = (AQUI / "visor_plantilla.html").read_text(encoding="utf-8")
    html = plantilla.replace("/*__DATOS__*/null", json.dumps(datos))
    (AQUI / "visor.html").write_text(html, encoding="utf-8")

    print("giro libre de B respecto de A:", giro)
    for k, man in piezas.items():
        print(f"{k:28s} {man.volume() / 1000:7.2f} cm3")


if __name__ == "__main__":
    main()
