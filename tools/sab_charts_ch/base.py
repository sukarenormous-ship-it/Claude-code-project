"""ภาคพื้นฐาน "คืนก่อนวันที่ 1" (docs/sab-base1..4.html · แผน 14.5) — สเปกกราฟของหน้าพื้นฐาน

ปลั๊กอินของ tools/sab_charts.py (โหลดก่อน ch00) · คีย์กราฟขึ้นต้น sab-base- · ตัวเลขอ่านจาก fig["base"]
สีประจำขาเหมือนกันทุกหน้า: ขา A = น้ำเงิน · ขา B = ส้ม · ผลรวม/ผลสุทธิ = เขียว (ได้) / แดง (เสีย) หรือเทาเข้ม (ผลรวมของชุด)
สัญญาที่มีวันหมดอายุ (หน้า 4) = ม่วงเส้นประ · เส้นอ้างอิง = เทา
แกนทุกแกนใช้ค่าจาก JSON (ไม่ใช้ nice_ticks) เพื่อให้ป้ายแกนไม่กลายเป็นเลขลอย
"""
from sab_charts import chart, wrap, text, C, B

LEG = {"A": C["blue"], "B": C["amber"], "รวม": C["ink"], "สัญญา": C["purple"]}


def _sign(v):
    return ("+" if v > 0 else "") + B.fmt(v)


def _legend(x, y, items):
    out = []
    for name, col, kind in items:
        if kind == "line":
            out.append(f'<line x1="{x}" y1="{y - 4}" x2="{x + 18}" y2="{y - 4}" stroke="{col}" stroke-width="2.5"/>')
        elif kind == "dash":
            out.append(f'<line x1="{x}" y1="{y - 4}" x2="{x + 18}" y2="{y - 4}" stroke="{col}" stroke-width="2.5" '
                       f'stroke-dasharray="5 3"/>')
        else:
            out.append(f'<rect x="{x}" y="{y - 10}" width="12" height="12" rx="2" fill="{col}"/>')
        out.append(text(x + 24, y, name, 11.5, C["muted"]))
        x += 34 + 7.2 * len(name)
    return out


class Axis:
    """แกน y เชิงเส้นในช่วง [lo, hi] บนพื้นที่ top..bottom"""

    def __init__(self, lo, hi, top, bottom):
        self.lo, self.hi, self.top, self.bottom = lo, hi, top, bottom

    def y(self, v):
        return self.bottom - (v - self.lo) / (self.hi - self.lo) * (self.bottom - self.top)


def _grid(ax, ticks, x0, x1, label=True):
    out = []
    for t in ticks:
        yy = ax.y(t)
        out.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="{C["axis"] if t == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if t == 0 else 1}"/>')
        if label:
            out.append(text(x0 - 8, yy + 4, B.fmt(t), 11, C["grey"], "end"))
    return out


