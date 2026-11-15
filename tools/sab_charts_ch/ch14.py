"""บท 14 — −22 แล้วสัญญาณกลับมาที่ 3.8 · สเปกกราฟของบท

sab-pause-timeline (★): เส้น X ของไม้ 3 + แถบโหมด ACTIVE/PAUSED + จุดเข้าที่ถูกบล็อก (3.8 · 2.4)
    และสองโลกของไม้ที่ถูกบล็อก (เชือกอยู่ +12 · เชือกขาด −22 · ต้นทุน 2 ของ ch14.v2) — ราคาของการพักสองด้าน
sab-moving-mean (★): สามช่อง X ค้างที่ 10 · Mean ที่เลื่อนตามด้วยความเร็ว 0.8 กับ 0.2 (ch14.v2.ไม้บรรทัดเลื่อน) ·
    ระยะห่างหดทั้งสองแบบ · กำไรจากราคา 0 ทั้งสองแบบ (v2: ให้กลไกแทนเลข 0 → 8 → 10 ที่ไม่มีที่มา)
sab-rolling-exit (★ v2): ไม้บรรทัดเฉลี่ย 4 ช่วงล่าสุดแบบที่แอปวาด · X ค้างที่ 2 · เส้นเข้า/ออกเลื่อนขึ้นมาหา X ·
    Z-score 2 → 1 → 0.5 ทั้งที่ X ไม่ขยับ (ch14.v2.ไม้บรรทัดเฉลี่ย4)
"""
from sab_charts import chart, wrap, text, C, B


def sg(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-pause-timeline")
def _pause_timeline(fig):
    c, acct = fig["ch14"], fig["บัญชีมิน"]
    xs = c["เส้นทาง"]
    card = acct["การ์ด"]
    t3, w = c["v2"]["ไม้3"], c["v2"]["ถ้าเข้า38"]
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
           f"ถ้าเข้าที่ {B.fmt(xs[4])} เส้นจริงที่ลงมา {B.fmt(xs[5])} คือโลกที่เชือกอยู่ {sg(w['เชือกอยู่']['สุทธิ'])} "
           f"เส้นประแดงคือโลกที่เชือกขาด {B.fmt(w['เชือกขาด']['สุทธิ'])}")
    cap = "short X 10 ชุด ต้นทุนไปกลับ 2 · ผลของไม้ที่ถูกบล็อกนับเหมือนปิดตอนนั้น"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-moving-mean")
