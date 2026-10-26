// 00503-00-EPG002 — Anexo: Protocolos de ensayo EL CID (excitación, calibración, software ELCSoft).
const { Paragraph, AlignmentType, TextRun } = require("docx");
const F = require("./formato_mecanalisis");
const { p, vineta, numerada, h1, h2, h3, rol, nota, espacio, tabla, figura } = F;

const PROC = "00503-00-EPG001";

// ---------- ecuaciones ----------
// Texto con subíndices: "v_t" → v con subíndice t. Se evita OMML para que se vea igual en cualquier visor.
const ec = (expr, nro) => new Paragraph({
  alignment: AlignmentType.LEFT, spacing: { before: 80, after: 120 },
  tabStops: [{ type: "center", position: F.ANCHO / 2 }, { type: "right", position: F.ANCHO }],
  children: [
    new TextRun({ text: "\t" }),
    ...expr.split(/(\S_\{[^}]+\}|\S_[a-z]+)/u).filter(Boolean).map((t) => {
      const m = t.match(/^(\S)_\{?([^}]+?)\}?$/u);
      if (m) return [new TextRun({ text: m[1], italics: true, size: 24 }), new TextRun({ text: m[2], subScript: true, size: 24 })];
      return [new TextRun({ text: t, size: 24 })];
    }).flat(),
    new TextRun({ text: `\t(${nro})`, color: F.C.gris }),
  ],
});