# ───────── หน้า 1: เงินที่ออกและเข้าของขา A กับผลที่เหลือ ─────────
@chart("sab-base-long-cash")
def _long_cash(fig):
    b = fig["base"]["b1"]
    one, two = b["หนึ่งหน่วย"], b["สองหน่วย"]
    ticks = b["แกนกราฟ"]
    W, H = 760, 360
    ax = Axis(min(ticks), max(ticks), 92, 300)
    out = [text(24, 26, "เงินที่ออกและเข้าดูใหญ่ แต่ผลที่เหลือจริงเล็กกว่ามาก", 13.5, C["ink"], weight=700)]
    out += _legend(24, 52, [("เงินของขา A ที่ออก/เข้า", LEG["A"], "box"), ("ผลได้", C["green"], "box"),
                            ("ผลเสีย", C["red"], "box")])
    panels = [(70, f"(ก) {one['จำนวน']} หน่วย · ซื้อ {B.fmt(one['ราคาซื้อ'])} ขาย {B.fmt(one['ราคาขาย'])}", one),
              (430, f"(ข) {two['จำนวน']} หน่วย · ซื้อ {B.fmt(two['ราคาซื้อ'])} ขาย {B.fmt(two['ราคาขาย'])}", two)]
    for x0, title, t in panels:
        x1 = x0 + 300
        out += _grid(ax, ticks, x0, x1, label=(x0 == 70))
        out.append(text(x0, 80, title, 12, C["ink"], weight=700))
        bars = [("จ่ายตอนซื้อ", -t["จ่าย"], LEG["A"]), ("รับตอนขาย", t["รับ"], LEG["A"]),
                ("ผลที่เหลือ", t["ผล"], C["green"] if t["ผล"] >= 0 else C["red"])]
        gw, bw = 100, 46
        for k, (name, v, col) in enumerate(bars):
            cx = x0 + gw * k + gw / 2
            y0, y1 = ax.y(0), ax.y(v)
            h = max(2.5, abs(y1 - y0))
            top = min(y0, y1) if abs(y1 - y0) >= 2.5 else (y0 - 2.5 if v >= 0 else y0)
            out.append(f'<rect x="{cx - bw / 2:.1f}" y="{top:.1f}" width="{bw}" height="{h:.1f}" rx="3" fill="{col}"/>')
            ly = (top - 7) if v >= 0 else (top + h + 15)
            out.append(text(cx, ly, _sign(v), 12, C["ink"], "middle", 700))
            out.append(text(cx, 324, name, 11.5, C["muted"], "middle"))
        hold = f"ถือ A {t['จำนวน']} หน่วยระหว่างนี้"
        out.append(text(x0 + 150, 342, hold, 11, C["grey"], "middle"))
    alt = (f"กราฟแท่งสองแผง แผงซ้ายซื้อ A {one['จำนวน']} หน่วยที่ {one['ราคาซื้อ']} จ่าย {one['จ่าย']} ขายที่ {one['ราคาขาย']} "
           f"รับ {one['รับ']} ผลได้ {one['ผล']} แผงขวาซื้อ {two['จำนวน']} หน่วยที่ {two['ราคาซื้อ']} จ่าย {two['จ่าย']} "
           f"ขายที่ {two['ราคาขาย']} รับ {two['รับ']} ผลเสีย {abs(two['ผล'])}")
    cap = "ยังไม่คิดค่าธรรมเนียม · แท่งน้ำเงินคือเงินที่เดินจริง แท่งสุดท้ายคือรับลบจ่าย"
    return wrap(W, H, alt, out, cap, "สอน")


