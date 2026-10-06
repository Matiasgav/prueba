"""Rigidez y resistencia al alabeo entre los ejes de acople (fuera del plano).

Modelo de emparrillado: barras A y B, eslabones largos y eslabón corto como vigas en el plano XY,
cargadas fuera del plano. Secciones (inercia fuera del plano y torsión) medidas sobre el CAD.
Los pivotes se toman rígidos fuera del plano: horquilla con pasador ajustado y arandela de precarga.
El carro se toma unido a B (lo guían las alas). B empotrada en sus dos acoples; a A se le aplica:
  Mx  cupla alrededor del ancho (X): una punta de A sube y la otra baja respecto de B.
  My  cupla alrededor del largo (Y): A gira sobre su eje de acople respecto de B.
Torsión por sección: J ≈ A^4 / (40 Ip) (sección maciza; sobrestima un poco en secciones abiertas).
Uso: python torsion.py   -> tabla y salida/torsion.json
"""
import json, math, os, sys
import numpy as np, cadquery as cq
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
import eslabon as E

T_LONCHA = 0.05
Ea, G, Sy = 71700.0, 26900.0, 503.0                    # barras: 7075-T651
E_ESL, G_ESL, SY_ESL = 197000.0, 76000.0, 725.0         # eslabones: 17-4PH (SUS630)


def _sec(sol, y):
    bb = sol.BoundingBox()
    s = sol.intersect(cq.Solid.makeBox(bb.xlen + 2, T_LONCHA, bb.zlen + 2, cq.Vector(bb.xmin - 1, y, bb.zmin - 1)))
    p = GProp_GProps(); BRepGProp.VolumeProperties_s(s.wrapped, p); v = p.Mass()
    if v < 1e-9:
        return None
    m = p.MatrixOfInertia(); ixx, iyy, izz = m.Value(1, 1), m.Value(2, 2), m.Value(3, 3)
    iz2 = (ixx + iyy - izz) / 2 / T_LONCHA; ix2 = (iyy + izz - ixx) / 2 / T_LONCHA; A = v / T_LONCHA
    c = p.CentreOfMass(); sb = s.BoundingBox()
    return dict(A=A, Iout=iz2, Ip=iz2 + ix2, J=A ** 4 / (40 * (iz2 + ix2)), x=c.X(), z=c.Z(),
                cz=max(sb.zmax - c.Z(), c.Z() - sb.zmin))


def medir_secciones():
    res = {}
    for n, f in (("A", E.barra_a), ("B", E.barra_b)):
        sol = f().val()
        largo = E.LARGO_A if n == "A" else E.LARGO
        res[n] = [(float(y), _sec(sol, y)) for y in np.arange(1, largo - 0.9, 1.0)]
    for n, f, L in (("L1", E.eslabon1, E.L2), ("L2", E.eslabon2, E.L2), ("corto", E.eslabon_corto, E.L1)):
        sol = f().val().rotate((0, 0, 0), (0, 0, 1), 90)
        res[n] = [(float(x), _sec(sol, x)) for x in np.arange(0.5, L - 0.49, 0.5)]
    return res


def props(tab, s):
    best=None
    for x,d in tab:
        if d and (best is None or abs(x-s)<abs(best[0]-s)): best=(x,d)
    return best[1]
class Emp:
    def __init__(s): s.n=[]; s.el=[]
    def nodo(s,p): s.n.append(np.array(p,float)); return len(s.n)-1
    def viga(s,i,j,EI,GJ,info=None): s.el.append((i,j,EI,GJ,info))
    def K(s):
        N=len(s.n); K=np.zeros((3*N,3*N))
        for i,j,EI,GJ,_ in s.el:
            d=s.n[j]-s.n[i]; L=np.linalg.norm(d); c,sn=d/L
            # local: w, rot about local x (torsion), rot about local y (flexión)
            k=np.zeros((6,6))
            a=12*EI/L**3; b=6*EI/L**2; e=4*EI/L; f=2*EI/L; t=GJ/L
            # dof order local: w1, tx1, ty1, w2, tx2, ty2 ; flexión con ty (w' = -ty convención)
            k[np.ix_([0,2,3,5],[0,2,3,5])]=np.array([[a,-b,-a,-b],[-b,e,b,f],[-a,b,a,b],[-b,f,b,e]])
            k[1,1]=k[4,4]=t; k[1,4]=k[4,1]=-t
            T=np.zeros((6,6))
            for o in (0,3):
                T[o,o]=1; T[o+1:o+3,o+1:o+3]=[[c,sn],[-sn,c]]
            kg=T.T@k@T
            idx=[3*i,3*i+1,3*i+2,3*j,3*j+1,3*j+2]
            K[np.ix_(idx,idx)]+=kg
        return K
    def fuerzas_elem(s,u):
        out=[]
        for i,j,EI,GJ,info in s.el:
            d=s.n[j]-s.n[i]; L=np.linalg.norm(d); c,sn=d/L
            T=np.zeros((6,6))
            for o in (0,3):
                T[o,o]=1; T[o+1:o+3,o+1:o+3]=[[c,sn],[-sn,c]]
            ul=T@np.r_[u[3*i:3*i+3],u[3*j:3*j+3]]
            a=12*EI/L**3; b=6*EI/L**2; e=4*EI/L; f=2*EI/L
            kb=np.array([[a,-b,-a,-b],[-b,e,b,f],[-a,b,a,b],[-b,f,b,e]])
            fb=kb@ul[[0,2,3,5]]
            Tq=GJ/L*(ul[4]-ul[1])
            out.append((info, abs(fb[1]), abs(fb[3]), abs(Tq)))
        return out
