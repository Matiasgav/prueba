# Brief de investigación para Claude Code
## Mapa exhaustivo de oportunidades de robots de inspección industrial para generación y utilities
**Idioma del informe final:** español  
**Fecha de corte inicial:** 31 de agosto de 2026  
**Objetivo de salida:** informe profesional HTML autocontenido, con rigor de *state of the art* y análisis de negocio, comparable en disciplina al informe previo de Wedge Tightness Testing (WTT).

---

# 0. Tu misión

Actuá como un equipo combinado de:

- ingeniero senior de robótica de inspección;
- especialista en NDE/NDT;
- analista de mercado industrial B2B;
- analista de mantenimiento de generación eléctrica;
- investigador de prior art/patentes;
- analista de producto y estrategia.

Debés producir una investigación **profunda, verificable y escéptica** sobre qué robots de inspección industrial conviene desarrollar como próximos productos.

La pregunta central NO es:

> “¿Qué robots interesantes podríamos construir?”

La pregunta es:

> **“¿En qué tareas de inspección/mantenimiento existe un dolor económico suficientemente grande, acceso suficientemente difícil y un mercado suficientemente abierto como para justificar el desarrollo de un robot industrial especializado y construir un negocio rentable alrededor de él?”**

La referencia de calidad metodológica es un *prior-art review*: identificar qué existe, qué se probó, qué falló, quién lo vende, cuánto valor crea, qué barreras quedan y dónde existe realmente un espacio defendible para un nuevo producto.

**No des por válida ninguna de las oportunidades preliminares de este brief. Verificalas desde cero y descartalas si la evidencia lo exige.**

---

# 1. Contexto del producto de referencia

Ya existe un proyecto de robot RI (*robotic inspection*) para inspección de generadores con rotor instalado. Usalo como **benchmark económico y tecnológico**, no como oportunidad nueva.

La lógica del negocio de referencia es:

- activo extremadamente caro;
- acceso difícil;
- una inspección convencional puede exigir gran desmontaje, personal especializado o una parada larga;
- el robot reduce outage, desmontaje y riesgo;
- el cliente no compra solamente “un robot”: compra **información de condición confiable** y ahorro de mantenimiento;
- el valor del servicio puede ser muy superior al costo del hardware;
- la plataforma combina locomoción, cámaras, iluminación, sensado especializado, posicionamiento, tether/comunicaciones, procesamiento y generación automática de informes.

Buscamos oportunidades con una lógica económica comparable.

## Restricciones y filosofía de producto

Al evaluar soluciones propuestas, priorizar:

1. **Calidad industrial:** hardware apto para servicio profesional repetido y alta confiabilidad.
2. **Costo/beneficio:** evitar soluciones metrológicas o robóticas innecesariamente exóticas si una arquitectura commodity logra el resultado.
3. **Componentes commodity:** preferir componentes con múltiples fabricantes y cadena de suministro amplia.
4. **Industrialización:** evaluar manufacturabilidad, mantenimiento, calibración, reemplazo de consumibles y vida útil.
5. **Argentina/Latinoamérica:** considerar disponibilidad de componentes, soporte, exportación/importación y potencial de mercado regional.
6. **Precio:** buscar precios reales cuando existan. Si el OEM no publica precio, buscar distribuidores, contratos públicos, RFP/RFQ, compras gubernamentales, integradores, mercado usado o estimaciones claramente etiquetadas.
7. **FME / recuperación:** en generación eléctrica y nuclear, un robot que queda atrapado puede ser peor que no inspeccionar. La estrategia de recuperación es parte del producto.
8. **Servicio antes que hardware:** considerar seriamente Robotics-as-a-Service / Inspection-as-a-Service si la frecuencia por activo es baja pero el ticket por inspección es alto.

---

# 2. Regla de oro: separar HECHO, DECLARACIÓN e INFERENCIA

El informe debe aplicar una disciplina estricta similar a un buen *engineering decision document*.

Para cada afirmación relevante, distinguir:

### A. Hecho verificado
Información respaldada por una fuente primaria o independiente de alta calidad.

Ejemplo:
> EPRI estima ahorros >USD 1 M y <USD 5 M por utilización para una aplicación específica de crawler de tuberías enterradas [ref].

### B. Declarado por fabricante
Una afirmación comercial del OEM/proveedor.

Ejemplo:
> TesTex declara que su IAT puede inspeccionar todos los tubos conectados a un header en 3–4 turnos [ref].

No convertir una afirmación del proveedor en validación independiente.

### C. Inferencia de ingeniería
Conclusión razonada del autor.

Debe etiquetarse explícitamente:
> **Inferencia de ingeniería:** ...

### D. Estimación comercial
Cálculo propio de TAM, ticket, ahorro o volumen.

Debe mostrar:
- fórmula;
- supuestos;
- rango;
- fuentes de cada entrada;
- sensibilidad.

Nunca presentar una estimación propia como dato publicado.

---

# 3. Jerarquía de evidencia

Usar y mostrar una clasificación consistente.

## Nivel A — máxima prioridad
- EPRI
- DOE / NRC / IAEA / EIA / FERC / NERC
- IEEE / IEC / ASME / API / NACE/AMPP
- CIGRE
- documentos oficiales de utilities
- papers revisados por pares
- patentes originales
- documentación técnica oficial del fabricante
- licitaciones/RFP/contratos oficiales

## Nivel B
- proceedings de congresos
- tesis
- informes institucionales
- presentaciones técnicas EPRI/OEM
- casos técnicos de utilities
- publicaciones de asociaciones industriales serias (HRSG Forum/CCJ, etc.)

## Nivel C
- páginas de proveedores de servicios
- casos comerciales
- notas técnicas secundarias
- prensa especializada

## Nivel D
- agregadores de contratos
- blogs
- ResearchGate/Scribd
- notas de marketing de terceros

Nivel D solamente debe servir para **descubrir la fuente primaria**. No usarlo como evidencia final si puede localizarse el original.

---

# 4. Reglas de verificación obligatorias

1. **Una patente demuestra divulgación, no funcionamiento comercial.**
   - verificar familia;
   - titular;
   - prioridad;
   - legal status;
   - expiración/abandono cuando sea relevante.

2. **Un prototipo universitario no es un producto.**

3. **Un producto anunciado no equivale a despliegue de campo.**
   Buscar:
   - clientes;
   - sitios;
   - fechas;
   - cantidad de inspecciones;
   - evidencia de repetición.

