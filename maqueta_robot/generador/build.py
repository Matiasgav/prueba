import sys, json, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
from scipy.spatial.transform import Rotation as Rot
S = 1/6.0            # escala maqueta
G = 0.4              # holgura axial entre eslabones (mm, escala maqueta)
OUT = sys.argv[1] if len(sys.argv)>1 else 'out'
os.makedirs(OUT, exist_ok=True)

def T(t): M=np.eye(4); M[:3,3]=t; return M
def R(axis,deg): M=np.eye(4); M[:3,:3]=Rot.from_rotvec(np.radians(deg)*np.array(axis,float)).as_matrix(); return M
# DH -> pose cero (mm, escala real). FANUC: brazo vertical, antebrazo horizontal
d1,a1,a2,a3,d4,d6 = 450,75,640,195,700,75
POSE = {'base':T([0,0,0]), 'j1':T([0,0,d1]), 'j2':T([a1,0,d1]), 'j3':T([a1,0,d1+a2]),
        'j4':T([a1,0,d1+a2+a3]), 'j5':T([a1+d4,0,d1+a2+a3]), 'j6':T([a1+d4,0,d1+a2+a3])}
POSE['tool'] = POSE['j6'] @ T([d6+4,0,0]) @ R([0,1,0],90)

def xf(m, M): return m.transform(M[:3,:4].astype(np.float64))
SC = np.diag([S,S,S,1.0])
parts = {}
for n in ['base','j1','j2','j3','j4','j5','j6']:
    parts[n] = xf(link_mf(n), SC @ POSE[n])
# herramienta: placa + cabezal laser (hull por cuerpo -> solido imprimible)
tm = trimesh.load(SRC+'RayTools_BT220.stl'); tool=None
for b in tm.split(only_watertight=False):
    if len(b.vertices)<4 or b.extents.min()<0.5: continue
    try: h=to_mf(b.convex_hull)
    except Exception: continue
    tool = h if tool is None else tool+h
# cabezal a 90 grados (como Fig. 6): planchuela atornillada a la brida J6 y brida lateral del
# cabezal (cara x=-40.7, z 165..225, y -35.7..44.3) apoyada sobre la planchuela; boquilla hacia abajo
plate = xf(to_mf(trimesh.load(SRC+'planchuela_BT220.stl')), SC @ POSE['tool'])
HEAD90 = np.array([[1,0,0,d6+15+40.7-0.3],[0,-1,0,4.3],[0,0,-1,195],[0,0,0,1]],float)
tool = xf(tool, SC @ POSE['j6'] @ HEAD90) + plate
parts['j6'] = parts['j6'] + tool

# ---------- primitivas ----------
def frame(a):
    a=np.array(a,float); a/=np.linalg.norm(a)
    ref=np.array([0,0,1.]) if abs(a[2])<0.9 else np.array([1.,0,0])
    u=np.cross(a,ref); u/=np.linalg.norm(u); v=np.cross(a,u)
    M=np.eye(4); M[:3,0]=u; M[:3,1]=v; M[:3,2]=a; return M
def place(m, O, a, t): # m modelado a lo largo de +Z local; t = posicion axial
    return xf(m, T(np.array(O)+t*np.array(a)) @ frame(a))
def cyl(r, h, r2=None, seg=48): return mf.Manifold.cylinder(h, r, r if r2 is None else r2, seg)
def hexprism(af, h):  # af = entre caras
    rc = af/np.sqrt(3); return mf.Manifold.cylinder(h, rc, rc, 6)

