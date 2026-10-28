// 00503-00-EPG002 — Anexo: Protocolos de ensayo EL CID (excitación, calibración, software ELCSoft).
const fs = require("fs");
const path = require("path");
const { Paragraph, AlignmentType, TextRun, ImageRun } = require("docx");
const F = require("./formato_mecanalisis");
const { p, vineta, numerada, h1, h2, h3, rol, nota, espacio, tabla, figura } = F;

const PROC = "00503-00-EPG001";
// Apartados del procedimiento general que invocan cada protocolo (se calculan desde EPG001).
const { etapas } = require("./epg001_procedimiento");
const invocado = (nro) => etapas
  .filter((e) => e.pasos.some((ps) => !ps.seccion && ps[2].includes(`Protocolo ${nro}`)))
  .map((e) => e.apartado).join(", ");

// ---------- ecuaciones ----------
// Imágenes generadas por ecuaciones.py (mathtext, 600 dpi), centradas y con su número a la derecha.
const EC = JSON.parse(fs.readFileSync(path.join(__dirname, "img", "ec", "medidas.json"), "utf8"));
// Numeración en el orden en que aparecen en el apéndice (permite citarlas antes de insertarlas).
const ORDEN_EC = ["faraday", "fem", "vt", "q", "k", "tph", "practica", "yugo", "rotor", "vvar", "fmm", "q_reac", "pfe", "s", "n"];
const numEc = Object.fromEntries(ORDEN_EC.map((id, i) => [id, i + 1]));
const ec = (id) => {
  const [w, h] = EC.ecuaciones[id];
  const k = 96 / EC.dpi;
  const nroEc = numEc[id];
  return new Paragraph({
    alignment: AlignmentType.LEFT, spacing: { before: 100, after: 140 }, keepLines: true,
    tabStops: [{ type: "center", position: F.ANCHO / 2 }, { type: "right", position: F.ANCHO }],
    children: [
      new TextRun({ text: "\t" }),
      new ImageRun({ type: "png", data: fs.readFileSync(path.join(__dirname, "img", "ec", `${id}.png`)),
        transformation: { width: Math.round(w * k), height: Math.round(h * k) }, altText: { title: id, description: `Ecuación ${nroEc}`, name: id } }),
      new TextRun({ text: `\t(${nroEc})`, color: F.C.gris }),
    ],
  });
};
const e = (id) => `(${numEc[id]})`;

const meta = {
  codigo: "00503-00-EPG002",
  version: "00",
  fecha: "28/10/2026",
  tipo: "PROCEDIMIENTO – ANEXO",
  tituloEncabezado: ["PROTOCOLOS DE ENSAYO EL CID", "EXCITACIÓN, CALIBRACIÓN Y SOFTWARE"],
  tituloPortada: ["PROTOCOLOS DE ENSAYO EL CID", "Excitación del núcleo, calibración y operación de ELCSoft"],
  objetivo: `Establecer los protocolos técnicos para la excitación del núcleo, la calibración del sistema de medición y la operación del software ELCSoft en el ensayo EL CID, como anexo del procedimiento ${PROC}.`,
  alcance: "Ensayo EL CID para determinar la condición de la aislación interlaminar de núcleos estatóricos de generadores eléctricos, con el rotor colocado (inspección robotizada GRIS) o con el rotor desmontado.",
  listasNumeradas: ["calib", "secuencia"],
  registros: [["RME-ELC-01", "Registro de cálculo de excitación – Ensayo EL CID"]],
  revisiones: [["00", "28/10/2026", "Versión inicial. Adaptación al formato Mecanálisis de los «Protocolos de ensayo ELCID robotizado» (Nexergy Corp., junio 2025)."]],
  firmas: ["", "", "", ""],
  referencias: ["[1] Ridley G. K., «EL CID – Application and Analysis», 2000."],
};

