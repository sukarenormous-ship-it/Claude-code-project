"""บท 10 — คู่ที่สวยที่สุดจาก 200 คู่ · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py)

ทุกค่าคำนวณจากค่าที่สร้างแล้วใน data หรือจากการจำลองชุดเดิมของบท 9 (seed 7 · ฟังก์ชันเดียวกับ sab_figures.py)
"""

import importlib.util
import os
import random
import statistics

_HERE = os.path.dirname(os.path.abspath(__file__))
_THRESHOLDS = (70, 80, 85, 90, 95)      # เกณฑ์ "อยู่ในกรอบช่วงทดสอบอย่างน้อย x%" ที่ใช้ทำตารางอัตราผ่าน


def _lib():
    """โหลดฟังก์ชันจำลองจาก sab_figures.py ด้วยชื่อโมดูลอื่น (บล็อก __main__ ไม่ทำงาน · ไม่ซ้ำตรรกะ)"""
    path = os.path.join(os.path.dirname(_HERE), "sab_figures.py")
    spec = importlib.util.spec_from_file_location("sab_figures_lib_ch10", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _inband_rows(L, seed, pairs=200):
    """เรียก RNG ลำดับเดียวกับ o_v09_population → สัดส่วนวันในกรอบช่วงทดสอบรายคู่ ของคู่ไม่มีเชือก / มีเชือก"""
    rng = random.Random(seed)
    n, nf = 500, 250
    out = {}
    for name, maker in (("ไม่มีเชือก", L.pair_h), ("มีเชือก", L.pair_c)):
        rows = []
        for _ in range(pairs):
            a, b = maker(rng, n)
            sp = [x - y for x, y in zip(a, b)]
            rows.append(L.zstats(sp, nf)[2])
        out[name] = rows
    return out


def _rates(rows, t):
    fake = sum(1 for v in rows["ไม่มีเชือก"] if v * 100 >= t) / len(rows["ไม่มีเชือก"])
    cut = sum(1 for v in rows["มีเชือก"] if v * 100 < t) / len(rows["มีเชือก"])
    return fake, cut


def extend(data, D, q):
    L = _lib()
    c10 = data["ch10"]
    pct = lambda x, n=1: q(D(str(x)) * 100, n)  # noqa: E731

    # ตารางอัตราผ่านของคู่ปลอมสำเร็จรูป (seed ของบท 9 = ตัวอย่าง · seed 1–30 = ช่วง)
    base = _inband_rows(L, L.SEED_POP)
    many = [_inband_rows(L, sd) for sd in L.ROBUST_SEEDS]
    table = []
    for t in _THRESHOLDS:
        fake, cut = _rates(base, t)
        fakes = [_rates(r, t)[0] for r in many]
        table.append({"ในกรอบขั้นต่ำ": t, "ปล่อยคู่ปลอม": pct(fake), "ตัดคู่จริง": pct(cut),
                      "ปล่อยคู่ปลอมมัธยฐาน30ชุด": pct(statistics.median(fakes)),
                      "ปล่อยคู่ปลอมต่ำสุด30ชุด": pct(min(fakes)), "ปล่อยคู่ปลอมสูงสุด30ชุด": pct(max(fakes))})
    row85 = next(r for r in table if r["ในกรอบขั้นต่ำ"] == 85)
    assert row85["ปล่อยคู่ปลอม"] == c10["เกณฑ์ในกรอบ85"]["ปล่อยคู่ปลอม"], "จำลองซ้ำไม่ตรงค่าเดิมของบท 9/10"

    top1, all200, top10 = c10["อันดับ1"], c10["ทั้ง200คู่"], c10["10อันดับแรก"]
    miss = {k: pct(D("0.95") ** int(k)) for k in c10["ลองหลายครั้ง"]}
    v2 = _v2(data, D, q, L, base, table)
    exercises = v2.pop("_แบบฝึก_v2")
    return {
        "อัตราผ่านคู่ปลอม": table,
        "อัตราผ่านคู่ปลอม_ที่มา": "คู่ไม่มีเชือก 200 คู่ + คู่มีเชือก 200 คู่ ชุดจำลองเดียวกับบท 9 (seed 7) · ช่วง = seed 1–30",
        "ลองหลายครั้ง_ไม่เจอเลย": miss,
        "อันดับ1เทียบเฉลี่ยเท่า": q(D(str(top1["ข้ามค่ากลาง"])) / D(str(all200["ข้ามค่ากลาง"])), 1),
        "อันดับ1นอกกรอบ": q(D(100) - D(str(top1["ในกรอบ"])), 1),
        "คัดแล้วข้ามเพิ่ม": q(D(str(top10["ข้ามค่ากลาง"])) - D(str(all200["ข้ามค่ากลาง"])), 1),
        "คัดแล้วในกรอบเพิ่ม": q(D(str(top10["ในกรอบ"])) - D(str(all200["ในกรอบ"])), 1),
        "ทะเบียน": {"ในกรอบขั้นต่ำ": 85, "ประเมินใหม่ทุกวัน": 90},
        "คูณ095": {"2ครั้ง": q(D("0.95") ** 2, 4), "10ครั้ง": q(D("0.95") ** 10, 3)},
        "v2": v2,                                   # คู่มือ v2 §8: คีย์ใหม่ของ v2 อยู่ใต้ ch10.v2.*
        "_แบบฝึก": exercises,
    }


# ── v2: ตัวเลขกลางทางที่บทเขียนให้เห็น ──
_BUCKETS = ((0, 70), (70, 80), (80, 85), (85, 90), (90, 95), (95, 101))   # ช่วง "อยู่ในกรอบช่วงทดสอบ (%)" ของกราฟสองหัว


def _crossings(xs, mean=0):
    """นับครั้งข้าม Mean แบบเดียวกับ zstats ของ sab_figures.py: ฝั่ง (X − Mean > 0) เปลี่ยนระหว่างวันติดกัน
    ค่าที่เท่ากับ Mean พอดีนับว่ายังไม่ขึ้นเหนือ Mean (แตะแล้วไม่ข้าม)"""
    out = []
    for i in range(1, len(xs)):
        if (xs[i - 1] - mean > 0) != (xs[i] - mean > 0):
            out.append(i)
    return out


def _selection_rows(L):
    """เรียก RNG ลำดับเดียวกับ o_v09_selection (seed 11) → (ครั้งข้าม, ในกรอบ, ระยะไกลสุด) ของ 200 คู่ไม่มีเชือก + 10 คู่มีเชือก"""
    rng = random.Random(L.SEED_SEL)
    n, nf = 500, 250
    rows, gen = [], []
    for _ in range(200):
        a, b = L.pair_h(rng, n)
        _, cross, inband, maxz, _, _ = L.zstats([x - y for x, y in zip(a, b)], nf)
        rows.append((cross, inband, maxz))
    for _ in range(10):
        a, b = L.pair_c(rng, n)
        _, cross, inband, maxz, _, _ = L.zstats([x - y for x, y in zip(a, b)], nf)
        gen.append((cross, inband, maxz))
    return rows, gen


def _v2(data, D, q, L, base, table):
    c9, c10 = data["ch09"], data["ch10"]
    dd = lambda x: D(str(x))  # noqa: E731

    # ① นับครั้งข้าม Mean ด้วยมือบนตาราง 20 วันของบท 9 (Mean 0)
    x20 = c9["นับมือ20วัน"]["X"]
    cr = _crossings(x20)
    hand = {
        "ครั้ง": len(cr), "วัน": len(x20),
        "ต่อวัน": q(D(len(cr)) / D(len(x20)), 2), "ต่อร้อยวัน": q(D(len(cr)) * 100 / D(len(x20)), 0),
        "จุดข้าม": [{"จากวัน": i, "ถึงวัน": i + 1, "Xก่อน": x20[i - 1], "Xหลัง": x20[i]} for i in cr],
        "แตะไม่ข้าม": {"จากวัน": 19, "ถึงวัน": 20, "Xก่อน": x20[18], "Xหลัง": x20[19]},
    }
    assert hand["ครั้ง"] == 3 and x20[19] == 0.0
    nf = c10["ค้น"]["วันช่วงเลือก"]
    rate = lambda c: {"ต่อวัน": q(dd(c) / D(nf), 3), "ต่อร้อยวัน": q(dd(c) * 100 / D(nf), 1)}  # noqa: E731
    rates = {"อันดับ1": rate(c10["อันดับ1"]["ข้ามค่ากลาง"]), "เฉลี่ย200": rate(c10["ทั้ง200คู่"]["ข้ามค่ากลาง"]),
             "คู่จริง": rate(c10["คู่จริง"]["ข้ามค่ากลาง"])}

    # ② คู่อันดับ 1 ใน Test Period เป็นจำนวนวัน · 1 SD ของคู่นี้คิดเป็นระยะกี่ %
    top1 = c10["อันดับ1"]
    days_in = int(q(dd(top1["ในกรอบ"]) * D(nf) / 100, 0))
    sd_pct = dd(top1["ระยะlog"]) / dd(top1["zต่ำสุด"]) * 100
    t1 = {"วันในกรอบ": days_in, "วันนอกกรอบ": nf - days_in,
          "SDเปอร์เซ็นต์": q(sd_pct, 1), "ระยะเป็นจุดของSD": q(dd(top1["ระยะสูงสุด"]) * dd(q(sd_pct, 1)), 1)}

    # ③ ชุดของบทนี้ (seed 11): อันดับ 2 · กี่คู่ผ่านเกณฑ์ 85% · 10 อันดับแรกผ่านกี่คู่
    rows, gen = _selection_rows(L)
    ranked = sorted(rows, key=lambda r: -r[0])
    assert ranked[0][0] == top1["ข้ามค่ากลาง"]
    thr = 85 / 100                        # เกณฑ์ของทะเบียน (ch10.ทะเบียน.ในกรอบขั้นต่ำ)
    own = {
        "อันดับ2": {"ข้ามค่ากลาง": ranked[1][0], "ในกรอบ": q(D(ranked[1][1]) * 100, 1), "ระยะสูงสุด": q(D(ranked[1][2]), 2)},
        "ทั้ง200ผ่าน85": sum(1 for r in rows if r[1] >= thr),
        "10อันดับผ่าน85": sum(1 for r in ranked[:10] if r[1] >= thr),
        "คู่จริงผ่าน85": sum(1 for g in gen if g[1] >= thr),
        "ข้ามมากสุด": ranked[0][0], "ข้ามน้อยสุด": ranked[-1][0],
    }

    # ④ ตารางเกณฑ์เป็นจำนวนคู่ (จาก 200) + ส่วนต่างจากแถวก่อน · ชุดบท 9 (seed 7)
    npair = len(base["ไม่มีเชือก"])
    counts, prev = [], None
    for row in table:
        t = row["ในกรอบขั้นต่ำ"]
        fake = sum(1 for v in base["ไม่มีเชือก"] if v * 100 >= t)
        cut = sum(1 for v in base["มีเชือก"] if v * 100 < t)
        assert q(D(fake) * 100 / D(npair), 1) == row["ปล่อยคู่ปลอม"] and q(D(cut) * 100 / D(npair), 1) == row["ตัดคู่จริง"]
        item = {"ในกรอบขั้นต่ำ": t, "คู่ปลอมผ่าน": fake, "คู่จริงถูกตัด": cut}
        if prev:
            item["คู่ปลอมลด"] = prev["คู่ปลอมผ่าน"] - fake
            item["คู่จริงถูกตัดเพิ่ม"] = cut - prev["คู่จริงถูกตัด"]
        counts.append(item)
        prev = item
    buckets = []
    for lo, hi in _BUCKETS:
        buckets.append({"ตั้งแต่": lo, "ต่ำกว่า": hi,
                        "ไม่มีเชือก": sum(1 for v in base["ไม่มีเชือก"] if lo <= v * 100 < hi),
                        "มีเชือก": sum(1 for v in base["มีเชือก"] if lo <= v * 100 < hi)})
    assert sum(b["ไม่มีเชือก"] for b in buckets) == npair and sum(b["มีเชือก"] for b in buckets) == npair
    c85 = next(c for c in counts if c["ในกรอบขั้นต่ำ"] == 85)
    assumed = D("0.05")

    # ⑤ ลองหลายครั้ง: สองคู่ก่อน · 200 คู่ที่ 5%
    tries = {"สองคู่ไม่หลอก": q(D("0.95") ** 2 * 100, 2), "สองคู่เจอ": q((1 - D("0.95") ** 2) * 100, 2),
             "คาดคู่ปลอมใน200": q(D(200) * assumed, 0), "ห้าคู่ไม่หลอก": q(D("0.95") ** 5, 3),
             "สิบคู่ผิดแบบบวก": q(D(10) * assumed * 100, 0),
             "วัดได้เทียบสมมติเท่า": q(dd(c10["เกณฑ์ในกรอบ85"]["ปล่อยคู่ปลอม"]) / (assumed * 100), 1)}

    # ⑥ กรอบรั่ว: ส่วนห่างของสองแบบ · วันที่ 24 ของ A–B เมื่อ Mean เลื่อนเป็น 0.37
    lk = c10["กรอบรั่ว"]
    test = c9["v2"]["วันทดสอบ"]
    leak = {"ห่างเมื่อตรึง": q(dd(lk["มีเชือกไม่รั่ว"]) - dd(lk["ไม่มีเชือกไม่รั่ว"]), 1),
            "ห่างเมื่อรั่ว": q(dd(lk["ไม่มีเชือก"]) - dd(lk["มีเชือก"]), 1),
            "วัน24X": test["X"][3], "วัน24ห่างเมื่อรั่ว": q(dd(test["X"][3]) - dd(test["Mean30"]), 2)}

    # ⑦ แบบฝึก
    xt = test["X"]
    cr_t = _crossings(xt)
    ex1 = {"ครั้ง": len(cr_t), "วัน": len(xt), "ต่อวัน": q(D(len(cr_t)) / D(len(xt)), 1),
           "ต่อร้อยวัน": q(D(len(cr_t)) * 100 / D(len(xt)), 0), "ข้ามแรกจากวัน": 20 + cr_t[0], "ข้ามสองจากวัน": 20 + cr_t[1]}
    c80 = next(c for c in counts if c["ในกรอบขั้นต่ำ"] == 80)
    c90 = next(c for c in counts if c["ในกรอบขั้นต่ำ"] == 90)
    nstock = 12
    npairs_stock = nstock * (nstock - 1) // 2
    ex5 = {"หุ้น": nstock, "คู่": npairs_stock, "คาดคู่ปลอม": q(D(npairs_stock) * assumed, 1),
           "เจออย่างน้อยหนึ่ง": q((1 - D("0.95") ** npairs_stock) * 100, 1)}
    exercises = [
        {"โจทย์": "นับครั้งข้าม Mean ของ A–B วันที่ 21–30 (ไม้บรรทัดตรึง Mean 0) · ครั้ง · ต่อวัน", "คำตอบ": [ex1["ครั้ง"], ex1["ต่อวัน"]]},
        {"โจทย์": "ลอง 10 คู่ไม่มีเชือก โอกาสดูผ่านโดยบังเอิญ 5% ต่อคู่ · โอกาสเจออย่างน้อยหนึ่งคู่ (%)",
         "คำตอบ": c10["ลองหลายครั้ง"]["10"]},
        {"โจทย์": "ยอมให้คู่จริงถูกตัดไม่เกิน 20 จาก 200 คู่ · เลือกเกณฑ์ไหน · คู่ปลอมผ่านกี่คู่",
         "คำตอบ": [c80["ในกรอบขั้นต่ำ"], c80["คู่ปลอมผ่าน"], c80["คู่จริงถูกตัด"]]},
        {"โจทย์": "เพื่อนลองเพิ่ม 50 คู่บนช่วงเดิมแล้วเจอคู่ในกรอบ 90% · ลงสถานะอะไร (แนวคำตอบ: ไม่ใช่ผ่าน — โชคจากการลอง 92.3% · "
                  "ช่วงทดสอบถูกใช้เลือกแล้ว · เกณฑ์ 90% ยังปล่อยคู่ปลอมผ่าน 59 จาก 200)", "คำตอบ": [c10["ลองหลายครั้ง"]["50"], c90["คู่ปลอมผ่าน"]]},
        {"โจทย์": "หุ้นกลุ่มเดียวกัน 12 ตัว จับคู่ได้กี่คู่ · ที่ 5% ต่อคู่ คาดคู่ปลอมกี่คู่ · โอกาสเจออย่างน้อยหนึ่ง (%)",
         "คำตอบ": [ex5["คู่"], ex5["คาดคู่ปลอม"], ex5["เจออย่างน้อยหนึ่ง"]]},
    ]
    return {
        "ข้ามมือ20วัน": hand, "อัตราข้าม": rates, "อันดับ1ทดสอบ": t1, "ชุดบทนี้": own,
        "เกณฑ์นับคู่": counts, "เกณฑ์85": {"คู่ปลอมผ่าน": c85["คู่ปลอมผ่าน"], "คู่จริงถูกตัด": c85["คู่จริงถูกตัด"], "จาก": npair},
        "กองคู่": buckets, "ลองหลายครั้ง": tries, "กรอบรั่ว": leak,
        "แบบฝึก": {"ข้อ1": ex1, "ข้อ5": ex5},
        "_แบบฝึก_v2": exercises,
    }
