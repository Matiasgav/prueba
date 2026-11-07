# Paquete de arandelas de fricción: verificación

Cálculo: `python3 calculo_arandelas.py` (solo usa la biblioteca estándar). Los supuestos están marcados en el código.

## Supuestos
- 6 arandelas intercaladas A-B-A-B-A-B (así se ve en el corte), con un espesor de **t ≈ 0,5 mm** medido sobre la imagen. Hay que confirmarlo.
- 5 interfaces A/B que deslizan. Las caras extremas se toman como solidarias.
- Tornillo de hombro Ø6/M5 inoxidable A2-70, hexágono de 3 mm (tipo ISO 7379), K = 0,25 (inox en seco). La cabeza mide Ø10 y aprieta una corona de Ø6 a Ø10, con r_eff = 4,08 mm.
- μ inox/inox entre 0,15 (lubricado) y 0,40 (seco). Para el criterio "desliza antes de deformar" se usa μ_máx.
- Se toma como fallo el inicio de la fluencia (Rp0,2) en el aplastamiento de los cantos.

## Resultados (t = 0,5 mm, AISI 304)
| Elemento | Carga con la Allen apretada (2,5 N·m → ~2000 N) | Capacidad | Estado |
|---|---|---|---|
| Tornillo (cuello de rosca) | 250 MPa von Mises | 450 MPa | OK hasta ~4 N·m |
| Compresión entre arandelas | 40 MPa | 215 MPa | OK |
| **Oreja A** (aplastamiento lateral, 1 mm × t, brazo 7 mm) | par de fricción por arandela 6,5 N·m | **0,75 N·m** | **FLUYE (×8,7)** |
| Caras de 11 mm de B (cantos) | 6,5 N·m | 1,38 N·m | FLUYE (×4,7) |

Con todo apretado, el paquete resiste bien la compresión. El problema aparece cuando se le aplica par a la articulación. Antes de deslizar, cada arandela intermedia tiene que transmitir la fricción de sus **dos** caras, 2·μ·F·r_eff. Ese par supera con creces lo que aguanta la oreja de A, que es el punto débil n.º 1, y también lo que aguantan los cantos de B, el n.º 2. En ese caso el sistema **no desliza: se deforman las orejas**.

## Conclusión clave
El par máximo de traba que se puede tener deslizando antes de deformar es

    T_traba,máx = (N_interfaces / 2) · T_cap,arandela

Este valor **no depende de μ ni de la precarga**. μ y F solo fijan el apriete al que se alcanza ese límite. Para subirlo hay tres palancas:
1. Más capacidad por arandela: más encastre de la oreja (pasar de 1 mm a toda la oreja), más espesor y un inox endurecido (301 1/2 duro, 17-7PH).
2. Más arandelas: el par crece de forma lineal con el número de interfaces.
3. Una precarga **controlada** que no dependa del par de apriete a mano.

Ejemplos con la tabla del script: con t = 1 mm de 17-7PH desliza antes de fluir incluso apretando a 2,5 N·m (~22 N·m de traba máxima). Con t = 0,5 mm de 304 hay que limitar la precarga a ~230 N (≈0,3 N·m de apriete, imposible de controlar a mano) y la traba queda en ~1,9 N·m.

## Recomendaciones
- **Oreja A**: encastrarla en toda su longitud (2–2,5 mm) en lugar de solo 1 mm. Mejor aún, usar dos orejas opuestas, que reparten la carga en un par de fuerzas y descargan el agujero contra el vástago.
- **Precarga definida**: dejar que el tornillo de hombro haga tope en su hombro y dar la carga con una arandela Belleville calibrada. Así F no depende de cuánto se apriete la Allen y se compensa el desgaste. Atención: si el hombro hace tope antes que el paquete, las arandelas quedan sin apriete.
- **Arandela en contacto con la cabeza**: tiene que ser del mismo tipo que el eslabón en el que rosca el tornillo. Si no, el giro de la articulación aplica par a la cabeza y afloja (o sobreaprieta) el tornillo.
- **Gripado inox/inox**: el 304 contra 304 en seco gripa. Lubricar (μ más bajo y estable) o alternar materiales/recubrimientos. Bajar μ no cambia la traba máxima, solo exige más F.
- **Eslabones**: el eslabón recibe la misma fuerza de aplastamiento que la oreja. Si es de aluminio o plástico, puede ser él el que se marque primero.
