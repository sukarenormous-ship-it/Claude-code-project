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


def _bridge_v2(D, q, qty, mid, fc, ex_mid, half, rate, carry_rate, carry_rounds, leg=1000):
    """สะพานผล v2 (การ์ด → แอป) · ชั้นละหนึ่งสมมติฐาน:
    ค่าที่คาดไว้ → คาดพลาด → ส่วนต่างราคาตอนเข้า → ส่วนต่างราคาตอนออก → Slippage (กระดาษ = 0) → ค่าธรรมเนียม → ค่าถือ
    ราคาที่ได้ = ราคากลาง ± ครึ่งหนึ่งของส่วนต่างราคาเสนอซื้อ-ขาย (ซื้อได้ที่ ask ขายได้ที่ bid)
    ค่าธรรมเนียมใช้ฐานต้นทุนเดียว (ch11.v2: 0.05% × ขาละ 1,000 × 4 fill = 2) · ตรวจกับมูลค่าที่ซื้อขายจริงสี่ fill"""
    qa, qb = D(qty[0]), D(qty[1])
    m, f, e, h = [[D(str(v)) for v in arr] for arr in (mid, fc, ex_mid, half)]
    sa, sb = (1 if qa > 0 else -1), (1 if qb > 0 else -1)
    fill_in = [m[0] + sa * h[0], m[1] + sb * h[1]]          # long จ่าย ask · short ได้ bid
    fill_out = [e[0] - sa * h[0], e[1] - sb * h[1]]         # ปิด long ขายที่ bid · ปิด short ซื้อคืนที่ ask
    exp_a, exp_b = qa * (f[0] - m[0]), qb * (f[1] - m[1])
    mid_a, mid_b = qa * (e[0] - m[0]), qb * (e[1] - m[1])
    sp_in = [abs(qa) * h[0], abs(qb) * h[1]]
    sp_out = [abs(qa) * h[0], abs(qb) * h[1]]
    trad_a, trad_b = qa * (fill_out[0] - fill_in[0]), qb * (fill_out[1] - fill_in[1])
    vals = [abs(qa) * fill_in[0], abs(qb) * fill_in[1], abs(qa) * fill_out[0], abs(qb) * fill_out[1]]
    fee_exact = D(str(rate)) / 100 * sum(vals)
    fee = D(str(rate)) / 100 * leg * 4                       # ฐานต้นทุนเดียว
    per_round = D(str(carry_rate)) / 100 * leg
    carry = per_round * carry_rounds                          # มีเครื่องหมาย (ลบ = จ่าย)
    exp, midr = exp_a + exp_b, mid_a + mid_b
    after_in = midr - sum(sp_in)
    after_out = after_in - sum(sp_out)
    slip = D(0)
    after_fee = after_out - slip - fee
    net = after_fee + carry
    assert trad_a + trad_b == after_out                       # สองทาง: ทีละชั้น = ทีละขาที่ราคาที่ได้
    levels = [exp, midr, after_in, after_out, after_out - slip, after_fee, net]
    return {"จำนวน": [int(qa), int(qb)], "ราคากลางตอนเข้า": [float(v) for v in m], "ราคาออกที่คาด": [float(v) for v in f],
            "ราคากลางตอนออก": [float(v) for v in e], "ครึ่งส่วนต่าง": [float(v) for v in h],
            "ราคาได้ตอนเข้า": [q(v, 2) for v in fill_in], "ราคาได้ตอนออก": [q(v, 2) for v in fill_out],
            "คาดขาA": q(exp_a, 2), "คาดขาB": q(exp_b, 2), "คาด": q(exp, 2),
            "กลางขาA": q(mid_a, 2), "กลางขาB": q(mid_b, 2), "ผลที่ราคากลาง": q(midr, 2), "คาดพลาด": q(midr - exp, 2),
            "ส่วนต่างเข้า": [q(v, 2) for v in sp_in], "ส่วนต่างเข้ารวม": q(-sum(sp_in), 2), "หลังเข้า": q(after_in, 2),
            "ส่วนต่างออก": [q(v, 2) for v in sp_out], "ส่วนต่างออกรวม": q(-sum(sp_out), 2), "หลังออก": q(after_out, 2),
            "ส่วนต่างรวม": q(-sum(sp_in) - sum(sp_out), 2),
            "slippage": 0, "หลังslippage": q(after_out - slip, 2),
            "มูลค่าfill": [q(v, 2) for v in vals], "มูลค่ารวม": q(sum(vals), 2), "ค่าธรรมเนียมไม่ปัด": q(fee_exact, 2),
            "ค่าธรรมเนียม": q(-fee, 2), "หลังค่าธรรมเนียม": q(after_fee, 2),
            "ค่าถือต่อรอบ": q(per_round, 2), "รอบค่าถือ": carry_rounds, "ค่าถือ": q(carry, 2), "สุทธิ": q(net, 2),
            "ขาAที่ราคาได้": q(trad_a, 2), "ขาBที่ราคาได้": q(trad_b, 2), "ชั้น": [q(v, 2) for v in levels],
            "ไปถึงคนอื่น": q(sum(sp_in) + sum(sp_out) + fee - min(carry, D(0)), 2),
            "bidaskเข้า": {"A": [q(m[0] - h[0], 2), q(m[0] + h[0], 2)], "B": [q(m[1] - h[1], 2), q(m[1] + h[1], 2)]},
            "bidaskออก": {"A": [q(e[0] - h[0], 2), q(e[0] + h[0], 2)], "B": [q(e[1] - h[1], 2), q(e[1] + h[1], 2)]},
            "ขาAต่อเหรียญ": q(fill_out[0] - fill_in[0], 2), "ขาBต่อเหรียญ": q(fill_out[1] - fill_in[1], 2),
            "Aขยับคาด": q(f[0] - m[0], 2), "Bขยับคาด": q(f[1] - m[1], 2), "Bขยับจริง": q(e[1] - m[1], 2),
            "Xเข้า": q(m[0] - 2 * m[1], 2), "Xคาด": q(f[0] - 2 * f[1], 2), "Xจริง": q(e[0] - 2 * e[1], 2),
            "สองBคาด": q(2 * f[1], 2), "สองBจริง": q(2 * e[1], 2),
            "ผิดลืมชั้นออก": q(net + sum(sp_out), 2), "ผิดใช้ทั้งช่อง": q(net - sum(sp_in) - sum(sp_out), 2)}


