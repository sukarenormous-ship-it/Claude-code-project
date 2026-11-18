"""เล่ม 2 บท 3 — มีเชือกจริงไหม · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch03 เท่านั้น)

sab2-rw-thirty   : 30 โลกเดินสุ่ม 10 แถว · แถวบน slope ของการเปลี่ยนบนระดับ · แถวล่างค่าสถิติ (slope ÷ SE)
                   โลกของพี่ฝน (seed 16) สีม่วง · โลกที่แรงเท่าหรือแรงกว่าสีเทาเข้ม · เส้น 5% ของตาราง
sab2-pass-length : จำนวนโลก (จาก 30) ที่ผ่าน ADF ที่เส้น 5% · เดินสุ่ม / เชือก φ 0.95 / เชือก φ 0.99 · 60 / 250 / 731 วัน
sab2-ltc-dot     : 📡 log LTC เดี่ยว (ลบ Mean ช่วงเลือก) กับ X ของ LTC–DOT (h ตรึงจากช่วงเลือก) · ช่วงเลือก + ช่วงตรวจ
sab2-ten-rows    : 🎲 สิบแถวของโลกที่ 16 · แกนนอน X วันนี้ แกนตั้งการเปลี่ยน · เส้น slope −0.77 เทียบเส้น 0 · แถว 7 กับ 5 เด่น
"""

from sab_charts import B, C, chart, grouped_bars, lines, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]
GREEN_LIGHT = "#86efac"   # เชือกอ่อน (φ ใกล้ 1) = เขียวอ่อน · ไล่เฉดสีเดียว (README)


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
        col = C["purple"] if i == hand_i else (INK if red_le is not None and v <= red_le else GREY)
        r = 5.2 if i == hand_i else 4.2
        cx = X(v) if i == hand_i else X(bv)   # จุดม่วงวางที่ค่าจริงให้ตรงกับเส้นประของมัน
        out.append(f'<circle cx="{cx:.1f}" cy="{y0 - 7 - 10 * k:.1f}" r="{r}" fill="{col}" fill-opacity=".85"/>')


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
           0.25, [(h["เส้น5"], f"เส้น 5% {B.fmt(h['เส้น5'])}", INK, 0), (h["stat"], f"โลกพี่ฝน {B.fmt(h['stat'])}", C["purple"], 14)],
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
              ("เชือก φ 0.99", c["เชือก099"], GREEN_LIGHT)]
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
    series = [("log LTC เดี่ยว ลบ Mean (%)", g["LTC"], C["amber"]),
              ("X ของ LTC–DOT (%)", g["X"], C["blue"])]
    parts = lines(xs, series, "LTC เดี่ยว กับ X ของคู่ LTC–DOT: เกือบเป็นเส้นเดียวกัน", unit="%",
                  xticks=[(0, ""), (split, "เริ่มช่วงตรวจ")])
    # เส้นแบ่งช่วงเลือก | ช่วงตรวจ
    W, L, R, T, Bm = 760, 64, 24, 56, 250
    sx = L + split / xs[-1] * (W - L - R)
    parts.append(f'<line x1="{sx:.1f}" y1="{T}" x2="{sx:.1f}" y2="{Bm}" stroke="{C["purple"]}" stroke-dasharray="5 4" stroke-width="1.5"/>')
    parts.append(text(sx + 6, T + 14, "h ตรึงจากช่วงเลือก →", 11, C["purple"], weight=700))
    parts.append(text(L, Bm + 16, "เริ่มช่วงเลือก", 10.5, GREY, "start"))
    parts.append(text(W - R, Bm + 16, "จบช่วงตรวจ", 10.5, GREY, "end"))
    alt = (f"กราฟเส้นสองเส้นตลอด {g['วันรวม']} วัน เส้นส้มคือ log ราคา LTC ลบ Mean เส้นน้ำเงินคือ X ของคู่ LTC–DOT "
           f"สองเส้นขึ้นลงเกือบพร้อมกันทั้งช่วง สหสัมพันธ์ {B.fmt(g['corr'])} เส้นประม่วงแบ่งช่วงเลือกกับช่วงตรวจ")
    cap = f"ราคาปิดรายวัน Binance · จุดทุก {step} วัน · ช่วงเลือก {split} วัน แล้วต่อด้วยช่วงตรวจ (ไม่แตะช่วงทดสอบสุดท้าย)"
    return wrap(760, 320, alt, parts, cap, "จริง")


