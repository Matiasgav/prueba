// Catálogo de materiales y terminaciones.
// Cada clave se usa en el modelo (elemento.mat). "criterio" explica por qué se eligió:
//   DURABLE  -> zona de desgaste o difícil de reemplazar: se paga calidad.
//   ECONOMICO -> lo puede romper el inquilino o se cambia fácil: se compra barato.
//   ESTANDAR -> material común de obra, sin sobrecosto.

export const SPECS = {
  // ---------------- Fundación ----------------
  hormigon: { nombre: 'Hormigón H-21 (platea + viga de borde)', color: '#b9b5ad', criterio: 'ESTANDAR', unidad: 'm3' },
  eps_fund: { nombre: 'Poliestireno expandido 20 kg/m³ 50 mm bajo platea y perimetral', color: '#f2f2ee', criterio: 'ESTANDAR', unidad: 'm2' },
  film: { nombre: 'Film polietileno 200 µm bajo platea', color: '#7d8c99', criterio: 'ESTANDAR', unidad: 'm2' },

  // ---------------- Estructura de madera ----------------
  pino_2x6: { nombre: 'Pino impregnado CCA cepillado 2"x6" (45x145) — montantes y soleras muros exteriores', color: '#d9b77e', criterio: 'ESTANDAR', unidad: 'ml' },
  pino_2x3: { nombre: 'Pino cepillado 2"x3" (45x70) — tabiques interiores', color: '#dcbd88', criterio: 'ESTANDAR', unidad: 'ml' },
  pino_2x8: { nombre: 'Pino impregnado cepillado 2"x8" (45x195) — vigas entrepiso y cabios', color: '#d2ad70', criterio: 'ESTANDAR', unidad: 'ml' },
  pino_2x2: { nombre: 'Pino cepillado 2"x2" (45x45) — clavaderas de techo', color: '#d8b98a', criterio: 'ESTANDAR', unidad: 'ml' },
  pino_1x2: { nombre: 'Pino cepillado 1"x2" (20x45) — listones / clavaderas fachada / contraclavaderas', color: '#dcc195', criterio: 'ESTANDAR', unidad: 'ml' },
  pino_1x8: { nombre: 'Pino cepillado 1"x8" (20x195) — frentines de alero (se revisten en chapa)', color: '#d6b583', criterio: 'ESTANDAR', unidad: 'ml' },
  laminada: { nombre: 'Viga laminada de pino 90x300 — cumbrera (a verificar por calculista)', color: '#c99a5b', criterio: 'DURABLE', unidad: 'ml' },

  // ---------------- Placas ----------------
  osb_11: { nombre: 'OSB 11,1 mm 1,22x2,44 — arriostramiento exterior', color: '#c9a66b', criterio: 'ESTANDAR', unidad: 'placa' },
  osb_18: { nombre: 'OSB 18 mm machihembrado 1,22x2,44 — piso planta alta', color: '#c4a064', criterio: 'ESTANDAR', unidad: 'placa' },
  durlock_std: { nombre: 'Placa de yeso estándar 12,5 mm 1,20x2,40 (Durlock ST)', color: '#f4f2ec', criterio: 'ESTANDAR', unidad: 'placa' },
  durlock_rh: { nombre: 'Placa de yeso resistente a la humedad 12,5 mm 1,20x2,40 (Durlock RH, verde)', color: '#d5e6d0', criterio: 'DURABLE', unidad: 'placa' },
  cementicia: { nombre: 'Placa cementicia 10 mm 1,20x2,40 (tipo Superboard) — box de ducha', color: '#c8c8c2', criterio: 'DURABLE', unidad: 'placa' },
  fibro_reg: { nombre: 'Cassette de registro: fibrocemento 10 mm pintado + bastidor + burlete EPDM, tornillos inox', color: '#3a3f44', criterio: 'DURABLE', unidad: 'u' },

  // ---------------- Aislaciones y barreras ----------------
  lana_150: { nombre: 'Lana de vidrio 150 mm (rollo, sin foil) — muros y techo', color: '#f3d36b', criterio: 'ESTANDAR', unidad: 'm2' },
  barrera_vapor: { nombre: 'Barrera de vapor polietileno 200 µm (cara interior)', color: '#9fb4c7', criterio: 'ESTANDAR', unidad: 'm2' },
  membrana: { nombre: 'Barrera de agua y viento hidrófuga respirable (tipo Tyvek)', color: '#eaeef2', criterio: 'ESTANDAR', unidad: 'm2' },

  // ---------------- Envolvente exterior ----------------
  chapa_muro: { nombre: 'Chapa trapezoidal T-101 prepintada C25 — gris grafito, colocación vertical', color: '#3b4248', criterio: 'DURABLE', unidad: 'ml' },
  chapa_techo: { nombre: 'Chapa trapezoidal T-101 prepintada C25 — negra, techo', color: '#26292c', criterio: 'DURABLE', unidad: 'ml' },
  siding: { nombre: 'Siding cementicio texturado símil madera 8 mm, pintado "roble" (fachada frente)', color: '#93704f', criterio: 'DURABLE', unidad: 'm2' },
  zinguerias: { nombre: 'Zinguería chapa prepintada negra (cumbrera, babetas, cenefas, cupertinas)', color: '#202325', criterio: 'DURABLE', unidad: 'ml' },
  canaleta: { nombre: 'Canaleta y bajada chapa prepintada negra 15 cm', color: '#1e2124', criterio: 'DURABLE', unidad: 'ml' },
  zocalo_chapa: { nombre: 'Zócalo de chapa lisa plegada negra (protege EPS perimetral)', color: '#1f2225', criterio: 'DURABLE', unidad: 'ml' },
  alero_fibro: { nombre: 'Cielorraso de alero: fibrocemento 6 mm ventilado, pintado gris oscuro', color: '#4a4f54', criterio: 'ESTANDAR', unidad: 'm2' },
  visera: { nombre: 'Visera de entrada: chapa plegada negra sobre ménsulas de planchuela', color: '#1c1f22', criterio: 'ESTANDAR', unidad: 'u' },

  // ---------------- Aberturas ----------------
  pvc_marco: { nombre: 'Ventana PVC (perfil 60 mm) exterior foliado antracita / interior blanco, DVH 4/12/4', color: '#33373b', criterio: 'DURABLE', unidad: 'u' },
  vidrio: { nombre: 'DVH 4/12/4 float', color: '#9cc3d5', criterio: 'DURABLE', unidad: 'm2' },
  puerta_ext: { nombre: 'Puerta exterior chapa inyectada con poliuretano 80x200, cerradura de seguridad, color ocre', color: '#c6902f', criterio: 'DURABLE', unidad: 'u' },
  puerta_int: { nombre: 'Puerta placa interior 70x200 MDF pintada blanca, marco chapa N°18', color: '#f2f0ea', criterio: 'ECONOMICO', unidad: 'u' },
  herrajes: { nombre: 'Herrajes de acero inoxidable / bronce platil (manijas, bisagras de 3 alas)', color: '#8a8d90', criterio: 'DURABLE', unidad: 'u' },
  cortina: { nombre: 'Cortina roller blackout estándar (reemplazable)', color: '#e6e0d4', criterio: 'ECONOMICO', unidad: 'u' },

  // ---------------- Pisos y revestimientos ----------------
  porcelanato: { nombre: 'Porcelanato 60x60 símil cemento gris claro, rectificado, PEI IV', color: '#c9c6c0', criterio: 'DURABLE', unidad: 'm2' },
  spc: { nombre: 'Piso SPC (vinílico rígido) 5 mm símil roble claro, click, uso comercial', color: '#c9a477', criterio: 'DURABLE', unidad: 'm2' },
  ceramica_ducha: { nombre: 'Revestimiento cerámico 30x60 blanco mate (box ducha hasta 2,10 m)', color: '#f1f1ef', criterio: 'DURABLE', unidad: 'm2' },
  ceramica_cocina: { nombre: 'Revestimiento cerámico 7,5x15 "subway" blanco brillante (frente de mesada)', color: '#f7f7f5', criterio: 'DURABLE', unidad: 'm2' },
  zocalo: { nombre: 'Zócalo MDF hidrófugo 7 cm pintado blanco', color: '#f0eee8', criterio: 'ECONOMICO', unidad: 'ml' },

  // ---------------- Pinturas (colores del proyecto) ----------------
  pintura_blanco: { nombre: 'Látex interior lavable — Blanco cálido (paredes y cielorrasos)', color: '#f4f1ea', criterio: 'ECONOMICO', unidad: 'm2' },
  pintura_salvia: { nombre: 'Látex interior lavable — Verde salvia (pared de respaldo planta alta)', color: '#9aac8f', criterio: 'ECONOMICO', unidad: 'm2' },
  pintura_antihongo: { nombre: 'Látex antihongo — Blanco (baño)', color: '#f4f4f1', criterio: 'ECONOMICO', unidad: 'm2' },

  // ---------------- Escalera ----------------
  lenga: { nombre: 'Lenga maciza 38 mm (huellas) con nariz antideslizante — madera local dura', color: '#b0703f', criterio: 'DURABLE', unidad: 'm2' },
  zanca: { nombre: 'Zancas de pino laminado 45x240', color: '#cfa36a', criterio: 'ESTANDAR', unidad: 'ml' },
  hierro_negro: { nombre: 'Baranda de hierro (planchuela 38x6 + barrotes Ø12) pintada negro satinado', color: '#191b1d', criterio: 'DURABLE', unidad: 'ml' },
  pasamanos: { nombre: 'Pasamanos de lenga 45x45 barnizado', color: '#a8693a', criterio: 'DURABLE', unidad: 'ml' },

  // ---------------- Cocina ----------------
  melamina_blanca: { nombre: 'Muebles melamina 18 mm blanca, canto ABS, bisagras cierre suave (estándar comercial)', color: '#f5f5f2', criterio: 'ECONOMICO', unidad: 'u' },
  granito: { nombre: 'Mesada granito Gris Mara 20 mm con zócalo', color: '#7f7d7a', criterio: 'DURABLE', unidad: 'ml' },
  bacha: { nombre: 'Bacha simple acero inoxidable 52x37', color: '#cfd3d6', criterio: 'DURABLE', unidad: 'u' },
  cocina: { nombre: 'Cocina a gas 51 cm 4 hornallas con horno, encendido y válvula de seguridad', color: '#e8e8e6', criterio: 'ESTANDAR', unidad: 'u' },
  heladera: { nombre: 'Heladera con freezer 56 cm (~250 l) — la provee el propietario', color: '#f0f0ee', criterio: 'ESTANDAR', unidad: 'u' },
  lavarropas: { nombre: 'Conexión lavarropas carga frontal 60 cm bajo mesada (canilla + desagüe con sifón + toma)', color: '#eeeeec', criterio: 'ESTANDAR', unidad: 'u' },
  purificador: { nombre: 'Purificador/campana 60 cm', color: '#c9cdd0', criterio: 'ECONOMICO', unidad: 'u' },
  griferia_cocina: { nombre: 'Grifería monocomando de mesada pico alto (FV o similar, cuerpo de bronce)', color: '#c5c9cc', criterio: 'DURABLE', unidad: 'u' },

  // ---------------- Baño ----------------
  inodoro: { nombre: 'Inodoro largo con mochila apoyada (loza blanca, línea económica de marca)', color: '#fbfbfa', criterio: 'DURABLE', unidad: 'u' },
  lavatorio: { nombre: 'Lavatorio de colgar 45 cm loza blanca con columna corta/ménsulas', color: '#fbfbfa', criterio: 'DURABLE', unidad: 'u' },
  plato_ducha: { nombre: 'Receptáculo de ducha 80x120 acrílico reforzado', color: '#f7f7f6', criterio: 'DURABLE', unidad: 'u' },
  griferia_bano: { nombre: 'Grifería monocomando lavatorio + mezcladora ducha (FV o similar, cuerpo bronce)', color: '#c7cbce', criterio: 'DURABLE', unidad: 'u' },
  cortina_bano: { nombre: 'Barral inox + cortina de baño (reemplazable)', color: '#dfe7ea', criterio: 'ECONOMICO', unidad: 'u' },
  espejo: { nombre: 'Botiquín con espejo 45x60', color: '#cfe0e6', criterio: 'ECONOMICO', unidad: 'u' },
  accesorios: { nombre: 'Accesorios de baño acero inox (toallero, portarrollo, percha)', color: '#b8bcbf', criterio: 'DURABLE', unidad: 'jgo' },

  // ---------------- Instalaciones ----------------
  ppr_20: { nombre: 'Termofusión PPR 20 mm (agua fría)', color: '#2f7fd6', criterio: 'DURABLE', unidad: 'ml' },
  ppr_20c: { nombre: 'Termofusión PPR 20 mm PN20 (agua caliente) + vaina aislante', color: '#d83b2d', criterio: 'DURABLE', unidad: 'ml' },
  pvc_110: { nombre: 'PVC 3,2 mm Ø110 desagüe cloacal', color: '#e98f2e', criterio: 'ESTANDAR', unidad: 'ml' },
  pvc_63: { nombre: 'PVC 3,2 mm Ø63 / ventilación', color: '#eda253', criterio: 'ESTANDAR', unidad: 'ml' },
  pvc_50: { nombre: 'PVC 3,2 mm Ø50 / Ø40 desagües secundarios', color: '#f0b064', criterio: 'ESTANDAR', unidad: 'ml' },
  camara: { nombre: 'Cámara de inspección 60x60 premoldeada con tapa', color: '#8b8a86', criterio: 'ESTANDAR', unidad: 'u' },
  gas_pipe: { nombre: 'Gas: termofusión PE-AL-PE aprobado (tipo Sigas) Ø20/25', color: '#e8c21a', criterio: 'DURABLE', unidad: 'ml' },
  llave_paso: { nombre: 'Llave de paso esférica (agua) / llave de gas aprobada', color: '#c33', criterio: 'DURABLE', unidad: 'u' },
  conduit: { nombre: 'Caño corrugado ignífugo (no propagante) 3/4"', color: '#8d939a', criterio: 'ESTANDAR', unidad: 'ml' },
  caja_rect: { nombre: 'Caja rectangular 5x10 PVC (tomas y llaves)', color: '#eceae4', criterio: 'ESTANDAR', unidad: 'u' },
  caja_oct: { nombre: 'Caja octogonal chica PVC (centros de luz)', color: '#eceae4', criterio: 'ESTANDAR', unidad: 'u' },
  caja_cuad: { nombre: 'Caja cuadrada 10x10 PVC (derivación)', color: '#eceae4', criterio: 'ESTANDAR', unidad: 'u' },
  tablero: { nombre: 'Tablero embutir 12 módulos con ID 40A 30mA + 4 PIA', color: '#e4e4e0', criterio: 'DURABLE', unidad: 'u' },
  cable: { nombre: 'Cable unipolar IRAM NM-247-3 (1,5 / 2,5 / 4 mm²)', color: '#d22', criterio: 'ESTANDAR', unidad: 'ml' },
  luminaria: { nombre: 'Luminarias LED (plafones, apliques) línea económica', color: '#fff7d6', criterio: 'ECONOMICO', unidad: 'u' },
  calefactor: { nombre: 'Calefactor tiro balanceado 3000 kcal/h (≈3,5 kW), válvula de seguridad', color: '#e9e6df', criterio: 'DURABLE', unidad: 'u' },
  termotanque: { nombre: 'Termotanque eléctrico 50 l (2 kW) de colgar', color: '#f2f2f2', criterio: 'ESTANDAR', unidad: 'u' },
  rejilla: { nombre: 'Rejilla de ventilación de gas reglamentaria 15x15 (alta y baja)', color: '#8a8a8a', criterio: 'ESTANDAR', unidad: 'u' },

  // ---------------- Muebles ----------------
  cama_doble: { nombre: 'Sommier + colchón 2 plazas 140x190 (estándar)', color: '#ece7de', criterio: 'ECONOMICO', unidad: 'u' },
  cama_simple: { nombre: 'Sommier + colchón 1 plaza 80x190 (estándar)', color: '#ece7de', criterio: 'ECONOMICO', unidad: 'u' },
  textil_mostaza: { nombre: 'Textiles (almohadones/cubrecama) mostaza — reemplazables', color: '#c99a2e', criterio: 'ECONOMICO', unidad: 'jgo' },
  textil_terracota: { nombre: 'Textiles terracota — reemplazables', color: '#b4613f', criterio: 'ECONOMICO', unidad: 'jgo' },
  placard: { nombre: 'Placard melamina 150x60x200 puertas corredizas (estándar comercial)', color: '#efede7', criterio: 'ECONOMICO', unidad: 'u' },
  escritorio: { nombre: 'Escritorio melamina 120x55 roble claro', color: '#caa679', criterio: 'ECONOMICO', unidad: 'u' },
  silla: { nombre: 'Silla de comedor de madera/metal (estándar)', color: '#2b2b2b', criterio: 'ECONOMICO', unidad: 'u' },
  mesa: { nombre: 'Mesa 80x60 tapa melamina roble + patas metálicas', color: '#caa679', criterio: 'ECONOMICO', unidad: 'u' },
  banco: { nombre: 'Banco-sofá integrado a escalera: estructura pino + tapa OSB pintada + almohadones', color: '#d8c4a4', criterio: 'ECONOMICO', unidad: 'u' },
  mesa_luz: { nombre: 'Mesa de luz / estante flotante melamina', color: '#caa679', criterio: 'ECONOMICO', unidad: 'u' },
  zapatero: { nombre: 'Zapatero-banco de entrada + percheros', color: '#caa679', criterio: 'ECONOMICO', unidad: 'u' },

  // ---------------- Exterior ----------------
  planta: { nombre: 'Planta de interior (decoración)', color: '#4f7a3a', criterio: 'ECONOMICO', unidad: 'u' },
  pasto: { nombre: 'Terreno (referencia)', color: '#7c8f5a', criterio: 'ESTANDAR', unidad: '-' },
  grava: { nombre: 'Senda de grava / laja', color: '#a7a297', criterio: 'ESTANDAR', unidad: 'm2' },
  deck: { nombre: 'Deck de acceso pino impregnado CCA 1x4 sobre tirantes 2x4 (con lasur)', color: '#a5835c', criterio: 'ESTANDAR', unidad: 'm2' },
  escalon: { nombre: 'Escalón de hormigón premoldeado', color: '#a9a69f', criterio: 'ESTANDAR', unidad: 'u' },
};

// Paleta de diseño (para documentación)
export const PALETA = [
  { nombre: 'Gris grafito chapa', hex: '#2f3438', uso: 'Volumen exterior' },
  { nombre: 'Roble (siding)', hex: '#93704f', uso: 'Fachada de acceso' },
  { nombre: 'Ocre', hex: '#c6902f', uso: 'Puerta de entrada' },
  { nombre: 'Blanco cálido', hex: '#f4f1ea', uso: 'Paredes y cielorrasos' },
  { nombre: 'Verde salvia', hex: '#9aac8f', uso: 'Pared de respaldo planta alta' },
  { nombre: 'Lenga', hex: '#b0703f', uso: 'Escalera y pasamanos' },
  { nombre: 'Gris cemento', hex: '#c9c6c0', uso: 'Piso planta baja y baño' },
  { nombre: 'Roble claro', hex: '#c9a477', uso: 'Piso planta alta, escritorio, mesa' },
  { nombre: 'Mostaza / terracota', hex: '#c99a2e', uso: 'Textiles reemplazables' },
  { nombre: 'Negro satinado', hex: '#191b1d', uso: 'Herrería, griferías opcionales, zinguerías' },
];
