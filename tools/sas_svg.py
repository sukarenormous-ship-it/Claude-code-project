#!/usr/bin/env python3
"""ตัวช่วยวาดกราฟ inline SVG ของชุด "แกะสไลด์ Stat Arb" (สไตล์เดียวกับทั้งคลัง)

ทุกฟังก์ชันคืน "สตริง" ล้วน ๆ (numpy + stdlib) · โมดูลทดลอง tools/sas_exp<N>.py เรียกใช้แล้วคืน
{"sas-p<N>-slug": html} ให้ tools/sas_build.py charts ฉีดลงหน้า HTML · ดูตัวอย่างทุกตัวที่
    python3 tools/sas_svg.py [ไฟล์ปลายทาง.html]        (แกลเลอรี — เปิดดูก่อนลงมือ)

ตัวอย่าง 5 บรรทัด
    import sas_svg as V
    fig = V.Fig("sas-p3-demo", 760, 300)                      # cid = ชื่อกราฟ → prefix ของทุก id ใน <defs>
    p = fig.panel((0, len(y) - 1), V.auto_lim(y)); p.grid().yaxis(title="ε (%)").xaxis(title="แท่งที่")
    p.area(x, y, V.BLUE).line(x, y, V.BLUE, hero=True).hline(0, label="μ").callout(x[-1], y[-1], "ล่าสุด")
    html = fig.svg("คำบรรยายสำหรับโปรแกรมอ่านจอ", "คำบรรยายใต้ภาพ (เป็น HTML ได้)")

สิ่งที่ทุกตัวคืน (ผ่าน wrap):
    <div class="figw"><svg class="fig" viewBox="0 0 w h" role="img" aria-label="alt">…</svg></div>
    <div class="cap">cap</div>
  div.figw = กรอบเลื่อนแนวนอนบนจอแคบ (รูปกว้าง ≤ 560 ไม่มีกรอบนี้) · ป้ายหลายบรรทัดใช้ "\\n" ได้ในที่ที่ docstring บอก

ชั้นที่ 1 — ตัวสร้างสำเร็จรูป (ทุกตัว: cid, …, alt, cap → html · รายละเอียดอยู่ใน docstring ของแต่ละตัว)
    stacked_panels(cid, panels, alt, cap, x=None, share_y=False, xlabel=None, xbands=None, …)   หลายกรอบแกน x ร่วม
    series_with_hist(cid, rows, alt, cap=None, x=None, xlabel=None, hist_xlabel=None, …)        อนุกรม + ฮิสโทแกรม
    zone_chart(cid, eps, pcts, alt, cap, x=None, mark_last=False, label="VaR {p}%: {v}", …)     ε + เส้นเปอร์เซ็นไทล์
    heat_table(cid, row_labels, col_labels, values, alt, cap, scale="seq"|"div", fmt=None, …)   ตารางตัวเลขระบายสี
    dot_interval(cid, rows, alt, cap, zero=True, xlabel=None, fmt=None, …)                      จุด + ช่วง 5–95%
    stacked_bars(cid, bars, parts, alt, cap, colors=None, normalize=True, …)                    แท่งซ้อน 100%
    grouped_bars(cid, groups, series, alt, cap, ylabel=None, xlabel=None, hlines=None, …)       แท่งเป็นกลุ่ม
    line_chart(cid, x, series, alt, cap, xlabel=None, ylabel=None, categories=False, …)         หลายเส้น + legend
    hist_chart(cid, values, alt, cap, bins=40, vlines=None, shade=None, …)                      ฮิสโทแกรม + เส้นเกณฑ์
    scatter_chart(cid, x, y, alt, cap, lines=None, max_points=300, …)                           จุดกระจาย + เส้น fit

ชั้นที่ 2 — Fig + Panel (ประกอบเอง · เรียกก่อน = อยู่ล่าง · ทุกเมธอดของ Panel คืน self)
    Fig(cid, w=760, h=320)  .panel(xlim, ylim, x=None, y=None, w=None, h=None, left=58, top=34, right=18, bottom=44)
                            .title(s, sub)  .legend(items, x, y, anchor)  .text(x, y, s, …)  .add(svg)  .svg(alt, cap)
    Panel  โครง     .grid(yticks, xticks)  .xaxis(ticks, labels, title, fmt)  .yaxis(ticks, labels, title, fmt)
           ข้อมูล   .line(xs, ys, color, hero=False, dash=None)  .area(xs, ys, color, base, color_below)
                    .scatter(xs, ys, color, ring=False)  .bars(xs, vals, …)  .hbars(ys, vals, …)  .hist(edges, heights, …)
           อ้างอิง  .hline(v, label=, pos="right"|"left"|"out")  .vline(v, label=, pos="top"|"bottom"|"above")
                    .band(lo, hi, color, label=)  .xband(lo, hi, color, label=)  .gutter_labels([(y, ข้อความ)])
           คำอธิบาย .title(s, sub)  .legend(items, pos="top"|"tl"|"tr"|"bl"|"br")  .text(x, y, s, dx, dy, …)
                    .callout(x, y, label, dx, dy, color)       พิกัด: .X(v) .Y(v) .right .bottom
    legend item = (ชื่อ, สี[, "line"|"rect"|"dot"|"ring"|"band"[, dash]])

ชั้นที่ 3 — ของดิบ
    wrap(w, h, alt, parts, cap)  text(x, y, s, size, color, anchor, weight, halo)  esc()  esc_attr()
    num(v, d=None, sign=False)  pct(v, d=0)  minus(s)  tick_fmt(ticks)  nice_ticks(lo, hi, n=5)
    auto_lim(*arrays, include=(), pad=0.06)  downsample(xs, ys, max_points=400)  declutter(pos, gap, lo, hi)
    text_w(s, size)  mix(c1, c2, t)  ink_on(fill)
    สี: GREEN RED BLUE AMBER PURPLE · INK MUTED GRID AXIS DARK · SERIES (ลำดับสีของชุดข้อมูล) · DASHES · FONT

กติกาสไตล์ที่โค้ดนี้ทำให้อยู่แล้ว (ดู .claude/skills/knowledge-book/references/visual-guide.md)
  • id ใน <defs> ทุกตัวขึ้นต้นด้วย cid — หลายกราฟอยู่ในหน้าเดียวกันได้โดยไม่ชนกัน (cid ต้องไม่ซ้ำกันในหน้า)
  • grid/แกนสีจาง · เส้นข้อมูลปลายมน · ตัวอักษรใช้สีหมึก (INK/MUTED) ไม่ใช้สีของชุดข้อมูล
    ยกเว้นป้าย callout / จุดล่าสุด ที่จงใจให้สีสื่อความหมาย
  • ≥ 2 ชุดข้อมูลมี legend เสมอ วางเหนือกรอบ (นอกพื้นที่ข้อมูล) · ป้ายของเส้นอ้างอิงในตัวสร้างสำเร็จรูป
    อยู่ในร่องขวาหรือเหนือกรอบ และขยับหลบกันเอง · ไม่มีทางสร้างแกน y สองแกน
  • หัวข้อยาวจน legend ต้องขึ้นแถวใหม่ → ตัวสร้างสำเร็จรูปขยายความสูงของหัวกรอบให้เอง (ไม่มีอะไรถูกตัดขอบ)
    แต่หัวข้อที่ยาวกว่าความกว้างกรอบจะล้น — เขียนหัวข้อให้สั้น แล้วเอารายละเอียดไปไว้ใน cap
  • ลำดับสี SERIES = น้ำเงิน ส้ม แดง ม่วง เขียว — ตรวจด้วย validator ของ dataviz skill แล้ว: คู่ที่ "ติดกัน"
    แยกออกสำหรับคนตาบอดสี แต่ น้ำเงิน↔ม่วง และ แดง↔เขียว แยกไม่ออก จึงให้เส้นลำดับที่ 4–5 เป็นเส้นประ
    โดยอัตโนมัติ (DASHES) — ถ้ากำหนดสีเอง อย่าให้สองคู่นี้ต่างกันด้วยสีอย่างเดียว
  • อนุกรมยาวถูกย่อด้วย downsample() (เก็บ min/max ต่อช่วง ยอดแหลมไม่หาย) และเขียน path แบบพิกัดสัมพัทธ์
    กราฟเส้น 1,500 จุดหนึ่งเส้น ≈ 2–3 KB · หน้าหนึ่งมีหลายกราฟ จึงควรดูขนาดที่แกลเลอรีพิมพ์ให้
"""

import html as _html
import math
import os
import re
import sys

import numpy as np

# ───────────────────────── สี · ฟอนต์ ─────────────────────────

GREEN, RED, BLUE, AMBER, PURPLE = "#16a34a", "#dc2626", "#2563eb", "#d97706", "#7c3aed"
INK, MUTED, GRID, AXIS = "#374151", "#6b7280", "#e5e7eb", "#cbd5e1"
DARK = "#1f2937"                       # เส้นข้อมูลสีหมึกเข้ม (เช่น ε บนพื้นแรเงา)
NEUTRAL = "#f3f4f6"                    # จุดกลางของสเกลสองขั้ว
SERIES = (BLUE, AMBER, RED, PURPLE, GREEN)
DASHES = (None, None, None, "7 4", "2 4")
FONT = 'font-family="Sarabun,sans-serif"'
MINUS = "\u2212"                       # เครื่องหมายลบจริง (ไม่ใช่ขีดกลาง)
SIZE = 11.5                            # ขนาดตัวอักษรตั้งต้น (กำหนดที่ <g> ครอบใน wrap)

LINE_H = 15.0                          # ระยะบรรทัดของป้ายหลายบรรทัด (ภาษาไทยมีสระ/วรรณยุกต์ซ้อนบน 13px ชนกัน)
_NARROW = 560                          # รูปที่กว้างไม่เกินนี้ไม่ต้องมีกรอบเลื่อน div.figw (ดู wrap)
_HALO = 'stroke="#fff" stroke-width="3" stroke-linejoin="round" paint-order="stroke"'
_TH_ZERO = set(range(0x0E34, 0x0E3B)) | set(range(0x0E47, 0x0E4F)) | {0x0E31}


# ───────────────────────── ตัวช่วยพื้นฐาน ─────────────────────────

def esc(s):
    """escape สำหรับข้อความใน element"""
    return _html.escape(str(s), quote=False)


def esc_attr(s):
    """escape สำหรับค่า attribute (เช่น aria-label) — ยุบช่องว่าง/ขึ้นบรรทัดให้เหลือช่องเดียว"""
    return _html.escape(" ".join(str(s).split()), quote=True)


def _f(v):
    """พิกัดทศนิยม 1 ตำแหน่ง ตัด .0 ทิ้ง (ให้ SVG เบา)"""
    s = f"{float(v):.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


def _n(v):
    """ตัวเลขสั้นที่สุดสำหรับ path: ทศนิยม 1 ตำแหน่ง ไม่มี 0 นำหน้า"""
    s = f"{float(v):.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s.startswith("0.") or s.startswith("-0."):
        s = s.replace("0.", ".", 1)
    return "0" if s in ("-0", "-") else s


def _d(px, py):
    """สตริง d ของเส้นต่อเนื่องแบบพิกัดสัมพัทธ์ (สั้นกว่าพิกัดสัมบูรณ์ราวหนึ่งในสี่)"""
    qx, qy = np.round(np.asarray(px, float), 1), np.round(np.asarray(py, float), 1)
    if len(qx) < 2:
        return f"M{_n(qx[0])} {_n(qy[0])}h.01".replace(" -", "-")
    body = " ".join(f"{_n(a)} {_n(b)}" for a, b in zip(np.diff(qx), np.diff(qy)))
    return (f"M{_n(qx[0])} {_n(qy[0])}l" + body).replace(" -", "-")


def num(v, d=None, sign=False):
    """ตัวเลขเป็นข้อความ: คั่นหลักพัน · เครื่องหมายลบเป็น U+2212 · d=None = ทศนิยมเท่าที่เก็บไว้ (ไม่เกิน 4)
    sign=True เติม + หน้าค่าบวก · None/NaN → '–'"""
    if v is None:
        return "–"
    v = float(v)
    if not math.isfinite(v):
        return "–"
    if d is None:
        for d in range(0, 5):
            if abs(v - round(v, d)) <= 1e-9 * max(1.0, abs(v)):
                break
    s = f"{abs(v):,.{d}f}"
    if float(s.replace(",", "")) == 0:
        return s
    return (MINUS if v < 0 else ("+" if sign else "")) + s


def pct(v, d=0, sign=False):
    """ค่าที่เป็นเปอร์เซ็นต์อยู่แล้ว → '12.5%'"""
    return num(v, d, sign) + "%"


def minus(s):
    """เปลี่ยน '-' ที่นำหน้าตัวเลขเป็น U+2212 (ใช้กับสตริงที่จัดรูปเองแล้ว)"""
    return re.sub(r"(?<![\w.])-(?=[\d.])", MINUS, str(s))


def tick_fmt(ticks):
    """ฟังก์ชันจัดรูปป้ายแกน ให้ทุกขีดมีทศนิยมเท่ากัน"""
    d = 0
    for d in range(0, 7):
        if all(abs(t - round(t, d)) <= 1e-9 * max(1.0, abs(t)) for t in ticks):
            break
    return lambda v: num(v, d)


def nice_ticks(lo, hi, n=5):
    """ขีดแกน "เลขกลม" (ก้าว 1 · 2 · 2.5 · 5 × 10^k) ที่อยู่ในช่วง [lo, hi] ประมาณ n ช่อง"""
    lo, hi = float(lo), float(hi)
    if hi < lo:
        lo, hi = hi, lo
    if hi == lo:
        lo, hi = lo - 0.5, hi + 0.5
    raw = (hi - lo) / max(int(n), 1)
    mag = 10.0 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if raw <= m * mag * 1.2)
    k0 = math.ceil(lo / step - 1e-9)
    out = []
    while (k0 + len(out)) * step <= hi + step * 1e-9:
        out.append(round((k0 + len(out)) * step, 12) + 0.0)
    return out


