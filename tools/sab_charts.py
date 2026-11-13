#!/usr/bin/env python3
"""วาดกราฟ SVG inline ลงบท docs/sab-*.html จาก docs/sab-figures.json (แบบ nq_charts.py) + เติมค่าในตาราง

ในบทวางตัวคั่นคู่แล้วรันสคริปต์ (รันซ้ำได้ — แทนที่เฉพาะของระหว่างตัวคั่น):
    <!--CHART:sab-two-pockets--><!--/CHART:sab-two-pockets-->        → SVG + คำบรรยายพร้อมป้ายที่มา
    <!--DATA:ch04--><!--/DATA:ch04-->                                → <script type="application/json"> ของคีย์นั้น (ให้เครื่องมือ/JS อ่าน)
    <td data-key="ch04.ต้องโอน"></td>                                  → เติมค่าจาก JSON (--fill · ใบมิน · บัตร · 📒)

    python3 tools/sab_charts.py              # วาดกราฟ + DATA ทุกหน้า sab-*
    python3 tools/sab_charts.py --fill       # + เติม data-key
    python3 tools/sab_charts.py --check      # ไม่เขียน: รายงานตัวคั่นที่ไม่รู้จัก/หน้าที่จะเปลี่ยน (exit 1 ถ้าต้องรันใหม่)
    python3 tools/sab_charts.py --list       # คีย์กราฟที่มี vs ที่แผนกำหนด (★ 31 · ☆ 12)
    python3 tools/sab_charts.py --selftest

สีตามความหมาย (knowledge-book visual-guide): เขียว = กำไร · แดง = ขาดทุน · ม่วง = จุดสำคัญ · เทา = บริบท
ตัวสร้างทั่วไป 5 ตัว: bars · waterfall · lines · steps · dots + ฟังก์ชันกลาง slip_strip() (แถบผล) และ ladder_bars() (บันได)
ตัวคั่นที่อยู่ใน <script>/<style> ไม่ถูกแตะ
"""

import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402

FONT = 'font-family="Sarabun,sans-serif"'
C = {"green": "#16a34a", "red": "#dc2626", "purple": "#7c3aed", "blue": "#2563eb", "amber": "#d97706",
     "grey": "#9ca3af", "ink": "#374151", "muted": "#6b7280", "grid": "#f3f4f6", "axis": "#d1d5db"}
SRC = {"สอน": "🔢 ตัวเลขสมมติเพื่อสอน", "จำลอง": "🎲 จำลอง (ผลนิ่งเมื่อสุ่มใหม่ 30 ชุด)", "จริง": "📡 ข้อมูลจริง (สแนปช็อต)",
       "แนวคิด": "🔢 ภาพแนวคิด ไม่ใช่ข้อมูล"}

PLANNED_STAR = ["sab-converge", "sab-cost-roundtrip", "sab-tail", "sab-shape-strips", "sab-ledger-bars", "sab-two-pockets",
                "sab-buffer-line", "sab-carry-ladder", "sab-crowding-ladder", "sab-hold-or-close", "sab-carry-strip",
                "sab-funding-paths", "sab-hedge-compare", "sab-beta-count", "sab-corr-vs-rope", "sab-formation-test",
                "sab-selection-bias", "sab-seed-spread", "sab-pair-legs", "sab-cost-steps", "sab-exit-paths",
                "sab-pair-strip", "sab-paths-fan", "sab-mult-table", "sab-pause-timeline", "sab-moving-mean",
                "sab-pnl-bridge", "sab-fill-timeline", "sab-capacity-curve", "sab-shape-gallery", "sab-drawdown"]
PLANNED_OPT = ["sab-orderbook", "sab-basis-time", "sab-one-leg", "sab-capital-tradeoff", "sab-settlement-gap",
               "sab-funding-rounds", "sab-stress", "sab-decision-ladder", "sab-first-passage", "sab-tries-luck",
               "sab-netting", "sab-crowded-unwind"]


