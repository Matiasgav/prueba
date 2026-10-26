// Genera los .docx de procedimientos_gris/ con índice (campo TOC) precalculado.
// Uso: node build.js   (requiere LibreOffice, pdftotext, zip/unzip)
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");
const { Packer } = require("docx");
const F = require("./formato_mecanalisis");

const SALIDA = path.resolve(__dirname, "..");
const SOFFICE = process.env.SOFFICE || "soffice";
const DOCS = [
  ["epg001_procedimiento", "00503-00-EPG001 Procedimiento Inspeccion Robotizada GRIS"],
  ["epg002_protocolos_elcid", "00503-00-EPG002 Anexo Protocolos de Ensayo EL CID"],
];

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const textoParrafo = (xml) => [...xml.matchAll(/<w:t(?: [^>]*)?>([^<]*)<\/w:t>/g)].map((m) => m[1]).join("");

function titulos(docXml) {
  const out = [];
  for (const m of docXml.matchAll(/<w:p>(?:(?!<\/w:p>).)*?<w:pStyle w:val="Heading([12])"\/>(?:(?!<\/w:p>).)*<\/w:p>/gs)) {
    out.push({ nivel: Number(m[1]), texto: textoParrafo(m[0]) });
  }
  return out;
}

function campoIndice(entradas) {
  const fila = (e, i) => {
    const ini = i === 0 ? `<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-2" \\u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>` : "";
    const fin = i === entradas.length - 1 ? `<w:r><w:fldChar w:fldCharType="end"/></w:r>` : "";
    const sangria = e.nivel === 2 ? 425 : 0;
    const neg = e.nivel === 1 ? "<w:b/>" : "";
    return `<w:p><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="${F.ANCHO}"/></w:tabs><w:spacing w:after="${e.nivel === 1 ? 60 : 30}"/><w:ind w:left="${sangria}"/></w:pPr>${ini}<w:r><w:rPr>${neg}<w:sz w:val="${e.nivel === 1 ? 20 : 19}"/></w:rPr><w:t xml:space="preserve">${esc(e.texto)}</w:t></w:r><w:r><w:rPr><w:sz w:val="19"/></w:rPr><w:tab/><w:t>${e.pagina}</w:t></w:r>${fin}</w:p>`;
  };
  return entradas.map(fila).join("");
}

function sh(cmd, args, cwd) { return execFileSync(cmd, args, { cwd, stdio: ["ignore", "pipe", "pipe"] }).toString(); }

function paginasDeTitulos(pdf, entradas) {
  const paginas = sh("pdftotext", ["-layout", pdf, "-"]).split("\f");
  const norm = (s) => s.replace(/\s+/g, " ").trim().toUpperCase();
  let desde = 2; // las páginas 1 (portada) y 2 (índice) contienen los títulos del índice
  return entradas.map((e, i) => {
    if (i < 3) return { ...e, pagina: 1 }; // OBJETIVO, ALCANCE, RESPONSABLE
    for (let k = desde; k < paginas.length; k++) {
      if (paginas[k].split("\n").some((l) => norm(l) === norm(e.texto))) {
        desde = k; return { ...e, pagina: k + 1 };
      }
    }
    return { ...e, pagina: "?" };
  });
}

async function construir(modulo, nombre) {
  const { meta, cuerpo } = require(`./${modulo}`);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "gris-"));
  const base = path.join(tmp, "base.docx");
  fs.writeFileSync(base, await Packer.toBuffer(F.documento(meta, cuerpo)));
  const dir = path.join(tmp, "x");
  sh("unzip", ["-q", base, "-d", dir]);
  const docPath = path.join(dir, "word", "document.xml");
  const original = fs.readFileSync(docPath, "utf8");
  const marcador = /<w:p>(?:(?!<w:p>).)*?%%INDICE%%.*?<\/w:p>/s;
  let entradas = titulos(original).map((e) => ({ ...e, pagina: 0 }));
  const final = path.join(SALIDA, `${nombre}.docx`);

  // Dos pasadas: la primera mide las páginas, la segunda escribe el índice definitivo.
  for (let pasada = 0; pasada < 2; pasada++) {
    fs.writeFileSync(docPath, original.replace(marcador, campoIndice(entradas)));
    if (fs.existsSync(final)) fs.unlinkSync(final);
    sh("zip", ["-q", "-X", "-r", final, "."], dir);
    sh(SOFFICE, ["--headless", "--convert-to", "pdf", "--outdir", tmp, final]);
    const pdf = path.join(tmp, `${nombre}.pdf`);
    if (pasada === 0) entradas = paginasDeTitulos(pdf, entradas);
    else fs.copyFileSync(pdf, path.join(SALIDA, "pdf", `${nombre}.pdf`));
  }
  const faltantes = entradas.filter((e) => e.pagina === "?");
  console.log(`${nombre}.docx — ${entradas.length} entradas de índice${faltantes.length ? `, sin página: ${faltantes.map((e) => e.texto).join(", ")}` : ""}`);
  fs.rmSync(tmp, { recursive: true, force: true });
}

(async () => {
  fs.mkdirSync(path.join(SALIDA, "pdf"), { recursive: true });
  for (const [m, n] of DOCS) await construir(m, n);
})().catch((e) => { console.error(e.stderr ? e.stderr.toString() : e); process.exit(1); });
