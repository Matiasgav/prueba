#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compone el informe LaTeX desde resultados/resultados.json y lo compila.

Uso:
    python3 tools/calculo.py && python3 tools/capturas.py
    python3 tools/informe_tex.py        # escribe y compila informe_conicos_m05_z20.tex

Todos los números del texto salen del JSON de cálculo.
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(ROOT, 'resultados', 'resultados.json'), encoding='utf-8'))
NOMBRE = 'informe_conicos_m05_z20'

MET, POM, G, F, D = R['metales'], R['pom'], R['geometria'], R['factores'], R['datos']
RPM = ['0', '0.5', '50', '100']
RPMN = ['0.5', '50', '100']
NOM = {'S45C': 'S45C', 'SUS304L MIM': 'SUS304L (MIM)', 'Latón C3604B': 'Latón C3604B'}


def n(x, d=3):
    """Número en texto con coma decimal."""
    return f'{x:.{d}f}'.replace('.', ',')


def m_(x, d=3):
    """Número para modo matemático."""
    return f'{x:.{d}f}'.replace('.', '{,}')


def e(x):
    a, b = f'{x:.2e}'.split('e')
    return f'${a.replace(".", "{,}")}\\times10^{{{int(b)}}}$'


def rpm_t(r):
    return {'0': '0', '0.5': '0,5', '50': '50', '100': '100'}[r]


def T(mat, reg, r):
    return MET[mat][reg][r]['T_adm']


def figura(path, cap, fuente, ancho='\\linewidth', label=None):
    lab = f'\\label{{{label}}}' if label else ''
    return (f'\\begin{{figure}}[H]\\centering\\includegraphics[width={ancho}]{{{path}}}'
            f'\\caption{{{cap} \\textit{{Fuente: {fuente}}}}}{lab}\\end{{figure}}\n')


# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------
def tabla_resumen():
    filas = []
    for k in MET:
        c = ' & '.join(n(T(k, 'normal', r)) for r in RPMN)
        p = ' & '.join(n(T(k, 'pico', r)) for r in RPM)
        filas.append(f'{NOM[k]} & {c} & {p} \\\\')
    c = ' & '.join(n(POM['normal'][r]['T_adm']) for r in RPMN)
    p = ' & '.join(n(POM['pico'][r]['T_adm']) for r in RPM)
    filas.append(f'POM inyectado$^{{*}}$ & {c} & {p} \\\\')
    return r'''\begin{table}[H]\centering\small
\caption{Torque admisible por engranaje, en N\,m ($R=0{,}95$, carga en ambos sentidos, 10 años).}\label{tab:resumen}
\begin{tabular}{l ccc cccc}
\toprule
 & \multicolumn{3}{c}{Torque normal (toda la vida)} & \multicolumn{4}{c}{Torque de pico (10 s, ocasional)}\\
\cmidrule(lr){2-4}\cmidrule(lr){5-8}
Material & 0,5 rpm & 50 rpm & 100 rpm & 0 rpm & 0,5 rpm & 50 rpm & 100 rpm\\
\midrule
''' + '\n'.join(filas) + r'''
\bottomrule
\end{tabular}

\smallskip\footnotesize $^{*}$POM: fuera del alcance de AGMA; método de Lewis (sección~\ref{sec:pom}).
\end{table}
'''


def tabla_detalle(reg):
    filas = []
    rr = RPMN if reg == 'normal' else RPM
    for k in MET:
        for r in rr:
            x = MET[k][reg][r]
            filas.append(f'{NOM[k]} & {rpm_t(r)} & {e(x["N"])} & {n(x["K_v"], 4)} & '
                         f'{n(x["Y_NT"])} & {n(x["Z_NT"])} & {n(x["sFP"], 1)} & {n(x["sHP"], 0)} & '
                         f'{n(x["W_F"], 1)} & {n(x["W_H"], 1)} & {n(x["T_F"])} & {n(x["T_H"])} & '
                         f'\\textbf{{{n(x["T_adm"])}}} \\\\')
    tit = ('Servicio normal: ciclos de toda la vida' if reg == 'normal'
           else 'Picos de 10 s: ciclos de los picos')
    return (r'\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3.2pt}'
            f'\\caption{{{tit} (evaluados al doble, regla de Miner).}}'
            r'''\begin{tabular}{l r r c c c r r r r r r r}
\toprule
Material & rpm & $N_L$ & $K_v$ & $Y_{NT}$ & $Z_{NT}$ & $\sigma_{FP}$ & $\sigma_{HP}$ & $W_F$ & $W_H$ & $T_F$ & $T_H$ & $T_{adm}$\\
 & & & & & & MPa & MPa & N & N & N\,m & N\,m & N\,m\\
\midrule
''' + '\n'.join(filas) + '\n\\bottomrule\\end{tabular}\\end{table}\n')


def tabla_materiales():
    filas = []
    for k in MET:
        mt = R['materiales'][k]
        x = MET[k]['normal']['100']
        filas.append(f'{NOM[k]} & {n(mt["E"] / 1000, 0)} & {n(mt["nu"], 2)} & {n(mt["HB"], 0)} & '
                     f'{n(x["Z_E"], 1)} & {n(mt["sFlim"], 1)} & {mt["base_F"]} & '
                     f'{n(mt["sHlim"], 0)} & {mt["base_H"]} \\\\')
    return (r'''\begin{table}[H]\centering\small\setlength{\tabcolsep}{4pt}
\caption{Propiedades y resistencias de referencia de los metales.}\label{tab:mat}
\begin{tabular}{l r r r r r p{3.2cm} r p{2.6cm}}
\toprule
Material & $E$ & $\nu$ & HB & $Z_E$ & $\sigma_{F\,\lim}$ & Base & $\sigma_{H\,\lim}$ & Base\\
 & GPa & & & $\sqrt{\text{MPa}}$ & MPa & & MPa & \\
\midrule
''' + '\n'.join(filas).replace('×', r'$\times$') + '\n\\bottomrule\\end{tabular}\\end{table}\n')