@chart("sab2-ten-rows")
def _ten_rows(fig):
    h = fig["ch03"]["มือ"]
    xs, ys, prod = h["วันนี้"], h["เปลี่ยน"], h["คูณ"]
    W, H, L, R, T, Bm = 760, 390, 70, 230, 60, 330
    x0, x1, y0, y1 = -6.5, 3.5, -8.5, 7.5
    X = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - y0) / (y1 - y0) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "สิบแถวของโลกที่ไม่มีเชือก: สองแถวที่บังเอิญเด้งเข้าหากลางพาเส้นเอียงลง", 13.5, INK, weight=700)]
    # มุมที่ "ขยับเข้าหา Mean" (ผลคูณติดลบ): ซ้ายบนกับขวาล่าง
    out.append(f'<rect x="{L}" y="{T}" width="{X(0) - L:.1f}" height="{Y(0) - T:.1f}" fill="{C["green"]}" fill-opacity=".07"/>')
    out.append(f'<rect x="{X(0):.1f}" y="{Y(0):.1f}" width="{W - R - X(0):.1f}" height="{Bm - Y(0):.1f}" fill="{C["green"]}" fill-opacity=".07"/>')
    out.append(text(X(-4.6), Y(0) - 8, "ต่ำกว่า Mean แล้วขยับขึ้น", 10, C["green"]))
    out.append(text(W - R - 6, Y(-5.6), "สูงกว่า Mean แล้วขยับลง", 10, C["green"], "end"))
    for g in (-6, -4, -2, 0, 2):
        out.append(f'<line x1="{X(g):.1f}" y1="{T}" x2="{X(g):.1f}" y2="{Bm}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(X(g), Bm + 17, B.fmt(g), 10.5, GREY, "middle"))
    for g in (-6, -3, 0, 3, 6):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 10.5, GREY, "end"))
    out.append(text((L + W - R) / 2, Bm + 36, "X วันนี้ (%, ลบ Mean แล้ว)", 11.5, MUTED, "middle", 700))
    out.append(text(16, T - 12, "การเปลี่ยนไปพรุ่งนี้", 11.5, MUTED, "start", 700))
    # เส้นศูนย์ = คำตอบจริงของโลกนี้ · เส้นที่ Regression ได้
    out.append(f'<line x1="{L}" y1="{Y(0):.1f}" x2="{W - R}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="6 4"/>')
    sl, c0 = h["slope3"], h["Meanเปลี่ยน"]
    out.append(f'<line x1="{X(x0):.1f}" y1="{Y(c0 + sl * x0):.1f}" x2="{X(x1):.1f}" y2="{Y(c0 + sl * x1):.1f}" stroke="{C["blue"]}" stroke-width="2.6"/>')
    big = {6: (10, 4, "start"), 4: (-10, 4, "end")}        # แถว 7 กับแถว 5 (ลำดับ 6 กับ 4)
    for i, (x, y) in enumerate(zip(xs, ys)):
        col = C["purple"] if i in big else GREY
        out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{6 if i in big else 4.5}" fill="{col}" fill-opacity="{1 if i in big else .8}"/>')
        if i in big:
            dx, dy, anc = big[i]
            out.append(text(X(x) + dx, Y(y) + dy, f"แถว {i + 1} · ผลคูณ {B.fmt(prod[i])}", 10.5, C["purple"], anc, 700))
        else:
            out.append(text(X(x) + 7, Y(y) + (14 if i == 2 else -6), str(i + 1), 9.5, MUTED))   # แถว 3 ป้ายอยู่ใต้จุด (เส้นผ่านด้านบน)
    lx = W - R + 18
    out.append(f'<line x1="{lx}" y1="{T + 16}" x2="{lx + 26}" y2="{T + 16}" stroke="{C["blue"]}" stroke-width="2.6"/>')
    out.append(text(lx + 32, T + 20, f"Regression: slope {B.fmt(h['slope'])}", 11, C["blue"], weight=700))
    out.append(text(lx + 32, T + 36, f"({B.fmt(h['รวมคูณ'])} ÷ {B.fmt(h['รวมกำลังสอง'])})", 10.5, MUTED))
    out.append(f'<line x1="{lx}" y1="{T + 62}" x2="{lx + 26}" y2="{T + 62}" stroke="{INK}" stroke-width="2" stroke-dasharray="6 4"/>')
    out.append(text(lx + 32, T + 66, "slope 0 = คำตอบจริง", 11, INK, weight=700))
    out.append(text(lx + 32, T + 82, "(เดินสุ่ม ไม่มีเชือก)", 10.5, MUTED))
    out.append(text(lx, T + 116, f"แถว 7 แถวเดียวให้ {B.fmt(prod[6])}", 10.5, INK))
    out.append(text(lx, T + 132, f"จากผลรวม {B.fmt(h['รวมคูณ'])}", 10.5, INK))
    out.append(text(lx, T + 152, "ตัวเลขข้างจุด = แถวในตาราง", 10, MUTED))
    alt = (f"กราฟจุดสิบจุด แกนนอนคือ X วันนี้ แกนตั้งคือการเปลี่ยนไปพรุ่งนี้ เส้นน้ำเงินเอียงลง slope {B.fmt(h['slope'])} "
           f"เส้นประเทาเข้มคือ slope 0 ซึ่งเป็นคำตอบจริง จุดแถว 7 อยู่ซ้ายบน (−5.4 แล้วขึ้น 6.3) และแถว 5 อยู่ขวาล่าง (2 แล้วลง 7.3) "
           "สองจุดนี้อยู่ในมุมที่ขยับเข้าหา Mean และดึงเส้นให้เอียงลง")
    cap = f"โลกเดินสุ่มที่ {h['seed']} ของพี่ฝน · {h['แถว']} แถว · จุดเดียวกับตารางในตอน ก · 1"
    return wrap(W, H, alt, out, cap, "จำลอง")
