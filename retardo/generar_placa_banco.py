import re, html
SP='/tmp/claude-0/-home-user-prueba/72c9e2c6-9447-55de-846e-f400757c54e2/scratchpad/'
W,H=33,16; P=22; ML=210; MT=40
def X(i,m=False): return ML+((W-1-i) if m else i)*P
def Y(j): return MT+j*P
SVGW=ML*2+(W-1)*P; SVGH=MT+(H-1)*P+130

bornes=[
 ("J1",[(1,1),(1,3)],["+ fuente (por la llave de carga)","pulsador (otro lado al + de la pila)"],"L","ENTRADAS"),
 ("J2",[(1,11),(1,13)],["− fuente","− pila 9 V"],"L","MASAS"),
 ("J4",[(31,3),(31,5)],["retorno del iniciador","al iniciador"],"R","INICIADOR"),
 ("J3",[(31,7),(31,9)],["retorno de la llave","a la llave de armado"],"R","ARMADO"),
]
axial=[ # ref,label,a,b,thick(holes)
 ("R1","100 Ω 3 W",(24,0),(24,6),2.0),
 ("R2","1 kΩ",(4,3),(9,3),0.8),
 ("R3","10 kΩ",(11,5),(11,9),0.8),
 ("RS","0,1 Ω",(14,7),(14,12),1.3),
]
bncs=[("BNC1","CH1 · corriente",18,(18,13),[(16,15),(20,15)],"ch1"),("BNC2","CH2 · tensión de C1",29,(29,13),[(27,15),(31,15)],"ch2")]
C1=dict(c=(26,9),neg=(25,9),pos=(27,9),r=2.15)
Q1=dict(G=(12,5),D=(13,5),S=(14,5))
thick=[[(27,9),(31,9)],[(31,5),(31,7)],[(13,5),(13,3),(31,3)],[(14,5),(14,7)],[(14,12),(14,15)],[(14,15),(25,15)],[(25,9),(25,15)]]
thin=[[(1,1),(1,0),(24,0)],[(24,6),(29,6),(29,13)],[(1,3),(4,3)],[(9,3),(9,5),(12,5)],[(11,9),(11,15)],
      [(1,11),(1,15),(14,15)],[(25,15),(31,15)],[(14,7),(15,7),(15,10),(18,10),(18,13)]]
pins=set()
for b in bornes: pins|=set(b[1])
for a in axial: pins|={a[2],a[3]}
for b in bncs: pins|={b[3]}|set(b[4])
pins|=set(Q1.values())|{C1['neg'],C1['pos']}
def pts(tr,m): return " ".join(f"{X(i,m)},{Y(j)}" for i,j in tr)

