"""บท 13 — กลับจริง แต่ทันไหม · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py)

ทุกค่าคำนวณจาก data (ch12 ไม้ 3 · ch13 ตาราง φ / แตะเป้า) หรือจากการจำลอง AR(1) ด้วย seed ของบท (20261111)
ไม่มีผลลัพธ์พิมพ์ลอย · การจำลองใช้ random.Random แยกตัว จึงไม่กระทบตัวเลขเดิมของ sab_figures.py
"""

import random
import statistics

SEED = 20261111          # seed ของบท 13 (ตรง SEED_FP ใน sab_figures.py)
FAN_N, FAN_T = 20, 24    # 20 เส้นทาง · 24 ช่วง
FAN_PHI, FAN_SD = 0.99, 0.5   # โลกเดียวกับแถวที่ 3 ของตาราง "แตะเป้า" (44.8%)
SHORT_LEN, SHORT_REPS = 60, 2000   # φ จากข้อมูลสั้น (🔎)


def _fan(start=2.0):
    """เดินทีละช่วงจนแตะเป้า X ≤ 1 (มินหยุดนับตรงนั้น) หรือครบ 24 ช่วง · ถึง 3 ระหว่างทางไม่หยุด แค่จดไว้"""
    rng = random.Random(SEED)
    paths = []
    for _ in range(FAN_N):
        x, p = start, [start]
        for _ in range(FAN_T):
            x = FAN_PHI * x + rng.gauss(0.0, FAN_SD)
            p.append(x)
            if x <= 1:
                break
        paths.append(p)
    return paths


def _first_event(p):
    """('เป้า'|'ขอบ'|None, ช่วงที่เกิด) — X ≥ 3 ก่อนแตะ X ≤ 1 = ถึงขอบก่อน (นิยามเดียวกับ 44.8%)"""
    for t, x in enumerate(p[1:], 1):
        if x >= 3:
            return "ขอบ", t
        if x <= 1:
            return "เป้า", t
    return None, None


def _hit_time(p):
    """ช่วงแรกที่ X ≤ 1 (นับมือแบบใบ 13) · None = ไม่แตะใน 24 ช่วง"""
    for t, x in enumerate(p[1:], 1):
        if x <= 1:
            return t
    return None


def _ols_phi(xs):
    a, b = xs[:-1], xs[1:]
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    cov = sum((u - ma) * (v - mb) for u, v in zip(a, b))
    var = sum((u - ma) ** 2 for u in a)
    return cov / var


def _short_phi(phi=0.99, sd=0.5):
    """ประมาณ φ จากข้อมูล 60 ช่วง (เริ่มจากการกระจายนิ่ง) ซ้ำ 2,000 ครั้ง → มัธยฐาน · สัดส่วนที่ได้ต่ำกว่าจริง"""
    rng = random.Random(SEED + 1)
    stat_sd = sd / (1 - phi * phi) ** 0.5
    ests = []
    for _ in range(SHORT_REPS):
        x = rng.gauss(0.0, stat_sd)
        xs = [x]
        for _ in range(SHORT_LEN - 1):
            x = phi * x + rng.gauss(0.0, sd)
            xs.append(x)
        ests.append(_ols_phi(xs))
    below = sum(1 for e in ests if e < phi) / len(ests)
    return statistics.median(ests), below