4. **Una reducción de costos publicada por el fabricante debe identificarse como tal.**

5. **No usar market reports opacos** (“market size USD X billion”) como base principal.

6. Si no existe precio:
   - escribir “precio no publicado”;
   - luego buscar contratos/RFPs/distribuidores;
   - no inventar.

7. Si no hay evidencia de competencia:
   - escribir “no se identificó competencia después de las búsquedas X/Y/Z”;
   - no escribir “no existe competencia”.

8. Buscar productos **actuales, discontinuados, adquiridos y fallidos**.

9. Buscar en inglés y, cuando corresponda, también:
   - alemán;
   - japonés;
   - chino;
   - coreano;
   - francés;
   - español/portugués.

   Empresas importantes pueden no estar bien indexadas en búsquedas en inglés.

10. Para cada oportunidad hacer al menos:
   - búsquedas EPRI por activo;
   - búsquedas EPRI por “robot/robotic/remote inspection/automation”;
   - Google/web general;
   - Google Patents/WIPO/Espacenet;
   - OEMs;
   - utilities;
   - papers IEEE/ASME/Elsevier/Springer;
   - RFP/RFQ/contratos;
   - videos técnicos sólo como evidencia suplementaria.

---

# 5. Error que este estudio debe evitar

No queremos descubrir dentro de dos años que:

- EPRI ya investigó exactamente el problema;
- un OEM ya patentó la arquitectura;
- existe un producto comercial establecido;
- el cliente ya compra ese servicio;
- hubo un programa de desarrollo que fracasó por una razón física conocida.

Por eso, **para cada candidato debés hacer una búsqueda histórica además de una búsqueda actual**.

Construí una línea temporal:

> problema identificado → primer prototipo → investigación EPRI → patentes → primeros despliegues → productos comerciales → estado 2026.

Las fuentes negativas son especialmente valiosas:
- productos discontinuados;
- programas abandonados;
- papers con resultados insuficientes;
- robots que quedaron atascados;
- herramientas que no entraron;
- FME;
- fallas de tether;
- NDE que no logró sensibilidad;
- costos que destruyeron el business case.

---

# 6. Fuentes EPRI que DEBÉS recorrer antes de concluir

No limitarte a estas. Son un paquete inicial verificado.

## 6.1 Mapa cross-sector de robótica EPRI

### EPRI 3002023899
**Robotic Process Automation for Nuclear Power Plants: Evaluation of Near-Term Opportunities**  
Junio 2022  
https://restservice.epri.com/publicdownload/000000003002023899/0/Product

Usarlo para:
- lista de tareas de alto valor;
- horas-hombre;
- gaps tecnológicos;
- diferencia entre teleoperación, autonomía e inspección+mantenimiento;
- criterio de selección de tareas.

Este documento identifica, entre otras, oportunidades en:
- buried service water piping;
- component supports;
- cooling-water intake/discharge structures;
- isophase bus duct;
- 3D radiation mapping;
- containment leak detection;
- reactor head studs/stud holes;
- water storage tanks;
- dry fuel casks;
- operator rounds;
- fire protection;
- steam-generator tubing.

**No asumir que todas son buenos productos nuevos. Varias ya son mercados maduros.**

### EPRI 3002025693
**Program on Technology Innovation: Landscape of Automation in Nuclear Power Plants**  
https://restservice.epri.com/publicdownload/000000003002025693/0/Product

Buscar especialmente la conclusión de negocio sobre:
- robots custom para tareas de alto valor y baja frecuencia;
- uso frecuente de vendors externos;
- costo/tiempo de desarrollar plataformas custom.

Esto puede respaldar un modelo de **servicio especializado**.

### EPRI Unmanned Mobile Technologies Collaboration Group
Product Index:  
https://transmission.epri.com/p37_substations/robotics/mobiletechgrp/products/

Webcasts / actividad actual:  
https://transmission.epri.com/p37_substations/robotics/mobiletechgrp/webcasts/

Recorrer **todo el índice**, no sólo los títulos que parecen obvios.

### EPRI Tech Portal
https://techportal.epri.com/

Usarlo como herramienta de descubrimiento; luego ir a fuentes primarias.

### EPRI Generation reports / Digital Transformation
https://dx-wiki.epri.com/Generation_Reports

Buscar explícitamente:
- robots;
- inspection;
- remote inspection;
- crawlers;
- vine robots;
- confined spaces;
- NDE/NDT;
- autonomous inspection.

---

# 7. Candidatos que deben investigarse EN PROFUNDIDAD

La lista siguiente es un punto de partida, no una conclusión.

---

## CANDIDATO A — Robot para Isolated Phase Bus / Isophase Bus (IPB)

### Hipótesis
Puede ser la mejor extensión inmediata del RI por:
- mismo tipo de cliente;
- inspección durante outages;
- espacio confinado;
- reducción de scaffolding/man-entry;
- alta reutilización de cámaras, tether, iluminación, software de mapping y arquitectura de crawler.

### Fuentes EPRI iniciales

#### MTA-MA-029
**Reduce Inspection Cost for Isophase Bus Duct Using Robotic Crawler**  
https://nuclearplantmod.epri.com/MTA-MA-029

Datos verificados que debés revisar y citar en contexto:
- experiencia reportada de una utility con costo de vendor de aproximadamente **USD 100.000 por implementación**;
- inspección en **menos de un día**;
- EPRI reporta reducción aproximada de **10×** frente a la inspección manual en un caso;
- payback inmediato según SWEEP;
- tecnología comercialmente disponible;
- riesgos de crawler/tool failure;
- una gran parte del ahorro proviene de evitar scaffolding y acceso humano.

No generalizar el USD 100k a todo el mercado sin evidencia.

#### EPRI 1015057
**Isolated Phase Bus Maintenance Guide**  
https://restservice.epri.com/publicdownload/000000000001015057/0/Product

Buscar:
- frecuencia típica de inspección;
- defectos;
- accesos;
- figuras de robotic walkers;
- mantenimiento recomendado;
- mediciones eléctricas.

#### EPRI 3002023899
Investigar la idea de evolucionar desde “cámara crawler” a:
- limpieza;
- transporte/remoción de FOD;
- verificación de torque;
- resistance testing;
- manipulación.

### Competidores/soluciones a investigar

