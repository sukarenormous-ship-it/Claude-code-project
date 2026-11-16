"""บท 12 เล่ม 2 — จัดเงินหลายกลยุทธ์ · ค่าทุกตัวของบท (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ตอน ก  สามงาน เงินก้อนเดียว สองเพดาน (ต่อจากเรื่อง 5 ภาคผนวก J เล่ม 1 + งานที่สาม funding carry) → ผลต่อความเสี่ยง
       จากหกเดือนสอน (Mean · SD ตัวหาร n − 1 · Mean ÷ SD)
ตอน ข  สองงานที่แกว่งสวนกัน: ความแปรปรวนของพอร์ตด้วยมือ (ตรง ๆ เทียบสูตร a²σ² + b²σ² + 2ab·cov) → ตารางน้ำหนัก (Mean–Variance)
ตอน ค  📡 funding carry BTC (Deribit · รายเดือน 30 วัน) กับคู่ LTC–DOT (การ์ดของบท 7 · h 3.76 · ไม้บรรทัดช่วงเลือก · 10 ชุด)
       ช่วงเลือก → น้ำหนัก → ช่วงตรวจ · 🎲 โลกที่รู้น้ำหนักที่ถูก (30 โลก × 24 เดือน) · Mean เต็ม / หดครึ่ง / ไม่ใช้ Mean
ตอน ง  Kelly บนเกมฉลากของเล่ม 1 บท 2 (+4 / −2 / −5 · โอกาส 0.5 / 0.3 / 0.2) · ด้วยมือสิบตา · sab2_stats.kelly_discrete
       🎲 30 โลก × 100 ตา: เต็ม · ครึ่ง · สองเท่า Kelly และเมื่อโอกาสจริงแย่กว่าที่คิด · Kelly ของ funding carry จริง · Risk Budget

ข้อมูลจริงผ่าน sab2_realdata.load_closes/load_funding เท่านั้น (ช่วงเลือกและช่วงตรวจ) · สถิติผ่าน sab2_stats ·
backtest ผ่าน sab2_engine.run · ตัวเลขเล่ม 1 ผ่าน sab_book.load_figures("sab") · โลกจำลองใช้ random.Random(seed) seed 1–30
(ชุดเดียวกับ sab2_sim.ROBUST_SEEDS)
"""

import math
import random
import statistics
from collections import defaultdict

import sab_book as SB
import sab2_engine as E
import sab2_sim as M
import sab2_stats as S
from sab2_realdata import load_closes, load_funding

SEEDS = M.ROBUST_SEEDS
MONTH = 30                       # หนึ่ง "เดือน" ของบท = 30 วัน (แบบเดือนของต้นในบท 13)
PAIR_H, PAIR_SETS = 3.76, 10     # การ์ด LTC บน DOT ของบท 7 (h ปัด · 10 ชุด · เส้น 2 / 0.5 / 30 วัน)
CAPITAL = 1000.0

# ── ตอน ก · สามงาน (หน่วยละ 630 รวมเงินกันขา short ตามเรื่อง 5 · funding carry = spot แห่งที่ 2 + perp short แห่งที่ 1) ──
JOBS = [("คู่", 630, 630, 6), ("carry", 630, 130, 5), ("funding", 630, 130, 3)]   # ชื่อ · เงินรวมต่อหน่วย · แห่งที่ 1 · คาดได้

# ── ตอน ก–ข · หกเดือนสอน (ผลต่อหน่วยต่อเดือน · ตัวเลขตั้งโจทย์ ไม่ใช่ผลวัด) ──
SIX = {"carry": [7, 3, 6, 4, 5, 5], "funding": [6, 0, 4, 1, 5, 2], "คู่": [10, 12, -4, 8, -2, 12]}

# ── ตอน ง · ฉลาก ──
LOT_P, LOT_PAY = [0.5, 0.3, 0.2], [4, -2, -5]
LOT_TRUE_P = [0.45, 0.35, 0.2]   # โลกที่โอกาสจริงแย่กว่าที่คิด (ได้ 4 น้อยลง 5 จุด ไปอยู่ที่เสีย 2)
LOT_WEALTH, LOT_DRAWS = 100, 100

# ── ตอน ค · โลกจำลองที่รู้คำตอบ (ผลรายเดือนเป็นเปอร์เซ็นต์ · ใกล้ค่าที่ประมาณได้จากช่วงเลือก) ──
SIM_MU = (0.6, 1.0)              # funding carry · คู่
SIM_SD = (0.7, 6.0)
SIM_RHO = -0.15
SIM_MONTHS = 24


def _r(x, n=2):
    return round(float(x) + 0.0, n)


def _monthly_funding(split, inst):
    by = defaultdict(float)
    for ts, _, rate in load_funding(split, instrument=inst):
        by[ts[:10]] += rate
    daily = [by[d] for d in sorted(by)]
    return [100 * sum(daily[i:i + MONTH]) for i in range(0, len(daily) - MONTH + 1, MONTH)], daily, sorted(by)


