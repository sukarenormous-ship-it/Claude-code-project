#!/usr/bin/env python3
"""สร้าง docs/ic-figures.json — ตัวเลขของบท "IC: สัญญาณนี้ทำนายอะไรได้จริงไหม"

ตอบคำถามของหลักสูตร Part XIII (Alpha Discovery) แบบเดินเลข:
วัด Information Coefficient (IC) ของอินดิเคเตอร์จริงบนราคา BTC ในคลัง แล้วเทียบกับ
"ฐานจากความสุ่ม" ที่ได้จากการสลับป้ายกำกับ — เพื่อแยก "สัญญาณที่ทำนายได้" ออกจาก
"ตัวเลขที่สวยเพราะตัวอย่างน้อยและเพราะเราเลือกตัวที่ดีที่สุด"

อินพุตคือราคารายวัน BTC ชุดเดียวกับทุกบท (docs/nq-figures.json → "ราคารายวัน")
จึงรันซ้ำได้ผลเดิมเสมอ ไม่ต้องพึ่งข้อมูลดิบภายนอก

ข้อจำกัดที่บทต้องพูดตรง ๆ:
  - 57 วัน = ตัวอย่างน้อยมาก · SE ของ IC ≈ 1/√(n−1) จึงกว้างกว่า IC ที่วัดได้เกือบทุกตัว
  - ผลตอบแทนล่วงหน้าที่ horizon > 1 วันซ้อนทับกัน (overlapping) ทำให้ t-stat ดูใหญ่เกินจริง
  - สินทรัพย์เดียว = IC แบบอนุกรมเวลา ไม่ใช่ cross-sectional IC ของพอร์ตหลายตัว

    python3 tools/ic_figures.py
"""

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "nq-figures.json")
OUT = os.path.join(ROOT, "docs", "ic-figures.json")

HORIZONS = [1, 3, 5, 10]
SEED, DRAWS = 20260913, 5000
COST_ROUND_TRIP = 0.2          # % ต่อรอบ — ชุดเดียวกับ "มิน" ใน nq-figures.json
SIGNAL_WINDOW = 20             # วัน — หน้าต่างของ "ความชัน regression 20 วัน" (สัญญาณที่ IC แรงที่สุด)
                               # วันติดกันใช้หน้าต่างซ้อนกัน 19/20 จึงไม่ใช่เดิมพันอิสระคนละอัน


def daily_prices():
    with open(SRC, encoding="utf-8") as fh:
        d = json.load(fh)["ราคารายวัน"]
    ks = sorted(d)
    return ks, np.array([float(d[k]) for k in ks])


def rank(a):
    """อันดับ 1..n · ค่าที่เท่ากันได้อันดับเฉลี่ย (เหมือน scipy.stats.rankdata)"""
    a = np.asarray(a, float)
    order = a.argsort(kind="mergesort")
    r = np.empty(len(a), float)
    r[order] = np.arange(1, len(a) + 1)
    vals, counts = np.unique(a, return_counts=True)
    for v in vals[counts > 1]:
        m = a == v
        r[m] = r[m].mean()
    return r


def spearman(x, y):
    rx, ry = rank(x), rank(y)
    rx = rx - rx.mean(); ry = ry - ry.mean()
    den = np.sqrt((rx @ rx) * (ry @ ry))
    return float(rx @ ry / den) if den else 0.0


def signals(prices):
    """สัญญาณหกตัวจากอินดิเคเตอร์ที่บทภาคผนวก E อธิบายไว้แล้ว — คืน dict ชื่อ → array (NaN ช่วงอุ่นเครื่อง)"""
    import indicator_figures as IF
    px = list(prices)
    n = len(px)
    out = {}

    rsi = IF.rsi_wilder(px)
    out["RSI(14)"] = np.array([r["rsi"] if r else np.nan for r in rsi])

    mac = IF.macd(px)
    out["MACD histogram"] = np.array([m["hist"] if m and m.get("hist") is not None else np.nan for m in mac])

    bb = IF.bollinger(px)
    out["Bollinger %B"] = np.array([b["pct_b"] if b and b.get("pct_b") is not None else np.nan for b in bb])

    mom = np.full(n, np.nan)
    for t in range(5, n): mom[t] = px[t] / px[t - 5] - 1
    out["โมเมนตัม 5 วัน"] = mom

    slope = np.full(n, np.nan)
    for t in range(19, n): slope[t] = IF.ols_time(px[t - 19:t + 1])["slope"]
    out["ความชัน regression 20 วัน"] = slope

    adx = IF.adx_close_only(px)
    out["ADX (ประมาณ)"] = np.array([a["adx"] if a and a.get("adx") is not None else np.nan for a in adx])
    return out


def fwd_returns(prices, h):
    """ผลตอบแทนล่วงหน้า h วัน (%) ที่วันที่ t — ช่องท้ายที่ไม่มีอนาคตเป็น NaN"""
    n = len(prices)
    r = np.full(n, np.nan)
    for t in range(n - h): r[t] = (prices[t + h] / prices[t] - 1) * 100
    return r


