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
    W, H = 760, 372
    ax = Axis(min(ticks), max(ticks), 112, 298)
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
            out.append(text(cx, 338, name, 11.5, C["muted"], "middle"))
        hold = f"ถือ A {t['จำนวน']} หน่วยระหว่างนี้"
        out.append(text(x0 + 150, 358, hold, 11, C["grey"], "middle"))
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
    # ป้ายวางฝั่งที่เส้นลาดลงไม่ผ่าน: จุดซ้าย (ได้) ป้ายล่างซ้าย · จุดขวา (เสีย) ป้ายบนขวา
    for key, dx, dy, anchor in (("ขึ้น", 12, -12, "start"), ("ลง", -12, 22, "end")):
        t = b["ตกลงขาย"][key]
        cx, cy = X(t["ราคาซื้อคืน"]), ax.y(t["ผล"])
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="{LEG["B"]}" stroke="#fff" stroke-width="2"/>')
        lab = f"ซื้อคืนที่ {B.fmt(t['ราคาซื้อคืน'])}: {_sign(t['ผล'])}"
        out.append(text(cx + dx, cy + dy, lab, 12, C["ink"], anchor, 700))
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
        out.append(text(X(0) + 2, ax.y(fu[0]) - 18, f"สัญญา {B.fmt(b['สัญญา'])}", 11.5, C["ink"], "start", 700))
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


# ───────── หน้า 1 (เพิ่ม): มูลค่าตามจอขยับได้ จนกว่าจะขาย แล้วจึงนิ่งเป็นเงิน ─────────
def _wig(t, a):
    """คลื่นเล็กระหว่างจุดตัวเลข (ภาพแนวคิด) · ศูนย์ที่ปลายช่วงเสมอ เพื่อให้ผ่านจุดในตารางพอดี"""
    import math
    return a * math.sin(math.pi * t) * math.sin(5 * math.pi * t)


