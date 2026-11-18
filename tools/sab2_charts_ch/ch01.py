"""บท 1 เล่ม 2 — เส้นที่ลากผ่านจุด · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json → ch01 เท่านั้น)

sab2-fit6     : หกจุดของคู่ A–B (แกนนอน B · แกนตั้ง A) + เส้นสามความชัน 2 / 2.5 / 3 ผ่านจุดกลาง (50, 100)
                + ก้านระยะพลาดของเส้น 2.5
sab2-bowl     : ผลรวมกำลังสองของระยะพลาด เทียบความชัน (ชาม 10 × (b − 2.5)² + 5.5) · จุดที่ลองในหน้า
sab2-btceth   : 📡 731 วันของช่วงเลือก แกนนอน ETH แกนตั้ง BTC · สีแยกปีแรก/ปีหลัง · เส้น A บน B (23.69)
                กับเส้นจากทิศ B บน A (27.46)
sab2-windows  : 🎲 h ที่ประมาณได้จากโลกที่รู้คำตอบ (h = 2) ที่ 20 / 60 / 250 / 731 วัน · 30 ชุดสุ่ม
sab2-resid3   : Residual หารด้วย SD ของตัวเอง สามแผง: 🎲 มีเชือก · 🎲 ไม่มีเชือก · 📡 BTC/ETH
sab2-two-dirs : หกจุดเดิม สองแผง: A บน B (ก้านแนวตั้ง · เส้น 2.5) กับ B บน A (ก้านแนวนอน · เส้น 68 ÷ 25 = 2.72)
"""

from sab_charts import chart, wrap, text, C, B

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]
BLUE_LIGHT, BLUE_DARK = "#60a5fa", "#1e40af"   # ไล่เฉดสีเดียว (README: Graded series)


def _n(v):
    """ตัวเลขที่เป็นจำนวนเต็มพิมพ์ไม่มี .0 (เช่น 2.0 → 2)"""
    return B.fmt(int(v)) if float(v).is_integer() else B.fmt(v)


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


