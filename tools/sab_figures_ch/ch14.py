"""บท 14 — −21 แล้วสัญญาณกลับมาที่ 3.8 · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py)

ทุกค่าคำนวณจาก ch12 / ch14 / ch08 / บัญชีมิน ที่ sab_figures.py สร้างแล้ว — ไม่มีตัวเลขผลลัพธ์ลอย
- ไม้3: สรุปไม้ 3 (short X 10 ชุด เข้า 2.1 ปิด 4.1) · บัญชีคู่ก่อน/หลัง · เส้นงบ · % ของทุนรวม
- ถ้าเข้า38: สองโลกของไม้ที่ถูกบล็อก — เชือกยังอยู่ (3.8 → 2.4 = ราคาการพัก) vs
  เชือกขาด (X ขยับต่อเท่าที่ไม้ 3 ขยับ 2.1 → 4.1 = 2.0 → ปิดที่ 5.8) ⓝ สมมติฐานของบท
- ตลาด: ไม้ 3 เป็นฝั่งกลับด้าน (short A 10 · ซื้อ B 20) beta exposure −500 · BTC +4% → −20 = X ขยับ 2 ต่อ 10 ชุด
- หลายคู่: ถือ 3 คู่ฝั่งเดียวกันที่ +500 ต่อคู่ · BTC −4% → เสียพร้อมกัน
- dist: สัดส่วนตอนจบสองโลกของบท 12 (60/25/15 · 45/20/35) → โอกาสที่สามไม้แรกไม่ชนงบ ·
  โอกาสที่สามไม้รวมกันได้ −3 หรือแย่กว่า (ผลจริงของมิน 16 + 2 − 21) · เฉลี่ยสามไม้
- แบบฝึกก: เส้นทางใหม่หลังพัก 0 → 2.3 → 3.0 → 4.4 → 3.6 → 1.0 (สมมติเพื่อสอน)
- แบบฝึกค: basis คืนวันที่ 9 (บท 4) = 113,200 − 110,000 เทียบ X 2.8 → 4.1
"""
from itertools import product


def _exit_by_card(path, entry_i, sets, cost, budget, exit_line, max_hold):
    """เดินการ์ดบท 12 ฝั่ง short X จากจุดเข้า: คืน (ดัชนีที่ออก, เหตุออก, สุทธิ) · ลำดับตรวจ ขาดทุน → สัญญาณ → เวลา"""
    e = path[entry_i]
    for j in range(entry_i + 1, len(path)):
        net = sets * (e - path[j]) - cost
        if net <= budget:
            return j, "งบ", net
        if path[j] <= exit_line:
            return j, "เป้า", net
        if j - entry_i >= max_hold:
            return j, "เวลา", net
    return None, None, None