def board(m, view):
    o=[f'<svg viewBox="0 0 {SVGW} {SVGH}" width="100%" style="min-width:880px" role="img" aria-label="{"Placa perforada vista desde el lado de los componentes" if view=="comp" else "Placa perforada vista desde el lado del cobre, espejada"}">']
    o.append(f'<rect class="pcb" x="{ML-0.7*P}" y="{MT-0.7*P}" width="{(W-1+1.4)*P}" height="{(H-1+1.4)*P}" rx="6"/>')
    for i in range(W):
        if i%5==0: o.append(f'<text class="gx" x="{X(i,m)}" y="{MT-0.95*P}" text-anchor="middle">{i}</text>')
    for j in range(H):
        if j%5==0: o.append(f'<text class="gx" x="{ML-0.5*P if not m else X(-0.5,m)}" y="{Y(j)+3}" text-anchor="middle">{j}</text>')
    o.append('<g class="holes">'+"".join(f'<circle cx="{X(i,m)}" cy="{Y(j)}" r="2.3"/>' for i in range(W) for j in range(H))+'</g>')
    cls = "" if view=="cu" else " ghost"
    for tr in thick: o.append(f'<polyline class="trk{cls}" points="{pts(tr,m)}"/>')
    for tr in thin: o.append(f'<polyline class="trn{cls}" points="{pts(tr,m)}"/>')
    if view=="cu":
        o.append('<g class="pads">'+"".join(f'<circle cx="{X(i,m)}" cy="{Y(j)}" r="5"/>' for i,j in pins)+'</g>')
    g='cmpo' if view=="comp" else 'cmpg'
    for name,ps,lab,side,title in bornes:
        (i0,j0),(i1,j1)=ps
        x=X(i0,m); y0=Y(j0)-0.95*P; h=(j1-j0+1.9)*P
        o.append(f'<rect class="{g} bor" x="{x-0.95*P}" y="{y0}" width="{1.9*P}" height="{h}" rx="3"/>')
        for (i,j) in ps:
            o.append(f'<circle class="{g}" cx="{X(i,m)}" cy="{Y(j)}" r="6"/><path class="scr" d="M{X(i,m)-4} {Y(j)}h8"/>')
        sd = side if not m else ("R" if side=="L" else "L")
        ex = x-1.4*P if sd=="L" else x+1.4*P
        anc = "end" if sd=="L" else "start"
        rx = x+1.25*P if sd=="L" else x-1.25*P
        o.append(f'<text class="ref" x="{rx}" y="{Y(j0)+(j1-j0)*P/2+4}" text-anchor="{"start" if sd=="L" else "end"}">{name}</text>')
        if view=="comp":
            o.append(f'<text class="nm" x="{ex}" y="{Y(j0)-14}" text-anchor="{anc}">{title}</text>')
            for k,(i,j) in enumerate(ps):
                o.append(f'<path class="wire" d="M{X(i,m)} {Y(j)}H{ex+(6 if sd=="L" else -6)}"/>') if False else None
                o.append(f'<text class="off" x="{ex}" y="{Y(j)+4}" text-anchor="{anc}">{lab[k]}</text>')
    for ref,lab,a,b,t in axial:
        xa,ya,xb,yb=X(a[0],m),Y(a[1]),X(b[0],m),Y(b[1])
        o.append(f'<path class="lead" d="M{xa} {ya}L{xb} {yb}"/>')
        vert = a[0]==b[0]
        L=(abs(b[0]-a[0])+abs(b[1]-a[1])-1.4)*P; T=t*P*0.8
        cx,cy=(xa+xb)/2,(ya+yb)/2
        if vert: o.append(f'<rect class="{g} res" x="{cx-T/2}" y="{cy-L/2}" width="{T}" height="{L}" rx="4"/>')
        else: o.append(f'<rect class="{g} res" x="{cx-L/2}" y="{cy-T/2}" width="{L}" height="{T}" rx="4"/>')
        if vert:
            tx = cx-T/2-5 if not m else cx+T/2+5
            an = "end" if not m else "start"
            o.append(f'<text class="ref" x="{tx}" y="{cy-2}" text-anchor="{an}">{ref}</text><text class="val" x="{tx}" y="{cy+12}" text-anchor="{an}">{lab}</text>')
        else:
            o.append(f'<text class="ref" x="{cx}" y="{cy-T/2-6}" text-anchor="middle">{ref} · {lab}</text>')
    # C1
    cx,cy=X(C1['c'][0],m),Y(C1['c'][1]); r=C1['r']*P
    o.append(f'<circle class="{g} cap" cx="{cx}" cy="{cy}" r="{r}"/>')
    o.append(f'<path class="stripe" d="M{X(24.4,m)} {cy-r*0.7}V{cy+r*0.7}"/>')
    o.append(f'<text class="ref" x="{cx}" y="{cy-14}" text-anchor="middle">C1</text><text class="val" x="{cx}" y="{cy+30}" text-anchor="middle">680 µF</text>')
    o.append(f'<text class="pol" x="{X(27,m)}" y="{cy-6}" text-anchor="middle">+</text><text class="pol" x="{X(25,m)}" y="{cy-6}" text-anchor="middle">−</text>')
    # Q1
    xl,xr=sorted([X(11.4,m),X(14.6,m)])
    o.append(f'<rect class="{g} tab" x="{xl}" y="{Y(3.0)}" width="{xr-xl}" height="{0.45*P}" rx="2"/>')
    o.append(f'<rect class="{g} q" x="{xl}" y="{Y(3.45)}" width="{xr-xl}" height="{1.2*P}" rx="2"/>')
    for k,l in [("G","G"),("D","D"),("S","S")]:
        i,j=Q1[k]
        o.append(f'<path class="lead" d="M{X(i,m)} {Y(4.65)}V{Y(5)}"/><text class="pin" x="{X(i,m)}" y="{Y(5)+18}" text-anchor="middle">{l}</text>')
    o.append(f'<text class="ref" x="{(xl+xr)/2}" y="{Y(3.45)+0.78*P}" text-anchor="middle">Q1</text>')
    # BNCs (montaje en placa a 90°, sobresalen del borde inferior)
    for nm,lab,cxh,cp,sp,c in bncs:
        bx0,bx1=sorted([X(cxh-3,m),X(cxh+3,m)])
        bc = "bnc" if view=="comp" else "cmpg"
        o.append(f'<rect class="{bc}" x="{bx0}" y="{Y(12.4)}" width="{bx1-bx0}" height="{Y(15.6)-Y(12.4)}" rx="3"/>')
        o.append(f'<rect class="{"bncn" if view=="comp" else "cmpg"}" x="{X(cxh,m)-0.95*P}" y="{Y(15.6)}" width="{1.9*P}" height="{1.6*P}" rx="2"/>')
        o.append(f'<circle class="tp {c}" cx="{X(cp[0],m)}" cy="{Y(cp[1])}" r="6"/>')
        for (i,j) in sp: o.append(f'<rect class="peg" x="{X(i,m)-5}" y="{Y(j)-5}" width="10" height="10" rx="2"/>')
        o.append(f'<text class="tpl {c}" x="{X(cxh,m)}" y="{Y(17.2)+16}" text-anchor="middle">{nm}</text>')
        if view=="comp": o.append(f'<text class="val" x="{X(cxh,m)}" y="{Y(17.2)+30}" text-anchor="middle">{lab}</text>')
    if view=="comp":
        pass
    else:
        o.append(f'<text class="net" x="{X(14,m)}" y="{Y(15)+19}" dx="0" text-anchor="middle">estrella</text>')
    o.append('</svg>')
    return "\n".join(o)

