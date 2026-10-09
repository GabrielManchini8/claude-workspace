import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COR, entra, sai, Tela, TITULO } from "../estilo";
import { ORDEM, Terco } from "../Terco";

// [quadro inicial, título, detalhe, conta inicial, conta final (anima entre elas)]
const PASSOS: [number, string, string, string, string][] = [
  [0, "Na cruz", "Faça o sinal da cruz e reze o Creio", "cruz", "cruz"],
  [120, "Pai-Nosso", "Na primeira conta grande", "p1", "p1"],
  [210, "3 Ave-Marias", "Pela fé, pela esperança e pela caridade", "a0", "a2"],
  [330, "Glória ao Pai", "Anuncie o 1º mistério e reze o Pai-Nosso", "p2", "p2"],
  [440, "10 Ave-Marias", "Meditando a cena do mistério", "l0", "l9"],
  [620, "Glória · Ó meu Jesus", "Depois, anuncie o próximo mistério e reze o Pai-Nosso", "l10", "l10"],
  [720, "Repita nas 5 dezenas", "Cada dezena é um mistério da vida de Jesus", "l11", "l53"],
  [860, "Salve-Rainha", "Na medalha, para encerrar. Amém!", "medalha", "medalha"],
];

export const PassoAPasso: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const idx = PASSOS.reduce((acc, p, i) => (frame >= p[0] ? i : acc), 0);
  const [de, titulo, detalhe, c0, c1] = PASSOS[idx];
  const ate = idx + 1 < PASSOS.length ? PASSOS[idx + 1][0] : durationInFrames;
  const i0 = ORDEM.indexOf(c0), i1 = ORDEM.indexOf(c1);
  const ativo = Math.round(interpolate(frame, [de + 10, ate - 20], [i0, i1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  return (
    <Tela style={{ gap: 48, opacity: sai(frame, durationInFrames) }}>
      <div style={{ fontFamily: TITULO, fontSize: 80, ...entra(frame, 0) }}>Passo a passo</div>
      <Terco largura={600} ativo={ativo} />
      <div key={idx} style={{ width: "100%", background: COR.painel, border: `2px solid ${COR.linha}`, borderRadius: 32, padding: "40px 48px", ...entra(frame, de, 12) }}>
        <div style={{ fontSize: 34, color: COR.ouro, fontWeight: 700, letterSpacing: 3 }}>PASSO {idx + 1} DE {PASSOS.length}</div>
        <div style={{ fontFamily: TITULO, fontSize: 76, marginTop: 10, lineHeight: 1.1 }}>{titulo}</div>
        <div style={{ fontSize: 46, color: COR.suave, marginTop: 14, lineHeight: 1.3 }}>{detalhe}</div>
      </div>
    </Tela>
  );
};
