"""บท 13 — กลับจริง แต่ทันไหม · สเปกกราฟของบท

sab-mult-table : ตารางคูณเป็นภาพ — ระดับที่คาดของ X จาก 2 ใน 4 ช่วง ที่ φ 0.80 / 0.99 / 1.00 / 1.02
                 + เส้นคุ้มต้นทุน (2 − ต้นทุน ÷ ชุด = 1.9) · ป้ายท้ายเส้นบอกสุทธิหลังต้นทุน 1
sab-paths-fan  : 20 เส้นทางจริงของโลก φ 0.99 แรงสะบัด 0.5 จาก X = 2 (เดินจนแตะ 1 หรือครบ 24 ช่วง)
                 + เส้นค่าเฉลี่ย · เส้นทางที่ถึง 3 ก่อนแตะ 1 เป็นสีแดง
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
    cost, hold = rule["ต้นทุน"], rule["ช่วงถือ"]
    even = c["เส้นคุ้มต้นทุน"]                      # 1.9 = ต้องลงต่ำกว่านี้จึงคุ้มต้นทุน
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
        net = r["สุทธิ4ช่วง"]
        s = f"φ {k} → {B.fmt(c['ปลายทาง4ช่วงปัด'][k])} · สุทธิ {'+' if net > 0 else ''}{B.fmt(net)}"
        out.append(f'<line x1="{W - R + 4}" y1="{y0:.1f}" x2="{W - R + 14}" y2="{y:.1f}" stroke="{cols[k]}"/>')
        out.append(text(W - R + 18, y + 4, s, 11.5, cols[k] if k != "1.00" else MUTED, weight=700))
    alt = ("กราฟเส้นสี่เส้นเริ่มที่ 2 φ 0.80 ลงเหลือ 0.82 ใน 4 ช่วง φ 0.99 ลงเหลือ 1.92 φ 1.00 อยู่ที่ 2 "
           "φ 1.02 ขึ้นเป็น 2.16 เส้นประคุ้มต้นทุนที่ 1.9")
    cap = "เส้นค่าเฉลี่ย ไม่ใช่เส้นทาง · φ 0.99 ยังมีแรงดึงกลับ แต่ลงไม่ถึงเส้นคุ้มต้นทุน"
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
    cap = (f"φ {B.fmt(f['phi'])} แรงสะบัด {B.fmt(f['แรงสะบัด'])} · แต่ละเส้นเดินจนแตะ 1 หรือครบ {n_t} ช่วง · "
           f"ถึง 3 ก่อน {B.fmt(fig['ch13']['แตะเป้า'][2]['ขึ้นถึง3ก่อนเปอร์เซ็นต์'])}% จาก 100,000 เส้นทาง")
    return wrap(W, H, alt, out, cap, "จำลอง")
