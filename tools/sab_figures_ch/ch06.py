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

    # ── v2 รอบเขียนบท (ผู้เขียนบท 6): ผลกลางทางที่หน้าแสดงให้เห็นทีละขั้น ──
    v2 = out["v2"]
    leg_s, leg_f = s30 - s0, f0 - f30                      # +1,000 · +1,500
    open_s, open_f = fee * s0, fee * f0                    # 50 · 51.50
    close_s, close_f = fee * s30, fee * f30                # 50.50 · 50.75
    cash_close = cap + realised                            # 127,297.25
    cash_hold = cap + hold_ledger                          # 127,848.00
    opp_year = cap * hurdle                                # 5,000
    close_then_park = cash_close + opp60                   # 127,297.25 + 821.92 (ฝากทุนเดิม 125,000 · กำไรวางไว้เฉย ๆ)
    v2["ทีละขา"] = {"ขาspot": q(leg_s, 0), "ขาfutures": q(leg_f, 0), "รวม": q(leg_s + leg_f, 0),
                    "basisหด": q(D(btc["basis"]) - D(d30["basis"]), 0)}
    v2["ค่าธรรมเนียมทีละครั้ง"] = {"เปิดspot": q(open_s, 2), "เปิดfutures": q(open_f, 2),
                                   "ปิดspot": q(close_s, 2), "ปิดfutures": q(close_f, 2)}
    v2["เงินสดเมื่อจบ"] = {"ปิดวันนี้": q(cash_close, 2), "ถือถึงวันหมดอายุ": q(cash_hold, 2)}
    v2["ค่าธรรมเนียมตอนจบต่างกัน"] = q(close_fee - hold_sale_fee_30, 2)            # 50.75
    v2["เทียบวันเดียวกัน"] = {"เสียโอกาสต่อปี": q(opp_year, 0), "ปิดแล้วฝาก": q(close_then_park, 2),
                               "ถือ": q(cash_hold, 2), "ปิดดีกว่า": q(close_then_park - cash_hold, 2)}
    assert q(close_then_park - cash_hold, 2) == d30["ปิดดีกว่า"][0]
    v2["ค่าธรรมเนียมรวมสองครั้ง"] = q(open_fee + close_fee, 2)                       # 202.75
    # .dist: ค่าปิดสองขาคิดจากราคาสัญญาที่ต่างกันตาม basis
    dist_rows = []
    for row in c6["dist"]:
        bb = D(row["basisวันที่30"])
        cv = s30 + s30 + bb
        dist_rows.append({"basis": int(bb), "futures": q(s30 + bb, 0), "มูลค่าปิดสองขา": q(cv, 0),
                          "ค่าปิดสองขา": q(fee * cv, 2), "ถือได้เพิ่ม": q(bb + fee * cv - fixed, 2)})
        assert q(bb + fee * cv - fixed, 2) == row["ถือได้เพิ่ม"]
    v2["distคิดอย่างไร"] = dist_rows
    # ตารางลองสามแถว 700 / 771 / 800 พร้อมค่าปิดสองขา และห่างจากค่าเสียโอกาสเท่าไร
    trial3 = []
    for b in (700, 771, 800):
        bb = D(b)
        cv = s30 + s30 + bb
        ext = bb + fee * cv - fixed
        trial3.append({"basis": b, "มูลค่าปิดสองขา": q(cv, 0), "ค่าปิดสองขา": q(fee * cv, 2),
                       "ถือได้เพิ่ม": q(ext, 2), "ห่างจากเสียโอกาส": q(abs(ext - opp60), 2),
                       "ตัดสิน": "ถือ" if ext > opp60 else "ปิด"})
    v2["ลองสามแถว"] = trial3
    base_two = s30 + s30                                   # 202,000 (สองราคาเมื่อ basis เป็นศูนย์)
    v2["ประมาณเส้นแบ่ง"] = {"สองราคาราว": q(base_two, 0), "ค่าปิดราว": q(fee * base_two, 0),
                            "ได้นอกจากbasisราว": q(fee * base_two - fixed, 2)}
    v2["จุดเปลี่ยนhurdle"]["ตรวจกลับ"] = q(cap * D("2.68") / 100 * left / year, 2)  # ≈ 550.75
    # 🎬 เทียบวันหมดอายุ: ถือจริง (ชำระ 105,000 ขายได้ 104,900) กับปิดแล้วฝาก
    cash_hold_real = cap + hold_net
    v2["ถือจริง"]["เงินสด"] = q(cash_hold_real, 2)
    v2["ถือจริง"]["ปิดแล้วฝากดีกว่า"] = q(close_then_park - cash_hold_real, 2)
    # รอบชดเชย: วันรวมของ 44 รอบ
    r6 = c6["รอบชดเชย"]
    v2["รอบชดเชยวัน"] = int(D(r6["เสียทั้ง125000"]) * days)                          # 3,960
    v2["รอบชดเชย25000ทศนิยม"] = q(D(on_ex) / D(r6["กำไรต่อรอบ"]), 2)                 # 8.78
    # Depeg: stablecoin 0.99 ดอลลาร์ · เงินสดหลังปิดทั้งก้อน
    peg = D("0.99")
    v2["หลุดหมุด"] = {"ราคา": q(peg, 2), "มูลค่าจริง": q(cash_close * peg, 2),
                      "หายไป": q(cash_close * (1 - peg), 2)}
    # Isolated / Cross: กติกาบท 4 (Initial 10,300 · Maintenance 5,150 คงที่) · กระเป๋ารวม = Margin + Free Cash
    im, fc = D(m["ทุนภาค1"]["หลักประกัน"]), D(m["ทุนภาค1"]["เงินสดอิสระ"])
    mm = im / 2                                            # 5,150 (บท 4)
    pool = im + fc                                         # 25,000
    f9 = D(113200)                                         # คืนวันที่ 9 (บท 4)
    other = D(15000)                                       # สถานะอื่นในบัญชีรวมขาดทุน (ตัวอย่างสอน)
    v2["แยกรวม"] = {"maintenance": q(mm, 0), "แตะแบบแยก": q(f0 + (im - mm), 0),
                     "กระเป๋ารวม": q(pool, 0), "ทนได้แบบรวม": q(pool - mm, 0), "แตะแบบรวม": q(f0 + pool - mm, 0),
                     "ขาดทุนคืนวันที่9": q(f9 - f0, 0), "เหลือคืนวันที่9": q(pool - (f9 - f0), 0),
                     "สถานะอื่นขาดทุน": q(other, 0), "เหลือหลังสถานะอื่น": q(pool - other, 0),
                     "ทนได้หลังสถานะอื่น": q(pool - other - mm, 0), "แตะหลังสถานะอื่น": q(f0 + pool - other - mm, 0)}
    # Haircut: เหรียญคืนวันที่ 9 (110,000) หัก 10% (ค่าสอน)
    coin9, hc = D(110000), D(10)
    v2["haircut"] = {"เปอร์เซ็นต์": int(hc), "มูลค่าเหรียญ": q(coin9, 0), "นับได้": q(coin9 * (100 - hc) / 100, 0),
                     "ส่วนที่หัก": q(coin9 * hc / 100, 0)}

    # ✍️ v2 (ห้าข้อ · แบบฝึกบันไดห้าขั้น)
    h3_ = D(3) / 100
    x2_opp = cap * h3_ * left / year                       # 616.44
    settle_fee = fee * s30                                 # ✍️ 3: ค่าชำระสัญญา 0.05% ที่ราคา 101,000
    x3_hold = hold_ledger - settle_fee                     # 2,797.50
    x3_extra = x3_hold - realised                          # 500.25
    x3_turn = x3_extra / cap * 100 * year / left
    # ✍️ 5 ถ่ายโอน: กองทุนดัชนี 2,100 · futures 2,105 · เหลือ 40 วัน · ค่าธรรมเนียมครั้งละ 1.5 · ทุน 2,500 · hurdle 4%
    t_basis, t_fee, t_cap, t_days = D(5), D("1.5"), D(2500), D(40)
    t_extra = t_basis + 2 * t_fee - t_fee
    t_opp = t_cap * hurdle * t_days / year
    t_turn_60 = t_extra / t_cap * 100
    v2["ฝึก"] = {
        "1": {"ค่าปิด": q(close_fee, 2), "ปิด": q(realised, 2), "ค่าถือ": q(hold_sale_fee_30, 2),
              "ถือ": q(hold_ledger, 2), "ต่าง": q(diff, 2), "ผิดเครื่องหมาย": q(D(d30["basis"]) - close_fee + hold_sale_fee_30, 2)},
        "2": {"hurdle": 3, "ต่อปี": q(cap * h3_, 0), "เสียโอกาส": q(x2_opp, 2), "ปิดดีกว่า": q(x2_opp - diff, 2)},
        "3": {"ค่าชำระ": q(settle_fee, 2), "ถือ": q(x3_hold, 2), "ถือได้เพิ่ม": q(x3_extra, 2),
              "ปิดดีกว่า": q(opp60 - x3_extra, 2), "จุดเปลี่ยนต่อ60วัน": q(x3_extra / cap * 100, 2),
              "จุดเปลี่ยน": q(x3_turn, 2)},
        "5": {"กองทุน": 2100, "futures": 2105, "basis": q(t_basis, 0), "ค่าธรรมเนียมครั้งละ": q(t_fee, 1), "ค่าปิดสองครั้ง": q(2 * t_fee, 0),
              "ถือได้เพิ่ม": q(t_extra, 1), "ทุน": q(t_cap, 0), "เสียโอกาสต่อปี": q(t_cap * hurdle, 0),
              "เสียโอกาส": q(t_opp, 2), "ปิดดีกว่า": q(t_opp - t_extra, 2),
              "จุดเปลี่ยนต่อ40วัน": q(t_turn_60, 2), "จุดเปลี่ยน": q(t_turn_60 * year / t_days, 2)},
    }
    out["_แบบฝึก"] = [
        {"โจทย์": "สมุดสองเล่มวันที่ 30: ค่าปิดสองขา · กำไรถ้าปิด · ค่าขายเหรียญถ้าถือ · กำไรถ้าถือ · ต่างกัน",
         "คำตอบ": [q(close_fee, 2), q(realised, 2), q(hold_sale_fee_30, 2), q(hold_ledger, 2), q(diff, 2)]},
        {"โจทย์": "วันที่ 30 ของมินแต่ hurdle 3% → ค่าเสียโอกาส 60 วัน และปิดดีกว่าเท่าไร",
         "คำตอบ": [q(x2_opp, 2), q(x2_opp - diff, 2)]},
        {"โจทย์": "exchange เก็บค่าชำระสัญญา 0.05% ที่ 101,000 → สมุดถือ · ถือได้เพิ่ม · ปิดดีกว่า · จุดเปลี่ยน hurdle",
         "คำตอบ": [q(x3_hold, 2), q(x3_extra, 2), q(opp60 - x3_extra, 2), q(x3_turn, 2)]},
        {"โจทย์": "วันที่ 30 แต่ hurdle 2% → ถือดีกว่าเท่าไร และเหลือเท่าไรถ้าขายเหรียญต่ำกว่าราคาชำระ 100",
         "คำตอบ": [q(e2_margin, 2), q(e2_after_gap, 2)]},
        {"โจทย์": "กองทุนดัชนี 2,100 futures 2,105 เหลือ 40 วัน ค่าธรรมเนียมครั้งละ 1.5 ทุน 2,500 hurdle 4% → ถือได้เพิ่ม · ค่าเสียโอกาส · จุดเปลี่ยน",
         "คำตอบ": [q(t_extra, 1), q(t_opp, 2), q(t_turn_60 * year / t_days, 2)]},
    ]
    out["_claims"].append(
        {"id": "ch06-collateral-rules",
         "ข้อความ": "exchange คริปโตหลายแห่งมีทั้งโหมดหลักประกันแยกต่อสถานะ (isolated) และแบบรวมทั้งบัญชี (cross) · "
                    "บางแห่งรับเหรียญเป็นหลักประกันโดยหักมูลค่าบางส่วน (haircut) และปรับอัตราหักได้เมื่อตลาดผันผวน — "
                    "อัตราและเงื่อนไขต่างกันตามแห่งและเปลี่ยนได้ เล่มใช้ค่าสอน (หัก 10%) ไม่อ้างกติกาของแห่งใด",
         "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [6]})
    return out