def ic_of(sig, fwd):
    m = ~(np.isnan(sig) | np.isnan(fwd))
    if m.sum() < 8: return None
    return dict(ic=spearman(sig[m], fwd[m]), n=int(m.sum()))


def null_band(sig, fwd, rng, draws=DRAWS):
    """ฐานจากความสุ่ม: สลับผลตอบแทนล่วงหน้าแล้ววัด IC ใหม่ — คืนช่วง 90% และค่าสัมบูรณ์ที่ 95"""
    m = ~(np.isnan(sig) | np.isnan(fwd))
    s, f = sig[m], fwd[m]
    vals = np.empty(draws)
    for i in range(draws):
        vals[i] = spearman(s, rng.permutation(f))
    return dict(lo90=float(np.percentile(vals, 5)), hi90=float(np.percentile(vals, 95)),
                abs95=float(np.percentile(np.abs(vals), 95)), sd=float(vals.std(ddof=1)))


def terciles(sig, fwd):
    """แบ่งวันตามสัญญาณเป็นสามกลุ่มเท่า ๆ กัน แล้วดูผลตอบแทนล่วงหน้าเฉลี่ยของแต่ละกลุ่ม"""
    m = ~(np.isnan(sig) | np.isnan(fwd))
    s, f = sig[m], fwd[m]
    q1, q2 = np.percentile(s, [100 / 3, 200 / 3])
    groups = [("ต่ำสุด", f[s <= q1]), ("กลาง", f[(s > q1) & (s <= q2)]), ("สูงสุด", f[s > q2])]
    return [{"กลุ่ม": nm, "จำนวนวัน": int(len(g)),
             "ผลตอบแทนเฉลี่ยเปอร์เซ็นต์": round(float(g.mean()), 3),
             "มัธยฐานเปอร์เซ็นต์": round(float(np.median(g)), 3)} for nm, g in groups if len(g)]