# ---------- definicion de articulaciones (escala real -> se escala abajo) ----------
# O: punto del eje (mm reales), a: eje (padre -> hijo), t0: plano de interfaz (mm reales)
# Rc: radio de despeje (mm maqueta), head: lado de la cabeza avellanada, slot: direccion de la ranura de tuerca
JOINTS = [
 dict(n='J1', rs=8.0, hs=3.0, parent='base', child='j1', O=[0,0,0],        a=[0,0,1],  t0=303.5, Rc=175/6+0.5, head='parent', slot=[-1,0,0], rb=5.5, lim=(-170,170)),
 dict(n='J2', rs=6.0, hs=3.0, parent='j1',   child='j2', O=[a1,0,d1],      a=[0,-1,0], t0=80,    Rc=105/6+0.5, head='child',  slot=[0,0,-1], rb=5.5, lim=(-100,160)),
 dict(n='J3', rs=6.0, hs=3.0, parent='j2',   child='j3', O=[a1,0,d1+a2],   a=[0,1,0],  t0=-65,   Rc=92/6+0.5,  head='parent', slot=[0,0,-1], rb=5.5, lim=(-70,250)),
 dict(n='J4', rs=6.0, hs=3.0, parent='j3',   child='j4', O=[a1,0,d1+a2+a3],a=[1,0,0],  t0=a1+261,Rc=80/6+0.5,  head='parent', slot=[0,0,-1], rb=6.0, lim=(-190,190), dh=(261-114)/6),
 dict(n='J5', rs=5.0, hs=2.5, parent='j4',   child='j5', O=[a1+d4,0,d1+a2+a3],a=[0,1,0],t0=-52,  Rc=56/6+0.5,  head='parent', slot=[0,0,-1], rb=5.0, lim=(-140,140)),
 dict(n='J6', rs=4.0, hs=2.5, parent='j5',   child='j6', O=[a1+d4,0,d1+a2+a3],a=[1,0,0],t0=a1+d4+60,Rc=35.5/6+0.45,head='parent',slot=[0,0,-1], rb=4.6, lim=(-360,360), dh=(60+52)/6),
]
for j in JOINTS:
    j['O']=np.array(j['O'],float)*S; j['a']=np.array(j['a'],float); j['t0']*=S
    if j['n'] in ('J4','J6'): j['t0'] -= np.dot(j['O'], j['a'])  # t0 dado en x absoluto
LENGTHS=[8,10,12,16,20,25,30]
HOLE=3.4; HOLE_FREE=4.0; RAD=0.2; BOT=0.3; CSK_D=6.7; CBORE=7.0; NUT_AF=5.75; NUT_H=4.3; WALL=1.2

# hull de cada pieza para recortar bujes
hulls = {n: parts[n].hull() for n in parts}
mesh_cache = {n: from_mf(parts[n]) for n in parts}
def last_hit(n, p, d, maxd=60):
    m=mesh_cache[n]; locs,_,_ = m.ray.intersects_location([p],[d])
    if len(locs)==0: return 0.0
    t=(locs-p)@d; t=t[(t>0)&(t<maxd)]
    return float(t.max()) if len(t) else 0.0

