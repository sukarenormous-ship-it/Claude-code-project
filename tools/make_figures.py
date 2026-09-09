#!/usr/bin/env python3
"""วาดภาพประกอบ (inline SVG) จากข้อมูลชุดเดียวกับที่สคริปต์ทวนตัวเลขใช้ แล้วเขียนลงไฟล์ HTML
ระหว่าง marker  <!-- FIG:<ชื่อ>:BEGIN --> … <!-- FIG:<ชื่อ>:END -->

เหตุผล: ภาพที่มีตัวเลข (ความชัน, จุด, ระยะ) ต้องมาจากข้อมูลเดียวกับข้อความ ไม่ใช่วาดมือแล้วเดา
ใช้:  python3 tools/make_figures.py            → เขียนทุกภาพ (idempotent)
      python3 tools/make_figures.py --check    → ตรวจว่า SVG ในไฟล์ตรงกับที่สคริปต์สร้าง (exit 1 ถ้าไม่ตรง)
ต้องมี numpy
"""
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FIGS = {}  # (file, name) -> svg string
NUMS = {}  # name -> dict ตัวเลขที่ภาพใช้ (ให้ math_figures.py เทียบกับข้อความ)

FONT = 'font-family="Sarabun"'
INK, INK2, GRID, AXIS = "#374151", "#6b7280", "#e5e7eb", "#9ca3af"
BLUE, RED, GREEN, PURPLE, AMBER = "#2563eb", "#dc2626", "#16a34a", "#7c3aed", "#d97706"


def f(v):
    return f"{v:.1f}"


def fig(file, name):
    def deco(fn):
        FIGS[(file, name)] = fn
        return fn
    return deco


# ── 2·A §1.4 OLS vs PCA — ย่อระยะแนวตั้ง vs ระยะตั้งฉาก บนจุดชุดเดียวกัน ─────────
def ols_pca_data():
    rng = np.random.default_rng(3)
    n = 22
    x = rng.normal(0, 1.0, n)                     # ผลตอบแทน BTC (%) — สเกลเท่ากันทั้งสองแกน
    y = 0.70 * x + rng.normal(0, 0.95, n)         # ผลตอบแทน ETH (%) — noise มากพอให้สองเส้นแยกกันชัด
    x -= x.mean(); y -= y.mean()
    b_ols = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    C = np.cov(np.vstack([x, y]), ddof=1)
    w, v = np.linalg.eigh(C)
    pc1 = v[:, -1]
    b_pca = pc1[1] / pc1[0]
    b_rev = 1 / (np.cov(x, y, ddof=1)[0, 1] / np.var(y, ddof=1))   # OLS ของ x บน y แล้วสลับกลับ
    return x, y, b_ols, b_pca, b_rev


