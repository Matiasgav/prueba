import sys,os,pickle,base64,json; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from build_hw import screw_mesh, nut_mesh, frame
D=pickle.load(open(sys.argv[1],'rb')); RNG=pickle.load(open(sys.argv[2],'rb'))
def enc(m):
    m=trimesh.Trimesh(m.vertices,m.faces,process=True)
    return dict(p=base64.b64encode(np.asarray(m.vertices,np.float32).round(3).astype(np.float32).tobytes()).decode(),
                i=base64.b64encode(np.asarray(m.faces,np.uint32).tobytes()).decode())
parts={n:enc(m) for n,m in D['final'].items()}
joints=[]; hw=[]
P={n:to_mf(m) for n,m in D['final'].items()}
def slot_info(j):
    sd=np.array(j['sd']); O=np.array(j['O']); Mn=frame(sd); Mn[:3,3]=O+(j['nut_s']+0.15)*sd
    a=np.radians(j['slot_ang']); d=np.array([np.cos(a),np.sin(a),0]); big=mf.Manifold.cylinder(4.3,4.2,4.2,24)
    ex=40
    for t in np.arange(0,40,0.5):
        if (big.translate((d*t).tolist()).transform(Mn[:3,:4])^P[j['ns']]).volume()<1e-6: ex=t; break
    return (Mn[:3,:3]@d).tolist(), float(ex)
for j in D['joints']:
    sd=np.array(j['sd']); O=np.array(j['O'])
    hw.append(dict(part=j['hs'], kind='screw', m=enc(screw_mesh(O,sd,j['s_head'],j['L']))))
    wd,ex=slot_info(j)
    hw.append(dict(part=j['ns'], kind='nut', joint=j['n'], dir=wd, depth=ex, m=enc(nut_mesh(O,sd,j['nut_s']+0.15,j['slot_ang']))))
    hw[-2]['joint']=j['n']
    joints.append(dict(n=j['n'],parent=j['parent'],child=j['child'],O=list(map(float,O)),a=list(map(float,j['a'])),
        L=int(j['L']),rs=float(j['rs']),hsp=float(j['hsp']),head=j['hs'],nut=j['ns'],rng=([-360,360] if RNG[j['n']]==[-360,360] else [max(-180,RNG[j['n']][0]),min(180,RNG[j['n']][1])])))
json.dump(dict(parts=parts,joints=joints,hw=hw),open(sys.argv[3],'w'))
print('ok', os.path.getsize(sys.argv[3]))
