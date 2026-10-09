import React from "react";
import { useCurrentFrame } from "remotion";
import { COR, entra, Tela, TITULO } from "../estilo";
import { Terco } from "../Terco";

export const Final: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Tela style={{ justifyContent: "center", gap: 64 }}>
      <div style={entra(frame, 0)}><Terco largura={300} ativo={60} /></div>
      <div style={{ fontFamily: TITULO, fontSize: 92, textAlign: "center", lineHeight: 1.2, ...entra(frame, 12) }}>
        “Rezem o terço<br />todos os dias”
      </div>
      <div style={{ fontSize: 50, color: COR.ouro, ...entra(frame, 30) }}>Nossa Senhora · Fátima, 1917</div>
      <div style={{ position: "absolute", bottom: 130, fontSize: 40, color: COR.suave, letterSpacing: 2, ...entra(frame, 50) }}>Logos · Apologética Católica</div>
    </Tela>
  );
};
