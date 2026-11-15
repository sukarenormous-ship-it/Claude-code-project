"""บท 17 — ธรรมชาติของ stat arb: ใครจ่ายเงินให้เรา · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py)

ทุกค่าคำนวณจาก ch01 / ch02 / ch06 / ch07 / ch12 / ch16 / ch17 / ch18 / บัญชีมิน ที่ sab_figures.py สร้างแล้ว
- แกลเลอรี: แถบผลสี่กลยุทธ์ (★ sab-shape-gallery)
    carry   = ลำดับแนวคิดของบท 2 (carry) แทน +1 ด้วยกำไรสุทธิรอบละ 2,846 (บท 6) และไม้เสียด้วย
              เงินบน exchange 25,000 (เก็บ spot นอก exchange · บท 6) — 20 รอบ 90 วัน
    funding = funding รายรอบของเส้นทาง "กลับขั้ว" (บท 7) = ผลต่างของยอดสะสม 90 รอบ
    คู่     = ลำดับ 20 ไม้ของการ์ดบท 12 (โลก 60/25/15)
    สภาพคล่อง = ลำดับแนวคิดของบท 2 (ให้สภาพคล่อง) แทนไม้ได้ด้วย +0.2 (ได้สองฝั่ง · บท 1) และไม้เสียด้วย −0.4 (ได้ขาเดียว)
- ต้องชนะ: ต่อกลยุทธ์ "ชนะกี่ครั้งคืนการแพ้หนึ่งครั้ง" = |เสีย| ÷ ได้ และอัตราชนะที่ต้องได้ = |เสีย| ÷ (ได้ + |เสีย|)
- drawdown: ตำแหน่งยอดก่อนลึกสุด / จุดต่ำสุด / ไม้ที่กลับยอดเดิม จากลำดับ 100 ไม้ (ch17.drawdown.กราฟ)
  นานสุด = จำนวนไม้ที่อยู่ใต้ยอดเดิม (ตรวจกับค่าที่ sab_figures.py คำนวณไว้)
- คู่ส่วนเกิน: บัญชีคู่ตามกลยุทธ์ −6 บนทุนคู่ 1,000 (ยังไม่หัก hurdle)
- บัตร4: ร่างบัตรให้สภาพคล่องจากตัวอย่างบท 1 (ได้สองฝั่ง 0.2 · ได้ขาเดียว −0.4)
- แบบฝึก (ตัวเลขตั้งโจทย์ 🔢 สมมติเพื่อสอน): carry รอบละ 1,500 เทียบเงินบน exchange 25,000 ·
  grid bot ได้ขั้นละ 2 เสีย 50 เมื่อราคาหลุดกรอบ
"""


def _need(D, q, gain, loss, cost=0):
    g, l = D(str(gain)) - D(str(cost)), -D(str(loss)) + D(str(cost))
    k = q(l / g, 2)
    out = {"ได้": gain, "เสีย": loss, "ชนะคืนหนึ่งแพ้": int(k) if k == int(k) else k,
           "ต้องชนะเปอร์เซ็นต์": q(l / (g + l) * 100, 2)}
    if cost:                                            # ตารางแสดงค่าหลังหักต้นทุน ให้ เสีย ÷ ได้ คิดซ้ำได้จากตาราง
        out["ได้สุทธิ"], out["เสียสุทธิ"] = float(q(g, 2)), float(q(-l, 2))
    return out


def _drawdown(seed, outcomes, trades=100):
    """สำเนาตรรกะ drawdown ของ sab_figures.py (ลำดับสุ่มเดียวกัน) ที่รับผลสามแบบเป็นตัวแปร"""
    import random
    rng = random.Random(seed)
    win, mid, lose = outcomes
    seq = []
    for _ in range(trades):
        u = rng.random()
        seq.append(win if u < 0.60 else mid if u < 0.85 else lose)
    cum, peak, deepest, longest, cur = 0, 0, 0, 0, 0
    curve = []
    for x in seq:
        cum += x
        curve.append(cum)
        if cum >= peak:
            peak, cur = cum, 0
        else:
            cur += 1
            deepest = max(deepest, peak - cum)
            longest = max(longest, cur)
    return {"ลึกสุด": -deepest, "นานสุดไม้": longest, "ผลรวม100ไม้": cum,
            "ไม้บวก": sum(1 for x in seq if x > 0), "ไม้ชนงบ": sum(1 for x in seq if x == lose), "กราฟ": curve}


