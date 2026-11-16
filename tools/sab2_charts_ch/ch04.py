"""เล่ม 2 บท 4 — กลับเร็วแค่ไหน และมั่นใจได้แค่ไหน · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch04 เท่านั้น)

sab2-ci-ladder   : 🎲 โลกเดียว φ 0.95 · 20 / 60 / 250 วันแรก · จุด = φ ที่ประมาณได้ · เส้น = ช่วง 95% · เส้นประ = φ จริง · เส้นทึบ = 1
sab2-bias-thirty : 🎲 30 โลก φ 0.95 · จุด φ ที่ประมาณได้ของทุกโลกที่ 20 / 60 / 250 วัน · เส้นประ = φ จริง · ขีดม่วง = Median
sab2-hl-real     : 📡 ช่วง 95% ของ Half-life (วัน) ของ LTC เดี่ยว · LTC–DOT · BTC–ETH ช่วงเลือก และช่วงตรวจแบบตรึง h · เส้นเกณฑ์ 30 วัน
"""

from sab_charts import B, C, chart, text, wrap

INK, MUTED, GREY, AXIS = C["ink"], C["muted"], C["grey"], C["axis"]


def _axis(out, lo, hi, step, y0, L, R, W, fmt=None, top=None):
    X = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)  # noqa: E731
    out.append(f'<line x1="{L}" y1="{y0}" x2="{W - R}" y2="{y0}" stroke="{AXIS}"/>')
    t = lo
    while t <= hi + 1e-9:
        out.append(f'<line x1="{X(t):.1f}" y1="{y0}" x2="{X(t):.1f}" y2="{y0 + 4}" stroke="{AXIS}"/>')
        if top is not None:
            out.append(f'<line x1="{X(t):.1f}" y1="{top}" x2="{X(t):.1f}" y2="{y0}" stroke="{C["grid"]}"/>')
        out.append(text(X(t), y0 + 17, fmt(t) if fmt else B.fmt(round(t, 2)), 10.5, GREY, "middle"))
        t += step
    return X


@chart("sab2-ci-ladder")
def _ci_ladder(fig):
    c = fig["ch04"]["บันได"]
    true = fig["ch04"]["มือ"]["phiจริง"]
    W, H, L, R = 760, 300, 120, 200
    lo, hi = 0.5, 1.1
    out = [text(16, 24, "φ ที่ประมาณได้ และช่วง 95% จากโลกเดียวกัน", 12.5, INK, weight=700)]
    X = _axis(out, lo, hi, 0.1, 250, L, R, W, top=46)
    out.append(f'<line x1="{X(true):.1f}" y1="46" x2="{X(true):.1f}" y2="250" stroke="{C["green"]}" stroke-dasharray="5 4" stroke-width="1.6"/>')
    out.append(text(X(true), 42, f"φ จริง {B.fmt(true)}", 10.5, C["green"], "middle", 700))
    out.append(f'<line x1="{X(1):.1f}" y1="46" x2="{X(1):.1f}" y2="250" stroke="{C["red"]}" stroke-width="1.4"/>')
    out.append(text(X(1) + 4, 60, "1 = ไม่มีเชือก", 10.5, C["red"], "start", 700))
    for i, d in enumerate(c["วัน"]):
        y = 95 + 60 * i
        a, b, p = c["ล่าง"][i], c["บน"][i], c["phi"][i]
        out.append(text(L - 12, y + 4, f"{d} วันแรก", 12, INK, "end", 700))
        out.append(f'<line x1="{X(a):.1f}" y1="{y}" x2="{X(min(b, hi)):.1f}" y2="{y}" stroke="{C["blue"]}" stroke-width="3"/>')
        for v in (a, b):
            out.append(f'<line x1="{X(v):.1f}" y1="{y - 8}" x2="{X(v):.1f}" y2="{y + 8}" stroke="{C["blue"]}" stroke-width="2"/>')
        out.append(f'<circle cx="{X(p):.1f}" cy="{y}" r="5.5" fill="{C["purple"]}"/>')
        hl_hi = "∞" if c["ครึ่งชีวิตบน"][i] is None else B.fmt(c["ครึ่งชีวิตบน"][i])
        out.append(text(W - R + 14, y - 3, f"φ {B.fmt(p)} [{B.fmt(a)}, {B.fmt(b)}]", 11, INK))
        out.append(text(W - R + 14, y + 13, f"Half-life {B.fmt(c['ครึ่งชีวิต'][i])} [{B.fmt(c['ครึ่งชีวิตล่าง'][i])}, {hl_hi}] วัน", 11, MUTED))
    alt = ("ช่วง 95% ของ φ สามแถว 20 วัน " + f"{B.fmt(c['ล่าง'][0])} ถึง {B.fmt(c['บน'][0])} · 60 วัน {B.fmt(c['ล่าง'][1])} ถึง {B.fmt(c['บน'][1])} · "
           f"250 วัน {B.fmt(c['ล่าง'][2])} ถึง {B.fmt(c['บน'][2])} · ช่วงแคบลงเมื่อข้อมูลยาวขึ้น และสองแถวแรกข้ามเส้น 1")
    cap = "โลกเชือก φ 0.95 หนึ่งโลก (seed 1032) · 20 / 60 / 250 วันแรกของโลกเดียวกัน · ช่วง = φ ± 1.96 × SE"
    return wrap(W, H, alt, out, cap, "จำลอง")


