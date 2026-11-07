"""Catálogo PDF do acervo: capa + uma folha por desenho CAD + página diagramada da AG-017."""
import glob,os,subprocess
from PIL import Image, ImageDraw, ImageFont, ImageOps
A="/mnt/project-files/acervo-agel/"; C=A+"CAD/"
W,H=3508,2480  # A4 paisagem 300 dpi
AZ=(29,80,140); LA=(218,144,30); CINZA=(245,247,251)
NOMES={"AG-001":"Tubo revestimento nervurado DN100 STD (4\")","AG-002":"Tubo revestimento nervurado DN115 STD (4½\")",
"AG-003":"Tubo revestimento nervurado DN150 Leve (6\")","AG-004":"Tubo revestimento nervurado DN150 STD (6\")",
"AG-005":"Tubo revestimento nervurado DN150 Reforçado (6\")","AG-006":"Luva roscada 1.1/4\" BSP paralela 11 FPP",
"AG-007":"Luva roscada 1.1/2\" BSP STD paralela 11 FPP","AG-008":"Luva roscada 1.1/2\" BSP REF paralela 11 FPP",
"AG-009":"Disco dentado aço SAE 1045 com furo cônico","AG-010":"Tubo edutor RWG","AG-011":"Inserto especial 3 arestas, com cobertura",
"AG-012":"Resistência cerâmica segmentada 4 x 850 W - 220 V","AG-013":"Fresa circular MD soldada 117 x 7,0 - Ø4\" STD",
"AG-014":"Fresa diamantada DN 60 mm - 11 FPP","AG-015":"Fresa diamantada D50 - 11,5 FPP NPT",
"AG-016":"Fresa de rosca P6 h2,6 - para Ø231 x 12,0","AG-017":"Rosca da bolsa: fresa x guia"}
logo=Image.open(A+"_logo/agel-brasil-logo.png").convert("RGBA"); logo.thumbnail((520,170))
def font(s,b=False):
    f="/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"%("-Bold" if b else "")
    return ImageFont.truetype(f,s)
