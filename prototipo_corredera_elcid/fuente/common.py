import cadquery as cq
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
def loadb(f):
    s=TopoDS_Shape(); BRepTools.Read_s(s,f,BRep_Builder()); return cq.Shape.cast(s)
def inter(a,b):
    try:
        v=a.intersect(b).Volume()
    except Exception as e: v=-1
    return v
