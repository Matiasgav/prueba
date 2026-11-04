"""Explicación de las dos capas: piso 1, piso 2 y vista 3D."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rod import W, H, r, D
import dibujo_z as dz

A, B = dz.path(dz.XR, dz.XL, dz.XR)          # estado guardado
DEP = 2.5 * D; zA = r + .8; zB = DEP - r
cA, cB = '#1f6fb2', '#e07b00'
fig = plt.figure(figsize=(15, 9))

def frente(ax, P, c, tit, extra=None):
    ax.add_patch(Rectangle((-8, -3), W + 11, H + 6, color='#d5d8dc'))
    ax.add_patch(Rectangle((0, 0), W, H, fc='w', ec='k'))
    ax.add_patch(Rectangle((-8, H - D), 8, D, color='w'))
    ax.add_patch(Rectangle((0.2, 0.2), 5, 3.1, fc='#bdbdbd', ec='k', lw=.8, zorder=6))
    ax.text(2.7, 1.75, 'sold.', fontsize=7, ha='center', va='center', zorder=7)
    if extra is not None:
        ax.plot(extra[:, 0], extra[:, 1], color='#999', lw=D * 4.5, alpha=.15, solid_capstyle='round')
    ax.plot(P[:, 0], P[:, 1], color=c, lw=D * 4.5, alpha=.45, solid_capstyle='round')
    ax.plot(P[:, 0], P[:, 1], color=c, lw=1.5)
    n = len(P); 
    for k in (n // 6, n // 2, 5 * n // 6):                 # flechas de sentido
        ax.annotate('', P[k + 1], P[k], arrowprops=dict(arrowstyle='-|>', color=c, lw=1.5, mutation_scale=16))
    ax.set_xlim(-8, W + 3); ax.set_ylim(-3, H + 3); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(tit, fontsize=11, loc='left')

a1 = fig.add_axes([0.02, 0.52, 0.46, 0.42]); a2 = fig.add_axes([0.52, 0.52, 0.46, 0.42])
frente(a1, A, cA, 'PISO 1 (pegado a la PCB)\nsale de la soldadura → vuelta a la derecha → vuelve por arriba')
a1.text(1.0, H / 2 + 1, 'acá\nbaja al\npiso 2', fontsize=8, color=cA)
frente(a2, B, cB, 'PISO 2 (encima del piso 1, del lado de la tapa)\nbaja por la izquierda → va por abajo → vuelta a la derecha → salida',
       extra=A)
a2.text(1.0, H / 2 - 4, 'llega\ndel\npiso 1', fontsize=8, color=cB)
a2.text(-7.5, H - D - 2.5, 'SALIDA ←', fontsize=9, fontweight='bold')
a2.text(W / 2, -2.3, 'en gris, debajo: el piso 1', fontsize=8, ha='center', color='#666')

# 3D
ax = fig.add_axes([0.08, 0.0, 0.84, 0.5], projection='3d')
def tubo(P, z, c):
    Z = z if np.ndim(z) else np.full(len(P), z)
    ax.plot(P[:, 0], Z, P[:, 1], color=c, lw=7, alpha=.9, solid_capstyle='round')
zAa = np.full(len(A), zA)
# lazo 2: tramo final de A y tramo inicial de B cambian de piso gradualmente
k = np.where(A[:, 0] < dz.XL + 9.5)[0]; zAa[k] = np.interp(A[k, 1], [H / 2, H - r], [(zA + zB) / 2, zA])
zBb = np.full(len(B), zB)
k = np.where((B[:, 0] < dz.XL + 9.5) & (np.arange(len(B)) < len(B) // 3))[0]
zBb[k] = np.interp(B[k, 1], [r, H / 2], [zB, (zA + zB) / 2])
tubo(A, zAa, cA); tubo(B, zBb, cB)
ax.plot([-8, B[-1, 0]], [zB, zB], [B[-1, 1]] * 2, color=cB, lw=7)
# caja
for x in (0, W):
    for z in (0, DEP):
        ax.plot([x, x], [z, z], [0, H], color='k', lw=.5)
for y in (0, H):
    for z in (0, DEP):
        ax.plot([0, W], [z, z], [y, y], color='k', lw=.5)
    for x in (0, W):
        ax.plot([x, x], [0, DEP], [y, y], color='k', lw=.5)
xx, yy = np.meshgrid([0, W], [0, H]); ax.plot_surface(xx, np.zeros_like(xx), yy, color='#2e7d32', alpha=.18)
ax.text(W / 2, -1, -4, 'PCB (fondo)', color='#1b5e20', fontsize=9)
ax.text(-8, zB, H + 2, 'salida', fontsize=9)
ax.set_box_aspect((W + 8, DEP * 2.2, H)); ax.view_init(elev=22, azim=-62)
ax.set_xlabel('ancho (mm)'); ax.set_ylabel('profundidad'); ax.set_zlabel('alto')
ax.set_yticks([0, DEP]); ax.set_yticklabels(['0', '8,75'])
ax.set_title('Vista 3D: dos vueltas, una encima de la otra (azul = piso 1, naranja = piso 2)', fontsize=11)
fig.savefig('dibujo_capas.png', dpi=140)
