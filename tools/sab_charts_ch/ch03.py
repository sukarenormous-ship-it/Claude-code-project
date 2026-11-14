"""บท 3 — สมุดบัญชีสองขา · สเปกกราฟของบท

sab-ledger-bars (★): แท่งนอนซ้อนสามแถวของ 03.09 (เริ่ม → ซื้อ spot → short futures) — ยาวเท่ากันทุกแถว (equity 125,000)
เพราะเงินแค่ย้ายช่อง · แถวที่สี่คือยอดที่มินบวกจากหน้าจอเอง (นับขนาดสัญญา futures เป็นเงิน) ยาวเกินเส้น equity
sab-basis-time (☆): เลื่อนไว้ — ร้อยแก้วกรณี 1 + ตารางสี่แถวพูดประเด็นเดียวกันแล้ว และงบคำเส้นทางหลักไม่พอ
"""
from sab_charts import chart, wrap, text, C, B


@chart("sab-ledger-bars")
def _ledger_bars(fig):
    c3, m = fig["ch03"], fig["บัญชีมิน"]
    cap = m["ทุนภาค1"]["รวม"]
    spot, margin, free = m["ทุนภาค1"]["spot"], m["ทุนภาค1"]["หลักประกัน"], m["ทุนภาค1"]["เงินสดอิสระ"]
    w = c3["จอบวกผิด"]
    seg = {"cash": ("Free Cash", C["blue"]), "spot": ("มูลค่า spot", C["grey"]),
           "margin": ("บัญชี Margin", C["amber"]), "contract": ("ขนาดสัญญา futures (ไม่ใช่เงิน)", C["red"])}
    rows = [("เริ่ม", [("cash", cap)]),
            ("ซื้อ spot 1 BTC", [("spot", spot), ("cash", cap - spot)]),
            ("short futures + วาง Margin", [("spot", spot), ("margin", margin), ("cash", free)]),
            ("ยอดที่มินบวกจากหน้าจอ", [("spot", w["spot"]), ("contract", w["ขนาดสัญญาfutures"]), ("cash", w["เงินสดอิสระ"])])]
    W, H = 760, 352
    L, R, T = 210, 30, 92
    hi = w["รวมผิด"] * 1.1                       # สเกลเท่านั้น (ไม่พิมพ์) · ป้ายแกนใช้เฉพาะค่าที่มีใน JSON
    X = lambda v: L + v / hi * (W - L - R)  # noqa: E731
    rh, gap = 30, 34
    out = []
    for t in (0, spot, w["รวมผิด"]):
        if 0 <= t <= hi:
            out.append(f'<line x1="{X(t):.1f}" y1="{T - 6}" x2="{X(t):.1f}" y2="{T + 4 * (rh + gap) - gap + 6}" '
                       f'stroke="{C["axis"] if t == 0 else C["grid"]}" stroke-width="1"/>')
            out.append(text(X(t), T + 4 * (rh + gap) - gap + 22, B.fmt(t), 10.5, C["grey"], "middle"))
    for i, (name, parts) in enumerate(rows):
        y = T + i * (rh + gap)
        out.append(text(L - 10, y + rh / 2 + 4, name, 11.5, C["ink"], "end", 700 if i == 3 else None))
        x, small = 0, 0
        for k, (key, v) in enumerate(parts):
            col = seg[key][1]
            x0, x1 = X(x), X(x + v)
            dash = ' fill-opacity=".28" stroke="#dc2626" stroke-dasharray="4 3"' if key == "contract" else ""
            out.append(f'<rect x="{x0:.1f}" y="{y}" width="{x1 - x0:.1f}" height="{rh}" fill="{col}"{dash}/>')
            lab = B.fmt(v)
            if x1 - x0 > 52:
                out.append(text((x0 + x1) / 2, y + rh / 2 + 4, lab, 11, C["red"] if key == "contract" else "#ffffff",
                                "middle", 700))
            else:                                   # ช่องแคบ: สลับป้ายบน/ล่างไม่ให้ชนกัน
                small += 1
                yy = y - 5 if small % 2 else y + rh + 13
                out.append(text((x0 + x1) / 2, yy, lab, 10.5, col, "middle", 700))
            x += v
        if i == 3:
            out.append(text(X(x) + 6, y + rh / 2 + 4, B.fmt(x), 11.5, C["red"], "start", 700))
    # เส้น equity 125,000
    xe = X(cap)
    out.append(f'<line x1="{xe:.1f}" y1="{T - 14}" x2="{xe:.1f}" y2="{T + 4 * (rh + gap) - gap + 4}" '
               f'stroke="{C["purple"]}" stroke-width="1.8" stroke-dasharray="6 4"/>')
    out.append(text(xe + 6, T - 16, f"equity {B.fmt(cap)} ทุกแถวจริง", 11.5, C["purple"], "start", 700))
    # คำอธิบายสี
    lx = 16
    for key in ("cash", "spot", "margin", "contract"):
        nm, col = seg[key]
        out.append(f'<rect x="{lx}" y="{T - 52}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 42, nm, 11, C["muted"]))
        lx += 30 + 7.2 * len(nm)
    out.append(text(16, T - 70, f"เงินแค่ย้ายช่อง ยอดรวมจึงเท่าเดิม — ยอด {B.fmt(w['รวมผิด'])} มาจากการนับสัญญาเป็นเงิน",
                    13, C["ink"], weight=700))
    alt = (f"แท่งนอนสี่แถว สามแถวแรกยาวเท่ากันที่ {B.fmt(cap)} เงินสดย้ายไปเป็นมูลค่า spot {B.fmt(spot)} "
           f"บัญชี Margin {B.fmt(margin)} และเหลือ Free Cash {B.fmt(free)} แถวสุดท้ายคือยอดที่มินบวกจากหน้าจอ "
           f"{B.fmt(w['รวมผิด'])} เพราะนับขนาดสัญญา futures {B.fmt(w['ขนาดสัญญาfutures'])} เป็นเงิน")
    cap_txt = (f"คิดที่ 1 BTC (ของมิน ÷ 100) · ยังไม่หักค่าธรรมเนียม · ยอดที่บวกผิดเกินจริง {B.fmt(w['เกินจริง'])} "
               f"= ขนาดสัญญา {B.fmt(w['ขนาดสัญญาfutures'])} − เงินจริงในบัญชี Margin {B.fmt(margin)}")
    return wrap(W, H, alt, out, cap_txt, "สอน")

