"""AG-011 - Inserto especial 3 arestas com cobertura (Steelvidea SV0682I0004-01-00-VD).
Triângulo equilátero IC Ø15,88 x 6,35, dente trapezoidal 30° em cada vértice (rosca passo 6)."""
import math
import cadquery as cq
from lib import *
OUT="/home/claude/claude-workspace/cad/acervo/saida"
cod="AG-011"
IC=15.88; T=6.35; TIP=2.20; HD=1.9; FL=math.tan(math.radians(15))
FURO=7.1; ESC=11.1   # estimados pela escala
ri=IC/2; rv=2*ri      # raio do vértice do triângulo
hb=TIP/2+HD*FL        # meia largura na base do dente
d_sh=hb/math.tan(math.radians(30))  # recuo do vértice até o ombro
def corner(ang):
    """pontos do vértice em ang (graus): ombro, flanco, ponta, flanco, ombro."""
    a=math.radians(ang); u=(math.cos(a),math.sin(a)); v=(-u[1],u[0])
    xs=rv-d_sh; xt=xs+HD
    P=lambda x,y:(u[0]*x+v[0]*y,u[1]*x+v[1]*y)
    return [P(xs,-hb),P(xt,-TIP/2),P(xt,TIP/2),P(xs,hb)]
pts=[]
for ang in (90,210,330): pts+=corner(ang)
solid=cq.Workplane("XY").polyline(pts).close().extrude(T)
solid=solid.faces(">Z").workplane().hole(FURO)
solid=solid.faces(">Z").workplane().cskHole(FURO,ESC,90) if False else solid
doc=setup_doc(0.35); msp=doc.modelspace(); g=1.5
X0,Y0=30,30
poly=[(X0+x,Y0+y) for x,y in pts]
msp.add_lwpolyline(poly,close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
for r,lay in ((ri,"CENTRO"),(FURO/2,"CONTORNO"),(ESC/2,"CONTORNO")): msp.add_circle((X0,Y0),r,dxfattribs={"layer":lay})
msp.add_line((X0-ri-2,Y0),(X0+ri+2,Y0),dxfattribs={"layer":"CENTRO"}); msp.add_line((X0,Y0-ri-2),(X0,Y0+rv+2),dxfattribs={"layer":"CENTRO"})
dim_h(msp,(X0-ri,Y0),(X0+ri,Y0),Y0-rv*0.6-2*g,txt="Ø<> (círculo inscrito)")
dim_h(msp,(X0-FURO/2,Y0),(X0+FURO/2,Y0),Y0-0.6*g,txt="Ø<>",conf=False)
msp.add_text("VISTA SUPERIOR",height=g,dxfattribs={"layer":"COTAS"}).set_placement((X0-ri,Y0+rv+4*g))
# vista lateral
sx=X0+ri+18
msp.add_lwpolyline([(sx,Y0-rv*0.5),(sx+T,Y0-rv*0.5),(sx+T,Y0+rv-d_sh+HD),(sx,Y0+rv-d_sh+HD)],close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
msp.add_line((sx+T/2,Y0-rv*0.5-2),(sx+T/2,Y0+rv+2),dxfattribs={"layer":"CENTRO"})
dim_h(msp,(sx,Y0-rv*0.5),(sx+T,Y0-rv*0.5),Y0-rv*0.6-2*g)
msp.add_text("VISTA LATERAL",height=g,dxfattribs={"layer":"COTAS"}).set_placement((sx-2,Y0+rv+4*g))
# detalhe do dente 10:1
K=5; dx,dy=sx+32,Y0-4
D=lambda x,y:(dx+K*x,dy+K*y)
prof=[(-3.2,0),(-hb,0),(-TIP/2,HD),(TIP/2,HD),(hb,0),(3.2,0)]
msp.add_lwpolyline([D(*p) for p in prof],dxfattribs={"layer":"CONTORNO","lineweight":50})
dim_h(msp,D(-TIP/2,HD),D(TIP/2,HD),dy+K*HD+2*g,txt="2,20")
dim_v(msp,D(TIP/2,0),D(TIP/2,HD),dx+K*3.6,"1,9 ±0,1")
msp.add_text("30° (ângulo incluído)   R0,20 (2x) nos cantos   0,30 (2x)",height=0.8*g,dxfattribs={"layer":"COTAS"}).set_placement((dx-K*3.2,dy-3*g))
msp.add_text("DETALHE DO DENTE (5:1) - passo 6 mm",height=g,dxfattribs={"layer":"COTAS"}).set_placement((dx-K*3.2,dy+K*HD+5*g))
yy=Y0-rv*0.6-5*g
for i,t in enumerate(["Inserto especial 3 arestas, com cobertura - Steelvidea SV0682I0004-01-00-VD, suporte especial SV0683A0001-00-01-VD.",
                      "Produto: Tubo Ø4\" STD em PVC - passo 6 mm - Ø da peça 101,60. Aprovado condicionado a anotações (11/05/2020).",
                      "Anotações à mão: \"6\" STD 2,7 ±0,1\" (altura do dente para 6\"), \"Ø da rosca 169,3\", \"Sem hone\"."]):
    msp.add_text(t,height=0.75*g,dxfattribs={"layer":"COTAS"}).set_placement((X0-ri,yy-1.4*g*i))
msp.add_text("(*) Em vermelho: não cotado no original, confirmar:",height=0.75*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((X0-ri,yy-5*g))
for i,t in enumerate(["Furo de fixação Ø7,1 com escareado Ø11,1: medidos pela escala da foto",
                      "Cota 2,20 lida como largura da ponta do dente; altura do dente 1,9 (4\" STD)",
                      "Cotas 4 (vista superior) e 3,3 (vista lateral) do original não modeladas: referência não clara"]):
    msp.add_text("- "+t,height=0.65*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((X0-ri,yy-5*g-1.3*g*(i+1)))
title_block(msp,dx+K*3.6+6*g-180*0.45,yy-5*g-1.3*g*4-32*0.45,cod,"Inserto especial 3 arestas, com cobertura","Steelvidea SV0682I0004-01-00-VD (cliente ITEC Tubos, 2020)",escala="2:1",k=0.45)
v,bb=save_all(doc,solid,OUT+"/"+cod,cod)
print(cod,"bbox",["%.2f"%b for b in bb])
