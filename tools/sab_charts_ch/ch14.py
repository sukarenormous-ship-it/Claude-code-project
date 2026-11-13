"""บท 14 — −21 แล้วสัญญาณกลับมาที่ 3.8 · สเปกกราฟของบท

sab-pause-timeline (★): เส้น X ของไม้ 3 + แถบโหมด ACTIVE/PAUSED + จุดเข้าที่ถูกบล็อก (3.8 · 2.4)
    และสองโลกของไม้ที่ถูกบล็อก (เชือกอยู่ +13 · เชือกขาด −21) — ราคาของการพักสองด้าน
sab-moving-mean (★): สามช่อง X คงที่ 10 กับค่ากลางที่เลื่อน 0 → 8 → 10 · ระยะห่าง 10 → 2 → 0 ·
    กำไรในบัญชี 0 (เส้นกำไรที่ภาพ 10.1 ของต้นฉบับไม่มี)
"""
from sab_charts import chart, wrap, text, C, B


def sg(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-pause-timeline")
def _pause_timeline(fig):
    c, acct = fig["ch14"], fig["บัญชีมิน"]
    xs = c["เส้นทาง"]
    card = acct["การ์ด"]
    t3, w = c["ไม้3"], c["ถ้าเข้า38"]
    W, H, L, R, T, Bm = 760, 350, 64, 72, 92, 300
    lo, hi = -0.5, max(w["เชือกขาด"]["ออก"], max(xs)) + 0.4
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    gx = (W - L - R) / (len(xs) - 1)
    X = lambda i: L + gx * i  # noqa: E731
    out = [text(L - 40, 26, f"ไม้ 3 ปิด {B.fmt(t3['สุทธิ'])} แล้วพัก: สัญญาณที่กลับมาถูกบล็อก",
                13, C["ink"], weight=700)]
    # แถบโหมด
    i_exit = c["เหตุการณ์"].index("exit")
    out.append(f'<rect x="{X(0) - 20:.1f}" y="42" width="{X(i_exit) - X(0) + 20:.1f}" height="20" rx="4" fill="#dcfce7"/>')
    out.append(text((X(0) + X(i_exit)) / 2 - 10, 56, "ACTIVE", 11, C["green"], "middle", 700))
    out.append(f'<rect x="{X(i_exit):.1f}" y="42" width="{X(len(xs) - 1) - X(i_exit) + 20:.1f}" height="20" rx="4" fill="#e5e7eb"/>')
    out.append(text((X(i_exit) + X(len(xs) - 1)) / 2 + 10, 56, "PAUSED (พัก)", 11, C["ink"], "middle", 700))
    # ช่วงที่ถือ
    i_in = c["เหตุการณ์"].index("entry")
    out.append(f'<rect x="{X(i_in):.1f}" y="{T}" width="{X(i_exit) - X(i_in):.1f}" height="{Bm - T}" fill="#fef2f2"/>')
    out.append(text((X(i_in) + X(i_exit)) / 2, Bm - 8, "ถือ 10 ชุด", 10.5, C["red"], "middle"))
    # เส้นอ้างอิง
    for lvl, lab, col in ((card["เข้า"], f"เข้า {B.fmt(card['เข้า'])}", C["purple"]),
                          (t3["เส้นงบ"], f"งบ {B.fmt(t3['เส้นงบ'])}", C["red"]),
                          (card["ออก"], f"ออก {B.fmt(card['ออก'])}", C["grey"])):
        out.append(f'<line x1="{L}" y1="{Y(lvl):.1f}" x2="{W - R}" y2="{Y(lvl):.1f}" stroke="{col}" '
                   f'stroke-dasharray="5 4" stroke-width="1.3"/>')
        out.append(text(W - R + 6, Y(lvl) + 4, lab, 10.5, col, "start"))
    out.append(f'<line x1="{L}" y1="{Y(0):.1f}" x2="{W - R}" y2="{Y(0):.1f}" stroke="{C["axis"]}"/>')
    out.append(text(L - 8, Y(0) + 4, "X = 0", 10.5, C["grey"], "end"))
    # เส้น X จริง
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(xs))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.4" stroke-linejoin="round"/>')
    # สองโลกของไม้ที่ถูกบล็อก
    i_b = c["เหตุการณ์"].index("entry_blocked_by_pause")
    for v, lab, col in ((w["เชือกขาด"]["ออก"], f"เชือกขาด {sg(w['เชือกขาด']['สุทธิ'])}", C["red"]),):
        out.append(f'<line x1="{X(i_b):.1f}" y1="{Y(xs[i_b]):.1f}" x2="{X(i_b + 1):.1f}" y2="{Y(v):.1f}" '
                   f'stroke="{col}" stroke-width="1.8" stroke-dasharray="4 4"/>')
        out.append(f'<circle cx="{X(i_b + 1):.1f}" cy="{Y(v):.1f}" r="4" fill="none" stroke="{col}" stroke-width="1.6"/>')
        out.append(text(X(i_b + 1) - 10, Y(v) - 8, lab, 10.5, col, "end", 700))
    out.append(text((X(i_b) + X(i_b + 1)) / 2 + 6, (Y(xs[i_b]) + Y(xs[i_b + 1])) / 2 + 22, f"เชือกอยู่ {sg(w['เชือกอยู่']['สุทธิ'])}", 10.5,
                    C["green"], "middle", 700))
    # จุดสำคัญ
    for i, v in enumerate(xs):
        ev = c["เหตุการณ์"][i]
        if ev == "entry":
            out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="5.5" fill="{C["purple"]}"/>')
            out.append(text(X(i), Y(v) + 22, f"เข้า {B.fmt(v)}", 11, C["purple"], "middle", 700))
        elif ev == "hold":
            out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" fill="{C["blue"]}"/>')
            out.append(text(X(i) + 8, Y(v) + 18, B.fmt(v), 11, C["blue"], "start", 700))
        elif ev == "exit":
            out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="6" fill="{C["red"]}"/>')
            out.append(text(X(i), Y(v) - 12, f"ปิด {B.fmt(v)} · {B.fmt(t3['สุทธิ'])}", 11.5, C["red"], "middle", 700))
        elif ev == "entry_blocked_by_pause":
            out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="7" fill="#fff" stroke="{C["ink"]}" stroke-width="1.8"/>')
            out.append(f'<path d="M{X(i) - 4:.1f},{Y(v) - 4:.1f} L{X(i) + 4:.1f},{Y(v) + 4:.1f} M{X(i) + 4:.1f},{Y(v) - 4:.1f} '
                       f'L{X(i) - 4:.1f},{Y(v) + 4:.1f}" stroke="{C["ink"]}" stroke-width="1.8"/>')
            last = i == len(xs) - 1
            out.append(text(X(i) + (-12 if last else 12), Y(v) + (22 if last else 4), f"{B.fmt(v)} บล็อก", 11,
                            C["ink"], "end" if last else "start", 700))
    labels = ["ก่อนเข้า", "เข้า"] + [f"ช่วง {k}" for k in range(1, len(xs) - 1)]
    for i, lab in enumerate(labels):
        out.append(text(X(i), Bm + 18, lab, 10.5, C["grey"], "middle"))
    alt = (f"เส้น X ของไม้ 3 จาก 0 เข้าที่ {B.fmt(xs[1])} ขึ้น {B.fmt(xs[2])} กระโดด {B.fmt(xs[3])} ปิดขาดทุน "
           f"{B.fmt(t3['สุทธิ'])} แถบโหมดเปลี่ยนจาก ACTIVE เป็น PAUSED จุด {B.fmt(xs[4])} และ {B.fmt(xs[5])} ถูกบล็อก "
           f"เส้นประสองเส้นแสดงว่าถ้าเข้าที่ {B.fmt(xs[4])} อาจได้ {sg(w['เชือกอยู่']['สุทธิ'])} หรือเสีย "
           f"{B.fmt(w['เชือกขาด']['สุทธิ'])}")
    cap = (f"ไม้ 3 ของมิน 10 ชุด · X กระโดดข้ามเส้นงบ {B.fmt(t3['เส้นงบ'])} · หลังปิด {B.fmt(xs[4])} และ {B.fmt(xs[5])} "
           f"ถูกบล็อก · เส้นประแดงเป็นโลกสมมติที่ X ขยับต่อ {B.fmt(w['เชือกขาด']['ขยับ'])} ไม่ใช่ข้อมูล")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-moving-mean")