No limitarse a:
- Trident NGS — https://www.tridentngs.com/
- Electrical Builders Inc.
- MidStates Energy
- nVent
- GE Vernova / Siemens Energy / Hitachi Energy, si ofrecen servicios
- empresas nucleares especializadas
- sistemas coreanos/japoneses/chinos
- trabajos de Beihang y otras universidades.

Buscar:
- nombre exacto del crawler;
- fabricante;
- locomoción;
- dimensiones;
- tether/wireless;
- cómo pasa aisladores/supports;
- recuperación;
- sensores;
- limpieza;
- si mide torque o resistencia;
- precio de servicio;
- clientes;
- frecuencia de inspección.

### Pregunta estratégica
**¿Existe espacio para un sistema “inspection + maintenance” y no solamente otro crawler con cámara?**

---

## CANDIDATO B — Robot para HRSG: headers, tube-to-header welds y tubos

### Fuente EPRI fundamental

#### EPRI 1017635
**Study for Snake Robot Technology for Inspection of Headers and Tubes in Heat Recovery Steam Generators**  
Final Report, 2009  
https://restservice.epri.com/publicdownload/000000000001017635/0/Product

Leer COMPLETO.

Extraer:
- por qué la inspección convencional no llega a tubos interiores;
- geometrías;
- diámetros;
- longitudes;
- tipos de HRSG;
- puntos de acceso;
- modalidades de inspección;
- qué conceptos de snake robot analizaron;
- qué demostraron;
- qué no resolvieron;
- por qué no se comercializó directamente ese concepto;
- NDE propuesto.

### Competidor crítico: TesTex

#### TesTex HRSG tools
https://testex-ndt.com/services/hrsg/

#### TesTex IAT
https://testex-ndt.com/products/iat-internal-access-tool-for-hrsg-inspections/

Información declarada por TesTex a verificar:
- **Internal Access Tool (IAT)** es un crawler colocado dentro del header;
- puede entrar por end cap o versión modular por un agujero de aproximadamente 8";
- empuja una sonda RFET + cámara por los tubos;
- remote control;
- puede inspeccionar todos los tubos de un header en 3–4 shifts;
- tiene despliegues con múltiples utilities;
- el sitio declara 100% tube coverage dentro de las condiciones de aplicación.

#### TesTex “Claw”
https://testex-ndt.com/products/claw-bfet-inspection-tool/

Investigar:
- BFET;
- cobertura real;
- 200 welds/shift declarado;
- diámetros;
- accesibilidad.

### Investigación adicional obligatoria
Buscar:
- patents TesTex;
- EPRI/TesTex joint development;
- Combined Cycle Journal / HRSG Forum;
- GE Vernova;
- Siemens Energy;
- Nooter/Eriksen;
- Vogt;
- Alstom/Altrad;
- EDF;
- MISTRAS;
- Eddyfi;
- Waygate/Baker Hughes;
- Olympus/Evident;
- robots académicos para boiler tubes;
- tube crawlers magnéticos;
- snake robots;
- continuum robots.

### Pregunta estratégica
No asumir mercado vacío. Determinar:

**¿Qué parte del problema NO resuelve hoy TesTex?**

Posibles hipótesis a validar:
- menor access hole;
- no retirar end cap;
- más tipos de headers;
- automatic tube indexing;
- mayor alcance;
- mejor localization;
- un solo despliegue para weld + tube wall;
- NDE cuantitativo superior;
- mejor autonomía;
- depósitos/bloqueos;
- inspección + limpieza/reparación.

Si no aparece un gap defendible, bajar el ranking.

---

## CANDIDATO C — Robot para underground transmission vaults / HV cable manholes

### EPRI histórico + actual

#### EPRI 3002000878
**Underground Transmission Vault Inspection Using Robotic Techniques**  
2013  
Localizar en EPRI y descargar si está público.

#### EPRI 3002032834
**Underground Transmission Vault Inspection Using Robotic Techniques — 2025 Update**

Página de research updates:
https://transmission.epri.com/p36_underground/public/p36001_design_construction/research_updates/

Hecho crítico:
EPRI continúa este trabajo en **2026 y 2027** y declara que:
- se busca mejorar seguridad de trabajadores;
- reducir requisitos de circuit outage;
- conceptos/prototipos robóticos fueron demostrados en laboratorios EPRI y sitios de utilities.

#### Applications
https://transmission.epri.com/p36_underground/public/p36_applications/

La página enumera:
> Robotic Inspections of Underground Vaults — Prototype Development, Laboratory Tests, Demo in Planning.

#### Contactos EPRI actuales
https://transmission.epri.com/p36_underground/leads/

Verificar antes de usar:
- David Kummer — Robotic Inspection;
- Tom Zhao — Underground Transmission Program Manager.

### Proyecto complementario actual
Buscar “Extruded Cable Manhole Inspections” en los Collaborative Supplemental Projects 2025/2026 de EPRI.

Investigar la arquitectura:
- inspección desde superficie;
- energized cable;
- IR;
- cámara;
- gas sensing;
- mechanical arm;
- PD/acoustic/ultrasonic si aplica.

### Competencia
Buscar en profundidad:
- Osmose;
- Con Edison;
- National Grid;
- SCE;
- PG&E;
- NYPA;
- Duke;
- Dominion;
- Entergy;
- Hydro-Québec;
- empresas de sewer crawlers adaptados;
- drones confined-space;
- Boston Dynamics/ANYbotics en vaults;
- integradores.

### Pregunta estratégica
Este candidato puede estar **menos maduro** que IPB o buried-pipe NDE.

Determinar:
- cantidad de vaults;
- frecuencia de inspección;
- necesidad de de-energización;
- costo actual;
- safety/confined-space burden;
- si puede venderse como servicio recurrente;
- ticket razonable;
- requirements de aislamiento eléctrico y gas.

---

## CANDIDATO D — Crawler NDE para piping enterrado / inaccesible

### EPRI MTA-MA-017
https://nuclearplantmod.epri.com/MTA-MA-017

Datos EPRI iniciales:
- inspección desde un único acceso;
- puede evitar excavación;
- EMAT permite determinados exámenes volumétricos sin remover coating;
- EPRI SWEEP:
  - implementation cost < USD 1 M;
  - ahorro > USD 1 M y < USD 5 M por utilización;
  - payback inmediato/<1 año;
  - tecnología ya comercial en nuclear.

### EPRI 1025272
**Compilation of Lessons Learned on Buried and Underground Piping**  
https://restservice.epri.com/publicdownload/000000000001025272/0/Product

