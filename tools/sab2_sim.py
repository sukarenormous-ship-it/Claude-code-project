#!/usr/bin/env python3
"""โลกจำลองที่รู้คำตอบของเล่ม 2 (ต่อจากเล่ม 1) · seeded simulated worlds with known answers for volume 2

ต่อจากการจำลองของเล่ม 1 (tools/sab_figures.py rw/ar1/pair_c · tools/sab_figures_ch/ch13.py):
ใช้ random.Random(seed) แยกตัว · log ราคา = แรงร่วมแบบเดินสุ่ม + ส่วนเฉพาะ · ระยะห่าง (spread ของคู่) เป็น AR(1)
x[t] = φ·x[t−1] + e (φ < 1 = มีเชือก · φ = 1 = เดินสุ่ม) · ไม่ตั้งชื่อเหรียญจริง (แผน 6) · ไม่พึ่งข้อมูลจริง

ทุกโลกคืน dict: ซีรีส์ (log ราคา "logA"/"logB" และราคา "A"/"B" · ระยะห่างจริง "X") + "true" (พารามิเตอร์จริง) + "seed"
    stationary_pair    คู่ที่มีเชือก φ คงที่ (รู้ φ · h · ค่ากลาง · half-life) — h อยู่บน log ราคา
    price_pair         คู่ที่มีเชือกบนราคา A = α + h·B + X (รู้ h บนระดับราคา → ถดถอยแบบบท 1 ได้ h ในค่าคาดหวัง)
    drifting_price_pair  คู่บนราคาที่ h ไหลเป็นเส้นตรง h0 → h1 (บท 5 · rolling h ที่รู้คำตอบ)
    random_walk_pair   คู่ที่ไม่มีเชือก (ระยะห่างเดินสุ่ม φ = 1)
    drifting_h_pair    คู่ที่ h ค่อย ๆ ไหลจาก h0 ไป h1 (หรือเดินสุ่มช้า ๆ)
    broken_pair        คู่ที่เชือกขาดที่วัน break_at (φ ก่อน → φ หลัง · เลือกให้ค่ากลางกระโดดได้)
    threshold_pair     คู่บนราคาที่เชือกดึงเฉพาะเมื่อ |X| เกิน band (ในกรอบเดินสุ่ม · เล่ม 2 บท 7 Threshold Model)
    regime_pair        คู่บนราคาที่สลับสองสภาวะแบบสุ่ม (φ และค่ากลางต่างกันได้ · เล่ม 2 บท 7 Regime Switching)
    factor_basket      N เหรียญ = β_i × แรงร่วม + ส่วนเฉพาะที่กลับค่ากลาง (รู้ β · φ ของแต่ละตัว)
    reseed             รันโลกเดิมด้วย seed 1–30 (ชุดเดียวกับเล่ม 1) → ค่าต่ำสุด · มัธยฐาน · สูงสุด · ตัวอย่าง

    python3 tools/sab2_sim.py --selftest
"""

import math
import random
import statistics
import sys

ROBUST_SEEDS = list(range(1, 31))     # ชุด seed เดียวกับเล่ม 1 (sab_figures.ROBUST_SEEDS)
COMMON_SD = 0.03                      # SD ต่อวันของแรงร่วม (log) — เท่ากับ pair_c ของเล่ม 1
SPREAD_SD = 0.03                      # SD ต่อวันของแรงกระแทกระยะห่าง (log) — เท่ากับ ar1(…, 0.9, 0.03) ของเล่ม 1


def _rw(rng, n, sd, start=0.0):
    """เดินสุ่ม n วัน (วันแรก = start + ก้าวแรก) · random walk"""
    x, out = start, []
    for _ in range(n):
        x += rng.gauss(0.0, sd)
        out.append(x)
    return out


