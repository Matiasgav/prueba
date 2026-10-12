"""Prototipo impreso de la corredera del captor ELCID.
Parte del STEP original (Solid Edge) y genera chasis, tapa y bastidor de bobina
listos para imprimir, más la trayectoria del cable de 1 mm."""
import math, json, sys
import cadquery as cq
from common import loadb

# ---------------- parámetros ----------------
PILOT_M3   = 2.5    # agujero piloto para roscar M3 directo en plástico
CLEAR_M3   = 3.2    # paso libre M3 (ranura del chasis)
CLR_SLIDE  = 0.30   # holgura de deslizamiento bobina / chasis-tapa
CLR_FIX    = 0.15   # holgura lateral entre encastres fijos chasis / tapa
CABLE_D    = 1.0
CABLE_CUT  = 0.70   # radio del canal para el cable dentro del bastidor (Ø1.4)
S0         = -11.7  # posición X del tornillo de la bobina en el STEP
L_FREE     = 28.0   # largo libre de cable entre bobina y punto fijo (ver informe)

chasis0 = loadb("p0.brep"); tapa = loadb("p1.brep"); caja0 = loadb("p2.brep")
box = lambda x0,x1,y0,y1,z0,z1: cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
cyl = lambda r,x,y,z0,z1: cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0))

# ---------------- canal de salida del cable (copia la ranura de la tapa) ----------------
ZG0, ZG1 = 9.5, 11.6
groove = (box(-1.25,18.75,-2.5,0.5,ZG0,ZG1)
          .fuse(cyl(1.5,18.75,-1,ZG0,ZG1))
          .fuse(cyl(6,-1.25,3.5,ZG0,ZG1).cut(cyl(3,-1.25,3.5,ZG0-1,ZG1+1)).intersect(box(-7.25,-1.25,-2.5,3.5,ZG0,ZG1)))
          .fuse(box(-7.25,-4.25,3.5,9,ZG0,ZG1)))

# ---------------- chasis ----------------
ch = chasis0.cut(tapa)                                   # el chasis simplificado invadía la tapa (391 mm³)
for dx,dy in ((CLR_FIX,0),(-CLR_FIX,0),(0,CLR_FIX),(0,-CLR_FIX)):
    ch = ch.cut(tapa.translate(cq.Vector(dx,dy,0)))      # holgura lateral en los escalones
ch = ch.cut(groove)                                      # canal de salida del cable libre
slot = box(-17.25,12.75,-4-CLEAR_M3/2,-4+CLEAR_M3/2,-1,3.5).fuse(cyl(CLEAR_M3/2,-17.25,-4,-1,3.5)).fuse(cyl(CLEAR_M3/2,12.75,-4,-1,3.5))
ch = ch.cut(slot)                                        # ranura 2.5 -> 3.2 para que pase el M3
for (x,y) in ((17.25,4),(-16.25,4)):
    ch = ch.cut(cyl(3.6,x,y,9.5,20))                     # el chasis no entra en el avellanado de la tapa
    ch = ch.cut(cyl(PILOT_M3/2,x,y,-1,20))               # pasantes para roscar los M3 de la tapa
chasis = ch.clean()

# ---------------- trayectoria del cable ----------------
YC, ZL, ZU = -0.8, 3.55, 11.0
R  = (ZU-ZL)/2
XF = -1.25            # el cable deja de moverse aquí (empieza la curva hacia la salida)
RP = 3.5-YC           # radio en planta de la curva de salida
def attached_pts(s):
    """tramo pegado a la bobina: agujero diagonal + vuelta al buje + muesca"""
    dx = s-S0; pts=[]
    t0,t1 = 31.06,34.8
    for t in (t0,t1): pts.append((2.39-0.5*t+dx, -35.90+0.866*t, ZL))
    a0 = math.atan2(-5.76+4, -15.01+11.7); a1 = math.pi/2
    if a0 < 0: a0 += 2*math.pi
    r0 = math.hypot(-15.01+11.7,-5.76+4); r1 = -4-YC; r1=abs(r1)
    n=24
    for i in range(1,n+1):
        u=i/n; a=a0+(a1-a0)*u; r=r0+(r1-r0)*u
        pts.append((-11.7+dx+r*math.cos(a), -4+r*math.sin(a), ZL))
    pts.append((-4.2+dx, YC, ZL))
    return pts
def cable_pts(s, L=L_FREE, n=24):
    pts = attached_pts(s)
    xs = s-S0-4.2
    xb = (L-math.pi*R+xs+XF)/2
    if xb > xs: pts.append((xb,YC,ZL))
    for i in range(1,n):
        a=-math.pi/2+math.pi*i/n; pts.append((xb+R*math.cos(a),YC,ZL+R+R*math.sin(a)))
    pts.append((xb,YC,ZU)); pts.append((XF,YC,ZU))
    for i in range(1,n+1):
        a=-math.pi/2-(math.pi/2)*i/n; pts.append((XF+RP*math.cos(a),3.5+RP*math.sin(a),ZU))
    pts.append((XF-RP,9.0,ZU))
    return pts, xb
def plen(p): return sum(math.dist(a,b) for a,b in zip(p[:-1],p[1:]))

def tube(pts, r):
    # tubo como unión de cilindros + esferas (robusto para chequear interferencias)
    sol=None
    for a,b in zip(pts[:-1],pts[1:]):
        va,vb=cq.Vector(*a),cq.Vector(*b); d=vb-va
        if d.Length<1e-6: continue
        c=cq.Solid.makeCylinder(r,d.Length,va,d)
        sol=c if sol is None else sol.fuse(c)
    for p in pts[1:-1]: sol=sol.fuse(cq.Solid.makeSphere(r,cq.Vector(*p),angleDegrees1=-90,angleDegrees2=90))
    return sol.clean()

# ---------------- bastidor de bobina ----------------
cj = caja0.fuse(cyl(3.0,-11.7,-4,3.0,9.0))                 # rellena el alojamiento del inserto
cj = cj.cut(box(-30,10,-8-CLR_SLIDE,1,9.0-CLR_SLIDE,20))   # techo: holgura con el labio de la tapa
cj = cj.cut(box(-30,10,-8-CLR_SLIDE,1,-1,3.0))             # frente inferior: holgura con el chasis
cj = cj.cut(box(-30,10,-CLR_SLIDE,1,-1,20))                # atrás: holgura con la pared del chasis
cj = cj.cut(cyl(PILOT_M3/2,-11.7,-4,-1,20))                # piloto M3 pasante (rosca directa)
cj = cj.cut(tube(attached_pts(S0)+[(0.5,YC,ZL)], CABLE_CUT))  # canal Ø1.4 para pegar el cable
caja = cj.clean()

if __name__ == "__main__":
    from OCP.BRepTools import BRepTools
    for n,s in (("chasis",chasis),("tapa",tapa),("bobina",caja)):
        BRepTools.Write_s(s.wrapped, f"new_{n}.brep")
        print(n, "vol=%.1f"%s.Volume(), "válido", s.isValid())
    info={}
    p,_=cable_pts(S0); fixed_len = plen(attached_pts(S0))
    exit_len = math.pi/2*RP + (9.0-3.5) - 1.0
    info.update(R=R, L_free=L_FREE, attached=fixed_len, exit=exit_len, XF=XF, YC=YC, ZL=ZL, ZU=ZU, RP=RP, S0=S0)
    json.dump(info, open("cable_info.json","w"), indent=1); print(info)
