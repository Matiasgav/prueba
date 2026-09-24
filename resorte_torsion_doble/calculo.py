"""Cálculo de un resorte de torsión doble (cuerda de piano, ASTM A228).

Requisito: par de 5 N·mm en posición inicial y 10 N·mm tras 60° de giro,
montado sobre un eje de Ø3 mm. Fórmulas de Shigley (cap. 10, resortes de torsión).
"""
from math import pi

# --- Requisitos ---------------------------------------------------------
T_ini, T_fin = 5.0, 10.0      # N·mm, par total del resorte doble
recorrido = 60.0              # grados
eje = 3.0                     # mm

# --- Diseño elegido -----------------------------------------------------
d = 0.38                      # mm, diámetro de alambre (0,015") — mínimo largo con FS ≈ 2
ID = 3.6                      # mm, diámetro interior libre
L_brazo, L_lazo = 10.0, 5.0   # mm, brazo exterior y medio lazo central (por cuerpo)
E = 200_000                   # MPa, cuerda de piano
A, m = 2211, 0.145            # Sut = A / d^m (Shigley, tabla 10-4)

D = ID + d
C = D / d
k_total = (T_fin - T_ini) / recorrido          # N·mm/°
k_cuerpo = k_total / 2                         # cada cuerpo aporta la mitad
theta_pre = T_ini / k_total                    # precarga desde libre
theta_max = theta_pre + recorrido

Ne = E * d**4 / (3666 * D * k_cuerpo)          # espiras efectivas por cuerpo
Nb = Ne - (L_brazo + L_lazo) / (3 * pi * D)    # espiras del cuerpo

D_min = D * Nb / (Nb + theta_max / 360)        # el diámetro se cierra al cargar
ID_min = D_min - d
largo_cuerpo = (Nb + 1 + theta_max / 360) * d

M_cuerpo = T_fin / 2
Ki = (4 * C**2 - C - 1) / (4 * C * (C - 1))
sigma = Ki * 32 * M_cuerpo / (pi * d**3)
Sut = A / d**m
Sy = 0.78 * Sut

print(f"Índice C = {C:.2f}   D medio = {D:.2f} mm   OD = {D + d:.2f} mm")
print(f"k total = {k_total:.4f} N·mm/°   k por cuerpo = {k_cuerpo:.4f} N·mm/°")
print(f"Precarga = {theta_pre:.0f}°   ángulo máx desde libre = {theta_max:.0f}°")
print(f"Espiras efectivas Ne = {Ne:.2f}   espiras de cuerpo Nb = {Nb:.2f}")
print(f"ID mínimo cargado = {ID_min:.2f} mm (holgura diametral {ID_min - eje:.2f} mm)")
print(f"Largo de cada cuerpo ≈ {largo_cuerpo:.1f} mm")
print(f"Ki = {Ki:.3f}   σ máx = {sigma:.0f} MPa   Sut = {Sut:.0f} MPa   "
      f"Sy ≈ {Sy:.0f} MPa   FS estático = {Sy / sigma:.1f}")
