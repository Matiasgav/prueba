from build import *
def iv(a,b):
    x=a.intersect(b); v=x.Volume(); return v, (x.BoundingBox() if v>1e-6 else None)
print("chasis∩tapa", "%.4f"%iv(chasis,tapa)[0])
for s in (-17.25,-11.7,-5,0,5,7.5):
    b = caja.translate(cq.Vector(s-S0,0,0))
    pts,xb = cable_pts(s); c = tube(pts, CABLE_D/2)
    out=[]
    for n,o in (("chasis",chasis),("tapa",tapa),("bobina",b)):
        v,bb=iv(c,o); out.append(f"cable∩{n}={v:.4f}" + (f" @({bb.xmin:.1f},{bb.ymin:.1f},{bb.zmin:.1f})-({bb.xmax:.1f},{bb.ymax:.1f},{bb.zmax:.1f})" if v>1e-4 else ""))
    for n,o in (("chasis",chasis),("tapa",tapa)):
        v,bb=iv(b,o); out.append(f"bob∩{n}={v:.4f}")
    # holgura mínima bobina-chasis/tapa y cable-pared
    d1=b.distance(chasis) if hasattr(b,'distance') else None
    print(f"s={s:6.2f} xb={xb:6.2f} xs={s-S0-4.2:6.2f} curva_ext={xb+R+0.5:6.2f}", *out)
