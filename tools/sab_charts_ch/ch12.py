"""บท 12 — กฎก่อนกด: สามตอนจบที่ซ้อมไว้ · สเปกกราฟของบท

sab-exit-paths: สี่แผง (2 × 2) เส้นทาง X จากจุดเข้าเดียวกัน 2.1 · เส้นออก 0.5 · เส้นงบ 3.4 (ต้นทุน 2 · ch12.v2) · เส้นเวลา 3 ช่วง
               แผง 4 = งบกับเวลาพร้อมกัน (ลำดับ ขาดทุน → สัญญาณ → เวลา → ออกเพราะงบ)
sab-pair-strip: แถบผล 20 ไม้ของการ์ดเดียวกันในสองโลก (60/25/15 vs 45/20/35) · ลำดับตรึงเพื่อสอน
"""
from sab_charts import chart, wrap, text, slip_strip, C, B


_TITLES = {"1": "เส้นทาง 1 · ถึงเส้นออก", "2": "เส้นทาง 2 · ครบเวลา",
           "3": "เส้นทาง 3 · กระโดดข้ามงบ", "4": "เส้นทาง 4 · งบพร้อมเวลา"}


def _sign(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-exit-paths")
def _exit_paths(fig):
    c = fig["ch12"]
    v2 = c["v2"]
    card = fig["บัญชีมิน"]["การ์ด"]
    line_loss = v2["เส้นขาดทุนถึงงบ"]
    tmax = card["ช่วงถือสูงสุด"]
    W, H = 760, 592
    pw, ph = 322, 210                      # ขนาดแผง
    origins = [(40, 70), (40 + pw + 36, 70), (40, 70 + ph + 70), (40 + pw + 36, 70 + ph + 70)]
    lo, hi = -0.5, 4.6
    out = [text(16, 26, f"การ์ดเดียว จุดเข้าเดียว {B.fmt(c['จุดเข้า'])} — สี่ตอนจบ", 14, C["ink"], weight=700)]
    for (ox, oy), k in zip(origins, ("1", "2", "3", "4")):
        p = c["เส้นทาง"][k]
        xs = p["X"]
        Y = lambda v: oy + ph - (v - lo) / (hi - lo) * ph          # noqa: E731
        X = lambda i: ox + (i + 0.45) / (tmax + 0.9) * pw          # noqa: E731  i = ช่วงหลังเข้า (0 = จุดเข้า)
        net = v2["เส้นทาง"][k]["สุทธิ"]
        col = C["green"] if net > 0 else C["red"]
        out.append(text(ox, oy - 12, _TITLES[k], 12.5, C["ink"], weight=700))
        out.append(f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" fill="none" stroke="{C["grid"]}"/>')
        # เส้นอ้างอิง
        for v, lab, cc in ((card["เข้า"], f"เข้า {B.fmt(card['เข้า'])}", C["muted"]),
                           (card["ออก"], f"ออก {B.fmt(card['ออก'])}", C["green"]),
                           (line_loss, f"งบ {B.fmt(card['งบขาดทุนสุทธิ'])} ≈ X {B.fmt(line_loss)}", C["red"])):
            out.append(f'<line x1="{ox}" y1="{Y(v):.1f}" x2="{ox + pw}" y2="{Y(v):.1f}" stroke="{cc}" '
                       f'stroke-dasharray="5 4" stroke-width="1.2" stroke-opacity=".8"/>')
            if k == "1":
                out.append(text(ox + pw - 4, Y(v) - 4, lab, 10, cc, "end"))
        out.append(f'<line x1="{X(tmax):.1f}" y1="{oy}" x2="{X(tmax):.1f}" y2="{oy + ph}" stroke="{C["grey"]}" '
                   f'stroke-dasharray="2 3" stroke-width="1.2"/>')
        if k == "1":
            out.append(text(X(tmax) - 4, oy + 14, f"ครบ {tmax} ช่วง", 10, C["grey"], "end"))
        # เส้นทาง (เริ่มที่จุดเข้า · ไม่วาดจุดก่อนเข้า เพื่อไม่ให้ดูเหมือน X กระโดดจาก 0 ไป 2.1 ในช่วงเดียว)
        pts = " ".join(f"{X(i - 1):.1f},{Y(v):.1f}" for i, v in enumerate(xs) if i >= 1)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.2" stroke-linejoin="round"/>')
        for i, v in enumerate(xs):
            if i == 0:
                continue
            out.append(f'<circle cx="{X(i - 1):.1f}" cy="{Y(v):.1f}" r="3" fill="{C["blue"]}"/>')
            if i >= 2 and i < len(xs) - 1:
                out.append(text(X(i - 1), Y(v) + (16 if k == "1" else -9), B.fmt(v), 10, C["muted"], "middle"))
        # จุดเข้า + จุดออก
        out.append(f'<circle cx="{X(0):.1f}" cy="{Y(xs[1]):.1f}" r="5" fill="{C["purple"]}"/>')
        ex_i = len(xs) - 2
        out.append(f'<circle cx="{X(ex_i):.1f}" cy="{Y(xs[-1]):.1f}" r="5.5" fill="{col}"/>')
        ty = Y(xs[-1]) + (22 if net > 0 else -12)
        if k == "3":
            ty = Y(xs[-1]) + 4
        anchor = "middle" if k == "1" else "end"
        dx = -10 if anchor == "end" else 0
        out.append(text(X(ex_i) + dx, ty, f"ออก {B.fmt(xs[-1])} → {_sign(net)}", 12, col, anchor, 700))
        # แกน x (เฉพาะแผงล่าง · แผงบนใช้แกนเดียวกัน)
        if k in ("3", "4"):
            for i in range(0, tmax + 1):
                out.append(text(X(i), oy + ph + 14, str(i), 9.5, C["grey"], "middle"))
    n = {k: _sign(v2["เส้นทาง"][k]["สุทธิ"]) for k in ("1", "2", "3", "4")}
    alt = (f"สี่แผงจากจุดเข้า 2.1 · เส้นทาง 1 ลง 1.7 แล้ว 0.4 ออกตามสัญญาณ {n['1']} · เส้นทาง 2 ลง 2.0 1.9 1.8 ครบสามช่วง {n['2']} · "
           f"เส้นทาง 3 ขึ้น 2.8 แล้วกระโดดไป 4.1 เลยเส้นงบ {B.fmt(line_loss)} ได้ {n['3']} · เส้นทาง 4 ขึ้น 2.6 3.0 3.7 ครบเวลาพร้อมชนงบ ออกเพราะงบ {n['4']}")
    cap = ("แกนนอน = ช่วงหลังเข้า · เส้นประแดง = X ที่ขาดทุนถึงงบ · ตัวเลขสีคือกำไรสุทธิก่อนค่าถือ · "
           "ระหว่างจุดไม่มีราคาให้ซื้อขาย")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-pair-strip")
def _pair_strip(fig):
    s = fig["ch12"]["v2"]["แถบผล"]
    mix = fig["ch12"]["v2"]["สัดส่วนตอนจบ"]
    r = [fig["ch12"]["v2"]["เส้นทาง"][k]["สุทธิ"] for k in ("1", "2", "3")]
    W, h1 = 760, 176
    out = [text(16, 24, "แถบผล: การ์ดเดียวกัน 20 ไม้ ในสองส่วนผสมซ้อม", 14, C["ink"], weight=700)]
    for j, name in enumerate(("หลัก", "เทียบ")):
        m = mix[name]["สัดส่วน"]
        title = f"ส่วนผสมซ้อม {m[0]}/{m[1]}/{m[2]} (สมมติ) · Expected Value {_sign(mix[name]['ค่าคาดหมาย'])} ต่อไม้"
        parts = slip_strip(s[name]["ลำดับ"], title, W=W, H=h1)
        out.append(f'<g transform="translate(0,{36 + j * (h1 + 10)})">' + "\n".join(parts) + "</g>")
    H = 36 + 2 * (h1 + 10)
    alt = (f"สองแถบ 20 ไม้ แถวบน {s['หลัก']['จำนวน'][0]} ไม้ได้ {r[0]} · {s['หลัก']['จำนวน'][1]} ไม้ได้ {r[1]} · "
           f"{s['หลัก']['จำนวน'][2]} ไม้เสีย {-r[2]} รวม {B.fmt(s['หลัก']['รวม'])} · แถวล่าง {s['เทียบ']['จำนวน'][0]} · "
           f"{s['เทียบ']['จำนวน'][1]} · {s['เทียบ']['จำนวน'][2]} ไม้ รวม {B.fmt(s['เทียบ']['รวม'])}")
    cap = f"ส่วนผสมสมมติเพื่อซ้อม ไม่ใช่ค่าที่วัด · เขียว = {_sign(r[0])} หรือ {_sign(r[1])} · แดง = {B.fmt(r[2])} · ลำดับไม้ตรึงเพื่อสอน ไม่ใช่ผลสุ่ม"
    return wrap(W, H, alt, out, cap, "สอน")
