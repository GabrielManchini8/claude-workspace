# Casa E-TEC — animação da logo (Remotion)

Animação de 5 s (1080×1080, 30 fps) da logo Casa E-TEC, recriada em SVG/React.

Sequência:
1. O botão (o ponto da logo) vem do fundo, com rastros de velocidade, e atravessa a tela (0–0,7 s)
2. Ele volta encolhendo como uma íris até o lugar dele e "clica", com ondas de choque (0,7–1,3 s)
3. O clique "liga" a casa: o telhado acende a partir do topo, com faíscas (1,2–1,9 s)
4. O "C" e o "T" emergem da profundidade girando, com trilhas de circuito (1,4–2,5 s)
5. As ondas de Wi-Fi se expandem com eco (1,9–3 s)
6. "CASA E-TEC" vira para cima letra por letra e o espaçamento se fecha (2,6–3,8 s)
7. Brilho atravessa a logo, o Wi-Fi pulsa e a câmera flutua em 3D (3,5–5 s)

Durante todo o vídeo: camadas com profundidade (paralaxe), motion blur de câmera,
bokeh ao fundo, vinheta e granulação de filme.

Prévias renderizadas: `render/casa-etec-logo.mp4` e `render/casa-etec-logo.gif`.

## Comandos

```bash
npm install
# opcional: usar um Chromium já instalado
# export REMOTION_BROWSER=/caminho/para/chrome-headless-shell
npm run dev          # Remotion Studio para ajustar
npm run render       # out/casa-etec-logo.mp4
npm run render:gif   # out/casa-etec-logo.gif
```

Fonte: Montserrat Black (SIL Open Font License), incluída em `public/`.
