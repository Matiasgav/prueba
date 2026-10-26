# Procedimientos GRIS – formato Mecanálisis

| Código | Documento | Origen |
|---|---|---|
| 00503-00-EPG001 | Procedimiento de inspección robotizada GRIS (visual, EL CID y WTT) | Reemplaza 00503-00-ZPL001 (Method Statement) |
| 00503-00-EPG002 | Anexo: Protocolos de ensayo EL CID (excitación, calibración, ELCSoft) | Protocolos Nexergy, junio 2025 |

El procedimiento indica **qué** hacer y en qué orden; el anexo contiene el **cómo** técnico.
No se repite información: el procedimiento remite al protocolo correspondiente y el anexo indica desde qué pasos se lo invoca.

Codificación según PR-OEI-027: proyecto `00503`, máquina `00`, área `E` (eléctrica), tipo `PG` (procedimiento de ensayo del generador, combinación nueva a aprobar por la Gerencia de O&I).

## Regenerar

```
cd src && node build.js
```

Genera los `.docx` (con índice precalculado) y los `.pdf` de control en `pdf/`. El contenido se edita en `src/epg001_procedimiento.js` y `src/epg002_protocolos_elcid.js`; el formato en `src/formato_mecanalisis.js`.
