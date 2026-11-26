import re, html
SP='/tmp/claude-0/-home-user-prueba/72c9e2c6-9447-55de-846e-f400757c54e2/scratchpad/'
W,H=32,15; P=22; ML=200; MT=46; OFF=7
def X(i,m=False): return ML+((W-1-i) if m else i)*P
def Y(j): return MT+(j-OFF)*P
SVGW=ML*2+(W-1)*P; SVGH=MT*2+(H-1)*P+120

# ---------- data
bornes=[ # name, pins, pinlabels(offboard), side
 ("J1 FUENTE",[(1,17),(1,19)],["+ fuente (por la llave de carga)","− fuente"],"L"),
 ("J5 DISPARO",[(1,11),(1,13)],["pulsador (otro lado al + de la pila)","− pila 9 V"],"L"),
 ("J3 ARMADO",[(30,15),(30,17)],["retorno de la llave","a la llave"],"R"),
 ("J4 INICIADOR",[(30,9),(30,11)],["retorno del iniciador","al iniciador"],"R"),
]
axial=[ # ref,label,a,b,thick
 ("R1","100 Ω 5 W",(4,15),(14,15),1.3),
 ("R2","1 kΩ",(14,11),(19,11),0.8),
 ("R3","10 kΩ",(20,12),(20,17),0.8),
 ("RS","0,1 Ω",(23,13),(23,18),1.1),
]
tps=[("TP1","BNC1 centro",(24,13),"ch1"),("TP2","BNC2 centro",(28,20),"ch2"),("TP3","BNC1 malla",(24,19),"gnd"),("TP4","BNC2 malla",(29,21),"gnd")]
thick=[[(27,17),(30,17)],[(30,15),(30,11)],[(30,9),(22,9),(22,11)],[(23,11),(23,13)],[(23,18),(25,18),(25,17)]]
thin=[[(23,13),(24,13)],[(27,17),(27,20),(28,20)],[(24,18),(24,19)],
      [(1,19),(1,20),(22,20),(22,18),(23,18)],[(24,19),(24,21),(29,21)],[(20,17),(20,18),(22,18)],
      [(20,12),(20,11),(21,11)],[(19,11),(20,11)],[(1,11),(14,11)],[(1,13),(5,13),(5,20)],
      [(1,17),(4,17),(4,15)],[(14,15),(14,16)]]
jumper=((14,16),(27,20))
pins=set()
for _,ps,_,_ in bornes: pins|=set(ps)
for a in axial: pins|={a[2],a[3]}
for t in tps: pins.add(t[2])
pins|={(21,11),(22,11),(23,11),(25,17),(27,17),(14,16),(27,20)}
for tr in thick+thin:
    pins|={tr[0],tr[-1]}

def pts(tr,m): return " ".join(f"{X(i,m)},{Y(j)}" for i,j in tr)

