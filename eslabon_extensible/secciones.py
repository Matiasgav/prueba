"""Propiedades de sección de las piezas del CAD, cortadas por planos y = cte (flexión en el plano XY)."""
import cadquery as cq
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

T_LONCHA = 0.05


def seccion(pieza, y):
    """Devuelve área [mm²], x del baricentro, I respecto del eje Z por el baricentro [mm⁴], c_max [mm]."""
    sol = pieza.val() if hasattr(pieza, "val") else pieza
    bb = sol.BoundingBox()
    loncha = cq.Solid.makeBox(bb.xlen + 2, T_LONCHA, bb.zlen + 2, cq.Vector(bb.xmin - 1, y, bb.zmin - 1))
    s = sol.intersect(loncha)
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(s.wrapped, props)
    v = props.Mass()
    if v < 1e-9:
        return dict(A=0.0, xc=0.0, I=0.0, c=0.0, xmin=0.0, xmax=0.0)
    cm = props.CentreOfMass()
    m = props.MatrixOfInertia()
    ixx, iyy, izz = m.Value(1, 1), m.Value(2, 2), m.Value(3, 3)
    ix2 = (iyy + izz - ixx) / 2          # ∫(x-xc)² dV
    sb = s.BoundingBox()
    return dict(A=v / T_LONCHA, xc=cm.X(), I=ix2 / T_LONCHA,
                c=max(cm.X() - sb.xmin, sb.xmax - cm.X()), xmin=sb.xmin, xmax=sb.xmax)


def apoyo_perno(pieza, x, y, d, ancho=1.5):
    """Volumen de material en un anillo alrededor del perno, por capa (abajo, medio, arriba)."""
    sol = pieza.val() if hasattr(pieza, "val") else pieza
    out = {}
    for nombre, (z0, z1) in {"inf": (0, 2.9), "med": (3.0, 10.0), "sup": (10.1, 13)}.items():
        anillo = (cq.Workplane("XY").workplane(offset=z0).center(x, y)
                  .circle(d / 2 + ancho).circle(d / 2 + 0.01).extrude(z1 - z0)).val()
        vol_lleno = anillo.Volume()
        out[nombre] = sol.intersect(anillo).Volume() / vol_lleno
    return out
