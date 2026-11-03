---
name: nova-skill
description: Cria uma skill nova em .claude/skills a partir de um fluxo que o usuário repete ou pede. Use quando o usuário disser "/nova-skill", "transforma isso numa skill", ou quando o loop de aprendizado detectar um pedido repetido.
---

# Nova skill

1. Confirme com o usuário **o fluxo** a automatizar e **quando** ele deve disparar.
2. Veja `memoria/` e as skills existentes em `.claude/skills/` para não duplicar e para usar as preferências dele.
3. Crie `.claude/skills/<nome-kebab>/SKILL.md`:
   - frontmatter com `name` e `description` (a descrição diz *o que faz* e *quando usar*, com frases que o usuário falaria);
   - passos curtos e verificáveis, no estilo do usuário;
   - arquivos de apoio (exemplos, scripts) só se necessários.
4. Registre em `memoria/aprendizados.md`: `- [skill] criada /<nome> para <fluxo>. (data)`.
5. Commit: `skill: adiciona /<nome>` e envie para a branch atual.
6. Diga ao usuário como chamá-la.
