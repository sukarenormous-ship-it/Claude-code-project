"""บท 12 เล่ม 2 — จัดเงินหลายกลยุทธ์ · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json เท่านั้น)

sab2-mix-ratio      : ผลต่อความเสี่ยง (Mean ÷ SD) ของสองหน่วยที่แบ่งระหว่าง funding carry กับคู่ · หกเดือนสอน · ρ −0.5 / 0 / 0.5
sab2-weight-spread  : น้ำหนักคู่ที่ประมาณจาก 24 เดือนใน 30 โลกที่รู้คำตอบ · Mean–Variance เต็ม / หด Mean ครึ่งทาง / ไม่ใช้ Mean
sab2-kelly-curve    : เงินคูณเท่าไรหลังสิบตาของเกมฉลาก ตามสัดส่วนที่ยอมเสียในตาที่แย่ที่สุด · โอกาสที่เชื่อ เทียบโอกาสที่แย่กว่า
"""

from sab_charts import B, C, chart, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]


def _lines(xs, series, title, xlabel, yticks, xticks, marks, W=760, H=340, L=64, R=24, T=70, Bm=270):
    """เส้นหลายเส้นบนแกน y ที่กำหนดเอง (ป้ายแกนทุกตัวมาจาก JSON) · marks = [(x, y, ข้อความ)] จุดม่วง"""
    lo, hi = yticks[0], yticks[-1]
    x0, x1 = min(xs), max(xs)
    X = lambda x: L + (x - x0) / ((x1 - x0) or 1) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, title, 13, INK, weight=700)]
    for g in yticks:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 1 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for x, lab in xticks:
        out.append(text(X(x), Bm + 18, lab, 10.5, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 40, xlabel, 12, MUTED, "middle"))
    for name, s, col in series:
        pts = " ".join(f"{X(x):.1f},{Y(v):.1f}" for x, v in zip(xs, s))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/>')
    lx = L
    for name, _, col in series:
        out.append(f'<rect x="{lx}" y="{T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 20, name, 11.5, MUTED))
        lx += 34 + 7.2 * len(name)
    for x, y, lab in marks:
        out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="5" fill="{C["purple"]}"/>')
        right = X(x) > W * 0.6
        out.append(text(X(x) + (-9 if right else 9), Y(y) - 9, lab, 11.5, C["purple"], "end" if right else "start", 700))
    return out


@chart("sab2-mix-ratio")
def _mix_ratio(fig):
    c = fig["ch12"]["ผสม"]
    xs = [r["ส่วนคู่"] for r in c["เส้น"]]
    ser = [("ρ −0.5 (หกเดือนของบทนี้)", [r["-0.5"] for r in c["เส้น"]], C["blue"]),
           ("ρ 0", [r["0"] for r in c["เส้น"]], C["amber"]),
           ("ρ 0.5", [r["0.5"] for r in c["เส้น"]], C["red"])]
    best = c["ดีสุด"]
    share = best["P"] / (best["F"] + best["P"])
    marks = [(share, best["ratio"], f"funding {B.fmt(best['F'])} กับคู่ {B.fmt(best['P'])} หน่วย · {B.fmt(best['ratio'])}")]
    ticks = [(v / 100, f"{v}%") for v in c["แกน"]]
    parts = _lines(xs, ser, "ผลต่อความเสี่ยง (Mean ÷ SD) เมื่อแบ่งสองหน่วยระหว่าง funding carry กับคู่",
                   "ส่วนของคู่ในสองหน่วย", c["แกนy"], ticks, marks)
    alt = ("เส้นสามเส้นของผลต่อความเสี่ยงตามส่วนของคู่ เส้นน้ำเงินที่ correlation −0.5 ขึ้นสูงสุดราว 2.1 เมื่อคู่เป็นหนึ่งในสี่ "
           "เส้นส้มที่ correlation 0 สูงสุดราว 1.5 เส้นแดงที่ correlation 0.5 แทบไม่สูงกว่าการถือ funding carry อย่างเดียว "
           "และทุกเส้นลดลงเมื่อคู่เกินครึ่ง")
    return wrap(760, 340, alt, parts, "หกเดือนสอนของบทนี้ · funding carry Mean 3 SD 2.37 · คู่ Mean 6 SD 7.16 ต่อหน่วยต่อเดือน", "สอน")


@chart("sab2-weight-spread")
def _weight_spread(fig):
    w = fig["ch12"]["โลก"]
    true = w["จริง"]["น้ำหนักคู่ที่ถูกเปอร์เซ็นต์"]
    rows = [("Mean–Variance (ใช้ Mean ตามที่ประมาณ)", w["เต็ม"], C["blue"]),
            ("หด Mean ของสองงานเข้าหากันครึ่งทาง", w["หดครึ่ง"], C["amber"]),
            ("ไม่ใช้ Mean (ดูแค่ SD กับ correlation)", w["ไม่ใช้Mean"], C["green"])]
    W, H, L, R = 760, 268, 290, 40
    lo, hi = 0, max(r[1]["สูงสุด"] for r in rows) + 2
    X = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)  # noqa: E731
    out = [text(16, 28, f"น้ำหนักของคู่ที่ประมาณจาก {w['จริง']['เดือน']} เดือน ใน {w['โลก']} โลกที่รู้คำตอบ", 13, INK, weight=700)]
    top, bot = 62, 62 + 62 * len(rows) - 20
    out.append(f'<line x1="{X(true):.1f}" y1="{top - 14}" x2="{X(true):.1f}" y2="{bot + 6}" stroke="{C["purple"]}" '
               f'stroke-width="2" stroke-dasharray="5 4"/>')
    out.append(text(X(true) + 6, top - 18, f"คำตอบที่ถูก {B.fmt(true)}%", 11, C["purple"], "start", 700))
    for i, (name, r, col) in enumerate(rows):
        y = top + 20 + 62 * i
        out.append(text(16, y + 4, name, 11.5, INK))
        out.append(f'<line x1="{X(r["ต่ำสุด"]):.1f}" y1="{y}" x2="{X(r["สูงสุด"]):.1f}" y2="{y}" stroke="{col}" stroke-width="10" '
                   f'stroke-opacity=".3" stroke-linecap="round"/>')
        out.append(f'<line x1="{X(r["มัธยฐาน"]):.1f}" y1="{y - 10}" x2="{X(r["มัธยฐาน"]):.1f}" y2="{y + 10}" stroke="{col}" stroke-width="3"/>')
        out.append(text(X(r["มัธยฐาน"]) + 4, y + 25, f"มัธยฐาน {B.fmt(r['มัธยฐาน'])}%", 10.5, col, "end", 700))
        out.append(text(X(r["ต่ำสุด"]) - 8, y + 4, f"{B.fmt(r['ต่ำสุด'])}%", 10.5, GREY, "end"))
        out.append(text(X(r["สูงสุด"]) + 8, y + 4, f"{B.fmt(r['สูงสุด'])}%", 10.5, GREY))
    alt = (f"แถบช่วงสามแถบของน้ำหนักคู่ที่ประมาณได้ใน 30 โลก แบบใช้ Mean ตามที่ประมาณกว้างตั้งแต่ {w['เต็ม']['ต่ำสุด']} ถึง "
           f"{w['เต็ม']['สูงสุด']} เปอร์เซ็นต์ อีกสองแบบแคบกว่า ราว {w['หดครึ่ง']['ต่ำสุด']} ถึง {w['หดครึ่ง']['สูงสุด']} "
           f"เส้นประม่วงคือคำตอบที่ถูก {true} เปอร์เซ็นต์")
    return wrap(W, H, alt, out, f"30 โลก × {w['จริง']['เดือน']} เดือน · funding carry Mean 0.6% SD 0.7% · คู่ Mean 1% SD 6% · "
                "correlation −0.15 · แถบ = ต่ำสุดถึงสูงสุด", "จำลอง")