# ───────────────────────── ส่วนประกอบพื้นฐาน ─────────────────────────

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def text(x, y, s, size=11.5, fill=None, anchor="start", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{fill or C["muted"]}"{w} {FONT}>{esc(s)}</text>')


def wrap(w, h, alt, parts, cap, src):
    """SVG + คำบรรยาย · ป้ายที่มา (W16) ขึ้นต้นคำบรรยายเสมอ"""
    return (f'<div class="figw"><svg class="fig" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(alt)}">\n' + "\n".join(parts) +
            f'\n</svg></div>\n<div class="cap">{SRC[src]} · {cap}</div>')


class Frame:
    """แกน y เชิงเส้น (รองรับค่าลบ) บนพื้นที่ L..W-R × T..Bm"""

    def __init__(self, lo, hi, W=760, H=320, L=64, R=24, T=56, Bm=250, pad=0.12):
        span = (hi - lo) or 1
        self.lo, self.hi = min(lo, 0) - (span * pad if lo < 0 else 0), hi + span * pad
        self.W, self.H, self.L, self.R, self.T, self.Bm = W, H, L, R, T, Bm

    def y(self, v):
        return self.Bm - (v - self.lo) / (self.hi - self.lo) * (self.Bm - self.T)

    def grid(self, ticks, unit=""):
        out = []
        for g in ticks:
            if self.lo <= g <= self.hi:
                yy = self.y(g)
                out.append(f'<line x1="{self.L}" y1="{yy:.1f}" x2="{self.W - self.R}" y2="{yy:.1f}" '
                           f'stroke="{C["axis"] if g == 0 else C["grid"]}" stroke-width="{1.5 if g == 0 else 1}"/>')
                out.append(text(self.L - 8, yy + 4, f"{B.fmt(g)}{unit}", 11, C["grey"], "end"))
        return out


def nice_ticks(lo, hi, n=5):
    span = (max(hi, 0) - min(lo, 0)) or 1
    raw = span / n
    mag = 10 ** len(str(int(raw))) / 10 if raw >= 1 else 10 ** -len(f"{raw:.10f}".split(".")[1].rstrip("0"))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=raw)
    step = int(step) if step >= 1 else step
    k0 = int(min(lo, 0) // step)
    return [round(k * step, 6) if step < 1 else int(k * step) for k in range(k0, k0 + n + 3)
            if min(lo, 0) - step <= k * step <= max(hi, 0) + step]


def bars(cats, values, title, unit="", colors=None, labels=None, W=760, H=320):
    """แท่งเดียวต่อหมวด · สีตามเครื่องหมาย (เขียว/แดง) ถ้าไม่กำหนด"""
    f = Frame(min(values + [0]), max(values + [0]), W, H)
    out = f.grid(nice_ticks(min(values), max(values)), unit)
    gw = (W - f.L - f.R) / len(cats)
    bw = min(64, gw * 0.55)
    for i, (c, v) in enumerate(zip(cats, values)):
        cx = f.L + gw * i + gw / 2
        y0, y1 = f.y(0), f.y(v)
        col = (colors[i] if colors else (C["green"] if v >= 0 else C["red"]))
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{min(y0, y1):.1f}" width="{bw:.1f}" height="{abs(y1 - y0):.1f}" rx="3" fill="{col}"/>')
        lab = labels[i] if labels else f"{B.fmt(v)}{unit}"
        out.append(text(cx, (y1 - 7) if v >= 0 else (y1 + 16), lab, 12, col, "middle", 700))
        out.append(text(cx, f.Bm + 18, c, 11.5, C["muted"], "middle"))
    out.append(text(f.L, f.T - 26, title, 13, C["ink"], weight=700))
    return out


def waterfall(steps, title, unit="", W=760, H=320):
    """steps = [(ชื่อ, ค่า, 'start'|'delta'|'total')] — แท่งลอยสะสม"""
    run, tops = 0, []
    for _, v, kind in steps:
        if kind == "delta":
            tops += [run, run + v]
            run += v
        else:
            run = v
            tops += [0, v]
    f = Frame(min(tops), max(tops), W, H)
    out = f.grid(nice_ticks(min(tops), max(tops)), unit)
    gw = (W - f.L - f.R) / len(steps)
    bw = min(70, gw * 0.6)
    run, prev_x = 0, None
    for i, (name, v, kind) in enumerate(steps):
        cx = f.L + gw * i + gw / 2
        if kind == "delta":
            a, b = run, run + v
            col = C["green"] if v >= 0 else C["red"]
            lab = ("+" if v > 0 else "") + B.fmt(v) + unit
            run = b
        else:
            a, b = 0, v
            col = C["purple"] if kind == "total" else C["blue"]
            lab = B.fmt(v) + unit
            run = v
        ya, yb = f.y(a), f.y(b)
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{min(ya, yb):.1f}" width="{bw:.1f}" height="{max(1, abs(yb - ya)):.1f}" rx="2" fill="{col}"/>')
        out.append(text(cx, min(ya, yb) - 7, lab, 12, col, "middle", 700))
        out.append(text(cx, f.Bm + 18, name, 11, C["muted"], "middle"))
        if prev_x is not None:
            out.append(f'<line x1="{prev_x:.1f}" y1="{f.y(a if kind == "delta" else run):.1f}" x2="{cx - bw / 2:.1f}" '
                       f'y2="{f.y(a if kind == "delta" else run):.1f}" stroke="{C["axis"]}" stroke-dasharray="3 3"/>')
        prev_x = cx + bw / 2
    out.append(text(f.L, f.T - 26, title, 13, C["ink"], weight=700))
    return out


def lines(xs, series, title, unit="", xlabel="", W=760, H=320, marks=None, xticks=None, every=1):
    """series = [(ชื่อ, [y], สี)] · marks = [(x, y, ข้อความ)] จุดสำคัญสีม่วง"""
    ys = [v for _, s, _ in series for v in s if v is not None]
    f = Frame(min(ys), max(ys), W, H)
    out = f.grid(nice_ticks(min(ys), max(ys)), unit)
    x0, x1 = min(xs), max(xs)
    X = lambda x: f.L + (x - x0) / ((x1 - x0) or 1) * (W - f.L - f.R)  # noqa: E731
    for name, s, col in series:
        keep = [(x, v) for i, (x, v) in enumerate(zip(xs, s)) if v is not None and (i % every == 0 or i == len(xs) - 1)]
        pts = " ".join(f"{X(x):.1f},{f.y(v):.1f}" for x, v in keep)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linejoin="round"/>')
    for x, y, lab in marks or []:
        out.append(f'<circle cx="{X(x):.1f}" cy="{f.y(y):.1f}" r="4.5" fill="{C["purple"]}"/>')
        right = X(x) > W * 0.7
        out.append(text(X(x) + (-8 if right else 8), f.y(y) - 8, lab, 11.5, C["purple"], "end" if right else "start", 700))
    lx = f.L
    for name, _, col in series:
        out.append(f'<rect x="{lx}" y="{f.T - 16}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 6, name, 11.5, C["muted"]))
        lx += 24 + 7.5 * len(name)
    out.append(text(f.L, f.T - 30, title, 13, C["ink"], weight=700))
    if xlabel:
        out.append(text((f.L + W - f.R) / 2, f.Bm + 36, xlabel, 12, C["muted"], "middle"))
    # ป้ายแกน x: ส่ง xticks = [(x, ป้าย)] เมื่อค่า x ไม่ได้อยู่ใน JSON (ป้ายอัตโนมัติจะกลายเป็น "เลขลอย")
    for x, lab in (xticks if xticks is not None else [(x, B.fmt(x)) for x in xs[:: max(1, len(xs) // 8)]]):
        out.append(text(X(x), f.Bm + 16, lab, 10.5, C["grey"], "middle"))
    return out


def steps(xs, ys, title, unit="", xlabel="", W=760, H=320, col=None):
    """เส้นทางขั้นบันได (เช่น equity ที่เปลี่ยนเป็นช่วง ๆ)"""
    f = Frame(min(ys), max(ys), W, H)
    out = f.grid(nice_ticks(min(ys), max(ys)), unit)
    x0, x1 = min(xs), max(xs)
    X = lambda x: f.L + (x - x0) / ((x1 - x0) or 1) * (W - f.L - f.R)  # noqa: E731
    d = f"M{X(xs[0]):.1f},{f.y(ys[0]):.1f}"
    for i in range(1, len(xs)):
        d += f" H{X(xs[i]):.1f} V{f.y(ys[i]):.1f}"
    out.append(f'<path d="{d}" fill="none" stroke="{col or C["blue"]}" stroke-width="2.2"/>')
    out.append(text(f.L, f.T - 26, title, 13, C["ink"], weight=700))
    if xlabel:
        out.append(text((f.L + W - f.R) / 2, f.Bm + 36, xlabel, 12, C["muted"], "middle"))
    return out


def dots(points, title, xlabel="", ylabel="", W=760, H=320, hline=None):
    """points = [(x, y, สี)] · hline = (y, ข้อความ) เส้นอ้างอิง"""
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    f = Frame(min(ys + ([hline[0]] if hline else [])), max(ys + ([hline[0]] if hline else [])), W, H)
    out = f.grid(nice_ticks(min(ys), max(ys)))
    x0, x1 = min(xs), max(xs)
    X = lambda x: f.L + (x - x0) / ((x1 - x0) or 1) * (W - f.L - f.R)  # noqa: E731
    if hline:
        out.append(f'<line x1="{f.L}" y1="{f.y(hline[0]):.1f}" x2="{W - f.R}" y2="{f.y(hline[0]):.1f}" '
                   f'stroke="{C["purple"]}" stroke-dasharray="5 4" stroke-width="1.5"/>')
        out.append(text(W - f.R, f.y(hline[0]) - 6, hline[1], 11.5, C["purple"], "end", 700))
    for x, y, col in points:
        out.append(f'<circle cx="{X(x):.1f}" cy="{f.y(y):.1f}" r="3.2" fill="{col}" fill-opacity=".75"/>')
    out.append(text(f.L, f.T - 26, title, 13, C["ink"], weight=700))
    if xlabel:
        out.append(text((f.L + W - f.R) / 2, f.Bm + 36, xlabel, 12, C["muted"], "middle"))
    if ylabel:
        out.append(text(f.L - 46, f.T - 8, ylabel, 11, C["muted"]))
    return out


def slip_strip(outcomes, title, W=760, H=200, label_every=None):
    """แถบผล: ผลทีละไม้เรียงตามเวลา (เขียวขึ้น/แดงลง) + ยอดสะสม — ภาพเดียวใช้กับทุกกลยุทธ์"""
    f = Frame(min(outcomes + [0]), max(outcomes + [0]), W, H, T=44, Bm=H - 36)
    out = f.grid([0])
    gw = (W - f.L - f.R) / len(outcomes)
    run, pts = 0, []
    for i, v in enumerate(outcomes):
        x = f.L + gw * i
        y0, y1 = f.y(0), f.y(v)
        out.append(f'<rect x="{x + gw * .15:.1f}" y="{min(y0, y1):.1f}" width="{max(1, gw * .7):.1f}" '
                   f'height="{max(1, abs(y1 - y0)):.1f}" fill="{C["green"] if v >= 0 else C["red"]}"/>')
        run += v
        pts.append((x + gw / 2, run))
        if label_every and i % label_every == 0:
            out.append(text(x + gw / 2, f.Bm + 16, str(i + 1), 10, C["grey"], "middle"))
    out.append(text(f.L, f.T - 18, title, 13, C["ink"], weight=700))
    out.append(text(W - f.R, f.T - 18, f"รวม {B.fmt(round(run, 2))}", 12, C["green"] if run >= 0 else C["red"], "end", 700))
    return out


def ladder_bars(rungs, title, unit="%", W=760, H=320):
    """บันได: [(ชื่อขั้น, ค่า)] ลดหลั่น · บอกส่วนที่หายระหว่างขั้น"""
    vals = [v for _, v in rungs]
    out = bars([n for n, _ in rungs], vals, title, unit,
               colors=[C["blue"]] + [C["blue"]] * (len(rungs) - 2) + [C["purple"]] if len(rungs) > 1 else None, W=W, H=H)
    f = Frame(min(vals + [0]), max(vals + [0]), W, H)
    gw = (W - f.L - f.R) / len(rungs)
    for i in range(1, len(rungs)):
        d = round(vals[i] - vals[i - 1], 2)
        x = f.L + gw * i
        out.append(text(x, f.y(max(vals[i], vals[i - 1])) - 24, ("−" if d < 0 else "+") + B.fmt(abs(d)), 11, C["red"] if d < 0 else C["green"], "middle"))
    return out


# ───────────────────────── สเปกต่อคีย์ (เติมทีละบท) ─────────────────────────

CHARTS = {}


def chart(key):
    def deco(fn):
        if key in CHARTS:                      # กันปลั๊กอินทับสเปกเดิมเงียบ ๆ
            raise SystemExit(f"กราฟ {key!r} ถูกนิยามซ้ำ ({fn.__module__}) — ย้ายมาไว้ที่เดียว")
        CHARTS[key] = fn
        return fn
    return deco



def grouped_bars(cats, series, title, unit="", W=760, H=330, legend=True):
    """series = [(ชื่อ, [ค่า], สี)] · แท่งเรียงข้างกันต่อหมวด · ค่าลบลงใต้ศูนย์"""
    vals = [v for _, s, _ in series for v in s]
    f = Frame(min(vals + [0]), max(vals + [0]), W, H, T=70)
    out = f.grid(nice_ticks(min(vals), max(vals)), unit)
    gw = (W - f.L - f.R) / len(cats)
    bw = min(46, (gw - 24) / len(series))
    for i, c in enumerate(cats):
        cx = f.L + gw * i + gw / 2
        for j, (_, s, col) in enumerate(series):
            v = s[i]
            x = cx - len(series) * (bw + 4) / 2 + j * (bw + 4)
            y0, y1 = f.y(0), f.y(v)
            out.append(f'<rect x="{x:.1f}" y="{min(y0, y1):.1f}" width="{bw:.1f}" height="{max(1, abs(y1 - y0)):.1f}" rx="2" fill="{col}"/>')
            lab = ("+" if v > 0 else "") + B.fmt(v)
            out.append(text(x + bw / 2, (y1 - 6) if v >= 0 else (y1 + 14), lab, 10.5, col, "middle", 700))
        out.append(text(cx, f.Bm + 18, c, 11.5, C["muted"], "middle"))
    if legend:
        lx = f.L
        for name, _, col in series:
            out.append(f'<rect x="{lx}" y="{f.T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
            out.append(text(lx + 16, f.T - 20, name, 11.5, C["muted"]))
            lx += 30 + 8 * len(name)
    out.append(text(f.L, f.T - 46, title, 13, C["ink"], weight=700))
    return out


def stacked_bars(cats, layers, title, totals=None, W=760, H=330):
    """layers = [(ชื่อ, [ค่า ≥ 0], สี)] ซ้อนจากล่าง · totals = ป้ายบนแท่ง"""
    tops = [sum(l[1][i] for l in layers) for i in range(len(cats))]
    f = Frame(0, max(tops), W, H, T=70, pad=0.15)
    out = f.grid(nice_ticks(0, max(tops)))
    gw = (W - f.L - f.R) / len(cats)
    bw = min(60, gw * 0.55)
    for i, c in enumerate(cats):
        cx, base = f.L + gw * i + gw / 2, 0
        for _, vals, col in layers:
            v = vals[i]
            if v:
                out.append(f'<rect x="{cx - bw / 2:.1f}" y="{f.y(base + v):.1f}" width="{bw:.1f}" '
                           f'height="{f.y(base) - f.y(base + v):.1f}" fill="{col}"/>')
            base += v
        if totals:
            out.append(text(cx, f.y(tops[i]) - 7, totals[i], 11, C["ink"], "middle", 700))
        for k, line in enumerate(c.split("\n")):
            out.append(text(cx, f.Bm + 16 + 13 * k, line, 10.5, C["muted"], "middle"))
    lx = f.L
    for name, _, col in layers:
        out.append(f'<rect x="{lx}" y="{f.T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 20, name, 11.5, C["muted"]))
        lx += 30 + 8 * len(name)
    out.append(text(f.L, f.T - 46, title, 13, C["ink"], weight=700))
    return out


def range_rows(rows, title, unit="", W=760, H=None):
    """rows = [(ชื่อ, ต่ำสุด, มัธยฐาน, สูงสุด, ค่าในเล่ม, สี)] — แถบช่วงข้ามหลายชุดสุ่ม + จุดค่าที่เล่มใช้"""
    H = H or 90 + 46 * len(rows)
    lo = min(r[1] for r in rows)
    hi = max(r[3] for r in rows)
    span = (hi - lo) or 1
    L, R = 220, 40
    X = lambda v: L + (v - lo + span * .05) / (span * 1.1) * (W - L - R)  # noqa: E731
    out = [text(16, 30, title, 13, C["ink"], weight=700)]
    for i, (name, mn, md, mx, ex, col) in enumerate(rows):
        y = 70 + 46 * i
        out.append(text(16, y + 4, name, 11.5, C["ink"]))
        out.append(f'<line x1="{X(mn):.1f}" y1="{y}" x2="{X(mx):.1f}" y2="{y}" stroke="{col}" stroke-width="8" stroke-opacity=".25" stroke-linecap="round"/>')
        out.append(f'<line x1="{X(md):.1f}" y1="{y - 9}" x2="{X(md):.1f}" y2="{y + 9}" stroke="{col}" stroke-width="3"/>')
        out.append(text(X(md), y - 13, f"มัธยฐาน {B.fmt(md)}{unit}", 10.5, col, "middle", 700))
        out.append(f'<circle cx="{X(ex):.1f}" cy="{y}" r="5" fill="{C["purple"]}"/>')
        out.append(text(X(ex), y + 22, f"ในเล่ม {B.fmt(ex)}{unit}", 10.5, C["purple"], "middle"))
        out.append(text(X(mn) - 8, y + 4, B.fmt(mn), 10, C["grey"], "end"))
        out.append(text(X(mx) + 8, y + 4, B.fmt(mx), 10, C["grey"]))
    return out, H


# ── บท 0 ──
@chart("sab-converge")
def _converge(fig):
    rows = fig["ch00"]["ปลายทาง"]
    cats = [f"วันหมดอายุ {B.fmt(r['ราคาวันหมดอายุ'])}" for r in rows]
    parts = grouped_bars(cats, [("ขา spot", [r["ขาspot"] for r in rows], C["blue"]),
                                ("ขา short futures", [r["ขาshortfutures"] for r in rows], C["amber"]),
                                ("รวมสองขา", [r["รวม"] for r in rows], C["green"])],
                         f"ราคาปลายทางจะเป็นเท่าไรก็ตาม สองขารวมกันได้ +{B.fmt(fig['ch00']['basis'])} เท่ากันทุกแถว")
    alt = "กราฟแท่งสามกลุ่ม ราคาวันหมดอายุ 60,000 100,000 150,000 ขา spot และขา short futures สวนทางกัน รวมสองขาเท่ากันทุกกลุ่ม"
    cap = (f"ถือ spot 1 BTC ที่ {B.fmt(rows[1]['ราคาวันหมดอายุ'])} และ short futures 1 BTC · "
           "ขาหนึ่งกำไรเท่าไร อีกขาขาดทุนเกือบเท่ากัน ส่วนที่เหลือคือ basis ที่ล็อกไว้ตั้งแต่วันเปิด (ก่อนค่าธรรมเนียม)")
    return wrap(760, 330, alt, parts, cap, "สอน")


# ── บท 4 ──
@chart("sab-buffer-line")
def _buffer_line(fig):
    d = fig["ch04"]["dist"]
    cash_main = fig["เรื่อง"]["part3"]["close"]["เงินสดอิสระ"]
    cash_ton = fig["ch04"]["ต้นเงินสดอิสระ"]
    cats = [f"ขึ้น {r['spotขึ้นเปอร์เซ็นต์']}%" for r in d]
    vals = [r["ต้องโอน"] for r in d]
    parts = bars(cats, vals, "ต้องโอนเติมเท่าไร เทียบกับเงินสดอิสระที่มี",
                 colors=[C["red"] if v > cash_main else (C["amber"] if v > cash_ton else C["blue"]) for v in vals])
    f = Frame(0, max(vals + [cash_main]), 760, 320)
    for lvl, lab, col in ((cash_main, f"ทุน 125,000 มีเงินสดอิสระ {B.fmt(cash_main)}", C["green"]),
                          (cash_ton, f"ทุน 120,000 (ต้น) มี {B.fmt(cash_ton)}", C["red"])):
        y = f.y(lvl)
        parts.append(f'<line x1="{f.L}" y1="{y:.1f}" x2="{760 - f.R}" y2="{y:.1f}" stroke="{col}" stroke-dasharray="6 4" stroke-width="1.6"/>')
        parts.append(text(f.L + 6, y - 6, lab, 11, col, "start", 700))
    alt = "กราฟแท่งเงินที่ต้องโอนเติมเมื่อราคาขึ้น 5 10 15 เปอร์เซ็นต์ เทียบเส้นเงินสดอิสระของทุน 125,000 และ 120,000"
    cap = (f"ขึ้น 10% ทุน 120,000 ขาด {B.fmt(d[1]['ขาดที่ทุน120000'])} (ต้นถูกบังคับปิด) · ขึ้น 15% ทุน 125,000 ก็ขาด "
           f"{B.fmt(d[2]['ขาดที่ทุน125000'])} · ไม่ใช่การพยากรณ์ — คือการถามว่ากันชนรับได้ถึงไหน")
    return wrap(760, 320, alt, parts, cap, "สอน")


# ── บท 10 ──
@chart("sab-selection-bias")
def _selection_bias(fig):
    g, s = fig["ch10"]["กราฟ"], fig["ch10"]["ค้น"]
    top, real = g["อันดับ1"], g["คู่จริง"]
    nf = s["วันช่วงเลือก"]
    xs = list(range(1, len(top) + 1))
    a1 = fig["ch10"]["อันดับ1"]
    lo_day = nf + a1["วันทดสอบที่ต่ำสุด"]
    parts = lines(xs, [("คู่อันดับ 1 จาก 200 คู่ (ไม่มีเชือก)", top, C["red"]), ("คู่ที่มีเชือกจริง", real, C["green"])],
                  "สวยที่สุดในช่วงเลือก — แล้วหลุดในช่วงทดสอบ", xlabel="วัน (ช่วงเลือก | ช่วงทดสอบ)",
                  marks=[(lo_day, top[lo_day - 1], f"{B.fmt(a1['zต่ำสุด'])} ระยะแกว่ง")], every=2,
                  xticks=[(1, "วันที่ 1"), (nf, f"วันที่ {B.fmt(nf)}"), (len(top), f"วันที่ {B.fmt(s['วันทั้งหมด'])}")])
    f = Frame(min(top + real), max(top + real), 760, 320)
    X = lambda x: f.L + (x - 1) / (len(top) - 1) * (760 - f.L - f.R)  # noqa: E731
    for lvl in (2, -2):
        parts.append(f'<line x1="{f.L}" y1="{f.y(lvl):.1f}" x2="{760 - f.R}" y2="{f.y(lvl):.1f}" stroke="{C["grey"]}" stroke-dasharray="4 4"/>')
    parts.append(f'<line x1="{X(nf):.1f}" y1="{f.T}" x2="{X(nf):.1f}" y2="{f.Bm}" stroke="{C["purple"]}" stroke-width="1.5"/>')
    parts.append(text(X(nf) + 6, f.T - 4, "เริ่มช่วงทดสอบ", 11, C["purple"], weight=700))
    alt = "กราฟเส้นสองเส้น คู่ที่คัดได้อันดับ 1 อยู่ในกรอบช่วงเลือก แล้วหลุดลงถึงราว −4.85 ในช่วงทดสอบ ส่วนคู่ที่มีเชือกอยู่ในกรอบ"
    cap = (f"ค้น {s['คู่ที่ค้น']} คู่ที่ไม่มีเชือก แล้วเลือกคู่ที่ข้ามค่ากลางบ่อยสุดในช่วงเลือก {nf} วัน · "
           f"เทียบกับคู่ที่มีเชือกซึ่งสร้างแยกอีก {s['คู่จริง']} คู่ · ช่วงทดสอบคู่อันดับ 1 อยู่ในกรอบ ±2 เพียง "
           f"{B.fmt(a1['ในกรอบ'])}% · เส้นประ = กรอบ ±2 ระยะแกว่ง")
    return wrap(760, 320, alt, parts, cap, "จำลอง")


@chart("sab-seed-spread")
def _seed_spread(fig):
    r = fig["seed_robustness"]["ch10"]
    rows = [("ในกรอบ: 10 คู่ที่คัด", r["ในกรอบ"], C["red"]), ("ในกรอบ: คู่ที่มีเชือก", r["ในกรอบคู่จริง"], C["green"]),
            ("ในกรอบ: ทั้ง 200 คู่", r["ทั้ง200ในกรอบ"], C["grey"])]
    parts, H = range_rows([(n, v["ต่ำสุด"], v["มัธยฐาน"], v["สูงสุด"], v["ตัวอย่าง"], c) for n, v, c in rows],
                          f"สุ่มใหม่ {r['ในกรอบ']['จำนวนseed']} ชุด: ตัวอย่างในเล่มอยู่ฝั่งที่ดูดีของช่วง", unit="%")
    alt = "แถบช่วงของสัดส่วนวันในกรอบข้าม 30 ชุดสุ่ม คู่ที่คัดกระจาย 18 ถึง 63 เปอร์เซ็นต์ คู่ที่มีเชือกอยู่ราว 89 ถึง 95"
    cap = (f"ตัวอย่างในเล่ม {B.fmt(r['ในกรอบ']['ตัวอย่าง'])}% แต่มัธยฐานข้ามชุดคือ {B.fmt(r['ในกรอบ']['มัธยฐาน'])}% · "
           f"คู่ที่คัดแย่กว่าคู่ที่มีเชือกใน {r['คู่ที่คัดแย่กว่าคู่จริง']['จำนวนseed']} จาก {r['คู่ที่คัดแย่กว่าคู่จริง']['จาก']} ชุด")
    return wrap(760, H, alt, parts, cap, "จำลอง")


def _load_chapter_charts():
    """สเปกกราฟต่อบทจาก tools/sab_charts_ch/chNN.py (แยกไฟล์ต่อบท) · ไฟล์ใช้ `from sab_charts import *`"""
    import glob as _glob
    import importlib.util as _ilu
    sys.modules.setdefault("sab_charts", sys.modules[__name__])
    for path in sorted(_glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sab_charts_ch", "ch[0-9][0-9].py"))):
        spec = _ilu.spec_from_file_location("sab_charts_ch_" + os.path.basename(path)[:-3], path)
        spec.loader.exec_module(_ilu.module_from_spec(spec))


_load_chapter_charts()

# ───────────────────────── ประมวลผลหน้า ─────────────────────────

PROTECT_RE = re.compile(r"<(script|style)\b.*?</\1>", re.S)
MARK_RE = re.compile(r"(<!--(CHART|DATA):([^>]+?)-->)(.*?)(<!--/\2:\3-->)", re.S)


def _protected(html):
    return [(m.start(), m.end()) for m in PROTECT_RE.finditer(html)
            if not m.group(0).startswith('<script type="application/json"')]


def process(html, fig, fill=False):
    """คืน (html ใหม่, คีย์ที่ไม่รู้จัก)"""
    unknown = []
    prot = _protected(html)

    def sub(m):
        if any(s <= m.start() < e for s, e in prot):
            return m.group(0)
        kind, key = m.group(2), m.group(3)
        if kind == "CHART":
            if key not in CHARTS:
                unknown.append(key)
                return m.group(0)
            return f"{m.group(1)}\n{CHARTS[key](fig)}\n{m.group(5)}"
        try:
            data = B.get_path(fig, key)
        except KeyError:
            unknown.append(key)
            return m.group(0)
        js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        sid = "data-" + re.sub(r"[^\w-]", "-", key)
        return f'{m.group(1)}<script type="application/json" id="{sid}">{js}</script>{m.group(5)}'
    out = MARK_RE.sub(sub, html)
    if fill:
        def fsub(m):
            try:
                return f"{m.group(1)}{B.fmt(B.get_path(fig, m.group(2)))}</td>"
            except KeyError:
                unknown.append(m.group(2))
                return m.group(0)
        out = re.sub(r'(<td\b(?=[^>]*\bdata-key="([^"]+)")(?![^>]*\bclass="blank")[^>]*>).*?</td>', fsub, out, flags=re.S)
    return out, unknown


def run(docs, fig, fill=False, write=True):
    changed, unknown = [], []
    for name in sorted(os.listdir(docs)):
        if not (name.startswith(f"{B.PREFIX}-") and name.endswith(".html")):
            continue
        path = os.path.join(docs, name)
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        new, unk = process(html, fig, fill)
        unknown += [f"{name}: {k}" for k in unk]
        if new != html:
            changed.append(name)
            if write:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
    return changed, unknown


def selftest():
    fig = {"ch04": {"ต้องโอน": 11220, "equity": -200}, "t": {"v": [3, -1, 2]}}

    @chart("sab-zz-test")
    def _t(f):
        return wrap(400, 200, "ทดสอบ", slip_strip(f["t"]["v"], "แถบผล"), "คำบรรยาย", "สอน")
    head, tail = B.shell()
    page = (head + '<!--CHART:sab-zz-test--><!--/CHART:sab-zz-test-->\n<!--DATA:ch04--><!--/DATA:ch04-->'
            '<table><tr><td data-key="ch04.ต้องโอน"></td><td data-key="ch04.equity">เก่า</td>'
            '<td class="blank" data-key="ch04.ต้องโอน"></td></tr></table>'
            '<script>var s = "<!--CHART:sab-zz-test--><!--/CHART:sab-zz-test-->";</script>'
            '<!--CHART:sab-nope--><!--/CHART:sab-nope-->' + tail)
    ok = True
    one, unk = process(page, fig, fill=True)
    two, _ = process(one, fig, fill=True)
    if one != two:
        ok = False
        print("selftest ล้ม: รันซ้ำแล้วไม่นิ่ง")
    if "<svg" not in one or "🔢" not in one or '"ต้องโอน": 11220' not in one:
        ok = False
        print("selftest ล้ม: ไม่วาด/ไม่ใส่ DATA")
    if ">11,220</td>" not in one or ">−200</td>" not in one or 'class="blank" data-key="ch04.ต้องโอน"></td>' not in one:
        ok = False
        print("selftest ล้ม: --fill")
    if 'var s = "<!--CHART:sab-zz-test--><!--/CHART:sab-zz-test-->"' not in one:
        ok = False
        print("selftest ล้ม: แตะตัวคั่นใน <script>")
    if unk != ["sab-nope"]:
        ok = False
        print("selftest ล้ม: คีย์ไม่รู้จัก", unk)
    for k in [k for k in CHARTS if k.startswith("sab-zz")]:
        del CHARTS[k]
    # ทุกกราฟจริงต้องวาดได้จาก JSON ปัจจุบันและมีป้ายที่มา
    figp = os.path.join(B.DOCS, "sab-figures.json")
    if os.path.exists(figp):
        with open(figp, encoding="utf-8") as fh:
            real = json.load(fh)
        for k, fn in CHARTS.items():
            try:
                svg = fn(real)
                assert "<svg" in svg and any(t in svg for t in ("🔢", "🎲", "📡"))
            except Exception as e:  # noqa: BLE001
                ok = False
                print(f"selftest ล้ม: กราฟ {k} วาดไม่ได้ — {e!r}")
    print("selftest", f"ผ่าน ✓ (รันซ้ำนิ่ง · DATA · --fill ข้ามใบเปล่า · ไม่แตะ <script> · จับคีย์ไม่รู้จัก · กราฟจริง {len(CHARTS)} คีย์วาดได้)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


def load_fig():
    with open(os.path.join(B.DOCS, "sab-figures.json"), encoding="utf-8") as fh:
        return json.load(fh)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(selftest())
    if a == ["--list"]:
        have = set(CHARTS)
        for label, keys in (("★", PLANNED_STAR), ("☆", PLANNED_OPT)):
            done = [k for k in keys if k in have]
            print(f"{label} {len(done)}/{len(keys)}: ยังไม่มี → " + ", ".join(k for k in keys if k not in have))
        sys.exit(0)
    changed, unknown = run(B.DOCS, load_fig(), fill="--fill" in a, write="--check" not in a)
    for u in unknown:
        print("  - ไม่รู้จัก:", u)
    if "--check" in a:
        print(("ต้องรันใหม่: " + ", ".join(changed)) if changed else "กราฟ/ค่าในบทตรงกับ JSON ✓")
        sys.exit(1 if changed or unknown else 0)
    print(("อัปเดต " + ", ".join(changed)) if changed else "ไม่มีหน้าที่ต้องเปลี่ยน")
    sys.exit(1 if unknown else 0)
