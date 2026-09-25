#!/usr/bin/env python3
"""วาดภาพประกอบ (inline SVG) จากข้อมูลชุดเดียวกับที่สคริปต์ทวนตัวเลขใช้ แล้วเขียนลงไฟล์ HTML
ระหว่าง marker  <!-- FIG:<ชื่อ>:BEGIN --> … <!-- FIG:<ชื่อ>:END -->

เหตุผล: ภาพที่มีตัวเลข (ความชัน, จุด, ระยะ) ต้องมาจากข้อมูลเดียวกับข้อความ ไม่ใช่วาดมือแล้วเดา
ใช้:  python3 tools/make_figures.py            → เขียนทุกภาพ (idempotent)
      python3 tools/make_figures.py --check    → ตรวจว่า SVG ในไฟล์ตรงกับที่สคริปต์สร้าง (exit 1 ถ้าไม่ตรง)
ต้องมี numpy
"""
import json
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FIGS = {}
_CUR = ["?"]  # ชื่อภาพที่กำลังวาด (ใช้ตอนรายงานข้อความล้นขอบ)
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


# สระ/วรรณยุกต์ไทยที่ซ้อนบน-ล่าง ไม่กินความกว้าง จึงไม่นับ
_COMBINING = set("\u0e31\u0e34\u0e35\u0e36\u0e37\u0e38\u0e39\u0e3a\u0e47\u0e48\u0e49\u0e4a\u0e4b\u0e4c\u0e4d\u0e4e")
WIDE = []  # (ชื่อภาพ, ชนิด, กว้างที่ประมาณได้, กว้างที่มีจริง) — เก็บไว้ให้ --check รายงาน


_NARROW = set("ijltfrI.,:;!|'\u2019 ")
# ความกว้างต่ออักษร (เท่าของ font-size) วัดจริงจาก Sarabun ในเบราว์เซอร์ด้วย getComputedTextLength
# แล้ว fit กำลังสองน้อยสุดจากหัวภาพ/คำโปรยทั้งคลัง 335 ชิ้น — คลาดเคลื่อนเฉลี่ย ~1.7%
_W_THAI, _W_NARROW, _W_LATIN, _W_SYM = 0.601, 0.293, 0.530, 0.404


def text_width(text, size):
    """ความกว้างโดยประมาณของข้อความ Sarabun (px) — ใช้กันหัวภาพ/คำโปรยล้นขอบ"""
    w = 0.0
    for ch in text:
        if ch in _COMBINING: continue          # สระ/วรรณยุกต์ซ้อน ไม่กินความกว้าง
        if ch in _NARROW: w += _W_NARROW
        elif "\u0e00" <= ch <= "\u0e7f": w += _W_THAI
        elif ch.isdigit() or ("a" <= ch <= "z") or ("A" <= ch <= "Z"): w += _W_LATIN
        else: w += _W_SYM
    return w * size


def title(out, W, text, sub=""):
    for t, size, kind in ((text, 12.5, "หัวภาพ"), (sub, 10.0, "คำโปรย")):
        if t and text_width(t, size) > W - 20: WIDE.append((_CUR[0], kind, text_width(t, size), W - 20))
    out.append(f'<text x="{W/2:.0f}" y="18" text-anchor="middle" {FONT} font-size="12.5" font-weight="700" fill="{INK}">{text}</text>')
    if sub: out.append(f'<text x="{W/2:.0f}" y="32" text-anchor="middle" {FONT} font-size="10" fill="{INK2}">{sub}</text>')


def legend(out, items, x, y):
    for col, lab, dash in items:
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{x}" y1="{y}" x2="{x+22}" y2="{y}" stroke="{col}" stroke-width="2.5"{extra}/><text x="{x+27}" y="{y+3.5}" {FONT} font-size="10" fill="{INK}">{lab}</text>')
        x += 27 + 6.2 * len(lab) + 18


def svg_open(W, H, label, multipanel=False, cls="d"):
    mp = ' data-legend="per-panel"' if multipanel else ""   # หลายพาเนล พาเนลละซีรีส์เดียว — ไม่ต้องมี legend รวม
    return [f'<svg class="{cls}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}"{mp}>',
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


_TEXT_TAG = re.compile(r'<text\b([^>]*)>')


def add_halo(svg):
    """ใส่ขอบขาวบาง ๆ หลังตัวอักษรทุกชิ้น — ข้อความที่บังเอิญวางทับเส้นกราฟจึงยังอ่านออก
    (paint-order="stroke" วาดเส้นขอบก่อนแล้วค่อยวาดตัวอักษรทับ จึงไม่ทำให้ตัวอักษรบวม)"""
    def one(m):
        tag = m.group(1)
        if "paint-order" in tag or "stroke=" in tag: return m.group(0)
        fill = re.search(r'fill="([^"]*)"', tag)
        if fill and fill.group(1).lower() in ("#fff", "#ffffff", "white"): return m.group(0)
        sz = re.search(r'font-size="([\d.]+)"', tag)
        w = max(2.0, float(sz.group(1)) * 0.26) if sz else 2.6
        return f'<text{tag} paint-order="stroke" stroke="#fff" stroke-width="{w:.1f}" stroke-linejoin="round" stroke-opacity="0.92">'
    return _TEXT_TAG.sub(one, svg)


def render_all():
    out = {}
    for (fl, nm), fn in FIGS.items():
        _CUR[0] = nm          # ให้ title() รู้ว่ากำลังวาดภาพไหน เวลารายงานข้อความล้นขอบ
        out[(fl, nm)] = add_halo(fn())
    return out



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
    out.append(f'<text x="{sx2(im)+dx:.1f}" y="{sy2(sg[im]*100)-20:.1f}" text-anchor="{anc}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">σ พุ่งถึง {sg[im]*100:.1f}% หลังวันช็อก</text>')
    out.append(f'<text x="{sx2(im)+dx:.1f}" y="{sy2(sg[im]*100)-8:.1f}" text-anchor="{anc}" {FONT} font-size="9.5" fill="{PURPLE}">ส่วนเกินของ σ² เหนือ long-run หายไป 2% ของที่เหลือทุกวัน (half-life ≈ {np.log(0.5)/np.log(0.98):.0f} วัน)</text>')
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
    out.append(f'<text x="{sx(0.168):.1f}" y="{sy(1.08):.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">ถ้าเป็นเส้นตรง (สัญชาตญาณผิด)</text>')
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
    out.append(f'<text x="{sx(90)+8:.1f}" y="{sy(c90)+18:.1f}" {FONT} font-size="10" fill="{PURPLE}" font-weight="700">S = 90: −5 + (−2) + (−10) = −{abs(c90):.0f}</text>')
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
    title(out, Wd, "อ่าน Greeks ด้วยตาจากเส้นโค้งเส้นเดียว — slope · ความโค้ง · หด · ถ่าง", "Long Call K=100 ซื้อที่ ฿6.89 (ราคา BS: S=100, σ=20%, r=5%, T=0.5) · เส้นหักศอก = ณ วันหมดอายุ")
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
    out.append(f'<text x="{x0+6}" y="{y0+28}" {FONT} font-size="9.5" fill="{PURPLE}">Γ = ความโค้ง — โค้งสุดที่ ATM (จุดที่ slope เปลี่ยนเร็วที่สุด)</text>')
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
    title(out, Wd, "overround — ผลลัพธ์ที่ตัดกันขาดต้องรวม 100% ส่วนที่เกินคือค่าธรรมเนียมที่ซ่อนในราคา", f"odds 2.10 / 3.30 / 3.50 → 1/odds = {imp[0]*100:.1f}% + {imp[1]*100:.1f}% + {imp[2]*100:.1f}% = {tot*100:.1f}% · หารด้วย {tot:.3f} → {fair[0]*100:.1f}% + {fair[1]*100:.1f}% + {fair[2]*100:.1f}%")
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
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (91, "3 เดือน"), (182, "6 เดือน"), (273, "9 เดือน"), (365, "1 ปี")], [(0, "0"), (10, "10%"), (20, "20%"), (30, "30%"), (40, "40%")], xlab="เวลาที่ถือ", ylab="funding สะสม (% ของ notional)")
    days = k / 3
    polyline(out, [(sx(a), sy(b)) for a, b in zip(days[::9], comp[::9])], INK2, 1.6, dash="5 4", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(days[::9], simple[::9])], GREEN, 2.75)
    out.append(f'<circle cx="{sx(365):.1f}" cy="{sy(simple[-1]):.1f}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.4"/>')
    out.append(f'<text x="{sx(365)-8:.1f}" y="{sy(18):.1f}" text-anchor="end" {FONT} font-size="10" fill="{PURPLE}" font-weight="700">1 ปี = {n:,} รอบ × 0.03% = {simple[-1]:.2f}%</text>')
    out.append(f'<text x="{sx(250):.1f}" y="{sy(comp[750])-10:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">ทบต้น (นำ funding ไปเพิ่ม position) → {comp[-1]:.1f}% ที่ 1 ปี</text>')
    d1 = 30; out.append(f'<text x="{sx(d1)-6:.1f}" y="{sy(simple[d1*3])-6:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{GREEN}">1 เดือน ≈ {simple[d1*3]:.1f}%</text>')
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
    out.append(f'<text x="{x0-4}" y="{sy(1)+3.5:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{RED}" font-weight="700">$1.00</text>')
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
    arrow(410, yA, 435, yA, INK, lab="ออก/stop", ly=-9)
    # EXITING → FLAT (โค้งกลับด้านบน)
    out.append(f'<path d="M490,{yA-22} C490,52 70,52 70,{yA-22}" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    out.append(f'<polygon points="70,{yA-22} 65,{yA-31} 75,{yA-31}" fill="{INK}"/>')
    out.append(f'<text x="280" y="56" text-anchor="middle" {FONT} font-size="9" fill="{INK}">ปิดครบ → กลับ FLAT · ledger ปิดบัญชีไม้นี้</text>')
    arrow(225, yA + 22, 265, yB - 22, RED, dash="4 3", lab="เกินเวลา", lx=-30, ly=4)
    arrow(475, yA + 22, 320, yB - 22, RED, dash="4 3", lab="เกินเวลา", lx=30, ly=-4)
    arrow(220, yB, 85, yA + 22, RED, dash="4 3", lab="คนตัดสิน / กฎที่เขียนไว้ก่อน", lx=-55, ly=-4)
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
             (470, 180, "EMH", "1970 · Fama", AMBER), (330, 270, "Black-Scholes", "1973 · Black · Scholes · Merton", PURPLE), (95, 270, "Time Series · Backtest", "1982–2014 · Engle · López de Prado", RED)]
    for x, y, nm, sub, col in nodes:
        wd = 160 if len(nm) > 20 else 150 if len(nm) > 12 else 110
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
    arrow(255, 270, 170, 270, "vol คงที่ไม่จริง — วัดจากข้อมูล", 0, 33)
    arrow(95, 248, 95, 112, "ทุก edge คือ deviation จากความสุ่ม ที่ต้องพิสูจน์", 118, 0, dash="5 4")
    out.append(f'<text x="{Wd/2:.0f}" y="{H-8}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">คำว่า "เกือบ" ทุกตัว (เกือบ efficient · เกือบถูก · เกือบจริง) คือที่ที่ quant ทำมาหากิน — และที่ quant เจ๊ง</text>')
    out.append("</svg>")
    return "\n".join(out)


# ══ เครื่องวาด payoff diagram — ทุกภาพ payoff ในคลังวาดจาก spec ของขา ═══════════════════════
from payoff_lib import Leg, value, strikes, segments, summary, net_premium, slope_between  # noqa: E402

LEG_COLORS = [GREEN, RED, AMBER, PURPLE, "#0891b2", "#be185d"]
KIND_TH = {"call": "Call", "put": "Put", "stock": "Stock", "bond": "Bond", "dcall": "Digital Call", "dput": "Digital Put"}


def leg_name(l):
    side = "Long" if l.qty > 0 else "Short"
    n = "" if abs(l.qty) == 1 else f"{abs(l.qty):g}× "
    if l.kind == "stock": return f"{side} {n}Stock @{l.K:g}"
    if l.kind == "bond": return f"Bond เงินต้น {l.K:g}"
    return f"{side} {n}{KIND_TH[l.kind]}({l.K:g})"


def fmt(v):
    s = f"{v:+g}" if abs(v) < 1e6 else f"{v:+.3g}"
    return s.replace("-", "−")


def _pts(legs, lo, hi, with_premium):
    """จุดของเส้น payoff ระหว่าง lo..hi รวมรอยกระโดดของ digital"""
    ks = [k for k in strikes(legs) if lo < k < hi]
    pts = [(lo, value(legs, lo, with_premium))]
    for k in ks:
        fl, fr = value(legs, k - 1e-9, with_premium), value(legs, k + 1e-9, with_premium)
        pts.append((k, fl))
        if abs(fl - fr) > 1e-9: pts.append((k, fr))
    pts.append((hi, value(legs, hi, with_premium)))
    return pts


def _nice_ticks(lo, hi, n=5):
    span = hi - lo
    if span <= 0: return [lo]
    raw = span / n; mag = 10 ** np.floor(np.log10(raw)); step = mag * min([1, 2, 2.5, 5, 10], key=lambda m: abs(m * mag - raw))
    a = np.floor(lo / step) * step; b = np.ceil(hi / step) * step
    return [round(v, 6) for v in np.arange(a, b + step / 2, step)]


def _draw_payoff(out, legs, box, *, with_premium=True, show_legs=True, slopes=False, overlays=(), fill=True,
                 callouts=True, xr=None, notes=(), total_color=BLUE, total_label=None, ylab="P/L (฿)", xlab="ราคาสินทรัพย์ S ณ วันหมดอายุ", xticks=None, be_below=False, unbounded_dy=-8,
                 strike_fmt=None, compact=False, ytick_fmt=None):
    x0, y0, w, h = box
    all_legs = list(legs) + [l for o in overlays for l in o["legs"]]
    ks = strikes(all_legs) or [100]
    tick_ks = list(xticks) if xticks is not None else ks  # สไตรก์ที่ติดป้ายบนแกน X (ค่าเริ่มต้น = ทุกสไตรก์รวม overlay)
    sm = summary(legs, with_premium)
    if xr is None:
        span = max(ks) - min(ks); pad = max(10.0, 0.6 * span) if span else 30.0
        lo, hi = min(ks) - pad, max(ks) + pad
        for b in sm["breakevens"]:
            lo, hi = min(lo, b - pad * 0.4), max(hi, b + pad * 0.4)
        lo = max(0.0, lo)
    else:
        lo, hi = xr
    lines = [(legs, with_premium, total_color, 2.75, "", True)]
    for o in overlays:
        lines.append((o["legs"], o.get("with_premium", with_premium), o.get("color", INK2), o.get("width", 1.8), o.get("dash", "6 3"), False))
    leg_lines = [([l], with_premium, LEG_COLORS[i % len(LEG_COLORS)], 1.5, "5 3") for i, l in enumerate(legs)] if show_legs and len(legs) > 1 else []
    ys = [0.0]
    for lg, wp, *_ in lines + [(a, b, None) for a, b, *_ in leg_lines]:
        ys += [y for _, y in _pts(lg, lo, hi, wp)]
    ymin, ymax = min(ys), max(ys)
    if ymax - ymin < 1e-9: ymin, ymax = ymin - 10, ymax + 10
    padv = (ymax - ymin) * 0.12; ymin -= padv; ymax += padv
    yt = _nice_ticks(ymin, ymax, 4 if compact else 5); ymin, ymax = min(yt), max(yt)
    def sx(v): return x0 + (v - lo) / (hi - lo) * w
    def sy(v): return y0 + h - (v - ymin) / (ymax - ymin) * h
    fs = 8.5 if compact else 9.5
    # grid + แกน
    out.append(f'<g stroke="{GRID}" stroke-width="1">' + "".join(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}"/>' for v in yt if abs(v) > 1e-9) + "</g>")
    for k in tick_ks:
        if lo <= k <= hi: out.append(f'<line x1="{sx(k):.1f}" y1="{y0}" x2="{sx(k):.1f}" y2="{y0+h}" stroke="{GRID}" stroke-width="1" stroke-dasharray="3 3"/>')
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.2"/>')
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    for v in yt:
        lab = (ytick_fmt(v) if ytick_fmt else fmt(v).replace("+", ""))
        out.append(f'<text x="{x0-5}" y="{sy(v)+3.5:.1f}" text-anchor="end" {FONT} font-size="{fs}" fill="{INK2}">{lab}</text>')
    for k in tick_ks:
        if lo <= k <= hi:
            lab = strike_fmt(k) if strike_fmt else f"{k:g}"
            out.append(f'<text x="{sx(k):.1f}" y="{y0+h+13}" text-anchor="middle" {FONT} font-size="{fs}" fill="{INK}" font-weight="600">{lab}</text>')
    if not compact:
        out.append(f'<text x="{x0+w}" y="{y0+h+27}" text-anchor="end" {FONT} font-size="9.5" fill="{INK2}">{xlab}</text>')
        out.append(f'<text transform="rotate(-90)" x="{-(y0 + h/2):.1f}" y="{x0-38}" text-anchor="middle" {FONT} font-size="9.5" fill="{INK2}">{ylab}</text>')
    # พื้นที่กำไร/ขาดทุนใต้เส้นรวม
    tp = _pts(legs, lo, hi, with_premium)
    if fill:
        dense = []
        for (xa, ya), (xb, yb) in zip(tp[:-1], tp[1:]):
            dense.append((xa, ya))
            if ya * yb < 0 and xb != xa: dense.append((xa + (0 - ya) * (xb - xa) / (yb - ya), 0.0))
        dense.append(tp[-1])
        for (xa, ya), (xb, yb) in zip(dense[:-1], dense[1:]):
            if xb == xa: continue
            col = GREEN if (ya + yb) > 0 else RED
            out.append(f'<polygon points="{sx(xa):.1f},{sy(0):.1f} {sx(xa):.1f},{sy(ya):.1f} {sx(xb):.1f},{sy(yb):.1f} {sx(xb):.1f},{sy(0):.1f}" fill="{col}" opacity="0.10"/>')
    # ขาแยก (ประ) · overlays · เส้นรวม (hero)
    for lg, wp, col, wd, dash in leg_lines:
        polyline(out, [(sx(a), sy(b)) for a, b in _pts(lg, lo, hi, wp)], col, wd, dash=dash, shadow=False)
    # แถบเรือง (halo) ใต้เส้นรวม: ให้เห็นเส้นรวมแม้ขาย่อย/overlay จะทับพอดี (เช่น parity, bracket)
    out.append(f'<g opacity="0.22">'); polyline(out, [(sx(a), sy(b)) for a, b in tp], total_color, 8, shadow=False); out.append('</g>')
    polyline(out, [(sx(a), sy(b)) for a, b in tp], total_color, 2.75)
    for lg, wp, col, wd, dash, is_total in lines[1:]:
        polyline(out, [(sx(a), sy(b)) for a, b in _pts(lg, lo, hi, wp)], col, wd, dash=dash, shadow=False)
    def _tbox(xpx, ybase, anc, tw):  # กล่องข้อความโดยประมาณ (x0, y0, x1, y1) หน่วย px
        xl = xpx - tw if anc == "end" else xpx if anc == "start" else xpx - tw / 2
        return (xl, ybase - 9, xl + tw, ybase + 2)
    def _hit(b1, b2, pad=3):
        return not (b1[2] + pad < b2[0] or b2[2] + pad < b1[0] or b1[3] + pad < b2[1] or b2[3] + pad < b1[1])
    be_boxes = []
    # callouts · กราฟ payoff ก่อนหักเบี้ย (with_premium=False) ไม่เรียก "กำไร/ขาดทุน/BE" เพื่อไม่ให้สับสนกับ profit
    W_MAX, W_MIN, W_BE, W_UP, W_DN = (("กำไรสูงสุด", "ขาดทุนสูงสุด", "BE", "กำไรไม่จำกัด →", "ขาดทุนไม่จำกัด →") if with_premium
                                     else ("payoff สูงสุด", "payoff ต่ำสุด", "ตัดศูนย์", "ขึ้นไม่จำกัด →", "ลงไม่จำกัด →"))
    if callouts:
        d = 0.01 * (hi - lo)
        for i, b in enumerate(sm["breakevens"]):
            if lo <= b <= hi and value(legs, b - d, with_premium) * value(legs, b + d, with_premium) < 0:  # ต้องเปลี่ยนเครื่องหมายจริง
                out.append(f'<circle cx="{sx(b):.1f}" cy="{sy(0):.1f}" r="4.2" fill="#fff" stroke="{PURPLE}" stroke-width="2.2"/>')
                # ป้ายวางเฉียงขึ้น ฝั่งที่เส้นอยู่ต่ำกว่าศูนย์ (ไม่ทับเส้นที่กำลังไต่ผ่านศูนย์)
                s_here = slope_between(legs, b - 1e-6, b + 1e-6)
                if s_here > 0: anc, dx = "end", -7
                elif s_here < 0: anc, dx = "start", 7
                else: anc, dx = "middle", 0
                if be_below: anc, dx = ("start", 7) if anc == "end" else ("end", -7) if anc == "start" else (anc, dx)
                be_boxes.append(_tbox(sx(b) + dx, sy(0) + (16 if be_below else -8), anc, 6 * len(f"{W_BE} {b:g}")))
                out.append(f'<text x="{sx(b)+dx:.1f}" y="{sy(0)+(16 if be_below else -8):.1f}" text-anchor="{anc}" {FONT} font-size="{fs}" fill="{PURPLE}" font-weight="700">{W_BE} {b:g}</text>')
        mp, mpa, ml, mla = sm["max_profit"], sm["max_profit_at"], sm["max_loss"], sm["max_loss_at"]
        if mp is not None and mp > 0:
            xa = min(max(mpa, lo), hi); anc = "start" if xa < (lo + hi) / 2 else "end"; dx = 6 if anc == "start" else -6
            if mpa >= hi - 1e-9 or (sm["right_slope"] == 0 and mpa == max(ks) and value(legs, hi, with_premium) == mp): xa, anc, dx = hi, "end", -4
            tail = " (ที่ S = 0)" if mpa == 0 and lo > 0 else ""
            yy = sy(min(mp, ymax)) if mpa >= lo else sy(value(legs, lo, with_premium))
            out.append(f'<text x="{sx(xa)+dx:.1f}" y="{yy-6:.1f}" text-anchor="{anc}" {FONT} font-size="{fs}" fill="{GREEN}" font-weight="700">{W_MAX} {fmt(mp)}{tail}</text>')
        elif mp is None:
            out.append(f'<text x="{x0+w-4}" y="{sy(value(legs, hi, with_premium))+unbounded_dy:.1f}" text-anchor="end" {FONT} font-size="{fs}" fill="{GREEN}" font-weight="700">{W_UP}</text>')
        if ml is not None and ml < 0:
            if mla <= lo + 1e-9:
                out.append(f'<text x="{x0+4}" y="{sy(value(legs, lo, with_premium))+14:.1f}" {FONT} font-size="{fs}" fill="{RED}" font-weight="700">{W_MIN} {fmt(ml)}' + (f" (ที่ S = 0)" if mla == 0 and lo > 0 and sm["left_slope"] != 0 else "") + '</text>')
            else:
                anc = "start" if mla < (lo + hi) / 2 else "end"; dx = 6 if anc == "start" else -6
                out.append(f'<text x="{sx(mla)+dx:.1f}" y="{sy(ml)+14:.1f}" text-anchor="{anc}" {FONT} font-size="{fs}" fill="{RED}" font-weight="700">{W_MIN} {fmt(ml)}</text>')
        elif ml is None:
            out.append(f'<text x="{x0+w-4}" y="{sy(value(legs, hi, with_premium))+14:.1f}" text-anchor="end" {FONT} font-size="{fs}" fill="{RED}" font-weight="700">{W_DN}</text>')
    if slopes:
        for a, b, s, fa, fb in segments(legs, lo, hi, with_premium):
            xm = (a + b) / 2
            # ป้าย slope อย่าให้ทับป้าย BE ที่อยู่บนช่วงเดียวกัน: ขยับจุดยึดออกห่าง ≥ 55px ไปฝั่งที่มีที่ว่างมากกว่า
            lab0 = "แบน (slope 0)" if abs(s) < 1e-9 else f"slope {fmt(s)}"
            tw0 = 6 * len(lab0)
            anc0, dx0, dy0 = ("middle", 0, -8) if abs(s) < 1e-9 else ("end", -7, -5) if s > 0 else ("start", 7, -5)
            def _box_at(x):
                return _tbox(sx(x) + dx0, sy(value(legs, x, with_premium)) + dy0, anc0, tw0)
            for bb in be_boxes:  # ถ้าป้าย slope ทับป้าย BE ให้เลื่อนไปทางที่ขยับน้อยกว่าแต่ยังอยู่ในช่วง
                if _hit(_box_at(xm), bb):
                    step = (b - a) / 40; cands = []
                    for sgn in (1, -1):
                        x = xm
                        for _ in range(40):
                            x += sgn * step
                            if not (a + 0.05 * (b - a) <= x <= b - 0.05 * (b - a)): break
                            if not _hit(_box_at(x), bb): cands.append((abs(x - xm), x)); break
                    if cands: xm = min(cands)[1]
            ym = value(legs, xm, with_premium)
            lab = "แบน (slope 0)" if abs(s) < 1e-9 else f"slope {fmt(s)}"
            below = abs(s) < 1e-9 and sm["max_profit"] is not None and abs(ym - sm["max_profit"]) < 1e-9 and ym > 0
            if abs(s) < 1e-9 and ym < 0 and leg_lines:  # พื้นราบใต้ศูนย์และมีขาประ: วางป้ายใต้เส้น ค่อนไปทางขวา
                below = True; xm = a + 0.62 * (b - a); ym = value(legs, xm, with_premium)
            # ตัวเลือกตำแหน่ง (anchor, dx, dy): ลองฝั่งแรกก่อน ถ้าทับเส้นขาประให้สลับไปอีกฝั่ง
            if abs(s) < 1e-9: opts = [("middle", 0, 14), ("middle", 0, -8)] if below else [("middle", 0, -8), ("middle", 0, 14)]
            elif s > 0: opts = [("end", -7, -5), ("start", 7, 14)]
            else: opts = [("start", 7, -5), ("end", -7, 14)]
            tw = 6 * len(lab)  # ความกว้างป้ายโดยประมาณ (px)
            def _clear(anc, dx, dy):
                xl = sx(xm) + dx + (tw / 2 if anc == "start" else -tw / 2 if anc == "end" else 0); yc = sy(ym) + dy - 3.5
                for lg, wp, *_ in leg_lines:
                    for px in (xl - tw / 2, xl, xl + tw / 2):
                        xx = lo + (px - x0) / w * (hi - lo)
                        if lo <= xx <= hi and abs(sy(value(lg, xx, wp)) - yc) < 8: return False
                return True
            anc, dx, dy = next((o for o in opts if _clear(*o)), opts[0])
            out.append(f'<text x="{sx(xm)+dx:.1f}" y="{sy(ym)+dy:.1f}" text-anchor="{anc}" {FONT} font-size="{fs}" fill="{INK2}" font-style="italic">{lab}</text>')
    for n in notes:  # (x, y, text, color, anchor, dy)
        x, y, text, col = n[:4]; anc = n[4] if len(n) > 4 else "start"; dy = n[5] if len(n) > 5 else 0
        out.append(f'<text x="{sx(x):.1f}" y="{sy(y)+dy:.1f}" text-anchor="{anc}" {FONT} font-size="{fs}" fill="{col}" font-weight="600">{text}</text>')
    dflt = ("profit (หักเบี้ยแล้ว)" if len(legs) == 1 else "รวมทุกขา (หักเบี้ยแล้ว)") if with_premium else ("payoff ณ วันหมดอายุ" if len(legs) == 1 else "payoff รวม ณ วันหมดอายุ")
    items = [(total_color, total_label or dflt, "")]
    items += [(col, leg_name(lg[0]), "5 3") for lg, wp, col, wd, dash in leg_lines]
    items += [(o.get("color", INK2), o["label"], o.get("dash", "6 3")) for o in overlays]
    return sm, items, (sx, sy, lo, hi)


def payoff_fig(legs, title_text, sub="", *, W=560, H=310, legend_rows=1, **kw):
    out = svg_open(W, H, kw.pop("aria", title_text))
    title(out, W, title_text, sub)
    box = (55, 48, W - 55 - 22, H - 48 - 66 - (legend_rows - 1) * 15)
    sm, items, _ = _draw_payoff(out, legs, box, **kw)
    per = max(1, int(np.ceil(len(items) / legend_rows)))
    for r in range(legend_rows):
        legend(out, items[r * per:(r + 1) * per], 55, H - 10 - (legend_rows - 1 - r) * 15)
    out.append("</svg>")
    return "\n".join(out), sm


def payoff_grid(panels, title_text, sub="", *, W=560, H=400, cols=2, **kw):
    """หลายพาเนลเล็ก · panels = [(legs, ชื่อพาเนล, opts), …]"""
    out = svg_open(W, H, kw.pop("aria", title_text), multipanel=True)
    title(out, W, title_text, sub)
    rows = int(np.ceil(len(panels) / cols)); pw = (W - 60) / cols - 20; ph = (H - 70) / rows - 40
    sms = []
    for i, (legs, name, opts) in enumerate(panels):
        cx = 50 + (i % cols) * (pw + 40); cy = 62 + (i // cols) * (ph + 40)
        out.append(f'<text x="{cx + pw/2:.0f}" y="{cy-6}" text-anchor="middle" {FONT} font-size="11" font-weight="700" fill="{INK}">{name}</text>')
        o = dict(kw); o.update(opts); o.setdefault("compact", True); o.setdefault("show_legs", False)
        sm, _, _ = _draw_payoff(out, legs, (cx, cy, pw, ph), **o); sms.append(sm)
    out.append("</svg>")
    return "\n".join(out), sms


def payoff(file, name, legs, title_text, sub="", **kw):
    """ลงทะเบียนภาพ payoff หนึ่งชิ้น และเก็บสรุปตัวเลข (BE, กำไร/ขาดทุนสูงสุด, เบี้ยสุทธิ) ไว้ใน NUMS"""
    def fn():
        svg, sm = payoff_fig(legs, title_text, sub, **kw)
        NUMS[name] = {k: (v if v is not None else float("nan")) for k, v in sm.items() if k != "breakevens"}
        NUMS[name].update({f"be{i+1}": b for i, b in enumerate(sm["breakevens"])})
        return svg
    FIGS[(file, name)] = fn
    return fn


# ── Payoff Mastery Part 0 — ขั้นตอนอ่านกราฟ (K = 100 · เบี้ย 5 ตามเล่ม) ────────────────────
LC = [Leg("call", 100, 1, 5)]; SC = [Leg("call", 100, -1, 5)]; LP = [Leg("put", 100, 1, 5)]; SP = [Leg("put", 100, -1, 5)]
payoff("pm-part0.html", "p0-payoff-vs-profit", LC,
       "Payoff กับ Profit ต่างกันแค่เลื่อนลงเท่าเบี้ย 5 — รูปร่างและความชันเหมือนเดิม",
       "Long Call K = 100 · เบี้ย 5 · เส้นทึบ = profit (หักเบี้ยแล้ว) · เส้นประ = payoff (ก่อนหักเบี้ย)",
       overlays=[dict(legs=[Leg("call", 100, 1, 0)], label="payoff ก่อนหักเบี้ย max(S − K, 0)", color=INK2)],
       notes=[(85, -2.5, "ระยะห่าง = เบี้ย 5", RED, "start", 3), (129, 4, "ทั้งสองเส้นชัน +1 เท่ากัน", INK2, "end", 0)], slopes=False, unbounded_dy=-22)
payoff("pm-part0.html", "p0-step1-long-call", LC,
       "ขั้นตอนที่ 1 — Long Call: แบนที่ −5 จนถึง K แล้วหักขึ้นชัน +1 ตัดศูนย์ที่ K + เบี้ย",
       "Long Call K = 100 · เบี้ย 5 · BE = 100 + 5 = 105 · ขาดทุนสูงสุด = เบี้ยที่จ่าย", slopes=True)
payoff("pm-part0.html", "p0-step2-short-call", SC,
       "ขั้นตอนที่ 2 — Short Call คือ Long Call พลิกหัวกลับ: กำไรจำกัดที่เบี้ย ขาดทุนไม่จำกัด",
       "Short Call K = 100 · รับเบี้ย 5 · เส้นประ = Long Call เดิม · สังเกตว่า BE อยู่ที่ 105 เท่ากัน",
       overlays=[dict(legs=LC, label="Long Call (พลิกกลับได้เส้นนี้)", color=INK2)], slopes=True)
payoff("pm-part0.html", "p0-put-pair", LP,
       "ขั้นตอนที่ 2.5 — Long Put ชันลง −1 ทางซ้าย · Short Put คือภาพพลิก ชันขึ้น +1 แล้วแบนที่ +5",
       "K = 100 · เบี้ย 5 · BE ทั้งคู่ = 100 − 5 = 95 · Short Put ขาดทุนได้ถึง −95 ที่ S = 0",
       overlays=[dict(legs=SP, label="Short Put (พลิกกลับ)", color=RED, dash="6 3", width=2.2)], slopes=True, xr=(60, 140),
       notes=[(80, -20, "slope +1", RED, "middle", 14)])
payoff("pm-part0.html", "p0-step3-bull-call-spread", [Leg("call", 100, 1, 0), Leg("call", 110, -1, 0)],
       "ขั้นตอนที่ 3 — รวมสองขา: วาดทีละขาแล้วบวก y ที่ราคาเดียวกัน ได้ Bull Call Spread",
       "Long Call(100) + Short Call(110) · ภาพนี้เป็น payoff ณ วันหมดอายุ ยังไม่หักเบี้ย · ปลายขวาแบนเพราะ +1 − 1 = 0",
       with_premium=False, slopes=True, xr=(80, 130))


def payoff_grid_reg(file, name, panels, title_text, sub="", **kw):
    def fn():
        svg, sms = payoff_grid(panels, title_text, sub, **kw)
        for (legs, pname, _), sm in zip(panels, sms):
            NUMS[f"{name}/{pname}"] = {k: (v if v is not None else float("nan")) for k, v in sm.items() if k != "breakevens"}
        return svg
    FIGS[(file, name)] = fn


USD = dict(ylab="payoff ($)", ytick_fmt=lambda v: f"${v:g}".replace("$-", "−$"))

# ── Payoff Mastery Part 1 ─────────────────────────────────────────────────────────────────
payoff_grid_reg("pm-part1.html", "p1-four-blocks",
                [(LC, "Long Call — ขาดทุนจำกัด −5 · กำไรไม่จำกัด", {}), (SC, "Short Call — กำไรจำกัด +5 · ขาดทุนไม่จำกัด", {}),
                 (LP, "Long Put — ขาดทุนจำกัด −5 · กำไรถึง +95", {}), (SP, "Short Put — กำไรจำกัด +5 · ขาดทุนถึง −95", {})],
                "4 ตัวต่อพื้นฐาน — K = 100 · เบี้ย 5 · Short คือ Long พลิกหัว", "ทุกภาพสเกลเดียวกัน · BE ของ Call = 105 · BE ของ Put = 95", xr=(60, 140))
payoff("pm-part1.html", "p1-pcp-overlay", [Leg("call", 100, 1, 0), Leg("bond", 100, 1, 0)],
       "Put-Call Parity ในภาพ — Call + Bond กับ Put + Stock ให้ payoff เส้นเดียวกันทุกจุด",
       "ทั้งสองข้าง = max(S, 100) ณ วันหมดอายุ · เส้นซ้อนกันพอดี → ราคาวันนี้จึงต้องเท่ากัน (C + PV(K) = P + S)",
       with_premium=False, show_legs=False, xr=(60, 140), callouts=False,
       overlays=[dict(legs=[Leg("put", 100, 1, 0), Leg("stock", 0, 1, 0)], label="Put(100) + Stock", color=RED, dash="7 4", width=2.2)],
       total_label="Call(100) + Bond เงินต้น 100", ylab="มูลค่า ณ วันหมดอายุ (฿)",
       notes=[(120, 120, "= max(S, 100) ทั้งคู่", PURPLE, "middle", -8), (75, 100, "แบนที่ 100 (bond / put คุ้มกัน)", INK2, "start", -8)])

# ── Payoff Mastery Part 2 ─────────────────────────────────────────────────────────────────
payoff("pm-part2.html", "p2-bull-call-spread", [Leg("call", 90, 1, 8), Leg("call", 110, -1, 3)],
       "Bull Call Spread 90/110 เบี้ยสุทธิ 5 — เริ่มที่ −5 · ชัน +1 ที่ 90 · กลับมาแบนที่ 110",
       "ขั้น 1 ระดับเริ่ม = −(เบี้ยสุทธิ) = −5 · ขั้น 2 เดินขวา ปรับ slope ทุกสไตรก์ · ปลายขวา +1 − 1 = 0 → กำไรสูงสุด −5 + 20 = +15",
       show_legs=False, slopes=True, xr=(70, 130))
payoff("pm-part2.html", "p2-straddle-strangle", [Leg("call", 100, 1, 5), Leg("put", 100, 1, 5)],
       "Long Straddle กับ Long Strangle — ตัว V สองแบบ ยิ่งถูก ยิ่งต้องวิ่งไกล",
       "ตัวอย่างสมมติ: Straddle ซื้อ Call + Put ที่ 100 เบี้ยรวม 10 · Strangle ซื้อ Put 90 + Call 110 เบี้ยรวม 4",
       show_legs=False, xr=(70, 130),
       overlays=[dict(legs=[Leg("put", 90, 1, 2), Leg("call", 110, 1, 2)], label="Long Strangle 90/110 (เบี้ยรวม 4)", color=AMBER, dash="6 3", width=2.2)],
       total_label="Long Straddle 100 (เบี้ยรวม 10)")
payoff("pm-part2.html", "p2-covered-call-short-put", [Leg("stock", 100, 1, 0), Leg("call", 100, -1, 5)],
       "Covered Call กับ Short Put — รูปเดียวกันทุกจุด ต่างแค่ PV(K) ของเงินที่ต้องวางวันนี้",
       "สมมติเบี้ยเท่ากัน 5 (S = PV(K)) · หุ้นซื้อที่ 100 + ขาย Call(100) · เทียบขาย Put(100) · ชัน +1 ทางซ้าย แบนที่ +5 ทางขวา",
       show_legs=False, slopes=True, xr=(60, 140),
       overlays=[dict(legs=SP, label="Short Put(100) รับเบี้ย 5", color=RED, dash="7 4", width=2.2)],
       total_label="Covered Call = Stock @100 + Short Call(100)")
payoff("pm-part2.html", "p2-collar", [Leg("stock", 100, 1, 0), Leg("put", 90, 1, 3), Leg("call", 110, -1, 3)],
       "Collar — หุ้น + Long Put(90) + Short Call(110): ตัดทั้งขาดทุนและกำไร",
       "ตัวอย่างสมมติ zero-cost: เบี้ย Put ที่จ่าย = เบี้ย Call ที่รับ = 3 · เส้นประ = ถือหุ้นเปล่า",
       show_legs=False, slopes=True, xr=(60, 140),
       overlays=[dict(legs=[Leg("stock", 100, 1, 0)], label="ถือหุ้นเปล่า (ซื้อที่ 100)", color=INK2)],
       total_label="Collar")

# ── Payoff Mastery Part 3 ─────────────────────────────────────────────────────────────────
BF = [Leg("call", 90, 1, 12), Leg("call", 100, -2, 6), Leg("call", 110, 1, 3)]
payoff("pm-part3.html", "p3-butterfly", BF,
       "Long Call Butterfly 90/100/110 — เต็นท์ยอดแหลม ยอด = ความกว้าง − เบี้ยสุทธิ = 10 − 3 = +7",
       "+1 Call(90) −2 Call(100) +1 Call(110) · เบี้ยสุทธิ 3 · slope 0 → +1 → −1 → 0 · บวกเลขหน้าทุกขา +1 − 2 + 1 = 0 → ปลายแบน",
       show_legs=False, slopes=True, xr=(80, 120))
payoff("pm-part3.html", "p3-iron-condor", [Leg("put", 90, 1, 1), Leg("put", 95, -1, 2), Leg("call", 105, -1, 2), Leg("call", 110, 1, 1)],
       "Iron Condor 90/95/105/110 — ที่ราบสูงตรงกลาง กำไรสูงสุด = เบี้ยสุทธิที่รับ 2",
       "Bull Put Spread(90,95) + Bear Call Spread(105,110) · ขาดทุนสูงสุด = −(ความกว้าง 5 − เบี้ย 2) = −3 · ตัวเลขตามตัวอย่างในบท",
       show_legs=False, slopes=True, xr=(80, 120))
payoff("pm-part3.html", "p3-ratio-1x2", [Leg("call", 100, 1, 0), Leg("call", 110, -2, 0)],
       "Ratio Call Spread 1×2 — เต็นท์ข้างเดียว: ยอดที่ 110 แล้วชันลง −1 ไม่มีพื้น",
       "Long 1 Call(100) + Short 2 Call(110) · payoff ณ วันหมดอายุ ยังไม่หักเบี้ย · +1 − 2 = −1 ≠ 0 → ขาดทุนไม่จำกัดทางขวา",
       with_premium=False, slopes=False, xr=(85, 135),
       notes=[(92, 0, "แบน (slope 0)", INK2, "middle", -8), (103, 3, "slope +1", INK2, "end", 14), (121, -1, "slope −1", INK2, "middle", 16)])

# ── Payoff Mastery Part 3a — วิธี slope และ reverse engineering ─────────────────────────────
payoff("pm-part3a.html", "p3a-active-zone", [Leg("put", 90, 1, 0), Leg("put", 100, -1, 0)],
       "โซนที่ขา 'ทำงาน' — ฝั่งซ้ายของ Iron Condor: Long Put(90) + Short Put(100)",
       "ซ้ายของ 90 ทั้งสองขา active: −1 + 1 = 0 หักล้างกัน · ระหว่าง 90–100 มีแต่ Short Put: +1 · เหนือ 100 ไม่มีขาไหนทำงาน: 0",
       with_premium=False, show_legs=True, slopes=True, xr=(70, 120), callouts=False, legend_rows=1)
payoff("pm-part3a.html", "p3a-re-bull-call-spread", [Leg("call", 100, 1, 0), Leg("call", 110, -1, 0)],
       "ตัวอย่างที่ 1 — ลำดับความชัน 0 → +1 → 0 ถอดเป็น +1 ที่ 100 และ −1 ที่ 110",
       "Long Call(100) + Short Call(110) · เช็ค s₀ + ΣΔs = 0 + 1 − 1 = 0 = ความชันปลายขวา ✓",
       with_premium=False, show_legs=True, slopes=True, xr=(85, 125))
payoff("pm-part3a.html", "p3a-3x-cap", [Leg("call", 100, 3, 0), Leg("call", 110, -3, 0)],
       "ตัวอย่างที่ 2 — slope +3 แล้วกลับเป็น 0: 3× Bull Call Spread 100/110",
       "Long 3 Call(100) + Short 3 Call(110) · payoff สูงสุด 3 × 10 = 30 (ก่อนหักเบี้ยสุทธิ) · ขาดทุนสูงสุด = เบี้ยสุทธิ",
       with_premium=False, show_legs=False, slopes=True, xr=(85, 125))
payoff("pm-part3a.html", "p3a-asymmetric", [Leg("call", 95, 2, 0), Leg("call", 105, -3, 0), Leg("call", 115, 1, 0)],
       "ตัวอย่างที่ 3 — ความชันไม่สมมาตร +2 → −1 → 0: เต็นท์เอียงซ้าย",
       "Long 2 Call(95) + Short 3 Call(105) + Long 1 Call(115) · Δs = +2, −3, +1 รวม 0 → ปลายขวาแบน (bounded)",
       with_premium=False, show_legs=False, slopes=True, xr=(80, 130))
payoff("pm-part3a.html", "p3a-mixed-4sp", [Leg("call", 100, 1, 0), Leg("put", 100, -4, 0), Leg("call", 100, -1, 0)],
       "LC(100) + 4× SP(100) + SC(100) — ปลายขวาแบน แต่ซ้ายชัน +4: ราคาลงเจ็บสี่เท่า",
       "payoff ณ วันหมดอายุ ยังไม่หักเบี้ย · Call สองขาหักล้างกัน เหลือ 4× Short Put(100) · slope ซ้าย +4 · ขวา 0",
       with_premium=False, show_legs=False, slopes=True, xr=(80, 120))
payoff("pm-part3a.html", "p3a-re-butterfly", BF,
       "RE ตัวอย่างที่ 1 — Butterfly จากกราฟ: Δs = +1 ที่ 90, −2 ที่ 100, +1 ที่ 110",
       "เบี้ยสุทธิ 3 → ยอดที่ 100 = −3 + 10 = +7 · ปลายขวา 0 + 1 − 2 + 1 = 0 ✓",
       show_legs=False, slopes=False, xr=(80, 120),
       notes=[(90, -3, "Δs = +1", PURPLE, "middle", 16), (101, 7, "Δs = −2", PURPLE, "start", 2), (110, -3, "Δs = +1", PURPLE, "middle", 16)])
payoff("pm-part3a.html", "p3a-re-covered-call", [Leg("stock", 100, 1, 0), Leg("call", 100, -1, 0)],
       "RE ตัวอย่างที่ 3 — เริ่มชัน +1 แล้วแบนที่ 100: s₀ = +1 คือหุ้น · Δs = −1 คือ Short Call",
       "Long Stock @100 + Short Call(100) = Covered Call · payoff ยังไม่รวมเบี้ยที่รับ",
       with_premium=False, show_legs=True, slopes=True, xr=(70, 130), callouts=False)

# ── Payoff Mastery Part 4a — prediction market เป็น digital option ──────────────────────────
payoff("pm-part4a.html", "p4a-above-yes", [Leg("dcall", 100, 1, 0)],
       "PM Above Yes(100) — จ่าย $1 ถ้า S > 100 ไม่ว่าจะเกินไปเท่าไร: บันไดขั้นเดียว",
       "เส้นประ = Call Spread 100/105 ÷ 5 (ทางลาดที่จ่ายสูงสุด $1 พอดี) · ยิ่งสเปรดแคบ ยิ่งใกล้บันได",
       with_premium=False, show_legs=False, xr=(85, 115), callouts=False,
       overlays=[dict(legs=[Leg("call", 100, 0.2, 0), Leg("call", 105, -0.2, 0)], label="Call Spread 100/105 ÷ 5", color=AMBER, dash="6 3", width=2)],
       total_label="PM Above Yes(100)", **USD)
payoff("pm-part4a.html", "p4a-above-no", [Leg("dput", 100, 1, 0)],
       "PM Above No(100) — จ่าย $1 คงที่เมื่อ S < 100 · ไม่ใช่ Long Put ที่จ่ายมากขึ้นเมื่อราคาลงแรง",
       "เส้นประ = Long Put(100) ÷ 10: ที่ S = 90 ได้ $1 เท่ากัน แต่ที่ S = 80 ได้ $2 ส่วน PM ยังได้ $1",
       with_premium=False, show_legs=False, xr=(75, 115), callouts=False,
       overlays=[dict(legs=[Leg("put", 100, 0.1, 0)], label="Long Put(100) ÷ 10 (เชิงเส้น)", color=AMBER, dash="6 3", width=2)],
       total_label="PM Above No(100)", **USD)
payoff("pm-part4a.html", "p4a-range-yes", [Leg("dcall", 90, 1, 0), Leg("dcall", 110, -1, 0)],
       "PM Range Yes(90–110) — จ่าย $1 เมื่ออยู่ในช่วง = Digital Call(90) − Digital Call(110)",
       "เส้นประ = Butterfly 90/100/110 ÷ 10 (สามเหลี่ยม) · Range Yes คือสามเหลี่ยมที่ถูกดันเป็นสี่เหลี่ยม",
       with_premium=False, show_legs=False, xr=(75, 125), callouts=False,
       overlays=[dict(legs=[Leg("call", 90, 0.1, 0), Leg("call", 100, -0.2, 0), Leg("call", 110, 0.1, 0)], label="Butterfly 90/100/110 ÷ 10", color=AMBER, dash="6 3", width=2)],
       total_label="PM Range Yes(90–110)", **USD)
payoff("pm-part4a.html", "p4a-range-no", [Leg("dput", 90, 1, 0), Leg("dcall", 110, 1, 0)],
       "PM Range No(90–110) — จ่าย $1 เมื่ออยู่นอกช่วง: ส่วนกลับของ Range Yes",
       "Digital Put(90) + Digital Call(110) · ช่องว่างตรงกลางคือ $0 · คล้าย Strangle แต่จ่ายเป็นขั้น",
       with_premium=False, show_legs=False, xr=(75, 125), callouts=False, total_label="PM Range No(90–110)", **USD)
payoff("pm-part4a.html", "p4a-parity", [Leg("dcall", 100, 1, 0), Leg("dput", 100, 1, 0)],
       "PM Parity — Above Yes + Above No = $1 เสมอ ไม่ว่าราคาจะจบที่ไหน",
       "ถือทั้งสองขาได้ $1 แน่ · ราคา Yes + No จึงต้อง ≈ $1 (ต่างได้แค่ค่า spread) มิฉะนั้นมี arb",
       with_premium=False, show_legs=True, xr=(80, 120), callouts=False, total_label="Yes + No", **USD)
payoff("pm-part4a.html", "p4a-brackets", [Leg("dput", 90, 1, 0), Leg("dcall", 90, 1, 0)],
       "Multi-bracket — ปูกระเบื้องราคา: ทุกช่วงรวมกัน = $1 เสมอ (Generalized Parity)",
       "ช่วง <90 · 90–100 · 100–110 · >110 · แต่ละช่วงคือ Range Yes หนึ่งชิ้น · ผลรวมทุกชิ้น = เส้นแบนที่ $1",
       with_premium=False, show_legs=False, xr=(75, 125), callouts=False, legend_rows=2, total_label="ผลรวมทุก bracket", **USD,
       overlays=[dict(legs=[Leg("dput", 90, 1, 0)], label="<90", color=GREEN, dash="", width=1.8),
                 dict(legs=[Leg("dcall", 90, 1, 0), Leg("dcall", 100, -1, 0)], label="90–100", color=AMBER, dash="", width=1.8),
                 dict(legs=[Leg("dcall", 100, 1, 0), Leg("dcall", 110, -1, 0)], label="100–110", color=PURPLE, dash="", width=1.8),
                 dict(legs=[Leg("dcall", 110, 1, 0)], label=">110", color=RED, dash="", width=1.8)])
payoff("pm-part4a.html", "p4a-staircase", [Leg("dcall", k, 1, 0) for k in (90, 95, 100, 105, 110)],
       "PM Staircase — ซ้อน Above Yes ห่างกัน d = 5 ห้าขั้น ได้บันไดที่เฉลี่ยแล้วชัน 1/5",
       "Above Yes(90) + (95) + (100) + (105) + (110) · เส้นประ = เส้นตรงอุดมคติ slope $0.20 ต่อ $1 · ระหว่างขั้น payoff ไม่ขยับเลย",
       with_premium=False, show_legs=False, xr=(80, 120), callouts=False, total_label="บันได 5 ขั้น", **USD,
       xticks=(90, 95, 100, 105, 110),
       overlays=[dict(legs=[Leg("call", 87.5, 0.2, 0), Leg("call", 112.5, -0.2, 0)], label="เส้นตรงอุดมคติ (slope 1/5 · ตันที่ $5)", color=AMBER, dash="6 3", width=2)])

# ── Payoff Mastery Part 7 — structured products ────────────────────────────────────────────
payoff("pm-part7.html", "p7-eln", [Leg("bond", 100, 1, 0), Leg("call", 100, 0.5, 0)],
       "ELN = พันธบัตรไม่มีคูปอง + Long Call: แบนซ้าย (เงินต้นคืน) ชันขวา (ร่วมขาขึ้นบางส่วน)",
       "เงินต้น 100 · participation 50% ของส่วนที่เกิน K = 100 · ตัวอย่างสมมติ · เส้นประ = ถือหุ้นเปล่า",
       with_premium=False, show_legs=True, xr=(60, 160), callouts=False, ylab="มูลค่าที่ได้คืน (฿ ต่อเงินต้น 100)",
       overlays=[dict(legs=[Leg("stock", 0, 1, 0)], label="ถือหุ้นเปล่า (= S)", color=INK2)], total_label="ELN",
       notes=[(75, 100, "เงินต้นคืน 100 ทุกกรณี (ถ้าผู้ออกไม่ผิดนัด)", GREEN, "start", -8), (150, 125, "slope 0.5 = participation", INK2, "end", 16)])
payoff("pm-part7.html", "p7-risk-reversal", [Leg("put", 90, -1, 0), Leg("call", 110, 1, 0)],
       "Risk Reversal — Short Put(90) + Long Call(110): synthetic forward ที่มีช่องว่างตรงกลาง",
       "slope +1 → 0 → +1 · payoff ณ วันหมดอายุ ยังไม่หักเบี้ย (โครงสร้างนี้มักตั้งให้เบี้ยหักกันเป็นศูนย์)",
       with_premium=False, show_legs=True, slopes=True, xr=(70, 130), callouts=False)

# ── Payoff Mastery Part 8 — ปรับ position ระหว่างทาง และ DW ───────────────────────────────
payoff("pm-part8.html", "p8-roll-up", [Leg("call", 110, -1, 0)],
       "Roll Up — ปิด Short Call(100) เปิด Short Call(110): จุดหักศอกเลื่อนขวา ได้ upside room อีก 10",
       "payoff ณ วันหมดอายุ ยังไม่รวมเบี้ย · การ roll ขึ้นมักต้องจ่าย debit เพราะขาเดิม ITM แพงกว่าขาใหม่ OTM",
       with_premium=False, show_legs=False, slopes=True, xr=(80, 130), callouts=False,
       overlays=[dict(legs=[Leg("call", 100, -1, 0)], label="ก่อน roll: Short Call(100)", color=RED, dash="6 3", width=2.2)],
       total_label="หลัง roll: Short Call(110)")
payoff("pm-part8.html", "p8-dw-vs-vanilla", [Leg("call", 100, 1, 6), Leg("call", 120, -1, 0)],
       "DW กับ Vanilla Call — รูปคล้ายกัน แต่ DW แพงกว่า และรุ่นที่มี cap จะมีเพดาน",
       "ตัวอย่างสมมติ: Vanilla Call(100) เบี้ย 5 · DW สไตรก์ 100 เบี้ย 6 (issuer margin) สมมติมี cap ที่ 120",
       show_legs=False, xr=(80, 140),
       overlays=[dict(legs=[Leg("call", 100, 1, 5)], label="Vanilla Call(100) เบี้ย 5", color=INK2)], total_label="DW (cap 120 · เบี้ย 6)")


# ── Payoff 3 บทที่ 12 · study-guide 6.3: Calendar spread ที่วันหมดอายุของขาใกล้ (เส้นโค้งจาก BS) ──
def calendar_data(S0=100.0, K=100.0, r=0.05, sg=0.20, T1=1 / 12, T2=3 / 12):
    c_near = float(bs_greeks(S0, K=K, r=r, sg=sg, T=T1)["C"]); c_far = float(bs_greeks(S0, K=K, r=r, sg=sg, T=T2)["C"])
    debit = c_far - c_near
    S = np.linspace(70, 130, 121)
    far_left = bs_greeks(S, K=K, r=r, sg=sg, T=T2 - T1)["C"]
    pl = far_left - np.maximum(S - K, 0) - debit
    return S, pl, debit, c_near, c_far


def _calendar_svg(title_text, sub):
    S, pl, debit, c_near, c_far = calendar_data()
    Wd, H = 560, 314
    out = svg_open(Wd, H, "P/L ของ calendar spread ณ วันหมดอายุของขาใกล้ เป็นเส้นโค้งยอดที่สไตรก์ ไม่ใช่เส้นหักศอก เทียบกับเส้นหักศอกของ short call ขาใกล้")
    title(out, Wd, title_text, sub)
    x0, y0, w, h = 55, 48, 483, 180
    sx, sy = frame(out, x0, y0, w, h, [(70, "70"), (80, "80"), (90, "90"), (100, "100"), (110, "110"), (120, "120"), (130, "130")], [(-4, "−4"), (-2, "−2"), (0, "0"), (2, "+2"), (4, "+4")], xlab="ราคาหุ้น S ณ วันหมดอายุของขาใกล้", ylab="P/L (฿)")
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    for (xa, ya), (xb, yb) in zip(zip(S[:-1], pl[:-1]), zip(S[1:], pl[1:])):
        out.append(f'<polygon points="{sx(xa):.1f},{sy(0):.1f} {sx(xa):.1f},{sy(ya):.1f} {sx(xb):.1f},{sy(yb):.1f} {sx(xb):.1f},{sy(0):.1f}" fill="{GREEN if ya+yb>0 else RED}" opacity="0.10"/>')
    sc = -np.maximum(S - 100, 0) + c_near
    keep = sc >= -4.4  # ตัดส่วนที่ทะลุขอบล่างของกรอบ (ขาดทุนไม่จำกัดของ short call)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S[keep], sc[keep])], RED, 1.6, dash="5 3", shadow=False)
    xe = float(S[keep][-1]); out.append(f'<text x="{sx(xe)+4:.1f}" y="{y0+h-4:.1f}" {FONT} font-size="9" fill="{RED}">Short Call ขาใกล้: ลงต่อ −1 ต่อ 1 บาท ↘</text>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, pl)], BLUE, 2.75)
    i = int(np.argmax(pl))
    out.append(f'<circle cx="{sx(S[i]):.1f}" cy="{sy(pl[i]):.1f}" r="4.2" fill="#fff" stroke="{PURPLE}" stroke-width="2.2"/>')
    out.append(f'<text x="{sx(S[i])+8:.1f}" y="{sy(pl[i])-4:.1f}" {FONT} font-size="9.5" fill="{PURPLE}" font-weight="700">ยอดที่ S ≈ {S[i]:.0f}: +{pl[i]:.2f}</text>')
    out.append(f'<text x="{sx(S[i])+8:.1f}" y="{sy(pl[i])+8:.1f}" {FONT} font-size="9" fill="{PURPLE}">ขาไกลยังมี time value เต็ม ขาใกล้หมดค่า</text>')
    out.append(f'<text x="{x0+4}" y="{y0+14}" {FONT} font-size="9.5" fill="{INK2}">เบี้ยสุทธิที่จ่ายวันแรก = {c_far:.2f} − {c_near:.2f} = {debit:.2f} · ขาดทุนสูงสุดเมื่อราคาวิ่งไกลจาก K ทั้งสองทาง</text>')
    legend(out, [(BLUE, "Calendar: ขาย Call 1 เดือน + ซื้อ Call 3 เดือน (K = 100) ณ วันหมดอายุขาใกล้", "")], x0, H - 24)
    legend(out, [(RED, "Short Call ขาใกล้อย่างเดียว (เส้นหักศอก)", "5 3")], x0, H - 8)
    out.append("</svg>")
    NUMS["calendar"] = dict(debit=debit, c_near=c_near, c_far=c_far, peak=float(pl[i]), peak_at=float(S[i]))
    return "\n".join(out)


@fig("pm-part3.html", "p3-calendar")
def fig_p3_calendar():
    return _calendar_svg("Calendar Spread — payoff เป็นเส้นโค้ง ไม่ใช่เส้นหักศอก เพราะขาไกลยังมี time value",
                         "S₀ = K = 100 · σ = 20% · r = 5% · ขาใกล้ 1 เดือน ขาไกล 3 เดือน · ตีราคาด้วย Black-Scholes")

# ── Payoff Chart Study Guide — 16 ภาพ ใช้ตัวเลขจริงชุดเดียวกับเล่ม (K = 100 · เบี้ย 5 · สเปรด 90/110) ─────
SG = "payoff-chart-study-guide.html"
payoff(SG, "sg-anatomy", LC,
       "องค์ประกอบของกราฟ payoff — ตัวอย่าง Long Call K = 100 เบี้ย 5",
       "แกน X = ราคา S ณ วันหมดอายุ · แกน Y = กำไร/ขาดทุนสุทธิ · เส้นศูนย์แบ่งโซนกำไร (เขียว) / ขาดทุน (แดง) · BE คือจุดตัดศูนย์",
       slopes=False, xr=(70, 130),
       notes=[(118, 10, "โซนกำไร (เหนือเส้นศูนย์)", GREEN, "middle", 0), (90, -2.5, "โซนขาดทุน (ใต้เส้นศูนย์)", RED, "middle", 3),
              (100, -5, "จุดหักศอก = K", INK2, "middle", 26), (72, 0, "เส้นศูนย์ (Y = 0)", INK2, "start", -6)])
payoff(SG, "sg-long-call", LC, "2.1 Long Call — K = 100 · เบี้ย 5: แบนที่ −5 แล้วชัน +1 หลัง K · BE = 105",
       "กำไรไม่จำกัด · ขาดทุนสูงสุด = เบี้ย 5 · BE = K + P = 105", slopes=True)
payoff(SG, "sg-short-call", SC, "2.2 Short Call — K = 100 · รับเบี้ย 5: แบนที่ +5 แล้วชัน −1 หลัง K · BE = 105",
       "กำไรสูงสุด = เบี้ย 5 · ขาดทุนไม่จำกัด · BE = K + P = 105", slopes=True)
payoff(SG, "sg-long-put", LP, "2.3 Long Put — K = 100 · เบี้ย 5: ชัน −1 ก่อน K แล้วแบนที่ −5 · BE = 95",
       "กำไรสูงสุด = K − P = 95 (ที่ S = 0) · ขาดทุนสูงสุด = เบี้ย 5 · BE = K − P = 95", slopes=True)
payoff(SG, "sg-short-put", SP, "2.4 Short Put — K = 100 · รับเบี้ย 5: ชัน +1 ก่อน K แล้วแบนที่ +5 · BE = 95",
       "กำไรสูงสุด = เบี้ย 5 · ขาดทุนสูงสุด = K − P = 95 (ที่ S = 0) · BE = K − P = 95", slopes=True)
payoff(SG, "sg-bull-call-spread", [Leg("call", 90, 1, 8), Leg("call", 110, -1, 3)],
       "4.1 Bull Call Spread — Long Call 90 (เบี้ย 8) + Short Call 110 (รับ 3): บันไดขึ้น",
       "เบี้ยสุทธิ 8 − 3 = 5 · กำไรสูงสุด = (110 − 90) − 5 = +15 · ขาดทุนสูงสุด = −5 · BE = 90 + 5 = 95", slopes=True, xr=(75, 125), show_legs=False)
payoff(SG, "sg-bear-put-spread", [Leg("put", 110, 1, 8), Leg("put", 90, -1, 3)],
       "4.2 Bear Put Spread — Long Put 110 (เบี้ย 8) + Short Put 90 (รับ 3): บันไดลง",
       "เบี้ยสุทธิ 8 − 3 = 5 · กำไรสูงสุด = (110 − 90) − 5 = +15 · ขาดทุนสูงสุด = −5 · BE = 110 − 5 = 105", slopes=True, xr=(75, 125), show_legs=False)
payoff(SG, "sg-straddle", [Leg("call", 100, 1, 5), Leg("put", 100, 1, 5)],
       "4.3 Long Straddle — Call 100 + Put 100 เบี้ยรวม 10: รูปตัว V",
       "ขาดทุนสูงสุด −10 ที่ S = 100 พอดี · BE = 100 ± 10 → 90 และ 110 · กำไรไม่จำกัดขาขึ้น (ขาลงถึง +90 ที่ S = 0)", slopes=True, xr=(75, 125))
payoff(SG, "sg-strangle", [Leg("put", 90, 1, 2), Leg("call", 110, 1, 2)],
       "4.4 Long Strangle — Put 90 + Call 110 เบี้ยรวม 4: ตัว V กว้าง / ตัว U",
       "ถูกกว่า straddle แต่ต้องวิ่งไกลกว่า · ขาดทุนสูงสุด −4 ระหว่าง 90–110 · BE = 90 − 4 = 86 และ 110 + 4 = 114", slopes=True, xr=(75, 125))
payoff(SG, "sg-iron-condor", [Leg("put", 90, 1, 1), Leg("put", 95, -1, 2), Leg("call", 105, -1, 2), Leg("call", 110, 1, 1)],
       "4.5 Iron Condor 90/95/105/110 — ที่ราบสูง: รับเบี้ยสุทธิ 2",
       "LP 90 (1) + SP 95 (2) + SC 105 (2) + LC 110 (1) · กำไรสูงสุด +2 · ขาดทุนสูงสุด −(5 − 2) = −3 · BE 93 / 107",
       show_legs=False, slopes=True, xr=(80, 120))
payoff(SG, "sg-butterfly", BF,
       "4.6 Long Call Butterfly 90/100/110 — เต็นท์: ยอด +7 ที่ K₂ = 100",
       "+1 Call 90 (12) −2 Call 100 (6) +1 Call 110 (3) · เบี้ยสุทธิ 12 − 12 + 3 = 3 · ยอด = 10 − 3 = +7 · ขาดทุนสูงสุด −3 · BE 93 / 107",
       show_legs=False, slopes=True, xr=(80, 120))
payoff(SG, "sg-ratio-1x2", [Leg("call", 100, 1, 0), Leg("call", 110, -2, 0)],
       "6.1 Ratio Call Spread 1×2 — Long 1 Call 100 + Short 2 Call 110: เต็นท์ข้างเดียว",
       "payoff ก่อนหักเบี้ย · slope 0 → +1 → −1 · ยอด +10 ที่ 110 · ตัดศูนย์ที่ 120 แล้วลงไม่จำกัด (ขา short 1 ตัวไม่มีอะไรคุ้ม)",
       with_premium=False, slopes=False, xr=(85, 135),
       notes=[(92, 0, "แบน (slope 0)", INK2, "middle", -8), (103, 3, "slope +1", INK2, "end", 14), (121, -1, "slope −1", INK2, "middle", 16)])
payoff(SG, "sg-back-ratio-1x2", [Leg("call", 100, -1, 0), Leg("call", 110, 2, 0)],
       "6.2 Back Ratio Call Spread 1×2 — Short 1 Call 100 + Long 2 Call 110: กลับด้าน",
       "payoff ก่อนหักเบี้ย · slope 0 → −1 → +1 · dead zone ต่ำสุด −10 ที่ 110 · ตัดศูนย์ที่ 120 แล้วขึ้นไม่จำกัด",
       with_premium=False, slopes=False, xr=(85, 135),
       notes=[(92, 0, "แบน (slope 0)", INK2, "middle", -8), (103, -3, "slope −1", INK2, "end", 14), (124, 4, "slope +1", INK2, "start", -6),
              (110, -10, "dead zone", RED, "middle", 28)], be_below=True)
payoff_grid_reg(SG, "sg-collar-buildup",
                [([Leg("stock", 100, 1, 0)], "Long Stock @100 — ชัน +1 ตลอด", {}),
                 ([Leg("stock", 100, 1, 0), Leg("put", 90, 1, 3)], "+ Put 90 (เบี้ย 3) = Protective Put · พื้น −13", {}),
                 ([Leg("stock", 100, 1, 0), Leg("call", 110, -1, 3)], "+ Short Call 110 (รับ 3) = Covered Call · เพดาน +13", {}),
                 ([Leg("stock", 100, 1, 0), Leg("put", 90, 1, 3), Leg("call", 110, -1, 3)], "Collar 90/110 — พื้น −10 · เพดาน +10 · เบี้ยสุทธิ 0", {})],
                "Hedging ด้วย Options — จากหุ้นเปล่า สู่ Protective Put, Covered Call และ Collar",
                "หุ้นซื้อที่ 100 · Put 90 เบี้ย 3 · Call 110 รับ 3 · Collar นี้เป็น zero-cost: เบี้ยรับ 3 จ่าย 3", xr=(70, 130), H=420)


def _time_value_svg():
    """5.1 ราคา call ก่อนหมดอายุ (Black-Scholes) เทียบเส้นหักศอก ณ วันหมดอายุ — K = 100 · σ = 20% · r = 5%"""
    S = np.linspace(70, 130, 121)
    curves = [(90 / 365, "T = 90 วัน", PURPLE), (30 / 365, "T = 30 วัน", BLUE)]
    Wd, H = 560, 314
    out = svg_open(Wd, H, "ราคา call K = 100 ตามราคาหุ้น S: เส้นโค้งที่เหลือ 90 วัน อยู่สูงกว่าเส้นที่เหลือ 30 วัน และทั้งคู่อยู่เหนือเส้นหักศอก ณ วันหมดอายุ")
    title(out, Wd, "5.1 ก่อนหมดอายุ ราคา option เป็นเส้นโค้ง อยู่เหนือเส้นหักศอกเสมอ — ยิ่งเหลือเวลามาก ยิ่งสูง",
          "Call K = 100 · σ = 20% · r = 5% · ราคาจาก Black-Scholes · ส่วนต่างแนวดิ่งระหว่างเส้นโค้งกับเส้นหักศอก = time value")
    x0, y0, w, h = 55, 48, 483, 180
    sx, sy = frame(out, x0, y0, w, h, [(70, "70"), (80, "80"), (90, "90"), (100, "100"), (110, "110"), (120, "120"), (130, "130")],
                   [(0, "0"), (10, "10"), (20, "20"), (30, "30")], xlab="ราคาหุ้น S", ylab="ราคา call (฿)")
    intr = np.maximum(S - 100, 0)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, intr)], INK2, 2.2, dash="", shadow=False)
    vals = {}
    for T, lab, col in curves:
        C = bs_greeks(S, K=100, r=0.05, sg=0.20, T=T)["C"]; vals[lab] = C
        polyline(out, [(sx(a), sy(b)) for a, b in zip(S, C)], col, 2.4)
    i = 60  # S = 100
    c90, c30 = float(vals["T = 90 วัน"][i]), float(vals["T = 30 วัน"][i])
    out.append(f'<line x1="{sx(100):.1f}" y1="{sy(0):.1f}" x2="{sx(100):.1f}" y2="{sy(c90):.1f}" stroke="{AMBER}" stroke-width="1.4" stroke-dasharray="3 3"/>')
    out.append(f'<text x="{sx(100)-6:.1f}" y="{sy(9.5):.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{AMBER}" font-weight="700">ที่ S = 100 (ATM): intrinsic = 0 ทั้งเส้นโค้งจึงเป็น time value</text>')
    out.append(f'<text x="{sx(100)-6:.1f}" y="{sy(9.5)+12:.1f}" text-anchor="end" {FONT} font-size="9.5" fill="{AMBER}">= {c90:.2f} (90 วัน) · {c30:.2f} (30 วัน) · 0 (หมดอายุ)</text>')
    out.append(f'<text x="{sx(71):.1f}" y="{sy(27):.1f}" {FONT} font-size="9.5" fill="{INK2}">ลึกใน ITM (ขวา) เส้นโค้งเข้าใกล้เส้นหักศอก: time value เล็กลง</text>')
    legend(out, [(PURPLE, "T = 90 วัน (Black-Scholes)", ""), (BLUE, "T = 30 วัน", ""), (INK2, "T = 0 วันหมดอายุ: max(S − 100, 0)", "")], x0, H - 10)
    out.append("</svg>")
    NUMS["sg-time-value"] = dict(c90=c90, c30=c30)
    return "\n".join(out)


@fig(SG, "sg-time-value")
def fig_sg_time_value():
    return _time_value_svg()


@fig(SG, "sg-calendar")
def fig_sg_calendar():
    return _calendar_svg("6.3 Calendar Spread — ณ วันหมดอายุขาใกล้ P/L เป็นเส้นโค้ง ไม่ใช่เส้นตรงหักศอก",
                         "ขาย Call 1 เดือน + ซื้อ Call 3 เดือน K = 100 · S₀ = 100 · σ = 20% · r = 5% · ขาไกลตีราคาด้วย Black-Scholes")


# ── Arbitrage · ตาของ Arbitrageur · คณิตศาสตร์เล่ม 1 — กราฟ payoff ที่เคยวาดมือ ─────────────────
USD_K = dict(ylab="payoff ($)", ytick_fmt=lambda v: f"${v:,.0f}".replace("$-", "−$"), strike_fmt=lambda k: f"{k:,.0f}")
CS2000 = [Leg("call", 2000, 1, 0), Leg("call", 2500, -1, 0)]
payoff_grid_reg("arb-part1.html", "a1-payoff-shapes",
                [([Leg("stock", 100, 1, 0)], "Linear (Spot) · slope +1", {}),
                 ([Leg("call", 100, 1, 0)], "Convex (Call) · หักศอกที่ K", {}),
                 ([Leg("dcall", 100, 1, 0)], "Binary (PM Yes) · 0 หรือ 1", {})],
                "รูปร่าง payoff 3 ตระกูล — เชิงเส้น · หักศอก · ดิจิทัล (K = 100 · ยังไม่หักเบี้ย)",
                "Spot ได้เสียเท่าราคาที่เคลื่อน · Call ไม่เสียซ้าย ได้ +1 ขวา · PM จ่าย 1 หรือ 0 ไม่สนว่าเกินเท่าไร",
                with_premium=False, callouts=False, slopes=False, cols=3, W=620, H=260, xr=(70, 130), ylab="payoff")
payoff("arb-part1.html", "a1-synthetic-stock", [Leg("stock", 100, 1, 0)],
       "Replication — หุ้นจริง กับหุ้นสังเคราะห์ Call − Put + Bond: payoff ซ้อนกันพอดี",
       "S = C − P + PV(K) · K = 100 · ทั้งสองเส้นให้ S ทุกราคา → ราคาวันนี้ต้องเท่ากัน มิฉะนั้นซื้อถูก ขายแพง = arb",
       with_premium=False, show_legs=False, callouts=False, xr=(60, 140), total_label="หุ้นจริง (S − 100)",
       overlays=[dict(legs=[Leg("call", 100, 1, 0), Leg("put", 100, -1, 0), Leg("bond", 100, 1, 0), Leg("bond", 100, -1, 0)],
                      label="สังเคราะห์: Long Call(100) + Short Put(100) (+ Bond หักต้นทุน 100)", color=RED, dash="7 4", width=2.2)],
       notes=[(138, -10, "ซ้อนทับกันพอดี → ราคาวันนี้ต้องเท่ากัน", PURPLE, "end", 0)])
payoff("arb-part2a.html", "a2a-call-spread-2000-2500", CS2000,
       "Step 3: Solve — payoff ที่ต้องการ 0 → S − 2000 → ตันที่ +500 คือ Call Spread(2000, 2500)",
       "Long Call 2000 + Short Call 2500 · ยังไม่หักเบี้ย · ต่ำกว่า 2000 ไม่เสีย · ระหว่างชัน +1 · เหนือ 2500 ได้ 500 คงที่",
       with_premium=False, show_legs=True, slopes=True, xr=(1500, 3000), total_label="Call Spread(2000, 2500)", **USD_K)
payoff("eye-part2.html", "e2-call-spread-2000-2500", CS2000,
       "Payoff Construction — \"ขึ้นไม่เกิน $2,500 ไม่อยากเสียถ้าลง\" = Call Spread(2000, 2500)",
       "0 ถ้า S < 2000 · S − 2000 ระหว่าง 2000–2500 (slope +1) · +500 cap เหนือ 2500 · ซื้อ 1 ชุดจบ (ยังไม่หักเบี้ย)",
       with_premium=False, show_legs=True, slopes=True, xr=(1500, 3000), total_label="Call Spread(2000, 2500)", **USD_K)
payoff("arb-part2b.html", "a2b-belief-cap", CS2000 + [Leg("dput", 2500, 100, 0)],
       "Belief \"ขึ้นแต่ไม่เกิน 2500\" → Call Spread(2000, 2500) + PM No(2500) ×100 สัญญา",
       "Call spread ให้ขาขึ้นถึง 2500 · PM No จ่าย $100 เพิ่มถ้าไม่ทะลุ 2500 (income) · ทะลุแล้ว PM หมดค่า เหลือ cap 500",
       with_premium=False, show_legs=True, slopes=False, xr=(1500, 3000), total_label="รวม: Call Spread + PM No ×100", legend_rows=2, callouts=False,
       notes=[(2480, 600, "ก่อนถึง 2500 ได้เกือบ 600 (500 + 100)", PURPLE, "end", -8), (2950, 500, "ทะลุ 2500: PM หมดค่า เหลือ cap 500", INK2, "end", 16)], **USD_K)
payoff("arb-part3.html", "a3-conversion", [Leg("stock", 100, 1, 0), Leg("put", 100, 1, 0), Leg("call", 100, -1, 0)],
       "Conversion — หุ้น @100 + Long Put(100) + Short Call(100): payoff แบน = ได้คืน 100 แน่",
       "ตัวอย่าง §11.4: จ่ายวันนี้ S + P − C = 100 + 5.80 − 8.50 = 97.30 · ได้ 100 แน่ที่หมดอายุ · เทียบ PV(K) = 97.53 → ล็อกกำไร 0.23",
       with_premium=False, show_legs=True, callouts=False, xr=(60, 140), total_label="รวม 3 ขา (เทียบต้นทุนหุ้น 100) = 0 คงที่", legend_rows=2,
       notes=[(62, 0, "สามขาหักล้างกันหมด → สิ้นงวดถือเงิน 100 พอดี = พันธบัตร", PURPLE, "start", -8)])
payoff("arb-part3.html", "a3-box", [Leg("call", 90, 1, 0), Leg("call", 110, -1, 0), Leg("put", 110, 1, 0), Leg("put", 90, -1, 0)],
       "Box Spread 90/110 — Bull Call Spread + Bear Put Spread = แบนที่ 20 ทุกราคา = พันธบัตร",
       "ซ้ายของ 90 ได้ 0 + 20 · ขวาของ 110 ได้ 20 + 0 · ตรงกลาง (S − 90) + (110 − S) = 20 · ค่ายุติธรรม = PV(20)",
       with_premium=False, show_legs=False, callouts=False, xr=(70, 130), total_label="Box = รวมสองสเปรด = 20",
       overlays=[dict(legs=[Leg("call", 90, 1, 0), Leg("call", 110, -1, 0)], label="Bull Call Spread 90/110", color=GREEN, dash="6 3", width=2),
                 dict(legs=[Leg("put", 110, 1, 0), Leg("put", 90, -1, 0)], label="Bear Put Spread 90/110", color=RED, dash="6 3", width=2)],
       notes=[(128, 20, "= 20 เสมอ → ราคาวันนี้ต้อง = 20·e⁻ʳᵀ", PURPLE, "end", -8)])
payoff("math-part1.html", "m1-long-call", LC,
       "Long Call: payoff = max(0, S − 100) − 5 — จุดหักศอกที่ K = 100 · จุดคุ้มทุน 105",
       "ซ้ายของ K แบนที่ −5 (ปุ่ม \"ห้ามติดลบ\" ตัดเป็น 0 แล้วหักเบี้ย) · ขวาของ K ชัน +1 กำไรวิ่งขึ้นเรื่อย ๆ", slopes=True, xr=(70, 130))
payoff("math-part1.html", "m1-mirror", LC,
       "Short คือ Long พลิกหัว — Short Call = −f(S): กระจกสะท้อนผ่านเส้นศูนย์",
       "K = 100 · เบี้ย 5 · ที่ไหน Long กำไร Short ขาดทุนเท่ากันเป๊ะ · จุดคุ้มทุน 105 เดียวกัน",
       show_legs=False, callouts=False, xr=(70, 130), total_label="Long Call = f(S)",
       overlays=[dict(legs=SC, label="Short Call = −f(S)", color=RED, dash="7 4", width=2.2)],
       notes=[(120, -15, "พลิกหัว!", RED, "middle", 0), (104, 0, "คุ้มทุน 105 ทั้งคู่", PURPLE, "end", -20),
              (72, -5, "Long ขาดทุนสูงสุด −5 ↔ Short กำไรสูงสุด +5", INK2, "start", 14)])
payoff("math-part1.html", "m1-bull-call-spread", [Leg("call", 90, 1, 5), Leg("call", 110, -1, 0)],
       "Bull Call Spread 90/110 จ่ายสุทธิ 5 — ฟังก์ชันแบ่งช่วง 3 ช่วง: −5 → S − 95 → +15",
       "ช่วง 1 (S < 90) ขาดทุนคงที่ −5 · ช่วง 2 (90–110) ชัน +1 · ช่วง 3 (S > 110) กำไรคงที่ 110 − 90 − 5 = +15 · คุ้มทุน 95",
       show_legs=False, slopes=True, xr=(70, 130))
payoff("math-part1.html", "m1-straddle", [Leg("call", 100, 1, 4), Leg("put", 100, 1, 3)],
       "Long Straddle — Call(100) จ่าย 4 + Put(100) จ่าย 3: รูปตัว V คุ้มทุน 93 และ 107",
       "1 strike → 2 ช่วง · ซ้ายชัน −1 ขวาชัน +1 · ขาดทุนสูงสุด −7 (เบี้ยรวม) เมื่อหุ้นนิ่งที่ 100 · คุ้มทุน = 100 ∓ 7",
       show_legs=True, slopes=True, xr=(80, 120), unbounded_dy=-22)


# ── คณิตศาสตร์เล่ม 1 Part I (math-part1) — กราฟตัวเลขที่เคยวาดมือ ──────────────────────────
def _std_frame(out, Wd, H, xt, yt, xlab, ylab, x0=55, y0=48, w=483, h=180):
    return frame(out, x0, y0, w, h, xt, yt, xlab=xlab, ylab=ylab), (x0, y0, w, h)


def _zero_line(out, sx, sy, lo, hi):
    out.append(f'<line x1="{sx(lo):.1f}" y1="{sy(0):.1f}" x2="{sx(hi):.1f}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')


def _dot(out, x, y, col=PURPLE, r=4.2):
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" stroke="{col}" stroke-width="2.2"/>')


ARROW_DEF = '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#dc2626"/></marker></defs>'


def _txt(out, x, y, text, col=INK2, anc="start", size=9.5, bold=False, italic=False):
    fw = ' font-weight="700"' if bold else ""; fi = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anc}" {FONT} font-size="{size}" fill="{col}"{fw}{fi}>{text}</text>')


@fig("math-part1.html", "m1-drawdown-bars")
def fig_m1_drawdown_bars():
    drops = [0.10, 0.25, 0.50, 0.75, 0.90]
    reb = [d / (1 - d) for d in drops]
    Wd, H = 560, 300
    out = svg_open(Wd, H, "แท่งเทียบ: ร่วง 10/25/50/75/90% ต้องเด้งกลับ 11/33/100/300/900% — ยิ่งร่วงลึก ช่องว่างยิ่งถ่างออก")
    title(out, Wd, "ร่วงแล้วต้องเด้งกลับเท่าไรถึงเท่าทุน — ขาลงกับขาขึ้นไม่ใช่กระจกสะท้อนกัน",
          "เริ่ม ฿100 · เด้งกลับที่ต้องการ = ร่วง ÷ (1 − ร่วง) · ร่วง 50% ต้อง +100% · ร่วง 90% ต้อง +900%")
    x0, y0, w, h = 70, 50, 470, 190
    rows = len(drops); rh = h / rows; mid = x0 + 150  # แกนกลาง: ซ้ายแท่งร่วง (สเกล 100%) ขวาแท่งเด้ง (สเกล 900%)
    lw, rw = 130, w - 150 - 10
    _txt(out, mid - 4, y0 - 6, "ขนาดที่ร่วง", RED, "end", bold=True); _txt(out, mid + 4, y0 - 6, "ต้องเด้งกลับ", GREEN, "start", bold=True)
    out.append(f'<line x1="{mid}" y1="{y0}" x2="{mid}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.2"/>')
    for i, (d, r) in enumerate(zip(drops, reb)):
        yc = y0 + i * rh + rh / 2; bh = rh * 0.52
        out.append(f'<rect x="{mid - lw*d:.1f}" y="{yc-bh/2:.1f}" width="{lw*d:.1f}" height="{bh:.1f}" fill="{RED}" opacity="0.75" rx="2"/>')
        out.append(f'<rect x="{mid:.1f}" y="{yc-bh/2:.1f}" width="{rw*r/9:.1f}" height="{bh:.1f}" fill="{GREEN}" opacity="0.75" rx="2"/>')
        _txt(out, mid - lw * d - 5, yc + 3.5, f"−{d*100:.0f}%", RED, "end", bold=True)
        _txt(out, mid + rw * r / 9 + 5, yc + 3.5, f"+{r*100:.0f}%" if r >= 1 else f"+{r*100:.1f}%", GREEN, "start", bold=True)
        _txt(out, x0 - 4, yc + 3.5, f"฿100 → ฿{100*(1-d):.0f}", INK2, "end", size=9)
    _txt(out, x0, H - 24, "ยิ่งร่วงลึก ช่องว่างยิ่งถ่างออก — นี่คือเหตุผลที่ Options วัดผลด้วย log return", INK2, "start", size=9)
    _txt(out, x0, H - 11, "ln(50/100) = −0.69 และ ln(100/50) = +0.69 สมมาตรกัน ส่วน −50% กับ +100% ไม่สมมาตร", INK2, "start", size=9)
    out.append("</svg>")
    NUMS["m1-drawdown-bars"] = {f"reb{int(d*100)}": r * 100 for d, r in zip(drops, reb)}
    return "\n".join(out)


@fig("math-part1.html", "m1-linear-fn")
def fig_m1_linear_fn():
    Wd, H = 560, 300
    out = svg_open(Wd, H, "กราฟเส้นตรง f(x) = 2x − 100 ผ่าน (0, −100) ตัดแกน x ที่จุดคุ้มทุน (50, 0) และผ่าน (100, 100)")
    title(out, Wd, "ฟังก์ชัน f(x) = 2x − 100 — ป้อน x ได้ f(x): เส้นตรงตัดแกน x ที่ (50, 0)",
          "ใต้เส้นศูนย์ = โซนขาดทุน · เหนือเส้นศูนย์ = โซนกำไร · ทุก payoff chart ก็คือกราฟของฟังก์ชันแบบนี้")
    (sx, sy), _ = _std_frame(out, Wd, H, [(0, "0"), (25, "25"), (50, "50"), (75, "75"), (100, "100")], [(-100, "−100"), (-50, "−50"), (0, "0"), (50, "50"), (100, "100")], "x", "f(x)")
    out.append(f'<polygon points="{sx(0):.1f},{sy(0):.1f} {sx(50):.1f},{sy(0):.1f} {sx(0):.1f},{sy(-100):.1f}" fill="{RED}" opacity="0.10"/>')
    out.append(f'<polygon points="{sx(50):.1f},{sy(0):.1f} {sx(100):.1f},{sy(0):.1f} {sx(100):.1f},{sy(100):.1f}" fill="{GREEN}" opacity="0.10"/>')
    _zero_line(out, sx, sy, 0, 100)
    polyline(out, [(sx(0), sy(-100)), (sx(100), sy(100))], BLUE, 2.75)
    for x, lab, anc, dx, dy in [(0, "(0, −100)", "start", 8, -8), (50, "จุดคุ้มทุน (50, 0)", "start", 8, -8), (100, "(100, 100)", "end", -8, -8)]:
        _dot(out, sx(x), sy(2 * x - 100)); _txt(out, sx(x) + dx, sy(2 * x - 100) + dy, lab, PURPLE, anc, bold=True)
    _txt(out, sx(75), sy(20), "f(x) = 2x − 100", BLUE, "start", bold=True)
    _txt(out, sx(30), sy(-80), "โซนขาดทุน", RED, "start", bold=True); _txt(out, sx(75), sy(80), "โซนกำไร", GREEN, "start", bold=True)
    out.append("</svg>")
    return "\n".join(out)


@fig("math-part1.html", "m1-slopes")
def fig_m1_slopes():
    Wd, H = 560, 300
    out = svg_open(Wd, H, "เส้นตรงสี่เส้นจากจุดเดียวกัน ความชัน +1, +0.5, 0 และ −1 พร้อมสามเหลี่ยม Δx = 1 Δy = 1")
    title(out, Wd, "ความชัน m = Δy/Δx — ขึ้น 1 ต่อ 1 (+1) · ขึ้นครึ่ง (+0.5 = Delta ATM) · แบน (0) · ลง 1 ต่อ 1 (−1)",
          "Long Call หลัง strike ชัน +1 · Short Call ชัน −1 · payoff ก่อนถึง strike ชัน 0 · Delta คือความชันของราคา option")
    (sx, sy), _ = _std_frame(out, Wd, H, [(-3, "−3"), (-2, "−2"), (-1, "−1"), (0, "0"), (1, "1"), (2, "2"), (3, "3")], [(-3, "−3"), (-2, "−2"), (-1, "−1"), (0, "0"), (1, "1"), (2, "2"), (3, "3")], "x", "y")
    _zero_line(out, sx, sy, -3, 3)
    for m, col, lab, dash in [(1, GREEN, "m = +1", ""), (0.5, PURPLE, "m = +0.5", "5 3"), (0, INK2, "m = 0", ""), (-1, RED, "m = −1", "")]:
        polyline(out, [(sx(-3), sy(-3 * m)), (sx(3), sy(3 * m))], col, 2.4, dash=dash, shadow=not dash)
        if m < 0: _txt(out, sx(1.5), sy(-2.4), lab, col, "start", bold=True)
        else: _txt(out, sx(3) - 4, sy(3 * m) - 6, lab, col, "end", bold=True)
    # สามเหลี่ยม Δx = 1, Δy = 1 บนเส้น m = +1
    out.append(f'<polyline points="{sx(1):.1f},{sy(1):.1f} {sx(2):.1f},{sy(1):.1f} {sx(2):.1f},{sy(2):.1f}" fill="none" stroke="{GREEN}" stroke-width="1.4" stroke-dasharray="3 3"/>')
    _txt(out, sx(1.5), sy(1) + 12, "Δx = 1", GREEN, "middle", size=9); _txt(out, sx(2) + 4, sy(1.5) + 3, "Δy = 1", GREEN, "start", size=9)
    out.append("</svg>")
    return "\n".join(out)


@fig("math-part1.html", "m1-two-lines")
def fig_m1_two_lines():
    Wd, H = 560, 300
    out = svg_open(Wd, H, "เส้น x + y = 10 กับ 2x − y = 5 ตัดกันที่จุดคำตอบ (5, 5)")
    title(out, Wd, "ระบบสมการสองตัวแปร — คำตอบคือจุดที่เส้นสองเส้นตัดกัน: (5, 5)",
          "x + y = 10 และ 2x − y = 5 · แทน y = 10 − x → 3x = 15 → x = 5, y = 5 · เหมือนหา strike ที่เบี้ย Call = เบี้ย Put ใน zero-cost collar")
    (sx, sy), _ = _std_frame(out, Wd, H, [(0, "0"), (2, "2"), (4, "4"), (6, "6"), (8, "8"), (10, "10")], [(0, "0"), (2, "2"), (4, "4"), (6, "6"), (8, "8"), (10, "10")], "x", "y")
    polyline(out, [(sx(0), sy(10)), (sx(10), sy(0))], BLUE, 2.4); _txt(out, sx(1.2), sy(9.2), "x + y = 10", BLUE, "start", bold=True)
    polyline(out, [(sx(2.5), sy(0)), (sx(7.5), sy(10))], AMBER, 2.4); _txt(out, sx(7.6), sy(9.4), "2x − y = 5", AMBER, "start", bold=True)
    _dot(out, sx(5), sy(5)); _txt(out, sx(6.5), sy(2.6), "(5, 5) ← คำตอบ", PURPLE, "start", bold=True)
    out.append(f'<line x1="{sx(5):.1f}" y1="{sy(5):.1f}" x2="{sx(5):.1f}" y2="{sy(0):.1f}" stroke="{PURPLE}" stroke-width="1" stroke-dasharray="3 3"/>')
    out.append(f'<line x1="{sx(5):.1f}" y1="{sy(5):.1f}" x2="{sx(0):.1f}" y2="{sy(5):.1f}" stroke="{PURPLE}" stroke-width="1" stroke-dasharray="3 3"/>')
    out.append("</svg>")
    return "\n".join(out)


def growth_data(P=10000.0, r=0.10, T=10):
    t = np.linspace(0, T, 101)
    return t, P * (1 + r * t), P * (1 + r) ** t, P * np.exp(r * t)


@fig("math-part1.html", "m1-growth")
def fig_m1_growth():
    t, simple, comp, cont = growth_data()
    Wd, H = 560, 328
    out = svg_open(Wd, H, "เงิน 10,000 ที่ 10% ต่อปี 10 ปี: เชิงเดี่ยวเป็นเส้นตรงจบ 20,000 ทบต้นรายปีโค้งขึ้นจบ 25,937 ทบต้นต่อเนื่องจบ 27,183")
    title(out, Wd, "เงินโตอย่างไร — เชิงเดี่ยวเป็นเส้นตรง · ทบต้นโค้งขึ้น · ทบต้นต่อเนื่อง (e) โค้งสุด",
          "เริ่ม ฿10,000 · 10% ต่อปี · 10 ปี · ช่องว่างระหว่างเส้นถ่างออกตามเวลา = ดอกเบี้ยของดอกเบี้ย")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (2, "2"), (4, "4"), (6, "6"), (8, "8"), (10, "10")], [(10000, "10k"), (15000, "15k"), (20000, "20k"), (25000, "25k"), (30000, "30k")], "ปี", "฿")
    for y, col, lab, dash in [(simple, INK2, "เชิงเดี่ยว → เส้นตรง", ""), (comp, BLUE, "ทบต้นรายปี → โค้งขึ้น", ""), (cont, PURPLE, "ทบต้นต่อเนื่อง (e)", "6 3")]:
        polyline(out, [(sx(a), sy(b)) for a, b in zip(t, y)], col, 2.4, dash=dash, shadow=not dash)
    _txt(out, x0 + 8, y0 + 14, "จบปีที่ 10:", INK, "start", bold=True)
    _txt(out, x0 + 8, y0 + 28, f"เชิงเดี่ยว {simple[-1]:,.0f}", INK2, "start", bold=True)
    _txt(out, x0 + 8, y0 + 42, f"ทบต้นรายปี {comp[-1]:,.0f}", BLUE, "start", bold=True)
    _txt(out, x0 + 8, y0 + 56, f"ต่อเนื่อง (e) {cont[-1]:,.0f}", PURPLE, "start", bold=True)
    legend(out, [(INK2, "เชิงเดี่ยว 10,000(1 + 0.1t)", ""), (BLUE, "ทบต้นรายปี 10,000(1.1)ᵗ", "")], x0, H - 24)
    legend(out, [(PURPLE, "ทบต้นต่อเนื่อง 10,000·e^(0.1t)", "6 3")], x0, H - 8)
    out.append("</svg>")
    NUMS["m1-growth"] = dict(simple=float(simple[-1]), comp=float(comp[-1]), cont=float(cont[-1]))
    return "\n".join(out)


@fig("math-part1.html", "m1-log")
def fig_m1_log():
    Wd, H = 560, 300
    out = svg_open(Wd, H, "กราฟ y = log₁₀(x) ผ่าน (1, 0) (10, 1) (100, 2): โตเร็วช่วงแรกแล้วค่อย ๆ แบนราบ")
    title(out, Wd, "y = log₁₀(x) — ผ่าน (1, 0) · x เพิ่ม 10 เท่า log เพิ่มทีละ 1 · โตช้าลงเรื่อย ๆ",
          "log บีบช่วงกว้างให้อ่านไหว: 1 → 10 → 100 กลายเป็น 0 → 1 → 2 · คูณ → บวก")
    (sx, sy), _ = _std_frame(out, Wd, H, [(0, "0"), (20, "20"), (40, "40"), (60, "60"), (80, "80"), (100, "100")], [(-1, "−1"), (0, "0"), (1, "1"), (2, "2")], "x", "log₁₀(x)")
    _zero_line(out, sx, sy, 0, 100)
    x = np.linspace(0.12, 100, 400)
    polyline(out, [(sx(a), sy(np.log10(a))) for a in x], BLUE, 2.6)
    for xv, lab, dy in [(1, "log(1) = 0", 16), (10, "log(10) = 1", -8), (100, "log(100) = 2", -8)]:
        _dot(out, sx(xv), sy(np.log10(xv))); _txt(out, sx(xv) + (8 if xv < 100 else -8), sy(np.log10(xv)) + dy, lab, PURPLE, "start" if xv < 100 else "end", bold=True)
    _txt(out, sx(55), sy(1.45), "โตช้าลงเรื่อย ๆ (x เพิ่ม 10 เท่า → log เพิ่มแค่ 1)", INK2, "middle", italic=True)
    out.append("</svg>")
    return "\n".join(out)


@fig("math-part1.html", "m1-exp-ln")
def fig_m1_exp_ln():
    Wd, H = 560, 320
    out = svg_open(Wd, H, "เส้น y = eˣ ผ่าน (0, 1) กับ y = ln(x) ผ่าน (1, 0) เป็นภาพสะท้อนกันผ่านเส้น y = x")
    title(out, Wd, "eˣ กับ ln(x) เป็นปุ่ม undo ของกัน — กราฟสะท้อนกันผ่านกระจก y = x",
          "eˣ ผ่าน (0, 1) และเป็นบวกเสมอ · ln(x) ผ่าน (1, 0) และรับเฉพาะ x > 0 · ln(eˣ) = x")
    x0, y0, w, h = 175, 48, 240, 240  # จัตุรัสเพื่อให้กระจก 45° ดูเป็น 45° จริง
    sx, sy = frame(out, x0, y0, w, h, [(-3, "−3"), (-2, "−2"), (-1, "−1"), (0, "0"), (1, "1"), (2, "2"), (3, "3")], [(-3, "−3"), (-2, "−2"), (-1, "−1"), (0, "0"), (1, "1"), (2, "2"), (3, "3")], xlab="x", ylab="y")
    _zero_line(out, sx, sy, -3, 3); out.append(f'<line x1="{sx(0):.1f}" y1="{y0}" x2="{sx(0):.1f}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.2"/>')
    polyline(out, [(sx(-3), sy(-3)), (sx(3), sy(3))], INK2, 1.4, dash="4 3", shadow=False); _txt(out, sx(2.55), sy(2.85), "y = x (กระจก)", INK2, "end", size=9)
    xe = np.linspace(-3, np.log(3), 200); polyline(out, [(sx(a), sy(np.exp(a))) for a in xe], BLUE, 2.5)
    xl = np.linspace(np.exp(-3), 3, 300); polyline(out, [(sx(a), sy(np.log(a))) for a in xl], GREEN, 2.5)
    _dot(out, sx(0), sy(1)); _txt(out, sx(0) - 8, sy(1) - 6, "(0, 1)", BLUE, "end", bold=True)
    _dot(out, sx(1), sy(0)); _txt(out, sx(1) + 8, sy(0) + 14, "(1, 0)", GREEN, "start", bold=True)
    _txt(out, sx(0.4), sy(2.6), "y = eˣ", BLUE, "end", bold=True); _txt(out, sx(2.2), sy(0.55), "y = ln(x)", GREEN, "start", bold=True)
    out.append("</svg>")
    return "\n".join(out)


# ── คณิตศาสตร์เล่ม 1 Part II (math-part2) — ระฆังและการแจกแจง ────────────────────────────────
def _bell_frame(out, Wd, H, xt, xlab, ylab="ความหนาแน่น", ymax=1.0, x0=55, y0=48, w=483, h=180):
    yt = [(0, "0"), (ymax, "")]
    sx, sy = frame(out, x0, y0, w, h, xt, yt, xlab=xlab, ylab=ylab, grid_y=False)
    return sx, sy, (x0, y0, w, h)


def _fill_between(out, sx, sy, xs, ys, col, op=0.18):
    pts = " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(xs, ys))
    out.append(f'<polygon points="{sx(xs[0]):.1f},{sy(0):.1f} {pts} {sx(xs[-1]):.1f},{sy(0):.1f}" fill="{col}" opacity="{op}"/>')


def two_bells_strike_data(S0=100.0, sgA=5.0, sgB=20.0, K=120.0):
    S = np.linspace(40, 160, 481)
    fA = _npdf((S - S0) / sgA) / sgA; fB = _npdf((S - S0) / sgB) / sgB
    pA = 1 - _N((K - S0) / sgA); pB = 1 - _N((K - S0) / sgB)
    return S, fA, fB, pA, pB


@fig("math-part2.html", "m2-two-bells-strike")
def fig_m2_two_bells_strike():
    S, fA, fB, pA, pB = two_bells_strike_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, "ระฆังสองใบศูนย์กลาง 100 เดียวกัน หุ้น A แคบสูง (σ 5) หุ้น B กว้างเตี้ย (σ 20) พื้นที่เลย strike 120 ของ B มากกว่ามาก")
    title(out, Wd, "หุ้น A กับ B ราคาเท่ากัน ค่าเฉลี่ยเท่ากัน — แต่โอกาส \"พุ่งเลย strike\" ต่างกันมหาศาล",
          f"ศูนย์กลาง 100 ทั้งคู่ · A เหวี่ยง ±5 · B เหวี่ยง ±20 · พื้นที่เกิน strike 120: A ≈ {pA*100:.3f}% · B ≈ {pB*100:.1f}% → Option ของ B แพงกว่ามาก")
    sx, sy, (x0, y0, w, h) = _bell_frame(out, Wd, H, [(40, "40"), (60, "60"), (80, "80"), (100, "100"), (120, "120"), (140, "140"), (160, "160")], "ราคาหุ้นวันหมดอายุ", ymax=float(fA.max()) * 1.08)
    mask = S >= 120
    _fill_between(out, sx, sy, S[mask], fB[mask], RED, 0.30)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, fA)], BLUE, 2.4)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, fB)], RED, 2.4)
    out.append(f'<line x1="{sx(120):.1f}" y1="{y0}" x2="{sx(120):.1f}" y2="{y0+h}" stroke="{PURPLE}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    _txt(out, sx(120) + 4, y0 + 12, "Strike 120", PURPLE, "start", bold=True)
    _txt(out, sx(100) + 8, sy(fA.max()) + 4, "หุ้น A (σ แคบ)", BLUE, "start", bold=True)
    _txt(out, sx(100) + 8, sy(fA.max()) + 16, "เกือบไม่มีทางเลย 120", BLUE, "start", size=9)
    _txt(out, sx(60), sy(fB.max() * 1.6), "หุ้น B (σ กว้าง)", RED, "middle", bold=True)
    _txt(out, sx(141), sy(fB.max() * 1.35), f"พื้นที่เลย strike ของ B ≈ {pB*100:.0f}%", RED, "middle", bold=True)
    _txt(out, sx(141), sy(fB.max() * 1.35) + 12, "→ Option แพงกว่า", RED, "middle", size=9)
    out.append("</svg>")
    NUMS["m2-two-bells-strike"] = dict(pA=pA, pB=pB)
    return "\n".join(out)


def hist_data(n=500, sg=1.2, seed=7):
    rng = np.random.default_rng(seed); r = rng.normal(0, sg, n)
    edges = np.arange(-4.5, 4.51, 0.5); cnt, _ = np.histogram(r, edges)
    return r, edges, cnt


@fig("math-part2.html", "m2-histogram")
def fig_m2_histogram():
    r, edges, cnt = hist_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, "Histogram ผลตอบแทนรายวัน 500 วัน (จำลอง σ = 1.2%) รูประฆัง มีเส้น Normal ทาบ")
    title(out, Wd, "Histogram — เอาผลตอบแทนรายวันมากองใส่ช่อง ช่องไหนสูง = เกิดบ่อย → รูประฆัง",
          f"จำลอง 500 วัน ผลตอบแทน ~ Normal(0, σ = 1.2%) · ช่องกว้าง 0.5% · ค่าเฉลี่ยตัวอย่าง {r.mean():+.2f}% · σ ตัวอย่าง {r.std(ddof=1):.2f}%")
    x0, y0, w, h = 55, 48, 483, 180
    ymax = cnt.max() * 1.15
    sx, sy = frame(out, x0, y0, w, h, [(v, f"{v:+.0f}%".replace("+0%", "0%").replace("-", "−")) for v in range(-4, 5)], [(0, "0"), (ymax, "")], xlab="ผลตอบแทนรายวัน (%)", ylab="จำนวนวัน", grid_y=False)
    for a, b, c in zip(edges[:-1], edges[1:], cnt):
        if c: out.append(f'<rect x="{sx(a)+1:.1f}" y="{sy(c):.1f}" width="{sx(b)-sx(a)-2:.1f}" height="{sy(0)-sy(c):.1f}" fill="{BLUE}" opacity="0.55"/>')
    xs = np.linspace(-4.5, 4.5, 300); dens = _npdf(xs / r.std(ddof=1)) / r.std(ddof=1) * len(r) * 0.5
    polyline(out, [(sx(a), sy(b)) for a, b in zip(xs, dens)], RED, 2.4)
    _txt(out, sx(1.6), sy(dens.max() * 0.85), "เส้น Normal ทาบ", RED, "start", bold=True)
    _txt(out, sx(-4.4), sy(cnt.max()), f"ช่องสูงสุด {cnt.max()} วัน ที่ใกล้ 0%", INK2, "start", size=9)
    out.append("</svg>")
    NUMS["m2-histogram"] = dict(mean=float(r.mean()), sd=float(r.std(ddof=1)), peak=int(cnt.max()))
    return "\n".join(out)


def two_bells_sigma_data():
    rA = np.array([1, -1, 2, -2.0]); rB = np.array([10, -8, 12, -14.0])
    return rA.std(ddof=0), rB.std(ddof=0)  # เล่มใช้ σ ประชากร (หาร n) → 1.58% และ 11.2%


@fig("math-part2.html", "m2-two-bells-sigma")
def fig_m2_two_bells_sigma():
    sA, sB = two_bells_sigma_data()
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"ระฆังสองใบ หุ้น A σ = {sA:.2f}% แคบสูง หุ้น B σ = {sB:.1f}% กว้างเตี้ย พื้นที่ใต้กราฟเท่ากัน")
    title(out, Wd, "σ คือความกว้างของระฆัง — A นิ่ง (แคบสูง) · B เหวี่ยง (กว้างเตี้ย) · พื้นที่เท่ากัน 100%",
          f"หุ้น A ผลตอบแทน +1, −1, +2, −2% → σ = {sA:.2f}% · หุ้น B +10, −8, +12, −14% → σ = {sB:.1f}% · mean 0% ทั้งคู่")
    x = np.linspace(-35, 35, 701)
    fA = _npdf(x / sA) / sA; fB = _npdf(x / sB) / sB
    sx, sy, (x0, y0, w, h) = _bell_frame(out, Wd, H, [(-30, "−30%"), (-20, "−20%"), (-10, "−10%"), (0, "0"), (10, "+10%"), (20, "+20%"), (30, "+30%")], "ผลตอบแทน", ymax=float(fA.max()) * 1.08)
    _fill_between(out, sx, sy, x, fB, RED, 0.12); _fill_between(out, sx, sy, x, fA, BLUE, 0.12)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(x, fA)], BLUE, 2.4); polyline(out, [(sx(a), sy(b)) for a, b in zip(x, fB)], RED, 2.4)
    _txt(out, sx(0) + 8, sy(fA.max()) + 4, f"หุ้น A · σ = {sA:.2f}% — แคบ = นิ่ง", BLUE, "start", bold=True)
    _txt(out, sx(29.5), sy(fB.max() * 1.6), f"หุ้น B · σ = {sB:.1f}% — กว้าง = เหวี่ยง", RED, "end", bold=True)
    _txt(out, x0 + w, H - 8, "พื้นที่ใต้กราฟเท่ากัน (= 100%) — B แค่ \"เตี้ยลงและกว้างออก\"", INK2, "end", size=9, italic=True)
    out.append("</svg>")
    NUMS["m2-two-bells-sigma"] = dict(sA=float(sA), sB=float(sB))
    return "\n".join(out)


@fig("math-part2.html", "m2-binomial")
def fig_m2_binomial():
    from math import comb
    n, p = 4, 0.5; probs = [comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]
    Wd, H = 560, 290
    out = svg_open(Wd, H, "แท่ง Binomial n = 4 p = 0.5: 6.25% 25% 37.5% 25% 6.25% สมมาตร สูงสุดที่ k = 2")
    title(out, Wd, "โยนเหรียญ 4 ครั้ง — โอกาสได้หัว k ครั้ง: แท่งสมมาตร สูงสุดที่ k = 2 (37.5%)",
          "P(X = k) = C(4, k) · 0.5ᵏ · 0.5⁴⁻ᵏ · รวมทุกแท่ง = 100% · n ยิ่งมาก แท่งยิ่งเข้าใกล้ระฆัง Normal")
    x0, y0, w, h = 55, 48, 483, 170
    sx, sy = frame(out, x0, y0, w, h, [(-0.5, ""), (0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), (4.5, "")], [(0, "0"), (0.1, "10%"), (0.2, "20%"), (0.3, "30%"), (0.4, "40%")], xlab="k (จำนวนครั้งที่ได้หัว)", ylab="ความน่าจะเป็น")
    for k, pr in enumerate(probs):
        out.append(f'<rect x="{sx(k-0.35):.1f}" y="{sy(pr):.1f}" width="{sx(k+0.35)-sx(k-0.35):.1f}" height="{sy(0)-sy(pr):.1f}" fill="{BLUE}" opacity="{0.9 if k == 2 else 0.6}" rx="2"/>')
        _txt(out, sx(k), sy(pr) - 5, f"{pr*100:g}%", INK, "middle", bold=True)
    _txt(out, sx(3.2), sy(0.34), "n ยิ่งมาก → เข้าใกล้ระฆัง Normal", INK2, "start", italic=True)
    out.append("</svg>")
    NUMS["m2-binomial"] = {f"p{k}": pr for k, pr in enumerate(probs)}
    return "\n".join(out)


@fig("math-part2.html", "m2-68-95")
def fig_m2_68_95():
    Wd, H = 560, 300
    p1 = _N(1) - _N(-1); p2 = _N(2) - _N(-2)
    out = svg_open(Wd, H, f"ระฆัง Normal กับกฎ 68-95-99.7: แถบ ±1σ ครอบ {p1*100:.1f}% แถบ ±2σ ครอบ {p2*100:.1f}% หางสองข้างที่เหลือ")
    title(out, Wd, "กฎ 68-95-99.7 — ระฆัง Normal: ±1σ ครอบ 68% · ±2σ ครอบ 95% · เกิน ±2σ คือ \"หาง\" ราว 5%",
          f"คำนวณจริง: N(1) − N(−1) = {p1*100:.1f}% · N(2) − N(−2) = {p2*100:.1f}% · หุ้น σ = 20%/ปี → 68% ของปีอยู่ใน ±20%")
    x = np.linspace(-3.5, 3.5, 701); f = _npdf(x)
    sx, sy, (x0, y0, w, h) = _bell_frame(out, Wd, H, [(-3, "μ−3σ"), (-2, "μ−2σ"), (-1, "μ−1σ"), (0, "μ"), (1, "μ+1σ"), (2, "μ+2σ"), (3, "μ+3σ")], "", ymax=float(f.max()) * 1.1)
    m2 = (x >= -2) & (x <= 2); m1 = (x >= -1) & (x <= 1)
    _fill_between(out, sx, sy, x[m2], f[m2], AMBER, 0.22); _fill_between(out, sx, sy, x[m1], f[m1], BLUE, 0.28)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(x, f)], INK, 2.4)
    for v in (-2, -1, 1, 2):
        out.append(f'<line x1="{sx(v):.1f}" y1="{sy(0):.1f}" x2="{sx(v):.1f}" y2="{sy(_npdf(v)):.1f}" stroke="{INK2}" stroke-width="1" stroke-dasharray="3 3"/>')
    _txt(out, sx(0), sy(0.17), f"{p1*100:.0f}%", BLUE, "middle", size=13, bold=True); _txt(out, sx(0), sy(0.17) + 13, "อยู่ใน ±1σ", BLUE, "middle", size=9)
    _txt(out, sx(1.5), sy(0.04), f"{p2*100:.0f}% อยู่ใน ±2σ", AMBER, "middle", bold=True)
    _txt(out, sx(2.7), sy(0.03), "หาง ≈ 2.3%", RED, "middle", size=9, bold=True); _txt(out, sx(-2.7), sy(0.03), "หาง ≈ 2.3%", RED, "middle", size=9, bold=True)
    out.append("</svg>")
    NUMS["m2-68-95"] = dict(p1=p1, p2=p2)
    return "\n".join(out)


@fig("math-part2.html", "m2-Nd")
def fig_m2_Nd():
    d = 0.5; Nd = _N(d)
    Wd, H = 560, 290
    out = svg_open(Wd, H, f"N(d) คือพื้นที่สะสมใต้ระฆังมาตรฐานทางซ้ายของ d: ที่ d = 0.5 พื้นที่ = {Nd:.4f}")
    title(out, Wd, f"N(d) = พื้นที่ใต้ระฆังทางซ้ายของ d — ตัวอย่าง d = 0.5 → N(0.5) = {Nd:.4f}",
          "N(0) = 0.5 พอดี (ครึ่งซ้าย) · d ยิ่งมาก พื้นที่ยิ่งเข้าใกล้ 1 · d ติดลบ พื้นที่น้อยกว่า 0.5 · ใน Black-Scholes ใช้ N(d₁) และ N(d₂)")
    x = np.linspace(-3.5, 3.5, 701); f = _npdf(x)
    sx, sy, (x0, y0, w, h) = _bell_frame(out, Wd, H, [(-3, "−3"), (-2, "−2"), (-1, "−1"), (0, "0"), (1, "1"), (2, "2"), (3, "3")], "z (หน่วย σ)", ymax=float(f.max()) * 1.1)
    m = x <= d; _fill_between(out, sx, sy, x[m], f[m], BLUE, 0.30)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(x, f)], INK, 2.4)
    out.append(f'<line x1="{sx(d):.1f}" y1="{sy(0):.1f}" x2="{sx(d):.1f}" y2="{sy(_npdf(d)):.1f}" stroke="{PURPLE}" stroke-width="1.6"/>')
    _txt(out, sx(d), sy(0) + 14, "d = 0.5", PURPLE, "middle", bold=True)
    _txt(out, sx(-0.6), sy(0.15), f"N(d) = {Nd:.4f}", BLUE, "middle", size=12, bold=True); _txt(out, sx(-0.6), sy(0.15) + 13, "= พื้นที่ทางซ้าย", BLUE, "middle", size=9)
    _txt(out, sx(1.8), sy(0.08), f"ที่เหลือ 1 − N(d) = {1-Nd:.4f}", INK2, "middle", size=9)
    out.append("</svg>")
    NUMS["m2-Nd"] = dict(Nd=Nd)
    return "\n".join(out)


def lognormal_data(S0=100.0, sg=0.20, T=1.0):
    S = np.linspace(0.5, 200, 800)
    mu = np.log(S0) - sg * sg * T / 2
    f_ln = np.exp(-(np.log(S) - mu) ** 2 / (2 * sg * sg * T)) / (S * sg * np.sqrt(2 * np.pi * T))
    sd = S0 * sg * np.sqrt(T)  # normal ที่มี σ ราคาเท่ากัน ๆ ไว้เทียบ
    f_n = _npdf((S - S0) / sd) / sd
    return S, f_n, f_ln, float(np.exp(mu)), float(np.exp(mu - sg * sg * T))


@fig("math-part2.html", "m2-normal-vs-lognormal")
def fig_m2_normal_vs_lognormal():
    S, f_n, f_ln, med, mode = lognormal_data()
    Wd, H = 560, 300
    out = svg_open(Wd, H, "เทียบระฆัง Normal สมมาตรที่ลากไปถึงค่าลบได้ กับ Lognormal ของราคาหุ้นที่เริ่มจาก 0 และเบ้ขวา")
    title(out, Wd, "Normal สมมาตรและ \"ติดลบได้\" — Lognormal ของราคาหุ้นเริ่มที่ 0 และเบ้ขวา",
          f"S₀ = 100 · σ = 20% · 1 ปี · Lognormal: มัธยฐาน {med:.1f} · ยอด (mode) {mode:.1f} · หางขวายาวกว่าหางซ้าย")
    xt = [(0, "0"), (50, "50"), (100, "100"), (150, "150"), (200, "200")]
    sx, sy, (x0, y0, w, h) = _bell_frame(out, Wd, H, xt, "ราคาหุ้น S", ymax=float(max(f_n.max(), f_ln.max())) * 1.1)
    Sn = np.linspace(0, 200, 801); sd = 20.0; fn = _npdf((Sn - 100) / sd) / sd
    polyline(out, [(sx(a), sy(b)) for a, b in zip(Sn, fn)], INK2, 2.0, dash="6 3", shadow=False)
    _fill_between(out, sx, sy, S, f_ln, GREEN, 0.15); polyline(out, [(sx(a), sy(b)) for a, b in zip(S, f_ln)], GREEN, 2.5)
    out.append(f'<line x1="{sx(0):.1f}" y1="{y0}" x2="{sx(0):.1f}" y2="{y0+h}" stroke="{RED}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    _txt(out, sx(0) + 5, y0 + 12, "S = 0 ขอบล่าง — ราคาติดลบไม่ได้", RED, "start", size=9, bold=True)
    _txt(out, sx(140), sy(f_n.max() * 0.62), "Normal (เส้นประ): สมมาตร มีค่าลบได้ ✗", INK2, "start", size=9)
    _txt(out, sx(140), sy(f_ln.max() * 0.42), "Lognormal (ราคาหุ้น): เบ้ขวา ✓", GREEN, "start", bold=True)
    out.append("</svg>")
    NUMS["m2-normal-vs-lognormal"] = dict(median=med, mode=mode)
    return "\n".join(out)


def fat_tail_data(nu=3.0):
    from math import gamma, sqrt, pi
    x = np.linspace(-5, 5, 1001)
    s = sqrt(nu / (nu - 2))  # ปรับให้ t มีความแปรปรวน 1 เท่ากับ Normal
    t = gamma((nu + 1) / 2) / (sqrt(nu * pi) * gamma(nu / 2)) * (1 + (x * s) ** 2 / nu) ** (-(nu + 1) / 2) * s
    n = _npdf(x)
    # ความน่าจะเป็นที่เกิน 3σ (สองข้าง) เทียบกัน
    # หางจริงของ t ต้องอินทิเกรตถึงอนันต์ — ผลรวมบนกริด ±5 ตัดส่วนที่เกิน ±5σ ทิ้ง (เคยได้ 1.06% แทน 1.38%)
    # t ที่ ν = 3 มี CDF ปิด: F(u) = ½ + (1/π)[ (u/√3)/(1 + u²/3) + arctan(u/√3) ]
    assert nu == 3.0, "สูตรหางปิดข้างล่างใช้ได้เฉพาะ ν = 3"
    c = 3 * s; u = c / sqrt(3)
    tail_t = 2 * (0.5 - (u / (1 + u * u) + np.arctan(u)) / pi); tail_n = 2 * (1 - _N(3))
    return x, n, t, tail_n, tail_t


@fig("math-part2.html", "m2-fat-tails")
def fig_m2_fat_tails():
    x, n, t, tail_n, tail_t = fat_tail_data()
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"เทียบระฆัง Normal หางบาง กับการแจกแจงหางหนา (Student-t ν = 3 ความแปรปรวนเท่ากัน): เกิน 3σ Normal {tail_n*100:.2f}% หางหนา {tail_t*100:.1f}%")
    title(out, Wd, "หางหนา (fat tails) — ความแปรปรวนเท่ากัน แต่เหตุการณ์สุดขั้วเกิดบ่อยกว่า Normal หลายเท่า",
          f"ตัวแทนตลาดจริง = Student-t (ν = 3) ปรับให้ σ เท่ากัน · โอกาสเกิน ±3σ: Normal {tail_n*100:.2f}% · หางหนา {tail_t*100:.1f}% (≈ {tail_t/tail_n:.0f} เท่า)")
    sx, sy, (x0, y0, w, h) = _bell_frame(out, Wd, H, [(-4, "−4σ"), (-3, "−3σ"), (-2, "−2σ"), (-1, "−1σ"), (0, "0"), (1, "+1σ"), (2, "+2σ"), (3, "+3σ"), (4, "+4σ")], "", ymax=float(t.max()) * 1.1)
    xs = np.linspace(-5, 5, 1001)
    mt = np.abs(xs) >= 2.5
    _fill_between(out, sx, sy, xs[xs <= -2.5], t[xs <= -2.5], RED, 0.35); _fill_between(out, sx, sy, xs[xs >= 2.5], t[xs >= 2.5], RED, 0.35)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(xs, n)], INK2, 2.2, dash="6 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(xs, t)], RED, 2.5)
    _txt(out, sx(0) + 8, sy(t.max()) + 4, "ตลาดจริง (หางหนา): ยอดสูงกว่า ไหล่ต่ำกว่า", RED, "start", bold=True)
    _txt(out, sx(-0.7), sy(n.max()) - 2, "Normal (หางบาง · เส้นประ)", INK2, "end", size=9)
    _txt(out, sx(-3.3), sy(0.06), "crash บ่อยกว่าที่ Normal บอก", RED, "middle", size=9, bold=True); _txt(out, sx(3.3), sy(0.06), "rally บ่อยกว่าที่ Normal บอก", RED, "middle", size=9, bold=True)
    out.append("</svg>")
    NUMS["m2-fat-tails"] = dict(tail_n=tail_n, tail_t=tail_t)
    return "\n".join(out)


# ── คณิตศาสตร์เล่ม 1 Part III–VI (math-part3…7) — กราฟตัวเลขที่เคยวาดมือ ────────────────────
@fig("math-part3.html", "m3-tangent")
def fig_m3_tangent():
    x1 = 1.0; f1 = x1 ** 2; m = 2 * x1
    Wd, H = 560, 300
    out = svg_open(Wd, H, "เส้นโค้ง f(x) = x² กับเส้นสัมผัสที่ x = 1 ความชัน f′(1) = 2 และเส้น secant จาก h = 1 ที่ชันกว่า")
    title(out, Wd, "อนุพันธ์ = ความชันของเส้นสัมผัส — f(x) = x² ที่ x = 1: f′(1) = 2·1 = 2",
          "secant (h = 1) ชัน [f(2) − f(1)]/1 = 3 · บีบ h → 0 จะกลายเป็นเส้นสัมผัสชัน 2 · Delta คือความชันแบบนี้")
    (sx, sy), _ = _std_frame(out, Wd, H, [(-1, "−1"), (0, "0"), (1, "1"), (2, "2"), (3, "3")], [(-1, "−1"), (0, "0"), (2, "2"), (4, "4"), (6, "6"), (8, "8")], "x", "f(x)")
    _zero_line(out, sx, sy, -1, 3)
    xs = np.linspace(-1, 3, 200); polyline(out, [(sx(a), sy(a * a)) for a in xs], BLUE, 2.6)
    polyline(out, [(sx(-0.5), sy(f1 + m * (-0.5 - x1))), (sx(3), sy(f1 + m * (3 - x1)))], GREEN, 2.0)
    polyline(out, [(sx(-0.2), sy(f1 + 3 * (-0.2 - x1))), (sx(2.8), sy(f1 + 3 * (2.8 - x1)))], AMBER, 1.6, dash="5 3", shadow=False)
    _dot(out, sx(1), sy(1)); _dot(out, sx(2), sy(4), AMBER, 3.5)
    _txt(out, sx(1) + 8, sy(1) + 14, "(1, 1)", PURPLE, "start", bold=True); _txt(out, sx(2) + 8, sy(4) + 4, "(2, 4) จุดที่ h = 1", AMBER, "start", size=9)
    _txt(out, sx(-0.9), sy(7.3), "f(x) = x²", BLUE, "start", bold=True)
    _txt(out, sx(3) - 4, sy(2.2), "เส้นสัมผัส ชัน f′(1) = 2", GREEN, "end", bold=True)
    _txt(out, sx(0.0), sy(5.5), "secant h = 1 ชัน 3 (เส้นประ)", AMBER, "start", size=9)
    out.append("</svg>")
    NUMS["m3-tangent"] = dict(slope=m, secant=3.0)
    return "\n".join(out)


@fig("math-part3.html", "m3-call-curve-gamma")
def fig_m3_call_curve_gamma():
    S = np.linspace(70, 130, 241); g = bs_greeks(S); g0 = bs_greeks(100.0)
    C, C0, d0, gm0 = g["C"], float(g0["C"]), float(g0["delta"]), float(g0["gamma"])
    # Gamma เทียบ S สูงสุดที่ d₁ = −σ√T คือ S* = K·e^(−(r + 1.5σ²)T) — ต่ำกว่า K เล็กน้อย ไม่ใช่ที่ K พอดี
    s_pk = 100.0 * np.exp(-(0.05 + 1.5 * 0.20 ** 2) * 0.5); g_pk = float(bs_greeks(s_pk)["gamma"])
    assert abs(float(S[np.argmax(g["gamma"])]) - s_pk) < 0.3, "จุดสูงสุดของ Γ บนกริดต้องตรงกับสูตร"
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"เส้นราคา Call ความชัน Delta {d0:.2f} ที่ S = 100 โค้งมากที่สุดแถว ATM (Gamma สูงสุดจริงที่ S ≈ {s_pk:.1f}) แบนทางซ้าย OTM และเกือบตรงทางขวา ITM")
    title(out, Wd, "ราคา Call เทียบราคาหุ้น — ความชัน = Delta · ความโค้ง = Gamma (สูงแถว ATM)",
          f"K = 100 · σ = 20% · r = 5% · T = 0.5 ปี · ที่ S = 100: C = {C0:.2f} · Delta = {d0:.2f} · Gamma = {gm0:.4f} ต่อ ฿1")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(70, "70"), (80, "80"), (90, "90"), (100, "100 (K)"), (110, "110"), (120, "120"), (130, "130")], [(0, "0"), (10, "10"), (20, "20"), (30, "30")], "S (ราคาหุ้น)", "ราคา Call")
    polyline(out, [(sx(a), sy(max(a - 100, 0))) for a in S], INK2, 1.4, dash="4 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, C)], BLUE, 2.6)
    polyline(out, [(sx(90), sy(C0 + d0 * -10)), (sx(112), sy(C0 + d0 * 12))], GREEN, 1.8)
    _dot(out, sx(100), sy(C0))
    _txt(out, sx(100) - 8, sy(C0) - 8, f"ความชัน = Delta ≈ {d0:.2f}", GREEN, "end", bold=True)
    _txt(out, sx(100) + 8, sy(C0) + 16, f"Gamma ที่ ATM = {gm0:.4f}", PURPLE, "start", bold=True)
    _txt(out, sx(100) + 8, sy(C0) + 29, f"(สูงสุดจริงที่ S ≈ {s_pk:.1f}: {g_pk:.4f})", PURPLE, "start", size=9)
    _txt(out, sx(72), sy(3.5), "OTM: เกือบแบน (Γ ต่ำ · Δ → 0)", INK2, "start", size=9, italic=True)
    _txt(out, sx(129), sy(6), "ITM: เกือบตรง (Γ ต่ำ · Δ → 1)", INK2, "end", size=9, italic=True)
    _txt(out, sx(129), sy(29.2), "เส้นประ = intrinsic max(S − K, 0)", INK2, "end", size=9)
    out.append("</svg>")
    NUMS["m3-call-curve-gamma"] = dict(C=C0, delta=d0, gamma=gm0, s_peak=s_pk, gamma_peak=g_pk)
    return "\n".join(out)


def port_risk_data(w=(0.6, 0.4), s1=0.20, s2=0.30, cov=0.01):
    var = w[0] ** 2 * s1 ** 2 + w[1] ** 2 * s2 ** 2 + 2 * w[0] * w[1] * cov
    return s1, s2, w[0] * s1 + w[1] * s2, var ** 0.5


@fig("math-part4.html", "m4-port-risk-bars")
def fig_m4_port_risk_bars():
    s1, s2, naive, real = port_risk_data()
    Wd, H = 560, 290
    out = svg_open(Wd, H, f"แท่งเทียบความเสี่ยง: หุ้น A 20% หุ้น B 30% เดาไร้เดียงสา 60/40 ได้ {naive*100:.0f}% แต่พอร์ตจริง {real*100:.1f}% ต่ำกว่าหุ้นที่นิ่งที่สุด")
    title(out, Wd, f"20% + 30% ผสม 60/40 — เดาว่า {naive*100:.0f}% แต่พอร์ตจริงเสี่ยงแค่ {real*100:.1f}%",
          "σ²ₚ = 0.6²(0.04) + 2(0.6)(0.4)(0.01) + 0.4²(0.09) = 0.0336 → σₚ = 18.3% · Cov ต่ำ (0.01) ดึงความเสี่ยงรวมลง")
    x0, y0, w, h = 70, 50, 470, 175; out.append(ARROW_DEF)
    sx, sy = frame(out, x0, y0, w, h, [(0, ""), (4, "")], [(0, "0"), (0.1, "10%"), (0.2, "20%"), (0.3, "30%")], xlab="", ylab="σ")
    bars = [(0.5, s1, BLUE, "หุ้น A", f"{s1*100:.0f}%"), (1.5, s2, BLUE, "หุ้น B", f"{s2*100:.0f}%"),
            (2.5, naive, AMBER, "เดาไร้เดียงสา (0.6·20 + 0.4·30)", f"{naive*100:.0f}%"), (3.5, real, GREEN, "พอร์ตจริง √(wᵀΣw)", f"{real*100:.1f}%")]
    for xc, v, col, lab, vl in bars:
        out.append(f'<rect x="{sx(xc-0.32):.1f}" y="{sy(v):.1f}" width="{sx(xc+0.32)-sx(xc-0.32):.1f}" height="{sy(0)-sy(v):.1f}" fill="{col}" opacity="0.75" rx="3"/>')
        _txt(out, sx(xc), sy(v) - 6, vl, INK, "middle", bold=True); _txt(out, sx(xc), y0 + h + 14, lab, INK2, "middle", size=9)
    out.append(f'<line x1="{sx(2.5):.1f}" y1="{sy(naive):.1f}" x2="{sx(3.5):.1f}" y2="{sy(real):.1f}" stroke="{RED}" stroke-width="1.4" stroke-dasharray="4 3" marker-end="url(#arr)"/>')
    _txt(out, sx(3.0), sy((naive + real) / 2) - 8, "covariance ต่ำ ดึงลงมา", RED, "middle", size=9, bold=True)
    out.append("</svg>")
    NUMS["m4-port-risk-bars"] = dict(naive=naive, real=real)
    return "\n".join(out)


def beta_data():
    x = np.array([3, -2, 5, -1, 2, -4]) / 100; y = np.array([5, -4, 7, 0, 2, -7]) / 100
    xb, yb = x.mean(), y.mean()
    beta = ((x - xb) * (y - yb)).sum() / ((x - xb) ** 2).sum(); alpha = yb - beta * xb
    return x, y, beta, alpha


@fig("math-part4.html", "m4-beta-scatter")
def fig_m4_beta_scatter():
    x, y, beta, alpha = beta_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"scatter ผลตอบแทนหุ้น 6 จุดเทียบตลาด กับเส้น regression ความชัน β = {beta:.2f} และเส้น residual แนวดิ่ง")
    title(out, Wd, f"Regression → Beta: เส้นที่ทำให้ residual² รวมน้อยสุด ความชัน β = {beta:.2f}",
          f"ตลาด X = [3, −2, 5, −1, 2, −4]% · หุ้น Y = [5, −4, 7, 0, 2, −7]% · β = Cov/Var = {beta:.2f} · α = {alpha*100:.2f}% · หุ้นเหวี่ยงกว่าตลาด {beta:.2f} เท่า")
    (sx, sy), _ = _std_frame(out, Wd, H, [(-0.06, "−6%"), (-0.04, "−4%"), (-0.02, "−2%"), (0, "0"), (0.02, "+2%"), (0.04, "+4%"), (0.06, "+6%")], [(-0.09, "−9%"), (-0.06, "−6%"), (-0.03, "−3%"), (0, "0"), (0.03, "+3%"), (0.06, "+6%"), (0.09, "+9%")], "ผลตอบแทนตลาด (X)", "ผลตอบแทนหุ้น (Y)")
    _zero_line(out, sx, sy, -0.06, 0.06); out.append(f'<line x1="{sx(0):.1f}" y1="{sy(0.09):.1f}" x2="{sx(0):.1f}" y2="{sy(-0.09):.1f}" stroke="{AXIS}" stroke-width="1"/>')
    polyline(out, [(sx(-0.06), sy(alpha + beta * -0.06)), (sx(0.06), sy(alpha + beta * 0.06))], BLUE, 2.4)
    for a, b in zip(x, y):
        yhat = alpha + beta * a
        out.append(f'<line x1="{sx(a):.1f}" y1="{sy(b):.1f}" x2="{sx(a):.1f}" y2="{sy(yhat):.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="3 2"/>')
        out.append(f'<circle cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="4.5" fill="{PURPLE}" opacity="0.85"/>')
    _txt(out, sx(0.052), sy(alpha + beta * 0.052) - 10, f"ความชัน = β = {beta:.2f}", BLUE, "end", bold=True)
    _txt(out, sx(-0.058), sy(0.075), "เส้นที่ผลรวมระยะห่าง² (residual) น้อยที่สุด", INK2, "start", size=9, italic=True)
    _txt(out, sx(0.02) + 7, sy(0.02) - 2, "residual", RED, "start", size=9)
    out.append("</svg>")
    NUMS["m4-beta-scatter"] = dict(beta=beta, alpha=alpha)
    return "\n".join(out)


def lp_data():
    corners = [(0, 0), (0, 5), (4, 0), (10 / 3, 5 / 3)]
    z = [8 * a + 5 * b for a, b in corners]
    return corners, z


@fig("math-part5.html", "m5-lp")
def fig_m5_lp():
    corners, z = lp_data()
    Wd, H = 560, 320
    out = svg_open(Wd, H, "LP: feasible region สี่เหลี่ยมใต้เส้น 5x₁ + 2x₂ = 20 และ x₁ + x₂ = 5 มุมที่ดีที่สุด (10/3, 5/3) ให้ z = 35")
    title(out, Wd, "Linear Programming — คำตอบอยู่ที่มุมของ feasible region เสมอ: (10/3, 5/3) ให้ z = 35",
          "Max z = 8x₁ + 5x₂ · งบ 5x₁ + 2x₂ ≤ 20 · จำนวน x₁ + x₂ ≤ 5 · x ≥ 0 · เช็ค 4 มุม: z = 0, 25, 32, 35")
    x0, y0, w, h = 70, 48, 240, 220
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6")], [(0, "0"), (2, "2"), (4, "4"), (6, "6"), (8, "8"), (10, "10")], xlab="x₁ (Call K = 100)", ylab="x₂ (Call K = 110)")
    poly = [(0, 0), (4, 0), (10 / 3, 5 / 3), (0, 5)]
    out.append('<polygon points="' + " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in poly) + f'" fill="{GREEN}" opacity="0.18"/>')
    polyline(out, [(sx(0), sy(10)), (sx(4), sy(0))], RED, 2.0); _txt(out, sx(1.6), sy(6.6), "5x₁ + 2x₂ = 20 (งบ)", RED, "start", size=9, bold=True)
    polyline(out, [(sx(0), sy(5)), (sx(5), sy(0))], BLUE, 2.0); _txt(out, sx(3.3), sy(2.4), "x₁ + x₂ = 5", BLUE, "start", size=9, bold=True)
    _txt(out, sx(1.1), sy(1.6), "Feasible", GREEN, "start", bold=True); _txt(out, sx(1.1), sy(1.0), "Region", GREEN, "start", bold=True)
    # เส้นระดับ z = 35 ผ่านจุดดีที่สุด
    polyline(out, [(sx(0), sy(7)), (sx(4.375), sy(0))], PURPLE, 1.4, dash="5 3", shadow=False); _txt(out, sx(0.15), sy(7.5), "z = 35 (เส้นระดับ)", PURPLE, "start", size=9)
    for (a, b), zz in zip(corners, z):
        best = zz == max(z); _dot(out, sx(a), sy(b), PURPLE if best else INK2, 4.5 if best else 3.5)
    # ตารางมุมด้านขวา
    tx = 340; _txt(out, tx, y0 + 12, "มุม (x₁, x₂)", INK, "start", bold=True); _txt(out, tx + 150, y0 + 12, "z = 8x₁ + 5x₂", INK, "start", bold=True)
    labels = ["(0, 0)", "(0, 5)", "(4, 0)", "(10/3, 5/3)"]
    for i, (lab, zz) in enumerate(zip(labels, z)):
        best = zz == max(z); col = PURPLE if best else INK2
        _txt(out, tx, y0 + 34 + i * 20, lab, col, "start", bold=best); _txt(out, tx + 150, y0 + 34 + i * 20, f"{zz:g}" + (" ← ดีที่สุด" if best else ""), col, "start", bold=best)
    _txt(out, tx, y0 + 34 + 4 * 20 + 6, "มุมที่ดีที่สุด = จุดตัดของสองเส้น constraint:", INK2, "start", size=9)
    _txt(out, tx, y0 + 34 + 4 * 20 + 20, "แก้ 5x₁ + 2x₂ = 20 กับ x₁ + x₂ = 5 → x₁ = 10/3, x₂ = 5/3", INK2, "start", size=9)
    _txt(out, tx, y0 + 34 + 4 * 20 + 34, "z = 8(10/3) + 5(5/3) = 80/3 + 25/3 = 35", INK2, "start", size=9)
    out.append("</svg>")
    NUMS["m5-lp"] = {f"z{i}": v for i, v in enumerate(z)}
    return "\n".join(out)


def gd_data(x0=0.0, alpha=0.1, steps=8):
    xs = [x0]
    for _ in range(steps): xs.append(xs[-1] - alpha * 2 * (xs[-1] - 3))
    return xs


@fig("math-part5.html", "m5-gradient-descent")
def fig_m5_gradient_descent():
    xs = gd_data()
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"gradient descent บน f(x) = (x − 3)² + 2 เริ่ม x = 0 ก้าว α = 0.1: 0 → 0.6 → 1.08 → … → {xs[-1]:.2f} เข้าหาก้นหลุม x = 3")
    title(out, Wd, "Gradient Descent — เดินลงเขาทีละก้าว: xₜ₊₁ = xₜ − α·f′(xₜ) เข้าหาก้นหลุมที่ x = 3",
          f"f(x) = (x − 3)² + 2 · f′(x) = 2(x − 3) · เริ่ม x = 0 · α = 0.1 · 8 ก้าว: " + " → ".join(f"{v:.2f}" for v in xs[:5]) + f" → … → {xs[-1]:.2f}")
    (sx, sy), _ = _std_frame(out, Wd, H, [(-1, "−1"), (0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")], [(0, "0"), (4, "4"), (8, "8"), (12, "12"), (16, "16"), (20, "20")], "x", "f(x)")
    out.append(ARROW_DEF); gx = np.linspace(-1, 5, 200); polyline(out, [(sx(a), sy((a - 3) ** 2 + 2)) for a in gx], BLUE, 2.4)
    f = lambda v: (v - 3) ** 2 + 2
    for i, (a, b) in enumerate(zip(xs[:-1], xs[1:])):
        out.append(f'<line x1="{sx(a):.1f}" y1="{sy(f(a)):.1f}" x2="{sx(b):.1f}" y2="{sy(f(b)):.1f}" stroke="{RED}" stroke-width="1.6" marker-end="url(#arr)"/>')
    for i, a in enumerate(xs):
        _dot(out, sx(a), sy(f(a)), RED if i < len(xs) - 1 else PURPLE, 3.6)
    _txt(out, sx(0) - 6, sy(f(0)) - 8, "เริ่ม x = 0 · ชัน f′ = −6 → ก้าวไปทางขวา 0.6", RED, "start", size=9, bold=True)
    _txt(out, sx(3), sy(2) + 16, "จุดต่ำสุด x = 3 (f′ = 0 หยุดเดิน)", PURPLE, "middle", bold=True)
    _txt(out, sx(4.9), sy(17), "ก้าวสั้นลงเรื่อย ๆ เพราะความชันเล็กลงเมื่อใกล้ก้นหลุม", INK2, "end", size=9, italic=True)
    out.append("</svg>")
    NUMS["m5-gradient-descent"] = {f"x{i}": v for i, v in enumerate(xs)}
    return "\n".join(out)


def frontier_data(m1=0.08, s1=0.20, m2=0.12, s2=0.30, rho=0.2):
    w = np.linspace(-0.3, 1.3, 321)
    mu = w * m1 + (1 - w) * m2
    var = w ** 2 * s1 ** 2 + (1 - w) ** 2 * s2 ** 2 + 2 * w * (1 - w) * rho * s1 * s2
    wmin = (s2 ** 2 - rho * s1 * s2) / (s1 ** 2 + s2 ** 2 - 2 * rho * s1 * s2)
    mu_min = wmin * m1 + (1 - wmin) * m2; s_min = (wmin ** 2 * s1 ** 2 + (1 - wmin) ** 2 * s2 ** 2 + 2 * wmin * (1 - wmin) * rho * s1 * s2) ** 0.5
    return w, mu, np.sqrt(var), wmin, mu_min, s_min


@fig("math-part5.html", "m5-frontier")
def fig_m5_frontier():
    w, mu, sg, wmin, mu_min, s_min = frontier_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"Efficient Frontier รูปกระสุนจากหุ้นสองตัว ขอบบนคือเส้นที่ดีที่สุด จุด min-variance ที่ σ = {s_min*100:.1f}% ผลตอบแทน {mu_min*100:.1f}%")
    title(out, Wd, "Efficient Frontier — ส่วนผสมสองหุ้นวางเป็นรูปกระสุน ขอบบนซ้ายคือ \"ดีที่สุด\" ในแต่ละระดับ σ",
          f"A: μ 8% σ 20% · B: μ 12% σ 30% · ρ = 0.2 · Min-Variance ที่ w_A = {wmin*100:.0f}%: σ = {s_min*100:.1f}% μ = {mu_min*100:.1f}% · ขอบล่างแย่กว่าเสมอ")
    (sx, sy), _ = _std_frame(out, Wd, H, [(0.10, "10%"), (0.15, "15%"), (0.20, "20%"), (0.25, "25%"), (0.30, "30%"), (0.35, "35%")], [(0.06, "6%"), (0.08, "8%"), (0.10, "10%"), (0.12, "12%"), (0.14, "14%")], "ความเสี่ยง σ →", "ผลตอบแทนคาดหวัง μ")
    up = mu >= mu_min; lo_ = mu <= mu_min
    polyline(out, [(sx(a), sy(b)) for a, b in zip(sg[lo_], mu[lo_])], INK2, 1.8, dash="6 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(sg[up], mu[up])], BLUE, 2.8)
    _dot(out, sx(0.20), sy(0.08), INK2, 4); _txt(out, sx(0.20) + 8, sy(0.08) + 14, "หุ้น A (100% A)", INK2, "start", size=9)
    _dot(out, sx(0.30), sy(0.12), INK2, 4); _txt(out, sx(0.30) + 8, sy(0.12) + 14, "หุ้น B (100% B)", INK2, "start", size=9)
    _dot(out, sx(s_min), sy(mu_min)); _txt(out, sx(s_min) + 8, sy(mu_min) + 4, f"Min-Variance (σ {s_min*100:.1f}%)", PURPLE, "start", bold=True)
    _txt(out, sx(0.20), sy(0.126), "Efficient Frontier (ขอบบน)", BLUE, "start", bold=True)
    _txt(out, sx(0.235), sy(0.068), "ขอบล่าง = เสี่ยงเท่ากันแต่ได้น้อยกว่า — ไม่มีใครเลือก", INK2, "start", size=9, italic=True)
    out.append("</svg>")
    NUMS["m5-frontier"] = dict(wmin=wmin, mu_min=mu_min, s_min=s_min)
    return "\n".join(out)


def sma_ewma_data(n=120, spike=60, lam=0.94, sg=0.01, seed=11):
    rng = np.random.default_rng(seed); r = rng.normal(0, sg, n); r[spike] = 0.05
    sma = np.full(n, np.nan); ew = np.zeros(n); ew[0] = sg * sg
    for t in range(n):
        if t >= 19: sma[t] = np.sqrt(np.mean(r[t - 19:t + 1] ** 2))
        if t: ew[t] = lam * ew[t - 1] + (1 - lam) * r[t - 1] ** 2
    return r, sma, np.sqrt(ew)


@fig("math-part6.html", "m6-sma-ewma")
def fig_m6_sma_ewma():
    r, sma, ew = sma_ewma_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, "เทียบ σ จาก SMA 20 วันที่กระโดดขึ้นแล้วตกฮวบเมื่อวัน spike หลุดหน้าต่าง กับ EWMA λ = 0.94 ที่ขึ้นไวและจางลงเนียน")
    title(out, Wd, "SMA กับ EWMA หลังวัน spike — SMA ค้างแล้วตกฮวบ · EWMA ขึ้นทันทีแล้วค่อย ๆ จาง",
          f"จำลอง 120 วัน σ 1% · วันที่ 60 ผลตอบแทน +5% · SMA 20 วัน · EWMA λ = 0.94 · สูงสุด SMA {np.nanmax(sma)*100:.2f}% · EWMA {ew.max()*100:.2f}%")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (20, "20"), (40, "40"), (60, "60"), (80, "80"), (100, "100"), (120, "120")], [(0, "0"), (0.01, "1%"), (0.02, "2%"), (0.03, "3%")], "วัน", "σ รายวัน")
    out.append(f'<line x1="{sx(60):.1f}" y1="{y0}" x2="{sx(60):.1f}" y2="{y0+h}" stroke="{RED}" stroke-width="1.2" stroke-dasharray="4 3"/>'); _txt(out, sx(60) + 4, y0 + 12, "วันที่ 60: σ พุ่ง (ผลตอบแทน +5%)", RED, "start", size=9, bold=True)
    t = np.arange(len(r))
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t[19:], sma[19:])], AMBER, 2.2)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, ew)], BLUE, 2.4)
    _txt(out, sx(119), sy(np.nanmax(sma)) - 7, "SMA ค้าง 20 วัน แล้วตกฮวบเมื่อ spike หลุดหน้าต่าง", AMBER, "end", size=9, bold=True)
    _txt(out, sx(3), sy(0.026), f"EWMA ขึ้นทันทีวันถัดไป ({ew.max()*100:.2f}%) แล้ว σ² จางลง 6%/วัน (σ ≈ {(1-0.94**0.5)*100:.0f}%/วัน)", BLUE, "start", size=9, bold=True)
    legend(out, [(AMBER, "SMA 20 วัน (ช้า + กระตุก)", ""), (BLUE, "EWMA λ = 0.94 (ไว + เนียน)", "")], x0, H - 10)
    out.append("</svg>")
    NUMS["m6-sma-ewma"] = dict(sma_max=float(np.nanmax(sma)), ew_max=float(ew.max()))
    return "\n".join(out)


def newton_data(sigma_true=0.25, s0=0.15, S=100.0, K=100.0, r=0.05, T=1.0):
    """Call ชุดเดียวกับ bisection/โค้ดในบท §9.3: S = K = 100 · r = 5% · T = 1 ปี → ราคา 12.336"""
    price = float(bs_greeks(S, K=K, r=r, sg=sigma_true, T=T)["C"])
    def f(sg): return float(bs_greeks(S, K=K, r=r, sg=sg, T=T)["C"]) - price
    def vega(sg): return float(bs_greeks(S, K=K, r=r, sg=sg, T=T)["vega1"]) * 100  # ต่อ 1 หน่วย σ
    its = [s0]
    for _ in range(3): its.append(its[-1] - f(its[-1]) / vega(its[-1]))
    return price, f, vega, its


@fig("math-part6.html", "m6-newton")
def fig_m6_newton():
    price, f, vega, its = newton_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"Newton-Raphson หา IV: จากเดา σ₁ = 15% ลากเส้นสัมผัสไป σ₂ = {its[1]*100:.1f}% แล้ว σ₃ = {its[2]*100:.2f}% เข้าหาราก σ* = 25%")
    title(out, Wd, "Newton-Raphson หา Implied Vol — ลากเส้นสัมผัส (ความชัน = Vega) ไปตัดศูนย์ ซ้ำจนเข้าเป้า",
          f"Call S = K = 100 · r = 5% · T = 1 ปี · ราคาตลาด {price:.3f} · σ₁ = 15% → σ₂ = {its[1]*100:.2f}% → σ₃ = {its[2]*100:.3f}% · เข้าเป้าใน 2 รอบ")
    sgs = np.linspace(0.05, 0.40, 141); fv = np.array([f(v) for v in sgs])
    (sx, sy), _ = _std_frame(out, Wd, H, [(0.05, "5%"), (0.10, "10%"), (0.15, "15%"), (0.20, "20%"), (0.25, "25%"), (0.30, "30%"), (0.35, "35%"), (0.40, "40%")], [(-8, "−8"), (-6, "−6"), (-4, "−4"), (-2, "−2"), (0, "0"), (2, "2"), (4, "4"), (6, "6")], "σ (เดา)", "f(σ) = BS(σ) − ราคาตลาด")
    _zero_line(out, sx, sy, 0.05, 0.40)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(sgs, fv)], BLUE, 2.4)
    s1, s2 = its[0], its[1]
    polyline(out, [(sx(s1), sy(f(s1))), (sx(s2), sy(0))], RED, 1.6, dash="5 3", shadow=False)
    out.append(f'<line x1="{sx(s2):.1f}" y1="{sy(0):.1f}" x2="{sx(s2):.1f}" y2="{sy(f(s2)):.1f}" stroke="{RED}" stroke-width="1" stroke-dasharray="2 2"/>')
    _dot(out, sx(s1), sy(f(s1)), RED); _txt(out, sx(s1), sy(f(s1)) + 16, f"σ₁ = 15% · f = {f(s1):.2f}".replace("-", "−"), RED, "middle", size=9, bold=True)
    _dot(out, sx(s2), sy(0), RED, 3.6); _txt(out, sx(s2) - 8, sy(0) - 10, f"σ₂ = {s2*100:.1f}% (ห่างรากแค่ {abs(s2-0.25)*100:.1f} จุด)", RED, "end", size=9, bold=True)
    _dot(out, sx(0.25), sy(0)); _txt(out, sx(0.25) + 6, sy(0) + 16, "σ* = IV = 25% (ราก)", PURPLE, "start", bold=True)
    _txt(out, sx(0.11), sy(2.6), "เส้นประ = เส้นสัมผัส ชัน Vega(σ₁)", RED, "start", size=9)
    _txt(out, sx(0.11), sy(2.6) + 12, "σ₂ = σ₁ − f(σ₁)/Vega(σ₁)", RED, "start", size=9)
    out.append("</svg>")
    NUMS["m6-newton"] = dict(price=price, s2=its[1], s3=its[2], s4=its[3])
    return "\n".join(out)


def random_walk_data(n=60, seed=5, paths=3):
    rng = np.random.default_rng(seed)
    steps = rng.choice([-1.0, 1.0], size=(paths, n))
    return np.concatenate([np.zeros((paths, 1)), np.cumsum(steps, axis=1)], axis=1)


@fig("math-part6.html", "m6-random-walk")
def fig_m6_random_walk():
    W_ = random_walk_data(); n = W_.shape[1] - 1
    Wd, H = 560, 324
    out = svg_open(Wd, H, "เส้นทางเดินสุ่มสามเส้นจากจุดเริ่มเดียวกัน ก้าวละ ±1 กระจายออกตามเวลาในกรวย ±√t และ ±2√t")
    title(out, Wd, "Random Walk — ก้าวละ ±1 สุ่ม: ทำนายทิศไม่ได้ แต่ทำนาย \"ความกว้าง\" ได้ = √t",
          f"3 เส้นทาง 60 ก้าว (สุ่มแบบตรึง seed) · กรวยเทา = ±√t (1σ) และ ±2√t · จบที่ {', '.join(f'{v:+.0f}' for v in W_[:, -1])} ทั้งที่เริ่มเท่ากัน")
    (sx, sy), _ = _std_frame(out, Wd, H, [(0, "0"), (10, "10"), (20, "20"), (30, "30"), (40, "40"), (50, "50"), (60, "60")], [(-20, "−20"), (-10, "−10"), (0, "S₀"), (10, "+10"), (20, "+20")], "เวลา (ก้าว)", "S − S₀")
    t = np.arange(n + 1)
    for k in (2, 1):
        pts = [(sx(a), sy(k * np.sqrt(a))) for a in t] + [(sx(a), sy(-k * np.sqrt(a))) for a in t[::-1]]
        out.append('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="{INK2}" opacity="{0.07 if k == 2 else 0.10}"/>')
    _zero_line(out, sx, sy, 0, n)
    for i, col in enumerate((BLUE, GREEN, RED)):
        polyline(out, [(sx(a), sy(b)) for a, b in zip(t, W_[i])], col, 2.0, shadow=False)
    legend(out, [(BLUE, f"เส้นทาง 1 (จบ {W_[0, -1]:+.0f})", ""), (GREEN, f"เส้นทาง 2 (จบ {W_[1, -1]:+.0f})", ""), (RED, f"เส้นทาง 3 (จบ {W_[2, -1]:+.0f})", "")], 55, H - 10)
    _txt(out, sx(40), sy(2 * np.sqrt(40)) - 6, "±2√t", INK2, "middle", size=9); _txt(out, sx(48), sy(np.sqrt(48)) + 12, "±√t", INK2, "middle", size=9)
    out.append("</svg>")
    NUMS["m6-random-walk"] = {f"end{i+1}": float(W_[i, -1]) for i in range(3)}
    return "\n".join(out)


def mc_paths_data(S0=100.0, K=100.0, r=0.05, sg=0.20, T=1.0, n=20, steps=120, seed=3):
    rng = np.random.default_rng(seed); dt = T / steps
    Z = rng.standard_normal((n, steps))
    logS = np.log(S0) + np.cumsum((r - sg * sg / 2) * dt + sg * np.sqrt(dt) * Z, axis=1)
    S = np.concatenate([np.full((n, 1), S0), np.exp(logS)], axis=1)
    pay = np.maximum(S[:, -1] - K, 0)
    return S, pay, float(np.exp(-r * T) * pay.mean()), float(bs_greeks(S0, K=K, r=r, sg=sg, T=T)["C"])


@fig("math-part7.html", "m7-mc-paths")
def fig_m7_mc_paths():
    S, pay, mc, bs = mc_paths_data(); n, steps = S.shape[0], S.shape[1] - 1
    n_itm = int((pay > 0).sum())
    Wd, H = 560, 320
    out = svg_open(Wd, H, f"เส้นทางราคาหุ้น GBM 20 เส้นจาก S₀ = 100 หนึ่งปี {n_itm} เส้นจบเหนือ K = 100 (ITM) ที่เหลือจบต่ำกว่าได้ payoff 0")
    title(out, Wd, "Monte Carlo — จำลองเส้นทางราคาหลายเส้น: จบเหนือ K ได้ S − K · จบต่ำกว่าได้ 0",
          f"GBM risk-neutral · S₀ = K = 100 · r = 5% · σ = 20% · T = 1 · ITM {n_itm} เส้น · เฉลี่ยคิดลด {mc:.2f} (BS {bs:.2f})")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1.0, "T = 1 ปี")], [(60, "60"), (80, "80"), (100, "100"), (120, "120"), (140, "140"), (160, "160")], "เวลา", "S")
    t = np.linspace(0, 1, steps + 1)
    out.append(f'<line x1="{x0}" y1="{sy(100):.1f}" x2="{x0+w}" y2="{sy(100):.1f}" stroke="{PURPLE}" stroke-width="1.4" stroke-dasharray="5 3"/>'); _txt(out, x0 + 4, sy(100) - 5, "K = 100", PURPLE, "start", size=9, bold=True)
    for i in range(n):
        col = GREEN if pay[i] > 0 else RED
        polyline(out, [(sx(a), sy(b)) for a, b in zip(t, S[i])], col, 1.2, shadow=False)
    _txt(out, sx(1.0) - 4, sy(150), f"จบเหนือ K → ITM ({n_itm} เส้น) payoff = S − K", GREEN, "end", size=9, bold=True)
    _txt(out, sx(1.0) - 4, sy(66), f"จบต่ำกว่า K → payoff 0 ({n - n_itm} เส้น)", RED, "end", size=9, bold=True)
    _txt(out, x0 + w, H - 8, "จำลองหมื่นเส้นทาง → เฉลี่ย payoff → คิดลดด้วย e⁻ʳᵀ = ราคา option", INK2, "end", size=9, italic=True)
    out.append("</svg>")
    NUMS["m7-mc-paths"] = dict(n_itm=n_itm, mc=mc, bs=bs)
    return "\n".join(out)


# ── คณิตศาสตร์เล่ม 2 · C (math-part8) — อ่านข้อมูลด้วยตา ──────────────────────────────────
def _panel(out, x0, y0, w, h, name, xt, yt, xlab="", ylab=""):
    _txt(out, x0 + w / 2, y0 - 6, name, INK, "middle", size=10, bold=True)
    return frame(out, x0, y0, w, h, xt, yt, xlab=xlab, ylab=ylab)


def _ols_line(x, y):
    b, a = np.polyfit(x, y, 1); return a, b


ANSCOMBE = dict(
    x123=[10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5],
    y1=[8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68],
    y2=[9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74],
    y3=[7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73],
    x4=[8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
    y4=[6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89])


def anscombe_stats():
    A = ANSCOMBE; sets = [(A["x123"], A["y1"]), (A["x123"], A["y2"]), (A["x123"], A["y3"]), (A["x4"], A["y4"])]
    rows = []
    for x, y in sets:
        x, y = np.array(x, float), np.array(y, float); a, b = _ols_line(x, y)
        rows.append(dict(xm=x.mean(), ym=y.mean(), b=b, a=a, r=float(np.corrcoef(x, y)[0, 1])))
    return sets, rows


@fig("math-part8.html", "m8-anscombe")
def fig_m8_anscombe():
    sets, rows = anscombe_stats()
    Wd, H = 560, 420
    out = svg_open(Wd, H, "Anscombe's quartet: กราฟ 4 ใบที่ค่าเฉลี่ย ความชัน และ correlation เท่ากัน แต่รูปร่างข้อมูลต่างกันสิ้นเชิง", multipanel=True)
    title(out, Wd, "Anscombe's quartet — สถิติเท่ากันทั้ง 4 ชุด แต่สิ่งที่ข้อมูลบอกคนละเรื่อง",
          f"ทุกชุด: x̄ = {rows[0]['xm']:.1f} · ȳ = {rows[0]['ym']:.2f} · เส้น OLS y = {rows[0]['a']:.2f} + {rows[0]['b']:.2f}x · ρ = {rows[0]['r']:.3f} — ดูตารางไม่พอ ต้องวาด")
    names = ["ชุดที่ 1 — ปกติดี", "ชุดที่ 2 — จริง ๆ เป็นเส้นโค้ง", "ชุดที่ 3 — จุดหลุด 1 จุดลากเส้น", "ชุดที่ 4 — x เท่ากันหมดยกเว้น 1"]
    notes = ["", "เส้นตรงจับรูปโค้งไม่ได้", "จุดเดียวคุมทั้งเส้น (leverage)", "จุดเดียวสร้างความชันทั้งหมด"]
    pw, ph = 215, 130
    for i, ((x, y), r_) in enumerate(zip(sets, rows)):
        cx = 60 + (i % 2) * 265; cy = 62 + (i // 2) * 175
        sx, sy = _panel(out, cx, cy, pw, ph, names[i], [(2, "2"), (6, "6"), (10, "10"), (14, "14"), (18, "18"), (20, "")], [(2, "2"), (6, "6"), (10, "10"), (14, "14")])
        polyline(out, [(sx(2), sy(r_["a"] + r_["b"] * 2)), (sx(20), sy(r_["a"] + r_["b"] * 20))], RED, 1.6, shadow=False)
        for a, b in zip(x, y):
            out.append(f'<circle cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="3.6" fill="{BLUE}" opacity="0.85"/>')
        if notes[i]: _txt(out, cx + 4, cy + 12, notes[i], RED, "start", size=9, italic=True)
        if i == 2: _txt(out, sx(13) + 6, sy(12.74) + 3, "outlier", RED, "start", size=9, bold=True)
    _txt(out, Wd / 2, H - 8, "สถิติเท่ากันทั้ง 4 ใบ · แต่สิ่งที่ข้อมูลบอก คนละเรื่องสิ้นเชิง — นี่คือเหตุที่ต้องพล็อตก่อนเชื่อตัวเลข", INK2, "middle", size=9.5, bold=True)
    out.append("</svg>")
    NUMS["m8-anscombe"] = dict(b=rows[0]["b"], r=rows[0]["r"], b3=rows[2]["b"], r4=rows[3]["r"])
    return "\n".join(out)


def corr_gallery_data(n=80, seed=21):
    rng = np.random.default_rng(seed); x = rng.normal(0, 1, n); x = (x - x.mean()) / x.std()
    def mk(rho):  # สร้าง y ให้ correlation ตัวอย่างเท่ากับ rho พอดี (ทำ e ให้ตั้งฉากกับ x ก่อน)
        e = rng.normal(0, 1, n); e = e - e.mean(); e = e - (e @ x) / (x @ x) * x; e = e / e.std()
        return rho * x + np.sqrt(1 - rho * rho) * e
    ys = [x.copy(), mk(0.7), mk(0.0), mk(-0.7), x * x - 1 + 0.3 * rng.normal(0, 1, n)]
    return x, ys, [float(np.corrcoef(x, y)[0, 1]) for y in ys]


@fig("math-part8.html", "m8-corr-gallery")
def fig_m8_corr_gallery():
    x, ys, rhos = corr_gallery_data()
    Wd, H = 560, 270
    out = svg_open(Wd, H, "แกลเลอรี scatter 5 ใบ: ρ = +1 ตรงกันเป๊ะ · +0.7 ไปด้วยกัน · 0 ไม่เกี่ยวกัน · −0.7 สวนทาง · รูปตัว U ที่ ρ ≈ 0 แต่สัมพันธ์ชัด", multipanel=True)
    title(out, Wd, "Correlation ρ แต่ละค่าหน้าตาเป็นอย่างไร — และกับดักตัว U ที่ ρ ≈ 0 แต่สัมพันธ์ชัด",
          f"จำลอง 80 จุดต่อใบ · ρ ที่วัดได้จริง: {rhos[0]:+.2f} · {rhos[1]:+.2f} · {rhos[2]:+.2f} · {rhos[3]:+.2f} · {rhos[4]:+.2f} (ตัว U) — ρ วัดได้แต่ความเป็นเส้นตรง")
    names = ["ρ = +1.0", "ρ = +0.7", "ρ = 0", "ρ = −0.7", "ρ ≈ 0 (!)"]; subs = ["ตรงกันเป๊ะ", "ไปด้วยกัน", "ไม่เกี่ยวกัน", "สวนทาง", "แต่สัมพันธ์ชัด!"]
    pw, ph = 88, 120
    for i, y in enumerate(ys):
        cx = 30 + i * 106; cy = 62
        out.append(f'<rect x="{cx}" y="{cy}" width="{pw}" height="{ph}" fill="none" stroke="{GRID}"/>')
        _txt(out, cx + pw / 2, cy - 6, names[i], INK if i < 4 else RED, "middle", size=10, bold=True)
        lo_x, hi_x = -3, 3; lo_y, hi_y = (-3, 3) if i < 4 else (-2, 8)
        for a, b in zip(x, y):
            px = cx + (a - lo_x) / (hi_x - lo_x) * pw; py = cy + ph - (b - lo_y) / (hi_y - lo_y) * ph
            if cx <= px <= cx + pw and cy <= py <= cy + ph: out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.4" fill="{BLUE if i < 4 else RED}" opacity="0.7"/>')
        _txt(out, cx + pw / 2, cy + ph + 14, subs[i], INK2 if i < 4 else RED, "middle", size=9, bold=i == 4)
    _txt(out, Wd / 2, H - 10, "ρ = 0 ไม่ได้แปลว่า \"ไม่เกี่ยวกัน\" — แปลว่า \"ไม่เกี่ยวกันแบบเส้นตรง\" เท่านั้น · ต้องพล็อตดูเสมอ", INK2, "middle", size=9.5, italic=True)
    out.append("</svg>")
    NUMS["m8-corr-gallery"] = {f"rho{i}": r for i, r in enumerate(rhos)}
    return "\n".join(out)


def residual_panels_data(n=60, seed=8):
    rng = np.random.default_rng(seed); x = np.linspace(0, 10, n)
    return x, [rng.normal(0, 1, n), 0.25 * (x - 5) ** 2 - 2 + rng.normal(0, 0.5, n), rng.normal(0, 1, n) * (0.2 + 0.25 * x), 1.8 * np.sin(x * 1.3) + rng.normal(0, 0.4, n)]


@fig("math-part8.html", "m8-residual-plots")
def fig_m8_residual_plots():
    x, res = residual_panels_data()
    Wd, H = 560, 400
    out = svg_open(Wd, H, "residual plot 4 แบบ: สุขภาพดีสุ่มไร้รูปแบบ · โค้ง (ไม่เป็นเส้นตรง) · กรวย (heteroskedasticity) · คลื่น (autocorrelation)", multipanel=True)
    title(out, Wd, "Residual plot — อ่าน \"ของที่โมเดลอธิบายไม่ได้\": มีแต่ใบแรกที่ผ่าน อีก 3 ใบคือสัญญาณว่ามีอะไรผิด",
          "แกนตั้ง = residual (จริง − ทำนาย) · แกนนอน = ค่าทำนายหรือลำดับเวลา · จำลอง 60 จุดต่อใบ")
    names = ["✅ สุขภาพดี — สุ่มไร้รูปแบบ", "❌ โค้ง — ความสัมพันธ์ไม่เป็นเส้นตรง", "❌ กรวย — heteroskedasticity", "❌ คลื่น — autocorrelation"]
    pw, ph = 215, 120
    for i, rr in enumerate(res):
        cx = 60 + (i % 2) * 265; cy = 62 + (i // 2) * 165
        sx, sy = _panel(out, cx, cy, pw, ph, names[i], [(0, "0"), (5, "5"), (10, "10")], [(-4, "−4"), (0, "0"), (4, "4")])
        out.append(f'<line x1="{sx(0):.1f}" y1="{sy(0):.1f}" x2="{sx(10):.1f}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.2"/>')
        col = GREEN if i == 0 else RED
        for a, b in zip(x, rr):
            if -4 <= b <= 4: out.append(f'<circle cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="2.8" fill="{col}" opacity="0.75"/>')
        if i == 2:
            polyline(out, [(sx(0), sy(2 * 0.2)), (sx(10), sy(2 * 2.7))], RED, 1, dash="4 3", shadow=False); polyline(out, [(sx(0), sy(-2 * 0.2)), (sx(10), sy(-2 * 2.7))], RED, 1, dash="4 3", shadow=False)
    _txt(out, Wd / 2, H - 8, "โค้ง → เพิ่มพจน์กำลังสอง/แปลงตัวแปร · กรวย → ใช้ log หรือ robust SE · คลื่น → มี autocorrelation ต้องใช้แบบจำลองอนุกรมเวลา", INK2, "middle", size=9)
    out.append("</svg>")
    return "\n".join(out)


HEAT = dict(names=["TECH-A", "TECH-B", "BANK", "GOLD", "BOND"],
            M=[[1.00, 0.86, 0.42, -0.05, -0.30], [0.86, 1.00, 0.38, -0.02, -0.26], [0.42, 0.38, 1.00, 0.10, -0.44], [-0.05, -0.02, 0.10, 1.00, 0.18], [-0.30, -0.26, -0.44, 0.18, 1.00]])


def _heat_color(v):
    # แดง (+1) ↔ ขาว (0) ↔ น้ำเงิน (−1)
    if v >= 0: r, g, b = 220, int(235 - 180 * v), int(235 - 200 * v)
    else: r, g, b = int(235 - 190 * -v), int(235 - 130 * -v), 235
    return f"rgb({r},{g},{b})"


@fig("math-part8.html", "m8-heatmap")
def fig_m8_heatmap():
    names, M = HEAT["names"], HEAT["M"]
    Wd, H = 560, 330
    out = svg_open(Wd, H, "correlation heatmap ของ 5 สินทรัพย์: TECH-A กับ TECH-B สัมพันธ์ 0.86 กลุ่มหุ้นสีแดง พันธบัตรสวนทางกับหุ้น −0.30 ถึง −0.44")
    title(out, Wd, "Correlation Heatmap — เห็นทั้งพอร์ตในภาพเดียว: กลุ่มแดงเข้มไปด้วยกัน · น้ำเงินสวนทาง",
          "ตัวอย่างพอร์ต 5 ตัว (10 คู่) · TECH-A/TECH-B 0.86 · BOND สวนทางหุ้น −0.26 ถึง −0.44 · GOLD แทบไม่เกี่ยวใคร")
    cell = 44; x0, y0 = 150, 70
    for i, nm in enumerate(names):
        _txt(out, x0 - 8, y0 + i * cell + cell / 2 + 3.5, nm, INK, "end", size=9.5, bold=True)
        _txt(out, x0 + i * cell + cell / 2, y0 - 8, nm, INK, "middle", size=9.5, bold=True)
        for j, v in enumerate(M[i]):
            out.append(f'<rect x="{x0 + j*cell}" y="{y0 + i*cell}" width="{cell}" height="{cell}" fill="{_heat_color(v)}" stroke="#fff" stroke-width="1.5"/>')
            _txt(out, x0 + j * cell + cell / 2, y0 + i * cell + cell / 2 + 3.5, f"{v:.2f}".replace("-", "−"), "#fff" if abs(v) > 0.6 else INK, "middle", size=9.5, bold=abs(v) > 0.6)
    # แถบสี
    bx, by = 400, 90
    for k in range(20):
        v = 1 - k / 9.5
        out.append(f'<rect x="{bx}" y="{by + k*8}" width="16" height="8" fill="{_heat_color(max(-1, min(1, v)))}"/>')
    _txt(out, bx + 22, by + 6, "+1 ไปด้วยกัน", INK2, "start", size=9); _txt(out, bx + 22, by + 84, "0 ไม่เกี่ยวกัน", INK2, "start", size=9); _txt(out, bx + 22, by + 162, "−1 สวนทาง", INK2, "start", size=9)
    _txt(out, x0, y0 + 5 * cell + 22, "กลุ่มสีแดงเข้ม = แทบเป็นตัวเดียวกัน (ถือทั้งคู่ไม่ได้กระจายความเสี่ยงเพิ่ม)", RED, "start", size=9, bold=True)
    _txt(out, x0, y0 + 5 * cell + 36, "สีน้ำเงิน = สวนทาง (ตัวช่วยพยุงพอร์ตเวลาหุ้นร่วง)", BLUE, "start", size=9, bold=True)
    out.append("</svg>")
    return "\n".join(out)


def hist_bins_data(n=3000, seed=4):
    rng = np.random.default_rng(seed); return rng.normal(0, 1, n)


@fig("math-part8.html", "m8-hist-bins")
def fig_m8_hist_bins():
    d = hist_bins_data()
    Wd, H = 560, 250
    out = svg_open(Wd, H, "histogram ข้อมูลชุดเดียวกัน 3,000 จุด ที่จำนวนแท่ง 6, 18 และ 45 ให้ภาพต่างกัน: หยาบไป พอดี ฟันหลอ", multipanel=True)
    title(out, Wd, "ข้อมูลชุดเดียวกัน 3 ภาพ — จำนวนแท่งเปลี่ยนข้อสรุปได้",
          "Normal(0, 1) จำลอง 3,000 จุด · 6 แท่งเห็นแค่ \"มียอดเดียว\" · 18 แท่งเห็นระฆังชัด · 45 แท่งฟันหลอ noise บังรูปทรง")
    names = ["6 แท่ง — หยาบไป", "18 แท่ง — พอดี", "45 แท่ง — ฟันหลอ"]; subs = ["เห็นแค่ \"มียอดเดียว\"", "เห็นรูประฆังชัด", "noise บังรูปทรง"]
    pw, ph = 150, 120
    for i, nb in enumerate((6, 18, 45)):
        cx = 30 + i * 178; cy = 62
        cnt, edges = np.histogram(d, bins=nb, range=(-4, 4)); dens = cnt / cnt.max()
        _txt(out, cx + pw / 2, cy - 6, names[i], INK if i == 1 else RED, "middle", size=10, bold=True)
        out.append(f'<line x1="{cx}" y1="{cy+ph}" x2="{cx+pw}" y2="{cy+ph}" stroke="{AXIS}"/>')
        for a, b, c in zip(edges[:-1], edges[1:], dens):
            px0 = cx + (a + 4) / 8 * pw; px1 = cx + (b + 4) / 8 * pw
            out.append(f'<rect x="{px0+0.5:.1f}" y="{cy + ph - c*ph:.1f}" width="{max(px1-px0-1, 0.8):.1f}" height="{c*ph:.1f}" fill="{BLUE if i == 1 else INK2}" opacity="0.7"/>')
        _txt(out, cx + pw / 2, cy + ph + 14, subs[i], INK2, "middle", size=9)
    _txt(out, Wd / 2, H - 10, "กฎหยาบ ๆ: จำนวนแท่ง ≈ √n หรือกฎ Freedman–Diaconis · ลองหลายค่าเสมอก่อนสรุปรูปทรง", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


def qq_data(n=300, seed=12):
    from scipy.stats import norm
    rng = np.random.default_rng(seed)
    samples = [rng.normal(0, 1, n), rng.standard_t(3, n) / np.sqrt(3), (np.exp(rng.normal(0, 0.6, n)) - np.exp(0.18))]
    p = (np.arange(1, n + 1) - 0.5) / n; theo = norm.ppf(p)
    outp = []
    for smp in samples:
        z = (smp - smp.mean()) / smp.std(ddof=1); outp.append(np.sort(z))
    return theo, outp


@fig("math-part8.html", "m8-qq")
def fig_m8_qq():
    theo, qs = qq_data()
    Wd, H = 560, 260
    out = svg_open(Wd, H, "QQ plot สามแบบ: Normal จุดเกาะเส้นตลอด · หางหนาปลายทั้งสองข้างงอออก · เบ้โค้งทั้งเส้นไม่สมมาตร", multipanel=True)
    title(out, Wd, "QQ plot — ถ้าข้อมูลเป็น Normal จริง จุดต้องเรียงบนเส้นตรง จุดที่หลุด = ตรงนั้นไม่เหมือน Normal",
          "จำลอง 300 จุดต่อใบ (ปรับให้ mean 0, SD 1) · แกนนอน = quantile ของ Normal ที่ควรเป็น · แกนตั้ง = quantile ของข้อมูลจริง")
    names = ["✅ Normal", "❌ หางหนา (fat tails)", "❌ เบ้ (skew)"]; subs = ["จุดเกาะเส้นตลอด", "ปลายทั้งสองข้างงอออกจากเส้น", "โค้งทั้งเส้น ไม่สมมาตร"]
    pw, ph = 150, 130
    for i, q in enumerate(qs):
        cx = 45 + i * 175; cy = 62
        sx, sy = _panel(out, cx, cy, pw, ph, names[i], [(-3, "−3"), (0, "0"), (3, "3")], [(-4, "−4"), (0, "0"), (4, "4")])
        polyline(out, [(sx(-3), sy(-3)), (sx(3), sy(3))], RED, 1.4, dash="5 3", shadow=False)
        for a, b in zip(theo, q):
            if -4 <= b <= 4: out.append(f'<circle cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="2" fill="{GREEN if i == 0 else BLUE}" opacity="0.7"/>')
        _txt(out, cx + pw / 2, cy + ph + 26, subs[i], INK2, "middle", size=9)
    _txt(out, Wd / 2, H - 6, "เส้นประแดง = ถ้าเป็น Normal เป๊ะ จุดต้องอยู่บนเส้นนี้", RED, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


def boxplot_data(n=120, seed=9):
    rng = np.random.default_rng(seed); d = np.concatenate([rng.normal(0, 1, n), [3.9, -3.4, 4.6]])
    q1, med, q3 = np.percentile(d, [25, 50, 75]); iqr = q3 - q1
    lo_w = d[d >= q1 - 1.5 * iqr].min(); hi_w = d[d <= q3 + 1.5 * iqr].max()
    outl = d[(d < q1 - 1.5 * iqr) | (d > q3 + 1.5 * iqr)]
    return d, q1, med, q3, iqr, lo_w, hi_w, outl


@fig("math-part8.html", "m8-boxplot")
def fig_m8_boxplot():
    d, q1, med, q3, iqr, lo_w, hi_w, outl = boxplot_data()
    Wd, H = 560, 250
    out = svg_open(Wd, H, f"กายวิภาคของ box plot: กล่อง Q1 {q1:.2f} ถึง Q3 {q3:.2f} เส้น median {med:.2f} หนวดถึง {lo_w:.2f} และ {hi_w:.2f} จุดเลยหนวด {len(outl)} จุด")
    title(out, Wd, "Box plot ย่อข้อมูลทั้งกองเหลือ 5 ตัวเลข — และจุดที่เลยหนวดไม่ได้แปลว่า \"ข้อมูลผิด\"",
          f"จำลอง {len(d)} จุด · Q1 = {q1:.2f} · median = {med:.2f} · Q3 = {q3:.2f} · IQR = {iqr:.2f} · หนวดยืดถึงค่าจริงไกลสุดในกฎ 1.5·IQR")
    x0, w, yc = 60, 440, 130; lo, hi = -5, 5
    def sx(v): return x0 + (v - lo) / (hi - lo) * w
    out.append(f'<line x1="{x0}" y1="{yc+50}" x2="{x0+w}" y2="{yc+50}" stroke="{AXIS}"/>')
    for v in range(-4, 5): _txt(out, sx(v), yc + 63, f"{v}".replace("-", "−"), INK2, "middle", size=9)
    out.append(f'<line x1="{sx(lo_w):.1f}" y1="{yc}" x2="{sx(q1):.1f}" y2="{yc}" stroke="{INK}" stroke-width="1.6"/><line x1="{sx(q3):.1f}" y1="{yc}" x2="{sx(hi_w):.1f}" y2="{yc}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<line x1="{sx(lo_w):.1f}" y1="{yc-10}" x2="{sx(lo_w):.1f}" y2="{yc+10}" stroke="{INK}" stroke-width="1.6"/><line x1="{sx(hi_w):.1f}" y1="{yc-10}" x2="{sx(hi_w):.1f}" y2="{yc+10}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<rect x="{sx(q1):.1f}" y="{yc-24}" width="{sx(q3)-sx(q1):.1f}" height="48" fill="{BLUE}" opacity="0.18" stroke="{BLUE}" stroke-width="1.8"/>')
    out.append(f'<line x1="{sx(med):.1f}" y1="{yc-24}" x2="{sx(med):.1f}" y2="{yc+24}" stroke="{PURPLE}" stroke-width="2.4"/>')
    for v in outl: out.append(f'<circle cx="{sx(v):.1f}" cy="{yc}" r="3.5" fill="#fff" stroke="{RED}" stroke-width="1.8"/>')
    _txt(out, sx(q1) - 2, yc - 32, f"Q1 (25%) = {q1:.2f}", BLUE, "end", size=9, bold=True); _txt(out, sx(q3) + 2, yc - 32, f"Q3 (75%) = {q3:.2f}", BLUE, "start", size=9, bold=True)
    _txt(out, sx(med), yc + 40, f"median = {med:.2f}", PURPLE, "middle", size=9, bold=True)
    _txt(out, sx(lo_w), yc - 16, f"หนวดล่าง {lo_w:.2f}", INK2, "middle", size=9); _txt(out, sx(hi_w), yc - 16, f"หนวดบน {hi_w:.2f}", INK2, "middle", size=9)
    _txt(out, sx((q1 + q3) / 2), yc + 6 + 24 + 24, "", INK2)
    _txt(out, sx(outl.max()), yc - 10, "\"outlier\"", RED, "middle", size=9, bold=True); _txt(out, sx(outl.min()), yc - 10, "\"outlier\"", RED, "middle", size=9, bold=True)
    _txt(out, x0, H - 26, f"IQR = ข้อมูลตรงกลาง 50% · หนวดยาวสุดถึง Q3 + 1.5×IQR = {q3 + 1.5*iqr:.2f} (กฎมาตรฐาน) · เลยจากนี้ถูกวาดเป็นจุด", INK2, "start", size=9)
    _txt(out, x0, H - 12, "แต่ \"จุด\" ไม่ได้แปลว่า \"ข้อมูลผิด\" — ในข้อมูลหางหนา จุดพวกนี้คือของจริงที่สำคัญที่สุด (ดูกับดักข้างล่าง)", RED, "start", size=9, bold=True)
    out.append("</svg>")
    NUMS["m8-boxplot"] = dict(q1=q1, med=med, q3=q3, iqr=iqr, n_out=len(outl))
    return "\n".join(out)


# ── คณิตศาสตร์เล่ม 2 · D (math-part9) — อนุกรมเวลา ─────────────────────────────────────
def series3_data(n=200, seed=6):
    rng = np.random.default_rng(seed); e = rng.normal(0, 1, n)
    return e, np.cumsum(e), 0.06 * np.arange(n) + e


@fig("math-part9.html", "m9-stationary")
def fig_m9_stationary():
    wn, rw, tr = series3_data(); n = len(wn); t = np.arange(n)
    Wd, H = 560, 330
    out = svg_open(Wd, H, "เทียบ 3 อนุกรม 200 จุด: white noise วนรอบศูนย์ (นิ่ง) · random walk ลอยไปไม่กลับ · trend มีทิศทางชัด (ไม่นิ่ง)", multipanel=True)
    title(out, Wd, "Stationary หรือไม่ — ใบบนวนรอบจุดยึด · สองใบล่างลอยไปไม่กลับ",
          f"จำลอง 200 จุดจากช็อกชุดเดียวกัน · white noise σ 1 · random walk = ผลรวมสะสมของช็อก (จบที่ {rw[-1]:+.1f}) · trend = 0.06t + ช็อก")
    panels = [(wn, "✅ White noise — นิ่ง (stationary)", GREEN, (-4, 4)), (rw, "❌ Random walk — ไม่นิ่ง (แบบราคาหุ้น)", RED, (min(-4, rw.min() - 1), max(4, rw.max() + 1))), (tr, "❌ Trend — ไม่นิ่ง (มีทิศทางชัด)", RED, (-4, 16))]
    for i, (y, name, col, (lo, hi)) in enumerate(panels):
        cx, cy, pw, ph = 55, 60 + i * 88, 483, 62
        _txt(out, cx, cy - 4, name, col, "start", size=10, bold=True)
        def sy(v, lo=lo, hi=hi, cy=cy, ph=ph): return cy + ph - (v - lo) / (hi - lo) * ph
        def sx(v, cx=cx, pw=pw): return cx + v / (n - 1) * pw
        out.append(f'<rect x="{cx}" y="{cy}" width="{pw}" height="{ph}" fill="none" stroke="{GRID}"/>')
        if lo < 0 < hi: out.append(f'<line x1="{cx}" y1="{sy(0):.1f}" x2="{cx+pw}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1" stroke-dasharray="3 3"/>')
        polyline(out, [(sx(a), sy(b)) for a, b in zip(t, y)], col, 1.4, shadow=False)
        if i == 0: _txt(out, cx + pw - 4, cy + ph - 4, "เส้นประ = จุดยึด (ค่าเฉลี่ย 0)", INK2, "end", size=9)
    out.append("</svg>")
    NUMS["m9-stationary"] = dict(rw_end=float(rw[-1]))
    return "\n".join(out)


def acf_data(phi=0.7, n=2000, seed=6, lags=7):
    rng = np.random.default_rng(seed); e = rng.normal(0, 1, n)
    ar = np.zeros(n)
    for t in range(1, n): ar[t] = phi * ar[t - 1] + e[t]
    rw = np.cumsum(e)
    def acf(x, k):
        xc = x - x.mean(); return float((xc[:-k] @ xc[k:]) / (xc @ xc))
    return [phi ** k for k in range(1, lags + 1)], [acf(ar, k) for k in range(1, lags + 1)], [acf(rw, k) for k in range(1, lags + 1)]


@fig("math-part9.html", "m9-acf")
def fig_m9_acf():
    theo, ar, rw = acf_data()
    Wd, H = 560, 270
    out = svg_open(Wd, H, "เทียบ ACF 7 lag: AR(1) φ = 0.7 ลดเร็วตาม 0.7 ยกกำลัง k เหลือ 0.08 ที่ lag 7 กับ random walk ที่ยังสูงกว่า 0.9 ทุก lag", multipanel=True)
    title(out, Wd, "ACF — ลายนิ้วมือของอนุกรม: AR(1) ลดเร็วแบบเรขาคณิต · random walk แทบไม่ลดเลย",
          f"AR(1) φ = 0.7: ทฤษฎี ACF(k) = 0.7ᵏ (lag 1 = 0.70 · lag 7 = {theo[-1]:.2f}) · จำลอง 2,000 จุด · random walk: lag 7 ยัง {rw[-1]:.2f}")
    names = ["AR(1) φ = 0.7 — นิ่ง", "Random walk — ไม่นิ่ง"]; subs = ["ลดเร็ว → มีจุดยึด", "แทบไม่ลดเลย"]
    for i, vals in enumerate((ar, rw)):
        cx, cy, pw, ph = 60 + i * 270, 62, 215, 130
        sx, sy = _panel(out, cx, cy, pw, ph, names[i], [(0.5, ""), (1, "1"), (3, "3"), (5, "5"), (7, "7"), (7.5, "")], [(0, "0"), (0.5, "0.5"), (1, "1.0"), (1.15, "")], xlab="lag (กี่วันก่อน)")
        for k, v in enumerate(vals, 1):
            out.append(f'<rect x="{sx(k-0.3):.1f}" y="{sy(v):.1f}" width="{sx(k+0.3)-sx(k-0.3):.1f}" height="{sy(0)-sy(v):.1f}" fill="{GREEN if i == 0 else RED}" opacity="0.75" rx="2"/>')
            _txt(out, sx(k), sy(v) - 4, f"{v:.2f}", INK2, "middle", size=8)
        if i == 0:
            polyline(out, [(sx(k), sy(v)) for k, v in enumerate(theo, 1)], INK2, 1.2, dash="3 3", shadow=False); _txt(out, sx(4), sy(0.62), "เส้นประ = 0.7ᵏ ทฤษฎี", INK2, "start", size=8.5)
        _txt(out, cx + pw / 2, cy + ph + 28, subs[i], GREEN if i == 0 else RED, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, H - 6, "ACF ที่ลดช้ามาก = สัญญาณว่าอนุกรมไม่นิ่ง → ต้อง difference ก่อนสร้างโมเดล", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    NUMS["m9-acf"] = dict(ar7=ar[-1], rw7=rw[-1], theo7=theo[-1])
    return "\n".join(out)


def pair_ab_data(seed=0, n=500):
    """คู่ A/B ของ §9.1 ตรงกับโค้ดในบท: A = 100 + random walk · B = 5 + 1.5A + N(0, 2) → β OLS = 1.5068"""
    rng = np.random.default_rng(seed)
    A_ = 100 + np.cumsum(rng.normal(0, 1, n)); B_ = 5.0 + 1.5 * A_ + rng.normal(0, 2, n)
    beta, alpha = np.polyfit(A_, B_, 1); spread = B_ - (alpha + beta * A_); z = (spread - spread.mean()) / spread.std(ddof=1)
    return A_, B_, float(beta), spread, z


@fig("math-part9.html", "m9-coint-pair")
def fig_m9_coint_pair():
    A_, B_, beta, spread, z = pair_ab_data(); n = len(A_); t = np.arange(n)
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"ราคาหุ้น A และ B 500 วันที่ต่างเดินสุ่ม แต่ B เกาะ A ไปตลอดด้วย β = {beta:.4f} (cointegrated)")
    title(out, Wd, "Cointegration — แต่ละเส้นเดินสุ่มทำนายไม่ได้ แต่เกาะกันไปตลอด",
          f"คู่ A/B ของ §9.1 (โค้ดในบท · 500 วัน) · B = 5 + 1.5A + noise · β OLS = {beta:.4f} · spread = B − (α + βA) มีจุดยึด")
    lo = min(A_.min(), B_.min()) - 5; hi = max(A_.max(), B_.max()) + 12
    step = 20 if hi - lo > 80 else 10
    yt = [(v, f"{v:g}") for v in np.arange(np.ceil(lo / step) * step, hi, step)]
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (100, "100"), (200, "200"), (300, "300"), (400, "400"), (500, "500")], yt, "วัน", "ราคา")
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, A_)], BLUE, 1.6, shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, B_)], RED, 1.6, dash="4 3", shadow=False)
    legend(out, [(BLUE, "หุ้น A", ""), (RED, "หุ้น B (เส้นประ)", "4 3")], x0, H - 10)
    _txt(out, x0 + w, H - 8, "ต่างเดินสุ่ม แต่ส่วนต่างถ่วงน้ำหนักมีจุดยึด", INK2, "end", size=9, italic=True)
    out.append("</svg>")
    NUMS["m9-coint-pair"] = dict(beta=beta)
    return "\n".join(out)


@fig("math-part9.html", "m9-zscore")
def fig_m9_zscore():
    A_, B_, beta, spread, z = pair_ab_data(); n = len(z); t = np.arange(n)
    n_hi = int((z > 2).sum()); n_lo = int((z < -2).sum())
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"z-score ของ spread 500 วัน วนรอบศูนย์ แตะ +2 {n_hi} วัน และ −2 {n_lo} วัน: เกิน +2 ขาย spread · ต่ำกว่า −2 ซื้อ spread · กลับศูนย์ปิดสถานะ")
    title(out, Wd, "z-score ของ spread — วนรอบศูนย์เสมอ แตะขอบ ±2 เมื่อไรคือโอกาส",
          f"z = (spread − ค่าเฉลี่ย) / SD · จากคู่ A/B ด้านบน · วันที่ z > +2: {n_hi} วัน · z < −2: {n_lo} วัน จาก 500 ({(n_hi+n_lo)/n*100:.1f}% ใกล้ 4.6% ของ Normal)")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (100, "100"), (200, "200"), (300, "300"), (400, "400"), (500, "500")], [(-4, "−4"), (-2, "−2"), (0, "0"), (2, "+2"), (4, "+4")], "วัน", "z-score")
    out.append(f'<rect x="{x0}" y="{sy(4):.1f}" width="{w}" height="{sy(2)-sy(4):.1f}" fill="{RED}" opacity="0.08"/><rect x="{x0}" y="{sy(-2):.1f}" width="{w}" height="{sy(-4)-sy(-2):.1f}" fill="{GREEN}" opacity="0.08"/>')
    for v, col in ((2, RED), (-2, GREEN)): out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{col}" stroke-width="1.2" stroke-dasharray="5 3"/>')
    _zero_line(out, sx, sy, 0, n - 1)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, z)], BLUE, 1.5, shadow=False)
    _txt(out, x0 + 4, sy(2) - 5, "z = +2 → ขาย spread (short B, long βA)", RED, "start", size=9, bold=True)
    _txt(out, x0 + 4, sy(-2) + 13, "z = −2 → ซื้อ spread (long B, short βA)", GREEN, "start", size=9, bold=True)
    _txt(out, x0 + w - 4, sy(3.3), "z กลับมา 0 (ค่าเฉลี่ย) → ปิดสถานะ", INK2, "end", size=9)
    out.append("</svg>")
    NUMS["m9-zscore"] = dict(n_hi=n_hi, n_lo=n_lo)
    return "\n".join(out)


# ── คณิตศาสตร์เล่ม 2 · E (math-part10) — ผลตอบแทน ความเสี่ยง ขนาดเดิมพัน ─────────────────────
@fig("math-part10.html", "m10-sml")
def fig_m10_sml():
    rf, prem = 0.02, 0.07; beta_f, ret_f = 1.5, 0.14; capm = rf + beta_f * prem; alpha = ret_f - capm
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"Security Market Line จาก r_f 2% ชันขึ้น 7% ต่อหนึ่ง β กองทุน β 1.5 ได้ 14% อยู่เหนือเส้นที่ {capm*100:.1f}% คือ alpha {alpha*100:+.1f}%")
    title(out, Wd, "Security Market Line — อยู่เหนือเส้น = เก่งจริง (alpha) · อยู่บนเส้น = แค่รับความเสี่ยงมากขึ้น",
          f"r_f = 2% · market premium 7% · CAPM: E[r] = 2% + β × 7% · กองทุน β = 1.5 ได้ 14% ทั้งที่ CAPM บอก {capm*100:.1f}% → alpha = {alpha*100:+.1f}%")
    (sx, sy), _ = _std_frame(out, Wd, H, [(0, "0"), (0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0")], [(0, "0"), (0.04, "4%"), (0.08, "8%"), (0.12, "12%"), (0.16, "16%"), (0.20, "20%")], "β →", "ผลตอบแทนคาดหวัง")
    polyline(out, [(sx(0), sy(rf)), (sx(2), sy(rf + 2 * prem))], BLUE, 2.4)
    for b in (0.5, 1.0, 1.5, 2.0): _dot(out, sx(b), sy(rf + b * prem), BLUE, 3)
    _dot(out, sx(0), sy(rf), INK2, 3.5); _txt(out, sx(0) + 8, sy(rf) + 4, "r_f = 2%", INK2, "start", size=9)
    _dot(out, sx(1.0), sy(rf + prem), INK2, 3.5); _txt(out, sx(1.0) + 8, sy(rf + prem) + 12, "ตลาด (β = 1): 9%", INK2, "start", size=9)
    out.append(f'<line x1="{sx(beta_f):.1f}" y1="{sy(capm):.1f}" x2="{sx(beta_f):.1f}" y2="{sy(ret_f):.1f}" stroke="{GREEN}" stroke-width="2" stroke-dasharray="3 2"/>')
    _dot(out, sx(beta_f), sy(ret_f), GREEN, 5); _txt(out, sx(beta_f) - 8, sy(ret_f) - 6, f"กองทุนนี้ β 1.5 ได้ 14%", GREEN, "end", size=9.5, bold=True)
    _txt(out, sx(beta_f) + 8, sy((capm + ret_f) / 2) + 3, f"alpha = {alpha*100:+.1f}%", GREEN, "start", size=9.5, bold=True)
    _txt(out, sx(beta_f) + 8, sy(capm) + 12, f"CAPM บอก {capm*100:.1f}%", BLUE, "start", size=9)
    _txt(out, sx(1.75), sy(0.185), "Security Market Line", BLUE, "middle", size=9.5, bold=True)
    out.append("</svg>")
    NUMS["m10-sml"] = dict(capm=capm, alpha=alpha)
    return "\n".join(out)


def kelly_data(p=0.55, b=1.0):
    f = np.linspace(0.0, 0.30, 301)
    g = p * np.log1p(b * f) + (1 - p) * np.log1p(-f)
    fstar = (p * (b + 1) - 1) / b
    # จุดตัดศูนย์ (f > 0)
    idx = np.where((g[:-1] > 0) & (g[1:] <= 0))[0][0]; f0 = f[idx] + (0 - g[idx]) * (f[idx + 1] - f[idx]) / (g[idx + 1] - g[idx])
    return f, g, fstar, float(f0), float(p * np.log1p(b * fstar) + (1 - p) * np.log1p(-fstar))


@fig("math-part10.html", "m10-kelly")
def fig_m10_kelly():
    f, g, fstar, f0, gmax = kelly_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"อัตราเติบโตต่องวดเทียบขนาดเดิมพัน เป็นรูประฆังคว่ำ สูงสุดที่ Kelly f* = 10% ตัดศูนย์ที่ {f0*100:.2f}% ราวสองเท่าของ Kelly แล้วติดลบ")
    title(out, Wd, "Kelly — เดิมพันมากขึ้นไม่ได้ดีขึ้นเสมอ: ยอดที่ f* = 10% · เกิน ~20% (2×Kelly) เติบโตติดลบทั้งที่ยังมี edge",
          f"ชนะ 55% จ่าย 1:1 · g(f) = 0.55·ln(1 + f) + 0.45·ln(1 − f) · ยอด {gmax*100:.3f}% ต่องวดที่ f = 10% · ตัดศูนย์ที่ {f0*100:.2f}%")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (0.05, "5%"), (0.10, "10%"), (0.15, "15%"), (0.20, "20%"), (0.25, "25%"), (0.30, "30%")], [(-0.02, "−2%"), (-0.01, "−1%"), (0, "0"), (0.01, "+1%")], "ขนาดเดิมพัน f (สัดส่วนของพอร์ต) →", "อัตราเติบโตต่องวด")
    out.append(f'<rect x="{sx(f0):.1f}" y="{y0}" width="{sx(0.30)-sx(f0):.1f}" height="{h}" fill="{RED}" opacity="0.08"/>')
    _zero_line(out, sx, sy, 0, 0.30)
    mask = g >= -0.02; polyline(out, [(sx(a), sy(b)) for a, b in zip(f[mask], g[mask])], BLUE, 2.6)
    for xv, col, lab, dy in ((0.05, GREEN, "half-Kelly 5%", -10), (fstar, PURPLE, "Kelly f* = 10% — โตเร็วที่สุด", -10), (f0, RED, f"{f0*100:.1f}% ≈ 2×Kelly: เติบโต = 0 (เท่าทุน)", 0)):
        gv = 0.55 * np.log1p(xv) + 0.45 * np.log1p(-xv)
        out.append(f'<line x1="{sx(xv):.1f}" y1="{sy(gv):.1f}" x2="{sx(xv):.1f}" y2="{sy(0):.1f}" stroke="{col}" stroke-width="1.2" stroke-dasharray="3 3"/>'); _dot(out, sx(xv), sy(gv), col)
    _txt(out, sx(0.05), sy(0) + 14, "half-Kelly 5%", GREEN, "middle", size=9, bold=True)
    _txt(out, sx(fstar) + 6, sy(gmax) - 8, "Kelly f* = 10% — โตเร็วที่สุด", PURPLE, "start", size=9.5, bold=True)
    _txt(out, sx(f0) + 6, sy(0) - 8, f"{f0*100:.1f}% ≈ 2×Kelly: เติบโต = 0 (เท่าทุน)", RED, "start", size=9, bold=True)
    _txt(out, sx(0.245), sy(-0.011), "เกินจากนี้ = เงินหดทุกงวด", RED, "middle", size=9.5, bold=True)
    _txt(out, sx(0.245), sy(-0.011) + 12, "ทั้งที่ยังชนะ 55% ทุกครั้ง", RED, "middle", size=9)
    _txt(out, x0 + 4, sy(-0.0165), "ฝั่งซ้ายของยอดลาดน้อย ฝั่งขวาชันมาก → ถ้าไม่แน่ใจ ให้พลาดไปทางน้อย", INK2, "start", size=9, italic=True)
    out.append("</svg>")
    NUMS["m10-kelly"] = dict(fstar=fstar, f0=f0, gmax=gmax)
    return "\n".join(out)


def drawdown_data():
    """ตรงกับโค้ด Python ในบท: seed 17 · 1000 วัน · r ~ N(0.0006, 0.013)"""
    rng = np.random.default_rng(17); r = rng.normal(0.0006, 0.013, 1000)
    equity = np.concatenate([[1.0], np.cumprod(1 + r)]); peak = np.maximum.accumulate(equity); dd = equity / peak - 1
    bottom = int(dd.argmin()); top = int(np.argmax(equity[:bottom + 1]))
    idx = np.where(equity[bottom:] >= equity[top])[0]; recov = int(idx[0]) if len(idx) else None
    sharpe = (r.mean() * 252 - 0.02) / (r.std() * np.sqrt(252))
    return equity, dd, top, bottom, recov, float(equity[-1] - 1), float(dd.min()), float(sharpe)


@fig("math-part10.html", "m10-drawdown")
def fig_m10_drawdown():
    equity, dd, top, bottom, recov, total, mdd, sharpe = drawdown_data(); n = len(equity); t = np.arange(n)
    Wd, H = 560, 380
    out = svg_open(Wd, H, f"กราฟเงินทุน 1000 วันจบที่ {total*100:+.0f}% พร้อมกราฟ underwater แสดง drawdown สูงสุด {mdd*100:.1f}% ยอดถึงก้น {bottom-top} วัน กลับเท่าทุนอีก {recov} วัน รวม {bottom-top+recov} วัน", multipanel=True)
    title(out, Wd, f"กลยุทธ์ที่ \"ดี\" ก็ยังเจ็บ — กำไรรวม {total*100:+.0f}% (Sharpe {sharpe:.2f}) แต่ระหว่างทางเงินหาย {mdd*100:.1f}% จากยอด",
          f"โค้ดในบท (seed 17 · 1000 วัน) · ยอด→ก้น {bottom-top} วัน · ก้น→เท่าทุน {recov} วัน · รวม {bottom-top+recov} วัน · ต้องกำไร {1/(1+mdd)-1:.0%}")
    # บน: equity
    x0, y0, w, h = 55, 55, 483, 150
    sx, sy = frame(out, x0, y0, w, h, [(0, "0"), (250, "250"), (500, "500"), (750, "750"), (1000, "1000")], [(0.8, "0.8"), (1.2, "1.2"), (1.6, "1.6"), (2.0, "2.0"), (2.4, "2.4")], ylab="เงินทุน (เริ่ม 1.0)")
    peak = np.maximum.accumulate(equity)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, peak)], INK2, 1, dash="3 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, equity)], BLUE, 1.6, shadow=False)
    out.append(f'<rect x="{sx(top):.1f}" y="{y0}" width="{sx(top + (bottom-top) + recov)-sx(top):.1f}" height="{h}" fill="{RED}" opacity="0.07"/>')
    _dot(out, sx(top), sy(equity[top]), INK2, 3.5); _txt(out, sx(top), sy(equity[top]) - 8, "ยอดเดิม", INK2, "middle", size=9)
    _dot(out, sx(bottom), sy(equity[bottom]), RED, 3.5); _txt(out, sx(bottom), sy(equity[bottom]) + 14, f"ก้นบึ้ง {mdd*100:.1f}%", RED, "middle", size=9, bold=True)
    _txt(out, sx(n - 1) - 4, sy(equity[-1]) - 8, f"จบที่ {total*100:+.0f}%", BLUE, "end", size=9.5, bold=True)
    _txt(out, sx(top + (bottom - top + recov) / 2), y0 + 12, f"เจ็บอยู่ {bottom-top+recov} วัน กว่าจะกลับเท่าทุน", RED, "middle", size=9, bold=True)
    # ล่าง: underwater
    y1, h1 = 240, 100
    sx2, sy2 = frame(out, x0, y1, w, h1, [(0, "0"), (250, "250"), (500, "500"), (750, "750"), (1000, "1000")], [(-0.4, "−40%"), (-0.2, "−20%"), (0, "0%")], xlab="วัน · Drawdown = ต่ำกว่ายอดสูงสุดที่เคยเห็นกี่ %", ylab="Drawdown")
    pts = " ".join(f"{sx2(a):.1f},{sy2(b):.1f}" for a, b in zip(t, dd))
    out.append(f'<polygon points="{sx2(0):.1f},{sy2(0):.1f} {pts} {sx2(n-1):.1f},{sy2(0):.1f}" fill="{RED}" opacity="0.25"/>')
    polyline(out, [(sx2(a), sy2(b)) for a, b in zip(t, dd)], RED, 1.2, shadow=False)
    _txt(out, sx2(bottom), sy2(mdd) - 4, f"{mdd*100:.1f}%", RED, "middle", size=9, bold=True)
    out.append("</svg>")
    NUMS["m10-drawdown"] = dict(total=total, mdd=mdd, sharpe=sharpe, top_to_bottom=bottom - top, recov=recov)
    return "\n".join(out)


# ── Arbitrage (arb-part1…6) · ตาของ Arbitrageur · เล่ม 2·F — กราฟตัวเลขที่เคยวาดมือ ──────────
def converge_data(pa=30000.0, pb=30500.0, n=60, k=0.09):
    """ราคาสองตลาดวิ่งเข้าหากันแบบเลขชี้กำลัง: กึ่งกลางคงที่ ช่องว่างหดด้วยอัตรา k ต่อหน่วยเวลา"""
    t = np.arange(n + 1); mid = (pa + pb) / 2; gap0 = pb - pa
    gap = gap0 * np.exp(-k * t)
    return t, mid - gap / 2, mid + gap / 2, gap


@fig("arb-part1.html", "a1-converge")
def fig_a1_converge():
    t, A, B, gap = converge_data(); n = len(t) - 1
    i90 = int(np.argmax(gap <= 0.1 * gap[0]))
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"ราคาตลาด A ไต่ขึ้นและตลาด B ไหลลงเข้าหากัน ช่องว่าง 500 บาทหดเหลือไม่ถึง 50 บาทภายใน {i90} หน่วยเวลา")
    title(out, Wd, "No-Arbitrage — พอมีคนไล่ซื้อที่ถูกและไล่ขายที่แพง ช่องว่างก็ปิดตัวเอง",
          f"ตลาด A ฿{A[0]:,.0f} · ตลาด B ฿{B[0]:,.0f} · ช่องว่าง ฿{gap[0]:,.0f} = arb · เหลือ ฿{gap[i90]:,.0f} ใน {i90} หน่วยเวลา")
    yt = [(v, f"{v:,.0f}") for v in (29900, 30100, 30300, 30500, 30700)]
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (15, "15"), (30, "30"), (45, "45"), (60, "60")], yt, "เวลา →", "ราคา (฿)")
    pts = " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(t, B)) + " " + " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(t[::-1], A[::-1]))
    out.append(f'<polygon points="{pts}" fill="{AMBER}" opacity="0.18"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, A)], GREEN, 2.5)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, B)], RED, 2.5)
    out.append(f'<line x1="{sx(0):.1f}" y1="{sy(A[0]):.1f}" x2="{sx(0):.1f}" y2="{sy(B[0]):.1f}" stroke="{AMBER}" stroke-width="2"/>')
    _txt(out, sx(2), sy((A[0] + B[0]) / 2) + 3.5, f"ช่องว่าง ฿{gap[0]:,.0f} = arb", AMBER, "start", bold=True)
    _txt(out, sx(1), sy(A[0]) + 14, f"ตลาด A ฿{A[0]:,.0f} — ถูกกว่า จึงมีคนไล่ซื้อ ↑", GREEN, "start", size=9, bold=True)
    _txt(out, sx(1), sy(B[0]) - 6, f"ตลาด B ฿{B[0]:,.0f} — แพงกว่า จึงมีคนไล่ขาย ↓", RED, "start", size=9, bold=True)
    _dot(out, sx(n), sy((A[-1] + B[-1]) / 2)); _txt(out, sx(n) - 4, sy((A[-1] + B[-1]) / 2) - 10, "converge → ไม่เหลือ arb", PURPLE, "end", bold=True)
    out.append("</svg>")
    NUMS["a1-converge"] = dict(gap0=float(gap[0]), gap_end=float(gap[-1]), t90=float(i90))
    return "\n".join(out)


def call_bounds_data(K=100.0, r=0.05, T=0.5, sg=0.20):
    S = np.linspace(0, 200, 401); disc = K * np.exp(-r * T)
    return S, S, np.maximum(S - disc, 0), bs_greeks(S[1:], K=K, r=r, sg=sg, T=T)["C"], disc


@fig("arb-part1.html", "a1-call-bounds")
def fig_a1_call_bounds():
    S, up, lo_, C, disc = call_bounds_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"โซนราคา Call ที่เป็นไปได้ อยู่ระหว่างเส้นล่าง max(0, S − {disc:.2f}) กับเส้นบน C = S · ราคาจริงจาก Black-Scholes อยู่ในโซนเสมอ")
    title(out, Wd, "Bounds — ราคา Call ต้องอยู่ในโซนนี้เสมอ ไม่ต้องรู้ σ ก็บอกได้",
          f"K = 100 · r = 5% · T = 0.5 ปี · PV(K) = 100·e⁻⁰·⁰²⁵ = {disc:.2f} · เพดาน C ≤ S · พื้น C ≥ max(0, S − PV(K)) · หลุดโซน = arb ที่พิสูจน์ได้")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (50, "50"), (100, "100 (K)"), (150, "150"), (200, "200")], [(0, "0"), (50, "50"), (100, "100"), (150, "150"), (200, "200")], "S (ราคาหุ้น)", "ราคา Call")
    pts = " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(S, up)) + " " + " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(S[::-1], lo_[::-1]))
    out.append(f'<polygon points="{pts}" fill="{GREEN}" opacity="0.14"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, up)], INK2, 1.8, dash="5 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S, lo_)], INK2, 1.8, dash="5 3", shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(S[1:], C)], BLUE, 2.5)
    _txt(out, sx(168), sy(180), "เพดาน C = S", INK2, "middle", size=9, bold=True)
    _txt(out, sx(198), sy(88), "พื้น C = S − PV(K)", INK2, "end", size=9, bold=True)
    _txt(out, sx(60), sy(120), "Valid Zone", GREEN, "start", size=11, bold=True)
    _txt(out, sx(60), sy(105), "ราคา Call ต้องอยู่ในโซนนี้", GREEN, "start", size=9.5, bold=True)
    _txt(out, sx(60), sy(90), "เหนือเพดานหรือใต้พื้น = arb", RED, "start", size=9.5, bold=True)
    _txt(out, sx(128), sy(24), f"เส้นทึบ = Black-Scholes ที่ σ = 20% · C(100) = {float(bs_greeks(100.0)['C']):.2f}", BLUE, "start", size=9)
    out.append("</svg>")
    NUMS["a1-call-bounds"] = dict(disc=disc)
    return "\n".join(out)


def convexity_data(S0=100.0, r=0.05, sg=0.20, T=0.5, ks=(90.0, 100.0, 110.0)):
    cs = [float(bs_greeks(S0, K=k, r=r, sg=sg, T=T)["C"]) for k in ks]
    chord = (cs[0] + cs[2]) / 2
    return ks, cs, chord, cs[0] - 2 * cs[1] + cs[2]


@fig("arb-part2a.html", "a2a-convexity")
def fig_a2a_convexity():
    ks, cs, chord, fly = convexity_data()
    Kg = np.linspace(80, 120, 161); Cg = bs_greeks(100.0, K=Kg, r=0.05, sg=0.20, T=0.5)["C"]
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"ราคา Call เทียบ strike เป็นเส้นโค้งคว่ำลงและโค้งขึ้น จุดกลางของคอร์ด {chord:.2f} อยู่เหนือราคาจริงที่ K = 100 ซึ่งเท่ากับ {cs[1]:.2f}")
    title(out, Wd, "Convexity ใน K — ราคาจริงที่ K กลาง ต้องอยู่ใต้จุดกึ่งกลางของคอร์ดเสมอ",
          f"S = 100 · r = 5% · σ = 20% · T = 0.5 · Butterfly = {cs[0]:.2f} − 2({cs[1]:.2f}) + {cs[2]:.2f} = {fly:.2f} ≥ 0 ✓")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(80, "80"), (90, "90 (K₁)"), (100, "100 (K₂)"), (110, "110 (K₃)"), (120, "120")], [(0, "0"), (5, "5"), (10, "10"), (15, "15"), (20, "20")], "Strike (K)", "ราคา Call")
    polyline(out, [(sx(a), sy(b)) for a, b in zip(Kg, Cg)], BLUE, 2.6)
    polyline(out, [(sx(ks[0]), sy(cs[0])), (sx(ks[2]), sy(cs[2]))], AMBER, 1.8, dash="5 3", shadow=False)
    out.append(f'<line x1="{sx(100):.1f}" y1="{sy(chord):.1f}" x2="{sx(100):.1f}" y2="{sy(cs[1]):.1f}" stroke="{GREEN}" stroke-width="2.4"/>')
    for k, c in zip(ks, cs):
        _dot(out, sx(k), sy(c), BLUE, 4)
        _txt(out, sx(k), sy(c) + (-9 if k != 100 else 16), f"C({k:g}) = {c:.2f}", BLUE, "middle", size=9, bold=True)
    _dot(out, sx(100), sy(chord), AMBER, 4)
    _txt(out, sx(100) + 8, sy(chord) - 4, f"จุดกึ่งกลางคอร์ด = {chord:.2f}", AMBER, "start", size=9, bold=True)
    _txt(out, sx(101), sy((chord + cs[1]) / 2) + 3.5, f"ห่าง {fly:.2f} = ราคา Butterfly", GREEN, "start", size=9, bold=True)
    _txt(out, sx(119), sy(18.5), "ถ้าราคาจริงโผล่เหนือคอร์ด → Butterfly ติดลบ = arb", RED, "end", size=9, bold=True)
    out.append("</svg>")
    NUMS["a2a-convexity"] = dict(c1=cs[0], c2=cs[1], c3=cs[2], chord=chord, fly=fly)
    return "\n".join(out)


def iv_rv_data(n=120, seed=13, base=0.24):
    rng = np.random.default_rng(seed)
    # RV เหวี่ยงแรง (วัดจากราคาจริง) · IV ปรับตัวช้ากว่าและมีส่วนเกินเฉลี่ยเป็นบวก แต่บางช่วง RV แซงได้
    shock = np.zeros(n); shock[46:56] = np.linspace(0, 0.11, 10); shock[56:70] = np.linspace(0.11, 0, 14)
    rv = base + 0.035 * np.sin(np.arange(n) / 9.0) + shock + rng.normal(0, 0.020, n)
    iv = base + 0.038 + 0.022 * np.sin(np.arange(n) / 14.0 + 1.0) + 0.45 * shock + rng.normal(0, 0.007, n)
    return rv, iv, float((iv - rv).mean()), float((iv > rv).mean())


@fig("arb-part3.html", "a3-iv-rv")
def fig_a3_iv_rv():
    rv, iv, gap, share = iv_rv_data(); n = len(rv); t = np.arange(n)
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"เส้น implied volatility อยู่เหนือ realized volatility เกือบตลอด {n} วัน ช่องว่างเฉลี่ย {gap*100:.1f} จุดเปอร์เซ็นต์")
    title(out, Wd, "IV เทียบ RV — ส่วนใหญ่ IV อยู่เหนือ RV ช่องว่างนั้นคือ edge ของคนขาย vol",
          f"จำลอง {n} วัน · IV เฉลี่ย {iv.mean()*100:.1f}% · RV {rv.mean()*100:.1f}% · ส่วนเกิน {gap*100:.1f} จุด · IV > RV {share*100:.0f}% ของวัน [Heuristic]")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (30, "30"), (60, "60"), (90, "90"), (120, "120")], [(0.10, "10%"), (0.20, "20%"), (0.30, "30%"), (0.40, "40%")], "วัน", "Volatility (ต่อปี)")
    for a, b in zip(range(n - 1), range(1, n)):  # ระบายทีละช่วง: เขียวเมื่อ IV เหนือ RV แดงเมื่อ RV แซง
        col = GREEN if (iv[a] + iv[b]) > (rv[a] + rv[b]) else RED
        out.append(f'<polygon points="{sx(a):.1f},{sy(rv[a]):.1f} {sx(a):.1f},{sy(iv[a]):.1f} {sx(b):.1f},{sy(iv[b]):.1f} {sx(b):.1f},{sy(rv[b]):.1f}" fill="{col}" opacity="0.22"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, rv)], BLUE, 2.0, shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, iv)], RED, 2.2, shadow=False)
    _txt(out, sx(4), sy(0.375), f"แถบเขียว = IV เหนือ RV (edge ของคนขาย vol · เฉลี่ยทั้งช่วง {gap*100:.1f} จุด)", GREEN, "start", size=9.5, bold=True)
    _txt(out, sx(4), sy(0.375) + 13, f"แถบแดง = RV แซง IV ({(1-share)*100:.0f}% ของวัน — ช่วงที่คนขาย vol เจ็บ)", RED, "start", size=9.5, bold=True)
    legend(out, [(RED, "IV — ที่ตลาดฝังไว้ในราคา option", ""), (BLUE, "RV — ที่วัดได้จริงจากราคาหุ้น", "")], x0, H - 10)
    out.append("</svg>")
    NUMS["a3-iv-rv"] = dict(gap=gap, share=share, iv_mean=float(iv.mean()), rv_mean=float(rv.mean()))
    return "\n".join(out)


def basis_data(S0=900.0, r=0.02, d=0.025, T=0.25, F_mkt=905.0, n=90, seed=2):
    """ตัวอย่าง SET50 ของ §15.4: ค่ายุติธรรม F = S·e^(r−d)T · ตลาดเสนอ 905 · basis หดเป็น 0 ที่หมดอายุ"""
    fair = S0 * np.exp((r - d) * T)
    rng = np.random.default_rng(seed); t = np.linspace(0, T, n + 1)
    S = S0 + np.cumsum(np.concatenate([[0.0], rng.normal(0, 1.1, n)]))
    prem = (F_mkt - S0) * (1 - t / T)  # ส่วนเกินเหนือ spot หดเป็นศูนย์เชิงเส้น
    return t, S, S + prem, fair, F_mkt - fair


@fig("arb-part4.html", "a4-basis")
def fig_a4_basis():
    t, S, F, fair, over = basis_data()
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"ราคา futures เริ่มที่ 905 สูงกว่า spot 900 แล้วหดเข้าหา spot จนเท่ากันที่วันหมดอายุ ค่ายุติธรรมอยู่ที่ {fair:.2f} จึงแพงเกินไป {over:.2f}")
    title(out, Wd, "Basis หดเป็นศูนย์ที่วันหมดอายุเสมอ — นั่นคือสิ่งที่ล็อกกำไรของ cash & carry",
          f"§15.4: spot 900 · r = 2% · d = 2.5% · T = 3 เดือน → ค่ายุติธรรม {fair:.2f} · ตลาดเสนอ 905 → แพงเกิน {over:.2f}")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "วันนี้"), (0.0625, ""), (0.125, "1.5 เดือน"), (0.1875, ""), (0.25, "หมดอายุ")], [(885, "885"), (895, "895"), (905, "905"), (915, "915")], "เวลา →", "ราคา")
    pts = " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(t, F)) + " " + " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(t[::-1], S[::-1]))
    out.append(f'<polygon points="{pts}" fill="{AMBER}" opacity="0.22"/>')
    out.append(f'<line x1="{x0}" y1="{sy(fair):.1f}" x2="{x0+w}" y2="{sy(fair):.1f}" stroke="{PURPLE}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, S)], BLUE, 2.2, shadow=False)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, F)], RED, 2.4, shadow=False)
    _txt(out, sx(0.004), sy(913), f"basis = F − S = {905-900:.0f} วันนี้", AMBER, "start", size=9, bold=True)
    _txt(out, sx(0.246), sy(889), f"เส้นประ = ค่ายุติธรรม {fair:.2f} · ตลาดเสนอ 905 จึงแพงเกิน {over:.2f}", PURPLE, "end", size=9, bold=True)
    _dot(out, sx(0.25), sy(F[-1])); _txt(out, sx(0.246), sy(913), "converge → basis = 0 ที่หมดอายุ", PURPLE, "end", size=9, bold=True)
    legend(out, [(BLUE, "Spot", ""), (RED, "Futures", "")], x0, H - 10)
    out.append("</svg>")
    NUMS["a4-basis"] = dict(fair=float(fair), over=float(over))
    return "\n".join(out)


FX = dict(usd_eur=0.92, eur_gbp=0.86, gbp_usd=1.28, start=1000.0)


def triangular_data(start=None, **rates):
    r = dict(FX); r.update(rates); start = FX["start"] if start is None else start
    a = start * r["usd_eur"]; b = a * r["eur_gbp"]; c = b * r["gbp_usd"]
    return a, b, c, c - start, r["usd_eur"] * r["eur_gbp"] * r["gbp_usd"]


@fig("arb-part4.html", "a4-triangular")
def fig_a4_triangular():
    eur, gbp, back, profit, loop = triangular_data()
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"วงสามเหลี่ยมค่าเงิน: 1,000 ดอลลาร์แลกเป็น {eur:,.0f} ยูโร แล้วเป็น {gbp:,.2f} ปอนด์ แล้วกลับเป็น {back:,.2f} ดอลลาร์ กำไร {profit:.2f} ดอลลาร์ต่อรอบ")
    title(out, Wd, f"Triangular Arbitrage — เดินครบวงแล้วได้เงินกลับมามากกว่าเดิม ${profit:.2f}",
          f"ผลคูณรอบวง {FX['usd_eur']} × {FX['eur_gbp']} × {FX['gbp_usd']} = {loop:.5f} ≠ 1 · ส่วนเกิน {(loop-1)*100:.3f}% ต่อรอบ ไม่ขึ้นกับว่าเริ่มด้วยเงินเท่าไร")
    nodes = [("USD", 280, 70, f"${FX['start']:,.0f}"), ("EUR", 120, 215, f"€{eur:,.0f}"), ("GBP", 440, 215, f"£{gbp:,.2f}")]
    for nm, cx, cy, amt in nodes:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="40" fill="{BLUE}" opacity="0.12" stroke="{BLUE}" stroke-width="2"/>')
        _txt(out, cx, cy - 4, nm, INK, "middle", size=13, bold=True); _txt(out, cx, cy + 13, amt, BLUE, "middle", size=11, bold=True)
    arrows = [((280, 70), (120, 215), f"×{FX['usd_eur']}", -30, 4), ((120, 215), (440, 215), f"×{FX['eur_gbp']}", 0, 22), ((440, 215), (280, 70), f"×{FX['gbp_usd']}", 30, 4)]
    for (ax, ay), (bx, by), lab, dx, dy in arrows:
        ux, uy = bx - ax, by - ay; L = (ux * ux + uy * uy) ** 0.5; ux, uy = ux / L, uy / L
        x1, y1 = ax + ux * 42, ay + uy * 42; x2, y2 = bx - ux * 46, by - uy * 46
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{AMBER}" stroke-width="2.4" marker-end="url(#arrA)"/>')
        _txt(out, (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, lab, AMBER, "middle", size=11, bold=True)
    _txt(out, 280, 268, f"${FX['start']:,.0f} → €{eur:,.0f} → £{gbp:,.2f} → ${back:,.2f}  =  กำไร ${profit:.2f} ต่อรอบ ({(loop-1)*100:.3f}%)", GREEN, "middle", size=10.5, bold=True)
    _txt(out, 280, 285, "ถ้าผลคูณรอบวง = 1 พอดี ก็ไม่มี arb · อ่านทิศอัตราผิดทางเดียว \"กำไร\" กลายเป็นขาดทุน", INK2, "middle", size=9, italic=True)
    out.append('<defs><marker id="arrA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#d97706"/></marker></defs>')
    out.append("</svg>")
    NUMS["a4-triangular"] = dict(eur=eur, gbp=gbp, back=back, profit=profit, loop=loop)
    return "\n".join(out)


def ou_z_data(n=260, theta=0.06, seed=4):
    rng = np.random.default_rng(seed); x = np.zeros(n)
    for t in range(1, n): x[t] = (1 - theta) * x[t - 1] + rng.normal(0, 1)
    return (x - x.mean()) / x.std(ddof=1)


@fig("arb-part5.html", "a5-zscore")
def fig_a5_zscore():
    z = ou_z_data(); n = len(z); t = np.arange(n)
    # หาไม้แรก: ข้าม +2 → ปิดที่ 0 · ข้าม −2 → ปิดที่ 0
    trades = []
    i = 1
    while i < n and len(trades) < 2:
        if abs(z[i]) >= 2 and abs(z[i - 1]) < 2:
            side = "short" if z[i] > 0 else "long"
            j = i
            while j < n and (z[j] > 0) == (z[i] > 0) and abs(z[j]) > 0.05: j += 1
            if j < n: trades.append((i, j, side)); i = j
        i += 1
    Wd, H = 560, 310
    out = svg_open(Wd, H, f"z-score ของ spread วนรอบศูนย์ แตะ +2 แล้วเปิด short และแตะ −2 แล้วเปิด long ปิดสถานะเมื่อกลับมาที่ศูนย์")
    title(out, Wd, "z-score ของ spread — แตะ +2 ขาย · แตะ −2 ซื้อ · กลับมา 0 ปิดไม้",
          f"จำลอง OU {n} วัน (θ = 0.06) · z = (spread − ค่าเฉลี่ย) / SD · วันที่ |z| ≥ 2 มี {int((abs(z)>=2).sum())} วันจาก {n} ({(abs(z)>=2).mean()*100:.1f}% ใกล้ 4.6% ของ Normal)")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (50, "50"), (100, "100"), (150, "150"), (200, "200"), (250, "250")], [(-4, "−4"), (-2, "−2"), (0, "0"), (2, "+2"), (4, "+4")], "วัน", "Z")
    out.append(f'<rect x="{x0}" y="{sy(4):.1f}" width="{w}" height="{sy(2)-sy(4):.1f}" fill="{RED}" opacity="0.08"/><rect x="{x0}" y="{sy(-2):.1f}" width="{w}" height="{sy(-4)-sy(-2):.1f}" fill="{GREEN}" opacity="0.08"/>')
    for v, col in ((2, RED), (-2, GREEN)): out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{col}" stroke-width="1.2" stroke-dasharray="5 3"/>')
    _zero_line(out, sx, sy, 0, n - 1)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, z)], BLUE, 1.6, shadow=False)
    for i, j, side in trades:
        col = RED if side == "short" else GREEN
        _dot(out, sx(i), sy(z[i]), col, 4.4); _dot(out, sx(j), sy(z[j]), PURPLE, 4)
        _txt(out, sx(i), sy(z[i]) + (-9 if side == "short" else 16), "Short!" if side == "short" else "Long!", col, "middle", size=9.5, bold=True)
        _txt(out, sx(j) + 5, sy(z[j]) - 7, "Exit", PURPLE, "start", size=9, bold=True)
    _txt(out, x0 + w - 4, sy(2) - 5, "+2σ → ขาย spread", RED, "end", size=9, bold=True)
    _txt(out, x0 + w - 4, sy(-2) + 13, "−2σ → ซื้อ spread", GREEN, "end", size=9, bold=True)
    out.append("</svg>")
    NUMS["a5-zscore"] = dict(n_extreme=int((abs(z) >= 2).sum()))
    return "\n".join(out)


def merger_data(pre=42.0, deal=50.0, start=47.50, fail=35.0, n=90):
    t = np.arange(n + 1)
    p = np.where(t < 10, pre, start + (deal - start) * np.clip((t - 10) / (n - 10), 0, 1) ** 1.6)
    return t, p, deal - start, (deal - start) / deal * 100, (start - fail) / start * 100


@fig("arb-part6.html", "a6-merger-spread")
def fig_a6_merger_spread():
    t, p, spread, pct, downside = merger_data(); n = len(t) - 1
    Wd, H = 560, 320
    out = svg_open(Wd, H, f"ราคาหุ้นเป้าหมายกระโดดจาก 42 เป็น 47.50 วันประกาศดีล แล้วไต่เข้าหาราคาดีล 50 บาท ส่วนต่าง 2.50 บาทค่อย ๆ แคบลงจนปิดดีล")
    title(out, Wd, "Merger Arbitrage — ส่วนต่างจากราคาดีลคือค่าจ้างของการแบกความเสี่ยงว่าดีลจะล่ม",
          f"ประกาศซื้อที่ ฿50 · ราคาเด้ง ฿42 → ฿47.50 · เหลือส่วนต่าง ฿{spread:.2f} = {pct:.0f}% · ดีลล่มกลับไป ฿35 = −{downside:.1f}%")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "ก่อนประกาศ"), (10, "ประกาศ"), (35, "Regulatory"), (60, "โหวต"), (90, "ปิดดีล")], [(34, "34"), (38, "38"), (42, "42"), (46, "46"), (50, "50")], "เวลา →", "ราคาหุ้น B (฿)")
    out.append(f'<line x1="{x0}" y1="{sy(50):.1f}" x2="{x0+w}" y2="{sy(50):.1f}" stroke="{PURPLE}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    _txt(out, x0 + 4, sy(50) - 5, "ราคาดีล ฿50", PURPLE, "start", size=9, bold=True)
    pts = " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(t[10:], p[10:])) + f" {sx(n):.1f},{sy(50):.1f} {sx(10):.1f},{sy(50):.1f}"
    out.append(f'<polygon points="{pts}" fill="{AMBER}" opacity="0.22"/>')
    polyline(out, [(sx(a), sy(b)) for a, b in zip(t, p)], BLUE, 2.5, shadow=False)
    polyline(out, [(sx(12), sy(47.5)), (sx(38), sy(35))], RED, 1.8, dash="5 3", shadow=False)
    _txt(out, sx(40), sy(35.4), "ถ้าดีลล่ม → ฿35 (เสีย ฿12.50)", RED, "start", size=9, bold=True)
    _dot(out, sx(10), sy(47.5)); _txt(out, sx(12), sy(46.2), "ประกาศดีล: ฿42 → ฿47.50", PURPLE, "start", size=9, bold=True)
    _txt(out, sx(88), sy(48.4), f"ส่วนต่าง ฿{spread:.2f} ค่อย ๆ แคบลง", AMBER, "end", size=9, bold=True)
    for xv, lab in ((35, "Regulatory review"), (60, "Shareholder vote")):
        out.append(f'<line x1="{sx(xv):.1f}" y1="{y0}" x2="{sx(xv):.1f}" y2="{y0+h}" stroke="{GRID}" stroke-width="1" stroke-dasharray="3 3"/>')
        _txt(out, sx(xv), sy(41.2), lab, INK2, "middle", size=9)
    _txt(out, x0 + w, H - 8, "เสีย ฿12.50 เพื่อได้ ฿2.50 → ต้องมั่นใจเกิน 83.3% ว่าดีลจะปิด", INK2, "end", size=9, italic=True)
    out.append("</svg>")
    NUMS["a6-merger-spread"] = dict(spread=spread, pct=pct, downside=downside)
    return "\n".join(out)


@fig("eye-part2.html", "e2-five-markets")
def fig_e2_five_markets():
    X = 2500.0
    Wd, H = 560, 330
    out = svg_open(Wd, H, "เทียบสองรูปแบบของ 'จ่ายถ้าเกิน X' ที่ชื่อต่างกันห้าตลาด: จ่ายคงที่แบบดิจิทัล กับจ่ายตามส่วนเกินแบบเส้นตรง", multipanel=True)
    title(out, Wd, "\"จ่ายถ้าเกิน X\" — ห้าตลาดเรียกคนละชื่อ แต่โครงเดียวกัน ต่างแค่ \"จ่ายเท่าไร\"",
          f"X = {X:,.0f} · เงื่อนไขจ่ายเหมือนกัน (S > X) · ซ้าย = จ่ายก้อนคงที่ · ขวา = จ่ายตามส่วนเกิน")
    S = np.linspace(2000, 3000, 401)
    panels = [("จ่ายคงที่ (ดิจิทัล)", np.where(S > X, 1.0, 0.0), (0, 1.35), ["PM Above Yes", "Betting \"Over X\"", "ประกันแบบจ่ายก้อน"], PURPLE),
              ("จ่ายตามส่วนเกิน (เชิงเส้น)", np.maximum(S - X, 0) / 500, (0, 1.35), ["Call(X)", "Call on DEX", "ประกันตามความเสียหาย"], BLUE)]
    for i, (nm, y, (ylo, yhi), names, col) in enumerate(panels):
        cx, cy, pw, ph = 55 + i * 265, 70, 215, 130
        _txt(out, cx + pw / 2, cy - 8, nm, INK, "middle", size=11, bold=True)
        sx, sy = frame(out, cx, cy, pw, ph, [(2000, "2,000"), (2500, "X"), (3000, "3,000")], [(0, "0"), (1, "จ่ายเต็ม")], xlab="ราคา S", ylab="payoff", grid_y=False)
        out.append(f'<line x1="{sx(X):.1f}" y1="{cy}" x2="{sx(X):.1f}" y2="{cy+ph}" stroke="{GRID}" stroke-width="1" stroke-dasharray="3 3"/>')
        pts = " ".join(f"{sx(a):.1f},{sy(min(b, yhi)):.1f}" for a, b in zip(S, y))
        out.append(f'<polygon points="{sx(S[0]):.1f},{sy(0):.1f} {pts} {sx(S[-1]):.1f},{sy(0):.1f}" fill="{col}" opacity="0.13"/>')
        polyline(out, [(sx(a), sy(min(b, yhi))) for a, b in zip(S, y)], col, 2.6)
        for j, nmm in enumerate(names):
            _txt(out, cx, cy + ph + 30 + j * 15, f"• {nmm}", col, "start", size=9.5, bold=True)
    _txt(out, Wd / 2, H - 10, "เงื่อนไขเหมือนกัน แต่คนละรูปจ่าย — เอาราคามาเทียบกันตรง ๆ คือเทียบคนละของ", RED, "middle", size=9.5, bold=True)
    out.append("</svg>")
    return "\n".join(out)


def indicator_breakeven_data(cost=0.00436):
    """เส้นกำไรต่อไม้ = k·σ โดย k มาจากจุดตัดต้นทุนที่บทวัดไว้ · จุดวัดจริงจากตาราง §13.4"""
    cross = {"RSI(14) 30→50": 0.0015, "Bollinger −2SD": 0.0033, "Stochastic %K 20→50": 0.0074}
    ks = {k: cost / v for k, v in cross.items()}
    meas = {"RSI(14) 30→50": [(0.001, 0.002864), (0.003, 0.008673), (0.012, 0.036056)],
            "Stochastic %K 20→50": [(0.001, 0.000583), (0.003, 0.001769), (0.012, 0.007321)]}
    return cost, cross, ks, meas


@fig("math-part11.html", "m11-indicator-breakeven")
def fig_m11_indicator_breakeven():
    cost, cross, ks, meas = indicator_breakeven_data()
    Wd, H = 560, 334
    out = svg_open(Wd, H, "เส้นตรงสามเส้นของกำไรต่อไม้ก่อนหักต้นทุนที่โตตามความผันผวนรายวัน ตัดเส้นต้นทุน 0.436% ที่ σ 0.15% 0.33% และ 0.74% ตามลำดับ")
    title(out, Wd, "เส้นเอียงชนเส้นแบน — กำไรต่อไม้โตตาม σ แต่ต้นทุนไม่สนใจว่าตลาดเหวี่ยงหรือนิ่ง",
          f"ต้นทุนไป-กลับหุ้น SET50 = {cost*100:.3f}% · แต่ละเครื่องมือมีจุดตัดของตัวเอง: RSI {cross['RSI(14) 30→50']*100:.2f}% · Bollinger {cross['Bollinger −2SD']*100:.2f}% · %K {cross['Stochastic %K 20→50']*100:.2f}%")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(0, "0"), (0.002, "0.2%"), (0.004, "0.4%"), (0.006, "0.6%"), (0.008, "0.8%"), (0.010, "1.0%")], [(0, "0"), (0.01, "1.0%"), (0.02, "2.0%"), (0.03, "3.0%")], "σ ต่อวัน (ความผันผวนของตลาด) →", "กำไรต่อไม้ ก่อนหักต้นทุน")
    out.append(f'<rect x="{x0}" y="{sy(cost):.1f}" width="{w}" height="{sy(0)-sy(cost):.1f}" fill="{RED}" opacity="0.10"/>')
    out.append(f'<line x1="{x0}" y1="{sy(cost):.1f}" x2="{x0+w}" y2="{sy(cost):.1f}" stroke="{RED}" stroke-width="2"/>')
    _txt(out, x0 + w - 6, sy(cost * 0.42), "โซนแดง = ขาดทุนแน่นอน", RED, "end", size=9, bold=True)
    cols = {"RSI(14) 30→50": GREEN, "Bollinger −2SD": BLUE, "Stochastic %K 20→50": AMBER}
    dash = {"RSI(14) 30→50": "", "Bollinger −2SD": "6 3", "Stochastic %K 20→50": "2 3"}
    for nm, k in ks.items():
        xmax = min(0.010, 0.032 / k)
        polyline(out, [(sx(0), sy(0)), (sx(xmax), sy(k * xmax))], cols[nm], 2.2, dash=dash[nm], shadow=not dash[nm])
        xv = cross[nm]; _dot(out, sx(xv), sy(cost), cols[nm], 4)
        _txt(out, sx(xv), sy(cost) + 15, f"{xv*100:.2f}%", cols[nm], "middle", size=9, bold=True)
        for mx, my in meas.get(nm, []):
            if mx <= xmax: out.append(f'<circle cx="{sx(mx):.1f}" cy="{sy(my):.1f}" r="3" fill="#fff" stroke="{cols[nm]}" stroke-width="1.8"/>')
    _txt(out, sx(0.0078), sy(0.0262), "RSI — เก็บได้มากต่อไม้", GREEN, "end", size=9, bold=True)
    _txt(out, x0 + 4, y0 + 12, "เส้นแดงแนวนอน = ต้นทุนไป-กลับ 0.436% — ไม่ขึ้นกับ σ", RED, "start", size=9, bold=True)
    _txt(out, x0 + 4, y0 + 26, "วงกลมกลวง = ค่าที่วัดได้จริงจากตาราง §13.4", INK2, "start", size=9, italic=True)
    _txt(out, x0 + 4, y0 + 38, "ทุกเส้นผ่านจุดกำเนิด — กำไรต่อไม้แปรตาม σ", INK2, "start", size=9, italic=True)
    legend(out, [(GREEN, "RSI(14) 30→50", ""), (BLUE, "Bollinger −2SD", "6 3"), (AMBER, "Stochastic %K 20→50 (ถี่กว่า 10 เท่า)", "2 3")], x0, H - 10)
    out.append("</svg>")
    NUMS["m11-indicator-breakeven"] = dict(cost=cost, **{f"cross_{i}": v for i, v in enumerate(cross.values())})
    return "\n".join(out)


def ridge_path_data(seed=5, n=250):
    """ข้อมูลชุดเดียวกับโค้ดในบท §14.3: val เกือบเป็นตัวเดียวกับ mkt (VIF 113) · β จริง = [0.8, 0.4, 0.3]"""
    rng = np.random.default_rng(seed)
    mkt = rng.normal(0, 1, n); val = mkt + rng.normal(0, 0.10, n); size = rng.normal(0, 1, n)
    X = np.column_stack([mkt, val, size]); beta_true = np.array([0.8, 0.4, 0.3])
    y = X @ beta_true + rng.normal(0, 1.0, n)
    Xc = X - X.mean(0); yc = y - y.mean()
    alphas = np.logspace(-2, 2, 200)
    paths = np.array([np.linalg.solve(Xc.T @ Xc + a * np.eye(3), Xc.T @ yc) for a in alphas])
    ols = np.linalg.solve(Xc.T @ Xc, Xc.T @ yc)
    return alphas, paths, ols, beta_true


@fig("math-part11.html", "m11-ridge-path")
def fig_m11_ridge_path():
    alphas, paths, ols, bt = ridge_path_data()
    r10 = paths[np.argmin(abs(alphas - 10))]
    Wd, H = 560, 320
    out = svg_open(Wd, H, f"เส้นทางสัมประสิทธิ์ของ Ridge เมื่อ alpha เพิ่มขึ้น: market เริ่มที่ติดลบ {ols[0]:.2f} แล้วไต่ขึ้น value เริ่มสูง {ols[1]:.2f} แล้วลดลง ทั้งคู่มาบรรจบกันราว 0.6 ส่วน size คงที่")
    title(out, Wd, "Ridge Path — ยิ่งเพิ่มค่าปรับ α สองตัวที่ซ้ำกันยิ่งเลิกแย่งกัน แล้วเดินเข้าหาคำตอบจริง",
          f"§14.3 (val ≈ mkt · VIF 113) · OLS ให้ {ols[0]:.2f} / {ols[1]:.2f} — เพี้ยน · α = 10 ได้ {r10[0]:.2f} / {r10[1]:.2f} / {r10[2]:.2f} · จริง 0.8 / 0.4 / 0.3")
    (sx0, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(-2, "0.01"), (-1, "0.1"), (0, "1"), (1, "10"), (2, "100")], [(-0.4, "−0.4"), (0, "0"), (0.4, "0.4"), (0.8, "0.8"), (1.2, "1.2"), (1.6, "1.6")], "α (ค่าปรับ) — สเกล log →", "สัมประสิทธิ์ β̂")
    def sx(a): return sx0(np.log10(a))
    _zero_line(out, sx0, sy, -2, 2)
    for v, col in ((0.8, BLUE), (0.4, GREEN), (0.3, AMBER)):
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{col}" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>')
    _txt(out, x0 + w - 4, sy(0.8) - 5, "← ค่าจริง 0.8", BLUE, "end", size=9)
    _txt(out, x0 + w - 4, sy(0.4) - 5, "← ค่าจริง 0.4", GREEN, "end", size=9)
    names = [("market (จริง 0.8)", BLUE, ""), ("value (จริง 0.4)", GREEN, "6 3"), ("size (จริง 0.3)", AMBER, "")]
    for j, (nm, col, dsh) in enumerate(names):
        polyline(out, [(sx(a), sy(b)) for a, b in zip(alphas, paths[:, j])], col, 2.4, dash=dsh, shadow=not dsh)
    out.append(f'<line x1="{sx(10):.1f}" y1="{y0}" x2="{sx(10):.1f}" y2="{y0+h}" stroke="{PURPLE}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    _txt(out, sx(10) + 5, y0 + 12, "α = 10 ที่บทเลือก", PURPLE, "start", size=9, bold=True)
    _txt(out, sx(0.012), sy(ols[1]) + 15, f"OLS: value พุ่งไป {ols[1]:.2f}", GREEN, "start", size=9, bold=True)
    _txt(out, sx(0.012), sy(ols[0]) + 15, f"OLS: market ติดลบ {ols[0]:.2f}", BLUE, "start", size=9, bold=True)
    legend(out, [(c, n_, d) for n_, c, d in names], x0, H - 10)
    out.append("</svg>")
    NUMS["m11-ridge-path"] = dict(ols_mkt=float(ols[0]), ols_val=float(ols[1]), r10_mkt=float(r10[0]), r10_val=float(r10[1]), r10_size=float(r10[2]))
    return "\n".join(out)


# ── เครื่องมือวาดผัง (กล่อง · ลูกศร) ─────────────────────────────────────────────────────
_ARROW_COLS = dict(ink2=INK2, blue=BLUE, green=GREEN, red=RED, amber=AMBER, purple=PURPLE)


def arrow_defs():
    """marker หัวลูกศรครบทุกสีของเล่ม — เรียกครั้งเดียวต่อภาพที่มีลูกศร"""
    ms = "".join(f'<marker id="ar-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>' for k, v in _ARROW_COLS.items())
    return f"<defs>{ms}</defs>"


def _arrow_key(col):
    for k, v in _ARROW_COLS.items():
        if v == col: return k
    return "ink2"


def dbox(out, x, y, w, h, lines, col=BLUE, fill=0.10, rx=7):
    """กล่องมุมมน + ข้อความกึ่งกลาง · lines = [(ข้อความ, ขนาด, สี, หนา)] หรือสตริงล้วน"""
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{col}" fill-opacity="{fill}" stroke="{col}" stroke-width="1.8"/>')
    rows = [(ln, 10.5, INK, True) if isinstance(ln, str) else ln for ln in lines]
    total = sum(sz + 3.5 for _, sz, _, _ in rows) - 3.5
    cy = y + h / 2 - total / 2
    for text, sz, c, bold in rows:
        cy += sz
        _txt(out, x + w / 2, cy - sz * 0.22, text, c, "middle", size=sz, bold=bold)
        cy += 3.5


def darrow(out, x1, y1, x2, y2, col=INK2, width=2.0, dash="", label="", lsize=9, ldy=-5, lcol=None):
    ex = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{width}"{ex} marker-end="url(#ar-{_arrow_key(col)})"/>')
    if label: _txt(out, (x1 + x2) / 2, (y1 + y2) / 2 + ldy, label, lcol or col, "middle", size=lsize, bold=True)


def dchain(out, x, y, bw, h, gap, items, col=BLUE, fill=0.10, arrow_col=None):
    """กล่องเรียงแนวนอนพร้อมลูกศรเชื่อม · items = [lines, …] · คืนพิกัด x กึ่งกลางของแต่ละกล่อง"""
    xs = []
    for i, lines in enumerate(items):
        bx = x + i * (bw + gap)
        dbox(out, bx, y, bw, h, lines, col=col, fill=fill); xs.append(bx + bw / 2)
        if i: darrow(out, bx - gap + 2, y + h / 2, bx - 3, y + h / 2, arrow_col or INK2, 2.0)
    return xs


# ── Arbitrage (arb-part1…9) — ผังและแผนภาพ ────────────────────────────────────────────────
@fig("arb-part1.html", "a1-two-shops")
def fig_a1_two_shops():
    buy, sell = 30000.0, 30500.0
    Wd, H = 560, 250
    out = svg_open(Wd, H, f"ของชิ้นเดียวกันขายอยู่สองร้านคนละราคา ซื้อจากร้าน A ที่ {buy:,.0f} บาท แล้วขายที่ร้าน B ที่ {sell:,.0f} บาท ได้กำไร {sell-buy:,.0f} บาททันทีโดยไม่ต้องเดาราคา")
    title(out, Wd, f"Arbitrage คือซื้อถูกขายแพง พร้อมกัน ของชิ้นเดียวกัน — กำไร ฿{sell-buy:,.0f} ที่ไม่ต้องเดาทิศทาง",
          f"ทองแท่งเดียวกัน · ร้าน A ขาย ฿{buy:,.0f} · ร้าน B รับซื้อ ฿{sell:,.0f} · ทำสองขาพร้อมกัน จึงไม่มีความเสี่ยงราคาระหว่างทาง")
    out.append(arrow_defs())
    dbox(out, 40, 74, 180, 92, [("ร้าน A", 13, INK, True), ("ขาย ฿30,000", 11.5, GREEN, True), ("(ถูกกว่า)", 9.5, INK2, False)], col=GREEN, fill=0.12)
    dbox(out, 340, 74, 180, 92, [("ร้าน B", 13, INK, True), ("รับซื้อ ฿30,500", 11.5, RED, True), ("(แพงกว่า)", 9.5, INK2, False)], col=RED, fill=0.12)
    darrow(out, 228, 102, 332, 102, GREEN, 2.4, label="ซื้อที่ ฿30,000 →", ldy=-8)
    darrow(out, 332, 140, 228, 140, RED, 2.4, label="← ขายที่ ฿30,500", ldy=16)
    dbox(out, 190, 182, 180, 46, [(f"กำไร ฿{sell-buy:,.0f} ต่อแท่ง", 12.5, PURPLE, True), ("ไม่ต้องเดาว่าทองจะขึ้นหรือลง", 9.5, INK2, False)], col=PURPLE, fill=0.10)
    _txt(out, Wd / 2, 244, "เงื่อนไขที่ทำให้เป็น arb จริง: ของเหมือนกันเป๊ะ · ทำสองขาพร้อมกัน · ส่วนต่างเหลือหลังหักค่าใช้จ่ายทุกอย่าง", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    NUMS["a1-two-shops"] = dict(profit=sell - buy)
    return "\n".join(out)


def cost_waterfall_data(gross=0.80, comm=0.20, spread=0.50, slip=0.20):
    """ตัวเลขชุดเดียวกับกล่อง "กฎทอง" ในบท: arb 4 ขา · gross ฿0.80 → หักแล้วขาดทุน ฿0.10"""
    steps = [("Gross", gross, GREEN), ("Commission", -comm, RED), ("Bid-Ask Spread", -spread, RED), ("Slippage", -slip, RED)]
    return steps, gross - comm - spread - slip, comm + spread + slip


@fig("arb-part1.html", "a1-cost-waterfall")
def fig_a1_cost_waterfall():
    steps, net, total_cost = cost_waterfall_data()
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"แผนภาพน้ำตก: กำไรก่อนหักค่าใช้จ่าย 0.80 บาท ถูกหักค่านายหน้า 0.20 ส่วนต่างราคา 0.50 และ slippage 0.20 จึงติดลบ {net:.2f} บาท")
    title(out, Wd, f"ดูเหมือนกำไร ฿0.80 — หักค่าใช้จ่ายแล้วขาดทุนจริง ฿{abs(net):.2f}",
          f"arb 4 ขา จึงจ่ายค่านายหน้าและสเปรดสี่รอบ · ค่าใช้จ่ายรวม ฿{total_cost:.2f} = {total_cost/0.80*100:.0f}% ของ gross")
    x0, y0, w, h = 60, 62, 460, 170
    ymax, ymin = 0.9, -0.2
    def sy(v): return y0 + h - (v - ymin) / (ymax - ymin) * h
    out.append(f'<g stroke="{GRID}" stroke-width="1">' + "".join(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}"/>' for v in (0.2, 0.4, 0.6, 0.8)) + "</g>")
    for v in (-0.2, 0, 0.2, 0.4, 0.6, 0.8): _txt(out, x0 - 6, sy(v) + 3.5, f"{v:.1f}".replace("-", "−"), INK2, "end", size=9)
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    bw = 62; gap = (w - 5 * bw) / 4; run = 0.0
    for i, (nm, dv, col) in enumerate(steps):
        bx = x0 + i * (bw + gap)
        top, bot = (run, run + dv) if dv < 0 else (dv, 0.0)
        if i == 0: top, bot = dv, 0.0
        else: top, bot = run, run + dv
        out.append(f'<rect x="{bx:.1f}" y="{sy(max(top, bot)):.1f}" width="{bw}" height="{abs(sy(top)-sy(bot)):.1f}" rx="3" fill="{col}" opacity="0.75"/>')
        _txt(out, bx + bw / 2, sy(max(top, bot)) - 6, f"{dv:+.2f}".replace("-", "−"), col, "middle", size=10, bold=True)
        _txt(out, bx + bw / 2, y0 + h + 15, nm, INK2, "middle", size=9)
        run = dv if i == 0 else run + dv
        if i < len(steps) - 1:
            out.append(f'<line x1="{bx+bw:.1f}" y1="{sy(run):.1f}" x2="{bx+bw+gap:.1f}" y2="{sy(run):.1f}" stroke="{INK2}" stroke-width="1" stroke-dasharray="3 2"/>')
    bx = x0 + 4 * (bw + gap)
    col_net = PURPLE if net > 0 else RED
    out.append(f'<rect x="{bx:.1f}" y="{sy(max(net, 0)):.1f}" width="{bw}" height="{abs(sy(net)-sy(0)):.1f}" rx="3" fill="{col_net}" opacity="0.8"/>')
    _txt(out, bx + bw / 2, sy(min(net, 0)) + 14, f"−฿{abs(net):.2f}" if net < 0 else f"฿{net:.2f}", col_net, "middle", size=11, bold=True)
    _txt(out, bx + bw / 2, y0 + h + 15, "Net", col_net, "middle", size=9, bold=True)
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    _txt(out, x0, H - 26, f"฿0.80 − ฿0.20 − ฿0.50 − ฿0.20 = −฿{abs(net):.2f} — ส่วนต่างที่เห็นบนจอหายไปหมดแล้วยังติดลบ", INK, "start", size=10.5, bold=True)
    _txt(out, x0, H - 10, "เกณฑ์ก่อนกดจึงไม่ใช่ \"มากกว่า 0\" แต่คือ \"มากกว่าค่าใช้จ่ายทั้งหมดของทุกขา\"", RED, "start", size=9.5, bold=True)
    out.append("</svg>")
    NUMS["a1-cost-waterfall"] = dict(net=net, total_cost=total_cost)
    return "\n".join(out)


@fig("arb-part1.html", "a1-short-selling")
def fig_a1_short_selling():
    Wd, H = 560, 260
    out = svg_open(Wd, H, "สี่ขั้นของการขายชอร์ต: ยืมหุ้นจากโบรกเกอร์ ขายที่ 100 บาท รอราคาลงเหลือ 80 บาท ซื้อคืนแล้วคืนหุ้น ได้กำไร 20 บาท")
    title(out, Wd, "Short Selling — ยืมของมาขายก่อน แล้วค่อยซื้อคืนถูกกว่า: กำไร ฿100 − ฿80 = ฿20",
          "ขาที่คนใหม่มักลืม: ต้องมีของให้ยืมจริง · มีค่ายืม (borrow cost) · ถูกเรียกคืนกลางทางได้ (recall)")
    out.append(arrow_defs())
    items = [[("1. ยืมหุ้น", 11, INK, True), ("จากโบรกเกอร์", 9.5, INK2, False)],
             [("2. ขาย ฿100", 11, RED, True), ("ในตลาดวันนี้", 9.5, INK2, False)],
             [("3. รอราคาลง", 11, INK, True), ("฿100 → ฿80", 9.5, INK2, False)],
             [("4. ซื้อคืน ฿80", 11, GREEN, True), ("แล้วคืนหุ้น", 9.5, INK2, False)]]
    dchain(out, 34, 80, 112, 68, 27, items, col=BLUE, fill=0.10)
    dbox(out, 170, 176, 220, 42, [(f"กำไร = ฿100 − ฿80 = ฿20", 12, PURPLE, True)], col=PURPLE, fill=0.10)
    _txt(out, Wd / 2, 236, "ถ้าราคาขึ้นแทน ขาดทุนไม่จำกัด — เพราะราคาขึ้นได้ไม่มีเพดาน ต่างจากขาลงที่ตันที่ 0", RED, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, 250, "ใน arb ขาชอร์ตมักเป็นขาที่ 'ทำไม่ได้จริง' บ่อยที่สุด — เช็คก่อนเสมอว่ายืมได้และค่ายืมเท่าไร", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


@fig("arb-part2a.html", "a2a-two-layers")
def fig_a2a_two_layers():
    Wd, H = 560, 280
    out = svg_open(Wd, H, "สองชั้นของตัวต่อ: ชั้นเครื่องมือกำหนดรูปร่าง payoff ส่วนชั้นแพลตฟอร์มกำหนดเศรษฐศาสตร์ ต้นทุน yield และ margin")
    title(out, Wd, "ตัวต่อมีสองชั้น — ชั้นบนกำหนด \"รูปร่าง payoff\" ชั้นล่างกำหนด \"เศรษฐศาสตร์\"",
          "คนส่วนใหญ่มองแค่ชั้นบน · ดีลที่ดีที่สุดหลายดีลมาจากชั้นล่าง (ค่าธรรมเนียม · yield · margin offset)")
    out.append(arrow_defs())
    dbox(out, 40, 64, 480, 76, [("Instrument Blocks → กำหนดรูปร่าง Payoff", 11.5, BLUE, True),
                                ("Spot · Futures · Call · Put · Spread · PM Above · PM Range · Box · Conversion", 9.5, INK2, False),
                                ("ถามว่า: \"ถ้าราคาเป็นแบบนี้ → ได้หรือเสียเท่าไร\"", 9.5, INK, False)], col=BLUE, fill=0.10)
    dbox(out, 40, 156, 480, 76, [("Platform Blocks → กำหนดเศรษฐศาสตร์", 11.5, AMBER, True),
                                 ("Earn Yield · Convert Rate · Promo Rate · Margin Offset · Staking", 9.5, INK2, False),
                                 ("ถามว่า: \"ต้นทุนเท่าไร · ได้ yield ไหม · ลด margin ได้ไหม\"", 9.5, INK, False)], col=AMBER, fill=0.10)
    darrow(out, 280, 144, 280, 152, INK2, 2.0)
    _txt(out, Wd / 2, 250, "ผสมทั้งสองชั้น — payoff เดียวกันบนคนละแพลตฟอร์ม ให้ผลตอบแทนสุทธิไม่เท่ากัน", PURPLE, "middle", size=10, bold=True)
    _txt(out, Wd / 2, 266, "นี่คือที่มาของ near-arb ส่วนใหญ่: รูปร่างเหมือนกัน แต่เศรษฐศาสตร์ต่างกัน", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


@fig("arb-part2a.html", "a2a-claim-ladder")
def fig_a2a_claim_ladder():
    Wd, H = 560, 290
    out = svg_open(Wd, H, "บันไดความแน่นอนของข้อความสี่ระดับ จาก Exact Identity ที่จริงเสมอ ลงไปถึง Heuristic ที่อาจผิดได้")
    title(out, Wd, "ติดป้ายทุกข้อความก่อนเชื่อ — สี่ระดับ จาก \"จริงเสมอ\" ลงไปถึง \"อาจผิดได้\"",
          "ป้ายบอกว่าต้องตรวจอะไรก่อนลงเงิน · ข้อความที่ไม่มีป้าย คือข้อความที่ยังไม่ได้ตรวจ")
    rows = [("[Exact Identity]", "PCP · Box Spread · PM Yes + No = $1 — จริงเสมอ ไม่มีเงื่อนไข", GREEN),
            ("[Contract-specific]", "จริงตามกติกาของแพลตฟอร์มนั้น — ต้องเปิดอ่านกติกาก่อน", BLUE),
            ("[Observed]", "เห็นจริงในข้อมูล แต่ตัวเลขเปลี่ยนตามเวลา — ต้องวัดซ้ำ", AMBER),
            ("[Heuristic]", "กฎทั่วไปที่ใช้ได้บ่อย แต่อาจผิด — ต้องมีแผนรับเมื่อผิด", RED)]
    for i, (tag, desc, col) in enumerate(rows):
        y = 62 + i * 52
        dbox(out, 116, y, 404, 42, [(f"{tag}  {desc}", 9.8, INK, False)], col=col, fill=0.10)
        _txt(out, 112, y + 25, tag.strip("[]"), col, "end", size=10.5, bold=True)
    out.append(f'<line x1="70" y1="66" x2="70" y2="{62+3*52+42:.0f}" stroke="{INK2}" stroke-width="1.6" marker-end="url(#ar-ink2)"/>')
    out.append(arrow_defs())
    _txt(out, 64, 78, "แน่ใจมาก", GREEN, "end", size=9.5, bold=True)
    _txt(out, 64, 258, "ไม่แน่ใจ", RED, "end", size=9.5, bold=True)
    _txt(out, Wd / 2, 284, "ยิ่งลงล่าง ยิ่งต้องมีหลักฐานของตัวเองมากขึ้น และยิ่งต้องลงเงินน้อยลง", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


@fig("arb-part2b.html", "a2b-levels")
def fig_a2b_levels():
    Wd, H = 560, 250
    out = svg_open(Wd, H, "ห้าระดับของโอกาส จาก Pure Arb ที่กำไรแน่นอน ไล่ไปถึง Speculation ที่ต้องเดาทิศทาง")
    title(out, Wd, "ห้าระดับของ \"โอกาส\" — จากกำไรแน่นอน ไล่ไปจนถึงการเดาทิศทาง",
          "ระดับไม่ได้บอกว่าอันไหนดีกว่า แต่บอกว่าต้องใช้หลักฐานแค่ไหนและลงเงินได้เท่าไร")
    names = [("Lv.1", "Pure Arb", GREEN), ("Lv.2", "Near-Pure", BLUE), ("Lv.3", "Near-Arb", AMBER),
             ("Lv.4", "Structured", PURPLE), ("Lv.5", "Speculation", RED)]
    bw, gap = 92, 10
    x0 = (Wd - (5 * bw + 4 * gap)) / 2
    for i, (lv, nm, col) in enumerate(names):
        dbox(out, x0 + i * (bw + gap), 76, bw, 70, [(lv, 12, col, True), (nm, 10, INK, True)], col=col, fill=0.13)
    out.append(f'<line x1="{x0}" y1="168" x2="{x0+5*bw+4*gap:.0f}" y2="168" stroke="{INK2}" stroke-width="1.6" marker-end="url(#ar-ink2)"/>')
    out.append(arrow_defs())
    _txt(out, x0, 184, "แน่นอนมาก · กำไรล็อกได้", GREEN, "start", size=9.5, bold=True)
    _txt(out, x0 + 5 * bw + 4 * gap, 184, "ไม่แน่นอน · ต้องเดาทิศทาง", RED, "end", size=9.5, bold=True)
    _txt(out, Wd / 2, 214, "Lv.1–2 ล็อกกำไรได้ตั้งแต่วันเข้า · Lv.3–4 ต้องมีสมมติฐานและแผนรับเมื่อผิด · Lv.5 คือการเดา", INK2, "middle", size=9.5)
    _txt(out, Wd / 2, 234, "กับดัก: คนมักเรียก Lv.4–5 ว่า \"arb\" เพราะฟังดูปลอดภัยกว่า — ชื่อไม่ได้เปลี่ยนความเสี่ยง", RED, "middle", size=9.5, bold=True)
    out.append("</svg>")
    return "\n".join(out)


def stack_data(locked=(("Conversion", 50.0), ("Basis", 30.0), ("Box", 20.0)), income=(("Sell Put", 40.0), ("PM Tail Fade", 50.0))):
    return sum(v for _, v in locked), sum(v for _, v in income)


@fig("arb-part2b.html", "a2b-stack")
def fig_a2b_stack():
    locked = [("Conversion", 50.0), ("Basis", 30.0), ("Box", 20.0)]
    income = [("Sell Put", 40.0), ("PM Tail Fade", 50.0)]
    L, I = stack_data(tuple(locked), tuple(income))
    Wd, H = 560, 336
    out = svg_open(Wd, H, f"แกนกลางที่ล็อกกำไรไว้ {L:.0f} บาท รองรับชั้นหารายได้ที่ขาดทุนมากสุดรวม {I:.0f} บาท ผลรวมจึงไม่ติดลบ")
    title(out, Wd, f"วางชั้นหารายได้บนแกนที่ล็อกกำไรแล้ว — ขาดทุนมากสุด ฿{I:.0f} ≤ กำไรที่ล็อกไว้ ฿{L:.0f}",
          f"แกนกลาง: {' + '.join(f'{n} ฿{v:.0f}' for n, v in locked)} = ฿{L:.0f} · ชั้นรายได้เสียได้มากสุด ฿{income[0][1]:.0f} + ฿{income[1][1]:.0f} = ฿{I:.0f}")
    x0, w = 60, 440
    dbox(out, x0, 64, w, 56, [("Locked Edge (แกนกลาง)", 11.5, GREEN, True),
                              (" | ".join(f"{n} ฿{v:.0f}" for n, v in locked) + f"  →  รวม ฿{L:.0f}", 10, INK, False)], col=GREEN, fill=0.14)
    for i, (nm, v) in enumerate(income):
        dbox(out, x0, 132 + i * 56, w, 44, [(f"Income Layer {i+1} — {nm}: ขาดทุนมากสุด ฿{v:.0f}", 10.5, AMBER, True)], col=AMBER, fill=0.12)
    y = 132 + 2 * 56 + 6
    out.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+w}" y2="{y:.1f}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 3"/>')
    _txt(out, x0 + w, y - 6, f"เส้นขาดทุนรวมของชั้นรายได้ = ฿{I:.0f}", RED, "end", size=9.5, bold=True)
    dbox(out, x0, y + 12, w, 42, [(f"฿{I:.0f} ≤ ฿{L:.0f} ✓ ถ้าชั้นรายได้เสียหมด แกนกลางยังคุ้ม — ผลรวมไม่ติดลบ", 10.5, PURPLE, True)], col=PURPLE, fill=0.10)
    _txt(out, Wd / 2, H - 8, "ถ้าเมื่อไรขาดทุนมากสุดของชั้นรายได้เกินกำไรที่ล็อกไว้ โครงสร้างทั้งก้อนก็กลายเป็นการเดา", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    NUMS["a2b-stack"] = dict(locked=L, income=I)
    return "\n".join(out)


@fig("arb-part2b.html", "a2b-process")
def fig_a2b_process():
    Wd, H = 620, 250
    out = svg_open(Wd, H, "กระบวนการหกขั้นจากการสังเกตตลาด กรองด้วย regime จับคู่โปรไฟล์ สร้างโครงสร้าง ตรวจสี่ด่าน แล้วจัดอันดับ", multipanel=True)
    title(out, Wd, "กระบวนการหกขั้น — จาก \"เห็นอะไรบนจอ\" ไปถึง \"ลงไม้ไหนก่อน\"",
          "ทุกขั้นตัดของที่ไม่ผ่านทิ้ง · สิ่งที่รอดถึงขั้น 6 เท่านั้นที่ได้เงิน")
    out.append(arrow_defs())
    steps = [("1. OBSERVE", "ดู products", "อ่าน regime"), ("2. FILTER", "ตัดกลยุทธ์", "ที่ผิด regime"),
             ("3. MATCH", "จับคู่สิ่งที่เห็น", "กับโปรไฟล์"), ("4. CREATE", "สร้างโครงสร้างใหม่", "ถ้ายังไม่มี"),
             ("5. VERIFY", "4 ด่าน: ตัวเลข →", "ฐาน → ทำได้ → ข้อมูล"), ("6. RANK", "จัดอันดับ:", "ทำ / รอ / เฝ้า")]
    bw, gap = 88, 12
    x0 = (Wd - (6 * bw + 5 * gap)) / 2
    for i, (a, b, c) in enumerate(steps):
        bx = x0 + i * (bw + gap)
        dbox(out, bx, 76, bw, 74, [(a, 10.5, BLUE, True), (b, 8.8, INK2, False), (c, 8.8, INK2, False)], col=BLUE, fill=0.10)
        if i: darrow(out, bx - gap + 1, 113, bx - 3, 113, INK2, 1.8)
    _txt(out, Wd / 2, 178, "ทางเข้าอื่น: มีความเชื่ออยู่แล้ว → ข้ามขั้น 1–2 เข้าขั้น 3 ได้เลย แต่ต้องผ่านขั้น 5 เสมอ", PURPLE, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, 200, "ขั้นที่คนข้ามบ่อยที่สุดคือ 5 (VERIFY) — และเป็นขั้นเดียวที่กันไม่ให้เสียเงิน", RED, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, 222, "ผลลัพธ์ของขั้น 6 ไม่ใช่ \"ทำทุกอัน\" แต่คือลำดับว่าเงินก้อนถัดไปควรไปไหน", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


def ou_force_data(mu=0.0, theta=0.25, xs=(-3, -2, -1, 1, 2, 3)):
    return [(x, -theta * (x - mu)) for x in xs]


@fig("arb-part5.html", "a5-ou-spring")
def fig_a5_ou_spring():
    pts = ou_force_data(); theta = 0.25
    Wd, H = 560, 290
    out = svg_open(Wd, H, "แรงดึงกลับเข้าหาค่าเฉลี่ยโตตามระยะห่าง ที่ห่าง 3 หน่วยแรงดึงกลับแรงเป็นสามเท่าของที่ห่าง 1 หน่วย")
    title(out, Wd, "Mean Reversion เหมือนยางยืด — ยิ่งดึงออกไกลจาก μ ยิ่งถูกดึงกลับแรง",
          f"dx = θ(μ − x)dt + σ dW · θ = {theta} คือความแข็งของยาง · แรงดึงกลับ = θ × ระยะห่าง จึงโตเป็นเส้นตรงตามระยะ")
    (sx, sy), (x0, y0, w, h) = _std_frame(out, Wd, H, [(-3, "−3σ"), (-2, "−2σ"), (-1, "−1σ"), (0, "μ"), (1, "+1σ"), (2, "+2σ"), (3, "+3σ")], [(-0.9, "−0.9"), (-0.45, ""), (0, "0"), (0.45, ""), (0.9, "+0.9")], "ระยะห่างจากค่าเฉลี่ย", "แรงดึงกลับต่อหน่วยเวลา")
    out.append(arrow_defs())
    out.append(f'<line x1="{sx(0):.1f}" y1="{y0}" x2="{sx(0):.1f}" y2="{y0+h}" stroke="{PURPLE}" stroke-width="1.6" stroke-dasharray="5 3"/>')
    _zero_line(out, sx, sy, -3, 3)
    polyline(out, [(sx(-3), sy(theta * 3)), (sx(3), sy(-theta * 3))], BLUE, 2.4)
    for x, f in pts:
        col = GREEN if f > 0 else RED
        _dot(out, sx(x), sy(f), col, 4)
        darrow(out, sx(x), sy(f), sx(x + (0.55 if f > 0 else -0.55)), sy(f), col, 2.0)
    _txt(out, sx(-2.9), sy(0.82), "ต่ำกว่า μ → ถูกดึงขึ้น", GREEN, "start", size=9.5, bold=True)
    _txt(out, sx(2.9), sy(-0.82), "สูงกว่า μ → ถูกดึงลง", RED, "end", size=9.5, bold=True)
    _txt(out, sx(0) + 6, y0 + 12, "μ = จุดยึด", PURPLE, "start", size=9.5, bold=True)
    _txt(out, sx(-2.9), sy(-0.62), "เส้นน้ำเงิน = แรงดึงกลับ θ(μ − x)", BLUE, "start", size=9.5, bold=True)
    _txt(out, x0, H - 8, f"ครึ่งชีวิตของการกลับเข้าหาค่าเฉลี่ย = ln2 / θ ≈ {np.log(2)/theta:.1f} หน่วยเวลา — บอกว่าไม้หนึ่งควรถือนานแค่ไหน", INK2, "start", size=9, italic=True)
    out.append("</svg>")
    NUMS["a5-ou-spring"] = dict(theta=theta, halflife=float(np.log(2) / theta))
    return "\n".join(out)


@fig("arb-part7.html", "a7-pipeline")
def fig_a7_pipeline():
    Wd, H = 620, 270
    out = svg_open(Wd, H, "สายงานของระบบเทรดหกกล่อง จาก data feed ไปถึง position monitor โดยมี kill switch และ position limit คุมอยู่ทุกจุด", multipanel=True)
    title(out, Wd, "สายงานของระบบ — ทุกกล่องมีทางหยุดของตัวเอง ไม่ใช่แค่กล่องสุดท้าย",
          "ระบบที่หยุดไม่ได้ ไม่ใช่ระบบอัตโนมัติ แต่คือระเบิดเวลา · คนต้องเห็นและสั่งหยุดได้เสมอ")
    out.append(arrow_defs())
    names = [("Data Feed", "ราคา · funding · IV"), ("Scanner", "ไล่หาเงื่อนไข"), ("Signal Gen", "แปลงเป็นไม้"),
             ("Risk Check", "ผ่าน/ไม่ผ่าน"), ("Order Router", "ส่งคำสั่ง"), ("Position Monitor", "เฝ้าและ rehedge")]
    bw, gap = 88, 12
    x0 = (Wd - (6 * bw + 5 * gap)) / 2
    for i, (a, b) in enumerate(names):
        bx = x0 + i * (bw + gap)
        col = RED if a == "Risk Check" else BLUE
        dbox(out, bx, 72, bw, 62, [(a, 10, col, True), (b, 8.8, INK2, False)], col=col, fill=0.12)
        if i: darrow(out, bx - gap + 1, 103, bx - 3, 103, INK2, 1.8)
    dbox(out, x0, 158, 2 * bw + gap, 44, [("Alert System", 10.5, AMBER, True), ("เตือนเมื่อผิดปกติ", 8.8, INK2, False)], col=AMBER, fill=0.12)
    dbox(out, x0 + 4 * (bw + gap), 158, 2 * bw + gap, 44, [("คน (Human)", 10.5, PURPLE, True), ("ตัดสินใจและสั่งหยุด", 8.8, INK2, False)], col=PURPLE, fill=0.12)
    darrow(out, x0 + bw, 144, x0 + bw, 154, INK2, 1.8)
    darrow(out, x0 + 2 * bw + gap + 8, 180, x0 + 4 * (bw + gap) - 4, 180, AMBER, 1.8)
    _txt(out, Wd / 2, 226, "Kill Switch + Position Limit ต้องมีที่ทุกจุด ไม่ใช่แค่ปลายทาง", RED, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, 246, "คำถามที่ต้องตอบได้ก่อนเปิดระบบ: ถ้ากล่องนี้พัง ระบบจะหยุดเองหรือจะยิงคำสั่งต่อ", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


@fig("arb-part9.html", "a9-checklist")
def fig_a9_checklist():
    Wd, H = 560, 430
    out = svg_open(Wd, H, "ผังตัดสินใจเจ็ดข้อ ตั้งแต่ติดป้ายชนิดข้อความ ไปจนถึงลงขนาดครึ่ง Kelly โดยมีทางออก STOP สองจุด")
    title(out, Wd, "เจอ \"โอกาส\" แล้วทำอะไรต่อ — เจ็ดคำถามที่ต้องผ่านก่อนลงเงิน",
          "สองข้อที่ทำให้หยุดบ่อยที่สุดคือข้อ 3 (เหลือกำไรจริงไหม) และข้อ 5 (กรณีแย่สุดรับได้ไหม)")
    out.append(arrow_defs())
    rows = [("เจอ \"Opportunity\"", INK2, False), ("1. ติดป้าย: [Exact] หรือ [Heuristic]?", BLUE, False),
            ("2. ระดับไหน: Lv.1–5?", BLUE, False), ("3. หักค่าใช้จ่ายทุกอย่างแล้ว ยังเหลือกำไรไหม?", RED, True),
            ("4. ดีกว่าทางที่ง่ายที่สุดไหม (baseline)?", BLUE, False), ("5. กรณีแย่สุดรับไหวไหม · อยู่รอดไหม?", RED, True),
            ("6. ขนาด: Kelly → ใช้ครึ่ง Kelly", AMBER, False), ("7. ลงไม้ + เฝ้า + บันทึก", GREEN, False)]
    bw = 330; x0 = 80
    for i, (text, col, stop) in enumerate(rows):
        y = 58 + i * 42
        dbox(out, x0, y, bw, 32, [(text, 10, INK, i in (0, 7))], col=col, fill=0.10)
        if i: darrow(out, x0 + bw / 2, y - 10, x0 + bw / 2, y - 3, INK2, 1.6)
        if stop:
            darrow(out, x0 + bw + 4, y + 16, x0 + bw + 52, y + 16, RED, 1.8)
            _txt(out, x0 + bw + 56, y + 20, "ไม่ → STOP", RED, "start", size=9.5, bold=True)
    _txt(out, Wd / 2, H - 22, "ไม่มีข้อไหนข้ามได้ — ข้อที่ข้ามคือข้อที่จะทำให้เสียเงิน", RED, "middle", size=10, bold=True)
    _txt(out, Wd / 2, H - 6, "STOP ไม่ใช่ความล้มเหลว · ส่วนใหญ่ของวันที่ทำงานดี คือวันที่ไม่ได้ลงไม้เลย", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


# ── ตาของ Arbitrageur · คณิตศาสตร์ · คิดแบบ Quant — ผังและแผนภาพ ─────────────────────────
@fig("eye-part1.html", "e1-everything-option")
def fig_e1_everything_option():
    Wd, H = 560, 330
    out = svg_open(Wd, H, "ของใช้ประจำวันหกอย่างที่จริง ๆ แล้วเป็น option: ประกันรถคือ long put คูปองลดราคาคือ call มัดจำคอนโดคือ call คืนของได้เจ็ดวันคือ free put เงินเดือนคือ bond และโบนัสถึงเป้าคือ digital call")
    title(out, Wd, "\"ถ้า…แล้ว…\" ที่ไหนก็ตาม ที่นั่นมี option ซ่อนอยู่",
          "ทุกแถวมีคนถือสิทธิ์และคนรับภาระเสมอ · คำถามเดียวที่ต้องถามคือ \"ใครจ่ายเบี้ย และใครรับความเสี่ยง\"")
    dbox(out, 150, 58, 260, 36, [("สัญญาที่ขึ้นกับเงื่อนไข = Option", 11.5, PURPLE, True)], col=PURPLE, fill=0.12)
    rows = [("ประกันรถ", "Long Put — จ่ายเบี้ย ได้ชดเชยถ้าชน", "คุณ", "บริษัทประกัน", BLUE),
            ("คูปอง \"ลด 20% ภายในเดือนนี้\"", "Call — สิทธิ์ซื้อถูก มีวันหมดอายุ", "คุณ", "ร้านค้า", GREEN),
            ("มัดจำคอนโด ฿50,000", "Call — เบี้ย = มัดจำ · strike = ราคาคอนโด", "คุณ", "ผู้พัฒนา", GREEN),
            ("\"คืนได้ภายใน 7 วัน\"", "Put ที่แถมฟรี — ไม่พอใจก็คืนได้", "คุณ", "ร้านค้า", BLUE),
            ("เงินเดือนประจำ", "Bond — ได้เงินคงที่ทุกงวด ไม่ขึ้นกับผลงาน", "คุณ", "บริษัท", INK2),
            ("โบนัส \"ถ้ายอดขายถึงเป้า\"", "Digital Call — ได้ก้อนคงที่ถ้าเกินเป้า", "คุณ", "บริษัท", AMBER)]
    _txt(out, 40, 112, "ของใช้ประจำวัน", INK, "start", size=9.5, bold=True)
    _txt(out, 240, 112, "จริง ๆ แล้วคือ", INK, "start", size=9.5, bold=True)
    _txt(out, 512, 112, "ใครถือสิทธิ์ / ใครรับภาระ", INK, "end", size=9.5, bold=True)
    for i, (thing, kind, long_, short_, col) in enumerate(rows):
        y = 122 + i * 32
        out.append(f'<rect x="34" y="{y}" width="492" height="28" rx="4" fill="{col}" fill-opacity="0.07"/>')
        _txt(out, 40, y + 18, thing, INK, "start", size=9.5, bold=True)
        _txt(out, 240, y + 18, kind, col, "start", size=9.5, bold=True)
        _txt(out, 512, y + 18, f"{long_} / {short_}", INK2, "end", size=9)
    _txt(out, Wd / 2, 322, "เห็น option ในของธรรมดาได้เมื่อไร ก็เริ่มถามได้ว่า \"เบี้ยที่จ่ายอยู่นี้ แพงไปหรือเปล่า\"", INK2, "middle", size=9.5, italic=True)
    out.append("</svg>")
    return "\n".join(out)


def eln_data(note_price=105.0, bond=97.0, half_call=5.0):
    """฿5 คือราคาของ \"0.5 × Call\" ทั้งชิ้น (ตามบท: 97 + 5 = 102) ไม่ใช่ราคา Call เต็มสัญญา"""
    cost = bond + half_call
    return cost, note_price - cost


@fig("eye-part2.html", "e2-eln-decompose")
def fig_e2_eln_decompose():
    cost, markup = eln_data()
    Wd, H = 560, 280
    out = svg_open(Wd, H, f"ถอด structured note ราคา 105 บาท ออกเป็นพันธบัตร 97 บาท บวกครึ่งสัญญาของ call 5 บาท ต้นทุนจริงจึงเป็น {cost:.0f} บาท ส่วนต่าง {markup:.0f} บาทคือส่วนที่จ่ายเกิน")
    title(out, Wd, f"ถอดเลโก้แล้วรู้ราคาจริง — ขาย ฿105 แต่ต้นทุนชิ้นส่วนรวม ฿{cost:.0f} ต่างกัน ฿{markup:.0f}",
          "\"คืนเงินต้น + 50% ของ upside\" = พันธบัตร + Call ครึ่งสัญญา · ราคาของประกอบต้องเท่ากับผลรวมราคาชิ้นส่วน")
    out.append(arrow_defs())
    dbox(out, 34, 76, 150, 74, [("Structured Note", 11, INK, True), ("ขาย ฿105", 13, RED, True)], col=RED, fill=0.12)
    _txt(out, 198, 118, "=", INK, "middle", size=18, bold=True)
    dbox(out, 214, 76, 130, 74, [("Bond", 11, GREEN, True), ("฿97", 13, GREEN, True), ("(คืนเงินต้น 100)", 8.8, INK2, False)], col=GREEN, fill=0.12)
    _txt(out, 358, 118, "+", INK, "middle", size=18, bold=True)
    dbox(out, 374, 76, 150, 74, [("0.5 × Call", 11, BLUE, True), ("฿5", 13, BLUE, True), ("(ราคาของครึ่งสัญญา)", 8.8, INK2, False)], col=BLUE, fill=0.12)
    darrow(out, 289, 158, 289, 176, INK2, 2.0)
    dbox(out, 150, 182, 260, 44, [(f"ต้นทุนจริง = 97 + 5 = ฿{cost:.0f}", 11.5, PURPLE, True),
                                  (f"คุณจ่ายแพงเกินไป ฿{markup:.0f}", 10.5, RED, True)], col=PURPLE, fill=0.10)
    _txt(out, Wd / 2, 246, "ความซับซ้อนคือเบี้ยที่คนจ่ายเพราะไม่รู้ว่ามันประกอบจากอะไร — ถอดเป็นก็ไม่ต้องจ่าย", INK, "middle", size=10, bold=True)
    _txt(out, Wd / 2, 266, "กับดัก: \"50% ของ upside\" คือ Call 0.5 สัญญา ไม่ใช่ Call ที่ strike ครึ่งหนึ่ง และไม่ใช่ครึ่งราคา", RED, "middle", size=9, bold=True)
    out.append("</svg>")
    NUMS["e2-eln-decompose"] = dict(cost=cost, markup=markup)
    return "\n".join(out)


@fig("math-part1.html", "m1-pcp")
def fig_m1_pcp():
    Wd, H = 560, 300
    out = svg_open(Wd, H, "สมการ put-call parity: call บวกเงินสดเท่ากับ put บวกหุ้น แล้วย้ายข้างได้สูตรประกอบร่างสี่แบบ")
    title(out, Wd, "Put-Call Parity — สมการเดียวที่ย้ายข้างได้สี่สูตร \"ประกอบร่าง\"",
          "C + PV(K) = P + S ทั้งสองข้างให้ max(S, K) ที่วันหมดอายุเหมือนกัน ราคาวันนี้จึงต้องเท่ากัน")
    out.append(arrow_defs())
    dbox(out, 60, 62, 180, 56, [("C + PV(K)", 13, BLUE, True), ("Long Call + เงินฝาก", 9.5, INK2, False)], col=BLUE, fill=0.12)
    _txt(out, 280, 96, "=", INK, "middle", size=20, bold=True)
    dbox(out, 320, 62, 180, 56, [("P + S", 13, GREEN, True), ("Long Put + หุ้น", 9.5, INK2, False)], col=GREEN, fill=0.12)
    _txt(out, Wd / 2, 138, "↓ ย้ายข้างสมการ ได้สี่สูตรประกอบร่าง ↓", PURPLE, "middle", size=10, bold=True)
    rows = [("S = C − P + PV(K)", "Synthetic Stock", GREEN), ("C = P + S − PV(K)", "Synthetic Call", BLUE),
            ("P = C − S + PV(K)", "Synthetic Put", AMBER), ("PV(K) = P + S − C", "Synthetic Bond", PURPLE)]
    for i, (eq, nm, col) in enumerate(rows):
        x = 34 + (i % 2) * 254; y = 152 + (i // 2) * 56
        dbox(out, x, y, 238, 46, [(eq, 11, col, True), (nm, 9.5, INK2, False)], col=col, fill=0.10)
    _txt(out, Wd / 2, 286, "อยากได้ของชิ้นไหนแต่ซื้อตรง ๆ ไม่ได้ — ย้ายข้างหาชิ้นนั้น แล้วประกอบจากที่เหลือ", INK2, "middle", size=9.5, italic=True)
    out.append("</svg>")
    return "\n".join(out)


def bs_anatomy_data(S=100.0, K=100.0, r=0.05, sg=0.25, T=1.0):
    """เลขชุดเดียวกับตัวอย่างหลักของบท §11.3: S = K = 100 · r = 5% · σ = 25% · T = 1 ปี → C = 12.34"""
    g = bs_greeks(S, K=K, r=r, sg=sg, T=T)
    d1 = (np.log(S / K) + (r + sg * sg / 2) * T) / (sg * np.sqrt(T)); d2 = d1 - sg * np.sqrt(T)
    Nd1, Nd2 = _N(float(d1)), _N(float(d2)); disc = K * np.exp(-r * T)
    return float(d1), float(d2), Nd1, Nd2, float(disc), S * Nd1, float(disc) * Nd2, float(g["C"])


@fig("math-part7.html", "m7-bs-anatomy")
def fig_m7_bs_anatomy():
    d1, d2, Nd1, Nd2, disc, term1, term2, C = bs_anatomy_data()
    Wd, H = 560, 290
    out = svg_open(Wd, H, f"กายวิภาคของสูตร Black-Scholes ด้วยตัวเลขจริง: สิ่งที่ได้ {term1:.2f} ลบสิ่งที่จ่าย {term2:.2f} เท่ากับราคา call {C:.2f}")
    title(out, Wd, "สูตร Black-Scholes อ่านเป็นภาษาคน — \"คาดว่าจะได้\" ลบ \"คาดว่าจะจ่าย\"",
          f"เลขชุดเดียวกับ §11.3: S = K = 100 · r = 5% · σ = 25% · T = 1 ปี · d₁ = {d1:.3f} · d₂ = {d2:.3f}")
    out.append(arrow_defs())
    dbox(out, 30, 64, 200, 80, [("S₀ · N(d₁)", 12.5, GREEN, True), (f"100 × {Nd1:.4f} = {term1:.2f}", 10.5, INK, True),
                                ("สิ่งที่ได้: หุ้น ถ่วงด้วย Delta", 9, INK2, False)], col=GREEN, fill=0.12)
    _txt(out, 252, 108, "−", INK, "middle", size=20, bold=True)
    dbox(out, 274, 64, 256, 80, [("K · e⁻ʳᵀ · N(d₂)", 12.5, RED, True), (f"{disc:.2f} × {Nd2:.4f} = {term2:.2f}", 10.5, INK, True),
                                 ("สิ่งที่จ่าย: เงิน K คิดลด ถ้าได้ใช้สิทธิ์", 9, INK2, False)], col=RED, fill=0.12)
    darrow(out, 280, 152, 280, 170, INK2, 2.0)
    dbox(out, 170, 176, 220, 46, [(f"= C = {term1:.2f} − {term2:.2f} = {C:.2f}", 12.5, PURPLE, True)], col=PURPLE, fill=0.10)
    _txt(out, Wd / 2, 244, "N(d₂) = โอกาส (risk-neutral) ที่จะได้ใช้สิทธิ์ · N(d₁) = Delta ไม่ใช่ความน่าจะเป็น", INK, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, 262, "S₀ มาจาก Part I · N(·) มาจาก Part II · d₁ ใช้แคลคูลัส Part III · การคิดลดมาจาก Part I", INK2, "middle", size=9, italic=True)
    _txt(out, Wd / 2, 280, f"ATM แต่ N(d₁) = {Nd1:.4f} ไม่ใช่ 0.5 เพราะดอกเบี้ยและ σ²/2 ดัน d₁ ให้เป็นบวก", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    NUMS["m7-bs-anatomy"] = dict(d1=d1, d2=d2, Nd1=Nd1, Nd2=Nd2, term1=term1, term2=term2, C=C)
    return "\n".join(out)


@fig("math-part11.html", "m11-cv-split")
def fig_m11_cv_split():
    Wd, H = 560, 300
    out = svg_open(Wd, H, "เทียบสองวิธีแบ่งข้อมูล: k-fold สุ่มสลับทำให้ชุดฝึกอยู่ทั้งก่อนและหลังชุดทดสอบ ส่วน walk-forward ให้ชุดฝึกอยู่ก่อนชุดทดสอบเสมอ", multipanel=True)
    title(out, Wd, "k-fold กับ walk-forward — วิธีแบ่งข้อมูลที่ต่างกันตรง \"เวลา\"",
          "ข้อมูลการเงินมีลำดับเวลา · แบ่งผิดวิธี ชุดฝึกจะมีอนาคตปนอยู่ และผลทดสอบจะสวยเกินจริง")
    L, R = 55, 505; n = 5; bw = (R - L) / n
    _txt(out, L, 66, "k-fold (สุ่มสลับ) — ชุดฝึกอยู่ทั้งสองข้างของชุดทดสอบ", RED, "start", size=10.5, bold=True)
    for i in range(n):
        test = i == 2
        col = AMBER if test else BLUE
        out.append(f'<rect x="{L+i*bw+2:.1f}" y="76" width="{bw-4:.1f}" height="36" rx="4" fill="{col}" fill-opacity="{0.55 if test else 0.20}" stroke="{col}" stroke-width="1.5"/>')
        _txt(out, L + i * bw + bw / 2, 99, "ทดสอบ" if test else "ฝึก", INK if test else INK2, "middle", size=10, bold=test)
    out.append(arrow_defs())
    darrow(out, L + 3.6 * bw, 124, L + 2.6 * bw, 124, RED, 1.8)
    _txt(out, L + 3.7 * bw, 128, "อนาคตรั่วย้อนกลับมาสอนอดีต", RED, "start", size=9.5, bold=True)
    _txt(out, L, 166, "walk-forward — ชุดฝึกอยู่ก่อนชุดทดสอบเสมอ", GREEN, "start", size=10.5, bold=True)
    for k in range(4):
        y = 176 + k * 26
        tr = 1 + k
        out.append(f'<rect x="{L+2:.1f}" y="{y}" width="{tr*bw-4:.1f}" height="20" rx="3" fill="{BLUE}" fill-opacity="0.20" stroke="{BLUE}" stroke-width="1.2"/>')
        _txt(out, L + tr * bw / 2, y + 14, "ฝึก", INK2, "middle", size=9)
        out.append(f'<rect x="{L+tr*bw+2:.1f}" y="{y}" width="{bw-4:.1f}" height="20" rx="3" fill="{AMBER}" fill-opacity="0.55" stroke="{AMBER}" stroke-width="1.2"/>')
        _txt(out, L + tr * bw + bw / 2, y + 14, "ทดสอบ", INK, "middle", size=9, bold=True)
    darrow(out, L, 288, R, 288, INK2, 1.6)
    _txt(out, L + 4, 282, "เวลา →  ชุดฝึกโตขึ้นเรื่อย ๆ เหมือนตอนเทรดจริง", INK2, "start", size=9.5, bold=True)
    out.append("</svg>")
    return "\n".join(out)


def belief_line_stations():
    return ["① ข้อความ", "② ฐาน", "③ การวัด", "④ การกระจาย", "⑤ ต้นทุน", "⑥ โครงสร้าง", "⑦ ขนาด", "⑧ บันทึก"]


def _belief_line_svg():
    st = belief_line_stations()
    Wd, H = 620, 320
    out = svg_open(Wd, H, "สายการผลิตความเชื่อแปดสถานี เรียงสองแถว ตั้งแต่ตั้งข้อความไปจนถึงบันทึก โดยอินดิเคเตอร์อยู่ที่สถานีที่ 3 เพียงสถานีเดียว", multipanel=True)
    title(out, Wd, "สายการผลิตความเชื่อ 8 สถานี — อินดิเคเตอร์อยู่แค่สถานีเดียว",
          "ความรู้สึกเข้าต้นสาย · ออกปลายสายเป็นตำแหน่งที่มีขนาด มีกฎออก และมีวิธีรู้ว่าผิด")
    out.append(arrow_defs())
    bw, bh, gap = 92, 44, 12
    x0, y1, y2 = 90, 92, 178
    # หมายเหตุอินดิเคเตอร์วางไว้เหนือแถวบน เพื่อให้ช่องว่างระหว่างแถวโล่ง
    bx3 = x0 + 2 * (bw + gap) + bw / 2
    _txt(out, bx3, y1 - 16, "อินดิเคเตอร์ทั้งหมดอยู่ตรงนี้ — สถานีเดียว", AMBER, "middle", size=9.5, bold=True)
    darrow(out, bx3, y1 - 12, bx3, y1 - 3, AMBER, 1.8)
    dbox(out, 8, y1, 72, bh, [("ความรู้สึก", 9.5, INK2, True)], col=INK2, fill=0.08)
    darrow(out, 82, y1 + bh / 2, x0 - 3, y1 + bh / 2, INK2, 1.8)
    for i, nm in enumerate(st):
        row, ci = divmod(i, 4)
        bx = x0 + ci * (bw + gap); by = y1 if row == 0 else y2
        col = AMBER if i == 2 else BLUE
        dbox(out, bx, by, bw, bh, [(nm, 10, col, True)], col=col, fill=0.16 if i == 2 else 0.10)
        if ci: darrow(out, bx - gap + 1, by + bh / 2, bx - 3, by + bh / 2, INK2, 1.6)
    right = x0 + 3 * (bw + gap) + bw
    _txt(out, right + 6, y1 + bh / 2 + 4, "↓ ต่อแถวล่าง", INK2, "start", size=9, bold=True)
    dbox(out, 500, y2 - 4, 112, 52, [("ออกปลายทาง", 9.5, GREEN, True), ("ตำแหน่งที่มีขนาด", 9, INK, True)], col=GREEN, fill=0.12)
    darrow(out, right + 3, y2 + bh / 2, 496, y2 + bh / 2, GREEN, 1.8)
    _txt(out, 556, y2 + 62, "มีกฎออก · รู้ว่าผิดเมื่อไร", GREEN, "middle", size=9, bold=True)
    yf = y2 + bh + 30
    out.append(f'<path d="M {right-46:.0f} {y2+bh+4:.0f} C {right-46:.0f} {yf:.0f}, {x0+40:.0f} {yf:.0f}, {x0+40:.0f} {y2+bh+6:.0f}" fill="none" stroke="{PURPLE}" stroke-width="1.6" stroke-dasharray="5 3" marker-end="url(#ar-purple)"/>')
    _txt(out, (right + x0) / 2 - 20, yf + 4, "⑧ บันทึก ป้อนกลับไปแก้ ① ข้อความ", PURPLE, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, 292, "สถานีที่คนข้ามบ่อยที่สุดคือ ② ฐาน และ ⑤ ต้นทุน — สองสถานีที่ตัดสินว่าได้เงินหรือไม่", RED, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, 310, "ถ้าสถานีไหนตอบไม่ได้ ความเชื่อนั้นยังไม่พร้อมลงเงิน — ไม่ใช่เพราะสัญญาณไม่ดี แต่เพราะยังไม่ครบสาย", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    return "\n".join(out)


@fig("nq-index.html", "nq-belief-line")
def fig_nq_belief_line_index():
    return _belief_line_svg()


@fig("nq-part0.html", "nq-belief-line")
def fig_nq_belief_line_part0():
    return _belief_line_svg()


def _nq_fig():
    with open(os.path.join(DOCS, "nq-figures.json"), encoding="utf-8") as fh:
        return json.load(fh)


@fig("nq-part0.html", "nq0-base-rate")
def fig_nq0_base_rate():
    f = _nq_fig(); b = f["btc"]
    base = b["สัดส่วนวันที่ขึ้นเปอร์เซ็นต์"]; nb = b["จำนวนวันที่มีผลตอบแทน"]
    aft = b["วันถัดจากขึ้น3วันติด"]["สัดส่วนที่ขึ้นเปอร์เซ็นต์"]; na = b["วันถัดจากขึ้น3วันติด"]["จำนวนตัวอย่าง"]
    flip = b["วันถัดจากขึ้น3วันติด"]["ถ้าพลิกหนึ่งครั้งเปอร์เซ็นต์"]
    Wd, H = 560, 300
    out = svg_open(Wd, H, f"แท่งเทียบสัดส่วนวันที่ราคาขึ้น: ทุกวันได้ {base}% จาก {nb} วัน เทียบกับหลังขึ้นสามวันติดได้ {aft}% จากแค่ {na} ครั้ง")
    title(out, Wd, f"สัญญาณทำให้แย่ลง ไม่ใช่ดีขึ้น — ฐาน {base}% แต่หลังขึ้น 3 วันติดเหลือ {aft}%",
          f"BTC {f['btc']['ช่วงข้อมูล']['จำนวนวัน']} วัน · ก่อนถามว่า \"สัญญาณนี้ดีไหม\" ต้องรู้ก่อนว่าไม่ใช้สัญญาณเลยได้เท่าไร")
    x0, y0, w, h = 90, 66, 380, 150
    def sy(v): return y0 + h - (v - 40) / 25 * h
    for v in (40, 45, 50, 55, 60):
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, x0 - 6, sy(v) + 3.5, f"{v}%", INK2, "end", size=9)
    out.append(f'<line x1="{x0}" y1="{sy(50):.1f}" x2="{x0+w}" y2="{sy(50):.1f}" stroke="{INK2}" stroke-width="1.6" stroke-dasharray="5 3"/>')
    _txt(out, x0 + w + 4, sy(50) + 3.5, "50% = เหรียญ", INK2, "start", size=9)
    bars = [(base, f"ทุกวัน (ไม่ใช้สัญญาณ)", f"n = {nb}", BLUE), (aft, "หลังขึ้น 3 วันติด", f"n = {na} — น้อยเกินไป", RED)]
    bw = 110
    for i, (v, nm, sub, col) in enumerate(bars):
        bx = x0 + 60 + i * 190
        out.append(f'<rect x="{bx:.1f}" y="{sy(v):.1f}" width="{bw}" height="{sy(40)-sy(v):.1f}" rx="4" fill="{col}" opacity="0.75"/>')
        _txt(out, bx + bw / 2, sy(v) - 7, f"{v}%", col, "middle", size=13, bold=True)
        _txt(out, bx + bw / 2, y0 + h + 16, nm, INK, "middle", size=9.5, bold=True)
        _txt(out, bx + bw / 2, y0 + h + 30, sub, INK2, "middle", size=9)
    _txt(out, Wd / 2, 258, f"ตัวอย่างแค่ {na} ครั้ง — พลิกผลแค่ครั้งเดียวก็กลายเป็น {flip}% แล้ว", RED, "middle", size=10, bold=True)
    _txt(out, Wd / 2, 276, "ตัวเลขที่ขยับง่ายขนาดนี้ ยังไม่ใช่หลักฐานว่าสัญญาณใช้ได้หรือใช้ไม่ได้", INK2, "middle", size=9.5, italic=True)
    _txt(out, Wd / 2, 292, "สิ่งที่บอกได้แน่คือ: มันไม่ได้ดีกว่าการไม่ใช้สัญญาณเลย", INK, "middle", size=9.5, bold=True)
    out.append("</svg>")
    NUMS["nq0-base-rate"] = dict(base=base, aft=aft, n_after=na, flip=flip)
    return "\n".join(out)


@fig("nq-part2.html", "nq2-claim-ladder")
def fig_nq2_claim_ladder():
    Wd, H = 560, 300
    out = svg_open(Wd, H, "บันไดสี่ขั้นจากความรู้สึกที่ตรวจสอบไม่ได้ ไปสู่ข้อความที่ครบห้าช่องและบอกได้ว่าผิดเมื่อไร")
    title(out, Wd, "สี่ขั้นจาก \"ความรู้สึก\" ไปเป็น \"ข้อความที่ตัดสินได้\"",
          "ขั้นที่ตัดสินไม่ได้ ไม่ใช่ข้อความที่ผิด — แต่เป็นข้อความที่ไม่มีวันผิด จึงสอนอะไรไม่ได้เลย")
    rows = [("ขั้น 1 · \"BTC กำลังจะขึ้น\"", "ทุกผลลัพธ์เข้าได้หมด — ไม่มีวันผิด", RED),
            ("ขั้น 2 · \"จะขึ้นแรงในระยะสั้น\"", "\"แรง\" กับ \"สั้น\" ไม่มีเส้นแบ่ง — ยังตัดสินไม่ได้", AMBER),
            ("ขั้น 3 · \"ปิดเหนือ 72,000 ใน 5 วันทำการ\"", "ตรวจสอบได้แล้ว แต่ยังไม่บอกว่าวัดจากไหน", BLUE),
            ("ขั้น 4 · ครบห้าช่อง + เงื่อนไขที่บอกว่าผิด", "ตัดสินได้ · สอนได้ · แก้ย้อนหลังไม่ได้", GREEN)]
    for i, (head, desc, col) in enumerate(rows):
        y = 68 + i * 52
        dbox(out, 96, y, 424, 44, [(head, 10.5, col, True), (desc, 9.2, INK2, False)], col=col, fill=0.10)
        _txt(out, 88, y + 27, f"{i+1}", col, "end", size=13, bold=True)
    out.append(arrow_defs())
    out.append(f'<line x1="60" y1="72" x2="60" y2="266" stroke="{INK2}" stroke-width="1.6" marker-end="url(#ar-ink2)"/>')
    _txt(out, 52, 84, "ตรวจสอบไม่ได้", RED, "middle", size=9, bold=True)
    _txt(out, 52, 262, "ตรวจสอบได้", GREEN, "middle", size=9, bold=True)
    _txt(out, Wd / 2, 292, "ห้าช่อง: อะไร · เท่าไร · เมื่อไร · วัดจากไหน · ผิดเมื่อไร", INK, "middle", size=9.5, bold=True)
    out.append("</svg>")
    return "\n".join(out)


def copula_tail_data():
    with open(os.path.join(DOCS, "copula-figures.json"), encoding="utf-8") as fh:
        d = json.load(fh)
    tails = d["tailถ้าสมมติfamilyไว้ก่อน"]; fits = d["fitด้วยML"]
    aic = {k: v["AIC"] for k, v in fits.items()}
    return d, tails, aic


@fig("statarb-copula-practice.html", "copula-tail-by-family")
def fig_copula_tail_by_family():
    d, tails, aic = copula_tail_data()
    rows = [("Gaussian", tails["Gaussian"], aic.get("Gaussian")), ("Student-t (df=8)", tails["Student-t (df=8)"], None),
            ("Student-t (df=5)", tails["Student-t (df=5)"], None), ("Student-t (df=3)", tails["Student-t (df=3)"], aic.get("Student-t")),
            ("Gumbel", tails["Gumbel"], aic.get("Gumbel")), ("Clayton", tails["Clayton"], aic.get("Clayton"))]
    lo, hi = min(v for _, v, _ in rows), max(v for _, v, _ in rows)
    nd = d["ข้อมูล"]["จำนวนวันผลตอบแทน"]
    Wd, H = 560, 334
    out = svg_open(Wd, H, f"แท่งแสดง tail dependence จากข้อมูลชุดเดียวกัน {nd} วัน ที่เปลี่ยนไปตามตระกูล copula ที่สมมติ ตั้งแต่ {lo:.3f} ถึง {hi:.3f}")
    title(out, Wd, f"ข้อมูลชุดเดิม {nd} วัน แต่ tail dependence วิ่งตั้งแต่ {lo:.3f} ถึง {hi:.3f}",
          f"BTC/ETH · Kendall tau = {d['ความสัมพันธ์']['Kendall']} · ตัวเลขที่ได้ขึ้นกับว่าคุณสมมติ family ไหน ไม่ใช่ข้อมูลบอก")
    x0, y0, w, h = 150, 62, 330, 186
    def sx(v): return x0 + v / 0.9 * w
    for v in (0, 0.2, 0.4, 0.6, 0.8):
        out.append(f'<line x1="{sx(v):.1f}" y1="{y0}" x2="{sx(v):.1f}" y2="{y0+h}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, sx(v), y0 + h + 14, f"{v:.1f}", INK2, "middle", size=9)
    bh = h / len(rows) - 8
    best = min((a for _, _, a in rows if a is not None))
    for i, (nm, v, a) in enumerate(rows):
        y = y0 + i * (bh + 8) + 4
        col = GREEN if a == best else (BLUE if a is None else AMBER)
        out.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{max(sx(v)-x0, 2):.1f}" height="{bh:.1f}" rx="3" fill="{col}" opacity="0.72"/>')
        _txt(out, x0 - 6, y + bh / 2 + 3.5, nm, INK, "end", size=9.5, bold=True)
        _txt(out, max(sx(v) + 6, x0 + 8), y + bh / 2 + 3.5, f"{v:.3f}" + (f"  ·  AIC {a:.2f}" if a is not None else ""), col, "start", size=9, bold=True)
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.4"/>')
    _txt(out, x0 + w / 2, y0 + h + 32, "ค่า tail dependence (λ) ที่ family นั้นบอก", INK2, "middle", size=9.5)
    _txt(out, Wd / 2, 302, f"ML เลือก Gaussian (AIC {best:.2f} ต่ำสุด) ซึ่งบอกว่า λ = 0 พอดี — ไม่มี tail dependence เลย", GREEN, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, 322, "ถ้าสมมติ Clayton ไว้ก่อน จะได้ 0.857 จากข้อมูลชุดเดียวกัน — family คือสิ่งที่คุณเลือก ไม่ใช่สิ่งที่ข้อมูลเลือก", RED, "middle", size=9.5, bold=True)
    out.append("</svg>")
    NUMS["copula-tail-by-family"] = dict(lo=lo, hi=hi, best_aic=best)
    return "\n".join(out)


# ── ภาคผนวก E (nq) และ statarb — ภาพที่เคยอยู่ใน marker CHART แต่ไม่มี generator เขียนให้ ──────
# ไฟล์กลุ่มนี้ใช้ CSS คลาส .fig (เต็มความกว้าง) และมีบรรทัดคำบรรยายใต้ภาพ จึงคืน svg + <div class="cap">
def _cap(text):
    return f'<div class="cap">{text}</div>'


def _load(name):
    with open(os.path.join(DOCS, name), encoding="utf-8") as fh:
        return json.load(fh)


def _daily_prices():
    d = _load("nq-figures.json")["ราคารายวัน"]
    ks = sorted(d)
    return ks, [float(d[k]) for k in ks]


def _thai_day(iso):
    m = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    y, mo, dd = iso.split("-")
    return f"{int(dd)} {m[int(mo)-1]}"


def rsi_series():
    import indicator_figures as IF
    ks, px = _daily_prices()
    rows = IF.rsi_wilder(px)
    pts = [(k, r["rsi"]) for k, r in zip(ks, rows) if r]
    return pts, _load("indicator-figures.json")["RSI"]


@fig("nq-appendix-indicators.html", "ind-rsi")
def fig_ind_rsi():
    pts, R = rsi_series()
    first = R["ครั้งแรกที่เกิน70"]; top = R["RSI สูงสุด"]
    n_over, n_under = R["จำนวนวันเกิน70"], R["จำนวนวันต่ำกว่า30"]
    Wd, H = 780, 300
    out = svg_open(Wd, H, f"กราฟ RSI 14 วันของ BTC {len(pts)} วัน พร้อมเส้น 70 และ 30 · RSI ทะลุ 70 ครั้งแรกวันที่ {first['วันที่']} ที่ {first['RSI']} แล้วค้างอยู่เหนือ 70 รวม {n_over} วัน ส่วนโซนต่ำกว่า 30 ไม่มีวันไหนแตะเลย", cls="fig")
    title(out, Wd, f"RSI(14) บนราคาจริง — ทะลุ 70 แล้วค้าง {n_over} วัน ขณะราคายังขึ้นต่อ +{first['ราคาเปลี่ยนหลังจากนั้นเปอร์เซ็นต์']}%",
          f"{_thai_day(pts[0][0])} – {_thai_day(pts[-1][0])} 2026 · โซนต่ำกว่า 30 ไม่มีวันไหนแตะเลยทั้งช่วง ({n_under} วัน) — เพราะเป็นตลาดขาขึ้น ไม่ใช่เพราะสูตรแม่น")
    x0, y0, w, h = 56, 56, Wd - 96, 176
    sx = lambda i: x0 + i / (len(pts) - 1) * w
    sy = lambda v: y0 + h - v / 100 * h
    for v, lab, col in ((70, "70", RED), (50, "50", INK2), (30, "30", GREEN)):
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{col}" stroke-width="1.2" stroke-dasharray="5 3" opacity="0.8"/>')
        _txt(out, x0 - 8, sy(v) + 4, lab, col, "end", size=10, bold=True)
    for v in (0, 100): _txt(out, x0 - 8, sy(v) + 4, str(v), INK2, "end", size=9)
    out.append(f'<rect x="{x0}" y="{sy(100):.1f}" width="{w}" height="{sy(70)-sy(100):.1f}" fill="{RED}" opacity="0.07"/>')
    out.append(f'<rect x="{x0}" y="{sy(30):.1f}" width="{w}" height="{sy(0)-sy(30):.1f}" fill="{GREEN}" opacity="0.07"/>')
    _txt(out, x0 + 6, sy(94), "โซน \"overbought\" ตามตำรา", RED, "start", size=9.5, bold=True)
    _txt(out, x0 + w - 6, sy(8), f"โซน \"oversold\" ตามตำรา — ไม่มีวันไหนลงมาเลย ({n_under} วัน)", GREEN, "end", size=9.5, bold=True)
    polyline(out, [(sx(i), sy(v)) for i, (_, v) in enumerate(pts)], BLUE, 2.2, shadow=False)
    idx = {k: i for i, (k, _) in enumerate(pts)}
    vmap = dict(pts)
    for key, lab, anc, dx, dy in ((first["วันที่"], f"{_thai_day(first['วันที่'])} · RSI {first['RSI']}", "end", -9, 4),
                                  (top["วันที่"], f"{_thai_day(top['วันที่'])} · สูงสุด {top['RSI']}", "start", 9, -6)):
        i = idx[key]; v = vmap[key]
        _dot(out, sx(i), sy(v), PURPLE, 4)
        _txt(out, sx(i) + dx, sy(v) + dy, lab, PURPLE, anc, size=9.5, bold=True)
    i0 = idx[first["วันที่"]]
    _txt(out, sx(i0) - 9, sy(vmap[first["วันที่"]]) + 18, "EMA สั่งซื้อวันเดียวกัน", AMBER, "end", size=9, bold=True)
    out.append(f'<line x1="{x0}" y1="{y0+h:.1f}" x2="{x0+w}" y2="{y0+h:.1f}" stroke="{AXIS}" stroke-width="1.2"/>')
    _txt(out, x0, y0 + h + 15, _thai_day(pts[0][0]), INK2, "start", size=9)
    _txt(out, x0 + w, y0 + h + 15, _thai_day(pts[-1][0]), INK2, "end", size=9)
    _txt(out, Wd / 2, y0 + h + 40, f"RSI ทะลุ 70 แล้วค้างอยู่ {n_over} วัน ขณะราคาขึ้นต่ออีก +{first['ราคาเปลี่ยนหลังจากนั้นเปอร์เซ็นต์']}% — \"overbought\" ไม่ได้แปลว่าจะลง", RED, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, y0 + h + 58, f"สัดส่วนวันที่ RSI เกิน 70 = {R['สัดส่วนวันเกิน70เปอร์เซ็นต์']}% ของ {len(pts)} วันที่คำนวณได้", INK2, "middle", size=9.5)
    out.append("</svg>")
    NUMS["ind-rsi"] = dict(n=len(pts), over70=n_over, under30=n_under, first=first["RSI"], top=top["RSI"])
    return "\n".join(out) + "\n" + _cap(f"RSI(14) แบบ Wilder บนราคา BTC รายวันจริง {len(pts)} วันที่คำนวณได้ · ช่วงอุ่นเครื่อง 14 วันแรกตัดทิ้ง")


def lsma_series(win=20, last=24):
    import indicator_figures as IF
    ks, px = _daily_prices()
    em = IF.ema(px, win)
    ls = [None] * len(px)
    for i in range(win - 1, len(px)):
        ls[i] = IF.ols_time(px[i - win + 1:i + 1])["end"]
    sl = slice(len(px) - last, len(px))
    return ks[sl], px[sl], em[sl], ls[sl]


@fig("nq-appendix-indicators.html", "ind-lsma")
def fig_ind_lsma():
    ks, px, em, ls = lsma_series()
    LR = _load("indicator-figures.json")["LinearRegression"]["วันสุดท้าย"]
    Wd, H = 780, 320
    out = svg_open(Wd, H, f"กราฟราคา BTC เทียบ EMA 20 วัน และ LSMA 20 วัน · EMA ตามหลังราคาตลอดขาขึ้น ส่วน LSMA แซงขึ้นไปอยู่เหนือราคาในวันสุดท้ายที่ {ls[-1]:,.0f} ขณะราคาอยู่ที่ {px[-1]:,.0f}", cls="fig")
    title(out, Wd, "ค่าเฉลี่ยตามหลัง · regression ล้ำหน้า — ราคาอยู่ตรงกลาง",
          f"{_thai_day(ks[0])} – {_thai_day(ks[-1])} 2026 · EMA20 ตามหลังเพราะถ่วงอดีต · LSMA คือปลายเส้นถดถอย 20 วัน จึงยื่นไปตามความชันล่าสุด")
    x0, y0, w, h = 64, 58, Wd - 108, 190
    vals = [v for v in px + list(em) + list(ls) if v is not None]
    lo, hi = min(vals) * 0.985, max(vals) * 1.015
    sx = lambda i: x0 + i / (len(px) - 1) * w
    sy = lambda v: y0 + h - (v - lo) / (hi - lo) * h
    for v in range(int(lo // 5000) * 5000, int(hi) + 5000, 5000):
        if lo <= v <= hi:
            out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
            _txt(out, x0 - 8, sy(v) + 4, f"{v//1000}k", INK2, "end", size=9)
    for series, col, wdt, dash in ((px, INK, 2.4, ""), (em, BLUE, 2.0, ""), (ls, GREEN, 2.0, "6 3")):
        pts = [(sx(i), sy(v)) for i, v in enumerate(series) if v is not None]
        polyline(out, pts, col, wdt, dash=dash, shadow=False)
    _dot(out, sx(len(px) - 1), sy(ls[-1]), GREEN, 4); _dot(out, sx(len(px) - 1), sy(px[-1]), INK, 4); _dot(out, sx(len(px) - 1), sy(em[-1]), BLUE, 4)
    _txt(out, sx(len(px) - 1) - 8, sy(ls[-1]) - 8, f"LSMA20 {ls[-1]:,.0f} — ล้ำหน้าราคา", GREEN, "end", size=9.5, bold=True)
    _txt(out, sx(len(px) - 1) - 8, sy(px[-1]) + 18, f"ราคา {px[-1]:,.0f}", INK, "end", size=9.5, bold=True)
    _txt(out, sx(len(px) - 1) - 8, sy(em[-1]) + 16, f"EMA20 {em[-1]:,.0f} — ตามหลังราคา", BLUE, "end", size=9.5, bold=True)
    out.append(f'<line x1="{x0}" y1="{y0+h:.1f}" x2="{x0+w}" y2="{y0+h:.1f}" stroke="{AXIS}" stroke-width="1.2"/>')
    _txt(out, x0, y0 + h + 15, _thai_day(ks[0]), INK2, "start", size=9)
    _txt(out, x0 + w, y0 + h + 15, _thai_day(ks[-1]), INK2, "end", size=9)
    legend(out, [(INK, "ราคา BTC", ""), (BLUE, "EMA20", ""), (GREEN, "LSMA20 (ปลายเส้นถดถอย 20 วัน)", "6 3")], x0, H - 34)
    _txt(out, Wd / 2, H - 12, f"วันสุดท้าย regression ชัน {LR['slope ต่อวัน']:,.0f} ดอลลาร์/วัน (R² = {LR['R2']}) — LSMA จึงยื่นเลยราคาไป {ls[-1]-px[-1]:,.0f}", INK2, "middle", size=9.5, bold=True)
    out.append("</svg>")
    NUMS["ind-lsma"] = dict(lsma=float(ls[-1]), price=float(px[-1]), ema=float(em[-1]))
    return "\n".join(out) + "\n" + _cap("ราคา BTC รายวันจริง · EMA20 และ LSMA20 คำนวณจากชุดเดียวกัน · บนเทรนด์เส้นตรง EMA20 ตามหลัง 9.5 วันโดยนิยาม ส่วน LSMA ตามหลัง 0 วัน — แต่ที่โค้งมันจะยื่นเลย")


def _hbars(out, rows, x0, y0, w, bh, gap, vmax, fmt_v, hi_i=None):
    """แท่งแนวนอน: rows = [(ป้าย, ค่า, สี, ป้ายย่อย)]"""
    for i, (lab, v, col, sub) in enumerate(rows):
        y = y0 + i * (bh + gap)
        out.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{max(v/vmax*w, 2):.1f}" height="{bh:.1f}" rx="3" fill="{col}" opacity="{0.85 if i == hi_i else 0.7}"/>')
        _txt(out, x0 - 8, y + bh / 2 + 4, lab, INK, "end", size=10, bold=True)
        _txt(out, x0 + max(v / vmax * w, 2) + 8, y + bh / 2 + 4, fmt_v(v), col, "start", size=11, bold=True)
        if sub: _txt(out, x0 + max(v / vmax * w, 2) + 8 + 6.2 * len(fmt_v(v)) + 10, y + bh / 2 + 4, sub, INK2, "start", size=9)


@fig("statarb-alpha-decay.html", "decay-detection")
def fig_decay_detection():
    d = _load("alpha-decay-figures.json")
    tab = [r for r in d["ตารางตรวจจับ"] if (r["edgeเดิมเปอร์เซ็นต์"], r["ลดลงจุด"]) in {(55.0, 3.0), (55.0, 5.0), (55.0, 7.0), (60.0, 5.0), (60.0, 10.0)}]
    base = d["กรณีตั้งต้นของบท"]; rate = d["สมมติฐานจังหวะเทรดของมิน"]["ไม้ต่อสัปดาห์"]
    Wd, H = 780, 288
    out = svg_open(Wd, H, f"กราฟแท่งแสดงจำนวนปีที่ต้องใช้ถึงจะตรวจจับได้ว่า edge เสื่อมจริง ที่ {rate} ไม้ต่อสัปดาห์ · edge ลดลงยิ่งน้อย ยิ่งใช้เวลานาน จาก {tab[0]['ปี']} ปีเหลือ {tab[-1]['ปี']} ปี", cls="fig")
    title(out, Wd, f"ยิ่ง edge เสื่อมน้อย ยิ่งตรวจจับยากแบบไม่เป็นเส้นตรง — ที่ {rate} ไม้/สัปดาห์",
          f"กรณีตั้งต้นของบท: {base['edgeเดิมเปอร์เซ็นต์']:.0f}% → {base['edgeหลังเสื่อมเปอร์เซ็นต์']:.0f}% ต้องใช้ {base['จำนวนไม้']:,} ไม้ = {base['ปี']} ปี · ระหว่างนั้นยังไม่รู้ว่า edge หายจริงหรือแค่ดวงไม่ดี")
    rows = [(f"{r['edgeเดิมเปอร์เซ็นต์']:.0f}% → {r['edgeหลังเสื่อมเปอร์เซ็นต์']:.0f}%", r["ปี"],
             RED if r["ปี"] > 20 else (AMBER if r["ปี"] > 8 else GREEN), f"ลดลง {r['ลดลงจุด']:.0f} จุด · {r['จำนวนไม้']:,} ไม้") for r in tab]
    vmax = max(v for _, v, _, _ in rows) * 1.12
    _hbars(out, rows, 150, 66, 430, 28, 10, vmax, lambda v: f"{v} ปี")
    _txt(out, Wd / 2, 260, f"เวลาที่ต้องใช้ถึงจะตรวจจับได้ (ที่ {rate} ไม้/สัปดาห์) — ไม่ใช่เวลาที่ edge หายไป", INK, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, 278, "แปลว่า: การสรุปว่า \"edge หายแล้ว\" หลังขาดทุนสองเดือน แทบไม่มีหลักฐานทางสถิติรองรับ", RED, "middle", size=9.5, bold=True)
    out.append("</svg>")
    NUMS["decay-detection"] = dict(base_years=base["ปี"], n_rows=len(rows))
    return "\n".join(out) + "\n" + _cap(f"สูตร power calculation เดียวกับ nq-tool-samplesize · z_alpha={d['สูตร']['z_alpha']} z_beta={d['สูตร']['z_beta']} (90% power) · จังหวะเทรดของมิน {rate} ไม้/สัปดาห์")


@fig("statarb-data-quality.html", "data-quality-survivorship")
def fig_dq_survivorship():
    d = _load("data-quality-figures.json")["ผู้รอดชีวิต"]
    ven = [("Deribit", d["deribit"]), ("OKX", d["okx"])]
    days = _load("nq-figures.json")["btc"]["ช่วงข้อมูล"]["จำนวนวัน"]
    Wd, H = 780, 178
    out = svg_open(Wd, H, f"กราฟแท่งเทียบอัตราการรอดของสัญญา BTC จากวันแรกถึงวันสุดท้ายของข้อมูล {days} วัน Deribit รอด {ven[0][1]['สัดส่วนที่รอดเปอร์เซ็นต์']}% ส่วน OKX รอดเพียง {ven[1][1]['สัดส่วนที่รอดเปอร์เซ็นต์']}%", cls="fig")
    title(out, Wd, f"สัญญาที่ยังอยู่ครบทั้งวันแรกและวันสุดท้าย — Deribit {ven[0][1]['สัดส่วนที่รอดเปอร์เซ็นต์']}% · OKX {ven[1][1]['สัดส่วนที่รอดเปอร์เซ็นต์']}%",
          f"ถ้าเทสต์กับเฉพาะสัญญาที่ \"ยังอยู่\" ก็กำลังเลือกเฉพาะผู้รอดชีวิต · และสองตลาดรอดไม่เท่ากัน จึงย้ายผลข้ามตลาดไม่ได้")
    rows = [(nm, v["สัดส่วนที่รอดเปอร์เซ็นต์"], BLUE if i == 0 else AMBER, f"{v['อยู่ครบทั้งสองวัน']:,}/{v['จำนวนวันแรก']:,} สัญญา") for i, (nm, v) in enumerate(ven)]
    _hbars(out, rows, 130, 62, 420, 30, 12, 100.0, lambda v: f"{v}%")
    _txt(out, Wd / 2, 156, f"ฐาน = สัญญา BTC ที่มีอยู่ในวันแรก ({days} วัน) · ที่เหลือหมดอายุหรือหายไประหว่างทาง", INK2, "middle", size=9.5)
    _txt(out, Wd / 2, 172, "ตลาดหนึ่งบอกอะไรไม่ได้เลยเกี่ยวกับอีกตลาด — ความต่างนี้คือสัญญาณ ไม่ใช่ noise", RED, "middle", size=9.5, bold=True)
    out.append("</svg>")
    NUMS["data-quality-survivorship"] = dict(deribit=ven[0][1]["สัดส่วนที่รอดเปอร์เซ็นต์"], okx=ven[1][1]["สัดส่วนที่รอดเปอร์เซ็นต์"])
    return "\n".join(out) + "\n" + _cap(f"Deribit: {ven[0][1]['อยู่ครบทั้งสองวัน']}/{ven[0][1]['จำนวนวันแรก']} สัญญา · OKX: {ven[1][1]['อยู่ครบทั้งสองวัน']}/{ven[1][1]['จำนวนวันแรก']} สัญญา · ทั้งสองตลาดข้อมูลครบ {days}/{days} วัน ไม่มีวันขาดหาย")


@fig("statarb-live-vs-backtest.html", "live-liquidity")
def fig_live_liquidity():
    d = _load("live-backtest-figures.json")
    L = d["สภาพคล่องทั้งกระดาน"]; day = d["ข้อมูล"]["วันที่ตรวจ"]
    rows = [("ไม่มีปริมาณซื้อขายเลยใน 24 ชม. · Deribit", L["deribit"]["ไม่มีปริมาณซื้อขาย24ชมเปอร์เซ็นต์"], RED, f"{L['deribit']['ไม่มีปริมาณซื้อขาย24ชม']:,}/{L['deribit']['สัญญาทั้งหมด']:,}"),
            ("ไม่มีปริมาณซื้อขายเลยใน 24 ชม. · OKX", L["okx"]["ไม่มีปริมาณซื้อขาย24ชมเปอร์เซ็นต์"], RED, f"{L['okx']['ไม่มีปริมาณซื้อขาย24ชม']:,}/{L['okx']['สัญญาทั้งหมด']:,}"),
            ("ไม่มีราคาเสนอซื้อเลย · Deribit", L["deribit"]["ไม่มีราคาเสนอซื้อเปอร์เซ็นต์"], AMBER, f"{L['deribit']['ไม่มีราคาเสนอซื้อ']:,}/{L['deribit']['สัญญาทั้งหมด']:,}"),
            ("ไม่มีราคาเสนอซื้อเลย · OKX", L["okx"]["ไม่มีราคาเสนอซื้อเปอร์เซ็นต์"], AMBER, f"{L['okx']['ไม่มีราคาเสนอซื้อ']:,}/{L['okx']['สัญญาทั้งหมด']:,}")]
    Wd, H = 780, 268
    out = svg_open(Wd, H, f"กราฟแท่งเทียบสัดส่วนสัญญาที่ไม่มีปริมาณซื้อขายใน 24 ชั่วโมงและไม่มีราคาเสนอซื้อ ระหว่าง Deribit และ OKX ในวันที่ {day}", cls="fig")
    title(out, Wd, "การมีราคาในไฟล์ข้อมูล ไม่ได้แปลว่าเทรดได้จริง",
          f"ตรวจทั้งกระดานในวันเดียว ({day}) ไม่ใช่แค่ใกล้ ATM · เกือบครึ่งกระดานไม่มีใครซื้อขายเลยตลอด 24 ชั่วโมง")
    _hbars(out, rows, 260, 62, 300, 26, 12, 55.0, lambda v: f"{v}%")
    _txt(out, Wd / 2, 226, f"mark price อยู่นอกช่วง bid-ask: Deribit {L['deribit']['markอยู่นอกช่วงbidask']} สัญญา · OKX {L['okx']['markอยู่นอกช่วงbidask']} สัญญา", INK2, "middle", size=9.5)
    _txt(out, Wd / 2, 246, "backtest ที่สมมติว่า \"ถ้าราคาผ่านเกณฑ์ก็เทรดได้\" กำลังนับไม้ที่ไม่มีทางเกิดขึ้นจริง", RED, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, 262, "ตัวเลขนี้เป็นของวันเดียว — แต่พอจะบอกได้ว่า \"มีข้อมูล\" กับ \"มีสภาพคล่อง\" เป็นคนละเรื่อง", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    NUMS["live-liquidity"] = dict(novol_deribit=rows[0][1], novol_okx=rows[1][1], nobid_deribit=rows[2][1], nobid_okx=rows[3][1])
    return "\n".join(out) + "\n" + _cap(f"ทั้งกระดาน ไม่ใช่แค่ใกล้ ATM · Deribit {L['deribit']['สัญญาทั้งหมด']:,} สัญญา · OKX {L['okx']['สัญญาทั้งหมด']:,} สัญญา · mark price อยู่นอกช่วง bid-ask: Deribit {L['deribit']['markอยู่นอกช่วงbidask']} สัญญา · OKX {L['okx']['markอยู่นอกช่วงbidask']} สัญญา")


@fig("statarb-signal-blending.html", "blending-search")
def fig_blending_search():
    d = _load("blending-figures.json")
    S = d["การค้นหา"]; trap = S["ตัวกรองเดี่ยวที่ดีที่สุดแบบไม่จำกัดวันกระตุ้น_กับดัก"]
    solo = S["ตัวกรองเดี่ยวที่ดีที่สุดที่วันกระตุ้นพอ"]; best = S["ชุดรวมที่ดีที่สุด"]
    gain = S["ส่วนที่การรวมสร้างขึ้นจุดเปอร์เซ็นต์"]; base = d["ป้ายกำกับ"]["อัตราฐานเปอร์เซ็นต์"]
    rows = [(f"ตัวกรองเดี่ยว ไม่จำกัดวันกระตุ้น", trap["ค่ายกเปอร์เซ็นต์"], RED, f"{trap['ชื่อวิธี']} · กระตุ้นแค่ {trap['จำนวนวันกระตุ้น']} วัน (กับดัก)"),
            (f"ตัวกรองเดี่ยว กระตุ้น ≥ 5 วัน", solo["ค่ายกเปอร์เซ็นต์"], BLUE, f"{solo['ชื่อวิธี']} · กระตุ้น {solo['จำนวนวันกระตุ้น']} วัน"),
            (f"ชุดรวมที่ดีที่สุดจาก {S['จำนวนวิธีรวมทั้งหมด']} วิธี", best["ค่ายกเปอร์เซ็นต์"], GREEN, f"= {best['ชื่อวิธี']} เท่านั้น · กระตุ้น {best['จำนวนวันกระตุ้น']} วัน")]
    Wd, H = 780, 262
    out = svg_open(Wd, H, f"กราฟแท่งเทียบค่ายกของตัวกรอง: ตัวกรองเดี่ยวที่ไม่จำกัดวันกระตุ้นให้ {trap['ค่ายกเปอร์เซ็นต์']} จุดแต่เป็นกับดักตัวอย่างเล็ก ส่วนตัวกรองเดี่ยวที่กระตุ้นพอและชุดรวมที่ดีที่สุดให้เท่ากันที่ {best['ค่ายกเปอร์เซ็นต์']} จุด", cls="fig")
    title(out, Wd, f"ค้นหา {S['จำนวนวิธีรวมทั้งหมด']} วิธีรวมตัวกรอง — ชุดที่ดีที่สุดคือตัวกรองเดี่ยว การรวมไม่ได้เพิ่มอะไรเลย",
          f"ป้ายกำกับ: สเปรดวันถัดไปลู่เข้าจริงไหม · อัตราฐาน {base}% · ค่ายก = อัตราสำเร็จ − อัตราฐาน (จุดเปอร์เซ็นต์)")
    _hbars(out, rows, 250, 66, 300, 30, 14, 55.0, lambda v: f"+{v} จุด")
    _txt(out, Wd / 2, 200, f"ส่วนที่ \"การรวม\" สร้างขึ้นจริง = {gain} จุด — ชุดรวมที่ดีที่สุดเท่ากับตัวกรองเดี่ยวพอดี", PURPLE, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, 222, f"แถบแดงคือกับดัก: กระตุ้นแค่ {trap['จำนวนวันกระตุ้น']} วันแล้วถูก {trap['อัตราสำเร็จเปอร์เซ็นต์']:.0f}% ทุกวัน — ตัวอย่างเล็กเกินกว่าจะเชื่อ", RED, "middle", size=9.5, bold=True)
    _txt(out, Wd / 2, 242, f"จาก {S['จำนวนวิธีรวมทั้งหมด']} วิธี เหลือ {S['จำนวนวิธีที่มีวันกระตุ้นพอ(≥5วัน)']} วิธีที่มีวันกระตุ้นพอจะอ่านค่าได้", INK2, "middle", size=9, italic=True)
    out.append("</svg>")
    NUMS["blending-search"] = dict(trap=trap["ค่ายกเปอร์เซ็นต์"], solo=solo["ค่ายกเปอร์เซ็นต์"], best=best["ค่ายกเปอร์เซ็นต์"], gain=gain)
    return "\n".join(out) + "\n" + _cap(f"ป้ายกำกับ: สเปรดวันถัดไปลู่เข้าจริงไหม · อัตราฐาน {base}% · ค้นหาทั้งหมด {S['จำนวนวิธีรวมทั้งหมด']} วิธี เหลือ {S['จำนวนวิธีที่มีวันกระตุ้นพอ(≥5วัน)']} วิธีที่มีวันกระตุ้นพอจะอ่านค่าได้")


# ── statarb: ความเป็นกลาง (Part XV Portfolio Engineering) — อ่านจาก docs/neutrality-figures.json ──
def _nt():
    return _load("neutrality-figures.json")


@fig("statarb-neutrality.html", "nt-ladder")
def fig_nt_ladder():
    d = _nt(); rows = d["ขั้นบันไดความเป็นกลาง"]
    Wd, H = 780, 330
    out = svg_open(Wd, H, "แท่งคู่แสดง exposure ที่เหลือต่อปัจจัยตลาดและปัจจัยที่สอง ของความเป็นกลางสี่ขั้น — ขั้นที่สูงขึ้นลด exposure ลงเรื่อย ๆ แต่ dollar-neutral ไม่ลดปัจจัยที่สองเลย", cls="fig")
    title(out, Wd, "สามขั้นของ \"ความเป็นกลาง\" ลดคนละอย่าง — ไม่ใช่คำเดียวกัน",
          "ค่าสัมบูรณ์เฉลี่ยของ exposure ที่เหลือ วัดด้วยเบต้า/แกมมาจริง ซึ่งรู้ได้เพราะหน้าตัดขวางเป็นข้อมูลจำลอง")
    x0, y0, w, h = 190, 66, 470, 196
    vmax = max(max(r["exposureตลาดสัมบูรณ์เฉลี่ย"] for r in rows),
               max(r["exposureปัจจัยสองสัมบูรณ์เฉลี่ย"] for r in rows)) * 1.18
    sx = lambda v: x0 + v / vmax * w
    for k in range(6):
        v = vmax * k / 5
        out.append(f'<line x1="{sx(v):.1f}" y1="{y0}" x2="{sx(v):.1f}" y2="{y0+h}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, sx(v), y0 + h + 15, f"{v:.2f}", INK2, "middle", size=9)
    rh = h / len(rows)
    for i, r in enumerate(rows):
        yb = y0 + i * rh + 6
        _txt(out, x0 - 12, yb + 14, r["ขั้น"], INK, "end", size=9.5, bold=True)
        for j, (key, col, nm) in enumerate((("exposureตลาดสัมบูรณ์เฉลี่ย", BLUE, "ตลาด"),
                                            ("exposureปัจจัยสองสัมบูรณ์เฉลี่ย", AMBER, "ปัจจัยสอง"))):
            yy = yb + j * 17
            out.append(f'<rect x="{x0}" y="{yy:.1f}" width="{max(sx(r[key])-x0, 2):.1f}" height="14" rx="2.5" fill="{col}" opacity="0.75"/>')
            _txt(out, sx(r[key]) + 7, yy + 11, f"{r[key]:.3f}", col, "start", size=9.5, bold=True)
    out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.4"/>')
    legend(out, [(BLUE, "exposure ต่อปัจจัยตลาด", ""), (AMBER, "exposure ต่อปัจจัยที่สอง", "")], x0, H - 30)
    _txt(out, Wd / 2, H - 10, "อ่านว่า: dollar-neutral ลดตลาดได้มาก แต่ไม่แตะปัจจัยที่สองเลย · มีแต่ factor-neutral ที่ลดทั้งคู่", INK, "middle", size=10, bold=True)
    out.append("</svg>")
    NUMS["nt-ladder"] = {r["ขั้น"][:12]: r["exposureตลาดสัมบูรณ์เฉลี่ย"] for r in rows}
    return "\n".join(out) + "\n" + _cap("ปัจจัยตลาดคือผลตอบแทน BTC ของจริง · หน้าตัดขวางเป็นเหรียญจำลองแปดตัวที่รู้เบต้าจริง จึงวัด exposure ที่เหลือได้ตรง ๆ")


@fig("statarb-neutrality.html", "nt-what-it-buys")
def fig_nt_what_it_buys():
    d = _nt(); rows = d["หางซ้าย"]["ผลของแต่ละขั้น"]
    Wd, H = 780, 300
    k = "ค่าสัมบูรณ์เฉลี่ยของกำไร5วันที่ตลาดขยับแรงสุด"
    first, last = rows[0][k], rows[-1][k]
    out = svg_open(Wd, H, f"แท่งแสดงขนาดการแกว่งของพอร์ตใน 5 วันที่ตลาดขยับแรงที่สุด ลดจาก {first} เหลือ {last} เมื่อไล่ขึ้นบันไดความเป็นกลาง", cls="fig")
    title(out, Wd, f"ความเป็นกลางซื้ออะไร — วันที่ตลาดเหวี่ยงแรง พอร์ตแกว่งน้อยลงครึ่งหนึ่ง",
          f"ค่าสัมบูรณ์เฉลี่ยของกำไร/ขาดทุน ใน 5 วันที่ตลาดขยับแรงที่สุด · {first:.2f}% → {last:.2f}%")
    x0, y0, w, h = 120, 66, 540, 150
    vmax = max(r[k] for r in rows) * 1.25
    bw = w / len(rows) - 44
    sy = lambda v: y0 + h - v / vmax * h
    for j in range(5):
        v = vmax * j / 4
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, x0 - 8, sy(v) + 4, f"{v:.1f}%", INK2, "end", size=9)
    cols = [RED, AMBER, BLUE, GREEN]
    for i, r in enumerate(rows):
        cx = x0 + i * (w / len(rows)) + 22
        v = r[k]
        out.append(f'<rect x="{cx:.1f}" y="{sy(v):.1f}" width="{bw:.1f}" height="{y0+h-sy(v):.1f}" rx="3" fill="{cols[i]}" opacity="0.75"/>')
        _txt(out, cx + bw / 2, sy(v) - 8, f"{v:.2f}%", cols[i], "middle", size=11, bold=True)
        for li, ln in enumerate(r["ขั้น"].split(" · ")):
            _txt(out, cx + bw / 2, y0 + h + 17 + li * 13, ln, INK, "middle", size=9, bold=li == len(r["ขั้น"].split(" · ")) - 1)
        _txt(out, cx + bw / 2, y0 + h + 46, f"วันแย่สุด {r['วันแย่ที่สุดเปอร์เซ็นต์']:.2f}%".replace("-", "−"), INK2, "middle", size=8.5)
    out.append(f'<line x1="{x0}" y1="{y0+h:.1f}" x2="{x0+w}" y2="{y0+h:.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    _txt(out, Wd / 2, H - 22, "นี่คือสิ่งที่ซื้อได้จริง — ไม่ใช่กำไรที่มากขึ้น แต่คือการไม่ถูกตลาดลากในวันที่ตลาดเหวี่ยง", INK, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, H - 6, "ขาดทุนสะสมสูงสุดไม่ได้ลดตาม — ความเป็นกลางตัดความเสี่ยงจากปัจจัย ไม่ได้ตัดความเสี่ยงทั้งหมด", INK2, "middle", size=9.5, italic=True)
    out.append("</svg>")
    NUMS["nt-what-it-buys"] = {"first": first, "last": last}
    return "\n".join(out) + "\n" + _cap("วัดบนพอร์ตที่ถือจริงวันต่อวัน · \"5 วันที่ตลาดขยับแรงที่สุด\" เลือกด้วยค่าสัมบูรณ์ของผลตอบแทนตลาดวันถัดไป")


@fig("statarb-neutrality.html", "nt-beta-error")
def fig_nt_beta_error():
    d = _nt(); B = d["ความผิดพลาดของเบต้า"]; R = d["exposureที่เหลือจริง"]
    rows = B["รายเหรียญ"]
    Wd, H = 780, 340
    out = svg_open(Wd, H, f"เบต้าจริงของเหรียญแปดตัวเทียบกับช่วงของเบต้าที่ประมาณได้จากหน้าต่าง {B['หน้าต่างที่ใช้ประมาณ']} วัน — คลาดเคลื่อนเฉลี่ย {B['ความคลาดเคลื่อนสัมบูรณ์เฉลี่ยทั้งแผง']} สูงสุด {B['ความคลาดเคลื่อนสัมบูรณ์สูงสุด']}", cls="fig")
    title(out, Wd, f"β ที่ประมาณได้จริง แกว่งกว้างกว่าที่คิดมาก — คลาดเคลื่อนเฉลี่ย {B['ความคลาดเคลื่อนสัมบูรณ์เฉลี่ยทั้งแผง']:.2f}",
          f"จุดม่วง = β จริง · แท่งเทา = ช่วงที่ OLS หน้าต่าง {B['หน้าต่างที่ใช้ประมาณ']} วันให้ได้ตลอดช่วงข้อมูล")
    x0, y0, w, h = 88, 66, 540, 186
    lo = min(min(r["เบต้าประมาณต่ำสุด"] for r in rows), 0) - 0.15
    hi = max(max(r["เบต้าประมาณสูงสุด"] for r in rows), 2.0) + 0.15
    sx = lambda v: x0 + (v - lo) / (hi - lo) * w
    for v in np.arange(np.ceil(lo * 2) / 2, hi, 0.5):
        out.append(f'<line x1="{sx(v):.1f}" y1="{y0}" x2="{sx(v):.1f}" y2="{y0+h}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, sx(v), y0 + h + 15, f"{v if abs(v) > 1e-9 else 0:g}", INK2, "middle", size=9)
    rh = h / len(rows)
    for i, r in enumerate(rows):
        cy = y0 + i * rh + rh / 2
        out.append(f'<rect x="{sx(r["เบต้าประมาณต่ำสุด"]):.1f}" y="{cy-6:.1f}" width="{sx(r["เบต้าประมาณสูงสุด"])-sx(r["เบต้าประมาณต่ำสุด"]):.1f}" height="12" rx="3" fill="{INK2}" opacity="0.22"/>')
        out.append(f'<line x1="{sx(r["เบต้าประมาณเฉลี่ย"]):.1f}" y1="{cy-8:.1f}" x2="{sx(r["เบต้าประมาณเฉลี่ย"]):.1f}" y2="{cy+8:.1f}" stroke="{BLUE}" stroke-width="2.4"/>')
        _dot(out, sx(r["เบต้าจริง"]), cy, PURPLE, 4.0)
        _txt(out, x0 - 10, cy + 4, r["เหรียญ"], INK, "end", size=9)
        _txt(out, x0 + w + 10, cy + 4, f"ผิด {r['ความคลาดเคลื่อนสัมบูรณ์เฉลี่ย']:.2f}",
             RED if r["ความคลาดเคลื่อนสัมบูรณ์เฉลี่ย"] >= 0.3 else INK2, "start", size=9,
             bold=r["ความคลาดเคลื่อนสัมบูรณ์เฉลี่ย"] >= 0.3)
    out.append(f'<line x1="{sx(0):.1f}" y1="{y0}" x2="{sx(0):.1f}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.2"/>')
    _txt(out, x0 + w / 2, y0 + h + 32, "ค่า β", INK2, "middle", size=9.5)
    legend(out, [(PURPLE, "β จริง", ""), (BLUE, "β ประมาณเฉลี่ย", ""), (INK2, "ช่วงที่ประมาณได้", "")], x0, H - 30)
    _txt(out, Wd / 2, H - 10, f"ผลที่ตามมา: \"beta-neutral\" ด้วย β ประมาณ ยังเหลือ exposure {R['exposureเหลือเมื่อใช้เบต้าประมาณ']:.3f} · ถ้ารู้ β จริงจะเหลือ {R['exposureเหลือถ้ารู้เบต้าจริง']:.3f} พอดี", RED, "middle", size=10.5, bold=True)
    out.append("</svg>")
    NUMS["nt-beta-error"] = {"mean_err": B["ความคลาดเคลื่อนสัมบูรณ์เฉลี่ยทั้งแผง"],
                             "max_err": B["ความคลาดเคลื่อนสัมบูรณ์สูงสุด"],
                             "resid": R["exposureเหลือเมื่อใช้เบต้าประมาณ"]}
    return "\n".join(out) + "\n" + _cap("β จริงรู้ได้เพราะหน้าตัดขวางเป็นข้อมูลจำลอง — ในงานจริงไม่มีทางรู้ จึงไม่มีทางรู้ว่าเหลือ exposure เท่าไรด้วย")


@fig("statarb-neutrality.html", "nt-decay")
def fig_nt_decay():
    d = _nt(); D = d["ความเร็วที่alphaเสื่อม"]
    hs = ["1 วัน", "2 วัน", "3 วัน", "5 วัน"]
    Wd, H = 780, 326
    F = [D["สัญญาณเร็ว"][k] for k in hs]; S = [D["สัญญาณช้า"][k] for k in hs]
    fast = [x["IC"] for x in F]; slow = [x["IC"] for x in S]
    n_out = sum(1 for x in S if x["หลุดฐาน"])
    out = svg_open(Wd, H, f"เส้น IC พร้อมแถบสองเท่าของความคลาดเคลื่อนมาตรฐาน ของสัญญาณสองแบบที่ระยะล่วงหน้า 1 ถึง 5 วัน — สัญญาณช้าหลุดแถบความสุ่มที่ {n_out} ระยะ ส่วนสัญญาณเร็วไม่หลุดเลยสักระยะ", cls="fig")
    title(out, Wd, f"สัญญาณช้าโผล่พ้นความสุ่มได้ {n_out} ระยะ — สัญญาณเร็วไม่ผ่านสักระยะเดียว",
          f"IC ± 2 SE เทียบกับผลตอบแทนส่วนเกินสะสม h วันข้างหน้า · แถบคลุมศูนย์ = ยังแยกจากความสุ่มไม่ได้")
    x0, y0, w, h = 78, 66, 560, 170
    lo = min(min(x["IC"] - 2 * x["SE"] for x in F + S), 0) - 0.03
    hi = max(x["IC"] + 2 * x["SE"] for x in F + S) + 0.04
    sx = lambda i: x0 + i / (len(hs) - 1) * w
    sy = lambda v: y0 + h - (v - lo) / (hi - lo) * h
    for v in np.arange(np.ceil(lo / 0.1) * 0.1, hi, 0.1):
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, x0 - 8, sy(v) + 4, f"{v:.2f}", INK2, "end", size=9)
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    for i, lab in enumerate(hs):
        _txt(out, sx(i), y0 + h + 16, lab, INK, "middle", size=9.5, bold=True)
    for rows_, col, dx in ((F, RED, -4), (S, GREEN, 4)):
        polyline(out, [(sx(i), sy(x["IC"])) for i, x in enumerate(rows_)], col, 2.6)
        for i, x in enumerate(rows_):
            lo_, hi_ = x["IC"] - 2 * x["SE"], x["IC"] + 2 * x["SE"]
            out.append(f'<line x1="{sx(i)+dx:.1f}" y1="{sy(lo_):.1f}" x2="{sx(i)+dx:.1f}" y2="{sy(hi_):.1f}" stroke="{col}" stroke-width="1.6" opacity="0.65"/>')
            for yy in (lo_, hi_):
                out.append(f'<line x1="{sx(i)+dx-3:.1f}" y1="{sy(yy):.1f}" x2="{sx(i)+dx+3:.1f}" y2="{sy(yy):.1f}" stroke="{col}" stroke-width="1.6" opacity="0.65"/>')
            if x["หลุดฐาน"]:
                out.append(f'<circle cx="{sx(i):.1f}" cy="{sy(x["IC"]):.1f}" r="5.2" fill="none" stroke="{PURPLE}" stroke-width="2"/>')
            _dot(out, sx(i), sy(x["IC"]), col, 3.2)
    _txt(out, sx(0) + 12, sy(fast[0]) + 20, f"t = {F[0]['tstat']:+.2f} — แถบยังคลุมศูนย์", RED, "start", size=9, bold=True)
    _txt(out, sx(3) - 12, sy(slow[3]) - 16, f"t = {S[3]['tstat']:+.2f} — หลุดฐาน", GREEN, "end", size=9.5, bold=True)
    _txt(out, sx(3) + 14, sy(0) - 6, "วงม่วง = หลุดฐาน", PURPLE, "end", size=8.5, bold=True)
    _txt(out, x0 + w / 2, y0 + h + 34, "ระยะล่วงหน้าที่ถือ", INK2, "middle", size=9.5)
    legend(out, [(RED, "สัญญาณเร็ว (residual เมื่อวาน)", ""), (GREEN, "สัญญาณช้า (residual เฉลี่ย 10 วัน)", "")], x0, H - 34)
    _txt(out, Wd / 2, H - 8, "สัญญาณที่เสื่อมเร็วบังคับให้เทรดเร็ว — และการเทรดเร็วคือสิ่งที่ต้องจ่ายค่าธรรมเนียม", INK, "middle", size=10, bold=True)
    out.append("</svg>")
    NUMS["nt-decay"] = {"fast1_t": F[0]["tstat"], "slow5_t": S[3]["tstat"], "n_out": n_out}
    return "\n".join(out) + "\n" + _cap("ทั้งสองสัญญาณคำนวณจากแผงเดียวกันและผ่าน factor-neutral เหมือนกัน — ต่างกันแค่ความยาวหน้าต่างที่ใช้อ่าน residual · SE จากการกระจายของ IC รายวัน ตามมาตรฐานเดียวกับบท IC")


@fig("statarb-neutrality.html", "nt-turnover")
def fig_nt_turnover():
    d = _nt(); T = d["turnoverControl"]
    fast, slow = T["สัญญาณเร็ว"], T["สัญญาณช้า"]
    gf, gs = fast["ที่ลอง"], slow["ที่ลอง"]
    Wd, H = 780, 340
    out = svg_open(Wd, H, f"เส้นกำไรสุทธิเทียบกับความเร็วปรับพอร์ต สำหรับสัญญาณสองแบบ — สัญญาณช้าให้กำไรสุทธิสูงกว่าที่ทุกความเร็ว และจุดที่ดีที่สุดอยู่ที่ {slow['ดีที่สุด']['ความเร็วปรับพอร์ต']}", cls="fig")
    title(out, Wd, "เทรดช้าลงไม่ได้ช่วยเสมอ — ช่วยเฉพาะเมื่อ alpha ทนพอจะรอ",
          f"กำไรสุทธิหลังต้นทุน เทียบกับ λ (สัดส่วนระยะทางที่เดินไปหาพอร์ตเป้าหมายต่อวัน) · ต้นทุนไป-กลับ {d['ข้อมูล']['ต้นทุนไปกลับbps']} bps")
    x0, y0, w, h = 78, 68, 500, 178
    lams = [g["ความเร็วปรับพอร์ต"] for g in gf]
    allv = [g["กำไรสุทธิเปอร์เซ็นต์"] for g in gf + gs]
    lo, hi = min(allv) - 0.6, max(allv) + 0.8
    sx = lambda lm: x0 + (1.0 - lm) / (1.0 - min(lams)) * w
    sy = lambda v: y0 + h - (v - lo) / (hi - lo) * h
    for v in np.arange(np.ceil(lo / 2) * 2, hi, 2):
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, x0 - 8, sy(v) + 4, f"{v:+.0f}%".replace("-", "−").replace("+0%", "0%"), INK2, "end", size=9)
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    for lm in (1.0, 0.6, 0.4, 0.2, 0.05):
        _txt(out, sx(lm), y0 + h + 16, f"{lm:g}", INK2, "middle", size=9)
    for grid_, col, nm, bst in ((gf, RED, "สัญญาณเร็ว", fast["ดีที่สุด"]), (gs, GREEN, "สัญญาณช้า", slow["ดีที่สุด"])):
        polyline(out, [(sx(g["ความเร็วปรับพอร์ต"]), sy(g["กำไรสุทธิเปอร์เซ็นต์"])) for g in grid_], col, 2.4)
        for g in grid_:
            _dot(out, sx(g["ความเร็วปรับพอร์ต"]), sy(g["กำไรสุทธิเปอร์เซ็นต์"]), col, 2.8)
        _dot(out, sx(bst["ความเร็วปรับพอร์ต"]), sy(bst["กำไรสุทธิเปอร์เซ็นต์"]), PURPLE, 5.2)
    _txt(out, sx(gs[2]["ความเร็วปรับพอร์ต"]), sy(slow["ดีที่สุด"]["กำไรสุทธิเปอร์เซ็นต์"]) - 12,
         f"ดีที่สุด {slow['ดีที่สุด']['กำไรสุทธิเปอร์เซ็นต์']:.2f}% ที่ λ = {slow['ดีที่สุด']['ความเร็วปรับพอร์ต']:g}", GREEN, "middle", size=9.5, bold=True)
    _txt(out, sx(0.8), sy(fast["ดีที่สุด"]["กำไรสุทธิเปอร์เซ็นต์"]) - 12,
         f"ดีที่สุด {fast['ดีที่สุด']['กำไรสุทธิเปอร์เซ็นต์']:.2f}%", RED, "middle", size=9.5, bold=True)
    _txt(out, x0, y0 + h + 34, "← เทรดเร็ว (λ = 1 ไปถึงเป้าทุกวัน)", INK2, "start", size=9)
    _txt(out, x0 + w, y0 + h + 34, "เทรดช้า (λ = 0.05 ขยับทีละ 5%) →", INK2, "end", size=9)
    bx = x0 + w + 22
    out.append(f'<rect x="{bx-8}" y="{y0-4}" width="{Wd-bx-4:.0f}" height="128" rx="8" fill="{GREEN}" opacity="0.07"/>')
    _txt(out, bx, y0 + 14, "turnover ต่อวัน", INK, "start", size=9.5, bold=True)
    _txt(out, bx, y0 + 32, f"เร็ว {gf[0]['turnoverเฉลี่ยต่อวัน']:.2f}", RED, "start", size=9.5, bold=True)
    _txt(out, bx, y0 + 47, f"ช้า {gs[0]['turnoverเฉลี่ยต่อวัน']:.2f}", GREEN, "start", size=9.5, bold=True)
    _txt(out, bx, y0 + 70, "ต้นทุนรวม", INK, "start", size=9.5, bold=True)
    _txt(out, bx, y0 + 88, f"เร็ว {gf[0]['ต้นทุนรวมเปอร์เซ็นต์']:.2f}%", RED, "start", size=9.5, bold=True)
    _txt(out, bx, y0 + 103, f"ช้า {gs[0]['ต้นทุนรวมเปอร์เซ็นต์']:.2f}%", GREEN, "start", size=9.5, bold=True)
    _txt(out, Wd / 2, H - 24, f"turnover ต่างกัน {gf[0]['turnoverเฉลี่ยต่อวัน']/gs[0]['turnoverเฉลี่ยต่อวัน']:.1f} เท่า · ต้นทุนต่อวันต่างกัน {gf[0]['ต้นทุนต่อวันเปอร์เซ็นต์']/gs[0]['ต้นทุนต่อวันเปอร์เซ็นต์']:.1f} เท่า — สัญญาณช้าจึงชนะที่กำไรสุทธิ", INK, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, H - 8, "และถ้าชะลอมากเกินไป สัญญาณช้าก็พังเหมือนกัน — มีจุดที่ดีที่สุดจริง ไม่ใช่ยิ่งช้ายิ่งดี", INK2, "middle", size=9.5, italic=True)
    out.append("</svg>")
    NUMS["nt-turnover"] = {"fast_best": fast["ดีที่สุด"]["กำไรสุทธิเปอร์เซ็นต์"],
                           "slow_best": slow["ดีที่สุด"]["กำไรสุทธิเปอร์เซ็นต์"],
                           "turn_fast": gf[0]["turnoverเฉลี่ยต่อวัน"], "turn_slow": gs[0]["turnoverเฉลี่ยต่อวัน"]}
    return "\n".join(out) + "\n" + _cap("ทั้งสองเส้นผ่าน factor-neutral เหมือนกัน · หลังผสมพอร์ตเมื่อวานกับเป้าหมายวันนี้แล้ว ต้องฉายให้เป็นกลางซ้ำอีกครั้งเสมอ เพราะ β̂ และ γ̂ เปลี่ยนทุกวัน")


# ── statarb: IC lab (Part XIII Alpha Discovery) — ทุกตัวเลขอ่านจาก docs/ic-figures.json ─────
def _ic():
    return _load("ic-figures.json")


@fig("statarb-ic-lab.html", "ic-vs-null")
def fig_ic_vs_null():
    d = _ic(); rows = d["สัญญาณ"]; nd = d["ข้อมูล"]["จำนวนวัน"]
    Wd, H = 780, 318
    out = svg_open(Wd, H, f"IC ของสัญญาณหกตัวบน BTC {nd} วัน วางบนแถบฐานจากความสุ่มของแต่ละตัว — ทุกตัวอยู่ในแถบฐานทั้งหมด จึงยังแยกจากความสุ่มไม่ได้", cls="fig")
    title(out, Wd, "IC ของทั้งหกสัญญาณตกอยู่ในแถบความสุ่มทั้งหมด — ยังไม่มีตัวไหนพิสูจน์ได้",
          f"BTC {nd} วัน · แถบเทา = ช่วงที่ความสุ่มล้วนให้ได้ 95% ของเวลา (กว้างไม่เท่ากันเพราะจำนวนวันใช้ได้ต่างกัน)")
    x0, y0, w, h = 210, 58, 470, 190
    lo, hi = -0.5, 0.5
    sx = lambda v: x0 + (v - lo) / (hi - lo) * w
    for v in (-0.4, -0.2, 0.0, 0.2, 0.4):
        out.append(f'<line x1="{sx(v):.1f}" y1="{y0}" x2="{sx(v):.1f}" y2="{y0+h}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, sx(v), y0 + h + 15, f"{v:+.1f}".replace("-", "−").replace("+0.0", "0"), INK2, "middle", size=9)
    bh = h / len(rows) - 10
    for i, r in enumerate(rows):
        y = y0 + i * (bh + 10) + 5
        a95 = r["ฐานสุ่ม"]["absที่95"]
        out.append(f'<rect x="{sx(-a95):.1f}" y="{y:.1f}" width="{sx(a95)-sx(-a95):.1f}" height="{bh:.1f}" rx="3" fill="{INK2}" opacity="0.13"/>')
        ic = r["IC1วัน"]
        col = RED if r["นอกฐาน"] else BLUE
        out.append(f'<line x1="{sx(ic):.1f}" y1="{y:.1f}" x2="{sx(ic):.1f}" y2="{y+bh:.1f}" stroke="{col}" stroke-width="3"/>')
        _txt(out, x0 - 10, y + bh / 2 + 4, r["สัญญาณ"], INK, "end", size=9.5, bold=True)
        _txt(out, sx(ic) - 6, y + bh / 2 + 4, f"{ic:+.3f}".replace("-", "−"), col, "end", size=9, bold=True)
        _txt(out, sx(a95) + 6, y + bh / 2 + 4, f"ฐาน ±{a95:.2f} · n = {r['จำนวนวัน']}", INK2, "start", size=8.5)
    out.append(f'<line x1="{sx(0):.1f}" y1="{y0}" x2="{sx(0):.1f}" y2="{y0+h}" stroke="{AXIS}" stroke-width="1.4"/>')
    _txt(out, Wd / 2, y0 + h + 36, "แท่งสีคือ IC ที่วัดได้ · แถบเทาคือสิ่งที่ \"ไม่มีสัญญาณเลย\" ให้ได้ — ไม่มีตัวไหนโผล่พ้นแถบ", INK, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, y0 + h + 54, "อ่านว่า: ยังสรุปไม่ได้ว่าใช้ได้ และยังสรุปไม่ได้ว่าใช้ไม่ได้ — ตัวอย่างน้อยเกินไปทั้งคู่", INK2, "middle", size=9.5, italic=True)
    out.append("</svg>")
    NUMS["ic-vs-null"] = {r["สัญญาณ"][:10]: r["IC1วัน"] for r in rows}
    return "\n".join(out) + "\n" + _cap(f"IC = Spearman rank correlation ระหว่างสัญญาณวันที่ t กับผลตอบแทนวันถัดไป · ฐานจากการสลับผลตอบแทน {d['วิธีวัด']['จำนวนรอบจำลองฐาน']:,} รอบ")


@fig("statarb-ic-lab.html", "ic-signal-corr")
def fig_ic_signal_corr():
    d = _ic(); C = d["สหสัมพันธ์ระหว่างสัญญาณ"]
    names = C["ชื่อสัญญาณ"]; ma = C["ค่าเฉลี่ยสัมบูรณ์ต่อสัญญาณ"]
    lut = {}
    for r in C["รายคู่"]:
        a, b = r["คู่"]; lut[(a, b)] = lut[(b, a)] = r["สหสัมพันธ์อันดับ"]
    hi, lo = C["สูงสุด"], C["ต่ำสุด"]
    Wd, H = 780, 372
    out = svg_open(Wd, H, f"ตารางสหสัมพันธ์อันดับระหว่างสัญญาณหกตัว · ค่าสูงสุด {hi['สหสัมพันธ์อันดับ']} ระหว่าง {hi['คู่'][0]} กับ {hi['คู่'][1]} · ต่ำสุด {lo['สหสัมพันธ์อันดับ']} — ทุกคู่เป็นบวกหมด แปลว่าหกสัญญาณไม่ใช่หกหลักฐานอิสระ", cls="fig")
    title(out, Wd, f"สัญญาณ \"หกตัว\" ซ้ำกันเองแทบทั้งหมด — สูงสุด {hi['สหสัมพันธ์อันดับ']:.2f}",
          "สหสัมพันธ์อันดับระหว่างสัญญาณเอง (ไม่เกี่ยวกับผลตอบแทน) · ทุกคู่เป็นบวก เพราะทุกตัวคำนวณจากราคาชุดเดียวกัน")
    n = len(names)
    cell, x0, y0 = 34, 300, 74
    for j, b in enumerate(names):
        _txt(out, x0 + j * cell + cell / 2, y0 - 8, f"{j+1}", INK2, "middle", size=9.5, bold=True)
    for i, a in enumerate(names):
        cy = y0 + i * cell
        _txt(out, x0 - 10, cy + cell / 2 + 4, f"{i+1}. {a}", INK, "end", size=9.5)
        for j, b in enumerate(names):
            cx = x0 + j * cell
            if i == j:
                out.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" fill="{GRID}"/>')
                continue
            v = lut[(a, b)]
            col = RED if v >= 0.9 else (AMBER if v >= 0.7 else (BLUE if v >= 0.4 else GREEN))
            out.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="2" fill="{col}" opacity="{0.14 + 0.62*abs(v):.2f}"/>')
            _txt(out, cx + cell / 2, cy + cell / 2 + 4, f"{v:.2f}".lstrip("0") if v < 1 else "1", INK, "middle", size=8.6, bold=abs(v) >= 0.9)
    gy = y0 + n * cell + 26
    _txt(out, x0 - 10, gy, "ซ้ำกับตัวอื่นเฉลี่ย:", INK2, "end", size=9)
    for i, a in enumerate(names):
        _txt(out, x0 + i * cell + cell / 2, gy, f"{ma[a]:.2f}".lstrip("0"), INK, "middle", size=9,
             bold=a == C["ตัวที่ซ้ำกับตัวอื่นน้อยที่สุด"])
    bx = 40
    _txt(out, bx, y0 + 6, f"คู่ที่ซ้ำกันที่สุด", RED, "start", size=9.5, bold=True)
    _txt(out, bx, y0 + 21, f"{hi['คู่'][0]} · {hi['คู่'][1]}", INK, "start", size=9)
    _txt(out, bx, y0 + 35, f"= {hi['สหสัมพันธ์อันดับ']:.2f} — แทบเป็นตัวเดียวกัน", RED, "start", size=9, bold=True)
    _txt(out, bx, y0 + 62, f"คู่ที่ต่างกันที่สุด", GREEN, "start", size=9.5, bold=True)
    _txt(out, bx, y0 + 77, f"{lo['คู่'][0]} · {lo['คู่'][1]}", INK, "start", size=9)
    _txt(out, bx, y0 + 91, f"= {lo['สหสัมพันธ์อันดับ']:.2f} — ยังเป็นบวกอยู่ดี", GREEN, "start", size=9, bold=True)
    _txt(out, bx, y0 + 122, "ผลที่ตามมา:", INK, "start", size=9.5, bold=True)
    for k, ln in enumerate(["ลองหกครั้ง ไม่เท่ากับ", "ลองหกครั้งอิสระ", "ฐานของ \"ตัวที่ดีที่สุด\"", "จึงต้องสลับลำดับเวลา", "ครั้งเดียวใช้กับทุกตัว"]):
        _txt(out, bx, y0 + 140 + k * 14, ln, INK2, "start", size=8.8)
    _txt(out, Wd / 2, H - 14, f"ตัวที่ซ้ำกับตัวอื่นน้อยที่สุดคือ \"{C['ตัวที่ซ้ำกับตัวอื่นน้อยที่สุด']}\" ({ma[C['ตัวที่ซ้ำกับตัวอื่นน้อยที่สุด']]:.2f}) — และเป็นตัวที่ IC แรงที่สุดด้วย", INK, "middle", size=10, bold=True)
    out.append("</svg>")
    NUMS["ic-signal-corr"] = {"hi": hi["สหสัมพันธ์อันดับ"], "lo": lo["สหสัมพันธ์อันดับ"],
                              "least": ma[C["ตัวที่ซ้ำกับตัวอื่นน้อยที่สุด"]]}
    return "\n".join(out) + "\n" + _cap("วัดระหว่างสัญญาณกันเองบนวันที่ทั้งสองตัวมีค่า · นี่คือเหตุผลที่ฐานของ \"ตัวที่ดีที่สุด\" ต้องคงโครงสร้างนี้ไว้ ไม่ใช่สลับแยกรายสัญญาณ")


@fig("statarb-ic-lab.html", "ic-selection")
def fig_ic_selection():
    d = _ic(); sel = d["ผลของการเลือกตัวที่ดีที่สุด"]; hs = d["การกระจายของmaxABSจากความสุ่ม"]
    edges, cnt = hs["ขอบช่อง"], hs["จำนวน"]
    Wd, H = 780, 300
    out = svg_open(Wd, H, f"ฮิสโทแกรมของ max|IC| จากข้อมูลสุ่มล้วนเมื่อลอง {sel['จำนวนสัญญาณที่ลอง']} สัญญาณ ค่าเฉลี่ย {sel['maxABSเฉลี่ยจากความสุ่ม']} ขณะที่ของจริงได้เพียง {sel['ของจริง']}", cls="fig")
    title(out, Wd, f"ลองหกสัญญาณแล้วหยิบตัวที่ดีที่สุด — ความสุ่มล้วนยังให้ max|IC| เฉลี่ย {sel['maxABSเฉลี่ยจากความสุ่ม']:.2f}",
          f"สลับลำดับเวลา {hs['จำนวนรอบ']:,} รอบ · รอบละครั้งเดียวใช้กับทั้ง {sel['จำนวนสัญญาณที่ลอง']} ตัว แล้วเก็บค่าสัมบูรณ์ที่ใหญ่ที่สุด · ของจริงได้ {sel['ของจริง']:.3f}")
    x0, y0, w, h = 60, 62, 660, 168
    lo, hi = edges[0], edges[-1]
    sx = lambda v: x0 + (v - lo) / (hi - lo) * w
    mx = max(cnt)
    sy = lambda c: y0 + h - c / mx * h
    for i, c in enumerate(cnt):
        a, b = edges[i], edges[i + 1]
        col = GREEN if b <= sel["ของจริง"] else INK2
        out.append(f'<rect x="{sx(a)+0.6:.1f}" y="{sy(c):.1f}" width="{sx(b)-sx(a)-1.2:.1f}" height="{sy(0)-sy(c):.1f}" fill="{col}" opacity="0.55"/>')
    for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        if lo <= v <= hi: _txt(out, sx(v), y0 + h + 15, f"{v:.1f}", INK2, "middle", size=9)
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.2"/>')
    for v, col, lab, dy in ((sel["ของจริง"], RED, f"ของจริง {sel['ของจริง']:.3f}", 0),
                            (sel["maxABSเฉลี่ยจากความสุ่ม"], PURPLE, f"ค่าเฉลี่ยจากความสุ่ม {sel['maxABSเฉลี่ยจากความสุ่ม']:.3f}", 16),
                            (sel["maxABSที่95จากความสุ่ม"], AMBER, f"95% ของความสุ่ม {sel['maxABSที่95จากความสุ่ม']:.3f}", 32)):
        out.append(f'<line x1="{sx(v):.1f}" y1="{y0}" x2="{sx(v):.1f}" y2="{y0+h}" stroke="{col}" stroke-width="2" stroke-dasharray="5 3"/>')
        _txt(out, sx(v) + 6, y0 + 14 + dy, lab, col, "start", size=9.5, bold=True)
    _txt(out, x0 + w / 2, y0 + h + 34, "max|IC| ที่ได้จากข้อมูลที่ไม่มีความสัมพันธ์จริงเลย", INK2, "middle", size=9.5)
    _txt(out, Wd / 2, y0 + h + 56, f"ของจริงอยู่ที่เปอร์เซ็นไทล์ {sel['เปอร์เซ็นไทล์ของของจริง']:.1f} ของความสุ่ม — เล็กกว่าที่ความสุ่มให้ตามปกติด้วยซ้ำ", RED, "middle", size=10.5, bold=True)
    out.append("</svg>")
    NUMS["ic-selection"] = {"mean_null": sel["maxABSเฉลี่ยจากความสุ่ม"], "obs": sel["ของจริง"], "pct": sel["เปอร์เซ็นไทล์ของของจริง"]}
    return "\n".join(out) + "\n" + _cap("ยิ่งลองหลายสัญญาณ ยิ่งได้ค่าสูงโดยไม่ต้องมีสัญญาณจริง — ฐานที่ถูกจึงต้องเป็นฐานของ \"ตัวที่ดีที่สุด\" ไม่ใช่ฐานของตัวเดียว · "
                                        "สลับลำดับเวลาครั้งเดียวต่อรอบแล้วใช้กับทุกสัญญาณ เพื่อคงความซ้ำกันระหว่างสัญญาณไว้ในฐานด้วย")


@fig("statarb-ic-lab.html", "ic-samplesize")
def fig_ic_samplesize():
    d = _ic(); cur = d["เส้นขนาดตัวอย่าง"]; best = d["สัญญาณที่ดีที่สุด"]
    yr = d["กฎพื้นฐานของการจัดการเชิงรุก"]["ของสัญญาณที่ดีที่สุด"]["วันต่อปีของสินทรัพย์เดียว"]
    ics, ns = cur["IC"], cur["จำนวนวันที่ต้องใช้"]
    have = best["จำนวนวัน"]
    # จำนวนวันที่ต้องใช้ "ที่ IC ที่วัดได้จริง" — อ่านจากตารางใน JSON ไม่ใช่ปัดไปจุดใกล้ ๆ บนเส้น
    need = next(v for k, v in d["ขนาดตัวอย่างที่ต้องใช้"].items() if "ที่วัดได้" in k)
    Wd, H = 780, 300
    out = svg_open(Wd, H, f"เส้นจำนวนวันที่ต้องใช้เพื่อแยก IC ออกจากศูนย์ ยิ่ง IC เล็กยิ่งต้องใช้วันมากแบบกำลังสอง ที่ IC {abs(best['IC']):.3f} ต้องใช้ราว {need:,} วัน ขณะที่มีอยู่ {have} วัน", cls="fig")
    title(out, Wd, f"IC เล็กลงครึ่งหนึ่ง ต้องใช้วันมากขึ้นสี่เท่า — ที่ IC {abs(best['IC']):.3f} ต้องใช้ราว {need:,} วัน",
          f"{cur['สูตร']} · ข้อมูลที่มีจริง {have} วัน จึงห่างจากที่ต้องใช้อยู่ราว {need/have:.0f} เท่า")
    x0, y0, w, h = 66, 60, 650, 175
    lo, hi = 0.03, 0.42
    ylo, yhi = 1.5, 4.2      # log10 ของจำนวนวัน
    sx = lambda v: x0 + (v - lo) / (hi - lo) * w
    sy = lambda n: y0 + h - (np.log10(n) - ylo) / (yhi - ylo) * h
    for e, lab in ((2, "100 วัน"), (3, "1,000 วัน"), (4, "10,000 วัน")):
        out.append(f'<line x1="{x0}" y1="{sy(10**e):.1f}" x2="{x0+w}" y2="{sy(10**e):.1f}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, x0 - 8, sy(10 ** e) + 4, lab, INK2, "end", size=9)
    for v in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40):
        _txt(out, sx(v), y0 + h + 15, f"{v:.2f}", INK2, "middle", size=9)
    polyline(out, [(sx(a), sy(b)) for a, b in zip(ics, ns)], BLUE, 2.6)
    out.append(f'<line x1="{x0}" y1="{sy(have):.1f}" x2="{x0+w}" y2="{sy(have):.1f}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 3"/>')
    _txt(out, x0 + 8, sy(have) - 7, f"ข้อมูลที่มีจริง {have} วัน", RED, "start", size=9.5, bold=True)
    _dot(out, sx(abs(best["IC"])), sy(need))
    _txt(out, sx(abs(best["IC"])) + 10, sy(need) - 20, f"IC {abs(best['IC']):.3f} → ต้องใช้ {need:,} วัน", PURPLE, "start", size=9.5, bold=True)
    _txt(out, sx(abs(best["IC"])) + 10, sy(need) - 6, f"≈ {need/yr:.1f} ปีตามปฏิทิน", PURPLE, "start", size=9)
    _txt(out, x0 + w / 2, y0 + h + 34, "ขนาดของ IC ที่อยากแยกออกจากศูนย์", INK2, "middle", size=9.5)
    _txt(out, Wd / 2, y0 + h + 56, "นี่คือเหตุผลที่ IC เล็ก ๆ ต้องใช้ข้อมูลมหาศาล — ไม่ใช่เพราะสูตรยาก แต่เพราะเสียงรบกวนดังกว่าสัญญาณมาก", INK, "middle", size=10, bold=True)
    out.append("</svg>")
    NUMS["ic-samplesize"] = {"need": need, "have": have}
    return "\n".join(out) + "\n" + _cap(f"power calculation ตระกูลเดียวกับ nq-tool-samplesize และบท edge เสื่อม (ที่นั่นตัวส่วนเป็นส่วนต่างอัตราชนะ ที่นี่เป็น IC) · "
                                        f"z_α = {d['โอกาสที่การทดสอบจะจับได้']['zที่ใช้ตัด']} · z_β = 1.2816 (power 90%) · หนึ่งปีของ BTC = {yr} วันตามปฏิทิน")


@fig("statarb-ic-lab.html", "ic-tercile")
def fig_ic_tercile():
    d = _ic(); T = d["กลุ่มสามส่วนของสัญญาณที่ดีที่สุด"]; best = d["สัญญาณที่ดีที่สุด"]
    gs = T["กลุ่ม"]
    Wd, H = 780, 290
    out = svg_open(Wd, H, f"แท่งผลตอบแทนวันถัดไปเฉลี่ยของสามกลุ่มที่แบ่งตาม {best['ชื่อ']} กลุ่มสัญญาณสูงสุดกลับให้ผลตอบแทนติดลบ ส่วนต่างสูงสุดลบต่ำสุดคือ {T['ส่วนต่างสูงสุดลบต่ำสุดเปอร์เซ็นต์']}%", cls="fig")
    title(out, Wd, f"แบ่งวันตาม \"{best['ชื่อ']}\" เป็นสามกลุ่ม — กลุ่มสัญญาณแรงที่สุดกลับได้ผลตอบแทนติดลบ",
          f"ผลตอบแทนวันถัดไปเฉลี่ยของแต่ละกลุ่ม · แต่ละกลุ่มมีแค่ 12–13 วัน จึงยังไม่ใช่หลักฐาน")
    x0, y0, w, h = 130, 62, 520, 150
    vals = [g["ผลตอบแทนเฉลี่ยเปอร์เซ็นต์"] for g in gs]
    lo, hi = min(min(vals) - 0.3, -0.5), max(max(vals) + 0.4, 1.2)
    sy = lambda v: y0 + h - (v - lo) / (hi - lo) * h
    for v in np.arange(np.ceil(lo * 2) / 2, hi, 0.5):
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, x0 - 8, sy(v) + 4, f"{v:+.1f}%".replace("-", "−").replace("+0.0", "0.0"), INK2, "end", size=9)
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    bw = w / len(gs) - 46
    for i, g in enumerate(gs):
        cx = x0 + i * (w / len(gs)) + 23
        v = g["ผลตอบแทนเฉลี่ยเปอร์เซ็นต์"]
        col = GREEN if v > 0 else RED
        out.append(f'<rect x="{cx:.1f}" y="{sy(max(v, 0)):.1f}" width="{bw:.1f}" height="{abs(sy(v)-sy(0)):.1f}" rx="3" fill="{col}" opacity="0.72"/>')
        _txt(out, cx + bw / 2, sy(v) + (-7 if v > 0 else 15), f"{v:+.2f}%".replace("-", "−"), col, "middle", size=11, bold=True)
        _txt(out, cx + bw / 2, y0 + h + 17, f"สัญญาณ{g['กลุ่ม']}", INK, "middle", size=9.5, bold=True)
        _txt(out, cx + bw / 2, y0 + h + 31, f"n = {g['จำนวนวัน']} วัน", INK2, "middle", size=9)
    _txt(out, Wd / 2, y0 + h + 56, f"ส่วนต่างกลุ่มสูงสุด − ต่ำสุด = {T['ส่วนต่างสูงสุดลบต่ำสุดเปอร์เซ็นต์']:+.2f}% ต่อวัน — ติดลบแปลว่าต้องเทรดกลับทางจากที่สัญญาณบอก".replace("-", "−"), RED, "middle", size=10.5, bold=True)
    _txt(out, Wd / 2, y0 + h + 74, f"เทรดตามทิศที่ถูก กำไรขั้นต้น {T['กำไรขั้นต้นตามทิศที่ถูกเปอร์เซ็นต์']:.2f}% ต่อวัน · หักต้นทุน {T['ต้นทุนไปกลับเปอร์เซ็นต์']}% เหลือ {T['เหลือหลังต้นทุนเปอร์เซ็นต์']:+.2f}% — ยังอยู่ในช่วงที่ความสุ่มให้ได้ จึงเชื่อไม่ได้", INK2, "middle", size=9.5, italic=True)
    out.append("</svg>")
    NUMS["ic-tercile"] = {"spread": T["ส่วนต่างสูงสุดลบต่ำสุดเปอร์เซ็นต์"], "gross": T["กำไรขั้นต้นตามทิศที่ถูกเปอร์เซ็นต์"], "after_cost": T["เหลือหลังต้นทุนเปอร์เซ็นต์"]}
    return "\n".join(out) + "\n" + _cap(f"แบ่งสามกลุ่มเท่า ๆ กันตามค่าสัญญาณ แล้วดูผลตอบแทนวันถัดไป · ต้นทุนไป-กลับ {T['ต้นทุนไปกลับเปอร์เซ็นต์']}% ชุดเดียวกับที่ \"มิน\" ใช้ทั้งเล่ม")


@fig("statarb-ic-lab.html", "ic-decay")
def fig_ic_decay():
    d = _ic(); rows = d["สัญญาณ"]
    hs = ["1 วัน", "3 วัน", "5 วัน", "10 วัน"]
    last = hs[-1]
    out_n = sum(1 for r in rows if r["ทุกhorizon"].get(last, {}).get("นอกฐาน"))
    neffs = [r["ทุกhorizon"][last]["จำนวนวันอิสระโดยประมาณ"] for r in rows if last in r["ทุกhorizon"]]
    Wd, H = 780, 352
    out = svg_open(Wd, H, f"เส้น IC ของสัญญาณหกตัวที่ระยะล่วงหน้า 1 3 5 และ 10 วัน · ที่ 10 วันมี {out_n} ใน {len(rows)} ตัวที่ IC ดิ่งจนหลุดแถบฐาน พร้อมกันทั้งหมด ทั้งที่จำนวนวันอิสระเหลือเพียง {min(neffs)} ถึง {max(neffs)} วัน", cls="fig")
    title(out, Wd, f"ยืดระยะเป็น 10 วัน แล้ว {out_n} ใน {len(rows)} ตัว \"ผ่าน\" พร้อมกัน — นั่นคืออาการว่าการทดสอบพัง",
          f"ไม่ใช่หลักฐาน {out_n} ชิ้น แต่เป็นชิ้นเดียวนับซ้ำ — สัญญาณซ้ำกันเองสูงถึง {d['สหสัมพันธ์ระหว่างสัญญาณ']['สูงสุด']['สหสัมพันธ์อันดับ']:.2f} และวัดเหตุการณ์เดียวกัน")
    x0, y0, w, h = 62, 62, 505, 190
    lo, hi = -0.85, 0.32
    sx = lambda i: x0 + i / (len(hs) - 1) * w
    sy = lambda v: y0 + h - (v - lo) / (hi - lo) * h
    for v in (-0.8, -0.6, -0.4, -0.2, 0.0, 0.2):
        out.append(f'<line x1="{x0}" y1="{sy(v):.1f}" x2="{x0+w}" y2="{sy(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        _txt(out, x0 - 8, sy(v) + 4, f"{v:+.1f}".replace("-", "−").replace("+0.0", "0"), INK2, "end", size=9)
    out.append(f'<line x1="{x0}" y1="{sy(0):.1f}" x2="{x0+w}" y2="{sy(0):.1f}" stroke="{AXIS}" stroke-width="1.4"/>')
    for i, lab in enumerate(hs):
        _txt(out, sx(i), y0 + h + 16, lab, INK, "middle", size=9.5, bold=True)
    _txt(out, x0 + w / 2, y0 + h + 32, "ระยะล่วงหน้าที่ใช้วัด IC", INK2, "middle", size=9)
    cols = [BLUE, RED, GREEN, AMBER, PURPLE, INK2]
    for j, r in enumerate(rows):
        c = cols[j % len(cols)]
        pts = [(sx(i), sy(r["ทุกhorizon"][lab]["IC"])) for i, lab in enumerate(hs) if lab in r["ทุกhorizon"]]
        polyline(out, pts, c, 1.8, shadow=False)
        for k, (px_, py_) in enumerate(pts):
            ring = hs[k] == last and r["ทุกhorizon"][last]["นอกฐาน"]
            out.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="{4.6 if ring else 2.6:.1f}" fill="{c}"'
                       + (f' stroke="{RED}" stroke-width="2"/>' if ring else "/>"))
    legend(out, [(cols[j % len(cols)], r["สัญญาณ"], "") for j, r in enumerate(rows[:3])], x0, H - 28)
    legend(out, [(cols[(j + 3) % len(cols)], r["สัญญาณ"], "") for j, r in enumerate(rows[3:])], x0, H - 10)
    bx = x0 + w + 22
    out.append(f'<rect x="{bx-8}" y="{y0-4}" width="{Wd-bx-6:.0f}" height="196" rx="8" fill="{RED}" opacity="0.06"/>')
    _txt(out, bx, y0 + 14, f"ที่ 10 วัน: {out_n} ใน {len(rows)} ตัว", RED, "start", size=10, bold=True)
    _txt(out, bx, y0 + 30, "หลุดแถบฐานพร้อมกัน", RED, "start", size=10, bold=True)
    for k, line in enumerate(["ผลตอบแทน 10 วันของ", "วันติดกันซ้อนทับกัน 9 ใน 10",
                              f"วันอิสระจริงเหลือ {min(neffs)}–{max(neffs)} วัน", "",
                              "การสลับป้ายทำลายการ", "ซ้อนทับนั้นทิ้ง แถบฐาน", "จึงแคบเกินจริง"]):
        if line:
            _txt(out, bx, y0 + 54 + k * 14, line, INK, "start", size=8.8)
    _txt(out, bx, y0 + 162, "วงแดง = หลุดฐาน", RED, "start", size=8.5, bold=True)
    _txt(out, bx, y0 + 176, "(ที่ไม่ควรเชื่อ)", INK2, "start", size=8.5)
    _txt(out, Wd / 2, y0 + h + 54, "อ่านว่า: ที่ 1 วันไม่มีตัวไหนผ่าน · พอยืดระยะจนตัวอย่างซ้อนทับ เกือบทุกตัวผ่าน — การทดสอบเปลี่ยน ไม่ใช่สัญญาณเปลี่ยน", INK, "middle", size=10, bold=True)
    out.append("</svg>")
    NUMS["ic-decay"] = {"out_at_10": out_n, "n_signals": len(rows), "neff_lo": min(neffs), "neff_hi": max(neffs)}
    return "\n".join(out) + "\n" + _cap("ทุกเส้นคำนวณจากราคาชุดเดียวกัน · แถบฐานของแต่ละระยะได้จากการสลับผลตอบแทนล่วงหน้าของระยะนั้น ซึ่งเป็นฐานที่แคบเกินจริงเมื่อผลตอบแทนซ้อนทับกัน")





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
    for nm, kind, got, lim in WIDE:  # หัวภาพ/คำโปรยที่ยาวเกินกรอบ — ล้นขอบเวลาเรนเดอร์จริง
        print(f"❌ {nm}: {kind}ยาวเกินกรอบ ~{got:.0f}px (พื้นที่ {lim:.0f}px) — ตัดข้อความให้สั้นลง"); bad += 1
    print(f"ภาพ {len(FIGS)} ชิ้น · ปัญหา {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
