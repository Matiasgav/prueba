"""Cálculo de un resorte de torsión simple (cuerda de piano, ASTM A228).

Requisito: par de 5 N·mm en posición inicial y 10 N·mm tras 60° de giro,
montado sobre un eje de Ø3 mm. Fórmulas de Shigley (cap. 10, resortes de torsión).
"""
from math import pi, sqrt

# --- Requisitos ---------------------------------------------------------
T_ini, T_fin = 5.0, 10.0      # N·mm
recorrido = 60.0              # grados
eje = 3.0                     # mm

# --- Diseño elegido -----------------------------------------------------
d = 0.45                      # mm, diámetro de alambre
ID = 3.6                      # mm, diámetro interior libre
L1, L2 = 10.0, 10.0           # mm, largo de los dos brazos
E = 203_400                   # MPa, cuerda de piano d < 0,8 mm (Shigley, tabla 10-5)
A, m = 2211, 0.145            # Sut = A / d^m (Shigley, tabla 10-4)

D = ID + d
C = D / d
k = (T_fin - T_ini) / recorrido                # N·mm/°
theta_pre = T_ini / k                          # precarga desde libre
theta_max = theta_pre + recorrido

Ne = E * d**4 / (10.8 * D * k * 360)           # espiras efectivas (Shigley ec. 10-51, incluye fricción)
Nb = Ne - (L1 + L2) / (3 * pi * D)             # espiras del cuerpo

D_min = D * Nb / (Nb + theta_max / 360)        # el diámetro se cierra al cargar
ID_min = D_min - d
largo_cuerpo = (Nb + 1 + theta_max / 360) * d

Ki = (4 * C**2 - C - 1) / (4 * C * (C - 1))
sigma = Ki * 32 * T_fin / (pi * d**3)
Sut = A / d**m
Sy = 0.78 * Sut

# Fatiga a 1e6 ciclos: Sr = 0,50·Sut sin granallar (Shigley, tabla 10-6), criterio de Gerber
sigma_min = sigma * T_ini / T_fin
sa, sm = (sigma - sigma_min) / 2, (sigma + sigma_min) / 2
Sr = 0.50 * Sut
Se = (Sr / 2) / (1 - (Sr / 2 / Sut)**2)
nf = 0.5 * (Sut / sm)**2 * (sa / Se) * (-1 + sqrt(1 + (2 * sm * Se / (Sut * sa))**2))

print(f"Índice C = {C:.2f}   D medio = {D:.2f} mm   OD = {D + d:.2f} mm")
print(f"k = {k:.4f} N·mm/°")
print(f"Precarga = {theta_pre:.0f}°   ángulo máx desde libre = {theta_max:.0f}°")
print(f"Espiras efectivas Ne = {Ne:.2f}   espiras de cuerpo Nb = {Nb:.2f}")
print(f"ID mínimo cargado = {ID_min:.2f} mm (holgura diametral {ID_min - eje:.2f} mm)")
print(f"Largo del cuerpo ≈ {largo_cuerpo:.1f} mm")
print(f"Ki = {Ki:.3f}   σ máx = {sigma:.0f} MPa   Sut = {Sut:.0f} MPa   "
      f"Sy ≈ {Sy:.0f} MPa   FS estático = {Sy / sigma:.1f}")
print(f"σ mín = {sigma_min:.0f} MPa   FS fatiga 1e6 ciclos (Gerber) = {nf:.2f}")
