"""บท 2 — เงินบนโต๊ะมาจากไหน · สเปกกราฟของบท

sab-tail: วาดใหม่ 50 ช่วง (errata 3) · ซ้าย = เส้นทางที่ชนะทุกช่วง 50 ช่วง เทียบเส้นค่าคาดหมาย แล้วช่วงที่ 51 (นอกหน้าต่าง)
          เสียครั้งเดียว · ขวา = โอกาสไม่เห็นวันเสียเลยเมื่อดู N ช่วง ("คูณ 0.99 ซ้ำ N ครั้ง")
sab-shape-strips: แถบผลแนวคิดสี่กลไก (ภาพแนวคิด ไม่พิมพ์ตัวเลข · สเกลแยกต่อแถว)
"""
from sab_charts import chart, wrap, text, nice_ticks, C, B


@chart("sab-tail")
def _tail(fig):
    c = fig["ch02"]
    t = c["หางหนึ่งเปอร์เซ็นต์"]
    n = c["ช่วงในภาพหาง"]
    after = c["ถ้าช่วงที่51เสีย"]
    ev_n = t["ค่าคาดหมาย50รอบ"]
    W, H = 760, 340
    out = []
    # ── ซ้าย: เส้นทางสะสม ──
    L, R, T, Bm = 64, 392, 74, 290
    lo, hi = min(after, ev_n) * 1.35, n * 1.3
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)          # noqa: E731
    X = lambda i: L + i / (n + 6) * (R - L)                       # noqa: E731
    for g in nice_ticks(lo, hi, 4):
        if lo <= g <= hi:
            out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                       f'stroke-width="{1.5 if g == 0 else 1}"/>')
            out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    # พื้นที่นอกหน้าต่างทดสอบ
    out.append(f'<rect x="{X(n):.1f}" y="{T}" width="{R - X(n):.1f}" height="{Bm - T}" fill="{C["grid"]}"/>')
    pts = " ".join(f"{X(i):.1f},{Y(i * t['ได้']):.1f}" for i in range(n + 1))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["green"]}" stroke-width="2.4"/>')
    out.append(f'<line x1="{X(n):.1f}" y1="{Y(n):.1f}" x2="{X(n + 1):.1f}" y2="{Y(after):.1f}" stroke="{C["red"]}" stroke-width="2.4"/>')
    out.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(n):.1f}" y2="{Y(ev_n):.1f}" stroke="{C["grey"]}" '
               f'stroke-dasharray="6 4" stroke-width="2"/>')
    out.append(f'<circle cx="{X(n):.1f}" cy="{Y(n):.1f}" r="4.5" fill="{C["purple"]}"/>')
    out.append(text(X(n) - 8, Y(n) - 10, f"หน้าจอ +{B.fmt(t['ถ้าไม่เห็นวันเสีย50รอบ'])}", 11.5, C["green"], "end", 700))
    out.append(text(X(n) - 8, Y(ev_n) + 18, f"Expected Value {B.fmt(ev_n)}", 11.5, C["muted"], "end", 700))
    out.append(f'<circle cx="{X(n + 1):.1f}" cy="{Y(after):.1f}" r="4" fill="{C["red"]}"/>')
    out.append(text(X(n + 1) - 10, Y(after) + 4, f"รอบที่ {n + 1} เสีย {B.fmt(t['เสีย'])} → {B.fmt(after)}", 11, C["red"], "end", 700))
    out.append(text((X(n) + R) / 2, Bm - 6, "นอกที่ดู", 10, C["grey"], "middle"))
    out.append(text(L, Bm + 18, "รอบที่ 1", 10.5, C["grey"]))
    out.append(text(X(n), Bm + 18, f"รอบที่ {n}", 10.5, C["grey"], "middle"))
    out.append(text(L, T - 26, f"ยอดสะสม: ชนะ {n} รอบติด", 12.5, C["ink"], weight=700))
    # ── ขวา: โอกาสไม่เห็นวันเสีย ──
    L2, R2 = 452, 736
    rows = list(c["ไม่เห็นวันเสีย"].items())
    gw = (R2 - L2) / len(rows)
    Y2 = lambda v: Bm - v / 100 * (Bm - T)                         # noqa: E731
    out.append(f'<line x1="{L2}" y1="{Bm}" x2="{R2}" y2="{Bm}" stroke="{C["axis"]}" stroke-width="1.5"/>')
    for i, (k, v) in enumerate(rows):
        cx = L2 + gw * i + gw / 2
        hot = int(k) == n                      # ม่วง = จำนวนรอบที่ภาพซ้ายดู (คำถามให้ทายของบท)
        col = C["purple"] if hot else C["blue"]
        out.append(f'<rect x="{cx - 20:.1f}" y="{Y2(v):.1f}" width="40" height="{Bm - Y2(v):.1f}" rx="3" fill="{col}"/>')
        out.append(text(cx, Y2(v) - 7, f"{B.fmt(v)}%", 11.5, col, "middle", 700))
        out.append(text(cx, Bm + 18, f"{k} รอบ", 10.5, C["grey"], "middle"))
    out.append(text(L2, T - 26, "โอกาสไม่เห็นรอบแพ้เลย", 12.5, C["ink"], weight=700))
    out.append(text(16, 24, f"ชนะ {B.fmt(t['โอกาสชนะ'])}% แต่ Expected Value ติดลบ: รอบแพ้อยู่นอกช่วงที่ดู", 13.5, C["ink"], weight=700))
    alt = (f"สองภาพ ซ้าย เส้นทางที่ได้ +1 ติดกัน {n} รอบขึ้นไปถึง +{n} ขณะที่เส้น Expected Value ลงไป {B.fmt(ev_n)} "
           f"แล้วช่วงถัดไปเสีย 120 ครั้งเดียวยอดตกเป็น {B.fmt(after)} ขวา แท่งโอกาสไม่เห็นรอบแพ้เลย "
           + " ".join(f"{k} รอบ {B.fmt(v)}%" for k, v in rows))
    cap = (f"แต่ละรอบ {B.fmt(t['โอกาสชนะ'])}% ได้ +{B.fmt(t['ได้'])} · 1% เสีย {B.fmt(t['เสีย'])} · "
           f"แถบเทา = รอบที่ {n + 1} ซึ่งอยู่นอก {n} รอบที่ดู")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-shape-strips")
