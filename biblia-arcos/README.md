# Bíblia Católica em Arcos

Gráfico de arcos das referências cruzadas da Bíblia no cânon católico (73 livros, ordem do CIC 120),
inspirado no trabalho de Chris Harrison e Christoph Römhild.

- `prep.py`: agrega as referências versículo a versículo do OpenBible.info em pares de capítulos.
  Uso: `python3 prep.py <clone de scrollmapper/bible_databases> data.json`
  (precisa de `sources/extras/cross_references.txt`, `formats/csv/KJV.csv` e `formats/csv/CPDV.csv`).
- `deutero.json`: 66 ligações deuterocanônicas escolhidas à mão (não oficiais).
- `prep_atlas.py`: monta pessoas, famílias, lugares, viagens e menções por capítulo a partir do
  [Theographic Bible Metadata](https://github.com/robertrouse/theographic-bible-metadata) (CC BY-SA 4.0).
  Uso: `python3 prep_atlas.py <clone do theographic> data.json names_pt.json land.json atlas.json`
- `land.js`: recorta o litoral do Natural Earth (`world-atlas@2.0.2`, `topojson-client@3.1.0`) em `land.json`.
- `names_pt.json`: nomes em português das pessoas e lugares mais citados.
- `template.html`: a página; `__DATA__`, `__DEUT__` e `__ATLAS__` são substituídos pelos JSON.
- `biblia-catolica-arcos.html`: a página já montada.

Dados: OpenBible.info, CC BY. As referências vêm do *Treasury of Scripture Knowledge* e não incluem os deuterocanônicos.
