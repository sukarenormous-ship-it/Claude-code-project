"""บท 0 — ส่วนต่าง 3,000 บนหน้าจอ · ค่าใหม่ที่บทใช้ (ตาราง ±0.1 BTC · แว่นขยาย ×100 · funding ฉบับสั้น · ใบ 00 · ✍️)

ทุกค่าคำนวณจาก บัญชีมิน / ch00 เดิม หรือจากตัวเลขโจทย์ที่ประกาศในบท (🔢 สมมติเพื่อสอน)
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

    return {
        "ตารางขา": legs,
        "แว่นขยาย": lens,
        "funding90วัน": funding,
        "บัตรตลาดมิน": card,
        "ฝึก": drill,
        "_แบบฝึก": [
            {"โจทย์": "ถือ spot 0.3 BTC ที่ 50,000 และ short futures 0.3 BTC ที่ 51,000 จนหมดอายุ — สองขารวมกันได้เท่าไรทุกปลายทาง",
             "คำตอบ": float(drill["รวมสองขา"])},
            {"โจทย์": "funding +0.01% ต่อรอบ รอบละ 8 ชั่วโมงในตัวอย่างนี้ คงที่ 90 วัน — short perp 1 BTC ที่ 100,000 ได้รวมเท่าไร",
             "คำตอบ": float(funding["รวม90วันถ้าอัตราคงที่"])},
            {"โจทย์": "เหรียญที่มีแค่ perp ไม่มี dated futures — คำถามประจำเล่มข้อไหนเปลี่ยนคำตอบ"},
        ],
    }
