"""บท 16 — จากกราฟสู่คำสั่งจริง · สเปกกราฟของบท

sab-fill-timeline : มูลค่าสุทธิที่ถือ (long − short) สี่จังหวะของคำสั่งตั้งรอสองขา · เป้า = 0 (เส้นประ) · เอียง 600
sab-book-walk (v2): เดินกระดานสมมติของ A สี่ชั้น · ขาละ 1,000 / 5,000 / 10,000 / 20,000 กินถึงชั้นไหน เสียต่อ fill 0.5 / 4 / 14 / 54
sab-capacity-curve: เส้นกำไรตามขนาด (ch16.v2: 5.95 × ขาละ ÷ 1,000 − 4 × ราคาที่เสียต่อ fill จากกระดานสมมติ · โลก 60/25/15)
"""
from sab_charts import chart, wrap, text, Frame, nice_ticks, C, B


def _sign(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-fill-timeline")
def _fill_timeline(fig):
    c = fig["ch16"]
    tl = c["เส้นเวลา"]
    tgtB = c["ได้ขาเดียวบางส่วน"]["Bเป้า"]
    tilt = c["ขาเดียว"]["เอียง"]
    W, H = 760, 330
    ys = [r["สุทธิ"] for r in tl]
    f = Frame(0, max(ys), W, H, L=70, R=30, T=64, Bm=240)
    out = f.grid(nice_ticks(0, max(ys), 4))
    n = len(tl)
    gw = (W - f.L - f.R) / n
    X = lambda i: f.L + gw * i + gw / 2          # noqa: E731
    # เป้า: สุทธิ 0 (สองขามูลค่าเท่ากัน)
    out.append(f'<line x1="{f.L}" y1="{f.y(0):.1f}" x2="{W - f.R}" y2="{f.y(0):.1f}" stroke="{C["green"]}" '
               f'stroke-dasharray="6 4" stroke-width="2"/>')
    out.append(text(W - f.R - 4, f.y(0) - 7, "เป้า: สุทธิ 0", 11, C["green"], "end", 700))
    # ขั้นบันได
    d = f"M{f.L:.1f},{f.y(ys[0]):.1f} H{X(0):.1f}"
    for i in range(1, n):
        d += f" H{X(i) - gw / 2:.1f} V{f.y(ys[i]):.1f} H{X(i):.1f}"
    d += f" H{W - f.R:.1f}"
    out.append(f'<path d="{d}" fill="none" stroke="{C["blue"]}" stroke-width="2.6"/>')
    for i, r in enumerate(tl):
        col = C["purple"] if r["สุทธิ"] == tilt and i == 2 else C["blue"]
        out.append(f'<circle cx="{X(i):.1f}" cy="{f.y(r["สุทธิ"]):.1f}" r="4.5" fill="{col}"/>')
        if i > 0:
            out.append(text(X(i), f.y(r["สุทธิ"]) - 10, B.fmt(r["สุทธิ"]), 12, col, "middle", 700))
        out.append(text(X(i), f.Bm + 20, r["จังหวะ"], 11.5, C["ink"], "middle", 700))
        out.append(text(X(i), f.Bm + 38, f"A {B.fmt(r['Aได้'])} · B {B.fmt(r['Bได้'])}", 11, C["muted"], "middle"))
    out.append(text(X(2) + 12, f.y(tilt) + 24, f"เอียง long {B.fmt(tilt)}", 12.5, C["purple"], "start", 700))
    out.append(text(f.L, 26, f"Net Exposure (long − short) · เป้า A 10 กับ B {B.fmt(tgtB)}", 13.5, C["ink"], weight=700))
    alt = (f"เส้นขั้นบันไดของ Net Exposure: ส่งคำสั่ง 0 · A ได้ครบ {B.fmt(ys[1])} · B ได้ −8 จาก {B.fmt(tgtB)} "
           f"เหลือ {B.fmt(ys[2])} · ครบเวลารอยังค้าง {B.fmt(ys[3])} ขณะที่เป้าคือ 0")
    cap = "แกนตั้ง = Net Exposure (ดอลลาร์)"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-capacity-curve")
def _capacity_curve(fig):
    v2 = fig["ch16"]["v2"]["capacity"]
    c = [{"ขนาดต่อขา": r["ขนาดต่อขา"], "ต่อรอบ": r["ต่อไม้_หลัก"]} for r in v2["ตาราง"]]
    naive = v2["ขยาย20เท่าถ้าเส้นตรง"]     # 20 × ค่าที่ขาละ 1,000 (คำตอบยั่วใจของ 🛑)
    xs = [r["ขนาดต่อขา"] for r in c]
    ys = [r["ต่อรอบ"] for r in c]
    W, H = 760, 340
    f = Frame(min(ys), naive, W, H, L=70, R=30, T=60, Bm=270, pad=0.1)
    out = f.grid(nice_ticks(min(ys), naive, 5))
    x0, x1 = 0, max(xs)
    X = lambda x: f.L + (x - x0) / (x1 - x0) * (W - f.L - f.R)    # noqa: E731
    # เส้นประ: ถ้ากำไรโตตามขนาด (ไม่มีกระดาน) — จาก 0 ถึง 20 × ค่าที่ขาละ 1,000
    out.append(f'<line x1="{X(0):.1f}" y1="{f.y(0):.1f}" x2="{X(max(xs)):.1f}" y2="{f.y(naive):.1f}" '
               f'stroke="{C["grey"]}" stroke-dasharray="6 4" stroke-width="2"/>')
    out.append(text(X(max(xs)) - 6, f.y(naive) - 8, f"ถ้าโตตามขนาด {_sign(naive)}", 12, C["muted"], "end", 700))
    pts = " ".join(f"{X(x):.1f},{f.y(y):.1f}" for x, y in zip(xs, ys))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.4" stroke-linejoin="round"/>')
    for x, y in zip(xs, ys):
        col = C["green"] if y >= 0 else C["red"]
        out.append(f'<circle cx="{X(x):.1f}" cy="{f.y(y):.1f}" r="3.5" fill="{col}"/>')
    peak = max(c, key=lambda r: r["ต่อรอบ"])
    last = c[-1]
    small = next(r for r in c if r["ขนาดต่อขา"] == 1000)
    out.append(f'<circle cx="{X(peak["ขนาดต่อขา"]):.1f}" cy="{f.y(peak["ต่อรอบ"]):.1f}" r="6" fill="{C["purple"]}"/>')
    out.append(text(X(peak["ขนาดต่อขา"]), f.y(peak["ต่อรอบ"]) - 28, f"สูงสุด {_sign(peak['ต่อรอบ'])}",
                    12.5, C["purple"], "middle", 700))
    out.append(f'<circle cx="{X(last["ขนาดต่อขา"]):.1f}" cy="{f.y(last["ต่อรอบ"]):.1f}" r="6" fill="{C["purple"]}"/>')
    out.append(text(X(last["ขนาดต่อขา"]) - 10, f.y(last["ต่อรอบ"]) + 4, _sign(last["ต่อรอบ"]), 12.5, C["purple"], "end", 700))
    out.append(text(X(small["ขนาดต่อขา"]) + 4, f.y(small["ต่อรอบ"]) + 20, f"ของมิน {_sign(small['ต่อรอบ'])}",
                    11.5, C["ink"], "start", 700))
    ten = next(r for r in c if r["ขนาดต่อขา"] == 10000)
    out.append(text(X(ten["ขนาดต่อขา"]) + 10, f.y(ten["ต่อรอบ"]) - 8, _sign(ten["ต่อรอบ"]), 11.5, C["ink"], "start", 700))
    for x in (1000, 5000, 10000, 20000):
        out.append(text(X(x), f.Bm + 18, B.fmt(x), 11, C["grey"], "middle"))
    out.append(text((f.L + W - f.R) / 2, f.Bm + 40, "ขนาดต่อขา (ดอลลาร์)", 12, C["muted"], "middle"))
    out.append(text(f.L, 26, "Expected Value ต่อไม้ เมื่อขยายขนาด (Order Book เดิม)", 13.5, C["ink"], weight=700))
    alt = (f"เส้น Expected Value ต่อไม้ตามขนาดต่อขา: 1,000 ได้ {_sign(small['ต่อรอบ'])} · สูงสุดที่ "
           f"{B.fmt(peak['ขนาดต่อขา'])} ได้ {_sign(peak['ต่อรอบ'])} · 10,000 เหลือ {_sign(ten['ต่อรอบ'])} · "
           f"20,000 ติดลบ {_sign(last['ต่อรอบ'])}")
    cap = "การ์ดโลกซ้อม 60/25/15 (5.95 ต่อไม้ที่ขาละ 1,000 หักค่าธรรมเนียมแล้ว) · Order Book สมมติของ A · 4 fill ต่อไม้"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-notrade-buffer")
def _notrade_buffer(fig):
    """กันชนไม่เทรด: สองแผง · ซ้าย เป้าแกว่ง (เชือกเดิม) · ขวา เป้าเดินทางเดียว · แถบ = ที่ถือ ± กันชน"""
    g = fig["ch16"]["v2"]["กันชน"]
    buf = fig["ch16"]["กันชนไม่เทรด"]["กันชนตัว"]
    W, H = 760, 330
    panels = [("แกว่ง", "เป้าแกว่ง (เชือกเดิม)", 0), ("เดินทางเดียว", "เป้าเดินทางเดียว", 1)]
    allv = [v for k, _, _ in panels for v in g[k]["เป้า"]]
    lo, hi = min(allv) - buf, max(allv) + buf
    T, Bm = 70, 250
    Y = lambda v: T + (hi - v) / (hi - lo) * (Bm - T)       # noqa: E731  (ค่าลบมากอยู่ล่าง)
    out = []
    pw, gap, L0 = 320, 40, 60
    for key, title, i in panels:
        L = L0 + i * (pw + gap)
        R = L + pw
        ts = g[key]["เป้า"]
        held = [ts[0]] + [m["ถือหลัง"] for m in g[key]["มีกันชน"]["เดือน"]]
        n = len(ts)
        X = lambda k: L + 18 + k * (pw - 36) / (n - 1)        # noqa: E731
        for v in range(int(hi), int(lo) - 1, -2):
            out.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{R}" y2="{Y(v):.1f}" stroke="{C["grid"]}" stroke-width="1"/>')
            if i == 0:
                out.append(text(L - 8, Y(v) + 4, B.fmt(v), 11, C["grey"], "end"))
        # แถบกันชน: ที่ถือ ± (กันชน − 1) = ช่วงที่เป้าอยู่แล้วไม่ส่งคำสั่ง
        for k in range(n):
            x0 = X(k) - (pw - 36) / (n - 1) / 2 if k else X(0)
            x1 = X(k) + (pw - 36) / (n - 1) / 2 if k < n - 1 else X(n - 1)
            hb = held[k - 1] if k else held[0]
            out.append(f'<rect x="{x0:.1f}" y="{Y(hb + buf - 1):.1f}" width="{x1 - x0:.1f}" '
                       f'height="{Y(hb - buf + 1) - Y(hb + buf - 1):.1f}" fill="{C["blue"]}" opacity="0.10"/>')
        # ที่ถือ (มีกันชน): ขั้นบันได
        d = f"M{X(0):.1f},{Y(held[0]):.1f}"
        for k in range(1, n):
            d += f" H{X(k):.1f} V{Y(held[k]):.1f}"
        out.append(f'<path d="{d}" fill="none" stroke="{C["blue"]}" stroke-width="2.6"/>')
        # เป้า: จุดเทาเส้นประ
        pts = " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in enumerate(ts))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{C["grey"]}" stroke-dasharray="5 4" stroke-width="1.6"/>')
        for k, v in enumerate(ts):
            out.append(f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="4" fill="{C["grey"]}"/>')
        for k, m in enumerate(g[key]["มีกันชน"]["เดือน"], start=1):
            if m["ส่ง"]:
                out.append(f'<circle cx="{X(k):.1f}" cy="{Y(m["ถือหลัง"]):.1f}" r="6" fill="{C["purple"]}"/>')
                out.append(text(X(k), Y(m["ถือหลัง"]) + (-12 if i == 0 else 20), f"ส่ง {B.fmt(m['ส่ง'])}",
                                11.5, C["purple"], "middle", 700))
            out.append(text(X(k), Bm + 18, f"เดือน {k}", 10.5, C["grey"], "middle"))
        out.append(text(X(0), Bm + 18, "เริ่ม", 10.5, C["grey"], "middle"))
        out.append(text(L, T - 22, title, 13, C["ink"], weight=700))
        f1, f2 = g[key]["ตามทุกครั้ง"], g[key]["มีกันชน"]
        out.append(text(L, Bm + 42, f"ตามทุกครั้ง {B.fmt(f1['คำสั่ง'])} คำสั่ง · {B.fmt(f1['ต้นทุน'])}", 11.5, C["muted"]))
        out.append(text(L, Bm + 62, f"มีกันชน {B.fmt(f2['คำสั่ง'])} คำสั่ง · {B.fmt(f2['ต้นทุน'])}", 11.5, C["blue"], weight=700))
    out.append(f'<rect x="{L0}" y="{T - 58}" width="11" height="11" rx="2" fill="{C["grey"]}"/>')
    out.append(text(L0 + 16, T - 48, "เป้า B (จุดเทา)", 11.5, C["muted"]))
    out.append(f'<rect x="{L0 + 130}" y="{T - 58}" width="11" height="11" rx="2" fill="{C["blue"]}"/>')
    out.append(text(L0 + 146, T - 48, "B ที่ถือเมื่อมีกันชน (แถบจาง = ไม่ส่ง)", 11.5, C["muted"]))
    alt = (f"สองแผง เป้าแกว่ง {', '.join(B.fmt(v) for v in g['แกว่ง']['เป้า'])} มีกันชนส่งคำสั่ง "
           f"{g['แกว่ง']['มีกันชน']['คำสั่ง']} ครั้ง แทน {g['แกว่ง']['ตามทุกครั้ง']['คำสั่ง']} · เป้าเดินทางเดียว "
           f"{', '.join(B.fmt(v) for v in g['เดินทางเดียว']['เป้า'])} มีกันชนส่ง {g['เดินทางเดียว']['มีกันชน']['คำสั่ง']} "
           f"ครั้ง ต้นทุนเท่ากัน {B.fmt(g['เดินทางเดียว']['มีกันชน']['ต้นทุน'])}")
    cap = f"ขา B ของคู่ A–B · กันชน {buf} ตัว · ต้นทุน 0.1% ของมูลค่าที่ซื้อขาย"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-book-walk")
def _book_walk(fig):
    """เดิน Order Book ฝั่งขายของ A: แถวบน = กระดานสมมติสี่ชั้น (ความกว้าง = มูลค่าที่รอ · สีเข้มขึ้น = ห่าง Mid Price มากขึ้น)
    แถวล่าง = ขนาดต่อขา 1,000 / 5,000 / 10,000 / 20,000 กินไปถึงชั้นไหน · ป้ายขวา = เสียต่อ fill และเฉลี่ย %"""
    bk = fig["ch16"]["v2"]["กระดาน"]
    layers, walk = bk["ชั้น"], bk["เดิน"]
    mid = fig["ch16"]["v2"]["ทันที"]["A"]["mid"]
    sizes = ["1000", "5000", "10000", "20000"]
    shades = ["#fde68a", "#fbbf24", "#f97316", "#dc2626"]
    W = 760
    L, R, T, rh, gap = 130, 170, 92, 30, 16
    total = sum(l["มูลค่า"] for l in layers)
    X = lambda v: L + v / total * (W - L - R)  # noqa: E731
    H = T + (len(sizes) + 1) * (rh + gap) + 40
    out = [text(16, 24, "ขนาดใหญ่ขึ้นห้าเท่า แต่ราคาที่เสียต่อ fill ใหญ่ขึ้นแปดเท่า เพราะต้องเอื้อมไปชั้นที่แพงกว่า",
                13.5, C["ink"], weight=700)]
    lx = 16
    for k, (l, sh) in enumerate(zip(layers, shades)):
        lab = f"ชั้น {k + 1} · ห่าง {B.fmt(l['ห่างเปอร์เซ็นต์'])}%"
        out.append(f'<rect x="{lx}" y="46" width="12" height="12" rx="2" fill="{sh}"/>')
        out.append(text(lx + 17, 56, lab, 11, C["muted"]))
        lx += 34 + 7.0 * len(lab)
    # แถวบน: กระดาน
    y = T
    out.append(text(L - 10, y + rh / 2 + 4, "กระดานฝั่งขาย A", 11.5, C["ink"], "end", 700))
    acc = 0
    for k, (l, sh) in enumerate(zip(layers, shades)):
        x0, x1 = X(acc), X(acc + l["มูลค่า"])
        out.append(f'<rect x="{x0:.1f}" y="{y}" width="{x1 - x0:.1f}" height="{rh}" fill="{sh}" fill-opacity=".45" '
                   f'stroke="{sh}" stroke-width="1.5"/>')
        out.append(text((x0 + x1) / 2, y + rh / 2 + 4, f"รอ {B.fmt(l['มูลค่า'])}", 10.5, C["ink"], "middle"))
        acc += l["มูลค่า"]
    out.append(text(W - R + 10, y + rh / 2 + 4, "ราคาที่เสียต่อ fill", 11, C["muted"], "start", 700))
    # แถวขนาด
    for i, s in enumerate(sizes):
        y = T + (i + 1) * (rh + gap)
        w = walk[s]
        out.append(text(L - 10, y + rh / 2 + 4, f"ขาละ {B.fmt(int(s))}", 11.5, C["ink"], "end", 700 if s in ("1000", "5000") else None))
        acc = 0
        for k, part in enumerate(w["ชั้น"]):
            val = part["เหรียญ"] * mid                 # มูลค่าที่ราคากลาง (ขาละ … คิดที่ Mid Price)
            x0, x1 = X(acc), X(acc + val)
            out.append(f'<rect x="{x0:.1f}" y="{y}" width="{x1 - x0:.1f}" height="{rh}" fill="{shades[k]}" stroke="#fff" stroke-width="1"/>')
            if x1 - x0 > 34:
                out.append(text((x0 + x1) / 2, y + rh / 2 + 4, f"+{B.fmt(part['เกิน'])}", 11, "#ffffff" if k >= 2 else C["ink"], "middle", 700))
            acc += val
        out.append(text(W - R + 10, y + rh / 2 + 4, f"{B.fmt(w['เกินรวม'])} (เฉลี่ย {B.fmt(w['เกินเฉลี่ยเปอร์เซ็นต์'])}%)", 12,
                        C["red"] if w["เกินรวม"] > walk["1000"]["เกินรวม"] else C["ink"], "start", 700))
    ybot = T + (len(sizes) + 1) * (rh + gap) - gap
    for t in (0, 5000, 10000, 20000):
        out.append(text(X(t), ybot + 18, B.fmt(t), 10.5, C["grey"], "middle"))
    out.append(text((X(0) + X(total)) / 2, ybot + 34, "มูลค่าที่ซื้อ (ดอลลาร์)", 11, C["muted"], "middle"))
    alt = (f"แถวบนคือกระดานสี่ชั้น รอ {', '.join(B.fmt(l['มูลค่า']) for l in layers)} ที่ห่าง Mid Price "
           f"{', '.join(B.fmt(l['ห่างเปอร์เซ็นต์']) for l in layers)}% แถวล่างคือขาละ 1,000 5,000 10,000 20,000 "
           f"เสียต่อ fill {', '.join(B.fmt(walk[s]['เกินรวม']) for s in sizes)}")
    cap = "Order Book สมมติของ A ช่วงปกติ · ตัวเลขในแท่ง = ส่วนที่จ่ายเกิน Mid Price ในชั้นนั้น"
    return wrap(W, H, alt, out, cap, "สอน")
