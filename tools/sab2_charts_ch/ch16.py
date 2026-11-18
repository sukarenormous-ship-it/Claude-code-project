"""บท 16 เล่ม 2 — รวมหลายสัญญาณ และโมเดลที่เรียนรู้เอง · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json เท่านั้น)

sab2-blend-hand  : แปดวันด้วยมือ · คะแนนรวม (Z + funding) กับผล 5 วันข้างหน้า · เส้นผลที่คาด (ความชัน 0.5) · แถบที่ไม่คุ้มต้นทุนไปกลับ
sab2-blend-sim   : โลกจำลองที่รู้คำตอบ (30 โลก) · IC มัธยฐานช่วงเลือกเทียบช่วงตรวจ ของสัญญาณเดี่ยว · คะแนนรวม · Regression · ใส่ทุกอย่าง
sab2-blend-real  : ETH–BTC จริง · IC ช่วงเลือกเทียบช่วงตรวจ ของสามสัญญาณ · คะแนนรวม · Regression · ใส่ทุกอย่าง 12 ตัว · แถบโชคช่วงตรวจ
แกนทุกแกนมาจาก JSON (ch16.แกน) — ไม่ใช้ nice_ticks
"""

from sab_charts import B, C, chart, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]


def _ic_bars(cats, fvals, vvals, ticks, title, band=None):
    """แท่งคู่ (ช่วงเลือก · ช่วงตรวจ) ต่อหมวด · แกนจาก ticks · band = ครึ่งความกว้างแถบโชครอบศูนย์ (ช่วงตรวจ)"""
    W, H, L, R, T, Bm = 760, 350, 64, 24, 78, 296
    lo, hi = ticks[0], ticks[-1]
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 24, title, 13, INK, weight=700)]
    if band is not None:
        out.append(f'<rect x="{L}" y="{Y(band):.1f}" width="{W - L - R}" height="{Y(-band) - Y(band):.1f}" fill="{C["grid"]}" '
                   f'stroke="{C["axis"]}" stroke-dasharray="4 3"/>')
        out.append(text(W - R - 4, Y(-band) - 6, f"แถบที่โชคให้ได้ในช่วงตรวจ (±{B.fmt(band)})", 10.5, GREY, "end"))
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" '
                   f'stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    gw = (W - L - R) / len(cats)
    bw = min(34, (gw - 22) / 2)
    for i, cat in enumerate(cats):
        cx = L + gw * i + gw / 2
        for j, (v, col) in enumerate(((fvals[i], C["blue"]), (vvals[i], C["amber"]))):
            x = cx - (bw + 3) + j * (bw + 3)
            y0, y1 = Y(0), Y(v)
            out.append(f'<rect x="{x:.1f}" y="{min(y0, y1):.1f}" width="{bw:.1f}" height="{max(1, abs(y1 - y0)):.1f}" '
                       f'rx="2" fill="{col}"/>')
            out.append(text(x + bw / 2, (y1 - 5) if v >= 0 else (y1 + 13), B.fmt(v), 10, col, "middle", 700))
        for k, line in enumerate(cat.split("\n")):
            out.append(text(cx, Bm + 18 + 13 * k, line, 10.5, MUTED, "middle"))
    lx = L
    for name, col in (("ช่วงเลือก (ที่ใช้เรียน)", C["blue"]), ("ช่วงตรวจ (ปีถัดไป)", C["amber"])):
        out.append(f'<rect x="{lx}" y="{T - 34}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 24, name, 11.5, MUTED))
        lx += 40 + 7.4 * len(name)
    return W, H, out


@chart("sab2-blend-hand")
def _blend_hand(fig):
    c = fig["ch16"]["มือ"]
    ax = fig["ch16"]["แกน"]["มือ"]
    days = c["วัน"]
    slope, cut = c["ความชัน"], c["คะแนนต้องเกิน"]
    W, H, L, R, T, Bm = 760, 360, 70, 30, 60, 300
    xlo, xhi, ylo, yhi = ax["x"][0], ax["x"][-1], ax["y"][0], ax["y"][-1]
    X = lambda v: L + (v - xlo) / (xhi - xlo) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - ylo) / (yhi - ylo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "คะแนนรวมสูงกว่า ผลที่ตามมามักสูงกว่า แต่ไม่ใช่ทุกวัน", 13, INK, weight=700)]
    out.append(f'<rect x="{X(-cut):.1f}" y="{T}" width="{X(cut) - X(-cut):.1f}" height="{Bm - T}" fill="{C["grid"]}" '
               f'stroke="{C["axis"]}" stroke-dasharray="4 3"/>')
    out.append(text(X(0), T + 14, "ไม่คุ้มต้นทุน", 10.5, GREY, "middle", 700))
    for g in ax["y"]:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for g in ax["x"]:
        out.append(text(X(g), Bm + 18, B.fmt(g), 11, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 38, "คะแนนรวม (คะแนน Z + คะแนน funding)", 11.5, MUTED, "middle"))
    out.append(text(16, T - 8, "ผล 5 วันข้างหน้า (% ของขาหนึ่ง)", 11.5, MUTED))
    out.append(f'<line x1="{X(xlo):.1f}" y1="{Y(slope * xlo):.1f}" x2="{X(xhi):.1f}" y2="{Y(slope * xhi):.1f}" '
               f'stroke="{C["purple"]}" stroke-width="2.2" stroke-dasharray="7 4"/>')
    out.append(text(X(xhi) - 4, Y(slope * xhi) - 8, f"ผลที่คาด = {B.fmt(slope)} × คะแนน", 11, C["purple"], "end", 700))
    for d in days:
        col = C["green"] if d["ผล"] > 0 else C["red"]
        out.append(f'<circle cx="{X(d["รวมสอง"]):.1f}" cy="{Y(d["ผล"]):.1f}" r="5.5" fill="{col}"/>')
        right = d["รวมสอง"] < xhi - 0.5
        out.append(text(X(d["รวมสอง"]) + (8 if right else -8), Y(d["ผล"]) + (4 if right else -10), f"วัน {d['วัน']}", 10.5, col,
                        "start" if right else "end", 700))
    alt = ("จุดแปดจุดของแปดวัน แกนนอนคือคะแนนรวมจาก -2.5 ถึง 3 แกนตั้งคือผลห้าวันข้างหน้าจาก -2.4 ถึง 1.8 "
           "เส้นประม่วงคือผลที่คาดเท่ากับครึ่งหนึ่งของคะแนน แถบเทากลางคือคะแนนระหว่าง -0.4 ถึง 0.4 ที่ผลที่คาดไม่ถึงต้นทุนไปกลับ")
    return wrap(W, H, alt, out, "แปดวันตัวอย่างของบท · ผลที่คาดจากความชันของ Regression · ต้นทุนไปกลับ 0.2% ของขาหนึ่ง", "สอน")


