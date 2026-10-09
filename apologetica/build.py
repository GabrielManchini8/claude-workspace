"""Gera objecoes.json e app.html a partir de onde-esta-na-biblia.md.

Uso: python3 build.py
"""
import html
import json
import re
from pathlib import Path

DIR = Path(__file__).parent
MD = (DIR / "onde-esta-na-biblia.md").read_text(encoding="utf-8")

# Público de cada parte (para os filtros da página)
PARTES = {
    "I": ("Autoridade", "protestantes"),
    "II": ("Salvação", "protestantes"),
    "III": ("Sacramentos e culto", "protestantes"),
    "IV": ("Maria, santos e imagens", "protestantes"),
    "V": ("Práticas católicas", "protestantes"),
    "VI": ("TJ, unicistas, adventistas", "seitas"),
    "VII": ("Objeções ateias", "ateus"),
    "VIII": ("Mais objeções protestantes", "protestantes"),
    "IX": ("Questões morais", "moral"),
    "X": ("Mais objeções ateias", "ateus"),
    "XI": ("Islã", "islam"),
}

# Marcador no início da linha → campo
CAMPOS = [
    ("❌", "objecao"),
    ("✅", "resposta"),
    ("📖", "biblia"),
    ("🔁", "replica"),
    ("🏛️", "historia"),
    ("📚", "catecismo"),
]


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t


def md_html(text):
    """Conversor mínimo: parágrafos, listas (2 níveis), citações e tabelas."""
    out, lista, tabela = [], [], []

    def fecha_lista():
        if not lista:
            return
        h, nivel = "", -1
        for ind, item in lista:
            n = 1 if ind >= 2 and nivel >= 0 else 0
            if nivel == -1:
                h += "<ul><li>"
            elif n > nivel:
                h += "<ul><li>"
            elif n == nivel:
                h += "</li><li>"
            else:
                h += "</li></ul></li><li>"
            h += inline(item)
            nivel = n
        h += "</li>" + ("</ul></li>" if nivel == 1 else "") + "</ul>"
        out.append(h)
        lista.clear()

    def fecha_tabela():
        if not tabela:
            return
        linhas = [r for r in tabela if not re.match(r"^\|[-\s|]+\|$", r)]
        cel = lambda r: [c.strip() for c in r.strip("|").split("|")]
        h = '<div class="tbl"><table><thead><tr>'
        h += "".join(f"<th>{inline(c)}</th>" for c in cel(linhas[0])) + "</tr></thead><tbody>"
        for r in linhas[1:]:
            h += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cel(r)) + "</tr>"
        out.append(h + "</tbody></table></div>")
        tabela.clear()

    for linha in text.split("\n"):
        m = re.match(r"^( *)- (.*)", linha)
        if m:
            fecha_tabela()
            lista.append((len(m.group(1)), m.group(2)))
            continue
        fecha_lista()
        if linha.startswith("|"):
            tabela.append(linha)
            continue
        fecha_tabela()
        if not linha.strip():
            continue
        if linha.startswith(">"):
            out.append("<blockquote>" + inline(linha.lstrip("> ")) + "</blockquote>")
        else:
            out.append("<p>" + inline(linha) + "</p>")
    fecha_lista()
    fecha_tabela()
    return "".join(out)


def plano(t):
    return re.sub(r"[*_`>|]", "", t).strip()


itens, parte = [], None
estudos_islam = ""
blocos = re.split(r"^(?=# PARTE |### \d+\. |## Cola rápida|## Existem estudos)", MD, flags=re.M)
for b in blocos:
    if b.startswith("# PARTE "):
        parte = re.match(r"# PARTE ([IVX]+)", b).group(1)
        continue
    if b.startswith("## Existem estudos"):
        corpo = b.split("\n", 1)[1].split("\n---")[0]
        estudos_islam = md_html(corpo)
        continue
    m = re.match(r"### (\d+)\. (.+)", b)
    if not m:
        continue
    num, titulo = int(m.group(1)), m.group(2).strip()
    corpo = b.split("\n", 1)[1].split("\n---")[0].strip()
    campos, atual = {}, None
    for linha in corpo.split("\n"):
        for marca, nome in CAMPOS:
            if linha.startswith(marca):
                atual = nome
                linha = linha[len(marca):].strip()
                break
        if atual is None:
            atual = "biblia"
        campos.setdefault(atual, []).append(linha)
    item = {"n": num, "titulo": plano(titulo), "parte": parte,
            "tema": PARTES[parte][0], "publico": PARTES[parte][1]}
    for nome, linhas in campos.items():
        texto = "\n".join(linhas).strip()
        # Remove o rótulo em negrito do começo ("**Objeção:**", "**Na Bíblia:**"…)
        rotulo = re.match(r"^\*\*([^*]+?):?\*\*:?\s*", texto)
        if rotulo:
            item[nome + "_rotulo"] = rotulo.group(1).rstrip(":")
            texto = texto[rotulo.end():]
        item[nome] = md_html(texto)
        item[nome + "_txt"] = plano(texto)
    usa = re.search(r"\((?:usam|popularizado)[^)]*\)", item.get("objecao_txt", ""))
    item["usam"] = usa.group(0)[1:-1] if usa else ""
    itens.append(item)

assert len(itens) == 100, len(itens)

cola = re.search(r"## Cola rápida\n(.*?)\n---", MD, re.S).group(1)
cola_html = md_html(cola)
como = re.search(r"## Como usar este guia\n(.*?)\n---", MD, re.S).group(1)
como_html = md_html(como)
leituras = re.search(r"## Para aprofundar\n(.*?)\n> ", MD, re.S).group(1)
leituras_html = md_html(leituras)

dados = {"itens": itens, "partes": {k: v[0] for k, v in PARTES.items()},
         "cola": cola_html, "como": como_html, "leituras": leituras_html,
         "islam": estudos_islam}

# Formato padrão legível por outras ferramentas
(DIR / "objecoes.json").write_text(json.dumps(
    [{k: v for k, v in i.items() if k.endswith("_txt") or k in ("n", "titulo", "parte", "tema", "publico", "usam")}
     for i in itens], ensure_ascii=False, indent=1), encoding="utf-8")

tpl = (DIR / "app.template.html").read_text(encoding="utf-8")
(DIR / "app.html").write_text(
    tpl.replace("/*DADOS*/null", json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")),
    encoding="utf-8")
print("ok:", len(itens), "objeções")