def _pair(split):
    _, F = load_closes("formation", coins=["LTC", "DOT"])
    X = [a - PAIR_H * b for a, b in zip(F["LTC"], F["DOT"])]
    m, s = S.mean(X), S.sd(X)
    dates, V = load_closes(split, coins=["LTC", "DOT"])
    a, b = V["LTC"], V["DOT"]
    z = [(x - PAIR_H * y - m) / s for x, y in zip(a, b)]
    r = E.run(a, b, PAIR_H, z, sets=PAIR_SETS, capital=CAPITAL)
    eq = r["equity"]
    months = [100 * (eq[i + MONTH - 1] - (eq[i - 1] if i else CAPITAL)) / CAPITAL
              for i in range(0, len(eq) - MONTH + 1, MONTH)]
    return months, r, dates, m, s


def _grid(F, P, step=10):
    rows = []
    for k in range(step + 1):
        w = k / step
        p = [(1 - w) * f + w * x for f, x in zip(F, P)]
        mu, sd = S.mean(p), S.sd(p)
        rows.append({"w": w, "mean": mu, "sd": sd, "ratio": mu / sd})
    return rows


def _best_w(mu, sd, rho, step=100):
    """น้ำหนักของงานที่สอง (0..1 ทีละ 1/step) ที่ทำให้ Mean ÷ SD สูงสุด · สองงาน · ห้ามติดลบ"""
    best = None
    for k in range(step + 1):
        w = k / step
        m = (1 - w) * mu[0] + w * mu[1]
        v = (1 - w) ** 2 * sd[0] ** 2 + w ** 2 * sd[1] ** 2 + 2 * w * (1 - w) * rho * sd[0] * sd[1]
        r = m / math.sqrt(v)
        if best is None or r > best[1] + 1e-15:
            best = (w, r)
    return best[0]


def _lottery_hand(q):
    rows = []
    for f, tickets in ((0.05, 1), (0.1, 2), (0.2, 4), (0.3, 6), (0.5, 10), (1.0, 20)):
        pays = [tickets * x for x in LOT_PAY]
        fac = [1 + x / LOT_WEALTH for x in pays]
        mult = fac[0] ** 5 * fac[1] ** 3 * fac[2] ** 2
        rows.append({"f": f, "fเปอร์เซ็นต์": q(100 * f, 0), "ใบ": tickets, "ได้": pays[0], "เสียเล็ก": pays[1], "เสียใหญ่": pays[2],
                     "คูณ": [q(x, 2) for x in fac], "ห้ายก": q(fac[0] ** 5, 4), "สามยก": q(fac[1] ** 3, 4),
                     "สองยก": q(fac[2] ** 2, 4), "สิบตา": q(mult, 4), "สิบตาเงิน": q(LOT_WEALTH * mult, 2),
                     "ห้าเงิน": q(LOT_WEALTH * fac[0] ** 5, 2), "แปดเงิน": q(LOT_WEALTH * fac[0] ** 5 * fac[1] ** 3, 2)})
    return rows


def _lottery_sim(f, probs, q):
    finals, below, dds = [], 0, []
    cum = [sum(probs[:i + 1]) for i in range(len(probs))]
    for sd in SEEDS:
        rng = random.Random(sd)
        w, peak, dd = 1.0, 1.0, 0.0
        for _ in range(LOT_DRAWS):
            u = rng.random()
            i = next(k for k, c in enumerate(cum) if u < c)
            w *= 1 + f * LOT_PAY[i] / 5
            peak = max(peak, w)
            dd = max(dd, 1 - w / peak)
        finals.append(LOT_WEALTH * w)
        dds.append(100 * dd)
        below += w < 1
    return {"มัธยฐาน": q(statistics.median(finals), 1), "ต่ำสุด": q(min(finals), 1), "สูงสุด": q(max(finals), 1),
            "ต่ำกว่าทุน": below, "ลดลงสูงสุดมัธยฐาน": q(statistics.median(dds), 0)}


