---
name: last-30-days
description: "Filtro temporal: só novidades dos últimos 30 dias. Use quando: Commits recentes ou atualizações de pacotes."
disable-model-invocation: true
---

# last-30-days (Pesquisa)

Filtro temporal: só novidades dos últimos 30 dias.

## Como fazer
1. Calcule a data de corte (hoje − 30 dias).
2. Busque apenas conteúdo/commits/releases após a data (`git log --since`, changelogs, notícias).
3. Descarte qualquer coisa anterior e diga isso.
4. Liste por data, mais recente primeiro.

## Não fazer
- Entender o motivo de decisões antigas.

## Quando usar
- Commits recentes ou atualizações de pacotes.
