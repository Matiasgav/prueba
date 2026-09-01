---
titulo: Oportunidades de robótica de inspección industrial para generación y utilities
subtitulo: Marco de evaluación, mapa de candidatos y plan de verificación
edicion: Edición 2026 · Documento de trabajo para decisión de inversión
fecha: Fecha de corte de la evidencia recopilada: 31 de agosto de 2026
---

# Resumen ejecutivo

Este documento define **qué robot de inspección industrial conviene desarrollar como próximo producto**, con qué evidencia se decide y qué queda por verificar antes de comprometer inversión. No es un catálogo de ideas técnicas: es el marco de decisión, el mapa de las siete oportunidades candidatas y el plan de verificación que las confirma o las descarta.

::: nota dato | Cómo leer este informe
Los términos de negocio y del sector están definidos en el **Anexo C**, cada uno con la fuente donde puede verificarse la definición. En el texto, la primera aparición de cada término enlaza a su entrada. Cuando un término no tiene definición normativa, el anexo lo declara como definición operativa de este informe en lugar de atribuirle una fuente inexistente.

Las afirmaciones llevan su clase: {{ev:A}} a {{ev:D}} indican el nivel de la fuente, {{tipo:Declaración}} señala una afirmación comercial del fabricante no verificada de forma independiente, y {{mad:M4}} indica madurez comercial en la escala de la sección 3.4.
:::

::: nota clave | La pregunta que ordena todo el estudio
No se busca responder *qué robots interesantes podrían construirse*, sino:

**¿En qué tareas de inspección o mantenimiento existe un dolor económico suficientemente grande, un acceso suficientemente difícil y un mercado suficientemente abierto como para justificar el desarrollo de un robot industrial especializado y construir un negocio rentable alrededor de él?**
:::

## Estado de la evidencia al cierre de esta edición

::: kpi
8 || candidatos con ficha de evaluación || uno de ellos surgido del barrido ampliado
3 || con valor económico publicado || por fuente de nivel A
2 || con incumbente comercial identificado || TesTex en HRSG, Diakont en piping
6 || familias de activos descartadas con evidencia || y registradas con su fuente
:::

## Lectura rápida de los siete candidatos

La tabla ordena los candidatos por el estado de la evidencia disponible hoy, no por preferencia. El candidato H proviene del barrido ampliado documentado en la sección 15. La columna de madurez usa la escala M0–M5 definida en la sección 3.4 y expresa una **hipótesis de partida**, no una medición.

| Candidato | Activo | {{t:madurez-m|Madurez}} hipotética | Evidencia económica | {{t:incumbente|Incumbente}} conocido | Reutilización de plataforma |
|---|---|:--:|---|---|:--:|
| **A** | {{t:ipb|Bus isofásico (IPB)}} | {{mad:M3}} {{mad:M4}} | Publicada, nivel A | Servicios de inspección especializados | Alta |
| **B** | {{t:hrsg|HRSG}}: headers y tubos | {{mad:M4}} | Parcial; parte declarada por fabricante | TesTex (IAT, Claw) | Media-alta |
| **C** | Vaults subterráneos de transmisión | {{mad:M1}} {{mad:M2}} | No publicada | No identificado aún | Media |
| **D** | Piping enterrado e inaccesible | {{mad:M4}} {{mad:M5}} | Publicada, nivel A | Diakont y otros | Media |
| **E** | Contenedores de combustible en seco | {{mad:M3}} | Publicada, cualitativa | Robotic Technologies of Tennessee | Media |
| **F** | Penstocks y túneles hidro | {{mad:M4}} | Parcial | Múltiples proveedores de ROV | Media-baja |
| **G** | Robots everting (vine) | {{mad:M1}} | No publicada | No identificado aún | Baja |
| **H** | Condensador refrigerado por aire | {{mad:M1}} | Dolor publicado, sin cifra de costo | Ninguno identificado para inspección interna | Alta |

::: fig fig-mapa-candidatos | Figura 1 — Posicionamiento de partida de los ocho candidatos. | Elaboración propia sobre las fuentes del Anexo A.
:::

## Qué dice hoy la evidencia

::: tarjetas 3
::: tarjeta Donde hay valor probado | Candidatos A y D
El valor económico está **publicado y es alto** en bus isofásico y en piping enterrado: reducción de costo cercana a un orden de magnitud en un caso reportado, y ahorros de entre uno y cinco millones de dólares por utilización, respectivamente. En ambos casos la contrapartida es madurez comercial alta.
:::
::: tarjeta Donde hay incumbente | Candidatos B, D y F
HRSG, piping enterrado y penstocks tienen proveedor establecido. Entrar exige demostrar un {{t:whitespace|espacio no cubierto (*whitespace*)}} concreto —una geometría, un acceso o una medición que el incumbente no cubre—, no una plataforma equivalente.
:::
::: tarjeta Donde el problema sigue abierto | Candidatos C, G y H
Vaults subterráneos mantiene actividad de investigación vigente con prototipos y demostraciones en curso, sin producto consolidado. Los robots everting son una tecnología sin mercado asignado. En condensadores refrigerados por aire, los propios operadores declaran que la mayor parte del activo **no se inspecciona** por razones de acceso.
:::
:::

::: nota inferencia | El hallazgo más útil del barrido ampliado
En seis de las siete familias de activos barridas, el mercado ya está ocupado o el hueco aparente está cerrado por una razón física conocida. La excepción —condensadores refrigerados por aire— no destaca porque la inspección sea cara, sino porque **hoy no se hace**: es una necesidad declarada por los operadores y no cubierta por los proveedores actuales.
:::

## Qué no debería desarrollarse sin un hallazgo que lo justifique

- Un **{{t:crawler|crawler}} genérico de tuberías**: el problema ya está resuelto comercialmente y el valor lo captura un proveedor establecido.
- Un **robot nadador para transformadores** que replique una función ya cubierta por el producto de referencia del mercado.
- **Otro cuadrúpedo o vehículo de patrulla** de subestaciones: el valor diferencial está en la carga sensora y la analítica, no en la plataforma.
- Un **crawler de línea de transmisión** para inspección visual de rutina, salvo que se demuestre que los drones no lo hicieron económicamente obsoleto.

## Las incógnitas que bloquean la decisión

1. Qué parte del problema de HRSG **no** resuelve hoy el incumbente, con evidencia independiente y no comercial.
2. Cuántos activos direccionables existen por año y a qué ticket real se contrata cada inspección, según contratos y licitaciones y no según informes de mercado.
3. Qué familias de patentes vigentes cubren las arquitecturas candidatas.
4. Qué exige la calificación regulatoria en los candidatos nucleares y cuánto cuesta obtenerla.
5. Si el problema de vaults subterráneos sostiene un ticket recurrente o es un servicio de baja frecuencia y bajo precio.
6. Si en condensadores refrigerados por aire el robot puede evitar el andamiaje, que es donde está la mayor parte del costo, o si igual hay que montarlo para posicionarlo.

::: nota riesgo | El error que este estudio existe para evitar
Descubrir dentro de dos años que el problema ya había sido investigado por una organización de referencia, que un fabricante ya había patentado la arquitectura, que existía un producto comercial establecido, que el cliente ya compraba ese servicio o que hubo un programa de desarrollo que fracasó por una razón física conocida.
:::

---

# Parte I — Marco de decisión

## 1. Objetivo y alcance

### 1.1 Qué produce este estudio

Una recomendación de inversión sostenida por evidencia verificable, que separa con claridad tres cosas distintas:

1. **Lo que sabemos**, con fuente y nivel de evidencia declarados.
2. **Lo que inferimos**, etiquetado como inferencia de ingeniería.
3. **Lo que todavía debe validarse**, con un plan concreto para hacerlo.

La conclusión debe responder sin ambigüedad: **¿cuál debería ser el próximo robot que se desarrolle, y por qué?**

### 1.2 Perfiles que requiere el análisis

El estudio combina seis competencias, porque una oportunidad puede caerse por cualquiera de ellas:

- ingeniería sénior de robótica de inspección;
- especialidad en {{t:nde|ensayos no destructivos (NDE/NDT)}};
- análisis de mercado industrial B2B;
- mantenimiento de generación eléctrica;
- investigación de {{t:prior-art|*prior art*}} y patentes;
- análisis de producto y estrategia.

### 1.3 Qué queda fuera

- No es un diseño de detalle: las propuestas de robot se definen por requisitos funcionales, no por ingeniería de producto.
- No es una opinión legal de {{t:fto|libertad de operación}}. El análisis de patentes es un **screening preliminar de propiedad intelectual**.
- No es un dimensionamiento de mercado basado en informes genéricos de la industria. Cuando no hay datos suficientes para un cálculo defendible, el tamaño de mercado no se publica.

## 2. Qué hace rentable un negocio de robótica de inspección

### 2.1 La lógica del producto de referencia

Existe un proyecto de robot de inspección (RI) para generadores con rotor instalado. Se usa como **{{t:benchmark|benchmark}} económico y tecnológico**, no como oportunidad nueva. Su lógica de negocio define el patrón que se busca replicar:

- activo extremadamente caro;
- acceso difícil;
- la inspección convencional puede exigir gran desmontaje, personal especializado o una parada prolongada;
- el robot reduce {{t:outage|salida de servicio}}, desmontaje y riesgo;
- el cliente no compra un robot: compra **información de condición confiable** y ahorro de mantenimiento;
- el valor del servicio puede superar ampliamente el costo del hardware;
- la plataforma integra locomoción, cámaras, iluminación, sensado especializado, posicionamiento, {{t:tether|tether}} y comunicaciones, procesamiento y generación automática de informes.

::: nota inferencia | Consecuencia para la selección de candidatos
Una oportunidad es comparable al producto de referencia sólo si reproduce la estructura completa del valor: activo caro **y** acceso difícil **y** costo convencional alto **y** decisión de mantenimiento que depende del resultado. Un activo caro con acceso sencillo no sostiene el modelo.
:::

### 2.2 Restricciones y filosofía de producto

Ocho criterios se aplican a toda solución propuesta, y funcionan como filtro de diseño antes que como preferencia estética.

::: tarjetas 2
::: tarjeta 1. Calidad industrial
Hardware apto para servicio profesional repetido y alta confiabilidad. Un prototipo de campo no es un producto de servicio.
:::
::: tarjeta 2. Costo/beneficio
Se evitan soluciones metrológicas o robóticas innecesariamente exóticas cuando una arquitectura commodity logra el mismo resultado.
:::
::: tarjeta 3. Componentes commodity
Se prefieren componentes con múltiples fabricantes y cadena de suministro amplia, por disponibilidad y por costo de repuesto.
:::
::: tarjeta 4. Industrialización
Se evalúa manufacturabilidad, mantenimiento, calibración, reemplazo de consumibles y vida útil desde el primer concepto.
:::
::: tarjeta 5. Argentina y Latinoamérica
Disponibilidad de componentes, soporte, importación y exportación, y potencial real de mercado regional.
:::
::: tarjeta 6. Precio real
Se buscan precios efectivos: distribuidores, contratos públicos, licitaciones, integradores o mercado usado. Las estimaciones se etiquetan como tales.
:::
::: tarjeta 7. Recuperación y {{t:fme|FME}}
En generación eléctrica y nuclear, un robot atrapado puede ser peor que no inspeccionar. La estrategia de recuperación es parte del producto.
:::
::: tarjeta 8. Servicio antes que hardware
Si la frecuencia por activo es baja pero el ticket por inspección es alto, el modelo de {{t:raas|inspección como servicio}} puede superar a la venta de equipos.
:::
:::

