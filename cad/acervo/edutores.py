"""AG-010 - Tubos edutores RWG DN25..DN60 (tabela da folha 13/13).
Tubo liso com rosca externa 55 graus 11 FPP nas duas pontas.
Uso: python3 edutores.py [DN25 DN32 ...]"""
import sys, math
from lib import *
OUT="/home/claude/claude-workspace/cad/acervo/saida"
# produto: (DE, e, peso kg, L rosca min, max)
TAB={"DN25":("1\"",33.50,3.5,"1,850 - 1,950",20.0,22.5,"33,50","3,5","20,0 - 22,5"),
     "DN32":("1.1/4\"",42.00,3.7,"2,600 - 2,850",21.5,24.0,"42,00","3,7","21,5 - 24,0"),
     "DN40":("1.1/2\"",47.80,6.0,"4,450 - 4,700",23.5,27.0,"47,80","6,0","23,5 - 27,0"),
     "DN50":("2\"",59.75,7.0,"6,400 - 6,000",25.5,30.0,"59,75","7,0","25,5 - 30,0"),
     "DN60":("2.1/2\"",75.00,7.5,"8,700 - 9,000",30.0,36.0,"75,00","7,5","30,0 - 36,0")}
L=4000.0; P=2.309; H=1.48; T=math.tan(math.radians(27.5))
CR=0.30  # largura plana representando R0,2 na crista e no fundo

