"""บท 6 — วันที่ 30: ปิดหรือถือ · ค่าที่บทพิมพ์แต่ยังไม่มีใน JSON หลัก

ทุกค่าคำนวณจาก บัญชีมิน + ch05 (บันได) + ch06 เดิม (วันที่30 · ถือถึงวันหมดอายุ · รอบชดเชย)
ค่าธรรมเนียม taker 0.05% ต่อครั้ง · ไม่รวมส่วนต่างราคาซื้อ-ขาย (ตามบท 5)
กำไรที่มินรับรู้ = กำไรจากราคา 2,500 − ค่าธรรมเนียมเปิด (ซื้อ spot + short futures) − ค่าธรรมเนียมปิดสองขาวันที่ 30
"""


def extend(data, D, q):
    m, c5, c6 = data["บัญชีมิน"], data["ch05"], data["ch06"]
    btc = m["BTC"]
    fee = D(str(m["ค่าธรรมเนียม"]["taker"])) / 100
    hurdle = D(str(m["hurdle"])) / 100
    year = D(365)
    scale = D(str(m["สเกล"]))
    cap = D(m["ทุนภาค1"]["รวม"])
    s0, f0, settle = D(btc["spot"]), D(btc["futures"]), D(btc["ราคาชำระ"])
    days = D(btc["วันถึงหมดอายุ"])
    d30 = c6["วันที่30"]
    s30, f30 = D(d30["spot"]), D(d30["futures"])
    left = days - 30                                    # 60 วันที่เหลือ
    opp60 = D(str(d30["เสียโอกาส60วัน"]))

    open_fee = fee * (s0 + f0)                          # 50 + 51.5
    close_value = s30 + f30                             # มูลค่าที่ซื้อขายตอนปิดสองขา
    close_fee = fee * close_value
    price_pnl = (s30 - s0) + (f0 - f30)                 # 2,500
    realised = price_pnl - open_fee - close_fee         # 2,297.25

    # ถือถึงวันหมดอายุจริงตามเรื่อง: ชำระ 105,000 แต่ขาย spot ได้ 104,900
    h = c6["ถือถึงวันหมดอายุ"]
    sold = D(h["ขายspotได้"])
    hold_price = D(h["กำไรจากราคา"])
    hold_sale_fee = fee * sold
    hold_net = hold_price - open_fee - hold_sale_fee
    hold_extra = hold_net - realised

    # basis วันที่ 30 ที่ทำให้ "ถือได้เพิ่ม" = ค่าเสียโอกาส 60 วัน
    #   ถือได้เพิ่ม = b + fee·(2·S30 + b) − fee·S30  →  b·(1 + fee) = ค่าเสียโอกาส − fee·S30
    be_basis = (opp60 - fee * s30) / (1 + fee)

    # ✍️ ข้อ 1: วันที่ 45 · เหลือ 45 วัน · spot 101,000 · futures 101,800
    e1_left, e1_s, e1_f = D(45), D(101000), D(101800)
    e1_basis = e1_f - e1_s
    e1_close_fee = fee * (e1_s + e1_f)
    e1_hold_fee = fee * e1_s
    e1_extra = e1_basis - e1_hold_fee + e1_close_fee
    e1_opp = cap * hurdle * e1_left / year

    # ✍️ ข้อ 2: ชุดของมินวันที่ 30 แต่ hurdle 2% · ถ้าขาย spot ต่ำกว่าราคาชำระ 100 ด้วย
    extra = D(str(d30["ถือได้เพิ่ม"]))
    opp2 = D(str(d30["เสียโอกาสที่hurdle2"]))
    gap = D(btc["ราคาชำระ"]) - sold                     # 100
    e2_margin = extra - opp2
    e2_after_gap = e2_margin - gap

    # ✍️ ข้อ 3 (ถ่ายโอน · การต่อสัญญา): วันที่ 30 ปิดแล้วเปิดสัญญา 90 วันถัดไปที่ spot 101,000 futures 103,500
    r_s, r_f, r_days = s30, D(103500), days
    r_basis = r_f - r_s
    r_fee = fee * (r_s + r_f + r_f)                     # ซื้อ spot · short futures · ขาย spot วันหมดอายุที่ราคา futures
    r_net = r_basis - r_fee
    r_opp = cap * hurdle * r_days / year
    r_excess = r_net - r_opp

    def ann(x, base, d):
        return x / base * year / d * 100

    def mini(x):
        return q(D(str(x)) * scale, 2)

    on_ex = D(m["ทุนภาค1"]["หลักประกัน"]) + D(m["ทุนภาค1"]["เงินสดอิสระ"])

    out = {
        "วันที่เหลือ": int(left),
        "ค่าธรรมเนียมเปิด": q(open_fee, 2),
        "มูลค่าปิดสองขา": q(close_value, 0),
        "ค่าธรรมเนียมรวมไปกลับ": q(open_fee + close_fee, 2),
        "equityก่อนค่าธรรมเนียม": q(cap + price_pnl, 0),
        "เงินสดหลังปิด": q(cap + realised, 2),
        "basisคุ้มถือวันที่30": q(be_basis, 2),
        "ถือจริงถึงวันหมดอายุ": {
            "ค่าธรรมเนียมขายspot": q(hold_sale_fee, 2),
            "ค่าธรรมเนียมรวม": q(open_fee + hold_sale_fee, 2),
            "สุทธิ": q(hold_net, 2),
            "มากกว่าปิดวันที่30": q(hold_extra, 2),
            "ส่วนที่หาย": q(D(btc["basis"]) - hold_price, 0),
            "ขาspot": q(sold - s0, 0),
            "ขาfutures": q(f0 - D(btc["ราคาชำระ"]), 0),
        },
        "เงินบนexchangeถ้าspotอยู่นอก": q(on_ex, 0),
        "ของมิน": {
            "กำไรจากราคา": int(mini(price_pnl)) if mini(price_pnl) == int(mini(price_pnl)) else mini(price_pnl),
            "ค่าธรรมเนียมเปิด": mini(open_fee),
            "ค่าธรรมเนียมปิด": mini(close_fee),
            "เงินสดหลังปิด": mini(cap + realised),
            "ถือได้เพิ่ม": mini(extra),
            "เสียโอกาส60วัน": mini(opp60),
        },
        "ฝึก": {
            "1": {"วันที่เหลือ": int(e1_left), "spot": q(e1_s, 0), "futures": q(e1_f, 0), "basis": q(e1_basis, 0),
                  "มูลค่าปิดสองขา": q(e1_s + e1_f, 0), "ค่าธรรมเนียมปิด": q(e1_close_fee, 2), "ค่าธรรมเนียมถือ": q(e1_hold_fee, 2),
                  "ถือได้เพิ่ม": q(e1_extra, 2), "เสียโอกาส": q(e1_opp, 2), "ถือดีกว่า": q(e1_extra - e1_opp, 2),
                  "ตัดสิน": "ถือ" if e1_extra > e1_opp else "ปิด"},
            "2": {"ถือดีกว่า": q(e2_margin, 2), "ส่วนต่างราคาชำระ": q(gap, 0), "เหลือหลังหักส่วนต่าง": q(e2_after_gap, 2)},
            "3": {"futures": q(r_f, 0), "basis": q(r_basis, 0), "ค่าธรรมเนียม": q(r_fee, 2), "สุทธิ": q(r_net, 2),
                  "ค่าเสียโอกาส": q(r_opp, 2), "ส่วนเกิน": q(r_excess, 2),
                  "ส่วนเกินเปอร์เซ็นต์": q(ann(r_excess, cap, r_days), 2),
                  "ต้นทุนไปกลับรวมปิดเดิม": q(close_fee + r_fee, 2)},
        },
        "_claims": [
            {"id": "ch06-exchange-custody",
             "ข้อความ": "เงินและเหรียญที่ฝากไว้ใน exchange เสียหายได้เมื่อ exchange ระงับการถอนหรือล้ม แม้สถานะจะ hedge ราคาไว้ครบ · "
                        "การเก็บ spot นอก exchange ลดเงินที่เสี่ยงแต่เพิ่มเวลาโอนกลับเมื่อต้องขายหรือใช้เป็นหลักประกัน — "
                        "เล่มไม่อ้างเหตุการณ์หรือ exchange ใดเป็นการเฉพาะ",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [6]},
            {"id": "ch06-stablecoin-peg",
             "ข้อความ": "stablecoin สกุลดอลลาร์ที่ใช้คิดกำไรขาดทุนและวางหลักประกันอาจซื้อขายต่ำกว่า 1 ดอลลาร์ชั่วคราว (หลุดหมุด) · "
                        "สถานะที่ hedge ราคา BTC ไว้ครบไม่ได้ hedge ความเสี่ยงนี้ — ขนาดและความถี่ขึ้นกับเหรียญและช่วงเวลา",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [6]},
            {"id": "ch06-settlement-index",
             "ข้อความ": "dated futures คริปโตส่วนใหญ่ชำระด้วยดัชนีที่ exchange คำนวณจากหลายตลาดในช่วงเวลาที่กำหนด "
                        "ไม่ใช่ราคาที่ผู้ถือขาย spot ได้จริง · นิยามดัชนีและช่วงเวลาต่างกันตามสัญญา ต้องอ่านจากเอกสารสัญญา",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [6]},
        ],
        "_แบบฝึก": [
            {"โจทย์": "วันที่ 45 เหลือ 45 วัน spot 101,000 futures 101,800 taker 0.05% hurdle 4% ทุน 125,000 → ถือได้เพิ่ม vs ค่าเสียโอกาส",
             "คำตอบ": [q(e1_extra, 2), q(e1_opp, 2)]},
            {"โจทย์": "ชุดวันที่ 30 ของมิน แต่ hurdle 2% → ถือดีกว่ากี่ดอลลาร์ และเหลือเท่าไรถ้าขาย spot ต่ำกว่าราคาชำระ 100",
             "คำตอบ": [q(e2_margin, 2), q(e2_after_gap, 2)]},
            {"โจทย์": "ต่อสัญญา: ปิดวันที่ 30 แล้วเปิด 90 วันใหม่ spot 101,000 futures 103,500 ทุน 125,000 → ส่วนเกินหลัง hurdle %",
             "คำตอบ": q(ann(r_excess, cap, r_days), 2)},
        ],
    }
    assert q(realised, 2) == c6["มินปิด"]["ต่อ1BTC"], "กำไรรับรู้ต้องตรง ch06.มินปิด"

    # ── v2 (แผน 14.5 · รายงาน C §2.6 ข้อ 4–6): ทุกตัวเลขของ "ปิดหรือถือ" คิดตามได้จากหน้าเดียว ──
    # สมุดสองเล่มจบที่กำไรรับรู้ (เครื่องหมายเดียวกันทั้งสองคอลัมน์) · ถือ = basis บรรจบครบ ขาย spot วันหมดอายุที่ราคา spot วันที่ 30
    hold_price_full = D(btc["basis"])                       # 3,000 (basis เปิดบรรจบครบ)
    hold_sale_fee_30 = fee * s30                            # 50.50 (ขาย spot อย่างเดียว · futures ชำระเอง)
    hold_ledger = hold_price_full - open_fee - hold_sale_fee_30     # 2,848.00
    diff = hold_ledger - realised                           # 550.75
    assert q(diff, 2) == d30["ถือได้เพิ่ม"], "สมุดสองเล่มต้องต่างกันเท่า ch06.วันที่30.ถือได้เพิ่ม"
    # เส้นแบ่ง: ถือได้เพิ่ม = b − fee·S30 + fee·(2·S30 + b) = b × (1 + fee) + fee × S30
    fixed = fee * s30                                       # 50.50 (ส่วนที่ไม่ขึ้นกับ b)
    mult = 1 + fee                                          # 1.0005
    gap_need = opp60 - fixed                                # 771.42
    trial = []
    for b in (700, 750, 771, 800):
        bb = D(b)
        trial.append({"basis": b, "ถือได้เพิ่ม": q(bb * mult + fixed, 2), "เสียโอกาส": q(opp60, 2),
                      "ตัดสิน": "ถือ" if bb * mult + fixed > opp60 else "ปิด"})
    # จุดเปลี่ยน hurdle 2.68%: ถือได้เพิ่ม ÷ ทุน × 365 ÷ วันที่เหลือ
    per60 = diff / cap * 100
    turn = per60 * year / left
    # 🎬 ถือจริงถึงวันหมดอายุ: 550.75 − 448.80 = 100 (ขาย spot ต่ำกว่าราคาชำระ) + 1.95 (ค่าธรรมเนียมขายที่ราคาสูงขึ้น)
    lost_price = D(btc["basis"]) - hold_price                # 100
    extra_fee = hold_sale_fee - fee * s30                    # 52.45 − 50.50 = 1.95
    out["v2"] = {
        "สมุดปิดวันนี้": {"กำไรจากราคา": q(price_pnl, 0), "ค่าธรรมเนียมเปิด": q(open_fee, 2),
                          "ค่าธรรมเนียมปิดสองขา": q(close_fee, 2), "กำไรรับรู้": q(realised, 2)},
        "สมุดถือถึงวันหมดอายุ": {"กำไรจากราคา": q(hold_price_full, 0), "ค่าธรรมเนียมเปิด": q(open_fee, 2),
                                 "ค่าธรรมเนียมขายspot": q(hold_sale_fee_30, 2), "กำไรรับรู้": q(hold_ledger, 2)},
        "ต่างกัน": q(diff, 2), "ต่างกันแยก": {"basisที่เหลือ": q(d30["basis"], 0),
                                              "ค่าธรรมเนียมปิดที่ไม่ต้องจ่าย": q(close_fee, 2),
                                              "ค่าธรรมเนียมขายspotถ้าถือ": q(hold_sale_fee_30, 2)},
        "เส้นแบ่ง": {"ส่วนคงที่": q(fixed, 2), "ตัวคูณ": q(mult, 4), "เสียโอกาส": q(opp60, 2),
                     "เสียโอกาสลบส่วนคงที่": q(gap_need, 2), "basis": q(be_basis, 2), "ลอง": trial},
        "จุดเปลี่ยนhurdle": {"ต่อ60วันเปอร์เซ็นต์": q(per60, 2), "ต่อ60วันเปอร์เซ็นต์ละเอียด": q(per60, 4),
                            "ต่อปีเปอร์เซ็นต์": q(turn, 2), "ตัวคูณต่อปี": q(year / left, 2)},
        "ถือจริง": {"ต่างจากที่คิด": q(diff - hold_extra, 2), "ราคาที่หาย": q(lost_price, 0),
                    "ค่าธรรมเนียมขายเพิ่ม": q(extra_fee, 2), "ค่าธรรมเนียมขายที่104900": q(hold_sale_fee, 2)},
    }
    assert q(diff - hold_extra, 2) == q(lost_price + extra_fee, 2)
    return out