def _weights_sim(q):
    true_w = _best_w(SIM_MU, SIM_SD, SIM_RHO)
    est = {"เต็ม": [], "หดครึ่ง": [], "ไม่ใช้Mean": []}
    one_side, zero, mP_est, sP_est = 0, 0, [], []
    for sd in SEEDS:
        rng = random.Random(1000 + sd)
        F, P = [], []
        for _ in range(SIM_MONTHS):
            z1, z2 = rng.gauss(0, 1), rng.gauss(0, 1)
            F.append(SIM_MU[0] + SIM_SD[0] * z1)
            P.append(SIM_MU[1] + SIM_SD[1] * (SIM_RHO * z1 + math.sqrt(1 - SIM_RHO ** 2) * z2))
        mu, sdv, rho = (S.mean(F), S.mean(P)), (S.sd(F), S.sd(P)), S.corr(F, P)
        mid = (mu[0] + mu[1]) / 2
        w_full = _best_w(mu, sdv, rho) if min(mu) > 0 else (0.0 if mu[1] <= 0 else 1.0)
        shr = ((mu[0] + mid) / 2, (mu[1] + mid) / 2)
        w_shr = _best_w(shr, sdv, rho) if min(shr) > 0 else (0.0 if shr[1] <= 0 else 1.0)
        w_mv = _best_w((1.0, 1.0), sdv, rho)               # Mean เท่ากัน = เลือกจาก SD และ correlation อย่างเดียว
        est["เต็ม"].append(100 * w_full)
        est["หดครึ่ง"].append(100 * w_shr)
        est["ไม่ใช้Mean"].append(100 * w_mv)
        one_side += w_full <= 0.02 or w_full >= 0.98
        zero += w_full == 0
        mP_est.append(mu[1])
        sP_est.append(sdv[1])
    shr_true = ((SIM_MU[0] + sum(SIM_MU) / 2) / 2, (SIM_MU[1] + sum(SIM_MU) / 2) / 2)
    out = {"จริง": {"Mean": list(SIM_MU), "SD": list(SIM_SD), "rho": SIM_RHO, "เดือน": SIM_MONTHS,
                    "น้ำหนักคู่ที่ถูกเปอร์เซ็นต์": q(100 * true_w, 0),
                    "น้ำหนักคู่หดครึ่งเปอร์เซ็นต์": q(100 * _best_w(shr_true, SIM_SD, SIM_RHO), 0),
                    "น้ำหนักคู่ไม่ใช้Meanเปอร์เซ็นต์": q(100 * _best_w((1.0, 1.0), SIM_SD, SIM_RHO), 0)},
           "สุดขั้ว": one_side, "ไม่ใส่คู่": zero, "โลก": len(SEEDS),
           "Meanคู่ที่ประมาณ": {"ต่ำสุด": q(min(mP_est), 2), "มัธยฐาน": q(statistics.median(mP_est), 2), "สูงสุด": q(max(mP_est), 2),
                              "ติดลบ": sum(1 for x in mP_est if x < 0)},
           "SDคู่ที่ประมาณ": {"ต่ำสุด": q(min(sP_est), 2), "สูงสุด": q(max(sP_est), 2)},
           "SEของMeanคู่": q(SIM_SD[1] / math.sqrt(SIM_MONTHS), 2)}
    for k, v in est.items():
        out[k] = {"ต่ำสุด": q(min(v), 0), "มัธยฐาน": q(statistics.median(v), 0), "สูงสุด": q(max(v), 0),
                  "ห่างจากถูกมัธยฐาน": q(statistics.median([abs(x - 100 * true_w) for x in v]), 0)}
    return out


