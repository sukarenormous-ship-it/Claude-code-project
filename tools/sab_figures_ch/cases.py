"""ภาคผนวก J — กรณีศึกษา 5 เรื่อง (ปลั๊กอินของ tools/sab_figures.py · ลงใต้ data["cases"])

หน้า docs/sab-appendix-cases.html · ทุกเรื่องใช้โครงเดียวกัน: คำถาม → ข้อมูล → ของที่ถือ → สมุดบัญชี → ตัดสิน
ตัวเลขทุกตัวของหน้าคิดที่นี่ด้วย Decimal จากค่าตั้งโจทย์ด้านล่าง (ห้ามพิมพ์ผลลัพธ์ลอย) · เงินปัดเป็นเซนต์แบบ half-up

  c1 funding สองตลาด หลักประกันแยก     (ต่อจากบท 4 · 7 · 16)
  c2 ตามเป้าทุกวัน vs กันชนไม่เทรด      (ต่อจากบท 11 · 16)
  c3 ไม้บรรทัดที่เลื่อนเอง              (ต่อจากบท 9 · 12 · 14)
  c4 หยุดแล้วแต่ยังไม่แบน              (ต่อจากบท 14 · 16)
  c5 เงินก้อนเดียว สองงาน สองเพดาน      (ต่อจากบท 0 · 6 · 16 · 17)
"""


