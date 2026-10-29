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
const ORDEN_EC = ["flujo", "faraday", "eficaz", "mitad", "v4", "fem", "vt", "practica"];
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
  fecha: "29/10/2026",
  tipo: "PROCEDIMIENTO – ANEXO",
  tituloEncabezado: ["PROTOCOLOS DE ENSAYO EL CID", "EXCITACIÓN, CALIBRACIÓN Y SOFTWARE"],
  tituloPortada: ["PROTOCOLOS DE ENSAYO EL CID", "Excitación del núcleo, calibración y operación de ELCSoft"],
  objetivo: `Establecer los protocolos técnicos para la excitación del núcleo, la calibración del sistema de medición y la operación del software ELCSoft en el ensayo EL CID, como anexo del procedimiento ${PROC}.`,
  alcance: "Ensayo EL CID para determinar la condición de la aislación interlaminar de núcleos estatóricos de generadores eléctricos, con el rotor colocado (inspección robotizada GRIS) o con el rotor desmontado.",
  listasNumeradas: ["calib", "secuencia"],
  registros: [["RME-ELC-01", "Registro de cálculo de excitación – Ensayo EL CID"]],
  revisiones: [["00", "29/10/2026", "Versión inicial. Adaptación al formato Mecanálisis de los «Protocolos de ensayo ELCID robotizado» (Nexergy Corp., junio 2025)."]],
  firmas: ["Matias Gaviño", "", "", ""],
  referencias: ["[1] Ridley G. K., «EL CID – Application and Analysis», 2000."],
};

const cuerpo = [
  h1("1. DEFINICIONES"),
  tabla(["Término", "Significado"], [1700, 7938], [
    ["**EL CID**", "Electromagnetic Core Imperfection Detection. Ensayo de la aislación interlaminar del núcleo estatórico mediante magnetización débil (≈ 4 % del flujo nominal)."],
    ["**Iq**", "Componente en cuadratura de la corriente de falla, medida por el captor [mA]."],
    ["**Captor**", "Sensor magnético de dos bobinas captoras que mide la corriente de falla."],
    ["**Espira auxiliar**", "Conductor fijo en una ranura que permite medir la tensión por espira y generar la falla simulada de calibración."],
    ["**KF**", "Constante de calibración del captor (constante de sensor Iq) en el software."],
    ["**ELCSoft**", "Software de adquisición y visualización del ensayo EL CID (versión 1.0)."],
    ["**DAQ**", "Unidad de adquisición de datos."],
  ]),

  h1("2. CONTENIDO"),
  p(`Este anexo contiene los tres protocolos que se invocan desde ${PROC}:`),
  tabla(["Protocolo", "Contenido", "Invocado en " + PROC], [2600, 4238, 2800], [
    ["Protocolo 1 – Excitación del núcleo", "Equipo, puesta a tierra, cálculo y montaje del arrollamiento de excitación y espira auxiliar.", `Apartados ${invocado(1)}`],
    ["Protocolo 2 – Calibración", "Tensión por espira, falla simulada de calibración y constante KF.", `Apartados ${invocado(2)}`],
    ["Protocolo 3 – Software ELCSoft", "Parámetros, registro de ranuras, visualización y archivos.", `Apartados ${invocado(3)}`],
  ]),

  // ---------------- PROTOCOLO 1 ----------------
  h2("2.1 PROTOCOLO 1 – EXCITACIÓN DEL NÚCLEO"),
  p("Guía para la magnetización débil del núcleo estatórico a ensayar."),
  h3("2.1.1 Características técnicas del equipo"),
  tabla(["Característica", "Valor"], [4200, 5438], [
    ["Alimentación eléctrica", "CA 110/220 V, 50/60 Hz"],
    ["Corriente de excitación", "5 A a 40 A"],
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
  vineta("La tensión aplicada no supere la capacidad nominal del autotransformador."),
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
  p("La espira auxiliar permite medir la tensión por espira durante todo el ensayo y generar la falla simulada de calibración (Protocolo 2). Se aloja dentro de una ranura del estator, en una posición fija y representativa."),
  p("Dado que la corriente de calibración es baja (100 mA a 200 mA) y que la espira no conduce corriente en forma permanente, se recomienda un conductor de **1,5 mm²**."),
  nota("Precaución:", "verificar que la espira auxiliar no quede en cortocircuito en ningún momento del ensayo. Un cortocircuito provocaría una corriente elevada y no controlada, con riesgo para el equipo, el sensor y la validez del ensayo."),

  // ---------------- PROTOCOLO 2 ----------------
  h2("2.2 PROTOCOLO 2 – CALIBRACIÓN"),
  p("Establece la correspondencia entre la señal medida por el captor y una corriente de falla conocida, a partir de la configuración de referencia de la Figura 1. La puesta a tierra se realiza según 2.1.2."),
  ...figura("fig_calibracion.png", 1292, 537, "Figura 1: Configuración de referencia para la calibración del ensayo EL CID"),
  numerada("**Preparación.** Verificar que el arrollamiento de excitación (número de espiras calculado) y la espira auxiliar estén montados según el Protocolo 1.", "calib"),
  numerada("**Ausencia de espiras parásitas.** Antes de energizar, retirar o reubicar todo elemento conductor que forme un lazo cerrado alrededor del núcleo: cintas pasacables metálicas, alambres o cables sueltos, herramientas, fijaciones o elementos estructurales transversales al flujo. Estos lazos inducen corrientes espurias que simulan fallas inexistentes.", "calib"),
  numerada("**Tensión por espira.** Alimentar el arrollamiento con el autotransformador y ajustar la tensión hasta que la tensión medida en la espira auxiliar sea igual al valor teórico calculado (apartado 2.4).", "calib"),
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
  h2("2.4 APÉNDICE – DETERMINACIÓN DE LA TENSIÓN POR ESPIRA"),
  p("El ensayo se realiza con el núcleo magnetizado al 4 % del flujo nominal (Ridley [1]). El cálculo de cada máquina se registra en RME-ELC-01 «Registro de cálculo de excitación – Ensayo EL CID»."),
  p("Considerando $Φ$ el flujo sinusoidal inducido en forma anular en el núcleo del estator:"),
  ec("flujo"),
  p("donde $Φ_m$ es el valor máximo del flujo [Wb], $f$ la frecuencia [Hz] y $t$ el tiempo [s]. La tensión inducida por espira viene dada por la ley de Faraday:"),
  ec("faraday"),
  p("cuyo valor eficaz es:"),
  ec("eficaz"),
  p("El flujo por polo a través del entrehierro, $Φ_a$, queda dividido en dos en el yugo, por lo tanto:"),
  ec("mitad"),
  p("Para un 4 % del flujo nominal en el entrehierro, la tensión eficaz por espira es la siguiente; para 50 Hz resulta $v_4%$ = 4,44 · $Φ_a$ y para 60 Hz, $v_4%$ = 5,33 · $Φ_a$:"),
  ec("v4"),
  p("El flujo en el entrehierro de la máquina, en webers, es:"),
  ec("fem"),
  p("donde $V_l$ es la tensión de línea, $K$ la combinación de los factores de paso y de distribución y $T_ph$ el número de espiras por fase. Para el 4 % del flujo nominal, la tensión por espira queda:"),
  ec("vt"),
  p("Si $V_l$ se expresa en kV y se adopta $K$ = 0,926:"),
  ec("practica"),

  h1("3. REGISTROS"),
  p("Los registros generados como consecuencia de las acciones involucradas en el documento son:", { keepNext: true }),
];

module.exports = { meta, cuerpo };
