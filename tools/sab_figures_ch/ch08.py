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

# ── v2 (แผน 14 · คู่มือ v2 §8): ผลกลางทางที่บทแสดงการคิด อยู่ใต้ ch08.v2.* ─────────────────────────
# ตาราง beta 8 วันของ v2 (แทนตัวอย่างเดิมในหน้า · คีย์ ch08.นับbeta เดิมยังอยู่): มีวันที่ไม่นับ 2 วัน และวันที่นับแต่
# A สวนทาง BTC 1 วัน (วันที่ 6) เพื่อให้กติกา "จดลบเมื่อสวนทาง" ได้ใช้จริง · วันลง 3 วันรวมได้ 1.7 = ค่า stress ตรึง
# (ให้ค่า stress มีที่มาบนหน้า) · วันขึ้นได้ 1.3 · ทุกวันที่นับรวมได้ 1.5 = ค่าตรึง
BETA_DAYS_V2 = [("3", "5.5"), ("0.8", "-0.4"), ("-2.5", "-4"), ("4", "8.5"),
                ("-1.2", "0.3"), ("3", "-1"), ("-3.5", "-7"), ("-4", "-6")]   # (BTC, A) · วันสุดท้าย = คืนในฉาก
# สามคืนจากจุดเปิดเดียวกัน (A 10 เหรียญที่ 100 · short BTC 0.01 ที่ 100,000): (A %, BTC %)
NIGHTS_V2 = {"หักกันพอดี": ("-4", "-4"), "คืนในฉาก": ("-6", "-4"), "เสียทั้งสองขา": ("-6", "2")}
# ✍️ v2
EX1_V2 = {"BTC": "3", "A": "4.5"}          # ข้อ 1 ทำตาม: คืนที่ BTC +3% และ A +4.5%
EX2_V2_BETA = "2"                          # ข้อ 2 เปลี่ยนเลขหนึ่งตัว: เหรียญที่ beta 2.0 แทน 1.5

# ── ✍️
EX2_B_NEWS = "2"        # ข้อ 2: ข่าวเฉพาะของ B ทำให้ B ขึ้นเอง 2%
EX3 = {"หุ้น": "2000", "beta": "1.3", "shortดัชนี": "2000", "ดัชนีลง": "-5"}   # ข้อ 3 (ถ่ายโอน) ตลาดหุ้น


