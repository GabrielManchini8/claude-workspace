import {CameraMotionBlur} from '@remotion/motion-blur';
import {noise2D} from '@remotion/noise';
import {getLength, getPointAtLength} from '@remotion/paths';
import React from 'react';
import {
	AbsoluteFill,
	Easing,
	interpolate,
	random,
	spring,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';
import {CircuitLetter, InnerTraces} from './CircuitLetter';
import GLYPHS from './glyphs.json';


// A logo é desenhada num espaço 1024x1024; o vídeo tem 1080x1080.
const SIZE = 1080;
const K = SIZE / 1024;
const PERSPECTIVE = 1600;

const ARC_CENTER = {x: 515, y: 470};
const DOT = {x: 516, y: 360, r: 41};

const arcPath = (r: number, halfAngleDeg: number) => {
	const a = (halfAngleDeg * Math.PI) / 180;
	const x1 = ARC_CENTER.x - r * Math.sin(a);
	const x2 = ARC_CENTER.x + r * Math.sin(a);
	const y = ARC_CENTER.y - r * Math.cos(a);
	return `M ${x1} ${y} A ${r} ${r} 0 0 1 ${x2} ${y}`;
};

const OUTER_ARC = arcPath(395, 44);
const INNER_ARC = arcPath(298, 43);

const ROOF = 'M 822 378 L 515 252 L 132 452 L 152 480';
const ROOF_LENGTH = getLength(ROOF);
const ROOF_APEX = Math.hypot(822 - 515, 378 - 252);

// C começa no ponto mais à esquerda e T na ponta direita: é onde as trilhas chegam.
const C_SHAPE =
	'M 165 560 A 140 160 0 0 0 305 720 L 432 720 L 432 630 L 330 630 A 100 82.5 0 0 1 330 465 L 432 465 L 432 400 L 305 400 A 140 160 0 0 0 165 560 Z';
const T_SHAPE =
	'M 916 436 L 890 474 L 776 474 L 776 718 L 694 718 L 694 474 L 605 474 L 605 408 L 866 408 Z';
// Ponto numa "faixa" paralela dentro do C. t: 0 = borda externa, 1 = borda interna.
// u: 0 = ponta de cima, 1 = ponta de baixo (passando pela curva da esquerda).
const cLane = (t: number, u: number) => {
	const cx = 305 + 25 * t;
	const cy = 560 - 12.5 * t;
	const rx = 140 - 40 * t;
	const ry = 160 - 77.5 * t;
	const a = 0.14;
	const tipX = 418;
	if (u < a) return {x: tipX + (cx - tipX) * (u / a), y: cy - ry};
	if (u > 1 - a) return {x: cx + (tipX - cx) * ((u - (1 - a)) / a), y: cy + ry};
	const th = -Math.PI / 2 - ((u - a) / (1 - 2 * a)) * Math.PI;
	return {x: cx + rx * Math.cos(th), y: cy + ry * Math.sin(th)};
};
// Trilha que segue faixas do C; cada item é [t, uInicial, uFinal] e as trocas de faixa viram diagonais.
const cTrace = (legs: [number, number, number][]) => {
	const pts: {x: number; y: number}[] = [];
	for (const [t, u0, u1] of legs) {
		const n = Math.max(2, Math.ceil(Math.abs(u1 - u0) * 60));
		for (let i = 0; i <= n; i++) pts.push(cLane(t, u0 + ((u1 - u0) * i) / n));
	}
	return 'M ' + pts.map((p) => `${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' L ');
};

const C_INNER: InnerTraces = {
	color: '#9dd3ff',
	paths: [
		cTrace([[0.22, 0.02, 0.38], [0.5, 0.43, 0.6]]),
		cTrace([[0.5, 0.06, 0.32]]),
		cTrace([[0.78, 0.04, 0.5]]),
		cTrace([[0.22, 0.45, 0.66], [0.5, 0.71, 0.98]]),
		cTrace([[0.78, 0.58, 0.97]]),
		cTrace([[0.22, 0.74, 0.97]]),
		cTrace([[0.64, 0.36, 0.55]]),
		cTrace([[0.36, 0.7, 0.8]]),
		cTrace([[0.64, 0.66, 0.88]]),
	],
};
const T_INNER: InnerTraces = {
	color: '#b9c4d9',
	paths: [
		'M 620 424 H 866',
		'M 640 441 H 690 L 712 463 V 700',
		'M 880 446 H 792 L 758 480 V 702',
		'M 622 458 H 668',
		'M 735 492 V 655',
		'M 800 461 H 862',
	],
};

const C_FEED = 'M -300 640 H 85 L 165 560';
const T_FEED = 'M 1324 520 H 1000 L 916 436';

const BOKEH = new Array(14).fill(0).map((_, i) => ({
	x: random(`bx${i}`) * 1024,
	y: random(`by${i}`) * 1024,
	r: 18 + random(`br${i}`) * 80,
	o: 0.05 + random(`bo${i}`) * 0.1,
	blur: 6 + random(`bb${i}`) * 18,
	color: random(`bc${i}`) > 0.5 ? '#2f8cff' : '#8fc4ff',
}));

const STREAKS = new Array(46).fill(0).map((_, i) => ({
	angle: random(`sa${i}`) * Math.PI * 2,
	start: random(`ss${i}`) * 6,
	speed: 0.7 + random(`sv${i}`) * 0.8,
	width: 1.5 + random(`sw${i}`) * 3,
}));

// Até aqui o fundo é transparente (o botão sai do meio do seu vídeo).
// Neste quadro o botão cobre a tela inteira e o fundo branco entra por trás dele.
const BG_ON_FRAME = 20;

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const expoOut = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * Uma camada da cena com profundidade própria (translateZ) para gerar paralaxe
 * quando a câmera inclina. A escala compensa a perspectiva, então em repouso
 * todas as camadas se alinham exatamente como na logo.
 */
const Layer: React.FC<{
	depth: number;
	origin?: [number, number];
	style?: React.CSSProperties;
	html?: boolean;
	children: React.ReactNode;
}> = ({depth, origin = [512, 512], style, html, children}) => (
	<div
		style={{
			position: 'absolute',
			inset: 0,
			transformStyle: 'preserve-3d',
			transformOrigin: `${SIZE / 2}px ${SIZE / 2}px`,
			transform: `translateZ(${depth}px) scale(${(PERSPECTIVE - depth) / PERSPECTIVE})`,
		}}
	>
		<div
			style={{
				position: 'absolute',
				inset: 0,
				transformOrigin: `${origin[0] * K}px ${origin[1] * K}px`,
				...style,
			}}
		>
			{html ? (
				children
			) : (
				<svg
					viewBox="0 0 1024 1024"
					width={SIZE}
					height={SIZE}
					style={{position: 'absolute', overflow: 'visible'}}
				>
					{children}
				</svg>
			)}
		</div>
	</div>
);

const Defs: React.FC = () => (
	<svg width={0} height={0} style={{position: 'absolute'}}>
		<defs>
			<linearGradient id="roofGrad" gradientUnits="userSpaceOnUse" x1="130" y1="0" x2="830" y2="0">
				<stop offset="0" stopColor="#0b3aa6" />
				<stop offset="0.5" stopColor="#1d3f86" />
				<stop offset="1" stopColor="#4b5468" />
			</linearGradient>
			<linearGradient id="arcGrad" gradientUnits="userSpaceOnUse" x1="220" y1="0" x2="810" y2="0">
				<stop offset="0" stopColor="#0c3cb4" />
				<stop offset="0.55" stopColor="#2fa6ff" />
				<stop offset="1" stopColor="#0f46c8" />
			</linearGradient>
			<linearGradient id="cGrad" x1="0" y1="0" x2="1" y2="1">
				<stop offset="0" stopColor="#3aa2ff" />
				<stop offset="0.45" stopColor="#1661e0" />
				<stop offset="1" stopColor="#0a2f8c" />
			</linearGradient>
			<linearGradient id="tGrad" x1="0" y1="0" x2="1" y2="0.4">
				<stop offset="0" stopColor="#273250" />
				<stop offset="1" stopColor="#6a7284" />
			</linearGradient>
			<radialGradient id="dotGrad" cx="0.36" cy="0.32" r="0.75">
				<stop offset="0" stopColor="#4b8cf2" />
				<stop offset="0.55" stopColor="#1a4fc4" />
				<stop offset="1" stopColor="#0a2d86" />
			</radialGradient>
			<linearGradient id="casaGrad" gradientUnits="userSpaceOnUse" x1="0" y1="794" x2="0" y2="872">
				<stop offset="0" stopColor="#1a55c8" />
				<stop offset="1" stopColor="#0a2f86" />
			</linearGradient>
			<linearGradient id="etecGrad" gradientUnits="userSpaceOnUse" x1="0" y1="794" x2="0" y2="872">
				<stop offset="0" stopColor="#454d5f" />
				<stop offset="1" stopColor="#252b38" />
			</linearGradient>
			<linearGradient id="shineGrad" x1="0" y1="0" x2="1" y2="0">
				<stop offset="0" stopColor="#fff" stopOpacity="0" />
				<stop offset="0.5" stopColor="#fff" stopOpacity="0.7" />
				<stop offset="1" stopColor="#fff" stopOpacity="0" />
			</linearGradient>
			<filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
				<feGaussianBlur stdDeviation="5" result="b" />
				<feMerge>
					<feMergeNode in="b" />
					<feMergeNode in="SourceGraphic" />
				</feMerge>
			</filter>
			<mask id="maskC">
				<path d={C_SHAPE} fill="#fff" />
			</mask>
			<mask id="maskT">
				<path d={T_SHAPE} fill="#fff" />
			</mask>
			<mask id="maskArcs">
				<path d={OUTER_ARC} fill="none" stroke="#fff" strokeWidth={44} />
				<path d={INNER_ARC} fill="none" stroke="#fff" strokeWidth={40} />
			</mask>
			<mask id="maskRoof">
				<path d={ROOF} fill="none" stroke="#fff" strokeWidth={34} />
			</mask>
		</defs>
	</svg>
);

const Shine: React.FC<{x: number; mask: string}> = ({x, mask}) => (
	<g mask={`url(#${mask})`}>
		<rect
			x={x}
			y={-100}
			width={170}
			height={1200}
			fill="url(#shineGrad)"
			transform={`rotate(20 ${x + 85} 500)`}
		/>
	</g>
);

const Scene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	// ── 1. O botão vem do fundo e atravessa a tela (0–20) ──────────────────
	const flyT = interpolate(frame, [0, 20], [0, 1], clamp);
	const flyScale = 0.035 * Math.exp(Math.log(28 / 0.035) * Easing.in(Easing.cubic)(flyT));
	const flyBlur = interpolate(flyT, [0, 0.45, 1], [5, 0, 16], clamp);

	// ── 2. Volta como uma íris até o lugar dele (20–38) ─────────────────────
	const back = spring({frame: frame - 20, fps, config: {damping: 15, stiffness: 110, mass: 0.9}});
	const backScale = interpolate(back, [0, 1], [28, 1]);
	const isFlying = frame < 20;
	const dotScale = isFlying ? flyScale : backScale;
	const dotPos = isFlying
		? {x: 512 + noise2D('dx', frame / 14, 0) * 10, y: 512}
		: {x: interpolate(back, [0, 1], [512, DOT.x]), y: interpolate(back, [0, 1], [512, DOT.y])};
	const dotBlur = isFlying ? flyBlur : interpolate(back, [0, 0.5], [12, 0], clamp);

	// "Clique": achata e estica ao assentar
	const tSquash = frame - 33;
	const squash = tSquash > 0 ? Math.exp(-tSquash / 5) * Math.sin(tSquash * 0.75) * 0.24 : 0;
	const pressGlow = interpolate(frame, [33, 38, 70], [0, 1, 0.25], clamp);

	// Ondas de choque do clique
	const shock = (start: number, reach: number) => {
		const p = interpolate(frame, [start, start + 22], [0, 1], {...clamp, easing: expoOut});
		return {r: DOT.r + p * reach, o: (1 - p) * 0.7, w: 8 * (1 - p) + 0.5, visible: p > 0 && p < 1};
	};
	const shocks = [shock(34, 130), shock(38, 230)];

	// ── 3. Telhado acende a partir do topo, com faíscas (36–58) ─────────────
	const roofP = interpolate(frame, [36, 58], [0, 1], {...clamp, easing: expoOut});
	const roofStart = ROOF_APEX * (1 - roofP);
	const roofEnd = ROOF_APEX + (ROOF_LENGTH - ROOF_APEX) * roofP;
	const sparkO = interpolate(roofP, [0, 0.05, 0.8, 1], [0, 1, 1, 0], clamp);
	const sparkA = getPointAtLength(ROOF, Math.max(0.01, roofStart)) ?? {x: 515, y: 252};
	const sparkB = getPointAtLength(ROOF, Math.min(ROOF_LENGTH - 0.01, roofEnd)) ?? {x: 515, y: 252};

	// ── 5. Wi-Fi expande com eco (58–90) ────────────────────────────────────
	const wave = (delay: number) => {
		const s = spring({frame: frame - delay, fps, config: {damping: 10, mass: 0.6}});
		const echo = interpolate(frame, [delay + 5, delay + 30], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
		return {
			scale: interpolate(s, [0, 1], [0.15, 1]),
			opacity: interpolate(frame, [delay, delay + 6], [0, 1], clamp),
			blur: interpolate(s, [0, 0.7], [10, 0], clamp),
			echoScale: 1 + echo * 0.32,
			echoOpacity: echo > 0 && echo < 1 ? (1 - echo) * 0.45 : 0,
		};
	};
	const waves = [
		{d: INNER_ARC, w: 40, a: wave(58), pulse: interpolate(frame, [114, 121, 136], [0, 0.55, 0], clamp)},
		{d: OUTER_ARC, w: 44, a: wave(64), pulse: interpolate(frame, [120, 127, 142], [0, 0.55, 0], clamp)},
	];

	// ── 7. Brilho final ─────────────────────────────────────────────────────
	const shineX = interpolate(frame, [104, 134], [-400, 1300], {...clamp, easing: Easing.inOut(Easing.quad)});

	// ── Câmera: varredura 3D na montagem + flutuação orgânica ───────────────
	const sweep = interpolate(frame, [36, 96], [1, 0], {...clamp, easing: Easing.out(Easing.cubic)});
	const idle = interpolate(frame, [60, 110], [0, 1], clamp);
	const camRotY = -14 * sweep + noise2D('ry', frame / 80, 0) * 5 * idle;
	const camRotX = 8 * sweep + noise2D('rx', frame / 90, 3) * 3.5 * idle;
	const camRotZ = noise2D('rz', frame / 60, 7) * 0.5;
	const camX = noise2D('cx', frame / 45, 1) * 4;
	const camY = noise2D('cy', frame / 50, 2) * 4;
	const camScale = interpolate(frame, [30, 150], [0.9, 0.95], {...clamp, easing: Easing.out(Easing.quad)});

	const bgOn = frame >= BG_ON_FRAME ? 1 : 0;

	// Fundo: zoom durante a viagem do botão, depois deriva lenta
	const bgScale = interpolate(frame, [0, 22, 150], [0.55, 1, 1.08], {
		...clamp,
		easing: Easing.inOut(Easing.quad),
	});

	return (
		<AbsoluteFill
			style={{
				perspective: PERSPECTIVE,
				overflow: 'hidden',
			}}
		>
			<Defs />

			{/* Fundo branco: só aparece depois que o botão cobre a tela */}
			<AbsoluteFill
				style={{
					background: 'radial-gradient(circle at 50% 42%, #ffffff 0%, #f1f5fc 55%, #dfe7f5 100%)',
					opacity: bgOn,
				}}
			/>

			{/* Bokeh distante */}
			<div style={{position: 'absolute', inset: 0, transform: `scale(${bgScale})`, opacity: bgOn}}>
				{BOKEH.map((b, i) => (
					<div
						key={i}
						style={{
							position: 'absolute',
							left: (b.x + noise2D(`bnx${i}`, frame / 120, 0) * 40) * K - b.r,
							top: (b.y + noise2D(`bny${i}`, frame / 120, 0) * 40) * K - b.r,
							width: b.r * 2,
							height: b.r * 2,
							borderRadius: '50%',
							background: b.color,
							opacity: b.o,
							filter: `blur(${b.blur}px)`,
						}}
					/>
				))}
			</div>

			{/* Rastros de velocidade enquanto o botão avança */}
			<svg viewBox="0 0 1024 1024" width={SIZE} height={SIZE} style={{position: 'absolute'}}>
				{STREAKS.map((s, i) => {
					const t = (frame - s.start) / 18;
					if (t <= 0 || t >= 1) return null;
					const r1 = 30 + Math.pow(t, 2.2) * 900 * s.speed;
					const r2 = r1 + 40 + t * 260;
					const cos = Math.cos(s.angle);
					const sin = Math.sin(s.angle);
					return (
						<line
							key={i}
							x1={512 + cos * r1}
							y1={512 + sin * r1}
							x2={512 + cos * r2}
							y2={512 + sin * r2}
							stroke="#6cb8ff"
							strokeWidth={s.width}
							strokeLinecap="round"
							opacity={Math.sin(t * Math.PI) * 0.55}
						/>
					);
				})}
			</svg>

			{/* Palco 3D com a logo */}
			<div
				style={{
					position: 'absolute',
					inset: 0,
					transformStyle: 'preserve-3d',
					transform: `translate(${camX}px, ${camY}px) scale(${camScale}) rotateX(${camRotX}deg) rotateY(${camRotY}deg) rotateZ(${camRotZ}deg)`,
				}}
			>
				{/* Wi-Fi */}
				{waves.map(({d, w, a, pulse}) => (
					<Layer
						key={d}
						depth={30}
						origin={[DOT.x, DOT.y]}
						style={{
							transform: `scale(${a.scale})`,
							opacity: a.opacity,
							filter: `blur(${a.blur}px)`,
						}}
					>
						<path d={d} fill="none" stroke="url(#arcGrad)" strokeWidth={w} />
						<path d={d} fill="none" stroke="#c4e8ff" strokeWidth={w} opacity={pulse} />
						<Shine x={shineX} mask="maskArcs" />
						<g
							opacity={a.echoOpacity}
							transform={`translate(${DOT.x} ${DOT.y}) scale(${a.echoScale}) translate(${-DOT.x} ${-DOT.y})`}
						>
							<path d={d} fill="none" stroke="#5aaeff" strokeWidth={w * 0.35} />
						</g>
					</Layer>
				))}

				{/* Telhado */}
				<Layer depth={10}>
					<path
						d={ROOF}
						fill="none"
						stroke="url(#roofGrad)"
						strokeWidth={34}
						strokeLinejoin="miter"
						strokeDasharray={`0 ${roofStart} ${roofEnd - roofStart} ${ROOF_LENGTH * 2}`}
					/>
					<Shine x={shineX - 120} mask="maskRoof" />
					{[sparkA, sparkB].map((p, i) => (
						<g key={i} opacity={sparkO} filter="url(#glow)">
							<circle cx={p.x} cy={p.y} r={14} fill="#9fd4ff" opacity={0.6} />
							<circle cx={p.x} cy={p.y} r={6} fill="#ffffff" />
						</g>
					))}
				</Layer>

				{/* C e T formados por trilhas de circuito */}
				<Layer depth={60}>
					<CircuitLetter inner={C_INNER} bend={{x: 85, y: 640}} feed={C_FEED} contours={[C_SHAPE]} fill="url(#cGrad)" edge="#0a2a78" start={40} speed={34} outlineFrames={18} />
					<CircuitLetter inner={T_INNER} bend={{x: 1000, y: 520}} feed={T_FEED} contours={[T_SHAPE]} fill="url(#tGrad)" edge="#1c2333" start={43} speed={34} outlineFrames={18} />
					<Shine x={shineX} mask="maskC" />
					<Shine x={shineX + 80} mask="maskT" />
				</Layer>

				{/* Ondas de choque do clique */}
				<Layer depth={80}>
					{shocks.map((s, i) =>
						s.visible ? (
							<circle key={i} cx={DOT.x} cy={DOT.y} r={s.r} fill="none" stroke="#2f8cff" strokeWidth={s.w} opacity={s.o} />
						) : null,
					)}
				</Layer>

				{/* Texto formado por trilhas que vêm da esquerda e da direita */}
				<Layer depth={25}>
					{GLYPHS.letters.map((l) => (
						<CircuitLetter
							key={l.index}
							bend={l.bend}
							feed={l.feed}
							contours={l.contours}
							fill={l.index < 4 ? 'url(#casaGrad)' : 'url(#etecGrad)'}
							edge={l.index < 4 ? '#0a2f86' : '#252b38'}
							start={64 + l.order * 3 + random(`t${l.index}`) * 2}
							speed={50}
							outlineFrames={12}
						/>
					))}
				</Layer>

				{/* O botão (sempre por cima, é ele que "liga" a casa) */}
				<Layer
					depth={90}
					origin={[DOT.x, DOT.y]}
					style={{
						transform: `translate(${(dotPos.x - DOT.x) * K}px, ${(dotPos.y - DOT.y) * K}px) scale(${dotScale * (1 + squash)}, ${dotScale * (1 - squash)})`,
						filter: `blur(${dotBlur}px) drop-shadow(0 0 ${18 * pressGlow}px rgba(47,140,255,${0.9 * pressGlow}))`,
					}}
				>
					<circle cx={DOT.x} cy={DOT.y} r={DOT.r} fill="url(#dotGrad)" />
					<ellipse cx={DOT.x - 12} cy={DOT.y - 15} rx={13} ry={8} fill="#ffffff" opacity={0.28} />
				</Layer>
			</div>
		</AbsoluteFill>
	);
};

export const CasaETecLogo: React.FC = () => {
	const frame = useCurrentFrame();
	const bgOn = frame >= BG_ON_FRAME ? 1 : 0;
	return (
		<AbsoluteFill>
			{/* Base opaca (o motion blur deixa o fundo levemente translúcido) */}
			<AbsoluteFill
				style={{
					background: 'radial-gradient(circle at 50% 42%, #ffffff 0%, #f1f5fc 55%, #dfe7f5 100%)',
					opacity: bgOn,
				}}
			/>
			<CameraMotionBlur shutterAngle={200} samples={7}>
				<Scene />
			</CameraMotionBlur>

			{/* Vinheta e granulação de filme */}
			<AbsoluteFill
				style={{
					background: 'radial-gradient(circle at 50% 45%, rgba(0,0,0,0) 55%, rgba(10,30,70,0.16) 100%)',
					opacity: bgOn,
					pointerEvents: 'none',
				}}
			/>
			<svg
				width={SIZE}
				height={SIZE}
				style={{position: 'absolute', opacity: 0.07 * bgOn, mixBlendMode: 'multiply', pointerEvents: 'none'}}
			>
				<filter id={`grain-${frame % 4}`}>
					<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={frame} stitchTiles="stitch" />
					<feColorMatrix type="saturate" values="0" />
				</filter>
				<rect width="100%" height="100%" filter={`url(#grain-${frame % 4})`} />
			</svg>
		</AbsoluteFill>
	);
};
