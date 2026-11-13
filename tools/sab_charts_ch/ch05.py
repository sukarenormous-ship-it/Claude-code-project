"""บท 5 — 12.17% บนจอ เหลือ 5.23% ในมือ · สเปกกราฟของบท

sab-carry-ladder    : บันไดสี่ขั้นของสถานะเดียวกัน (บนจอ → ต่อทุน → หลังค่าธรรมเนียม → ส่วนเกินหลัง hurdle) · แก้หมายเหตุ 25,000 (errata 13)
sab-crowding-ladder : มือที่แย่งเชือก — basis 3,000 → 500 แล้วส่วนเกินหลัง hurdle ลดจาก 5.23% เป็น −2.87% (hurdle คงที่ 4%)
"""
from sab_charts import chart, wrap, ladder_bars, bars, text, Frame, C, B


@chart("sab-carry-ladder")
def _carry_ladder(fig):
    d = fig["ch05"]["บันได"]
    m = fig["บัญชีมิน"]
    cap, fee, opp = m["ทุนภาค1"]["รวม"], d["ค่าธรรมเนียม"], d["ค่าเสียโอกาส"]
    rungs = [("อัตราบนจอ", d["บนจอ"]), ("ต่อทุนทั้งก้อน", d["ต่อทุน"]),
             ("หลังค่าธรรมเนียม", d["หลังค่าธรรมเนียม"]), ("ส่วนเกินหลัง hurdle", d["ส่วนเกินเปอร์เซ็นต์"])]
    subs = [f"basis ÷ ราคา spot {B.fmt(m['BTC']['spot'])}", f"basis ÷ ทุน {B.fmt(cap)}",
            f"หักค่าธรรมเนียม {B.fmt(fee)}", f"หักค่าเสียโอกาส {B.fmt(opp)}"]
    W, H = 760, 320
    out = ladder_bars(rungs, "สถานะเดียวกัน วัดสี่แบบ: อัตราต่อปีที่เหลือหลังแต่ละขั้น", "%", W, H)
    vals = [v for _, v in rungs]
    f = Frame(min(vals + [0]), max(vals + [0]), W, H)
    gw = (W - f.L - f.R) / len(rungs)
    for i, s in enumerate(subs):
        out.append(text(f.L + gw * i + gw / 2, f.Bm + 34, s, 10.5, C["grey"], "middle"))
    alt = (f"กราฟแท่งสี่ขั้น อัตราบนจอ {B.fmt(d['บนจอ'])}% เมื่อหารด้วยทุนทั้งก้อน {B.fmt(cap)} เหลือ {B.fmt(d['ต่อทุน'])}% "
           f"หักค่าธรรมเนียม {B.fmt(fee)} เหลือ {B.fmt(d['หลังค่าธรรมเนียม'])}% หักค่าเสียโอกาสที่ hurdle 4% "
           f"เหลือส่วนเกิน {B.fmt(d['ส่วนเกินเปอร์เซ็นต์'])}%")
    cap_txt = (f"ทุกแท่งเป็นอัตรา simple ต่อปีของสถานะเดียวกัน (spot 1 BTC + short futures 1 BTC · basis {B.fmt(d['basis'])} · 90 วัน) · "
               f"ทุน {B.fmt(cap)} = spot {B.fmt(m['ทุนภาค1']['spot'])} + หลักประกัน {B.fmt(m['ทุนภาค1']['หลักประกัน'])} "
               f"+ เงินสดอิสระ {B.fmt(m['ทุนภาค1']['เงินสดอิสระ'])} (เงินสด {B.fmt(fig['ch03']['เปิดไม้']['เงินสดหลังซื้อspot'])} "
               f"หลังซื้อ spot คือสองก้อนหลังรวมกัน ไม่ใช่เงินสำรองก้อนที่สาม) · ยังไม่รวมส่วนต่างราคาซื้อ-ขาย")
    return wrap(W, H, alt, out, cap_txt, "สอน")


@chart("sab-crowding-ladder")
def _crowding_ladder(fig):
    c5 = fig["ch05"]
    rows = c5["บันไดแย่ง"]
    W, H = 760, 330
    vals = [r["ส่วนเกินเปอร์เซ็นต์"] for r in rows]
    cats = [f"basis {B.fmt(r['basis'])}" for r in rows]
    out = bars(cats, vals, "มือที่แย่งเชือกมากขึ้น → basis แคบลง → ส่วนเกินหลัง hurdle 4% (% ต่อปีของทุน 125,000)",
               "%", W=W, H=H)
    f = Frame(min(vals + [0]), max(vals + [0]), W, H)
    gw = (W - f.L - f.R) / len(rows)
    for i, r in enumerate(rows):
        out.append(text(f.L + gw * i + gw / 2, f.Bm + 34, f"บนจอ {B.fmt(r['บนจอ'])}%", 10.5, C["grey"], "middle"))
    # callout: จุดที่มินเปิด
    x0 = f.L + gw / 2
    out.append(f'<line x1="{x0 + 30:.1f}" y1="{f.y(vals[0]) - 4:.1f}" x2="{x0 + 70:.1f}" y2="{f.y(vals[0]) - 4:.1f}" '
               f'stroke="{C["purple"]}" stroke-width="1.4"/>')
    out.append(text(x0 + 74, f.y(vals[0]), "มินเปิดที่นี่", 11, C["purple"], "start", 700))
    # เส้นคุ้มทุน: basis ราว 1,386 อยู่ระหว่างแถว 1,500 กับ 1,000
    be = c5["basisคุ้มทุน"]
    i_hi = next(i for i, r in enumerate(rows) if r["basis"] < be) - 1
    b_hi, b_lo = rows[i_hi]["basis"], rows[i_hi + 1]["basis"]
    xb = f.L + gw * (i_hi + 0.5) + gw * (b_hi - be) / (b_hi - b_lo)
    out.append(f'<line x1="{xb:.1f}" y1="{f.T - 6:.1f}" x2="{xb:.1f}" y2="{f.Bm:.1f}" stroke="{C["purple"]}" '
               f'stroke-dasharray="5 4" stroke-width="1.5"/>')
    out.append(text(xb + 6, f.T + 8, f"คุ้มทุนที่ basis ราว {B.fmt(be)}", 11, C["purple"], "start", 700))
    alt = (f"กราฟแท่งหกระดับ basis จาก {B.fmt(rows[0]['basis'])} ถึง {B.fmt(rows[-1]['basis'])} ส่วนเกินหลัง hurdle ลดจาก "
           f"{B.fmt(vals[0])}% เป็น {B.fmt(vals[-1])}% ติดลบเมื่อ basis ต่ำกว่าราว {B.fmt(be)} ทั้งที่อัตราบนจอยังเป็นบวกทุกแถว")
    cap_txt = (f"ทุน {B.fmt(fig['บัญชีมิน']['ทุนภาค1']['รวม'])} · ค่าธรรมเนียม taker 0.05% สามครั้ง · hurdle 4% คงที่ทุกแถว "
               f"— ตัวที่เปลี่ยนมีแค่ basis ที่คนเร่งยอมจ่าย · แถวใต้แท่งคืออัตราบนจอซึ่งยังบวกทุกแถว · "
               "ตัวเลขสมมติ ไม่ใช่ข้อมูลตลาด")
    return wrap(W, H, alt, out, cap_txt, "สอน")
