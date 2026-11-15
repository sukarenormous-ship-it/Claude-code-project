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


def _v2teach(data, D, q):
    """ผลกลางทางที่บท 17 v2 เขียนให้เห็นบนหน้า (ทุกตัวคิดจากค่าของบทก่อน หรือเป็นตัวเลขตั้งโจทย์ 🔢 ที่บอกไว้)"""
    v12 = data["ch12"]["v2"]
    r15, r1, r22 = (v12["เส้นทาง"][k]["สุทธิ"] for k in ("1", "2", "3"))
    cost = D(str(v12["ต้นทุน"]["ไปกลับ"]))                 # 2 ต่อไปกลับ (ch11.v2)
    entry = D(str(v12["หน้า"]["ไทม์ไลน์"]["Xเห็น"]))      # 2.1
    sets = D(10)
    out = {}

    # ── ก·2 รอบชดเชยของ carry: ตรวจด้วยการคูณกลับ ──
    gain = D(str(data["ch06"]["รอบชดเชย"]["กำไรต่อรอบ"]))
    big, small = D(str(data["บัญชีมิน"]["ทุนภาค1"]["รวม"])), D(str(data["ch06"]["เงินบนexchangeถ้าspotอยู่นอก"]))
    out["carryตรวจ"] = {"สี่สิบสี่รอบ": q(gain * 44, 0), "เก้ารอบ": q(gain * 9, 0), "แปดรอบ": q(gain * 8, 0),
                        "ต้องชนะ125000": q(big / (gain + big) * 100, 2), "รวมได้เสีย125000": q(gain + big, 0),
                        "ต้องชนะ25000": q(small / (gain + small) * 100, 2), "รวมได้เสีย25000": q(gain + small, 0)}

    # ── ก·2 ให้ Liquidity ที่ขนาดสอน 1 BTC (บท 1 v2 · บท 2 v2: ส่วนต่าง 20 · ได้ขาเดียว −40) ──
    lp = data["ch01"]["v2"]["ได้ขาเดียว"]
    g4, l4 = D(str(lp["ได้สองฝั่ง"])), -D(str(lp["ได้ขาเดียว"]))
    out["บัตร4"] = {"ได้สองฝั่ง": q(g4, 0), "ได้ขาเดียว": -q(l4, 0), "ต้องได้สองฝั่งต่อขาเดียว": q(l4 / g4, 2),
                    "ต้องชนะเปอร์เซ็นต์": q(l4 / (g4 + l4) * 100, 2), "ได้บวกเสีย": q(g4 + l4, 0)}
    concept = data["ch02"]["แถบผลแนวคิด"]["ให้สภาพคล่อง"]
    seq = [q(g4, 0) if v > 0 else -q(l4, 0) for v in concept]
    out["แกลเลอรีสภาพคล่อง"] = {"ลำดับ": seq, "รวม": sum(seq), "ครั้ง": len(seq)}

    # ── ก·2 ตารางรอบชดเชย: คู่ (บท 12) ──
    out["คู่ได้บวกเสีย"] = q(D(r15) - D(r22), 0)            # 15 + 22 = 37

    # ── ก·3 Win Rate กับ Expected Value ──
    tail = data["ch02"]["หางหนึ่งเปอร์เซ็นต์"]
    w, l = D(str(tail["ได้"])), D(str(tail["เสีย"]))
    out["ชนะ99"] = {"ส่วนชนะ": q(D("0.99") * w, 2), "ส่วนแพ้": q(D("0.01") * l, 2),
                    "รวม": q(D("0.99") * w + D("0.01") * l, 2), "ร้อยรอบได้": q(99 * w, 0), "ร้อยรอบเสีย": q(l, 0),
                    "ร้อยรอบรวม": q(99 * w + l, 0)}
    mix = {}
    for name in ("หลัก", "เทียบ"):
        p = v12["ค่าคาดหมาย100ไม้"][name]
        s = p["สัดส่วน"]
        mix[name] = {"อัตราชนะ": s[0] + s[1], "ส่วน": p["ส่วนต่อไม้"], "ต่อไม้": p["ต่อไม้"],
                     "ส่วนบวก": q(sum(D(str(x)) for x in p["ส่วนต่อไม้"][:2]), 2)}
    out["อัตราชนะการ์ด"] = mix

    # ── ข·1 ใครจ่าย: ตัวเลขต่อหน่วยของแต่ละใบ ──
    fx = data["บัญชีมิน"]["funding"]
    out["ใครจ่าย"] = {"basisต่อปีเปอร์เซ็นต์": data["ch03"]["simpleบนจอ"],
                      "fundingต่อรอบ": data["ch00"]["funding_short1BTCต่อรอบ"],
                      "fundingต่อรอบเปอร์เซ็นต์": fx["ต่อรอบเปอร์เซ็นต์"],
                      "คู่จากราคา": q(sets * (entry - D(str(v12["เส้นทาง"]["1"]["Xออก"]))), 0), "คู่สุทธิ": r15,
                      "ส่วนต่างสภาพคล่อง": q(g4, 0)}

    # ── ข·2 Crowded Unwind (🔢 เหตุการณ์ตั้งโจทย์): คนถือ short X เหมือนกันถูกบังคับปิดพร้อมกัน ──
    budget_x = D(str(v12["เส้นขาดทุนถึงงบ"]))              # 3.4
    jam = D(str(v12["เส้นทาง"]["4"]["Xออก"]))              # 3.7 · วันเดียวจาก 2.1 (ใช้ระดับเดียวกับเส้นทาง 4 ของบท 12)
    back = D(str(v12["เส้นทาง"]["1"]["Xออก"]))             # 0.4 · กลับหลังแรงปิดหมด
    price_jam = sets * (entry - jam)
    net_jam = price_jam - cost
    assert q(net_jam, 0) == v12["เส้นทาง"]["4"]["สุทธิ"]
    out["แห่ปิด"] = {"เข้า": float(entry), "เส้นงบ": float(budget_x), "Xวันแห่": float(jam), "Xหลังแห่": float(back),
                     "ถ่าง": q(jam - entry, 1), "เกินเส้นงบ": q(jam - budget_x, 1),
                     "กำไรจากราคา": q(price_jam, 0), "สุทธิถ้าปิด": q(net_jam, 0), "สุทธิถ้ารอด": r15,
                     "ต่าง": q(D(r15) - net_jam, 0)}

    # ── ข·3 Crowding ของ funding carry: อัตราเหลือครึ่ง (บท 7) ──
    half = data["ch07"]["แย่งหลังhurdle"][1]
    fee = D(str(data["ch07"]["ค่าธรรมเนียมเปิดปิด"]["maker"]))
    net = D(str(half["fundingรวม"])) - fee
    yr = net * 365 / 30
    out["fundingแย่ง"] = {"fundingรวม": half["fundingรวม"], "ค่าธรรมเนียม": int(fee), "สุทธิ": q(net, 0),
                          "ต่อปี": q(yr, 2), "ต่อทุนเปอร์เซ็นต์": q(yr / big * 100, 2),
                          "ส่วนเกินเปอร์เซ็นต์": half["ส่วนเกินmakerเปอร์เซ็นต์"]}
    assert q(yr / big * 100 - 4, 2) == half["ส่วนเกินmakerเปอร์เซ็นต์"]

    # ── ข·3 ต้นทุน taker ไปกลับ 200 กับ 240 (บท 1 · บท 7) ──
    fees = D(str(data["ch07"]["ค่าธรรมเนียมเปิดปิด"]["taker"]))       # 200 = 4 × 50
    gap = D(4) * D(str(data["ch01"]["v2"]["ครึ่งช่องว่าง"]))           # 40 = 4 × 10
    rt = fees + gap
    assert int(rt) == data["ch17"]["ต้นทุนสองขาเป็นรอบfunding"]["ต้นทุน"]
    rounds = rt / D(str(data["ch00"]["funding_short1BTCต่อรอบ"]))
    out["ต้นทุนtaker"] = {"ค่าธรรมเนียม": int(fees), "ต่อครั้ง": q(fees / 4, 0), "ช่องว่าง": int(gap),
                         "ครึ่งช่องว่าง": data["ch01"]["v2"]["ครึ่งช่องว่าง"], "รวม": int(rt), "รอบfunding": q(rounds, 0),
                         "ชั่วโมง": q(rounds * 8, 0), "วัน": q(rounds * 8 / 24, 0)}

    # ── ข·3 Capacity (บท 16 v2): เดิน Order Book ที่ขาละ 5,000 และ 20,000 ──
    cap = {r["ขนาดต่อขา"]: r for r in data["ch16"]["v2"]["capacity"]["ตาราง"]}
    out["capacityเดิน"] = {str(s): {"เท่าของ1000": q(D(s) / 1000, 0), "การ์ด": cap[s]["การ์ด_หลัก"],
                                     "ชั้น": [r["เสีย"] for r in cap[s]["ชั้นที่กิน"]], "เสียต่อfill": cap[s]["เสียต่อfill"],
                                     "เสียสี่fill": cap[s]["เสียสี่fill"], "ต่อไม้": cap[s]["ต่อไม้_หลัก"]}
                           for s in (1000, 5000, 20000)}

    return out