def extend(data, D, q):
    c = data["ch14"]
    acct = data["บัญชีมิน"]
    card, pair = acct["การ์ด"], acct["คู่"]
    sets = D(str(pair["ชุด"]))
    cost = D(str(card["ต้นทุนเข้า"])) + D(str(card["ต้นทุนออก"]))
    budget = D(str(card["งบขาดทุนสุทธิ"]))
    total = D(str(acct["กฎ1%"]["ทุนรวมดอลลาร์"]))
    path = [D(str(x)) for x in c["เส้นทาง"]]

    # ── ไม้ 3 ──
    p3 = data["ch12"]["เส้นทาง"]["3"]
    e3, x3 = D(str(p3["Xเข้า"])), D(str(p3["Xออก"]))
    net3 = q(sets * (e3 - x3) - cost, 0)
    assert net3 == p3["สุทธิ"], "ไม้ 3 ไม่ตรง ch12"
    before = data["เรื่อง"]["part14"]["open"]["บัญชีคู่"]
    after = before + net3
    assert after == c["บัญชีคู่"], "บัญชีคู่ไม่ตรง ch14"
    trade3 = {"บัญชีคู่ก่อน": before, "บัญชีคู่หลัง": after, "สุทธิ": net3,
              "Xขยับ": q(x3 - e3, 1), "เส้นงบ": q(e3 + (-budget - cost) / sets, 1),
              "เกินงบ": q(D(net3) - budget, 0),
              "เปอร์เซ็นต์ทุนรวม": q(D(-net3) / total * 100, 2)}

    # ── ถ้าเข้าที่ 3.8 (ไม้ที่ถูกบล็อก) ──
    e2, stay_x = path[4], path[5]
    stay = q(sets * (e2 - stay_x) - cost, 0)
    assert stay == c["ราคาการพัก"]
    move = x3 - e3
    broke_x = e2 + move
    broke = q(sets * (e2 - broke_x) - cost, 0)
    two = net3 + broke
    if38 = {"เข้า": float(e2),
            "เชือกอยู่": {"ออก": float(stay_x), "สุทธิ": stay, "บัญชีคู่": after + stay},
            "เชือกขาด": {"ขยับ": q(move, 1), "ออก": q(broke_x, 1), "สุทธิ": broke, "บัญชีคู่": after + broke,
                         "สองไม้": two, "สองไม้เปอร์เซ็นต์ทุนรวม": q(D(-two) / total * 100, 2)}}

    # ── beta: ไม้ 3 เป็นฝั่งกลับด้าน ──
    bA, bB = D(str(acct["beta"]["A"])), D(str(acct["beta"]["B"]))
    vA = D(str(pair["จำนวนA"])) * D(str(pair["A"]))          # +1,000 (ฝั่งซื้อ X)
    vB = D(str(pair["จำนวนB"])) * D(str(pair["B"]))          # −1,000
    exp_long = q(bA * vA + bB * vB, 0)                          # +500
    exp_short = -exp_long                                       # ไม้ 3: short A 10 · ซื้อ B 20
    btc_move = D(str(-data["ch08"]["ขาเดียว"]["BTCลงเปอร์เซ็นต์"]))   # 4
    mkt = q(D(exp_short) * btc_move / 100, 0)
    market = {"betaexposureฝั่งซื้อ": exp_long, "betaexposureไม้3": exp_short,
              "BTCขึ้นเปอร์เซ็นต์": int(btc_move), "เสียจากตลาด": mkt,
              "Xขยับเทียบเท่า": q(-D(mkt) / sets, 1)}

    # ── หลายคู่ฝั่งเดียวกัน ──
    npairs = 3
    each = q(D(exp_long) * -btc_move / 100, 0)
    many = {"คู่": npairs, "betaexposureต่อคู่": exp_long, "BTCลงเปอร์เซ็นต์": -int(btc_move),
            "เสียต่อคู่": each, "betaexposureรวม": exp_long * npairs, "เสียรวม": each * npairs,
            "เปอร์เซ็นต์ทุนรวม": q(D(-each * npairs) / total * 100, 2)}

    # ── dist: สามไม้แรกในสองโลกของบท 12 ──
    res = [data["ch12"]["เส้นทาง"][k]["สุทธิ"] for k in ("1", "2", "3")]       # +16 / +2 / −21
    mine = sum(res)                                                            # −3
    dist = {"ผลสามไม้ของมิน": mine}
    for name in ("หลัก", "เทียบ"):
        mix = [D(m) / 100 for m in data["ch12"]["สัดส่วนตอนจบ"][name]["สัดส่วน"]]
        no_hit = (1 - mix[2]) ** 3
        worse = sum(mix[a] * mix[b] * mix[g] for a, b, g in product(range(3), repeat=3)
                    if res[a] + res[b] + res[g] <= mine)
        ev3 = 3 * sum(m * r for m, r in zip(mix, res))
        dist[name] = {"สามไม้ไม่ชนงบเปอร์เซ็นต์": q(no_hit * 100, 2),
                      "มีไม้ชนงบอย่างน้อยหนึ่งเปอร์เซ็นต์": q((1 - no_hit) * 100, 2),
                      "สามไม้ได้ลบ3หรือแย่กว่าเปอร์เซ็นต์": q(worse * 100, 2),
                      "สามไม้ได้ลบ3หรือแย่กว่าปัด": q(worse * 100, 0),
                      "เฉลี่ยสามไม้": q(ev3, 2)}

    # ── ✍️ (ก) เส้นทางใหม่หลังพัก ──
    ex_path = [D("0"), D("2.3"), D("3.0"), D("4.4"), D("3.6"), D("1.0")]
    entry_line = D(str(card["เข้า"]))
    j, why, net = _exit_by_card(ex_path, 1, sets, cost, budget, D(str(card["ออก"])), card["ช่วงถือสูงสุด"])
    assert why == "งบ"
    blocked = [float(x) for x in ex_path[j + 1:] if x >= entry_line]
    miss = q(sets * (ex_path[4] - ex_path[5]) - cost, 0)
    ex_a = {"เส้นทาง": [float(x) for x in ex_path], "เข้า": float(ex_path[1]),
            "ที่3.0": q(sets * (ex_path[1] - ex_path[2]) - cost, 0),
            "ออกที่": float(ex_path[j]), "เหตุออก": why, "สุทธิ": q(net, 0),
            "เส้นงบ": q(ex_path[1] + (-budget - cost) / sets, 1), "เกินงบ": q(net - budget, 0),
            "เปอร์เซ็นต์ทุนรวม": q(-net / total * 100, 2),
            "บล็อก": blocked, "จำนวนบล็อก": len(blocked), "ถ้าเข้า3.6ปิด1.0": miss}

    # ── ✍️ (ค) โซ่มีวันล็อก vs ยางยืด ──
    n9 = data["ch04"]["คืนวันที่9"]
    basis0 = acct["BTC"]["basis"]
    ex_c = {"basisเปิด": basis0, "basisคืนวันที่9": n9["futures"] - n9["spot"],
            "basisกว้างขึ้น": n9["futures"] - n9["spot"] - basis0, "Xก่อน": float(path[2]), "Xหลัง": float(path[3])}

    claims = [
        {"id": "ch14-regime-events",
         "ข้อความ": ("เหตุการณ์ทั่วไปที่ทำให้ความสัมพันธ์ของสองเหรียญเปลี่ยนถาวรหรือนาน: ถูกถอดจาก exchange · "
                     "เครือข่ายถูกเจาะหรือเปลี่ยนกลไก · ฝากถอนถูกระงับ · ปลดล็อกโทเคนก้อนใหญ่ · funding ของขาใดขาหนึ่ง"
                     "อยู่ฝั่งจ่ายนาน — การจดเหตุการณ์เหล่านี้ไว้ก่อนในทะเบียนช่วยให้ตัดสินเร็วขึ้น แต่ข่าวมักมาถึงหลังราคา"
                     "ขยับแล้ว · เล่มไม่อ้างเหตุการณ์จริงใด"),
         "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [14]},
        {"id": "ch14-pairs-break-together",
         "ข้อความ": ("เมื่อตลาดคริปโตร่วงแรง เหรียญส่วนใหญ่ขยับไปทางเดียวกันมากขึ้น คู่ที่ไม่เป็นกลางต่อตลาดหลายคู่"
                     "ฝั่งเดียวกันจึงเสียพร้อมกัน และคนที่ทำงานเดียวกันปิดพร้อมกันทำให้ระยะถ่างก่อนแคบ — การถือหลายคู่"
                     "จึงช่วยน้อยกว่าที่จำนวนคู่บอก · การคุม beta exposure รวมช่วยส่วนตลาด แต่ไม่ช่วยส่วนที่คนแห่ปิด"),
         "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [14]},
    ]
    drills = [
        {"โจทย์": "การ์ดเดิม short X 10 ชุด เส้นทาง 0 → 2.3 → 3.0 → 4.4 → 3.6 → 1.0 · (1) ไม้ปิดที่ไหน ได้เท่าไร "
                  "(2) เกินงบเท่าไร (3) จุดไหนถูกบล็อก (4) ถ้าเข้าที่ 3.6 แล้วปิดที่ 1.0 ได้เท่าไร",
         "คำตอบ": [ex_a["ออกที่"], ex_a["สุทธิ"], ex_a["เกินงบ"], blocked[0], miss]},
        {"โจทย์": "เขียนข้อสรุปแคบของคู่ A–B และเลือกทางจากเมนูห้าทาง เมื่อเพื่อนบอกให้ลบคู่ทิ้ง"},
        {"โจทย์": "ห่างขึ้น = ถูกลง? basis 3,000 → 3,200 (โซ่มีวันล็อก) เทียบ X 2.8 → 4.1 (ยางยืด)",
         "คำตอบ": [ex_c["basisกว้างขึ้น"]]},
    ]
    return {
        "ไม้3": trade3,
        "ถ้าเข้า38": if38,
        "ตลาด": market,
        "หลายคู่": many,
        "dist": dist,
        "แบบฝึกก": ex_a,
        "แบบฝึกค": ex_c,
        "_claims": claims,
        "_แบบฝึก": drills,
    }