def auto_lim(*arrays, include=(), pad=0.06, n=5, snap=True):
    """ช่วงแกน (lo, hi) ที่ครอบข้อมูลทุกชุด (ข้าม NaN) · include = ค่าที่ต้องอยู่ในช่วงด้วย (เช่น 0)
    snap=True ขยายออกไปหาขีดเลขกลม · pad = ที่ว่างเผื่อ (สัดส่วนของช่วง)"""
    vals = [np.asarray(a, float).ravel() for a in arrays] + [np.asarray(list(include), float)]
    v = np.concatenate(vals) if vals else np.array([0.0, 1.0])
    v = v[np.isfinite(v)]
    if v.size == 0:
        return 0.0, 1.0
    lo, hi = float(v.min()), float(v.max())
    if hi == lo:
        lo, hi = lo - 0.5, hi + 0.5
    span = hi - lo
    lo, hi = lo - pad * span, hi + pad * span
    for inc in include:                      # ค่าที่ขอให้รวม ไม่ต้องเผื่อเลยออกไป (เช่น แท่งที่เริ่มจาก 0)
        if abs(float(v.min()) - inc) < 1e-12:
            lo = float(inc)
        if abs(float(v.max()) - inc) < 1e-12:
            hi = float(inc)
    if snap:                                 # ปัดออกไปหา "ครึ่งก้าว" ของขีดแกน — กรอบจะไม่หลวมเกิน
        t = nice_ticks(lo, hi, 2 * n)
        step = t[1] - t[0] if len(t) > 1 else (hi - lo)
        lo = math.floor(lo / step + 1e-9) * step
        hi = math.ceil(hi / step - 1e-9) * step
    return round(float(lo), 12), round(float(hi), 12)


