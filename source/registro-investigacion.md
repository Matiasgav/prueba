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
| 3 | Eólica: palas, torres y monopilotes marinos | **Completo** |
| 4 | Presas, vertederos, compuertas de toma y válvulas de gran tamaño | **Completo** |
| 5 | Chimeneas, hornos industriales e intercambiadores de calor | **Completo** |
| 6 | Subestaciones: interior de aparamenta, sistemas de cables y transformadores | **Completo** |
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

---

## Lote 3 — Eólica: palas, torres y monopilotes marinos

**Consultas:** `wind turbine blade internal inspection robot inside blade cavity crawler 2025 2026` ·
`wind blade bond line delamination NDT ultrasonic inspection inside blade limitation visual only spar cap` ·
`offshore wind monopile internal inspection robot transition piece weld corrosion ROV crawler service provider`.

### Hallazgo 3.1 — El interior de la pala ya tiene al menos cuatro proveedores

Existen crawlers comerciales específicos para inspección interna de palas, con cámara,
iluminación LED y tether de recuperación:

- **Aerones**, con un crawler de tercera generación que declara escaneo LiDAR, video
  360°, mayor alcance dentro de la pala y cobertura declarada de hasta el 90 % del
  interior.
- **Clobotics Wind Services**, con un crawler que declara dos cámaras de alto rango
  dinámico, iluminación LED, línea de recuperación, unos 6 kg y 50 × 23 × 28 cm, y un
  rendimiento declarado de dos aerogeneradores completos por día con dos técnicos.
- **CERBERUS**, de TSR Wind, con cámara panorámica frontal y dos laterales de alta
  resolución bajo iluminación LED autorregulada.
- **Sensoar**, que ofrece crawlers para diagnosticar fracturas y fallas de alma de
  cortante.

- **Clase:** declaraciones de fabricante, no verificadas de forma independiente.
  **Nivel:** C.
- **Fuentes:** https://aerones.com/meet-the-new-crawler-gen-3/ ·
  https://clobotics.com/news/clobotics-wind-services-announces-its-new-clobotics-crawler-robot/ ·
  https://tsrwind.com/cerberus-crawler-internal-blade-inspections-tsrwind/?lang=en ·
  https://www.sensoar.io/solutions/windturbine/internal-blade-inspection.html
- **Madurez estimada:** M4. Múltiples proveedores con producto y servicio.

### Hallazgo 3.2 — El hueco aparente está bloqueado por una razón física conocida

Los crawlers internos citados son **visuales**: cámara, luz y, en un caso, LiDAR. La
medición cuantitativa de pegado de largueros y alma de cortante se hace con ultrasonido
de baja frecuencia y arreglo de fases, y la literatura técnica documenta sus límites:
el vidrio-epoxi atenúa fuertemente el haz, los defectos cercanos a la superficie —menos
de unos 5 mm en laminados gruesos— caen en la zona muerta de la sonda y en el ruido de
la interfaz agua–vidrio, y **no es posible determinar la condición de regiones que no
son directamente accesibles**.

- **Clase:** hecho técnico publicado en literatura y notas de aplicación de
  fabricantes de instrumentación. **Nivel:** B.
- **Fuentes:** https://www.windpowerengineering.com/low-frequency-ultrasonic-solutions-for-spar-cap-and-shear-web-bonding-inspection-in-wind-blades/ ·
  https://ims.evidentscientific.com/en/applications/shear-web-bonding-inspection ·
  https://forcetechnology.com/en/expertise/inspection-verification-and-maintenance/inspection-and-non-destructive-testing-ndt/blade-inspection
- **Por qué importa:** el hueco que quedaba —llevar medición cuantitativa dentro de la
  pala— no está libre por falta de intentos, sino condicionado por la física del
  material. Es exactamente el tipo de razón por la que un programa de desarrollo
  fracasa, que este estudio busca detectar antes de invertir.

### Hallazgo 3.3 — Monopilotes marinos: también ocupado

En estructuras marinas operan al menos: **iFROG** (InnoTecUK con ORE Catapult, TWI y
Brunel University London, financiado por Innovate UK) para limpieza e inspección de
monopilotes con verificación de soldaduras; **Eddyfi**, con crawlers que acceden a
soldaduras en T para evaluación por método de foco total; **TSC Subsea**, con
verificación de integridad de grout, inspección de soldaduras, mapeo de corrosión y
detección de miembros inundados; **Intertek**, con servicios de ROV de integridad
submarina; e **InnovaIR** y otros proveedores de servicio en zona de salpicadura.

- **Clase:** mezcla de nota de prensa técnica y declaraciones de proveedor.
  **Nivel:** C. Existe además material de la agencia federal estadounidense de
  seguridad y cumplimiento ambiental marino sobre tecnología remota para inspección y
  mantenimiento de eólica marina, que debe leerse como fuente de nivel A antes de
  cualquier conclusión.
