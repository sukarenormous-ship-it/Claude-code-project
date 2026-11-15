"""บท 11 — สมุดบัญชีของคู่ · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py)

ทุกค่าคำนวณจาก data["ch11"] (บัญชีกระดาษ 03.02–03.07) และ data["บัญชีมิน"] — ไม่มีผลลัพธ์พิมพ์ลอย
บัญชีกระดาษไม่เข้าบัญชีคู่ (คัมภีร์เรื่อง part11)
"""


def _v2(data, D, q, nA, nB, pA0, pB0, h, sets, cap):
    """ฐานต้นทุนเดียวของบท 11–15 (แผน 14.5 · รายงาน B S8/S9 · รายงาน A ข้อ 22)

    แบบจำลองต้นทุน: ค่าธรรมเนียม taker ของบท 1 (บัญชีมิน.ค่าธรรมเนียม.taker = 0.05%) × มูลค่าที่ซื้อขายของแต่ละ fill
    · ไปกลับหนึ่งครั้งของคู่ = 4 fill (เข้า A · เข้า B · ออก A · ออก B) · คิดทุก fill ที่มูลค่าตอนตั้งคู่ขาละ 1,000
      (A 100 × 10 · B 50 × 20) — มูลค่าจริงของ fill อยู่ราว 1,000–1,041 ในบท 11–16 ค่าธรรมเนียมต่างไม่ถึง 0.03 ต่อ fill เล่มจึงปัดเป็นเลขเดียว
      (บท 16 กระทบยอดกับมูลค่าจริง: 2.01 · 2.02 · 2.03 ต่อไม้)
    · ราคาที่ได้แย่กว่าราคากลาง (ส่วนต่างราคาซื้อ-ขาย · กินกระดาน) ไม่อยู่ในต้นทุนนี้ — แยกเป็นชั้นของตัวเองในบท 15 (สะพาน)
      และบท 16 (เดินกระดาน) · funding เป็นบรรทัดแยก (ค่าถือขา short · บวกเมื่อรับ)
    ทำไม taker: การ์ดบท 12 ออกเพราะงบ/เวลา ต้องได้ทันที และ maker เสี่ยงได้ขาเดียว (บท 16) — ต้นทุนในการ์ดต้องเป็นของคำสั่งที่กดจริง

    บัญชีกระดาษบท 11 v2: ราคาออก A 102 · B 50.95 (เดิม 50.5) ให้ X ขยับแค่ 0.1 — บทเรียน "ถูกทางแต่ขาดทุน" ยังจริงด้วยต้นทุน 2
    """
    m = data["บัญชีมิน"]
    rate = D(str(m["ค่าธรรมเนียม"]["taker"]))               # 0.05 (%)
    leg = nA * pA0                                           # 1,000 (= −nB × pB0)
    assert leg == -nB * pB0
    fills = 4
    per_fill = rate / 100 * leg                              # 0.5
    entry = 2 * per_fill                                     # 1.0
    exit_ = 2 * per_fill                                     # 1.0
    rt = entry + exit_                                       # 2.0
    gross = 2 * leg                                          # 2,000
    cost = {"อัตราtakerเปอร์เซ็นต์": q(rate, 2), "มูลค่าต่อfill": q(leg, 0), "จำนวนfill": fills,
            "ต่อfill": q(per_fill, 1), "เข้า": q(entry, 0), "ออก": q(exit_, 0), "ไปกลับ": q(rt, 0),
            "ต่อชุด": q(rt / sets, 1), "ต่อgrossเปอร์เซ็นต์": q(rt / gross * 100, 2),
            "ต่อgross": q(gross, 0),
            "กติกา": "ค่าธรรมเนียม taker 0.05% × มูลค่าที่ซื้อขายต่อ fill · 4 fill ต่อไปกลับ · คิดที่ขาละ 1,000 · "
                     "ไม่รวมราคาที่แย่กว่าราคากลาง (บท 15–16) · funding แยกบรรทัด"}

    # บัญชีกระดาษ v2: A 100 → 102 · B 50 → 50.95
    pA1, pB1 = D(102), D("50.95")
    legA, legB = nA * (pA1 - pA0), nB * (pB1 - pB0)          # +20 · −19
    price = legA + legB                                      # +1
    X0, X1 = pA0 - h * pB0, pA1 - h * pB1                    # 0 · 0.1
    assert sets * (X1 - X0) == price
    net = price - rt                                         # −1
    # เงินสด (บัญชีกระดาษแบบบท 11: ขาย short ได้เงินสด) · ค่าธรรมเนียมตอนเข้าแล้วตอนออก
    cash0 = cap                                              # 1,000
    cash_after_buyA = cash0 - nA * pA0                       # 0
    cash_after_shortB = cash_after_buyA - nB * pB0           # 1,000
    cash_after_entry_fee = cash_after_shortB - entry         # 999
    hold_new = nA * pA1 + nB * pB1                           # 1,020 − 1,019 = 1
    eq_new = cash_after_entry_fee + hold_new                 # 1,000
    cash_after_close = cash_after_entry_fee + hold_new       # 1,000 (ขาย A รับ 1,020 · ซื้อคืน B จ่าย 1,019)
    cash_end = cash_after_close - exit_                      # 999
    assert cash_end - cash0 == net
    # ค่าธรรมเนียมจริงตอนออก (ไม่ปัด) ไว้ตรวจว่าปัดได้
    exit_exact = rate / 100 * (nA * pA1 + (-nB) * pB1)       # 0.51 + 0.5095
    paper = {
        "ราคาออก": {"A": q(pA1, 0), "B": q(pB1, 2)},
        "Bเปลี่ยน": q(pB1 - pB0, 2), "Aเปลี่ยน": q(pA1 - pA0, 0),
        "ขา": {"A": q(legA, 0), "B": q(legB, 0)}, "กำไรจากราคา": q(price, 0),
        "Xก่อนหลัง": [q(X0, 0), q(X1, 1)], "Xเปลี่ยน": q(X1 - X0, 1),
        "มูลค่าที่ราคาใหม่": {"A": q(nA * pA1, 0), "B": q(nB * pB1, 0), "สุทธิ": q(hold_new, 0)},
        "equityก่อนต้นทุน": q(cash0 + price, 0),
        "เงินสดระหว่างทาง": [q(cash0, 0), q(cash_after_buyA, 0), q(cash_after_shortB, 0),
                             q(cash_after_entry_fee, 0), q(cash_after_close, 0), q(cash_end, 0)],
        "equityหลังจ่ายค่าเข้า": q(cash_after_entry_fee + nA * pA0 + nB * pB0, 0),
        "equityที่ราคาใหม่หลังค่าเข้า": q(eq_new, 0),
        "ค่าธรรมเนียมออกไม่ปัด": q(exit_exact, 2), "ไปกลับไม่ปัด": q(entry + exit_exact, 2),
        "สุทธิไม่ปัด": q(price - entry - exit_exact, 2),
        "funding": 0, "สุทธิ": q(net, 0),
        "สุทธิต่อทุนเปอร์เซ็นต์": q(net / cap * 100, 1), "สุทธิต่อgrossเปอร์เซ็นต์": q(net / gross * 100, 2),
        "กำไรจากราคาต่อgrossเปอร์เซ็นต์": q(price / gross * 100, 2),
        "เทียบXขยับ1": {"กำไรจากราคา": q(sets * 1, 0), "สุทธิ": q(sets * 1 - rt, 0)},
    }
    # ✍️ (ก) v2: A 99 · B 49.5 · ต้นทุน 2 → ราคาให้ 0 · สุทธิ −2
    a_A, a_B = pA0 - 1, D("49.5")
    ex_a = {"ขาA": q(nA * (a_A - pA0), 0), "ขาB": q(nB * (a_B - pB0), 0),
            "กำไรจากราคา": q(nA * (a_A - pA0) + nB * (a_B - pB0), 0), "สุทธิ": q(nA * (a_A - pA0) + nB * (a_B - pB0) - rt, 0)}

    # ภาคผนวก F §3 — ขาที่สาม: dollar-neutral + beta-neutral พร้อมกัน
    bA, bB = D(str(m["beta"]["A"])), D(str(m["beta"]["B"]))   # 1.5 · 1.0
    bBTC = D(1)
    dA = leg                                                 # +1,000 (ถือ A ไว้เหมือนคู่เดิม)
    pair_beta = bA * dA + bB * (-leg)                        # +500
    third = {"betaA": float(bA), "betaB": float(bB), "betaBTC": float(bBTC), "ขาA": q(dA, 0),
             "betaexposureคู่": q(pair_beta, 0),
             # (ก) BTC เป็นขาที่สาม: dA + dB + dM = 0 · 1.5dA + dB + dM = 0 → ลบกัน 0.5 dA = 0
             "BTC": {"ผลต่างbeta": q(bA - bB, 1), "สมการลบกัน": "0.5 × ขา A = 0 → ขา A ต้องเป็น 0",
                     "กันbetaอย่างเดียว_shortBTC": q(-pair_beta / bBTC, 0),
                     "กันbetaอย่างเดียว_มูลค่าสุทธิ": q(dA - leg - pair_beta / bBTC, 0),
                     "ปรับBอย่างเดียว_B": q(-bA * dA / bB, 0),
                     "ปรับBอย่างเดียว_มูลค่าสุทธิ": q(dA - bA * dA / bB, 0),
                     "สองทางได้เมื่อไม่มีA_B": q(leg, 0), "สองทางได้เมื่อไม่มีA_BTC": q(-leg, 0)}}
    # (ข) เหรียญ C ที่ beta ต่างจาก B: dC = −(βA − βB) dA ÷ (βC − βB) · dB = −dA − dC
    for bc in ("2.0", "0.5"):
        bC = D(bc)
        dC = -(bA - bB) * dA / (bC - bB)
        dB = -dA - dC
        assert dA + dB + dC == 0 and bA * dA + bB * dB + bC * dC == 0
        third[f"C_beta{bc}"] = {"betaC": float(bC), "ขาC": q(dC, 0), "ขาB": q(dB, 0),
                                "betaexposure": q(bA * dA + bB * dB + bC * dC, 0),
                                "มูลค่าสุทธิ": q(dA + dB + dC, 0),
                                "gross": q(abs(dA) + abs(dB) + abs(dC), 0),
                                "betaของC_ขาC": q(bC * dC, 0), "betaของB_ขาB": q(bB * dB, 0)}
    third["สูตรขาC"] = "ขา C = −500 ÷ (beta C − 1) · ขา B = −1,000 − ขา C · beta C = 1 (BTC) หารด้วยศูนย์ = ไม่มีคำตอบ"
    # ปรับ hedge (h 2 → 1.8 · ซื้อคืน B 2 เหรียญที่ 50) ด้วยอัตราเดียวกัน: 0.05% × 100 = 0.05 (เดิมพิมพ์ 1)
    reb_val = 2 * pB0
    reb_fee = rate / 100 * reb_val
    rebalance = {"มูลค่าที่ซื้อคืน": q(reb_val, 0), "ค่าธรรมเนียม": q(reb_fee, 2), "equityหลังค่าธรรมเนียม": q(cap - reb_fee, 2)}
    return {"ต้นทุน": cost, "กระดาษ": paper, "แบบฝึกก": ex_a, "ขาที่สาม": third, "ปรับhedge": rebalance}


