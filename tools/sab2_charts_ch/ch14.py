"""บท 14 เล่ม 2 — ลองได้กี่ครั้งก่อนผลจะไม่มีความหมาย · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json เท่านั้น)

sab2-wf-hand      : ผัง walk-forward ของตารางมือ สามเส้น × ห้าช่วง · แต่ละแถวคือหนึ่งหน้าต่าง (ช่วงเลือกสองช่วง → ช่วงทดสอบหนึ่งช่วง)
sab2-grid-scatter : 25 แบบของ LTC–DOT · แกนนอนผลช่วงเลือก แกนตั้งผลช่วงตรวจ · ยอดเขา การ์ด และยอดของช่วงตรวจ
sab2-wf-worlds    : ที่ช่วงเลือกสัญญา เทียบ walk-forward ได้จริง · โลกมีเชือก · โลกไม่มีเชือก (มัธยฐาน 30 โลก) · LTC–DOT
"""

from sab_charts import B, C, chart, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]


@chart("sab2-wf-hand")
def _wf_hand(fig):
    h = fig["ch14"]["มือ"]
    wins = h["เดินหน้า"]["หน้าต่าง"]
    n = h["ช่วง"]
    W, H, L, T = 760, 330, 150, 78
    cw, ch, gap = 112, 46, 16
    out = [text(16, 26, "Walk-forward สามหน้าต่าง: เลือกจากสองช่วงล่าสุด แล้วใช้กับช่วงถัดไป", 13, INK, weight=700)]
    for j in range(n):
        out.append(text(L + j * cw + cw / 2, T - 12, f"ช่วง {j + 1}", 11.5, GREY, "middle", 700))
    for i, w in enumerate(wins):
        y = T + i * (ch + gap)
        out.append(text(16, y + ch / 2 + 4, f"หน้าต่าง {i + 1}", 12, INK, weight=700))
        a, b = [int(x) for x in w["ช่วงเลือก"].split("–")]
        for j in range(n):
            if not (a <= j + 1 <= b) and j + 1 != w["ช่วงทดสอบ"]:
                out.append(f'<rect x="{L + j * cw + 3}" y="{y}" width="{cw - 6}" height="{ch}" rx="6" fill="{C["grid"]}"/>')
        x0, x1 = L + (a - 1) * cw + 3, L + b * cw - 3
        out.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{ch}" rx="6" fill="#dbeafe" stroke="{C["blue"]}"/>')
        out.append(text((x0 + x1) / 2, y + 18, f"ช่วงเลือก {w['ช่วงเลือก']}", 11, C["blue"], "middle", 700))
        out.append(text((x0 + x1) / 2, y + 36, f"ชนะ: เส้น {w['เลือก']} (รวม {B.fmt(w['รวม'][str(w['เลือก'])])})", 11, C["blue"], "middle"))
        xt = L + (w["ช่วงทดสอบ"] - 1) * cw
        out.append(f'<rect x="{xt + 3}" y="{y}" width="{cw - 6}" height="{ch}" rx="6" fill="#fef3c7" stroke="{C["amber"]}"/>')
        v = w["ผลทดสอบ"]
        out.append(text(xt + cw / 2, y + 18, f"ใช้เส้น {w['เลือก']}", 11, C["amber"], "middle", 700))
        out.append(text(xt + cw / 2, y + 36, f"ได้ {B.fmt(v)}", 12, C["green"] if v > 0 else C["red"], "middle", 700))
    yb = T + len(wins) * (ch + gap) + 14
    tot = h["เดินหน้า"]["รวม"]
    out.append(text(16, yb + 8, f"รวมสามช่วงทดสอบ {B.fmt(tot)} · ช่วงเลือกสัญญาไว้ {B.fmt(h['เดินหน้า']['สัญญา'])}",
                    12.5, C["red"] if tot < 0 else C["green"], weight=700))
    alt = ("ผังห้าช่วงเรียงซ้ายไปขวา สามแถวคือสามหน้าต่าง แต่ละแถวมีช่วงเลือกสองช่วงสีฟ้าและช่วงทดสอบหนึ่งช่วงสีส้มต่อท้าย "
           "หน้าต่าง 1 เลือกเส้น 1 ได้ −20 หน้าต่าง 2 เลือกเส้น 3 ได้ −10 หน้าต่าง 3 เลือกเส้น 2 ได้ 10 รวม −20")
    return wrap(W, H, alt, out, "สามเส้น × ห้าช่วง (ตัวเลขสอน) · ช่วงเลือกยาวสองช่วง ช่วงทดสอบยาวหนึ่งช่วง", "สอน")