def _shape_strips(fig):
    s = fig["ch02"]["แถบผลแนวคิด"]
    # v2: ลำดับแถวตามลำดับที่บทสอน (สัญญา → ให้ Liquidity → Prediction → Carry)
    rows = [("สัญญาบังคับบรรจบ", "ได้ไม่เกินเพดาน · เสียเมื่อปล่อยมือก่อนวันหมดอายุ", s["สัญญาบังคับบรรจบ"], True),
            ("ให้ Liquidity", "ได้นิดเดียวแต่บ่อย · เสียเมื่อได้ขาเดียว", s["ให้สภาพคล่อง"], False),
            ("Prediction", "ได้บ้างเสียบ้าง · บวกได้แค่ค่าเฉลี่ย", s["การพยากรณ์"], False),
            ("Carry", "ได้ทีละนิด · เสียก้อนใหญ่นาน ๆ ครั้ง", s["carry"], False)]
    W, rh, top = 760, 78, 50
    H = top + rh * len(rows) + 12
    L, R = 300, 736
    out = [text(16, 26, "แถบผลของสี่กลไก: รูปร่างต่างกัน", 13.5, C["ink"], weight=700)]
    for i, (name, shape, vals, ceiling) in enumerate(rows):
        y0 = top + rh * i + rh / 2
        if i:
            out.append(f'<line x1="16" y1="{top + rh * i:.1f}" x2="{R}" y2="{top + rh * i:.1f}" stroke="{C["grid"]}"/>')
        out.append(text(16, y0 - 4, name, 12.5, C["ink"], weight=700))
        out.append(text(16, y0 + 14, shape, 11, C["muted"]))
        big = max(abs(v) for v in vals) or 1
        k = (rh / 2 - 8) / big
        gw = (R - L) / len(vals)
        out.append(f'<line x1="{L}" y1="{y0:.1f}" x2="{R}" y2="{y0:.1f}" stroke="{C["axis"]}" stroke-width="1.2"/>')
        for j, v in enumerate(vals):
            x = L + gw * j + gw * .15
            h = max(1.5, abs(v) * k)
            y = y0 - h if v >= 0 else y0
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{gw * .7:.1f}" height="{h:.1f}" fill="{C["green"] if v >= 0 else C["red"]}"/>')
        if ceiling:
            yc = y0 - max(vals) * k - 3
            out.append(f'<line x1="{L}" y1="{yc:.1f}" x2="{R}" y2="{yc:.1f}" stroke="{C["purple"]}" stroke-dasharray="5 4" stroke-width="1.4"/>')
    alt = ("แถบผลสี่แถว สัญญาบังคับบรรจบได้เท่ากันทุกไม้ใต้เพดานยกเว้นไม้ที่ปล่อยมือก่อนวันหมดอายุ "
           "ให้ Liquidity ได้เล็กมากและเสียเป็นระยะ Prediction ได้สลับเสีย Carry ได้เล็กสม่ำเสมอแล้วเสียก้อนใหญ่หนึ่งครั้ง")
    cap = "เขียว = ไม้ที่ได้ · แดง = ไม้ที่เสีย · สเกลแยกต่อแถว · เส้นม่วงประ = เพดานที่สัญญาล็อก"
    return wrap(W, H, alt, out, cap, "แนวคิด")


