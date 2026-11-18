"""เล่ม 2 บท 10 — PCA: ให้ข้อมูลบอกแรงร่วมเอง · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch10 เท่านั้น)

sab2-pca-rotate   : ซ้าย หกวันของสองเหรียญ (แกนนอน A · แกนตั้ง B) กับแกน PC1 (0.8, 0.6) และ PC2 (−0.6, 0.8) ·
                    ขวา ผลรวมกำลังสองของค่าบนแกนเมื่อหมุนทิศ 0°–180° พร้อมหกทิศที่ลองในหน้า
sab2-pca-loadings : 📡 loading ของ 10 เหรียญ ช่วงเลือกเทียบช่วงตรวจ · แผงบน PC1 · แผงล่าง PC2
sab2-pc1-index    : 📡 ผลตอบแทน log สะสมของช่วงเลือก · พอร์ต PC1 (เงินตาม loading) · Equal-weight Index · BTC
sab2-pca-sim      : 🎲 สองโลกที่รู้คำตอบเทียบข้อมูลจริง · ซ้าย สัดส่วนของ PC2 · ขวา ความตรงทิศของ PC2 ข้ามช่วง
sab2-pca-rolling  : 📡 หน้าต่าง 90 วันเลื่อนทีละ 30 วัน · ความตรงทิศของ PC1 และ PC2 กับ PC ของช่วงเลือกทั้งช่วง
"""

import math

from sab_charts import B, C, chart, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]


def _n(v):
    return B.fmt(int(v)) if float(v).is_integer() else B.fmt(v)