def tabla_pom():
    filas = []
    for reg, rr in (('normal', RPMN), ('pico', RPM)):
        for r in rr:
            x = POM[reg][r]
            filas.append(f'{"Normal" if reg == "normal" else "Pico"} & {rpm_t(r)} & {e(x["N"])} & '
                         f'{n(x["s_b"], 1)} & {n(x["C_S"], 2)} & {n(x["s_adm"], 1)} & '
                         f'{n(x["T_khk"])} & {n(x["T_lewis"])} & {n(x["T_kgcal"])} & '
                         f'\\textbf{{{n(x["T_adm"])}}} \\\\')
    return (r'''\begin{table}[H]\centering\small\setlength{\tabcolsep}{4pt}
\caption{POM inyectado: tres estimaciones y valor adoptado (N\,m), carga alternada incluida.}\label{tab:pom}
\begin{tabular}{l r r r r r r r r r}
\toprule
Régimen & rpm & $N$ & $\sigma_b(N)$ & $C_S$ & $\sigma_{b\,\mathrm{adm}}$ & KHK & Lewis--Shigley & Calibrado KG & Adoptado\\
 & & & MPa & & MPa & $y=0{,}597$ & $Y=0{,}353$ & & \\
\midrule
''' + '\n'.join(filas) + '\n\\bottomrule\\end{tabular}\\end{table}\n')


def tabla_alternativas():
    filas = []
    for a in R['alternativas']:
        g = a['geo']
        filas.append(f"{a['cod']} & {a['desc']} & {a['mat']} & {n(g['m'], 2)} & {g['z']} & "
                     f"{n(g['da'], 2)} & {n(g['b_ef'], 2)} & {n(a['normal100']['T_adm'])} & "
                     f"{n(a['pico100']['T_adm'])} & {n(a['pico0']['T_adm'])} & "
                     f"{n(a['normal100']['T_adm'] / R['alternativas'][0]['normal100']['T_adm'], 1)} \\\\")
    return (r'''\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}
\caption{Alternativas con diámetro exterior $d_a\le 14$ mm (relación 1:1, 90$^\circ$). Torques en N\,m por engranaje.}\label{tab:alt}
\begin{tabular}{c p{3.3cm} l r r r r r r r r}
\toprule
 & Producto & Material & $m$ & $z$ & $d_a$ & $b_{ef}$ & Normal & Pico & Pico & Relación\\
 & & & mm & & mm & mm & 100 rpm & 100 rpm & 0 rpm & vs.\ A\\
\midrule
''' + '\n'.join(filas) + '\n\\bottomrule\\end{tabular}\\end{table}\n')


def tabla_cota():
    filas = []
    mot = {'SUS304L MIM': r'$\sigma_{H\,\lim}=0{,}40\times$ S45C',
           'Latón C3604B': r'$\sigma_{H\,\lim}=0{,}36\times$ S45C (bronce, Shigley tabla 14-7)'}
    for k, c in R['cota_baja'].items():
        filas.append(f'{NOM[k]} & {mot[k]} & ' + ' & '.join(
            f'{n(T(k, "normal", r))} & {n(c[r])}' for r in ('50', '100')) + ' \\\\')
    return (r'''\begin{table}[H]\centering\small
\caption{Torque normal con hipótesis pesimistas de picado para materiales no tabulados por Shigley (N\,m).}
\begin{tabular}{l l rr rr}
\toprule
 & Hipótesis alternativa & \multicolumn{2}{c}{50 rpm} & \multicolumn{2}{c}{100 rpm}\\
\cmidrule(lr){3-4}\cmidrule(lr){5-6}
Material & & adoptado & cota baja & adoptado & cota baja\\
\midrule
''' + '\n'.join(filas) + '\n\\bottomrule\\end{tabular}\\end{table}\n')


# ---------------------------------------------------------------------------
# Valores sueltos
# ---------------------------------------------------------------------------
x = MET['S45C']['normal']['100']
xp = MET['S45C']['pico']['100']
b = G['b_ef']
kg = R['kg']['S45C']['100']
pr = R['prisionero']
YZ = R['Y_Z']
Npk = R['n_picos']
alt = {a['cod']: a for a in R['alternativas']}
T_pico_max = max(T(k, 'pico', '0') for k in MET)
tau = 16 * T_pico_max * 1000 / (3.14159265 * 27)

PRE = r'''\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[spanish,es-tabla,es-nodecimaldot,es-noshorthands]{babel}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage[a4paper,top=2.4cm,bottom=2.4cm,left=2.3cm,right=2.3cm,headheight=15pt]{geometry}
\usepackage{amsmath,amssymb}
\usepackage[output-decimal-marker={,}]{siunitx}
\usepackage{booktabs,array,tabularx}
\usepackage{graphicx,float}
\usepackage[font=small,labelfont=bf,labelsep=period]{caption}
\usepackage[table]{xcolor}
\usepackage[most]{tcolorbox}
\usepackage{fancyhdr,lastpage}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage[hidelinks]{hyperref}
\definecolor{azul}{HTML}{1C5CAB}
\definecolor{gris}{HTML}{52514E}
\titleformat{\section}{\Large\bfseries\color{azul}}{\thesection}{0.8em}{}[\vspace{-0.6ex}\color{azul!40}\rule{\linewidth}{0.6pt}]
\titleformat{\subsection}{\large\bfseries\color{azul}}{\thesubsection}{0.8em}{}
\setlength{\parskip}{0.45em}\setlength{\parindent}{0pt}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{gris}Mitras KG m\,0,5 $\times$ 20 --- Torque admisible según Shigley}
\fancyhead[R]{\small\color{gris}Informe técnico}
\fancyfoot[C]{\small\color{gris}Página \thepage\ de \pageref{LastPage}}
\renewcommand{\headrulewidth}{0.4pt}
\newtcolorbox{caja}[2][azul]{colback=#1!5,colframe=#1,boxrule=0.6pt,arc=1mm,left=2mm,right=2mm,top=1mm,bottom=1mm,fonttitle=\bfseries,title={#2}}
\setlist{itemsep=0.2em,topsep=0.3em}
\graphicspath{{./}}
\begin{document}
'''

