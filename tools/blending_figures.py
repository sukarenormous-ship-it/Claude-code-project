#!/usr/bin/env python3
"""สร้าง docs/blending-figures.json — ตัวเลขของบท "การรวมสัญญาณโดยไม่ overfit"

ใช้เครื่องจักรเดียวกับ nq_figures.py::_search_study (Part 8):
ลองรวมตัวกรอง 4 ตัวทุกแบบที่เป็นไปได้ วัดว่าวิธีที่ดีที่สุด "ดีขึ้น" เท่าไรจากตัวเดียว
แล้วรันการค้นหาชุดเดียวกันซ้ำบน "ป้ายกำกับที่สลับสุ่มแล้ว" (ไม่มีความสัมพันธ์จริง)
เพื่อวัดว่าการค้นหาล้วน ๆ สร้างผลงานปลอมได้กี่จุด

ตัวกรองสี่ตัว (บน BTC/ETH):
  z      สเปรด cointegration ยืดออกมาก (|z| > 1.5 — เกณฑ์เดียวกับบท copula)
  mi     Mispricing Index จาก copula ยืดออกมาก (|MI| > 0.35 — เกณฑ์เดียวกับบท copula)
  regime ตลาดอยู่ในช่วงนิ่ง (ผันผวน 5 วันย้อนหลัง ต่ำกว่ามัธยฐาน)
  cost   ต้นทุนเทรดถูก (ส่วนต่าง bid-ask ของ option ใกล้ ATM ต่ำกว่ามัธยฐาน)

ป้ายกำกับ (label): สเปรดวันถัดไป "ลู่เข้า" จริงไหม — |z[t+1]| < |z[t]|

ต้องมี numpy + scipy:  pip install numpy scipy
    python3 tools/blending_figures.py
"""

import csv
import glob
import json
import math
import os
import statistics
import sys

import numpy as np
from scipy import optimize, stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "blending-figures.json")
DATA_DIR = os.environ.get(
    "NQ_DATA_DIR",
    os.path.join(ROOT, "data") if os.path.isdir(os.path.join(ROOT, "data"))
    else os.path.join(ROOT, "..", "options-data", "data"),
)
SEED = 20260830
Z_TH, MI_TH = 1.5, 0.35
MIN_FIRED = 5          # ต้องมีวันกระตุ้นอย่างน้อยเท่านี้ ไม่งั้นถือว่าอ่านค่าไม่ได้
NOISE_ROUNDS = 300


# ── ข้อมูลดิบ ─────────────────────────────────────────────────────────────
def daily_prices():
    per = {}
    for coin in ("BTC", "ETH"):
        per[coin] = {}
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*", "*", "*", "*.csv"))):
        day = os.path.basename(path)[:-4]
        buckets = {"BTC": [], "ETH": []}
        with open(path) as fh:
            for row in csv.DictReader(fh):
                sym = row.get("underlying")
                if sym in buckets and row.get("underlying_price"):
                    buckets[sym].append(float(row["underlying_price"]))
        for sym, vals in buckets.items():
            if vals and day not in per[sym]:
                per[sym][day] = statistics.median(vals)
    return per


def daily_atm_spread():
    """ส่วนต่าง bid-ask กลาง (%) ของ option BTC ใกล้ ATM (±5%) ในแต่ละวัน ไม่จำกัด expiry"""
    out = {}
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "deribit", "*", "*", "*.csv"))):
        day = os.path.basename(path)[:-4]
        spreads = []
        with open(path) as fh:
            for row in csv.DictReader(fh):
                if row.get("underlying") != "BTC":
                    continue
                try:
                    bid, ask = float(row["bid"]), float(row["ask"])
                    spot, strike = float(row["underlying_price"]), float(row["strike"])
                except (ValueError, KeyError):
                    continue
                if bid <= 0 or ask <= 0 or abs(strike / spot - 1) > 0.05:
                    continue
                spreads.append(100 * (ask - bid) / ((ask + bid) / 2))
        if spreads:
            out[day] = statistics.median(spreads)
    return out


# ── z (cointegration) และ MI (copula) — วิธีเดียวกับ statarb-copula-practice ──
def _ll_gaussian(rho, u, v):
    if abs(rho) >= 0.999:
        return -1e9
    x, y = stats.norm.ppf(u), stats.norm.ppf(v)
    return float(np.sum(-0.5 * np.log(1 - rho ** 2)
                        - (rho ** 2 * (x ** 2 + y ** 2) - 2 * rho * x * y) / (2 * (1 - rho ** 2))))