@chart("sab2-pca-rotate")
def _rotate(fig):
    s = fig["ch10"]["สองเหรียญ"]
    W, H = 760, 392
    out = [text(16, 24, "หมุนแกนผ่านกองจุด แล้ววัดว่าค่าบนแกนแกว่งมากแค่ไหน", 13.5, INK, weight=700)]
    # ── แผงซ้าย: จุดหกวัน ──
    cx, cy, sc = 190, 210, 15.5            # จุดกำเนิด · พิกเซลต่อ 1%
    lim = 9
    for g in range(-8, 9, 4):
        out.append(f'<line x1="{cx + g * sc:.1f}" y1="{cy - lim * sc:.1f}" x2="{cx + g * sc:.1f}" y2="{cy + lim * sc:.1f}" stroke="{C["grid"]}"/>')
        out.append(f'<line x1="{cx - lim * sc:.1f}" y1="{cy - g * sc:.1f}" x2="{cx + lim * sc:.1f}" y2="{cy - g * sc:.1f}" stroke="{C["grid"]}"/>')
        if g:
            out.append(text(cx + g * sc, cy + lim * sc + 14, _n(g), 10.5, GREY, "middle"))
            out.append(text(cx - lim * sc - 6, cy - g * sc + 4, _n(g), 10.5, GREY, "end"))
    out.append(f'<line x1="{cx - lim * sc:.1f}" y1="{cy}" x2="{cx + lim * sc:.1f}" y2="{cy}" stroke="{C["axis"]}" stroke-width="1.4"/>')
    out.append(f'<line x1="{cx}" y1="{cy - lim * sc:.1f}" x2="{cx}" y2="{cy + lim * sc:.1f}" stroke="{C["axis"]}" stroke-width="1.4"/>')
    out.append(text(cx + lim * sc, cy + lim * sc + 30, "A ขยับ (%)", 11, MUTED, "end", 700))
    out.append(text(cx - lim * sc, cy - lim * sc - 8, "B ขยับ (%)", 11, MUTED, "start", 700))
    best = s["ดีสุด"]
    p2 = s["pc2"]
    for (a, b), col, dash, lab, ss in (((best["a"], best["b"]), C["purple"], None, "PC1", best["ss"]),
                                       ((p2["a"], p2["b"]), C["amber"], "6 4", "PC2", p2["ss"])):
        L = 7.2
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{cx - a * L * sc:.1f}" y1="{cy + b * L * sc:.1f}" x2="{cx + a * L * sc:.1f}" y2="{cy - b * L * sc:.1f}" '
                   f'stroke="{col}" stroke-width="2.4"{d}/>')
        tx, ty = cx + a * L * sc, cy - b * L * sc
        if a > 0:   # PC1: ป้ายใต้ปลายเส้น (ไม่ทับจุดวันที่ 1)
            out.append(text(tx + 4, ty + 20, f"{lab} ({_n(a)}, {_n(b)})", 11, col, "start", 700))
        else:       # PC2: ป้ายซ้ายของปลายเส้นบน
            out.append(text(tx - 6, ty + 2, f"{lab} ({_n(a)}, {_n(b)})", 11, col, "end", 700))
    for i, (a, b) in enumerate(zip(s["A"], s["B"])):
        out.append(f'<circle cx="{cx + a * sc:.1f}" cy="{cy - b * sc:.1f}" r="5" fill="{C["blue"]}"/>')
        if -2 < a < 0:   # จุดชิดแกนตั้งด้านซ้าย (วันที่ 5): ป้ายไว้ซ้ายจุด ไม่ให้แกนพาดทับ
            out.append(text(cx + a * sc - 7, cy - b * sc + 4, f"วัน {i + 1}", 9.5, MUTED, "end"))
        else:
            out.append(text(cx + a * sc + 7, cy - b * sc + 4, f"วัน {i + 1}", 9.5, MUTED))
    # ── แผงขวา: ผลรวมกำลังสองตามมุม ──
    L2, R2, T2, B2 = 430, 740, 70, 320
    curve = s["เส้นโค้ง"]
    lo, hi = 0, 340
    X = lambda d: L2 + d / 180 * (R2 - L2)  # noqa: E731
    Y = lambda v: B2 - (v - lo) / (hi - lo) * (B2 - T2)  # noqa: E731
    for g in (0, 100, 200, 300):
        out.append(f'<line x1="{L2}" y1="{Y(g):.1f}" x2="{R2}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L2 - 6, Y(g) + 4, _n(g), 10.5, GREY, "end"))
    for d in (0, 45, 90, 135, 180):
        out.append(text(X(d), B2 + 16, f"{d}°", 10.5, GREY, "middle"))
    out.append(text((L2 + R2) / 2, B2 + 34, "มุมของแกนที่หมุนจากแกน A", 11, MUTED, "middle", 700))
    out.append(text(L2, T2 - 14, "ผลรวมกำลังสองของค่าบนแกน (หกวัน)", 11.5, INK, "start", 700))
    pts = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v in curve)
    out.append(f'<polyline points="{pts}" fill="none" stroke="{GREY}" stroke-width="2"/>')
    for r in s["ทิศ"]:
        out.append(f'<circle cx="{X(r["มุม"]):.1f}" cy="{Y(r["ss"]):.1f}" r="4.5" fill="{C["blue"]}"/>')
    out.append(f'<circle cx="{X(best["มุม"]):.1f}" cy="{Y(best["ss"]):.1f}" r="6.5" fill="none" stroke="{C["purple"]}" stroke-width="2.4"/>')
    out.append(text(X(best["มุม"]) + 8, Y(best["ss"]) - 9, f"ยอด {_n(best['ss'])} ที่ {best['มุม']}°", 11, C["purple"], "start", 700))
    a2 = round(math.degrees(math.atan2(p2["b"], p2["a"])))
    out.append(f'<circle cx="{X(a2):.1f}" cy="{Y(p2["ss"]):.1f}" r="6.5" fill="none" stroke="{C["amber"]}" stroke-width="2.4"/>')
    out.append(text(X(a2), Y(p2["ss"]) + 22, f"ต่ำสุด {_n(p2['ss'])} ที่ {a2}°", 11, C["amber"], "middle", 700))
    alt = (f"หกจุดของสองเหรียญเรียงเอียงขึ้นขวา แกน PC1 ทิศ ({_n(best['a'])}, {_n(best['b'])}) ผ่านแนวยาวของกองจุด ผลรวมกำลังสองบนแกนนี้ "
           f"{_n(best['ss'])} สูงสุด แกน PC2 ตั้งฉากได้ {_n(p2['ss'])} ต่ำสุด เมื่อหมุนแกนจาก 0 ถึง 180 องศา ค่าขึ้นลงเป็นคลื่นเดียว")
    cap = f"สองเหรียญสมมติ หกวัน Mean เป็นศูนย์ · จุดน้ำเงินทางขวาคือหกทิศที่ลองในตาราง · ผลรวมทั้งหมด {_n(s['รวม'])} ทุกมุมของคู่แกนที่ตั้งฉากกัน"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab2-pca-loadings")
