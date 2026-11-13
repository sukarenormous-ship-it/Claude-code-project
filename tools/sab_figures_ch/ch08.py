"""บท 8 — hedge แล้ว…จากอะไร · ค่าที่บทพิมพ์แต่ยังไม่มีใน JSON หลัก

ทุกค่าคำนวณจาก บัญชีมิน (คู่ A = 100 · B = 50 · beta ตรึง A 1.5 / B 1.0 / stress 1.7 · BTC 100,000) + ch08 เดิม
ค่าตั้งต้นที่บทนี้สมมติเอง (🔢 ตัวเลขสอน) ประกาศเป็นค่าคงที่ข้างล่างพร้อมเหตุผล ผลทุกตัวคำนวณจากค่าเหล่านั้น
ห้ามใช้คีย์ "beta" ที่มี "A" ข้างใน (sab_check_figures.py ตรวจว่าเท่าค่าตรึง) — ตัวอย่างนับใช้คีย์ "ผล"
"""

# ── ตัวอย่างนับ beta (🔢): 8 วันของ A กับ BTC เป็น % · วันที่ |BTC| ≤ 2% ไม่นับ (ขยับน้อย ผลของ A เป็นเรื่องเฉพาะตัวมากกว่า)
# ออกแบบให้วันที่นับรวมได้ 1.5 = ค่าตรึง (assert ข้างล่าง) และวันลงหนักกว่าวันขึ้น — ไว้ปูทาง stress 1.5 → 1.7
BETA_DAYS = [("3", "4"), ("0.8", "-0.4"), ("-2.5", "-4.5"), ("2.2", "2"),
             ("-1.2", "0.3"), ("-5", "-8.5"), ("3.3", "5"), ("-4", "-6")]   # (BTC, A) · วันสุดท้าย = คืนในฉากเปิด
BETA_CUT = "2"

# ── แยกกำไรขาดทุนสามบรรทัด (🔢 สถานการณ์ที่ให้มา ไม่ต้องหา loading เอง)
SPLIT = {"BTC": "-3", "กลุ่ม": "-4", "Aเอง": "1", "Bเอง": "-1"}   # % · กลุ่มขยับ → A และ B ขยับเพิ่มเท่ากัน

STRESS_DOWN = -5       # แผน: beta ของ A 1.5 → 1.7 แล้ว BTC −5% (ตรงกับ ch08.beta_stress.BTC-5%)

# ── ✍️
EX2_B_NEWS = "2"        # ข้อ 2: ข่าวเฉพาะของ B ทำให้ B ขึ้นเอง 2%
EX3 = {"หุ้น": "2000", "beta": "1.3", "shortดัชนี": "2000", "ดัชนีลง": "-5"}   # ข้อ 3 (ถ่ายโอน) ตลาดหุ้น