# ───────── หน้า 2: ผลของการขายก่อน B หนึ่งหน่วย ตามราคาที่ซื้อคืน ─────────
@chart("sab-base-short-line")
def _short_line(fig):
    b = fig["base"]["b2"]
    xs, short, long_ = b["แกนราคา"], b["กราฟ"]["short1"], b["กราฟ"]["long1"]
    W, H = 760, 340
    L, R = 70, 730
    ticks = sorted(set(short))
    ax = Axis(min(ticks) - 0.5, max(ticks) + 0.5, 84, 282)
    X = lambda p: L + (p - xs[0]) / (xs[-1] - xs[0]) * (R - L)  # noqa: E731
    out = [text(24, 26, "ขาย B ไว้ก่อนที่ 50: ราคาที่ต้องซื้อคืนยิ่งสูง ผลยิ่งติดลบ", 13.5, C["ink"], weight=700)]
    out += _legend(24, 52, [("ขายก่อน B 1 หน่วย", LEG["B"], "line"), ("เทียบ: ซื้อไว้ก่อน B 1 หน่วย", C["grey"], "dash")])
    out += _grid(ax, ticks, L, R)
    x50 = X(b["B"])
    out.append(f'<line x1="{x50:.1f}" y1="{ax.top - 6}" x2="{x50:.1f}" y2="{ax.bottom}" stroke="{C["grey"]}" '
               f'stroke-dasharray="3 3" stroke-width="1"/>')
    out.append(text(x50 + 6, ax.top + 4, f"ราคาที่ขายไว้ {B.fmt(b['B'])}", 11, C["muted"]))
    pts = lambda ys: " ".join(f"{X(p):.1f},{ax.y(v):.1f}" for p, v in zip(xs, ys))  # noqa: E731
    out.append(f'<polyline points="{pts(long_)}" fill="none" stroke="{C["grey"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    out.append(f'<polyline points="{pts(short)}" fill="none" stroke="{LEG["B"]}" stroke-width="2.6" stroke-linecap="round"/>')
    for key, dx, anchor in (("ขึ้น", 10, "start"), ("ลง", -10, "end")):
        t = b["ตกลงขาย"][key]
        cx, cy = X(t["ราคาซื้อคืน"]), ax.y(t["ผล"])
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="{LEG["B"]}" stroke="#fff" stroke-width="2"/>')
        lab = f"ซื้อคืนที่ {B.fmt(t['ราคาซื้อคืน'])}: {_sign(t['ผล'])}"
        out.append(text(cx + dx, cy - 10 if t["ผล"] > 0 else cy + 20, lab, 12, C["ink"], anchor, 700))
    for p in xs:
        out.append(text(X(p), ax.bottom + 18, B.fmt(p), 11, C["grey"], "middle"))
    out.append(text((L + R) / 2, ax.bottom + 40, "ราคา B ตอนซื้อคืน (ปิด)", 12, C["muted"], "middle"))
    out.append(text(L - 50, ax.top - 14, "ผล", 11.5, C["muted"]))
    alt = ("กราฟเส้นผลของการขาย B ไว้ก่อนที่ 50 หนึ่งหน่วย เทียบกับราคาที่ซื้อคืนตั้งแต่ 47 ถึง 53 เส้นลาดลง "
           "ซื้อคืนที่ 51 เสีย 1 ซื้อคืนที่ 49 ได้ 1 เส้นประเทาคือการซื้อไว้ก่อนซึ่งลาดขึ้นตรงข้ามกัน")
    cap = "ยังไม่คิดค่าธรรมเนียม · หนึ่งหน่วย · ทุกจุดเริ่มจากการขายที่ 50 เหมือนกัน"
    return wrap(W, H, alt, out, cap, "สอน")


# ───────── หน้า 3: สี่ตอนจบจากจุดเปิดเดียวกัน ─────────
@chart("sab-base-four-endings")
def _four_endings(fig):
    b = fig["base"]["b3"]
    ends, ticks = b["ตอนจบ"], b["แกนกราฟ"]
    W, H = 760, 370
    L, R = 70, 740
    ax = Axis(min(ticks) - 0.6, max(ticks) + 0.6, 92, 288)
    out = [text(24, 26, "จุดเปิดเดียว สี่ตอนจบ: มีสองขาไม่ได้แปลว่าปลอดภัย", 13.5, C["ink"], weight=700)]
    out += _legend(24, 52, [("ขา A (ซื้อ 1 หน่วยที่ 100)", LEG["A"], "box"), ("ขา B (ขาย 2 หน่วยที่ 50)", LEG["B"], "box"),
                            ("รวมทั้งชุด", LEG["รวม"], "box")])
    out += _grid(ax, ticks, L, R)
    gw = (R - L) / len(ends)
    bw = 34
    for i, e in enumerate(ends):
        cx = L + gw * i + gw / 2
        for j, (key, col) in enumerate((("ขาA", LEG["A"]), ("ขาB", LEG["B"]), ("รวม", LEG["รวม"]))):
            v = e[key]
            x = cx - 1.5 * (bw + 6) + j * (bw + 6)
            y0, y1 = ax.y(0), ax.y(v)
            h = max(2.5, abs(y1 - y0))
            top = min(y0, y1) if v != 0 else y0 - 1.25
            out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw}" height="{h:.1f}" rx="3" fill="{col}"/>')
            ly = (top - 6) if v >= 0 else (top + h + 14)
            out.append(text(x + bw / 2, ly, _sign(v), 11.5, C["ink"], "middle", 700))
        out.append(text(cx, ax.bottom + 22, f"{i + 1}. {e['ชื่อ']}", 12, C["ink"], "middle", 700))
        out.append(text(cx, ax.bottom + 40, f"ปิดที่ A {B.fmt(e['A'])} · B {B.fmt(e['B'])}", 11, C["muted"], "middle"))
    out.append(text(L - 50, ax.top - 14, "ผล", 11.5, C["muted"]))
    alt = "กราฟแท่งสี่กลุ่ม แต่ละกลุ่มมีผลขา A ผลขา B และผลรวม " + " · ".join(
        f"{e['ชื่อ']} ปิดที่ A {e['A']} B {e['B']} ขา A {e['ขาA']} ขา B {e['ขาB']} รวม {e['รวม']}" for e in ends)
    cap = "ยังไม่คิดค่าธรรมเนียม · สี่ตอนจบแยกกัน ทุกตอนเริ่มใหม่จากจุดเปิดเดิม · ไม่ได้บอกว่าตอนไหนเกิดบ่อยกว่า"
    return wrap(W, H, alt, out, cap, "สอน")