@chart("sab-base-screen-cash")
def _screen_cash(fig):
    h = fig["base"]["b1"]["ยังไม่ขาย"]
    paid, knots = h["จ่ายไปแล้ว"], [h["มูลค่าหลังซื้อ"], h["มูลค่าคืนนี้"], h["มูลค่าพรุ่งนี้"]]
    W, H = 760, 352
    L, R = 70, 736
    ax = Axis(min(knots) - 3, max(knots) + 3, 96, 262)
    xs = [L + 40, L + 200, L + 360, L + 500]           # หลังซื้อ · คืนนี้ · พรุ่งนี้ · ขาย
    out = [text(24, 26, "ยังไม่ขาย ตัวเลขบนจอขยับได้ทุกนาที ขายแล้วจึงนิ่งเป็นเงินจริง", 13.5, C["ink"], weight=700)]
    out += _legend(24, 52, [(f"มูลค่าตามจอของ A {h['จำนวน']} หน่วย (ยังไม่ใช่เงิน)", LEG["A"], "dash"),
                            ("เงินที่รับเข้าบัญชีจริง", C["green"], "line")])
    out.append(f'<rect x="{xs[3]:.1f}" y="{ax.top - 8}" width="{R - xs[3]:.1f}" height="{ax.bottom - ax.top + 8}" fill="#f0fdf4"/>')
    out.append(text(xs[3] + 8, ax.top + 6, "ขายแล้ว", 11, C["green"], weight=700))
    out += _grid(ax, sorted(set(knots + [paid])), L, R)
    yp = ax.y(paid)
    out.append(f'<line x1="{L}" y1="{yp:.1f}" x2="{xs[3]:.1f}" y2="{yp:.1f}" stroke="{C["grey"]}" stroke-width="1.6" '
               f'stroke-dasharray="3 3"/>')
    out.append(text(xs[3] - 6, yp + 16, f"จ่ายไปแล้ว {B.fmt(paid)}", 11, C["muted"], "end", 700))
    # เส้นประ: ผ่านจุดในตารางพอดี · ระหว่างจุดเป็นคลื่นแนวคิด
    pts = []
    segs = [(xs[0], xs[1], knots[0], knots[1]), (xs[1], xs[2], knots[1], knots[2]), (xs[2], xs[3], knots[2], knots[2])]
    for x0, x1, v0, v1 in segs:
        for k in range(21):
            t = k / 20
            pts.append((x0 + (x1 - x0) * t, ax.y(v0 + (v1 - v0) * t + _wig(t, 0.9 if v0 != v1 else 0.45))))
    out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{LEG["A"]}" '
               f'stroke-width="2.4" stroke-dasharray="6 4"/>')
    sold = knots[2]
    out.append(f'<line x1="{xs[3]:.1f}" y1="{ax.y(sold):.1f}" x2="{R:.1f}" y2="{ax.y(sold):.1f}" stroke="{C["green"]}" '
               f'stroke-width="3" stroke-linecap="round"/>')
    labs = [(xs[0], knots[0], f"หลังซื้อ {B.fmt(knots[0])}", -14),
            (xs[1], knots[1], f"คืนนี้ {B.fmt(knots[1])} · ต่ำกว่าที่จ่าย {B.fmt(abs(h['ต่างคืนนี้']))}", 20),
            (xs[2], knots[2], f"พรุ่งนี้ {B.fmt(knots[2])} · สูงกว่าที่จ่าย {B.fmt(h['ต่างพรุ่งนี้'])}", -12)]
    for x, v, lab, dy in labs:
        out.append(f'<circle cx="{x:.1f}" cy="{ax.y(v):.1f}" r="4.5" fill="#fff" stroke="{LEG["A"]}" stroke-width="2.2"/>')
        out.append(text(x, ax.y(v) + dy, lab, 11.5, C["ink"], "middle", 700))
    out.append(f'<circle cx="{xs[3]:.1f}" cy="{ax.y(sold):.1f}" r="5.5" fill="{C["green"]}" stroke="#fff" stroke-width="2"/>')
    out.append(text((xs[3] + R) / 2 + 6, ax.y(sold) - 12, f"รับจริง {B.fmt(sold)} · ผล {_sign(sold - paid)} นิ่งแล้ว",
                    11.5, C["green"], "middle", 700))
    # แถวล่าง: เงินที่รับจริงในแต่ละจังหวะ
    names = ["หลังซื้อ", "คืนนี้ ยังไม่ขาย", "พรุ่งนี้ ยังไม่ขาย", "พรุ่งนี้ ขายทั้งหมด"]
    got = [0, 0, 0, sold]
    for x, n, g in zip(xs, names, got):
        out.append(text(x, ax.bottom + 20, n, 11, C["muted"], "middle"))
        out.append(text(x, ax.bottom + 42, B.fmt(g), 12, C["green"] if g else C["grey"], "middle", 700))
    out.append(text(L - 50, ax.bottom + 42, "รับจริง", 11, C["muted"]))
    alt = (f"กราฟเส้นแนวคิด มูลค่าตามจอของ A สองหน่วยเป็นเส้นประ เริ่ม {knots[0]} คืนนี้ลงเป็น {knots[1]} พรุ่งนี้ขึ้นเป็น {knots[2]} "
           f"ระหว่างนั้นเงินที่รับจริงเป็นศูนย์ พอขายทั้งหมดจึงเป็นเส้นทึบสีเขียวนิ่งที่ {sold} เทียบกับเส้นที่จ่ายไป {paid}")
    cap = "ซื้อ A 2 หน่วยที่ 100 · จุดที่มีตัวเลขคือเลขในตาราง · เส้นระหว่างจุดเป็นภาพตัวอย่าง ไม่ใช่ราคาจริง"
    return wrap(W, H, alt, out, cap, "แนวคิด")


