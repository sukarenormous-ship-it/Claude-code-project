"""บท 15 — อ่านผลที่ขาดทุนให้เป็น · สเปกกราฟของบท

sab-pnl-bridge (★): เจ็ดค่า 12 → 8 → 6.5 → 5 → 5 → 3 → 2 (ch15.v2.สะพาน) เป็นแท่งเต็ม · ส่วนที่หายจากแท่งก่อนเป็นกล่องผี
                   ชั้นแรก (8 − 12 = −4) สีอำพันประ = คาดพลาด ไม่ใช่เงินที่จ่าย · ชั้นที่เหลือสีแดง = เงินที่ไปถึงคนอื่น
                   Slippage ของกระดาษ = 0 วาดเป็นเส้นประ
sab-tries-luck (☆): ยังไม่ทำ (บทพูดตัวเลข 40.1 / 92.3% ในร้อยแก้ว)
"""
from sab_charts import chart, wrap, text, Frame, nice_ticks, C, B


def _sign(v):
    return ("+" if v > 0 else "−" if v < 0 else "") + B.fmt(abs(v))


@chart("sab-pnl-bridge")
def _pnl_bridge(fig):
    """สะพานผล v2 (การ์ด → แอป): เจ็ดแท่ง · ชั้นแรกคาดพลาด (อำพันประ ไม่มีใครได้ไป) · ชั้นที่เหลือแดง = เงินที่ไปถึงคนอื่น
    Slippage ของไม้กระดาษเป็นศูนย์ จึงวาดเป็นเส้นประบนยอดแท่งก่อน"""
    s = fig["ch15"]["v2"]["สะพาน"]
    levels = s["ชั้น"]
    deltas = [None, s["คาดพลาด"], s["ส่วนต่างเข้ารวม"], s["ส่วนต่างออกรวม"], s["slippage"], s["ค่าธรรมเนียม"], s["ค่าถือ"]]
    names = [("ค่าที่คาดไว้", "(การ์ด)"), ("ผลที่", "ราคากลาง"), ("หลัง bid/ask", "ตอนเข้า"), ("หลัง bid/ask", "ตอนออก"),
             ("หลัง", "Slippage"), ("หลัง", "ค่าธรรมเนียม"), ("ในบัญชี", "(หลังค่าถือ)")]
    dnames = [None, "คาดพลาด", "bid/ask เข้า", "bid/ask ออก", "กระดาษ = 0", "ค่าธรรมเนียม", "ค่าถือ"]
    W, H = 760, 320
    f = Frame(0, max(levels), W, H, T=78, Bm=262)
    out = f.grid(nice_ticks(0, max(levels))[::2])
    n = len(levels)
    gw = (W - f.L - f.R) / n
    bw = min(64, gw * 0.62)
    last = n - 1
    for i, v in enumerate(levels):
        cx = f.L + gw * i + gw / 2
        x0 = cx - bw / 2
        col = C["grey"] if i == 0 else C["purple"] if i == last else C["blue"]
        out.append(f'<rect x="{x0:.1f}" y="{f.y(v):.1f}" width="{bw:.1f}" height="{f.y(0) - f.y(v):.1f}" rx="3" fill="{col}"/>')
        out.append(text(cx, f.y(v) + 17, B.fmt(v), 13, "#fff", "middle", 700))
        if i:
            prev = levels[i - 1]
            gap = i == 1
            stroke = C["amber"] if gap else C["muted"] if deltas[i] == 0 else C["red"]
            if deltas[i] == 0:
                out.append(f'<line x1="{x0:.1f}" y1="{f.y(prev) - 3:.1f}" x2="{x0 + bw:.1f}" y2="{f.y(prev) - 3:.1f}" '
                           f'stroke="{stroke}" stroke-width="1.4" stroke-dasharray="4 3"/>')
                top = f.y(prev) - 3
            else:
                fill = "#fef3c7" if gap else "#fee2e2"
                dash = ' stroke-dasharray="5 4"' if gap else ""
                out.append(f'<rect x="{x0:.1f}" y="{f.y(prev):.1f}" width="{bw:.1f}" height="{f.y(v) - f.y(prev):.1f}" '
                           f'rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{dash}/>')
                top = f.y(prev)
            out.append(text(cx, top - 8, _sign(deltas[i]) if deltas[i] else "0", 12.5, stroke, "middle", 700))
            out.append(text(cx, top - 23, dnames[i], 10.5, stroke, "middle"))
            out.append(f'<line x1="{x0 - (gw - bw):.1f}" y1="{f.y(prev):.1f}" x2="{x0:.1f}" y2="{f.y(prev):.1f}" '
                       f'stroke="{C["axis"]}" stroke-dasharray="3 3"/>')
        strong = i in (0, last)
        for k, line in enumerate(names[i]):
            out.append(text(cx, f.Bm + 18 + 14 * k, line, 11, C["ink"] if strong else C["muted"], "middle", 700 if strong else None))
    out.append(text(16, 24, f"คาด {B.fmt(levels[0])} เหลือ {B.fmt(levels[-1])} ในบัญชี", 14, C["ink"], weight=700))
    lx = W - 330
    out.append(f'<rect x="{lx}" y="14" width="12" height="12" rx="2" fill="#fef3c7" stroke="{C["amber"]}" stroke-dasharray="3 2"/>')
    out.append(text(lx + 18, 24, "คาดพลาด ไม่มีใครได้ไป", 11.5, C["amber"]))
    out.append(f'<rect x="{lx + 160}" y="14" width="12" height="12" rx="2" fill="#fee2e2" stroke="{C["red"]}"/>')
    out.append(text(lx + 178, 24, "เงินที่ไปถึงคนอื่น", 11.5, C["red"]))
    alt = (f"เจ็ดแท่ง {' · '.join(f'{a} {b} {B.fmt(v)}' for (a, b), v in zip(names, levels))} · ส่วนที่หาย "
           f"คาดพลาด {_sign(deltas[1])} ข้าม bid/ask ตอนเข้า {_sign(deltas[2])} ตอนออก {_sign(deltas[3])} "
           f"Slippage 0 ค่าธรรมเนียม {_sign(deltas[5])} ค่าถือ {_sign(deltas[6])}")
    cap = f"ไม้ซ้อม long A 10 · short B 20 บนกระดาษ · ส่วนแดงรวม {B.fmt(s['ไปถึงคนอื่น'])}"
    return wrap(W, H, alt, out, cap, "สอน")
