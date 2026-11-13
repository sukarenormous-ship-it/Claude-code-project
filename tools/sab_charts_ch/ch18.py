"""บท 18 — เอาไปต่อยอด · สเปกกราฟของบท

sab-strategy-map : ผังแผนที่กลยุทธ์ (ชนิดเชือก × กลไก × บท) พร้อมป้ายใบตัดสินของมิน
                   ระดับใบตัดสินอ่านจาก เรื่อง.part18.close.ใบตัดสิน (ภาพแนวคิด · ไม่มีตัวเลขตลาด)
sab-transfer-matrix เป็นตาราง HTML ในบท (ไม่ใช่กราฟ — แผน 10.3)
"""

from sab_charts import chart, wrap, text, C

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]
BADGE = {"เล็ก": C["green"], "กระดาษ": C["blue"], "พัก": C["amber"], "ไม่รับ": C["red"], "คัดออก": C["red"],
         "ตัวอย่าง": C["purple"], "เล่ม 2": GREY}


def _chip(x, y, w, label, badge):
    """ป้ายสองบรรทัด: ชื่อไอเดีย (บน) · ป้ายใบตัดสิน (ล่าง) — กันข้อความทับป้าย"""
    col = BADGE[badge]
    bw = 14 + 11 * 0.6 * len(badge)
    return [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="40" rx="6" fill="#fff" stroke="{col}" stroke-width="1.4"/>',
            text(x + 7, y + 15, label, 11.5, INK),
            f'<rect x="{x + 6:.1f}" y="{y + 20:.1f}" width="{bw:.1f}" height="15" rx="7.5" fill="{col}"/>',
            text(x + 6 + bw / 2, y + 31.5, badge, 10.5, "#fff", "middle", 700)]


@chart("sab-strategy-map")
def _strategy_map(fig):
    dec = fig["เรื่อง"]["part18"]["close"]["ใบตัดสิน"]
    cols = ["สัญญาบังคับบรรจบ", "carry", "การพยากรณ์", "ให้สภาพคล่อง"]   # ชื่อกลไกตรึง (ข้อตัดสิน 34)
    rows = ["โซ่ที่มีวันล็อก", "perp ไม่มีวันล็อก", "เชือกที่มีคนคอยดึง", "ยางยืด", "เส้นที่วาดเอง", "ไม่มีเชือก"]
    W, L, T = 760, 150, 70
    two = {1, 5}                                   # แถวที่มีสองไอเดียในช่องเดียว
    hs = [96 if i in two else 52 for i in range(len(rows))]
    ys = [T + sum(hs[:i]) for i in range(len(rows))]
    cw = (W - L - 12) / len(cols)
    H = T + sum(hs) + 10
    out = [text(12, 24, "ไอเดียอยู่ช่องไหน", 13, INK, weight=700),
           text(12, 50, "ชนิดเชือก ↓  กลไก →", 11, MUTED)]
    for j, c in enumerate(cols):
        out.append(text(L + cw * j + cw / 2, 50, c, 12, INK, "middle", 700))
    for i, r in enumerate(rows):
        y, rh = ys[i], hs[i]
        fill = "#fafafa" if i % 2 == 0 else "#fff"
        out.append(f'<rect x="8" y="{y}" width="{W - 16}" height="{rh - 4}" rx="8" fill="{fill}" stroke="{C["grid"]}"/>')
        out.append(text(18, y + rh / 2 + 2, r, 12, INK, weight=700))
    for j in range(1, len(cols)):
        x = L + cw * j
        out.append(f'<line x1="{x:.1f}" y1="{T - 6}" x2="{x:.1f}" y2="{H - 10}" stroke="{C["grid"]}" stroke-width="1.2"/>')

    def cell(i, j, label, badge, span=1, slot=0):
        x = L + cw * j + 5
        y = ys[i] + 4 + slot * 44
        return _chip(x, y, cw * span - 10, label, badge)

    out += cell(0, 0, "carry BTC · บท 3–6", dec["carry"], span=2, slot=0)
    out += cell(1, 1, "funding carry · บท 7", dec["funding carry"], slot=0)
    out += cell(1, 1, "บอท funding ของโจ้", dec["บอทของโจ้"], slot=1)
    out += cell(2, 0, "โทเคนแลกคืน · บท 18", "ตัวอย่าง", slot=0)
    out += cell(3, 2, "คู่ A–B · บท 8–16", dec["คู่ A–B"], slot=0)
    out += cell(4, 2, "คู่จากการค้น · บท 10", "คัดออก", slot=0)
    out += cell(5, 2, "บอท AI ของโจ้", dec["บอทของโจ้"], slot=0)
    out += cell(5, 3, "บอท grid ของโจ้", dec["บอทของโจ้"], slot=0)
    out += cell(5, 3, "ดูแลสภาพคล่อง · บท 1", "เล่ม 2", slot=1)
    alt = ("ผังตาราง แถวคือชนิดเชือกหกแบบ คอลัมน์คือกลไกสี่แบบ carry BTC อยู่ช่องโซ่ที่มีวันล็อก ป้ายเล็ก "
           "funding carry อยู่ช่อง perp ป้ายกระดาษ ช่องเดียวกันมีบอท funding ของโจ้ ป้ายไม่รับ "
           "คู่ A–B อยู่ช่องยางยืดกับการพยากรณ์ ป้ายพัก บอท AI และบอท grid อยู่แถวไม่มีเชือก ป้ายไม่รับ")
    cap = ("ไอเดียใหม่ต้องหาช่องลงก่อนคำนวณ · ช่องเดียวกันตัดสินต่างได้: บอท funding ของโจ้ไม่บอกกฎออกและใครจ่าย "
           "· แถวล่างไม่มีอะไรดึงราคากลับ")
    return wrap(W, H, alt, out, cap, "แนวคิด")
