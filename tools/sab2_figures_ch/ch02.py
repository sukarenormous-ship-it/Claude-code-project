"""บท 2 เล่ม 2 — ราคาหรือ log ราคา · ตัวเลขทุกตัวของ docs/sab2-part2.html

ตอน ก  ไม้บรรทัดที่ยืดตามระดับราคา (ช่องว่าง 2% เท่ากัน: X 2 → 6 เมื่อราคาคูณ 3) · +10% สองครั้ง เทียบ +20 สองครั้ง ·
       นับศูนย์ (log ฐาน 10) → LN · ตาราง r เทียบ LN(1 + r) · log return สามวันบวกกันได้ (+10% · −10% · +5%)
ตอน ข  X แบบ log ของตัวอย่าง 2% (1.98% ทั้งสองระดับ) · ห้าวันด้วยมือบน "จุด log" 100 × LN(ราคา ÷ ราคาวันแรก):
       h 60 ÷ 40 = 1.5 · จาก h แบบ log เป็นเงินต่อขาและจำนวนเหรียญ (h × ราคา A ÷ ราคา B) · ตรวจเงินสองวิธี
ตอน ค  📡 BTC (A) กับ ETH (B) ช่วงเลือก: ถดถอย LN BTC บน LN ETH · ตาราง 9 แถว (ทุก 91 วันแบบบท 1) ·
       ไม้บรรทัดปีแรก → ปีหลัง (ราคา เทียบ log) · ครึ่งปี / การขยับรายวัน · จำนวน ETH ต่อ BTC ตาม h แบบ log
       🎲 โลกที่เชือกอยู่บนเปอร์เซ็นต์ (sab2_sim.stationary_pair h 1.4 · φ 0.9 · sd 0.01 · n 731 · seed 101 + seed 1–30)
       และโลกที่เชือกอยู่บนราคา (sab2_sim.price_pair seed 106) · โลกไม่มีเชือก (random_walk_pair seed 102)
ตอน ง  พังเมื่อไร: การเปลี่ยนใหญ่ (LN 1.5 = 0.41) · ไม่ปรับจำนวนเหรียญ · โลกเชือกบนราคา · ช่วงตรวจ (เปิดดูหนึ่งครั้ง)
ช่วงทดสอบสุดท้ายไม่ถูกแตะ (load_closes("formation") และ "validation" เท่านั้น)
"""

import math


