"""เล่ม 2 บท 9 — หักแรงร่วมออก เหลืออะไร · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch09 เท่านั้น)

sab2-fac-hand    : หกวันสอน · การขยับของ BTC · การขยับของ A · ส่วนที่เหลือของ A (A − 1.5 × BTC) เป็นแท่งข้างกัน
sab2-fac-beta    : 📡 β ของ 9 เหรียญบน BTC ช่วงเลือกเทียบช่วงตรวจ (ถดถอยการขยับ log รายวัน)
sab2-fac-weeks   : แปดสัปดาห์ของตอน ง · 1 · จุด (สัปดาห์นี้, สัปดาห์ถัดไป) เจ็ดคู่ · ค่าเฉลี่ยสองกอง · เส้นความชัน −17 ÷ 34
sab2-fac-horizon : 📡 correlation ของส่วนที่เหลือช่วงนี้กับช่วงถัดไป (รวม 9 เหรียญ) ที่ 1 / 5 / 10 / 20 วัน · ช่วงเลือกกับช่วงตรวจ
"""

from sab_charts import B, C, Frame, chart, text, wrap


def _gbars(cats, series, title, ticks, W=760, H=300, plus=True):
    """แท่งเรียงข้างกันแบบ grouped_bars แต่ใช้เส้นแกนจาก JSON (ทุกเลขบนแกนต้องมีที่มา)"""
    vals = [v for _, s_, _ in series for v in s_] + list(ticks)
    f = Frame(min(vals + [0]), max(vals + [0]), W, H, T=70, pad=0.04)
    out = f.grid(ticks)
    gw = (W - f.L - f.R) / len(cats)
    bw = min(46, (gw - 24) / len(series))
    for i, c in enumerate(cats):
        cx = f.L + gw * i + gw / 2
        for j, (_, s_, col) in enumerate(series):
            v = s_[i]
            x = cx - len(series) * (bw + 4) / 2 + j * (bw + 4)
            y0, y1 = f.y(0), f.y(v)
            out.append(f'<rect x="{x:.1f}" y="{min(y0, y1):.1f}" width="{bw:.1f}" height="{max(1, abs(y1 - y0)):.1f}" rx="2" fill="{col}"/>')
            v = int(v) if float(v) == int(v) else v
            lab = ("+" if plus and v > 0 else "") + B.fmt(v)
            out.append(text(x + bw / 2, (y1 - 6) if v >= 0 else (y1 + 14), lab, 10.5, col, "middle", 700))
        out.append(text(cx, f.Bm + 18, c, 11.5, C["muted"], "middle"))
    lx = f.L
    for name, _, col in series:
        out.append(f'<rect x="{lx}" y="{f.T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 20, name, 11.5, C["muted"]))
        lx += 30 + 8 * len(name)
    out.append(text(f.L, f.T - 46, title, 13, C["ink"], weight=700))
    return out


@chart("sab2-fac-hand")
def _hand(fig):
    h = fig["ch09"]["มือ"]
    a = h["A"]
    cats = [f"วันที่ {i + 1}" for i in range(len(h["m"]))]
    series = [("BTC ขยับ (%)", h["m"], C["amber"]), ("A ขยับ (%)", a["r"], C["blue"]),
              (f"ส่วนที่เหลือของ A (A − {B.fmt(a['beta'])} × BTC)", a["res"], C["purple"])]
    parts = _gbars(cats, series, "หกวันของ A กับ BTC และส่วนที่ BTC อธิบายไม่ได้", fig["ch09"]["แกน"]["มือ"])
    alt = ("แท่งสามสีต่อวัน วันที่ 1 และ 2 A ขยับ 3 และ −3 ขณะ BTC ขยับ 2 และ −2 ส่วนที่เหลือเป็นศูนย์ "
           "วันที่ 5 และ 6 BTC ไม่ขยับ ส่วนที่เหลือของ A จึงเท่ากับที่ A ขยับเองคือ 1 และ −2")
    cap = f"หกวันสมมติของตอน ก · β ของ A บน BTC คือ {B.fmt(a['smr'])} ÷ {B.fmt(h['smm'])} = {B.fmt(a['beta'])}"
    return wrap(760, 300, alt, parts, cap, "สอน")


@chart("sab2-fac-beta")
def _beta(fig):
    j = fig["ch09"]["จริง"]
    order = j["ลำดับ"]
    f = [j["เหรียญ"][c]["beta"] for c in order]
    v = [j["เหรียญ"][c]["betaV"] for c in order]
    series = [("ช่วงเลือก (β ที่ใช้)", f, C["blue"]), ("ช่วงตรวจ (วัดใหม่)", v, C["amber"])]
    parts = _gbars(order, series, "β ของแต่ละเหรียญบน BTC จากการขยับ log รายวัน", fig["ch09"]["แกน"]["beta"], plus=False)
    alt = (f"β ช่วงเลือกอยู่ระหว่าง {B.fmt(j['betaต่ำสุด'])} ถึง {B.fmt(j['betaสูงสุด'])} ส่วนช่วงตรวจอยู่ระหว่าง "
           f"{B.fmt(j['betaVต่ำสุด'])} ถึง {B.fmt(j['betaVสูงสุด'])} และสูงขึ้นทุกเหรียญ")
    cap = (f"ราคาปิดรายวัน Binance · ช่วงเลือก {j['เริ่มเลือก']} ถึง {j['จบเลือก']} · ช่วงตรวจ {j['เริ่มตรวจ']} ถึง {j['จบตรวจ']} "
           "· เรียงตาม β ช่วงเลือก")
    return wrap(760, 300, alt, parts, cap, "จริง")


@chart("sab2-fac-horizon")
def _horizon(fig):
    rows = fig["ch09"]["ระยะแถว"]
    cats = [f"{r['k']} วัน" for r in rows]
    series = [("ช่วงเลือก", [r["F"] for r in rows], C["blue"]), ("ช่วงตรวจ", [r["V"] for r in rows], C["amber"])]
    parts = _gbars(cats, series, "correlation ของส่วนที่เหลือช่วงนี้กับช่วงถัดไป (บวก = ไปต่อ · ลบ = กลับทิศ)",
                   fig["ch09"]["แกน"]["ระยะ"])
    r20 = rows[-1]
    alt = (f"ที่ 1 วัน ช่วงเลือกได้ {B.fmt(rows[0]['F'])} ช่วงตรวจได้ {B.fmt(rows[0]['V'])} ที่ 20 วัน ช่วงเลือกได้ "
           f"{B.fmt(r20['F'])} ช่วงตรวจได้ {B.fmt(r20['V'])}")
    cap = "ส่วนที่เหลือของ 9 เหรียญบน BTC (β จากช่วงเลือก) · แบ่งเป็นช่วงไม่ซ้อนกันแล้วจับคู่ช่วงนี้กับช่วงถัดไป · รวมทุกเหรียญ"
    return wrap(760, 300, alt, parts, cap, "จริง")


@chart("sab2-fac-weeks")
def _weeks(fig):
    w = fig["ch09"]["สัปดาห์"]
    ticks = fig["ch09"]["แกนสัปดาห์"]
    W, H = 760, 340
    top, bm = 60, 300
    lo, hi = min(ticks) - 0.5, max(ticks) + 0.5
    side = bm - top
    L0 = 70
    num = lambda v: B.fmt(int(v)) if float(v) == int(v) else B.fmt(v)  # noqa: E731
    xp = lambda v: L0 + (v - lo) / (hi - lo) * side  # noqa: E731
    y = lambda v: bm - (v - lo) / (hi - lo) * side  # noqa: E731
    out = []
    for t in ticks:
        for a in ("x", "y"):
            col, wd = (C["axis"], 1.5) if t == 0 else (C["grid"], 1)
            if a == "x":
                out.append(f'<line x1="{xp(t):.1f}" y1="{top}" x2="{xp(t):.1f}" y2="{bm}" stroke="{col}" stroke-width="{wd}"/>')
            else:
                out.append(f'<line x1="{L0}" y1="{y(t):.1f}" x2="{L0 + side}" y2="{y(t):.1f}" stroke="{col}" stroke-width="{wd}"/>')
        out.append(text(xp(t), bm + 15, B.fmt(t), 10.5, C["grey"], "middle"))
        out.append(text(L0 - 8, y(t) + 4, B.fmt(t), 10.5, C["grey"], "end"))
    out.append(text(L0 + side / 2, bm + 32, "สัปดาห์นี้ (%)", 11.5, C["muted"], "middle"))
    out.append(text(L0 - 44, top - 12, "สัปดาห์ถัดไป (%)", 11.5, C["muted"], "start"))
    # ค่าเฉลี่ยสองกอง
    for xa, xb, v, col, lab in ((0, hi, w["ขึ้นเฉลี่ย"], C["red"], f"หลังสัปดาห์ที่ขึ้น เฉลี่ย {num(w['ขึ้นเฉลี่ย'])}"),
                                (lo, 0, w["ลงเฉลี่ย"], C["green"], f"หลังสัปดาห์ที่ลง เฉลี่ย {B.fmt(w['ลงเฉลี่ย'])}")):
        out.append(f'<line x1="{xp(xa) + 4:.1f}" y1="{y(v):.1f}" x2="{xp(xb) - 4:.1f}" y2="{y(v):.1f}" stroke="{col}" stroke-width="2.4" stroke-dasharray="5 3"/>')
    # เส้นความชัน (ผ่านศูนย์ เพราะ Mean ของทั้งสองคอลัมน์เป็นศูนย์)
    sl = w["slope"]
    out.append(f'<line x1="{xp(lo):.1f}" y1="{y(sl * lo):.1f}" x2="{xp(hi):.1f}" y2="{y(sl * hi):.1f}" stroke="{C["purple"]}" stroke-width="2.4"/>')
    seen = {}
    for a, b in w["คู่"]:
        seen[(a, b)] = seen.get((a, b), 0) + 1
    for (a, b), n in seen.items():
        out.append(f'<circle cx="{xp(a):.1f}" cy="{y(b):.1f}" r="6" fill="{C["blue"]}" fill-opacity="0.85"/>')
        if n > 1:
            out.append(text(xp(a) + 10, y(b) + 4, f"× {n}", 10.5, C["blue"], "start", 700))
    # คำอธิบายด้านขวา
    rx = L0 + side + 40
    out.append(text(rx, top + 8, "แปดสัปดาห์ของส่วนที่เหลือ → เจ็ดคู่ (สัปดาห์นี้, สัปดาห์ถัดไป)", 13, C["ink"], weight=700))
    rows = [("จุดน้ำเงิน", "หนึ่งคู่ของสัปดาห์ติดกัน (คู่ที่ซ้ำกันเขียน × 2)", C["blue"]),
            ("เส้นประแดง", f"กองที่ขึ้น {w['ขึ้นจำนวน']} สัปดาห์ ถัดไปรวม {B.fmt(w['ผลรวมขึ้น'])} เฉลี่ย {num(w['ขึ้นเฉลี่ย'])}", C["red"]),
            ("เส้นประเขียว", f"กองที่ลง {w['ลงจำนวน']} สัปดาห์ ถัดไปรวม {B.fmt(w['ผลรวมลง'])} เฉลี่ย {B.fmt(w['ลงเฉลี่ย'])}", C["green"]),
            ("เส้นม่วง", f"Regression ความชัน {B.fmt(w['sxy'])} ÷ {B.fmt(w['sxx'])} = {num(sl)}", C["purple"])]
    for i, (h, body, col) in enumerate(rows):
        yy = top + 44 + i * 46
        out.append(text(rx, yy, h, 12, col, weight=700))
        out.append(text(rx, yy + 17, body, 11.5, C["ink"]))
    out.append(text(rx, top + 44 + 4 * 46 + 4, "เส้นเอียงลง = ขึ้นแล้วมักลง ลงแล้วมักขึ้น (กลับทิศ)", 12, C["purple"], weight=700))
    alt = (f"จุดเจ็ดจุดของสัปดาห์นี้กับสัปดาห์ถัดไป สัปดาห์ที่ขึ้นตามด้วยค่าเฉลี่ย {num(w['ขึ้นเฉลี่ย'])} "
           f"สัปดาห์ที่ลงตามด้วยค่าเฉลี่ย {B.fmt(w['ลงเฉลี่ย'])} เส้น Regression เอียงลงด้วยความชัน {B.fmt(sl)}")
    cap = f"แปดสัปดาห์สมมติของตอน ง · 1 · {', '.join(B.fmt(v) for v in w['ค่า'])} (%)"
    return wrap(W, H, alt, out, cap, "สอน")