@chart("sab2-blend-sim")
def _blend_sim(fig):
    s = fig["ch16"]["โลก"]
    ticks = fig["ch16"]["แกน"]["ICโลก"]
    names = [("Z", "IC_z"), ("funding\nจำลอง", "IC_f"), ("สำเนา\nของ Z", "IC_c"), ("รวมสอง\nZ + funding", "IC_รวมสอง"),
             ("รวมสาม\n(มีสำเนา)", "IC_รวมสาม"), ("Regression\n3 ตัว", "IC_Regression"), ("ใส่ทุกอย่าง\n20 ตัว", "IC_ใส่ทุกอย่าง")]
    W, H, out = _ic_bars([n for n, _ in names], [s[k]["ช่วงเลือก"] for _, k in names], [s[k]["ช่วงตรวจ"] for _, k in names],
                         ticks, "IC มัธยฐานของ 30 โลกที่รู้คำตอบ: รวมสองสัญญาณจริงชนะตัวเดียว ใส่ตัวสุ่มเพิ่มแล้วตกในปีถัดไป")
    alt = ("แท่งคู่เจ็ดหมวด สัญญาณเดี่ยวมี IC ราว 0.11 ถึง 0.14 ทั้งสองช่วง คะแนนรวม Z กับ funding ราว 0.21 ถึง 0.22 "
           "โมเดลใส่ทุกอย่าง 20 ตัวได้ 0.25 ในช่วงเลือกแต่เหลือ 0.16 ในช่วงตรวจ")
    return wrap(W, H, alt, out, "30 โลก · ชุดที่มีเชือก φ 0.97 · funding จำลองมีผลจริง · สำเนาของ Z · ตัวแปรสุ่ม 17 ตัว · "
                "เรียน 731 วัน ตรวจ 365 วัน", "จำลอง")


