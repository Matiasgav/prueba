"""Actualiza en el manual 00503-00-EPG003 los números de paso que remiten a 00503-00-EPG001.

El manual se edita aparte (fuentes/…(original).docx); este script toma la numeración vigente de
EPG001 (ids de pasos en epg001_procedimiento.js) y la escribe en la tabla «Relación con el
procedimiento» y en las citas del texto. Uso: python3 epg003_referencias.py
"""
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

AQUI = Path(__file__).parent
ORIGEN = AQUI / "fuentes" / "00503-00-EPG003 Manual de uso del software GRIS (original).docx"
FECHA_ORIGEN, FECHA = "26/10/2026", "29/10/2026"
DESTINO = AQUI.parent / "00503-00-EPG003 Manual de uso del software GRIS.docx"

num = json.loads(subprocess.check_output(
    ["node", "-e", 'console.log(JSON.stringify(require("./epg001_procedimiento").num))'], cwd=AQUI))

# Primera columna de la tabla «Relación con el procedimiento», en el orden de sus filas.
FILAS = [
    f"{num['sw_config']} y {num['sw_rampa']}",           # parámetros geométricos y ajustes → 4.2
    f"{num['conexiones']}",                                # conexión del equipo → 3.1
    f"{num['sw_param']}",                                  # paso de imágenes y de muestreo WTT → 4.4 y 5.3
    f"{num['montaje']} a {num['limite']}",                 # montaje, reconocimiento y posición máxima → 4.3
    f"{num['wtt_verif']}",                                 # verificación funcional del WTT → 5.2
    f"{num['foco']}",                                      # foco de las cámaras → 4.4
    f"{num['ciclo_ini']} a {num['avance']}, {num['ciclo_fin']}",  # cero, avance y cambio de ranura → 4.3
    f"{num['wtt']}",                                       # registro WTT → 5.3 y 5.4
    f"{num['guardar']}",                                   # guardado de los datos → 7
]
CITAS = [
    (r"pasos \d+ y \d+ de EPG001", f"pasos {num['sw_config']} y {num['sw_rampa']} de 00503-00-EPG001"),
    (r"paso \d+ de EPG001\)\. No se toman", f"paso {num['sw_param']} de 00503-00-EPG001). No se toman"),
    (r"paso \d+ de EPG001\): tres muestras", f"paso {num['wtt_verif']} de 00503-00-EPG001): tres muestras"),
]


def poner_texto(celda, texto):
    """Deja el texto de la celda en su primer <w:t> y vacía los demás."""
    ts = list(re.finditer(r"(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)", celda))
    out, pos = [], 0
    for i, m in enumerate(ts):
        out.append(celda[pos:m.start()] + m.group(1) + (texto if i == 0 else "") + m.group(3))
        pos = m.end()
    return "".join(out) + celda[pos:]


def main():
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(ORIGEN) as z:
        z.extractall(tmp)
    doc = tmp / "word" / "document.xml"
    s = doc.read_text(encoding="utf8")
    titulo = [m.start() for m in re.finditer("RELACIÓN CON EL PROCEDIMIENTO", s)][-1]
    t0 = s.index("<w:tbl>", titulo)
    t1 = s.index("</w:tbl>", t0)
    tabla = s[t0:t1]
    filas = re.findall(r"<w:tr[ >].*?</w:tr>", tabla, re.S)[1:]
    assert len(filas) == len(FILAS), f"la tabla tiene {len(filas)} filas, se esperaban {len(FILAS)}"
    for fila, nuevo in zip(filas, FILAS):
        celda = re.search(r"<w:tc>.*?</w:tc>", fila, re.S).group(0)
        tabla = tabla.replace(fila, fila.replace(celda, poner_texto(celda, nuevo), 1), 1)
    s = s[:t0] + tabla + s[t1:]
    for patron, nuevo in CITAS:
        s, n = re.subn(patron, nuevo, s)
        assert n == 1, patron
    doc.write_text(s, encoding="utf8")
    for xml in (tmp / "word").glob("*.xml"):  # fecha de revisión unificada del paquete
        x = xml.read_text(encoding="utf8")
        if FECHA_ORIGEN in x:
            xml.write_text(x.replace(FECHA_ORIGEN, FECHA), encoding="utf8")
    if DESTINO.exists():
        DESTINO.unlink()
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(tmp.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(tmp).as_posix())
    shutil.rmtree(tmp)
    print(f"{DESTINO.name}: pasos de EPG001 actualizados ({', '.join(FILAS)})")


if __name__ == "__main__":
    main()
