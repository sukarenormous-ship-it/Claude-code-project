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
    pw, ph = 200, 200          # ขนาดแต่ละพาเนล — px ต่อหน่วยเท่ากันสองแกน ไม่งั้นมุมฉากบนจอไม่ฉาก
    ox = [55, 320]             # มุมซ้ายบนของแต่ละพาเนล (x)
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



# ── เครื่องมือวาดร่วม ────────────────────────────────────────────────────────────
def frame(out, x0, y0, w, h, xt, yt, xlab="", ylab="", grid_y=True):
    """แกน + grid ถอยหลัง · xt/yt = list ของ (ค่า, ป้าย) · คืนฟังก์ชันแปลงพิกัด"""
    (xa, xb), (ya, yb) = (xt[0][0], xt[-1][0]), (yt[0][0], yt[-1][0])
    def sx(v): return x0 + (v - xa) / (xb - xa) * w
    def sy(v): return y0 + h - (v - ya) / (yb - ya) * h
    if grid_y:
        out.append(f'<g stroke="{GRID}" stroke-width="1">' + "".join(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}"/>' for v, _ in yt[1:]) + "</g>")
    out.append(f'<line x1="{x0}" y1="{y0+h}" x2="{x0+w}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.2"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.2"/>')
    for v, lab in xt:
        out.append(f'<text x="{sx(v):.1f}" y="{y0+h+13}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">{lab}</text>')
    for v, lab in yt:
        out.append(f'<text x="{x0-5}" y="{sy(v)+3.5:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">{lab}</text>')
    if xlab: out.append(f'<text x="{x0+w}" y="{y0+h+27}" text-anchor="end" {FONT} font-size="10" fill="{INK2}">{xlab}</text>')
    if ylab: out.append(f'<text x="{x0-2}" y="{y0-8}" {FONT} font-size="10" fill="{INK2}">{ylab}</text>')
    return sx, sy


def polyline(out, pts, col, width=2.5, dash="", shadow=True):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    fl = ' filter="url(#fsoft)"' if shadow else ""
    out.append(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{extra}{fl}/>')


def title(out, W, text, sub=""):
    out.append(f'<text x="{W/2:.0f}" y="18" text-anchor="middle" {FONT} font-size="12.5" font-weight="700" fill="{INK}">{text}</text>')
    if sub: out.append(f'<text x="{W/2:.0f}" y="32" text-anchor="middle" {FONT} font-size="10" fill="{INK2}">{sub}</text>')


def legend(out, items, x, y):
    for col, lab, dash in items:
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{x}" y1="{y}" x2="{x+22}" y2="{y}" stroke="{col}" stroke-width="2.5"{extra}/><text x="{x+27}" y="{y+3.5}" {FONT} font-size="10" fill="{INK}">{lab}</text>')
        x += 27 + 6.2 * len(lab) + 18


def svg_open(W, H, label):
    return [f'<svg class="d" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">',
            '<defs><filter id="fsoft" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="1.4" stdDeviation="1.4" flood-color="#111827" flood-opacity="0.18"/></filter></defs>']


# ── 2·A §2.1 rolling β 60 วัน — OLS vs Theil-Sen เมื่อวัน jump เข้า/ออกหน้าต่าง ─────────────
def rolling_beta_data():
    from scipy.stats import theilslopes
    rng = np.random.default_rng(11); T, W, J = 250, 60, 120
    m = rng.normal(0, 0.01, T); s = 1.2 * m + rng.normal(0, 0.008, T)
    m[J], s[J] = -0.07, -0.20
    def beta(x, y): return np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    days = np.arange(W - 1, T)
    ols = np.array([beta(m[d - W + 1:d + 1], s[d - W + 1:d + 1]) for d in days])
    ts = np.array([theilslopes(s[d - W + 1:d + 1], m[d - W + 1:d + 1])[0] for d in days])
    return days, ols, ts, J, W


@fig("math-part4.html", "rolling-beta")
def fig_rolling_beta():
    days, ols, ts, J, W = rolling_beta_data()
    NUMS["rolling-beta"] = dict(ols_before=ols[days == J - 1][0], ols_jump=ols[days == J][0], ols_after=ols[days == J + W][0], ts_jump=ts[days == J][0])
    Wd, H = 560, 280
    out = svg_open(Wd, H, "rolling β 60 วัน: OLS กระโดดขึ้นวันที่ 120 ค้าง 60 วัน แล้วตกวันที่ 180 ส่วน Theil-Sen แทบไม่ขยับ")
    title(out, Wd, "β บนหน้าต่างเลื่อน 60 วัน — ขั้นบันไดที่กว้างพอดี 60 วันคือลายเซ็นของหน้าต่าง", "β จริง = 1.2 ทั้งปี · วันที่ 120 ตลาด −7% หุ้น −20% วันเดียว")
    x0, y0, w, h = 50, 46, 480, 180
    sx, sy = frame(out, x0, y0, w, h, [(60, "60"), (120, "120"), (180, "180"), (240, "240")], [(0.8, "0.8"), (1.2, "1.2"), (1.6, "1.6"), (2.0, "2.0"), (2.4, "2.4")], xlab="วันที่ (วันทำการ)", ylab="β")
    out.append(f'<line x1="{x0}" y1="{sy(1.2):.1f}" x2="{x0+w}" y2="{sy(1.2):.1f}" stroke="{INK2}" stroke-width="1" stroke-dasharray="4 4"/>')
    out.append(f'<text x="{x0+w-2}" y="{sy(1.2)+11:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">β จริง 1.2</text>')
    # แถบ 60 วันที่วัน jump อยู่ในหน้าต่าง
    out.append(f'<rect x="{sx(J):.1f}" y="{y0}" width="{sx(J+W)-sx(J):.1f}" height="{h}" fill="{RED}" opacity="0.06"/>')
    out.append(f'<text x="{(sx(J)+sx(J+W))/2:.1f}" y="{y0+12}" text-anchor="middle" {FONT} font-size="9.5" fill="{RED}">วัน jump อยู่ในหน้าต่าง (60 วัน)</text>')
    polyline(out, [(sx(d), sy(v)) for d, v in zip(days, ts)], GREEN, 2.2, shadow=False)
    polyline(out, [(sx(d), sy(v)) for d, v in zip(days, ols)], RED, 2.5)
    # callouts
    bj = ols[days == J][0]; ba = ols[days == J + W][0]
    out.append(f'<circle cx="{sx(J):.1f}" cy="{sy(bj):.1f}" r="4" fill="#fff" stroke="{PURPLE}" stroke-width="2.2"/>')
    out.append(f'<text x="{sx(J)-6:.1f}" y="{sy(bj)-8:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">วันที่ 120: {bj:.2f} — ขึ้นวันเดียว</text>')
    out.append(f'<circle cx="{sx(J+W):.1f}" cy="{sy(ba):.1f}" r="4" fill="#fff" stroke="{PURPLE}" stroke-width="2.2"/>')
    out.append(f'<text x="{sx(J+W)+7:.1f}" y="{sy(ba)+14:.1f}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">วันที่ 180: {ba:.2f} — ตกวันเดียว ไม่มีข่าว</text>')
    legend(out, [(RED, "OLS", ""), (GREEN, "Theil-Sen (median ของความชันทุกคู่)", "")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── 2·A §1.6 ฐานจากความสุ่ม — histogram ของ λ₁ จาก noise ล้วน 1,000 ชุด ─────────────
def mp_hist_data():
    p6, nn = 5, 250
    r_ = np.random.default_rng(1)
    arr = np.array([np.linalg.eigvalsh(np.corrcoef(r_.standard_normal((nn, p6)).T))[-1] for _ in range(1000)])
    r2 = np.random.default_rng(2); f1 = r2.standard_normal(nn); f2 = r2.standard_normal(nn)
    Xs = np.outer(f1, np.full(p6, .8)) + np.outer(f2, .2 * np.array([-2, -1, 0, 1, 2.])) + r2.standard_normal((nn, p6))
    lam_struct = np.linalg.eigvalsh(np.corrcoef(Xs.T))[::-1]
    lam_noise0 = np.linalg.eigvalsh(np.corrcoef(np.random.default_rng(0).standard_normal((nn, p6)).T))[-1]
    lp = (1 + np.sqrt(p6 / nn)) ** 2
    return arr, np.percentile(arr, 95), lam_struct, lam_noise0, lp


@fig("math-part4.html", "mp-hist")
def fig_mp_hist():
    arr, q95, lam_s, lam_n0, lp = mp_hist_data()
    NUMS["mp-hist"] = dict(q95=q95, lam1_struct=lam_s[0], lam2_struct=lam_s[1], lam_noise0=lam_n0, lp=lp)
    Wd, H = 560, 280
    out = svg_open(Wd, H, "histogram ของ eigenvalue ใหญ่สุดจากข้อมูลสุ่มล้วน 1,000 ชุด กับเส้นเปอร์เซ็นไทล์ 95 และ λ ของข้อมูลจริง")
    title(out, Wd, "λ₁ ของ noise ล้วน (5 ตัวแปร × 250 วัน · 1,000 ชุด) — โครงสร้างต้องโผล่พ้นนี้", "ฐานจากความสุ่ม: ก่อนเรียกอะไรว่า factor ให้ดูว่า noise ทำได้แค่ไหน")
    x0, y0, w, h = 50, 46, 480, 175
    lo, hi, nb = 1.10, 1.50, 32
    cnt, edges = np.histogram(arr, bins=nb, range=(lo, hi))
    xt = [(1.1, "1.10"), (1.2, "1.20"), (1.3, "1.30"), (1.4, "1.40"), (1.5, "1.50")]
    ymax = int(np.ceil(cnt.max() / 20) * 20)
    sx, sy = frame(out, x0, y0, w, h, xt, [(0, "0"), (ymax // 2, str(ymax // 2)), (ymax, str(ymax))], xlab="eigenvalue ใหญ่สุด (λ₁)", ylab="จำนวนชุด")
    for c, a, b in zip(cnt, edges[:-1], edges[1:]):
        if c: out.append(f'<rect x="{sx(a)+0.5:.1f}" y="{sy(c):.1f}" width="{sx(b)-sx(a)-1:.1f}" height="{sy(0)-sy(c):.1f}" fill="{BLUE}" opacity="0.55"/>')
    def vline(v, col, lab, dy, anchor="start", dx=4):
        out.append(f'<line x1="{sx(v):.1f}" y1="{y0}" x2="{sx(v):.1f}" y2="{y0+h}" stroke="{col}" stroke-width="1.6" stroke-dasharray="5 3"/>')
        out.append(f'<text x="{sx(v)+dx:.1f}" y="{y0+dy}" text-anchor="{anchor}" {FONT} font-size="9.5" fill="{col}" font-weight="700">{lab}</text>')
    vline(q95, PURPLE, f"เปอร์เซ็นไทล์ 95 = {q95:.3f}", 14, "end", -4)
    vline(lp, INK2, f"λ₊ ของ Marchenko-Pastur = {lp:.3f} (ลิมิต p, n ใหญ่)", 14)
    vline(lam_n0, AMBER, f"noise ชุด seed 0: {lam_n0:.3f} — ผ่านเกณฑ์ทั้งที่ไม่มีอะไร", 46)
    # λ₁ ของข้อมูลที่มีโครงสร้างอยู่นอกช่วงกราฟ → ลูกศรที่ขอบขวา
    ya = y0 + h * 0.74
    out.append(f'<line x1="{sx(1.42):.1f}" y1="{ya:.1f}" x2="{x0+w-4}" y2="{ya:.1f}" stroke="{GREEN}" stroke-width="2.2" stroke-linecap="round"/>')
    out.append(f'<polygon points="{x0+w-2},{ya:.1f} {x0+w-10},{ya-4:.1f} {x0+w-10},{ya+4:.1f}" fill="{GREEN}"/>')
    out.append(f'<text x="{x0+w-4}" y="{ya-8:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{GREEN}" font-weight="700">ข้อมูลมีปัจจัยจริง: λ₁ = {lam_s[0]:.3f} — อยู่นอกกราฟไปทางขวาไกล</text>')
    out.append(f'<text x="{x0+w-4}" y="{ya+14:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{GREEN}">(λ₂ = {lam_s[1]:.3f} ต้องเทียบฐานที่ปอกชั้นแรกออกแล้ว — ตาราง 3)</text>')
    out.append("</svg>")
    return "\n".join(out)


# ── 2·A §1.7 residual สะสม — noise ล้วนก็เดินเป็น random walk · OU จริงวนรอบศูนย์ ─────────
def cum_resid_data():
    n7 = 2500
    def _ports(Rm, k=2):
        sg = Rm.std(0, ddof=1); Cm = np.corrcoef(Rm.T); l_, V_ = np.linalg.eigh(Cm); V_ = V_[:, ::-1]
        F_ = [Rm @ ((V_[:, j] * np.sign(V_[:, j].sum() if j == 0 else V_[-1, j])) / sg) for j in range(k)]
        return np.column_stack(F_)
    def _data(p_, seed=2):
        r_ = np.random.default_rng(seed); g1 = r_.standard_normal(n7); g2 = r_.standard_normal(n7); En = r_.standard_normal((n7, p_))
        L2_ = .2 * np.array([-2, -1, 0, 1, 2.])
        return g1, g2, L2_, np.outer(g1, np.full(p_, .8)) + np.outer(g2, L2_) + En
    g1, g2, L2, R5 = _data(5)
    FA = _ports(R5[:, 1:]); XA = np.column_stack([np.ones(n7), FA]); bA = np.linalg.lstsq(XA, R5[:, 0], rcond=None)[0]
    XcA = np.cumsum(R5[:, 0] - XA @ bA)
    r_ = np.random.default_rng(3); Xou = np.zeros(n7); et = r_.standard_normal(n7) * np.sqrt(1 - .9 ** 2)
    for t_ in range(1, n7): Xou[t_] = .9 * Xou[t_ - 1] + et[t_]
    Rb = R5.copy(); Rb[:, 0] = .8 * g1 + L2[0] * g2 + np.diff(np.concatenate([[0], Xou]))
    Fb = _ports(Rb[:, 1:]); Xb = np.column_stack([np.ones(n7), Fb]); bb = np.linalg.lstsq(Xb, Rb[:, 0], rcond=None)[0]
    XcB = np.cumsum(Rb[:, 0] - Xb @ bb)
    return XcA, XcB


@fig("math-part4.html", "cum-resid")
def fig_cum_resid():
    XcA, XcB = cum_resid_data()
    NUMS["cum-resid"] = dict(A_min=XcA.min(), A_max=XcA.max(), B_min=XcB.min(), B_max=XcB.max())
    Wd, H = 560, 290
    out = svg_open(Wd, H, "residual สะสม 2,500 วัน: กรณี A noise ล้วนเดินเป็น random walk ไปไกล กรณี B ที่ฝัง OU ไว้วนรอบศูนย์")
    title(out, Wd, "residual สะสม X = Σε — เส้นไหน 'แกว่งรอบเส้น' จริง?", "หุ้นตัวที่ 1 หัก factor จากอีก 4 ตัว · 2,500 วัน · ข้อมูลชุดเดียวกับตาราง 2 และ 3")
    x0, y0, w, h = 50, 46, 480, 190
    lo = float(np.floor(min(XcA.min(), XcB.min()) / 10) * 10); hi = float(np.ceil(max(XcA.max(), XcB.max()) / 10) * 10)
    yt = [(v, f"{v:+.0f}".replace("-", "−").replace("+0", "0")) for v in np.arange(lo, hi + 1, 10)]
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (500, "500"), (1000, "1,000"), (1500, "1,500"), (2000, "2,000"), (2500, "2,500")], yt, xlab="วันที่", ylab="X (หน่วย %-วัน)")
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{INK2}" stroke-width="1" stroke-dasharray="4 4"/>')
    step = 5
    polyline(out, [(sx(i), sy(v)) for i, v in enumerate(XcB) if i % step == 0], GREEN, 1.8, shadow=False)
    polyline(out, [(sx(i), sy(v)) for i, v in enumerate(XcA) if i % step == 0], RED, 2.2)
    im = int(np.argmin(XcA))
    out.append(f'<circle cx="{sx(im):.1f}" cy="{sy(XcA[im]):.1f}" r="4" fill="#fff" stroke="{PURPLE}" stroke-width="2.2"/>')
    out.append(f'<text x="{x0+6}" y="{y0+14}" {FONT} font-size="9.5" fill="{RED}" font-weight="700">A: noise ล้วน เดินไปถึง −{abs(XcA.min()):.0f} และ +{XcA.max():.0f} — random walk ไม่ใช่ mean reversion</text>')
    out.append(f'<text x="{x0+6}" y="{y0+28}" {FONT} font-size="9.5" fill="{GREEN}" font-weight="700">B: ฝัง OU (φ = 0.9) — วนรอบศูนย์ แต่ก็เคยไปถึง −{abs(XcB.min()):.0f} (noise ของอีก 4 หุ้นรั่วเข้ามา)</text>')
    legend(out, [(RED, "กรณี A — residual ของ noise ล้วน", ""), (GREEN, "กรณี B — residual ที่มี OU จริงซ่อนอยู่", "")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── 2·D §9.1 first passage 2SD→0 ของ OU φ = 0.9048 — histogram กับครึ่งชีวิต ─────────────
def first_passage_data():
    rng = np.random.default_rng(1); phi = 0.9048; hl = -np.log(2) / np.log(phi)
    n = 200_000; x = np.full(n, 2.0); t = np.zeros(n); alive = np.ones(n, bool); sig = np.sqrt(1 - phi ** 2)
    for k in range(1, 5001):
        x = phi * x + sig * rng.standard_normal(n)
        hit = alive & (x <= 0); t[hit] = k; alive &= ~hit
        if not alive.any(): break
    return t, hl


@fig("math-part9.html", "first-passage")
def fig_first_passage():
    t, hl = first_passage_data()
    med, mean, p90, p95 = np.median(t), t.mean(), np.percentile(t, 90), np.percentile(t, 95)
    NUMS["first-passage"] = dict(hl=hl, median=med, mean=mean, p90=p90, p95=p95, le_hl=(t <= hl).mean())
    Wd, H = 560, 290
    out = svg_open(Wd, H, "histogram ของเวลาที่ spread เดินจาก 2SD กลับถึงศูนย์ครั้งแรก มีหางยาวไปทางขวา ครึ่งชีวิตอยู่ทางซ้ายของค่ากลาง")
    title(out, Wd, f"เวลาปิดไม้จริง (first passage 2SD → 0) เทียบครึ่งชีวิต {hl:.2f} วัน", "OU φ = 0.9048 · จำลอง 200,000 ไม้ · ครึ่งชีวิตบอกว่า 'หุบครึ่งทาง' ไม่ใช่ 'ถึงศูนย์'")
    x0, y0, w, h = 50, 46, 480, 175
    xmax = 60; cnt, edges = np.histogram(t, bins=60, range=(0, xmax)); frac = cnt / len(t) * 100
    ymax = float(np.ceil(frac.max()))
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (10, "10"), (20, "20"), (30, "30"), (40, "40"), (50, "50"), (60, "60+")], [(0, "0%"), (ymax / 2, f"{ymax/2:.0f}%"), (ymax, f"{ymax:.0f}%")], xlab="วันที่ spread แตะศูนย์ครั้งแรก", ylab="สัดส่วนไม้")
    for c, a, b in zip(frac, edges[:-1], edges[1:]):
        if c: out.append(f'<rect x="{sx(a)+0.5:.1f}" y="{sy(c):.1f}" width="{sx(b)-sx(a)-1:.1f}" height="{sy(0)-sy(c):.1f}" fill="{BLUE}" opacity="0.55"/>')
    tail = (t > xmax).mean() * 100
    out.append(f'<text x="{x0+w-6}" y="{y0+h-8}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">อีก {tail:.1f}% ของไม้นานกว่า 60 วัน →</text>')
    def vline(v, col, lab, dy):
        out.append(f'<line x1="{sx(v):.1f}" y1="{y0}" x2="{sx(v):.1f}" y2="{y0+h}" stroke="{col}" stroke-width="1.6" stroke-dasharray="5 3"/>')
        out.append(f'<text x="{x0+w-6}" y="{y0+dy}" text-anchor="end" {FONT} font-size="9.5" fill="{col}" font-weight="700">{lab}</text>')
    vline(hl, PURPLE, f"เส้นม่วง — ครึ่งชีวิต {hl:.2f} วัน: มีแค่ {(t<=hl).mean()*100:.0f}% ของไม้ปิดทัน", 14)
    vline(med, GREEN, f"เส้นเขียว — มัธยฐาน {med:.0f} วัน", 28)
    vline(mean, AMBER, f"เส้นเหลือง — ค่าเฉลี่ย {mean:.1f} วัน", 42)
    vline(p90, RED, f"เส้นแดง — 1 ใน 10 ไม้นานเกิน {p90:.0f} วัน", 56)
    out.append("</svg>")
    return "\n".join(out)


# ── 2·F §14.6 logistic — sigmoid กับ calibration plot ─────────────────────────────────────
def logistic_data():
    def fit_logit(Xf, y, C=1.0, iters=50):
        Xa = np.column_stack([np.ones(len(y)), Xf]); k = Xa.shape[1]
        theta = np.zeros(k); reg = np.eye(k); reg[0, 0] = 0
        for _ in range(iters):
            p = 1 / (1 + np.exp(-Xa @ theta)); g = C * Xa.T @ (p - y) + reg @ theta
            H = C * (Xa.T * (p * (1 - p))) @ Xa + reg; theta -= np.linalg.solve(H, g)
        return theta
    rng = np.random.default_rng(7); n = 400
    Xl = rng.normal(0, 1, (n, 2)); yl = (0.8 * Xl[:, 0] - 0.5 * Xl[:, 1] + rng.normal(0, 1, n) > 0).astype(int)
    th = fit_logit(Xl, yl)
    rg = np.random.default_rng(77); X2 = rg.normal(0, 1, (2000, 2)); y2 = (0.8 * X2[:, 0] - 0.5 * X2[:, 1] + rg.normal(0, 1, 2000) > 0).astype(int)
    p2 = 1 / (1 + np.exp(-(th[0] + X2 @ th[1:])))
    edges = [0, .2, .4, .6, .8, 1.01]; rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p2 >= lo) & (p2 < hi); rows.append((m.sum(), p2[m].mean(), y2[m].mean()))
    return th, rows


@fig("math-part11.html", "logistic")
def fig_logistic():
    th, rows = logistic_data()
    NUMS["logistic"] = dict(coef1=th[1], coef2=th[2], **{f"bin{i}_pred": r[1] for i, r in enumerate(rows)}, **{f"bin{i}_act": r[2] for i, r in enumerate(rows)})
    Wd, H = 560, 290
    out = svg_open(Wd, H, "ซ้าย: เส้น sigmoid ของ logistic regression กับจุดจากตารางแทนค่า · ขวา: calibration plot ห้าช่อง ความน่าจะเป็นที่ทำนายเทียบสัดส่วนที่เกิดจริง")
    # ซ้าย sigmoid
    out.append(f'<text x="150" y="18" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="{INK}">sigmoid: P = 1/(1 + e^−(β₀ + β₁x))</text>')
    out.append(f'<text x="150" y="32" text-anchor="middle" {FONT} font-size="10" fill="{INK2}">β₀ = −0.2 · β₁ = 0.8 (ตารางแทนค่า)</text>')
    x0, y0, w, h = 45, 58, 215, 163
    sx, sy = frame(out, x0, y0, w, h, [(-4, "−4"), (-2, "−2"), (0, "0"), (2, "2"), (4, "4")], [(0, "0"), (0.5, "0.5"), (1, "1")], xlab="x", ylab="P(y = 1)")
    xs = np.linspace(-4, 4, 80); ps = 1 / (1 + np.exp(-(-0.2 + 0.8 * xs)))
    out.append(f'<line x1="{x0}" y1="{sy(0.5):.1f}" x2="{x0+w}" y2="{sy(0.5):.1f}" stroke="{INK2}" stroke-width="1" stroke-dasharray="4 4"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(xs, ps)], BLUE, 2.5)
    for xv in (-1, 0, 1, 2):
        pv = 1 / (1 + np.exp(-(-0.2 + 0.8 * xv)))
        out.append(f'<circle cx="{sx(xv):.1f}" cy="{sy(pv):.1f}" r="3.8" fill="#fff" stroke="{PURPLE}" stroke-width="2"/>')
        out.append(f'<text x="{sx(xv)+6:.1f}" y="{sy(pv)+(12 if xv<1 else -6):.1f}" {FONT} font-size="9" fill="{PURPLE}" font-weight="600">x={xv}: {pv:.3f}</text>')
    out.append(f'<text x="{sx(-3.9):.1f}" y="{sy(0.5)-5:.1f}" {FONT} font-size="9" fill="{INK2}">P = 0.5 ที่ x = 0.25 (= −β₀/β₁)</text>')
    # ขวา calibration
    out.append(f'<text x="420" y="18" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="{INK}">calibration — ทำนาย 30% แล้วเกิดจริง 30% ไหม</text>')
    out.append(f'<text x="420" y="32" text-anchor="middle" {FONT} font-size="10" fill="{INK2}">out-of-sample 2,000 จุด แบ่ง 5 ช่องตาม P ที่ทำนาย</text>')
    x1 = 315; sx2, sy2 = frame(out, x1, y0, w, h, [(0, "0"), (0.5, "0.5"), (1, "1")], [(0, "0"), (0.5, "0.5"), (1, "1")], xlab="P ที่ทำนาย (เฉลี่ยในช่อง)", ylab="สัดส่วนที่เกิดจริง")
    out.append(f'<line x1="{sx2(0):.1f}" y1="{sy2(0):.1f}" x2="{sx2(1):.1f}" y2="{sy2(1):.1f}" stroke="{INK2}" stroke-width="1.2" stroke-dasharray="4 4"/>')
    out.append(f'<text x="{sx2(0.98):.1f}" y="{sy2(0.4):.1f}" text-anchor="end" {FONT} font-size="9" fill="{INK2}">เส้นประ 45° = calibrated สมบูรณ์</text>')
    polyline(out, [(sx2(r[1]), sy2(r[2])) for r in rows], GREEN, 2.2)
    for nn, pr, ac in rows:
        rad = 3 + 4 * nn / max(r[0] for r in rows)
        out.append(f'<circle cx="{sx2(pr):.1f}" cy="{sy2(ac):.1f}" r="{rad:.1f}" fill="{GREEN}" opacity="0.75"/>')
        out.append(f'<text x="{sx2(pr)+9:.1f}" y="{sy2(ac)+3.5:.1f}" {FONT} font-size="8.5" fill="{INK2}">n={nn}</text>')
    out.append(f'<text x="{x1+2}" y="{y0+h-6}" {FONT} font-size="9" fill="{INK2}">ขนาดจุด = จำนวนตัวอย่างในช่อง</text>')
    out.append("</svg>")
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
