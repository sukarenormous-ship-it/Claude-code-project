"""บท 13 — กลับจริง แต่ทันไหม · สเปกกราฟของบท

sab-mult-table : ตารางคูณเป็นภาพ — ระดับที่คาดของ X จาก 2 ใน 4 ช่วง ที่ φ 0.80 / 0.99 / 1.00 / 1.02
                 + เส้นคุ้มต้นทุน (2 − ต้นทุน ÷ ชุด = 1.8) · ป้ายท้ายเส้นบอกสุทธิหลังต้นทุน 2 (ch13.v2 · ฐานต้นทุน ch11.v2)
sab-paths-fan  : 20 เส้นทางจริงของโลก φ 0.99 แรงสะบัด 0.5 จาก X = 2 (เดินจนแตะ 1 หรือครบ 24 ช่วง)
                 + เส้นค่าเฉลี่ย · เส้นทางที่ถึง 3 ก่อนแตะ 1 เป็นสีแดง
sab-coin-vs-rope (v2): เกมโยนเหรียญ (Random Walk จบที่ 4) กับเกมที่เหลือ 80% ต่อช่วง (จบที่ 0.21) จากจุดเริ่ม 2 เดียวกัน
sab-phi-scatter (v2): 19 คู่วันของ A–B · X วันนี้ กับ X พรุ่งนี้ · เส้นเท่าเดิม (φ 1) กับเส้น φ 0.74 ที่หาด้วยมือ
"""

from sab_charts import chart, wrap, text, C, B

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def _spread(ys, gap=15):
    """เลื่อนป้ายแนวตั้งไม่ให้ทับกัน (เรียงจากบนลงล่าง) · คืนตำแหน่งใหม่ตามลำดับเดิม"""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    out = list(ys)
    for k in range(1, len(order)):
        a, b = order[k - 1], order[k]
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    return out


@chart("sab-mult-table")
def _mult_table(fig):
    c = fig["ch13"]
    rows = c["ตารางphi"]
    rule = c["กติกาตารางphi"]
    hold = rule["ช่วงถือ"]
    cost = c["v2"]["ต้นทุน"]                        # 2 (ฐานต้นทุนเดียว ch11.v2)
    even = c["v2"]["เส้นคุ้มต้นทุน"]                # 1.8 = ต้องลงต่ำกว่านี้จึงคุ้มต้นทุน
    W, H, L, R, T, Bm = 760, 360, 64, 250, 64, 300
    lo, hi = 0.7, 2.25
    X = lambda t: L + t / hold * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, f"คูณ φ ทุกช่วง: เหลือเท่าไรเมื่อครบ {hold} ช่วง", 13, INK, weight=700)]
    for g in (1, 1.5, 2):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for t in range(hold + 1):
        out.append(text(X(t), Bm + 18, f"ช่วง {t}", 10.5, GREY, "middle"))
    # เส้นคุ้มต้นทุน
    out.append(f'<line x1="{L}" y1="{Y(even):.1f}" x2="{W - R}" y2="{Y(even):.1f}" stroke="{C["purple"]}" '
               f'stroke-dasharray="5 4" stroke-width="1.5"/>')
    out.append(text(W - R - 4, Y(even) + 16, f"ต้องลงต่ำกว่า {B.fmt(even)} จึงคุ้มต้นทุน {B.fmt(cost)}", 11, C["purple"], "end", 700))
    cols = {"0.80": C["green"], "0.99": C["amber"], "1.00": GREY, "1.02": C["red"]}
    keys = ["0.80", "0.99", "1.00", "1.02"]
    ends = []
    for k in keys:
        lv = rows[k]["ระดับ"]
        pts = [(X(t), Y(v)) for t, v in enumerate(lv)]
        out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{cols[k]}" stroke-width="2.4" stroke-linejoin="round"/>')
        for x, y in pts:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{cols[k]}"/>')
        ends.append(Y(lv[-1]))
    labs = _spread(ends)
    for k, y0, y in zip(keys, ends, labs):
        r = rows[k]
        net = round(rule["ชุด"] * (rule["เริ่ม"] - r["ระดับ"][-1]) - cost, 2)
        s = f"φ {k} → {B.fmt(c['ปลายทาง4ช่วงปัด'][k])} · สุทธิ {'+' if net > 0 else ''}{B.fmt(net)}"
        out.append(f'<line x1="{W - R + 4}" y1="{y0:.1f}" x2="{W - R + 14}" y2="{y:.1f}" stroke="{cols[k]}"/>')
        out.append(text(W - R + 18, y + 4, s, 11.5, cols[k] if k != "1.00" else MUTED, weight=700))
    alt = ("กราฟเส้นสี่เส้นเริ่มที่ 2 φ 0.80 ลงเหลือ 0.82 ใน 4 ช่วง φ 0.99 ลงเหลือ 1.92 φ 1.00 อยู่ที่ 2 "
           f"φ 1.02 ขึ้นเป็น 2.16 เส้นประคุ้มต้นทุนที่ {B.fmt(even)}")
    cap = f"คูณ φ ทุกช่วง ยังไม่มีแรงสะบัด · short {rule['ชุด']} ชุดที่ X = {B.fmt(rule['เริ่ม'])} · ต้นทุนไปกลับ {B.fmt(cost)}"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-paths-fan")
