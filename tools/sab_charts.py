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
SRC = {"สอน": "🔢 ตัวเลขสมมติเพื่อสอน", "จำลอง": "🎲 จำลอง seed คงที่", "จริง": "📡 ข้อมูลจริง (สแนปช็อต)",
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
    return (f'<svg class="fig" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(alt)}">\n' + "\n".join(parts) +
            f'\n</svg>\n<div class="cap">{SRC[src]} · {cap}</div>')


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


def lines(xs, series, title, unit="", xlabel="", W=760, H=320, marks=None):
    """series = [(ชื่อ, [y], สี)] · marks = [(x, y, ข้อความ)] จุดสำคัญสีม่วง"""
    ys = [v for _, s, _ in series for v in s if v is not None]
    f = Frame(min(ys), max(ys), W, H)
    out = f.grid(nice_ticks(min(ys), max(ys)), unit)
    x0, x1 = min(xs), max(xs)
    X = lambda x: f.L + (x - x0) / ((x1 - x0) or 1) * (W - f.L - f.R)  # noqa: E731
    for name, s, col in series:
        pts = " ".join(f"{X(x):.1f},{f.y(v):.1f}" for x, v in zip(xs, s) if v is not None)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linejoin="round"/>')
    for x, y, lab in marks or []:
        out.append(f'<circle cx="{X(x):.1f}" cy="{f.y(y):.1f}" r="4.5" fill="{C["purple"]}"/>')
        out.append(text(X(x) + 8, f.y(y) - 8, lab, 11.5, C["purple"], weight=700))
    lx = f.L
    for name, _, col in series:
        out.append(f'<rect x="{lx}" y="{f.T - 16}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 6, name, 11.5, C["muted"]))
        lx += 24 + 7.5 * len(name)
    out.append(text(f.L, f.T - 30, title, 13, C["ink"], weight=700))
    if xlabel:
        out.append(text((f.L + W - f.R) / 2, f.Bm + 36, xlabel, 12, C["muted"], "middle"))
    for x in xs[:: max(1, len(xs) // 8)]:
        out.append(text(X(x), f.Bm + 16, B.fmt(x), 10.5, C["grey"], "middle"))
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
        CHARTS[key] = fn
        return fn
    return deco


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
