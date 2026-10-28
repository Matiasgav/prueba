"""Arma el paquete de entrega con todos los documentos necesarios para realizar el ensayo GRIS.

Uso: python3 empaquetar.py   (después de node build.js)
Salida: entrega/Paquete documental GRIS 00503.zip
"""
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F = Path(__file__).resolve().parent / "fuentes"
PDF = RAIZ / "pdf"

CONTENIDO = [
    ("1 Procedimiento", [RAIZ / "00503-00-EPG001 Procedimiento Inspeccion Robotizada GRIS.docx",
                         PDF / "00503-00-EPG001 Procedimiento Inspeccion Robotizada GRIS.pdf",
                         PDF / "00503-00-EPG001 Figura 1 Esquema general de conexiones (A3).pdf"]),
    ("2 Anexo EL CID", [RAIZ / "00503-00-EPG002 Anexo Protocolos de Ensayo EL CID.docx",
                        PDF / "00503-00-EPG002 Anexo Protocolos de Ensayo EL CID.pdf",
                        F / "RME-ELC-01 Registro de calculo de excitacion.xlsx"]),
    ("3 Manual del software", [RAIZ / "00503-00-EPG003 Manual de uso del software GRIS.docx",
                               PDF / "00503-00-EPG003 Manual de uso del software GRIS.pdf"]),
    ("4 Desprendimiento de piezas", [F / "00503-00-ZIT003 Residual Part Detachment Risk Assessment.docx",
                                     F / "00503-00-ZIT003 Residual Part Detachment Risk Assessment.pdf",
                                     RAIZ / "00503-00-ZRQ001 Inspection Detachment Checklist.docx",
                                     PDF / "00503-00-ZRQ001 Inspection Detachment Checklist.pdf"]),
]

INDICE = """PAQUETE DOCUMENTAL – INSPECCIÓN ROBOTIZADA GRIS (00503)

El documento principal es 00503-00-EPG001. Los demás derivan de él y se invocan desde sus pasos.

1 Procedimiento
  00503-00-EPG001  Procedimiento de inspección robotizada GRIS (ensayos EL CID y WTT en entrehierro).
                   Figura 1 (esquema de conexiones) también como PDF A3 suelto, para imprimir.
2 Anexo EL CID
  00503-00-EPG002  Protocolos de ensayo EL CID: excitación, calibración, ELCSoft y cálculo de la excitación.
  RME-ELC-01       Registro de cálculo de excitación (planilla).
3 Manual del software
  00503-00-EPG003  Manual de uso del software GRIS.
4 Desprendimiento de piezas
  00503-00-ZIT003  Evaluación del riesgo residual de desprendimiento de piezas del robot.
  00503-00-ZRQ001  Checklist de verificación pre y post-ensayo (formato Mecanálisis).
"""


def main():
    salida = RAIZ / "entrega" / "Paquete documental GRIS 00503.zip"
    salida.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("0 Indice del paquete.txt", INDICE)
        for carpeta, archivos in CONTENIDO:
            for a in archivos:
                assert a.exists(), a
                z.write(a, f"{carpeta}/{a.name}")
    print(salida, f"{salida.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