@chart("sab2-grid-scatter")
def _grid_scatter(fig):
    r = fig["ch14"]["จริง"]
    cells = list(r["ช่อง"].values())
    xt, yt = r["แกนกราฟ"]["x"], r["แกนกราฟ"]["y"]
    W, H, L, R, T, Bm = 760, 380, 76, 30, 60, 320
    X = lambda v: L + (v - xt[0]) / (xt[-1] - xt[0]) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - yt[0]) / (yt[-1] - yt[0]) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "25 แบบของ LTC–DOT: ผลในช่วงเลือก เทียบผลในช่วงตรวจ (ทุนเริ่ม 1,000 · 10 ชุด)", 13, INK, weight=700)]
    for g in yt:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for g in xt:
        out.append(f'<line x1="{X(g):.1f}" y1="{T}" x2="{X(g):.1f}" y2="{Bm}" stroke="{C["grid"]}"/>')
        out.append(text(X(g), Bm + 18, B.fmt(g), 11, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 38, "ผลในช่วงเลือก (2022-11-15 ถึง 2024-11-14)", 11.5, MUTED, "middle"))
    out.append(text(L, T - 10, "ผลในช่วงตรวจ (2024-11-15 ถึง 2025-11-14)", 11.5, MUTED))
    pk, vb, cd = r["ยอด"], r["ยอดตรวจ"], r["การ์ด"]
    special = {(pk["เส้น"], pk["ถือ"]), (vb["เส้น"], vb["ถือ"]), (cd["เส้น"], cd["ถือ"])}
    for c in cells:
        if (c["เส้น"], c["ถือ"]) in special:
            continue
        out.append(f'<circle cx="{X(c["เลือก"]):.1f}" cy="{Y(c["ตรวจ"]):.1f}" r="5" fill="{C["blue"]}" fill-opacity="0.55"/>')
    marks = [(pk, f"ยอดเขาช่วงเลือก: เส้น {B.fmt(pk['เส้น'])} ถือ {pk['ถือ']} วัน", C["purple"], pk["เลือก"], pk["ตรวจ"], "end", -12),
             (vb, f"ยอดของช่วงตรวจ: เส้น {B.fmt(vb['เส้น'])} ถือ {vb['ถือ']} วัน", C["amber"], vb["เลือก"], vb["ตรวจ"], "start", -12),
             (cd, f"การ์ดเดิม: เส้น {B.fmt(cd['เส้น'])} ถือ {cd['ถือ']} วัน", C["green"], cd["เลือก"], cd["ตรวจ"], "start", -9)]
    for _, lab, col, x, y, anc, dy in marks:
        out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="7" fill="{col}"/>')
        dx = -10 if anc == "end" else 10
        out.append(text(X(x) + dx, Y(y) + dy, f"{lab} ({B.fmt(x)} → {B.fmt(y)})", 11, col, anc, 700))
    alt = ("จุด 25 จุด แกนนอนคือผลในช่วงเลือก แกนตั้งคือผลในช่วงตรวจ จุดยิ่งไปทางขวายิ่งลงต่ำ "
           "ยอดเขาของช่วงเลือกอยู่ขวาสุดแต่ต่ำสุดในช่วงตรวจ ส่วนยอดของช่วงตรวจอยู่กลางกลุ่มในช่วงเลือก")
    return wrap(W, H, alt, out, "ราคาปิดรายวัน Binance spot (UTC) · LTC บน DOT h 3.76 ไม้บรรทัดจากช่วงเลือก · "
                "เส้นเข้า 1 ถึง 3 × ถือไม่เกิน 10 ถึง 60 วัน · ออกที่ Z 0.5 · ได้ราคาปิดวันถัดไป · ค่าธรรมเนียม 0.05% ต่อ fill", "จริง")


