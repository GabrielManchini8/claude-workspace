from lib import *
OUT="/home/claude/claude-workspace/cad/acervo/saida"
# segmentos do furo, da esquerda p/ direita: (comprimento, diâmetro, tipo, confirmado)
LUVAS={
"AG-006":dict(nome="Luva roscada 1.1/4\" BSP paralela 11 FPP",De=52,L=80,origem="Tubo Revestimento NERVURADO_ITEC folha 8/11 (14/07/2016)",
  rosca="Rosca 1.1/4\" BSP paralela 11FPP - Passo 2,309 - h 1,48 - r 0,32", tolmin="+0,00/-0,10",
  seg=[(10,42.2,"rebaixo",1),(22,39.0,"rosca",1),(3,42.2,"alivio",1),(10,33.1,"centro",1),(3,42.2,"alivio",0),(22,39.0,"rosca",0),(10,42.2,"rebaixo",0)],
  nota="Lado direito não cotado no original: adotado simétrico ao esquerdo (fecha exatamente 80)."),
"AG-007":dict(nome="Luva roscada 1.1/2\" BSP STD paralela 11 FPP",De=59.70,L=80,origem="Tubo Revestimento NERVURADO_ITEC folha 9/11 (14/07/2016)",
  rosca="Rosca 1.1/2\" BSP STD paralela 11FPP - Passo 2,309 - h 1,48 - r 0,32 - Di 45 - Df 44,5", tolmin="+0,00/-0,10",
  seg=[(10,48.1,"rebaixo",1),(22,45.0,"rosca",1),(3,48.1,"alivio",1),(10,36.0,"centro",1),(3,48.1,"alivio",0),(22,45.0,"rosca",0),(10,48.1,"rebaixo",0)],
  nota="Lado direito não cotado no original: adotado simétrico ao esquerdo (fecha exatamente 80). Cota Df 44,5 mostrada como nota."),
"AG-008":dict(nome="Luva roscada 1.1/2\" BSP REF paralela 11 FPP",De=60,L=120,origem="Tubo Revestimento NERVURADO_ITEC folha 10/11 (14/07/2016)",
  rosca="Rosca 1.1/2\" BSP REF paralela 11FPP - Passo 2,309 - h 1,48 - r 0,32 - Di 45 - Df 44,4", tolmin="+0,00/-0,10",
  seg=[(11,47.8,"rebaixo",1),(34,45.0,"rosca",1),(3,47.8,"alivio",1),(25,33.8,"centro",1),(36,45.0,"rosca",0),(11,47.8,"rebaixo",0)],
  nota="Lado direito NÃO cotado no original e não é simétrico: 36 + 11 = 47 medidos pela escala da foto. CONFIRMAR."),
}
for cod,p in LUVAS.items():
    L,R=p["L"],p["De"]/2
    inner=[];x=0
    for l,d,_,_ in p["seg"]:
        inner+= [(x,d/2),(x+l,d/2)]; x+=l
    assert abs(x-L)<1e-6,(cod,x)
    # sólido
    outer_prof=[(0,R),(L,R)]
    prof=outer_prof+list(reversed(inner))
    solid=revolve(prof)
    doc=setup_doc(); msp=doc.modelspace()
    X0,Y0=110,150
    section_revolution(msp,outer_prof,inner,X0,Y0)
    # linhas verticais das mudanças de diâmetro (visíveis no corte)
    x=0
    for l,d,_,_ in p["seg"][:-1]:
        x+=l; prev=None
    xs=0
    for i,(l,d,t,_) in enumerate(p["seg"]):
        if i>0:
            dp=p["seg"][i-1][1]; r=max(d,dp)/2
            msp.add_line((X0+xs,Y0-r),(X0+xs,Y0+r),dxfattribs={"layer":"CONTORNO"})
        if t=="rosca":  # rosca cosmética: diâmetro maior em linha fina
            dM=p["seg"][i-1][1]/2
            for s in (1,-1): msp.add_line((X0+xs,Y0+s*dM),(X0+xs+l,Y0+s*dM),dxfattribs={"layer":"ROSCA"})
        xs+=l
    # vista frontal
    cx,cy=X0-55,Y0
    msp.add_circle((cx,cy),R,dxfattribs={"layer":"CONTORNO"})
    for d in sorted({s[1] for s in p["seg"]}): msp.add_circle((cx,cy),d/2,dxfattribs={"layer":"CONTORNO"})
    msp.add_line((cx-R-4,cy),(cx+R+4,cy),dxfattribs={"layer":"CENTRO"}); msp.add_line((cx,cy-R-4),(cx,cy+R+4),dxfattribs={"layer":"CENTRO"})
    # cotas de comprimento (embaixo)
    yb=Y0-R-12; xs=0
    for i,(l,d,t,c) in enumerate(p["seg"]):
        dim_h(msp,(X0+xs,Y0-d/2),(X0+xs+l,Y0-d/2),yb-(i%2)*7,conf=bool(c)); xs+=l
    dim_h(msp,(X0,Y0-R),(X0+L,Y0-R),yb-22)
    # cotas de diâmetro (à esquerda do corte)
    dim_v(msp,(X0,Y0-R),(X0,Y0+R),X0-10-0,"%%c<>")
    ds=[]; 
    for l,d,t,c in p["seg"]:
        if d not in ds: ds.append(d)
    xs=0
    for i,d in enumerate(sorted(ds,reverse=True)):
        # posição x do primeiro segmento com esse diâmetro
        xx=0
        for l,dd,t,c in p["seg"]:
            if dd==d: break
            xx+=l
        txt="%%c<>"+(" "+p["tolmin"] if [s for s in p["seg"] if s[1]==d][0][2]=="rosca" else "")
        dim_v(msp,(X0+xx+2,Y0-d/2),(X0+xx+2,Y0+d/2),X0+L+12+i*12,txt)
    msp.add_text(p["rosca"],height=3,dxfattribs={"layer":"COTAS"}).set_placement((X0,Y0+R+14))
    msp.add_text("CORTE LONGITUDINAL 1:1",height=3.5,dxfattribs={"layer":"COTAS"}).set_placement((X0,Y0+R+22))
    title_block(msp,X0+L-60 if L>100 else X0+L-100,20,cod,p["nome"],p["origem"],obs="(*) "+p["nota"]+"  Rosca representada de forma convencional (diâmetro menor).")
    vol,bb=save_all(doc,solid,OUT+"/"+cod,cod)
    print(cod,"vol %.0f mm3"%vol,"bbox",["%.1f"%b for b in bb])