@chart("sab2-fit6")
def _fit6(fig):
    h = fig["ch01"]["หกวัน"]
    A, Bv = h["A"], h["B"]
    mA, mB = h["MeanA"], h["MeanB"]
    tr = h["ลอง"]
    W, H, L, R, T, Bm = 760, 400, 70, 190, 58, 340
    x0, x1, y0, y1 = 47.5, 52.5, 92, 108
    X = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - y0) / (y1 - y0) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "ลากเส้นผ่านจุดกลาง แล้ววัดว่าแต่ละวันพลาดเส้นไปเท่าไร", 13.5, INK, weight=700)]
    for b in sorted(set(Bv)):
        out.append(f'<line x1="{X(b):.1f}" y1="{T}" x2="{X(b):.1f}" y2="{Bm}" stroke="{C["grid"]}"/>')
        out.append(text(X(b), Bm + 18, B.fmt(b), 11, GREY, "middle"))
    for a in (95, 100, 105):
        out.append(f'<line x1="{L}" y1="{Y(a):.1f}" x2="{W - R}" y2="{Y(a):.1f}" stroke="{C["grid"]}"/>')
        out.append(text(L - 8, Y(a) + 4, B.fmt(a), 11, GREY, "end"))
    out.append(text((L + W - R) / 2, Bm + 38, "ราคา B (ดอลลาร์)", 11.5, MUTED, "middle", 700))
    out.append(text(L - 8, T - 12, "ราคา A", 11.5, MUTED, "end", 700))
    styles = [("2", GREY, "6 4", 1.6), ("3", GREY, "2 4", 1.8), ("2.5", C["purple"], None, 2.6)]
    for k, col, dash, sw in styles:
        b = tr[k]["ความชัน"]
        ya, yb = mA + b * (x0 + 0.3 - mB), mA + b * (x1 - 0.3 - mB)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{X(x0 + 0.3):.1f}" y1="{Y(ya):.1f}" x2="{X(x1 - 0.3):.1f}" y2="{Y(yb):.1f}" '
                   f'stroke="{col}" stroke-width="{sw}"{d}/>')
    # ก้านระยะพลาดของเส้น 2.5
    fit = tr["2.5"]["เส้น"]
    for i, (b, a) in enumerate(zip(Bv, A)):
        dx = -7 if i == 3 else 0   # วันที่ 3 กับ 4 มี B เท่ากัน — เลื่อนก้านวันที่ 4 ให้เห็นแยก
        out.append(f'<line x1="{X(b) + dx:.1f}" y1="{Y(fit[i]):.1f}" x2="{X(b) + dx:.1f}" y2="{Y(a):.1f}" '
                   f'stroke="{C["red"]}" stroke-width="2"/>')
    for i, (b, a) in enumerate(zip(Bv, A)):
        dx = -7 if i == 3 else 0
        out.append(f'<circle cx="{X(b) + dx:.1f}" cy="{Y(a):.1f}" r="5" fill="{C["blue"]}"/>')
        lab = f"วัน {i + 1}"
        above = A[i] > fit[i]
        out.append(text(X(b) + dx + (-9 if i == 3 else 9), Y(a) + (-8 if above else 16), lab, 10.5, INK, "end" if i == 3 else "start"))
    out.append(f'<circle cx="{X(mB):.1f}" cy="{Y(mA):.1f}" r="6.5" fill="none" stroke="{INK}" stroke-width="1.8"/>')
    out.append(text(X(mB) + 10, Y(mA) + 18, f"จุดกลาง ({_n(mB)}, {_n(mA)})", 10.5, INK, "start", 700))
    lx = W - R + 14
    legend = [(f"เอียง {_n(tr['3']['ความชัน'])} · รวม {_n(tr['3']['รวมกำลังสอง'])}", GREY, "2 4"),
              (f"เอียง {_n(tr['2.5']['ความชัน'])} · รวม {_n(tr['2.5']['รวมกำลังสอง'])}", C["purple"], None),
              (f"เอียง {_n(tr['2']['ความชัน'])} · รวม {_n(tr['2']['รวมกำลังสอง'])}", GREY, "6 4")]
    for j, (lab, col, dash) in enumerate(legend):
        yy = T + 20 + 26 * j
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{lx}" y1="{yy}" x2="{lx + 26}" y2="{yy}" stroke="{col}" stroke-width="2.4"{d}/>')
        out.append(text(lx + 32, yy + 4, lab, 11, INK if col != GREY else MUTED, weight=700 if col != GREY else None))
    out.append(text(lx, T + 112, "รวม = ผลรวมกำลังสอง", 10.5, MUTED))
    out.append(text(lx, T + 128, "ของระยะพลาด", 10.5, MUTED))
    out.append(f'<line x1="{lx}" y1="{T + 152}" x2="{lx}" y2="{T + 172}" stroke="{C["red"]}" stroke-width="2"/>')
    out.append(text(lx + 10, T + 166, "ระยะพลาดของเส้นเอียง 2.5", 10.5, C["red"]))
    alt = ("กราฟจุดหกจุด แกนนอนราคา B 48 ถึง 52 แกนตั้งราคา A 95 ถึง 105 เส้นสามเส้นผ่านจุดกลาง 50, 100 "
           "ความชัน 2 และ 3 ได้ผลรวมกำลังสองของระยะพลาด 8 เท่ากัน ความชัน 2.5 ได้ 5.5 ก้านสีแดงคือระยะพลาดของเส้น 2.5 "
           "ก้านยาวสุดคือวันที่ 4 ที่ต่ำกว่าเส้น 2")
    cap = "หกวันสมมติของคู่ A–B ในตอน ก · วันที่ 3 กับ 4 มีราคา B เท่ากัน (50) จุดวันที่ 4 จึงเลื่อนซ้ายเล็กน้อยให้เห็นแยก"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab2-bowl")
