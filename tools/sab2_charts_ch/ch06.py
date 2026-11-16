"""เล่ม 2 บท 6 — เชื่อข้อมูลใหม่แค่ไหน · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch06 เท่านั้น)

sab2-kalman-five  : ห้าวันด้วยมือ · ค่าที่เห็น (จุด) · ค่ากลางจาก Kalman (K คำนวณเอง) · ค่ากลางจาก K คงที่ 0.2 (เล่ม 1 บท 14)
sab2-kalman-drift : 🎲 โลกที่ h ไหล 1.0 → 1.5 (seed 1) · h จริง · Kalman SD 0.01 · Kalman SD 0.1 · rolling 60 วัน
sab2-kalman-btceth: 📡 BTC บน ETH (การขยับ log รายวัน) · rolling 60 · Kalman SD 0.01 · Kalman SD 0.1 · ช่วงเลือก → ช่วงตรวจ
"""

from sab_charts import B, C, chart, text, wrap

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


@chart("sab2-kalman-five")
def _five(fig):
    c = fig["ch06"]["ห้าวัน"]
    W, H = 760, 320
    xs = [0, 1, 2, 3, 4, 5]
    kal = [c["เริ่ม"]] + [d["ใหม่"] for d in c["วัน"]]
    fix = [c["เริ่ม"]] + c["Kคงที่02"]
    seen = c["เห็น"]
    out, y = _lines(xs, [("Kalman (K คิดเองทุกวัน)", kal, C["purple"]), ("K คงที่ 0.2", fix, C["amber"])],
                    "ค่ากลางที่ประมาณได้ เทียบกับค่าที่เห็นแต่ละวัน", [10, 11, 12, 13, 14, 15, 16], "วัน",
                    [(x, "เริ่ม" if x == 0 else f"วัน {x}") for x in xs], W=W, H=H)
    for x, v in zip(xs[1:], seen):
        out.append(f'<circle cx="{_xpos(x, 0, 5, W):.1f}" cy="{y(v):.1f}" r="5" fill="none" stroke="{C["blue"]}" stroke-width="2"/>')
        right = x == 5
        out.append(text(_xpos(x, 0, 5, W) + (-9 if right else 8), y(v) - 8, f"เห็น {B.fmt(v)}", 10.5, C["blue"],
                        "end" if right else "start"))
    for x, v, col in ((5, kal[-1], C["purple"]), (5, fix[-1], C["amber"])):
        out.append(text(_xpos(x, 0, 5, W) - 8, y(v) + 4, B.fmt(v), 11, col, "end", 700))
    alt = (f"ห้าวันด้วยมือ ค่าที่เห็น {', '.join(B.fmt(v) for v in seen)} เส้นม่วงคือค่ากลางจาก Kalman จาก {B.fmt(kal[0])} "
           f"ไป {B.fmt(kal[-1])} เส้นส้มคือ K คงที่ 0.2 ไป {B.fmt(fix[-1])}")
    cap = f"ห้าวันในตอน ก · Q {c['Q']} · R {c['R']} · เริ่มที่ {B.fmt(c['เริ่ม'])} · วงกลมน้ำเงินคือค่าที่เห็น"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab2-kalman-drift")
def _drift(fig):
    s = fig["ch06"]["จำลอง"]
    g = s["กราฟ"]
    W, H = 760, 330
    out, _ = _lines(g["วัน"], [("h จริง", g["จริง"], C["green"]), ("Kalman SD 0.01", g["k001"], C["purple"]),
                               ("Kalman SD 0.1", g["k01"], C["red"]), ("หน้าต่าง 60 วัน", g["r60"], C["grey"])],
                    f"โลกที่ h ไหลจาก {B.fmt(s['h0'])} ไป {B.fmt(s['h1'])} ใน {B.fmt(s['n'])} วัน",
                    [0.5, 1, 1.5, 2], "วันที่", [(d, B.fmt(d)) for d in g["วัน"][::12]], W=W, H=H)
    alt = (f"เส้นเขียว h จริงไหลจาก {B.fmt(s['h0'])} ไป {B.fmt(s['h1'])} เส้นม่วง Kalman SD 0.01 เกาะเส้นเขียว "
           f"เส้นแดง Kalman SD 0.1 สะบัดขึ้นลงรอบเส้นเขียว เส้นเทาหน้าต่าง 60 วันอยู่ระหว่างกลาง")
    cap = f"โลกจำลองหนึ่งโลก (seed 1) · drifting_h_pair · วัดบนการขยับ log รายวัน · แสดงทุก 10 วัน ตั้งแต่วันที่ {s['เริ่มวัด']}"
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-kalman-btceth")
def _btceth(fig):
    r = fig["ch06"]["จริง"]
    g = r["กราฟ"]
    W, H = 760, 340
    xs = g["i"]
    out, y = _lines(xs, [("หน้าต่าง 60 วัน", g["r60"], C["grey"]), ("Kalman SD 0.01", g["k001"], C["purple"]),
                         ("Kalman SD 0.1", g["k01"], C["red"])],
                    "h ของ BTC บน ETH แต่ละวัน (ใช้ข้อมูลถึงเมื่อวานเท่านั้น)", [0, 0.5, 1, 1.5], "เดือน",
                    [(x, lab) for x, lab in g["ปีป้าย"]], W=W, H=H)
    xb = _xpos(g["เส้นแบ่ง"], xs[0], xs[-1], W)
    out.append(f'<line x1="{xb:.1f}" y1="56" x2="{xb:.1f}" y2="250" stroke="{C["ink"]}" stroke-dasharray="5 4" stroke-width="1.3"/>')
    out.append(text(xb - 6, 70, "ช่วงเลือก", 11, C["ink"], "end", 700))
    out.append(text(xb + 6, 70, "ช่วงตรวจ", 11, C["ink"], "start", 700))
    alt = (f"h ของ BTC บน ETH สามวิธี ช่วงเลือกอยู่แถว {B.fmt(r['hเลือก'])} ช่วงตรวจลดลงไปแถว {B.fmt(r['hตรวจ'])} "
           f"เส้นแดง Kalman SD 0.1 กระโดดแรงที่สุด เส้นม่วง Kalman SD 0.01 กับเส้นเทาหน้าต่าง 60 วันไปด้วยกัน")
    cap = (f"Binance ราคาปิดรายวัน · {r['เริ่มวัด']} ถึง {r['จบตรวจ']} · ช่วงทดสอบสุดท้ายไม่ได้แตะ · แสดงทุก 5 วัน · "
           f"เส้นประคือวันแรกของช่วงตรวจ {r['เริ่มตรวจ']}")
    return wrap(W, H, alt, out, cap, "จริง")
