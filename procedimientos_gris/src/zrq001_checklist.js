// 00503-00-ZRQ001 – GRIS Detachment Inspection Checklist, en el formato Mecanálisis.
// Mismo contenido que el original (en inglés): 22 posiciones, controles pre y post-ensayo y vistas del robot.
const {
  Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, VerticalAlign, ShadingType, BorderStyle,
} = require("docx");
const F = require("./formato_mecanalisis");
const { C } = F;

const meta = {
  codigo: "00503-00-ZRQ001",
  version: "00",
  fecha: "29/10/2026",
  tipo: "CHECKLIST",
  tituloEncabezado: ["GRIS – DETACHMENT INSPECTION CHECKLIST"],
  tituloPortada: ["GRIS – DETACHMENT INSPECTION CHECKLIST", ""],
  formulario: true,
};

// [posición, ítem, modo de desprendimiento, riesgo residual, cantidad esperada, controles]
const POSICIONES = [
  [1, "Cover retaining screw", "Backing out", "Low", 8, ["Torque mark aligned", "Retention tape present and intact", "No visible loosening or backing out"]],
  [2, "Module joining shoulder screw", "Backing out", "Low", 8, ["Torque level verified"]],
  [3, "Extender retaining screw", "Backing out", "Very Low", 6, ["Torque level verified"]],
  [4, "ELCID magnetic sensor fastening screw", "Backing out / Pull-out", "Very Low", 2, ["Torque level verified"]],
  [5, "Motor cover screw", "Backing out / Pull-out", "Low", 8, ["Torque mark aligned", "Retention tape present and intact"]],
  [6, "ELCID magnetic sensor", "Fracture", "Very Low", 2, ["No visible damage or degradation"]],
  [7, "Camera retaining screw", "Backing out / Pull-out", "Low", 10, ["Torque mark aligned"]],
  [8, "Gear cover", "Fracture / Disengagement", "Very Low", 2, ["Fit fully seated", "Retention tape present and intact"]],
  [9, "Track belt", "Derailment", "Very Low", 2, []],
  [10, "Recovery hook", "Backing out / Pull-out", "Very Low", 2, ["Torque mark aligned"]],
  [11, "Wheel axle shoulder screw", "Backing out", "Low", 6, ["Torque mark aligned"]],
  [12, "Main connector housing screw", "Backing out", "Very Low", 2, ["Torque mark aligned", "Retention tape present and intact"]],
  [13, "Main connector latch screw", "Backing out", "Very Low", 2, ["Mechanical retention engaged"]],
  [14, "Bottom camera position locking screw", "Backing out", "Very Low", 2, ["Mechanical retention engaged"]],
  [15, "Central slot guide", "Disengagement", "Very Low", 2, ["Fit fully seated", "No movement or disengagement"]],
  [16, "Leaf spring retaining screw", "Backing out", "Low", 2, ["Torque mark aligned", "No visible loosening or backing out"]],
  [17, "Leaf spring", "Fracture", "Very Low", 1, ["No cracks or permanent deformation"]],
  [18, "Impactor grub screw", "Backing out", "Very Low", 2, ["Retention tape present and intact", "Light torque confirmation"]],
  [19, "Track wheels", "Fracture", "Very Low", 6, ["No visible damage or degradation"]],
  [20, "Magnets retaining screw", "Backing out", "Low", 8, ["Torque mark aligned"]],
  [21, "Impact solenoid", "Detachment", "Very Low", 1, ["Fully seated in mount"]],
  [22, "Camera lens", "Backing out", "Very Low", 6, ["No movement under light torque"]],
];
const RIESGO = { "Low": { fill: "EEF2DC", color: "5B6B1E" }, "Very Low": { fill: "DFF0D8", color: "2E7D32" } };

// Columnas (dxa, suman F.ANCHO): posición, ítem, desprendimiento, riesgo, cantidad, verificada pre,
// control, casilla, observaciones, verificada post.
const ANCHOS = [640, 1880, 1080, 760, 720, 680, 2160, 300, 738, 680];
const linea = { style: BorderStyle.SINGLE, size: 4, color: "A6B4B8" };
const bordes = { top: linea, bottom: linea, left: linea, right: linea };

const parrafo = (texto, o = {}) => new Paragraph({  // "\n" separa renglones
  alignment: o.align || AlignmentType.LEFT, spacing: { before: 0, after: 0, line: 216 },
  children: String(texto).split("\n").map((t, i) => new TextRun({ text: t, break: i ? 1 : 0, size: o.size || 14, bold: o.bold, color: o.color })),
});

