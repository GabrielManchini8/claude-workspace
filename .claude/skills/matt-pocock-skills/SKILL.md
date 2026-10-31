---
name: matt-pocock-skills
description: "Varre o código procurando hot spots e falhas de design (acoplamento, módulos rasos, tipos fracos). Use quando: Ao refatorar ou reestruturar sistemas legados."
disable-model-invocation: true
---

# matt-pocock-skills (Programação)

Varre o código procurando hot spots e falhas de design (acoplamento, módulos rasos, tipos fracos).

## Como fazer
1. Mapeie os módulos e as dependências entre eles.
2. Aponte hot spots: arquivos grandes, muito alterados ou muito acoplados.
3. Para cada um, proponha uma interface mais profunda e simples, com o trade-off.
4. Não refatore sem aprovação; evite abstração desnecessária.

## Não fazer
- Aplicar em código que deve continuar simples (overengineering).

## Quando usar
- Ao refatorar ou reestruturar sistemas legados.
