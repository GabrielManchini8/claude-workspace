import {loadFont} from '@remotion/fonts';
import {CameraMotionBlur} from '@remotion/motion-blur';
import {noise2D} from '@remotion/noise';
import {evolvePath, getLength, getPointAtLength} from '@remotion/paths';
import React from 'react';
import {
	AbsoluteFill,
	Easing,
	interpolate,
	random,
	spring,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';

const fontFamily = 'Montserrat';
loadFont({
	family: fontFamily,
	url: staticFile('montserrat-latin-900-normal.woff2'),
	weight: '900',
});

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

const C_SHAPE =
	'M 432 400 L 305 400 A 140 160 0 0 0 305 720 L 432 720 L 432 630 L 330 630 A 100 82.5 0 0 1 330 465 L 432 465 Z';
const T_SHAPE =
	'M 605 408 L 866 408 L 916 436 L 890 474 L 776 474 L 776 718 L 694 718 L 694 474 L 605 474 Z';

// Trilhas de circuito (referência à versão "circuito" da logo).
const TRACES = [
	{d: 'M 420 432 L 305 432 A 108 121.5 0 0 0 305 675 L 420 675', nodes: [[420, 432], [420, 675]]},
	{d: 'M 360 520 L 290 520 L 262 548 L 262 600', nodes: [[360, 520], [262, 600]]},
	{d: 'M 625 441 L 878 441', nodes: [[625, 441], [878, 441]]},
	{d: 'M 735 474 L 735 700', nodes: [[735, 700]]},
	{d: 'M 712 500 L 712 600 L 690 622', nodes: [[690, 622]]},
	{d: 'M 758 500 L 758 640 L 780 662', nodes: [[780, 662]]},
];

const LETTERS = 'CASA E-TEC'.split('');

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

	// ── 4. C e T emergem da profundidade girando (42–70) ────────────────────
	const letterIn = (delay: number) => spring({frame: frame - delay, fps, config: {damping: 13, mass: 0.8}});
	const cP = letterIn(41);
	const tP = letterIn(46);
	const outlineP = interpolate(frame, [41, 58], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
	const fillOpacity = interpolate(frame, [52, 66], [0, 1], clamp);
	const traceP = interpolate(frame, [45, 62], [0, 1], {...clamp, easing: Easing.out(Easing.quad)});
	const traceOpacity = interpolate(frame, [62, 74], [1, 0], clamp);

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

	// ── 6. Texto: letras viram para cima e o espaçamento fecha (78–112) ────
	const tracking = interpolate(frame, [76, 114], [30, 3], {...clamp, easing: expoOut});
	const letter = (i: number) => {
		const delay = 77 + i * 2 + random(`l${i}`) * 3;
		const s = spring({frame: frame - delay, fps, config: {damping: 12, mass: 0.7}});
		return {
			y: (1 - s) * 70,
			rot: (1 - s) * -85,
			blur: Math.max(0, 1 - s) * 10,
			opacity: interpolate(s, [0, 0.45], [0, 1], clamp),
		};
	};

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

	// Fundo: zoom durante a viagem do botão, depois deriva lenta
	const bgScale = interpolate(frame, [0, 22, 150], [0.55, 1, 1.08], {
		...clamp,
		easing: Easing.inOut(Easing.quad),
	});

	return (
		<AbsoluteFill
			style={{
				background: 'radial-gradient(circle at 50% 42%, #ffffff 0%, #f1f5fc 55%, #dfe7f5 100%)',
				perspective: PERSPECTIVE,
				overflow: 'hidden',
			}}
		>
			<Defs />

			{/* Bokeh distante */}
			<div style={{position: 'absolute', inset: 0, transform: `scale(${bgScale})`}}>
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
							stroke="#3d8fff"
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

				{/* C e T */}
				{[
					{d: C_SHAPE, p: cP, fill: 'url(#cGrad)', edge: '#0a2a78', glow: '#2f8cff', o: [300, 560], dir: -1, mask: 'maskC'},
					{d: T_SHAPE, p: tP, fill: 'url(#tGrad)', edge: '#1c2333', glow: '#6b84b8', o: [760, 560], dir: 1, mask: 'maskT'},
				].map((l) => {
					const outline = evolvePath(outlineP, l.d);
					return (
						<Layer
							key={l.d}
							depth={60}
							origin={l.o as [number, number]}
							style={{
								transform: `perspective(1000px) translateX(${(1 - l.p) * l.dir * 60}px) rotateY(${(1 - l.p) * l.dir * -55}deg) scale(${interpolate(l.p, [0, 1], [0.35, 1])})`,
								opacity: interpolate(l.p, [0, 0.25], [0, 1], clamp),
								filter: `blur(${Math.max(0, 1 - l.p) * 14}px)`,
							}}
						>
							<path d={l.d} fill={l.fill} opacity={fillOpacity} stroke={l.edge} strokeWidth={3} strokeLinejoin="round" />
							<path
								d={l.d}
								fill="none"
								stroke={l.glow}
								strokeWidth={5}
								strokeLinejoin="round"
								strokeDasharray={outline.strokeDasharray}
								strokeDashoffset={outline.strokeDashoffset}
								opacity={1 - fillOpacity * 0.9}
								filter="url(#glow)"
							/>
							<Shine x={shineX + (l.dir > 0 ? 80 : 0)} mask={l.mask} />
						</Layer>
					);
				})}

				{/* Trilhas de circuito */}
				<Layer depth={62} style={{opacity: traceOpacity}}>
					<g filter="url(#glow)">
						{TRACES.map((t) => {
							const ev = evolvePath(traceP, t.d);
							return (
								<g key={t.d}>
									<path
										d={t.d}
										fill="none"
										stroke="#8fd0ff"
										strokeWidth={4}
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeDasharray={ev.strokeDasharray}
										strokeDashoffset={ev.strokeDashoffset}
									/>
									{t.nodes.map(([x, y]) => (
										<circle
											key={`${x}-${y}`}
											cx={x}
											cy={y}
											r={7}
											fill="#ffffff"
											stroke="#8fd0ff"
											strokeWidth={4}
											opacity={interpolate(traceP, [0.8, 1], [0, 1], clamp)}
										/>
									))}
								</g>
							);
						})}
					</g>
				</Layer>

				{/* Ondas de choque do clique */}
				<Layer depth={80}>
					{shocks.map((s, i) =>
						s.visible ? (
							<circle key={i} cx={DOT.x} cy={DOT.y} r={s.r} fill="none" stroke="#2f8cff" strokeWidth={s.w} opacity={s.o} />
						) : null,
					)}
				</Layer>

				{/* Texto */}
				<Layer depth={25} html>
					<div
						style={{
							position: 'absolute',
							left: 0,
							right: 0,
							top: (770 / 1024) * SIZE + 10,
							display: 'flex',
							justifyContent: 'center',
						}}
					>
						{LETTERS.map((ch, i) => {
							const a = letter(i);
							return (
								<span
									key={i}
									style={{
										display: 'inline-block',
										fontFamily,
										fontWeight: 900,
										fontSize: 118,
										lineHeight: 1.1,
										marginRight: i < LETTERS.length - 1 ? tracking : 0,
										whiteSpace: 'pre',
										transformOrigin: '50% 100%',
										transform: `perspective(600px) translateY(${a.y}px) rotateX(${a.rot}deg)`,
										filter: `blur(${a.blur}px)`,
										opacity: a.opacity,
										backgroundImage:
											i < 4
												? 'linear-gradient(180deg, #1a55c8, #0a2f86)'
												: 'linear-gradient(180deg, #454d5f, #252b38)',
										WebkitBackgroundClip: 'text',
										backgroundClip: 'text',
										color: 'transparent',
									}}
								>
									{ch}
								</span>
							);
						})}
					</div>
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
	return (
		<AbsoluteFill>
			<CameraMotionBlur shutterAngle={200} samples={7}>
				<Scene />
			</CameraMotionBlur>

			{/* Vinheta e granulação de filme */}
			<AbsoluteFill
				style={{
					background: 'radial-gradient(circle at 50% 45%, rgba(0,0,0,0) 55%, rgba(10,30,70,0.16) 100%)',
					pointerEvents: 'none',
				}}
			/>
			<svg
				width={SIZE}
				height={SIZE}
				style={{position: 'absolute', opacity: 0.07, mixBlendMode: 'multiply', pointerEvents: 'none'}}
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
