"""บท 17 — ธรรมชาติของ stat arb: ใครจ่ายเงินให้เรา · สเปกกราฟของบท

sab-shape-gallery (★): แถบผลสี่กลยุทธ์ (slip_strip × 4) · สเกลแยกต่อแถว
    carry 20 รอบ (+2,846 · เสียเงินบน exchange 25,000 ครั้งเดียว) · funding carry 90 รอบของเส้นทางกลับขั้ว ·
    คู่ A–B 20 ไม้ (60/25/15) · ให้สภาพคล่อง 20 ครั้ง (+0.2 · ได้ขาเดียว −0.4 · ร่าง)
sab-drawdown (★): สองแผง — บน: ยอดสะสม 100 ไม้ของการ์ดคู่ · ล่าง: ระยะใต้ยอดเดิม (underwater)
    callout ลึกสุด −46 และนานสุด 11 ไม้ (ช่วงเดียวกัน ไม้ 78 → 90)
"""
from sab_charts import chart, wrap, text, slip_strip, C, B


def sg(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-shape-gallery")
def _shape_gallery(fig):
    g = fig["ch17"]["แกลเลอรี"]
    r6 = fig["ch06"]["รอบชดเชย"]
    lp = fig["ch17"]["บัตร4"]
    rows = [
        ("carry", f"carry · รอบละ {sg(r6['กำไรต่อรอบ'])} · เสีย {B.fmt(-g['carry']['เสีย'])} ครั้งเดียว"),
        ("funding", f"funding carry · {g['funding']['รอบบวก']} รอบ +10 แล้วกลับขั้ว {g['funding']['รอบลบ']} รอบ"),
        ("คู่", "คู่ A–B · +16 / +2 / −21"),
        ("สภาพคล่อง", f"ให้สภาพคล่อง (ร่าง) · {sg(lp['ได้สองฝั่ง'])} / ได้ขาเดียว {B.fmt(lp['ได้ขาเดียว'])}"),
    ]
    W, h1, top = 760, 140, 34
    out = [text(16, 22, "แถบผลสี่กลยุทธ์: ได้เล็กบ่อย เสียเป็นก้อน", 14, C["ink"], weight=700)]
    for j, (k, title) in enumerate(rows):
        parts = slip_strip(g[k]["ลำดับ"], title, W=W, H=h1)
        out.append(f'<g transform="translate(0,{top + j * h1})">' + "\n".join(parts) + "</g>")
    H = top + 4 * h1 + 6
    alt = (f"สี่แถบ carry ได้รอบละ {B.fmt(r6['กำไรต่อรอบ'])} สิบเก้ารอบ เสีย {B.fmt(-g['carry']['เสีย'])} หนึ่งรอบ รวม {B.fmt(g['carry']['รวม'])} · "
           f"funding ได้ 10 ต่อรอบ {g['funding']['รอบบวก']} รอบ แล้วจ่าย 10 ต่อรอบ {g['funding']['รอบลบ']} รอบ รวม {B.fmt(g['funding']['รวม'])} · "
           f"คู่ 20 ไม้ รวม {B.fmt(g['คู่']['รวม'])} · ให้สภาพคล่อง 20 ครั้ง รวม {B.fmt(g['สภาพคล่อง']['รวม'])}")
    cap = ("สเกลแยกต่อแถว · carry คิดที่ 1 BTC เก็บ spot นอก exchange · funding = เส้นทางกลับขั้วบท 7 ก่อนค่าธรรมเนียม "
           "ไม่ใช้เกณฑ์ออก · ลำดับตรึงเพื่อสอน")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-drawdown")
def _drawdown(fig):
    c = fig["ch17"]
    eq = [0] + c["drawdown"]["กราฟ"]
    p = c["drawdownจุด"]
    ex = c["drawdown"]["ตัวอย่าง"]
    n = len(eq) - 1
    W, L, R = 760, 64, 24
    X = lambda i: L + i / n * (W - L - R)  # noqa: E731
    out = [text(16, 22, f"100 ไม้ของการ์ดคู่: ยอดขึ้นถึง {sg(ex['ผลรวม100ไม้'])} แต่ระหว่างทางต้องทน", 14, C["ink"], weight=700)]
    # แผงบน: ยอดสะสม
    T1, B1 = 48, 196
    hi = max(eq) * 1.08
    lo = min(min(eq), 0) - hi * 0.04
    Y1 = lambda v: B1 - (v - lo) / (hi - lo) * (B1 - T1)  # noqa: E731
    for gv in (0, 250, 500):
        if gv <= hi:
            out.append(f'<line x1="{L}" y1="{Y1(gv):.1f}" x2="{W - R}" y2="{Y1(gv):.1f}" stroke="{C["axis"] if gv == 0 else C["grid"]}"/>')
            out.append(text(L - 8, Y1(gv) + 4, B.fmt(gv), 10.5, C["grey"], "end"))
    out.append(f'<rect x="{X(p["ไม้ยอด"]):.1f}" y="{T1}" width="{X(p["ไม้กลับยอด"]) - X(p["ไม้ยอด"]):.1f}" '
               f'height="{B1 - T1}" fill="#fef2f2"/>')
    pts = " ".join(f"{X(i):.1f},{Y1(v):.1f}" for i, v in enumerate(eq))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["green"]}" stroke-width="2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{X(p["ไม้ยอด"]):.1f}" cy="{Y1(p["ยอด"]):.1f}" r="4" fill="{C["purple"]}"/>')
    out.append(text(X(p["ไม้ยอด"]) - 8, Y1(p["ยอด"]) - 8, f"ยอด {B.fmt(p['ยอด'])} (ไม้ {p['ไม้ยอด']})", 11, C["purple"], "end", 700))
    out.append(text(L, T1 - 6, "ยอดสะสม", 11, C["muted"]))
    # แผงล่าง: ระยะใต้ยอดเดิม
    T2, B2 = 232, 330
    peak, under = eq[0], []
    for v in eq:
        peak = max(peak, v)
        under.append(v - peak)
    dlo = min(under) * 1.25
    Y2 = lambda v: T2 + v / dlo * (B2 - T2)  # noqa: E731
    out.append(f'<line x1="{L}" y1="{T2}" x2="{W - R}" y2="{T2}" stroke="{C["axis"]}" stroke-width="1.5"/>')
    out.append(text(L - 8, T2 + 4, "0", 10.5, C["grey"], "end"))
    out.append(text(L - 8, Y2(ex["ลึกสุด"]) + 4, B.fmt(ex["ลึกสุด"]), 10.5, C["grey"], "end"))
    bw = (W - L - R) / n
    for i, v in enumerate(under):
        if v < 0:
            out.append(f'<rect x="{X(i) - bw * .4:.1f}" y="{T2}" width="{bw * .8:.1f}" height="{Y2(v) - T2:.1f}" fill="{C["red"]}"/>')
    out.append(f'<circle cx="{X(p["ไม้ต่ำสุด"]):.1f}" cy="{Y2(ex["ลึกสุด"]):.1f}" r="4" fill="{C["purple"]}"/>')
    out.append(text(X(p["ไม้ต่ำสุด"]) - 10, Y2(ex["ลึกสุด"]) + 4, f"ลึกสุด {B.fmt(ex['ลึกสุด'])}", 11.5, C["purple"], "end", 700))
    yb = B2 + 10
    out.append(f'<line x1="{X(p["ไม้ยอด"]):.1f}" y1="{yb}" x2="{X(p["ไม้กลับยอด"]):.1f}" y2="{yb}" stroke="{C["purple"]}" stroke-width="1.6"/>')
    for i in (p["ไม้ยอด"], p["ไม้กลับยอด"]):
        out.append(f'<line x1="{X(i):.1f}" y1="{yb - 4}" x2="{X(i):.1f}" y2="{yb + 4}" stroke="{C["purple"]}" stroke-width="1.6"/>')
    out.append(text(X(p["ไม้ยอด"]) - 8, yb + 4, f"นานสุด {ex['นานสุดไม้']} ไม้", 11.5, C["purple"], "end", 700))
    out.append(text(L, T2 - 6, "ห่างจากยอดเดิม", 11, C["muted"]))
    for i in (1, 50, 100):
        out.append(text(X(i), B2 + 32, f"ไม้ {i}", 10.5, C["grey"], "middle"))
    H = B2 + 44
    alt = (f"แผงบนยอดสะสมของ 100 ไม้ขึ้นถึง {B.fmt(ex['ผลรวม100ไม้'])} แผงล่างระยะห่างจากยอดเดิม "
           f"ลึกสุด {B.fmt(ex['ลึกสุด'])} จากยอด {B.fmt(p['ยอด'])} ที่ไม้ {p['ไม้ยอด']} ลงถึง {B.fmt(p['ต่ำสุด'])} ที่ไม้ {p['ไม้ต่ำสุด']} "
           f"และกลับยอดเดิมที่ไม้ {p['ไม้กลับยอด']} อยู่ใต้ยอด {ex['นานสุดไม้']} ไม้")
    cap = (f"การ์ดบท 12 · +16 / +2 / −21 สุ่มตามสัดส่วน 60/25/15 · ชนะ {ex['ไม้ชนะ']} เสีย {ex['ไม้เสีย']} ไม้ · "
           "แถบแดงอ่อน = ช่วงใต้ยอดเดิมที่นานสุด ซึ่งเป็นช่วงเดียวกับที่ลึกสุด")
    return wrap(W, H, alt, out, cap, "จำลอง")