def extend(data, D, q):
    out = {}

    # ════════════ เล่ม 1 ที่ทวน ════════════
    f1 = SB.load_figures("sab")
    c5 = f1["cases"]["c5"]
    lot = f1["ch02"]["v2"]["ฉลาก"]
    out["เล่ม1"] = {"เงินรวม": c5["เงินรวม"], "เพดาน": c5["เพดานแห่งที่1"], "มูลค่าขา": c5["มูลค่าขา"],
                    "กันต่อขา": c5["ช่องว่าง"]["ต้องมีต่อขา"], "หน่วยแห่งที่1คู่": c5["คู่ต่อหน่วยแห่งที่1กัน"],
                    "หน่วยแห่งที่1carry": c5["carryต่อหน่วยแห่งที่1กัน"], "หน่วยรวม": c5["carryต่อหน่วยรวมกัน"],
                    "คาดคู่": c5["คาดคู่"], "คาดcarry": c5["คาดcarry"], "ดีสุดคาด": c5["ดีสุดกัน"]["คาดได้"],
                    "ดีสุดเงินว่าง": c5["ดีสุดกันเงินว่าง"],
                    "ฉลาก": {"ค่า": lot["ค่า"], "จำนวน": lot["จำนวน"], "โอกาส": lot["โอกาส"], "ค่าคาดหมาย": lot["ค่าคาดหมาย"],
                             "ค่าเล่นต่อตา": lot["ค่าเล่นต่อตา"], "หักค่าเล่น": lot["หักค่าเล่น"]},
                    "carryรอบชดเชย": f1["ch17"]["รอบชดเชย"][0]}
    assert [JOBS[0][3], JOBS[1][3]] == [c5["คาดคู่"], c5["คาดcarry"]] and JOBS[0][2] == c5["คู่ต่อหน่วยแห่งที่1กัน"]
    assert LOT_PAY == lot["ค่า"] and LOT_P == lot["โอกาส"]

    # ════════════ ตอน ก · 1  ไล่ทุกทาง ════════════
    rows = []
    for p in range(3):
        for c in range(3):
            for f in range(3):
                n = p + c + f
                if n == 0 or n > 2:
                    continue
                total = 630 * n
                ex1 = 630 * p + 130 * (c + f)
                ok_t, ok_1 = total <= c5["เงินรวม"], ex1 <= c5["เพดานแห่งที่1"]
                why = "ผ่าน" if ok_t and ok_1 else ("แห่งที่ 1 เกิน" if ok_t else "เงินรวมเกิน")
                rows.append({"คู่": p, "carry": c, "funding": f, "เงินรวม": total, "แห่งที่1": ex1, "ผ่าน": ok_t and ok_1,
                             "เหตุ": why, "คาดได้": 6 * p + 5 * c + 3 * f, "เงินว่าง": c5["เงินรวม"] - total})
    rows.sort(key=lambda r: (not r["ผ่าน"], -r["คาดได้"]))
    best = rows[0]
    out["สามงาน"] = {"แถว": rows, "ดีสุด": best, "คาดfunding": 3, "ผ่าน": sum(r["ผ่าน"] for r in rows),
                     "สามหน่วย": 630 * 3, "ไม่ผ่าน": sum(not r["ผ่าน"] for r in rows)}

    # ════════════ ตอน ก · 2  หกเดือน: Mean · SD · ผลต่อความเสี่ยง ════════════
    six = {}
    for k, xs in SIX.items():
        m = S.mean(xs)
        dev = [x - m for x in xs]
        ss = sum(d * d for d in dev)
        sq = sum(x * x for x in xs)
        var = ss / (len(xs) - 1)
        six[k] = {"ผล": xs, "รวม": sum(xs), "Mean": q(m, 2), "ห่าง": [q(d, 0) for d in dev], "ห่างกำลังสอง": [q(d * d, 0) for d in dev],
                  "รวมห่างกำลังสอง": q(ss, 0), "Var": q(var, 2), "SD": q(math.sqrt(var), 2), "ratio": q(m / math.sqrt(var), 2),
                  "รวมกำลังสอง": q(sq, 0), "nMeanกำลังสอง": q(len(xs) * m * m, 0), "ตรวจVar": q((sq - len(xs) * m * m) / 5, 2),
                  "ratioจากเลขปัด": q(D(str(q(m, 2))) / D(str(q(math.sqrt(var), 2))), 2)}
        assert abs(S.var(xs) - var) < 1e-12
    out["หกเดือน"] = six
    out["SEMeanคู่หกเดือน"] = q(math.sqrt(S.var(SIX["คู่"]) / 6), 2)
    out["รากหก"] = q(math.sqrt(6), 2)
    # หางของ carry: เดือนที่ exchange แห่งที่ 2 ถอนไม่ได้ เสียขา spot 500 ทั้งก้อน (ภาพของเล่ม 1 บท 17)
    tail = SIX["carry"][:5] + [-500]
    mt, st = S.mean(tail), S.sd(tail)
    out["หางcarry"] = {"ผล": tail, "Mean": q(mt, 2), "SD": q(st, 2), "ratio": q(mt / st, 2), "เสีย": -500,
                       "เดือนดีต้องชดเชย": q(500 / 5, 0)}

    # ════════════ ตอน ข · 1  ความแปรปรวนของพอร์ต ด้วยมือ ════════════
    F, P = SIX["funding"], SIX["คู่"]
    mF, mP = S.mean(F), S.mean(P)
    dF, dP = [x - mF for x in F], [x - mP for x in P]
    both = [a + b for a, b in zip(F, P)]
    mB = S.mean(both)
    dB = [x - mB for x in both]
    cross = [a * b for a, b in zip(dF, dP)]
    cov = sum(cross) / 5
    vF, vP = S.var(F), S.var(P)
    vB = sum(d * d for d in dB) / 5
    assert abs(vB - (vF + vP + 2 * cov)) < 1e-9 and abs(cov - S.cov(F, P)) < 1e-12
    rho = cov / math.sqrt(vF * vP)
    rhos = []
    for rr in (-0.5, 0, 0.5, 1):
        c_ = rr * math.sqrt(vF * vP)
        v_ = vF + vP + 2 * c_
        rhos.append({"rho": rr, "cov": q(c_, 1), "สองเท่าcov": q(2 * c_, 1), "Var": q(v_, 1), "SD": q(math.sqrt(v_), 2),
                     "ratio": q((mF + mP) / math.sqrt(v_), 2)})
    cC = S.cov(SIX["carry"], F)
    out["พอร์ต"] = {"รวม": both, "Meanรวม": q(mB, 0), "ห่างรวม": [q(x, 0) for x in dB], "ห่างรวมกำลังสอง": [q(x * x, 0) for x in dB],
                    "รวมห่างรวมกำลังสอง": q(sum(x * x for x in dB), 0), "Varรวม": q(vB, 2), "SDรวม": q(math.sqrt(vB), 2),
                    "ratioรวม": q(mB / math.sqrt(vB), 2), "ห่างF": [q(x, 0) for x in dF], "ห่างP": [q(x, 0) for x in dP],
                    "คูณห่าง": [q(x, 0) for x in cross], "รวมคูณห่าง": q(sum(cross), 0), "cov": q(cov, 2), "สองเท่าcov": q(2 * cov, 2),
                    "rho": q(rho, 2), "บวกSD": q(math.sqrt(vF) + math.sqrt(vP), 2), "บวกVar": q(vF + vP, 2),
                    "rhoแถว": rhos, "covcarryfunding": q(cC, 2),
                    "rhocarryfunding": q(cC / math.sqrt(S.var(SIX["carry"]) * vF), 2),
                    "คูณห่างcarryfunding": [q((a - 5) * (b - mF), 0) for a, b in zip(SIX["carry"], F)],
                    "รวมคูณห่างcarryfunding": q(sum((a - 5) * (b - mF) for a, b in zip(SIX["carry"], F)), 0)}

    # ════════════ ตอน ข · 2  ตารางน้ำหนัก (สองหน่วยรวม) ════════════
    mix = []
    for a, b in ((2, 0), (1.5, 0.5), (1, 1), (0.5, 1.5), (0, 2)):
        m_ = a * mF + b * mP
        p1, p2, p3 = a * a * vF, b * b * vP, 2 * a * b * cov
        v_ = p1 + p2 + p3
        mix.append({"F": a, "P": b, "Mean": q(m_, 2), "aกำลังสองVar": q(p1, 2), "bกำลังสองVar": q(p2, 2), "สองabcov": q(p3, 2),
                    "Var": q(v_, 2), "SD": q(math.sqrt(v_), 2), "ratio": q(m_ / math.sqrt(v_), 2)})
    bestmix = max(mix, key=lambda r: r["ratio"])
    curve = []
    for k in range(21):
        s_ = k / 20
        row = {"ส่วนคู่": s_}
        for rr in (-0.5, 0, 0.5):
            c_ = rr * math.sqrt(vF * vP)
            v_ = (1 - s_) ** 2 * vF + s_ ** 2 * vP + 2 * s_ * (1 - s_) * c_
            row[str(rr)] = q(((1 - s_) * mF + s_ * mP) / math.sqrt(v_), 3)
        curve.append(row)
    out["ผสม"] = {"แถว": mix, "ดีสุด": bestmix, "เส้น": curve, "สองเท่าดีสุด": {"F": 3, "P": 1, "Mean": q(2 * bestmix["Mean"], 2),
                  "SD": q(2 * bestmix["SD"], 2), "ratio": bestmix["ratio"]},
                  "ส่วนคู่ต่ำสุดVar": q(100 * (vF - cov) / (vF + vP - 2 * cov), 0), "แกน": [0, 25, 50, 75, 100], "แกนy": [0.5, 1, 1.5, 2, 2.5]}

    # ════════════ ตอน ค · 1  📡 ข้อมูลจริง ════════════
    real = {}
    for sp in ("formation", "validation"):
        Fm, daily, days = _monthly_funding(sp, "BTC-PERPETUAL")
        Em, _, _ = _monthly_funding(sp, "ETH-PERPETUAL")
        Pm, r, dates, m_, s_ = _pair(sp)
        assert len(Fm) == len(Pm)
        g = _grid(Fm, Pm)
        bw = max(g, key=lambda x: x["ratio"])
        real[sp] = {"เดือน": len(Fm), "วันใช้": len(Fm) * MONTH, "วัน": len(days),
                    "F": {"Mean": q(S.mean(Fm), 2), "SD": q(S.sd(Fm), 2), "ratio": q(S.mean(Fm) / S.sd(Fm), 2),
                          "ต่อปี": q(100 * sum(daily) / len(daily) * 365, 2), "เดือนติดลบ": sum(1 for x in Fm if x < 0),
                          "ต่ำสุด": q(min(Fm), 2), "สูงสุด": q(max(Fm), 2)},
                    "E": {"Mean": q(S.mean(Em), 2), "SD": q(S.sd(Em), 2), "rhoกับBTC": q(S.corr(Fm, Em), 2)},
                    "P": {"Mean": q(S.mean(Pm), 2), "SD": q(S.sd(Pm), 2), "ratio": q(S.mean(Pm) / S.sd(Pm), 2),
                          "ไม้": r["trades"], "ชนะ": r["wins"], "net": q(r["net"], 2), "ค้าง": int(bool(r["open"])),
                          "เดือนที่มีผล": sum(1 for x in Pm if abs(x) > 1e-9), "ต่ำสุด": q(min(Pm), 2), "สูงสุด": q(max(Pm), 2)},
                    "rho": q(S.corr(Fm, Pm), 2),
                    "ตารางน้ำหนัก": [{"w": q(100 * x["w"], 0), "Mean": q(x["mean"], 2), "SD": q(x["sd"], 2), "ratio": q(x["ratio"], 2)} for x in g],
                    "ดีสุดw": q(100 * bw["w"], 0), "ดีสุดratio": q(bw["ratio"], 2),
                    "_F": Fm, "_P": Pm, "_E": Em}
        if sp == "formation":
            real[sp]["ไม้บรรทัด"] = {"Mean": q(m_, 2), "SD": q(s_, 2)}
            real[sp]["ตัวอย่าง"] = [{"เดือน": i + 1, "เริ่ม": days[i * MONTH], "F": q(Fm[i], 2), "P": q(Pm[i], 2)} for i in range(8)]
    fo, va = real["formation"], real["validation"]
    # น้ำหนักที่เลือกจากช่วงเลือก (ทีละ 10%) ไปเจออะไรในช่วงตรวจ · ทุกแถวดูพร้อมกันครั้งเดียว
    pick = fo["ดีสุดw"]
    vrow = next(x for x in va["ตารางน้ำหนัก"] if x["w"] == pick)
    # ความไว: ถ้าใส่ค่า Mean / SD ของคู่ผิดไป (ช่วงเลือกเป็นฐาน · corr เดิม)
    mF_, sF_ = S.mean(fo["_F"]), S.sd(fo["_F"])
    mP_, sP_ = S.mean(fo["_P"]), S.sd(fo["_P"])
    rh_ = S.corr(fo["_F"], fo["_P"])
    sens = []
    for lab, mu2, sd2 in (("ตามช่วงเลือก", mP_, sP_), ("Mean คู่ครึ่งเดียว", mP_ / 2, sP_), ("Mean คู่สองเท่า", 2 * mP_, sP_),
                          ("SD คู่เท่าช่วงตรวจ", mP_, S.sd(va["_P"])), ("ทั้งสองค่าเท่าช่วงตรวจ", S.mean(va["_P"]), S.sd(va["_P"]))):
        sens.append({"แบบ": lab, "MeanP": q(mu2, 2), "SDP": q(sd2, 2), "w": q(100 * _best_w((mF_, mu2), (sF_, sd2), rh_), 0)})
    # carry (futures มีวันหมดอายุ): ไม่มีในชุดข้อมูล · ใช้ basis ที่ล็อกของเล่ม 1 (5 ต่อขา 500 ต่อเดือน = 1%)
    carry_m = 100 * c5["คาดcarry"] / c5["มูลค่าขา"]
    # Kelly แบบต่อเนื่อง f ≈ Mean ÷ Var (ผลรายเดือนเป็นสัดส่วน)
    kel = {"F": q((mF_ / 100) / (sF_ / 100) ** 2, 0),
           "Fจากเลขปัด": q(D(str(q(mF_, 2))) / 100 / (D(str(q(sF_, 2))) / 100) ** 2, 0), "P": q((mP_ / 100) / (sP_ / 100) ** 2, 1),
           "Pตรวจ": q((S.mean(va["_P"]) / 100) / (S.sd(va["_P"]) / 100) ** 2, 2)}
    # หางสมมติ: ทุก 100 เดือนมีหนึ่งเดือนที่ exchange ถือขา spot ไว้ไม่คืน เสียครึ่งหนึ่งของเงิน (ตัวเลขสมมติเพื่อดูทิศ)
    tail_o = [(0.99, mF_ / 100), (0.01, -0.5)]
    kt = S.kelly_discrete(tail_o)
    kel["Fหาง"] = q(kt["f"], 2)
    kel["หางโอกาสเปอร์เซ็นต์"] = 1
    kel["หางเสียเปอร์เซ็นต์"] = 50
    # Risk Budget เท่ากัน: แต่ละงานได้ SD เท่ากัน → น้ำหนัก ∝ 1 ÷ SD (ไม่สนใจ correlation)
    def eq_risk(s1, s2):
        return 100 * (1 / s2) / (1 / s1 + 1 / s2)
    rb = {"ช่วงเลือกw": q(eq_risk(sF_, sP_), 0), "ช่วงตรวจw": q(eq_risk(S.sd(va["_F"]), S.sd(va["_P"])), 0),
          "หนึ่งส่วนSDF": q(1 / sF_, 2), "หนึ่งส่วนSDP": q(1 / sP_, 3)}
    rbw = rb["ช่วงเลือกw"] / 100
    pv = [(1 - rbw) * f + rbw * x for f, x in zip(va["_F"], va["_P"])]
    rb["ช่วงตรวจMean"], rb["ช่วงตรวจSD"] = q(S.mean(pv), 2), q(S.sd(pv), 2)
    rb["ช่วงตรวจratio"] = q(S.mean(pv) / S.sd(pv), 2)
    for sp in real:
        for k in ("_F", "_P", "_E"):
            real[sp].pop(k)
    out["จริง"] = {"ช่วงเลือก": fo, "ช่วงตรวจ": va, "เลือกw": pick, "ช่วงตรวจที่w": vrow,
                   "ช่วงตรวจw0": va["ตารางน้ำหนัก"][0], "ช่วงตรวจw50": va["ตารางน้ำหนัก"][5],
                   "ความไว": sens, "carryเดือนเปอร์เซ็นต์": q(carry_m, 2), "Kelly": kel, "งบความเสี่ยง": rb,
                   "SDคู่เท่า": q(va["P"]["SD"] / fo["P"]["SD"], 1),
                   "ดูช่วงตรวจ": 1, "การ์ด": {"h": PAIR_H, "ชุด": PAIR_SETS, "เข้า": 2, "ออก": 0.5, "ถือ": 30},
                   "สองหน่วยFมูลค่า": 1000}

    # ════════════ ตอน ค · 2  🎲 โลกที่รู้น้ำหนักที่ถูก ════════════
    out["โลก"] = _weights_sim(q)

    # ════════════ ตอน ง  Kelly บนเกมฉลาก ════════════
    hand = _lottery_hand(q)
    outs = [(p, x / 5) for p, x in zip(LOT_P, LOT_PAY)]
    k = S.kelly_discrete(outs)
    fk = k["f"]
    g = lambda f, o=outs: S.kelly_growth(f, o)  # noqa: E731
    lnrow = {"ln108": q(math.log(1.08), 4), "ln096": q(math.log(0.96), 4), "ln090": q(math.log(0.90), 4),
             "ln108p": q(100 * math.log(1.08), 2), "ln096p": q(100 * math.log(0.96), 2), "ln090p": q(100 * math.log(0.90), 2)}
    parts_p = [q(D("0.5") * D(str(lnrow["ln108p"])), 2), q(D("0.3") * D(str(lnrow["ln096p"])), 2),
               q(D("0.2") * D(str(lnrow["ln090p"])), 2)]
    lnrow["ส่วนp"] = parts_p
    lnrow["gp"] = q(sum(D(str(x)) for x in parts_p), 2)
    lnrow["สิบgp"] = q(10 * D(str(lnrow["gp"])), 1)
    lnrow["expเงิน"] = q(LOT_WEALTH * math.exp(float(lnrow["สิบgp"]) / 100), 2)
    g10 = 0.5 * lnrow["ln108"] + 0.3 * lnrow["ln096"] + 0.2 * lnrow["ln090"]
    true_o = [(p, x / 5) for p, x in zip(LOT_TRUE_P, LOT_PAY)]
    kt2 = S.kelly_discrete(true_o)
    curve = [{"f": q(i / 100, 2), "เชื่อ": q(LOT_WEALTH * math.exp(10 * g(i / 100)), 2),
              "จริง": q(LOT_WEALTH * math.exp(10 * g(i / 100, true_o)), 2)}
             for i in range(0, 36)]
    out["ฉลาก"] = {
        "มือ": hand, "ln": lnrow, "gจากเลขปัด": q(g10, 4), "สิบgจากเลขปัด": q(10 * g10, 3),
        "expสิบg": q(math.exp(10 * g10), 4), "ตาละย่อ": [q(x / 5, 1) for x in LOT_PAY],
        "Kelly": {"f": q(fk, 2), "fเปอร์เซ็นต์": q(100 * fk, 0), "ใบ": q(fk * LOT_WEALTH / 5, 1),
                  "g": q(k["growth"], 4), "gp": q(100 * k["growth"], 2), "สิบตา": q(math.exp(10 * k["growth"]), 4),
                  "สิบตาเงิน": q(LOT_WEALTH * math.exp(10 * k["growth"]), 2), "ร้อยตา": q(math.exp(100 * k["growth"]), 2),
                  "ev": q(k["ev"], 2), "evต่อใบ": q(5 * k["ev"], 1)},
        "ครึ่ง": {"f": q(fk / 2, 2), "fเปอร์เซ็นต์": q(50 * fk, 0), "g": q(g(fk / 2), 4), "gp": q(100 * g(fk / 2), 2), "สิบตา": q(math.exp(10 * g(fk / 2)), 4),
                  "สิบตาเงิน": q(LOT_WEALTH * math.exp(10 * g(fk / 2)), 2),
                  "ร้อยตา": q(math.exp(100 * g(fk / 2)), 2), "ส่วนของเต็มเปอร์เซ็นต์": q(100 * g(fk / 2) / k["growth"], 0)},
        "สองเท่า": {"f": q(2 * fk, 2), "g": q(g(2 * fk), 4), "ร้อยตา": q(math.exp(100 * g(2 * fk)), 2)},
        "โอกาสจริงแย่กว่า": {"โอกาส": LOT_TRUE_P, "ev": q(sum(p * x for p, x in zip(LOT_TRUE_P, LOT_PAY)), 2),
                            "Kellyจริง": q(kt2["f"], 2), "Kellyจริงเปอร์เซ็นต์": q(100 * kt2["f"], 0),
                            "gเต็ม": q(g(fk, true_o), 4), "gครึ่ง": q(g(fk / 2, true_o), 5),
                            "gเต็มp": q(100 * g(fk, true_o), 2), "gครึ่งp": q(100 * g(fk / 2, true_o), 2),
                            "ร้อยตาเต็ม": q(math.exp(100 * g(fk, true_o)), 2), "ร้อยตาครึ่ง": q(math.exp(100 * g(fk / 2, true_o)), 2)},
        "เส้น": curve, "แกน": [0, 5, 10, 15, 20, 25, 30, 35], "แกนy": [70, 80, 90, 100, 110],
        "ค่าเล่น": {"ค่า": [x - lot["ค่าเล่นต่อตา"] for x in LOT_PAY], "ev": q(sum(p * (x - lot["ค่าเล่นต่อตา"]) for p, x in zip(LOT_P, LOT_PAY)), 2),
                    "Kelly": q(S.kelly_discrete([(p, (x - lot["ค่าเล่นต่อตา"]) / 5.5) for p, x in zip(LOT_P, LOT_PAY)])["f"], 2),
                    "สิบตาที่สองใบ": q(100 * (1 + 2 * 3.5 / 100) ** 5 * (1 - 2 * 2.5 / 100) ** 3 * (1 - 2 * 5.5 / 100) ** 2, 2),
                    "คูณ": [q(1 + 2 * 3.5 / 100, 2), q(1 - 2 * 2.5 / 100, 2), q(1 - 2 * 5.5 / 100, 2)]},
        "จำลอง": {"ตา": LOT_DRAWS, "โลก": len(SEEDS),
                  "เชื่อ": {"เต็ม": _lottery_sim(fk, LOT_P, q), "ครึ่ง": _lottery_sim(fk / 2, LOT_P, q), "สองเท่า": _lottery_sim(2 * fk, LOT_P, q)},
                  "จริง": {"เต็ม": _lottery_sim(fk, LOT_TRUE_P, q), "ครึ่ง": _lottery_sim(fk / 2, LOT_TRUE_P, q),
                           "สองเท่า": _lottery_sim(2 * fk, LOT_TRUE_P, q)}},
    }

    # ════════════ 🧰 คนทำงานจริง (tools/sab_research/practitioner-research.md §0 · §7 · §8.5 · ตัวเลขตามบันทึก) ════════════
    sh = data.get("ch08", {}).get("ขาร่วม", {})
    out["คนทำงานจริง"] = {"corrLTC": sh.get("corrLTC", 0.92), "corrXRP": sh.get("corrXRP", 1), "คู่LTC": 8,
                          "แยกได้": sh.get("แยกได้สูงสุด", 5), "เหรียญ": sh.get("เหรียญ", 10), "คู่ทั้งหมด": 45,
                          "ปีGGR": "2006", "ห้าคู่": 5, "ยี่สิบคู่": 20, "ปีDoFaff": "2012", "ปีหลังDoFaff": "2002",
                          "ปีRad": "2016", "ปีโอกาสลด": "2009", "ปีCK": "2018", "CKปีเริ่ม": "2010", "CKปีจบ": "2015",
                          "ปีKL": "2011", "KLปีเหตุการณ์": "2007"}

    # ════════════ แบบฝึก ════════════
    ex = {}
    # ข้อ 1: carry + funding อย่างละหนึ่งหน่วย
    cf = [a + b for a, b in zip(SIX["carry"], F)]
    mcf = S.mean(cf)
    vcf = S.var(cf)
    ex["ข้อ1"] = {"รวม": cf, "Mean": q(mcf, 0), "ห่าง": [q(x - mcf, 0) for x in cf], "รวมห่างกำลังสอง": q(sum((x - mcf) ** 2 for x in cf), 0),
                 "Var": q(vcf, 2), "SD": q(math.sqrt(vcf), 2), "ratio": q(mcf / math.sqrt(vcf), 2),
                 "บวกSD": q(math.sqrt(S.var(SIX["carry"])) + math.sqrt(vF), 2), "สองเท่าcov": q(2 * cC, 0)}
    # ข้อ 2: ถ้า cov เป็น 0
    ex["ข้อ2"] = {"Var": q(vF + vP, 2), "SD": q(math.sqrt(vF + vP), 2), "ratio": q((mF + mP) / math.sqrt(vF + vP), 2)}
    # ข้อ 5: BTC + ETH funding carry ครึ่งต่อครึ่ง (ช่วงเลือก · ใช้ค่าปัดบนหน้า)
    sB, sE, rBE = fo["F"]["SD"], fo["E"]["SD"], fo["E"]["rhoกับBTC"]
    bB, bE = sB * 100, sE * 100          # เป็นเงินต่อขา spot 10,000
    v5 = 0.25 * bB ** 2 + 0.25 * bE ** 2 + 2 * 0.25 * rBE * bB * bE
    ex["ข้อ5"] = {"ขาspot": 10000, "sB": sB, "sE": sE, "rho": rBE, "เงินB": q(bB, 0), "เงินE": q(bE, 0), "ส่วน1": q(0.25 * bB ** 2, 0),
                 "ส่วน2": q(0.25 * bE ** 2, 0), "ส่วน3": q(0.5 * rBE * bB * bE, 0), "Var": q(v5, 0), "SDเงิน": q(math.sqrt(v5), 1),
                 "SD": q(math.sqrt(v5) / 100, 2), "SDถ้าอิสระเงิน": q(math.sqrt(0.25 * bB ** 2 + 0.25 * bE ** 2), 1),
                 "SDถ้าอิสระ": q(math.sqrt(0.25 * bB ** 2 + 0.25 * bE ** 2) / 100, 2)}
    out["แบบฝึก"] = ex
    # ตัวเลขกลางทางที่หน้าเขียนเป็นข้อความ (ให้ตามที่มาได้)
    mFr, sFr = D(str(fo["F"]["Mean"])), D(str(fo["F"]["SD"]))
    out["กลางทาง"] = {"เดือนให้Meanคลาดครึ่ง": q((D(str(SIM_SD[1])) / D("0.5")) ** 2, 0),
                      "หดตัวอย่าง": {"ประมาณ": [0.6, 1.4], "กลาง": 1, "หด": [0.8, 1.2]},
                      "สองใบเงิน": [LOT_WEALTH + 2 * x for x in LOT_PAY],
                      "SDกำลังสอง": q(sFr * sFr, 2), "Meanหารvar": q(mFr / D(str(q(sFr * sFr, 2))) * 100, 0),
                      "ข้อ1ลืมcov": q(S.var(SIX["carry"]) + vF, 1),
                      "ข้อ3ev": [q(D("0.5") * D("3.5"), 2), q(D("0.3") * D("2.5"), 2), q(D("0.2") * D("5.5"), 2)],
                      "ผสมMean": [[q(r["F"] * mF, 2), q(r["P"] * mP, 2)] for r in mix],
                      "ยี่สิบสี่ยกลบ": [q(1.24 * 0.76, 2)]}
    out["_แบบฝึก"] = [
        {"โจทย์": "(ทำตาม) funding carry + คู่ อย่างละหนึ่งหน่วย หกเดือน — SD ของผลรวมสองวิธี", "คำตอบ": out["พอร์ต"]["SDรวม"]},
        {"โจทย์": "(เปลี่ยนเลข) ถ้า Covariance เป็น 0 แทน −8.4 — SD และผลต่อความเสี่ยงของหนึ่งหน่วยต่อหนึ่งหน่วย", "คำตอบ": ex["ข้อ2"]["SD"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ฉลากมีค่าเล่น 0.5 ต่อใบ — สิบตาที่ขนาดสองใบ และ Kelly", "คำตอบ": out["ฉลาก"]["ค่าเล่น"]["สิบตาที่สองใบ"]},
        {"โจทย์": "(ตัดสินใจ) Kelly ของ funding carry บอกราว 110 เท่า ต้นจะใช้ 20 เท่า", "คำตอบ": kel["Fหาง"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) funding carry BTC ครึ่ง ETH ครึ่ง ช่วงเลือก — SD ของพอร์ต", "คำตอบ": ex["ข้อ5"]["SD"]},
    ]
    return out
