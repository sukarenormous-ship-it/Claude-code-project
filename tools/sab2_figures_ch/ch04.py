"""เล่ม 2 บท 4 — กลับเร็วแค่ไหน และมั่นใจได้แค่ไหน · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ทุกค่าคำนวณที่นี่ ไม่มีเลขลอย:
  มือ        20 วันแรกของโลกเชือก φ 0.95 หนึ่งโลก (sab2_sim.stationary_pair seed 1032) · X × 100 ปัดหนึ่งตำแหน่ง แล้วลบ Mean
             ของ 19 ค่า "วันนี้" (ปัดหนึ่งตำแหน่ง) ให้ผลรวมเป็น 0 พอดี (seed นี้เลือกเพราะลบแล้วรวมเป็นศูนย์ลงตัว) → φ ด้วยมือ
             = Σ วันนี้ × พรุ่งนี้ ÷ Σ วันนี้² (ตรงกับ sab2_stats.ar1 ทุกตำแหน่ง) · SE แบบลัด √((1 − φ²) ÷ n) เทียบ SE แบบบท 3
  บันได      โลกเดียวกัน 20 / 60 / 250 วันแรก → φ · SE · ช่วง 95% · Half-life และช่วง (sab2_stats.half_life_ci)
  สามสิบโลก  seed 1–30 ของโลก φ 0.95 → Median φ ที่ประมาณได้ · กี่โลกต่ำกว่าจริง · ช่วงครอบค่าจริงกี่โลก (และ 1,000 โลก)
  OU         ou_from_ar1 ของโลกจริง (รู้คำตอบ) และของค่าที่ประมาณจาก 250 วัน · รายวันเทียบรายสัปดาห์บนข้อมูลจริง
  จริง       ช่วงเลือก/ช่วงตรวจ (ไม่แตะช่วงทดสอบสุดท้าย) · เหรียญเดี่ยวก่อน (log ราคา) · X ของ LTC–DOT, LTC–LINK, BTC–ETH
             (h จาก Engle–Granger ช่วงเลือก · ช่วงตรวจตรึง h และแบบหา h ใหม่) · AR(1) มีค่าคงที่
  คู่จำลอง   โลก φ 0.97 ยาว 731 วัน (ใกล้ค่าที่ LTC–DOT ให้) · คู่เดินสุ่ม 731 วัน 1,000 คู่ (ทั้งหมด และเฉพาะที่ผ่าน Engle–Granger)
"""

import math
import statistics

SEED_HAND = 1032       # โลกที่ใช้ทำมือ (φ จริง 0.95)
PHI_TRUE = 0.95
LADDER = (20, 60, 250)
N_COVER = 1000         # จำนวนโลกที่ใช้นับอัตราครอบคลุม
PHI_REAL_LIKE = 0.97   # โลกคู่ของ LTC–DOT
N_REAL = 731
HOLD_DAYS = 30         # เกณฑ์ "เร็วพอ" ที่มินเขียนไว้ก่อนเปิดข้อมูล (ปลายบนของ Half-life ไม่เกิน 30 วัน)


def _r(v, n=2):
    """ปัด n ตำแหน่ง · ค่าที่ลงตัวเป็นจำนวนเต็มเก็บเป็น int"""
    if v is None or (isinstance(v, float) and (math.isinf(v) or math.isnan(v))):
        return None
    v = round(float(v) + 0.0, n)
    return int(v) if v == int(v) else v


def _hl(phi):
    return math.log(2.0) / -math.log(phi) if 0 < phi < 1 else float("inf")