def extend(data, D, q):
    def m(x):
        """เงิน → int ถ้าลงตัว ไม่งั้น float สองตำแหน่ง (B.fmt ไม่พิมพ์ .0 ท้ายจำนวนเต็ม)"""
        v = q(x, 2)
        return int(v) if float(v).is_integer() else v

    def pct(x, n=2):
        v = q(x * 100, n)
        return int(v) if float(v).is_integer() else v

    acct = data["บัญชีมิน"]
    taker = D(str(acct["ค่าธรรมเนียม"]["taker"])) / 100          # 0.05% (บท 1)
    maker = D(str(acct["ค่าธรรมเนียม"]["maker"])) / 100          # 0.02% (บท 16)
    im = D(str(acct["กติกาหลักประกันเปอร์เซ็นต์"])) / 100        # 10% (บท 4)
    mm = im / 2                                                    # ระดับรักษา = ครึ่งหนึ่งของหลักประกันเริ่มต้น (บท 4 · 16)
    out = {}

    # ───────── c1 funding สองตลาด หลักประกันแยก ─────────
    size = D("0.02")
    prices = [D(100000), D(105000), D(110000)]
    r_long = [D("0.01"), D("0.01"), D("0.01")]       # แห่งที่ 1 (ถือ long perp) อัตราบวก → long จ่าย
    r_short = [D("0.02"), D("0.02"), D("0.01")]      # แห่งที่ 2 (ถือ short perp) อัตราบวก → short รับ
    dep = D(300)
    p0 = prices[0]
    notional = size * p0
    fee_open = notional * taker
    cash1, cash2 = dep - fee_open, dep - fee_open
    rounds = []
    f1_tot = f2_tot = D(0)
    for i, (p, a, b) in enumerate(zip(prices, r_long, r_short)):
        base = size * p
        f1 = -(base * a / 100)
        f2 = base * b / 100
        cash1 += f1
        cash2 += f2
        f1_tot += f1
        f2_tot += f2
        u1 = size * (p - p0)
        u2 = -size * (p - p0)
        mmv = mm * base
        e1, e2 = cash1 + u1, cash2 + u2
        rounds.append({"รอบ": i + 1, "ราคา": int(p), "ฐาน": m(base), "อัตรา1": float(a), "อัตรา2": float(b),
                       "funding1": m(f1), "funding2": m(f2), "fundingสุทธิ": m(f1 + f2),
                       "เงินสด1": m(cash1), "กำไรค้าง1": m(u1), "equity1": m(e1),
                       "เงินสด2": m(cash2), "กำไรค้าง2": m(u2), "equity2": m(e2),
                       "ระดับรักษา": m(mmv), "ผ่าน1": bool(e1 >= mmv), "ผ่าน2": bool(e2 >= mmv),
                       "equityรวม": m(e1 + e2), "ห่างระดับรักษา2": m(e2 - mmv)})
    assert not rounds[2]["ผ่าน2"] and rounds[1]["ผ่าน2"]
    total_e = cash1 + cash2 + size * (prices[-1] - p0) - size * (prices[-1] - p0)
    assert total_e == 2 * dep - 2 * fee_open + f1_tot + f2_tot

    def need(sz, move, side):
        """เงินที่ต้องวางต่อแห่ง ให้รอดราคาวิ่ง move โดยไม่โอนเพิ่ม: ค่าธรรมเนียมเปิด + ขาดทุน + ระดับรักษาที่ราคาใหม่"""
        nv = sz * p0
        newp = 1 + move if side == "short" else 1 - move
        return nv * taker + nv * move + mm * nv * newp

    def survive(deposit, sz, side):
        nv = sz * p0
        # deposit − fee − nv·r ≥ mm·nv·(1 ± r)
        return (deposit - nv * taker - mm * nv) / (nv + (mm * nv if side == "short" else -mm * nv))

    move = D("0.20")
    half = size / 2
    out["c1"] = {
        "ขนาดBTC": float(size), "ราคาเปิด": int(p0), "มูลค่าสัญญา": m(notional), "ฝากต่อแห่ง": int(dep), "ฝากรวม": int(2 * dep),
        "ค่าธรรมเนียมเปิดต่อแห่ง": m(fee_open), "ค่าธรรมเนียมเปิดรวม": m(2 * fee_open),
        "หลักประกันเริ่มต้น": m(im * notional), "ส่วนเกินหลักประกันเริ่มต้น": m(dep - im * notional),
        "ระดับรักษาเปอร์เซ็นต์": pct(mm, 0), "หลักประกันเริ่มต้นเปอร์เซ็นต์": pct(im, 0),
        "เงินสดหลังเปิด": m(dep - fee_open), "ระดับรักษาตอนเปิด": m(mm * notional),
        "รอบ": rounds,
        "funding1รวม": m(f1_tot), "funding2รวม": m(f2_tot), "fundingสุทธิรวม": m(f1_tot + f2_tot),
        "equityรวมท้าย": m(total_e), "ตรวจequityรวม": m(2 * dep - 2 * fee_open + f1_tot + f2_tot),
        "ราคาขึ้นรอบ3เปอร์เซ็นต์": pct((prices[2] - p0) / p0, 0),
        "รอดได้แห่งshortเปอร์เซ็นต์": pct(survive(dep, size, "short")),
        "รอดได้แห่งlongเปอร์เซ็นต์": pct(survive(dep, size, "long")),
        "ทางเลือก": {
            "วิ่งเปอร์เซ็นต์": pct(move, 0),
            "ขาดทุนที่วิ่ง": m(notional * move),
            "ระดับรักษาshort": m(mm * notional * (1 + move)), "ระดับรักษาlong": m(mm * notional * (1 - move)),
            "ต้องวางshort": m(need(size, move, "short")), "ต้องวางlong": m(need(size, move, "long")),
            "ต้องวางรวม": m(need(size, move, "short") + need(size, move, "long")),
            "ครึ่งขนาดBTC": float(half), "ครึ่งมูลค่า": m(half * p0),
            "ครึ่งค่าธรรมเนียมเปิด": m(half * p0 * taker),
            "ครึ่งขาดทุนที่วิ่ง": m(half * p0 * move),
            "ครึ่งระดับรักษาshort": m(mm * half * p0 * (1 + move)), "ครึ่งระดับรักษาlong": m(mm * half * p0 * (1 - move)),
            "ครึ่งต้องวางshort": m(need(half, move, "short")), "ครึ่งต้องวางlong": m(need(half, move, "long")),
            "ครึ่งต้องวางรวม": m(need(half, move, "short") + need(half, move, "long")),
            "ครึ่งเหลือแห่งshort": m(dep - need(half, move, "short")),
            "ครึ่งเหลือแห่งlong": m(dep - need(half, move, "long")),
            "ครึ่งfundingรอบ1": m(half * p0 * (r_short[0] - r_long[0]) / 100),
            "ครึ่งรอดได้แห่งshortเปอร์เซ็นต์": pct(survive(dep, half, "short")),
        },
    }
    # แบบฝึกข้อ 1: แบ่งเงิน 350 / 250 (แห่ง short ได้ 350)
    ex1_s, ex1_l = survive(D(350), size, "short"), survive(D(250), size, "long")

    # ───────── c2 ตามเป้าทุกวัน vs กันชนไม่เทรด ─────────
    cost_rate = D("0.001")                                  # taker 0.05% + ชั้นแรกของกระดาน 0.05% (บท 16)
    band = 2

    def per_coin(p):
        return (p * cost_rate).quantize(D("0.01"))

    def walk(targets, px, rule_band, start_cash=D(100)):
        held = targets[0]
        cash, unreal = start_cash, D(0)
        rows, orders, coins = [], 0, 0
        for t in range(1, len(targets)):
            gain = held * (px[t] - px[t - 1])               # ขา short: held ติดลบ ราคาลง → บวก
            unreal += gain
            gap = targets[t] - held
            send = gap if (rule_band == 0 and gap != 0) or (rule_band and abs(gap) >= rule_band) else 0
            c = abs(send) * per_coin(px[t])
            cash -= c
            if send:
                orders += 1
                coins += abs(send)
            held += send
            rows.append({"วัน": t, "เป้า": targets[t], "ส่ง": send, "ถือ": held, "ต้นทุน": m(c),
                         "ห่าง": abs(targets[t] - held), "ราคา": m(px[t]), "กำไรวันนี้": m(gain),
                         "เงินสด": m(cash), "กำไรค้าง": m(unreal), "equity": m(cash + unreal)})
        return {"วัน": rows, "คำสั่ง": orders, "เหรียญ": coins, "ต้นทุน": m(start_cash - cash),
                "กำไรจากราคา": m(unreal), "สุทธิ": m(unreal - (start_cash - cash)), "equityท้าย": m(cash + unreal),
                "ห่างสูงสุด": max(r["ห่าง"] for r in rows)}

    wig_t = [-20, -21, -19, -21, -20, -19, -20]
    wig_p = [D(50)] * len(wig_t)
    tr_t = [-20, -21, -22, -23, -24, -25, -26]
    tr_p = [D(50) - D("0.5") * i for i in range(len(tr_t))]
    assert all(per_coin(p) == D("0.05") for p in tr_p)
    wf, wb = walk(wig_t, wig_p, 0), walk(wig_t, wig_p, band)
    tf, tb = walk(tr_t, tr_p, 0), walk(tr_t, tr_p, band)
    t3 = walk(tr_t, tr_p, 3)
    save = D(str(wf["ต้นทุน"])) - D(str(wb["ต้นทุน"]))
    lose = D(str(tf["สุทธิ"])) - D(str(tb["สุทธิ"]))
    be = lose / (save + lose)
    out["c2"] = {
        "ต้นทุนต่อเหรียญ": m(per_coin(D(50))), "ต้นทุนเปอร์เซ็นต์": pct(cost_rate, 1), "ราคาB": 50,
        "กันชน": band, "กันชนมูลค่า": m(band * 50), "หลักประกันเริ่ม": 100,
        "แกว่ง": {"เป้า": wig_t, "ตาม": wf, "กันชน": wb, "ประหยัด": m(save),
                  "เอียงสูงสุดมูลค่า": m(wb["ห่างสูงสุด"] * 50)},
        "เดิน": {"เป้า": tr_t, "ราคา": [m(p) for p in tr_p], "ราคาลงต่อวัน": 0.5, "ราคาท้าย": m(tr_p[-1]),
                 "ตาม": tf, "กันชน": tb, "แพ้": m(lose),
                 "ต้นทุนต่อเหรียญที่47": float(tr_p[-1] * cost_rate)},
        "คุ้มทุนเปอร์เซ็นต์": pct(be, 0), "คุ้มทุนส่วน": m(save + lose),
        "สิบสัปดาห์": {"แกว่ง8": m(8 * save - 2 * lose), "แกว่ง7": m(7 * save - 3 * lose),
                       "แกว่ง8ได้": m(8 * save), "แกว่ง8เสีย": m(2 * lose),
                       "แกว่ง7ได้": m(7 * save), "แกว่ง7เสีย": m(3 * lose)},
    }
    ex2 = {"กันชน3": t3, "แพ้ตาม": m(D(str(tf["สุทธิ"])) - D(str(t3["สุทธิ"])))}

    # ───────── c3 ไม้บรรทัดที่เลื่อนเอง ─────────
    xs = [D(0), D(0), D(0), D(2), D(2), D(2), D(2)]          # วัน −3..3 · เข้าวัน 0
    win = 4
    frozen_mean, frozen_sd = D(acct["ไม้บรรทัด"]["ค่ากลาง"]), D(acct["ไม้บรรทัด"]["ระยะแกว่งปกติ"])
    exit_z = D(str(acct["การ์ด"]["ออก"]))
    enter_z = D(str(acct["การ์ด"]["เข้า"]))
    days = []
    for k in range(3, len(xs)):
        w = xs[k - win + 1:k + 1]
        mu = sum(w) / win
        dev = [x - mu for x in w]
        ss = sum(d * d for d in dev)
        var = ss / (win - 1)
        sd = var.sqrt()
        sd2 = sd.quantize(D("0.01"))
        z = None if sd == 0 else (xs[k] - mu) / sd2
        days.append({"วัน": k - 3, "X": m(xs[k]), "หน้าต่าง": [m(x) for x in w], "ผลรวม": m(sum(w)), "Mean": m(mu),
                     "ห่าง": [m(d) for d in dev], "กำลังสอง": [m(d * d) for d in dev], "ผลรวมกำลังสอง": m(ss),
                     "ความแปรปรวน": m(var), "SD": m(sd2), "Xลบmean": m(xs[k] - mu),
                     "Z": None if z is None else m(z), "Zตรึง": m((xs[k] - frozen_mean) / frozen_sd),
                     "ออก": bool(z is not None and z <= exit_z)})
    trig = next(d["วัน"] for d in days if d["ออก"])
    assert trig == 2
    sets = 10
    pa, pb = D(102), D(50)
    na, nb = sets * pa, 2 * sets * pb
    fa, fb = na * taker, nb * taker
    start = D(1100)
    led, cash = [], start
    hold_b = D(0)
    steps3 = [("เข้า: ซื้อ B 20 ที่ 50", -nb, fb, nb, 0), ("เข้า: short A 10 ที่ 102", 0, fa, nb, 0),
              ("วัน 1 และวัน 2: ราคาไม่ขยับ", 0, 0, nb, 0),
              ("ออก: ขาย B 20 ที่ 50", nb, fb, 0, 0), ("ออก: ซื้อคืน A 10 ที่ 102", 0, fa, 0, 0)]
    for name, flow, fee, bval, ua in steps3:
        cash += flow - fee
        led.append({"เหตุการณ์": name, "เงินสด": m(cash), "Bมูลค่า": m(bval), "กำไรค้างA": ua,
                    "equity": m(cash + bval + ua), "ค่าธรรมเนียม": m(fee)})
    fees3 = 2 * (fa + fb)
    out["c3"] = {
        "หน้าต่าง": win, "Meanตรึง": m(frozen_mean), "SDตรึง": m(frozen_sd), "เส้นเข้า": m(enter_z), "เส้นออก": m(exit_z),
        "Xก่อนเข้า": m(xs[0]), "Xเข้า": m(xs[3]), "วัน": days, "วันที่ออก": trig,
        "ชุด": sets, "A": int(pa), "B": int(pb), "จำนวนA": sets, "จำนวนB": 2 * sets,
        "มูลค่าA": m(na), "มูลค่าB": m(nb), "ค่าธรรมเนียมA": m(fa), "ค่าธรรมเนียมB": m(fb),
        "ค่าธรรมเนียมเข้า": m(fa + fb), "ค่าธรรมเนียมรวม": m(fees3), "เงินเริ่ม": int(start),
        "สมุด": led, "กำไรจากราคา": m(sets * (xs[3] - xs[-1])), "สุทธิ": m(-fees3), "equityท้าย": m(start - fees3),
        "ทางถัดไป": {
            "กลับ05": {"Xวัน3": 0.5, "กำไรจากราคา": m(sets * (xs[3] - D("0.5"))), "สุทธิ": m(sets * (xs[3] - D("0.5")) - fees3)},
            "ค้าง2": {"Xวัน3": 2, "กำไรจากราคา": 0, "สุทธิ": m(-fees3)},
            "ห่าง3": {"Xวัน3": 3, "กำไรจากราคา": m(sets * (xs[3] - 3)), "สุทธิ": m(sets * (xs[3] - 3) - fees3)},
        },
        "ช่วงถือสูงสุด": acct["การ์ด"]["ช่วงถือสูงสุด"], "งบ": acct["การ์ด"]["งบขาดทุนสุทธิ"],
    }

    # ───────── c4 หยุดแล้วแต่ยังไม่แบน ─────────
    A0, B0 = 10, -20
    pA, pB, pB2 = D(100), D(50), D(52)
    cash = D(100)
    held = {"A": A0, "B": B0}
    pend = {"A": 0, "B": 0}
    rows = []

    def snap(label, fee=D(0), pb=pB, note=""):
        ua = held["B"] * (pb - pB)            # กำไรค้างขา B (perp) เทียบราคาเข้า 50
        e = cash + held["A"] * pA + ua
        rows.append({"เหตุการณ์": label, "A": held["A"], "B": held["B"], "ค้างA": pend["A"], "ค้างB": pend["B"],
                     "เงินสด": m(cash), "Aมูลค่า": m(held["A"] * pA), "กำไรค้างB": m(ua), "equity": m(e),
                     "ค่าธรรมเนียม": m(fee), "หมายเหตุ": note})
        return e

    e0 = snap("กดปิดทั้งชุดด้วยคำสั่งตั้งรอ")
    pend.update(A=-10, B=20)
    rows[-1].update(ค้างA=-10, ค้างB=20)
    fA1 = 6 * pA * maker
    cash += 6 * pA - fA1
    held["A"] -= 6
    pend["A"] += 6
    snap("ได้ขาย A 6 ที่ 100 (ตั้งรอ)", fA1)
    fB1 = 8 * pB * maker
    cash -= fB1
    held["B"] += 8
    pend["B"] -= 8
    snap("ได้ซื้อคืน B 8 ที่ 50 (ตั้งรอ)", fB1)
    seen_B, seen_pend_B = held["B"], pend["B"]
    fB2 = 2 * pB * maker
    cash -= fB2
    held["B"] += 2
    pend["B"] -= 2
    snap("กดหยุด แต่ได้ B เพิ่ม 2 ก่อนแอปยืนยัน", fB2)
    pend.update(A=0, B=0)
    e_ack = snap("แอปยืนยัน: ยกเลิกที่ค้างหมด")
    send_A, send_B = 0 - held["A"] - pend["A"], 0 - held["B"] - pend["B"]
    netexp = held["A"] * pA + held["B"] * pB
    # ทางที่ปิดทันทีหลังยืนยัน (taker ที่ราคาเดิม)
    now_cost = abs(send_A) * pA * taker + abs(send_B) * pB * taker
    e_now = e_ack - now_cost
    # ทางที่เกิดจริง: เข้านอน เช้า B 52
    e_morn = snap("เช้า: B ขึ้นเป็น 52 (A ยังที่ 100)", pb=pB2)
    fA2 = abs(send_A) * pA * taker
    cash += abs(send_A) * pA - fA2
    held["A"] += send_A
    snap("ขาย A 4 ที่ 100 (ทันที · ลดสถานะเท่านั้น)", fA2, pb=pB2)
    fB3 = abs(send_B) * pB2 * taker
    cash += held["B"] * (pB2 - pB) - fB3          # ปิดขา B: กำไรค้างกลายเป็นเงินสด
    held["B"] += send_B
    e_flat = snap("ซื้อคืน B 10 ที่ 52 (ทันที · ลดสถานะเท่านั้น)", fB3, pb=pB2)
    fees4 = fA1 + fB1 + fB2 + fA2 + fB3
    assert e_flat == e0 - fees4 + (B0 + 10) * (pB2 - pB)
    wrong_send = 0 - seen_B                      # ดูจอแล้วคิดว่าที่ค้างหายไปแล้ว: ซื้อคืน 12
    out["c4"] = {
        "Aเริ่ม": A0, "Bเริ่ม": B0, "ราคาA": int(pA), "ราคาB": int(pB), "ราคาBเช้า": int(pB2), "เงินสดเริ่ม": 100,
        "สมุด": rows, "equityเริ่ม": m(e0), "equityยืนยัน": m(e_ack), "equityเช้า": m(e_morn), "equityแบน": m(e_flat),
        "ส่งA": send_A, "ส่งB": send_B, "สุทธิหลังยืนยัน": m(netexp),
        "Aมูลค่าหลังยืนยัน": m(4 * pA), "Bมูลค่าหลังยืนยัน": m(10 * pB),
        "เห็นบนจอB": seen_B, "เห็นค้างB": seen_pend_B, "สูตรตอนยังไม่ยืนยัน": 0 - seen_B - seen_pend_B,
        "ส่งผิด": wrong_send, "Bถ้าส่งผิด": seen_B + 2 + wrong_send, "ตัดเหลือ": 10,
        "ค่าปิดทันที": m(now_cost), "equityปิดทันที": m(e_now), "ราคาของการไม่แบน": m(e_now - e_flat),
        "ค่าธรรมเนียมรวม": m(fees4), "equityลดรวม": m(e0 - e_flat), "Bเสียตอนเช้า": m(10 * (pB2 - pB)),
        "Bขึ้นเปอร์เซ็นต์": pct((pB2 - pB) / pB, 0),
        "ค่าธรรมเนียมmakerเปอร์เซ็นต์": float(acct["ค่าธรรมเนียม"]["maker"]),
    }
    # แบบฝึกข้อ 3: ได้ B เพิ่ม 5 ระหว่างกดหยุด
    ex3_B = -12 + 5
    ex3 = {"Bถือ": ex3_B, "ส่งB": -ex3_B, "ส่งA": -4, "Bมูลค่า": m(abs(ex3_B) * pB), "สุทธิ": m(4 * pA + ex3_B * pB)}

    # ───────── c5 เงินก้อนเดียว สองงาน สองเพดาน ─────────
    pot, cap1 = D(1500), D(700)
    unit = D(500)
    marg = im * unit
    exp_pair, exp_carry = D(6), D(5)
    gap = D("0.20")
    reserve_need = unit * gap + mm * unit * (1 + gap)            # เงินที่บัญชี short ต้องมีเพื่อรอดราคาวิ่ง 20%
    extra = reserve_need - marg

    def enum(pair_ex1, carry_ex1, carry_ex2):
        rows = []
        for p in range(0, 3):
            for c in range(0, 3):
                if p == c == 0:
                    continue
                money = p * pair_ex1 + c * (carry_ex1 + carry_ex2)
                ex1 = p * pair_ex1 + c * carry_ex1
                ok_m, ok_1 = money <= pot, ex1 <= cap1
                why = "ผ่าน" if ok_m and ok_1 else ("เกินทั้งสอง" if not ok_m and not ok_1 else
                                                     ("เงินรวมเกิน" if not ok_m else "แห่งที่ 1 เกิน"))
                rows.append({"คู่": p, "carry": c, "เงินรวม": m(money), "แห่งที่1": m(ex1), "ผ่าน": ok_m and ok_1,
                             "เหตุ": why, "คาดได้": m(p * exp_pair + c * exp_carry)})
        best = max((r for r in rows if r["ผ่าน"]), key=lambda r: r["คาดได้"])
        return rows, best

    pair1, carry1, carry2 = unit + marg, marg, unit
    naive, nbest = enum(pair1, carry1, carry2)
    pair1r, carry1r = unit + reserve_need, reserve_need
    res, rbest = enum(pair1r, carry1r, carry2)
    assert (nbest["คู่"], nbest["carry"]) == (1, 1) and (rbest["คู่"], rbest["carry"]) == (0, 2)
    # ช่องว่างราคา +20% กับแผน (1, 1)
    loss = unit * gap
    ex1_before = unit + marg + marg
    a_after = unit * (1 + gap)
    ex2_free = pot - (pair1 + carry1 + carry2)
    out["c5"] = {
        "เงินรวม": int(pot), "เพดานแห่งที่1": int(cap1), "มูลค่าขา": int(unit), "หลักประกันต่อขา": m(marg),
        "คาดคู่": int(exp_pair), "คาดcarry": int(exp_carry),
        "คู่ต่อหน่วยแห่งที่1": m(pair1), "carryต่อหน่วยแห่งที่1": m(carry1), "carryต่อหน่วยแห่งที่2": m(carry2),
        "carryต่อหน่วยรวม": m(carry1 + carry2),
        "ไล่แบบไม่กัน": naive, "ดีสุดไม่กัน": nbest,
        "ช่องว่าง": {
            "เปอร์เซ็นต์": pct(gap, 0), "ขาดทุนขาshort": m(loss), "แห่งที่1ก่อน": m(ex1_before),
            "Aหลัง": m(a_after), "หลักประกันหลัง": m(marg - loss),
            "แห่งที่2spotหลัง": m(a_after), "เงินว่าง": m(ex2_free), "แห่งที่2หลัง": m(a_after + ex2_free),
            "รวมหลัง": m(a_after + a_after + ex2_free), "ถือlongเปลือย": m(2 * a_after),
            "ราคากลับรวม": m(unit + unit + ex2_free), "เสียหลักประกันสองขา": m(2 * marg),
            "ระดับรักษาหลัง": m(mm * unit * (1 + gap)),
            "ต้องมีต่อขา": m(reserve_need), "ต้องเติมต่อขา": m(extra), "ต้องเติมสองขา": m(2 * extra),
            "แห่งที่1ถ้าเติมก่อน": m(ex1_before + 2 * extra),
        },
        "คู่ต่อหน่วยแห่งที่1กัน": m(pair1r), "carryต่อหน่วยแห่งที่1กัน": m(carry1r), "carryต่อหน่วยรวมกัน": m(carry1r + carry2),
        "ไล่แบบกัน": res, "ดีสุดกัน": rbest,
        "ต่อร้อยแห่งที่1คู่": m(exp_pair / pair1r * 100), "ต่อร้อยแห่งที่1carry": m(exp_carry / carry1r * 100),
        "ดีสุดกันเงินว่าง": m(pot - 2 * (carry1r + carry2)), "ดีสุดกันแห่งที่1": m(2 * carry1r),
        "ดีสุดกันแห่งที่1ว่าง": m(cap1 - 2 * carry1r),
        "คู่เพิ่มบนแห่งที่1": m(2 * carry1r + pair1r),
    }

    out["แบบฝึก"] = {
        "ข้อ1": {"แห่งshort": 350, "แห่งlong": 250, "รอดshortเปอร์เซ็นต์": pct(ex1_s), "รอดlongเปอร์เซ็นต์": pct(ex1_l),
                 "ส่วนshort": m(D(350) - fee_open - mm * notional), "ส่วนlong": m(D(250) - fee_open - mm * notional),
                 "ตัวหารshort": m(notional * (1 + mm)), "ตัวหารlong": m(notional * (1 - mm))},
        "ข้อ2": ex2,
        "ข้อ3": ex3,
    }
    out["_แบบฝึก"] = [
        {"โจทย์": "เคส 1 แบ่งเงิน 350 ที่แห่ง short และ 250 ที่แห่ง long ราคาวิ่งได้กี่เปอร์เซ็นต์ก่อนแห่งใดแห่งหนึ่งถูกบังคับปิด",
         "คำตอบ": pct(min(ex1_s, ex1_l))},
        {"โจทย์": "เคส 2 เส้นทางเดินทางเดียว ถ้ากันชนกว้าง 3 เหรียญ แพ้การตามทุกวันเท่าไร", "คำตอบ": ex2["แพ้ตาม"]},
        {"โจทย์": "เคส 4 ถ้าได้ B เพิ่ม 5 ระหว่างกดหยุด ต้องซื้อคืน B กี่เหรียญ และเอียงสุทธิเท่าไร", "คำตอบ": ex3["สุทธิ"]},
    ]
    return out