def _ar1(rng, n, phi, sd, start=None):
    """AR(1) n วัน · start=None → เริ่มจากการกระจายนิ่ง (φ < 1) หรือ 0 (φ ≥ 1)"""
    if start is None:
        start = rng.gauss(0.0, sd / math.sqrt(1 - phi * phi)) if abs(phi) < 1 else 0.0
    x, out = start, [start]
    for _ in range(n - 1):
        x = phi * x + rng.gauss(0.0, sd)
        out.append(x)
    return out


def _half_life(phi):
    return math.log(2.0) / -math.log(phi) if 0 < phi < 1 else float("inf")


def _prices(d):
    d["A"] = [math.exp(v) for v in d["logA"]]
    d["B"] = [math.exp(v) for v in d["logB"]]
    return d


def stationary_pair(seed=101, n=500, phi=0.95, h=1.0, alpha=math.log(2.0), sd=SPREAD_SD, common_sd=COMMON_SD,
                    b0=math.log(50.0)):
    """คู่ที่มีเชือก: logB = b0 + แรงร่วม · logA = α + h·logB + X · X เป็น AR(1) φ (เริ่มจากการกระจายนิ่ง)
    stationary (cointegrated) pair with known φ, h, α · ค่าเริ่มต้น: A ≈ 100 · B ≈ 50 แบบคู่ A–B ของเล่ม 1"""
    rng = random.Random(seed)
    logb = _rw(rng, n, common_sd, b0)
    x = _ar1(rng, n, phi, sd)
    loga = [alpha + h * b + e for b, e in zip(logb, x)]
    return _prices({"logA": loga, "logB": logb, "X": x, "seed": seed,
                    "true": {"phi": phi, "h": h, "alpha": alpha, "mean": 0.0, "sd_shock": sd,
                             "sd_stationary": sd / math.sqrt(1 - phi * phi), "half_life": _half_life(phi),
                             "cointegrated": True}})


def price_pair(seed=106, n=500, h=2.0, phi=0.9, sd=0.5, alpha=0.0, common_sd=COMMON_SD, b0=50.0):
    """คู่ที่มีเชือกบน "ราคา" (ไม่ใช่ log): A = α + h·B + X · X เป็น AR(1) φ หน่วยเป็นราคา (แรงกระแทก SD sd ต่อวัน ·
    เริ่มจากการกระจายนิ่ง) · B = b0 × exp(เดินสุ่ม SD common_sd) · X ไม่ขึ้นกับ B → ถดถอย A บน B ด้วยราคา (แบบบท 1)
    ได้ความชันเท่า h จริงในค่าคาดหวัง · price-level cointegrated pair with a known hedge ratio h on prices
    ค่าเริ่มต้น: A ≈ 100 · B ≈ 50 · h 2 (คู่ A–B ของเล่ม 1) · "logA"/"logB" = None ถ้ามีราคา A ≤ 0 (โลกที่ B ตกแรงมาก)"""
    rng = random.Random(seed)
    b = [b0 * math.exp(v) for v in _rw(rng, n, common_sd)]
    x = _ar1(rng, n, phi, sd)
    a = [alpha + h * bb + e for bb, e in zip(b, x)]
    pos = min(a) > 0
    return {"A": a, "B": b, "X": x, "logA": [math.log(v) for v in a] if pos else None,
            "logB": [math.log(v) for v in b], "seed": seed,
            "true": {"h": h, "alpha": alpha, "phi": phi, "mean": 0.0, "sd_shock": sd,
                     "sd_stationary": sd / math.sqrt(1 - phi * phi) if abs(phi) < 1 else float("inf"),
                     "half_life": _half_life(phi), "cointegrated": abs(phi) < 1, "scale": "price"}}


