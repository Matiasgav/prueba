"""Recorrido de la Z en dos pisos: estados de 0 a ~82 mm extraídos (cinemática con el lazo simulado)."""
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation, PillowWriter
from rod import W, H, r, D
import dibujo_z as dz

w = 9.3                                   # punta-base de un lazo (simulación)
EMAX = 4 * (dz.XR - (dz.XL + 2 * w))      # ~82 mm
cA, cB = '#1f6fb2', '#e07b00'


def dibujar(ax, e, small=False):
    ax.clear()
    t = dz.XR - e / 4                     # lazos 1 y 3 ruedan 1 mm cada 4 mm extraídos (2 lazos x 2)
    A, B = dz.path(t, dz.XL, t)
    ax.add_patch(Rectangle((-14, -3), W + 17, H + 6, color='#d5d8dc'))
    ax.add_patch(Rectangle((0, 0), W, H, fc='w', ec='k'))
    ax.add_patch(Rectangle((-14, H - D), 14, D, color='w'))
    ax.add_patch(Rectangle((0.2, 0.2), 5, 3.1, fc='#bdbdbd', ec='k', lw=.8, zorder=6))
    for P, c in ((A, cA), (B, cB)):
        ax.plot(P[:, 0], P[:, 1], color=c, lw=D * (2.2 if small else 4.2), alpha=.4, solid_capstyle='round')
        ax.plot(P[:, 0], P[:, 1], color=c, lw=1.3)
    # cable afuera: marca roja cada 10 mm
    ax.plot([-14, B[-1, 0]], [B[-1, 1]] * 2, color=cB, lw=1.3)
    m0 = B[-1, 0] - e                    # una marca fija del cable, que sale con él
    for k in range(0, 9):
        xm = m0 + 10 * k
        if xm < -14 or xm > B[-1, 0]:
            continue
    ax.annotate('', (-13.5, H - r), (-3, H - r), arrowprops=dict(arrowstyle='-|>', color='#c62828', lw=1.5))
    ax.set_xlim(-14, W + 3); ax.set_ylim(-3, H + 3); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(f'{e:.0f} mm extraídos', fontsize=10 if small else 13, color='#c62828' if e >= 70 else 'k')


# tira de estados
es = [0, 20, 40, 60, 70, EMAX]
fig, axs = plt.subplots(2, 3, figsize=(15, 7.4))
for ax, e in zip(axs.flat, es):
    dibujar(ax, e, small=True)
axs.flat[-1].set_title(f'{EMAX:.0f} mm extraídos (tope)', fontsize=10, color='#c62828')
fig.suptitle('Cable en Z, dos pisos: azul = piso 1 (PCB), naranja = piso 2 (tapa). '
             'Al tirar, los dos lazos de la derecha ruedan juntos hacia la izquierda.', fontsize=11)
fig.tight_layout(); fig.savefig('carrera_Z.png', dpi=140)

# animación
fig2, ax2 = plt.subplots(figsize=(8, 5))
fr = np.r_[np.linspace(0, EMAX, 40), np.full(8, EMAX), np.linspace(EMAX, 0, 40), np.zeros(8)]
anim = FuncAnimation(fig2, lambda i: dibujar(ax2, fr[i]), frames=len(fr))
anim.save('carrera_Z.gif', writer=PillowWriter(fps=15))
print(EMAX)
