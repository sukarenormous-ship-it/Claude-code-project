"""บท 15 — อ่านผลที่ขาดทุนให้เป็น · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py)

- สะพานรายขา: แยก 12 → 8 → 5 → 3 → 2 เป็นรายขา (คำนวณจากราคาใน ch15.สะพาน)
- ตารางจำนวนรอบที่ต้องมี (แผนให้ค่า null): กติกาที่ประกาศในบท
      ค่าเฉลี่ยของไม้ทั้งหมดต้องห่างศูนย์อย่างน้อย 2 เท่าของ "ระยะแกว่งของค่าเฉลี่ย" (ระยะแกว่งต่อไม้ ÷ รากที่สองของจำนวนไม้)
      → ไม้ที่ต้องมี = ปัดขึ้น (2 × ระยะแกว่งต่อไม้ ÷ ค่าคาดหมายต่อไม้)²  (ราว 95% · ไม่สอนสูตรบนเส้นทางหลัก)
  ผลต่อไม้สามแบบของการ์ด (+16 / +2 / −21) ที่สัดส่วนต่าง ๆ · สองแถว = สองโลกของบท 12 · สองแถวกลางเพิ่มเพื่อให้เห็นการโต
- เงินก็หลอกได้ ข้าม 30 ชุด: ไม้แรกกำไรกี่ชุด · รวมบวกกี่ชุด · ไม้แย่สุด (งบไม่ใช่เพดานแข็ง) · หน่วยของการ์ดบนคู่อื่น
- แบบฝึก ✍️ ข้อ ก (สะพานชุดใหม่) และ ข (ทดสอบกระดาษ 12 ไม้ เฉลี่ย +5)
"""

import importlib.util
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_MIXES = ((60, 25, 15), (55, 25, 20), (50, 25, 25), (45, 20, 35))