@chart("sab2-blend-real")
def _blend_real(fig):
    r = fig["ch16"]["จริง"]
    ticks = fig["ch16"]["แกน"]["ICจริง"]
    ic = r["IC"]
    cats = ["Z\n(60 วัน)", "funding\n(7 วัน)", "ส่วนที่เหลือ\n(20 วัน)", "รวมสาม", "Regression\n3 ตัว", "ใส่ทุกอย่าง\n12 ตัว"]
    fv = [ic["z"]["ช่วงเลือก"], ic["f"]["ช่วงเลือก"], ic["r"]["ช่วงเลือก"], r["ICรวม"]["รวมสาม"]["ช่วงเลือก"],
          r["Regression"]["ICช่วงเลือก"], r["ใส่ทุกอย่าง"]["สิบสอง"]["ICช่วงเลือก"]]
    vv = [ic["z"]["ช่วงตรวจ"], ic["f"]["ช่วงตรวจ"], ic["r"]["ช่วงตรวจ"], r["ICรวม"]["รวมสาม"]["ช่วงตรวจ"],
          r["Regression"]["ICช่วงตรวจ"], r["ใส่ทุกอย่าง"]["สิบสอง"]["ICช่วงตรวจ"]]
    W, H, out = _ic_bars(cats, fv, vv, ticks, "IC ของชุด ETH–BTC: ทุกแบบที่บวกในช่วงเลือก กลายเป็นลบในช่วงตรวจ",
                         band=r["สองเท่าสั่นเองช่วงตรวจ"])
    alt = ("แท่งคู่หกหมวด ช่วงเลือก Z กับส่วนที่เหลือบวกราว 0.14 ถึง 0.15 funding ราวศูนย์ โมเดลใส่ทุกอย่างบวก 0.36 "
           "ช่วงตรวจทุกแท่งอยู่ใต้ศูนย์หรือใกล้ศูนย์ และอยู่ในแถบที่โชคให้ได้")
    return wrap(W, H, alt, out, "ราคาปิดรายวัน Binance spot (UTC) · funding Deribit · ช่วงเลือก 2022-11-15 ถึง 2024-11-14 · "
                "ช่วงตรวจ 2024-11-15 ถึง 2025-11-14 · ผล 5 วันข้างหน้า", "จริง")


