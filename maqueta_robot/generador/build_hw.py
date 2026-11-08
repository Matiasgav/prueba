from load import *
def frame(a):
    a=np.array(a,float); ref=np.array([0,0,1.]) if abs(a[2])<0.9 else np.array([1.,0,0])
    u=np.cross(a,ref); u/=np.linalg.norm(u); v=np.cross(a,u); M=np.eye(4); M[:3,0]=u; M[:3,1]=v; M[:3,2]=a; return M
def place(m,O,a,t):
    M=frame(a); M[:3,3]=np.array(O)+t*np.array(a); return m.transform(M[:3,:4])
def screw_mesh(O,sd,s_head,L):
    head=mf.Manifold.cylinder(1.65,3.0,1.5,40)
    shank=mf.Manifold.cylinder(L-1.65,1.5,1.5,24).translate([0,0,1.65])
    slot=mf.Manifold.cylinder(1.2,1.25,1.25,6).translate([0,0,-0.01])  # hexagono 2mm (allen)
    s=(head+shank)-slot
    return from_mf(place(s,O,sd,s_head))
def nut_mesh(O,sd,s0,ang):
    rc=5.5/np.sqrt(3)
    n=mf.Manifold.cylinder(4.0,rc,rc,6).rotate([0,0,ang+30]) - mf.Manifold.cylinder(10,1.5,1.5,24).translate([0,0,-1])
    return from_mf(place(n,O,sd,s0))
