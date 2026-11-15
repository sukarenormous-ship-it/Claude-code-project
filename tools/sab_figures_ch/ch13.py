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


def _three_worlds_v2(cost, start=2.0, sd=0.5, trials=100_000, phis=(0.80, 0.99, 1.00), budget=-15.0,
                     exit_line=0.5, max_hold=3, sets=10):
    """กฎเดียวสามโลกด้วยฐานต้นทุน v2 (ต้นทุน 2) · กติกาเดียวกับ three_worlds ใน sab_figures.py ทุกข้อ ยกเว้นต้นทุน
    คืน เหตุออก · ไม้กำไร · ค่าคาดหมาย · ช่วงถือเฉลี่ย · Standard Deviation ของผลต่อไม้ (ใช้คิดไม้ที่ต้องมีแบบบท 15)"""
    rng = random.Random(SEED)
    out = {}
    for phi in phis:
        reasons = {"งบ": 0, "เป้า": 0, "เวลา": 0}
        tot = tot2 = 0.0
        wins = held = 0
        for _ in range(trials):
            x = start
            for t in range(1, max_hold + 1):
                x = phi * x + rng.gauss(0.0, sd)
                liq = sets * (start - x) - cost
                if liq <= budget:
                    r = "งบ"
                elif x <= exit_line:
                    r = "เป้า"
                elif t >= max_hold:
                    r = "เวลา"
                else:
                    continue
                reasons[r] += 1
                tot += liq
                tot2 += liq * liq
                wins += liq > 0
                held += t
                break
        mean = tot / trials
        out[f"{phi:.2f}"] = {"เป้า": reasons["เป้า"] / trials, "งบ": reasons["งบ"] / trials,
                             "เวลา": reasons["เวลา"] / trials, "กำไร": wins / trials, "ค่าคาดหมาย": mean,
                             "ช่วงถือ": held / trials, "sd": (tot2 / trials - mean * mean) ** 0.5}
    return out