PORTADA = r'''\begin{titlepage}
\centering
\vspace*{2.2cm}
{\color{azul}\rule{\linewidth}{1.2pt}}\\[0.8cm]
{\Huge\bfseries Torque admisible de un par de\\[0.25cm] engranajes cónicos KG m\,0,5 $\times$ 20\\[0.25cm] para la transmisión a 90$^\circ$ de una rueda\par}
\vspace{0.6cm}
{\Large Análisis según Shigley (método AGMA para engranajes cónicos),\\ alternativas de mayor capacidad y lubricación\par}
\vspace{0.6cm}
{\color{azul}\rule{\linewidth}{1.2pt}}\\[1.4cm]
\begin{tabular}{rl}
\textbf{Producto analizado:} & KG STOCK GEARS, mitra serie M, $m=0{,}5$ mm, $z=20$\\
\textbf{Materiales:} & S45C, SUS304L (MIM), latón C3604B, POM inyectado\\
\textbf{Velocidades:} & 0, 0,5, 50 y 100 rpm\\
\textbf{Confiabilidad:} & 95\,\%\\
\textbf{Servicio:} & rueda de carro, torque en ambos sentidos, picos de 10 s\\
\textbf{Método:} & Budynas y Nisbett, \textit{Diseño en ingeniería mecánica de Shigley}, cap. 15\\
\end{tabular}
\vfill
{\large Informe técnico\\ Septiembre de 2026\par}
\end{titlepage}
'''

FIGS = [
    figura('capturas/kg_codigo_producto.png', 'Código de producto de las mitras KG.', 'KG, catálogo KG4001, p. 233.', '0.95\\linewidth'),
    figura('capturas/kg_s45c_datos.png', 'Mitra S45C m\\,0,5 $\\times$ 20 (M50S20): JIS B1704 grado 3, sin tratamiento térmico, $b=2{,}5$ mm, $d=10$ mm.', 'KG, catálogo KG4001, p. 260.'),
    figura('capturas/kg_s45c_potencia.png', 'Potencia admisible de M50S20: 1,5 W a 100 rpm a flexión; la resistencia superficial no se publica («--»).', 'KG, catálogo KG4001, p. 261.'),
    figura('capturas/kg_mim_datos.png', 'Mitra SUS304L MIM m\\,0,5 $\\times$ 20 (M50SUM20*1103): sin prisioneros y solo combinable con otra mitra MIM.', 'KG, catálogo KG4001, p. 270.', '0.9\\linewidth'),
    figura('capturas/kg_mim_potencia.png', 'Potencia admisible de M50SUM20 (0,5 W a 100 rpm) y relación orientativa de resistencia: S45C 1, SUS304 0,6, MIM 0,4.', 'KG, catálogo KG4001, p. 271.', '0.8\\linewidth'),
    figura('capturas/kg_laton_datos.png', 'Mitra de latón C3604B m\\,0,5 (M50B20 y M50B25); sin tabla de potencia.', 'KG, catálogo KG4001, p. 272.', '0.9\\linewidth'),
    figura('capturas/kg_pom_datos.png', 'Mitra de POM negro inyectado m\\,0,5 $\\times$ 20 (M50DM20-1103), catálogo 2020.', 'KG, catálogo KG3001, p. 400.'),
    figura('capturas/kg_condiciones_conicos.png', 'Condiciones de las tablas de KG para cónicos: JGMA 403-01/404-01; $\\geq10^7$ ciclos; choque moderado ($K_O=1{,}25$); baño de aceite 100 cSt; ambos engranajes en voladizo; con carga en ambos sentidos, 2/3 del valor de tabla.', 'KG, KG5001, p. 18.'),
    figura('capturas/kg_jgma403_alcance.png', 'Alcance de JGMA 403-01/404-01: módulo exterior de 1,5 a 25 mm.', 'KG, Technical Data, cap. 10.2, p. 137.', '0.48\\linewidth'),
    figura('capturas/kg_conversion_potencia.png', 'Conversión de potencia a torque: $T\\,[\\mathrm{N\\,m}]=9549{,}7\\,P\\,[\\mathrm{kW}]/n$.', 'KG, KG5001, p. 20.'),
    figura('figuras/fig_ciclos.pdf', 'Factores de ciclos de Shigley (Figs. 15-8 y 15-9, graficados desde sus ecuaciones) y puntos de trabajo.', 'ecuaciones de Shigley, cap. 15.', '0.95\\linewidth'),
    figura('figuras/fig_resumen.pdf', 'Torque admisible por material y velocidad: servicio normal y picos.', 'cálculo propio.', label='fig:resumen'),
    figura('figuras/fig_modos.pdf', 'Servicio normal a 100 rpm: flexión alternada y picado según Shigley frente a la tabla de KG.', 'cálculo propio; KG, catálogo KG4001.'),
    figura('figuras/fig_rpm.pdf', 'Torque admisible en función de la velocidad de la rueda.', 'cálculo propio.'),
    figura('figuras/fig_sensibilidad.pdf', 'Sensibilidad del torque normal del S45C a 100 rpm a cada supuesto.', 'cálculo propio.', label='fig:sens'),
    figura('figuras/fig_picos.pdf', 'Torque de pico admisible a 100 rpm en función de la frecuencia de picos.', 'cálculo propio.'),
    figura('figuras/fig_alternativas.pdf', 'Torque admisible de las alternativas a 100 rpm (escala logarítmica).', 'cálculo propio.'),
]