Buscar:
- por qué conventional ILI no funciona bien en nuclear;
- falta de launcher/receiver;
- elbows;
- tees;
- verticals;
- coatings;
- diámetros;
- water-filled/dry;
- FME/recovery.

### Competidor crítico: Diakont
https://diakont.com/case-studies/nuclear-solutions/first-buried-piping-in-line-inspection/

También buscar:
- Structural Integrity Associates;
- Westinghouse;
- Framatome;
- Eddyfi/Inuktun;
- Waygate;
- Gecko Robotics;
- MISTRAS;
- ROSEN;
- NDT Global;
- Eddyfi VersaTrax;
- pipe inspection service companies.

### Pregunta estratégica
EPRI ya lo clasifica como comercialmente implementado.

Por lo tanto:
**no recomendar un crawler genérico de tuberías.**

Sólo recomendar si se identifica white space concreto:
- small diameter;
- 1D elbow;
- tees;
- reducers;
- vertical;
- wet/dry transition;
- protected/coated pipe;
- inspection + repair;
- deployability without cutting;
- smaller access;
- low-cost service outside nuclear.

---

## CANDIDATO E — Robot para dry spent-fuel storage casks

### EPRI
Buscar:
**3002008234 — Dry Canister Storage System Inspection and Robotic Delivery System Development**

EPRI Journal:
https://eprijournal.com/wall-climbing-robots-inspect-nuclear-storage-casks/

Datos iniciales:
- gaps pequeños;
- cámara + ECA + EMAT + radiation/temp en ciertas configuraciones;
- múltiples field tests;
- EPRI describe reducción de costos muy alta frente a métodos con heavy lift/movimiento de canister.

### Competidor crítico
**Robotic Technologies of Tennessee (RTT)**  
https://www.robotictechtn.com/

El fabricante declara que nuclear sites usan sus plataformas para Dry Cask Storage inspection.

Buscar:
- robots exactos;
- EPRI/DOE programs;
- SONGS;
- Holtec;
- Orano;
- NAC;
- DOE;
- NRC requirements;
- Penn State/PRINSE;
- radiation qualification;
- patent landscape.

### Pregunta estratégica
Alto valor, pero:
- mercado nuclear limitado;
- qualification;
- FME;
- radiation;
- incumbent.

Compararlo rigurosamente contra oportunidades menos reguladas.

---

## CANDIDATO F — ROV/AUV/crawler para penstocks y túneles hidro

### EPRI TR-113584-V7 / 1007576
**ROV Technology: Applications and Advancements at Hydro Facilities**  
https://restservice.epri.com/publicdownload/000000000001007576/0/Product

Extraer:
- tunnel/penstock;
- visual;
- sonar;
- UT thickness;
- tether limitations;
- alcance;
- recuperación;
- case studies;
- ahorro de outage/dewatering.

Buscar además:
**3002011682 — Autonomous Underwater Vehicles for Tunnel and Penstock Inspection**

Y proyectos actuales del EPRI Unmanned Mobile Technologies Collaboration Group.

### Competencia
Investigar:
- Deep Trekker;
- VideoRay;
- Eddyfi/Inuktun;
- Deep Ocean Engineering;
- Saab Seaeye;
- Blue Robotics integrators;
- utility-owned custom ROVs;
- Hydro-Québec;
- Voith;
- Andritz;
- GE Vernova Hydro;
- specialized tunnel inspection vendors.

### Pregunta estratégica
ROV visual puede ser maduro.

El posible gap puede estar en:
- navegación autónoma en km;
- localization sin GPS;
- wall thickness mapping;
- close-contact NDE;
- recovery guaranteed;
- turbidity;
- high flow;
- long tether.

---

## CANDIDATO G — Vine / everting robot para equipos de planta

### EPRI
Buscar y verificar:
**3002032954 — Everting Vine Robots for Plant Equipment Inspection – Technology Review and Feasibility Study**

Catálogo:
https://dx-wiki.epri.com/Generation_Reports

No asumir resultados no públicos.

### Fuentes externas iniciales
- IEEE Robotics & Automation Magazine — large-scale vine robots for industrial inspection.
- UCSB/Bechtel capstone.
- Stanford vine robots.
- Trellis Robotics.
- IvySpec.

### Pregunta estratégica
“Vine robot” es una tecnología, NO un mercado.

Identificar un activo concreto donde:
- crawler no pasa;
- borescope no alcanza;
- desmontaje es costoso;
- el vine pueda llevar NDE útil.

Ejemplos a evaluar:
- ductos de aire/gases;
- HRSG;
- piping complejo;
- turbine/boiler spaces;
- cable ducts;
- confined equipment.

---

# 8. Mercados que deben analizarse como “posiblemente demasiado maduros”

No descartarlos sin investigar, pero exigir evidencia de white space.

## 8.1 Transformer swimming robot
Benchmark:
**ABB TXplore**

Buscar fuentes ABB oficiales y EPRI.

ABB ha publicado:
- inspección en menos de un día;
- eliminación de tareas de drenaje/procesamiento de aceite;
- reducción de costos de hasta aproximadamente 50% en comunicaciones de fabricante/casos.

Pregunta:
¿hay algo que TXplore no haga y tenga mercado independiente de ABB?

## 8.2 Substation patrol robots
EPRI trabaja con plataformas comerciales, incluyendo Spot en ciertos proyectos.

Buscar:
https://transmission.epri.com/p37_substations/public/robotics/substation_robot_application/

Hipótesis:
el valor puede estar más en **sensor payload + analytics** que en fabricar otro cuadrúpedo/UGV.

## 8.3 Transmission-line crawling robots
Investigar:
- EPRI Ti;
- Hydro-Québec LineScout / LineROVer;
- HiBot Expliner;
- drones modernos.

Determinar si los drones hicieron económicamente obsoleto el crawler para visual routine inspection.

## 8.4 Tank inspection robots
Investigar:
- Square Robot;
- Newton Labs;
- Eddyfi;
- ROVs.

Probablemente mercado maduro.

## 8.5 Reactor internals / steam-generator tube robotics
Investigar:
- Framatome;
- Westinghouse;
- AREVA SUSI;
- KHNP/KEPRI;
- SG manipulators.

Es un mercado de altísimo valor, pero probablemente muy maduro y regulado.

---

# 9. Buscar oportunidades QUE NO FIGURAN en esta lista

Esto es obligatorio.

Hacé un barrido independiente por:

