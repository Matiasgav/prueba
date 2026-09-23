#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compone el informe HTML autocontenido desde resultados/resultados.json.

Uso:
    python3 tools/calculo.py && python3 tools/capturas.py
    python3 tools/informe.py            # escribe informe_conicos_m05_z20.html

Todos los números del texto salen del JSON de cálculo, de modo que el informe
y el cálculo no pueden divergir. Las imágenes se incrustan en base64.
"""
import base64
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(ROOT, 'resultados', 'resultados.json'), encoding='utf-8'))
OUT = os.path.join(ROOT, 'informe_conicos_m05_z20.html')

MET = R['metales']
POM = R['pom']
G = R['geometria']
F = R['factores']
D = R['datos']
RPM = [str(r) if r != 0.5 else '0.5' for r in D['rpm']]
RPM = ['0', '0.5', '50', '100']
NOM = {'S45C': 'S45C', 'SUS304L MIM': 'SUS304L (MIM)', 'Latón C3604B': 'Latón C3604B'}


def n(x, d=3):
    """Número con coma decimal."""
    return f'{x:.{d}f}'.replace('.', ',')


def e(x):
    m, ex = f'{x:.2e}'.split('e')
    return f'{m.replace(".", ",")}·10<sup>{int(ex)}</sup>'


def rpm_txt(r):
    return {'0': '0 (estático)', '0.5': '0,5', '50': '50', '100': '100'}[r]


def img(path, alt, cls=''):
    p = os.path.join(ROOT, path)
    ext = os.path.splitext(p)[1].lower().lstrip('.')
    mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'svg': 'image/svg+xml'}[ext]
    b64 = base64.b64encode(open(p, 'rb').read()).decode()
    return f'<img class="{cls}" src="data:{mime};base64,{b64}" alt="{alt}">'


def fig(path, num, cap, fuente, cls=''):
    return (f'<figure class="{cls}">{img(path, cap)}<figcaption><b>Figura {num}.</b> '
            f'{cap}<span class="src">Fuente: {fuente}</span></figcaption></figure>')


# ---------------------------------------------------------------------------
# Tablas derivadas
# ---------------------------------------------------------------------------
def tabla_resumen():
    filas = []
    for k, v in MET.items():
        c = ''.join(f'<td class="num">{n(v[r]["T_adm"])}</td>' for r in RPM)
        modo = v['100']['modo']
        filas.append(f'<tr><th>{NOM[k]}</th>{c}<td class="num">'
                     f'{n(min(v["100"]["T_F_alt"], v["100"]["T_H"]))}</td>'
                     f'<td>{modo}</td></tr>')
    c = ''.join(f'<td class="num">{n(POM[r]["T_adm"])}</td>' for r in RPM)
    filas.append(f'<tr><th>POM inyectado</th>{c}<td class="num">'
                 f'{n(0.7 * POM["100"]["T_adm"])}</td><td>flexión (Lewis)</td></tr>')
    return ('<table class="res"><thead><tr><th>Material</th>'
            + ''.join(f'<th>{rpm_txt(r)} rpm</th>' for r in RPM)
            + '<th>100 rpm, carga en<br>ambos sentidos</th><th>Modo que limita a 100 rpm</th>'
              '</tr></thead><tbody>' + ''.join(filas) + '</tbody></table>')


def tabla_detalle():
    filas = []
    for k, v in MET.items():
        for r in RPM:
            x = v[r]
            filas.append(
                f'<tr><th>{NOM[k]}</th><td>{rpm_txt(r)}</td><td class="num">{e(x["N"])}</td>'
                f'<td class="num">{n(x["K_v"], 4)}</td><td class="num">{n(x["Y_NT"], 3)}</td>'
                f'<td class="num">{n(x["Z_NT"], 3)}</td><td class="num">{n(x["sFP"], 1)}</td>'
                f'<td class="num">{n(x["sHP"], 0)}</td><td class="num">{n(x["W_F"], 1)}</td>'
                f'<td class="num">{n(x["W_H"], 1)}</td><td class="num">{n(x["T_F"])}</td>'
                f'<td class="num">{n(x["T_H"])}</td><td class="num"><b>{n(x["T_adm"])}</b></td></tr>')
    return ('<table class="det"><thead><tr><th>Material</th><th>rpm</th><th>N<sub>L</sub></th>'
            '<th>K<sub>v</sub></th><th>Y<sub>NT</sub></th><th>Z<sub>NT</sub></th>'
            '<th>σ<sub>FP</sub><br>MPa</th><th>σ<sub>HP</sub><br>MPa</th>'
            '<th>W<sub>F</sub><br>N</th><th>W<sub>H</sub><br>N</th>'
            '<th>T<sub>F</sub><br>N·m</th><th>T<sub>H</sub><br>N·m</th><th>T<sub>adm</sub><br>N·m</th>'
            '</tr></thead><tbody>' + ''.join(filas) + '</tbody></table>')


def tabla_materiales():
    filas = []
    for k, m in R['materiales'].items():
        v = MET[k]['100']
        filas.append(
            f'<tr><th>{NOM[k]}</th><td>{m["codigo"]}</td><td class="num">{n(m["E"] / 1000, 0)}</td>'
            f'<td class="num">{n(m["nu"], 2)}</td><td class="num">{n(m["HB"], 0)}</td>'
            f'<td class="num">{n(v["Z_E"], 1)}</td>'
            f'<td class="num">{n(v["sFlim"], 1)}</td><td>{m["base_F"]}</td>'
            f'<td class="num">{n(v["sHlim"], 0)}</td><td>{m["base_H"]}</td></tr>')
    return ('<table class="det"><thead><tr><th>Material</th><th>Código KG</th><th>E<br>GPa</th>'
            '<th>ν</th><th>HB</th><th>Z<sub>E</sub><br>√MPa</th><th>σ<sub>F lim</sub><br>MPa</th>'
            '<th>Base de σ<sub>F lim</sub></th><th>σ<sub>H lim</sub><br>MPa</th>'
            '<th>Base de σ<sub>H lim</sub></th></tr></thead><tbody>' + ''.join(filas)
            + '</tbody></table>')


def tabla_kg():
    kg = R['kg']
    s = kg['S45C']
    mim = kg['SUS304L MIM']
    t_s = MET['S45C']['100']
    return f'''<table class="det"><thead><tr><th>Material (m 0,5, z 20)</th><th>Código</th>
<th>Potencia KG a flexión, 100 rpm</th><th>Torque equivalente<br>T = 9549,7·P/n</th>
<th>Picado (KG)</th><th>Base del dato KG</th></tr></thead><tbody>
<tr><th>S45C</th><td>M50S20-1103 / *1103</td><td class="num">1,5 W</td><td class="num">{n(s["100"])} N·m</td>
<td>«–» (no publicado)</td><td>JGMA 403-01 con K<sub>O</sub> = 1,25, K<sub>Mβ</sub> = 1,8, K<sub>R</sub> = 1,2</td></tr>
<tr><th>SUS304L (MIM)</th><td>M50SUM20*1103</td><td class="num">0,5 W</td><td class="num">{n(mim["100"])} N·m</td>
<td>no publicado</td><td>ensayo de durabilidad propio (cat. 2020); «fórmula JGMA» (cat. 2022)</td></tr>
<tr><th>Latón C3604B</th><td>M50B20-1103 / *1103</td><td>sin tabla</td><td>—</td><td>no publicado</td>
<td>KG no publica capacidad para el latón m 0,5</td></tr>
<tr><th>POM negro inyectado</th><td>M50DM20-1103</td><td>sin tabla</td><td>—</td><td>no publicado</td>
<td>catálogo 2020; no figura en el catálogo 2022</td></tr>
</tbody></table>
<p class="nota">Para comparar con el caso real, el torque de KG para S45C referido a carga uniforme
(K<sub>O</sub> = 1,0 en lugar de 1,25) sería {n(s["100"] * 1.25)} N·m. Shigley da, a flexión y en las
mismas condiciones de vida, {n(t_s["T_F"])} N·m.</p>'''


def tabla_pom():
    filas = []
    for r in RPM:
        x = POM[r]
        filas.append(f'<tr><th>{rpm_txt(r)}</th><td class="num">{e(x["N"])}</td>'
                     f'<td class="num">{n(x["s_b"], 1)}</td><td class="num">{n(x["s_adm"], 1)}</td>'
                     f'<td class="num">{n(x["T_khk"])}</td><td class="num">{n(x["T_lewis"])}</td>'
                     f'<td class="num">{n(x["T_kgcal"])}</td><td class="num"><b>{n(x["T_adm"])}</b></td></tr>')
    return ('<table class="det"><thead><tr><th>rpm</th><th>N</th><th>σ<sub>b</sub>(N)<br>MPa</th>'
            '<th>σ<sub>b adm</sub><br>MPa</th><th>T método KHK<br>(y = 0,597)</th>'
            '<th>T Lewis–Shigley<br>(Y = 0,353)</th><th>T calibrado<br>con tabla KG</th>'
            '<th>T<sub>adm</sub> adoptado<br>N·m</th></tr></thead><tbody>'
            + ''.join(filas) + '</tbody></table>')


def tabla_cota():
    c = R['cota_baja']
    filas = []
    motivos = {'SUS304L MIM': 'σ<sub>H lim</sub> = 0,40 × S45C (relación de KG aplicada también al contacto)',
               'Latón C3604B': 'σ<sub>H lim</sub> = 0,36 × S45C (bronce al estaño, Shigley tabla 14-7, frente a acero 170 HB)'}
    for k in c:
        filas.append(f'<tr><th>{NOM[k]}</th><td>{motivos[k]}</td>'
                     + ''.join(f'<td class="num">{n(MET[k][r]["T_adm"])}</td>'
                               f'<td class="num">{n(c[k][r])}</td>' for r in ('50', '100')) + '</tr>')
    return ('<table class="det"><thead><tr><th>Material</th><th>Hipótesis alternativa</th>'
            '<th>50 rpm<br>adoptado</th><th>50 rpm<br>cota baja</th><th>100 rpm<br>adoptado</th>'
            '<th>100 rpm<br>cota baja</th></tr></thead><tbody>' + ''.join(filas) + '</tbody></table>')


# ---------------------------------------------------------------------------
# Ejemplo paso a paso: S45C a 100 rpm
# ---------------------------------------------------------------------------
x = MET['S45C']['100']
b = G['b_ef']
ej = dict(
    b=n(b, 3), d=n(G['d'], 1), m=n(D['m'], 1), v=n(x['v_et'], 4), Kv=n(x['K_v'], 4),
    KHb=n(x['K_Hb'], 4), YNT=n(x['Y_NT'], 4), ZNT=n(x['Z_NT'], 4), ZE=n(x['Z_E'], 1),
    sF=n(x['sFlim'], 2), sH=n(x['sHlim'], 1), sFP=n(x['sFP'], 2), sHP=n(x['sHP'], 1),
    WF=n(x['W_F'], 2), WH=n(x['W_H'], 2), TF=n(x['T_F'], 4), TH=n(x['T_H'], 4),
    N=e(x['N']), J=n(F['J'], 2), I=n(F['I'], 3),
)
pr = R['prisionero']
T_max = max(v[r]['T_adm'] for v in MET.values() for r in RPM)
tau = 16 * T_max * 1000 / (3.141592653589793 * 3 ** 3)

CSS = '''
:root{--bg:#fcfcfb;--panel:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--line:#e4e3df;
--acc:#2a78d6;--accbg:#eef4fc;--warn:#b25e00;--warnbg:#fdf3e6;--ok:#1a7f4b;--okbg:#e9f6ef}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1a1a19;--panel:#222221;
--ink:#fff;--ink2:#c3c2b7;--muted:#9b9a93;--line:#3a3936;--acc:#3987e5;--accbg:#1d2a3a;--warn:#e0a060;
--warnbg:#33281b;--ok:#5cc08a;--okbg:#1b2e24}}
:root[data-theme="dark"]{--bg:#1a1a19;--panel:#222221;--ink:#fff;--ink2:#c3c2b7;--muted:#9b9a93;
--line:#3a3936;--acc:#3987e5;--accbg:#1d2a3a;--warn:#e0a060;--warnbg:#33281b;--ok:#5cc08a;--okbg:#1b2e24}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 "Source Sans 3","Segoe UI",system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:32px 16px 80px}
h1{font-size:30px;line-height:1.2;margin:0 0 6px}
h2{font-size:22px;margin:44px 0 10px;padding-top:10px;border-top:2px solid var(--line)}
h3{font-size:17px;margin:26px 0 6px}
p,li{color:var(--ink)}
.sub{color:var(--ink2);margin:0 0 18px}
.meta{color:var(--muted);font-size:13px}
table{border-collapse:collapse;width:100%;margin:10px 0 14px;font-size:13.5px;background:var(--panel)}
th,td{border:1px solid var(--line);padding:5px 7px;text-align:left;vertical-align:top}
thead th{background:var(--accbg);font-weight:600}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
table.res{font-size:15px}
table.res td.num{font-weight:600}
.wrap{overflow-x:auto}
figure{margin:16px 0 22px;background:var(--panel);border:1px solid var(--line);padding:10px}
figure img{max-width:100%;height:auto;display:block;margin:0 auto;background:#fff}
figure.small img{max-width:420px}
figcaption{font-size:13px;color:var(--ink2);margin-top:8px}
figcaption .src{display:block;color:var(--muted);font-size:12px}
.eq{font-family:"Cambria Math","STIX Two Math",Georgia,serif;font-size:16px;background:var(--panel);
border-left:3px solid var(--acc);padding:8px 14px;margin:10px 0;overflow-x:auto;white-space:nowrap}
.box{border:1px solid var(--line);border-left:4px solid var(--acc);background:var(--accbg);padding:12px 16px;margin:16px 0}
.box.warn{border-left-color:var(--warn);background:var(--warnbg)}
.box.ok{border-left-color:var(--ok);background:var(--okbg)}
.box h4{margin:0 0 4px;font-size:15px}
.nota{font-size:13px;color:var(--ink2)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:700px){.grid2{grid-template-columns:1fr}h1{font-size:24px}}
nav.toc{columns:2;font-size:14px;background:var(--panel);border:1px solid var(--line);padding:10px 18px}
nav.toc a{color:var(--acc);text-decoration:none}
code{font-size:13px}
@media print{body{background:#fff;font-size:11pt}main{max-width:none;padding:0}
h2,h3{break-before:auto;break-after:avoid}figure,table,.box,.eq{break-inside:avoid}
.wrap{overflow:visible}nav.toc{break-inside:avoid}}
@page{size:A4;margin:16mm 14mm}
'''

HTML = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mitras KG m0,5 z20</title>
<meta name="description" content="Torque admisible según Shigley (AGMA) de un par de engranajes cónicos rectos KG m 0,5, 20 dientes, a 90°, en todos los materiales del fabricante.">
<style>{CSS}</style></head><body><main>

<h1>Torque admisible de un par de engranajes cónicos KG m 0,5 × 20 dientes a 90°</h1>
<p class="sub">Análisis independiente según Shigley (capítulo 15, método AGMA para engranajes cónicos),
para todos los materiales en que KG ofrece la pieza, a 0, 0,5, 50 y 100 rpm.</p>
<p class="meta">Informe de cálculo · septiembre de 2026 · Cálculo reproducible: <code>tools/calculo.py</code></p>

<nav class="toc">
<a href="#s1">1. Resultado</a><br><a href="#s2">2. Datos y supuestos</a><br>
<a href="#s3">3. Producto KG y alcance de su dato</a><br><a href="#s4">4. Geometría</a><br>
<a href="#s5">5. Método de Shigley</a><br><a href="#s6">6. Factores adoptados</a><br>
<a href="#s7">7. Resistencia de cada material</a><br><a href="#s8">8. Cálculo paso a paso</a><br>
<a href="#s9">9. Resultados de todos los casos</a><br><a href="#s10">10. POM</a><br>
<a href="#s11">11. Sensibilidad</a><br><a href="#s12">12. Verificaciones adicionales</a><br>
<a href="#s13">13. Conclusiones</a><br><a href="#s14">14. Referencias y capturas</a>
</nav>

<h2 id="s1">1. Resultado</h2>
<p>Torque admisible <b>por engranaje</b> (el mismo en piñón y corona, relación 1:1), en N·m, con
confiabilidad del 99 %, factores de seguridad S<sub>F</sub> = S<sub>H</sub> = 1 (capacidad nominal AGMA),
vida de 10 años a 20 h por mes y temperatura hasta 40 °C. Cada valor es el menor entre la capacidad a flexión
del diente y la capacidad a picado del flanco.</p>
<div class="wrap">{tabla_resumen()}</div>
{fig('figuras/fig_resumen.png', 1, 'Torque admisible por material y velocidad.', 'cálculo propio, Shigley cap. 15 (metales) y Lewis/KHK (POM).')}

<div class="box">
<h4>Lectura rápida</h4>
<ul>
<li><b>S45C es el material más resistente</b>: {n(MET["S45C"]["50"]["T_adm"])} N·m a 50 rpm y
{n(MET["S45C"]["100"]["T_adm"])} N·m a 100 rpm. Lo limita el <b>picado del flanco</b>, que KG no publica para m 0,5.</li>
<li>El dato de KG para S45C (1,5 W a 100 rpm = {n(R["kg"]["S45C"]["100"])} N·m) es solo a flexión. La flexión según Shigley da
{n(MET["S45C"]["100"]["T_F"])} N·m, pero el picado da {n(MET["S45C"]["100"]["T_H"])} N·m:
<b>usar el dato de KG sobrestima la capacidad real del par en un {n((R["kg"]["S45C"]["100"] / MET["S45C"]["100"]["T_adm"] - 1) * 100, 0)} %</b>.</li>
<li>El latón y el SUS304L MIM quedan alrededor de 0,04–0,05 N·m. El POM, alrededor de 0,03 N·m.</li>
<li>Si el BLDC invierte el sentido de giro (o frena la carga), la flexión pasa a ser alternada y su capacidad baja al 70 %
(columna «ambos sentidos»).</li>
<li>El torque «a 0 rpm» (carga estática o de retención, hasta 10<sup>4</sup> aplicaciones) admite más del doble que en servicio continuo en los metales.
En el POM una retención sostenida produce fluencia lenta (creep), y el valor tabulado no la cubre.</li>
</ul></div>

<h2 id="s2">2. Datos del pedido y supuestos</h2>
<table class="det"><thead><tr><th>Dato</th><th>Valor</th><th>Origen</th></tr></thead><tbody>
<tr><td>Par</td><td>Dos engranajes cónicos rectos iguales (mitra), relación 1:1, ejes a 90°</td><td>pedido</td></tr>
<tr><td>Fabricante y producto</td><td>KG (協育歯車工業, KG STOCK GEARS), serie M, m = 0,5 mm, z = 20</td><td>pedido y catálogo</td></tr>
<tr><td>Velocidades</td><td>0, 0,5, 50 y 100 rpm</td><td>pedido (ver nota)</td></tr>
<tr><td>Uso</td><td>20 h seguidas una vez por mes</td><td>pedido</td></tr>
<tr><td>Vida de diseño</td><td>10 años: 2400 h. Ciclos por diente: 7,2·10<sup>6</sup> a 50 rpm y 1,44·10<sup>7</sup> a 100 rpm</td><td><b>supuesto</b> (ver Figura 23 para otras vidas)</td></tr>
<tr><td>Carga a 0 rpm</td><td>Torque estático o de retención aplicado hasta 10<sup>4</sup> veces en la vida</td><td><b>supuesto</b></td></tr>
<tr><td>Motor y carga</td><td>BLDC con perfil trapezoidal suave: fuente uniforme; carga conducida supuesta uniforme</td><td>pedido</td></tr>
<tr><td>Lubricación</td><td>Compartimento engrasado</td><td>pedido</td></tr>
<tr><td>Temperatura</td><td>30–40 °C (se calcula a 40 °C)</td><td>pedido</td></tr>
<tr><td>Montaje</td><td>Ambos engranajes en voladizo (ninguno entre apoyos), el caso típico de estas piezas con cubo y prisioneros</td><td><b>supuesto</b> conservador</td></tr>
</tbody></table>
<p class="nota"><b>Nota sobre las velocidades.</b> El pedido dice «0, 50 rpm y 100 rpm». Se leyó como 0, 50 y 100 rpm,
pero con coma decimal también puede leerse «0,50 rpm y 100 rpm». Para no dejar dudas se calcularon los cuatro casos: 0 (estático), 0,5, 50 y 100 rpm.</p>

<h2 id="s3">3. Producto KG y alcance de su dato de capacidad</h2>
<h3>3.1 Materiales en que KG ofrece la mitra m 0,5 × 20</h3>
<p>El catálogo vigente de mitras de KG (KG4001, serie M, código <i>M·módulo·material·dientes</i>) ofrece la mitra
m 0,5 de 20 dientes en tres materiales: S45C, inoxidable SUS304L por inyección de metal (MIM) y latón C3604B. El POM azul y el blanco
empiezan en m 0,8 y m 1. El catálogo anterior (KG3001, 2020) incluía además una versión de <b>POM negro inyectado</b>, M50DM20-1103,
que también se analiza.</p>
{fig('capturas/kg_codigo_producto.png', 2, 'Lectura del código de producto de las mitras KG. Materiales: S = S45C, SU = SUS304, B = latón, BP = POM azul, D = POM blanco.', 'KG, catálogo KG4001, p. 233.')}
{fig('capturas/kg_s45c_datos.png', 3, 'Mitra S45C, m 0,5, z 20 (M50S20). Precisión JIS B1704 grado 3, sin tratamiento térmico, ancho b = 2,5 mm, d = 10 mm. La tabla de potencia usa la fórmula JGMA.', 'KG, catálogo KG4001, p. 260.')}
{fig('capturas/kg_s45c_potencia.png', 4, 'Potencia admisible de M50S20: 1,5 W a 100 rpm a flexión. La columna de resistencia superficial (歯面強さ) está vacía («–») para m 0,5.', 'KG, catálogo KG4001, p. 261.')}
{fig('capturas/kg_mim_datos.png', 5, 'Mitra SUS304L MIM, m 0,5, z 20 (M50SUM20*1103). Se vende sin prisioneros y solo puede combinarse con otra mitra MIM.', 'KG, catálogo KG4001, p. 270.')}
{fig('capturas/kg_mim_potencia.png', 6, 'Potencia admisible de M50SUM20 (0,5 W a 100 rpm) y relación orientativa de resistencia entre materiales: S45C 1, SUS304 0,6, MIM 0,4.', 'KG, catálogo KG4001, p. 271.')}
{fig('capturas/kg_mim_potencia_2020.png', 7, 'En el catálogo 2020 la misma tabla MIM se declara como «valor experimental del ensayo de durabilidad de KG».', 'KG, catálogo KG3001, p. 401.')}
{fig('capturas/kg_laton_datos.png', 8, 'Mitra de latón C3604B, m 0,5, z 20 (M50B20). JIS B1704 grado 4. KG no publica tabla de potencia para esta pieza.', 'KG, catálogo KG4001, p. 272.')}
{fig('capturas/kg_pom_datos.png', 9, 'Mitra de POM negro inyectado m 0,5, z 20 (M50DM20-1103), catálogo 2020, sin tabla de potencia.', 'KG, catálogo KG3001, p. 400.')}

<h3>3.2 Qué cubre y qué no cubre el dato de KG</h3>
{tabla_kg()}
{fig('capturas/kg_condiciones_conicos.png', 10, 'Condiciones de cálculo de las tablas de KG para cónicos: JGMA 403-01 (flexión) y 404-01 (superficie); S45C sin tratamiento σ<sub>F lim</sub> = 19 kgf/mm², σ<sub>H lim</sub> = 54 kgf/mm²; SUS304 σ<sub>F lim</sub> = 10,5 kgf/mm²; ≥ 10<sup>7</sup> ciclos; motor uniforme y choque moderado de la máquina conducida (K<sub>O</sub> = 1,25); baño de aceite de 100 cSt; ambos engranajes en voladizo (K<sub>Mβ</sub> = 1,8); K<sub>R</sub> = 1,2, C<sub>R</sub> = 1,15. Con carga en ambos sentidos, 2/3 del valor de tabla.', 'KG, KG5001 Material de referencia, p. 18.')}
{fig('capturas/kg_jgma403_alcance.png', 11, 'Alcance declarado de JGMA 403-01/404-01: módulo exterior de 1,5 a 25 mm. La mitra m 0,5 queda fuera del rango de la norma que usa KG.', 'KG, Technical Data, cap. 10.2, p. 137.', 'small')}
{fig('capturas/kg_conversion_potencia.png', 12, 'Conversión de potencia a torque usada en este informe: T [N·m] = 9549,7·kW/n.', 'KG, KG5001 Material de referencia, p. 20.')}

<div class="box warn"><h4>Por qué el dato de KG no alcanza</h4>
<ol>
<li><b>Solo da flexión.</b> Para m 0,5 la columna de resistencia superficial (picado) está vacía, y en este par el picado es lo que limita al S45C.</li>
<li><b>La norma que aplica (JGMA 403/404) empieza en m 1,5.</b> Para m 0,5 se extrapola fuera de su rango.</li>
<li><b>Sus condiciones no son las de este caso</b>: choque moderado (K<sub>O</sub> = 1,25), baño de aceite, ≥ 10<sup>7</sup> ciclos y carga en un solo sentido.</li>
<li><b>El latón y el POM no tienen dato.</b> El valor del MIM es experimental o no indica sus condiciones.</li>
</ol></div>

<h2 id="s4">4. Geometría</h2>
<div class="grid2">
{fig('figuras/fig_geometria.png', 13, 'Corte axial esquemático del par con las cotas del catálogo.', 'elaboración propia con datos de KG.')}
<table class="det"><thead><tr><th>Magnitud</th><th>Valor</th></tr></thead><tbody>
<tr><td>Módulo exterior m<sub>et</sub></td><td>0,5 mm</td></tr>
<tr><td>Dientes z<sub>1</sub> = z<sub>2</sub></td><td>20</td></tr>
<tr><td>Ángulo de presión φ</td><td>20°</td></tr>
<tr><td>Diámetro primitivo exterior d<sub>e</sub> = m·z</td><td>{n(G["d"], 1)} mm</td></tr>
<tr><td>Ángulo de paso δ = arctan(z<sub>1</sub>/z<sub>2</sub>)</td><td>45°</td></tr>
<tr><td>Distancia de cono exterior R<sub>e</sub> = d/(2 sen δ)</td><td>{n(G["Re"], 3)} mm</td></tr>
<tr><td>Ancho de cara del catálogo b</td><td>{n(G["b"], 1)} mm (b/R<sub>e</sub> = {n(G["ratio_b_Re"], 3)})</td></tr>
<tr><td>Ancho máximo recomendado por Shigley: min(0,3 R<sub>e</sub>; 10 m)</td><td>{n(G["b_max"], 3)} mm</td></tr>
<tr><td><b>Ancho efectivo usado</b> b<sub>ef</sub></td><td><b>{n(G["b_ef"], 3)} mm</b></td></tr>
<tr><td>Diámetro primitivo medio d<sub>m</sub> = d − b sen δ</td><td>{n(G["dm"], 3)} mm</td></tr>
<tr><td>Dientes virtuales z<sub>v</sub> = z/cos δ</td><td>{n(G["zv"], 2)}</td></tr>
<tr><td>Velocidad tangencial exterior a 100 rpm</td><td>{n(MET["S45C"]["100"]["v_et"], 4)} m/s</td></tr>
</tbody></table></div>
<p>El ancho de catálogo (2,5 mm) supera el 30 % de la distancia de cono que Shigley recomienda como máximo. El tramo de cara
más cercano al vértice trabaja poco, por eso <b>solo se acreditan 0,3·R<sub>e</sub> = {n(G["b_max"], 2)} mm</b>. La Figura 18 muestra
el efecto de acreditar el ancho completo.</p>

<h2 id="s5">5. Método de Shigley (cap. 15, AGMA para cónicos, unidades SI)</h2>
<p>Shigley presenta en el capítulo 15 las ecuaciones de la norma AGMA para engranajes cónicos rectos
(ANSI/AGMA 2003-B97). Se usan las versiones en SI: W<sup>t</sup> es la fuerza tangencial en el diámetro primitivo
exterior, T = W<sup>t</sup>·d<sub>e</sub>/2.</p>
<h3>Picado (esfuerzo de contacto)</h3>
<div class="eq">σ<sub>H</sub> = Z<sub>E</sub> · [ W<sup>t</sup> · K<sub>A</sub> K<sub>v</sub> K<sub>Hβ</sub> Z<sub>x</sub> Z<sub>xc</sub> / ( b · d<sub>e1</sub> · Z<sub>I</sub> ) ]<sup>1/2</sup>
&nbsp;&nbsp;≤&nbsp;&nbsp; σ<sub>HP</sub> = σ<sub>H lim</sub> Z<sub>NT</sub> Z<sub>W</sub> / ( S<sub>H</sub> K<sub>θ</sub> Z<sub>Z</sub> )</div>
<h3>Flexión (esfuerzo en el pie del diente)</h3>
<div class="eq">σ<sub>F</sub> = ( W<sup>t</sup> / b ) · ( K<sub>A</sub> K<sub>v</sub> / m<sub>et</sub> ) · ( Y<sub>x</sub> K<sub>Hβ</sub> / ( Y<sub>β</sub> Y<sub>J</sub> ) )
&nbsp;&nbsp;≤&nbsp;&nbsp; σ<sub>FP</sub> = σ<sub>F lim</sub> Y<sub>NT</sub> / ( S<sub>F</sub> K<sub>θ</sub> Y<sub>Z</sub> )</div>
<h3>Despeje del torque admisible</h3>
<div class="eq">T<sub>F</sub> = (d<sub>e</sub>/2) · σ<sub>FP</sub> · b · m<sub>et</sub> · Y<sub>β</sub> Y<sub>J</sub> / ( K<sub>A</sub> K<sub>v</sub> Y<sub>x</sub> K<sub>Hβ</sub> )</div>
<div class="eq">T<sub>H</sub> = (d<sub>e</sub>/2) · (σ<sub>HP</sub>/Z<sub>E</sub>)<sup>2</sup> · b · d<sub>e</sub> · Z<sub>I</sub> / ( K<sub>A</sub> K<sub>v</sub> K<sub>Hβ</sub> Z<sub>x</sub> Z<sub>xc</sub> )
&nbsp;&nbsp;&nbsp;&nbsp; T<sub>adm</sub> = min(T<sub>F</sub>, T<sub>H</sub>)</div>
<p class="nota">Los esfuerzos σ<sub>F</sub> y σ<sub>H</sub> de AGMA no son tensiones «reales». Se comparan solo contra los
admisibles σ<sub>F lim</sub> y σ<sub>H lim</sub> del mismo método, que ya incluyen su propia calibración (y la confiabilidad del 99 %).</p>

<h2 id="s6">6. Factores adoptados</h2>
<div class="wrap"><table class="det"><thead><tr><th>Factor (Shigley US / SI)</th><th>Valor</th><th>Justificación</th></tr></thead><tbody>
<tr><td>Sobrecarga K<sub>o</sub> / K<sub>A</sub></td><td>{n(F["K_A"], 2)}</td><td>Tabla de factores de sobrecarga del cap. 15: motor uniforme y carga uniforme. El BLDC con perfil trapezoidal suave no produce golpes. Con carga conducida de choque leve sería 1,25 (Figura 18).</td></tr>
<tr><td>Dinámico K<sub>v</sub></td><td>{n(MET["S45C"]["50"]["K_v"], 4)} (50 rpm), {n(MET["S45C"]["100"]["K_v"], 4)} (100 rpm)</td><td>K<sub>v</sub> = [(A + √(200 v<sub>et</sub>))/A]<sup>B</sup>, B = 0,25(12 − Q<sub>v</sub>)<sup>2/3</sup>, A = 50 + 56(1 − B), con Q<sub>v</sub> = {F["Q_v"]} (conservador frente a JIS B1704 grados 3–4). A 0,05 m/s el efecto dinámico es despreciable.</td></tr>
<tr><td>Tamaño a flexión K<sub>s</sub> / Y<sub>x</sub></td><td>0,5</td><td>Y<sub>x</sub> = 0,5 para m<sub>et</sub> &lt; 1,6 mm.</td></tr>
<tr><td>Tamaño a picado C<sub>s</sub> / Z<sub>x</sub></td><td>0,5</td><td>Z<sub>x</sub> = 0,5 para b &lt; 12,7 mm.</td></tr>
<tr><td>Distribución de carga K<sub>m</sub> / K<sub>Hβ</sub></td><td>{n(MET["S45C"]["100"]["K_Hb"], 4)}</td><td>K<sub>Hβ</sub> = K<sub>mb</sub> + 5,6·10<sup>−6</sup> b², con K<sub>mb</sub> = 1,25 (ningún engranaje entre apoyos).</td></tr>
<tr><td>Coronamiento C<sub>xc</sub> / Z<sub>xc</sub></td><td>{n(F["Z_xc"], 1)}</td><td>1,5 solo para dientes correctamente coronados. Una mitra de stock m 0,5 no garantiza coronamiento, así que se toma 2,0.</td></tr>
<tr><td>Curvatura longitudinal K<sub>x</sub> / Y<sub>β</sub></td><td>1</td><td>Dientes rectos.</td></tr>
<tr><td>Geometría a flexión J / Y<sub>J</sub></td><td>{ej["J"]}</td><td>Fig. 15-7 (φ = 20°, Σ = 90°), 20 dientes contra 20. Es una lectura de gráfico (±0,01). Como referencia, el Ejemplo 15-1 de Shigley da J = 0,216 para una mitra de 25 dientes.</td></tr>
<tr><td>Geometría a picado I / Z<sub>I</sub></td><td>{ej["I"]}</td><td>Fig. 15-6, 20 dientes contra 20 (±0,003). Ejemplo 15-1: I = 0,065 para 25 dientes.</td></tr>
<tr><td>Ciclos a flexión K<sub>L</sub> / Y<sub>NT</sub></td><td>ver Figura 15</td><td>Fig. 15-9: 2,7 (10<sup>2</sup>–10<sup>3</sup>); 6,1514 N<sup>−0,1192</sup> (10<sup>3</sup>–3·10<sup>6</sup>); 1,6831 N<sup>−0,0323</sup> (3·10<sup>6</sup>–10<sup>10</sup>).</td></tr>
<tr><td>Ciclos a picado C<sub>L</sub> / Z<sub>NT</sub></td><td>ver Figura 15</td><td>Fig. 15-8: 2,0 (10<sup>3</sup>–10<sup>4</sup>); 3,4822 N<sup>−0,0602</sup> (10<sup>4</sup>–10<sup>10</sup>).</td></tr>
<tr><td>Confiabilidad K<sub>R</sub> / Y<sub>Z</sub> y C<sub>R</sub> / Z<sub>Z</sub></td><td>1,0 y 1,0</td><td>R = 0,99: Y<sub>Z</sub> = 0,50 − 0,25 log(1 − R) = 1,0; Z<sub>Z</sub> = √Y<sub>Z</sub>.</td></tr>
<tr><td>Temperatura K<sub>T</sub> / K<sub>θ</sub></td><td>1</td><td>Temperatura ≤ 120 °C (en este caso, 40 °C).</td></tr>
<tr><td>Relación de dureza C<sub>H</sub> / Z<sub>W</sub></td><td>1</td><td>Piñón y corona del mismo material.</td></tr>
<tr><td>Seguridad S<sub>F</sub>, S<sub>H</sub></td><td>1</td><td>Capacidad nominal AGMA. El margen lo dan R = 0,99 y los supuestos conservadores. Para un margen explícito, dividir T<sub>adm</sub> por el factor deseado.</td></tr>
</tbody></table></div>
{fig('figuras/fig_ciclos.png', 15, 'Factores de ciclos de Shigley (Figs. 15-8 y 15-9) y punto de trabajo de cada velocidad (10 años). Para los metales no carburizados se usa la curva general como aproximación.', 'ecuaciones de Shigley, figs. 15-8 y 15-9, graficadas por el autor.')}
<p class="nota">A 0 rpm los ciclos no dependen de la velocidad sino de cuántas veces se aplica el torque (arranques, retenciones).
Se tomó N = 10<sup>4</sup>. En ese tramo las curvas de Shigley dan Y<sub>NT</sub> = 2,05 y Z<sub>NT</sub> = 2,0. Además se verificó que el esfuerzo
admisible a flexión resultante quede por debajo de la fluencia de cada material (S45C 134 MPa &lt; 345 MPa; latón 65 &lt; 250; MIM 54 &lt; 175).</p>

<h2 id="s7">7. Resistencia admisible de cada material</h2>
<p>Shigley tabula σ<sub>F lim</sub> y σ<sub>H lim</sub> para cónicos solo en aceros y fundiciones (Figs. 15-12 y 15-13,
tablas del cap. 15). El S45C sin tratamiento entra directamente como <b>acero templado total grado 1 de 170 HB</b>
(el extremo inferior del rango JIS G4051 para S45C normalizado, 167–229 HB):</p>
<div class="eq">σ<sub>F lim</sub> = 0,30·HB + 14,48 = {n(R["referencia"]["sFlim"], 1)} MPa &nbsp;&nbsp;&nbsp;
σ<sub>H lim</sub> = 2,35·HB + 162,89 = {n(R["referencia"]["sHlim"], 1)} MPa</div>
<p>El SUS304L MIM y el latón no están en las tablas de Shigley. Se los escala a partir del S45C con el indicador más
defendible disponible para cada uno:</p>
<ul>
<li><b>Flexión.</b> MIM: la relación de resistencia que publica el propio KG (0,4 × S45C, Figura 6). Latón: la relación de límites de fatiga,
138 MPa (C36000 semiduro, 10<sup>8</sup> ciclos) contra 0,5·S<sub>ut</sub> = 285 MPa del S45C (criterio de Shigley para aceros), = 0,48.</li>
<li><b>Picado.</b> La resistencia a picado de AGMA crece con la dureza superficial. Se escala por dureza Brinell: MIM 120 HB, latón 100 HB, frente a 170 HB.
La sección 11 da cotas más pesimistas.</li>
</ul>
<div class="wrap">{tabla_materiales()}</div>
<p class="nota">Z<sub>E</sub> = {{1/[π·2(1 − ν²)/E]}}<sup>1/2</sup> para dos engranajes del mismo material.</p>

<h2 id="s8">8. Cálculo paso a paso: S45C a 100 rpm</h2>
<ol>
<li>Ciclos: N<sub>L</sub> = 100 rpm · 60 · 20 h/mes · 12 · 10 años = {ej["N"]}.</li>
<li>v<sub>et</sub> = π·d·n/60 000 = {ej["v"]} m/s → K<sub>v</sub> = {ej["Kv"]}.</li>
<li>K<sub>Hβ</sub> = 1,25 + 5,6·10<sup>−6</sup>·{ej["b"]}² = {ej["KHb"]}.</li>
<li>Y<sub>NT</sub> = 1,6831·N<sup>−0,0323</sup> = {ej["YNT"]} ; Z<sub>NT</sub> = 3,4822·N<sup>−0,0602</sup> = {ej["ZNT"]}.</li>
<li>σ<sub>FP</sub> = {ej["sF"]}·{ej["YNT"]} / (1·1·1) = <b>{ej["sFP"]} MPa</b> ; σ<sub>HP</sub> = {ej["sH"]}·{ej["ZNT"]}·1 / (1·1·1) = <b>{ej["sHP"]} MPa</b>.</li>
<li>Flexión: W<sub>F</sub> = σ<sub>FP</sub>·b·m·Y<sub>J</sub> / (K<sub>A</sub>K<sub>v</sub>Y<sub>x</sub>K<sub>Hβ</sub>)
= {ej["sFP"]}·{ej["b"]}·{ej["m"]}·{ej["J"]} / (1·{ej["Kv"]}·0,5·{ej["KHb"]}) = <b>{ej["WF"]} N</b> → T<sub>F</sub> = W·d/2 = <b>{ej["TF"]} N·m</b>.</li>
<li>Picado: W<sub>H</sub> = (σ<sub>HP</sub>/Z<sub>E</sub>)²·b·d·Z<sub>I</sub> / (K<sub>A</sub>K<sub>v</sub>K<sub>Hβ</sub>Z<sub>x</sub>Z<sub>xc</sub>)
= ({ej["sHP"]}/{ej["ZE"]})²·{ej["b"]}·{ej["d"]}·{ej["I"]} / (1·{ej["Kv"]}·{ej["KHb"]}·0,5·2,0) = <b>{ej["WH"]} N</b> → T<sub>H</sub> = <b>{ej["TH"]} N·m</b>.</li>
<li><b>T<sub>adm</sub> = min({ej["TF"]}; {ej["TH"]}) = {ej["TH"]} N·m</b>, limitado por picado.</li>
</ol>

<h2 id="s9">9. Resultados de todos los casos metálicos</h2>
<div class="wrap">{tabla_detalle()}</div>
{fig('figuras/fig_modos.png', 16, 'A 100 rpm: capacidad a flexión y a picado según Shigley, y valor de la tabla KG. En S45C el picado limita y queda muy por debajo del dato de catálogo.', 'cálculo propio; KG, catálogo KG4001 pp. 261 y 271.')}
{fig('figuras/fig_rpm.png', 17, 'Torque admisible en función de la velocidad, con los puntos de las tablas KG. El quiebre cerca de 20 rpm es el cambio de tramo de la curva de ciclos de flexión (3·10<sup>6</sup> ciclos).', 'cálculo propio; KG.')}

<h2 id="s10">10. POM (acetal) inyectado: fuera del alcance de AGMA</h2>
<p>Las ecuaciones AGMA de Shigley valen solo para metales. Para plásticos, tanto KG («ルイスの式», en sus tablas de POM)
como KHK usan la ecuación de Lewis (la base del cap. 14 de Shigley) con un esfuerzo admisible propio del material y factores de servicio:</p>
<div class="eq">F = m · y · b · σ<sub>b adm</sub> · (R<sub>e</sub> − b)/R<sub>e</sub> &nbsp;&nbsp;&nbsp; σ<sub>b adm</sub> = σ<sub>b</sub>(N) · K<sub>V</sub> K<sub>T</sub> K<sub>L</sub> K<sub>M</sub> / C<sub>S</sub> &nbsp;&nbsp;&nbsp; T = F·d/2</div>
<p>Factores: σ<sub>b</sub>(N) de la curva m 0,8 de KHK Fig. 11.3 (la de menor módulo publicada, que es conservadora para m 0,5); K<sub>V</sub> = 1,4 (v ≈ 0),
K<sub>T</sub> = 0,80 (40 °C), K<sub>L</sub> = 1 (engrase inicial), K<sub>M</sub> = 0,75 (POM contra POM), C<sub>S</sub> = 1,25 (carga uniforme, 20 h seguidas);
y = 0,597 para z<sub>v</sub> = 28 (KHK); (R<sub>e</sub> − b)/R<sub>e</sub> = {n(POM["100"]["fb"], 3)}.</p>
<p>Se obtienen tres estimaciones y se adopta la menor:</p>
<ul><li><b>Método KHK completo.</b></li>
<li><b>Lewis con el factor de forma Y de Shigley</b> (tabla 14-2, 28 dientes: 0,353), más conservador.</li>
<li><b>Calibrado con el propio KG.</b> La tabla del POM azul M80BP20 (m 0,8, b 3,7 mm) da 1,20 W a 100 rpm = {n(POM["100"]["T08_kg"])} N·m. Se lo escala a m 0,5 por m·b·(R<sub>e</sub> − b)/R<sub>e</sub>·d y por la curva σ<sub>b</sub>(N).</li></ul>
<div class="wrap">{tabla_pom()}</div>
<p class="nota">A 0 rpm el valor queda por debajo del de 0,5 rpm porque en carga estática no se acredita el factor de velocidad K<sub>V</sub> = 1,4
que KHK concede a baja velocidad.</p>
<div class="grid2">
{fig('capturas/Fig.11.3.jpg', 19, 'Esfuerzo de flexión admisible de Duracon (POM) en función de los ciclos.', 'KHK, Design of Plastic Gears, Fig. 11.3.')}
{fig('capturas/Fig.-11.5-Temperature-factor-KT.jpg', 20, 'Factor de temperatura K<sub>T</sub> (1 a 20 °C; ≈ 0,80 a 40 °C).', 'KHK, Fig. 11.5.')}
{fig('capturas/Table-11.7-Working-factor-CS.jpg', 21, 'Factor de servicio C<sub>S</sub>.', 'KHK, tabla 11.7.')}
{fig('capturas/Table-11.9-Material-factor-KM.jpg', 22, 'Factor de combinación de materiales K<sub>M</sub>.', 'KHK, tabla 11.9.')}
</div>
<div class="box warn"><h4>Advertencias del POM</h4>
El POM absorbe humedad y se dilata con la temperatura, de modo que el juego cambia. Con torque sostenido a 40 °C además fluye (creep):
el valor a «0 rpm» vale para aplicaciones breves, no para retener carga durante horas. La grasa debe ser compatible con acetal.</div>

<h2 id="s11">11. Sensibilidad a los supuestos</h2>
{fig('figuras/fig_sensibilidad.png', 18, 'Variación del torque admisible del S45C a 100 rpm al cambiar cada supuesto entre su valor base y uno alternativo. J no cambia el resultado porque el que limita es el picado.', 'cálculo propio.')}
{fig('figuras/fig_vida.png', 23, 'Torque admisible a 100 rpm en función de la vida supuesta (20 h por mes).', 'cálculo propio.')}
<h3>Cotas bajas para los materiales fuera de las tablas de Shigley</h3>
<div class="wrap">{tabla_cota()}</div>
<p class="nota">Si se busca el valor más seguro para MIM o latón, use la cota baja. La diferencia muestra cuánto depende el resultado de la
resistencia a picado supuesta para materiales que Shigley no tabula.</p>

<h2 id="s12">12. Verificaciones adicionales</h2>
<ul>
<li><b>Prisioneros (fijación al eje).</b> Shigley tabla 7-4: un prisionero n.º 2 (Ø 2,18 mm, por debajo del M2,5) sujeta alrededor de 85 lbf = {n(pr["F"], 0)} N.
Sobre un eje de Ø 3 mm son {n(pr["T_uno"], 2)} N·m por tornillo, o {n(pr["T_seguro"], 2)} N·m con factor 2. Eso supera el torque de los dientes, así que la
fijación no limita, siempre que el eje tenga un plano para el prisionero. En latón y MIM la rosca es del material blando, y la versión MIM se entrega sin prisioneros.</li>
<li><b>Eje de Ø 3 mm.</b> Con el mayor torque de la tabla ({n(T_max)} N·m), τ = 16T/(πd³) = {n(tau, 1)} MPa, admisible para un eje de acero.</li>
<li><b>Lubricación con grasa a baja velocidad.</b> A 0,03–0,05 m/s no se forma película elastohidrodinámica. El modo de falla real más probable a largo plazo es el
<b>desgaste</b> más que el picado clásico, y ninguno de los dos métodos (AGMA, JGMA) lo calcula. Conviene una grasa con aditivos EP para acero, y
compatible con plástico si se usa POM, y verificar el juego tras las primeras campañas.</li>
<li><b>Temperatura.</b> A 30–40 °C no hay reducción para los metales (K<sub>θ</sub> = 1). Para el POM se aplicó K<sub>T</sub> = 0,80.</li>
<li><b>Perfil trapezoidal del BLDC.</b> El torque a usar es el <b>pico de la fase de aceleración</b> (carga más inercia reflejada), no el de régimen. Si en la
desaceleración la carga arrastra al motor, los flancos opuestos también trabajan: use la columna «ambos sentidos».</li>
</ul>

<h2 id="s13">13. Conclusiones</h2>
<div class="box ok"><ol>
<li>Con Shigley (AGMA, R = 0,99, S = 1, 10 años), el par de mitras KG m 0,5 × 20 admite como máximo:
<b>S45C {n(MET["S45C"]["50"]["T_adm"])} N·m a 50 rpm y {n(MET["S45C"]["100"]["T_adm"])} N·m a 100 rpm</b>;
latón {n(MET["Latón C3604B"]["50"]["T_adm"])} y {n(MET["Latón C3604B"]["100"]["T_adm"])} N·m;
SUS304L MIM {n(MET["SUS304L MIM"]["50"]["T_adm"])} y {n(MET["SUS304L MIM"]["100"]["T_adm"])} N·m;
POM {n(POM["50"]["T_adm"])} y {n(POM["100"]["T_adm"])} N·m.</li>
<li>En S45C limita el picado, que KG no publica. El dato de catálogo (0,143 N·m a flexión) no debe usarse como capacidad del par.</li>
<li>La capacidad casi no cambia entre 50 y 100 rpm: a esta velocidad no hay efecto dinámico, y lo único que cambia es el número de ciclos.</li>
<li>A 0 rpm (estático, ≤ 10<sup>4</sup> aplicaciones) la capacidad de los metales es 2 a 2,5 veces la de servicio. A 0,5 rpm, 1,6 a 2 veces.</li>
<li><b>Recomendación:</b> S45C, con un torque de trabajo pico que no supere T<sub>adm</sub> dividido por el margen que se quiera tener
(por ejemplo, 1,5 → ≈ {n(MET["S45C"]["100"]["T_adm"] / 1.5)} N·m a 100 rpm). Si se necesita más, el paso natural es la mitra m 0,8 (M80S20) o m 1.</li>
</ol></div>

<h2 id="s14">14. Referencias y capturas</h2>
<ol>
<li>Budynas, R. G. y Nisbett, J. K. <i>Diseño en ingeniería mecánica de Shigley</i>, 10.ª ed., McGraw-Hill. Cap. 15 «Engranes cónicos y de tornillo sinfín»
(ecuaciones AGMA de esfuerzo en SI, Figs. 15-6, 15-7, 15-8, 15-9, 15-12, 15-13, Ejemplo 15-1); cap. 14 (Lewis, tabla 14-2, tabla 14-7); cap. 6 (S′<sub>e</sub> = 0,5 S<sub>ut</sub>); tabla 7-4 (prisioneros).</li>
<li>KG (協育歯車工業). Catálogo KG4001, sección マイタギヤ, pp. 233, 260–276. <a href="https://www.kggear.co.jp/wp-content/uploads/2022/11/KG4001WEB-7.pdf">KG4001WEB-7.pdf</a></li>
<li>KG. Catálogo KG3001, pp. 379–444. <a href="https://www.kggear.co.jp/wp-content/uploads/KG3001_web_0009.pdf">KG3001_web_0009.pdf</a></li>
<li>KG. Material de referencia KG5001, pp. 18 y 20. <a href="https://www.kggear.co.jp/wp-content/uploads/2024/06/KG5001JP_reference.pdf">KG5001JP_reference.pdf</a></li>
<li>KG. <i>Technical Data Note</i>, cap. 10.2. <a href="https://www.kggear.co.jp/en/wp-content/themes/bizvektor-global-edition/pdf/TechnicalData_KGSTOCKGEARS.pdf">TechnicalData_KGSTOCKGEARS.pdf</a></li>
<li>KHK. <i>Design of Plastic Gears</i>. <a href="https://khkgears.net/new/gear_knowledge/gear_technical_reference/design-of-plastic-gears.html">khkgears.net</a></li>
<li>Copper Development Association. C36000 Free-Cutting Brass (resistencia a la fatiga del latón semiduro). <a href="https://www.copper.org/applications/rodbar/alloy360/free_cutting.html">copper.org</a></li>
</ol>
<div class="box warn"><h4>Sobre las capturas del libro de Shigley</h4>
Las capturas del fabricante (Figuras 2–12) están tomadas de los PDF oficiales de KG, y las de KHK de su sitio. <b>No se incluyen capturas del libro de Shigley</b>
porque no hay una copia licenciada del libro disponible en este entorno. En su lugar, las ecuaciones de Shigley aparecen transcritas (sección 5), las
Figs. 15-8 y 15-9 se reconstruyeron desde sus ecuaciones (Figura 15) y cada factor cita su figura o tabla. Para completar el informe con las capturas, basta
agregar al repositorio las páginas del cap. 15 (Figs. 15-6 y 15-7 para J e I, y la tabla de K<sub>A</sub>) y regenerar.</div>
</main></body></html>
'''

# Renumera las figuras en orden de aparición y actualiza las referencias.
import re  # noqa: E402
orden = re.findall(r'<b>Figura (\d+)\.</b>', HTML)
mapa = {old: str(i + 1) for i, old in enumerate(orden)}
assert len(mapa) == len(orden), 'número de figura repetido'
HTML = re.sub(r'(Figuras? )(\d+)(–(\d+))?',
              lambda m: m.group(1) + mapa.get(m.group(2), m.group(2))
              + (('–' + mapa.get(m.group(4), m.group(4))) if m.group(3) else ''),
              HTML)

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write(HTML)
print(OUT, len(HTML) // 1024, 'KiB')
