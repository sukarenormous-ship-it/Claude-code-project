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

    # ── v2: ผลกลางทางที่บท v2 แสดงการคิด (แผน 14 · ไม่แตะคีย์เดิม) ──
    fee = D(data["ch00"]["v2"]["ค่าผ่านทาง"]["ค่าธรรมเนียมต่อครั้ง"])   # 50 ต่อครั้งต่อ 1 BTC (บท 0 · บท 1)
    pct_m = D(m["กติกาหลักประกันเปอร์เซ็นต์"])
    cash1 = cap - s0                       # หลังซื้อ spot
    cash3 = cash1 - margin0                # วาง Margin (ขายสัญญาไม่มีเงินสดเข้า) = Free Cash ก่อนค่าธรรมเนียม
    cash4 = cash3 - fee                    # ค่าธรรมเนียมขา spot (ตารางรวบไว้ท้าย)
    cash5 = cash4 - fee                    # ค่าธรรมเนียมขา futures
    k2 = case(c2["spot"], c2["futures"], c2["วันที่เหลือ"])
    rate0 = D(str(c["simpleบนจอ"]))        # 12.17 ที่ปัดแล้ว (ตัวที่จอโชว์)
    pct0 = basis0 / s0 * 100               # 3% ต่อ 90 วัน
    k1_close_fee = D(k1["รวม"]) - 4 * fee

    def annual_ex(spot, fut, days, days_back):
        spot, fut, days, days_back = D(spot), D(fut), D(days), D(days_back)
        b = fut - spot
        p = b / spot * 100
        r = p * year / days
        back = r * days_back / year
        b_back = spot * back / 100
        return {"basis": q(b, 0), "basisเปอร์เซ็นต์": q(p, 2), "คูณ365": q(p * year, 2), "ต่อปี": q(r, 2),
                "ถอยคูณวัน": q(r * days_back, 2), "ถอยเปอร์เซ็นต์": q(back, 2), "basisถอย": q(b_back, 0),
                "futuresถอย": q(spot + b_back, 0), "กำไรขาshort": q(b - b_back, 0)}

    # ✍️ ข้อ 5 (ถ่ายโอน): กองทุนดัชนีหุ้น 2,000 · futures 2,030 · 73 วัน · ทุน 2,500 · Margin 10% · ดัชนีลง 1,900 / 1,926
    i_s0, i_f0, i_days, i_cap = D(2000), D(2030), D(73), D(2500)
    i_m = i_f0 * pct_m / 100
    i_free = i_cap - i_s0 - i_m
    i_s1, i_f1 = D(1900), D(1926)
    ex5 = {"ราคากองทุน": q(i_s0, 0), "futures": q(i_f0, 0), "วัน": q(i_days, 0), "ทุน": q(i_cap, 0),
           "Margin": q(i_m, 0), "เงินสดอิสระ": q(i_free, 0), "basis": q(i_f0 - i_s0, 0),
           "basisเปอร์เซ็นต์": q((i_f0 - i_s0) / i_s0 * 100, 2),
           "คูณ365": q((i_f0 - i_s0) / i_s0 * 100 * year, 2),
           "ต่อปี": q((i_f0 - i_s0) / i_s0 * 100 * year / i_days, 2),
           "ต่อทุนเปอร์เซ็นต์": q((i_f0 - i_s0) / i_cap * 100, 2),
           "กองทุนใหม่": q(i_s1, 0), "futuresใหม่": q(i_f1, 0),
           "ขากองทุน": q(i_s1 - i_s0, 0), "ขาfutures": q(i_f0 - i_f1, 0),
           "รวม": q(i_s1 - i_s0 + i_f0 - i_f1, 0), "basisใหม่": q(i_f1 - i_s1, 0),
           "equity": q(i_free + i_s1 + i_m + (i_f0 - i_f1), 0)}
    # ✍️ ข้อ 2 (เปลี่ยนเลขหนึ่งตัว): สัญญา 90 วันขึ้นจอที่ 104,500 · อัตราต่อปีคงที่ · เหลือ 60 วัน spot เท่าเดิม
    ex2v = annual_ex(s0, 104500, days0, c1["วันที่เหลือ"])

    v2 = {
        "ค่าธรรมเนียมต่อครั้ง": q(fee, 0),
        "กติกาMargin": {"เปอร์เซ็นต์": q(pct_m, 0), "ราคาfutures": q(f0, 0), "Margin": q(f0 * pct_m / 100, 0)},
        # ตารางเปิดไม้ทีละจังหวะ (ต่อเนื่องกัน) พร้อมค่าธรรมเนียมสองครั้ง — ตารางหลังจากนี้ตัดค่าธรรมเนียมออก
        "เปิดพร้อมค่าธรรมเนียม": {
            "เริ่ม": {"เงินสด": q(cap, 0), "equity": q(cap, 0)},
            "ซื้อspot": {"เงินสด": q(cash1, 0), "เหรียญ": q(s0, 0), "equity": q(cash1 + s0, 0)},
            "วางMargin": {"เงินสด": q(cash3, 0), "Margin": q(margin0, 0), "equity": q(cash3 + s0 + margin0, 0)},
            "ค่าธรรมเนียมspot": {"เงินสด": q(cash4, 0), "equity": q(cash4 + s0 + margin0, 0)},
            "ค่าธรรมเนียมfutures": {"เงินสด": q(cash5, 0), "equity": q(cash5 + s0 + margin0, 0)},
            "ค่าธรรมเนียมรวม": q(2 * fee, 0),
            "equityต่ำกว่าทุน": q(cash5 + s0 + margin0 - cap, 0),
        },
        # สองภาพของขา short (พื้นฐาน 2): ยืมมาขาย vs ข้อตกลงขาย (futures + Margin) · สมมติขายได้ 103,000 ทั้งคู่เพื่อเทียบ
        "สองภาพ": {
            "ยืม": {"เงินสด": q(cash1 + f0, 0), "เหรียญ": q(s0, 0), "ภาระ": q(-f0, 0),
                    "equity": q(cash1 + f0 + s0 - f0, 0)},
            "สัญญา": {"เงินสด": q(free0, 0), "เหรียญ": q(s0, 0), "Margin": q(margin0, 0), "สัญญา": 0,
                      "equity": q(free0 + s0 + margin0, 0)},
            "จอบวกลบequity": q(wrong - cap, 0),
        },
        "กรณี1": {"Marginหลังชำระ": q(margin0 + D(k1["ขาfutures"]), 0), "เงินสดหลังปิด": q(free0 + s0 + margin0 + D(k1["ขาfutures"]), 0),
                  "รับรู้": k1["รวม"], "ค่าธรรมเนียมสี่ครั้ง": q(4 * fee, 0), "รับรู้หลังค่าธรรมเนียม": q(k1_close_fee, 0)},
        "กรณี2": {"Marginหลังชำระ": q(margin0 + D(k2["ขาfutures"]), 0),
                  "equityหลังชำระ": q(free0 + D(k2["spot"]) + margin0 + D(k2["ขาfutures"]), 0),
                  "เหลือFreeCashหลังเติมให้ศูนย์": q(free0 + margin0 + D(k2["ขาfutures"]), 0)},
        # สอนคิดต่อปีก่อนใช้ 12.17%: 3% ใน 90 วัน → × 365 → ÷ 90 · ถอยกลับ: 12.17 × 60 ÷ 365 ≈ 2% → 2,000
        "ต่อปี": {"basisเปอร์เซ็นต์": q(pct0, 2), "คูณ365": q(pct0 * year, 0), "ต่อปี": c["simpleบนจอ"],
                  "ต่อปีก่อนปัด": q(pct0 * year / days0, 4),
                  "ถอยคูณ60": q(rate0 * D(c1["วันที่เหลือ"]), 2), "ถอยเปอร์เซ็นต์": q(pct0 * D(c1["วันที่เหลือ"]) / days0, 2),
                  "ต่อ30วัน": q(pct0 * 30 / days0, 2),
                  "basis60": q(s0 * pct0 * D(c1["วันที่เหลือ"]) / days0 / 100, 0),
                  "futures60": q(s0 + s0 * pct0 * D(c1["วันที่เหลือ"]) / days0 / 100, 0)},
        "ฝึก1": {"พลาดลืมสัญญา": q(free0 + D(ex1["spot"]) + margin0, 0)},
        "ฝึก2": ex2v,
        "ฝึก4": {"Marginหลังชำระ": q(margin0 + D(ex2["ขาfutures"]), 0)},
        "ฝึก5": dict(ex5, พลาดนับมูลค่าสถานะ=q(D(ex5["equity"]) + i_f0, 0)),
    }

    out = {
        "v2": v2,
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
            # v2 (ต่อท้าย ไม่เลื่อนลำดับเดิม): ✍️ ข้อ 2 เปลี่ยนเลขหนึ่งตัว · ✍️ ข้อ 5 ถ่ายโอน
            {"โจทย์": "สัญญา 90 วันขึ้นจอ 104,500 แทน 103,000 → basis เป็น % · ต่อปี · ถ้าอัตราต่อปีคงที่ เหลือ 60 วัน "
                      "spot เท่าเดิม futures เป็นเท่าไร ขา short ได้เท่าไร", **ex2v, "คำตอบ": ex2v["ต่อปี"]},
            {"โจทย์": "กองทุนดัชนี 2,000 + short futures 2,030 (73 วัน) ทุน 2,500 Margin 10% → Free Cash · % ต่อปี · "
                      "% ต่อทุน · ดัชนี 1,900 futures 1,926 → ทีละขา · ทางลัด · equity", **ex5, "คำตอบ": ex5["รวม"]},
        ],
    }
    return out