## 3. Disciplina de evidencia

### 3.1 Cuatro clases de afirmación que nunca deben mezclarse

::: tarjetas 2
::: tarjeta A · Hecho verificado | {{ev:A}}
Información respaldada por una fuente primaria o independiente de alta calidad.

*Ejemplo:* EPRI estima ahorros mayores a un millón y menores a cinco millones de dólares por utilización en una aplicación específica de crawler para tuberías enterradas [EPRI MTA-MA-017].
:::
::: tarjeta B · Declarado por el fabricante | {{tipo:Declaración}}
Afirmación comercial del fabricante o proveedor. **No se convierte en validación independiente.**

*Ejemplo:* TesTex declara que su herramienta de acceso interno inspecciona todos los tubos conectados a un header en tres o cuatro turnos.
:::
::: tarjeta C · Inferencia de ingeniería | {{tipo:Inferencia}}
Conclusión razonada del autor a partir de la evidencia disponible. Se etiqueta explícitamente en el texto.
:::
::: tarjeta D · Estimación comercial | {{tipo:Estimación}}
Cálculo propio de mercado, ticket, ahorro o volumen. Debe mostrar fórmula, supuestos, rango, fuente de cada entrada y sensibilidad. **Nunca se presenta como dato publicado.**
:::
:::

### 3.2 Jerarquía de fuentes

::: fig fig-evidencia | Figura 2 — Jerarquía de evidencia y familias de fuentes de cada nivel. | Elaboración propia.
:::

El nivel D sirve únicamente para **descubrir** la fuente primaria. No se usa como evidencia final si el original puede localizarse.

### 3.3 Diez reglas de verificación

1. **Una patente demuestra divulgación, no funcionamiento comercial.** Se verifica familia, titular, prioridad, estado legal y expiración o abandono cuando sea relevante.
2. **Un prototipo universitario no es un producto.**
3. **Un producto anunciado no equivale a despliegue de campo.** Se buscan clientes, sitios, fechas, cantidad de inspecciones y evidencia de repetición.
4. **Una reducción de costos publicada por el fabricante se identifica como tal**, no como resultado independiente.
5. **No se usan informes de mercado opacos** del tipo «mercado de X mil millones de dólares» como base principal.
6. Si no existe precio publicado: se escribe *precio no publicado* y se buscan contratos, licitaciones y distribuidores. No se inventa.
7. Si no hay evidencia de competencia: se escribe *no se identificó competencia después de las búsquedas X, Y y Z*. No se escribe *no existe competencia*.
8. Se buscan productos **actuales, discontinuados, adquiridos y fallidos**.
9. Se busca en inglés y, cuando corresponda, también en alemán, japonés, chino, coreano, francés, español y portugués: empresas relevantes pueden no estar bien indexadas en inglés.
10. Cada candidato recibe, como mínimo, búsquedas por activo en la base del instituto de investigación sectorial; búsquedas por robótica, inspección remota y automatización; búsqueda web general; búsqueda de patentes en las bases internacionales; revisión de fabricantes y de utilities; literatura técnica revisada; licitaciones y contratos; y material audiovisual técnico sólo como evidencia suplementaria.

### 3.4 Escala de madurez comercial

::: fig fig-madurez | Figura 3 — Escala de madurez comercial M0–M5 usada en todo el documento. | Elaboración propia.
:::

::: nota riesgo | No confundir madurez con nivel tecnológico
Un desarrollo puede tener {{t:trl|nivel tecnológico}} alto y madurez comercial baja: la escala mide **despliegue real en el mercado**, no capacidad demostrada en laboratorio.
:::

## 4. Proceso de evaluación

::: fig fig-proceso | Figura 4 — Secuencia de evaluación por candidato y filtro de clasificación de evidencia. | Elaboración propia.
:::

### 4.1 La búsqueda histórica es obligatoria

Para cada candidato se reconstruye una línea temporal completa, además de la búsqueda del estado actual.

::: fig fig-cronologia | Figura 5 — Línea temporal de prior art que debe reconstruirse por candidato. | Elaboración propia.
:::

### 4.2 Las fuentes negativas son las más valiosas

Un programa que se detuvo explica más que diez folletos comerciales. Se documentan explícitamente:

- productos discontinuados y programas abandonados;
- resultados insuficientes publicados en literatura técnica;
- robots que quedaron atascados y herramientas que no entraron;
- eventos de material extraño (FME) y fallas de tether;
- ensayos no destructivos que no alcanzaron la sensibilidad requerida;
- costos que destruyeron el {{t:caso-negocio|caso de negocio}}.

---

# Parte II — Mapa de oportunidades

## 5. Panorama y criterio de entrada

Los siete candidatos que siguen no son una conclusión: son el punto de partida verificado hasta la fecha de corte. **Ninguno se da por válido**: cada uno se verifica desde cero y se descarta si la evidencia lo exige. Si durante la verificación aparece que un candidato está saturado, que el incumbente cerró el hueco o que otra aplicación ofrece un negocio mejor, el orden cambia.

Cada ficha responde siempre a la misma estructura: geometría y problema, hipótesis de valor, evidencia disponible con su nivel, competencia identificada, pregunta estratégica que decide el caso y agenda de verificación pendiente.

## 6. Candidato A — Bus isofásico (IPB)

::: fig esq-ipb | Figura 6 — Geometría de acceso del bus isofásico y obstáculos internos. | Esquema del autor.
:::

### 6.1 Hipótesis de valor

Puede ser la extensión inmediata más natural del producto de referencia:

- mismo tipo de cliente;
- inspección durante paradas programadas;
- espacio confinado;
- reducción de andamiaje y de entrada de personal;
- alta reutilización de cámaras, tether, iluminación, software de mapeo y arquitectura de crawler.

### 6.2 Evidencia disponible

::: nota dato | Dato EPRI verificado — MTA-MA-029 {{ev:A}}
Experiencia reportada por una utility con costo de proveedor de aproximadamente **USD 100.000 por implementación**; ejecución de la inspección en **menos de un día**; reducción de costo de aproximadamente **10×** frente a la inspección manual en ese caso; {{t:payback|payback}} inmediato según la evaluación {{t:sweep|SWEEP}}; tecnología comercialmente disponible; riesgos identificados de falla de crawler o de herramienta. Una parte sustancial del ahorro proviene de evitar andamiaje y acceso humano.

**Este dato no se generaliza al mercado completo sin evidencia adicional.**
:::

::: fig fig-ipb-economia | Figura 7 — Costo relativo de la inspección de bus isofásico e indicadores del caso reportado. | EPRI, Plant Modernization Toolbox, MTA-MA-029.
:::

::: nota riesgo | Advertencia de recurrencia, verificada en fuente primaria {{ev:A}}
EPRI declara que las inspecciones de bus isofásico se realizan **típicamente cada 10 años**. El candidato A combina entonces valor alto por intervención con recurrencia baja: un activo que se inspecciona una vez por década sólo sostiene un negocio de servicio si la base instalada accesible es grande.

El criterio de recurrencia del Ranking A penaliza a este candidato más de lo que suponía la hipótesis de partida, y el dimensionamiento debe hacerse sobre inspecciones por año, no sobre cantidad de activos.

*Nota de calidad de fuente:* en ese mismo documento, la tabla del bus isofásico repite literalmente la frase de horas-hombre de la tabla de estructuras de toma de agua, incluida la explicación de que el rango depende de la calidad del agua, que no aplica a un ducto de barras. Por esa inconsistencia **no se utiliza** ninguna cifra de horas-hombre para este candidato desde esa fuente.
:::

De la guía de mantenimiento de bus aislado por fases (EPRI 1015057) deben extraerse: frecuencia típica de inspección, modos de defecto, condiciones de acceso, figuras de plataformas robóticas existentes, mantenimiento recomendado y mediciones eléctricas asociadas.

### 6.3 Competencia identificada para verificación

Trident NGS · Electrical Builders Inc. · MidStates Energy · nVent · áreas de servicio de GE Vernova, Siemens Energy e Hitachi Energy · empresas especializadas del sector nuclear · sistemas de origen coreano, japonés y chino · desarrollos universitarios, entre ellos los de la Universidad de Beihang.

La evolución posible del alcance —de cámara sobre crawler a limpieza, retiro de material extraño, verificación de torque, medición de resistencia y manipulación— debe evaluarse contra el catálogo de tareas de alto valor de EPRI 3002023899.

De cada uno debe registrarse: nombre exacto del equipo, fabricante, tipo de locomoción, dimensiones, tether o inalámbrico, forma de superar aisladores y soportes, estrategia de recuperación, sensores, capacidad de limpieza, medición de torque o resistencia, precio del servicio, clientes y frecuencia de inspección.

::: nota clave | Pregunta estratégica que decide el candidato
¿Existe espacio para un sistema de **inspección y mantenimiento** —limpieza, retiro de material extraño, verificación de torque, medición de resistencia, manipulación— y no solamente para otro crawler con cámara?
:::

::: detalle Agenda de verificación pendiente
- Confirmar si el valor de USD 100.000 corresponde a un contrato típico o a un caso aislado, contrastando con licitaciones y contratos de utilities.
- Determinar la frecuencia real de inspección por tramo y por central.
- Establecer si el ahorro por evitar andamiaje se sostiene en plantas con accesos ya construidos.
- Verificar el estado 2026 de cada proveedor identificado: activo, discontinuado, adquirido o sin comercialización.
- Buscar patentes sobre crawlers para ductos de barras y sobre mecanismos de superación de aisladores.
:::

## 7. Candidato B — HRSG: headers, soldaduras y tubos

::: fig esq-hrsg | Figura 8 — Acceso a header, soldaduras tubo-header y tubos en una caldera de recuperación. | Esquema del autor.
:::

### 7.1 El problema físico

El estudio EPRI 1017635 sobre tecnología de robots tipo serpiente para inspección de {{t:header|headers}} y tubos en calderas de recuperación de calor documenta el punto de partida: ciertos tubos interiores **no pueden inspeccionarse fácilmente con ensayos no destructivos convencionales sin acceso destructivo**. De ese informe deben extraerse las razones por las que la inspección convencional no llega, las geometrías y diámetros involucrados, las longitudes, los tipos de caldera, los puntos de acceso, las modalidades de inspección evaluadas, los conceptos de robot analizados, lo que se demostró, lo que quedó sin resolver y por qué ese concepto no se comercializó directamente.

### 7.2 El incumbente

::: nota dato | Declarado por el fabricante — TesTex {{tipo:Declaración}}
La herramienta de acceso interno (IAT) es un crawler que se coloca dentro del header; puede ingresar por la tapa del extremo o, en versión modular, por un orificio de aproximadamente 8 pulgadas; empuja una sonda de {{t:rfet|corrientes inducidas por campo remoto}} junto con una cámara a lo largo de los tubos; se opera en forma remota; según el fabricante inspecciona todos los tubos de un header en tres o cuatro turnos y declara cobertura del 100 % de los tubos dentro de sus condiciones de aplicación, con despliegues en múltiples utilities.