def _lib():
    path = os.path.join(os.path.dirname(_HERE), "sab_figures.py")
    spec = importlib.util.spec_from_file_location("sab_figures_lib_ch15", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rounds(D, q, mix, outcomes):
    p = [D(m) / 100 for m in mix]
    x = [D(v) for v in outcomes]
    mean = sum(pi * xi for pi, xi in zip(p, x))
    var = sum(pi * xi * xi for pi, xi in zip(p, x)) - mean * mean
    sd = var.sqrt()
    need = int(math.ceil((2 * sd / mean) ** 2))
    return {"สัดส่วน": list(mix), "ค่าคาดหมาย": q(mean, 2), "ระยะแกว่งต่อไม้": q(sd, 2), "ไม้ที่ต้องมี": need}


def _bridge_case(D, q, qty, mid, fc, ex, fill, fee, carry):
    qa, qb = D(qty[0]), D(qty[1])
    m, f, e, fl = [[D(str(v)) for v in arr] for arr in (mid, fc, ex, fill)]
    exp = qa * (f[0] - m[0]) + qb * (f[1] - m[1])
    real = qa * (e[0] - m[0]) + qb * (e[1] - m[1])
    trad = qa * (e[0] - fl[0]) + qb * (e[1] - fl[1])
    return {"คาด": q(exp, 0), "ราคาจริง": q(real, 0), "ราคาที่ซื้อขายได้": q(trad, 0),
            "หลังค่าธรรมเนียม": q(trad - D(fee), 0), "หลังค่าถือ": q(trad - D(fee) - D(carry), 0),
            "คาดพลาด": q(real - exp, 0), "ผลของราคาfill": q(trad - real, 0)}


def _fake_money(sel, cost, leg=1000, budget=-15):
    """สำเนาตรรกะ fake_money ของ sab_figures.py ที่รับต้นทุนเป็นตัวแปร (เดิมตรึง 1) — การ์ดบท 12 ขาละ 1,000 ก่อนค่าถือ"""
    a, b, z = sel["_best_pair"]["a"], sel["_best_pair"]["b"], sel["_best_pair"]["z"]
    nf, n = 250, len(z)
    PA = [100 * math.exp(v) for v in a]
    PB = [100 * math.exp(v) for v in b]
    trades, pos, paused = [], None, False
    for i in range(nf, n):
        if pos is not None:
            el = i - pos["i"]
            gross = pos["qa"] * (PA[i] - PA[pos["i"]]) + pos["qb"] * (PB[i] - PB[pos["i"]])
            liq = gross - cost
            rec = z[i] <= 0.5 if pos["side"] < 0 else z[i] >= -0.5
            r = "งบ" if liq <= budget else "เป้า" if rec else "เวลา" if el >= 3 else None
            if r:
                trades.append({"วันเข้า": pos["i"] - nf + 1, "zเข้า": z[pos["i"]], "วันออก": i - nf + 1,
                               "zออก": z[i], "เหตุออก": r, "กำไรจากราคา": gross, "สุทธิ": liq})
                pos = None
                paused = paused or r == "งบ"
        elif not paused and abs(z[i]) >= 2:
            side = -1 if z[i] > 0 else 1
            pos = {"i": i, "side": side, "qa": side * leg / PA[i], "qb": -side * leg / PB[i]}
    return {"ไม้": trades, "รวมสุทธิ": sum(t["สุทธิ"] for t in trades), "หยุดเปิดเพราะงบ": paused}


def _v2(data, D, q, L, base, sels):
    """บท 15 ด้วยฐานต้นทุนเดียว (ch11.v2 · ต้นทุน 2 · สามตอนจบ +15 / +1 / −22 ของ ch12.v2)"""
    cost = D(str(data["ch11"]["v2"]["ต้นทุน"]["ไปกลับ"]))
    v12 = data["ch12"]["v2"]
    res = tuple(v12["เส้นทาง"][k]["สุทธิ"] for k in ("1", "2", "3"))    # 15 · 1 · −22
    table = []
    for mix in _MIXES:
        p = [D(m) / 100 for m in mix]
        x = [D(v) for v in res]
        mean = sum(pi * xi for pi, xi in zip(p, x))
        ex2 = sum(pi * xi * xi for pi, xi in zip(p, x))
        var = ex2 - mean * mean
        sd = var.sqrt()
        row = {"สัดส่วน": list(mix), "ค่าคาดหมาย": q(mean, 2), "ค่าเฉลี่ยกำลังสอง": q(ex2, 2),
               "ความแปรปรวน": q(var, 2), "ระยะแกว่งต่อไม้": q(sd, 2)}
        if mean > 0:
            raw = (2 * sd / mean) ** 2
            row.update({"สองเท่าsdหารค่าคาดหมาย": q(2 * sd / mean, 2), "ไม้ก่อนปัด": q(raw, 1),
                        "ไม้ที่ต้องมี": int(math.ceil(raw))})
        else:
            row.update({"ไม้ที่ต้องมี": None, "เหตุ": "ค่าคาดหมายไม่บวก — ไม่มีจำนวนไม้ที่ทำให้ผลเฉลี่ยพ้นศูนย์ฝั่งบวกได้"})
        table.append(row)
    assert table[0]["ค่าคาดหมาย"] == v12["สัดส่วนตอนจบ"]["หลัก"]["ค่าคาดหมาย"]
    # บันไดการแกว่งของค่าเฉลี่ย (รายงาน B S18): ไม้ 4 / 16 / 64 → แกว่ง sd ÷ √n · ต้องการ 2 × แกว่ง ≤ ค่าคาดหมาย
    sd0, mean0 = D(str(table[0]["ระยะแกว่งต่อไม้"])), D(str(table[0]["ค่าคาดหมาย"]))
    ladder = []
    for n in (4, 16, 64, table[0]["ไม้ที่ต้องมี"]):
        wob = sd0 / D(n).sqrt()
        ladder.append({"ไม้": n, "รากที่สอง": q(D(n).sqrt(), 2), "แกว่งของค่าเฉลี่ย": q(wob, 2),
                       "สองเท่า": q(2 * wob, 2), "ผ่าน": bool(2 * wob <= mean0)})

    # คู่ปลอมบนการ์ดบท 12 ด้วยต้นทุน 2
    fm = _fake_money(base, float(cost))
    fakes = [_fake_money(s, float(cost)) for s in sels]
    totals = sorted(f["รวมสุทธิ"] for f in fakes)
    import statistics
    budget_trades = [t["สุทธิ"] for f in fakes for t in f["ไม้"] if t["เหตุออก"] == "งบ"]
    fake = {"ไม้": [{"วันเข้า": t["วันเข้า"], "วันออก": t["วันออก"], "zเข้า": q(D(str(t["zเข้า"])), 2),
                     "zออก": q(D(str(t["zออก"])), 2), "เหตุออก": t["เหตุออก"],
                     "กำไรจากราคา": q(D(str(t["กำไรจากราคา"])), 2), "สุทธิ": q(D(str(t["สุทธิ"])), 2)} for t in fm["ไม้"]],
            "รวมสุทธิ": q(D(str(fm["รวมสุทธิ"])), 2), "หยุดเปิดเพราะงบ": fm["หยุดเปิดเพราะงบ"],
            "สามสิบชุด": {"จำนวนชุด": len(fakes), "จบที่พัก": sum(1 for f in fakes if f["หยุดเปิดเพราะงบ"]),
                          "มัธยฐานรวม": q(D(str(statistics.median(totals))), 2),
                          "ต่ำสุดรวม": q(D(str(totals[0])), 2), "สูงสุดรวม": q(D(str(totals[-1])), 2),
                          "ไม้แรกกำไร": sum(1 for f in fakes if f["ไม้"] and f["ไม้"][0]["สุทธิ"] > 0),
                          "รวมบวก": sum(1 for f in fakes if f["รวมสุทธิ"] > 0),
                          "ไม้งบเสียเกิน20": sum(1 for v in budget_trades if v < -20),
                          "ไม้แย่สุด": q(D(str(min(t["สุทธิ"] for f in fakes for t in f["ไม้"]))), 2),
                          "จำนวนไม้": {"ตัวอย่าง": len(fm["ไม้"]),
                                       "มัธยฐาน": q(D(str(statistics.median([len(f["ไม้"]) for f in fakes]))), 0),
                                       "ต่ำสุด": min(len(f["ไม้"]) for f in fakes), "สูงสุด": max(len(f["ไม้"]) for f in fakes)}}}
    sd_money = D(str(base["_best_sd"])) * 1000
    room = -D(str(data["บัญชีมิน"]["การ์ด"]["งบขาดทุนสุทธิ"])) - cost                  # 13
    unit = {"หนึ่งระยะแกว่งเป็นเงินคู่ปลอม": q(sd_money, 1), "หนึ่งระยะแกว่งเป็นเงินAB": 10,
            "ขาดทุนจากราคาก่อนชนงบ": q(room, 0), "งบเป็นระยะแกว่งคู่ปลอม": q(room / sd_money, 2),
            "งบเป็นระยะแกว่งAB": q(room / 10, 1)}

    # ค่าธรรมเนียมของไม้ซ้อมในสะพาน = taker 0.05% × มูลค่าซื้อขายจริงสี่ fill (ตรวจว่าปัดเป็น 2 ตามฐานต้นทุน)
    br = data["ch15"]["สะพาน"]
    rate = D(str(data["ch11"]["v2"]["ต้นทุน"]["อัตราtakerเปอร์เซ็นต์"])) / 100
    qa, qb = (abs(D(v)) for v in br["จำนวน"])
    fills = [qa * D(str(br["ราคาเข้าจริง"][0])), qb * D(str(br["ราคาเข้าจริง"][1])),
             qa * D(str(br["ราคาออกจริง"][0])), qb * D(str(br["ราคาออกจริง"][1]))]
    fee_exact = rate * sum(fills)
    assert q(fee_exact, 0) == -br["ค่าธรรมเนียม"] == cost
    bridge_fee = {"มูลค่าfill": [q(v, 0) for v in fills], "มูลค่ารวม": q(sum(fills), 0), "ค่าธรรมเนียมไม่ปัด": q(fee_exact, 2),
                  "ตามฐานต้นทุน": q(cost, 0)}

    # ไม้ที่ต้องมีในโลกจำลองของบท 13 (รายงาน B S15) — จากค่าคาดหมายและ SD ของผลต่อไม้ในโลกนั้น
    w13 = data["ch13"]["v2"]["กฎเดียวสามโลก"]
    worlds = {k: {"ค่าคาดหมาย": w13[k]["ค่าคาดหมายต่อไม้ก่อนค่าถือ"], "sd": w13[k]["sdผลต่อไม้"],
                  "ไม้ที่ต้องมี": w13[k]["ไม้ที่ต้องมี"]} for k in ("0.80", "0.99", "1.00")}
    return {"สามตอนจบ": list(res), "จำนวนรอบ": table, "บันไดแกว่ง": ladder, "เงินก็หลอกได้": fake,
            "หน่วยการ์ด": unit, "ค่าธรรมเนียมสะพาน": bridge_fee, "ไม้ที่ต้องมีโลกบท13": worlds,
            "จำนวนรอบ_คิดมือ": {"กำลังสอง15": 15 * 15, "กำลังสอง1": 1, "กำลังสอง22": 22 * 22,
                               "ค่าเฉลี่ยกำลังสอง": table[0]["ค่าเฉลี่ยกำลังสอง"],
                               "ค่าคาดหมายกำลังสอง": q(mean0 * mean0, 4), "ความแปรปรวน": table[0]["ความแปรปรวน"]}}


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
    L = _lib()
    c15 = data["ch15"]
    br = c15["สะพาน"]
    qa, qb = (D(v) for v in br["จำนวน"])
    mid = [D(str(v)) for v in br["ราคากลางตอนเข้า"]]
    fc = [D(str(v)) for v in br["ราคาออกที่คาด"]]
    ex = [D(str(v)) for v in br["ราคาออกจริง"]]
    fl = [D(str(v)) for v in br["ราคาเข้าจริง"]]
    legs = {"คาดขาA": q(qa * (fc[0] - mid[0]), 0), "คาดขาB": q(qb * (fc[1] - mid[1]), 0),
            "จริงขาB": q(qb * (ex[1] - mid[1]), 0), "fillขาA": q(qa * (ex[0] - fl[0]), 0),
            "fillขาB": q(qb * (ex[1] - fl[1]), 0), "ราคาเข้าเสียขาA": q(qa * (fl[0] - mid[0]), 0),
            "ราคาเข้าเสียขาB": q(-qb * (mid[1] - fl[1]), 0)}
    lost = D(br["คาด"]) - D(br["หลังค่าถือ"])
    paid = -D(br["ค่าธรรมเนียม"]) - D(br["ค่าใช้จ่ายระหว่างถือ"])
    assert legs["คาดขาA"] + legs["คาดขาB"] == br["คาด"]
    assert legs["fillขาA"] + legs["fillขาB"] == br["ราคาที่ซื้อขายได้"]

    # ตารางจำนวนรอบที่ต้องมี
    outcomes = data["ch12"]["สัดส่วนตอนจบ"]  # มีค่าคาดหมายของสองโลกให้ตรวจ
    res = (16, 2, -21)
    table = [_rounds(D, q, m, res) for m in _MIXES]
    p0 = [D(m) / 100 for m in _MIXES[0]]
    mean0 = sum(pi * D(x) for pi, x in zip(p0, res))
    var0 = sum(pi * D(x) * D(x) for pi, x in zip(p0, res)) - mean0 * mean0
    assert table[0]["ค่าคาดหมาย"] == outcomes["หลัก"]["ค่าคาดหมาย"]
    assert table[-1]["ค่าคาดหมาย"] == outcomes["เทียบ"]["ค่าคาดหมาย"]

    # เงินก็หลอกได้ ข้าม 30 ชุด
    base = L.o_v09_selection(seed=L.SEED_SEL, series=False)
    fm = L.fake_money(base)
    assert fm["รวมสุทธิ"] == c15["เงินก็หลอกได้"]["รวมสุทธิ"], "จำลองซ้ำไม่ตรง ch15.เงินก็หลอกได้"
    sd_money = D(str(base["_best_sd"])) * 1000
    leg = 1000
    sels = [L.o_v09_selection(seed=s, series=False) for s in L.ROBUST_SEEDS]
    fakes = [L.fake_money(x) for x in sels]
    first_win = sum(1 for f in fakes if f["ไม้"] and f["ไม้"][0]["สุทธิ"] > 0)
    total_pos = sum(1 for f in fakes if f["รวมสุทธิ"] > 0)
    budget_trades = [t["สุทธิ"] for f in fakes for t in f["ไม้"] if t["เหตุออก"] == "งบ"]
    worst = min(t["สุทธิ"] for f in fakes for t in f["ไม้"])
    over20 = sum(1 for v in budget_trades if v < -20)
    budget = D(data["บัญชีมิน"]["การ์ด"]["งบขาดทุนสุทธิ"])
    cost = D(str(data["บัญชีมิน"]["การ์ด"]["ต้นทุนเข้า"])) + D(str(data["บัญชีมิน"]["การ์ด"]["ต้นทุนออก"]))
    price_room = -budget - cost   # ขาดทุนจากราคาก่อนชนงบ = 14

    # แบบฝึก ก: สะพานชุดใหม่
    ex_a = {"ราคากลางตอนเข้า": [100, 50], "ราคาออกที่คาด": [103.0, 50.5], "ราคาออกจริง": [102.5, 50.5],
            "ราคาเข้าจริง": [100.3, 49.9], "ค่าธรรมเนียม": 2, "ค่าถือ": 1}
    ex_a.update(_bridge_case(D, q, br["จำนวน"], ex_a["ราคากลางตอนเข้า"], ex_a["ราคาออกที่คาด"],
                             ex_a["ราคาออกจริง"], ex_a["ราคาเข้าจริง"], ex_a["ค่าธรรมเนียม"], ex_a["ค่าถือ"]))
    ex_b = {"ไม้": 12, "เฉลี่ยต่อไม้": 5, "แถวใกล้สุด": table[1]["ไม้ที่ต้องมี"]}

    v2 = _ints(_v2(data, D, q, L, base, sels))
    return {
        "v2": v2,
        "สะพานรายขา": legs,
        "สะพานหายรวม": q(lost, 0),
        "สะพานจ่ายจริง": q(paid, 0),
        "สะพานค่าธรรมเนียมส่วนของที่หายเปอร์เซ็นต์": q(-D(br["ค่าธรรมเนียม"]) / lost * 100, 0),
        "จำนวนรอบ": table,
        "จำนวนรอบ_กติกา": "ไม้ที่ต้องมี = ปัดขึ้น (2 × ระยะแกว่งต่อไม้ ÷ ค่าคาดหมายต่อไม้)² · ผลต่อไม้ +16 / +2 / −21",
        "จำนวนรอบ_คิดมือ": {"กำลังสอง16": 16 * 16, "กำลังสอง21": 21 * 21,
                           "ความแปรปรวน": q(var0, 2), "ไม้ก่อนปัด": q((2 * var0.sqrt() / mean0) ** 2, 1)},
        "จำนวนรอบเท่าโลกเทียบต่อโลกหลัก": q(D(table[-1]["ไม้ที่ต้องมี"]) / D(table[0]["ไม้ที่ต้องมี"]), 0),
        "ไม้ของมิน": 3,
        "หลอก30ชุด": {"ไม้แรกกำไร": first_win, "รวมบวก": total_pos, "ไม้แย่สุด": worst,
                      "ไม้งบเสียเกิน20": over20, "จำนวนชุด": len(fakes)},
        "หน่วยการ์ด": {"หนึ่งระยะแกว่งเป็นเงินคู่ปลอม": q(sd_money, 1), "ขาละ": leg,
                       "หนึ่งระยะแกว่งเป็นเงินAB": 10, "ขาดทุนจากราคาก่อนชนงบ": q(price_room, 0),
                       "งบเป็นระยะแกว่งคู่ปลอม": q(price_room / sd_money, 2),
                       "งบเป็นระยะแกว่งAB": q(price_room / 10, 1)},
        "บันได": {"เล็กเสียได้ไม่เกิน": data["บัญชีมิน"]["กฎ1%"]["เพดานต่อไม้"]},
        "แบบฝึกก": ex_a,
        "แบบฝึกข": ex_b,
        "_แบบฝึก": [
            {"โจทย์": "long A 10 · short B 20 · ราคากลาง 100 / 50 · คาด A 103 B 50.5 · จริง A 102.5 B 50.5 · "
                      "เข้าได้จริง A 100.3 B 49.9 · ค่าธรรมเนียม 2 · ค่าถือ 1 → กำไรสุทธิ",
             "คำตอบ": ex_a["หลังค่าถือ"]},
            {"โจทย์": "ทดสอบการ์ดบนกระดาษ 12 ไม้ เฉลี่ย +5 ต่อไม้ เพื่อนให้ขึ้นเงินจริงขนาดปกติ · ตัดสินอย่างไร "
                      "(แนวคำตอบ: ยังไม่พอ ตารางจำนวนรอบ (ต้นทุน 2) ต้องราว 49 ไม้ที่เฉลี่ยราว 4 · กระดาษไม่พิสูจน์ edge · ขั้นถัดไปคือขนาดเล็ก)"},
            {"โจทย์": "ใช้สะพาน 5 ชั้นกับ funding carry ของภาค 1 · ชั้นไหนเปลี่ยนเครื่องหมาย และคาดพลาดวัดจากอะไร"},
        ],
    }
