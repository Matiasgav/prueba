import sys,glob,os,pickle
from OCP.STEPControl import STEPControl_Reader
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
for f in sorted(glob.glob(sys.argv[1]+'/STEP/*.step')):
    r=STEPControl_Reader(); r.ReadFile(f); r.TransferRoots(); s=r.OneShape()
    p=GProp_GProps(); BRepGProp.VolumeProperties_s(s,p)
    k=0; ex=TopExp_Explorer(s,TopAbs_SOLID)
    while ex.More(): k+=1; ex.Next()
    print(os.path.basename(f), 'solidos',k,'vol %.0f mm3'%p.Mass(),'valido',BRepCheck_Analyzer(s).IsValid())