const meta = {
  codigo: "00503-00-EPG002",
  version: "00",
  fecha: "26/10/2026",
  tipo: "PROCEDIMIENTO – ANEXO",
  tituloEncabezado: ["PROTOCOLOS DE ENSAYO EL CID", "EXCITACIÓN, CALIBRACIÓN Y SOFTWARE"],
  tituloPortada: ["PROTOCOLOS DE ENSAYO EL CID", "Excitación del núcleo, calibración y operación de ELCSoft"],
  objetivo: `Establecer los protocolos técnicos para la excitación del núcleo, la calibración del sistema de medición y la operación del software ELCSoft en el ensayo EL CID, como anexo del procedimiento ${PROC}.`,
  alcance: "Ensayo EL CID para determinar la condición de la aislación interlaminar de núcleos estatóricos de generadores eléctricos, con el rotor colocado (inspección robotizada GRIS) o con el rotor desmontado.",
  responsable: "Gerente de Operaciones e Ingeniería.",
  listasNumeradas: ["calib", "secuencia"],
  registros: [
    ["A asignar", "Registro de calibración EL CID (tensión por espira, corriente de falla, KF)"],
    ["—", "Archivos de ensayo ELCSoft: parámetros, matrices Iq e Iqp y registro en bruto (reg)"],
    ["A asignar", "Memoria de cálculo de la excitación del núcleo (#####-##-EMC###)"],
  ],
  revisiones: [["N° 00", "26/10/2026", "Versión inicial. Adaptación al formato Mecanálisis de los «Protocolos de ensayo ELCID robotizado» (Nexergy Corp., junio 2025)."]],
  firmas: ["", "", "", ""],
  referencias: [
    "Norma ISO 9001:2015",
    `${PROC} – Procedimiento de inspección robotizada GRIS`,
    "Protocolos de ensayo ELCID robotizado – Nexergy Corp., junio 2025 (Tarea N° 19, Producto N° 7)",
    "IEEE Std 56-2016 – Guide for Insulation Maintenance of Electric Machines",
  ],
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
    ["**Vl, Tph, K**", "Tensión de línea nominal, número de espiras en serie por fase y factor de bobinado (paso × distribución) del generador."],
  ]),

  h1("2. RESPONSABILIDADES"),
  rol("Ingeniero de Generadores (IG)"),
  vineta("Calcular la excitación del núcleo (Protocolo 1) y validar la calibración (Protocolo 2)."),
  rol("Responsable del Ensayo (RE)"),
  vineta("Aplicar los protocolos en sitio, registrar la calibración y resguardar los archivos generados por ELCSoft."),

  h1("3. CONTENIDO"),
  p(`Este anexo contiene los tres protocolos que se invocan desde ${PROC}:`),
  tabla(["Protocolo", "Contenido", "Invocado en " + PROC], [2600, 4238, 2800], [
    ["Protocolo 1 – Excitación del núcleo", "Equipo, puesta a tierra, cálculo y montaje del arrollamiento de excitación y espira auxiliar.", "Pasos 6, 7, 10, 15, 18 y 25"],
    ["Protocolo 2 – Calibración", "Tensión por espira, corriente de falla controlada y constante KF.", "Pasos 13, 34, 40 y 44"],
    ["Protocolo 3 – Software ELCSoft", "Parámetros, registro de ranuras, visualización y archivos.", "Pasos 27, 37 y 39"],
  ]),

  // ---------------- PROTOCOLO 1 ----------------
  h2("3.1 PROTOCOLO 1 – EXCITACIÓN DEL NÚCLEO"),
  p("Guía para la magnetización débil del núcleo estatórico a ensayar."),
  h3("3.1.1 Características técnicas del equipo"),
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
  h3("3.1.2 Puesta a tierra"),
  nota("Precaución:", "la puesta a tierra se realiza en forma local desde el estator de la máquina y se distribuye radialmente hacia cada equipo del ensayo. El borne «Ground» del equipo EL CID es su única vinculación a tierra: no se admite ninguna otra conexión paralela o secundaria. Esta disposición evita lazos de corriente que inducen señales espurias y ponen en riesgo los equipos conectados."),
  h3("3.1.3 Cálculo del número de espiras"),
  p("El número de espiras se determina a partir de la tensión por espira calculada según el apartado 3.4 (Apéndice), considerando que:"),
  vineta("La tensión aplicada no supere la capacidad nominal del Variac."),
  vineta("La corriente de excitación resultante quede dentro del rango operativo recomendado: **5 A a 40 A**."),
  h3("3.1.4 Selección de la sección del conductor"),
  p("La sección del conductor debe admitir la corriente de ensayo sin sobrecalentamiento. Un conductor sobrecalentado aumenta su resistencia, reduce la corriente de excitación y obliga a recalibrar y a corregir permanentemente la tensión aplicada para mantener constante la tensión por espira."),
  h3("3.1.5 Montaje con rotor desmontado"),
  vineta("Fijar el arrollamiento en forma concéntrica respecto del eje del núcleo, cubriendo toda su longitud axial."),
  vineta("En los extremos del núcleo, utilizar un radio de curvatura amplio para evitar efectos de borde."),
  vineta("Agrupar en forma compacta el tramo del arrollamiento dispuesto a lo largo del eje."),
  h3("3.1.6 Montaje con rotor colocado"),
  vineta("Aislar eléctricamente el rotor de su apoyo, al menos en uno de sus extremos, para que no forme una espira de falla con el núcleo y el arrollamiento de excitación."),
  vineta("Ubicar el arrollamiento lateralmente al núcleo, en la medida de lo posible."),
  vineta("Desplazar el arrollamiento a medida que avanza el ensayo, para evitar que el captor quede próximo al conductor de excitación (el acoplamiento directo produce lecturas erróneas)."),
  nota("Inspección GRIS:", `la ubicación inicial y la reubicación del arrollamiento cada 120° se realizan según ${PROC}, pasos 16, 17 y 44.`, F.C.gris),
  h3("3.1.7 Montaje de la espira auxiliar"),
  p("La espira auxiliar permite medir la tensión por espira durante todo el ensayo y generar la corriente de falla controlada de calibración (Protocolo 2). Se aloja dentro de una ranura del estator, en una posición fija y representativa."),
  p("Dado que la corriente de calibración es baja (100 mA a 200 mA) y que la espira no conduce corriente en forma permanente, se recomienda un conductor de **1,5 mm²**."),
  nota("Precaución:", "verificar que la espira auxiliar no quede en cortocircuito en ningún momento del ensayo. Un cortocircuito provocaría una corriente elevada y no controlada, con riesgo para el equipo, el sensor y la validez del ensayo."),

  // ---------------- PROTOCOLO 2 ----------------
  h2("3.2 PROTOCOLO 2 – CALIBRACIÓN"),
  p("Establece la correspondencia entre la señal medida por el captor y una corriente de falla conocida, a partir de la configuración de referencia de la Figura 1. La puesta a tierra se realiza según 3.1.2."),
  ...figura("fig_calibracion.png", 1292, 537, "Figura 1: Configuración de referencia para la calibración del ensayo EL CID"),
  numerada("**Preparación.** Verificar que el arrollamiento de excitación (número de espiras calculado) y la espira auxiliar estén montados según el Protocolo 1.", "calib"),
  numerada("**Ausencia de espiras parásitas.** Antes de energizar, retirar o reubicar todo elemento conductor que forme un lazo cerrado alrededor del núcleo: cintas pasacables metálicas, alambres o cables sueltos, herramientas, fijaciones o elementos estructurales transversales al flujo. Estos lazos inducen corrientes espurias que simulan fallas inexistentes.", "calib"),
  numerada("**Tensión por espira.** Alimentar el arrollamiento con el Variac y ajustar la tensión hasta que la tensión medida en la espira auxiliar sea igual al valor teórico calculado (apartado 3.4).", "calib"),
  numerada("**Corriente de falla.** Con la espira auxiliar firmemente alojada en su ranura, conectar en serie una resistencia de calibración de valor tal que circule una corriente de **100 mA a 200 mA**.", "calib"),
  numerada("**Posicionamiento del captor.** Alinear el eje central entre las dos bobinas captoras con el centro de la ranura de la espira auxiliar, a una distancia del borde del núcleo de aproximadamente **¼ de la longitud total del núcleo**, para minimizar los efectos de borde.", "calib"),
  numerada("**Constante KF.** En ELCSoft, ajustar KF hasta que la lectura coincida con la corriente de falla establecida.", "calib"),
  numerada("**Finalización.** Abrir el circuito de la espira auxiliar y confirmar que la tensión en ella sea igual a la tensión por espira calculada. Registrar los valores en el registro de calibración.", "calib"),
  espacio(60),
  nota("Durante el ensayo:", "monitorear continuamente la tensión por espira y corregirla cuando sea necesario para mantenerla constante.", F.C.gris),

  // ---------------- PROTOCOLO 3 ----------------
  h2("3.3 PROTOCOLO 3 – OPERACIÓN DEL SOFTWARE ELCSOFT"),
  p("ELCSoft 1.0 es el software de adquisición del ensayo EL CID. Permite iniciar ensayos, continuar ensayos incompletos y visualizar los resultados en forma gráfica."),
  h3("3.3.1 Menú principal"),
  ...figura("fig_menu_principal.png", 1340, 644, "Figura 2: Menú principal de ELCSoft", 14),
  tabla(["Opción", "Función"], [2600, 7038], [
    ["Iniciar nuevo ensayo", "Comienza un nuevo ensayo. Requiere completar los datos de la máquina, del ensayo y la configuración del hardware (3.3.2)."],
    ["Continuar un ensayo", "Retoma un ensayo interrumpido. Se carga el archivo principal (.csv); el programa detecta las ranuras registradas y continúa en la siguiente."],
    ["Abrir gráficos 2D", "Muestra Iq [mA] en función de la posición axial, por ranura (3.3.5)."],
    ["Abrir gráficos 3D", "Muestra el mapa completo: posición axial, número de ranura y magnitud de Iq (3.3.5)."],
    ["Parámetros", "Permite prefijar los mismos datos requeridos al iniciar un ensayo."],
  ]),
  h3("3.3.2 Parámetros del ensayo"),
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
  h3("3.3.3 Pantalla de adquisición"),
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
  h3("3.3.4 Secuencia de registro"),
  p("Con la calibración finalizada y KF definida, ubicar el robot en la posición axial cero sobre la ranura inicial:", { keepNext: true }),
  numerada("Presionar **Posición Cero** para fijar la referencia respecto del borde del núcleo.", "secuencia"),
  numerada("Presionar **Iniciar**; el indicador pasa a verde (ON).", "secuencia"),
  numerada("Avanzar el robot en sentido creciente de posición axial hasta completar la ranura.", "secuencia"),
  numerada("Ante cualquier problema, presionar **Descartar ranura actual** y repetir la pasada.", "secuencia"),
  numerada("Al finalizar, presionar **Guardar ranura**; el registro se detiene y el indicador vuelve a rojo (OFF).", "secuencia"),
  numerada("Posicionar el robot en la ranura siguiente y repetir hasta completar las ranuras previstas.", "secuencia"),
  numerada("Al completar la última ranura, presionar **Volver al Menú**.", "secuencia"),
  h3("3.3.5 Visualización de resultados"),
  ...figura("fig_graficos_2d.png", 1353, 701, "Figura 5: Visualización de gráficos 2D", 15),
  vineta("**Mapa 2D (izquierda):** cada línea es una ranura; el color indica la intensidad relativa de Iq según los umbrales ingresados."),
  vineta("**Gráficos por ranura (derecha):** Iq [mA] en función de la posición [mm], con número de ranura, Iq máxima e indicador de condición: verde (normal), amarillo (precaución), rojo (posible defecto)."),
  vineta("**Controles:** Amp2D (amplitud del mapa 2D), Up / Down / X5 (grupo de ranuras visualizado), Archivo (abrir otro registro) y Volver al Menú."),
  ...figura("fig_graficos_3d.png", 1356, 704, "Figura 6: Visualización de gráficos 3D", 15),
  p("El gráfico 3D (posición axial, número de ranura y magnitud de Iq) brinda una visión global del núcleo y facilita la localización de zonas con posibles defectos mediante una paleta de colores por umbral."),
  h3("3.3.6 Archivos generados"),
  tabla(["Archivo", "Contenido"], [2900, 6738], [
    ["Parámetros", "Todos los parámetros del ensayo."],
    ["Sufijo Iq / Iqp", "Datos matriciales para los gráficos 2D y 3D."],
    ["Sufijo reg", "Registro completo en bruto; respaldo y análisis posterior."],
  ]),

  // ---------------- APÉNDICE ----------------
  h2("3.4 APÉNDICE – DETERMINACIÓN DE LA TENSIÓN POR ESPIRA"),
  p("Para un flujo sinusoidal Φ = Φm · sen(2πft) inducido en forma anular en el núcleo, la tensión inducida por espira (ley de Faraday) tiene un valor eficaz:"),
  ec("v_t = 2π · f · Φ_m / √2", 1),
  p("Como el flujo por polo en el entrehierro, Φa, se divide en dos mitades en el yugo (Φm = Φa/2):"),
  ec("v_t = π · f · Φ_a / √2 = 2,22 · f · Φ_a", 2),
  p("Para el 4 % del flujo nominal: v4% = 0,0888·f·Φa, es decir **4,44·Φa** a 50 Hz y **5,33·Φa** a 60 Hz. El flujo en el entrehierro [Wb] es:"),
  ec("Φ_a = (V_l / √3) / (4,44 · K · T_{ph} · f)", 3),
  p("Reemplazando, la tensión por espira para el 4 % del flujo nominal resulta:"),
  ec("v_t = 0,04 · V_l / (√3 · 2 · K · T_{ph})", 4),
  p("Con Vl en kV y K = 0,926 se obtiene la expresión práctica [V/espira]:"),
  ec("v_t ≈ 12,5 · V_l [kV] / T_{ph}", 5),
  p("Donde Vl es la tensión de línea nominal, K el factor de bobinado (paso × distribución) y Tph el número de espiras en serie por fase."),

  h1("4. REGISTROS"),
  p("Los registros generados como consecuencia de las acciones involucradas en el documento son:"),
];

module.exports = { meta, cuerpo };
