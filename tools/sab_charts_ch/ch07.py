"""บท 7 — Perp: เชือกที่ไม่มีวันล็อก · สเปกกราฟของบท

sab-funding-paths  (★): funding สะสม 90 รอบของสถานะเดียวกันภายใต้สี่เส้นทาง (ราบ · พุ่งแล้วแผ่ว · กลับขั้ว · สลับ)
                        + เส้นค่าธรรมเนียม maker 80 + จุดที่กฎ "ติดลบ 3 รอบติดแล้วออก" ทำงาน (กลับขั้ว +340 · สลับ −45)
(☆ sab-funding-rounds ยังไม่ทำ — บทชนเพดานคำ)
"""

from sab_charts import chart, wrap, text, Frame, C, B


def _sgn(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-funding-paths")
def _funding_paths(fig):
    c7 = fig["ch07"]
    g, p, rule = c7["กราฟ"], c7["สี่เส้นทาง"], c7["กฎออก"]
    fee = c7["ค่าธรรมเนียมเปิดปิด"]["maker"]
    n = c7["รอบ"]["ใน30วัน"]
    W, H = 760, 370
    f = Frame(0, max(max(v) for v in g.values()), W, H, L=64, R=128, T=64, Bm=290, pad=0.06)
    xs = list(range(1, n + 1))
    X = lambda x: f.L + (x - 1) / (n - 1) * (W - f.L - f.R)  # noqa: E731
    out = f.grid([0, fee, p["สลับ"]["fundingรวม"], p["ราบ"]["fundingรวม"], p["พุ่งแล้วแผ่ว"]["fundingรวม"]])
    # เส้นค่าธรรมเนียม
    yf = f.y(fee)
    out.append(f'<line x1="{f.L}" y1="{yf:.1f}" x2="{W - f.R}" y2="{yf:.1f}" stroke="{C["muted"]}" '
               f'stroke-dasharray="4 4" stroke-width="1.3"/>')
    out.append(text(X(62), yf - 6, f"ค่าธรรมเนียม {B.fmt(fee)} (maker)", 10.5, C["muted"], "middle"))
    # ราบกับกลับขั้วทับกัน 45 รอบแรก: วาดราบเส้นหนาไว้ใต้ ให้เห็นเป็นขอบน้ำเงินรอบเส้นแดง
    series = [("ราบ", C["blue"], "", 5.5), ("พุ่งแล้วแผ่ว", C["green"], "", 2.5), ("กลับขั้ว", C["red"], "", 2.2),
              ("สลับ", C["amber"], ' stroke-dasharray="7 4"', 2.5)]
    for name, col, dash, sw in series:
        pts = " ".join(f"{X(x):.1f},{f.y(v):.1f}" for x, v in zip(xs, g[name]))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{sw}" '
                   f'stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        last = g[name][-1]
        out.append(text(X(n) + 8, f.y(last) + 4, f"{name} {B.fmt(p[name]['fundingรวม'])}", 11.5, col, "start", 700))
    # จุดที่กฎออกทำงาน: ① กลับขั้ว ② สลับ
    pts = [(rule["รอบที่ออกกลับขั้ว"], g["กลับขั้ว"][rule["รอบที่ออกกลับขั้ว"] - 1], "1"),
           (rule["รอบที่ออกสลับ"], g["สลับ"][rule["รอบที่ออกสลับ"] - 1], "2")]
    for x, y, lab in pts:
        out.append(f'<circle cx="{X(x):.1f}" cy="{f.y(y):.1f}" r="8" fill="#fff" stroke="{C["purple"]}" stroke-width="2.2"/>')
        out.append(text(X(x), f.y(y) + 4, lab, 10.5, C["purple"], "middle", 700))
    # ป้ายแกน x (จำนวนรอบ < 100 · ไม่ใช่เลขลอย)
    for x in (1, 30, 45, 60, n):
        out.append(text(X(x), f.Bm + 16, str(x), 10.5, C["grey"], "middle"))
    out.append(text((f.L + W - f.R) / 2, f.Bm + 34, "รอบ funding (90 รอบ = 30 วันในตัวอย่างนี้)", 11.5, C["muted"], "middle"))
    fl, al = p["กลับขั้ว"], p["สลับ"]
    out.append(text(f.L, f.Bm + 64, f"① กลับขั้ว: กฎออกรอบที่ {rule['รอบที่ออกกลับขั้ว']} → สุทธิ "
                    f"{_sgn(fl['กฎmaker'])} (ถือต่อ {_sgn(fl['สุทธิmaker'])})", 11.5, C["purple"], "start", 700))
    out.append(text(f.L + (W - f.L - f.R) / 2 + 20, f.Bm + 64, f"② สลับ: กฎออกรอบที่ {rule['รอบที่ออกสลับ']} → สุทธิ "
                    f"{_sgn(al['กฎmaker'])} (ถือต่อ {_sgn(al['สุทธิmaker'])})", 11.5, C["purple"], "start", 700))
    out.append(text(f.L, f.T - 36, "funding สะสม 90 รอบ ของสถานะเดียวกัน (1 BTC)", 13, C["ink"], weight=700))
    alt = (f"กราฟเส้นสี่เส้น funding สะสม 90 รอบ เส้นทางราบจบที่ {B.fmt(p['ราบ']['fundingรวม'])} "
           f"พุ่งแล้วแผ่วจบที่ {B.fmt(p['พุ่งแล้วแผ่ว']['fundingรวม'])} กลับขั้วขึ้นไปแล้วคืนจนเหลือ 0 "
           f"สลับขึ้นช้า ๆ จบที่ {B.fmt(p['สลับ']['fundingรวม'])} เส้นประค่าธรรมเนียม {B.fmt(fee)} "
           f"กฎออกเมื่อติดลบสามรอบติดช่วยเส้นทางกลับขั้วจาก {B.fmt(fl['สุทธิmaker'])} เป็น {_sgn(fl['กฎmaker'])} "
           f"แต่ทำให้เส้นทางสลับจาก {_sgn(al['สุทธิmaker'])} เหลือ {B.fmt(al['กฎmaker'])}")
    cap = (f"ราคา mark ตรึง 100,000 จึงยังไม่รวมกำไรจากราคาสองขา · กฎเดียวกันช่วยกลับขั้ว "
           f"{_sgn(rule['กลับขั้วต่างจากถือ'])} แต่ทำร้ายสลับ {B.fmt(rule['สลับต่างจากถือ'])}")
    return wrap(W, H, alt, out, cap, "สอน")
