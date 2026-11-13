"""บท 8 — hedge แล้ว…จากอะไร · สเปกกราฟของบท

sab-beta-count : 8 วันของ BTC กับ A · วันที่ BTC ขยับไม่เกิน 2% เป็นสีเทา (ไม่นับ) · ใต้แต่ละวันบอก A ÷ BTC ของวันนั้น
                 เพื่อให้เห็นว่ารายวันแกว่ง แต่ผลรวมของวันที่นับให้ 1.5
sab-hedge-compare : สามวิธีให้ขา B (10 / 20 / 30 เหรียญ) · แท่งแดง = BTC ลง 4% · แท่งส้ม = B ขึ้นเอง 1% (stress)
"""
from sab_charts import chart, wrap, grouped_bars, text, Frame, nice_ticks, C, B


def _whole(v):
    """30.0 → "30" (ผลรวมที่เป็นจำนวนเต็มไม่ต้องมีทศนิยม)"""
    t = B.fmt(v)
    return t[:-2] if t.endswith(".0") else t


def _signed(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-beta-count")
def _beta_count(fig):
    nb = fig["ch08"]["นับbeta"]
    days, cut = nb["วัน"], nb["เกณฑ์เปอร์เซ็นต์"]
    W, H = 760, 372
    vals = [d[k] for d in days for k in ("BTC", "A")]
    f = Frame(min(vals), max(vals), W, H, T=112, Bm=290, pad=0.1)
    out = f.grid(nice_ticks(min(vals), max(vals)), "%")
    for lvl in (cut, -cut):
        y = f.y(lvl)
        out.append(f'<line x1="{f.L}" y1="{y:.1f}" x2="{W - f.R}" y2="{y:.1f}" stroke="{C["grey"]}" '
                   f'stroke-dasharray="4 4" stroke-width="1"/>')
    out.append(text(W - f.R, f.y(cut) - 5, f"เกณฑ์ BTC ±{cut}%", 10.5, C["grey"], "end"))
    gw = (W - f.L - f.R) / len(days)
    bw = 26
    for i, d in enumerate(days):
        cx = f.L + gw * i + gw / 2
        for j, (k, col) in enumerate((("BTC", C["blue"]), ("A", C["amber"]))):
            v = d[k]
            colr = col if d["นับ"] else "#d1d5db"
            x = cx - bw - 2 + j * (bw + 4)
            y0, y1 = f.y(0), f.y(v)
            out.append(f'<rect x="{x:.1f}" y="{min(y0, y1):.1f}" width="{bw}" height="{max(1.5, abs(y1 - y0)):.1f}" '
                       f'rx="2" fill="{colr}"/>')
            out.append(text(x + bw / 2, (y1 - 5) if v >= 0 else (y1 + 13), _signed(v), 10,
                            C["ink"] if d["นับ"] else C["grey"], "middle", 700 if d["นับ"] else None))
        out.append(text(cx, f.Bm + 18, f"วัน {i + 1}", 11, C["ink"], "middle", 700))
        if d["นับ"]:
            out.append(text(cx, f.Bm + 34, f"A÷BTC {B.fmt(d['Aต่อBTC'])}", 10.5, C["muted"], "middle"))
        else:
            out.append(text(cx, f.Bm + 34, "ไม่นับ", 10.5, C["grey"], "middle"))
    last = f.L + gw * (len(days) - 1) + gw / 2
    out.append(text(last, f.Bm + 50, "คืนในฉาก", 10.5, C["purple"], "middle", 700))
    # หัว + legend + สรุปสีม่วง
    out.append(text(f.L, 26, f"นับ beta จากวันที่ BTC ขยับเกิน {cut}%", 13, C["ink"], weight=700))
    lx = f.L
    for name, col in (("BTC", C["blue"]), ("A", C["amber"]), ("ไม่นับ", "#d1d5db")):
        out.append(f'<rect x="{lx}" y="{40}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, 50, name, 11.5, C["muted"]))
        lx += 34 + 8 * len(name)
    sA, sB = _whole(nb['ผลรวมA']), _whole(nb['ผลรวมBTC'])
    out.append(text(f.L, 80, f"{nb['วันที่นับ']} วันที่นับ (ทุกวัน A ไปทางเดียวกับ BTC จึงจดบวก): "
                             f"A รวม {sA} ÷ BTC รวม {sB} = {B.fmt(nb['ผล'])}", 12.5, C["purple"], weight=700))
    alt = (f"กราฟแท่ง 8 วัน แท่งน้ำเงินคือการขยับของ BTC แท่งส้มคือการขยับของ A เป็นเปอร์เซ็นต์ "
           f"วันที่ BTC ขยับไม่เกิน {cut}% เป็นสีเทาและไม่นับ วันที่นับ {nb['วันที่นับ']} วัน A ขยับรวม {sA} "
           f"BTC ขยับรวม {sB} ได้ beta {B.fmt(nb['ผล'])}")
    cap = (f"รายวัน A ÷ BTC แกว่งตั้งแต่ {B.fmt(min(d['Aต่อBTC'] for d in days if d['นับ']))} ถึง "
           f"{B.fmt(max(d['Aต่อBTC'] for d in days if d['นับ']))} แต่ผลรวมให้ {B.fmt(nb['ผล'])} · "
           f"วันลงนับแยกได้ {B.fmt(nb['วันลง']['ผล'])} วันขึ้นได้ {B.fmt(nb['วันขึ้น']['ผล'])}")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-hedge-compare")
def _hedge_compare(fig):
    c = fig["ch08"]
    m = c["สามวิธี"]
    st = c["stress_B1%"]
    gross = c["grossสามวิธี"]
    keys = ("จำนวนเท่ากัน", "มูลค่าเท่ากัน", "betaneutral")
    sub = {"จำนวนเท่ากัน": "จำนวนเท่า A", "มูลค่าเท่ากัน": "มูลค่าเท่า A", "betaneutral": "เป็นกลางต่อตลาด"}
    cats = [f"B {m[k]['จำนวนB']} เหรียญ" for k in keys]
    s1 = [m[k]["BTCลง4"] for k in keys]
    s2 = [st["ขา500"], st["ขา1000"], st["ขา1500"]]
    W, H = 760, 330
    parts = grouped_bars(cats, [("BTC ลง 4% (B ลงตามตลาด)", s1, C["red"]),
                                ("B ขึ้นเอง 1% (ตลาดนิ่ง)", s2, C["amber"])],
                         "ขา B ยิ่งใหญ่ ยิ่งกันตลาดได้มาก แต่ยิ่งรับข่าวของ B เองมาก", W=W, H=H)
    f = Frame(min(s1 + s2 + [0]), 0, W, H, T=70)
    gw = (W - f.L - f.R) / len(keys)
    for i, k in enumerate(keys):
        cx = f.L + gw * i + gw / 2
        parts.append(text(cx, f.Bm + 34, sub[k], 11, C["ink"], "middle", 700))
        parts.append(text(cx, f.Bm + 50, f"สองขารวม {B.fmt(gross[k])}", 10.5, C["muted"], "middle"))
    # callout ที่แท่งส้มของแถว 30 เหรียญ
    bw = min(46, (gw - 24) / 2)
    cx = f.L + gw * 2 + gw / 2
    x = cx - 2 * (bw + 4) / 2 + (bw + 4) + bw / 2
    y = (f.y(0) + f.y(s2[2])) / 2
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#fff" stroke="{C["purple"]}" stroke-width="2.2"/>')
    ty = f.y(s1[1]) + 40                          # ใต้ป้าย −20 ของแถว 20 เหรียญ ไม่ทับแท่ง
    parts.append(f'<path d="M{x - 4:.1f},{y + 4:.1f} C{x - 20:.1f},{ty - 4:.1f} {x - 60:.1f},{ty - 4:.1f} {x - 100:.1f},{ty - 4:.1f}" '
                 f'fill="none" stroke="{C["purple"]}" stroke-width="1.2"/>')
    parts.append(text(x - 104, ty, "ขา hedge ใหญ่สุด รับข่าวของ B มากสุด", 11, C["purple"], "end", 700))
    alt = (f"กราฟแท่งสามกลุ่ม ขา B 10 20 30 เหรียญ เมื่อ BTC ลง 4% เสีย {B.fmt(s1[0])} {B.fmt(s1[1])} {B.fmt(s1[2])} "
           f"เมื่อ B ขึ้นเอง 1% เสีย {B.fmt(s2[0])} {B.fmt(s2[1])} {B.fmt(s2[2])}")
    cap = (f"ถือ A {B.fmt(c['ฉาก']['Aจำนวน'])} เหรียญ ({B.fmt(c['ฉาก']['Aมูลค่า'])}) beta {B.fmt(c['ฉาก']['betaA'])} · "
           f"B ราคา {B.fmt(fig['บัญชีมิน']['คู่']['B'])} beta {B.fmt(fig['บัญชีมิน']['beta']['B'])} · "
           "แท่งแดงคิดเฉพาะผลของตลาด แท่งส้มคิดเฉพาะการขยับของ B เอง")
    return wrap(W, H, alt, parts, cap, "สอน")
