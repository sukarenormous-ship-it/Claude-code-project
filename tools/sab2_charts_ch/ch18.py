"""บท 18 เล่ม 2 — ปิดเล่ม: โครงงานของคุณเอง · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json เท่านั้น)

sab2-noskill-authors : 🎲 ผู้เขียนที่ไม่มีฝีมือ 30 คน คนละ 190 แบบ × 12 เดือน · Sharpe รายเดือนที่ดีที่สุดของแต่ละคน
                       เทียบ 0.7 ที่งานในกลุ่มแชตอ้าง และเส้นโชค 0.79 จากสูตร
sab2-final-worlds    : 🎲 การ์ดบนปีทดสอบ 365 วัน ในโลกมีเชือก (φ 0.97) และโลกไม่มีเชือก 30 โลกต่อแบบ · Sharpe รายเดือน
                       เทียบเส้นเลื่อนขั้น 0.58 ที่ลงทะเบียนไว้ และ 📡 ผลจริงของช่วงทดสอบสุดท้าย
sab2-final-funding   : 📡 แผนภูมิควบคุมของบท 15 เดินต่อ 24 เดือน (ช่วงตรวจ 12 + ช่วงทดสอบสุดท้าย 12) ของ BTC และ ETH
"""

from sab_charts import B, C, chart, text, wrap

INK, GREY = C["ink"], C["grey"]


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def _strip(out, vals, X, y, col, step=9):
    """จุดเรียงตามค่า ซ้อนขึ้นเมื่อค่าใกล้กัน (ช่องละ 0.04)"""
    seen = {}
    for v in sorted(vals):
        k = round(v / 0.04)
        n = seen.get(k, 0)
        seen[k] = n + 1
        out.append(f'<circle cx="{X(v):.1f}" cy="{y - n * step:.1f}" r="4" fill="{col}" opacity="0.85"/>')


@chart("sab2-noskill-authors")
def _authors(fig):
    c = fig["ch18"]["กระดาษ"]
    w = c["โลก"]
    ticks = fig["ch18"]["แกน"]["ผู้เขียน"]
    W, H, L, R, T, Bm = 760, 300, 40, 30, 70, 220
    lo, hi = ticks[0] - 0.2, ticks[-1]
    X = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)  # noqa: E731
    out = [text(16, 26, "ผู้เขียน 30 คนที่ไม่มีฝีมือ: Sharpe ที่ดีที่สุดจาก 190 แบบของแต่ละคน", 13, INK, weight=700)]
    out.append(f'<line x1="{L}" y1="{Bm}" x2="{W - R}" y2="{Bm}" stroke="{C["axis"]}" stroke-width="1.5"/>')
    for g in ticks:
        out.append(f'<line x1="{X(g):.1f}" y1="{T}" x2="{X(g):.1f}" y2="{Bm}" stroke="{C["grid"]}"/>')
        out.append(text(X(g), Bm + 18, B.fmt(g), 11, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 38, "Sharpe รายเดือนที่ดีที่สุดของผู้เขียนแต่ละคน (12 เดือน)", 11, GREY, "middle"))
    _strip(out, w["ดีสุด"], X, Bm - 8, C["blue"])
    for v, lab, col, dy in ((c["Sharpe"], f"งานในกลุ่มแชตอ้าง {B.fmt(c['Sharpe'])}", C["red"], 46),
                            (c["เส้นโชค"]["เส้น"], f"เส้นโชคจากสูตร {B.fmt(c['เส้นโชค']['เส้น'])}", C["amber"], 64),
                            (w["ดีสุดมัธยฐาน"], f"มัธยฐานของ 30 คน {B.fmt(w['ดีสุดมัธยฐาน'])}", C["purple"], 82)):
        out.append(f'<line x1="{X(v):.1f}" y1="{T - 18}" x2="{X(v):.1f}" y2="{Bm}" stroke="{col}" stroke-width="1.8" stroke-dasharray="5 4"/>')
    out.append(text(X(c["Sharpe"]) - 6, T - 22, f"อ้าง {B.fmt(c['Sharpe'])}", 11, C["red"], "end", 700))
    out.append(text(X(c["เส้นโชค"]["เส้น"]) + 4, T - 22, f"เส้นโชค {B.fmt(c['เส้นโชค']['เส้น'])}", 11, C["amber"], "start", 700))
    out.append(text(X(w["ดีสุดมัธยฐาน"]) + 6, T - 4, f"มัธยฐาน {B.fmt(w['ดีสุดมัธยฐาน'])}", 11, C["purple"], "start", 700))
    out.append(text(W - R, T - 4, f"ถึง {B.fmt(c['Sharpe'])} ได้ {w['ถึงที่อ้าง']} จาก {w['คน']} คน", 11.5, INK, "end", 700))
    alt = (f"จุดสีน้ำเงิน 30 จุดคือ Sharpe ที่ดีที่สุดของผู้เขียนที่ไม่มีฝีมือแต่ละคน ต่ำสุด {B.fmt(w['ต่ำสุด'])} สูงสุด {B.fmt(w['สูงสุด'])} "
           f"มัธยฐาน {B.fmt(w['ดีสุดมัธยฐาน'])} สูงกว่าเส้นโชคจากสูตร {B.fmt(c['เส้นโชค']['เส้น'])} และ {w['ถึงที่อ้าง']} คนถึง {B.fmt(c['Sharpe'])} ที่งานในกลุ่มแชตอ้าง")
    return wrap(W, H, alt, out, "ผลรายเดือนสุ่มจากการแจกแจงปกติที่ Mean 0 · คนละ 190 แบบ แบบละ 12 เดือน · 30 คน", "จำลอง")


