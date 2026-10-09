"""Fontes extrabíblicas citadas no guia (notas de rodapé) e onde inseri-las.

Uso único: python3 fontes.py  → insere [^id] no .md e escreve a seção "Fontes".
Rodar de novo não duplica marcas.
"""
import re
from pathlib import Path

FONTES = {
    # Padres e escritos antigos
    "didaque": "*Didaqué* (Doutrina dos Doze Apóstolos), c. 70–100 d.C. Sobre o aborto: 2,2. Sobre o batismo por infusão: 7,1-3.",
    "inacio": "Santo Inácio de Antioquia, *Carta aos Esmirnenses* 8,2 (c. 107 d.C.): \"onde está Jesus Cristo, aí está a Igreja católica\". Primeiro uso conhecido da expressão.",
    "pedro-roma": "Pedro em Roma: São Clemente de Roma, *1ª Carta aos Coríntios* 5 (c. 96); Santo Inácio, *Carta aos Romanos* 4,3 (c. 107); Santo Irineu, *Contra as Heresias* III,1,1 e III,3,2 (c. 180); Tertuliano, *A Prescrição dos Hereges* 36 (c. 200); Eusébio de Cesareia, *História Eclesiástica* II,25 (c. 325).",
    "escavacoes": "Escavações sob a Basílica de São Pedro (1939–1949), autorizadas por Pio XII. Em 26/06/1968, Paulo VI anunciou a identificação das relíquias de Pedro.",
    "jeronimo": "São Jerônimo, *Comentário a Isaías*, Prólogo (c. 408). Citado em Dei Verbum 25 e CIC 133.",
    "efeso": "Concílio de Éfeso (431), que proclamou Maria *Theotokos* (Mãe de Deus) contra Nestório.",
    "niceia": "Concílio de Niceia (325), que definiu que o Filho é \"consubstancial ao Pai\" (Credo Niceno).",
    "edito": "Édito de Milão (313), de Constantino e Licínio, que deu liberdade de culto aos cristãos. O cristianismo só virou religião oficial com o Édito de Tessalônica (380), de Teodósio.",
    # Cânon e Reforma
    "canon": "Lista dos livros da Bíblia: Concílio de Roma (382, atribuído ao Papa Dâmaso), Hipona (393), III de Cartago (397), Florença (1442, bula *Cantate Domino*), Trento (1546, sessão IV, decreto *Sacrosancta*).",
    "lutero-allein": "Martinho Lutero, Novo Testamento em alemão (1522), Rm 3,28: \"allein durch den Glauben\" (somente pela fé). Ele defende o acréscimo na *Carta aberta sobre a tradução* (*Sendbrief vom Dolmetschen*, 1530).",
    "lutero-palha": "Martinho Lutero, Prefácio ao Novo Testamento (1522), que chama Tiago de \"epístola de palha\" (*eine rechte stroherne Epistel*), e seus prefácios a Hebreus, Tiago, Judas e Apocalipse.",
    "trento": "Concílio de Trento, sessão XXI (1562), decreto de reforma, cap. 9 (abolição dos \"coletores de esmolas\" ligados às indulgências); sessão XXV (1563), *Decreto sobre as indulgências*.",
    "alemao": "Antes de Lutero havia 14 edições impressas da Bíblia em alto-alemão (a primeira é a Bíblia de Mentelin, Estrasburgo, 1466) e 4 em baixo-alemão.",
    "gutenberg": "Bíblia de Gutenberg (Mogúncia, c. 1455): a Vulgata latina, primeiro grande livro impresso com tipos móveis.",
    "darby": "John Nelson Darby (1800–1882), dos Irmãos de Plymouth. A ideia foi popularizada pela *Bíblia de Referência Scofield* (1909).",
    "lambeth": "Conferência de Lambeth (Comunhão Anglicana), 1930, resolução 15: primeira igreja cristã a admitir a contracepção.",
    "reformadores": "Lutero, *Comentário ao Gênesis* (sobre Gn 38); João Calvino, *Comentário ao Gênesis* (sobre Gn 38,9-10).",
    # Magistério
    "dv": "Concílio Vaticano II, Constituição dogmática *Dei Verbum* (DV), sobre a Revelação divina (18/11/1965). Texto integral em vatican.va.",
    "lg": "Concílio Vaticano II, Constituição dogmática *Lumen Gentium* (LG), sobre a Igreja (21/11/1964), n. 16. Texto integral em vatican.va.",
    "na": "Concílio Vaticano II, Declaração *Nostra Aetate* (NA), sobre as religiões não cristãs (28/10/1965), n. 2-3. Texto integral em vatican.va.",
    "sc": "Concílio Vaticano II, Constituição *Sacrosanctum Concilium* (SC), sobre a liturgia (04/12/1963), n. 36 e 54. Texto integral em vatican.va.",
    "vat1": "Concílio Vaticano I, Constituição dogmática *Pastor Aeternus* (18/07/1870), cap. 4: definição da infalibilidade papal.",
    "const3": "III Concílio de Constantinopla (680–681), sessões XIII e XVI. O Papa Leão II, ao confirmá-lo, explicou que Honório foi condenado por não ter combatido a heresia.",
    "hv": "São Paulo VI, encíclica *Humanae Vitae* (HV), sobre a regulação da natalidade (25/07/1968). Texto integral em vatican.va.",
    "os": "São João Paulo II, carta apostólica *Ordinatio Sacerdotalis* (22/05/1994), n. 4. Texto integral em vatican.va.",
    "humani": "Pio XII, encíclica *Humani Generis* (1950), n. 36; São João Paulo II, Mensagem à Pontifícia Academia das Ciências sobre a evolução (22/10/1996).",
    "galileu": "São João Paulo II, discurso à Pontifícia Academia das Ciências sobre o caso Galileu (31/10/1992).",
    "sublimis": "Paulo III, bula *Sublimis Deus* (1537), contra a escravização dos indígenas; Gregório XVI, carta apostólica *In supremo apostolatus* (1839), contra o tráfico de escravos.",
    "cti": "Comissão Teológica Internacional, *A esperança da salvação para as crianças que morrem sem batismo* (19/04/2007).",
    "mpf": "Dicastério para a Doutrina da Fé, nota doutrinal *Mater Populi Fidelis*, sobre títulos marianos ligados à cooperação de Maria na salvação (novembro de 2025).",
    "pena2018": "Papa Francisco, Rescrito de 02/08/2018 (Congregação para a Doutrina da Fé), com a nova redação do CIC 2267.",
    "regensburg": "Bento XVI, discurso *Fé, razão e universidade* (Universidade de Regensburg, 12/09/2006), citando Manuel II Paleólogo, *Diálogos com um persa*, VII (1391). Texto integral em vatican.va.",
    # São Tomás e autores sobre o Islã
    "st": "São Tomás de Aquino, *Suma Teológica* (ST) I, q. 2, a. 3: as Cinco Vias para provar a existência de Deus.",
    "aquino-dr": "São Tomás de Aquino, *De rationibus fidei ad Cantorem Antiochenum* (*Sobre as razões da fé, ao Cantor de Antioquia*), c. 1264, caps. 1-10.",
    "aquino-scg": "São Tomás de Aquino, *Suma contra os Gentios* (SCG), 1259–1265, livro I, caps. 2 e 6. A encomenda de São Raimundo de Penyafort é contada na crônica de Pedro Marsílio (1313).",
    "damasceno": "São João Damasceno, *Sobre as heresias* (*De haeresibus*), cap. 100 (101 em algumas edições), parte da *Fonte do Conhecimento* (c. 730–750).",
    "abuqurrah": "Teodoro Abu Qurrah (c. 750–c. 825), bispo de Harã: tratados em árabe, como o *Tratado sobre a veneração dos ícones*.",
    "pedrov": "Pedro, o Venerável, *Contra sectam Saracenorum* (c. 1155). A tradução latina do Alcorão feita por Roberto de Ketton (1143) integra a chamada *Coleção Toledana*.",
    "francisco": "Encontro de São Francisco com o sultão al-Kamil (Damieta, 1219): São Boaventura, *Legenda Maior* IX,8; testemunho de Jacques de Vitry (carta de 1220).",
    "lulio": "Ramon Llull, *Llibre del gentil e dels tres savis* (*Livro do gentio e dos três sábios*), c. 1274–1276.",
    "ricoldo": "Ricoldo da Monte Croce, *Contra legem Sarracenorum* (c. 1300). Tradução alemã de Lutero: *Verlegung des Alcoran* (1542).",
    "cusa": "Nicolau de Cusa, *Cribratio Alkorani* (1461).",
    "samir": "Samir Khalil Samir, *111 Questions on Islam* (Ignatius Press, 2008).",
    "qureshi": "Nabeel Qureshi, *Seeking Allah, Finding Jesus* (Zondervan, 2014). Autor protestante, ex-muçulmano.",
    "alcorao": "Alcorão, citado como \"Q sura,versículo\" (numeração do Cairo, 1924). Tradução de referência em português: Helmi Nasr, *Tradução do sentido do Nobre Alcorão* (Complexo do Rei Fahd).",
    # História, ciência e outros
    "tacito": "Tácito, *Anais* XV,44 (c. 116 d.C.): \"Cristo, que no reinado de Tibério foi condenado ao suplício pelo procurador Pôncio Pilatos\".",
    "josefo": "Flávio Josefo, *Antiguidades Judaicas* XVIII,3,3 e XX,9,1 (c. 93 d.C.).",
    "plinio": "Plínio, o Jovem, *Cartas* X,96, ao imperador Trajano (c. 112 d.C.).",
    "talmude": "Talmude Babilônico, *Sanhedrin* 43a: \"na véspera da Páscoa, suspenderam Yeshu\".",
    "historiadores": "Bart D. Ehrman, *Did Jesus Exist?* (2012); John Dominic Crossan, *Jesus: A Revolutionary Biography* (1994). Os dois são críticos do cristianismo tradicional.",
    "manuscritos": "Codex Sinaiticus e Codex Vaticanus (séc. IV); Papiro P52 (John Rylands Library, c. 125–150 d.C., com Jo 18,31-33.37-38); Grande Rolo de Isaías de Qumrã (1QIsaª, c. 125 a.C.). A contagem de cerca de 5.800 manuscritos gregos é do Instituto de Pesquisa do Texto do NT (Münster).",
    "tell": "Inscrição funerária judaica de Arsinoé, Tell el-Yehudieh (Egito), datada de 5 a.C.",
    "lemaitre": "Georges Lemaître, \"Un Univers homogène de masse constante et de rayon croissant\" (1927) e a hipótese do \"átomo primordial\" (1931).",
    "lourdes": "Comitê Médico Internacional de Lourdes (CMIL). O 70º milagre reconhecido pela Igreja foi o da Ir. Bernadette Moriau (2018).",
    "wars": "Charles Phillips e Alan Axelrod, *Encyclopedia of Wars* (Facts on File, 2004), 3 vols.: 123 de 1.763 conflitos classificados como principalmente religiosos.",
    "massey": "Gerald Massey, *The Natural Genesis* (1883) e *Ancient Egypt: The Light of the World* (1907); Kersey Graves, *The World's Sixteen Crucified Saviors* (1875); filme *Zeitgeist* (2007).",
    "lewis": "C. S. Lewis, *Cristianismo puro e simples* (*Mere Christianity*, 1952), livro II, cap. 3.",
}