def _moving_mean(fig):
    m = fig["ch14"]["v2"]["ไม้บรรทัดเลื่อน"]
    x = m["X"]
    fast = [0] + [r["Mean"] for r in m["ช่วงเร็ว"]]
    slow = [0] + [r["Mean"] for r in m["ช่วงช้า"]]
    gfast = [x] + [r["ระยะ"] for r in m["ช่วงเร็ว"]]
    gslow = [x] + [r["ระยะ"] for r in m["ช่วงช้า"]]
    pnl = m["กำไรจากราคา"]
    n = len(fast)
    W, H, T, Bm = 760, 312, 84, 246
    pw, gapw = 210, 35
    out = [text(16, 24, f"ระยะห่างหดทั้งสองแบบ แต่กำไรจากราคา {B.fmt(pnl)} ทั้งสองแบบ", 13, C["ink"], weight=700)]
    out.append(f'<line x1="300" y1="40" x2="322" y2="40" stroke="{C["amber"]}" stroke-width="2.4"/>')
    out.append(text(328, 44, f"Mean เร็ว {B.fmt(m['เร็ว'])}", 11, C["amber"], weight=700))
    out.append(f'<line x1="440" y1="40" x2="462" y2="40" stroke="{C["purple"]}" stroke-width="2.4" stroke-dasharray="5 4"/>')
    out.append(text(468, 44, f"Mean ช้า {B.fmt(m['ช้า'])}", 11, C["purple"], weight=700))
    hi = x * 1.2
    for p, (title, kind) in enumerate((("X กับ Mean", "line"), ("ระยะห่าง X − Mean", "bar"), ("กำไรจากราคา", "pnl"))):
        L = 40 + p * (pw + gapw)
        Rr = L + pw
        out.append(text(L, T - 16, title, 12, C["ink"], weight=700))
        lo_, hi_ = (0, hi) if kind != "pnl" else (-hi / 2, hi / 2)
        Y = lambda v, lo_=lo_, hi_=hi_: Bm - (v - lo_) / (hi_ - lo_) * (Bm - T)  # noqa: E731
        X = lambda i, L=L: L + 24 + i * (pw - 48) / (n - 1)  # noqa: E731
        out.append(f'<line x1="{L}" y1="{Y(0):.1f}" x2="{Rr}" y2="{Y(0):.1f}" stroke="{C["axis"]}" stroke-width="1.5"/>')
        if kind == "line":
            out.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(x):.1f}" for i in range(n))}" fill="none" '
                       f'stroke="{C["blue"]}" stroke-width="2.4"/>')
            out.append(text(X(0), Y(x) - 8, f"X = {B.fmt(x)} ทุกช่วง", 11, C["blue"], "start", 700))
            for ser, col, dash in ((fast, C["amber"], ""), (slow, C["purple"], ' stroke-dasharray="5 4"')):
                out.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ser))}" '
                           f'fill="none" stroke="{col}" stroke-width="2.2"{dash}/>')
                for i, v in enumerate(ser):
                    out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{col}"/>')
            out.append(text(X(n - 1), Y(fast[-1]) + 18, B.fmt(fast[-1]), 10.5, C["amber"], "middle", 700))
            out.append(text(X(n - 1), Y(slow[-1]) + 18, B.fmt(slow[-1]), 10.5, C["purple"], "middle", 700))
        elif kind == "bar":
            for i in range(n):
                for k, (v, col) in enumerate(((gfast[i], C["amber"]), (gslow[i], C["purple"]))):
                    bx = X(i) - 13 + k * 13
                    out.append(f'<rect x="{bx:.1f}" y="{Y(v):.1f}" width="12" height="{max(1, Y(0) - Y(v)):.1f}" rx="2" '
                               f'fill="{col}" fill-opacity=".85"/>')
                if i > 0:
                    out.append(text(X(i), Y(max(gfast[i], gslow[i])) - 6, B.fmt(gslow[i]), 10.5, C["purple"], "middle", 700))
            out.append(text(X(1) + 10, Y(gfast[1]) - 6, B.fmt(gfast[1]), 10.5, C["amber"], "start", 700))
            out.append(text(X(0), Y(gfast[0]) - 6, B.fmt(gfast[0]), 10.5, C["ink"], "middle", 700))
        else:
            out.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(pnl):.1f}" for i in range(n))}" fill="none" '
                       f'stroke="{C["ink"]}" stroke-width="2.4"/>')
            for i in range(n):
                out.append(f'<circle cx="{X(i):.1f}" cy="{Y(pnl):.1f}" r="4" fill="{C["ink"]}"/>')
            out.append(f'<rect x="{L + 20}" y="{Y(pnl) - 52:.1f}" width="{pw - 40}" height="28" rx="6" fill="#f5f3ff" '
                       f'stroke="{C["purple"]}"/>')
            out.append(text(L + pw / 2, Y(pnl) - 33, f"{B.fmt(pnl)} ทั้งสองแบบ", 12.5, C["purple"], "middle", 700))
        for i in range(n):
            out.append(text(X(i), Bm + 18, f"ช่วง {i}", 10.5, C["grey"], "middle"))
    alt = (f"สามแผง แผงแรก X ค้างที่ {B.fmt(x)} Mean เร็ว {B.fmt(m['เร็ว'])} เลื่อน "
           f"{' '.join(B.fmt(v) for v in fast)} และ Mean ช้า {B.fmt(m['ช้า'])} เลื่อน {' '.join(B.fmt(v) for v in slow)} "
           f"แผงสองระยะห่างหดเป็น {B.fmt(gfast[-1])} และ {B.fmt(gslow[-1])} แผงสามกำไรจากราคาเป็น {B.fmt(pnl)} ทุกช่วง")
    cap = f"short X 10 ชุดที่ X = {B.fmt(x)} · แผงขวาเป็นแผงเดียวที่เป็นเงิน"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-rolling-exit")
