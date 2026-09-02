"""Propiedades de materiales usadas en todo el modelo.

Cada valor lleva su trazabilidad:
    V = verificado contra fuente primaria o recálculo independiente
    E = estimación (tratar como tal, no como dato)
    ? = incógnita abierta (parametrizar, no inventar)

Referencia de origen: brief WTD/GRIS, septiembre 2026, §3, §4.4, §4.5, §4.7.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Material:
    """Material elástico isótropo equivalente (para Hertz y viga)."""

    name: str
    E: float           # módulo de Young [Pa]
    nu: float          # coeficiente de Poisson [-]
    rho: float         # densidad [kg/m^3]
    G: float | None = None      # módulo de corte [Pa]; None => E/(2(1+nu))
    sigma_y: float | None = None   # límite de fluencia / compresión [Pa]
    hardness_HV: float | None = None
    tag: str = "E"     # trazabilidad V / E / ?
    note: str = ""

    @property
    def shear_modulus(self) -> float:
        if self.G is not None:
            return self.G
        return self.E / (2.0 * (1.0 + self.nu))

    def with_E(self, E: float) -> "Material":
        return replace(self, E=E)


# --------------------------------------------------------------------------
# Aceros y metales duros (punta del martillo, cuerpo de la masa)
# --------------------------------------------------------------------------

STEEL = Material(
    name="Acero (bola rodamiento 100Cr6)",
    E=210e9, nu=0.29, rho=7850.0,
    sigma_y=2.0e9, hardness_HV=750,
    tag="V", note="E, nu del brief §4.4. rho nominal acero.",
)

TUNGSTEN_CARBIDE = Material(
    name="Carburo de tungsteno (WC-Co 6%)",
    E=600e9, nu=0.22, rho=14900.0,
    sigma_y=4.5e9, hardness_HV=1500,
    tag="V", note="E, nu del brief §4.4. rho típico WC-6Co.",
)

# Aleación pesada de tungsteno (W 90-97 %, matriz Ni-Fe). Es lo que permite
# meter 10-15 g en el envolvente de 10x10x50 sin ocupar todo el volumen.
TUNGSTEN_HEAVY = Material(
    name="Aleación pesada W (W-Ni-Fe 95%)",
    E=360e9, nu=0.28, rho=18000.0,
    sigma_y=0.7e9, hardness_HV=320,
    tag="E", note="Densimet/Inermet clase 18 g/cm3. Valores típicos de catálogo.",
)

SPRING_STEEL = Material(
    name="Acero de resorte (SAE 1074 / 17-7PH)",
    E=200e9, nu=0.30, rho=7850.0,
    sigma_y=1.5e9,
    tag="E", note="Para dimensionado de resortes plano/helicoidal.",
)

TITANIUM = Material(
    name="Ti-6Al-4V",
    E=114e9, nu=0.34, rho=4430.0, sigma_y=0.88e9,
    tag="E",
)

ALUMINUM = Material(
    name="Aluminio 7075-T6",
    E=71.7e9, nu=0.33, rho=2810.0, sigma_y=0.503e9,
    tag="E",
)

SI3N4 = Material(
    name="Nitruro de silicio (bola cerámica)",
    E=310e9, nu=0.27, rho=3200.0, sigma_y=3.0e9, hardness_HV=1600,
    tag="E",
)

# --------------------------------------------------------------------------
# G11 (laminado epoxi-vidrio tejido, cuña de ranura)
# --------------------------------------------------------------------------
#
# ATENCIÓN a la inconsistencia heredada del brief:
#   §4.4 (Hertz) usa E = 20 GPa, nu = 0.2   [E]
#   §4.7 (modal) usa E = 24 GPa, rho = 1900 [V] (los anclas de f1 salen con 24)
# Ambos se mantienen tal cual porque los casos ancla de §9 dependen de ellos.
# La diferencia es real y es una incógnita abierta (#6): en un laminado tejido
# el módulo "de flexión" en el plano y el módulo transversal que ve un
# indentador esférico NO tienen por qué coincidir.

G11_HERTZ = Material(
    name="G11 (transversal, para contacto de Hertz)",
    E=20e9, nu=0.20, rho=1900.0,
    sigma_y=400e6,
    tag="E", note="Brief §4.4. Incógnita abierta #6.",
)

G11_BEAM = Material(
    name="G11 (flexión en el plano, para viga)",
    E=24e9, nu=0.20, rho=1900.0,
    G=5.7e9,
    tag="V", note="Brief §4.7. G13 = 5.7 GPa (PPPL/ITER G11-CR 300 K, rango 4.8-6.8).",
)

# Rango reportado del módulo de corte fuera del plano del G11-CR a 300 K.
G11_G13_RANGE = (4.8e9, 6.8e9)

# --------------------------------------------------------------------------
# Umbrales de daño en G11 bajo indentador esférico  [E] (brief §4.5)
# Calibrados contra el ensayo de bola de Matías: 900 MPa no deja marca.
# --------------------------------------------------------------------------

G11_DAMAGE = {
    "elastic_max": 640e6,      # < 640 MPa: elástico, sin marca
    "yield_local_max": 1800e6,  # 640-1800: fluencia local, marca leve acumulativa
    # > 1800 MPa: plastificación, indentación visible
}

MATERIALS = {
    "steel": STEEL,
    "wc": TUNGSTEN_CARBIDE,
    "w_heavy": TUNGSTEN_HEAVY,
    "spring_steel": SPRING_STEEL,
    "ti": TITANIUM,
    "al": ALUMINUM,
    "si3n4": SI3N4,
    "g11_hertz": G11_HERTZ,
    "g11_beam": G11_BEAM,
}

G = 9.80665  # gravedad estándar [m/s^2]
MU0 = 4e-7 * 3.141592653589793  # permeabilidad del vacío [H/m]