@chart("sab2-leak-timeline")
def _leak_timeline(fig):
    k = fig["ch16"]["รั่วมือ"]
    hz = fig["ch16"]["ค่า"]["ป้ายวัน"]
    days, last, test = k["วัน"], k["เรียนถึง"], k["ทดสอบ"]
    W, L, R, T, rh = 760, 160, 24, 96, 34
    H = T + rh * len(k["แถว"]) + 70
    dw = (W - L - R) / len(days)
    X = lambda d: L + (d - days[0]) * dw + dw / 2  # noqa: E731
    out = [text(16, 26, f"ป้ายคำตอบของแถววันที่ d ใช้ราคาปิดวันที่ d + {hz}: แถวท้ายช่วงเรียนรู้ป้ายหลังวันทดสอบ", 13, INK, weight=700)]
    yb = T + rh * len(k["แถว"])
    x0, x1 = X(days[0]) - dw / 2, X(last) + dw / 2
    out.append(f'<rect x="{x0:.1f}" y="{T - 30}" width="{x1 - x0:.1f}" height="{yb - T + 34:.1f}" fill="#dbeafe" fill-opacity="0.45"/>')
    out.append(text((x0 + x1) / 2, T - 14, f"ช่วงเรียน วันที่ {days[0]}–{last}", 11.5, C["blue"], "middle", 700))
    xt = X(test) - dw / 2
    out.append(f'<rect x="{xt:.1f}" y="{T - 30}" width="{dw:.1f}" height="{yb - T + 34:.1f}" fill="#fef3c7" stroke="{C["amber"]}"/>')
    out.append(text(X(test), T - 34, f"ทดสอบวันที่ {test}", 11.5, C["amber"], "middle", 700))
    for d in days:
        out.append(text(X(d), yb + 20, f"{d}", 10.5, GREY, "middle"))
    out.append(text((L + W - R) / 2, yb + 40, "วันที่ (ราคาปิด)", 11, GREY, "middle"))
    bad = 0
    for i, d in enumerate(k["แถว"]):
        y = T + rh * i + rh / 2
        known = d + hz
        ok = known <= last
        bad += 0 if ok else 1
        col = C["green"] if ok else C["red"]
        out.append(text(16, y - 2, f"แถวของวันที่ {d}", 11.5, INK, weight=700))
        out.append(text(16, y + 12, f"รู้ป้ายหลังปิดวันที่ {known}" + (" · ใช้ได้" if ok else " · ใช้ไม่ได้"), 10.5, col))
        out.append(f'<line x1="{X(d):.1f}" y1="{y:.1f}" x2="{X(known):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="5" stroke-linecap="round" stroke-opacity="0.75"/>')
        out.append(f'<rect x="{X(d) - 5:.1f}" y="{y - 5:.1f}" width="10" height="10" rx="2" fill="{C["blue"]}"/>')
        out.append(f'<circle cx="{X(known):.1f}" cy="{y:.1f}" r="5.5" fill="#ffffff" stroke="{col}" stroke-width="2.4"/>')
    ly = H - 12
    out.append(f'<rect x="16" y="{ly - 9}" width="10" height="10" rx="2" fill="{C["blue"]}"/>')
    out.append(text(32, ly, "วันตัดสินใจ (ตัวแปรทำนายรู้ได้)", 11, MUTED))
    out.append(f'<circle cx="262" cy="{ly - 4}" r="5" fill="#ffffff" stroke="{GREY}" stroke-width="2.2"/>')
    out.append(text(274, ly, f"วันที่ป้ายคำตอบรู้ได้ (ผล {hz} วันข้างหน้า)", 11, MUTED))
    out.append(text(W - R, ly, f"ต้องตัด {bad} แถวท้ายก่อนทดสอบ", 11.5, C["red"], "end", 700))
    alt = (f"เส้นเวลาวันที่ {days[0]} ถึง {days[-1]} ช่วงเรียนคือวันที่ {days[0]} ถึง {last} วันทดสอบคือ {test} "
           f"แถวของวันที่ {k['แถว'][0]} ถึง {k['แถว'][-1]} แต่ละแถวมีแท่งจากวันตัดสินใจไปถึงวันที่ป้ายคำตอบรู้ได้ {hz} วันถัดไป "
           f"แถวของวันที่ {k['แถว'][0]} รู้ได้วันที่ {k['แถว'][0] + hz} จึงใช้ได้ อีก {bad} แถวรู้ได้หลังวันทดสอบ จึงต้องตัดทิ้ง")
    return wrap(W, H, alt, out, f"ตัวอย่างของบท · ช่วงเรียนวันที่ {days[0]}–{last} · ทดสอบวันที่ {test} · ป้ายคำตอบคือผล {hz} วันข้างหน้า", "แนวคิด")