def _rolling_exit(fig):
    r = fig["ch14"]["v2"]["ไม้บรรทัดเฉลี่ย4"]
    rows, xv = r["แถว"], r["X"]
    hist = rows[0]["หน้าต่าง"]                       # สี่ช่วงแรก (ช่วงที่ 4 คือจุดเข้า)
    xs = hist + [xv] * (len(rows) - 1)
    n = len(xs)
    i0 = len(hist) - 1                               # ดัชนีจุดเข้า
    W, H, L, R, T, Bm = 760, 330, 64, 96, 64, 276
    lo, hi = -2.6, 4.2
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    gx = (W - L - R) / (n - 1)
    X = lambda i: L + gx * i  # noqa: E731
    out = [text(24, 26, "แอปวาดไม้บรรทัดเฉลี่ย 4 ช่วง: เส้นเลื่อนขึ้นมาหา X ทั้งที่ X ไม่ขยับ", 13, C["ink"], weight=700)]
    for g in (-2, 0, 2, 4):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 10.5, C["grey"], "end"))
    ids = list(range(i0, n))
    for key, lab, col, dash in (("เส้นเข้า", "เส้นเข้า Mean + 2", C["red"], "5 4"),
                                ("Mean", "Mean 4 ช่วง", C["amber"], ""),
                                ("เส้นออก", "เส้นออก Mean + 0.5", C["green"], "5 4")):
        pts = " ".join(f"{X(i):.1f},{Y(rows[k][key]):.1f}" for k, i in enumerate(ids))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.8"'
                   + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
        out.append(text(X(n - 1) + 8, Y(rows[-1][key]) + (4 if key != "เส้นออก" else 16), lab, 10.5, col, "start", 700))
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(xs))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.6" stroke-linejoin="round"/>')
    for i, v in enumerate(xs):
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{C["blue"]}"/>')
    out.append(text(X(0), Y(xs[0]) + 18, f"X {B.fmt(xs[0])}", 10.5, C["blue"], "middle", 700))
    for k, i in enumerate(ids):
        z = rows[k]["Z"]
        out.append(text(X(i), Y(xv) - 14, f"Z {B.fmt(z)}", 11.5, C["purple"], "middle", 700))
    out.append(f'<circle cx="{X(i0):.1f}" cy="{Y(xv):.1f}" r="6" fill="{C["purple"]}"/>')
    out.append(text(X(i0), Y(xv) + 22, "เข้า short", 11, C["purple"], "middle", 700))
    out.append(f'<circle cx="{X(n - 1):.1f}" cy="{Y(xv):.1f}" r="6" fill="#fff" stroke="{C["green"]}" stroke-width="2.2"/>')
    out.append(text(X(n - 1), Y(xv) + 22, "สัญญาณออก", 11, C["green"], "middle", 700))
    out.append(text((X(i0) + X(n - 1)) / 2, Bm + 40, f"X อยู่ที่ {B.fmt(xv)} ตลอด · กำไรจากราคา {B.fmt(r['กำไรจากราคา'])} · "
                    f"หลังต้นทุน {B.fmt(r['สุทธิ'])}", 11.5, C["red"], "middle", 700))
    for i in range(n):
        out.append(text(X(i), Bm + 18, f"ช่วง {i + 1}", 10.5, C["grey"], "middle"))
    alt = (f"เส้น X {' '.join(B.fmt(v) for v in xs)} · ตั้งแต่ช่วงที่ {i0 + 1} Mean ของ 4 ช่วงล่าสุดเป็น "
           f"{' '.join(B.fmt(rw['Mean']) for rw in rows)} เส้นออกเลื่อนขึ้นมาแตะ X ที่ {B.fmt(xv)} Z-score "
           f"{' '.join(B.fmt(rw['Z']) for rw in rows)} กำไรจากราคา {B.fmt(r['กำไรจากราคา'])}")
    cap = f"short X 10 ชุดที่ X = {B.fmt(xv)} · SD ตรึง 1 · Mean = ค่าเฉลี่ยของ 4 ช่วงล่าสุดรวมช่วงนั้น"
    return wrap(W, H, alt, out, cap, "สอน")