La herramienta complementaria de inspección de soldaduras por campo lejano declara del orden de 200 soldaduras por turno.

**Ninguna de estas cifras es evidencia independiente hasta que se contraste con clientes, contratos o literatura técnica.**
:::

### 7.3 Competencia y fuentes adicionales a recorrer

Patentes de TesTex · desarrollos conjuntos entre EPRI y TesTex · *Combined Cycle Journal* y el HRSG Forum · fabricantes de calderas de recuperación: Nooter/Eriksen, Vogt, Alstom/Altrad · GE Vernova · Siemens Energy · EDF · proveedores de servicios de ensayos no destructivos: MISTRAS · fabricantes de instrumentación: Eddyfi, Waygate/Baker Hughes, Olympus/Evident · robots académicos para tubos de caldera · crawlers magnéticos · robots serpiente y robots continuos.

::: nota clave | Pregunta estratégica que decide el candidato
El mercado no está vacío. La pregunta correcta es: **¿qué parte del problema no resuelve hoy el incumbente?**

Hipótesis a validar: menor diámetro de acceso; no retirar la tapa del extremo; más tipos de header cubiertos; indexado automático de tubos; mayor alcance dentro del tubo; mejor localización; un solo despliegue que cubra soldadura y espesor de pared; medición cuantitativa superior; mayor autonomía; capacidad frente a depósitos y bloqueos; inspección combinada con limpieza o reparación.

Si no aparece un hueco defendible, el candidato baja en el ranking.
:::

::: detalle Agenda de verificación pendiente
- Obtener evidencia independiente de cobertura real por header y por turno.
- Determinar qué proporción del parque de calderas queda fuera del alcance del incumbente por geometría.
- Cuantificar el costo de una parada por falla de soldadura tubo-header frente al costo de la inspección.
- Revisar la familia de patentes del incumbente y su estado legal.
:::

## 8. Candidato C — Vaults subterráneos de transmisión

::: fig esq-vault | Figura 9 — Vault subterráneo con cables energizados, empalmes y acceso por boca de registro. | Esquema del autor.
:::

### 8.1 Estado de la investigación

::: nota dato | Investigación vigente {{ev:A}}
El programa de transmisión subterránea de EPRI publicó *Underground Transmission Vault Inspection Using Robotic Techniques* (3002000878) sobre inspección de {{t:vault|vaults}} en 2013 y mantiene el trabajo con la actualización 2025 (3002032834) y actividad declarada para 2026 y 2027. Los objetivos declarados son mejorar la seguridad de los trabajadores y reducir los requerimientos de salida de servicio del circuito. Se reportan conceptos y prototipos demostrados en laboratorio y en sitios de utilities, con demostraciones en planificación.
:::

Existe además un proyecto complementario sobre inspección de bocas de registro con cable extruido dentro de los proyectos suplementarios colaborativos 2025–2026, cuya arquitectura debe caracterizarse: inspección desde la superficie, cable energizado, termografía infrarroja, cámara, detección de gases, brazo mecánico y, si aplica, descargas parciales o medición acústica y ultrasónica.

### 8.2 Competencia a investigar

Osmose · utilities con desarrollo propio: Con Edison, National Grid, Southern California Edison, PG&E, NYPA, Duke Energy, Dominion, Entergy e Hydro-Québec · empresas de crawlers para colectores adaptados · drones de espacio confinado · plataformas cuadrúpedas (Boston Dynamics, ANYbotics) aplicadas a vaults · integradores.

::: nota clave | Pregunta estratégica que decide el candidato
Este candidato puede estar **menos maduro** que el bus isofásico o el piping enterrado, lo que es simultáneamente su oportunidad y su riesgo. Debe determinarse: cantidad de vaults, frecuencia de inspección, necesidad de desenergización, costo actual, carga de seguridad y espacio confinado, si puede venderse como servicio recurrente, ticket razonable y requisitos de aislamiento eléctrico y detección de gases.
:::

::: detalle Agenda de verificación pendiente
- Contactar a los responsables técnicos del programa de transmisión subterránea de EPRI —David Kummer, inspección robótica, y Tom Zhao, dirección del programa— verificando previamente que sigan en esos roles.
- Buscar el proyecto *Extruded Cable Manhole Inspections* dentro de los proyectos suplementarios colaborativos 2025–2026.
- Obtener el censo de vaults de al menos dos utilities y su plan de inspección.
- Verificar si la inspección hoy exige salida de servicio y cuánto cuesta esa salida.
- Determinar si el comprador es el área de mantenimiento, la de seguridad o la de ingeniería de activos.
:::

## 9. Candidato D — Piping enterrado e inaccesible

::: fig esq-piping | Figura 10 — Inspección de tubería enterrada desde un acceso único, sin excavación. | Esquema del autor.
:::

### 9.1 Evidencia disponible

::: nota dato | Dato EPRI verificado — MTA-MA-017 {{ev:A}}
Inspección desde un único punto de acceso, que puede evitar la excavación. La {{t:emat|técnica electromagnética acústica (EMAT)}} permite determinados exámenes volumétricos sin remover el revestimiento. Según la evaluación SWEEP: costo de implementación menor a un millón de dólares; ahorro mayor a un millón y menor a cinco millones por utilización; payback inmediato o menor a un año; tecnología ya comercialmente implementada en el sector nuclear.
:::

::: fig fig-piping-economia | Figura 11 — Costo de implementación y rango de ahorro esperado por utilización. | EPRI, Plant Modernization Toolbox, MTA-MA-017.
:::

De la compilación de lecciones aprendidas sobre tuberías enterradas y subterráneas (EPRI 1025272) deben extraerse: por qué la {{t:ili|inspección en línea}} convencional no funciona bien en instalaciones nucleares, ausencia de estaciones de lanzamiento y recepción, codos, derivaciones, tramos verticales, revestimientos, diámetros, condición con y sin agua, y los eventos de material extraño y recuperación.

### 9.2 Competencia

Diakont, con caso documentado de primera inspección en línea de tubería enterrada en el sector nuclear · Structural Integrity Associates · Westinghouse · Framatome · Eddyfi/Inuktun, incluida la familia VersaTrax · Waygate Technologies · Gecko Robotics · MISTRAS · ROSEN y NDT Global en inspección en línea de hidrocarburos · empresas de inspección de tuberías industriales.

::: nota clave | Pregunta estratégica que decide el candidato
La evidencia clasifica este candidato como **comercialmente implementado**. Por lo tanto, **no debe recomendarse un crawler genérico de tuberías**. Sólo se recomienda si se identifica un hueco concreto: diámetro pequeño, codos de radio corto, derivaciones, reducciones, tramos verticales, transición seco-húmedo, tubería protegida o revestida, inspección combinada con reparación, despliegue sin corte, acceso menor, o un servicio de bajo costo fuera del ámbito nuclear.
:::

::: detalle Agenda de verificación pendiente
- Mapear qué geometrías quedan explícitamente fuera del alcance de los proveedores actuales.
- Obtener precios de servicio por metro inspeccionado en al menos dos mercados.
- Evaluar el mercado no nuclear —industrial, municipal, petroquímico— donde el costo de calificación es menor.
:::

## 10. Candidato E — Contenedores de combustible gastado en seco

::: fig esq-cask | Figura 12 — Espacio anular de inspección en un contenedor de almacenamiento en seco. | Esquema del autor.
:::

### 10.1 Evidencia disponible

EPRI desarrolla sistemas de inspección y de entrega robótica para almacenamiento en {{t:canister|canister}} seco (3002008234, *Dry Canister Storage System Inspection and Robotic Delivery System Development*), con difusión adicional en EPRI Journal sobre robots trepadores para contenedores. Los elementos verificados hasta la fecha: espacios anulares muy estrechos; combinación de cámara, {{t:eca|corrientes inducidas}}, técnica electromagnética acústica y medición de dosis y temperatura en ciertas configuraciones; múltiples ensayos de campo; y una reducción de costo muy alta frente a los métodos que exigen izaje pesado o movimiento del canister.

### 10.2 Competencia

Robotic Technologies of Tennessee declara que instalaciones nucleares utilizan sus plataformas para inspección de almacenamiento en seco. Deben verificarse: los modelos exactos; los programas de EPRI y del Departamento de Energía; el caso de San Onofre (SONGS); los fabricantes de sistemas de almacenamiento —Holtec, Orano, NAC—; los requisitos de la Comisión Reguladora Nuclear; los desarrollos universitarios asociados, entre ellos los de Penn State y la iniciativa PRINSE; la calificación frente a radiación; y el panorama de patentes.

::: nota clave | Pregunta estratégica que decide el candidato
El valor por inspección es alto, pero el mercado es limitado, la calificación es exigente, el riesgo de material extraño es crítico, hay dosis y existe un incumbente. Debe compararse rigurosamente contra oportunidades menos reguladas antes de asignarle prioridad.
:::

## 11. Candidato F — Penstocks y túneles hidroeléctricos

::: fig esq-penstock | Figura 13 — Inspección de conducto forzado con vehículo remoto y tether. | Esquema del autor.
:::

### 11.1 Base de evidencia

El informe EPRI sobre tecnología de {{t:rov|vehículos operados remotamente}} en instalaciones hidroeléctricas (TR-113584-V7 / 1007576) aporta: aplicaciones en túnel y {{t:penstock|conducto forzado}}, inspección visual, sonar, medición de espesor por ultrasonido, limitaciones de tether, alcance, recuperación, casos de estudio y ahorro por evitar vaciado y salida de servicio. Debe complementarse con EPRI 3002011682, *Autonomous Underwater Vehicles for Tunnel and Penstock Inspection*, y con la actividad vigente del EPRI Unmanned Mobile Technologies Collaboration Group.

### 11.2 Competencia

Deep Trekker · VideoRay · Eddyfi/Inuktun · Deep Ocean Engineering · Saab Seaeye · integradores sobre plataformas Blue Robotics · vehículos propios de utilities como Hydro-Québec · fabricantes de turbinas con área de servicio: Voith, Andritz y GE Vernova Hydro · proveedores especializados en inspección de túneles.

::: nota clave | Pregunta estratégica que decide el candidato
La inspección visual con vehículo remoto es probablemente madura. El hueco, si existe, está en: navegación autónoma en distancias kilométricas; localización sin señal satelital; mapeo de espesor de pared; ensayos no destructivos en contacto; recuperación garantizada; operación con turbidez, con caudal alto y con tether largo.
:::

## 12. Candidato G — Robots everting (vine) para equipos de planta

::: fig esq-vine | Figura 14 — Avance por eversión en un conducto ramificado de equipo de planta. | Esquema del autor.
:::

### 12.1 Estado

EPRI registra sobre {{t:vine|robots everting}} el estudio 3002032954, *Everting Vine Robots for Plant Equipment Inspection – Technology Review and Feasibility Study*, cuyos resultados deben verificarse directamente y sin asumir contenidos no públicos. Como fuentes externas iniciales: la literatura de *IEEE Robotics & Automation Magazine* sobre robots vine de gran escala para inspección industrial; el trabajo conjunto de UCSB y Bechtel; los desarrollos de Stanford; y las empresas emergentes Trellis Robotics e IvySpec.