# ───────── หน้า 2 (เพิ่ม): ยืมมาขาย กับ ตกลงขาย — ผลเท่ากัน ต่างแค่จังหวะเงิน ─────────
@chart("sab-base-cash-timing")
def _cash_timing(fig):
    b = fig["base"]["b2"]
    t = b["ยืมมาขาย"]
    sell, buy = t["ขายรวม"], t["ซื้อคืนรวม"]
    res = t["ผล"]
    borrow = [0, sell, sell - buy, sell - buy]
    agree = [0, 0, res, res]
    W, H = 760, 340
    L, R = 70, 736
    ax = Axis(min(borrow + agree) - 6, max(borrow) + 8, 92, 262)
    xs = [L + 50 + i * (R - L - 100) / 3 for i in range(4)]
    out = [text(24, 26, f"ขาย B ไว้ก่อนสองแบบ: เงินเดินคนละจังหวะ แต่จบที่ {_sign(res)} เท่ากัน", 13.5, C["ink"], weight=700)]
    out += _legend(24, 52, [("ยืม B มาขายจริง", LEG["B"], "line"), ("ตกลงขาย ไม่มีเหรียญเปลี่ยนมือ", C["ink"], "dash")])
    out += _grid(ax, [0, sell], L, R)

    def path(vals):
        d = f"M{xs[0]:.1f},{ax.y(vals[0]):.1f}"
        for i in range(1, 4):
            d += f" H{xs[i]:.1f} V{ax.y(vals[i]):.1f}"
        return d + f" H{R - 10:.1f}"
    out.append(f'<path d="{path(borrow)}" fill="none" stroke="{LEG["B"]}" stroke-width="2.8" stroke-linejoin="round"/>')
    out.append(f'<path d="{path(agree)}" fill="none" stroke="{C["ink"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    yb = ax.y(sell)
    out.append(text(xs[1] + 10, yb - 10, f"รับ {B.fmt(sell)} ก่อน · แต่ยังค้างภาระซื้อ B คืน {t['จำนวน']} หน่วย", 11.5, C["ink"],
                    "start", 700))
    out.append(text(xs[2] - 8, ax.y(0) - 34, f"ซื้อคืนจ่าย {B.fmt(buy)}", 11, LEG["B"], "end", 700))
    out.append(text(xs[2] - 8, ax.y(0) - 18, f"ตกลงขาย: จ่ายแค่ส่วนต่าง {B.fmt(abs(res))}", 11, C["ink"], "end", 700))
    out.append(f'<circle cx="{xs[3]:.1f}" cy="{ax.y(res):.1f}" r="5" fill="{C["red"]}" stroke="#fff" stroke-width="2"/>')
    out.append(text(xs[3], ax.y(res) + 22, f"สองแบบจบที่ {_sign(res)}", 12, C["red"], "middle", 700))
    names = ["เริ่ม", f"เปิด: ขายที่ {B.fmt(t['ราคาขาย'])}", f"ปิด: ซื้อคืนที่ {B.fmt(t['ราคาซื้อคืน'])}", "จบ ไม่มีอะไรค้าง"]
    for x, n in zip(xs, names):
        out.append(text(x, ax.bottom + 44, n, 11, C["muted"], "middle"))
    out.append(text(L - 50, ax.top - 14, "เงินที่เข้า/ออกสะสม", 11, C["muted"]))
    alt = (f"กราฟขั้นบันไดสองเส้น เส้นส้มคือยืม B มาขาย เงินขึ้นเป็น {sell} ตอนเปิด แล้วลงเป็น {sell - buy} เมื่อซื้อคืนที่ "
           f"{t['ราคาซื้อคืน']} เส้นประคือข้อตกลงขาย เงินเป็นศูนย์ตอนเปิด แล้วจ่ายส่วนต่าง {abs(res)} ตอนปิด ทั้งสองเส้นจบที่ {res}")
    cap = "ขาย B 1 หน่วยที่ 50 · ปิดที่ 51 · ยังไม่คิดค่าธรรมเนียม"
    return wrap(W, H, alt, out, cap, "สอน")


# ───────── หน้า 4 (เพิ่ม): เงินสามกองทีละจังหวะ ─────────
@chart("sab-base-three-pockets")
def _three_pockets(fig):
    b = fig["base"]["b4"]
    acc = b["บัญชี"]
    names = {"เริ่ม": ["เริ่ม", ""], "ซื้อBspot": ["ซื้อ B spot", f"ที่ {B.fmt(b['spot'])}"],
             "ขายสัญญา": ["ขายสัญญา", f"ที่ {B.fmt(b['สัญญา'])}"],
             "กลางทาง": ["กลางทาง", f"spot {B.fmt(b['กลางทาง']['spot'])} สัญญา {B.fmt(b['กลางทาง']['สัญญา'])}"],
             "วันหมดอายุ": ["วันหมดอายุ", f"spot {B.fmt(b['ขายBวันหมดอายุ'])}"], "ปิดครบ": ["ปิดครบ", "ทุกอย่างเป็นเงินสด"]}
    W, H = 800, 380
    L, R = 70, 784
    top = max(r["เงินสด"] + r["มูลค่าB"] for r in acc)
    ax = Axis(-12, top * 1.12, 96, 290)
    gw = (R - L) / len(acc)
    bw = 54
    col = {"cash": LEG["A"], "B": LEG["B"], "k": LEG["สัญญา"]}
    out = [text(24, 26, "ซื้อ B แล้วเงินสดเหลือครึ่งเดียว แต่ equity ยังเป็น 100 — เงินแค่ย้ายกอง", 13.5, C["ink"], weight=700)]
    out += _legend(24, 52, [("เงินสด", col["cash"], "box"), ("B ในมือ (ตามราคาตอนนั้น)", col["B"], "box"),
                            ("สัญญาที่ขายไว้ (ถ้าปิดตอนนี้)", col["k"], "box"), ("equity", C["ink"], "line")])
    out += _grid(ax, [0, b["เงินสดตั้งต้น"]], L, R)
    for i, r in enumerate(acc):
        cx = L + gw * i + gw / 2
        x = cx - bw / 2
        base = 0
        for key, v in (("cash", r["เงินสด"]), ("B", r["มูลค่าB"])):
            if v:
                y1, y0 = ax.y(base + v), ax.y(base)
                out.append(f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw}" height="{y0 - y1:.1f}" fill="{col[key]}"/>')
                out.append(text(cx, (y0 + y1) / 2 + 4, B.fmt(v), 11, "#ffffff", "middle", 700))
                base += v
        k = r["สัญญา"]
        if k:
            y0 = ax.y(0)
            hk = max(5, ax.y(k) - y0)
            out.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw}" height="{hk:.1f}" fill="{col["k"]}" fill-opacity=".25" '
                       f'stroke="{col["k"]}" stroke-dasharray="3 2"/>')
            out.append(text(cx, y0 + hk + 13, B.fmt(k), 11, col["k"], "middle", 700))
        ye = ax.y(r["equity"])
        out.append(f'<line x1="{x - 8:.1f}" y1="{ye:.1f}" x2="{x + bw + 8:.1f}" y2="{ye:.1f}" stroke="{C["ink"]}" stroke-width="2.4"/>')
        out.append(text(cx, ye - 8, f"equity {B.fmt(r['equity'])}", 11, C["ink"], "middle", 700))
        n1, n2 = names.get(r["จังหวะ"], [r["จังหวะ"], ""])
        out.append(text(cx, ax.bottom + 30, n1, 11.5, C["ink"], "middle", 700))
        if n2:
            out.append(text(cx, ax.bottom + 46, n2, 10.5, C["muted"], "middle"))
    alt = "กราฟแท่งซ้อนหกจังหวะ " + " · ".join(
        f"{r['จังหวะ']} เงินสด {r['เงินสด']} B {r['มูลค่าB']} สัญญา {r['สัญญา']} equity {r['equity']}" for r in acc)
    cap = (f"เริ่มด้วยเงินสด {B.fmt(b['เงินสดตั้งต้น'])} · ซื้อ B spot 1 หน่วย คู่กับขายสัญญา 1 ใบ · "
           "ยังไม่คิดค่าธรรมเนียมและเงินค้ำสัญญา")
    return wrap(W, H, alt, out, cap, "สอน")
