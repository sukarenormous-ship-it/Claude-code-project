"""เล่ม 2 บท 8 — สายพานคัดคู่ของคนทำงานจริง · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch08 เท่านั้น)

sab2-pipe-cost   : กำไรต่อไม้ (ดอลลาร์ต่อขา 500) ที่ correlation 0.80 / 0.95 / 0.98 / 0.99 · Half-life 2 กับ 5 วัน · เส้นต้นทุนไปกลับของเล่ม
                   (1 ดอลลาร์) กับแบบแอป (3 ดอลลาร์)
sab2-pipe-sim    : 🎲 โลกปัจจัยที่รู้คำตอบ · จำนวนคู่ที่เหลือแต่ละขั้นของสายพาน (มัธยฐานของ 30 โลก) แยกคู่มีเชือกกับคู่อื่น
sab2-pipe-ssd    : สามคู่สมมติห้าวันของตอน ค · 1 (P · Q · R) · ระยะห่างแต่ละวัน · Mean ของระยะ · SSD = 5 × Mean² + ส่วนแกว่ง · Zero Crossing
sab2-pipe-groups : 📡 กำไรเฉลี่ยช่วงตรวจของกลุ่มคู่ที่คัดด้วยตัวกรองต่าง ๆ จากช่วงเลือก (การ์ดเล่ม 1 ไม้บรรทัดตรึง)
"""

from sab_charts import B, C, Frame, chart, nice_ticks, text, wrap


