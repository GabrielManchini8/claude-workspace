"""AG-013 e AG-016 - fresas de pastilha (10 dentes) para rosca da bolsa.
Opcao aprovada pelo usuario: modelo 3D = ENVOLTORIA DE CORTE (solido de revolucao que a
fresa descreve girando) + furo com rasgo de chaveta. Dentes/pastilhas: esquema no 2D (nao cotados).
Uso: python3 fresas.py [AG-013 AG-016]"""
import sys, math
import cadquery as cq
from lib import *
OUT="/home/claude/claude-workspace/cad/acervo/saida"
F={
"AG-013":dict(nome="Fresa circular MD soldada (117 x 7,0) - Rosca P6 h1,8 - Ø4\" STD",
  origem="MJF Ferramentas cod. 632.05.002 (24/09/2020) - material usinado: PVC",
  D=59, Dc=55.4, B=19, lado=7.515, base=3.971, topo=2.12, topo_conf=False, h=1.8,
  furo=25, furo_t="+0,10/+0,05", rasgo=6, rasgo_t="+0,05/-0,03", c_rasgo=27.8, c_t="+0,1/+0,0", z=10,
  perfil="Detalhe A (original): 30 graus, 38 graus, base 3,971 (1,732 + 2,238), altura 1,8, R0,25 (2x), 0,64, 0,5, 2,12, 2,5",
  estimados=["Largura do topo do filete 2,12: o detalhe A traz 2,12 e 2,5 sem deixar claro qual e o topo",
             "Filete desenhado simetrico; no original o topo e deslocado (1,732 / 2,238) e tem chanfro 0,64 x 0,5 a 38 graus"]),
"AG-016":dict(nome="Fresa de rosca P6 h2,6 - para Ø231 x 12,0 (2 pecas)",
  origem="Desenho chines 160519#-250-TS (carimbo nao traduzido)",
  D=59, Dc=53.8, B=29, lado=12.31, base=4.38, topo=2.5, topo_conf=True, h=2.6,
  furo=25, furo_t="+0,10/+0,05 (leitura fraca)", rasgo=6, rasgo_t="+0,05/+0,03 (leitura fraca)", c_rasgo=27.8, c_t="+0,1/0", z=10,
  perfil="Detalhe A (original): 30 graus, 38 graus, base 4,38, topo 2,5, altura 2,6, R0,5, R0,25, 0,64, 0,5",
  estimados=["Filete desenhado simetrico; no original um lado tem chanfro 0,64 x 0,5 a 38 graus",
             "Tolerancias do furo e do rasgo com leitura fraca na fotocopia"]),
}
def build(cod,p):
    R,Rc,B=p["D"]/2,p["Dc"]/2,p["B"]; rb=p["furo"]/2
    x0=p["lado"]; a=(p["base"]-p["topo"])/2
    prof=[(0,rb),(0,Rc),(x0,Rc),(x0+a,R),(x0+a+p["topo"],R),(x0+p["base"],Rc),(B,Rc),(B,rb)]
    solid=revolve(prof)
    # rasgo de chaveta: largura 6, ate 27,8 medido do fundo do furo oposto
    top=p["c_rasgo"]-rb
    key=cq.Workplane("YZ").workplane(offset=-1).center(0,(top+rb*0.5)/2).rect(p["rasgo"],top-rb*0.5).extrude(B+2)
    solid=solid.cut(key)
    k=0.9; doc=setup_doc(0.8); msp=doc.modelspace(); g=3.4
    X0,Y0=150,140
    for s in (1,-1):
        rin=rb if s<0 else top
        poly=[(X0+x,Y0+s*(r if r!=rb else rin)) for x,r in prof]
        msp.add_lwpolyline(poly,close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
        h=msp.add_hatch(color=8,dxfattribs={"layer":"HACHURA"}); h.set_pattern_fill("ANSI31",scale=0.35); h.paths.add_polyline_path(poly,is_closed=True)
    msp.add_line((X0-5,Y0),(X0+B+5,Y0),dxfattribs={"layer":"CENTRO"})
    yb=Y0-R
    dim_h(msp,(X0,yb),(X0+B,yb),yb-6*g)
    dim_h(msp,(X0,Y0-Rc),(X0+x0,Y0-Rc),yb-3*g)
    dim_h(msp,(X0+x0+p["base"],Y0-Rc),(X0+B,Y0-Rc),yb-3*g)
    dim_h(msp,(X0+x0,Y0+Rc),(X0+x0+p["base"],Y0+Rc),Y0+R+3*g)
    dim_h(msp,(X0+x0+a,Y0+R),(X0+x0+a+p["topo"],Y0+R),Y0+R+6*g,conf=p["topo_conf"])
    dim_v(msp,(X0+x0+a+0.5,Y0-R),(X0+x0+a+0.5,Y0+R),X0+B+12*g,"%%c<>")
    dim_v(msp,(X0+B,Y0-Rc),(X0+B,Y0+Rc),X0+B+8*g,"%%c<>")
    dim_v(msp,(X0+B,Y0-rb),(X0+B,Y0+top),X0+B+4*g,"<> "+p["c_t"]+" (rasgo)")
    dim_v(msp,(X0,Y0-rb),(X0,Y0+rb),X0+B*0.35,"%%c<>")
    dim_v(msp,(X0+x0+p["base"]/2,Y0+Rc),(X0+x0+p["base"]/2,Y0+R),X0-4*g,"<>")
    msp.add_text("ENVOLTORIA DE CORTE (corte longitudinal)",height=g,dxfattribs={"layer":"COTAS"}).set_placement((X0-30,Y0+R+10*g))
    msp.add_text(p["perfil"],height=0.7*g,dxfattribs={"layer":"COTAS"}).set_placement((X0-110,Y0+R+8.3*g))
    # vista frontal esquemática
    cx,cy=X0-75,Y0
    msp.add_text("VISTA FRONTAL (dentes em esquema)",height=g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,cy+R+5*g))
    msp.add_circle((cx,cy),R,dxfattribs={"layer":"ROSCA"}); msp.add_circle((cx,cy),Rc,dxfattribs={"layer":"ROSCA"})
    n=p["z"]
    for i in range(n):
        t=math.radians(90+i*360/n); u=(math.cos(t),math.sin(t)); v=(-u[1],u[0])
        # pastilha esquemática: retângulo radial de Rc-8 a R, largura 3
        pts=[(cx+u[0]*r+v[0]*w,cy+u[1]*r+v[1]*w) for r,w in ((R-9,0),(R,0),(R,-3),(R-9,-3))]
        msp.add_lwpolyline(pts,close=True,dxfattribs={"layer":"CONTORNO"})
    msp.add_circle((cx,cy),rb,dxfattribs={"layer":"CONTORNO","lineweight":50})
    w=p["rasgo"]/2; msp.add_lwpolyline([(cx-w,cy+rb*0.97),(cx-w,cy+top),(cx+w,cy+top),(cx+w,cy+rb*0.97)],dxfattribs={"layer":"CONTORNO","lineweight":50})
    msp.add_line((cx-R-4,cy),(cx+R+4,cy),dxfattribs={"layer":"CENTRO"}); msp.add_line((cx,cy-R-4),(cx,cy+R+4),dxfattribs={"layer":"CENTRO"})
    dim_h(msp,(cx-w,cy+top),(cx+w,cy+top),cy+R+2*g,txt="<> "+p["rasgo_t"])
    dim_h(msp,(cx-R,cy),(cx+R,cy),cy-R-3*g,txt="Ø<> (externo, ponta dos dentes)")
    yy=Y0-R-11*g
    for i,t in enumerate(["%d dentes com pastilha de metal duro soldada. Forma do corpo, dos dentes e das pastilhas NAO cotada no original: desenho esquematico."%n,
                          "O 3D e a envoltoria de corte (o que a fresa gera ao girar), com furo e rasgo de chaveta.","Furo Ø%s %s"%(fmt(p["furo"]),p["furo_t"])]):
        msp.add_text(t,height=0.7*g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,yy-1.3*g*i))
    msp.add_text("(*) Em vermelho: confirmar:",height=0.75*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((cx-R,yy-4.5*g))
    for i,e in enumerate(p["estimados"]):
        msp.add_text("- "+e,height=0.65*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((cx-R,yy-4.5*g-1.3*g*(i+1)))
    title_block(msp,X0+B+14*g-126,yy-4.5*g-1.3*g*(len(p["estimados"])+1)-26,cod,p["nome"],p["origem"],k=0.7)
    vol,bb=save_all(doc,solid,OUT+"/"+cod,cod)
    print(cod,"bbox",["%.2f"%b for b in bb])
for cod in (sys.argv[1:] or F): build(cod,F[cod])
