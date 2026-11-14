"""บท 13 — กลับจริง แต่ทันไหม · ค่าใหม่ที่บทใช้ (ปลั๊กอินของ tools/sab_figures.py)

ทุกค่าคำนวณจาก data (ch12 ไม้ 3 · ch13 ตาราง φ / แตะเป้า) หรือจากการจำลอง AR(1) ด้วย seed ของบท (20261111)
ไม่มีผลลัพธ์พิมพ์ลอย · การจำลองใช้ random.Random แยกตัว จึงไม่กระทบตัวเลขเดิมของ sab_figures.py
"""

import math
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


def _three_worlds_carry(start=2.0, sd=0.5, trials=100_000, phis=(0.80, 0.99, 1.00)):
    """กฎเดียวสามโลกซ้ำ (ลำดับสุ่มเดียวกับ three_worlds ใน sab_figures.py ทุกตัว) + จำนวนช่วงที่ถือของแต่ละไม้
    → ค่าคาดหมายหลังค่าถือ ⓝ (แผน 3.5 แถว "ค่าถือคู่" · แผนบท 13)"""
    rng = random.Random(SEED)
    out = {}
    for phi in phis:
        tot, held = 0.0, 0
        for _ in range(trials):
            x = start
            for t in range(1, 4):
                x = phi * x + rng.gauss(0.0, sd)
                liq = 10 * (start - x) - 1
                if liq <= -15 or x <= 0.5 or t >= 3:
                    tot += liq
                    held += t
                    break
        out[f"{phi:.2f}"] = (tot / trials, held / trials)
    return out


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
        "phiจากตารางปัด": q(D("0.5") ** (D(1) / med_d), 2),
        "phiจริง": FAN_PHI,
        "ครึ่งชีวิตจริงปัด": c13["ตารางphi"]["0.99"]["ครึ่งชีวิตปัด"],
    }

    # ── กล่องแปลงหน่วยเวลา: φ ต่อวัน → ต่อสัปดาห์ (7 ช่วง) ──
    week = {k: q(D(k) ** 7, 2) for k in ("0.80", "0.99")}
    unit = {"ต่อวัน": {"0.80": 0.8, "0.99": 0.99}, "ต่อสัปดาห์": week,
            "ครึ่งชีวิตสัปดาห์_0.99": q(D(str(c13["ตารางphi"]["0.99"]["ครึ่งชีวิต"])) / 7, 1)}

    # ── 🔎 φ จากข้อมูลสั้นมักดูกลับเร็วเกินจริง ──
    med_est, below = _short_phi()
    short = {"ความยาว": SHORT_LEN, "ครั้ง": SHORT_REPS, "phiจริง": 0.99,
             "มัธยฐานที่ประมาณได้": q(D(str(med_est)), 2),
             "ต่ำกว่าจริงเปอร์เซ็นต์": q(D(str(below)) * 100, 1),
             "ครึ่งชีวิตของค่าที่ประมาณได้": q(D(str(math.log(0.5) / math.log(med_est))), 0)}

    # ── กฎเดียวสามโลกหลังค่าถือ: ขา short (A ผ่าน perp) รับ/จ่าย ต่อรอบ × รอบต่อช่วง × ช่วงที่ถือ ──
    carry = data["บัญชีมิน"]["ค่าถือคู่"]
    per_bar = D(str(carry["ต่อรอบ"])) * carry["รอบต่อช่วง"]          # 0.1 × 3 = 0.3 ต่อช่วง
    worlds = {}
    for k, (ev, held) in _three_worlds_carry().items():
        assert q(D(str(ev)), 2) == c13["กฎเดียวสามโลก"][k]["ค่าคาดหมายต่อไม้ก่อนค่าถือ"], "ลำดับสุ่มไม่ตรง three_worlds"
        evd, hd = D(str(ev)), D(str(held))
        worlds[k] = {"ช่วงถือเฉลี่ย": q(hd, 2), "ค่าถือต่อไม้": q(per_bar * hd, 2),
                     "หลังค่าถือถ้ารับ": q(evd + per_bar * hd, 2), "หลังค่าถือถ้าจ่าย": q(evd - per_bar * hd, 2)}
    worlds["ค่าถือต่อช่วง"] = q(per_bar, 1)

    ends = {k: q(D(str(r["ระดับ"][-1])), 2) for k, r in c13["ตารางphi"].items()}

    lv2 = {k: [q(D(str(v)), 2) for v in c13["ตารางphi"][k]["ระดับ"]] for k in ("0.80", "0.99")}
    ex = [D(2) * D("0.9") ** t for t in range(5)]

    return {
        "ปลายทาง4ช่วงปัด": ends,
        "ระดับปัด": lv2,
        "แบบฝึกก": {"phi": 0.9, "ระดับ": [q(v, 2) for v in ex], "สุทธิ": q(sets * (D(2) - ex[-1]) - cost, 2)},
        "เส้นคุ้มต้นทุน": q(D(str(c13["กติกาตารางphi"]["เริ่ม"])) - cost / sets, 1),
        "ไม้3": trade3,
        "เส้นทาง20": fan,
        "ใบ13นับ": count,
        "แปลงหน่วย": unit,
        "ข้อมูลสั้น": short,
        "สามโลกค่าถือ": worlds,
        "_claims": [{"id": "ch13-crowding-slower",
                     "ข้อความ": "Mean Reversion ของคู่อ่อนลงได้เมื่อเหตุผลที่ผูกสองเหรียญจางลง หรือเมื่อคนทำงานเดียวกันมากขึ้นจนระยะห่างที่กลับเร็วถูกเก็บไปก่อน "
                                 "ส่วนที่เหลือให้คนมาทีหลังมักกลับช้าหรือไม่กลับ · คู่ที่ยังกลับเร็วก็ยังมีได้ แต่ระยะที่เหลือให้เก็บเล็กลง — "
                                 "ตัวเลข φ 0.80 → 0.99 ในบท 13 เป็นตัวเลขสมมติ ไม่ใช่ค่าที่วัดจากตลาด",
                     "ระดับหลักฐาน": "สมมติฐาน", "แหล่ง": None, "บท": [13]}],
        "_แบบฝึก": [
            {"โจทย์": "φ 0.90 ต่อช่วง เริ่ม 2 short 10 ชุด ถือ 4 ช่วง ต้นทุน 1 — กำไรสุทธิตามเส้นค่าเฉลี่ย",
             "คำตอบ": q(sets * (D(2) - D(2) * D("0.9") ** 4) - cost, 2)},
            {"โจทย์": "เพื่อนประมาณ φ ได้ 0.99 แล้วบอกว่ามีแรงดึงกลับ ถือ 3 ช่วงตามการ์ดก็คุ้ม — เห็นด้วยไหม"},
            {"โจทย์": "basis spot–perp ที่ห่างจากปกติเหลือ 98% ต่อวัน — ครึ่งชีวิตกี่วัน และทำไมใช้ φ กับ dated futures ไม่ได้",
             "คำตอบ": next(r["ครึ่งชีวิต"] for r in c13["phiเป็นครึ่งชีวิต"] if r["phi"] == 0.98)},
        ],
    }
