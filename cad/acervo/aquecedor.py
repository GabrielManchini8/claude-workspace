"""AG-012 - Resistência cerâmica segmentada 4 x 850 W - 220 V (um segmento de 90°).
Leitura: 223 = comprimento do arco (desenvolvido) na face interna -> R interno = 223/(pi/2) = 142,0,
confere com a flecha 42 (142 x (1 - cos 45°) = 41,6). R158 = raio externo. Altura 190."""
import math
import cadquery as cq
from lib import *
OUT="/home/claude/claude-workspace/cad/acervo/saida"
cod="AG-012"
ARCO=223.0; ALT=190.0; RE=158.0; RI=ARCO/(math.pi/2); FURO=35.0; X70=70.0
seg=(cq.Workplane("XY").circle(RE).circle(RI).extrude(ALT)
     .intersect(cq.Workplane("XY").polyline([(0,0),(RE*2,0),(RE*2,RE*2),(0,RE*2)]).close().extrude(ALT)))
seg=seg.rotate((0,0,0),(0,0,1),-45)  # segmento centrado no eixo X
hole=cq.Workplane("YZ").workplane(offset=RI-5).center(0,ALT-X70).circle(FURO/2).extrude(RE-RI+10)
seg=seg.cut(hole)
doc=setup_doc(2.2); msp=doc.modelspace(); g=8
# vista desenvolvida (planificada): horizontal = altura 190, vertical = arco 223
X0,Y0=60,40
msp.add_lwpolyline([(X0,Y0),(X0+ALT,Y0),(X0+ALT,Y0+ARCO),(X0,Y0+ARCO)],close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
hx,hy=X0+ALT-X70,Y0+ARCO/2
msp.add_circle((hx,hy),FURO/2,dxfattribs={"layer":"CONTORNO","lineweight":50})
msp.add_line((X0-8,hy),(X0+ALT+8,hy),dxfattribs={"layer":"CENTRO"}); msp.add_line((hx,Y0-8),(hx,Y0+ARCO+8),dxfattribs={"layer":"CENTRO"})
for x in (X0+30,X0+ALT-50):  # suportes de fixação (esquema)
    for y in (Y0+ARCO-2,Y0-2):
        msp.add_lwpolyline([(x,y-12),(x+22,y-12),(x+22,y+14),(x,y+14)],close=True,dxfattribs={"layer":"ROSCA"})
dim_h(msp,(X0,Y0+ARCO),(X0+ALT,Y0+ARCO),Y0+ARCO+3*g)
dim_h(msp,(hx,hy),(X0+ALT,Y0+ARCO),Y0+ARCO+1.5*g)
dim_v(msp,(X0,Y0),(X0,Y0+ARCO),X0-2.5*g,"<> (arco interno)")
dim_h(msp,(hx-FURO/2,hy),(hx+FURO/2,hy),hy-FURO/2-2.5*g,txt="Ø<>")
msp.add_text("VISTA PLANIFICADA (face interna)",height=g,dxfattribs={"layer":"COTAS"}).set_placement((X0,Y0+ARCO+5.5*g))
# vista de topo: arco de 90°
cx,cy=X0+ALT+90,Y0+ARCO/2
def arc(r,lay="CONTORNO"): msp.add_arc((cx,cy),r,-45,45,dxfattribs={"layer":lay,"lineweight":50})
arc(RI); arc(RE)
for a in (-45,45):
    t=math.radians(a); msp.add_line((cx+RI*math.cos(t),cy+RI*math.sin(t)),(cx+RE*math.cos(t),cy+RE*math.sin(t)),dxfattribs={"layer":"CONTORNO","lineweight":50})
    msp.add_line((cx,cy),(cx+RI*math.cos(t),cy+RI*math.sin(t)),dxfattribs={"layer":"CENTRO"})
msp.add_line((cx,cy),(cx+RE+10,cy),dxfattribs={"layer":"CENTRO"})
xc=cx+RI*math.cos(math.radians(45))
msp.add_line((xc,cy-RI*0.75),(xc,cy+RI*0.75),dxfattribs={"layer":"CENTRO"})
dim_h(msp,(xc,cy-10),(cx+RI,cy-10),cy-18,txt="42 (flecha)")
msp.add_text("R%s (*) interno"%fmt(round(RI,1)),height=0.8*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((cx+RI*0.55,cy+RI*0.35))
msp.add_text("R158 externo",height=0.8*g,dxfattribs={"layer":"COTAS"}).set_placement((cx+RE*0.72,cy+RE*0.76))
msp.add_text("90°",height=0.9*g,dxfattribs={"layer":"COTAS"}).set_placement((cx+30,cy+4))
msp.add_text("Espessura %s (*)"%fmt(round(RE-RI,1)),height=0.8*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((cx+RE+4,cy-RE*0.55))
msp.add_text("VISTA SUPERIOR (1 segmento de 90°)",height=g,dxfattribs={"layer":"COTAS"}).set_placement((cx,Y0+ARCO+5.5*g))
yy=Y0-4*g
for i,t in enumerate(["Resistência cerâmica segmentada 4 x 850 W - 220 V monofásica. Os 4 segmentos de 90° formam o anel completo.",
                      "Rabicho conectado diretamente ao filamento da resistência - comprimento do rabicho 2,5 m.",
                      "Anotações à mão no original: \"90 mm\", \"205 mm\", \"215 / 205 mm\" (significado não indicado)."]):
    msp.add_text(t,height=0.75*g,dxfattribs={"layer":"COTAS"}).set_placement((X0,yy-1.4*g*i))
msp.add_text("(*) Em vermelho: calculado, confirmar:",height=0.75*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((X0,yy-5*g))
for i,t in enumerate(["223 lido como comprimento do arco interno: R interno = 223 / (π/2) = 142,0; confere com a flecha 42 (cálculo dá 41,6)",
                      "Espessura 16 = R158 - R142; altura 190; furo Ø35 a 70 da borda, no meio do arco",
                      "Suportes de fixação e saída do rabicho desenhados em esquema (sem cotas no original)"]):
    msp.add_text("- "+t,height=0.65*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((X0,yy-5*g-1.3*g*(i+1)))
title_block(msp,cx+RE+30-180*1.6,yy-5*g-1.3*g*4-32*1.6,cod,"Resistência cerâmica segmentada 4 x 850 W - 220 V","Desenho do fornecedor (sem carimbo)",escala="1:2",k=1.6)
vol,bb=save_all(doc,seg,OUT+"/"+cod,cod)
print(cod,"R interno %.1f"%RI,"bbox",["%.1f"%b for b in bb])