def _dd_walk(curve, lo, hi):
    """แถวทีละไม้ของยอดสะสม: ไม้ · ผล · ยอดสะสม · ยอดสูงสุดที่เคยถึง · ห่างจากยอด"""
    eq = [0] + list(curve)
    rows, peak = [], 0
    for i in range(1, len(eq)):
        peak = max(peak, eq[i])
        if lo <= i <= hi:
            rows.append({"ไม้": i, "ผล": eq[i] - eq[i - 1], "ก่อน": eq[i - 1], "ยอดสะสม": eq[i], "ยอดสูงสุด": peak,
                         "ห่าง": eq[i] - peak})
    return rows


def _two_jobs():
    """🔢 เงินก้อนเดียว สองงาน สองเพดาน (ตัวเลขตั้งโจทย์ · ไม่ต่อกับบัญชีของมิน)"""
    money, cap1 = 1000, 600
    pair = {"เงินต่อหน่วย": 400, "อยู่แห่งที่1": 400, "คาดได้": 4}
    fund = {"เงินต่อหน่วย": 300, "อยู่แห่งที่1": 200, "คาดได้": 3}
    alone = {"คู่": min(money // pair["เงินต่อหน่วย"], cap1 // pair["อยู่แห่งที่1"]),
             "funding": min(money // fund["เงินต่อหน่วย"], cap1 // fund["อยู่แห่งที่1"])}
    rows = []
    for a in range(0, alone["คู่"] + 1):
        for b in range(0, alone["funding"] + 1):
            m = a * pair["เงินต่อหน่วย"] + b * fund["เงินต่อหน่วย"]
            e1 = a * pair["อยู่แห่งที่1"] + b * fund["อยู่แห่งที่1"]
            rows.append({"คู่": a, "funding": b, "เงิน": m, "แห่งที่1": e1, "คาดได้": a * pair["คาดได้"] + b * fund["คาดได้"],
                         "ผ่านเงิน": m <= money, "ผ่านแห่งที่1": e1 <= cap1})
    ok = [r for r in rows if r["ผ่านเงิน"] and r["ผ่านแห่งที่1"]]
    best = max(ok, key=lambda r: r["คาดได้"])
    both = next(r for r in rows if r["คู่"] == alone["คู่"] and r["funding"] == alone["funding"])
    return {"เพดานเงิน": money, "เพดานแห่งที่1": cap1, "คู่": pair, "funding": fund, "ทีละใบ": alone,
            "ใส่เต็มทั้งสอง": both, "แถว": rows, "ดีสุด": best, "แถวผ่าน": len(ok),
            "คู่หารเงิน": money // pair["เงินต่อหน่วย"], "คู่หารแห่งที่1": cap1 // pair["อยู่แห่งที่1"],
            "fundingหารเงิน": money // fund["เงินต่อหน่วย"], "fundingหารแห่งที่1": cap1 // fund["อยู่แห่งที่1"]}


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
    extra = _v2teach(data, D, q)
    curve = v2["drawdown"]["กราฟ"]
    p = v2["drawdown"]
    extra["drawdownเดิน"] = {"หกไม้แรก": _dd_walk(curve, 1, 6),
                             "ช่วงลึกสุด": _dd_walk(curve, p["ไม้ยอด"], p["ไม้กลับยอด"]),
                             "ลึกสุดคิด": p["ต่ำสุด"] - p["ยอด"],
                             "ไม้ใต้ยอดแรก": p["ไม้ยอด"] + 1, "ไม้ใต้ยอดสุดท้าย": p["ไม้กลับยอด"] - 1}
    assert extra["drawdownเดิน"]["ลึกสุดคิด"] == p["ตัวอย่าง"]["ลึกสุด"]
    assert p["ไม้กลับยอด"] - 1 - p["ไม้ยอด"] == p["ตัวอย่าง"]["นานสุดไม้"]
    ev = D(str(v2["ค่าคาดหมายการ์ด"]["หลัก"]))
    extra["drawdownเดิน"]["ลึกสุดหารไม้เฉลี่ย"] = q(D(-p["ตัวอย่าง"]["ลึกสุด"]) / ev, 2)
    extra["drawdownเดิน"]["ไม้80ห่าง"] = next(r["ห่าง"] for r in extra["drawdownเดิน"]["ช่วงลึกสุด"] if r["ไม้"] == 80)
    extra["drawdownเดิน"]["ไม้80ยอด"] = next(r["ยอดสะสม"] for r in extra["drawdownเดิน"]["ช่วงลึกสุด"] if r["ไม้"] == 80)
    extra["สองงาน"] = _two_jobs()
    v2.update(_ints(extra))

    # ── แบบฝึก v2 (5 ข้อ · 🔢 ตั้งโจทย์จากการ์ดเดิม) ──
    g15, g22 = v2["ต้องชนะคู่"]["ได้"], v2["ต้องชนะคู่"]["เสีย"]
    one = data["ch12"]["v2"]["เส้นทาง"]["2"]["สุทธิ"]
    seq1 = [g15, g15, g22, one, g22, g15, g15, g15]
    w1 = _dd_walk([sum(seq1[:i + 1]) for i in range(len(seq1))], 1, len(seq1))
    deep1 = min(r["ห่าง"] for r in w1)
    longest1, cur = 0, 0
    for r in w1:
        cur = cur + 1 if r["ห่าง"] < 0 else 0
        longest1 = max(longest1, cur)
    c4 = data["ch12"]["v2"]["หน้า"]["สามต้นทุน"]["4"]
    s4 = c4["สามตอนจบ"]
    ev4 = q(D("0.6") * s4[0] + D("0.25") * s4[1] + D("0.15") * s4[2], 2)
    assert ev4 == c4["ค่าคาดหมาย"]
    total = D(str(acct["กฎ1%"]["ทุนรวมดอลลาร์"]))
    v2["แบบฝึก"] = _ints({
        "ลำดับแปดไม้": {"ลำดับ": seq1, "แถว": w1, "ลึกสุด": deep1, "นานสุด": longest1, "รวม": sum(seq1)},
        "ต้นทุน4": {"สามตอนจบ": s4, "ต้องชนะ": c4["ต้องชนะ"], "ส่วน": [q(D("0.6") * s4[0], 2), q(D("0.25") * s4[1], 2),
                                                                     q(D("0.15") * s4[2], 2)], "ค่าคาดหมาย": ev4,
                    "ช่วงรวม": c4["ช่วงรวม"]},
        "ลึก60": {"ลึก": -60, "เปอร์เซ็นต์ทุนรวม": q(D(60) / total * 100, 2), "ลึก60หารไม้เฉลี่ย": q(D(60) / ev, 1)},
    })
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
            {"โจทย์": "ลำดับแปดไม้ +15 +15 −22 +1 −22 +15 +15 +15 ของการ์ดคู่: Drawdown ลึกสุดเท่าไร",
             "คำตอบ": float(v2["แบบฝึก"]["ลำดับแปดไม้"]["ลึกสุด"])},
            {"โจทย์": "carry รอบละ 1,500 ต้องกี่รอบจึงคืนเงินบน exchange 25,000", "คำตอบ": float(ex1)},
            {"โจทย์": "การ์ดคู่จ่ายต้นทุนไปกลับ 4 แทน 2 (+13 / −1 / −24) ส่วนผสม 60/25/15 ได้ Expected Value ต่อไม้เท่าไร",
             "คำตอบ": float(v2["แบบฝึก"]["ต้นทุน4"]["ค่าคาดหมาย"])},
            {"โจทย์": "drawdown −60 ใน 100 ไม้ของการ์ดคู่: เลิก ถือต่อ หรือเพิ่มขนาด"},
            {"โจทย์": "grid bot ได้ขั้นละ 2 เสีย 50 เมื่อหลุดกรอบ ต้องชนะกี่ครั้งคืนการแพ้หนึ่งครั้ง",
             "คำตอบ": float(grid["ชนะคืนหนึ่งแพ้"])},
        ],
    }
