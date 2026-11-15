"""บท 14 — −21 แล้วสัญญาณกลับมาที่ 3.8 · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py)

ทุกค่าคำนวณจาก ch12 / ch14 / ch08 / บัญชีมิน ที่ sab_figures.py สร้างแล้ว — ไม่มีตัวเลขผลลัพธ์ลอย
- ไม้3: สรุปไม้ 3 (short X 10 ชุด เข้า 2.1 ปิด 4.1) · บัญชีคู่ก่อน/หลัง · เส้นงบ · % ของทุนรวม
- ถ้าเข้า38: สองโลกของไม้ที่ถูกบล็อก — เชือกยังอยู่ (3.8 → 2.4 = ราคาการพัก) vs
  เชือกขาด (X ขยับต่อเท่าที่ไม้ 3 ขยับ 2.1 → 4.1 = 2.0 → ปิดที่ 5.8) ⓝ สมมติฐานของบท
- ตลาด: ไม้ 3 เป็นฝั่งกลับด้าน (short A 10 · ซื้อ B 20) beta exposure −500 · BTC +4% → −20 = X ขยับ 2 ต่อ 10 ชุด
- หลายคู่: ถือ 3 คู่ฝั่งเดียวกันที่ +500 ต่อคู่ · BTC −4% → เสียพร้อมกัน
- dist: สัดส่วนตอนจบสองโลกของบท 12 (60/25/15 · 45/20/35) → โอกาสที่สามไม้แรกไม่ชนงบ ·
  โอกาสที่สามไม้รวมกันได้ −3 หรือแย่กว่า (ผลจริงของมิน 16 + 2 − 21) · เฉลี่ยสามไม้
- ค่าถือ: ค่าถือขา short สะสม 3 ไม้ (ช่วงที่ถือ × 3 รอบ × 0.1 · funding +0.01% ทุกรอบ สมมติ) → บัญชีคู่หลังค่าถือ
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


def _v2(data, D, q, old):
    """บท 14 ด้วยฐานต้นทุนเดียว (ch11.v2 · ต้นทุน 2) + ตัวกลางของ 65% (เดิม 62%) · 22% / 51% · 6 ชุด"""
    c = data["ch14"]
    acct = data["บัญชีมิน"]
    card, pair = acct["การ์ด"], acct["คู่"]
    v12 = data["ch12"]["v2"]
    sets = D(str(pair["ชุด"]))
    cost = D(str(data["ch11"]["v2"]["ต้นทุน"]["ไปกลับ"]))
    budget = D(str(card["งบขาดทุนสุทธิ"]))
    total = D(str(acct["กฎ1%"]["ทุนรวมดอลลาร์"]))
    path = [D(str(x)) for x in c["เส้นทาง"]]

    p3 = data["ch12"]["เส้นทาง"]["3"]
    e3, x3 = D(str(p3["Xเข้า"])), D(str(p3["Xออก"]))
    net3 = q(sets * (e3 - x3) - cost, 0)                              # −22
    assert net3 == v12["เส้นทาง"]["3"]["สุทธิ"]
    before = v12["บัญชีคู่หลังไม้2"]                                   # +16
    after = before + net3                                              # −6
    trade3 = {"บัญชีคู่ก่อน": before, "บัญชีคู่หลัง": after, "สุทธิ": net3, "กำไรจากราคา": q(sets * (e3 - x3), 0),
              "เส้นงบ": v12["เส้นขาดทุนถึงงบ"], "เกินงบ": q(budget - D(net3), 0),
              "เปอร์เซ็นต์ทุนรวม": q(D(-net3) / total * 100, 2)}

    # ไม้ที่ถูกบล็อกที่ 3.8: เชือกอยู่ → ปิด 2.4 · เชือกขาด → X ขยับต่อ 2.0 ไปปิด 5.8
    e2, stay_x = path[4], path[5]
    stay = q(sets * (e2 - stay_x) - cost, 0)                          # 12
    move = x3 - e3
    broke_x = e2 + move
    broke = q(sets * (e2 - broke_x) - cost, 0)                        # −22
    two = net3 + broke
    # คุ้มเมื่อ p × ได้ = (1 − p) × เสีย → p = เสีย ÷ (ได้ + เสีย)
    p_need = D(-broke) / D(stay - broke)
    if38 = {"เข้า": float(e2), "เชือกอยู่": {"ออก": float(stay_x), "สุทธิ": stay},
            "เชือกขาด": {"ขยับ": q(move, 1), "ออก": q(broke_x, 1), "สุทธิ": broke, "สองไม้": two,
                         "สองไม้เปอร์เซ็นต์ทุนรวม": q(D(-two) / total * 100, 2)},
            "ได้บวกเสีย": q(D(stay - broke), 0), "ต้องมั่นใจเปอร์เซ็นต์": q(p_need * 100, 0),
            "ต้องมั่นใจทศนิยม": q(p_need * 100, 2),
            "ตรวจ": {"p": q(p_need, 4), "ได้คาด": q(p_need * stay, 2), "เสียคาด": q((1 - p_need) * -broke, 2)}}

    carry = acct["ค่าถือคู่"]
    per, rps = D(str(carry["ต่อรอบ"])), carry["รอบต่อช่วง"]
    held = [data["ch12"]["เส้นทาง"][k]["ช่วงที่ถือ"] for k in ("1", "2", "3")]
    carry_sum = q(per * rps * sum(held), 1)
    carry14 = {"ช่วงสามไม้": sum(held), "สามไม้": carry_sum, "บัญชีคู่หลังค่าถือ": q(D(after) + D(str(carry_sum)), 1)}

    # dist: สามไม้ในสองโลก · โอกาสที่รวมได้ −6 หรือแย่กว่า (ผลจริงของมิน 15 + 1 − 22) · แยกตามชุดผลให้นับเห็น
    res = [v12["เส้นทาง"][k]["สุทธิ"] for k in ("1", "2", "3")]
    mine = sum(res)
    dist = {"ผลสามไม้ของมิน": mine}
    names = {0: "ถึงเส้นออก", 1: "ครบเวลา", 2: "ชนงบ"}
    for name in ("หลัก", "เทียบ"):
        mix = [D(m) / 100 for m in data["ch12"]["สัดส่วนตอนจบ"][name]["สัดส่วน"]]
        groups = {}
        for seq in product(range(3), repeat=3):
            key = tuple(sorted(seq))
            g = groups.setdefault(key, {"ลำดับ": 0, "ต่อลำดับ": D(1), "รวม": sum(res[i] for i in seq)})
            g["ลำดับ"] += 1
            g["ต่อลำดับ"] = mix[seq[0]] * mix[seq[1]] * mix[seq[2]]
        rows = []
        worse = D(0)
        for key, g in sorted(groups.items()):
            if g["รวม"] <= mine:
                pr = g["ต่อลำดับ"] * g["ลำดับ"]
                worse += pr
                rows.append({"ผล": [res[i] for i in key], "ชื่อ": " + ".join(names[i] for i in key),
                             "รวม": g["รวม"], "จำนวนลำดับ": g["ลำดับ"], "โอกาสต่อลำดับเปอร์เซ็นต์": q(g["ต่อลำดับ"] * 100, 4),
                             "โอกาสรวมเปอร์เซ็นต์": q(pr * 100, 2)})
        dist[name] = {"แถวที่นับ": rows, "สามไม้ได้ลบ6หรือแย่กว่าเปอร์เซ็นต์": q(worse * 100, 2),
                      "สามไม้ได้ลบ6หรือแย่กว่าปัด": q(worse * 100, 0),
                      "เฉลี่ยสามไม้": q(3 * sum(m * r for m, r in zip(mix, res)), 2)}
    assert dist["หลัก"]["สามไม้ได้ลบ6หรือแย่กว่าเปอร์เซ็นต์"] == old["หลัก"]["สามไม้ได้ลบ3หรือแย่กว่าเปอร์เซ็นต์"], \
        "ชุดลำดับที่นับต้องเหมือนเดิม (ต้นทุนเลื่อนทุกตอนจบเท่ากัน)"

    # ✍️ (ก) เส้นทางใหม่หลังพัก
    ex_path = [D("0"), D("2.3"), D("3.0"), D("4.4"), D("3.6"), D("1.0")]
    j, why, net = _exit_by_card(ex_path, 1, sets, cost, budget, D(str(card["ออก"])), card["ช่วงถือสูงสุด"])
    assert why == "งบ"
    blocked = [float(x) for x in ex_path[j + 1:] if x >= D(str(card["เข้า"]))]
    ex_a = {"ที่3.0": q(sets * (ex_path[1] - ex_path[2]) - cost, 0), "ออกที่": float(ex_path[j]), "สุทธิ": q(net, 0),
            "เส้นงบ": q(ex_path[1] + (-budget - cost) / sets, 1), "เกินงบ": q(budget - net, 0),
            "บล็อก": blocked, "ถ้าเข้า3.6ปิด1.0": q(sets * (ex_path[4] - ex_path[5]) - cost, 0)}

    return {"ไม้3": trade3, "ถ้าเข้า38": if38, "ราคาการพัก": stay, "ค่าถือ": carry14, "dist": dist,
            "กฎ1ทางรอด": v12["กฎ1"], "แบบฝึกก": ex_a,
            "บัญชีคู่ก่อนค่าถือ": after}


def _ints(o):
    """ค่า float ที่เป็นจำนวนเต็ม → int (พิมพ์ไม่มี .0 · คู่มือข้อ 33)"""
    if isinstance(o, dict):
        return {k: _ints(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_ints(v) for v in o]
    if isinstance(o, float) and o == int(o):
        return int(o)
    return o


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
    before = data["ch12"]["บัญชีคู่หลังไม้2"]          # ต้นทุนการ์ดเดิม 1 (คัมภีร์ใช้ v2 แล้ว · ดู _v2)
    after = before + net3
    assert after == c["บัญชีคู่"], "บัญชีคู่ไม่ตรง ch14"
    trade3 = {"บัญชีคู่ก่อน": before, "บัญชีคู่หลัง": after, "สุทธิ": net3,
              "Xขยับ": q(x3 - e3, 1), "เส้นงบ": q(e3 + (-budget - cost) / sets, 1),
              "เกินงบ": q(budget - D(net3), 0),
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
                         "สองไม้": two, "สองไม้เปอร์เซ็นต์ทุนรวม": q(D(-two) / total * 100, 2)},
            # เข้าที่ 3.8 คุ้มเมื่อโอกาสที่เชือกยังอยู่ p ทำให้ p × 13 − (1 − p) × 21 > 0 → p > 21 ÷ 34
            "ต้องมั่นใจเปอร์เซ็นต์": q(D(-broke) / D(stay - broke) * 100, 0)}

    # ── ค่าถือขา short สะสม 3 ไม้ (funding +0.01% ทุกรอบ · สมมติ) · บัญชีคู่หลังค่าถือ ──
    carry = acct["ค่าถือคู่"]
    per, rps = D(str(carry["ต่อรอบ"])), carry["รอบต่อช่วง"]
    held = [data["ch12"]["เส้นทาง"][k]["ช่วงที่ถือ"] for k in ("1", "2", "3")]
    carry_sum = q(per * rps * sum(held), 1)
    assert carry_sum == q(sum(D(str(data["ch12"]["เส้นทาง"][k]["ค่าถือ"])) for k in ("1", "2", "3")), 1)
    carry14 = {"ต่อรอบ": float(per), "รอบต่อช่วง": rps, "ช่วงสามไม้": sum(held), "รอบสามไม้": rps * sum(held),
               "ไม้3": q(per * rps * held[2], 1), "สามไม้": carry_sum,
               "บัญชีคู่หลังค่าถือ": q(D(after) + D(str(carry_sum)), 1)}

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
            "เส้นงบ": q(ex_path[1] + (-budget - cost) / sets, 1), "เกินงบ": q(budget - net, 0),
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
        {"โจทย์": "การ์ดเดิม short X 10 ชุด เส้นทาง 0 → 2.3 → 3.0 → 4.4 → 3.6 → 1.0 (สมมติเพื่อสอน) · (1) ไม้ปิดที่ไหน "
                  "(2) ได้เท่าไร (3) จุดไหนถูกบล็อก (4) ถ้าเข้าที่ 3.6 แล้วนับผลที่ 1.0 (คิดเหมือนปิดตอนนั้น) ได้เท่าไร",
         "คำตอบ": [ex_a["ออกที่"], ex_a["สุทธิ"], blocked[0], miss]},
        {"โจทย์": "เขียนข้อสรุปแคบของคู่ A–B และเลือกทางจากเมนูห้าทาง เมื่อเพื่อนบอกให้ลบคู่ทิ้ง"},
        {"โจทย์": "ห่างขึ้น = ถูกลง? basis 3,000 → 3,200 (โซ่มีวันล็อก) เทียบ X 2.8 → 4.1 (ยางยืด)",
         "คำตอบ": [ex_c["basisกว้างขึ้น"]]},
    ]
    v2 = _ints(_v2(data, D, q, dist))
    ex2 = v2["แบบฝึกก"]
    drills[0] = {"โจทย์": "การ์ดเดิม (ต้นทุน 2) short X 10 ชุด เส้นทาง 0 → 2.3 → 3.0 → 4.4 → 3.6 → 1.0 (สมมติเพื่อสอน) · "
                          "(1) ไม้ปิดที่ไหน (2) ได้เท่าไร (3) จุดไหนถูกบล็อก (4) ถ้าเข้าที่ 3.6 แล้วนับผลที่ 1.0 ได้เท่าไร",
                 "คำตอบ": [ex2["ออกที่"], ex2["สุทธิ"], ex2["บล็อก"][0], ex2["ถ้าเข้า3.6ปิด1.0"]]}
    return {
        "v2": v2,
        "ไม้3": trade3,
        "ถ้าเข้า38": if38,
        "ค่าถือ": carry14,
        "ตลาด": market,
        "หลายคู่": many,
        "dist": dist,
        "แบบฝึกก": ex_a,
        "แบบฝึกค": ex_c,
        "_claims": claims,
        "_แบบฝึก": drills,
    }
