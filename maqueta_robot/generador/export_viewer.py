import sys,os,pickle,base64,json; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from load import *
from build_hw import screw_mesh, nut_mesh
D=pickle.load(open(sys.argv[1],'rb')); RNG=pickle.load(open(sys.argv[2],'rb'))
def enc(m):
    m=trimesh.Trimesh(m.vertices,m.faces,process=True)
    return dict(p=base64.b64encode(np.asarray(m.vertices,np.float32).round(3).astype(np.float32).tobytes()).decode(),
                i=base64.b64encode(np.asarray(m.faces,np.uint32).tobytes()).decode())
parts={n:enc(m) for n,m in D['final'].items()}
joints=[]; hw=[]
for j in D['joints']:
    sd=np.array(j['sd']); O=np.array(j['O'])
    hw.append(dict(part=j['hs'], kind='screw', m=enc(screw_mesh(O,sd,j['s_head'],j['L']))))
    hw.append(dict(part=j['ns'], kind='nut',   m=enc(nut_mesh(O,sd,j['nut_s']+0.15,j['slot_ang']))))
    joints.append(dict(n=j['n'],parent=j['parent'],child=j['child'],O=list(map(float,O)),a=list(map(float,j['a'])),
        L=int(j['L']),rs=float(j['rs']),hsp=float(j['hsp']),head=j['hs'],nut=j['ns'],rng=([-360,360] if RNG[j['n']]==[-360,360] else [max(-180,RNG[j['n']][0]),min(180,RNG[j['n']][1])])))
json.dump(dict(parts=parts,joints=joints,hw=hw),open(sys.argv[3],'w'))
print('ok', os.path.getsize(sys.argv[3]))