def _v2(data, D, q):
    """บท 17 ด้วยฐานต้นทุนเดียว (ch11.v2 · การ์ด +15 / +1 / −22) — ลำดับสุ่มของ drawdown เดิม (seed 20261111 · 1–30)"""
    import statistics
    v12 = data["ch12"]["v2"]
    res = tuple(v12["เส้นทาง"][k]["สุทธิ"] for k in ("1", "2", "3"))
    need = _need(D, q, res[0], res[2])
    seed = int(data["บัญชีมิน"]["seed"]["บท13"])
    ex = _drawdown(seed, res)
    old = _drawdown(seed, (16, 2, -21))
    assert old["ลึกสุด"] == data["ch17"]["drawdown"]["ตัวอย่าง"]["ลึกสุด"], "ลำดับสุ่มไม่ตรง drawdown เดิม"
    many = [_drawdown(sd, res) for sd in range(1, 31)]

    def summ(vals):
        return {"มัธยฐาน": q(D(str(statistics.median(vals))), 0), "ต่ำสุด": min(vals), "สูงสุด": max(vals)}
    eq = [0] + ex["กราฟ"]
    peak, pi, worst, uw, longest = eq[0], 0, (0, 0, 0), None, (0, 0, 0)
    for i, v in enumerate(eq):
        if v >= peak:
            if uw is not None and i - uw - 1 > longest[0]:
                longest = (i - uw - 1, uw, i)
            peak, pi, uw = v, i, None
        else:
            uw = pi if uw is None else uw
            if v - peak < worst[0]:
                worst = (v - peak, pi, i)
    assert worst[0] == ex["ลึกสุด"]
    ev = D(str(v12["สัดส่วนตอนจบ"]["หลัก"]["ค่าคาดหมาย"]))
    total = D(str(data["บัญชีมิน"]["กฎ1%"]["ทุนรวมดอลลาร์"]))
    med_deep = summ([d["ลึกสุด"] for d in many])
    dd = {"ตัวอย่าง": {k: v for k, v in ex.items() if k != "กราฟ"}, "กราฟ": ex["กราฟ"],
          "ไม้ยอด": worst[1], "ยอด": eq[worst[1]], "ไม้ต่ำสุด": worst[2], "ต่ำสุด": eq[worst[2]],
          "ไม้กลับยอด": longest[2] if longest[0] else None,
          "ลึกสุดเป็นไม้เฉลี่ย": q(D(-worst[0]) / ev, 1), "ลึกสุดเปอร์เซ็นต์ทุนรวม": q(D(-worst[0]) / total * 100, 2),
          "สามสิบชุด": {"ลึกสุด": med_deep, "นานสุดไม้": summ([d["นานสุดไม้"] for d in many]),
                        "ผลรวม100ไม้": summ([d["ผลรวม100ไม้"] for d in many]),
                        "จบบวก": sum(1 for d in many if d["ผลรวม100ไม้"] > 0)},
          "มัธยฐานเปอร์เซ็นต์ทุนรวม": q(D(-med_deep["มัธยฐาน"]) / total * 100, 2)}
    cap = data["ch16"]["v2"]["capacity"]
    return {"ต้องชนะคู่": need, "drawdown": dd, "ค่าคาดหมายการ์ด": {"หลัก": float(ev), "เทียบ": v12["สัดส่วนตอนจบ"]["เทียบ"]["ค่าคาดหมาย"]},
            "capacity": {"ที่1000": cap["ต่อรอบ"][0], "สูงสุด": cap["สูงสุด"], "ที่20000": cap["ต่อรอบ"][3]},
            "แถบผลคู่": v12["แถบผล"]["หลัก"]}


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
    acct = data["บัญชีมิน"]
    c17 = data["ch17"]

    # ── แกลเลอรีแถบผล ──
    r6 = data["ch06"]["รอบชดเชย"]
    gain6 = r6["กำไรต่อรอบ"]
    small = data["ch06"]["เงินบนexchangeถ้าspotอยู่นอก"]
    concept = data["ch02"]["แถบผลแนวคิด"]
    carry = [gain6 if v > 0 else -small for v in concept["carry"]]
    flip = data["ch07"]["กราฟ"]["กลับขั้ว"]
    funding = [q(D(str(flip[0])), 0)] + [q(D(str(flip[i])) - D(str(flip[i - 1])), 0) for i in range(1, len(flip))]
    pair = data["ch12"]["แถบผล"]["หลัก"]["ลำดับ"]
    lp = data["ch01"]["ได้ขาเดียว"]
    liq = [lp["ได้สองฝั่ง"] if v > 0 else lp["ได้ขาเดียว"] for v in concept["ให้สภาพคล่อง"]]
    gallery = {
        "carry": {"ลำดับ": carry, "รวม": sum(carry), "รอบ": len(carry), "เสีย": -small},
        "funding": {"ลำดับ": funding, "รวม": sum(funding), "รอบ": len(funding),
                    "รอบบวก": sum(1 for v in funding if v > 0), "รอบลบ": sum(1 for v in funding if v < 0)},
        "คู่": {"ลำดับ": pair, "รวม": sum(pair), "ไม้": len(pair)},
        "สภาพคล่อง": {"ลำดับ": liq, "รวม": float(q(sum(D(str(v)) for v in liq), 2)), "ครั้ง": len(liq)},
    }
    assert gallery["คู่"]["รวม"] == data["ch12"]["แถบผล"]["หลัก"]["รวม"]
    assert gallery["funding"]["รวม"] == data["ch07"]["สี่เส้นทาง"]["กลับขั้ว"]["fundingรวม"]

    # ── ต้องชนะกี่ครั้งคืนการแพ้หนึ่งครั้ง ──
    tail = data["ch02"]["หางหนึ่งเปอร์เซ็นต์"]
    bot = data["ch18"]["บอทชนะ65"]
    path = data["ch12"]["เส้นทาง"]
    need = {
        "carry": _need(D, q, gain6, -acct["ทุนภาค1"]["รวม"]),
        "carryเฉพาะexchange": _need(D, q, gain6, -small),
        "หาง99": _need(D, q, tail["ได้"], tail["เสีย"]),
        "บอท65": _need(D, q, bot["ได้"], bot["เสีย"], bot["ต้นทุน"]),
        "คู่": _need(D, q, path["1"]["สุทธิ"], path["3"]["สุทธิ"]),
        "สภาพคล่อง": _need(D, q, lp["ได้สองฝั่ง"], lp["ได้ขาเดียว"]),
    }
    assert need["carry"]["ชนะคืนหนึ่งแพ้"] == r6["เสียทั้ง125000_ทศนิยม"]
    assert q(D(str(need["carryเฉพาะexchange"]["ชนะคืนหนึ่งแพ้"])), 1) == r6["เสียเฉพาะ25000"]
    assert need["บอท65"]["ต้องชนะเปอร์เซ็นต์"] == bot["คุ้มทุนเปอร์เซ็นต์"]
    assert q(D(str(need["คู่"]["ต้องชนะเปอร์เซ็นต์"])), 0) == c17["ต้องชนะคู่"]

    # ── drawdown: ตำแหน่งบนกราฟ ──
    eq = [0] + c17["drawdown"]["กราฟ"]
    peak, pi, worst, uw, longest = eq[0], 0, (0, 0, 0), None, (0, 0, 0)
    for i, v in enumerate(eq):
        if v >= peak:
            if uw is not None and i - uw - 1 > longest[0]:
                longest = (i - uw - 1, uw, i)
            peak, pi, uw = v, i, None
        else:
            uw = pi if uw is None else uw
            if v - peak < worst[0]:
                worst = (v - peak, pi, i)
    ex = c17["drawdown"]["ตัวอย่าง"]
    assert worst[0] == ex["ลึกสุด"] and longest[0] == ex["นานสุดไม้"]
    ev = D(str(data["ch12"]["สัดส่วนตอนจบ"]["หลัก"]["ค่าคาดหมาย"]))
    total = D(str(acct["กฎ1%"]["ทุนรวมดอลลาร์"]))
    dd = {"ไม้ยอด": worst[1], "ยอด": eq[worst[1]], "ไม้ต่ำสุด": worst[2], "ต่ำสุด": eq[worst[2]],
          "ไม้กลับยอด": longest[2], "ลึกสุดเป็นไม้เฉลี่ย": q(D(-worst[0]) / ev, 1),
          "ลึกสุดเปอร์เซ็นต์ทุนรวม": q(D(-worst[0]) / total * 100, 2),
          "มัธยฐานเปอร์เซ็นต์ทุนรวม": q(D(-data["seed_robustness"]["ch17"]["ลึกสุด"]["มัธยฐาน"]) / total * 100, 2)}

    # ── คู่: ผลจริงเทียบทุน (ก่อน hurdle) ──
    real = c17["คู่ตามกลยุทธ์"]
    cap = acct["คู่"]["ทุนคู่"]
    pair_x = {"ผลจริง": real, "ทุน": cap, "เปอร์เซ็นต์": q(D(real) / D(cap) * 100, 1)}

    # ── บัตร 4 (ร่าง) ──
    card4 = {"ได้สองฝั่ง": lp["ได้สองฝั่ง"], "ได้ขาเดียว": lp["ได้ขาเดียว"],
             "ต้องได้สองฝั่งต่อขาเดียว": need["สภาพคล่อง"]["ชนะคืนหนึ่งแพ้"],
             "ต้องชนะเปอร์เซ็นต์": need["สภาพคล่อง"]["ต้องชนะเปอร์เซ็นต์"]}

    # ── แบบฝึก ──
    g_new = D("1500")                                   # 🔢 กำไรสุทธิต่อรอบเมื่อ basis หด (ตั้งโจทย์)
    ex1 = q(D(small) / g_new, 2)
    grid_gain, grid_loss = D("2"), D("-50")             # 🔢 grid bot ตั้งโจทย์
    grid = _need(D, q, int(grid_gain), int(grid_loss))
    grid["ชนะ90ค่าคาดหมาย"] = q(D("0.9") * grid_gain + D("0.1") * grid_loss, 2)
    drill = {"carry1500": {"กำไรต่อรอบ": int(g_new), "เสีย": -small, "รอบ": ex1, "ปี": q(ex1 / 4, 1)}, "grid": grid}

    v2 = _ints(_v2(data, D, q))
    return {
        "v2": v2,
        "แกลเลอรี": gallery,
        "ต้องชนะ": need,
        "drawdownจุด": dd,
        "คู่ผลต่อทุน": pair_x,
        "บัตร4": card4,
        "แบบฝึก": drill,
        "_claims": [
            {"id": "ch17-who-pays-map",
             "ข้อความ": "ผู้จ่ายของกลยุทธ์ในเล่มเป็นสมมติฐาน: carry และ funding carry ได้จากฝั่ง long ที่ยอมจ่ายเพื่อถือ BTC "
                        "ด้วยเงินน้อย (คนเร่ง) · คู่ที่มีเชือกได้จากคนที่ต้องซื้อขายทันที (คนรีบ) · การให้สภาพคล่องได้ส่วนต่างราคาซื้อ-ขาย"
                        "จากคนที่กดซื้อขายทันที · ทุกแบบเสียให้คนที่รู้ข่าวก่อน (คนรู้) และเสียพร้อมกันเมื่อคนทำงานเดียวกันออกพร้อมกัน "
                        "— เล่มไม่ได้วัดสัดส่วนผู้จ่ายจริงในตลาดใด",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [17]},
            {"id": "ch17-crowded-unwind",
             "ข้อความ": "เมื่อคนจำนวนมากถือสถานะเดียวกันแล้วต้องออกพร้อมกัน (ขาดทุนถึงเพดาน · ถูกเรียกหลักประกัน · กติกาเปลี่ยน) "
                        "แรงปิดฝั่งเดียวกันทำให้ระยะที่ควรแคบถ่างออกก่อน แล้วจึงแคบเมื่อแรงปิดหมด · คนที่ทุนน้อยหรือ leverage สูง"
                        "มักถูกบังคับออกที่จุดถ่างสุด — เล่มไม่อ้างเหตุการณ์จริงใด และไม่มีตัวเลขวัดขนาดของแรงนี้",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [17]},
        ],
        "_แบบฝึก": [
            {"โจทย์": "carry รอบละ 1,500 ต้องกี่รอบจึงคืนเงินบน exchange 25,000", "คำตอบ": float(ex1)},
            {"โจทย์": "drawdown −60 ใน 100 ไม้ของการ์ดคู่: เลิก ถือต่อ หรือเพิ่มขนาด"},
            {"โจทย์": "grid bot ได้ขั้นละ 2 เสีย 50 เมื่อหลุดกรอบ ต้องชนะกี่ครั้งคืนการแพ้หนึ่งครั้ง",
             "คำตอบ": float(grid["ชนะคืนหนึ่งแพ้"])},
        ],
    }
