import sys,os,pickle; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D=pickle.load(open(sys.argv[1],'rb'))
names=list(D['final']); fig,ax=plt.subplots(len(names),3,figsize=(15,4.2*len(names)))
for r,n in enumerate(names):
    m=D['final'][n]; c=m.bounds.mean(0)
    for k,(nv,lab) in enumerate([([0,1,0],'XZ'),([1,0,0],'YZ'),([0,0,1],'XY')]):
        s=m.section(plane_origin=c,plane_normal=nv); a=ax[r,k]
        if s is not None:
            p,_=s.to_2D(); 
            for poly in p.polygons_full:
                xs,ys=poly.exterior.xy; a.fill(xs,ys,color='#e0a800',ec='k',lw=.5)
                for h in poly.interiors: xs,ys=h.xy; a.fill(xs,ys,color='white',ec='r',lw=.8)
        a.set_aspect('equal'); a.set_title(f'{n} corte {lab}'); a.axis('off')
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=55)