@chart("sab2-final-worlds")
def _worlds(fig):
    c = fig["ch18"]
    sim, pre, card = c["โลก"], c["ลงทะเบียน"], c["สุดท้าย"]["การ์ด"]
    ticks = c["แกน"]["Sharpeโลก"]
    bar = pre["เส้นเลื่อนขั้น"]["เส้น"]
    W, H, L, R = 760, 370, 150, 30
    lo, hi = ticks[0] - 0.25, ticks[-1]
    X = lambda v: L + (v - lo) / (hi - lo) * (W - L - R)  # noqa: E731
    rows = [("มีเชือก", "โลกมีเชือก", 160, C["green"]), ("ไม่มีเชือก", "โลกไม่มีเชือก", 300, C["grey"])]
    out = [text(16, 26, "การ์ดหนึ่งปี: Sharpe รายเดือนในโลกที่รู้คำตอบ เทียบผลจริงและเส้นเลื่อนขั้น", 13, INK, weight=700)]
    for g in ticks:
        out.append(f'<line x1="{X(g):.1f}" y1="70" x2="{X(g):.1f}" y2="312" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(X(g), 332, B.fmt(g), 11, GREY, "middle"))
    out.append(text((L + W - R) / 2, 352, "Sharpe รายเดือนของการ์ดในปีทดสอบ (12 เดือน)", 11, GREY, "middle"))
    for key, lab, y, col in rows:
        s = sim[key]
        out.append(f'<line x1="{L}" y1="{y}" x2="{W - R}" y2="{y}" stroke="{C["grid"]}"/>')
        out.append(text(L - 10, y - 6, lab, 11.5, INK, "end", 700))
        out.append(text(L - 10, y + 10, f"ถึงเส้น {s['ถึงเส้นเลื่อนขั้น']} จาก {s['โลก']}", 10.5, GREY, "end"))
        _strip(out, s["Sharpeทุกโลก"], X, y, col, step=7)
    out.append(f'<line x1="{X(bar):.1f}" y1="58" x2="{X(bar):.1f}" y2="312" stroke="{C["purple"]}" stroke-width="1.8" stroke-dasharray="6 4"/>')
    out.append(text(X(bar) + 6, 64, f"เส้นเลื่อนขั้น {B.fmt(bar)}", 11, C["purple"], "start", 700))
    v = card["Sharpe"]
    out.append(f'<line x1="{X(v):.1f}" y1="58" x2="{X(v):.1f}" y2="312" stroke="{C["blue"]}" stroke-width="2.2"/>')
    out.append(text(X(v) - 6, 64, f"ผลจริง {B.fmt(v)}", 11, C["blue"], "end", 700))
    alt = (f"จุดของโลกมีเชือก 30 โลกกระจายจาก {B.fmt(sim['มีเชือก']['Sharpeต่ำสุด'])} ถึง {B.fmt(sim['มีเชือก']['Sharpeสูงสุด'])} "
           f"ถึงเส้นเลื่อนขั้น {B.fmt(bar)} เพียง {sim['มีเชือก']['ถึงเส้นเลื่อนขั้น']} โลก โลกไม่มีเชือกกระจายจาก "
           f"{B.fmt(sim['ไม่มีเชือก']['Sharpeต่ำสุด'])} ถึง {B.fmt(sim['ไม่มีเชือก']['Sharpeสูงสุด'])} ผลจริงของช่วงทดสอบสุดท้าย {B.fmt(v)} "
           f"อยู่กลางกลุ่มของทั้งสองโลก")
    return wrap(W, H, alt, out, "คู่จำลองแบบบท 14 (φ 0.97 และ φ 1) · h และไม้บรรทัดจากช่วงเลือก 731 วัน · การ์ดเข้า 2 ออก 0.5 ถือไม่เกิน 30 วัน 10 ชุด · เส้นสีน้ำเงินคือ 📡 LTC–DOT", "จำลอง")


@chart("sab2-final-funding")
def _funding(fig):
    f = fig["ch18"]["สุดท้าย"]["funding"]
    ticks = fig["ch18"]["แกน"]["funding"]
    months = fig["ch18"]["แกน"]["เดือน"]
    W, H, L, R = 760, 590, 64, 30
    lo, hi = -1, 15
    n = 24
    X = lambda m: L + (m - 1) / (n - 1) * (W - L - R)  # noqa: E731
    out = [text(16, 26, "funding carry: ผลสะสม 24 เดือนเทียบที่คาดจากช่วงเลือก", 13, INK, weight=700)]
    panels = [("BTC", 56, 270), ("ETH", 316, 530)]
    for coin, T, Bm in panels:
        Y = lambda v, T=T, Bm=Bm: Bm - (v - lo) / (hi - lo) * (Bm - T - 20)  # noqa: E731
        rows = f[coin]["แผนภูมิ"]
        out.append(text(L, T + 6, f"{coin} (μ {B.fmt(f[coin]['μ'])} · σ {B.fmt(f[coin]['σ'])} ต่อเดือน)", 12, INK, "start", 700))
        for g in ticks:
            out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
            out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
        xm = (X(12) + X(13)) / 2
        out.append(f'<line x1="{xm:.1f}" y1="{T + 14}" x2="{xm:.1f}" y2="{Bm}" stroke="{GREY}" stroke-dasharray="3 3"/>')
        out.append(text(xm - 6, T + 26, "ช่วงตรวจ", 10.5, GREY, "end"))
        out.append(text(xm + 6, T + 26, "ช่วงทดสอบสุดท้าย", 10.5, GREY, "start"))
        for key, col, dash, wd in (("คาด", GREY, None, 2), ("เตือน", C["amber"], "6 4", 2), ("ลงมือ", C["red"], "6 4", 2),
                                   ("สะสม", C["blue"], None, 2.8)):
            pts = [(X(r["เดือน"]), Y(r[key])) for r in rows]
            d_ = f' stroke-dasharray="{dash}"' if dash else ""
            out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{col}" stroke-width="{wd}"{d_} stroke-linejoin="round"/>')
        last = rows[-1]
        out.append(text(X(n) - 4, Y(last["คาด"]) - 8, f"ที่คาด {B.fmt(last['คาด'])}", 11, GREY, "end", 700))
        m_lab = 15 if coin == "BTC" else 19                 # ตำแหน่งป้ายเส้น: ห่างจากเส้นผลจริงของแต่ละแผง
        out.append(text(X(m_lab), Y(rows[m_lab - 1]["เตือน"]) + (20 if coin == "BTC" else -14), f"เส้นเตือน (เดือน 24: {B.fmt(last['เตือน'])})", 11, C["amber"], "middle", 700))
        out.append(text(X(m_lab), Y(rows[m_lab - 1]["ลงมือ"]) + (20 if coin == "BTC" else -12), f"เส้นลงมือ (เดือน 24: {B.fmt(last['ลงมือ'])})", 11, C["red"], "middle", 700))
        out.append(text(X(n) - 4, Y(last["สะสม"]) + 18, f"ผลจริง {B.fmt(last['สะสม'])}", 11, C["blue"], "end", 700))
        a = f[coin]["ลงมือเดือนแรก"]
        if a:
            r = rows[a - 1]
            out.append(f'<circle cx="{X(a):.1f}" cy="{Y(r["สะสม"]):.1f}" r="6.5" fill="none" stroke="{C["purple"]}" stroke-width="2.4"/>')
            out.append(text(X(a), Y(r["สะสม"]) - 14, f"เดือนที่ {a} แตะเส้นลงมือ", 11, C["purple"], "middle", 700))
        for m in months:
            out.append(text(X(m), Bm + 16, f"{m}", 10.5, GREY, "middle"))
    out.append(text((L + W - R) / 2, H - 10, "เดือนนับจากวันแรกของช่วงตรวจ (เดือนละ 30 วัน)", 11, GREY, "middle"))
    b, e = f["BTC"], f["ETH"]
    alt = (f"สองแผง BTC และ ETH ผลสะสม 24 เดือน BTC จบที่ {B.fmt(b['ปลายสะสม'])} ต่ำกว่าเส้นเตือน {B.fmt(b['ปลายเตือน'])} "
           f"แต่สูงกว่าเส้นลงมือ {B.fmt(b['ปลายลงมือ'])} ETH แตะเส้นลงมือเดือนที่ {e['ลงมือเดือนแรก']} และจบที่ {B.fmt(e['ปลายสะสม'])} "
           f"ขณะที่ที่คาดคือ {B.fmt(e['ปลายคาด'])}")
    return wrap(W, H, alt, out, "Deribit BTC-PERPETUAL และ ETH-PERPETUAL · % ของมูลค่าที่ถือ · ค่าคาดและเส้นจาก Mean และ SD ช่วงเลือก 24 เดือน · เส้นเตือน 1 SD × √n · เส้นลงมือ 2 SD × √n", "จริง")