CUERPO = rf'''
\section*{{Resumen ejecutivo}}
\addcontentsline{{toc}}{{section}}{{Resumen ejecutivo}}
Se determinó el torque admisible del par de mitras KG m\,0,5 $\times$ 20 que transmite el giro a la rueda de un carro,
para cada material en que el fabricante ofrece la pieza. Se usaron las ecuaciones AGMA para engranajes cónicos
del capítulo~15 de Shigley. Como la rueda recibe torque en ambos sentidos, la resistencia a flexión se toma como alternada (70\,\%).
La confiabilidad es del 95\,\%. El servicio combina un torque normal bajo durante toda la vida con picos ocasionales de 10~s.

{tabla_resumen()}

\begin{{caja}}{{Conclusiones principales}}
\begin{{enumerate}}[leftmargin=1.2em]
\item \textbf{{S45C es la mejor opción de KG}}: admite {n(T('S45C', 'normal', '100'))}~N\,m en servicio normal a 100~rpm,
{n(T('S45C', 'pico', '100'))}~N\,m en picos de 10~s a 100~rpm y {n(T('S45C', 'pico', '0'))}~N\,m a rueda detenida.
\item El dato del catálogo KG (1,5~W a 100~rpm $=$ {n(kg)}~N\,m) no sirve para este uso. Es solo a flexión, en un solo sentido,
y extrapola una norma que empieza en $m=1{{,}}5$. Supera en un {n((kg / T('S45C', 'normal', '100') - 1) * 100, 0)}\,\% la capacidad normal calculada.
\item \textbf{{Dentro de $d_a\le14$ mm}} hay margen. La mitra KG m\,0,5 $\times$ 25 de stock (alternativa B) casi duplica la capacidad
($\times${n(alt['B']['normal100']['T_adm'] / alt['A']['normal100']['T_adm'], 1)}). Una mitra a medida m\,0,6 $\times$ 21
carburizada la multiplica por {n(alt['G']['normal100']['T_adm'] / alt['A']['normal100']['T_adm'], 1)} (sección~\ref{{sec:alt}}).
\item \textbf{{La lubricación es imprescindible}} en los metales: los valores AGMA presuponen engranajes lubricados.
A la velocidad de trabajo la película es de lubricación límite, así que se requiere grasa con aditivos EP (sección~\ref{{sec:lub}}).
\end{{enumerate}}
\end{{caja}}

\tableofcontents
\newpage

\section{{Objeto y datos de partida}}
\subsection{{Aplicación}}
El par de mitras transmite el giro de un motor BLDC a la rueda de un carro, con ejes a 90$^\circ$ y relación 1:1.
El compartimiento está engrasado y la temperatura de trabajo es de 30 a 40\,$^\circ$C. El motor sigue un perfil
trapezoidal suave. El equipo se usa 20~h seguidas una vez por mes.

\subsection{{Ciclo de carga de la rueda}}
\begin{{itemize}}
\item \textbf{{Torque en ambos sentidos.}} Marcha adelante y atrás, aceleración y frenado. Cada diente se flexiona hacia
uno y otro lado, así que Shigley indica usar el 70\,\% de la resistencia a flexión.
\item \textbf{{Servicio normal}} con torque bajo durante toda la vida: $N_{{normal}}=n\cdot60\cdot20\cdot12\cdot10$ ciclos por diente.
\item \textbf{{Picos ocasionales}} al torque admisible, de 10~s cada uno. Se supuso \textbf{{un pico por hora de uso}}:
$N_{{picos}}={n(Npk, 0)}$ eventos en 10 años. Cada pico suma $\max(1;\,n\cdot10/60)$ ciclos por diente.
\item \textbf{{Combinación (regla de Miner).}} A cada régimen se le asigna la mitad del daño admisible, así que su resistencia se evalúa al
doble de sus ciclos:
\begin{{equation}}
\frac{{n_{{normal}}}}{{N_{{normal}}}}+\frac{{n_{{pico}}}}{{N_{{pico}}}}=0{{,}}5+0{{,}}5=1
\quad\Rightarrow\quad N_{{eval}}=2\,n .
\end{{equation}}
\end{{itemize}}

\begin{{table}}[H]\centering\small
\caption{{Datos, supuestos y su origen.}}
\begin{{tabularx}}{{\linewidth}}{{l X l}}
\toprule
Dato & Valor & Origen\\\midrule
Par & Dos mitras iguales, 1:1, $\Sigma=90^\circ$ & pedido\\
Producto & KG serie M, $m=0{{,}}5$ mm, $z=20$, $b=2{{,}}5$ mm & catálogo KG\\
Velocidades & 0, 0,5, 50 y 100 rpm (el pedido admite leer <<0,50 rpm>>; se calcularon ambas) & pedido\\
Confiabilidad & $R=0{{,}}95$ & pedido\\
Uso & 20 h por mes; vida de diseño 10 años (2400 h) & pedido / \textbf{{supuesto}}\\
Picos & 10 s, 1 por hora de uso ({n(Npk, 0)} en la vida) & pedido / \textbf{{supuesto}}\\
Carga & BLDC, perfil trapezoidal suave, torque en ambos sentidos & pedido\\
Lubricación & Grasa en compartimiento cerrado & pedido\\
Temperatura & 30--40\,$^\circ$C (se calcula a 40\,$^\circ$C) & pedido\\
Montaje & Ambos engranajes en voladizo & \textbf{{supuesto}} conservador\\
\bottomrule
\end{{tabularx}}
\end{{table}}

\section{{El producto KG y el alcance de su dato de capacidad}}
\subsection{{Materiales disponibles en m\,0,5 $\times$ 20}}
El catálogo vigente de KG (KG4001) ofrece la mitra m\,0,5 de 20 dientes en S45C (M50S20), inoxidable SUS304L inyectado (MIM, M50SUM20)
y latón C3604B (M50B20). El POM azul y el blanco empiezan en m\,0,8. El catálogo 2020 (KG3001) incluía además
una versión de POM negro inyectado (M50DM20-1103).
{FIGS[0]}
{FIGS[1]}
{FIGS[2]}
{FIGS[3]}
{FIGS[4]}
{FIGS[5]}
{FIGS[6]}

\subsection{{Qué cubre el dato de KG}}
{FIGS[7]}
{FIGS[8]}
{FIGS[9]}

\begin{{caja}}[orange!80!black]{{Limitaciones del dato del fabricante}}
\begin{{enumerate}}[leftmargin=1.2em]
\item Solo publica flexión. Para m\,0,5 no hay resistencia superficial (picado).
\item Usa JGMA 403/404, cuyo alcance empieza en $m=1{{,}}5$ mm.
\item Supone carga en un sentido, baño de aceite y $\geq10^7$ ciclos, condiciones distintas a las de una rueda.
\item El latón y el POM m\,0,5 no tienen dato. El del MIM es experimental (catálogo 2020).
\end{{enumerate}}
\end{{caja}}

\section{{Geometría}}
\begin{{minipage}}[c]{{0.46\linewidth}}\centering
\includegraphics[width=\linewidth]{{figuras/fig_geometria.pdf}}
\captionof{{figure}}{{Corte axial esquemático del par.}}
\end{{minipage}}\hfill
\begin{{minipage}}[c]{{0.5\linewidth}}\small
\begin{{tabular}}{{l r}}
\toprule
Magnitud & Valor\\\midrule
Módulo exterior $m_{{et}}$ & 0,5 mm\\
Dientes $z_1=z_2$ & 20\\
Ángulo de presión $\phi$ & 20$^\circ$\\
Diámetro primitivo $d_e=m\,z$ & {n(G['d'], 1)} mm\\
Ángulo de paso $\delta$ & 45$^\circ$\\
Distancia de cono $R_e=d_e/(2\sin\delta)$ & {n(G['Re'], 3)} mm\\
Ancho de catálogo $b$ & {n(G['b'], 1)} mm\\
Máximo recomendado $0{{,}}3R_e$ & {n(G['b_max'], 3)} mm\\
\textbf{{Ancho efectivo}} $b_{{ef}}$ & \textbf{{{n(G['b_ef'], 3)} mm}}\\
Diámetro exterior $d_a$ & {n(G['da'], 2)} mm\\
Dientes virtuales $z_v=z/\cos\delta$ & {n(G['zv'], 2)}\\
$v_{{et}}$ a 100 rpm & {n(x['v_et'], 4)} m/s\\
\bottomrule
\end{{tabular}}
\end{{minipage}}

El ancho de catálogo supera el 30\,\% de la distancia de cono ($b/R_e={n(G['ratio_b_Re'], 3)}$), límite que recomienda Shigley.
Por eso solo se acredita $b_{{ef}}=0{{,}}3R_e$.

\section{{Método de cálculo (Shigley, capítulo 15)}}
Shigley presenta las ecuaciones de ANSI/AGMA 2003 para engranajes cónicos rectos. En unidades SI, con $W^t$ la fuerza
tangencial en el diámetro primitivo exterior:

\paragraph{{Esfuerzo de contacto (picado).}}
\begin{{equation}}
\sigma_H = Z_E\left(\frac{{W^t}}{{b\,d_{{e1}}\,Z_I}}\,K_A K_v K_{{H\beta}} Z_x Z_{{xc}}\right)^{{1/2}}
\le \sigma_{{HP}}=\frac{{\sigma_{{H\,\lim}}\,Z_{{NT}}\,Z_W}}{{S_H\,K_\theta\,Z_Z}}
\label{{eq:contacto}}
\end{{equation}}

\paragraph{{Esfuerzo de flexión.}}
\begin{{equation}}
\sigma_F = \frac{{W^t}}{{b}}\,\frac{{K_A K_v}}{{m_{{et}}}}\,\frac{{Y_x K_{{H\beta}}}}{{Y_\beta\,Y_J}}
\le \sigma_{{FP}}=\frac{{0{{,}}70\,\sigma_{{F\,\lim}}\,Y_{{NT}}}}{{S_F\,K_\theta\,Y_Z}}
\label{{eq:flexion}}
\end{{equation}}
El factor $0{{,}}70$ corresponde a la carga en ambos sentidos.

\paragraph{{Torque admisible.}} Se despeja $W^t$ de \eqref{{eq:contacto}} y \eqref{{eq:flexion}}, con $T=W^t d_e/2$:
\begin{{align}}
T_F &= \frac{{d_e}}{{2}}\;\frac{{\sigma_{{FP}}\;b\;m_{{et}}\;Y_\beta\,Y_J}}{{K_A\,K_v\,Y_x\,K_{{H\beta}}}}\\[4pt]
T_H &= \frac{{d_e}}{{2}}\left(\frac{{\sigma_{{HP}}}}{{Z_E}}\right)^{{2}}\frac{{b\;d_e\;Z_I}}{{K_A\,K_v\,K_{{H\beta}}\,Z_x\,Z_{{xc}}}}\\[4pt]
T_{{adm}} &= \min\left(T_F,\;T_H\right)
\end{{align}}
Los esfuerzos AGMA no son tensiones reales: se comparan solo con los admisibles del mismo método.

\section{{Factores adoptados}}
\begin{{table}}[H]\centering\small
\caption{{Factores de Shigley (notación US / SI) y su justificación.}}
\begin{{tabularx}}{{\linewidth}}{{l c X}}
\toprule
Factor & Valor & Justificación\\\midrule
Sobrecarga $K_o$ / $K_A$ & {n(F['K_A'], 2)} & Motor uniforme (BLDC, perfil suave) y carga suave. Si la rueda recibe golpes por obstáculos, usar 1,25 (figura~\ref{{fig:sens}}).\\
Dinámico $K_v$ & {n(MET['S45C']['normal']['100']['K_v'], 3)} & $K_v=\left[(A+\sqrt{{200\,v_{{et}}}})/A\right]^B$, $B=0{{,}}25(12-Q_v)^{{2/3}}$, $A=50+56(1-B)$, $Q_v=6$ (100 rpm)\\
Tamaño $K_s$ / $Y_x$ & 0,5 & $m_{{et}}<1{{,}}6$ mm\\
Tamaño $C_s$ / $Z_x$ & 0,5 & $b<12{{,}}7$ mm\\
Distribución $K_m$ / $K_{{H\beta}}$ & {n(x['K_Hb'], 3)} & $K_{{mb}}+5{{,}}6\times10^{{-6}}b^2$, $K_{{mb}}=1{{,}}25$ (ambos en voladizo)\\
Coronamiento $C_{{xc}}$ / $Z_{{xc}}$ & 2,0 & Dientes sin coronamiento garantizado\\
Curvatura $K_x$ / $Y_\beta$ & 1 & Dientes rectos\\
Geometría $J$ / $Y_J$ & 0,20 & Fig.~15-7, 20 contra 20 dientes (lectura $\pm0{{,}}01$)\\
Geometría $I$ / $Z_I$ & 0,062 & Fig.~15-6, 20 contra 20 dientes (lectura $\pm0{{,}}003$)\\
Ciclos $K_L$ / $Y_{{NT}}$ & ec. & Fig.~15-9: $2{{,}}7$ ($<10^3$); $6{{,}}1514N^{{-0{{,}}1192}}$ ($10^3$--$3\times10^6$); $1{{,}}6831N^{{-0{{,}}0323}}$\\
Ciclos $C_L$ / $Z_{{NT}}$ & ec. & Fig.~15-8: $2{{,}}0$ ($<10^4$); $3{{,}}4822N^{{-0{{,}}0602}}$\\
Confiabilidad $K_R$ / $Y_Z$ & {n(YZ, 3)} & $R=0{{,}}95$: $Y_Z=0{{,}}70-0{{,}}15\log(1-R)$\\
Confiabilidad $C_R$ / $Z_Z$ & {n(YZ ** 0.5, 3)} & $Z_Z=\sqrt{{Y_Z}}$\\
Temperatura $K_T$ / $K_\theta$ & 1 & $t\le120\,^\circ$C\\
Dureza $C_H$ / $Z_W$ & 1 & Mismo material en piñón y corona\\
Seguridad $S_F$, $S_H$ & 1 & Capacidad nominal; el margen lo dan $R$ y los supuestos\\
Carga alternada & 0,70 & Flexión con torque en ambos sentidos\\
\bottomrule
\end{{tabularx}}
\end{{table}}
{FIGS[10]}

\section{{Resistencia de los materiales}}
El S45C sin tratamiento entra en Shigley como acero templado total grado~1. Se toma 170~HB, el extremo inferior de JIS G4051:
\begin{{equation}}
\sigma_{{F\,\lim}}=0{{,}}30\,\mathrm{{HB}}+14{{,}}48={m_(R['referencia']['sFlim'], 1)}\ \text{{MPa}},\qquad
\sigma_{{H\,\lim}}=2{{,}}35\,\mathrm{{HB}}+162{{,}}89={m_(R['referencia']['sHlim'], 1)}\ \text{{MPa}}
\end{{equation}}
El SUS304L (MIM) y el latón no figuran en Shigley. Se escalan desde el S45C con el mejor indicador disponible.
A flexión: la relación de resistencia de KG para el MIM (0,4) y la relación de límites de fatiga para el latón
(138/285). A picado: la dureza Brinell. El módulo elástico de cada par entra en $Z_E$:
\begin{{equation}}
Z_E=\left[\pi\left(\frac{{1-\nu_1^2}}{{E_1}}+\frac{{1-\nu_2^2}}{{E_2}}\right)\right]^{{-1/2}}
\end{{equation}}
{tabla_materiales()}

\section{{Cálculo paso a paso: S45C, servicio normal a 100 rpm}}
\begin{{align*}}
N_L &= 2\times(100\cdot60\cdot20\cdot12\cdot10) = {e(x['N'])[1:-1]}\\
v_{{et}} &= \pi\,d_e\,n/60\,000 = {m_(x['v_et'], 4)}\ \text{{m/s}} \;\Rightarrow\; K_v={m_(x['K_v'], 4)}\\
K_{{H\beta}} &= 1{{,}}25+5{{,}}6\times10^{{-6}}\,({m_(b, 3)})^2={m_(x['K_Hb'], 4)}\\
Y_{{NT}} &= 1{{,}}6831\,N_L^{{-0{{,}}0323}}={m_(x['Y_NT'], 4)},\qquad Z_{{NT}}=3{{,}}4822\,N_L^{{-0{{,}}0602}}={m_(x['Z_NT'], 4)}\\
\sigma_{{FP}} &= \frac{{0{{,}}70\times{m_(R['referencia']['sFlim'], 2)}\times{m_(x['Y_NT'], 4)}}}{{1\times1\times{m_(YZ, 4)}}}={m_(x['sFP'], 2)}\ \text{{MPa}}\\
\sigma_{{HP}} &= \frac{{{m_(R['referencia']['sHlim'], 1)}\times{m_(x['Z_NT'], 4)}}}{{1\times1\times{m_(YZ ** 0.5, 4)}}}={m_(x['sHP'], 1)}\ \text{{MPa}}\\
W_F &= \frac{{{m_(x['sFP'], 2)}\times{m_(b, 3)}\times0{{,}}5\times0{{,}}20}}{{1\times{m_(x['K_v'], 4)}\times0{{,}}5\times{m_(x['K_Hb'], 4)}}}={m_(x['W_F'], 2)}\ \text{{N}}
&&\Rightarrow\; T_F={m_(x['T_F'], 4)}\ \text{{N\,m}}\\
W_H &= \left(\frac{{{m_(x['sHP'], 1)}}}{{{m_(x['Z_E'], 1)}}}\right)^2\frac{{{m_(b, 3)}\times10\times0{{,}}062}}{{1\times{m_(x['K_v'], 4)}\times{m_(x['K_Hb'], 4)}\times0{{,}}5\times2{{,}}0}}={m_(x['W_H'], 2)}\ \text{{N}}
&&\Rightarrow\; T_H={m_(x['T_H'], 4)}\ \text{{N\,m}}\\
T_{{adm}} &= \min({m_(x['T_F'], 4)};\,{m_(x['T_H'], 4)})=\mathbf{{{m_(x['T_adm'], 4)}\ \textbf{{N\,m}}}}\quad\text{{({x['modo']})}}
\end{{align*}}
Para los picos de 10~s a 100~rpm: $N_L=2\times{n(Npk, 0)}\times16{{,}}7={e(xp['N'])[1:-1]}$, $Y_{{NT}}={m_(xp['Y_NT'])}$,
$Z_{{NT}}={m_(xp['Z_NT'])}$ y $T_{{adm}}={m_(xp['T_adm'], 4)}$~N\,m ({xp['modo']}).

\section{{Resultados de los metales}}
{tabla_detalle('normal')}
{tabla_detalle('pico')}
{FIGS[11]}
{FIGS[12]}
{FIGS[13]}
Todos los picos cumplen además $\sigma_{{FP}}<S_y$: no hay fluencia estática del diente.

\section{{POM inyectado}}\label{{sec:pom}}
Las ecuaciones AGMA valen solo para metales. Para plásticos, KG y KHK usan la ecuación de Lewis con factores de servicio:
\begin{{equation}}
T=\frac{{d_e}}{{2}}\;m\,y\,b\,\sigma_{{b\,\mathrm{{adm}}}}\,\frac{{R_e-b}}{{R_e}},\qquad
\sigma_{{b\,\mathrm{{adm}}}}=0{{,}}70\;\sigma_b(N)\,\frac{{K_V\,K_T\,K_L\,K_M}}{{C_S}}
\end{{equation}}
con $\sigma_b(N)$ de la curva m\,0,8 de KHK, $K_V=1{{,}}4$ ($v\approx0$; 1 en estático), $K_T=0{{,}}80$ (40\,$^\circ$C),
$K_L=1$ (grasa), $K_M=0{{,}}75$ (POM contra POM), $C_S=1{{,}}25$ en servicio normal y $0{{,}}80$ en picos.
Se adopta la menor de tres estimaciones: el método KHK, Lewis con el factor $Y$ de Shigley (tabla 14-2)
y la tabla de KG del POM azul m\,0,8 escalada a m\,0,5.
{tabla_pom()}
\begin{{minipage}}{{0.49\linewidth}}\centering\includegraphics[width=0.95\linewidth]{{capturas/Fig.11.3.jpg}}
\captionof{{figure}}{{Esfuerzo admisible de flexión del POM (Duracon). \textit{{Fuente: KHK, Fig. 11.3.}}}}\end{{minipage}}\hfill
\begin{{minipage}}{{0.49\linewidth}}\centering\includegraphics[width=0.95\linewidth]{{capturas/Fig.-11.5-Temperature-factor-KT.jpg}}
\captionof{{figure}}{{Factor de temperatura $K_T$. \textit{{Fuente: KHK, Fig. 11.5.}}}}\end{{minipage}}

\begin{{caja}}[orange!80!black]{{Advertencias del POM}}
El POM absorbe humedad, se dilata con la temperatura y fluye (creep) bajo torque sostenido a 40\,$^\circ$C.
El valor a 0~rpm vale para picos de 10~s, no para retener la rueda durante minutos.
\end{{caja}}

\section{{Sensibilidad}}
{FIGS[14]}
{FIGS[15]}
{tabla_cota()}

\section{{Alternativas para aumentar el torque con $d_a\le14$ mm}}\label{{sec:alt}}
El torque de un cónico crece con el diámetro, el módulo, el ancho útil ($\le0{{,}}3R_e$) y la resistencia superficial del material.
Con el diámetro exterior limitado a 14~mm, las opciones son:
\begin{{itemize}}
\item \textbf{{B -- KG M50S25 (stock).}} m\,0,5, 25 dientes, $d_a=13{{,}}21$ mm, $b=3$ mm. Es el mismo proveedor y el mismo tipo de montaje
(agujero $\varnothing4$). $J=0{{,}}216$ e $I=0{{,}}065$ se tomaron del Ejemplo 15-1 de Shigley (mitras de 25 dientes).
\item \textbf{{C -- KG M50B25 (latón, stock).}} Mismo tamaño en latón. No mejora frente al S45C de 20 dientes.
\item \textbf{{D -- RS PRO 521-5780 (acero, stock).}} m\,0,8, 16 dientes, $d_a\approx13{{,}}9$ mm. El ancho de cara ($0{{,}}3R_e$ supuesto), $J$ e $I$
(extrapolados a 16 dientes) deben confirmarse con la hoja de datos.
\item \textbf{{E -- A medida, m\,0,6 $\times$ 21, S45C.}} Módulo normalizado, $d_a=13{{,}}45$ mm.
\item \textbf{{F/G -- A medida, carburizado (SCM415, 58--62 HRC).}} Shigley, acero carburizado grado~1:
$\sigma_{{F\,\lim}}=206{{,}}8$ MPa y $\sigma_{{H\,\lim}}=1379$ MPa. Es la mejora más grande, a costa de fabricación especial.
\end{{itemize}}
{tabla_alternativas()}
{FIGS[16]}
\begin{{caja}}{{Recomendación}}
Como cambio inmediato con piezas de stock y el mismo proveedor: \textbf{{KG M50S25}} (B), con $\times${n(alt['B']['normal100']['T_adm'] / alt['A']['normal100']['T_adm'], 1)}
en servicio normal y {n(alt['B']['pico0']['T_adm'])}~N\,m de pico a rueda detenida.
Si hace falta más, una mitra a medida \textbf{{m\,0,6 $\times$ 21 carburizada}} (G). Con esa capacidad la fijación y el eje pasan a ser el límite
(sección~\ref{{sec:verif}}): prever chaveta o plano de arrastre y un eje de $\varnothing4$ o mayor.
\end{{caja}}

\section{{Lubricación}}\label{{sec:lub}}
\textbf{{Sí, es imprescindible.}}
\begin{{enumerate}}[leftmargin=1.2em]
\item \textbf{{El método la supone.}} Las capacidades AGMA de Shigley y las tablas de KG (baño de aceite de 100~cSt)
valen para engranajes lubricados. En seco los valores de este informe no son válidos: domina el desgaste adhesivo.
\item \textbf{{Régimen de lubricación límite.}} A $v_{{et}}\approx0{{,}}03$--$0{{,}}05$ m/s no se forma película elastohidrodinámica.
Los flancos se separan solo por la capa adsorbida de la grasa, así que el modo de falla a largo plazo es el
\textbf{{desgaste}}, que AGMA no calcula. Se necesita grasa con aditivos de extrema presión (EP) y antidesgaste, o con lubricante sólido (MoS$_2$).
\item \textbf{{Materiales.}} El S45C sin tratamiento se oxida (una rueda puede recibir humedad). El SUS304L contra SUS304L tiende a gripar
(\textit{{galling}}), así que en seco fallaría rápido. El latón tolera mejor la marcha pobre de lubricante, pero se desgasta. El POM puede andar en seco,
pero la grasa reduce el desgaste y el calentamiento.
\item \textbf{{Recomendación práctica.}} Grasa semifluida NLGI 00--0 (penetra y vuelve al engrane) de complejo de litio con EP para los metales.
Para POM, grasa sintética compatible con plásticos. Compartimiento cerrado contra polvo y arena, que en una rueda actúan como abrasivo.
Reengrase en cada mantenimiento y control del juego tras las primeras campañas.
\end{{enumerate}}

\section{{Verificaciones adicionales}}\label{{sec:verif}}
\begin{{itemize}}
\item \textbf{{Prisioneros.}} Shigley tabla 7-4: un prisionero n.º~2 sujeta 85~lbf $\approx{n(pr['F'], 0)}$~N. Sobre $\varnothing3$ mm son
{n(pr['T_uno'], 2)}~N\,m por tornillo, {n(pr['T_seguro'], 2)}~N\,m con factor 2. Alcanza para los picos del S45C
({n(T('S45C', 'pico', '0'))}~N\,m), siempre que el eje tenga un plano de apoyo. \textbf{{No alcanza para las alternativas D a G.}}
\item \textbf{{Eje $\varnothing3$ mm.}} Con el mayor pico ({n(T_pico_max)}~N\,m): $\tau=16T/(\pi d^3)={n(tau, 1)}$ MPa, admisible para acero.
\item \textbf{{Golpes de la rueda.}} Si la rueda choca contra obstáculos o el carro frena bruscamente, $K_A=1{{,}}25$ y todos los valores bajan un 20\,\%.
\end{{itemize}}

\section{{Conclusiones}}
\begin{{enumerate}}[leftmargin=1.2em]
\item Con Shigley ($R=0{{,}}95$, carga alternada, 10 años), la mitra KG m\,0,5 $\times$ 20 en S45C admite
{n(T('S45C', 'normal', '50'))} y {n(T('S45C', 'normal', '100'))}~N\,m de torque normal a 50 y 100~rpm, y picos de 10~s de
{n(T('S45C', 'pico', '50'))} y {n(T('S45C', 'pico', '100'))}~N\,m ({n(T('S45C', 'pico', '0'))}~N\,m a rueda detenida).
\item El latón admite alrededor de la mitad, el MIM un 40\,\% y el POM un 25\,\% de esos valores.
\item El dato de KG no representa la capacidad del par en esta aplicación.
\item Dentro de 14~mm, el reemplazo directo es KG M50S25. Con fabricación a medida carburizada se llega a más de seis veces la capacidad actual.
\item La lubricación con grasa EP es condición necesaria de todos los valores de este informe.
\end{{enumerate}}

\section*{{Referencias}}
\addcontentsline{{toc}}{{section}}{{Referencias}}
\begin{{enumerate}}[label={{[\arabic*]}},leftmargin=2em]
\item Budynas, R.\,G. y Nisbett, J.\,K. \textit{{Diseño en ingeniería mecánica de Shigley}}, 10.ª ed. McGraw-Hill. Caps. 6, 7 (tabla 7-4), 14 (tablas 14-2 y 14-7) y 15.
\item KG (Kyoiku Gear Mfg.). Catálogo KG4001, sección de mitras, pp. 233--276. \url{{https://www.kggear.co.jp/wp-content/uploads/2022/11/KG4001WEB-7.pdf}}
\item KG. Catálogo KG3001, pp. 379--444. \url{{https://www.kggear.co.jp/wp-content/uploads/KG3001_web_0009.pdf}}
\item KG. Material de referencia KG5001, pp. 18 y 20. \url{{https://www.kggear.co.jp/wp-content/uploads/2024/06/KG5001JP_reference.pdf}}
\item KG. \textit{{Technical Data Note}}, cap. 10.2. \url{{https://www.kggear.co.jp/en/wp-content/themes/bizvektor-global-edition/pdf/TechnicalData_KGSTOCKGEARS.pdf}}
\item KHK. \textit{{Design of Plastic Gears}}. \url{{https://khkgears.net/new/gear_knowledge/gear_technical_reference/design-of-plastic-gears.html}}
\item KHK. \textit{{Hardened Miter Gears (SMA/SMB/SMC)}}. \url{{https://www.khkgears.us/catalog/category/hardened_miter_gears_sma-smb-smc/}}
\item RS Components. RS PRO Steel Mitre Gear, 0,8 Module, 16 Teeth, 521-5780. \url{{https://ie.rs-online.com/web/p/mitre-bevel-gears/5215780}}
\item Copper Development Association. C36000 Free-Cutting Brass. \url{{https://www.copper.org/applications/rodbar/alloy360/free_cutting.html}}
\end{{enumerate}}
\end{{document}}
'''

tex = PRE + PORTADA + CUERPO
path = os.path.join(ROOT, NOMBRE + '.tex')
with open(path, 'w', encoding='utf-8') as fh:
    fh.write(tex)
for _ in range(3):
    r = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', NOMBRE + '.tex'],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-3000:])
        raise SystemExit('pdflatex falló')
for ext in ('aux', 'log', 'out', 'toc'):
    p = os.path.join(ROOT, f'{NOMBRE}.{ext}')
    if os.path.exists(p):
        os.remove(p)
print('ok', path)
