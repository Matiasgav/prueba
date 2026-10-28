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
    "faraday": rf"v_t=\dfrac{{2\pi\,f\,\Phi_{m_}}}{{\sqrt{{2}}}}=\dfrac{{\pi\,f\,\Phi_a}}{{\sqrt{{2}}}}{Q_}\mathrm{{con}}{Q_}\Phi_{m_}=\dfrac{{\Phi_a}}{{2}}",
    "fem": rf"\Phi_a=\dfrac{{V_L/\sqrt{{3}}}}{{4{{,}}44\,K\,T_{{{ph}}}\,f}}",
    "vt": rf"v_t=\dfrac{{0{{,}}04\,\pi\,V_L}}{{4{{,}}44\,\sqrt{{3}}\,\sqrt{{2}}\,K\,T_{{{ph}}}}}=\dfrac{{0{{,}}04\,V_L}}{{2\sqrt{{3}}\,K\,T_{{{ph}}}}}",
    "practica": rf"v_t\approx 12{{,}}5\,\dfrac{{V_L\,[\mathrm{{kV}}]}}{{T_{{{ph}}}}}{Q_}[\mathrm{{V/espira}}]",
    "q": rf"q=\dfrac{{Z}}{{3\,p}}{Q_}{Q_}\tau=\dfrac{{Z}}{{p}}",
    "k": rf"k_d=\dfrac{{{sen}(q\,\pi/Z)}}{{q\;{sen}(\pi/Z)}}{Q_}{Q_}k_p={sen}\left(\dfrac{{y}}{{\tau}}\,\dfrac{{\pi}}{{2}}\right){Q_}{Q_}K=k_d\,k_p",
    "tph": rf"T_{{{ph}}}=\dfrac{{Z\,b\,n}}{{6\,a}}",
    "yugo": rf"v_t=4{{,}}44\,f\cdot 0{{,}}04\,B_{{{nom}}}\,h_y\,l_{{{Fe}}}{Q_}\mathrm{{con}}{Q_}h_y=\dfrac{{d_{{{ext}}}-d_{{{int_}}}}}{{2}}-h_r{Q_}l_{{{Fe}}}=l-N_v\,l_v",
    "rotor": rf"v_t=4{{,}}44\,f\cdot 0{{,}}04\,B_g\,\dfrac{{\pi\,d_r\,l}}{{8}}",
    "vvar": rf"V_{{{var}}}=N\,v_t",
    "fmm": rf"N\,I_{{{m_}}}=H\,\pi\,d_{{{m_}}}{Q_}\mathrm{{con}}{Q_}d_{{{m_}}}=\dfrac{{d_{{{ext}}}+d_{{{int_}}}}}{{2}}",
    "q_reac": rf"Q=V_{{{var}}}\,I_{{{m_}}}=v_t\,H\,\pi\,d_{{{m_}}}",
    "pfe": rf"m=\rho\,\dfrac{{\pi\,(d_{{{ext}}}^2-d_{{{int_}}}^2)}}{{4}}\,l_{{{Fe}}}{Q_}{Q_}P_{{{Fe}}}=p_{{{Fe}}}\,m",
    "s": rf"S=\sqrt{{Q^2+P_{{{Fe}}}^2}}{Q_}{Q_}I_{{{var}}}=\dfrac{{S}}{{V_{{{var}}}}}=\dfrac{{S}}{{N\,v_t}}",
    "n": rf"\dfrac{{S}}{{v_t\,I_{{{mx}}}}}\;\leq\;N\;\leq\;\dfrac{{V_{{{var},{mx}}}}}{{v_t}}",
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
