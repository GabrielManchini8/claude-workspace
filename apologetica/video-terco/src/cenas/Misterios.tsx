import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { COR, entra, Icone, sai, Tela, TITULO } from "../estilo";

const GRUPOS: [string, string, string, string][] = [
  ["Gozosos", "Segunda e sábado", "estrela", COR.branco],
  ["Luminosos", "Quinta-feira", "luz", COR.ouro],
  ["Dolorosos", "Terça e sexta", "cruz", COR.vermelho],
  ["Gloriosos", "Quarta e domingo", "coroa", COR.azul],
];

export const Misterios: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <Tela style={{ gap: 44, opacity: sai(frame, durationInFrames) }}>
      <div style={{ fontFamily: TITULO, fontSize: 84, textAlign: "center", lineHeight: 1.15, ...entra(frame, 0) }}>Os mistérios<br />de cada dia</div>
      {GRUPOS.map(([nome, dias, ico, cor], i) => (
        <div key={nome} style={{ width: "100%", display: "flex", gap: 36, alignItems: "center", background: COR.painel, borderRadius: 32, padding: "34px 40px", borderLeft: `14px solid ${cor}`, ...entra(frame, Math.round((0.7 + i * 1.4) * fps)) }}>
          <Icone nome={ico} tam={96} cor={cor} />
          <div>
            <div style={{ fontSize: 60, fontWeight: 700 }}>Mistérios {nome}</div>
            <div style={{ fontSize: 46, color: COR.suave }}>{dias}</div>
          </div>
        </div>
      ))}
    </Tela>
  );
};
