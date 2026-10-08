// Gera src/glyphs.json: contornos vetoriais de "CASA E-TEC" (Montserrat Black)
// já posicionados no espaço 1024x1024, com o ponto de entrada da trilha de cada letra.
// Uso: node scripts/gen-glyphs.mjs
import fs from 'node:fs';
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
			feed: `M ${edgeX} ${r(lane)} H ${r(bendX)} L ${entry.x} ${entry.y}`,
			bend: {x: r(bendX), y: r(lane)},
		});
	}
	x += g.advanceWidth * scale + SPACING;
	if (i < glyphs.length - 1) x += font.getKerningValue(g, glyphs[i + 1]) * scale;
});

fs.writeFileSync(new URL('../src/glyphs.json', import.meta.url), JSON.stringify({letters}, null, '\t') + '\n');
console.log(letters.map((l) => `${l.ch} ${l.side}/${l.order} ${l.feed}`).join('\n'));