- **Fuentes:** https://www.oedigital.com/news/483611-ifrog-robot-for-cleaning-and-inspection-of-offshore-wind-monopiles-completes-trials ·
  https://blog.eddyfi.com/en/renewable-energy-robotic-inspection-solutions ·
  https://www.tscsubsea.com/offshore-wind-subsea-ndt-inspection/ ·
  https://www.bsee.gov/sites/bsee.gov/files/2023-03/802ac.pdf *(no leído en este lote;
  queda registrado como pendiente)*

### Conclusión preliminar del lote 3

**No perseguir.** Tres razones convergentes:

1. El interior de la pala es un mercado M4 con al menos cuatro proveedores y modelo de
   servicio ya instalado.
2. El único hueco funcional aparente —medición cuantitativa desde el interior— está
   limitado por la atenuación del material, un obstáculo físico documentado y no un
   descuido del mercado.
3. La eólica marina, además de estar ocupada, tiene un canal comercial y una logística
   que no se solapan con el activo de referencia ni con el mercado regional
   sudamericano, lo que anula la ventaja de reutilización que sostiene a los mejores
   candidatos.

---

## Lote 4 — Presas, compuertas de toma y válvulas de gran tamaño

**Consultas:** `dam intake gate inspection diver dewatering cost ROV alternative USACE Bureau of Reclamation underwater inspection guidance` ·
lectura de la ficha del proyecto de investigación del Bureau of Reclamation ·
`"large valve" internal inspection robot hydro penstock butterfly valve in-situ inspection without disassembly service`.

### Hallazgo 4.1 — Un organismo federal declara que el buzo no puede entrar

El Bureau of Reclamation de Estados Unidos mantiene un proyecto de investigación sobre
la estructura de toma de Trinity, donde declara que

> *«the tunnel is too dangerous to deploy divers due to its depth, length and confined
> spaces»*

y se pregunta si un vehículo remoto submarino puede realizar evaluaciones de condición
y fotogrametría subacuática. La misma ficha declara que

> *«Reclamation does not have an official underwater ROV inspection program»*

y que el organismo no tiene experiencia previa con fotogrametría subacuática como
alternativa al sonar y al modelado láser 3D.

- **Clase:** hecho publicado por el organismo propietario del activo. **Nivel:** A.
- **Fuente:** U.S. Bureau of Reclamation, Research and Development Office, ficha de
  proyecto 9612. https://www.usbr.gov/research/projects/detail.cfm?id=9612
- **Por qué importa:** es la combinación que este estudio busca —el método convencional
  no puede ejecutarse por seguridad **y** el propietario declara no tener programa
  propio—, pero apunta a una oportunidad de **servicio y método**, no de hardware
  nuevo: los vehículos remotos ya existen comercialmente.

### Hallazgo 4.2 — Las cifras de ahorro que circulan son de proveedor

En material comercial de proveedores de inspección robótica circulan cifras del orden
de USD 2 a 8 millones y de cuatro a seis meses para un ciclo de inspección con vaciado
de embalse en una presa mediana, frente a menos de USD 200.000 y cinco a diez días con
vehículo remoto; y de USD 50.000 a 500.000 de generación perdida por vaciar un canal.

- **Clase:** **declaración de proveedor con interés comercial directo en la
  comparación.** **Nivel:** C, y no se usa como base de ningún cálculo.
- **Por qué se registra igual:** marca el orden de magnitud a verificar contra un
  contrato, una licitación o un informe de utility. Si se confirmara con fuente
  independiente, sería uno de los mayores costos evitados de todo este estudio.
- **Pendiente:** localizar el informe final del proyecto del Bureau of Reclamation y
  documentos de la agencia de ingenieros del ejército estadounidense sobre inspección
  con vehículos remotos de estructuras de navegación, ambos de nivel A.

### Hallazgo 4.3 — Penstocks y válvulas: el equipamiento ya existe

Para inspección interna de conductos y válvulas de gran diámetro se usan crawlers
comerciales —por ejemplo la familia VersaTrax de Eddyfi/Inuktun con cámara de
paneo, inclinación y zoom— para evaluar costuras de soldadura y remaches. La literatura
técnica describe además robots para tuberías de 900 a 1200 mm con cámaras y LiDAR. Las
válvulas mariposa de guarda existen precisamente para permitir inspeccionar el conducto
forzado sin vaciar todo el túnel de aducción.

- **Clase:** mezcla de declaración de fabricante y literatura técnica. **Nivel:** B–C.
- **Fuentes:** https://blog.eddyfi.com/en/how-the-versatrax-goes-the-distance-for-internal-pipeline-inspection ·
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11174578/ ·
  https://www.avkvalves.eu/en/insights/product-insights/dams-reservoirs-and-hydropower/dams-and-reservoirs

