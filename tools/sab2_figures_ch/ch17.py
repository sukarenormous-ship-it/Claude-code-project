"""บท 17 เล่ม 2 — สิ่งที่อยู่ถัดไป: ความสัมพันธ์ไม่เป็นเส้นตรง และ options · ค่าทุกตัวของบท (ปลั๊กอินของ tools/sab_figures.py --book sab2)

ตอน ก  Copula ด้วยมือ: สิบวันของ A กับ B → อันดับ → ห้ากลุ่ม → ตาราง 5 × 5 → ความน่าจะเป็นแบบมีเงื่อนไข
       สองโลกที่ Rank Correlation เท่ากัน (0.9) แต่วันแย่สุดของ A ไปด้วยกันกับ B 100% เทียบ 0%
ตอน ข  ข้อมูลจริง: BTC–ETH การขยับ log รายวัน ช่วงเลือก / ช่วงตรวจ · 10% ล่างกับ 10% บนไปด้วยกันกี่วัน ·
       ตาราง 5 × 5 ของช่วงเลือก · 45 คู่ · เทียบโลกปกติ (Gaussian · random_walk_pair) และโลกตกพร้อมกันที่รู้คำตอบ
ตอน ค  Options สำหรับคน stat arb: ต้นไม้สองทางด้วยมือ (ค่าพรีเมียม = ค่าเฉลี่ยของ payoff เมื่อราคาเฉลี่ยไม่เปลี่ยน ·
       ดอกเบี้ยศูนย์) · Put-Call Parity · เพดานขาดทุนของขา short · ข้อมูลจริง: short X ของ BTC–ETH 12 ไม้ ไม้ละ 30 วัน
       ในช่วงตรวจ (แบบที่เครื่องของบท 13 ถือเกือบทั้งปี) ซื้อ call BTC +10% และ put ETH −10% ตั้งราคาด้วย Black-Scholes
       (σ จากช่วงเลือก · ดอกเบี้ยศูนย์ · ไม่ใช่ราคาตลาด — ชุดข้อมูลกลางไม่มีราคา options) · โลกจำลองที่รู้ σ จริง

ข้อมูลจริงผ่าน sab2_realdata.load_closes เท่านั้น (ช่วงเลือก · ช่วงตรวจ · ไม่แตะช่วงทดสอบสุดท้าย) · สถิติผ่าน sab2_stats ·
โลกจำลองผ่าน sab2_sim (seed ระบุทุกที่ · ชุด seed 1–30 ของเล่ม)
"""

import itertools
import math
import statistics

import sab2_realdata as R
import sab2_sim as M
import sab2_stats as S

TAIL = 0.10           # หาง = 10% ล่าง / บนของวัน
GROUPS = 5            # ตาราง 5 × 5
CRASH_P, CRASH_K, CRASH_RHO = 0.07, 0.12, 0.70     # โลกตกพร้อมกัน: วันปกติ ρ 0.7 + 7% ของวันตกเพิ่มพร้อมกัน 12%
LONG_N = 200000       # โลกยาวมากเพื่อหา "ค่าจริงของโลก" (ไม่ใช่การสุ่มเพื่อ p-value)
OPT_DAYS, OPT_WINDOWS, OTM = 30, 12, 0.10
POS_BTC, POS_ETH = 0.01, 0.24                     # short X ของบท 13: short BTC 0.01 · long ETH 0.24
SIM_WINDOWS = 120     # โลกจำลอง options: ไม้ต่อโลก
HIGH_VOL = 1.4        # โลกที่ความผันผวนจริงสูงกว่าที่ตั้งราคา 1.4 เท่า


def _ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0] * len(v)
    for k, i in enumerate(o):
        r[i] = k + 1
    return r


