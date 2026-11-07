from lib import *
import math
OUT="/home/claude/claude-workspace/cad/acervo/saida"
T15=math.tan(math.radians(15))
def grooves(x0,length,P,r_crest,r_root,wr):
    """anéis trapezoidais 30 graus (representação da rosca): wr = largura no fundo."""
    h=abs(r_crest-r_root); wc=wr+2*h*T15; n=int(length//P); off=(length-n*P)/2
    pts=[(x0,r_crest)]
    for i in range(n):
        a=x0+off+i*P+(P-wc)/2
        pts+=[(a,r_crest),(a+(wc-wr)/2,r_root),(a+(wc+wr)/2,r_root),(a+wc,r_crest)]
    return pts+[(x0+length,r_crest)]

# Bolsa: lista de (comprimento, tipo) a partir da face: ent|ros|can|liso
# Ponta: lista de (comprimento, tipo) do degrau até a ponta: liso|can|ros|fim
# cotas: (x1,x2,texto,linha) em coordenadas da bolsa (bot) ou ponta (top, relativas ao degrau)
TUBOS={
"AG-005":dict(nome="Tubo Revestimento Nervurado DN150 Reforcado x 4 m",L=4075,ltol="+/- 40",
  origem="Tubo Revestimento NERVURADO_ITEC folha 5/11 (14/07/2016) - PVC rigido",
  De=174.0,Detol="+0,4/-0,0",Di=151.0,Ditol="+1,6/-0,4",parede="11,5 +1,0/-0,0",
  P=7,h_ponta=2.6,wr=2.6,rosca_txt="Rosca P7 - 30 graus - prof. 2,6 +0,2/-0,0 - fundo 2,6",
  crista=169.5,ct="+0,0/-0,2",canal=163.9,cnt="+0,0/-0,2",
  ponta=[(8,"liso"),(6,"can"),(65,"ros"),(8,"fim")],
  cot_ponta=[(0,8,"8 +2/-0",3),(8,14,"6,0 +0,5/-0,0",2),(14,79,"65",0),(79,87,"8 +2/-0",1)],
  dM=171.1,dMt="+0,2/-0,0",dm=165.3,dmt="+0,2/-0,0",
  bolsa=[(8,"ent"),(65,"ros"),(6,"can"),(8,"liso")],
  cot_bolsa=[(0,8,"8,0 +0,5/-0,0",1),(8,73,"65",0),(73,79,"6 +2/-0",2),(79,87,"8,0 +0,5/-0,0",3)],
  l_reto=118,De_bolsa=186.0,De_bolsa_conf=False,x_fim_cone=161,
  estimados=["Diametro externo da bolsa (186)","Fim do cone de transicao bolsa/tubo (x=161)",
             "Diametros das faixas lisas e do canal internos da bolsa (adotados = 171,1 / 165,3)",
             "Rosca desenhada como aneis (perfil 30 graus do detalhe L), sem helice"]),
"AG-002":dict(nome="Tubo Revestimento Nervurado DN115 STD x 4 m",L=4075,ltol="+/- 40",
  origem="Tubo Revestimento NERVURADO_ITEC folha 2/11 (14/07/2016) - PVC rigido",
  De=129.0,Detol="+0,3/-0,0",Di=115.0,Ditol="+1,6/-0,4",parede="7,0 +0,7/-0,0",
  P=6,h_ponta=1.6,wr=2.2,rosca_txt="Rosca P6 - 30 graus - prof. 1,6 +0,2/-0,0 - fundo 2,2",
  crista=125.5,ct="+0,0/-0,2",canal=122.1,cnt="+0,0/-0,2",
  ponta=[(8,"liso"),(6,"can"),(50,"ros"),(6,"fim")],
  cot_ponta=[(0,8,"8 +2/-0",3),(8,14,"6,0 +0,5/-0,0",2),(14,64,"50",0),(64,70,"6,0 +0,5/-0,0",1)],
  dM=125.9,dMt="+0,2/-0,0",dm=122.3,dmt="+0,2/-0,0",
  bolsa=[(6,"ent"),(44,"ros"),(6,"can"),(8,"liso")],
  cot_bolsa=[(0,6,"6,0 +0,5/-0,0",1),(0,50,"50",0),(50,56,"6,0 +0,5/-0,0",2),(56,64,"8 +2/-0",3)],
  l_reto=97,De_bolsa=136.30,De_bolsa_conf=True,x_fim_cone=118,
  estimados=["Fim do cone de transicao bolsa/tubo (x=118)",
             "Diametros das faixas lisas e do canal internos da bolsa (adotados = 125,9 / 122,3)",
             "Cota 50 da bolsa lida como medida a partir da face (inclui a entrada de 6,0) - confirmar",
             "Rosca desenhada como aneis (perfil 30 graus do detalhe R), sem helice"]),
}
import sys
sel=sys.argv[1:] or list(TUBOS)
for cod in sel:
    p=TUBOS[cod]
    L=p["L"];R=p["De"]/2;ri=p["Di"]/2;rc=p["crista"]/2
    lp=sum(l for l,_ in p["ponta"]); xs=L-lp
    outer=[(0,p["De_bolsa"]/2),(p["l_reto"],p["De_bolsa"]/2),(p["x_fim_cone"],R),(xs,R),(xs,rc)]
    x=xs
    for l,t in p["ponta"]:
        if t=="can": outer+=[(x,p["canal"]/2),(x+l,p["canal"]/2),(x+l,rc)]
        elif t=="ros": outer+=grooves(x,l,p["P"],rc,rc-p["h_ponta"],p["wr"])
        else: outer+=[(x,rc),(x+l,rc)]
        x+=l
    rM,rm=p["dM"]/2,p["dm"]/2
    inner=[];x=0
    for l,t in p["bolsa"]:
        if t in("ent","can"): inner+=[(x,rM),(x+l,rM)]
        elif t=="ros": inner+=grooves(x,l,p["P"],rm,rM,p["wr"])
        else: inner+=[(x,rm),(x+l,rm)]
        x+=l
    xb=x
    inner+=[(p["x_fim_cone"],ri),(L,ri)]
    solid=revolve(outer+list(reversed(inner)))
    k=p["De"]/174.0*2.0  # escala de texto proporcional
    doc=setup_doc(1.5*k); msp=doc.modelspace()
    CUT1=max(230,p["x_fim_cone"]+70); CUT2=L-lp-55; GAP=40
    def mapx(x): return x if x<=CUT1 else x-(CUT2-CUT1)+GAP
    def rint(pts,x):
        for (x1,r1),(x2,r2) in zip(pts,pts[1:]):
            if x1<=x<=x2 and x2>x1: return r1+(r2-r1)*(x-x1)/(x2-x1)
        return pts[-1][1]
    X0,Y0=300,200
    for lo,hi in ((0,CUT1),(CUT2,L)):
        o=[(lo,rint(outer,lo))]+[q for q in outer if lo<=q[0]<=hi]+[(hi,rint(outer,hi))]
        i_=[(lo,rint(inner,lo))]+[q for q in inner if lo<=q[0]<=hi]+[(hi,rint(inner,hi))]
        for s in (1,-1):
            poly=[(X0+mapx(x),Y0+s*r) for x,r in o]+[(X0+mapx(x),Y0+s*r) for x,r in reversed(i_)]
            msp.add_lwpolyline(poly,close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
            h=msp.add_hatch(color=8,dxfattribs={"layer":"HACHURA"}); h.set_pattern_fill("ANSI31",scale=0.7*k); h.paths.add_polyline_path(poly,is_closed=True)
    H=p["De_bolsa"]/2+8
    for xx in (CUT1,CUT2):
        X=X0+mapx(xx)+(4 if xx==CUT1 else -4)
        msp.add_spline([(X,Y0+H),(X+3,Y0+H/2),(X-3,Y0),(X+3,Y0-H/2),(X,Y0-H)],dxfattribs={"layer":"CONTORNO"})
    msp.add_line((X0-10,Y0),(X0+mapx(L)+10,Y0),dxfattribs={"layer":"CENTRO"})
    XL=X0+mapx(L); top=Y0+p["De_bolsa"]/2; g=6*k
    dim_h(msp,(X0,top),(XL,top),top+8*g,txt="%d %s (vista interrompida)"%(L,p["ltol"]))
    dim_h(msp,(X0,top),(X0+p["l_reto"],top),top+2.5*g)
    yb=Y0-p["De_bolsa"]/2-2.5*g
    for x1,x2,t,row in p["cot_bolsa"]:
        dim_h(msp,(X0+x1,Y0-rm),(X0+x2,Y0-rm),yb-row*1.6*g,txt=t)
    yt=Y0+R+2.5*g
    for x1,x2,t,row in p["cot_ponta"]:
        dim_h(msp,(X0+mapx(xs+x1),Y0+rc),(X0+mapx(xs+x2),Y0+rc),yt+row*1.6*g,txt=t)
    xw=X0+mapx(CUT2+18)
    dim_v(msp,(xw,Y0+ri),(xw,Y0+R),xw-2*g,p["parede"].replace(p["parede"].split()[0],"<>") if False else p["parede"])
    dim_v(msp,(X0+12,Y0-rM),(X0+12,Y0+rM),X0+xb+5*g,"Ø<> "+p["dMt"])
    dim_v(msp,(X0+12,Y0-rm),(X0+12,Y0+rm),X0+xb+2*g,"Ø<> "+p["dmt"])
    dim_v(msp,(X0,Y0-p["De_bolsa"]/2),(X0,Y0+p["De_bolsa"]/2),X0-7.5*g,"Ø<>",conf=p["De_bolsa_conf"])
    dim_v(msp,(XL,Y0-rc),(XL,Y0+rc),XL+2.5*g,"Ø<> "+p["ct"])
    xc=X0+mapx(xs+[l for l,t in p["ponta"]][0]+1)
    dim_v(msp,(xc,Y0-p["canal"]/2),(xc,Y0+p["canal"]/2),XL+5*g,"Ø<> "+p["cnt"])
    msp.add_text("CORTE LONGITUDINAL (1:2)",height=g,dxfattribs={"layer":"COTAS"}).set_placement((X0+40,top+10*g))
    msp.add_text(p["rosca_txt"],height=0.8*g,dxfattribs={"layer":"COTAS"}).set_placement((XL-28*g,Y0-R-3*g))
    cx,cy=X0-1.15*p["De_bolsa"]-8*g,Y0
    msp.add_text("VISTA FRONTAL - TUBO",height=g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,cy+R+4*g))
    for rr in (R,ri): msp.add_circle((cx,cy),rr,dxfattribs={"layer":"CONTORNO","lineweight":50})
    msp.add_line((cx-R-8,cy),(cx+R+8,cy),dxfattribs={"layer":"CENTRO"}); msp.add_line((cx,cy-R-8),(cx,cy+R+8),dxfattribs={"layer":"CENTRO"})
    # cota interna DENTRO do circulo; externa FORA (abaixo)
    dim_h(msp,(cx-ri,cy),(cx+ri,cy),cy+0.35*ri,txt="\u00d8%s %s (interno)"%(fmt(p["Di"]),p["Ditol"]))
    dim_h(msp,(cx-R,cy),(cx+R,cy),cy-R-2.5*g,txt="\u00d8%s %s (externo)"%(fmt(p["De"]),p["Detol"]))
    title_block(msp,XL-180*k,Y0-p["De_bolsa"]/2-22*g,cod,p["nome"],p["origem"],escala="1:2",k=k)
    yy=Y0-p["De_bolsa"]/2-10*g
    msp.add_text("(*) Em vermelho: NAO cotado no desenho original - estimado pela escala, confirmar:",height=0.8*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((cx-R,yy))
    for n,e in enumerate(p["estimados"]):
        msp.add_text("- "+e,height=0.7*g,dxfattribs={"layer":"CONFIRMAR"}).set_placement((cx-R,yy-1.5*g*(n+1)))
    vol,bb=save_all(doc,solid,OUT+"/"+cod,cod)
    print(cod,"vol %.0f cm3"%(vol/1000),"bbox",["%.1f"%b for b in bb])
