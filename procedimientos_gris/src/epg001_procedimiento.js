// 00503-00-EPG001 — Procedimiento general de inspección robotizada GRIS (visual, EL CID y WTT).
// Los pasos se numeran automáticamente; las referencias cruzadas usan {id} → número de paso.
const F = require("./formato_mecanalisis");
const { p, h1, h2, nota, espacio, tabla, pasos } = F;

const ANEXO = "00503-00-EPG002";
const P1 = `${ANEXO} – Protocolo 1`;
const P2 = `${ANEXO} – Protocolo 2`;
const P3 = `${ANEXO} – Protocolo 3`;
const CHECKLIST = "00503-00-ZRQ001";
const MANUAL = "00503-00-EPG003";
const RIESGO = "00503-00-ZIT003";
const ESQUEMA = "Figura 1";

const meta = {
  codigo: "00503-00-EPG001",
  version: "00",
  fecha: "28/10/2026",
  tipo: "PROCEDIMIENTO",
  tituloEncabezado: ["INSPECCIÓN ROBOTIZADA GRIS", "ENSAYOS EL CID Y WTT EN ENTREHIERRO"],
  tituloPortada: ["INSPECCIÓN ROBOTIZADA GRIS", "Inspección visual, EL CID y WTT en el entrehierro"],
  objetivo: "Establecer la metodología para ejecutar la inspección robotizada del entrehierro de generadores de rotor cilíndrico mediante el sistema GRIS, asegurando la seguridad del personal y del equipo, la calidad de los datos adquiridos y la trazabilidad de los resultados.",
  alcance: [
    "Aplica exclusivamente a la inspección robotizada en el entrehierro de generadores de rotor cilíndrico **con el rotor montado**, que comprende una o más de las siguientes tareas, según lo acordado en el servicio:",
    "**a)** Inspección visual del estator (ranuras, cuñas y canales de ventilación).",
    "**b)** Ensayo EL CID del núcleo estatórico.",
    "**c)** Ensayo WTT de ajuste de cuñas del estator.",
    "Este documento es el procedimiento general de la inspección. Los aspectos técnicos de cada tarea se desarrollan en los documentos asociados indicados en el apartado 2.2.",
  ],
  registros: [],
  revisiones: [["00", "28/10/2026", "Versión inicial."]],
  firmas: ["Matias Gaviño", "", "", ""],
  referencias: [],
};

