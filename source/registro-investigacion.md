# Registro de investigación — barrido ampliado de oportunidades

Bitácora del barrido de oportunidades fuera de la lista inicial de candidatos A–G
(sección 14 del informe). Registra consultas realizadas, hallazgos con su fuente y
nivel de evidencia, y las pistas descartadas.

**Regla de la bitácora:** ningún hallazgo entra al informe sin fuente localizable.
Lo que no se pudo obtener se registra como no obtenido, no se completa con
supuestos.

---

## Plan de lotes

| Lote | Alcance | Estado |
|---:|---|---|
| 1 | Condensadores refrigerados por aire (ACC), condensadores y torres de refrigeración | **Completo** |
| 2 | Paredes de agua de caldera, headers de caldera e internos de hogar | **Completo** |
| 3 | Eólica: palas, torres y monopilotes marinos | Pendiente |
| 4 | Presas, vertederos, compuertas de toma y válvulas de gran tamaño | Pendiente |
| 5 | Chimeneas, hornos industriales e intercambiadores de calor | Pendiente |
| 6 | Subestaciones: interior de aparamenta, sistemas de cables y transformadores | Pendiente |
| 7 | Solar y tareas nucleares del catálogo sectorial aún no cubiertas | Pendiente |
| 8 | Consolidación: fichas nuevas, ranking e integración al informe | Pendiente |

---

## Lote 1 — Condensadores refrigerados por aire (ACC)

**Consultas:** `EPRI robotic inspection air-cooled condenser ACC tube inspection robot utility` ·
`air-cooled condenser ACC tube leak detection robot crawler inspection service vendor` ·
descarga y lectura completa de la guía de inspección interna de ACCUG.

### Hallazgo 1.1 — La cobertura de inspección es reconocidamente incompleta

La guía de inspección interna de la asociación de usuarios de ACC establece que los
ductos inferiores se acceden sin gran dificultad, pero que

> «es probablemente irreal esperar que se inspeccione más de uno o dos de los ductos
> superiores de una unidad durante una parada»

y recomienda que la planta elija un ducto superior específico para inspeccionar.

- **Clase:** hecho publicado por una asociación de usuarios de la industria.
- **Nivel:** B.
- **Fuente:** Air Cooled Condenser Users Group, *ACC.01: Guidelines for Internal
  Inspection of Air-Cooled Condensers*, mayo 2015. Comité integrado por Xcel Energy,
  PG&E, NV Energy, GWF Energy, Structural Integrity Associates y Falcon Group.
  https://competitivepower.us/pub/pdfs/guidelines-for-internal-inspection-of-air-cooled-condensers-2015.pdf
- **Por qué importa:** es una declaración explícita de cobertura incompleta hecha por
  los propios operadores. El dolor no es que la inspección sea cara: es que **no se
  hace** sobre la mayor parte del activo.

### Hallazgo 1.2 — El acceso reúne los tres costos que este informe busca

De la misma guía: alcanzar el ducto superior de distribución puede exigir andamiaje o
escalera temporal y una trepada difícil por barandas hasta el registro de acceso, con
protección contra caídas obligatoria. El ductwork del ACC se define como **espacio
confinado**: exige calidad de aire respirable verificada, monitoreo durante la
permanencia y plan de rescate, porque las riostras cruzadas de los ductos superiores
pueden obstruir la extracción de una persona en una emergencia.

- **Clase:** hecho publicado. **Nivel:** B. **Fuente:** ídem 1.1.
- **Por qué importa:** andamiaje + trabajo en altura + espacio confinado + parada. Es
  la misma estructura de costo evitado que sostiene el caso del bus isofásico.

### Hallazgo 1.3 — Mecanismo de falla y consecuencia económica

La corrosión del lado vapor transporta óxido de hierro al agua de alimentación de
caldera, y las penetraciones pasantes en los tubos de refrigeración causan ingreso de
aire, con pérdida de rendimiento del condensador.

- **Clase:** hecho publicado. **Nivel:** B. **Fuente:** ídem 1.1.

### Hallazgo 1.4 — Escala del activo

Un ACC típico puede tener del orden de 20.000 tubos, 40.000 soldaduras, numerosas
válvulas, ductos de gran tamaño y paredes de placa; buscar una fuga puede equivaler a
encontrar un orificio menor que una moneda en una superficie de tres o cuatro canchas
de fútbol.

- **Clase:** cifra de prensa técnica especializada, no verificada de forma
  independiente. **Nivel:** C.
- **Fuente:** *Combined Cycle Journal*, artículos sobre limpieza y detección de fugas
  en ACC. https://www.ccj-online.com/air-cooled-condensers-effective-cleaning-and-leak-detection/

### Hallazgo 1.5 — Qué resuelve hoy el mercado