pre = {n:[] for n in parts}; add = {n:[] for n in parts}; sub = {n:[] for n in parts}; hw=[]
for j in JOINTS:
    O,a,t0=j['O'],j['a'],j['t0']; P,C=j['parent'],j['child']; g=G/2
    # 1) despeje: planos paralelos con holgura G
    pre[P].append(place(cyl(j['Rc'],80),O,a,t0-g))
    pre[C].append(place(cyl(j['Rc'],80),O,a,t0+g-80))
    # 2) tornillo: direccion desde la cabeza hacia la punta
    hs, ns = (P,C) if j['head']=='parent' else (C,P)
    sd = a if j['head']=='parent' else -a          # direccion del tornillo
    ti = t0*np.dot(a,sd)                            # coordenada de interfaz sobre sd
    Osd = O
    # profundidad disponible del lado de la cabeza (hasta superficie exterior)
    pI = O + t0*a
    dh = j.get('dh') or last_hit(hs, pI - sd*g, -sd)
    dh = max(dh, 5.0)
    # tuerca del otro lado
    s_nut0 = ti + g + WALL; s_nut1 = s_nut0 + NUT_H; s_tip = s_nut1 + 0.8
    rs, hsp = j['rs'], j['hs']
    s_sock = ti - g - hsp - BOT                       # fondo de la embocadura (lado cabeza)
    csk_h=(CSK_D-HOLE_FREE)/2
    s_head_max = s_sock - csk_h - 1.0                 # >=1 mm de pared entre avellanado y embocadura
    cand=[l for l in LENGTHS if l<=30 and s_tip-l >= ti-dh and s_tip-l <= s_head_max]
    if not cand: raise SystemExit(f"{j['n']}: no entra un tornillo estandar (dh={dh:.1f})")
    L=max(cand); s_head=s_tip-L
    j.update(L=L, s_head=float(s_head), s_tip=float(s_tip), sd=sd.tolist(), cbore=float(s_head-(ti-dh)), hs_=hs, hs=hs, ns=ns,
             s_sock=float(s_sock), rs=rs, hsp=hsp, ti=float(ti))
    # bujes (material garantizado, recortado al hull de la pieza)
    rbh = max(j['rb'], rs+RAD+1.6); rbn = max(j['rb'], rs+1.2)
    add[hs].append(place(cyl(rbh, (ti-g)-(s_head-1.0)), Osd, sd, s_head-1.0) ^ hulls[hs])
    add[ns].append(place(cyl(rbn, (s_nut1+1.5)-(ti+g)), Osd, sd, ti+g) ^ hulls[ns])
    # ENCASTRE: saliente cilindrico en la pieza de la tuerca, embocadura en la pieza de la cabeza
    add[ns].append(place(cyl(rs, hsp+2*g+0.3, seg=96), Osd, sd, ti-g-hsp))
    sub[hs].append(place(cyl(rs+RAD, hsp+BOT+g+0.01, seg=96), Osd, sd, s_sock))
    # tornillo: holgado en la pieza que gira (4.0) -> solo trabaja axial; 3.4 en saliente/pieza de tuerca
    sub[hs].append(place(cyl(HOLE_FREE/2, s_sock+0.1-(s_head-0.1)), Osd, sd, s_head-0.1))
    sub[ns].append(place(cyl(HOLE/2, s_tip+3-(ti-g-hsp-0.1)), Osd, sd, ti-g-hsp-0.1))
    sub[hs].append(place(cyl(CSK_D/2, csk_h, HOLE_FREE/2), Osd, sd, s_head))
    sub[hs].append(place(cyl(CBORE/2, 60), Osd, sd, s_head-60+0.01))
    # alojamiento de tuerca hex + ranura de insercion lateral
    sl=np.array(j['slot'],float); sl-=np.dot(sl,sd)*sd; sl/=np.linalg.norm(sl)
    Mn = T(Osd + s_nut0*sd) @ frame(sd)
    # orientar hex: caras paralelas a la ranura
    lx = np.linalg.inv(Mn[:3,:3]) @ sl; ang=np.degrees(np.arctan2(lx[1],lx[0]))
    hx = xf(hexprism(NUT_AF, NUT_H).rotate([0,0,ang]), Mn)  # vértice hacia la ranura -> rotar 30
    slot = mf.Manifold.cube([40, NUT_AF, NUT_H]).translate([0,-NUT_AF/2,0]).rotate([0,0,ang])
    sub[ns].append(hx); sub[ns].append(xf(slot, Mn))
    j['nut_s']=float(s_nut0); j['slot_ang']=float(ang)

final={}
for n in parts:
    m=parts[n]
    for c in pre[n]: m=m-c
    for b in add[n]: m=m+b
    for s in sub[n]: m=m-s
    comps=sorted(m.decompose(), key=lambda c:-c.volume())
    m=comps[0]
    for c in comps[1:]:
        if c.volume()<0: m=m+c.hull()^m.hull() if False else m   # vacio interno -> se rellena (se descarta la cascara)
    voids=[c for c in comps if c.volume()<0]
    if voids: m=mf.Manifold.compose([comps[0]])
    assert all(c.volume()<150 for c in comps[1:]), (n,'pieza suelta grande',[c.volume() for c in comps[1:]])
    final[n]=m
    print('   descartados', n, [(round(c.volume(),1), np.round(np.array(c.bounding_box()).reshape(2,3) if False else from_mf(c).bounds,1).tolist()) for c in comps[1:]])
    print(n, 'vol %.0f'%m.volume(), 'tris', m.num_tri(), 'genus', m.genus(), 'componentes', [round(c.volume(),1) for c in m.decompose()])
for j in JOINTS:
    print(j['n'], 'saliente D%.1f x %.1f'%(2*j['rs'],j['hsp']), 'M3x%d'%j['L'], 'cabeza en', j['hs'], 'tuerca en', j['ns'], 'contrataladro %.1f mm'%j['cbore'])
import pickle
pickle.dump(dict(final={n:from_mf(final[n]) for n in final}, joints=[{k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in j.items()} for j in JOINTS]), open(OUT+'/build.pkl','wb'))
