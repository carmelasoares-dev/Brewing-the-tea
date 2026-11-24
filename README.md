# Brewing-the-tea

What's happening on social this week, and what brands can do with it.

The Tea is Apparent's social trend radar, published at Netlify from `index.html`.

- `src/page.html`: the page (the same one the Claude dashboard uses)
- `data/trends.json`, `data/language.json`: trend, hook and language data, one set of rows per update
- `vendor/d3.min.js`: charting library (d3 v7, ISC licence)
- `build.py`: run `python3 build.py` to rebuild `index.html` from the above

A Claude scheduled task updates `data/`, rebuilds and pushes every weekday morning (Sydney). Netlify republishes on every push to `main`.
