# Bisagra de torque con arandelas D

Dos eslabones con una articulación, para medir el torque de trabado que da una
pila de arandelas D entre una oreja y el nudillo. Todo sale de
`generar_modelo.py` (`python3 generar_modelo.py`; requiere `manifold3d`,
`trimesh` y `numpy`), que escribe los STL en `stl/` y el visor `visor.html`.

## Qué imprimir (`stl/`)

Cada archivo es una sola pieza; la cantidad sugerida se copia en el laminador.

| Archivo | Cantidad | Notas |
|---|---|---|
| `eslabon_A_horquilla.stl` | 1 | Acostado, sin soportes. Placa aligerada (8 mm con ventana) |
| `eslabon_B_nudillo.stl` | 1 | Tuerca M4 cautiva del lado de la pila; autorroscante del lado libre |
| `arandela_D_0_2mm.stl` | 24 | Una sola capa de 0,2. Con 24 se arma la pila completa |
| `arandela_D_0_4mm.stl` | 12 | |
| `arandela_D_0_8mm.stl` | 8 | 6 para la pila + 2 de repuesto |
| `arandela_redonda_0_2mm.stl` | 4 | Relleno |
| `arandela_redonda_0_4mm.stl` | 4 | Relleno |
| `arandela_redonda_0_8mm.stl` | 6 | Relleno |
| `tapa_B_1_6mm.stl` | 1 | Va bajo la cabeza, con la lengüeta hacia B |

## Armado de la pila

Orden desde el nudillo, en el lado x = 0:
`nudillo B · oreja A (3 mm) · arandelas · tapa B (1,6 mm) · cabeza`.

- La pila va por fuera de la oreja y **siempre suma 4,8 mm** (más la tapa):
  arandelas D de un espesor más redondas de relleno. Con todo apretado el hombro
  entra 0,6 mm en el nudillo y nunca toca fondo.
- Cada arandela D tiene una lengüeta que entra en la ranura de su eslabón. Las
  ranuras quedan abiertas en la punta de los eslabones: con el tornillo afuera,
  las arandelas entran deslizando a lo largo del eje. Después va la tapa (con
  lengüeta hacia B) y el tornillo.
- Las D van alternadas desde la oreja: la primera con la lengüeta hacia B, la
  siguiente hacia A, y así. Las redondas van al final, del lado de la tapa.
- Caras deslizantes: nudillo/oreja + oreja/1.ª D + … + última/tapa. Con n
  arandelas D: n + 2 si n es par y n + 1 si es impar.
- La otra oreja no lleva arandelas: su tornillo se aprieta a fondo contra el
  hombro y la deja girar con 0,2 mm de juego.

Tornillos: Accu SSHE-M4-5-10-A2 (hombro Ø5 × 10, rosca M4 × 5).

Tuerca: 1 tuerca hexagonal M4 común (DIN 934, 7 mm entre caras, 3,2 de alto),
del lado de la pila. Se mete de costado por una ranura abierta hacia arriba
antes de pasar el tornillo; empieza a 2,8 mm de la cara del nudillo. El
alojamiento es ajustado entre caras (+0,1 mm), tiene 0,4 mm de holgura a lo
largo del eje y el hexágono baja 0,4 mm más allá del centro, por si el fondo
sale corto al imprimir. En la oreja libre el tornillo se enrosca directo en el
plástico (agujero de Ø3,5) y el hombro hace tope a 5,6 mm de la cara. En la pila la tuerca empieza a 2,8 mm de la cara del nudillo; en
la oreja libre el hombro hace tope sobre la tuerca. La versión sin tuercas usa
agujeros autorroscantes de Ø3,5.