comp=board(False,"comp"); cu=board(True,"cu")

# ---------- schematic
sch=open(SP+'sch.svg').read()
rep=[
 ('<path class="w" d="M130 140H160V90H170M240 90H270M330 90H370"/>','<path class="w" d="M130 140H160V90H169M231 90H262M332 90H370"/>'),
 ('<rect class="cmp" x="170" y="80" width="70" height="20" rx="2"/>\n    <text class="t" x="166" y="66">R_carga 100 Ω 5 W</text>','<rect class="cmp" x="262" y="80" width="70" height="20" rx="2"/>\n    <text class="t" x="262" y="66">R1 · 100 Ω 3 W</text><text class="jt" x="246" y="108" text-anchor="middle">J1</text>'),
 ('<circle class="cmp" cx="272" cy="90" r="3"/><circle class="cmp" cx="328" cy="90" r="3"/>\n    <path class="w" d="M274 89L322 70"/>\n    <text class="ts" x="250" y="118">LLAVE DE CARGA</text><text class="ts" x="250" y="133">se abre antes de disparar</text>',
  '<circle class="cmp" cx="172" cy="90" r="3"/><circle class="cmp" cx="228" cy="90" r="3"/>\n    <path class="w" d="M174 89L222 70"/>\n    <text class="ts" x="150" y="118">LLAVE DE CARGA</text><text class="ts" x="150" y="133">en el cable de la fuente</text>'),
 ('<text class="t" x="398" y="252">C 680 µF</text>','<text class="t" x="398" y="252">C1 680 µF</text>'),
 ('<text class="t2" x="426" y="48">CH2 · punta ×10 · tensión de C</text>','<text class="t2" x="426" y="48">BNC2 → CH2 · tensión de C1</text>'),
 ('<text class="ts" x="474" y="118">LLAVE DE ARMADO</text>','<text class="ts" x="474" y="118">LLAVE DE ARMADO (J3)</text>'),
 ('<text class="tl" x="686" y="160">INICIADOR</text>','<text class="tl" x="686" y="160">INICIADOR</text><text class="jt" x="686" y="208">en J4</text>'),
 ('<text class="tl" x="676" y="290">Q · IRLZ44N</text>','<text class="tl" x="676" y="290">Q1 · IRLZ44N</text>'),
 ('<text class="tl" x="682" y="386">R_shunt</text>','<text class="tl" x="682" y="386">RS shunt</text>'),
 ('<text class="t1" x="772" y="340" >CH1 · punta ×1</text>','<text class="t1" x="694" y="340" >BNC1 → CH1 · corriente</text>'),
 ('<text class="ts" x="560" y="500">masa del osciloscopio en este punto (uno solo)</text>','<text class="ts" x="520" y="500">mallas de BNC1 y BNC2, solo en este punto</text>'),
 ('<text class="ts" x="560" y="372" text-anchor="end">10 kΩ</text>','<text class="ts" x="586" y="372" text-anchor="end">R3 10 kΩ</text>'),
 ('<text class="ts" x="545" y="282">1 kΩ</text>','<text class="ts" x="536" y="282">R2 1 kΩ</text>'),
 ('<text class="ts" x="400" y="400">pila 9 V</text>','<text class="ts" x="400" y="400">pila 9 V (J2)</text>'),
 ('<text class="ts" x="470" y="330">PULSADOR</text>','<text class="ts" x="470" y="330">PULSADOR (J1)</text>'),
]
for a,b in rep:
    assert sch.count(a)==1,a[:60]; sch=sch.replace(a,b)