def _group(rank, n, g=GROUPS):
    """อันดับ 1..n → กลุ่ม 1..g (กลุ่ม 1 = วันที่แย่ที่สุด)"""
    return min(g, (rank - 1) * g // n + 1)


def _grid(a, b, g=GROUPS):
    n = len(a)
    ra, rb = _ranks(a), _ranks(b)
    cells = [[0] * g for _ in range(g)]
    for x, y in zip(ra, rb):
        cells[_group(x, n, g) - 1][_group(y, n, g) - 1] += 1
    return cells


def _tails(a, b, q=TAIL):
    """จำนวนวันในหาง (k) · วันที่ทั้งสองอยู่ 10% ล่างพร้อมกัน · 10% บนพร้อมกัน · Pearson · Rank Correlation"""
    n = len(a)
    ra, rb = _ranks(a), _ranks(b)
    k = int(round(q * n))
    lo = sum(1 for i in range(n) if ra[i] <= k and rb[i] <= k)
    hi = sum(1 for i in range(n) if ra[i] > n - k and rb[i] > n - k)
    return {"k": k, "ล่าง": lo, "บน": hi, "ล่างสัดส่วน": lo / k, "บนสัดส่วน": hi / k,
            "pearson": S.corr(a, b), "rank": S.corr(ra, rb)}


def _lr(p):
    return S.diff(S.logs(p))


# ───────────────────────── ตอน ก: สิบวันด้วยมือ ─────────────────────────

HAND_A = [1.2, -4.0, 0.5, -0.8, 3.1, -2.5, 0.1, 2.0, -1.5, 4.4]          # % ต่อวันของ A
B_SORTED = [-5.0, -3.2, -1.0, -0.6, -0.2, 0.3, 0.9, 1.6, 2.4, 3.0]       # ค่าของ B เรียงจากแย่สุด (อันดับ 1..10)
MAP_TOGETHER = {1: 1, 2: 2, 3: 5, 4: 6, 5: 3, 6: 4, 7: 7, 8: 8, 9: 9, 10: 10}   # อันดับ A → อันดับ B (โลก "ตกพร้อมกัน")
MAP_APART = {1: 3, 2: 4, 3: 1, 4: 2, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10}      # โลก "หางแยก" (Σd² เท่ากัน)


def _hand_world(mapping, q):
    ra = _ranks(HAND_A)
    rb = [mapping[r] for r in ra]
    b = [B_SORTED[r - 1] for r in rb]
    n = len(HAND_A)
    d2 = [(x - y) ** 2 for x, y in zip(ra, rb)]
    ga = [_group(r, n) for r in ra]
    gb = [_group(r, n) for r in rb]
    cells = [[0] * GROUPS for _ in range(GROUPS)]
    for x, y in zip(ga, gb):
        cells[x - 1][y - 1] += 1
    worst = [i for i in range(n) if ga[i] == 1]
    both = sum(1 for i in worst if gb[i] == 1)
    best = [i for i in range(n) if ga[i] == GROUPS]
    both_top = sum(1 for i in best if gb[i] == GROUPS)
    mean_r = (n + 1) / 2
    ss = sum((r - mean_r) ** 2 for r in ra)
    prod = sum((x - mean_r) * (y - mean_r) for x, y in zip(ra, rb))
    spread_worst = [q(HAND_A[i] - b[i], 2) for i in worst]          # long A หนึ่งส่วน short B หนึ่งส่วน (เงินเท่ากัน) ในวันแย่สุดของ A
    return {
        "วัน": [{"วัน": i + 1, "A": HAND_A[i], "B": b[i], "อันดับA": ra[i], "อันดับB": rb[i], "กลุ่มA": ga[i], "กลุ่มB": gb[i],
                 "ต่าง2": d2[i]} for i in range(n)],
        "ตาราง": cells, "รวมต่าง2": sum(d2), "หกเท่า": 6 * sum(d2), "ตัวหาร": n * (n * n - 1),
        "rank": q(1 - 6 * sum(d2) / (n * (n * n - 1)), 2), "rank_สามตำแหน่ง": q(1 - 6 * sum(d2) / (n * (n * n - 1)), 3),
        "ผลรวมกำลังสอง": q(ss, 1), "ผลรวมผลคูณ": q(prod, 1), "rankทางคูณ": q(prod / ss, 2),
        "pearson": q(S.corr(HAND_A, b), 2),
        "วันแย่สุดของA": [i + 1 for i in worst], "Bในวันแย่สุด": [b[i] for i in worst],
        "อันดับBในวันแย่สุด": [rb[i] for i in worst],
        "ไปด้วยกันล่าง": both, "ความน่าจะเป็นล่าง": q(100 * both / len(worst), 0),
        "ไปด้วยกันบน": both_top, "ความน่าจะเป็นบน": q(100 * both_top / len(best), 0),
        "คู่ในวันแย่สุด": spread_worst, "คู่ในวันแย่สุดรวม": q(sum(spread_worst), 2),
        "_b": b,
    }


def _hand(q):
    t = _hand_world(MAP_TOGETHER, q)
    a = _hand_world(MAP_APART, q)
    # แบบฝึก ข้อ 2: วันแย่สุดของ B ในโลกตกพร้อมกันกลายเป็น −15 (แทน −5) → Pearson ขยับ อันดับไม่ขยับ
    b2 = list(t["_b"])
    i = b2.index(min(b2))
    b2[i] = -15.0
    t2 = _tails(HAND_A, b2)
    drill2 = {"วัน": i + 1, "ใหม่": -15.0, "pearson": q(S.corr(HAND_A, b2), 2), "rank": q(t2["rank"], 2)}
    t.pop("_b")
    a.pop("_b")
    return {"n": len(HAND_A), "กลุ่ม": GROUPS, "วันต่อกลุ่ม": len(HAND_A) // GROUPS, "อันดับกลาง": (len(HAND_A) + 1) / 2,
            "ตกพร้อมกัน": t, "หางแยก": a, "แบบฝึก2": drill2,
            "ระดับ": {"อันดับ1": q(1 / (len(HAND_A) + 1), 2), "อันดับ10": q(10 / (len(HAND_A) + 1), 2)}}


# ───────────────────────── ตอน ข: ข้อมูลจริง + โลกจำลอง ─────────────────────────

def _real_tails(q):
    out = {}
    for split in ("formation", "validation"):
        d, P = R.load_closes(split)
        ret = {c: _lr(P[c]) for c in P}
        dates = d[1:]
        a, b = ret["BTC"], ret["ETH"]
        t = _tails(a, b)
        n = len(a)
        rec = {"วันข้อมูล": len(d), "วันขยับ": n, "เริ่ม": d[0], "จบ": d[-1],
               "pearson": q(t["pearson"], 2), "rank": q(t["rank"], 2), "k": t["k"],
               "ล่าง": t["ล่าง"], "บน": t["บน"], "ล่างเปอร์เซ็นต์": q(100 * t["ล่างสัดส่วน"], 0),
               "บนเปอร์เซ็นต์": q(100 * t["บนสัดส่วน"], 0), "ล่างลบบน": t["ล่าง"] - t["บน"],
               "ไม่ตามเปอร์เซ็นต์": 100 - q(100 * t["ล่างสัดส่วน"], 0), "หางห้าเปอร์เซ็นต์วัน": int(round(0.05 * n))}
        rows = []
        for x, y in itertools.combinations(list(P), 2):
            tt = _tails(ret[x], ret[y])
            rows.append({"คู่": f"{x}/{y}", "ล่าง": tt["ล่างสัดส่วน"], "บน": tt["บนสัดส่วน"], "pearson": tt["pearson"],
                         "rank": tt["rank"]})
        rec["สี่สิบห้า"] = {"คู่": len(rows), "ล่างมากกว่าบน": sum(1 for r in rows if r["ล่าง"] > r["บน"]),
                             "ล่างเท่าบน": sum(1 for r in rows if r["ล่าง"] == r["บน"]),
                             "ล่างเฉลี่ยเปอร์เซ็นต์": q(100 * statistics.mean(r["ล่าง"] for r in rows), 0),
                             "บนเฉลี่ยเปอร์เซ็นต์": q(100 * statistics.mean(r["บน"] for r in rows), 0),
                             "pearsonเฉลี่ย": q(statistics.mean(r["pearson"] for r in rows), 2),
                             "rankเฉลี่ย": q(statistics.mean(r["rank"] for r in rows), 2)}
        if split == "formation":
            g = _grid(a, b)
            rec["ตาราง"] = g
            rec["วันต่อกลุ่ม"] = n // GROUPS
            rec["มุมล่าง"], rec["มุมบน"] = g[0][0], g[-1][-1]
            rec["มุมล่างเปอร์เซ็นต์"] = q(100 * g[0][0] / sum(g[0]), 0)
            rec["มุมบนเปอร์เซ็นต์"] = q(100 * g[-1][-1] / sum(g[-1]), 0)
            rec["มุมตรงข้าม"] = g[0][-1] + g[-1][0]
            # สิบวันที่ BTC แย่ที่สุด (ตาราง 📡 ตัวอย่าง)
            ra, rb = _ranks(a), _ranks(b)
            worst = sorted(range(n), key=lambda i: a[i])[:10]
            rec["สิบวันแย่สุด"] = [{"วัน": dates[i], "BTC": q(100 * a[i], 2), "อันดับBTC": ra[i], "ETH": q(100 * b[i], 2),
                                    "อันดับETH": rb[i], "ในหางล่าง": rb[i] <= t["k"]} for i in worst]
            rec["สิบวันแย่สุดETHในหาง"] = sum(1 for i in worst if rb[i] <= t["k"])
            j = next(i for i in worst if rb[i] > t["k"])          # วันแย่สุดของ BTC ที่ ETH ไม่อยู่หางล่าง
            leg_b, leg_e = q(10 * q(100 * a[j], 2), 2), q(-10 * q(100 * b[j], 2), 2)   # long BTC 1,000 · short ETH 1,000
            rec["วันหางแยก"] = {"วัน": dates[j], "BTC": q(100 * a[j], 2), "ETH": q(100 * b[j], 2), "อันดับETH": rb[j],
                                "ขาBTC": leg_b, "ขาETH": leg_e, "รวม": q(leg_b + leg_e, 2)}
            rec["_a"], rec["_b"] = a, b
        out[split] = rec
    return out


def _gauss_world(seed, n, rho):
    """โลกปกติ: random_walk_pair ของ sab2_sim · การขยับ log ของ B = แรงร่วม SD 3% · ของ A = แรงร่วม + ส่วนเฉพาะ
    เลือก SD ส่วนเฉพาะให้ correlation จริงของโลก = rho · การแจกแจงปกติทั้งคู่ → หางล่างกับหางบนสมมาตร"""
    sd = M.COMMON_SD * math.sqrt(1 / rho ** 2 - 1)
    w = M.random_walk_pair(seed=seed, n=n + 1, sd=sd)
    return S.diff(w["logA"]), S.diff(w["logB"])


def _crash_world(seed, n, rho=CRASH_RHO, p=CRASH_P, k=CRASH_K):
    """โลกตกพร้อมกัน: โลกปกติ ρ 0.7 + วันที่ "ตัวสุ่มตัวที่สาม" (stationary_pair φ 0 = ปกติมาตรฐานอิสระ) ต่ำกว่าเส้น p ล่าง
    สองเหรียญตกเพิ่มพร้อมกัน k (log) · รู้คำตอบ: หางล่างไปด้วยกันมากกว่าหางบน"""
    a, b = _gauss_world(seed, n, rho)
    z = M.stationary_pair(seed=seed + 1000, n=n, phi=0.0, sd=1.0)["X"]
    cut = S.norm_ppf(p)
    a = [x - (k if zz < cut else 0.0) for x, zz in zip(a, z)]
    b = [x - (k if zz < cut else 0.0) for x, zz in zip(b, z)]
    return a, b


def _worlds_tails(q, rho):
    out = {}
    for name, fn in (("ปกติ", lambda s, n: _gauss_world(s, n, rho)), ("ตกพร้อมกัน", lambda s, n: _crash_world(s, n))):
        rec = {}
        for label, n in (("ยาวเท่าช่วงเลือก", 730), ("ยาวเท่าช่วงตรวจ", 364)):
            rs = [_tails(*fn(sd, n)) for sd in M.ROBUST_SEEDS]
            rec[label] = {"ล่างมัธยฐาน": q(100 * statistics.median(r["ล่างสัดส่วน"] for r in rs), 0),
                          "ล่างต่ำสุด": q(100 * min(r["ล่างสัดส่วน"] for r in rs), 0),
                          "ล่างสูงสุด": q(100 * max(r["ล่างสัดส่วน"] for r in rs), 0),
                          "บนมัธยฐาน": q(100 * statistics.median(r["บนสัดส่วน"] for r in rs), 0),
                          "บนต่ำสุด": q(100 * min(r["บนสัดส่วน"] for r in rs), 0),
                          "บนสูงสุด": q(100 * max(r["บนสัดส่วน"] for r in rs), 0),
                          "pearsonมัธยฐาน": q(statistics.median(r["pearson"] for r in rs), 2),
                          "rankมัธยฐาน": q(statistics.median(r["rank"] for r in rs), 2),
                          "ล่างมากกว่าบน": sum(1 for r in rs if r["ล่าง"] > r["บน"]), "โลก": len(rs)}
        big = _tails(*fn(7, LONG_N))
        rec["ค่าจริง"] = {"ล่าง": q(100 * big["ล่างสัดส่วน"], 0), "บน": q(100 * big["บนสัดส่วน"], 0),
                          "pearson": q(big["pearson"], 2)}
        out[name] = rec
    v = out["ปกติ"]["ยาวเท่าช่วงตรวจ"]
    out["กว้างโลกปกติช่วงตรวจ"] = v["ล่างสูงสุด"] - v["ล่างต่ำสุด"]
    out["rhoโลกปกติ"] = q(rho, 2)
    out["ตกพร้อมกัน_ค่า"] = {"วันตกเปอร์เซ็นต์": q(100 * CRASH_P, 0), "ตกเพิ่มเปอร์เซ็นต์": q(100 * CRASH_K, 0),
                             "rhoวันปกติ": CRASH_RHO}
    return out


def _spread_tail(q):
    """หางของ X ของคู่ BTC–ETH บน log ราคา (h จาก Regression ช่วงเลือก บท 2): การขยับรายวันเกิน 3 SD กี่วัน
    เทียบการแจกแจงปกติ (0.27% ของวัน)"""
    _, pf = R.load_closes("formation", coins=["BTC", "ETH"])
    _, pv = R.load_closes("validation", coins=["BTC", "ETH"])
    h = S.ols(S.logs(pf["ETH"]), S.logs(pf["BTC"]))["slope"]
    p_norm = 2 * (1 - S.norm_cdf(3))
    out = {"h": q(h, 2), "ปกติเปอร์เซ็นต์": q(100 * p_norm, 2)}
    for name, p in (("ช่วงเลือก", pf), ("ช่วงตรวจ", pv)):
        x = [100 * (a - h * b) for a, b in zip(S.logs(p["BTC"]), S.logs(p["ETH"]))]
        dx = S.diff(x)
        m, s = S.mean(dx), S.sd(dx)
        out[name] = {"วัน": len(dx), "SD": q(s, 2), "เกินสาม": sum(1 for v in dx if abs(v - m) > 3 * s),
                     "คาดถ้าปกติ": q(p_norm * len(dx), 0), "ขึ้นมากสุด": q(max(dx), 2), "ลงมากสุด": q(min(dx), 2),
                     "ลงมากสุดเท่าSD": q(abs(min(dx)) / s, 0)}
    return out


# ───────────────────────── ตอน ค: options ─────────────────────────

def _bs_call(s0, strike, sig, t):
    """Black-Scholes ดอกเบี้ยศูนย์ ไม่มีเงินปันผล (ต้นไม้สองทางหลายขั้นจนละเอียด) · ใช้ S.norm_cdf"""
    d1 = (math.log(s0 / strike) + 0.5 * sig * sig * t) / (sig * math.sqrt(t))
    return s0 * S.norm_cdf(d1) - strike * S.norm_cdf(d1 - sig * math.sqrt(t))


def _bs_put(s0, strike, sig, t):
    return _bs_call(s0, strike, sig, t) - s0 + strike          # Put-Call Parity ที่ดอกเบี้ยศูนย์


def _tree(q):
    """ต้นไม้สองทางด้วยมือ: A 100 · ขึ้นหรือลงเท่ากันโอกาสครึ่งหนึ่ง (ราคาเฉลี่ยยังเป็น 100) · ดอกเบี้ยศูนย์"""
    a0 = 100
    out = {"ราคาเริ่ม": a0}
    for move in (20, 30):
        up, dn = a0 + move, a0 - move
        rec = {"ขึ้น": up, "ลง": dn}
        for k in (100, 110):
            cu, cd = max(up - k, 0), max(dn - k, 0)
            pu, pd = max(k - up, 0), max(k - dn, 0)
            call, put = (cu + cd) / 2, (pu + pd) / 2
            rec[f"k{k}"] = {"callขึ้น": cu, "callลง": cd, "call": q(call, 2), "putขึ้น": pu, "putลง": pd, "put": q(put, 2),
                            "callลบput": q(call - put, 2), "ราคาลบk": a0 - k}
        out[f"ขยับ{move}"] = rec
    # เพดานขาดทุนของขา short A หนึ่งเหรียญที่ 100 ด้วย call ราคาใช้สิทธิ์ 110 ค่าพรีเมียม 5 (จากต้นไม้ ±20)
    prem = out["ขยับ20"]["k110"]["call"]
    rows = []
    for a in (80, 90, 100, 110, 120, 130, 140):
        short = a0 - a
        pay = max(a - 110, 0)
        rows.append({"A": a, "short": short, "call": pay, "พรีเมียม": -prem, "รวม": q(short + pay - prem, 2)})
    out["เพดานขยับ30"] = q((110 - a0) + out["ขยับ30"]["k110"]["call"], 2)
    out["เพดาน"] = {"แถว": rows, "พรีเมียม": prem, "ขาดทุนสูงสุด": q((110 - a0) + prem, 2), "ห่างราคาใช้สิทธิ์": 110 - a0,
                    "ไม่มีเพดานที่140": a0 - 140}
    # Put-Call Parity ราคาผิด: call 8 put 15 ที่ราคาใช้สิทธิ์ 110 (ควรต่าง −10) → ล็อก 3
    out["ราคาผิด"] = {"call": 8, "put": 15, "ต่างจริง": 8 - 15, "ควรต่าง": a0 - 110, "เงินที่ใช้": a0 + 15 - 8,
                     "ล็อก": 110 - (a0 + 15 - 8)}
    return out


def _options_real(q):
    """12 ไม้ ไม้ละ 30 วันในช่วงตรวจ: short X ของบท 13 (short BTC 0.01 · long ETH 0.24) · call BTC ราคาใช้สิทธิ์ +10% ·
    put ETH ราคาใช้สิทธิ์ −10% · ตั้งราคาด้วย Black-Scholes σ จากช่วงเลือก (SD การขยับ log รายวัน × √365) · ดอกเบี้ยศูนย์ ·
    ไม่มีค่าธรรมเนียม options · ไม่ใช่ราคาตลาด"""
    _, pf = R.load_closes("formation", coins=["BTC", "ETH"])
    dv, pv = R.load_closes("validation", coins=["BTC", "ETH"])
    sd_d = {c: S.sd(_lr(pf[c])) for c in ("BTC", "ETH")}
    sd_v = {c: S.sd(_lr(pv[c])) for c in ("BTC", "ETH")}
    root = math.sqrt(365)
    sig = {c: sd_d[c] * root for c in sd_d}
    t = OPT_DAYS / 365
    A, B = pv["BTC"], pv["ETH"]
    rows = []
    for w in range(OPT_WINDOWS):
        t0, t1 = OPT_DAYS * w, OPT_DAYS * (w + 1)
        a0, a1, b0, b1 = A[t0], A[t1], B[t0], B[t1]
        leg_btc, leg_eth = -POS_BTC * (a1 - a0), POS_ETH * (b1 - b0)
        pc = POS_BTC * _bs_call(a0, (1 + OTM) * a0, sig["BTC"], t)
        pp = POS_ETH * _bs_put(b0, (1 - OTM) * b0, sig["ETH"], t)
        gc = POS_BTC * max(a1 - (1 + OTM) * a0, 0)
        gp = POS_ETH * max((1 - OTM) * b0 - b1, 0)
        base = leg_btc + leg_eth
        rows.append({"เริ่ม": dv[t0], "จบ": dv[t1], "BTCเริ่ม": q(a0, 2), "BTCจบ": q(a1, 2), "ETHเริ่ม": q(b0, 2), "ETHจบ": q(b1, 2),
                     "ขาBTC": q(leg_btc, 2), "ขาETH": q(leg_eth, 2), "ไม่มีเพดาน": q(base, 2),
                     "ค่าcall": q(pc, 2), "ค่าput": q(pp, 2), "ได้call": q(gc, 2), "ได้put": q(gp, 2),
                     "มีเพดาน": q(base - pc - pp + gc + gp, 2), "ค่ารวม": q(pc + pp, 2),
                     "BTCเปลี่ยนเปอร์เซ็นต์": q(100 * (a1 / a0 - 1), 0), "ETHเปลี่ยนเปอร์เซ็นต์": q(100 * (b1 / b0 - 1), 0), "_base": base, "_cap": base - pc - pp + gc + gp,
                     "_pc": pc, "_pp": pp, "_gc": gc, "_gp": gp})
    tot = {k: sum(r[f"_{k}"] for r in rows) for k in ("base", "cap", "pc", "pp", "gc", "gp")}
    worst_b = min(rows, key=lambda r: r["_base"])
    worst_c = min(rows, key=lambda r: r["_cap"])
    first = rows[0]
    r0 = {"BTC": A[0], "ETH": B[0]}
    for r in rows:
        for k in ("_base", "_cap", "_pc", "_pp", "_gc", "_gp"):
            r.pop(k)
    return {
        "σรายวันเปอร์เซ็นต์": {c: q(100 * sd_d[c], 2) for c in sd_d},
        "σต่อปีเปอร์เซ็นต์": {c: q(100 * sig[c], 1) for c in sig},
        "σต่อปีช่วงตรวจเปอร์เซ็นต์": {c: q(100 * sd_v[c] * root, 1) for c in sd_v},
        "σรายวันช่วงตรวจเปอร์เซ็นต์": {c: q(100 * sd_v[c], 2) for c in sd_v},
        "รากสามหกห้า": q(root, 2),
        "σต่อปีจากเลขปัด": {c: q(q(100 * sd_d[c], 2) * q(root, 2), 1) for c in sd_d},
        "ไม้": rows, "จำนวนไม้": OPT_WINDOWS, "วันต่อไม้": OPT_DAYS, "ห่างเปอร์เซ็นต์": q(100 * OTM, 0),
        "ไม้แรก": {"BTC": q(r0["BTC"], 2), "ราคาใช้สิทธิ์call": q((1 + OTM) * r0["BTC"], 2), "ค่าcallต่อเหรียญ": q(first["ค่าcall"] / POS_BTC, 2),
                   "ETH": q(r0["ETH"], 2), "ราคาใช้สิทธิ์put": q((1 - OTM) * r0["ETH"], 2), "ค่าputต่อเหรียญ": q(first["ค่าput"] / POS_ETH, 2),
                   "callต่อเหรียญเปอร์เซ็นต์": q(100 * first["ค่าcall"] / POS_BTC / r0["BTC"], 2)},
        "รวม": {"ไม่มีเพดาน": q(tot["base"], 2), "มีเพดาน": q(tot["cap"], 2), "ค่าcall": q(tot["pc"], 2), "ค่าput": q(tot["pp"], 2),
                "ได้call": q(tot["gc"], 2), "ได้put": q(tot["gp"], 2), "ค่าประกัน": q(tot["pc"] + tot["pp"], 2),
                "ได้คืน": q(tot["gc"] + tot["gp"], 2), "สุทธิcall": q(tot["gc"] - tot["pc"], 2), "สุทธิput": q(tot["gp"] - tot["pp"], 2),
                "สุทธิประกัน": q(tot["gc"] + tot["gp"] - tot["pc"] - tot["pp"], 2),
                "ได้ต่อจ่ายcall": q(tot["gc"] / tot["pc"], 2), "ได้ต่อจ่ายput": q(tot["gp"] / tot["pp"], 2),
                "ค่าประกันต่อทุนเปอร์เซ็นต์": q(100 * (tot["pc"] + tot["pp"]) / 1000, 1)},
        "ไม้แย่สุดไม่มีเพดาน": {"เริ่ม": worst_b["เริ่ม"], "ไม่มีเพดาน": worst_b["ไม่มีเพดาน"], "มีเพดาน": worst_b["มีเพดาน"],
                                "ขาBTC": worst_b["ขาBTC"], "ขาETH": worst_b["ขาETH"]},
        "ไม้แย่สุดมีเพดาน": {"เริ่ม": worst_c["เริ่ม"], "มีเพดาน": worst_c["มีเพดาน"], "ไม่มีเพดาน": worst_c["ไม่มีเพดาน"]},
        "ไม้ที่callจ่าย": sum(1 for r in rows if r["ได้call"] > 0), "ไม้ที่putจ่าย": sum(1 for r in rows if r["ได้put"] > 0),
        "ไม้ขาETHลบ": sum(1 for r in rows if r["ขาETH"] < 0), "ไม้ขาBTCลบ": sum(1 for r in rows if r["ขาBTC"] < 0),
        "แกนกราฟ": [-200, -100, 0, 100, 200, 300, 400],
    }


def _options_sim(q, sig_annual):
    """โลกที่รู้ σ จริง: ราคา = exp(เดินสุ่ม) ของ sab2_sim.random_walk_pair (ขา B · SD รายวันตามที่ตั้ง) คูณ exp(−SD² × วัน ÷ 2)
    ให้ราคาเฉลี่ยไม่เปลี่ยน (สมมติฐานเดียวกับต้นไม้ด้วยมือ · ดอกเบี้ยศูนย์) · ตั้งราคา call +10% 30 วันด้วย σ ช่วงเลือกของ BTC ·
    30 โลก × 120 ไม้ (ไม้มากพอให้ค่าเฉลี่ยนิ่ง) · โลกแรก σ จริง = σ ที่ตั้งราคา · โลกสอง σ จริง × 1.4"""
    t = OPT_DAYS / 365
    sd_daily = sig_annual / math.sqrt(365)
    out = {}
    for name, mult in (("เท่ากัน", 1.0), ("สูงกว่า", HIGH_VOL)):
        paid = got = 0.0
        hits = 0
        s2 = (sd_daily * mult) ** 2
        for sd in M.ROBUST_SEEDS:
            raw = M.random_walk_pair(seed=sd, n=OPT_DAYS * SIM_WINDOWS + 1, common_sd=sd_daily * mult)["B"]
            b = [v * math.exp(-s2 * i / 2) for i, v in enumerate(raw)]
            for w in range(SIM_WINDOWS):
                a0, a1 = b[OPT_DAYS * w], b[OPT_DAYS * (w + 1)]
                paid += _bs_call(a0, (1 + OTM) * a0, sig_annual, t) / a0
                g = max(a1 - (1 + OTM) * a0, 0) / a0
                got += g
                hits += g > 0
        n = len(M.ROBUST_SEEDS) * SIM_WINDOWS
        out[name] = {"ไม้": n, "จ่ายเฉลี่ยเปอร์เซ็นต์": q(100 * paid / n, 2), "ได้เฉลี่ยเปอร์เซ็นต์": q(100 * got / n, 2),
                     "ได้ต่อจ่าย": q(got / paid, 2), "ไม้ที่จ่าย": hits, "ไม้ที่จ่ายเปอร์เซ็นต์": q(100 * hits / n, 0),
                     "σจริงต่อปีเปอร์เซ็นต์": q(100 * sig_annual * mult, 1)}
    out["เท่า"] = HIGH_VOL
    out["โลก"] = len(M.ROBUST_SEEDS)
    out["ไม้ต่อโลก"] = SIM_WINDOWS
    return out


def extend(data, D, q):
    hand = _hand(q)
    real = _real_tails(q)
    rho = S.corr(real["formation"].pop("_a"), real["formation"].pop("_b"))
    worlds = _worlds_tails(q, rho)
    spread = _spread_tail(q)
    tree = _tree(q)
    opt = _options_real(q)
    sig_btc = opt["σต่อปีเปอร์เซ็นต์"]["BTC"] / 100
    osim = _options_sim(q, float(sig_btc))
    c13 = data["ch13"]["v2"]["จริง"]
    prev = {"บท13ผล": c13["ผล"], "บท13Equityต่ำสุด": c13["Equityต่ำสุด"], "บท13วันZเกินสอง": c13["วันที่Zเกิน2"],
            "บท13วันช่วงตรวจ": c13["ช่วงตรวจ"]["วัน"], "บท8ห้าคู่": data["ch08"]["ห้าคู่"]["ผล"]}
    looks = 2       # เปิดช่วงตรวจในบทนี้: (1) นับหางของ BTC–ETH และ 45 คู่ (2) 12 ไม้ short X พร้อม options
    drills = [
        {"โจทย์": "(ทำตาม) สิบวันของ A กับ B โลกตกพร้อมกัน — อันดับ กลุ่ม ตาราง 5 × 5 และความน่าจะเป็นที่ B อยู่กลุ่ม 1 เมื่อ A อยู่กลุ่ม 1",
         "คำตอบ": hand["ตกพร้อมกัน"]["ความน่าจะเป็นล่าง"]},
        {"โจทย์": "(เปลี่ยนเลข) วันแย่สุดของ B เป็น −15 แทน −5 — Pearson · Rank Correlation · ความน่าจะเป็นแบบมีเงื่อนไข",
         "คำตอบ": hand["แบบฝึก2"]["rank"]},
        {"โจทย์": "(เปลี่ยนเงื่อนไข) ต้นไม้ขยับ ±30 — ค่า call และ put ราคาใช้สิทธิ์ 110 และตรวจ Put-Call Parity",
         "คำตอบ": tree["ขยับ30"]["k110"]["callลบput"]},
        {"โจทย์": "(ตัดสินใจ) ต้นจะซื้อ put ETH ทุกเดือนเพราะช่วงตรวจได้กำไร — เห็นด้วยไหม",
         "คำตอบ": opt["รวม"]["สุทธิput"]},
        {"โจทย์": "(ถ่ายโอน · ข้อมูลจริง) ช่วงตรวจ 36 วันในหาง — ความน่าจะเป็นแบบมีเงื่อนไขล่างและบน เทียบช่วงของโลกปกติยาว 364 วัน",
         "คำตอบ": real["validation"]["ล่างเปอร์เซ็นต์"]},
    ]
    # กล่อง 🧰 (ที่มา: tools/sab_research/practitioner-research.md §1.1–1.2 · §5 · §9.1 · ตัวเลขตามที่บันทึกไว้ ไม่ได้คำนวณ)
    prac = {"ปีRad": "2016", "Radปีเริ่ม": "1962", "Radปีจบ": "2014",
            "ระยะก่อน": 0.91, "ระยะหลัง": 0.38, "coก่อน": 0.85, "coหลัง": 0.33, "copulaก่อน": 0.43, "copulaหลัง": 0.05,
            "ไม้บรรจบกำไร": 98, "ไม้บรรจบระยะ": 62.53,
            "ปีTadi": "2025", "ปีPindza": "2026", "Pindzaตัว": 10, "Pindzaปีเริ่ม": "2021", "Pindzaปีจบ": "2023", "Pindzaต้นทุน": 0.08}
    return {"_แบบฝึก": drills, "มือ": hand, "จริง": real, "โลก": worlds, "หางคู่": spread, "ต้นไม้": tree,
            "optionsจริง": opt, "optionsโลก": osim, "คนทำงานจริง": prac,
            "นับรอบ": {"ดูช่วงตรวจ_บทนี้": looks}, "ทวน": prev,
            "ค่า": {"หางเปอร์เซ็นต์": q(100 * TAIL, 0), "กลุ่ม": GROUPS, "ทุน": 1000, "เส้นสาม": 3, "วันโลกยาว": LONG_N,
                    "ขาBTC": POS_BTC, "ขาETH": POS_ETH},
            "แกนเพดาน": [-40, -20, 0, 20]}   # กราฟ sab2-cap-payoff (แกนตั้ง)
