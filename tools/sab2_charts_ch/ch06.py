"""เล่ม 2 บท 6 — เชื่อข้อมูลใหม่แค่ไหน · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch06 เท่านั้น)

sab2-kalman-five  : ห้าวันด้วยมือ · ค่าที่เห็น (จุด) · ค่ากลางจาก Kalman (K คำนวณเอง) · ค่ากลางจาก K คงที่ 0.2 (เล่ม 1 บท 14)
sab2-kalman-drift : 🎲 โลกที่ h ไหล 1.0 → 1.5 (seed 1) · h จริง · Kalman SD 0.01 · Kalman SD 0.1 · rolling 60 วัน
sab2-kalman-btceth: 📡 BTC บน ETH (การขยับ log รายวัน) · rolling 60 · Kalman SD 0.01 · Kalman SD 0.1 · ช่วงเลือก → ช่วงตรวจ
sab2-kalman-weights: น้ำหนักของข้อมูลอายุ 0–7 วัน · หน้าต่าง 4 วัน (เท่ากันแล้วตัดขาด) กับ K นิ่ง 0.39 (จางลงทีละ 0.61 เท่า)
sab2-kalman-reads : สามวันของตอน ข · 1 · ค่าที่อ่านได้ A ÷ B ± SD ที่มันพลาดได้ (1 ÷ |B|) กับ h ของตัวกรองที่ขยับตาม K
"""

from sab_charts import B, C, chart, text, wrap

BLUE_LIGHT, BLUE_DARK = "#60a5fa", "#1e40af"   # Kalman สองค่า SD = ไล่เฉดน้ำเงิน (README: Graded series)
L, R = 64, 24          # ขอบซ้าย/ขวาของ Frame ใน sab_charts.lines (ใช้วางจุดและเส้นแบ่งช่วงให้ตรงแกน x)


def _xpos(x, x0, x1, W):
    return L + (x - x0) / ((x1 - x0) or 1) * (W - L - R)


