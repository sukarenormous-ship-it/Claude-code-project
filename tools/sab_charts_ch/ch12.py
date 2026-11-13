"""บท 12 — กฎก่อนกด: สามตอนจบที่ซ้อมไว้ · สเปกกราฟของบท

sab-exit-paths: สี่แผง (2 × 2) เส้นทาง X จากจุดเข้าเดียวกัน 2.1 · เส้นออก 0.5 · เส้นงบ 3.5 · เส้นเวลา 3 ช่วง
               แผง 4 = งบกับเวลาพร้อมกัน (ลำดับ ขาดทุน → สัญญาณ → เวลา → ออกเพราะงบ)
sab-pair-strip: แถบผล 20 ไม้ของการ์ดเดียวกันในสองโลก (60/25/15 vs 45/20/35) · ลำดับตรึงเพื่อสอน
"""
from sab_charts import chart, wrap, text, slip_strip, C, B


_TITLES = {"1": "เส้นทาง 1 · กลับถึงเส้นออก", "2": "เส้นทาง 2 · ครบเวลา 3 ช่วง",
           "3": "เส้นทาง 3 · กระโดดข้ามเส้นงบ", "4": "เส้นทาง 4 · งบกับเวลาพร้อมกัน"}


def _sign(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-exit-paths")
def _exit_paths(fig):
    c = fig["ch12"]
    card = fig["บัญชีมิน"]["การ์ด"]
    line_loss = c["เส้นขาดทุนถึงงบ"]
    tmax = card["ช่วงถือสูงสุด"]
    W, H = 760, 560
    pw, ph = 340, 210                      # ขนาดแผง
    origins = [(56, 70), (56 + pw + 40, 70), (56, 70 + ph + 64), (56 + pw + 40, 70 + ph + 64)]
    lo, hi = -0.5, 4.6
    out = [text(16, 26, f"การ์ดเดียว จุดเข้าเดียว {B.fmt(c['จุดเข้า'])} — สี่ตอนจบ", 14, C["ink"], weight=700)]
    for (ox, oy), k in zip(origins, ("1", "2", "3", "4")):
        p = c["เส้นทาง"][k]
        xs = p["X"]
        Y = lambda v: oy + ph - (v - lo) / (hi - lo) * ph          # noqa: E731
        X = lambda i: ox + (i + 1) / (tmax + 1.4) * pw             # noqa: E731  i = อายุ (−1 = ก่อนเข้า)
        net = p["สุทธิ"]
        col = C["green"] if net > 0 else C["red"]
        out.append(text(ox, oy - 12, _TITLES[k], 12.5, C["ink"], weight=700))
        out.append(f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" fill="none" stroke="{C["grid"]}"/>')
        # เส้นอ้างอิง
        for v, lab, cc in ((card["เข้า"], f"เข้า {B.fmt(card['เข้า'])}", C["muted"]),
                           (card["ออก"], f"ออก {B.fmt(card['ออก'])}", C["green"]),
                           (line_loss, f"งบ {B.fmt(card['งบขาดทุนสุทธิ'])} ≈ X {B.fmt(line_loss)}", C["red"])):
            out.append(f'<line x1="{ox}" y1="{Y(v):.1f}" x2="{ox + pw}" y2="{Y(v):.1f}" stroke="{cc}" '
                       f'stroke-dasharray="5 4" stroke-width="1.2" stroke-opacity=".8"/>')
            out.append(text(ox + pw - 4, Y(v) - 4, lab, 10, cc, "end"))
        out.append(f'<line x1="{X(tmax):.1f}" y1="{oy}" x2="{X(tmax):.1f}" y2="{oy + ph}" stroke="{C["grey"]}" '
                   f'stroke-dasharray="2 3" stroke-width="1.2"/>')
        out.append(text(X(tmax) + 3, oy + ph - 6, f"ครบ {tmax} ช่วง", 10, C["grey"]))
        # เส้นทาง
        pts = " ".join(f"{X(i - 1):.1f},{Y(v):.1f}" for i, v in enumerate(xs))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.2" stroke-linejoin="round"/>')
        for i, v in enumerate(xs):
            out.append(f'<circle cx="{X(i - 1):.1f}" cy="{Y(v):.1f}" r="3" fill="{C["blue"]}"/>')
            if i >= 1:
                out.append(text(X(i - 1), Y(v) + (16 if k in ("1", "2") or i == 1 else -9), B.fmt(v), 10, C["muted"], "middle"))
        # จุดเข้า + จุดออก
        out.append(f'<circle cx="{X(0):.1f}" cy="{Y(xs[1]):.1f}" r="5" fill="{C["purple"]}"/>')
        ex_i = len(xs) - 2
        out.append(f'<circle cx="{X(ex_i):.1f}" cy="{Y(xs[-1]):.1f}" r="5.5" fill="{col}"/>')
        ty = Y(xs[-1]) + (22 if net > 0 and xs[-1] < 1 else -12)
        if k == "3":
            ty = Y(xs[-1]) + 4
        anchor = "end" if k in ("3", "4") else "middle"
        dx = -10 if anchor == "end" else 0
        out.append(text(X(ex_i) + dx, ty, f"ออก {B.fmt(xs[-1])} → {_sign(net)}", 12, col, anchor, 700))
        # แกน x
        for i in range(0, len(xs) - 1):
            out.append(text(X(i), oy + ph + 14, f"ช่วง {i}", 9.5, C["grey"], "middle"))
    alt = ("สี่แผงจากจุดเข้า 2.1 · เส้นทาง 1 ลง 1.7 แล้ว 0.4 ออกตามสัญญาณ +16 · เส้นทาง 2 ลง 2.0 1.9 1.8 ครบสามช่วง +2 · "
           "เส้นทาง 3 ขึ้น 2.8 แล้วกระโดดไป 4.1 เลยเส้นงบ 3.5 ได้ −21 · เส้นทาง 4 ขึ้น 2.6 3.0 3.7 ครบเวลาพร้อมชนงบ ออกเพราะงบ −17")
    cap = (f"short X 10 ชุด · ต้นทุนเข้า + ออก 1 · เส้นแดงประ = X ที่ขาดทุนสุทธิถึงงบ {B.fmt(card['งบขาดทุนสุทธิ'])} · "
           f"ตัวเลขสีที่จุดออกคือกำไรสุทธิก่อนค่าถือขา short · เส้นเชื่อมจุดช่วยอ่านลำดับ ไม่ใช่ราคาที่ซื้อขายได้ระหว่างจุด")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-pair-strip")
def _pair_strip(fig):
    s = fig["ch12"]["แถบผล"]
    mix = fig["ch12"]["สัดส่วนตอนจบ"]
    W, h1 = 760, 190
    out = [text(16, 24, "แถบผล: การ์ดเดียวกัน 20 ไม้ ในสองโลก", 14, C["ink"], weight=700)]
    for j, name in enumerate(("หลัก", "เทียบ")):
        m = mix[name]["สัดส่วน"]
        title = f"โลก {m[0]}/{m[1]}/{m[2]} · ค่าคาดหมาย {_sign(mix[name]['ค่าคาดหมาย'])} ต่อไม้"
        parts = slip_strip(s[name]["ลำดับ"], title, W=W, H=h1, label_every=1)
        out.append(f'<g transform="translate(0,{36 + j * (h1 + 10)})">' + "\n".join(parts) + "</g>")
    H = 36 + 2 * (h1 + 10)
    alt = (f"สองแถบ 20 ไม้ แถวบน {s['หลัก']['จำนวน'][0]} ไม้ได้ 16 · {s['หลัก']['จำนวน'][1]} ไม้ได้ 2 · "
           f"{s['หลัก']['จำนวน'][2]} ไม้เสีย 21 รวม {s['หลัก']['รวม']} · แถวล่าง {s['เทียบ']['จำนวน'][0]} · "
           f"{s['เทียบ']['จำนวน'][1]} · {s['เทียบ']['จำนวน'][2]} ไม้ รวม {s['เทียบ']['รวม']}")
    cap = ("เขียว = ไม้ที่ได้ (+16 กลับถึงเส้นออก · +2 ครบเวลา) · แดง = ไม้ที่ชนงบ −21 · ลำดับไม้ตรึงไว้เพื่อสอน ไม่ใช่ผลสุ่ม · "
           f"กติกาเหมือนกันทุกไม้ ต่างกันแค่ว่าโลกส่งไม้แบบไหนมาบ่อยแค่ไหน")
    return wrap(W, H, alt, out, cap, "สอน")
