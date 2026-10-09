import React from "react";
import { COR } from "./estilo";

// Ordem das contas ao rezar: cruz, Pai-Nosso, 3 Ave-Marias, Glória/Pai-Nosso, 5 dezenas no círculo, medalha
export const ORDEM: string[] = ["cruz", "p1", "a0", "a1", "a2", "p2", ...Array.from({ length: 54 }, (_, i) => `l${i}`), "medalha"];

const C = 150, R = 118;
const POS: Record<string, [number, number, number]> = (() => {
  const p: Record<string, [number, number, number]> = {};
  const gap = (14 * Math.PI) / 180, a0 = Math.PI / 2 + gap, a1 = Math.PI / 2 + 2 * Math.PI - gap;
  for (let i = 0; i < 54; i++) {
    const a = a0 + ((a1 - a0) * i) / 53;
    p[`l${i}`] = [C + R * Math.cos(a), C + R * Math.sin(a), i % 11 === 10 ? 9 : 6.3];
  }
  p.medalha = [150, 274, 11];
  p.p2 = [150, 302, 9];
  [0, 1, 2].forEach((i) => (p[`a${i}`] = [150, 324 + i * 19, 6.3]));
  p.p1 = [150, 389, 9];
  return p;
})();

type Props = {
  readonly largura: number;
  readonly ativo?: number; // índice em ORDEM da conta atual (-1 = nenhuma)
  readonly visiveis?: number; // quantas contas já foram "desenhadas" (para a animação de entrada)
};

export const Terco: React.FC<Props> = ({ largura, ativo = -1, visiveis = ORDEM.length }) => {
  const estado = (k: string) => {
    const i = ORDEM.indexOf(k);
    if (i === ativo) return "atual";
    if (i < ativo) return "feita";
    return "livre";
  };
  const visivel = (k: string) => ORDEM.indexOf(k) < visiveis;
  const fill = (e: string) => (e === "atual" ? COR.ouro : e === "feita" ? COR.azul : COR.painel);
  const cruz = estado("cruz");
  return (
    <svg width={largura} height={(largura * 450) / 300} viewBox="0 0 300 450">
      <circle cx={C} cy={C} r={R} fill="none" stroke={COR.linha} strokeWidth={1.6} />
      <path d="M150 262V408" stroke={COR.linha} strokeWidth={1.6} />
      {Object.entries(POS).map(([k, [x, y, r]]) => {
        if (!visivel(k)) return null;
        const e = estado(k);
        return (
          <g key={k}>
            {e === "atual" ? <circle cx={x} cy={y} r={r + 8} fill={COR.ouro} opacity={0.25} /> : null}
            <circle cx={x} cy={y} r={r} fill={fill(e)} stroke={e === "livre" ? COR.suave : COR.texto} strokeWidth={1.4} />
            {k === "medalha" ? (
              <text x={x} y={y + 4} textAnchor="middle" fontSize={11} fontWeight={700} fill={e === "livre" ? COR.texto : COR.fundo}>M</text>
            ) : null}
          </g>
        );
      })}
      {visivel("cruz") ? (
        <g>
          {cruz === "atual" ? <circle cx={150} cy={424} r={26} fill={COR.ouro} opacity={0.25} /> : null}
          <path d="M150 404v40M138 416h24" stroke={cruz === "livre" ? COR.suave : cruz === "atual" ? COR.ouro : COR.azul} strokeWidth={6} strokeLinecap="round" />
        </g>
      ) : null}
    </svg>
  );
};
