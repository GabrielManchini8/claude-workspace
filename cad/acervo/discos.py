"""AG-009 (disco SAE 1045 com furo cônico) e AG-015 (fresa diamantada D50 11,5 FPP NPT).
Peças de revolução com: cubo + alma com furos + aro dentado. x=0 na face esquerda do cubo.
Uso: python3 discos.py [AG-009 AG-015]"""
import sys, math
import cadquery as cq
from lib import *
OUT="/home/claude/claude-workspace/cad/acervo/saida"

def clip(poly,c,keep_below):
    """Sutherland-Hodgman do polígono (x,r) contra r<=c (keep_below) ou r>=c."""
    ins=(lambda p:p[1]<=c+1e-9) if keep_below else (lambda p:p[1]>=c-1e-9)
    out=[]
    for i in range(len(poly)):
        a,b=poly[i-1],poly[i]
        if ins(b):
            if not ins(a): out.append((a[0]+(b[0]-a[0])*(c-a[1])/(b[1]-a[1]),c))
            out.append(b)
        elif ins(a): out.append((a[0]+(b[0]-a[0])*(c-a[1])/(b[1]-a[1]),c))
    return out

def dentes(x0,x1,rc0,rc1,P,H,crista,fundo,trunc=()):
    """Dentes anelares na periferia (crista em cone de rc0 a rc1). trunc: [(altura, crista)] dos primeiros dentes.
    Retorna pontos (x,r) da esquerda p/ direita."""
    rc=lambda x: rc0+(rc1-rc0)*(x-x0)/(x1-x0)
    flk=(P-crista-fundo)/2; pts=[]; x=x0; i=0
    while x+P<=x1+1e-6:
        h,cr=(trunc[i] if i<len(trunc) else (H,crista))
        fl=(P-cr-fundo)/2
        a=x+fundo/2
        pts+=[(x,rc(x)-H),(a,rc(a)-H),(a+fl,rc(a+fl)-H+h),(a+fl+cr,rc(a+fl+cr)-H+h),(a+2*fl+cr,rc(a+2*fl+cr)-H),(x+P,rc(x+P)-H)]
        x+=P; i+=1
    pts+=[(x,rc(x)-H),(x1,rc(x1)-H)]
    return pts

PECAS={
"AG-009":dict(nome="Disco dentado aco SAE 1045 - furo conico (2 pecas)",
  origem="Tubo Revestimento NERVURADO_ITEC folha 12/12 (14/07/2016) - Aco SAE 1045",
  Lh=28.0, d_cubo=30, bore=(16.5,19.0), cham_cubo=1.0, cham_conf=False,
  aro=(3.0,23.0), aro_conf=False, d_aro_int=70, d_crista=(80,80),
  alma=(8.0,17.0), alma_conf=(True,False),
  furos=(8,15,50), dente=dict(P=2.309,H=1.52,crista=0.36,fundo=0.367,trunc=()),
  dente_txt="Dentes 55 graus (Whitworth) - passo 2,309 - prof. 1,52 - R0,25 crista / R0,35 fundo",
  bore_txt="Furo conico: furar Ø16,5 (menor) e abrir cone 5,1 graus ate Ø19. Chanfro nas duas arestas.",
  estimados=["Comprimento do cubo 28 = calculado do cone Ø16,5 -> Ø19 a 5,1 graus (28,07); pela escala da foto ~29",
             "Espessura da alma 9 = 28 - 8 - 11",
             "Posicao do aro: cubo sobressai 3 a esquerda (medido pela escala)",
             "Chanfro do cubo 1 x 45 graus (original pede chanfro, sem medida)",
             "Raios R0,25/R0,35 dos dentes representados como planos (crista 0,36 / fundo 0,37)",
             "Posicao axial do 1o dente nao cotada"]),
"AG-015":dict(nome="Fresa diamantada D50 - 11,5 FPP NPT",
  origem="Maquina rosqueadeira automatica - des. 32563 folha 70/70 (02/05/2015)",
  Lh=25.0, d_cubo=30, bore=(16.5,18.73), cham_cubo=2.0, cham_conf=True,
  aro=(0.0,25.0), aro_conf=True, d_aro_int=50, d_crista=(58.5,60),
  alma=(4.5,14.5), alma_conf=(False,True),
  furos=(8,10,40), dente=dict(P=2.308,H=1.59,crista=0.28,fundo=0.19,trunc=[(0.69,1.23),(1.1,0.76),(1.5,0.30)]),
  dente_txt="Dentes 60 graus - 11,5 FPP (passo 2,308) - altura 1,59 - crista 0,28 - fundo 0,19 - cone NPT 3,56 graus (Ø58,5 -> Ø60)",
  bore_txt="1- Usinar furo Ø menor 16,5   2- Usinar cone 5,1 graus ate Ø maior 18,73   3- Chanfro nos dois lados 2 x 45 graus",
  estimados=["Posicao da alma: rebaixo esquerdo 4,5 (medido pela escala); espessura 10 e cotada",
             "Primeiros 3 dentes truncados (alturas 0,69 / 1,1 / 1,5 e cristas 1,23 / 0,76 / 0,30 conforme detalhe EM)",
             "Posicao axial do 1o dente nao cotada"]),
}

