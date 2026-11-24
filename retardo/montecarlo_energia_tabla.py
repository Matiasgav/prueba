import numpy as np, json
rng=np.random.default_rng(7); N=1_000_000
out={}
reqs=[round(x,1) for x in np.arange(1,15.01,0.5)]
for Cn in [150,330,560,1000]:
    Vp=rng.uniform(10.8,13.2,N); V0=Vp-rng.uniform(0.35,0.5,N)
    C=Cn*1e-6*rng.normal(1,0.2/3,N)*rng.uniform(0.88,1.0,N)
    Vf=V0-rng.uniform(5e-6,25e-6,N)*40/C
    R=rng.uniform(1,2,N)+2*rng.uniform(0.035,0.06,N)+rng.uniform(0.025,0.1,N)+0.02
    I2t=Vf**2*C/(2*R)*(1-np.exp(-0.04/(R*C)))*1e3
    out[Cn]={"p":[float(max(np.mean(I2t<r),0)) for r in reqs],"med":float(np.median(I2t)),"p01":float(np.percentile(I2t,0.1)),"min":float(I2t.min())}
# Alternativa A: 470 µF (un polímero) y 660 µF (dos híbridos Panasonic, el elegido), puente de entrada (2 diodos), fuga aceptada por el banco (≤ 17 µA),
# corte de Q1 cuando V_GS = 0,41·V_CF baja del umbral (0,5–1,3 V) y bloqueo de carga en la entrada (no carga si el pulso es < 9,25–9,75 V).
for Cn in (470,660):
    Vp=rng.uniform(10.8,13.2,N); V0=Vp-2*rng.uniform(0.45,0.65,N)
    C=Cn*1e-6*rng.normal(1,0.2/3,N)*rng.uniform(0.88,1.0,N)
    Vf=V0-rng.uniform(5e-6,17e-6,N)*40/C
    R=rng.uniform(1,2,N)+rng.uniform(0.04,0.09,N)+rng.uniform(0.03,0.06,N)+rng.uniform(0.025,0.1,N)+0.02
    Vcut=rng.uniform(0.5,1.3,N)/0.41
    I2t=Vf**2*C/(2*R)*(1-(Vcut/Vf)**2)*1e3
    uv=Vp<rng.uniform(9.25,9.75,N)
    out[Cn]={"p":[float(np.mean((I2t<r)|uv)) for r in reqs],"med":float(np.median(I2t)),"p01":float(np.percentile(I2t,0.1)),"min":float(I2t.min()),"uv":float(np.mean(uv))}
print(json.dumps({"reqs":reqs,"cf":out}))
