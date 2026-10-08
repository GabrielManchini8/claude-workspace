import {getLength, getPointAtLength} from '@remotion/paths';
import React, {useMemo} from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const ENERGY = '#c9f3ff';
const TRACE = '#3a8cf0';
const TRAIL = 110;

type Props = {
	/** Curva de 45° da trilha, onde fica uma ilha de solda. */
	bend?: {x: number; y: number};
	/** Trilha que vem da borda da tela até o ponto de entrada da letra. */
	feed: string;
	/** Contornos da letra; o primeiro começa no ponto de entrada. */
	contours: string[];
	fill: string;
	edge: string;
	/** Quadro em que a energia sai da borda. */
	start: number;
	/** Velocidade da energia na trilha (unidades por quadro). */
	speed: number;
	/** Quadros que a energia leva para contornar a letra. */
	outlineFrames: number;
};

// A ilha de solda aparece quando a energia passa pela curva (a trilha é reta até ela).
const isPast = (feed: string, head: number, bend: {x: number; y: number}) => {
	const edgeX = Number(feed.split(' ')[1]);
	return head >= Math.abs(bend.x - edgeX);
};

/**
 * Letra formada por trilhas de placa de circuito: a energia corre pela trilha
 * a partir da borda, chega à letra, contorna-a pelos dois lados e a letra
 * se preenche. Depois a trilha de alimentação se apaga.
 */
export const CircuitLetter: React.FC<Props> = ({bend, feed, contours, fill, edge, start, speed, outlineFrames}) => {
	const frame = useCurrentFrame();
	const feedLen = useMemo(() => getLength(feed), [feed]);
	const lens = useMemo(() => contours.map((c) => getLength(c)), [contours]);

	const feedFrames = feedLen / speed;
	const arrive = start + feedFrames;
	const closed = arrive + outlineFrames;

	const head = interpolate(frame, [start, arrive], [0, feedLen], {...clamp, easing: Easing.in(Easing.sin)});
	const outlineP = interpolate(frame, [arrive, closed], [0, 1], {...clamp, easing: Easing.out(Easing.sin)});
	const fillO = interpolate(frame, [closed - 2, closed + 6], [0, 1], clamp);
	const flash = interpolate(frame, [closed - 1, closed + 2, closed + 12], [0, 1, 0], clamp);
	const feedFade = interpolate(frame, [closed + 4, closed + 26], [1, 0], clamp);
	const glowFade = interpolate(frame, [closed, closed + 14], [1, 0], clamp);

	if (frame < start) return null;

	const feedHead = getPointAtLength(feed, Math.min(head, feedLen - 0.01));
	const L0 = lens[0];
	const ringHeads =
		outlineP > 0 && outlineP < 1
			? [
					getPointAtLength(contours[0], Math.max(0.01, (outlineP * L0) / 2)),
					getPointAtLength(contours[0], Math.min(L0 - 0.01, L0 - (outlineP * L0) / 2)),
				]
			: [];
	const heads = (frame < arrive ? [feedHead] : ringHeads).filter((p): p is {x: number; y: number} => p !== null);

	return (
		<g>
			{/* Trilha de alimentação */}
			<g opacity={feedFade}>
				<path
					d={feed}
					fill="none"
					stroke={TRACE}
					strokeWidth={4.5}
					strokeLinejoin="round"
					strokeDasharray={`${head} ${feedLen * 2}`}
				/>
				<path
					d={feed}
					fill="none"
					stroke={ENERGY}
					strokeWidth={6}
					strokeLinecap="round"
					strokeLinejoin="round"
					strokeDasharray={`0 ${Math.max(0, head - TRAIL)} ${Math.min(head, TRAIL)} ${feedLen * 2}`}
					opacity={frame < arrive ? 1 : 0}
					filter="url(#glow)"
				/>
				{bend && isPast(feed, head, bend) ? (
					<circle cx={bend.x} cy={bend.y} r={6} fill="#ffffff" stroke={TRACE} strokeWidth={3} />
				) : null}
			</g>

			{/* Letra preenchida */}
			<path d={contours.join(' ')} fill={fill} opacity={fillO} stroke={edge} strokeWidth={2.5} strokeLinejoin="round" />

			{/* Contorno sendo traçado pela energia, pelos dois lados */}
			<g opacity={glowFade} filter="url(#glow)">
				{contours.map((c, i) => {
					const L = lens[i];
					const half = (outlineP * L) / 2;
					return (
						<path
							key={i}
							d={c}
							fill="none"
							stroke="#5ab4ff"
							strokeWidth={3.5}
							strokeLinejoin="round"
							strokeDasharray={`${half} ${Math.max(0, L - 2 * half)} ${half} 0`}
						/>
					);
				})}
			</g>
			<path d={contours.join(' ')} fill="none" stroke="#ffffff" strokeWidth={5} opacity={flash * 0.9} filter="url(#glow)" />

			{/* Pontas de energia */}
			{heads.map((p, i) => (
				<g key={i} filter="url(#glow)">
					<circle cx={p.x} cy={p.y} r={14} fill="#7fd0ff" opacity={0.6} />
					<circle cx={p.x} cy={p.y} r={6} fill="#ffffff" />
				</g>
			))}
		</g>
	);
};
