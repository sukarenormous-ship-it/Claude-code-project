"""บท 17 เล่ม 2 — ความสัมพันธ์ไม่เป็นเส้นตรง และ options · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json เท่านั้น)

sab2-copula-grid : ตาราง 5 × 5 ของอันดับ BTC กับ ETH (การขยับ log รายวัน ช่วงเลือก 730 วัน · กลุ่มละ 146 วัน)
sab2-tail-bars   : วันที่ 10% ล่าง / 10% บน ไปด้วยกันกี่เปอร์เซ็นต์ · โลกปกติ · โลกตกพร้อมกัน · BTC–ETH สองช่วง · 45 คู่
sab2-cap-months  : 12 ไม้ short X ของ BTC–ETH ในช่วงตรวจ · ไม่มีเพดาน เทียบ มี call BTC + put ETH (ราคาจากแบบจำลอง)
"""

from sab_charts import B, C, chart, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]
def _i(v):
    return int(v) if float(v).is_integer() else v


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


@chart("sab2-two-copulas")
def _two_copulas(fig):
    m = fig["ch17"]["มือ"]
    n, g = m["n"], m["กลุ่ม"]
    per = m["วันต่อกลุ่ม"]
    W, H = 760, 412
    side, T = 250, 74
    panels = [("ตกพร้อมกัน", "โลกตกพร้อมกัน", 90), ("หางแยก", "โลกหางแยก", 450)]
    out = [text(16, 26, f"สองโลก Rank Correlation {B.fmt(m['ตกพร้อมกัน']['rank'])} เท่ากัน แต่วันที่ A แย่สุด B ไปคนละทาง", 13, INK, weight=700)]
    cell = side / g
    for key, name, L in panels:
        w = m[key]
        P = lambda r: (r - 0.5) / n * side  # noqa: E731
        out.append(text(L, T - 18, name, 12.5, INK, weight=700))
        for i in range(g):
            for j in range(g):
                fill = "#fee2e2" if (i, j) == (0, 0) else ("#f9fafb" if (i + j) % 2 else "#ffffff")
                out.append(f'<rect x="{L + j * cell:.1f}" y="{T + side - (i + 1) * cell:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
                           f'fill="{fill}" stroke="{C["grid"]}"/>')
        out.append(f'<rect x="{L}" y="{T}" width="{side}" height="{side}" fill="none" stroke="{C["axis"]}"/>')
        out.append(f'<rect x="{L:.1f}" y="{T + side - cell:.1f}" width="{side:.1f}" height="{cell:.1f}" fill="none" '
                   f'stroke="{C["red"]}" stroke-width="1.4" stroke-dasharray="4 3"/>')
        for r in (1, n):
            out.append(text(L + P(r), T + side + 16, f"{r}", 10.5, GREY, "middle"))
            out.append(text(L - 8, T + side - P(r) + 4, f"{r}", 10.5, GREY, "end"))
        out.append(text(L + side / 2, T + side + 32, "อันดับของ B (1 = แย่สุด)", 11, MUTED, "middle"))
        out.append(text(L - 8, T - 4, "อันดับ A", 11, MUTED, "end"))
        worst = set(w["วันแย่สุดของA"])
        for d in w["วัน"]:
            col = C["red"] if d["วัน"] in worst else C["blue"]
            cx, cy = L + P(d["อันดับB"]), T + side - P(d["อันดับA"])
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6.5" fill="{col}" fill-opacity="0.85"/>')
            if d["วัน"] in worst:
                out.append(text(cx + 10, cy + 4, f"วัน {d['วัน']}", 10.5, col, "start", 700))
        k_ = w["ไปด้วยกันล่าง"]
        out.append(text(L, T + side + 54, f"B แย่สุดด้วย {k_} จาก {per} วัน ({B.fmt(w['ความน่าจะเป็นล่าง'])}%)", 12, C["red"] if k_ == 0 else INK, weight=700))
        tot = w["คู่ในวันแย่สุดรวม"]
        out.append(text(L, T + side + 72, f"long A short B ในสองวันนั้น: {'+' if tot > 0 else ''}{B.fmt(tot)}", 11.5,
                        C["green"] if tot > 0 else C["red"], weight=700))
    alt = (f"สองแผงของจุดสิบจุด แกนนอนคืออันดับของ B แกนตั้งคืออันดับของ A จุดแดงคือวันที่ A แย่สุดสองวัน "
           f"โลกตกพร้อมกันจุดแดงอยู่ในช่องมุมล่างซ้ายที่ B แย่สุดด้วยทั้ง {m['ตกพร้อมกัน']['ไปด้วยกันล่าง']} วัน ชุด long A short B ได้ {B.fmt(m['ตกพร้อมกัน']['คู่ในวันแย่สุดรวม'])} "
           f"โลกหางแยกจุดแดงหลุดออกนอกช่อง {m['หางแยก']['ไปด้วยกันล่าง']} วันในช่อง ชุดเสีย {B.fmt(m['หางแยก']['คู่ในวันแย่สุดรวม'])} ทั้งที่ Rank Correlation {B.fmt(m['ตกพร้อมกัน']['rank'])} เท่ากัน")
    return wrap(W, H, alt, out, f"สิบวันตัวอย่างของบท · ห้ากลุ่ม กลุ่มละ {per} วัน · โลกหางแยกสลับ B สี่วัน (วันที่ 2, 4, 6 และ 9)", "สอน")


