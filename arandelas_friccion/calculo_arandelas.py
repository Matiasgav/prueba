#!/usr/bin/env python3
"""Verificación del paquete de arandelas de fricción (articulación con traba por fricción).

Arandela tipo A: con oreja de 5 mm, se arrastra por los lados de la oreja (1 mm encastrada).
Arandela tipo B: simétrica, se arrastra por las caras paralelas de 11 mm.
Tornillo: de hombro Ø6 / M5, hexágono 3 mm (tipo ISO 7379), inoxidable.

Todas las longitudes en mm, fuerzas en N, momentos en N·mm salvo que se indique.
Los supuestos que no salen de los planos están marcados con (SUPUESTO).
"""
import math

# --------------------------------------------------------------- geometría (planos)
R_HOLE = 3.0            # agujero Ø6
R_OUT = 6.0             # R6
H_FLATS_B = 11.0        # caras paralelas tipo B
ANG_CHAFLAN = 20.0      # 40° incluidos => 20° c/u
EAR_W = 5.0             # ancho oreja A
EAR_TIP = 7.5           # punta de la oreja desde el centro
EAR_ROOT = 5.0          # donde termina el cuerpo de A (medido en el plano, ~5,0-5,5)
EAR_ENGAGE = 1.0        # encastre de la oreja en el eslabón
# punto donde termina el plano de 11 mm de B (tangente al R6 a 20°)
L_FLAT_B = (R_OUT - (H_FLATS_B / 2) * math.sin(math.radians(ANG_CHAFLAN))) / math.cos(math.radians(ANG_CHAFLAN))

# --------------------------------------------------------------- supuestos
N_WASHERS = 6           # 3 A + 3 B intercaladas (se ve en el corte)
N_INTERFACES = 5        # A/B internas; las caras extremas se suponen solidarias (SUPUESTO)
D_CLAMP = 10.0          # Ø de la cara que aprieta (cabeza ISO 7379 Ø6 = Ø10) (SUPUESTO)
K_NUT = 0.25            # factor de par inox sin lubricar (0,20 lubricado) (SUPUESTO)
D_THREAD = 5.0
A_NECK = math.pi / 4 * 3.9**2   # garganta de la rosca del tornillo de hombro
SY_BOLT = 450.0         # A2-70 / A4-70 Rp0,2
MU_MIN, MU_MAX = 0.15, 0.40      # banda de fricción inox/inox (lubricado ... seco)

MATERIALES = {          # límite elástico Rp0,2 [MPa]
    "AISI 304 recocido": 215.0,
    "AISI 301 1/2 duro": 760.0,
    "17-7PH RH950": 1300.0,
}
ESPESORES = [0.5, 0.7, 1.0]   # (SUPUESTO) medido en la imagen ~0,55 mm


def r_eff(ri, ro):
    """Radio eficaz de fricción, presión uniforme en corona."""
    return 2 / 3 * (ro**3 - ri**3) / (ro**2 - ri**2)


R_EFF = r_eff(R_HOLE, min(D_CLAMP / 2, H_FLATS_B / 2))
A_CONTACT = math.pi * (min(D_CLAMP / 2, 5.5)**2 - R_HOLE**2)


def precarga(T_Nm, K=K_NUT):
    return T_Nm * 1000 / (K * D_THREAD)


def cap_A(t, sy):
    """Par que aguanta una arandela A antes de fluir (oreja)."""
    brazo = EAR_TIP - EAR_ENGAGE / 2                 # resultante en el centro del encastre
    F_aplast = sy * t * EAR_ENGAGE                    # aplastamiento lado oreja
    W = t * EAR_W**2 / 6                              # flexión en el plano, raíz
    F_flex = sy * W / (brazo - EAR_ROOT)
    F_corte = (sy / math.sqrt(3)) * t * EAR_W / 1.5
    F = min(F_aplast, F_flex, F_corte)
    modo = {F_aplast: "aplastamiento lateral oreja", F_flex: "flexión raíz oreja",
            F_corte: "corte raíz oreja"}[F]
    return F * brazo, modo, F


def cap_B(t, sy):
    """Par que aguanta una arandela B: presión triangular sobre medio plano de c/lado."""
    L = L_FLAT_B
    return 2 / 3 * sy * t * L**2, "aplastamiento cantos caras 11 mm"


def tornillo(T_Nm, K=K_NUT):
    F = precarga(T_Nm, K)
    sig = F / A_NECK
    T_rosca = 0.5 * T_Nm * 1000                       # ~50 % del par va a la rosca
    tau = 16 * T_rosca / (math.pi * 3.9**3)
    return F, sig, math.sqrt(sig**2 + 3 * tau**2)


def main():
    p = print
    p(f"Radio eficaz de fricción r_eff = {R_EFF:.2f} mm (corona Ø6–Ø{D_CLAMP:g})")
    p(f"Largo de semiplano B = {L_FLAT_B:.2f} mm\n")

    p("== Tornillo de hombro Ø6/M5 inox, llave Allen 3 mm ==")
    for T in (1.0, 2.5, 4.0):
        F, s, vm = tornillo(T)
        p(f"  T={T:.1f} N·m -> F={F:5.0f} N, σ={s:4.0f} MPa, von Mises={vm:4.0f} MPa "
          f"(Rp0,2 {SY_BOLT:.0f}) | compresión en corona {F/A_CONTACT:4.0f} MPa")
    F_hand = precarga(2.5)
    p("")

    p("== Capacidad por arandela y condición 'desliza antes de deformar' ==")
    p("t[mm] | material            | T_A [N·m] modo                  | T_B [N·m] | F_máx desliz.[N] | T_apriete[N·m] | T_traba máx [N·m] | T_fricc. a 2,5 N·m apriete por arandela")
    for t in ESPESORES:
        for nombre, sy in MATERIALES.items():
            tA, modoA, _ = cap_A(t, sy)
            tB, _ = cap_B(t, sy)
            tcap = min(tA, tB)
            F_lim = tcap / (2 * MU_MAX * R_EFF)       # peor caso μ alto
            T_apr = F_lim * K_NUT * D_THREAD / 1000
            T_traba = N_INTERFACES * MU_MAX * F_lim * R_EFF / 1000   # = N_int * tcap / 2
            T_w_hand = 2 * MU_MAX * F_hand * R_EFF / 1000
            p(f"{t:4.1f}  | {nombre:19s} | {tA/1000:5.2f} {modoA:26s} | {tB/1000:5.2f}     | "
              f"{F_lim:7.0f}          | {T_apr:5.2f}          | {T_traba:5.2f}             | "
              f"{T_w_hand:4.2f} ({'OK' if T_w_hand <= tcap/1000 else 'FLUYE'})")


if __name__ == "__main__":
    main()