// ---------------------------------------------------------------------------
// Etapas y pasos. Cada paso: [id | null, actividad, referencia]. { seccion } agrega un subtítulo.
const etapas = [
  { id: "seg", titulo: "SEGURIDAD Y PERMISOS", ref: "ATS / requisitos del Cliente", pasos: [
    [null, "Asistir a la inducción de seguridad del sitio y revisar la evaluación de riesgos del Cliente.", "Requisitos del Cliente"],
    [null, "Obtener el permiso de trabajo y el permiso de aislamiento/bloqueo. El Cliente debe verificar la ausencia de tensión antes de iniciar cualquier tarea.", "Permiso de trabajo"],
    [null, "Confeccionar el ATS considerando los riesgos del apartado 2.1 y revisarlo con todo el personal involucrado. Utilizar como mínimo el EPP especificado y el adicional que requieran las condiciones del sitio.", "ATS"],
    [null, "Vallar el área de trabajo y colocar carteles que indiquen «Ensayo eléctrico en curso».", "—"],
  ], despues: () => [espacio(), nota("Reglas permanentes:", `desenergizar el arrollamiento de excitación durante pausas, descansos y ante cualquier intervención mecánica sobre el sistema. Respetar el esquema de puesta a tierra única definido en ${P1}.`)] },

  { id: "prep", titulo: "PREPARACIÓN TÉCNICA PREVIA", ref: P1, pasos: [
    [null, "Definir con el Cliente los ensayos a realizar: inspección visual, EL CID y/o WTT.", "Alcance del servicio"],
    [null, "Obtener los datos de la máquina: número de serie, datos de placa, dimensiones principales, número de ranuras, longitud axial del núcleo, diámetro y entrehierro disponibles, y datos para el cálculo de la excitación.", `${ANEXO}, apartado 2.4`],
    [null, "Calcular la excitación del núcleo (tensión por espira, número de espiras, tensión y corriente del Variac y sección del conductor) y registrarla en RME-ELC-01, o solicitarla a Ingeniería.", `${ANEXO}, apartado 2.4 / RME-ELC-01`],
    ["operadores", "Asignar al menos dos operadores calificados para el ensayo y planificar pausas regulares.", "—"],
    [null, "Verificar que el kit de repuestos GRIS esté completo.", "Tabla 1"],
    [null, "Confirmar la disponibilidad de alimentación para la PC GRIS, la PC EL CID, el control box, el tablero EL CID y el Variac. Verificar la protección diferencial.", "—"],
  ] },

  { id: "area", titulo: "PREPARACIÓN DEL ÁREA Y CONVENCIONES", ref: "—", pasos: [
    [null, "Preparar un área de trabajo despejada o un banco en un extremo del generador, con visibilidad de la pantalla del sistema desde el interior del estator o desde el puesto de operación.", "—"],
    [null, "Verificar que al menos un extremo del rotor esté aislado de tierra.", P1],
    ["conv", "Definir con el Cliente las convenciones de referencia indicadas en la Tabla 2 y registrarlas antes de iniciar el ensayo.", "Tabla 2"],
    [null, "Identificar las ranuras con cinta o marcas visibles, como mínimo cada cinco ranuras. Reforzar la identificación en la ranura inicial, en las ranuras de control y en los sectores de cambio de excitación.", "—"],
    [null, "Verificar que no existan lazos conductores cerrados alrededor del núcleo que puedan afectar la excitación del EL CID.", P2],
  ], despues: () => [
    espacio(),
    p("**Tabla 2: Convenciones de referencia.** Se acuerdan con el Cliente; cuando no exista una convención previa se aplica el criterio indicado.", { keepNext: true }),
    tabla(["Convención", "Criterio"], [2800, 6838], [
      ["Ranura 1", "Según la convención previa del Cliente. Si no existe, la ranura ubicada en el punto muerto superior (PMS)."],
      ["Sentido de numeración", "Según la convención previa del Cliente. Si no existe, sentido horario visto desde el lado DE."],
      ["Sentido de avance angular", "Sentido creciente de la numeración de ranuras (ELCSoft incrementa el número de ranura de a una unidad)."],
      ["Lado de ingreso del robot", "DE o NDE, según la accesibilidad de la máquina."],
      ["Cero axial", "Borde del núcleo del lado de ingreso del robot. Las posiciones axiales crecen hacia el extremo opuesto."],
    ]),
  ] },

  { id: "exc", titulo: "MONTAJE DE LA EXCITACIÓN DEL NÚCLEO", ref: P1, pasos: [
    [null, "Montar el cable de excitación a través del entrehierro y conectar sus extremos a la bornera EXCITATION del tablero de excitación, haciendo coincidir números y colores, de modo que las espiras queden en serie.", `${P1} / Figura 1`],
    ["variac", "Con el Variac desconectado de la red, conectar su ficha al tablero de excitación. Recién entonces conectar el Variac a la red. Para desconectar, seguir el orden inverso: primero desconectar el Variac de la red y luego la ficha.", "Apartado 2.1 / Figura 1"],
    [null, "Ubicar inicialmente el arrollamiento a 120° de la primera ranura a inspeccionar, en sentido opuesto al avance angular previsto.", "—"],
    [null, "Planificar la reubicación del arrollamiento cada 120° de avance angular, de modo que durante el ensayo nunca quede a menos de 120° de la ranura inspeccionada.", "Paso {reubicar}"],
    [null, "Instalar la espira auxiliar en la primera ranura a inspeccionar o en la ranura definida por Ingeniería.", P1],
  ], despues: () => [espacio(), nota("Precaución:", ref("el tablero de excitación se encuentra en desarrollo. No operarlo ni manipularlo con tensión. La ficha que viene del Variac queda con los contactos macho expuestos: nunca manipularla con el Variac conectado a la red (paso {variac})."))] },

  { id: "conf", titulo: "CONFIGURACIÓN Y MONTAJE DEL SISTEMA GRIS", ref: `${P3} / ${MANUAL} / Figura 1`, intro: "Las conexiones se realizan según el esquema general de la Figura 1.", pasos: [
    ["sw_config", "Ingresar en el software GRIS los parámetros geométricos medidos y obtener los valores de ajuste del robot y de la rampa.", `${MANUAL}, apartado 4.2`],
    [null, "Cortar los rieles de la rampa a la longitud requerida. Limar los bordes y eliminar rebabas.", "—"],
    ["sw_rampa", "Ajustar la rampa con los valores obtenidos para posicionar tangencialmente el robot sobre la ranura a inspeccionar.", `${MANUAL}, apartado 4.2`],
    [null, "Proteger con cinta (duct tape) las zonas de contacto de la rampa con el cuerpo del rotor y, cuando corresponda, el trinquete.", "—"],
    [null, "Ajustar las cámaras inferiores, las cámaras laterales y el captor Chattock según la geometría de la ranura y del entrehierro. Instalar las guías centrales adecuadas, dejando una holgura recomendada de 1 a 2 mm.", "—"],
    ["conexiones", "Realizar las conexiones de la Figura 1: arnés del robot al control box (cable principal) y al tablero EL CID (señal del captor); control box al tablero EL CID (señal de posición); PC GRIS al control box (USB y Ethernet); PC EL CID al tablero EL CID (USB); tablero de excitación (Variac, cable de excitación, espira auxiliar y salida al tablero EL CID) y alimentaciones desde la red (regleta de enchufes), respetando el esquema de puesta a tierra.", `${ESQUEMA} / ${P1} / ${MANUAL}, apartado 3.1`],
    ["cuerdas", "Instalar las cuerdas de seguridad del robot y atarlas al punto de amarre con un nudo ocho reconstruido. Verificar el nudo según la Tabla 3.", "Figura 2 / Tabla 3"],
    ["sw_param", "Configurar en ELCSoft los parámetros del ensayo y el paso de registro EL CID (recomendado: 7 mm). Configurar el paso de adquisición automática de fotografías y el paso de muestreo WTT.", `${P3} / ${MANUAL}, apartados 4.4 y 5.3`],
    ["check", "Realizar la verificación pre-ensayo de desprendimiento de piezas del robot y registrarla en el checklist antes de introducir el robot.", `${CHECKLIST} (Pre-Test)`],
    ["montaje", "Montar el robot sobre la rampa y verificar que el conjunto ingresa, se posiciona y se desplaza sin interferencias.", `${MANUAL}, apartado 4.3`],
  ], despues: () => [
    F.hojaA3("esquema_general.png", 5200, 3000, "Figura 1: Esquema general de conexiones del sistema GRIS"),
    p(ref("**Amarre de las cuerdas de seguridad: nudo ocho reconstruido (paso {cuerdas}).** Las cuerdas de seguridad (3 mm) se atan al punto de amarre del robot con un nudo ocho reconstruido, también llamado ocho por seno reconstituido. Se usa este nudo porque, bien hecho y apretado, no se corre ni se desata con los tirones y las vibraciones del ensayo: al tensarse, los ramales paralelos se aprietan entre sí y el nudo se bloquea. Además es fácil de controlar a simple vista, porque bien hecho siempre muestra la misma figura. La Figura 2 muestra la secuencia de atado en el robot."), { keepNext: true }),
    ...F.figura("nudo_ocho.png", 3200, 3000, "Figura 2: Nudo ocho reconstruido paso a paso en el punto de amarre del robot", 17),
    p("Secuencia de atado:", { keepNext: true }),
    tabla(["Paso", "Acción"], [900, 8738], [
      ["1", "A unos 30 cm de la punta (chicote), hacer un bucle con la cuerda."],
      ["2", "Dar una vuelta con la punta alrededor de la cuerda principal (firme)."],
      ["3", "Pasar la punta por el bucle: queda un ocho simple, flojo."],
      ["4", "Pasar la punta por el ojal de amarre del robot."],
      ["5", "Volver con la punta por el mismo camino del ocho, en sentido inverso y siempre al lado de la cuerda, sin cruzarla."],
      ["6", "Seguir hasta que la punta salga del nudo junto a la cuerda principal: queda un ocho doble."],
      ["7", "Acomodar el nudo (cuerdas de a pares, paralelas y sin cruzarse) y apretarlo tirando por separado de las cuatro puntas. Dejar de 3 cm a 5 cm de punta libre."],
    ], { centrar: [0], keepNext: true }),
    espacio(),
    p("**Tabla 3: Verificación del nudo ocho reconstruido.** La realiza el operador que lo ató y la repite un segundo operador antes de introducir el robot en el entrehierro:", { keepNext: true }),
    tabla(["Control", "Criterio de aceptación"], [2400, 7238], [
      ["Figura", "Se ve un ocho completo, formado en todo su recorrido por pares de cuerdas paralelas."],
      ["Ramales", "Los dos ramales de cada par van juntos, sin cruzarse ni montarse uno sobre el otro."],
      ["Recorrido", "El lazo pasa por el ojal de amarre del robot y la punta (chicote) sale del nudo junto a la cuerda principal (firme)."],
      ["Apriete", "El nudo no se deforma ni se corre al tirar con fuerza de la cuerda principal y del lazo."],
      ["Punta libre", "Entre 3 cm y 5 cm (unas 10 a 15 veces el diámetro de la cuerda). Más corto puede salirse del nudo; más largo puede engancharse o quedar debajo del robot."],
    ]),
    nota("Importante:", "si algún control no se cumple, desatar el nudo y volver a hacerlo desde el paso 1. Revisar el nudo al inicio de cada jornada y cada vez que la cuerda haya quedado enganchada o haya soportado un tirón.", F.C.gris),
  ] },

  { id: "cal", titulo: "RECONOCIMIENTO Y CALIBRACIÓN", ref: P2, intro: "Se realizan sobre la primera ranura a inspeccionar, antes de iniciar la secuencia completa.", pasos: [
    ["recon", "Realizar una pasada lenta de reconocimiento con las cámaras para detectar gotas de resina, rebabas, obstáculos o cualquier condición que impida el paso o la adherencia del robot.", `Apartado 2.1 / ${MANUAL}, apartado 4.3`],
    [null, "Registrar la ubicación de los límites de cuñas y de las referencias axiales visibles, para referenciar la posición axial del robot.", "—"],
    ["limite", "Definir la posición máxima de avance axial seguro y los límites de recorrido del robot dentro del núcleo.", `Apartado 2.1 / ${MANUAL}, apartado 4.3`],
    ["wtt_verif", "Realizar verificaciones funcionales del WTT sobre la misma ranura/cuña: detección, repetibilidad y registro correcto.", `${MANUAL}, apartado 5.2`],
    [null, "Calibrar el sistema EL CID: elevar gradualmente la tensión de excitación hasta el valor calculado, verificar la tensión por espira, realizar la medición de falla controlada con la espira auxiliar y el robot, y ajustar la constante del captor (KF).", P2],
    ["foco", "Fijar el foco de las cámaras donde se requiera.", `${MANUAL}, apartado 4.4`],
  ] },

  { id: "ran", titulo: "INSPECCIÓN POR RANURA", ref: `${P2} / ${P3}`, antes: () => [
    nota("Ciclo repetitivo:", ref("los pasos {ciclo_ini} a {ciclo_fin} se repiten para cada ranura a inspeccionar. El paso {reubicar} se ejecuta cuando se alcanza la condición indicada."), F.C.gris),
    espacio(),
  ], pasos: [
    { seccion: "Posicionamiento" },
    ["ciclo_ini", "Posicionar el robot en una posición axial conocida de la ranura, utilizando las cámaras laterales y las referencias físicas del núcleo.", `${MANUAL}, apartado 4.3`],
    ["cero", "Establecer el cero de posición axial en el software antes de iniciar el avance de medición.", `Tabla 2 / ${P3} / ${MANUAL}, apartado 4.3`],
    [null, "Durante todo movimiento del robot, un operador acompaña el cable y las cuerdas de seguridad manteniendo una tensión constante, para evitar atrapamientos y que el robot los pise.", "—"],
    { seccion: "Ensayo EL CID (avance)" },
    ["avance", "Avanzar axialmente a velocidad constante (recomendada: 50 mm/s) registrando el EL CID, sin superar el límite de avance seguro definido en el paso {limite}. Activar las cámaras laterales y monitorearlas junto con las demás para detectar anomalías.", `${P3} / ${MANUAL}, apartado 4.3`],
    [null, "Controlar periódicamente la tensión de excitación mediante la medición del sistema y la espira auxiliar.", P2],
    { seccion: "Ensayo WTT e inspección visual (retroceso)" },
    ["wtt", "Retroceder axialmente registrando el WTT de las cuñas. Durante el retroceso, activar las cámaras inferiores e inspeccionar los canales de ventilación.", `${MANUAL}, apartados 5.3 y 5.4`],
    ["fallas", "Comunicar en forma inmediata toda indicación de falla (EL CID, WTT o visual) al ingeniero de generadores a cargo y al Cliente, para que pueda planificar, si corresponde, la extracción del rotor.", "—"],
    { seccion: "Avance angular" },
    ["ciclo_fin", "Desplazar la rampa a la ranura siguiente, verificar la alineación y repetir desde el paso {ciclo_ini}.", `${MANUAL}, apartado 4.3`],
    ["reubicar", "Antes de que el arrollamiento de excitación quede a menos de 120° de la ranura inspeccionada: detener, desenergizar, reubicar el arrollamiento y verificar nuevamente la excitación.", P2],
  ], despues: () => [
    espacio(),
    p("**Situaciones durante el ensayo.** Ante las siguientes situaciones se debe proceder como se indica:", { keepNext: true }),
    tabla(["Situación", "Acción"], [3800, 5838], [
      ["Detención del robot durante la medición EL CID.", "Retroceder aproximadamente 20 mm antes de reanudar el avance."],
      ["Lectura EL CID anómala o inesperada.", "Repetir la zona afectada y confirmar que la excitación y la posición sean correctas."],
      ["Pérdida de referencia o evento que afecte la calidad del EL CID.", "Descartar los datos de la ranura y repetirla."],
      ["Medición WTT compatible con cuña floja.", "Realizar un barrido adicional con paso menor sobre la zona de la indicación."],
      ["Pérdida de referencia durante el WTT.", "Realizar la medición WTT en una segunda pasada de avance."],
    ]),
  ] },

  { id: "cierre", titulo: "CIERRE: DATOS, DESMONTAJE E INFORME", ref: "—", pasos: [
    ["guardar", "Guardar los datos periódicamente en las PC y en un segundo dispositivo de almacenamiento.", `${MANUAL}, apartado 7`],
    ["revision", "Revisar los datos al finalizar cada sector y al completar el ensayo. Repetir las ranuras o zonas con datos incompletos, ruido, pérdida de posición o anomalías.", "—"],
    ["post", "Al retirar el robot del entrehierro, realizar la verificación post-ensayo y confirmar en el checklist que las cantidades verificadas coinciden con las esperadas. Ante cualquier faltante, informar al Cliente y no devolver la máquina hasta recuperar la pieza.", `${CHECKLIST} (Post-Test)`],
    [null, "Desmontar el robot, la rampa, el tablero EL CID, el control box, el tablero de excitación, el Variac, el arrollamiento de excitación, la espira auxiliar, las barreras y la cartelería. Limpiar el área y cerrar los permisos.", "Permiso de trabajo"],
    [null, "Emitir el informe de resultados para revisión de Ingeniería, incluyendo: parámetros de excitación, convenciones de referencia, trazabilidad de ranuras, datos EL CID, datos WTT, indicaciones visuales y zonas repetidas.", "—"],
  ] },
];

