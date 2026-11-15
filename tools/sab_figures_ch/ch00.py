"""บท 0 — ส่วนต่าง 3,000 บนหน้าจอ · ค่าใหม่ที่บทใช้ (ตาราง ±0.1 BTC · แว่นขยาย ×100 · funding ฉบับสั้น · ใบ 00 · ✍️)

ทุกค่าคำนวณจาก บัญชีมิน / ch00 เดิม หรือจากตัวเลขโจทย์ที่ประกาศในบท (🔢 สมมติเพื่อสอน)

v2 (แผน 14 · บทย้ายเป็นแม่แบบ v2): คีย์ "v2" เก็บผลกลางทางที่บทแสดงการคิด (1 BTC ตลอดบท) —
ตรวจเงินรวม · ก่อนหมดอายุ · ค่าผ่านทางสี่ครั้ง · เงินสดที่ต้องหา · ราคาชำระต่างจากราคาขายจริง · 🔎 ขนาดไม่เท่ากัน · ✍️ ห้าข้อ
คีย์เดิม (ตารางขา · แว่นขยาย · funding90วัน · ฝึก · บัตรตลาดมิน.perp/funding…) คงไว้: ภาคผนวกและบท 7 อาจยังอ่าน
"""


def extend(data, D, q):
    m = data["บัญชีมิน"]
    btc = m["BTC"]
    spot, fut, days = D(btc["spot"]), D(btc["futures"]), D(btc["วันถึงหมดอายุ"])
    scale = D(str(m["สเกล"]))
    basis = fut - spot

    # ตาราง long/short 0.1 BTC เมื่อราคาขึ้น 2,000 (00.02)
    now = D(102000)
    qty = D("0.1")
    legs = {
        "ราคาเปิด": q(spot, 0),
        "ราคาปัจจุบัน": q(now, 0),
        "ราคาเปลี่ยน": q(now - spot, 0),
        "จำนวน": q(qty, 1),
        "long": q(qty * (now - spot), 0),
        "short": q(-qty * (now - spot), 0),
    }

    # แว่นขยาย ×100: ตารางคิดที่ 1 BTC · มินทำจริง 0.01 BTC
    lens = {
        "ตัวคูณ": q(1 / scale, 0),
        "basisของมิน": q(basis * scale, 0),
        "เงินบนexchangeสาธิต": q(D(m["เงินบนexchange"]) / scale, 0),
    }

    # funding ฉบับสั้น: short perp 1 BTC · +0.01% ต่อรอบ · รอบละ 8 ชั่วโมงในตัวอย่างนี้
    rate = D(str(m["funding"]["ต่อรอบเปอร์เซ็นต์"])) / 100
    per_round = spot * rate
    rounds_day = D(24) / D(m["funding"]["ชั่วโมงต่อรอบในตัวอย่าง"])
    rounds = rounds_day * days
    total = per_round * rounds
    funding = {
        "ต่อรอบ": q(per_round, 0),
        "รอบต่อวัน": q(rounds_day, 0),
        "รอบใน90วัน": q(rounds, 0),
        "รวม90วันถ้าอัตราคงที่": q(total, 0),
        "ต่ำกว่าbasis": q(basis - total, 0),
    }

    # ใบ 00 บัตรตลาดของมิน (สี่ช่องของบทนี้) — สัญญาใกล้ใช้อัตรา basis ต่อวันเดียวกับสัญญา 90 วัน
    near_days = D(30)
    near = spot + basis * near_days / days
    perp_gap_pct = D("0.05")                       # สมมติ: perp ห่าง spot 0.05% (ภาพหน้าจอสอน)
    perp = spot * (1 + perp_gap_pct / 100)
    card = {
        "spot": q(spot, 0),
        "futures90": q(fut, 0),
        "วัน90": q(days, 0),
        "basis90": q(basis, 0),
        "basis90เปอร์เซ็นต์": q(basis / spot * 100, 2),
        "futuresใกล้": q(near, 0),
        "วันใกล้": q(near_days, 0),
        "basisใกล้": q(near - spot, 0),
        "basisใกล้เปอร์เซ็นต์": q((near - spot) / spot * 100, 2),
        "perp": q(perp, 0),
        "perpห่างspot": q(perp - spot, 0),
        "perpห่างspotเปอร์เซ็นต์": q(perp_gap_pct, 2),
        "fundingล่าสุดเปอร์เซ็นต์": q(rate * 100, 2),
    }

    # ✍️ ข้อ 1: spot 50,000 · futures 51,000 · ถือ 0.3 BTC สองขา · สามปลายทาง
    es, ef, eq = D(50000), D(51000), D("0.3")
    rows = []
    for p in (D(40000), D(51000), D(65000)):
        a, b = eq * (p - es), eq * (ef - p)
        rows.append({"ราคา": q(p, 0), "ขาspot": q(a, 0), "ขาshort": q(b, 0), "รวม": q(a + b, 0)})
    drill = {
        "spot": q(es, 0), "futures": q(ef, 0), "จำนวน": q(eq, 1),
        "basis": q(ef - es, 0), "basisเปอร์เซ็นต์": q((ef - es) / es * 100, 2),
        "รวมสองขา": q(eq * (ef - es), 0),
        "ปลายทาง": rows,
    }

    v2 = _v2(data, D, q, spot, fut, basis, card)

    return {
        "v2": v2,
        "ตารางขา": legs,
        "แว่นขยาย": lens,
        "funding90วัน": funding,
        "บัตรตลาดมิน": card,
        "ฝึก": drill,
        "_แบบฝึก": [
            {"โจทย์": "ชุดเดิม (ซื้อ spot 1 BTC ที่ 100,000 · ขาย futures 1 BTC ที่ 103,000) ราคาวันหมดอายุ 120,000 — ขา spot / ขา futures / รวม",
             "คำตอบ": [float(v2["ฝึก"]["ข้อ1"]["ขาspot"]), float(v2["ฝึก"]["ข้อ1"]["ขาfutures"]), float(v2["ฝึก"]["ข้อ1"]["รวม"])]},
            {"โจทย์": "futures 104,500 แทน 103,000 ราคาวันหมดอายุ 60,000 — ขา spot / ขา futures / รวม",
             "คำตอบ": [float(v2["ฝึก"]["ข้อ2"]["ขาspot"]), float(v2["ฝึก"]["ข้อ2"]["ขาfutures"]), float(v2["ฝึก"]["ข้อ2"]["รวม"])]},
            {"โจทย์": "ชุดเดิม แต่ปิดวันที่ 30 ที่ spot 101,000 · futures 101,500 — ขา spot / ขา futures / รวม",
             "คำตอบ": [float(v2["ฝึก"]["ข้อ3"]["ขาspot"]), float(v2["ฝึก"]["ข้อ3"]["ขาfutures"]), float(v2["ฝึก"]["ข้อ3"]["รวม"])]},
            {"โจทย์": "สัญญา 30 วัน basis 1,000 กับสัญญา 90 วัน basis 3,000 — ต่อ 30 วันได้เท่ากันไหม และใช้สัญญา 30 วันสามรอบเสียค่าผ่านทางรวมเท่าไร",
             "คำตอบ": [float(v2["ฝึก"]["ข้อ4"]["ต่อ30วันของสัญญา90วัน"]), float(v2["ฝึก"]["ข้อ4"]["ค่าผ่านทางสามรอบ"])]},
            {"โจทย์": "กองทุนดัชนี 2,000 · futures ดัชนี 2,030 (60 วัน) ถือหนึ่งหน่วยสองขาจนหมดอายุ — ทั้งชุดได้เท่าไร และกี่ %",
             "คำตอบ": [float(v2["ฝึก"]["ข้อ5"]["basis"]), float(v2["ฝึก"]["ข้อ5"]["basisเปอร์เซ็นต์"])]},
        ],
    }


