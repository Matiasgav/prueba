// 00503-00-EPG001 — Procedimiento general de inspección robotizada GRIS (visual, EL CID y WTT).
// Los pasos se numeran automáticamente; las referencias cruzadas usan {id} → número de paso.
const F = require("./formato_mecanalisis");
const { p, h1, h2, nota, espacio, tabla, pasos } = F;

const ANEXO = "00503-00-EPG002";
const P1 = `${ANEXO} – Protocolo 1`;
const P2 = `${ANEXO} – Protocolo 2`;
const P3 = `${ANEXO} – Protocolo 3`;
const CHECKLIST = "00503-00-ZRQ001";
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
  firmas: ["", "", "", ""],
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
    [null, "Obtener los datos de la máquina: número de serie, datos de placa, dimensiones principales, número de ranuras, longitud axial del núcleo, diámetro y entrehierro disponibles, y datos para el cálculo de la excitación.", `${P1}, Apéndice`],
    [null, "Calcular la excitación del núcleo (tensión por espira, número de espiras, corriente y sección del conductor) o solicitarla a Ingeniería.", P1],
    [null, "Confirmar la disponibilidad de alimentación para la PC, el tablero EL CID, el control box, la rampa y el Variac. Verificar la protección diferencial.", "—"],
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
    [null, "Montar el arrollamiento de excitación y el Variac según el cálculo aprobado.", P1],
    [null, "Ubicar inicialmente el arrollamiento a 120° de la primera ranura a inspeccionar, en sentido opuesto al avance angular previsto.", "—"],
    [null, "Planificar la reubicación del arrollamiento cada 120° de avance angular, de modo que durante el ensayo nunca quede a menos de 120° de la ranura inspeccionada.", "Paso {reubicar}"],
    [null, "Instalar la espira auxiliar en la primera ranura a inspeccionar o en la ranura definida por Ingeniería.", P1],
  ] },

  { id: "conf", titulo: "CONFIGURACIÓN Y MONTAJE DEL SISTEMA GRIS", ref: `${P3} / Manual de software GRIS / Figura 1`, intro: "Las conexiones se realizan según el esquema general de la Figura 1.", pasos: [
    [null, "Ingresar en el software GRIS los parámetros geométricos medidos y obtener los valores de ajuste del robot y de la rampa.", "Manual de software GRIS"],
    [null, "Cortar los rieles de la rampa a la longitud requerida. Limar los bordes y eliminar rebabas.", "—"],
    [null, "Ajustar la rampa con los valores obtenidos para posicionar tangencialmente el robot sobre la ranura a inspeccionar.", "—"],
    [null, "Proteger con cinta (duct tape) las zonas de contacto de la rampa con el cuerpo del rotor y, cuando corresponda, el trinquete.", "—"],
    [null, "Ajustar las cámaras inferiores, las cámaras laterales y el captor Chattock según la geometría de la ranura y del entrehierro. Instalar las guías centrales adecuadas, dejando una holgura recomendada de 1 a 2 mm.", "—"],
    [null, "Conectar el control box, el tablero EL CID, la rampa, el Variac, la PC y todos los dispositivos de control, adquisición y potencia, respetando el esquema de puesta a tierra.", `${ESQUEMA} / ${P1}`],
    [null, "Instalar las cuerdas de seguridad del robot.", "—"],
    [null, "Configurar en ELCSoft los parámetros del ensayo y el paso de registro EL CID (recomendado: 7 mm). Configurar el paso de adquisición automática de fotografías y el paso de muestreo WTT.", `${P3} / Manual de software GRIS`],
    ["check", "Realizar la verificación pre-ensayo de desprendimiento de piezas del robot y registrarla en el checklist antes de introducir el robot.", `${CHECKLIST} (Pre-Test)`],
    [null, "Montar el robot sobre la rampa y verificar que el conjunto ingresa, se posiciona y se desplaza sin interferencias.", "—"],
  ], despues: () => [
    F.saltoPagina(),
    ...F.figura("esquema_general_vertical.png", 2200, 3200, "Figura 1: Esquema general de conexiones del sistema GRIS (líneas a trazos: conexiones a confirmar)", 15.2),
  ] },

  { id: "cal", titulo: "RECONOCIMIENTO Y CALIBRACIÓN", ref: P2, intro: "Se realizan sobre la primera ranura a inspeccionar, antes de iniciar la secuencia completa.", pasos: [
    ["recon", "Realizar una pasada lenta de reconocimiento con las cámaras para detectar gotas de resina, rebabas, obstáculos o cualquier condición que impida el paso o la adherencia del robot.", "Apartado 2.1"],
    [null, "Registrar la ubicación de los límites de cuñas y de las referencias axiales visibles, para referenciar la posición axial del robot.", "—"],
    ["limite", "Definir la posición máxima de avance axial seguro y los límites de recorrido del robot dentro del núcleo.", "Apartado 2.1"],
    [null, "Realizar verificaciones funcionales del WTT sobre la misma ranura/cuña: detección, repetibilidad y registro correcto.", "—"],
    [null, "Calibrar el sistema EL CID: elevar gradualmente la tensión de excitación hasta el valor calculado, verificar la tensión por espira, realizar la medición de falla controlada con la espira auxiliar y el robot, y ajustar la constante del captor (KF).", P2],
    [null, "Fijar el foco de las cámaras donde se requiera.", "—"],
  ] },

  { id: "ran", titulo: "INSPECCIÓN POR RANURA", ref: `${P2} / ${P3}`, antes: () => [
    nota("Ciclo repetitivo:", ref("los pasos {ciclo_ini} a {ciclo_fin} se repiten para cada ranura a inspeccionar. El paso {reubicar} se ejecuta cuando se alcanza la condición indicada."), F.C.gris),
    espacio(),
  ], pasos: [
    { seccion: "Posicionamiento" },
    ["ciclo_ini", "Posicionar el robot en una posición axial conocida de la ranura, utilizando las cámaras laterales y las referencias físicas del núcleo.", "—"],
    [null, "Establecer el cero de posición axial en el software antes de iniciar el avance de medición.", `Tabla 2 / ${P3}`],
    [null, "Durante todo movimiento del robot, un operador acompaña el cable y las cuerdas de seguridad manteniendo una tensión constante, para evitar atrapamientos y que el robot los pise.", "—"],
    { seccion: "Ensayo EL CID (avance)" },
    [null, "Avanzar axialmente a velocidad constante (recomendada: 50 mm/s) registrando el EL CID, sin superar el límite de avance seguro definido en el paso {limite}. Activar las cámaras laterales y monitorearlas junto con las demás para detectar anomalías.", P3],
    [null, "Controlar periódicamente la tensión de excitación mediante la medición del sistema y la espira auxiliar.", P2],
    { seccion: "Ensayo WTT e inspección visual (retroceso)" },
    [null, "Retroceder axialmente registrando el WTT de las cuñas. Durante el retroceso, activar las cámaras inferiores e inspeccionar los canales de ventilación.", "—"],
    [null, "Comunicar toda indicación de falla (EL CID, WTT o visual) al ingeniero de generadores a cargo.", "—"],
    { seccion: "Avance angular" },
    ["ciclo_fin", "Desplazar la rampa a la ranura siguiente, verificar la alineación y repetir desde el paso {ciclo_ini}.", "—"],
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
    [null, "Guardar los datos periódicamente en la PC y en un segundo dispositivo de almacenamiento.", "—"],
    [null, "Revisar los datos al finalizar cada sector y al completar el ensayo. Repetir las ranuras o zonas con datos incompletos, ruido, pérdida de posición o anomalías.", "—"],
    ["post", "Al retirar el robot del entrehierro, realizar la verificación post-ensayo y confirmar en el checklist que las cantidades verificadas coinciden con las esperadas. Ante cualquier faltante, informar al Cliente y no devolver la máquina hasta recuperar la pieza.", `${CHECKLIST} (Post-Test)`],
    [null, "Desmontar el robot, la rampa, el tablero EL CID, el control box, el Variac, el arrollamiento de excitación, la espira auxiliar, las barreras y la cartelería. Limpiar el área y cerrar los permisos.", "Permiso de trabajo"],
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
    ["**Control box**", "Caja de control que alimenta y comanda el robot y la rampa."],
    ["**Tablero EL CID**", "Unidad de adquisición del ensayo EL CID (DAQ), con entradas de captor, posición axial y corriente de excitación."],
    ["**EL CID**", "Ensayo de detección electromagnética de imperfecciones del núcleo (Electromagnetic Core Imperfection Detection). Se realiza excitando el núcleo a un flujo reducido y midiendo con captor Chattock."],
    ["**WTT**", "Ensayo de ajuste de cuñas (Wedge Tightness Test). Verifica el ajuste e integridad de las cuñas del estator."],
    ["**Captor Chattock**", "Sensor magnético de dos bobinas montado en el robot que mide la corriente de falla Iq."],
    ["**Espira auxiliar**", "Conductor alojado en una ranura que permite medir la tensión por espira y generar la falla controlada de calibración."],
    ["**Variac**", "Fuente de CA de tensión variable que alimenta el arrollamiento de excitación."],
    ["**ELCSoft**", "Software de adquisición y visualización del ensayo EL CID."],
    ["**Gota de resina**", "Protuberancia de resina sobre la superficie del estator (resin drip) que puede dificultar el paso o la adherencia del robot."],
    ["**ATS**", "Análisis de Trabajo Seguro."],
    ["**PMS**", "Punto muerto superior (Top Dead Centre, TDC)."],
    ["**DE / NDE**", "Drive End / Non-Drive End: lado acople / lado opuesto al acople del generador."],
  ]),

  h1("2. CONTENIDO"),
  h2("2.1 RIESGOS PRINCIPALES"),
  p("Antes de iniciar el trabajo, todo el personal debe conocer los siguientes riesgos, que pueden ocasionar accidentes o incidentes, y las medidas de este procedimiento que los controlan:"),
  tabla(["Riesgo", "Consecuencia posible", "Control"], [3500, 2900, 3238], [
    ["Pérdida de adherencia del robot al pasar sobre una gota de resina de gran altura, en especial en la parte superior del estator.", "Caída del robot dentro del entrehierro; daño al robot o a la máquina.", `Pasada de reconocimiento (paso ${num.recon}); cuerdas de seguridad con tensión constante.`],
    ["Salida del robot por el extremo opuesto del núcleo o caída por uno de los extremos del estator.", "Caída del robot; daño al robot o a la máquina.", `Límite de avance axial seguro (paso ${num.limite}); cuerdas de seguridad.`],
    ["Desprendimiento de piezas del robot dentro del generador.", "Pieza suelta dentro de la máquina; daño a sus componentes si se pone en servicio.", `Riesgo residual evaluado en ${RIESGO} (todas las posiciones: bajo o muy bajo). Verificación pre y post-ensayo con ${CHECKLIST} (pasos ${num.check} y ${num.post}).`],
    ["Riesgo eléctrico: equipos alimentados en 220 V CA y arrollamiento de excitación energizado.", "Choque eléctrico.", "Protección diferencial; desenergizar en pausas e intervenciones; puesta a tierra única."],
    ["Manipulación de la rampa con esfuerzos elevados en posiciones incómodas.", "Golpes, caídas y cortes.", "EPP; rieles limados y sin rebabas."],
  ]),

  h2("2.2 DOCUMENTOS ASOCIADOS"),
  p("Este procedimiento establece la secuencia general de la inspección y remite a los siguientes documentos para el detalle técnico:"),
  tabla(["Documento", "Contenido"], [3800, 5838], [
    [`${ANEXO} – Protocolos de ensayo EL CID`, "Protocolo 1: excitación del núcleo. Protocolo 2: calibración. Protocolo 3: operación de ELCSoft."],
    ["Manual de software GRIS", "Operación del software de control del robot y de la rampa."],
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
    ["Control box y cable principal GRIS", "Alimentación y control del robot y de la rampa."],
    ["Cuerdas de seguridad (3 mm)", "Retención del robot ante pérdida de adherencia o caída."],
    ["Kit de repuestos GRIS", "Reemplazo de componentes en sitio."],
    { seccion: "Ensayo EL CID y WTT" },
    ["Tablero EL CID y captor Chattock", `Medición de la corriente de falla Iq. Características técnicas en ${P1}.`],
    ["Variac", "Alimentación del arrollamiento de excitación del núcleo."],
    ["Cable de excitación (50 m)", "Arrollamiento de excitación del núcleo."],
    ["Cable de espira auxiliar", "Medición de la tensión por espira y calibración."],
    ["Kit de calibración", `Resistencias de calibración y cables con fichas banana para la falla controlada (${P2}).`],
    ["Cable de puesta a tierra (verde/amarillo)", `Puesta a tierra única desde el estator (${P1}).`],
    ["Detector WTT y bloque de calibración", "Verificación del ajuste de cuñas."],
    { seccion: "Instrumentos" },
    ["Multímetro y pinza amperométrica", "Control de la tensión por espira y de la corriente de excitación."],
    ["Inclinómetro digital", "Posicionamiento de la rampa."],
    ["Calibre y cinta métrica", "Medición de los parámetros geométricos de la máquina."],
    { seccion: "Informática y conexiones" },
    ["PC portátil con software GRIS y ELCSoft", "Control del sistema, adquisición y almacenamiento de datos."],
    ["Cables USB, Ethernet, BNC y de alimentación; zapatillas y adaptadores de enchufe", "Interconexión y alimentación de los equipos según el esquema de conexiones."],
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
