"""บท 12 — กฎก่อนกด: สามตอนจบที่ซ้อมไว้ · สเปกกราฟของบท

sab-exit-paths: สี่แผง (2 × 2) เส้นทาง X จากจุดเข้าเดียวกัน 2.1 · เส้นออก 0.5 · เส้นงบ 3.4 (ต้นทุน 2 · ch12.v2) · เส้นเวลา 3 ช่วง
               แผง 4 = งบกับเวลาพร้อมกัน (ลำดับ ขาดทุน → สัญญาณ → เวลา → ออกเพราะงบ)
sab-breakeven-winrate: (v2 ตอน ค · 3) โลกสองตอนจบ: เงินเฉลี่ยต่อไม้ตามสัดส่วนไม้ชนะ · ต้นทุน 2 / 4 / 6 ตัดศูนย์ที่ 59 / 65 / 70%
                (ch12.v2.หน้า.สามต้นทุน) · เส้น 50% ให้เห็นว่าชนะครึ่งหนึ่งยังติดลบทุกเส้น
sab-pair-strip: แถบผล 20 ไม้ของการ์ดเดียวกันในสองโลก (60/25/15 vs 45/20/35) · ลำดับตรึงเพื่อสอน
"""
import re

from sab_charts import chart, wrap, text, slip_strip, Frame, C, B


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
        dy = 36 + j * (h1 + 10)                    # เลื่อนพิกัด y ตรง ๆ (ไม่ใช้ transform ให้ svg_overlap อ่านตำแหน่งจริงได้)
        out += [re.sub(r'\b(y|y1|y2)="(-?[\d.]+)"', lambda m: f'{m.group(1)}="{float(m.group(2)) + dy:.1f}"', ln) for ln in parts]
    H = 36 + 2 * (h1 + 10)
    alt = (f"สองแถบ 20 ไม้ แถวบน {s['หลัก']['จำนวน'][0]} ไม้ได้ {r[0]} · {s['หลัก']['จำนวน'][1]} ไม้ได้ {r[1]} · "
           f"{s['หลัก']['จำนวน'][2]} ไม้เสีย {-r[2]} รวม {B.fmt(s['หลัก']['รวม'])} · แถวล่าง {s['เทียบ']['จำนวน'][0]} · "
           f"{s['เทียบ']['จำนวน'][1]} · {s['เทียบ']['จำนวน'][2]} ไม้ รวม {B.fmt(s['เทียบ']['รวม'])}")
    cap = f"ส่วนผสมสมมติเพื่อซ้อม ไม่ใช่ค่าที่วัด · เขียว = {_sign(r[0])} หรือ {_sign(r[1])} · แดง = {B.fmt(r[2])} · ลำดับไม้ตรึงเพื่อสอน ไม่ใช่ผลสุ่ม"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-breakeven-winrate")
def _breakeven_winrate(fig):
    rows = fig["ch12"]["v2"]["หน้า"]["สามต้นทุน"]
    cols = {"2": C["blue"], "4": C["amber"], "6": C["red"]}
    W, H = 760, 340
    allv = [v for k in rows for v in (rows[k]["สามตอนจบ"][0], rows[k]["สามตอนจบ"][2])]
    f = Frame(min(allv), max(allv), W, H, L=64, R=150, T=70, Bm=280, pad=0.08)
    X = lambda p: f.L + p / 100 * (W - f.L - f.R)                  # noqa: E731
    out = [text(f.L, 24, "ถ้าทุกไม้จบแค่ชนะหรือชนงบ ต้องชนะบ่อยแค่ไหนจึงเท่าทุน", 13, C["ink"], weight=700)]
    out += f.grid([-20, -10, 0, 10])
    for p in (0, 25, 50, 75, 100):
        out.append(text(X(p), f.Bm + 18, f"{p}%", 10.5, C["grey"], "middle"))
    out.append(text((f.L + W - f.R) / 2, f.Bm + 38, "สัดส่วนไม้ที่ชนะ (ที่เหลือคือไม้ที่ชนงบ)", 11.5, C["muted"], "middle"))
    out.append(text(f.L - 50, f.T - 14, "เงินเฉลี่ยต่อไม้", 11, C["muted"]))
    out.append(f'<line x1="{X(50):.1f}" y1="{f.T}" x2="{X(50):.1f}" y2="{f.Bm}" stroke="{C["grey"]}" stroke-dasharray="4 4"/>')
    out.append(text(X(50) - 6, f.T + 12, "ชนะครึ่งหนึ่ง", 11, C["muted"], "end", 700))
    ylab = f.T - 4                                                # ป้ายปลายเส้นเรียงห่างกันอย่างน้อย 16 px
    for k, r in rows.items():
        win, _, lose = r["สามตอนจบ"]
        col = cols[k]
        out.append(f'<line x1="{X(0):.1f}" y1="{f.y(lose):.1f}" x2="{X(100):.1f}" y2="{f.y(win):.1f}" stroke="{col}" '
                   f'stroke-width="2.4" stroke-linecap="round"/>')
        ylab = max(ylab + 16, f.y(win) + 4)
        out.append(text(X(100) + 8, ylab, f"ต้นทุน {k}: +{B.fmt(win)} / {B.fmt(lose)}", 11.5, col, "start", 700))
        be = r["ต้องชนะ"]
        out.append(f'<line x1="{X(be):.1f}" y1="{f.y(0):.1f}" x2="{X(be):.1f}" y2="{f.Bm - 22:.1f}" stroke="{C["purple"]}" '
                   f'stroke-dasharray="2 3" stroke-width="1.2"/>')
        out.append(f'<circle cx="{X(be):.1f}" cy="{f.y(0):.1f}" r="4.5" fill="{C["purple"]}"/>')
        out.append(text(X(be), f.Bm - 8, f"{B.fmt(r['ต้องชนะปัด'])}%", 11.5, C["purple"], "middle", 700))
    out.append(text(X(be) + 24, f.Bm - 8, "จุดเท่าทุน", 11, C["purple"], "start"))
    alt = ("เส้นตรงสามเส้นของเงินเฉลี่ยต่อไม้ตามสัดส่วนไม้ชนะ ต้นทุน 2 ตัดศูนย์ที่ "
           + " · ".join(f"ต้นทุน {k} ตัดศูนย์ที่ {B.fmt(r['ต้องชนะปัด'])}%" for k, r in rows.items())
           + " ที่ชนะครึ่งหนึ่งทุกเส้นยังติดลบ")
    cap = "การ์ดเดียวกัน 10 ชุด · โลกสมมติที่มีแค่ตอนจบ \"ถึงเส้นออก\" กับ \"ชนงบ\" (ไม่มีไม้ครบเวลา) · ยังไม่รวมค่าถือ"
    return wrap(W, H, alt, out, cap, "สอน")