::: nota clave | Pregunta estratégica que decide el candidato
Un robot everting es **una tecnología, no un mercado**. Sólo se justifica si se identifica un activo concreto donde el crawler no pasa, el boroscopio no alcanza, el desmontaje es costoso y el robot puede transportar un ensayo no destructivo útil.

Candidatos de activo a evaluar: conductos de aire y gases; calderas de recuperación; tramos de tubería compleja; espacios internos de turbina y caldera; conductos de cables; equipos confinados.
:::

## 13. Candidato H — Condensador refrigerado por aire (ACC)

Candidato incorporado durante el barrido ampliado de oportunidades. Es el único de ese barrido que llegó a ficha: el resto se cerró como mercado maduro o quedó descartado, con el detalle registrado en la sección 15.

::: fig esq-acc | Figura 15 — Acceso a los ductos de un condensador refrigerado por aire. | Esquema del autor.
:::

### 13.1 El problema, declarado por los propios operadores

::: nota dato | Dato verificado — guía de inspección interna de ACC {{ev:B}}
La guía de inspección interna de la asociación de usuarios de condensadores refrigerados por aire establece que los ductos inferiores se acceden sin gran dificultad, pero que **es probablemente irreal esperar que se inspeccione más de uno o dos de los ductos superiores de una unidad durante una parada**, y recomienda que la planta elija un ducto superior específico.

Alcanzar ese ducto superior puede exigir andamiaje o escalera temporal y una trepada por barandas hasta el registro de acceso, con protección contra caídas. El ductwork se define como espacio confinado: exige aire respirable verificado, monitoreo durante la permanencia y plan de rescate, porque las riostras cruzadas pueden obstruir la extracción de una persona en una emergencia.
:::

Esto invierte la formulación habitual del problema. **El dolor no es que la inspección sea cara: es que no se hace** sobre la mayor parte del activo, y la razón es el acceso.

El mecanismo de falla está documentado en la misma fuente: la corrosión del lado vapor transporta óxido de hierro al agua de alimentación de caldera, y las penetraciones pasantes en los tubos causan ingreso de aire con pérdida de rendimiento del condensador.

### 13.2 Escala del activo

Un condensador de este tipo puede tener del orden de 20.000 tubos y 40.000 soldaduras, y localizar una fuga puede equivaler a encontrar un orificio menor que una moneda en una superficie de tres o cuatro canchas de fútbol. {{ev:C}} — cifra de prensa técnica especializada, no verificada de forma independiente.

### 13.3 Competencia identificada

- **Conco Services** presta limpieza y detección de fugas con gas trazador. Resuelve la **localización de fugas desde el exterior**, no la evaluación interna del estado de corrosión. {{ev:C}}
- **EPRI** desarrolla una metodología con cámara acústica montada en dron para inspección de estos condensadores, sobre la base de resultados con cámara acústica de mano, y reporta ensayos con dron infrarrojo para analizar distribución de calor. {{ev:B}}
- **No se identificó** ningún crawler ni robot de inspección interna de ductos de este activo después de las búsquedas registradas en la bitácora. Esto **no equivale** a afirmar que no exista.

::: nota clave | Pregunta estratégica que decide el candidato
¿Puede un robot inspeccionar los ductos superiores que hoy se dejan sin inspeccionar, con calidad suficiente para sustituir la entrada humana, y sin exigir el andamiaje que constituye la mayor parte del costo evitado?

Si la respuesta exige igualmente montar andamiaje para posicionar el robot, el caso se cae: el ahorro dejaría de ser el acceso y pasaría a ser sólo el tiempo de inspección.
:::

### 13.4 Por qué encaja con la plataforma existente

Espacio confinado, tether, cámara e iluminación, mapeo y localización dentro de un ducto de sección constante, y generación automática de informe: la reutilización es alta y no exige un ensayo no destructivo nuevo, porque el hallazgo primario es visual y de estado de superficie.

::: detalle Agenda de verificación pendiente
- Cuantificar cuántas unidades con condensador refrigerado por aire existen en el mercado objetivo y en la región, y su antigüedad.
- Obtener el costo real de una parada con andamiaje para inspección de ducto superior, en al menos dos plantas.
- Verificar si algún proveedor de limpieza o de detección de fugas ya ofrece inspección interna robotizada, aunque no la publique.
- Screening de patentes sobre inspección interna de ductos de condensadores refrigerados por aire.
- Determinar si el comprador es mantenimiento, química o ingeniería de activos, y quién firma la orden de compra.
- Confirmar con la asociación de usuarios si la limitación de cobertura declarada en 2015 sigue vigente en 2026.
:::

## 14. Mercados con madurez probablemente alta

No se descartan sin investigación, pero se exige evidencia de hueco antes de invertir en ellos.

::: tarjetas 2
::: tarjeta 13.1 Robot nadador para transformadores | {{mad:M4}} {{mad:M5}}
Referencia de mercado: **ABB TXplore**, con inspección en menos de un día, eliminación de las tareas de drenaje y procesamiento de aceite y reducciones de costo declaradas de hasta aproximadamente 50 % en comunicaciones del fabricante y casos publicados.

**Pregunta:** ¿hay algo que TXplore no haga y que tenga mercado independiente de ABB?
:::
::: tarjeta 13.2 Robots de patrulla de subestaciones | {{mad:M4}}
EPRI trabaja con plataformas comerciales, incluido Spot de Boston Dynamics en determinados proyectos de subestaciones.

**Hipótesis:** el valor está más en la carga sensora y la analítica que en fabricar otro cuadrúpedo o vehículo terrestre no tripulado.
:::
::: tarjeta 13.3 Robots trepadores de línea de transmisión | {{mad:M3}}
Debe investigarse el linaje completo: los desarrollos Ti de EPRI, LineScout y LineROVer de Hydro-Québec y el Expliner de HiBot, y determinar si los drones modernos hicieron económicamente obsoleto al crawler para inspección visual de rutina.
:::
::: tarjeta 13.4 Robots de inspección de tanques | {{mad:M4}} {{mad:M5}}
Square Robot, Newton Labs, Eddyfi y proveedores de vehículos submarinos operan hoy en tanques en servicio. Mercado probablemente maduro; se exige evidencia de hueco antes de considerarlo.
:::
::: tarjeta 13.5 Robótica de internos de reactor y tubos de generador de vapor | {{mad:M5}}
Framatome, Westinghouse, la familia SUSI de AREVA y los desarrollos de KHNP/KEPRI cubren manipuladores de generador de vapor e internos de reactor. Mercado de altísimo valor, con proveedores establecidos y fuerte carga regulatoria: probablemente muy maduro.
:::
:::

## 15. Barrido de oportunidades fuera de la lista

El estudio no se limita a los siete candidatos: el barrido independiente es obligatorio y puede reordenar todo el ranking.

### 15.1 Resultado del barrido ejecutado

El barrido se ejecutó por familias de activos y quedó registrado con sus consultas, fuentes y niveles de evidencia en la bitácora de investigación que acompaña a este informe. Resultado por familia:

| Familia de activos | Veredicto | Razón determinante |
|---|---|---|
| Condensadores refrigerados por aire | **Candidato nuevo (H)** | Cobertura de inspección incompleta declarada por los operadores; ningún robot identificado para el interior de los ductos |
| Paredes de agua de caldera e internos de hogar | No perseguir | Incumbente consolidado con producto, datos, canal y alianza con fabricante de calderas, más media docena de competidores |
| Eólica: palas, torres y monopilotes | No perseguir | Cuatro proveedores en el interior de la pala; el hueco restante está limitado por la atenuación del material |
| Presas, compuertas y válvulas | Refuerza al candidato F | Dolor documentado por el propietario del activo, pero el equipamiento base ya es comercial: el valor está en el paquete de servicio |
| Intercambiadores de calor, hornos y chimeneas | Descartado | Intercambiadores en mercado M5; hornos pertenecen a siderurgia, con otro canal y prior art de alta temperatura ya patentado |
| Aparamenta blindada y túneles de cables | Línea a investigar / no perseguir | Costo de intervención documentado en aparamenta pero búsqueda insuficiente; prior art abundante en túneles de cables |
| Solar y tareas nucleares del catálogo | Sin candidato, con dato clave | El valor en solar es analítica, no robótica; el catálogo nuclear aportó las horas-hombre por tarea de la sección 17 |

::: nota inferencia | Cómo leer este resultado
Seis de siete familias se cerraron por evidencia de ocupación del mercado o por una limitación física documentada. Ese es el rendimiento normal de un barrido honesto: la mayoría de las ideas atractivas ya fueron intentadas, y el valor del ejercicio está en descartarlas rápido y por escrito.
:::

### 15.2 Barrido por programa sectorial

Generación · nuclear · transmisión · distribución · hidroeléctrica · combustibles fósiles y ciclo combinado · eólica · solar · subestaciones · transmisión subterránea · modernización de plantas · ensayos no destructivos · transformación digital · grupos de colaboración en robótica.

### 15.3 Tareas ya identificadas en la literatura sectorial

EPRI 3002023899 identifica, entre otras, oportunidades de automatización en: tuberías enterradas de agua de servicio; soportes de componentes; estructuras de toma y descarga de agua de refrigeración; ducto de bus isofásico; mapeo tridimensional de radiación; detección de fugas en contención; espárragos y alojamientos de la tapa del reactor; tanques de almacenamiento de agua; contenedores de combustible en seco; rondas de operación; protección contra incendios; y tubos de generador de vapor.

::: nota riesgo | Esta lista no es una lista de productos
Varias de esas tareas corresponden a mercados ya maduros. La lista sirve para orientar la búsqueda y para cruzarla con horas-hombre y brechas tecnológicas, no para elegir un producto.
:::

### 15.4 Barrido por problema físico

Espacio confinado · inspección inaccesible · inspección con rotor instalado · sin desmontaje · sin andamiaje · sin excavación · sin drenaje · sin buceo · sin desenergización · en sitio · inspección en línea · inspección interna · ensayos no destructivos robotizados y remotos · inspección autónoma · inspección combinada con reparación · inspección combinada con limpieza · recuperación de material extraño.

### 15.5 Activos adicionales a evaluar

Condensadores refrigerados por aire · condensadores · torres de refrigeración · paredes de agua de caldera · headers de caldera · internos de hogar · zonas de escape y combustión de turbina de gas · internos de turbina de vapor · palas y torres de aerogeneradores · monopilotes marinos · presas · vertederos · compuertas de toma · válvulas de gran tamaño · intercambiadores de calor · chimeneas · hornos industriales · recipientes y tuberías petroquímicas · activos mineros cuando la tecnología sea transferible.

---

# Parte III — Método de evaluación y economía

## 16. Ficha estándar por candidato

Todos los candidatos se documentan con la misma ficha de 23 campos. La uniformidad es lo que permite comparar; una ficha incompleta se marca como incompleta y no se completa con supuestos.