# (expressão regular, id): marca inserida logo após o primeiro trecho encontrado em cada objeção
REGRAS = [
    (r"Didaqué", "didaque"),
    (r"Esmirnenses\* 8,2", "inacio"),
    (r"Clemente de Roma", "pedro-roma"),
    (r"Escavações", "escavacoes"),
    (r"São Jerônimo", "jeronimo"),
    (r"Éfeso, 431", "efeso"),
    (r"Concílio de Niceia", "niceia"),
    (r"Édito de Milão, 313", "edito"),
    (r"Hipona", "canon"),
    (r"\(\*allein\*\)", "lutero-allein"),
    (r"epístola de palha\"", "lutero-palha"),
    (r"Concílio de Trento \(1562\)", "trento"),
    (r"baixo-alemão", "alemao"),
    (r"\(c\. 1455\)", "gutenberg"),
    (r"J\. N\. Darby\)", "darby"),
    (r"Lambeth\)", "lambeth"),
    (r"Lutero e Calvino também a condenavam", "reformadores"),
    (r"Dei Verbum", "dv"),
    (r"Lumen Gentium", "lg"),
    (r"Nostra Aetate", "na"),
    (r"Sacrosanctum Concilium", "sc"),
    (r"Pastor Aeternus\*", "vat1"),
    (r"Concílio de Constantinopla \(681\)", "const3"),
    (r"Humanae Vitae\*", "hv"),
    (r"Ordinatio Sacerdotalis\*", "os"),
    (r"Humani Generis\*, 1950", "humani"),
    (r"erros \(1992\)", "galileu"),
    (r"Sublimis Deus\*, 1537", "sublimis"),
    (r"Comissão Teológica Internacional \(2007\)", "cti"),
    (r"Mater Populi Fidelis\*", "mpf"),
    (r"revisou o CIC 2267", "pena2018"),
    (r"Regensburg", "regensburg"),
    (r"Suma Teológica\* I, q\. 2, a\. 3", "st"),
    (r"De rationibus fidei\*+", "aquino-dr"),
    (r"Suma contra os Gentios\*+", "aquino-scg"),
    (r"Sobre as heresias\*, cap\. 100", "damasceno"),
    (r"Tratados em \*\*árabe\*\*", "abuqurrah"),
    (r"Contra a seita dos sarracenos\*", "pedrov"),
    (r"\*\*al-Kamil\*\*", "francisco"),
    (r"Livro do gentio e dos três sábios\*", "lulio"),
    (r"Contra a lei dos sarracenos\*", "ricoldo"),
    (r"Peneirando o Alcorão\*\)", "cusa"),
    (r"\*111 Questions on Islam\*", "samir"),
    (r"Seeking Allah, Finding Jesus\*", "qureshi"),
    (r"\bQ \d+,\d+", "alcorao"),
    (r"Tácito", "tacito"),
    (r"Josefo", "josefo"),
    (r"Plínio, o Jovem", "plinio"),
    (r"Talmude", "talmude"),
    (r"Ehrman", "historiadores"),
    (r"Qumrã|Codex Sinaiticus", "manuscritos"),
    (r"Tell el-Yehudieh \(5 a\.C\.\)", "tell"),
    (r"Lemaître", "lemaitre"),
    (r"cerca de 70 como milagrosas", "lourdes"),
    (r"Phillips e Axelrod, 2004\)", "wars"),
    (r"Kersey Graves\)", "massey"),
    (r"trilema de C\. S\. Lewis\)", "lewis"),
]

