---
name: headroom
description: "Comprime arquivos grandes (logs, boilerplate) antes de analisar. Use quando: Logs massivos ou boilerplates gigantes."
disable-model-invocation: true
---

# headroom (Gestão)

Comprime arquivos grandes (logs, boilerplate) antes de analisar.

## Como fazer
1. Meça o tamanho (`wc -l`).
2. Deduplique linhas repetidas com contagem (`sort | uniq -c`), mantendo primeira/última ocorrência e timestamps.
3. Analise a versão comprimida.
4. Avise se a repetição em si pode ser a pista do bug.

## Não fazer
- Comprimir arquivos onde o padrão repetitivo é a pista do bug.

## Quando usar
- Logs massivos ou boilerplates gigantes.
