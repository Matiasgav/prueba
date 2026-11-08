import sys,os,pickle; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
D=pickle.load(open(sys.argv[1],'rb')); P={n:to_mf(m) for n,m in D['final'].items()}
order=['base','j1','j2','j3','j4','j5','j6']
def rot(m,O,a,deg):
    from scipy.spatial.transform import Rotation as R
    Rm=R.from_rotvec(np.radians(deg)*np.array(a)).as_matrix(); O=np.array(O)
    M=np.eye(4)[:3]; M[:,:3]=Rm; M[:,3]=O-Rm@O
    return m.transform(M)
res={}
for k,j in enumerate(D['joints']):
    mov=None; fix=None
    for i,n in enumerate(order):
        if i>k: mov = P[n] if mov is None else mov+P[n]
        else: fix = P[n] if fix is None else fix+P[n]
    v0=(mov^fix).volume()
    lims=[]
    for sgn in (-1,1):
        last=0
        for d in range(2, 362, 2):
            v=(rot(mov,j['O'],j['a'],sgn*d)^fix).volume()
            if v>0.5: break
            last=d
        lims.append(sgn*last)
    res[j['n']]=lims; print(j['n'],'vol en 0:',round(v0,3),'rango libre (otras en 0):',lims, flush=True)
pickle.dump(res,open(os.path.dirname(sys.argv[1])+'/ranges.pkl','wb'))