## EPRI
- Generation
- Nuclear
- Transmission
- Distribution
- Hydropower
- Fossil/combined-cycle
- Wind
- Solar
- substations
- underground transmission
- plant modernization
- NDE
- digital transformation
- robotic collaboration groups

## Problemas físicos
Buscar combinaciones de:
- confined space;
- inaccessible inspection;
- rotor-in-place;
- no disassembly;
- no scaffolding;
- no excavation;
- no draining;
- no diving;
- no de-energization;
- in-situ;
- online inspection;
- internal inspection;
- robotic NDE;
- remote NDE;
- autonomous inspection;
- inspection + repair;
- inspection + cleaning;
- FOD retrieval.

## Otros activos a evaluar
No asumir que son buenos, pero verificarlos:
- air-cooled condensers;
- condensers;
- cooling towers;
- boiler waterwalls;
- boiler headers;
- furnace internals;
- gas turbine exhaust/combustion areas;
- steam turbine internals;
- wind turbine blades/towers;
- offshore wind monopiles;
- dams;
- spillways;
- intake gates;
- large valves;
- heat exchangers;
- stacks/chimneys;
- industrial furnaces;
- petrochemical vessels/pipes;
- mining assets si la tecnología es transferible.

Queremos descubrir **candidatos nuevos** si la evidencia los hace mejores.

---

# 10. Para CADA robot/candidato usar una ficha fija

Esto es obligatorio para poder comparar.

## [Nombre del candidato]

### 1. Activo y problema
- qué se inspecciona;
- mecanismo de falla;
- por qué importa.

### 2. Cómo se inspecciona hoy
- rotor-out/disassembly/scaffolding/diver/human entry/etc.;
- frecuencia;
- duración;
- personal;
- outage;
- riesgos.

### 3. Pain económico verificable
- costo directo;
- costo de outage;
- costo de acceso;
- horas-hombre;
- pérdida por falla;
- ejemplos reales.

Separar:
- datos publicados;
- estimaciones.

### 4. Propuesta de robot
Definir funcionalmente:
- locomoción;
- dimensiones aproximadas;
- sensores;
- NDE;
- tether/wireless;
- autonomía;
- mapping/localization;
- manipulación;
- recovery.

No diseñar con detalle todavía; definir requirements.

### 5. Qué valor crea
- evita qué operación;
- reduce cuánto tiempo;
- aumenta cobertura;
- mejora confiabilidad;
- disminuye riesgo.

### 6. Robots/productos existentes
Tabla obligatoria:

| Producto | Fabricante | Año | Estado 2026 | Locomoción | Payload/NDE | Dimensiones | Despliegues | Precio/servicio | Fuente |
|---|---|---:|---|---|---|---|---|---|---|

No dejar fuera:
- products;
- service-only systems;
- prototypes;
- discontinued;
- patents.

### 7. Cómo resolvieron los existentes el problema
Analizar ingeniería:
- adhesion;
- wheels/tracks/magnetic;
- snake/continuum;
- tether;
- power;
- sensor coupling;
- NDE contact;
- crossing obstacles;
- alignment;
- recovery;
- FME.

### 8. Qué NO resuelven
Identificar whitespace real.

### 9. Mercado y madurez
Usar una escala explicada:

- **M0:** sólo papers/conceptos
- **M1:** prototipos de laboratorio
- **M2:** demostración industrial aislada
- **M3:** servicios comerciales iniciales
- **M4:** múltiples proveedores/despliegues
- **M5:** mercado maduro/commodity

No confundir TRL con madurez comercial.

### 10. Barreras técnicas
- geometría;
- temperatura;
- radiación;
- EMI;
- fluidos;
- suciedad;
- corrosión;
- tether;
- adhesion;
- battery;
- sensing;
- NDE calibration.

### 11. Riesgo de FME/atasco y recuperación
Proponer filosofía fail-safe.

### 12. Regulación/calificación
- nuclear;
- NDE qualification;
- electrical HV;
- confined-space;
- pressure boundary;
- ASME/API/etc.

### 13. Patentes/IP
- principales familias;
- propietarios;
- estado legal;
- riesgo de bloqueo;
- posibles áreas libres.

### 14. Desarrollo estimado
Separar:
- platform;
- sensor payload;
- NDE;
- software;
- qualification;
- field validation.

Dar rango y justificar.

### 15. Business model
Comparar:
- venta de robot;
- lease;
- service;
- per-inspection;
- annual contract;
- data/analytics subscription.

### 16. Cliente y comprador
- utility;
- OEM;
- outage contractor;
- NDE company;
- insurance;
- asset owner.

Identificar quién firma el PO.

### 17. Frecuencia de compra/inspección
Fundamentar.

### 18. Market size
Calcular solamente si hay datos suficientes.

Separar:
- global;
- USA;
- Latinoamérica;
- Argentina.

### 19. Precio/ticket
Usar:
- precios publicados;
- RFP;
- contratos;
- quotes;
- comparables.

No inventar.

### 20. Reutilización de nuestra plataforma RI
Puntuar:
- locomoción;
- Kria/compute;
- cámaras;
- iluminación;
- tether;
- FPGA;
- encoders;
- software;
- mapping;
- reporting;
- safety architecture.

### 21. Moat posible
- mecánica;
- NDE;
- dataset;
- calibration;
- software;
- qualification;
- workflow/service;
- patents.

### 22. Go / No-Go
Conclusión breve y contundente.

### 23. Confianza
- Alta;
- Media;
- Baja.

Explicar qué dato falta.

---

# 11. Tamaño de mercado: metodología obligatoria

No usar como base reportes genéricos de “robot inspection market”.

Construir **bottom-up**.

## Fuentes preferidas

### USA
- EIA;
- NRC;
- DOE;
- FERC;
- NERC;
- utilities;
- EPRI.

### Nuclear global
- IAEA PRIS;
- WNA sólo como secundaria.

### Argentina
- CAMMESA;
- Secretaría de Energía;
- ENRE;
- Nucleoeléctrica;
- Transener;
- empresas generadoras;
- operadores de ciclo combinado/hidro.

### Latinoamérica
- ministerios/ISO/operadores eléctricos;
- utilities;
- OLADE;
- CIER;
- bases públicas verificables.

## Cálculo sugerido

Por oportunidad:

`Activos addressables × inspecciones/año × ticket de servicio = TAM de servicios`

Mostrar:
- low case;
- base case;
- high case.

Si falta información crítica, NO fabricar el TAM.

---

# 12. Economía del cliente

