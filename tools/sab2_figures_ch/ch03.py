"""เล่ม 2 บท 3 — มีเชือกจริงไหม: ทดสอบแทนการมอง · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ทุกค่าคำนวณที่นี่ ไม่มีเลขลอย:
  มือ        สิบแถวของพี่ฝน = โลกเดินสุ่ม sab2_sim.random_walk_pair(seed=16, n=11) · X × 100 ปัดหนึ่งตำแหน่ง แล้วลบ Mean
             ของสิบวันแรก (ปัดหนึ่งตำแหน่ง) ให้ Mean ของ "X วันนี้" เป็น 0 พอดี → ถดถอยการเปลี่ยนบนระดับด้วยมือ
             (slope = Σ x·Δ ÷ Σ x² เพราะ Mean ของ x เป็น 0) · ค่าสถิติตรงกับ sab2_stats.adf(x) lag 0 ทุกตำแหน่ง
  สามสิบโลก  seed 1–30 ของโลกเดียวกัน (ปัดแบบเดียวกัน) → slope และค่าสถิติ ADF ของทุกโลก
  หมื่นโลก   seed 1–10,000 (n = 11 ไม่ปัด · ค่าสถิติไม่ขึ้นกับหน่วย) → เส้น 5% ที่จำลองได้ เทียบตาราง MacKinnon
  ความยาว    เดินสุ่ม · เชือก φ 0.95 · เชือก φ 0.99 ที่ 60 / 250 / 731 วัน · 30 seed → จำนวนที่ผ่าน ADF 5%
  eg_sim     Engle–Granger บนคู่เดินสุ่ม 731 วัน: เส้น ADF ธรรมดา (ผิด) กับเส้นสองขา (ถูก) · 30 seed และ 1,000 seed
  เชือกขาด   broken_pair เชือก φ 0.9 ขาดที่วัน 300 จาก 500 · EG บนทั้งช่วง / ก่อนขาด / หลังขาด · 30 seed
  จริง       ข้อมูลจริงช่วงเลือกและช่วงตรวจ (ไม่แตะช่วงทดสอบสุดท้าย) · log ราคาปิด · EG lag 0 · เหรียญซ้ายถูกอธิบาย
"""

import itertools
import math

SEED_HAND = 16          # โลกที่พี่ฝนหยิบ (หนึ่งใน 30)
N_HAND = 11             # 11 วัน = 10 แถวของการเปลี่ยน
N_MANY = 10000          # จำนวนโลกที่ใช้หาเส้น 5% แบบจำลอง
LENGTHS = (60, 250, 731)
PAIRS = (("LTC", "LINK"), ("LTC", "DOT"), ("BTC", "ETH"))     # (เหรียญที่ถูกอธิบาย, เหรียญที่ใช้อธิบาย)


def _r(v, n=2):
    """ปัด n ตำแหน่ง · ค่าที่ลงตัวเป็นจำนวนเต็มเก็บเป็น int (ตัวเติมในหน้าพิมพ์ 2 ไม่ใช่ 2.0)"""
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _pct_series(world):
    return [round(v * 100, 1) for v in world["X"]]


