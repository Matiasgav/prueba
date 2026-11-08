import sys,os,pickle; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from build_hw import frame
D=pickle.load(open(sys.argv[1],'rb')); P={n:to_mf(m) for n,m in D['final'].items()}
order=['base','j1','j2','j3','j4','j5','j6']
for j in D['joints']:
    sd=np.array(j['sd']); O=np.array(j['O']); ns=j['ns']
    Mn=frame(sd); Mn[:3,3]=O+(j['nut_s']+0.15)*sd
    big=mf.Manifold.cylinder(4.3,4.2,4.2,24)    # tuerca + 1 mm de margen
    res=[]
    for ang in range(0,360,30):
        d=np.array([np.cos(np.radians(ang)),np.sin(np.radians(ang)),0])
        ex=None
        for t in np.arange(0,40,0.5):
            if (big.translate((d*t).tolist()).transform(Mn[:3,:4])^P[ns]).volume()<1e-6: ex=t; break
        wd=(Mn[:3,:3]@d)
        others=[n for n in order if n!=ns]
        lane=mf.Manifold.cube([ex or 40,5.5,4]).translate([0,-2.75,0]).rotate([0,0,ang]).transform(Mn[:3,:4])
        blk=[n for n in others if (lane^P[n]).volume()>0.01]
        res.append((ex if ex is not None else 99, ang, wd.round(2).tolist(), blk))
    res.sort()
    print(j['n'], ns, 'actual: ang', round(j['slot_ang']), '| mejores:', [(r[0],r[1],r[2],r[3]) for r in res[:4]])