def compute_signals(days, b, e):
    rb, re = np.diff(np.log(b)), np.diff(np.log(e))
    n = len(rb)
    lb, le = np.cumsum(rb), np.cumsum(re)
    beta = float(np.polyfit(lb, le, 1)[0])
    spread = le - beta * lb
    z = (spread - spread.mean()) / spread.std(ddof=1)

    u = stats.rankdata(rb) / (n + 1)
    v = stats.rankdata(re) / (n + 1)
    r = optimize.minimize_scalar(lambda x: -_ll_gaussian(x, u, v), bounds=(-0.98, 0.98), method="bounded")
    rho = float(r.x)
    x, y = stats.norm.ppf(u), stats.norm.ppf(v)
    mi = stats.norm.cdf((y - rho * x) / math.sqrt(1 - rho ** 2)) - 0.5

    return rb, z, mi, beta, rho


# ── การรวมตัวกรอง ────────────────────────────────────────────────────────
NAMES = ["z", "mi", "regime", "cost"]


def all_combos():
    """คืนลิสต์ (คำอธิบาย, ฟังก์ชันรวม) — AND ทุกเซตย่อย · OR ทุกเซตย่อย · vote-k · ถ่วงน้ำหนัก"""
    combos = []
    idx = list(range(4))
    subsets = []
    for m in range(1, 16):
        s = [i for i in idx if m & (1 << i)]
        subsets.append(s)

    for s in subsets:
        label = "และ".join(NAMES[i] for i in s)
        combos.append((f"AND({label})", ("and", tuple(s))))
    for s in subsets:
        label = "หรือ".join(NAMES[i] for i in s)
        combos.append((f"OR({label})", ("or", tuple(s))))
    for k in range(1, 5):
        combos.append((f"vote>={k}/4", ("vote", k)))
    weights = []
    for w0 in (0, 1, 2):
        for w1 in (0, 1, 2):
            for w2 in (0, 1, 2):
                for w3 in (0, 1, 2):
                    if w0 + w1 + w2 + w3 == 0:
                        continue
                    weights.append((w0, w1, w2, w3))
    for w in weights:
        combos.append((f"weight{w}", ("weight", w)))
    return combos


def fire(kind_arg, F):
    kind, arg = kind_arg
    n = len(F[0])
    if kind == "and":
        out = np.ones(n, dtype=bool)
        for i in arg:
            out &= F[i]
        return out
    if kind == "or":
        out = np.zeros(n, dtype=bool)
        for i in arg:
            out |= F[i]
        return out
    if kind == "vote":
        total = np.sum([F[i].astype(int) for i in range(4)], axis=0)
        return total >= arg
    if kind == "weight":
        score = np.sum([arg[i] * F[i].astype(int) for i in range(4)], axis=0)
        return score >= max(1, sum(arg) / 2)
    raise ValueError(kind)


def search_best(F, label, min_fired=MIN_FIRED, combos=None):
    combos = combos or all_combos()
    base = float(np.mean(label))
    best = None
    tried_enough = 0
    for name, spec in combos:
        fired = fire(spec, F)
        nf = int(np.sum(fired))
        if nf < min_fired:
            continue
        tried_enough += 1
        hr = float(np.mean(label[fired]))
        lift = hr - base
        if best is None or lift > best["ค่ายกเปอร์เซ็นต์"]:
            best = {"ชื่อวิธี": name, "จำนวนวันกระตุ้น": nf,
                    "อัตราสำเร็จเปอร์เซ็นต์": round(100 * hr, 1),
                    "ค่ายกเปอร์เซ็นต์": round(100 * lift, 1)}
    return best, tried_enough, len(combos), base


