"""บท 1 เล่ม 2 — เส้นที่ลากผ่านจุด: h มาจากข้อมูลอย่างไร · ตัวเลขทุกตัวของ docs/sab2-part1.html

ตอน ก  หกวันสมมติของคู่ A–B → ลากเส้นผ่านจุดกลาง · ระยะพลาดของความชัน 2 / 2.5 / 3 · ชามกำลังสอง
       10 × (b − 2.5)² + 5.5 · สูตรความชัน Σ(dB·dA) ÷ Σ(dB²) = cov ÷ var · Intercept
ตอน ข  Residual = X − Mean ของ X (X = A − 2.5B) · R² = 1 − 5.5 ÷ 68 · สลับทิศ (B บน A) ได้ h 68 ÷ 25 = 2.72
       · ค่าผิดปกติหนึ่งจุด (A วันที่ 6 = 111) ดัน h เป็น 3.7
ตอน ค  📡 BTC (A) กับ ETH (B) ช่วงเลือก (formation) เท่านั้น · สองทิศ · เทียบ h มูลค่าเท่ากัน · h วิธีบท 11 เล่ม 1 ·
       ถดถอยบนการขยับรายวัน · ครึ่งแรก/ครึ่งหลัง · หน้าต่าง 60 วัน · Residual ข้ามค่าเฉลี่ยกี่ครั้ง
       🎲 โลกจำลองที่รู้คำตอบ (sab2_sim.stationary_pair · random_walk_pair · sd 0.01 · φ 0.9 · n 731)
       ตัวอย่าง seed 101/102 · สุ่มซ้ำ seed 1–30 ที่ 20 / 60 / 250 / 731 วัน
ค่าเล่ม 1 ที่อ้าง (2.53 · 14.56 ÷ 19.74 · 28 กับ 19) คำนวณซ้ำ/อ่านผ่าน sab_book.load_figures("sab") (ไม่ใช่ข้อมูลจริงของเล่ม 2)
ช่วงทดสอบสุดท้ายไม่ถูกแตะ (ใช้ load_closes("formation") เท่านั้น · ไม่มี unlock_final)
"""

import sab_book as SB


