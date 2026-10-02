# Oportunidades de robots de inspección de nicho, del tipo GRIS

*Corte: 2 de octubre de 2026. Archivos que acompañan este informe: `oportunidades.csv` (27 filas, puntuadas) y `registro.md` (bitácora de búsqueda con cada URL).*

**Convención de evidencia**

| Marca | Significado |
|---|---|
| **[V]** | Verificado: leí la fuente citada y el dato está ahí. |
| **[F]** | Lo declara el fabricante o el proveedor. No hay confirmación independiente. |
| **[E]** | Estimación o inferencia mía. |
| **[SV]** | Sin verificar: lo vi en un extracto de buscador, o la fuente está detrás de un muro de pago o no se pudo leer. |

Cuando digo "no se halló" me refiero a las búsquedas registradas en `registro.md`. Que no aparezca nada publicado no prueba que no exista.

---

## 1. Lo que mostró la verificación de la lista semilla

| Semilla | Estado verificado | Fuente |
|---|---|---|
| GE MAGIC (rotor-in) | [F] Entra por huecos desde 0,25"; desde 0,50" hace también cuñas y ELCID | [GE fact sheet](https://www.gevernova.com/content/dam/gepower-new/global/en_US/downloads/gas-new-site/services/generator-services/generator-in-situ-inspection-fact-sheet.pdf) |
| ABB Air Gap Inspector | [V] **Sólo inspección visual** (5 cámaras), entrehierro ≥ 10 mm, motores y generadores; parada con rotor extraído "20 días o más" | [ABB 9AKK106713A3999](https://library.e.abb.com/public/89c60b34032a46569035a62f23f95285/9AKK106713A3999_Air%20gap%20inspection_Service%20Note_EN_RevB_lowres.pdf) |
| Mitsubishi GenSPIDER | [V/F] Mide 19,9 mm. La inspección pasa de **34 días a 6**. Los robots de ~30 mm no entran en ~30 % de los generadores MELCO | [MELCO PR 3079](https://www.mitsubishielectric.com/en/pr/pdf/2017/0125.pdf) |
| MD&A Air Gap-Bot / Nova GenEX | [F] Entrada de 0,9", visual + cuñas + ELCID. MD&A vende el GenEX de Nova como servicio | [MD&A](https://www.mdaturbines.com/services/generator/robotic-generator-in-situ-inspection/), [folleto GenEX](https://www.mdaturbines.com/wp-content/uploads/2019/06/GenEX-Robot-Inspection_FINAL.pdf) |
| Validación EPRI | [V] Informe 3002013612 (2018). Con rotor extraído la inspección cuesta hasta **USD 500 k**; con robot, hasta **75 % menos**. El **82 %** de más de 30 utilities ya lo usó | [EPRI Journal 2021](https://eprijournal.com/robotics-in-power-plants-getting-smaller-smarter/) |
| ABB/Hitachi TXplore | [V] Desarrollado dentro de un proyecto colaborativo de EPRI. Caso NYPA (2020). El método tradicional lleva 5 días de trabajo continuo; con el robot, 1. Costo de inspección **–50 %** | [T&D World](https://www.tdworld.com/test-and-measurement/article/20973023/oil-filled-power-transformers-time-for-robotic-inspection), [IWP](https://www.waterpowermagazine.com/news/mini-submersible-robot-successfully-inspects-nypa-power-transformer-7744420/) |
| Square Robot | [F] Más de 430 tanques y "USD 190 M de downtime evitado". [V] Serie B de USD 13,5 M con Marathon Petroleum. Premio NIOSH 2026 | [Square Robot](https://squarerobot.com/solutions/inspection-services) |
| Gecko Robotics | [V] Serie D de USD 125 M con valuación de USD 1,25 B (jun-2025) | [Gecko](https://www.geckorobotics.com/news/gecko-reaches-unicorn-status) |
| ULC CISBOT | [V] Con Edison: **USD 400 k frente a 1,5–1,8 M**. Obra de 18 días frente a 45–50. 50.000 juntas selladas | [Wikipedia/NYT](https://en.wikipedia.org/wiki/CISBOT), [Robotics 24/7](https://www.robotics247.com/article/ulc_technologies_cisbot_seals_50000_joints_live_gas_mains) |
| Aerones | [V] Ronda de USD 62 M (2025). Clientes: NextEra, GE, Vestas, Enel y Siemens Gamesa | [Aerones](https://aerones.com/aerones-secures-62m-in-oversubscribed-financing-round/) |
| GE / OC Robotics | [V] GE compró OC Robotics en 2017. Usa brazos serpiente on-wing y desarrolla Sensiworm | [GE Aerospace](https://www.geaerospace.com/news/press-releases/services/ge-aerospace-service-operators-meet-your-mini-robot-inspector-companions) |
| Waygate | [V] Crawler BIKE (menos de 10 kg, entra por bocas de 12"). Acuerdo de propiedad intelectual con PETRONAS (2022) | [Baker Hughes](https://www.bakerhughes.com/waygate-technologies/news/waygate-technologies-and-petronas-sign-agreement-roll-out-codeveloped) |
| Eddyfi | [V] Compró Inuktun (2019). Ofrece VersaTrax para tuberías y penstocks | [Aerospace Testing Intl.](https://www.aerospacetestinginternational.com/news/supplier-news/eddyfi-acquires-robot-crawler-company-inuktun.html) |

Nombres que se suman a la lista semilla: **Toshiba** (robots de 10 y 33 mm, comercializados en 2022), **Iris Power/Qualitrol RIV802** (se vende como equipo, entrehierro de 35 mm, hace ELCID y cuñas), **Siemens Energy AirGapCrawler**, **Constellation Clearsight** (bus isofásico), **Flyability** (drones para espacio confinado), **MIRS** y **Maquintel** (Chile) y **Kinectrics** (CANDU).

### Tres lecciones de la verificación

1. **El robot de entrehierro en turbogeneradores ya es un mercado maduro.** Hay al menos nueve fabricantes y los OEM lo venden como servicio. GRIS queda como referencia: por eso no compite en el ranking.
2. **La inspección *visual* de grandes espacios confinados ya está comoditizada por los drones con jaula.** Flyability Elios 3 inspecciona condensadores nucleares (Surry: más de USD 200 k ahorrados por parada [F]) y **ductos de ACC** [F]. Esto **debilita al candidato H** (ACC) del informe anterior. Un robot nuevo sólo se diferencia si **mide en contacto** (UT, ELCID, cuñas, torque) o si entra donde un dron no vuela: ranuras de menos de 50 mm, líquido o gas presurizado.
3. **El incumbente que más pesa en motores grandes, ABB, hace sólo inspección visual.** Lo declara su propia nota de servicio [V]. GRIS ya combina visual, ELCID y cuñas. De este hueco funcional sale la oportunidad número 1.

---

## 2. Método de puntuación

Cada criterio va de 1 a 5, y el total máximo es 25. El desempate se hace primero por *ahorro* y después por *ajuste*.

- **Ahorro:** 5 si la maniobra evitada más la parada supera USD 1 M por evento, o si el lucro cesante supera USD 1 M por día. 3 si está entre USD 100 k y 1 M. 1 si es menor.
- **Validación:** 5 si hay un informe EPRI o de una utility, más inversión o adquisición, más clientes con nombre. 1 si sólo hay I+D.
- **Hueco en Latinoamérica:** 5 si no se encontró ningún proveedor regional. 1 si hay un incumbente local fuerte.
- **Ajuste:** qué tanto encaja con crawlers compactos, señales débiles, mecánica de precisión, firmware y el canal de generadores y turbinas de vapor.
- **Factibilidad:** 5 si un equipo de 3 a 6 personas lo resuelve con la plataforma de GRIS. 1 si exige calificación nuclear, ATEX u OEM.

Los puntajes son **juicio propio [E]** apoyado en los datos de cada fila del CSV.

---

## 3. Ranking de las 10 mejores oportunidades

| # | Oportunidad | Ahorro | Valid. | Hueco LatAm | Ajuste | Factib. | **Total** |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| ref | Turbogenerador rotor-in (GRIS) | 5 | 5 | 2 | 5 | 5 | 22 |
| 1 | **Motores sincrónicos grandes y GMD de molinos: visual + ELCID + cuñas con el rotor adentro** | 5 | 4 | 4 | 4 | 4 | **21** |
| 2 | **Crawler para bus isofásico (IPB)** | 3 | 5 | 4 | 5 | 4 | **21** |
| 3 | **Hidrogeneradores rotor-in sin retirar polos** | 3 | 3 | 4 | 5 | 4 | **19** |
| 4 | Reactores PHWR/CANDU: inspección y reparación remota | 5 | 4 | 3 | 4 | 2 | 18 |
| 5 | Headers y tubos de HRSG desde adentro | 4 | 4 | 3 | 4 | 3 | 18 |
| 6 | Penstocks y túneles: espesor UT sin vaciar | 4 | 4 | 3 | 4 | 3 | 18 |
| 7 | Transformadores: inspección interna sumergida | 3 | 5 | 4 | 3 | 3 | 18 |
| 8 | END in situ del rotor (anillos de retención, cuñas de rotor) | 4 | 3 | 3 | 4 | 3 | 17 |
| 9 | Reparación in situ de cavitación en rodetes (tipo SCOMPI) | 4 | 4 | 4 | 3 | 2 | 17 |
| 10 | Tuberías enterradas y no pigables | 4 | 5 | 2 | 3 | 2 | 16 |

### Justificación breve

1. **Motores grandes y GMD.**
   - **Ahorro:** Un molino GMD de 60.000 t/d pierde **USD 4 a más de 7 M por día** [V, ABB + Zurich]. En Antapaccay (Perú) cada hora de parada cuesta "mucho más de USD 100.000" [V, Siemens]. Extraer el rotor de un motor grande lleva "20 días o más" [V, ABB].
   - **Mercado:** Chile y Perú tienen la mayor base instalada de GMD del mundo [V, ABB]. Hay fallas documentadas: Collahuasi, Cadia y un desplazamiento de estator [V, E&A]. ABB escribió que "con inspecciones regulares, el impacto de algunas fallas podría haberse reducido" [V].
   - **Competencia:** ABB ofrece en Chile su robot, pero **sólo hace inspección visual** [V].
   - **Riesgos:** El entrehierro de un GMD puede bajar a 8 mm [V, Antapaccay], así que hay que verificar la factibilidad. Además, el canal comercial es minero y no de generación.
2. **Bus isofásico.**
   - **Validación:** Es la ficha EPRI más concreta: el proveedor cobra unos **USD 100.000** por implementación, la inspección dura menos de un día, el payback es inmediato y la reducción llegó a 10× en un caso [V]. Lo compra el mismo cliente, en la misma parada y con el mismo tipo de robot.
   - **Límite:** Se inspecciona **cada 10 años** [V]. Por eso funciona como servicio que acompaña a GRIS, no como producto aislado.
3. **Hidrogeneradores.**
   - **Mercado:** Ajuste perfecto y la mayor flota de la región: 110 GW en Brasil, 13,2 GW en Colombia, 8,8 GW en Paraguay y 7,6 GW en Chile [SV, IHA, según extracto de buscador].
   - **Competencia:** Iris RIV802 y ABB AGI cubren entrehierros grandes [F]. No se hallaron despliegues regionales.
   - **Pendiente:** Hay que probar que hoy se retiran polos o rotor para inspeccionar [SV] y cuantificarlo.
4. **CANDU/PHWR.** El ahorro es enorme: Atucha II se reparó de forma remota en **10 meses en lugar de ~4 años** [V, prensa y gobierno]. Pero son proyectos, no un producto que se repite, y exigen calificación nuclear. Sirve como cliente ancla de I+D en Argentina.
5. **HRSG.** EPRI documenta tubos que no se pueden inspeccionar sin acceso destructivo [V]. TesTex es el incumbente [F]. El cliente es de ciclo combinado, el mismo canal.
6. **Penstocks.** El USBR declara un túnel demasiado peligroso para buzos y que no tiene programa propio de vehículos remotos [V]. Los vehículos ya existen comercialmente: el valor está en medir espesor en contacto y en el servicio.
7. **Transformadores.** Validación fuerte (EPRI, NYPA), un único incumbente OEM y ningún despliegue regional publicado. La física es distinta: un vehículo en aceite dieléctrico, con propiedad intelectual de ABB/Hitachi.
8. **END del rotor in situ.** Es una extensión natural de GRIS, con UT en anillos y cuñas. Ya hay oferta (DEKRA, 3Angles, patentes Siemens).
9. **SCOMPI.** Hydro-Québec lo usó en 40 trabajos mayores y buscó socios de licencia [V]. Conviene más **licenciar o representar** que desarrollar.
10. **Tuberías enterradas.** Ahorro de USD 1 a 5 M por uso [V, EPRI], pero el mercado ya está maduro (Diakont, Pipetel, ROSEN).

Quedaron fuera del top 10 aunque están validadas: tanques API 653, CISBOT, calderas, eólica y motores aeronáuticos. Las cubren startups bien financiadas u OEM, o quedan fuera del canal (detalle en el CSV).

---

## 4. Los huecos más claros: problema validado con poca presencia en Latinoamérica

| Hueco | Problema validado por | Presencia en LatAm hallada | Lectura |
|---|---|---|---|
| **ELCID + cuñas con rotor adentro en motores sincrónicos grandes y GMD** | ABB + Zurich (lucro cesante), Siemens (USD/h), fallas documentadas, ABB (20 días con rotor afuera) | ABB, **sólo visual**, en Chile | Es el hueco más claro. El dolor está en USD/día y la región es el centro mundial del activo. |
| **Bus isofásico con crawler** | EPRI MTA-MA-029 | Ninguna | Hueco claro pero chico. Encaja como paquete "GRIS + IPB" en la misma parada. |
| **Hidrogeneradores rotor-in** | EPRI P220 (HGHAT), IREQ | Ninguna publicada | Hay que medir el dolor antes de construir. |
| **Transformadores sin vaciar aceite** | EPRI, NYPA, ABB | Ninguna publicada (Hitachi podría llegar) | Validado, pero el incumbente es un OEM con propiedad intelectual. |
| **Tanques en servicio** | Square Robot (inversión, NIOSH) | Sin clientes regionales publicados | Hay hueco, pero fuera del canal. Conviene representación. |
| **GIS por dentro** | Sólo la patente US 8717742 e I+D china | Ninguna | Todavía no está validado. |

---

## 5. Las 3 que conviene investigar primero

### 5.1 Motores sincrónicos grandes y GMD: visual + ELCID + cuñas sin extraer el rotor

**Por qué primero.** Combina el ahorro más grande de todo el estudio (USD/día de un concentrador de cobre) con un hueco funcional que declara el propio incumbente (visual solamente). Está en el país vecino con la mayor base del mundo y usa la misma física y la misma electrónica de señales débiles que GRIS.

**Riesgos que hay que cerrar antes de invertir:**

- El entrehierro de un GMD puede ser de 8 mm [V, Antapaccay], por debajo de GRIS. Hay que ver si se entra por otro lado (tapas de estator) o si hace falta un crawler ultradelgado (Toshiba tiene uno de 10 mm [F]).
- ELCID en máquinas de polos salientes con estator segmentado (cuartos): hay que confirmar aplicabilidad y protocolo [E].
- ABB y Siemens tienen contratos de servicio de largo plazo con su base instalada (ABB–Codelco [SV]), así que hay que ver si un tercero puede entrar.

**Preguntas para mantenimiento eléctrico de una minera (Codelco, Escondida, Collahuasi, Antamina, Cerro Verde, Las Bambas):**

1. ¿Cada cuánto inspeccionan internamente el GMD y los motores sincrónicos de más de 5 MW? ¿Con qué método (desplazar estator, retirar tapas, boroscopio, robot ABB)?
2. ¿Cuántas horas de molino detenido lleva hoy esa inspección y en qué ventana se hace (relining)?
3. ¿Alguna vez midieron ELCID o estado de cuñas en el GMD? Si no lo hicieron, ¿por qué: acceso, tiempo o no lo ofrece nadie?
4. ¿Qué falla les preocupa más: aislación de bobinado, cuñas flojas, laminación o polos? ¿Tuvieron eventos?
5. ¿El contrato con el OEM les impide contratar a un tercero para inspecciones? ¿Lo exige la aseguradora?
6. ¿Cuánto pagarían por una inspección que entre en la parada de relining sin agregar horas? ¿Quién firma la orden de compra?

### 5.2 Bus isofásico (como paquete con GRIS)

**Por qué.** Es la oportunidad con la validación más fuerte, por EPRI, el costo y el payback. Lo compra **el mismo cliente**, en **la misma parada** y con **el mismo canal** que ya tiene tu empresa en generadores. Además, el desarrollo es incremental: es un crawler más grande, en un ambiente más simple que el entrehierro.

**Riesgos:** la frecuencia es decenal, y si el crawler queda atascado se convierte en material extraño.

**Preguntas para jefes de mantenimiento eléctrico de centrales (los clientes actuales de GRIS):**

1. ¿Cuándo inspeccionaron el bus isofásico por última vez? ¿Con andamio? ¿Cuántos días y cuánto costó el andamio?
2. ¿Tuvieron sobrecalentamientos, arcos, entrada de agua o material extraño en el IPB?
3. Si la inspección del IPB se hace en la misma movilización que la del generador, ¿la contratarían? ¿Con qué frecuencia?
4. ¿Qué medición sumaría valor además de la visual: termografía, resistencia de juntas, limpieza?
5. ¿Qué tramos tienen hoy inaccesibles (verticales, cruces de muros)?

### 5.3 Hidrogeneradores rotor-in

**Por qué.** Tiene el ajuste técnico más alto, es la flota más grande de Sudamérica (Brasil, Paraguay, Argentina y Colombia) y no se encontraron despliegues regionales. Pero el **dolor no está cuantificado**: es la oportunidad que más necesita validación con clientes.

**Preguntas para mantenimiento de hidroeléctricas (Yacyretá, Salto Grande, El Chocón/AES, Itaipú, Eletrobras, ISA/EPM):**

1. Para inspeccionar el estator y las cuñas, ¿retiran polos o rotor? ¿Cada cuánto, cuánto dura y cuánto cuesta (horas de grúa y personal)?
2. ¿Hacen ELCID o pruebas de cuñas hoy? ¿Con qué acceso?
3. ¿Cuál es el costo de un día de unidad parada según la temporada hidrológica?
4. ¿Qué entrehierro tienen sus unidades y qué obstrucciones hay (ventilación, deflectores)?
5. ¿Contratarían el servicio al OEM (Andritz, Voith, GE) o a un tercero? ¿Hay restricciones de garantía?

**Siguiente candidato si una de las tres cae:** transformadores (sección 3, #7), con la pregunta clave de si Hitachi presta TXplore en la región y a qué precio.

---

## 6. Hechos verificados y lo que es inferencia

- **Hechos verificados [V]:** todas las cifras con fuente de las secciones 1, 3 y 4 que llevan la marca [V].
- **Inferencias [E]:**
  - los puntajes;
  - el valor de "≈ USD 440 k por tanque", que dividí yo a partir de cifras de Square Robot;
  - la aplicabilidad del ELCID en GMD;
  - la ausencia de competidores en Latinoamérica, que sólo significa que no encontré nada publicado.
- **Sin verificar [SV]:** la hoja de FM Global (acceso restringido), el retiro de polos en hidrogeneradores (no se pudo extraer el PDF) y los "4 años" de Atucha II (dato de gobierno y prensa, sin confirmación independiente).

---

## 7. Fuentes consultadas

**EPRI**
- EPRI Journal, *Robotics in Power Plants: Getting Smaller, Smarter* (10-mar-2021). https://eprijournal.com/robotics-in-power-plants-getting-smaller-smarter/
- EPRI 3002013612, *Generator Robotic Inspection and Test Guidelines: A State-of-the-Art Update* (2018, muro de pago, título y código citados).
- EPRI (Moore), *Generator Research*, IRMC 2022. https://irispower.com/wp-content/uploads/2023/07/EPRI-Generator-Research-Recent-In-Progress-and-Future-Planned-Moore-IRMC-2022.pdf
- EPRI MTA-MA-029 (IPB). https://nuclearplantmod.epri.com/MTA-MA-029
- EPRI MTA-MA-017 (tubería enterrada). https://nuclearplantmod.epri.com/MTA-MA-017
- EPRI 3002023899, *Robotic Process Automation for Nuclear Power Plants*. https://restservice.epri.com/publicdownload/000000003002023899/0/Product
- EPRI 1017635, *Snake Robot for HRSG*. https://restservice.epri.com/publicdownload/000000000001017635/0/Product
- EPRI TR-113584-V7, *ROV Technology at Hydro*. https://restservice.epri.com/publicdownload/000000000001007576/0/Product
- EPRI 1011489, *HPFF Pipe Type Cable best practices*. https://restservice.epri.com/publicdownload/000000000001011489/0/Product
- EPRI 3002031100, proyecto suplementario de cables pipe-type extruidos. https://restservice.epri.com/publicdownload/000000003002031100/0/Product
- EPRI Transmisión subterránea. https://transmission.epri.com/p36_underground/public/p36_applications/
- EPRI Journal, contenedores secos. https://eprijournal.com/wall-climbing-robots-inspect-nuclear-storage-casks/

**Fabricantes y OEM**
- GE Vernova, generator in-situ. https://www.gevernova.com/content/dam/gepower-new/global/en_US/downloads/gas-new-site/services/generator-services/generator-in-situ-inspection-fact-sheet.pdf
- GE Vernova, Rotor-In Major Inspection. https://www.gevernova.com/gas-power/services/gas-turbines/upgrades/rotor-major-inspection
- Mitsubishi Electric, PR 3079 (2017). https://www.mitsubishielectric.com/en/pr/pdf/2017/0125.pdf
- Mitsubishi Electric, folleto GenSPIDER. https://www.mitsubishielectric.com/eig/energysystems/downloads/pdf/GenSPIDER_pamphlet.pdf
- Toshiba (2022). https://www.global.toshiba/ww/news/energy/2022/10/news-20221012-01.html
- ABB, Air Gap Inspection Service Note. https://library.e.abb.com/public/89c60b34032a46569035a62f23f95285/9AKK106713A3999_Air%20gap%20inspection_Service%20Note_EN_RevB_lowres.pdf
- ABB, página de Air Gap Inspection. https://www.abb.com/global/en/areas/motion/services/asset-health-and-monitoring/air-gap-inspection
- ABB + Zurich, *Insurability of Large Gearless Mill Drives*. https://library.e.abb.com/public/bbe88e6615f95e49c1257b20003b5c3b/INSURABILITY%20OF%20LARGE%20GEARLESS%20MILL%20DRIVES.pdf
- ABB, *Mills and GMDs*. https://library.e.abb.com/public/9c87aa6aa2d41043c12577dc0056b6ae/Mills%20and%20GMDs.pdf
- ABB, *Remote Diagnostic Services for GMDs*. https://library.e.abb.com/public/3b41eb5173848571c125793d00572de5/REMOTE%20DIAGNOSTIC%20SERVICES%20FOR%20GEARLESS%20MILL%20DRIVES.pdf
- Siemens, *Increasing availability through advanced Gearless Drive Technology*. https://assets.new.siemens.com/siemens/assets/api/uuid:43bdd1aa8285cab50dcc8127a6e141b14e6dcc51/availability-and-reliability-gearless-drives.pdf
- MD&A, inspección robótica de generador. https://www.mdaturbines.com/services/generator/robotic-generator-in-situ-inspection/
- MD&A, sitio en español. https://www.mdaturbines.com/es/servicios/servicios-de-generador/inspeccion-robotica-de-generador-en-sitio/
- Folleto GenEX. https://www.mdaturbines.com/wp-content/uploads/2019/06/GenEX-Robot-Inspection_FINAL.pdf
- Nova Technology. https://www.novatechnologyinc.com/turbo-generators
- Iris Power RIV802. https://irispower.com/products/robotic-inspection-camera/
- Hitachi Energy TXplore. https://www.hitachienergy.com/products-and-solutions/transformers/transformer-service/assess-and-secure/txplore-transformer-inspection-robot
- ABB/Simcoa. https://new.abb.com/news/detail/51406/how-are-abbs-swimming-robots-saving-time-and-money-for-simcoa-operations
- Waygate/PETRONAS. https://www.bakerhughes.com/waygate-technologies/news/waygate-technologies-and-petronas-sign-agreement-roll-out-codeveloped
- Eddyfi VersaTrax. https://www.eddyfi.com/en/product/versatrax-inspection-crawlers
- Kinectrics, folleto IMS. https://www.kinectrics.com/files/brochures/IMSBrochure_NI020321.pdf
- Kinectrics, inspección de feeders. https://www.kinectrics.com/capabilities/services/nuclear-services-site-outage-support/feeder-inspection
- TesTex IAT. https://testex-ndt.com/products/iat-internal-access-tool-for-hrsg-inspections/
- DEKRA. https://www.dekra.in/en/ultrasonic-testing-for-in-situ-generator-inspection/
- 3Angles. https://3anglesndt.com/generator-retaining-rings/
- Constellation Clearsight. https://constellationclearsight.com/case-studies/emergent-isophase-bus-duct-inspection/

**Startups, inversiones y adquisiciones**
- Square Robot. https://squarerobot.com/solutions/inspection-services
- Square Robot, Serie B (WBJ). https://wbjournal.com/article/westborough-robotics-firm-raises-7-5m-capping-off-2025-expansion-efforts/
- Square Robot, USD 5 M (The Robot Report). https://www.therobotreport.com/square-robots-brings-in-5m-for-tank-inspection-robots/
- Square Robot SR-3 en prensa brasileña. https://clickpetroleoegas.com.br/robo-entra-em-tanque-industrial-cheio-examina-o-fundo-sem-retirar-o-produto-e-mantem-trabalhadores-do-lado-de-fora-durante-a-inspecao-fcmo87
- Gecko Robotics, unicornio. https://www.geckorobotics.com/news/gecko-reaches-unicorn-status
- Gecko Robotics, SiliconANGLE. https://siliconangle.com/2025/06/12/gecko-robotics-raises-125m-inspect-monitor-critical-infrastructure/
- Aerones. https://aerones.com/aerones-secures-62m-in-oversubscribed-financing-round/
- CISBOT (Wikipedia). https://en.wikipedia.org/wiki/CISBOT
- CISBOT (Robotics 24/7). https://www.robotics247.com/article/ulc_technologies_cisbot_seals_50000_joints_live_gas_mains
- ULC Air Gap Inspector. https://ulctechnologies.com/technologies/air-gap-inspector/
- Eddyfi compra Inuktun. https://www.aerospacetestinginternational.com/news/supplier-news/eddyfi-acquires-robot-crawler-company-inuktun.html
- Rolls-Royce. https://www.aerospacetestinginternational.com/news/technology/rolls-royce-demonstrates-robotic-engine-inspection-and-repair-tools.html
- GE Sensiworm. https://www.geaerospace.com/news/press-releases/services/ge-aerospace-service-operators-meet-your-mini-robot-inspector-companions
- Pipetel/Intero. https://www.intero-integrity.com/services/unpiggable-mfl-robotic-inline-inspection
- NETL Explorer. https://www.netl.doe.gov/node/3037
- Diakont. https://diakont.com/case-studies/nuclear-solutions/first-buried-piping-in-line-inspection/
- Flyability, ACC. https://www.flyability.com/casestudies/air-cooled-condenser-drone-inspection-with-the-elios-3
- Flyability, condensadores. https://www.flyability.com/casestudies/condenser-inspection
- Flyability, Exelon/Clearsight. https://www.flyability.com/news/exelon-clearsight-renewal

**Utilities, gobierno y organismos**
- USBR, proyecto 9612. https://www.usbr.gov/research/projects/detail.cfm?id=9612
- USBR, S&T 22064. https://data.usbr.gov/catalog/7976
- Hydro-Québec, SCOMPI. https://www.renewableenergyworld.com/hydro-power/technology-equipment/hydro-quebec-seeks-partners-to-use-scompi-robot-in-hydro-turbin/
- Hydro-Québec, ficha SCOMPI. http://www.hydroquebec.com/innovation/en/pdf/2010G080-18A%20SCOMPI.pdf
- Hydro-Québec, LineRanger. https://news.hydroquebec.com/news/press-releases/all-quebec/lineranger-robot-innovative-live-line-inspection-solution.html
- IREQ, verificación de acuñado. https://www.osti.gov/etdeweb/biblio/515797
- OPG, SAFIRE. https://www.osti.gov/etdeweb/biblio/22254410
- SCOMPI en CANDU. https://www.osti.gov/etdeweb/biblio/20521468
- Gobierno argentino, Atucha II. https://www.argentina.gob.ar/noticias/atucha-ii-autoridades-de-energia-supervisaron-los-trabajos-de-reparacion
- Rosario3, Atucha II. https://www.rosario3.com/informaciongeneral/La-central-nuclear-Atucha-II-volvio-a-funcionar-tras-10-meses-en-los-que-permanecio-sin-generar-energia-20230829-0064.html
- EconoJournal, Atucha II. https://econojournal.com.ar/2023/01/la-central-nuclear-atucha-ii-continuara-fuera-de-servicio-hasta-que-se-defina-como-reparar-el-reactor/
- NA-SA, parada de Embalse. https://www.na-sa.com.ar/es/prensa/la-central-nuclear-embalse-vuelve-a-aportar-energia-tras-finalizar-su-parada-programada-396
- Petrobras, Tupã Ex. https://petronoticias.com.br/petrobras-desenvolveu-robo-autonomo-de-inspecao-com-primeiros-testes-agendados-para-o-fim-do-ano/
- Petrobras, drones en FPSO. https://droneshowla.com/drone-e-usado-para-inspecao-de-tanques-em-um-fpso-da-petrobras/
- IHA, Sudamérica. https://www.hydropower.org/region-profiles/south-america
- FM Global, *Motors and Adjustable Speed Drives*, ene-2024 (acceso restringido). https://www.fm.com/FMAApi/data/ApprovalStandardsDownload?itemId=%7BA23ED704-D145-41A8-A17B-0E5FEEF38627%7D

**Prensa técnica y paper**
- T&D World, TXplore. https://www.tdworld.com/test-and-measurement/article/20973023/oil-filled-power-transformers-time-for-robotic-inspection
- International Water Power, NYPA. https://www.waterpowermagazine.com/news/mini-submersible-robot-successfully-inspects-nypa-power-transformer-7744420/
- International Water Power, operaciones subacuáticas. https://www.waterpowermagazine.com/analysis/underwater-operations/
- Revista Tecnología Minera (ABB Chile). https://tecnologiaminera.com/actualidad/la-importancia-de-una-inspeccion-visual-sin-remover-el-rotor-de-motores-y-generadores-1593573982
- E&A, fallas de GMD. https://www.eand.com.au/2014/09/10/literature-review-gealess-motor-failures-a-mill-designers-viewpoint/
- Portal Innova (ABB GMD). https://portalinnova.cl/experto-de-abb-da-a-conocer-plataforma-basada-en-machine-learning-para-mantenimiento-predictivo-de-gearless-mill-drives-gmd/
- International Mining, MIRS. https://im-mining.com/2019/09/05/chiles-mirs-launches-world-first-emmr-robotic-mill-lining-innovation/
- Mining.com, MIRS. https://www.mining.com/robots-could-now-be-in-charge-of-mill-reline-process/
- Mining Magazine, relining. https://www.miningmagazine.com/technology/news/1263771/rethinking-value-relining
- Maquintel. https://www.maquintel.com/
- EECSS 2024, reparación de estator hidro. https://avestia.com/EECSS2024_Proceedings/files/paper/EEE/EEE_104.pdf
- Wiley, robot para transformador. https://onlinelibrary.wiley.com/doi/10.1155/2023/6699265
- PMC, robot para transformador. https://pmc.ncbi.nlm.nih.gov/articles/PMC11314836/
- Wiley, robot GIS. https://onlinelibrary.wiley.com/doi/10.1155/2021/6691905
- Emerald, robot de descargas parciales en GIS. https://www.emerald.com/ir/article-abstract/51/6/908/1227344/An-automatic-robot-for-ultrasonic-partial
- MATEC 2024, ECT de condensador. https://www.matec-conferences.org/articles/matecconf/pdf/2024/11/matecconf_aeege2024_00008.pdf

**Patentes**
- US 10712391 (ABB, crawler para máquinas que incluye GMD). https://patents.google.com/patent/US10712391B2/en
- US 12015839 (Siemens Energy, vehículo de inspección). https://patents.google.com/patent/US12015839B2/en
- US 20140345384 (robot para anillos de retención). https://patents.google.com/patent/US20140345384
- US 5650579 (crawler de entrehierro). https://patents.google.com/patent/US5650579A/en
- Otras citadas por número, sin enlace: US 7201055, 7555966, 7681452, 10434641, 10427290, 10596713, 10603802, 10197538 y 8717742 (GIS).

**Informe previo del repositorio**
- `../source/informe.md` y `../source/registro-investigacion.md`: candidatos A–H, ACCUG, USBR, horas-hombre de EPRI.