def build(cod,p):
    Lh=p["Lh"]; rh=p["d_cubo"]/2; c=p["cham_cubo"]
    rb0,rb1=p["bore"][0]/2,p["bore"][1]/2
    xa0,xa1=p["aro"]; ra=p["d_aro_int"]/2; xw0,xw1=p["alma"]
    d=p["dente"]
    teeth=dentes(xa0,xa1,p["d_crista"][0]/2,p["d_crista"][1]/2,d["P"],d["H"],d["crista"],d["fundo"],d["trunc"])
    # contorno superior (sentido horário a partir do furo na face esquerda)
    prof=[(0,rb0),(0,rh-c),(c,rh),(xw0,rh),(xw0,ra),(xa0,ra)]+teeth+[(xa1,ra),(xw1,ra),(xw1,rh),(Lh-c,rh),(Lh,rh-c),(Lh,rb1)]
    solid=revolve(prof)
    n,df,pcd=p["furos"]
    for i in range(n):
        a=math.radians(90+i*360/n)
        hole=cq.Workplane("YZ").workplane(offset=xw0-1).center(pcd/2*math.cos(a),pcd/2*math.sin(a)).circle(df/2).extrude(xw1-xw0+2)
        solid=solid.cut(hole)
    # ---------- desenho ----------
    k=p["d_crista"][1]/80
    doc=setup_doc(0.9*k); msp=doc.modelspace(); g=4*k
    X0,Y0=150*k,150*k; R=p["d_crista"][1]/2
    rh0,rh1=pcd/2-df/2,pcd/2+df/2
    for s in (1,-1):
        for part in (clip(prof,rh0,True),clip(prof,rh1,False)):
            poly=[(X0+x,Y0+s*r) for x,r in part]
            msp.add_lwpolyline(poly,close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
            h=msp.add_hatch(color=8,dxfattribs={"layer":"HACHURA"}); h.set_pattern_fill("ANSI31",scale=0.35*k); h.paths.add_polyline_path(poly,is_closed=True)
        for xx in (xw0,xw1): msp.add_line((X0+xx,Y0+s*rh0),(X0+xx,Y0+s*rh1),dxfattribs={"layer":"CONTORNO"})
        # eixo do furo da alma
        msp.add_line((X0+xw0-3,Y0+s*pcd/2),(X0+xw1+3,Y0+s*pcd/2),dxfattribs={"layer":"CENTRO"})
    msp.add_line((X0-6,Y0),(X0+Lh+6,Y0),dxfattribs={"layer":"CENTRO"})
    xL=X0+min(0,xa0); xR=X0+max(Lh,xa1)
    # cotas axiais
    top=Y0+R
    dim_h(msp,(X0+xa0,top),(X0+xa1,top),top+2*g)
    if abs(Lh-(xa1-xa0))>1e-6 or xa0!=0:
        dim_h(msp,(X0,Y0-rh),(X0+Lh,Y0-rh),Y0-R-6*g,conf=False)
        dim_h(msp,(X0,Y0-rh),(X0+xa0,Y0-rh),Y0-R-2*g,conf=p["aro_conf"])
    dim_h(msp,(X0,Y0-rh1),(X0+xw0,Y0-rh1),Y0-R-4*g,conf=p["alma_conf"][0])
    if cod=="AG-009": dim_h(msp,(X0+xw1,Y0-rh1),(X0+Lh,Y0-rh1),Y0-R-4*g)
    dim_h(msp,(X0+xw0,Y0+pcd/2),(X0+xw1,Y0+pcd/2),Y0+pcd/2,conf=p["alma_conf"][1])
    # diâmetros: externos à direita/esquerda, fora da peça; furo dentro
    dim_v(msp,(X0+xa1,Y0-p["d_crista"][1]/2),(X0+xa1,Y0+p["d_crista"][1]/2),xR+12*g,"%%c<>")
    if p["d_crista"][0]!=p["d_crista"][1]:
        dim_v(msp,(X0+xa0,Y0-p["d_crista"][0]/2),(X0+xa0,Y0+p["d_crista"][0]/2),xL-6*g,"%%c<>")
    dim_v(msp,(xL,Y0-ra),(xL,Y0+ra),xL-3*g,"%%c<>")
    dim_v(msp,(X0+Lh,Y0-pcd/2),(X0+Lh,Y0+pcd/2),xR+9*g,"%%c<> (furos)")
    dim_v(msp,(X0+Lh,Y0-rh),(X0+Lh,Y0+rh),xR+6*g,"%%c<>")
    dim_v(msp,(X0+Lh,Y0-rb1),(X0+Lh,Y0+rb1),xR+3*g,"%%c<>")
    dim_v(msp,(X0,Y0-rb0),(X0,Y0+rb0),X0+Lh*0.3,"%%c<>")
    msp.add_text("5,1° (cone)",height=0.8*g,dxfattribs={"layer":"COTAS"}).set_placement((X0+Lh*0.42,Y0-1.6*g))
    msp.add_text("CORTE LONGITUDINAL (pelos furos)",height=g,dxfattribs={"layer":"COTAS"}).set_placement((X0-5*g,top+6*g))
    msp.add_text(p["dente_txt"],height=0.7*g,dxfattribs={"layer":"COTAS"}).set_placement((X0-40*k,top+4.6*g))
    # vista frontal
    cx,cy=X0-75*k,Y0
    msp.add_text("VISTA FRONTAL",height=g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,cy+R+6*g))
    msp.add_circle((cx,cy),R,dxfattribs={"layer":"CONTORNO","lineweight":50})
    msp.add_circle((cx,cy),R-d["H"],dxfattribs={"layer":"ROSCA"})
    for rr in (ra,rh,rb1,rb0): msp.add_circle((cx,cy),rr,dxfattribs={"layer":"CONTORNO"})
    msp.add_circle((cx,cy),pcd/2,dxfattribs={"layer":"CENTRO"})
    for i in range(n):
        a=math.radians(90+i*360/n); hx,hy=cx+pcd/2*math.cos(a),cy+pcd/2*math.sin(a)
        msp.add_circle((hx,hy),df/2,dxfattribs={"layer":"CONTORNO"})
    msp.add_line((cx-R-4,cy),(cx+R+4,cy),dxfattribs={"layer":"CENTRO"}); msp.add_line((cx,cy-R-4),(cx,cy+R+4),dxfattribs={"layer":"CENTRO"})
    a=math.radians(90+360/n); hx,hy=cx+pcd/2*math.cos(a),cy+pcd/2*math.sin(a)
    msp.add_text("%d x Ø%s em Ø%s (a cada %s°)"%(n,fmt(df),fmt(pcd),fmt(360/n)),height=0.8*g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,cy+R+3*g))
    dim_h(msp,(cx-R,cy),(cx+R,cy),cy-R-3*g,txt="Ø<> (externo)")
    # notas
    yy=Y0-R-10*g
    msp.add_text(p["bore_txt"],height=0.75*g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,yy))
    msp.add_text("(*) Em vermelho: NAO cotado no original - estimado, confirmar:",height=0.75*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((cx-R,yy-2*g))
    for i,e in enumerate(p["estimados"]):
        msp.add_text("- "+e,height=0.65*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((cx-R,yy-2*g-1.3*g*(i+1)))
    title_block(msp,xR+20*g-180*0.7*k,yy-2*g-1.3*g*(len(p["estimados"])+1)-30*0.7*k,cod,p["nome"],p["origem"],k=0.7*k)
    vol,bb=save_all(doc,solid,OUT+"/"+cod,cod)
    print(cod,"vol %.1f cm3"%(vol/1000),"massa aco %.0f g"%(vol*7.85e-3),"bbox",["%.2f"%b for b in bb])

for cod in (sys.argv[1:] or PECAS):
    build(cod,PECAS[cod])
