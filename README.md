# claude-workspace

Base para projetos no Claude Code. Abra uma sessão com este repositório e os plugins e skills carregam sozinhos:

- Watch (`/watch`): assistir vídeos
- Ponytail: código mais simples (sempre ligado; `/ponytail off` desliga)
- Impeccable (`/impeccable`): design de interface
- Remotion (`/remotion-create` e outras): vídeos com React

Cada projeto novo pode ficar numa pasta própria aqui dentro.

## Projetos

- [Apologética Católica](apologetica/apologetica-catolica.md) — app católico de bolso: https://claude.ai/artifact/NMsFZHLvPtHWCD67snnxvs
  - **Defesa da fé:** 100 objeções com versículos (`apologetica-catolica.md`, `objecoes.json`), heresias (`heresias.md`) e outras religiões (`religioes.md`)
  - **Ano litúrgico:** cores, tempos e festas, calculados para a data de hoje (`liturgia.md`)
  - **Na Missa:** o que fazer e o que evitar (`missa.md`)
  - **Terço:** passo a passo interativo, mistérios e orações (`terco.md`) e vídeo (`terco.mp4`, feito em Remotion em `video-terco/`)
  - Fontes extrabíblicas (notas de rodapé): `fontes.py`. A página é gerada por `build.py` a partir de `app.template.html`.
