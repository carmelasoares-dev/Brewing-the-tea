#!/usr/bin/env python3
"""Build index.html for Netlify from src/page.html + data/*.json.

Usage: python3 build.py
The page source (src/page.html) is the same page the Claude dashboard uses.
This script swaps the dashboard runtime for a tiny local one and embeds the data,
so index.html is one self-contained file.
"""
import json, os, datetime
here = os.path.dirname(os.path.abspath(__file__))
rd = lambda p: open(os.path.join(here, p), encoding='utf-8').read()

trends = json.loads(rd('data/trends.json'))
language = json.loads(rd('data/language.json'))
latest = max((r['week'] for r in trends), default='')
try:
    stamp = datetime.date.fromisoformat(latest).strftime('%-d %b %Y')
except ValueError:
    stamp = latest

page = rd('src/page.html')
for drop in ('<meta name="dash-one-writer">\n', '<meta name="dash-form" content="dashboard">\n', '#dash-root { --dash-gutter: 0; }'):
    page = page.replace(drop, '')
page = page.replace('<div class="tr-refresh">', '<div class="tr-refresh" hidden>')
page = page.replace('<span>The Tea by Apparent Social</span>', f'<span>The Tea by Apparent Social · updated {stamp}</span>')

data = json.dumps({'trends': trends, 'language': language}, ensure_ascii=False).replace('<', '\\u003c')
d3 = rd('vendor/d3.min.js').replace('</script', '<\\/script')

shim = r"""
window.claude = { use: async () => null };
window.dash = (function () {
  const DATA = window.__TEA_DATA__, calcs = {}, draws = {}, cache = {};
  const api = {
    colors: ['#FA0500', '#6B0000', '#242322', '#B5ADA7'],
    data(id) {
      if (id in DATA) return { status: 'ok', data: DATA[id], columns: DATA[id].length ? Object.keys(DATA[id][0]) : [], refreshing: false, truncated: false };
      const c = calcs[id];
      if (c) { if (!(id in cache)) cache[id] = c.fn(...c.inputs.map((i) => api.data(i).data)); return { status: 'ok', data: cache[id], refreshing: false, truncated: false }; }
      return { status: 'missing', data: [] };
    },
    calc(id, o) { calcs[id] = o; }, loader() {}, onData(fn) { fn(); },
    draw(name, fn) { if (fn === undefined) { run(name); return; } draws[name] = fn; },
    params: () => ({}), setParams() {}, resetParams() {}, setLink() {}, refresh() {}
  };
  function run(name) {
    const f = draws[name]; if (!f) return;
    document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
      if (typeof f === 'function') { f(el); return; }
      if (!el.__made) { el.textContent = ''; el.__made = { v: f.mount ? f.mount(el) : undefined }; }
      if (f.update) f.update(el, el.__made.v);
    });
  }
  api._start = () => {
    Object.keys(draws).forEach(run);
    let t; window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(() => ['curve', 'hooktypes'].forEach(run), 150); });
  };
  return api;
})();
"""
icon = "data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 40 180 182%27%3E%3Cpath fill=%27%23FA0500%27 d=%27M117.701 102.257V152.332C114.032 126.392 93.4232 105.876 67.3856 102.257H117.701ZM175.956 217.261V159.589C175.956 95.9478 124.198 44.3564 60.3506 44.3564H2.32758V102.257H50.9032C22.1398 106.256 0 130.869 0 160.64C0 193.199 26.4815 219.595 59.146 219.595C88.9835 219.595 113.653 197.572 117.704 168.947V217.265H175.956V217.261Z%27/%3E%3C/svg%3E"
html = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Tea · social trend radar · Apparent</title>
<link rel="icon" href="{icon}">
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter+Tight:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script>{d3}</script>
<style>
html, body {{ margin: 0; background: #F7F4F2; }}
.tr .dash-select {{ -webkit-appearance: none; appearance: none; padding: 6px 30px 6px 12px; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23FA0500' stroke-width='1.5' fill='none'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 12px center; }}
.tr h1, .tr h2, .tr h3, .tr-rank, .tr-num, .tr-hook q {{ font-weight: 800; }}
</style>
<script>window.__TEA_DATA__ = {data};</script>
<script>{shim}</script>
</head>
<body>
<div id="dash-root">
{page}
</div>
<script>dash._start();</script>
</body>
</html>
"""
open(os.path.join(here, 'index.html'), 'w', encoding='utf-8').write(html)
print(f'Built index.html ({len(html):,} bytes) for {latest}: {len(trends)} trend rows, {len(language)} language rows')