@chart("sab2-pipe-cost")
def _cost(fig):
    c = fig["ch08"]
    rows = c["กำไรแถว"]
    t = c["ต้นทุน"]
    rhos = [r["rho"] for r in c["rhoแถว"]]
    h2 = [next(r["กำไรดอลลาร์"] for r in rows if r["rho"] == rho and r["hl"] == 2) for rho in rhos]
    h5 = [next(r["กำไรดอลลาร์"] for r in rows if r["rho"] == rho and r["hl"] == 5) for rho in rhos]
    W, H = 760, 340
    vals = h2 + h5
    f = Frame(0, max(vals), W, H, T=78)
    out = f.grid(nice_ticks(0, max(vals)))
    gw = (W - f.L - f.R) / len(rhos)
    bw = 46
    for i, rho in enumerate(rhos):
        cx = f.L + gw * i + gw / 2
        for j, (v, col) in enumerate(((h2[i], C["amber"]), (h5[i], C["blue"]))):
            x = cx - (bw + 4) + j * (bw + 4)
            out.append(f'<rect x="{x:.1f}" y="{f.y(v):.1f}" width="{bw}" height="{max(1, f.y(0) - f.y(v)):.1f}" rx="2" fill="{col}"/>')
            out.append(text(x + bw / 2, f.y(v) - 6, B.fmt(v), 10.5, col, "middle", 700))
        out.append(text(cx, f.Bm + 30, f"correlation {B.fmt(rho)}", 11.5, C["muted"], "middle"))
    legend_lines = []
    for v, lab, col, dy in ((t["เล่มดอลลาร์"], f"ต้นทุนเล่ม {int(t['เล่มดอลลาร์'])} ดอลลาร์", C["green"], 14),
                            (t["แอปดอลลาร์"], f"ต้นทุนแอป {int(t['แอปดอลลาร์'])} ดอลลาร์", C["red"], -5)):
        out.append(f'<line x1="{f.L}" y1="{f.y(v):.1f}" x2="{W - f.R}" y2="{f.y(v):.1f}" stroke="{col}" stroke-dasharray="5 4" stroke-width="1.6"/>')
        legend_lines.append((lab, col))
    lx = f.L
    for name, col in (("Half-life 2 วัน", C["amber"]), ("Half-life 5 วัน", C["blue"])):
        out.append(f'<rect x="{lx}" y="{f.T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 20, name, 11.5, C["muted"]))
        lx += 130
    for name, col in legend_lines:
        out.append(f'<line x1="{lx}" y1="{f.T - 25}" x2="{lx + 18}" y2="{f.T - 25}" stroke="{col}" stroke-dasharray="5 3" stroke-width="2"/>')
        out.append(text(lx + 24, f.T - 20, name, 11.5, col, weight=700))
        lx += 140
    out.append(text(f.L, f.T - 48, f"กำไรต่อไม้ (ดอลลาร์ ขาละ {B.fmt(t['ขา'])}) เมื่อเข้าที่ 2 SD ออกที่ 0.5 SD", 13, C["ink"], weight=700))
    alt = ("กำไรต่อไม้ลดลงเมื่อ correlation สูงขึ้น ที่ correlation " + B.fmt(rhos[-1]) + " Half-life 2 วันได้ " + B.fmt(h2[-1]) +
           " ดอลลาร์ ใกล้เส้นต้นทุนแบบแอป " + B.fmt(t["แอปดอลลาร์"]) + " ดอลลาร์ ส่วนที่ correlation " + B.fmt(rhos[0]) + " ได้ " +
           B.fmt(h2[0]) + " ถึง " + B.fmt(h5[0]) + " ดอลลาร์")
    cap = (f"สองเหรียญแกว่งวันละ {B.fmt(c['sigma'])}% เท่ากัน · h 1 · กำไรต่อไม้ราว 1.5 เท่าของ SD ที่ X แกว่ง · "
           f"ต้นทุนแอปสมมติ {B.fmt(t['แอปต่อfill'])}% ต่อ fill")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab2-pipe-sim")
def _sim(fig):
    s = fig["ch08"]["จำลองสายพาน"]
    labels = ["45 คู่", "ผ่าน\nEngle–Granger", "ตัดเหรียญ\nนิ่งเดี่ยว · h", "Half-life ·\nZero Crossing", "ช่วงตรวจ\nยังข้าม Mean"]
    rope, other = s["มีเชือกมัธยฐาน"], s["อื่นมัธยฐาน"]
    W, H = 760, 340
    f = Frame(0, max(r + o for r, o in zip(rope, other)), W, H, T=78, pad=0.18)
    out = f.grid(nice_ticks(0, max(r + o for r, o in zip(rope, other))))
    gw = (W - f.L - f.R) / len(labels)
    bw = 58
    for i, lab in enumerate(labels):
        cx = f.L + gw * i + gw / 2
        base = 0
        for v, col in ((rope[i], C["green"]), (other[i], C["grey"])):
            if v:
                out.append(f'<rect x="{cx - bw / 2:.1f}" y="{f.y(base + v):.1f}" width="{bw}" height="{f.y(base) - f.y(base + v):.1f}" fill="{col}"/>')
            base += v
        out.append(text(cx, f.y(base) - 8, f"มีเชือก {B.fmt(rope[i])} · อื่น {B.fmt(other[i])}", 10.5, C["ink"], "middle", 700))
        for k, line in enumerate(lab.split("\n")):
            out.append(text(cx, f.Bm + 16 + 13 * k, line, 10.5, C["muted"], "middle"))
    lx = f.L
    for name, col in (("คู่ที่มีเชือกจริง (3 คู่)", C["green"]), ("คู่อื่น (รวมคู่ที่ติดกับดักเหรียญนิ่ง)", C["grey"])):
        out.append(f'<rect x="{lx}" y="{f.T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 20, name, 11.5, C["muted"]))
        lx += 200
    out.append(text(f.L, f.T - 48, "จำนวนคู่ที่เหลือหลังแต่ละขั้นของสายพาน (มัธยฐานของ 30 โลก)", 13, C["ink"], weight=700))
    alt = (f"เริ่ม 45 คู่ มีเชือกจริง 3 คู่ ผ่าน Engle–Granger เหลือคู่อื่น {B.fmt(other[1])} คู่ หลังตัดเหรียญนิ่งเดี่ยวเหลือคู่อื่น "
           f"{B.fmt(other[2])} คู่ คู่ที่มีเชือกยังอยู่ {B.fmt(rope[-1])} คู่จนขั้นสุดท้าย")
    cap = (f"โลกปัจจัย 10 เหรียญ · คู่มีเชือก φ {B.fmt(s['phi'])} สามคู่ · คู่แน่นที่ไม่มีเชือกหนึ่งคู่ · เหรียญนิ่งในตัวเอง φ "
           f"{B.fmt(s['กับดักphi'])} หนึ่งตัว · 731 + 365 วัน · seed 1–30")
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-pipe-groups")
def _groups(fig):
    g = fig["ch08"]["กราฟกลุ่ม"]
    names = ["ทั้ง 45 คู่", "ผ่าน EG\n(มี LTC ทุกคู่)", "สายพานไม่\nทดสอบเดี่ยว", "Correlation\nสูงสุด 5", "ระดับราคา\nสูงสุด 5",
             "Half-life\n≤ 30 วัน", "Correlation\nต่ำสุด 5"]
    vals = g["ค่า"]
    W, H = 760, 350
    f = Frame(min(vals), max(vals), W, H, T=60, Bm=262)
    out = f.grid(nice_ticks(min(vals), max(vals)))
    gw = (W - f.L - f.R) / len(names)
    bw = min(56, gw * 0.55)
    for i, (nm, v) in enumerate(zip(names, vals)):
        cx = f.L + gw * i + gw / 2
        y0, y1 = f.y(0), f.y(v)
        col = C["green"] if v >= 0 else C["red"]
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{min(y0, y1):.1f}" width="{bw:.1f}" height="{max(1, abs(y1 - y0)):.1f}" rx="3" fill="{col}"/>')
        out.append(text(cx, (y1 - 7) if v >= 0 else (y1 + 16), ("+" if v > 0 else "") + B.fmt(v), 11.5, col, "middle", 700))
        for k, line in enumerate(nm.split("\n")):
            out.append(text(cx, f.Bm + 18 + 13 * k, line, 10.5, C["muted"], "middle"))
    out.append(text(f.L, f.T - 30, "กำไรเฉลี่ยต่อคู่ในช่วงตรวจ (ดอลลาร์ ทุนคู่ละ 1,000) ของกลุ่มที่คัดจากช่วงเลือก", 13, C["ink"], weight=700))
    alt = ("กำไรเฉลี่ยช่วงตรวจ: ทั้ง 45 คู่ " + B.fmt(vals[0]) + " · ผ่าน EG " + B.fmt(vals[1]) + " · สายพานไม่ทดสอบเดี่ยว " +
           B.fmt(vals[2]) + " · correlation สูงสุด 5 " + B.fmt(vals[3]) + " · ระดับราคาสูงสุด 5 " + B.fmt(vals[4]) +
           " · Half-life ไม่เกิน 30 วัน " + B.fmt(vals[5]) + " · correlation ต่ำสุด 5 " + B.fmt(vals[6]))
    r = fig["ch08"]["จริง"]
    cap = (f"Binance ราคาปิดรายวัน · คัดด้วยช่วงเลือก {r['เริ่มเลือก']} ถึง {r['จบเลือก']} · วัดผลช่วงตรวจ {r['เริ่มตรวจ']} ถึง "
           f"{r['จบตรวจ']} · การ์ดเล่ม 1 ไม้บรรทัดตรึง · ค่าธรรมเนียม {B.fmt(fig['ch08']['ต้นทุน']['เล่มต่อfill'])}% ต่อ fill")
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-pipe-ssd")
def _ssd(fig):
    d = fig["ch08"]["ระยะ"]
    ticks = fig["ch08"]["ระยะแกน"]
    W, H = 760, 320
    top, bm = 112, 272
    lo, hi = min(ticks), max(ticks)
    y = lambda v: bm - (v - lo) / (hi - lo) * (bm - top)  # noqa: E731
    out = []
    pw, gap, L0 = 206, 22, 64
    num = lambda v: B.fmt(int(v)) if float(v) == int(v) else B.fmt(v)  # noqa: E731
    notes = {"P": ("Distance Method เลือกก่อน", C["red"]), "Q": ("คู่เดียวที่การ์ดทำเงินได้", C["green"]),
             "R": ("ห่างออกไปเรื่อย ๆ", C["muted"])}
    for k, name in enumerate(("P", "Q", "R")):
        r = d[name]
        x0 = L0 + k * (pw + gap)
        for t in ticks:
            out.append(f'<line x1="{x0}" y1="{y(t):.1f}" x2="{x0 + pw}" y2="{y(t):.1f}" stroke="{C["axis"] if t == 0 else C["grid"]}" '
                       f'stroke-width="{1.5 if t == 0 else 1}"/>')
            if k == 0:
                out.append(text(x0 - 8, y(t) + 4, B.fmt(t), 11, C["grey"], "end"))
        xs = [x0 + 18 + i * (pw - 36) / 4 for i in range(5)]
        ym = y(r["Mean"])
        out.append(f'<line x1="{x0}" y1="{ym:.1f}" x2="{x0 + pw}" y2="{ym:.1f}" stroke="{C["amber"]}" stroke-width="1.6" stroke-dasharray="6 4"/>')
        pts = " ".join(f"{x:.1f},{y(v):.1f}" for x, v in zip(xs, r["ห่าง"]))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.2" stroke-linejoin="round"/>')
        for x, v in zip(xs, r["ห่าง"]):
            out.append(f'<circle cx="{x:.1f}" cy="{y(v):.1f}" r="3.6" fill="{C["blue"]}"/>')
        for i, x in enumerate(xs):
            out.append(text(x, bm + 15, str(i + 1), 10, C["grey"], "middle"))
        out.append(text(x0 + pw / 2, top - 66, f"คู่ {name} · SSD {num(r['SSD'])}", 12.5, C["ink"], "middle", 700))
        out.append(text(x0 + pw / 2, top - 50, f"= 5 × Mean² {num(r['nMean2'])} + แกว่ง {num(r['ส่วนแกว่ง'])}", 11, C["muted"], "middle"))
        out.append(text(x0 + pw / 2, top - 34, f"ตัดผ่าน Mean {num(r['ข้าม'])} ครั้ง", 11, C["ink"], "middle"))
        out.append(text(x0 + pw / 2, top - 18, notes[name][0], 11, notes[name][1], "middle", 700))
    out.append(text(L0 + 1.5 * pw + gap, bm + 32, "วันที่ 1–5 ของแต่ละคู่ · เส้นทึบน้ำเงิน = ระยะห่าง (%) · เส้นประส้ม = Mean ของระยะ",
                    11, C["muted"], "middle"))
    out.append(text(L0, top - 90, "SSD ลงโทษทั้ง \"ห่างคงที่\" และ \"แกว่ง\" แต่เงินของการ์ดมาจากการแกว่งเท่านั้น", 13, C["ink"], weight=700))
    alt = ("สามคู่ห้าวัน คู่ P ห่าง 1 ทุกวัน SSD 5 ไม่เคยตัดผ่าน Mean คู่ Q ห่าง 4 กับ −4 สลับกัน SSD 64 ตัดผ่านสามครั้ง "
           "คู่ R ห่าง 6 ถึง 10 SSD 330 ตัดผ่านครั้งเดียว")
    cap = "สามคู่สมมติของตอน ค · 1 · ระยะห่างเป็นเปอร์เซ็นต์ · SSD = ผลรวมของระยะยกกำลังสอง"
    return wrap(W, H, alt, out, cap, "สอน")