El análisis debe mirar la decisión desde el cliente.

Construir cuando sea posible:

`Valor creado = costo convencional evitado + outage evitado + riesgo evitado + cobertura adicional - costo de robotización`

Separar los componentes.

No asignar valor monetario arbitrario a seguridad.

Buscar ejemplos reales de:
- días de outage;
- scaffolding;
- excavation;
- dewatering;
- tank draining;
- rotor pull;
- human confined-space entry;
- dive operation;
- heavy-lift operation.

---

# 13. Ranking: NO usar una puntuación arbitraria sin explicación

Crear al menos dos rankings.

## Ranking A — mejor próximo producto / bajo riesgo
Pesos iniciales sugeridos:
- dolor económico / avoided cost: 20%
- competencia / whitespace: 15%
- reutilización RI: 15%
- factibilidad técnica: 15%
- ticket/margen: 10%
- frecuencia/recurrencia: 10%
- tamaño de mercado: 10%
- overlap de clientes/canal comercial: 5%

## Ranking B — mayor moat / upside a largo plazo
- whitespace/IP: 20%
- pain económico: 20%
- barrera tecnológica defendible: 20%
- mercado: 15%
- ticket: 10%
- recurrencia: 5%
- reutilización RI: 5%
- regulatory burden inverso: 5%

Claude puede cambiar los pesos si lo justifica.

### Importante
Mostrar una **sensitivity analysis**:
¿cambia el ganador si se modifica ±20% el peso de competencia, desarrollo o mercado?

Los scores son **síntesis de ingeniería/comercial**, no datos medidos. Etiquetarlos como tales.

---

# 14. Gráficos requeridos

Crear gráficos sólo si agregan información.

Recomendados:

1. **Value vs market maturity**
   - X: madurez/competencia
   - Y: valor económico para cliente
   - tamaño de burbuja: mercado estimado (sólo si es defendible)

2. **Reuse from RI vs development difficulty**

3. **Opportunity score comparison**

4. **Timeline of prior art / commercialization**
   Para los top 3.

5. **Customer economics**
   Convencional vs robotic cuando existan números reales.

6. **Market landscape**
   Número/cluster de proveedores por oportunidad.

Toda gráfica debe:
- indicar fuentes;
- diferenciar datos de scores;
- no inventar precisión numérica.

---

# 15. Imágenes en el HTML

Usar imágenes cuando ayuden a entender:

- geometría del activo;
- robot existente;
- mecanismo de acceso;
- herramienta NDE;
- arquitectura propuesta.

## Preferencia
1. EPRI;
2. OEM/fabricante;
3. utility/case study;
4. paper;
5. patente.

Evitar stock photos decorativas.

Cada imagen debe tener:
- caption;
- fabricante/sistema;
- fuente;
- URL;
- fecha de consulta.

Si copyright/licencia no permite embebido confiable:
- no copiar;
- usar enlace o crear un esquema original claramente marcado como **“Esquema del autor”**.

No hotlinkear imágenes frágiles si el HTML debe quedar autocontenido. Si es legal/técnicamente apropiado, guardar assets locales en `/assets`.

---

# 16. Prior-art y patentes

Para los **Top 5** hacer búsqueda de patentes formal.

Buscar:
- Google Patents;
- Espacenet;
- WIPO Patentscope;
- USPTO.

Keywords combinadas:
- asset + robotic inspection
- asset + crawler
- asset + remote inspection
- asset + NDE
- asset + wall climbing
- asset + snake robot
- asset + inspection vehicle
- asset + manipulator

Registrar:

| Familia | Prioridad | Titular | Qué reivindica | Estado | Riesgo para nosotros |
|---|---|---|---|---|---|

No hacer una opinión legal de FTO; llamarlo **“screening preliminar de IP”**.

---

# 17. Investigación de competidores

Para cada top opportunity buscar exhaustivamente:

### OEM de robot
¿Quién fabrica el hardware?

### NDE vendor
¿Quién fabrica/posee el sensor?

### Service company
¿Quién realmente vende la inspección?

### Integrator
¿Quién combina ambas cosas?

### Utility-developed technology
¿La utility desarrolló internamente una solución?

### University spin-off
¿Existe un spin-off comercial?

### Acquisition history
¿El producto cambió de dueño/nombre?

### Current status
A fecha 2026:
- active;
- discontinued;
- acquired;
- no longer marketed;
- unclear.

Buscar además:
- LinkedIn sólo como lead;
- Wayback / archived brochures si un producto desapareció;
- patents;
- trade show proceedings;
- RFP award documents.

---

# 18. RFPs y contratos: fuente de verdad comercial

Buscar RFP/RFQ/bids/awards reales para cada top opportunity.

Términos:
- “inspection services”
- “robotic inspection”
- “isophase bus”
- “HRSG inspection”
- “vault inspection”
- “buried piping”
- “penstock inspection”
- “dry cask inspection”
- “crawler”
- “remote visual inspection”

Preferir portales oficiales:
- utility procurement;
- state procurement;
- federal procurement;
- municipal utilities;
- nuclear procurement si es público.

Extraer:
- scope;
- frecuencia;
- requisitos;
- duración;
- award amount si aparece;
- vendor ganador.

Esto es mucho más útil que un “market size report”.

---

# 19. Argentina y Latinoamérica

Para los **Top 3** incluir capítulo específico.

Preguntas:

1. ¿Cuántos activos existen en Argentina?
2. ¿Quiénes los operan?
3. ¿Quién hoy hace la inspección?
4. ¿Contratan OEM internacional o servicio local?
5. ¿El robot podría prestar servicio regional desde Argentina?
6. ¿Qué importación/calibración requiere?
7. ¿Hay integradores/NDE partners locales?
8. ¿Hay centrales con equipos GE/Siemens/Mitsubishi/ABB donde el canal comercial sea similar al RI?
9. ¿Qué mercados vecinos son naturales?
   - Brasil
   - Chile
   - Uruguay
   - Paraguay
   - Perú
   - Colombia
   - México

No inventar cantidades. Usar CAMMESA/operadores/utilities.

---

# 20. Investigación de costos de desarrollo

Para cada shortlist estimar separadamente:

- diseño mecánico;
- prototipo;
- electrónica;
- sensors/NDE;
- tether/power;
- software/control;
- autonomous navigation;
- data/reporting;
- test rig;
- mock-up;
- field qualification;
- certification;
- tooling/manufacturing.

