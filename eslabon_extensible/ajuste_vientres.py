"""Busca la profundidad máxima de los vientres de los eslabones largos sin tocar la columna de B
ni comer la barra A más allá del fondo que deja el ojo. Uso: python ajuste_vientres.py"""
import sys, math, numpy as np
sys.path.insert(0,'.')
import eslabon as E
from shapely.geometry import box, LineString
from shapely import affinity
WS=np.linspace(E.W_MIN,E.W_MIN+30,16)
def colocar_en(poly,w,quien,pieza):
    k=E.cinematica(w)
    org=k["Q1"] if quien==1 else k["Q2"]
    g=E.colocar(poly,org,k["ang_largo"]); dx,dy=E.marco(pieza,w)
    return affinity.translate(g,dx,dy)
y0c,y1c=E.canal_carro()
LIM_B=E.C_CARRO+E.HOLG-E.HOLG_PLANO-0.05
LIM_A=E.D_A-E.R_OJO-E.HOLG_PLANO+0.05      # piso que ya deja el ojo en la horquilla de A
def ok1(poly):
    for w in WS:
        g=colocar_en(poly,w,1,"B").intersection(box(-1,y0c,E.BWB+1,y1c))
        if not g.is_empty and g.bounds[2]>LIM_B: return False
    return True
def ok2(poly):
    for w in WS:
        g=colocar_en(poly,w,2,"A").intersection(box(-1,-1,E.BWA+1,191))
        if not g.is_empty and g.bounds[0]<LIM_A: return False
    return True
def prof_en(poly,x):
    seg=LineString([(x,-40),(x,40)]).intersection(poly); return seg.bounds
def z_en_C(poly):
    from shapely.geometry import Point
    p=poly.difference(Point(E.L1,0).buffer(E.D_PERNO/2,32))
    seg=LineString([(E.L1,-40),(E.L1,40)]).intersection(p)
    tr=[(min(s.coords[0][1],s.coords[-1][1]),max(s.coords[0][1],s.coords[-1][1])) for s in getattr(seg,'geoms',[seg])]
    t=7.0; A=sum(b-a for a,b in tr)*t; ec=sum((b-a)*(a+b)/2 for a,b in tr)*t/A
    I=sum(t*((b-a)**3/12+(b-a)*((a+b)/2-ec)**2) for a,b in tr); return I/max(ec-min(a for a,_ in tr),max(b for _,b in tr)-ec)
def gota(Q,Rk,dx,lado):
    if lado<0: circ=[(0,0,E.R_OJO),(E.L1+dx,-(Q-Rk),Rk),(E.L2,0,E.R_OJO)]
    else: circ=[(0,0,E.R_OJO),(E.L2,0,E.R_OJO),(E.L1+dx,Q-Rk,Rk)]
    return E._tramos_a_poligono(E._casco(circ))
def max_Q(Rk,dx,lado,ok):
    lo,hi=E.R_OJO+0.2,20.0
    if not ok(gota(lo,Rk,dx,lado)): return None
    for _ in range(14):
        m=(lo+hi)/2
        try: g=gota(m,Rk,dx,lado); good=ok(g)
        except Exception: good=False
        lo,hi=(m,hi) if good else (lo,m)
    return lo
if __name__=="__main__":
    tri=E._tramos_a_poligono(E._casco([(0,0,E.R_OJO),(E.L1,-(11.6-E.R_OJO),E.R_OJO),(E.L2,0,E.R_OJO)]))
    print("triángulo Q=11.6 ok?",ok1(tri),"Z en C",round(z_en_C(tri)))
    for Rk in (25,40,60,90):
        for dx in (0,-6,-12,-18):
            Q=max_Q(Rk,dx,-1,ok1)
            if Q is None: print(Rk,dx,"no entra"); continue
            g=gota(Q,Rk,dx,-1); print(f"eslabón1 Rk={Rk} dx={dx}: Q={Q:.2f}  Z en C={z_en_C(g):.0f}  área={g.area:.0f}")
    for Rk in (40,90,200):
        Q=max_Q(Rk,0,+1,ok2); print(f"eslabón2 Rk={Rk}: panza máx {Q}")