def _v2(data, D, q, spot, fut, basis, card):
    """ผลกลางทางของบท 0 ฉบับ v2 — 1 BTC ตลอด · ทุกค่าคิดจากราคาบนจอ (spot 100,000 · futures 103,000) หรือโจทย์ที่ประกาศในบท"""
    m = data["บัญชีมิน"]
    one = D(1)

    # ตรวจอีกทาง: สมุดสามบัญชีแบบหน้าพื้นฐาน 4 (เงินสด · ของที่ถือ/ภาระ · มูลค่าบัญชีรวม)
    # ขายสัญญาไม่มีเงินสดเข้า · วันหมดอายุสัญญาจ่ายส่วนต่างเป็นเงินสด · ขายเหรียญที่ราคาวันนั้น
    cash = []
    for t in (D(60000), D(100000), D(150000)):
        contract = fut - t                         # บวก = สัญญาจ่ายให้มิน · ลบ = มินจ่าย
        cash.append({"ราคาวันหมดอายุ": q(t, 0), "เงินสดเริ่ม": q(spot, 0), "เงินสดหลังซื้อ": q(spot - spot, 0),
                     "เหรียญ": q(t, 0), "สัญญา": q(contract, 0), "equity": q(t + contract, 0),
                     "เงินสดจบ": q(t + contract, 0), "สุทธิ": q(t + contract - spot, 0)})

    # ก่อนหมดอายุ (วันที่ 10 ในตัวอย่าง): ราคาขึ้น 10% · basis กว้างขึ้นเป็น 3,200 (ราคาเดียวกับบท 4)
    s10 = spot * D("1.1")
    f10 = s10 + D(3200)
    early = {"spot": q(s10, 0), "futures": q(f10, 0), "basis": q(f10 - s10, 0),
             "ขาspot": q(s10 - spot, 0), "ขาfutures": q(fut - f10, 0), "รวม": q((s10 - spot) + (fut - f10), 0),
             "basisกว้างขึ้น": q(f10 - s10 - basis, 0),
             "เงินสดที่ต้องหา": q(f10 - fut, 0)}

    # ค่าผ่านทาง: ทุกครั้งที่กด = ค่าธรรมเนียม taker 0.05% ของ 100,000 + ราคาแย่กว่าบนจอครึ่งหนึ่งของส่วนต่างซื้อ-ขาย 20
    fee = spot * D(str(m["ค่าธรรมเนียม"]["taker"])) / 100
    half = D(m["BTC"]["ask"] - m["BTC"]["bid"]) / 2
    per_fill = fee + half
    fills = D(4)
    toll = {"ค่าธรรมเนียมต่อครั้ง": q(fee, 0), "ราคาแย่กว่าต่อครั้ง": q(half, 0), "ต่อครั้ง": q(per_fill, 0),
            "จำนวนครั้ง": q(fills, 0), "รวม": q(per_fill * fills, 0), "เหลือ": q(basis - per_fill * fills, 0)}

    # ราคาชำระ ≠ ราคาที่ขายเหรียญได้จริง: สัญญาปิดที่ 60,000 แต่ขายเหรียญได้ 59,900
    settle, sold = D(60000), D(59900)
    gap = {"ราคาชำระ": q(settle, 0), "ขายได้จริง": q(sold, 0), "ต่าง": q(sold - settle, 0),
           "เหลือ": q(basis + sold - settle, 0)}

    # 🔎 ขนาดไม่เท่ากัน: spot 1 BTC แต่ขาย futures 2 สัญญา
    uneq = []
    for t in (D(60000), D(150000)):
        a, b = one * (t - spot), 2 * (fut - t)
        uneq.append({"ราคาวันหมดอายุ": q(t, 0), "ขาspot": q(a, 0), "ขาfutures": q(b, 0), "รวม": q(a + b, 0)})

    # ✍️ ห้าข้อ
    t1 = D(120000)
    ex1 = {"ราคา": q(t1, 0), "ขาspot": q(t1 - spot, 0), "ขาfutures": q(fut - t1, 0), "รวม": q(fut - spot, 0)}
    f2, t2 = D(104500), D(60000)
    ex2 = {"futures": q(f2, 0), "basis": q(f2 - spot, 0), "basisเปอร์เซ็นต์": q((f2 - spot) / spot * 100, 1),
           "ราคา": q(t2, 0), "ขาspot": q(t2 - spot, 0), "ขาfutures": q(f2 - t2, 0), "รวม": q(f2 - spot, 0)}
    s30, f30 = D(101000), D(101500)
    ex3 = {"spot": q(s30, 0), "futures": q(f30, 0), "basis": q(f30 - s30, 0),
           "ขาspot": q(s30 - spot, 0), "ขาfutures": q(fut - f30, 0), "รวม": q((s30 - spot) + (fut - f30), 0)}
    near_basis, near_days, days = D(card["basisใกล้"]), D(card["วันใกล้"]), D(card["วัน90"])
    ex4 = {"basis30วัน": q(near_basis, 0), "basis90วัน": q(basis, 0),
           "จำนวนช่วง30วัน": q(days / near_days, 0),
           "ต่อ30วันของสัญญา90วัน": q(basis * near_days / days, 0),
           "ค่าผ่านทางสามรอบ": q(per_fill * fills * days / near_days, 0)}
    is_, if_ = D(2000), D(2030)
    rows5 = []
    for t in (D(1800), D(2300)):
        rows5.append({"ราคา": q(t, 0), "ขากองทุน": q(t - is_, 0), "ขาfutures": q(if_ - t, 0), "รวม": q(if_ - is_, 0)})
    ex5 = {"กองทุน": q(is_, 0), "futures": q(if_, 0), "วัน": 60, "basis": q(if_ - is_, 0),
           "basisเปอร์เซ็นต์": q((if_ - is_) / is_ * 100, 1), "ปลายทาง": rows5}

    return {
        "ตรวจเงินรวม": cash,
        "ก่อนหมดอายุ": early,
        "ค่าผ่านทาง": toll,
        "ราคาชำระต่าง": gap,
        "ขนาดไม่เท่ากัน": uneq,
        "ฝึก": {"ข้อ1": ex1, "ข้อ2": ex2, "ข้อ3": ex3, "ข้อ4": ex4, "ข้อ5": ex5},
    }
