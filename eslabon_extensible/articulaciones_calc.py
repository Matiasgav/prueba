"""Cálculos de las opciones de articulación sin tornillos (ver ARTICULACIONES_OPCIONES.md).

Para cada articulación con pasador a la vista (Q1, Q2, O, C) y cada concepto:
  - flexión del pasador (o del tubo) con el mismo modelo que analisis.py:
        M = F/2 · (t_apoyo/2 + juego + t_ojo/4)
  - aplastamiento en la mejilla que queda después de cajeras y avellanados,
  - capacidad de la traba axial y momento en la garganta (donde la hay),
  - anillo elástico: tensión al abrirse para dejar pasar el pasador.
Márgenes a W = 35, sobre la carga que rompe la estructura (salida/capacidad.json).
"""
import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
CAP = json.load(open(os.path.join(AQUI, "salida", "capacidad.json")))
R35 = [r for r in CAP if r["W"] == 35.0][0]
F_ESTR = min(R35["traccion"], R35["compresion"])           # carga entre ejes que rompe la estructura
FZ = R35["fuerzas"]                                        # fuerza en cada pivote por N entre ejes

AL = dict(nombre="7075-T651", Sy=503.0)
H900 = dict(nombre="17-4PH H900", Sy=1170.0)
D = 5.0
JUEGO = 0.1

# pivote: fuerza por N, espesor de cada mejilla, espesor del ojo, material de la mejilla
PIVOTES = {
    "Q1": dict(f=FZ["eslabon1_Q1"], t=2.9, te=7.0, mej=AL),
    "Q2": dict(f=FZ["eslabon2"], t=2.9, te=7.0, mej=AL),
    "O": dict(f=FZ["corto"], t=5.15, te=2.5, mej=AL),
    "C": dict(f=FZ["corto"], t=2.15, te=2.5, mej=H900),
}

# conceptos: sección resistente del pasador, admisible a flexión, cuánto se come la cajera/avellanado
# de cada mejilla (arriba, abajo) en Q/O y en C, y piso de agujero ciego
Z_MACIZO = math.pi * D ** 3 / 32
Z_TUBO = math.pi * (D ** 4 - 3.3 ** 4) / (32 * D)
CONCEPTOS = {
    "A anillo oculto (pasador ciego)": dict(Z=Z_MACIZO, S=1500, rebaje=(0.0, 0.6), rebaje_C=(0.0, 0.6)),
    "B cabeza + virola estampada": dict(Z=Z_MACIZO, S=1500, rebaje=(1.0, 1.2), rebaje_C=(0.7, 0.8)),
    "C tubo + remache aeronáutico": dict(Z=Z_TUBO, S=1500, rebaje=(1.1, 1.1), rebaje_C=(1.1, 1.1)),
    "D estampado del aluminio": dict(Z=Z_MACIZO, S=1500, rebaje=(0.0, 0.0), rebaje_C=None),
    "E remache del pasador (H1150)": dict(Z=Z_MACIZO, S=725, rebaje=(0.3, 0.3), rebaje_C=(0.3, 0.3)),
    # F: casquillo Ø5/Ø3,2 + perno macho Ø3,2 ajustado adentro: flexionan juntos (I casi de macizo);
    # manda la fibra del casquillo con I total. Cabezas de 1,0 (0,7 en C) en las dos caras.
    "F casquillo + perno con anillo interno": dict(Z=math.pi * D ** 4 / 64 / (D / 2), S=1500,
                                                   rebaje=(1.0, 1.0), rebaje_C=(0.7, 0.7)),
    # G: pasador ciego abajo, tapón estampado en cajera con contrasalida arriba (cajera de 1,2)
    "G tapón estampado sobre el pasador": dict(Z=Z_MACIZO, S=1500, rebaje=(1.2, 0.6), rebaje_C=(0.8, 0.6)),
    # H: pasador de temple parcial (centro templado, puntas blandas) remachado
    "H temple parcial + puntas remachadas": dict(Z=Z_MACIZO, S=1500, rebaje=(0.3, 0.3), rebaje_C=(0.3, 0.3)),
}


def margenes(c, p):
    reb = c["rebaje_C"] if p is PIVOTES["C"] else c["rebaje"]
    if reb is None:
        return None
    F = p["f"] * F_ESTR
    t_ap = p["t"] - max(reb)                       # la mejilla más recortada manda
    m = F / 2 * (t_ap / 2 + JUEGO + p["te"] / 4)
    flex = c["S"] / (m / c["Z"])
    apl = 1.5 * p["mej"]["Sy"] / ((F / 2) / (D * t_ap))
    return flex, apl, F


