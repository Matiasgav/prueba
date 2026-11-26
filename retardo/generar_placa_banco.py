import re, html
SP='/tmp/claude-0/-home-user-prueba/72c9e2c6-9447-55de-846e-f400757c54e2/scratchpad/'
W,H=36,18; P=22; ML=210; MT=40
def X(i,m=False): return ML+((W-1-i) if m else i)*P
def Y(j): return MT+j*P
SVGW=ML*2+(W-1)*P; SVGH=MT+(H-1)*P+130

bornes=[
 ("J1",[(1,6),(1,8)],["pulsador (el otro lado al + de la pila)","− pila 9 V"],"L","PULSADOR Y PILA"),
 ("J4",[(34,3),(34,5)],["retorno del iniciador","al iniciador"],"R","INICIADOR"),
 ("J3",[(34,7),(34,9)],["retorno de la llave","a la llave de armado"],"R","ARMADO"),
]
bananas=[("B+","rojo · + fuente",(2,2),(5,2),"red"),("B−","negro · − fuente",(2,14),(5,14),"blk")]
axial=[ # ref,label,a,b,diam(holes)
 ("R1","100 Ω 3 W",(26,0),(26,9),2.4),
 ("R2","1 kΩ",(4,6),(9,6),1.0),
 ("R3","10 kΩ",(13,5),(13,9),1.0),
 ("RS","0,1 Ω 2 W",(16,7),(16,14),1.8),
]
bncs=[("BNC1","CH1 · corriente",20,(20,15),[(18,17),(22,17)],"ch1"),("BNC2","CH2 · tensión de C1",26,(26,15),[(24,17),(28,17)],"ch2")]
C1=dict(c=(30,12),neg=(31,12),pos=(29,12),r=2.15)
Q1=dict(G=(14,5),D=(15,5),S=(16,5))
thick=[[(29,12),(29,9),(34,9)],[(34,5),(34,7)],[(15,5),(15,3),(34,3)],[(16,5),(16,7)],[(16,14),(16,17)],[(16,17),(31,17)],[(31,12),(31,17)]]
thin=[[(5,2),(5,0),(26,0)],[(26,9),(29,9)],[(26,15),(26,11),(29,11)],[(1,6),(4,6)],[(9,6),(9,5),(14,5)],
      [(13,9),(13,17)],[(1,8),(1,10),(5,10),(5,14),(5,17),(16,17)],[(16,7),(17,7),(17,12),(20,12),(20,15)]]
pins=set()
for b in bornes: pins|=set(b[1])
for b in bananas: pins.add(b[3])
for a in axial: pins|={a[2],a[3]}
for b in bncs: pins|={b[3]}|set(b[4])
pins|=set(Q1.values())|{C1['neg'],C1['pos']}

# ---- verificación del conexionado (union-find sobre agujeros)
def cells(tr):
    out=[]
    for (x0,y0),(x1,y1) in zip(tr,tr[1:]):
        assert x0==x1 or y0==y1, tr
        if x0==x1:
            st=1 if y1>y0 else -1
            out+=[(x0,y) for y in range(y0,y1+st,st)]
        else:
            st=1 if x1>x0 else -1
            out+=[(x,y0) for x in range(x0,x1+st,st)]
    return out
par={}
def f(a):
    par.setdefault(a,a)
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
def u(a,b): par[f(a)]=f(b)
used={}
for tr in thick+thin:
    cs=cells(tr)
    for c in cs: u(c,cs[0])
for b in bncs:
    for sp in b[4][1:]: u(sp,b[4][0])
pinmap={"B+":(5,2),"B-":(5,14),"J1.PULS":(1,6),"J1.PILA":(1,8),"J4.RET":(34,3),"J4.INI":(34,5),"J3.RET":(34,7),"J3.LLAVE":(34,9),
 "R1.a":(26,0),"R1.b":(26,9),"R2.a":(4,6),"R2.b":(9,6),"R3.a":(13,5),"R3.b":(13,9),"RS.a":(16,7),"RS.b":(16,14),
 "Q1.G":(14,5),"Q1.D":(15,5),"Q1.S":(16,5),"C1+":(29,12),"C1-":(31,12),"BNC1.c":(20,15),"BNC1.m":(18,17),"BNC2.c":(26,15),"BNC2.m":(24,17)}
