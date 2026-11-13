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
        "_แบบฝึก": [
            {"โจทย์": "ลอง 10 คู่ที่ไม่มีเชือก แต่ละคู่มีโอกาสดูผ่านโดยบังเอิญ 5% · โอกาสเจออย่างน้อยหนึ่งคู่ที่ดูผ่าน (%)",
             "คำตอบ": c10["ลองหลายครั้ง"]["10"]},
            {"โจทย์": "เพื่อนลองเพิ่ม 50 คู่บนช่วงเดิมแล้วเจอคู่ในกรอบ 90% · ลงสถานะอะไร (แนวคำตอบ: ผู้สมัคร — โชคจากการลอง "
                      "ช่วงทดสอบถูกใช้เลือกแล้ว และเกณฑ์ 90% ยังปล่อยคู่ปลอมผ่าน)"},
            {"โจทย์": "ทำไมรายชื่อผู้สมัครต้องรวมเหรียญที่ถูกถอดออกระหว่างทาง · ใช้กับ backtest ที่ดีที่สุดจากการลองตั้งค่า 100 แบบของคนขายบอทอย่างไร"},
        ],
    }
