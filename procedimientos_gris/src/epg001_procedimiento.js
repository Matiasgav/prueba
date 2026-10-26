// 00503-00-EPG001 — Procedimiento de inspección robotizada GRIS (visual, EL CID y WTT).
const { AlignmentType } = require("docx");
const F = require("./formato_mecanalisis");
const { p, vineta, h1, h2, rol, nota, espacio, tabla, pasos } = F;

const ANEXO = "00503-00-EPG002";
const P1 = `${ANEXO} – Protocolo 1`;
const P2 = `${ANEXO} – Protocolo 2`;
const P3 = `${ANEXO} – Protocolo 3`;

const meta = {
  codigo: "00503-00-EPG001",
  version: "00",
  fecha: "26/10/2026",
  tipo: "PROCEDIMIENTO",
  tituloEncabezado: ["INSPECCIÓN ROBOTIZADA GRIS", "ENSAYOS EL CID Y WTT EN ENTREHIERRO"],
  tituloPortada: ["INSPECCIÓN ROBOTIZADA GRIS", "Inspección visual, EL CID y WTT en el entrehierro"],
  objetivo: "Establecer la metodología para ejecutar la inspección robotizada del entrehierro de generadores de rotor cilíndrico mediante el sistema GRIS, asegurando la seguridad del personal y del equipo, la calidad de los datos adquiridos y la trazabilidad de los resultados.",
  alcance: [
    "Aplica a la inspección robotizada en el entrehierro de generadores de rotor cilíndrico, con el rotor colocado, que comprende una o más de las siguientes tareas, según lo acordado en el servicio:",
    "**a)** Inspección visual del estator (ranuras, cuñas y canales de ventilación).",
    "**b)** Ensayo EL CID del núcleo estatórico.",
    "**c)** Ensayo WTT de ajuste de cuñas del estator.",
  ],
  responsable: "Gerente de Operaciones e Ingeniería.",
  listasNumeradas: [],
  registros: [
    ["A asignar", "Checklist de prevención de desprendimiento de partes"],
    ["A asignar", "Registro de calibración EL CID"],
    ["SIG / Cliente", "ATS – Análisis de Trabajo Seguro y permisos de trabajo"],
    ["—", "Archivos de ensayo ELCSoft (parámetros, Iq, Iqp, reg), registros WTT y fotografías"],
    ["FO-OEI-004", "Informe (Informe de ensayos del generador, código #####-##-EIG###)"],
    ["—", "Registro de toma de conocimiento del personal (apartado 3.11)"],
  ],
  revisiones: [["N° 00", "26/10/2026", "Versión inicial. Reemplaza al documento 00503-00-ZPL001 (Method Statement)."]],
  firmas: ["", "", "", ""],
  referencias: [
    "Norma ISO 9001:2015",
    `${ANEXO} – Protocolos de ensayo EL CID (excitación, calibración y software ELCSoft)`,
    "PR-OEI-027 – Codificación documentación de Operaciones e Ingeniería",
    "CP-OEI-001 – Planificación de proyectos / CP-OEI-003 – Ejecución del proyecto",
    "IEEE Std 56-2016 – Guide for Insulation Maintenance of Electric Machines",
  ],
};