def _v2(data, D, q, fan_count):
    """บท 13 ด้วยฐานต้นทุนเดียว (ch11.v2 · ต้นทุน 2) + ตัวกลางที่ทำให้ Z-score / φ คิดตามได้ (รายงาน B S13–S16 · C §2.6 ข้อ 9, 11)"""
    c12, c13 = data["ch12"], data["ch13"]
    cost = D(str(data["ch11"]["v2"]["ต้นทุน"]["ไปกลับ"]))      # 2
    sets = D(str(c13["กติกาตารางphi"]["ชุด"]))                  # 10
    start = D(str(c13["กติกาตารางphi"]["เริ่ม"]))               # 2

    # ── ตารางคูณถือ 4 ช่วง: ปลายทางไม่ปัด และสุทธิ ──
    table = {}
    for k in c13["ตารางphi"]:
        end = start * D(k) ** 4
        table[k] = {"ปลายทางไม่ปัด": q(end, 4), "ปลายทางปัด": q(end, 2), "ลด": q(start - end, 4),
                    "สุทธิ4ช่วง": q(sets * (start - end) - cost, 2)}
    breakeven_x = start - cost / sets                              # 1.8: X ต้องลงต่ำกว่านี้จึงคุ้มต้นทุน

    # ── SD ของ X ในแต่ละโลก: ความแปรปรวนนิ่ง = แรงสะบัด² ÷ (1 − φ²) · SD = รากที่สอง ──
    def world_sd(phi, noise):
        phi, noise = D(str(phi)), D(str(noise))
        one = 1 - phi * phi
        var = noise * noise / one
        sd = var.sqrt()
        return {"phi": float(phi), "แรงสะบัด": float(noise), "phiกำลังสอง": q(phi * phi, 4),
                "หนึ่งลบphiกำลังสอง": q(one, 4), "แรงสะบัดกำลังสอง": q(noise * noise, 2),
                "ความแปรปรวน": q(var, 4), "ความแปรปรวนปัด": q(var, 2), "sd": q(sd, 2), "sdละเอียด": q(sd, 4),
                "รากหนึ่งลบphiกำลังสอง": q(one.sqrt(), 3),
                "zของจุดเข้า2": q(start / sd, 2 if sd > 1 else 1),
                "zจากsdปัด": q(start / D(str(q(sd, 2))), 2 if sd > 1 else 1)}
    sd_fp = [world_sd(r["phi"], r["แรงสะบัด"]) for r in c13["แตะเป้า"]]
    for got, r in zip(sd_fp, c13["แตะเป้า"]):
        assert got["zของจุดเข้า2"] == r["ระยะzของจุดเข้า"], "SD ไม่ตรงคอลัมน์ Z-score เดิม"

    # ── กฎเดียวสามโลก (ต้นทุน 2) ──
    worlds = {}
    carry = data["บัญชีมิน"]["ค่าถือคู่"]
    per_bar = D(str(carry["ต่อรอบ"])) * carry["รอบต่อช่วง"]       # 0.3
    for k, r in _three_worlds_v2(float(cost)).items():
        ev, held, sdv = D(str(r["ค่าคาดหมาย"])), D(str(r["ช่วงถือ"])), D(str(r["sd"]))
        w = {"ออกเพราะเป้าเปอร์เซ็นต์": q(D(str(r["เป้า"])) * 100, 1),
             "ออกเพราะงบเปอร์เซ็นต์": q(D(str(r["งบ"])) * 100, 1),
             "ออกเพราะเวลาเปอร์เซ็นต์": q(D(str(r["เวลา"])) * 100, 1),
             "ไม้กำไรเปอร์เซ็นต์": q(D(str(r["กำไร"])) * 100, 1),
             "ค่าคาดหมายต่อไม้ก่อนค่าถือ": q(ev, 2), "ช่วงถือเฉลี่ย": q(held, 2),
             "ค่าถือต่อไม้": q(per_bar * held, 2),
             "หลังค่าถือถ้ารับ": q(ev + per_bar * held, 2), "หลังค่าถือถ้าจ่าย": q(ev - per_bar * held, 2),
             "sdผลต่อไม้": q(sdv, 2)}
        w["ไม้ที่ต้องมี"] = int(math.ceil((2 * sdv / ev) ** 2)) if ev > 0 else None
        if k != "1.00":
            s = world_sd(k, 0.5)
            w["sdของX"] = s["sd"]
            w["zของจุดเข้า2"] = s["zจากsdปัด"]
        else:
            w["sdของX"] = None      # ไม่มีเชือก: ระยะแกว่งโตตามเวลา ไม่มีค่านิ่ง
            w["zของจุดเข้า2"] = None
        worlds[k] = w
    worlds["ค่าถือต่อช่วง"] = q(per_bar, 1)
    worlds["กติกา"] = "การ์ดบท 12 · เริ่ม X = 2 · แรงสะบัด 0.5 · 100,000 ไม้ต่อโลก · ต้นทุน 2 (ch11.v2) · seed 20261111"

    # ── ไม้ 3 ที่ 2.8: อีก 2 ช่วงตามเส้นค่าเฉลี่ย ──
    entry = D(str(c12["จุดเข้า"]))
    now = D(str(c12["เส้นทาง"]["3"]["X"][2]))
    trade3 = {}
    for k in ("0.80", "0.99", "1.00"):
        phi = D(k)
        x_end = now * phi * phi
        trade3[k] = {"phiกำลังสอง": q(phi * phi, 4), "Xคาดไม่ปัด": q(x_end, 4), "Xคาดตอนครบเวลา": q(x_end, 2),
                     "สุทธิถ้าครบเวลา": q(sets * (entry - x_end) - cost, 2)}
    trade3["ตอนนี้"] = q(sets * (entry - now) - cost, 0)              # −9

    # ── ใบ 13: นับมือ → Median → φ (ทุกขั้นเห็นได้) ──
    sorted_hits = fan_count["นับได้เรียง"]
    miss = fan_count["ไม่แตะใน24ช่วง"]
    full = sorted_hits + [None] * miss
    tenth, eleventh = full[9], full[10]
    med = D(tenth + eleventh) / 2
    phi_m = D("0.5") ** (1 / med)
    phi_r = q(phi_m, 2)
    count = {"จำนวน": len(full), "ลำดับที่10": tenth, "ลำดับที่11": eleventh, "ผลรวมสองตัวกลาง": tenth + eleventh,
             "มัธยฐาน": q(med, 0) if med == med.to_integral() else q(med, 1),
             "phiไม่ปัด": q(phi_m, 3), "phiปัด": phi_r, "phiปัดยกกำลังมัธยฐาน": q(D(str(phi_r)) ** int(med), 2),
             "ตารางครึ่งชีวิตล่าง": {"phi": 0.9, "ครึ่งชีวิต": next(r["ครึ่งชีวิต"] for r in c13["phiเป็นครึ่งชีวิต"] if r["phi"] == 0.9)},
             "ตารางครึ่งชีวิตบน": {"phi": 0.95, "ครึ่งชีวิต": next(r["ครึ่งชีวิต"] for r in c13["phiเป็นครึ่งชีวิต"] if r["phi"] == 0.95)}}

    # ── ประมาณ φ ด้วยมือจาก 20 วันของบท 9 (Mean 0): φ ≈ Σ(X วันนี้ × X พรุ่งนี้) ÷ Σ(X วันนี้²) ──
    X = [D(str(v)) for v in data["ch09"]["นับมือ20วัน"]["X"]]
    assert sum(X) == 0, "สูตรมือใช้ได้เมื่อ Mean = 0"
    prods = [a * b for a, b in zip(X[:-1], X[1:])]
    sq = [a * a for a in X[:-1]]
    phi_h = sum(prods) / sum(sq)
    phi_hr = q(phi_h, 2)
    hl = D(str(math.log(0.5) / math.log(phi_hr)))
    hand = {"คู่วัน": len(prods), "ผลคูณ": [q(v, 2) + 0.0 for v in prods], "ผลรวมผลคูณ": q(sum(prods), 2),
            "กำลังสอง": [q(v, 2) for v in sq], "ผลรวมกำลังสอง": q(sum(sq), 2),
            "phiไม่ปัด": q(phi_h, 3), "phi": phi_hr, "ยกกำลังสอง": q(D(str(phi_hr)) ** 2, 2), "ยกกำลังสาม": q(D(str(phi_hr)) ** 3, 2),
            "ครึ่งชีวิต": q(hl, 1),
            "หมายเหตุ": "20 วันเป็นข้อมูลสั้น — 🔎 บท 13 แสดงว่าข้อมูลสั้นมักให้ φ ต่ำกว่าจริง (กลับเร็วเกินจริง)"}

    ex = start * D("0.9") ** 4
    out = {"ต้นทุน": q(cost, 0), "ตารางคูณ": table, "เส้นคุ้มต้นทุน": q(breakeven_x, 1),
           "sdโลก": sd_fp, "กฎเดียวสามโลก": worlds, "ไม้3": trade3, "ใบ13นับ": count, "phiมือบท9": hand,
           "แบบฝึกก": {"ปลายทาง": q(ex, 2), "สุทธิ": q(sets * (start - ex) - cost, 2)}}
    _v2_page(data, D, q, out, sets, start, cost, X)
    return out


