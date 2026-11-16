"""เล่ม 2 บท 11 — ตะกร้าหลายขา · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch11 เท่านั้น)

sab2-basket-sim   : 🎲 โลกตะกร้าที่รู้คำตอบหนึ่งโลก · X ของคู่ A บน B เทียบ X ของตะกร้า A บน B กับ D (ช่วงเลือก 731 วัน)
sab2-basket-crit  : 🎲 เส้น 5% ของ Engle–Granger ตามจำนวนเหรียญในตะกร้า (โลกเดินสุ่ม) · ค่าสถิติตะกร้า 9 เหรียญของต้น
sab2-basket-real  : 📡 Z-score ของตะกร้า XRP บน BTC กับ BNB และคู่ XRP บน BTC · ไม้บรรทัดตรึงจากช่วงเลือก · ช่วงเลือก + ช่วงตรวจ
"""

from sab_charts import B, C, Frame, chart, nice_ticks, text, wrap


def _poly(pts, col, w=2.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" '
            f'stroke-width="{w}" stroke-linejoin="round"{d}/>')


def _legend(out, items, x, y, step=None):
    for name, col in items:
        out.append(f'<rect x="{x}" y="{y - 10}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(x + 16, y, name, 11.5, C["muted"]))
        x += step or (28 + 7.2 * len(name))


@chart("sab2-basket-sim")
def _sim(fig):
    c = fig["ch11"]["จำลอง"]
    ex = c["ตัวอย่าง"]
    pair, bask = ex["คู่"], ex["ตะกร้า"]
    W, H = 760, 340
    lo, hi = min(pair + bask), max(pair + bask)
    f = Frame(lo, hi, W, H, T=78)
    out = f.grid(nice_ticks(lo, hi), "%")
    n = len(pair)
    X = lambda i: f.L + i / (n - 1) * (W - f.L - f.R)  # noqa: E731
    out.append(_poly([(X(i), f.y(v)) for i, v in enumerate(pair)], C["amber"], 1.8))
    out.append(_poly([(X(i), f.y(v)) for i, v in enumerate(bask)], C["blue"], 1.8))
    _legend(out, [(f"คู่ A บน B (ค่าสถิติ {B.fmt(ex['คู่stat'])})", C["amber"]),
                  (f"ตะกร้า A บน B กับ D (ค่าสถิติ {B.fmt(ex['ตะกร้าstat'])})", C["blue"])], f.L, f.T - 22, 270)
    out.append(text(f.L, f.T - 48, "ส่วนที่เหลือจากเส้น (X) ของคู่เทียบตะกร้า ในโลกที่ A = 0.5 × B + 0.5 × D + เชือก", 13, C["ink"], weight=700))
    out.append(text(f.L, f.Bm + 18, "วันที่ 1", 10.5, C["grey"], "start"))
    out.append(text(W - f.R, f.Bm + 18, f"วันที่ {B.fmt(ex['n'])}", 10.5, C["grey"], "end"))
    alt = (f"X ของคู่ A บน B เดินออกห่างจากศูนย์เป็นช่วงยาว ส่วน X ของตะกร้าแกว่งแคบรอบศูนย์ตลอด ค่าสถิติคู่ "
           f"{B.fmt(ex['คู่stat'])} ตะกร้า {B.fmt(ex['ตะกร้าstat'])}")
    cap = (f"โลกตัวอย่างหนึ่งโลกจาก {B.fmt(c['โลก'])} โลก · log ราคา × 100 · เชือก φ {B.fmt(c['phi'])} · B และ D เดินสุ่มอิสระ · "
           f"จุดละ {B.fmt(ex['ทุก'])} วัน")
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-basket-crit")
def _crit(fig):
    c = fig["ch11"]["เส้นตามขา"]
    t = fig["ch11"]["ต้น"]
    ns, vals = c["N"], c["เส้น5"]
    W, H = 760, 340
    lo = min(vals + [t["stat"]])
    f = Frame(lo, 0, W, H, T=78, R=170)
    out = f.grid(nice_ticks(lo, 0))
    gw = (W - f.L - f.R) / len(ns)
    bw = 40
    for i, (k, v) in enumerate(zip(ns, vals)):
        cx = f.L + gw * i + gw / 2
        col = C["purple"] if k == t["ขา"] else C["grey"]
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{f.y(0):.1f}" width="{bw}" height="{f.y(v) - f.y(0):.1f}" rx="2" fill="{col}"/>')
        out.append(text(cx, f.Bm + 22, B.fmt(v), 11.5, C["purple"] if k == t["ขา"] else C["ink"], "middle", 700))
        out.append(text(cx, f.y(0) - 6, f"{k} เหรียญ", 10.5, C["muted"], "middle"))
    xr = W - f.R + 8
    for v, col, dash, l1, l2 in ((c["Mac2"], C["green"], "3 3", "เส้น 5% ของคู่", f"ที่บท 3 ใช้ {B.fmt(c['Mac2'])}"),
                                 (t["stat"], C["red"], "6 4", f"ตะกร้า {B.fmt(t['ขา'])} เหรียญ", f"ของต้น {B.fmt(t['stat'])}")):
        yy = f.y(v)
        out.append(f'<line x1="{f.L}" y1="{yy:.1f}" x2="{W - f.R}" y2="{yy:.1f}" stroke="{col}" stroke-dasharray="{dash}" stroke-width="1.8"/>')
        out.append(text(xr, yy - 2, l1, 11.5, col, weight=700))
        out.append(text(xr, yy + 13, l2, 11.5, col, weight=700))
    out.append(text(f.L, f.T - 48, "เส้น 5% ของ Engle–Granger เมื่อจำนวนเหรียญในตะกร้าเพิ่ม (ยิ่งติดลบยิ่งผ่านยาก)", 13, C["ink"], weight=700))
    out.append(text(f.L, f.T - 26, "แท่งคือค่าที่ 5% ของโลกเดินสุ่มทำได้ดีกว่า · แท่งม่วงคือจำนวนเหรียญเท่าตะกร้าของต้น", 11.5, C["muted"]))
    out.append(text(W - f.R + 8, f.Bm + 22, "← เส้น 5%", 11.5, C["muted"]))
    alt = ("เส้น 5% เลื่อนจาก " + B.fmt(vals[0]) + " ที่ 2 เหรียญ ไปถึง " + B.fmt(vals[-1]) + " ที่ 9 เหรียญ ตะกร้าของต้นได้ " +
           B.fmt(t["stat"]) + " ผ่านเส้นของคู่แต่ไม่ผ่านเส้นของ 9 เหรียญ")
    cap = (f"โลกเดินสุ่มที่ไม่มีเชือกเลย ยาวเท่าช่วงเลือก · {B.fmt(c['แถว'][0]['โลก'])} โลกต่อแท่งสำหรับ 2–3 เหรียญ · "
           f"{B.fmt(c['แถว'][-1]['โลก'])} โลกต่อแท่งสำหรับ 4–9 เหรียญ")
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-basket-real")
def _real(fig):
    r = fig["ch11"]["จริง"]
    zb, zp = r["ตะกร้า"]["zpath"], r["คู่"]["zpath"]
    every = 3
    idx = list(range(0, len(zb), every)) + ([len(zb) - 1] if (len(zb) - 1) % every else [])
    W, H = 760, 340
    lo, hi = min(zb + zp), max(zb + zp)
    f = Frame(lo, hi, W, H, T=78)
    out = f.grid(nice_ticks(lo, hi))
    n = len(zb)
    X = lambda i: f.L + i / (n - 1) * (W - f.L - f.R)  # noqa: E731
    for lv in (2, -2):
        out.append(f'<line x1="{f.L}" y1="{f.y(lv):.1f}" x2="{W - f.R}" y2="{f.y(lv):.1f}" stroke="{C["grey"]}" stroke-dasharray="4 4"/>')
    xv = X(r["วันเลือก"])
    out.append(f'<line x1="{xv:.1f}" y1="{f.T}" x2="{xv:.1f}" y2="{f.Bm}" stroke="{C["ink"]}" stroke-dasharray="2 3"/>')
    out.append(text(xv - 6, f.T + 14, "ช่วงเลือก ←", 11, C["ink"], "end", 700))
    out.append(text(xv + 6, f.T + 14, "→ ช่วงตรวจ", 11, C["ink"], "start", 700))
    out.append(_poly([(X(i), f.y(zp[i])) for i in idx], C["amber"], 1.6))
    out.append(_poly([(X(i), f.y(zb[i])) for i in idx], C["blue"], 1.6))
    _legend(out, [(f"ตะกร้า {r['ตะกร้า']['ชื่อ']}", C["blue"]), (f"คู่ {r['คู่']['ชื่อ']}", C["amber"])], f.L, f.T - 22, 250)
    out.append(text(f.L, f.T - 48, "Z-score จากไม้บรรทัดตรึงของช่วงเลือก (เส้นประเทาคือเส้นเข้า ±2)", 13, C["ink"], weight=700))
    for i, lab, anc in ((0, r["เริ่มเลือก"], "start"), (r["วันเลือก"], r["เริ่มตรวจ"], "middle"), (n - 1, r["จบตรวจ"], "end")):
        out.append(text(X(i), f.Bm + 18, lab, 10.5, C["grey"], anc))
    alt = (f"ในช่วงเลือก Z ของทั้งสองแกว่งในกรอบ ในช่วงตรวจ Z ของตะกร้าพุ่งไปเฉลี่ย {B.fmt(r['ตะกร้า']['ตรวจZเฉลี่ย'])} "
           f"และของคู่ไปเฉลี่ย {B.fmt(r['คู่']['ตรวจZเฉลี่ย'])} ไม่กลับมาที่ศูนย์อีกเลย")
    cap = (f"Binance ราคาปิดรายวัน · ช่วงเลือก {r['เริ่มเลือก']} ถึง {r['จบเลือก']} · ช่วงตรวจ {r['เริ่มตรวจ']} ถึง "
           f"{r['จบตรวจ']} · จุดละ {every} วัน")
    return wrap(W, H, alt, out, cap, "จริง")
