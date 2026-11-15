"""เล่ม 2 บท 3 — มีเชือกจริงไหม · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch03 เท่านั้น)

sab2-rw-thirty   : 30 โลกเดินสุ่ม 10 แถว · แถวบน slope ของการเปลี่ยนบนระดับ · แถวล่างค่าสถิติ (slope ÷ SE)
                   โลกของพี่ฝน (seed 16) สีม่วง · โลกที่แรงเท่าหรือแรงกว่าสีแดง · เส้น 5% ของตาราง
sab2-pass-length : จำนวนโลก (จาก 30) ที่ผ่าน ADF ที่เส้น 5% · เดินสุ่ม / เชือก φ 0.95 / เชือก φ 0.99 · 60 / 250 / 731 วัน
sab2-ltc-dot     : 📡 log LTC เดี่ยว (ลบ Mean ช่วงเลือก) กับ X ของ LTC–DOT (h ตรึงจากช่วงเลือก) · ช่วงเลือก + ช่วงตรวจ
"""

from sab_charts import B, C, chart, grouped_bars, lines, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]


def _stack(values, width):
    """จัดจุดเป็นกองตามช่องกว้าง width (แบบ dot histogram) · คืน [(ค่า, ลำดับในกอง)] ตามลำดับเดิม"""
    seen, out = {}, []
    for v in values:
        b = round(v / width)
        k = seen.get(b, 0)
        seen[b] = k + 1
        out.append((b * width, k))
    return out


def _strip(out, vals, hand_i, lo, hi, y0, title, width, marks, W=760, L=40, R=30, red_le=None):
    X = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)  # noqa: E731
    out.append(text(L, y0 - 74, title, 12.5, INK, weight=700))
    out.append(f'<line x1="{L}" y1="{y0}" x2="{W - R}" y2="{y0}" stroke="{C["axis"]}"/>')
    t = lo
    while t <= hi + 1e-9:
        out.append(f'<line x1="{X(t):.1f}" y1="{y0}" x2="{X(t):.1f}" y2="{y0 + 4}" stroke="{C["axis"]}"/>')
        out.append(text(X(t), y0 + 16, B.fmt(round(t, 2)), 10.5, GREY, "middle"))
        t += 0.5 if hi - lo <= 3 else 1
    for v, lab, col, dy in marks:
        out.append(f'<line x1="{X(v):.1f}" y1="{y0 - 66}" x2="{X(v):.1f}" y2="{y0}" stroke="{col}" stroke-dasharray="4 3" stroke-width="1.4"/>')
        out.append(text(X(v) + 4, y0 - 58 + dy, lab, 10.5, col, "start", 700))
    for i, ((bv, k), v) in enumerate(zip(_stack(vals, width), vals)):
        col = C["purple"] if i == hand_i else (C["red"] if red_le is not None and v <= red_le else GREY)
        r = 5.2 if i == hand_i else 4.2
        out.append(f'<circle cx="{X(bv):.1f}" cy="{y0 - 7 - 10 * k:.1f}" r="{r}" fill="{col}" fill-opacity=".85"/>')