### Conclusión preliminar del lote 4

**No es un candidato nuevo de hardware, pero refuerza al candidato F.** El activo
—túneles, tomas y compuertas— tiene un dolor documentado por el propietario, con el
agravante de que el método convencional está vedado por seguridad en ciertos casos. El
equipamiento base ya es comercial, de modo que el valor no está en construir otro
vehículo sino en el paquete de servicio: navegación y localización sin señal satelital
en tramos largos, medición de espesor en contacto, fotogrametría y modelo del activo,
y garantía de recuperación.

**Acción para el lote 8:** no crear ficha nueva; incorporar estos hallazgos como
evidencia adicional del candidato F y mover su pregunta estratégica hacia el paquete de
servicio y método, que es donde el propietario declara no tener capacidad.

---

## Lote 5 — Intercambiadores de calor, hornos industriales y chimeneas

**Consultas:** `heat exchanger tube bundle inspection robot IRIS eddy current remote field automated vendor market mature` ·
`industrial furnace refractory inspection robot high temperature online inspection stack chimney liner drone inspection service`.

### Hallazgo 5.1 — Intercambiadores de calor: mercado maduro y multi-proveedor

La inspección de haces tubulares se hace con una batería de técnicas ya
estandarizadas —corrientes inducidas, campo remoto, campo cercano, fuga de flujo
magnético, sistema rotatorio interno por ultrasonido y videoscopía— combinadas según
el material del tubo. Los proveedores de instrumentación y de servicio están
consolidados: Eddyfi, Evident (ex Olympus), TechCorr, TCR Engineering, entre otros.
Existen además posicionadores robóticos sobre placa tubular con patentes concedidas
desde hace más de una década, y trabajo publicado sobre robots autónomos para
intercambiadores de casco y tubos con análisis automático por redes neuronales.

- **Clase:** hechos técnicos de fabricantes de instrumentación más literatura
  publicada. **Nivel:** B–C.
- **Fuentes:** https://www.eddyfi.com/en/application/heat-exchangers-inspection ·
  https://ims.evidentscientific.com/en/insights/a-faster-way-to-inspect-heat-exchanger-tubes ·
  https://www.tcreng.com/tube-inspection ·
  https://osti.gov/biblio/1853801-autonomous-robot-shell-tube-heat-exchanger-inspection ·
  patentes US 8746089 y US 9273985 sobre posicionamiento automatizado de sonda de
  corrientes inducidas.
- **Madurez estimada:** M5. Técnica normalizada, instrumentación commodity y varios
  proveedores de servicio compitiendo por precio.

### Hallazgo 5.2 — Hornos industriales: hay actividad, pero fuera del sector objetivo

La inspección robotizada de refractarios en siderurgia es un campo activo: sistemas de
inspección para hornos de arco eléctrico, brazos robóticos con transductores
ultrasónicos que miden espesor de refractario a través del casco, cámaras térmicas
para detectar puntos calientes, y el proyecto europeo Robs4Steel, que propone
robotizar la inspección visual del refractario después de cada colada y declara
reducir la presencia humana alrededor del horno de diez veces a una.

- **Clase:** proyecto de investigación europeo y material de proveedores.
  **Nivel:** B para el proyecto, C para los proveedores.
- **Fuentes:** https://trinityrobotics.eu/use-cases/robotized-inspection-system-for-high-temperature-electric-arc-furnaces-eaf/ ·
  https://oxmaint.com/industries/steel-plant/steel-mill-refractory-inspection-robots-ladle-converter-furnace-lining-maintenance

### Hallazgo 5.3 — Prior art de alta temperatura ya patentado

Aparecen patentes recientes específicas sobre **ruedas de alta temperatura para robots
de inspección** (US 12420585 y US 12420586) y sobre control térmico y refrigeración
activa de robots de inspección (US 12302499, US 12156334). El problema de operar un
crawler en ambiente caliente ya tiene titular.

- **Clase:** patentes concedidas: prueban divulgación, no producto en el mercado.
  **Nivel:** A como documento.
- **Por qué importa:** si alguna vez se evaluara un crawler para ambiente caliente,
  estas familias son el primer punto del screening de propiedad intelectual.

### Hallazgo 5.4 — Chimeneas: no se profundizó

Las búsquedas de este lote no arrojaron material específico sobre inspección
robotizada de chimeneas y revestimientos de conducto de humos más allá de servicios
con dron ya establecidos. **Registrado como no obtenido**; queda como consulta
pendiente con términos más específicos de revestimiento refractario de chimenea y de
inspección interna con parada.

