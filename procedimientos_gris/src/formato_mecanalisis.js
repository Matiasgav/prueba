// Formato documental Mecanálisis (según CP-OEI-001 / PR-OEI-027).
// Encabezado, pie, títulos, tablas y bloque de control reutilizables.
const fs = require("fs");
const path = require("path");
const {
  Document, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer,
  ImageRun, AlignmentType, WidthType, BorderStyle, ShadingType, HeadingLevel,
  PageNumber, VerticalAlign, LevelFormat, TabStopType, PageBreak,
} = require("docx");

const C = {
  naranja: "E36C0A",
  gris: "6D8289",
  grisClaro: "DAE0E2",
  texto: "262626",
  pie: "595959",
};
const FUENTE = "Calibri";
const ANCHO = 9638; // A4 con márgenes de 2 cm
const IMG = path.join(__dirname, "img");

const sinBorde = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const sinBordes = { top: sinBorde, bottom: sinBorde, left: sinBorde, right: sinBorde };
const linea = { style: BorderStyle.SINGLE, size: 4, color: "A6B4B8" };
const bordes = { top: linea, bottom: linea, left: linea, right: linea };

// ---------- texto ----------
// Admite **negrita** dentro del texto.
function runs(texto, base = {}) {
  return String(texto).split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((t) =>
    t.startsWith("**")
      ? new TextRun({ text: t.slice(2, -2), bold: true, ...base })
      : new TextRun({ text: t, ...base }));
}

const p = (texto, o = {}) => new Paragraph({
  spacing: { after: 100, line: 264 },
  alignment: o.align || AlignmentType.JUSTIFIED,
  indent: o.indent,
  keepNext: o.keepNext,
  children: runs(texto, o.run || {}),
});

const vineta = (texto, nivel = 0) => new Paragraph({
  numbering: { reference: "vinetas", level: nivel },
  spacing: { after: 60, line: 264 },
  alignment: AlignmentType.JUSTIFIED,
  children: runs(texto),
});

const numerada = (texto, ref) => new Paragraph({
  numbering: { reference: ref, level: 0 },
  spacing: { after: 60, line: 264 },
  alignment: AlignmentType.JUSTIFIED,
  children: runs(texto),
});

const h1 = (texto) => new Paragraph({
  heading: HeadingLevel.HEADING_1, keepNext: true,
  spacing: { before: 280, after: 140 },
  children: [new TextRun({ text: texto })],
});
const h2 = (texto) => new Paragraph({
  heading: HeadingLevel.HEADING_2, keepNext: true,
  spacing: { before: 220, after: 100 },
  children: [new TextRun({ text: texto })],
});
const h3 = (texto) => new Paragraph({
  heading: HeadingLevel.HEADING_3, keepNext: true,
  spacing: { before: 160, after: 80 },
  children: [new TextRun({ text: texto })],
});
// Títulos de la portada (OBJETIVO, ALCANCE, ...) — entran en el índice.
const hPortada = (texto) => new Paragraph({
  heading: HeadingLevel.HEADING_1, keepNext: true,
  spacing: { before: 200, after: 60 },
  children: [new TextRun({ text: texto, color: C.gris })],
});
// Subtítulo de rol en Responsabilidades (estilo CP: negrita cursiva subrayada)
const rol = (texto) => new Paragraph({
  keepNext: true, spacing: { before: 140, after: 40 },
  children: [new TextRun({ text: texto, bold: true, italics: true, underline: {} })],
});

const saltoPagina = () => new Paragraph({ children: [new PageBreak()] });

// Recuadro destacado (nota / precaución)
function nota(titulo, texto, color = C.naranja) {
  const b = { style: BorderStyle.SINGLE, size: 4, color };
  return new Table({
    width: { size: ANCHO, type: WidthType.DXA }, columnWidths: [ANCHO],
    rows: [new TableRow({ children: [new TableCell({
      width: { size: ANCHO, type: WidthType.DXA },
      borders: { top: b, bottom: b, right: b, left: { style: BorderStyle.SINGLE, size: 24, color } },
      shading: { fill: color === C.naranja ? "FDF0E6" : "EEF2F3", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 160, right: 160 },
      children: [new Paragraph({ spacing: { after: 0, line: 264 }, alignment: AlignmentType.JUSTIFIED, children: [
        new TextRun({ text: titulo + " ", bold: true, color }), ...runs(texto)] })],
    })] })],
  });
}
const espacio = (after = 120) => new Paragraph({ spacing: { after, before: 0 }, children: [] });

// ---------- tablas ----------
function celda(contenido, ancho, o = {}) {
  const parrafos = (Array.isArray(contenido) ? contenido : [contenido]).map((c) =>
    c instanceof Paragraph ? c : new Paragraph({
      spacing: { after: 0, line: 252 },
      keepNext: o.keepNext,
      alignment: o.align || AlignmentType.LEFT,
      children: runs(c, { size: o.size || 19, bold: o.bold, color: o.color }),
    }));
  return new TableCell({
    width: { size: ancho, type: WidthType.DXA },
    borders: o.borders || bordes,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    verticalAlign: o.vAlign || VerticalAlign.CENTER,
    columnSpan: o.span,
    children: parrafos,
  });
}

