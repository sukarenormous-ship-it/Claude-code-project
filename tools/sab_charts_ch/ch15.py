"""บท 15 — อ่านผลที่ขาดทุนให้เป็น · สเปกกราฟของบท

sab-pnl-bridge (★): เจ็ดค่า 12 → 8 → 6.5 → 5 → 5 → 3 → 2 (ch15.v2.สะพาน) เป็นแท่งเต็ม · ส่วนที่หายจากแท่งก่อนเป็นกล่องผี
                   ชั้นแรก (8 − 12 = −4) สีอำพันประ = คาดพลาด ไม่ใช่เงินที่จ่าย · ชั้นที่เหลือสีแดง = เงินที่ไปถึงคนอื่น
                   Slippage ของกระดาษ = 0 วาดเป็นเส้นประ
sab-outcome-spread (v2): สามผลบนเส้นจำนวน + แถบ ±1 SD + ส่วนแบ่งความแปรปรวน (ไม้ชนงบเป็นเจ้าของก้อนใหญ่)
sab-trades-needed (v2): แถบโชค 0 ± สองเท่าของการแกว่งของค่าเฉลี่ย ทีละจำนวนไม้ เทียบเส้น 5.95 · จุด −2 ของมิน
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


@chart("sab-outcome-spread")
def _outcome_spread(fig):
    """ผลต่อไม้มีสามแบบบนเส้นจำนวน (วงกลมใหญ่ตามสัดส่วน) · เส้นม่วง = ค่าเฉลี่ย 5.95 · แถบ ±1 SD
    แถวล่าง: แท่งซ้อนว่าแต่ละแบบให้ความแปรปรวนเท่าไร (49.14 / 6.13 / 117.18 จาก 172.45) — ไม้ชนงบเป็นเจ้าของก้อนใหญ่"""
    v2 = fig["ch15"]["v2"]
    outs = v2["สามตอนจบ"]                       # [15, 1, -22]
    mix = v2["จำนวนรอบ"][0]["สัดส่วน"]           # [60, 25, 15]
    sd = v2["sdมือ"]
    ev = v2["จำนวนรอบ"][0]["ค่าคาดหมาย"]
    names = ["ถึงเส้นออก", "ครบเวลา", "ชนงบ"]
    cols = [C["green"], C["green"], C["red"]]
    W, H = 760, 330
    L, R = 70, 40
    lo, hi = min(outs) - 6, max(outs) + 8
    X = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)  # noqa: E731
    out = [text(16, 24, f"ผลต่อไม้มีแค่สามแบบ แต่แบบที่ไกลค่าเฉลี่ยที่สุดคุมการแกว่ง {B.fmt(sd['sd'])}", 13.5, C["ink"], weight=700)]
    # แถวบน: เส้นจำนวน
    y = 120
    out.append(f'<rect x="{X(sd["แถบล่าง"]):.1f}" y="{y - 46}" width="{X(sd["แถบบน"]) - X(sd["แถบล่าง"]):.1f}" height="92" '
               f'fill="#ede9fe" fill-opacity=".7"/>')
    out.append(text((X(sd["แถบล่าง"]) + X(sd["แถบบน"])) / 2, y - 52, f"แถบ ±1 SD: {B.fmt(sd['แถบล่าง'])} ถึง {B.fmt(sd['แถบบน'])} "
                    f"(ไม้ {sd['ในแถบเปอร์เซ็นต์']}% อยู่ข้างใน)", 11, C["purple"], "middle", 700))
    out.append(f'<line x1="{L}" y1="{y}" x2="{W - R}" y2="{y}" stroke="{C["axis"]}" stroke-width="1.5"/>')
    for t in range(-20, 21, 10):
        out.append(f'<line x1="{X(t):.1f}" y1="{y - 4}" x2="{X(t):.1f}" y2="{y + 4}" stroke="{C["axis"]}"/>')
        out.append(text(X(t), y + 62, B.fmt(t), 10.5, C["grey"], "middle"))
    out.append(f'<line x1="{X(ev):.1f}" y1="{y - 46}" x2="{X(ev):.1f}" y2="{y + 46}" stroke="{C["purple"]}" stroke-width="2.2"/>')
    out.append(text(X(ev) + 6, y + 42, f"ค่าเฉลี่ย {B.fmt(ev)}", 11, C["purple"], "start", 700))
    for v, p, nm, col in zip(outs, mix, names, cols):
        r = 6 + 16 * (p / 60) ** 0.5
        out.append(f'<circle cx="{X(v):.1f}" cy="{y}" r="{r:.1f}" fill="{col}" fill-opacity=".85"/>')
        out.append(text(X(v), y - r - 6, f"{nm} {'+' if v > 0 else ''}{B.fmt(v)} · {p}%", 11, C["ink"], "middle", 700))
    # ระยะจากค่าเฉลี่ยของไม้ชนงบ
    yd = y + 30
    out.append(f'<line x1="{X(outs[2]):.1f}" y1="{yd}" x2="{X(ev):.1f}" y2="{yd}" stroke="{C["red"]}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    out.append(text((X(outs[2]) + X(ev)) / 2, yd - 4, f"ห่าง {B.fmt(abs(sd['ระยะ'][2]))}", 10.5, C["red"], "middle", 700))
    # แถวล่าง: ส่วนแบ่งความแปรปรวน
    yb, bh = 238, 30
    tot = sd["รวม"]
    BX = lambda v: L + v / tot * (W - L - R)  # noqa: E731
    out.append(text(L, yb - 10, f"แต่ละแบบให้ความแปรปรวนเท่าไร (รวม {B.fmt(tot)} ถอดรากได้ {B.fmt(sd['sd'])})", 11.5, C["muted"], weight=700))
    acc = 0
    shades = ["#4ade80", "#86efac", C["red"]]
    for v, nm, sh in zip(sd["ถ่วง"], names, shades):
        x0, x1 = BX(acc), BX(acc + v)
        out.append(f'<rect x="{x0:.1f}" y="{yb}" width="{x1 - x0:.1f}" height="{bh}" fill="{sh}" stroke="#fff" stroke-width="1.5"/>')
        if x1 - x0 > 70:
            out.append(text((x0 + x1) / 2, yb + 20, f"{nm} {B.fmt(v)}", 11.5, "#ffffff" if sh == C["red"] else C["ink"], "middle", 700))
        else:
            out.append(text((x0 + x1) / 2, yb + bh + 16, f"{nm} {B.fmt(v)}", 10.5, C["muted"], "middle"))
        acc += v
    alt = (f"เส้นจำนวน ผลสามแบบ +15 ร้อยละ 60 +1 ร้อยละ 25 −22 ร้อยละ 15 ค่าเฉลี่ย {B.fmt(ev)} แถบหนึ่ง SD จาก "
           f"{B.fmt(sd['แถบล่าง'])} ถึง {B.fmt(sd['แถบบน'])} มี −22 อยู่นอกแถบ แถวล่างแท่งซ้อนส่วนของความแปรปรวน "
           f"{' · '.join(B.fmt(v) for v in sd['ถ่วง'])} รวม {B.fmt(tot)}")
    cap = f"ส่วนผสมซ้อม {'/'.join(str(p) for p in mix)} ของบท 12 (ตั้งขึ้นเอง) · ขนาดวงกลมตามสัดส่วนไม้"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-trades-needed")
def _trades_needed(fig):
    """ไม้บรรทัดของโชค: ทุกแถวคือจำนวนไม้ · แถบเทา = 0 ± สองเท่าของการแกว่งของค่าเฉลี่ย (ที่โชคพาการ์ดไม่มีกำไรไปได้)
    เส้นม่วงตั้ง = 5.95 (ค่าเฉลี่ยถ้าโลกซ้อมจริง) · แถบที่ 5.95 อยู่นอกขอบเปลี่ยนเป็นเขียว (พอ) · แถว 3 ไม้มีจุด −2 ของมิน"""
    v2 = fig["ch15"]["v2"]
    lad = v2["บันไดแกว่งมือ"]
    ev = lad["ค่าคาดหมาย"]
    mine = v2["สมุดไม้"]["เฉลี่ย"]
    rows = lad["แถว"]
    W = 760
    L, R, T, rh = 150, 150, 70, 38
    H = T + rh * len(rows) + 50
    lim = max(r["สองเท่า"] for r in rows) + 3
    X = lambda v: L + (v + lim) / (2 * lim) * (W - L - R)  # noqa: E731
    out = [text(16, 24, f"ยิ่งเห็นไม้มาก แถบโชคยิ่งแคบ จนค่าเฉลี่ย {B.fmt(ev)} หลุดขอบที่ {lad['ไม้ที่ต้องมี']} ไม้", 13.5, C["ink"], weight=700)]
    ybot = T + rh * len(rows) - 8
    for t in (-15, -10, -5, 0, 5, 10, 15):
        out.append(f'<line x1="{X(t):.1f}" y1="{T - 14}" x2="{X(t):.1f}" y2="{ybot}" stroke="{C["axis"] if t == 0 else C["grid"]}"/>')
        out.append(text(X(t), ybot + 16, B.fmt(t), 10.5, C["grey"], "middle"))
    out.append(text((X(-lim) + X(lim)) / 2, ybot + 34, "ค่าเฉลี่ยต่อไม้", 11, C["muted"], "middle"))
    out.append(text(L - 12, T - 22, "จำนวนไม้", 11, C["muted"], "end", 700))
    out.append(text(W - R + 12, T - 22, "แถบโชค (0 ± สองเท่า)", 11, C["muted"], "start", 700))
    for i, r in enumerate(rows):
        y = T + i * rh + rh / 2 - 4
        ok = r["ผ่าน"]
        col = C["green"] if ok else C["grey"]
        lab = f"{r['ไม้']} ไม้" + (" (มิน)" if i == 0 else "")
        out.append(text(L - 12, y + 4, lab, 11.5, C["ink"], "end", 700 if r["ไม้"] in (lad["ไม้ที่ต้องมี"],) or i == 0 else None))
        out.append(f'<rect x="{X(-r["สองเท่า"]):.1f}" y="{y - 9}" width="{X(r["สองเท่า"]) - X(-r["สองเท่า"]):.1f}" height="18" rx="4" '
                   f'fill="{col}" fill-opacity="{.28 if ok else .35}"/>')
        out.append(text(W - R + 12, y + 4, f"±{B.fmt(r['สองเท่า'])} · {'พอ' if ok else 'ยังไม่พอ'}", 11.5,
                        C["green"] if ok else C["muted"], "start", 700 if ok else None))
        if i == 0:
            out.append(f'<circle cx="{X(mine):.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="{C["ink"]}" stroke-width="2"/>')
            out.append(text(X(mine), y - 12, f"มินได้ {B.fmt(mine)}", 10.5, C["ink"], "middle", 700))
    out.append(f'<line x1="{X(ev):.1f}" y1="{T - 14}" x2="{X(ev):.1f}" y2="{ybot}" stroke="{C["purple"]}" stroke-width="2" stroke-dasharray="5 4"/>')
    out.append(text(X(ev) + 6, T - 18, f"{B.fmt(ev)} ถ้าโลกซ้อมจริง", 11, C["purple"], "start", 700))
    alt = (f"หกแถว จำนวนไม้ {', '.join(str(r['ไม้']) for r in rows)} แถบรอบศูนย์กว้าง ±"
           f"{', ±'.join(B.fmt(r['สองเท่า']) for r in rows)} เส้นตั้ง {B.fmt(ev)} อยู่ในแถบจนถึง 19 ไม้ "
           f"และอยู่นอกแถบตั้งแต่ 20 ไม้ แถว 3 ไม้มีจุดค่าเฉลี่ยของมิน {B.fmt(mine)} อยู่ในแถบ")
    cap = f"การ์ดในส่วนผสมซ้อม · การแกว่งต่อไม้ {B.fmt(lad['sd'])} · แถบ = 0 ± 2 × {B.fmt(lad['sd'])} ÷ รากที่สองของจำนวนไม้"
    return wrap(W, H, alt, out, cap, "สอน")