def drifting_price_pair(seed=107, n=500, h0=2.0, h1=2.2, phi=0.9, sd=0.5, alpha=0.0, common_sd=COMMON_SD, b0=50.0):
    """คู่บน "ราคา" ที่ h ไหลเป็นเส้นตรง h0 → h1 (เล่ม 2 บท 5 · rolling h ที่รู้คำตอบ): A = α + h[t]·B + X
    price-level pair whose hedge ratio drifts linearly · สุ่มเหมือน price_pair ทุกขั้น (h0 = h1 → ได้ price_pair เดิมตรงตัว)
    true["h_path"] = h ทุกวัน · X ไม่ขึ้นกับ B · ค่าเริ่มต้น A ≈ 100 · B ≈ 50 แบบคู่ A–B ของเล่ม 1"""
    rng = random.Random(seed)
    b = [b0 * math.exp(v) for v in _rw(rng, n, common_sd)]
    x = _ar1(rng, n, phi, sd)
    hs = [h0 + (h1 - h0) * t / (n - 1) for t in range(n)] if n > 1 else [h0]
    a = [alpha + h * bb + e for h, bb, e in zip(hs, b, x)]
    return {"A": a, "B": b, "X": x, "seed": seed,
            "true": {"h_path": hs, "h0": h0, "h1": h1, "alpha": alpha, "phi": phi, "sd_shock": sd,
                     "sd_stationary": sd / math.sqrt(1 - phi * phi) if abs(phi) < 1 else float("inf"),
                     "half_life": _half_life(phi), "scale": "price"}}

def random_walk_pair(seed=102, n=500, h=1.0, alpha=math.log(2.0), sd=SPREAD_SD, common_sd=COMMON_SD, b0=math.log(50.0)):
    """คู่ที่ไม่มีเชือก: เหมือน stationary_pair แต่ระยะห่าง X เดินสุ่ม (φ = 1) — ดูเหมือนเดินด้วยกันได้ แต่ไม่กลับ
    random-walk (non-cointegrated) pair"""
    rng = random.Random(seed)
    logb = _rw(rng, n, common_sd, b0)
    x = _ar1(rng, n, 1.0, sd)
    loga = [alpha + h * b + e for b, e in zip(logb, x)]
    return _prices({"logA": loga, "logB": logb, "X": x, "seed": seed,
                    "true": {"phi": 1.0, "h": h, "alpha": alpha, "sd_shock": sd, "half_life": float("inf"),
                             "cointegrated": False}})


def drifting_h_pair(seed=103, n=500, h0=1.0, h1=1.5, phi=0.9, alpha=math.log(2.0), sd=SPREAD_SD,
                    common_sd=COMMON_SD, b0=math.log(50.0), h_walk_sd=None):
    """คู่ที่ h ไหลช้า ๆ: logA = α + b0 + h[t]·(logB − b0) + X · h เดินเป็นเส้นตรง h0 → h1 (หรือเดินสุ่ม SD h_walk_sd ต่อวัน)
    pair whose hedge ratio drifts slowly · วัด logB จากระดับอ้างอิง b0 (true["b_ref"]) เพื่อให้การไหลของ h ไม่กลายเป็น
    แนวโน้มของระดับราคา (h × log ราคาราว 4) · true["h_path"] = h ทุกวัน (ไว้วัดว่า rolling / Kalman ตามทันแค่ไหน)"""
    rng = random.Random(seed)
    logb = _rw(rng, n, common_sd, b0)
    x = _ar1(rng, n, phi, sd)
    if h_walk_sd:
        hs = _rw(rng, n, h_walk_sd, h0)
    else:
        hs = [h0 + (h1 - h0) * t / (n - 1) for t in range(n)]
    loga = [alpha + b0 + h * (b - b0) + e for h, b, e in zip(hs, logb, x)]
    return _prices({"logA": loga, "logB": logb, "X": x, "seed": seed,
                    "true": {"phi": phi, "h_path": hs, "h0": hs[0], "h1": hs[-1], "alpha": alpha, "b_ref": b0, "sd_shock": sd,
                             "half_life": _half_life(phi)}})