def _paths_fan(fig):
    f = fig["ch13"]["เส้นทาง20"]
    n_t = f["ช่วง"]
    paths, mean, ev = f["เส้นทาง"], f["เส้นค่าเฉลี่ย"], f["เหตุการณ์"]
    W, H, L, R, T, Bm = 760, 380, 64, 24, 70, 320
    allv = [v for p in paths for v in p]
    lo, hi = min(-1, int(min(allv)) - 1), max(5, int(max(allv)) + 1)
    X = lambda t: L + t / n_t * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "เส้นค่าเฉลี่ยแทบไม่ขยับ เส้นทางจริงไปทั้งสองทาง",
                13, INK, weight=700)]
    for g in range(lo, hi + 1):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for t in range(0, n_t + 1, 4):
        out.append(text(X(t), Bm + 18, f"ช่วง {t}", 10.5, GREY, "middle"))
    for lvl, lab, col in ((1, "เป้า X ≤ 1", C["green"]), (3, "ขอบ X ≥ 3", C["red"])):
        out.append(f'<line x1="{L}" y1="{Y(lvl):.1f}" x2="{W - R}" y2="{Y(lvl):.1f}" stroke="{col}" stroke-dasharray="6 4" stroke-width="1.4"/>')
        out.append(text(W - R - 4, Y(lvl) + (16 if lvl == 1 else -6), lab, 11, col, "end", 700))
    for p, e in zip(paths, ev):
        col = C["red"] if e["ชนิด"] == "ขอบ" else C["green"]
        pts = [(X(t), Y(v)) for t, v in enumerate(p)]
        out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{col}" stroke-width="1.3" stroke-opacity=".55" stroke-linejoin="round"/>')
        if p[-1] <= 1:
            out.append(f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="2.6" fill="{C["green"]}"/>')
        if e["ชนิด"] == "ขอบ":
            t = e["ช่วง"]
            out.append(f'<circle cx="{X(t):.1f}" cy="{Y(p[t]):.1f}" r="2.6" fill="{C["red"]}"/>')
    mpts = [(X(t), Y(v)) for t, v in enumerate(mean)]
    out.append(f'<polyline points="{_poly(mpts)}" fill="none" stroke="{C["purple"]}" stroke-width="3.2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{mpts[-1][0]:.1f}" cy="{mpts[-1][1]:.1f}" r="4.5" fill="{C["purple"]}"/>')
    out.append(text(mpts[-1][0] - 8, mpts[-1][1] - 10, f"เส้นค่าเฉลี่ย {B.fmt(f['ค่าเฉลี่ยที่ช่วง24'])}", 11.5, C["purple"], "end", 700))
    lx = L
    for lab, col in ((f"แตะ 1 ก่อน ({f['แตะเป้าก่อน']} เส้น)", C["green"]), (f"ถึง 3 ก่อนแตะ 1 ({f['ถึงขอบก่อน']} เส้น)", C["red"]),
                     ("เส้นค่าเฉลี่ย", C["purple"])):
        out.append(f'<rect x="{lx}" y="{T - 30}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 20, lab, 11.5, MUTED))
        lx += 34 + 7.2 * len(lab)
    alt = ("กราฟ 20 เส้นทางเริ่มที่ 2 กระจายขึ้นลง บางเส้นลงแตะ 1 บางเส้นขึ้นเกิน 3 ก่อน "
           "เส้นค่าเฉลี่ยสีม่วงค่อย ๆ ลงจาก 2 เหลือ 1.57 อย่างราบเรียบ")
    cap = (f"φ {B.fmt(f['phi'])} แรงสะบัด {B.fmt(f['แรงสะบัด'])} · แต่ละเส้นเดินจนแตะ 1 หรือครบ {n_t} ช่วง")
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab-coin-vs-rope")
def _coin_vs_rope(fig):
    """สองเกมจากจุดเริ่ม 2 เดียวกัน สิบช่วง: เกมโยนเหรียญ (Random Walk · ขั้นบันได ±1) จบที่ 4
    กับเกมที่เหลือ 80% ต่อช่วง (Mean Reversion) จบที่ 0.21 · เส้น Mean 0 · ลูกศรสั้นบอกว่าช่วงแรกถูกดึงมากกว่าช่วงหลัง"""
    g = fig["ch13"]["เดินสุ่ม"]
    rw, mr = g["เดินสุ่ม"], g["เหลือ80เปอร์เซ็นต์"]
    n = len(rw) - 1
    W, H, L, R, T, Bm = 760, 330, 64, 150, 64, 270
    lo, hi = -0.5, max(rw) + 0.6
    X = lambda t: L + t / n * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 24, f"จุดเริ่มเดียวกัน: เกมโยนเหรียญเดินไปจบที่ {B.fmt(rw[-1])} เกมที่มีเชือกถูกดึงกลับจนเหลือ {B.fmt(mr[-1])}",
                13.5, C["ink"], weight=700)]
    for gv in range(0, int(hi) + 1):
        out.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W - R}" y2="{Y(gv):.1f}" stroke="{C["axis"] if gv == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if gv == 0 else 1}"/>')
        out.append(text(L - 8, Y(gv) + 4, B.fmt(gv), 11, GREY, "end"))
    out.append(text(W - R + 8, Y(0) + 16, "Mean 0", 11, MUTED, "start", 700))
    for t in range(n + 1):
        out.append(text(X(t), Bm + 18, f"{t}", 10.5, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 38, "ช่วง", 11, MUTED, "middle"))
    # เกมโยนเหรียญ: ขั้นบันได
    d = f"M{X(0):.1f},{Y(rw[0]):.1f}"
    for t in range(1, n + 1):
        d += f" L{X(t):.1f},{Y(rw[t]):.1f}"
    out.append(f'<path d="{d}" fill="none" stroke="{GREY}" stroke-width="2.4" stroke-linejoin="round"/>')
    for t, v in enumerate(rw):
        out.append(f'<circle cx="{X(t):.1f}" cy="{Y(v):.1f}" r="3.2" fill="{GREY}"/>')
    # เกมที่เหลือ 80%
    pts = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in enumerate(mr))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.8" stroke-linejoin="round"/>')
    for t, v in enumerate(mr):
        out.append(f'<circle cx="{X(t):.1f}" cy="{Y(v):.1f}" r="3.4" fill="{C["blue"]}"/>')
    # ส่วนที่ถูกดึงในช่วงแรกกับช่วงที่ 10
    for t in (1, n):
        a, b = mr[t - 1], mr[t]
        out.append(f'<line x1="{X(t) + 9:.1f}" y1="{Y(a):.1f}" x2="{X(t) + 9:.1f}" y2="{Y(b):.1f}" stroke="{C["purple"]}" stroke-width="2"/>')
    out.append(text(X(1) + 14, (Y(mr[0]) + Y(mr[1])) / 2 + 4, f"ช่วงแรกดึง {B.fmt(round(mr[0] - mr[1], 2))}", 10.5, C["purple"], "start", 700))
    out.append(text(W - R + 8, Y(rw[-1]) + 4, f"เกมโยนเหรียญ {B.fmt(rw[-1])}", 11.5, MUTED, "start", 700))
    out.append(text(W - R + 8, Y(mr[-1]) - 22, "เหลือ 80% ต่อช่วง", 11.5, C["blue"], "start", 700))
    out.append(text(W - R + 8, Y(mr[-1]) - 7, f"จบ {B.fmt(mr[-1])}", 11.5, C["blue"], "start", 700))
    alt = (f"สองเส้นเริ่มที่ 2 เส้นเทาของเกมโยนเหรียญขึ้นลงทีละหนึ่ง {', '.join(B.fmt(v) for v in rw)} จบที่ {B.fmt(rw[-1])} "
           f"เส้นน้ำเงินของเกมที่เหลือ 80% ต่อช่วงลดลงเร็วตอนแรกแล้วช้าลง {', '.join(B.fmt(v) for v in mr)}")
    cap = "เกมบนกระดาษของมิน · โยนเหรียญชุดเดียว (หัว +1 ก้อย −1) · เส้นน้ำเงินไม่มีแรงสะบัด"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-phi-scatter")