@chart("sab2-kelly-curve")
def _kelly_curve(fig):
    k = fig["ch12"]["ฉลาก"]
    xs = [r["f"] for r in k["เส้น"]]
    ser = [("โอกาสที่เชื่อ 0.5 / 0.3 / 0.2", [r["เชื่อ"] for r in k["เส้น"]], C["blue"]),
           ("โอกาสจริงแย่กว่า 0.45 / 0.35 / 0.2", [r["จริง"] for r in k["เส้น"]], C["red"])]
    full, half = k["Kelly"], k["ครึ่ง"]
    marks = [(full["f"], full["สิบตาเงิน"], f"Kelly {B.fmt(full['fเปอร์เซ็นต์'])}% · {B.fmt(full['สิบตาเงิน'])}"),
             (half["f"], half["สิบตาเงิน"], f"ครึ่ง Kelly {B.fmt(half['fเปอร์เซ็นต์'])}%")]
    ticks = [(v / 100, f"{v}%") for v in k["แกน"]]
    parts = _lines(xs, ser, "เงิน 100 เหลือเท่าไรหลังสิบตาที่ออกตามสัดส่วน", "ส่วนของเงินที่ยอมเสียในตาที่แย่ที่สุด", k["แกนy"],
                   ticks, marks)
    alt = ("เส้นน้ำเงินของเงินหลังสิบตาขึ้นจาก 100 สูงสุดที่ 14 เปอร์เซ็นต์ราว 105.8 แล้วลดลงต่ำกว่า 100 หลังราว 28 เปอร์เซ็นต์ "
           "เส้นแดงเมื่อโอกาสจริงแย่กว่าสูงสุดที่ราว 4 เปอร์เซ็นต์และต่ำกว่า 100 ที่ 14 เปอร์เซ็นต์")
    return wrap(760, 340, alt, parts, "เกมฉลากสิบใบของเล่ม 1 บท 2 (+4 / −2 / −5) · ขนาดตาเป็นสัดส่วนของเงินที่มี · สิบตาออกตามสัดส่วน", "สอน")
