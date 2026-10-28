"""Ecuaciones del anexo 00503-00-EPG002 renderizadas con mathtext (matplotlib) como PNG a 600 dpi.

Se insertan como imagen para que se vean iguales en Word, LibreOffice y PDF.
Salida: img/ec/<id>.png y img/ec/medidas.json (ancho y alto en píxeles).
Uso: python3 ecuaciones.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

matplotlib.rcParams["mathtext.fontset"] = "cm"
DPI = 600
SALIDA = Path(__file__).parent / "img" / "ec"

ph, nom, Fe, var, ext, int_, m_, mx = (r"\mathrm{ph}", r"\mathrm{nom}", r"\mathrm{Fe}", r"\mathrm{var}",
                                        r"\mathrm{ext}", r"\mathrm{int}", r"\mathrm{m}", r"\mathrm{m\acute{a}x}")
sen = r"\mathrm{sen}"
Q_ = r"\quad"

ECUACIONES = {
    "flujo": rf"\Phi=\Phi_{{{m_}}}\,{sen}(2\pi f t)",
    "faraday": rf"v_t=-\dfrac{{d\Phi}}{{dt}}=-2\pi f\,\Phi_{{{m_}}}\cos(2\pi f t)",
    "eficaz": rf"v_t=\dfrac{{2\pi f\,\Phi_{{{m_}}}}}{{\sqrt{{2}}}}",
    "mitad": rf"\Phi_{{{m_}}}=\dfrac{{\Phi_a}}{{2}}{Q_}\Rightarrow{Q_}v_t=\dfrac{{\pi f\,\Phi_a}}{{\sqrt{{2}}}}=2{{,}}22\,f\,\Phi_a",
    "v4": rf"v_{{4\%}}=0{{,}}0888\,f\,\Phi_a",
    "fem": rf"\Phi_a=\dfrac{{V_l/\sqrt{{3}}}}{{4{{,}}44\,K\,T_{{{ph}}}\,f}}",
    "vt": rf"v_t=0{{,}}0888\,f\,\dfrac{{V_l/\sqrt{{3}}}}{{4{{,}}44\,K\,T_{{{ph}}}\,f}}=0{{,}}04\,\dfrac{{V_l}}{{\sqrt{{3}}\,K\,2\,T_{{{ph}}}}}",
    "practica": rf"v_t\approx 12{{,}}5\,\dfrac{{V_l\,[\mathrm{{kV}}]}}{{T_{{{ph}}}}}{Q_}[\mathrm{{V/espira}}]",
}



def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    medidas = {}
    for nombre, tex in ECUACIONES.items():
        fig = plt.figure()
        fig.text(0, 0, f"${tex}$", fontsize=12)
        archivo = SALIDA / f"{nombre}.png"
        fig.savefig(archivo, dpi=DPI, bbox_inches="tight", pad_inches=0.03, facecolor="white")
        plt.close(fig)
        from PIL import Image
        with Image.open(archivo) as im:
            medidas[nombre] = list(im.size)
    (SALIDA / "medidas.json").write_text(json.dumps({"dpi": DPI, "ecuaciones": medidas}, indent=1))
    print(f"{len(medidas)} ecuaciones en {SALIDA}")


if __name__ == "__main__":
    main()