::: tarjetas 2
::: tarjeta 1 · Activo y problema
Qué se inspecciona, cuál es el mecanismo de falla y por qué importa para la operación.
:::
::: tarjeta 2 · Cómo se inspecciona hoy
Rotor extraído, desmontaje, andamiaje, buceo, entrada de personal; frecuencia, duración, personal, salida de servicio y riesgos.
:::
::: tarjeta 3 · Dolor económico verificable
Costo directo, costo de parada, costo de acceso, horas-hombre, pérdida por falla y ejemplos reales. Separando dato publicado de estimación.
:::
::: tarjeta 4 · Propuesta de robot
Locomoción, dimensiones aproximadas, sensores, ensayo no destructivo, tether o inalámbrico, autonomía, mapeo y localización, manipulación y recuperación. A nivel de requisitos, no de diseño.
:::
::: tarjeta 5 · Valor creado
Qué operación evita, cuánto tiempo reduce, cuánta cobertura agrega, cuánta confiabilidad mejora y cuánto riesgo disminuye.
:::
::: tarjeta 6 · Robots y productos existentes
Registro obligatorio en tabla, incluyendo productos vivos, sistemas sólo de servicio, prototipos, discontinuados y patentes.
:::
::: tarjeta 7 · Cómo lo resolvieron los existentes
Adhesión, ruedas, orugas o magnetismo, arquitectura serpiente o continua, tether, energía, acoplamiento del sensor, contacto del ensayo, superación de obstáculos, alineación, recuperación y material extraño.
:::
::: tarjeta 8 · Qué no resuelven
Identificación del hueco real. Es el campo que decide si hay producto.
:::
::: tarjeta 9 · Mercado y madurez
Posición en la escala M0–M5, sin confundir nivel tecnológico con madurez comercial.
:::
::: tarjeta 10 · Barreras técnicas
Geometría, temperatura, radiación, interferencia electromagnética, fluidos, suciedad, corrosión, tether, adhesión, batería, sensado y calibración del ensayo.
:::
::: tarjeta 11 · Riesgo de atascamiento y recuperación
Filosofía de falla segura y procedimiento de recuperación como parte del producto.
:::
::: tarjeta 12 · Regulación y calificación
Ámbito nuclear, calificación de ensayos no destructivos, alta tensión, espacio confinado, frontera de presión y códigos aplicables.
:::
::: tarjeta 13 · Patentes y propiedad intelectual
Familias principales, titulares, estado legal, riesgo de bloqueo y áreas posiblemente libres.
:::
::: tarjeta 14 · Desarrollo estimado
Separado en plataforma, carga sensora, ensayo no destructivo, software, calificación y validación de campo. Con rango y justificación.
:::
::: tarjeta 15 · Modelo de negocio
Venta, alquiler, servicio, precio por inspección, contrato anual o suscripción de datos y analítica.
:::
::: tarjeta 16 · Cliente y comprador
Utility, fabricante, contratista de parada, empresa de ensayos, aseguradora o propietario del activo. Debe identificarse quién firma la orden de compra.
:::
::: tarjeta 17 · Frecuencia de compra
Fundamentada con evidencia, no supuesta.
:::
::: tarjeta 18 · Tamaño de mercado
Sólo si hay datos suficientes. Separado en global, Estados Unidos, Latinoamérica y Argentina.
:::
::: tarjeta 19 · Precio y {{t:ticket|ticket}}
Precios publicados, licitaciones, contratos, cotizaciones o comparables. No se inventa.
:::
::: tarjeta 20 · Reutilización de la plataforma existente
Puntuación por subsistema: locomoción, cómputo, cámaras, iluminación, tether, lógica programable, encoders, software, mapeo, generación de informes y arquitectura de seguridad.
:::
::: tarjeta 21 · Defensa posible
Mecánica, ensayo no destructivo, conjunto de datos, calibración, software, calificación, flujo de trabajo de servicio y patentes.
:::
::: tarjeta 22 · {{t:go-nogo|Decisión de avance}}
Avanzar o no avanzar, con conclusión breve y sin ambigüedad.
:::
::: tarjeta 23 · Confianza
Alta, media o baja, explicando qué dato falta para elevarla.
:::
:::

### 16.1 Registro obligatorio de productos existentes

| Producto | Fabricante | Año | Estado 2026 | Locomoción | Carga sensora / NDE | Dimensiones | Despliegues | Precio o servicio | Fuente |
|---|---|---:|---|---|---|---|---|---|---|

## 17. Dimensionamiento de mercado

No se usan como base informes genéricos del tipo «mercado de robots de inspección». El cálculo se construye **{{t:bottom-up|de abajo hacia arriba}}**, y su resultado es el mercado total direccionable de servicios ({{t:tam|TAM}}):

`Activos direccionables × inspecciones por año × ticket de servicio = mercado de servicios`

Se publican tres escenarios —bajo, base y alto— con la fuente de cada entrada. **Si falta información crítica, no se fabrica el número.**

### 17.1 Anclaje verificado: horas-hombre por tarea

EPRI publica, a partir del análisis de su base de órdenes de trabajo, el consumo de horas-hombre por caso de uso. Es el punto de partida para el cálculo de abajo hacia arriba del costo evitado, y evita construir el dimensionamiento sobre supuestos propios.

| Caso de uso | Frecuencia declarada | Horas-hombre por unidad y por año |
|---|---|---|
| Tuberías de agua de servicio, enterradas y sobre nivel | Inspección dirigida cada 10 años; cada 3 a 5 años en la década previa al fin de vida de diseño | 5.000 a 10.000 |
| Estructuras de toma y descarga de agua de refrigeración | Entre anual y cada 5 años, según condición observada | 50 a 1.500, con el rango gobernado por la calidad del agua |
| Rondas de operación | Diarias | ≈ 1.400, unas 4 horas por día |
| Vigilancia contra incendios | Variable, de semanal a mayor | 500 a 1.500 |
| Mapa tridimensional de radiación | Línea de base cada 10 años | 250 a 750 en trabajo emergente |
| Tanques de almacenamiento de agua | Inspección completa en cada período de 10 años | 50 a 500, tanques de condensado |
| Espárragos y alojamientos de la tapa del reactor | Aproximadamente cada parada | 150 o más por parada |
| Detección de fugas en contención | Emergente, creciente con la edad de la planta | ≈ 50 |
| Tubos de generador de vapor | Cada parada o cada dos paradas | ≈ 50 con la tecnología existente |

Fuente: EPRI, *Robotic Process Automation for Nuclear Power Plants: Evaluation of Near-Term Opportunities*, 3002023899, junio 2022, tablas 1 a 12. {{ev:A}}

::: nota inferencia | Qué dice esta tabla sobre dónde está el negocio
Las mayores bolsas de horas no corresponden a las tareas más difíciles: tuberías de agua de servicio, rondas de operación y vigilancia contra incendios concentran mucho más tiempo que las inspecciones especializadas. Pero son tareas de alta frecuencia y baja complejidad, que compiten contra plataformas de propósito general ya comerciales.

El negocio del tipo de robot que este estudio evalúa no está en las horas totales sino en el **costo evitado por intervención**: parada, andamiaje, excavación, buceo o izaje pesado. La tabla sirve para dimensionar, no para elegir.
:::

### 17.2 Fuentes preferidas por región

::: tarjetas 2
::: tarjeta Estados Unidos
EIA, NRC, DOE, FERC y NERC; informes públicos de utilities; y EPRI.
:::
::: tarjeta Nuclear global
Base de datos PRIS del OIEA como fuente primaria; la World Nuclear Association sólo como fuente secundaria.
:::
::: tarjeta Argentina
CAMMESA, Secretaría de Energía, ENRE, Nucleoeléctrica Argentina, Transener, empresas generadoras y operadores de ciclo combinado e hidroeléctricos.
:::
::: tarjeta Latinoamérica
Ministerios, operadores de sistema y utilities; OLADE y CIER; siempre sobre bases públicas verificables.
:::
:::

## 18. Economía del cliente

El análisis mira la decisión desde el lado del cliente, no desde el costo del producto.

::: fig fig-valor | Figura 16 — Componentes del valor creado por una inspección robotizada. | Elaboración propia.
:::

Cada componente se documenta por separado y con su fuente. **No se asigna valor monetario arbitrario a la seguridad**: se declara como beneficio no monetizado cuando no hay base para cuantificarlo.

Se buscan ejemplos reales y verificables de: días de parada, andamiaje, excavación, vaciado de conducto, drenaje de tanque, extracción de rotor, entrada de personal a espacio confinado, operación de buceo y maniobras de izaje pesado.

## 19. Rankings y análisis de sensibilidad

Se construyen dos rankings con criterios distintos, porque responden a preguntas distintas: cuál es el mejor próximo producto ({{t:fast-follow|seguidor rápido}}) y cuál es la posición más defendible a largo plazo ({{t:moat|moat}}, con su {{t:upside|potencial de crecimiento}}).

::: fig fig-pesos | Figura 17 — Pesos comparados de los criterios en ambos rankings. | Elaboración propia; los pesos son una decisión de método.
:::

::: nota inferencia | Los puntajes no son mediciones
Los puntajes son una **síntesis de ingeniería y de negocio**, y así deben etiquetarse en el informe. Los pesos pueden modificarse si se justifica el cambio, pero entonces debe recalcularse el orden completo.
:::

### 19.1 Sensibilidad obligatoria

En el {{t:sensibilidad|análisis de sensibilidad}} se recalcula el ranking moviendo ±20 % el peso de competencia, de esfuerzo de desarrollo y de tamaño de mercado. Si el ganador cambia con esas variaciones, la recomendación debe declararse **inestable** y la decisión debe esperar a la evidencia que estabilice el criterio dominante.

## 20. Prior art, patentes y competidores

### 20.1 Screening preliminar de propiedad intelectual

Para los cinco candidatos mejor posicionados se realiza búsqueda formal en Google Patents, Espacenet, WIPO Patentscope y USPTO, combinando el activo con: inspección robótica, crawler, inspección remota, ensayo no destructivo, trepado de paredes, robot serpiente, vehículo de inspección y manipulador.

| Familia | Prioridad | Titular | Qué reivindica | Estado legal | Riesgo para el proyecto |
|---|---|---|---|---|---|

::: nota riesgo | Alcance del análisis
Esto **no** constituye una opinión legal de libertad de operación. Es un screening preliminar orientado a detectar bloqueos evidentes y áreas potencialmente libres.
:::

### 20.2 Mapa de actores por oportunidad

Para cada oportunidad se identifican por separado seis papeles, porque rara vez los cumple la misma empresa:

1. **Fabricante del robot**: quién construye el hardware.
2. **Proveedor del ensayo no destructivo**: quién fabrica o posee el sensor.
3. **Empresa de servicio**: quién vende efectivamente la inspección.
4. **Integrador**: quién combina plataforma y sensor.
5. **Tecnología desarrollada por la utility**: si el cliente resolvió el problema internamente.
6. **Derivación universitaria**: si existe una empresa surgida de un grupo de investigación.

Se registra además el historial de adquisiciones —un producto puede haber cambiado de dueño o de nombre— y el estado a 2026: activo, discontinuado, adquirido, sin comercialización o indeterminado. Para productos desaparecidos se recurre al Internet Archive y a folletos archivados; las redes profesionales se usan sólo como pista inicial, nunca como evidencia.

### 20.3 Licitaciones y contratos como fuente de verdad comercial

Un contrato adjudicado dice más sobre el mercado que cualquier informe de tamaño de mercado. Se buscan {{t:licitacion|licitaciones, pedidos de cotización}} y adjudicaciones reales por servicio de inspección, inspección robótica, bus isofásico, inspección de HRSG, inspección de vaults, tuberías enterradas, conductos forzados, contenedores en seco, crawlers e inspección visual remota, en portales oficiales de compras de utilities, estatales, federales, municipales y nucleares cuando sean públicos.

