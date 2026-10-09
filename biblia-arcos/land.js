const topo = require('topojson-client'); const fs = require('fs');
const t = JSON.parse(fs.readFileSync('node_modules/world-atlas/land-10m.json'));
const land = topo.feature(t, t.objects.land);
const B = { x0: 6, x1: 60, y0: 12, y1: 47 };
function clip(ring) { // Sutherland-Hodgman
  const edges = [p => p[0] >= B.x0, p => p[0] <= B.x1, p => p[1] >= B.y0, p => p[1] <= B.y1];
  const inter = [(a, b) => { const t = (B.x0 - a[0]) / (b[0] - a[0]); return [B.x0, a[1] + t * (b[1] - a[1])]; },
    (a, b) => { const t = (B.x1 - a[0]) / (b[0] - a[0]); return [B.x1, a[1] + t * (b[1] - a[1])]; },
    (a, b) => { const t = (B.y0 - a[1]) / (b[1] - a[1]); return [a[0] + t * (b[0] - a[0]), B.y0]; },
    (a, b) => { const t = (B.y1 - a[1]) / (b[1] - a[1]); return [a[0] + t * (b[0] - a[0]), B.y1]; }];
  let out = ring;
  for (let e = 0; e < 4; e++) { const inp = out; out = []; if (!inp.length) break;
    for (let i = 0; i < inp.length; i++) { const cur = inp[i], prev = inp[(i + inp.length - 1) % inp.length];
      const ci = edges[e](cur), pi = edges[e](prev);
      if (ci) { if (!pi) out.push(inter[e](prev, cur)); out.push(cur); } else if (pi) out.push(inter[e](prev, cur)); } }
  return out;
}
const fine = p => p[0] > 32.5 && p[0] < 37.5 && p[1] > 28.5 && p[1] < 34.8;
const rings = [];
const geoms = land.features ? land.features.map(f => f.geometry) : [land.geometry];
for (const g of geoms) for (const poly of (g.type === "Polygon" ? [g.coordinates] : g.coordinates)) for (const ring of poly) {
  const c = clip(ring); if (c.length < 4) continue;
  const out = []; let last = null;
  for (const p of c) { const tol = fine(p) ? 0.012 : 0.05;
    if (!last || Math.hypot(p[0] - last[0], p[1] - last[1]) >= tol) { out.push([+p[0].toFixed(3), +p[1].toFixed(3)]); last = p; } }
  if (out.length >= 4) rings.push(out.flat());
}
fs.writeFileSync(process.argv[2], JSON.stringify(rings));
console.log(rings.length, 'rings', rings.reduce((a, r) => a + r.length / 2, 0), 'points');