def _v2(data, D, q, split_old):
    """ผลกลางทางของบท 8 v2 — ทุกค่าคำนวณจากบัญชีมินและค่าคงที่ข้างบน · assert ให้ตรงกับคีย์เดิมที่หน้าอื่นใช้"""
    m, c = data["บัญชีมิน"], data["ch08"]
    bA, bB, bS = D(str(m["beta"]["A"])), D(str(m["beta"]["B"])), D(str(m["beta"]["A_stress"]))
    pA, pB, nA = D(m["คู่"]["A"]), D(m["คู่"]["B"]), D(m["คู่"]["จำนวนA"])
    btc, lot = D(m["BTC"]["spot"]), D("0.01")
    vA = pA * nA                                       # 1,000
    vS = btc * lot                                     # short BTC 0.01 = 1,000
    pct = lambda x: D(x) / 100

    # ── ตอน ก · หนึ่งเหรียญก่อน แล้วสามคืนจากจุดเปิดเดียวกัน
    nights = {}
    for name, (a, b) in NIGHTS_V2.items():
        a_px, b_px = pA * (1 + pct(a)), btc * (1 + pct(b))
        a_leg = (a_px - pA) * nA
        buy_back = b_px * lot
        s_leg = vS - buy_back
        nights[name] = {"Aเปอร์เซ็นต์": q(D(a), 0), "BTCเปอร์เซ็นต์": q(D(b), 0),
                        "Aราคาใหม่": q(a_px, 0), "Aหนึ่งเหรียญ": q(a_px - pA, 0), "Aมูลค่าใหม่": q(a_px * nA, 0),
                        "ขาA": q(a_leg, 0), "BTCราคาใหม่": q(b_px, 0), "ซื้อคืน": q(buy_back, 0),
                        "ขาBTC": q(s_leg + 0, 0), "รวม": q(a_leg + s_leg + 0, 0)}
    assert nights["คืนในฉาก"]["รวม"] == c["ขาเดียว"]["รวม"]
    assert nights["คืนในฉาก"]["ขาA"] == c["ขาเดียว"]["ขาA"] and nights["คืนในฉาก"]["ขาBTC"] == c["ขาเดียว"]["ขาshortBTC"]
    # หนึ่งเหรียญ A คู่กับ short BTC มูลค่า 100 (0.001 BTC) — ใช้ในประโยค "หนึ่งเหรียญก่อน"
    sa, sb = (pct(x) for x in NIGHTS_V2["คืนในฉาก"])
    one = {"BTCต่อเหรียญ": q(pA / btc, 3), "ขาAหนึ่งเหรียญ": q(pA * sa, 0), "ขาBTCหนึ่งเหรียญ": q(-pA * sb, 0),
           "รวมหนึ่งเหรียญ": q(pA * sa - pA * sb, 0)}

    # ── ตอน ก · ตาราง beta 8 วัน
    days, sA, sB, dA, dB, uA, uB = [], D(0), D(0), D(0), D(0), D(0), D(0)
    for b, a in BETA_DAYS_V2:
        b, a = D(b), D(a)
        used = abs(b) > D(BETA_CUT)
        same = (a > 0) == (b > 0)
        recA = abs(a) if same else -abs(a)
        days.append({"BTC": q(b, 1), "A": q(a, 1), "นับ": used, "ทิศ": "เดียวกัน" if same else "สวนทาง",
                     "BTCที่จด": q(abs(b), 1), "Aที่จด": q(recA, 1), "Aต่อBTC": q(recA / abs(b), 2)})
        if used:
            sA, sB = sA + recA, sB + abs(b)
            if b < 0:
                dA, dB = dA + recA, dB + abs(b)
            else:
                uA, uB = uA + recA, uB + abs(b)
    assert sA / sB == bA, "ตาราง beta v2 ต้องได้ค่าตรึง 1.5"
    assert dA / dB == bS, "วันลงของตาราง v2 ต้องได้ค่า stress ตรึง 1.7"
    ratios = [d["Aต่อBTC"] for d in days if d["นับ"]]
    beta = {"วัน": days, "จำนวนวัน": len(days), "วันที่นับ": sum(1 for d in days if d["นับ"]),
            "วันที่ไม่นับ": sum(1 for d in days if not d["นับ"]),
            "ผลรวมA": q(sA, 1), "ผลรวมBTC": q(sB, 1), "ผล": q(sA / sB, 1),
            "วันลง": {"A": q(dA, 1), "BTC": q(dB, 1), "ผล": q(dA / dB, 1)},
            "วันขึ้น": {"A": q(uA, 1), "BTC": q(uB, 1), "ผล": q(uA / uB, 1)},
            "รายวันต่ำสุด": min(ratios), "รายวันสูงสุด": max(ratios)}

    # ── ตอน ข · Exposure · เป็นกลางสองแบบ · ล็อต
    down4 = pct(c["ขาเดียว"]["BTCลงเปอร์เซ็นต์"])
    vFull = vA * bA                                    # 1,500
    full_btc = vFull / btc                             # 0.015 BTC
    buy_full = full_btc * btc * (1 + down4)            # 1,440
    expo = {"แรงA": q(vA * bA, 0), "แรงBTC": q(-vS, 0), "สุทธิ": q(vA * bA - vS, 0),
            "BTCลง4": q((vA * bA - vS) * down4, 0),
            "เต็ม": {"BTC": q(full_btc, 3), "ซื้อคืน": q(buy_full, 0), "ขาBTC": q(vFull - buy_full, 0),
                     "ขาA": c["ขาเดียว"]["ขาA"], "รวม": q(vA * down4 * bA + vFull - buy_full + 0, 0)}}
    a2 = nA * 2                                        # ปรับขาที่ถือแทน: A 20 เหรียญ
    lots = {"ต่อล็อต": q(vS, 0), "ต้องการ": q(vFull / vS, 1),
            "ปัดลง": {"exposure": q(vFull - vS, 0), "BTCลง4": q((vFull - vS) * down4, 0)},
            "ปัดขึ้น": {"มูลค่า": q(2 * vS, 0), "exposure": q(vFull - 2 * vS, 0),
                       "BTCลง4": q((vFull - 2 * vS) * down4, 0), "BTCขึ้น4": q((vFull - 2 * vS) * -down4, 0)},
            "Aสองเท่า": {"จำนวน": q(a2, 0), "มูลค่า": q(pA * a2, 0), "แรง": q(pA * a2 * bA, 0),
                         "BTC": q(pA * a2 * bA / btc, 2), "ล็อต": q(pA * a2 * bA / vS, 0)}}
    assert lots["ปัดลง"]["exposure"] == c["ปัดlot"]["ปัดลง"]["exposure"]

    # ── ตอน ค · beta 1.5 → 1.7 แล้ว BTC −5% (ตรวจสองทาง: แรงสุทธิ × % กับทีละขา)
    dn = pct(STRESS_DOWN)
    a_leg_s = vA * bS * dn                             # A ขยับ 1.7 × −5% = −8.5% → −85
    stress = {"Aเปอร์เซ็นต์": q(bS * STRESS_DOWN, 1), "ขาA": q(a_leg_s, 0)}
    for h in (vFull, vS):
        stress[f"hedge{q(h, 0)}"] = {"แรงสุทธิ": q(vA * bS - h, 0), "ขาBTC": q(-h * dn, 0), "รวม": q(a_leg_s - h * dn, 0)}
    assert stress["hedge1500"]["รวม"] == c["beta_stress"]["BTC-5%"]   # hedge 1,000 = ch08.ฉาก.stressBTC-5 (คำนวณใน extend)

    # ── ตอน ค · สามบรรทัดทีละขา
    mk, gr, oa, ob = (pct(SPLIT[k]) for k in ("BTC", "กลุ่ม", "Aเอง", "Bเอง"))
    vB20 = pB * 20
    A_lines = {"ตลาด": vA * bA * mk, "กลุ่ม": vA * gr, "เฉพาะเหรียญ": vA * oa}
    legs = {"hedgeBTC1500": {"ตลาด": -vFull * mk, "กลุ่ม": D(0), "เฉพาะเหรียญ": D(0)},
            "hedgeB20": {"ตลาด": -vB20 * bB * mk, "กลุ่ม": -vB20 * gr, "เฉพาะเหรียญ": -vB20 * ob}}
    split = {"ขาA": {k: q(v, 0) for k, v in A_lines.items()}, "ขาAรวม": q(sum(A_lines.values()), 0)}
    for name, hl in legs.items():
        split[name] = {"ขาhedge": {k: q(v + 0, 0) for k, v in hl.items()}, "ขาhedgeรวม": q(sum(hl.values()) + 0, 0)}
        for k in A_lines:
            assert q(A_lines[k] + hl[k], 0) == split_old[name][k]
        assert q(sum(A_lines.values()) + sum(hl.values()), 0) == split_old[name]["รวม"]

    # ── ตอน ค · ขา B 10 / 20 / 30 เหรียญ ทีละขา
    bnews = D(1) / 100
    sizes = {}
    for n in (10, 20, 30):
        vb = pB * n
        sizes[f"B{n}"] = {"มูลค่า": q(vb, 0), "แรงB": q(vb * bB, 0), "ขาBเมื่อBTCลง4": q(-vb * bB * down4, 0),
                          "ขาAเมื่อBTCลง4": q(vA * bA * down4, 0), "รวมBTCลง4": q((vA * bA - vb * bB) * down4, 0),
                          "Bขึ้นเอง1": q(-vb * bnews, 0)}
    assert [sizes[k]["รวมBTCลง4"] for k in ("B10", "B20", "B30")] == \
        [c["สามวิธี"][k]["BTCลง4"] for k in ("จำนวนเท่ากัน", "มูลค่าเท่ากัน", "betaneutral")]
    sizes["Bต่อAหนึ่งเหรียญเป็นกลาง"] = q(pA * bA / (pB * bB), 0)          # 3

    # ── ✍️
    e1b, e1a = pct(EX1_V2["BTC"]), pct(EX1_V2["A"])
    ex1 = {"BTCเปอร์เซ็นต์": q(D(EX1_V2["BTC"]), 0), "Aเปอร์เซ็นต์": q(D(EX1_V2["A"]), 1),
           "ขาA": q(vA * e1a, 0), "ซื้อคืน": q(vS * (1 + e1b), 0), "ขาBTC": q(-vS * e1b, 0),
           "รวม": q(vA * e1a - vS * e1b, 0), "ตรวจExposure": q((vA * bA - vS) * e1b, 0)}
    assert ex1["รวม"] == ex1["ตรวจExposure"]
    b2 = D(EX2_V2_BETA)
    ex2 = {"beta": q(b2, 1), "แรง": q(vA * b2, 0), "exposure": q(vA * b2 - vS, 0), "BTCลง4": q((vA * b2 - vS) * down4, 0),
           "shortที่เป็นกลาง": q(vA * b2, 0), "ล็อต": q(vA * b2 / vS, 0)}
    nb = NIGHTS_V2["เสียทั้งสองขา"]
    mkt_A = vA * bA * pct(nb[1])                       # +30
    ex3 = {"Aจากตลาดเปอร์เซ็นต์": q(bA * D(nb[1]), 0), "ขาAส่วนตลาด": q(mkt_A, 0),
           "ขาBTC": nights["เสียทั้งสองขา"]["ขาBTC"], "บรรทัดตลาด": q(mkt_A + D(nights["เสียทั้งสองขา"]["ขาBTC"]), 0),
           "บรรทัดเฉพาะA": q(D(nights["เสียทั้งสองขา"]["ขาA"]) - mkt_A, 0), "รวม": nights["เสียทั้งสองขา"]["รวม"]}
    assert ex3["บรรทัดตลาด"] + ex3["บรรทัดเฉพาะA"] == ex3["รวม"]
    return {"สามคืน": nights, "หนึ่งเหรียญ": one, "นับbeta": beta, "exposure": expo, "ล็อต": lots,
            "stress": stress, "สามบรรทัด": split, "ขาB": sizes,
            "แบบฝึก": {"ข้อ1": ex1, "ข้อ2": ex2, "ข้อ3": ex3}}


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
    v2 = _v2(data, D, q, split)
    return {
        "v2": v2,                                                     # คู่มือ v2 §8: คีย์ใหม่ของ v2 อยู่ใต้ ch08.v2.*
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
            "BTCลง4": q((vA * bA - vFull) * down4 / 100 + 0, 0),   # + 0 กัน Decimal −0
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
        "_แบบฝึก": [   # ห้าข้อของ ✍️ v2 (ข้อ 1–3 ใหม่ · ข้อ 4–5 = ข้อ 2–3 เดิม)
            {"โจทย์": "A 1,000 + short BTC 1,000 · คืนที่ BTC +3% และ A +4.5% ทั้งชุดได้เท่าไร",
             "คำตอบ": v2["แบบฝึก"]["ข้อ1"]["รวม"]},
            {"โจทย์": "เหรียญ beta 2.0 มูลค่า 1,000 + short BTC 1,000 · beta exposure เท่าไร",
             "คำตอบ": v2["แบบฝึก"]["ข้อ2"]["exposure"]},
            {"โจทย์": "คืนเสียทั้งสองขา (A −6% · BTC +2%) ของชุด A 1,000 + short BTC 1,000 · บรรทัดเฉพาะเหรียญ A เท่าไร",
             "คำตอบ": v2["แบบฝึก"]["ข้อ3"]["บรรทัดเฉพาะA"]},
            {"โจทย์": "ขา B 30 เหรียญ (1,500) เมื่อ B ขึ้นเอง 2% เสียเท่าไร (เทียบ 20 เหรียญ)",
             "คำตอบ": ex2["B30"]["Bข่าว"]},
            {"โจทย์": "หุ้น 2,000 beta 1.3 เทียบดัชนี ต้อง short ดัชนีเท่าไรจึงเป็นกลางต่อตลาด",
             "คำตอบ": ex3["shortที่เป็นกลาง"]},
        ],
    }
