"""บท 17 เล่ม 2 — ความสัมพันธ์ไม่เป็นเส้นตรง และ options · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json เท่านั้น)

sab2-copula-grid : ตาราง 5 × 5 ของอันดับ BTC กับ ETH (การขยับ log รายวัน ช่วงเลือก 730 วัน · กลุ่มละ 146 วัน)
sab2-tail-bars   : วันที่ 10% ล่าง / 10% บน ไปด้วยกันกี่เปอร์เซ็นต์ · โลกปกติ · โลกตกพร้อมกัน · BTC–ETH สองช่วง · 45 คู่
sab2-cap-months  : 12 ไม้ short X ของ BTC–ETH ในช่วงตรวจ · ไม่มีเพดาน เทียบ มี call BTC + put ETH (ราคาจากแบบจำลอง)
"""

from sab_charts import B, C, chart, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]
TH_MONTH = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]


@chart("sab2-copula-grid")
def _copula_grid(fig):
    r = fig["ch17"]["จริง"]["formation"]
    g = r["ตาราง"]
    n = len(g)
    W, H = 760, 420
    L, T, cell = 250, 70, 62
    peak = max(max(row) for row in g)
    out = [text(16, 26, "ตาราง 5 × 5 ของอันดับ: BTC อยู่กลุ่มไหน ETH อยู่กลุ่มไหน (นับวัน)", 13, INK, weight=700)]
    out.append(text(L + n * cell / 2, T - 14, "กลุ่มของ ETH (1 = วันที่แย่ที่สุด 20% · 5 = ดีที่สุด 20%)", 11.5, MUTED, "middle"))
    for j in range(n):
        out.append(text(L + j * cell + cell / 2, T + n * cell + 18, f"{j + 1}", 11.5, GREY, "middle"))
    out.append(text(L - 70, T + n * cell / 2 - 8, "กลุ่มของ BTC", 11.5, MUTED, "end"))
    out.append(text(L - 70, T + n * cell / 2 + 10, "(1 = แย่สุด)", 11, MUTED, "end"))
    for i in range(n):
        out.append(text(L - 10, T + i * cell + cell / 2 + 4, f"{i + 1}", 11.5, GREY, "end"))
        for j in range(n):
            v = g[i][j]
            op = 0.08 + 0.85 * v / peak
            x, y = L + j * cell, T + i * cell
            col = C["red"] if (i, j) == (0, 0) else (C["green"] if (i, j) == (n - 1, n - 1) else C["blue"])
            out.append(f'<rect x="{x}" y="{y}" width="{cell - 3}" height="{cell - 3}" rx="3" fill="{col}" fill-opacity="{op:.2f}"/>')
            out.append(text(x + (cell - 3) / 2, y + cell / 2 + 4, B.fmt(v), 12, "#ffffff" if op > 0.55 else INK, "middle", 700))
    rx = L + n * cell + 24
    out.append(text(rx, T + 20, f"มุมซ้ายบน {B.fmt(g[0][0])} วัน", 11.5, C["red"], weight=700))
    out.append(text(rx, T + 38, "ทั้งคู่อยู่กลุ่มแย่สุด", 11, MUTED))
    out.append(text(rx, T + n * cell - 26, f"มุมขวาล่าง {B.fmt(g[-1][-1])} วัน", 11.5, C["green"], weight=700))
    out.append(text(rx, T + n * cell - 8, "ทั้งคู่อยู่กลุ่มดีสุด", 11, MUTED))
    alt = (f"ตาราง 5 คูณ 5 ของอันดับการขยับรายวัน BTC กับ ETH ช่วงเลือก กลุ่มละ {r['วันต่อกลุ่ม']} วัน ตัวเลขกองอยู่ตามเส้นทแยง "
           f"มุมที่ทั้งคู่แย่สุดมี {g[0][0]} วัน มากกว่ามุมที่ทั้งคู่ดีสุดซึ่งมี {g[-1][-1]} วัน")
    return wrap(W, H, alt, out, f"การขยับ log รายวันของ BTC กับ ETH · Binance spot (UTC) ช่วงเลือก {r['เริ่ม']} ถึง {r['จบ']} · "
                f"{r['วันขยับ']} วัน กลุ่มละ {r['วันต่อกลุ่ม']} วัน", "จริง")


