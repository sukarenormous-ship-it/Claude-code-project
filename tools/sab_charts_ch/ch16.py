"""บท 16 — จากกราฟสู่คำสั่งจริง · สเปกกราฟของบท

sab-fill-timeline : มูลค่าสุทธิที่ถือ (long − short) สี่จังหวะของคำสั่งตั้งรอสองขา · เป้า = 0 (เส้นประ) · เอียง 600
sab-capacity-curve: เส้นกำไรตามขนาด (ค่าคาดหมายต่อไม้หลัง taker + ส่วนต่างราคาจากกระดานสมมติ · โลก 60/25/15)
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
    out.append(text(f.L, 26, f"มูลค่าที่ถือสุทธิ (long − short) · เป้า A 10 กับ B {B.fmt(tgtB)}", 13.5, C["ink"], weight=700))
    alt = (f"เส้นขั้นบันไดของมูลค่าสุทธิที่ถือ: ส่งคำสั่ง 0 · A ได้ครบ {B.fmt(ys[1])} · B ได้ −8 จาก {B.fmt(tgtB)} "
           f"เหลือ {B.fmt(ys[2])} · ครบเวลารอยังค้าง {B.fmt(ys[3])} ขณะที่เป้าคือ 0")
    cap = "แกนตั้ง = มูลค่าที่ถือสุทธิ (ดอลลาร์) · ของเข้าบัญชีทีละขาตามที่ได้จริง"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-capacity-curve")
def _capacity_curve(fig):
    c = fig["ch16"]["capacity"]["หลัก"]["ตาราง"]
    naive = fig["ch16"]["capacityที่อ้าง"]["ขยาย20เท่าถ้าเส้นตรง"]     # 20 × ค่าที่ขาละ 1,000 (คำตอบยั่วใจของ 🛑)
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
    out.append(text(f.L, 26, "ค่าคาดหมายต่อไม้ เมื่อขยายขนาด (กระดานเดิม)", 13.5, C["ink"], weight=700))
    alt = (f"เส้นค่าคาดหมายต่อไม้ตามขนาดต่อขา: 1,000 ได้ {_sign(small['ต่อรอบ'])} · สูงสุดที่ "
           f"{B.fmt(peak['ขนาดต่อขา'])} ได้ {_sign(peak['ต่อรอบ'])} · 10,000 เหลือ {_sign(ten['ต่อรอบ'])} · "
           f"20,000 ติดลบ {_sign(last['ต่อรอบ'])}")
    cap = ("หัก taker 0.05% ทุกครั้งและราคาเฉลี่ยจากกระดานสมมติ · "
           "เส้นประ = คูณตามขนาด")
    return wrap(W, H, alt, out, cap, "สอน")