def _phi_scatter(fig):
    """19 คู่วันของ A–B (บท 9): แกนนอน X วันนี้ แกนตั้ง X พรุ่งนี้ · เส้นเทาประ = เดาเท่าเดิม (φ 1)
    เส้นม่วง = φ 0.74 ที่หาได้ (ผ่านจุด 0,0 เพราะ Mean 0) · จุดวันที่ 11 → 12 (2.2 → 1.2) ถูกเน้น"""
    xs = fig["ch09"]["นับมือ20วัน"]["X"]
    h = fig["ch13"]["v2"]["phiมือบท9"]
    phi = h["phi"]
    pairs = list(zip(xs[:-1], xs[1:]))
    W, H = 760, 380
    L, R, T, Bm = 250, 250, 56, 336
    lim = 2.5
    X = lambda v: L + (v + lim) / (2 * lim) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v + lim) / (2 * lim) * (Bm - T)  # noqa: E731
    out = [text(16, 24, f"X พรุ่งนี้ ≈ {B.fmt(phi)} × X วันนี้: จุดเอียงตามเส้นที่ลาดน้อยกว่าเส้นเท่าเดิม", 13.5, INK, weight=700)]
    for gv in (-2, -1, 0, 1, 2):
        out.append(f'<line x1="{X(gv):.1f}" y1="{T}" x2="{X(gv):.1f}" y2="{Bm}" stroke="{C["axis"] if gv == 0 else C["grid"]}"/>')
        out.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W - R}" y2="{Y(gv):.1f}" stroke="{C["axis"] if gv == 0 else C["grid"]}"/>')
        out.append(text(X(gv), Bm + 16, B.fmt(gv), 10.5, GREY, "middle"))
        out.append(text(L - 8, Y(gv) + 4, B.fmt(gv), 10.5, GREY, "end"))
    out.append(text((L + W - R) / 2, Bm + 34, "X วันนี้", 11.5, MUTED, "middle", 700))
    out.append(text(L - 8, T - 10, "X พรุ่งนี้", 11.5, MUTED, "end", 700))
    out.append(f'<line x1="{X(-lim):.1f}" y1="{Y(-lim):.1f}" x2="{X(lim):.1f}" y2="{Y(lim):.1f}" stroke="{GREY}" '
               f'stroke-width="1.6" stroke-dasharray="6 4"/>')
    out.append(f'<line x1="{X(-lim):.1f}" y1="{Y(-lim * phi):.1f}" x2="{X(lim):.1f}" y2="{Y(lim * phi):.1f}" stroke="{C["purple"]}" '
               f'stroke-width="2.4"/>')
    for a, b in pairs:
        out.append(f'<circle cx="{X(a):.1f}" cy="{Y(b):.1f}" r="4.2" fill="{C["blue"]}" fill-opacity=".8"/>')
    a, b = xs[10], xs[11]
    out.append(f'<circle cx="{X(a):.1f}" cy="{Y(b):.1f}" r="7" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    out.append(text(X(a) + 12, Y(b) + 4, f"วันที่ 11 → 12: {B.fmt(a)} → {B.fmt(b)}", 10.5, INK, "start", 700))
    out.append(text(W - R + 10, Y(lim) + 4, "เดาเท่าเดิม (φ 1)", 11.5, MUTED, "start", 700))
    out.append(text(W - R + 10, Y(lim * phi) + 4, f"φ {B.fmt(phi)} ที่หาได้", 11.5, C["purple"], "start", 700))
    out.append(text(W - R + 10, Y(lim * phi) + 20, f"= {B.fmt(h['ผลรวมผลคูณ'])} ÷ {B.fmt(h['ผลรวมกำลังสอง'])}", 10.5, C["purple"]))
    alt = (f"กราฟจุด {h['คู่วัน']} จุด แกนนอน X วันนี้ แกนตั้ง X พรุ่งนี้ ของคู่ A–B ช่วง 20 วันในบท 9 "
           f"เส้นประเท่าเดิมลาดหนึ่งต่อหนึ่ง เส้นม่วงลาด {B.fmt(phi)} ผ่านศูนย์ จุดส่วนใหญ่อยู่ใกล้เส้นม่วง")
    cap = f"{h['คู่วัน']} คู่วันจาก X 20 วันของ A–B ในบท 9 · Mean 0 เส้นจึงผ่านจุด (0, 0)"
    return wrap(W, H, alt, out, cap, "สอน")
