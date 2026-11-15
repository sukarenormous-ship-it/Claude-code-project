"""บท 5 — 12.17% บนจอ เหลือ 5.23% ในมือ · สเปกกราฟของบท

sab-carry-ladder    : บันไดสี่ขั้นของสถานะเดียวกัน (บนจอ → ต่อทุน → หลังค่าธรรมเนียม → ส่วนเกินหลัง hurdle) · แก้หมายเหตุ 25,000 (errata 13)
sab-crowding-ladder : Crowding (มือที่แย่งเชือก) — basis 3,000 → 500 แล้วส่วนเกินหลัง hurdle ลดจาก 5.23% เป็น −2.87% (hurdle คงที่ 4%)
"""
import re

from sab_charts import chart, wrap, ladder_bars, bars, text, Frame, C, B


def _num(v):
    """154.0 → 154 (ค่าเต็มใน JSON เป็น float)"""
    return B.fmt(int(v)) if float(v).is_integer() else B.fmt(v)


@chart("sab-carry-ladder")
def _carry_ladder(fig):
    d = fig["ch05"]["บันได"]
    m = fig["บัญชีมิน"]
    cap, fee, opp = m["ทุนภาค1"]["รวม"], d["ค่าธรรมเนียม"], d["ค่าเสียโอกาส"]
    rungs = [("อัตราบนจอ", d["บนจอ"]), ("ต่อทุนทั้งก้อน", d["ต่อทุน"]),
             ("หลังค่าธรรมเนียม", d["หลังค่าธรรมเนียม"]), ("ส่วนเกินหลัง hurdle", d["ส่วนเกินเปอร์เซ็นต์"])]
    subs = [f"basis ÷ ราคา spot {B.fmt(m['BTC']['spot'])}", f"basis ÷ ทุน {B.fmt(cap)}",
            f"หักค่าธรรมเนียม {_num(fee)}", f"หักค่าเสียโอกาส {B.fmt(opp)}"]
    W, H = 760, 320
    out = ladder_bars(rungs, "ไม้เดียวกัน วัดสี่แบบ (% ต่อปี)", "%", W, H)
    out = [re.sub(r">([−+]\d+)\.0<", r">\1<", o) for o in out]          # ป้ายส่วนที่หาย −4.0 → −4
    vals = [v for _, v in rungs]
    f = Frame(min(vals + [0]), max(vals + [0]), W, H)
    gw = (W - f.L - f.R) / len(rungs)
    for i, s in enumerate(subs):
        out.append(text(f.L + gw * i + gw / 2, f.Bm + 34, s, 10.5, C["grey"], "middle"))
    alt = (f"กราฟแท่งสี่ขั้น อัตราบนจอ {B.fmt(d['บนจอ'])}% เมื่อหารด้วยทุนทั้งก้อน {B.fmt(cap)} เหลือ {B.fmt(d['ต่อทุน'])}% "
           f"หักค่าธรรมเนียม {_num(fee)} เหลือ {B.fmt(d['หลังค่าธรรมเนียม'])}% หักค่าเสียโอกาสที่ hurdle 4% "
           f"เหลือส่วนเกิน {B.fmt(d['ส่วนเกินเปอร์เซ็นต์'])}%")
    cap_txt = f"ไม้เดียวกัน ทุน {B.fmt(cap)} · ยืดเป็นต่อปีแบบคูณตรง ไม่ทบต้น · ยังไม่รวม Bid-Ask Spread"
    return wrap(W, H, alt, out, cap_txt, "สอน")