function celda(texto, ancho, o = {}) {
  return new TableCell({
    width: { size: ancho, type: WidthType.DXA }, borders: bordes,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 8, bottom: 8, left: 60, right: 60 },
    verticalAlign: VerticalAlign.CENTER, rowSpan: o.rowSpan, columnSpan: o.span,
    children: [parrafo(texto, o)],
  });
}
const cab = (t, i, o = {}) => celda(t, o.ancho || ANCHOS[i], { bold: true, fill: C.grisClaro, align: AlignmentType.CENTER, ...o });

function tablaPosiciones() {
  const filas = [
    new TableRow({ tableHeader: true, cantSplit: true, children: [
      cab("Position", 0), cab("Item", 1), cab("Potential Detachment Concern", 2), cab("Residual risk", 3),
      cab("Expected Qty", 4), cab("Pre-Test\nQty Verified", 5),
      cab("Pre-Test\nAssociated Control / Verification Point", 6, { span: 2, ancho: ANCHOS[6] + ANCHOS[7] }),
      cab("Pre-Test\nRemarks", 8), cab("Post-Test\nQty Verified", 9),
    ] }),
  ];
  for (const [pos, item, modo, riesgo, cant, controles] of POSICIONES) {
    const n = Math.max(controles.length, 1);
    const lista = controles.length ? controles : [""];
    lista.forEach((ctrl, k) => {
      const fijas = k === 0 ? [
        celda(pos, ANCHOS[0], { rowSpan: n, align: AlignmentType.CENTER }),
        celda(item, ANCHOS[1], { rowSpan: n }),
        celda(modo, ANCHOS[2], { rowSpan: n }),
        celda(riesgo, ANCHOS[3], { rowSpan: n, align: AlignmentType.CENTER, bold: true, ...RIESGO[riesgo] }),
        celda(cant, ANCHOS[4], { rowSpan: n, align: AlignmentType.CENTER }),
        celda("", ANCHOS[5], { rowSpan: n }),
      ] : [];
      const finales = k === 0 ? [celda("", ANCHOS[8], { rowSpan: n }), celda("", ANCHOS[9], { rowSpan: n })] : [];
      filas.push(new TableRow({ cantSplit: true, children: [
        ...fijas,
        celda(ctrl, ANCHOS[6]),
        celda(ctrl ? "☐" : "", ANCHOS[7], { align: AlignmentType.CENTER, size: 18 }),
        ...finales,
      ] }));
    });
  }
  return new Table({ width: { size: F.ANCHO, type: WidthType.DXA }, columnWidths: ANCHOS, rows: filas });
}

function bloque(titulo, campos) {
  const a = [2200, F.ANCHO - 2200];
  const filas = [];
  if (titulo) filas.push(new TableRow({ cantSplit: true, children: [cab(titulo, 0, { span: 2, ancho: F.ANCHO })] }));
  for (const c of campos) {
    filas.push(new TableRow({ cantSplit: true, height: { value: 210, rule: "atLeast" }, children: [
      celda(c, a[0], { bold: true, align: AlignmentType.RIGHT, fill: "F7F9F9" }), celda("", a[1]),
    ] }));
  }
  return new Table({ width: { size: F.ANCHO, type: WidthType.DXA }, columnWidths: a, rows: filas });
}

const titulo = (t, nuevaPagina = false) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 }, pageBreakBefore: nuevaPagina,
  children: [new TextRun({ text: t, bold: true, size: 24, color: C.naranja })] });

const sep = () => new Paragraph({ spacing: { before: 0, after: 0 }, children: [new TextRun({ text: "", size: 10 })] });

const cuerpo = [
  titulo("GRIS – Detachment Inspection Checklist"),
  bloque(null, ["Project:", "Unit:", "Remarks:"]),
  sep(),
  tablaPosiciones(),
  sep(),
  bloque("Pre-Test Verification", ["Verified by:", "Signature:", "Date:"]),
  sep(),
  bloque("Post-Test Verification", ["Verified by:", "Signature:", "Date:"]),
  titulo("Position Identification", true),
  ...F.figura("zrq001_vista_superior.png", 660, 480, "Figure 1. Position Identification - GRIS isometric top view", 12),
  ...F.figura("zrq001_vista_inferior.png", 936, 771, "Figure 2. Position Identification - GRIS isometric bottom view", 12),
];

module.exports = { meta, cuerpo };