- **Conco Services** presta servicios de limpieza y de detección de fugas con gas
  trazador en ACC. Resuelve **localización de fugas desde el exterior**, no inspección
  interna del estado de corrosión. **Nivel:** C.
- **EPRI** desarrolla una metodología de ensayo con cámara acústica montada en dron
  para inspección de ACC, sobre la base de resultados con cámara acústica de mano, y
  reporta inspección con dron infrarrojo para analizar distribución de calor en
  instalaciones de utilities. **Nivel:** B (publicación institucional).
  https://eprijournal.com/robotics-in-power-plants-getting-smaller-smarter/
- **No se identificó** ningún crawler ni robot de inspección interna de ductos de ACC
  después de las búsquedas listadas arriba. No equivale a decir que no exista: hay que
  cerrar con búsqueda de patentes y con consulta directa a la asociación de usuarios.

### Conclusión preliminar del lote 1

Candidato nuevo con perfil atractivo: **inspección interna robotizada de ductos de
distribución de ACC**. Dolor documentado por los usuarios, cobertura hoy incompleta por
razones de acceso y seguridad, incumbente que resuelve un problema adyacente y no el
mismo, y alta reutilización de la plataforma existente (espacio confinado, tether,
cámara, iluminación, mapeo).

**Pendiente antes de promoverlo a ficha completa:** cantidad de unidades con ACC en el
parque objetivo, costo real de una parada con andamiaje, screening de patentes y
verificación de si algún proveedor de limpieza ya ofrece inspección interna
robotizada.

---

## Lote 2 — Paredes de agua de caldera e internos de hogar

**Consultas:** `Gecko Robotics boiler waterwall ultrasonic inspection robot utility deployments 2025` ·
`boiler waterwall tube inspection robot competitors Gecko Robotics alternative wall climbing ultrasonic 2026 market`.

### Hallazgo 2.1 — El nicho tiene un incumbente fuerte y consolidado

Gecko Robotics opera una familia de robots trepadores con ruedas magnéticas que
recorren superficies de acero —paredes de caldera, tanques, cascos de buque, exterior
de tuberías— con ultrasonido de arreglo de fases, sensores acústicos, corrientes
inducidas, cámara y LiDAR, y entrega los resultados como modelo digital del activo.
El chorro de agua actúa como acoplante y permite un barrido continuo de gran densidad
de puntos, frente a la cobertura parcial de una inspección manual con acceso por
cuerdas.

- **Clase:** declaración de fabricante y de prensa especializada, no verificada de
  forma independiente. **Nivel:** C.
- **Fuentes:** sitio del fabricante, https://www.geckorobotics.com/ ; Robotics 24/7,
  ampliación de la alianza con Sumitomo SHI FW para inspección de calderas,
  https://www.robotics247.com/article/sumitomo_expands_partnership_with_gecko_robotics_to_help_service_boilers

### Hallazgo 2.2 — No es un proveedor aislado

Además del anterior aparecen, en el mismo nicho de inspección robotizada de calderas y
superficies de acero: Waygate Technologies, HiBot, ICM International Climbing
Machines, Invert Robotics, Inuktun, ULC Robotics, Sarcos, Gridbots y varios
fabricantes de origen chino.

- **Clase:** listado de agregadores de mercado y perfiles de empresa. **Nivel:** D,
  usado sólo para descubrir nombres; cada uno debe verificarse en fuente primaria.

### Hallazgo 2.3 — Evidencia de que el mercado ya se comporta como servicio

La alianza con un fabricante de calderas para prestar el servicio de inspección a
escala global indica que el canal comercial ya está tomado por el eje
fabricante-proveedor de servicio, no sólo el producto.

- **Clase:** inferencia de ingeniería y de negocio sobre la fuente de 2.1.

### Nota de calidad de fuente

Un perfil comercial secundario atribuye a estos robots una velocidad de trepado de
«60 pies por segundo». La cifra es físicamente inverosímil para un crawler magnético
—equivale a 18 m/s— y probablemente corresponda a pies por minuto. **No se utiliza**;
queda registrada como ejemplo de por qué las fuentes de nivel D no sostienen una
conclusión.

Las cifras de tamaño de mercado que aparecen en estas búsquedas provienen de informes
comerciales opacos (nivel D) y, por la regla de metodología del informe, **no se usan
como base** de ningún dimensionamiento.

### Conclusión preliminar del lote 2

**No perseguir** como producto genérico. La inspección robotizada de paredes de agua
de caldera está ocupada por un incumbente con producto, datos, canal y contratos, y
por al menos media docena de competidores adicionales. Sólo justificaría revisarse si
apareciera un hueco muy concreto —geometría interna del hogar inaccesible al trepador
externo, o headers de caldera, que se solapan con el candidato B— y ese hueco debería
demostrarse antes de invertir, no suponerse.