style=open(SP+'style.css').read()
extra="""
:root{--pcb:#dfe8d6;--hole:#9fae95;--cu:#b06a22;--cuf:color-mix(in srgb,var(--cu) 30%,transparent);--part:#ffffff;--jump:#7a3fb5}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--pcb:#1f2a22;--hole:#4c5d50;--cu:#e0964f;--part:#25302b;--jump:#c79bff}}
:root[data-theme="dark"]{--pcb:#1f2a22;--hole:#4c5d50;--cu:#e0964f;--part:#25302b;--jump:#c79bff}
.pcb{fill:var(--pcb);stroke:var(--line);stroke-width:1.5}
.holes circle{fill:var(--hole)}
.gx{fill:var(--muted);font:10px var(--f-mono)}
.trk{fill:none;stroke:var(--cu);stroke-width:8;stroke-linecap:round;stroke-linejoin:round}
.trn{fill:none;stroke:var(--cu);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}
.ghost{opacity:.28}
.pads circle{fill:var(--cu);stroke:var(--pcb);stroke-width:1.5}
.cmpo{fill:var(--part);stroke:var(--fg);stroke-width:1.6}
.cmpg{fill:none;stroke:var(--muted);stroke-width:1;stroke-dasharray:3 3}
.lead{stroke:var(--muted);stroke-width:2}
.scr{stroke:var(--muted);stroke-width:1.5}
.stripe{stroke:var(--muted);stroke-width:5;opacity:.6}
.ref{fill:var(--fg);font:600 12px var(--f-mono)}
.val{fill:var(--muted);font:11px var(--f-mono)}
.pin{fill:var(--muted);font:600 10px var(--f-mono)}
.pol{fill:var(--fg);font:700 14px var(--f-mono)}
.nm{fill:var(--accent);font:600 11.5px var(--f-mono);letter-spacing:.04em}
.off{fill:var(--muted);font:11px var(--f-body)}
.wire{stroke:var(--muted);stroke-width:1.5;stroke-dasharray:2 3}
.tp{fill:none;stroke-width:3}
.tp.ch1{stroke:var(--ch1)} .tp.ch2{stroke:var(--ch2)} .tp.gnd{stroke:var(--fg)}
.tpl{font:600 11.5px var(--f-mono)} .tpl.ch1{fill:var(--ch1)} .tpl.ch2{fill:var(--ch2)} .tpl.gnd{fill:var(--fg)}
.jump{fill:none;stroke:var(--jump);stroke-width:2.4;stroke-dasharray:7 4}
.jl{fill:var(--jump);font:11px var(--f-body)}
.coax{fill:none;stroke-width:2.6} .coax.ch1{stroke:var(--ch1)} .coax.ch2{stroke:var(--ch2)}
.shd{fill:none;stroke:var(--fg);stroke-width:1.6;stroke-dasharray:4 3}
.bnc{fill:var(--part);stroke:var(--fg);stroke-width:1.6}.bncn{fill:var(--bg);stroke:var(--fg);stroke-width:1.6}
.peg{fill:none;stroke:var(--fg);stroke-width:1.5}
.bnco{fill:var(--part);stroke:var(--fg);stroke-width:2} .bnci{fill:var(--bg);stroke:var(--muted);stroke-width:1.5}
.net{fill:var(--cu);font:600 11px var(--f-mono)}
.jt{fill:var(--accent);font:600 11px var(--f-mono)}
.tabs{display:flex;gap:6px;flex-wrap:wrap}
.tabs button[aria-pressed="false"]{background:transparent;color:var(--accent)}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{display:inline-block;width:22px;height:0;border-top:7px solid var(--cu);border-radius:3px}
.sw.thin{border-top-width:3px}
.sw.j{border-top:2px dashed var(--jump)}
ul.list{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px;max-width:72ch}
"""
style=style.replace("</style>",extra+"</style>")