if __name__ == "__main__":
    p = Path(__file__).parent / "apologetica-catolica.md"
    md = p.read_text(encoding="utf-8")
    md = re.sub(r"\n## Fontes das citações\n.*", "\n", md, flags=re.S).rstrip() + "\n"
    # Só até a cola rápida (a tabela final fica sem notas)
    corte = md.index("## Cola rápida")
    corpo, resto = md[:corte], md[corte:]
    blocos = re.split(r"(?=^### \d+\. |^## Existem estudos|^# PARTE )", corpo, flags=re.M)
    usados = set()
    for k, b in enumerate(blocos):
        for rx, fid in REGRAS:
            if f"[^{fid}]" in b:
                usados.add(fid)
                continue
            m = re.search(rx, b)
            if m:
                b = b[:m.end()] + f"[^{fid}]" + b[m.end():]
                usados.add(fid)
        blocos[k] = b
    md = "".join(blocos) + resto
    faltam = set(FONTES) - usados
    assert not faltam, f"fontes sem marca no texto: {faltam}"
    md += "\n## Fontes das citações\n\nFontes de tudo o que é citado fora da Bíblia (os números aparecem como notas no texto).\n\n"
    md += "\n".join(f"[^{k}]: {v}" for k, v in FONTES.items()) + "\n"
    p.write_text(md, encoding="utf-8")
    print("marcas:", sum(md.count(f"[^{k}]") - 1 for k in FONTES), "fontes:", len(FONTES))