De cada uno se extrae: alcance, frecuencia, requisitos, duración, monto adjudicado si aparece y proveedor ganador.

## 21. Argentina y Latinoamérica

Para los tres candidatos mejor posicionados se desarrolla un capítulo específico que responde:

1. ¿Cuántos activos de ese tipo existen en Argentina?
2. ¿Quiénes los operan?
3. ¿Quién realiza hoy la inspección?
4. ¿Se contrata al fabricante internacional o a un servicio local?
5. ¿Podría prestarse el servicio regional desde Argentina?
6. ¿Qué requisitos de importación y calibración implica?
7. ¿Existen integradores o socios locales de ensayos no destructivos?
8. ¿Hay centrales con equipamiento de los grandes fabricantes donde el canal comercial sea similar al del producto de referencia?
9. ¿Qué mercados vecinos son naturales: Brasil, Chile, Uruguay, Paraguay, Perú, Colombia o México?

Las cantidades se toman de fuentes oficiales del sector y de los operadores. **No se estiman cantidades de activos sin fuente.**

## 22. Costos de desarrollo

Para cada candidato de la lista corta se estima por separado: diseño mecánico, prototipo, electrónica, sensores y ensayos no destructivos, tether y alimentación, software y control, navegación autónoma, gestión de datos e informes, banco de pruebas, maqueta de ensayo, calificación de campo, certificación y utillaje de fabricación.

Se prefieren **rangos amplios antes que falsa precisión**, y se distinguen cuatro magnitudes que suelen confundirse:

- costo de construir un prototipo;
- {{t:nre|ingeniería no recurrente}} para industrializar;
- costo unitario aproximado en producción;
- costo del kit de servicio de campo.

Se buscan precios reales de los componentes críticos siempre que sea posible.

---

# Parte IV — Entregables, validación y cierre

## 23. Estructura y requisitos del informe final

### 23.1 Estructura

El informe final se organiza en: portada; resumen ejecutivo de tres páginas como máximo; objetivo y alcance; metodología y evidencia; qué hace atractivo un negocio de robótica de inspección; mapa completo de oportunidades; fichas por candidato; panorama competitivo transversal; panorama de patentes; mercado global, de Estados Unidos, de Latinoamérica y de Argentina; economía del cliente; matriz de comparación; rankings con sensibilidad; conceptos de producto para los tres primeros; lista de oportunidades a no perseguir por ahora; incógnitas y {{t:due-diligence|debida diligencia}} pendiente; conclusiones; y anexos de registro de búsquedas, competidores, patentes y fuentes.

### 23.2 Requisitos de presentación

::: tarjetas 2
::: tarjeta Estilo
Limpio, técnico y ejecutivo. Legible y adaptable a pantalla e impresión. Tablas largas con encabezado fijo, índice navegable y llamados diferenciados para hallazgo, riesgo, inferencia y dato verificado. Sin saturación de color.
:::
::: tarjeta Componentes
Tarjetas de resultado ejecutivo, matriz de comparación, notas de fuente desplegables, distintivos de nivel de evidencia A–D, de madurez M0–M5 y de confianza.
:::
::: tarjeta Gráficos requeridos
Valor frente a madurez de mercado; reutilización de plataforma frente a dificultad de desarrollo; comparación de puntajes; línea temporal de prior art de los tres primeros; economía del cliente convencional frente a robotizada cuando existan cifras reales; y panorama de proveedores por oportunidad.
:::
::: tarjeta Qué evitar
Lenguaje de marketing, afirmaciones sin sustento, imágenes decorativas, gráficos tridimensionales, tablas ilegibles y relleno sin contenido.
:::
:::

Toda gráfica debe indicar su fuente, diferenciar dato de puntaje y no inventar precisión numérica.

### 23.3 Imágenes

Se usan imágenes cuando ayudan a entender geometría del activo, robot existente, mecanismo de acceso, herramienta de ensayo o arquitectura propuesta, con este orden de preferencia: instituto de investigación sectorial, fabricante, caso de utility, literatura técnica y patente. Cada imagen lleva epígrafe, sistema y fabricante, fuente, dirección y fecha de consulta.

Si la licencia no permite incorporación confiable, se enlaza la fuente o se elabora un esquema original claramente identificado como tal, como los de este documento. Los archivos gráficos se guardan localmente para que el informe sea autocontenido.

### 23.4 Referencias

Las referencias se colocan junto a la afirmación que sostienen, no en una bibliografía desconectada. Ejemplo del formato esperado:

> EPRI reporta que una utility pagó aproximadamente USD 100.000 por una implementación de inspección robótica de bus isofásico y que la ejecución tomó menos de un día [EPRI-MTA-029].

Cada referencia registra organización o autor, título, fecha, identificador de producto, DOI o número de patente, dirección, fecha de acceso y nivel de evidencia.

### 23.5 Archivos que componen la entrega

- informe completo en formato navegable;
- registro de fuentes con nota de qué sostiene cada una;
- tabla de evidencia con candidato, afirmación, valor, unidad, identificador de fuente, tipo, nivel, dirección, fecha de acceso, confianza y notas;
- tabla de competidores con producto, empresa, aplicación, estado, país, tecnología, dimensiones, carga sensora, despliegues, precio y fuente;
- tabla de patentes;
- carpeta de imágenes y gráficos generados;
- registro de investigación con consultas realizadas, bases consultadas, pistas descartadas y fuentes que no pudieron obtenerse.

## 24. Preguntas que el informe debe responder

::: tarjetas 2
::: tarjeta Decisión
1. Si hubiera que invertir hoy en un solo robot después del producto de referencia, ¿cuál sería?
2. ¿Por qué pagaría un cliente por él?
3. ¿Qué costo concreto se le evita?
4. ¿Qué ticket de servicio puede sostener?
5. ¿Cuántas oportunidades de servicio existen por año?
:::
::: tarjeta Competencia
6. ¿Quién hace esto hoy?
7. ¿Por qué el producto propuesto sería mejor o diferente?
8. ¿Qué tan difícil es copiarlo?
9. ¿Qué propiedad intelectual puede bloquearlo?
:::
::: tarjeta Ejecución
10. ¿Qué parte de la plataforma actual se reutiliza?
11. ¿Cuánto desarrollo falta?
12. ¿Cuál es el primer {{t:mvp|producto mínimo viable}} que un cliente pagaría por probar?
13. ¿Qué validación técnica sería suficiente?
14. ¿Cuál es el principal mecanismo de fracaso?
:::
::: tarjeta Alcance
15. ¿Qué robot no debería desarrollarse aunque parezca atractivo?
16. ¿Qué oportunidad nueva apareció durante la investigación?
17. ¿Qué información no existe públicamente y requiere entrevistas?
18. ¿A qué diez personas u organizaciones debería contactarse primero?
:::
:::

## 25. Programa de entrevistas

Para los tres candidatos mejor posicionados se define una lista concreta de entrevistas de {{t:customer-discovery|descubrimiento de clientes}}. Los perfiles a cubrir son: responsable de mantenimiento de generadores; responsable de paradas; responsable de ensayos no destructivos; jefe de planta; ingeniero de cables de transmisión; especialista en calderas de recuperación; responsable de servicio del fabricante de equipos; líder técnico del instituto de investigación sectorial; proveedor de servicios de ensayos no destructivos; e ingeniero de riesgo o de seguros cuando aplique.

Se preparan entre 8 y 12 preguntas por segmento, orientadas a: costo actual, frecuencia, dolor operativo, fallas sufridas, disposición a pagar, requisitos de aceptación, recuperación de herramienta y material extraño, proceso de compra e incumbente.

## 26. Criterio de finalización

El informe no se cierra porque «haya suficiente información». Se cierra cuando esta lista está completa:

- [ ] Se recorrió el índice completo de productos de robótica y tecnologías móviles del instituto sectorial.
- [ ] Se recorrió el catálogo de modernización de plantas buscando robótica e inspección.
- [ ] Se buscó cada activo combinado con robótica.
- [ ] Se buscó cada activo **sin** la palabra robot, para encontrar métodos competidores.
- [ ] Se investigaron al menos los siete candidatos principales.
- [ ] Se buscaron candidatos nuevos fuera de la lista inicial.
- [ ] Se hizo búsqueda profunda de competidores para los cinco primeros.
- [ ] Se hizo screening de patentes para los cinco primeros.
- [ ] Se buscaron licitaciones y contratos para los tres primeros.
- [ ] Se verificó el estado 2026 de cada competidor principal.
- [ ] Se buscó precio o ticket cuando existe.
- [ ] Cada número relevante tiene referencia inmediata.
- [ ] Cada afirmación de fabricante está etiquetada como tal.
- [ ] Cada inferencia está etiquetada como tal.
- [ ] Se documentó la evidencia negativa encontrada.
- [ ] Se hizo dimensionamiento de mercado de abajo hacia arriba, o se explicó por qué no es defendible.
- [ ] Se desarrolló el capítulo de Argentina y Latinoamérica para los tres primeros.
- [ ] Se hizo el análisis de sensibilidad del ranking.
- [ ] Se definieron los tres candidatos principales.
- [ ] Se definió la lista de oportunidades a no perseguir por ahora.
- [ ] Se listaron las incógnitas pendientes.
- [ ] Se listaron las entrevistas y contactos prioritarios.
- [ ] Se verificó que el informe sea autocontenido y abra correctamente.

## 27. Conclusión operativa

::: nota clave | Principio rector
La prioridad no es defender una solución: es no enamorarse de ninguna. Si la evidencia muestra que el bus isofásico está saturado, que el incumbente de HRSG cerró el hueco, que la robótica de vaults no tiene economía, que existe un producto desconocido que invalida la propuesta o que otra aplicación ofrece un negocio mucho mejor, **el ranking cambia**.
:::

El resultado debe permitir tomar una decisión de inversión con tres cosas claramente separadas: lo que sabemos, lo que inferimos y lo que todavía debemos validar. Y la conclusión debe responder sin ambigüedad cuál debería ser el próximo robot a desarrollar, y por qué.

---

# Anexos

## Anexo A — Paquete de fuentes verificado

Fuentes iniciales verificadas a la fecha de corte. No reemplazan la investigación: son el punto de partida.