def broken_pair(seed=104, n=500, break_at=300, phi_before=0.9, phi_after=1.0, jump=0.0, h=1.0,
                alpha=math.log(2.0), sd=SPREAD_SD, common_sd=COMMON_SD, b0=math.log(50.0)):
    """คู่ที่เชือกขาด: ก่อนวัน break_at ระยะห่างเป็น AR(1) φ_before · ตั้งแต่ break_at เป็น AR(1) φ_after
    (ค่าเริ่มต้น 1 = เดินสุ่ม) รอบค่ากลางใหม่ jump · pair whose rope breaks at a known date (index เริ่ม 0)"""
    if not 0 < break_at < n:
        raise ValueError("break_at ต้องอยู่ใน (0, n)")
    rng = random.Random(seed)
    logb = _rw(rng, n, common_sd, b0)
    x = _ar1(rng, break_at, phi_before, sd)
    v = x[-1] - jump
    for _ in range(n - break_at):
        v = phi_after * v + rng.gauss(0.0, sd)
        x.append(v + jump)
    loga = [alpha + h * b + e for b, e in zip(logb, x)]
    return _prices({"logA": loga, "logB": logb, "X": x, "seed": seed,
                    "true": {"break_at": break_at, "phi_before": phi_before, "phi_after": phi_after, "jump": jump,
                             "h": h, "alpha": alpha, "sd_shock": sd, "half_life_before": _half_life(phi_before)}})


def threshold_pair(seed=108, n=500, band=1.0, phi_out=0.8, phi_in=1.0, sd=0.5, h=2.0, alpha=0.0,
                   common_sd=COMMON_SD, b0=50.0):
    """คู่บน "ราคา" ที่เชือกดึงเฉพาะนอกกรอบ (Threshold Model · เล่ม 2 บท 7): A = α + h·B + X
    X[t] = φ_in·X[t−1] + e เมื่อ |X[t−1]| ≤ band (ค่าเริ่มต้น φ_in 1 = ในกรอบเดินสุ่ม ไม่มีแรงดึง) ·
    X[t] = φ_out·X[t−1] + e เมื่อ |X[t−1]| > band · X เริ่มที่ 0 · B แบบ price_pair · threshold (band) pair with known band"""
    rng = random.Random(seed)
    b = [b0 * math.exp(v) for v in _rw(rng, n, common_sd)]
    x, xs = 0.0, []
    for _ in range(n):
        x = (phi_in if abs(x) <= band else phi_out) * x + rng.gauss(0.0, sd)
        xs.append(x)
    a = [alpha + h * bb + e for bb, e in zip(b, xs)]
    return {"A": a, "B": b, "X": xs, "seed": seed,
            "true": {"h": h, "alpha": alpha, "band": band, "phi_in": phi_in, "phi_out": phi_out, "sd_shock": sd,
                     "scale": "price"}}


def regime_pair(seed=109, n=500, phis=(0.9, 0.9), mus=(0.0, 1.0), stays=(0.995, 0.99), sd=0.5, h=2.0, alpha=0.0,
                common_sd=COMMON_SD, b0=50.0):
    """คู่บน "ราคา" ที่สลับสองสภาวะ (Regime Switching · เล่ม 2 บท 7): สภาวะ s ∈ {0, 1} เปลี่ยนแบบสุ่มทุกวัน
    (อยู่สภาวะเดิมด้วยโอกาส stays[s]) · X = mus[s] + u · u[t] = phis[s]·u[t−1] + e (เริ่มสภาวะ 0 · u จากการกระจายนิ่ง
    ของสภาวะ 0) · A = α + h·B + X · true["state"] = สภาวะทุกวัน · two-state Markov-switching pair (mean and/or φ)"""
    rng = random.Random(seed)
    b = [b0 * math.exp(v) for v in _rw(rng, n, common_sd)]
    s = 0
    u = rng.gauss(0.0, sd / math.sqrt(1 - phis[0] ** 2)) if abs(phis[0]) < 1 else 0.0
    xs, st = [], []
    for _ in range(n):
        if rng.random() > stays[s]:
            s = 1 - s
        u = phis[s] * u + rng.gauss(0.0, sd)
        xs.append(mus[s] + u)
        st.append(s)
    a = [alpha + h * bb + e for bb, e in zip(b, xs)]
    return {"A": a, "B": b, "X": xs, "seed": seed,
            "true": {"h": h, "alpha": alpha, "phis": list(phis), "mus": list(mus), "stays": list(stays), "sd_shock": sd,
                     "state": st, "scale": "price"}}


