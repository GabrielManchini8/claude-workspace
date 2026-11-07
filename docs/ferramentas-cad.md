# Ferramentas de CAD

## Instaladas neste repositório

| Ferramenta | Para quê | Licença |
|---|---|---|
| [CadQuery](https://github.com/CadQuery/cadquery) 2.8 | Modelagem 3D paramétrica em Python (STEP, STL, DXF, SVG) | Apache-2.0 |
| [build123d](https://github.com/gumyr/build123d) 0.11 | Modelagem 3D em Python, sucessor moderno do CadQuery | Apache-2.0 |
| [draftwright](https://github.com/pzfreo/draftwright) 0.4 | Desenho técnico automático (vistas, cotas, corte, legenda ISO 7200) em PDF/SVG/DXF a partir de build123d ou STEP | AGPL-3.0 |
| [FreeCAD](https://www.freecad.org) 1.0.2 (só na nuvem) | `freecadcmd`: ler/converter STEP, IGES, DXF, IFC; TechDraw; scripts Python | LGPL-2.0+ |

A skill `/draftwright` (em `.claude/skills/draftwright`) ensina o Claude a usar o draftwright.

## Das listas do GitHub (não instaladas, só referência)

Escolhidas em https://github.com/topics/text-to-cad e https://github.com/topics/mechanical-cad
pela utilidade para desenho técnico de produtos:

- [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad): gera peças a partir de texto com IA (Python). O mais popular do tópico.
- [Adam-CAD/CADAM](https://github.com/Adam-CAD/CADAM): app web de texto para CAD.
- [U-C4N/Autocad-MCP](https://github.com/U-C4N/Autocad-MCP): servidor MCP para desenhar e editar DWG/DXF. Útil para editar desenhos 2D existentes.
- [giuliano-t/openAI-to-freeCAD-workflow](https://github.com/giuliano-t/openAI-to-freeCAD-workflow): texto para scripts FreeCAD.
- [capwitf/mechanical-cad-skills](https://github.com/capwitf/mechanical-cad-skills): skills de CAD mecânico e verificação de desenhos.
- [BOMWiki/partmode](https://github.com/BOMWiki/partmode): CAD paramétrico no navegador (OpenCascade WASM).
- [mlightcad/awesome-cad](https://github.com/mlightcad/awesome-cad): lista curada de softwares e bibliotecas de CAD abertos.

**Cuidado:** o tópico mechanical-cad tem repositórios que oferecem Inventor, ANSYS, Enscape e
Autodesk Civil "ativados". São pirataria e costumam trazer malware. Não baixe.