def downsample(xs, ys, max_points=400):
    """ย่ออนุกรมให้เหลือ ≤ max_points จุด โดยเก็บ "ค่าต่ำสุดและสูงสุดของแต่ละช่วง" (ยอดแหลมไม่หาย)
    คืน (xs, ys) เป็น numpy array · จุดที่เป็น NaN ถูกตัดทิ้ง"""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    ok = np.isfinite(xs) & np.isfinite(ys)
    xs, ys = xs[ok], ys[ok]
    n = len(ys)
    if n <= max_points or max_points < 4:
        return xs, ys
    buckets = max(1, max_points // 2 - 1)
    edges = np.linspace(1, n - 1, buckets + 1).astype(int)
    keep = {0, n - 1}
    for a, b in zip(edges[:-1], edges[1:]):
        if b > a:
            seg = ys[a:b]
            keep.add(a + int(seg.argmin()))
            keep.add(a + int(seg.argmax()))
    idx = np.array(sorted(keep))
    return xs[idx], ys[idx]


def declutter(pos, gap, lo=None, hi=None):
    """ขยับตำแหน่งป้าย 1 มิติให้ห่างกันอย่างน้อย gap โดยขยับน้อยที่สุดและคงลำดับเดิม
    (ใช้กับป้ายเส้นเปอร์เซ็นไทล์ที่อยู่ชิดกัน) · คืนลิสต์ตำแหน่งใหม่ตามลำดับ input"""
    pos = [float(p) for p in pos]
    order = sorted(range(len(pos)), key=lambda i: pos[i])
    blocks = []
    for i in order:
        blocks.append([[i], pos[i]])
        while len(blocks) > 1 and blocks[-2][1] + gap * len(blocks[-2][0]) > blocks[-1][1] + 1e-9:
            b = blocks.pop()
            a = blocks[-1]
            a[0] += b[0]
            a[1] = sum(pos[it] - k * gap for k, it in enumerate(a[0])) / len(a[0])
    out = [0.0] * len(pos)
    for items, start in blocks:
        for k, it in enumerate(items):
            out[it] = start + k * gap
    if order and (lo is not None or hi is not None):
        seq = [out[i] for i in order]
        if lo is not None and seq[0] < lo:
            seq[0] = lo
        for k in range(1, len(seq)):
            seq[k] = max(seq[k], seq[k - 1] + gap)
        if hi is not None and seq[-1] > hi:
            seq[-1] = hi
            for k in range(len(seq) - 2, -1, -1):
                seq[k] = min(seq[k], seq[k + 1] - gap)
        for k, i in enumerate(order):
            out[i] = seq[k]
    return out


def text_w(s, size=SIZE):
    """ความกว้างโดยประมาณ (px) ของข้อความ Sarabun — สระบน/ล่างและวรรณยุกต์ไทยไม่กินที่"""
    w = 0.0
    for ch in str(s):
        o = ord(ch)
        if o in _TH_ZERO or o == 0xFE0F:
            continue
        if 0x0E00 <= o <= 0x0E7F:
            w += 0.58
        elif ch == " ":
            w += 0.27
        elif ch.isdigit():
            w += 0.55
        elif ch in ".,:;'|!ilj()[]·":
            w += 0.3
        elif ch in "mwMW%—":
            w += 0.85
        elif ch.isupper():
            w += 0.66
        elif o > 0x2000:
            w += 0.62 if o < 0x1F000 else 1.1
        else:
            w += 0.52
    return w * size


def text(x, y, s, size=SIZE, color=INK, anchor="start", weight=None, halo=False, rotate=None, raw=False):
    """<text> หนึ่งบรรทัด · พิกัดเป็นพิกเซลของ viewBox · halo=True ใส่ขอบขาวให้อ่านออกเมื่อทับข้อมูล
    raw=True = s เป็น SVG อยู่แล้ว (เช่น มี <tspan>) ไม่ต้อง escape"""
    a = [f'x="{_f(x)}" y="{_f(y)}"']
    if anchor != "start":
        a.append(f'text-anchor="{anchor}"')
    if abs(size - SIZE) > 1e-9:
        a.append(f'font-size="{_f(size)}"')
    if weight:
        a.append(f'font-weight="{weight}"')
    a.append(f'fill="{color}"')
    if halo:
        a.append(_HALO)
    if rotate:
        a.append(f'transform="rotate({_f(rotate)} {_f(x)} {_f(y)})"')
    return f'<text {" ".join(a)}>{s if raw else esc(s)}</text>'


def wrap(w, h, alt, parts, cap=None):
    """ห่อชิ้นส่วน SVG เป็นกราฟพร้อมคำบรรยาย:
    <div class="figw"><svg class="fig" viewBox="0 0 w h" role="img" aria-label="…">…</svg></div>\\n<div class="cap">…</div>
    alt ถูก escape ให้ · cap เป็น HTML (cap ว่าง/None = ไม่ใส่ <div class="cap">)
    div.figw = กรอบเลื่อนแนวนอนบนจอแคบ (CSS อยู่ในเปลือกของ tools/sas_new_part.py): บนมือถือกราฟกว้าง 760
    จะไม่ถูกบีบจนตัวอักษรเหลือ 5px แต่เลื่อนดูด้านข้างได้ เหมือนตารางใน .tw · บนจอกว้างและตอนพิมพ์ไม่มีผลอะไร
    รูปที่แคบ (w ≤ 560) ไม่ใส่กรอบ เพราะย่อเต็มจอแล้วยังอ่านออก"""
    body = "\n".join(p for p in parts if p)
    out = (f'<svg class="fig" viewBox="0 0 {_f(w)} {_f(h)}" role="img" aria-label="{esc_attr(alt)}">\n'
           f'<g {FONT} font-size="{SIZE}">\n{body}\n</g>\n</svg>')
    if float(w) > _NARROW:
        out = f'<div class="figw">{out}</div>'
    if cap:
        out += f'\n<div class="cap">{cap}</div>'
    return out


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    """ผสมสี hex สองสี (t=0 → c1 · t=1 → c2)"""
    t = min(1.0, max(0.0, float(t)))
    a, b = _hex(c1), _hex(c2)
    return "#" + "".join(f"{round(a[i] + (b[i] - a[i]) * t):02x}" for i in range(3))


def _lum(c):
    def lin(u):
        u /= 255.0
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(u) for u in _hex(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ink_on(fill):
    """สีตัวอักษรที่อ่านออกบนพื้นสี fill (ขาว หรือ หมึกเข้ม)"""
    lum = _lum(fill)
    return "#ffffff" if 1.05 / (lum + 0.05) >= (lum + 0.05) / (_lum(DARK) + 0.05) else DARK


def _items(items):
    """legend item: (label, color[, kind[, dash]]) หรือ dict · kind = line | rect | dot | ring | band"""
    out = []
    for it in items:
        if isinstance(it, dict):
            out.append((it["label"], it.get("color", BLUE), it.get("kind", "line"), it.get("dash")))
        else:
            it = tuple(it)
            out.append((it[0], it[1], it[2] if len(it) > 2 else "line", it[3] if len(it) > 3 else None))
    return out


_SW = {"line": 20, "rect": 11, "dot": 10, "ring": 10, "band": 14}


def _swatch(x, yc, color, kind, dash):
    if kind == "rect":
        return f'<rect x="{_f(x)}" y="{_f(yc - 5.5)}" width="11" height="11" rx="2" fill="{color}"/>'
    if kind == "band":
        return (f'<rect x="{_f(x)}" y="{_f(yc - 5.5)}" width="14" height="11" rx="2" fill="{color}" '
                f'fill-opacity=".2" stroke="{color}" stroke-opacity=".55"/>')
    if kind == "dot":
        return f'<circle cx="{_f(x + 5)}" cy="{_f(yc)}" r="4.5" fill="{color}"/>'
    if kind == "ring":
        return f'<circle cx="{_f(x + 5)}" cy="{_f(yc)}" r="4" fill="#fff" stroke="{color}" stroke-width="2.2"/>'
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{_f(x + 1)}" y1="{_f(yc)}" x2="{_f(x + 19)}" y2="{_f(yc)}" stroke="{color}" '
            f'stroke-width="2.5" stroke-linecap="round"{d}/>')


def _flow(items, max_w, size=SIZE, gap=16):
    """จัด legend เป็นแถว ๆ ไม่ให้กว้างเกิน max_w → [[(item, width), …], …]"""
    rows, cur, used = [], [], 0.0
    for it in _items(items):
        w = _SW.get(it[2], 20) + 5 + text_w(it[0], size)
        if cur and used + gap + w > max_w:
            rows.append(cur)
            cur, used = [], 0.0
        used += (gap if cur else 0) + w
        cur.append((it, w))
    if cur:
        rows.append(cur)
    return rows


def _legend_row(row, x, y, anchor="start", size=SIZE, gap=16):
    """วาด legend หนึ่งแถว (baseline ที่ y) · anchor = start | end | middle เทียบกับ x"""
    total = sum(w for _, w in row) + gap * (len(row) - 1)
    cx = x - total if anchor == "end" else (x - total / 2 if anchor == "middle" else x)
    out = []
    for (label, color, kind, dash), w in row:
        out.append(_swatch(cx, y - 4, color, kind, dash))
        out.append(text(cx + _SW.get(kind, 20) + 5, y, label, size=size, color="#4b5563"))
        cx += w + gap
    return "".join(out)


def _lines(label):
    return str(label).split("\n")


# ───────────────────────── Fig + Panel ─────────────────────────

class Fig:
    """ผืนกราฟหนึ่งรูป (หนึ่ง <svg>) · cid = ชื่อกราฟ ใช้เป็น prefix ของทุก id ใน <defs>
    เพิ่มชิ้นส่วนตามลำดับที่เรียก (เรียกก่อน = อยู่ล่าง) แล้วปิดด้วย .svg(alt, cap)"""

    def __init__(self, cid, w=760, h=320):
        self.cid = re.sub(r"[^A-Za-z0-9_-]", "-", str(cid))
        self.w, self.h = float(w), float(h)
        self.defs, self.parts = [], []
        self._n = 0
        self._cache = {}

    def uid(self, tag="d"):
        """id ใหม่ที่ไม่ซ้ำในทั้งหน้า (ขึ้นต้นด้วย cid)"""
        self._n += 1
        return f"{self.cid}-{tag}{self._n}"

    def add(self, *parts):
        self.parts.extend(p for p in parts if p)
        return self

    def panel(self, xlim=(0.0, 1.0), ylim=(0.0, 1.0), x=None, y=None, w=None, h=None,
              left=58, top=34, right=18, bottom=44):
        """กรอบพล็อตหนึ่งกรอบ · ไม่ระบุ x/y/w/h = ใช้ทั้งรูปลบขอบ left/top/right/bottom"""
        x = left if x is None else x
        y = top if y is None else y
        w = self.w - x - right if w is None else w
        h = self.h - y - bottom if h is None else h
        return Panel(self, x, y, w, h, xlim, ylim)

    def text(self, x, y, s, **kw):
        return self.add(text(x, y, s, **kw))

    def title(self, s, sub=None, x=12, y=20, size=13):
        """หัวกราฟ (ตัวหนา สีหมึก) + คำอธิบายรองสีจาง ต่อท้ายในบรรทัดเดียวกัน"""
        raw = f'<tspan font-weight="700">{esc(s)}</tspan>'
        if sub:
            raw += f'<tspan fill="{MUTED}" font-size="{_f(size - 1.5)}">  {esc(sub)}</tspan>'
        return self.add(text(x, y, raw, size=size, raw=True))

    def legend(self, items, x, y, anchor="start", max_w=None, size=SIZE):
        """legend แนวนอน (ไม่มีกรอบ) เริ่มที่ baseline y · คืนจำนวนแถวที่ใช้ (แถวละ 17px)"""
        rows = _flow(items, max_w or self.w - 24, size)
        for i, row in enumerate(rows):
            self.add(_legend_row(row, x, y + 17 * i, anchor, size))
        return len(rows)

    def shadow(self, color):
        """filter เงานุ่มสีเดียวกับเส้น (ใช้กับเส้น hero) → id"""
        key = ("sh", color)
        if key not in self._cache:
            i = self.uid("sh")
            self.defs.append(f'<filter id="{i}" x="-10%" y="-30%" width="120%" height="160%">'
                             f'<feDropShadow dx="0" dy="1.5" stdDeviation="1.6" flood-color="{color}" '
                             f'flood-opacity=".28"/></filter>')
            self._cache[key] = i
        return self._cache[key]

    def svg(self, alt, cap=None):
        """ประกอบเป็น HTML: <svg class="fig" …>…</svg> + <div class="cap">…</div>"""
        defs = ["<defs>" + "".join(self.defs) + "</defs>"] if self.defs else []
        return wrap(self.w, self.h, alt, defs + self.parts, cap)


class Panel:
    """กรอบพล็อตหนึ่งกรอบ มีช่วงข้อมูลของตัวเอง (xlim, ylim) · ทุกเมธอดวาดคืน self จึงเรียกต่อกันได้
    พิกัดของเมธอดวาดเป็น "หน่วยข้อมูล" เสมอ · แปลงเป็นพิกเซลด้วย .X(v) .Y(v)"""

    def __init__(self, fig, x, y, w, h, xlim=(0.0, 1.0), ylim=(0.0, 1.0)):
        self.fig = fig
        self.x, self.y, self.w, self.h = float(x), float(y), float(w), float(h)
        self.x0, self.x1 = (float(v) for v in xlim)
        self.y0, self.y1 = (float(v) for v in ylim)
        if self.x1 == self.x0:
            self.x1 = self.x0 + 1.0
        if self.y1 == self.y0:
            self.y1 = self.y0 + 1.0
        self._rows = []            # แถวป้ายเหนือกรอบ (หัวข้อ/legend) ที่ถูกจองแล้ว
        self._below = 0.0          # พิกเซลใต้กรอบที่ถูกใช้ไปแล้ว (ป้ายแกน x)
        self._clip = None
        self._yticks = None
        self._xband_y = None       # baseline ของแถวป้าย xband (จองครั้งแรกที่มีป้าย)

    # ── พิกัด ──
    def X(self, v):
        return self.x + (np.asarray(v, float) - self.x0) / (self.x1 - self.x0) * self.w

    def Y(self, v):
        return self.y + self.h - (np.asarray(v, float) - self.y0) / (self.y1 - self.y0) * self.h

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y + self.h

    def _clip_attr(self):
        if self._clip is None:
            self._clip = self.fig.uid("clip")
            self.fig.defs.append(f'<clipPath id="{self._clip}"><rect x="{_f(self.x - 1)}" y="{_f(self.y - 1)}" '
                                 f'width="{_f(self.w + 2)}" height="{_f(self.h + 2)}"/></clipPath>')
        return f' clip-path="url(#{self._clip})"'

    def _top_slot(self, side, width):
        """จองที่ในแถวเหนือกรอบ (ซ้าย = หัวข้อ · ขวา = legend) → baseline y ของแถวนั้น"""
        r = self._rows
        if (not r or r[-1][side] is not None
                or (r[-1]["left"] or 0) + (r[-1]["right"] or 0) + width > self.w - 14):
            r.append({"left": None, "right": None})
        r[-1][side] = width
        return self.y - 9 - 17 * (len(r) - 1)

    def _note_row(self):
        """baseline ของแถวป้ายกำกับเหนือกรอบ (ป้ายของ xband และ vline pos="above" ใช้แถวเดียวกัน)"""
        if self._xband_y is None:
            self._xband_y = self._top_slot("left", self.w) + 4
        return self._xband_y

    def _path(self, xs, ys, max_points):
        """สตริง d ของเส้น (ตัดเป็นท่อนตรงที่เป็น NaN · ย่อจุดให้พอดีความกว้างกรอบ)"""
        xs, ys = np.asarray(xs, float), np.asarray(ys, float)
        ok = np.isfinite(xs) & np.isfinite(ys)
        budget = int(min(max_points, max(40, self.w / 2.5)))
        total = max(int(ok.sum()), 1)
        d, start = [], None
        for i in range(len(ok) + 1):
            if i < len(ok) and ok[i]:
                if start is None:
                    start = i
                continue
            if start is not None:
                rx, ry = downsample(xs[start:i], ys[start:i], max(8, round(budget * (i - start) / total)))
                px = self.X(rx)
                py = np.clip(self.Y(ry), self.y - 3 * self.h, self.y + 4 * self.h)
                d.append(_d(px, py))
                start = None
        return "".join(d)

    # ── โครง: grid · แกน ──
    def grid(self, yticks=None, xticks=None, n=5):
        """เส้น grid จาง ๆ · แนวนอนที่ yticks (ไม่ระบุ = เลขกลมอัตโนมัติ) · แนวตั้งเฉพาะเมื่อส่ง xticks"""
        yt = nice_ticks(self.y0, self.y1, n) if yticks is None else list(yticks)
        self._yticks = yt
        d = "".join(f"M{_f(self.x)} {_f(y)}H{_f(self.right)}" for y in self.Y(yt))
        if xticks is not None:
            d += "".join(f"M{_f(x)} {_f(self.y)}V{_f(self.bottom)}" for x in self.X(list(xticks)))
        if d:
            self.fig.add(f'<path d="{d}" fill="none" stroke="{GRID}" stroke-width="1"/>')
        return self

    def xaxis(self, ticks=None, labels=None, title=None, fmt=None, n=6, line=True):
        """แกน x: เส้นฐาน + ป้ายขีด + ชื่อแกน (title)
        ticks = ค่าบนแกน · labels = ลิสต์ข้อความ (รองรับ \\n) หรือ False = ไม่แสดงป้าย · fmt = ฟังก์ชันจัดรูป"""
        tk = nice_ticks(self.x0, self.x1, n) if ticks is None else list(ticks)
        out = []
        if line:
            out.append(f'<line x1="{_f(self.x)}" y1="{_f(self.bottom)}" x2="{_f(self.right)}" '
                       f'y2="{_f(self.bottom)}" stroke="{AXIS}" stroke-width="1.5"/>')
        depth = 0
        if labels is not False and tk:
            f = fmt or tick_fmt(tk)
            lab = [f(t) for t in tk] if labels is None else list(labels)
            for t, s in zip(tk, lab):
                for k, ln in enumerate(_lines(s)):
                    out.append(text(self.X(t), self.bottom + 16 + LINE_H * k, ln, size=11, color=MUTED,
                                    anchor="middle"))
                    depth = max(depth, 20 + LINE_H * k)
        if title:
            out.append(text(self.x + self.w / 2, self.bottom + depth + 17, title, size=12, color=MUTED,
                            anchor="middle"))
            depth += 22
        self._below = max(self._below, depth)
        self.fig.add("".join(out))
        return self

    def yaxis(self, ticks=None, labels=None, title=None, fmt=None, n=5, line=False):
        """แกน y: ป้ายขีดชิดซ้ายของกรอบ · title = หน่วยของแกน วางแนวนอนเหนือมุมซ้ายบน (ไม่หมุนตัวอักษร)
        ไม่ระบุ ticks = ใช้ชุดเดียวกับ grid() ที่เรียกไว้ก่อน"""
        tk = (self._yticks or nice_ticks(self.y0, self.y1, n)) if ticks is None else list(ticks)
        out = []
        if line:
            out.append(f'<line x1="{_f(self.x)}" y1="{_f(self.y)}" x2="{_f(self.x)}" y2="{_f(self.bottom)}" '
                       f'stroke="{AXIS}" stroke-width="1.5"/>')
        if labels is not False and tk:
            f = fmt or tick_fmt(tk)
            lab = [f(t) for t in tk] if labels is None else list(labels)
            for t, s in zip(tk, lab):
                out.append(text(self.x - 8, float(self.Y(t)) + 4, s, size=11, color=MUTED, anchor="end"))
        if title:
            y = self._top_slot("left", text_w(title, 11))
            out.append(text(self.x, y, title, size=11, color=MUTED))
        self.fig.add("".join(out))
        return self

    def title(self, s, sub=None, size=12.5):
        """หัวข้อของกรอบ วางเหนือมุมซ้ายบน · sub = คำอธิบายรองสีจางต่อท้าย"""
        y = self._top_slot("left", _title_w(s, sub, size))
        raw = f'<tspan font-weight="700">{esc(s)}</tspan>'
        if sub:
            raw += f'<tspan fill="{MUTED}" font-size="{_f(size - 1.5)}">  {esc(sub)}</tspan>'
        self.fig.add(text(self.x, y, raw, size=size, raw=True))
        return self

    def legend(self, items, pos="top", size=SIZE):
        """legend · pos="top" (ค่าเริ่มต้น) = แถวแนวนอนเหนือกรอบชิดขวา ไม่ทับข้อมูล
        pos = "tl" | "tr" | "bl" | "br" = กล่องในมุมกรอบ (ใช้เมื่อมุมนั้นว่างจริง)
        items = [(label, color[, kind[, dash]])] · kind = line | rect | dot | ring | band"""
        if pos == "top":
            rows = _flow(items, self.w - 8, size)
            for row in reversed(rows):           # แถวล่างสุดจองก่อน (อาจใช้แถวเดียวกับหัวข้อทางซ้าย)
                y = self._top_slot("right", sum(w for _, w in row) + 16 * (len(row) - 1))
                self.fig.add(_legend_row(row, self.right, y, "end", size))
            return self
        its = _items(items)
        bw = max(_SW.get(k, 20) + 5 + text_w(lab, size) for lab, _, k, _ in its) + 20
        bh = 17 * len(its) + 10
        bx = self.x + 10 if pos[1] == "l" else self.right - bw - 10
        by = self.y + 10 if pos[0] == "t" else self.bottom - bh - 10
        out = [f'<rect x="{_f(bx)}" y="{_f(by)}" width="{_f(bw)}" height="{_f(bh)}" rx="6" fill="#fff" '
               f'fill-opacity=".9" stroke="{GRID}"/>']
        for i, (lab, color, kind, dash) in enumerate(its):
            yc = by + 14 + 17 * i
            out.append(_swatch(bx + 10, yc - 0.5, color, kind, dash))
            out.append(text(bx + 15 + _SW.get(kind, 20), yc + 3.5, lab, size=size, color="#4b5563"))
        self.fig.add("".join(out))
        return self

    # ── ข้อมูล ──
    def line(self, xs, ys, color=BLUE, width=2.0, hero=False, dash=None, max_points=400, opacity=None):
        """เส้นข้อมูล ปลายมน · hero=True = เส้นเอกของภาพ (หนาขึ้น + เงานุ่ม) · ขาดช่วงตรงที่เป็น NaN
        อนุกรมยาวถูกย่ออัตโนมัติ (min/max ต่อช่วง) ไม่เกิน max_points จุด"""
        d = self._path(xs, ys, max_points)
        if not d:
            return self
        a = f' stroke-width="{_f(2.75 if hero and width <= 2 else width)}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' stroke-opacity="{opacity}"'
        if hero:
            a += f' filter="url(#{self.fig.shadow(color)})"'
        self.fig.add(f'<g{self._clip_attr()}><path d="{d}" fill="none" stroke="{color}" stroke-linecap="round" '
                     f'stroke-linejoin="round"{a}/></g>')
        return self

    def area(self, xs, ys, color=BLUE, base=None, color_below=None, top=0.26, bottom=0.03, max_points=400):
        """พื้นที่ไล่เฉดระหว่างเส้นกับเส้นฐาน base (ไม่ระบุ = 0 ถ้าอยู่ในช่วงแกน ไม่งั้นขอบล่าง)
        เข้มสุดที่ปลายข้อมูล จางเข้าหาเส้นฐาน · color_below = สีของส่วนที่อยู่ใต้เส้นฐาน"""
        rx, ry = downsample(xs, ys, int(min(max_points, max(40, self.w / 2.5))))
        if len(ry) < 2:
            return self
        if base is None:
            base = 0.0 if self.y0 <= 0.0 <= self.y1 else self.y0
        cb = color_below or color
        hi, lo = max(float(ry.max()), base), min(float(ry.min()), base)
        yt, yb, ym = float(self.Y(hi)), float(self.Y(lo)), float(self.Y(base))
        gid = self.fig.uid("ga")
        t = (ym - yt) / (yb - yt) if yb > yt else 1.0
        stops = []
        if hi > base:
            stops += [f'<stop offset="0" stop-color="{color}" stop-opacity="{top}"/>',
                      f'<stop offset="{t:.3f}" stop-color="{color}" stop-opacity="{bottom}"/>']
        if lo < base:
            stops += [f'<stop offset="{t:.3f}" stop-color="{cb}" stop-opacity="{bottom}"/>',
                      f'<stop offset="1" stop-color="{cb}" stop-opacity="{top}"/>']
        self.fig.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{_f(yt)}" '
                             f'x2="0" y2="{_f(yb)}">{"".join(stops)}</linearGradient>')
        px, py = self.X(rx), self.Y(ry)
        d = _d(np.concatenate([[px[0]], px, [px[-1]]]), np.concatenate([[ym], py, [ym]])) + "Z"
        self.fig.add(f'<g{self._clip_attr()}><path d="{d}" fill="url(#{gid})"/></g>')
        return self

    def hline(self, v, color=AXIS, width=1.2, dash="4 4", label=None, pos="right", below=False,
              label_color=MUTED, size=10.5, opacity=None):
        """เส้นอ้างอิงแนวนอน (ประ) ที่ค่า v · dash=None = เส้นทึบ
        label วางที่ pos = "right" | "left" (ในกรอบ เหนือเส้น · below=True = ใต้เส้น · มีขอบขาวกันทับข้อมูล)
        หรือ pos = "out" = นอกกรอบด้านขวา ระดับเดียวกับเส้น (ไม่ทับข้อมูลแน่นอน แต่ต้องเผื่อขอบขวาไว้เอง)"""
        if not (min(self.y0, self.y1) <= v <= max(self.y0, self.y1)):
            return self
        y = float(self.Y(v))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        if opacity is not None:
            d += f' stroke-opacity="{opacity}"'
        out = (f'<line x1="{_f(self.x)}" y1="{_f(y)}" x2="{_f(self.right)}" y2="{_f(y)}" stroke="{color}" '
               f'stroke-width="{_f(width)}"{d}/>')
        if label:
            ty = y + 13 if below else y - 5
            if pos == "out":
                out += text(self.right + 6, y + 3.5, label, size=size, color=label_color)
            elif pos == "left":
                out += text(self.x + 6, ty, label, size=size, color=label_color, halo=True)
            else:
                out += text(self.right - 6, ty, label, size=size, color=label_color, anchor="end", halo=True)
        self.fig.add(out)
        return self

    def vline(self, v, color=AXIS, width=1.2, dash="4 4", label=None, pos="top", side=None,
              label_color=MUTED, size=10.5):
        """เส้นอ้างอิงแนวตั้งที่ค่า v · label วางที่ pos = "top" | "bottom" (ในกรอบ มีขอบขาว) ด้าน side = "right" | "left"
        (ไม่ระบุ side = เลือกด้านที่ไม่ล้นกรอบให้เอง) · หรือ pos = "above" = เหนือกรอบ ตรงกับเส้น
        (ไม่ทับข้อมูลแน่นอน · ใช้แถวป้ายเดียวกับ xband — เรียกก่อน title()/legend() และเผื่อขอบบน 17px)"""
        if not (min(self.x0, self.x1) <= v <= max(self.x0, self.x1)):
            return self
        x = float(self.X(v))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out = (f'<line x1="{_f(x)}" y1="{_f(self.y)}" x2="{_f(x)}" y2="{_f(self.bottom)}" stroke="{color}" '
               f'stroke-width="{_f(width)}"{d}/>')
        if label and pos == "above":
            half = text_w(label, size) / 2
            out += text(min(max(x, self.x + half), self.right - half), self._note_row(), label, size=size,
                        color=label_color, anchor="middle")
        elif label:
            if side is None:
                side = "left" if x + 8 + text_w(label, size) > self.right else "right"
            ty = self.y + 13 if pos == "top" else self.bottom - 7
            out += text(x + (6 if side == "right" else -6), ty, label, size=size, color=label_color,
                        anchor="start" if side == "right" else "end", halo=True)
        self.fig.add(out)
        return self

    def band(self, lo=None, hi=None, color=BLUE, opacity=0.08, label=None, pos="left", size=10.5):
        """แถบแนวนอนระหว่างค่า y = lo ถึง hi (None = สุดขอบกรอบ)
        label วางในแถบชิด pos = "left" | "right" · หรือ pos = "out" = นอกกรอบด้านขวา กลางแถบ (ต้องเผื่อขอบขวาเอง)"""
        a = self.y0 if lo is None else max(min(lo, self.y1), self.y0)
        b = self.y1 if hi is None else max(min(hi, self.y1), self.y0)
        ya, yb = float(self.Y(b)), float(self.Y(a))
        out = (f'<rect x="{_f(self.x)}" y="{_f(ya)}" width="{_f(self.w)}" height="{_f(max(yb - ya, 0))}" '
               f'fill="{color}" fill-opacity="{opacity}"/>')
        if label:
            if pos == "out":
                out += text(self.right + 6, (ya + yb) / 2 + 3.5, label, size=size, color=MUTED)
            elif pos == "left":
                out += text(self.x + 6, ya + 13, label, size=size, color=MUTED, halo=True)
            else:
                out += text(self.right - 6, ya + 13, label, size=size, color=MUTED, anchor="end", halo=True)
        self.fig.add(out)
        return self

    def xband(self, lo=None, hi=None, color=MUTED, opacity=0.08, label=None, size=10.5):
        """แถบแนวตั้งระหว่างค่า x = lo ถึง hi (เช่น ช่วง train / ช่วง test)
        label วางกลางแถบ "เหนือกรอบ" (จองแถวป้ายหนึ่งแถว ใช้ร่วมกันทุก xband — เรียกก่อน title()/legend()
        แล้วเผื่อขอบบนเพิ่ม 17px)"""
        a = self.x0 if lo is None else max(min(lo, self.x1), self.x0)
        b = self.x1 if hi is None else max(min(hi, self.x1), self.x0)
        xa, xb = float(self.X(a)), float(self.X(b))
        out = (f'<rect x="{_f(xa)}" y="{_f(self.y)}" width="{_f(max(xb - xa, 0))}" height="{_f(self.h)}" '
               f'fill="{color}" fill-opacity="{opacity}"/>')
        if label:
            out += text((xa + xb) / 2, self._note_row(), label, size=size, color=MUTED, anchor="middle")
        self.fig.add(out)
        return self

    def scatter(self, xs, ys, color=BLUE, r=2.4, opacity=0.5, ring=False):
        """จุดกระจาย · ring=False = จุดทึบโปร่งแสง (เบามาก เหมาะกับหลายร้อยจุด)
        ring=True = จุดมีขอบขาว (ใช้กับจุดจำนวนน้อยที่ต้องเด่น เช่น จุดบนเส้น)"""
        xs, ys = np.asarray(xs, float), np.asarray(ys, float)
        ok = np.isfinite(xs) & np.isfinite(ys)
        px, py = self.X(xs[ok]), self.Y(ys[ok])
        if ring:
            s = "".join(f'<circle cx="{_f(u)}" cy="{_f(v)}" r="{_f(r)}"/>' for u, v in zip(px, py))
            self.fig.add(f'<g fill="{color}" stroke="#fff" stroke-width="2">{s}</g>')
        else:
            order = np.argsort(px)
            d, cx, cy = [], 0.0, 0.0
            for u, v in zip(px[order], py[order]):      # ขยับแบบสัมพัทธ์จากจุดก่อนหน้า (ติดตามตำแหน่งจริง ไม่สะสมคลาด)
                du, dv = round(float(u) - cx, 1), round(float(v) - cy, 1)
                d.append(f"m{_n(du)} {_n(dv)}h.01")
                cx, cy = cx + du + 0.01, cy + dv
            d = "".join(d).replace(" -", "-")
            self.fig.add(f'<g{self._clip_attr()}><path d="{d}" fill="none" stroke="{color}" '
                         f'stroke-width="{_f(2 * r)}" stroke-linecap="round" stroke-opacity="{opacity}"/></g>')
        return self

    def bars(self, xs, vals, color=BLUE, width=None, base=0.0, colors=None, labels=None, fmt=None,
             r=3.0, label_size=10.5):
        """แท่งแนวตั้ง กึ่งกลางที่ xs สูงจาก base ถึง vals · ปลายข้อมูลมน โคนเหลี่ยม · width เป็นพิกเซล (≤ 24)
        labels=True = พิมพ์ค่าที่ปลายแท่ง (จัดรูปด้วย fmt) · หรือส่งลิสต์ข้อความ · colors = สีรายแท่ง"""
        xs, vals = np.asarray(xs, float), np.asarray(vals, float)
        px = self.X(xs)
        if width is None:
            gap = float(np.min(np.diff(np.sort(px)))) if len(px) > 1 else self.w * 0.5
            width = min(24.0, 0.62 * gap)
        yb = float(self.Y(base))
        out = []
        f = fmt or num
        for i, (cx, v) in enumerate(zip(px, vals)):
            if not math.isfinite(v):
                continue
            yt = float(self.Y(v))
            rr = min(r, width / 2, abs(yb - yt))
            s = 1 if yt <= yb else -1
            x0, x1 = cx - width / 2, cx + width / 2
            c = colors[i] if colors else color
            out.append(f'<path d="M{_f(x0)},{_f(yb)}V{_f(yt + s * rr)}Q{_f(x0)},{_f(yt)} {_f(x0 + rr)},{_f(yt)}'
                       f'H{_f(x1 - rr)}Q{_f(x1)},{_f(yt)} {_f(x1)},{_f(yt + s * rr)}V{_f(yb)}Z" fill="{c}"/>')
            if labels:
                lab = f(v) if labels is True else labels[i]
                out.append(text(cx, yt - 5 if s == 1 else yt + 13, lab, size=label_size, color=INK,
                                anchor="middle", halo=True))
        self.fig.add("".join(out))
        return self

    def hbars(self, ys, vals, color=BLUE, height=None, base=0.0, colors=None, labels=None, fmt=None,
              r=3.0, label_size=11):
        """แท่งแนวนอน กึ่งกลางที่ ys ยาวจาก base ถึง vals · height เป็นพิกเซล (≤ 24) · labels เหมือน bars()"""
        ys, vals = np.asarray(ys, float), np.asarray(vals, float)
        py = self.Y(ys)
        if height is None:
            gap = float(np.min(np.abs(np.diff(np.sort(py))))) if len(py) > 1 else self.h * 0.5
            height = min(24.0, 0.62 * gap)
        xb = float(self.X(base))
        out = []
        f = fmt or num
        for i, (cy, v) in enumerate(zip(py, vals)):
            if not math.isfinite(v):
                continue
            xt = float(self.X(v))
            rr = min(r, height / 2, abs(xt - xb))
            s = 1 if xt >= xb else -1
            y0, y1 = cy - height / 2, cy + height / 2
            c = colors[i] if colors else color
            out.append(f'<path d="M{_f(xb)},{_f(y0)}H{_f(xt - s * rr)}Q{_f(xt)},{_f(y0)} {_f(xt)},{_f(y0 + rr)}'
                       f'V{_f(y1 - rr)}Q{_f(xt)},{_f(y1)} {_f(xt - s * rr)},{_f(y1)}H{_f(xb)}Z" fill="{c}"/>')
            if labels:
                lab = f(v) if labels is True else labels[i]
                out.append(text(xt + 6 * s, cy + 4, lab, size=label_size, color=INK,
                                anchor="start" if s == 1 else "end", halo=True))
        self.fig.add("".join(out))
        return self

    def hist(self, edges, heights, color=BLUE, horizontal=False, colors=None, opacity=1.0, gap=1.0):
        """ฮิสโทแกรมจากขอบช่อง edges (ยาว n+1) และความสูง heights (ยาว n) — แท่งชิดกัน เว้นช่อง gap px
        horizontal=True = นอนตะแคง (ค่าอยู่บนแกน y ความถี่อยู่บนแกน x) · colors = สีรายช่อง"""
        out = []
        for i, hgt in enumerate(heights):
            if not hgt or not math.isfinite(hgt):
                continue
            c = colors[i] if colors else color
            if horizontal:
                ya, yb = float(self.Y(edges[i + 1])), float(self.Y(edges[i]))
                xa, xb = float(self.X(0.0)), float(self.X(hgt))
                out.append(f'<rect x="{_f(xa)}" y="{_f(ya + gap / 2)}" width="{_f(max(xb - xa, 0.5))}" '
                           f'height="{_f(max(yb - ya - gap, 0.5))}" fill="{c}"/>')
            else:
                xa, xb = float(self.X(edges[i])), float(self.X(edges[i + 1]))
                ya, yb = float(self.Y(hgt)), float(self.Y(0.0))
                out.append(f'<rect x="{_f(xa + gap / 2)}" y="{_f(ya)}" width="{_f(max(xb - xa - gap, 0.5))}" '
                           f'height="{_f(max(yb - ya, 0.5))}" fill="{c}"/>')
        op = f' fill-opacity="{opacity}"' if opacity != 1.0 else ""
        self.fig.add(f'<g{op}>{"".join(out)}</g>')
        return self

    # ── คำอธิบาย ──
    def text(self, x, y, s, dx=0.0, dy=0.0, **kw):
        """ข้อความที่ตำแหน่งข้อมูล (x, y) เลื่อน dx, dy พิกเซล · kw ส่งต่อให้ text() (size, color, anchor, weight, halo)"""
        self.fig.add(text(float(self.X(x)) + dx, float(self.Y(y)) + dy, s, **kw))
        return self

    def gutter_labels(self, items, size=10.5, gap=12.0, color=MUTED):
        """ป้ายหลายอันในร่องขวานอกกรอบ แต่ละอันตรงกับระดับค่า y ของตัวเอง — ถ้าชิดกันจะขยับหลบกันเอง
        พร้อมขีดโยงสั้น ๆ (ใช้แทน hline(pos="out") เมื่อมีหลายเส้นใกล้กัน) · items = [(ค่า y, ข้อความ), …]
        ต้องเผื่อขอบขวาของกรอบไว้เอง (ราว text_w(ข้อความ, 10.5) + 16)"""
        its = [(float(v), t) for v, t in items if t and min(self.y0, self.y1) <= v <= max(self.y0, self.y1)]
        ys = [float(self.Y(v)) for v, _ in its]
        out = []
        for (_, t), y0, y1 in zip(its, ys, declutter(ys, gap, self.y + 4, self.bottom - 2)):
            if abs(y1 - y0) > 1.5:
                out.append(f'<path d="M{_f(self.right)} {_f(y0)}L{_f(self.right + 5)} {_f(y1)}" fill="none" '
                           f'stroke="{AXIS}" stroke-width="1"/>')
            out.append(text(self.right + 8, y1 + 3.5, t, size=size, color=color))
        self.fig.add("".join(out))
        return self

    def callout(self, x, y, label, dx=44.0, dy=-30.0, color=PURPLE, size=SIZE, r=4.5):
        """ชี้จุดสำคัญ: จุดกลวง + เส้นโค้งนำสายตา + ป้ายตัวหนา (ป้ายใช้สี color โดยจงใจ)
        dx, dy = ตำแหน่งป้ายเทียบกับจุด (พิกเซล) · พลิกด้านให้เองถ้าป้ายจะล้นกรอบ"""
        px, py = float(self.X(x)), float(self.Y(y))
        tw = text_w(label, size) * 1.08
        if dx > 0 and px + dx + tw > self.right + 4:
            dx = -abs(dx)
        elif dx < 0 and px + dx - tw < self.x - 4:
            dx = abs(dx)
        if dy < 0 and py + dy < self.y + 8:
            dy = abs(dy)
        elif dy > 0 and py + dy > self.bottom - 4:
            dy = -abs(dy)
        tx, ty = px + dx, py + dy
        self.fig.add(
            f'<path d="M{_f(px)},{_f(py)}C{_f(px + dx * 0.45)},{_f(ty)} {_f(px + dx * 0.7)},{_f(ty)} '
            f'{_f(tx)},{_f(ty)}" fill="none" stroke="{color}" stroke-width="1"/>'
            f'<circle cx="{_f(px)}" cy="{_f(py)}" r="{_f(r)}" fill="#fff" stroke="{color}" stroke-width="2.5"/>'
            + text(tx + (4 if dx >= 0 else -4), ty + 4, label, size=size, color=color, weight=700,
                   anchor="start" if dx >= 0 else "end", halo=True))
        return self