const cuerpo = [
  // 1 ------------------------------------------------------------------
  h1("1. DEFINICIONES"),
  tabla(["Término", "Significado"], [1700, 7938], [
    ["**GRIS**", "Sistema de inspección robotizada de Mecanálisis para el entrehierro de generadores: robot, TPD, caja de control y software."],
    ["**TPD**", "Dispositivo de posicionamiento tangencial (Tangential Positioning Device). Ubica el robot sobre la ranura a inspeccionar y permite el avance angular entre ranuras."],
    ["**EL CID**", "Ensayo de detección electromagnética de imperfecciones del núcleo (Electromagnetic Core Imperfection Detection). Se realiza excitando el núcleo a un flujo reducido y midiendo con captor Chattock."],
    ["**WTT**", "Ensayo de ajuste de cuñas (Wedge Tightness Test). Verifica el ajuste e integridad de las cuñas del estator."],
    ["**ATS**", "Análisis de Trabajo Seguro."],
    ["**Captor Chattock**", "Sensor magnético de dos bobinas montado en el robot que mide la corriente de falla Iq."],
    ["**Espira auxiliar**", "Conductor alojado en una ranura que permite medir la tensión por espira y generar la falla controlada de calibración."],
    ["**Variac**", "Fuente de CA de tensión variable que alimenta el arrollamiento de excitación."],
    ["**ELCSoft**", "Software de adquisición y visualización del ensayo EL CID."],
    ["**PMS**", "Punto muerto superior (Top Dead Centre, TDC)."],
    ["**LA / LOA**", "Lado acople / lado opuesto al acople del generador."],
    ["**PM / IG / RE / OP**", "Administrador del Proyecto / Ingeniero de Generadores / Responsable del Ensayo / Operador técnico (ver apartado 2)."],
  ]),

  // 2 ------------------------------------------------------------------
  h1("2. RESPONSABILIDADES"),
  rol("Gerencia de Operaciones e Ingeniería"),
  vineta("Hacer cumplir el presente procedimiento, asignar el personal calificado y aprobar sus revisiones."),
  rol("Administrador del Proyecto (PM)"),
  vineta("Acordar con el Cliente los ensayos a realizar y gestionar la información de la máquina y los permisos de acceso."),
  vineta("Coordinar la logística de equipos según CP-OEI-001."),
  rol("Ingeniero de Generadores (IG)"),
  vineta("Calcular o aprobar la excitación del núcleo y validar la calibración EL CID."),
  vineta("Recibir y evaluar las indicaciones de falla comunicadas durante el ensayo."),
  vineta("Revisar y aprobar el informe de resultados."),
  rol("Responsable del Ensayo (RE)"),
  vineta("Dirigir la ejecución en sitio conforme a este procedimiento y a los protocolos de " + ANEXO + "."),
  vineta("Gestionar el ATS y los permisos, y verificar que el personal haya firmado la toma de conocimiento."),
  vineta("Asegurar la calidad, el respaldo y la trazabilidad de los datos, y elaborar el informe."),
  rol("Operadores técnicos (OP)"),
  vineta("Montar, operar y desmontar el sistema GRIS y la excitación según las instrucciones del RE."),
  vineta("Acompañar el cable y las cuerdas de seguridad durante todo movimiento del robot."),
  rol("Cliente (CL)"),
  vineta("Entregar la máquina aislada y bloqueada, verificar la ausencia de tensión y proveer los datos técnicos y la convención de numeración de ranuras."),

  // 3 ------------------------------------------------------------------
  h1("3. CONTENIDO"),
  h2("3.1 SECUENCIA GENERAL"),
  p("La inspección se desarrolla en las etapas indicadas a continuación. Los pasos se numeran en forma correlativa y deben ejecutarse en el orden establecido."),
  tabla(["Etapa", "Pasos", "Documento de referencia"], [4638, 1400, 3600], [
    ["3.3 Seguridad y permisos", "1 – 4", "ATS / requisitos del Cliente"],
    ["3.4 Preparación técnica previa", "5 – 8", `${P1}`],
    ["3.5 Preparación del área y del estator", "9 – 13", "—"],
    ["3.6 Montaje de la excitación del núcleo", "14 – 19", `${P1}`],
    ["3.7 Configuración y montaje del sistema GRIS", "20 – 29", `${P3}`],
    ["3.8 Reconocimiento y calibración", "30 – 35", `${P2}`],
    ["3.9 Inspección por ranura (ciclo repetitivo)", "36 – 45", `${P3}`],
    ["3.10 Cierre: datos, desmontaje e informe", "46 – 49", "FO-OEI-004"],
  ], { centrar: [1] }),

  h2("3.2 EQUIPAMIENTO"),
  tabla(["Equipo", "Función"], [3600, 6038], [
    ["Robot de inspección GRIS", "Desplazamiento axial dentro del entrehierro. Porta las cámaras inferiores y laterales, el captor Chattock y el detector WTT."],
    ["Dispositivo de posicionamiento tangencial (TPD)", "Posicionamiento del robot sobre la ranura y avance angular entre ranuras."],
    ["Caja de control GRIS", "Alimentación y control del robot y del TPD."],
    ["Unidad de adquisición EL CID (DAQ), captor Chattock y espira auxiliar", `Medición de la corriente de falla Iq y de la tensión por espira. Características técnicas en ${P1}.`],
    ["Variac y cable del arrollamiento de excitación", "Excitación del núcleo estatórico."],
    ["Detector WTT y bloque de calibración", "Verificación del ajuste de cuñas."],
    ["PC portátil con software GRIS y ELCSoft", "Control del sistema, adquisición y almacenamiento de datos."],
    ["Dispositivo de almacenamiento externo", "Respaldo de datos."],
    ["Accesorios", "Soportes provisorios para cables, cinta (duct tape), cuerdas/eslingas de seguridad, cinta de identificación, barreras y cartelería."],
  ]),

  h2("3.3 SEGURIDAD Y PERMISOS"),
  pasos([
    ["1", "Asistir a la inducción de seguridad del sitio y revisar la evaluación de riesgos del Cliente.", "RE / OP", "Requisitos del Cliente"],
    ["2", "Obtener el permiso de trabajo y el permiso de aislamiento/bloqueo. El Cliente debe verificar la ausencia de tensión antes de iniciar cualquier tarea.", "RE / CL", "Permiso de trabajo"],
    ["3", "Confeccionar el ATS y revisarlo con todo el personal involucrado. Utilizar como mínimo el EPP especificado y el adicional que requieran las condiciones del sitio.", "RE", "ATS"],
    ["4", "Vallar el área de trabajo y colocar carteles que indiquen «Ensayo eléctrico en curso».", "OP", "—"],
  ]),
  espacio(),
  nota("Reglas permanentes:", "desenergizar el arrollamiento de excitación durante pausas, descansos y ante cualquier intervención mecánica sobre el sistema. Respetar el esquema de puesta a tierra única definido en " + P1 + "."),

  h2("3.4 PREPARACIÓN TÉCNICA PREVIA"),
  pasos([
    ["5", "Definir con el Cliente los ensayos a realizar: inspección visual, EL CID y/o WTT.", "PM / IG", "Alcance del servicio"],
    ["6", "Obtener los datos de la máquina: número de serie, datos de placa, dimensiones principales, número de ranuras, longitud axial del núcleo, diámetro y entrehierro disponibles, convención de numeración de ranuras y datos para el cálculo de la excitación.", "PM / CL", `${P1}, Apéndice`],
    ["7", "Calcular la excitación del núcleo (tensión por espira, número de espiras, corriente y sección del conductor) o solicitarla a Ingeniería.", "IG", `${P1}`],
    ["8", "Confirmar la disponibilidad de alimentación para PC, DAQ EL CID, caja de control GRIS, TPD y Variac. Verificar la protección diferencial.", "RE", "—"],
  ]),

  h2("3.5 PREPARACIÓN DEL ÁREA Y DEL ESTATOR"),
  pasos([
    ["9", "Preparar un área de trabajo despejada o un banco en un extremo del generador, con visibilidad de la pantalla del sistema desde el interior del estator o desde el puesto de operación.", "OP", "—"],
    ["10", "Verificar que al menos un extremo del rotor esté aislado de tierra.", "RE / CL", `${P1}`],
    ["11", "Definir con el Cliente la ranura 1 y el sentido de numeración. Si no existe convención, tomar como referencia el PMS y numerar en sentido horario visto desde el LA.", "RE / CL", "—"],
    ["12", "Identificar las ranuras con cinta o marcas visibles, como mínimo cada cinco ranuras. Reforzar la identificación en la ranura inicial, en las ranuras de control y en los sectores de cambio de excitación.", "OP", "—"],
    ["13", "Verificar que el entrehierro esté libre de objetos metálicos, suciedad, elementos sueltos, gotas, obstáculos o interferencias mecánicas, y que no existan lazos conductores cerrados alrededor del núcleo.", "OP", `${P2}`],
  ]),

  h2("3.6 MONTAJE DE LA EXCITACIÓN DEL NÚCLEO"),
  pasos([
    ["14", "Instalar soportes provisorios en ambos extremos del estator para guiar y sostener los cables de excitación a través del entrehierro.", "OP", "—"],
    ["15", "Montar el arrollamiento de excitación y el Variac según el cálculo aprobado.", "OP / RE", `${P1}`],
    ["16", "Ubicar inicialmente el arrollamiento a 120° de la primera ranura a inspeccionar, en sentido opuesto al avance angular previsto.", "RE", "—"],
    ["17", "Planificar la reubicación del arrollamiento cada 120° de avance angular, de modo que durante el ensayo nunca quede a menos de 120° de la ranura inspeccionada.", "RE", "Paso 44"],
    ["18", "Instalar la espira auxiliar en la primera ranura a inspeccionar o en la ranura definida por Ingeniería.", "OP", `${P1}`],
    ["19", "Disponer el cable de excitación sobrante extendido o en zigzag, nunca enrollado, para mejorar su refrigeración y reducir la inductancia.", "OP", "—"],
  ]),

  h2("3.7 CONFIGURACIÓN Y MONTAJE DEL SISTEMA GRIS"),
  pasos([
    ["20", "Ingresar en el software GRIS los parámetros geométricos medidos y obtener los valores de ajuste del robot y del TPD.", "RE", "Software GRIS"],
    ["21", "Ajustar el TPD con los valores obtenidos para posicionar tangencialmente el robot sobre la ranura a inspeccionar.", "OP", "—"],
    ["22", "Cortar los rieles del TPD a la longitud requerida. Limar los bordes y eliminar rebabas.", "OP", "—"],
    ["23", "Proteger con cinta (duct tape) las zonas de contacto del TPD con el cuerpo del rotor y, cuando corresponda, el trinquete.", "OP", "—"],
    ["24", "Ajustar las cámaras inferiores, las cámaras laterales y el captor Chattock según la geometría de la ranura y del entrehierro. Instalar las guías centrales adecuadas, dejando una holgura recomendada de 1 a 2 mm.", "OP", "—"],
    ["25", "Conectar la caja de control GRIS, la DAQ EL CID, el TPD, el Variac, la PC y todos los dispositivos de control, adquisición y potencia, respetando el esquema de puesta a tierra.", "OP", `${P1}`],
    ["26", "Instalar las cuerdas/eslingas de seguridad.", "OP", "—"],
    ["27", "Configurar el paso de registro EL CID y los parámetros del ensayo en ELCSoft, el paso de adquisición automática de fotografías y el paso de muestreo WTT.", "RE", `${P3}`],
    ["28", "Completar el checklist de prevención de desprendimiento de partes antes de introducir el robot.", "RE", "Checklist"],
    ["29", "Montar el robot sobre el TPD y verificar que el conjunto ingresa, se posiciona y se desplaza sin interferencias.", "OP", "—"],
  ]),

  h2("3.8 RECONOCIMIENTO Y CALIBRACIÓN"),
  p("Se realizan sobre la primera ranura a inspeccionar, antes de iniciar la secuencia completa."),
  pasos([
    ["30", "Realizar una pasada lenta de reconocimiento con las cámaras para detectar gotas, rebabas, obstáculos o cualquier condición que impida el paso del robot.", "OP", "—"],
    ["31", "Registrar la ubicación de los límites de cuñas y de las referencias axiales visibles, para referenciar la posición axial del robot.", "RE", "—"],
    ["32", "Definir la posición máxima de avance axial seguro y los límites de recorrido del robot dentro del núcleo.", "RE", "—"],
    ["33", "Realizar verificaciones funcionales del WTT sobre la misma ranura/cuña: detección, repetibilidad y registro correcto.", "RE", "—"],
    ["34", "Calibrar el sistema EL CID: elevar gradualmente la tensión de excitación hasta el valor calculado, verificar la tensión por espira, realizar la medición de falla controlada con la espira auxiliar y el robot, y ajustar la constante del captor (KF).", "IG / RE", `${P2} / Registro de calibración`],
    ["35", "Fijar el foco de las cámaras donde se requiera.", "OP", "—"],
  ]),

  h2("3.9 INSPECCIÓN POR RANURA"),
  nota("Ciclo repetitivo:", "los pasos 36 a 43 se repiten para cada ranura a inspeccionar. Los pasos 44 y 45 se ejecutan cuando se alcanza la condición indicada.", F.C.gris),
  espacio(),
  pasos([
    { seccion: "Posicionamiento" },
    ["36", "Posicionar el robot en una posición axial conocida de la ranura, utilizando las cámaras laterales y las referencias físicas del núcleo.", "OP", "—"],
    ["37", "Establecer el cero de posición axial en el software antes de iniciar el avance de medición.", "RE", `${P3}`],
    ["38", "Durante todo movimiento del robot, un operador acompaña el cable y las cuerdas de seguridad para evitar atrapamientos.", "OP", "—"],
    { seccion: "Ensayo EL CID (avance)" },
    ["39", "Avanzar axialmente a velocidad constante registrando el EL CID. Activar las cámaras laterales y monitorearlas junto con las demás para detectar anomalías.", "RE / OP", `${P3}`],
    ["40", "Controlar periódicamente la tensión de excitación mediante la medición del sistema y la espira auxiliar.", "RE", `${P2}`],
    { seccion: "Ensayo WTT e inspección visual (retroceso)" },
    ["41", "Retroceder axialmente registrando el WTT de las cuñas. Durante el retroceso, activar las cámaras inferiores e inspeccionar los canales de ventilación.", "RE / OP", "—"],
    ["42", "Comunicar toda indicación de falla (EL CID, WTT o visual) al Ingeniero de Generadores.", "RE", "—"],
    { seccion: "Avance angular" },
    ["43", "Desplazar el TPD a la ranura siguiente, verificar la alineación y repetir desde el paso 36.", "OP", "—"],
    ["44", "Antes de que el arrollamiento de excitación quede a menos de 120° de la ranura inspeccionada: detener, desenergizar, reubicar el arrollamiento y verificar nuevamente la excitación.", "RE", `${P2}`],
    ["45", "Cada 10 ranuras, retirar el robot del entrehierro, verificar su estado y completar el checklist de prevención de desprendimiento de partes.", "OP / RE", "Checklist"],
  ]),
  espacio(),
  p("**Situaciones durante el ensayo.** Ante las siguientes situaciones se debe proceder como se indica:", { keepNext: true }),
  tabla(["Situación", "Acción"], [3800, 5838], [
    ["Detención del robot durante la medición EL CID.", "Retroceder aproximadamente 20 mm antes de reanudar el avance."],
    ["Lectura EL CID anómala o inesperada.", "Repetir la zona afectada y confirmar que la excitación y la posición sean correctas."],
    ["Pérdida de referencia o evento que afecte la calidad del EL CID.", "Descartar los datos de la ranura y repetirla."],
    ["Medición WTT compatible con cuña floja.", "Realizar un barrido adicional con paso menor sobre la zona de la indicación."],
    ["Pérdida de referencia durante el WTT.", "Realizar la medición WTT en una segunda pasada de avance."],
  ]),

  h2("3.10 CIERRE: DATOS, DESMONTAJE E INFORME"),
  pasos([
    ["46", "Guardar los datos periódicamente en la PC y en un segundo dispositivo de almacenamiento.", "RE", "Archivos de ensayo"],
    ["47", "Revisar los datos al finalizar cada sector y al completar el ensayo. Repetir las ranuras o zonas con datos incompletos, ruido, pérdida de posición o anomalías.", "RE / IG", "—"],
    ["48", "Desmontar el robot, el TPD, la DAQ EL CID, la caja de control, el Variac, el arrollamiento de excitación, la espira auxiliar, las barreras y la cartelería. Limpiar el área y cerrar los permisos.", "OP / RE", "Permiso de trabajo"],
    ["49", "Emitir el informe de resultados para revisión de Ingeniería, incluyendo: parámetros de excitación, trazabilidad de ranuras, datos EL CID, datos WTT, indicaciones visuales y zonas repetidas.", "RE / IG", "FO-OEI-004"],
  ]),

  F.saltoPagina(),
  h2("3.11 TOMA DE CONOCIMIENTO DEL PERSONAL"),
  p("Los abajo firmantes declaran haber leído y comprendido el presente procedimiento y se comprometen a cumplirlo."),
  tabla(["Nombre y apellido", "Función", "Firma", "Fecha"], [3200, 2400, 2438, 1600],
    Array.from({ length: 6 }, () => [" ", " ", " ", " "])),

  h1("4. REGISTROS"),
  p("Los registros generados como consecuencia de las acciones involucradas en el documento son:"),
];

module.exports = { meta, cuerpo };
