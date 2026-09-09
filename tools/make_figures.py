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
    if ylab: out.append(f'<text transform="rotate(-90)" x="{-(y0 + h/2):.1f}" y="{x0-40}" text-anchor="middle" {FONT} font-size="10" fill="{INK2}">{ylab}</text>')
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


def svg_open(W, H, label, multipanel=False):
    mp = ' data-legend="per-panel"' if multipanel else ""   # หลายพาเนล พาเนลละซีรีส์เดียว — ไม่ต้องมี legend รวม
    return [f'<svg class="d" viewBox="0 0 {W} {H}" role="img" aria-label="{label}"{mp}>',
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
    legend(out, [(RED, "OLS", ""), (GREEN, "Theil-Sen (median ของความชันทุกคู่)", ""), (INK2, "β จริง 1.2", "4 4")], x0, H - 10)
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
    out = svg_open(Wd, H, "ซ้าย: เส้น sigmoid ของ logistic regression กับจุดจากตารางแทนค่า · ขวา: calibration plot ห้าช่อง ความน่าจะเป็นที่ทำนายเทียบสัดส่วนที่เกิดจริง", multipanel=True)
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



# ── Payoff Mastery 5a — Black-Scholes: เส้นโค้งราคา Call กับความชัน Δ · Greeks ตามราคาหุ้น ──
def _N(x):
    from math import erf, sqrt
    return 0.5 * (1 + erf(x / sqrt(2)))
def _npdf(x):
    return np.exp(-x * x / 2) / np.sqrt(2 * np.pi)
def bs_greeks(S, K=100.0, r=0.05, sg=0.20, T=0.5):
    S = np.asarray(S, float)
    d1 = (np.log(S / K) + (r + sg * sg / 2) * T) / (sg * np.sqrt(T)); d2 = d1 - sg * np.sqrt(T)
    Nd1 = np.vectorize(_N)(d1); Nd2 = np.vectorize(_N)(d2); disc = np.exp(-r * T)
    C = S * Nd1 - K * disc * Nd2
    return dict(C=C, delta=Nd1, gamma=_npdf(d1) / (S * sg * np.sqrt(T)),
                theta_day=(-(S * _npdf(d1) * sg) / (2 * np.sqrt(T)) - r * K * disc * Nd2) / 365,
                vega1=S * _npdf(d1) * np.sqrt(T) / 100)


@fig("pm-part5a.html", "bs-call-curve")
def fig_bs_call_curve():
    S = np.linspace(70, 130, 121); g = bs_greeks(S); g0 = bs_greeks(100.0)
    NUMS["bs-call-curve"] = dict(C=float(g0["C"]), delta=float(g0["delta"]))
    Wd, H = 560, 300
    out = svg_open(Wd, H, "เส้นโค้งราคา Call ของ Black-Scholes เหนือเส้นหักศอกของ intrinsic value จุด S = 100 ราคา 6.89 และเส้นสัมผัสความชัน 0.5977 คือ Delta")
    title(out, Wd, "Black-Scholes บอกว่า 'เส้นโค้ง' อยู่ตรงไหนเหนือเส้นหักศอก", "K = 100 · r = 5% · σ = 20% · T = 0.5 ปี · ตัวเลขชุดเดียวกับตัวอย่างคำนวณ")
    x0, y0, w, h = 50, 46, 480, 195
    sx, sy = frame(out, x0, y0, w, h, [(70, "70"), (80, "80"), (90, "90"), (100, "100"), (110, "110"), (120, "120"), (130, "130")], [(0, "0"), (10, "10"), (20, "20"), (30, "30"), (40, "40")], xlab="ราคาหุ้น S วันนี้", ylab="ราคา Call (฿)")
    # intrinsic
    polyline(out, [(sx(70), sy(0)), (sx(100), sy(0)), (sx(130), sy(30))], INK2, 1.6, dash="5 4", shadow=False)
    out.append(f'<text x="{sx(121):.1f}" y="{sy(21)+14:.1f}" {FONT} font-size="9.5" fill="{INK2}">intrinsic = max(S − K, 0)</text>')
    # time value shading ระหว่างเส้นโค้งกับ intrinsic
    pts = [(sx(a), sy(b)) for a, b in zip(S, g["C"])] + [(sx(a), sy(max(a - 100, 0))) for a in S[::-1]]
    out.append('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="{BLUE}" opacity="0.08"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, g["C"])], BLUE, 2.75)
    # tangent at S=100
    C0, D0 = float(g0["C"]), float(g0["delta"])
    out.append(f'<line x1="{sx(86):.1f}" y1="{sy(C0 + D0*(86-100)):.1f}" x2="{sx(114):.1f}" y2="{sy(C0 + D0*(114-100)):.1f}" stroke="{PURPLE}" stroke-width="1.6" stroke-dasharray="6 3"/>')
    out.append(f'<circle cx="{sx(100):.1f}" cy="{sy(C0):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
    out.append(f'<text x="{sx(100)-8:.1f}" y="{sy(C0)-10:.1f}" text-anchor="end" {FONT} font-size="10" fill="{PURPLE}" font-weight="700">S = 100: C = ฿{C0:.2f}</text>')
    out.append(f'<text x="{sx(100)-8:.1f}" y="{sy(C0)+3:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{PURPLE}">ความชันเส้นสัมผัส = Δ = {D0:.4f}</text>')
    out.append(f'<text x="{sx(100)+6:.1f}" y="{sy(C0/2)+3:.1f}" {FONT} font-size="9.5" fill="{BLUE}">time value ที่ ATM = ทั้งก้อน ฿{C0:.2f}</text>')
    out.append(f'<line x1="{sx(100):.1f}" y1="{sy(C0):.1f}" x2="{sx(100):.1f}" y2="{sy(0):.1f}" stroke="{BLUE}" stroke-width="1" stroke-dasharray="2 2"/>')
    out.append(f'<text x="{sx(72):.1f}" y="{sy(3.2):.1f}" {FONT} font-size="9.5" fill="{INK2}">OTM ลึก: เส้นโค้งแนบศูนย์ Δ → 0</text>')
    out.append(f'<text x="{sx(128):.1f}" y="{sy(2.5):.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">ITM ลึก: Δ → 1</text>')
    legend(out, [(BLUE, "ราคา Call (Black-Scholes)", ""), (INK2, "intrinsic value", "5 4"), (PURPLE, "เส้นสัมผัส (ความชัน = Δ)", "6 3")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


@fig("pm-part5a.html", "greeks-grid")
def fig_greeks_grid():
    S = np.linspace(70, 130, 121); g = bs_greeks(S); g0 = bs_greeks(100.0)
    NUMS["greeks-grid"] = dict(delta=float(g0["delta"]), gamma=float(g0["gamma"]), theta_day=float(g0["theta_day"]), vega1=float(g0["vega1"]))
    Wd, H = 560, 400
    out = svg_open(Wd, H, "Greeks ของ Call ตามราคาหุ้น 4 ช่อง: Delta รูปตัว S จาก 0 ถึง 1 · Gamma ยอดแหลมที่ ATM · Theta ติดลบสุดที่ ATM · Vega ยอดที่ ATM · จุดที่ S = 100 ตรงกับตารางค่าตัวอย่าง", multipanel=True)
    title(out, Wd, "Greeks ตามราคาหุ้น — ทุกตัว 'สุด' ที่ ATM ยกเว้น Delta ที่แค่ผ่านครึ่งทาง", "K = 100 · r = 5% · σ = 20% · T = 0.5 · จุดม่วง = ค่าในตารางที่ S = 100")
    panels = [("Delta = N(d₁)", "delta", (0, "0"), (0.5, "0.5"), (1, "1"), f"{g0['delta']:.4f}", GREEN),
              ("Gamma = N′(d₁)/(Sσ√T)", "gamma", (0, "0"), (0.015, "0.015"), (0.03, "0.03"), f"{g0['gamma']:.4f}", BLUE),
              ("Theta ต่อวัน (฿)", "theta_day", (-0.03, "−0.03"), (-0.015, "−0.015"), (0, "0"), f"−฿{abs(g0['theta_day']):.3f}", RED),
              ("Vega ต่อ vol 1% (฿)", "vega1", (0, "0"), (0.15, "0.15"), (0.3, "0.30"), f"฿{g0['vega1']:.3f}", AMBER)]
    pw, ph = 205, 120
    for k, (name, key, y_a, y_m, y_b, lab, col) in enumerate(panels):
        cx, cy = 50 + (k % 2) * 275, 56 + (k // 2) * 170
        out.append(f'<text x="{cx + pw/2:.0f}" y="{cy-6}" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="{INK}">{name}</text>')
        sx, sy = frame(out, cx, cy, pw, ph, [(70, "70"), (100, "100"), (130, "130")], [y_a, y_m, y_b], xlab="S" if k >= 2 else "")
        if key == "theta_day":
            out.append(f'<line x1="{cx}" y1="{sy(0):.1f}" x2="{cx+pw}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1"/>')
        polyline(out, [(sx(a), sy(b)) for a, b in zip(S, g[key])], col, 2.4)
        v0 = float(g0[key])
        out.append(f'<circle cx="{sx(100):.1f}" cy="{sy(v0):.1f}" r="4" fill="#fff" stroke="{PURPLE}" stroke-width="2.2"/>')
        dy = 16 if key in ("theta_day",) else -8
        anchor_ = "start" if key == "delta" else "end"; dx = 7 if key == "delta" else -7
        out.append(f'<text x="{sx(100)+dx:.1f}" y="{sy(v0)+dy:.1f}" text-anchor="{anchor_}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">{lab}</text>')
    out.append(f'<text x="{Wd/2:.0f}" y="{H-20}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">Gamma · Vega และก้อนแรกของ Theta มี N′(d₁) เป็นแกน — จึงมียอดที่ ATM พร้อมกัน</text>')
    out.append(f'<text x="{Wd/2:.0f}" y="{H-6}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">Theta ฝั่ง ITM ลึกยังเหลือก้อนดอกเบี้ย −rKe⁻ʳᵀ ไม่ถึงศูนย์</text>')
    out.append("</svg>")
    return "\n".join(out)


def render_all():
    return {(fl, nm): fn() for (fl, nm), fn in FIGS.items()}



# ══ ทฤษฎีของ Quant (เล่ม A) และ เสาหลัก (เล่ม B) — ภาพประกอบการ์ด ★★★ ═══════════════════

# ── A · Part 1 Random Walk: GBM 20 เส้น μ = 10% σ = 20% · ค่าเฉลี่ย vs มัธยฐาน (vol drag) ──
def gbm_paths_data(n=20, T=252, mu=0.10, sg=0.20, seed=5):
    rng = np.random.default_rng(seed); dt = 1 / 252
    z = rng.standard_normal((n, T))
    logS = np.cumsum((mu - sg * sg / 2) * dt + sg * np.sqrt(dt) * z, axis=1)
    return np.hstack([np.ones((n, 1)), np.exp(logS)])


@fig("theory-part1.html", "gbm-paths")
def fig_gbm_paths():
    P = gbm_paths_data(); mu, sg = 0.10, 0.20
    NUMS["gbm-paths"] = dict(mean_end=np.exp(mu), median_end=np.exp(mu - sg * sg / 2), drag=sg * sg / 2)
    Wd, H = 560, 300
    out = svg_open(Wd, H, "เส้นทางราคาแบบ geometric Brownian motion 20 เส้นในหนึ่งปี กับกรวย ±1σ√t · เส้นค่าเฉลี่ยตามทฤษฎี e^μt สูงกว่าเส้นมัธยฐาน e^(μ−σ²/2)t คือ vol drag")
    title(out, Wd, "Random walk ที่ใช้จริง (GBM) — ราคาถ่างออกตาม √t และค่าเฉลี่ยกับมัธยฐานแยกจากกัน", "μ = 10%/ปี · σ = 20%/ปี · 20 เส้นทางจำลอง (seed 5) · เริ่มที่ 100")
    x0, y0, w, h = 50, 46, 480, 195
    tt = np.arange(P.shape[1]) / 252
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (0.25, "3 เดือน"), (0.5, "6 เดือน"), (0.75, "9 เดือน"), (1, "1 ปี")], [(60, "60"), (80, "80"), (100, "100"), (120, "120"), (140, "140"), (160, "160")], xlab="เวลา", ylab="ราคา")
    # กรวย ±1σ√t รอบมัธยฐาน (log-space)
    med = 100 * np.exp((mu - sg * sg / 2) * tt); up = med * np.exp(sg * np.sqrt(tt)); dn = med * np.exp(-sg * np.sqrt(tt))
    poly = [(sx(a), sy(b)) for a, b in zip(tt, up)] + [(sx(a), sy(b)) for a, b in zip(tt[::-1], dn[::-1])]
    out.append('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in poly) + f'" fill="{BLUE}" opacity="0.08"/>')
    for row in P:
        out.append('<polyline points="' + " ".join(f"{sx(a):.1f},{sy(100*b):.1f}" for a, b in zip(tt[::3], row[::3])) + f'" fill="none" stroke="{BLUE}" stroke-width="1.1" opacity="0.55"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(tt, 100 * np.exp(mu * tt))], GREEN, 2.2, dash="6 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(tt, med)], PURPLE, 2.2, shadow=False)
    out.append(f'<text x="{x0+6}" y="{y0+14}" {FONT} font-size="9.5" fill="{GREEN}" font-weight="700">ปลายปี ค่าเฉลี่ย e^μ = {100*np.exp(mu):.1f} (+{(np.exp(mu)-1)*100:.1f}%)</text>')
    out.append(f'<text x="{x0+6}" y="{y0+28}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">ปลายปี มัธยฐาน e^(μ−σ²/2) = {med[-1]:.1f} (+{(med[-1]/100-1)*100:.1f}%) — vol drag σ²/2 = 2%</text>')
    out.append(f'<text x="{x0+6}" y="{y0+42}" {FONT} font-size="9.5" fill="{INK2}">แถบสีจาง = มัธยฐาน × e^(±σ√t) — กว้างขึ้นตาม √t ไม่ใช่ t</text>')
    legend(out, [(BLUE, "เส้นทางจำลอง 20 เส้น", ""), (GREEN, "ค่าเฉลี่ยตามทฤษฎี", "6 3"), (PURPLE, "มัธยฐาน (เส้นทางตรงกลาง)", "")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── A · Part 2 Mean-Variance: σ พอร์ต 50/50 ของสองสินทรัพย์ σ = 20% ตาม correlation ──
@fig("theory-part2.html", "diversification-corr")
def fig_diversification_corr():
    rho = np.linspace(-1, 1, 201); sp = np.sqrt(0.5 ** 2 * 0.04 + 0.5 ** 2 * 0.04 + 2 * 0.5 * 0.5 * 0.04 * rho) * 100
    NUMS["diversification-corr"] = dict(s_m1=float(sp[0]), s_0=float(sp[100]), s_p1=float(sp[-1]))
    Wd, H = 560, 280
    out = svg_open(Wd, H, "ความผันผวนของพอร์ต 50/50 จากสินทรัพย์สองตัวที่ σ = 20% เท่ากัน ลดลงจาก 20% ที่ correlation +1 เป็น 14.1% ที่ 0 และ 0% ที่ −1")
    title(out, Wd, "free lunch มื้อเดียวในการเงิน — ผลตอบแทนคาดหวังเท่าเดิม แต่ σ พอร์ตลดตาม correlation", "สองสินทรัพย์ σ = 20% ทั้งคู่ · ลงเท่ากัน 50/50 · σ_p = √(w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρσ₁σ₂)")
    x0, y0, w, h = 50, 60, 480, 166
    sx, sy = frame(out, x0, y0, w, h, [(-1, "−1"), (-0.5, "−0.5"), (0, "0"), (0.5, "+0.5"), (1, "+1")], [(0, "0%"), (5, "5%"), (10, "10%"), (15, "15%"), (20, "20%")], xlab="correlation ρ ระหว่างสองสินทรัพย์", ylab="σ ของพอร์ต")
    out.append(f'<line x1="{x0}" y1="{sy(20):.1f}" x2="{x0+w}" y2="{sy(20):.1f}" stroke="{INK2}" stroke-width="1" stroke-dasharray="4 4"/>')
    out.append(f'<text x="{x0+4}" y="{sy(20)+12:.1f}" {FONT} font-size="9.5" fill="{INK2}">ถือตัวเดียว σ = 20%</text>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(rho, sp)], BLUE, 2.75)
    for r_, lab, dy, anc in [(-1, f"ρ = −1: σ = {sp[0]:.0f}% — กำจัดหมด (ทฤษฎี)", -8, "start"), (0, f"ρ = 0: σ = {sp[100]:.1f}% — ลด ~30% ฟรี", -10, "middle"), (1, f"ρ = +1: σ = {sp[-1]:.0f}% — ไม่ลดเลย", -7, "end")]:
        v = float(np.interp(r_, rho, sp))
        out.append(f'<circle cx="{sx(r_):.1f}" cy="{sy(v):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
        out.append(f'<text x="{sx(r_)+(6 if anc=="start" else -6 if anc=="end" else 0):.1f}" y="{sy(v)+dy:.1f}" text-anchor="{anc}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">{lab}</text>')
    out.append(f'<text x="{x0+w-4}" y="{sy(3):.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">หุ้นกับหุ้นมัก ρ ≈ 0.3–0.8 — ลดได้แต่ไม่หมด และ ρ วิ่งขึ้นตอนวิกฤต (เสาหลัก Part 5 กฎ 3)</text>')
    out.append("</svg>")
    return "\n".join(out)


# ── A · Part 3 Prospect Theory: ฟังก์ชันคุณค่าที่หักศอกที่ศูนย์ (λ = 2.25) กับเดิมพัน +100/−50 ──
@fig("theory-part3.html", "prospect-value")
def fig_prospect_value():
    lam = 2.25
    NUMS["prospect-value"] = dict(v_gain=100.0, v_loss=-lam * 50, ev_mind=0.5 * 100 - 0.5 * lam * 50)
    Wd, H = 560, 300
    out = svg_open(Wd, H, "ฟังก์ชันคุณค่าของ prospect theory หักศอกที่ศูนย์ ฝั่งขาดทุนชันกว่า 2.25 เท่า · เดิมพัน 50/50 ได้ 100 หรือเสีย 50 มีค่าทางใจติดลบ −6.25 ทั้งที่ EV เป็นบวก 25")
    title(out, Wd, "loss aversion — เส้นฝั่งขาดทุนชันกว่าฝั่งกำไร 2.25 เท่า จึงปฏิเสธเดิมพันที่ EV บวก", "v(x) = x เมื่อได้ · v(x) = 2.25x เมื่อเสีย (รุ่นเส้นตรงตามตัวอย่างในการ์ด · ของ Kahneman-Tversky โค้งเพิ่มอีกชั้น)")
    x0, y0, w, h = 60, 60, 470, 186
    sx, sy = frame(out, x0, y0, w, h, [(-100, "−100"), (-50, "−50"), (0, "0"), (50, "+50"), (100, "+100")], [(-225, "−225"), (-150, "−150"), (-75, "−75"), (0, "0"), (75, "+75"), (150, "+150")], xlab="ผลลัพธ์จริง ($)", ylab="ค่าทางใจ v(x)")
    out.append(f'<line x1="{sx(0):.1f}" y1="{y0}" x2="{sx(0):.1f}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1"/>')
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1"/>')
    polyline(out, [(sx(-100), sy(-100)), (sx(0), sy(0)), (sx(100), sy(100))], INK2, 1.4, dash="5 4", shadow=False)
    out.append(f'<text x="{sx(58):.1f}" y="{sy(58)+18:.1f}" {FONT} font-size="9.5" fill="{INK2}">คนไร้ bias: v(x) = x</text>')
    polyline(out, [(sx(-100), sy(-lam * 100)), (sx(0), sy(0))], RED, 2.75)
    polyline(out, [(sx(0), sy(0)), (sx(100), sy(100))], GREEN, 2.75)
    out.append(f'<circle cx="{sx(100):.1f}" cy="{sy(100):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
    out.append(f'<text x="{sx(100)-8:.1f}" y="{sy(100)-8:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">ชนะ +$100 → ค่าทางใจ +100</text>')
    out.append(f'<circle cx="{sx(-50):.1f}" cy="{sy(-lam*50):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
    out.append(f'<text x="{sx(-50)+8:.1f}" y="{sy(-lam*50)+24:.1f}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">แพ้ −$50 → ค่าทางใจ −{lam*50:.2f} (= 2.25 × 50)</text>')
    out.append(f'<text x="{sx(-98):.1f}" y="{sy(130):.1f}" {FONT} font-size="10" fill="{INK}" font-weight="700">เดิมพัน 50/50: EV = +$25 แต่ค่าทางใจ = ½(100) − ½({lam*50:.2f}) = {0.5*100-0.5*lam*50:+.2f} → ปฏิเสธ</text>')
    legend(out, [(GREEN, "ฝั่งกำไร ความชัน 1", ""), (RED, "ฝั่งขาดทุน ความชัน 2.25", ""), (INK2, "เส้นอ้างอิงไร้ bias", "5 4")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── A · Part 4 Binomial ขั้นเดียว: $100 → $110/$90 · p* = 0.5 · call K=100 = $5 ──
@fig("theory-part4.html", "binomial-tree")
def fig_binomial_tree():
    u, d, S0, K = 1.1, 0.9, 100, 100; p = (1 - d) / (u - d); C = p * max(S0 * u - K, 0) + (1 - p) * max(S0 * d - K, 0)
    NUMS["binomial-tree"] = dict(p=p, C=C)
    Wd, H = 560, 290
    out = svg_open(Wd, H, "ต้นไม้ทวินามขั้นเดียว หุ้น 100 ขึ้นเป็น 110 หรือลงเป็น 90 · ความน่าจะเป็น risk-neutral 0.5 · call strike 100 จ่าย 10 หรือ 0 · ราคาวันนี้ 5")
    title(out, Wd, "ต้นไม้ขั้นเดียว — ราคา call มาจาก p* ที่คำนวณ ไม่ใช่ความน่าจะเป็นที่เชื่อ", "u = 1.1 · d = 0.9 · r ≈ 0 · K = 100 · p* = (1 − d)/(u − d)")
    xa, xb = 130, 415; ya, yu, yd = 140, 78, 202
    def node(x, y, big, small, col):
        out.append(f'<rect x="{x-90}" y="{y-24}" width="180" height="48" rx="8" fill="#fff" stroke="{col}" stroke-width="2"/>')
        out.append(f'<text x="{x}" y="{y-5}" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="{INK}">{big}</text>')
        out.append(f'<text x="{x}" y="{y+12}" text-anchor="middle" {FONT} font-size="9.5" fill="{col}">{small}</text>')
    out.append(f'<line x1="{xa+90}" y1="{ya-8}" x2="{xb-90}" y2="{yu}" stroke="{GREEN}" stroke-width="2.2"/>')
    out.append(f'<line x1="{xa+90}" y1="{ya+8}" x2="{xb-90}" y2="{yd}" stroke="{RED}" stroke-width="2.2"/>')
    out.append(f'<text x="{(xa+xb)/2:.0f}" y="{(ya+yu)/2-8:.0f}" text-anchor="middle" {FONT} font-size="10" fill="{GREEN}" font-weight="700">ขึ้น ×{u} · p* = {p:.1f}</text>')
    out.append(f'<text x="{(xa+xb)/2:.0f}" y="{(ya+yd)/2+16:.0f}" text-anchor="middle" {FONT} font-size="10" fill="{RED}" font-weight="700">ลง ×{d} · 1 − p* = {1-p:.1f}</text>')
    node(xa, ya, f"หุ้น ${S0}", f"call = {p:.1f}×10 + {1-p:.1f}×0 = ${C:.0f}", PURPLE)
    node(xb, yu, f"หุ้น ${S0*u:.0f}", f"call จ่าย max({S0*u:.0f} − {K}, 0) = $10", GREEN)
    node(xb, yd, f"หุ้น ${S0*d:.0f}", f"call จ่าย max({S0*d:.0f} − {K}, 0) = $0", RED)
    out.append(f'<text x="{Wd/2:.0f}" y="{H-30}" text-anchor="middle" {FONT} font-size="10" fill="{INK}">p* = (1 − {d})/({u} − {d}) = {p:.1f} คือค่าที่ทำให้ "หุ้นวันนี้ = ค่าคาดหวังของหุ้นพรุ่งนี้" พอดี ({p:.1f}×110 + {1-p:.1f}×90 = 100)</text>')
    out.append(f'<text x="{Wd/2:.0f}" y="{H-12}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">ถ้าคุณเชื่อว่าหุ้นขึ้น 90% ราคา call ก็ยัง $5 — ความเชื่อไม่อยู่ในสูตร มีแต่ replication</text>')
    out.append("</svg>")
    return "\n".join(out)


# ── A · Part 5 GARCH(1,1) ω = 2e-6 α = 0.08 β = 0.90: vol clustering และการลู่กลับหา 1%/วัน ──
def garch_sim(T=500, seed=21, om=2e-6, al=0.08, be=0.90):
    rng = np.random.default_rng(seed); z = rng.standard_normal(T)
    s2 = np.empty(T); r = np.empty(T); s2[0] = om / (1 - al - be)
    r[0] = np.sqrt(s2[0]) * z[0]
    for t_ in range(1, T):
        s2[t_] = om + al * r[t_ - 1] ** 2 + be * s2[t_ - 1]; r[t_] = np.sqrt(s2[t_]) * z[t_]
    return r, np.sqrt(s2), np.sqrt(om / (1 - al - be))


@fig("theory-part5.html", "garch-sim")
def fig_garch_sim():
    r, sg, lr = garch_sim()
    NUMS["garch-sim"] = dict(long_run=lr, max_sigma=sg.max(), persistence=0.98)
    Wd, H = 560, 330
    out = svg_open(Wd, H, "บน: ผลตอบแทนรายวันจำลองจาก GARCH(1,1) ที่ vol จับกลุ่ม · ล่าง: σ_t ที่พุ่งหลังวันช็อกแล้วค่อยลู่กลับหา 1% ต่อวันด้วย persistence 0.98", multipanel=True)
    title(out, Wd, "GARCH(1,1) — vol จับกลุ่ม แล้วลู่กลับหา long-run 1%/วัน อย่างช้า ๆ (persistence 0.98)", "ω = 0.000002 · α = 0.08 · β = 0.90 · 500 วันจำลอง (seed 21)")
    x0, w = 50, 480; T = len(r); xt = [(0, "0"), (100, "100"), (200, "200"), (300, "300"), (400, "400"), (500, "500")]
    y0, h = 46, 110
    sx, sy = frame(out, x0, y0, w, h, xt, [(-4, "−4%"), (-2, "−2%"), (0, "0"), (2, "+2%"), (4, "+4%")], ylab="ผลตอบแทนรายวัน")
    for i, v in enumerate(r * 100):
        out.append(f'<line x1="{sx(i):.1f}" y1="{sy(0):.1f}" x2="{sx(i):.1f}" y2="{sy(v):.1f}" stroke="{BLUE}" stroke-width="1" opacity="0.8"/>')
    y1, h1 = 186, 110
    sx2, sy2 = frame(out, x0, y1, w, h1, xt, [(0, "0"), (1, "1%"), (2, "2%"), (3, "3%")], xlab="วันที่", ylab="σ_t (GARCH)")
    out.append(f'<line x1="{x0}" y1="{sy2(lr*100):.1f}" x2="{x0+w}" y2="{sy2(lr*100):.1f}" stroke="{INK2}" stroke-width="1" stroke-dasharray="4 4"/>')
    out.append(f'<text x="{x0+4}" y="{sy2(lr*100)-5:.1f}" {FONT} font-size="9.5" fill="{INK2}">long-run √(ω/(1−α−β)) = {lr*100:.0f}%/วัน</text>')
    polyline(out, [(sx2(i), sy2(v)) for i, v in enumerate(sg * 100)], RED, 2.2)
    im = int(np.argmax(sg))
    out.append(f'<circle cx="{sx2(im):.1f}" cy="{sy2(sg[im]*100):.1f}" r="4" fill="#fff" stroke="{PURPLE}" stroke-width="2.2"/>')
    anc = "end" if im > len(sg) / 2 else "start"; dx = -8 if anc == "end" else 8
    out.append(f'<text x="{sx2(im)+dx:.1f}" y="{sy2(sg[im]*100)-8:.1f}" text-anchor="{anc}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">σ พุ่งถึง {sg[im]*100:.1f}% หลังวันช็อก · ส่วนเกินของ σ² เหนือ long-run หายไป 2% ของที่เหลือทุกวัน (ตัวคูณ 0.98 · half-life ≈ {np.log(0.5)/np.log(0.98):.0f} วัน)</text>')
    out.append(f'<text x="{x0+w-4}" y="{y1+12}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">ช่วงที่แท่งบนหนาแน่น = σ ล่างสูง — วันเหวี่ยงแรงมักตามด้วยวันเหวี่ยงแรง</text>')
    out.append("</svg>")
    return "\n".join(out)


# ── B · Part 1 PCA ของ yield curve: โหลด Level / Slope / Curvature จาก correlation matrix ของ 2·A §1.4 ──
YC_CORR = np.array([[1.00, 0.95, 0.88, 0.80, 0.72], [0.95, 1.00, 0.96, 0.90, 0.83], [0.88, 0.96, 1.00, 0.97, 0.92], [0.80, 0.90, 0.97, 1.00, 0.97], [0.72, 0.83, 0.92, 0.97, 1.00]])


@fig("pillars-part1.html", "yc-loadings")
def fig_yc_loadings():
    vals, vecs = np.linalg.eigh(YC_CORR); vals, vecs = vals[::-1], vecs[:, ::-1]; pct = vals / vals.sum() * 100
    L = [vecs[:, k] * (1 if vecs[:, k].sum() > 0 or k > 0 else -1) for k in range(3)]
    if L[0].sum() < 0: L[0] = -L[0]
    if L[1][0] > 0: L[1] = -L[1]          # Slope: สั้นลบ ยาวบวก
    if L[2][2] < 0: L[2] = -L[2]          # Curvature: กลางบวก
    NUMS["yc-loadings"] = dict(pc1=pct[0], pc2=pct[1], pc3=pct[2], cum3=pct[:3].sum())
    Wd, H = 560, 300
    out = svg_open(Wd, H, "โหลดของสามองค์ประกอบหลักของเส้นผลตอบแทน 5 ช่วงอายุ: Level แบนเครื่องหมายเดียว · Slope เปลี่ยนเครื่องหมายครั้งเดียวจากสั้นไปยาว · Curvature โก่งตรงกลาง")
    title(out, Wd, "Level · Slope · Curvature — หน้าตาของ eigenvector สามตัวแรก", f"จาก correlation matrix ตัวอย่างใน 2 · A §1.4 · อธิบาย {pct[0]:.1f}% · {pct[1]:.1f}% · {pct[2]:.1f}% (ของจริงราว 90 / 8 / 2 ตามการ์ด)")
    x0, y0, w, h = 50, 46, 480, 180
    mats = ["3 เดือน", "2 ปี", "5 ปี", "10 ปี", "30 ปี"]
    sx, sy = frame(out, x0, y0, w, h, [(i, m) for i, m in enumerate(mats)], [(-0.8, "−0.8"), (-0.4, "−0.4"), (0, "0"), (0.4, "+0.4"), (0.8, "+0.8")], xlab="ช่วงอายุ (สั้น → ยาว)", ylab="โหลด (น้ำหนักของแต่ละช่วงอายุใน PC)")
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1"/>')
    cols = [BLUE, GREEN, AMBER]; names = ["PC1 Level — ทุกช่วงขยับพร้อมกัน", "PC2 Slope — สั้นกับยาวสวนทาง", "PC3 Curvature — กลางโค้งต่างจากปลาย"]
    for k in range(3):
        polyline(out, [(sx(i), sy(v)) for i, v in enumerate(L[k])], cols[k], 2.5)
        out.append(f'<g fill="{cols[k]}">' + "".join(f'<circle cx="{sx(i):.1f}" cy="{sy(v):.1f}" r="3.6"/>' for i, v in enumerate(L[k])) + "</g>")
    legend(out, [(cols[k], f"{names[k]} ({pct[k]:.1f}%)", "") for k in range(3)][:2], x0, H - 26)
    legend(out, [(cols[2], f"{names[2]} ({pct[2]:.1f}%)", "")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── B · Part 2 Hazard rate: survival e^(−λt) กับ λ = 2%/0.6 = 3.3% ──
@fig("pillars-part2.html", "survival-curve")
def fig_survival_curve():
    lam = 0.02 / 0.6; tt = np.linspace(0, 10, 101); S = np.exp(-lam * tt)
    NUMS["survival-curve"] = dict(lam=lam, s5=float(np.exp(-lam * 5)), s1=float(np.exp(-lam)))
    Wd, H = 560, 280
    out = svg_open(Wd, H, "เส้นโค้งโอกาสรอด e^(−λt) ของบริษัทที่ CDS 200 bp recovery 40% ให้ hazard rate 3.3% ต่อปี · โอกาสรอด 5 ปีราว 85%")
    title(out, Wd, "credit triangle ในภาพ — spread 200 bp กับ recovery 40% แปลงเป็นโอกาสรอดแต่ละปี", f"λ = spread/(1 − R) = 2.0%/0.6 = {lam*100:.1f}%/ปี · P(รอดถึง t) = e^(−λt)")
    x0, y0, w, h = 50, 46, 480, 180
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (2, "2"), (4, "4"), (6, "6"), (8, "8"), (10, "10")], [(60, "60%"), (70, "70%"), (80, "80%"), (90, "90%"), (100, "100%")], xlab="ปีข้างหน้า", ylab="โอกาสรอด")
    poly = [(sx(a), sy(b * 100)) for a, b in zip(tt, S)] + [(sx(10), sy(60)), (sx(0), sy(60))]
    out.append('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in poly) + f'" fill="{GREEN}" opacity="0.08"/>')
    poly2 = [(sx(a), sy(b * 100)) for a, b in zip(tt, S)] + [(sx(10), sy(100)), (sx(0), sy(100))]
    out.append('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in poly2) + f'" fill="{RED}" opacity="0.10"/>')
    polyline(out, [(sx(a), sy(b * 100)) for a, b in zip(tt, S)], GREEN, 2.75)
    for yr in (1, 5):
        v = float(np.exp(-lam * yr)) * 100
        out.append(f'<line x1="{sx(yr):.1f}" y1="{sy(v):.1f}" x2="{sx(yr):.1f}" y2="{sy(60):.1f}" stroke="{PURPLE}" stroke-width="1" stroke-dasharray="3 3"/>')
        out.append(f'<circle cx="{sx(yr):.1f}" cy="{sy(v):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
        out.append(f'<text x="{sx(yr)+7:.1f}" y="{sy(v)-8:.1f}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">รอด {yr} ปี = e^(−{lam*100:.1f}%×{yr}) ≈ {v:.0f}%</text>')
    out.append(f'<text x="{x0+w-4}" y="{sy(97):.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{RED}">พื้นที่แดง = โอกาสผิดนัดสะสม — โตเกือบเป็นเส้นตรง ~{lam*100:.1f}% ต่อปีช่วงแรก</text>')
    out.append(f'<text x="{sx(0.3):.1f}" y="{sy(63):.1f}" {FONT} font-size="9.5" fill="{INK2}">λ คงที่คือสมมติฐาน — ของจริง λ พุ่งตอนเศรษฐกิจแย่ (❌ ในการ์ด)</text>')
    out.append("</svg>")
    return "\n".join(out)


# ── B · Part 3 √-law: impact = Y σ √(Q/ADV) เทียบเส้นตรง ──
@fig("pillars-part3.html", "sqrt-impact")
def fig_sqrt_impact():
    q = np.linspace(0, 0.30, 121); sg, Y = 0.02, 1.0; imp = Y * sg * np.sqrt(q) * 100
    NUMS["sqrt-impact"] = dict(imp10=float(Y * sg * np.sqrt(0.10) * 100), imp2_5=float(Y * sg * np.sqrt(0.025) * 100))
    Wd, H = 560, 280
    out = svg_open(Wd, H, "เส้นโค้งรากที่สองของ market impact ตามสัดส่วนขนาดออเดอร์ต่อปริมาณเฉลี่ยต่อวัน · ที่ 10% ของ ADV impact 0.63% ของราคา · ชันมากช่วงแรกแล้วแบนลง")
    title(out, Wd, "√-law — ชิ้นแรกดันราคาแรงสุด แต่ละชิ้นที่เพิ่มดันน้อยลง", "impact ≈ Y · σ · √(Q/ADV) · σ = 2%/วัน · Y = 1 · กำไรที่คาด 0.5% หมดก่อนถึง 10% ของ ADV")
    x0, y0, w, h = 50, 46, 480, 180
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (0.05, "5%"), (0.10, "10%"), (0.15, "15%"), (0.20, "20%"), (0.25, "25%"), (0.30, "30%")], [(0, "0"), (0.4, "0.4%"), (0.8, "0.8%"), (1.2, "1.2%")], xlab="ขนาดออเดอร์ Q เป็นสัดส่วนของ ADV", ylab="impact (% ของราคา)")
    polyline(out, [(sx(0), sy(0)), (sx(0.30), sy(0.02 * 0.30 / 0.10 * np.sqrt(0.10) * 100))], INK2, 1.4, dash="5 4", shadow=False)
    out.append(f'<text x="{sx(0.29):.1f}" y="{sy(0.02*0.29/0.10*np.sqrt(0.10)*100)+14:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">ถ้าเป็นเส้นตรง (สัญชาตญาณผิด)</text>')
    out.append(f'<line x1="{x0}" y1="{sy(0.5):.1f}" x2="{x0+w}" y2="{sy(0.5):.1f}" stroke="{RED}" stroke-width="1" stroke-dasharray="4 4"/>')
    out.append(f'<text x="{x0+w-4}" y="{sy(0.5)-5:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{RED}">กำไรที่กลยุทธ์คาด 0.5% ต่อเทรด</text>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(q, imp)], BLUE, 2.75)
    v10 = Y * sg * np.sqrt(0.10) * 100
    out.append(f'<circle cx="{sx(0.10):.1f}" cy="{sy(v10):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
    out.append(f'<text x="{sx(0.10)+8:.1f}" y="{sy(v10)-16:.1f}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">10% ของ ADV: impact = 2% × √0.10 ≈ {v10:.2f}% → กินกำไรหมด</text>')
    qc = (0.5 / (Y * sg * 100)) ** 2
    out.append(f'<line x1="{sx(qc):.1f}" y1="{sy(0.5):.1f}" x2="{sx(qc):.1f}" y2="{sy(0):.1f}" stroke="{RED}" stroke-width="1" stroke-dasharray="2 2"/>')
    out.append(f'<text x="{sx(qc):.1f}" y="{sy(0)-6:.1f}" text-anchor="middle" {FONT} font-size="9.5" fill="{RED}">capacity ≈ {qc*100:.2f}% ของ ADV</text>')
    out.append("</svg>")
    return "\n".join(out)


# ── B · Part 4 VaR vs ES: หาง 1% ของ normal σ = 2% (พอร์ต $100M) ──
@fig("pillars-part4.html", "var-es-tail")
def fig_var_es_tail():
    from math import erf, sqrt, pi
    sg = 2.0; z99 = 2.33; es_mult = round(float(np.exp(-2.326 ** 2 / 2) / np.sqrt(2 * np.pi) / 0.01), 2)   # 2.67 ตามการ์ด
    xs = np.linspace(-8, 8, 321); pdf = np.exp(-xs ** 2 / (2 * sg ** 2)) / (sg * np.sqrt(2 * np.pi))
    NUMS["var-es-tail"] = dict(var=z99 * sg, es=es_mult * sg, es_mult=es_mult)
    Wd, H = 560, 290
    out = svg_open(Wd, H, "การแจกแจง normal ของผลตอบแทนรายวัน σ 2% · เส้น VaR 99% ที่ −4.66% ตัดหางซ้าย 1% · ES คือค่าเฉลี่ยของหางที่ถูกตัดอยู่ที่ −5.34% · เส้นประหางอ้วนแสดงว่าหางจริงลึกกว่า")
    title(out, Wd, "VaR คือ 'เส้น' — ES คือ 'พื้นที่ใต้หาง' ที่อยู่เลยเส้นนั้น", f"ผลตอบแทนรายวัน σ = 2% (พอร์ต $100M) · VaR₉₉ = 2.33σ = {z99*sg:.2f}% = $4.66M · ES₉₉ = {es_mult:.2f}σ = {es_mult*sg:.2f}% = ${es_mult*sg:.2f}M")
    x0, y0, w, h = 50, 46, 480, 185
    sx, sy = frame(out, x0, y0, w, h, [(-8, "−8%"), (-6, "−6%"), (-4, "−4%"), (-2, "−2%"), (0, "0"), (2, "+2%"), (4, "+4%"), (6, "+6%"), (8, "+8%")], [(0, "0"), (0.15, ""), (0.3, "")], xlab="ผลตอบแทนรายวัน", ylab="ความหนาแน่น", grid_y=False)
    tail = xs <= -z99 * sg
    poly = [(sx(a), sy(b)) for a, b in zip(xs[tail], pdf[tail])] + [(sx(-z99 * sg), sy(0)), (sx(-8), sy(0))]
    out.append('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in poly) + f'" fill="{RED}" opacity="0.35"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(xs, pdf)], BLUE, 2.5)
    # หางอ้วน: t ν=4 ปรับให้ σ เท่ากัน
    nu = 4; sc = sg / np.sqrt(nu / (nu - 2))
    from math import gamma
    tpdf = gamma((nu + 1) / 2) / (np.sqrt(nu * np.pi) * gamma(nu / 2) * sc) * (1 + (xs / sc) ** 2 / nu) ** (-(nu + 1) / 2)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(xs, tpdf)], AMBER, 1.8, dash="5 3", shadow=False)
    vx = -z99 * sg; ex = -es_mult * sg
    out.append(f'<line x1="{sx(vx):.1f}" y1="{y0+20}" x2="{sx(vx):.1f}" y2="{sy(0):.1f}" stroke="{PURPLE}" stroke-width="1.8" stroke-dasharray="5 3"/>')
    out.append(f'<text x="{sx(vx):.1f}" y="{y0+14}" text-anchor="middle" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">VaR₉₉ = −{z99*sg:.2f}% ($4.66M)</text>')
    out.append(f'<circle cx="{sx(ex):.1f}" cy="{sy(0):.1f}" r="4.5" fill="#fff" stroke="{RED}" stroke-width="2.4"/>')
    out.append(f'<line x1="{sx(ex):.1f}" y1="{sy(0)-6:.1f}" x2="{sx(ex):.1f}" y2="{y0+52}" stroke="{RED}" stroke-width="1" stroke-dasharray="2 2"/>')
    out.append(f'<text x="{sx(-7.9):.1f}" y="{y0+36}" {FONT} font-size="9.5" fill="{RED}" font-weight="700">ES₉₉ = −{es_mult*sg:.2f}% (${es_mult*sg:.2f}M)</text>')
    out.append(f'<text x="{sx(-7.9):.1f}" y="{y0+48}" {FONT} font-size="9" fill="{RED}">= ค่าเฉลี่ยของพื้นที่แดง (1% ของวัน) — อยู่ลึกกว่าเส้น VaR เสมอ</text>')
    out.append(f'<text x="{x0+w-4}" y="{sy(0.12):.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{AMBER}" font-weight="700">เส้นประ = หางอ้วน (t, ν = 4) σ เท่ากัน</text>')
    out.append(f'<text x="{x0+w-4}" y="{sy(0.12)+13:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">หางจริงหนากว่า normal — ES จาก normal ยังต่ำเกินจริง</text>')
    out.append("</svg>")
    return "\n".join(out)


# ══ Payoff 4/5 · ตาของ Arbitrageur 3 · Arb 8 · statarb-ledger · ทฤษฎี A·6 ═══════════════════

# ── Payoff 5 บทที่ 19: combined payoff = ผลรวมของขา ประเมินที่ราคาเดียวกัน ──
@fig("pm-part5.html", "combined-payoff")
def fig_combined_payoff():
    S = np.linspace(70, 130, 121)
    lc = np.maximum(S - 100, 0) - 5; sp = 3 - np.maximum(95 - S, 0); st = S - 100; comb = lc + sp + st
    NUMS["combined-payoff"] = dict(at90=float(np.interp(90, S, comb)), lc90=-5.0, sp90=-2.0, st90=-10.0)
    Wd, H = 560, 320
    out = svg_open(Wd, H, "payoff ของสามขา Long Call 100, Short Put 95, Long Stock ที่ 100 และเส้นรวม · ที่ S = 90 เส้นรวมอยู่ที่ −17 = −5 −2 −10")
    title(out, Wd, "combined payoff — บวก y ของทุกขาที่ราคาเดียวกัน ทีละจุด", "Long Call K=100 (P=5) · Short Put K=95 (P=3) · Long Stock ซื้อที่ 100 · ตัวอย่างในบท: S = 90")
    x0, y0, w, h = 55, 46, 475, 210
    sx, sy = frame(out, x0, y0, w, h, [(70, "70"), (80, "80"), (90, "90"), (100, "100"), (110, "110"), (120, "120"), (130, "130")], [(-60, "−60"), (-40, "−40"), (-20, "−20"), (0, "0"), (20, "+20"), (40, "+40"), (60, "+60")], xlab="ราคาหุ้น S ณ วันหมดอายุ", ylab="P/L (฿)")
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, lc)], GREEN, 1.6, dash="5 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, sp)], RED, 1.6, dash="5 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, st)], AMBER, 1.6, dash="5 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, comb)], BLUE, 2.75)
    for v, col, dy in [(-5, GREEN, 0), (-2, RED, 0), (-10, AMBER, 0)]:
        out.append(f'<circle cx="{sx(90):.1f}" cy="{sy(v):.1f}" r="3.2" fill="{col}"/>')
    c90 = float(np.interp(90, S, comb))
    out.append(f'<line x1="{sx(90):.1f}" y1="{sy(3):.1f}" x2="{sx(90):.1f}" y2="{sy(c90):.1f}" stroke="{PURPLE}" stroke-width="1" stroke-dasharray="2 2"/>')
    out.append(f'<circle cx="{sx(90):.1f}" cy="{sy(c90):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
    out.append(f'<text x="{sx(90)+8:.1f}" y="{sy(c90)+18:.1f}" {FONT} font-size="10" fill="{PURPLE}" font-weight="700">S = 90: −5 + (−2) + (−10) = {c90:.0f}</text>')
    out.append(f'<text x="{x0+6}" y="{y0+14}" {FONT} font-size="9.5" fill="{BLUE}" font-weight="700">เส้นรวมชัน +2 ทั้งเหนือ 100 (หุ้น + call) และใต้ 95 (หุ้น + short put)</text>')
    out.append(f'<text x="{x0+6}" y="{y0+28}" {FONT} font-size="9.5" fill="{BLUE}">→ ขาลงเจ็บสองเท่าของหุ้นเปล่า — risk ที่ดูทีละขาไม่เห็น</text>')
    legend(out, [(BLUE, "รวม 3 ขา", ""), (GREEN, "Long Call 100", "5 3"), (RED, "Short Put 95", "5 3"), (AMBER, "Long Stock @100", "5 3")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── Payoff 5 บทที่ 20: Greeks อ่านจากเส้นโค้ง — slope Δ · ความโค้ง Γ · หด (Θ) · กว้าง (ν) ──
@fig("pm-part5.html", "visual-greeks")
def fig_visual_greeks():
    S = np.linspace(70, 130, 121)
    c_far = bs_greeks(S, T=0.5)["C"] - 6.89; c_near = bs_greeks(S, T=0.1)["C"] - 6.89; c_hv = bs_greeks(S, T=0.5, sg=0.30)["C"] - 6.89
    pay = np.maximum(S - 100, 0) - 6.89; g0 = bs_greeks(100.0, T=0.5)
    NUMS["visual-greeks"] = dict(delta=float(g0["delta"]), c_near_100=float(bs_greeks(100.0, T=0.1)["C"]), c_hv_100=float(bs_greeks(100.0, T=0.5, sg=0.30)["C"]))
    Wd, H = 560, 320
    out = svg_open(Wd, H, "P/L ของ Long Call 100 ก่อนหมดอายุเป็นเส้นโค้งเหนือเส้นหักศอกที่หมดอายุ · ความชันที่ ATM คือ Delta · ความโค้งคือ Gamma · เส้นโค้งหดเข้าหาเส้นหักศอกเมื่อเวลาผ่าน (Theta) และถ่างออกเมื่อ vol เพิ่ม (Vega)")
    title(out, Wd, "อ่าน Greeks ด้วยตาจากเส้นโค้งเส้นเดียว — slope · ความโค้ง · หด · ถ่าง", "Long Call K=100 ซื้อที่ ฿6.89 (S=100, σ=20%, r=5%, T=0.5) · เส้นหักศอก = ณ วันหมดอายุ")
    x0, y0, w, h = 55, 46, 475, 210
    sx, sy = frame(out, x0, y0, w, h, [(70, "70"), (80, "80"), (90, "90"), (100, "100"), (110, "110"), (120, "120"), (130, "130")], [(-10, "−10"), (0, "0"), (10, "+10"), (20, "+20"), (30, "+30")], xlab="ราคาหุ้น S วันนี้", ylab="P/L (฿)")
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, pay)], INK2, 1.6, dash="5 4", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, c_hv)], AMBER, 1.8, dash="6 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, c_near)], GREEN, 1.8, dash="3 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, c_far)], BLUE, 2.75)
    D = float(g0["delta"])
    out.append(f'<line x1="{sx(90):.1f}" y1="{sy(D*(90-100)):.1f}" x2="{sx(110):.1f}" y2="{sy(D*(110-100)):.1f}" stroke="{PURPLE}" stroke-width="1.6"/>')
    out.append(f'<circle cx="{sx(100):.1f}" cy="{sy(0):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
    out.append(f'<text x="{x0+6}" y="{y0+14}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">Δ = ความชันของเส้นสัมผัสที่ ATM = {D:.2f} (เส้นม่วง)</text>')
    out.append(f'<text x="{x0+6}" y="{y0+28}" {FONT} font-size="9.5" fill="{PURPLE}">Γ = ความโค้ง — โค้งสุดตรง ATM ตรงที่เส้นตรงกลายเป็นเส้นหักศอก</text>')
    out.append(f'<text x="{x0+6}" y="{y0+42}" {FONT} font-size="9.5" fill="{GREEN}" font-weight="700">Θ: เวลาผ่านไป (T=0.5 → 0.1) เส้นโค้งหดเข้าหาเส้นหักศอก</text>')
    out.append(f'<text x="{x0+6}" y="{y0+56}" {FONT} font-size="9.5" fill="{AMBER}" font-weight="700">ν: vol ขึ้น (20% → 30%) เส้นโค้งถ่างออกจากเส้นหักศอก</text>')
    legend(out, [(BLUE, "วันนี้ T=0.5 σ=20%", ""), (GREEN, "เหลือ T=0.1", "3 3"), (AMBER, "σ=30%", "6 3"), (INK2, "หมดอายุ", "5 4")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── Payoff 4 บทที่ 16: overround — ความน่าจะเป็นโดยนัยรวม 106.5% แล้วหารกลับให้เต็ม 100 ──
@fig("pm-part4.html", "overround-bars")
def fig_overround_bars():
    odds = [2.10, 3.30, 3.50]; imp = [1 / o for o in odds]; tot = sum(imp); fair = [p / tot for p in imp]
    NUMS["overround-bars"] = dict(tot=tot * 100, over=(tot - 1) * 100, **{f"imp{i}": p * 100 for i, p in enumerate(imp)}, **{f"fair{i}": p * 100 for i, p in enumerate(fair)})
    Wd, H = 560, 260
    out = svg_open(Wd, H, "แท่งซ้อนสองแท่ง: ความน่าจะเป็นโดยนัยจาก odds 2.10, 3.30, 3.50 รวม 106.5% เกินเส้น 100% อยู่ 6.5% · แท่งขวาหารกลับด้วย 1.065 จนรวม 100% พอดี")
    title(out, Wd, "overround — ผลลัพธ์ที่ตัดกันขาดต้องรวม 100% ส่วนที่เกินคือค่าธรรมเนียมที่ซ่อนในราคา", "odds 2.10 / 3.30 / 3.50 → 1/odds = 47.6% + 30.3% + 28.6% = 106.5% · หารด้วย 1.065 → 44.7% + 28.5% + 26.9%")
    x0, y0, w, h = 60, 46, 470, 165
    cols = [BLUE, GREEN, AMBER]; names = ["ทีม A (2.10)", "เสมอ (3.30)", "ทีม B (3.50)"]
    def sy(v): return y0 + h - v / 110 * h
    for gx, vals, lab in [(x0 + 90, imp, "ที่ bookmaker ตั้ง"), (x0 + 300, fair, "หารกลับ (de-vig)")]:
        acc = 0
        for k, v in enumerate(vals):
            out.append(f'<rect x="{gx}" y="{sy(acc+v*100):.1f}" width="90" height="{sy(acc)-sy(acc+v*100):.1f}" fill="{cols[k]}" opacity="0.8"/>')
            out.append(f'<text x="{gx+45}" y="{(sy(acc)+sy(acc+v*100))/2+4:.1f}" text-anchor="middle" {FONT} font-size="10" fill="#fff" font-weight="700">{v*100:.1f}%</text>')
            acc += v * 100
        out.append(f'<text x="{gx+45}" y="{y0+h+14}" text-anchor="middle" {FONT} font-size="10" fill="{INK}" font-weight="700">{lab} — รวม {acc:.1f}%</text>')
    out.append(f'<line x1="{x0}" y1="{sy(100):.1f}" x2="{x0+w}" y2="{sy(100):.1f}" stroke="{RED}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    out.append(f'<text x="{x0+w}" y="{sy(100)-5:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{RED}" font-weight="700">100% — ความน่าจะเป็นจริงรวมได้แค่นี้</text>')
    out.append(f'<rect x="{x0+90}" y="{sy(tot*100):.1f}" width="90" height="{sy(100)-sy(tot*100):.1f}" fill="none" stroke="{RED}" stroke-width="2"/>')
    out.append(f'<text x="{x0+190}" y="{sy(100)+12:.1f}" {FONT} font-size="9.5" fill="{RED}" font-weight="700">← overround {(tot-1)*100:.1f}%</text>')
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.2"/>')
    legend(out, [(cols[k], names[k], "") for k in range(3)], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── ตา 3 Case A: funding −0.03%/8 ชม. สะสมทั้งปี 1,095 รอบ = 32.85% (ไม่ทบต้น) ──
@fig("eye-part3.html", "funding-carry")
def fig_funding_carry():
    per = 0.0003; n = 3 * 365; k = np.arange(n + 1); simple = per * k * 100; comp = (np.power(1 + per, k) - 1) * 100
    NUMS["funding-carry"] = dict(simple=simple[-1], comp=comp[-1], rounds=n)
    Wd, H = 560, 280
    out = svg_open(Wd, H, "funding 0.03% ต่อ 8 ชั่วโมงสะสมเป็นเส้นตรงถึง 32.85% ต่อปีเมื่อคิดไม่ทบต้น 1,095 รอบ · เส้นประคือถ้าทบต้น · แถบเตือนว่าอัตราพลิกได้ทุก 8 ชั่วโมง")
    title(out, Wd, "3 bp ต่อรอบดูไม่มีอะไร — จนเห็นว่ามันเกิด 1,095 รอบต่อปี", f"0.03% × 3 รอบ/วัน × 365 วัน = {simple[-1]:.2f}% (ไม่ทบต้น) · ถ้าทบต้นทุกรอบ = {comp[-1]:.1f}% · สมมติอัตราคงที่ทั้งปี")
    x0, y0, w, h = 55, 46, 475, 180
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (91, "3 เดือน"), (182, "6 เดือน"), (273, "9 เดือน"), (365, "1 ปี")], [(0, "0"), (10, "10%"), (20, "20%"), (30, "30%"), (40, "40%")], xlab="เวลาที่ถือ (วัน)", ylab="funding สะสม (% ของ notional)")
    days = k / 3
    polyline(out, [(sx(a), sy(b)) for a, b in zip(days[::9], comp[::9])], INK2, 1.6, dash="5 4", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(days[::9], simple[::9])], GREEN, 2.75)
    out.append(f'<circle cx="{sx(365):.1f}" cy="{sy(simple[-1]):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
    out.append(f'<text x="{sx(365)-8:.1f}" y="{sy(simple[-1])+14:.1f}" text-anchor="end" {FONT} font-size="10" fill="{PURPLE}" font-weight="700">1 ปี = {n:,} รอบ × 0.03% = {simple[-1]:.2f}%</text>')
    out.append(f'<text x="{sx(250):.1f}" y="{sy(comp[750])-10:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">ทบต้น (นำ funding ไปเพิ่ม position) → {comp[-1]:.1f}% ที่ 1 ปี</text>')
    d1 = 30; out.append(f'<text x="{sx(d1)+6:.1f}" y="{sy(simple[d1*3])-8:.1f}" {FONT} font-size="9.5" fill="{GREEN}">1 เดือน ≈ {simple[d1*3]:.1f}%</text>')
    out.append(f'<text x="{x0+6}" y="{y0+14}" {FONT} font-size="9.5" fill="{RED}" font-weight="700">[Heuristic] เส้นนี้ฉายอัตรา "ปัจจุบัน" ไปทั้งปี — funding พลิกเครื่องหมายได้ทุก 8 ชั่วโมง</text>')
    legend(out, [(GREEN, "ไม่ทบต้น (ตามที่บทคิด)", ""), (INK2, "ทบต้นทุกรอบ", "5 4")], x0, H - 10)
    out.append("</svg>")
    return "\n".join(out)


# ── Arb 8 §30.2 PM parity: Ask(Yes) + Ask(No) เทียบ $1 ──
@fig("arb-part8.html", "pm-parity")
def fig_pm_parity():
    cases = [("ปกติ", 0.62, 0.40), ("โอกาส", 0.62, 0.36)]
    NUMS["pm-parity"] = dict(s1=1.02, s2=0.98, profit=0.02)
    Wd, H = 560, 250
    out = svg_open(Wd, H, "แท่งซ้อนราคา ask ของ Yes กับ No สองกรณี: 0.62 + 0.40 = 1.02 สูงกว่าเส้น 1 ดอลลาร์ ไม่มี arb · 0.62 + 0.36 = 0.98 ต่ำกว่า 1 ดอลลาร์ ซื้อทั้งคู่กำไร 2 เซนต์แน่")
    title(out, Wd, "PM parity — ถือ Yes กับ No พร้อมกันได้ $1 แน่ · ถามแค่ว่าจ่ายไปเท่าไร", "Ask(Yes) + Ask(No) ≥ $1.00 คือภาวะปกติ (spread ของ market maker) · ต่ำกว่า $1 คือโอกาส")
    x0, y0, w, h = 60, 46, 470, 150
    def sy(v): return y0 + h - v / 1.15 * h
    for gx, (lab, y_, n_) in zip([x0 + 70, x0 + 280], cases):
        s_ = y_ + n_
        out.append(f'<rect x="{gx}" y="{sy(y_):.1f}" width="110" height="{sy(0)-sy(y_):.1f}" fill="{BLUE}" opacity="0.8"/>')
        out.append(f'<text x="{gx+55}" y="{(sy(0)+sy(y_))/2+4:.1f}" text-anchor="middle" {FONT} font-size="10.5" fill="#fff" font-weight="700">Yes ${y_:.2f}</text>')
        out.append(f'<rect x="{gx}" y="{sy(s_):.1f}" width="110" height="{sy(y_)-sy(s_):.1f}" fill="{AMBER}" opacity="0.85"/>')
        out.append(f'<text x="{gx+55}" y="{(sy(y_)+sy(s_))/2+4:.1f}" text-anchor="middle" {FONT} font-size="10.5" fill="#fff" font-weight="700">No ${n_:.2f}</text>')
        col = INK if s_ >= 1 else GREEN
        out.append(f'<text x="{gx+55}" y="{sy(s_)-6:.1f}" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="{col}">รวม ${s_:.2f}</text>')
        out.append(f'<text x="{gx+55}" y="{y0+h+14}" text-anchor="middle" {FONT} font-size="10" fill="{INK2}">{lab}: {"ไม่มี arb (จ่ายเกิน $" + f"{s_-1:.2f}" + ")" if s_ >= 1 else "ซื้อทั้งคู่ กำไรแน่ $" + f"{1-s_:.2f}" + " ต่อชุด"}</text>')
    out.append(f'<line x1="{x0}" y1="{sy(1):.1f}" x2="{x0+w}" y2="{sy(1):.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 3"/>')
    out.append(f'<text x="{x0+4}" y="{sy(1)-5:.1f}" {FONT} font-size="9.5" fill="{RED}" font-weight="700">$1.00 ที่จะได้แน่เมื่อ settle</text>')
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.2"/>')
    out.append(f'<text x="{Wd/2:.0f}" y="{H-8}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">ใช้ราคา ask ทั้งคู่ (ราคาที่ซื้อได้จริง) · ยังไม่หัก fee และเงินที่ล็อกจนถึง settle</text>')
    out.append("</svg>")
    return "\n".join(out)


# ── statarb-ledger: state machine ของหนึ่งคู่ (แผนภาพ) ──
@fig("statarb-ledger.html", "pair-states")
def fig_pair_states():
    Wd, H = 560, 316
    out = svg_open(Wd, H, "แผนภาพสถานะของหนึ่งคู่ pairs: FLAT ไป ENTERING ไป OPEN ไป EXITING กลับ FLAT · ENTERING และ EXITING ที่เกินเวลาไป STUCK · ทุกสถานะไป HALTED ได้เมื่อความสัมพันธ์ขาด")
    title(out, Wd, "หนึ่งคู่ไม่ได้มีแค่ 'เปิด' กับ 'ปิด' — สถานะที่ต้องมีชื่อในโค้ด", "ลูกศรทึบ = ทางปกติ · ลูกศรประ = ทางที่ผิดแผน · 70 วินาทีที่ไม่ neutral อยู่ในกล่อง ENTERING")
    def box(x, y, name, sub, col, wd=110):
        out.append(f'<rect x="{x-wd/2:.0f}" y="{y-22}" width="{wd}" height="44" rx="8" fill="#fff" stroke="{col}" stroke-width="2"/>')
        out.append(f'<text x="{x}" y="{y-4}" text-anchor="middle" {FONT} font-size="12" font-weight="700" fill="{INK}">{name}</text>')
        out.append(f'<text x="{x}" y="{y+11}" text-anchor="middle" {FONT} font-size="9" fill="{col}">{sub}</text>')
    def arrow(x1, y1, x2, y2, col, dash="", lab="", lx=0, ly=0):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.8"{extra}/>')
        ang = np.arctan2(y2 - y1, x2 - x1); ax, ay = x2 - 9 * np.cos(ang), y2 - 9 * np.sin(ang)
        px, py = 4.5 * np.sin(ang), -4.5 * np.cos(ang)
        out.append(f'<polygon points="{x2:.1f},{y2:.1f} {ax+px:.1f},{ay+py:.1f} {ax-px:.1f},{ay-py:.1f}" fill="{col}"/>')
        if lab: out.append(f'<text x="{(x1+x2)/2+lx:.1f}" y="{(y1+y2)/2+ly:.1f}" text-anchor="middle" {FONT} font-size="9" fill="{col}">{lab}</text>')
    yA, yB = 122, 222
    box(70, yA, "FLAT", "ไม่มีสถานะทั้งสองขา", INK2, 100)
    box(210, yA, "ENTERING", "fill ยังไม่ครบสองขา", AMBER, 120)
    box(350, yA, "OPEN", "ครบสองขา รอ spread หุบ", GREEN, 120)
    box(490, yA, "EXITING", "ปิดยังไม่ครบ", AMBER, 110)
    box(280, yB, "STUCK", "ขาหนึ่งค้าง — คนตัดสิน", RED, 120)
    box(470, yB, "HALTED", "ความสัมพันธ์ขาด / tracking error เกิน", RED, 150)
    arrow(120, yA, 150, yA, INK, lab="เข้า", ly=-9)
    arrow(270, yA, 290, yA, INK, lab="ครบ", ly=-9)
    arrow(410, yA, 435, yA, INK, lab="ออก", ly=-9)
    # EXITING → FLAT (โค้งกลับด้านบน)
    out.append(f'<path d="M490,{yA-22} C490,52 70,52 70,{yA-22}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    out.append(f'<polygon points="70,{yA-22} 65,{yA-31} 75,{yA-31}" fill="{INK}"/>')
    out.append(f'<text x="280" y="62" text-anchor="middle" {FONT} font-size="9" fill="{INK}">ปิดครบ → กลับ FLAT · ledger ปิดบัญชีไม้นี้ · OPEN → EXITING เมื่อมีสัญญาณออกหรือ stop</text>')
    arrow(225, yA + 22, 265, yB - 22, RED, dash="4 3", lab="เกินเวลา", lx=-30, ly=4)
    arrow(475, yA + 22, 320, yB - 22, RED, dash="4 3", lab="เกินเวลา", lx=30, ly=-4)
    arrow(330, yB, 395, yB, RED, dash="4 3", lab="กฎที่เขียนไว้ก่อน", ly=-8)
    arrow(370, yA + 22, 440, yB - 22, RED, dash="4 3")
    out.append(f'<text x="{Wd/2:.0f}" y="{H-24}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">ENTERING/EXITING = ช่วงที่ net exposure ≠ 0 (ในบท: 5,340 บาทนาน 70 วินาที) — บันทึกทุก fill แยกบรรทัด</text>')
    out.append(f'<text x="{Wd/2:.0f}" y="{H-8}" text-anchor="middle" {FONT} font-size="9.5" fill="{RED}">HALTED เข้าได้จากทุกสถานะ (วาดจาก OPEN เพื่อไม่ให้รก) · STUCK ออกทาง EXITING หรือ FLAT ตามทางเลือก (ก)(ข)(ค)</text>')
    out.append("</svg>")
    return "\n".join(out)


# ── ทฤษฎี A·6: สายโซ่ 5 ทฤษฎี (แผนภาพ) ──
@fig("theory-part6.html", "theory-chain")
def fig_theory_chain():
    Wd, H = 560, 330
    out = svg_open(Wd, H, "แผนภาพสายโซ่ห้าทฤษฎี: Random Walk 1900 ไป Mean-Variance และ CAPM 1952–64 ไป EMH 1970 ไป Black-Scholes 1973 ไป Time Series และ Backtest 1982–2014 แล้ววนกลับไป Random Walk · แต่ละลูกศรคือคำถามที่ทฤษฎีก่อนทิ้งไว้")
    title(out, Wd, "ห้าตำนานคือบทสนทนาเดียว — แต่ละทฤษฎีตอบช่องโหว่ของทฤษฎีก่อนหน้า", "ปี = ผลงานหลัก · ข้อความบนลูกศร = คำถามที่ส่งต่อ · ลูกศรประ = วงปิดกลับไปที่จุดเริ่ม")
    nodes = [(95, 90, "Random Walk", "1900 · Bachelier", BLUE), (330, 90, "Mean-Variance · CAPM", "1952–64 · Markowitz · Sharpe", GREEN),
             (470, 180, "EMH", "1970 · Fama", AMBER), (330, 270, "Black-Scholes", "1973 · Black · Scholes · Merton", PURPLE), (95, 270, "Time Series · Backtest", "1982–2014 · Engle → López de Prado", RED)]
    for x, y, nm, sub, col in nodes:
        wd = 150 if len(nm) > 12 else 110
        out.append(f'<rect x="{x-wd/2:.0f}" y="{y-22}" width="{wd}" height="44" rx="10" fill="#fff" stroke="{col}" stroke-width="2.2"/>')
        out.append(f'<text x="{x}" y="{y-4}" text-anchor="middle" {FONT} font-size="11.5" font-weight="700" fill="{INK}">{nm}</text>')
        out.append(f'<text x="{x}" y="{y+11}" text-anchor="middle" {FONT} font-size="8.5" fill="{col}">{sub}</text>')
    def arrow(x1, y1, x2, y2, lab, lx, ly, dash=""):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.8"{extra}/>')
        ang = np.arctan2(y2 - y1, x2 - x1); ax, ay = x2 - 9 * np.cos(ang), y2 - 9 * np.sin(ang); px, py = 4.5 * np.sin(ang), -4.5 * np.cos(ang)
        out.append(f'<polygon points="{x2:.1f},{y2:.1f} {ax+px:.1f},{ay+py:.1f} {ax-px:.1f},{ay-py:.1f}" fill="{INK}"/>')
        out.append(f'<text x="{(x1+x2)/2+lx:.1f}" y="{(y1+y2)/2+ly:.1f}" text-anchor="middle" {FONT} font-size="9" fill="{INK2}">{lab}</text>')
    arrow(150, 90, 255, 90, "ทิศเดาไม่ได้ — แล้ววัดความเสี่ยงยังไง?", 0, -30)
    arrow(405, 100, 425, 160, "ราคาที่ 'ถูก' มาจากไหน?", 62, 0)
    arrow(425, 200, 405, 250, "ถ้า hedge ได้ ราคาถูกบังคับด้วย no-arb", -95, -4)
    arrow(255, 270, 170, 270, "vol คงที่ไม่จริง — วัดจากข้อมูล", 0, 28)
    arrow(95, 248, 95, 112, "ทุก edge คือ deviation จากความสุ่ม ที่ต้องพิสูจน์", 118, 0, dash="5 4")
    out.append(f'<text x="{Wd/2:.0f}" y="{H-8}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">คำว่า "เกือบ" ทุกตัว (เกือบ efficient · เกือบถูก · เกือบจริง) คือที่ที่ quant ทำมาหากิน — และที่ quant เจ๊ง</text>')
    out.append("</svg>")
    return "\n".join(out)


VOLUMES = [("คิดแบบ Quant", r"^nq-"), ("คณิตศาสตร์สำหรับ Options เล่ม 1", r"^math-part(1|2|3|6|7)\.html$"),
           ("คณิตศาสตร์สำหรับ Options เล่ม 2 · A–F", r"^math-part(4|5|8|9|10|11)\.html$"), ("Payoff Mastery", r"^pm-|^payoff-chart"),
           ("ทฤษฎีของ Quant (เล่ม A)", r"^theory-"), ("เสาหลัก (เล่ม B)", r"^pillars-"), ("Arbitrage", r"^arb-"),
           ("ตาของ Arbitrageur", r"^eye-"), ("statarb", r"^statarb-"), ("เครื่องมือ / หน้ารวม", r"^(tool|tools|notation|index|curriculum|quant-tool|case-|math-for)")]


# หน้าที่โดยธรรมชาติไม่ต้องมีภาพ (อภิธานศัพท์ · แผนที่ · หน้ารวม · เครื่องคิดเลข · ฉบับเล่าเรื่อง)
NO_FIG_NEEDED = r"-narrative|glossary|appendix-map|appendix-drills|runbook|^index|nq-index|tools-index|^tools\.|notation|curriculum|^tool-|nq-tool-|guide|critique|^case-"


def figure_map():
    """ตารางภาพประกอบต่อเล่ม: จำนวนไฟล์ · ไฟล์ที่ไม่มีภาพ · SVG ทั้งหมด · ภาพจาก generator"""
    import glob
    files = sorted(os.path.basename(f) for f in glob.glob(os.path.join(DOCS, "*.html")))
    gen = {}
    for (fl, nm) in FIGS: gen[fl] = gen.get(fl, 0) + 1
    rows = []
    for name, pat in VOLUMES:
        fs = [f for f in files if re.search(pat, f)]
        if not fs: continue
        n_svg = 0; empty = []
        for f in fs:
            s = open(os.path.join(DOCS, f), encoding="utf-8").read()
            k = sum(1 for m in re.finditer(r"<svg\b.*?</svg>", s, re.S) if len(m.group(0)) >= 200)
            n_svg += k
            if k == 0 and not re.search(NO_FIG_NEEDED, f): empty.append(f[:-5])
        g = sum(gen.get(f, 0) for f in fs)
        rows.append(f"<tr><td>{name}</td><td class=\"nw\">{len(fs)}</td><td class=\"nw\">{n_svg}</td><td class=\"nw\">{g}</td><td>{' · '.join(empty) if empty else '—'}</td></tr>")
    total_svg = sum(int(re.search(r'<td class="nw">\d+</td><td class="nw">(\d+)</td>', r).group(1)) for r in rows)
    return ("<h2 id=\"figmap\">ภาพประกอบ — บทไหนมีภาพ บทไหนยังไม่มี</h2>\n"
            f"<p>สร้างอัตโนมัติจาก <code>tools/make_figures.py --map</code> · SVG ทั้งคลัง {total_svg} ชิ้น · \"จาก generator\" = ภาพที่วาดจากข้อมูลชุดเดียวกับตัวตรวจตัวเลข (ตัวเลขในภาพกับในข้อความจึงตรงกันโดยโครงสร้าง) · คอลัมน์ขวาคือบทที่ยังไม่มีภาพเลย</p>\n"
            "<p><strong>แผนปรับภาพประกอบ (ก.ย. 2026):</strong> ส่วน 1 ข้อควรระวังของ regression (outlier · jump · robust) — เสร็จ · ส่วน 2 ภาพกลุ่ม PCA/OLS/first passage/logistic จาก generator — เสร็จ · ส่วน 3 ไล่ทั้งคลัง: ให้ aria-label ทุกภาพ · svg_qa ผ่านทั้งคลัง · ภาพจากข้อมูลให้ทฤษฎีของ Quant/เสาหลัก/Payoff 5a แล้ว — ที่เหลือคือบทในคอลัมน์ขวา</p>\n"
            "<div class=\"tw\"><table>\n<tr><th>เล่ม</th><th class=\"nw\">ไฟล์</th><th class=\"nw\">SVG</th><th class=\"nw\">จาก generator</th><th>บทที่ยังไม่มีภาพ</th></tr>\n" + "\n".join(rows) + "\n</table></div>")


def write_map():
    p = os.path.join(DOCS, "curriculum-map.html"); s = open(p, encoding="utf-8").read()
    b, e = "<!-- FIGMAP:BEGIN -->", "<!-- FIGMAP:END -->"
    assert b in s and e in s, "ไม่พบ marker FIGMAP ใน curriculum-map.html"
    new = re.sub(re.escape(b) + r".*?" + re.escape(e), lambda m: b + "\n" + figure_map() + "\n" + e, s, flags=re.S)
    if new != s: open(p, "w", encoding="utf-8").write(new); print("✏️  curriculum-map.html · ตารางภาพประกอบ เขียนแล้ว")
    return new != s


def main():
    check = "--check" in sys.argv
    bad = 0
    if "--map" in sys.argv:
        write_map(); return 0
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
    # ตารางภาพประกอบใน curriculum-map ต้องนับ SVG หลังเขียนภาพแล้ว
    if check:
        p = os.path.join(DOCS, "curriculum-map.html"); s0 = open(p, encoding="utf-8").read()
        if write_map():
            open(p, "w", encoding="utf-8").write(s0); print("❌ curriculum-map.html: ตารางภาพประกอบล้าสมัย — รัน python3 tools/make_figures.py"); bad += 1
    else:
        write_map()
    for nm, d in NUMS.items():
        print(f"   {nm}: " + " ".join(f"{k}={v:.4f}" for k, v in d.items()))
    print(f"ภาพ {len(FIGS)} ชิ้น · ปัญหา {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
