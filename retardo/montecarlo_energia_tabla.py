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
print(json.dumps({"reqs":reqs,"cf":out}))
