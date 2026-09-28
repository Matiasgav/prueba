#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compone el informe LaTeX desde resultados/resultados.json y lo compila.

Uso:
    python3 tools/calculo.py && python3 tools/capturas.py
    python3 tools/informe_tex.py        # escribe y compila informe_conicos_m05_z20.tex

Todos los números del texto salen del JSON de cálculo.
"""
import json
import math
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(ROOT, 'resultados', 'resultados.json'), encoding='utf-8'))
NOMBRE = 'informe_conicos_m05_z20'

DIS, F, D = R['disenos'], R['factores'], R['datos']
CL = list(DIS)
RPM = ['0', '0.5', '50', '100']
RPMN = ['0.5', '50', '100']
YZ = R['Y_Z']

# Datos de montaje de cada diseño (catálogos; custom = propuesta)
MONTAJE = {
    'M50S20': {'agujero': 3, 'fijacion': '2 prisioneros M2,5', 'cap': 'M2,5 en eje 3'},
    'M50B20': {'agujero': 3, 'fijacion': '2 prisioneros M2,5', 'cap': 'M2,5 en eje 3'},
    'M50S25': {'agujero': 4, 'fijacion': '2 prisioneros M3', 'cap': 'M3 en eje 4'},
    'RS': {'agujero': 4, 'fijacion': 'prisionero (a confirmar)', 'cap': 'M3 en eje 4'},
    'CARB': {'agujero': 5, 'fijacion': 'pasador o chaveta (propuesta)', 'cap': None},
}


def n(x, d=3):
    return f'{x:.{d}f}'.replace('.', ',')


def m_(x, d=3):
    return f'{x:.{d}f}'.replace('.', '{,}')


def e(x):
    a, b = f'{x:.2e}'.split('e')
    return f'${a.replace(".", "{,}")}\\times10^{{{int(b)}}}$'


def rpm_t(r):
    return {'0': '0', '0.5': '0,5', '50': '50', '100': '100'}[r]


def T(k, reg, r):
    return DIS[k][reg][r]['T_adm']


def figura(path, cap, fuente, ancho='\\linewidth', label=None):
    lab = f'\\label{{{label}}}' if label else ''
    return ('\\begin{figure}[H]\\centering\\includegraphics[width=' + ancho + ']{' + path + '}'
            '\\caption{' + cap + ' \\textit{Fuente: ' + fuente + '}}' + lab + '\\end{figure}\n')


def nombre(k):
    return {'M50S20': 'KG M50S20 (S45C)', 'M50B20': 'KG M50B20 (latón)',
            'M50S25': 'KG M50S25 (S45C)', 'RS': 'RS PRO 521-5780',
            'CARB': 'A medida carburizada'}[k]


# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------
def tabla_resumen():
    filas = []
    for k in CL:
        c = ' & '.join(n(T(k, 'normal', r)) for r in RPMN)
        p = ' & '.join(n(T(k, 'pico', r)) for r in RPM)
        filas.append(f'{nombre(k)} & {n(DIS[k]["geo"]["da"], 1)} & {c} & {p} \\\\')
    return (r'''\begin{table}[H]\centering\small\setlength{\tabcolsep}{4.5pt}
\caption{Torque admisible por engranaje, en N\,m ($R=0{,}95$, carga en ambos sentidos, 10 años, grasa).}\label{tab:resumen}
\begin{tabular}{l r ccc cccc}
\toprule
 & & \multicolumn{3}{c}{Torque normal (toda la vida)} & \multicolumn{4}{c}{Torque de pico (10 s, ocasional)}\\
\cmidrule(lr){3-5}\cmidrule(lr){6-9}
Diseño & $d_a$ [mm] & 0,5 rpm & 50 rpm & 100 rpm & 0 rpm & 0,5 rpm & 50 rpm & 100 rpm\\
\midrule
''' + '\n'.join(filas) + '\n\\bottomrule\\end{tabular}\\end{table}\n')


def tabla_disenos():
    filas = []
    for k in CL:
        g = DIS[k]['geo']
        mt = DIS[k]['mat'].replace('SCM415 carburizado', 'SCM415 carb.')
        filas.append(f'{nombre(k)} & {mt} & {n(g["m"], 1)} & {g["z"]} & {n(g["d"], 1)} & '
                     f'{n(g["da"], 2)} & {n(g["Re"], 2)} & {n(g["b"], 2)} & {n(g["b_ef"], 2)} & '
                     f'{n(g["J"], 3)} & {n(g["I"], 3)} & {MONTAJE[k]["agujero"]} \\\\')
    return (r'''\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3.5pt}
\caption{Diseños analizados: geometría y factores de geometría de Shigley.}\label{tab:disenos}
\begin{tabular}{l l r r r r r r r r r r}
\toprule
Diseño & Material & $m$ & $z$ & $d_e$ & $d_a$ & $R_e$ & $b$ & $b_{ef}$ & $Y_J$ & $Z_I$ & Agujero\\
 & & mm & & mm & mm & mm & mm & mm & & & mm\\
\midrule
''' + '\n'.join(filas) + '\n\\bottomrule\\end{tabular}\\end{table}\n')


def tabla_detalle(reg):
    filas = []
    rr = RPMN if reg == 'normal' else RPM
    for k in CL:
        for i, r in enumerate(rr):
            x = DIS[k][reg][r]
            nom = nombre(k) if i == 0 else ''
            filas.append(f'{nom} & {rpm_t(r)} & {e(x["N"])} & {n(x["K_v"], 3)} & '
                         f'{n(x["Y_NT"])} & {n(x["Z_NT"])} & {n(x["sFP"], 1)} & {n(x["sHP"], 0)} & '
                         f'{n(x["W_F"], 1)} & {n(x["W_H"], 1)} & {n(x["T_F"])} & {n(x["T_H"])} & '
                         f'\\textbf{{{n(x["T_adm"])}}} & {x["modo"]} \\\\')
        filas.append('\\addlinespace[2pt]')
    tit = ('Servicio normal: ciclos de toda la vida' if reg == 'normal'
           else 'Picos de 10 s: ciclos de los picos')
    return (r'\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{2.8pt}'
            '\\caption{' + tit + ' (evaluados al doble, regla de Miner).}'
            r'''\begin{tabular}{l r r c c c r r r r r r r l}
\toprule
Diseño & rpm & $N_L$ & $K_v$ & $Y_{NT}$ & $Z_{NT}$ & $\sigma_{FP}$ & $\sigma_{HP}$ & $W_F$ & $W_H$ & $T_F$ & $T_H$ & $T_{adm}$ & Limita\\
 & & & & & & MPa & MPa & N & N & N\,m & N\,m & N\,m & \\
\midrule
''' + '\n'.join(filas) + '\n\\bottomrule\\end{tabular}\\end{table}\n')


def tabla_materiales():
    filas = []
    for k in ('S45C', 'Latón C3604B', 'SCM415 carburizado'):
        mt = R['materiales'][k]
        ze = math.sqrt(1 / (math.pi * 2 * (1 - mt['nu'] ** 2) / mt['E']))
        filas.append(f'{k} & {n(mt["E"] / 1000, 0)} & {n(mt["nu"], 2)} & {n(ze, 1)} & '
                     f'{n(mt["sFlim"], 1)} & {mt["base_F"]} & {n(mt["sHlim"], 0)} & {mt["base_H"]} \\\\')
    return (r'''\begin{table}[H]\centering\small\setlength{\tabcolsep}{4pt}
\caption{Propiedades y resistencias de referencia.}\label{tab:mat}
\begin{tabular}{l r r r r p{3.6cm} r p{3.2cm}}
\toprule
Material & $E$ & $\nu$ & $Z_E$ & $\sigma_{F\,\lim}$ & Base & $\sigma_{H\,\lim}$ & Base\\
 & GPa & & $\sqrt{\text{MPa}}$ & MPa & & MPa & \\
\midrule
''' + '\n'.join(filas).replace('×', r'$\times$') + '\n\\bottomrule\\end{tabular}\\end{table}\n')


def tabla_fijacion():
    filas = []
    for k in CL:
        mo = MONTAJE[k]
        tp = T(k, 'pico', '0')
        dd = mo['agujero']
        tau = 16 * tp * 1000 / (math.pi * dd ** 3)
        if mo['cap']:
            ts = R['prisionero'][mo['cap']]['T_seguro']
            ok = 'sí' if ts >= tp else '\\textbf{no}'
            cap = n(ts, 2)
        else:
            cap, ok = '--', 'arrastre positivo'
        filas.append(f'{nombre(k)} & {dd} & {mo["fijacion"]} & {n(tp)} & {cap} & {ok} & {n(tau, 0)} \\\\')
    return (r'''\begin{table}[H]\centering\small\setlength{\tabcolsep}{4pt}
\caption{Fijación al eje y torsión del eje frente al mayor pico (0 rpm).}\label{tab:fij}
\begin{tabular}{l r l r r l r}
\toprule
Diseño & Eje & Fijación & Pico 0 rpm & Prisioneros ($n=2$) & ¿Alcanza? & $\tau$ eje\\
 & mm & & N\,m & N\,m & & MPa\\
\midrule
''' + '\n'.join(filas) + '\n\\bottomrule\\end{tabular}\\end{table}\n')


# ---------------------------------------------------------------------------
# Valores sueltos
# ---------------------------------------------------------------------------
ref = DIS['M50S20']
x = ref['normal']['100']
xp = ref['pico']['100']
g0 = ref['geo']
b = g0['b_ef']
kg20, kg25 = R['kg']['M50S20'], R['kg']['M50S25']
Npk = R['n_picos']
rel = {k: T(k, 'normal', '100') / T('M50S20', 'normal', '100') for k in CL}
lat = R['cota_laton']

PRE = open(os.path.join(ROOT, 'tools', 'preambulo.tex'), encoding='utf-8').read()

PORTADA = r'''\begin{titlepage}
\centering
\vspace*{2.2cm}
{\color{azul}\rule{\linewidth}{1.2pt}}\\[0.8cm]
{\Huge\bfseries Torque admisible de engranajes\\[0.25cm] cónicos a 90$^\circ$ para la rueda de un carro\par}
\vspace{0.6cm}
{\Large Mitras KG m\,0,5, RS PRO m\,0,8 y mitra carburizada a medida\\ Análisis según Shigley (método AGMA para engranajes cónicos)\par}
\vspace{0.6cm}
{\color{azul}\rule{\linewidth}{1.2pt}}\\[1.4cm]
\begin{tabular}{rl}
\textbf{Diseños:} & KG M50S20 (S45C), KG M50B20 (latón), KG M50S25 (S45C),\\
 & RS PRO 521-5780 (m\,0,8 $\times$ 16), a medida m\,0,6 $\times$ 21 SCM415 carburizado\\
\textbf{Envolvente:} & diámetro exterior $d_a\le14$ mm, relación 1:1, ejes a 90$^\circ$\\
\textbf{Velocidades:} & 0, 0,5, 50 y 100 rpm\\
\textbf{Confiabilidad:} & 95\,\%\\
\textbf{Servicio:} & torque en ambos sentidos, normal bajo y picos de 10 s\\
\textbf{Método:} & Budynas y Nisbett, \textit{Diseño en ingeniería mecánica de Shigley}, cap. 15\\
\end{tabular}
\vfill
{\large Informe técnico\\ Septiembre de 2026\par}
\end{titlepage}
'''

FIGS = {
    'codigo': figura('capturas/kg_codigo_producto.png', 'Código de producto de las mitras KG (S = S45C, B = latón).', 'KG, catálogo KG4001, p. 233.', '0.95\\linewidth'),
    's45c_datos': figura('capturas/kg_s45c_datos.png', 'Mitras S45C M50S20 y M50S25: JIS B1704 grado 3, sin tratamiento térmico; $b=2{,}5$ y $3{,}0$ mm; agujeros de 3 y 4 mm.', 'KG, catálogo KG4001, p. 260.'),
    's45c_pot': figura('capturas/kg_s45c_potencia.png', 'Potencia admisible KG a flexión: M50S20 1,5 W y M50S25 2,5 W a 100 rpm. La resistencia superficial no se publica («--»).', 'KG, catálogo KG4001, p. 261.'),
    'laton': figura('capturas/kg_laton_datos.png', 'Mitra de latón C3604B M50B20: JIS B1704 grado 4, sin tabla de potencia.', 'KG, catálogo KG4001, p. 272.', '0.9\\linewidth'),
    'cond': figura('capturas/kg_condiciones_conicos.png', 'Condiciones de las tablas de KG para cónicos: JGMA 403-01/404-01; $\\geq10^7$ ciclos; choque moderado ($K_O=1{,}25$); baño de aceite de 100 cSt; ambos engranajes en voladizo; con carga en ambos sentidos, 2/3 del valor de tabla.', 'KG, KG5001, p. 18.'),
    'jgma': figura('capturas/kg_jgma403_alcance.png', 'Alcance de JGMA 403-01/404-01: módulo exterior de 1,5 a 25 mm.', 'KG, Technical Data, cap. 10.2, p. 137.', '0.48\\linewidth'),
    'conv': figura('capturas/kg_conversion_potencia.png', 'Conversión de potencia a torque: $T\\,[\\mathrm{N\\,m}]=9549{,}7\\,P\\,[\\mathrm{kW}]/n$.', 'KG, KG5001, p. 20.'),
    'ciclos': figura('figuras/fig_ciclos.pdf', 'Factores de ciclos de Shigley (Figs. 15-8 y 15-9, graficados desde sus ecuaciones) y puntos de trabajo.', 'ecuaciones de Shigley, cap. 15.', '0.95\\linewidth'),
    'resumen': figura('figuras/fig_resumen.pdf', 'Torque admisible de cada diseño: servicio normal y picos de 10 s.', 'cálculo propio.', label='fig:resumen'),
    'modos': figura('figuras/fig_modos.pdf', 'Servicio normal a 100 rpm: capacidad a flexión alternada y a picado de cada diseño (escala logarítmica).', 'cálculo propio.'),
    'rpm': figura('figuras/fig_rpm.pdf', 'Torque admisible en función de la velocidad de la rueda (escala logarítmica).', 'cálculo propio.'),
    'picos': figura('figuras/fig_picos.pdf', 'Pico admisible a 100 rpm en función de la frecuencia de picos.', 'cálculo propio.'),
    'sens': figura('figuras/fig_sensibilidad.pdf', 'Sensibilidad del torque normal de KG M50S20 a 100 rpm a cada supuesto.', 'cálculo propio.', label='fig:sens'),
}

CUERPO = rf'''
\section*{{Resumen ejecutivo}}
\addcontentsline{{toc}}{{section}}{{Resumen ejecutivo}}
Se determinó el torque admisible de cinco pares de engranajes cónicos 1:1 a 90$^\circ$ con diámetro exterior de hasta 14 mm,
para la transmisión de la rueda de un carro. Se usaron las ecuaciones AGMA para engranajes cónicos del capítulo~15 de Shigley,
con confiabilidad del 95\,\% y flexión alternada (torque en ambos sentidos). El servicio combina un torque normal bajo
durante toda la vida con picos ocasionales de 10~s.

{tabla_resumen()}

\begin{{caja}}{{Conclusiones principales}}
\begin{{enumerate}}[leftmargin=1.2em]
\item \textbf{{KG M50S20 (actual)}}: {n(T('M50S20', 'normal', '100'))}~N\,m en servicio normal y {n(T('M50S20', 'pico', '100'))}~N\,m en picos a 100~rpm.
El dato del catálogo KG (1,5~W a 100~rpm $=$ {n(kg20)}~N\,m) supera en un {n((kg20 / T('M50S20', 'normal', '100') - 1) * 100, 0)}\,\% esa capacidad y no debe usarse.
\item \textbf{{KG M50S25}}, de stock y del mismo proveedor: $\times${n(rel['M50S25'], 1)} ({n(T('M50S25', 'normal', '100'))}~N\,m normal; {n(T('M50S25', 'pico', '0'))}~N\,m de pico a rueda detenida).
\item \textbf{{RS PRO 521-5780}}: $\times${n(rel['RS'], 1)} ({n(T('RS', 'normal', '100'))}~N\,m normal; {n(T('RS', 'pico', '0'))}~N\,m de pico). Hay que confirmar el ancho de diente.
\item \textbf{{Mitra a medida carburizada}}: $\times${n(rel['CARB'], 1)} ({n(T('CARB', 'normal', '100'))}~N\,m normal; {n(T('CARB', 'pico', '0'))}~N\,m de pico). Exige eje de 5~mm con arrastre positivo.
\item El latón (M50B20) admite la mitad que el S45C. La lubricación con grasa EP es condición de todos los valores.
\end{{enumerate}}
\end{{caja}}

\tableofcontents
\newpage

\section{{Objeto y datos de partida}}
\subsection{{Aplicación}}
El par de engranajes transmite el giro de un motor BLDC a la rueda de un carro, con ejes a 90$^\circ$ y relación 1:1.
El compartimiento está engrasado y la temperatura de trabajo es de 30 a 40\,$^\circ$C. El motor sigue un perfil
trapezoidal suave y el equipo se usa 20~h seguidas una vez por mes. El diámetro exterior disponible es de 14~mm.

\subsection{{Ciclo de carga de la rueda}}
\begin{{itemize}}
\item \textbf{{Torque en ambos sentidos}} (marcha adelante y atrás, aceleración y frenado). Cada diente se flexiona hacia uno y otro lado,
así que se usa el 70\,\% de la resistencia a flexión.
\item \textbf{{Servicio normal}} con torque bajo durante toda la vida: $n_{{normal}}=n\cdot60\cdot20\cdot12\cdot10$ ciclos por diente.
\item \textbf{{Picos}} de 10~s. Se supuso \textbf{{un pico por hora de uso}}: {n(Npk, 0)} eventos en 10 años, con $\max(1;\,n\cdot10/60)$ ciclos por diente cada uno.
\item \textbf{{Combinación por la regla de Miner.}} Cada régimen consume la mitad del daño admisible:
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
Par & Engranajes cónicos rectos iguales, 1:1, $\Sigma=90^\circ$, $d_a\le14$ mm & pedido\\
Velocidades & 0, 0,5, 50 y 100 rpm & pedido\\
Confiabilidad & $R=0{{,}}95$ & pedido\\
Uso & 20 h por mes; vida de diseño 10 años (2400 h) & pedido / \textbf{{supuesto}}\\
Picos & 10 s, 1 por hora de uso ({n(Npk, 0)} en la vida) & pedido / \textbf{{supuesto}}\\
Carga & BLDC, perfil trapezoidal suave, torque en ambos sentidos & pedido\\
Lubricación & Grasa en compartimiento cerrado & pedido\\
Temperatura & 30--40\,$^\circ$C & pedido\\
Montaje & Ambos engranajes en voladizo & \textbf{{supuesto}} conservador\\
\bottomrule
\end{{tabularx}}
\end{{table}}

\section{{Diseños analizados}}
{tabla_disenos()}
\begin{{itemize}}
\item \textbf{{KG M50S20 y M50B20}}: la mitra actual en S45C y en latón (catálogo KG4001).
\item \textbf{{KG M50S25}}: m\,0,5 con 25 dientes, $b=3$ mm, agujero de 4 mm. $Y_J$ y $Z_I$ corresponden al Ejemplo 15-1 de Shigley (mitras de 25 dientes).
\item \textbf{{RS PRO 521-5780}}: acero S45C (RS indica temple por inducción y resistencia mínima de 569 MPa), m\,0,8, 16 dientes, sistema Gleason, DIN 3971.
RS no publica el ancho de diente, así que se tomó $b=0{{,}}3R_e$. Como no se pudo confirmar que el flanco esté templado, se calculó sin temple (lado seguro).
$Y_J$ y $Z_I$ se extrapolaron a 16 dientes.
\item \textbf{{A medida carburizada}}: m\,0,6 (módulo normalizado) con 21 dientes, el mayor tamaño que entra en 14 mm, de SCM415 cementado y templado a 58--62 HRC.
Shigley, acero carburizado grado~1: $\sigma_{{F\,\lim}}=206{{,}}8$ MPa (30 kpsi) y $\sigma_{{H\,\lim}}=1379$ MPa (200 kpsi).
\end{{itemize}}
{FIGS['codigo']}
{FIGS['s45c_datos']}
{FIGS['s45c_pot']}
{FIGS['laton']}

\section{{Alcance del dato de capacidad de KG}}
{FIGS['cond']}
{FIGS['jgma']}
{FIGS['conv']}
\begin{{caja}}[orange!80!black]{{Limitaciones del dato del fabricante}}
\begin{{enumerate}}[leftmargin=1.2em]
\item Solo publica flexión. Para m\,0,5 no hay resistencia superficial (picado).
\item Usa JGMA 403/404, cuyo alcance empieza en $m=1{{,}}5$ mm.
\item Supone carga en un sentido, baño de aceite y $\geq10^7$ ciclos, condiciones distintas a las de una rueda.
\item M50S25: 2,5~W a 100~rpm $=$ {n(kg25)}~N\,m, frente a {n(T('M50S25', 'normal', '100'))}~N\,m calculados aquí para el servicio normal.
\end{{enumerate}}
\end{{caja}}

\section{{Geometría}}
\begin{{minipage}}[c]{{0.46\linewidth}}\centering
\includegraphics[width=\linewidth]{{figuras/fig_geometria.pdf}}
\captionof{{figure}}{{Corte axial esquemático de KG M50S20.}}
\end{{minipage}}\hfill
\begin{{minipage}}[c]{{0.5\linewidth}}\small
Relaciones usadas para todos los diseños ($\delta=45^\circ$):
\begin{{align*}}
d_e&=m\,z, & R_e&=\frac{{d_e}}{{2\sin\delta}},\\
d_a&=d_e+2m\cos\delta, & z_v&=\frac{{z}}{{\cos\delta}},\\
b_{{ef}}&=\min\left(b;\,0{{,}}3R_e\right).
\end{{align*}}
Shigley limita el ancho útil al 30\,\% de la distancia de cono. En las mitras KG el ancho de catálogo supera ese valor,
así que solo se acredita $0{{,}}3R_e$.
\end{{minipage}}

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
Dinámico $K_v$ & $\approx1{{,}}04$ & $K_v=\left[(A+\sqrt{{200\,v_{{et}}}})/A\right]^B$, $B=0{{,}}25(12-Q_v)^{{2/3}}$, $A=50+56(1-B)$, $Q_v=6$\\
Tamaño $K_s$ / $Y_x$ & 0,5 & $m_{{et}}<1{{,}}6$ mm\\
Tamaño $C_s$ / $Z_x$ & 0,5 & $b<12{{,}}7$ mm\\
Distribución $K_m$ / $K_{{H\beta}}$ & 1,25 & $K_{{mb}}+5{{,}}6\times10^{{-6}}b^2$, $K_{{mb}}=1{{,}}25$ (ambos en voladizo)\\
Coronamiento $C_{{xc}}$ / $Z_{{xc}}$ & 2,0 & Dientes sin coronamiento garantizado\\
Curvatura $K_x$ / $Y_\beta$ & 1 & Dientes rectos\\
Geometría $J$ / $Y_J$, $I$ / $Z_I$ & tabla~\ref{{tab:disenos}} & Figs.~15-7 y 15-6 de Shigley\\
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
{FIGS['ciclos']}

\section{{Resistencia de los materiales}}
El S45C sin tratamiento entra en Shigley como acero templado total grado~1; se toma 170~HB, el extremo inferior de JIS G4051:
\begin{{equation}}
\sigma_{{F\,\lim}}=0{{,}}30\,\mathrm{{HB}}+14{{,}}48={m_(R['referencia']['sFlim'], 1)}\ \text{{MPa}},\qquad
\sigma_{{H\,\lim}}=2{{,}}35\,\mathrm{{HB}}+162{{,}}89={m_(R['referencia']['sHlim'], 1)}\ \text{{MPa}}
\end{{equation}}
El latón no figura en Shigley. Se escala desde el S45C por la relación de límites de fatiga (138/285) a flexión y por la dureza
Brinell (100/170) a picado. El SCM415 carburizado toma los valores tabulados por Shigley para acero carburizado grado~1.
\begin{{equation}}
Z_E=\left[\pi\left(\frac{{1-\nu_1^2}}{{E_1}}+\frac{{1-\nu_2^2}}{{E_2}}\right)\right]^{{-1/2}}
\end{{equation}}
{tabla_materiales()}

\section{{Cálculo paso a paso: KG M50S20, servicio normal a 100 rpm}}
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
$Z_{{NT}}={m_(xp['Z_NT'])}$ y $T_{{adm}}={m_(xp['T_adm'], 4)}$~N\,m ({xp['modo']}). Los demás diseños siguen el mismo procedimiento con su
geometría y su material (tablas~\ref{{tab:disenos}} y \ref{{tab:mat}}).

\section{{Resultados}}
{tabla_detalle('normal')}
{tabla_detalle('pico')}
{FIGS['resumen']}
{FIGS['modos']}
{FIGS['rpm']}
En todos los casos $\sigma_{{FP}}<S_y$, así que ningún pico produce fluencia estática del diente.

\section{{Sensibilidad}}
{FIGS['sens']}
{FIGS['picos']}
Para el latón, si en lugar de escalar por dureza se toma la resistencia a picado del bronce al estaño de Shigley (tabla 14-7),
el torque normal baja de {n(T('M50B20', 'normal', '100'))} a {n(lat['100'])}~N\,m a 100~rpm.

\section{{Fijación al eje}}
Con más capacidad en los dientes, la unión al eje puede pasar a ser el límite. Prisioneros según Shigley tabla 7-4
(n.º 2 $\approx$ M2,5: 85~lbf; n.º 4 $\approx$ M3: 160~lbf), con factor 2; eje de acero.
{tabla_fijacion()}
La mitra carburizada supera la capacidad de los prisioneros. Requiere eje de 5~mm con pasador, chaveta o plano de arrastre, y hay que
verificar también rodamientos y carcasa para ese torque.

\section{{Lubricación}}\label{{sec:lub}}
\textbf{{Es imprescindible.}}
\begin{{enumerate}}[leftmargin=1.2em]
\item \textbf{{El método la supone.}} Las capacidades AGMA de Shigley y las tablas de KG (baño de aceite de 100~cSt) valen para engranajes lubricados.
En seco los valores de este informe no son válidos: domina el desgaste adhesivo.
\item \textbf{{Régimen de lubricación límite.}} A $v_{{et}}\approx0{{,}}03$--$0{{,}}07$ m/s no se forma película elastohidrodinámica. El modo de falla a largo plazo es
el \textbf{{desgaste}}, que AGMA no calcula. Se requiere grasa con aditivos de extrema presión (EP) y antidesgaste, o con MoS$_2$.
\item \textbf{{Materiales.}} El S45C sin tratamiento se oxida (una rueda puede recibir humedad). El latón se desgasta más rápido. El carburizado es
el más resistente al desgaste, pero también necesita grasa EP.
\item \textbf{{Recomendación práctica.}} Grasa semifluida NLGI 00--0 de complejo de litio con EP, compartimiento cerrado contra polvo y arena,
reengrase en cada mantenimiento y control del juego tras las primeras campañas.
\end{{enumerate}}

\section{{Conclusiones y recomendación}}
\begin{{enumerate}}[leftmargin=1.2em]
\item Con Shigley ($R=0{{,}}95$, carga alternada, 10 años), el torque admisible a 100~rpm es:
KG M50S20 {n(T('M50S20', 'normal', '100'))}~N\,m (pico {n(T('M50S20', 'pico', '100'))});
KG M50B20 {n(T('M50B20', 'normal', '100'))} ({n(T('M50B20', 'pico', '100'))});
KG M50S25 {n(T('M50S25', 'normal', '100'))} ({n(T('M50S25', 'pico', '100'))});
RS PRO 521-5780 {n(T('RS', 'normal', '100'))} ({n(T('RS', 'pico', '100'))});
a medida carburizada {n(T('CARB', 'normal', '100'))} ({n(T('CARB', 'pico', '100'))}).
\item \textbf{{Recomendación inmediata: KG M50S25.}} Es de stock y del mismo proveedor, entra en 14~mm, casi duplica la capacidad y mantiene la fijación por prisioneros.
\item El RS PRO rinde algo más, pero depende de datos no publicados (ancho de diente y temple). Si RS confirma temple por inducción del flanco, su capacidad sube.
\item Para más del doble de la capacidad del M50S25, la única vía dentro de 14~mm es la mitra carburizada a medida, con eje de 5~mm y arrastre positivo.
\item La lubricación con grasa EP es condición necesaria de todos los valores.
\end{{enumerate}}

\section*{{Referencias}}
\addcontentsline{{toc}}{{section}}{{Referencias}}
\begin{{enumerate}}[label={{[\arabic*]}},leftmargin=2em]
\item Budynas, R.\,G. y Nisbett, J.\,K. \textit{{Diseño en ingeniería mecánica de Shigley}}, 10.ª ed. McGraw-Hill. Caps. 6, 7 (tabla 7-4), 14 (tabla 14-7) y 15.
\item KG (Kyoiku Gear Mfg.). Catálogo KG4001, sección de mitras, pp. 233--276. \url{{https://www.kggear.co.jp/wp-content/uploads/2022/11/KG4001WEB-7.pdf}}
\item KG. Material de referencia KG5001, pp. 18 y 20. \url{{https://www.kggear.co.jp/wp-content/uploads/2024/06/KG5001JP_reference.pdf}}
\item KG. \textit{{Technical Data Note}}, cap. 10.2. \url{{https://www.kggear.co.jp/en/wp-content/themes/bizvektor-global-edition/pdf/TechnicalData_KGSTOCKGEARS.pdf}}
\item RS Components. RS PRO Steel Mitre Gear, 0,8 Module, 16 Teeth, 521-5780. \url{{https://int.rsdelivers.com/product/rs-pro/rs-pro-steel-mitre-gear-4mm-bore-16-teeth-08/5215780}}
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
                       cwd=ROOT, capture_output=True, text=True, errors='replace')
    if r.returncode:
        print(r.stdout[-3000:])
        raise SystemExit('pdflatex falló')
for ext in ('aux', 'log', 'out', 'toc'):
    p = os.path.join(ROOT, f'{NOMBRE}.{ext}')
    if os.path.exists(p):
        os.remove(p)
print('ok', path)
