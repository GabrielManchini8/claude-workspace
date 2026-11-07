"""Planilha com todas as medidas dos tubos do acervo (gerada dos mesmos dados do CAD)."""
import math, re, sys, importlib.util, io, contextlib
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
src=open("tubos.py").read().split("import sys\nsel=")[0]
ns={}; exec(src,ns); T=ns["TUBOS"]
src=open("edutores.py").read().split("def rosca")[0]; ns2={}; exec(src,ns2); E=ns2["TAB"]
src=open("luvas.py").read().split("for cod,p in LUVAS")[0]; ns3={}; exec(src,ns3); LV=ns3["LUVAS"]
AZ="1D508C"; LA="DA901E"; VERM="C00000"
thin=Side(style="thin",color="B7C3D6"); B=Border(left=thin,right=thin,top=thin,bottom=thin)
wb=Workbook()
def folha(ws,titulo,grupos,linhas,est):
    """grupos: [(nome_grupo,[colunas])]; linhas: lista de listas; est: set de (linha,col) estimados -> texto"""
    ncol=sum(len(c) for _,c in grupos)
    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=ncol)
    ws.cell(1,1,titulo).font=Font(bold=True,size=16,color="FFFFFF"); ws.cell(1,1).fill=PatternFill("solid",fgColor=AZ)
    ws.cell(1,1).alignment=Alignment(vertical="center"); ws.row_dimensions[1].height=30
    ws.cell(2,1,"AGEL BRASIL - Tubos e Conexões | Medidas em mm | Vermelho = não cotado no original (estimado/calculado), a confirmar").font=Font(italic=True,size=9,color="555555")
    c=1
    for g,cols in grupos:
        ws.merge_cells(start_row=3,start_column=c,end_row=3,end_column=c+len(cols)-1)
        cell=ws.cell(3,c,g); cell.font=Font(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor=LA); cell.alignment=Alignment(horizontal="center")
        for i,h in enumerate(cols):
            x=ws.cell(4,c+i,h); x.font=Font(bold=True,color=AZ); x.fill=PatternFill("solid",fgColor="EEF2F8")
            x.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True); x.border=B
            ws.cell(3,c+i).border=B
        c+=len(cols)
    ws.row_dimensions[4].height=48
    for r,row in enumerate(linhas):
        for j,v in enumerate(row):
            x=ws.cell(5+r,1+j,v); x.border=B; x.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True)
            if isinstance(v,float): x.number_format="0.0##"
            if r%2: x.fill=PatternFill("solid",fgColor="F7F9FC")
            if (r,j) in est:
                x.font=Font(color=VERM,bold=True); x.comment=Comment(est[(r,j)],"Acervo Agel")
        ws.cell(5+r,1).font=Font(bold=True,color=AZ)
    for j in range(ncol): ws.column_dimensions[get_column_letter(j+1)].width=13
    ws.column_dimensions["B"].width=34
    ws.freeze_panes="C5"
# ---------- Tubos de revestimento ----------
ordem=["AG-001","AG-002","AG-003","AG-004","AG-005"]
info={"AG-001":("DN100","4\"","STD","50,9"),"AG-002":("DN115","4½\"","STD","52,4"),"AG-003":("DN150","6\"","Leve","47 ou 49"),
      "AG-004":("DN150","6\"","STD","49"),"AG-005":("DN150","6\"","Reforçado","—")}
grupos=[("IDENTIFICAÇÃO",["Código","Descrição","DN","Polegada","Classe","Material","Desenho original"]),
 ("TUBO (corpo extrudado)",["Comprimento L","Tol. L","Ø externo DE","Tol. DE","Ø interno DI","Tol. DI","Espessura de parede","Área da seção (mm²) - calc.","Massa PVC kg/m (1,40 g/cm³) - calc."]),
 ("ROSCA (perfil 30°)",["Passo P","Profundidade h","Largura do fundo","Fresa / guia (AG-017)"]),
 ("PONTA (rosca externa)",["Ø crista","Tol. crista","Ø canal (fundo)","Tol. canal","Faixa lisa","Canal de saída","Comprimento roscado","Faixa final"]),
 ("BOLSA (rosca interna)",["Ø externo da bolsa","Ø maior (crista int.)","Tol. Ø maior","Ø menor","Tol. Ø menor","Entrada","Comprimento roscado","Canal","Faixa lisa","Comprimento reto da bolsa","Fim do cone bolsa/tubo (x)"])]