@chart("sab2-rw-thirty")
def _rw_thirty(fig):
    c = fig["ch03"]
    h, t = c["มือ"], c["สามสิบโลก"]
    i = h["seed"] - 1                          # seed 1–30 เรียงตามลำดับ · seed 16 = ลำดับที่ 16
    W, H = 760, 330
    out = []
    _strip(out, t["slope"], i, -1.5, 0.5, 130, f"แถวบน: slope ของ 30 โลก (ลบ {t['ลบ']} โลก · แรงเท่าหรือแรงกว่าโลกพี่ฝน {t['slopeแรงเท่ามือ']} โลก)",
           0.1, [(0, "ศูนย์ = ไม่มีแรงดึง", MUTED, 0), (h["slope"], f"โลกพี่ฝน {B.fmt(h['slope'])}", C["purple"], 14)],
           red_le=h["slope"])
    _strip(out, t["stat"], i, -4.5, 1.0, 290, f"แถวล่าง: ค่าสถิติ slope ÷ SE (แรงเท่าหรือแรงกว่าโลกพี่ฝน {t['statแรงเท่ามือ']} โลก)",
           0.25, [(h["เส้น5"], f"เส้น 5% {B.fmt(h['เส้น5'])}", C["red"], 0), (h["stat"], f"โลกพี่ฝน {B.fmt(h['stat'])}", C["purple"], 14)],
           red_le=h["stat"])
    alt = (f"จุด 30 จุดสองแถว แถวบนคือ slope ของ 30 โลกเดินสุ่ม {t['ลบ']} โลกติดลบ โลกของพี่ฝน {B.fmt(h['slope'])} "
           f"แถวล่างคือค่าสถิติ โลกพี่ฝน {B.fmt(h['stat'])} มี {t['statแรงเท่ามือ']} โลกที่แรงเท่าหรือแรงกว่า "
           f"และมี {t['ผ่านเส้น5']} โลกที่ต่ำกว่าเส้น 5% {B.fmt(h['เส้น5'])}")
    cap = f"โลกเดินสุ่ม (ไม่มีเชือก) 30 โลก · โลกละ {h['แถว']} แถว · จุดม่วงคือโลกที่พี่ฝนส่งให้มิน"
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-pass-length")
def _pass_length(fig):
    c = fig["ch03"]["ความยาว"]
    cats = [f"{n} วัน" for n in c["วัน"]]
    series = [("เดินสุ่ม (ไม่มีเชือก)", c["เดินสุ่ม"], GREY),
              ("เชือก φ 0.95", c["เชือก095"], C["green"]),
              ("เชือก φ 0.99", c["เชือก099"], C["amber"])]
    parts = grouped_bars(cats, series, "ผ่าน ADF ที่เส้น 5% กี่โลก จาก 30 โลก")
    parts = [t.replace('font-weight="700" font-family="Sarabun,sans-serif">+', 'font-weight="700" font-family="Sarabun,sans-serif">')
             for t in parts]                   # จำนวนโลกไม่ใช่กำไร จึงไม่ใส่เครื่องหมาย +
    alt = ("แท่งสามกลุ่มตามความยาวข้อมูล 60 250 และ 731 วัน "
           f"เดินสุ่มผ่าน {c['เดินสุ่ม'][0]} {c['เดินสุ่ม'][1]} {c['เดินสุ่ม'][2]} โลก "
           f"เชือก φ 0.95 ผ่าน {c['เชือก095'][0]} {c['เชือก095'][1]} {c['เชือก095'][2]} โลก "
           f"เชือก φ 0.99 ผ่าน {c['เชือก099'][0]} {c['เชือก099'][1]} {c['เชือก099'][2]} โลก")
    cap = "แต่ละแท่งนับจาก 30 โลก (สุ่มใหม่ 30 ชุด) · ADF แบบมีค่าคงที่ · เส้น 5% ตามความยาวข้อมูล"
    return wrap(760, 330, alt, parts, cap, "จำลอง")


@chart("sab2-ltc-dot")
def _ltc_dot(fig):
    g = fig["ch03"]["จริง"]["กราฟ"]
    step, split = g["ทุก"], g["แบ่ง"]
    xs = [k * step for k in range(len(g["LTC"]))]
    series = [("log LTC เดี่ยว ลบ Mean (%)", g["LTC"], C["blue"]),
              ("X ของ LTC–DOT (%)", g["X"], C["amber"])]
    parts = lines(xs, series, "LTC เดี่ยว กับ X ของคู่ LTC–DOT: เกือบเป็นเส้นเดียวกัน", unit="%",
                  xticks=[(0, ""), (split, "เริ่มช่วงตรวจ")])
    # เส้นแบ่งช่วงเลือก | ช่วงตรวจ
    W, L, R, T, Bm = 760, 64, 24, 56, 250
    sx = L + split / xs[-1] * (W - L - R)
    parts.append(f'<line x1="{sx:.1f}" y1="{T}" x2="{sx:.1f}" y2="{Bm}" stroke="{C["purple"]}" stroke-dasharray="5 4" stroke-width="1.5"/>')
    parts.append(text(sx + 6, T + 14, "h ตรึงจากช่วงเลือก →", 11, C["purple"], weight=700))
    parts.append(text(L, Bm + 16, "เริ่มช่วงเลือก", 10.5, GREY, "start"))
    parts.append(text(W - R, Bm + 16, "จบช่วงตรวจ", 10.5, GREY, "end"))
    alt = (f"กราฟเส้นสองเส้นตลอด {g['วันรวม']} วัน เส้นน้ำเงินคือ log ราคา LTC ลบ Mean เส้นส้มคือ X ของคู่ LTC–DOT "
           f"สองเส้นขึ้นลงเกือบพร้อมกันทั้งช่วง สหสัมพันธ์ {B.fmt(g['corr'])} เส้นประม่วงแบ่งช่วงเลือกกับช่วงตรวจ")
    cap = f"ราคาปิดรายวัน Binance · จุดทุก {step} วัน · ช่วงเลือก {split} วัน แล้วต่อด้วยช่วงตรวจ (ไม่แตะช่วงทดสอบสุดท้าย)"
    return wrap(760, 320, alt, parts, cap, "จริง")
