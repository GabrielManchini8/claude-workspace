import {getLength, getPointAtLength} from '@remotion/paths';
import React, {useMemo} from 'react';
import {Easing, interpolate, random, useCurrentFrame} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const ENERGY = '#c9f3ff';
const TRACE = '#3a8cf0';
const TRAIL = 110;

export type InnerTraces = {
	/** Trilhas gravadas dentro da letra (polilinhas com ilhas de solda nas pontas). */
	paths: string[];
	color: string;
	width?: number;
	pad?: number;
};

const endsOf = (d: string, len: number) => [getPointAtLength(d, 0), getPointAtLength(d, len)];

type Props = {
	inner?: InnerTraces;
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
export const CircuitLetter: React.FC<Props> = ({inner, bend, feed, contours, fill, edge, start, speed, outlineFrames}) => {
	const frame = useCurrentFrame();
	const feedLen = useMemo(() => getLength(feed), [feed]);
	const lens = useMemo(() => contours.map((c) => getLength(c)), [contours]);

	const clipId = useMemo(() => `paint-${random(contours[0]).toString(36).slice(2, 10)}`, [contours]);
	const box = useMemo(() => {
		const ys = new Array(40).fill(0).map((_, i) => getPointAtLength(contours[0], (i / 40) * lens[0])?.y ?? 0);
		return {top: Math.min(...ys) - 4, bottom: Math.max(...ys) + 4};
	}, [contours, lens]);
	const innerLens = useMemo(() => (inner ? inner.paths.map((d) => getLength(d)) : []), [inner]);

	const feedFrames = feedLen / speed;
	const arrive = start + feedFrames;
	const closed = arrive + outlineFrames;

	const head = interpolate(frame, [start, arrive], [0, feedLen], {...clamp, easing: Easing.in(Easing.sin)});
	const outlineP = interpolate(frame, [arrive, closed], [0, 1], {...clamp, easing: Easing.out(Easing.sin)});
	// A tinta enche a letra de baixo para cima
	const fillP = interpolate(frame, [closed - 3, closed + 9], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
	const innerFade = interpolate(frame, [closed + 5, closed + 15], [1, 0], clamp);
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

			{/* Letra preenchida pela tinta */}
			<clipPath id={clipId}>
				<rect x={-500} y={box.bottom - (box.bottom - box.top) * fillP} width={2000} height={2000} />
			</clipPath>
			{fillP > 0 ? (
				<path
					d={contours.join(' ')}
					fill={fill}
					stroke={edge}
					strokeWidth={2.5}
					strokeLinejoin="round"
					clipPath={`url(#${clipId})`}
				/>
			) : null}

			{/* Trilhas internas: formam a letra junto com o contorno e somem depois da tinta */}
			{inner && innerFade > 0
				? inner.paths.map((d, i) => {
						const len = innerLens[i];
						const t0 = arrive + 1 + i * 1.2;
						const prog = interpolate(frame, [t0, t0 + outlineFrames], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
						if (prog <= 0) return null;
						const [a, b] = endsOf(d, len);
						const tip = prog < 1 ? getPointAtLength(d, prog * len) : null;
						return (
							<g key={i} opacity={innerFade}>
								<path
									d={d}
									fill="none"
									stroke={inner.color}
									strokeWidth={inner.width ?? 2.6}
									strokeLinejoin="round"
									strokeDasharray={`${prog * len} ${len * 2}`}
								/>
								{[a, prog >= 1 ? b : null].map((p, j) =>
									p ? <circle key={j} cx={p.x} cy={p.y} r={inner.pad ?? 4.2} fill="none" stroke={inner.color} strokeWidth={(inner.width ?? 2.6) * 0.9} /> : null,
								)}
								{tip ? (
									<g filter="url(#glow)">
										<circle cx={tip.x} cy={tip.y} r={8} fill="#a8e2ff" opacity={0.7} />
										<circle cx={tip.x} cy={tip.y} r={3.2} fill="#ffffff" />
									</g>
								) : null}
							</g>
						);
					})
				: null}

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