def build():
    days, px = daily_prices()
    sigs = signals(px)

    rows = []
    for nm, sg in sigs.items():
        per_h = {}
        for h in HORIZONS:
            r = ic_of(sg, fwd_returns(px, h))
            if r:
                nh = null_band(sg, fwd_returns(px, h), np.random.default_rng(SEED + 100 * h))
                per_h[f"{h} วัน"] = {"IC": round(r["ic"], 4), "จำนวนวัน": r["n"],
                                     "SEโดยประมาณ": round(1 / np.sqrt(r["n"] - 1), 4),
                                     "tstat": round(r["ic"] * np.sqrt(r["n"] - 1), 2),
                                     "ฐานabsที่95": round(nh["abs95"], 4),
                                     "นอกฐาน": bool(abs(r["ic"]) > nh["abs95"]),
                                     "จำนวนวันอิสระโดยประมาณ": int(r["n"] // h)}
        base = ic_of(sg, fwd_returns(px, 1))
        if not base:
            continue
        nb = null_band(sg, fwd_returns(px, 1), np.random.default_rng(SEED))
        rows.append({"สัญญาณ": nm, "IC1วัน": round(base["ic"], 4), "จำนวนวัน": base["n"],
                     "ฐานสุ่ม": {"ช่วง90": [round(nb["lo90"], 4), round(nb["hi90"], 4)],
                                 "absที่95": round(nb["abs95"], 4), "SDของฐาน": round(nb["sd"], 4)},
                     "นอกฐาน": bool(abs(base["ic"]) > nb["abs95"]),
                     "ทุกhorizon": per_h})

    best = max(rows, key=lambda r: abs(r["IC1วัน"]))
    f1 = fwd_returns(px, 1)
    mats = []
    for nm, sg in sigs.items():
        m = ~(np.isnan(sg) | np.isnan(f1))
        if m.sum() >= 8:
            mats.append((sg[m], f1[m]))
    rng2 = np.random.default_rng(SEED + 1)
    max_null = np.empty(DRAWS)
    for i in range(DRAWS):
        max_null[i] = max(abs(spearman(a, rng2.permutation(b))) for a, b in mats)
    sel = {"จำนวนสัญญาณที่ลอง": len(mats),
           "maxABSที่95จากความสุ่ม": round(float(np.percentile(max_null, 95)), 4),
           "maxABSเฉลี่ยจากความสุ่ม": round(float(max_null.mean()), 4),
           "ของจริง": round(abs(best["IC1วัน"]), 4),
           "เปอร์เซ็นไทล์ของของจริง": round(float((max_null < abs(best["IC1วัน"])).mean() * 100), 1)}

    z_a, z_b = 1.96, 1.2816
    def n_needed(ic):
        return int(np.ceil(((z_a + z_b) / max(abs(ic), 1e-6)) ** 2 + 1))
    sample = {f"IC = {v}": n_needed(v) for v in (0.05, 0.10, 0.20, 0.30)}
    sample[f"IC ที่วัดได้ของ {best['สัญญาณ']} = {abs(best['IC1วัน']):.3f}"] = n_needed(best["IC1วัน"])

    hist_cnt, hist_edges = np.histogram(max_null, bins=28, range=(0.0, 0.7))
    ic_grid = [round(v, 3) for v in np.arange(0.04, 0.42, 0.02)]

    ir_target = 1.0
    def breadth_needed(ic):
        return int(np.ceil((ir_target / max(abs(ic), 1e-6)) ** 2))
    law = {"สูตร": "IR ≈ IC × √breadth (Grinold 1989)",
           "IRที่ตั้งเป้า": ir_target,
           "จำนวนเดิมพันอิสระที่ต้องใช้ต่อปี": {f"IC = {v}": breadth_needed(v) for v in (0.05, 0.10, 0.20)},
           "ของสัญญาณที่ดีที่สุด": {"IC": abs(best["IC1วัน"]),
                                     "เดิมพันอิสระที่ต้องใช้ต่อปี": breadth_needed(best["IC1วัน"]),
                                     "วันทำการต่อปีของสินทรัพย์เดียว": 252,
                                     "หน้าต่างของสัญญาณ(วัน)": SIGNAL_WINDOW,
                                     "เดิมพันอิสระที่มีจริงต่อปีต่อสินทรัพย์": 252 // SIGNAL_WINDOW,
                                     "จำนวนสินทรัพย์ที่ต้องใช้": int(np.ceil(breadth_needed(best["IC1วัน"]) / (252 // SIGNAL_WINDOW)))}}

    terc = terciles(sigs[best["สัญญาณ"]], f1)
    spread = round(terc[-1]["ผลตอบแทนเฉลี่ยเปอร์เซ็นต์"] - terc[0]["ผลตอบแทนเฉลี่ยเปอร์เซ็นต์"], 3)
    spread_med = round(terc[-1]["มัธยฐานเปอร์เซ็นต์"] - terc[0]["มัธยฐานเปอร์เซ็นต์"], 3)

    return {
        "_อ่านก่อน": "สร้างด้วย tools/ic_figures.py จาก docs/nq-figures.json (ราคารายวัน) — ห้ามแก้ด้วยมือ",
        "ข้อมูล": {"สินทรัพย์": "BTC", "ตั้งแต่": days[0], "ถึง": days[-1], "จำนวนวัน": len(days),
                   "จำนวนวันผลตอบแทน": len(days) - 1,
                   "หมายเหตุ": "IC แบบอนุกรมเวลาบนสินทรัพย์เดียว ไม่ใช่ cross-sectional IC"},
        "วิธีวัด": {"นิยาม": "Spearman rank correlation ระหว่างสัญญาณวันที่ t กับผลตอบแทนล่วงหน้า h วัน",
                    "เหตุที่ใช้อันดับ": "ทนค่าสุดขั้ว — วันเดียวที่ราคากระโดดไม่ลากค่าทั้งชุด",
                    "จำนวนรอบจำลองฐาน": DRAWS,
                    "ข้อควรระวัง": "horizon > 1 วัน ผลตอบแทนซ้อนทับกัน t-stat จึงดูใหญ่เกินจริง"},
        "สัญญาณ": rows,
        "สัญญาณที่ดีที่สุด": {"ชื่อ": best["สัญญาณ"], "IC": best["IC1วัน"], "จำนวนวัน": best["จำนวนวัน"]},
        "ผลของการเลือกตัวที่ดีที่สุด": sel,
        "ขนาดตัวอย่างที่ต้องใช้": sample,
        "เส้นขนาดตัวอย่าง": {"IC": ic_grid, "จำนวนวันที่ต้องใช้": [n_needed(v) for v in ic_grid],
                             "สูตร": "n = ((zα + zβ) ÷ IC)² + 1 · two-sided 5% · power 90%"},
        "การกระจายของmaxABSจากความสุ่ม": {"ขอบช่อง": [round(float(v), 4) for v in hist_edges],
                                          "จำนวน": [int(v) for v in hist_cnt], "จำนวนรอบ": DRAWS},
        "กฎพื้นฐานของการจัดการเชิงรุก": law,
        "กลุ่มสามส่วนของสัญญาณที่ดีที่สุด": {"กลุ่ม": terc,
                                             "ส่วนต่างสูงสุดลบต่ำสุดเปอร์เซ็นต์": spread,
                                             "ส่วนต่างมัธยฐานเปอร์เซ็นต์": spread_med,
                                             "ต้นทุนไปกลับเปอร์เซ็นต์": COST_ROUND_TRIP,
                                             "เหลือหลังต้นทุนเปอร์เซ็นต์": round(spread - COST_ROUND_TRIP, 3)},
    }


if __name__ == "__main__":
    data = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("เขียน", os.path.relpath(OUT, ROOT))