def _moving_mean(fig):
    m = fig["ch14"]["ค่ากลางเลื่อน"]
    xs, mu, gap, pnl = m["X"], m["ค่ากลาง"], m["ระยะ"], m["กำไร"]
    W, H, T, Bm = 760, 300, 78, 240
    pw, gapw = 210, 35
    out = [text(16, 26, f"ระยะหด {B.fmt(gap[0])} → {B.fmt(gap[-1])} แต่กำไร {B.fmt(pnl)}",
                13, C["ink"], weight=700)]
    hi = max(xs + mu + gap) * 1.2
    for p, (title, kind) in enumerate((("X กับค่ากลาง", "line"), ("ระยะห่าง", "bar"), ("กำไรของที่ถือ", "pnl"))):
        L = 40 + p * (pw + gapw)
        Rr = L + pw
        out.append(text(L, T - 22, title, 12, C["ink"], weight=700))
        lo_, hi_ = (0, hi) if kind != "pnl" else (-hi / 2, hi / 2)
        Y = lambda v, lo_=lo_, hi_=hi_: Bm - (v - lo_) / (hi_ - lo_) * (Bm - T)  # noqa: E731
        X = lambda i, L=L: L + 30 + i * (pw - 60) / (len(xs) - 1)  # noqa: E731
        out.append(f'<line x1="{L}" y1="{Y(0):.1f}" x2="{Rr}" y2="{Y(0):.1f}" stroke="{C["axis"]}" stroke-width="1.5"/>')
        if kind == "line":
            out.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(xs))}" fill="none" '
                       f'stroke="{C["blue"]}" stroke-width="2.4"/>')
            out.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(mu))}" fill="none" '
                       f'stroke="{C["amber"]}" stroke-width="2.2" stroke-dasharray="5 4"/>')
            for i, v in enumerate(mu):
                out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" fill="{C["amber"]}"/>')
                out.append(text(X(i) + (8 if i == 0 else 0), Y(v) + (4 if i == 0 else 18), B.fmt(v), 11, C["amber"],
                                "start" if i == 0 else "middle", 700))
            out.append(text(X(0), Y(xs[0]) - 8, f"X = {B.fmt(xs[0])}", 11, C["blue"], "start", 700))
            out.append(text(X(len(xs) - 1), Y(mu[1]) + 4 + 30, "ค่ากลาง", 10.5, C["amber"], "end"))
        elif kind == "bar":
            for i, v in enumerate(gap):
                out.append(f'<rect x="{X(i) - 18:.1f}" y="{Y(v):.1f}" width="36" height="{max(1, Y(0) - Y(v)):.1f}" rx="3" '
                           f'fill="{C["purple"]}" fill-opacity=".8"/>')
                out.append(text(X(i), Y(v) - 6, B.fmt(v), 12, C["purple"], "middle", 700))
        else:
            out.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(pnl):.1f}" for i in range(len(xs)))}" fill="none" '
                       f'stroke="{C["ink"]}" stroke-width="2.4"/>')
            for i in range(len(xs)):
                out.append(f'<circle cx="{X(i):.1f}" cy="{Y(pnl):.1f}" r="4" fill="{C["ink"]}"/>')
            out.append(f'<rect x="{L + 20}" y="{Y(pnl) - 52:.1f}" width="{pw - 40}" height="28" rx="6" fill="#f5f3ff" '
                       f'stroke="{C["purple"]}"/>')
            out.append(text(L + pw / 2, Y(pnl) - 33, f"{B.fmt(pnl)} ทุกช่วง", 12.5, C["purple"], "middle", 700))
        for i in range(len(xs)):
            out.append(text(X(i), Bm + 18, f"ช่วง {i + 1}", 10.5, C["grey"], "middle"))
    alt = (f"สามแผง แผงแรก X คงที่ {B.fmt(xs[0])} ขณะค่ากลางเลื่อน {B.fmt(mu[0])} {B.fmt(mu[1])} {B.fmt(mu[2])} "
           f"แผงสองระยะห่าง {B.fmt(gap[0])} {B.fmt(gap[1])} {B.fmt(gap[2])} แผงสามกำไรของที่ถือเป็น {B.fmt(pnl)} ทุกช่วง")
    cap = f"ระยะหดเพราะย้ายไม้บรรทัด ไม่ใช่ราคา · แผงขวาเป็นแผงเดียวที่เป็นเงิน (ภาพต้นฉบับไม่มี)"
    return wrap(W, H, alt, out, cap, "สอน")
