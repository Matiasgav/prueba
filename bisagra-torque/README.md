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

## Armado de la pila

- La pila va en la oreja de x = 0, entre la oreja y el nudillo, y **siempre
  suma 4,8 mm**: arandelas D de un espesor más redondas de relleno. Con todo
  apretado el hombro entra 1,2 mm en el nudillo y nunca toca fondo.
- Cada arandela D tiene una lengüeta que entra en la ranura de su eslabón.
- Para meterlas, sin el tornillo puesto, girá el eslabón B unos 90° (placa B
  hacia arriba). Las D de A entran de costado desde el lado de B, deslizando
  la lengüeta en la ranura de A; las D de B entran subiendo desde abajo hasta
  la ranura de B. Cada una va en su capa, así que no se cruzan. Después volvé
  B a 0°, agregá las redondas y pasá el tornillo.
- Las D van alternadas desde la oreja: la primera con la lengüeta hacia B, la
  siguiente hacia A, y así. Las redondas van al final, del lado del nudillo.
- Caras deslizantes: con n arandelas D, n + 1 si n es par y n si es impar, más
  la cara bajo la cabeza.
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