# ───────────────────────── ตัวสร้างสำเร็จรูป ─────────────────────────

def _series_list(y):
    """y เดี่ยว (อนุกรมเดียว) หรือ ลิสต์ของอนุกรม (หรือ array สองมิติ แถวละอนุกรม) → ลิสต์ของ array"""
    if isinstance(y, np.ndarray) and y.ndim == 2:
        return [np.asarray(v, float) for v in y]
    if isinstance(y, (list, tuple)) and len(y) and hasattr(y[0], "__len__"):
        return [np.asarray(v, float) for v in y]
    return [np.asarray(y, float)]


def _colors(spec, n):
    if spec is None:
        return [SERIES[i % len(SERIES)] for i in range(n)]
    if isinstance(spec, str):
        return [spec] * n
    return list(spec)


def _legend_w(row):
    return sum(w for _, w in row) + 16 * (len(row) - 1)


def _head_rows(pw, left_w=0.0, rows=()):
    """จำนวนแถวป้ายเหนือกรอบที่ต้องเผื่อไว้: ป้ายซ้าย (หัวข้อ / หน่วยแกน y) + legend ขวา
    ใช้แถวล่างสุดร่วมกันถ้ากว้างพอ — ตรรกะเดียวกับ Panel._top_slot"""
    n = 1 if left_w else 0
    for i, row in enumerate(reversed(list(rows))):
        if i == 0 and n == 1 and left_w + _legend_w(row) <= pw - 14:
            continue
        n += 1
    return n


def _title_w(s, sub=None, size=12.5):
    """ความกว้างโดยประมาณของหัวข้อกรอบ (ตัวหนา) รวมคำอธิบายรอง — ต้องตรงกับที่ Panel.title จองไว้"""
    return text_w(s, size) * 1.06 + (text_w(sub, size - 1.5) + 8 if sub else 0)