| # | Fuente | Referencia y dirección | Nivel | Qué sostiene |
|---:|---|---|:--:|---|
| 1 | EPRI — *Robotic Process Automation for Nuclear Power Plants: Evaluation of Near-Term Opportunities*, junio 2022 | 3002023899 · https://restservice.epri.com/publicdownload/000000003002023899/0/Product | {{ev:A}} | Catálogo de tareas de alto valor, horas-hombre, brechas tecnológicas, distinción entre teleoperación y autonomía, y criterio de selección de tareas |
| 2 | EPRI — *Program on Technology Innovation: Landscape of Automation in Nuclear Power Plants* | 3002025693 · https://restservice.epri.com/publicdownload/000000003002025693/0/Product | {{ev:A}} | Robots a medida para tareas de alto valor y baja frecuencia; uso frecuente de proveedores externos; costo y plazo de desarrollar plataformas propias |
| 3 | EPRI — Unmanned Mobile Technologies Collaboration Group, índice de productos | https://transmission.epri.com/p37_substations/robotics/mobiletechgrp/products/ | {{ev:A}} | Catálogo sectorial de desarrollos robóticos, a recorrer completo y no sólo por títulos evidentes |
| 4 | EPRI — Transmisión subterránea, actualizaciones de investigación | https://transmission.epri.com/p36_underground/public/p36001_design_construction/research_updates/ | {{ev:A}} | Continuidad del trabajo de inspección robótica de vaults en 2026 y 2027 |
| 5 | EPRI — Transmisión subterránea, aplicaciones | https://transmission.epri.com/p36_underground/public/p36_applications/ | {{ev:A}} | Estado declarado: prototipo desarrollado, ensayos de laboratorio y demostración en planificación |
| 6 | EPRI — Transmisión subterránea, referentes del programa | https://transmission.epri.com/p36_underground/leads/ | {{ev:A}} | Interlocutores técnicos para validación directa |
| 7 | EPRI — *Reduce Inspection Cost for Isophase Bus Duct Using Robotic Crawler* | MTA-MA-029 · https://nuclearplantmod.epri.com/MTA-MA-029 | {{ev:A}} | Costo de proveedor, duración, razón de reducción y payback en bus isofásico |
| 8 | EPRI — *Isolated Phase Bus Maintenance Guide* | 1015057 · https://restservice.epri.com/publicdownload/000000000001015057/0/Product | {{ev:A}} | Frecuencia de inspección, defectos, accesos, plataformas robóticas y mediciones eléctricas |
| 9 | Trident NGS | https://www.tridentngs.com/ | {{ev:C}} | Oferta comercial de servicios de inspección de bus isofásico |
| 10 | EPRI — *Study for Snake Robot Technology for Inspection of Headers and Tubes in Heat Recovery Steam Generators*, 2009 | 1017635 · https://restservice.epri.com/publicdownload/000000000001017635/0/Product | {{ev:A}} | Por qué la inspección convencional no alcanza el interior de los tubos, geometrías, accesos y conceptos evaluados |
| 11 | TesTex — Servicios para HRSG | https://testex-ndt.com/services/hrsg/ | {{ev:C}} | Alcance comercial declarado |
| 12 | TesTex — Internal Access Tool (IAT) | https://testex-ndt.com/products/iat-internal-access-tool-for-hrsg-inspections/ | {{ev:C}} | Arquitectura, diámetro de acceso y cobertura declarada |
| 13 | TesTex — Claw, herramienta de inspección de soldaduras | https://testex-ndt.com/products/claw-bfet-inspection-tool/ | {{ev:C}} | Rendimiento declarado por turno y accesibilidad |
| 14 | EPRI — Inspección de tuberías enterradas con crawler | MTA-MA-017 · https://nuclearplantmod.epri.com/MTA-MA-017 | {{ev:A}} | Costo de implementación, rango de ahorro por utilización y madurez comercial |
| 15 | EPRI — *Compilation of Lessons Learned on Buried and Underground Piping* | 1025272 · https://restservice.epri.com/publicdownload/000000000001025272/0/Product | {{ev:A}} | Limitaciones geométricas, revestimientos, ausencia de lanzador y receptor, y eventos de material extraño |
| 16 | Diakont — Primera inspección en línea de tubería enterrada | https://diakont.com/case-studies/nuclear-solutions/first-buried-piping-in-line-inspection/ | {{ev:C}} | Existencia de despliegue comercial en el sector nuclear |
| 17 | EPRI — *ROV Technology: Applications and Advancements at Hydro Facilities* | TR-113584-V7 / 1007576 · https://restservice.epri.com/publicdownload/000000000001007576/0/Product | {{ev:A}} | Aplicaciones en túnel y penstock, limitaciones de tether y ahorro por evitar vaciado |
| 18 | EPRI Journal — Robots trepadores para inspección de contenedores en seco | https://eprijournal.com/wall-climbing-robots-inspect-nuclear-storage-casks/ | {{ev:B}} | Configuración sensora y reducción de costo frente a izaje pesado |
| 19 | Robotic Technologies of Tennessee | https://www.robotictechtn.com/ | {{ev:C}} | Declaración de uso de sus plataformas en instalaciones nucleares |
| 20 | EPRI — Catálogo de informes de generación y portal tecnológico | https://dx-wiki.epri.com/Generation_Reports · https://techportal.epri.com/ | {{ev:A}} | Herramienta de descubrimiento de estudios adicionales, incluidos los de robots everting |

### Fuentes incorporadas durante el barrido ampliado

| # | Fuente | Referencia y dirección | Nivel | Qué sostiene |
|---:|---|---|:--:|---|
| 21 | Air Cooled Condenser Users Group — *ACC.01: Guidelines for Internal Inspection of Air-Cooled Condensers*, mayo 2015 | https://competitivepower.us/pub/pdfs/guidelines-for-internal-inspection-of-air-cooled-condensers-2015.pdf | {{ev:B}} | Cobertura de inspección incompleta en ductos superiores, condiciones de acceso y espacio confinado, y mecanismo de falla por corrosión del lado vapor |
| 22 | EPRI 3002023899, tablas 1 a 12 | https://restservice.epri.com/publicdownload/000000003002023899/0/Product | {{ev:A}} | Horas-hombre y frecuencia por caso de uso; frecuencia decenal de la inspección de bus isofásico |
| 23 | U.S. Bureau of Reclamation, ficha de proyecto 9612 | https://www.usbr.gov/research/projects/detail.cfm?id=9612 | {{ev:A}} | Túnel de toma inaccesible para buzos por profundidad, longitud y espacio confinado, y ausencia de programa propio de inspección con vehículo remoto |
| 24 | *Combined Cycle Journal*, limpieza y detección de fugas en condensadores refrigerados por aire | https://www.ccj-online.com/air-cooled-condensers-effective-cleaning-and-leak-detection/ | {{ev:C}} | Escala del activo y práctica actual de detección de fugas con gas trazador |
| 25 | EPRI Journal, robótica en centrales | https://eprijournal.com/robotics-in-power-plants-getting-smaller-smarter/ | {{ev:B}} | Metodología con cámara acústica en dron para condensadores refrigerados por aire |
| 26 | Patente US 8717742, aparamenta blindada con interruptor extraíble | https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8717742 | {{ev:A}} | Costo de intervención declarado: inspeccionar por dentro exige cortar servicio y evacuar el gas aislante |

La bitácora completa del barrido —consultas realizadas, hallazgos con su clase y nivel, y pistas descartadas— se conserva junto a este informe como registro de investigación.

## Anexo B — Registro de hallazgos iniciales

Hallazgos ya verificados en fuentes primarias o actuales. Deben releerse en su contexto antes de utilizarse en una conclusión.

| Candidato | Hallazgo | Clase | Consecuencia para la decisión |
|---|---|---|---|
| A · Bus isofásico | Inspección con soporte de proveedor por aproximadamente USD 100.000, ejecución en menos de un día, reducción de costo cercana a 10× frente al método manual en ese caso, payback inmediato y disponibilidad comercial alta | {{ev:A}} Hecho | Demuestra mercado y valor, pero también que un crawler con cámara solo ya existe |
| D · Piping enterrado | Ahorro esperado mayor a un millón y menor a cinco millones por utilización, implementación menor a un millón, payback menor a un año, ya comercial en el sector nuclear | {{ev:A}} Hecho | Gran valor con madurez alta: sólo entra un hueco geométrico o de despliegue muy concreto |
| B · HRSG | Ciertos tubos interiores no pueden inspeccionarse con ensayos convencionales sin acceso destructivo; la robótica tipo serpiente fue estudiada para ese problema | {{ev:A}} Hecho | El problema es real y está documentado |
| B · HRSG | Herramienta de acceso interno con sonda de campo remoto y video, crawler dentro del header y despliegues en múltiples sitios | {{tipo:Declaración}} | La oportunidad debe reevaluarse contra un incumbente real y activo |
| C · Vaults | Programa vigente 2025–2027 con prototipos, ensayos de laboratorio y demostraciones en sitios de utilities, orientado a seguridad y reducción de salidas de servicio | {{ev:A}} Hecho | Señal de problema vigente y tecnología aún en evolución |
| H · Condensador por aire | Es irreal esperar que se inspeccione más de uno o dos de los ductos superiores de una unidad durante una parada | {{ev:B}} Hecho | La necesidad está declarada por los operadores y hoy no está cubierta |
| A · Bus isofásico | Las inspecciones se realizan típicamente cada 10 años | {{ev:A}} Hecho | Recurrencia baja: penaliza el caso de servicio y obliga a dimensionar por inspecciones anuales |

## Anexo C — Glosario con fuente de cada definición

Cada entrada indica **dónde puede verificarse la definición**. Cuando un término no tiene definición normativa y se usa como convención comercial, se declara explícitamente como *definición operativa de este informe* en lugar de atribuirle una fuente que no existe.

En el cuerpo del informe, la primera aparición de cada término enlaza a su entrada: con línea de puntos en la versión navegable y con una marca <sup>G</sup> en la versión impresa.

### C.1 Términos de negocio