def moldura(cod,titulo,status="DESENHO CAD"):
    p=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(p)
    d.rectangle((60,60,W-60,H-60),outline=AZ,width=8)
    d.rectangle((60,60,W-60,250),fill=CINZA); d.line((60,250,W-60,250),fill=AZ,width=6)
    p.paste(logo,(100,60+(190-logo.height)//2),logo)
    d.text((700,95),cod,fill=AZ,font=font(70,True)); d.text((700,180),titulo,fill=(40,40,40),font=font(44))
    d.text((W-100,115),status,fill=LA,font=font(40,True),anchor="ra")
    d.rectangle((60,H-130,W-60,H-60),fill=LA)
    d.text((100,H-112),"AGEL BRASIL - Tubos e Conexões  |  Acervo técnico  |  Desenho refeito em CAD (STEP + DXF)",fill="white",font=font(36))
    return p,d
def page(img,cod,titulo):
    p,d=moldura(cod,titulo); im=img.convert("RGB"); bw,bh=W-200,H-250-130-60
    im.thumbnail((bw,bh),Image.LANCZOS); p.paste(im,(100+(bw-im.width)//2,280+(bh-im.height)//2)); return p
def render(pdf):
    subprocess.run(["pdftoppm","-r","400","-png","-singlefile",pdf,"/tmp/claude-0/r"],check=True)
    im=Image.open("/tmp/claude-0/r.png").convert("RGB")
    bb=ImageOps.invert(im.convert("L")).point(lambda v:255 if v>20 else 0).getbbox()
    return im.crop((max(bb[0]-40,0),max(bb[1]-40,0),bb[2]+40,bb[3]+40))
def pagina_ag017():
    p,d=moldura("AG-017",NOMES["AG-017"],"TABELA DE PROCESSO")
    d.text((W//2,380),"Rosca da Bolsa",fill=AZ,font=font(96,True),anchor="mm")
    d.text((W//2,480),"Fresa a usar e regulagem da guia para cada tubo",fill=(90,90,90),font=font(46),anchor="mm")
    cols=[("Tubo",560),("Desenho",420),("Fresa - passo",520),("Profundidade da rosca",640),("Guia",560)]
    rows=[("4\"","AG-001","P6","1,8 mm","50,9"),("4½\"","AG-002","P6","1,6 mm","52,4"),
          ("6\" Leve","AG-003","P5","1,8 mm","47 ou 49"),("6\" STD","AG-004","P6","2,6 mm","49")]
    tw=sum(w for _,w in cols); x0=(W-tw)//2; y=640; rh=230
    d.rounded_rectangle((x0,y,x0+tw,y+140),radius=24,fill=AZ)
    x=x0
    for t,w in cols: d.text((x+w//2,y+70),t,fill="white",font=font(48,True),anchor="mm"); x+=w
    y+=160
    for i,r in enumerate(rows):
        d.rounded_rectangle((x0,y,x0+tw,y+rh-30),radius=24,fill=CINZA if i%2==0 else "white",outline=(210,218,230),width=3)
        x=x0
        for j,(v,(t,w)) in enumerate(zip(r,cols)):
            if j==4:
                d.rounded_rectangle((x+90,y+35,x+w-90,y+rh-65),radius=40,fill=LA)
                d.text((x+w//2,y+(rh-30)//2),v,fill="white",font=font(62,True),anchor="mm")
            else:
                d.text((x+w//2,y+(rh-30)//2),v,fill=AZ if j in(0,2) else (50,50,50),font=font(70 if j==0 else 56,j in(0,2)),anchor="mm")
            x+=w
        y+=rh
    d.text((x0,y+40),"Fonte: anotação interna \"Rosca da Bolsa\" (texto original: 4\" Fresa P6 1.8 = Guia 50.9 / 6\" STD Fresa P6 2.6 = Guia 49 /",fill=(110,110,110),font=font(34))
    d.text((x0,y+95),"6\" Leve Fresa P5 1.8 = Guia 47 ou 49 / 4½ Fresa P6 1.6 = Guia 52.4). Passo e profundidade conferem com os desenhos AG-001 a AG-004.",fill=(110,110,110),font=font(34))
    return p
ordem=[]
for k in range(1,18):
    cod="AG-%03d"%k
    if cod=="AG-017": ordem.append(pagina_ag017()); continue
    pdfs=sorted(set(glob.glob(C+cod+"/"+cod+"*_desenho.pdf")+glob.glob(C+cod+"/"+cod+"-*_desenho.pdf")))
    assert pdfs, cod+" sem desenho CAD"
    for f in pdfs:
        c=os.path.basename(f).replace("_desenho.pdf","")
        t=NOMES[cod]+(" "+c.split("-")[-1] if c!=cod else "")
        ordem.append(page(render(f),c,t))
os.makedirs(C+"AG-017",exist_ok=True); ordem[-1].save(C+"AG-017/AG-017_tabela.pdf",resolution=300); ordem[-1].save(C+"AG-017/AG-017_tabela.png")
capa=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(capa)
big=Image.open(A+"_logo/agel-brasil-logo.png").convert("RGBA"); big.thumbnail((1600,600)); capa.paste(big,((W-big.width)//2,450),big)
d.text((W//2,1250),"Acervo Técnico - Desenhos em CAD",fill=AZ,font=font(110,True),anchor="mm")
d.text((W//2,1420),"Peças AG-001 a AG-017 - %d folhas"%len(ordem),fill=(60,60,60),font=font(60),anchor="mm")
d.text((W//2,1560),"Cotas em vermelho (*) = não cotadas no original, a confirmar",fill=(200,0,0),font=font(48),anchor="mm")
d.rectangle((0,H-160,W,H),fill=AZ)
capa.save(C+"catalogo-cad-acervo-agel.pdf",save_all=True,append_images=ordem,resolution=300)
print(len(ordem),"folhas")