linhas=[]; est={}
def tx(lst,i): return lst[i][2] if i<len(lst) else "—"
for r,cod in enumerate(ordem):
    p=T[cod]; dn,pol,cl,guia=info[cod]
    A=math.pi/4*(p["De"]**2-p["Di"]**2)
    par=p["parede"].split()[0]; part=" ".join(p["parede"].split()[1:])
    cp=p["cot_ponta"]; cb=p["cot_bolsa"]
    pt={"liso":"—","can":"—","ros":"—","fim":"—"}
    for (x1,x2,t,_),(l,ty) in zip(cp,p["ponta"]): pt[ty]=t
    bt={"ent":"—","ros":"—","can":"—","liso":"—"}
    for (x1,x2,t,_),(l,ty) in zip(cb,p["bolsa"]): bt[ty]=t
    if cod=="AG-002" or cod=="AG-004" or cod=="AG-003":  # cota longa inclui a entrada
        bt["ros"]=[t for x1,x2,t,_ in cb if x1==0 and x2>20][0]+" (inclui entrada)"
    row=[cod,p["nome"],dn,pol,cl,"PVC rígido",p["origem"].split(" - ")[0],
         p["L"],p["ltol"].replace("+/-","±"),p["De"],p["Detol"],p["Di"],p["Ditol"],par+(" "+part if part else ""),round(A,0),round(A*1e-6*1400,2),
         p["P"],p["h_ponta"],p["wr"],"Fresa P%d h%s = guia %s"%(p["P"],str(p["h_ponta"]).replace(".",","),guia) if guia!="—" else "não consta na tabela",
         p["crista"],p["ct"],p["canal"],p["cnt"],pt["liso"],pt["can"],pt["ros"],pt["fim"],
         p["De_bolsa"],p["dM"],p["dMt"],p["dm"],p["dmt"],bt["ent"],bt["ros"],bt["can"],bt["liso"],
         str(p["l_reto"])+(" "+p.get("l_reto_t","") if p.get("l_reto_t") else ""),p["x_fim_cone"]]
    linhas.append(row)
    ci=lambda name: [h for _,c in grupos for h in c].index(name)
    if not p["De_bolsa_conf"]: est[(r,ci("Ø externo da bolsa"))]="Não cotado no original: estimado pela escala do desenho."
    est[(r,ci("Fim do cone bolsa/tubo (x)"))]="Não cotado: estimado pela escala."
    est[(r,ci("Área da seção (mm²) - calc."))]="Calculado: π/4 x (DE² - DI²)."; est[(r,ci("Massa PVC kg/m (1,40 g/cm³) - calc."))]="Calculado com densidade 1,40 g/cm³."
    H=[h for _,c in grupos for h in c]; ib=len(H)-1-H[::-1].index("Comprimento roscado")
    if cod in("AG-002","AG-003","AG-004"): est[(r,ib)]="Leitura: a cota longa é medida a partir da face e inclui a entrada. Confirmar."
    if cod in("AG-003","AG-004"):
        est[(r,ci("Comprimento roscado"))]="Leitura: a cota longa vai até a ponta e inclui a faixa final. Confirmar."; row[ci("Comprimento roscado")]+=" (inclui faixa final)"
ws=wb.active; ws.title="Tubos revestimento"
folha(ws,"TUBOS DE REVESTIMENTO NERVURADO - TODAS AS MEDIDAS",grupos,linhas,est)
r0=5+len(linhas)+1
for i,t in enumerate(["Notas:","AG-001: medidas da versão NERVURADO. Versão LISO no mesmo desenho: parede (cota A) 5,0 -0/+0,2 e Ø externo 113,0 -0/+0,7.",
   "Ø maior / Ø menor da bolsa = diâmetros internos da rosca da bolsa (crista e fundo). Ø crista / Ø canal da ponta = diâmetros da rosca externa.",
   "Fresa / guia: tabela 'Rosca da Bolsa' (AG-017). 4\" = DN100, 4½\" = DN115, 6\" = DN150."]):
    ws.cell(r0+i,1,t).font=Font(bold=(i==0),size=9)
# ---------- Edutores ----------
g2=[("IDENTIFICAÇÃO",["Código","Descrição","DN","Polegada"]),("TUBO",["Comprimento L","Ø externo DE","Espessura e","Ø interno DI - calc.","Peso (kg) tabela","Massa PVC calc. (kg)"]),
    ("ROSCA EXTERNA (2 pontas)",["Comprimento roscado","Perfil","Passo","Profundidade h","Raio"])]
l2=[]; e2={}
for r,(dn,v) in enumerate(E.items()):
    pol,DE,e,peso,a,b=v[:6]; di=DE-2*e; m=math.pi/4*(DE**2-di**2)*4000*1.4e-6
    l2.append(["AG-010-"+dn,"Tubo edutor RWG %s - %s x 4 m"%(dn,pol),dn,pol,"3.996 - 4.004",DE,e,round(di,2),peso,round(m,2),v[8],"55° Whitworth 11 FPP",2.309,1.48,"R0,2"])
    e2[(r,7)]="Calculado: DE - 2e."; e2[(r,9)]="Calculado com densidade 1,40 g/cm³."
ws2=wb.create_sheet("Tubos edutores"); folha(ws2,"TUBOS EDUTORES RWG - TODAS AS MEDIDAS",g2,l2,e2)
ws2.cell(5+len(l2)+1,1,"Origem: Tubo Revestimento NERVURADO folha 13/13 (14/07/2016). Peso do DN50 consta no original como \"6,400 - 6,000\".").font=Font(size=9)
# ---------- Luvas ----------
g3=[("IDENTIFICAÇÃO",["Código","Descrição"]),("CORPO",["Comprimento L","Ø externo"]),("FURO (da esquerda para a direita: comprimento @ diâmetro)",["Segmentos do furo"]),("ROSCA",["Especificação","Tol. diâmetro menor"])]
l3=[]; e3={}
for r,(cod,p) in enumerate(LV.items()):
    seg="  |  ".join("%s @ Ø%s%s"%(str(l).replace(".",","),str(d).replace(".",","),"" if c else " (*)") for l,d,t,c in p["seg"])
    l3.append([cod,p["nome"],p["L"],p["De"],seg,p["rosca"],p["tolmin"]])
    e3[(r,4)]="(*) = segmento não cotado no original: "+p["nota"]
ws3=wb.create_sheet("Luvas"); folha(ws3,"LUVAS ROSCADAS BSP - TODAS AS MEDIDAS",g3,l3,e3); ws3.column_dimensions["E"].width=70; ws3.column_dimensions["F"].width=45
out="/mnt/project-files/acervo-agel/CAD/tabela-medidas-tubos-agel.xlsx"; wb.save(out); print(out)
