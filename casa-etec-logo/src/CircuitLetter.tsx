import {getLength, getPointAtLength} from '@remotion/paths';
import React, {useMemo} from 'react';
import {Easing, interpolate, random, useCurrentFrame} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const ENERGY = '#c9f3ff';
const TRACE = '#3a8cf0';
const TRAIL = 110;

type Pt = {x: number; y: number};

type Branch = {
	/** Caminhos da bifurcação (todos saem do mesmo ponto). */
	paths: {d: string; len: number; end: Pt}[];
	/** Distância, ao longo do contorno, em que a energia chega à base. */
	dist: number;
};

export type BranchStyle = {
	count: number;
	/** Tamanho do primeiro trecho e dos dois ramos da forquilha. */
	stem: [number, number];
	fork: [number, number];
	/** "vertical": só para cima/baixo (texto). "noUp": nunca para cima (C e T, por causa do telhado). */
	mode: 'vertical' | 'noUp';
};

const DIRS = new Array(8).fill(0).map((_, i) => ({x: Math.cos((i * Math.PI) / 4), y: Math.sin((i * Math.PI) / 4)}));
const rot = (i: number, k: number) => DIRS[(i + k + 8) % 8];
const pt = (p: Pt, d: Pt, l: number) => ({x: p.x + d.x * l, y: p.y + d.y * l});
const f = (n: number) => Math.round(n * 10) / 10;

// Bifurcações a 45° saindo do contorno da letra, terminando em ilhas de solda.
const makeBranches = (contour: string, L: number, style: BranchStyle, seed: string): Branch[] => {
	const samples = new Array(48).fill(0).map((_, i) => getPointAtLength(contour, (i / 48) * L) as Pt);
	const center = {
		x: samples.reduce((a, p) => a + p.x, 0) / samples.length,
		y: samples.reduce((a, p) => a + p.y, 0) / samples.length,
	};
	const chosen: number[] = [];
	const out: Branch[] = [];
	for (let k = 0; k < 60 && out.length < style.count; k++) {
		const s = random(`${seed}-s${k}`) * L;
		if (chosen.some((c) => Math.abs(c - s) < L * 0.1)) continue;
		const base = getPointAtLength(contour, s) as Pt;
		const ox = base.x - center.x;
		const oy = base.y - center.y;
		const n = Math.hypot(ox, oy) || 1;
		let dir: number;
		if (style.mode === 'vertical') {
			if (Math.abs(oy / n) < 0.55) continue;
			dir = oy > 0 ? 2 : 6;
		} else {
			dir = Math.round(Math.atan2(oy, ox) / (Math.PI / 4));
			dir = (dir + 8) % 8;
			if (DIRS[dir].y < -0.1) continue;
		}
		chosen.push(s);
		const r = (key: string, [a, b]: [number, number]) => a + random(`${seed}-${key}${k}`) * (b - a);
		const knee = pt(base, DIRS[dir], r('a', style.stem));
		const ends = [pt(knee, rot(dir, -1), r('b', style.fork)), pt(knee, rot(dir, 1), r('c', style.fork))];
		if (random(`${seed}-x${k}`) > 0.55) ends.push(pt(knee, DIRS[dir], r('e', style.fork) * 0.7));
		out.push({
			dist: Math.min(s, L - s),
			paths: ends.map((e) => ({
				d: `M ${f(base.x)} ${f(base.y)} L ${f(knee.x)} ${f(knee.y)} L ${f(e.x)} ${f(e.y)}`,
				len: Math.hypot(knee.x - base.x, knee.y - base.y) + Math.hypot(e.x - knee.x, e.y - knee.y),
				end: e,
			})),
		});
	}
	return out;
};

const BranchView: React.FC<{b: Branch; reach: number}> = ({b, reach}) => (
	<>
		{b.paths.map((p, i) => {
			const prog = Math.max(0, Math.min(1, ((reach - b.dist) * 1.6) / p.len));
			if (prog <= 0) return null;
			const tip = prog < 1 ? getPointAtLength(p.d, prog * p.len) : null;
			return (
				<g key={i}>
					<path
						d={p.d}
						fill="none"
						stroke={TRACE}
						strokeWidth={3}
						strokeLinejoin="round"
						strokeDasharray={`${prog * p.len} ${p.len * 2}`}
					/>
					{tip ? (
						<g filter="url(#glow)">
							<circle cx={tip.x} cy={tip.y} r={7} fill="#7fd0ff" opacity={0.6} />
							<circle cx={tip.x} cy={tip.y} r={3} fill="#ffffff" />
						</g>
					) : (
						<circle cx={p.end.x} cy={p.end.y} r={4.5} fill="#ffffff" stroke={TRACE} strokeWidth={2.5} />
					)}
				</g>
			);
		})}
	</>
);

type Props = {
	branches?: BranchStyle;
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
export const CircuitLetter: React.FC<Props> = ({branches, bend, feed, contours, fill, edge, start, speed, outlineFrames}) => {
	const frame = useCurrentFrame();
	const feedLen = useMemo(() => getLength(feed), [feed]);
	const lens = useMemo(() => contours.map((c) => getLength(c)), [contours]);
	const branchList = useMemo(
		() => (branches ? makeBranches(contours[0], lens[0], branches, contours[0].slice(0, 24)) : []),
		[branches, contours, lens],
	);
	// Toco que continua reto depois da curva da trilha, com ilha de solda
	const stub = useMemo((): Branch | null => {
		if (!bend) return null;
		const edgeX = Number(feed.split(' ')[1]);
		const dirX = Math.sign(bend.x - edgeX);
		const len = 16 + random(`stub-${feed}`) * 12;
		const end = {x: bend.x + dirX * len, y: bend.y};
		return {dist: Math.abs(bend.x - edgeX), paths: [{d: `M ${bend.x} ${bend.y} H ${f(end.x)}`, len, end}]};
	}, [bend, feed]);

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
				{stub ? <BranchView b={stub} reach={head} /> : null}
				{bend && isPast(feed, head, bend) ? (
					<circle cx={bend.x} cy={bend.y} r={6} fill="#ffffff" stroke={TRACE} strokeWidth={3} />
				) : null}
			</g>

			{/* Bifurcações da letra */}
			<g opacity={feedFade}>
				{branchList.map((b, i) => (
					<BranchView key={i} b={b} reach={(outlineP * lens[0]) / 2} />
				))}
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