@chart("sab2-wf-worlds")
def _wf_worlds(fig):
    c = fig["ch14"]
    sim, wf = c["จำลอง"], c["จริง"]["เดินหน้า"]
    cats = ["🎲 โลกมีเชือก (มัธยฐาน 30 โลก)", "🎲 โลกไม่มีเชือก (มัธยฐาน 30 โลก)", "📡 LTC–DOT (เส้นทางเดียว)"]
    promise = [sim["มีเชือก"]["สัญญามัธยฐาน"], sim["ไม่มีเชือก"]["สัญญามัธยฐาน"], wf["สัญญารวม"]]
    got = [sim["มีเชือก"]["เดินหน้ามัธยฐาน"], sim["ไม่มีเชือก"]["เดินหน้ามัธยฐาน"], wf["รวม"]]
    ticks = c["แกนกราฟโลก"]
    W, H, L, R, T, Bm = 760, 350, 70, 24, 70, 290
    lo, hi = ticks[0], ticks[-1]
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "ที่ช่วงเลือกสัญญาไว้ เทียบกับที่ walk-forward ได้จริงในช่วงทดสอบ (363 วัน)", 13, INK, weight=700)]
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    lx = L
    for name, col in (("ที่ช่วงเลือกสัญญา (ผลของแบบที่ชนะ ย่อเหลือ 121 วันต่อหน้าต่าง)", C["grey"]), ("walk-forward ได้จริง", C["blue"])):
        out.append(f'<rect x="{lx}" y="{T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 20, name, 11.5, MUTED))
        lx += 40 + 6.4 * len(name)
    gw = (W - L - R) / len(cats)
    bw = 70
    for i, (cat, a, b) in enumerate(zip(cats, promise, got)):
        x0 = L + i * gw + gw / 2 - bw - 4
        for j, (v, col) in enumerate(((a, C["grey"]), (b, C["blue"] if b >= 0 else C["red"]))):
            x = x0 + j * (bw + 8)
            y1, y2 = sorted((Y(0), Y(v)))
            out.append(f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw}" height="{max(y2 - y1, 1):.1f}" rx="3" fill="{col}"/>')
            ty = Y(v) - 6 if v >= 0 else Y(v) + 15
            out.append(text(x + bw / 2, ty, B.fmt(v), 11.5, INK, "middle", 700))
        out.append(text(L + i * gw + gw / 2, Bm + 22, cat, 11, MUTED, "middle"))
    alt = ("แท่งคู่สามกลุ่ม แท่งเทาคือที่ช่วงเลือกสัญญา แท่งน้ำเงินหรือแดงคือที่ walk-forward ได้จริง "
           "โลกมีเชือกสัญญาราว 219 ได้ราว 74 โลกไม่มีเชือกสัญญาราว 195 ได้ติดลบราว 33 ส่วน LTC–DOT สัญญาราว 531 ได้ราว 209")
    return wrap(W, H, alt, out, "walk-forward สามหน้าต่าง: ช่วงเลือก 365 วัน → ช่วงทดสอบ 121 วัน · เลือก h ไม้บรรทัด และแบบจาก 25 แบบในทุกหน้าต่าง · "
                "10 ชุด · ค่าธรรมเนียม 0.05% ต่อ fill · โลกจำลองเป็นคู่บนราคาแบบบท 7 (SD นิ่งของ X = 3)", "จำลอง")