body=f"""<title>Placa del banco de I²t</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Sans+Condensed:wght@600;700&display=swap">
{style}
<main>
<header class="hdr">
  <div class="eyebrow">Banco de I²t · circuito de descarga</div>
  <h1>Placa del banco de I²t</h1>
  <p class="lead">Circuito y armado en placa perforada de paso 2,54 mm (33 × 16 agujeros, unos 85 × 41 mm). Todo va soldado en la placa, sin cables sueltos: las conexiones son pistas de un solo lado, sin cruces, y los dos BNC del osciloscopio están soldados en el borde. Lo externo (fuente, llaves, pulsador, pila, iniciador) entra por cuatro borneras.</p>
  <div class="meta"><span>Q1 IRLZ44N</span><span>C1 680 µF 25 V</span><span>RS 0,1 Ω</span><span>4 borneras · 2 BNC en placa</span></div>
</header>

<section>
  <h2><span class="n">1</span>Circuito</h2>
  <div class="fig">{sch}</div>
  <p class="cap">Mismas referencias que en la placa. La llave de carga va en el cable + de la fuente, antes de J1. El puente de seguridad se monta en la caja, sobre los bornes del iniciador, para que también proteja el cable.</p>
</section>

<section>
  <h2><span class="n">2</span>Ubicación en la placa</h2>
  <div class="tabs" role="group" aria-label="Vista de la placa">
    <button type="button" id="v-comp" aria-pressed="true">Lado de los componentes</button>
    <button type="button" id="v-cu" aria-pressed="false">Lado del cobre (espejado)</button>
  </div>
  <div class="fig" id="f-comp">{comp}</div>
  <div class="fig" id="f-cu" hidden>{cu}</div>
  <div class="legend"><span><i class="sw"></i>Lazo de descarga: alambre de cobre estañado de 1 mm soldado en cada agujero</span><span><i class="sw thin"></i>Señal y masa: alambre estañado fino (0,5 mm) o pata de resistor sobrante</span></div>
  <p class="cap">En la vista del cobre la placa está dada vuelta: lo que en los componentes está a la derecha, en el cobre queda a la izquierda. Los números sirven para ubicar cada agujero como (columna, fila); en esa vista las columnas aparecen en orden inverso.</p>
</section>

<section>
  <h2><span class="n">3</span>Por qué está ubicado así</h2>
  <ul class="list">
    <li><b>Sin cruces ni cables.</b> Todas las pistas van del lado del cobre y ninguna se cruza. Donde una señal tiene que pasar al otro lado de una pista, la cruza un componente por arriba: R1 pasa sobre la pista del drain y lleva la carga hasta C1 sin puentes.</li>
    <li><b>Lazo de descarga corto y grueso.</b> C1+ → J3 → llave → J3 → J4 → iniciador → J4 → drain de Q1 → RS → estrella → bus de masa → C1−. Unos 12 cm de alambre de 1 mm suman ~3 mΩ, nada frente a los 2 Ω del puente. Con un pulso de 1,5 ms, el tamaño del lazo no cambia la medición.</li>
    <li><b>Masa en estrella.</b> La pata inferior de RS es la estrella. El bus de abajo junta C1−, las mallas de los BNC, R3 y las masas de J2. Las corrientes chicas (gate, pila) no pasan por el tramo entre RS y BNC1.</li>
    <li><b>Medición Kelvin del shunt.</b> El centro de BNC1 sale por su propia pista desde la pata superior de RS, y su malla está a dos agujeros de la estrella. CH1 lee la caída en RS y casi nada de las pistas (menos del 0,2 %).</li>
    <li><b>BNC2 lee C1 directo.</b> Su centro va al + de C1 y su malla al bus, al lado de C1−.</li>
    <li><b>Gate protegido.</b> R2 y R3 están junto a Q1, y R3 lleva el gate a masa: si la pila o el pulsador quedan desconectados, Q1 queda apagado.</li>
    <li><b>Borneras por función.</b> A la izquierda, lo que viene del operador (fuente, pulsador, pila). A la derecha, el iniciador y la llave de armado. Abajo, el osciloscopio.</li>
  </ul>
</section>

<section>
  <h2><span class="n">4</span>Materiales de la placa</h2>
  <div class="tw"><table style="min-width:640px"><thead><tr><th>Ref.</th><th>Componente</th><th>Agujeros (col, fila)</th><th>Nota</th></tr></thead><tbody>
    <tr><td>Q1</td><td>MOSFET IRLZ44N (o IRL540N, IRLB8721)</td><td class="n">G 12,5 · D 13,5 · S 14,5</td><td>Parado, aleta hacia atrás. Sin disipador: el pulso dura milisegundos.</td></tr>
    <tr><td>C1</td><td>Electrolítico 680 µF 25 V 105 °C, radial 10 mm</td><td class="n">− 25,9 · + 27,9</td><td>Franja (−) hacia la izquierda.</td></tr>
    <tr><td>RS</td><td>0,1 Ω 1 %, 2 W, axial</td><td class="n">14,7 · 14,12</td><td>Paso de 12,7 mm. Si es de 5 W cerámico no entra: pedí uno de 2 W de película metálica o bobinado chico.</td></tr>
    <tr><td>R1</td><td>100 Ω 3 W, óxido metálico</td><td class="n">24,0 · 24,6</td><td>Acostado. Pasa por arriba de la pista del drain. Con la fuente limitada a 0,2 A disipa como mucho 2 W.</td></tr>
    <tr><td>R2</td><td>1 kΩ ¼ W</td><td class="n">4,3 · 9,3</td><td></td></tr>
    <tr><td>R3</td><td>10 kΩ ¼ W</td><td class="n">11,5 · 11,9</td><td></td></tr>
    <tr><td>BNC1, BNC2</td><td>BNC hembra para placa, a 90°</td><td class="n">centro 18,13 · 29,13</td><td>Las patas de malla y sujeción van al bus de masa (fila 15). Si son gruesas, agrandá esos agujeros con mecha de 1,5–2 mm.</td></tr>
    <tr><td>J1–J4</td><td>Bornera de 2 polos, paso 5 mm</td><td class="n">ver dibujo</td><td>Tornillos hacia afuera de la placa.</td></tr>
    <tr><td>—</td><td>Alambre de cobre estañado de 1 mm y de 0,5 mm</td><td class="n">—</td><td>Para las pistas gruesas y finas.</td></tr>
  </tbody></table></div>
  <p class="note">Fuera de la placa: fuente con la llave de carga en su cable +, llave de armado, pulsador, pila de 9 V, caja con el iniciador y su puente de seguridad, y el resistor de 2,2 Ω 5 W que va en J4 en lugar del iniciador para validar.</p>
</section>

<section>
  <h2><span class="n">5</span>Qué pedir en Electrónica Mendoza</h2>
  <div class="tw"><table style="min-width:640px"><thead><tr><th>Cant.</th><th>Componente</th><th>Si no lo tienen</th></tr></thead><tbody>
    <tr><td class="n">2</td><td>BNC hembra para placa a 90° (montaje en PCB)</td><td>BNC hembra de chasis soldado directo en el borde: el pin central en el agujero del centro y la arandela de masa doblada y soldada al bus, sin cable.</td></tr>
    <tr><td class="n">2</td><td>Cable BNC macho–BNC macho RG58, 50 cm a 1 m</td><td>—</td></tr>
    <tr><td class="n">2</td><td>Resistor 0,1 Ω 1 % 2 W axial</td><td>0,1 Ω 5 % 2 W (se calibra igual)</td></tr>
    <tr><td class="n">1</td><td>Resistor 100 Ω 3 W óxido metálico</td><td>100 Ω 2 W</td></tr>
    <tr><td class="n">1 m</td><td>Alambre de cobre estañado de 1 mm (o hilo de 1 mm² pelado)</td><td>—</td></tr>
    <tr><td class="n">1 m</td><td>Alambre de cobre estañado de 0,5 mm</td><td>Patas de resistores sobrantes</td></tr>
    <tr><td class="n">4</td><td>Bornera de 2 polos, paso 5 mm</td><td>—</td></tr>
    <tr><td class="n">1</td><td>Placa perforada de 10 × 5 cm, paso 2,54 mm, islas individuales</td><td>Cortar una más grande</td></tr>
  </tbody></table></div>
  <p class="note">Lo demás (IRLZ44N, 680 µF, 1 kΩ, 10 kΩ, pulsador, interruptores, llave, broche de 9 V) es igual que en la lista anterior. En el osciloscopio: CH1 y CH2 con atenuación ×1 y acoplamiento DC. CH1 a 100–200 mV/div; CH2 a 2–5 V/div.</p>
</section>

<section>
  <h2><span class="n">6</span>Orden de armado</h2>
  <ol class="steps">
    <li><div><h3>Componentes bajos primero</h3><p>R2, R3, RS y R1 (R1 acostado, sobre la placa). Doblá cada pata hacia el lado de su pista y soldala sin cortar: la misma pata sirve de pista hasta el agujero siguiente.</p></div></li>
    <li><div><h3>Pistas gruesas</h3><p>Del lado del cobre, el alambre de 1 mm siguiendo el lazo: J3 → C1+, J3 ↔ J4, J4 → drain, source → RS, RS → bus de masa → C1−. Soldalo en cada agujero por donde pasa.</p></div></li>
    <li><div><h3>Borneras, C1, Q1 y BNC</h3><p>Al final los componentes altos. Los BNC con el frente sobresaliendo del borde de la placa.</p></div></li>
    <li><div><h3>Pistas finas</h3><p>Fuente → R1, R1 → C1+ y centro de BNC2, gate, R3 a masa, la pista Kelvin desde RS hasta el centro de BNC1, y las masas de J2.</p></div></li>
  </ol>
</section>

<section>
  <h2><span class="n">7</span>Verificación antes de conectar nada</h2>
  <ul class="list">
    <li>Con el tester en continuidad: no hay continuidad entre el centro y la malla de BNC2 (C1+ y masa), ni entre drain y source de Q1.</li>
    <li>Entre el centro y la malla de BNC1 mide casi 0 Ω (el shunt).</li>
    <li>Entre el gate y la masa mide ~10 kΩ (R3). Entre J1 (+ fuente) y el centro de BNC2 mide ~100 Ω (R1).</li>
    <li>Revisá con lupa que no haya puentes de estaño entre pistas vecinas, sobre todo alrededor de Q1 y de los BNC.</li>
    <li>Primera prueba con el resistor de 2,2 Ω en J4 y C1 cargado a 3–5 V: el I²t medido tiene que coincidir con V₀²·C/(2·R).</li>
  </ul>
</section>
</main>
<script>
(function(){{const b1=document.getElementById("v-comp"),b2=document.getElementById("v-cu"),f1=document.getElementById("f-comp"),f2=document.getElementById("f-cu");
function set(cu){{f1.hidden=cu;f2.hidden=!cu;b1.setAttribute("aria-pressed",String(!cu));b2.setAttribute("aria-pressed",String(cu));}}
b1.addEventListener("click",()=>set(false));b2.addEventListener("click",()=>set(true));}})();
</script>
"""
open('/home/user/prueba/retardo/placa-banco-i2t.html','w').write(body)
print("ok")