def stacked_panels(cid, panels, alt, cap, x=None, w=760, panel_h=112, xlabel=None, share_y=False,
                   xticks=None, xlabels=None, xbands=None):
    """หลายกรอบอนุกรมเวลาเรียงแนวตั้ง ใช้แกน x ร่วมกัน (แบบสไลด์ "Asset A / Asset B / Spread")
    panels = [{"y": อนุกรม หรือ [อนุกรม, …], "title": หัวข้อกรอบ, "sub": คำอธิบายรอง,
               "color": สี หรือ [สี, …], "names": [ชื่อ, …] (legend เมื่อมีหลายเส้น),
               "zero": วาดเส้นประที่ 0 (ค่าเริ่มต้น = อัตโนมัติ), "ylim": (lo, hi), "hero": bool,
               "hlines": [(ค่า, ป้าย[, สี]), …]}]
    share_y=True = ทุกกรอบใช้สเกล y เดียวกัน (เทียบขนาดการแกว่งได้ตรง ๆ)
    xbands = [(lo, hi, ป้าย[, สี]), …] แถบแนวตั้งในทุกกรอบ (ป้ายเฉพาะกรอบบน)"""
    L = 58
    labs = [h[1] for p in panels for h in p.get("hlines", []) if h[1]]
    R = max([18.0] + [text_w(s, 10.5) + 18 for s in labs])      # ร่องขวาสำหรับป้ายของ hlines
    B = 46 if xlabel else 26
    n = len(panels)
    pw = w - L - R
    allys = [_series_list(p["y"]) for p in panels]
    note = any(b[2] for b in (xbands or []))                    # แถวป้ายของ xband (เฉพาะกรอบบนสุด)
    # ความสูงของหัวแต่ละกรอบขึ้นกับจำนวนแถวที่หัวข้อ + legend ต้องใช้ (หัวข้อยาว → legend ขึ้นแถวใหม่)
    legends, tops, y = [], [], 0.0
    for i, (p, ys) in enumerate(zip(panels, allys)):
        cols = _colors(p.get("color"), len(ys))
        items = ([(nm, cols[k], "line", DASHES[k % len(DASHES)] if p.get("color") is None else None)
                  for k, nm in enumerate(p["names"])] if p.get("names") and len(ys) > 1 else [])
        legends.append(items)
        rows = _head_rows(pw, _title_w(p["title"], p.get("sub")) if p.get("title") else 0,
                          _flow(items, pw - 8) if items else []) + (1 if note and i == 0 else 0)
        y += 15 + 17 * max(rows, 1) + (6 if i else 0)
        tops.append(y)
        y += panel_h
    fig = Fig(cid, w, y + B)
    npts = max(len(v) for ys in allys for v in ys)
    xs = np.arange(npts, dtype=float) if x is None else np.asarray(x, float)
    xlim = (float(np.nanmin(xs)), float(np.nanmax(xs)))
    shared = auto_lim(*[v for ys in allys for v in ys], n=4) if share_y else None
    for i, (p, ys) in enumerate(zip(panels, allys)):
        extra = [h[0] for h in p.get("hlines", [])]
        ylim = p.get("ylim") or shared or auto_lim(*ys, include=extra, n=4)
        pan = fig.panel(xlim, ylim, x=L, y=tops[i], w=pw, h=panel_h)
        for b in xbands or []:
            pan.xband(b[0], b[1], color=b[3] if len(b) > 3 else MUTED, label=b[2] if i == 0 else None)
        pan.grid(n=4).yaxis()
        if p.get("zero", ylim[0] < 0 < ylim[1]):
            pan.hline(0.0, color="#94a3b8")
        for h in p.get("hlines", []):
            pan.hline(h[0], color=h[2] if len(h) > 2 else "#94a3b8")
        pan.gutter_labels([(h[0], h[1]) for h in p.get("hlines", [])])
        cols = _colors(p.get("color"), len(ys))
        for k, v in enumerate(ys):
            pan.line(xs[:len(v)], v, cols[k], hero=p.get("hero", False) and k == 0,
                     dash=DASHES[k % len(DASHES)] if len(ys) > 1 and p.get("color") is None else None)
        if p.get("title"):
            pan.title(p["title"], p.get("sub"))
        if legends[i]:
            pan.legend(legends[i])
        last = i == n - 1
        pan.xaxis(ticks=xticks, labels=(xlabels if last else False), title=xlabel if last else None)
    return fig.svg(alt, cap)


def series_with_hist(cid, rows, alt, cap=None, x=None, w=760, row_h=150, bins=22, xlabel=None,
                     hist_xlabel=None, share_y=False):
    """อนุกรมเวลา (ซ้าย) คู่กับฮิสโทแกรมของค่าเดียวกัน (ขวา) · หนึ่งแถวต่อหนึ่งอนุกรม
    rows = dict เดียว หรือ ลิสต์ของ dict → ส่งสองแถว = รูป 2×2 แบบสไลด์ "Non-Stationary vs Stationary"
      {"y": อนุกรม, "title": หัวข้อกรอบซ้าย, "hist_title": หัวข้อกรอบขวา, "color": สี,
       "ylim": (lo, hi), "mean": True = ขีดเส้นค่าเฉลี่ยทั้งสองกรอบ}
    (เรียกสองครั้งโดยให้ครั้งแรก cap=None ก็ได้ ถ้าอยากได้สอง <svg> แยกกัน — cid ต้องต่างกัน)"""
    rows = [rows] if isinstance(rows, dict) else list(rows)
    L, R, MID = 58, 16, 62
    B = 46 if (xlabel or hist_xlabel) else 26
    n = len(rows)
    wl = round((w - L - R - MID) * 0.64)
    wr = w - L - R - MID - wl
    mean_item = [("ค่าเฉลี่ยทั้งช่วง", "#64748b", "line", "4 4")]
    tops, yy = [], 0.0
    for i, r in enumerate(rows):                 # หัวข้อยาวจน legend ต้องขึ้นแถวใหม่ → เผื่อหัวกรอบสูงขึ้น
        k = _head_rows(wl, _title_w(r["title"], r.get("sub")) if r.get("title") else 0,
                       _flow(mean_item, wl - 8) if r.get("mean") else [])
        yy += 15 + 17 * max(k, 1) + (26 if i else 0)
        tops.append(yy)
        yy += row_h
    fig = Fig(cid, w, yy + B)
    shared = auto_lim(*[r["y"] for r in rows], n=4) if share_y else None
    for i, r in enumerate(rows):
        y = np.asarray(r["y"], float)
        xs = np.arange(len(y), dtype=float) if x is None else np.asarray(x, float)
        color = r.get("color", SERIES[i % len(SERIES)])
        ylim = r.get("ylim") or shared or auto_lim(y, n=4)
        top = tops[i]
        last = i == n - 1
        a = fig.panel((float(np.nanmin(xs)), float(np.nanmax(xs))), ylim, x=L, y=top, w=wl, h=row_h)
        a.grid(n=4).yaxis()
        if r.get("mean"):
            a.hline(float(np.nanmean(y)), color="#64748b")
        a.line(xs, y, color)
        a.xaxis(title=xlabel if last else None)
        if r.get("title"):
            a.title(r["title"], r.get("sub"))
        if r.get("mean"):
            a.legend(mean_item)
        fin = y[np.isfinite(y)]
        cnt, edges = np.histogram(fin, bins=r.get("bins", bins), range=(float(fin.min()), float(fin.max())))
        b = fig.panel(ylim, (0.0, float(cnt.max()) * 1.12), x=L + wl + MID, y=top, w=wr, h=row_h)
        b.grid(n=3).yaxis(fmt=lambda v: num(v, 0))
        b.hist(edges, cnt, color, opacity=0.85)
        if r.get("mean"):
            b.vline(float(np.nanmean(y)), color="#64748b")
        b.xaxis(n=4, title=hist_xlabel if last else None)
        if r.get("hist_title"):
            b.title(r["hist_title"])
    return fig.svg(alt, cap)


def _pct_label(p):
    p = float(p)
    return str(int(p)) if p == int(p) else f"{p:g}"


def zone_chart(cid, eps, pcts, alt, cap, x=None, w=780, h=372, mark_last=False,
               label="VaR {p}%: {v}", decimals=None, titles=("การกระจายของ ε", "ε ตามเวลา กับเส้นเปอร์เซ็นไทล์"),
               xlabel="แท่งที่ (วัน)", xticks=None, xlabels=None, bins=28, kde=True, ylim=None, color=DARK):
    """กราฟ "Error Distribution + Error Time Series with VaR Zones" แบบในสไลด์
    ซ้าย = ฮิสโทแกรมนอนตะแคงของ ε (+ เส้นความหนาแน่น) · ขวา = ε ตามเวลา พร้อมเส้นเปอร์เซ็นไทล์แนวนอน
    แรเงาฟ้าเหนือมัธยฐาน แดงใต้มัธยฐาน · ป้ายของทุกเส้นเรียงในร่องขวา ไม่ทับข้อมูลและไม่ทับกันเอง
      eps   = อนุกรมของ ε
      pcts  = {เปอร์เซ็นไทล์: ค่า} เช่น {1: -1.46, 10: -0.91, …, 99: 1.52} (คีย์เป็น int หรือ str ก็ได้)
      label = รูปแบบป้าย ใช้ {p} และ {v} · decimals = ทศนิยมของ {v} (ไม่ระบุ = เลือกตามขนาดของช่วง)
      mark_last = True หรือ ข้อความ → ชี้จุดสุดท้ายของอนุกรม (ค่าเริ่มต้นของป้าย = "ล่าสุด <ค่า>")"""
    eps = np.asarray(eps, float)
    xs = np.arange(len(eps), dtype=float) if x is None else np.asarray(x, float)
    pv = sorted((float(k), float(v)) for k, v in dict(pcts).items())
    med = dict(pv).get(50.0, float(np.nanmedian(eps)))
    fin = eps[np.isfinite(eps)]
    ylim = ylim or auto_lim(fin, [v for _, v in pv], n=6, pad=0.05)
    if decimals is None:                         # ราว 3 เลขนัยสำคัญของช่วงค่า: ±1.5 → 2 ตำแหน่ง · ±100 → 1 · ±0.0005 → 5
        span = max(v for _, v in pv) - min(v for _, v in pv) if len(pv) > 1 else float(fin.max() - fin.min())
        decimals = (0 if span >= 1000 else 1 if span >= 100 else 2 if span >= 1
                    else min(8, 2 + math.ceil(-math.log10(span))) if span > 0 else 2)
    labs = [label.format(p=_pct_label(p), v=num(v, decimals)) for p, v in pv]
    L, T, B, HW, MID = 54, 34, 46, 118, 26
    gut = max((text_w(s, 10.5) for s in labs), default=60) + 22
    fig = Fig(cid, w, h)
    ph = h - T - B

    # ซ้าย: ฮิสโทแกรมนอนตะแคง
    dens, edges = np.histogram(fin, bins=bins, range=(float(fin.min()), float(fin.max())), density=True)
    curve = None
    if kde and len(fin) > 20 and fin.std() > 0:
        bw = 1.06 * float(fin.std()) * len(fin) ** -0.2
        gy = np.linspace(float(fin.min()) - 2 * bw, float(fin.max()) + 2 * bw, 60)
        curve = np.exp(-0.5 * ((gy[:, None] - fin[None, :]) / bw) ** 2).mean(axis=1) / (bw * math.sqrt(2 * math.pi))
    dmax = max(float(dens.max()), float(curve.max()) if curve is not None else 0.0) * 1.08
    a = fig.panel((0.0, dmax), ylim, x=L, y=T, w=HW, h=ph)
    a.band(med, None, BLUE, 0.06).band(None, med, RED, 0.06)
    a.grid(n=6).yaxis()
    mids = (edges[:-1] + edges[1:]) / 2
    a.hist(edges, dens, horizontal=True, colors=[BLUE if m >= med else RED for m in mids], opacity=0.55)
    if curve is not None:
        fig.add(f'<path d="{_d(a.X(curve), a.Y(gy))}" fill="none" stroke="{INK}" stroke-width="1.5" '
                f'stroke-linejoin="round"{a._clip_attr()}/>')
    a.xaxis(labels=False, title="ความถี่")
    a.title(titles[0])

    # ขวา: อนุกรมเวลา + เส้นเปอร์เซ็นไทล์
    b = fig.panel((float(np.nanmin(xs)), float(np.nanmax(xs))), ylim, x=L + HW + MID, y=T, w=w - L - HW - MID - gut,
                  h=ph)
    b.band(med, None, BLUE, 0.07).band(None, med, RED, 0.07)
    b.grid(yticks=a._yticks)
    for p, v in pv:
        mid, edge = p == 50.0, (p <= 1.0 or p >= 99.0)
        c = INK if mid else (BLUE if v >= med else RED)
        b.hline(v, color=c, width=1.5 if (mid or edge) else 1.0, dash=None if mid else ("6 3" if edge else "3 3"),
                opacity=None if (mid or edge) else 0.8)
    b.line(xs, eps, color, width=1.5)
    b.xaxis(ticks=xticks, labels=xlabels, title=xlabel)
    b.title(titles[1])
    ys = [float(b.Y(v)) - 1e-6 * p for p, v in pv]       # ค่าเท่ากัน → เปอร์เซ็นไทล์สูงอยู่บน
    ly = declutter(ys, 12.5, T + 4, T + ph - 2)
    for (p, v), y0, y1, s in zip(pv, ys, ly, labs):
        strong = p == 50.0 or p <= 1.0 or p >= 99.0
        fig.add(f'<path d="M{_f(b.right)},{_f(y0)}L{_f(b.right + 9)},{_f(y1)}H{_f(b.right + 13)}" fill="none" '
                f'stroke="{AXIS}" stroke-width="1"/>'
                + text(b.right + 16, y1 + 3.5, s, size=10.5, color=INK if strong else MUTED,
                       weight=700 if strong else None))
    if mark_last:                                # ป้ายอยู่เหนือกรอบ (ไม่ทับข้อมูล) โยงลงมาที่จุดสุดท้าย
        k = int(np.max(np.nonzero(np.isfinite(eps))[0]))
        s = mark_last if isinstance(mark_last, str) else f"ล่าสุด {num(eps[k], decimals)}"
        px, py = float(b.X(xs[k])), float(b.Y(eps[k]))
        fig.add(f'<path d="M{_f(px)} {_f(py)}V{_f(T - 5)}" fill="none" stroke="{PURPLE}" stroke-width="1"/>'
                f'<circle cx="{_f(px)}" cy="{_f(py)}" r="4.5" fill="#fff" stroke="{PURPLE}" stroke-width="2.5"/>'
                + text(px + 2, T - 9, s, size=11.5, color=PURPLE, weight=700, anchor="end"))
    return fig.svg(alt, cap)