def _stack(values, width):
    seen, out = {}, []
    for v in values:
        b = round(v / width)
        k = seen.get(b, 0)
        seen[b] = k + 1
        out.append((b * width, k))
    return out


@chart("sab2-bias-thirty")
def _bias_thirty(fig):
    c = fig["ch04"]["สามสิบโลก"]
    true = fig["ch04"]["มือ"]["phiจริง"]
    W, H, L, R = 760, 440, 96, 24
    lo, hi = 0.3, 1.05
    out = [text(16, 24, "φ ที่ประมาณได้ของ 30 โลก (ทุกโลกมี φ จริง 0.95)", 12.5, INK, weight=700)]
    X = _axis(out, lo, hi, 0.1, 400, L, R, W, top=44)
    out.append(f'<line x1="{X(true):.1f}" y1="44" x2="{X(true):.1f}" y2="400" stroke="{C["green"]}" stroke-dasharray="5 4" stroke-width="1.6"/>')
    out.append(text(X(true) - 4, 40, f"φ จริง {B.fmt(true)}", 10.5, C["green"], "end", 700))
    for i, d in enumerate(c["วัน"]):
        y0 = 140 + 120 * i
        vals = c["phiทุกโลก"][i]
        out.append(text(L - 10, y0 - 4, f"{d} วัน", 12, INK, "end", 700))
        out.append(f'<line x1="{L}" y1="{y0}" x2="{W - R}" y2="{y0}" stroke="{AXIS}" stroke-dasharray="2 3"/>')
        for (bv, k), v in zip(_stack(vals, 0.02), vals):
            col = C["amber"] if v < true else C["blue"]
            out.append(f'<circle cx="{X(bv):.1f}" cy="{y0 - 6 - 7 * k:.1f}" r="3.4" fill="{col}" fill-opacity=".85"/>')
        m = c["มัธยฐานphi"][i]
        out.append(f'<line x1="{X(m):.1f}" y1="{y0 - 80}" x2="{X(m):.1f}" y2="{y0 + 4}" stroke="{C["purple"]}" stroke-width="2.4"/>')
        out.append(text(X(m) - 5, y0 + 16, f"Median {B.fmt(m)} · ต่ำกว่าจริง {c['ต่ำกว่าจริง'][i]} โลก", 10.5, C["purple"], "end", 700))
    alt = (f"จุด 30 จุดต่อแถว สามแถว 20 60 และ 250 วัน Median ของ φ ที่ประมาณได้คือ {B.fmt(c['มัธยฐานphi'][0])} "
           f"{B.fmt(c['มัธยฐานphi'][1])} และ {B.fmt(c['มัธยฐานphi'][2])} ต่ำกว่า φ จริง 0.95 ทุกแถว "
           f"จำนวนโลกที่ต่ำกว่าจริง {c['ต่ำกว่าจริง'][0]} {c['ต่ำกว่าจริง'][1]} และ {c['ต่ำกว่าจริง'][2]} จาก 30")
    cap = "30 โลก (seed 1–30) · เชือก φ 0.95 · จุดส้ม = ต่ำกว่าค่าจริง (ดูกลับเร็วเกินจริง) · จุดน้ำเงิน = สูงกว่าหรือเท่า"
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-hl-real")
def _hl_real(fig):
    j = fig["ch04"]["จริง"]
    p, s = j["คู่"], j["เดี่ยว"]
    rows = [("LTC เดี่ยว · ช่วงเลือก", s["LTC"]["ช่วงเลือก"]),
            ("LTC–DOT · ช่วงเลือก", p["LTC-DOT"]["ช่วงเลือก"]),
            ("LTC–DOT · ช่วงตรวจ ตรึง h", p["LTC-DOT"]["ตรวจตรึงh"]),
            ("BTC–ETH · ช่วงเลือก", p["BTC-ETH"]["ช่วงเลือก"]),
            ("BTC–ETH · ช่วงตรวจ ตรึง h", p["BTC-ETH"]["ตรวจตรึงh"])]
    W, H, L, R = 760, 380, 200, 40
    lo, hi = 0, 120
    out = [text(16, 24, "Half-life (วัน) และช่วง 95% ของข้อมูลจริง", 12.5, INK, weight=700)]
    X = _axis(out, lo, hi, 20, 340, L, R, W, top=46)
    k = j["เกณฑ์วัน"]
    out.append(f'<line x1="{X(k):.1f}" y1="46" x2="{X(k):.1f}" y2="340" stroke="{C["green"]}" stroke-dasharray="5 4" stroke-width="1.6"/>')
    out.append(text(X(k) - 4, 58, f"เกณฑ์ {k} วัน", 10.5, C["green"], "end", 700))
    out.append(text(W - R, 40, "ลูกศร = ปลายบนเกิน 120 วันหรือไม่มีที่สิ้นสุด", 10, GREY, "end"))
    for i, (name, d) in enumerate(rows):
        y = 88 + 58 * i
        a, m = d["ครึ่งชีวิตล่าง"], d["ครึ่งชีวิต"]
        b = d["ครึ่งชีวิตบน"]
        col = C["red"] if b is None else C["blue"]
        out.append(text(L - 12, y + 4, name, 11.5, INK, "end", 700))
        end = hi if (b is None or b > hi) else b
        out.append(f'<line x1="{X(a):.1f}" y1="{y}" x2="{X(end):.1f}" y2="{y}" stroke="{col}" stroke-width="3"/>')
        out.append(f'<line x1="{X(a):.1f}" y1="{y - 8}" x2="{X(a):.1f}" y2="{y + 8}" stroke="{col}" stroke-width="2"/>')
        if end == hi:
            out.append(f'<path d="M{X(hi):.1f},{y} l-9,-6 l0,12 z" fill="{col}"/>')
        else:
            out.append(f'<line x1="{X(b):.1f}" y1="{y - 8}" x2="{X(b):.1f}" y2="{y + 8}" stroke="{col}" stroke-width="2"/>')
        if m <= hi:
            out.append(f'<circle cx="{X(m):.1f}" cy="{y}" r="5.5" fill="{C["purple"]}"/>')
        lab = f"{B.fmt(m)} [{B.fmt(a)}, {'∞' if b is None else B.fmt(b)}]"
        out.append(text(X(min(m, hi)), y - 13, lab, 10.5, INK, "middle").replace("<text ", '<text stroke="#fff" stroke-width="4" paint-order="stroke" ', 1))
    alt = ("ช่วง Half-life ห้าแถว " + " · ".join(
        f"{n} {B.fmt(d['ครึ่งชีวิต'])} วัน ช่วง {B.fmt(d['ครึ่งชีวิตล่าง'])} ถึง {'อนันต์' if d['ครึ่งชีวิตบน'] is None else B.fmt(d['ครึ่งชีวิตบน'])}"
        for n, d in rows))
    cap = "log ราคาปิดรายวัน Binance · AR(1) มีค่าคงที่ · ช่วง 95% แปลงจากช่วงของ φ · ช่วงตรวจใช้ h จากช่วงเลือก (ไม่แตะช่วงทดสอบสุดท้าย)"
    return wrap(W, H, alt, out, cap, "จริง")