def fraccion_momento(x_desde_afuera, t, te):
    """Momento en una sección de la mejilla, a x de la cara exterior, sobre el momento máximo del
    modelo (reparto triangular de la presión en la mejilla)."""
    m_x = x_desde_afuera ** 3 / (3 * t ** 2)
    m_max = t / 2 + JUEGO + te / 4
    return m_x / m_max


def anillo(d_alambre, di_libre, di_abierto, E=193000.0):
    """Anillo partido de alambre redondo: tensión de flexión al abrirse de di_libre a di_abierto."""
    r0 = (di_libre + d_alambre) / 2
    r1 = (di_abierto + d_alambre) / 2
    return E * d_alambre / 2 * (1 / r0 - 1 / r1)


if __name__ == "__main__":
    print(f"Carga entre ejes que rompe la estructura a W = 35: {F_ESTR:.0f} N")
    for n, c in CONCEPTOS.items():
        print(f"\n{n}")
        for j, p in PIVOTES.items():
            r = margenes(c, p)
            if r is None:
                print(f"  {j}: no aplica")
                continue
            flex, apl, F = r
            print(f"  {j}: F = {F:5.0f} N   flexión del pasador: margen {flex:4.2f}   aplastamiento mejilla: margen {apl:4.2f}")
    print("\nMomento en la garganta (fracción del máximo):")
    for j, x in (("Q, garganta a 1,0 de la cara (A, B)", 1.0), ("Q, garganta a 2,0", 2.0)):
        print(f"  {j}: {fraccion_momento(x, 2.9, 7.0) * 100:.1f} %")
    print(f"  C, garganta a 0,9 del piso del ala: {fraccion_momento(0.9, 1.55, 2.5) * 100:.1f} %")
    print("\nAnillo oculto (alambre inoxidable de resorte, Rp ≈ 1.500 a 1.700 MPa):")
    for dw, di in ((0.5, 4.75), (0.6, 4.70), (0.6, 4.60)):
        s = anillo(dw, di, 5.05)
        print(f"  alambre Ø{dw}, Ø interior libre {di}: al abrirse a 5,05 -> {s:.0f} MPa;"
              f" se mete {(5.0 - di) / 2:.2f} mm en la garganta del pasador")
    print("\nCapacidad axial de las trabas (estimada):")
    print(f"  A anillo Ø0,6: contacto en el pasador 0,15 × π × 4,7 = {0.15 * math.pi * 4.7:.1f} mm²"
          f" -> ~{0.15 * math.pi * 4.7 * 1000 / 1000:.1f} kN techo; real 0,5 a 1 kN (el anillo rueda)")
    print(f"  B virola 304 recocido, garganta 0,8 × 0,3: corte π × 4,4 × 0,8 × 0,6 × 520 = "
          f"{math.pi * 4.4 * 0.8 * 0.6 * 520 / 1000:.1f} kN")
    print(f"  C cabeza MS20426-4 sobre la mejilla: π/4 (5,72² − 5²) × 755 = "
          f"{math.pi / 4 * (5.72 ** 2 - 25) * 755 / 1000:.1f} kN")
    print(f"  D aluminio en garganta 0,8: π × 5 × 0,8 × 0,58 × 503 = {math.pi * 5 * 0.8 * 0.58 * 503 / 1000:.1f} kN")
    print(f"  F anillo Ø0,5 entre casquillo y perno Ø3,2 (acero/acero): ~{0.12 * math.pi * 3.2 * 1200 / 1000:.1f} kN techo; real ~0,5 kN")
    print(f"  G tapón de inox. 304 recocido Ø6 en contrasalida de 0,3: corte π × 6 × 0,8 × 0,6 × 520 = "
          f"{math.pi * 6 * 0.8 * 0.6 * 520 / 1000:.1f} kN")
    print(f"  G pared entre la cajera Ø6,6 (con contrasalida) y la cara interior de A: {14.2 - 10 - 3.3:.2f} mm")
    p_hinch, r_i, r_m, t_tubo = 250.0, 1.65, 2.07, 0.85
    print(f"\nC: si el remache hincha el tubo con {p_hinch:.0f} MPa, el diámetro exterior crece "
          f"~{2 * p_hinch * r_i * r_m / (200000 * t_tubo) * 1000:.0f} µm (el ojo tiene 0 a 3 µm de holgura)")