def heat_table(cid, row_labels, col_labels, values, alt, cap, scale="seq", fmt=None, row_title=None,
               col_title=None, lo=None, hi=None, center=0.0, color=BLUE, pos=BLUE, neg=RED,
               w=760, cell_h=34, legend=True):
    """ตารางตัวเลขระบายสี (ตาราง power · ตารางต้นทุน) — พิมพ์ตัวเลขในทุกช่อง
      values[r][c]  ค่าของแถว r คอลัมน์ c (None/NaN = ช่องว่าง)
      scale="seq"   สีเดียวไล่อ่อน→เข้ม ตามขนาด (lo…hi) · color = สีของสเกล
      scale="div"   สองขั้วรอบ center: ต่ำกว่า = neg (แดง) · สูงกว่า = pos (น้ำเงิน) · กลาง = เทา
                    (อยากได้ เขียว=กำไร ส่ง pos=V.GREEN ได้ แต่แดง↔เขียวแยกไม่ออกสำหรับคนตาบอดสี
                     ตัวเลขในช่องจึงต้องมีเครื่องหมายเสมอ)
      fmt           ฟังก์ชัน หรือ สตริงรูปแบบ เช่น "{:.0f}%" (ไม่ระบุ = num())
      row_title / col_title = ชื่อของแกนแถว / แกนคอลัมน์ · row/col label รองรับ \\n"""
    vals = [[None if (v is None or not math.isfinite(float(v))) else float(v) for v in row] for row in values]
    flat = [v for row in vals for v in row if v is not None] or [0.0]
    lo = min(flat) if lo is None else lo
    hi = max(flat) if hi is None else hi
    if isinstance(fmt, str):
        pattern = fmt
        fmt = lambda v: minus(pattern.format(v))
    fmt = fmt or num
    nr, nc = len(vals), len(col_labels)
    cell_h = max(cell_h, LINE_H * max(len(_lines(s)) for s in row_labels) + 6)
    left = min(250, max(72, max(text_w(ln, 11.5) for s in list(row_labels) + [row_title or ""]
                                for ln in _lines(s)) + 20))
    R = 14
    head = 25 + LINE_H * (max(len(_lines(c)) for c in col_labels) - 1)
    T = 8 + (20 if col_title else 0) + head
    cw = (w - left - R) / nc
    H = T + nr * cell_h + (40 if legend else 10)
    fig = Fig(cid, w, H)
    if col_title:
        fig.text(left + (w - left - R) / 2, 20, col_title, size=11.5, color=MUTED, anchor="middle")
    if row_title:
        fig.text(left - 12, T - 9, row_title, size=11.5, color=MUTED, anchor="end")
    for c, s in enumerate(col_labels):
        ls = _lines(s)
        for k, ln in enumerate(ls):
            fig.text(left + (c + 0.5) * cw, T - 9 - LINE_H * (len(ls) - 1 - k), ln, size=11.5, color=INK,
                     anchor="middle", weight=700)

    def fill(v):
        if scale == "div":
            m = max(abs(hi - center), abs(lo - center)) or 1.0
            t = (v - center) / m
            return mix(NEUTRAL, pos if t >= 0 else neg, min(1.0, abs(t)) ** 0.8 * 0.92)
        t = (v - lo) / (hi - lo) if hi > lo else 0.5
        return mix("#ffffff", color, 0.07 + 0.88 * min(1.0, max(0.0, t)))

    cells = []
    for r in range(nr):
        y = T + r * cell_h
        ls = _lines(row_labels[r])
        for k, ln in enumerate(ls):
            fig.text(left - 12, y + cell_h / 2 + 4 - LINE_H / 2 * (len(ls) - 1) + LINE_H * k, ln, size=11.5,
                     color=INK, anchor="end")
        for c in range(nc):
            v = vals[r][c] if c < len(vals[r]) else None
            f = "#fafafa" if v is None else fill(v)
            cells.append(f'<rect x="{_f(left + c * cw + 1)}" y="{_f(y + 1)}" width="{_f(cw - 2)}" '
                         f'height="{_f(cell_h - 2)}" rx="4" fill="{f}"/>'
                         + text(left + (c + 0.5) * cw, y + cell_h / 2 + 4.5, "–" if v is None else fmt(v),
                                size=12.5, color=MUTED if v is None else ink_on(f), anchor="middle", weight=600))
    fig.add("".join(cells))
    if legend:
        # แถบสเกลสี: ค่าต่ำสุด ▯▯▯▯▯▯▯▯▯ ค่าสูงสุด (ชิดขวาใต้ตาราง)
        y = T + nr * cell_h + 16
        n, sw = 9, 20
        m = max(abs(hi - center), abs(lo - center))
        ramp = ([center - m + 2 * m * k / (n - 1) for k in range(n)] if scale == "div"
                else [lo + (hi - lo) * k / (n - 1) for k in range(n)])
        a, b = fmt(ramp[0]), fmt(ramp[-1])
        x0 = w - R - text_w(b, 10.5) - 8 - n * sw
        fig.add("".join(f'<rect x="{_f(x0 + k * sw)}" y="{_f(y)}" width="{sw - 1}" height="10" rx="2" '
                        f'fill="{fill(v)}"/>' for k, v in enumerate(ramp)))
        fig.text(x0 - 8, y + 9, a, size=10.5, color=MUTED, anchor="end")
        fig.text(x0 + n * sw + 7, y + 9, b, size=10.5, color=MUTED)
    return fig.svg(alt, cap)


def dot_interval(cid, rows, alt, cap, zero=True, xlabel=None, fmt=None, w=760, row_h=38, xlim=None,
                 mid_name="ค่ากลาง", range_name="ช่วง 5–95%", vlines=None):
    """หนึ่งแถวต่อหนึ่งหมวด: จุด (ค่าเฉลี่ย/มัธยฐาน) + เส้นแนวนอนช่วง 5–95% (เทียบกลยุทธ์ข้ามหลายโลก)
      rows = [{"label": ชื่อ (รองรับ \\n), "mid": ค่า, "lo": ค่า, "hi": ค่า, "color": สี (ไม่บังคับ)}]
      zero=True ขีดเส้นประที่ 0 · vlines = [(ค่า, ป้าย[, สี])] เส้นอ้างอิงเพิ่ม · fmt = จัดรูปตัวเลขด้านขวา"""
    fmt = fmt or (lambda v: num(v, 2))
    vals = [[fmt(r["mid"]), f"({fmt(r['lo'])} ถึง {fmt(r['hi'])})"] for r in rows]
    left = min(260, max(80, max(text_w(ln, 12) for r in rows for ln in _lines(r["label"])) + 20))
    gut = max(text_w(a, 12) * 1.08 + text_w(b, 10.5) for a, b in vals) + 26
    row_h = max(row_h, LINE_H * max(len(_lines(r["label"])) for r in rows) + 10)
    noted = any(v[1] for v in (vlines or []))    # ป้ายของ vlines อยู่ในแถวเหนือกรอบ (ไม่ทับแถวข้อมูลแถวแรก)
    T = 34 + (17 if noted else 0)
    B = 46 if xlabel else 28
    fig = Fig(cid, w, T + len(rows) * row_h + B)
    inc = [0.0] if zero else []
    inc += [v[0] for v in (vlines or [])]
    xl = xlim or auto_lim([r["lo"] for r in rows], [r["hi"] for r in rows], include=inc, n=6)
    p = fig.panel(xl, (len(rows), 0.0), x=left, y=T, w=w - left - gut, h=len(rows) * row_h)
    xt = nice_ticks(xl[0], xl[1], 6)
    p.grid(yticks=[], xticks=xt)
    if zero:
        p.vline(0.0, color="#94a3b8")
    for v in vlines or []:
        p.vline(v[0], label=v[1], color=v[2] if len(v) > 2 else "#94a3b8", pos="above")
    out = []
    for i, r in enumerate(rows):
        c = r.get("color", BLUE)
        cy = float(p.Y(i + 0.5))
        xa, xb, xm = float(p.X(r["lo"])), float(p.X(r["hi"])), float(p.X(r["mid"]))
        ls = _lines(r["label"])
        for k, ln in enumerate(ls):
            out.append(text(left - 12, cy + 4 - LINE_H / 2 * (len(ls) - 1) + LINE_H * k, ln, size=12, color=INK,
                            anchor="end"))
        out.append(f'<line x1="{_f(xa)}" y1="{_f(cy)}" x2="{_f(xb)}" y2="{_f(cy)}" stroke="{c}" stroke-width="5" '
                   f'stroke-linecap="round" stroke-opacity=".32"/>'
                   f'<circle cx="{_f(xm)}" cy="{_f(cy)}" r="6" fill="{c}" stroke="#fff" stroke-width="2"/>')
        a, b = vals[i]
        out.append(text(p.right + 14, cy + 4, f'<tspan font-weight="700">{esc(a)}</tspan>'
                        f'<tspan fill="{MUTED}" font-size="10.5">  {esc(b)}</tspan>', size=12, raw=True))
    fig.add("".join(out))
    p.xaxis(ticks=xt, title=xlabel)
    c0 = rows[0].get("color", BLUE) if len({r.get("color", BLUE) for r in rows}) == 1 else MUTED
    fig.legend([(mid_name, c0, "dot"), (range_name, c0, "band")], p.right, 22, anchor="end")
    return fig.svg(alt, cap)


def stacked_bars(cid, bars, parts, alt, cap, colors=None, w=760, bar_h=28, normalize=True, fmt=None,
                 xlabel=None):
    """แท่งซ้อนแนวนอน (ค่าเริ่มต้น = 100% ต่อแท่ง) พร้อม legend — เช่น แยกความแปรปรวนเป็นส่วน ๆ
      bars  = [{"label": ชื่อแท่ง (รองรับ \\n), "values": [ค่าของแต่ละส่วน ตามลำดับ parts]}]
      parts = [ชื่อส่วน, …] · colors = สีของแต่ละส่วน (ไม่ระบุ = SERIES)
      normalize=True → แปลงเป็นสัดส่วน % ของผลรวมแต่ละแท่ง และพิมพ์ % ในช่องที่กว้างพอ"""
    cols = _colors(colors, len(parts))
    left = min(250, max(72, max(text_w(ln, 12) for b in bars for ln in _lines(b["label"])) + 20))
    R = 22
    rows = _flow([(nm, cols[k], "rect") for k, nm in enumerate(parts)], w - left - R)
    T = 14 + 17 * len(rows) + 8
    step = max(bar_h + 16, LINE_H * max(len(_lines(b["label"])) for b in bars) + 10)
    B = 46 if xlabel else 28
    fig = Fig(cid, w, T + len(bars) * step + B)
    for i, row in enumerate(rows):
        fig.add(_legend_row(row, left, 16 + 17 * i))
    data = []
    for b in bars:
        v = np.maximum(np.asarray(b["values"], float), 0.0)
        data.append(100.0 * v / v.sum() if normalize and v.sum() > 0 else v)
    xmax = 100.0 if normalize else auto_lim([float(v.sum()) for v in data], include=[0.0])[1]
    p = fig.panel((0.0, xmax), (len(bars), 0.0), x=left, y=T, w=w - left - R, h=len(bars) * step)
    xt = [0, 25, 50, 75, 100] if normalize else nice_ticks(0.0, xmax, 5)
    p.grid(yticks=[], xticks=xt)
    fmt = fmt or ((lambda v: pct(v, 0)) if normalize else num)
    out = []
    for i, (b, v) in enumerate(zip(bars, data)):
        cy = float(p.Y(i + 0.5))
        ls = _lines(b["label"])
        for k, ln in enumerate(ls):
            out.append(text(left - 12, cy + 4 - LINE_H / 2 * (len(ls) - 1) + LINE_H * k, ln, size=12, color=INK,
                            anchor="end"))
        acc = 0.0
        for k, val in enumerate(v):
            xa, xb = float(p.X(acc)), float(p.X(acc + val))
            acc += val
            if xb - xa < 0.6:
                continue
            out.append(f'<rect x="{_f(xa + 1)}" y="{_f(cy - bar_h / 2)}" width="{_f(max(xb - xa - 2, 0.6))}" '
                       f'height="{bar_h}" rx="4" fill="{cols[k]}"/>')
            s = fmt(val)
            if xb - xa >= text_w(s, 11.5) + 12:
                out.append(text((xa + xb) / 2, cy + 4, s, size=11.5, color=ink_on(cols[k]), anchor="middle",
                                weight=600))
    fig.add("".join(out))
    p.xaxis(ticks=xt, labels=[fmt(t) for t in xt], title=xlabel, line=False)
    return fig.svg(alt, cap)


def grouped_bars(cid, groups, series, alt, cap, ylabel=None, xlabel=None, fmt=None, w=760, h=320,
                 ylim=None, values=True, hlines=None):
    """แท่งแนวตั้งเป็นกลุ่ม: groups = ป้ายของแต่ละกลุ่มบนแกน x (รองรับ \\n)
      series = [{"name": ชื่อชุด, "values": [ค่าต่อกลุ่ม], "color": สี (ไม่บังคับ)}]
      values=True พิมพ์ค่าบนปลายแท่ง (ถ้าแท่งกว้างพอ) · hlines = [(ค่า, ป้าย[, สี])] · ค่าติดลบวาดลงใต้เส้น 0"""
    cols = [s.get("color", SERIES[k % len(SERIES)]) for k, s in enumerate(series)]
    L = 58
    R = max([18.0] + [text_w(hl[1], 10.5) + 18 for hl in (hlines or []) if hl[1]])
    multi = len(series) > 1
    items = [(s["name"], cols[k], "rect") for k, s in enumerate(series)] if multi else []
    rows = _flow(items, w - L - R - 8) if items else []
    T = 14 + 17 * max(_head_rows(w - L - R, text_w(ylabel, 11) if ylabel else 0, rows), 1)
    lab_lines = max(len(_lines(g)) for g in groups)
    B = 30 + LINE_H * (lab_lines - 1) + (22 if xlabel else 0)
    fig = Fig(cid, w, h)
    allv = [v for s in series for v in s["values"] if v is not None]
    yl = ylim or auto_lim(allv, include=[0.0] + [hl[0] for hl in (hlines or [])], pad=0.12)
    p = fig.panel((0.0, float(len(groups))), yl, x=L, y=T, w=w - L - R, h=h - T - B)
    p.grid().yaxis(title=ylabel)
    if items:
        p.legend(items)
    gw = p.w / len(groups)
    bw = min(46.0, (gw * 0.78 - 3 * (len(series) - 1)) / len(series))
    f = fmt or num
    allvals = [[np.nan if v is None else float(v) for v in s["values"]] for s in series]
    # พิมพ์ค่าบนปลายแท่งเฉพาะเมื่อป้ายไม่กว้างกว่าแท่ง (ไม่งั้นป้ายจะทับแท่งข้าง ๆ) — ทุกชุดใช้กติกาเดียวกัน
    widest = max([text_w(f(v), 10.5) for vals in allvals for v in vals if math.isfinite(v)], default=0.0)
    show = bool(values) and widest <= bw + (2 if multi else 0.6 * (gw - bw))
    for k, vals in enumerate(allvals):
        off = (k - (len(series) - 1) / 2) * (bw + 3) / gw
        xs = [g + 0.5 + off for g in range(len(groups))]
        p.bars(xs, vals, cols[k], width=bw, fmt=f, labels=True if show else None)
    if yl[0] < 0 < yl[1]:
        p.hline(0.0, color="#94a3b8", dash=None)
    for hl in hlines or []:
        p.hline(hl[0], color=hl[2] if len(hl) > 2 else "#94a3b8")
    p.gutter_labels([(hl[0], hl[1]) for hl in (hlines or [])])
    p.xaxis(ticks=[g + 0.5 for g in range(len(groups))], labels=list(groups), title=xlabel,
            line=not (yl[0] < 0 < yl[1]))
    return fig.svg(alt, cap)