def _loadings(fig):
    j = fig["ch10"]["จริง"]
    coins = j["เหรียญ"]
    W, H = 760, 470
    out = [text(16, 24, "loading ของ 10 เหรียญ ช่วงเลือกเทียบช่วงตรวจ", 13.5, INK, weight=700)]
    L, R = 64, 24
    gw = (W - L - R) / len(coins)
    bw = 15
    panels = (("PC1", j["pc1"], j["ตรวจ"]["pc1"], 62, 200, j["ตรงทิศ"][0]),
              ("PC2", j["pc2"], j["ตรวจ"]["pc2"], 262, 420, j["ตรงทิศ"][1]))
    for name, f_, v_, top, bot, al in panels:
        lo, hi = -0.8, 0.8
        Y = lambda v, t=top, b=bot: b - (v - lo) / (hi - lo) * (b - t)  # noqa: E731
        for g in (-0.6, -0.3, 0, 0.3, 0.6):
            out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                       f'stroke-width="{1.4 if g == 0 else 1}"/>')
            out.append(text(L - 6, Y(g) + 4, B.fmt(g), 10, GREY, "end"))
        out.append(text(L, top - 10, f"{name} · ความตรงทิศสองช่วง {B.fmt(al)}", 12, INK, "start", 700))
        for i, c in enumerate(coins):
            x0 = L + gw * i + gw / 2
            for k, (vals, col) in enumerate(((f_, C["blue"]), (v_, C["amber"]))):
                v = vals[c]
                x = x0 - bw - 1 + k * (bw + 2)
                y0, y1 = Y(0), Y(v)
                out.append(f'<rect x="{x:.1f}" y="{min(y0, y1):.1f}" width="{bw}" height="{max(1, abs(y1 - y0)):.1f}" rx="2" fill="{col}"/>')
            out.append(text(x0, bot + 16, c, 10.5, MUTED, "middle"))
    lx = W - R - 300
    for nm, col in (("ช่วงเลือก", C["blue"]), ("ช่วงตรวจ", C["amber"])):
        out.append(f'<rect x="{lx}" y="14" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, 24, nm, 11.5, MUTED))
        lx += 110
    alt = (f"PC1 ทุกเหรียญเป็นบวกทั้งสองช่วง ตรงทิศกัน {B.fmt(j['ตรงทิศ'][0])} · PC2 ช่วงเลือกคือ SOL บวก XRP ลบ "
           f"ช่วงตรวจกลายเป็น LTC บวก ADA ลบ ตรงทิศกันเพียง {B.fmt(j['ตรงทิศ'][1])}")
    cap = (f"Binance ราคาปิดรายวัน 10 เหรียญ · ผลตอบแทน log รายวัน · PCA จากความแปรปรวนร่วม · ช่วงเลือก {j['เริ่มเลือก']} ถึง {j['จบเลือก']} · "
           f"ช่วงตรวจ {j['เริ่มตรวจ']} ถึง {j['จบตรวจ']}")
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-pca-sim")
def _sim(fig):
    s = fig["ch10"]["จำลอง"]
    j = fig["ch10"]["จริง"]
    W, H = 760, 350
    out = [text(16, 24, "PC2 จริงหรือแค่แรงสะบัด: สองโลกที่รู้คำตอบเทียบข้อมูลของเล่ม", 13.5, INK, weight=700)]
    groups = (("โลกแรงเดียว", C["grey"]), ("โลกสองแรง", C["green"]), ("ข้อมูลจริง", C["blue"]))
    panels = (
        ("สัดส่วนของ PC2 ในช่วงเลือก (%)", 40, 360, 0, 10,
         [s["W1"]["pc2เปอร์เซ็นต์"], s["W2"]["pc2เปอร์เซ็นต์"], {"มัธยฐาน": j["เปอร์เซ็นต์"][1]}], "%"),
        ("ความตรงทิศของ PC2 ช่วงเลือกกับช่วงตรวจ", 420, 740, 0, 1.1,
         [s["W1"]["ข้ามpc2"], s["W2"]["ข้ามpc2"], {"มัธยฐาน": j["ตรงทิศ"][1]}], ""),
    )
    T, Bm = 76, 290
    for title, L, R, lo, hi, vals, unit in panels:
        Y = lambda v, lo=lo, hi=hi: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
        ticks = (0, 2, 4, 6, 8, 10) if hi > 2 else (0, 0.25, 0.5, 0.75, 1)
        for g in ticks:
            out.append(f'<line x1="{L + 30}" y1="{Y(g):.1f}" x2="{R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
            out.append(text(L + 24, Y(g) + 4, B.fmt(g), 10.5, GREY, "end"))
        out.append(text(L + 30, T - 22, title, 12, INK, "start", 700))
        gw = (R - L - 30) / 3
        for i, ((nm, col), v) in enumerate(zip(groups, vals)):
            x0 = L + 30 + gw * i + gw / 2
            m = v["มัธยฐาน"]
            out.append(f'<rect x="{x0 - 24:.1f}" y="{Y(m):.1f}" width="48" height="{max(1, Y(0) - Y(m)):.1f}" rx="3" fill="{col}"/>')
            if "ต่ำสุด" in v:
                out.append(f'<line x1="{x0:.1f}" y1="{Y(v["ต่ำสุด"]):.1f}" x2="{x0:.1f}" y2="{Y(v["สูงสุด"]):.1f}" stroke="{INK}" stroke-width="1.6"/>')
                for e in (v["ต่ำสุด"], v["สูงสุด"]):
                    out.append(f'<line x1="{x0 - 7:.1f}" y1="{Y(e):.1f}" x2="{x0 + 7:.1f}" y2="{Y(e):.1f}" stroke="{INK}" stroke-width="1.6"/>')
            ytxt = min(Y(m), Y(v.get("สูงสุด", m))) - 8
            out.append(text(x0, ytxt, f"{B.fmt(m)}{unit}", 11, col if col != C["grey"] else INK, "middle", 700))
            out.append(text(x0, Bm + 18, nm, 10.5, MUTED, "middle"))
    alt = (f"สัดส่วน PC2: โลกแรงเดียว {B.fmt(s['W1']['pc2เปอร์เซ็นต์']['มัธยฐาน'])}% โลกสองแรง {B.fmt(s['W2']['pc2เปอร์เซ็นต์']['มัธยฐาน'])}% "
           f"ข้อมูลจริง {B.fmt(j['เปอร์เซ็นต์'][1])}% · ความตรงทิศข้ามช่วง: โลกแรงเดียว {B.fmt(s['W1']['ข้ามpc2']['มัธยฐาน'])} "
           f"โลกสองแรง {B.fmt(s['W2']['ข้ามpc2']['มัธยฐาน'])} ข้อมูลจริง {B.fmt(j['ตรงทิศ'][1])}")
    cap = (f"โลกละ {s['เหรียญ']} เหรียญ {_n(s['วันเลือก'])} + {_n(s['วันตรวจ'])} วัน · สุ่มซ้ำ {s['โลก']} โลก · แท่งคือมัธยฐาน "
           f"เส้นคือต่ำสุดถึงสูงสุด · โลกสองแรงเพิ่มแรงกลุ่มให้ {s['กลุ่มเหรียญ']} เหรียญ · ข้อมูลจริงคือ 10 เหรียญของเล่ม")
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-pca-rolling")
def _rolling(fig):
    j = fig["ch10"]["จริง"]
    rows = j["หน้าต่าง"]
    W, H = 760, 340
    L, R, T, Bm = 64, 24, 70, 270
    n = len(rows)
    X = lambda i: L + i / (n - 1) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - v * (Bm - T)  # noqa: E731
    out = [text(16, 24, f"PC ของหน้าต่าง {j['หน้าต่างวัน']} วัน ตรงทิศกับ PC ของช่วงเลือกทั้งช่วงแค่ไหน", 13.5, INK, weight=700)]
    k0 = next(i for i, r in enumerate(rows) if r["จบ"] > j["จบเลือก"])
    out.append(f'<rect x="{X(k0) - (X(1) - X(0)) / 2:.1f}" y="{T}" width="{W - R - X(k0) + (X(1) - X(0)) / 2:.1f}" height="{Bm - T}" fill="#fef3c7" opacity="0.6"/>')
    out.append(text(W - R - 4, T - 8, "พื้นเหลือง = หน้าต่างที่จบในช่วงตรวจ", 10.5, C["amber"], "end", 700))
    for g in (0, 0.25, 0.5, 0.75, 1):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 10.5, GREY, "end"))
    for key, col, lab in (("ตรงpc1", C["purple"], "PC1"), ("ตรงpc2", C["amber"], "PC2")):
        pts = " ".join(f"{X(i):.1f},{Y(r[key]):.1f}" for i, r in enumerate(rows))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.4"/>')
        for i, r in enumerate(rows):
            out.append(f'<circle cx="{X(i):.1f}" cy="{Y(r[key]):.1f}" r="2.6" fill="{col}"/>')
    for i in range(0, n, 6):
        out.append(text(X(i), Bm + 18, rows[i]["จบ"][:7], 10, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 36, "เดือนที่หน้าต่างจบ", 11, MUTED, "middle", 700))
    lx = L
    for nm, col in (("PC1 ของหน้าต่าง", C["purple"]), ("PC2 ของหน้าต่าง", C["amber"])):
        out.append(f'<rect x="{lx}" y="{T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 20, nm, 11.5, MUTED))
        lx += 150
    alt = (f"PC1 ของทุกหน้าต่างตรงทิศกับช่วงเลือกตั้งแต่ {B.fmt(j['ตรงpc1ต่ำสุด'])} ขึ้นไป ส่วน PC2 กระโดดระหว่าง "
           f"{B.fmt(j['ตรงpc2ต่ำสุด'])} ถึง {B.fmt(j['ตรงpc2สูงสุด'])} และต่ำกว่า 0.5 ใน {j['หน้าต่างครึ่งต่ำ']} จาก {j['หน้าต่างจำนวน']} หน้าต่าง")
    cap = (f"Binance ราคาปิดรายวัน 10 เหรียญ · หน้าต่าง {j['หน้าต่างวัน']} วันเลื่อนทีละ {j['หน้าต่างเลื่อน']} วัน · "
           f"{j['หน้าต่างจำนวน']} หน้าต่าง · {j['หน้าต่างในตรวจ']} หน้าต่างจบในช่วงตรวจ · 1 = ทิศเดียวกัน 0 = ตั้งฉาก")
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-pc1-index")
def _pc1_index(fig):
    j = fig["ch10"]["จริง"]
    c = j["สะสม"]
    ticks = c["แกน"]
    W, H, L, R, T, Bm = 760, 340, 64, 120, 84, 280
    lo, hi = ticks[0] - 25, ticks[-1] + 20
    n = len(c["วัน"])
    X = lambda i: L + i / (n - 1) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 24, "ตัวแทนตลาดสามแบบในช่วงเลือก: ผลตอบแทน log สะสม (%)", 13.5, INK, weight=700)]
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.4 if g == 0 else 1}"/>')
        out.append(text(L - 8, Y(g) + 4, f"{_n(g)}%", 10.5, GREY, "end"))
    for k, i in enumerate(c["ป้ายวัน"]):
        out.append(text(X(i), Bm + 18, c["วัน"][i], 10.5, GREY, "start" if k == 0 else ("end" if i == n - 1 else "middle")))
    series = (("btc", C["amber"], None, "BTC ตัวเดียว"), ("pc1", C["purple"], None, "พอร์ต PC1 (เงินตาม loading)"),
              ("ew", C["green"], "6 4", "Equal-weight Index (ถือสิบเหรียญเท่ากัน)"))
    for key, col, dash, _ in series:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(c[key]))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"{d}/>')
    lx, ly = L, 50
    for key, col, dash, name in series:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{lx}" y1="{ly - 4}" x2="{lx + 22}" y2="{ly - 4}" stroke="{col}" stroke-width="2.6"{d}/>')
        out.append(text(lx + 28, ly, name, 11.5, MUTED))
        lx += 44 + 7.4 * len(name)
    xe = W - R + 8
    out.append(text(xe, Y(c["btc"][-1]) + 4, "BTC", 11.5, C["amber"], "start", 700))
    ym = (Y(c["pc1"][-1]) + Y(c["ew"][-1])) / 2
    out.append(text(xe, ym - 3, "PC1 กับ", 11.5, C["purple"], "start", 700))
    out.append(text(xe, ym + 12, "ดัชนีเท่ากัน", 11.5, C["green"], "start", 700))
    alt = (f"เส้นสะสมของพอร์ต PC1 กับ Equal-weight Index แทบทับกันตลอดสองปี จบราว {_n(c['จบ']['pc1'])} และ {_n(c['จบ']['ew'])} เปอร์เซ็นต์ "
           f"ส่วน BTC แยกออกไปจบราว {_n(c['จบ']['btc'])} เปอร์เซ็นต์")
    cap = (f"Binance ราคาปิดรายวัน 10 เหรียญ · ช่วงเลือก {j['เริ่มเลือก']} ถึง {j['จบเลือก']} · ผลตอบแทน log รายวันบวกสะสม · "
           f"พอร์ต PC1 ถือเงินตาม loading รวมเป็นหนึ่งหน่วย (เหรียญละ {_n(c['น้ำหนักpc1ต่ำสุด'])}% ถึง {_n(c['น้ำหนักpc1สูงสุด'])}%) · จุดละ 7 วัน")
    return wrap(W, H, alt, out, cap, "จริง")
