"""ภาคผนวก J — กรณีศึกษา 5 เรื่อง (ปลั๊กอินของ tools/sab_charts.py · ตัวเลขทุกตัวอ่านจาก fig["cases"])

sab-cases-venues : เคส 1 · มูลค่าบัญชีของสองแห่งทีละรอบ เทียบระดับรักษาหลักประกัน (แห่ง short หลุดรอบ 3)
sab-cases-ruler  : เคส 3 · X ค้างที่ 2 แต่ Mean แบบเลื่อนไล่ขึ้น · Z-score แบบเลื่อนลงถึงเส้นออก ส่วน Z-score ที่ตรึงไว้อยู่ที่ 2
แกนทุกแกนใช้ค่าจาก JSON (ไม่ใช้ nice_ticks) เพื่อให้ป้ายแกนไม่กลายเป็นเลขลอย
"""

from sab_charts import chart, wrap, text, C, B

LONG, SHORT, MM = C["blue"], C["amber"], C["grey"]


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
        x += 34 + 7.0 * len(name)
    return out


@chart("sab-cases-venues")
def _venues(fig):
    c = fig["cases"]["c1"]
    rs = c["รอบ"]
    cats = ["เปิด"] + [f"รอบ {r['รอบ']}" for r in rs]
    e1 = [c["เงินสดหลังเปิด"]] + [r["equity1"] for r in rs]
    e2 = [c["เงินสดหลังเปิด"]] + [r["equity2"] for r in rs]
    mm = [c["ระดับรักษาตอนเปิด"]] + [r["ระดับรักษา"] for r in rs]
    W, H, L, R, T, Bm = 760, 360, 64, 24, 78, 300
    ticks = [0, c["ระดับรักษาตอนเปิด"], c["หลักประกันเริ่มต้น"], c["ฝากต่อแห่ง"], c["ทางเลือก"]["ขาดทุนที่วิ่ง"],
             c["ทางเลือก"]["ครึ่งมูลค่า"] // 2]
    hi = ticks[-1]
    Y = lambda v: Bm - v / hi * (Bm - T)                 # noqa: E731
    p = [text(L, 24, f"รวมสองแห่งยังมี {B.fmt(rs[-1]['equityรวม'])} แต่แห่ง short เหลือ {B.fmt(rs[-1]['equity2'])} "
                     f"ต่ำกว่าระดับรักษา {B.fmt(rs[-1]['ระดับรักษา'])}", 13, C["ink"], weight=700)]
    p += _legend(L, 52, [("มูลค่าบัญชีแห่งที่ 1 (long)", LONG, "box"), ("มูลค่าบัญชีแห่งที่ 2 (short)", SHORT, "box"),
                         ("ระดับรักษาหลักประกัน", MM, "dash")])
    for t in ticks:
        p.append(f'<line x1="{L}" y1="{Y(t):.1f}" x2="{W - R}" y2="{Y(t):.1f}" stroke="{C["axis"] if t == 0 else C["grid"]}" '
                 f'stroke-width="1"/>')
        p.append(text(L - 8, Y(t) + 4, B.fmt(t), 10.5, C["grey"], "end"))
    gw = (W - L - R) / len(cats)
    bw = 44
    for i, cat in enumerate(cats):
        cx = L + gw * i + gw / 2
        for j, (v, col) in enumerate(((e1[i], LONG), (e2[i], SHORT))):
            x = cx - bw - 3 + j * (bw + 6)
            p.append(f'<rect x="{x:.1f}" y="{Y(v):.1f}" width="{bw}" height="{Bm - Y(v):.1f}" rx="2" fill="{col}"/>')
            p.append(text(x + bw / 2, Y(v) - 6, B.fmt(v), 10.5, col, "middle", 700))
        p.append(f'<line x1="{cx - bw - 10:.1f}" y1="{Y(mm[i]):.1f}" x2="{cx + bw + 10:.1f}" y2="{Y(mm[i]):.1f}" '
                 f'stroke="{C["ink"]}" stroke-width="2" stroke-dasharray="5 3"/>')
        p.append(text(cx, Bm + 18, cat, 11.5, C["muted"], "middle"))
    last = L + gw * (len(cats) - 1) + gw / 2
    p.append(text(last + bw / 2 + 3, Y(mm[-1]) - 22, "หลุดเส้น", 11, C["red"], "middle", 700))
    alt = (f"แท่งคู่สี่กลุ่ม เปิด รอบ 1 ถึง 3 บัญชี long ขึ้นจาก {B.fmt(e1[0])} เป็น {B.fmt(e1[-1])} "
           f"บัญชี short ลงจาก {B.fmt(e2[0])} เป็น {B.fmt(e2[-1])} ต่ำกว่าเส้นระดับรักษา {B.fmt(mm[-1])} ในรอบ 3")
    cap = f"ถือ {B.fmt(c['ขนาดBTC'])} BTC ต่อแห่ง · วางแห่งละ {B.fmt(c['ฝากต่อแห่ง'])} · เส้นประ = ระดับรักษา {B.fmt(c['ระดับรักษาเปอร์เซ็นต์'])}% ของมูลค่าสัญญา ณ ราคาของรอบ"
    return wrap(W, H, alt, p, cap, "สอน")


@chart("sab-cases-ruler")
def _ruler(fig):
    c = fig["cases"]["c3"]
    ds = c["วัน"]
    xs_all = [c["Xก่อนเข้า"]] * 3 + [d["X"] for d in ds]
    W, H, T, Bm = 760, 330, 78, 270
    panels = [(40, 360), (420, 740)]
    p = [text(40, 24, f"X ค้างที่ {B.fmt(c['Xเข้า'])} ทุกวัน แต่ Z-score แบบเลื่อนลงถึง {B.fmt(c['เส้นออก'])} ในวันที่ "
                      f"{c['วันที่ออก']}", 13, C["ink"], weight=700)]
    labels = [f"วัน {k}" if k >= 0 else f"วัน −{-k}" for k in range(-3, len(ds))]
    lo, hi = 0, c["เส้นเข้า"]
    # แผงซ้าย: X กับ Mean
    x0, x1 = panels[0]
    n = len(xs_all)
    X = lambda i, a=x0, b=x1: a + 10 + i / (n - 1) * (b - a - 20)          # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)                     # noqa: E731
    p.append(text(x0, 50, "X กับ Mean", 12, C["ink"], weight=700))
    for t in (lo, c["Meanตรึง"] + c["SDตรึง"], hi):
        p.append(f'<line x1="{x0}" y1="{Y(t):.1f}" x2="{x1}" y2="{Y(t):.1f}" stroke="{C["grid"]}" stroke-width="1"/>')
        p.append(text(x0 - 4, Y(t) + 4, B.fmt(t), 10.5, C["grey"], "end"))
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(xs_all))
    p.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.6"/>')
    p.append(f'<line x1="{X(0):.1f}" y1="{Y(c["Meanตรึง"]) - 2:.1f}" x2="{X(n - 1):.1f}" y2="{Y(c["Meanตรึง"]) - 2:.1f}" '
             f'stroke="{C["purple"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    mpts = [(3 + i, d["Mean"]) for i, d in enumerate(ds)]
    p.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in mpts)}" fill="none" '
             f'stroke="{C["amber"]}" stroke-width="2.2"/>')
    for i, v in mpts:
        p.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{C["amber"]}"/>')
        p.append(text(X(i) + 6, Y(v) + 14, B.fmt(v), 10.5, C["amber"], "start", 700))
    for i, lab in enumerate(labels):
        p.append(text(X(i), Bm + 18, lab, 10, C["grey"], "middle"))
    # แผงขวา: Z-score
    x0, x1 = panels[1]
    m = len(ds)
    X2 = lambda i: x0 + 20 + i / (m - 1) * (x1 - x0 - 40)                 # noqa: E731
    p.append(text(x0, 50, "Z-score ของวันที่ถือ", 12, C["ink"], weight=700))
    for t, lab, col in ((c["เส้นเข้า"], "เส้นเข้า", C["grey"]), (c["เส้นออก"], "เส้นออก", C["red"]), (lo, "", C["axis"])):
        dash = ' stroke-dasharray="4 3"' if lab else ""
        p.append(f'<line x1="{x0}" y1="{Y(t):.1f}" x2="{x1}" y2="{Y(t):.1f}" stroke="{col}" stroke-width="1.2"{dash}/>')
        p.append(text(x0 - 4, Y(t) + 4, B.fmt(t), 10.5, C["grey"], "end"))
        if lab:
            p.append(text(x1, Y(t) - 5, lab, 10.5, col, "end", 700))
    fz = " ".join(f"{X2(i):.1f},{Y(d['Zตรึง']) + 3:.1f}" for i, d in enumerate(ds))
    p.append(f'<polyline points="{fz}" fill="none" stroke="{C["purple"]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
    rz = [(i, d["Z"]) for i, d in enumerate(ds) if d["Z"] is not None]
    p.append(f'<polyline points="{" ".join(f"{X2(i):.1f},{Y(v):.1f}" for i, v in rz)}" fill="none" '
             f'stroke="{C["amber"]}" stroke-width="2.2"/>')
    for i, v in rz:
        p.append(f'<circle cx="{X2(i):.1f}" cy="{Y(v):.1f}" r="4" fill="{C["amber"]}"/>')
        p.append(text(X2(i) + 7, Y(v) - 7, B.fmt(v), 10.5, C["amber"], "start", 700))
    p.append(text(X2(m - 1), Y(lo) - 8, "หารด้วย 0 ไม่ได้", 10, C["muted"], "middle"))
    for i, d in enumerate(ds):
        p.append(text(X2(i), Bm + 18, f"วัน {d['วัน']}", 10, C["grey"], "middle"))
    p += _legend(40, 300 + 10, [("X", C["blue"], "line"), ("ไม้บรรทัดตรึง (Mean และ Z-score)", C["purple"], "dash"),
                                ("ไม้บรรทัดเลื่อน 4 วัน", C["amber"], "line")])
    alt = (f"สองแผง แผงซ้าย X เป็น 0 สามวันแล้วเป็น 2 ค้างไว้ Mean แบบเลื่อน 4 วันไล่ขึ้น "
           f"{', '.join(B.fmt(d['Mean']) for d in ds)} ส่วน Mean ที่ตรึงอยู่ที่ 0 แผงขวา Z-score ที่ตรึงอยู่ที่ 2 ทุกวัน "
           f"Z-score แบบเลื่อนลง {', '.join(B.fmt(d['Z']) for d in ds if d['Z'] is not None)} ถึงเส้นออกในวันที่ 2")
    cap = f"ถือ short X {c['ชุด']} ชุด · ไม้บรรทัดเลื่อนใช้ X {c['หน้าต่าง']} วันล่าสุดรวมวันนี้ · ไม้บรรทัดตรึงคือ Mean {B.fmt(c['Meanตรึง'])} กับ SD {B.fmt(c['SDตรึง'])}"
    return wrap(W, H + 20, alt, p, cap, "สอน")