def extend(data, D, q):
    import sab2_sim as M
    import sab2_stats as S
    from sab2_realdata import load_closes

    def r(x, n=2):
        return q(D(repr(float(x))), n)

    def r1(x):
        return r(x, 1)

    def r4(x):
        return r(x, 4)

    def i0(x):
        return q(D(repr(float(x))), 0)

    LN = math.log
    out = {}

    # ════════════ ตอน ก · 1 ไม้บรรทัดที่ยืด ════════════
    gap = 0.02
    early_b, mult = 50, 3
    early_a = 2 * early_b * (1 + gap)
    late_b, late_a = early_b * mult, 2 * early_b * mult * (1 + gap)
    RULER_SD = 2
    out["ยืด"] = {
        "ช่องว่างเปอร์เซ็นต์": i0(gap * 100), "คูณ": mult, "SD": RULER_SD,
        "ต้น": {"B": early_b, "สองเท่าB": 2 * early_b, "A": i0(early_a), "X": i0(early_a - 2 * early_b),
                "Z": i0((early_a - 2 * early_b) / RULER_SD)},
        "หลัง": {"B": late_b, "สองเท่าB": 2 * late_b, "A": i0(late_a), "X": i0(late_a - 2 * late_b),
                 "Z": i0((late_a - 2 * late_b) / RULER_SD)},
    }

    # ════════════ ตอน ก · 2 +10% สองครั้ง เทียบ +20 สองครั้ง ════════════
    pa = [100, 110, 121]
    pb = [100, 120, 140]
    out["สองทาง"] = {
        "คูณ": pa, "บวก": pb,
        "คูณ_ดอลลาร์": [pa[1] - pa[0], pa[2] - pa[1]], "บวก_ดอลลาร์": [pb[1] - pb[0], pb[2] - pb[1]],
        "คูณ_เปอร์เซ็นต์": [i0(100 * (pa[1] / pa[0] - 1)), i0(100 * (pa[2] / pa[1] - 1))],
        "บวก_เปอร์เซ็นต์": [i0(100 * (pb[1] / pb[0] - 1)), r(100 * (pb[2] / pb[1] - 1))],
        "คูณ_รวมเปอร์เซ็นต์": i0(100 * (pa[2] / pa[0] - 1)), "บวก_รวมเปอร์เซ็นต์": i0(100 * (pb[2] / pb[0] - 1)),
        "LNคูณ": [r4(LN(v)) for v in pa], "LNบวก": [r4(LN(v)) for v in pb],
        "LNคูณ_ก้าว": [r4(LN(pa[1]) - LN(pa[0])), r4(LN(pa[2]) - LN(pa[1]))],
        "LNบวก_ก้าว": [r4(LN(pb[1]) - LN(pb[0])), r4(LN(pb[2]) - LN(pb[1]))],
        "LNคูณ_รวม": r4(LN(pa[2]) - LN(pa[0])), "LN121หาร100": r4(LN(1.21)),
        "LN1_1": r4(LN(1.1)), "LN1_1คูณสอง": r4(2 * LN(1.1)),
        # ก้าวจากเลขปัด: 4.7005 − 4.6052 = 0.0953 · 4.7958 − 4.7005 = 0.0953
        "จากเลขปัด": {"ก้าว1": r4(r4(LN(110)) - r4(LN(100))), "ก้าว2": r4(r4(LN(121)) - r4(LN(110))),
                      "รวม": r4(r4(LN(121)) - r4(LN(100)))},
    }
    assert out["สองทาง"]["จากเลขปัด"]["ก้าว1"] == out["สองทาง"]["จากเลขปัด"]["ก้าว2"]
    # นับศูนย์ (log ฐาน 10)
    out["นับศูนย์"] = {"LOG10_200": r(math.log10(200), 3), "LOG10_2": r(math.log10(2), 3),
                       "LOG10_100": 2, "LOG10_1000": 3, "LOG10_100000": 5}

    # ════════════ ตอน ก · 3 log ≈ เปอร์เซ็นต์ ════════════
    rs = [1, 2, 5, 10, 20, 50, -10, -50]
    out["ใกล้เปอร์เซ็นต์"] = {
        "r": rs, "LN": [r4(LN(1 + v / 100)) for v in rs], "LNคูณร้อย": [r(100 * LN(1 + v / 100)) for v in rs],
        "ห่าง": [r(v - 100 * LN(1 + v / 100)) for v in rs],
        "EXP005": r4(math.exp(0.05)), "EXP005เปอร์เซ็นต์": r(100 * (math.exp(0.05) - 1)),
        "LN1_05": r4(LN(1.05)),
    }
    # สามวัน +10% · −10% · +5%
    steps = [10, -10, 5]
    p = [100.0]
    for s in steps:
        p.append(p[-1] * (1 + s / 100))
    lr = [100 * LN(1 + s / 100) for s in steps]
    out["สามวัน"] = {
        "ขยับ": steps, "ราคา": [r(v) for v in p], "รวมเปอร์เซ็นต์ธรรมดา": sum(steps),
        "จริงเปอร์เซ็นต์": r(100 * (p[-1] / p[0] - 1)),
        "logreturn": [r(v) for v in lr], "รวมlog": r(sum(lr)), "LNท้ายหารต้น": r(100 * LN(p[-1] / p[0])),
        "รวมlogจากเลขปัด": r(sum(round(v, 2) for v in lr)),
    }
    assert out["สามวัน"]["รวมlog"] == out["สามวัน"]["LNท้ายหารต้น"]

    # ════════════ ตอน ข · 1 X แบบ log ของตัวอย่าง 2% ════════════
    out["ยืด"]["logX"] = {"ต้น": r(100 * (LN(early_a) - LN(early_b) - LN(2))),
                         "หลัง": r(100 * (LN(late_a) - LN(late_b) - LN(2))), "LN1_02": r4(LN(1.02))}

    # ════════════ ตอน ข · 1 ห้าวันบนจุด log ════════════
    LB = [0, 4, 8, 2, 6]
    LA = [0, 3, 12, 2, 8]
    n5 = len(LB)
    mB5, mA5 = sum(LB) / n5, sum(LA) / n5
    dB5 = [v - mB5 for v in LB]
    dA5 = [v - mA5 for v in LA]
    sxx5 = sum(v * v for v in dB5)
    sxy5 = sum(x * y for x, y in zip(dB5, dA5))
    h5 = sxy5 / sxx5
    c5 = mA5 - h5 * mB5
    res5 = [y - c5 - h5 * x for x, y in zip(LB, LA)]
    PB = [round(50 * math.exp(v / 100), 2) for v in LB]
    PA = [round(100 * math.exp(v / 100), 2) for v in LA]
    # ตรวจว่าราคาปัดสองตำแหน่งให้จุด log ปัดเป็นจำนวนเต็มเท่าเดิม
    assert [round(100 * LN(v / PB[0])) for v in PB] == LB
    assert [round(100 * LN(v / PA[0])) for v in PA] == LA
    ref5 = S.ols([float(v) for v in LB], [float(v) for v in LA])
    assert abs(ref5["slope"] - h5) < 1e-12
    ref5p = S.ols(PB, PA)
    X5 = [y - h5 * x for x, y in zip(LB, LA)]
    out["ห้าวัน"] = {
        "B": PB, "A": PA, "LB": LB, "LA": LA, "MeanLB": i0(mB5), "MeanLA": i0(mA5),
        "dB": [i0(v) for v in dB5], "dA": [i0(v) for v in dA5],
        "dBกำลังสอง": [i0(v * v) for v in dB5], "dBคูณdA": [i0(x * y) for x, y in zip(dB5, dA5)],
        "ผลรวมdBกำลังสอง": i0(sxx5), "ผลรวมdBคูณdA": i0(sxy5), "h": r(h5, 1), "ค่าตัดแกน": i0(c5),
        "hคูณMeanLB": i0(h5 * mB5), "X": [r(v, 1) for v in X5], "Residual": [i0(v) for v in res5],
        "ผลรวมResidual": i0(sum(res5)), "R2": r(ref5["r2"]),
        "hราคา": r(ref5p["slope"]),
        "LN_B1": r4(LN(PB[1] / PB[0])), "LN_A2": r4(LN(PA[2] / PA[0])),
    }

    # ════════════ ตอน ข · 2 จาก h แบบ log เป็นเงินและเหรียญ ════════════
    VA = 1000
    coinsA = VA / PA[0]
    VB = h5 * VA
    coinsB = VB / PB[0]
    # วันที่ 1 → 2
    legA = coinsA * (PA[1] - PA[0])
    legB = -coinsB * (PB[1] - PB[0])
    dX = (LA[1] - h5 * LB[1]) - (LA[0] - h5 * LB[0])
    # ตัวอย่างเลขกลม: B +2% A +3% (ตามเชือก) · B +2% A +4% (หลุดเชือก 1 จุด)
    b2 = PB[0] * 1.02
    on_a, off_a = PA[0] * 1.03, PA[0] * 1.04
    legA_on, legA_off = coinsA * (on_a - PA[0]), coinsA * (off_a - PA[0])
    legB_2 = -coinsB * (b2 - PB[0])
    dX_off = LN(1.04) - h5 * LN(1.02)
    # วันที่ 3: ราคาเปลี่ยน → จำนวน B ต่อ A ที่ต้องถือเปลี่ยน
    out["เงิน"] = {
        "VA": VA, "เหรียญA": i0(coinsA), "VB": i0(VB), "เหรียญB": i0(coinsB),
        "Bต่อA": i0(h5 * PA[0] / PB[0]), "ราคาAหารB": i0(PA[0] / PB[0]),
        "วัน2": {"ขาA": r(legA), "ขาB": r(legB), "รวม": r(legA + legB), "Aขยับ": r(PA[1] - PA[0]),
                 "Bขยับ": r(PB[1] - PB[0]), "dXจุด": i0(dX), "dXเงิน": i0(dX / 100 * VA)},
        "ตามเชือก": {"Bใหม่": r(b2), "Aใหม่": r(on_a), "ขาA": r(legA_on), "ขาB": r(legB_2), "รวม": r(legA_on + legB_2)},
        "หลุด": {"Aใหม่": r(off_a), "ขาA": r(legA_off), "ขาB": r(legB_2), "รวม": r(legA_off + legB_2),
                 "LN1_04": r4(LN(1.04)), "LN1_02": r4(LN(1.02)), "hคูณLN1_02": r4(h5 * LN(1.02)),
                 "dX": r4(dX_off), "dXเงิน": r(dX_off * VA)},
        "วัน3": {"Bต่อA": r(h5 * PA[2] / PB[2]), "A": PA[2], "B": PB[2], "ราคาAหารB": r(PA[2] / PB[2])},
    }

    # ════════════ ตอน ค · ข้อมูลจริง (ช่วงเลือกเท่านั้น) ════════════
    dts, px = load_closes("formation")
    btc, eth = px["BTC"], px["ETH"]
    nf = len(dts)
    half = nf // 2
    lb, le = S.logs(btc), S.logs(eth)
    op = S.ols(eth, btc)
    ol = S.ols(le, lb)
    hl, cl = ol["slope"], ol["intercept"]
    Xl = [100 * v for v in ol["residuals"]]           # X แบบ log เป็นเปอร์เซ็นต์ (ลบ Mean แล้ว · Mean ของ residual = 0)
    Xp = op["residuals"]
    sdl, sdp = S.sd(Xl), S.sd(Xp)
    cross_l = sum(1 for a, b in zip(Xl, Xl[1:]) if (a > 0) != (b > 0))
    cross_p = sum(1 for a, b in zip(Xp, Xp[1:]) if (a > 0) != (b > 0))
    zl = [v / sdl for v in Xl]
    zp = [v / sdp for v in Xp]
    # จุด log แบบห้าวัน: 100 × LN(ราคา ÷ ราคาวันแรกของช่วงเลือก) · h ไม่เปลี่ยน · ค่าตัดแกนเปลี่ยนหน่วย
    pa_ = [100 * (v - lb[0]) for v in lb]
    pb_ = [100 * (v - le[0]) for v in le]
    oc = S.ols(pb_, pa_)
    assert abs(oc["slope"] - hl) < 1e-9
    rows, gaps = [], []
    for i in range(0, nf, 91):
        x_pct = 100 * (lb[i] - cl - hl * le[i])
        assert abs(x_pct - (pa_[i] - hl * pb_[i] - oc["intercept"])) < 1e-9
        hand = round(pa_[i], 2) - round(hl, 2) * round(pb_[i], 2) - round(oc["intercept"], 2)
        gaps.append(abs(hand - x_pct))
        rows.append({"วัน": dts[i], "BTC": r(btc[i]), "ETH": r(eth[i]), "LNBTC": r4(lb[i]), "LNETH": r4(le[i]),
                     "จุดBTC": r(pa_[i]), "จุดETH": r(pb_[i]), "X": r1(x_pct), "Xจากเลขปัด": r(hand)})

    def ruler(x, y):
        """ไม้บรรทัดจากปีแรก (h · Mean · SD ของครึ่งแรก) ใช้วัดทุกวัน → Z ทั้งช่วง + สรุปปีหลัง"""
        a = S.ols(x[:half], y[:half])
        X = [yy - a["slope"] * xx for xx, yy in zip(x, y)]
        m, s = S.mean(X[:half]), S.sd(X[:half])
        z = [(v - m) / s for v in X]
        z2 = z[half:]
        out_ = sum(1 for v in z2 if abs(v) > 2)
        return {"h": a["slope"], "Mean": m, "SD": s, "z": z, "zmax2": max(z2), "zmin2": min(z2),
                "นอกสอง2": out_, "นอกสอง2เปอร์เซ็นต์": 100 * out_ / len(z2),
                "SD2": S.sd(X[half:]), "h2": S.ols(x[half:], y[half:])["slope"]}

    rp = ruler(eth, btc)
    rl = ruler(le, lb)
    rl_pct = {"SD": 100 * rl["SD"], "SD2": 100 * rl["SD2"]}
    chg_l = S.ols(S.diff(le), S.diff(lb))
    chg_p = S.ols(S.diff(eth), S.diff(btc))
    mean_btc1, mean_btc2 = S.mean(btc[:half]), S.mean(btc[half:])
    sd_full_p1, sd_full_p2 = S.sd(Xp[:half]), S.sd(Xp[half:])
    sd_full_l1, sd_full_l2 = S.sd(Xl[:half]), S.sd(Xl[half:])
    ratio0, ratio1 = btc[0] / eth[0], btc[-1] / eth[-1]
    coins = [hl * a / b for a, b in zip(btc, eth)]
    hl2 = round(hl, 2)
    real = {
        "วัน": nf, "เริ่ม": dts[0], "จบ": dts[-1], "ครึ่ง": half, "ครึ่งหลังวัน": nf - half,
        "ปีแรกจบ": dts[half - 1], "ปีหลังเริ่ม": dts[half],
        "h": r(hl), "hละเอียด": r4(hl), "ค่าตัดแกน": r(cl), "ค่าตัดแกนละเอียด": r4(cl), "R2": r(ol["r2"]),
        "SDX": r(sdl), "ข้ามMean": cross_l, "ค่าตัดแกนจุด": r(oc["intercept"]), "ห่างเลขปัดสูงสุด": r(max(gaps)), "Zต่ำสุด": r(min(zl)), "Zสูงสุด": r(max(zl)),
        "แถว": rows,
        "ราคา": {"h": r(op["slope"]), "R2": r(op["r2"]), "SDX": r(sdp), "ข้ามMean": cross_p,
                 "Zต่ำสุด": r(min(zp)), "Zสูงสุด": r(max(zp)), "hการขยับ": r(chg_p["slope"]),
                 "SDปีแรก": r(sd_full_p1), "SDปีหลัง": r(sd_full_p2), "SDเท่า": r(sd_full_p2 / sd_full_p1, 1)},
        "logส่วน": {"SDปีแรก": r(sd_full_l1), "SDปีหลัง": r(sd_full_l2), "SDเท่า": r(sd_full_l2 / sd_full_l1, 1)},
        "BTCเฉลี่ยปีแรก": r(mean_btc1), "BTCเฉลี่ยปีหลัง": r(mean_btc2), "BTCเท่า": r(mean_btc2 / mean_btc1, 1),
        "ไม้ปีแรก": {
            "ราคา": {"h": r(rp["h"]), "SD": i0(rp["SD"]), "Zสูงสุด": r1(rp["zmax2"]), "Zต่ำสุด": r(rp["zmin2"]),
                     "นอกสอง": rp["นอกสอง2"], "นอกสองเปอร์เซ็นต์": i0(rp["นอกสอง2เปอร์เซ็นต์"]),
                     "hปีหลัง": r(rp["h2"])},
            "log": {"h": r(rl["h"]), "SD": r(rl_pct["SD"]), "Zสูงสุด": r(rl["zmax2"]), "Zต่ำสุด": r(rl["zmin2"]),
                    "นอกสอง": rl["นอกสอง2"], "นอกสองเปอร์เซ็นต์": i0(rl["นอกสอง2เปอร์เซ็นต์"]),
                    "hปีหลัง": r(rl["h2"])},
        },
        "hการขยับ": r(chg_l["slope"]), "R2การขยับ": r(chg_l["r2"]),
        "ห่างครึ่งราคาเปอร์เซ็นต์": i0(100 * (rp["h"] - rp["h2"]) / rp["h"]),
        "ห่างครึ่งlogเปอร์เซ็นต์": i0(100 * (rl["h"] - rl["h2"]) / rl["h"]),
        "เหรียญ": {"วันแรกอัตรา": r(ratio0), "วันสุดท้ายอัตรา": r(ratio1),
                   "วันแรก": r(hl2 * round(ratio0, 2)), "วันสุดท้าย": r(hl2 * round(ratio1, 2)),
                   "วันแรกละเอียด": r(coins[0]), "วันสุดท้ายละเอียด": r(coins[-1]),
                   "ต่ำสุด": r(min(coins)), "สูงสุด": r(max(coins)), "hราคา": r(op["slope"]),
                   "BTCวันแรก": r(btc[0]), "ETHวันแรก": r(eth[0]), "BTCวันสุดท้าย": r(btc[-1]), "ETHวันสุดท้าย": r(eth[-1]),
                   # ถือ ETH เท่าวันแรกไว้จนวันสุดท้าย: เงินขา ETH ÷ เงินขา BTC
                   "ไม่ปรับอัตราส่วนเงิน": r(hl2 * round(ratio0, 2) * round(eth[-1], 2) / round(btc[-1], 2))},
        "ชุดกราฟ": {"zราคา": [round(v, 3) for v in rp["z"]], "zlog": [round(v, 3) for v in rl["z"]],
                    "เหรียญ": [round(v, 2) for v in coins], "iครึ่ง": half},
    }
    out["จริง"] = real

    # ช่วงตรวจ (เปิดดูหนึ่งครั้ง · จดในสมุดวิจัย): ไม้บรรทัดทั้งช่วงเลือก → Z ของช่วงตรวจ
    dv, pv = load_closes("validation")
    vb, ve = pv["BTC"], pv["ETH"]
    zv_p = [(b - op["intercept"] - op["slope"] * e) / sdp for b, e in zip(vb, ve)]
    zv_l = [100 * (LN(b) - cl - hl * LN(e)) / sdl for b, e in zip(vb, ve)]
    out["ตรวจ"] = {"วัน": len(dv), "เริ่ม": dv[0], "จบ": dv[-1],
                   "ราคาZสูงสุด": r(max(zv_p)), "logZสูงสุด": r(max(zv_l)),
                   "ราคานอกสอง": sum(1 for v in zv_p if abs(v) > 2), "logนอกสอง": sum(1 for v in zv_l if abs(v) > 2),
                   "จำนวนครั้งที่เปิด": 1}

    # ════════════ 🎲 โลกจำลอง ════════════
    kw = dict(phi=0.9, sd=0.01, h=1.4)

    def judge(w):
        A, Bw = w["A"], w["B"]
        p_ = ruler(Bw, A)
        l_ = ruler([LN(v) for v in Bw], [LN(v) for v in A])
        return p_, l_

    w0 = M.stationary_pair(seed=101, n=nf, **kw)
    p0, l0 = judge(w0)
    zmax_p = M.reseed(M.stationary_pair, lambda w: judge(w)[0]["zmax2"], n=nf, **kw)
    zmax_l = M.reseed(M.stationary_pair, lambda w: judge(w)[1]["zmax2"], n=nf, **kw)
    gap_l = M.reseed(M.stationary_pair, lambda w: abs(judge(w)[1]["h"] - judge(w)[1]["h2"]) / judge(w)[1]["h"] * 100, n=nf, **kw)
    gap_p = M.reseed(M.stationary_pair, lambda w: abs(judge(w)[0]["h"] - judge(w)[0]["h2"]) / judge(w)[0]["h"] * 100, n=nf, **kw)

    def rng(z, f=r):
        return {"ต่ำสุด": f(z["min"]), "มัธยฐาน": f(z["median"]), "สูงสุด": f(z["max"])}

    ol0 = S.ols([LN(v) for v in w0["B"]], [LN(v) for v in w0["A"]])
    rl0 = [100 * v for v in ol0["residuals"]]
    cr0 = sum(1 for a, b in zip(rl0, rl0[1:]) if (a > 0) != (b > 0))
    loose = M.random_walk_pair(seed=102, n=nf, sd=0.01, h=1.4)
    oll = S.ols([LN(v) for v in loose["B"]], [LN(v) for v in loose["A"]])
    crl = sum(1 for a, b in zip(oll["residuals"], oll["residuals"][1:]) if (a > 0) != (b > 0))
    # โลกที่เชือกอยู่บนราคา (ดอลลาร์)
    wp = M.price_pair(seed=106, n=nf, phi=0.9, sd=0.5)
    pp, lp = judge(wp)
    olp = S.ols([LN(v) for v in wp["B"]], [LN(v) for v in wp["A"]])
    sdp1, sdp2 = S.sd(olp["residuals"][:half]), S.sd(olp["residuals"][half:])
    out["จำลอง"] = {
        "h": 1.4, "phi": 0.9, "แกว่งต่อวันเปอร์เซ็นต์": 1, "Bแกว่งต่อวันเปอร์เซ็นต์": i0(M.COMMON_SD * 100), "วัน": nf, "ชุด": 30,
        "Bวันแรก": r(w0["B"][0]), "Bกลาง": r(w0["B"][half]), "Bวันสุดท้าย": r(w0["B"][-1]),
        "ตัวอย่าง": {
            "ราคา": {"h": r(p0["h"]), "hปีหลัง": r(p0["h2"]), "Zสูงสุด": r1(p0["zmax2"]),
                     "นอกสองเปอร์เซ็นต์": i0(p0["นอกสอง2เปอร์เซ็นต์"])},
            "log": {"h": r(l0["h"]), "hปีหลัง": r(l0["h2"]), "Zสูงสุด": r(l0["zmax2"]),
                    "นอกสองเปอร์เซ็นต์": r1(l0["นอกสอง2เปอร์เซ็นต์"])},
            "hทั้งช่วง": r(ol0["slope"]), "ข้ามMean": cr0,
        },
        "ไม่มีเชือก": {"ข้ามMean": crl},
        "สุ่มซ้ำ": {"Zสูงสุดราคา": rng(zmax_p, r1), "Zสูงสุดlog": rng(zmax_l), "ห่างครึ่งlog": rng(gap_l, i0),
                    "ห่างครึ่งราคา": rng(gap_p, i0)},
        "ชุดกราฟ": {"Zราคา": [round(v, 2) for v in zmax_p["values"]], "Zlog": [round(v, 2) for v in zmax_l["values"]]},
        "เชือกบนราคา": {"Zสูงสุดราคา": r(pp["zmax2"]), "Zสูงสุดlog": r(lp["zmax2"]),
                        "SDlogปีแรก": r(100 * sdp1), "SDlogปีหลัง": r(100 * sdp2), "SDlogเท่า": r(sdp2 / sdp1),
                        "Bวันแรก": r(wp["B"][0]), "Bวันสุดท้าย": r(wp["B"][-1])},
    }

    # ════════════ ตัวเลขประกอบในหน้า (ที่มาของเลขกลางทาง) ════════════
    r0 = rows[0]
    hl4, cl4 = round(hl, 4), round(cl, 4)
    step1 = round(hl4 * r0["LNETH"], 4)
    step2 = round(r0["LNBTC"] - step1, 4)
    out["ประกอบ"] = {
        "ทวนบท1": {"ผลรวมdBคูณdA": 25, "ผลรวมdBกำลังสอง": 10, "h": 2.5},
        "SDปีแรกปัด": i0(sd_full_p1), "SDปีหลังปัด": i0(sd_full_p2),
        "นับศูนย์": {"ร้อยคูณพัน": 100 * 1000, "ศูนย์": [1, 2, 3, 5]},
        "เหรียญตัวอย่าง": 30000, "ขาAขยับ": i0(1.5 / 100 * VA), "สองเท่าแรก": 200,
        "คูณ": [1.1, 1.21, 1.04, 1.02], "สามวันอัตรา": r4(p[-1] / p[0]),
        "ห้าวันอัตรา": {"B": [r4(v / PB[0]) for v in PB], "A": [r4(v / PA[0]) for v in PA]},
        "แถวแรก": {"hคูณLNETH": step1, "ลบ": step2, "บวกค่าตัดแกน": round(step2 - cl4, 4)},
        "Bเพิ่มวัน3": r(h5 * PA[2] / PB[2] - h5 * PA[0] / PB[0]),
        "EXP040เปอร์เซ็นต์": i0(100 * (math.exp(0.40) - 1)), "ห่างแบบฝึก1": r(100 * (1.1 ** 3 - 1) - 30, 1),
        "ราคาบวกสิบสามวัน": 130, "logสามสิบ": 0.3,
        "ร้อยLN": {"สองทาง_คูณ": [r(100 * LN(v)) for v in pa], "สองทาง_บวก": [r(100 * LN(v)) for v in pb],
                   "ก้าวคูณ": r(r(100 * LN(110)) - r(100 * LN(100))), "ก้าวคูณ2": r(r(100 * LN(121)) - r(100 * LN(110))),
                   "ก้าวบวก": [r(r(100 * LN(120)) - r(100 * LN(100))), r(r(100 * LN(140)) - r(100 * LN(120)))],
                   "รวมคูณ": r(r(100 * LN(121)) - r(100 * LN(100))), "LN121": r(100 * LN(1.21)),
                   "LN104": r(100 * LN(1.04)), "LN102": r(100 * LN(1.02)), "hคูณLN102": r(1.5 * r(100 * LN(1.02))),
                   "ต่างจุด": r(r(100 * LN(1.04)) - 1.5 * r(100 * LN(1.02))),
                   "ต่างเงิน": r((r(100 * LN(1.04)) - 1.5 * r(100 * LN(1.02))) / 100 * VA, 1),
                   "สามก้าว": r(3 * r(100 * LN(1.1))), "LN1331": r(100 * LN(1.331)), "EXP005ปัด": r(math.exp(0.05)),
                   "LOG10_200": r(math.log10(200)), "LOG10_2": r(math.log10(2))},
        "อนุกรม": {"r005ยกกำลังสองหารสอง": 0.00125, "r05ยกกำลังสองหารสอง": 0.125, "e": 2.718},
        "ห่างครึ่งปีlogสูงสุดโลก": out["จำลอง"]["สุ่มซ้ำ"]["ห่างครึ่งlog"]["สูงสุด"],
    }
    assert abs(out["ประกอบ"]["แถวแรก"]["บวกค่าตัดแกน"] * 100 - rows[0]["X"]) < 0.06
    out["จำนวนวิธีรวม"] = out_methods = 5 + 2      # บท 1 ห้าวิธี + log บนระดับ + Log Return
    assert out_methods == 7

    # กล่อง 🧰 (ที่มา: tools/sab_research/practitioner-research.md §1.1 · §2 · §6 · §8.2–8.3 · ตัวเลขตามที่บันทึกไว้ ไม่ได้คำนวณ)
    out["คนทำงานจริง"] = {"ปีVidyamurthy": "2004", "ปีKrauss": "2017", "ปีGGR": "2006", "ปีChan": "2006",
                          "คู่ที่สแกน": 45, "CorrระดับBTCSOL": 0.97, "คู่Corrระดับสูงสุด": 5, "หน้าต่างวัน": 60}

    # ════════════ แบบฝึก ════════════
    # ข้อ 1: +10% สามครั้ง → 133.1 · LN 0.0953 × 3 = 0.2859 · LN(1.331) = 0.2859
    p3 = 100 * 1.1 ** 3
    # ข้อ 2: h แบบ log 1.5 · ราคา A 120 · B 40 · เงินขา A 1,200 → เหรียญ
    a2, b2_, va2 = 120, 40, 1200
    # ข้อ 3: ช่องว่าง 2% เดิม แต่ราคาลดลงครึ่งหนึ่ง (B 25)
    b3 = 25
    a3 = 2 * b3 * (1 + gap)
    # ข้อ 5: ETH ต่อ BTC วันกลางช่วงเลือก (วันแรกของปีหลัง)
    i5 = half
    out["แบบฝึก"] = {
        "ข้อ1": {"ราคา": r(p3, 1), "สามก้าว": r4(3 * r4(LN(1.1))), "LN1331": r4(LN(1.331)),
                 "เปอร์เซ็นต์รวม": r(100 * (1.1 ** 3 - 1), 1), "บวกธรรมดา": 30},
        "ข้อ2": {"A": a2, "B": b2_, "VA": va2, "เหรียญA": i0(va2 / a2), "VB": i0(1.5 * va2), "เหรียญB": i0(1.5 * va2 / b2_),
                 "Bต่อA": r(1.5 * a2 / b2_, 1)},
        "ข้อ3": {"B": b3, "สองเท่าB": 2 * b3, "A": r(a3), "X": r(a3 - 2 * b3), "Z": r((a3 - 2 * b3) / RULER_SD, 1),
                 "logX": r(100 * LN(1.02))},
        "ข้อ5": {"วัน": dts[i5], "BTC": r(btc[i5]), "ETH": r(eth[i5]), "อัตรา": r(round(btc[i5], 2) / round(eth[i5], 2)),
                 "เหรียญ": r(hl2 * round(round(btc[i5], 2) / round(eth[i5], 2), 2)),
                 "เงินETHต่อBTC": r(hl2 * round(btc[i5], 2))},
    }
    out["_แบบฝึก"] = [
        {"โจทย์": "+10% สามครั้งจาก 100: ผลรวม Log Return × 100", "คำตอบ": out["ประกอบ"]["ร้อยLN"]["สามก้าว"]},
        {"โจทย์": "h แบบ log 1.5 · A 120 · B 40 · เงินขา A 1,200: จำนวน B ที่ต้อง short", "คำตอบ": out["แบบฝึก"]["ข้อ2"]["เหรียญB"]},
        {"โจทย์": "ช่องว่าง 2% เมื่อราคาลดครึ่ง: Z ด้วยไม้บรรทัด SD 2", "คำตอบ": out["แบบฝึก"]["ข้อ3"]["Z"]},
        {"โจทย์": "เปิดตาม Z แบบ log หรือไม่ (ตัดสินใจ)"},
        {"โจทย์": "จำนวน ETH ต่อ BTC ตาม h แบบ log วันแรกของปีหลัง", "คำตอบ": out["แบบฝึก"]["ข้อ5"]["เหรียญ"]},
    ]
    return out
