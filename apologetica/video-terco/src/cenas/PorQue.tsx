import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { COR, entra, Icone, sai, Tela, TITULO } from "../estilo";

const ITENS: [string, string, string][] = [
  ["livro", "É o Evangelho resumido", "Cada mistério é uma cena da vida de Jesus."],
  ["olhos", "Olhar Jesus com Maria", "“Maria guardava tudo no coração” (Lc 2,19)."],
  ["estrela", "Pedido de Nossa Senhora", "“Rezem o terço todos os dias” (Fátima, 1917)."],
  ["escudo", "Arma espiritual", "A vitória de Lepanto (1571) foi atribuída ao Rosário."],
];

export const PorQue: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <Tela style={{ gap: 56, opacity: sai(frame, durationInFrames) }}>
      <div style={{ fontFamily: TITULO, fontSize: 92, ...entra(frame, 0) }}>Por que rezar?</div>
      {ITENS.map(([ico, tit, txt], i) => (
        <div key={tit} style={{ display: "flex", gap: 40, alignItems: "center", width: "100%", ...entra(frame, Math.round((0.8 + i * 2.6) * fps)) }}>
          <div style={{ width: 150, height: 150, borderRadius: 75, background: "#1D2A40", display: "grid", placeItems: "center", flex: "none" }}>
            <Icone nome={ico} tam={84} cor={COR.ouro} />
          </div>
          <div>
            <div style={{ fontSize: 58, fontWeight: 700, lineHeight: 1.15 }}>{tit}</div>
            <div style={{ fontSize: 44, color: COR.suave, lineHeight: 1.3, marginTop: 8 }}>{txt}</div>
          </div>
        </div>
      ))}
    </Tela>
  );
};
