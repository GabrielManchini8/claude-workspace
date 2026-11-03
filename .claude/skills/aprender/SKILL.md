---
name: aprender
description: Reflete sobre a sessão atual e atualiza a memória do usuário em memoria/*.md (perfil, preferências, projetos, aprendizados). Use ao fim de uma tarefa relevante, quando o usuário corrigir um comportamento, ou quando ele disser "/aprender", "lembra disso", "salva isso".
---

# Aprender

Feche o loop de aprendizado desta sessão.

1. Releia a conversa e liste os **sinais**:
   - correções e reclamações do usuário (mais valiosos);
   - aprovações ("perfeito", "isso");
   - preferências de estilo, ferramentas, idioma, formato;
   - decisões e estado de projetos;
   - pedidos repetidos (candidatos a skill).
2. Leia os quatro arquivos em `memoria/`.
3. Para cada sinal, decida: **novo**, **reforça** (não duplique), **contradiz** (substitua a linha antiga) ou **descartar** (pontual demais).
4. Edite os arquivos certos — um fato por linha, com data. Sem segredos.
5. Se viu um pedido repetido, sugira `/nova-skill` ao usuário (não crie sem ele aprovar).
6. Mostre ao usuário um resumo curto: o que foi adicionado, alterado e removido.
7. Faça commit só dos arquivos de memória: `memoria: <resumo>` e envie para a branch atual.

Se não houver nada novo que valha guardar, diga isso e não altere nada.
