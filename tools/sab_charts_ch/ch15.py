"""บท 15 — อ่านผลที่ขาดทุนให้เป็น · สเปกกราฟของบท

sab-pnl-bridge (★): ห้าค่า 12 → 8 → 5 → 3 → 2 เป็นแท่งเต็ม · ส่วนที่หายจากแท่งก่อนเป็นกล่องผี
                   ชั้นแรก (8 − 12 = −4) สีอำพันประ = คาดพลาด ไม่ใช่เงินที่จ่าย · ชั้นที่เหลือสีแดง = เงินที่หายจริง
sab-tries-luck (☆): ยังไม่ทำ (บทพูดตัวเลข 40.1 / 92.3% ในร้อยแก้ว)
"""
from sab_charts import chart, wrap, text, Frame, nice_ticks, C, B


def _sign(v):
    return ("+" if v > 0 else "−" if v < 0 else "") + B.fmt(abs(v))


@chart("sab-pnl-bridge")
def _pnl_bridge(fig):
    s = fig["ch15"]["สะพาน"]
    levels = [s["คาด"], s["ราคาจริง"], s["ราคาที่ซื้อขายได้"], s["หลังค่าธรรมเนียม"], s["หลังค่าถือ"]]
    deltas = [None, s["คาดพลาด"], s["ผลของราคาfill"], s["ค่าธรรมเนียม"], s["ค่าใช้จ่ายระหว่างถือ"]]
    names = ["ค่าที่คาดไว้", "ราคาจริง", "ราคาที่ซื้อขายได้", "หลังค่าธรรมเนียม", "หลังค่าถือ"]
    dnames = [None, "คาดพลาด", "ราคาเข้า", "ค่าธรรมเนียม", "ค่าถือ"]
    W, H = 760, 300
    f = Frame(0, max(levels), W, H, T=70, Bm=262)
    out = f.grid(nice_ticks(0, max(levels)))
    gw = (W - f.L - f.R) / len(levels)
    bw = min(78, gw * 0.56)
    for i, v in enumerate(levels):
        cx = f.L + gw * i + gw / 2
        x0 = cx - bw / 2
        col = C["grey"] if i == 0 else C["purple"] if i == len(levels) - 1 else C["blue"]
        out.append(f'<rect x="{x0:.1f}" y="{f.y(v):.1f}" width="{bw:.1f}" height="{f.y(0) - f.y(v):.1f}" rx="3" fill="{col}"/>')
        out.append(text(cx, f.y(v) + 18, B.fmt(v), 14, "#fff", "middle", 700))
        if i:
            prev = levels[i - 1]
            gap = i == 1
            stroke = C["amber"] if gap else C["red"]
            fill = "#fef3c7" if gap else "#fee2e2"
            dash = ' stroke-dasharray="5 4"' if gap else ""
            out.append(f'<rect x="{x0:.1f}" y="{f.y(prev):.1f}" width="{bw:.1f}" height="{f.y(v) - f.y(prev):.1f}" '
                       f'rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{dash}/>')
            out.append(text(cx, f.y(prev) - 8, f"{_sign(deltas[i])} {dnames[i]}", 12, stroke, "middle", 700))
            out.append(f'<line x1="{x0 - (gw - bw):.1f}" y1="{f.y(prev):.1f}" x2="{x0:.1f}" y2="{f.y(prev):.1f}" '
                       f'stroke="{C["axis"]}" stroke-dasharray="3 3"/>')
        out.append(text(cx, f.Bm + 20, names[i], 11.5, C["ink"] if i in (0, 4) else C["muted"], "middle", 700 if i in (0, 4) else None))
    out.append(text(16, 26, f"คาด {B.fmt(levels[0])} เหลือ {B.fmt(levels[-1])}", 14, C["ink"], weight=700))
    # คำอธิบายสีสั้น ๆ
    lx = W - 330
    out.append(f'<rect x="{lx}" y="16" width="12" height="12" rx="2" fill="#fef3c7" stroke="{C["amber"]}" stroke-dasharray="3 2"/>')
    out.append(text(lx + 18, 26, "คาดพลาด ไม่มีใครได้ไป", 11.5, C["amber"]))
    out.append(f'<rect x="{lx + 160}" y="16" width="12" height="12" rx="2" fill="#fee2e2" stroke="{C["red"]}"/>')
    out.append(text(lx + 178, 26, "เงินที่ไปถึงคนอื่น", 11.5, C["red"]))
    alt = (f"ห้าแท่ง {' · '.join(f'{n} {B.fmt(v)}' for n, v in zip(names, levels))} · ส่วนที่หาย "
           f"คาดพลาด {_sign(deltas[1])} ราคาเข้า {_sign(deltas[2])} ค่าธรรมเนียม {_sign(deltas[3])} ค่าถือ {_sign(deltas[4])}")
    cap = (f"long A 10 · short B 20 · ไม้ซ้อมหนึ่งไม้ · อำพันประ = คาดพลาด ไม่มีใครได้ไป · "
           f"แดง = เงินที่ไปถึงคนอื่น รวม {B.fmt(-(deltas[2] + deltas[3] + deltas[4]))} · เป็นการกระทบยอด ไม่ใช่การพิสูจน์สาเหตุ")
    return wrap(W, H, alt, out, cap, "สอน")
