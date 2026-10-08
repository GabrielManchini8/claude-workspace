// Gera src/glyphs.json: contornos vetoriais de "CASA E-TEC" (Montserrat Black)
// já posicionados no espaço 1024x1024, com o ponto de entrada da trilha de cada letra.
// Uso: node scripts/gen-glyphs.mjs
import fs from 'node:fs';
import ClipperLib from 'clipper-lib';
import opentype from 'opentype.js';

const font = opentype.loadSync(new URL('../assets/montserrat-latin-900-normal.woff', import.meta.url).pathname);
const TEXT = 'CASA E-TEC';
const SIZE = 112;
const SPACING = 3;
const BASELINE = 872;
const CAP_TOP = BASELINE - (font.tables.os2.sCapHeight / font.unitsPerEm) * SIZE;

const glyphs = [...TEXT].map((ch) => font.charToGlyph(ch));
const scale = SIZE / font.unitsPerEm;
let width = 0;
glyphs.forEach((g, i) => {
	width += g.advanceWidth * scale + (i < glyphs.length - 1 ? SPACING : 0);
	if (i < glyphs.length - 1) width += font.getKerningValue(g, glyphs[i + 1]) * scale;
});

const r = (n) => Math.round(n * 100) / 100;
const segStr = (c) => {
	if (c.type === 'L') return `L ${r(c.x)} ${r(c.y)}`;
	if (c.type === 'Q') return `Q ${r(c.x1)} ${r(c.y1)} ${r(c.x)} ${r(c.y)}`;
	if (c.type === 'C') return `C ${r(c.x1)} ${r(c.y1)} ${r(c.x2)} ${r(c.y2)} ${r(c.x)} ${r(c.y)}`;
	throw new Error(c.type);
};

// Separa o caminho em contornos e reordena cada um para começar no ponto
// mais alto (entrada por cima) ou mais baixo (entrada por baixo).
const contoursOf = (path, fromTop) => {
	const out = [];
	let cur = null;
	for (const c of path.commands) {
		if (c.type === 'M') cur = {p0: {x: c.x, y: c.y}, segs: []};
		else if (c.type === 'Z') {
			const last = cur.segs[cur.segs.length - 1];
			if (!last || Math.hypot(last.x - cur.p0.x, last.y - cur.p0.y) > 0.01) {
				cur.segs.push({type: 'L', x: cur.p0.x, y: cur.p0.y});
			}
			out.push(cur);
		} else cur.segs.push(c);
	}
	return out.map(({segs}) => {
		let k = 0;
		segs.forEach((s, i) => {
			if (fromTop ? s.y < segs[k].y : s.y > segs[k].y) k = i;
		});
		const ordered = [...segs.slice(k + 1), ...segs.slice(0, k + 1)];
		const start = segs[k];
		const xs = segs.map((s) => s.x);
		return {
			d: `M ${r(start.x)} ${r(start.y)} ${ordered.map(segStr).join(' ')} Z`,
			start: {x: r(start.x), y: r(start.y)},
			area: (Math.max(...xs) - Math.min(...xs)) * Math.abs(Math.max(...segs.map((s) => s.y)) - Math.min(...segs.map((s) => s.y))),
		};
	});
};

// ── Trilhas internas: contornos recuados (offset para dentro) da letra,
// cortados em pedaços com ilhas de solda nas pontas.
const SCALE = 100;
const flatten = (path) => {
	const polys = [];
	let cur = null;
	let last = null;
	for (const c of path.commands) {
		if (c.type === 'M') {
			cur = [{X: c.x, Y: c.y}];
			polys.push(cur);
		} else if (c.type === 'L') cur.push({X: c.x, Y: c.y});
		else if (c.type === 'Q' || c.type === 'C') {
			for (let i = 1; i <= 8; i++) {
				const t = i / 8;
				const u = 1 - t;
				if (c.type === 'Q') {
					cur.push({X: u * u * last.x + 2 * u * t * c.x1 + t * t * c.x, Y: u * u * last.y + 2 * u * t * c.y1 + t * t * c.y});
				} else {
					cur.push({
						X: u ** 3 * last.x + 3 * u * u * t * c.x1 + 3 * u * t * t * c.x2 + t ** 3 * c.x,
						Y: u ** 3 * last.y + 3 * u * u * t * c.y1 + 3 * u * t * t * c.y2 + t ** 3 * c.y,
					});
				}
			}
		}
		if (c.x !== undefined) last = {x: c.x, y: c.y};
	}
	return polys.map((p) => p.map((q) => ({X: Math.round(q.X * SCALE), Y: Math.round(q.Y * SCALE)})));
};