expected={"VIN":["B+","R1.a"],"A":["R1.b","C1+","J3.LLAVE","BNC2.c"],"K":["J3.RET","J4.INI"],"I":["J4.RET","Q1.D"],
 "S":["Q1.S","RS.a","BNC1.c"],"GND":["RS.b","C1-","B-","J1.PILA","R3.b","BNC1.m","BNC2.m"],"PB":["J1.PULS","R2.a"],"G":["R2.b","R3.a","Q1.G"]}
for p in pinmap.values(): f(p)
for net,ps in expected.items():
    roots={f(pinmap[p]) for p in ps}
    assert len(roots)==1,(net,ps)
roots=[f(pinmap[ps[0]]) for ps in expected.values()]
assert len(set(roots))==len(roots),"dos redes en corto"
# ningún agujero de pin de otra red está sobre una pista
allcells={}
for tr in thick+thin:
    for c in cells(tr): allcells[c]=f(c)
for name,p in pinmap.items():
    if p in allcells: assert allcells[p]==f(p)
for c in pins:
    if c in allcells: assert allcells[c]==f(c)
print("conexionado OK:", {k:len(v) for k,v in expected.items()})
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
    for nm,lab,(ci,cj),(li,lj),c in bananas:
        cx,cy=X(ci,m),Y(cj)
        o.append(f'<circle class="{"kout" if view=="comp" else "cmpg"}" cx="{cx}" cy="{cy}" r="{1.75*P}"/>')
        if view=="comp":
            o.append(f'<circle class="ban {c}" cx="{cx}" cy="{cy}" r="{1.25*P}"/><circle class="banh" cx="{cx}" cy="{cy}" r="{0.45*P}"/>')
        else:
            o.append(f'<circle class="lug" cx="{cx}" cy="{cy}" r="{0.9*P}"/><path class="lugt" d="M{cx} {cy}L{X(li,m)} {Y(lj)}"/><circle class="drill" cx="{cx}" cy="{cy}" r="{0.55*P}"/>')
        o.append(f'<text class="ref" x="{cx}" y="{cy+1.75*P+14}" text-anchor="middle">{nm}</text>')
        if view=="comp":
            sd = "L"
            o.append(f'<text class="off" x="{X(-1.4,m)}" y="{cy+4}" text-anchor="end">{lab}</text>')
    for ref,lab,a,b,t in axial:
        xa,ya,xb,yb=X(a[0],m),Y(a[1]),X(b[0],m),Y(b[1])
        o.append(f'<path class="lead" d="M{xa} {ya}L{xb} {yb}"/>')
        vert = a[0]==b[0]
        L=(abs(b[0]-a[0])+abs(b[1]-a[1])-2.2)*P; T=t*P
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
    o.append(f'<path class="stripe" d="M{X(C1["c"][0]+1.6,m)} {cy-r*0.7}V{cy+r*0.7}"/>')
    o.append(f'<text class="ref" x="{cx}" y="{cy-14}" text-anchor="middle">C1</text><text class="val" x="{cx}" y="{cy+30}" text-anchor="middle">680 µF</text>')
    o.append(f'<text class="pol" x="{X(C1["pos"][0],m)}" y="{cy-6}" text-anchor="middle">+</text><text class="pol" x="{X(C1["neg"][0],m)}" y="{cy-6}" text-anchor="middle">−</text>')
    # Q1
    xl,xr=sorted([X(Q1["G"][0]-0.6,m),X(Q1["S"][0]+0.6,m)])
    o.append(f'<rect class="{g} tab" x="{xl}" y="{Y(3.0)}" width="{xr-xl}" height="{0.45*P}" rx="2"/>')
    o.append(f'<rect class="{g} q" x="{xl}" y="{Y(3.45)}" width="{xr-xl}" height="{1.2*P}" rx="2"/>')
    for k,l in [("G","G"),("D","D"),("S","S")]:
        i,j=Q1[k]
        o.append(f'<path class="lead" d="M{X(i,m)} {Y(4.65)}V{Y(5)}"/><text class="pin" x="{X(i,m)}" y="{Y(5)+18}" text-anchor="middle">{l}</text>')
    o.append(f'<text class="ref" x="{(xl+xr)/2}" y="{Y(3.45)+0.78*P}" text-anchor="middle">Q1</text>')
    # BNCs (montaje en placa a 90°, sobresalen del borde inferior)
    for nm,lab,cxh,cp,sp,c in bncs:
        bx0,bx1=sorted([X(cxh-2.9,m),X(cxh+2.9,m)])
        bc = "bnc" if view=="comp" else "cmpg"
        o.append(f'<rect class="{bc}" x="{bx0}" y="{Y(14.4)}" width="{bx1-bx0}" height="{Y(17.6)-Y(14.4)}" rx="3"/>')
        o.append(f'<rect class="{"bncn" if view=="comp" else "cmpg"}" x="{X(cxh,m)-0.95*P}" y="{Y(17.6)}" width="{1.9*P}" height="{1.6*P}" rx="2"/>')
        o.append(f'<circle class="tp {c}" cx="{X(cp[0],m)}" cy="{Y(cp[1])}" r="6"/>')
        for (i,j) in sp: o.append(f'<rect class="peg" x="{X(i,m)-5}" y="{Y(j)-5}" width="10" height="10" rx="2"/>')
        o.append(f'<text class="tpl {c}" x="{X(cxh,m)}" y="{Y(19.2)+16}" text-anchor="middle">{nm}</text>')
        if view=="comp": o.append(f'<text class="val" x="{X(cxh,m)}" y="{Y(19.2)+30}" text-anchor="middle">{lab}</text>')
    if view=="comp":
        pass
    else:
        o.append(f'<text class="net" x="{X(16,m)}" y="{Y(17)+19}" dx="0" text-anchor="middle">estrella</text>')
    o.append('</svg>')
    return "\n".join(o)