RIG=1e12
def armar(w, seg=4.0):
    k=E.cinematica(w); m=Emp(); xb=k["xb"]
    xA=E.D_A; xBc=xb+12.39
    def barra(tab, x, ys_extra, nombre, largo=E.LARGO):
        ys=sorted(set([y for y in np.arange(0,largo+0.01,seg)]+[largo]+ys_extra))
        ids={}
        prev=None
        for y in ys:
            n=m.nodo((x,y)); ids[round(y,4)]=n
            if prev is not None:
                d=props(tab,(y+prev[0])/2); m.viga(prev[1],n,Ea*d["Iout"],G*d["J"],(nombre,(y+prev[0])/2,d))
            prev=(y,n)
        return ids
    yQ1,yQ2=E.Y0,E.Y0+E.DP; yP1=k["P1"][1]; yP2=k["P2"][1]
    yA=E.LARGO_A-5.0
    A=barra(S["A"],xA,[yQ1,yQ2,5.0,yA],"barra A",E.LARGO_A)
    B=barra(S["B"],xBc,[E.Y0,yP1,yP2,5.0,185.0],"barra B")
    def brazo(n_bar, p):
        q=m.nodo(p); m.viga(n_bar,q,RIG,RIG,None); return q
    acA=[brazo(A[5.0],(E.X_ACOPLE,5.0)),brazo(A[round(yA,4)],(E.X_ACOPLE,yA))]
    acB=[brazo(B[5.0],(xb+E.BWB-E.X_ACOPLE,5.0)),brazo(B[185.0],(xb+E.BWB-E.X_ACOPLE,185.0))]
    O=brazo(B[E.Y0],tuple(k["O"])); P1=brazo(B[round(yP1,4)],tuple(k["P1"])); P2=brazo(B[round(yP2,4)],tuple(k["P2"]))
    def eslabon(tab, ni, nj, nombre, nm=40, nodo_medio=False):
        pi,pj=m.n[ni],m.n[nj]; L=np.linalg.norm(pj-pi); prev=ni; mid=None
        for t in range(1,nm+1):
            n = nj if t==nm else m.nodo(pi+(pj-pi)*t/nm)
            s_=L*(t-0.5)/nm; d=props(tab,s_)
            m.viga(prev,n,E_ESL*d["Iout"],G_ESL*d["J"],(nombre,s_,d)); prev=n
            if t==nm//2: mid=n
        return mid
    C=eslabon(S["L1"],A[yQ1],P1,"eslabón 1")
    eslabon(S["L2"],A[yQ2],P2,"eslabón 2")
    eslabon(S["corto"],O,C,"eslabón corto",nm=20)
    return m,acA,acB
def resolver(w, caso):
    m,acA,acB=armar(w)
    K=m.K(); N=len(m.n); F=np.zeros(3*N)
    if caso=="Mx":      # 1 N·m alrededor de X: fuerzas en z en los acoples de A
        brazoA=E.LARGO_A-10.0; f=1000.0/brazoA; F[3*acA[1]]+=f; F[3*acA[0]]-=f
    else:               # 1 N·m alrededor de Y en el eje de acople de A
        F[3*acA[0]+2]+=500.0; F[3*acA[1]+2]+=500.0
    fijos=[3*n+d for n in acB for d in range(3)]
    libres=[i for i in range(3*N) if i not in fijos]
    u=np.zeros(3*N); u[libres]=np.linalg.solve(K[np.ix_(libres,libres)],F[libres])
    if caso=="Mx": giro=(u[3*acA[1]]-u[3*acA[0]])/(E.LARGO_A-10.0)
    else: giro=(u[3*acA[0]+2]+u[3*acA[1]+2])/2
    peor={}
    for info,M1,M2,T in m.fuerzas_elem(u):
        if info is None: continue
        nombre,s_,d=info
        if "eslabón" in nombre:
            # los cortes que pasan por el agujero del pasador no cuentan: ahí el momento lo toma el pasador
            L = E.L1 if nombre == "eslabón corto" else E.L2
            huecos = [0.0, L] + ([E.L1] if nombre == "eslabón 1" else [])
            if min(abs(s_ - h) for h in huecos) < E.R_OJO:
                continue
        sig=max(M1,M2)*d["cz"]/d["Iout"]
        tmin=(E.T_CORTO if nombre=="eslabón corto" else 7.0) if "eslabón" in nombre else 13.0
        tau=T*tmin/d["J"]
        vm=math.sqrt(sig**2+3*tau**2)
        if vm>peor.get(nombre,(0,))[0]: peor[nombre]=(vm,s_,max(M1,M2),T)
    return giro,peor,u,acA
S = None

if __name__ == "__main__":
  S = medir_secciones()
  filas = []
  for caso in ("Mx","My"):
    for w in (35,50,70,90,105):
        giro,peor,u,acA=resolver(w,caso)
        caps={n:(SY_ESL if "eslabón" in n else Sy)/v[0] for n,v in peor.items()}
        lim=min(caps,key=caps.get); grados=math.degrees(giro)
        filas.append(dict(caso=caso,W=w,grados_por_Nm=grados,rigidez_Nm_por_grado=1/grados,capacidad_Nm=caps[lim],limita=lim,caps=caps))
        print(f"{caso} W={w}: {grados:.4f} °/N·m  rigidez {1/grados:.1f} N·m/°  capacidad {caps[lim]:.1f} N·m ({lim})")
  with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida", "torsion.json"), "w") as fh:
      json.dump(filas, fh, indent=1, ensure_ascii=False)