def factor_basket(seed=105, n=500, n_coins=5, betas=None, phis=None, idio_sd=0.02, factor_sd=COMMON_SD,
                  levels=None):
    """N เหรียญที่มีแรงร่วมหนึ่งตัว: logP_i = a_i + β_i·F[t] + u_i[t] · F เดินสุ่ม · u_i เป็น AR(1) φ_i (กลับค่ากลาง)
    group of coins = common factor + idiosyncratic mean-reverting parts · คืน "logP" / "P" (list ต่อเหรียญ) · "F" ·
    "U" (ส่วนเฉพาะจริง) · true: betas · phis · half_lives · idio_sd · factor_sd"""
    rng = random.Random(seed)
    betas = list(betas) if betas is not None else [round(0.6 + 0.8 * i / max(1, n_coins - 1), 3) for i in range(n_coins)]
    phis = list(phis) if phis is not None else [round(0.85 + 0.12 * i / max(1, n_coins - 1), 3) for i in range(n_coins)]
    levels = list(levels) if levels is not None else [math.log(10.0 * (i + 1)) for i in range(n_coins)]
    if not len(betas) == len(phis) == len(levels) == n_coins:
        raise ValueError("betas / phis / levels ต้องยาวเท่า n_coins")
    f = _rw(rng, n, factor_sd)
    us = [_ar1(rng, n, p, idio_sd) for p in phis]
    logp = [[a + b * ft + ut for ft, ut in zip(f, u)] for a, b, u in zip(levels, betas, us)]
    return {"logP": logp, "P": [[math.exp(v) for v in s] for s in logp], "F": f, "U": us, "seed": seed,
            "true": {"betas": betas, "phis": phis, "levels": levels, "half_lives": [_half_life(p) for p in phis],
                     "idio_sd": idio_sd, "factor_sd": factor_sd}}


def reseed(world, stat, seeds=None, example_seed=None, **kw):
    """รัน world(seed=s, **kw) ทุก seed แล้ววัด stat(ผลของโลก) → ช่วงของค่า (แบบ seed_robustness ของเล่ม 1)
    30-reseed helper: คืน values · min · median · max · example (ค่าที่ seed ตัวอย่าง = example_seed หรือ seed แรก)"""
    seeds = list(seeds or ROBUST_SEEDS)
    vals = [stat(world(seed=s, **kw)) for s in seeds]
    ex = example_seed if example_seed is not None else seeds[0]
    example = vals[seeds.index(ex)] if ex in seeds else stat(world(seed=ex, **kw))
    return {"seeds": seeds, "values": vals, "min": min(vals), "median": statistics.median(vals), "max": max(vals),
            "example": example}


# ═══════════════════════════ selftest ═══════════════════════════