@chart("sab2-cap-payoff")
def _cap_payoff(fig):
    t = fig["ch17"]["ต้นไม้"]
    cp = t["เพดาน"]
    rows = cp["แถว"]
    ticks = fig["ch17"]["แกนเพดาน"]
    start = t["ราคาเริ่ม"]
    strike = start + cp["ห่างราคาใช้สิทธิ์"]
    W, H, L, R, T, Bm = 760, 350, 64, 30, 70, 290
    xa, xb = rows[0]["A"], rows[-1]["A"]
    X = lambda a: L + (a - xa) / (xb - xa) * (W - L - R)  # noqa: E731
    lo, hi = ticks[0] - 6, ticks[-1] + 6
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, f"short A ที่ {start} คู่กับ Call ราคาใช้สิทธิ์ {strike}: ขาดทุนหยุดที่ −{B.fmt(_i(cp['ขาดทุนสูงสุด']))}", 13, INK, weight=700)]
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for r in rows:
        out.append(text(X(r["A"]), Bm + 18, f"{r['A']}", 10.5, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 38, "ราคา A วันหมดอายุ", 11, GREY, "middle"))
    out.append(text(L, T - 14, "ผลรวม ณ วันหมดอายุ (ดอลลาร์)", 11, GREY))
    out.append(f'<line x1="{X(strike):.1f}" y1="{T}" x2="{X(strike):.1f}" y2="{Bm}" stroke="{INK}" stroke-dasharray="3 3"/>')
    out.append(text(X(strike) + 6, T + 12, f"ราคาใช้สิทธิ์ {strike}", 11, INK, "start", 700))
    short = " ".join(f"{X(r['A']):.1f},{Y(r['short']):.1f}" for r in rows)
    capd = " ".join(f"{X(r['A']):.1f},{Y(r['รวม']):.1f}" for r in rows)
    out.append(f'<polyline points="{short}" fill="none" stroke="{GREY}" stroke-width="2.2" stroke-dasharray="7 5"/>')
    out.append(f'<polyline points="{capd}" fill="none" stroke="{C["blue"]}" stroke-width="2.8" stroke-linejoin="round"/>')
    last = rows[-1]
    out.append(text(X(last["A"]) - 4, Y(last["short"]) + 14, f"short อย่างเดียว: {B.fmt(_i(cp['ไม่มีเพดานที่140']))}", 11, GREY, "end", 700))
    out.append(text(X(last["A"]) - 4, Y(last["รวม"]) - 10, f"มี Call: −{B.fmt(_i(cp['ขาดทุนสูงสุด']))} ทุกราคาตั้งแต่ {strike}", 11, C["blue"], "end", 700))
    first = rows[0]
    xg = (first["A"] + strike) / 2
    yg_s, yg_c = start - xg, start - xg - cp["พรีเมียม"]
    out.append(f'<line x1="{X(xg):.1f}" y1="{Y(yg_s) + 3:.1f}" x2="{X(xg):.1f}" y2="{Y(yg_c) - 3:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    out.append(text(X(xg) - 8, Y(yg_c) + 24, f"ห่างกัน {B.fmt(_i(cp['พรีเมียม']))} = ค่าพรีเมียมที่จ่าย", 11, INK, "end", 700))
    lx = W - R - 330
    out.append(f'<line x1="{lx}" y1="{T - 18}" x2="{lx + 22}" y2="{T - 18}" stroke="{GREY}" stroke-width="2.2" stroke-dasharray="7 5"/>')
    out.append(text(lx + 28, T - 14, "short A อย่างเดียว", 11, MUTED))
    out.append(f'<line x1="{lx + 150}" y1="{T - 18}" x2="{lx + 172}" y2="{T - 18}" stroke="{C["blue"]}" stroke-width="2.8"/>')
    out.append(text(lx + 178, T - 14, f"short A + Call (จ่าย {B.fmt(_i(cp['พรีเมียม']))})", 11, MUTED))
    alt = (f"แกนนอนคือราคา A วันหมดอายุจาก {xa} ถึง {xb} เส้นประเทาคือ short A อย่างเดียว จาก +{B.fmt(first['short'])} ลงไป {B.fmt(_i(cp['ไม่มีเพดานที่140']))} "
           f"เส้นน้ำเงินคือ short A คู่กับ Call ราคาใช้สิทธิ์ {strike} หักค่าพรีเมียม {B.fmt(_i(cp['พรีเมียม']))} แล้ว ลงไปหยุดที่ −{B.fmt(_i(cp['ขาดทุนสูงสุด']))} ตั้งแต่ราคา {strike} ขึ้นไป")
    return wrap(W, H, alt, out, f"ตัวเลขกลมของบท · A เริ่มที่ {start} · Call ราคาใช้สิทธิ์ {strike} ค่าพรีเมียม {B.fmt(_i(cp['พรีเมียม']))} จากต้นไม้สองทาง ±20", "สอน")