### Conclusión preliminar del lote 5

**Descartado para el alcance de este estudio.** Los intercambiadores de calor son un
mercado M5 donde competir significa competir por precio de servicio con instrumentación
commodity. Los hornos industriales tienen actividad real, pero pertenecen a
siderurgia: distinto cliente, distinto canal comercial, ambiente térmico que exige
ingeniería específica y prior art ya patentado sobre el problema central de la alta
temperatura. Ninguno de los dos aprovecha el canal ni la plataforma del activo de
referencia.

---

## Lote 6 — Subestaciones: aparamenta blindada, cables y transformadores

**Consultas:** `gas insulated switchgear GIS internal inspection robot SF6 enclosure without disassembly research prototype` ·
`"inspection robot" GIS busbar enclosure crawler research paper power cable tunnel inspection robot utility deployment`.

### Hallazgo 6.1 — La aparamenta blindada tiene un costo de intervención documentado

En una patente concedida sobre aparamenta blindada con interruptor extraíble se
establece, como problema de partida, que

> *«If the circuit breaker of a conventional GIS requires service or inspection, it is
> necessary to interrupt the power supply and evacuate the insulating gas from the
> sealed container»*

Es decir: inspeccionar por dentro cuesta corte de servicio más recuperación y
reposición del gas aislante.

- **Clase:** hecho técnico establecido en el fondo de una patente concedida.
  **Nivel:** A como documento.
- **Fuente:** patente US 8717742, aparamenta blindada con unidad de interruptor
  extraíble. https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8717742

### Hallazgo 6.2 — Lo que existe hoy es monitoreo, no inspección interna

La práctica actual se apoya en medición de densidad y de descomposición del gas
aislante, y en descargas parciales por vía eléctrica y acústica, es decir en
diagnóstico **desde fuera** del recinto. La inspección visual sigue asociada al
desarmado.

- **Clase:** hechos de proveedores de instrumentación y literatura técnica.
  **Nivel:** B–C.
- **Fuentes:** https://www.omicronenergy.com/en/application/online-monitoring-and-testing/gas-insulated-switchgear-gis-testing/ ·
  https://cambridge-sensotec.co.uk/wp-content/uploads/2024/08/GIS-monitoring-of-SF6-IET-2024.pdf

### Hallazgo 6.3 — No se identificó robot de inspección interna de aparamenta blindada

**No se identificó competencia** después de las dos consultas listadas. Es un resultado
débil: una sola pasada de búsqueda, sin bases de patentes en japonés, chino ni coreano,
que es exactamente donde el informe advierte que pueden estar los desarrollos no
indexados en inglés. **Queda como pendiente de verificación, no como whitespace.**

::: inferencia de ingeniería
Aunque no exista producto, la física acota el valor: el robot igual exige recinto
desenergizado y gas evacuado, porque no puede operar dentro del aislante presurizado en
servicio. El ahorro no sería evitar la parada, sino evitar el **desarmado sucesivo de
cámaras** para llegar a un punto concreto. Ese diferencial debe cuantificarse con una
utility antes de considerarlo una oportunidad.
:::

### Hallazgo 6.4 — Túneles y canaletas de cables: prior art abundante

Existe una literatura y un cuerpo de patentes considerable, sobre todo de origen chino,
para robots de inspección de túneles y canaletas de cables: orugas dobles con cámara,
sensores de temperatura, humedad y gases, imagen térmica, navegación con mapeo
simultáneo, y trabajos publicados desde 2008 hasta la actualidad. También hay patente
estadounidense reciente sobre robot para canaleta de cables.

- **Clase:** patentes y literatura revisada. **Nivel:** A–B.
- **Fuentes:** https://patents.google.com/patent/CN202217963U/en ·
  https://www.mdpi.com/2075-1702/10/11/1011 ·
  https://ieeexplore.ieee.org/document/8521077 ·
  patente US 11731280, robot de inspección de canaleta de cables.
- **Por qué importa:** el espacio adyacente al candidato C ya está poblado de prior
  art. Refuerza que el valor del candidato C, si existe, está en el **vault** con
  cables energizados y sus requisitos de seguridad, no en recorrer un túnel con una
  cámara.

### Conclusión preliminar del lote 6

**Un candidato posible pero no confirmado, y una advertencia para el candidato C.**

La inspección interna de aparamenta blindada reúne un costo de intervención alto y
documentado y ninguna solución robótica identificada, pero el hallazgo es demasiado
débil para promoverlo: falta búsqueda de patentes en asiático y falta cuantificar qué
parte del costo se evita realmente. Se registra como **línea a investigar**, con las
consultas concretas anotadas.

Para túneles y canaletas de cables la conclusión es la opuesta: prior art abundante,
sin espacio para un producto nuevo genérico.
