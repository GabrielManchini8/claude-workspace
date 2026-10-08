# Bíblia Católica em Arcos

Gráfico de arcos das referências cruzadas da Bíblia no cânon católico (73 livros, ordem do CIC 120),
inspirado no trabalho de Chris Harrison e Christoph Römhild.

- `prep.py`: agrega as referências versículo a versículo do OpenBible.info em pares de capítulos.
  Uso: `python3 prep.py <clone de scrollmapper/bible_databases> data.json`
  (precisa de `sources/extras/cross_references.txt`, `formats/csv/KJV.csv` e `formats/csv/CPDV.csv`).
- `deutero.json`: 66 ligações deuterocanônicas escolhidas à mão (não oficiais).
- `template.html`: a página; `__DATA__` e `__DEUT__` são substituídos pelo JSON.
- `biblia-catolica-arcos.html`: a página já montada.

Dados: OpenBible.info, CC BY. As referências vêm do *Treasury of Scripture Knowledge* e não incluem os deuterocanônicos.
