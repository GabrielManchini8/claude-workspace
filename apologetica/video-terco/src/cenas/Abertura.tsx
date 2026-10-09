import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COR, entra, sai, Tela, TITULO } from "../estilo";
import { ORDEM, Terco } from "../Terco";

export const Abertura: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Tela style={{ justifyContent: "center", gap: 60, opacity: sai(frame, durationInFrames) }}>
      <Terco largura={460} visiveis={Math.round(interpolate(frame, [0, 70], [0, ORDEM.length], { extrapolateRight: "clamp" }))} />
      <div style={{ textAlign: "center", ...entra(frame, 40) }}>
        <div style={{ fontFamily: TITULO, fontSize: 104, lineHeight: 1.1, letterSpacing: 2 }}>Como rezar<br />o Terço</div>
        <div style={{ width: 120, height: 4, background: COR.ouro, margin: "36px auto" }} />
        <div style={{ fontSize: 52, color: COR.suave }}>e por que rezar</div>
      </div>
    </Tela>
  );
};