Rangos amplios son preferibles a falsa precisión.

Diferenciar:
- costo de construir 1 prototipo;
- NRE para industrialización;
- costo unitario aproximado;
- costo de field service kit.

Buscar precios reales de componentes críticos cuando sea posible.

---

# 21. Estructura del informe HTML final

## Portada
**Oportunidades de Robótica de Inspección Industrial para Generación y Utilities**  
*State of the art, landscape competitivo y evaluación de negocio — 2026*

## Executive Summary
Máximo ~3 páginas:
- top 3;
- por qué;
- qué NO desarrollar;
- biggest unknowns;
- decisión recomendada.

## 1. Objetivo y alcance

## 2. Metodología y evidencia
- jerarquía;
- search coverage;
- limitaciones.

## 3. Qué hace atractivo un negocio de inspection robotics
- economics;
- outage;
- service model;
- FME;
- qualification.

## 4. Mapa completo de oportunidades
Taxonomía por activo/sector.

## 5. Candidate cards
Una sección completa por robot.

## 6. Competitive landscape
Tabla transversal de vendors/products.

## 7. Patent / IP landscape

## 8. Mercado
- global;
- USA;
- LATAM;
- Argentina.

## 9. Economics
- customer ROI;
- ticket;
- service model.

## 10. Comparison matrix

## 11. Rankings
- fast-follow;
- deep-tech/moat;
- sensitivity.

## 12. Top 3 — Concept briefs
Para cada uno:
- target requirements;
- MVP;
- differentiation;
- validation plan;
- 12–24 month roadmap;
- customer discovery.

## 13. Do-not-pursue-now
Explicar por qué.

## 14. Unknowns / due diligence
Lista accionable.

## 15. Conclusiones

## Anexo A — Search log
Keywords, bases y fecha.

## Anexo B — Competitor register

## Anexo C — Patent register

## Anexo D — Source register

---

# 22. Formato de referencias

Usar referencias junto a la información.

Ejemplo:

> EPRI reporta que una utility pagó aproximadamente USD 100.000 por una implementación de inspección robótica de isophase bus y que la ejecución tomó menos de un día [EPRI-MTA-029].

Al hacer click o hover debería ser fácil localizar la referencia.

Al final:

**[EPRI-MTA-029]** Electric Power Research Institute, *Reduce Inspection Cost for Isophase Bus Duct Using Robotic Crawler*, Plant Modernization Toolbox, consultado 2026-08-31. URL...

No poner una bibliografía desconectada donde resulte imposible saber qué afirmación sostiene cada fuente.

### Cada referencia debe registrar
- autor/organización;
- título;
- fecha;
- Product ID/DOI/patent;
- URL;
- fecha de acceso;
- evidence level.

---

# 23. Paquete de evidencia inicial verificado

Estas fuentes son **seeds**, no reemplazan tu investigación.

## EPRI — oportunidad y landscape
1. EPRI 3002023899 — Robotic Process Automation for Nuclear Power Plants  
   https://restservice.epri.com/publicdownload/000000003002023899/0/Product

2. EPRI Unmanned Mobile Technologies — Product Index  
   https://transmission.epri.com/p37_substations/robotics/mobiletechgrp/products/

3. EPRI underground transmission research updates  
   https://transmission.epri.com/p36_underground/public/p36001_design_construction/research_updates/

4. EPRI underground transmission applications  
   https://transmission.epri.com/p36_underground/public/p36_applications/

5. EPRI underground transmission contacts  
   https://transmission.epri.com/p36_underground/leads/

## Isophase bus
6. EPRI MTA-MA-029  
   https://nuclearplantmod.epri.com/MTA-MA-029

7. EPRI 1015057 — Isolated Phase Bus Maintenance Guide  
   https://restservice.epri.com/publicdownload/000000000001015057/0/Product

8. Trident NGS  
   https://www.tridentngs.com/

## HRSG
9. EPRI 1017635 — Study for Snake Robot Technology for Inspection of Headers and Tubes in HRSGs  
   https://restservice.epri.com/publicdownload/000000000001017635/0/Product

10. TesTex HRSG  
    https://testex-ndt.com/services/hrsg/

11. TesTex IAT  
    https://testex-ndt.com/products/iat-internal-access-tool-for-hrsg-inspections/

12. TesTex Claw  
    https://testex-ndt.com/products/claw-bfet-inspection-tool/

## Buried piping
13. EPRI MTA-MA-017  
    https://nuclearplantmod.epri.com/MTA-MA-017

14. EPRI 1025272  
    https://restservice.epri.com/publicdownload/000000000001025272/0/Product

15. Diakont — first buried-pipe inline inspection case  
    https://diakont.com/case-studies/nuclear-solutions/first-buried-piping-in-line-inspection/

## Hydro
16. EPRI 1007576 / TR-113584-V7 — ROV Technology at Hydro Facilities  
    https://restservice.epri.com/publicdownload/000000000001007576/0/Product

## Dry cask
17. EPRI Journal — wall-climbing dry cask robots  
    https://eprijournal.com/wall-climbing-robots-inspect-nuclear-storage-casks/

18. Robotic Technologies of Tennessee  
    https://www.robotictechtn.com/

## Emerging
19. EPRI Generation Reports  
    https://dx-wiki.epri.com/Generation_Reports

20. EPRI Tech Portal  
    https://techportal.epri.com/

---

# 24. Hallazgos seed que NO deben perderse

Estos hallazgos ya fueron verificados en fuentes primarias/actuales, pero debés volver a leer el contexto antes de utilizarlos.

## IPB
EPRI MTA-MA-029 informa:
- vendor-supported inspection ~USD 100k en experiencia de una utility;
- <1 día de ejecución;
- reducción de costo de aproximadamente 10× frente a método manual en ese caso;
- payback inmediato;
- commercial readiness alta.

Esto demuestra **mercado y valor**, pero también que un “camera crawler” solo ya existe.

## Buried piping
EPRI MTA-MA-017 informa:
- ahorro esperado >USD 1 M y <USD 5 M por uso;
- implementación <USD 1 M;
- payback <1 año/inmediato;
- ya comercial en nuclear.

Esto indica **gran valor pero madurez alta**.

## HRSG
EPRI 1017635 confirma que:
- ciertos tubos interiores no pueden inspeccionarse fácilmente con NDE convencional sin acceso destructivo;
- snake robotics fue estudiada para ese problema.

Pero TesTex hoy ofrece:
- IAT;
- RFET + video;
- crawler en header;
- múltiples work sites.