@chart("sab-crowding-ladder")
def _crowding_ladder(fig):
    c5 = fig["ch05"]
    rows = c5["บันไดแย่ง"]
    W, H = 760, 330
    vals = [r["ส่วนเกินเปอร์เซ็นต์"] for r in rows]
    cats = [f"basis {B.fmt(r['basis'])}" for r in rows]
    out = bars(cats, vals, "Crowding มากขึ้น → basis แคบลง → ส่วนเกินหลัง hurdle (% ต่อปี)",
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
    cap_txt = (f"ทุน {B.fmt(fig['บัญชีมิน']['ทุนภาค1']['รวม'])} · ค่าธรรมเนียมและ hurdle 4% คงที่ ตัวที่เปลี่ยนมีแค่ basis "
               "· แถวใต้แท่งคืออัตราบนจอ ยังบวกทุกแถว · ไม่ใช่ข้อมูลตลาด")
    return wrap(W, H, alt, out, cap_txt, "สอน")


@chart("sab-capital-tradeoff")
def _capital_tradeoff(fig):
    """v2 (ตอน ข · กันเงินมากขึ้น): ทุนสามขนาด — ซ้าย = กันชน (% ที่ราคาสัญญาขึ้นสะสมได้) เทียบคืนวันที่ 9 ·
    ขวา = ส่วนเกินหลัง hurdle · ทุนที่กันชนไม่ถึงคืนวันที่ 9 ส่วนเกินเป็นแค่ตัวเลขบนกระดาษ"""
    rows = [fig["ch05"]["v2"]["ทุน"][k] for k in ("120000", "125000", "150000")]
    night = fig["ch04"]["futuresขึ้นเปอร์เซ็นต์คืนวันที่9"]
    who = {120000: " (ต้น)", 125000: " (มิน)", 150000: ""}
    W, rh, top = 760, 58, 118
    H = top + rh * len(rows) + 40
    L1, R1, L2, R2 = 170, 430, 500, 736
    bmax = max(r["กันชน"] for r in rows) * 1.15
    emax = max(r["ส่วนเกินเปอร์เซ็นต์"] for r in rows) * 1.8
    X1 = lambda v: L1 + v / bmax * (R1 - L1)                   # noqa: E731
    X2 = lambda v: L2 + v / emax * (R2 - L2)                   # noqa: E731
    out = [text(16, 26, "กันเงินมากขึ้น กันชนหนาขึ้น แต่ส่วนเกินบางลง — ต้องรอดก่อน ส่วนเกินจึงเป็นเงิน", 13.5, C["ink"], weight=700)]
    out.append(text(L1, 62, "กันชน: ราคาสัญญาขึ้นสะสมได้กี่ %", 12, C["ink"], weight=700))
    out.append(text(L2, 62, "ส่วนเกินหลัง hurdle (% ต่อปี)", 12, C["ink"], weight=700))
    yb = top + rh * len(rows) - 8
    for x0, x1 in ((L1, R1), (L2, R2)):
        out.append(f'<line x1="{x0}" y1="{top - 30}" x2="{x0}" y2="{yb}" stroke="{C["axis"]}" stroke-width="1.5"/>')
    xn = X1(night)
    out.append(f'<line x1="{xn:.1f}" y1="{top - 30}" x2="{xn:.1f}" y2="{yb}" stroke="{C["red"]}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    out.append(text(xn + 6, top - 18, f"คืนวันที่ 9 ขึ้น {B.fmt(night)}%", 11, C["red"], "start", 700))
    bh = 24
    for i, r in enumerate(rows):
        y = top + rh * i
        ok = r["กันชน"] >= night
        out.append(text(16, y + bh / 2 + 4, f"ทุน {B.fmt(r['ทุน'])}{who.get(r['ทุน'], '')}", 12, C["ink"], weight=700))
        cb = C["green"] if ok else C["red"]
        out.append(f'<rect x="{L1}" y="{y:.1f}" width="{X1(r["กันชน"]) - L1:.1f}" height="{bh}" rx="3" fill="{cb}"/>')
        lx = X1(r["กันชน"]) + 6 if ok else xn + 6               # ป้ายของแท่งที่ไม่ถึงเส้น วางขวาเส้น ไม่ให้เส้นพาด
        out.append(text(lx, y + bh / 2 + 4, f"{B.fmt(r['กันชน'])}%" + ("" if ok else " · ไม่รอด"), 11.5, cb, "start", 700))
        xe = X2(r["ส่วนเกินเปอร์เซ็นต์"])
        fill = (f'fill="{C["blue"]}"' if ok else f'fill="{C["blue"]}" fill-opacity=".18" stroke="{C["blue"]}" stroke-dasharray="4 3"')
        out.append(f'<rect x="{L2}" y="{y:.1f}" width="{xe - L2:.1f}" height="{bh}" rx="3" {fill}/>')
        lab = f"{B.fmt(r['ส่วนเกินเปอร์เซ็นต์'])}%" + ("" if ok else " บนกระดาษ")
        out.append(text(xe + 6, y + bh / 2 + 4, lab, 11.5, C["blue"] if ok else C["muted"], "start", 700))
        out.append(text(16, y + bh + 14, f"Free Cash {B.fmt(r['เงินสดอิสระ'])}", 10.5, C["grey"]))
        out.append(text(L2 + 4, y + bh + 14, f"หักค่าเสียโอกาส {B.fmt(r['ค่าเสียโอกาสต่อปี'])} ต่อปี", 10.5, C["grey"]))
    alt = ("แท่งนอนสองแผงของทุนสามขนาด " + " · ".join(
        f"ทุน {r['ทุน']} กันชน {r['กันชน']}% ส่วนเกิน {r['ส่วนเกินเปอร์เซ็นต์']}%" for r in rows) +
        f" เส้นคืนวันที่ 9 อยู่ที่ {night}% กันชนของทุน 120,000 ไม่ถึงเส้นนี้")
    btc = fig["บัญชีมิน"]["BTC"]
    cap = (f"เปิดชุดเดียวกันทุกแถว (spot 1 BTC · short futures 1 BTC · basis {B.fmt(btc['basis'])} · "
           f"{btc['วันถึงหมดอายุ']} วัน) · hurdle {B.fmt(fig['บัญชีมิน']['hurdle'])}% · แต่ละแถวเป็นคนละทุน")
    return wrap(W, H, alt, out, cap, "สอน")
