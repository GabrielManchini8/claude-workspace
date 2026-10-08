# Casa E-TEC — animação da logo (Remotion)

Animação de 5 s (1080×1080, 30 fps) da logo Casa E-TEC, recriada em SVG/React.

Sequência:
1. O botão (o ponto da logo) vem do fundo, com rastros de velocidade, e atravessa a tela (0–0,7 s)
2. Ele volta encolhendo como uma íris até o lugar dele e "clica", com ondas de choque (0,7–1,3 s)
3. O clique "liga" a casa: o telhado acende a partir do topo, com faíscas (1,2–1,9 s)
4. O "C" e o "T" são formados por trilhas de circuito: a energia vem da borda esquerda (C) e da direita (T), contorna a letra pelos dois lados e ela se preenche (1,3–2,6 s)
5. As ondas de Wi-Fi se expandem com eco (1,9–3 s)
6. "CASA E-TEC" também nasce de trilhas: "CASA" pela esquerda e "E-TEC" pela direita, cada letra com sua trilha, ilha de solda na curva de 45° e energia correndo até formá-la (2,1–3,5 s)
7. Brilho atravessa a logo, o Wi-Fi pulsa e a câmera flutua em 3D (3,5–5 s)

**Fundo transparente no começo:** até 0,66 s o fundo é transparente: o botão
sai do meio do seu vídeo, com os rastros de velocidade por cima da cena.
Quando ele cobre a tela, o fundo branco entra por trás e a logo se monta.
Para usar num editor, use o arquivo com canal alfa (ProRes 4444 `.mov`, ou WebM).

Durante todo o vídeo: camadas com profundidade (paralaxe), motion blur de câmera,
bokeh ao fundo, vinheta e granulação de filme.

Prévias renderizadas em `render/`: `casa-etec-logo-alpha.webm` (com transparência) e
`preview-sobre-video.mp4` (exemplo sobre um fundo qualquer). O `.mov` ProRes fica
fora do git por ser grande (~180 MB); gere com `npm run render:alpha`.

## Comandos

```bash
npm install
# opcional: usar um Chromium já instalado
# export REMOTION_BROWSER=/caminho/para/chrome-headless-shell
npm run dev          # Remotion Studio para ajustar
npm run render       # out/casa-etec-logo.mp4
npm run render:gif   # out/casa-etec-logo.gif
npm run render:alpha # out/casa-etec-logo-alpha.mov (ProRes 4444 com transparência)
npm run render:webm  # out/casa-etec-logo-alpha.webm (VP9 com transparência)
```

Fonte: Montserrat Black (SIL Open Font License), em `assets/`. Os contornos das letras
e as trilhas do texto ficam em `src/glyphs.json`, gerado por `node scripts/gen-glyphs.mjs`
(rode de novo se mudar o texto, o tamanho ou as faixas das trilhas).
