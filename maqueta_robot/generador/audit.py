import sys,os,pickle; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from build_hw import screw_mesh, nut_mesh
D=pickle.load(open(sys.argv[1],'rb')); P={n:to_mf(m) for n,m in D['final'].items()}
names=list(P)
print('-- interferencias entre piezas en pose cero (mm3)')
for i,a in enumerate(names):
    for b in names[i+1:]:
        v=(P[a]^P[b]).volume()
        if v>1e-3: print('  CHOQUE',a,b,round(v,3))
print('-- por eje: encastre y tornilleria')
for j in D['joints']:
    sd=np.array(j['sd']); O=np.array(j['O']); hs,ns=j['hs'],j['ns']
    sc=to_mf(screw_mesh(O,sd,j['s_head'],j['L'])); nu=to_mf(nut_mesh(O,sd,j['nut_s']+0.15,j['slot_ang']))
    # saliente: material de la pieza de tuerca dentro de la embocadura
    probe=mf.Manifold.cylinder(j['hsp']-0.05, j['rs']-0.3, j['rs']-0.3, 48)
    from build_hw import place
    probe=place(probe,O,sd,j['ti']-0.2-j['hsp']+0.02)
    eng=(P[ns]^probe).volume()/probe.volume()
    ring=place(mf.Manifold.cylinder(j['hsp'],j['rs']+0.15,j['rs']+0.15,96)-mf.Manifold.cylinder(j['hsp'],j['rs']+0.05,j['rs']+0.05,96),O,sd,j['ti']-0.2-j['hsp'])
    print(f"  {j['n']}: saliente lleno {eng*100:.0f}%  | holgura radial libre: {'OK' if (P[hs]^ring).volume()<1e-3 and (P[ns]^ring).volume()<1e-3 else 'NO'}"
          f" | tornillo toca pieza-cabeza (fuera del avellanado): {round((sc^P[hs]).volume(),3)} mm3 | tornillo vs pieza-tuerca: {round((sc^P[ns]).volume(),3)} | tuerca vs pieza: {round((nu^P[ns]).volume(),3)}")
