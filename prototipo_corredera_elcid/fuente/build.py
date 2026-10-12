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
S0         = -11.7  # posición X del tornillo de la bobina en el STEP
L_FREE     = 27.0   # largo libre de cable entre bobina y punto fijo (ver informe)

chasis0 = loadb("p0.brep"); tapa = loadb("p1.brep"); caja0 = loadb("p2.brep")
box = lambda x0,x1,y0,y1,z0,z1: cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
cyl = lambda r,x,y,z0,z1: cq.Solid.makeCylinder(r,z1-z0,cq.Vector(x,y,z0))

# ---------------- chasis ----------------
ch = chasis0.cut(tapa)                                   # el chasis simplificado invadía la tapa (391 mm³)
for dx,dy in ((-CLR_FIX,0),(0,-CLR_FIX)):
    ch = ch.cut(tapa.translate(cq.Vector(dx,dy,0)))      # holgura de armado; no toca las caras de la salida 1x1
slot = box(-17.25,12.75,-4-CLEAR_M3/2,-4+CLEAR_M3/2,-1,3.5).fuse(cyl(CLEAR_M3/2,-17.25,-4,-1,3.5)).fuse(cyl(CLEAR_M3/2,12.75,-4,-1,3.5))
ch = ch.cut(slot)                                        # ranura 2.5 -> 3.2 para que pase el M3
for (x,y) in ((17.25,4),(-16.25,4)):
    ch = ch.cut(cyl(3.6,x,y,9.5,20))                     # el chasis no entra en el avellanado de la tapa
    ch = ch.cut(cyl(PILOT_M3/2,x,y,-1,20))               # pasantes para roscar los M3 de la tapa
chasis = ch.clean()

# ---------------- trayectoria del cable ----------------
YC, ZL, ZU = -0.5, 3.5, 11.0     # cable apoyado en piso y pared, como en el STEP
R  = (ZU-ZL)/2
XF = -1.25            # el cable deja de moverse aquí (empieza la curva hacia la salida)
CP = (-1.25, 3.5)     # centro de la ranura curva de la tapa (R3..R6)
RP0, RP1 = 3.5-YC, 5.5   # radio de la curva del cable: de la ranura (y=-0.5) a la salida 1x1 (x=-6.75)
WALL_EFF = 18.4       # la pared del extremo tiene un radio interior R1.5: a la altura del cable está en x≈18.4
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
        u=i/n; a=-math.pi/2-(math.pi/2)*u; r=RP1-(RP1-RP0)*(1-u)**2
        pts.append((CP[0]+r*math.cos(a),CP[1]+r*math.sin(a),ZU))
    pts.append((CP[0]-RP1,9.0,ZU))
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
cj = cj.fuse(cyl(2.75,-11.7,-4,9.0-CLR_SLIDE,9.58))         # falange del inserto en plástico: guía y tope en el bolsillo de la tapa
cj = cj.cut(cyl(PILOT_M3/2,-11.7,-4,-1,20))                # piloto M3 pasante (rosca directa)
caja = cj.clean()

if __name__ == "__main__":
    from OCP.BRepTools import BRepTools
    for n,s in (("chasis",chasis),("tapa",tapa),("bobina",caja)):
        BRepTools.Write_s(s.wrapped, f"new_{n}.brep")
        print(n, "vol=%.1f"%s.Volume(), "válido", s.isValid())
    info={}
    p,_=cable_pts(S0); fixed_len = plen(attached_pts(S0))
    exit_len = plen(cable_pts(S0)[0][-(n_exit:=26):-1]) + (8.0-CP[1])
    info.update(R=R, L_free=L_FREE, attached=fixed_len, exit=exit_len, XF=XF, YC=YC, ZL=ZL, ZU=ZU, S0=S0, WALL_EFF=WALL_EFF)
    json.dump(info, open("cable_info.json","w"), indent=1); print(info)