def _v2_teach(data, D, q, nA, nB, pA0, pB0, h, sets, cap):
    """ผลกลางทางที่บท 11 v2 แสดงการคิด (คู่มือ v2 §4 · รายงาน B S7/S8/3.3/3.4 · รายงาน A บท 11) — ใต้ ch11.v2.*

    ทุกค่าคำนวณจากบัญชีมิน ch09 และค่าคงที่ของการสอนที่ประกาศในฟังก์ชันนี้ · assert ให้ตรงกับคีย์เดิมที่หน้าอื่นใช้
    """
    m = data["บัญชีมิน"]
    rate = D(str(m["ค่าธรรมเนียม"]["taker"]))                 # 0.05 (%)
    leg = nA * pA0                                             # 1,000
    per_fill = rate / 100 * leg                                # 0.5
    pA1, pB1 = D(102), D("50.95")
    out = {}

    # ── ตอน ก · 1 — X ตอนออกทีละขั้น (2 × 50.95 = 101.9 · 102 − 101.9 = 0.1)
    out["Xออก"] = {"สองB": q(h * pB1, 1), "X": q(pA1 - h * pB1, 1), "สองBเปิด": q(h * pB0, 0)}

    # ── ตอน ก · 2 — h มาได้สองทาง: มูลค่าเท่ากัน (2) vs จากข้อมูล 20 วันของบท 9 (≈ 2.5)
    c9 = data["ch09"]["นับมือ20วัน"]
    A = [D(str(v)) for v in c9["A"]]
    Bp = [D(str(v)) for v in c9["B"]]
    # วิธีมือ: วันที่ 2–11 (ตารางนับทิศของบท 9) A ขยับรวมกี่ดอลลาร์ (ไม่สนเครื่องหมาย) เทียบ B
    dA = [abs(A[i] - A[i - 1]) for i in range(1, 11)]
    dB = [abs(Bp[i] - Bp[i - 1]) for i in range(1, 11)]
    sA, sB = sum(dA), sum(dB)                                  # 9.4 · 3.7
    # สเปรดชีต SLOPE(ราคา A 20 วัน, ราคา B 20 วัน) = เส้นตรงที่ใกล้จุดราคาที่สุด
    mA, mB = sum(A) / len(A), sum(Bp) / len(Bp)
    slope = sum((a - mA) * (b - mB) for a, b in zip(A, Bp)) / sum((b - mB) ** 2 for b in Bp)
    hfit = D("2.5")
    assert abs(sA / sB - hfit) < D("0.1") and abs(slope - hfit) < D("0.1")
    bA, bB = D(str(m["beta"]["A"])), D(str(m["beta"]["B"]))

    def holding(hh):
        nb = -hh * nA
        vb = -nb * pB0
        return {"h": q(hh, 1), "B": q(nb, 0), "มูลค่าB": q(vb, 0), "มูลค่าสุทธิ": q(leg - vb, 0),
                "gross": q(leg + vb, 0), "betaexposure": q(bA * leg - bB * vb, 0), "Xวันนี้": q(pA0 - hh * pB0, 0),
                "hคูณB": q(hh * pB0, 0)}
    out["hสองทาง"] = {"วันมือ": "2–11", "Aขยับรวม": q(sA, 1), "Bขยับรวม": q(sB, 1), "อัตราส่วนมือ": q(sA / sB, 2),
                      "SLOPE20วัน": q(slope, 2), "hจากข้อมูล": q(hfit, 1),
                      "มูลค่าเท่ากัน": holding(h), "จากข้อมูล": holding(hfit),
                      "ตัวอย่างวัน2": {"A": q(A[1] - A[0], 1), "B": q(Bp[1] - Bp[0], 1)}}

    # ── ตอน ก · 3 — ตารางคู่แบบ perp: หลักประกัน 10% (กติกาของเล่ม บท 3–4) ของขา B มาจากเงินบน exchange นอกทุนคู่
    mr = D(str(m["กติกาหลักประกันเปอร์เซ็นต์"]))               # 10
    margin = mr / 100 * leg                                    # 100
    start = cap + margin                                       # 1,100
    upnl = nB * (pB1 - pB0)                                    # −19
    eq_mark = (start - leg - margin) + nA * pA1 + margin + upnl
    assert eq_mark - start == nA * (pA1 - pA0) + upnl
    b_wipe = pB0 + margin / (-nB)                              # 55: ขาดทุนค้างขา B = หลักประกันทั้งก้อน
    out["perp"] = {"หลักประกันเปอร์เซ็นต์": q(mr, 0), "หลักประกัน": q(margin, 0), "เริ่ม": q(start, 0),
                   "เงินสดหลังซื้อA": q(start - leg, 0), "เงินสดหลังวางหลักประกัน": q(start - leg - margin, 0),
                   "มูลค่าAใหม่": q(nA * pA1, 0), "ขาดทุนค้างB": q(upnl, 0), "equityที่ราคาใหม่": q(eq_mark, 0),
                   "เงินสดหลังปิด": q(eq_mark, 0), "equityเปลี่ยน": q(eq_mark - start, 0),
                   "Bที่กินหลักประกันหมด": q(b_wipe, 0), "ขาดทุนที่Bนั้น": q(nB * (b_wipe - pB0), 0),
                   "Bขึ้นต่อเหรียญ": q(b_wipe - pB0, 0)}

    # ── ตอน ก · 4 — สมุดทีละ fill (แบบกระดาษ: ขาย short ได้เงินสด) · ส่งขา short ก่อนให้เงินสดไม่ติดลบ
    vals = [(-nB) * pB0, nA * pA0, nA * pA1, (-nB) * pB1]       # 1,000 · 1,000 · 1,020 · 1,019
    signs = [1, -1, 1, -1]                                     # รับ · จ่าย · รับ · จ่าย
    cash, walk = cap, []
    for v, s in zip(vals, signs):
        cash = cash + s * v - per_fill
        walk.append(q(cash, 1))
    assert cash == cap + nA * (pA1 - pA0) + nB * (pB1 - pB0) - 4 * per_fill
    exact = [q(rate / 100 * v, 2) for v in vals]
    out["fill"] = {"มูลค่า": [q(v, 0) for v in vals], "ค่าธรรมเนียม": q(per_fill, 1),
                   "เงินสดหลังfill": [float(w) if w != int(w) else int(w) for w in walk],
                   "ค่าธรรมเนียมจริง": [float(e) for e in exact],
                   "ส่วนต่างจากปัดรวม": q(sum(rate / 100 * v for v in vals) - 4 * per_fill, 2)}

    # ── ตอน ข · 3 — สี่คำถามของราคาคู่เดียว: A 100 · B 47.5 → X 5 · ไม้บรรทัด Mean 0 · SD 1 แล้ว SD ใหม่ 2.5
    qB = D("47.5")
    x5 = pA0 - h * qB
    sd0, sd1 = D(1), D("2.5")
    assert x5 == D(str(data["ch11"]["sdเปลี่ยน"]["X"][0]))
    out["สี่คำถาม"] = {"A": q(pA0, 0), "B": q(qB, 1), "สองB": q(h * qB, 0), "X": q(x5, 0), "ห่างMean": q(x5, 0),
                       "z": q(x5 / sd0, 0), "zใหม่": q(x5 / sd1, 0), "sdใหม่": q(sd1, 1),
                       "เงินเมื่อXขยับ1": q(sets, 0), "เงินเมื่อzขยับ1_sd1": q(sets * sd0, 0),
                       "เงินเมื่อzขยับ1_sdใหม่": q(sets * sd1, 0), "ขาAเมื่อAขยับ1": q(nA, 0)}

    # ── ตอน ข · 3 — ได้ B ไม่ครบ: ได้ 10 จาก 20 แล้วราคาเดินแบบกระดาษ
    nBp = nB / 2
    legBp = nBp * (pB1 - pB0)
    out["ได้ไม่ครบ"] = {"Bได้": q(nBp, 0), "ขาB": q(legBp, 1), "ขาA": q(nA * (pA1 - pA0), 0),
                        "รวม": q(nA * (pA1 - pA0) + legBp, 1), "ตามX": q(sets * (pA1 - h * pB1 - (pA0 - h * pB0)), 0)}

    # ── ✍️ ห้าข้อ
    e1A, e1B = D("101.5"), D("50.5")
    e1 = {"A": q(e1A, 1), "B": q(e1B, 1), "ขาA": q(nA * (e1A - pA0), 0), "ขาB": q(nB * (e1B - pB0), 0),
          "กำไรจากราคา": q(nA * (e1A - pA0) + nB * (e1B - pB0), 0), "Xหลัง": q(e1A - h * e1B, 1),
          "สองB": q(h * e1B, 0)}
    e1["สุทธิ"] = q(D(str(e1["กำไรจากราคา"])) - 4 * per_fill, 0)
    rate2 = D("0.1")
    f2 = rate2 / 100 * leg
    price = nA * (pA1 - pA0) + nB * (pB1 - pB0)
    e2 = {"อัตรา": q(rate2, 1), "ต่อfill": q(f2, 0), "ไปกลับ": q(4 * f2, 0), "สุทธิ": q(price - 4 * f2, 0),
          "คุ้มทุนต่อชุด": q(4 * f2 / sets, 1)}
    a1, a2, b1, b2 = A[0], A[1], Bp[0], Bp[1]
    nB3 = -hfit * nA
    e3 = {"B": q(nB3, 0), "ขาA": q(nA * (a2 - a1), 0), "ขาB": q(nB3 * (b2 - b1), 1),
          "รวม": q(nA * (a2 - a1) + nB3 * (b2 - b1), 1), "รวมh2": q(nA * (a2 - a1) + nB * (b2 - b1), 0),
          "ต่อชุด": q((a2 - a1) - hfit * (b2 - b1), 2)}
    pP0, pP1, pQ0, pQ1, comm, borrow = D(80), D(82), D(40), D("40.5"), D("0.1"), D("0.5")
    nP, nQ = D(10), D(-20)
    legv = nP * pP0
    e5 = {"P": [q(pP0, 0), q(pP1, 0)], "Q": [q(pQ0, 0), q(pQ1, 1)], "มูลค่าขา": q(legv, 0),
          "ขาP": q(nP * (pP1 - pP0), 0), "ขาQ": q(nQ * (pQ1 - pQ0), 0),
          "กำไรจากราคา": q(nP * (pP1 - pP0) + nQ * (pQ1 - pQ0), 0),
          "ค่านายหน้าต่อครั้ง": q(comm / 100 * legv, 1), "ค่านายหน้ารวม": q(4 * comm / 100 * legv, 1),
          "ค่ายืม": q(borrow, 1), "สองQ": q(2 * pQ1, 0), "Xหลัง": q(pP1 - 2 * pQ1, 0)}
    e5["สุทธิ"] = q(D(str(e5["กำไรจากราคา"])) - 4 * comm / 100 * legv - borrow, 1)
    # เฉลยที่วินิจฉัยได้: ตัวเลขของคำตอบผิดที่พบบ่อย
    e5["ผิด_ลืมค่ายืม"] = q(D(str(e5["กำไรจากราคา"])) - 4 * comm / 100 * legv, 1)
    e5["ผิด_สองครั้ง"] = q(D(str(e5["กำไรจากราคา"])) - 2 * comm / 100 * legv - borrow, 1)
    e3["ผิด_บวกขาB"] = q(nA * (a2 - a1) - nB3 * (b2 - b1), 1)
    e1["ผิด_บวกขาB"] = q(nA * (e1A - pA0) - nB * (e1B - pB0), 0)
    out["แบบฝึก"] = {"1": e1, "2": e2, "3": e3, "5": e5}
    return out


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
    c = data["ch11"]
    m = data["บัญชีมิน"]
    nA, nB = D(str(c["เปิด"]["A"]["จำนวน"])), D(str(c["เปิด"]["B"]["จำนวน"]))
    pA0, pB0 = D(str(c["เปิด"]["A"]["ราคา"])), D(str(c["เปิด"]["B"]["ราคา"]))
    pA1, pB1 = D(str(c["ราคาใหม่"]["A"])), D(str(c["ราคาใหม่"]["B"]))
    h = D(str(m["คู่"]["h"]))
    sets = D(str(c["เปิด"]["ชุด"]))
    gross, cost, price = D(str(c["gross"])), D(str(c["ต้นทุน"]["รวม"])), D(str(c["กำไรจากราคา"]))
    cap = D(str(c["เปิด"]["ทุน"]))
    assert nA * (pA1 - pA0) + nB * (pB1 - pB0) == price
    assert sets * ((pA1 - h * pB1) - (pA0 - h * pB0)) == price

    def X(a, b, hh=h):
        return a - hh * b

    # 🛑 ทาย: B ลดเป็น 49.5 แทน (A ยัง 102) — 03.03 ย่อหน้าท้าย
    pB_guess = pB0 - (pB1 - pB0)
    legB_guess = nB * (pB_guess - pB0)

    # ✍️ (ก) ราคาลงทั้งคู่ A 99 · B 49.5 (03.11 ข้อ 1) + ต้นทุน 12
    a_A, a_B = pA0 - 1, pB_guess
    ex_a = {"A": q(a_A, 0), "B": q(a_B, 1), "ขาA": q(nA * (a_A - pA0), 0), "ขาB": q(nB * (a_B - pB0), 0)}
    ex_a["กำไรจากราคา"] = q(D(str(ex_a["ขาA"])) + D(str(ex_a["ขาB"])), 0)
    ex_a["Xหลัง"] = q(X(a_A, a_B), 0)
    ex_a["สุทธิ"] = q(D(str(ex_a["กำไรจากราคา"])) - cost, 0)

    # ✍️ (ข) h 2 → 2.2 ราคาเท่าเดิม (03.11 ข้อ 3)
    h2 = D("2.2")
    nB2 = -(h2 * nA)
    cash2 = cap + (nB - nB2) * pB0            # short B เพิ่ม → รับเงินขายเพิ่ม (บัญชีแบบง่าย)
    hold2 = nA * pA0 + nB2 * pB0
    ex_b = {"hใหม่": float(h2), "Xใหม่": q(X(pA0, pB0, h2), 0), "กำไร": 0, "Bเป้า": q(nB2, 0),
            "ขายBเพิ่ม": q(nB - nB2, 0), "เงินสดหลังปรับ": q(cash2, 0), "มูลค่าถือ": q(hold2, 0),
            "equity": q(cash2 + hold2, 0), "กำไรที่จดผิด": q(sets * X(pA0, pB0, h2), 0)}

    # ✍️ (ค) วาดสัดส่วนแทน X (02.06) — ใช้ค่า ch11.สัดส่วนกับตะกร้า
    r = c["สัดส่วนกับตะกร้า"]
    ex_c_profit = sum(D(str(w)) * (D(str(p1)) - D(str(p0)))
                      for w, (p0, p1) in zip(r["ถือ"], (r["A"], r["B"])))
    assert ex_c_profit == D(str(r["กำไร"]))

    # ✍️ (ค) ชุดเลขของบทนี้ (บท 9 ใช้ 105/54 · 50/25 แล้ว — บทนี้ใช้ชุดใหม่ไม่ให้โจทย์ซ้ำ)
    A0, A1, B0_, B1_ = D(108), D(56), D(50), D(25)
    ex_c = {"A": [int(A0), int(A1)], "B": [int(B0_), int(B1_)],
            "สัดส่วน": [q(A0 / B0_, 2), q(A1 / B1_, 2)], "X": [int(A0 - 2 * B0_), int(A1 - 2 * B1_)],
            "ขาA": int(A1 - A0), "ขาB": int(-2 * (B1_ - B0_)), "กำไร": int((A1 - A0) - 2 * (B1_ - B0_))}
    assert ex_c["กำไร"] == ex_c["X"][1] - ex_c["X"][0]

    half = {"A": q(nA / 2, 0), "B": q(nB / 2, 0), "ชุด": q(sets / 2, 0), "กำไร": q(price / 2, 0)}

    v2 = _v2(data, D, q, nA, nB, pA0, pB0, h, sets, cap)
    teach = _v2_teach(data, D, q, nA, nB, pA0, pB0, h, sets, cap)
    assert not set(teach) & set(v2)
    v2 = _ints({**v2, **teach})

    return {
        "v2": v2,
        "ฝึกสัดส่วน": ex_c,
        "มูลค่าที่ราคาใหม่": {"A": q(nA * pA1, 0), "B": q(nB * pB1, 0), "สุทธิ": q(nA * pA1 + nB * pB1, 0)},
        "จำนวนAจากทุน": q(cap / pA0, 0),
        "มูลค่าขาB": q(-nB * pB0, 0),
        "Xเปลี่ยน": q(X(pA1, pB1) - X(pA0, pB0), 0),
        "ทาย": {"Bใหม่": q(pB_guess, 1), "ขาB": q(legB_guess, 0),
                 "กำไร": q(nA * (pA1 - pA0) + legB_guess, 0)},
        "ครึ่งขนาด": half,
        "กลับด้าน": {"A": q(-nA, 0), "B": q(-nB, 0), "กำไรเมื่อXขึ้น1": q(-sets, 0)},
        "กำไรจากราคาต่อgrossเปอร์เซ็นต์": q(price / gross * 100, 1),
        "ต้นทุนต่อgrossเปอร์เซ็นต์": q(cost / gross * 100, 1),
        "hเปลี่ยน_กำไรที่จดผิด": q(sets * D(str(c["hเปลี่ยน"]["Xใหม่"])), 0),
        "ค่าถือขาshortต่อรอบ": m["ค่าถือคู่"]["ต่อรอบ"],
        "แบบฝึก_ค่า": {"ก": ex_a, "ข": ex_b, "ค": {"กำไร": r["กำไร"]}},
        "_แบบฝึก": [
            {"โจทย์": "(ทำตาม) ถือ 10 ชุด (A +10 · B −20) เปิดที่ A 100 · B 50 ปิดที่ A 101.5 · B 50.5 · ค่าธรรมเนียม 0.5 ต่อ fill × 4 · "
                      "ขา A ขา B กำไรจากราคา X ตอนออก และกำไรสุทธิ",
             "คำตอบ": v2["แบบฝึก"]["1"]["สุทธิ"], "กลางทาง": v2["แบบฝึก"]["1"]},
            {"โจทย์": "(เปลี่ยนเลขหนึ่งตัว) ไม้กระดาษเดิม (A 100 → 102 · B 50 → 50.95) แต่ exchange คิด taker 0.1% · "
                      "ค่าธรรมเนียมไปกลับ กำไรสุทธิ และ Break-even ต่อชุด",
             "คำตอบ": v2["แบบฝึก"]["2"]["สุทธิ"], "กลางทาง": v2["แบบฝึก"]["2"]},
            {"โจทย์": "(เปลี่ยนเงื่อนไข) ถือ A 10 กับ short B 25 (h 2.5) จากวันที่ 1 ถึงวันที่ 2 ของบท 9 "
                      "(A 99.6 → 100.7 · B 49.6 → 49.9) · กำไรจากราคาเทียบกับ h 2",
             "คำตอบ": v2["แบบฝึก"]["3"]["รวม"], "กลางทาง": v2["แบบฝึก"]["3"]},
            {"โจทย์": "(ตัดสินใจ) ราคาเท่าเดิม A 100 · B 50 หน้าวิเคราะห์เปลี่ยน h 2 → 2.2 · X ไป −10 · ยังถือ A +10 B −20 · "
                      "กำไรจากราคาเท่าไร (คำตอบที่ยั่ว: −100) · ถ้าปรับตาม h ใหม่ต้องทำอะไรกับ B",
             "คำตอบ": 0, "กลางทาง": ex_b},
            {"โจทย์": "(ถ่ายโอนไปตลาดหุ้น) ซื้อหุ้น P 10 หุ้นที่ 80 · short Q 20 หุ้นที่ 40 · ปิดที่ P 82 · Q 40.5 · "
                      "ค่านายหน้า 0.1% ต่อครั้ง × 4 ครั้ง · ค่ายืมหุ้น Q 0.5 · กำไรสุทธิ",
             "คำตอบ": v2["แบบฝึก"]["5"]["สุทธิ"], "กลางทาง": v2["แบบฝึก"]["5"]},
        ],
    }