// Tabla con encabezado gris claro (estilo CP-OEI)
function tabla(cols, anchos, filas, o = {}) {
  const total = anchos.reduce((a, b) => a + b, 0);
  const cab = new TableRow({
    tableHeader: true, cantSplit: true,
    children: cols.map((c, i) => celda(c, anchos[i], {
      bold: true, fill: C.grisClaro, align: o.alignCab || AlignmentType.LEFT, keepNext: o.keepNext })),
  });
  const cuerpo = filas.map((f) => {
    if (f.seccion) {
      return new TableRow({ cantSplit: true, children: [celda(f.seccion, total, {
        span: anchos.length, bold: true, color: C.naranja, fill: "F7F9F9" })] });
    }
    return new TableRow({ cantSplit: true, children: f.map((v, i) => celda(v, anchos[i], {
      align: (o.centrar || []).includes(i) ? AlignmentType.CENTER : AlignmentType.LEFT,
      bold: (o.negrita || []).includes(i),
      vAlign: VerticalAlign.TOP,
      keepNext: o.keepNext,
    })) });
  });
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: anchos, rows: [cab, ...cuerpo] });
}

// Tabla de pasos: Nº | Actividad | Referencia
function pasos(filas) {
  return tabla(["Nº", "Actividad", "Referencia"], [560, 6878, 2200], filas,
    { centrar: [0], negrita: [0], alignCab: AlignmentType.CENTER });
}

function figura(archivo, anchoPx, altoPx, leyenda, anchoCm = 16) {
  const w = Math.round(anchoCm / 2.54 * 96);
  const h = Math.round(w * altoPx / anchoPx);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(IMG, archivo)),
        transformation: { width: w, height: h }, altText: { title: leyenda, description: leyenda, name: archivo } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
      children: [new TextRun({ text: leyenda, italics: true, size: 18, color: C.gris })] }),
  ];
}

// ---------- encabezado y pie ----------
function encabezado(meta) {
  const lab = (t, align = AlignmentType.LEFT) => new Paragraph({ alignment: align, spacing: { after: 20 },
    children: [new TextRun({ text: t, size: 14, font: FUENTE })] });
  const val = (t, o = {}) => new Paragraph({ alignment: o.align || AlignmentType.LEFT, spacing: { after: 0 },
    children: [new TextRun({ text: t, size: o.size || 16, bold: true, color: o.color || C.gris, font: FUENTE })] });
  const bordeNaranja = { ...sinBordes, right: { style: BorderStyle.SINGLE, size: 12, color: C.naranja } };
  const anchos = [1750, 3900, 1900, 2088];
  const tituloLineas = meta.tituloEncabezado.map((t) => val(t));
  const fila = new TableRow({ children: [
    celda([lab("TIPO DE DOCUMENTO"), lab("TÍTULO DE DOCUMENTO")], anchos[0], { borders: sinBordes, vAlign: VerticalAlign.TOP }),
    celda([val(meta.tipo), ...tituloLineas], anchos[1], { borders: sinBordes, vAlign: VerticalAlign.TOP }),
    celda([
      new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { before: 40, after: 40 }, children: [new TextRun({ text: "CÓDIGO", size: 14 })] }),
      lab("VERSIÓN", AlignmentType.RIGHT), lab("FECHA DE REVISIÓN", AlignmentType.RIGHT)],
    anchos[2], { borders: sinBordes, vAlign: VerticalAlign.TOP }),
    celda([
      val(meta.codigo, { align: AlignmentType.RIGHT, size: 22, color: C.naranja }),
      val(meta.version, { align: AlignmentType.RIGHT, color: C.naranja }),
      val(meta.fecha, { align: AlignmentType.RIGHT, color: C.naranja })],
    anchos[3], { borders: bordeNaranja, vAlign: VerticalAlign.TOP }),
  ] });
  return new Header({ children: [
    new Table({ width: { size: ANCHO, type: WidthType.DXA }, columnWidths: anchos, rows: [fila] }),
    new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { before: 60, after: 0 }, children: [
      new TextRun({ children: [PageNumber.CURRENT], size: 28, color: C.gris }),
      new TextRun({ text: "/", size: 28, color: C.gris }),
      new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 28, color: C.gris })] }),
  ] });
}