def line_chart(cid, x, series, alt, cap, xlabel=None, ylabel=None, w=760, h=320, xlim=None, ylim=None,
               categories=False, xticks=None, xlabels=None, xfmt=None, yfmt=None, markers=None,
               hlines=None, vlines=None, bands=None, xbands=None, callouts=None, zero=None, title=None,
               area=False):
    """กราฟเส้นหลายเส้นพร้อม legend (แกน y เดียวเสมอ)
      x      = ค่าบนแกน x ที่ใช้ร่วมกัน (None = 0, 1, 2, …)
      series = [{"name": ชื่อ, "y": อนุกรม, "color": สี, "dash": "6 4", "hero": bool, "x": แกน x ของเส้นนี้เอง}]
               ไม่ระบุ color/dash = ไล่ตาม SERIES/DASHES (เส้นที่ 4–5 เป็นเส้นประ)
      categories=True = วางจุดห่างเท่ากันตามลำดับ แล้วใช้ค่า x เป็นป้าย (เช่น เกณฑ์ 0.5, 1, 2, 4, 8)
      markers = True/False วาดจุดบนข้อมูล (ไม่ระบุ = วาดเมื่อจุดไม่เกิน 25)
      hlines / vlines = [(ค่า, ป้าย[, สี])] · bands = [(lo, hi, ป้าย[, สี])] แถบแนวนอน
      xbands = [(lo, hi, ป้าย[, สี])] แถบแนวตั้ง · callouts = [(x, y, ป้าย[, dx, dy[, สี]])]
      zero=True บังคับให้แกน y รวม 0 และขีดเส้น 0 · area=True ระบายใต้เส้นแรก"""
    ys = [np.asarray(s["y"], float) for s in series]
    npts = max(len(v) for v in ys)
    cat_labels = None
    if categories:
        cat_labels = [num(v) if isinstance(v, (int, float, np.integer, np.floating)) else str(v)
                      for v in (x if x is not None else range(npts))]
        base_x = np.arange(npts, dtype=float)
    else:
        base_x = np.arange(npts, dtype=float) if x is None else np.asarray(x, float)
    xss = [np.asarray(s["x"], float) if "x" in s and not categories else base_x[:len(v)]
           for s, v in zip(series, ys)]
    inc = ([0.0] if zero else []) + [hl[0] for hl in (hlines or [])]
    yl = ylim or auto_lim(*ys, include=inc)
    if xlim is None:
        lo, hi = min(float(np.nanmin(v)) for v in xss), max(float(np.nanmax(v)) for v in xss)
        xlim = (lo - 0.35, hi + 0.35) if categories else (lo, hi)
    L = 58
    gutter = [h[1] for h in (hlines or [])] + [b[2] for b in (bands or [])]      # ป้ายที่วางในร่องขวา
    R = max([20.0] + [text_w(t, 10.5) + 18 for t in gutter if t])
    cols = [s.get("color", SERIES[k % len(SERIES)]) for k, s in enumerate(series)]
    dashes = [s.get("dash", DASHES[k % len(DASHES)] if "color" not in s else None) for k, s in enumerate(series)]
    items = [(s.get("name", ""), cols[k], "line", dashes[k]) for k, s in enumerate(series)]
    rows = _flow(items, w - L - R - 8) if len(series) > 1 else []
    T = 14 + 17 * max(_head_rows(w - L - R, text_w(ylabel, 11) if ylabel else 0, rows), 1) + (22 if title else 0)
    T += 17 if any([b[2] for b in (xbands or [])] + [v[1] for v in (vlines or [])]) else 0   # แถวป้ายเหนือกรอบ
    tick_labs = list(xlabels) if xlabels else (cat_labels or [])
    B = 26 + (22 if xlabel else 0) + LINE_H * (max([len(_lines(s)) for s in tick_labs], default=1) - 1)
    fig = Fig(cid, w, h)
    if title:
        fig.title(title, x=L)
    p = fig.panel(xlim, yl, x=L, y=T, w=w - L - R, h=h - T - B)
    for bd in xbands or []:
        p.xband(bd[0], bd[1], label=bd[2], color=bd[3] if len(bd) > 3 else MUTED)
    for bd in bands or []:
        p.band(bd[0], bd[1], color=bd[3] if len(bd) > 3 else BLUE)
    for vl in vlines or []:                      # จองแถวป้ายเหนือกรอบก่อนหัวข้อ/legend
        if vl[1]:
            p._note_row()
    p.grid().yaxis(title=ylabel, fmt=yfmt)
    if rows:
        p.legend(items)
    if zero or (zero is None and yl[0] < 0 < yl[1]):
        p.hline(0.0, color="#94a3b8")
    for hl in hlines or []:
        p.hline(hl[0], color=hl[2] if len(hl) > 2 else "#94a3b8")
    mid = lambda bd: ((yl[0] if bd[0] is None else max(bd[0], yl[0])) + (yl[1] if bd[1] is None else min(bd[1], yl[1]))) / 2
    p.gutter_labels([(hl[0], hl[1]) for hl in (hlines or [])] + [(mid(bd), bd[2]) for bd in (bands or [])])
    for vl in vlines or []:
        p.vline(vl[0], label=vl[1], color=vl[2] if len(vl) > 2 else "#94a3b8", pos="above")
    if area:
        p.area(xss[0], ys[0], cols[0])
    for k, s in enumerate(series):
        p.line(xss[k], ys[k], cols[k], hero=s.get("hero", False), dash=dashes[k], width=s.get("width", 2.0))
    if markers or (markers is None and npts <= 25):
        for k in range(len(series)):
            p.scatter(xss[k], ys[k], cols[k], r=4, ring=True)
    for c in callouts or []:
        p.callout(c[0], c[1], c[2], dx=c[3] if len(c) > 3 else 44, dy=c[4] if len(c) > 4 else -30,
                  color=c[5] if len(c) > 5 else PURPLE)
    if categories:
        p.xaxis(ticks=list(base_x), labels=cat_labels if xlabels is None else xlabels, title=xlabel)
    else:
        p.xaxis(ticks=xticks, labels=xlabels, fmt=xfmt, title=xlabel)
    return fig.svg(alt, cap)


def hist_chart(cid, values, alt, cap, bins=40, xlabel=None, ylabel=None, color=BLUE, vlines=None,
               shade=None, xlim=None, w=760, h=300, title=None):
    """ฮิสโทแกรมแนวตั้งของ values พร้อมเส้นแนวตั้งกำกับ (เช่น การแจกแจงของค่า ADF ใต้สมมติฐานว่าง)
      vlines = [(ค่า, ป้าย[, สี])] — ป้ายเรียงเหนือกรอบ ไม่ทับแท่งและไม่ทับกันเอง
      shade  = (lo, hi, สี) ระบายแท่งที่อยู่ในช่วงนี้ด้วยอีกสีหนึ่ง (None = สุดขอบ) เช่น หางซ้ายที่ "ผ่านเกณฑ์"
      xlim   = ตัดช่วงแกน x (ค่านอกช่วงไม่ถูกนับ)"""
    v = np.asarray(values, float)
    v = v[np.isfinite(v)]
    rng_ = xlim or (float(v.min()), float(v.max()))
    if rng_[1] <= rng_[0]:                       # ค่าทุกตัวเท่ากัน → กันหารด้วยศูนย์
        rng_ = (rng_[0] - 0.5, rng_[0] + 0.5)
    cnt, edges = np.histogram(v, bins=bins, range=rng_)
    marks = sorted(vlines or [], key=lambda m: m[0])
    L, R = 58, 20
    fig = Fig(cid, w, h)
    # จัดป้ายของเส้นแนวตั้งเป็นแถว ๆ เหนือกรอบ
    px = lambda val: L + (val - rng_[0]) / (rng_[1] - rng_[0]) * (w - L - R)
    slots, row_end = [], []
    for m in marks:
        tw = text_w(m[1], 11) + 10
        a = min(max(px(m[0]) - tw / 2, L), w - R - tw)
        r = next((i for i, e in enumerate(row_end) if a >= e), len(row_end))
        if r == len(row_end):
            row_end.append(0.0)
        row_end[r] = a + tw
        slots.append((r, a + tw / 2))
    T = 18 + 16 * max(len(row_end), 1) + (20 if title else 0) + (16 if ylabel else 0)
    B = 26 + (22 if xlabel else 0)
    if title:
        fig.title(title, x=L)
    p = fig.panel(rng_, (0.0, float(cnt.max()) * 1.08), x=L, y=T, w=w - L - R, h=h - T - B)
    p.grid(n=4).yaxis(fmt=lambda t: num(t, 0))
    if ylabel:
        fig.text(L, T - 12 - 16 * max(len(row_end), 1), ylabel, size=11, color=MUTED)
    mids = (edges[:-1] + edges[1:]) / 2
    cols = None
    if shade:
        a = -math.inf if shade[0] is None else shade[0]
        b = math.inf if shade[1] is None else shade[1]
        cols = [shade[2] if a <= m <= b else color for m in mids]
    p.hist(edges, cnt, color, colors=cols, opacity=0.85)
    for m, (r, cx) in zip(marks, slots):
        d = f"M{_f(p.X(m[0]))} {_f(p.bottom)}V{_f(T - 4 - 16 * r)}"
        fig.add(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="4" stroke-opacity=".85"/>'
                f'<path d="{d}" fill="none" stroke="{m[2] if len(m) > 2 else INK}" stroke-width="1.6" '
                f'stroke-dasharray="5 3"/>')
    for m, (r, cx) in zip(marks, slots):         # ป้ายวาดทีหลัง มีขอบขาว จึงไม่ถูกเส้นของป้ายแถวบนขีดทับ
        fig.add(text(cx, T - 10 - 16 * r, m[1], size=11, color=INK, anchor="middle", weight=600, halo=True))
    p.xaxis(title=xlabel)
    return fig.svg(alt, cap)


def scatter_chart(cid, x, y, alt, cap, xlabel=None, ylabel=None, lines=None, max_points=300, color=BLUE,
                  w=760, h=360, xlim=None, ylim=None, callouts=None):
    """จุดกระจาย y เทียบ x (สุ่มหยิบไม่เกิน max_points จุด แบบเว้นช่วงเท่ากัน) + เส้นตรงที่ fit ไว้
      lines = [{"a": จุดตัดแกน, "b": ความชัน, "name": ชื่อ, "color": สี, "dash": "6 4"}]  (y = a + b·x)"""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    idx = np.unique(np.linspace(0, len(x) - 1, min(max_points, len(x))).astype(int))
    xl = xlim or auto_lim(x, pad=0.04)
    yl = ylim or auto_lim(y, pad=0.06)
    lines = lines or []
    L, R = 62, 20
    items = [(f"ข้อมูล ({len(idx):,} จุดจาก {len(x):,})", color, "dot")] + [
        (ln.get("name", "เส้น fit"), ln.get("color", SERIES[(k + 1) % len(SERIES)]), "line", ln.get("dash"))
        for k, ln in enumerate(lines)]
    rows = _flow(items, w - L - R - 8)
    T = 14 + 17 * _head_rows(w - L - R, text_w(ylabel, 11) if ylabel else 0, rows)
    B = 26 + (22 if xlabel else 0)
    fig = Fig(cid, w, h)
    p = fig.panel(xl, yl, x=L, y=T, w=w - L - R, h=h - T - B)
    p.grid(xticks=nice_ticks(xl[0], xl[1], 6)).yaxis(title=ylabel)
    p.legend(items)
    p.scatter(x[idx], y[idx], color)
    for k, ln in enumerate(lines):
        xe = np.array(xl)
        p.line(xe, ln["a"] + ln["b"] * xe, ln.get("color", SERIES[(k + 1) % len(SERIES)]), dash=ln.get("dash"),
               hero=k == 0)
    for c in callouts or []:
        p.callout(c[0], c[1], c[2], dx=c[3] if len(c) > 3 else 44, dy=c[4] if len(c) > 4 else -30,
                  color=c[5] if len(c) > 5 else PURPLE)
    p.xaxis(title=xlabel)
    return fig.svg(alt, cap)


# ───────────────────────── แกลเลอรีตัวอย่าง ─────────────────────────