def _money_steps(D, q, sets, dist, phi, n):
    """เงินที่ short ‹sets› ชุดได้ในแต่ละช่วงตามเส้นค่าเฉลี่ย: ช่วงละ sets × (1 − φ) × ระยะที่เหลือ
    = เงินช่วงก่อน × φ (ลำดับเรขาคณิต) · คืนค่าไม่ปัด (ใช้รวม) และค่าปัดสองตำแหน่ง (ใช้พิมพ์)"""
    raw, d = [], dist
    for _ in range(n):
        drop = d * (1 - phi)
        raw.append(sets * drop)
        d -= drop
    return raw, [q(v, 2) for v in raw]


def _v2_page(data, D, q, out, sets, start, cost, X):
    """ตัวกลางของหน้า v2 (เขียนใหม่ 2026-11) — ทุกตัวเลขที่หน้าพิมพ์เพื่อ "แสดงการคิด" (คู่มือ v2 ข้อ 3)
    ไม่แตะคีย์เดิม · เพิ่มคีย์ใหม่ใต้ ch13.v2.* เท่านั้น"""
    c09 = data["ch09"]
    entry = D(str(data["ch12"]["จุดเข้า"]))                       # 2.1
    now = D(str(data["ch12"]["เส้นทาง"]["3"]["X"][2]))             # 2.8

    # ── ตามเงินทีละช่วง (ตารางคูณถือ 4 ช่วง): เงินช่วงนี้ = เงินช่วงก่อน × φ ──
    money = {}
    for k in ("0.80", "0.99", "0.90"):
        raw, shown = _money_steps(D, q, sets, start, D(k), 4)
        money[k] = {"ต่อช่วง": shown, "รวม": q(sum(D(str(v)) for v in shown), 2),
                    "รวมไม่ปัด": q(sum(raw), 2), "สุทธิ": q(sum(raw) - cost, 2),
                    "ช่วงแรกระยะลด": q(start * (1 - D(k)), 2)}
        assert money[k]["รวม"] == money[k]["รวมไม่ปัด"], "ผลรวมค่าปัดต้องตรงค่าไม่ปัด (ผู้อ่านบวกเองได้)"
    for k in ("0.80", "0.99"):
        assert money[k]["สุทธิ"] == out["ตารางคูณ"][k]["สุทธิ4ช่วง"]
    for k in ("0.80", "0.99", "1.00", "1.02"):
        out["ตารางคูณ"][k]["กำไรก่อนต้นทุนปัด"] = q(sets * D(str(out["ตารางคูณ"][k]["ลด"])), 2)
        out["ตารางคูณ"][k]["คิดจากปลายทางปัด"] = q(sets * (start - D(str(out["ตารางคูณ"][k]["ปลายทางปัด"]))), 2)
        out["ตารางคูณ"][k]["ลดปัด"] = q(D(str(out["ตารางคูณ"][k]["ลด"])), 2)
    lv80 = data["ch13"]["ตารางphi"]["0.80"]["ระดับ"]
    out["ตารางคูณ"]["0.80"]["ลดช่วง2"] = q(D(str(lv80[1])) - D(str(lv80[2])), 2)     # 1.6 − 1.28
    out["เงินทีละช่วง"] = money

    # ── Mean ไม่ใช่ศูนย์: คู่ E–F ของบท 9 วันที่ 11 (X 11 · Mean 6) · φ 0.80 ──
    ef = c09["v2"]["คู่สอนEF"]
    xm, mu, phi8 = D(str(ef["Xใหม่"])), D(str(ef["Mean"])), D("0.8")
    out["Meanไม่ศูนย์"] = {"X": q(xm, 0), "Mean": q(mu, 0), "ห่าง": q(xm - mu, 0), "phi": 0.8,
                          "ห่างหลังคูณ": q((xm - mu) * phi8, 1), "Xหลัง": q((xm - mu) * phi8 + mu, 1),
                          "คูณตรงผิด": q(xm * phi8, 1), "ลดจริง": q(xm - ((xm - mu) * phi8 + mu), 1),
                          "ลดถ้าผิด": q(xm - xm * phi8, 1)}

    # ── แรงสะบัดหนึ่งครั้ง (คู่ A–B · Mean 0 · φ 0.80 · แรงสะบัดขนาด 0.5 ของโลกจำลอง) ──
    shock = D("0.5")
    mean1 = start * phi8
    out["สะบัดหนึ่งครั้ง"] = {"X": q(start, 0), "phi": 0.8, "เส้นค่าเฉลี่ย": q(mean1, 1), "สะบัด": 0.5,
                             "Xจริง": q(mean1 + shock, 1), "สะบัดลบ": -0.5, "Xจริงลบ": q(mean1 - shock, 1),
                             "เงินshort10ถ้าสะบัดบวก": q(sets * (start - mean1 - shock), 0),
                             "เงินshort10ถ้าสะบัดลบ": q(sets * (start - mean1 + shock), 0),
                             "เงินshort10ตามเส้น": q(sets * (start - mean1), 0)}

    # ── SD ของ X ในแต่ละโลก ผ่าน "SD ยกกำลังสอง" ที่ใช้ φ² ปัดสองตำแหน่ง (หน้าไม่พิมพ์ทศนิยมเกินสอง) ──
    sdpage = []
    for r in out["sdโลก"]:
        p2 = q(D(str(r["phi"])) ** 2, 2)
        one = D(1) - D(str(p2))
        n2 = D(str(r["แรงสะบัด"])) ** 2
        v = n2 / one
        sdp = q(v.sqrt(), 2)
        assert sdp == r["sd"], "SD จาก φ² ปัดต้องตรง SD จริงที่สองตำแหน่ง"
        chk = D(str(p2)) * D(str(q(v, 2))) + n2
        sdpage.append({"phi": r["phi"], "แรงสะบัด": r["แรงสะบัด"], "phiกำลังสองปัด": p2, "หนึ่งลบ": q(one, 2),
                       "แรงสะบัดกำลังสอง": q(n2, 2), "sdกำลังสอง": q(v, 2) if v > D("0.05") else q(v, 2),
                       "sd": sdp, "zของ2": r["zจากsdปัด"], "ตรวจสมดุล": q(chk, 2),
                       "หดเหลือ": q(D(str(p2)) * D(str(q(v, 2))), 2)})
    out["sdหน้า"] = sdpage

    # ── ส่วนผสมตอนจบของกฎเดียวสามโลก: แต่ละเหตุออกได้เฉลี่ยเท่าไร (สะพานไปส่วนผสมซ้อม 60/25/15 ของบท 12) ──
    mix = {}
    for k, r in _three_worlds_by_reason(float(cost)).items():
        rows, parts = {}, []
        for reason in ("เป้า", "งบ", "เวลา"):
            pct = q(D(str(r[reason][0])) * 100, 1)
            avg = q(D(str(r[reason][1])), 2)
            part = q(D(str(pct)) / 100 * D(str(avg)), 2)
            rows[reason] = {"เปอร์เซ็นต์": pct, "เฉลี่ยต่อไม้": avg, "ส่วนต่อไม้": part}
            parts.append(D(str(part)))
        assert rows["เป้า"]["เปอร์เซ็นต์"] == out["กฎเดียวสามโลก"][k]["ออกเพราะเป้าเปอร์เซ็นต์"]
        rows["รวมจากค่าปัด"] = q(sum(parts), 2)
        rows["ค่าคาดหมาย"] = out["กฎเดียวสามโลก"][k]["ค่าคาดหมายต่อไม้ก่อนค่าถือ"]
        mix[k] = rows
    c12 = data["ch12"]["v2"]["ค่าคาดหมาย100ไม้"]["หลัก"]
    mix["บท12"] = {"สัดส่วน": c12["สัดส่วน"], "ผล": [data["ch12"]["v2"]["เส้นทาง"][i]["สุทธิ"] for i in ("1", "2", "3")],
                  "ต่อไม้": c12["ต่อไม้"]}
    mix["เส้นค่าเฉลี่ย3ช่วง_0.80"] = q(start * D("0.8") ** 3, 2)     # 1.02: เส้นค่าเฉลี่ยไปไม่ถึง 0.5 ใน 3 ช่วง
    mix["ครบเวลาบท12_X"] = data["ch12"]["v2"]["เส้นทาง"]["2"]["Xออก"]   # 1.8
    out["ส่วนผสมตอนจบ"] = mix

    # ── φ มือ: ทำไมไม่หารทีละวัน · น้ำหนักของวันที่ห่างมาก ──
    out["phiมือบท9"]["หารวัน11ไป12"] = q(X[11] / X[10], 2)        # 1.2 ÷ 2.2
    out["phiมือบท9"]["หารวัน5ไป6"] = q(X[5] / X[4], 1)            # −0.9 ÷ −0.2 = 4.5
    out["phiมือบท9"]["นับมือวัน11ครึ่ง"] = q(X[10] / 2, 1)         # ครึ่งของ 2.2 = 1.1 → แตะวันที่ 13 (0.5)

    # ── เทียบกับการเดาแบบไม่ทำอะไร: "พรุ่งนี้เท่าวันนี้" vs "พรุ่งนี้ 80% ของวันนี้" ──
    def errs(lo, hi):
        rows = []
        for i in range(lo, hi):
            a, b = X[i], X[i + 1]
            g = a * phi8
            rows.append({"วัน": i + 1, "วันนี้": q(a, 1), "พรุ่งนี้": q(b, 1), "พลาดถ้าเท่าเดิม": q(abs(b - a), 1),
                         "เดา80": q(g, 2), "พลาดถ้า80": q(abs(b - g), 2)})
        return rows
    five = errs(10, 15)                                             # วันที่ 11 (X ไกลสุด 2.2) ถึงวันที่ 16
    allr = errs(0, len(X) - 1)
    out["เทียบไม่ทำอะไร"] = {
        "ห้าแถว": five,
        "รวมเท่าเดิม": q(sum(D(str(r["พลาดถ้าเท่าเดิม"])) for r in five), 1),
        "รวม80": q(sum(D(str(r["พลาดถ้า80"])) for r in five), 2),
        "ทั้งหมดแถว": len(allr),
        "ทั้งหมดรวมเท่าเดิม": q(sum(D(str(r["พลาดถ้าเท่าเดิม"])) for r in allr), 1),
        "ทั้งหมดรวม80": q(sum(D(str(r["พลาดถ้า80"])) for r in allr), 2),
        "ทั้งหมด80ชนะแถว": sum(1 for r in allr if r["พลาดถ้า80"] < r["พลาดถ้าเท่าเดิม"]),
    }
    t = out["เทียบไม่ทำอะไร"]
    t["ห้าแถวต่าง"] = q(D(str(t["รวมเท่าเดิม"])) - D(str(t["รวม80"])), 2)
    t["ทั้งหมดต่าง"] = q(D(str(t["ทั้งหมดรวมเท่าเดิม"])) - D(str(t["ทั้งหมดรวม80"])), 2)
    t["ทั้งหมดต่างเปอร์เซ็นต์"] = q(D(str(t["ทั้งหมดต่าง"])) / D(str(t["ทั้งหมดรวมเท่าเดิม"])) * 100, 0)

    # ── ไม้ 3 ที่ 2.8: ตามเงินอีก 2 ช่วง (ช่วงละ 10 × ระยะที่เชือกดึง) แล้วตรวจด้วยปลายทาง ──
    price_now = sets * (entry - now)                                 # −7
    for k in ("0.80", "0.99", "1.00"):
        raw, shown = _money_steps(D, q, sets, now, D(k), 2)
        tot = q(sum(raw), 2)
        tr = out["ไม้3"][k]
        tr["เงินต่อช่วง"] = shown
        tr["เงินรวมสองช่วง"] = tot
        tr["กำไรจากราคา"] = q(price_now + sum(raw), 2)
        tr["คิดจากXปัด"] = q(sets * (entry - D(str(tr["Xคาดตอนครบเวลา"]))) - cost, 2)
        assert q(price_now + D(str(tot)) - cost, 2) == tr["สุทธิถ้าครบเวลา"]
    out["ไม้3"]["กำไรจากราคาตอนนี้"] = q(price_now, 0)
    out["ไม้3"]["งบที่ใช้ไป"] = q(-out["ไม้3"]["ตอนนี้"], 0)        # 9 จากงบ 15

    # ── แบบฝึก v2 ──
    ex2 = {}                                                        # (เปลี่ยนเลข) ไม้ 3 ถ้าโลกเป็น φ 0.90
    raw, shown = _money_steps(D, q, sets, now, D("0.9"), 2)
    ex2 = {"X": [q(now, 1), q(now * D("0.9"), 2), q(now * D("0.81"), 2)], "เงินต่อช่วง": shown,
           "เงินรวม": q(sum(raw), 2), "กำไรจากราคา": q(price_now + sum(raw), 2),
           "สุทธิ": q(price_now + sum(raw) - cost, 2)}
    mu1 = D(1)                                                      # (เปลี่ยนเงื่อนไข) Mean ของคู่เป็น 1 ไม่ใช่ 0
    raw3, shown3 = _money_steps(D, q, sets, now - mu1, phi8, 2)
    ex3 = {"Mean": 1, "ห่าง": q(now - mu1, 1), "ห่างช่วง1": q((now - mu1) * phi8, 2),
           "ห่างช่วง2": q((now - mu1) * phi8 * phi8, 2), "X": q((now - mu1) * phi8 * phi8 + mu1, 2),
           "เงินต่อช่วง": shown3, "เงินรวม": q(sum(raw3), 2), "กำไรจากราคา": q(price_now + sum(raw3), 2),
           "สุทธิ": q(price_now + sum(raw3) - cost, 2)}
    out["แบบฝึกv2"] = {"ข้อ1": {"เงินต่อช่วง": money["0.90"]["ต่อช่วง"], "รวม": money["0.90"]["รวม"],
                                "สุทธิ": money["0.90"]["สุทธิ"], "ครึ่งชีวิต": 6.6},
                       "ข้อ2": ex2, "ข้อ3": ex3}


