"""Figura 2: nudo ocho reconstruido paso a paso, con fotos del atado en el robot GRIS.

Las fotos (fuentes/fotos_nudo/paso_N.jpeg, ya ordenadas según el atado) se giran 90° y se componen en
una grilla con el número de paso y una leyenda corta. Salida: img/nudo_ocho.svg (build.js la convierte a PNG).
Uso: python3 nudo_ocho_fotos.py
"""
import base64
import io
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).parent
PASOS = [
    "Formar un seno a unos\n30 cm del extremo.",
    "Rodear el firme\ncon el chicote.",
    "Pasar el chicote por el\nseno: queda el ocho simple.",
    "Pasar el chicote por el\nojal de amarre del robot.",
    "Repasar el ocho con el\nchicote, en sentido inverso.",
    "Completar el repaso: el\nchicote sale junto al firme.",
    "Peinar y apretar tirando de los cuatro\nramales. Chicote de 3 a 5 cm.",
]
# Zoom de cada paso sobre la foto ya girada (1156 × 651 px): centro (x, y) y ancho del recorte.
ZOOM = {1: (716, 254, 880), 2: (635, 370, 1000), 3: (559, 300, 600), 4: (440, 330, 680),
        5: (531, 254, 700), 6: (578, 323, 760), 7: (520, 380, 560)}
T = 34                    # ≥ 10 pt con la figura a 17 cm de ancho
W, M = 1600, 20           # ancho total y margen
NAR = "#E8731A"


def foto(n, ancho):
    im = Image.open(AQUI / "fuentes" / "fotos_nudo" / f"paso_{n}.jpeg").convert("RGB").rotate(90, expand=True)
    cx, cy, w = ZOOM[n]
    h = w * im.height / im.width
    x0 = min(max(cx - w / 2, 0), im.width - w)
    y0 = min(max(cy - h / 2, 0), im.height - h)
    im = im.crop((round(x0), round(y0), round(x0 + w), round(y0 + h)))
    alto = round(ancho * im.height / im.width)
    b = io.BytesIO()
    im.resize((ancho * 2, alto * 2), Image.LANCZOS).save(b, "JPEG", quality=88)
    return base64.b64encode(b.getvalue()).decode(), alto


def main():
    capas = []

    def texto(x, y, t, tam=T, peso="normal", ancla="start", color="#1A1A1A"):
        for i, r in enumerate(t.split("\n")):
            capas.append(f'<text x="{x}" y="{y + i * (tam + 8)}" font-size="{tam}" font-weight="{peso}" text-anchor="{ancla}" fill="{color}">{r}</text>')

    def celda(n, x, y, ancho):
        datos, alto = foto(n, ancho)
        capas.append(f'<image x="{x}" y="{y}" width="{ancho}" height="{alto}" href="data:image/jpeg;base64,{datos}"/>')
        capas.append(f'<rect x="{x}" y="{y}" width="{ancho}" height="{alto}" fill="none" stroke="#9AA0A6" stroke-width="1.5"/>')
        capas.append(f'<circle cx="{x + 34}" cy="{y + 34}" r="24" fill="{NAR}" stroke="#FFFFFF" stroke-width="3"/>')
        texto(x + 34, y + 45, str(n), 32, "bold", "middle", "#FFFFFF")
        return alto

    ancho = (W - 2 * M - 2 * 30) // 3
    y = M
    for fila in range(2):
        for col in range(3):
            n = fila * 3 + col + 1
            x = M + col * (ancho + 30)
            alto = celda(n, x, y, ancho)
            texto(x, y + alto + 44, PASOS[n - 1])
        y += alto + 44 + 2 * (T + 8) + 30
    # paso final más grande, con su leyenda al costado
    grande = 2 * ancho + 30
    alto = celda(7, M, y, grande)
    texto(M + grande + 30, y + 60, "Nudo terminado", T, "bold")
    texto(M + grande + 30, y + 110, "Peinar y apretar\ntirando de los\ncuatro ramales.\n\nChicote de\n3 a 5 cm.")
    H = y + alto + M
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="Arial, Liberation Sans, Helvetica, sans-serif"><rect width="{W}" height="{H}" fill="#FFFFFF"/>'
           + "".join(capas) + "</svg>")
    (AQUI / "img" / "nudo_ocho.svg").write_text(svg, encoding="utf8")
    print(f"img/nudo_ocho.svg ({W} × {H})")


if __name__ == "__main__":
    main()