def rosca(x0,x1,rc):
    """sulcos 55 graus (V) entre x0 e x1, crista rc, prof. H."""
    fl=H*T; pts=[(x0,rc)]; n=int((x1-x0)//P); x=x0+(x1-x0-n*P)/2
    for i in range(n):
        a=x+i*P+(P-2*fl-CR)/2
        pts+=[(a,rc),(a+fl,rc-H),(a+fl+CR,rc-H),(a+2*fl+CR,rc)]
    return pts+[(x1,rc)]

def build(dn):
    pol,DE,e,peso,lr0,lr1=TAB[dn][:6]; R=DE/2; ri=R-e; lr=(lr0+lr1)/2
    outer=rosca(0,lr,R)+rosca(L-lr,L,R)
    solid=revolve(outer+[(L,ri),(0,ri)])
    k=DE/60; g=4*k
    doc=setup_doc(0.9*k); msp=doc.modelspace()
    CUT1=lr+25*k; CUT2=L-lr-25*k; GAP=12*k
    mapx=lambda x: x if x<=CUT1 else x-(CUT2-CUT1)+GAP
    X0,Y0=120*k,100*k
    for lo,hi in ((0,CUT1),(CUT2,L)):
        o=[(lo,R)]+[q for q in outer if lo<=q[0]<=hi]+[(hi,R)]
        for s in (1,-1):
            poly=[(X0+mapx(x),Y0+s*r) for x,r in o]+[(X0+mapx(hi),Y0+s*ri),(X0+mapx(lo),Y0+s*ri)]
            msp.add_lwpolyline(poly,close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
            h=msp.add_hatch(color=8,dxfattribs={"layer":"HACHURA"}); h.set_pattern_fill("ANSI31",scale=0.3*k); h.paths.add_polyline_path(poly,is_closed=True)
    for xx,dx in ((CUT1,2*k),(CUT2,-2*k)):
        X=X0+mapx(xx)+dx; Hh=R+3*k
        msp.add_spline([(X,Y0+Hh),(X+1.5*k,Y0+Hh/2),(X-1.5*k,Y0),(X+1.5*k,Y0-Hh/2),(X,Y0-Hh)],dxfattribs={"layer":"CONTORNO"})
    XL=X0+mapx(L)
    msp.add_line((X0-5*k,Y0),(XL+5*k,Y0),dxfattribs={"layer":"CENTRO"})
    dim_h(msp,(X0,Y0-R),(XL,Y0-R),Y0-R-4*g,txt="L 3.996 - 4.004 (vista interrompida)")
    dim_h(msp,(X0,Y0-R),(X0+lr,Y0-R),Y0-R-1.8*g,txt="L rosca %s - %s"%(fmt(lr0),fmt(lr1)))
    dim_h(msp,(XL-lr,Y0-R),(XL,Y0-R),Y0-R-1.8*g,txt="%s - %s"%(fmt(lr0),fmt(lr1)))
    dim_v(msp,(X0+lr+3*k,Y0-R),(X0+lr+3*k,Y0+R),X0-3*g,"DE %%c<>")
    dim_v(msp,(XL-lr-4*k,Y0+ri),(XL-lr-4*k,Y0+R),XL+2*g,"e <>")
    dim_v(msp,(X0+lr,Y0-ri),(X0+lr,Y0+ri),X0+mapx(CUT1)-3*g,"%%c<> (interno)")
    msp.add_text("CORTE LONGITUDINAL - TUBO EDUTOR RWG %s - %s"%(dn,pol),height=g,dxfattribs={"layer":"COTAS"}).set_placement((X0,Y0+R+5*g))
    msp.add_text("Rosca externa nas duas pontas: 55 graus (Whitworth) - 11 FPP - passo 2,309 - h 1,48 - R0,2",height=0.75*g,dxfattribs={"layer":"COTAS"}).set_placement((X0,Y0+R+3.3*g))
    # vista frontal
    cx,cy=X0-12*g-R,Y0
    for rr in (R,ri): msp.add_circle((cx,cy),rr,dxfattribs={"layer":"CONTORNO","lineweight":50})
    msp.add_circle((cx,cy),R-H,dxfattribs={"layer":"ROSCA"})
    msp.add_line((cx-R-3*k,cy),(cx+R+3*k,cy),dxfattribs={"layer":"CENTRO"}); msp.add_line((cx,cy-R-3*k),(cx,cy+R+3*k),dxfattribs={"layer":"CENTRO"})
    dim_h(msp,(cx-ri,cy),(cx+ri,cy),cy+0.4*ri,txt="Ø<> (interno)")
    dim_h(msp,(cx-R,cy),(cx+R,cy),cy-R-2*g,txt="Ø<> (externo)")
    msp.add_text("VISTA FRONTAL",height=g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,cy+R+5*g))
    # tabela
    ty=Y0-R-9*g; W=[74,24,18,32,34,32]; cols=[0]; rh=2.2*g
    for w in W: cols.append(cols[-1]+w*k)
    hdr=["PRODUTO","DE [mm]","e [mm]","PESO [kg]","L [mm]","L ROSCA [mm]"]
    msp.add_text("TABELA DE EDUTORES RWG (original) - linha em azul = esta folha",height=0.9*g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,ty+0.6*g))
    rows=[hdr]+[["TUBO EDUTOR RWG %s - %s"%(d,v[0]),v[6],v[7],v[3],"3.996 - 4.004",v[8]] for d,v in TAB.items()]
    for j,row in enumerate(rows):
        y=ty-(j+1)*rh; lay="COTAS" if j>0 and list(TAB)[j-1]==dn else "CARIMBO"
        for i,c in enumerate(row):
            msp.add_text(c,height=0.7*g,dxfattribs={"layer":lay}).set_placement((cx-R+cols[i]+0.4*g,y+0.6*g))
        msp.add_line((cx-R,y),(cx-R+cols[-1],y),dxfattribs={"layer":"CARIMBO"})
    msp.add_line((cx-R,ty),(cx-R+cols[-1],ty),dxfattribs={"layer":"CARIMBO"})
    for c in cols: msp.add_line((cx-R+c,ty),(cx-R+c,ty-len(rows)*rh),dxfattribs={"layer":"CARIMBO"})
    vol,_=solid.val().Volume(),0
    yn=ty-len(rows)*rh-2*g
    for i,t in enumerate(["Comprimento da rosca modelado no valor médio da faixa (%s)."%fmt(lr),
              "Conferência: massa do modelo em PVC (1,40 g/cm3) = %.2f kg; tabela = %s kg."%(vol*1.4e-6,peso),
              "Anotações a mão no original: \"1.1/2\" Reforçado\" e \"35\" (abaixo de L rosca do DN60)."]):
        msp.add_text(t,height=0.7*g,dxfattribs={"layer":"COTAS"}).set_placement((cx-R,yn-1.4*g*i))
    title_block(msp,XL-180*0.75*k,yn-1.4*g*3-28*k,"AG-010 "+dn,"Tubo edutor RWG %s - %s x 4 m"%(dn,pol),"Tubo Revestimento NERVURADO folha 13/13 (14/07/2016)",escala="1:1",k=0.75*k)
    cod="AG-010-"+dn
    v,bb=save_all(doc,solid,OUT+"/"+cod,cod)
    print(cod,"massa PVC %.2f kg (tabela %s)"%(v*1.4e-6,peso))

for dn in (sys.argv[1:] or TAB): build(dn)