def extend(data, D, q):
    c12, c13 = data["ch12"], data["ch13"]
    entry = D(str(c12["จุดเข้า"]))                 # 2.1
    now = D(str(c12["เส้นทาง"]["3"]["X"][2]))      # 2.8 (ค้าง)
    sets = D(str(c13["กติกาตารางphi"]["ชุด"]))     # 10
    cost = D(str(c13["กติกาตารางphi"]["ต้นทุน"]))  # 1
    left = 2                                        # การ์ดครบ 3 ช่วง · ถือมาแล้ว 1 ช่วง

    # ── ฉาก: ไม้ 3 ที่ 2.8 ถ้าครบเวลาอีก 2 ช่วงในแต่ละโลก (เส้นค่าเฉลี่ย ไม่ใช่เส้นทาง) ──
    trade3 = {}
    for k in ("0.80", "0.99", "1.00"):
        phi = D(k)
        x_end = now * phi ** left
        trade3[k] = {"Xคาดตอนครบเวลา": q(x_end, 2), "สุทธิถ้าครบเวลา": q(sets * (entry - x_end) - cost, 2)}
    trade3["ช่วงที่เหลือ"] = left
    trade3["ระยะเพิ่มขึ้นเปอร์เซ็นต์"] = q((now - entry) / entry * 100, 0)   # 2.1 → 2.8 = +33%

    # ── 20 เส้นทาง (★ sab-paths-fan) ──
    paths = _fan()
    events = [_first_event(p) for p in paths]
    hits = [_hit_time(p) for p in paths]
    hit_sorted = sorted(h for h in hits if h is not None)
    n_miss = sum(1 for h in hits if h is None)
    # มัธยฐานของ 20 ค่า (ค่าที่ไม่แตะใน 24 ช่วงนับเป็น "มากกว่า 24" อยู่ท้ายแถว)
    full = hit_sorted + [10 ** 6] * n_miss
    med = (full[9] + full[10]) / 2
    assert med < 10 ** 5, "เส้นทางที่แตะเป้ามีไม่ถึงครึ่ง — มัธยฐานนับมือใช้ไม่ได้"
    med_d = D(str(med))
    fan = {
        "phi": FAN_PHI, "แรงสะบัด": FAN_SD, "จำนวน": FAN_N, "ช่วง": FAN_T,
        "เส้นทาง": [[q(v, 2) for v in p] for p in paths],
        "เส้นค่าเฉลี่ย": [q(D(2) * D(str(FAN_PHI)) ** t, 2) for t in range(FAN_T + 1)],
        "ค่าเฉลี่ยที่ช่วง24": q(D(2) * D(str(FAN_PHI)) ** FAN_T, 2),
        "แตะเป้าก่อน": sum(1 for e, _ in events if e == "เป้า"),
        "ถึงขอบก่อน": sum(1 for e, _ in events if e == "ขอบ"),
        "ยังไม่ถึงทั้งสอง": sum(1 for e, _ in events if e is None),
        "เหตุการณ์": [{"ชนิด": e, "ช่วง": t} for e, t in events],
    }

    # ── ใบ 13 ของมิน: ทดสอบวิธีนับบนโลกที่รู้คำตอบ (φ 0.99 · ครึ่งชีวิตจริงราว 69) ──
    count = {
        "นับได้เรียง": hit_sorted,
        "ไม่แตะใน24ช่วง": n_miss,
        "แตะใน24ช่วง": len(hit_sorted),
        "มัธยฐานนับ": q(med_d, 1) if med != int(med) else int(med),
        "phiจากตาราง": q(D("0.5") ** (D(1) / med_d), 3),
        "phiจริง": FAN_PHI,
        "ครึ่งชีวิตจริงปัด": c13["ตารางphi"]["0.99"]["ครึ่งชีวิตปัด"],
    }

    # ── กล่องแปลงหน่วยเวลา: φ ต่อวัน → ต่อสัปดาห์ (7 ช่วง) ──
    week = {k: q(D(k) ** 7, 3) for k in ("0.80", "0.99")}
    unit = {"ต่อวัน": {"0.80": 0.8, "0.99": 0.99}, "ต่อสัปดาห์": week,
            "ครึ่งชีวิตสัปดาห์_0.99": q(D(str(c13["ตารางphi"]["0.99"]["ครึ่งชีวิต"])) / 7, 1)}

    # ── 🔎 φ จากข้อมูลสั้นมักดูกลับเร็วเกินจริง ──
    med_est, below = _short_phi()
    short = {"ความยาว": SHORT_LEN, "ครั้ง": SHORT_REPS, "phiจริง": 0.99,
             "มัธยฐานที่ประมาณได้": q(D(str(med_est)), 2),
             "ต่ำกว่าจริงเปอร์เซ็นต์": q(D(str(below)) * 100, 1),
             "ครึ่งชีวิตของค่าที่ประมาณได้": q(D(str(__import__("math").log(0.5) / __import__("math").log(med_est))), 0)}

    # ── ตาราง "ครึ่งชีวิต ≠ เวลาแตะเป้า" (สามแถวจาก แตะเป้า) ส่วนต่างเป็นเท่า ──
    fp = c13["แตะเป้า"]

    ends = {k: q(D(str(r["ระดับ"][-1])), 2) for k, r in c13["ตารางphi"].items()}

    return {
        "ปลายทาง4ช่วงปัด": ends,
        "เส้นคุ้มต้นทุน": q(D(str(c13["กติกาตารางphi"]["เริ่ม"])) - cost / sets, 1),
        "ไม้3": trade3,
        "เส้นทาง20": fan,
        "ใบ13นับ": count,
        "แปลงหน่วย": unit,
        "ข้อมูลสั้น": short,
        "แตะเป้าเร็วกว่าครึ่งชีวิต": q(D(str(fp[2]["ครึ่งชีวิต"])) - D(str(fp[2]["มัธยฐานช่วง"])), 0),
        "_แบบฝึก": [
            {"โจทย์": "φ 0.90 ต่อช่วง เริ่ม 2 short 10 ชุด ถือ 4 ช่วง ต้นทุน 1 — กำไรสุทธิตามเส้นค่าเฉลี่ย",
             "คำตอบ": q(sets * (D(2) - D(2) * D("0.9") ** 4) - cost, 2)},
            {"โจทย์": "คู่ใหม่นับเวลาจาก 2 ถึง 1 ได้มัธยฐาน 10 ช่วง แต่ยอมถือ 3 ช่วง — เปิดไหม"},
            {"โจทย์": "basis เหลือ 98% ต่อวัน — ครึ่งชีวิตกี่วัน และใช้กับ dated futures ได้ไหม"},
        ],
    }