def _bowl(fig):
    h = fig["ch01"]["หกวัน"]
    bowl = h["ชาม"]
    k, b0, m = bowl["คูณหน้า"], bowl["ก้น"], bowl["เหลือที่ก้น"]
    f = lambda b: k * (b - b0) ** 2 + m  # noqa: E731
    W, H, L, R, T, Bm = 760, 340, 70, 40, 56, 286
    x0, x1, y0, y1 = 1.75, 3.25, 0, 14
    X = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - y0) / (y1 - y0) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "ทุกความเอียงมีผลรวมกำลังสองหนึ่งค่า: ได้รูปชาม ก้นชามคือความเอียงที่พอดีที่สุด", 13.5, INK, weight=700)]
    for g in (0, 4, 8, 12):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for key in ("2", "2.5", "3"):
        b = h["ลอง"][key]["ความชัน"]
        out.append(text(X(b), Bm + 18, _n(b), 11, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 38, "ความเอียงที่ลอง (h)", 11.5, MUTED, "middle", 700))
    out.append(text(16, T - 12, "ผลรวมกำลังสองของระยะพลาด", 11.5, MUTED, "start", 700))
    pts = [(X(x0 + i * (x1 - x0) / 60), Y(f(x0 + i * (x1 - x0) / 60))) for i in range(61)]
    out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{C["blue"]}" stroke-width="2.4"/>')
    marks = [("2", "start", 10, -10), ("3", "end", -10, -10), ("2.4", "end", -8, 22), ("2.6", "start", 8, 22), ("2.5", "middle", 0, 26)]
    for key, anc, dx, dy in marks:
        t = h["ลอง"][key]
        b, s = t["ความชัน"], t["รวมกำลังสอง"]
        col = C["purple"] if key == "2.5" else INK
        out.append(f'<circle cx="{X(b):.1f}" cy="{Y(s):.1f}" r="{6 if key == "2.5" else 4.5}" fill="{col}"/>')
        out.append(text(X(b) + dx, Y(s) + dy, f"{_n(b)} → {_n(s)}", 11, col, anc, 700)
                   .replace("<text ", '<text stroke="#fff" stroke-width="4" paint-order="stroke" ', 1))
    # เส้นประก้นชามเริ่มใต้ป้าย 2.5 → 5.5 เพื่อไม่ให้ทับตัวอักษร
    out.insert(-2, f'<line x1="{X(b0):.1f}" y1="{Y(m) + 32:.1f}" x2="{X(b0):.1f}" y2="{Bm}" stroke="{C["purple"]}" stroke-dasharray="4 4"/>')
    alt = ("เส้นโค้งรูปชาม แกนนอนความชัน 1.75 ถึง 3.25 แกนตั้งผลรวมกำลังสองของระยะพลาด จุดที่ลอง 2 ได้ 8 "
           "2.4 ได้ 5.6 2.5 ได้ 5.5 ซึ่งต่ำสุด 2.6 ได้ 5.6 และ 3 ได้ 8")
    cap = f"เส้นโค้งคือ {B.fmt(k)} × (ความชัน − {B.fmt(b0)})² + {B.fmt(m)} ของหกวันในตอน ก · จุดคือค่าที่คิดด้วยมือในตาราง"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab2-btceth")
