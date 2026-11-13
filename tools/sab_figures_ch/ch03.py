"""บท 3 — สมุดบัญชีสองขา · ค่าที่บทพิมพ์แต่ยังไม่มีใน JSON หลัก

ทุกค่าคำนวณจาก บัญชีมิน + ch03 เดิม (03.09 สามแถวแรก · 02.05 กรณี 1/2 แบบ simple) หรือจากตัวเลขโจทย์ที่ประกาศในบท
กำไรจากราคา = จำนวนมีเครื่องหมาย × ราคาที่เปลี่ยน (spot +1 · futures −1) = basis ตอนเข้า − basis ตอนนี้
"""


def extend(data, D, q):
    m, c = data["บัญชีมิน"], data["ch03"]
    btc = m["BTC"]
    s0, f0 = D(btc["spot"]), D(btc["futures"])
    days0 = D(btc["วันถึงหมดอายุ"])
    basis0 = f0 - s0
    year = D(365)
    cap = D(m["ทุนภาค1"]["รวม"])
    margin0 = D(m["ทุนภาค1"]["หลักประกัน"])
    free0 = D(m["ทุนภาค1"]["เงินสดอิสระ"])
    scale = D(str(m["สเกล"]))

    def simple(basis, spot, days):
        return q(basis / spot * year / days * 100, 2)

    def case(spot, fut, days):
        spot, fut, days = D(spot), D(fut), D(days)
        leg_s = spot - s0                 # +1 BTC
        leg_f = -(fut - f0)               # −1 BTC
        basis = fut - spot
        return {
            "spot": q(spot, 0), "futures": q(fut, 0), "วันที่เหลือ": q(days, 0),
            "ขาspot": q(leg_s, 0), "ขาfutures": q(leg_f, 0), "รวม": q(leg_s + leg_f, 0),
            "basis": q(basis, 0), "basisตอนเข้าลบตอนนี้": q(basis0 - basis, 0),
            "อัตราบนจอ": simple(basis, spot, days) if days > 0 else None,
            # equity = เงินสดอิสระ + มูลค่า spot + บัญชีหลักประกัน + กำไรค้างของ futures (ยังไม่ย้ายเข้าบัญชี)
            "equity": q(free0 + spot + margin0 + leg_f, 0),
        }

    c1 = c["กรณี1_simple"]
    c2 = c["กรณี2"]
    settle = D(btc["ราคาชำระ"])

    def mini(x):
        v = D(str(x)) * scale
        return q(v, 0) if v == v.to_integral() else q(v, 2)

    # หน้าจอที่มินบวกเอง: นับขนาดสัญญา futures ที่ขายไว้เป็นเงิน แทนเงินจริงในบัญชีหลักประกัน
    wrong = s0 + f0 + free0

    # ✍️ ข้อ 1 (คำนวณ): ผ่านไป 20 วัน spot 96,000 · futures 98,400
    ex1 = case(96000, 98400, days0 - 20)
    # ✍️ ข้อ 2 (ตัดสินใจ): spot 108,000 · futures 111,500 · หน้า spot เขียว หน้า futures แดง
    ex2 = case(108000, 111500, days0 - 10)
    # ✍️ ข้อ 3 (ถ่ายโอน): กรณี 1 ใต้สองกติกา — ชำระสิ้นวัน vs ค้างเป็นกำไรค้างจนปิด
    k1 = case(c1["spot"], c1["futures"], c1["วันที่เหลือ"])
    ex3 = {
        "ชำระสิ้นวัน": {"บัญชีหลักประกัน": q(margin0 + D(k1["ขาfutures"]), 0), "กำไรค้าง": 0,
                         "equity": k1["equity"]},
        "ค้างจนปิด": {"บัญชีหลักประกัน": q(margin0, 0), "กำไรค้าง": k1["ขาfutures"], "equity": k1["equity"]},
        "นับซ้ำผิด": q(D(k1["equity"]) + D(k1["ขาfutures"]), 0),
    }

    out = {
        "วันต่อปี": q(year, 0),
        "เปิดไม้_เปลี่ยน": {
            "ซื้อspot": q(-s0, 0),                 # เงินสด → เหรียญ
            "วางหลักประกัน": q(-margin0, 0),       # เงินสด → บัญชีหลักประกัน
            "ขนาดสัญญาfutures": q(f0, 0),
        },
        "จอบวกผิด": {"spot": q(s0, 0), "ขนาดสัญญาfutures": q(f0, 0), "เงินสดอิสระ": q(free0, 0),
                      "รวมผิด": q(wrong, 0), "เกินจริง": q(wrong - cap, 0)},
        "ตารางกรณี": {
            "เริ่ม": {"basis": q(basis0, 0), "อัตราบนจอ": c["simpleบนจอ"], "กำไรจากราคา": 0, "equity": q(cap, 0)},
            "กรณี1": k1,
            "กรณี2": case(c2["spot"], c2["futures"], c2["วันที่เหลือ"]),
            "หมดอายุ": case(settle, settle, 0),
        },
        "ตัวหาร": {
            "ต่อspot": q(basis0 / s0 * 100, 2),
            "ต่อทุน": q(basis0 / cap * 100, 2),
            "สองขาบวกกัน": q(s0 + f0, 0),
            "ต่อสองขา": q(basis0 / (s0 + f0) * 100, 2),
        },
        "ของมิน": {
            "เงินบนexchange": mini(cap), "ซื้อspot": mini(s0), "ขนาดสัญญาfutures": mini(f0),
            "หลักประกัน": mini(margin0), "เงินสดอิสระ": mini(free0), "equity": mini(cap),
            "basis": mini(basis0), "จอบวกผิด": mini(wrong),
            "บัญชีทดลอง": mini(data["เรื่อง"]["part3"]["close"]["บัญชีทดลอง"]),
            "กรณี1กำไร": mini(k1["รวม"]), "กรณี1equity": mini(k1["equity"]), "กรณี2รวม": mini(c2["รวม"]),
        },
        "_claims": [
            {"id": "ch03-app-labels",
             "ข้อความ": "แอป exchange คริปโตหลายแห่งแสดงกำไรของสถานะที่ยังเปิดเป็น Unrealized PnL และยอดบัญชี futures เป็น "
                        "Margin balance (มักรวม Unrealized แล้ว) · ชื่อป้ายและนิยาม Available balance ต่างกันตาม exchange "
                        "และชนิดบัญชี — ต้องจับคู่จากหน้าจอและเอกสารของ exchange ที่ใช้",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [3]},
        ],
        "_แบบฝึก": [
            {"โจทย์": "spot 1 BTC (ซื้อ 100,000) + short futures 1 BTC (ขาย 103,000) · ผ่านไป 20 วัน spot 96,000 futures 98,400 "
                      "→ กำไรทีละขา · ทางลัด basis · equity", **{k: ex1[k] for k in
                      ("spot", "futures", "ขาspot", "ขาfutures", "รวม", "basis", "basisตอนเข้าลบตอนนี้", "equity")},
             "คำตอบ": ex1["รวม"]},
            {"โจทย์": "หน้า spot +8,000 หน้า futures −8,500 (spot 108,000 · futures 111,500) → รวมเท่าไร ควรปิดขาแดงไหม",
             **{k: ex2[k] for k in ("spot", "futures", "ขาspot", "ขาfutures", "รวม", "basis", "equity")},
             "คำตอบ": ex2["รวม"]},
            {"โจทย์": "กรณี 1 ใต้สองกติกา: ชำระสิ้นวัน vs ค้างเป็นกำไรค้างจนปิด → ช่องไหนต่าง equity ต่างไหม", **ex3,
             "คำตอบ": ex3["ชำระสิ้นวัน"]["equity"]},
        ],
    }
    return out