@fig("math-part4.html", "ols-vs-pca")
def fig_ols_vs_pca():
    x, y, b_ols, b_pca, b_rev = ols_pca_data()
    NUMS["ols-vs-pca"] = dict(b_ols=b_ols, b_pca=b_pca, b_rev=b_rev)
    W, H = 560, 300
    pw, ph = 230, 200          # ขนาดแต่ละพาเนล
    ox = [40, 310]             # มุมซ้ายบนของแต่ละพาเนล (x)
    oy = 48
    L = 3.0                    # ช่วงแกน ±3
    def sx(o, val): return o + (val + L) / (2 * L) * pw
    def sy(val): return oy + (L - val) / (2 * L) * ph
    out = [f'<svg class="d" viewBox="0 0 {W} {H}" role="img" aria-label="OLS ย่อระยะแนวตั้ง PCA ย่อระยะตั้งฉาก บนจุดข้อมูลชุดเดียวกัน — ได้เส้นคนละเส้น">']
    out.append(f'<defs><filter id="fsoft" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="1.4" stdDeviation="1.4" flood-color="#111827" flood-opacity="0.18"/></filter></defs>')
    titles = [("OLS — ย่อระยะแนวตั้ง", RED, b_ols, "vertical"), ("PCA (= TLS) — ย่อระยะตั้งฉาก", GREEN, b_pca, "orth")]
    for k, (title, col, slope, mode) in enumerate(titles):
        o = ox[k]
        out.append(f'<text x="{o + pw/2:.0f}" y="{oy-22}" text-anchor="middle" {FONT} font-size="12.5" font-weight="700" fill="{INK}">{title}</text>')
        out.append(f'<text x="{o + pw/2:.0f}" y="{oy-8}" text-anchor="middle" {FONT} font-size="10" fill="{INK2}">ความชัน = {slope:.2f}</text>')
        # grid + axes
        out.append(f'<g stroke="{GRID}" stroke-width="1">' + "".join(f'<line x1="{sx(o,g):.1f}" y1="{oy}" x2="{sx(o,g):.1f}" y2="{oy+ph}"/><line x1="{o}" y1="{sy(g):.1f}" x2="{o+pw}" y2="{sy(g):.1f}"/>' for g in (-2, -1, 1, 2)) + '</g>')
        out.append(f'<line x1="{o}" y1="{sy(0):.1f}" x2="{o+pw}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.2"/>')
        out.append(f'<line x1="{sx(o,0):.1f}" y1="{oy}" x2="{sx(o,0):.1f}" y2="{oy+ph}" stroke="{AXIS}" stroke-width="1.2"/>')
        out.append(f'<text x="{o+pw}" y="{oy+ph+13}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">X — ผลตอบแทน BTC (%)</text>')
        out.append(f'<text x="{o+2}" y="{oy+9}" {FONT} font-size="9.5" fill="{INK2}">Y — ETH (%)</text>')
        # เส้นอีกวิธี (จาง) เพื่อให้เห็นว่าไม่ทับกัน
        other = b_pca if mode == "vertical" else b_ols
        ocol = GREEN if mode == "vertical" else RED
        xs = np.array([-L, L]); xs_o = xs.copy()
        out.append(f'<line x1="{sx(o,-L):.1f}" y1="{sy(-L*other):.1f}" x2="{sx(o,L):.1f}" y2="{sy(L*other):.1f}" stroke="{ocol}" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.55"/>')
        # ระยะ
        for xi, yi in zip(x, y):
            if mode == "vertical":
                out.append(f'<line x1="{sx(o,xi):.1f}" y1="{sy(yi):.1f}" x2="{sx(o,xi):.1f}" y2="{sy(slope*xi):.1f}" stroke="{col}" stroke-width="1.3" opacity="0.9"/>')
            else:
                # ฉายจุดลงบนเส้นผ่านศูนย์ทิศ (1, slope)
                d = np.array([1, slope]) / np.hypot(1, slope)
                t = xi * d[0] + yi * d[1]
                px, py = t * d[0], t * d[1]
                out.append(f'<line x1="{sx(o,xi):.1f}" y1="{sy(yi):.1f}" x2="{sx(o,px):.1f}" y2="{sy(py):.1f}" stroke="{col}" stroke-width="1.3" opacity="0.9"/>')
        # เส้นหลัก
        out.append(f'<line x1="{sx(o,-L):.1f}" y1="{sy(-L*slope):.1f}" x2="{sx(o,L):.1f}" y2="{sy(L*slope):.1f}" stroke="{col}" stroke-width="2.75" stroke-linecap="round" filter="url(#fsoft)"/>')
        # จุด
        out.append(f'<g fill="{BLUE}" opacity="0.85">' + "".join(f'<circle cx="{sx(o,xi):.1f}" cy="{sy(yi):.1f}" r="3.6"/>' for xi, yi in zip(x, y)) + '</g>')
        # callout จุดตัวอย่าง (จุดที่ระยะยาวสุด)
        if mode == "vertical":
            i = int(np.argmax(np.abs(y - slope * x)))
            xi, yi = x[i], y[i]
            out.append(f'<text x="{sx(o,xi)+6:.1f}" y="{(sy(yi)+sy(slope*xi))/2:.1f}" {FONT} font-size="9.5" fill="{RED}" font-weight="600">yᵢ − ŷᵢ</text>')
        else:
            d = np.array([1, slope]) / np.hypot(1, slope)
            t = x * d[0] + y * d[1]
            i = int(np.argmax(np.hypot(x - t * d[0], y - t * d[1])))
            xi, yi = x[i], y[i]
            px, py = t[i] * d[0], t[i] * d[1]
            # เครื่องหมายมุมฉากที่ตีนของระยะตั้งฉาก (ในหน่วยข้อมูล ยาว 0.18)
            u = np.array([xi - px, yi - py]); u = u / np.linalg.norm(u) * 0.18
            dd = d * 0.18 * (1 if (xi - px) * (-d[1]) + (yi - py) * d[0] >= 0 else 1)
            c1 = (px + u[0], py + u[1]); c2 = (px + u[0] - dd[0], py + u[1] - dd[1]); c3 = (px - dd[0], py - dd[1])
            out.append(f'<polyline points="{sx(o,c1[0]):.1f},{sy(c1[1]):.1f} {sx(o,c2[0]):.1f},{sy(c2[1]):.1f} {sx(o,c3[0]):.1f},{sy(c3[1]):.1f}" fill="none" stroke="{GREEN}" stroke-width="1"/>')
            out.append(f'<text x="{sx(o,xi)+6:.1f}" y="{sy(yi)-4:.1f}" {FONT} font-size="9.5" fill="{GREEN}" font-weight="600">dᵢ ⊥ เส้น</text>')
    # legend
    ly = H - 14
    out.append(f'<line x1="40" y1="{ly}" x2="64" y2="{ly}" stroke="{RED}" stroke-width="2.5"/><text x="70" y="{ly+3.5}" {FONT} font-size="10" fill="{INK}">เส้น OLS (Y บน X)</text>')
    out.append(f'<line x1="200" y1="{ly}" x2="224" y2="{ly}" stroke="{GREEN}" stroke-width="2.5"/><text x="230" y="{ly+3.5}" {FONT} font-size="10" fill="{INK}">เส้น PC1 = TLS</text>')
    out.append(f'<line x1="330" y1="{ly}" x2="354" y2="{ly}" stroke="{INK2}" stroke-width="1.2" stroke-dasharray="4 4"/><text x="360" y="{ly+3.5}" {FONT} font-size="10" fill="{INK}">อีกวิธีวางทาบ (จาง) — ไม่ทับกัน</text>')
    out.append('</svg>')
    return "\n".join(out)