Por lo tanto, la oportunidad HRSG debe reevaluarse contra un incumbente real.

## Underground transmission vault
EPRI mantiene el proyecto activo en 2025–2027:
- prototipos;
- lab;
- utility demos;
- objetivo de seguridad y reducción de outage.

Esto es una señal de **problema vigente y tecnología aún en evolución**.

---

# 25. Preguntas que el informe DEBE responder al final

1. **Si tuviéramos que invertir hoy en un solo robot después del RI, ¿cuál sería?**
2. ¿Por qué un cliente pagaría por él?
3. ¿Qué costo concreto le evitamos?
4. ¿Qué ticket de servicio puede sostener?
5. ¿Cuántas oportunidades de servicio existen por año?
6. ¿Quién ya hace esto?
7. ¿Por qué nuestro producto sería mejor/diferente?
8. ¿Qué tan difícil es copiarlo?
9. ¿Qué IP puede bloquearlo?
10. ¿Qué parte del RI actual podemos reutilizar?
11. ¿Cuánto desarrollo falta?
12. ¿Cuál es el primer MVP que un cliente pagaría por probar?
13. ¿Qué validación técnica sería suficiente?
14. ¿Cuál es el principal mecanismo de fracaso?
15. ¿Qué robot NO deberíamos desarrollar aunque parezca atractivo?
16. ¿Qué oportunidad nueva apareció durante la investigación que no estaba en este brief?
17. ¿Qué información todavía no existe públicamente y requiere entrevistas?
18. ¿A qué 10 personas/organizaciones deberíamos contactar primero?

---

# 26. Customer discovery recomendado

Para los Top 3 generar una lista concreta de entrevistas.

Tipos de persona:
- generator maintenance manager;
- outage manager;
- NDE manager;
- plant manager;
- transmission cable engineer;
- HRSG engineer;
- OEM service manager;
- EPRI technical lead;
- NDE service provider;
- insurance/risk engineer cuando aplique.

Crear 8–12 preguntas por segmento orientadas a:
- costo actual;
- frecuencia;
- pain;
- fallas;
- willingness to pay;
- acceptance requirements;
- tool recovery/FME;
- procurement;
- incumbent.

---

# 27. Requisitos visuales del HTML

El informe anterior funcionó bien visualmente; mantener un nivel profesional.

### Estilo
- limpio;
- técnico;
- ejecutivo;
- legible;
- responsive;
- tablas con sticky header cuando sean largas;
- TOC lateral o superior;
- callouts de “Hallazgo”, “Riesgo”, “Inferencia”, “Dato EPRI”;
- no saturar de colores;
- gráficos vectoriales/SVG cuando convenga.

### Componentes útiles
- executive scorecards;
- comparison matrix;
- expandable source notes;
- evidence badges A/B/C/D;
- maturity badges M0–M5;
- confidence badges.

### Evitar
- marketing genérico;
- frases sin sustento;
- imágenes decorativas;
- gráficas 3D;
- tablas ilegibles;
- “AI generated” filler.

---

# 28. Archivos finales a entregar

Crear:

1. `robot_opportunities_2026.html`
   - informe completo en español.

2. `robot_opportunities_sources.md`
   - registro de fuentes con notas de qué respalda cada una.

3. `robot_opportunities_evidence.csv`
   Columnas sugeridas:
   - candidate
   - claim
   - value
   - unit
   - source_id
   - source_type
   - evidence_level
   - url
   - access_date
   - confidence
   - notes

4. `robot_opportunities_competitors.csv`
   - producto;
   - empresa;
   - aplicación;
   - status;
   - país;
   - tech;
   - dimensions;
   - payload;
   - deployments;
   - price;
   - source.

5. `robot_opportunities_patents.csv`

6. `/assets`
   - imágenes permitidas/locales;
   - gráficos generados;
   - diagramas.

7. `research_log.md`
   - consultas realizadas;
   - bases consultadas;
   - leads descartados;
   - fuentes que no pudieron obtenerse.

---

# 29. Criterio de finalización

NO dar por terminado el informe porque “hay suficiente información”.

Antes de cerrar, ejecutar este checklist:

- [ ] Se recorrió EPRI Product Index completo de robotics/mobile technologies.
- [ ] Se recorrió EPRI Plant Modernization Toolbox buscando robotics/inspection.
- [ ] Se buscó cada activo + robot en EPRI.
- [ ] Se buscó cada activo sin la palabra robot para encontrar métodos competidores.
- [ ] Se investigaron al menos los Top 7 candidatos.
- [ ] Se buscaron candidatos nuevos.
- [ ] Se hizo competitor search profundo de Top 5.
- [ ] Se hizo patent screening de Top 5.
- [ ] Se buscaron RFPs/contratos de Top 3.
- [ ] Se verificó status 2026 de cada competidor principal.
- [ ] Se buscó precio/ticket cuando exista.
- [ ] Cada número importante tiene referencia inmediata.
- [ ] Cada claim de fabricante está etiquetado.
- [ ] Cada inferencia está etiquetada.
- [ ] Se documentó evidencia negativa.
- [ ] Se hizo market sizing bottom-up o se explicó por qué no es defendible.
- [ ] Se hizo capítulo Argentina/LATAM para Top 3.
- [ ] Se hizo sensitivity analysis del ranking.
- [ ] Se definieron Top 3.
- [ ] Se definieron “Do not pursue now”.
- [ ] Se listaron unknowns.
- [ ] Se listaron entrevistas/contactos prioritarios.
- [ ] Se revisó que el HTML sea autocontenido y abra correctamente.

---

# 30. Instrucción final

**Buscá más de lo que te estoy dando acá.**

Este brief contiene hipótesis y fuentes seed, no las conclusiones.

Si durante la investigación encontrás que:
- IPB está saturado;
- TesTex cerró el gap de HRSG;
- vault robotics no tiene economics;
- existe un robot desconocido que invalida nuestra propuesta;
- otra aplicación EPRI ofrece un negocio mucho mejor;

**cambiá el ranking.**

La prioridad es no enamorarse de una solución.

El resultado debe permitir tomar una decisión de inversión con tres cosas claramente separadas:

1. **lo que sabemos;**
2. **lo que inferimos;**
3. **lo que todavía debemos validar.**

Y la conclusión debe responder sin ambigüedad:

> **¿Cuál debería ser el próximo robot que desarrollemos, y por qué?**
