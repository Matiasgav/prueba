import sys, time, numpy as np
from rod import Rod, best_state, YMAX
x=float(sys.argv[1]); y=float(sys.argv[2]) if len(sys.argv)>2 else YMAX
phi=np.deg2rad(float(sys.argv[3])) if len(sys.argv)>3 else -np.pi/2
rod=Rod((x,y),phi)
prev=None; t=time.time(); out=[]
for L in np.arange(75,30,-2.5):
    if prev is None: b=best_state(rod,L,light=True)
    else:
        b=rod.solve(L, prev['c']*prev['L']/L, prev['target'], rounds=2)
        if not b['ok']: b=best_state(rod,L,prev,light=True)
    if b is not None and b['ok']: prev=b; out.append(f"{L:.1f}:{b['Rmin']:.1f}")
    else: out.append(f"{L:.1f}:X")
print(x, y, round(np.degrees(phi)), ' '.join(out), f"{time.time()-t:.0f}s", flush=True)
