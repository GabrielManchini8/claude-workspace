import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { COR, entra, sai, Tela, TITULO } from "../estilo";
import { Terco } from "../Terco";

const Bola: React.FC<{ tam: number }> = ({ tam }) => (
  <div style={{ width: tam, height: tam, borderRadius: tam, background: COR.azul, border: `3px solid ${COR.texto}`, flex: "none" }} />
);

export const Mapa: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const linhas: [React.ReactNode, string, string][] = [
    [<div key="c" style={{ fontSize: 64, color: COR.ouro, width: 56, textAlign: "center" }}>✝</div>, "Cruz", "Sinal da cruz e Creio"],
    [<Bola key="g" tam={52} />, "Conta grande", "Pai-Nosso"],
    [<Bola key="p" tam={34} />, "Conta pequena", "Ave-Maria"],
    [<div key="d" style={{ fontSize: 52, fontWeight: 700, color: COR.ouro, width: 56, textAlign: "center" }}>5×</div>, "5 dezenas", "5 mistérios, 10 Ave-Marias cada"],
  ];
  return (
    <Tela style={{ gap: 40, opacity: sai(frame, durationInFrames) }}>
      <div style={{ fontFamily: TITULO, fontSize: 88, ...entra(frame, 0) }}>O mapa do terço</div>
      <div style={entra(frame, 10)}><Terco largura={520} /></div>
      <div style={{ display: "grid", gap: 26, width: "100%" }}>
        {linhas.map(([ico, tit, txt], i) => (
          <div key={tit} style={{ display: "flex", gap: 32, alignItems: "center", ...entra(frame, Math.round((1 + i * 1.3) * fps)) }}>
            <div style={{ width: 64, display: "grid", placeItems: "center" }}>{ico}</div>
            <div style={{ fontSize: 48 }}><b>{tit}</b> <span style={{ color: COR.suave }}>· {txt}</span></div>
          </div>
        ))}
      </div>
    </Tela>
  );
};