def extend(data, D, q):
    import sab2_realdata as R
    import sab2_sim as M
    import sab2_stats as S
    import sab_book as SB

    seeds = M.ROBUST_SEEDS
    z = S.norm_ppf(0.975)

    # ═══ ตอน ก · 20 วันด้วยมือ ═══
    world = M.stationary_pair(seed=SEED_HAND, n=max(LADDER), phi=PHI_TRUE)["X"]
    raw = [round(v * 100, 1) for v in world[:20]]
    shift = round(sum(raw[:19]) / 19, 1)
    x = [round(v - shift, 1) for v in raw]
    today, tom = x[:-1], x[1:]
    assert abs(sum(today)) < 1e-9, "Mean ของ X วันนี้ต้องเป็น 0"
    prod = [round(a * b, 2) for a, b in zip(today, tom)]
    sq = [round(a * a, 2) for a in today]
    sxy, sxx = round(sum(prod), 2), round(sum(sq), 2)
    phi = sxy / sxx
    a1 = S.ar1(x)
    assert abs(a1["phi"] - phi) < 1e-9, "มือ ≠ sab2_stats.ar1"
    n = len(today)
    phi2 = _r(phi)                                    # 0.82 ที่ผู้อ่านใช้ต่อ
    se_exact = a1["se_phi"]
    sq_r = _r(phi2 * phi2)                            # 0.67
    one_minus = _r(1 - sq_r)                          # 0.33
    per_n = one_minus / n                             # 0.0174
    se_short = math.sqrt(per_n)
    se_r = _r(se_short)                               # 0.13 (จากเลขปัด)
    half_w = _r(z * se_r)                             # 1.96 × 0.13
    lo_r, hi_r = _r(phi2 - half_w), _r(phi2 + half_w)
    ci_full = S.half_life_ci(a1["phi"], se_exact)
    rem = [phi2]
    for _ in range(3):
        rem.append(_r(rem[-1] * phi2))                # 0.82 → 0.67 → 0.55 → 0.45
    hand = {
        "seed": SEED_HAND, "phiจริง": PHI_TRUE, "ลบMean": shift, "แถว": n, "วัน": len(x),
        "x": [_r(v, 1) for v in x], "วันนี้": [_r(v, 1) for v in today], "พรุ่งนี้": [_r(v, 1) for v in tom],
        "คูณ": [_r(v) for v in prod], "กำลังสอง": [_r(v) for v in sq],
        "รวมคูณ": sxy, "รวมกำลังสอง": sxx, "phi": phi2, "phi3": _r(phi, 3),
        "รวมคูณการเปลี่ยน": _r(sxy - sxx), "slopeการเปลี่ยน": _r((sxy - sxx) / sxx),
        "คูณซ้ำ": rem, "ครึ่งชีวิต": _r(_hl(phi), 1), "ครึ่งชีวิตจริง": _r(_hl(PHI_TRUE), 1),
        # SE: ทางลัดจากเลขปัด และแบบบท 3 (s ÷ √Σx²)
        "phiกำลังสอง": sq_r, "หนึ่งลบ": one_minus, "หารn": _r(per_n, 4), "SEลัด": se_r, "SEลัด3": _r(se_short, 3),
        "s": _r(a1["sigma"]), "รากรวมกำลังสอง": _r(math.sqrt(sxx)), "SEบท3": _r(se_exact), "SEบท3_3": _r(se_exact, 3),
        "z": _r(z), "ครึ่งกว้าง": half_w, "ล่าง": lo_r, "บน": hi_r,
        "ล่างเต็ม": _r(ci_full["phi_lo"]), "บนเต็ม": _r(ci_full["phi_hi"]),
        "ครึ่งชีวิตล่าง": _r(_hl(lo_r), 1), "lnล่าง": _r(-math.log(lo_r)),
        "ln2": _r(math.log(2), 3), "lnphi": _r(-math.log(phi2), 3),
        "ครึ่งชีวิตจากปัด": _r(math.log(2) / -math.log(phi2), 1),
        # ที่มาของทางลัด: Σx² ÷ n ≈ SD² ของ X ≈ s² ÷ (1 − φ²) (เล่ม 1 บท 13)
        "เฉลี่ยกำลังสอง": _r(sxx / n), "s2": _r(_r(a1["sigma"]) ** 2), "s2หาร": _r(_r(_r(a1["sigma"]) ** 2) / one_minus, 1),
        "รากn": _r(math.sqrt(n), 2), "ล่างกำลังสอง": _r(lo_r * lo_r),
        "รากหนึ่งลบ": _r(math.sqrt(one_minus)), "thetaเปอร์เซ็นต์": _r(-100 * math.log(phi2), 1),
        "SEลัดสองขั้น": _r(_r(math.sqrt(one_minus)) / _r(math.sqrt(n), 2)),
    }

    # ═══ ตอน ข · บันได 20 / 60 / 250 วันของโลกเดียวกัน ═══
    lad = {"วัน": list(LADDER), "แถว": [], "phi": [], "SE": [], "SEลัด": [], "ล่าง": [], "บน": [],
           "ครึ่งชีวิต": [], "ครึ่งชีวิตล่าง": [], "ครึ่งชีวิตบน": [], "ครอบจริง": []}
    world_pct = [round(v * 100, 1) for v in world]                  # หน่วย % ปัดหนึ่งตำแหน่ง (20 วันแรก = ตารางมือก่อนลบ Mean)
    for m in LADDER:
        r = S.ar1(world_pct[:m])
        c = S.half_life_ci(r["phi"], r["se_phi"])
        lad["แถว"].append(r["n"])
        lad["phi"].append(_r(r["phi"]))
        lad["SE"].append(_r(r["se_phi"], 3))
        lad["SEลัด"].append(_r(math.sqrt((1 - r["phi"] ** 2) / r["n"]), 3))
        lad["ล่าง"].append(_r(c["phi_lo"]))
        lad["บน"].append(_r(c["phi_hi"]))
        lad["ครึ่งชีวิต"].append(_r(c["half_life"], 1))
        lad["ครึ่งชีวิตล่าง"].append(_r(c["lo"], 1))
        lad["ครึ่งชีวิตบน"].append(_r(c["hi"], 1) if c["phi_hi"] < 1 else None)
        lad["ครอบจริง"].append(bool(c["phi_lo"] <= PHI_TRUE <= c["phi_hi"]))
    lad["SE2"] = [_r(v) for v in lad["SE"]]
    lad["SEลัด2"] = [_r(v) for v in lad["SEลัด"]]
    lad["SEอัตราส่วน"] = _r(lad["SE"][0] / lad["SE"][2], 1)
    lad["รากอัตราส่วนวัน"] = _r(math.sqrt(lad["แถว"][2] / lad["แถว"][0]), 1)

    # ═══ สามสิบโลก (และ 1,000 โลก) ═══
    def ladder_worlds(seed_list):
        out = {m: {"phi": [], "hl": [], "cover": 0, "finite": 0} for m in LADDER}
        for s in seed_list:
            w = M.stationary_pair(seed=s, n=max(LADDER), phi=PHI_TRUE)["X"]
            for m in LADDER:
                r = S.ar1(w[:m])
                c = S.half_life_ci(r["phi"], r["se_phi"])
                out[m]["phi"].append(r["phi"])
                out[m]["hl"].append(c["half_life"])
                out[m]["cover"] += c["phi_lo"] <= PHI_TRUE <= c["phi_hi"]
                out[m]["finite"] += c["phi_hi"] < 1
        return out
    w30 = ladder_worlds(seeds)
    w1k = ladder_worlds(range(1, N_COVER + 1))
    thirty = {"วัน": list(LADDER), "phiทุกโลก": [[_r(v, 3) for v in w30[m]["phi"]] for m in LADDER],
              "มัธยฐานphi": [_r(statistics.median(w30[m]["phi"])) for m in LADDER],
              "ต่ำกว่าจริง": [sum(v < PHI_TRUE for v in w30[m]["phi"]) for m in LADDER],
              "มัธยฐานครึ่งชีวิต": [_r(statistics.median(w30[m]["hl"]), 1) for m in LADDER],
              "ครอบ": [w30[m]["cover"] for m in LADDER],
              "sdphi": [_r(statistics.stdev(w30[m]["phi"]), 2) for m in LADDER],
              "ต่ำสุด": [_r(min(w30[m]["phi"])) for m in LADDER], "สูงสุด": [_r(max(w30[m]["phi"])) for m in LADDER]}
    thousand = {"จำนวน": N_COVER,
                "ครอบเปอร์เซ็นต์": [_r(100 * w1k[m]["cover"] / N_COVER, 1) for m in LADDER],
                "ต่ำกว่าจริงเปอร์เซ็นต์": [_r(100 * sum(v < PHI_TRUE for v in w1k[m]["phi"]) / N_COVER, 1) for m in LADDER],
                "มัธยฐานphi": [_r(statistics.median(w1k[m]["phi"])) for m in LADDER],
                "มัธยฐานครึ่งชีวิต": [_r(statistics.median(w1k[m]["hl"]), 1) for m in LADDER]}
    # 🔎 สูตรประมาณของ Kendall (1954): ค่าคาดหวังของ φ ที่ประมาณได้ ≈ φ − (1 + 3φ) ÷ n
    thousand["kendall"] = [_r(PHI_TRUE - (1 + 3 * PHI_TRUE) / (m - 1)) for m in LADDER]
    thousand["kendallเลื่อน"] = [_r((1 + 3 * PHI_TRUE) / (m - 1)) for m in LADDER]

    # ═══ ตอน ค · OU ═══
    sd_e = M.SPREAD_SD * 100                                        # แรงสะบัดต่อวันของโลก (%) = 3
    ou_true = S.ou_from_ar1(PHI_TRUE, 0.0, sd_e)
    r250 = S.ar1(world_pct)
    ou_250 = S.ou_from_ar1(r250["phi"], r250["c"], r250["sigma"])
    ou = {"แรงสะบัด": _r(sd_e), "theta": _r(ou_true["theta"], 4), "theta2": _r(ou_true["theta"], 3),
          "หนึ่งลบphi": _r(1 - PHI_TRUE), "ครึ่งชีวิต": _r(ou_true["half_life"], 1),
          "sigma": _r(ou_true["sigma"]), "sdนิ่ง": _r(ou_true["sd_stationary"]),
          "สองtheta": _r(2 * ou_true["theta"], 3), "รากสองtheta": _r(math.sqrt(2 * ou_true["theta"]), 2),
          "sdนิ่งทางที่สอง": _r(ou_true["sigma"] / math.sqrt(2 * ou_true["theta"])),
          "หนึ่งลบphiกำลังสอง": _r(1 - PHI_TRUE ** 2, 4),
          "ประมาณ250": {"theta": _r(ou_250["theta"], 3), "mu": _r(ou_250["mu"], 1), "sigma": _r(ou_250["sigma"]),
                         "ครึ่งชีวิต": _r(ou_250["half_life"], 1), "phi": _r(r250["phi"], 3)},
          "phi7": _r(PHI_TRUE ** 7), "theta7": _r(7 * ou_true["theta"], 2), "ปี": _r(365 * ou_true["theta"], 1),
          "lnphi": _r(math.log(PHI_TRUE), 4), "คูณตรวจ": _r(_r(ou_true["half_life"], 1) * _r(ou_true["theta"], 4), 3),
          "ln05": _r(math.log(0.5), 3), "วงเล็บ": _r(2 * ou_true["theta"] / (1 - PHI_TRUE ** 2), 2),
          "รากวงเล็บ": _r(math.sqrt(2 * ou_true["theta"] / (1 - PHI_TRUE ** 2)), 2),
          "รากหนึ่งลบ": _r(math.sqrt(1 - PHI_TRUE ** 2), 3),
          "thetaเปอร์เซ็นต์": _r(100 * ou_true["theta"]), "theta7เปอร์เซ็นต์": _r(700 * ou_true["theta"], 1),
          "ln05เปอร์เซ็นต์": _r(100 * math.log(0.5), 1), "คูณตรวจเปอร์เซ็นต์": _r(_r(ou_true["half_life"], 1) * _r(100 * ou_true["theta"]), 1),
          "sdนิ่ง1": _r(ou_true["sd_stationary"], 1), "รากหนึ่งลบ2": _r(math.sqrt(1 - PHI_TRUE ** 2)),
          "phiเปอร์เซ็นต์": _r(100 * PHI_TRUE, 1), "phi250เปอร์เซ็นต์": _r(100 * r250["phi"], 1),
          "theta250เปอร์เซ็นต์": _r(100 * ou_250["theta"]),
          "ครึ่งชีวิตสัปดาห์": _r(_hl(PHI_TRUE ** 7), 2), "ครึ่งชีวิตสัปดาห์เป็นวัน": _r(7 * _hl(PHI_TRUE ** 7), 1)}

    # ═══ ข้อมูลจริง ═══
    dates_f, pf = R.load_closes("formation")
    dates_v, pv = R.load_closes("validation")
    coins = list(pf)
    lf = {c: S.logs(pf[c]) for c in coins}
    lv = {c: S.logs(pv[c]) for c in coins}

    def pack(xs, pct=True):
        r = S.ar1(xs)
        c = S.half_life_ci(r["phi"], r["se_phi"])
        k = 100 if pct else 1
        d = {"n": r["n"], "phi": _r(r["phi"]), "phi3": _r(r["phi"], 3), "SE": _r(r["se_phi"], 3),
             "ล่าง": _r(c["phi_lo"], 3), "บน": _r(c["phi_hi"], 3),
             "ครึ่งชีวิต": _r(c["half_life"], 1), "ครึ่งชีวิตล่าง": _r(c["lo"], 1),
             "ครึ่งชีวิตบน": _r(c["hi"], 1) if c["phi_hi"] < 1 else None, "บนอนันต์": bool(c["phi_hi"] >= 1),
             "s": _r(r["sigma"] * k), "Mean": _r(r["mean"] * k, 1) if r["phi"] < 1 else None,
             "phiเปอร์เซ็นต์": _r(100 * r["phi"], 1), "SEเปอร์เซ็นต์": _r(100 * r["se_phi"], 1),
             "ล่างเปอร์เซ็นต์": _r(100 * c["phi_lo"], 1), "บนเปอร์เซ็นต์": _r(100 * c["phi_hi"], 1),
             "thetaเปอร์เซ็นต์": _r(-100 * math.log(r["phi"])) if 0 < r["phi"] < 1 else None}
        if 0 < r["phi"] < 1:
            o = S.ou_from_ar1(r["phi"], r["c"] * k, r["sigma"] * k)
            d.update({"theta": _r(o["theta"], 4), "theta3": _r(o["theta"], 3), "mu": _r(o["mu"], 1),
                      "sigma": _r(o["sigma"]), "sdนิ่ง": _r(o["sd_stationary"], 1), "ปี": _r(365 * o["theta"], 1)})
        return d

    real = {"วันช่วงเลือก": len(dates_f), "วันช่วงตรวจ": len(dates_v),
            "ช่วงเลือก": [dates_f[0], dates_f[-1]], "ช่วงตรวจ": [dates_v[0], dates_v[-1]], "เกณฑ์วัน": HOLD_DAYS}
    single = {c: {"ช่วงเลือก": pack(lf[c]), "ช่วงตรวจ": pack(lv[c])} for c in coins}
    real["เดี่ยว"] = single
    real["เดี่ยวบนจำกัดเลือก"] = sorted(c for c in coins if not single[c]["ช่วงเลือก"]["บนอนันต์"])
    real["เดี่ยวบนอนันต์เลือก"] = sum(single[c]["ช่วงเลือก"]["บนอนันต์"] for c in coins)
    real["เหรียญ"] = len(coins)
    pairs = {}
    for a, b in (("LTC", "DOT"), ("LTC", "LINK"), ("BTC", "ETH")):
        e = S.engle_granger(lf[a], lf[b])
        xv = [ya - e["h"] * yb - e["intercept"] for ya, yb in zip(lv[a], lv[b])]
        ev = S.engle_granger(lv[a], lv[b])
        pairs[f"{a}-{b}"] = {"h": _r(e["h"]), "ช่วงเลือก": pack(e["residuals"]), "ตรวจตรึงh": pack(xv),
                             "ตรวจหาhใหม่": pack(ev["residuals"]), "hตรวจ": _r(ev["h"]),
                             "Meanตรวจตรึงh": _r(100 * S.mean(xv), 1)}
    real["คู่"] = pairs
    ld = pairs["LTC-DOT"]["ช่วงเลือก"]
    real["ต่างเดี่ยวกับคู่"] = _r(abs(single["LTC"]["ช่วงเลือก"]["ครึ่งชีวิต"] - ld["ครึ่งชีวิต"]), 1)
    # ตาราง 10 แถว 📡: X ของ LTC–DOT (h ช่วงเลือก) วันนี้กับพรุ่งนี้ ทุก 73 วัน
    e = S.engle_granger(lf["LTC"], lf["DOT"])
    xr = e["residuals"]
    idx = list(range(0, len(xr) - 1, 73))[:10]
    real["สิบแถว"] = {"ห่าง": 73, "แถว": [{"วันที่": dates_f[i], "วันนี้": _r(100 * xr[i], 1), "พรุ่งนี้": _r(100 * xr[i + 1], 1)}
                                            for i in idx]}
    # รายสัปดาห์ (ทุก 7 วัน) เทียบรายวันยกกำลังเจ็ด · ข้อมูลจริง LTC–DOT ช่วงเลือก
    wk = xr[::7]
    rw_ = S.ar1(wk)
    ph_d = S.ar1(xr)["phi"]
    real["สัปดาห์"] = {"จุด": len(wk), "phi": _r(rw_["phi"]), "phi3": _r(rw_["phi"], 3),
                       "ครึ่งชีวิตสัปดาห์": _r(_hl(rw_["phi"]), 2), "ครึ่งชีวิตวัน": _r(7 * _hl(rw_["phi"]), 1),
                       "รายวันยกเจ็ด": _r(ph_d ** 7), "phiเปอร์เซ็นต์": _r(100 * rw_["phi"], 1),
                       "thetaเปอร์เซ็นต์": _r(-100 * math.log(rw_["phi"]), 1), "thetaสัปดาห์": _r(-math.log(rw_["phi"]), 3),
                       "thetaวันคูณเจ็ด": _r(-7 * math.log(ph_d), 3)}
    # funding BTC (แบบฝึกข้อ 5) · หนึ่งรอบ = 8 ชั่วโมง
    fr = [r_[2] * 100 for r_ in R.load_funding("formation", instrument="BTC-PERPETUAL")]
    pfr = pack(fr, pct=False)
    real["funding"] = {"รอบ": len(fr), "phi": pfr["phi"], "SE": pfr["SE"], "ล่าง": pfr["ล่าง"], "บน": pfr["บน"],
                       "ครึ่งชีวิตรอบ": pfr["ครึ่งชีวิต"], "ครึ่งชีวิตล่าง": pfr["ครึ่งชีวิตล่าง"],
                       "ครึ่งชีวิตบน": pfr["ครึ่งชีวิตบน"], "ครึ่งชีวิตชั่วโมง": _r(8 * pfr["ครึ่งชีวิต"], 0),
                       "thetaรอบ": pfr["theta3"], "thetaวัน": _r(3 * pfr["theta"], 2),
                       "phiวัน": _r(pfr["phi3"] ** 3), "phiเปอร์เซ็นต์": pfr["phiเปอร์เซ็นต์"], "SEเปอร์เซ็นต์": pfr["SEเปอร์เซ็นต์"],
                       "ล่างเปอร์เซ็นต์": pfr["ล่างเปอร์เซ็นต์"], "บนเปอร์เซ็นต์": pfr["บนเปอร์เซ็นต์"],
                       "thetaรอบเปอร์เซ็นต์": _r(pfr["thetaเปอร์เซ็นต์"], 1), "thetaวันเปอร์เซ็นต์": _r(3 * pfr["thetaเปอร์เซ็นต์"], 0), "ครึ่งชีวิตวัน": _r(pfr["ครึ่งชีวิต"] / 3, 2)}

    # ═══ คู่จำลองของข้อมูลจริง ═══
    def ci_world(s, phi_, nn):
        r = S.ar1(M.stationary_pair(seed=s, n=nn, phi=phi_)["X"])
        return r, S.half_life_ci(r["phi"], r["se_phi"])
    like = [ci_world(s, PHI_REAL_LIKE, N_REAL) for s in seeds]
    sim_like = {"phi": PHI_REAL_LIKE, "วัน": N_REAL, "ครึ่งชีวิตจริง": _r(_hl(PHI_REAL_LIKE), 1),
                "มัธยฐานphi": _r(statistics.median(r["phi"] for r, _ in like), 3),
                "ต่ำกว่าจริง": sum(r["phi"] < PHI_REAL_LIKE for r, _ in like),
                "มัธยฐานครึ่งชีวิต": _r(statistics.median(c["half_life"] for _, c in like), 1),
                "ครอบ": sum(c["phi_lo"] <= PHI_REAL_LIKE <= c["phi_hi"] for _, c in like),
                "บนจำกัด": sum(c["phi_hi"] < 1 for _, c in like),
                "บนไม่เกินเกณฑ์": sum(c["phi_hi"] < 1 and c["hi"] <= HOLD_DAYS for _, c in like),
                "มัธยฐานล่าง": _r(statistics.median(c["lo"] for _, c in like), 1),
                "มัธยฐานบน": _r(statistics.median(c["hi"] for _, c in like), 1)}
    # คู่เดินสุ่ม (ไม่มีเชือก) 731 วัน: X จาก Engle–Granger · ทั้งหมด และเฉพาะที่ผ่าน
    rw_all, rw_pass, rw_fin = [], [], 0
    for s in range(1, N_COVER + 1):
        d = M.random_walk_pair(seed=s, n=N_REAL)
        eg = S.engle_granger(d["logA"], d["logB"])
        r = S.ar1(eg["residuals"])
        hl = _hl(r["phi"])
        rw_all.append(hl)
        rw_fin += S.half_life_ci(r["phi"], r["se_phi"])["phi_hi"] < 1
        if eg["reject5"]:
            rw_pass.append(hl)
    bt = pairs["BTC-ETH"]["ช่วงเลือก"]["ครึ่งชีวิต"]
    sim_rw = {"คู่": N_COVER, "วัน": N_REAL, "มัธยฐานทั้งหมด": _r(statistics.median(rw_all), 0),
              "ไม่เกินBTCETH": sum(h <= bt for h in rw_all), "ไม่เกินBTCETHเปอร์เซ็นต์": _r(100 * sum(h <= bt for h in rw_all) / N_COVER, 0),
              "บนจำกัด": rw_fin, "บนจำกัดเปอร์เซ็นต์": _r(100 * rw_fin / N_COVER, 0),
              "ผ่าน": len(rw_pass), "มัธยฐานผ่าน": _r(statistics.median(rw_pass), 1),
              "ผ่านต่ำสุด": _r(min(rw_pass), 1), "ผ่านสูงสุด": _r(max(rw_pass), 1),
              "ผ่านไม่เกินเกณฑ์": sum(h <= HOLD_DAYS for h in rw_pass)}

    # ═══ ตัวเลขเล่ม 1 ที่บททวน (อ่านผ่าน sab_book.load_figures("sab") ที่มาเดียว) ═══
    f1 = SB.load_figures("sab")["ch13"]
    v1 = {"phi": f1["v2"]["phiมือบท9"]["phi"], "ครึ่งชีวิต": f1["v2"]["phiมือบท9"]["ครึ่งชีวิต"],
          "sd080": f1["v2"]["sdหน้า"][1]["sd"], "หนึ่งลบ080": f1["v2"]["sdหน้า"][1]["หนึ่งลบ"],
          "สะบัดกำลังสอง080": f1["v2"]["sdหน้า"][1]["แรงสะบัดกำลังสอง"],
          "สั้นความยาว": f1["ข้อมูลสั้น"]["ความยาว"], "สั้นphiจริง": f1["ข้อมูลสั้น"]["phiจริง"],
          "สั้นมัธยฐาน": f1["ข้อมูลสั้น"]["มัธยฐานที่ประมาณได้"], "สั้นต่ำกว่า": f1["ข้อมูลสั้น"]["ต่ำกว่าจริงเปอร์เซ็นต์"],
          "ครึ่งชีวิต070": next(r["ครึ่งชีวิต"] for r in f1["phiเป็นครึ่งชีวิต"] if r["phi"] == 0.7),
          "ครึ่งชีวิต095": next(r["ครึ่งชีวิต"] for r in f1["phiเป็นครึ่งชีวิต"] if r["phi"] == 0.95),
          "ครึ่งชีวิต099": next(r["ครึ่งชีวิต"] for r in f1["phiเป็นครึ่งชีวิต"] if r["phi"] == 0.99)}

    # ═══ แบบฝึก ═══
    ex2_n = 4 * n                                                         # ข้อมูลยาวขึ้นสี่เท่า (76 แถว)
    ex2_se = _r(math.sqrt(one_minus / ex2_n))
    ex2_lo, ex2_hi = _r(phi2 - _r(z * ex2_se)), _r(phi2 + _r(z * ex2_se))
    ex4 = pairs["LTC-LINK"]["ตรวจหาhใหม่"]
    drills = {"ข้อ2": {"แถว": ex2_n, "SE": ex2_se, "ครึ่งกว้าง": _r(z * ex2_se), "ล่าง": ex2_lo, "บน": ex2_hi,
                       "ครึ่งชีวิตล่าง": _r(_hl(ex2_lo), 1), "ครึ่งชีวิตบน": _r(_hl(ex2_hi), 1),
                       "หารn": _r(one_minus / ex2_n, 4), "ผิดไม่ราก": _r(se_r / 4, 3), "รากn": _r(math.sqrt(ex2_n), 2)},
              "ข้อ1ผิดลืมยก": _r(math.sqrt((1 - phi2) / n), 2)}

    ch = {"เล่ม1": v1, "มือ": hand, "บันได": lad, "สามสิบโลก": thirty, "พันโลก": thousand, "ou": ou, "จริง": real,
          "จำลองคู่": sim_like, "จำลองเดินสุ่ม": sim_rw, "แบบฝึก": drills,
          "บันทึก": {"แบบที่ลองเพิ่ม": 3, "ช่วงตรวจดูไปแล้ว": 1},
          "อ้างอิง": {"ปีKendall": 1954, "เส้นADF731": _r(S.adf_crit(N_REAL - 1)["5%"]), "phiห่างออก": f1["ตารางphi"]["1.02"]["phi"],
                      "แกนphi": [0.5, 1.1], "แกนวัน": [0, 120]}}
    ch["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) Σ วันนี้×พรุ่งนี้ 438.04 · Σ วันนี้² 535.44 · 19 แถว → φ · SE ลัด · ช่วง 95% · Half-life สองปลาย",
         "คำตอบ": hand["บน"]},
        {"โจทย์": "(เปลี่ยนเลข) φ 0.82 เท่าเดิม แต่ข้อมูล 76 แถว → SE และช่วง Half-life", "คำตอบ": drills["ข้อ2"]["ครึ่งชีวิตบน"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข · ข้อมูลจริง) LTC–DOT รายสัปดาห์ φ 0.83 → Half-life เป็นวัน เทียบรายวัน",
         "คำตอบ": real["สัปดาห์"]["ครึ่งชีวิตวัน"]},
        {"โจทย์": "(ตัดสินใจ) LTC–LINK ช่วงตรวจหา h ใหม่ Half-life 8.7 [5.6, 18.4] แคบและเร็ว → เปิดไม้ไหม",
         "คำตอบ": ex4["ครึ่งชีวิต"]},
        {"โจทย์": "(ถ่ายโอน) funding BTC φ ต่อรอบ 8 ชั่วโมง → ช่วง และ Half-life เป็นวัน", "คำตอบ": real["funding"]["ครึ่งชีวิตวัน"]},
    ]
    ch["_claims"] = [{"id": "sab2-ch04-kendall",
                      "ข้อความ": "ค่า φ ที่ประมาณจากข้อมูลสั้นเอนลงด้วยขนาดราว (1 + 3φ) ÷ n (Kendall 1954) · บทนี้แสดงด้วยการจำลอง "
                                 "1,000 โลกและเทียบสูตรใน 🔎",
                      "ระดับหลักฐาน": "ตีพิมพ์", "แหล่ง": "Kendall, M. G. (1954) Note on bias in the estimation of autocorrelation. "
                                                        "Biometrika 41", "บท": [4]}]
    return ch
