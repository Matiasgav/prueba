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
def link_mf(n, **kw):
    m=trimesh.load(SRC+n+'.stl'); m.apply_scale(1000)
    out=None
    for b in m.split(only_watertight=False):
        if b.volume/np.prod(b.extents)<kw.get('minfill',0.06) or b.volume<kw.get('minvol',100): continue
        c=b.bounds.mean(0); e=np.maximum(b.extents,1e-6); k=(e+kw.get('grow',1.2))/e
        M=np.eye(4); M[:3,:3]=np.diag(k); M[:3,3]=c-k*c
        x=to_mf(b).transform(M[:3,:4])
        out = x if out is None else out+x
    return out
def from_mf(x):
    me=x.to_mesh(); return trimesh.Trimesh(me.vert_properties[:,:3], me.tri_verts, process=False)