def extend(data, D, q):
    m, c = data["บัญชีมิน"], data["ch08"]
    bA, bB, bS = D(str(m["beta"]["A"])), D(str(m["beta"]["B"])), D(str(m["beta"]["A_stress"]))
    pA, pB, nA = D(m["คู่"]["A"]), D(m["คู่"]["B"]), D(m["คู่"]["จำนวนA"])
    btc = D(m["BTC"]["spot"])
    lot = D("0.01")
    vA = pA * nA                                      # 1,000
    assert vA == D(c["ขาเดียว"]["A"])

    # ฉากเปิด: short BTC perp มูลค่าเท่า A
    vBTC = vA
    expo_scene = vA * bA - vBTC                       # +500
    down4 = D(c["ขาเดียว"]["BTCลงเปอร์เซ็นต์"])
    assert q(expo_scene * down4 / 100, 0) == c["ขาเดียว"]["รวม"]

    # beta-neutral ด้วย BTC
    vFull = vA * bA                                   # 1,500
    lots_full = vFull / (btc * lot)                   # 1.5 ล็อตของ 0.01 BTC
    lot_value = btc * lot                             # 1,000 ต่อล็อต

    # ตัวอย่างนับ beta
    days = []
    sA = sB = dA = dB = uA = uB = D(0)
    for b, a in BETA_DAYS:
        b, a = D(b), D(a)
        used = abs(b) > D(BETA_CUT)
        sign = 1 if b > 0 else -1
        days.append({"BTC": q(b, 1), "A": q(a, 1), "นับ": used, "Aต่อBTC": q(a / b, 2)})
        if used:
            sA += a * sign
            sB += abs(b)
            if b < 0:
                dA, dB = dA + a * sign, dB + abs(b)
            else:
                uA, uB = uA + a * sign, uB + abs(b)
    res = sA / sB
    assert res == bA, "ตัวอย่างนับต้องได้ค่าตรึง 1.5"
    nused = sum(1 for d in days if d["นับ"])

    # แยกสามบรรทัด
    mk, gr, oa, ob = (D(SPLIT[k]) / 100 for k in ("BTC", "กลุ่ม", "Aเอง", "Bเอง"))
    vB20 = pB * 20                                    # B 20 เหรียญ = มูลค่าเท่า A
    split = {
        "BTCเปอร์เซ็นต์": q(D(SPLIT["BTC"]), 0), "กลุ่มเปอร์เซ็นต์": q(D(SPLIT["กลุ่ม"]), 0),
        "Aเองเปอร์เซ็นต์": q(D(SPLIT["Aเอง"]), 0), "Bเองเปอร์เซ็นต์": q(D(SPLIT["Bเอง"]), 0),
        "Aรวมเปอร์เซ็นต์": q((bA * mk + gr + oa) * 100, 1), "Bรวมเปอร์เซ็นต์": q((bB * mk + gr + ob) * 100, 1),
    }
    hb = {"ตลาด": vA * bA * mk - vFull * mk, "กลุ่ม": vA * gr, "เฉพาะเหรียญ": vA * oa}
    hB = {"ตลาด": vA * bA * mk - vB20 * bB * mk, "กลุ่ม": vA * gr - vB20 * gr, "เฉพาะเหรียญ": vA * oa - vB20 * ob}
    for name, d in (("hedgeBTC1500", hb), ("hedgeB20", hB)):
        d["รวม"] = sum(d.values())
        split[name] = {k: q(v, 0) for k, v in d.items()}

    # funding ของขา hedge 1,500 ต่อเดือน (รอบละ 8 ชั่วโมงในตัวอย่างนี้ → 3 รอบต่อวัน × 30 วัน)
    rounds_day = D(24) / D(m["funding"]["ชั่วโมงต่อรอบในตัวอย่าง"])
    rounds30 = rounds_day * 30
    per_round = D(str(c["hedgeด้วยperp"]["ต่อรอบ"]))

    # ✍️ ข้อ 1: ปัดล็อต → BTC −4%
    lo, hi = c["ปัดlot"]["ปัดลง"]["exposure"], c["ปัดlot"]["ปัดขึ้น"]["exposure"]
    # ✍️ ข้อ 2: B 20 vs 30 เหรียญ เมื่อ BTC −4% / เมื่อ B ขึ้นเอง 2%
    news = D(EX2_B_NEWS) / 100
    ex2 = {"Bขึ้นเองเปอร์เซ็นต์": q(D(EX2_B_NEWS), 0)}
    for n in (20, 30):
        vb = pB * n
        ex2[f"B{n}"] = {"BTCลง4": q((vA * bA - vb * bB) * down4 / 100, 0), "Bข่าว": q(-vb * news, 0)}
    # ✍️ ข้อ 3: หุ้นเล็ก hedge ด้วย short ดัชนี
    s, sb, si, dn = (D(EX3[k]) for k in ("หุ้น", "beta", "shortดัชนี", "ดัชนีลง"))
    ex3 = {"หุ้น": q(s, 0), "betaหุ้น": q(sb, 1), "shortดัชนี": q(si, 0), "ดัชนีลงเปอร์เซ็นต์": q(dn, 0),
           "exposure": q(s * sb - si, 0), "ผลดัชนีลง": q((s * sb - si) * dn / 100, 0), "shortที่เป็นกลาง": q(s * sb, 0)}

    assert q((vA * bS - vFull) * STRESS_DOWN / 100, 0) == c["beta_stress"]["BTC-5%"]
    meth = c["สามวิธี"]
    return {
        "ฉาก": {
            "Aจำนวน": q(nA, 0), "Aราคา": q(pA, 0), "Aมูลค่า": q(vA, 0), "BTCมูลค่า": q(-vBTC, 0),
            "BTCจำนวน": q(vBTC / btc, 2), "net": q(vA - vBTC, 0), "gross": q(vA + vBTC, 0),
            "betaA": q(bA, 1), "betaBTC": q(D(1), 1),
            "betaexposureA": q(vA * bA, 0), "betaexposureBTC": q(-vBTC, 0), "betaexposureสุทธิ": q(expo_scene, 0),
            "BTCลง4": q(expo_scene * down4 / 100, 0),
            # ซ้อม stress กับขนาดในฉาก: beta ของ A เป็น 1.7 แล้ว BTC −5% (hedge 1,000 เท่าเดิม)
            "stressexposure": q(vA * bS - vBTC, 0), "stressBTC-5": q((vA * bS - vBTC) * STRESS_DOWN / 100, 0),
        },
        "hedgeBTCเต็ม": {
            "มูลค่า": q(vFull, 0), "ล็อต": q(lots_full, 1), "มูลค่าต่อล็อต": q(lot_value, 0),
            "net": q(vA - vFull, 0), "gross": q(vA + vFull, 0), "betaexposure": q(vA * bA - vFull, 0),
            "betaexposureAใหม่": q(vA * bS, 0),
        },
        "grossสามวิธี": {k: q(vA + D(meth[k]["มูลค่าB"]), 0) for k in ("จำนวนเท่ากัน", "มูลค่าเท่ากัน", "betaneutral")},
        "นับbeta": {
            "เกณฑ์เปอร์เซ็นต์": q(D(BETA_CUT), 0), "วัน": days, "จำนวนวัน": len(days), "วันที่นับ": nused,
            "ผลรวมA": q(sA, 1), "ผลรวมBTC": q(sB, 1), "ผล": q(res, 1),
            "วันลง": {"A": q(dA, 1), "BTC": q(dB, 1), "ผล": q(dA / dB, 2)},
            "วันขึ้น": {"A": q(uA, 1), "BTC": q(uB, 1), "ผล": q(uA / uB, 2)},
        },
        "แยกสามบรรทัด": split,
        "fundingเดือน": {"รอบต่อวัน": q(rounds_day, 0), "รอบ30วัน": q(rounds30, 0), "รวม30วัน": q(per_round * rounds30, 2)},
        "แบบฝึก": {
            "ข้อ1": {"ล็อตต้องการ": q(lots_full, 1), "ปัดลงBTCลง4": q(D(lo) * down4 / 100, 0),
                     "ปัดขึ้นBTCลง4": q(D(hi) * down4 / 100, 0)},
            "ข้อ2": ex2,
            "ข้อ3": ex3,
        },
        "_claims": [
            {"id": "ch08-smallcap-beta", "ข้อความ": "ในวันที่ตลาดคริปโตลงแรง เหรียญเล็กมักลงแรงกว่า BTC (beta มากกว่า 1) · "
             "แต่ไม่ใช่ทุกเหรียญและทุกช่วง — ค่าที่วัดได้แกว่งตามช่วงข้อมูล และบางเหรียญมีข่าวของตัวเองกลบผลของตลาด",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [8]},
            {"id": "ch08-beta-shift", "ข้อความ": "beta ที่วัดจากอดีตเปลี่ยนได้ โดยเฉพาะช่วงตลาดลงแรงที่หลายเหรียญขยับไปทางเดียวกันมากขึ้น · "
             "hedge ที่ตั้งจากค่าเก่าจึงเหลือ exposure ที่ไม่ได้ตั้งใจ — การวัดใหม่บ่อยขึ้นช่วยได้แต่ตามหลังเหตุการณ์เสมอ",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [8]},
        ],
        "_แบบฝึก": [
            {"โจทย์": "A 1,000 beta 1.5 ต้อง hedge BTC 1.5 ล็อต (ล็อตละ 0.01 BTC = 1,000) · ปัดลงเป็น 1 ล็อต เหลือ beta exposure เท่าไร",
             "คำตอบ": c["ปัดlot"]["ปัดลง"]["exposure"]},
            {"โจทย์": "ขา B 30 เหรียญ (1,500) เมื่อ B ขึ้นเอง 2% เสียเท่าไร (เทียบ 20 เหรียญ)",
             "คำตอบ": ex2["B30"]["Bข่าว"]},
            {"โจทย์": "หุ้น 2,000 beta 1.3 เทียบดัชนี ต้อง short ดัชนีเท่าไรจึงเป็นกลางต่อตลาด",
             "คำตอบ": ex3["shortที่เป็นกลาง"]},
        ],
    }
