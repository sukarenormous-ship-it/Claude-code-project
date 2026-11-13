"""บท 7 — Perp: เชือกที่ไม่มีวันล็อก · ค่าที่บทพิมพ์แต่ยังไม่มีใน JSON หลัก

ทุกค่าคำนวณจาก บัญชีมิน + ch00 (perp 100,050) + ch06 (มินปิด) + ch07 เดิม (สามรอบ · บันไดfunding · สี่เส้นทาง · fundingถูกแย่ง)
ตัวอย่าง funding: ราคา mark × อัตราของรอบ · รอบละ 8 ชั่วโมงในตัวอย่างนี้ (3 รอบต่อวัน) · 30 วัน = 90 รอบ
ค่าธรรมเนียม maker 0.02% (มินเปลี่ยนในบทนี้) · คอลัมน์ taker 0.05% · ทุน 125,000 เท่าบันได carry
อัตราต่อปีแบบ simple ทั้งบท ยกเว้น 🔎 (ทบต้น)
"""


def extend(data, D, q):
    m, c0, c6, c7 = data["บัญชีมิน"], data["ch00"], data["ch06"], data["ch07"]
    scale = D(str(m["สเกล"]))
    year = D(365)
    cap = D(m["ทุนภาค1"]["รวม"])
    hurdle = D(str(m["hurdle"]))
    maker = D(str(m["ค่าธรรมเนียม"]["maker"])) / 100
    taker = D(str(m["ค่าธรรมเนียม"]["taker"])) / 100
    rate = D(str(m["funding"]["ต่อรอบเปอร์เซ็นต์"]))
    hours = D(m["funding"]["ชั่วโมงต่อรอบในตัวอย่าง"])
    per_day = D(24) / hours                                   # 3 รอบต่อวัน
    days = D(30)
    rounds = per_day * days                                   # 90 รอบ
    mark = D(m["BTC"]["spot"])

    # ── สามรอบแรก (03.09 ครึ่งหลัง): ราคาและอัตราที่ตารางพิมพ์ ──
    s_open, p_open = mark, D(c0["บัตรตลาดมิน"]["perp"])        # 100,000 · 100,050
    s_close, p_close = D(99000), D(99020)                     # ราคาปิดสองขาของตัวอย่างต้นฉบับ
    marks3 = [D(100000), D(101000), D(99000)]
    rates3 = [D("0.01"), D("0.03"), D("-0.02")]
    fund3 = [mk * r / 100 for mk, r in zip(marks3, rates3)]
    spot_pnl, perp_pnl = s_close - s_open, p_open - p_close
    fee3 = maker * (s_open + p_open + s_close + p_close)
    net3 = sum(fund3) + spot_pnl + perp_pnl - fee3
    sam = c7["สามรอบ"]
    assert q(net3, 3) == sam["สุทธิ"], "สามรอบ: สุทธิไม่ตรง JSON หลัก"

    # ── บันได funding (เส้นทางราบ 30 วัน) ──
    fund_flat = mark * rate / 100 * rounds                    # 900
    fee_mk = D(c7["ค่าธรรมเนียมเปิดปิด"]["maker"])             # 80
    fee_tk = D(c7["ค่าธรรมเนียมเปิดปิด"]["taker"])             # 200
    opp30 = cap * hurdle / 100 * days / year
    net_flat = fund_flat - fee_mk

    def ann(x):
        return x / cap * year / days * 100

    # ── กฎออก "ติดลบ 3 รอบติดแล้วออก": รอบที่กฎทำงาน (นับจากเส้นสะสมในกราฟ) ──
    k = 3

    def exit_round(path):
        cum = path
        neg = 0
        for i in range(1, len(cum)):
            neg = neg + 1 if cum[i] < cum[i - 1] else 0
            if neg == k:
                return i + 1                                  # รอบที่ (นับจาก 1)
        return None

    g = c7["กราฟ"]
    ex_flip, ex_alt = exit_round(g["กลับขั้ว"]), exit_round(g["สลับ"])
    paths = c7["สี่เส้นทาง"]
    rule_flip, rule_alt = D(paths["กลับขั้ว"]["กฎmaker"]), D(paths["สลับ"]["กฎmaker"])
    hold_flip, hold_alt = D(paths["กลับขั้ว"]["สุทธิmaker"]), D(paths["สลับ"]["สุทธิmaker"])

    # ── บัญชีสะสมภาค 1 (สาธิต 1 BTC และของมิน) ──
    carry = D(str(c6["มินปิด"]["ต่อ1BTC"]))
    after3 = carry + net3
    after_flip = after3 + rule_flip
    after_alt = after_flip + rule_alt
    assert q(after_alt, 2) == c7["บัญชีสะสมภาค1"]["ต่อ1BTC"], "บัญชีสะสมภาค 1 ไม่ตรง"

    # ── มือที่แย่งเชือก: ส่วนเกินหลัง hurdle ของแต่ละอัตรา (maker) ──
    crowd = [{"ต่อรอบเปอร์เซ็นต์": r["ต่อรอบเปอร์เซ็นต์"],
              "fundingรวม": q(mark * D(str(r["ต่อรอบเปอร์เซ็นต์"])) / 100 * rounds, 2),
              "ส่วนเกินmakerเปอร์เซ็นต์": q(ann(mark * D(str(r["ต่อรอบเปอร์เซ็นต์"])) / 100 * rounds - fee_mk - opp30), 2)}
             for r in c7["fundingถูกแย่ง"]]

    # ── 🔎 ทบต้น: (1 + 0.01%) ยกกำลังจำนวนรอบในหนึ่งปี ──
    n_year = int(per_day * year)                              # 1,095 รอบ
    comp = ((1 + rate / 100) ** n_year - 1) * 100

    # ── ✍️ ข้อ 1: อัตรา +0.02% ต่อรอบ · mark 100,000 · maker 80 · 90 รอบ ──
    r1 = D("0.02")
    per1 = mark * r1 / 100
    net1 = per1 * rounds - fee_mk
    # ── ✍️ ข้อ 2: ถือ 20 รอบที่ +0.01% แล้วติดลบ −0.01% สองรอบ · ออกตอนนี้ vs รอรอบที่สาม ──
    per_round = mark * rate / 100
    got2 = per_round * 20 - per_round * 2
    now2 = got2 - fee_mk
    wait_neg = got2 - per_round - fee_mk
    # ── ✍️ ข้อ 3: exchange ที่รอบละ 4 ชั่วโมงในตัวอย่าง · อัตราต่อรอบเท่าเดิม 0.01% ──
    per_day4 = D(24) / D(4)
    screen4 = rate * per_day4 * year

    return {
        "สามรอบเพิ่ม": {
            "spotเปิด": q(s_open, 0), "perpเปิด": q(p_open, 0), "spotปิด": q(s_close, 0), "perpปิด": q(p_close, 0),
            "basisเปิด": q(p_open - s_open, 0), "basisปิด": q(p_close - s_close, 0),
            "mark": [q(x, 0) for x in marks3], "อัตราเปอร์เซ็นต์": [float(x) for x in rates3],
            "กำไรspot": q(spot_pnl, 0), "กำไรperp": q(perp_pnl, 0),
            "ค่าธรรมเนียมปัด": q(fee3, 2), "สุทธิปัด": q(net3, 2), "fundingรวมปัด": q(sum(fund3), 2),
        },
        "รอบ": {"ชั่วโมงต่อรอบ": int(hours), "ต่อวัน": int(per_day), "ใน30วัน": int(rounds), "fundingต่อรอบ": q(per_round, 0)},
        "บันไดเงิน": {"fundingราบ30วัน": q(fund_flat, 0), "สุทธิmaker": q(net_flat, 0),
                      "ค่าเสียโอกาส30วัน": q(opp30, 2), "ส่วนเกิน": q(net_flat - opp30, 2)},
        "กฎออก": {"รอบติดลบ": k, "รอบที่ออกกลับขั้ว": ex_flip, "รอบที่ออกสลับ": ex_alt,
                  "กลับขั้วต่างจากถือ": q(rule_flip - hold_flip, 0), "สลับต่างจากถือ": q(rule_alt - hold_alt, 0),
                  "มินสองเดือน": q(rule_flip + rule_alt, 0), "ต้นสองเดือน": q(hold_flip + hold_alt, 0),
                  "สลับสองเดือนตามกฎ": q(2 * rule_alt, 0), "สลับสองเดือนถือ": q(2 * hold_alt, 0)},
        "แย่งหลังhurdle": crowd,
        "บัญชีเดิน": {"หลังสามรอบ": q(after3, 2), "หลังกลับขั้ว": q(after_flip, 2), "หลังสลับ": q(after_alt, 2)},
        "ของมิน": {
            "mark": q(mark * scale, 0), "fundingต่อรอบ": q(per_round * scale, 2),
            "ค่าธรรมเนียมmaker": q(fee_mk * scale, 2), "ค่าธรรมเนียมtaker": q(fee_tk * scale, 2),
            "ปิดcarry": q(carry * scale, 2), "สามรอบ": q(net3 * scale, 2), "เดือนกลับขั้ว": q(rule_flip * scale, 2),
            "เดือนสลับ": q(rule_alt * scale, 2), "หลังสามรอบ": q(after3 * scale, 2),
            "หลังกลับขั้ว": q(after_flip * scale, 2), "หลังสลับ": q(after_alt * scale, 2),
            "fundingราบ30วัน": q(fund_flat * scale, 2), "สุทธิราบ": q(net_flat * scale, 2),
            "เงินบนexchange": q(cap * scale, 0), "บัญชีทดลอง": q(D(-120) * scale, 2),
            "fundingสามรอบ": q(sum(fund3) * scale, 2), "ราคาสามรอบ": q((spot_pnl + perp_pnl) * scale, 2),
            "ค่าธรรมเนียมสามรอบ": q(fee3 * scale, 2),
        },
        "ทบต้นต่อปีเปอร์เซ็นต์": q(comp, 2), "รอบต่อปี": n_year,
        "_claims": [
            {"id": "ch07-funding-long-demand",
             "ข้อความ": "ฝั่ง long perp จ่าย funding เมื่ออัตราเป็นบวก เพราะอยากได้กำไรขาดทุนตามราคา BTC ด้วยหลักประกันน้อยโดยไม่มีวันหมดอายุ · อัตรามักสูงเมื่อคนอยาก long มาก และติดลบได้เมื่อฝั่ง short มากกว่า — ไม่มีสัญญาใดล็อกอัตรารอบหน้า",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [7]},
            {"id": "ch07-funding-crowding",
             "ข้อความ": "เมื่อคนทำ funding carry (ถือ spot + short perp) มากขึ้น แรง short perp ดันราคา perp เข้าหา spot และอัตรา funding ลดลง · ตัวเลข 0.01 → 0.005 → 0.003% ต่อรอบในบท 7 เป็นตัวเลขสมมติ ไม่ใช่ข้อมูลตลาด",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [7]},
            {"id": "ch07-adl-insurance",
             "ข้อความ": "exchange perp หลายแห่งใช้กองทุนประกันรับส่วนขาดเมื่อสถานะที่ถูกบังคับปิดมีหลักประกันไม่พอ และเมื่อกองทุนไม่พอ ใช้การปิดอัตโนมัติ (ADL) กับสถานะฝั่งตรงข้ามที่กำไร · ลำดับ เงื่อนไข และการแจ้งเตือนต่างกันตาม exchange ต้องอ่านจากเอกสาร",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [7]},
            {"id": "ch07-funding-formula-cap",
             "ข้อความ": "สูตร funding ของ perp มักคิดจากระยะห่างระหว่างราคา perp กับดัชนี spot บวกส่วนดอกเบี้ย และมีเพดานต่อรอบ · exchange เปลี่ยนสูตร ความถี่ หรือเพดานได้ — ตัวเลขจริงต้องจดจากเอกสารสัญญา เล่มไม่อ้างกติกาของ exchange ใด",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [7]},
            {"id": "ch07-reverse-borrow",
             "ข้อความ": "เมื่อ funding ติดลบ การกลับทิศ (short spot + long perp) ต้องยืมเหรียญมาขาย ซึ่งยืมไม่ได้เสมอ มีค่ายืม และถูกเรียกคืนได้ · กลยุทธ์จึงไม่สมมาตร: ฝั่งรับ funding บวกทำง่ายกว่าฝั่งรับ funding ลบ",
             "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [7, 18]},
        ],
        "_แบบฝึก": [
            {"โจทย์": "อัตรา +0.02% ต่อรอบ ราคา mark 100,000 ค่าธรรมเนียม maker 80 ถือ 90 รอบ — สุทธิเท่าไร", "คำตอบ": float(q(net1, 0))},
            {"โจทย์": "ถือ 20 รอบที่ +0.01% แล้วติดลบ −0.01% สองรอบติด ค่าธรรมเนียม 80 — ถ้าออกตอนนี้ได้สุทธิเท่าไร", "คำตอบ": float(q(now2, 0))},
            {"โจทย์": "exchange ที่รอบละ 4 ชั่วโมงในตัวอย่าง อัตรา 0.01% ต่อรอบ — อัตราบนจอต่อปีแบบ simple กี่ %", "คำตอบ": float(q(screen4, 2))},
        ],
        "แบบฝึกค่า": {
            "ข้อ1": {"อัตรา": float(r1), "ต่อรอบ": q(per1, 0), "รอบพอค่าธรรมเนียม": q(fee_mk / per1, 0),
                     "fundingรวม": q(per1 * rounds, 0), "สุทธิ": q(net1, 0), "ต่อปีของทุน": q(ann(net1), 2),
                     "ส่วนเกิน": q(ann(net1 - opp30), 2)},
            "ข้อ2": {"ได้แล้ว": q(got2, 0), "ออกตอนนี้": q(now2, 0), "รอแล้วติดลบอีก": q(wait_neg, 0),
                     "ต่างกัน": q(now2 - wait_neg, 0)},
            "ข้อ3": {"รอบต่อวัน": int(per_day4), "ต่อวัน": q(per_round * per_day4, 0), "บนจอ": q(screen4, 2)},
        },
    }