def build():
    per = daily_prices()
    days = sorted(set(per["BTC"]) & set(per["ETH"]))
    b = np.array([per["BTC"][d] for d in days])
    e = np.array([per["ETH"][d] for d in days])
    rb, z, mi, beta, rho = compute_signals(days, b, e)
    n = len(rb)                                   # จำนวนวันผลตอบแทน (index 0..n-1 ตรงกับ days[1:])
    ret_days = days[1:]                            # วันที่ที่ rb/z/mi แต่ละตัวสังกัด

    # regime: ผันผวน 5 วันย้อนหลังของ BTC เทียบมัธยฐานของตัวมันเอง (ใช้ได้ตั้งแต่ index 5)
    vol5 = np.full(n, np.nan)
    for t in range(5, n):
        vol5[t] = float(np.std(rb[t - 5:t], ddof=1))
    vol_median = float(np.nanmedian(vol5))
    regime_calm = vol5 <= vol_median

    # cost: ส่วนต่าง bid-ask ATM ของวันนั้น เทียบมัธยฐานของทุกวันที่มีข้อมูล
    spread_by_day = daily_atm_spread()
    spreads = np.array([spread_by_day.get(d, np.nan) for d in ret_days])
    spread_median = float(np.nanmedian(spreads[~np.isnan(spreads)]))
    cost_cheap = spreads <= spread_median

    # ป้ายกำกับ: สเปรดวันถัดไปลู่เข้าจริงไหม (ใช้ได้ถึง index n-2 เพราะต้องมี t+1)
    converge = np.full(n, False)
    converge[:-1] = np.abs(z[1:]) < np.abs(z[:-1])

    z_fire = np.abs(z) > Z_TH
    mi_fire = np.abs(mi) > MI_TH

    # ตัดให้เหลือเฉพาะ index ที่ทุกอย่างพร้อมใช้: มี regime (>=5), มี cost (ไม่ nan), มี label (< n-1)
    usable = np.array([
        t for t in range(n - 1)
        if not np.isnan(vol5[t]) and not np.isnan(spreads[t])
    ])

    F = [z_fire[usable], mi_fire[usable], regime_calm[usable], cost_cheap[usable]]
    label = converge[usable]
    n_use = len(usable)
    base_rate = float(np.mean(label))

    combos = all_combos()
    best_combo, tried_enough, total_combos, _ = search_best(F, label, combos=combos)

    single_only = [(f"{NAMES[i]}เดี่ยว", ("and", (i,))) for i in range(4)]
    # กับดัก: ถ้าไม่บังคับขั้นต่ำวันกระตุ้น ตัวกรองที่กระตุ้นน้อยครั้งจะดูเทพเกินจริง (โชคของตัวอย่างเล็ก)
    best_single_unconstrained, _, _, _ = search_best(F, label, min_fired=1, combos=single_only)
    # ตัวเปรียบเทียบที่เป็นธรรม: บังคับขั้นต่ำเดียวกับที่ใช้กรองชุดรวม (≥5 วัน)
    best_single, _, _, _ = search_best(F, label, min_fired=MIN_FIRED, combos=single_only)

    # ── การค้นหาบนป้ายกำกับที่ไม่มีความสัมพันธ์จริง (สลับสุ่ม) ──────────────
    rng = np.random.default_rng(SEED + 41)
    noise_best_lifts, noise_single_lifts = [], []
    for _ in range(NOISE_ROUNDS):
        shuffled = rng.permutation(label)
        b_noise, _, _, base_n = search_best(F, shuffled, combos=combos)
        s_noise, _, _, _ = search_best(F, shuffled, min_fired=1, combos=single_only)
        noise_best_lifts.append(b_noise["ค่ายกเปอร์เซ็นต์"] if b_noise else 0.0)
        noise_single_lifts.append(s_noise["ค่ายกเปอร์เซ็นต์"] if s_noise else 0.0)
    noise_best_lifts.sort()
    pct = 100 * sum(1 for x in noise_best_lifts if x <= best_combo["ค่ายกเปอร์เซ็นต์"]) / NOISE_ROUNDS

    # งบ degrees of freedom แบบกฎนิ้วโป้ง (ต้องระบุว่าเป็น heuristic ไม่ใช่กฎตายตัว)
    dof_table = [{"จำนวนตัวอย่าง": n_use, "กฎนิ้วโป้ง": rule,
                  "จำนวนพารามิเตอร์ที่รองรับได้": max(1, n_use // per_param)}
                 for rule, per_param in [("10 ตัวอย่างต่อพารามิเตอร์", 10),
                                          ("20 ตัวอย่างต่อพารามิเตอร์ (อนุรักษ์นิยม)", 20)]]
    weighting_params = 4    # น้ำหนัก 4 ตัว (ก่อนหาร threshold)

    return {
        "_อ่านก่อน": "สร้างด้วย tools/blending_figures.py — ห้ามแก้ด้วยมือ",
        "ข้อมูล": {"คู่": "BTC / ETH", "ตั้งแต่": ret_days[0], "ถึง": ret_days[-1],
                   "จำนวนวันผลตอบแทนทั้งหมด": n,
                   "จำนวนวันที่ใช้วิเคราะห์ได้จริง": n_use,
                   "หมายเหตุ": "ตัดวันที่ไม่มีค่า regime (5 วันแรก) หรือไม่มีราคาเสนอ option ATM ออก"},
        "ตัวกรอง": {
            "z": {"เกณฑ์": Z_TH, "จำนวนวันกระตุ้น": int(np.sum(F[0]))},
            "mi": {"เกณฑ์": MI_TH, "จำนวนวันกระตุ้น": int(np.sum(F[1]))},
            "regime": {"เกณฑ์": "ผันผวน 5 วันย้อนหลัง ≤ มัธยฐาน", "มัธยฐานเปอร์เซ็นต์": round(vol_median * 100, 2),
                       "จำนวนวันกระตุ้น": int(np.sum(F[2]))},
            "cost": {"เกณฑ์": "ส่วนต่าง ATM ≤ มัธยฐาน", "มัธยฐานเปอร์เซ็นต์": round(spread_median, 1),
                     "จำนวนวันกระตุ้น": int(np.sum(F[3]))},
        },
        "ป้ายกำกับ": {"คำอธิบาย": "|z วันถัดไป| < |z วันนี้| (สเปรดลู่เข้า)",
                      "อัตราฐานเปอร์เซ็นต์": round(100 * base_rate, 1)},
        "การค้นหา": {
            "จำนวนวิธีรวมทั้งหมด": total_combos,
            "จำนวนวิธีที่มีวันกระตุ้นพอ(≥5วัน)": tried_enough,
            "ตัวกรองเดี่ยวที่ดีที่สุดแบบไม่จำกัดวันกระตุ้น_กับดัก": best_single_unconstrained,
            "ตัวกรองเดี่ยวที่ดีที่สุดที่วันกระตุ้นพอ": best_single,
            "ชุดรวมที่ดีที่สุด": best_combo,
            "ส่วนที่การรวมสร้างขึ้นจุดเปอร์เซ็นต์": round(
                best_combo["ค่ายกเปอร์เซ็นต์"] - (best_single["ค่ายกเปอร์เซ็นต์"] if best_single else 0.0), 1),
        },
        "ความไม่มีโครงสร้าง": {
            "จำนวนรอบสลับสุ่ม": NOISE_ROUNDS,
            "ค่ายกที่ดีที่สุดกลางเปอร์เซ็นต์": round(statistics.median(noise_best_lifts), 1),
            "ค่ายกที่ดีที่สุดช่วง90เปอร์เซ็นต์": [round(noise_best_lifts[NOISE_ROUNDS // 20], 1),
                                                    round(noise_best_lifts[NOISE_ROUNDS - NOISE_ROUNDS // 20 - 1], 1)],
            "ค่ายกตัวเดียวกลางเปอร์เซ็นต์": round(statistics.median(noise_single_lifts), 1),
            "เปอร์เซ็นไทล์ของผลจริงเทียบสุ่ม": round(pct),
        },
        "งบdegreesOfFreedom": {
            "ตาราง": dof_table,
            "จำนวนพารามิเตอร์ของวิธีถ่วงน้ำหนัก": weighting_params,
            "หมายเหตุ": "กฎนิ้วโป้งนี้เป็น heuristic ที่ใช้กันทั่วไป ไม่ใช่กฎทางสถิติตายตัว "
                       "n ที่แท้จริงในบทนี้เล็กมาก (57 วัน) ตาราง degrees-of-freedom จึงเป็นเพดานเชิงทฤษฎี "
                       "ไม่ใช่การยืนยันว่าผลลัพธ์ 'ปลอดภัย' จาก overfitting",
        },
        "ความสัมพันธ์cointegrationกับcopula": {"beta": round(beta, 3), "rhoGaussian": round(rho, 3)},
    }


if __name__ == "__main__":
    _args = sys.argv[1:]
    if "--data-dir" in _args:
        _i = _args.index("--data-dir")
        DATA_DIR = _args[_i + 1]
    if not os.path.isdir(DATA_DIR):
        sys.exit(f"ไม่พบโฟลเดอร์ข้อมูล: {DATA_DIR}\n"
                 f"ระบุตำแหน่งด้วย --data-dir <path> หรือตัวแปรแวดล้อม NQ_DATA_DIR "
                 f"(ต้องมี deribit/ และ okx/ อยู่ข้างใน)")
    with open(OUT, "w") as fh:
        json.dump(build(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("เขียน", os.path.relpath(OUT, ROOT))