function pie() {
  const logo = fs.readFileSync(path.join(IMG, "logo_mecanalisis.jpeg"));
  const t = (x) => new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: x, size: 16, color: C.pie })] });
  return new Footer({ children: [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [
      new TextRun({ text: "SI ESTE DOCUMENTO SE ENCUENTRA IMPRESO SE CONSIDERA COPIA NO CONTROLADA", bold: true, italics: true, size: 16 })] }),
    new Table({ width: { size: ANCHO, type: WidthType.DXA }, columnWidths: [6638, 3000], rows: [new TableRow({ children: [
      celda([t("www.mecanalisis.com.ar | +54 261 476 9010"), t("Pedro del Castillo 3160 . 5519 Guaymallén – Mendoza, Argentina.")], 6638, { borders: sinBordes }),
      celda(new Paragraph({ alignment: AlignmentType.RIGHT, children: [new ImageRun({ type: "jpg", data: logo,
        transformation: { width: 150, height: 42 }, altText: { title: "Mecanálisis", description: "Logo Mecanálisis", name: "logo" } })] }), 3000, { borders: sinBordes }),
    ] })] }),
  ] });
}

// ---------- portada (pág. 1) ----------
function portada(meta) {
  const out = [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 0 },
      children: [new TextRun({ text: meta.tituloPortada[0], bold: true, size: 36, color: C.naranja })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
      children: [new TextRun({ text: meta.tituloPortada[1], bold: true, size: 30, color: C.naranja })] }),
  ];
  const bloques = [["OBJETIVO", meta.objetivo], ["ALCANCE", meta.alcance]];
  if (meta.responsable) bloques.push(["RESPONSABLE DEL PROCESO", meta.responsable]);
  for (const [titulo, texto] of bloques) {
    out.push(hPortada(titulo));
    (Array.isArray(texto) ? texto : [texto]).forEach((t) => out.push(p(t)));
  }
  out.push(new Paragraph({ spacing: { before: 120 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: C.naranja, space: 1 } }, children: [] }));
  out.push(saltoPagina());
  // Índice: marcador que post-proceso.js reemplaza por un campo TOC con resultado precalculado.
  out.push(new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "ÍNDICE", bold: true, size: 24, color: C.gris })] }));
  out.push(new Paragraph({ children: [new TextRun("%%INDICE%%")] }));
  out.push(saltoPagina());
  return out;
}

// ---------- bloque de control (cierre del documento) ----------
function cierre(meta) {
  const out = [];
  const oVacia = (filas, n) => (filas && filas.length ? filas : [Array(n).fill(" ")]);
  out.push(tabla(["CÓDIGO", "TÍTULO"], [2200, 7438], oVacia(meta.registros, 2), { centrar: [0], alignCab: AlignmentType.CENTER, keepNext: true }));
  out.push(new Paragraph({ keepNext: true, spacing: { after: 200 }, children: [] }));
  out.push(tabla(["REVISIÓN", "FECHA", "DESCRIPCIÓN"], [1400, 1400, 6838], meta.revisiones, { keepNext: true }));
  out.push(new Paragraph({ keepNext: true, spacing: { after: 200 }, children: [] }));
  out.push(tabla(["PREPARÓ", "REVISÓ", "APROBÓ", "FECHA DE EMISIÓN"], [2410, 2410, 2409, 2409], [meta.firmas], { keepNext: true }));
  out.push(new Paragraph({ keepNext: true, spacing: { after: 200 }, children: [] }));
  out.push(tabla(["DOCUMENTOS DE REFERENCIA"], [ANCHO], oVacia((meta.referencias || []).map((r) => [r]), 1), { keepNext: true }));
  out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 480 },
    children: [new TextRun({ text: "FIN DE DOCUMENTO", bold: true, size: 28, color: C.naranja })] }));
  return out;
}

function documento(meta, cuerpo) {
  return new Document({
    creator: "Mecanálisis S.A.",
    title: `${meta.codigo} ${meta.tituloPortada.join(" – ")}`,
    styles: {
      default: { document: { run: { font: FUENTE, size: 20, color: C.texto } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, color: C.naranja, font: FUENTE }, paragraph: { outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 21, bold: true, color: C.naranja, font: FUENTE }, paragraph: { outlineLevel: 1, indent: { left: 0 } } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 20, bold: true, color: C.gris, font: FUENTE }, paragraph: { outlineLevel: 2 } },
      ],
    },
    numbering: { config: [
      { reference: "vinetas", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "-", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 283 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "▪", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1134, hanging: 283 } } } }] },
      ...(meta.listasNumeradas || []).map((ref) => ({ reference: ref, levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] })),
    ] },
    sections: [{
      properties: { page: { size: { width: 11906, height: 16838 },
        margin: { top: 2100, bottom: 1700, left: 1134, right: 1134, header: 500, footer: 400 } } },
      headers: { default: encabezado(meta) },
      footers: { default: pie() },
      children: [...portada(meta), ...cuerpo, ...cierre(meta)],
    }],
  });
}

module.exports = { C, ANCHO, p, vineta, numerada, h1, h2, h3, rol, nota, espacio, tabla, pasos, figura, saltoPagina, documento, runs };
