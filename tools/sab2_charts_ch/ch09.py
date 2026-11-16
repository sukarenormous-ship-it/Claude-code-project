"""เล่ม 2 บท 9 — หักแรงร่วมออก เหลืออะไร · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch09 เท่านั้น)

sab2-fac-hand    : หกวันสอน · การขยับของ BTC · การขยับของ A · ส่วนที่เหลือของ A (A − 1.5 × BTC) เป็นแท่งข้างกัน
sab2-fac-beta    : 📡 β ของ 9 เหรียญบน BTC ช่วงเลือกเทียบช่วงตรวจ (ถดถอยการขยับ log รายวัน)
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
