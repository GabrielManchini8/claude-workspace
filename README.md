# claude-workspace

Base para projetos no Claude Code. Abra uma sessão com este repositório e os plugins e skills carregam sozinhos:

- Watch (`/watch`): assistir vídeos
- watch-video (`/watch-video`): assistir vídeos e gerar notas em markdown
- Ponytail: código mais simples (sempre ligado; `/ponytail off` desliga)
- Impeccable (`/impeccable`): design de interface
- Remotion (`/remotion-create` e outras): vídeos com React

Cada projeto novo pode ficar numa pasta própria aqui dentro.

## Rabisco (app/)
```bash
cd app && npm install && cp .env.example .env   # Supabase opcional
npm run dev
```
Mapa mental: **Tab** = filho, **Enter** = irmão, **Espaço** = expandir/recolher, **Delete** = apaga ramo.
Caneta: ao tocar com a caneta o app entra em modo caneta (dedo navega, caneta desenha).
Veja `docs/ROADMAP.md` e `supabase/migrations/`.
