# CLAUDE.md

Este workspace tem uma **memória viva** sobre o usuário (Gabriel). Ela é carregada em toda sessão:

@memoria/perfil.md
@memoria/preferencias.md
@memoria/projetos.md
@memoria/aprendizados.md

## Loop de aprendizado (siga sempre)

1. **Antes de agir**: use a memória acima. Ela vale mais que suposições genéricas.
2. **Durante**: repare em sinais — correções ("não, faça assim"), aprovações, padrões repetidos, decisões de projeto, ferramentas usadas.
3. **Ao fim de uma tarefa relevante** (ou quando o usuário corrigir algo): rode `/aprender` para registrar o que mudou. Se o usuário corrigir um comportamento, registre na hora.
4. **Quando um mesmo tipo de pedido aparecer 2–3 vezes**: proponha transformá-lo em skill com `/nova-skill`.
5. Para uma revisão profunda (consolidar, podar, reorganizar a memória), delegue ao agente `curador`.

## Regras da memória

- Português, frases curtas, um fato por linha, com data `(AAAA-MM-DD)`.
- Só registre o que é **estável e útil** em sessões futuras. Nada de detalhes de uma tarefa só.
- Nunca grave segredos, senhas, tokens ou dados pessoais sensíveis.
- Fato novo que contradiz um antigo: **substitua** o antigo, não acumule.
- Mantenha cada arquivo com menos de ~150 linhas; condense quando crescer.
- Mudanças na memória vão para um commit próprio: `memoria: <resumo>`.
