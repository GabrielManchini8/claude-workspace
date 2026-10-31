---
name: icc-integration
description: "Prevê conflitos entre branches antes que quebrem. Use quando: Times integrando mudanças complexas e paralelas."
disable-model-invocation: true
---

# icc-integration (Programação)

Prevê conflitos entre branches antes que quebrem.

## Como fazer
1. Liste branches ativos e faça `git fetch`.
2. Para cada par relevante, rode `git merge-tree` ou compare arquivos tocados (`git diff --name-only base...branch`).
3. Reporte arquivos e funções com sobreposição e o risco de cada um.
4. Sugira ordem de merge e rebase.

## Não fazer
- Deixar ligado para edições simples e isoladas.

## Quando usar
- Times integrando mudanças complexas e paralelas.
