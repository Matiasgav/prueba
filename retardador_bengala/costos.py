# Modelo de costos del retardador (README §26). Precios LCSC (API) y JLCPCB (página oficial) al 06/11/2026.
# Uso: python3 costos.py
import math
# (ref, cant, {tramo: precio})  precios USD de LCSC por tramo
BOM=[("U1 STM32L010F4P6 C529415",1,{100:0.7867,500:0.726,1000:0.6965}),
("Y1 cristal SC-32S C97604",1,{150:0.1284,500:0.1108,3000:0.1059,6000:0.103}),
("C1,C2 10pF C32949",2,{1000:0.005,10000:0.0038}),
("U2 HT7525S C22466410",1,{300:0.0287,3000:0.0254,6000:0.0227,9000:0.0213}),
("Q1,Q2 AO3400A C20917",2,{500:0.0562,3000:0.0536,6000:0.0519}),
("Q3 2N7002 C8545",1,{500:0.0134,3000:0.0117,6000:0.0105}),
("D1 SS34 C8678",1,{600:0.0253,5000:0.0172,10000:0.0163}),
("D2 BAT54WS C191198",1,{500:0.0101,3000:0.0085,6000:0.0076}),
("TVS SMAJ15A C86819",1,{1000:0.0299,5000:0.0265,10000:0.0251}),
("C_F 330uF 25V polimero C54321572",1,{700:0.1253,2800:0.1202,4900:0.1172}),
("C_loc 10uF C15850",1,{600:0.0236,2000:0.0205,10000:0.0194}),
("1uF C52923",2,{1000:0.004,10000:0.0034}),
("100nF C1525",1,{3000:0.002,10000:0.0018}),
("R 0402 x9",9,{1000:0.001,3000:0.0008,10000:0.0007})]
def px(t,n):
    ks=sorted(t); p=t[ks[0]]
    for k in ks:
        if n>=k: p=t[k]
    return p
def bom_unit(n): return sum(c*px(t,n*c) for _,c,t in BOM)
JOINTS=70; UNIQUE=len(BOM)+1
def joints_cost(N):
    j=JOINTS*N; c=0
    for lim,p in ((50000,0.0016),(100000,0.0013),(10**9,0.0012)):
        take=min(j,lim-(0 if lim==50000 else (50000 if lim==100000 else 100000)))
        take=max(0,min(j, take)); c+=take*p; j-=take
        if j<=0: break
    return c
def lot(N, duty=0.16, freight=None, despachante=None, pcb_unit=0.06, merma=0.03):
    piezas=bom_unit(N)*N*(1+merma)
    asm=25.56+8.21+1.53*UNIQUE+joints_cost(N)+0.45
    pcb=pcb_unit*N
    varios=max(30,0.01*N)   # embalaje, comision de pago
    fob=piezas+asm+pcb+varios
    kg=0.5+N*0.0025
    fr=freight if freight is not None else 40+8*kg
    cif=(fob+fr)*1.01
    courier = fob<=3000
    desp = despachante if despachante is not None else (60 if courier else 450)
    d=cif*duty; te=cif*0.03
    nonrec=cif+d+te+desp
    base=cif+d+te
    rec=base*(0.21+0.20+0.06+0.025)
    return dict(N=N,bom=bom_unit(N),piezas=piezas,asm=asm,pcb=pcb,varios=varios,fob=fob,kg=kg,flete=fr,cif=cif,
                derecho=d,tasa=te,desp=desp,courier=courier,puesto=nonrec,puesto_u=nonrec/N,recup=rec)
LOCAL_U=0.25   # programacion+ensayo (propio, ~15 s/u valorado), barniz, etiqueta, bolsa
RECH=0.03
def anual(N, price=6.7, fijos=4500, iibb=0.03, cheque=0.012, ganancias=0.30, duty=0.16):
    L=lot(N,duty=duty)
    costo_u=L["puesto_u"]+LOCAL_U
    costo_u*=1+RECH
    ventas=price*N
    imp_ventas=ventas*(iibb+cheque)
    bruto=ventas-costo_u*N
    antes=bruto-imp_ventas-fijos
    neto=antes*(1-ganancias) if antes>0 else antes
    return L,costo_u,ventas,imp_ventas,bruto,antes,neto
if __name__=="__main__":
    for n in (10,1000,3300,4400,5400,10000):
        print(f"BOM unit @{n}: {bom_unit(n):.3f}")
    print()
    for N in (1000,3300,4400,5400,10000):
        L=lot(N)
        print(f"N={N}: piezas {L['piezas']:.0f} asm {L['asm']:.0f} pcb {L['pcb']:.0f} varios {L['varios']:.0f} FOB {L['fob']:.0f} kg {L['kg']:.1f} flete {L['flete']:.0f} CIF {L['cif']:.0f} der {L['derecho']:.0f} TE {L['tasa']:.0f} desp {L['desp']} courier {L['courier']} puesto {L['puesto']:.0f} ({L['puesto_u']:.3f}/u) recup {L['recup']:.0f}")
    print()
    for N in (3300,4400,5400,10000):
        L,cu,v,iv,b,a,n=anual(N)
        print(f"N={N}: costo/u {cu:.2f} ventas {v:.0f} costo {cu*N:.0f} bruto {b:.0f} imp.ventas {iv:.0f} antes_gan {a:.0f} neto {n:.0f}")
    print("sens duty 0/16/20 @4400:",[round(anual(4400,duty=d)[5]) for d in (0,0.16,0.20)])
    print("sens price 5/6/6.7/8 @4400:",[round(anual(4400,price=p)[5]) for p in (5,6,6.7,8)])