const cuerpo = [
  h1("1. DEFINICIONES"),
  tabla(["Término", "Significado"], [1700, 7938], [
    ["**EL CID**", "Electromagnetic Core Imperfection Detection. Ensayo de la aislación interlaminar del núcleo estatórico mediante magnetización débil (≈ 4 % del flujo nominal)."],
    ["**Iq**", "Componente en cuadratura de la corriente de falla, medida por el captor [mA]."],
    ["**Captor**", "Sensor magnético (bobina Chattock) de dos bobinas captoras que mide la corriente de falla."],
    ["**Espira auxiliar**", "Conductor fijo en una ranura que permite medir la tensión por espira y generar la corriente de falla de calibración."],
    ["**KF**", "Constante de calibración del captor (constante de sensor Iq) en el software."],
    ["**Variac**", "Fuente de CA de tensión variable que alimenta el arrollamiento de excitación."],
    ["**ELCSoft**", "Software de adquisición y visualización del ensayo EL CID (versión 1.0)."],
    ["**DAQ**", "Unidad de adquisición de datos."],
  ]),

  h1("2. CONTENIDO"),
  p(`Este anexo contiene los tres protocolos que se invocan desde ${PROC}:`),
  tabla(["Protocolo", "Contenido", "Invocado en " + PROC], [2600, 4238, 2800], [
    ["Protocolo 1 – Excitación del núcleo", "Equipo, puesta a tierra, cálculo y montaje del arrollamiento de excitación y espira auxiliar.", `Apartados ${invocado(1)}`],
    ["Protocolo 2 – Calibración", "Tensión por espira, corriente de falla controlada y constante KF.", `Apartados ${invocado(2)}`],
    ["Protocolo 3 – Software ELCSoft", "Parámetros, registro de ranuras, visualización y archivos.", `Apartados ${invocado(3)}`],
  ]),

  // ---------------- PROTOCOLO 1 ----------------
  h2("2.1 PROTOCOLO 1 – EXCITACIÓN DEL NÚCLEO"),
  p("Guía para la magnetización débil del núcleo estatórico a ensayar."),
  h3("2.1.1 Características técnicas del equipo"),
  tabla(["Característica", "Valor"], [4200, 5438], [
    ["Alimentación eléctrica", "CA 110/220 V, 50/60 Hz"],
    ["Corriente máxima de excitación", "Hasta 50 A"],
    ["Entrada de posición axial", "Analógica 0 – 10 V"],
    ["Entrada de captor", "Analógica, conector dedicado"],
    ["Puesta a tierra", "Borne «Ground»"],
    ["DAQ – interfaz de comunicación", "USB 2.0"],
    ["DAQ – temperatura de operación / almacenamiento", "0 °C a 50 °C / –20 °C a 70 °C"],
    ["DAQ – humedad relativa", "10 % a 90 % sin condensación"],
    ["DAQ – altitud máxima de operación", "2000 m s. n. m."],
  ]),
  h3("2.1.2 Puesta a tierra"),
  nota("Precaución:", "la puesta a tierra se realiza en forma local desde el estator de la máquina y se distribuye radialmente hacia cada equipo del ensayo. El borne «Ground» del tablero EL CID es su única vinculación a tierra: no se admite ninguna otra conexión paralela o secundaria. Esta disposición evita lazos de corriente que inducen señales espurias y ponen en riesgo los equipos conectados."),
  h3("2.1.3 Cálculo del número de espiras"),
  p("El número de espiras N se determina a partir de la tensión por espira calculada según el apartado 2.4 (Apéndice) y se registra en RME-ELC-01, considerando que:"),
  vineta("La tensión aplicada no supere la capacidad nominal del Variac."),
  vineta("La corriente de excitación resultante quede dentro del rango operativo recomendado: **5 A a 40 A**."),
  h3("2.1.4 Selección de la sección del conductor"),
  p("La sección del conductor debe admitir la corriente de ensayo sin sobrecalentamiento. Un conductor sobrecalentado aumenta su resistencia, reduce la corriente de excitación y obliga a recalibrar y a corregir permanentemente la tensión aplicada para mantener constante la tensión por espira."),
  h3("2.1.5 Montaje con rotor desmontado"),
  vineta("Fijar el arrollamiento en forma concéntrica respecto del eje del núcleo, cubriendo toda su longitud axial."),
  vineta("En los extremos del núcleo, utilizar un radio de curvatura amplio para evitar efectos de borde."),
  vineta("Agrupar en forma compacta el tramo del arrollamiento dispuesto a lo largo del eje."),
  h3("2.1.6 Montaje con rotor colocado"),
  vineta("Aislar eléctricamente el rotor de su apoyo, al menos en uno de sus extremos, para que no forme una espira de falla con el núcleo y el arrollamiento de excitación."),
  vineta("Ubicar el arrollamiento lateralmente al núcleo, en la medida de lo posible."),
  vineta("Desplazar el arrollamiento a medida que avanza el ensayo, para evitar que el captor quede próximo al conductor de excitación (el acoplamiento directo produce lecturas erróneas)."),
  nota("Inspección GRIS:", `la ubicación inicial y la reubicación del arrollamiento cada 120° se realizan según ${PROC}, apartados ${etapas.find((e) => e.id === "exc").apartado} (montaje de la excitación) y ${etapas.find((e) => e.id === "ran").apartado} (inspección por ranura).`, F.C.gris),
  h3("2.1.7 Montaje de la espira auxiliar"),
  p("La espira auxiliar permite medir la tensión por espira durante todo el ensayo y generar la corriente de falla controlada de calibración (Protocolo 2). Se aloja dentro de una ranura del estator, en una posición fija y representativa."),
  p("Dado que la corriente de calibración es baja (100 mA a 200 mA) y que la espira no conduce corriente en forma permanente, se recomienda un conductor de **1,5 mm²**."),
  nota("Precaución:", "verificar que la espira auxiliar no quede en cortocircuito en ningún momento del ensayo. Un cortocircuito provocaría una corriente elevada y no controlada, con riesgo para el equipo, el sensor y la validez del ensayo."),

  // ---------------- PROTOCOLO 2 ----------------
  h2("2.2 PROTOCOLO 2 – CALIBRACIÓN"),
  p("Establece la correspondencia entre la señal medida por el captor y una corriente de falla conocida, a partir de la configuración de referencia de la Figura 1. La puesta a tierra se realiza según 2.1.2."),
  ...figura("fig_calibracion.png", 1292, 537, "Figura 1: Configuración de referencia para la calibración del ensayo EL CID"),
  numerada("**Preparación.** Verificar que el arrollamiento de excitación (número de espiras calculado) y la espira auxiliar estén montados según el Protocolo 1.", "calib"),
  numerada("**Ausencia de espiras parásitas.** Antes de energizar, retirar o reubicar todo elemento conductor que forme un lazo cerrado alrededor del núcleo: cintas pasacables metálicas, alambres o cables sueltos, herramientas, fijaciones o elementos estructurales transversales al flujo. Estos lazos inducen corrientes espurias que simulan fallas inexistentes.", "calib"),
  numerada("**Tensión por espira.** Alimentar el arrollamiento con el Variac y ajustar la tensión hasta que la tensión medida en la espira auxiliar sea igual al valor teórico calculado (apartado 2.4).", "calib"),
  numerada("**Corriente de falla.** Con la espira auxiliar firmemente alojada en su ranura, conectar en serie una resistencia de calibración de valor tal que circule una corriente de **100 mA a 200 mA**.", "calib"),
  numerada("**Posicionamiento del captor.** Alinear el eje central entre las dos bobinas captoras con el centro de la ranura de la espira auxiliar, a una distancia del borde del núcleo de aproximadamente **¼ de la longitud total del núcleo**, para minimizar los efectos de borde.", "calib"),
  numerada("**Constante KF.** En ELCSoft, ajustar KF hasta que la lectura coincida con la corriente de falla establecida.", "calib"),
  numerada("**Finalización.** Abrir el circuito de la espira auxiliar y confirmar que la tensión en ella sea igual a la tensión por espira calculada. Registrar los valores en el registro de calibración.", "calib"),
  espacio(60),
  nota("Durante el ensayo:", "monitorear continuamente la tensión por espira y corregirla cuando sea necesario para mantenerla constante.", F.C.gris),

  // ---------------- PROTOCOLO 3 ----------------
  h2("2.3 PROTOCOLO 3 – OPERACIÓN DEL SOFTWARE ELCSOFT"),
  p("ELCSoft 1.0 es el software de adquisición del ensayo EL CID. Permite iniciar ensayos, continuar ensayos incompletos y visualizar los resultados en forma gráfica."),
  h3("2.3.1 Menú principal"),
  ...figura("fig_menu_principal.png", 1340, 644, "Figura 2: Menú principal de ELCSoft", 14),
  tabla(["Opción", "Función"], [2600, 7038], [
    ["Iniciar nuevo ensayo", "Comienza un nuevo ensayo. Requiere completar los datos de la máquina, del ensayo y la configuración del hardware (2.3.2)."],
    ["Continuar un ensayo", "Retoma un ensayo interrumpido. Se carga el archivo principal (.csv); el programa detecta las ranuras registradas y continúa en la siguiente."],
    ["Abrir gráficos 2D", "Muestra Iq [mA] en función de la posición axial, por ranura (2.3.5)."],
    ["Abrir gráficos 3D", "Muestra el mapa completo: posición axial, número de ranura y magnitud de Iq (2.3.5)."],
    ["Parámetros", "Permite prefijar los mismos datos requeridos al iniciar un ensayo."],
  ]),
  h3("2.3.2 Parámetros del ensayo"),
  ...figura("fig_parametros.png", 1356, 674, "Figura 3: Menú de parámetros", 14),
  tabla(["Grupo / parámetro", "Descripción"], [2900, 6738], [
    { seccion: "Datos generales" },
    ["Datos de la máquina", "Identificación, tipo de rotor, potencia, tensión y velocidad nominales, longitud activa y diámetro interno del estator, número de polos y de ranuras."],
    ["Datos del ensayo", "Responsable del ensayo, ubicación y nombre de la central."],
    { seccion: "Configuración del hardware" },
    ["Placa DAQ", "Selección de la placa de adquisición (por defecto DEV1)."],
    ["Ranura inicial", "Permite comenzar el barrido en una ranura distinta de la primera (registros parciales, zonas sospechosas o sectores intervenidos). La numeración avanza luego de a una unidad, en forma creciente."],
    ["Frecuencia de ensayo", "50 o 60 Hz. Debe coincidir con la frecuencia de la fuente de excitación; un valor incorrecto distorsiona la medición de Iq."],
    ["Paso de registro [mm]", "Distancia axial entre puntos de registro de Iq. Mínimo 1 mm."],
    ["Offset axial de bobinas [mm]", "Distancia desde el borde inicial del núcleo hasta el centro de las bobinas captoras. Valor ≥ 0."],
    ["Constante de posición [mm/V]", "Convierte la señal analógica del sensor de posición axial en desplazamiento."],
    ["Constante de sensor Iq (KF)", "Constante adimensional del captor, determinada según el Protocolo 2."],
  ]),
  h3("2.3.3 Pantalla de adquisición"),
  ...figura("fig_adquisicion.png", 1344, 646, "Figura 4: Pantalla de adquisición de datos – registro de ranura", 15),
  tabla(["Elemento", "Descripción"], [2900, 6738], [
    { seccion: "Visualización" },
    ["Gráfico superior derecho", "Registro en tiempo real de Iq en función de la posición axial de la ranura en curso."],
    ["Semáforo de estado", "Verde: valor normal. Amarillo: advertencia. Rojo: por encima del umbral crítico."],
    ["Gráfico inferior derecho", "Registro de la ranura anterior, como referencia de comparación."],
    ["Gráfico superior izquierdo", "Mapa de color de Iq por ranura (vertical) y posición axial (horizontal); se actualiza con cada ranura."],
    ["Valores numéricos", "Delta (ángulo entre flujo e Iq), Flujo (señal del captor), Iq, Pos (posición axial en mm) y Ranura."],
    ["Indicador ON/OFF", "Verde (ON): registrando. Rojo (OFF): registro inactivo."],
    { seccion: "Configuración" },
    ["Umbrales rojo, naranja y amarillo", "Límites de Iq para las alertas visuales."],
    ["Dial Iq-range", "Escala vertical de los gráficos 2D."],
    ["KF", "Constante de calibración (Protocolo 2)."],
    ["Pos Encoder / Pos-cero", "Señal de posición axial y referencia de cero."],
    { seccion: "Botones de control" },
    ["Posición Cero", "Fija la posición axial cero; se realiza antes de cada ranura. Al valor se suma el offset axial configurado."],
    ["Iniciar", "Comienza la adquisición de la ranura actual."],
    ["Descartar ranura actual", "Elimina la pasada en curso ante errores o interferencias."],
    ["Guardar ranura", "Almacena en forma definitiva los datos de la ranura."],
    ["Volver al Menú", "Regresa al menú principal."],
  ]),
  h3("2.3.4 Secuencia de registro"),
  p("Con la calibración finalizada y KF definida, ubicar el robot en la posición axial cero sobre la ranura inicial:", { keepNext: true }),
  numerada("Presionar **Posición Cero** para fijar la referencia respecto del borde del núcleo.", "secuencia"),
  numerada("Presionar **Iniciar**; el indicador pasa a verde (ON).", "secuencia"),
  numerada("Avanzar el robot en sentido creciente de posición axial hasta completar la ranura.", "secuencia"),
  numerada("Ante cualquier problema, presionar **Descartar ranura actual** y repetir la pasada.", "secuencia"),
  numerada("Al finalizar, presionar **Guardar ranura**; el registro se detiene y el indicador vuelve a rojo (OFF).", "secuencia"),
  numerada("Posicionar el robot en la ranura siguiente y repetir hasta completar las ranuras previstas.", "secuencia"),
  numerada("Al completar la última ranura, presionar **Volver al Menú**.", "secuencia"),
  h3("2.3.5 Visualización de resultados"),
  ...figura("fig_graficos_2d.png", 1353, 701, "Figura 5: Visualización de gráficos 2D", 15),
  vineta("**Mapa 2D (izquierda):** cada línea es una ranura; el color indica la intensidad relativa de Iq según los umbrales ingresados."),
  vineta("**Gráficos por ranura (derecha):** Iq [mA] en función de la posición [mm], con número de ranura, Iq máxima e indicador de condición: verde (normal), amarillo (precaución), rojo (posible defecto)."),
  vineta("**Controles:** Amp2D (amplitud del mapa 2D), Up / Down / X5 (grupo de ranuras visualizado), Archivo (abrir otro registro) y Volver al Menú."),
  ...figura("fig_graficos_3d.png", 1356, 704, "Figura 6: Visualización de gráficos 3D", 15),
  p("El gráfico 3D (posición axial, número de ranura y magnitud de Iq) brinda una visión global del núcleo y facilita la localización de zonas con posibles defectos mediante una paleta de colores por umbral."),
  h3("2.3.6 Archivos generados"),
  tabla(["Archivo", "Contenido"], [2900, 6738], [
    ["Parámetros", "Todos los parámetros del ensayo."],
    ["Sufijo Iq / Iqp", "Datos matriciales para los gráficos 2D y 3D."],
    ["Sufijo reg", "Registro completo en bruto; respaldo y análisis posterior."],
  ]),

  // ---------------- APÉNDICE ----------------
  h2("2.4 APÉNDICE – CÁLCULO DE LA EXCITACIÓN: TENSIÓN Y CORRIENTE"),
  p("Este apartado explica cómo se obtienen la tensión por espira, el número de espiras del arrollamiento de excitación y la tensión y la corriente que debe entregar el Variac. Las expresiones siguen a Ridley [1] y son las del formulario **RME-ELC-01 «Registro de cálculo de excitación – Ensayo EL CID»**, donde se registra el cálculo de cada máquina."),

  h3("2.4.1 Criterio: 4 % del flujo nominal"),
  p("Según Ridley [1], el ensayo EL CID se realiza con el núcleo magnetizado a aproximadamente el **4 % del flujo nominal**. A ese nivel, las corrientes de falla entre laminaciones son medibles con el captor, el núcleo no se calienta y la potencia necesaria es de pocos kVA, que puede entregar un Variac monofásico."),
  p("Todo el cálculo parte de la **tensión por espira** $v_t$: la tensión que se induce en una espira que abraza el yugo con ese 4 % del flujo. Es lo que mide la espira auxiliar y, por lo tanto, la referencia de la calibración (Protocolo 2, paso 3) y del control durante todo el ensayo. Con $v_t$ se eligen el número de espiras $N$ y, con él, la tensión y la corriente del Variac."),

  h3("2.4.2 Parámetros"),
  p("La tabla reúne todos los parámetros que intervienen, su unidad y de dónde se obtienen:", { keepNext: true }),
  tabla(["Símbolo", "Parámetro", "Unidad", "Origen"], [1150, 4000, 1000, 3488], [
    { seccion: "Datos del generador" },
    ["$V_L$", "Tensión de línea nominal.", "V", "Placa del generador."],
    ["$f$", "Frecuencia nominal; es también la del ensayo.", "Hz", "Placa (50 o 60 Hz)."],
    ["$p$", "Número de polos.", "—", "Placa, o p = 120 · f / n con n la velocidad nominal [rpm]."],
    ["$Z$", "Número de ranuras del estator.", "—", "Documentación del fabricante o conteo."],
    ["$b$", "Barras (lados de bobina) por ranura.", "—", "Documentación; normalmente 2."],
    ["$n$", "Espiras en serie por barra.", "—", "Documentación; 1 en barras Roebel."],
    ["$a$", "Circuitos en paralelo por fase.", "—", "Documentación del fabricante."],
    ["$y$", "Paso de bobina, en ranuras.", "—", "Documentación o inspección del cabezal."],
    ["$d_ext$, $d_int$", "Diámetros exterior e interior del núcleo.", "m", "Planos o medición."],
    ["$h_r$", "Profundidad de ranura.", "m", "Planos o medición."],
    ["$l$", "Longitud axial total del núcleo.", "m", "Planos o medición."],
    ["$N_v$, $l_v$", "Cantidad y ancho de los canales de ventilación.", "—, m", "Planos o inspección."],
    ["$d_r$", "Diámetro del rotor (solo método 3).", "m", "Planos."],
    ["$B_nom$, $B_g$", "Inducción nominal en el yugo y en el entrehierro (métodos 2 y 3).", "T", "Diseño del generador; si no se dispone, el valor adoptado se indica en RME-ELC-01."],
    { seccion: "Magnitudes calculadas" },
    ["$q$, $τ$", "Ranuras por polo y fase; paso polar en ranuras.", "—", `Ecuación ${e("q")}.`],
    ["$k_d$, $k_p$, $K$", "Factores de distribución, de paso y de bobinado.", "—", `Ecuación ${e("k")}.`],
    ["$T_ph$", "Espiras en serie por fase.", "—", `Documentación o ecuación ${e("tph")}.`],
    ["$Φ_a$", "Flujo por polo en el entrehierro, a tensión nominal.", "Wb", `Ecuación ${e("fem")}.`],
    ["$v_t$", "Tensión por espira al 4 % del flujo nominal.", "V", `Ecuación ${e("vt")} (o ${e("yugo")}, ${e("rotor")}).`],
    ["$d_m$, $l_Fe$", "Diámetro medio del núcleo; longitud efectiva de hierro.", "m", `Ecuaciones ${e("fmm")} y ${e("yugo")}.`],
    { seccion: "Excitación" },
    ["$N$", "Espiras del arrollamiento de excitación.", "—", `Se elige con la ecuación ${e("n")}.`],
    ["$H$", "Campo magnético necesario para el 4 % del flujo.", "A/m", "RME-ELC-01 adopta 15 A/m como máximo estimado."],
    ["$ρ$, $p_Fe$", "Densidad del acero; pérdidas específicas al 4 % del flujo.", "kg/m³, W/kg", "7870 kg/m³; ≈ 0,014 W/kg (RME-ELC-01)."],
    ["$V_var$, $I_var$", "Tensión y corriente que entrega el Variac.", "V, A", `Ecuaciones ${e("vvar")} y ${e("s")}.`],
    ["$V_var,máx$, $I_máx$", "Límites del Variac y del ensayo.", "V, A", "230 V; 25 A (nominal del Variac) dentro del rango de 5 A a 40 A."],
  ]),

  h3("2.4.3 Tensión por espira – método 1: datos de bobinado (referencia)"),
  p("Para un flujo sinusoidal que recorre el yugo en forma anular, la ley de Faraday da el valor eficaz de la tensión inducida en una espira. El flujo por polo $Φ_a$ se divide en dos mitades al entrar en el yugo:"),
  ec("faraday"),
  p("En servicio, la tensión de fase fija el flujo por polo a través de la ecuación general de la fuerza electromotriz:"),
  ec("fem"),
  p("Reemplazando y tomando el 4 % del flujo nominal, la frecuencia se cancela y la tensión por espira depende solo de la tensión nominal y del bobinado:"),
  ec("vt"),
  p("Si $K$ y $T_ph$ no figuran en la documentación, se calculan con los datos constructivos del estator:"),
  ec("q"),
  ec("k"),
  ec("tph"),
  p("Para una verificación rápida en campo, con $K$ ≈ 0,926 la expresión se reduce a:"),
  ec("practica"),

  h3("2.4.4 Tensión por espira – métodos 2 y 3: geometría (verificación)"),
  p("Si no se conocen los datos de bobinado, o para verificar el método 1, $v_t$ se estima con la sección del yugo (método 2) o con el flujo en el entrehierro calculado con la geometría del rotor (método 3):"),
  ec("yugo"),
  ec("rotor"),
  p("Si estos valores difieren mucho del método 1, revisar los datos de entrada antes de iniciar el ensayo."),

  h3("2.4.5 Tensión y corriente del Variac"),
  p("El arrollamiento de excitación de $N$ espiras abraza el yugo igual que la espira auxiliar, por lo que la tensión que debe entregar el Variac es:"),
  ec("vvar"),
  p("**Corriente de magnetización.** Para establecer el flujo se necesita una fuerza magnetomotriz igual al campo $H$ por la longitud media del recorrido del flujo en el yugo:"),
  ec("fmm"),
  p("Multiplicando ambas expresiones, la potencia reactiva no depende del número de espiras:"),
  ec("q_reac"),
  p("**Pérdidas en el núcleo.** Se estiman con la masa del núcleo y las pérdidas específicas al 4 % del flujo:"),
  ec("pfe"),
  p("**Potencia y corriente.** La potencia aparente y la corriente que debe entregar el Variac son:"),
  ec("s"),
  p("**Elección de N.** Más espiras aumentan la tensión del Variac y reducen su corriente. $N$ debe cumplir a la vez el límite de tensión y el de corriente:"),
  ec("n"),
  p("Verificar además que $S$ no supere la potencia nominal del Variac (6 kVA) y que $I_var$ quede dentro del rango de 5 A a 40 A."),
  nota("Importante:", "la corriente y la potencia calculadas son estimaciones para elegir N y verificar el Variac. En el ensayo, la referencia es siempre la tensión medida en la espira auxiliar, que debe igualar el valor de vt calculado (Protocolo 2). La tensión y la corriente reales se registran en RME-ELC-01.", F.C.gris),

  h3("2.4.6 Ejemplo de cálculo (método 1)"),
  p("Generador de 11,5 kV, 50 Hz, 2 polos, 54 ranuras, 2 barras por ranura, 1 espira en serie por barra, paso de bobina de 22 ranuras y 1 circuito por fase:", { keepNext: true }),
  tabla(["Paso", "Cálculo", "Resultado"], [3000, 4238, 2400], [
    ["Ranuras por polo y fase; paso polar", "$q$ = 54 / (3 · 2);  $τ$ = 54 / 2", "9;  27 ranuras"],
    ["Factor de distribución", "$k_d$ = sen(9π/54) / (9 · sen(π/54))", "0,9555"],
    ["Factor de paso", "$k_p$ = sen((22/27) · π/2)", "0,9580"],
    ["Factor de bobinado", "$K$ = 0,9555 · 0,9580", "0,9153"],
    ["Espiras en serie por fase", "$T_ph$ = 54 · 2 · 1 / (6 · 1)", "18"],
    ["Tensión por espira", "$v_t$ = 0,04 · 11 500 / (2 · √3 · 0,9153 · 18)", "8,07 V/espira"],
    ["Verificación rápida", "$v_t$ ≈ 12,5 · 11,5 / 18", "7,99 V/espira"],
    ["Tensión del Variac con N = 5", "$V_var$ = 5 · 8,07", "40,3 V"],
  ]),

  h1("3. REGISTROS"),
  p("Los registros generados como consecuencia de las acciones involucradas en el documento son:", { keepNext: true }),
];

module.exports = { meta, cuerpo };
