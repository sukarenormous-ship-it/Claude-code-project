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
    col = BADGE[badge]
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="22" rx="6" fill="#fff" stroke="{col}" stroke-width="1.4"/>',
           text(x + 7, y + 15.5, label, 11.5, INK)]
    bw = 9 + 11.5 * 0.62 * len(badge)
    out.append(f'<rect x="{x + w - bw - 3:.1f}" y="{y + 3:.1f}" width="{bw:.1f}" height="16" rx="8" fill="{col}"/>')
    out.append(text(x + w - bw / 2 - 3, y + 15, badge, 10.5, "#fff", "middle", 700))
    return out


@chart("sab-strategy-map")
def _strategy_map(fig):
    dec = fig["เรื่อง"]["part18"]["close"]["ใบตัดสิน"]
    cols = ["สัญญาบังคับบรรจบ", "carry", "แรงดึงกลับ", "ให้สภาพคล่อง"]
    rows = ["โซ่ที่มีวันล็อก", "perp ไม่มีวันล็อก", "เชือกที่มีคนคอยดึง", "ยางยืด", "เส้นที่วาดเอง", "ไม่มีเชือก"]
    W, L, T, rh = 760, 150, 70, 58
    cw = (W - L - 12) / len(cols)
    H = T + rh * len(rows) + 10
    out = [text(12, 24, "แต่ละไอเดียอยู่ช่องไหน: ชนิดเชือก × กลไก", 13, INK, weight=700),
           text(12, 50, "ชนิดเชือก ↓  กลไก →", 11, MUTED)]
    for j, c in enumerate(cols):
        out.append(text(L + cw * j + cw / 2, 50, c, 12, INK, "middle", 700))
    for i, r in enumerate(rows):
        y = T + i * rh
        fill = "#fafafa" if i % 2 == 0 else "#fff"
        out.append(f'<rect x="8" y="{y}" width="{W - 16}" height="{rh - 4}" rx="8" fill="{fill}" stroke="{C["grid"]}"/>')
        out.append(text(18, y + rh / 2 + 2, r, 12, INK, weight=700))
    for j in range(1, len(cols)):
        x = L + cw * j
        out.append(f'<line x1="{x:.1f}" y1="{T - 6}" x2="{x:.1f}" y2="{H - 10}" stroke="{C["grid"]}" stroke-width="1.2"/>')

    def cell(i, j, label, badge, span=1, slot=0):
        x = L + cw * j + 5
        y = T + i * rh + 4 + slot * 25
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
           "คู่ A–B อยู่ช่องยางยืดกับแรงดึงกลับ ป้ายพัก บอท AI และบอท grid อยู่แถวไม่มีเชือก ป้ายไม่รับ")
    cap = ("ช่องเดียวกันตัดสินต่างกันได้: funding carry ของมินได้ป้ายกระดาษ บอท funding ของโจ้ได้ไม่รับ "
           "เพราะไม่บอกกฎออกและใครจ่าย · แถวล่างไม่มีอะไรดึงสองราคากลับ กำไรต้องมาจากการทายถูกหรือการรับของค้าง")
    return wrap(W, H, alt, out, cap, "แนวคิด")
