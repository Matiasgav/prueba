import trimesh,numpy as np
import os
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','src','Robot mel')+'/'
def link(n, minfill=0.06, minvol=100):
    m=trimesh.load(SRC+n+'.stl'); m.apply_scale(1000)
    bs=[b for b in m.split(only_watertight=False) if b.volume/np.prod(b.extents)>=minfill and b.volume>minvol]
    return trimesh.util.concatenate(bs)
import manifold3d as mf
def to_mf(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices,np.float32), tri_verts=np.asarray(m.faces,np.uint32)))
# tapas de chapa (cascaras finas) que se conservan MACIZAS (envolvente convexa) -> sin cavidades debajo
COVERS={'base':[6], 'j1':[2]}
def link_mf(n, **kw):
    m=trimesh.load(SRC+n+'.stl'); m.apply_scale(1000)
    out=None
    bodies=sorted([b for b in m.split(only_watertight=False) if b.volume>=100], key=lambda b:-b.volume)
    for i,b in enumerate(bodies):
        if i in COVERS.get(n,[]):
            x=to_mf(b.convex_hull); out = x if out is None else out+x; continue
        if b.volume/np.prod(b.extents)<kw.get('minfill',0.06) or b.volume<kw.get('minvol',100): continue
        c=b.bounds.mean(0); e=np.maximum(b.extents,1e-6); k=(e+kw.get('grow',1.2))/e
        M=np.eye(4); M[:3,:3]=np.diag(k); M[:3,3]=c-k*c
        x=to_mf(b).transform(M[:3,:4])
        out = x if out is None else out+x
    return out
def from_mf(x):
    me=x.to_mesh(); return trimesh.Trimesh(me.vert_properties[:,:3], me.tri_verts, process=False)

def _fill_axis(m, axis, dz=0.25, min_area=0.3):
    # gira la pieza para que 'axis' quede en Z, rellena los huecos encerrados de cada capa
    rot={'z':None,'x':[0,-90,0],'y':[90,0,0]}[axis]
    mm = m if rot is None else m.rotate(rot)
    lo,hi = mm.bounding_box()[2], mm.bounding_box()[5]
    slabs=[]
    z=lo+dz/2
    while z<hi:
        cs=mm.slice(z)
        if not cs.is_empty():
            polys=cs.to_polygons()
            outer=[p for p in polys if _area(p)>0]
            if outer:
                full=mf.CrossSection(outer)
                holes=(full-cs).offset(0.08, mf.JoinType.Miter)
                if holes.area()>min_area:
                    slabs.append(mf.Manifold.extrude(holes, dz+0.02).translate([0,0,z-dz/2-0.01]))
        z+=dz
    if not slabs: return None
    f=mf.Manifold.compose(slabs)
    if rot is not None: f=f.rotate([-r for r in rot]) if axis=='z' else (f.rotate([0,90,0]) if axis=='x' else f.rotate([-90,0,0]))
    return f
def _area(p):
    p=np.asarray(p); x,y=p[:,0],p[:,1]; return 0.5*np.sum(x*np.roll(y,-1)-np.roll(x,-1)*y)
def solidify(m):
    out=m
    for ax in ('z','x','y'):
        f=_fill_axis(m,ax)
        if f is not None: out=out+f
    return out

def close_cavities(m, pitch=0.3, r=1.6):
    """Rellena cavidades cuya boca es menor que 2r (cierre morfologico en voxeles)."""
    from scipy import ndimage
    from matplotlib.path import Path
    from skimage import measure
    b=np.array(m.bounding_box()).reshape(2,3); pad=r+2*pitch
    lo=b[0]-pad; hi=b[1]+pad
    xs=np.arange(lo[0],hi[0],pitch); ys=np.arange(lo[1],hi[1],pitch); zs=np.arange(lo[2],hi[2],pitch)
    X,Y=np.meshgrid(xs,ys,indexing='ij'); P=np.c_[X.ravel(),Y.ravel()]
    O=np.zeros((len(xs),len(ys),len(zs)),bool)
    for k,z in enumerate(zs):
        cs=m.slice(z)
        if cs.is_empty(): continue
        inside=np.zeros(len(P),int)
        for q in cs.to_polygons():
            q=np.asarray(q); s=1 if _area(q)>0 else -1
            inside+= s*Path(q).contains_points(P)
        O[:,:,k]=(inside>0).reshape(X.shape)
    rv=int(round(r/pitch)); g=np.indices((2*rv+1,)*3)-rv; ball=(g**2).sum(0)<=rv*rv
    Od=ndimage.binary_dilation(O,ball)
    lab,_=ndimage.label(~Od); border=set(np.unique(np.r_[lab[0].ravel(),lab[-1].ravel(),lab[:,0].ravel(),lab[:,-1].ravel(),lab[:,:,0].ravel(),lab[:,:,-1].ravel()]))-{0}
    E=np.isin(lab,list(border))
    rv2=int(np.ceil(r*1.45/pitch))+1; g2=np.indices((2*rv2+1,)*3)-rv2; ball2=(g2**2).sum(0)<=rv2*rv2
    Et=ndimage.binary_dilation(E,ball2)   # restaura esquinas exteriores: no redondea, solo rellena cavidades
    C=(~O)&(~Et)
    C=ndimage.binary_opening(C, np.ones((2,2,2)))       # descarta astillas de 1 voxel
    if C.sum()==0: return m, 0.0
    Cd=ndimage.binary_dilation(C, ball[rv-1:rv+2,rv-1:rv+2,rv-1:rv+2]) & ~Et   # solapa paredes
    v,f,_,_=measure.marching_cubes(np.pad(Cd,1).astype(np.float32),0.5)
    v=(v-1)*pitch+lo
    fm=trimesh.Trimesh(v,f[:,::-1]); 
    if fm.volume<0: fm.invert()
    try: F=to_mf(fm)
    except Exception: return m, 0.0
    return m+F, float(C.sum()*pitch**3)