def _three_worlds_by_reason(cost, start=2.0, sd=0.5, trials=100_000, phis=(0.80, 0.99, 1.00), budget=-15.0,
                            exit_line=0.5, max_hold=3, sets=10):
    """ลำดับสุ่มเดียวกับ _three_worlds_v2 ทุกตัว · คืน {φ: {เหตุออก: (สัดส่วน, ผลเฉลี่ยต่อไม้ของเหตุนั้น)}}"""
    rng = random.Random(SEED)
    out = {}
    for phi in phis:
        acc = {"งบ": [0, 0.0], "เป้า": [0, 0.0], "เวลา": [0, 0.0]}
        for _ in range(trials):
            x = start
            for t in range(1, max_hold + 1):
                x = phi * x + rng.gauss(0.0, sd)
                liq = sets * (start - x) - cost
                if liq <= budget:
                    r = "งบ"
                elif x <= exit_line:
                    r = "เป้า"
                elif t >= max_hold:
                    r = "เวลา"
                else:
                    continue
                acc[r][0] += 1
                acc[r][1] += liq
                break
        out[f"{phi:.2f}"] = {k: (n / trials, s / n if n else 0.0) for k, (n, s) in acc.items()}
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

    v2 = _ints(_v2(data, D, q, count))
    return {
        "v2": v2,
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
            {"โจทย์": "(ทำตาม) φ 0.90 ต่อช่วง เริ่ม 2 short 10 ชุด ถือ 4 ช่วง ต้นทุน 2 — เงินทีละช่วงและสุทธิตามเส้นค่าเฉลี่ย",
             "คำตอบ": v2["แบบฝึกv2"]["ข้อ1"]["สุทธิ"]},
            {"โจทย์": "(เปลี่ยนเลข) ไม้ 3 ที่ 2.8 ถ้าโลกเป็น φ 0.90 ครบเวลาอีก 2 ช่วงได้สุทธิเท่าไร",
             "คำตอบ": v2["แบบฝึกv2"]["ข้อ2"]["สุทธิ"]},
            {"โจทย์": "(เปลี่ยนเงื่อนไข) ไม้ 3 ที่ 2.8 โลก φ 0.80 แต่ Mean ของคู่เป็น 1 — สุทธิเมื่อครบเวลา",
             "คำตอบ": v2["แบบฝึกv2"]["ข้อ3"]["สุทธิ"]},
            {"โจทย์": "(ตัดสินใจ) φ มือ 0.74 จาก 20 วัน Half-life 2.3 สั้นกว่า 3 ช่วง เพื่อนให้เพิ่มเป็น 20 ชุด — เห็นด้วยไหม",
             "คำตอบ": short["มัธยฐานที่ประมาณได้"]},
            {"โจทย์": "(ถ่ายโอน) basis spot–perp ที่ห่างจากปกติเหลือ 98% ต่อวัน — ครึ่งชีวิตกี่วัน และทำไมใช้ φ กับ dated futures ไม่ได้",
             "คำตอบ": next(r["ครึ่งชีวิต"] for r in c13["phiเป็นครึ่งชีวิต"] if r["phi"] == 0.98)},
        ],
    }