def _lines(xs, series, title, ticks, xlabel, xticks, W=760, H=320, T=56, Bm=250):
    """แบบ sab_charts.lines แต่กำหนดเส้นแกน y เอง และไม่บังคับให้แกนเริ่มที่ศูนย์ · คืน (ชิ้นส่วน SVG, ฟังก์ชัน y)"""
    lo, hi = min(ticks), max(ticks)
    y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = []
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{y(g):.1f}" x2="{W - R}" y2="{y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    x0, x1 = min(xs), max(xs)
    for name, ys, col in series:
        pts = " ".join(f"{_xpos(x, x0, x1, W):.1f},{y(v):.1f}" for x, v in zip(xs, ys) if v is not None)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.2" stroke-linejoin="round"/>')
    lx = L
    for name, _, col in series:
        out.append(f'<rect x="{lx}" y="{T - 16}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 6, name, 11.5, C["muted"]))
        lx += 24 + 7.5 * len(name)
    out.append(text(L, T - 30, title, 13, C["ink"], weight=700))
    out.append(text((L + W - R) / 2, Bm + 36, xlabel, 12, C["muted"], "middle"))
    for x, lab in xticks:
        out.append(text(_xpos(x, x0, x1, W), Bm + 16, lab, 10.5, C["grey"], "middle"))
    return out, y


def _legend(out, items, x, y):
    """items = [(ชื่อ, สี, แบบ)] แบบ = "box" | "line" | "dot" · คืนตำแหน่ง x ถัดไป"""
    for name, col, kind in items:
        if kind == "line":
            out.append(f'<line x1="{x}" y1="{y - 4}" x2="{x + 18}" y2="{y - 4}" stroke="{col}" stroke-width="2.6"/>')
            dx = 24
        elif kind == "dot":
            out.append(f'<circle cx="{x + 6}" cy="{y - 4}" r="5" fill="#fff" stroke="{col}" stroke-width="2"/>')
            dx = 16
        else:
            out.append(f'<rect x="{x}" y="{y - 10}" width="11" height="11" rx="2" fill="{col}"/>')
            dx = 16
        out.append(text(x + dx, y, name, 11.5, C["muted"]))
        x += dx + 12 + 7.2 * len(name)
    return x


@chart("sab2-kalman-five")
def _five(fig):
    c = fig["ch06"]["ห้าวัน"]
    W, H = 760, 320
    xs = [0, 1, 2, 3, 4, 5]
    kal = [c["เริ่ม"]] + [d["ใหม่"] for d in c["วัน"]]
    fix = [c["เริ่ม"]] + c["Kคงที่02"]
    seen = c["เห็น"]
    out, y = _lines(xs, [("Kalman (K คิดเองทุกวัน)", kal, C["blue"]), ("ความเร็ว 0.2 ทุกวัน (เล่ม 1)", fix, C["amber"])],
                    "ค่ากลางที่ประมาณได้ เทียบกับค่าที่เห็นแต่ละวัน", [10, 11, 12, 13, 14, 15, 16], "วัน",
                    [(x, "เริ่ม" if x == 0 else f"วัน {x}") for x in xs], W=W, H=H)
    for x, v in zip(xs[1:], seen):
        out.append(f'<circle cx="{_xpos(x, 0, 5, W):.1f}" cy="{y(v):.1f}" r="5" fill="none" stroke="{C["ink"]}" stroke-width="2"/>')
        right = x == 5
        out.append(text(_xpos(x, 0, 5, W) + (-9 if right else 8), y(v) - 8, f"เห็น {B.fmt(v)}", 10.5, C["ink"],
                        "end" if right else "start"))
    for x, v, col in ((5, kal[-1], C["blue"]), (5, fix[-1], C["amber"])):
        out.append(text(_xpos(x, 0, 5, W) - 8, y(v) + 4, B.fmt(v), 11, col, "end", 700))
    alt = (f"ห้าวันด้วยมือ ค่าที่เห็น {', '.join(B.fmt(v) for v in seen)} เส้นน้ำเงินคือค่ากลางจาก Kalman จาก {B.fmt(kal[0])} "
           f"ไป {B.fmt(kal[-1])} เส้นส้มคือ K คงที่ 0.2 ไป {B.fmt(fix[-1])}")
    cap = f"ห้าวันในตอน ก · Q {c['Q']} · R {c['R']} · เริ่มที่ {B.fmt(c['เริ่ม'])} · วงกลมเทาเข้มคือค่าที่เห็น"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab2-kalman-drift")
def _drift(fig):
    s = fig["ch06"]["จำลอง"]
    g = s["กราฟ"]
    W, H = 760, 330
    out, _ = _lines(g["วัน"], [("h จริง", g["จริง"], C["green"]), ("Kalman SD 0.01", g["k001"], BLUE_LIGHT),
                               ("Kalman SD 0.1", g["k01"], BLUE_DARK), ("หน้าต่าง 60 วัน", g["r60"], C["grey"])],
                    f"โลกที่ h ไหลจาก {B.fmt(s['h0'])} ไป {B.fmt(s['h1'])} ใน {B.fmt(s['n'])} วัน",
                    [0.5, 1, 1.5, 2], "วันที่", [(d, B.fmt(d)) for d in g["วัน"][::12]], W=W, H=H)
    alt = (f"เส้นเขียว h จริงไหลจาก {B.fmt(s['h0'])} ไป {B.fmt(s['h1'])} เส้นฟ้า Kalman SD 0.01 เกาะเส้นเขียว "
           f"เส้นน้ำเงินเข้ม Kalman SD 0.1 สะบัดขึ้นลงรอบเส้นเขียว เส้นเทาหน้าต่าง 60 วันอยู่ระหว่างกลาง")
    cap = f"โลกจำลองหนึ่งโลก (seed 1) · drifting_h_pair · วัดบนการขยับ log รายวัน · แสดงทุก 10 วัน ตั้งแต่วันที่ {s['เริ่มวัด']}"
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-kalman-btceth")
def _btceth(fig):
    r = fig["ch06"]["จริง"]
    g = r["กราฟ"]
    W, H = 760, 340
    xs = g["i"]
    out, y = _lines(xs, [("หน้าต่าง 60 วัน", g["r60"], C["grey"]), ("Kalman SD 0.01", g["k001"], BLUE_LIGHT),
                         ("Kalman SD 0.1", g["k01"], BLUE_DARK)],
                    "h ของ BTC บน ETH แต่ละวัน (ใช้ข้อมูลถึงเมื่อวานเท่านั้น)", [0, 0.5, 1, 1.5], "เดือน",
                    [(x, lab) for x, lab in g["ปีป้าย"]], W=W, H=H)
    xb = _xpos(g["เส้นแบ่ง"], xs[0], xs[-1], W)
    out.append(f'<line x1="{xb:.1f}" y1="56" x2="{xb:.1f}" y2="250" stroke="{C["ink"]}" stroke-dasharray="5 4" stroke-width="1.3"/>')
    out.append(text(xb - 6, 70, "ช่วงเลือก", 11, C["ink"], "end", 700))
    out.append(text(xb + 6, 70, "ช่วงตรวจ", 11, C["ink"], "start", 700))
    alt = (f"h ของ BTC บน ETH สามวิธี ช่วงเลือกอยู่แถว {B.fmt(r['hเลือก'])} ช่วงตรวจลดลงไปแถว {B.fmt(r['hตรวจ'])} "
           f"เส้นน้ำเงินเข้ม Kalman SD 0.1 กระโดดแรงที่สุด เส้นฟ้า Kalman SD 0.01 กับเส้นเทาหน้าต่าง 60 วันไปด้วยกัน")
    cap = (f"Binance ราคาปิดรายวัน · {r['เริ่มวัด']} ถึง {r['จบตรวจ']} · ช่วงทดสอบสุดท้ายไม่ได้แตะ · แสดงทุก 5 วัน · "
           f"เส้นประคือวันแรกของช่วงตรวจ {r['เริ่มตรวจ']}")
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-kalman-weights")
def _weights(fig):
    w = fig["ch06"]["น้ำหนักอายุ"]
    W, H, T, Bm = 760, 300, 84, 260
    ticks = w["แกน"]
    lo, hi = min(ticks), max(ticks)
    y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = []
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{y(g):.1f}" x2="{W - R}" y2="{y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    n = len(w["อายุ"])
    gw = (W - L - R) / n
    bw = 30
    for i, age in enumerate(w["อายุ"]):
        cx = L + gw * i + gw / 2
        for j, (v, col) in enumerate(((w["หน้าต่าง4"][i], C["grey"]), (w["Kalman"][i], C["blue"]))):
            x = cx - bw - 2 + j * (bw + 4)
            if v:
                out.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{bw}" height="{y(0) - y(v):.1f}" rx="2" fill="{col}"/>')
                out.append(text(x + bw / 2, y(v) - 6, B.fmt(v), 10.5, C["ink"] if j == 0 else col, "middle", 700))
            else:
                out.append(text(x + bw / 2, y(0) - 6, "0", 10.5, C["grey"], "middle", 700))
        out.append(text(cx, Bm + 18, "วันนี้" if age == 0 else f"{age} วันก่อน", 11, C["muted"], "middle"))
    # จุดตัดขาดของหน้าต่าง
    xc = L + gw * 4
    out.append(f'<line x1="{xc:.1f}" y1="{T + 4}" x2="{xc:.1f}" y2="{Bm}" stroke="{C["ink"]}" stroke-dasharray="5 4" stroke-width="1.2"/>')
    out.append(text(xc + 6, T + 16, "ข้อมูล 4 วันก่อนตกจากหน้าต่าง: น้ำหนักจาก 0.25 เหลือ 0 ทันที", 11, C["ink"], "start", 700))
    out.append(text(xc + 6, T + 32, f"Kalman ยังให้ต่อ ลดทีละ {B.fmt(w['หนึ่งลบK'])} เท่าทุกวัน ไม่ถึงศูนย์", 11, C["blue"], "start"))
    out.append(text(L, T - 58, "น้ำหนักที่ให้ข้อมูลแต่ละวัน ตามอายุของข้อมูล", 13, C["ink"], weight=700))
    _legend(out, [("หน้าต่าง 4 วัน (ได้วันละ 0.25 เท่ากัน)", C["grey"], "box"),
                  (f"Kalman ที่ K นิ่ง {B.fmt(w['K'])} (วันนี้ {B.fmt(w['K'])} · เมื่อวาน {B.fmt(w['K'])} × {B.fmt(w['หนึ่งลบK'])})", C["blue"], "box")],
            L, T - 34)
    alt = (f"แท่งเทาของหน้าต่าง 4 วันสูง 0.25 เท่ากันสี่วันแล้วเป็นศูนย์ แท่งน้ำเงินของ Kalman เริ่ม {B.fmt(w['Kalman'][0])} "
           f"แล้วลดเป็น {', '.join(B.fmt(v) for v in w['Kalman'][1:])} ไม่ถึงศูนย์")
    cap = f"ตอน ก · 3 · Q 1 · R 4 จึง K นิ่ง {B.fmt(w['K'])} · น้ำหนักของวันที่ย้อนไป k วันคือ K × {B.fmt(w['หนึ่งลบK'])} ยกกำลัง k"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab2-kalman-reads")
def _reads(fig):
    hm = fig["ch06"]["hมือ"]
    g = fig["ch06"]["กราฟอ่าน"]
    days = hm["วัน"]
    W, H, T, Bm = 760, 330, 86, 262
    ticks = g["แกน"]
    lo, hi = min(ticks), max(ticks)
    y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    xp = lambda i: L + 60 + i * (W - L - R - 200) / 3  # noqa: E731
    num = lambda v: B.fmt(int(v)) if float(v) == int(v) else B.fmt(v)  # noqa: E731
    out = []
    for t in ticks:
        out.append(f'<line x1="{L}" y1="{y(t):.1f}" x2="{W - R}" y2="{y(t):.1f}" stroke="{C["axis"] if t == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if t == 0 else 1}"/>')
        out.append(text(L - 8, y(t) + 4, B.fmt(t), 11, C["grey"], "end"))
    hs = [hm["เริ่ม"]] + [d["ใหม่"] for d in days]
    # h ของตัวกรอง: ขั้นบันไดจากวันหนึ่งไปอีกวัน
    d_ = f"M{xp(0):.1f},{y(hs[0]):.1f}"
    for i in range(1, 4):
        d_ += f" H{xp(i):.1f} V{y(hs[i]):.1f}"
    out.append(f'<path d="{d_}" fill="none" stroke="{C["blue"]}" stroke-width="2.6" stroke-linejoin="round"/>')
    for i, v in enumerate(hs):
        out.append(f'<circle cx="{xp(i):.1f}" cy="{y(v):.1f}" r="4" fill="{C["blue"]}"/>')
    out.append(text(xp(0), y(hs[0]) + 20, f"h เริ่ม {B.fmt(hs[0])}", 11, C["blue"], "middle", 700))
    for i, (d, sd) in enumerate(zip(days, g["sdอ่าน"]), start=1):
        x = xp(i) - 26
        top, bot = d["อ่าน"] + sd, max(lo, d["อ่าน"] - sd)
        out.append(f'<line x1="{x:.1f}" y1="{y(top):.1f}" x2="{x:.1f}" y2="{y(bot):.1f}" stroke="{C["ink"]}" stroke-width="2"/>')
        for v in (top, bot):
            out.append(f'<line x1="{x - 7:.1f}" y1="{y(v):.1f}" x2="{x + 7:.1f}" y2="{y(v):.1f}" stroke="{C["ink"]}" stroke-width="2"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y(d["อ่าน"]):.1f}" r="5.5" fill="#fff" stroke="{C["ink"]}" stroke-width="2.2"/>')
        out.append(text(x, y(top) - 9, f"อ่านได้ {num(d['อ่าน'])} ± {num(sd)}", 10.5, C["ink"], "middle", 700))
        out.append(text(xp(i) + 8, y(d["ใหม่"]) - 10, f"K {B.fmt(d['K'])} → h {num(d['ใหม่'])}", 11, C["blue"], "start", 700))
        out.append(text(xp(i), Bm + 18, f"วัน {i}", 11, C["muted"], "middle", 700))
        out.append(text(xp(i), Bm + 33, f"B ขยับ {num(d['B'])}%", 10.5, C["grey"], "middle"))
    out.append(text(xp(0), Bm + 18, "เริ่ม", 11, C["muted"], "middle", 700))
    out.append(text(L, T - 54, "ค่าที่อ่านได้ของ h ในแต่ละวัน กับ h ที่ตัวกรองยอมขยับตาม", 13, C["ink"], weight=700))
    _legend(out, [("ค่าที่อ่านได้ A ÷ B (ขีดตั้ง = ± SD ที่มันพลาดได้ คือ 1 ÷ |B|)", C["ink"], "dot"),
                  ("h ของ Kalman", C["blue"], "line")], L, T - 30)
    alt = (f"สามวัน ค่าที่อ่านได้ {', '.join(num(d['อ่าน']) for d in days)} พลาดได้ ± "
           f"{', '.join(B.fmt(v) for v in g['sdอ่าน'])} K {', '.join(B.fmt(d['K']) for d in days)} "
           f"h ไปจาก {B.fmt(hs[0])} เป็น {', '.join(num(v) for v in hs[1:])}")
    cap = f"สามวันของตอน ข · 1 · Q {B.fmt(hm['Q'])} · R {B.fmt(hm['R'])} · ความคลาดของค่าที่อ่านได้ = R ÷ B²"
    return wrap(W, H, alt, out, cap, "สอน")