def extend(data, D, q):
    import sab2_sim as M
    import sab2_stats as S
    from sab2_realdata import load_closes

    def r2(x):
        return q(D(str(x)), 2)

    def r1(x):
        return q(D(str(x)), 1)

    def i0(x):
        return q(D(str(x)), 0)

    out = {}

    # ════════════ ตอน ก · หกวันสมมติ ════════════
    A = [95, 98, 101, 98, 103, 105]
    Bp = [48, 49, 50, 50, 51, 52]
    n = len(A)
    mA, mB = sum(A) / n, sum(Bp) / n
    dA = [a - mA for a in A]
    dB = [b - mB for b in Bp]
    sxx = sum(x * x for x in dB)
    sxy = sum(x * y for x, y in zip(dB, dA))
    syy = sum(y * y for y in dA)
    slope = sxy / sxx
    icpt = mA - slope * mB
    ref = S.ols([float(b) for b in Bp], [float(a) for a in A])
    assert abs(ref["slope"] - slope) < 1e-12 and abs(ref["intercept"] - icpt) < 1e-9

    def trial(b):
        miss = [y - b * x for x, y in zip(dB, dA)]
        sq = [m * m for m in miss]
        return {"ความชัน": r2(b), "เส้น": [r2(mA + b * x) for x in dB], "พลาด": [r2(m) for m in miss],
                "กำลังสอง": [r2(s) for s in sq], "รวมพลาด": r2(sum(miss)), "รวมกำลังสอง": r2(sum(sq))}

    lo_b, hi_b = 2.0, 3.0
    tr = {"2": trial(2.0), "2.5": trial(2.5), "3": trial(3.0), "2.4": trial(2.4), "2.6": trial(2.6)}
    left = syy - slope * sxy                                    # กำลังสองที่เหลือที่ก้นชาม
    X = [a - slope * b for a, b in zip(A, Bp)]                  # X ของเล่ม 1 ที่ h = 2.5
    mX = sum(X) / n
    res = [x - mX for x in X]
    assert abs(sum(r * r for r in res) - left) < 1e-9
    out["หกวัน"] = {
        "A": A, "B": Bp, "MeanA": i0(mA), "MeanB": i0(mB), "dA": [i0(v) for v in dA], "dB": [i0(v) for v in dB],
        "dBกำลังสอง": [i0(x * x) for x in dB], "dBคูณdA": [i0(x * y) for x, y in zip(dB, dA)],
        "dAกำลังสอง": [i0(y * y) for y in dA],
        "ผลรวมdBกำลังสอง": i0(sxx), "ผลรวมdBคูณdA": i0(sxy), "ผลรวมdAกำลังสอง": i0(syy),
        "ลอง": tr, "ลองต่ำ": r1(lo_b), "ลองสูง": r1(hi_b),
        "กึ่งกลางสองความชัน": r2((lo_b + hi_b) / 2),
        "ชาม": {"คูณหน้า": i0(sxx), "ก้น": r2(slope), "เหลือที่ก้น": r2(left),
                "ขยาย_b2": i0(sxx), "ขยาย_b": i0(-2 * sxy), "ขยาย_คงที่": i0(syy),
                "ก้นยกกำลังสอง": r2(slope * slope), "ก้นยกกำลังสองคูณ": r2(sxx * slope * slope)},
        "ความชัน": r2(slope), "Intercept": i0(icpt), "ความชันคูณMeanB": r2(slope * mB),
        "ตัวหาร": n - 1, "cov": i0(sxy / (n - 1)), "varB": i0(sxx / (n - 1)), "varA": r2(syy / (n - 1)),
        "X": [r2(v) for v in X], "MeanX": r2(mX), "ผลรวมX": r2(sum(X)), "Residual": [r2(v) for v in res],
        "ผลรวมResidual": r2(sum(res)),
        "ทั้งหมด": i0(syy), "เหลือ": r2(left), "อธิบายได้": r2(syy - left),
        "R2": r2(ref["r2"]), "R2เปอร์เซ็นต์": i0(ref["r2"] * 100), "สัดส่วนเหลือ": r2(left / syy),
        "corr": r2(S.corr([float(b) for b in Bp], [float(a) for a in A])),
        "corrยกกำลังสอง": r2(round(S.corr([float(b) for b in Bp], [float(a) for a in A]), 2) ** 2),
        "BบนAความชัน": r2(sxy / syy), "hจากBบนA": r2(syy / sxy), "อัตราส่วนสองทิศ": r2(slope / (syy / sxy)),
        "หนึ่งต่อความชันปัด": r2(1 / round(sxy / syy, 2)),
        "เลื่อนขึ้น1": {"พลาด": [r2(v - 1) for v in res], "กำลังสอง": [r2((v - 1) ** 2) for v in res],
                       "รวม": r2(sum((v - 1) ** 2 for v in res)), "เพิ่ม": r2(sum((v - 1) ** 2 for v in res) - left)},
        "varX": r2(left / (n - 1)), "SDX": r2((left / (n - 1)) ** 0.5),
        "varXh2": r2(tr["2"]["รวมกำลังสอง"] / (n - 1)), "SDXh2": r2((tr["2"]["รวมกำลังสอง"] / (n - 1)) ** 0.5),
        "รวมกำลังสองที่hBบนA": r2(sxx * (syy / sxy - slope) ** 2 + left),
        "hคูณB": [r2(slope * b) for b in Bp], "Sxyยกกำลังสอง": i0(sxy * sxy), "SxxคูณSyy": i0(sxx * syy),
    }
    # ค่าผิดปกติหนึ่งจุด: A วันที่ 6 จด 111 แทน 105
    Ao = A[:-1] + [111]
    ro = S.ols([float(b) for b in Bp], [float(a) for a in Ao])
    mAo = sum(Ao) / n
    dAo = [a - mAo for a in Ao]
    out["หกวัน"]["ผิดปกติ"] = {
        "A6": 111, "A6เดิม": 105, "MeanA": i0(mAo), "dA": [i0(v) for v in dAo],
        "ผลรวมdBคูณdA": i0(sum(x * y for x, y in zip(dB, dAo))), "ความชัน": r2(ro["slope"]),
        "Intercept": i0(ro["intercept"]), "เปลี่ยนเปอร์เซ็นต์": i0((ro["slope"] / slope - 1) * 100),
        "R2": r2(ro["r2"]),
    }

    # ════════════ ค่าเล่ม 1 ที่อ้าง ════════════
    v1 = SB.load_figures("sab")
    a20 = [float(x) for x in v1["ch09"]["นับมือ20วัน"]["A"]]
    b20 = [float(x) for x in v1["ch09"]["นับมือ20วัน"]["B"]]
    o20 = S.ols(b20, a20)
    phi9 = v1["ch13"]["v2"]["phiมือบท9"]
    out["เล่ม1"] = {
        "SLOPE20วัน": r2(o20["slope"]), "R2_20วัน": r2(o20["r2"]),
        "อัตราส่วนมือ": v1["ch11"]["v2"]["hสองทาง"]["อัตราส่วนมือ"],
        "phiผลรวมผลคูณ": phi9["ผลรวมผลคูณ"], "phiผลรวมกำลังสอง": phi9["ผลรวมกำลังสอง"], "phi": phi9["phi"],
        "Kมูลค่าเท่ากัน": v1["realdata"]["h"]["มูลค่าเท่ากันปัด"], "Kข้อมูล": v1["realdata"]["h"]["ข้อมูลปัด"],
        "Kปีเริ่ม": v1["realdata"]["แหล่ง"]["ปีเริ่ม"], "Kปีจบ": v1["realdata"]["แหล่ง"]["ปีจบ"],
        "Kปีเริ่มข้อความ": str(v1["realdata"]["แหล่ง"]["ปีเริ่ม"]), "Kปีจบข้อความ": str(v1["realdata"]["แหล่ง"]["ปีจบ"]),   # ปีพิมพ์ไม่มีจุลภาค
    }
    assert out["เล่ม1"]["SLOPE20วัน"] == v1["ch11"]["v2"]["hสองทาง"]["SLOPE20วัน"]

    # ════════════ ตอน ค · ข้อมูลจริง (ช่วงเลือกเท่านั้น) ════════════
    dts, px = load_closes("formation")
    dv, pv = load_closes("validation")
    btc, eth = px["BTC"], px["ETH"]
    nf = len(dts)
    ab = S.ols(eth, btc)                    # A บน B: BTC = a + h·ETH
    ba = S.ols(btc, eth)                    # B บน A: ETH = c + g·BTC
    h_ab, h_ba = ab["slope"], 1 / ba["slope"]
    chg = S.ols(S.diff(eth), S.diff(btc))
    moves = sum(abs(x) for x in S.diff(btc)) / sum(abs(x) for x in S.diff(eth))
    half = nf // 2
    h1 = S.ols(eth[:half], btc[:half])
    h2 = S.ols(eth[half:], btc[half:])
    roll60 = [w["slope"] for w in S.rolling_ols(eth, btc, 60) if w]
    roll20 = [w["slope"] for w in S.rolling_ols(eth, btc, 20) if w]
    resid = ab["residuals"]
    cross = sum(1 for a, b in zip(resid, resid[1:]) if a * b < 0)
    rows = []
    for i in list(range(0, nf, 91)):
        fit = ab["intercept"] + h_ab * eth[i]
        rows.append({"วัน": dts[i], "BTC": r2(btc[i]), "ETH": r2(eth[i]), "hคูณETH": r2(h_ab * eth[i]),
                     "เส้น": r2(fit), "Residual": r2(btc[i] - fit)})
    yr = sorted({int(d[:4]) for d in dts + dv} | {2025, 2026})
    out["จริง"] = {
        "ช่วงเลือก": {"เริ่ม": dts[0], "จบ": dts[-1], "วัน": nf},
        "ช่วงตรวจ": {"เริ่ม": dv[0], "จบ": dv[-1], "วัน": len(dv)},
        "ช่วงทดสอบสุดท้าย": {"เริ่ม": "2025-11-15", "จบ": "2026-11-14", "วัน": 365, "เปิดในบท": 17},
        "ปี": yr, "เหรียญ": len(px), "วันรวม": nf + len(dv) + 365,
        "hAบนB": r2(h_ab), "InterceptAบนB": r2(ab["intercept"]), "R2": r2(ab["r2"]), "R2เต็ม": round(ab["r2"], 4),
        "SDResidual": r2(ab["sigma"]),
        "SDResidualSTDEV": r2(S.sd(ab["residuals"])),   # หาร n − 1 แบบ STDEV ของเล่ม 1 (ค่าที่หน้าบท 1 พิมพ์)
        "BบนAต่อBTC1000": r2(ba["slope"] * 1000), "hBบนA": r2(h_ba),
        "hAบนBหารR2": r2(h_ab / ab["r2"]), "อัตราส่วนสองทิศ": r2(h_ab / h_ba),
        "ห่างสองทิศเปอร์เซ็นต์": i0((h_ba / h_ab - 1) * 100),
        "corr": r2(S.corr(btc, eth)), "R2เปอร์เซ็นต์": r1(ab["r2"] * 100),
        "มูลค่าเท่ากันวันแรก": r2(btc[0] / eth[0]), "มูลค่าเท่ากันวันสุดท้าย": r2(btc[-1] / eth[-1]),
        "BTCวันแรก": r2(btc[0]), "ETHวันแรก": r2(eth[0]), "BTCวันสุดท้าย": r2(btc[-1]), "ETHวันสุดท้าย": r2(eth[-1]),
        "วิธีบท11": r2(moves),
        "hการขยับ": r2(chg["slope"]), "R2การขยับ": r2(chg["r2"]),
        "ครึ่งแรก": {"h": r2(h1["slope"]), "R2": r2(h1["r2"]), "จบ": dts[half - 1], "วัน": half},
        "ครึ่งหลัง": {"h": r2(h2["slope"]), "R2": r2(h2["r2"]), "เริ่ม": dts[half], "วัน": nf - half},
        "หน้าต่าง60": {"ต่ำสุด": r2(min(roll60)), "สูงสุด": r2(max(roll60))},
        "หน้าต่าง20": {"ต่ำสุด": r2(min(roll20)), "สูงสุด": r2(max(roll20))},
        "ข้ามMean": cross,
        "ResidualวันแรกBTC": r2(btc[0] - (ab["intercept"] + h_ab * eth[0])),
        "แถว": rows,
        "ชุดกราฟ": {"BTC": [round(v, 2) for v in btc], "ETH": [round(v, 2) for v in eth],
                    "z": [round(v / ab["sigma"], 3) for v in resid], "iครึ่ง": half,
                    "แกนETH": [1000, 2000, 3000, 4000], "แกนBTC": [20000, 40000, 60000, 80000]},
    }
    assert out["จริง"]["อัตราส่วนสองทิศ"] == out["จริง"]["R2"]
    tried = [btc[0] / eth[0], moves, h_ab, h_ba, chg["slope"]]     # วิธีหา h ที่ลองบนช่วงเลือก (สมุดวิจัย · ภาคผนวก H)
    out["จริง"]["จำนวนวิธีหาh"] = len(tried)
    out["จริง"]["hต่ำสุดห้าวิธี"] = r2(min(tried))
    out["จริง"]["hสูงสุดห้าวิธี"] = r2(max(tried))

    # ════════════ 🎲 โลกจำลองที่รู้คำตอบ ════════════
    kw = dict(phi=0.9, sd=0.01)
    rope = M.stationary_pair(seed=101, n=nf, **kw)
    loose = M.random_walk_pair(seed=102, n=nf, sd=0.01)
    o_r = S.ols(rope["B"], rope["A"])
    o_rba = S.ols(rope["A"], rope["B"])
    o_l = S.ols(loose["B"], loose["A"])
    cr_r = sum(1 for a, b in zip(o_r["residuals"], o_r["residuals"][1:]) if a * b < 0)
    cr_l = sum(1 for a, b in zip(o_l["residuals"], o_l["residuals"][1:]) if a * b < 0)

    def rng(world, f, **k):
        r = M.reseed(world, f, **k)
        return {"ต่ำสุด": r2(r["min"]), "มัธยฐาน": r2(r["median"]), "สูงสุด": r2(r["max"])}

    hAB = lambda w: S.ols(w["B"], w["A"])["slope"]                       # noqa: E731
    hBA = lambda w: 1 / S.ols(w["A"], w["B"])["slope"]                   # noqa: E731
    R2f = lambda w: S.ols(w["B"], w["A"])["r2"]                          # noqa: E731
    hCh = lambda w: S.ols(S.diff(w["B"]), S.diff(w["A"]))["slope"]       # noqa: E731
    windows = {}
    for nn in (20, 60, 250, nf):
        windows[str(nn)] = rng(M.stationary_pair, hAB, n=nn, **kw)
    out["จำลอง"] = {
        "h": 2, "phi": 0.9, "แกว่งต่อวันเปอร์เซ็นต์": 1, "วัน": nf, "ชุด": 30,
        "Bแกว่งต่อวันเปอร์เซ็นต์": i0(M.COMMON_SD * 100),
        "แกว่งนิ่งเปอร์เซ็นต์": r1(100 * 0.01 / (1 - 0.81) ** 0.5),
        "ตัวอย่าง": {"hAบนB": r2(o_r["slope"]), "Intercept": r2(o_r["intercept"]), "R2": r2(o_r["r2"]),
                     "R2เปอร์เซ็นต์": r1(o_r["r2"] * 100),
                     "hBบนA": r2(1 / o_rba["slope"]), "hการขยับ": r2(hCh(rope)), "ข้ามMean": cr_r,
                     "Bต่ำสุด": r2(min(rope["B"])), "Bสูงสุด": r2(max(rope["B"]))},
        "ไม่มีเชือก": {"hAบนB": r2(o_l["slope"]), "R2": r2(o_l["r2"]), "R2เปอร์เซ็นต์": r1(o_l["r2"] * 100),
                       "ข้ามMean": cr_l},
        "สุ่มซ้ำ": {"hAบนB": windows[str(nf)], "hBบนA": rng(M.stationary_pair, hBA, n=nf, **kw),
                    "R2": rng(M.stationary_pair, R2f, n=nf, **kw), "hการขยับ": rng(M.stationary_pair, hCh, n=nf, **kw),
                    "ไม่มีเชือกR2": rng(M.random_walk_pair, R2f, n=nf, sd=0.01),
                    "ไม่มีเชือกh": rng(M.random_walk_pair, hAB, n=nf, sd=0.01)},
        "หน้าต่าง": windows, "หน้าต่างวัน": [20, 60, 250, nf],
        "ชุดกราฟ": {"z_มีเชือก": [round(v / o_r["sigma"], 3) for v in o_r["residuals"]],
                    "z_ไม่มีเชือก": [round(v / o_l["sigma"], 3) for v in o_l["residuals"]]},
    }

    # ════════════ แบบฝึก ════════════
    # ข้อ 1: ตารางระยะพลาดของความชัน 2.2 (ผ่านจุดกลาง) · ข้อ 2: เปลี่ยน A วันที่ 3 จาก 101 เป็น 99
    t22 = trial(2.2)
    A2 = [95, 98, 99, 98, 103, 105]
    o2 = S.ols([float(b) for b in Bp], [float(a) for a in A2])
    mA2 = sum(A2) / n
    # ข้อ 3: ถ้าสลับทิศในหกวัน (ทำแล้วในหน้า) → เปลี่ยนเงื่อนไข: B ทุกวันบวก 10 (ความชันไม่เปลี่ยน · Intercept เปลี่ยน)
    B3 = [b + 10 for b in Bp]
    o3 = S.ols([float(b) for b in B3], [float(a) for a in A])
    # ข้อ 5 (ถ่ายโอน · ข้อมูลจริง): ETH บน BTC ในช่วงเลือก ถ้าเลือก A = ETH → h = ความชันของ ETH บน BTC เป็นจำนวน BTC ต่อ ETH
    out["แบบฝึก"] = {
        "ข้อ1": {"พลาด": t22["พลาด"], "กำลังสอง": t22["กำลังสอง"], "รวม": t22["รวมกำลังสอง"],
                 "เทียบชาม": r2(sxx * (2.2 - slope) ** 2 + left)},
        "ข้อ2": {"A": A2, "ผลรวมA": sum(A2), "MeanA": r2(mA2), "ผลรวมdBคูณdA": r2(sum(x * (a - mA2) for x, a in zip(dB, A2))),
                 "ความชัน": r2(o2["slope"]), "Intercept": r2(o2["intercept"]), "R2": r2(o2["r2"])},
        "ข้อ3": {"MeanB": i0(sum(B3) / n), "ความชัน": r2(o3["slope"]), "Intercept": r2(o3["intercept"]),
                 "R2": r2(o3["r2"])},
        "ข้อ5": {"ETHบนBTCต่อBTC1000": out["จริง"]["BบนAต่อBTC1000"], "BTCต่อETH100": r2(ab["slope"] and 100 / ab["slope"]),
                 "BTCต่อETH100ทิศB": r2(ba["slope"] * 100), "ETH100ขยับ": i0(round(ba["slope"] * 1000, 2) * 100),
                 "ETHต่อBTCกลับ": r2(1 / ba["slope"])},
    }
    out["_แบบฝึก"] = [
        {"โจทย์": "ความชัน 2.2 ผ่านจุดกลาง (50, 100): ผลรวมกำลังสองของระยะพลาด", "คำตอบ": t22["รวมกำลังสอง"]},
        {"โจทย์": "A วันที่ 3 เป็น 99: ความชันใหม่", "คำตอบ": r2(o2["slope"])},
        {"โจทย์": "B ทุกวันบวก 10: Intercept ใหม่", "คำตอบ": r2(o3["intercept"])},
        {"โจทย์": "เลือกทิศและ h ของคู่ใหม่ (ตัดสินใจ)"},
        {"โจทย์": "ETH บน BTC ช่วงเลือก: ETH ขยับกี่ดอลลาร์ต่อ BTC 1,000", "คำตอบ": out["จริง"]["BบนAต่อBTC1000"]},
    ]
    return out