def selftest():
    sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
    import sab2_stats as S
    ok, n = True, 0

    def check(label, cond, detail=""):
        nonlocal ok, n
        n += 1
        if not cond:
            ok = False
            print(f"  ✗ {label} {detail}")

    # ทำซ้ำได้ · seed ต่างได้ผลต่าง · ความยาวถูก
    a1, a2, a3 = stationary_pair(seed=1), stationary_pair(seed=1), stationary_pair(seed=2)
    check("seed เดิม = ผลเดิม · seed ใหม่ = ผลใหม่", a1["logA"] == a2["logA"] and a1["logA"] != a3["logA"])
    check("ความยาว · ราคา = exp(log)", len(a1["A"]) == 500 and abs(a1["A"][7] - math.exp(a1["logA"][7])) < 1e-12)
    check("ระดับราคาเริ่มต้นใกล้ A 100 / B 50", 80 < a1["A"][0] < 125 and 40 < a1["B"][0] < 62)
    # stationary: ประมาณค่ากลับมาได้ (ข้อมูลยาว)
    w = stationary_pair(seed=11, n=5000, phi=0.95)
    eg = S.engle_granger(w["logA"], w["logB"])
    f = S.ar1(w["X"])
    check("stationary: h ≈ 1 · φ ≈ 0.95 · EG ปฏิเสธ", abs(eg["h"] - 1.0) < 0.02 and abs(f["phi"] - 0.95) < 0.01
          and eg["reject5"], f"h={eg['h']:.3f} φ={f['phi']:.3f}")
    check("stationary: SD นิ่งตรงทฤษฎี (±10%)", abs(S.sd(w["X"]) / w["true"]["sd_stationary"] - 1) < 0.10)
    # random walk: EG ปฏิเสธไม่บ่อย (30 seed · ≤ 4 ครั้ง ≈ ขนาด 5% + ความคลาดสุ่ม)
    rr = reseed(random_walk_pair, lambda d: S.engle_granger(d["logA"], d["logB"])["reject5"], n=500)
    check("random walk: EG ปฏิเสธ ≤ 4/30", sum(rr["values"]) <= 4, f"{sum(rr['values'])}/30")
    rs = reseed(stationary_pair, lambda d: S.engle_granger(d["logA"], d["logB"])["reject5"], n=500, phi=0.9)
    check("stationary φ 0.9: EG ปฏิเสธ ≥ 27/30", sum(rs["values"]) >= 27, f"{sum(rs['values'])}/30")
    # reseed: φ ประมาณจาก 60 วันต่ำกว่าจริงในมัธยฐาน (ความเอนเอียงของข้อมูลสั้น ต่อจากบท 13 เล่ม 1)
    short = reseed(stationary_pair, lambda d: S.ar1(d["X"])["phi"], n=60, phi=0.95)
    check("reseed: ช่วง min ≤ มัธยฐาน ≤ max · 30 ค่า", len(short["values"]) == 30
          and short["min"] <= short["median"] <= short["max"] and short["example"] == short["values"][0])
    check("φ จาก 60 วัน: มัธยฐานต่ำกว่า 0.95", short["median"] < 0.95, f"{short['median']:.3f}")
    # drifting h: rolling h ปลายทาง ≈ h1 · ต้นทาง ≈ h0
    d = drifting_h_pair(seed=13, n=1000, h0=1.0, h1=1.5)
    check("drifting h: path เส้นตรง 1.0 → 1.5", d["true"]["h_path"][0] == 1.0 and abs(d["true"]["h_path"][-1] - 1.5) < 1e-12)

    def h_end(dd, w=250):                      # h จากหน้าต่าง 250 วันสุดท้าย − ค่าจริงเฉลี่ยของหน้าต่างเดียวกัน
        return S.ols(dd["logB"][-w:], dd["logA"][-w:])["slope"] - S.mean(dd["true"]["h_path"][-w:])
    he = reseed(drifting_h_pair, h_end, n=1000)
    hs0 = reseed(drifting_h_pair, lambda dd: S.ols(dd["logB"], dd["logA"])["slope"] - dd["true"]["h_path"][-1], n=1000)
    check("drifting h: h หน้าต่างท้ายตามทัน (มัธยฐานคลาด ≤ 0.1) แต่ h ทั้งช่วงล้าหลังค่าล่าสุด",
          abs(he["median"]) <= 0.1 and hs0["median"] < -0.1, f"{he['median']:.3f} / {hs0['median']:.3f}")
    dw = drifting_h_pair(seed=13, n=300, h_walk_sd=0.01)
    check("drifting h แบบเดินสุ่ม: h0 = 1 + ก้าวแรก", abs(dw["true"]["h_path"][0] - 1.0) < 0.05)
    # broken: ก่อนขาด ADF ปฏิเสธ · หลังขาด φ ใกล้ 1
    b = broken_pair(seed=14, n=1200, break_at=600, phi_before=0.85)
    pre, post = b["X"][:600], b["X"][600:]
    check("broken: ก่อนขาดมีเชือก · หลังขาด φ > 0.97", S.adf(pre)["reject5"] and S.ar1(post)["phi"] > 0.97,
          f"φ หลัง = {S.ar1(post)['phi']:.3f}")
    bj = broken_pair(seed=15, n=800, break_at=400, phi_before=0.8, phi_after=0.8, jump=0.3)
    check("broken แบบค่ากลางกระโดด: ค่าเฉลี่ยหลัง − ก่อน ≈ 0.3 (±0.08)",
          abs(S.mean(bj["X"][420:]) - S.mean(bj["X"][:400]) - 0.3) < 0.08)
    # threshold: ในกรอบเดินสุ่ม นอกกรอบถูกดึง · X = A − hB · regime: สภาวะสลับ ค่ากลางตามสภาวะ
    th = threshold_pair(seed=17, n=20000, band=1.5, sd=0.4, common_sd=0.0)
    xin = [(x0, x1) for x0, x1 in zip(th["X"], th["X"][1:]) if abs(x0) <= 1.5]
    xout = [(x0, x1) for x0, x1 in zip(th["X"], th["X"][1:]) if abs(x0) > 1.5]
    fin = S.ols_origin([p for p, _ in xin], [q for _, q in xin])["slope"]
    fout = S.ols_origin([p for p, _ in xout], [q for _, q in xout])["slope"]
    check("threshold: φ ในกรอบ ≈ 1 · นอกกรอบ ≈ 0.8 · X = A − 2B",
          abs(fin - 1.0) < 0.03 and abs(fout - 0.8) < 0.03
          and max(abs(a - 2.0 * b - x) for a, b, x in zip(th["A"], th["B"], th["X"])) < 1e-9, f"{fin:.3f} / {fout:.3f}")
    rg = regime_pair(seed=18, n=20000, phis=(0.9, 0.9), mus=(0.0, 3.0), stays=(0.99, 0.98), sd=0.4, common_sd=0.0)
    s1 = [x for x, k in zip(rg["X"], rg["true"]["state"]) if k == 1]
    s0 = [x for x, k in zip(rg["X"], rg["true"]["state"]) if k == 0]
    frac = len(s1) / len(rg["X"])
    check("regime: สัดส่วนสภาวะ 1 ≈ 1/3 · ค่ากลางสองสภาวะห่างราว 3", 0.25 < frac < 0.42
          and 2.4 < S.mean(s1) - S.mean(s0) < 3.3, f"{frac:.2f} {S.mean(s1) - S.mean(s0):.2f}")
    # factor basket: β จากการถดถอยบน F · PCA ตัวแรกชี้ทิศ β · ส่วนเฉพาะกลับค่ากลาง
    fb = factor_basket(seed=16, n=3000, n_coins=5)
    bh = [S.ols(fb["F"], s)["slope"] for s in fb["logP"]]
    check("factor: β ประมาณได้ (±0.05)", all(abs(u - v) < 0.05 for u, v in zip(bh, fb["true"]["betas"])),
          f"{[round(u, 3) for u in bh]}")
    rets = [S.diff(s) for s in fb["logP"]]
    p = S.pca(rets)
    bt = fb["true"]["betas"]
    cosang = abs(sum(u * v for u, v in zip(p["vectors"][0], bt))) / math.sqrt(sum(u * u for u in bt))
    check("factor: PC1 ขนานกับ β (cos > 0.98) · อธิบาย > 50%", cosang > 0.98 and p["explained"][0] > 0.5,
          f"cos={cosang:.4f} exp={p['explained'][0]:.3f}")
    resid_phi = [S.ar1(S.ols(fb["F"], s)["residuals"])["phi"] for s in fb["logP"]]
    check("factor: φ ของส่วนเหลือ ≈ φ จริง (±0.03)", all(abs(u - v) < 0.03 for u, v in zip(resid_phi, fb["true"]["phis"])),
          f"{[round(u, 3) for u in resid_phi]}")
    try:
        factor_basket(n_coins=3, betas=[1, 2])
        check("factor: ความยาวไม่ตรง → ValueError", False)
    except ValueError:
        check("factor: ความยาวไม่ตรง → ValueError", True)
    # drifting_price_pair: h0 = h1 → เท่า price_pair ตรงตัว · h ไหล → X = A − α − h[t]·B
    dq, pq0 = drifting_price_pair(seed=7, h0=2.0, h1=2.0), price_pair(seed=7)
    dr = drifting_price_pair(seed=7, h0=2.0, h1=2.4)
    check("drifting_price_pair: h คงที่ = price_pair · h ไหล 2 → 2.4 · X = A − h[t]B",
          dq["A"] == pq0["A"] and dq["B"] == pq0["B"] and abs(dr["true"]["h_path"][-1] - 2.4) < 1e-12
          and max(abs(a - h * b - x) for a, b, x, h in zip(dr["A"], dr["B"], dr["X"], dr["true"]["h_path"])) < 1e-9)
    # price_pair: h บนระดับราคา · ถดถอย A บน B (ราคา) ได้ h ในค่าคาดหวัง · X = A − α − h·B ตรงตัว
    pp, pp2 = price_pair(seed=7), price_pair(seed=7)
    check("price_pair: seed เดิม = ผลเดิม · X = A − α − hB · A ≈ 100 / B ≈ 50",
          pp["A"] == pp2["A"] and max(abs(a - 2.0 * b - x) for a, b, x in zip(pp["A"], pp["B"], pp["X"])) < 1e-9
          and 80 < pp["A"][0] < 125 and 40 < pp["B"][0] < 62 and pp["true"]["scale"] == "price")
    hp = reseed(price_pair, lambda d: S.ols(d["B"], d["A"])["slope"] - d["true"]["h"], n=250)
    hp_mean = S.mean(hp["values"])
    check("price_pair: h จากถดถอยราคา 250 วัน · 30 seed: ค่าเฉลี่ยคลาด ≤ 0.02 · มัธยฐานคลาด ≤ 0.02",
          abs(hp_mean) <= 0.02 and abs(hp["median"]) <= 0.02, f"mean={hp_mean:.4f} med={hp['median']:.4f}")
    big = [S.ols(price_pair(seed=s, n=250)["B"], price_pair(seed=s, n=250)["A"])["slope"] - 2.0 for s in range(1, 401)]
    se_big = S.sd(big) / math.sqrt(len(big))
    check("price_pair: 400 seed ค่าเฉลี่ยคลาดอยู่ในสาม SE ของศูนย์ (ไม่เอนเอียง)", abs(S.mean(big)) <= 3 * se_big,
          f"{S.mean(big):.5f} ± {se_big:.5f}")
    pl = price_pair(seed=8, n=5000, h=1.5, alpha=10.0)
    ol = S.ols(pl["B"], pl["A"])
    check("price_pair: 5000 วัน h 1.5 α 10 กลับมาได้ (±0.01 · ±1) · φ ของ X ≈ 0.9 · EG บนราคาปฏิเสธ",
          abs(ol["slope"] - 1.5) < 0.01 and abs(ol["intercept"] - 10.0) < 1.0 and abs(S.ar1(pl["X"])["phi"] - 0.9) < 0.02
          and S.engle_granger(pl["A"], pl["B"])["reject5"], f"h={ol['slope']:.4f} a={ol['intercept']:.3f}")
    lg = reseed(price_pair, lambda d: S.ols(d["logB"], d["logA"])["slope"], n=250)
    check("price_pair: ถดถอยบน log ให้ความชันราว 1 ไม่ใช่ h 2 (h ราคาต่างจาก h log)", 0.8 < lg["median"] < 1.2,
          f"{lg['median']:.3f}")
    print("selftest", f"ผ่าน ✓ ({n} ข้อ · ทำซ้ำได้ด้วย seed · stationary / ราคา (price_pair) / random walk / h ไหล / เชือกขาด / เชือกมีกรอบ / สลับสภาวะ / ตะกร้าแรงร่วม "
          "ประมาณพารามิเตอร์จริงกลับมาได้ · reseed 30 ชุด)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)