def board(m, view):
    o=[f'<svg viewBox="0 0 {SVGW} {SVGH}" width="100%" style="min-width:860px" role="img" aria-label="{"Placa perforada vista desde el lado de los componentes" if view=="comp" else "Placa perforada vista desde el lado del cobre, espejada"}">']
    o.append(f'<rect class="pcb" x="{ML-0.7*P}" y="{MT-0.7*P}" width="{(W-1+1.4)*P}" height="{(H-1+1.4)*P}" rx="6"/>')
    # holes
    for i in range(W):
        o.append(f'<text class="gx" x="{X(i,m)}" y="{MT-0.95*P}" text-anchor="middle">{i if i%5==0 else ""}</text>')
    for j in range(H):
        o.append(f'<text class="gx" x="{ML-0.5*P}" y="{Y(j+OFF)+3}" text-anchor="middle">{j if j%5==0 else ""}</text>')
    o.append('<g class="holes">'+"".join(f'<circle cx="{X(i,m)}" cy="{Y(j+OFF)}" r="2.3"/>' for i in range(W) for j in range(H))+'</g>')
    if view=="cu":
        for tr in thick: o.append(f'<polyline class="trk" points="{pts(tr,m)}"/>')
        for tr in thin: o.append(f'<polyline class="trn" points="{pts(tr,m)}"/>')
        o.append('<g class="pads">'+"".join(f'<circle cx="{X(i,m)}" cy="{Y(j)}" r="5"/>' for i,j in pins)+'</g>')
    else:
        for tr in thick: o.append(f'<polyline class="trk ghost" points="{pts(tr,m)}"/>')
        for tr in thin: o.append(f'<polyline class="trn ghost" points="{pts(tr,m)}"/>')
    # components (outline in cu view)
    g='cmpo' if view=="comp" else 'cmpg'
    # bornes
    for name,ps,lab,side in bornes:
        (i0,j0),(i1,j1)=ps
        x=X(i0,m); y0=Y(j0)-0.95*P; h=(j1-j0+1.9)*P
        o.append(f'<rect class="{g} bor" x="{x-0.95*P}" y="{y0}" width="{1.9*P}" height="{h}" rx="3"/>')
        for k,(i,j) in enumerate(ps):
            o.append(f'<circle class="{g}" cx="{X(i,m)}" cy="{Y(j)}" r="6"/><path class="scr" d="M{X(i,m)-4} {Y(j)}h8"/>')
        sd = side if not m else ("R" if side=="L" else "L")
        ex = x-1.4*P if sd=="L" else x+1.4*P
        anc = "end" if sd=="L" else "start"
        o.append(f'<text class="ref" x="{x}" y="{y0-5}" text-anchor="middle">{name.split()[0]}</text>')
        if view=="comp":
            o.append(f'<text class="nm" x="{ex}" y="{Y(ps[0][1])-12}" text-anchor="{anc}">{name.split(" ",1)[1]}</text>')
            for k,(i,j) in enumerate(ps):
                o.append(f'<path class="wire" d="M{X(i,m)} {Y(j)}H{ex+(6 if sd=="L" else -6)}"/>')
                o.append(f'<text class="off" x="{ex}" y="{Y(j)+16}" text-anchor="{anc}">{lab[k]}</text>')
    for ref,lab,a,b,t in axial:
        xa,ya,xb,yb=X(a[0],m),Y(a[1]),X(b[0],m),Y(b[1])
        o.append(f'<path class="lead" d="M{xa} {ya}L{xb} {yb}"/>')
        vert = a[0]==b[0]
        L=(abs(b[0]-a[0])+abs(b[1]-a[1])-1.6)*P; T=t*P*0.75
        cx,cy=(xa+xb)/2,(ya+yb)/2
        if vert: o.append(f'<rect class="{g} res" x="{cx-T/2}" y="{cy-L/2}" width="{T}" height="{L}" rx="4"/>')
        else: o.append(f'<rect class="{g} res" x="{cx-L/2}" y="{cy-T/2}" width="{L}" height="{T}" rx="4"/>')
        if vert:
            tx = cx-T/2-5 if not m else cx+T/2+5
            an = "end" if not m else "start"
            o.append(f'<text class="ref" x="{tx}" y="{cy-2}" text-anchor="{an}">{ref}</text><text class="val" x="{tx}" y="{cy+12}" text-anchor="{an}">{lab}</text>')
        else:
            o.append(f'<text class="ref" x="{cx}" y="{cy+4}" text-anchor="middle">{ref} · {lab}</text>' if view=="comp" else f'<text class="ref" x="{cx}" y="{cy-T/2-5}" text-anchor="middle">{ref}</text>')
    # C1
    cx,cy=X(26,m),Y(17); r=2.15*P
    o.append(f'<circle class="{g} cap" cx="{cx}" cy="{cy}" r="{r}"/>')
    sx = X(24.6 if not m else 24.6, m)
    o.append(f'<path class="stripe" d="M{X(24.45,m)} {cy-r*0.72}V{cy+r*0.72}" />')
    o.append(f'<text class="ref" x="{cx}" y="{cy-12}" text-anchor="middle">C1</text><text class="val" x="{cx}" y="{cy+30}" text-anchor="middle">680 µF</text>')
    o.append(f'<text class="pol" x="{X(27,m)}" y="{cy-8}" text-anchor="middle">+</text><text class="pol" x="{X(25,m)}" y="{cy-8}" text-anchor="middle">−</text>')
    # Q1
    x0,x1=X(20.4,m),X(23.6,m); xl,xr=min(x0,x1),max(x0,x1)
    o.append(f'<rect class="{g} tab" x="{xl}" y="{Y(8.95)}" width="{xr-xl}" height="{0.5*P}" rx="2"/>')
    o.append(f'<rect class="{g} q" x="{xl}" y="{Y(9.45)}" width="{xr-xl}" height="{1.2*P}" rx="2"/>')
    for i,l in [(21,"G"),(22,"D"),(23,"S")]:
        o.append(f'<path class="lead" d="M{X(i,m)} {Y(10.65)}V{Y(11)}"/><text class="pin" x="{X(i,m)}" y="{Y(11)+18}" text-anchor="middle">{l}</text>')
    o.append(f'<text class="ref" x="{(xl+xr)/2}" y="{Y(9.45)+0.75*P}" text-anchor="middle">Q1</text>')
    # TPs
    for ref,lab,(i,j),c in tps:
        o.append(f'<circle class="tp {c}" cx="{X(i,m)}" cy="{Y(j)}" r="7"/>')
    if view=="comp":
        o.append(f'<path class="jump" d="M{X(14,m)} {Y(16)}C{X(14,m)} {Y(21.2)} {X(27,m)} {Y(21.4)} {X(27,m)} {Y(20)}"/>')
        o.append(f'<text class="jl" x="{X(9,m)}" y="{Y(21.7)+16}" text-anchor="middle">cable fino aislado (camino de carga)</text>')
        for nm,ch,bx,sig,shd,c in [("BNC1","CH1",23.2,(24,13),(24,19),"ch1"),("BNC2","CH2",29.3,(28,20),(29,21),"ch2")]:
            cx,cy=X(bx,m),Y(21.7)+62
            o.append(f'<path class="coax {c}" d="M{X(sig[0],m)} {Y(sig[1])}L{X(sig[0],m)} {Y(sig[1])+6}L{cx-3} {cy-16}"/>')
            o.append(f'<path class="shd" d="M{X(shd[0],m)} {Y(shd[1])}L{cx+5} {cy-16}"/>')
            o.append(f'<circle class="bnco" cx="{cx}" cy="{cy}" r="16"/><circle class="bnci" cx="{cx}" cy="{cy}" r="9"/><circle class="tp {c}" cx="{cx}" cy="{cy}" r="3"/>')
            o.append(f'<text class="tpl {c}" x="{cx+24}" y="{cy+4}">{nm} → {ch}</text>')
        offs={"TP1":(12,4,"start"),"TP2":(12,4,"start"),"TP3":(-12,4,"end"),"TP4":(12,4,"start")}
        for ref,lab,(i,j),c in tps:
            dx,dy,an=offs[ref]
            o.append(f'<text class="tpl {c}" x="{X(i,m)+dx}" y="{Y(j)+dy}" text-anchor="{an}">{ref}</text>')
        o.append(f'<text class="nm" x="{X(21,m)}" y="{Y(8.95)-6}" text-anchor="middle">aleta metálica atrás · cara impresa hacia abajo</text>')
    else:
        lab={ "A":(X(28.5,m),Y(16.6)), }
        for txt,(i,j) in [("ESTRELLA",(23,18.9)),("G",(20.6,10.6))]:
            pass
        o.append(f'<text class="net" x="{X(23,m)}" y="{Y(21.7)+18}" text-anchor="middle">estrella de masa: debajo de RS (C1−, TP3)</text>')
    o.append('</svg>')
    return "\n".join(o)