def _gallery():
    """สร้างกราฟตัวอย่างของทุกตัวสร้าง จากข้อมูลจำลองใน sas_core → [(ชื่อ, html)]"""
    import sas_core as C

    out = []
    g = C.rng(9901)

    # 1) stacked_panels — แบบสไลด์แผ่นที่ 2
    t = np.arange(200)
    wave = 0.6 * np.sin(t / 32.0) + 0.3 * np.sin(t / 11.0)
    a, b = wave + 0.18 * g.standard_normal(200), wave + 0.18 * g.standard_normal(200)
    out.append(("stacked_panels", stacked_panels(
        "gal-stacked", [
            {"y": a, "title": "Asset A = Market + Size + Growth + Risk(A)", "color": BLUE},
            {"y": b, "title": "Asset B = Market + Size + Growth + Risk(B)", "color": AMBER},
            {"y": a - b, "title": "Spread = Risk(A) − Risk(B)", "color": GREEN, "zero": True},
        ],
        "สามกรอบเรียงกัน: สินทรัพย์ A และ B แกว่งตามคลื่นร่วม ส่วนสเปรดเป็นสัญญาณรบกวนรอบศูนย์",
        "ข้อมูลจำลอง 200 แท่ง · สองกรอบบนมีคลื่นร่วมเดียวกัน กรอบล่างคือส่วนต่างที่คลื่นร่วมหักล้างกันหมด",
        xlabel="แท่งที่ (t)")))
    out.append(("stacked_panels (share_y + สองเส้น + แถบแนวตั้ง)", stacked_panels(
        "gal-stacked2", [
            {"y": [a, b], "title": "ราคา (log)", "names": ["A", "B"]},
            {"y": a - b, "title": "สเปรด A − B", "color": GREEN, "hlines": [(0.4, "+2σ"), (-0.4, "−2σ")]},
        ], "สองกรอบที่ใช้สเกลเดียวกัน", "share_y=True ทำให้เห็นว่าสเปรดแกว่งแคบกว่าราคามาก",
        share_y=True, xbands=[(0, 100, "ช่วง train"), (100, 199, "ช่วง test", AMBER)], panel_h=120)))

    # 2) series_with_hist — แบบสไลด์แผ่นที่ 3
    rw = C.random_walk(200, 1.0, C.rng(9902))
    st = C.rng(9903).standard_normal(200)
    out.append(("series_with_hist (สองแถว = 2×2)", series_with_hist(
        "gal-hist2x2", [
            {"y": rw, "title": "Non-Stationary Time Series", "hist_title": "ฮิสโทแกรม", "color": RED, "mean": True},
            {"y": st, "title": "Stationary Time Series", "hist_title": "ฮิสโทแกรม", "color": BLUE, "mean": True},
        ],
        "สองแถว: random walk กับฮิสโทแกรมที่เบี้ยว และอนุกรมนิ่งกับฮิสโทแกรมทรงระฆัง",
        "ข้อมูลจำลอง 200 แท่ง · แถวบนไม่นิ่ง ฮิสโทแกรมจึงไม่มีความหมาย แถวล่างนิ่ง ฮิสโทแกรมจึงใช้ได้",
        xlabel="แท่งที่ (t)", hist_xlabel="ค่าของอนุกรม")))

    # 3) zone_chart — แบบสไลด์แผ่นที่ 6 และ 7
    qs = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
    for kind, name in (("good", "ดี"), ("fake", "พัง")):
        d = C.demo_pair(kind)
        e = C.ols(d["y"], d["x"])["resid"] * 100
        pc = {q: float(np.percentile(e, q)) for q in qs}
        out.append((f"zone_chart ({kind})", zone_chart(
            f"gal-zone-{kind}", e, pc,
            f"ฮิสโทแกรมและอนุกรมเวลาของ ε พร้อมเส้นเปอร์เซ็นไทล์ 11 เส้น กรณี{name}",
            f"ข้อมูลจำลอง คู่ <code>{kind}</code> 1,500 แท่ง · ε หน่วยเป็น % · เส้นประคือเปอร์เซ็นไทล์ของ ε ทั้งช่วง",
            mark_last=True)))

    # 4) heat_table — ตาราง power (seq) และตารางต้นทุน (div)
    hls, ns = [5, 10, 20, 40, 80], [125, 250, 500, 1000]
    power = []
    for hl in hls:
        row = []
        for n in ns:
            crit = C.crit_values(C.mc_null_adf(n, 1500, g=C.rng(9910)))[0.05]
            stat = C.adf_stat_batch(C.ar1_batch(300, n, hl, 1.0, C.rng(9911 + n + hl)))
            row.append(100.0 * float(np.mean(stat < crit)))
        power.append(row)
    out.append(("heat_table (seq)", heat_table(
        "gal-heat-seq", [f"half-life {h} แท่ง" for h in hls], [f"{n:,} แท่ง" for n in ns], power,
        "ตารางอัตราที่ ADF จับการดึงกลับได้ ตาม half-life และจำนวนแท่ง",
        "ข้อมูลจำลอง 300 โลกต่อช่อง · ตัวเลข = % ของโลกที่ ADF ปฏิเสธ random walk ที่ระดับ 5%",
        fmt="{:.0f}%", row_title="ความจริง", col_title="ความยาวข้อมูล", lo=0, hi=100)))
    sig, cs = [0.5, 1, 2, 4], [0, 2, 5, 10, 20, 50]
    net = [[round(8.0 * (2 * s - 2 * c / 100 * 2.4), 1) for c in cs] for s in sig]
    out.append(("heat_table (div)", heat_table(
        "gal-heat-div", [f"σ = {s}%" for s in sig], [f"{c} bps" for c in cs], net,
        "ตารางผลตอบแทนสุทธิต่อปีตามขนาดสเปรดและต้นทุน",
        "ตัวเลขสมมติเพื่อทดสอบการระบายสี · แดง = ติดลบ น้ำเงิน = เป็นบวก",
        scale="div", fmt="{:+.1f}%", row_title="ขนาดของ ε", col_title="ต้นทุนเที่ยวเดียวต่อขา (c)")))

    # 5) dot_interval — Sharpe ข้ามหลายโลก
    rows = []
    for kind, name in (("good", "มีสายจูงจริง"), ("drift", "สายจูงยืด (β เลื่อน)"),
                       ("break", "สายจูงขาดกลางทาง"), ("fake", "ไม่มีสายจูง\n(แค่ correlation สูง)")):
        sh = [C.walk_forward_pair(*(lambda d: (d["y"], d["x"]))(C.make_pair(kind, 1000, C.rng(9920 + i))),
                                  cost_per_leg=0.0005)["stats"]["sharpe"] for i in range(24)]
        rows.append({"label": name, "mid": float(np.mean(sh)), "lo": float(np.percentile(sh, 5)),
                     "hi": float(np.percentile(sh, 95)), "color": GREEN if kind == "good" else RED})
    out.append(("dot_interval", dot_interval(
        "gal-dots", rows, "ค่า Sharpe เฉลี่ยและช่วง 5–95% ของสี่ชนิดคู่",
        "ข้อมูลจำลอง 24 โลกต่อแถว · walk-forward · c = 5 bps",
        xlabel="Sharpe ต่อปี (หลังหักต้นทุน)", mid_name="ค่าเฉลี่ย")))

    # 6) stacked_bars — แยกความแปรปรวน
    out.append(("stacked_bars", stacked_bars(
        "gal-stack", [
            {"label": "A − B", "values": [38, 21, 30, 11]},
            {"label": "A − β·B (β จาก OLS)", "values": [3, 34, 41, 22]},
            {"label": "A − ตะกร้า B, C, D", "values": [0.4, 0.8, 0.6, 98.2]},
        ], ["Market", "Size", "Growth", "เฉพาะตัว (idio)"],
        "แท่งซ้อนสามแท่งแสดงสัดส่วนความแปรปรวนของผลตอบแทนสเปรดที่มาจากแต่ละปัจจัย",
        "ตัวเลขสมมติ · ยิ่งส่วน “เฉพาะตัว” ใหญ่ สเปรดยิ่งสะอาดจากปัจจัยร่วม",
        colors=[BLUE, AMBER, RED, "#94a3b8"])))

    # 7) grouped_bars
    out.append(("grouped_bars", grouped_bars(
        "gal-group", ["lag 0\n(บั๊ก)", "lag 1\n(ถูก)", "lag 2\n(ช้าหนึ่งแท่ง)"], [
            {"name": "ไม่คิดต้นทุน", "values": [-0.42, 1.31, 0.97]},
            {"name": "c = 5 bps", "values": [-0.81, 0.92, 0.55]},
        ], "แท่งเทียบ Sharpe ตาม lag ของการส่งคำสั่ง สองระดับต้นทุน",
        "ตัวเลขสมมติ · แสดงแท่งติดลบและป้ายสองบรรทัด", ylabel="Sharpe ต่อปี")))

    # 8) line_chart — เส้นยาว 1,500 จุด สี่เส้น และเส้นสั้นมีจุด
    curves = []
    for kind in ("good", "drift", "break", "fake"):
        d = C.demo_pair(kind)
        r = C.walk_forward_pair(d["y"], d["x"], cost_per_leg=0.0005)
        curves.append({"name": kind, "y": 100 * np.cumsum(r["pnl"])})
    out.append(("line_chart (ยาว)", line_chart(
        "gal-equity", None, curves, "เส้นผลตอบแทนสะสมของคู่ตัวอย่างสี่แบบ",
        "ข้อมูลจำลอง · walk-forward train 250 แท่ง · c = 5 bps · สี่เส้น เส้นละ 1,500 จุด (ถูกย่อเหลือไม่กี่ร้อยจุด)",
        xlabel="แท่งที่ (วัน)", ylabel="ผลตอบแทนสะสม (% ของเงินรวมสองขา)",
        xbands=[(0, 250, "ช่วง train แรก")])))
    ent = [0.5, 1, 1.5, 2, 2.5, 3]
    out.append(("line_chart (categories + จุด)", line_chart(
        "gal-threshold", ent, [
            {"name": "c = 0", "y": [2.1, 1.9, 1.6, 1.3, 0.9, 0.5]},
            {"name": "c = 5 bps", "y": [0.2, 1.1, 1.3, 1.15, 0.8, 0.45]},
            {"name": "c = 20 bps", "y": [-3.9, -0.8, 0.4, 0.7, 0.6, 0.35]},
        ], "Sharpe ตามเกณฑ์เข้า สามระดับต้นทุน", "ตัวเลขสมมติ · ต้นทุนสูงขึ้น จุดที่ดีที่สุดเลื่อนออกไปทางขวา",
        xlabel="เกณฑ์เข้า (|z|)", ylabel="Sharpe ต่อปี", categories=True, zero=True)))

    # 9) hist_chart — การแจกแจงของ ADF ใต้สมมติฐานว่าง
    null = C.mc_null_adf(500, 6000, g=C.rng(9930))
    c5 = float(np.quantile(null, 0.05))
    out.append(("hist_chart", hist_chart(
        "gal-adf", null, "ฮิสโทแกรมของค่า ADF เมื่อความจริงคือ random walk พร้อมเส้นเกณฑ์สองเส้น",
        "ข้อมูลจำลอง 6,000 เส้น ยาว 500 แท่ง · แท่งสีแดง = 5% ซ้ายสุด",
        xlabel="ค่า t ของ ADF", ylabel="จำนวนเส้น", shade=(None, c5, RED),
        vlines=[(c5, f"เกณฑ์จริง 5% = {num(c5, 2)}", RED), (-1.645, "ตาราง normal −1.645", MUTED)])))

    # 10) scatter_chart
    d = C.demo_pair("good")
    r = C.ols(d["y"], d["x"])
    out.append(("scatter_chart", scatter_chart(
        "gal-scatter", d["x"], d["y"], "จุดกระจายของ log ราคา Y เทียบ X พร้อมเส้น OLS",
        "ข้อมูลจำลอง คู่ <code>good</code> · หยิบ 300 จุดจาก 1,500 แท่ง", xlabel="X (log ราคา)", ylabel="Y (log ราคา)",
        lines=[{"a": float(r["coef"][0]), "b": float(r["coef"][1]), "name": f"OLS: β = {num(r['coef'][1], 3)}",
                "color": RED}])))

    # 11) Fig + Panel แบบประกอบเอง — ใช้ทุกเมธอด
    fig = Fig("gal-free", 760, 330)
    e = d["eps"][:400] * 100
    x = np.arange(400)
    p = fig.panel((0, 399), auto_lim(e, include=[-9, 9]), top=68, bottom=48, right=46)
    p.xband(300, 399, AMBER, label="ช่วงที่ยังไม่เห็น").xband(0, 300, MUTED, 0.0, label="ช่วงที่เห็นแล้ว")
    p.band(6, None, RED, 0.07, "โซน short สเปรด").band(None, -6, GREEN, 0.07)
    p.grid().yaxis(title="ε (%)").xaxis(title="แท่งที่ (วัน)")
    p.area(x, e, BLUE, color_below=RED).line(x, e, BLUE, hero=True)
    p.hline(0, label="μ", pos="out").hline(6, color=RED, label="+2σ", pos="out")
    p.hline(-6, color=GREEN, label="−2σ", pos="out").vline(300, label="วันนี้", pos="bottom")
    k = int(np.argmin(e[:300]))
    p.callout(k, e[k], "ห่างสุดในช่วงนี้", dx=40, dy=24)
    p.scatter([k + 40, k + 55], [e[k + 40], e[k + 55]], PURPLE, r=4, ring=True)
    p.title("ε ของคู่ตัวอย่าง", "400 แท่งแรก").legend([("ε", BLUE), ("เส้นอ้างอิง", AXIS, "line", "4 4"),
                                                      ("โซนเข้า", RED, "band")])
    out.append(("Fig + Panel (ประกอบเอง)", fig.svg("ตัวอย่างการประกอบกราฟเองด้วย Panel",
                                                  "ทดสอบ area · hero line · hline/vline · band/xband · callout · legend")))

    fig = Fig("gal-free2", 760, 300)
    p = fig.panel((0, 6), (-2, 5), x=58, y=40, w=300, h=200)
    p.grid().yaxis().bars([0.5, 1.5, 2.5, 3.5, 4.5, 5.5], [3.2, 4.1, -1.2, 2.2, 0.6, 1.9], labels=True,
                          colors=[BLUE, BLUE, RED, BLUE, BLUE, BLUE], fmt=lambda v: num(v, 1))
    p.hline(0, color="#94a3b8", dash=None).xaxis(ticks=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
                                               labels=list("ABCDEF"), line=False).title("bars()")
    q = fig.panel((0, 60), (4, 0), x=470, y=40, w=230, h=200)
    q.grid(yticks=[], xticks=[0, 20, 40, 60]).hbars([0.5, 1.5, 2.5, 3.5], [52, 31, 18, 7], AMBER, labels=True,
                                                   fmt=lambda v: pct(v, 0))
    for i, s in enumerate(["ไม่มีสายจูง", "ต้นทุนกินหมด", "มองอนาคต", "อื่น ๆ"]):
        q.text(0, i + 0.5, s, dx=-8, dy=4, anchor="end", size=11.5)
    q.xaxis(ticks=[0, 20, 40, 60], fmt=lambda v: pct(v, 0)).title("hbars()").legend([("สัดส่วน", AMBER, "rect")], "br")
    out.append(("Panel.bars / hbars / legend ในกรอบ", fig.svg("ตัวอย่างแท่งแนวตั้งและแนวนอน", "สองกรอบในรูปเดียว")))
    return out


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    if len(argv) > 1:
        dest = argv[1]
    else:
        import tempfile
        dest = os.path.join(tempfile.gettempdir(), "sas-svg-gallery.html")
    with open(os.path.join(os.path.dirname(here), "docs", "statarb-data-quality.html"), encoding="utf-8") as fh:
        shell = fh.read()
    head = shell[:shell.index("<body>") + len("<body>")]
    head = re.sub(r"<title>.*?</title>", "<title>sas_svg — แกลเลอรีตัวสร้างกราฟ</title>", head, count=1)
    try:                                         # CSS ของชุด (div.figw ฯลฯ) — ให้แกลเลอรีหน้าตาเหมือนหน้าจริง
        import sas_new_part
        head = head.replace("</head>", sas_new_part.SERIES_CSS + "\n</head>", 1)
    except ImportError:
        pass
    script = shell[shell.rindex("<!-- ═══════════════ Thai line-break script"):]
    body = ['<div class="cover"><h1>sas_svg — แกลเลอรี</h1><div class="sub">ตัวสร้างกราฟทุกตัว บนข้อมูลจำลองจาก '
            'sas_core</div></div>']
    ids = []
    for name, html in _gallery():
        ids += re.findall(r'\bid="([^"]+)"', html)
        body.append(f'<h3>{esc(name)} <span class="cc">· {len(html.encode("utf-8")) / 1024:.1f} KB</span></h3>\n{html}')
        print(f"  {name:<48s} {len(html.encode('utf-8')) / 1024:6.1f} KB")
    dup = sorted({i for i in ids if ids.count(i) > 1})
    assert not dup, f"id ซ้ำข้ามกราฟ: {dup}"
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(head + "\n" + "\n\n".join(body) + "\n" + script)
    print(f"เขียนแกลเลอรี → {dest}  ({len(ids)} id ใน <defs> ไม่ซ้ำกันเลย)")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main(sys.argv)
