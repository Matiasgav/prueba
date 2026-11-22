# Monte Carlo de energia (P3), error temporal (P2/P4) y acople dV/dt en gates (P1)
# Uso: python3 montecarlo_fallos.py
import numpy as np
rng=np.random.default_rng(1); N=2_000_000
# ---- Energía (peor caso t2 = 40 s) ----
Vp=rng.uniform(10.8,13.2,N); Vd1=rng.uniform(0.35,0.5,N)
V0=Vp-Vd1
C=330e-6*rng.normal(1,0.2/3,N)*rng.uniform(0.88,1.0,N)   # tol ±20 % (3σ) + frío
Ileak=rng.uniform(5e-6,25e-6,N)                            # cargas 7 µA + fuga C_F con cola
t2=40.0
Vf=V0-Ileak*t2/C
Rb=rng.uniform(1.0,2.0,N)
Rtot=Rb+2*rng.uniform(0.035,0.06,N)+rng.uniform(0.025,0.1,N)+0.02
tau=Rtot*C
I2t=Vf**2*C/(2*Rtot)*(1-np.exp(-2*0.020/tau))   # A^2·s
print("Vf 40 s: p0.1 %.2f  med %.2f"%(np.percentile(Vf,0.1),np.median(Vf)))
q=np.percentile(I2t*1e3,[1e-4*100,0.01,0.1,1,50])
print("I2t entregado A2ms percentiles 1ppm,0.01%,0.1%,1%,50%:",np.round(q,2))
for req in [2,3,5,8,10]:
    print(" req %2d A2ms -> P(I2t<req)=%.2e"%(req,np.mean(I2t*1e3<req)))
Ipk=Vf/Rtot; print("Ipico min %.2f A"%Ipk.min())
# ---- Tiempo ----
T=rng.uniform(10,40,N); temp=rng.uniform(-30,70,N)
ppm=rng.uniform(-20,20,N)-0.034*(temp-25)**2+rng.uniform(-5,5,N)
err_xtal=T*ppm*1e-6
err_start=rng.uniform(-1e-3,1e-3,N)*rng.uniform(0.5,3,N)   # corrección de arranque
lat=rng.uniform(0.005,0.050,N)-0.020                         # latencia t0 no compensada
err=err_xtal+err_start+lat
rel=err/T
print("Error temporal: max abs %.1f ms ; max rel %.3f %%"%(np.abs(err).max()*1e3,np.abs(rel).max()*100))
# sin cristal: LSI calibrado contra HSI16 (±3 % peor caso en T, supuesto)
hsi=rng.uniform(-0.03,0.03,N); rel2=hsi+lat/T
print("Sin cristal (HSI ±3%%): P(|err|>5%%)=%.1e  max %.2f %%"%(np.mean(np.abs(rel2)>0.05),np.abs(rel2).max()*100))
# ---- Miller dV/dt en las gates ----
Crss=77e-12; Vth_min=0.65-0.003*45  # a 70 °C
for Rs in [0,0.1,0.5]:
    Rch=Rs+0.15+0.05
    dvdt=11.3/(Rch*330e-6)
    for Rpd in [100e3,10e3]:
        print(" R_s=%.1f Ω Rpd=%3dk: dV/dt=%.0f V/ms  Vg=%.2f V (Vth min caliente %.2f)"%(Rs,Rpd/1e3,dvdt/1e3,Crss*dvdt*Rpd,Vth_min))
