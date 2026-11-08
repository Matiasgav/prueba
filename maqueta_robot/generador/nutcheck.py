import sys,os,pickle; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from build_hw import frame
D=pickle.load(open(sys.argv[1],'rb')); P={n:to_mf(m) for n,m in D['final'].items()}
order=['base','j1','j2','j3','j4','j5','j6']
NAF=5.5; NH=4.0   # tuerca DIN 985 M3 real: 5,5 entre caras, 4 mm alto
for j in D['joints']:
    sd=np.array(j['sd']); O=np.array(j['O']); ns=j['ns']
    Mn=frame(sd); Mn[:3,3]=O+(j['nut_s']+0.15)*sd
    rc=NAF/np.sqrt(3)
    nut=mf.Manifold.cylinder(NH,rc,rc,6).rotate([0,0,j['slot_ang']])
    d=np.array([np.cos(np.radians(j['slot_ang'])),np.sin(np.radians(j['slot_ang'])),0])
    worst=0; exit_at=None; prof=[]
    for t in np.arange(0,40.01,0.25):
        x=nut.translate((d*t).tolist()).transform(Mn[:3,:4])
        v=(x^P[ns]).volume(); worst=max(worst,v); prof.append(v)
        if exit_at is None and (x^P[ns].hull()).volume()<1e-6: exit_at=t
    # punto de salida y quien lo tapa al armar
    xe=nut.translate((d*(exit_at or 40)).tolist()).transform(Mn[:3,:4])
    lane=None
    for t in np.arange(0,(exit_at or 40)+0.01,0.5):
        x=nut.translate((d*t).tolist()).transform(Mn[:3,:4]); lane = x if lane is None else lane+x
    blockers=[n for n in order if n!=ns and (lane^P[n]).volume()>0.01]
    wd=(Mn[:3,:3]@d).round(2)
    print(f"{j['n']}: tuerca en {ns:4s} | roce max al deslizar {worst:.3f} mm3 | sale tras {exit_at} mm hacia {wd.tolist()} | piezas que tapan la ranura armado: {blockers or 'ninguna'}")