@chart("sab2-tail-bars")
def _tail_bars(fig):
    c = fig["ch17"]
    wn, wc = c["โลก"]["ปกติ"]["ยาวเท่าช่วงเลือก"], c["โลก"]["ตกพร้อมกัน"]["ยาวเท่าช่วงเลือก"]
    f, v = c["จริง"]["formation"], c["จริง"]["validation"]
    cats = ["โลกปกติ 🎲", "โลกตกพร้อมกัน 🎲", "BTC–ETH ช่วงเลือก", "BTC–ETH ช่วงตรวจ", "45 คู่ ช่วงเลือก"]
    lo = [wn["ล่างมัธยฐาน"], wc["ล่างมัธยฐาน"], f["ล่างเปอร์เซ็นต์"], v["ล่างเปอร์เซ็นต์"], f["สี่สิบห้า"]["ล่างเฉลี่ยเปอร์เซ็นต์"]]
    hi = [wn["บนมัธยฐาน"], wc["บนมัธยฐาน"], f["บนเปอร์เซ็นต์"], v["บนเปอร์เซ็นต์"], f["สี่สิบห้า"]["บนเฉลี่ยเปอร์เซ็นต์"]]
    W, H, L, R, T, Bm = 760, 340, 56, 20, 84, 280
    top = 100
    Y = lambda val: Bm - val / top * (Bm - T)  # noqa: E731
    out = [text(16, 26, "วันแย่สุด 10% ของเหรียญหนึ่ง อีกเหรียญอยู่ 10% แย่สุดด้วยกี่เปอร์เซ็นต์ (เทียบฝั่งดีสุด)", 13, INK, weight=700)]
    for g in (0, 20, 40, 60, 80, 100):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, f"{g}%", 11, GREY, "end"))
    gw = (W - L - R) / len(cats)
    bw = 34
    for i, cat in enumerate(cats):
        cx = L + gw * i + gw / 2
        for j, (val, col) in enumerate(((lo[i], C["red"]), (hi[i], C["green"]))):
            x = cx - bw - 2 + j * (bw + 4)
            out.append(f'<rect x="{x:.1f}" y="{Y(val):.1f}" width="{bw}" height="{Y(0) - Y(val):.1f}" rx="2" fill="{col}"/>')
            out.append(text(x + bw / 2, Y(val) - 6, f"{B.fmt(val)}%", 10.5, col, "middle", 700))
        out.append(text(cx, Bm + 18, cat, 11, MUTED, "middle"))
    lx = L
    for name, col in (("หางล่าง (วันแย่สุด 10% ทั้งคู่)", C["red"]), ("หางบน (วันดีสุด 10% ทั้งคู่)", C["green"])):
        out.append(f'<rect x="{lx}" y="{T - 36}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 26, name, 11.5, MUTED))
        lx += 250
    alt = (f"แท่งคู่ห้ากลุ่ม โลกปกติหางล่าง {lo[0]}% หางบน {hi[0]}% ใกล้กัน โลกตกพร้อมกันหางล่าง {lo[1]}% สูงกว่าหางบน {hi[1]}% "
           f"BTC–ETH ช่วงเลือก {lo[2]}% กับ {hi[2]}% ช่วงตรวจ {lo[3]}% กับ {hi[3]}% และ 45 คู่เฉลี่ย {lo[4]}% กับ {hi[4]}%")
    return wrap(W, H, alt, out, "สองกลุ่มซ้ายเป็น 🎲 โลกจำลองที่รู้คำตอบ (มัธยฐาน 30 โลก ยาว 730 วัน · correlation 0.82 ทั้งคู่) · "
                "สามกลุ่มขวาเป็นการขยับ log รายวันจาก Binance spot (UTC)", "จริง")


@chart("sab2-cap-months")
def _cap_months(fig):
    o = fig["ch17"]["optionsจริง"]
    rows = o["ไม้"]
    base = [r["ไม่มีเพดาน"] for r in rows]
    cap = [r["มีเพดาน"] for r in rows]
    ticks = o["แกนกราฟ"]
    W, H, L, R, T, Bm = 760, 366, 64, 20, 96, 316
    lo, hi = ticks[0], ticks[-1]
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "short X ของ BTC–ETH ในช่วงตรวจ ไม้ละ 30 วัน: ไม่มีเพดาน เทียบ ซื้อ call BTC + put ETH", 13, INK, weight=700)]
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    gw = (W - L - R) / len(rows)
    bw = 15
    for i, r in enumerate(rows):
        cx = L + gw * i + gw / 2
        for j, (val, col) in enumerate(((base[i], C["grey"]), (cap[i], C["blue"]))):
            x = cx - bw - 1 + j * (bw + 2)
            y0, y1 = Y(0), Y(val)
            out.append(f'<rect x="{x:.1f}" y="{min(y0, y1):.1f}" width="{bw}" height="{max(1, abs(y1 - y0)):.1f}" rx="2" fill="{col}"/>')
        y, m = r["เริ่ม"][2:4], int(r["เริ่ม"][5:7])
        out.append(text(cx, Bm + 18, f"{TH_MONTH[m - 1]} {y}", 10.5, MUTED, "middle"))
    lx = L
    for name, col in (("ไม่มีเพดาน", C["grey"]), ("มี call BTC +10% และ put ETH −10% (หักค่าพรีเมียมแล้ว)", C["blue"])):
        out.append(f'<rect x="{lx}" y="{T - 34}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 24, name, 11.5, MUTED))
        lx += 130
    t = o["รวม"]
    out.append(text(16, 46, f"รวม 12 ไม้: ไม่มีเพดาน {B.fmt(t['ไม่มีเพดาน'])} · มีเพดาน +{B.fmt(t['มีเพดาน'])}", 11.5, INK, "start", 700))
    alt = (f"แท่งคู่สิบสองเดือน แท่งเทาไม่มีเพดาน แท่งน้ำเงินมี options เดือนที่ ETH ตกแรง แท่งน้ำเงินติดลบน้อยกว่า "
           f"เดือนที่นิ่ง แท่งน้ำเงินแย่กว่าเพราะค่าพรีเมียม รวมทั้งปีไม่มีเพดาน {t['ไม่มีเพดาน']} มีเพดาน {t['มีเพดาน']}")
    return wrap(W, H, alt, out, "ราคาปิดรายวัน Binance spot (UTC) ช่วงตรวจ · short BTC 0.01 long ETH 0.24 · ค่าพรีเมียมจากแบบจำลอง "
                "Black-Scholes ด้วยความผันผวนของช่วงเลือก ดอกเบี้ยศูนย์ ไม่ใช่ราคาตลาด · ไม่รวมค่าธรรมเนียม", "จริง")
