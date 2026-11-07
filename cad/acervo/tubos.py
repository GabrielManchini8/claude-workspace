from lib import *
import math
OUT="/home/claude/claude-workspace/cad/acervo/saida"
T15=math.tan(math.radians(15))
def grooves(x0,length,P,r_crest,r_root,inward):
    """perfil trapezoidal 30 graus, anéis (representação), retorna pontos (x,r)."""
    pts=[];h=abs(r_crest-r_root);n=int(length//P)
    wc=P/2+h*T15; wr=P/2-h*T15
    off=(length-n*P)/2
    pts.append((x0,r_crest))
    for i in range(n):
        a=x0+off+i*P+(P-wc)/2
        pts+= [(a,r_crest),(a+(wc-wr)/2,r_root),(a+(wc+wr)/2,r_root),(a+wc,r_crest)]
    pts.append((x0+length,r_crest)); return pts

TUBOS={
"AG-005":dict(nome="Tubo Revestimento Nervurado DN150 Reforcado x 4 m",L=4075,ltol="+/- 40",
  origem="Tubo Revestimento NERVURADO_ITEC folha 5/11 (14/07/2016) - PVC rigido",
  De=174.0,Detol="+0,4/-0,0",Di=151.0,Ditol="+1,6/-0,4",
  # ponta (macho)
  pc=dict(rosca_crista=169.5,ct="+0,0/-0,2",canal=163.9,cnt="+0,0/-0,2",P=7,h=2.2,l_ini=8,l_ini_t="+2/-0",l_can=6,l_can_t="+0,5/-0,0",l_ros=65,l_fim=8,l_fim_t="+2/-0"),
  # bolsa (fêmea)
  bo=dict(d_maior=171.1,dmt="+0,2/-0,0",d_menor=165.3,dnt="+0,2/-0,0",l_ent=8,l_ent_t="+0,5/-0,0",l_ros=65,l_can=6,l_can_t="+2/-0",l_fim=8,l_fim_t="+0,5/-0,0",
          l_reto=118, De_bolsa=186.0, x_fim_cone=161),
  estimados=["Diametro externo da bolsa (186)","Fim do cone de transicao bolsa/tubo (x=161)","Diametros das faixas lisas e do canal internos da bolsa (adotados = 171,1 / 165,3)","Rosca desenhada como aneis com perfil trapezoidal 30 graus (P7 h2,2 na ponta; na bolsa pela diferenca dos diametros)"]),
}
for cod,p in TUBOS.items():
    L=p["L"];R=p["De"]/2;ri=p["Di"]/2;pc=p["pc"];bo=p["bo"]
    xs=L-(pc["l_ini"]+pc["l_can"]+pc["l_ros"]+pc["l_fim"])
    rc=pc["rosca_crista"]/2
    outer=[(0,bo["De_bolsa"]/2),(bo["l_reto"],bo["De_bolsa"]/2),(bo["x_fim_cone"],R),(xs,R),(xs,rc),(xs+pc["l_ini"],rc),
           (xs+pc["l_ini"],pc["canal"]/2),(xs+pc["l_ini"]+pc["l_can"],pc["canal"]/2)]
    outer+=grooves(xs+pc["l_ini"]+pc["l_can"],pc["l_ros"],pc["P"],rc,rc-pc["h"],False)
    outer+=[(L,rc)]
    rM,rm=bo["d_maior"]/2,bo["d_menor"]/2
    a=bo["l_ent"]; b=a+bo["l_ros"]; c=b+bo["l_can"]; d=c+bo["l_fim"]
    inner=[(0,rM),(a,rM)]+grooves(a,bo["l_ros"],pc["P"],rm,rM,True)+[(b,rM),(c,rM),(c,rm),(d,rm),(bo["x_fim_cone"],ri),(L,ri)]
    prof=outer+list(reversed(inner))
    solid=revolve(prof)
    doc=setup_doc(2.0); msp=doc.modelspace()
    # vista em corte interrompida: mostra 0..230 e L-140..L, com 60 mm de intervalo
    CUT1,CUT2=230,L-140; GAP=40
    def mapx(x): return x if x<=CUT1 else x-(CUT2-CUT1)+GAP
    def clip(pts,lo,hi):
        out=[]
        for x,r in pts:
            if lo<=x<=hi: out.append((x,r))
        return out
    X0,Y0=300,200
    for lo,hi in ((0,CUT1),(CUT2,L)):
        def rint(pts,x):
            for (x1,r1),(x2,r2) in zip(pts,pts[1:]):
                if x1<=x<=x2 and x2>x1: return r1+(r2-r1)*(x-x1)/(x2-x1)
            return pts[-1][1]
        o=[(lo,rint(outer,lo))]+clip(outer,lo,hi)+[(hi,rint(outer,hi))]
        i_=[(lo,rint(inner,lo))]+clip(inner,lo,hi)+[(hi,rint(inner,hi))]
        for s in (1,-1):
            poly=[(X0+mapx(x),Y0+s*r) for x,r in o]+[(X0+mapx(x),Y0+s*r) for x,r in reversed(i_)]
            msp.add_lwpolyline(poly,close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
            h=msp.add_hatch(color=8,dxfattribs={"layer":"HACHURA"}); h.set_pattern_fill("ANSI31",scale=1.2); h.paths.add_polyline_path(poly,is_closed=True)
    # linhas de interrupção
    for xx in (CUT1,CUT2):
        X=X0+mapx(xx)+(4 if xx==CUT1 else -4)
        msp.add_spline([(X,Y0+100),(X+3,Y0+50),(X-3,Y0),(X+3,Y0-50),(X,Y0-100)],dxfattribs={"layer":"CONTORNO"})
    msp.add_line((X0-10,Y0),(X0+mapx(L)+10,Y0),dxfattribs={"layer":"CENTRO"})
    XL=X0+mapx(L)
    # ---- cotas de comprimento
    top=Y0+bo["De_bolsa"]/2
    dim_h(msp,(X0,top),(XL,top),top+38,txt="4075 "+p["ltol"]+" (vista interrompida)")
    dim_h(msp,(X0,top),(X0+bo["l_reto"],top),top+14)
    # bolsa interna (embaixo)
    yb=Y0-bo["De_bolsa"]/2-14
    for (x1,x2,t) in ((0,a,bo["l_ent_t"]),(a,b,""),(b,c,bo["l_can_t"]),(c,d,bo["l_fim_t"])):
        dim_h(msp,(X0+x1,Y0-rm),(X0+x2,Y0-rm),yb-(14 if x1==b else 0)-(28 if x1==c else 0),txt="<> "+t)
    # ponta (em cima)
    yt=Y0+R+16
    for (x1,x2,t,k) in ((xs,xs+pc["l_ini"],pc["l_ini_t"],2),(xs+pc["l_ini"],xs+pc["l_ini"]+pc["l_can"],pc["l_can_t"],1),
                        (xs+pc["l_ini"]+pc["l_can"],L-pc["l_fim"],"",0),(L-pc["l_fim"],L,pc["l_fim_t"],1)):
        dim_h(msp,(X0+mapx(x1),Y0+rc),(X0+mapx(x2),Y0+rc),yt+k*12,txt="<> "+t)
    # espessura de parede
    xw=X0+mapx(CUT2+45)
    dim_v(msp,(xw,Y0+ri),(xw,Y0+R),xw-12,"<> +1,0/-0,0")
    # diametros da bolsa (à esquerda)
    dim_v(msp,(X0+a+3,Y0-rM),(X0+a+3,Y0+rM),X0-14,"Ø<> "+bo["dmt"])
    dim_v(msp,(X0+a+3,Y0-rm),(X0+a+3,Y0+rm),X0-30,"Ø<> "+bo["dnt"])
    dim_v(msp,(X0,Y0-bo["De_bolsa"]/2),(X0,Y0+bo["De_bolsa"]/2),X0-46,"Ø<>",conf=False)
    # diametros da ponta (à direita) - só rosca e canal
    dim_v(msp,(XL,Y0-rc),(XL,Y0+rc),XL+16,"Ø<> "+pc["ct"])
    dim_v(msp,(XL-pc["l_fim"]-pc["l_ros"]-3,Y0-pc["canal"]/2),(XL-pc["l_fim"]-pc["l_ros"]-3,Y0+pc["canal"]/2),XL+32,"Ø<> "+pc["cnt"])
    msp.add_text("CORTE K-K (1:2)",height=7,dxfattribs={"layer":"COTAS"}).set_placement((X0+60,top+52))
    msp.add_text("Rosca P7 - 30 graus - h 2,2",height=4.5,dxfattribs={"layer":"COTAS"}).set_placement((XL-150,Y0-R-30))
    # ---- vista frontal (tubo sem bolsa: De e Di)
    cx,cy=X0-190,Y0
    msp.add_text("VISTA FRONTAL - TUBO",height=7,dxfattribs={"layer":"COTAS"}).set_placement((cx-70,cy+R+30))
    for rr in (R,ri): msp.add_circle((cx,cy),rr,dxfattribs={"layer":"CONTORNO","lineweight":50})
    msp.add_line((cx-R-8,cy),(cx+R+8,cy),dxfattribs={"layer":"CENTRO"}); msp.add_line((cx,cy-R-8),(cx,cy+R+8),dxfattribs={"layer":"CENTRO"})
    d=msp.add_diameter_dim(center=(cx,cy),radius=R,angle=35,dimstyle="EZDXF",text="Ø174,0 "+p["Detol"]+" (externo)",dxfattribs={"layer":"COTAS"}); d.render()
    d=msp.add_diameter_dim(center=(cx,cy),radius=ri,angle=-35,dimstyle="EZDXF",text="Ø151,0 "+p["Ditol"]+" (interno)",dxfattribs={"layer":"COTAS"}); d.render()
    # carimbo + estimados
    tb_x=XL-180
    title_block(msp,XL-360,-60,cod,p["nome"],p["origem"],escala="1:2",k=2.0)
    yy=Y0-bo["De_bolsa"]/2-60
    msp.add_text("(*) Cotas em vermelho NAO existem no desenho original - estimadas pela escala, confirmar:",height=6,dxfattribs={"layer":"CONFIRMAR"}).set_placement((X0-280,yy))
    for k,e in enumerate(p["estimados"]):
        msp.add_text("- "+e,height=5,dxfattribs={"layer":"CONFIRMAR"}).set_placement((X0-280,yy-9*(k+1)))
    for s in doc.dimstyles: pass
    st=doc.dimstyles.get("EZDXF"); 
    vol,bb=save_all(doc,solid,OUT+"/"+cod,cod)
    print(cod,"vol %.0f cm3"%(vol/1000),"bbox",["%.1f"%b for b in bb])
