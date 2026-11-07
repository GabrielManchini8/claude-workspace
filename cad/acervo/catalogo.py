import glob,os,sys
from PIL import Image, ImageDraw, ImageFont
A="/mnt/project-files/acervo-agel/"; C=A+"CAD/"
W,H=3508,2480  # A4 paisagem 300dpi
AZ=(29,80,140); LA=(218,144,30)
logo=Image.open(A+"_logo/agel-brasil-logo.png").convert("RGBA"); logo.thumbnail((520,170))
def font(s,b=False):
    for f in (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if b else [])+["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(f): return ImageFont.truetype(f,s)
    return ImageFont.load_default()
def page(img,cod,titulo,status):
    p=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(p)
    d.rectangle((60,60,W-60,H-60),outline=AZ,width=8)
    d.rectangle((60,60,W-60,250),fill=(245,247,251)); d.line((60,250,W-60,250),fill=AZ,width=6)
    p.paste(logo,(100,60+(190-logo.height)//2),logo)
    d.text((700,95),cod,fill=AZ,font=font(70,True)); d.text((700,180),titulo,fill=(40,40,40),font=font(44))
    d.text((W-100,115),status,fill=LA,font=font(40,True),anchor="ra")
    d.rectangle((60,H-130,W-60,H-60),fill=LA); d.text((100,H-112),"AGEL BRASIL - Tubos e Conexoes  |  Acervo tecnico  |  Desenho refeito em CAD (STEP + DXF)",fill="white",font=font(36))
    im=img.convert("RGB"); bw,bh=W-200,H-250-130-60
    im.thumbnail((bw,bh),Image.LANCZOS); p.paste(im,(100+(bw-im.width)//2,280+(bh-im.height)//2)); return p
import subprocess
from PIL import ImageOps
def render(pdf):
    subprocess.run(["pdftoppm","-r","400","-png","-singlefile",pdf,"/tmp/claude-0/r"],check=True)
    im=Image.open("/tmp/claude-0/r.png").convert("RGB")
    bb=ImageOps.invert(im.convert("L")).point(lambda v:255 if v>20 else 0).getbbox()
    return im.crop((max(bb[0]-40,0),max(bb[1]-40,0),bb[2]+40,bb[3]+40))
ordem=[]
for k in range(1,18):
    cod="AG-%03d"%k
    pngs=sorted(glob.glob(C+cod+"*/"+cod+"*_desenho.png"))+sorted(glob.glob(C+cod+"/"+cod+"-*_desenho.png"))
    pngs=sorted(set(pngs))
    pasta=glob.glob(A+cod+"_*")[0]; nome=os.path.basename(pasta)[7:].replace("-"," ")
    if pngs:
        for f in pngs: ordem.append((render(f.replace(".png",".pdf")),os.path.basename(f).replace("_desenho.png",""),nome,"CAD"))
    else:
        ordem.append((Image.open(glob.glob(pasta+"/*limpo.png")[0]),cod,nome,"DIGITALIZADO - CAD PENDENTE"))
pages=[page(*o) for o in ordem]
capa=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(capa)
big=Image.open(A+"_logo/agel-brasil-logo.png").convert("RGBA"); big.thumbnail((1600,600)); capa.paste(big,((W-big.width)//2,450),big)
d.text((W//2,1250),"Acervo Tecnico - Desenhos em CAD",fill=AZ,font=font(110,True),anchor="mm")
d.text((W//2,1420),"Pecas AG-001 a AG-017 - %d folhas"%len(pages),fill=(60,60,60),font=font(60),anchor="mm")
d.text((W//2,1560),"Cotas em vermelho (*) = nao cotadas no original, a confirmar",fill=(200,0,0),font=font(48),anchor="mm")
d.rectangle((0,H-160,W,H),fill=AZ)
out=A+"CAD/catalogo-cad-acervo-agel.pdf"
capa.save(out,save_all=True,append_images=pages,resolution=300)
for o in ordem: print(o[1],o[3])
