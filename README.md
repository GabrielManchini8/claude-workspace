# claude-workspace

Base para projetos no Claude Code. Abra uma sessão com este repositório e os plugins e skills carregam sozinhos:

- Watch (`/watch`): assistir vídeos
- Ponytail: código mais simples (sempre ligado; `/ponytail off` desliga)
- Impeccable (`/impeccable`): design de interface
- Remotion (`/remotion-create` e outras): vídeos com React

Cada projeto novo pode ficar numa pasta própria aqui dentro.

## Projetos

- [Apologética Católica](apologetica/apologetica-catolica.md) — 100 objeções (protestantes, morais, ateias e muçulmanas) respondidas com versículos.
  - Página com busca: https://claude.ai/artifact/NMsFZHLvPtHWCD67snnxvs (gerada por `apologetica/build.py`)
  - Dados no formato padrão: `apologetica/objecoes.json`
  - Fontes extrabíblicas (notas de rodapé): `apologetica/fontes.py`
  - Heresias antigas e movimentos de hoje: `apologetica/heresias.md`