comp=board(False,"comp"); cu=board(True,"cu")

# ---------- schematic
sch=open(SP+'sch.svg').read()
rep=[
 ('<path class="w" d="M130 140H160V90H170M240 90H270M330 90H370"/>','<path class="w" d="M130 140H160V90H169M231 90H262M332 90H370"/>'),
 ('<rect class="cmp" x="170" y="80" width="70" height="20" rx="2"/>\n    <text class="t" x="166" y="66">R_carga 100 Ω 5 W</text>','<rect class="cmp" x="262" y="80" width="70" height="20" rx="2"/>\n    <text class="t" x="262" y="66">R1 · 100 Ω 5 W</text><text class="jt" x="240" y="82" text-anchor="middle">J1+</text>'),
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
 ('<text class="ts" x="470" y="330">PULSADOR</text>','<text class="ts" x="470" y="330">PULSADOR (J5)</text>'),
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
  <p class="lead">Circuito y armado en placa perforada de paso 2,54 mm (32 × 15 agujeros, unos 80 × 38 mm). Lo único que va en la placa es el lazo de descarga y el manejo del gate. La fuente, el osciloscopio, las llaves, el pulsador, la pila y el iniciador se conectan por borneras.</p>
  <div class="meta"><span>Q1 IRLZ44N</span><span>C1 680 µF 25 V</span><span>RS 0,1 Ω</span><span>4 borneras · 2 BNC al osciloscopio</span></div>
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
  <div class="legend"><span><i class="sw"></i>Lazo de descarga: alambre de cobre estañado de 1 mm o hilo de 1 mm² soldado sobre los agujeros</span><span><i class="sw thin"></i>Señal y masa: alambre fino o puentes de estaño</span><span><i class="sw j"></i>Cable fino aislado, del lado de los componentes</span></div>
  <p class="cap">La vista del cobre está dada vuelta como la ves al girar la placa: lo que en los componentes está a la derecha, en el cobre queda a la izquierda. Los números de fila y columna sirven para ubicar cada agujero (columna, fila); en esa vista las columnas aparecen en orden inverso.</p>
</section>

<section>
  <h2><span class="n">3</span>Por qué está ubicado así</h2>
  <ul class="list">
    <li><b>Lazo de descarga chico.</b> C1, Q1, RS y las borneras J3 y J4 están juntos en el borde derecho. La corriente de 2–8 A recorre unos 4 cm de placa: menos resistencia y menos inductancia, así el pulso se parece al del diseño.</li>
    <li><b>Masa en estrella debajo de RS.</b> El − de C1, la masa de la fuente, la de la pila, R3 y las dos masas del osciloscopio llegan a un mismo punto. La corriente del disparo no pasa por la masa de las puntas.</li>
    <li><b>Medición Kelvin del shunt.</b> El centro de BNC1 sale de la pata superior de RS (TP1) y su malla de al lado de la pata inferior (TP3). CH1 lee solo la caída en RS, sin la de las pistas.</li>
    <li><b>Mallas de los BNC solo en la estrella.</b> La malla de BNC2 vuelve por TP4 al mismo punto. Si la caja es metálica, los BNC tienen que ir aislados del chasis: si no, la tierra del osciloscopio encuentra otro camino y la medición de CH1 se ensucia.</li>
    <li><b>Gate corto.</b> R2 y R3 están pegados a Q1, y R3 va a la estrella. Si la pila o el pulsador quedan desconectados, R3 mantiene a Q1 apagado.</li>
    <li><b>Carga separada.</b> El camino de carga (R1, unos mA) va por un cable fino. Así no comparte pistas con el lazo de descarga ni lo cruza.</li>
    <li><b>Cables fuera de la placa:</b> los pares a la llave de armado (J3) y al iniciador (J4) van trenzados y lo más cortos posible, con cable de 1 mm². Son parte del lazo de descarga.</li>
  </ul>
</section>

<section>
  <h2><span class="n">4</span>Materiales de la placa</h2>
  <div class="tw"><table style="min-width:640px"><thead><tr><th>Ref.</th><th>Componente</th><th>Agujeros (col, fila)</th><th>Nota</th></tr></thead><tbody>
    <tr><td>Q1</td><td>MOSFET IRLZ44N (o IRL540N, IRLB8721)</td><td class="n">G 21,4 · D 22,4 · S 23,4</td><td>Parado, aleta hacia atrás. Sin disipador: el pulso dura milisegundos.</td></tr>
    <tr><td>C1</td><td>Electrolítico 680 µF 25 V 105 °C, radial 10 mm</td><td class="n">− 25,10 · + 27,10</td><td>La franja (−) hacia la izquierda.</td></tr>
    <tr><td>RS</td><td>0,1 Ω 1 %, 2–5 W</td><td class="n">23,6 · 23,11</td><td>Si es más largo, montalo parado. Si es SMD 2512, soldalo entre dos islas del lado del cobre.</td></tr>
    <tr><td>R1</td><td>100 Ω 5 W</td><td class="n">4,8 · 14,8</td><td>Separado unos mm de la placa: calienta poco, pero es grande.</td></tr>
    <tr><td>R2</td><td>1 kΩ ¼ W</td><td class="n">14,4 · 19,4</td><td></td></tr>
    <tr><td>R3</td><td>10 kΩ ¼ W</td><td class="n">20,5 · 20,10</td><td></td></tr>
    <tr><td>J1, J3, J4, J5</td><td>Bornera de 2 polos, paso 5 mm</td><td class="n">ver dibujo</td><td>Tornillos hacia afuera de la placa.</td></tr>
    <tr><td>TP1–TP4</td><td>Pads de soldadura para los coaxiales</td><td class="n">24,6 · 28,13 · 24,12 · 29,14</td><td>TP1 y TP3: centro y malla de BNC1. TP2 y TP4: centro y malla de BNC2.</td></tr>
    <tr><td>BNC1, BNC2</td><td>BNC hembra de chasis, con tuerca y terminal para soldar</td><td class="n">en la caja</td><td>Unidos a la placa con 10–15 cm de coaxial fino (RG174) o par trenzado.</td></tr>
    <tr><td>—</td><td>Alambre de cobre estañado de 1 mm o hilo de 1 mm²</td><td class="n">—</td><td>Para las pistas gruesas.</td></tr>
  </tbody></table></div>
  <p class="note">Fuera de la placa: fuente, llave de carga, llave de armado, pulsador, pila de 9 V, caja con el iniciador y el puente de seguridad, y el resistor de 2,2 Ω 5 W que va en J4 en lugar del iniciador para validar.</p>
</section>

<section>
  <h2><span class="n">5</span>Conexión al osciloscopio con BNC</h2>
  <p>Con dos BNC en la caja ya no hacen falta las puntas: se conecta con dos cables BNC–BNC y el osciloscopio queda listo en cada disparo, siempre igual.</p>
  <div class="tw"><table style="min-width:640px"><thead><tr><th>Cant.</th><th>Qué pedir en Electrónica Mendoza</th><th>Nota</th></tr></thead><tbody>
    <tr><td class="n">2</td><td>Conector BNC hembra de chasis (panel), con tuerca y terminal para soldar</td><td>Si la caja es de metal, pedilos aislados o usá caja plástica.</td></tr>
    <tr><td class="n">2</td><td>Cable BNC macho–BNC macho, RG58, 50 cm a 1 m</td><td>Uno por canal.</td></tr>
    <tr><td class="n">0,5 m</td><td>Cable coaxial fino RG174 (o RG58)</td><td>De cada BNC a la placa, 10–15 cm. Alternativa: par trenzado.</td></tr>
    <tr><td class="n">1</td><td>Caja plástica para la placa y los BNC (unos 120 × 80 × 50 mm)</td><td>Opcional, pero hace más prolijo y seguro el banco.</td></tr>
  </tbody></table></div>
  <ul class="list">
    <li><b>Si solo tienen BNC hembra para placa a 90°</b>, también sirve: va en el borde de abajo, en lugar de TP1–TP4, y hay que agrandar con mecha de 2 mm los agujeros de las patas de sujeción.</li>
    <li><b>En el osciloscopio:</b> CH1 y CH2 con atenuación ×1 (ya no hay punta ×10), acoplamiento DC. CH1 a 100–200 mV/div; CH2 a 2–5 V/div. La entrada del osciloscopio aguanta los 15 V del capacitor sin divisor.</li>
    <li>El cable coaxial suma unos 100 pF por metro. Con un pulso de milisegundos no afecta la medición.</li>
  </ul>
</section>

<section>
  <h2><span class="n">6</span>Orden de armado</h2>
  <ol class="steps">
    <li><div><h3>Pistas gruesas primero</h3><p>Del lado del cobre, soldá el alambre de 1 mm siguiendo el lazo de descarga, punto por punto en cada agujero: C1+ → J3, J3 → J4, J4 → D, S → RS, RS → estrella → C1−.</p></div></li>
    <li><div><h3>Componentes de abajo hacia arriba</h3><p>R2, R3, RS, R1, después las borneras, C1 y por último Q1. Soldá cada pata a su pista y cortá lo que sobre.</p></div></li>
    <li><div><h3>Pistas finas y puntos de prueba</h3><p>Masa de J1 y J5 hasta la estrella, gate, pads TP1–TP4 con sus coaxiales a los BNC, y el cable fino de carga del lado de los componentes, desde la pata de R1 (agujero 14,9) hasta el nodo de TP2 (27,13).</p></div></li>
  </ol>
</section>

<section>
  <h2><span class="n">7</span>Verificación antes de conectar nada</h2>
  <ul class="list">
    <li>Con el tester en continuidad: no hay continuidad entre C1+ (TP2) y la estrella (TP3), ni entre D y S de Q1.</li>
    <li>Entre el gate (pata G) y la estrella mide ~10 kΩ (R3).</li>
    <li>Entre J1+ y TP2 mide ~100 Ω (R1).</li>
    <li>Entre el centro y la malla de BNC1 mide casi 0 Ω (el shunt). Entre el centro y la malla de BNC2 no hay continuidad (C1 descargado mide como circuito abierto o sube lento).</li>
    <li>Revisá con lupa que no haya puentes de estaño entre pistas vecinas, sobre todo alrededor de Q1.</li>
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