@chart("sab-strip20")
def _strip20(fig):
    """v2: แถบผลของ 20 ไม้ตัวอย่าง เรียงตามเวลา · แกนตัดที่ −10 (ไม้แพ้ −120 ยาวเกินกรอบ) เพื่อให้เห็นไม้ชนะ Median และ Mean"""
    t = fig["ch02"]["ไม้20"]
    vals = t["ไม้"]
    med, mean = t["มัธยฐาน"], t["ค่าเฉลี่ย"]
    W, H = 760, 300
    L, R, T, Bm = 64, 736, 58, 250
    lo, hi = -10, 2
    Y = lambda v: T + (hi - max(lo, v)) / (hi - lo) * (Bm - T)       # noqa: E731
    out = []
    for g in (-10, -8, -6, -4, -2, 0, 2):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    gw = (R - L) / len(vals)
    for j, v in enumerate(vals):
        x = L + gw * j + gw * .18
        w = gw * .64
        if v >= 0:
            out.append(f'<rect x="{x:.1f}" y="{Y(v):.1f}" width="{w:.1f}" height="{Y(0) - Y(v):.1f}" fill="{C["green"]}"/>')
        else:
            out.append(f'<rect x="{x:.1f}" y="{Y(0):.1f}" width="{w:.1f}" height="{Bm - Y(0):.1f}" fill="{C["red"]}"/>')
            zx = x + w / 2
            out.append(f'<path d="M{x - 3:.1f},{Bm + 2:.1f} l{w / 4 + 1.5:.1f},6 l{w / 4 + 1.5:.1f},-6 l{w / 4 + 1.5:.1f},6 l{w / 4 + 1.5:.1f},-6" '
                       f'fill="none" stroke="{C["red"]}" stroke-width="1.6"/>')
            out.append(text(zx + w / 2 + 6, Bm - 6, f"ไม้ที่ {j + 1}: {B.fmt(v)} (ยาวเกินกรอบ)", 11.5, C["red"], "start", 700))
        if j in (0, len(vals) - 1) or (j + 1) % 5 == 0:
            out.append(text(x + w / 2, Bm + 26, str(j + 1), 10.5, C["grey"], "middle"))
    out.append(f'<line x1="{L}" y1="{Y(med):.1f}" x2="{R}" y2="{Y(med):.1f}" stroke="{C["blue"]}" stroke-dasharray="6 4" stroke-width="1.8"/>')
    out.append(text(R, Y(med) - 8, f"Median {B.fmt(med)}", 11.5, C["blue"], "end", 700))
    out.append(f'<line x1="{L}" y1="{Y(mean):.1f}" x2="{R}" y2="{Y(mean):.1f}" stroke="{C["purple"]}" stroke-dasharray="6 4" stroke-width="1.8"/>')
    out.append(text(L + 6, Y(mean) - 8, f"Mean {B.fmt(mean)}", 11.5, C["purple"], "start", 700))
    out.append(text(16, 26, f"แถบผล {len(vals)} ไม้ เรียงตามเวลา", 13.5, C["ink"], weight=700))
    out.append(text(16, 44, "แท่งเขียวขึ้นเมื่อได้ แท่งแดงลงเมื่อเสีย · ตัวเลขใต้แกนคือไม้ที่", 11, C["muted"]))
    alt = (f"แท่ง {len(vals)} แท่งเรียงตามเวลา ไม้ชนะสูง 0.6 ถึง 1.4 ไม้ที่ {t['ไม้ที่เสีย']} เสีย {B.fmt(t['เฉลี่ยไม้เสีย'])} ยาวเกินกรอบ "
           f"เส้น Median {B.fmt(med)} อยู่บนยอดไม้ชนะ เส้น Mean {B.fmt(mean)} อยู่ต่ำกว่าศูนย์")
    cap = f"ไม้ชนะ {t['ไม้ชนะ']} ไม้ ไม้แพ้ {t['ไม้เสีย']} ไม้ · แกนตั้งตัดที่ −10 แท่งแดงจริงยาวถึง {B.fmt(t['เฉลี่ยไม้เสีย'])}"
    return wrap(W, H, alt, out, cap, "สอน")