def _v2_more(data, D, q, v2):
    """ตัวเลขกลางทางของหน้า v2 (แสดงการคิดทุกตัวเลขที่พิมพ์ · รายงาน B S18 S20 3.8 3.11)"""
    out = {}
    # ── สะพานผล v2: ชั้นราคาออกแยกจากชั้นราคาเข้า · Slippage แยกชั้น (กระดาษ = 0) · ค่าถือ 5 รอบ × −0.02% ของ 1,000
    br = data["ch15"]["สะพาน"]
    rate = data["ch11"]["v2"]["ต้นทุน"]["อัตราtakerเปอร์เซ็นต์"]
    s = _bridge_v2(D, q, br["จำนวน"], br["ราคากลางตอนเข้า"], br["ราคาออกที่คาด"], br["ราคาออกจริง"],
                   [0.05, 0.05], rate, -0.02, 5)
    assert s["คาด"] == br["คาด"] and s["ผลที่ราคากลาง"] == br["ราคาจริง"] and s["หลังออก"] == br["ราคาที่ซื้อขายได้"]
    assert s["หลังค่าธรรมเนียม"] == br["หลังค่าธรรมเนียม"] and s["สุทธิ"] == br["หลังค่าถือ"]
    assert q(D(str(s["ค่าธรรมเนียมไม่ปัด"])), 0) == -s["ค่าธรรมเนียม"]
    s["ตัวอย่างslippage"] = {"ราคาที่เห็น": s["bidaskเข้า"]["A"][1], "ราคาที่ได้": q(D(str(s["bidaskเข้า"]["A"][1])) + D("0.05"), 2),
                             "ต่อเหรียญ": 0.05, "สิบเหรียญ": q(D("0.05") * abs(D(br["จำนวน"][0])), 2)}
    out["สะพาน"] = s

    # ── SD ของผลสามแบบ คิดสองทาง (ระยะจากค่าเฉลี่ย vs ค่าเฉลี่ยกำลังสอง − ค่าเฉลี่ยยกกำลังสอง) ด้วยเลขที่พิมพ์ (ปัด 2 ตำแหน่ง)
    row0 = v2["จำนวนรอบ"][0]
    mix = [D(m) / 100 for m in row0["สัดส่วน"]]
    res = [D(v) for v in v2["สามตอนจบ"]]
    mean = D(str(row0["ค่าคาดหมาย"]))
    dist = [x - mean for x in res]
    sq = [D(str(q(d * d, 2))) for d in dist]
    wsq = [D(str(q(p * s2, 2))) for p, s2 in zip(mix, sq)]
    var = sum(wsq)
    sd = D(str(q(var.sqrt(), 2)))
    assert q(var, 2) == row0["ความแปรปรวน"] and float(sd) == row0["ระยะแกว่งต่อไม้"]
    msq = sum(p * x * x for p, x in zip(mix, res))
    out["sdมือ"] = {"ระยะ": [q(d, 2) for d in dist], "กำลังสอง": [q(v, 2) for v in sq], "ถ่วง": [q(v, 2) for v in wsq],
                    "รวม": q(var, 2), "sd": q(sd, 2),
                    "ทางสอง": {"ส่วน": [q(p * x * x, 2) for p, x in zip(mix, res)], "ค่าเฉลี่ยกำลังสอง": q(msq, 2),
                               "ค่าเฉลี่ยยกกำลังสอง": q(mean * mean, 2), "ผลต่าง": q(msq - D(str(q(mean * mean, 2))), 2)},
                    "แถบล่าง": q(mean - sd, 2), "แถบบน": q(mean + sd, 2),
                    "คูณกลับ": q(sd * sd, 1),
                    "ในแถบเปอร์เซ็นต์": int(sum(m for m, x in zip(row0["สัดส่วน"], res) if mean - sd <= x <= mean + sd))}

    # ── บันไดการแกว่งของค่าเฉลี่ย (คิดจากรากที่ปัด 2 ตำแหน่ง ให้ผู้อ่านคิดตามได้ตรง)
    two_sd = 2 * sd
    rows = []
    for n in (3, 4, 16, 19, 20, 64):
        r = D(str(q(D(n).sqrt(), 2)))
        rows.append({"ไม้": n, "ราก": q(r, 2), "แกว่ง": q(sd / r, 2), "สองเท่า": q(two_sd / r, 2),
                     "ผ่าน": bool(D(str(q(two_sd / r, 2))) <= mean)})
    raw = (two_sd / mean) ** 2
    out["บันไดแกว่งมือ"] = {"sd": q(sd, 2), "สองเท่าsd": q(two_sd, 2), "ค่าคาดหมาย": q(mean, 2), "แถว": rows,
                            "สองเท่าsdหารค่าคาดหมาย": q(two_sd / mean, 2), "ไม้ก่อนปัด": q(raw, 1),
                            "ไม้ที่ต้องมี": int(math.ceil(raw))}
    assert out["บันไดแกว่งมือ"]["ไม้ที่ต้องมี"] == row0["ไม้ที่ต้องมี"]

    # ── โลกจำลอง φ 0.80 ของบท 13: ค่าคาดหมาย 7.7 · SD ผลต่อไม้ 6.91 → ราว 4 ไม้
    w = data["ch13"]["v2"]["กฎเดียวสามโลก"]["0.80"]
    ev13, sd13 = D(str(w["ค่าคาดหมายต่อไม้ก่อนค่าถือ"])), D(str(w["sdผลต่อไม้"]))
    two13 = 2 * sd13
    r3 = D(str(q(D(3).sqrt(), 2)))
    raw13 = (two13 / ev13) ** 2
    out["โลกบท13มือ"] = {"ค่าคาดหมาย": q(ev13, 2), "sd": q(sd13, 2), "สองเท่าsd": q(two13, 2),
                         "สามไม้ราก": q(r3, 2), "สามไม้สองเท่า": q(two13 / r3, 2), "สี่ไม้สองเท่า": q(two13 / 2, 2),
                         "ไม้ก่อนปัด": q(raw13, 2), "ไม้ที่ต้องมี": int(math.ceil(raw13)),
                         "ส่วนผสม": [w["ออกเพราะเป้าเปอร์เซ็นต์"], w["ออกเพราะงบเปอร์เซ็นต์"], w["ออกเพราะเวลาเปอร์เซ็นต์"]]}
    assert out["โลกบท13มือ"]["ไม้ที่ต้องมี"] == w["ไม้ที่ต้องมี"]

    # ── ลองหลายแบบ (บท 10): ไม่มีแบบไหนดูดีโดยบังเอิญ = 0.95 คูณกัน n ครั้ง
    luck = {}
    for n in (10, 50):
        none = D("0.95") ** n * 100
        luck["ต่อแบบ"] = 0.95
        luck[str(n)] = {"ไม่มีเลยเปอร์เซ็นต์": q(none, 1), "อย่างน้อยหนึ่งเปอร์เซ็นต์": q(100 - D(str(q(none, 1))), 1)}
        assert luck[str(n)]["อย่างน้อยหนึ่งเปอร์เซ็นต์"] == data["ch15"]["ลองหลายครั้ง"][str(n)]
    out["ลองหลายแบบ"] = luck

    # ── สมุดไม้ของมิน (สามไม้จริงบท 12–14) อ่านเป็นตารางผล · ระยะจากยอดสูงสุด (บท 17 ตั้งชื่อ)
    v12, v14 = data["ch12"]["v2"], data["ch14"]["v2"]
    trades = [v12["เส้นทาง"]["1"]["สุทธิ"], v12["เส้นทาง"]["2"]["สุทธิ"], v14["ไม้3"]["สุทธิ"]]

    def _book(tr):
        cum, peak, below, run, top = [], [], [], 0, None
        for t in tr:
            run += t
            top = run if top is None else max(top, run)
            cum.append(run)
            peak.append(top)
            below.append(run - top)
        wobble3 = D(str(q(sd / r3, 2)))
        return {"ไม้": list(tr), "สะสม": cum, "ยอดสูงสุด": peak, "ต่ำกว่ายอด": below, "รวม": run,
                "เฉลี่ย": q(D(run) / len(tr), 2), "ชนะ": sum(1 for t in tr if t > 0),
                "ชนะเปอร์เซ็นต์": q(D(sum(1 for t in tr if t > 0)) / len(tr) * 100, 0),
                "ลึกสุดจากยอด": -min(below), "แกว่งสามไม้": q(wobble3, 2), "สองเท่าสามไม้": q(two_sd / r3, 2)}
    book = _book(trades)
    carry3 = D(str(v14["ค่าถือ"]["สามไม้"]))
    cap = D(str(data["บัญชีมิน"]["คู่"]["ทุนคู่"]))
    book.update({"ค่าถือสามไม้": q(carry3, 2), "หลังค่าถือ": q(D(book["รวม"]) + carry3, 2),
                 "ต่อทุนคู่เปอร์เซ็นต์": q(D(book["รวม"]) / cap * 100, 1), "ไม้แย่สุด": min(trades),
                 "ไม้แย่สุดต่อทุนรวมเปอร์เซ็นต์": v14["ไม้3"]["เปอร์เซ็นต์ทุนรวม"],
                 "ไม้ที่ต้องมี": row0["ไม้ที่ต้องมี"], "ขาดอีก": row0["ไม้ที่ต้องมี"] - len(trades)})
    book["ช่วงโลกซ้อม"] = [q(mean - D(str(book["สองเท่าสามไม้"])), 2), q(mean + D(str(book["สองเท่าสามไม้"])), 2)]
    assert book["รวม"] == data["เรื่อง"]["part15"]["close"]["บัญชีคู่"]
    assert book["หลังค่าถือ"] == v14["ค่าถือ"]["บัญชีคู่หลังค่าถือ"]
    out["สมุดไม้"] = book

    # ── แบบฝึก ✍️ ห้าข้อ (บันได v2)
    # ข้อ 2 เปลี่ยนเลขหนึ่งตัว: ครึ่งส่วนต่างของ B กว้างเป็น 0.1
    ex2 = _bridge_v2(D, q, br["จำนวน"], br["ราคากลางตอนเข้า"], br["ราคาออกที่คาด"], br["ราคาออกจริง"],
                     [0.05, 0.1], rate, -0.02, 5)
    ex2["ผิดเปลี่ยนแค่ตอนเข้า"] = q(D(str(ex2["สุทธิ"])) - D(str(ex2["ส่วนต่างออกรวม"])) + D(str(s["ส่วนต่างออกรวม"])), 2)
    # ข้อ 3 เปลี่ยนเงื่อนไข: ไม้ 3 จบเพราะเวลา +1 แทน −22
    ex3 = _book([trades[0], trades[1], v12["เส้นทาง"]["2"]["สุทธิ"]])
    # ข้อ 4 ตัดสินใจ: เพื่อน 16 ไม้กระดาษ เฉลี่ย +5 ผลแต่ละไม้แกว่งเท่าการ์ด (SD 13.13)
    avg4 = D(5)
    ex4 = {"ไม้": 16, "เฉลี่ย": 5, "แกว่ง": q(sd / 4, 2), "สองเท่า": q(two_sd / 4, 2),
           "ไม้ก่อนปัด": q((two_sd / avg4) ** 2, 2), "ไม้ที่ต้องมี": int(math.ceil((two_sd / avg4) ** 2))}
    # ข้อ 5 ถ่ายโอน: funding carry ภาค 1 (1 BTC · รอบละ 10 ที่ +0.01%) คาด 3 รอบ ได้จริง +10 +10 −5
    f1 = data["ch00"]["funding_short1BTCต่อรอบ"]
    ex5 = {"ต่อรอบ": f1, "คาดสามรอบ": 3 * f1, "จริง": [f1, f1, -f1 // 2], "จริงรวม": 2 * f1 - f1 // 2,
           "คาดพลาด": 2 * f1 - f1 // 2 - 3 * f1}
    out["แบบฝึก"] = {"ข้อ2": ex2, "ข้อ3": ex3, "ข้อ4": ex4, "ข้อ5": ex5}
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
    v2.update(_ints(_v2_more(data, D, q, v2)))
    sv, ex = v2["สะพาน"], v2["แบบฝึก"]
    drills = [
        {"โจทย์": "(ทำตาม) สะพานผลของไม้ซ้อมในบท: ส่วนต่างราคาตอนเข้า · หลังเข้า · ตอนออก · หลังออก · ค่าธรรมเนียม · ค่าถือ · สุทธิ",
         "คำตอบ": [sv["ส่วนต่างเข้ารวม"], sv["หลังเข้า"], sv["ส่วนต่างออกรวม"], sv["หลังออก"], sv["ค่าธรรมเนียม"],
                   sv["ค่าถือ"], sv["สุทธิ"]]},
        {"โจทย์": "(เปลี่ยนเลขหนึ่งตัว) ครึ่งส่วนต่างของ B กว้างเป็น 0.1 · ชั้นส่วนต่างเข้า/ออก และสุทธิ",
         "คำตอบ": [ex["ข้อ2"]["ส่วนต่างเข้ารวม"], ex["ข้อ2"]["ส่วนต่างออกรวม"], ex["ข้อ2"]["หลังออก"], ex["ข้อ2"]["สุทธิ"]]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ไม้ 3 จบเพราะเวลา +1 แทน −22 · บัญชีสะสม · ลึกสุดจากยอด · เฉลี่ย · สองเท่าของการแกว่งที่ 3 ไม้",
         "คำตอบ": [ex["ข้อ3"]["สะสม"], ex["ข้อ3"]["ลึกสุดจากยอด"], ex["ข้อ3"]["เฉลี่ย"], ex["ข้อ3"]["สองเท่าสามไม้"]]},
        {"โจทย์": "(ตัดสินใจ) กระดาษ 16 ไม้ เฉลี่ย +5 แกว่งเท่าการ์ด · สองเท่าของการแกว่ง และไม้ที่ต้องมี",
         "คำตอบ": [ex["ข้อ4"]["สองเท่า"], ex["ข้อ4"]["ไม้ที่ต้องมี"]]},
        {"โจทย์": "(ถ่ายโอน) funding carry ภาค 1 คาดสามรอบ ได้จริง +10 +10 −5 · คาดพลาดเท่าไร ชั้นไหนเปลี่ยนเครื่องหมาย",
         "คำตอบ": [ex["ข้อ5"]["คาดสามรอบ"], ex["ข้อ5"]["จริงรวม"], ex["ข้อ5"]["คาดพลาด"]]},
    ]
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
        "_แบบฝึก": drills,
    }
