# claude-workspace

Base para projetos no Claude Code. Abra uma sessão com este repositório e os plugins e skills carregam sozinhos:

- Watch (`/watch`): assistir vídeos
- watch-video (`/watch-video`): assistir vídeos e gerar notas em markdown
- Ponytail: código mais simples (sempre ligado; `/ponytail off` desliga)
- Impeccable (`/impeccable`): design de interface
- Remotion (`/remotion-create` e outras): vídeos com React

Cada projeto novo pode ficar numa pasta própria aqui dentro.

## Desenho técnico (CAD)

Ferramentas para modelar peças e gerar desenhos técnicos, todas rodando na nuvem do Claude Code (nada é instalado na sua máquina). Lista completa e links em [docs/ferramentas-cad.md](docs/ferramentas-cad.md).

Preparar o ambiente (uma vez por sessão):

```bash
scripts/setup-cad.sh            # CadQuery, build123d e draftwright em .venv-cad
scripts/setup-cad.sh --freecad  # também o FreeCAD 1.0.2 sem interface (~800 MB, ~1 min)
```

Testar:

```bash
.venv-cad/bin/python cad/exemplos/flange.py     # modelo 3D + desenho em cad/saida/
.venv-cad/bin/draftwright cad/saida/flange.step --title "FLANGE DN50" --number AGEL-001 \
  --format pdf,dxf --out cad/saida/flange        # desenho a partir de qualquer STEP
freecadcmd cad/exemplos/freecad_step_info.py    # FreeCAD lendo o STEP
```

Use sempre `--out` no CLI do draftwright: sem ele, a versão 0.4 grava na pasta atual.

Bibliotecas de conexões (Tigre, Amanco, pipestd): veja [bibliotecas/README.md](bibliotecas/README.md).