comp=board(False,"comp"); cu=board(True,"cu")

# ---------- schematic
sch=open(SP+'sch.svg').read()
rep=[
 ('<path class="w" d="M130 140H160V90H170M240 90H270M330 90H370"/>','<path class="w" d="M130 140H160V90H169M231 90H262M332 90H370"/>'),
 ('<rect class="cmp" x="170" y="80" width="70" height="20" rx="2"/>\n    <text class="t" x="166" y="66">R_carga 100 Ω 5 W</text>','<rect class="cmp" x="262" y="80" width="70" height="20" rx="2"/>\n    <text class="t" x="262" y="66">R1 · 100 Ω 3 W</text><text class="jt" x="148" y="84" text-anchor="middle">B+</text>'),
 ('<circle class="cmp" cx="272" cy="90" r="3"/><circle class="cmp" cx="328" cy="90" r="3"/>\n    <path class="w" d="M274 89L322 70"/>\n    <text class="ts" x="250" y="118">LLAVE DE CARGA</text><text class="ts" x="250" y="133">se abre antes de disparar</text>',
  '<circle class="cmp" cx="172" cy="90" r="3"/><circle class="cmp" cx="228" cy="90" r="3"/>\n    <path class="w" d="M174 89L222 70"/>\n    <text class="ts" x="150" y="118">SALIDA DE LA FUENTE</text><text class="ts" x="150" y="133">OFF antes de disparar</text>'),
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
 ('<text class="ts" x="400" y="400">pila 9 V</text>','<text class="ts" x="400" y="400">pila 9 V (J1)</text>'),
 ('<text class="ts" x="470" y="330">PULSADOR</text>','<text class="ts" x="470" y="330">PULSADOR (J1)</text>'),
]
rep += [('<text class="ts" x="44" y="168">0–15 V</text><text class="ts" x="44" y="184">límite 0,2 A</text>','<text class="ts" x="44" y="168">máx. 15 V</text><text class="ts" x="44" y="184">límite 0,1 A</text>'),('<text class="tl" x="168" y="452">GND</text>','<text class="tl" x="168" y="452">GND · B−</text>')]
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
.kout{fill:none;stroke:var(--muted);stroke-width:1;stroke-dasharray:2 3}
.ban{stroke:var(--fg);stroke-width:1.6} .ban.red{fill:#c62828} .ban.blk{fill:#222}
.banh{fill:var(--bg);stroke:var(--fg);stroke-width:1.2}
.lug{fill:none;stroke:var(--cu);stroke-width:5} .lugt{stroke:var(--cu);stroke-width:5;stroke-linecap:round} .drill{fill:var(--bg);stroke:var(--muted);stroke-width:1}
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
  <p class="lead">Circuito y armado en placa perforada de paso 2,54 mm (36 × 18 agujeros, unos 92 × 46 mm; entra en una de 10 × 5 cm). Todo va soldado en la placa, sin cables sueltos: pistas de un solo lado y sin cruces, los dos BNC del osciloscopio en el borde de abajo y dos bornes banana para la fuente. El iniciador, la llave de armado, el pulsador y la pila entran por borneras.</p>
  <div class="meta"><span>Q1 IRLZ44N</span><span>C1 680 µF 25 V</span><span>RS 0,1 Ω</span><span>2 bananas · 3 borneras · 2 BNC</span></div>
</header>

<section>
  <h2><span class="n">1</span>Circuito</h2>
  <div class="fig">{sch}</div>
  <p class="cap">Mismas referencias que en la placa. Antes de disparar se corta la fuente con su botón de salida (OFF) o sacando la banana roja. El puente de seguridad se monta en la caja, sobre los bornes del iniciador, para que también proteja el cable.</p>
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
    <li><b>Sin cruces ni cables.</b> Todas las pistas van del lado del cobre y ninguna se cruza. R1 queda parado sobre la placa pasando por arriba de la pista del drain: así lleva la carga desde la banana roja hasta C1 sin puentes.</li>
    <li><b>Lazo de descarga grueso.</b> C1+ → J3 → llave → J3 → J4 → iniciador → J4 → drain de Q1 → RS → estrella → bus de masa → C1−. Unos 14 cm de alambre de 1 mm suman ~3 mΩ, nada frente a los 2 Ω del puente. Con un pulso de 1,5 ms, el tamaño del lazo no cambia la medición.</li>
    <li><b>Masa en estrella.</b> La pata inferior de RS es la estrella. El bus de abajo junta C1−, las mallas de los BNC, R3, la banana negra y el − de la pila.</li>
    <li><b>Medición Kelvin del shunt.</b> El centro de BNC1 sale por su propia pista desde la pata superior de RS, y su malla está a dos agujeros de la estrella. CH1 lee la caída en RS y casi nada de las pistas (menos del 0,2 %).</li>
    <li><b>BNC2 lee C1 directo.</b> Su centro va a la pista de C1+ y su malla al bus.</li>
    <li><b>Gate protegido.</b> R2 y R3 están junto a Q1, y R3 lleva el gate a masa: si la pila o el pulsador quedan desconectados, Q1 queda apagado. Con la pila de 9 V el gate recibe 8,2 V.</li>
    <li><b>Conectores por función.</b> A la izquierda, lo del operador: bananas de la fuente y bornera del pulsador y la pila. A la derecha, el iniciador y la llave de armado. Abajo, el osciloscopio.</li>
  </ul>
</section>

<section>
  <h2><span class="n">4</span>Revisión del diseño</h2>
  <p>Revisé el conexionado con un programa que recorre todas las pistas: cada una de las 8 redes (fuente, C1+, llave, drain, source, gate, pulsador, masa) conecta exactamente las patas que corresponde, y ninguna toca a otra. Además corregí esto:</p>
  <div class="tw"><table style="min-width:640px"><thead><tr><th>Qué había</th><th>Problema</th><th>Cómo quedó</th></tr></thead><tbody>
    <tr><td>Fuente y pulsador en la misma bornera</td><td>Si se invertían los cables, la fuente quedaba en el gate: Q1 podía encenderse y, armado, disparar.</td><td>Fuente en bananas rojo/negro; pulsador y pila en su propia bornera J1.</td></tr>
    <tr><td>R1 de 3 W con patas a 15 mm</td><td>Su cuerpo mide ~17 mm: no entraba.</td><td>Patas a 23 mm (9 agujeros).</td></tr>
    <tr><td>RS de 2 W con patas a 12,7 mm</td><td>Su cuerpo mide ~12 mm: las patas no se podían doblar.</td><td>Patas a 17,8 mm (7 agujeros).</td></tr>
    <tr><td>Fuente de 0–30 V</td><td>C1 es de 25 V.</td><td>Máximo 15 V, límite de corriente 0,1 A. Así R1 disipa como mucho 1 W.</td></tr>
    <tr><td>Fuente conectada durante el disparo</td><td>Si el iniciador no funciona, la fuente seguiría pasándole corriente.</td><td>Salida de la fuente en OFF (o banana roja afuera) antes de armar. R1 igual limita esa corriente a 0,15 A.</td></tr>
  </tbody></table></div>
  <ul class="list">
    <li><b>Masa de la fuente y del osciloscopio.</b> El osciloscopio de 220 V tiene la malla de los BNC a tierra. Si el − de la fuente también está a tierra (medí continuidad entre la banana negra y la pata de tierra del enchufe de la fuente), se forma un lazo por la instalación que puede meter algo de ruido de 50 Hz en CH1. No es peligroso; si lo ves, apagá la salida de la fuente antes del disparo, que es lo que hay que hacer igual.</li>
    <li><b>Los BNC de placa cambian según el modelo.</b> El dibujo supone el pin central a ~5 mm del borde y las patas de masa a ±5 mm. Si el tuyo es distinto, mantené el centro en su pista y llevá las patas al bus de masa.</li>
  </ul>
</section>

<section>
  <h2><span class="n">5</span>Materiales de la placa</h2>
  <div class="tw"><table style="min-width:640px"><thead><tr><th>Ref.</th><th>Componente</th><th>Agujeros (col, fila)</th><th>Nota</th></tr></thead><tbody>
    <tr><td>B+, B−</td><td>Borne banana 4 mm de panel, rojo y negro</td><td class="n">centros 2,2 · 2,14</td><td>Separados 30 mm. Agujero de 6–8 mm según el borne, arandela aislante a cada lado, y el terminal de ojal abajo, soldado a su pista (5,2 y 5,14).</td></tr>
    <tr><td>Q1</td><td>MOSFET IRLZ44N (o IRL540N, IRLB8721)</td><td class="n">G 14,5 · D 15,5 · S 16,5</td><td>Parado, aleta hacia atrás. Sin disipador: el pulso dura milisegundos.</td></tr>
    <tr><td>C1</td><td>Electrolítico 680 µF 25 V 105 °C, radial 10 mm</td><td class="n">+ 29,12 · − 31,12</td><td>Franja (−) hacia la derecha.</td></tr>
    <tr><td>RS</td><td>0,1 Ω 1 %, 2 W, axial</td><td class="n">16,7 · 16,14</td><td>Patas a 17,8 mm.</td></tr>
    <tr><td>R1</td><td>100 Ω 3 W, óxido metálico</td><td class="n">26,0 · 26,9</td><td>Acostado, pasa por arriba de la pista del drain.</td></tr>
    <tr><td>R2</td><td>1 kΩ ¼ W</td><td class="n">4,6 · 9,6</td><td></td></tr>
    <tr><td>R3</td><td>10 kΩ ¼ W</td><td class="n">13,5 · 13,9</td><td></td></tr>
    <tr><td>BNC1, BNC2</td><td>BNC hembra para placa a 90°, 50 Ω</td><td class="n">centro 20,15 · 26,15</td><td>Patas de masa al bus (fila 17). Si son gruesas, agrandá esos agujeros con mecha de 1,5–2 mm.</td></tr>
    <tr><td>J1, J3, J4</td><td>Bornera de 2 polos, paso 5 mm</td><td class="n">ver dibujo</td><td>Tornillos hacia afuera de la placa.</td></tr>
    <tr><td>—</td><td>Alambre de cobre estañado de 1 mm y de 0,5 mm</td><td class="n">—</td><td>Pistas gruesas y finas.</td></tr>
  </tbody></table></div>
  <p class="note">Fuera de la placa: fuente con cables banana–banana, llave de armado, pulsador, pila de 9 V, caja con el iniciador y su puente de seguridad, y el resistor de 2,2 Ω 5 W que va en J4 en lugar del iniciador para validar.</p>
</section>

<section>
  <h2><span class="n">6</span>Qué pedir en Electrónica Mendoza</h2>
  <div class="tw"><table style="min-width:640px"><thead><tr><th>Cant.</th><th>Componente</th><th>Nota</th></tr></thead><tbody>
    <tr><td class="n">1 + 1</td><td>Borne banana 4 mm de panel, rojo y negro</td><td>Con tuerca y terminal de ojal para soldar.</td></tr>
    <tr><td class="n">1</td><td>Par de cables banana–banana (rojo y negro)</td><td>Si la fuente tiene bornes banana.</td></tr>
    <tr><td class="n">2</td><td>BNC hembra para placa a 90°, 50 Ω</td><td>Llevá la placa para probar que las patas entren.</td></tr>
    <tr><td class="n">2</td><td>Cable BNC macho–BNC macho RG58, 50 cm a 1 m</td><td></td></tr>
    <tr><td class="n">2</td><td>Resistor 0,1 Ω 1 % 2 W axial</td><td>Si solo hay al 5 %, sirve: se calibra.</td></tr>
    <tr><td class="n">1</td><td>Resistor 100 Ω 3 W óxido metálico</td><td></td></tr>
    <tr><td class="n">1 m + 1 m</td><td>Alambre de cobre estañado de 1 mm y de 0,5 mm</td><td></td></tr>
    <tr><td class="n">3</td><td>Bornera de 2 polos, paso 5 mm</td><td></td></tr>
    <tr><td class="n">1</td><td>Placa perforada de 10 × 5 cm, paso 2,54 mm, islas individuales</td><td></td></tr>
  </tbody></table></div>
  <p class="note">Lo demás (IRLZ44N, 680 µF 25 V, 1 kΩ, 10 kΩ, pulsador, llave de armado, broche de 9 V) es igual que en la lista anterior. En el osciloscopio: CH1 y CH2 con atenuación ×1 y acoplamiento DC; CH1 a 100–200 mV/div, CH2 a 2–5 V/div.</p>
</section>

<section>
  <h2><span class="n">7</span>Orden de armado</h2>
  <ol class="steps">
    <li><div><h3>Agujeros de las bananas</h3><p>Antes de soldar nada, agujereá la placa en los centros de B+ y B− (2,2 y 2,14) y montá los bornes con sus arandelas aislantes y el terminal de ojal del lado del cobre.</p></div></li>
    <li><div><h3>Componentes bajos</h3><p>R2, R3, RS y R1. Doblá cada pata hacia el lado de su pista: la misma pata sirve de pista hasta el agujero siguiente.</p></div></li>
    <li><div><h3>Pistas gruesas</h3><p>Del lado del cobre, el alambre de 1 mm siguiendo el lazo: J3 → C1+, J3 ↔ J4, J4 → drain, source → RS, RS → bus de masa → C1−. Soldalo en cada agujero por donde pasa.</p></div></li>
    <li><div><h3>Borneras, C1, Q1 y BNC</h3><p>Al final los componentes altos. Los BNC con el frente sobresaliendo del borde de abajo.</p></div></li>
    <li><div><h3>Pistas finas</h3><p>Banana roja → R1, R1 → C1+, centro de BNC2 → C1+, gate, R3 a masa, la pista Kelvin desde RS hasta el centro de BNC1, y banana negra y − de pila al bus.</p></div></li>
  </ol>
</section>

<section>
  <h2><span class="n">8</span>Verificación antes de conectar nada</h2>
  <ul class="list">
    <li>Con el tester en continuidad: no hay continuidad entre el centro y la malla de BNC2 (C1+ y masa), ni entre drain y source de Q1, ni entre las dos bananas.</li>
    <li>Entre el centro y la malla de BNC1 mide casi 0 Ω (el shunt).</li>
    <li>Entre el gate y la masa mide ~10 kΩ (R3). Entre la banana roja y el centro de BNC2 mide ~100 Ω (R1).</li>
    <li>Entre la banana negra y la malla de cualquier BNC mide 0 Ω.</li>
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
