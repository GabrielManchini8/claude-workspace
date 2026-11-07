"""Gerador de peças de revolução: STEP 3D + DXF 2D cotado + PDF/PNG.
Todas as medidas em mm. Cotas marcadas 'conf=False' saem em vermelho
com '(*)' = medida estimada pela escala da foto, a confirmar."""
import cadquery as cq, ezdxf, os
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons.drawing import matplotlib as dxfplt

AZUL=5; VERM=1
def revolve(profile):
    """profile: lista de (x, r) fechada no plano XZ (x = eixo). Retorna sólido."""
    pts=[]
    for x,r in profile:
        if not pts or abs(pts[-1][0]-x)>1e-6 or abs(pts[-1][1]-r)>1e-6: pts.append((x,r))
    if abs(pts[0][0]-pts[-1][0])<1e-6 and abs(pts[0][1]-pts[-1][1])<1e-6: pts.pop()
    wp=cq.Workplane("XY").polyline(pts).close()
    return wp.revolve(360,(0,0,0),(1,0,0))

def setup_doc(k=1.0):
    doc=ezdxf.new("R2018",setup=True); doc.units=ezdxf.units.MM
    for n,c in [("CONTORNO",7),("COTAS",AZUL),("HACHURA",8),("CENTRO",3),("ROSCA",2),("CONFIRMAR",VERM),("CARIMBO",7)]:
        doc.layers.add(n,color=c)
    doc.layers.get("CENTRO").dxf.linetype="CENTER"
    doc.layers.get("ROSCA").dxf.linetype="DASHED" if "DASHED" in doc.linetypes else "CONTINUOUS"
    st=doc.dimstyles.get("EZDXF"); st.dxf.dimtxt=3.0*k; st.dxf.dimasz=2.5*k; st.dxf.dimexo=1.0*k; st.dxf.dimexe=1.5*k; st.dxf.dimgap=0.8*k; st.dxf.dimdec=2; st.dxf.dimdsep=ord(","); st.dxf.dimzin=8
    return doc

def fmt(v):
    s=("%.3f"%v).rstrip("0").rstrip("."); return s.replace(".",",")
def dim_h(msp,p1,p2,y,txt=None,conf=True):
    txt=(txt or "<>").replace("<>",fmt(abs(p2[0]-p1[0])))
    d=msp.add_linear_dim(base=(p1[0],y),p1=p1,p2=p2,dimstyle="EZDXF",text=txt+("" if conf else " (*)"),
        dxfattribs={"layer":"COTAS" if conf else "CONFIRMAR"}); d.render()
def dim_v(msp,p1,p2,x,txt,conf=True):
    txt=txt.replace("<>",fmt(abs(p2[1]-p1[1]))).replace("%%c","\u00d8")
    d=msp.add_linear_dim(base=(x,p1[1]),p1=p1,p2=p2,angle=90,dimstyle="EZDXF",text=txt+("" if conf else " (*)"),
        dxfattribs={"layer":"COTAS" if conf else "CONFIRMAR"}); d.render()

def section_revolution(msp,outer,inner,x0=0,y0=0,hatch=True):
    """outer/inner: listas de (x, r) do contorno externo e do furo (de x=0 a x=L).
    Desenha corte longitudinal completo (metade de cima e de baixo)."""
    for s in (1,-1):
        poly=[(x0+x,y0+s*r) for x,r in outer]+[(x0+x,y0+s*r) for x,r in reversed(inner)]
        msp.add_lwpolyline(poly,close=True,dxfattribs={"layer":"CONTORNO","lineweight":50})
        if hatch:
            h=msp.add_hatch(color=8,dxfattribs={"layer":"HACHURA"}); h.set_pattern_fill("ANSI31",scale=0.6)
            h.paths.add_polyline_path(poly,is_closed=True)
    # arestas visíveis do furo (linhas verticais nas mudanças de diâmetro, atrás do corte)
    L=outer[-1][0]
    msp.add_line((x0-5,y0),(x0+L+5,y0),dxfattribs={"layer":"CENTRO"})

def title_block(msp,x,y,cod,nome,origem,escala="1:1",obs="",k=1.0):
    w,h=180*k,32*k
    msp.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],close=True,dxfattribs={"layer":"CARIMBO","lineweight":50})
    for yy in (10,22): msp.add_line((x,y+yy*k),(x+w,y+yy*k),dxfattribs={"layer":"CARIMBO"})
    msp.add_line((x+40*k,y),(x+40*k,y+22*k),dxfattribs={"layer":"CARIMBO"})
    def t(s,px,py,hgt): msp.add_text(s,height=hgt*k,dxfattribs={"layer":"CARIMBO"}).set_placement((x+px*k,y+py*k))
    t("AGEL BRASIL",3,25.5,4.5); t("Tubos e Conexões",60,26,3)
    t(cod,3,14,4); t(nome,43,14,3.2)
    t("Escala "+escala,3,3.5,2.6); t("Ref.: "+origem,43,3.5,2.3)
    if obs: msp.add_text(obs,height=2.4*k,dxfattribs={"layer":"CARIMBO"}).set_placement((x,y-5*k))

def save_all(doc,solid,out,cod):
    os.makedirs(out,exist_ok=True)
    doc.saveas(f"{out}/{cod}.dxf")
    cq.exporters.export(solid,f"{out}/{cod}.step")
    cq.exporters.export(solid,f"{out}/{cod}.stl",tolerance=0.02,angularTolerance=0.1)
    cq.exporters.export(solid,f"{out}/{cod}_3d.svg",opt={"projectionDir":(1,-1.2,0.8),"showHidden":False,"width":700,"height":500,"strokeWidth":0.4})
    import matplotlib; matplotlib.use("Agg")
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
    import matplotlib.pyplot as plt
    fig=plt.figure(figsize=(16.54,11.69)); ax=fig.add_axes([0,0,1,1])
    cfg=Configuration(background_policy=BackgroundPolicy.WHITE,color_policy=ColorPolicy.COLOR)
    Frontend(RenderContext(doc),MatplotlibBackend(ax),config=cfg).draw_layout(doc.modelspace())
    ax.set_aspect("equal"); fig.savefig(f"{out}/{cod}_desenho.pdf"); fig.savefig(f"{out}/{cod}_desenho.png",dpi=150); plt.close(fig)
    bb=solid.val().BoundingBox(); return solid.val().Volume(), (bb.xlen,bb.ylen,bb.zlen)
