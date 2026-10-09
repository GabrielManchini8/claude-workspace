import "@fontsource/cinzel/600.css";
import "@fontsource/source-sans-3/400.css";
import "@fontsource/source-sans-3/700.css";
import React from "react";
import { continueRender, delayRender, Easing, interpolate } from "remotion";

// Espera as fontes antes de renderizar o primeiro quadro
const espera = delayRender("Carregando fontes");
Promise.all([
  document.fonts.load('600 80px "Cinzel"'),
  document.fonts.load('400 40px "Source Sans 3"'),
  document.fonts.load('700 40px "Source Sans 3"'),
]).then(() => continueRender(espera));

export const COR = {
  fundo: "#0F131A",
  painel: "#161B24",
  linha: "#2A3344",
  texto: "#E9ECF2",
  suave: "#9AA3B4",
  ouro: "#E4B83A",
  azul: "#86ACE6",
  verde: "#1FA34A",
  roxo: "#7B2FBF",
  vermelho: "#E0263B",
  branco: "#FFFFFF",
};
export const TITULO = '"Cinzel", Georgia, serif';
export const TEXTO = '"Source Sans 3", system-ui, sans-serif';

const suave = Easing.bezier(0.16, 1, 0.3, 1);
// Entrada: aparece subindo, a partir do quadro `de`
export const entra = (frame: number, de: number, dur = 18) => ({
  opacity: interpolate(frame, [de, de + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
  translate: interpolate(frame, [de, de + dur], ["0px 40px", "0px 0px"], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: suave,
  }),
});
// Saída: some nos últimos quadros da cena
export const sai = (frame: number, total: number, dur = 12) =>
  interpolate(frame, [total - dur, total], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

export const Tela: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      position: "absolute", inset: 0, background: `radial-gradient(ellipse at 50% 30%, #1A2233 0%, ${COR.fundo} 70%)`,
      color: COR.texto, fontFamily: TEXTO, display: "flex", flexDirection: "column", alignItems: "center",
      padding: "140px 90px", boxSizing: "border-box", ...style,
    }}
  >
    {children}
  </div>
);

// Ícones em linha (24×24)
const PATHS: Record<string, string> = {
  livro: "M4 5c3-1.5 5.5-1.5 8 0v14c-2.5-1.5-5-1.5-8 0zM20 5c-3-1.5-5.5-1.5-8 0v14c2.5-1.5 5-1.5 8 0z",
  olhos: "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 9a3 3 0 1 1 0 6 3 3 0 0 1 0-6z",
  estrela: "m12 3 2.6 5.6 6 .6-4.5 4 1.3 6L12 16.3 6.6 19.2l1.3-6-4.5-4 6-.6z",
  escudo: "M12 3 4.5 6v5.5c0 4.7 3.2 8.2 7.5 9.5 4.3-1.3 7.5-4.8 7.5-9.5V6zM12 8v8M9 11h6",
  cruz: "M12 3v18M6 8h12",
  sol: "M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8zM12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1",
  luz: "M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z",
  coroa: "M4 18h16M4 18 3 8l5 4 4-7 4 7 5-4-1 10",
  estrelaBelem: "M12 2v20M2 12h20M5 5l14 14M19 5 5 19",
};
export const Icone: React.FC<{ nome: string; tam: number; cor: string; largura?: number }> = ({ nome, tam, cor, largura = 1.8 }) => (
  <svg width={tam} height={tam} viewBox="0 0 24 24" fill="none" stroke={cor} strokeWidth={largura} strokeLinecap="round" strokeLinejoin="round">
    <path d={PATHS[nome]} />
  </svg>
);