def extend(data, D, q):
    import sab2_realdata as R
    import sab2_sim as M
    import sab2_stats as S

    seeds = M.ROBUST_SEEDS

    # ═══ ตอน ก · สิบแถวด้วยมือ ═══
    raw = _pct_series(M.random_walk_pair(seed=SEED_HAND, n=N_HAND))
    shift = round(sum(raw[:10]) / 10, 1)
    x = [round(v - shift, 1) for v in raw]
    today, tom = x[:-1], x[1:]
    chg = [round(b - a, 1) for a, b in zip(today, tom)]
    prod = [round(a * c, 2) for a, c in zip(today, chg)]
    sq = [round(a * a, 2) for a in today]
    sxd, sxx = round(sum(prod), 2), round(sum(sq), 2)
    assert abs(sum(today)) < 1e-9, "Mean ของ X วันนี้ต้องเป็น 0"
    slope = sxd / sxx
    mean_chg = sum(chg) / len(chg)
    fitted = [mean_chg + slope * a for a in today]
    resid = [c - f for c, f in zip(chg, fitted)]
    sse = sum(e * e for e in resid)
    s2 = sse / (len(today) - 2)
    se = math.sqrt(s2) / math.sqrt(sxx)
    stat = slope / se
    adf_hand = S.adf(x)
    assert abs(adf_hand["stat"] - stat) < 1e-9 and abs(adf_hand["gamma"] - slope) < 1e-12, "มือ ≠ sab2_stats.adf"
    crit10 = S.adf_crit(len(today))
    sxn = round(sum(round(a * b, 2) for a, b in zip(today, tom)), 2)
    hand = {
        "seed": SEED_HAND, "วัน": list(range(1, 11)), "ลบMean": shift,
        "x": [_r(v, 1) for v in x], "วันนี้": [_r(v, 1) for v in today], "พรุ่งนี้": [_r(v, 1) for v in tom],
        "เปลี่ยน": [_r(v, 1) for v in chg], "คูณ": [_r(v) for v in prod], "กำลังสอง": [_r(v) for v in sq],
        "รวมคูณ": sxd, "รวมกำลังสอง": sxx, "slope": _r(slope), "slope3": _r(slope, 3),
        "phi": _r(1 + slope), "รวมวันนี้คูณพรุ่งนี้": sxn, "phiตรวจ": _r(sxn / sxx),
        "รวมเปลี่ยน": _r(sum(chg), 1), "Meanเปลี่ยน": _r(mean_chg),
        "ทาย": [_r(v) for v in fitted], "residual": [_r(v) for v in resid], "res2": [_r(v * v) for v in resid],
        "SSE": _r(sse), "s2": _r(s2), "s": _r(math.sqrt(s2)), "รากรวมกำลังสอง": _r(math.sqrt(sxx)),
        "SE": _r(se), "stat": _r(stat), "เส้น5": _r(crit10["5%"]), "เส้น1": _r(crit10["1%"]), "เส้น10": _r(crit10["10%"]),
        "ครึ่งชีวิต": _r(S.half_life(1 + slope)), "แถว": len(today), "ตัวหาร": len(today) - 2,
        "ขนาดแรงสุด": max(abs(c) for c in chg),
    }
    # แบบฝึกข้อ 2: แรงสะบัดเล็กลงครึ่งหนึ่ง (s ครึ่ง → SE ครึ่ง → ค่าสถิติสองเท่า)
    hand["แบบฝึก2"] = {"s": _r(math.sqrt(s2) / 2), "SE": _r(se / 2), "stat": _r(stat * 2),
                       "ใช้ปัด": _r(_r(slope) / _r(se / 2)), "ผิดคูณ": _r(stat / 2)}

    # ═══ สามสิบโลก ═══
    slopes, stats = [], []
    for s in seeds:
        xs = _pct_series(M.random_walk_pair(seed=s, n=N_HAND))
        a = S.adf(xs)
        slopes.append(a["gamma"])
        stats.append(a["stat"])
    i_hand = seeds.index(SEED_HAND)
    assert abs(stats[i_hand] - stat) < 1e-9
    n_neg = sum(v < 0 for v in slopes)
    thirty = {
        "slope": [_r(v) for v in slopes], "stat": [_r(v) for v in stats],
        "ลบ": n_neg, "บวก": len(seeds) - n_neg, "ลบเปอร์เซ็นต์": _r(100 * n_neg / len(seeds), 0),
        "slopeแรงเท่ามือ": sum(v <= slopes[i_hand] for v in slopes),
        "statแรงเท่ามือ": sum(v <= stats[i_hand] for v in stats),
        "statแรงเท่ามือเปอร์เซ็นต์": _r(100 * sum(v <= stats[i_hand] for v in stats) / len(seeds), 0),
        "ผ่านเส้น5": sum(v < crit10["5%"] for v in stats),
        "statต่ำสุด": _r(min(stats)), "slopeต่ำสุด": _r(min(slopes)),
        "statมัธยฐาน": _r(sorted(stats)[14] / 2 + sorted(stats)[15] / 2),
        "slopeมัธยฐาน": _r(sorted(slopes)[14] / 2 + sorted(slopes)[15] / 2),
    }

    # ═══ หมื่นโลก: เส้น 5% แบบจำลอง ═══
    many = sorted(S.adf(M.random_walk_pair(seed=s, n=N_HAND)["X"])["stat"] for s in range(1, N_MANY + 1))
    k5 = int(0.05 * N_MANY)
    below_hand = sum(v <= stat for v in many)
    tenk = {"จำนวน": N_MANY, "เส้น5จำลอง": _r(many[k5 - 1]), "ตาราง5": _r(crit10["5%"]),
            "ต่ำกว่ามือ": below_hand, "ต่ำกว่ามือเปอร์เซ็นต์": _r(100 * below_hand / N_MANY, 1),
            "pตารางเชิงเส้นกำกับ": _r(100 * S.adf_pvalue(stat), 0), "ห้าเปอร์เซ็นต์ของหมื่น": k5}

    # ═══ ตอน ข · ความยาวของข้อมูล ═══
    def passes(world, n, **kw):
        return sum(S.adf(world(seed=s, n=n, **kw)["X"])["reject5"] for s in seeds)
    length = {"วัน": list(LENGTHS), "เดินสุ่ม": [], "เชือก095": [], "เชือก099": [], "เส้น5": []}
    for n in LENGTHS:
        length["เดินสุ่ม"].append(passes(M.random_walk_pair, n))
        length["เชือก095"].append(passes(M.stationary_pair, n, phi=0.95))
        length["เชือก099"].append(passes(M.stationary_pair, n, phi=0.99))
        length["เส้น5"].append(_r(S.adf_crit(n - 1)["5%"]))
    length["ครึ่งชีวิต095"] = _r(S.half_life(0.95), 1)
    length["ครึ่งชีวิต099"] = _r(S.half_life(0.99), 1)
    length["เส้นยาวมาก"] = _r(S.MACKINNON_2010_C[1]["5%"][0])
    length["เส้นยาวมาก1"] = _r(S.MACKINNON_2010_C[1]["1%"][0])
    length["เส้นสองขายาวมาก"] = _r(S.MACKINNON_2010_C[2]["5%"][0])
    length["เปอร์เซ็นต์เชือก095"] = [_r(100 * v / len(seeds), 0) for v in length["เชือก095"]]
    length["เปอร์เซ็นต์เชือก099"] = [_r(100 * v / len(seeds), 0) for v in length["เชือก099"]]
    length["เปอร์เซ็นต์เดินสุ่ม"] = [_r(100 * v / len(seeds), 0) for v in length["เดินสุ่ม"]]
    # ตัวอย่าง ADF หนึ่งโลก (บล็อก 💻): เชือก φ 0.95 · 250 วัน · seed 1
    ex = S.adf(M.stationary_pair(seed=1, n=250, phi=0.95)["X"])
    exr = S.adf(M.random_walk_pair(seed=1, n=250)["X"])
    length["ตัวอย่าง"] = {"stat": _r(ex["stat"]), "phi": _r(ex["phi"]), "p": _r(100 * ex["pvalue"], 1),
                          "statเดินสุ่ม": _r(exr["stat"]), "pเดินสุ่ม": _r(100 * exr["pvalue"], 0),
                          "เส้น5": _r(ex["crit"]["5%"])}

    # ═══ ตอน ค · Engle–Granger ในโลกจำลอง ═══
    n_eg = 731
    c1, c2 = S.adf_crit(n_eg - 1)["5%"], S.adf_crit(n_eg - 1, 2)["5%"]

    def eg_stat(d):
        return S.engle_granger(d["logA"], d["logB"])["stat"]
    rw30 = [eg_stat(M.random_walk_pair(seed=s, n=n_eg)) for s in seeds]
    rw1k = [eg_stat(M.random_walk_pair(seed=s, n=n_eg)) for s in range(1, 1001)]
    st30 = [eg_stat(M.stationary_pair(seed=s, n=n_eg, phi=0.95)) for s in seeds]
    eg_sim = {"วัน": n_eg, "เส้นADF": _r(c1), "เส้นEG": _r(c2),
              "ผิดเส้น30": sum(t < c1 for t in rw30), "ถูกเส้น30": sum(t < c2 for t in rw30),
              "ผิดเส้นพัน": _r(100 * sum(t < c1 for t in rw1k) / 1000, 1),
              "ถูกเส้นพัน": _r(100 * sum(t < c2 for t in rw1k) / 1000, 1),
              "เชือก095ผ่าน30": sum(t < c2 for t in st30)}

    # ═══ เชือกขาด ═══
    def broken_pass(sl):
        c = 0
        for s in seeds:
            d = M.broken_pair(seed=s, n=500, break_at=300)
            c += S.engle_granger(d["logA"][sl], d["logB"][sl])["reject5"]
        return c
    broken = {"วันทั้งหมด": 500, "วันขาด": 300, "หลังขาด": 200, "phiก่อน": 0.9,
              "ทั้งช่วง": broken_pass(slice(None)), "ก่อนขาด": broken_pass(slice(0, 300)),
              "หลังขาดผ่าน": broken_pass(slice(300, None))}
    broken["ทั้งช่วงเปอร์เซ็นต์"] = _r(100 * broken["ทั้งช่วง"] / len(seeds), 0)

    # ═══ ข้อมูลจริง ═══
    dates_f, pf = R.load_closes("formation")
    dates_v, pv = R.load_closes("validation")
    coins = list(pf)
    lf = {c: S.logs(pf[c]) for c in coins}
    lv = {c: S.logs(pv[c]) for c in coins}

    def pack(e):
        return {"h": _r(e["h"]), "a": _r(e["intercept"]), "stat": _r(e["stat"]), "เส้น5": _r(e["crit"]["5%"]),
                "p": _r(100 * e["pvalue"], 1), "ผ่าน": bool(e["reject5"]), "phi": _r(e["adf"]["phi"]),
                "phi3": _r(e["adf"]["phi"], 3), "ครึ่งชีวิต": _r(S.half_life(e["adf"]["phi"]), 1)}
    real = {"วันช่วงเลือก": len(dates_f), "วันช่วงตรวจ": len(dates_v),
            "ช่วงเลือก": [dates_f[0], dates_f[-1]], "ช่วงตรวจ": [dates_v[0], dates_v[-1]],
            "ปี": list(range(int(dates_f[0][:4]), int(dates_v[-1][:4]) + 1)), "คู่": {}}
    for a, b in PAIRS:
        ef, ev = S.engle_granger(lf[a], lf[b]), S.engle_granger(lv[a], lv[b])
        er = S.engle_granger(lf[b], lf[a])
        xv = [ya - ef["h"] * yb - ef["intercept"] for ya, yb in zip(lv[a], lv[b])]
        af = S.adf(xv)
        e1 = S.engle_granger(lf[a], lf[b], lags=1)
        real.setdefault("lag1", {})[f"{a}-{b}"] = {"stat": _r(e1["stat"]), "ผ่าน": bool(e1["reject5"])}
        real["คู่"][f"{a}-{b}"] = {"ช่วงเลือก": pack(ef), "ช่วงตรวจ": pack(ev), "กลับทิศ": pack(er),
                                    "ตรึงh": {"stat": _r(af["stat"]), "เส้น5": _r(af["crit"]["5%"]), "ผ่าน": bool(af["reject5"]),
                                              "Mean": _r(100 * S.mean(xv), 0)}}
    # LTC เดี่ยว ๆ และ XRP เดี่ยว ๆ (ADF บน log ราคาของเหรียญเดียว)
    single = {}
    for c in coins:
        a1, a2 = S.adf(lf[c]), S.adf(lv[c])
        single[c] = {"ช่วงเลือก": _r(a1["stat"]), "ช่วงตรวจ": _r(a2["stat"]),
                     "ผ่านเลือก": bool(a1["reject5"]), "ผ่านตรวจ": bool(a2["reject5"])}
    real["เดี่ยว"] = single
    real["เดี่ยวเส้น5เลือก"] = _r(S.adf_crit(len(dates_f) - 1)["5%"])
    real["เดี่ยวเส้น5ตรวจ"] = _r(S.adf_crit(len(dates_v) - 1)["5%"])
    real["เดี่ยวผ่านเลือก"] = sum(v["ผ่านเลือก"] for v in single.values())
    real["เดี่ยวผ่านตรวจ"] = sum(v["ผ่านตรวจ"] for v in single.values())
    real["LTCราคา"] = [_r(min(pf["LTC"]), 0), _r(max(pf["LTC"]), 0)]
    # 45 คู่ (ลำดับเหรียญตามไฟล์ · เหรียญที่มาก่อนถูกอธิบาย) และแบบสองทิศ 90 คู่
    combos = list(itertools.combinations(coins, 2))
    pf_pass = [(a, b) for a, b in combos if S.engle_granger(lf[a], lf[b])["reject5"]]
    pv_pass = [(a, b) for a, b in combos if S.engle_granger(lv[a], lv[b])["reject5"]]
    ltc_left = sum(S.engle_granger(lf["LTC"], lf[c])["reject5"] for c in coins if c != "LTC")
    ltc_right = sum(S.engle_granger(lf[c], lf["LTC"])["reject5"] for c in coins if c != "LTC")
    perm_f = sum(S.engle_granger(lf[a], lf[b])["reject5"] for a, b in itertools.permutations(coins, 2))
    xrp_v = sum(1 for a, b in pv_pass if "XRP" in (a, b))
    p_any = 1 - 0.95 ** len(combos)
    real["สี่สิบห้า"] = {"คู่": len(combos), "ผ่านเลือก": len(pf_pass), "ผ่านตรวจ": len(pv_pass),
                         "รายชื่อเลือก": [f"{a}-{b}" for a, b in pf_pass], "รายชื่อตรวจ": [f"{a}-{b}" for a, b in pv_pass],
                         "ผ่านทั้งสอง": len(set(pf_pass) & set(pv_pass)), "คาดจากโชค": float(q(D(len(combos)) * D("0.05"), 2)),
                         "อย่างน้อยหนึ่ง": _r(100 * p_any, 0), "LTCซ้ายผ่าน": ltc_left, "LTCขวาผ่าน": ltc_right,
                         "คู่ของLTC": len(coins) - 1, "สองทิศ": len(coins) * (len(coins) - 1), "สองทิศผ่าน": perm_f,
                         "XRPในตรวจ": xrp_v, "สองทิศคาด": float(q(D(len(coins) * (len(coins) - 1)) * D("0.05"), 1))}
    # ตาราง 10 แถว 📡: LTC–DOT ช่วงเลือก ทุก 81 วัน
    e = S.engle_granger(lf["LTC"], lf["DOT"])
    idx = list(range(0, len(dates_f), 81))[:10]
    real["สิบแถว"] = {"ห่าง": 81, "แถว": [{"วันที่": dates_f[i], "LTC": _r(pf["LTC"][i]), "DOT": _r(pf["DOT"][i]),
                                            "logLTC": _r(lf["LTC"][i]), "logDOT": _r(lf["DOT"][i]),
                                            "X": _r(100 * e["residuals"][i], 1)} for i in idx]}
    # กราฟ: log LTC เดี่ยว (ลบ Mean ช่วงเลือก) กับ X ของ LTC–DOT (h ตรึงจากช่วงเลือก) · ทุก 3 วัน · หน่วย %
    m_ltc = S.mean(lf["LTC"])
    all_ltc = lf["LTC"] + lv["LTC"]
    all_dot = lf["DOT"] + lv["DOT"]
    xs_all = [ya - e["h"] * yb - e["intercept"] for ya, yb in zip(all_ltc, all_dot)]
    step = 3
    real["กราฟ"] = {"ทุก": step, "แบ่ง": len(dates_f), "วันรวม": len(all_ltc),
                    "LTC": [_r(100 * (v - m_ltc), 1) for v in all_ltc[::step]],
                    "X": [_r(100 * v, 1) for v in xs_all[::step]],
                    "corr": _r(S.corr(xs_all, [v - m_ltc for v in all_ltc]))}
    # BTC–ETH ฉากเปิด: X (BTC บน ETH แบบบท 1 แต่บน log ราคา) ข้าม Mean กี่ครั้งในช่วงเลือก
    rb = S.engle_granger(lf["BTC"], lf["ETH"])["residuals"]
    real["ETHBTCข้ามMean"] = sum(1 for u, v in zip(rb, rb[1:]) if (u > 0) != (v > 0))
    real["ETHBTCsd"] = _r(100 * S.sd(rb), 1)

    # Funding BTC (Deribit) ช่วงเลือก — แบบฝึกข้อ 5
    fr = [r[2] * 100 for r in R.load_funding("formation", instrument="BTC-PERPETUAL")]
    af = S.adf(fr)
    real["funding"] = {"รอบ": len(fr), "stat": _r(af["stat"]), "เส้น5": _r(af["crit"]["5%"]), "phi": _r(af["phi"]),
                       "ครึ่งชีวิตรอบ": _r(S.half_life(af["phi"]), 1), "Meanต่อรอบ": _r(S.mean(fr), 4),
                       "ต่อหมื่น": _r(S.mean(fr) / 100 * 10000)}

    # ตัวเลขของเล่ม 1 ที่บทนี้ทวน (φ ด้วยมือของ A–B · เล่ม 1 บท 13) — อ่านจาก docs/sab-figures.json ของเล่ม 1 ที่มาเดียว
    import json
    import os
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "docs", "sab-figures.json"),
              encoding="utf-8") as fh:
        v1 = json.load(fh)["ch13"]["v2"]["phiมือบท9"]
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "docs", "sab-figures.json"),
              encoding="utf-8") as fh:
        sd_v1 = json.load(fh)["ch13"]["v2"]["sdหน้า"][1]["sd"]         # โลก φ 0.80 แรงสะบัด 0.5 → SD 0.83
    vol1 = {"รวมคูณ": v1["ผลรวมผลคูณ"], "รวมกำลังสอง": v1["ผลรวมกำลังสอง"], "phi": v1["phi"], "ครึ่งชีวิต": v1["ครึ่งชีวิต"],
            "sdโลก080": sd_v1}
    # ตัวเลขกลางทางที่หน้าคิดให้ดู (ทุกตัวคำนวณจากค่าข้างบน)
    r0 = real["สิบแถว"]["แถว"][0]
    lt_dot = real["คู่"]["LTC-DOT"]["ช่วงเลือก"]
    walk = {"phiลบหนึ่ง": _r(D(str(v1["phi"])) - 1), "สองเท่า": _r(2 * (D(str(v1["phi"])) - 1)),
            "phiมัธยฐาน30": _r(1 + thirty["slopeมัธยฐาน"]), "หารปัด": _r(hand["slope"] / hand["SE"], 1),
            "แถวแรกhคูณ": _r(lt_dot["h"] * r0["logDOT"]),
            "แถวแรกX": _r(r0["logLTC"] - _r(lt_dot["h"] * r0["logDOT"]) - lt_dot["a"])}

    ch = {"เล่ม1": vol1, "ทวน": walk, "มือ": hand, "สามสิบโลก": thirty, "หมื่นโลก": tenk, "ความยาว": length, "eg_sim": eg_sim,
          "เชือกขาด": broken, "จริง": real, "ปีMacKinnon": [1994, 2010]}
    lt = real["คู่"]["LTC-LINK"]
    ch["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) Σ x·การเปลี่ยน −67.91 · Σ x² 88.3 → slope · φ · ค่าสถิติจาก SE · เทียบเส้น 5%", "คำตอบ": hand["stat"]},
        {"โจทย์": "(เปลี่ยนเลข) แรงสะบัดเล็กลงครึ่งหนึ่ง → SE และค่าสถิติใหม่ ผ่านเส้น −3.23 ไหม", "คำตอบ": hand["แบบฝึก2"]["stat"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) LTC–LINK ช่วงตรวจแบบตรึง h ได้ −3.11 · เส้นไหนใช้ และถ้าประมาณ h ใหม่ล่ะ",
         "คำตอบ": lt["ตรึงh"]["stat"]},
        {"โจทย์": "(ตัดสินใจ) เพื่อนเลือก LTC–LINK จาก 45 คู่เพราะผ่านทั้งสองช่วง — เห็นด้วยไหม",
         "คำตอบ": real["สี่สิบห้า"]["คาดจากโชค"]},
        {"โจทย์": "(ถ่ายโอน) funding BTC ช่วงเลือก ADF −18.5 — แปลว่า funding carry ได้กำไรไหม", "คำตอบ": real["funding"]["stat"]},
    ]
    ch["_claims"] = [{"id": "sab2-ch03-mackinnon",
                      "ข้อความ": "ค่าวิกฤตและ p-value ของ ADF / Engle–Granger ในบทนี้มาจากสูตรของ MacKinnon (1994, 2010) ผ่าน tools/sab2_stats.py "
                                 "และตรวจซ้ำด้วยการจำลอง 10,000 โลกเดินสุ่ม (เส้น 5% ที่ 10 แถว)",
                      "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "MacKinnon (2010) Queen's Economics Dept. WP 1227 · MacKinnon (1994) JBES 12",
                      "บท": [3]}]
    return ch