# ───────── หน้า 4: ราคา spot กับราคาสัญญามาเจอกันในวันหมดอายุ ─────────
@chart("sab-base-converge")
def _converge(fig):
    b = fig["base"]["b4"]
    path, months = b["เส้นทาง"], b["เส้นทาง"]["เดือน"]
    W, H = 760, 350
    ticks = [48, 50, 52, 54]
    ax = Axis(46.5, 54.5, 92, 286)
    out = [text(24, 26, "ระหว่างทางสองราคาห่างกันได้ แต่ถึงวันหมดอายุต้องเท่ากัน", 13.5, C["ink"], weight=700)]
    out += _legend(24, 52, [("ราคา B แบบซื้อทันที (spot)", LEG["B"], "line"), ("ราคาสัญญา 3 เดือน", LEG["สัญญา"], "dash")])
    xlab = ["วันนี้", "เดือน 1", "เดือน 2", "วันหมดอายุ"]
    for x0, key, end in ((70, "ก", b["จบก"]), (430, "ข", b["จบข"])):
        x1 = x0 + 290
        X = lambda m: x0 + 10 + m / months[-1] * (x1 - x0 - 30)  # noqa: E731
        out += _grid(ax, ticks, x0, x1, label=(x0 == 70))
        out.append(text(x0, 80, f"({key}) วันหมดอายุ spot เป็น {B.fmt(end['spotวันหมดอายุ'])}", 12, C["ink"], weight=700))
        sp, fu = path[key]["spot"], path[key]["สัญญา"]
        pts = lambda ys: " ".join(f"{X(m):.1f},{ax.y(v):.1f}" for m, v in zip(months, ys))  # noqa: E731
        out.append(f'<polyline points="{pts(fu)}" fill="none" stroke="{LEG["สัญญา"]}" stroke-width="2.4" stroke-dasharray="6 4"/>')
        out.append(f'<polyline points="{pts(sp)}" fill="none" stroke="{LEG["B"]}" stroke-width="2.6" stroke-linecap="round"/>')
        out.append(text(X(0) + 6, ax.y(fu[0]) - 9, f"สัญญา {B.fmt(b['สัญญา'])}", 11.5, C["ink"], "start", 700))
        out.append(text(X(0) + 6, ax.y(sp[0]) + 18, f"spot {B.fmt(b['spot'])}", 11.5, C["ink"], "start", 700))
        ex, ey = X(months[-1]), ax.y(sp[-1])
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5.5" fill="{LEG["สัญญา"]}" stroke="#fff" stroke-width="2"/>')
        above = end["spotวันหมดอายุ"] > b["spot"]
        out.append(text(ex - 8, ey + (-12 if above else 22), f"เจอกันที่ {B.fmt(end['spotวันหมดอายุ'])}", 11.5, C["ink"], "end", 700))
        for m, lab in zip(months, xlab):
            out.append(text(X(m), ax.bottom + 18, lab, 10.5, C["grey"], "middle"))
    alt = (f"กราฟเส้นสองแผง ราคา B แบบซื้อทันทีเริ่มที่ {b['spot']} ราคาสัญญาสามเดือนเริ่มที่ {b['สัญญา']} "
           f"แผงซ้าย spot จบที่ {b['จบก']['spotวันหมดอายุ']} แผงขวาจบที่ {b['จบข']['spotวันหมดอายุ']} "
           "ทั้งสองแผงเส้นสัญญามาเจอเส้น spot พอดีในวันหมดอายุ")
    cap = "จุดเริ่มและจุดปลายคือเลขในตาราง · เส้นระหว่างทางเป็นภาพตัวอย่างหนึ่งแบบ ไม่ใช่ราคาจริง"
    return wrap(W, H, alt, out, cap, "แนวคิด")
