# Book tooling

- `book_style.py`   — shared matplotlib style (book palette + Sarabun font), exports SVG to ../docs/charts/
- `charts_chN.py`   — per-chapter chart generators (run: `python3 charts_chN.py`)
- `render-chapter.js` — render one chapter HTML → PDF (offline). Usage: `node render-chapter.js statarb-ch3`
- `fonts/`          — Sarabun TTFs used by matplotlib

Vendored web assets (offline, no CDN — chromium blocks external CDNs):
- `../docs/vendor/katex/`  — KaTeX 0.16.11 (CSS/JS/fonts)
- `../docs/vendor/fonts/`  — Sarabun @font-face (sarabun.css) for HTML/PDF