let seed = 7;
const rnd = () => {
	seed = (seed * 16807) % 2147483647;
	return seed / 2147483647;
};

const innerTraces = (path, insets) => {
	const base = ClipperLib.Clipper.SimplifyPolygons(flatten(path), ClipperLib.PolyFillType.pftNonZero);
	const out = [];
	for (const inset of insets) {
		const co = new ClipperLib.ClipperOffset(2, 25);
		co.AddPaths(base, ClipperLib.JoinType.jtMiter, ClipperLib.EndType.etClosedPolygon);
		const sol = new ClipperLib.Paths();
		co.Execute(sol, -inset * SCALE);
		for (const poly of sol) {
			const pts = poly.map((p) => ({x: p.X / SCALE, y: p.Y / SCALE}));
			pts.push(pts[0]);
			const cum = [0];
			for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y));
			const P = cum[cum.length - 1];
			if (P < 40) continue;
			// Corta o laço em 1–3 trilhas, deixando um vão entre elas
			const cuts = P > 260 ? 3 : P > 130 ? 2 : 1;
			const offset = rnd() * P;
			const gap = 9;
			const at = (d) => {
				d = ((d % P) + P) % P;
				let i = 1;
				while (cum[i] < d) i++;
				const t = (d - cum[i - 1]) / (cum[i] - cum[i - 1] || 1);
				return {x: pts[i - 1].x + (pts[i].x - pts[i - 1].x) * t, y: pts[i - 1].y + (pts[i].y - pts[i - 1].y) * t};
			};
			for (let k = 0; k < cuts; k++) {
				const a = offset + (k * P) / cuts + gap / 2;
				const b = offset + ((k + 1) * P) / cuts - gap / 2;
				const seg = [at(a)];
				for (let i = 0; i < pts.length - 1; i++) {
					for (const lap of [0, P]) {
						const d = cum[i] + lap;
						if (d > a && d < b) seg.push({d, p: pts[i]});
					}
				}
				const mid = seg.slice(1).sort((m, n) => m.d - n.d).map((m) => m.p);
				const line = [seg[0], ...mid, at(b)];
				out.push('M ' + line.map((p) => `${r(p.x)} ${r(p.y)}`).join(' L '));
			}
		}
	}
	return out;
};

let x = 512 - width / 2;
const letters = [];
glyphs.forEach((g, i) => {
	const ch = TEXT[i];
	if (ch !== ' ') {
		const side = i < 4 ? 'left' : 'right';
		const order = side === 'left' ? i : TEXT.length - 1 - i; // distância até a borda de onde a trilha vem
		const fromTop = order % 2 === 0;
		const contours = contoursOf(g.getPath(x, BASELINE, SIZE), fromTop).sort((a, b) => b.area - a.area);
		const entry = contours[0].start;
		const lane = fromTop ? CAP_TOP - 16 - order * 10 : BASELINE + 16 + order * 10;
		const dy = Math.abs(entry.y - lane);
		const bendX = side === 'left' ? entry.x - dy : entry.x + dy;
		const edgeX = side === 'left' ? -300 : 1324;
		letters.push({
			ch,
			index: i,
			side,
			order,
			contours: contours.map((c) => c.d),
			inner: innerTraces(g.getPath(x, BASELINE, SIZE), [6.5]),
			feed: `M ${edgeX} ${r(lane)} H ${r(bendX)} L ${entry.x} ${entry.y}`,
			bend: {x: r(bendX), y: r(lane)},
		});
	}
	x += g.advanceWidth * scale + SPACING;
	if (i < glyphs.length - 1) x += font.getKerningValue(g, glyphs[i + 1]) * scale;
});

fs.writeFileSync(new URL('../src/glyphs.json', import.meta.url), JSON.stringify({letters}, null, '\t') + '\n');
console.log(letters.map((l) => `${l.ch} ${l.side}/${l.order} ${l.feed}`).join('\n'));
