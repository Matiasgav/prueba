import numpy as np, trimesh
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCP.TopoDS import TopoDS
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Solid
def mesh_to_solid(m, tol=1e-3):
    m=trimesh.Trimesh(m.vertices,m.faces,process=True)
    V=m.vertices; sew=BRepBuilderAPI_Sewing(tol)
    for f in m.faces:
        a,b,c=V[f]
        if np.linalg.norm(np.cross(b-a,c-a))<1e-10: continue
        p=BRepBuilderAPI_MakePolygon(gp_Pnt(*a),gp_Pnt(*b),gp_Pnt(*c),True)
        fc=BRepBuilderAPI_MakeFace(p.Wire(),True)
        if fc.IsDone(): sew.Add(fc.Face())
    sew.Perform(); sh=sew.SewedShape()
    ex=TopExp_Explorer(sh,TopAbs_SHELL); shells=[]
    while ex.More(): shells.append(TopoDS.Shell(ex.Current())); ex.Next()
    ms=BRepBuilderAPI_MakeSolid()
    for s in shells: ms.Add(s)
    sol=ms.Solid(); fx=ShapeFix_Solid(sol); fx.Perform(); sol=fx.Solid()
    u=ShapeUpgrade_UnifySameDomain(sol,True,True,False); u.Build(); out=u.Shape()
    if not BRepCheck_Analyzer(out).IsValid():
        from OCP.ShapeFix import ShapeFix_Shape
        fx2=ShapeFix_Shape(out); fx2.Perform(); out=fx2.Shape()
    return out, BRepCheck_Analyzer(out).IsValid()
def write_step(shapes_named, path):
    from OCP.STEPCAFControl import STEPCAFControl_Writer
    from OCP.XCAFApp import XCAFApp_Application
    from OCP.TDocStd import TDocStd_Document
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.XCAFDoc import XCAFDoc_DocumentTool
    from OCP.TDataStd import TDataStd_Name
    from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
    from OCP.XCAFDoc import XCAFDoc_ColorType
    from OCP.STEPControl import STEPControl_AsIs
    from OCP.Interface import Interface_Static
    app=XCAFApp_Application.GetApplication_s(); doc=TDocStd_Document(TCollection_ExtendedString("XmlOcaf")); app.InitDocument(doc)
    st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    for name,shape,rgb in shapes_named:
        lab=st.AddShape(shape,False)
        TDataStd_Name.Set_s(lab,TCollection_ExtendedString(name))
        if rgb: ct.SetColor(lab,Quantity_Color(*rgb,Quantity_TOC_RGB),XCAFDoc_ColorType.XCAFDoc_ColorSurf)
    Interface_Static.SetCVal_s("write.step.schema","AP214")
    Interface_Static.SetCVal_s("write.step.unit","MM")
    w=STEPCAFControl_Writer(); w.SetNameMode(True); w.SetColorMode(True); w.Transfer(doc,STEPControl_AsIs); w.Write(path)