def render_all():
    return {(fl, nm): fn() for (fl, nm), fn in FIGS.items()}


def main():
    check = "--check" in sys.argv
    bad = 0
    for (fl, nm), svg in render_all().items():
        p = os.path.join(DOCS, fl)
        s = open(p, encoding="utf-8").read()
        b, e = f"<!-- FIG:{nm}:BEGIN -->", f"<!-- FIG:{nm}:END -->"
        if b not in s or e not in s:
            print(f"❌ {fl}: ไม่พบ marker {nm}"); bad += 1; continue
        new = re.sub(re.escape(b) + r".*?" + re.escape(e), lambda m: b + "\n" + svg + "\n" + e, s, flags=re.S)
        if check:
            if new != s:
                print(f"❌ {fl} · {nm}: SVG ในไฟล์ไม่ตรงกับที่สคริปต์สร้าง — รัน python3 tools/make_figures.py"); bad += 1
        elif new != s:
            open(p, "w", encoding="utf-8").write(new); print(f"✏️  {fl} · {nm} เขียนแล้ว")
    for nm, d in NUMS.items():
        print(f"   {nm}: " + " ".join(f"{k}={v:.4f}" for k, v in d.items()))
    print(f"ภาพ {len(FIGS)} ชิ้น · ปัญหา {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