// Numeración de etapas (apartados 2.4…) y pasos.
const PRIMER_APARTADO = 4;
const num = {};
let n = 0;
etapas.forEach((e, i) => {
  e.apartado = `2.${PRIMER_APARTADO + i}`;
  e.desde = n + 1;
  e.pasos.forEach((ps) => { if (!ps.seccion) { n += 1; if (ps[0]) num[ps[0]] = n; ps.n = n; } });
  e.hasta = n;
});
const ref = (t) => t.replace(/\{(\w+)\}/g, (_, id) => {
  if (!(id in num)) throw new Error(`Referencia a paso inexistente: ${id}`);
  return String(num[id]);
});
const oracion = (t) => (t.charAt(0) + t.slice(1).toLowerCase())
  .replace(/\bgris\b/g, "GRIS").replace(/\bel cid\b/g, "EL CID").replace(/\bwtt\b/g, "WTT");
const filasPasos = (e) => e.pasos.map((ps) => (ps.seccion ? ps : [String(ps.n), ref(ps[1]), ref(ps[2])]));

// ---------------------------------------------------------------------------
const cuerpo = [
  h1("1. DEFINICIONES"),
  tabla(["Término", "Significado"], [1700, 7938], [
    ["**GRIS**", "Sistema de inspección robotizada de Mecanálisis para el entrehierro de generadores: robot, rampa, control box y software."],
    ["**Rampa**", "Dispositivo de posicionamiento tangencial (TPD, Tangential Positioning Device). Ubica el robot sobre la ranura a inspeccionar y permite el avance angular entre ranuras."],
    ["**Control box**", "Caja de control que alimenta y comanda el robot."],
    ["**Tablero EL CID**", "Unidad de adquisición del ensayo EL CID (DAQ), con entradas de captor, posición axial y corriente de excitación."],
    ["**EL CID**", "Ensayo de detección electromagnética de imperfecciones del núcleo (Electromagnetic Core Imperfection Detection). Se realiza excitando el núcleo a un flujo reducido y midiendo con captor Chattock."],
    ["**WTT**", "Ensayo de ajuste de cuñas (Wedge Tightness Test). Verifica el ajuste e integridad de las cuñas del estator."],
    ["**Captor Chattock**", "Sensor magnético de dos bobinas montado en el robot que mide la corriente de falla Iq."],
    ["**Espira auxiliar**", "Conductor alojado en una ranura que permite medir la tensión por espira y generar la falla controlada de calibración."],
    ["**Variac**", "Fuente de CA de tensión variable que alimenta el circuito de excitación."],
    ["**Tablero de excitación**", "Tablero donde se conectan en serie los hilos del cable de excitación y el circuito de la espira auxiliar."],
    ["**ELCSoft**", "Software de adquisición y visualización del ensayo EL CID."],
    ["**Gota de resina**", "Protuberancia de resina sobre la superficie del estator (resin drip) que puede dificultar el paso o la adherencia del robot."],
    ["**ATS**", "Análisis de Trabajo Seguro."],
    ["**PMS**", "Punto muerto superior (Top Dead Centre, TDC)."],
    ["**DE / NDE**", "Drive End / Non-Drive End: lado acople / lado opuesto al acople del generador."],
    ["**Chicote (punta)**", "Extremo libre de la cuerda de seguridad, con el que se hace el nudo."],
    ["**Firme (cuerda principal)**", "Parte de la cuerda de seguridad que va desde el nudo hacia el operador."],
  ]),

  h1("2. CONTENIDO"),
  h2("2.1 RIESGOS PRINCIPALES"),
  p("Antes de iniciar el trabajo, todo el personal debe conocer los siguientes riesgos, que pueden ocasionar accidentes o incidentes, y las medidas de este procedimiento que los controlan. Los riesgos propios de la inspección robotizada se toman de la Tabla 4-4 del informe EPRI 3002013612 (2018), «Generator Robotic Inspection and Test Guidelines», en lo que aplica al sistema GRIS:"),
  tabla(["Riesgo", "Consecuencia posible", "Control"], [3500, 2900, 3238], [
    ["Pérdida de adherencia del robot al pasar sobre una gota de resina de gran altura, en especial en la parte superior del estator.", "Caída del robot dentro del entrehierro; daño al robot o a la máquina.", `Pasada de reconocimiento (paso ${num.recon}); cuerdas de seguridad con tensión constante.`],
    ["Salida del robot por el extremo opuesto del núcleo o caída por uno de los extremos del estator.", "Caída del robot; daño al robot o a la máquina.", `Límite de avance axial seguro (paso ${num.limite}); cuerdas de seguridad.`],
    ["Robot atascado en el entrehierro (gota de resina, pérdida de energía o falla del robot).", "Demora de la parada; en el peor caso, abrir el otro extremo del generador.", `Recuperación con las cuerdas de seguridad (paso ${num.cuerdas}).`],
    ["Desprendimiento de piezas del robot dentro del generador.", "Pieza suelta dentro de la máquina; daño a sus componentes si se pone en servicio.", `Riesgo residual evaluado en ${RIESGO} (todas las posiciones: bajo o muy bajo). Verificación pre y post-ensayo con ${CHECKLIST} (pasos ${num.check} y ${num.post}).`],
    ["Falla del robot durante el ensayo.", "Demora de la inspección.", "Kit de repuestos GRIS completo (Tabla 1)."],
    ["Fatiga del operador.", "Error de operación: caída del robot, salida por el extremo o datos erróneos.", `Al menos dos operadores calificados y pausas regulares (paso ${num.operadores}).`],
    ["Tablero de excitación en desarrollo; ficha del Variac con contactos macho expuestos.", "Choque eléctrico.", `No operar ni manipular el tablero con tensión; conectar el Variac a la red solo con la ficha ya conectada (paso ${num.variac}).`],
    ["Riesgo eléctrico: equipos alimentados en 220 V CA y arrollamiento de excitación energizado.", "Choque eléctrico.", "Protección diferencial; desenergizar en pausas e intervenciones; puesta a tierra única."],
    ["Manipulación de la rampa con esfuerzos elevados en posiciones incómodas.", "Golpes, caídas y cortes.", "EPP; rieles limados y sin rebabas."],
  ]),

  h2("2.2 DOCUMENTOS ASOCIADOS"),
  p("Este procedimiento establece la secuencia general de la inspección y remite a los siguientes documentos para el detalle técnico:"),
  tabla(["Documento", "Contenido"], [3800, 5838], [
    [`${ANEXO} – Protocolos de ensayo EL CID`, "Protocolo 1: excitación del núcleo. Protocolo 2: calibración. Protocolo 3: operación de ELCSoft."],
    [`${MANUAL} – Manual de uso del software GRIS`, "Operación del software GRIS: configuración del robot y de la rampa, movimiento, cámaras, ensayo de ajuste de cuñas (WTT) y almacenamiento de los datos."],
    [`${RIESGO} – Residual Part Detachment Risk Assessment`, "Evaluación del riesgo residual de desprendimiento de 22 posiciones del robot GRIS."],
    [`${CHECKLIST} – Inspection Detachment Checklist`, "Verificación pre y post-ensayo de las 22 posiciones evaluadas."],
  ]),

  h2("2.3 SECUENCIA GENERAL Y EQUIPAMIENTO"),
  p("La inspección se desarrolla en las etapas indicadas a continuación. Los pasos se numeran en forma correlativa y deben ejecutarse en el orden establecido."),
  tabla(["Etapa", "Pasos", "Documento de referencia"], [4638, 1400, 3600],
    etapas.map((e) => [`${e.apartado} ${oracion(e.titulo)}`, `${e.desde} – ${e.hasta}`, e.ref]),
    { centrar: [1] }),
  espacio(),
  p("**Tabla 1: Equipamiento.**", { keepNext: true }),
  tabla(["Equipo", "Función / observaciones"], [3600, 6038], [
    { seccion: "Sistema GRIS" },
    ["Robot de inspección GRIS", "Desplazamiento axial dentro del entrehierro. Porta las cámaras inferiores y laterales, el captor Chattock y el detector WTT."],
    ["Rampa: rieles, kit de resortes y extensores", "Posicionamiento del robot sobre la ranura y avance angular entre ranuras."],
    ["Kit de guías centrales", "Guiado del robot en la ranura según su geometría."],
    ["Control box y cable principal GRIS", "Alimentación y control del robot."],
    ["Cuerdas de seguridad (3 mm)", "Retención del robot ante pérdida de adherencia o caída."],
    ["Kit de repuestos GRIS", "Reemplazo de componentes en sitio."],
    { seccion: "Ensayo EL CID y WTT" },
    ["Tablero EL CID y captor Chattock", `Medición de la corriente de falla Iq. Características técnicas en ${P1}.`],
    ["Variac", "Alimentación del circuito de excitación (salida 0–250 V)."],
    ["Tablero de excitación", `Bornera EXCITATION para conectar en serie los hilos del cable de excitación y salida de la corriente de magnetización al tablero EL CID; bornera AUXILIAR con resistencias de calibración, llave del circuito y fichas banana para medir la tensión por espira (${P2}).`],
    ["Cable de excitación", "Espiras de excitación del núcleo, conectadas en serie en el tablero de excitación."],
    ["Cable de espira auxiliar", "Medición de la tensión por espira y calibración."],
    ["Cable de puesta a tierra (verde/amarillo)", `Puesta a tierra única desde el estator (${P1}).`],
    ["Detector WTT y bloque de calibración", "Verificación del ajuste de cuñas."],
    { seccion: "Instrumentos" },
    ["Multímetro y pinza amperométrica (UNI-T)", "Medición de la tensión por espira (fichas banana del tablero de excitación) y de la corriente en la espira auxiliar."],
    ["Inclinómetro digital", "Posicionamiento de la rampa."],
    ["Calibre y cinta métrica", "Medición de los parámetros geométricos de la máquina."],
    { seccion: "Informática y conexiones" },
    ["PC GRIS", "Control del robot (software GRIS), conectada al control box por USB y Ethernet."],
    ["PC EL CID", "Adquisición del ensayo EL CID (ELCSoft), conectada al tablero EL CID por USB."],
    ["Cables USB, Ethernet, BNC y de alimentación; regletas de enchufes y adaptadores", "Interconexión y alimentación de los equipos según el esquema de conexiones."],
    { seccion: "Consumibles y herramientas" },
    ["Cintas: duct tape, de papel y de poliimida; marcadores de pintura; precintos; pasacables", "Protección de la rampa, identificación de ranuras y tendido de cables."],
    ["Herramientas de mano", "Juego de llaves Allen y fijas, destornilladores, pinzas, alicates, cutter, sierra, limas, soldador y tubos termocontraíbles."],
    ["Linterna y linterna frontal", "Iluminación del entrehierro y de los extremos del estator."],
  ]),

  ...etapas.flatMap((e) => [
    h2(`${e.apartado} ${e.titulo}`),
    ...(e.intro ? [p(e.intro)] : []),
    ...(e.antes ? e.antes() : []),
    pasos(filasPasos(e)),
    ...(e.despues ? e.despues() : []),
  ]),

  h1("3. REGISTROS"),
  p("Los registros generados como consecuencia de las acciones involucradas en el documento son:", { keepNext: true }),
];

module.exports = { meta, cuerpo, num, etapas };