def _btceth(fig):
    r = fig["ch01"]["จริง"]
    g = r["ชุดกราฟ"]
    btc, eth, half = g["BTC"], g["ETH"], g["iครึ่ง"]
    W, H, L, R, T, Bm = 760, 420, 84, 200, 60, 360
    x0, x1, y0, y1 = 900, 4200, 10000, 95000
    X = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - y0) / (y1 - y0) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "BTC กับ ETH ทุกวันของช่วงเลือก: เส้นสองทิศไม่ทับกัน", 13.5, INK, weight=700)]
    for v in g["แกนETH"]:
        out.append(f'<line x1="{X(v):.1f}" y1="{T}" x2="{X(v):.1f}" y2="{Bm}" stroke="{C["grid"]}"/>')
        out.append(text(X(v), Bm + 18, B.fmt(v), 11, GREY, "middle"))
    for v in g["แกนBTC"]:
        out.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W - R}" y2="{Y(v):.1f}" stroke="{C["grid"]}"/>')
        out.append(text(L - 8, Y(v) + 4, B.fmt(v), 11, GREY, "end"))
    out.append(text((L + W - R) / 2, Bm + 38, "ราคา ETH (B · ดอลลาร์)", 11.5, MUTED, "middle", 700))
    out.append(text(L - 8, T - 12, "ราคา BTC (A)", 11.5, MUTED, "end", 700))
    for i, (e, b) in enumerate(zip(eth, btc)):
        col = BLUE_LIGHT if i < half else BLUE_DARK
        out.append(f'<circle cx="{X(e):.1f}" cy="{Y(b):.1f}" r="2.1" fill="{col}" fill-opacity=".55"/>')
    # เส้น A บน B
    hab, a = r["hAบนB"], r["InterceptAบนB"]
    ea, eb = 1100, 4100
    out.append(f'<line x1="{X(ea):.1f}" y1="{Y(a + hab * ea):.1f}" x2="{X(eb):.1f}" y2="{Y(a + hab * eb):.1f}" '
               f'stroke="{C["purple"]}" stroke-width="2.6"/>')
    # เส้นจากทิศ B บน A ผ่านจุดค่าเฉลี่ยเดียวกัน
    mE, mB = sum(eth) / len(eth), sum(btc) / len(btc)
    hba = r["hBบนA"]
    out.append(f'<line x1="{X(ea):.1f}" y1="{Y(mB + hba * (ea - mE)):.1f}" x2="{X(eb):.1f}" y2="{Y(mB + hba * (eb - mE)):.1f}" '
               f'stroke="{INK}" stroke-width="1.8" stroke-dasharray="6 4"/>')
    lx = W - R + 14
    items = [(C["purple"], None, f"A บน B: h {B.fmt(hab)}"), (INK, "6 4", f"B บน A: h {B.fmt(hba)}")]
    for j, (col, dash, lab) in enumerate(items):
        yy = T + 16 + 24 * j
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{lx}" y1="{yy}" x2="{lx + 26}" y2="{yy}" stroke="{col}" stroke-width="2.4"{d}/>')
        out.append(text(lx + 32, yy + 4, lab, 11.5, col, weight=700))
    for j, (col, lab) in enumerate([(BLUE_LIGHT, f"ปีแรก ถึง {r['ครึ่งแรก']['จบ']}"), (BLUE_DARK, f"ปีหลัง จาก {r['ครึ่งหลัง']['เริ่ม']}")]):
        yy = T + 80 + 22 * j
        out.append(f'<circle cx="{lx + 13}" cy="{yy}" r="4.5" fill="{col}"/>')
        out.append(text(lx + 24, yy + 4, lab, 10.5, MUTED))
    out.append(text(lx, T + 150, f"R² {B.fmt(r['R2'])}", 11.5, INK, weight=700))
    alt = (f"กราฟจุด {r['ช่วงเลือก']['วัน']} จุด แกนนอนราคา ETH แกนตั้งราคา BTC จุดปีแรกกองอยู่ล่างซ้าย ETH ราว 1,200 ถึง 2,100 "
           f"จุดปีหลังกระจายขึ้นไปด้านบนและเอียงชันกว่า เส้นม่วง A บน B ลาด {B.fmt(hab)} เส้นประจากทิศ B บน A ลาด {B.fmt(hba)} ชันกว่า")
    cap = f"ราคาปิดรายวัน Binance ช่วงเลือก {r['ช่วงเลือก']['เริ่ม']} ถึง {r['ช่วงเลือก']['จบ']} · {r['ช่วงเลือก']['วัน']} วัน · หนึ่งจุดต่อวัน"
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-windows")
def _windows(fig):
    s = fig["ch01"]["จำลอง"]
    w, days, true_h = s["หน้าต่าง"], s["หน้าต่างวัน"], s["h"]
    W, L, R = 760, 200, 60
    H = 110 + 52 * len(days)
    lo, hi = 1.0, 2.6
    X = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)  # noqa: E731
    out = [text(16, 26, f"ข้อมูลยิ่งสั้น h ที่ได้ยิ่งกระจายห่างคำตอบจริง {B.fmt(true_h)}", 13.5, INK, weight=700)]
    top, bot = 56, 56 + 52 * len(days)
    for g in (1.5, 2, 2.5):
        if g == 1.5:
            continue
        out.append(f'<line x1="{X(g):.1f}" y1="{top}" x2="{X(g):.1f}" y2="{bot}" stroke="{C["grid"]}"/>')
    out.append(f'<line x1="{X(true_h):.1f}" y1="{top - 6}" x2="{X(true_h):.1f}" y2="{bot}" stroke="{INK}" stroke-width="2" stroke-dasharray="5 4"/>')
    out.append(text(X(true_h), top - 12, f"คำตอบจริง h = {B.fmt(true_h)}", 11, INK, "middle", 700))
    for i, nn in enumerate(days):
        r = w[str(nn)]
        y = top + 28 + 52 * i
        out.append(text(16, y + 4, f"ข้อมูล {B.fmt(nn)} วัน", 12, INK, weight=700))
        out.append(f'<line x1="{X(r["ต่ำสุด"]):.1f}" y1="{y}" x2="{X(r["สูงสุด"]):.1f}" y2="{y}" stroke="{C["green"]}" '
                   f'stroke-width="9" stroke-opacity=".28" stroke-linecap="round"/>')
        out.append(f'<line x1="{X(r["มัธยฐาน"]):.1f}" y1="{y - 9}" x2="{X(r["มัธยฐาน"]):.1f}" y2="{y + 9}" stroke="{C["green"]}" stroke-width="3"/>')
        out.append(text(X(r["ต่ำสุด"]) - 10, y + 4, B.fmt(r["ต่ำสุด"]), 11, MUTED, "end", 700))
        out.append(text(X(r["สูงสุด"]) + 10, y + 4, B.fmt(r["สูงสุด"]), 11, MUTED, "start", 700))
    out.append(text(16, bot + 30, f"แถบ = ต่ำสุดถึงสูงสุดจาก {B.fmt(s['ชุด'])} โลกสุ่ม · ขีดตั้ง = มัธยฐาน", 10.5, MUTED))
    alt = ("แถบสี่แถว ข้อมูล 20 วันได้ h ตั้งแต่ 1.1 ถึง 2.44 ข้อมูล 60 วัน 1.56 ถึง 2.37 ข้อมูล 250 วัน 1.73 ถึง 2.1 "
           "ข้อมูล 731 วัน 1.95 ถึง 2.06 มัธยฐานทุกแถวใกล้ 2 ซึ่งเป็นคำตอบจริง")
    cap = f"โลกที่มีเชือกและรู้คำตอบ h = {B.fmt(true_h)} · สุ่มซ้ำ {B.fmt(s['ชุด'])} ชุดต่อความยาว"
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-resid3")
def _resid3(fig):
    c = fig["ch01"]
    s, r = c["จำลอง"], c["จริง"]
    panels = [("🎲 โลกมีเชือก", s["ชุดกราฟ"]["z_มีเชือก"], C["green"], f"{B.fmt(s['ตัวอย่าง']['R2เปอร์เซ็นต์'])}%", s["ตัวอย่าง"]["ข้ามMean"]),
              ("🎲 โลกไม่มีเชือก", s["ชุดกราฟ"]["z_ไม่มีเชือก"], GREY, f"{B.fmt(s['ไม่มีเชือก']['R2เปอร์เซ็นต์'])}%", s["ไม่มีเชือก"]["ข้ามMean"]),
              ("📡 BTC บน ETH", r["ชุดกราฟ"]["z"], C["blue"], f"{B.fmt(r['R2เปอร์เซ็นต์'])}%", r["ข้ามMean"])]
    W, L, R = 760, 70, 200
    ph, gap, top = 92, 30, 50
    H = top + len(panels) * (ph + gap) + 20
    out = [text(16, 26, "R² สูงทั้งสามแผง แต่ Residual กลับมาที่ศูนย์บ่อยแค่ไหนต่างกันมาก", 13.5, INK, weight=700)]
    lim = 4
    for k, (name, zs, col, r2t, cross) in enumerate(panels):
        t0 = top + k * (ph + gap)
        n = len(zs)
        X = lambda i: L + i / (n - 1) * (W - L - R)  # noqa: E731
        Y = lambda v, t0=t0: t0 + ph / 2 - max(-lim, min(lim, v)) / lim * (ph / 2)  # noqa: E731
        out.append(text(L, t0 - 6, name, 11.5, INK, weight=700))
        for gv in (-2, 0, 2):
            out.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W - R}" y2="{Y(gv):.1f}" stroke="{C["axis"] if gv == 0 else C["grid"]}"/>')
            out.append(text(L - 8, Y(gv) + 4, B.fmt(gv), 10, GREY, "end"))
        pts = [(X(i), Y(v)) for i, v in enumerate(zs)]
        out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{col}" stroke-width="1.4" stroke-linejoin="round"/>')
        out.append(text(W - R + 14, t0 + ph / 2 - 6, f"R² {r2t}", 11.5, INK, weight=700))
        out.append(text(W - R + 14, t0 + ph / 2 + 12, f"ข้ามศูนย์ {B.fmt(cross)} ครั้ง", 11.5, col if col != GREY else MUTED, weight=700))
    out.append(text(L, H - 8, f"แกนนอน = {B.fmt(r['ช่วงเลือก']['วัน'])} วัน · แกนตั้ง = Residual หารด้วย SD ของ Residual แผงนั้น", 10.5, MUTED))
    alt = (f"สามแผงเส้น {B.fmt(r['ช่วงเลือก']['วัน'])} วัน แผงบนโลกมีเชือกแกว่งถี่รอบศูนย์ ข้ามศูนย์ {s['ตัวอย่าง']['ข้ามMean']} ครั้ง "
           f"แผงกลางโลกไม่มีเชือกเดินเป็นคลื่นยาว ข้าม {s['ไม่มีเชือก']['ข้ามMean']} ครั้ง แผงล่าง BTC บน ETH เดินเป็นคลื่นยาวและพุ่งขึ้นช่วงท้าย ข้าม {r['ข้ามMean']} ครั้ง")
    cap = "แผงบนและกลางคือโลกจำลองตัวอย่างหนึ่งชุด (h จริง = 2) · แผงล่างคือข้อมูลจริงช่วงเลือก · ทุกแผงตัดที่ ±4"
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-two-dirs")
def _two_dirs(fig):
    h = fig["ch01"]["หกวัน"]
    A, Bv = h["A"], h["B"]
    mA, mB = h["MeanA"], h["MeanB"]
    hab, hba = h["ลอง"]["2.5"]["ความชัน"], h["hจากBบนA"]
    W, H, T, Bm = 760, 380, 76, 316
    x0, x1, y0, y1 = 47.5, 52.5, 93, 107
    panels = [(60, 360), (440, 740)]
    out = [text(16, 26, "ข้อมูลหกวันชุดเดียว วัดระยะพลาดคนละแนว ได้เส้นคนละเส้น", 13.5, INK, weight=700)]
    heads = [(f"A บน B: วัดแนวตั้ง (ดอลลาร์ของ A) · h {_n(hab)}", C["purple"]),
             (f"B บน A: วัดแนวนอน (ดอลลาร์ของ B) · h {_n(h['ผลรวมdAกำลังสอง'])} ÷ {_n(h['ผลรวมdBคูณdA'])} = {_n(hba)}", INK)]
    for k, (L, Rx) in enumerate(panels):
        X = lambda v, L=L, Rx=Rx: L + (v - x0) / (x1 - x0) * (Rx - L)  # noqa: E731
        Y = lambda v: Bm - (v - y0) / (y1 - y0) * (Bm - T)  # noqa: E731
        out.append(text(L, T - 22, heads[k][0], 11.5, heads[k][1], weight=700))
        for b in sorted(set(Bv)):
            out.append(f'<line x1="{X(b):.1f}" y1="{T}" x2="{X(b):.1f}" y2="{Bm}" stroke="{C["grid"]}"/>')
            out.append(text(X(b), Bm + 17, B.fmt(b), 10.5, GREY, "middle"))
        for a in (95, 100, 105):
            out.append(f'<line x1="{L}" y1="{Y(a):.1f}" x2="{Rx}" y2="{Y(a):.1f}" stroke="{C["grid"]}"/>')
            out.append(text(L - 6, Y(a) + 4, B.fmt(a), 10.5, GREY, "end"))
        out.append(text((L + Rx) / 2, Bm + 36, "ราคา B", 11, MUTED, "middle", 700))
        out.append(text(L - 6, T - 4, "ราคา A", 10.5, MUTED, "end", 700))
        ba, bb = x0 + 0.25, x1 - 0.25
        line_ab = (X(ba), Y(mA + hab * (ba - mB)), X(bb), Y(mA + hab * (bb - mB)))
        line_ba = (X(ba), Y(mA + hba * (ba - mB)), X(bb), Y(mA + hba * (bb - mB)))
        if k == 0:
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.6"/>' % (line_ab + (C["purple"],)))
            for i, (b, a) in enumerate(zip(Bv, A)):
                dx = -7 if i == 3 else 0
                fit = mA + hab * (b - mB)
                out.append(f'<line x1="{X(b) + dx:.1f}" y1="{Y(fit):.1f}" x2="{X(b) + dx:.1f}" y2="{Y(a):.1f}" stroke="{C["red"]}" stroke-width="2"/>')
        else:
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" stroke-opacity=".45"/>'
                       % (line_ab + (C["purple"],)))
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="6 4"/>'
                       % (line_ba + (INK,)))
            for i, (b, a) in enumerate(zip(Bv, A)):
                fitb = mB + (a - mA) / hba
                out.append(f'<line x1="{X(fitb):.1f}" y1="{Y(a):.1f}" x2="{X(b):.1f}" y2="{Y(a):.1f}" stroke="{C["red"]}" stroke-width="2"/>')
            out.append(text(Rx - 4, Bm - 10, f"เส้นม่วงจาง = เส้น {_n(hab)} ของแผงซ้าย", 10, C["purple"], "end"))
        for i, (b, a) in enumerate(zip(Bv, A)):
            dx = -7 if (i == 3 and k == 0) else 0
            out.append(f'<circle cx="{X(b) + dx:.1f}" cy="{Y(a):.1f}" r="4.6" fill="{C["blue"]}"/>')
    out.append(text(16, H - 8, f"ก้านแดง = ระยะพลาดที่แต่ละทิศพยายามทำให้ผลรวมกำลังสองน้อยที่สุด · {_n(hab)} ÷ {_n(hba)} ≈ R² {B.fmt(h['R2'])}",
                    10.5, MUTED))
    alt = (f"สองแผงของหกจุดเดิม แผงซ้ายเส้นม่วง A บน B เอียง {_n(hab)} มีก้านแดงแนวตั้ง แผงขวาเส้นประ B บน A "
           f"เอียง {_n(hba)} ชันกว่า มีก้านแดงแนวนอน และเส้น {_n(hab)} จาง ๆ ให้เทียบ")
    cap = "หกวันสมมติของคู่ A–B ในตอน ก · แผงซ้ายเลื่อนจุดวันที่ 4 ไปซ้ายเล็กน้อยเหมือนภาพหกจุด"
    return wrap(W, H, alt, out, cap, "สอน")