::: glosario
tam || Mercado total direccionable (TAM) || Valor anual de todo el mercado al que un producto podría aspirar si capturara el 100 % de la demanda que resuelve. Se acompaña de SAM (la parte alcanzable con el canal y la geografía reales) y SOM (la parte capturable en el horizonte de planificación). || Blank, S. y Dorf, B., *The Startup Owner's Manual*, K&S Ranch, 2012. {{ev:B}}
bottom-up || Dimensionamiento de abajo hacia arriba || Cálculo del mercado partiendo de unidades verificables —cantidad de activos, inspecciones por año, precio por inspección— en lugar de tomar un porcentaje de una cifra global publicada. Es el método que este informe exige. || Blank, S. y Dorf, B., *The Startup Owner's Manual*, K&S Ranch, 2012. {{ev:B}}
payback || Período de repago (payback) || Tiempo que tarda un proyecto en generar flujos de caja suficientes para recuperar la inversión inicial. Es un criterio de liquidez y de riesgo, no de rentabilidad: no considera el valor del dinero en el tiempo ni lo que ocurre después de recuperada la inversión. || Brealey, R., Myers, S. y Allen, F., *Principles of Corporate Finance*, McGraw-Hill (capítulo de criterios de decisión de inversión). {{ev:B}}
caso-negocio || Caso de negocio || Documento que justifica la inversión: necesidad, alternativas evaluadas, costos, beneficios esperados, riesgos y criterio de éxito. Es la base sobre la que se aprueba o se rechaza el desarrollo. || Project Management Institute, *Guía de los fundamentos para la dirección de proyectos* (Guía del PMBOK). {{ev:B}}
moat || Ventaja defendible (moat) || Característica estructural que permite sostener rentabilidad frente a la competencia durante años: patentes, costos de cambio, escala, datos propietarios, calificación regulatoria o relación de servicio. El término proviene del análisis de inversión y equivale a una barrera de entrada sostenida en el tiempo. || Porter, M., *Competitive Strategy*, Free Press, 1980 (barreras de entrada); Buffett, W., carta anual a los accionistas de Berkshire Hathaway, 2007 (uso del término *economic moat*). {{ev:B}}
incumbente || Incumbente || Empresa que ya vende hoy el producto o servicio en el mercado que se analiza. Su existencia no invalida una oportunidad, pero obliga a demostrar una ventaja concreta y no una capacidad equivalente. || Porter, M., *Competitive Strategy*, Free Press, 1980. {{ev:B}}
whitespace || Espacio no cubierto (whitespace) || Parte de la necesidad del cliente que ningún proveedor actual resuelve: una geometría a la que no llega la herramienta existente, una medición que no se ofrece o un modo de despliegue que no está disponible. || Johnson, M. W., *Seizing the White Space*, Harvard Business Press, 2010. {{ev:B}}
ticket || Precio por servicio (ticket) || Monto efectivamente facturado por una inspección o intervención. En este informe se usa siempre con su fuente: precio publicado, contrato, licitación adjudicada o cotización. No es un término normalizado. || Definición operativa de este informe.
recurrencia || Recurrencia || Frecuencia con la que un mismo cliente vuelve a comprar el servicio, medida en inspecciones por activo y por año. Determina si el negocio es un proyecto aislado o un ingreso repetido. || Definición operativa de este informe.
raas || Robótica como servicio (RaaS) || Modelo en el que el cliente no compra el robot sino el resultado de la inspección, y el proveedor conserva la propiedad, el mantenimiento y la calibración del equipo. Es preferible cuando la frecuencia por activo es baja y el precio por intervención es alto. || Definición operativa de este informe, sobre el modelo general de servicios gestionados.
mvp || Producto mínimo viable (MVP) || Versión más reducida del producto que permite aprender del cliente real con el menor esfuerzo: en este contexto, la primera inspección que un cliente pagaría por probar. || Ries, E., *The Lean Startup*, Crown Business, 2011. {{ev:B}}
customer-discovery || Descubrimiento de clientes || Proceso de entrevistas estructuradas con clientes potenciales para verificar que el problema, el costo actual y la disposición a pagar existen antes de construir el producto. || Blank, S., *The Four Steps to the Epiphany*, Cafepress, 2005. {{ev:B}}
go-nogo || Decisión de avance (go / no-go) || Punto formal de decisión en el que un proyecto se aprueba, se detiene o se reorienta según criterios definidos de antemano. || Cooper, R. G., *Winning at New Products* (proceso por etapas y compuertas). {{ev:B}}
due-diligence || Debida diligencia || Verificación sistemática de los supuestos de una inversión —mercado, competencia, propiedad intelectual, costos y riesgos— antes de comprometer capital. || Uso estándar en finanzas corporativas; definición de referencia divulgativa en Investopedia, *Due Diligence*. {{ev:C}}
nre || Ingeniería no recurrente (NRE) || Costo que se paga una sola vez para dejar un producto en condiciones de fabricarse: diseño, herramientas, moldes, ensayos de calificación. No se reparte por unidad producida salvo que se amortice. || Uso estándar en manufactura electrónica y de bienes de capital; definición operativa de este informe.
licitacion || Licitación y pedido de cotización (RFP / RFQ) || Documentos con los que un comprador solicita propuestas o precios. El pliego revela alcance, frecuencia y requisitos reales; la adjudicación revela precio y proveedor ganador. Por eso este informe los prefiere frente a los informes de tamaño de mercado. || Project Management Institute, *Guía del PMBOK*, procesos de adquisiciones. {{ev:B}}
sensibilidad || Análisis de sensibilidad || Recálculo de un resultado variando los supuestos de entrada, para saber si la conclusión depende de un dato incierto. Aquí se aplica a los pesos del ranking. || Brealey, R., Myers, S. y Allen, F., *Principles of Corporate Finance*, McGraw-Hill. {{ev:B}}
benchmark || Referencia de comparación (benchmark) || Caso ya conocido contra el cual se mide una oportunidad nueva. En este informe, el proyecto de robot de inspección de generadores. || Definición operativa de este informe.
fast-follow || Seguidor rápido (fast-follow) || Estrategia de entrar a un mercado que otro abrió, con menor riesgo técnico y menor margen de diferenciación. Es el criterio del Ranking A. || Definición operativa de este informe.
upside || Potencial de crecimiento (upside) || Valor que una oportunidad podría alcanzar en el escenario favorable, por encima del caso base. Es el criterio del Ranking B. || Definición operativa de este informe.
:::

### C.2 Términos técnicos y del sector

::: glosario
outage || Salida de servicio o parada (outage) || Período en que un equipo o una unidad de generación deja de estar disponible, sea por mantenimiento programado o por falla. Es el costo dominante en casi todos los casos de negocio de este informe: cada día de parada tiene un valor de energía no vendida. || North American Electric Reliability Corporation, *Glossary of Terms Used in NERC Reliability Standards*. {{ev:A}}
nde || Ensayos no destructivos (NDE / NDT) || Conjunto de técnicas que evalúan la integridad de un material o componente sin dañarlo: ultrasonido, corrientes inducidas, radiografía, líquidos penetrantes, inspección visual remota. || American Society for Nondestructive Testing (ASNT), cuerpo normativo y de certificación de la disciplina. {{ev:A}}
trl || Nivel de madurez tecnológica (TRL) || Escala que mide cuán probada está una tecnología, desde el principio observado hasta el sistema validado en operación. **No mide despliegue comercial**: para eso este informe usa la escala M0–M5. || ISO 16290:2013, *Space systems — Definition of the Technology Readiness Levels (TRL) and their criteria of assessment*. {{ev:A}}
madurez-m || Escala de madurez comercial (M0–M5) || Escala propia de este informe que mide despliegue real en el mercado: M0 conceptos, M1 prototipos de laboratorio, M2 demostración industrial aislada, M3 servicios comerciales iniciales, M4 múltiples proveedores y despliegues, M5 mercado maduro. || Definición operativa de este informe; ver sección 3.4.
ipb || Bus isofásico (IPB) || Conducto de barras con una envolvente metálica independiente por fase, que conecta el generador con el transformador principal. Su interior es un espacio confinado con obstáculos periódicos. || EPRI, *Isolated Phase Bus Maintenance Guide*, 1015057. {{ev:A}}
hrsg || Caldera de recuperación de calor (HRSG) || Intercambiador que recupera el calor de los gases de escape de una turbina de gas para generar vapor en una central de ciclo combinado. Sus headers y tubos son el activo del candidato B. || EPRI, *Study for Snake Robot Technology for Inspection of Headers and Tubes in HRSGs*, 1017635. {{ev:A}}
header || Header o colector || Tubo de gran diámetro al que se conectan decenas de tubos menores. La unión soldada tubo-header es un punto de falla frecuente y de inspección difícil. || EPRI, 1017635. {{ev:A}}
crawler || Crawler || Vehículo de inspección que avanza por contacto dentro o sobre el activo, con ruedas, orugas o adhesión magnética. || Definición operativa de este informe, de uso corriente en inspección industrial.
tether || Cable de conexión (tether) || Cable que une el robot con la superficie y transporta energía, datos y, cuando hace falta, la fuerza para recuperarlo. Su longitud y su arrastre suelen fijar el alcance útil del sistema. || Definición operativa de este informe, de uso corriente en robótica de inspección.
fme || Exclusión de material extraño (FME) || Conjunto de controles para evitar que un objeto quede dentro de un sistema tras una intervención. Un robot atrapado en un activo nuclear puede costar más que la inspección evitada, por lo que la estrategia de recuperación es parte del producto. || Práctica normalizada de la industria nuclear; ver EPRI, *Compilation of Lessons Learned on Buried and Underground Piping*, 1025272. {{ev:B}}
emat || Transductor electromagnético-acústico (EMAT) || Sensor que genera ondas ultrasónicas en la propia pieza mediante campos electromagnéticos, sin necesidad de gel acoplante y, en ciertos casos, sin remover el revestimiento. || Hirao, M. y Ogi, H., *EMATs for Science and Industry: Noncontacting Ultrasonic Measurements*, Springer, 2003. {{ev:B}}
eca || Corrientes inducidas y arreglos (ECA) || Técnica electromagnética que detecta discontinuidades superficiales y subsuperficiales en materiales conductores; en versión de arreglo cubre más superficie por pasada. || American Society for Nondestructive Testing (ASNT). {{ev:A}}
rfet || Ensayo por campo remoto y campo lejano (RFET / BFET) || Variantes electromagnéticas usadas para inspeccionar tubos y soldaduras desde el interior, incluso a través de la pared del tubo. || TesTex, documentación técnica de producto. {{tipo:Declaración}}
ili || Inspección en línea (ILI) || Inspección de una tubería mediante un dispositivo que recorre su interior. En instalaciones nucleares suele ser inviable por la falta de estaciones de lanzamiento y recepción. || API 1163, *In-line Inspection Systems Qualification*. {{ev:A}}
penstock || Conducto forzado (penstock) || Tubería que conduce el agua desde la toma hasta la turbina en una central hidroeléctrica. Su inspección exige vaciar el conducto o entrar con vehículo sumergible. || EPRI, *ROV Technology: Applications and Advancements at Hydro Facilities*, 1007576. {{ev:A}}
rov || Vehículo remoto y vehículo autónomo (ROV / AUV) || Vehículos sumergibles: el primero opera unido por cable y comandado por un operador; el segundo navega sin cable, siguiendo un plan de misión. || EPRI, 1007576 y 3002011682. {{ev:A}}
vault || Cámara subterránea (vault) || Recinto de hormigón bajo la calzada donde se alojan empalmes de cables de transmisión. Es un espacio confinado con cables energizados y riesgo de gases. || EPRI, programa de transmisión subterránea. {{ev:A}}
canister || Canister y sobre-contenedor || En almacenamiento en seco de combustible gastado, el canister sellado contiene el combustible y el sobre-contenedor de hormigón lo blinda. Entre ambos queda el espacio anular donde debe entrar el robot. || EPRI, *Dry Canister Storage System Inspection and Robotic Delivery System Development*, 3002008234. {{ev:A}}
vine || Robot everting (vine) || Robot que avanza dando vuelta su propio cuerpo desde la punta, por presión interna, de modo que la superficie no se arrastra contra la pared. Permite recorrer conductos con curvas donde un crawler no entra. || Hawkes, E. W. et al., «A soft robot that navigates its environment through growth», *Science Robotics*, 2017. {{ev:A}}
sweep || Evaluación económica SWEEP || Método de evaluación con el que EPRI estima costo de implementación, ahorro esperado y repago de una tecnología en su catálogo de modernización de plantas. Los valores citados en este informe provienen de esas fichas; la metodología detallada debe verificarse en la fuente. || EPRI, Plant Modernization Toolbox, fichas MTA-MA-017 y MTA-MA-029. {{ev:A}}
prior-art || Estado de la técnica (prior art) || Todo conocimiento divulgado antes de la fecha de prioridad de una solicitud de patente. Una patente concedida prueba divulgación, no que el producto exista ni que se venda. || Organización Mundial de la Propiedad Intelectual (OMPI), glosario de términos de propiedad intelectual; USPTO, *Manual of Patent Examining Procedure*, capítulo 2100. {{ev:A}}
fto || Libertad de operación (FTO) || Análisis legal que determina si un producto puede comercializarse sin infringir patentes vigentes de terceros en un territorio. El presente informe **no** realiza este análisis: sólo un screening preliminar. || Organización Mundial de la Propiedad Intelectual (OMPI), material de divulgación sobre libertad de operación. {{ev:B}}
:::

